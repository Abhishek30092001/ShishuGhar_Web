import frappe
import math
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict

def calculate_z_score(value, M, L, S):
    if L == 0:
        raise ValueError("L should not be zero to avoid division errors.")
    ratio = float(value / M)
    ratio_to_L = float(math.pow(ratio, L))
    numerator = float(ratio_to_L - 1)
    denominator = float(S * L)
    z_score = float(numerator / denominator)

    if z_score <= -3:
        sd3neg = float(M * math.pow(1 + L * S * (-3), 1 / L))
        sd2neg = float(M * math.pow(1 + L * S * (-2), 1 / L))
        sd23neg = float(sd2neg - sd3neg)
        z_score = float(-3 + (value - sd3neg) / sd23neg)
    elif z_score >= 3:
        sd3pos = float(M * math.pow(1 + L * S * (3), 1 / L))
        sd2pos = float(M * math.pow(1 + L * S * (2), 1 / L))
        sd23pos = float(sd3pos - sd2pos)
        z_score = float(3 + (value - sd3pos) / sd23pos)

    return round(z_score, 2)


def _load_age_indexed_table(doctype):
    fields = ["age_in_days", "green", "l", "m", "s", "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3", "sd4"]
    records = frappe.get_all(doctype, fields=fields)
    return {row["age_in_days"]: row for row in records}


def _load_height_indexed_table(doctype):
    fields = ["age_type", "length", "green", "l", "m", "s", "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0", "sd1", "sd2", "sd3", "sd4"]
    try:
        records = frappe.get_all(doctype, fields=fields, limit=0)
        data = defaultdict(list)
        for row in records:
            data[row["length"]].append(row)
        return dict(data)
    except Exception as e:
        frappe.log_error(f"Error loading {doctype}: {str(e)}")
        return {}


def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 150},
        {"label": "Age (At Enrollment)", "fieldname": "age", "fieldtype": "Data", "width": 180},
        {"label": "Current Age", "fieldname": "current_age", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
        {"label": "Height (cm)", "fieldname": "height", "fieldtype": "Data", "width": 130},
        {"label": "Weight (kg)", "fieldname": "weight", "fieldtype": "Data", "width": 130},
        {"label": "Measurement Date", "fieldname": "measurements_taken_date", "fieldtype": "Data", "width": 200},
        {"label": "Measurement Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 180},
        {"label": "Measurement Not Taken", "fieldname": "measurement_reason", "fieldtype": "Data", "width": 200},
        
        {"label": "Age in days", "fieldname": "age_months", "fieldtype": "Data", "width": 200},
        {"label": "Measurement Position", "fieldname": "measurement_position", "fieldtype": "Data", "width": 200},
        {"label": "Measurement Equipment", "fieldname": "measurement_equipment", "fieldtype": "Data", "width": 200},

        {"label": "Weight for Age (Z-score)", "fieldname": "weight_for_age_zscore", "fieldtype": "Data", "width": 200},
        {"label": "Weight for Height (Z-score)", "fieldname": "weight_for_height_zscore", "fieldtype": "Data", "width": 210},
        {"label": "Height for Age (Z-score)", "fieldname": "height_for_age_zscore", "fieldtype": "Data", "width": 200},
        {"label": "GF1", "fieldname": "gf1", "fieldtype": "Data", "width": 160, "align": "center"},
        {"label": "GF1+", "fieldname": "gf1_plus", "fieldtype": "Data", "width": 185, "align": "center"},
        {"label": "GF2", "fieldname": "gf2", "fieldtype": "Data", "width": 175, "align": "center"},
        {"label": "ZigZag", "fieldname": "gf_zigzag", "fieldtype": "Data", "width": 185, "align": "center"},
        {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 100, "align": "center"},


        {"label": "Weight Implaussible", "fieldname": "weight_implausible", "fieldtype": "Data", "width": 200},
        {"label": "Height Implaussible", "fieldname": "height_implausible", "fieldtype": "Data", "width": 200},
        {"label": "Weight Less Than 2kg", "fieldname": "weight_less_than_2kg", "fieldtype": "Data", "width": 200},
        {"label": "Any Reduction In Height", "fieldname": "any_reduction_in_height", "fieldtype": "Data", "width": 200}



        # {"label": "Home Visit", "fieldname": "red_flag_HV", "fieldtype": "Data", "width": 100, "align": "center"},
        # {"label": "Followup", "fieldname": "follow_up", "fieldtype": "Data", "width": 120},
        # {"label": "Taken to VHND", "fieldname": "vhsnd", "fieldtype": "Data", "width": 140},
        # {"label": "Taken to PHC", "fieldname": "phc", "fieldtype": "Data", "width": 120},
        # {"label": "Taken to CHC", "fieldname": "chc", "fieldtype": "Data", "width": 120},
        # {"label": "Taken to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 120},
        # {"label": "Taken to other Health Facility", "fieldname": "othr", "fieldtype": "Data", "width": 250},
    ]


@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    params = prepare_parameters(filters)
    data = execute_main_query(params)

    ref_tables = {
        "wfa_boys":  _load_age_indexed_table("Weight for age Boys"),
        "wfa_girls": _load_age_indexed_table("Weight for age Girls"),
        "wfh_boys":  _load_height_indexed_table("Weight to Height Boys"),
        "wfh_girls": _load_height_indexed_table("Weight to Height Girls"),
        "hfa_boys":  _load_age_indexed_table("Height for age Boys"),
        "hfa_girls": _load_age_indexed_table("Height for age Girls"),
    }

    data = process_data(data, ref_tables)
    data = add_summary_row(data)
    return data


def prepare_parameters(filters):
    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # EXACT historic month replication from the Summary Report
    # ── 1 month ago ──
    if month == 1:
        lmonth = 12
        lyear  = year - 1
    else:
        lmonth = month - 1
        lyear  = year

    # ── 2 months ago ──
    if month == 1:
        plmonth = 11
        pyear   = year - 1
    elif month == 2:
        plmonth = 12
        pyear   = year - 1
    else:
        plmonth = month - 2
        pyear   = year

    # ── 3 months ago ──
    if plmonth == 1:
        l2month = 12
        l2year  = pyear - 1
    else:
        l2month = plmonth - 1
        l2year  = pyear

    # ── 4 months ago ──
    if l2month == 1:
        l3month = 12
        l3year  = l2year - 1
    else:
        l3month = l2month - 1
        l3year  = l2year

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids    = ",".join(str(s["state_id"])    for s in current_user_state if s.get("state_id"))    or None
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id")) or None
    block_ids    = ",".join(str(s["block_id"])    for s in current_user_state if s.get("block_id"))    or None
    gp_ids       = ",".join(str(s["gp_id"])       for s in current_user_state if s.get("gp_id"))       or None

    phases_raw = filters.get("phases")
    phases = ",".join(p.strip() for p in phases_raw.split(",") if p.strip().isdigit()) if phases_raw else None

    state_id      = filters.get("state")      or None
    partner_id    = None if not partner_id else partner_id
    state_id      = None if not state_id   else state_id
    district_id   = filters.get("district")   or None
    block_id      = filters.get("block")      or None
    gp_id         = filters.get("gp")         or None
    creche_id     = filters.get("creche")     or None
    supervisor_id = filters.get("supervisor_id") or None
    c_status      = filters.get("creche_status_id") or None

    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()

        if range_type == "between" and filters.get("c_opening_range"):
            cstart_date, cend_date = filters["c_opening_range"]
        elif range_type == "before" and single_date:
            cstart_date = date(2017, 1, 1)
            cend_date   = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            cstart_date = single_date + timedelta(days=1)
            cend_date   = date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    def month_range(y, m):
        first = date(y, m, 1)
        last  = date(y, m, calendar.monthrange(y, m)[1])
        return first, last

    cgm_start, cgm_end     = month_range(year,   month)
    m1_start,  m1_end      = month_range(lyear,  lmonth)
    m2_start,  m2_end      = month_range(pyear,  plmonth)
    m3_start,  m3_end      = month_range(l2year, l2month)
    m4_start,  m4_end      = month_range(l3year, l3month)

    params = {
        "end_date": end_date, "year": year, "month": month, "start_date": start_date,
        "partner_id": partner_id, "state_id": state_id,
        "state_ids": state_ids, "district_id": district_id, "district_ids": district_ids,
        "block_id": block_id, "block_ids": block_ids,
        "gp_id": gp_id, "gp_ids": gp_ids,
        "creche_id": creche_id,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, "cend_date": cend_date,
        "c_status": c_status, "phases": phases,

        "lyear": lyear, "lmonth": lmonth,
        "pyear": pyear, "plmonth": plmonth,
        "l2year": l2year, "l2month": l2month,
        "l3year": l3year, "l3month": l3month,

        "cgm_start": cgm_start, "cgm_end": cgm_end,
        "m1_start": m1_start,   "m1_end": m1_end,
        "m2_start": m2_start,   "m2_end": m2_end,
        "m3_start": m3_start,   "m3_end": m3_end,
        "m4_start": m4_start,   "m4_end": m4_end,
        "crf_start": cgm_start, "crf_end": cgm_end,
    }
    return params


def execute_main_query(params):
    sql_query = """
    WITH
    -- ── Single-pass pivot: one scan of tabAnthropromatic Data gives zscore for each of 4 prior months ──
    ad_pivot AS (
        SELECT
            childenrollguid,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND weight_for_age_zscore IS NOT NULL THEN weight_for_age_zscore END) AS z_m1,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND weight_for_age_zscore IS NOT NULL THEN weight_for_age_zscore END) AS z_m2,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m3_start)s AND %(m3_end)s AND weight_for_age_zscore IS NOT NULL THEN weight_for_age_zscore END) AS z_m3,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m4_start)s AND %(m4_end)s AND weight_for_age_zscore IS NOT NULL THEN weight_for_age_zscore END) AS z_m4,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND weight  > 0 THEN weight  END) AS prev_weight,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND height > 0 THEN height  END) AS prev_height,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND weight  > 0 THEN measurement_taken_date END) AS prev_weight_date,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND weight  > 0 THEN weight  END) AS prev2_weight,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND height > 0 THEN height  END) AS prev2_height,
            MAX(CASE WHEN do_you_have_height_weight = 1 AND measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND weight  > 0 THEN measurement_taken_date END) AS prev2_weight_date
        FROM `tabAnthropromatic Data`
        WHERE do_you_have_height_weight = 1
          AND measurement_taken_date BETWEEN %(m4_start)s AND %(m1_end)s
        GROUP BY childenrollguid
    ),

    -- ── GF1: zscore dropped vs prior month (m1, exclusive fallback m2) ──
    gf1_flags AS (
        SELECT ad.name AS ad_name, COUNT(*) AS multiplier
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabAnthropromatic Data` ad_prev ON ad_prev.childenrollguid = ad.childenrollguid
            AND ad_prev.do_you_have_height_weight = 1 AND ad_prev.measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND ad_prev.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` ad_fallback ON ad_fallback.childenrollguid = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1 AND ad_fallback.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_fallback.weight_for_age_zscore IS NOT NULL AND ad_prev.childenrollguid IS NULL
        WHERE ad.do_you_have_height_weight = 1 AND ad.weight_for_age_zscore IS NOT NULL
          AND cgm.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
          AND cee.date_of_enrollment <= %(end_date)s AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
          AND (COALESCE(ad_prev.weight_for_age_zscore, ad_fallback.weight_for_age_zscore) - ad.weight_for_age_zscore) > 0
        GROUP BY ad.name
    ),

    -- ── GF1+: zscore fell by ≥ 0.5 vs prior month (m1, exclusive fallback m2) ──
    gf1p_flags AS (
        SELECT ad.name AS ad_name, COUNT(*) AS multiplier
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabAnthropromatic Data` ad_prev ON ad_prev.childenrollguid = ad.childenrollguid
            AND ad_prev.do_you_have_height_weight = 1 AND ad_prev.measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND ad_prev.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` ad_fallback ON ad_fallback.childenrollguid = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1 AND ad_fallback.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_fallback.weight_for_age_zscore IS NOT NULL AND ad_prev.childenrollguid IS NULL
        WHERE ad.do_you_have_height_weight = 1 AND ad.weight_for_age_zscore IS NOT NULL
          AND cgm.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
          AND cee.date_of_enrollment <= %(end_date)s AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
          AND (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
        GROUP BY ad.name
    ),

    -- ── ZigZag: fell ≥ 0.5 from best of 4 prior months, with direction changes (must have ALL 4) ──
    zz_flags AS (
        SELECT ad_current.name AS ad_name, COUNT(*) AS multiplier
        FROM `tabAnthropromatic Data` ad_current
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad_current.childenrollguid
        INNER JOIN `tabAnthropromatic Data` ad_m1 ON ad_m1.childenrollguid = ad_current.childenrollguid
            AND ad_m1.do_you_have_height_weight = 1 AND ad_m1.measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND ad_m1.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` ad_m2 ON ad_m2.childenrollguid = ad_current.childenrollguid
            AND ad_m2.do_you_have_height_weight = 1 AND ad_m2.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_m2.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` ad_m3 ON ad_m3.childenrollguid = ad_current.childenrollguid
            AND ad_m3.do_you_have_height_weight = 1 AND ad_m3.measurement_taken_date BETWEEN %(m3_start)s AND %(m3_end)s AND ad_m3.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` ad_m4 ON ad_m4.childenrollguid = ad_current.childenrollguid
            AND ad_m4.do_you_have_height_weight = 1 AND ad_m4.measurement_taken_date BETWEEN %(m4_start)s AND %(m4_end)s AND ad_m4.weight_for_age_zscore IS NOT NULL
        WHERE ad_current.do_you_have_height_weight = 1 AND ad_current.weight_for_age_zscore IS NOT NULL
          AND cgm.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
          AND cee.date_of_enrollment <= %(end_date)s AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))
          AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
        GROUP BY ad_current.name
    ),

    -- ── GF2: fell ≥ 0.5 vs 2-months-ago (m2, exclusive fallback m3) ──
    gf2_flags AS (
        SELECT DISTINCT ad.name AS ad_name, 1 AS multiplier
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabAnthropromatic Data` ad_priority ON ad_priority.childenrollguid = ad.childenrollguid
            AND ad_priority.do_you_have_height_weight = 1 AND ad_priority.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_priority.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` ad_fallback ON ad_fallback.childenrollguid = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1 AND ad_fallback.measurement_taken_date BETWEEN %(m3_start)s AND %(m3_end)s AND ad_fallback.weight_for_age_zscore IS NOT NULL AND ad_priority.childenrollguid IS NULL
        WHERE ad.do_you_have_height_weight = 1 AND ad.weight_for_age_zscore IS NOT NULL
          AND cgm.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
          AND cee.date_of_enrollment <= %(end_date)s AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (ad_priority.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
          AND (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
    ),

    -- ── SNC: union of GF1, GF1+, GF2, ZZ conditions plus direct flags ──
    snc_flags AS (
        SELECT DISTINCT ad_current.name AS ad_name, 1 AS multiplier
        FROM `tabAnthropromatic Data` AS ad_current
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad_current.childenrollguid

        LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_prev ON ad_gf1_prev.childenrollguid = ad_current.childenrollguid
            AND ad_gf1_prev.do_you_have_height_weight = 1 AND ad_gf1_prev.measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND ad_gf1_prev.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_fallback ON ad_gf1_fallback.childenrollguid = ad_current.childenrollguid
            AND ad_gf1_fallback.do_you_have_height_weight = 1 AND ad_gf1_fallback.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_gf1_fallback.weight_for_age_zscore IS NOT NULL AND ad_gf1_prev.childenrollguid IS NULL

        LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_priority ON ad_gf2_priority.childenrollguid = ad_current.childenrollguid
            AND ad_gf2_priority.do_you_have_height_weight = 1 AND ad_gf2_priority.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_gf2_priority.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_fallback ON ad_gf2_fallback.childenrollguid = ad_current.childenrollguid
            AND ad_gf2_fallback.do_you_have_height_weight = 1 AND ad_gf2_fallback.measurement_taken_date BETWEEN %(m3_start)s AND %(m3_end)s AND ad_gf2_fallback.weight_for_age_zscore IS NOT NULL AND ad_gf2_priority.childenrollguid IS NULL

        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m1 ON ad_zz_m1.childenrollguid = ad_current.childenrollguid
            AND ad_zz_m1.do_you_have_height_weight = 1 AND ad_zz_m1.measurement_taken_date BETWEEN %(m1_start)s AND %(m1_end)s AND ad_zz_m1.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m2 ON ad_zz_m2.childenrollguid = ad_current.childenrollguid
            AND ad_zz_m2.do_you_have_height_weight = 1 AND ad_zz_m2.measurement_taken_date BETWEEN %(m2_start)s AND %(m2_end)s AND ad_zz_m2.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m3 ON ad_zz_m3.childenrollguid = ad_current.childenrollguid
            AND ad_zz_m3.do_you_have_height_weight = 1 AND ad_zz_m3.measurement_taken_date BETWEEN %(m3_start)s AND %(m3_end)s AND ad_zz_m3.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m4 ON ad_zz_m4.childenrollguid = ad_current.childenrollguid
            AND ad_zz_m4.do_you_have_height_weight = 1 AND ad_zz_m4.measurement_taken_date BETWEEN %(m4_start)s AND %(m4_end)s AND ad_zz_m4.weight_for_age_zscore IS NOT NULL

        WHERE ad_current.do_you_have_height_weight = 1
          AND cgm.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
          AND cee.date_of_enrollment <= %(end_date)s AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (
              (
                  (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND (COALESCE(CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))) > 0
              )
              OR (
                  (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
              )
              OR (
                  (ad_gf2_priority.weight_for_age_zscore IS NOT NULL OR ad_gf2_fallback.weight_for_age_zscore IS NOT NULL)
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_gf2_priority.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_gf2_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
              )
              OR (
                  ad_zz_m1.weight_for_age_zscore IS NOT NULL AND ad_zz_m2.weight_for_age_zscore IS NOT NULL AND ad_zz_m3.weight_for_age_zscore IS NOT NULL AND ad_zz_m4.weight_for_age_zscore IS NOT NULL
                  AND ad_current.weight_for_age_zscore IS NOT NULL AND cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))
                  AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
                  AND (
                      (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                  )
                  AND (
                      (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                  )
              )
              OR ad_current.weight_for_age = 1
              OR ad_current.weight_for_height = 1
          )
    ),

    -- ── Children with at least one measured (flag = 1) record in the report month ──
    measured_children AS (
        SELECT DISTINCT ad2.childenrollguid
        FROM `tabAnthropromatic Data` ad2
        INNER JOIN `tabChild Growth Monitoring` cgm2 ON cgm2.name = ad2.parent
        WHERE ad2.do_you_have_height_weight = 1
          AND cgm2.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
    ),

    -- ── One representative un-measured record per child, so 'N' is flagged only once per child ──
    first_unmeasured AS (
        SELECT ad2.childenrollguid, MIN(ad2.name) AS first_ad
        FROM `tabAnthropromatic Data` ad2
        INNER JOIN `tabChild Growth Monitoring` cgm2 ON cgm2.name = ad2.parent
        WHERE cgm2.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
          AND (ad2.do_you_have_height_weight IS NULL OR ad2.do_you_have_height_weight <> 1)
        GROUP BY ad2.childenrollguid
    )

    SELECT
        cr.creche_name AS creche_name,
        usr.full_name AS supervisor,
        cee.child_id AS child_id,
        cr.creche_id AS creche_id,
        cee.child_name AS child_name,
        cee.age_at_enrollment_in_months AS age,
        DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS child_dob,
        CASE
            WHEN DATE_FORMAT(%(end_date)s,'%%Y-%%m') = DATE_FORMAT(CURDATE(),'%%Y-%%m')
            THEN TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE()) +
                 IF(DATE_ADD(cee.child_dob, INTERVAL TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE()) MONTH) < CURDATE(), 1, 0)
            ELSE TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) +
                 IF(DATE_ADD(cee.child_dob, INTERVAL TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) MONTH) < %(end_date)s, 1, 0)
        END AS current_age,
        CASE
            WHEN cee.gender_id = '1' THEN 'M'
            WHEN cee.gender_id = '2' THEN 'F'
            ELSE cee.gender_id
        END AS gender,
        ad.height AS height,
        ad.weight AS weight,
        pv.prev_weight AS prev_weight,
        pv.prev_height AS prev_height,
        pv.prev_weight_date AS prev_weight_date,
        pv.prev2_weight AS prev2_weight,
        pv.prev2_height AS prev2_height,
        pv.prev2_weight_date AS prev2_weight_date,
        ad.do_you_have_height_weight AS measurements_taken_raw,
        CASE
            WHEN ad.do_you_have_height_weight = 1 THEN 'Y'
            WHEN mc.childenrollguid IS NULL
                 AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
                 AND fu.first_ad = ad.name
            THEN 'N'
            ELSE '-'
        END AS measurements_taken,
        IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS measurements_taken_date,
        CASE
            WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
            WHEN ad.measurement_reason = 2 THEN 'Child not in village'
            WHEN ad.measurement_reason = 3 THEN 'Child is sick'
            WHEN ad.measurement_reason = 4 THEN 'Others'
            ELSE ''
        END AS measurement_reason,
        CASE
            WHEN ad.age_months <= 730 THEN 'Infantometer'
            WHEN ad.age_months > 730 THEN 'Stadiometer'
        END AS measurement_equipment,
        CASE
            WHEN ad.measurement_position = 1 THEN 'Standing'
            WHEN ad.measurement_position = 2 THEN 'Lying'
        END AS measurement_position,
        ad.age_months AS age_months,

        ad.weight_for_age_zscore AS weight_for_age_zscore,
        ad.weight_for_height_zscore AS weight_for_height_zscore,
        ad.height_for_age_zscore AS height_for_age_zscore,
        CASE WHEN ad.weight_for_age  = 3 THEN 'Normal'
             WHEN ad.weight_for_age  = 2 THEN 'Moderate'
             WHEN ad.weight_for_age  = 1 THEN 'Severe'
             ELSE '' END AS weight_for_age_status,
        CASE WHEN ad.height = 0 THEN '-'
             WHEN ad.height_for_age = 3 THEN 'Normal'
             WHEN ad.height_for_age = 2 THEN 'Moderate'
             WHEN ad.height_for_age = 1 THEN 'Severe'
             ELSE '' END AS height_for_age_status,
        CASE WHEN ad.height = 0 THEN '-'
             WHEN ad.weight_for_height = 3 THEN 'Normal'
             WHEN ad.weight_for_height = 2 THEN 'Moderate'
             WHEN ad.weight_for_height = 1 THEN 'Severe'
             ELSE '' END AS weight_for_height_status,

        IF(gf1_flags.ad_name  IS NOT NULL, 'Y', 'N') AS gf1_raw,
        COALESCE(gf1_flags.multiplier,  0) AS gf1_multiplier,
        IF(gf1p_flags.ad_name IS NOT NULL, 'Y', 'N') AS gf1_plus_raw,
        COALESCE(gf1p_flags.multiplier, 0) AS gf1_plus_multiplier,
        IF(gf2_flags.ad_name  IS NOT NULL, 'Y', 'N') AS gf2_raw,
        COALESCE(gf2_flags.multiplier,  0) AS gf2_multiplier,
        IF(zz_flags.ad_name   IS NOT NULL, 'Y', 'N') AS gf_zigzag_raw,
        COALESCE(zz_flags.multiplier,   0) AS gf_zigzag_multiplier,
        IF(snc_flags.ad_name  IS NOT NULL, 'Y', 'N') AS snc_raw,
        COALESCE(snc_flags.multiplier,  0) AS snc_multiplier,

        ad.any_medical_major_illness AS any_medical_major_illness,
        '-' AS red_flag_HV_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 5 THEN 'Y' END), '-') AS othr_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 4 THEN 'Y' END), '-') AS nrc_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 3 THEN 'Y' END), '-') AS chc_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 2 THEN 'Y' END), '-') AS phc_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 1 THEN 'Y' END), '-') AS vhsnd_raw,
        COALESCE(MAX(CASE WHEN cfu.name IS NOT NULL THEN 'Y' END), '-') AS follow_up_raw,
        p.partner_name  AS partner,
        s.state_name    AS state,
        d.district_name AS district,
        b.block_name    AS block,
        g.gp_name       AS gp

    FROM `tabAnthropromatic Data` AS ad
    INNER JOIN `tabChild Growth Monitoring`  AS cgm ON ad.parent           = cgm.name
    INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
    INNER JOIN `tabCreche`                   AS cr  ON cgm.creche_id        = cr.name

    LEFT JOIN `tabUser`           AS usr ON cr.supervisor_id = usr.name
    LEFT JOIN `tabPartner`        AS p   ON p.name           = cr.partner_id
    LEFT JOIN `tabState`          AS s   ON s.name           = cr.state_id
    LEFT JOIN `tabDistrict`       AS d   ON d.name           = cr.district_id
    LEFT JOIN `tabBlock`          AS b   ON b.name           = cr.block_id
    LEFT JOIN `tabGram Panchayat` AS g   ON g.name           = cr.gp_id

    LEFT JOIN ad_pivot   AS pv  ON pv.childenrollguid  = ad.childenrollguid
    LEFT JOIN gf1_flags  ON gf1_flags.ad_name  = ad.name
    LEFT JOIN gf1p_flags ON gf1p_flags.ad_name = ad.name
    LEFT JOIN gf2_flags  ON gf2_flags.ad_name  = ad.name
    LEFT JOIN zz_flags   ON zz_flags.ad_name   = ad.name
    LEFT JOIN snc_flags  ON snc_flags.ad_name  = ad.name
    LEFT JOIN measured_children AS mc ON mc.childenrollguid = ad.childenrollguid
    LEFT JOIN first_unmeasured  AS fu ON fu.childenrollguid = ad.childenrollguid

    LEFT JOIN `tabChild Referral`  AS crf ON crf.childenrolledguid = ad.childenrollguid
        AND crf.date_of_referral BETWEEN %(crf_start)s AND %(crf_end)s
    LEFT JOIN `tabChild Follow up` AS cfu ON cfu.childenrolledguid = ad.childenrollguid
        AND cfu.followup_visit_date BETWEEN %(crf_start)s AND %(crf_end)s

    WHERE cgm.measurement_date BETWEEN %(cgm_start)s AND %(cgm_end)s
      AND cee.date_of_enrollment <= %(end_date)s
      AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
      AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
      AND (
          (%(state_id)s IS NOT NULL AND cr.state_id = %(state_id)s)
          OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
          OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
      )
      AND (
          (%(district_id)s IS NOT NULL AND cr.district_id = %(district_id)s)
          OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cr.district_id, %(district_ids)s))
          OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
      )
      AND (
          (%(block_id)s IS NOT NULL AND cr.block_id = %(block_id)s)
          OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cr.block_id, %(block_ids)s))
          OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
      )
      AND (
          (%(gp_id)s IS NOT NULL AND cr.gp_id = %(gp_id)s)
          OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
          OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
      )
      AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
      AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
      AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
      AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
      AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
      AND (
          (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
          OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
      )

    GROUP BY ad.name, cgm.name, cee.name, cr.name, usr.name, p.name, s.name, d.name, b.name, g.name
    ORDER BY cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id,
             cr.supervisor_id, cr.name, cee.child_name
    """

    return frappe.db.sql(sql_query, params, as_dict=True)


def _zscore_color(value, sd3neg, sd2neg, sd2):
    if value < sd3neg:
        return "#FFCCCC", "#CC0000"
    elif value < sd2neg:
        return "#FFFFCC", "#999900"
    elif value <= sd2:
        return "#CCFFCC", "#006600"
    else:
        return "#E6E6E6", "#666666"


def _compute_wfa_zscore(row, ref_tables):
    age_in_days = row.get("age_months")
    gender_id   = row.get("gender_id") or ("1" if row.get("gender") == "M" else "2" if row.get("gender") == "F" else None)
    weight      = row.get("weight")

    if age_in_days is None or weight is None or gender_id not in ("1", "2"):
        return None, None
    try:
        age_in_days = int(age_in_days)
        weight = float(weight)
        if weight <= 0:
            return None, None
    except (TypeError, ValueError):
        return None, None

    table = ref_tables["wfa_boys"] if gender_id == "1" else ref_tables["wfa_girls"]
    gd = table.get(age_in_days)
    if not gd:
        return None, None
    try:
        z = calculate_z_score(weight, float(gd["m"]), float(gd["l"]), float(gd["s"]))
        bg, fg = _zscore_color(weight, float(gd["sd3neg"]), float(gd["sd2neg"]), float(gd["sd2"]))
        return z, (bg, fg)
    except (ValueError, TypeError):
        return None, None


def _compute_wfh_zscore(row, ref_tables):
    age_in_days = row.get("age_months")
    gender_id   = row.get("gender_id") or ("1" if row.get("gender") == "M" else "2" if row.get("gender") == "F" else None)
    weight      = row.get("weight")
    height      = row.get("height")
    equip       = row.get("measurement_equipment", "")

    if age_in_days is None or weight is None or height is None or gender_id not in ("1", "2"):
        return None, None
    try:
        age_in_days   = int(age_in_days)
        weight        = float(weight)
        height_rounded = round(float(height), 1)
        if weight <= 0 or height_rounded <= 0:
            return None, None
    except (TypeError, ValueError):
        return None, None

    if age_in_days < 730 and equip == "Stadiometer":
        height_rounded = round(height_rounded + 0.7, 1)
    if age_in_days > 730 and equip == "Infantometer":
        height_rounded = round(height_rounded - 0.7, 1)

    wfh_raw = ref_tables["wfh_boys"] if gender_id == "1" else ref_tables["wfh_girls"]
    age_key = "0" if age_in_days <= 730 else "24"
    records = wfh_raw.get(height_rounded, [])
    gd = next((r for r in records if str(r.get("age_type", "")).strip() in (age_key, f"{age_key}.0")), None)
    if not gd:
        return None, None
    try:
        z = calculate_z_score(weight, float(gd["m"]), float(gd["l"]), float(gd["s"]))
        bg, fg = _zscore_color(weight, float(gd["sd3neg"]), float(gd["sd2neg"]), float(gd["sd2"]))
        return z, (bg, fg)
    except (ValueError, TypeError):
        return None, None


def _compute_hfa_zscore(row, ref_tables):
    age_in_days = row.get("age_months")
    gender_id   = row.get("gender_id") or ("1" if row.get("gender") == "M" else "2" if row.get("gender") == "F" else None)
    height      = row.get("height")
    equip       = row.get("measurement_equipment", "")
    meas_date_str = row.get("measurements_taken_date", "")

    if age_in_days is None or height is None or gender_id not in ("1", "2"):
        return None, None
    try:
        age_in_days = int(age_in_days)
        h = float(height)
        if h <= 0:
            return None, None
    except (TypeError, ValueError):
        return None, None

    if equip and meas_date_str and meas_date_str != "-":
        try:
            measurement_date = datetime.strptime(meas_date_str, "%d-%m-%Y").date()
            dob = measurement_date - timedelta(days=age_in_days)
            two_years_ago = measurement_date - relativedelta(months=24)
            if dob > two_years_ago:
                if equip == "Stadiometer":
                    h = round(h + 0.7, 1)
            else:
                if equip == "Infantometer":
                    h = round(h - 0.7, 1)
        except (ValueError, TypeError):
            pass

    table = ref_tables["hfa_boys"] if gender_id == "1" else ref_tables["hfa_girls"]
    gd = table.get(age_in_days)
    if not gd:
        return None, None
    try:
        z = calculate_z_score(h, float(gd["m"]), float(gd["l"]), float(gd["s"]))
        bg, fg = _zscore_color(h, float(gd["sd3neg"]), float(gd["sd2neg"]), float(gd["sd2"]))
        return z, (bg, fg)
    except (ValueError, TypeError):
        return None, None


def process_data(data, ref_tables):
    for row in data:
        # Dynamically calculate and colour the three z-score columns
        wfa_z, wfa_colors = _compute_wfa_zscore(row, ref_tables)
        if wfa_z is not None:
            row["weight_for_age_zscore"] = format_cell(wfa_z, wfa_colors[0], wfa_colors[1])
        elif row.get("weight_for_age_zscore") is not None and row.get("weight_for_age_zscore") != "":
            status = row.get("weight_for_age_status", "").lower()
            row["weight_for_age_zscore"] = format_zscore_cell(row["weight_for_age_zscore"], status)

        wfh_z, wfh_colors = _compute_wfh_zscore(row, ref_tables)
        if wfh_z is not None:
            row["weight_for_height_zscore"] = format_cell(wfh_z, wfh_colors[0], wfh_colors[1])
        elif row.get("weight_for_height_zscore") is not None and row.get("weight_for_height_zscore") != "":
            status = row.get("weight_for_height_status", "").lower()
            row["weight_for_height_zscore"] = format_zscore_cell(row["weight_for_height_zscore"], status)

        hfa_z, hfa_colors = _compute_hfa_zscore(row, ref_tables)
        if hfa_z is not None:
            row["height_for_age_zscore"] = format_cell(hfa_z, hfa_colors[0], hfa_colors[1])
        elif row.get("height_for_age_zscore") is not None and row.get("height_for_age_zscore") != "":
            status = row.get("height_for_age_status", "").lower()
            row["height_for_age_zscore"] = format_zscore_cell(row["height_for_age_zscore"], status)

        flag_fields = [
            ("gf1_raw",        "gf1"),
            ("gf1_plus_raw",   "gf1_plus"),
            ("gf2_raw",        "gf2"),
            ("gf_zigzag_raw",  "gf_zigzag"),
            ("snc_raw",        "snc"),
            ("red_flag_raw",   "red_flag"),
        ]
        for raw_field, display_field in flag_fields:
            raw_val = row.get(raw_field, "N")
            bg = "#FFE0E0" if raw_val == "Y" else "#E8F5E9"
            fg = "#CC0000" if raw_val == "Y" else "#2E7D32"
            row[display_field] = format_flag_cell(raw_val, bg, fg)

        row["red_flag_HV"] = format_flag_cell(row.get("red_flag_HV_raw", "-"), "#E8F5E9", "#2E7D32")

        weight      = row.get("weight")
        height      = row.get("height")
        prev_weight = row.get("prev_weight")
        prev_height = row.get("prev_height")
        age_months  = row.get("current_age") or row.get("age_months")
        gender      = row.get("gender", "")

        def _missing(v):
            try:
                return v is None or v == "" or float(v) == 0
            except (TypeError, ValueError):
                return True

        weight_missing      = _missing(weight)
        height_missing      = _missing(height)
        prev_weight_missing = _missing(prev_weight)
        prev_height_missing = _missing(prev_height)

        weight_implausible_val = "-" if weight_missing else check_weight_implausible(weight, age_months, gender)
        height_implausible_val = "-" if height_missing else check_height_implausible(height, age_months, gender)

        # Weight Less Than 2kg: current weight dropped by ≥ 2 kg compared to previous month
        if weight_missing or prev_weight_missing:
            weight_less_than_2kg_val = "-"
        else:
            try:
                weight_less_than_2kg_val = "Yes" if (float(prev_weight) - float(weight)) >= 2 else "No"
            except (TypeError, ValueError):
                weight_less_than_2kg_val = "-"

        # Any Reduction In Height: current height is less than previous month's height
        if height_missing or prev_height_missing:
            any_reduction_in_height_val = "-"
        else:
            try:
                any_reduction_in_height_val = "Yes" if float(height) < float(prev_height) else "No"
            except (TypeError, ValueError):
                any_reduction_in_height_val = "-"

        # Build the 2-month history popup data embedded in a data attribute
        def _fmt_date(d):
            if not d:
                return "-"
            try:
                if hasattr(d, "strftime"):
                    return d.strftime("%d-%m-%Y")
                return str(d)
            except Exception:
                return str(d)

        meas_date    = row.get("measurements_taken_date", "-")
        curr_w       = "" if weight_missing else weight
        curr_h       = "" if height_missing else height
        prev_w       = "" if prev_weight_missing else prev_weight
        prev_h       = "" if prev_height_missing else prev_height
        prev_date    = _fmt_date(row.get("prev_weight_date"))
        prev2_w      = row.get("prev2_weight") or ""
        prev2_h      = row.get("prev2_height") or ""
        prev2_date   = _fmt_date(row.get("prev2_weight_date"))

        import json as _json
        row["_history_json"] = _json.dumps({
            "child":  row.get("child_name", ""),
            "dob":    row.get("child_dob", ""),
            "curr":   {"date": meas_date,  "weight": str(curr_w),  "height": str(curr_h)},
            "prev":   {"date": prev_date,  "weight": str(prev_w),  "height": str(prev_h)},
            "prev2":  {"date": prev2_date, "weight": str(prev2_w), "height": str(prev2_h)},
        })

        row["weight_implausible"]      = weight_implausible_val
        row["height_implausible"]      = height_implausible_val
        row["weight_less_than_2kg"]    = weight_less_than_2kg_val
        row["any_reduction_in_height"] = any_reduction_in_height_val

        for field in ["othr", "nrc", "chc", "phc", "vhsnd", "follow_up"]:
            raw_val = row.get(f"{field}_raw", "-")
            if raw_val == "Y":
                row[field] = format_flag_cell("Y", "#E8F5E9", "#2E7D32")
            else:
                row[field] = format_flag_cell("-", "#F5F5F5", "#999999")

    return data


def add_summary_row(data):
    counts = {
        "child_name": 0, "measurements_taken": 0, "gf1": 0, "gf1_plus": 0,
        "gf2": 0, "gf_zigzag": 0, "snc": 0, "any_medical_major_illness": 0,
        "red_flag": 0, "red_flag_HV": 0, "follow_up": 0, "vhsnd": 0,
        "phc": 0, "chc": 0, "nrc": 0, "othr": 0,
    }

    for row in data:
        counts["child_name"] += 1

        if row.get("measurements_taken_raw") == 1:
            counts["measurements_taken"] += 1

        # Use the hidden multiplier specifically for GF indicators to match the Summary report duplicates exactly
        for field in ["gf1", "gf1_plus", "gf2", "gf_zigzag", "snc"]:
            if row.get(f"{field}_raw") == "Y":
                counts[field] += row.get(f"{field}_multiplier", 1)

        # Standard +1 count for other standard indicators
        for field in ["nrc", "phc", "chc", "vhsnd", "follow_up", "red_flag", "othr"]:
            if row.get(f"{field}_raw") == "Y":
                counts[field] += 1

        if row.get("red_flag_HV_raw") == "Y":
            counts["red_flag_HV"] += 1
        if row.get("any_medical_major_illness") == 1:
            counts["any_medical_major_illness"] += 1

    summary_row = {
        "partner":                  "<b style='color:black;'>Total</b>",
        "child_name":               f"<b>{counts['child_name']}</b>",
        "measurements_taken":       f"<b>{counts['measurements_taken']}</b>",
        "gf1":                      f"<b>{counts['gf1']}</b>",
        "gf1_plus":                 f"<b>{counts['gf1_plus']}</b>",
        "gf2":                      f"<b>{counts['gf2']}</b>",
        "gf_zigzag":                f"<b>{counts['gf_zigzag']}</b>",
        "snc":                      f"<b>{counts['snc']}</b>",
        "any_medical_major_illness":f"<b>{counts['any_medical_major_illness']}</b>",
        "red_flag":                 f"<b>{counts['red_flag']}</b>",
        "red_flag_HV":              f"<b>{counts['red_flag_HV']}</b>",
        "follow_up":                f"<b>{counts['follow_up']}</b>",
        "vhsnd":                    f"<b>{counts['vhsnd']}</b>",
        "phc":                      f"<b>{counts['phc']}</b>",
        "chc":                      f"<b>{counts['chc']}</b>",
        "nrc":                      f"<b>{counts['nrc']}</b>",
        "othr":                     f"<b>{counts['othr']}</b>",
    }

    data.append(summary_row)
    return data


# WHO plausible range tables: key = age_months, value = (min_plausible, max_plausible)
# Weight (kg): -4 SD to +3 SD
WHO_WEIGHT_BOYS = {
    6:  (5.1, 11.0),  7:  (5.4, 11.4),  8:  (5.6, 11.9),  9:  (5.8, 12.3),
    10: (5.9, 12.7),  11: (6.1, 13.0),  12: (6.2, 13.3),  13: (6.3, 13.7),
    14: (6.5, 14.0),  15: (6.6, 14.3),  16: (6.7, 14.6),  17: (6.8, 14.9),
    18: (6.9, 15.1),  19: (7.1, 15.4),  20: (7.2, 15.7),  21: (7.3, 16.0),
    22: (7.4, 16.2),  23: (7.6, 16.5),  24: (7.7, 16.8),  25: (7.8, 17.1),
    26: (7.9, 17.3),  27: (8.0, 17.6),  28: (8.1, 17.9),  29: (8.2, 18.2),
    30: (8.3, 18.4),  31: (8.4, 18.7),  32: (8.5, 19.0),  33: (8.6, 19.3),
    34: (8.7, 19.6),  35: (8.8, 19.8),  36: (8.9, 20.1),
}

WHO_WEIGHT_GIRLS = {
    6:  (4.5, 10.2),  7:  (4.7, 10.6),  8:  (4.9, 11.1),  9:  (5.0, 11.4),
    10: (5.2, 11.8),  11: (5.3, 12.2),  12: (5.4, 12.5),  13: (5.6, 12.8),
    14: (5.7, 13.1),  15: (5.8, 13.4),  16: (5.9, 13.7),  17: (6.0, 14.0),
    18: (6.1, 14.3),  19: (6.2, 14.6),  20: (6.3, 14.9),  21: (6.5, 15.2),
    22: (6.6, 15.5),  23: (6.7, 15.8),  24: (6.8, 16.1),  25: (6.9, 16.4),
    26: (7.0, 16.7),  27: (7.1, 17.0),  28: (7.2, 17.3),  29: (7.3, 17.6),
    30: (7.4, 17.9),  31: (7.5, 18.2),  32: (7.6, 18.5),  33: (7.7, 18.8),
    34: (7.8, 19.1),  35: (7.9, 19.4),  36: (8.0, 19.7),
}

# Height (cm): -4 SD to +3 SD
WHO_HEIGHT_BOYS = {
    6:  (60.4, 75.4),  7:  (61.7, 77.1),  8:  (63.0, 78.7),  9:  (64.3, 80.3),
    10: (65.4, 81.7),  11: (66.5, 83.2),  12: (67.6, 84.5),  13: (68.6, 85.9),
    14: (69.6, 87.1),  15: (70.6, 88.4),  16: (71.6, 89.6),  17: (72.5, 90.8),
    18: (73.4, 92.0),  19: (74.3, 93.1),  20: (75.2, 94.2),  21: (76.0, 95.3),
    22: (76.8, 96.4),  23: (77.7, 97.4),  24: (78.0, 97.7),  25: (78.6, 98.7),
    26: (79.3, 99.6),  27: (79.9, 100.5), 28: (80.5, 101.4), 29: (81.1, 102.3),
    30: (81.7, 103.1), 31: (82.3, 104.0), 32: (82.8, 104.8), 33: (83.4, 105.6),
    34: (83.9, 106.4), 35: (84.4, 107.2), 36: (85.0, 108.0),
}

WHO_HEIGHT_GIRLS = {
    6:  (58.6, 73.5),  7:  (59.9, 75.3),  8:  (61.2, 76.9),  9:  (62.5, 78.5),
    10: (63.7, 80.0),  11: (64.9, 81.5),  12: (66.0, 82.9),  13: (67.0, 84.3),
    14: (68.0, 85.7),  15: (69.0, 87.0),  16: (70.0, 88.2),  17: (70.9, 89.4),
    18: (71.8, 90.7),  19: (72.8, 91.9),  20: (73.7, 93.1),  21: (74.5, 94.2),
    22: (75.2, 95.4),  23: (76.0, 96.5),  24: (76.0, 96.9),  25: (76.8, 98.0),
    26: (77.5, 99.0),  27: (78.1, 100.1), 28: (78.8, 101.1), 29: (79.5, 102.0),
    30: (80.1, 103.0), 31: (80.7, 103.9), 32: (81.3, 104.9), 33: (81.9, 105.8),
    34: (82.5, 106.7), 35: (83.1, 107.5), 36: (83.6, 108.4),
}


def check_weight_implausible(weight, age_months, gender):
    try:
        w = float(weight)
        age = int(age_months)
    except (TypeError, ValueError):
        return ""
    table = WHO_WEIGHT_BOYS if str(gender).upper() == "M" else WHO_WEIGHT_GIRLS
    limits = table.get(age)
    if limits is None:
        return ""
    low, high = limits
    if w < low:
        return "Yes ↓"
    if w > high:
        return "Yes ↑"
    return "No"


def check_height_implausible(height, age_months, gender):
    try:
        h = float(height)
        age = int(age_months)
    except (TypeError, ValueError):
        return ""
    table = WHO_HEIGHT_BOYS if str(gender).upper() == "M" else WHO_HEIGHT_GIRLS
    limits = table.get(age)
    if limits is None:
        return ""
    low, high = limits
    if h < low:
        return "Yes ↓"
    if h > high:
        return "Yes ↑"
    return "No"


def format_zscore_cell(value, status):
    if value is None or value == '':
        return value

    color_map = {
        "severe":   ("#FFCCCC", "#CC0000"),
        "moderate": ("#FFFFCC", "#999900"),
        "normal":   ("#CCFFCC", "#006600"),
    }
    if status in color_map:
        bg, fg = color_map[status]
        return format_cell(value, bg, fg)
    return str(value)


def format_flag_cell(value, bg_color, text_color):
    return format_cell(value, bg_color, text_color)


def format_cell(value, bg_color, text_color):
    if value is None:
        return ""
    return (
        f"<div style='"
        f"background-color:{bg_color};"
        f"color:{text_color};"
        f"border-radius:3px;"
        f"text-align:center;"
        f"font-weight:bold;"
        f"padding:2px 5px;"
        f"'>{value}</div>"
    )