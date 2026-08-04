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

        # New Growth Faltering Metrics
        {"label": "Growth Faltering 1", "fieldname": "gf1", "fieldtype": "Data", "width": 170},
        {"label": "Growth Faltering 1+", "fieldname": "gf1_plus", "fieldtype": "Data", "width": 170},
        {"label": "Growth Faltering 2", "fieldname": "gf2", "fieldtype": "Data", "width": 150},
        {"label": "Zig-Zag", "fieldname": "zigzag", "fieldtype": "Data", "width": 150},
        {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 150},

        {"label": "Referred to Health Facility", "fieldname": "hf", "fieldtype": "Data", "width": 260},
        {"label": "Referred to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 250},
        {"label": "Referred to VHND", "fieldname": "vhnd", "fieldtype": "Data", "width": 250},
        {"label": "Followup Visits Done", "fieldname": "cfu", "fieldtype": "Data", "width": 250}, 
        
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
    


    if month == 1:
        lmonth = 12
        plmonth = 11
        lyear = year - 1
        pyear = year - 1
    elif month == 2:
        lmonth = 1
        plmonth = 12
        lyear = year
        pyear = year - 1
    else:
        lmonth = month - 1
        plmonth = month - 2
        lyear = year
        pyear = year

    # Additional previous months for Zig-Zag (last 5 months: current + previous 4)
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

    l4month = l3month
    l4year = l3year
    if l3month == 1:
        l4month = 12
        l4year = l3year - 1
    else:
        l4month = l3month - 1
        l4year = l3year


    conditions = ["1=1"]
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
        "l4month": l4month,
        "l4year": l4year,
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
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))

    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

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
        params["cend_date"] = cend_date if cend_date else None  

    level_mapping = {
        "1": ["tf.partner"],
        "2": ["tf.state"],
        "3": ["tf.state", "tf.district"],
        "4": ["tf.state", "tf.district", "tf.block"],
        "5": ["tf.state", "tf.district", "tf.block", "tf.supervisor"],
        "6": ["tf.state", "tf.district", "tf.block", "tf.gp"],
        "7": ["tf.state", "tf.district", "tf.block", "tf.gp", "tf.supervisor","tf.creche"],
    }

    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "tf.partner AS partner", 
        "tf.state AS state", 
        "tf.district AS district", 
        "tf.block AS block", 
        "tf.supervisor AS supervisor",
        "tf.gp AS gp",         
        "tf.creche AS creche"
    ]
    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)

    # Optimized query using CTEs to materialize subqueries and reduce repeated computations/joins
    query = f"""
    WITH 
    -- CTE for enrolled children (ec)
    ec AS (
        SELECT 
            cee.creche_id, 
            COUNT(*) AS e_children
        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
        WHERE cee.date_of_enrollment <= %(end_date)s 
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(start_date)s)
        GROUP BY cee.creche_id
    ),
    
    -- CTE for growth measured children (gc)
    gc AS (
        SELECT 
            cgm.creche_id, 
            COUNT(*) AS g_children
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
    
    -- CTE for growth faltering 1 (gf1) - current WAZ > previous month WAZ (exact match with raw query)
    gf1c AS (
        SELECT 
            cgm.creche_id, 
            COUNT(*) AS gf1
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabAnthropromatic Data` ad_lyear ON 
            ad_lyear.childenrollguid = ad.childenrollguid 
            AND ad_lyear.do_you_have_height_weight = 1
            AND (
                (
                    -- Priority: Use previous month if available
                    YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
                    AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
                    AND ad_lyear.weight_for_age_zscore IS NOT NULL
                )
                OR (
                    -- Fallback: Use two months ago if previous month data is missing
                    YEAR(ad_lyear.measurement_taken_date) = %(pyear)s 
                    AND MONTH(ad_lyear.measurement_taken_date) = %(plmonth)s 
                    AND ad_lyear.weight_for_age_zscore IS NOT NULL
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
            -- GF1: Current > Previous (weight_for_age_zscore > previous)
            AND ad.weight_for_age_zscore > ad_lyear.weight_for_age_zscore
            AND ad.weight_for_age_zscore IS NOT NULL 
            AND ad_lyear.weight_for_age_zscore IS NOT NULL
        WHERE ad.do_you_have_height_weight = 1 
          AND YEAR(cgm.measurement_date) = %(year)s 
          AND MONTH(cgm.measurement_date) = %(month)s
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for growth faltering 1+ (gf1_plus) - significant WAZ drop (>=0.5) from previous month
    gf1pc AS (
        SELECT 
            cgm.creche_id, 
            COUNT(*) AS gf1_plus
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabAnthropromatic Data` ad_lyear ON 
            ad_lyear.childenrollguid = ad.childenrollguid 
            AND ad_lyear.do_you_have_height_weight = 1
            AND (
                (
                    -- Priority: Use previous month if available
                    YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
                    AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
                    AND ad_lyear.weight_for_age_zscore IS NOT NULL
                )
                OR (
                    -- Fallback: Use two months ago if previous month data is missing
                    YEAR(ad_lyear.measurement_taken_date) = %(pyear)s 
                    AND MONTH(ad_lyear.measurement_taken_date) = %(plmonth)s 
                    AND ad_lyear.weight_for_age_zscore IS NOT NULL
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
            -- GF1+ Drop Check (Previous - Current >= 0.5)
            AND (ad_lyear.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
            AND ad.weight_for_age_zscore IS NOT NULL 
            AND ad_lyear.weight_for_age_zscore IS NOT NULL
        WHERE ad.do_you_have_height_weight = 1 
          AND YEAR(cgm.measurement_date) = %(year)s 
          AND MONTH(cgm.measurement_date) = %(month)s
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
        GROUP BY cgm.creche_id
    ),
    
    gf2c AS (
        SELECT 
            cgm.creche_id, 
            COUNT(*) AS gf2
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabAnthropromatic Data` ad_2month ON 
            ad_2month.childenrollguid = ad.childenrollguid 
            AND ad_2month.do_you_have_height_weight = 1
            AND (
                (
                    -- Priority: Use 2 months ago (plmonth/pyear) if available
                    YEAR(ad_2month.measurement_taken_date) = %(pyear)s 
                    AND MONTH(ad_2month.measurement_taken_date) = %(plmonth)s 
                    AND ad_2month.weight_for_age_zscore IS NOT NULL
                )
                OR (
                    -- Fallback: Use 3 months ago (l2month/l2year) if 2 months ago data is missing
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
            -- GF2 Logic: 2 months ago WAZ - Current WAZ >= 0.5
            AND (ad_2month.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
            AND ad.weight_for_age_zscore IS NOT NULL 
            AND ad_2month.weight_for_age_zscore IS NOT NULL
        WHERE ad.do_you_have_height_weight = 1 
        AND YEAR(cgm.measurement_date) = %(year)s 
        AND MONTH(cgm.measurement_date) = %(month)s
        AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for zig-zag pattern - exact match with raw query
    zigzagc AS (
        SELECT 
            cgm.creche_id, 
            COUNT(*) AS zigzag
        FROM `tabAnthropromatic Data` ad_current
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        
        /* Month -1 (previous month) */
        INNER JOIN `tabAnthropromatic Data` ad_m1 ON 
            ad_m1.childenrollguid = ad_current.childenrollguid
            AND ad_m1.do_you_have_height_weight = 1
            AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s
            AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
            
        /* Month -2 (two months ago) */
        INNER JOIN `tabAnthropromatic Data` ad_m2 ON 
            ad_m2.childenrollguid = ad_current.childenrollguid
            AND ad_m2.do_you_have_height_weight = 1
            AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s
            AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
            
        /* Month -3 */
        INNER JOIN `tabAnthropromatic Data` ad_m3 ON 
            ad_m3.childenrollguid = ad_current.childenrollguid
            AND ad_m3.do_you_have_height_weight = 1
            AND YEAR(ad_m3.measurement_taken_date) = %(l2year)s
            AND MONTH(ad_m3.measurement_taken_date) = %(l2month)s
            
        /* Month -4 */
        INNER JOIN `tabAnthropromatic Data` ad_m4 ON 
            ad_m4.childenrollguid = ad_current.childenrollguid
            AND ad_m4.do_you_have_height_weight = 1
            AND YEAR(ad_m4.measurement_taken_date) = %(l3year)s
            AND MONTH(ad_m4.measurement_taken_date) = %(l3month)s

        WHERE ad_current.do_you_have_height_weight = 1
            AND YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad_current.weight_for_age_zscore IS NOT NULL
            AND ad_m1.weight_for_age_zscore IS NOT NULL
            AND ad_m2.weight_for_age_zscore IS NOT NULL
            AND ad_m3.weight_for_age_zscore IS NOT NULL
            AND ad_m4.weight_for_age_zscore IS NOT NULL
            AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
            
            /* Step 1: Zig-Zag = At least one Gain AND one Loss in last 4 transitions */
            AND (
                (
                    (ad_m1.weight_for_age_zscore > ad_m2.weight_for_age_zscore) OR
                    (ad_m2.weight_for_age_zscore > ad_m3.weight_for_age_zscore) OR
                    (ad_m3.weight_for_age_zscore > ad_m4.weight_for_age_zscore) OR
                    (ad_current.weight_for_age_zscore > ad_m1.weight_for_age_zscore)
                )
                AND
                (
                    (ad_m1.weight_for_age_zscore < ad_m2.weight_for_age_zscore) OR
                    (ad_m2.weight_for_age_zscore < ad_m3.weight_for_age_zscore) OR
                    (ad_m3.weight_for_age_zscore < ad_m4.weight_for_age_zscore) OR
                    (ad_current.weight_for_age_zscore < ad_m1.weight_for_age_zscore)
                )
            )
            
            /* Step 2 & 3: Highest (Month-4 to Month-1 ONLY) to Current drop ≥ 0.5 */
            AND (
                GREATEST(
                    ad_m4.weight_for_age_zscore,  -- Month-4
                    ad_m3.weight_for_age_zscore,  -- Month-3
                    ad_m2.weight_for_age_zscore,  -- Month-2
                    ad_m1.weight_for_age_zscore   -- Month-1
                ) - ad_current.weight_for_age_zscore
            ) >= 0.5
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for SNC (Severe Nutritional Concern) - FIXED with DISTINCT counting
    sncc AS (
        SELECT 
            creche_id, 
            COUNT(DISTINCT childenrollguid) AS snc
        FROM (
            /* GF1 Subquery */
            SELECT 
                cgm.creche_id,
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
            INNER JOIN `tabAnthropromatic Data` ad_lyear 
                ON ad_lyear.childenrollguid = ad.childenrollguid
                AND ad_lyear.do_you_have_height_weight = 1
                AND (
                    (
                        YEAR(ad_lyear.measurement_taken_date) = %(lyear)s
                        AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s
                        AND ad_lyear.weight_for_age_zscore IS NOT NULL
                    )
                    OR (
                        YEAR(ad_lyear.measurement_taken_date) = %(pyear)s
                        AND MONTH(ad_lyear.measurement_taken_date) = %(plmonth)s
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
                AND ad.weight_for_age_zscore > ad_lyear.weight_for_age_zscore
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad.weight_for_age_zscore IS NOT NULL
            
            UNION ALL
            
            /* GF1+ Subquery */
            SELECT 
                cgm.creche_id,
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
            INNER JOIN `tabAnthropromatic Data` ad_jan
                ON ad_jan.childenrollguid = ad.childenrollguid
                AND ad_jan.do_you_have_height_weight = 1
                AND YEAR(ad_jan.measurement_taken_date) = %(lyear)s
                AND MONTH(ad_jan.measurement_taken_date) = %(lmonth)s
                AND ad_jan.weight_for_age_zscore IS NOT NULL
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad.weight_for_age_zscore IS NOT NULL
                AND (ad_jan.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
            
            UNION ALL
            
            /* GF2 Subquery */
            SELECT 
                cgm.creche_id,
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
            INNER JOIN `tabAnthropromatic Data` ad_dec
                ON ad_dec.childenrollguid = ad.childenrollguid
                AND ad_dec.do_you_have_height_weight = 1
                AND YEAR(ad_dec.measurement_taken_date) = %(pyear)s
                AND MONTH(ad_dec.measurement_taken_date) = %(plmonth)s
                AND ad_dec.weight_for_age_zscore IS NOT NULL
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad.weight_for_age_zscore IS NOT NULL
                AND (ad_dec.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
            
            UNION ALL
            
            /* ZigZag Subquery */
            SELECT 
                cgm.creche_id,
                ad_current.childenrollguid
            FROM `tabAnthropromatic Data` ad_current
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
            INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
            INNER JOIN `tabAnthropromatic Data` ad_jan
                ON ad_jan.childenrollguid = ad_current.childenrollguid
                AND ad_jan.do_you_have_height_weight = 1
                AND YEAR(ad_jan.measurement_taken_date) = %(lyear)s
                AND MONTH(ad_jan.measurement_taken_date) = %(lmonth)s
                AND ad_jan.weight_for_age_zscore IS NOT NULL
            INNER JOIN `tabAnthropromatic Data` ad_dec
                ON ad_dec.childenrollguid = ad_current.childenrollguid
                AND ad_dec.do_you_have_height_weight = 1
                AND YEAR(ad_dec.measurement_taken_date) = %(pyear)s
                AND MONTH(ad_dec.measurement_taken_date) = %(plmonth)s
                AND ad_dec.weight_for_age_zscore IS NOT NULL
            INNER JOIN `tabAnthropromatic Data` ad_nov
                ON ad_nov.childenrollguid = ad_current.childenrollguid
                AND ad_nov.do_you_have_height_weight = 1
                AND YEAR(ad_nov.measurement_taken_date) = %(l2year)s
                AND MONTH(ad_nov.measurement_taken_date) = %(l2month)s
                AND ad_nov.weight_for_age_zscore IS NOT NULL
            INNER JOIN `tabAnthropromatic Data` ad_oct
                ON ad_oct.childenrollguid = ad_current.childenrollguid
                AND ad_oct.do_you_have_height_weight = 1
                AND YEAR(ad_oct.measurement_taken_date) = %(l3year)s
                AND MONTH(ad_oct.measurement_taken_date) = %(l3month)s
                AND ad_oct.weight_for_age_zscore IS NOT NULL
            WHERE ad_current.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad_current.weight_for_age_zscore IS NOT NULL
                AND (
                    (ad_current.weight_for_age_zscore > ad_jan.weight_for_age_zscore)
                    OR (ad_jan.weight_for_age_zscore > ad_dec.weight_for_age_zscore)
                    OR (ad_dec.weight_for_age_zscore > ad_nov.weight_for_age_zscore)
                    OR (ad_nov.weight_for_age_zscore > ad_oct.weight_for_age_zscore)
                )
                AND (
                    (ad_current.weight_for_age_zscore < ad_jan.weight_for_age_zscore)
                    OR (ad_jan.weight_for_age_zscore < ad_dec.weight_for_age_zscore)
                    OR (ad_dec.weight_for_age_zscore < ad_nov.weight_for_age_zscore)
                    OR (ad_nov.weight_for_age_zscore < ad_oct.weight_for_age_zscore)
                )
                AND (
                    GREATEST(
                        ad_oct.weight_for_age_zscore,
                        ad_nov.weight_for_age_zscore,
                        ad_dec.weight_for_age_zscore,
                        ad_jan.weight_for_age_zscore
                    ) - ad_current.weight_for_age_zscore
                ) >= 0.5
            
            UNION ALL
            
            /* SAM Subquery (weight_for_height = 1 indicates SAM) */
            SELECT 
                cgm.creche_id,
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad.weight_for_age_zscore IS NOT NULL
                AND ad.weight_for_height = 1
            
            UNION ALL
            
            /* SUW Subquery (weight_for_age = 1 indicates severe underweight) */
            SELECT 
                cgm.creche_id,
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad.weight_for_age_zscore IS NOT NULL
                AND ad.weight_for_age = 1
        ) sub
        GROUP BY creche_id
    ),
    
    -- CTE for measurement not taken reasons (counts per category)
    mnt AS (
        SELECT 
            cgm.creche_id, 
            COUNT(CASE WHEN ad.measurement_reason = 1 THEN 1 END) AS child_not_in_creche,
            COUNT(CASE WHEN ad.measurement_reason = 2 THEN 1 END) AS child_not_in_village,
            COUNT(CASE WHEN ad.measurement_reason = 3 THEN 1 END) AS child_is_sick,
            COUNT(CASE WHEN ad.measurement_reason = 4 THEN 1 END) AS other
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        WHERE YEAR(cgm.measurement_date) = %(year)s 
          AND MONTH(cgm.measurement_date) = %(month)s
          AND ad.do_you_have_height_weight = 0
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for health facility referrals (h)
    h AS (
        SELECT 
            cep.creche_id, 
            COUNT(cr.name) AS hf
        FROM `tabChild Referral` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s 
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND cr.referred_to != 1 
          AND YEAR(cr.date_of_referral) = %(year)s 
          AND MONTH(cr.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
    ),
    
    -- CTE for NRC referrals (nr)
    nr AS (
        SELECT 
            cep.creche_id, 
            COUNT(cr.name) AS nrc
        FROM `tabChild Referral` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s 
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND cr.referred_to = 4 
          AND YEAR(cr.date_of_referral) = %(year)s 
          AND MONTH(cr.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
    ),
    
    -- CTE for VHND referrals (vhn)
    vhn AS (
        SELECT 
            cep.creche_id, 
            COUNT(vh.name) AS vhnd
        FROM `tabChild Referral` vh
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = vh.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s 
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND vh.referred_to = 1 
          AND YEAR(vh.date_of_referral) = %(year)s 
          AND MONTH(vh.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
    ),
    
    -- CTE for follow-up visits (cfu)
    cfu AS (
        SELECT 
            cep.creche_id, 
            COUNT(cr.name) AS cfu
        FROM `tabChild Follow up` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s 
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND YEAR(cr.followup_visit_date) = %(year)s 
          AND MONTH(cr.followup_visit_date) = %(month)s
        GROUP BY cep.creche_id
    ),
    
    -- CTE for growth metrics (gmd)
    gmd AS (
        SELECT 
            cgm.creche_id,
            COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
            COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
            COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,
            COUNT(CASE WHEN ad.height_for_age = 3 THEN 1 END) AS height_for_age_normal,
            COUNT(CASE WHEN ad.height_for_age = 2 THEN 1 END) AS height_for_age_moderate,
            COUNT(CASE WHEN ad.height_for_age = 1 THEN 1 END) AS height_for_age_severe,
            COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
            COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
            COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
        WHERE ad.do_you_have_height_weight = 1 
          AND YEAR(cgm.measurement_date) = %(year)s 
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for GM entered (gme)
    gme AS (
        SELECT 
            cr.name AS creche_id, 
            COUNT(cgm.creche_id) AS gm_entered
        FROM `tabCreche` cr
        LEFT JOIN `tabChild Growth Monitoring` cgm ON cr.name = cgm.creche_id
        WHERE YEAR(cgm.measurement_date) = %(year)s 
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
            p.partner_name AS partner,
            u.full_name AS supervisor,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            v.village_name AS village,
            c.creche_name AS creche,
            c.creche_id AS creche_id,
            DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS cr_open_date,
            COALESCE(ec.e_children, 0) AS e_children,
            COALESCE(gc.g_children, 0) AS g_children,
            COALESCE(h.hf, 0) AS hf,
            COALESCE(nr.nrc, 0) AS nrc,
            COALESCE(vhn.vhnd, 0) AS vhnd,
            COALESCE(gf2c.gf2, 0) AS gf2,
            COALESCE(gf1c.gf1, 0) AS gf1,
            COALESCE(gf1pc.gf1_plus, 0) AS gf1_plus,
            COALESCE(zigzagc.zigzag, 0) AS zigzag,
            COALESCE(sncc.snc, 0) AS snc,
            COALESCE(mnt.child_not_in_creche, 0) AS child_not_in_creche,
            COALESCE(mnt.child_not_in_village, 0) AS child_not_in_village,
            COALESCE(mnt.child_is_sick, 0) AS child_is_sick,
            COALESCE(mnt.other, 0) AS other,
            COALESCE(cfu.cfu, 0) AS cfu,
            COALESCE(gmd.weight_for_age_normal, 0) AS weight_for_age_normal,
            COALESCE(gmd.weight_for_age_moderate, 0) AS weight_for_age_moderate,
            COALESCE(gmd.weight_for_age_severe, 0) AS weight_for_age_severe,
            COALESCE(gmd.height_for_age_normal, 0) AS height_for_age_normal,
            COALESCE(gmd.height_for_age_moderate, 0) AS height_for_age_moderate,
            COALESCE(gmd.height_for_age_severe, 0) AS height_for_age_severe,
            COALESCE(gmd.weight_for_height_normal, 0) AS weight_for_height_normal,
            COALESCE(gmd.weight_for_height_moderate, 0) AS weight_for_height_moderate,
            COALESCE(gmd.weight_for_height_severe, 0) AS weight_for_height_severe,
            COALESCE(gme.gm_entered, 0) AS gm_entered
            
        FROM `tabCreche` c 
        LEFT JOIN ec ON c.name = ec.creche_id
        LEFT JOIN gc ON c.name = gc.creche_id
        LEFT JOIN gf2c ON c.name = gf2c.creche_id
        LEFT JOIN gf1c ON c.name = gf1c.creche_id
        LEFT JOIN gf1pc ON c.name = gf1pc.creche_id
        LEFT JOIN zigzagc ON c.name = zigzagc.creche_id
        LEFT JOIN sncc ON c.name = sncc.creche_id
        LEFT JOIN h ON c.name = h.creche_id
        LEFT JOIN nr ON c.name = nr.creche_id
        LEFT JOIN vhn ON c.name = vhn.creche_id
        LEFT JOIN cfu ON c.name = cfu.creche_id
        LEFT JOIN gmd ON c.name = gmd.creche_id
        LEFT JOIN gme ON c.name = gme.creche_id
        LEFT JOIN mnt ON c.name = mnt.creche_id
        
        INNER JOIN `tabState` s ON c.state_id = s.name 
        INNER JOIN `tabDistrict` d ON c.district_id = d.name
        INNER JOIN `tabBlock` b ON c.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        INNER JOIN `tabVillage` v ON c.village_id = v.name
        INNER JOIN `tabPartner` p ON c.partner_id = p.name 
        INNER JOIN `tabUser` u ON u.name = c.supervisor_id
        WHERE {where_clause}
    ) AS tf
    
    GROUP BY {group_by_field}
    ORDER BY {group_by_field}
    """

    data = frappe.db.sql(query, params, as_dict=True)
    
    total_act_creches = sum(int(row.get('op_creches', 0) or 0) for row in data)
    total_gm_entered = sum(int(row.get('gm_entered', 0) or 0) for row in data)
    total_e_children = sum(int(row.get('e_children', 0) or 0) for row in data)
    total_g_children = sum(int(row.get('g_children', 0) or 0) for row in data)
    total_hf = sum(int(row.get('hf', 0) or 0) for row in data)
    total_nrc = sum(int(row.get('nrc', 0) or 0) for row in data)
    total_cfu = sum(int(row.get('cfu', 0) or 0) for row in data)
    total_vhnd = sum(int(row.get('vhnd', 0) or 0) for row in data)

    total_gf1 = sum(int(row.get('gf1', 0) or 0) for row in data)
    total_gf1_plus = sum(int(row.get('gf1_plus', 0) or 0) for row in data)
    total_gf2 = sum(int(row.get('gf2', 0) or 0) for row in data)
    total_zigzag = sum(int(row.get('zigzag', 0) or 0) for row in data)
    total_snc = sum(int(row.get('snc', 0) or 0) for row in data)
    
    total_child_not_in_creche = sum(int(row.get('child_not_in_creche', 0) or 0) for row in data)
    total_child_not_in_village = sum(int(row.get('child_not_in_village', 0) or 0) for row in data)
    total_child_is_sick = sum(int(row.get('child_is_sick', 0) or 0) for row in data)
    total_other = sum(int(row.get('other', 0) or 0) for row in data)
    
    total_weight_for_age_normal = sum(int(row.get('weight_for_age_normal', 0) or 0) for row in data)
    total_weight_for_age_moderate = sum(int(row.get('weight_for_age_moderate', 0) or 0) for row in data)
    total_weight_for_age_severe = sum(int(row.get('weight_for_age_severe', 0) or 0) for row in data)
    
    total_height_for_age_normal = sum(int(row.get('height_for_age_normal', 0) or 0) for row in data)
    total_height_for_age_moderate = sum(int(row.get('height_for_age_moderate', 0) or 0) for row in data)
    total_height_for_age_severe = sum(int(row.get('height_for_age_severe', 0) or 0) for row in data)
    
    total_weight_for_height_normal = sum(int(row.get('weight_for_height_normal', 0) or 0) for row in data)
    total_weight_for_height_moderate = sum(int(row.get('weight_for_height_moderate', 0) or 0) for row in data)
    total_weight_for_height_severe = sum(int(row.get('weight_for_height_severe', 0) or 0) for row in data)

    total_mea_percentage = round((total_g_children * 100.0 / total_e_children), 2) if total_e_children else 0

    total_wfan_per = round((total_weight_for_age_normal * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfam_per = round((total_weight_for_age_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfas_per = round((total_weight_for_age_severe * 100.0 / total_g_children), 2) if total_g_children else 0

    total_hfan_per = round((total_height_for_age_normal * 100.0 / total_g_children), 2) if total_g_children else 0
    total_hfam_per = round((total_height_for_age_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
    total_hfas_per = round((total_height_for_age_severe * 100.0 / total_g_children), 2) if total_g_children else 0

    total_wfhn_per = round((total_weight_for_height_normal * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfhm_per = round((total_weight_for_height_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
    total_wfhs_per = round((total_weight_for_height_severe * 100.0 / total_g_children), 2) if total_g_children else 0
    
    total_row = {
  
    "partner": "<b style='color:black;'>Total</b>",
    "state": "<b style='color:black;'>Total</b>",
    "gm_entered": f"<b>{total_gm_entered}</b>",
    "op_creches": f"<b>{total_act_creches}</b>",
    "e_children": f"<b>{total_e_children}</b>",
    "g_children": f"<b>{total_g_children}</b>",
    "e_children_percentage": f"<b>{total_mea_percentage}</b>",

    "child_not_in_creche": f"<b>{total_child_not_in_creche}</b>",
    "child_not_in_village": f"<b>{total_child_not_in_village}</b>",
    "child_is_sick": f"<b>{total_child_is_sick}</b>",
    "other": f"<b>{total_other}</b>",

    "hf": f"<b>{total_hf}</b>",
    "nrc": f"<b>{total_nrc}</b>",
    "cfu": f"<b>{total_cfu}</b>",    
    "vhnd": f"<b>{total_vhnd}</b>",

    "gf1": f"<b>{total_gf1}</b>",
    "gf1_plus": f"<b>{total_gf1_plus}</b>",
    "gf2": f"<b>{total_gf2}</b>",
    "zigzag": f"<b>{total_zigzag}</b>",
    "snc": f"<b>{total_snc}</b>",
   
    "weight_for_age_normal": f"<b>{total_weight_for_age_normal}</b>",
    "weight_for_age_moderate": f"<b>{total_weight_for_age_moderate}</b>",
    "weight_for_age_severe": f"<b>{total_weight_for_age_severe}</b>",
    
    "per_weight_for_age_normal": f"<b>{total_wfan_per}</b>",
    "per_weight_for_age_moderate": f"<b>{total_wfam_per}</b>",
    "per_weight_for_age_severe": f"<b>{total_wfas_per}</b>",
    
    "height_for_age_normal": f"<b>{total_height_for_age_normal}</b>",
    "height_for_age_moderate": f"<b>{total_height_for_age_moderate}</b>",
    "height_for_age_severe": f"<b>{total_height_for_age_severe}</b>", 
    
    "per_height_for_age_normal": f"<b>{total_hfan_per}</b>",
    "per_height_for_age_moderate": f"<b>{total_hfam_per}</b>",
    "per_height_for_age_severe": f"<b>{total_hfas_per}</b>",  
    
    "weight_for_height_normal": f"<b>{total_weight_for_height_normal}</b>",
    "weight_for_height_moderate": f"<b>{total_weight_for_height_moderate}</b>",
    "weight_for_height_severe": f"<b>{total_weight_for_height_severe}</b>",

    "per_weight_for_height_normal": f"<b>{total_wfhn_per}</b>",
    "per_weight_for_height_moderate": f"<b>{total_wfhm_per}</b>",
    "per_weight_for_height_severe": f"<b>{total_wfhs_per}</b>"
}

    data.append(total_row)
    return data









# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_level = filters.get("level", "7")
#     variable_columns = []

#     if selected_level == "1":
#         variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
#     if selected_level == "2":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#     if selected_level == "3":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#     if selected_level == "4":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#     if selected_level == "5":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#     if selected_level == "6":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#     if selected_level == "7":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 150})
        

#     fixed_columns = [
    
#         {"label": "Active Creches", "fieldname": "op_creches", "fieldtype": "Data", "width": 180},
#         {"label": "GM Submitted", "fieldname": "gm_entered", "fieldtype": "Data", "width": 180},
        
#         {"label": "Enrolled Children", "fieldname": "e_children", "fieldtype": "Data", "width": 150},
#         {"label": "Measurement Taken", "fieldname": "g_children", "fieldtype": "Data", "width": 180},
#         {"label": "Measurement (%)", "fieldname": "e_children_percentage", "fieldtype": "Data", "width": 150},
        
#         {"label": "Child Not In Creche", "fieldname": "child_not_in_creche", "fieldtype": "Data", "width": 180},
#         {"label": "Child Not In Village", "fieldname": "child_not_in_village", "fieldtype": "Data", "width": 180},
#         {"label": "Child is Sick", "fieldname": "child_is_sick", "fieldtype": "Data", "width": 180},
#         {"label": "Other", "fieldname": "other", "fieldtype": "Data", "width": 180},
        
#         {"label": "WFA - Normal", "fieldname": "weight_for_age_normal", "fieldtype": "Data", "width": 130},
#         {"label": "WFA - Normal (%)", "fieldname": "per_weight_for_age_normal", "fieldtype": "Data", "width": 150},
#         {"label": "WFA - Moderate", "fieldname": "weight_for_age_moderate", "fieldtype": "Data", "width": 140},
#         {"label": "WFA - Moderate (%)", "fieldname": "per_weight_for_age_moderate", "fieldtype": "Data", "width": 160},
#         {"label": "WFA - Severe", "fieldname": "weight_for_age_severe", "fieldtype": "Data", "width": 130},
#         {"label": "WFA - Severe (%)", "fieldname": "per_weight_for_age_severe", "fieldtype": "Data", "width": 150},

#         {"label": "WFH - Normal", "fieldname": "weight_for_height_normal", "fieldtype": "Data", "width": 130},
#         {"label": "WFH - Normal (%)", "fieldname": "per_weight_for_height_normal", "fieldtype": "Data", "width": 150},
#         {"label": "WFH - Moderate", "fieldname": "weight_for_height_moderate", "fieldtype": "Data", "width": 140},
#         {"label": "WFH - Moderate (%)", "fieldname": "per_weight_for_height_moderate", "fieldtype": "Data", "width": 160},
#         {"label": "WFH - Severe", "fieldname": "weight_for_height_severe", "fieldtype": "Data", "width": 130},
#         {"label": "WFH - Severe (%)", "fieldname": "per_weight_for_height_severe", "fieldtype": "Data", "width": 150},

#         {"label": "HFA - Normal", "fieldname": "height_for_age_normal", "fieldtype": "Data", "width": 130},
#         {"label": "HFA - Normal (%)", "fieldname": "per_height_for_age_normal", "fieldtype": "Data", "width": 150},
#         {"label": "HFA - Moderate", "fieldname": "height_for_age_moderate", "fieldtype": "Data", "width": 140},
#         {"label": "HFA - Moderate (%)", "fieldname": "per_height_for_age_moderate", "fieldtype": "Data", "width": 160},
#         {"label": "HFA - Severe", "fieldname": "height_for_age_severe", "fieldtype": "Data", "width": 130},
#         {"label": "HFA - Severe (%)", "fieldname": "per_height_for_age_severe", "fieldtype": "Data", "width": 150},

#         # New Growth Faltering Metrics
#         {"label": "Growth Faltering 1", "fieldname": "gf1", "fieldtype": "Data", "width": 170},
#         {"label": "Growth Faltering 1+", "fieldname": "gf1_plus", "fieldtype": "Data", "width": 170},
#         {"label": "Growth Faltering 2", "fieldname": "gf2", "fieldtype": "Data", "width": 150},
#         {"label": "Zig-Zag", "fieldname": "zigzag", "fieldtype": "Data", "width": 150},
#         {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 150},

#         {"label": "Referred to Health Facility", "fieldname": "hf", "fieldtype": "Data", "width": 260},
#         {"label": "Referred to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 250},
#         {"label": "Referred to VHND", "fieldname": "vhnd", "fieldtype": "Data", "width": 250},
#         {"label": "Followup Visits Done", "fieldname": "cfu", "fieldtype": "Data", "width": 250}, 
        
#     ]

#     columns = variable_columns + fixed_columns
#     data = get_report_data(filters)
#     return columns, data

# def get_report_data(filters):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    


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

#     # Additional previous months for Zig-Zag (last 5 months: current + previous 4)
#     l2month = plmonth
#     l2year = pyear
#     if plmonth == 1:
#         l2month = 12
#         l2year = pyear - 1
#     else:
#         l2month = plmonth - 1
#         l2year = pyear

#     l3month = l2month
#     l3year = l2year
#     if l2month == 1:
#         l3month = 12
#         l3year = l2year - 1
#     else:
#         l3month = l2month - 1
#         l3year = l2year

#     l4month = l3month
#     l4year = l3year
#     if l3month == 1:
#         l4month = 12
#         l4year = l3year - 1
#     else:
#         l4month = l3month - 1
#         l4year = l3year


#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "lyear": lyear,
#         "lmonth": lmonth,
#         "plmonth": plmonth,
#         "pyear": pyear,
#         "l2month": l2month,
#         "l2year": l2year,
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
#     }


#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """

#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))

#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range

#         elif range_type == "before" and single_date:
#             cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)

#         elif range_type == "after" and single_date:
#             cstart_date, cend_date = single_date + timedelta(days=1), date.today()

#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date

#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id
#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None
#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"):
#         conditions.append("(c.creche_status_id = %(creche_status_id)s)")
#         params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#             params["phases"] = phases_cleaned    
#     if cstart_date or cend_date:
#         conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
#         params["cstart_date"] = cstart_date if cstart_date else None  
#         params["cend_date"] = cend_date if cend_date else None  

#     level_mapping = {
#         "1": ["tf.partner"],
#         "2": ["tf.state"],
#         "3": ["tf.state", "tf.district"],
#         "4": ["tf.state", "tf.district", "tf.block"],
#         "5": ["tf.state", "tf.district", "tf.block", "tf.supervisor"],
#         "6": ["tf.state", "tf.district", "tf.block", "tf.gp"],
#         "7": ["tf.state", "tf.district", "tf.block", "tf.gp", "tf.supervisor","tf.creche"],
#     }

#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)

#     select_fields = [
#         "tf.partner AS partner", 
#         "tf.state AS state", 
#         "tf.district AS district", 
#         "tf.block AS block", 
#         "tf.supervisor AS supervisor",
#         "tf.gp AS gp",         
#         "tf.creche AS creche"
#     ]
#     selected_fields = []
#     for field in select_fields:
#         if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
#             selected_fields.append(field)

#     where_clause = " AND ".join(conditions)

#     # Optimized query using CTEs to materialize subqueries and reduce repeated computations/joins
#     query = f"""
#     WITH 
#     -- CTE for enrolled children (ec)
#     ec AS (
#         SELECT 
#             cee.creche_id, 
#             COUNT(*) AS e_children
#         FROM `tabChild Enrollment and Exit` cee
#         INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
#         WHERE cee.date_of_enrollment <= %(end_date)s 
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(start_date)s)
#         GROUP BY cee.creche_id
#     ),
    
#     -- CTE for growth measured children (gc)
#     gc AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(*) AS g_children
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND cee.date_of_enrollment <= %(end_date)s
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for growth faltering 1 (gf1) - current WAZ > previous month WAZ (exact match with raw query)
#     gf1c AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(*) AS gf1
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         INNER JOIN `tabAnthropromatic Data` ad_lyear ON 
#             ad_lyear.childenrollguid = ad.childenrollguid 
#             AND ad_lyear.do_you_have_height_weight = 1
#             AND (
#                 (
#                     -- Priority: Use previous month if available
#                     YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
#                     AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
#                     AND ad_lyear.weight_for_age_zscore IS NOT NULL
#                 )
#                 OR (
#                     -- Fallback: Use two months ago if previous month data is missing
#                     YEAR(ad_lyear.measurement_taken_date) = %(pyear)s 
#                     AND MONTH(ad_lyear.measurement_taken_date) = %(plmonth)s 
#                     AND ad_lyear.weight_for_age_zscore IS NOT NULL
#                     AND NOT EXISTS (
#                         SELECT 1
#                         FROM `tabAnthropromatic Data` jan
#                         WHERE jan.childenrollguid = ad.childenrollguid
#                         AND jan.do_you_have_height_weight = 1
#                         AND YEAR(jan.measurement_taken_date) = %(lyear)s 
#                         AND MONTH(jan.measurement_taken_date) = %(lmonth)s 
#                         AND jan.weight_for_age_zscore IS NOT NULL
#                     )
#                 )
#             )
#             -- GF1: Current > Previous (weight_for_age_zscore > previous)
#             AND ad.weight_for_age_zscore > ad_lyear.weight_for_age_zscore
#             AND ad.weight_for_age_zscore IS NOT NULL 
#             AND ad_lyear.weight_for_age_zscore IS NOT NULL
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for growth faltering 1+ (gf1_plus) - significant WAZ drop (>=0.5) from previous month
#     gf1pc AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(*) AS gf1_plus
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         INNER JOIN `tabAnthropromatic Data` ad_lyear ON 
#             ad_lyear.childenrollguid = ad.childenrollguid 
#             AND ad_lyear.do_you_have_height_weight = 1
#             AND (
#                 (
#                     -- Priority: Use previous month if available
#                     YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
#                     AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
#                     AND ad_lyear.weight_for_age_zscore IS NOT NULL
#                 )
#                 OR (
#                     -- Fallback: Use two months ago if previous month data is missing
#                     YEAR(ad_lyear.measurement_taken_date) = %(pyear)s 
#                     AND MONTH(ad_lyear.measurement_taken_date) = %(plmonth)s 
#                     AND ad_lyear.weight_for_age_zscore IS NOT NULL
#                     AND NOT EXISTS (
#                         SELECT 1
#                         FROM `tabAnthropromatic Data` jan
#                         WHERE jan.childenrollguid = ad.childenrollguid
#                         AND jan.do_you_have_height_weight = 1
#                         AND YEAR(jan.measurement_taken_date) = %(lyear)s 
#                         AND MONTH(jan.measurement_taken_date) = %(lmonth)s 
#                         AND jan.weight_for_age_zscore IS NOT NULL
#                     )
#                 )
#             )
#             -- GF1+ Drop Check (Previous - Current >= 0.5)
#             AND (ad_lyear.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
#             AND ad.weight_for_age_zscore IS NOT NULL 
#             AND ad_lyear.weight_for_age_zscore IS NOT NULL
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for growth faltering 2 (gf2) - children with significant WAZ drop (>=0.5) vs two months ago
#     gf2c AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(*) AS gf2
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         INNER JOIN `tabAnthropromatic Data` ad_pyear ON 
#             ad_pyear.childenrollguid = ad.childenrollguid 
#             AND ad_pyear.do_you_have_height_weight = 1
#             AND (
#                 (
#                     -- Priority: Use previous month if available
#                     YEAR(ad_pyear.measurement_taken_date) = %(lyear)s 
#                     AND MONTH(ad_pyear.measurement_taken_date) = %(lmonth)s 
#                     AND ad_pyear.weight_for_age_zscore IS NOT NULL
#                 )
#                 OR (
#                     -- Fallback: Use two months ago if previous month data is missing
#                     YEAR(ad_pyear.measurement_taken_date) = %(pyear)s 
#                     AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s 
#                     AND ad_pyear.weight_for_age_zscore IS NOT NULL
#                     AND NOT EXISTS (
#                         SELECT 1
#                         FROM `tabAnthropromatic Data` jan
#                         WHERE jan.childenrollguid = ad.childenrollguid
#                         AND jan.do_you_have_height_weight = 1
#                         AND YEAR(jan.measurement_taken_date) = %(lyear)s 
#                         AND MONTH(jan.measurement_taken_date) = %(lmonth)s 
#                         AND jan.weight_for_age_zscore IS NOT NULL
#                     )
#                 )
#             )
#             -- GF2 Logic: Previous - Current >= 0.5 WAZ drop
#             AND (ad_pyear.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
#             AND ad.weight_for_age_zscore IS NOT NULL 
#             AND ad_pyear.weight_for_age_zscore IS NOT NULL
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for zig-zag pattern - exact match with raw query
#     zigzagc AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(*) AS zigzag
#         FROM `tabAnthropromatic Data` ad_current
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        
#         /* Month -1 (previous month) */
#         INNER JOIN `tabAnthropromatic Data` ad_m1 ON 
#             ad_m1.childenrollguid = ad_current.childenrollguid
#             AND ad_m1.do_you_have_height_weight = 1
#             AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s
#             AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
            
#         /* Month -2 (two months ago) */
#         INNER JOIN `tabAnthropromatic Data` ad_m2 ON 
#             ad_m2.childenrollguid = ad_current.childenrollguid
#             AND ad_m2.do_you_have_height_weight = 1
#             AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s
#             AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
            
#         /* Month -3 */
#         INNER JOIN `tabAnthropromatic Data` ad_m3 ON 
#             ad_m3.childenrollguid = ad_current.childenrollguid
#             AND ad_m3.do_you_have_height_weight = 1
#             AND YEAR(ad_m3.measurement_taken_date) = %(l2year)s
#             AND MONTH(ad_m3.measurement_taken_date) = %(l2month)s
            
#         /* Month -4 */
#         INNER JOIN `tabAnthropromatic Data` ad_m4 ON 
#             ad_m4.childenrollguid = ad_current.childenrollguid
#             AND ad_m4.do_you_have_height_weight = 1
#             AND YEAR(ad_m4.measurement_taken_date) = %(l3year)s
#             AND MONTH(ad_m4.measurement_taken_date) = %(l3month)s

#         WHERE ad_current.do_you_have_height_weight = 1
#             AND YEAR(cgm.measurement_date) = %(year)s
#             AND MONTH(cgm.measurement_date) = %(month)s
#             AND ad_current.weight_for_age_zscore IS NOT NULL
#             AND ad_m1.weight_for_age_zscore IS NOT NULL
#             AND ad_m2.weight_for_age_zscore IS NOT NULL
#             AND ad_m3.weight_for_age_zscore IS NOT NULL
#             AND ad_m4.weight_for_age_zscore IS NOT NULL
#             AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
            
#             /* Step 1: Zig-Zag = At least one Gain AND one Loss in last 4 transitions */
#             AND (
#                 (
#                     (ad_m1.weight_for_age_zscore > ad_m2.weight_for_age_zscore) OR
#                     (ad_m2.weight_for_age_zscore > ad_m3.weight_for_age_zscore) OR
#                     (ad_m3.weight_for_age_zscore > ad_m4.weight_for_age_zscore) OR
#                     (ad_current.weight_for_age_zscore > ad_m1.weight_for_age_zscore)
#                 )
#                 AND
#                 (
#                     (ad_m1.weight_for_age_zscore < ad_m2.weight_for_age_zscore) OR
#                     (ad_m2.weight_for_age_zscore < ad_m3.weight_for_age_zscore) OR
#                     (ad_m3.weight_for_age_zscore < ad_m4.weight_for_age_zscore) OR
#                     (ad_current.weight_for_age_zscore < ad_m1.weight_for_age_zscore)
#                 )
#             )
            
#             /* Step 2 & 3: Highest (Month-4 to Month-1 ONLY) to Current drop ≥ 0.5 */
#             AND (
#                 GREATEST(
#                     ad_m4.weight_for_age_zscore,  -- Month-4
#                     ad_m3.weight_for_age_zscore,  -- Month-3
#                     ad_m2.weight_for_age_zscore,  -- Month-2
#                     ad_m1.weight_for_age_zscore   -- Month-1
#                 ) - ad_current.weight_for_age_zscore
#             ) >= 0.5
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for SNC (Severe Nutritional Concern) - exact match with raw query
#     sncc AS (
#         SELECT 
#             creche_id, 
#             COUNT(DISTINCT childenrollguid) AS snc
#         FROM (
#             -- GF1: Any drop from previous month (Current < Previous)
#             SELECT DISTINCT
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#             LEFT JOIN `tabAnthropromatic Data` ad_jan ON 
#                 ad_jan.childenrollguid = ad.childenrollguid
#                 AND ad_jan.do_you_have_height_weight = 1
#                 AND YEAR(ad_jan.measurement_taken_date) = %(lyear)s
#                 AND MONTH(ad_jan.measurement_taken_date) = %(lmonth)s
#                 AND ad_jan.weight_for_age_zscore IS NOT NULL
#             LEFT JOIN `tabAnthropromatic Data` ad_dec ON 
#                 ad_dec.childenrollguid = ad.childenrollguid
#                 AND ad_dec.do_you_have_height_weight = 1
#                 AND YEAR(ad_dec.measurement_taken_date) = %(pyear)s
#                 AND MONTH(ad_dec.measurement_taken_date) = %(plmonth)s
#                 AND ad_dec.weight_for_age_zscore IS NOT NULL
#             WHERE ad.do_you_have_height_weight = 1
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND ad.weight_for_age_zscore IS NOT NULL
#                 AND (
#                     /* Priority: Use Jan if available */
#                     (
#                         ad_jan.weight_for_age_zscore IS NOT NULL
#                         AND ad.weight_for_age_zscore < ad_jan.weight_for_age_zscore
#                     )
#                     OR
#                     /* Fallback: Use Dec if Jan is not available */
#                     (
#                         ad_jan.weight_for_age_zscore IS NULL
#                         AND ad_dec.weight_for_age_zscore IS NOT NULL
#                         AND ad.weight_for_age_zscore < ad_dec.weight_for_age_zscore
#                         AND NOT EXISTS (
#                             SELECT 1
#                             FROM `tabAnthropromatic Data` jan
#                             WHERE jan.childenrollguid = ad.childenrollguid
#                             AND jan.do_you_have_height_weight = 1
#                             AND YEAR(jan.measurement_taken_date) = %(lyear)s
#                             AND MONTH(jan.measurement_taken_date) = %(lmonth)s
#                             AND jan.weight_for_age_zscore IS NOT NULL
#                         )
#                     )
#                 )
            
#             UNION DISTINCT
            
#             -- GF1+: Drop ≥ 0.5 from last month
#             SELECT DISTINCT
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#             INNER JOIN `tabAnthropromatic Data` ad_jan ON 
#                 ad_jan.childenrollguid = ad.childenrollguid
#                 AND ad_jan.do_you_have_height_weight = 1
#                 AND YEAR(ad_jan.measurement_taken_date) = %(lyear)s
#                 AND MONTH(ad_jan.measurement_taken_date) = %(lmonth)s
#                 AND ad_jan.weight_for_age_zscore IS NOT NULL
#             WHERE ad.do_you_have_height_weight = 1
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND ad.weight_for_age_zscore IS NOT NULL
#                 AND (ad_jan.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
            
#             UNION DISTINCT
            
#             -- GF2: Drop ≥ 0.5 from two months ago
#             SELECT DISTINCT
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#             INNER JOIN `tabAnthropromatic Data` ad_dec ON 
#                 ad_dec.childenrollguid = ad.childenrollguid
#                 AND ad_dec.do_you_have_height_weight = 1
#                 AND YEAR(ad_dec.measurement_taken_date) = %(pyear)s
#                 AND MONTH(ad_dec.measurement_taken_date) = %(plmonth)s
#                 AND ad_dec.weight_for_age_zscore IS NOT NULL
#             WHERE ad.do_you_have_height_weight = 1
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND ad.weight_for_age_zscore IS NOT NULL
#                 AND (ad_dec.weight_for_age_zscore - ad.weight_for_age_zscore) >= 0.5
            
#             UNION DISTINCT
            
#             -- Zig-Zag Pattern (5 months)
#             SELECT DISTINCT
#                 cgm.creche_id, 
#                 ad_current.childenrollguid
#             FROM `tabAnthropromatic Data` ad_current
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
#             INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
            
#             /* Month -1 */
#             INNER JOIN `tabAnthropromatic Data` ad_m1 ON 
#                 ad_m1.childenrollguid = ad_current.childenrollguid
#                 AND ad_m1.do_you_have_height_weight = 1
#                 AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s
#                 AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s
                
#             /* Month -2 */
#             INNER JOIN `tabAnthropromatic Data` ad_m2 ON 
#                 ad_m2.childenrollguid = ad_current.childenrollguid
#                 AND ad_m2.do_you_have_height_weight = 1
#                 AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s
#                 AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s
                
#             /* Month -3 */
#             INNER JOIN `tabAnthropromatic Data` ad_m3 ON 
#                 ad_m3.childenrollguid = ad_current.childenrollguid
#                 AND ad_m3.do_you_have_height_weight = 1
#                 AND YEAR(ad_m3.measurement_taken_date) = %(l2year)s
#                 AND MONTH(ad_m3.measurement_taken_date) = %(l2month)s
                
#             /* Month -4 */
#             INNER JOIN `tabAnthropromatic Data` ad_m4 ON 
#                 ad_m4.childenrollguid = ad_current.childenrollguid
#                 AND ad_m4.do_you_have_height_weight = 1
#                 AND YEAR(ad_m4.measurement_taken_date) = %(l3year)s
#                 AND MONTH(ad_m4.measurement_taken_date) = %(l3month)s

#             WHERE ad_current.do_you_have_height_weight = 1
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND ad_current.weight_for_age_zscore IS NOT NULL
#                 AND ad_m1.weight_for_age_zscore IS NOT NULL
#                 AND ad_m2.weight_for_age_zscore IS NOT NULL
#                 AND ad_m3.weight_for_age_zscore IS NOT NULL
#                 AND ad_m4.weight_for_age_zscore IS NOT NULL
                
#                 /* At least one gain in consecutive months */
#                 AND (
#                     (ad_current.weight_for_age_zscore > ad_m1.weight_for_age_zscore) OR
#                     (ad_m1.weight_for_age_zscore > ad_m2.weight_for_age_zscore) OR
#                     (ad_m2.weight_for_age_zscore > ad_m3.weight_for_age_zscore) OR
#                     (ad_m3.weight_for_age_zscore > ad_m4.weight_for_age_zscore)
#                 )
                
#                 /* At least one loss in consecutive months */
#                 AND (
#                     (ad_current.weight_for_age_zscore < ad_m1.weight_for_age_zscore) OR
#                     (ad_m1.weight_for_age_zscore < ad_m2.weight_for_age_zscore) OR
#                     (ad_m2.weight_for_age_zscore < ad_m3.weight_for_age_zscore) OR
#                     (ad_m3.weight_for_age_zscore < ad_m4.weight_for_age_zscore)
#                 )
                
#                 /* Net drop ≥ 0.5 from the highest point in last 5 measurements */
#                 AND (
#                     GREATEST(
#                         ad_m4.weight_for_age_zscore,
#                         ad_m3.weight_for_age_zscore,
#                         ad_m2.weight_for_age_zscore,
#                         ad_m1.weight_for_age_zscore,
#                         ad_current.weight_for_age_zscore
#                     ) - ad_current.weight_for_age_zscore
#                 ) >= 0.5
            
#             UNION DISTINCT
            
#             -- SAM (Severe Acute Malnutrition)
#             SELECT DISTINCT
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             WHERE ad.do_you_have_height_weight = 1
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND ad.weight_for_height = 1
            
#             UNION DISTINCT
            
#             -- SUW (Severe Underweight) - weight_for_age = 1
#             SELECT DISTINCT
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             WHERE ad.do_you_have_height_weight = 1
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND ad.weight_for_age = 1
#         ) sub
#         GROUP BY creche_id
#     ),
    
#     -- CTE for measurement not taken reasons (counts per category)
#     mnt AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(CASE WHEN ad.measurement_reason = 1 THEN 1 END) AS child_not_in_creche,
#             COUNT(CASE WHEN ad.measurement_reason = 2 THEN 1 END) AS child_not_in_village,
#             COUNT(CASE WHEN ad.measurement_reason = 3 THEN 1 END) AS child_is_sick,
#             COUNT(CASE WHEN ad.measurement_reason = 4 THEN 1 END) AS other
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         WHERE YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND ad.do_you_have_height_weight = 0
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for health facility referrals (h)
#     h AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(cr.name) AS hf
#         FROM `tabChild Referral` cr
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND cr.referred_to != 1 
#           AND YEAR(cr.date_of_referral) = %(year)s 
#           AND MONTH(cr.date_of_referral) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for NRC referrals (nr)
#     nr AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(cr.name) AS nrc
#         FROM `tabChild Referral` cr
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND cr.referred_to = 4 
#           AND YEAR(cr.date_of_referral) = %(year)s 
#           AND MONTH(cr.date_of_referral) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for VHND referrals (vhn)
#     vhn AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(vh.name) AS vhnd
#         FROM `tabChild Referral` vh
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = vh.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND vh.referred_to = 1 
#           AND YEAR(vh.date_of_referral) = %(year)s 
#           AND MONTH(vh.date_of_referral) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for follow-up visits (cfu)
#     cfu AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(cr.name) AS cfu
#         FROM `tabChild Follow up` cr
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND YEAR(cr.followup_visit_date) = %(year)s 
#           AND MONTH(cr.followup_visit_date) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for growth metrics (gmd)
#     gmd AS (
#         SELECT 
#             cgm.creche_id,
#             COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
#             COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
#             COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,
#             COUNT(CASE WHEN ad.height_for_age = 3 THEN 1 END) AS height_for_age_normal,
#             COUNT(CASE WHEN ad.height_for_age = 2 THEN 1 END) AS height_for_age_moderate,
#             COUNT(CASE WHEN ad.height_for_age = 1 THEN 1 END) AS height_for_age_severe,
#             COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
#             COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
#             COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND cee.date_of_enrollment <= %(end_date)s
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for GM entered (gme)
#     gme AS (
#         SELECT 
#             cr.name AS creche_id, 
#             COUNT(cgm.creche_id) AS gm_entered
#         FROM `tabCreche` cr
#         LEFT JOIN `tabChild Growth Monitoring` cgm ON cr.name = cgm.creche_id
#         WHERE YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#         GROUP BY cr.name
#     )
    
#     SELECT
#         {", ".join(selected_fields)},
#         COUNT(*) AS op_creches,
#         COALESCE(SUM(tf.gm_entered), 0) AS gm_entered,
#         COALESCE(SUM(tf.e_children), 0) AS e_children,
#         COALESCE(SUM(tf.g_children), 0) AS g_children,
#         CASE 
#             WHEN COALESCE(SUM(tf.e_children), 0) = 0 THEN 0 
#             ELSE FORMAT(LEAST((SUM(tf.g_children) * 100.0) / SUM(tf.e_children), 100), 2) 
#         END AS e_children_percentage,
        
#         COALESCE(SUM(tf.child_not_in_creche), 0) AS child_not_in_creche,
#         COALESCE(SUM(tf.child_not_in_village), 0) AS child_not_in_village,
#         COALESCE(SUM(tf.child_is_sick), 0) AS child_is_sick,
#         COALESCE(SUM(tf.other), 0) AS other,
        
#         COALESCE(SUM(tf.hf), 0) AS hf,
#         COALESCE(SUM(tf.nrc), 0) AS nrc,
#         COALESCE(SUM(tf.vhnd), 0) AS vhnd,
#         COALESCE(SUM(tf.gf2), 0) AS gf2,
#         COALESCE(SUM(tf.gf1), 0) AS gf1,
#         COALESCE(SUM(tf.gf1_plus), 0) AS gf1_plus,
#         COALESCE(SUM(tf.zigzag), 0) AS zigzag,
#         COALESCE(SUM(tf.snc), 0) AS snc,
#         COALESCE(SUM(tf.cfu), 0) AS cfu,
#         tf.creche_id AS creche_id,
#         tf.cr_open_date AS cr_open_date,
        
#         COALESCE(SUM(tf.weight_for_age_normal), 0) AS weight_for_age_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_normal) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_age_normal,

#         COALESCE(SUM(tf.weight_for_age_moderate), 0) AS weight_for_age_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_moderate) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_age_moderate,

#         COALESCE(SUM(tf.weight_for_age_severe), 0) AS weight_for_age_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_severe) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_age_severe,
        
#         COALESCE(SUM(tf.height_for_age_normal), 0) AS height_for_age_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_normal) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_height_for_age_normal,

#         COALESCE(SUM(tf.height_for_age_moderate), 0) AS height_for_age_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_moderate) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_height_for_age_moderate,

#         COALESCE(SUM(tf.height_for_age_severe), 0) AS height_for_age_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_severe) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_height_for_age_severe,
        
#         COALESCE(SUM(tf.weight_for_height_normal), 0) AS weight_for_height_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_normal) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_height_normal,

#         COALESCE(SUM(tf.weight_for_height_moderate), 0) AS weight_for_height_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_moderate) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_height_moderate,

#         COALESCE(SUM(tf.weight_for_height_severe), 0) AS weight_for_height_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_severe) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_height_severe
#     FROM (
#         SELECT 
#             p.partner_name AS partner,
#             u.full_name AS supervisor,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             g.gp_name AS gp,
#             v.village_name AS village,
#             c.creche_name AS creche,
#             c.creche_id AS creche_id,
#             DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS cr_open_date,
#             COALESCE(ec.e_children, 0) AS e_children,
#             COALESCE(gc.g_children, 0) AS g_children,
#             COALESCE(h.hf, 0) AS hf,
#             COALESCE(nr.nrc, 0) AS nrc,
#             COALESCE(vhn.vhnd, 0) AS vhnd,
#             COALESCE(gf2c.gf2, 0) AS gf2,
#             COALESCE(gf1c.gf1, 0) AS gf1,
#             COALESCE(gf1pc.gf1_plus, 0) AS gf1_plus,
#             COALESCE(zigzagc.zigzag, 0) AS zigzag,
#             COALESCE(sncc.snc, 0) AS snc,
#             COALESCE(mnt.child_not_in_creche, 0) AS child_not_in_creche,
#             COALESCE(mnt.child_not_in_village, 0) AS child_not_in_village,
#             COALESCE(mnt.child_is_sick, 0) AS child_is_sick,
#             COALESCE(mnt.other, 0) AS other,
#             COALESCE(cfu.cfu, 0) AS cfu,
#             COALESCE(gmd.weight_for_age_normal, 0) AS weight_for_age_normal,
#             COALESCE(gmd.weight_for_age_moderate, 0) AS weight_for_age_moderate,
#             COALESCE(gmd.weight_for_age_severe, 0) AS weight_for_age_severe,
#             COALESCE(gmd.height_for_age_normal, 0) AS height_for_age_normal,
#             COALESCE(gmd.height_for_age_moderate, 0) AS height_for_age_moderate,
#             COALESCE(gmd.height_for_age_severe, 0) AS height_for_age_severe,
#             COALESCE(gmd.weight_for_height_normal, 0) AS weight_for_height_normal,
#             COALESCE(gmd.weight_for_height_moderate, 0) AS weight_for_height_moderate,
#             COALESCE(gmd.weight_for_height_severe, 0) AS weight_for_height_severe,
#             COALESCE(gme.gm_entered, 0) AS gm_entered
            
#         FROM `tabCreche` c 
#         LEFT JOIN ec ON c.name = ec.creche_id
#         LEFT JOIN gc ON c.name = gc.creche_id
#         LEFT JOIN gf2c ON c.name = gf2c.creche_id
#         LEFT JOIN gf1c ON c.name = gf1c.creche_id
#         LEFT JOIN gf1pc ON c.name = gf1pc.creche_id
#         LEFT JOIN zigzagc ON c.name = zigzagc.creche_id
#         LEFT JOIN sncc ON c.name = sncc.creche_id
#         LEFT JOIN h ON c.name = h.creche_id
#         LEFT JOIN nr ON c.name = nr.creche_id
#         LEFT JOIN vhn ON c.name = vhn.creche_id
#         LEFT JOIN cfu ON c.name = cfu.creche_id
#         LEFT JOIN gmd ON c.name = gmd.creche_id
#         LEFT JOIN gme ON c.name = gme.creche_id
#         LEFT JOIN mnt ON c.name = mnt.creche_id
        
#         INNER JOIN `tabState` s ON c.state_id = s.name 
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         INNER JOIN `tabVillage` v ON c.village_id = v.name
#         INNER JOIN `tabPartner` p ON c.partner_id = p.name 
#         INNER JOIN `tabUser` u ON u.name = c.supervisor_id
#         WHERE {where_clause}
#     ) AS tf
    
#     GROUP BY {group_by_field}
#     ORDER BY {group_by_field}
#     """

#     data = frappe.db.sql(query, params, as_dict=True)
    
#     total_act_creches = sum(int(row.get('op_creches', 0) or 0) for row in data)
#     total_gm_entered = sum(int(row.get('gm_entered', 0) or 0) for row in data)
#     total_e_children = sum(int(row.get('e_children', 0) or 0) for row in data)
#     total_g_children = sum(int(row.get('g_children', 0) or 0) for row in data)
#     total_hf = sum(int(row.get('hf', 0) or 0) for row in data)
#     total_nrc = sum(int(row.get('nrc', 0) or 0) for row in data)
#     total_cfu = sum(int(row.get('cfu', 0) or 0) for row in data)
#     total_vhnd = sum(int(row.get('vhnd', 0) or 0) for row in data)

#     total_gf1 = sum(int(row.get('gf1', 0) or 0) for row in data)
#     total_gf1_plus = sum(int(row.get('gf1_plus', 0) or 0) for row in data)
#     total_gf2 = sum(int(row.get('gf2', 0) or 0) for row in data)
#     total_zigzag = sum(int(row.get('zigzag', 0) or 0) for row in data)
#     total_snc = sum(int(row.get('snc', 0) or 0) for row in data)
    
#     total_child_not_in_creche = sum(int(row.get('child_not_in_creche', 0) or 0) for row in data)
#     total_child_not_in_village = sum(int(row.get('child_not_in_village', 0) or 0) for row in data)
#     total_child_is_sick = sum(int(row.get('child_is_sick', 0) or 0) for row in data)
#     total_other = sum(int(row.get('other', 0) or 0) for row in data)
    
#     total_weight_for_age_normal = sum(int(row.get('weight_for_age_normal', 0) or 0) for row in data)
#     total_weight_for_age_moderate = sum(int(row.get('weight_for_age_moderate', 0) or 0) for row in data)
#     total_weight_for_age_severe = sum(int(row.get('weight_for_age_severe', 0) or 0) for row in data)
    
#     total_height_for_age_normal = sum(int(row.get('height_for_age_normal', 0) or 0) for row in data)
#     total_height_for_age_moderate = sum(int(row.get('height_for_age_moderate', 0) or 0) for row in data)
#     total_height_for_age_severe = sum(int(row.get('height_for_age_severe', 0) or 0) for row in data)
    
#     total_weight_for_height_normal = sum(int(row.get('weight_for_height_normal', 0) or 0) for row in data)
#     total_weight_for_height_moderate = sum(int(row.get('weight_for_height_moderate', 0) or 0) for row in data)
#     total_weight_for_height_severe = sum(int(row.get('weight_for_height_severe', 0) or 0) for row in data)

#     total_mea_percentage = round((total_g_children * 100.0 / total_e_children), 2) if total_e_children else 0

#     total_wfan_per = round((total_weight_for_age_normal * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfam_per = round((total_weight_for_age_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfas_per = round((total_weight_for_age_severe * 100.0 / total_g_children), 2) if total_g_children else 0

#     total_hfan_per = round((total_height_for_age_normal * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_hfam_per = round((total_height_for_age_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_hfas_per = round((total_height_for_age_severe * 100.0 / total_g_children), 2) if total_g_children else 0

#     total_wfhn_per = round((total_weight_for_height_normal * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfhm_per = round((total_weight_for_height_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfhs_per = round((total_weight_for_height_severe * 100.0 / total_g_children), 2) if total_g_children else 0
    
#     total_row = {
  
#     "partner": "<b style='color:black;'>Total</b>",
#     "state": "<b style='color:black;'>Total</b>",
#     "gm_entered": f"<b>{total_gm_entered}</b>",
#     "op_creches": f"<b>{total_act_creches}</b>",
#     "e_children": f"<b>{total_e_children}</b>",
#     "g_children": f"<b>{total_g_children}</b>",
#     "e_children_percentage": f"<b>{total_mea_percentage}</b>",

#     "child_not_in_creche": f"<b>{total_child_not_in_creche}</b>",
#     "child_not_in_village": f"<b>{total_child_not_in_village}</b>",
#     "child_is_sick": f"<b>{total_child_is_sick}</b>",
#     "other": f"<b>{total_other}</b>",

#     "hf": f"<b>{total_hf}</b>",
#     "nrc": f"<b>{total_nrc}</b>",
#     "cfu": f"<b>{total_cfu}</b>",    
#     "vhnd": f"<b>{total_vhnd}</b>",

#     "gf1": f"<b>{total_gf1}</b>",
#     "gf1_plus": f"<b>{total_gf1_plus}</b>",
#     "gf2": f"<b>{total_gf2}</b>",
#     "zigzag": f"<b>{total_zigzag}</b>",
#     "snc": f"<b>{total_snc}</b>",
   
#     "weight_for_age_normal": f"<b>{total_weight_for_age_normal}</b>",
#     "weight_for_age_moderate": f"<b>{total_weight_for_age_moderate}</b>",
#     "weight_for_age_severe": f"<b>{total_weight_for_age_severe}</b>",
    
#     "per_weight_for_age_normal": f"<b>{total_wfan_per}</b>",
#     "per_weight_for_age_moderate": f"<b>{total_wfam_per}</b>",
#     "per_weight_for_age_severe": f"<b>{total_wfas_per}</b>",
    
#     "height_for_age_normal": f"<b>{total_height_for_age_normal}</b>",
#     "height_for_age_moderate": f"<b>{total_height_for_age_moderate}</b>",
#     "height_for_age_severe": f"<b>{total_height_for_age_severe}</b>", 
    
#     "per_height_for_age_normal": f"<b>{total_hfan_per}</b>",
#     "per_height_for_age_moderate": f"<b>{total_hfam_per}</b>",
#     "per_height_for_age_severe": f"<b>{total_hfas_per}</b>",  
    
#     "weight_for_height_normal": f"<b>{total_weight_for_height_normal}</b>",
#     "weight_for_height_moderate": f"<b>{total_weight_for_height_moderate}</b>",
#     "weight_for_height_severe": f"<b>{total_weight_for_height_severe}</b>",

#     "per_weight_for_height_normal": f"<b>{total_wfhn_per}</b>",
#     "per_weight_for_height_moderate": f"<b>{total_wfhm_per}</b>",
#     "per_weight_for_height_severe": f"<b>{total_wfhs_per}</b>"
# }

#     data.append(total_row)
#     return data







# """
# Growth Faltering Report - Frappe Query Report
# ==================================================
# This report analyzes child growth patterns using WHO-based WAZ (Weight-for-Age Z-Score) trends
# and identifies different categories of growth faltering.

# Growth Faltering Categories:
# - GF1: Any drop in WAZ from previous month
# - GF1+: WAZ drop >= 0.5 from best of last 2 months
# - GF2: WAZ drop >= 0.5 from 2 months ago
# - GF3: Zig-Zag pattern (mixed gain/loss in last 4 months) + drop >= 0.5 from peak
# - SNC: Severe Nutritional Concern (GF1+ OR GF2 OR GF3 OR SAM OR SUW)
# """

# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     """
#     Main execution function for Growth Faltering Report
#     Returns columns and data for Frappe Query Report
#     """
#     selected_level = filters.get("level", "7")
#     variable_columns = []

#     # Build dynamic columns based on selected aggregation level
#     if selected_level == "1":
#         variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
#     if selected_level == "2":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#     if selected_level == "3":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#     if selected_level == "4":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#     if selected_level == "5":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#     if selected_level == "6":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#     if selected_level == "7":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 150})
        

#     fixed_columns = [
#         # Basic Metrics
#         {"label": "Active Creches", "fieldname": "op_creches", "fieldtype": "Data", "width": 180},
#         {"label": "GM Submitted", "fieldname": "gm_entered", "fieldtype": "Data", "width": 180},
        
#         # Enrollment and Measurement Coverage
#         {"label": "Enrolled Children", "fieldname": "e_children", "fieldtype": "Data", "width": 150},
#         {"label": "Measurement Taken", "fieldname": "g_children", "fieldtype": "Data", "width": 180},
#         {"label": "Measurement (%)", "fieldname": "e_children_percentage", "fieldtype": "Data", "width": 150},
        
#         # Measurement Not Taken Reasons
#         {"label": "Child Not In Creche", "fieldname": "child_not_in_creche", "fieldtype": "Data", "width": 180},
#         {"label": "Child Not In Village", "fieldname": "child_not_in_village", "fieldtype": "Data", "width": 180},
#         {"label": "Child is Sick", "fieldname": "child_is_sick", "fieldtype": "Data", "width": 180},
#         {"label": "Other", "fieldname": "other", "fieldtype": "Data", "width": 180},
        
#         # Weight-for-Age (WFA) Indicators
#         {"label": "WFA - Normal", "fieldname": "weight_for_age_normal", "fieldtype": "Data", "width": 130},
#         {"label": "WFA - Normal (%)", "fieldname": "per_weight_for_age_normal", "fieldtype": "Data", "width": 150},
#         {"label": "WFA - Moderate", "fieldname": "weight_for_age_moderate", "fieldtype": "Data", "width": 140},
#         {"label": "WFA - Moderate (%)", "fieldname": "per_weight_for_age_moderate", "fieldtype": "Data", "width": 160},
#         {"label": "WFA - Severe", "fieldname": "weight_for_age_severe", "fieldtype": "Data", "width": 130},
#         {"label": "WFA - Severe (%)", "fieldname": "per_weight_for_age_severe", "fieldtype": "Data", "width": 150},

#         # Weight-for-Height (WFH) Indicators
#         {"label": "WFH - Normal", "fieldname": "weight_for_height_normal", "fieldtype": "Data", "width": 130},
#         {"label": "WFH - Normal (%)", "fieldname": "per_weight_for_height_normal", "fieldtype": "Data", "width": 150},
#         {"label": "WFH - Moderate", "fieldname": "weight_for_height_moderate", "fieldtype": "Data", "width": 140},
#         {"label": "WFH - Moderate (%)", "fieldname": "per_weight_for_height_moderate", "fieldtype": "Data", "width": 160},
#         {"label": "WFH - Severe", "fieldname": "weight_for_height_severe", "fieldtype": "Data", "width": 130},
#         {"label": "WFH - Severe (%)", "fieldname": "per_weight_for_height_severe", "fieldtype": "Data", "width": 150},

#         # Height-for-Age (HFA) Indicators
#         {"label": "HFA - Normal", "fieldname": "height_for_age_normal", "fieldtype": "Data", "width": 130},
#         {"label": "HFA - Normal (%)", "fieldname": "per_height_for_age_normal", "fieldtype": "Data", "width": 150},
#         {"label": "HFA - Moderate", "fieldname": "height_for_age_moderate", "fieldtype": "Data", "width": 140},
#         {"label": "HFA - Moderate (%)", "fieldname": "per_height_for_age_moderate", "fieldtype": "Data", "width": 160},
#         {"label": "HFA - Severe", "fieldname": "height_for_age_severe", "fieldtype": "Data", "width": 130},
#         {"label": "HFA - Severe (%)", "fieldname": "per_height_for_age_severe", "fieldtype": "Data", "width": 150},

#         # Growth Faltering Metrics (WHO-based WAZ trends)
#         {"label": "Growth Faltering 1", "fieldname": "gf1", "fieldtype": "Data", "width": 170},
#         {"label": "Growth Faltering 1+", "fieldname": "gf1_plus", "fieldtype": "Data", "width": 170},
#         {"label": "Growth Faltering 2", "fieldname": "gf2", "fieldtype": "Data", "width": 150},
#         {"label": "Growth Faltering 3 (Zig-Zag)", "fieldname": "gf3", "fieldtype": "Data", "width": 200},
#         {"label": "SNC", "fieldname": "snc", "fieldtype": "Data", "width": 150},

#         # Referral and Follow-up Metrics
#         {"label": "Referred to Health Facility", "fieldname": "hf", "fieldtype": "Data", "width": 260},
#         {"label": "Referred to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 250},
#         {"label": "Referred to VHND", "fieldname": "vhnd", "fieldtype": "Data", "width": 250},
#         {"label": "Followup Visits Done", "fieldname": "cfu", "fieldtype": "Data", "width": 250}, 
#     ]

#     columns = variable_columns + fixed_columns
#     data = get_report_data(filters)
#     return columns, data


# def get_report_data(filters):
#     """
#     Main data retrieval function
#     Builds and executes optimized SQL query with Growth Faltering calculations
#     """
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     # Calculate previous months for growth faltering analysis
#     # Month 1 month ago (for GF1)
#     if month == 1:
#         lmonth = 12
#         lyear = year - 1
#     else:
#         lmonth = month - 1
#         lyear = year
    
#     # Month 2 months ago (for GF2, GF1+)
#     if lmonth == 1:
#         plmonth = 12
#         pyear = lyear - 1
#     else:
#         plmonth = lmonth - 1
#         pyear = lyear

#     # Month 3 months ago (for GF3)
#     if plmonth == 1:
#         l3month = 12
#         l3year = pyear - 1
#     else:
#         l3month = plmonth - 1
#         l3year = pyear

#     # Month 4 months ago (for GF3)
#     if l3month == 1:
#         l4month = 12
#         l4year = l3year - 1
#     else:
#         l4month = l3month - 1
#         l4year = l3year

#     # Initialize filter conditions and parameters
#     conditions = ["1=1"]
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
#     }

#     # Get current user's partner
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Get current user's geographic access
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """

#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))

#     # Handle creche opening date range filter
#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None

#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range

#         elif range_type == "before" and single_date:
#             cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)

#         elif range_type == "after" and single_date:
#             cstart_date, cend_date = single_date + timedelta(days=1), date.today()

#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date

#     # Build WHERE clause conditions
#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None
    
#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("(c.creche_status_id = %(creche_status_id)s)")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#             params["phases"] = phases_cleaned    
    
#     if cstart_date or cend_date:
#         conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
#         params["cstart_date"] = cstart_date if cstart_date else None  
#         params["cend_date"] = cend_date if cend_date else None  

#     # Define aggregation level grouping
#     level_mapping = {
#         "1": ["tf.partner"],
#         "2": ["tf.state"],
#         "3": ["tf.state", "tf.district"],
#         "4": ["tf.state", "tf.district", "tf.block"],
#         "5": ["tf.state", "tf.district", "tf.block", "tf.supervisor"],
#         "6": ["tf.state", "tf.district", "tf.block", "tf.gp"],
#         "7": ["tf.state", "tf.district", "tf.block", "tf.gp", "tf.supervisor","tf.creche"],
#     }

#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)

#     # Build SELECT fields based on level
#     select_fields = [
#         "tf.partner AS partner", 
#         "tf.state AS state", 
#         "tf.district AS district", 
#         "tf.block AS block", 
#         "tf.supervisor AS supervisor",
#         "tf.gp AS gp",         
#         "tf.creche AS creche"
#     ]
#     selected_fields = []
#     for field in select_fields:
#         if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
#             selected_fields.append(field)

#     where_clause = " AND ".join(conditions)

#     # ===================================================================
#     # MAIN OPTIMIZED SQL QUERY WITH GROWTH FALTERING CALCULATIONS
#     # ===================================================================
#     query = f"""
#     WITH 
#     -- CTE for enrolled children (ec)
#     ec AS (
#         SELECT 
#             cee.creche_id, 
#             COUNT(*) AS e_children
#         FROM `tabChild Enrollment and Exit` cee
#         INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
#         WHERE cee.date_of_enrollment <= %(end_date)s 
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(start_date)s)
#         GROUP BY cee.creche_id
#     ),
    
#     -- CTE for growth measured children (gc)
#     gc AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(*) AS g_children
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND cee.date_of_enrollment <= %(end_date)s
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- ===================================================================
#     -- GROWTH FALTERING 1 (GF1): Any drop in WAZ from previous month
#     -- ===================================================================
#     gf1c AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(DISTINCT ad.childenrollguid) AS gf1
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         INNER JOIN `tabAnthropromatic Data` ad_last ON 
#             ad_last.childenrollguid = ad.childenrollguid 
#             AND ad_last.do_you_have_height_weight = 1
#             AND YEAR(ad_last.measurement_taken_date) = %(lyear)s 
#             AND MONTH(ad_last.measurement_taken_date) = %(lmonth)s 
#             AND ad_last.weight_for_age_zscore IS NOT NULL
#             AND ad_last.weight_for_age_zscore != ''
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND ad.weight_for_age_zscore IS NOT NULL
#           AND ad.weight_for_age_zscore != ''
#           AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_last.weight_for_age_zscore AS DECIMAL(10,4))
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- ===================================================================
#     -- GROWTH FALTERING 1+ (GF1+): WAZ drop >= 0.5 from best of last 2 months
#     -- ===================================================================
#     gf1pc AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(DISTINCT ad.childenrollguid) AS gf1_plus
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         -- Get last month data
#         LEFT JOIN `tabAnthropromatic Data` ad_m1 ON 
#             ad_m1.childenrollguid = ad.childenrollguid 
#             AND ad_m1.do_you_have_height_weight = 1
#             AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s 
#             AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s 
#             AND ad_m1.weight_for_age_zscore IS NOT NULL
#             AND ad_m1.weight_for_age_zscore != ''
#         -- Get 2 months ago data
#         LEFT JOIN `tabAnthropromatic Data` ad_m2 ON 
#             ad_m2.childenrollguid = ad.childenrollguid 
#             AND ad_m2.do_you_have_height_weight = 1
#             AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s 
#             AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s 
#             AND ad_m2.weight_for_age_zscore IS NOT NULL
#             AND ad_m2.weight_for_age_zscore != ''
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND ad.weight_for_age_zscore IS NOT NULL
#           AND ad.weight_for_age_zscore != ''
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#           -- At least one previous month must exist
#           AND (ad_m1.weight_for_age_zscore IS NOT NULL OR ad_m2.weight_for_age_zscore IS NOT NULL)
#           -- Current WAZ <= (Max of last 2 months - 0.5)
#           AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#               GREATEST(
#                   COALESCE(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), -999),
#                   COALESCE(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), -999)
#               ) - 0.5
#         GROUP BY cgm.creche_id
#     ),
    
#     -- ===================================================================
#     -- GROWTH FALTERING 2 (GF2): WAZ drop >= 0.5 from 2 months ago
#     -- ===================================================================
#     gf2c AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(DISTINCT ad.childenrollguid) AS gf2
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         INNER JOIN `tabAnthropromatic Data` ad_2m ON 
#             ad_2m.childenrollguid = ad.childenrollguid 
#             AND ad_2m.do_you_have_height_weight = 1
#             AND YEAR(ad_2m.measurement_taken_date) = %(pyear)s 
#             AND MONTH(ad_2m.measurement_taken_date) = %(plmonth)s 
#             AND ad_2m.weight_for_age_zscore IS NOT NULL
#             AND ad_2m.weight_for_age_zscore != ''
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND ad.weight_for_age_zscore IS NOT NULL
#           AND ad.weight_for_age_zscore != ''
#           AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#               CAST(ad_2m.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- ===================================================================
#     -- GROWTH FALTERING 3 (GF3): Zig-Zag pattern + drop >= 0.5 from peak
#     -- Requires: 4 previous months data + mixed gain/loss + significant drop
#     -- ===================================================================
#     gf3c AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(DISTINCT ad.childenrollguid) AS gf3
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#         -- Get 1 month ago (m1)
#         LEFT JOIN `tabAnthropromatic Data` ad_m1 ON 
#             ad_m1.childenrollguid = ad.childenrollguid 
#             AND ad_m1.do_you_have_height_weight = 1
#             AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s 
#             AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s 
#             AND ad_m1.weight_for_age_zscore IS NOT NULL
#             AND ad_m1.weight_for_age_zscore != ''
#         -- Get 2 months ago (m2)
#         LEFT JOIN `tabAnthropromatic Data` ad_m2 ON 
#             ad_m2.childenrollguid = ad.childenrollguid 
#             AND ad_m2.do_you_have_height_weight = 1
#             AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s 
#             AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s 
#             AND ad_m2.weight_for_age_zscore IS NOT NULL
#             AND ad_m2.weight_for_age_zscore != ''
#         -- Get 3 months ago (m3)
#         LEFT JOIN `tabAnthropromatic Data` ad_m3 ON 
#             ad_m3.childenrollguid = ad.childenrollguid 
#             AND ad_m3.do_you_have_height_weight = 1
#             AND YEAR(ad_m3.measurement_taken_date) = %(l3year)s 
#             AND MONTH(ad_m3.measurement_taken_date) = %(l3month)s 
#             AND ad_m3.weight_for_age_zscore IS NOT NULL
#             AND ad_m3.weight_for_age_zscore != ''
#         -- Get 4 months ago (m4)
#         LEFT JOIN `tabAnthropromatic Data` ad_m4 ON 
#             ad_m4.childenrollguid = ad.childenrollguid 
#             AND ad_m4.do_you_have_height_weight = 1
#             AND YEAR(ad_m4.measurement_taken_date) = %(l4year)s 
#             AND MONTH(ad_m4.measurement_taken_date) = %(l4month)s 
#             AND ad_m4.weight_for_age_zscore IS NOT NULL
#             AND ad_m4.weight_for_age_zscore != ''
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND ad.weight_for_age_zscore IS NOT NULL
#           AND ad.weight_for_age_zscore != ''
#           AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#           -- Must have all 4 previous months data
#           AND ad_m1.weight_for_age_zscore IS NOT NULL
#           AND ad_m2.weight_for_age_zscore IS NOT NULL
#           AND ad_m3.weight_for_age_zscore IS NOT NULL
#           AND ad_m4.weight_for_age_zscore IS NOT NULL
#           -- Find highest WAZ in last 4 months (excluding current) and check drop >= 0.5
#           AND GREATEST(
#               CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)),
#               CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)),
#               CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
#               CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4))
#           ) - CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5
#           -- Detect zig-zag: at least one gain AND one loss in the sequence
#           AND (
#               -- At least one gain detected (m_i > m_(i+1))
#               (CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4))
#                OR CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4))
#                OR CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)))
#               AND 
#               -- At least one loss detected (m_i < m_(i+1))
#               (CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4))
#                OR CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4))
#                OR CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)))
#           )
#         GROUP BY cgm.creche_id
#     ),
    
#     -- ===================================================================
#     -- SNC (Severe Nutritional Concern): DISTINCT children with ANY of:
#     -- GF1+, GF2, GF3, SAM (WFH=1), or SUW (WAZ<=-3)
#     -- ===================================================================
#     sncc AS (
#         SELECT 
#             creche_id, 
#             COUNT(DISTINCT childenrollguid) AS snc
#         FROM (
#             -- GF1+ cases
#             SELECT 
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             LEFT JOIN `tabAnthropromatic Data` ad_m1 ON 
#                 ad_m1.childenrollguid = ad.childenrollguid 
#                 AND ad_m1.do_you_have_height_weight = 1
#                 AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s 
#                 AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s 
#                 AND ad_m1.weight_for_age_zscore IS NOT NULL
#                 AND ad_m1.weight_for_age_zscore != ''
#             LEFT JOIN `tabAnthropromatic Data` ad_m2 ON 
#                 ad_m2.childenrollguid = ad.childenrollguid 
#                 AND ad_m2.do_you_have_height_weight = 1
#                 AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s 
#                 AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s 
#                 AND ad_m2.weight_for_age_zscore IS NOT NULL
#                 AND ad_m2.weight_for_age_zscore != ''
#             WHERE ad.do_you_have_height_weight = 1 
#               AND YEAR(cgm.measurement_date) = %(year)s 
#               AND MONTH(cgm.measurement_date) = %(month)s
#               AND ad.weight_for_age_zscore IS NOT NULL
#               AND ad.weight_for_age_zscore != ''
#               AND (ad_m1.weight_for_age_zscore IS NOT NULL OR ad_m2.weight_for_age_zscore IS NOT NULL)
#               AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                   GREATEST(
#                       COALESCE(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), -999),
#                       COALESCE(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), -999)
#                   ) - 0.5
            
#             UNION DISTINCT
            
#             -- GF2 cases
#             SELECT 
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             INNER JOIN `tabAnthropromatic Data` ad_2m ON 
#                 ad_2m.childenrollguid = ad.childenrollguid 
#                 AND ad_2m.do_you_have_height_weight = 1
#                 AND YEAR(ad_2m.measurement_taken_date) = %(pyear)s 
#                 AND MONTH(ad_2m.measurement_taken_date) = %(plmonth)s 
#                 AND ad_2m.weight_for_age_zscore IS NOT NULL
#                 AND ad_2m.weight_for_age_zscore != ''
#             WHERE ad.do_you_have_height_weight = 1 
#               AND YEAR(cgm.measurement_date) = %(year)s 
#               AND MONTH(cgm.measurement_date) = %(month)s
#               AND ad.weight_for_age_zscore IS NOT NULL
#               AND ad.weight_for_age_zscore != ''
#               AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= 
#                   CAST(ad_2m.weight_for_age_zscore AS DECIMAL(10,4)) - 0.5
            
#             UNION DISTINCT
            
#             -- GF3 (Zig-Zag) cases
#             SELECT 
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
#             LEFT JOIN `tabAnthropromatic Data` ad_m1 ON 
#                 ad_m1.childenrollguid = ad.childenrollguid 
#                 AND ad_m1.do_you_have_height_weight = 1
#                 AND YEAR(ad_m1.measurement_taken_date) = %(lyear)s 
#                 AND MONTH(ad_m1.measurement_taken_date) = %(lmonth)s 
#                 AND ad_m1.weight_for_age_zscore IS NOT NULL
#                 AND ad_m1.weight_for_age_zscore != ''
#             LEFT JOIN `tabAnthropromatic Data` ad_m2 ON 
#                 ad_m2.childenrollguid = ad.childenrollguid 
#                 AND ad_m2.do_you_have_height_weight = 1
#                 AND YEAR(ad_m2.measurement_taken_date) = %(pyear)s 
#                 AND MONTH(ad_m2.measurement_taken_date) = %(plmonth)s 
#                 AND ad_m2.weight_for_age_zscore IS NOT NULL
#                 AND ad_m2.weight_for_age_zscore != ''
#             LEFT JOIN `tabAnthropromatic Data` ad_m3 ON 
#                 ad_m3.childenrollguid = ad.childenrollguid 
#                 AND ad_m3.do_you_have_height_weight = 1
#                 AND YEAR(ad_m3.measurement_taken_date) = %(l3year)s 
#                 AND MONTH(ad_m3.measurement_taken_date) = %(l3month)s 
#                 AND ad_m3.weight_for_age_zscore IS NOT NULL
#                 AND ad_m3.weight_for_age_zscore != ''
#             LEFT JOIN `tabAnthropromatic Data` ad_m4 ON 
#                 ad_m4.childenrollguid = ad.childenrollguid 
#                 AND ad_m4.do_you_have_height_weight = 1
#                 AND YEAR(ad_m4.measurement_taken_date) = %(l4year)s 
#                 AND MONTH(ad_m4.measurement_taken_date) = %(l4month)s 
#                 AND ad_m4.weight_for_age_zscore IS NOT NULL
#                 AND ad_m4.weight_for_age_zscore != ''
#             WHERE ad.do_you_have_height_weight = 1 
#               AND YEAR(cgm.measurement_date) = %(year)s 
#               AND MONTH(cgm.measurement_date) = %(month)s
#               AND ad.weight_for_age_zscore IS NOT NULL
#               AND ad.weight_for_age_zscore != ''
#               AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
#               AND ad_m1.weight_for_age_zscore IS NOT NULL
#               AND ad_m2.weight_for_age_zscore IS NOT NULL
#               AND ad_m3.weight_for_age_zscore IS NOT NULL
#               AND ad_m4.weight_for_age_zscore IS NOT NULL
#               AND GREATEST(
#                   CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)),
#                   CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)),
#                   CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
#                   CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4))
#               ) - CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) >= 0.5
#               AND (
#                   (CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4))
#                    OR CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4))
#                    OR CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)))
#                   AND 
#                   (CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4))
#                    OR CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4))
#                    OR CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)))
#               )
            
#             UNION DISTINCT
            
#             -- SAM (weight_for_height = 1 = Severe Acute Malnutrition)
#             SELECT 
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             WHERE ad.do_you_have_height_weight = 1 
#               AND YEAR(cgm.measurement_date) = %(year)s 
#               AND MONTH(cgm.measurement_date) = %(month)s
#               AND ad.weight_for_height = 1
            
#             UNION DISTINCT
            
#             -- SUW (Severely Underweight: WAZ <= -3)
#             SELECT 
#                 cgm.creche_id, 
#                 ad.childenrollguid
#             FROM `tabAnthropromatic Data` ad
#             INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#             WHERE ad.do_you_have_height_weight = 1 
#               AND YEAR(cgm.measurement_date) = %(year)s 
#               AND MONTH(cgm.measurement_date) = %(month)s
#               AND ad.weight_for_age_zscore IS NOT NULL
#               AND ad.weight_for_age_zscore != ''
#               AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= -3
#         ) sub
#         GROUP BY creche_id
#     ),
    
#     -- CTE for measurement not taken reasons
#     mnt AS (
#         SELECT 
#             cgm.creche_id, 
#             COUNT(CASE WHEN ad.measurement_reason = 1 THEN 1 END) AS child_not_in_creche,
#             COUNT(CASE WHEN ad.measurement_reason = 2 THEN 1 END) AS child_not_in_village,
#             COUNT(CASE WHEN ad.measurement_reason = 3 THEN 1 END) AS child_is_sick,
#             COUNT(CASE WHEN ad.measurement_reason = 4 THEN 1 END) AS other
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
#         WHERE YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND ad.do_you_have_height_weight = 0
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for health facility referrals
#     h AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(cr.name) AS hf
#         FROM `tabChild Referral` cr
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND cr.referred_to != 1 
#           AND YEAR(cr.date_of_referral) = %(year)s 
#           AND MONTH(cr.date_of_referral) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for NRC referrals
#     nr AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(cr.name) AS nrc
#         FROM `tabChild Referral` cr
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND cr.referred_to = 4 
#           AND YEAR(cr.date_of_referral) = %(year)s 
#           AND MONTH(cr.date_of_referral) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for VHND referrals
#     vhn AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(vh.name) AS vhnd
#         FROM `tabChild Referral` vh
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = vh.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND vh.referred_to = 1 
#           AND YEAR(vh.date_of_referral) = %(year)s 
#           AND MONTH(vh.date_of_referral) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for follow-up visits
#     cfu AS (
#         SELECT 
#             cep.creche_id, 
#             COUNT(cr.name) AS cfu
#         FROM `tabChild Follow up` cr
#         INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
#         WHERE cep.date_of_enrollment <= %(end_date)s 
#           AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
#           AND YEAR(cr.followup_visit_date) = %(year)s 
#           AND MONTH(cr.followup_visit_date) = %(month)s
#         GROUP BY cep.creche_id
#     ),
    
#     -- CTE for growth metrics (WFA, HFA, WFH indicators)
#     gmd AS (
#         SELECT 
#             cgm.creche_id,
#             COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
#             COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
#             COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,
#             COUNT(CASE WHEN ad.height_for_age = 3 THEN 1 END) AS height_for_age_normal,
#             COUNT(CASE WHEN ad.height_for_age = 2 THEN 1 END) AS height_for_age_moderate,
#             COUNT(CASE WHEN ad.height_for_age = 1 THEN 1 END) AS height_for_age_severe,
#             COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
#             COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
#             COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#         INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
#         WHERE ad.do_you_have_height_weight = 1 
#           AND YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#           AND cee.date_of_enrollment <= %(end_date)s
#           AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#         GROUP BY cgm.creche_id
#     ),
    
#     -- CTE for GM entered count
#     gme AS (
#         SELECT 
#             cr.name AS creche_id, 
#             COUNT(cgm.creche_id) AS gm_entered
#         FROM `tabCreche` cr
#         LEFT JOIN `tabChild Growth Monitoring` cgm ON cr.name = cgm.creche_id
#         WHERE YEAR(cgm.measurement_date) = %(year)s 
#           AND MONTH(cgm.measurement_date) = %(month)s
#         GROUP BY cr.name
#     )
    
#     -- ===================================================================
#     -- MAIN SELECT WITH AGGREGATION
#     -- ===================================================================
#     SELECT
#         {", ".join(selected_fields)},
#         COUNT(*) AS op_creches,
#         COALESCE(SUM(tf.gm_entered), 0) AS gm_entered,
#         COALESCE(SUM(tf.e_children), 0) AS e_children,
#         COALESCE(SUM(tf.g_children), 0) AS g_children,
#         CASE 
#             WHEN COALESCE(SUM(tf.e_children), 0) = 0 THEN 0 
#             ELSE FORMAT(LEAST((SUM(tf.g_children) * 100.0) / SUM(tf.e_children), 100), 2) 
#         END AS e_children_percentage,
        
#         COALESCE(SUM(tf.child_not_in_creche), 0) AS child_not_in_creche,
#         COALESCE(SUM(tf.child_not_in_village), 0) AS child_not_in_village,
#         COALESCE(SUM(tf.child_is_sick), 0) AS child_is_sick,
#         COALESCE(SUM(tf.other), 0) AS other,
        
#         COALESCE(SUM(tf.hf), 0) AS hf,
#         COALESCE(SUM(tf.nrc), 0) AS nrc,
#         COALESCE(SUM(tf.vhnd), 0) AS vhnd,
#         COALESCE(SUM(tf.gf1), 0) AS gf1,
#         COALESCE(SUM(tf.gf1_plus), 0) AS gf1_plus,
#         COALESCE(SUM(tf.gf2), 0) AS gf2,
#         COALESCE(SUM(tf.gf3), 0) AS gf3,
#         COALESCE(SUM(tf.snc), 0) AS snc,
#         COALESCE(SUM(tf.cfu), 0) AS cfu,
#         tf.creche_id AS creche_id,
#         tf.cr_open_date AS cr_open_date,
        
#         -- Weight-for-Age metrics with percentages
#         COALESCE(SUM(tf.weight_for_age_normal), 0) AS weight_for_age_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_normal) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_age_normal,

#         COALESCE(SUM(tf.weight_for_age_moderate), 0) AS weight_for_age_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_moderate) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_age_moderate,

#         COALESCE(SUM(tf.weight_for_age_severe), 0) AS weight_for_age_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_severe) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_age_severe,
        
#         -- Height-for-Age metrics with percentages
#         COALESCE(SUM(tf.height_for_age_normal), 0) AS height_for_age_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_normal) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_height_for_age_normal,

#         COALESCE(SUM(tf.height_for_age_moderate), 0) AS height_for_age_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_moderate) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_height_for_age_moderate,

#         COALESCE(SUM(tf.height_for_age_severe), 0) AS height_for_age_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_severe) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_height_for_age_severe,
        
#         -- Weight-for-Height metrics with percentages
#         COALESCE(SUM(tf.weight_for_height_normal), 0) AS weight_for_height_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_normal) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_height_normal,

#         COALESCE(SUM(tf.weight_for_height_moderate), 0) AS weight_for_height_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_moderate) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_height_moderate,

#         COALESCE(SUM(tf.weight_for_height_severe), 0) AS weight_for_height_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_severe) * 100.0) / SUM(tf.g_children), 2) 
#         END AS per_weight_for_height_severe
#     FROM (
#         SELECT 
#             p.partner_name AS partner,
#             u.full_name AS supervisor,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             g.gp_name AS gp,
#             v.village_name AS village,
#             c.creche_name AS creche,
#             c.creche_id AS creche_id,
#             DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS cr_open_date,
#             COALESCE(ec.e_children, 0) AS e_children,
#             COALESCE(gc.g_children, 0) AS g_children,
#             COALESCE(h.hf, 0) AS hf,
#             COALESCE(nr.nrc, 0) AS nrc,
#             COALESCE(vhn.vhnd, 0) AS vhnd,
#             COALESCE(gf1c.gf1, 0) AS gf1,
#             COALESCE(gf1pc.gf1_plus, 0) AS gf1_plus,
#             COALESCE(gf2c.gf2, 0) AS gf2,
#             COALESCE(gf3c.gf3, 0) AS gf3,
#             COALESCE(sncc.snc, 0) AS snc,
#             COALESCE(mnt.child_not_in_creche, 0) AS child_not_in_creche,
#             COALESCE(mnt.child_not_in_village, 0) AS child_not_in_village,
#             COALESCE(mnt.child_is_sick, 0) AS child_is_sick,
#             COALESCE(mnt.other, 0) AS other,
#             COALESCE(cfu.cfu, 0) AS cfu,
#             COALESCE(gmd.weight_for_age_normal, 0) AS weight_for_age_normal,
#             COALESCE(gmd.weight_for_age_moderate, 0) AS weight_for_age_moderate,
#             COALESCE(gmd.weight_for_age_severe, 0) AS weight_for_age_severe,
#             COALESCE(gmd.height_for_age_normal, 0) AS height_for_age_normal,
#             COALESCE(gmd.height_for_age_moderate, 0) AS height_for_age_moderate,
#             COALESCE(gmd.height_for_age_severe, 0) AS height_for_age_severe,
#             COALESCE(gmd.weight_for_height_normal, 0) AS weight_for_height_normal,
#             COALESCE(gmd.weight_for_height_moderate, 0) AS weight_for_height_moderate,
#             COALESCE(gmd.weight_for_height_severe, 0) AS weight_for_height_severe,
#             COALESCE(gme.gm_entered, 0) AS gm_entered
            
#         FROM `tabCreche` c 
#         LEFT JOIN ec ON c.name = ec.creche_id
#         LEFT JOIN gc ON c.name = gc.creche_id
#         LEFT JOIN gf1c ON c.name = gf1c.creche_id
#         LEFT JOIN gf1pc ON c.name = gf1pc.creche_id
#         LEFT JOIN gf2c ON c.name = gf2c.creche_id
#         LEFT JOIN gf3c ON c.name = gf3c.creche_id
#         LEFT JOIN sncc ON c.name = sncc.creche_id
#         LEFT JOIN h ON c.name = h.creche_id
#         LEFT JOIN nr ON c.name = nr.creche_id
#         LEFT JOIN vhn ON c.name = vhn.creche_id
#         LEFT JOIN cfu ON c.name = cfu.creche_id
#         LEFT JOIN gmd ON c.name = gmd.creche_id
#         LEFT JOIN gme ON c.name = gme.creche_id
#         LEFT JOIN mnt ON c.name = mnt.creche_id
        
#         INNER JOIN `tabState` s ON c.state_id = s.name 
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         INNER JOIN `tabVillage` v ON c.village_id = v.name
#         INNER JOIN `tabPartner` p ON c.partner_id = p.name 
#         INNER JOIN `tabUser` u ON u.name = c.supervisor_id
#         WHERE {where_clause}
#     ) AS tf
    
#     GROUP BY {group_by_field}
#     ORDER BY {group_by_field}
#     """

#     # Execute the query
#     data = frappe.db.sql(query, params, as_dict=True)
    
#     # ===================================================================
#     # Calculate totals for summary row
#     # ===================================================================
#     total_act_creches = sum(int(row.get('op_creches', 0) or 0) for row in data)
#     total_gm_entered = sum(int(row.get('gm_entered', 0) or 0) for row in data)
#     total_e_children = sum(int(row.get('e_children', 0) or 0) for row in data)
#     total_g_children = sum(int(row.get('g_children', 0) or 0) for row in data)
#     total_hf = sum(int(row.get('hf', 0) or 0) for row in data)
#     total_nrc = sum(int(row.get('nrc', 0) or 0) for row in data)
#     total_cfu = sum(int(row.get('cfu', 0) or 0) for row in data)
#     total_vhnd = sum(int(row.get('vhnd', 0) or 0) for row in data)

#     total_gf1 = sum(int(row.get('gf1', 0) or 0) for row in data)
#     total_gf1_plus = sum(int(row.get('gf1_plus', 0) or 0) for row in data)
#     total_gf2 = sum(int(row.get('gf2', 0) or 0) for row in data)
#     total_gf3 = sum(int(row.get('gf3', 0) or 0) for row in data)
#     total_snc = sum(int(row.get('snc', 0) or 0) for row in data)
    
#     total_child_not_in_creche = sum(int(row.get('child_not_in_creche', 0) or 0) for row in data)
#     total_child_not_in_village = sum(int(row.get('child_not_in_village', 0) or 0) for row in data)
#     total_child_is_sick = sum(int(row.get('child_is_sick', 0) or 0) for row in data)
#     total_other = sum(int(row.get('other', 0) or 0) for row in data)
    
#     total_weight_for_age_normal = sum(int(row.get('weight_for_age_normal', 0) or 0) for row in data)
#     total_weight_for_age_moderate = sum(int(row.get('weight_for_age_moderate', 0) or 0) for row in data)
#     total_weight_for_age_severe = sum(int(row.get('weight_for_age_severe', 0) or 0) for row in data)
    
#     total_height_for_age_normal = sum(int(row.get('height_for_age_normal', 0) or 0) for row in data)
#     total_height_for_age_moderate = sum(int(row.get('height_for_age_moderate', 0) or 0) for row in data)
#     total_height_for_age_severe = sum(int(row.get('height_for_age_severe', 0) or 0) for row in data)
    
#     total_weight_for_height_normal = sum(int(row.get('weight_for_height_normal', 0) or 0) for row in data)
#     total_weight_for_height_moderate = sum(int(row.get('weight_for_height_moderate', 0) or 0) for row in data)
#     total_weight_for_height_severe = sum(int(row.get('weight_for_height_severe', 0) or 0) for row in data)

#     # Calculate percentages for totals
#     total_mea_percentage = round((total_g_children * 100.0 / total_e_children), 2) if total_e_children else 0

#     total_wfan_per = round((total_weight_for_age_normal * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfam_per = round((total_weight_for_age_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfas_per = round((total_weight_for_age_severe * 100.0 / total_g_children), 2) if total_g_children else 0

#     total_hfan_per = round((total_height_for_age_normal * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_hfam_per = round((total_height_for_age_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_hfas_per = round((total_height_for_age_severe * 100.0 / total_g_children), 2) if total_g_children else 0

#     total_wfhn_per = round((total_weight_for_height_normal * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfhm_per = round((total_weight_for_height_moderate * 100.0 / total_g_children), 2) if total_g_children else 0
#     total_wfhs_per = round((total_weight_for_height_severe * 100.0 / total_g_children), 2) if total_g_children else 0
    
#     # Build total row with bold formatting
#     total_row = {
#         "partner": "<b style='color:black;'>Total</b>",
#         "state": "<b style='color:black;'>Total</b>",
#         "gm_entered": f"<b>{total_gm_entered}</b>",
#         "op_creches": f"<b>{total_act_creches}</b>",
#         "e_children": f"<b>{total_e_children}</b>",
#         "g_children": f"<b>{total_g_children}</b>",
#         "e_children_percentage": f"<b>{total_mea_percentage}</b>",

#         "child_not_in_creche": f"<b>{total_child_not_in_creche}</b>",
#         "child_not_in_village": f"<b>{total_child_not_in_village}</b>",
#         "child_is_sick": f"<b>{total_child_is_sick}</b>",
#         "other": f"<b>{total_other}</b>",

#         "hf": f"<b>{total_hf}</b>",
#         "nrc": f"<b>{total_nrc}</b>",
#         "cfu": f"<b>{total_cfu}</b>",    
#         "vhnd": f"<b>{total_vhnd}</b>",

#         "gf1": f"<b>{total_gf1}</b>",
#         "gf1_plus": f"<b>{total_gf1_plus}</b>",
#         "gf2": f"<b>{total_gf2}</b>",
#         "gf3": f"<b>{total_gf3}</b>",
#         "snc": f"<b>{total_snc}</b>",
   
#         "weight_for_age_normal": f"<b>{total_weight_for_age_normal}</b>",
#         "weight_for_age_moderate": f"<b>{total_weight_for_age_moderate}</b>",
#         "weight_for_age_severe": f"<b>{total_weight_for_age_severe}</b>",
        
#         "per_weight_for_age_normal": f"<b>{total_wfan_per}</b>",
#         "per_weight_for_age_moderate": f"<b>{total_wfam_per}</b>",
#         "per_weight_for_age_severe": f"<b>{total_wfas_per}</b>",
        
#         "height_for_age_normal": f"<b>{total_height_for_age_normal}</b>",
#         "height_for_age_moderate": f"<b>{total_height_for_age_moderate}</b>",
#         "height_for_age_severe": f"<b>{total_height_for_age_severe}</b>", 
        
#         "per_height_for_age_normal": f"<b>{total_hfan_per}</b>",
#         "per_height_for_age_moderate": f"<b>{total_hfam_per}</b>",
#         "per_height_for_age_severe": f"<b>{total_hfas_per}</b>",  
        
#         "weight_for_height_normal": f"<b>{total_weight_for_height_normal}</b>",
#         "weight_for_height_moderate": f"<b>{total_weight_for_height_moderate}</b>",
#         "weight_for_height_severe": f"<b>{total_weight_for_height_severe}</b>",

#         "per_weight_for_height_normal": f"<b>{total_wfhn_per}</b>",
#         "per_weight_for_height_moderate": f"<b>{total_wfhm_per}</b>",
#         "per_weight_for_height_severe": f"<b>{total_wfhs_per}</b>"
#     }

#     data.append(total_row)
#     return data