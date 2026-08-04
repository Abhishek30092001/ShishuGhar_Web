import frappe
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date

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
        {"label": "Weight for Age (Z-score)", "fieldname": "weight_for_age_zscore", "fieldtype": "Data", "width": 200},
        {"label": "Weight for Height (Z-score)", "fieldname": "weight_for_height_zscore", "fieldtype": "Data", "width": 210},
        {"label": "Height for Age (Z-score)", "fieldname": "height_for_age_zscore", "fieldtype": "Data", "width": 200},
        {"label": "GF1", "fieldname": "gf1", "fieldtype": "Data", "width": 160, "align": "center"},
        {"label": "GF1+", "fieldname": "gf1_plus", "fieldtype": "Data", "width": 185, "align": "center"},
        {"label": "GF2", "fieldname": "gf2", "fieldtype": "Data", "width": 175, "align": "center"},
        {"label": "GF ZigZag", "fieldname": "gf_zigzag", "fieldtype": "Data", "width": 185, "align": "center"},
        {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": "Home Visit", "fieldname": "red_flag_HV", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": "Followup", "fieldname": "follow_up", "fieldtype": "Data", "width": 120},
        {"label": "Taken to VHND", "fieldname": "vhsnd", "fieldtype": "Data", "width": 140},
        {"label": "Taken to PHC", "fieldname": "phc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to CHC", "fieldname": "chc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to other Health Facility", "fieldname": "othr", "fieldtype": "Data", "width": 250},
    ]


@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    params = prepare_parameters(filters)
    where_clause = build_where_clause(filters, params)
    data = execute_main_query(params, where_clause)
    data = process_data(data)
    data = add_summary_row(data)
    return data


def prepare_parameters(filters):
    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    if month == 1:
        lmonth, plmonth = 12, 11
        lyear, pyear = year - 1, year - 1
    elif month == 2:
        lmonth, plmonth = 1, 12
        lyear, pyear = year, year - 1
    else:
        lmonth, plmonth = month - 1, month - 2
        lyear, pyear = year, year
    
    l2month = plmonth
    l2year = pyear
    if plmonth == 1:
        l2month = 12
        l2year = pyear - 1
    else:
        l2month = plmonth - 1
        l2year = pyear
    
    l3month = l2month
    l3year = l2year
    if l2month == 1:
        l3month = 12
        l3year = l2year - 1
    else:
        l3month = l2month - 1
        l3year = l2year
    
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "l2month": l2month,
        "l2year": l2year,
        "l3month": l3month,
        "l3year": l3year,
        "cstart_date": None,
        "cend_date": None,
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
        "supervisor_id": None,
        "creche_status_id": None,
        "phases": None,
    }
    
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    params["partner"] = filters.get("partner") or current_user_partner
    
    user_geo = frappe.db.sql("""
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
    """, frappe.session.user, as_dict=True)
    
    for key in ["state", "district", "block", "gp"]:
        if filters.get(key):
            params[key] = filters.get(key)
        else:
            ids = [str(s[f"{key}_id"]) for s in user_geo if s.get(f"{key}_id")]
            if ids:
                params[f"{key}_ids"] = ",".join(ids)
    
    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
        
        if range_type == "between" and filters.get("c_opening_range"):
            params["cstart_date"], params["cend_date"] = filters["c_opening_range"]
        elif range_type == "before" and single_date:
            params["cstart_date"] = date(2017, 1, 1)
            params["cend_date"] = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            params["cstart_date"] = single_date + timedelta(days=1)
            params["cend_date"] = date.today()
        elif range_type == "equal" and single_date:
            params["cstart_date"] = params["cend_date"] = single_date
    
    if filters.get("creche"):
        params["creche"] = filters.get("creche")
    if filters.get("supervisor_id"):
        params["supervisor_id"] = filters.get("supervisor_id")
    if filters.get("creche_status_id"):
        params["creche_status_id"] = filters.get("creche_status_id")
    if filters.get("phases"):
        cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
        if cleaned:
            params["phases"] = cleaned
    
    return params


def build_where_clause(filters, params):
    """Build the WHERE clause for the main query"""
    conditions = ["1=1"]
    
    if params.get("partner"):
        conditions.append("cr.partner_id = %(partner)s")
    if params.get("state"):
        conditions.append("cr.state_id = %(state)s")
    elif params.get("state_ids"):
        conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
    if params.get("district"):
        conditions.append("cr.district_id = %(district)s")
    elif params.get("district_ids"):
        conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
    if params.get("block"):
        conditions.append("cr.block_id = %(block)s")
    elif params.get("block_ids"):
        conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
    if params.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
    elif params.get("gp_ids"):
        conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
    if params.get("creche"):
        conditions.append("cr.name = %(creche)s")
    if params.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
    if params.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
    if params.get("phases"):
        conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"):
        conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")
    
    return " AND ".join(conditions)


def execute_main_query(params, where_clause):
    sql_query = """
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
            THEN TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE())
            ELSE TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s)
        END AS current_age,
        CASE 
            WHEN cee.gender_id = '1' THEN 'M'
            WHEN cee.gender_id = '2' THEN 'F'
            ELSE cee.gender_id
        END AS gender,
        ad.height AS height,
        ad.weight AS weight,
        ad.do_you_have_height_weight AS measurements_taken_raw,
        IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS measurements_taken,
        IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS measurements_taken_date,
        CASE 
            WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
            WHEN ad.measurement_reason = 2 THEN 'Child not in village'
            WHEN ad.measurement_reason = 3 THEN 'Child is sick'
            WHEN ad.measurement_reason = 4 THEN 'Others'
            ELSE ''
        END AS measurement_reason,
        ad.weight_for_age_zscore AS weight_for_age_zscore,
        ad.weight_for_height_zscore AS weight_for_height_zscore,
        ad.height_for_age_zscore AS height_for_age_zscore,
        CASE WHEN ad.weight_for_age = 3 THEN 'Normal'
             WHEN ad.weight_for_age = 2 THEN 'Moderate'
             WHEN ad.weight_for_age = 1 THEN 'Severe'
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
        
        -- GF1: Growth faltering 1 (current > previous, using priority month or fallback)
        CASE 
            WHEN EXISTS (
                SELECT 1
                FROM `tabAnthropromatic Data` ad_prev
                WHERE ad_prev.childenrollguid = ad.childenrollguid
                    AND ad_prev.do_you_have_height_weight = 1
                    AND (
                        (
                            -- Priority: Previous month (lmonth/lyear)
                            YEAR(ad_prev.measurement_taken_date) = %(lyear)s
                            AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
                            AND ad_prev.weight_for_age_zscore IS NOT NULL
                        )
                        OR (
                            -- Fallback: Two months ago (plmonth/pyear) if previous month missing
                            YEAR(ad_prev.measurement_taken_date) = %(pyear)s
                            AND MONTH(ad_prev.measurement_taken_date) = %(plmonth)s
                            AND ad_prev.weight_for_age_zscore IS NOT NULL
                            AND NOT EXISTS (
                                SELECT 1
                                FROM `tabAnthropromatic Data` jan
                                WHERE jan.childenrollguid = ad.childenrollguid
                                    AND jan.do_you_have_height_weight = 1
                                    AND YEAR(jan.measurement_taken_date) = %(lyear)s
                                    AND MONTH(jan.measurement_taken_date) = %(lmonth)s
                                    AND jan.weight_for_age_zscore IS NOT NULL
                            )
                        )
                    )
                    AND ad.weight_for_age_zscore > ad_prev.weight_for_age_zscore
                    AND ad.weight_for_age_zscore IS NOT NULL
                    AND ad_prev.weight_for_age_zscore IS NOT NULL
                    AND YEAR(ad.measurement_taken_date) = %(year)s 
                    AND MONTH(ad.measurement_taken_date) = %(month)s
            ) THEN 'Y'
            ELSE 'N'
        END AS gf1_raw,
        
        -- GF1+: Significant drop (≥0.5) from previous month
        CASE 
            WHEN EXISTS (
                SELECT 1
                FROM `tabAnthropromatic Data` ad_prev
                WHERE ad_prev.childenrollguid = ad.childenrollguid
                    AND ad_prev.do_you_have_height_weight = 1
                    AND (
                        (
                            YEAR(ad_prev.measurement_taken_date) = %(lyear)s
                            AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
                            AND ad_prev.weight_for_age_zscore IS NOT NULL
                        )
                        OR (
                            YEAR(ad_prev.measurement_taken_date) = %(pyear)s
                            AND MONTH(ad_prev.measurement_taken_date) = %(plmonth)s
                            AND ad_prev.weight_for_age_zscore IS NOT NULL
                            AND NOT EXISTS (
                                SELECT 1
                                FROM `tabAnthropromatic Data` jan
                                WHERE jan.childenrollguid = ad.childenrollguid
                                    AND jan.do_you_have_height_weight = 1
                                    AND YEAR(jan.measurement_taken_date) = %(lyear)s
                                    AND MONTH(jan.measurement_taken_date) = %(lmonth)s
                                    AND jan.weight_for_age_zscore IS NOT NULL
                            )
                        )
                    )
                    AND (ad_prev.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
                    AND ad.weight_for_age_zscore IS NOT NULL
                    AND ad_prev.weight_for_age_zscore IS NOT NULL
                    AND YEAR(ad.measurement_taken_date) = %(year)s 
                    AND MONTH(ad.measurement_taken_date) = %(month)s
            ) THEN 'Y'
            ELSE 'N'
        END AS gf1_plus_raw,
        
        -- GF2: Drop ≥0.5 from two months ago (with fallback to three months ago)
        CASE 
            WHEN EXISTS (
                SELECT 1
                FROM `tabAnthropromatic Data` ad_2month
                WHERE ad_2month.childenrollguid = ad.childenrollguid
                    AND ad_2month.do_you_have_height_weight = 1
                    AND (
                        (
                            -- Priority: Two months ago (plmonth/pyear)
                            YEAR(ad_2month.measurement_taken_date) = %(pyear)s
                            AND MONTH(ad_2month.measurement_taken_date) = %(plmonth)s
                            AND ad_2month.weight_for_age_zscore IS NOT NULL
                        )
                        OR (
                            -- Fallback: Three months ago (l2month/l2year) if two months ago missing
                            YEAR(ad_2month.measurement_taken_date) = %(l2year)s
                            AND MONTH(ad_2month.measurement_taken_date) = %(l2month)s
                            AND ad_2month.weight_for_age_zscore IS NOT NULL
                            AND NOT EXISTS (
                                SELECT 1
                                FROM `tabAnthropromatic Data` month_check
                                WHERE month_check.childenrollguid = ad.childenrollguid
                                    AND month_check.do_you_have_height_weight = 1
                                    AND YEAR(month_check.measurement_taken_date) = %(pyear)s
                                    AND MONTH(month_check.measurement_taken_date) = %(plmonth)s
                                    AND month_check.weight_for_age_zscore IS NOT NULL
                            )
                        )
                    )
                    AND (ad_2month.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
                    AND ad.weight_for_age_zscore IS NOT NULL
                    AND ad_2month.weight_for_age_zscore IS NOT NULL
                    
            ) THEN 'Y'
            ELSE 'N'
        END AS gf2_raw,
        
        -- GF ZigZag: Zig‑zag pattern over last 5 months (current + previous 4)
        CASE 
            WHEN EXISTS (
                SELECT 1
                FROM `tabAnthropromatic Data` ad_m1  -- Month -1
                INNER JOIN `tabAnthropromatic Data` ad_m2 ON  -- Month -2
                    ad_m2.childenrollguid = ad_m1.childenrollguid
                    AND ad_m2.do_you_have_height_weight = 1
                    AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s
                    AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
                INNER JOIN `tabAnthropromatic Data` ad_m3 ON  -- Month -3
                    ad_m3.childenrollguid = ad_m1.childenrollguid
                    AND ad_m3.do_you_have_height_weight = 1
                    AND YEAR(ad_m3.measurement_taken_date) = %(l2year)s
                    AND MONTH(ad_m3.measurement_taken_date) = %(l2month)s
                INNER JOIN `tabAnthropromatic Data` ad_m4 ON  -- Month -4
                    ad_m4.childenrollguid = ad_m1.childenrollguid
                    AND ad_m4.do_you_have_height_weight = 1
                    AND YEAR(ad_m4.measurement_taken_date) = %(l3year)s
                    AND MONTH(ad_m4.measurement_taken_date) = %(l3month)s
                WHERE ad_m1.childenrollguid = ad.childenrollguid
                    AND ad_m1.do_you_have_height_weight = 1
                    AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s
                    AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
                    AND ad_m1.weight_for_age_zscore IS NOT NULL
                    AND ad_m2.weight_for_age_zscore IS NOT NULL
                    AND ad_m3.weight_for_age_zscore IS NOT NULL
                    AND ad_m4.weight_for_age_zscore IS NOT NULL
                    AND ad.weight_for_age_zscore IS NOT NULL
                    
                    -- Step 1: At least one gain AND one loss in last 4 transitions
                    AND (
                        (
                            (ad_m1.weight_for_age_zscore > ad_m2.weight_for_age_zscore) OR
                            (ad_m2.weight_for_age_zscore > ad_m3.weight_for_age_zscore) OR
                            (ad_m3.weight_for_age_zscore > ad_m4.weight_for_age_zscore) OR
                            (ad.weight_for_age_zscore > ad_m1.weight_for_age_zscore)
                        )
                        AND
                        (
                            (ad_m1.weight_for_age_zscore < ad_m2.weight_for_age_zscore) OR
                            (ad_m2.weight_for_age_zscore < ad_m3.weight_for_age_zscore) OR
                            (ad_m3.weight_for_age_zscore < ad_m4.weight_for_age_zscore) OR
                            (ad.weight_for_age_zscore < ad_m1.weight_for_age_zscore)
                        )
                    )
                    
                    -- Step 2 & 3: Highest (Month-4 to Month-1) to Current drop ≥ 0.5
                    AND (
                        GREATEST(
                            ad_m4.weight_for_age_zscore,
                            ad_m3.weight_for_age_zscore,
                            ad_m2.weight_for_age_zscore,
                            ad_m1.weight_for_age_zscore
                        ) - ad.weight_for_age_zscore
                    ) >= 0.5
            ) THEN 'Y'
            ELSE 'N'
        END AS gf_zigzag_raw,
        
        -- SNC: Severe Nutritional Concern – any of GF1, GF1+, GF2, ZigZag, SAM, SUW
        CASE 
            WHEN (
                ad.weight_for_height = 1  -- SAM
                OR ad.weight_for_age = 1  -- SUW
                OR EXISTS (  -- GF1 (exact same subquery as above)
                    SELECT 1
                    FROM `tabAnthropromatic Data` ad_prev
                    WHERE ad_prev.childenrollguid = ad.childenrollguid
                        AND ad_prev.do_you_have_height_weight = 1
                        AND (
                            (
                                YEAR(ad_prev.measurement_taken_date) = %(lyear)s
                                AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
                                AND ad_prev.weight_for_age_zscore IS NOT NULL
                            )
                            OR (
                                YEAR(ad_prev.measurement_taken_date) = %(pyear)s
                                AND MONTH(ad_prev.measurement_taken_date) = %(plmonth)s
                                AND ad_prev.weight_for_age_zscore IS NOT NULL
                                AND NOT EXISTS (
                                    SELECT 1
                                    FROM `tabAnthropromatic Data` jan
                                    WHERE jan.childenrollguid = ad.childenrollguid
                                        AND jan.do_you_have_height_weight = 1
                                        AND YEAR(jan.measurement_taken_date) = %(lyear)s
                                        AND MONTH(jan.measurement_taken_date) = %(lmonth)s
                                        AND jan.weight_for_age_zscore IS NOT NULL
                                )
                            )
                        )
                        AND ad.weight_for_age_zscore > ad_prev.weight_for_age_zscore
                        AND ad.weight_for_age_zscore IS NOT NULL
                        AND ad_prev.weight_for_age_zscore IS NOT NULL
                )
                OR EXISTS (  -- GF1+
                    SELECT 1
                    FROM `tabAnthropromatic Data` ad_prev
                    WHERE ad_prev.childenrollguid = ad.childenrollguid
                        AND ad_prev.do_you_have_height_weight = 1
                        AND (
                            (
                                YEAR(ad_prev.measurement_taken_date) = %(lyear)s
                                AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
                                AND ad_prev.weight_for_age_zscore IS NOT NULL
                            )
                            OR (
                                YEAR(ad_prev.measurement_taken_date) = %(pyear)s
                                AND MONTH(ad_prev.measurement_taken_date) = %(plmonth)s
                                AND ad_prev.weight_for_age_zscore IS NOT NULL
                                AND NOT EXISTS (
                                    SELECT 1
                                    FROM `tabAnthropromatic Data` jan
                                    WHERE jan.childenrollguid = ad.childenrollguid
                                        AND jan.do_you_have_height_weight = 1
                                        AND YEAR(jan.measurement_taken_date) = %(lyear)s
                                        AND MONTH(jan.measurement_taken_date) = %(lmonth)s
                                        AND jan.weight_for_age_zscore IS NOT NULL
                                )
                            )
                        )
                        AND (ad_prev.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
                        AND ad.weight_for_age_zscore IS NOT NULL
                        AND ad_prev.weight_for_age_zscore IS NOT NULL
                )
                OR EXISTS (  -- GF2
                    SELECT 1
                    FROM `tabAnthropromatic Data` ad_2month
                    WHERE ad_2month.childenrollguid = ad.childenrollguid
                        AND ad_2month.do_you_have_height_weight = 1
                        AND (
                            (
                                YEAR(ad_2month.measurement_taken_date) = %(pyear)s
                                AND MONTH(ad_2month.measurement_taken_date) = %(plmonth)s
                                AND ad_2month.weight_for_age_zscore IS NOT NULL
                            )
                            OR (
                                YEAR(ad_2month.measurement_taken_date) = %(l2year)s
                                AND MONTH(ad_2month.measurement_taken_date) = %(l2month)s
                                AND ad_2month.weight_for_age_zscore IS NOT NULL
                                AND NOT EXISTS (
                                    SELECT 1
                                    FROM `tabAnthropromatic Data` month_check
                                    WHERE month_check.childenrollguid = ad.childenrollguid
                                        AND month_check.do_you_have_height_weight = 1
                                        AND YEAR(month_check.measurement_taken_date) = %(pyear)s
                                        AND MONTH(month_check.measurement_taken_date) = %(plmonth)s
                                        AND month_check.weight_for_age_zscore IS NOT NULL
                                )
                            )
                        )
                        AND (ad_2month.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
                        AND ad.weight_for_age_zscore IS NOT NULL
                        AND ad_2month.weight_for_age_zscore IS NOT NULL
                )
                OR EXISTS (  -- ZigZag (exact same subquery as above)
                    SELECT 1
                    FROM `tabAnthropromatic Data` ad_m1
                    INNER JOIN `tabAnthropromatic Data` ad_m2 
                        ON ad_m2.childenrollguid = ad_m1.childenrollguid
                        AND ad_m2.do_you_have_height_weight = 1
                        AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s
                        AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
                    INNER JOIN `tabAnthropromatic Data` ad_m3 
                        ON ad_m3.childenrollguid = ad_m1.childenrollguid
                        AND ad_m3.do_you_have_height_weight = 1
                        AND YEAR(ad_m3.measurement_taken_date) = %(l2year)s
                        AND MONTH(ad_m3.measurement_taken_date) = %(l2month)s
                    INNER JOIN `tabAnthropromatic Data` ad_m4 
                        ON ad_m4.childenrollguid = ad_m1.childenrollguid
                        AND ad_m4.do_you_have_height_weight = 1
                        AND YEAR(ad_m4.measurement_taken_date) = %(l3year)s
                        AND MONTH(ad_m4.measurement_taken_date) = %(l3month)s
                    WHERE ad_m1.childenrollguid = ad.childenrollguid
                        AND ad_m1.do_you_have_height_weight = 1
                        AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s
                        AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
                        AND ad_m1.weight_for_age_zscore IS NOT NULL
                        AND ad_m2.weight_for_age_zscore IS NOT NULL
                        AND ad_m3.weight_for_age_zscore IS NOT NULL
                        AND ad_m4.weight_for_age_zscore IS NOT NULL
                        AND ad.weight_for_age_zscore IS NOT NULL
                        AND (
                            (ad.weight_for_age_zscore > ad_m1.weight_for_age_zscore) OR
                            (ad_m1.weight_for_age_zscore > ad_m2.weight_for_age_zscore) OR
                            (ad_m2.weight_for_age_zscore > ad_m3.weight_for_age_zscore) OR
                            (ad_m3.weight_for_age_zscore > ad_m4.weight_for_age_zscore)
                        )
                        AND (
                            (ad.weight_for_age_zscore < ad_m1.weight_for_age_zscore) OR
                            (ad_m1.weight_for_age_zscore < ad_m2.weight_for_age_zscore) OR
                            (ad_m2.weight_for_age_zscore < ad_m3.weight_for_age_zscore) OR
                            (ad_m3.weight_for_age_zscore < ad_m4.weight_for_age_zscore)
                        )
                        AND (
                            GREATEST(
                                ad_m4.weight_for_age_zscore,
                                ad_m3.weight_for_age_zscore,
                                ad_m2.weight_for_age_zscore,
                                ad_m1.weight_for_age_zscore
                            ) - ad.weight_for_age_zscore
                        ) >= 0.5
                )
            ) THEN 'Y'
            ELSE 'N'
        END AS snc_raw,
        
        ad.any_medical_major_illness AS any_medical_major_illness,
        CASE 
            WHEN (ad.weight_for_age = 1 OR ad.weight_for_height = 1 
                  OR ad.any_medical_major_illness = 1
                  OR EXISTS (
                      SELECT 1
                      FROM `tabAnthropromatic Data` ad_2month
                      WHERE ad_2month.childenrollguid = ad.childenrollguid
                          AND ad_2month.do_you_have_height_weight = 1
                          AND (
                              (
                                  YEAR(ad_2month.measurement_taken_date) = %(pyear)s
                                  AND MONTH(ad_2month.measurement_taken_date) = %(plmonth)s
                                  AND ad_2month.weight_for_age_zscore IS NOT NULL
                              )
                              OR (
                                  YEAR(ad_2month.measurement_taken_date) = %(l2year)s
                                  AND MONTH(ad_2month.measurement_taken_date) = %(l2month)s
                                  AND ad_2month.weight_for_age_zscore IS NOT NULL
                                  AND NOT EXISTS (
                                      SELECT 1
                                      FROM `tabAnthropromatic Data` month_check
                                      WHERE month_check.childenrollguid = ad.childenrollguid
                                          AND month_check.do_you_have_height_weight = 1
                                          AND YEAR(month_check.measurement_taken_date) = %(pyear)s
                                          AND MONTH(month_check.measurement_taken_date) = %(plmonth)s
                                          AND month_check.weight_for_age_zscore IS NOT NULL
                                  )
                              )
                          )
                          AND (ad_2month.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
                  ))
            THEN 'Y'
            ELSE 'N'
        END AS red_flag_raw,
        '-' AS red_flag_HV_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 5 THEN 'Y' END), '-') AS othr_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 4 THEN 'Y' END), '-') AS nrc_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 3 THEN 'Y' END), '-') AS chc_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 2 THEN 'Y' END), '-') AS phc_raw,
        COALESCE(MAX(CASE WHEN crf.referred_to = 1 THEN 'Y' END), '-') AS vhsnd_raw,
        COALESCE(MAX(CASE WHEN cfu.name IS NOT NULL THEN 'Y' END), '-') AS follow_up_raw,
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block,
        g.gp_name AS gp
    FROM `tabAnthropromatic Data` AS ad
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
    INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cgm.creche_id = cr.name
    INNER JOIN `tabUser` AS usr ON cr.supervisor_id = usr.name
    INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
    INNER JOIN `tabState` AS s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
    INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` AS g ON g.name = cr.gp_id
    LEFT JOIN `tabChild Referral` AS crf ON crf.childenrolledguid = ad.childenrollguid
        AND YEAR(crf.date_of_referral) = %(year)s 
        AND MONTH(crf.date_of_referral) = %(month)s
    LEFT JOIN `tabChild Follow up` AS cfu ON cfu.childenrolledguid = ad.childenrollguid
        AND YEAR(cfu.followup_visit_date) = %(year)s 
        AND MONTH(cfu.followup_visit_date) = %(month)s
    WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND {where_clause}
    GROUP BY ad.name, cgm.name, cee.name, cr.name, usr.name, p.name, s.name, d.name, b.name, g.name
    ORDER BY cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id, cr.supervisor_id, cr.name, cee.child_name
    """.format(where_clause=where_clause)
    
    return frappe.db.sql(sql_query, params, as_dict=True)


def process_data(data):
    for row in data:
        for field in ["weight_for_age_zscore", "weight_for_height_zscore", "height_for_age_zscore"]:
            status_field = field.replace("zscore", "status")
            val = row.get(field)
            status = row.get(status_field, "").lower()
            if val is not None and val != '':
                row[field] = format_zscore_cell(val, status)
        
        flag_fields = [("gf1_raw", "gf1"), ("gf1_plus_raw", "gf1_plus"), ("gf2_raw", "gf2"),
            ("gf_zigzag_raw", "gf_zigzag"), ("snc_raw", "snc"), ("red_flag_raw", "red_flag")
        ]
        
        for raw_field, display_field in flag_fields:
            raw_val = row.get(raw_field, "N")
            bg = "#FFE0E0" if raw_val == "Y" else "#E8F5E9"
            fg = "#CC0000" if raw_val == "Y" else "#2E7D32"
            row[display_field] = format_flag_cell(raw_val, bg, fg)
        
        row["red_flag_HV"] = format_flag_cell(row.get("red_flag_HV_raw", "-"), "#E8F5E9", "#2E7D32")
        
        for field in ["othr", "nrc", "chc", "phc", "vhsnd", "follow_up"]:
            raw_val = row.get(f"{field}_raw", "-")
            if raw_val == "Y":
                row[field] = format_flag_cell("Y", "#E8F5E9", "#2E7D32")
            else:
                row[field] = format_flag_cell("-", "#F5F5F5", "#999999")
    
    return data


def add_summary_row(data):
    """Add summary totals row at the end"""
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
        
        for field in ["gf1", "gf1_plus", "gf2", "gf_zigzag", "snc", 
                      "nrc", "phc", "chc", "vhsnd", "follow_up", "red_flag", "othr"]:
            if row.get(f"{field}_raw") == "Y":
                counts[field] += 1
        
        if row.get("red_flag_HV_raw") == "Y":
            counts["red_flag_HV"] += 1
        if row.get("any_medical_major_illness") == 1:
            counts["any_medical_major_illness"] += 1
    
    summary_row = {
        "partner": "<b style='color:black;'>Total</b>",
        "child_name": f"<b>{counts['child_name']}</b>",
        "measurements_taken": f"<b>{counts['measurements_taken']}</b>",
        "gf1": f"<b>{counts['gf1']}</b>",
        "gf1_plus": f"<b>{counts['gf1_plus']}</b>",
        "gf2": f"<b>{counts['gf2']}</b>",
        "gf_zigzag": f"<b>{counts['gf_zigzag']}</b>",
        "snc": f"<b>{counts['snc']}</b>",
        "any_medical_major_illness": f"<b>{counts['any_medical_major_illness']}</b>",
        "red_flag": f"<b>{counts['red_flag']}</b>",
        "red_flag_HV": f"<b>{counts['red_flag_HV']}</b>",
        "follow_up": f"<b>{counts['follow_up']}</b>",
        "vhsnd": f"<b>{counts['vhsnd']}</b>",
        "phc": f"<b>{counts['phc']}</b>",
        "chc": f"<b>{counts['chc']}</b>",
        "nrc": f"<b>{counts['nrc']}</b>",
        "othr": f"<b>{counts['othr']}</b>",
    }
    
    data.append(summary_row)
    return data

def format_zscore_cell(value, status):
    if value is None or value == '':
        return value
    
    color_map = {
        "severe": ("#FFCCCC", "#CC0000"),
        "moderate": ("#FFFFCC", "#999900"),
        "normal": ("#CCFFCC", "#006600"),
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











# import frappe
# from frappe.utils import nowdate
# import calendar
# from datetime import datetime, timedelta, date

# def execute(filters=None):
#     columns = get_columns()
#     data    = get_summary_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         # ── Identity ──────────────────────────────────────────────────────────
#         {"label": "Partner",                        "fieldname": "partner",                   "fieldtype": "Data", "width": 120},
#         {"label": "State",                          "fieldname": "state",                     "fieldtype": "Data", "width": 120},
#         {"label": "District",                       "fieldname": "district",                  "fieldtype": "Data", "width": 120},
#         {"label": "Block",                          "fieldname": "block",                     "fieldtype": "Data", "width": 120},
#         {"label": "GP",                             "fieldname": "gp",                        "fieldtype": "Data", "width": 120},
#         {"label": "Creche",                         "fieldname": "creche_name",               "fieldtype": "Data", "width": 200},
#         {"label": "Creche ID",                      "fieldname": "creche_id",                 "fieldtype": "Data", "width": 150},
#         {"label": "Supervisor",                     "fieldname": "supervisor",                "fieldtype": "Data", "width": 200},
#         {"label": "Child Name",                     "fieldname": "child_name",                "fieldtype": "Data", "width": 200},
#         {"label": "Child ID",                       "fieldname": "child_id",                  "fieldtype": "Data", "width": 150},
#         {"label": "Date of Birth",                  "fieldname": "child_dob",                 "fieldtype": "Data", "width": 150},
#         {"label": "Age (At Enrollment)",            "fieldname": "age",                       "fieldtype": "Data", "width": 180},
#         {"label": "Current Age",                    "fieldname": "current_age",               "fieldtype": "Data", "width": 150},
#         {"label": "Gender",                         "fieldname": "gender",                    "fieldtype": "Data", "width": 100},

#         # ── Measurements ──────────────────────────────────────────────────────
#         {"label": "Height (cm)",                    "fieldname": "height",                    "fieldtype": "Data", "width": 130},
#         {"label": "Weight (kg)",                    "fieldname": "weight",                    "fieldtype": "Data", "width": 130},
#         {"label": "Measurement Date",               "fieldname": "measurements_taken_date",   "fieldtype": "Data", "width": 200},
#         {"label": "Measurement Taken",              "fieldname": "measurements_taken",        "fieldtype": "Data", "width": 180},
#         {"label": "Measurement Not Taken",          "fieldname": "measurement_reason",        "fieldtype": "Data", "width": 200},

#         # ── Z-scores (colour-coded) ───────────────────────────────────────────
#         {"label": "Weight for Age (Z-score)",       "fieldname": "weight_for_age_zscore",     "fieldtype": "Data", "width": 200},
#         {"label": "Weight for Height (Z-score)",    "fieldname": "weight_for_height_zscore",  "fieldtype": "Data", "width": 210},
#         {"label": "Height for Age (Z-score)",       "fieldname": "height_for_age_zscore",     "fieldtype": "Data", "width": 200},

#         # ── Growth Faltering (WHO WAZ-based) ─────────────────────────────────
#         {"label": "GF1 ",                           "fieldname": "gf1",                       "fieldtype": "Data", "width": 160, "align": "center"},
#         {"label": "GF1+",                           "fieldname": "gf1_plus",                  "fieldtype": "Data", "width": 185, "align": "center"},
#         {"label": "GF2",                            "fieldname": "gf2",                       "fieldtype": "Data", "width": 175, "align": "center"},
#         {"label": "GF ZigZag ",                     "fieldname": "gf_zigzag",                 "fieldtype": "Data", "width": 185, "align": "center"},
#         {"label": "SNC",                            "fieldname": "snc",                       "fieldtype": "Data", "width": 100, "align": "center"},

#         # ── Other flags ───────────────────────────────────────────────────────
#         {"label": "Home Visit",                     "fieldname": "red_flag_HV",               "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": "Followup",                       "fieldname": "follow_up",                 "fieldtype": "Data", "width": 120},
#         {"label": "Taken to VHND",                  "fieldname": "vhsnd",                     "fieldtype": "Data", "width": 140},
#         {"label": "Taken to PHC",                   "fieldname": "phc",                       "fieldtype": "Data", "width": 120},
#         {"label": "Taken to CHC",                    "fieldname": "chc",                       "fieldtype": "Data", "width": 120},
#         {"label": "Taken to NRC",                    "fieldname": "nrc",                       "fieldtype": "Data", "width": 120},
#         {"label": "Taken to other Health Facility", "fieldname": "othr",                      "fieldtype": "Data", "width": 250},
#     ]


# # ─────────────────────────────────────────────────────────────────────────────
# # Main data function
# # ─────────────────────────────────────────────────────────────────────────────

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}

#     # ── Date setup ────────────────────────────────────────────────────────────
#     current_date = date.today()
#     month  = int(filters.get("month",  current_date.month))
#     year   = int(filters.get("year",   current_date.year))

#     start_date = date(year, month, 1)
#     last_day   = calendar.monthrange(year, month)[1]
#     end_date   = date(year, month, last_day)

#     # Previous months (for GF calculations)
#     # m-1
#     if month == 1:
#         lmonth, lyear   = 12, year - 1
#     else:
#         lmonth, lyear   = month - 1, year

#     # m-2
#     if lmonth == 1:
#         plmonth, pyear  = 12, lyear - 1
#     else:
#         plmonth, pyear  = lmonth - 1, lyear

#     # m-3  (for GF ZigZag)
#     if plmonth == 1:
#         l3month, l3year = 12, pyear - 1
#     else:
#         l3month, l3year = plmonth - 1, pyear

#     # m-4  (for GF ZigZag)
#     if l3month == 1:
#         l4month, l4year = 12, l3year - 1
#     else:
#         l4month, l4year = l3month - 1, l3year

#     # ── Params ────────────────────────────────────────────────────────────────
#     params = {
#         "start_date":  start_date,
#         "end_date":    end_date,
#         "year":        year,
#         "month":       month,
#         "lyear":       lyear,
#         "lmonth":      lmonth,
#         "plmonth":     plmonth,
#         "pyear":       pyear,
#         "l3month":     l3month,
#         "l3year":      l3year,
#         "l4month":     l4month,
#         "l4year":      l4year,
#         "cstart_date": None,
#         "cend_date":   None,
#         "partner":     None,
#         "state":       None,
#         "district":    None,
#         "block":       None,
#         "gp":          None,
#         "creche":      None,
#         "supervisor_id":    None,
#         "creche_status_id": None,
#         "phases":      None,
#     }

#     # ── User partner + geography ──────────────────────────────────────────────
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     state_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)

#     # ── Creche opening date range ─────────────────────────────────────────────
#     range_type = filters.get("cr_opening_range_type")
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range  = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()

#         if range_type == "between" and date_range and len(date_range) == 2:
#             params["cstart_date"], params["cend_date"] = date_range
#         elif range_type == "before" and single_date:
#             params["cstart_date"] = date(2017, 1, 1)
#             params["cend_date"]   = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             params["cstart_date"] = single_date + timedelta(days=1)
#             params["cend_date"]   = date.today()
#         elif range_type == "equal" and single_date:
#             params["cstart_date"] = single_date
#             params["cend_date"]   = single_date

#     # ── Build geography params ────────────────────────────────────────────────
#     if partner_id:
#         params["partner"] = partner_id

#     if filters.get("state"):
#         params["state"] = filters.get("state")
#     else:
#         ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#         if ids:
#             params["state_ids"] = ",".join(ids)

#     if filters.get("district"):
#         params["district"] = filters.get("district")
#     else:
#         ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#         if ids:
#             params["district_ids"] = ",".join(ids)

#     if filters.get("block"):
#         params["block"] = filters.get("block")
#     else:
#         ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#         if ids:
#             params["block_ids"] = ",".join(ids)

#     if filters.get("gp"):
#         params["gp"] = filters.get("gp")
#     else:
#         ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
#         if ids:
#             params["gp_ids"] = ",".join(ids)

#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if cleaned:
#             params["phases"] = cleaned

#     # ── WHERE conditions ─────────────────────────────────────────────────────
#     conditions = ["1=1"]

#     if params.get("partner"):
#         conditions.append("cr.partner_id = %(partner)s")
#     if params.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#     if params.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#     if params.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#     if params.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#     if params.get("creche"):
#         conditions.append("cr.name = %(creche)s")
#     if params.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#     if params.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):
#         conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

#     where_clause = " AND ".join(conditions)

#     # ── SQL query using CTEs for GF calculations (same logic as first code) ──
#     sql_query = f"""
#     WITH 
#     -- Get all measurements for current month
#     current_measurements AS (
#         SELECT 
#             ad.name AS ad_name,
#             ad.parent AS cgm_name,
#             ad.childenrollguid,
#             ad.weight,
#             ad.height,
#             ad.do_you_have_height_weight,
#             ad.measurement_taken_date,
#             ad.measurement_reason,
#             ad.weight_for_age_zscore,
#             ad.weight_for_height_zscore,
#             ad.height_for_age_zscore,
#             ad.weight_for_age,
#             ad.weight_for_height,
#             ad.height_for_age,
#             ad.any_medical_major_illness,
#             cgm.creche_id,
#             cgm.measurement_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         WHERE YEAR(cgm.measurement_date) = %(year)s
#           AND MONTH(cgm.measurement_date) = %(month)s
#     ),
    
#     -- Previous month measurements (m-1)
#     prev_month_measurements AS (
#         SELECT 
#             ad.childenrollguid,
#             ad.weight_for_age_zscore,
#             ad.measurement_taken_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         WHERE YEAR(cgm.measurement_date) = %(lyear)s
#           AND MONTH(cgm.measurement_date) = %(lmonth)s
#           AND ad.do_you_have_height_weight = 1
#           AND ad.weight_for_age_zscore IS NOT NULL
#     ),
    
#     -- Two months ago measurements (m-2)
#     two_month_ago_measurements AS (
#         SELECT 
#             ad.childenrollguid,
#             ad.weight_for_age_zscore,
#             ad.measurement_taken_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         WHERE YEAR(cgm.measurement_date) = %(pyear)s
#           AND MONTH(cgm.measurement_date) = %(plmonth)s
#           AND ad.do_you_have_height_weight = 1
#           AND ad.weight_for_age_zscore IS NOT NULL
#     ),
    
#     -- Three months ago measurements (m-3)
#     three_month_ago_measurements AS (
#         SELECT 
#             ad.childenrollguid,
#             ad.weight_for_age_zscore,
#             ad.measurement_taken_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         WHERE YEAR(cgm.measurement_date) = %(l3year)s
#           AND MONTH(cgm.measurement_date) = %(l3month)s
#           AND ad.do_you_have_height_weight = 1
#           AND ad.weight_for_age_zscore IS NOT NULL
#     ),
    
#     -- Four months ago measurements (m-4)
#     four_month_ago_measurements AS (
#         SELECT 
#             ad.childenrollguid,
#             ad.weight_for_age_zscore,
#             ad.measurement_taken_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         WHERE YEAR(cgm.measurement_date) = %(l4year)s
#           AND MONTH(cgm.measurement_date) = %(l4month)s
#           AND ad.do_you_have_height_weight = 1
#           AND ad.weight_for_age_zscore IS NOT NULL
#     ),
    
#     -- GF1: Current WAZ > Previous month WAZ (improvement)
#     gf1_calc AS (
#         SELECT 
#             cm.childenrollguid,
#             'Y' AS gf1
#         FROM current_measurements cm
#         INNER JOIN prev_month_measurements pm ON cm.childenrollguid = pm.childenrollguid
#         WHERE cm.do_you_have_height_weight = 1
#           AND cm.weight_for_age_zscore IS NOT NULL
#           AND pm.weight_for_age_zscore IS NOT NULL
#           AND cm.weight_for_age_zscore > pm.weight_for_age_zscore
#     ),
    
#     -- GF1+: Drop >= 0.5 from best of last 2 months
#     gf1_plus_calc AS (
#         SELECT DISTINCT
#             cm.childenrollguid,
#             'Y' AS gf1_plus
#         FROM current_measurements cm
#         LEFT JOIN prev_month_measurements pm ON cm.childenrollguid = pm.childenrollguid
#         LEFT JOIN two_month_ago_measurements tm ON cm.childenrollguid = tm.childenrollguid
#         WHERE cm.do_you_have_height_weight = 1
#           AND cm.weight_for_age_zscore IS NOT NULL
#           AND (
#               (pm.weight_for_age_zscore IS NOT NULL AND 
#                CAST(pm.weight_for_age_zscore AS DECIMAL(10,4)) - CAST(cm.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5)
#               OR
#               (tm.weight_for_age_zscore IS NOT NULL AND 
#                CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)) - CAST(cm.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5)
#           )
#     ),
    
#     -- GF2: Drop >= 0.5 from two months ago
#     gf2_calc AS (
#         SELECT 
#             cm.childenrollguid,
#             'Y' AS gf2
#         FROM current_measurements cm
#         INNER JOIN two_month_ago_measurements tm ON cm.childenrollguid = tm.childenrollguid
#         WHERE cm.do_you_have_height_weight = 1
#           AND cm.weight_for_age_zscore IS NOT NULL
#           AND tm.weight_for_age_zscore IS NOT NULL
#           AND CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)) - CAST(cm.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5
#     ),
    
#     -- ZigZag: At least one gain AND one loss in last 4 transitions, AND drop >= 0.5 from highest
#     zigzag_calc AS (
#         SELECT 
#             cm.childenrollguid,
#             'Y' AS gf_zigzag
#         FROM current_measurements cm
#         INNER JOIN prev_month_measurements pm ON cm.childenrollguid = pm.childenrollguid
#         INNER JOIN two_month_ago_measurements tm ON cm.childenrollguid = tm.childenrollguid
#         INNER JOIN three_month_ago_measurements thm ON cm.childenrollguid = thm.childenrollguid
#         INNER JOIN four_month_ago_measurements fm ON cm.childenrollguid = fm.childenrollguid
#         WHERE cm.do_you_have_height_weight = 1
#           AND cm.weight_for_age_zscore IS NOT NULL
#           AND pm.weight_for_age_zscore IS NOT NULL
#           AND tm.weight_for_age_zscore IS NOT NULL
#           AND thm.weight_for_age_zscore IS NOT NULL
#           AND fm.weight_for_age_zscore IS NOT NULL
#           -- At least one gain (current vs previous OR previous vs older)
#           AND (
#               (CAST(pm.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)))
#               OR (CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(thm.weight_for_age_zscore AS DECIMAL(10,4)))
#               OR (CAST(thm.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(fm.weight_for_age_zscore AS DECIMAL(10,4)))
#               OR (CAST(cm.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(pm.weight_for_age_zscore AS DECIMAL(10,4)))
#           )
#           -- At least one loss
#           AND (
#               (CAST(pm.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)))
#               OR (CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(thm.weight_for_age_zscore AS DECIMAL(10,4)))
#               OR (CAST(thm.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(fm.weight_for_age_zscore AS DECIMAL(10,4)))
#               OR (CAST(cm.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(pm.weight_for_age_zscore AS DECIMAL(10,4)))
#           )
#           -- Drop >= 0.5 from highest of last 4 months
#           AND (
#               GREATEST(
#                   CAST(fm.weight_for_age_zscore AS DECIMAL(10,4)),
#                   CAST(thm.weight_for_age_zscore AS DECIMAL(10,4)),
#                   CAST(tm.weight_for_age_zscore AS DECIMAL(10,4)),
#                   CAST(pm.weight_for_age_zscore AS DECIMAL(10,4))
#               ) - CAST(cm.weight_for_age_zscore AS DECIMAL(10,4))
#           ) >= 0.5
#     ),
    
#     -- SAM (Severe Acute Malnutrition)
#     sam_calc AS (
#         SELECT 
#             cm.childenrollguid,
#             'Y' AS sam
#         FROM current_measurements cm
#         WHERE cm.do_you_have_height_weight = 1
#           AND cm.weight_for_height = 1
#     ),
    
#     -- SUW (Severely Underweight)
#     suw_calc AS (
#         SELECT 
#             cm.childenrollguid,
#             'Y' AS suw
#         FROM current_measurements cm
#         WHERE cm.do_you_have_height_weight = 1
#           AND cm.weight_for_age_zscore IS NOT NULL
#           AND CAST(cm.weight_for_age_zscore AS DECIMAL(10,4)) <= -3
#     ),
    
#     -- SNC: GF1+ OR GF2 OR ZigZag OR SAM OR SUW
#     snc_calc AS (
#         SELECT DISTINCT childenrollguid, 'Y' AS snc
#         FROM (
#             SELECT childenrollguid FROM gf1_plus_calc
#             UNION
#             SELECT childenrollguid FROM gf2_calc
#             UNION
#             SELECT childenrollguid FROM zigzag_calc
#             UNION
#             SELECT childenrollguid FROM sam_calc
#             UNION
#             SELECT childenrollguid FROM suw_calc
#         ) snc_union
#     ),
    
#     -- Referrals for current month
#     referrals AS (
#         SELECT 
#             crf.childenrolledguid,
#             MAX(CASE WHEN crf.referred_to = 1 THEN 'Y' ELSE '-' END) AS vhsnd,
#             MAX(CASE WHEN crf.referred_to = 2 THEN 'Y' ELSE '-' END) AS phc,
#             MAX(CASE WHEN crf.referred_to = 3 THEN 'Y' ELSE '-' END) AS chc,
#             MAX(CASE WHEN crf.referred_to = 4 THEN 'Y' ELSE '-' END) AS nrc,
#             MAX(CASE WHEN crf.referred_to = 5 THEN 'Y' ELSE '-' END) AS othr
#         FROM `tabChild Referral` crf
#         WHERE YEAR(crf.date_of_referral) = %(year)s
#           AND MONTH(crf.date_of_referral) = %(month)s
#         GROUP BY crf.childenrolledguid
#     ),
    
#     -- Follow-ups for current month
#     followups AS (
#         SELECT 
#             cfu.childenrolledguid,
#             'Y' AS follow_up
#         FROM `tabChild Follow up` cfu
#         WHERE YEAR(cfu.followup_visit_date) = %(year)s
#           AND MONTH(cfu.followup_visit_date) = %(month)s
#         GROUP BY cfu.childenrolledguid
#     )
    
#     SELECT 
#         cr.creche_name                                          AS creche_name,
#         usr.full_name                                           AS supervisor,
#         cee.child_id                                            AS child_id,
#         cr.creche_id                                            AS creche_id,
#         cee.child_name                                          AS child_name,
#         cee.age_at_enrollment_in_months                         AS age,
#         DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y')              AS child_dob,
#         CASE 
#             WHEN DATE_FORMAT(%(end_date)s,'%%Y-%%m') = DATE_FORMAT(CURDATE(),'%%Y-%%m')
#             THEN TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE())
#             ELSE TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s)
#         END                                                     AS current_age,
#         CASE 
#             WHEN cee.gender_id = '1' THEN 'M'
#             WHEN cee.gender_id = '2' THEN 'F'
#             ELSE cee.gender_id
#         END                                                     AS gender,
#         ad.height                                               AS height,
#         ad.weight                                               AS weight,
#         ad.do_you_have_height_weight                            AS measurements_taken_raw,
#         IF(ad.do_you_have_height_weight = 1,'Y','N')            AS measurements_taken,
#         IFNULL(DATE_FORMAT(ad.measurement_taken_date,'%%d-%%m-%%Y'),'-')
#                                                                 AS measurements_taken_date,
#         CASE 
#             WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
#             WHEN ad.measurement_reason = 2 THEN 'Child not in village'
#             WHEN ad.measurement_reason = 3 THEN 'Child is sick'
#             WHEN ad.measurement_reason = 4 THEN 'Others'
#             ELSE ''
#         END                                                     AS measurement_reason,

#         -- Z-scores
#         ad.weight_for_age_zscore                                AS weight_for_age_zscore,
#         ad.weight_for_height_zscore                             AS weight_for_height_zscore,
#         ad.height_for_age_zscore                                AS height_for_age_zscore,

#         -- Status labels
#         CASE WHEN ad.weight_for_age   = 3 THEN 'Normal'
#              WHEN ad.weight_for_age   = 2 THEN 'Moderate'
#              WHEN ad.weight_for_age   = 1 THEN 'Severe'
#              ELSE '' END                                        AS weight_for_age_status,
#         CASE WHEN ad.height = 0 THEN '-'
#              WHEN ad.height_for_age   = 3 THEN 'Normal'
#              WHEN ad.height_for_age   = 2 THEN 'Moderate'
#              WHEN ad.height_for_age   = 1 THEN 'Severe'
#              ELSE '' END                                        AS height_for_age_status,
#         CASE WHEN ad.height = 0 THEN '-'
#              WHEN ad.weight_for_height = 3 THEN 'Normal'
#              WHEN ad.weight_for_height = 2 THEN 'Moderate'
#              WHEN ad.weight_for_height = 1 THEN 'Severe'
#              ELSE '' END                                        AS weight_for_height_status,

#         -- GF flags from CTEs (raw Y/N values)
#         COALESCE(gf1.gf1, 'N')                                 AS gf1_raw,
#         COALESCE(gf1p.gf1_plus, 'N')                           AS gf1_plus_raw,
#         COALESCE(gf2.gf2, 'N')                                 AS gf2_raw,
#         COALESCE(zz.gf_zigzag, 'N')                            AS gf_zigzag_raw,
#         COALESCE(snc.snc, 'N')                                 AS snc_raw,

#         -- Medical & Red-flag fields
#         ad.any_medical_major_illness                            AS any_medical_major_illness,
#         CASE 
#             WHEN (ad.weight_for_age = 1 OR ad.weight_for_height = 1 
#                   OR ad.any_medical_major_illness = 1
#                   OR COALESCE(gf2.gf2, 'N') = 'Y') THEN 'Y'
#             ELSE 'N'
#         END AS red_flag_raw,
        
#         '-' AS red_flag_HV_raw,  -- Default value
#         COALESCE(r.othr, '-') AS othr_raw,
#         COALESCE(r.nrc, '-') AS nrc_raw,
#         COALESCE(r.chc, '-') AS chc_raw,
#         COALESCE(r.phc, '-') AS phc_raw,
#         COALESCE(r.vhsnd, '-') AS vhsnd_raw,
#         COALESCE(fu.follow_up, '-') AS follow_up_raw,
        
#         p.partner_name  AS partner,
#         s.state_name    AS state,
#         d.district_name AS district,
#         b.block_name    AS block,
#         g.gp_name       AS gp

#     FROM `tabAnthropromatic Data` AS ad
#     INNER JOIN `tabChild Growth Monitoring`   AS cgm ON ad.parent = cgm.name
#     INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
#     INNER JOIN `tabCreche`  AS cr  ON cgm.creche_id    = cr.name
#     INNER JOIN `tabUser`    AS usr ON cr.supervisor_id = usr.name
#     INNER JOIN `tabPartner` AS p   ON p.name           = cr.partner_id
#     INNER JOIN `tabState`   AS s   ON s.name           = cr.state_id
#     INNER JOIN `tabDistrict` AS d  ON d.name           = cr.district_id
#     INNER JOIN `tabBlock`   AS b   ON b.name           = cr.block_id
#     INNER JOIN `tabGram Panchayat` AS g ON g.name      = cr.gp_id
    
#     -- Join with GF CTEs
#     LEFT JOIN gf1_calc gf1 ON ad.childenrollguid = gf1.childenrollguid
#     LEFT JOIN gf1_plus_calc gf1p ON ad.childenrollguid = gf1p.childenrollguid
#     LEFT JOIN gf2_calc gf2 ON ad.childenrollguid = gf2.childenrollguid
#     LEFT JOIN zigzag_calc zz ON ad.childenrollguid = zz.childenrollguid
#     LEFT JOIN snc_calc snc ON ad.childenrollguid = snc.childenrollguid
#     LEFT JOIN referrals r ON ad.childenrollguid = r.childenrolledguid
#     LEFT JOIN followups fu ON ad.childenrollguid = fu.childenrolledguid

#     WHERE YEAR(cgm.measurement_date)  = %(year)s
#       AND MONTH(cgm.measurement_date) = %(month)s
#       AND cee.date_of_enrollment <= %(end_date)s
#       AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#       AND {where_clause}

#     ORDER BY
#         cr.partner_id, cr.state_id, cr.district_id,
#         cr.block_id,   cr.gp_id,    cr.supervisor_id,
#         cr.name,       cee.child_name
#     """

#     data = frappe.db.sql(sql_query, params, as_dict=True)

#     # ── Python post-processing: colour-code z-scores and GF flags ────────────
#     for row in data:
#         # Z-score colour coding
#         for zscore_field, status_field in [
#             ("weight_for_age_zscore",    "weight_for_age_status"),
#             ("weight_for_height_zscore", "weight_for_height_status"),
#             ("height_for_age_zscore",    "height_for_age_status"),
#         ]:
#             val    = row.get(zscore_field)
#             status = row.get(status_field, "").lower()
#             if val is not None and val != '':
#                 row[zscore_field] = format_zscore_cell(val, status)
        
#         # Copy raw values to display fields with formatting
#         row["gf1"] = format_flag_cell(row.get("gf1_raw", "N"), "#FFE0E0" if row.get("gf1_raw") == "Y" else "#E8F5E9", 
#                                       "#CC0000" if row.get("gf1_raw") == "Y" else "#2E7D32")
#         row["gf1_plus"] = format_flag_cell(row.get("gf1_plus_raw", "N"), "#FFE0E0" if row.get("gf1_plus_raw") == "Y" else "#E8F5E9",
#                                           "#CC0000" if row.get("gf1_plus_raw") == "Y" else "#2E7D32")
#         row["gf2"] = format_flag_cell(row.get("gf2_raw", "N"), "#FFE0E0" if row.get("gf2_raw") == "Y" else "#E8F5E9",
#                                      "#CC0000" if row.get("gf2_raw") == "Y" else "#2E7D32")
#         row["gf_zigzag"] = format_flag_cell(row.get("gf_zigzag_raw", "N"), "#FFE0E0" if row.get("gf_zigzag_raw") == "Y" else "#E8F5E9",
#                                            "#CC0000" if row.get("gf_zigzag_raw") == "Y" else "#2E7D32")
#         row["snc"] = format_flag_cell(row.get("snc_raw", "N"), "#FFE0E0" if row.get("snc_raw") == "Y" else "#E8F5E9",
#                                      "#CC0000" if row.get("snc_raw") == "Y" else "#2E7D32")
        
#         # Other flags
#         row["red_flag"] = format_flag_cell(row.get("red_flag_raw", "N"), "#FFE0E0" if row.get("red_flag_raw") == "Y" else "#E8F5E9",
#                                           "#CC0000" if row.get("red_flag_raw") == "Y" else "#2E7D32")
#         row["red_flag_HV"] = format_flag_cell(row.get("red_flag_HV_raw", "-"), "#E8F5E9", "#2E7D32")
        
#         # Referral flags (Y/- format)
#         for field in ["othr", "nrc", "chc", "phc", "vhsnd", "follow_up"]:
#             raw_val = row.get(f"{field}_raw", "-")
#             if raw_val == "Y":
#                 row[field] = format_flag_cell("Y", "#E8F5E9", "#2E7D32")
#             else:
#                 row[field] = format_flag_cell("-", "#F5F5F5", "#999999")

#     # ── Summary / totals row ─────────────────────────────────────────────────
#     counts = {
#         "child_name":              0,
#         "measurements_taken":      0,
#         "gf1":                     0,
#         "gf1_plus":                0,
#         "gf2":                     0,
#         "gf_zigzag":               0,
#         "snc":                     0,
#         "any_medical_major_illness": 0,
#         "red_flag":                0,
#         "red_flag_HV":             0,
#         "follow_up":               0,
#         "vhsnd":                   0,
#         "phc":                     0,
#         "chc":                     0,
#         "nrc":                     0,
#         "othr":                    0,
#     }

#     for row in data:
#         # Initialize missing fields
#         row.setdefault("othr_raw", "-")
#         row.setdefault("nrc_raw", "-")
#         row.setdefault("chc_raw", "-")
#         row.setdefault("vhsnd_raw", "-")
#         row.setdefault("follow_up_raw", "-")
#         row.setdefault("red_flag_raw", "N")
#         row.setdefault("red_flag_HV_raw", "-")
#         row.setdefault("phc_raw", "-")
#         row.setdefault("any_medical_major_illness", 0)

#         counts["child_name"] += 1
#         if row.get("measurements_taken_raw") == 1:
#             counts["measurements_taken"] += 1

#         # Count GF flags from raw values
#         if row.get("gf1_raw") == "Y":
#             counts["gf1"] += 1
#         if row.get("gf1_plus_raw") == "Y":
#             counts["gf1_plus"] += 1
#         if row.get("gf2_raw") == "Y":
#             counts["gf2"] += 1
#         if row.get("gf_zigzag_raw") == "Y":
#             counts["gf_zigzag"] += 1
#         if row.get("snc_raw") == "Y":
#             counts["snc"] += 1

#         # Count other flags from raw values
#         if row.get("nrc_raw") == "Y":
#             counts["nrc"] += 1
#         if row.get("phc_raw") == "Y":
#             counts["phc"] += 1
#         if row.get("chc_raw") == "Y":
#             counts["chc"] += 1
#         if row.get("vhsnd_raw") == "Y":
#             counts["vhsnd"] += 1
#         if row.get("follow_up_raw") == "Y":
#             counts["follow_up"] += 1
#         if row.get("red_flag_raw") == "Y":
#             counts["red_flag"] += 1
#         if row.get("red_flag_HV_raw") == "Y":
#             counts["red_flag_HV"] += 1
#         if row.get("othr_raw") == "Y":
#             counts["othr"] += 1

#         if row.get("any_medical_major_illness") == 1:
#             counts["any_medical_major_illness"] += 1

#     summary_row = {
#         "partner":                   "<b style='color:black;'>Total</b>",
#         "child_name":                f"<b>{counts['child_name']}</b>",
#         "measurements_taken":        f"<b>{counts['measurements_taken']}</b>",
#         "gf1":                       f"<b>{counts['gf1']}</b>",
#         "gf1_plus":                  f"<b>{counts['gf1_plus']}</b>",
#         "gf2":                       f"<b>{counts['gf2']}</b>",
#         "gf_zigzag":                 f"<b>{counts['gf_zigzag']}</b>",
#         "snc":                       f"<b>{counts['snc']}</b>",
#         "any_medical_major_illness": f"<b>{counts['any_medical_major_illness']}</b>",
#         "red_flag":                  f"<b>{counts['red_flag']}</b>",
#         "red_flag_HV":               f"<b>{counts['red_flag_HV']}</b>",
#         "follow_up":                 f"<b>{counts['follow_up']}</b>",
#         "vhsnd":                     f"<b>{counts['vhsnd']}</b>",
#         "phc":                       f"<b>{counts['phc']}</b>",
#         "chc":                       f"<b>{counts['chc']}</b>",
#         "nrc":                       f"<b>{counts['nrc']}</b>",
#         "othr":                      f"<b>{counts['othr']}</b>",
#     }
#     data.append(summary_row)
#     return data


# # ─────────────────────────────────────────────────────────────────────────────
# # Formatting helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def format_zscore_cell(value, status):
#     """Colour-code z-score cell based on nutritional status."""
#     if value is None or value == '':
#         return value
        
#     color_map = {
#         "severe":    ("#FFCCCC", "#CC0000"),
#         "moderate":  ("#FFFFCC", "#999900"),
#         "normal":    ("#CCFFCC", "#006600"),
#     }
#     if status in color_map:
#         bg, fg = color_map[status]
#         return format_cell(value, bg, fg)
#     return str(value)


# def format_flag_cell(value, bg_color, text_color):
#     """Colour-code a Y/N flag cell."""
#     return format_cell(value, bg_color, text_color)


# def format_cell(value, bg_color, text_color):
#     """Wrap a value in a coloured HTML div."""
#     if value is None:
#         return ""
#     return (
#         f"<div style='"
#         f"background-color:{bg_color};"
#         f"color:{text_color};"
#         f"border-radius:3px;"
#         f"text-align:center;"
#         f"font-weight:bold;"
#         f"padding:2px 5px;"
#         f"'>{value}</div>"
#     )











# import frappe
# from frappe.utils import nowdate
# import calendar
# from datetime import datetime, timedelta, date

# def execute(filters=None):
#     columns = get_columns()
#     data    = get_summary_data(filters)
#     return columns, data


# def get_columns():
#     return [
#         # ── Identity ──────────────────────────────────────────────────────────
#         {"label": "Partner",                        "fieldname": "partner",                   "fieldtype": "Data", "width": 120},
#         {"label": "State",                          "fieldname": "state",                     "fieldtype": "Data", "width": 120},
#         {"label": "District",                       "fieldname": "district",                  "fieldtype": "Data", "width": 120},
#         {"label": "Block",                          "fieldname": "block",                     "fieldtype": "Data", "width": 120},
#         {"label": "GP",                             "fieldname": "gp",                        "fieldtype": "Data", "width": 120},
#         {"label": "Creche",                         "fieldname": "creche_name",               "fieldtype": "Data", "width": 200},
#         {"label": "Creche ID",                      "fieldname": "creche_id",                 "fieldtype": "Data", "width": 150},
#         {"label": "Supervisor",                     "fieldname": "supervisor",                "fieldtype": "Data", "width": 200},
#         {"label": "Child Name",                     "fieldname": "child_name",                "fieldtype": "Data", "width": 200},
#         {"label": "Child ID",                       "fieldname": "child_id",                  "fieldtype": "Data", "width": 150},
#         {"label": "Date of Birth",                  "fieldname": "child_dob",                 "fieldtype": "Data", "width": 150},
#         {"label": "Age (At Enrollment)",            "fieldname": "age",                       "fieldtype": "Data", "width": 180},
#         {"label": "Current Age",                    "fieldname": "current_age",               "fieldtype": "Data", "width": 150},
#         {"label": "Gender",                         "fieldname": "gender",                    "fieldtype": "Data", "width": 100},

#         # ── Measurements ──────────────────────────────────────────────────────
#         {"label": "Height (cm)",                    "fieldname": "height",                    "fieldtype": "Data", "width": 130},
#         {"label": "Weight (kg)",                    "fieldname": "weight",                    "fieldtype": "Data", "width": 130},
#         {"label": "Measurement Date",               "fieldname": "measurements_taken_date",   "fieldtype": "Data", "width": 200},
#         {"label": "Measurement Taken",              "fieldname": "measurements_taken",        "fieldtype": "Data", "width": 180},
#         {"label": "Measurement Not Taken",          "fieldname": "measurement_reason",        "fieldtype": "Data", "width": 200},

#         # ── Z-scores (colour-coded) ───────────────────────────────────────────
#         {"label": "Weight for Age (Z-score)",       "fieldname": "weight_for_age_zscore",     "fieldtype": "Data", "width": 200},
#         {"label": "Weight for Height (Z-score)",    "fieldname": "weight_for_height_zscore",  "fieldtype": "Data", "width": 210},
#         {"label": "Height for Age (Z-score)",       "fieldname": "height_for_age_zscore",     "fieldtype": "Data", "width": 200},

#         # ── Growth Faltering (WHO WAZ-based) ─────────────────────────────────
#         {"label": "GF1 ",                           "fieldname": "gf1",                       "fieldtype": "Data", "width": 160, "align": "center"},
#         {"label": "GF1+",                           "fieldname": "gf1_plus",                  "fieldtype": "Data", "width": 185, "align": "center"},
#         {"label": "GF2",                            "fieldname": "gf2",                       "fieldtype": "Data", "width": 175, "align": "center"},
#         {"label": "GF ZigZag ",                     "fieldname": "gf_zigzag",                 "fieldtype": "Data", "width": 185, "align": "center"},
#         {"label": "SNC",                            "fieldname": "snc",                       "fieldtype": "Data", "width": 100, "align": "center"},

#         # ── Other flags ───────────────────────────────────────────────────────
#         # {"label": "Medical Complication",           "fieldname": "any_medical_major_illness", "fieldtype": "Data", "width": 170, "align": "center"},
#         # {"label": "Red Flag",                       "fieldname": "red_flag",                  "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": "Home Visit",                     "fieldname": "red_flag_HV",               "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": "Followup",                       "fieldname": "follow_up",                 "fieldtype": "Data", "width": 120},
#         {"label": "Taken to VHND",                  "fieldname": "vhsnd",                     "fieldtype": "Data", "width": 140},
#         {"label": "Taken to PHC",                   "fieldname": "phc",                       "fieldtype": "Data", "width": 120},
#         {"label": "Taken to CHC",                   "fieldname": "chc",                       "fieldtype": "Data", "width": 120},
#         {"label": "Taken to NRC",                   "fieldname": "nrc",                       "fieldtype": "Data", "width": 120},
#         {"label": "Taken to other Health Facility", "fieldname": "othr",                      "fieldtype": "Data", "width": 250},
#     ]


# # ─────────────────────────────────────────────────────────────────────────────
# # Main data function
# # ─────────────────────────────────────────────────────────────────────────────

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}

#     # ── Date setup ────────────────────────────────────────────────────────────
#     current_date = date.today()
#     month  = int(filters.get("month",  current_date.month))
#     year   = int(filters.get("year",   current_date.year))

#     start_date = date(year, month, 1)
#     last_day   = calendar.monthrange(year, month)[1]
#     end_date   = date(year, month, last_day)

#     # Previous months (for GF calculations)
#     # m-1
#     if month == 1:
#         lmonth, lyear   = 12, year - 1
#     else:
#         lmonth, lyear   = month - 1, year

#     # m-2
#     if lmonth == 1:
#         plmonth, pyear  = 12, lyear - 1
#     else:
#         plmonth, pyear  = lmonth - 1, lyear

#     # m-3  (for GF ZigZag)
#     if plmonth == 1:
#         l3month, l3year = 12, pyear - 1
#     else:
#         l3month, l3year = plmonth - 1, pyear

#     # m-4  (for GF ZigZag)
#     if l3month == 1:
#         l4month, l4year = 12, l3year - 1
#     else:
#         l4month, l4year = l3month - 1, l3year

#     # ── Params ────────────────────────────────────────────────────────────────
#     params = {
#         "start_date":  start_date,
#         "end_date":    end_date,
#         "year":        year,
#         "month":       month,
#         "lyear":       lyear,
#         "lmonth":      lmonth,
#         "plmonth":     plmonth,
#         "pyear":       pyear,
#         "l3month":     l3month,
#         "l3year":      l3year,
#         "l4month":     l4month,
#         "l4year":      l4year,
#         "cstart_date": None,
#         "cend_date":   None,
#         "partner":     None,
#         "state":       None,
#         "district":    None,
#         "block":       None,
#         "gp":          None,
#         "creche":      None,
#         "supervisor_id":    None,
#         "creche_status_id": None,
#         "phases":      None,
#     }

#     # ── User partner + geography ──────────────────────────────────────────────
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     state_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)

#     # ── Creche opening date range ─────────────────────────────────────────────
#     range_type = filters.get("cr_opening_range_type")
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range  = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()

#         if range_type == "between" and date_range and len(date_range) == 2:
#             params["cstart_date"], params["cend_date"] = date_range
#         elif range_type == "before" and single_date:
#             params["cstart_date"] = date(2017, 1, 1)
#             params["cend_date"]   = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             params["cstart_date"] = single_date + timedelta(days=1)
#             params["cend_date"]   = date.today()
#         elif range_type == "equal" and single_date:
#             params["cstart_date"] = single_date

#     # ── Build geography params ────────────────────────────────────────────────
#     if partner_id:
#         params["partner"] = partner_id

#     if filters.get("state"):
#         params["state"] = filters.get("state")
#     else:
#         ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#         if ids:
#             params["state_ids"] = ",".join(ids)

#     if filters.get("district"):
#         params["district"] = filters.get("district")
#     else:
#         ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#         if ids:
#             params["district_ids"] = ",".join(ids)

#     if filters.get("block"):
#         params["block"] = filters.get("block")
#     else:
#         ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#         if ids:
#             params["block_ids"] = ",".join(ids)

#     if filters.get("gp"):
#         params["gp"] = filters.get("gp")
#     else:
#         ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
#         if ids:
#             params["gp_ids"] = ",".join(ids)

#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if cleaned:
#             params["phases"] = cleaned

#     # ── WHERE conditions ─────────────────────────────────────────────────────
#     conditions = []

#     if params.get("partner"):
#         conditions.append("cr.partner_id = %(partner)s")
#     if params.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#     if params.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#     if params.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#     if params.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#     if params.get("creche"):
#         conditions.append("cr.name = %(creche)s")
#     if params.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#     if params.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):
#         conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     # ── SQL query ─────────────────────────────────────────────────────────────
#     # NOTE ON GF LOGIC:
#     #  All Growth Faltering is now based on weight_for_age_zscore (WAZ), not raw weight.
#     #  The self-join sub-CTE approach is used for GF1+ / GF2 / GF ZigZag
#     #  so that null z-scores are safely excluded.

#     sql_query = f"""
#         SELECT DISTINCT
#             cr.creche_name                                          AS creche_name,
#             usr.full_name                                           AS supervisor,
#             cee.child_id                                            AS child_id,
#             cr.creche_id                                            AS creche_id,
#             cee.child_name                                          AS child_name,
#             cee.age_at_enrollment_in_months                         AS age,
#             DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y')              AS child_dob,
#             CASE 
#                 WHEN DATE_FORMAT(%(end_date)s,'%%Y-%%m') = DATE_FORMAT(CURDATE(),'%%Y-%%m')
#                 THEN TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE())
#                 ELSE TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s)
#             END                                                     AS current_age,
#             CASE 
#                 WHEN cee.gender_id = '1' THEN 'M'
#                 WHEN cee.gender_id = '2' THEN 'F'
#                 ELSE cee.gender_id
#             END                                                     AS gender,
#             ad.height                                               AS height,
#             ad.weight                                               AS weight,
#             ad.do_you_have_height_weight                            AS measurements_taken_raw,
#             IF(ad.do_you_have_height_weight = 1,'Y','N')            AS measurements_taken,
#             IFNULL(DATE_FORMAT(ad.measurement_taken_date,'%%d-%%m-%%Y'),'-')
#                                                                     AS measurements_taken_date,
#             CASE 
#                 WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
#                 WHEN ad.measurement_reason = 2 THEN 'Child not in village'
#                 WHEN ad.measurement_reason = 3 THEN 'Child is sick'
#                 WHEN ad.measurement_reason = 4 THEN 'Others'
#                 ELSE ''
#             END                                                     AS measurement_reason,

#             -- Z-scores (raw; formatted in Python)
#             ad.weight_for_age_zscore                                AS weight_for_age_zscore,
#             ad.weight_for_height_zscore                             AS weight_for_height_zscore,
#             ad.height_for_age_zscore                                AS height_for_age_zscore,

#             -- Status labels (used for Python colour-coding; hidden in UI)
#             CASE WHEN ad.weight_for_age   = 3 THEN 'Normal'
#                  WHEN ad.weight_for_age   = 2 THEN 'Moderate'
#                  WHEN ad.weight_for_age   = 1 THEN 'Severe'
#                  ELSE '' END                                        AS weight_for_age_status,
#             CASE WHEN ad.height = 0 THEN '-'
#                  WHEN ad.height_for_age   = 3 THEN 'Normal'
#                  WHEN ad.height_for_age   = 2 THEN 'Moderate'
#                  WHEN ad.height_for_age   = 1 THEN 'Severe'
#                  ELSE '' END                                        AS height_for_age_status,
#             CASE WHEN ad.height = 0 THEN '-'
#                  WHEN ad.weight_for_height = 3 THEN 'Normal'
#                  WHEN ad.weight_for_height = 2 THEN 'Moderate'
#                  WHEN ad.weight_for_height = 1 THEN 'Severe'
#                  ELSE '' END                                        AS weight_for_height_status,

#             /*
#             ═══════════════════════════════════════════════════════════════
#              GF1 — Any drop in WAZ from the previous month
#              Logic : current_waz < last_month_waz
#             ═══════════════════════════════════════════════════════════════*/
#             CASE
#                 WHEN ad.do_you_have_height_weight = 0 THEN 'N'
#                 WHEN ad.weight_for_age_zscore IS NULL
#                   OR ad.weight_for_age_zscore = '' THEN 'N'
#                 WHEN ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     INNER JOIN `tabAnthropromatic Data` AS ad_prev
#                            ON  ad_prev.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_prev.do_you_have_height_weight = 1
#                            AND YEAR(ad_prev.measurement_taken_date)  = %(lyear)s
#                            AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
#                            AND ad_prev.weight_for_age_zscore IS NOT NULL
#                            AND ad_prev.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       AND CAST(ad_cur.weight_for_age_zscore  AS DECIMAL(10,4))
#                         < CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4))
#                 ) THEN 'Y'
#                 ELSE 'N'
#             END AS gf1,

#             /*
#             ═══════════════════════════════════════════════════════════════
#              GF1+ — WAZ drop >= 0.5 vs BEST of last 2 months
#              Logic : current_waz <= MAX(waz_m1, waz_m2) - 0.5
#             ═══════════════════════════════════════════════════════════════*/
#             CASE
#                 WHEN ad.do_you_have_height_weight = 0 THEN 'N'
#                 WHEN ad.weight_for_age_zscore IS NULL
#                   OR ad.weight_for_age_zscore = '' THEN 'N'
#                 WHEN ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     LEFT JOIN `tabAnthropromatic Data` AS ad_m1
#                            ON  ad_m1.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_m1.do_you_have_height_weight = 1
#                            AND YEAR(ad_m1.measurement_taken_date)  = %(lyear)s
#                            AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
#                            AND ad_m1.weight_for_age_zscore IS NOT NULL
#                            AND ad_m1.weight_for_age_zscore != ''
#                     LEFT JOIN `tabAnthropromatic Data` AS ad_m2
#                            ON  ad_m2.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_m2.do_you_have_height_weight = 1
#                            AND YEAR(ad_m2.measurement_taken_date)  = %(pyear)s
#                            AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
#                            AND ad_m2.weight_for_age_zscore IS NOT NULL
#                            AND ad_m2.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       -- At least one prior month must exist
#                       AND (ad_m1.weight_for_age_zscore IS NOT NULL
#                            OR ad_m2.weight_for_age_zscore IS NOT NULL)
#                       -- current <= BEST of last 2 months - 0.5
#                       AND CAST(ad_cur.weight_for_age_zscore AS DECIMAL(10,4))
#                           <= GREATEST(
#                                  COALESCE(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), -999),
#                                  COALESCE(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), -999)
#                              ) - 0.5
#                 ) THEN 'Y'
#                 ELSE 'N'
#             END AS gf1_plus,

#             /*
#             ═══════════════════════════════════════════════════════════════
#              GF2 — WAZ drop >= 0.5 vs 2 months ago
#              Logic : current_waz <= waz_2m_ago - 0.5
#             ═══════════════════════════════════════════════════════════════*/
#             CASE
#                 WHEN ad.do_you_have_height_weight = 0 THEN 'N'
#                 WHEN ad.weight_for_age_zscore IS NULL
#                   OR ad.weight_for_age_zscore = '' THEN 'N'
#                 WHEN ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     INNER JOIN `tabAnthropromatic Data` AS ad_2m
#                            ON  ad_2m.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_2m.do_you_have_height_weight = 1
#                            AND YEAR(ad_2m.measurement_taken_date)  = %(pyear)s
#                            AND MONTH(ad_2m.measurement_taken_date) = %(plmonth)s
#                            AND ad_2m.weight_for_age_zscore IS NOT NULL
#                            AND ad_2m.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       AND CAST(ad_cur.weight_for_age_zscore AS DECIMAL(10,4))
#                           <= CAST(ad_2m.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#                 ) THEN 'Y'
#                 ELSE 'N'
#             END AS gf2,

#             /*
#             ═══════════════════════════════════════════════════════════════
#              GF ZigZag — Mixed gain+loss over last 4 months
#                          AND drop >= 0.5 from peak of those 4 months
#              Requires all 4 prior months to have valid WAZ data.
#             ═══════════════════════════════════════════════════════════════*/
#             CASE
#                 WHEN ad.do_you_have_height_weight = 0 THEN 'N'
#                 WHEN ad.weight_for_age_zscore IS NULL
#                   OR ad.weight_for_age_zscore = '' THEN 'N'
#                 WHEN ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     -- 1 month ago
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz1
#                            ON  ad_zz1.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz1.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz1.measurement_taken_date)  = %(lyear)s
#                            AND MONTH(ad_zz1.measurement_taken_date) = %(lmonth)s
#                            AND ad_zz1.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz1.weight_for_age_zscore != ''
#                     -- 2 months ago
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz2
#                            ON  ad_zz2.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz2.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz2.measurement_taken_date)  = %(pyear)s
#                            AND MONTH(ad_zz2.measurement_taken_date) = %(plmonth)s
#                            AND ad_zz2.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz2.weight_for_age_zscore != ''
#                     -- 3 months ago
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz3
#                            ON  ad_zz3.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz3.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz3.measurement_taken_date)  = %(l3year)s
#                            AND MONTH(ad_zz3.measurement_taken_date) = %(l3month)s
#                            AND ad_zz3.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz3.weight_for_age_zscore != ''
#                     -- 4 months ago
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz4
#                            ON  ad_zz4.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz4.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz4.measurement_taken_date)  = %(l4year)s
#                            AND MONTH(ad_zz4.measurement_taken_date) = %(l4month)s
#                            AND ad_zz4.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz4.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       -- Drop >= 0.5 from highest of last 4 months
#                       AND GREATEST(
#                               CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)),
#                               CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)),
#                               CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)),
#                               CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                           ) - CAST(ad_cur.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5
#                       -- At least one gain in the 4-month sequence
#                       AND (
#                           CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                       )
#                       -- At least one loss in the 4-month sequence
#                       AND (
#                           CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                       )
#                 ) THEN 'Y'
#                 ELSE 'N'
#             END AS gf_zigzag,

#             /*
#             ═══════════════════════════════════════════════════════════════
#              SNC — Severe Nutritional Concern
#              = GF1+ OR GF2 OR GF ZigZag OR SAM (WFH=1) OR SUW (WAZ<=-3)
#             ═══════════════════════════════════════════════════════════════*/
#             CASE
#                 WHEN ad.do_you_have_height_weight = 0 THEN 'N'
#                 -- SAM: Severe Acute Malnutrition (WFH = 1)
#                 WHEN ad.weight_for_height = 1 THEN 'Y'
#                 -- SUW: Severely Underweight (WAZ <= -3)
#                 WHEN ad.weight_for_age_zscore IS NOT NULL
#                  AND ad.weight_for_age_zscore != ''
#                  AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= -3 THEN 'Y'
#                 -- GF1+
#                 WHEN ad.weight_for_age_zscore IS NOT NULL
#                  AND ad.weight_for_age_zscore != ''
#                  AND ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     LEFT JOIN `tabAnthropromatic Data` AS ad_m1
#                            ON  ad_m1.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_m1.do_you_have_height_weight = 1
#                            AND YEAR(ad_m1.measurement_taken_date)  = %(lyear)s
#                            AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
#                            AND ad_m1.weight_for_age_zscore IS NOT NULL
#                            AND ad_m1.weight_for_age_zscore != ''
#                     LEFT JOIN `tabAnthropromatic Data` AS ad_m2
#                            ON  ad_m2.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_m2.do_you_have_height_weight = 1
#                            AND YEAR(ad_m2.measurement_taken_date)  = %(pyear)s
#                            AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
#                            AND ad_m2.weight_for_age_zscore IS NOT NULL
#                            AND ad_m2.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       AND (ad_m1.weight_for_age_zscore IS NOT NULL OR ad_m2.weight_for_age_zscore IS NOT NULL)
#                       AND CAST(ad_cur.weight_for_age_zscore AS DECIMAL(10,4))
#                           <= GREATEST(
#                                  COALESCE(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), -999),
#                                  COALESCE(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), -999)
#                              ) - 0.5
#                  ) THEN 'Y'
#                 -- GF2
#                 WHEN ad.weight_for_age_zscore IS NOT NULL
#                  AND ad.weight_for_age_zscore != ''
#                  AND ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     INNER JOIN `tabAnthropromatic Data` AS ad_2m
#                            ON  ad_2m.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_2m.do_you_have_height_weight = 1
#                            AND YEAR(ad_2m.measurement_taken_date)  = %(pyear)s
#                            AND MONTH(ad_2m.measurement_taken_date) = %(plmonth)s
#                            AND ad_2m.weight_for_age_zscore IS NOT NULL
#                            AND ad_2m.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       AND CAST(ad_cur.weight_for_age_zscore AS DECIMAL(10,4))
#                           <= CAST(ad_2m.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#                  ) THEN 'Y'
#                 -- GF ZigZag
#                 WHEN ad.weight_for_age_zscore IS NOT NULL
#                  AND ad.weight_for_age_zscore != ''
#                  AND ad.childenrollguid IN (
#                     SELECT ad_cur.childenrollguid
#                     FROM `tabAnthropromatic Data`     AS ad_cur
#                     INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                            ON cgm2.name = ad_cur.parent
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz1
#                            ON  ad_zz1.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz1.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz1.measurement_taken_date)  = %(lyear)s
#                            AND MONTH(ad_zz1.measurement_taken_date) = %(lmonth)s
#                            AND ad_zz1.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz1.weight_for_age_zscore != ''
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz2
#                            ON  ad_zz2.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz2.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz2.measurement_taken_date)  = %(pyear)s
#                            AND MONTH(ad_zz2.measurement_taken_date) = %(plmonth)s
#                            AND ad_zz2.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz2.weight_for_age_zscore != ''
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz3
#                            ON  ad_zz3.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz3.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz3.measurement_taken_date)  = %(l3year)s
#                            AND MONTH(ad_zz3.measurement_taken_date) = %(l3month)s
#                            AND ad_zz3.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz3.weight_for_age_zscore != ''
#                     INNER JOIN `tabAnthropromatic Data` AS ad_zz4
#                            ON  ad_zz4.childenrollguid        = ad_cur.childenrollguid
#                            AND ad_zz4.do_you_have_height_weight = 1
#                            AND YEAR(ad_zz4.measurement_taken_date)  = %(l4year)s
#                            AND MONTH(ad_zz4.measurement_taken_date) = %(l4month)s
#                            AND ad_zz4.weight_for_age_zscore IS NOT NULL
#                            AND ad_zz4.weight_for_age_zscore != ''
#                     WHERE ad_cur.do_you_have_height_weight = 1
#                       AND YEAR(cgm2.measurement_date)  = %(year)s
#                       AND MONTH(cgm2.measurement_date) = %(month)s
#                       AND ad_cur.weight_for_age_zscore IS NOT NULL
#                       AND ad_cur.weight_for_age_zscore != ''
#                       AND GREATEST(
#                               CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)),
#                               CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)),
#                               CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)),
#                               CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                           ) - CAST(ad_cur.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5
#                       AND (
#                           CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                       )
#                       AND (
#                           CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4))
#                           OR CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                       )
#                  ) THEN 'Y'
#                 ELSE 'N'
#             END AS snc,

#             -- Medical & Red-flag fields
#             ad.any_medical_major_illness                            AS any_medical_major_illness,
#             CASE
#                 WHEN (
#                     ad.weight_for_age   = 1
#                     OR ad.weight_for_height = 1
#                     OR ad.any_medical_major_illness = 1
#                     -- GF2 re-check for red flag
#                     OR ad.childenrollguid IN (
#                         SELECT ad_cur.childenrollguid
#                         FROM `tabAnthropromatic Data`     AS ad_cur
#                         INNER JOIN `tabChild Growth Monitoring` AS cgm2
#                                ON cgm2.name = ad_cur.parent
#                         INNER JOIN `tabAnthropromatic Data` AS ad_lyear
#                                ON  ad_lyear.childenrollguid        = ad_cur.childenrollguid
#                                AND ad_lyear.do_you_have_height_weight = 1
#                                AND YEAR(ad_lyear.measurement_taken_date)  = %(lyear)s
#                                AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s
#                                AND ad_lyear.weight_for_age_zscore IS NOT NULL
#                                AND ad_lyear.weight_for_age_zscore != ''
#                         INNER JOIN `tabAnthropromatic Data` AS ad_pyear
#                                ON  ad_pyear.childenrollguid        = ad_cur.childenrollguid
#                                AND ad_pyear.do_you_have_height_weight = 1
#                                AND YEAR(ad_pyear.measurement_taken_date)  = %(pyear)s
#                                AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s
#                                AND ad_pyear.weight_for_age_zscore IS NOT NULL
#                                AND ad_pyear.weight_for_age_zscore != ''
#                         WHERE ad_cur.do_you_have_height_weight = 1
#                           AND YEAR(cgm2.measurement_date)  = %(year)s
#                           AND MONTH(cgm2.measurement_date) = %(month)s
#                           AND ad_cur.weight_for_age_zscore IS NOT NULL
#                           AND ad_cur.weight_for_age_zscore != ''
#                           AND CAST(ad_cur.weight_for_age_zscore  AS DECIMAL(10,4))
#                               <= CAST(ad_pyear.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#                     )
#                 ) THEN 'Y'
#                 ELSE 'N'
#             END AS red_flag,

#             CASE WHEN crfd.date_of_referral IS NOT NULL THEN 'Y' ELSE '-' END  AS red_flag_HV,
#             IFNULL(CASE WHEN crfd.referred_to = 5 THEN 'Y' ELSE '-' END, '-') AS othr,
#             CASE WHEN crfd.referred_to = 4 THEN 'Y' ELSE '-' END              AS nrc,
#             CASE WHEN crfd.referred_to = 3 THEN 'Y' ELSE '-' END              AS chc,
#             CASE WHEN crfd.referred_to = 2 THEN 'Y' ELSE '-' END              AS phc,
#             CASE WHEN crfd.referred_to = 1 THEN 'Y' ELSE '-' END              AS vhsnd,
#             cfud.follow_up                                                     AS follow_up,
#             p.partner_name  AS partner,
#             s.state_name    AS state,
#             d.district_name AS district,
#             b.block_name    AS block,
#             g.gp_name       AS gp

#         FROM `tabAnthropromatic Data` AS ad
#         INNER JOIN `tabChild Growth Monitoring`   AS cgm ON ad.parent = cgm.name
#         INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
#         INNER JOIN `tabCreche`  AS cr  ON cgm.creche_id    = cr.name
#         INNER JOIN `tabUser`    AS usr ON cr.supervisor_id = usr.name
#         INNER JOIN `tabPartner` AS p   ON p.name           = cr.partner_id
#         INNER JOIN `tabState`   AS s   ON s.name           = cr.state_id
#         INNER JOIN `tabDistrict` AS d  ON d.name           = cr.district_id
#         INNER JOIN `tabBlock`   AS b   ON b.name           = cr.block_id
#         INNER JOIN `tabGram Panchayat` AS g ON g.name      = cr.gp_id

#         LEFT JOIN (
#             SELECT crf.childenrolledguid, crf.date_of_referral, crf.referred_to
#             FROM `tabChild Referral` AS crf
#             WHERE YEAR(crf.date_of_referral)  = %(year)s
#               AND MONTH(crf.date_of_referral) = %(month)s
#               AND (%(partner)s  IS NULL OR crf.partner_id  = %(partner)s)
#               AND (%(state)s    IS NULL OR crf.state_id    = %(state)s)
#               AND (%(district)s IS NULL OR crf.district_id = %(district)s)
#               AND (%(block)s    IS NULL OR crf.block_id    = %(block)s)
#               AND (%(gp)s       IS NULL OR crf.gp_id       = %(gp)s)
#               AND (%(creche)s   IS NULL OR crf.creche_id   = %(creche)s)
#         ) AS crfd ON crfd.childenrolledguid = ad.childenrollguid

#         LEFT JOIN (
#             SELECT cfu.childenrolledguid,
#                    CASE WHEN cfu.followup_visit_date THEN 'Y' ELSE '-' END AS follow_up
#             FROM `tabChild Follow up` AS cfu
#             WHERE YEAR(cfu.followup_visit_date)  = %(year)s
#               AND MONTH(cfu.followup_visit_date) = %(month)s
#               AND (%(partner)s  IS NULL OR cfu.partner_id  = %(partner)s)
#               AND (%(state)s    IS NULL OR cfu.state_id    = %(state)s)
#               AND (%(district)s IS NULL OR cfu.district_id = %(district)s)
#               AND (%(block)s    IS NULL OR cfu.block_id    = %(block)s)
#               AND (%(gp)s       IS NULL OR cfu.gp_id       = %(gp)s)
#               AND (%(creche)s   IS NULL OR cfu.creche_id   = %(creche)s)
#         ) AS cfud ON cfud.childenrolledguid = ad.childenrollguid

#         WHERE YEAR(cgm.measurement_date)  = %(year)s
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND cee.date_of_enrollment <= %(end_date)s
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#           AND {where_clause}

#         ORDER BY
#             cr.partner_id, cr.state_id, cr.district_id,
#             cr.block_id,   cr.gp_id,    cr.supervisor_id,
#             cr.name,       cee.child_name
#     """

#     data = frappe.db.sql(sql_query, params, as_dict=True)

#     # ── Python post-processing: colour-code z-scores and GF flags ────────────
#     for row in data:
#         # Z-score colour coding
#         for zscore_field, status_field in [
#             ("weight_for_age_zscore",    "weight_for_age_status"),
#             ("weight_for_height_zscore", "weight_for_height_status"),
#             ("height_for_age_zscore",    "height_for_age_status"),
#         ]:
#             val    = row.get(zscore_field)
#             status = row.get(status_field, "").lower()
#             if val is not None:
#                 row[zscore_field] = format_zscore_cell(val, status)

#         # GF flag colour coding
#         for gf_field in ("gf1", "gf1_plus", "gf2", "gf_zigzag", "snc"):
#             val = row.get(gf_field)
#             if val == "Y":
#                 row[gf_field] = format_flag_cell("Y", "#FFE0E0", "#CC0000")
#             elif val == "N":
#                 row[gf_field] = format_flag_cell("N", "#E8F5E9", "#2E7D32")

#     # ── Summary / totals row ─────────────────────────────────────────────────
#     counts = {
#         "child_name":              0,
#         "measurements_taken":      0,
#         "gf1":                     0,
#         "gf1_plus":                0,
#         "gf2":                     0,
#         "gf_zigzag":               0,
#         "snc":                     0,
#         "any_medical_major_illness": 0,
#         "red_flag":                0,
#         "red_flag_HV":             0,
#         "follow_up":               0,
#         "vhsnd":                   0,
#         "phc":                     0,
#         "chc":                     0,
#         "nrc":                     0,
#         "othr":                    0,
#     }

#     for row in data:
#         row.setdefault("othr",     "-")
#         row.setdefault("nrc",      "-")
#         row.setdefault("chc",      "-")
#         row.setdefault("vhsnd",    "-")
#         row.setdefault("follow_up","-")
#         row.setdefault("red_flag", "-")
#         row.setdefault("red_flag_HV", "-")
#         row.setdefault("phc",      "-")
#         row.setdefault("any_medical_major_illness", 0)

#         counts["child_name"] += 1
#         if row.get("measurements_taken_raw") == 1:
#             counts["measurements_taken"] += 1

#         # GF flags — check raw 'Y' or HTML-wrapped 'Y'
#         for field in ("gf1", "gf1_plus", "gf2", "gf_zigzag", "snc"):
#             raw = row.get(field, "")
#             if "Y" in str(raw):
#                 counts[field] += 1

#         for field in ("nrc", "phc", "chc", "vhsnd", "follow_up",
#                       "red_flag", "red_flag_HV", "othr"):
#             if "Y" in str(row.get(field, "")):
#                 counts[field] += 1

#         if row.get("any_medical_major_illness") == 1:
#             counts["any_medical_major_illness"] += 1

#     summary_row = {
#         "partner":                   "<b style='color:black;'>Total</b>",
#         "child_name":                f"<b>{counts['child_name']}</b>",
#         "measurements_taken":        f"<b>{counts['measurements_taken']}</b>",
#         "gf1":                       f"<b>{counts['gf1']}</b>",
#         "gf1_plus":                  f"<b>{counts['gf1_plus']}</b>",
#         "gf2":                       f"<b>{counts['gf2']}</b>",
#         "gf_zigzag":                 f"<b>{counts['gf_zigzag']}</b>",
#         "snc":                       f"<b>{counts['snc']}</b>",
#         "any_medical_major_illness": f"<b>{counts['any_medical_major_illness']}</b>",
#         "red_flag":                  f"<b>{counts['red_flag']}</b>",
#         "red_flag_HV":               f"<b>{counts['red_flag_HV']}</b>",
#         "follow_up":                 f"<b>{counts['follow_up']}</b>",
#         "vhsnd":                     f"<b>{counts['vhsnd']}</b>",
#         "phc":                       f"<b>{counts['phc']}</b>",
#         "chc":                       f"<b>{counts['chc']}</b>",
#         "nrc":                       f"<b>{counts['nrc']}</b>",
#         "othr":                      f"<b>{counts['othr']}</b>",
#     }
#     data.append(summary_row)
#     return data


# # ─────────────────────────────────────────────────────────────────────────────
# # Formatting helpers
# # ─────────────────────────────────────────────────────────────────────────────

# def format_zscore_cell(value, status):
#     """Colour-code z-score cell based on nutritional status."""
#     color_map = {
#         "severe":    ("#FFCCCC", "#CC0000"),
#         "moderate":  ("#FFFFCC", "#999900"),
#         "normal":    ("#CCFFCC", "#006600"),
#     }
#     if status in color_map:
#         bg, fg = color_map[status]
#         return format_cell(value, bg, fg)
#     return value


# def format_flag_cell(value, bg_color, text_color):
#     """Colour-code a Y/N flag cell."""
#     return format_cell(value, bg_color, text_color)


# def format_cell(value, bg_color, text_color):
#     """Wrap a value in a coloured HTML div."""
#     if value is None:
#         return ""
#     return (
#         f"<div style='"
#         f"background-color:{bg_color};"
#         f"color:{text_color};"
#         f"border-radius:3px;"
#         f"text-align:center;"
#         f"font-weight:bold;"
#         f"padding:2px 5px;"
#         f"'>{value}</div>"
#     )


















## Old Structure code
# ||||||||||
# import frappe
# from frappe.utils import nowdate
# import calendar
# from datetime import datetime, timedelta, date

# def execute(filters=None):
#     columns = get_columns()
#     data = get_summary_data(filters)
#     return columns, data

# def get_columns():
#     columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
#         {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
#         {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 150},
#         {"label": "Age (At enrollment)", "fieldname": "age", "fieldtype": "Data", "width": 180},
#         {"label": "Current Age", "fieldname": "current_age", "fieldtype": "Data", "width": 150},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
#         {"label": "Height (cm)", "fieldname": "height", "fieldtype": "Data", "width": 130},
#         {"label": "Weight (kg)", "fieldname": "weight", "fieldtype": "Data", "width": 130},
#         {"label": "Measurement Date", "fieldname": "measurements_taken_date", "fieldtype": "Data", "width": 200},
#         {"label": "Measurement Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 180},
#         {"label": "Measurement Not Taken", "fieldname": "measurement_reason", "fieldtype": "Data", "width": 200},

#         {"label": "Weight for Age (Z-score)", "fieldname": "weight_for_age_zscore", "fieldtype": "Data", "width": 200},
#         {"label": "Weight for Height (Z-score)", "fieldname": "weight_for_height_zscore", "fieldtype": "Data", "width": 210},
#         {"label": "Height for Age (Z-score)", "fieldname": "height_for_age_zscore", "fieldtype": "Data", "width": 200},

#         {"label": "Growth Faltering 1", "fieldname": "growth_faltering_1", "fieldtype": "Data", "width": 160, "align": "center"},
#         {"label": "Growth Faltering 1+", "fieldname": "growth_faltering_1_plus", "fieldtype": "Data", "width": 170, "align": "center"},
#         {"label": "Growth Faltering 2", "fieldname": "growth_faltering_2", "fieldtype": "Data", "width": 160, "align": "center"},
#         {"label": "Growth Faltering ZigZag", "fieldname": "growth_faltering_zigzag", "fieldtype": "Data", "width": 190, "align": "center"},
#         {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 100, "align": "center"},

#         {"label": "Medical Complication ", "fieldname": "any_medical_major_illness", "fieldtype": "Data", "width": 170, "align": "center"},
#         {"label": "Red Flag", "fieldname": "red_flag", "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": "Home Visit", "fieldname": "red_flag_HV", "fieldtype": "Data", "width": 100, "align": "center"},
#         {"label": "Followup", "fieldname": "follow_up", "fieldtype": "Data", "width": 120},
#         {"label": "Taken to VHND", "fieldname": "vhsnd", "fieldtype": "Data", "width": 140},
#         {"label": "Taken to PHC", "fieldname": "phc", "fieldtype": "Data", "width": 120},
#         {"label": "Taken to CHC", "fieldname": "chc", "fieldtype": "Data", "width": 120},
#         {"label": "Taken to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 120},
#         {"label": "Taken to other Health Facility", "fieldname": "othr", "fieldtype": "Data", "width": 250}
#     ]
    
#     return columns

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     # Date range setup
#     current_date = date.today()
#     month = int(filters.get("month", current_date.month))
#     year = int(filters.get("year", current_date.year))
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     # Calculate previous months for growth faltering comparison
#     if month == 1:
#         lmonth = 12
#         plmonth = 11
#         lyear = year - 1
#         pyear = year - 1
#     elif month == 2:
#         lmonth = 1
#         plmonth = 12
#         lyear = year
#         pyear = year - 1
#     else:
#         lmonth = month - 1
#         plmonth = month - 2
#         lyear = year
#         pyear = year

#     # Month 3 months ago (for GF ZigZag)
#     if plmonth == 1:
#         l3month = 12
#         l3year = pyear - 1
#     else:
#         l3month = plmonth - 1
#         l3year = pyear

#     # Month 4 months ago (for GF ZigZag)
#     if l3month == 1:
#         l4month = 12
#         l4year = l3year - 1
#     else:
#         l4month = l3month - 1
#         l4year = l3year

#     # Initialize parameters
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "lyear": lyear,
#         "lmonth": lmonth,
#         "plmonth": plmonth,
#         "pyear": pyear,
#         "l3month": l3month,
#         "l3year": l3year,
#         "l4month": l4month,
#         "l4year": l4year,
#         "cstart_date": None,
#         "cend_date": None,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#         "supervisor_id": None,
#         "creche_status_id": None,
#         "phases": None
#     }

#     # Get user's partner and geography mapping
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Get user's geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
#     # Handle creche opening date filters
#     range_type = filters.get("cr_opening_range_type")
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             params['cstart_date'], params['cend_date'] = date_range
#         elif range_type == "before" and single_date:
#             params['cstart_date'] = date(2017, 1, 1)
#             params['cend_date'] = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             params['cstart_date'] = single_date + timedelta(days=1)
#             params['cend_date'] = date.today()
#         elif range_type == "equal" and single_date:
#             params['cstart_date'] = single_date

#     # Apply filters
#     if partner_id:
#         params["partner"] = partner_id
    
#     # Geography filters
#     if filters.get("state"):
#         params["state"] = filters.get("state")
#     else:
#         state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#         if state_ids:
#             params["state_ids"] = ",".join(state_ids)

#     if filters.get("district"):
#         params["district"] = filters.get("district")
#     else:
#         district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#         if district_ids:
#             params["district_ids"] = ",".join(district_ids)

#     if filters.get("block"):
#         params["block"] = filters.get("block")
#     else:
#         block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#         if block_ids:
#             params["block_ids"] = ",".join(block_ids)

#     if filters.get("gp"):
#         params["gp"] = filters.get("gp")
#     else:
#         gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
#         if gp_ids:
#             params["gp_ids"] = ",".join(gp_ids)

#     # Other filters
#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             params["phases"] = phases_cleaned

#     # Build conditions for geography filters
#     conditions = []
    
#     if params.get("partner"):
#         conditions.append("cr.partner_id = %(partner)s")
    
#     if params.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")

#     if params.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")

#     if params.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")

#     if params.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")

#     if params.get("creche"):
#         conditions.append("cr.name = %(creche)s")
    
#     if params.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
    
#     if params.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
    
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")

#     # Handle creche opening date conditions
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):
#         conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     sql_query = f"""
#         SELECT DISTINCT
#             cr.creche_name AS 'creche_name',
#             usr.full_name AS 'supervisor',
#             cee.child_id AS 'child_id',
#             cr.creche_id AS 'creche_id',
#             cee.child_name AS 'child_name',
#             cee.age_at_enrollment_in_months AS 'age',
#             DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS 'child_dob',
#             CASE 
#                 WHEN DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m')
#                 THEN TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE())
#                 ELSE TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s)
#             END AS current_age,

#             (CASE 
#                 WHEN cee.gender_id = '1' THEN 'M' 
#                 WHEN cee.gender_id = '2' THEN 'F' 
#                 ELSE cee.gender_id 
#             END) AS gender,
#             ad.height AS 'height',
#             ad.weight AS 'weight',
#             ad.do_you_have_height_weight AS 'measurements_taken_raw',
#             IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS 'measurements_taken',
#             IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS 'measurements_taken_date',
            
#             CASE 
#                 WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
#                 WHEN ad.measurement_reason = 2 THEN 'Child not in village'
#                 WHEN ad.measurement_reason = 3 THEN 'Child is sick'
#                 WHEN ad.measurement_reason = 4 THEN 'Others'
#                 ELSE ''
#             END AS 'measurement_reason',

#             -- ================================================================
#             -- GF1: Any drop in WAZ from previous month
#             -- Logic: current WAZ < last month WAZ
#             -- ================================================================
#             CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
#                 CASE WHEN ad.childenrollguid IN (
#                         SELECT 
#                             ad_current.childenrollguid 
#                         FROM 
#                             `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN 
#                             `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_lyear ON 
#                                 ad_lyear.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_lyear.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
#                                 MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
#                                 ad_lyear.weight_for_age_zscore IS NOT NULL AND
#                                 ad_lyear.weight_for_age_zscore != ''
#                         WHERE 
#                             ad_current.do_you_have_height_weight = 1 AND 
#                             YEAR(cgm.measurement_date) = %(year)s AND 
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < 
#                             CAST(ad_lyear.weight_for_age_zscore AS DECIMAL(10,4))
#                     ) THEN 'Y'
#                     ELSE 'N' 
#                 END 
#             END AS 'growth_faltering_1',

#             -- ================================================================
#             -- GF1+: WAZ drop >= 0.5 from BEST of last 2 months
#             -- Logic: current WAZ <= MAX(waz_m1, waz_m2) - 0.5
#             -- ================================================================
#             CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
#                 CASE WHEN ad.childenrollguid IN (
#                         SELECT 
#                             ad_current.childenrollguid 
#                         FROM 
#                             `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN 
#                             `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         LEFT JOIN
#                             `tabAnthropromatic Data` AS ad_m1 ON 
#                                 ad_m1.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_m1.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_m1.measurement_taken_date) = %(lyear)s AND 
#                                 MONTH(ad_m1.measurement_taken_date) = %(lmonth)s AND
#                                 ad_m1.weight_for_age_zscore IS NOT NULL AND
#                                 ad_m1.weight_for_age_zscore != ''
#                         LEFT JOIN
#                             `tabAnthropromatic Data` AS ad_m2 ON 
#                                 ad_m2.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_m2.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_m2.measurement_taken_date) = %(pyear)s AND 
#                                 MONTH(ad_m2.measurement_taken_date) = %(plmonth)s AND
#                                 ad_m2.weight_for_age_zscore IS NOT NULL AND
#                                 ad_m2.weight_for_age_zscore != ''
#                         WHERE 
#                             ad_current.do_you_have_height_weight = 1 AND 
#                             YEAR(cgm.measurement_date) = %(year)s AND 
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             (ad_m1.weight_for_age_zscore IS NOT NULL OR ad_m2.weight_for_age_zscore IS NOT NULL) AND
#                             CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                                 GREATEST(
#                                     COALESCE(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), -999),
#                                     COALESCE(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), -999)
#                                 ) - 0.5
#                     ) THEN 'Y'
#                     ELSE 'N' 
#                 END 
#             END AS 'growth_faltering_1_plus',

#             -- ================================================================
#             -- GF2: WAZ drop >= 0.5 compared to 2 months ago
#             -- Logic: current WAZ <= waz_2_months_ago - 0.5
#             -- ================================================================
#             CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
#                 CASE WHEN ad.childenrollguid IN (
#                         SELECT 
#                             ad_current.childenrollguid 
#                         FROM 
#                             `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN 
#                             `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_pyear ON 
#                                 ad_pyear.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_pyear.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
#                                 MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
#                                 ad_pyear.weight_for_age_zscore IS NOT NULL AND
#                                 ad_pyear.weight_for_age_zscore != ''
#                         WHERE 
#                             ad_current.do_you_have_height_weight = 1 AND
#                             YEAR(cgm.measurement_date) = %(year)s AND
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                             CAST(ad_pyear.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#                     ) THEN 'Y'
#                     ELSE 'N'
#                 END 
#             END AS 'growth_faltering_2',

#             -- ================================================================
#             -- GF ZigZag: Mixed gain+loss in last 4 months AND drop >= 0.5 from peak
#             -- Requires all 4 prior months to have valid WAZ data
#             -- ================================================================
#             CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
#                 CASE WHEN ad.childenrollguid IN (
#                         SELECT 
#                             ad_current.childenrollguid 
#                         FROM 
#                             `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN 
#                             `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_zz1 ON 
#                                 ad_zz1.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_zz1.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_zz1.measurement_taken_date) = %(lyear)s AND 
#                                 MONTH(ad_zz1.measurement_taken_date) = %(lmonth)s AND
#                                 ad_zz1.weight_for_age_zscore IS NOT NULL AND
#                                 ad_zz1.weight_for_age_zscore != ''
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_zz2 ON 
#                                 ad_zz2.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_zz2.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_zz2.measurement_taken_date) = %(pyear)s AND 
#                                 MONTH(ad_zz2.measurement_taken_date) = %(plmonth)s AND
#                                 ad_zz2.weight_for_age_zscore IS NOT NULL AND
#                                 ad_zz2.weight_for_age_zscore != ''
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_zz3 ON 
#                                 ad_zz3.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_zz3.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_zz3.measurement_taken_date) = %(l3year)s AND 
#                                 MONTH(ad_zz3.measurement_taken_date) = %(l3month)s AND
#                                 ad_zz3.weight_for_age_zscore IS NOT NULL AND
#                                 ad_zz3.weight_for_age_zscore != ''
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_zz4 ON 
#                                 ad_zz4.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_zz4.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_zz4.measurement_taken_date) = %(l4year)s AND 
#                                 MONTH(ad_zz4.measurement_taken_date) = %(l4month)s AND
#                                 ad_zz4.weight_for_age_zscore IS NOT NULL AND
#                                 ad_zz4.weight_for_age_zscore != ''
#                         WHERE 
#                             ad_current.do_you_have_height_weight = 1 AND
#                             YEAR(cgm.measurement_date) = %(year)s AND
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             GREATEST(
#                                 CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)),
#                                 CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)),
#                                 CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)),
#                                 CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                             ) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5 AND
#                             (
#                                 CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                             ) AND
#                             (
#                                 CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                             )
#                     ) THEN 'Y'
#                     ELSE 'N'
#                 END
#             END AS 'growth_faltering_zigzag',

#             -- ================================================================
#             -- SNC: Severe Nutritional Concern
#             -- = GF1+ OR GF2 OR GF ZigZag OR SAM (WFH=1) OR SUW (WAZ<=-3)
#             -- ================================================================
#             CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
#                 CASE WHEN 
#                     -- SAM: Severe Acute Malnutrition
#                     ad.weight_for_height = 1
#                     OR
#                     -- SUW: Severely Underweight (WAZ <= -3)
#                     (ad.weight_for_age_zscore IS NOT NULL AND ad.weight_for_age_zscore != '' AND
#                      CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= -3)
#                     OR
#                     -- GF1+
#                     ad.childenrollguid IN (
#                         SELECT ad_current.childenrollguid 
#                         FROM `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         LEFT JOIN `tabAnthropromatic Data` AS ad_m1 ON 
#                             ad_m1.childenrollguid = ad_current.childenrollguid AND 
#                             ad_m1.do_you_have_height_weight = 1 AND
#                             YEAR(ad_m1.measurement_taken_date) = %(lyear)s AND 
#                             MONTH(ad_m1.measurement_taken_date) = %(lmonth)s AND
#                             ad_m1.weight_for_age_zscore IS NOT NULL AND
#                             ad_m1.weight_for_age_zscore != ''
#                         LEFT JOIN `tabAnthropromatic Data` AS ad_m2 ON 
#                             ad_m2.childenrollguid = ad_current.childenrollguid AND 
#                             ad_m2.do_you_have_height_weight = 1 AND
#                             YEAR(ad_m2.measurement_taken_date) = %(pyear)s AND 
#                             MONTH(ad_m2.measurement_taken_date) = %(plmonth)s AND
#                             ad_m2.weight_for_age_zscore IS NOT NULL AND
#                             ad_m2.weight_for_age_zscore != ''
#                         WHERE ad_current.do_you_have_height_weight = 1 AND 
#                             YEAR(cgm.measurement_date) = %(year)s AND 
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             (ad_m1.weight_for_age_zscore IS NOT NULL OR ad_m2.weight_for_age_zscore IS NOT NULL) AND
#                             CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                                 GREATEST(
#                                     COALESCE(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), -999),
#                                     COALESCE(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), -999)
#                                 ) - 0.5
#                     )
#                     OR
#                     -- GF2
#                     ad.childenrollguid IN (
#                         SELECT ad_current.childenrollguid 
#                         FROM `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         INNER JOIN `tabAnthropromatic Data` AS ad_pyear ON 
#                             ad_pyear.childenrollguid = ad_current.childenrollguid AND 
#                             ad_pyear.do_you_have_height_weight = 1 AND
#                             YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
#                             MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
#                             ad_pyear.weight_for_age_zscore IS NOT NULL AND
#                             ad_pyear.weight_for_age_zscore != ''
#                         WHERE ad_current.do_you_have_height_weight = 1 AND
#                             YEAR(cgm.measurement_date) = %(year)s AND
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                             CAST(ad_pyear.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#                     )
#                     OR
#                     -- GF ZigZag
#                     ad.childenrollguid IN (
#                         SELECT ad_current.childenrollguid 
#                         FROM `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         INNER JOIN `tabAnthropromatic Data` AS ad_zz1 ON 
#                             ad_zz1.childenrollguid = ad_current.childenrollguid AND 
#                             ad_zz1.do_you_have_height_weight = 1 AND
#                             YEAR(ad_zz1.measurement_taken_date) = %(lyear)s AND 
#                             MONTH(ad_zz1.measurement_taken_date) = %(lmonth)s AND
#                             ad_zz1.weight_for_age_zscore IS NOT NULL AND
#                             ad_zz1.weight_for_age_zscore != ''
#                         INNER JOIN `tabAnthropromatic Data` AS ad_zz2 ON 
#                             ad_zz2.childenrollguid = ad_current.childenrollguid AND 
#                             ad_zz2.do_you_have_height_weight = 1 AND
#                             YEAR(ad_zz2.measurement_taken_date) = %(pyear)s AND 
#                             MONTH(ad_zz2.measurement_taken_date) = %(plmonth)s AND
#                             ad_zz2.weight_for_age_zscore IS NOT NULL AND
#                             ad_zz2.weight_for_age_zscore != ''
#                         INNER JOIN `tabAnthropromatic Data` AS ad_zz3 ON 
#                             ad_zz3.childenrollguid = ad_current.childenrollguid AND 
#                             ad_zz3.do_you_have_height_weight = 1 AND
#                             YEAR(ad_zz3.measurement_taken_date) = %(l3year)s AND 
#                             MONTH(ad_zz3.measurement_taken_date) = %(l3month)s AND
#                             ad_zz3.weight_for_age_zscore IS NOT NULL AND
#                             ad_zz3.weight_for_age_zscore != ''
#                         INNER JOIN `tabAnthropromatic Data` AS ad_zz4 ON 
#                             ad_zz4.childenrollguid = ad_current.childenrollguid AND 
#                             ad_zz4.do_you_have_height_weight = 1 AND
#                             YEAR(ad_zz4.measurement_taken_date) = %(l4year)s AND 
#                             MONTH(ad_zz4.measurement_taken_date) = %(l4month)s AND
#                             ad_zz4.weight_for_age_zscore IS NOT NULL AND
#                             ad_zz4.weight_for_age_zscore != ''
#                         WHERE ad_current.do_you_have_height_weight = 1 AND
#                             YEAR(cgm.measurement_date) = %(year)s AND
#                             MONTH(cgm.measurement_date) = %(month)s AND
#                             ad_current.weight_for_age_zscore IS NOT NULL AND
#                             ad_current.weight_for_age_zscore != '' AND
#                             GREATEST(
#                                 CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)),
#                                 CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)),
#                                 CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)),
#                                 CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                             ) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5 AND
#                             (
#                                 CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                             ) AND
#                             (
#                                 CAST(ad_zz1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) OR
#                                 CAST(ad_zz3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz4.weight_for_age_zscore AS DECIMAL(10,4))
#                             )
#                     )
#                 THEN 'Y'
#                 ELSE 'N'
#                 END
#             END AS 'snc',

#             p.partner_name AS partner,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             g.gp_name AS gp,
#             cfud.follow_up AS follow_up,
#             ad.any_medical_major_illness AS any_medical_major_illness,
#             CASE 
#                 WHEN crfd.date_of_referral IS NOT NULL
#                 THEN 'Y' 
#                 ELSE '-' 
#             END AS red_flag_HV,
#             IFNULL(
#                 CASE 
#                     WHEN crfd.referred_to = 5
#                     THEN 'Y' 
#                     ELSE '-' 
#                 END, '-'
#             ) AS othr,
#             CASE 
#                 WHEN crfd.referred_to = 4 
#                 THEN 'Y' 
#                 ELSE '-' 
#             END AS nrc, 
#             CASE 
#                 WHEN crfd.referred_to = 3 
#                 THEN 'Y' 
#                 ELSE '-' 
#             END AS chc, 
#             CASE 
#                 WHEN crfd.referred_to = 2
#                 THEN 'Y' 
#                 ELSE '-' 
#             END AS phc,
#             CASE 
#                 WHEN crfd.referred_to = 1 
#                 THEN 'Y' 
#                 ELSE '-' 
#             END AS vhsnd, 

#             CASE 
#                 WHEN (ad.weight_for_age = 1 
#                     OR ad.weight_for_height = 1
#                     OR ad.any_medical_major_illness = 1
#                     OR ad.childenrollguid IN (
#                         SELECT 
#                             ad_current.childenrollguid 
#                         FROM 
#                             `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN 
#                             `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_lyear ON 
#                                 ad_lyear.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_lyear.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
#                                 MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
#                                 ad_lyear.weight_for_age_zscore IS NOT NULL AND
#                                 ad_lyear.weight_for_age_zscore != ''
#                         INNER JOIN
#                             `tabAnthropromatic Data` AS ad_pyear ON 
#                                 ad_pyear.childenrollguid = ad_current.childenrollguid AND 
#                                 ad_pyear.do_you_have_height_weight = 1 AND
#                                 YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
#                                 MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
#                                 ad_pyear.weight_for_age_zscore IS NOT NULL AND
#                                 ad_pyear.weight_for_age_zscore != ''
#                         WHERE ad_current.do_you_have_height_weight = 1  
#                         AND YEAR(ad_current.measurement_taken_date) = %(year)s
#                         AND MONTH(ad_current.measurement_taken_date) = %(month)s
#                         AND ad_current.weight_for_age_zscore IS NOT NULL
#                         AND ad_current.weight_for_age_zscore != ''
#                         AND CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                             CAST(ad_pyear.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#                     ))
#                 THEN 'Y' 
#                 ELSE 'N' 
#             END AS red_flag,

#             -- Weight for Age
#             CASE 
#                 WHEN ad.weight_for_age = 3 THEN 'Normal'
#                 WHEN ad.weight_for_age = 2 THEN 'Moderate'
#                 WHEN ad.weight_for_age = 1 THEN 'Severe'
#                 ELSE '' 
#             END AS weight_for_age_status,
            
#             -- Height for Age
#             CASE 
#                 WHEN ad.height = 0 THEN '-'
#                 WHEN ad.height_for_age = 3 THEN 'Normal'
#                 WHEN ad.height_for_age = 2 THEN 'Moderate'
#                 WHEN ad.height_for_age = 1 THEN 'Severe'
#                 ELSE '' 
#             END AS height_for_age_status,
            
#             -- Weight for Height
#             CASE 
#                 WHEN ad.height = 0 THEN '-'
#                 WHEN ad.weight_for_height = 3 THEN 'Normal'
#                 WHEN ad.weight_for_height = 2 THEN 'Moderate'
#                 WHEN ad.weight_for_height = 1 THEN 'Severe'
#                 ELSE '' 
#             END AS weight_for_height_status,

#             ad.weight_for_age_zscore AS weight_for_age_zscore,
#             ad.weight_for_height_zscore AS weight_for_height_zscore,
#             ad.height_for_age_zscore AS height_for_age_zscore

#         FROM  
#             `tabAnthropromatic Data` AS ad 
#         INNER JOIN 
#             `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
#         INNER JOIN 
#             `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid 
#         INNER JOIN 
#             `tabCreche` AS cr ON cgm.creche_id = cr.name 
#         INNER JOIN 
#             `tabUser` AS usr ON cr.supervisor_id = usr.name 
#         INNER JOIN 
#             `tabPartner` AS p ON p.name = cr.partner_id
#         INNER JOIN 
#             `tabState` AS s ON s.name = cr.state_id
#         INNER JOIN 
#             `tabDistrict` AS d ON d.name = cr.district_id
#         INNER JOIN 
#             `tabBlock` AS b ON b.name = cr.block_id
#         INNER JOIN 
#             `tabGram Panchayat` AS g ON g.name = cr.gp_id
#         LEFT JOIN (
#             SELECT
#                 crf.childenrolledguid,
#                 crf.date_of_referral,
#                 crf.referred_to
#             FROM
#                 `tabChild Referral` AS crf 
#             WHERE 
#                 YEAR(crf.date_of_referral) = %(year)s
#                 AND MONTH(crf.date_of_referral) = %(month)s
#                 AND (%(partner)s IS NULL OR crf.partner_id = %(partner)s) 
#                 AND (%(state)s IS NULL OR crf.state_id = %(state)s) 
#                 AND (%(district)s IS NULL OR crf.district_id = %(district)s)
#                 AND (%(block)s IS NULL OR crf.block_id = %(block)s)
#                 AND (%(gp)s IS NULL OR crf.gp_id = %(gp)s) 
#                 AND (%(creche)s IS NULL OR crf.creche_id = %(creche)s)
#             ) as crfd ON crfd.childenrolledguid = ad.childenrollguid
#         LEFT JOIN(
#             SELECT
#                 cfu.childenrolledguid,
#                 CASE WHEN cfu.followup_visit_date THEN 'Y' ELSE '-' END AS follow_up 
#             FROM
#                 `tabChild Follow up` AS cfu 
#             WHERE YEAR(cfu.followup_visit_date) = %(year)s
#                 AND MONTH(cfu.followup_visit_date) = %(month)s
#                 AND (%(partner)s IS NULL OR cfu.partner_id = %(partner)s) 
#                 AND (%(state)s IS NULL OR cfu.state_id = %(state)s) 
#                 AND (%(district)s IS NULL OR cfu.district_id = %(district)s)
#                 AND (%(block)s IS NULL OR cfu.block_id = %(block)s)
#                 AND (%(gp)s IS NULL OR cfu.gp_id = %(gp)s) 
#                 AND (%(creche)s IS NULL OR cfu.creche_id = %(creche)s)
#             ) as cfud ON cfud.childenrolledguid = ad.childenrollguid
#         WHERE 
#             YEAR(cgm.measurement_date) = %(year)s
#             AND MONTH(cgm.measurement_date) = %(month)s
#             AND cee.date_of_enrollment <= %(end_date)s
#             AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#             AND {where_clause}
#         ORDER BY
#             cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id, cr.supervisor_id, cr.name, cee.child_name;
#     """
    
#     data = frappe.db.sql(sql_query, params, as_dict=True)

#     for row in data:
#         # Format Weight for Age Z-score
#         if 'weight_for_age_zscore' in row and row['weight_for_age_zscore'] is not None:
#             status = row.get('weight_for_age_status', '').lower()
#             row['weight_for_age_zscore'] = format_zscore_cell(row['weight_for_age_zscore'], status)
        
#         # Format Weight for Height Z-score
#         if 'weight_for_height_zscore' in row and row['weight_for_height_zscore'] is not None:
#             status = row.get('weight_for_height_status', '').lower()
#             row['weight_for_height_zscore'] = format_zscore_cell(row['weight_for_height_zscore'], status)
        
#         # Format Height for Age Z-score
#         if 'height_for_age_zscore' in row and row['height_for_age_zscore'] is not None:
#             status = row.get('height_for_age_status', '').lower()
#             row['height_for_age_zscore'] = format_zscore_cell(row['height_for_age_zscore'], status)

#     # Calculate summary counts
#     counts = {
#         "child_name": 0,
#         "measurements_taken": 0,
#         "growth_faltering_1": 0,
#         "growth_faltering_1_plus": 0,
#         "growth_faltering_2": 0,
#         "growth_faltering_zigzag": 0,
#         "snc": 0,
#         "nrc": 0,
#         "chc": 0,
#         "vhsnd": 0,
#         "follow_up": 0,
#         "red_flag": 0,
#         "red_flag_HV": 0,
#         "phc": 0,
#         "any_medical_major_illness": 0,
#         "othr": 0
#     }

#     for row in data:
#         # Initialize all expected keys with default values if they don't exist
#         row.setdefault("othr", "-")
#         row.setdefault("nrc", "-")
#         row.setdefault("chc", "-")
#         row.setdefault("vhsnd", "-")
#         row.setdefault("follow_up", "-")
#         row.setdefault("red_flag", "-")
#         row.setdefault("red_flag_HV", "-")
#         row.setdefault("phc", "-")
#         row.setdefault("any_medical_major_illness", 0)

#         counts["child_name"] += 1
#         if row.get("measurements_taken_raw") == 1:
#             counts["measurements_taken"] += 1
#         if row.get("growth_faltering_1") == "Y":
#             counts["growth_faltering_1"] += 1
#         if row.get("growth_faltering_1_plus") == "Y":
#             counts["growth_faltering_1_plus"] += 1
#         if row.get("growth_faltering_2") == "Y":
#             counts["growth_faltering_2"] += 1
#         if row.get("growth_faltering_zigzag") == "Y":
#             counts["growth_faltering_zigzag"] += 1
#         if row.get("snc") == "Y":
#             counts["snc"] += 1
#         if row.get("nrc") == "Y":
#             counts["nrc"] += 1
#         if row.get("phc") == "Y":
#             counts["phc"] += 1
#         if row.get("red_flag_HV") == "Y":
#             counts["red_flag_HV"] += 1
#         if row.get("othr") == "Y":
#             counts["othr"] += 1
#         if row.get("chc") == "Y":
#             counts["chc"] += 1
#         if row.get("vhsnd") == "Y":
#             counts["vhsnd"] += 1
#         if row.get("follow_up") == "Y":
#             counts["follow_up"] += 1
#         if row.get("red_flag") == "Y":
#             counts["red_flag"] += 1
#         if row.get("any_medical_major_illness") == 1:
#             counts["any_medical_major_illness"] += 1

#     # Add summary row
#     summary_row = {
#         "partner": "<b style='color:black;'>Total</b>",
#         "child_name": counts['child_name'],
#         "measurements_taken": counts['measurements_taken'],
#         "growth_faltering_1": counts['growth_faltering_1'],
#         "growth_faltering_1_plus": counts['growth_faltering_1_plus'],
#         "growth_faltering_2": counts['growth_faltering_2'],
#         "growth_faltering_zigzag": counts['growth_faltering_zigzag'],
#         "snc": counts['snc'],
#         "nrc": counts['nrc'],
#         "chc": counts['chc'],
#         "vhsnd": counts['vhsnd'],
#         "follow_up": counts['follow_up'],
#         "phc": counts['phc'],
#         "red_flag_HV": counts['red_flag_HV'],
#         "red_flag": counts['red_flag'],
#         "any_medical_major_illness": counts['any_medical_major_illness'],
#         "othr": counts['othr']
#     }
#     data.append(summary_row)

#     return data


# def format_zscore_cell(value, status):
#     """Format Z-score cell with color based on status"""
#     if status == 'severe':
#         return format_cell(value, "#FFCCCC", "#CC0000")
#     elif status == 'moderate':
#         return format_cell(value, "#FFFFCC", "#999900")
#     elif status == 'normal':
#         return format_cell(value, "#CCFFCC", "#006600")
#     else:
#         return value

# def format_cell(value, bg_color, text_color):
#     """Helper function to format a cell with background and text color"""
#     if value is None:
#         return ""
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 2px 5px;
#         '>
#             {value}
#         </div>
#     """