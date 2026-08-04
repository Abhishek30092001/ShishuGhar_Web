import frappe
from frappe import _


def execute(filters=None):
    selected_level = filters.get("level", "7")
    variable_columns = []

    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
    if selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
    if selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
    if selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
    if selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
    if selected_level == "7":
        variable_columns.append({"label": "SL", "fieldname": "sl", "fieldtype": "Data", "width": 60})
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche Name", "fieldname": "creche", "fieldtype": "Data", "width": 220})

    # Date columns only make sense at Creche / Supervisor level (individual records)
    date_columns = []
    if selected_level in ("5", "7"):
        date_columns = [
            {"label": "Date of Delivery", "fieldname": "date_of_delivery", "fieldtype": "Data", "width": 150},
            {"label": "Date of Expiry",   "fieldname": "date_of_expiry",   "fieldtype": "Data", "width": 150},
        ]

    fixed_columns = [
        {"label": "Fire Extinguisher Status", "fieldname": "fire_extinguisher_status_display", "fieldtype": "Data", "width": 300},
    ] + date_columns

    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
    return columns, data


def get_report_data(filters):
    selected_level = filters.get("level", "7")

    conditions = ["1=1"]
    params = {
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
    }

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    state_ids    = ",".join(str(s["state_id"])    for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids    = ",".join(str(s["block_id"])    for s in current_user_state if s.get("block_id"))
    gp_ids       = ",".join(str(s["gp_id"])       for s in current_user_state if s.get("gp_id"))

    if partner_id:
        conditions.append("fe.partner_id = %(partner)s")
        params["partner"] = partner_id
    if filters.get("state"):
        conditions.append("fe.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(fe.state_id, %(state_ids)s)")
            params["state_ids"] = state_ids
            params["state"] = None

    if filters.get("district"):
        conditions.append("fe.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(fe.district_id, %(district_ids)s)")
            params["district_ids"] = district_ids
            params["district"] = None

    if filters.get("block"):
        conditions.append("fe.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(fe.block_id, %(block_ids)s)")
            params["block_ids"] = block_ids
            params["block"] = None

    if filters.get("gp"):
        conditions.append("fe.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
        params["gp_ids"] = None
    else:
        if gp_ids:
            conditions.append("FIND_IN_SET(fe.gp_id, %(gp_ids)s)")
            params["gp_ids"] = gp_ids
            params["gp"] = None

    if filters.get("creche"):
        conditions.append("fe.creche_id = %(creche)s")
        params["creche"] = filters.get("creche")
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")

    where_clause = " AND ".join(conditions)

    # Creche level: one row per fire extinguisher record
    if selected_level == "7":
        query = f"""
            SELECT
                p.partner_name                                      AS partner,
                s.state_name                                        AS state,
                d.district_name                                     AS district,
                b.block_name                                        AS block,
                g.gp_name                                           AS gp,
                u.full_name                                         AS supervisor,
                c.creche_name                                       AS creche,
                c.creche_id                                         AS creche_id,
                fe.fire_extingusher_status                          AS fire_extingusher_status,
                fe.other                                            AS other_remarks,
                DATE_FORMAT(fe.date_of_delivery, '%%d-%%m-%%Y')    AS date_of_delivery,
                DATE_FORMAT(fe.date_of_expiry,   '%%d-%%m-%%Y')    AS date_of_expiry
            FROM `tabFire Extinguisher` fe
            LEFT JOIN `tabCreche`        c ON fe.creche_id   = c.name
            LEFT JOIN `tabPartner`       p ON fe.partner_id  = p.name
            LEFT JOIN `tabState`         s ON fe.state_id    = s.name
            LEFT JOIN `tabDistrict`      d ON fe.district_id = d.name
            LEFT JOIN `tabBlock`         b ON fe.block_id    = b.name
            LEFT JOIN `tabGram Panchayat` g ON fe.gp_id      = g.name
            LEFT JOIN `tabUser`          u ON c.supervisor_id = u.name
            WHERE {where_clause}
            ORDER BY s.state_name, d.district_name, b.block_name, g.gp_name, c.creche_name
        """
        rows = frappe.db.sql(query, params, as_dict=True)

        data = []
        for i, row in enumerate(rows, 1):
            status = row.get("fire_extingusher_status") or ""
            if status == "Other":
                display_status = row.get("other_remarks") or "Other"
            else:
                display_status = status

            data.append({
                "sl":                              i,
                "partner":                         row.get("partner") or "",
                "state":                           row.get("state") or "",
                "district":                        row.get("district") or "",
                "block":                           row.get("block") or "",
                "gp":                              row.get("gp") or "",
                "supervisor":                      row.get("supervisor") or "",
                "creche":                          row.get("creche") or "",
                "creche_id":                       row.get("creche_id") or "",
                "fire_extinguisher_status_display": display_status,
                "date_of_delivery":                row.get("date_of_delivery") or "",
                "date_of_expiry":                  row.get("date_of_expiry") or "",
            })

        # Totals row
        total_available      = sum(1 for r in rows if r.get("fire_extingusher_status") == "Available")
        total_not_available  = sum(1 for r in rows if r.get("fire_extingusher_status") == "Not Available")
        total_gone_refilling = sum(1 for r in rows if r.get("fire_extingusher_status") == "Gone for Refilling")
        total_other          = sum(1 for r in rows if r.get("fire_extingusher_status") == "Other")

        summary_parts = []
        if total_available:      summary_parts.append(f"Available - {total_available}")
        if total_not_available:  summary_parts.append(f"Not Available - {total_not_available}")
        if total_gone_refilling: summary_parts.append(f"Gone for Refilling - {total_gone_refilling}")
        if total_other:          summary_parts.append(f"Other - {total_other}")

        total_row = {
            "sl":                              "<b style='color:black;'>Total</b>",
            "partner":                         "",
            "state":                           "",
            "district":                        "",
            "block":                           "",
            "gp":                              "",
            "supervisor":                      "",
            "creche":                          "",
            "fire_extinguisher_status_display": f"<b>{', '.join(summary_parts)}</b>",
            "date_of_delivery":                "",
            "date_of_expiry":                  "",
        }
        data.append(total_row)
        return data

    # Aggregated levels: group by geography
    level_mapping = {
        "1": {"group_fields": ["p.partner_name"]},
        "2": {"group_fields": ["s.state_name"]},
        "3": {"group_fields": ["s.state_name", "d.district_name"]},
        "4": {"group_fields": ["s.state_name", "d.district_name", "b.block_name"]},
        "5": {"group_fields": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"]},
        "6": {"group_fields": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"]},
    }

    level_info    = level_mapping.get(selected_level, level_mapping["6"])
    group_by_sql  = ", ".join(level_info["group_fields"])

    # Pull detail rows and aggregate in Python so we can embed popup metadata
    detail_query = f"""
        SELECT
            p.partner_name                                      AS partner,
            s.state_name                                        AS state,
            d.district_name                                     AS district,
            b.block_name                                        AS block,
            g.gp_name                                           AS gp,
            u.full_name                                         AS supervisor,
            c.creche_name                                       AS creche,
            c.creche_id                                         AS creche_id,
            fe.fire_extingusher_status                          AS fire_extingusher_status,
            fe.other                                            AS other_remarks
        FROM `tabFire Extinguisher` fe
        LEFT JOIN `tabCreche`         c ON fe.creche_id   = c.name
        LEFT JOIN `tabPartner`        p ON fe.partner_id  = p.name
        LEFT JOIN `tabState`          s ON fe.state_id    = s.name
        LEFT JOIN `tabDistrict`       d ON fe.district_id = d.name
        LEFT JOIN `tabBlock`          b ON fe.block_id    = b.name
        LEFT JOIN `tabGram Panchayat` g ON fe.gp_id       = g.name
        LEFT JOIN `tabUser`           u ON c.supervisor_id = u.name
        WHERE {where_clause}
        ORDER BY {group_by_sql}
    """
    detail_rows = frappe.db.sql(detail_query, params, as_dict=True)

    # Build group key function per level
    def group_key(row):
        if selected_level == "1":
            return (row.get("partner") or "",)
        elif selected_level == "2":
            return (row.get("state") or "",)
        elif selected_level == "3":
            return (row.get("state") or "", row.get("district") or "")
        elif selected_level == "4":
            return (row.get("state") or "", row.get("district") or "", row.get("block") or "")
        elif selected_level == "5":
            return (row.get("state") or "", row.get("district") or "", row.get("block") or "", row.get("supervisor") or "")
        elif selected_level == "6":
            return (row.get("state") or "", row.get("district") or "", row.get("block") or "", row.get("gp") or "")
        return (row.get("state") or "",)

    from collections import OrderedDict
    groups = OrderedDict()
    for row in detail_rows:
        key = group_key(row)
        if key not in groups:
            groups[key] = {"geo": row, "records": []}
        groups[key]["records"].append(row)

    statuses = ["Available", "Not Available", "Gone for Refilling", "Other"]

    data = []
    for key, grp in groups.items():
        geo       = grp["geo"]
        records   = grp["records"]

        counts = {st: [] for st in statuses}
        for r in records:
            st = r.get("fire_extingusher_status") or "Other"
            if st not in counts:
                st = "Other"
            counts[st].append(r)

        status_parts = []
        for st in statuses:
            c = len(counts[st])
            if c:
                # Build popup detail list for this status bucket
                popup_rows = []
                for idx, r in enumerate(counts[st], 1):
                    popup_rows.append({
                        "sr_no":   idx,
                        "partner": r.get("partner") or "",
                        "state":   r.get("state") or "",
                        "district": r.get("district") or "",
                        "block":   r.get("block") or "",
                        "gp":      r.get("gp") or "",
                        "creche":  r.get("creche") or "",
                        "creche_id": r.get("creche_id") or "",
                    })
                import json
                popup_json = json.dumps(popup_rows).replace("'", "&#39;").replace('"', "&quot;")
                # Clickable link that JS will intercept
                link = (
                    f"<a href='#' "
                    f"data-popup='{popup_json}' "
                    f"data-status='{st}' "
                    f"class='fe-popup-link'>{st} - {c}</a>"
                )
                status_parts.append(link)

        row_out = {}
        if selected_level == "1":
            row_out["partner"]  = geo.get("partner") or ""
        if selected_level in ("2", "3", "4", "5", "6"):
            row_out["state"]    = geo.get("state") or ""
        if selected_level in ("3", "4", "5", "6"):
            row_out["district"] = geo.get("district") or ""
        if selected_level in ("4", "5", "6"):
            row_out["block"]    = geo.get("block") or ""
        if selected_level == "5":
            row_out["supervisor"] = geo.get("supervisor") or ""
        if selected_level == "6":
            row_out["gp"]       = geo.get("gp") or ""

        row_out["fire_extinguisher_status_display"] = ", ".join(status_parts)
        data.append(row_out)

    # Totals row for aggregated levels
    total_available      = sum(1 for r in detail_rows if r.get("fire_extingusher_status") == "Available")
    total_not_available  = sum(1 for r in detail_rows if r.get("fire_extingusher_status") == "Not Available")
    total_gone_refilling = sum(1 for r in detail_rows if r.get("fire_extingusher_status") == "Gone for Refilling")
    total_other          = sum(1 for r in detail_rows if r.get("fire_extingusher_status") not in ("Available", "Not Available", "Gone for Refilling") or r.get("fire_extingusher_status") == "Other")

    summary_parts = []
    if total_available:      summary_parts.append(f"Available - {total_available}")
    if total_not_available:  summary_parts.append(f"Not Available - {total_not_available}")
    if total_gone_refilling: summary_parts.append(f"Gone for Refilling - {total_gone_refilling}")
    if total_other:          summary_parts.append(f"Other - {total_other}")

    total_row = {
        "partner":  "<b style='color:black;'>Total</b>",
        "state":    "<b style='color:black;'>Total</b>",
        "district": "",
        "block":    "",
        "gp":       "",
        "supervisor": "",
        "fire_extinguisher_status_display": f"<b>{', '.join(summary_parts)}</b>",
    }
    data.append(total_row)
    return data
