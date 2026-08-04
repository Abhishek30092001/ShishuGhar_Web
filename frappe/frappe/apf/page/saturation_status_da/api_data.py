import frappe
from frappe import _
import json
import os
import re
import time
import gzip
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# LGD boundary loader
# ---------------------------------------------------------------------------
#
# The browser previously fetched the full India-wide District (88 MB) and
# Block (284 MB) GeoJSONs from a stale `geohacker/india` mirror, then tried
# to filter them client-side. That had three failure modes:
#
#   1. Missing areas: the mirror predates 2017-2024 district splits and the
#      newer CD-block re-divisions, so freshly created districts/blocks (e.g.
#      Anakapalli, Bapatla, Sri Sathya Sai, Konaseema, Mewat -> Nuh, etc.)
#      simply had no polygon.
#   2. Duplicate boundaries: same-named districts in two states (Bilaspur in
#      Chhattisgarh + Himachal, Aurangabad in Maharashtra + Bihar, etc.)
#      both matched, so the wrong polygon coloured in.
#   3. Browser crashes / 30 s+ loads on slower networks.
#
# The fix: serve LGD-aligned GeoJSON (https://lgdirectory.gov.in/) sourced
# from bharatlas.com on the server, cache it, and only return the polygons
# that fall inside the selected scope.

_LEVEL_KEYS = {"2": "state", "3": "district", "4": "block"}

_CACHE_TTL_SECONDS = 7 * 24 * 60 * 60   # 7 days - LGD changes are infrequent
_HTTP_TIMEOUT = 180


def _page_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _cache_dir():
    """Site-private cache for downloaded LGD GeoJSONs."""
    try:
        base = frappe.get_site_path("private", "files", "geo_cache")
    except Exception:
        base = os.path.join(_page_dir(), ".geo_cache")
    os.makedirs(base, exist_ok=True)
    return base


def _norm(value):
    """Case- and punctuation-insensitive name comparator."""
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


# ADM3 shapeNames carry suffixes like " CD Block", " (Pt)", " Block" that
# don't appear in the Frappe Block doctype names.  Strip them before matching.
_ADM3_SUFFIX_RE = re.compile(
    r"\s*\bcd\s+block\b|\s*\bblock\b|\s*\(pt\.?\)|\s*\(part\)|\s*\btaluk\b|\s*\btehsil\b|\s*\bmandal\b",
    re.IGNORECASE,
)


def _norm_adm3(shape_name):
    """Normalise an ADM3 shapeName by stripping common block suffixes first."""
    stripped = _ADM3_SUFFIX_RE.sub("", shape_name).strip()
    return _norm(stripped) or _norm(shape_name)


@frappe.whitelist()
def get_geolocation_config():
    """Read and return geolocation.json from the page directory."""
    json_path = os.path.join(_page_dir(), "geolocation.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_config():
    json_path = os.path.join(_page_dir(), "geolocation.json")
    if not os.path.exists(json_path):
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_block_names_for_district(district):
    """Return a set of normalised block names belonging to the given district."""
    if not district:
        return set()
    rows = frappe.db.sql(
        """
        SELECT b.block_name
        FROM `tabBlock` AS b
        JOIN `tabDistrict` AS d ON d.name = b.district_id
        WHERE d.district_name = %(district)s OR d.name = %(district)s
        """,
        {"district": district},
        as_dict=True,
    )
    return {_norm(r["block_name"]) for r in rows if r.get("block_name")}


def _get_block_names_for_state(state):
    """Return a set of normalised block names belonging to the given state."""
    if not state:
        return set()
    rows = frappe.db.sql(
        """
        SELECT b.block_name
        FROM `tabBlock` AS b
        JOIN `tabDistrict` AS d ON d.name = b.district_id
        JOIN `tabState` AS s ON s.name = d.state_id
        WHERE s.state_name = %(state)s OR s.name = %(state)s
        """,
        {"state": state},
        as_dict=True,
    )
    return {_norm(r["block_name"]) for r in rows if r.get("block_name")}


def _first_present(props, keys):
    """Return the first value found in `props` for any key in `keys`."""
    if not props:
        return ""
    for k in keys or []:
        if k in props and props[k] not in (None, ""):
            return props[k]
    # Case-insensitive fallback - LGD layers are lowercase but other mirrors
    # use upper/mixed case property keys.
    lowered = {str(k).lower(): k for k in props.keys()}
    for k in keys or []:
        actual = lowered.get(str(k).lower())
        if actual and props[actual] not in (None, ""):
            return props[actual]
    return ""


def _expand_aliases(value, alias_map):
    """Return the canonical name + all alias forms, lowercased+stripped."""
    out = set()
    if not value:
        return out
    out.add(_norm(value))
    if not alias_map:
        return out
    for canonical, aliases in alias_map.items():
        c_norm = _norm(canonical)
        a_norms = {_norm(a) for a in (aliases or [])}
        # if the supplied value matches the canonical, add all aliases
        if _norm(value) == c_norm:
            out.update(a_norms)
        # if it matches an alias, add the canonical and the other aliases
        if _norm(value) in a_norms:
            out.add(c_norm)
            out.update(a_norms)
    return out


def _download_layer(url, cache_path):
    """Download a GeoJSON layer, transparently handling gzip and caching."""
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < _CACHE_TTL_SECONDS and os.path.getsize(cache_path) > 1024:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Frappe-APF-Saturation-Dashboard/1.0 (+boundary fetch)",
            "Accept": "application/geo+json, application/json;q=0.9, */*;q=0.1",
            "Accept-Encoding": "gzip",
        },
    )
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
        raw = resp.read()
        if resp.headers.get("Content-Encoding", "").lower() == "gzip" or raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
    data = json.loads(raw.decode("utf-8"))
    tmp = cache_path + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, cache_path)
    return data


def _empty_collection():
    return {"type": "FeatureCollection", "features": []}


_ADM3_LOCAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geoBoundaries-IND-ADM3.geojson")
_ADM3_REMOTE_URL = "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/IND/ADM3/geoBoundaries-IND-ADM3.geojson"


def _load_adm3():
    """Load the ADM3 geojson from local file; fall back to remote download + cache."""
    if os.path.exists(_ADM3_LOCAL_PATH) and os.path.getsize(_ADM3_LOCAL_PATH) > 1024 * 1024:
        with open(_ADM3_LOCAL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    cache_path = os.path.join(_cache_dir(), "geoBoundaries-IND-ADM3.geojson")
    return _download_layer(_ADM3_REMOTE_URL, cache_path)


@frappe.whitelist()
def get_boundary_geojson(level=None, state=None, district=None):
    """Return GeoJSON boundaries scoped to the selected level.

    level "2" = State  (external URL from geolocation.json)
    level "3" = District (external URL from geolocation.json)
    level "4" = Block  (local geoBoundaries-IND-ADM3.geojson, shapeName property)

    For level 4 the features are filtered by cross-referencing block names
    stored in the Frappe Block/District/State doctypes so that only blocks
    belonging to the selected district (or state, if no district given) are
    returned.
    """
    level = str(level) if level is not None else ""
    if level not in _LEVEL_KEYS:
        return _empty_collection()

    cache_key = f"boundary:v3:{level}:{_norm(state)}:{_norm(district)}"
    mem_cache = None
    try:
        mem_cache = frappe.cache()
    except Exception:
        pass
    if mem_cache:
        cached = mem_cache.get_value(cache_key)
        if cached:
            try:
                return json.loads(cached)
            except Exception:
                pass

    # ---- Block level: use local ADM3 file filtered via Frappe DB -----------
    if level == "4":
        try:
            adm3 = _load_adm3()
        except Exception as e:
            frappe.log_error(title="ADM3 load failed", message=str(e))
            return _empty_collection()

        features = adm3.get("features") or []

        # Build allowed block name set from Frappe DB
        if district:
            allowed = _get_block_names_for_district(district)
        elif state:
            allowed = _get_block_names_for_state(state)
        else:
            allowed = set()

        filtered = []
        for feat in features:
            shape_name = (feat.get("properties") or {}).get("shapeName") or ""
            if not shape_name:
                continue
            if allowed and _norm_adm3(shape_name) not in allowed:
                continue
            filtered.append(feat)

        out = {
            "type": "FeatureCollection",
            "features": filtered,
            "_meta": {"level": level, "scope_state": state, "scope_district": district, "count": len(filtered)},
        }
        if mem_cache:
            try:
                mem_cache.set_value(cache_key, json.dumps(out), expires_in_sec=3600)
            except Exception:
                pass
        return out

    # ---- State / District level: download from external URL ----------------
    config = _load_config()
    sources = config.get("boundary_sources") or {}
    aliases = config.get("name_aliases") or {}
    fields = (config.get("boundary_fields") or {}).get(_LEVEL_KEYS[level], {}) or {}

    url = sources.get(_LEVEL_KEYS[level]) or ""
    if not url:
        return _empty_collection()

    cache_path = os.path.join(_cache_dir(), f"lgd_level_{level}.geojson")
    try:
        data = _download_layer(url, cache_path)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
        frappe.log_error(title="Boundary GeoJSON fetch failed", message=f"level={level} url={url}\n{e}")
        return _empty_collection()

    features = data.get("features") or []

    if level == "2":
        out = {"type": "FeatureCollection", "features": features, "_meta": {"source": url, "count": len(features), "level": level}}
        if mem_cache:
            try:
                mem_cache.set_value(cache_key, json.dumps(out), expires_in_sec=3600)
            except Exception:
                pass
        return out

    # District level: filter by state
    state_alias_set = _expand_aliases(state, aliases.get("state") or {})
    parent_state_keys = fields.get("parent_state_name") or []

    filtered = []
    for feat in features:
        props = feat.get("properties") or {}
        if state_alias_set and parent_state_keys:
            feat_state = _first_present(props, parent_state_keys)
            if feat_state and _norm(feat_state) not in state_alias_set:
                continue
        filtered.append(feat)

    out = {
        "type": "FeatureCollection",
        "features": filtered,
        "_meta": {"source": url, "level": level, "scope_state": state, "count": len(filtered)},
    }
    if mem_cache:
        try:
            mem_cache.set_value(cache_key, json.dumps(out), expires_in_sec=3600)
        except Exception:
            pass
    return out


# ---------------------------------------------------------------------------
# Creche master data (unchanged from before)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_creche_master_data(year=None, month=None, c_status=None, partner=None, state=None, district=None, block=None, gp=None, village=None, supervisor_id=None, creche=None, phases=None):
    conditions = []
    if year and month:
        conditions.append(f"(YEAR(c.creche_opening_date) < {frappe.db.escape(year)} OR (YEAR(c.creche_opening_date) = {frappe.db.escape(year)} AND MONTH(c.creche_opening_date) <= {frappe.db.escape(month)}))")
    elif year:
        conditions.append(f"YEAR(c.creche_opening_date) <= {frappe.db.escape(year)}")
    elif month:
        conditions.append(f"MONTH(c.creche_opening_date) <= {frappe.db.escape(month)}")
    if c_status:
        conditions.append(f"c.creche_status_id = {frappe.db.escape(c_status)}")
    if partner:
        conditions.append(f"c.partner_id = {frappe.db.escape(partner)}")
    if state:
        conditions.append(f"c.state_id = {frappe.db.escape(state)}")
    if district:
        conditions.append(f"c.district_id = {frappe.db.escape(district)}")
    if block:
        conditions.append(f"c.block_id = {frappe.db.escape(block)}")
    if gp:
        conditions.append(f"c.gp_id = {frappe.db.escape(gp)}")
    if village:
        conditions.append(f"c.village_id = {frappe.db.escape(village)}")
    if supervisor_id:
        conditions.append(f"c.supervisor_id = {frappe.db.escape(supervisor_id)}")
    if creche:
        conditions.append(f"c.name = {frappe.db.escape(creche)}")
    if phases:
        if isinstance(phases, str):
            try:
                phases_list = json.loads(phases)
            except Exception:
                phases_list = phases.split(",")
        else:
            phases_list = phases
        if phases_list:
            phases_str = ", ".join([frappe.db.escape(p.strip()) for p in phases_list])
            conditions.append(f"c.phases IN ({phases_str})")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    data = frappe.db.sql(f"""
        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            c.state_id AS state_id,
            d.district_name AS district,
            c.district_id AS district_id,
            b.block_name AS block,
            gp.gp_name AS gram_panchayat,
            v.village_name AS village,
            u.full_name AS supervisor,
            c.creche_name AS creche,
            c.creche_id AS creche_id,
            c.latitude AS latitude,
            c.longitude AS longitude

        FROM `tabCreche` AS c

        LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
        LEFT JOIN `tabPartner` AS p ON p.name = c.partner_id
        LEFT JOIN `tabState` AS s ON s.name = c.state_id
        LEFT JOIN `tabDistrict` AS d ON d.name = c.district_id
        LEFT JOIN `tabBlock` AS b ON b.name = c.block_id
        LEFT JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id
        LEFT JOIN `tabVillage` AS v ON v.name = c.village_id
        {where_clause}
        GROUP BY
            p.partner_name,s.state_name,c.state_id,d.district_name,c.district_id,b.block_name,gp.gp_name,v.village_name,u.full_name,c.creche_name,c.creche_id,c.latitude,c.longitude
        ORDER BY c.creche_name ASC
    """, as_dict=True)

    return {
        "success": True,
        "message": "Creche master data fetched successfully",
        "filters": {
            "year": year,
            "month": month,
            "c_status": c_status
        },
        "total_count": len(data),
        "data": data
    }
