import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

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
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
        variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 150})

    fixed_columns = [
        {"label": "Active Creches", "fieldname": "op_creches", "fieldtype": "Data", "width": 180},
        {"label": "GM Submitted", "fieldname": "gm_entered", "fieldtype": "Data", "width": 180},

        {"label": "Enrolled Children", "fieldname": "e_children", "fieldtype": "Data", "width": 150},
        {"label": "Measurement Taken", "fieldname": "g_children", "fieldtype": "Data", "width": 180},
        {"label": "Measurement (%)", "fieldname": "e_children_percentage", "fieldtype": "Data", "width": 150},

        {"label": "Child Not In Creche", "fieldname": "child_not_in_creche", "fieldtype": "Data", "width": 180},
        {"label": "Child Not In Village", "fieldname": "child_not_in_village", "fieldtype": "Data", "width": 180},
        {"label": "Child is Sick", "fieldname": "child_is_sick", "fieldtype": "Data", "width": 180},
        {"label": "Other", "fieldname": "other", "fieldtype": "Data", "width": 180},

        {"label": "WFA - Normal", "fieldname": "weight_for_age_normal", "fieldtype": "Data", "width": 130},
        {"label": "WFA - Normal (%)", "fieldname": "per_weight_for_age_normal", "fieldtype": "Data", "width": 150},
        {"label": "WFA - Moderate", "fieldname": "weight_for_age_moderate", "fieldtype": "Data", "width": 140},
        {"label": "WFA - Moderate (%)", "fieldname": "per_weight_for_age_moderate", "fieldtype": "Data", "width": 160},
        {"label": "WFA - Severe", "fieldname": "weight_for_age_severe", "fieldtype": "Data", "width": 130},
        {"label": "WFA - Severe (%)", "fieldname": "per_weight_for_age_severe", "fieldtype": "Data", "width": 150},

        {"label": "WFH - Normal", "fieldname": "weight_for_height_normal", "fieldtype": "Data", "width": 130},
        {"label": "WFH - Normal (%)", "fieldname": "per_weight_for_height_normal", "fieldtype": "Data", "width": 150},
        {"label": "WFH - Moderate", "fieldname": "weight_for_height_moderate", "fieldtype": "Data", "width": 140},
        {"label": "WFH - Moderate (%)", "fieldname": "per_weight_for_height_moderate", "fieldtype": "Data", "width": 160},
        {"label": "WFH - Severe", "fieldname": "weight_for_height_severe", "fieldtype": "Data", "width": 130},
        {"label": "WFH - Severe (%)", "fieldname": "per_weight_for_height_severe", "fieldtype": "Data", "width": 150},

        {"label": "HFA - Normal", "fieldname": "height_for_age_normal", "fieldtype": "Data", "width": 130},
        {"label": "HFA - Normal (%)", "fieldname": "per_height_for_age_normal", "fieldtype": "Data", "width": 150},
        {"label": "HFA - Moderate", "fieldname": "height_for_age_moderate", "fieldtype": "Data", "width": 140},
        {"label": "HFA - Moderate (%)", "fieldname": "per_height_for_age_moderate", "fieldtype": "Data", "width": 160},
        {"label": "HFA - Severe", "fieldname": "height_for_age_severe", "fieldtype": "Data", "width": 130},
        {"label": "HFA - Severe (%)", "fieldname": "per_height_for_age_severe", "fieldtype": "Data", "width": 150},

        {"label": "Growth Faltering 1", "fieldname": "gf1", "fieldtype": "Data", "width": 170},
        {"label": "Growth Faltering 1+", "fieldname": "gf1_plus", "fieldtype": "Data", "width": 170},
        {"label": "Growth Faltering 2", "fieldname": "gf2", "fieldtype": "Data", "width": 150},
        {"label": "Zig-Zag", "fieldname": "zigzag", "fieldtype": "Data", "width": 150},
        {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 150},

        # {"label": "Referred to Health Facility", "fieldname": "hf", "fieldtype": "Data", "width": 260},
        # {"label": "Referred to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 250},
        # {"label": "Referred to VHND", "fieldname": "vhnd", "fieldtype": "Data", "width": 250},
        # {"label": "Followup Visits Done", "fieldname": "cfu", "fieldtype": "Data", "width": 250},
    ]

    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
    return columns, data


def get_report_data(filters):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # ── 1 month ago (GF1 / GF1+ primary) ──────────────────────────────────
    if month == 1:
        lmonth = 12
        lyear  = year - 1
    else:
        lmonth = month - 1
        lyear  = year

    # ── 2 months ago (GF1 / GF1+ fallback  AND  GF2 primary) ────────────
    if month == 1:
        plmonth = 11
        pyear   = year - 1
    elif month == 2:
        plmonth = 12
        pyear   = year - 1
    else:
        plmonth = month - 2
        pyear   = year

    # ── 3 months ago (GF2 fallback  AND  zigzag m3) ───────────────────────
    if plmonth == 1:
        l2month = 12
        l2year  = pyear - 1
    else:
        l2month = plmonth - 1
        l2year  = pyear

    # ── 4 months ago (zigzag m4) ──────────────────────────────────────────
    if l2month == 1:
        l3month = 12
        l3year  = l2year - 1
    else:
        l3month = l2month - 1
        l3year  = l2year

    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "lyear": lyear,
        "lmonth": lmonth,
        "pyear": pyear,
        "plmonth": plmonth,
        "l2year": l2year,
        "l2month": l2month,
        "l3year": l3year,
        "l3month": l3month,
        "cstart_date": None,
        "cend_date": None,
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
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_ids    = ",".join(str(s["state_id"])    for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids    = ",".join(str(s["block_id"])    for s in current_user_state if s.get("block_id"))
    gp_ids       = ",".join(str(s["gp_id"])       for s in current_user_state if s.get("gp_id"))

    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

    if range_type:
        single_date = filters.get("single_date")
        date_range  = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()

        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
        elif range_type == "before" and single_date:
            cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            cstart_date, cend_date = single_date + timedelta(days=1), date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        params["partner"] = partner_id
    if filters.get("state"):
        conditions.append("c.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
            params["state_ids"] = state_ids
            params["state"] = None

    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
            params["district_ids"] = district_ids
            params["district"] = None

    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
            params["block_ids"] = block_ids
            params["block"] = None

    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
        params["gp_ids"] = None
    else:
        if gp_ids:
            conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
            params["gp_ids"] = gp_ids
            params["gp"] = None

    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
        params["creche"] = filters.get("creche")
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")
    if filters.get("creche_status_id"):
        conditions.append("(c.creche_status_id = %(creche_status_id)s)")
        params["creche_status_id"] = filters.get("creche_status_id")
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
        if phases_cleaned:
            conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
            params["phases"] = phases_cleaned
    if cstart_date or cend_date:
        conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
        params["cstart_date"] = cstart_date if cstart_date else None
        params["cend_date"]   = cend_date   if cend_date   else None

    creche_age = filters.get("creche_age", "")
    params["creche_age"] = creche_age
    if creche_age:
        conditions.append("""
            CASE
                WHEN c.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                ELSE ''
            END = %(creche_age)s
        """)

    level_mapping = {
        "1": ["tf.partner"],
        "2": ["tf.state"],
        "3": ["tf.state", "tf.district"],
        "4": ["tf.state", "tf.district", "tf.block"],
        "5": ["tf.state", "tf.district", "tf.block", "tf.supervisor"],
        "6": ["tf.state", "tf.district", "tf.block", "tf.gp"],
        "7": ["tf.state", "tf.district", "tf.block", "tf.gp", "tf.supervisor", "tf.creche"],
    }

    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field  = ", ".join(group_by_fields)

    select_fields = [
        "tf.partner AS partner",
        "tf.state AS state",
        "tf.district AS district",
        "tf.block AS block",
        "tf.supervisor AS supervisor",
        "tf.gp AS gp",
        "tf.creche AS creche",
    ]
    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in gbf for gbf in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)

    query = f"""
    WITH
    -- ── Enrolled children ────────────────────────────────────────────────
    ec AS (
        SELECT
            cee.creche_id,
            COUNT(DISTINCT cee.childenrollguid) AS e_children
        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
        WHERE cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(start_date)s)
        GROUP BY cee.creche_id
    ),

    -- ── Measurements taken ───────────────────────────────────────────────
    gc AS (
        SELECT
            cgm.creche_id,
            COUNT(ad.childenrollguid) AS g_children
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
        WHERE ad.do_you_have_height_weight = 1
          AND YEAR(cgm.measurement_date) = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        GROUP BY cgm.creche_id
    ),

-- ── Growth Faltering 1 ───────────────────────────────────────────────
    gf1c AS (
        SELECT
            cgm.creche_id,
            COUNT(ad.childenrollguid) AS gf1
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid

        -- primary: 1 month ago
        LEFT JOIN `tabAnthropromatic Data` ad_prev
            ON  ad_prev.childenrollguid  = ad.childenrollguid
            AND ad_prev.do_you_have_height_weight = 1
            AND YEAR(ad_prev.measurement_taken_date)  = %(lyear)s
            AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
            AND ad_prev.weight_for_age_zscore IS NOT NULL

        -- fallback: 2 months ago
        LEFT JOIN `tabAnthropromatic Data` ad_fallback
            ON  ad_fallback.childenrollguid        = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1
            AND YEAR(ad_fallback.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_fallback.measurement_taken_date) = %(plmonth)s
            AND ad_fallback.weight_for_age_zscore IS NOT NULL
            AND ad_prev.childenrollguid IS NULL

        WHERE ad.do_you_have_height_weight = 1
          AND ad.weight_for_age_zscore IS NOT NULL
          AND YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
          AND (ad_prev.weight_for_age_zscore IS NOT NULL
               OR ad_fallback.weight_for_age_zscore IS NOT NULL)
          AND (
              COALESCE(ad_prev.weight_for_age_zscore, ad_fallback.weight_for_age_zscore)
              - ad.weight_for_age_zscore
          ) > 0
        GROUP BY cgm.creche_id
    ),

    -- ── Growth Faltering 1+ (WITH EXPLICIT CAST as per API) ──────────────
    gf1pc AS (
        SELECT
            cgm.creche_id,
            COUNT(ad.childenrollguid) AS gf1_plus
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid

        LEFT JOIN `tabAnthropromatic Data` ad_prev
            ON  ad_prev.childenrollguid        = ad.childenrollguid
            AND ad_prev.do_you_have_height_weight = 1
            AND YEAR(ad_prev.measurement_taken_date)  = %(lyear)s
            AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
            AND ad_prev.weight_for_age_zscore IS NOT NULL

        LEFT JOIN `tabAnthropromatic Data` ad_fallback
            ON  ad_fallback.childenrollguid        = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1
            AND YEAR(ad_fallback.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_fallback.measurement_taken_date) = %(plmonth)s
            AND ad_fallback.weight_for_age_zscore IS NOT NULL
            AND ad_prev.childenrollguid IS NULL

        WHERE ad.do_you_have_height_weight = 1
          AND ad.weight_for_age_zscore IS NOT NULL
          AND YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
          AND (ad_prev.weight_for_age_zscore IS NOT NULL
               OR ad_fallback.weight_for_age_zscore IS NOT NULL)
          AND (
              CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
              - COALESCE(
                  CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                  CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
              )
          ) <= -0.5
        GROUP BY cgm.creche_id
    ),

    -- ── Growth Faltering 2 ───────────────────────────────────────────────
    gf2c AS (
        SELECT
            cgm.creche_id,
            COUNT(DISTINCT ad.childenrollguid) AS gf2
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid

        -- priority: 2 months ago
        LEFT JOIN `tabAnthropromatic Data` ad_priority
            ON  ad_priority.childenrollguid        = ad.childenrollguid
            AND ad_priority.do_you_have_height_weight = 1
            AND YEAR(ad_priority.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_priority.measurement_taken_date) = %(plmonth)s
            AND ad_priority.weight_for_age_zscore IS NOT NULL

        -- fallback: 3 months ago
        LEFT JOIN `tabAnthropromatic Data` ad_fallback
            ON  ad_fallback.childenrollguid        = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1
            AND YEAR(ad_fallback.measurement_taken_date)  = %(l2year)s
            AND MONTH(ad_fallback.measurement_taken_date) = %(l2month)s
            AND ad_fallback.weight_for_age_zscore IS NOT NULL
            AND ad_priority.childenrollguid IS NULL

        WHERE ad.do_you_have_height_weight = 1
          AND ad.weight_for_age_zscore IS NOT NULL
          AND YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
          AND (ad_priority.weight_for_age_zscore IS NOT NULL
               OR ad_fallback.weight_for_age_zscore IS NOT NULL)
          AND (
              CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
              - COALESCE(
                  CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                  CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
              )
          ) <= -0.5
        GROUP BY cgm.creche_id
    ),

    -- ── Zig-Zag (FIXED: INNER JOINs + Clean API Logic) ───────────────────
    zigzagc AS (
        SELECT
            cgm.creche_id,
            COUNT(ad_current.childenrollguid) AS zigzag
        FROM `tabAnthropromatic Data` ad_current
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad_current.childenrollguid

        INNER JOIN `tabAnthropromatic Data` ad_m1
            ON  ad_m1.childenrollguid        = ad_current.childenrollguid
            AND ad_m1.do_you_have_height_weight = 1
            AND YEAR(ad_m1.measurement_taken_date)  = %(lyear)s
            AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
            AND ad_m1.weight_for_age_zscore IS NOT NULL

        INNER JOIN `tabAnthropromatic Data` ad_m2
            ON  ad_m2.childenrollguid        = ad_current.childenrollguid
            AND ad_m2.do_you_have_height_weight = 1
            AND YEAR(ad_m2.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
            AND ad_m2.weight_for_age_zscore IS NOT NULL

        INNER JOIN `tabAnthropromatic Data` ad_m3
            ON  ad_m3.childenrollguid        = ad_current.childenrollguid
            AND ad_m3.do_you_have_height_weight = 1
            AND YEAR(ad_m3.measurement_taken_date)  = %(l2year)s
            AND MONTH(ad_m3.measurement_taken_date) = %(l2month)s
            AND ad_m3.weight_for_age_zscore IS NOT NULL

        INNER JOIN `tabAnthropromatic Data` ad_m4
            ON  ad_m4.childenrollguid        = ad_current.childenrollguid
            AND ad_m4.do_you_have_height_weight = 1
            AND YEAR(ad_m4.measurement_taken_date)  = %(l3year)s
            AND MONTH(ad_m4.measurement_taken_date) = %(l3month)s
            AND ad_m4.weight_for_age_zscore IS NOT NULL

        WHERE ad_current.do_you_have_height_weight = 1
          AND ad_current.weight_for_age_zscore IS NOT NULL
          AND YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
          AND cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))
          AND (
              CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
              - GREATEST(
                  CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)),
                  CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                  CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)),
                  CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))
              )
          ) <= -0.5
        GROUP BY cgm.creche_id
    ),


    -- ── SNC (FIXED WITH FALLBACKS) ───────────────────────────────────────
    sncc AS (
        SELECT
            cgm.creche_id,
            COUNT(DISTINCT ad_current.childenrollguid) AS snc
        FROM `tabAnthropromatic Data` AS ad_current
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad_current.childenrollguid

        -- GF1 / GF1+: primary (1 month ago)
        LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_prev
            ON  ad_gf1_prev.childenrollguid        = ad_current.childenrollguid
            AND ad_gf1_prev.do_you_have_height_weight = 1
            AND YEAR(ad_gf1_prev.measurement_taken_date)  = %(lyear)s
            AND MONTH(ad_gf1_prev.measurement_taken_date) = %(lmonth)s
            AND ad_gf1_prev.weight_for_age_zscore IS NOT NULL

        -- GF1 / GF1+: fallback (2 months ago)
        LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_fallback
            ON  ad_gf1_fallback.childenrollguid        = ad_current.childenrollguid
            AND ad_gf1_fallback.do_you_have_height_weight = 1
            AND YEAR(ad_gf1_fallback.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_gf1_fallback.measurement_taken_date) = %(plmonth)s
            AND ad_gf1_fallback.weight_for_age_zscore IS NOT NULL
            AND ad_gf1_prev.childenrollguid IS NULL

        -- GF2: priority (2 months ago)
        LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_priority
            ON  ad_gf2_priority.childenrollguid        = ad_current.childenrollguid
            AND ad_gf2_priority.do_you_have_height_weight = 1
            AND YEAR(ad_gf2_priority.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_gf2_priority.measurement_taken_date) = %(plmonth)s
            AND ad_gf2_priority.weight_for_age_zscore IS NOT NULL

        -- GF2: fallback (3 months ago)
        LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_fallback
            ON  ad_gf2_fallback.childenrollguid        = ad_current.childenrollguid
            AND ad_gf2_fallback.do_you_have_height_weight = 1
            AND YEAR(ad_gf2_fallback.measurement_taken_date)  = %(l2year)s
            AND MONTH(ad_gf2_fallback.measurement_taken_date) = %(l2month)s
            AND ad_gf2_fallback.weight_for_age_zscore IS NOT NULL
            AND ad_gf2_priority.childenrollguid IS NULL

        -- Zig-Zag: 4 previous months
        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m1
            ON  ad_zz_m1.childenrollguid        = ad_current.childenrollguid
            AND ad_zz_m1.do_you_have_height_weight = 1
            AND YEAR(ad_zz_m1.measurement_taken_date)  = %(lyear)s
            AND MONTH(ad_zz_m1.measurement_taken_date) = %(lmonth)s
            AND ad_zz_m1.weight_for_age_zscore IS NOT NULL

        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m2
            ON  ad_zz_m2.childenrollguid        = ad_current.childenrollguid
            AND ad_zz_m2.do_you_have_height_weight = 1
            AND YEAR(ad_zz_m2.measurement_taken_date)  = %(pyear)s
            AND MONTH(ad_zz_m2.measurement_taken_date) = %(plmonth)s
            AND ad_zz_m2.weight_for_age_zscore IS NOT NULL

        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m3
            ON  ad_zz_m3.childenrollguid        = ad_current.childenrollguid
            AND ad_zz_m3.do_you_have_height_weight = 1
            AND YEAR(ad_zz_m3.measurement_taken_date)  = %(l2year)s
            AND MONTH(ad_zz_m3.measurement_taken_date) = %(l2month)s
            AND ad_zz_m3.weight_for_age_zscore IS NOT NULL

        LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m4
            ON  ad_zz_m4.childenrollguid        = ad_current.childenrollguid
            AND ad_zz_m4.do_you_have_height_weight = 1
            AND YEAR(ad_zz_m4.measurement_taken_date)  = %(l3year)s
            AND MONTH(ad_zz_m4.measurement_taken_date) = %(l3month)s
            AND ad_zz_m4.weight_for_age_zscore IS NOT NULL

        WHERE ad_current.do_you_have_height_weight = 1
          AND YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)

          AND (
              -- 1. GF1 Condition
              (
                  (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND (
                      COALESCE(
                          CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                          CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                      ) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                  ) > 0
              )
              
              -- 2. GF1+ Condition
              OR (
                  (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND (
                      CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                      - COALESCE(
                          CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                          CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                      )
                  ) <= -0.5
              )
              
              -- 3. GF2 Condition
              OR (
                  (ad_gf2_priority.weight_for_age_zscore IS NOT NULL OR ad_gf2_fallback.weight_for_age_zscore IS NOT NULL)
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND (
                      CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                      - COALESCE(
                          CAST(ad_gf2_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                          CAST(ad_gf2_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                      )
                  ) <= -0.5
              )
              
              -- 4. Zig-Zag Condition
              OR (
                  ad_zz_m1.weight_for_age_zscore IS NOT NULL
                  AND ad_zz_m2.weight_for_age_zscore IS NOT NULL
                  AND ad_zz_m3.weight_for_age_zscore IS NOT NULL
                  AND ad_zz_m4.weight_for_age_zscore IS NOT NULL
                  AND ad_current.weight_for_age_zscore IS NOT NULL
                  AND cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))
                  AND (
                      CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                      - GREATEST(
                          CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)),
                          CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                          CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)),
                          CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))
                      )
                  ) <= -0.5
                  AND (
                      (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))
                      OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)))
                      OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)))
                      OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                  )
                  AND (
                      (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))
                      OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)))
                      OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)))
                      OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                  )
              )
              
              -- 5. SAM WFA
              OR ad_current.weight_for_age = 1
              
              -- 6. SAM WFH
              OR ad_current.weight_for_height = 1
          )
        GROUP BY cgm.creche_id
    ),

    -- ── Measurement-not-taken reasons ────────────────────────────────────
    mnt AS (
        SELECT
            cgm.creche_id,
            COUNT(CASE WHEN ad.measurement_reason = 1 THEN 1 END) AS child_not_in_creche,
            COUNT(CASE WHEN ad.measurement_reason = 2 THEN 1 END) AS child_not_in_village,
            COUNT(CASE WHEN ad.measurement_reason = 3 THEN 1 END) AS child_is_sick,
            COUNT(CASE WHEN ad.measurement_reason = 4 THEN 1 END) AS other
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        WHERE YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND ad.do_you_have_height_weight = 0
        GROUP BY cgm.creche_id
    ),

    -- ── Health-facility referrals ─────────────────────────────────────────
    h AS (
        SELECT
            cep.creche_id,
            COUNT(DISTINCT cr.name) AS hf
        FROM `tabChild Referral` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND cr.referred_to != 1
          AND YEAR(cr.date_of_referral)  = %(year)s
          AND MONTH(cr.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
    ),

    -- ── NRC referrals ─────────────────────────────────────────────────────
    nr AS (
        SELECT
            cep.creche_id,
            COUNT(DISTINCT cr.name) AS nrc
        FROM `tabChild Referral` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND cr.referred_to = 4
          AND YEAR(cr.date_of_referral)  = %(year)s
          AND MONTH(cr.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
    ),

    -- ── VHND referrals ────────────────────────────────────────────────────
    vhn AS (
        SELECT
            cep.creche_id,
            COUNT(DISTINCT vh.name) AS vhnd
        FROM `tabChild Referral` vh
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = vh.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND vh.referred_to = 1
          AND YEAR(vh.date_of_referral)  = %(year)s
          AND MONTH(vh.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
    ),

    -- ── Follow-up visits ──────────────────────────────────────────────────
    cfu AS (
        SELECT
            cep.creche_id,
            COUNT(DISTINCT cr.name) AS cfu
        FROM `tabChild Follow up` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND YEAR(cr.followup_visit_date)  = %(year)s
          AND MONTH(cr.followup_visit_date) = %(month)s
        GROUP BY cep.creche_id
    ),

    -- ── Growth metrics (WFA / WFH / HFA) ─────────────────────────────────
    gmd AS (
        SELECT
            cgm.creche_id,
            COUNT(CASE WHEN ad.weight_for_age   = 3 THEN 1 END) AS weight_for_age_normal,
            COUNT(CASE WHEN ad.weight_for_age   = 2 THEN 1 END) AS weight_for_age_moderate,
            COUNT(CASE WHEN ad.weight_for_age   = 1 THEN 1 END) AS weight_for_age_severe,
            COUNT(CASE WHEN ad.height_for_age   = 3 THEN 1 END) AS height_for_age_normal,
            COUNT(CASE WHEN ad.height_for_age   = 2 THEN 1 END) AS height_for_age_moderate,
            COUNT(CASE WHEN ad.height_for_age   = 1 THEN 1 END) AS height_for_age_severe,
            COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
            COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
            COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
        WHERE ad.do_you_have_height_weight = 1
          AND YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        GROUP BY cgm.creche_id
    ),

    -- ── GM entered ────────────────────────────────────────────────────────
    gme AS (
        SELECT
            cr.name AS creche_id,
            COUNT(DISTINCT cgm.creche_id) AS gm_entered
        FROM `tabCreche` cr
        LEFT JOIN `tabChild Growth Monitoring` cgm ON cr.name = cgm.creche_id
        WHERE YEAR(cgm.measurement_date)  = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
        GROUP BY cr.name
    )

    SELECT
        {", ".join(selected_fields)},
        COUNT(*) AS op_creches,
        COALESCE(SUM(tf.gm_entered), 0) AS gm_entered,
        COALESCE(SUM(tf.e_children), 0) AS e_children,
        COALESCE(SUM(tf.g_children), 0) AS g_children,
        CASE
            WHEN COALESCE(SUM(tf.e_children), 0) = 0 THEN 0
            ELSE FORMAT(LEAST((SUM(tf.g_children) * 100.0) / SUM(tf.e_children), 100), 2)
        END AS e_children_percentage,

        COALESCE(SUM(tf.child_not_in_creche), 0) AS child_not_in_creche,
        COALESCE(SUM(tf.child_not_in_village), 0) AS child_not_in_village,
        COALESCE(SUM(tf.child_is_sick), 0) AS child_is_sick,
        COALESCE(SUM(tf.other), 0) AS other,

        COALESCE(SUM(tf.hf), 0) AS hf,
        COALESCE(SUM(tf.nrc), 0) AS nrc,
        COALESCE(SUM(tf.vhnd), 0) AS vhnd,
        COALESCE(SUM(tf.gf2), 0) AS gf2,
        COALESCE(SUM(tf.gf1), 0) AS gf1,
        COALESCE(SUM(tf.gf1_plus), 0) AS gf1_plus,
        COALESCE(SUM(tf.zigzag), 0) AS zigzag,
        COALESCE(SUM(tf.snc), 0) AS snc,
        COALESCE(SUM(tf.cfu), 0) AS cfu,
        tf.creche_id AS creche_id,
        tf.cr_open_date AS cr_open_date,

        COALESCE(SUM(tf.weight_for_age_normal), 0) AS weight_for_age_normal,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.weight_for_age_normal) * 100.0) / SUM(tf.g_children), 2)
        END AS per_weight_for_age_normal,

        COALESCE(SUM(tf.weight_for_age_moderate), 0) AS weight_for_age_moderate,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.weight_for_age_moderate) * 100.0) / SUM(tf.g_children), 2)
        END AS per_weight_for_age_moderate,

        COALESCE(SUM(tf.weight_for_age_severe), 0) AS weight_for_age_severe,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.weight_for_age_severe) * 100.0) / SUM(tf.g_children), 2)
        END AS per_weight_for_age_severe,

        COALESCE(SUM(tf.height_for_age_normal), 0) AS height_for_age_normal,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.height_for_age_normal) * 100.0) / SUM(tf.g_children), 2)
        END AS per_height_for_age_normal,

        COALESCE(SUM(tf.height_for_age_moderate), 0) AS height_for_age_moderate,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.height_for_age_moderate) * 100.0) / SUM(tf.g_children), 2)
        END AS per_height_for_age_moderate,

        COALESCE(SUM(tf.height_for_age_severe), 0) AS height_for_age_severe,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.height_for_age_severe) * 100.0) / SUM(tf.g_children), 2)
        END AS per_height_for_age_severe,

        COALESCE(SUM(tf.weight_for_height_normal), 0) AS weight_for_height_normal,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.weight_for_height_normal) * 100.0) / SUM(tf.g_children), 2)
        END AS per_weight_for_height_normal,

        COALESCE(SUM(tf.weight_for_height_moderate), 0) AS weight_for_height_moderate,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.weight_for_height_moderate) * 100.0) / SUM(tf.g_children), 2)
        END AS per_weight_for_height_moderate,

        COALESCE(SUM(tf.weight_for_height_severe), 0) AS weight_for_height_severe,
        CASE
            WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0
            ELSE FORMAT((SUM(tf.weight_for_height_severe) * 100.0) / SUM(tf.g_children), 2)
        END AS per_weight_for_height_severe

    FROM (
        SELECT
            p.partner_name                                  AS partner,
            u.full_name                                     AS supervisor,
            s.state_name                                    AS state,
            d.district_name                                 AS district,
            b.block_name                                    AS block,
            g.gp_name                                       AS gp,
            v.village_name                                  AS village,
            c.creche_name                                   AS creche,
            c.creche_id                                     AS creche_id,
            DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS cr_open_date,
            COALESCE(ec.e_children, 0)                      AS e_children,
            COALESCE(gc.g_children, 0)                      AS g_children,
            COALESCE(h.hf, 0)                               AS hf,
            COALESCE(nr.nrc, 0)                             AS nrc,
            COALESCE(vhn.vhnd, 0)                           AS vhnd,
            COALESCE(gf2c.gf2, 0)                           AS gf2,
            COALESCE(gf1c.gf1, 0)                           AS gf1,
            COALESCE(gf1pc.gf1_plus, 0)                     AS gf1_plus,
            COALESCE(zigzagc.zigzag, 0)                     AS zigzag,
            COALESCE(sncc.snc, 0)                           AS snc,
            COALESCE(mnt.child_not_in_creche, 0)            AS child_not_in_creche,
            COALESCE(mnt.child_not_in_village, 0)           AS child_not_in_village,
            COALESCE(mnt.child_is_sick, 0)                  AS child_is_sick,
            COALESCE(mnt.other, 0)                          AS other,
            COALESCE(cfu.cfu, 0)                            AS cfu,
            COALESCE(gmd.weight_for_age_normal, 0)          AS weight_for_age_normal,
            COALESCE(gmd.weight_for_age_moderate, 0)        AS weight_for_age_moderate,
            COALESCE(gmd.weight_for_age_severe, 0)          AS weight_for_age_severe,
            COALESCE(gmd.height_for_age_normal, 0)          AS height_for_age_normal,
            COALESCE(gmd.height_for_age_moderate, 0)        AS height_for_age_moderate,
            COALESCE(gmd.height_for_age_severe, 0)          AS height_for_age_severe,
            COALESCE(gmd.weight_for_height_normal, 0)       AS weight_for_height_normal,
            COALESCE(gmd.weight_for_height_moderate, 0)     AS weight_for_height_moderate,
            COALESCE(gmd.weight_for_height_severe, 0)       AS weight_for_height_severe,
            COALESCE(gme.gm_entered, 0)                     AS gm_entered

        FROM `tabCreche` c
        LEFT JOIN ec       ON c.name = ec.creche_id
        LEFT JOIN gc       ON c.name = gc.creche_id
        LEFT JOIN gf2c     ON c.name = gf2c.creche_id
        LEFT JOIN gf1c     ON c.name = gf1c.creche_id
        LEFT JOIN gf1pc    ON c.name = gf1pc.creche_id
        LEFT JOIN zigzagc  ON c.name = zigzagc.creche_id
        LEFT JOIN sncc     ON c.name = sncc.creche_id
        LEFT JOIN h        ON c.name = h.creche_id
        LEFT JOIN nr       ON c.name = nr.creche_id
        LEFT JOIN vhn      ON c.name = vhn.creche_id
        LEFT JOIN cfu      ON c.name = cfu.creche_id
        LEFT JOIN gmd      ON c.name = gmd.creche_id
        LEFT JOIN gme      ON c.name = gme.creche_id
        LEFT JOIN mnt      ON c.name = mnt.creche_id

        -- ALL GEOGRAPHY & USER TABLES ARE NOW LEFT JOINs
        LEFT JOIN `tabState`          s ON c.state_id    = s.name
        LEFT JOIN `tabDistrict`       d ON c.district_id = d.name
        LEFT JOIN `tabBlock`          b ON c.block_id    = b.name
        LEFT JOIN `tabGram Panchayat` g ON c.gp_id       = g.name
        LEFT JOIN `tabVillage`        v ON c.village_id  = v.name
        LEFT JOIN `tabPartner`        p ON c.partner_id  = p.name
        LEFT JOIN `tabUser`           u ON u.name        = c.supervisor_id
        WHERE {where_clause}
    ) AS tf

    GROUP BY {group_by_field}
    ORDER BY {group_by_field}
    """

    data = frappe.db.sql(query, params, as_dict=True)

    # ── Totals row ─────────────────────────────────────────────────────────
    total_act_creches = sum(int(row.get('op_creches', 0) or 0) for row in data)
    total_gm_entered  = sum(int(row.get('gm_entered', 0) or 0) for row in data)
    total_e_children  = sum(int(row.get('e_children', 0) or 0) for row in data)
    total_g_children  = sum(int(row.get('g_children', 0) or 0) for row in data)
    total_hf          = sum(int(row.get('hf', 0) or 0) for row in data)
    total_nrc         = sum(int(row.get('nrc', 0) or 0) for row in data)
    total_cfu         = sum(int(row.get('cfu', 0) or 0) for row in data)
    total_vhnd        = sum(int(row.get('vhnd', 0) or 0) for row in data)

    total_gf1      = sum(int(row.get('gf1', 0) or 0) for row in data)
    total_gf1_plus = sum(int(row.get('gf1_plus', 0) or 0) for row in data)
    total_gf2      = sum(int(row.get('gf2', 0) or 0) for row in data)
    total_zigzag   = sum(int(row.get('zigzag', 0) or 0) for row in data)
    total_snc      = sum(int(row.get('snc', 0) or 0) for row in data)

    total_child_not_in_creche  = sum(int(row.get('child_not_in_creche', 0) or 0) for row in data)
    total_child_not_in_village = sum(int(row.get('child_not_in_village', 0) or 0) for row in data)
    total_child_is_sick        = sum(int(row.get('child_is_sick', 0) or 0) for row in data)
    total_other                = sum(int(row.get('other', 0) or 0) for row in data)

    total_weight_for_age_normal    = sum(int(row.get('weight_for_age_normal', 0) or 0) for row in data)
    total_weight_for_age_moderate  = sum(int(row.get('weight_for_age_moderate', 0) or 0) for row in data)
    total_weight_for_age_severe    = sum(int(row.get('weight_for_age_severe', 0) or 0) for row in data)

    total_height_for_age_normal    = sum(int(row.get('height_for_age_normal', 0) or 0) for row in data)
    total_height_for_age_moderate  = sum(int(row.get('height_for_age_moderate', 0) or 0) for row in data)
    total_height_for_age_severe    = sum(int(row.get('height_for_age_severe', 0) or 0) for row in data)

    total_weight_for_height_normal   = sum(int(row.get('weight_for_height_normal', 0) or 0) for row in data)
    total_weight_for_height_moderate = sum(int(row.get('weight_for_height_moderate', 0) or 0) for row in data)
    total_weight_for_height_severe   = sum(int(row.get('weight_for_height_severe', 0) or 0) for row in data)

    total_mea_percentage = round((total_g_children * 100.0 / total_e_children), 2) if total_e_children else 0

    total_wfan_per = round((total_weight_for_age_normal    * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfam_per = round((total_weight_for_age_moderate  * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfas_per = round((total_weight_for_age_severe    * 100.0 / total_g_children), 2) if total_g_children else 0

    total_hfan_per = round((total_height_for_age_normal    * 100.0 / total_g_children), 2) if total_g_children else 0
    total_hfam_per = round((total_height_for_age_moderate  * 100.0 / total_g_children), 2) if total_g_children else 0
    total_hfas_per = round((total_height_for_age_severe    * 100.0 / total_g_children), 2) if total_g_children else 0

    total_wfhn_per = round((total_weight_for_height_normal   * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfhm_per = round((total_weight_for_height_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfhs_per = round((total_weight_for_height_severe   * 100.0 / total_g_children), 2) if total_g_children else 0

    total_row = {
        "partner":  "<b style='color:black;'>Total</b>",
        "state":    "<b style='color:black;'>Total</b>",
        "gm_entered":  f"<b>{total_gm_entered}</b>",
        "op_creches":  f"<b>{total_act_creches}</b>",
        "e_children":  f"<b>{total_e_children}</b>",
        "g_children":  f"<b>{total_g_children}</b>",
        "e_children_percentage": f"<b>{total_mea_percentage}</b>",

        "child_not_in_creche":  f"<b>{total_child_not_in_creche}</b>",
        "child_not_in_village": f"<b>{total_child_not_in_village}</b>",
        "child_is_sick":        f"<b>{total_child_is_sick}</b>",
        "other":                f"<b>{total_other}</b>",

        "hf":   f"<b>{total_hf}</b>",
        "nrc":  f"<b>{total_nrc}</b>",
        "cfu":  f"<b>{total_cfu}</b>",
        "vhnd": f"<b>{total_vhnd}</b>",

        "gf1":      f"<b>{total_gf1}</b>",
        "gf1_plus": f"<b>{total_gf1_plus}</b>",
        "gf2":      f"<b>{total_gf2}</b>",
        "zigzag":   f"<b>{total_zigzag}</b>",
        "snc":      f"<b>{total_snc}</b>",

        "weight_for_age_normal":   f"<b>{total_weight_for_age_normal}</b>",
        "weight_for_age_moderate": f"<b>{total_weight_for_age_moderate}</b>",
        "weight_for_age_severe":   f"<b>{total_weight_for_age_severe}</b>",

        "per_weight_for_age_normal":   f"<b>{total_wfan_per}</b>",
        "per_weight_for_age_moderate": f"<b>{total_wfam_per}</b>",
        "per_weight_for_age_severe":   f"<b>{total_wfas_per}</b>",

        "height_for_age_normal":   f"<b>{total_height_for_age_normal}</b>",
        "height_for_age_moderate": f"<b>{total_height_for_age_moderate}</b>",
        "height_for_age_severe":   f"<b>{total_height_for_age_severe}</b>",

        "per_height_for_age_normal":   f"<b>{total_hfan_per}</b>",
        "per_height_for_age_moderate": f"<b>{total_hfam_per}</b>",
        "per_height_for_age_severe":   f"<b>{total_hfas_per}</b>",

        "weight_for_height_normal":   f"<b>{total_weight_for_height_normal}</b>",
        "weight_for_height_moderate": f"<b>{total_weight_for_height_moderate}</b>",
        "weight_for_height_severe":   f"<b>{total_weight_for_height_severe}</b>",

        "per_weight_for_height_normal":   f"<b>{total_wfhn_per}</b>",
        "per_weight_for_height_moderate": f"<b>{total_wfhm_per}</b>",
        "per_weight_for_height_severe":   f"<b>{total_wfhs_per}</b>",
    }

    data.append(total_row)
    return data








