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
        
        {"label": "Child Not In Creche", "fieldname": "child_not_in_creche", "fieldtype": "Data", "width": 170},
        {"label": "Child Not In Village", "fieldname": "child_not_in_village", "fieldtype": "Data", "width": 150},
        {"label": "Child is Sick", "fieldname": "child_is_sick", "fieldtype": "Data", "width": 130},
        {"label": "Other", "fieldname": "other_reason", "fieldtype": "Data", "width": 120},
        
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

        {"label": "Growth Faltering 1", "fieldname": "gf1", "fieldtype": "Data", "width": 150},
        {"label": "Growth Faltering 2", "fieldname": "gf2", "fieldtype": "Data", "width": 150},
        
        
        {"label": "Red Flagged Children", "fieldname": "red_flag", "fieldtype": "Data", "width": 250},
        {"label": "Red Flagged Children Home Visits Done", "fieldname": "red_flag_f", "fieldtype": "Data", "width": 300},

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
    
    -- CTE for measurement reasons
    mr AS (
        SELECT 
            cgm.creche_id,
            COUNT(CASE WHEN ad.measurement_reason = 1 THEN 1 END) AS child_not_in_creche,
            COUNT(CASE WHEN ad.measurement_reason = 2 THEN 1 END) AS child_not_in_village,
            COUNT(CASE WHEN ad.measurement_reason = 3 THEN 1 END) AS child_is_sick,
            COUNT(CASE WHEN ad.measurement_reason = 4 THEN 1 END) AS other_reason
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = ad.childenrollguid
        WHERE ad.do_you_have_height_weight = 0
          AND ad.measurement_reason IS NOT NULL
          AND ad.measurement_reason > 0
          AND YEAR(cgm.measurement_date) = %(year)s
          AND MONTH(cgm.measurement_date) = %(month)s
          AND cee.date_of_enrollment <= %(end_date)s
          AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for growth faltering 2 (gf2) - children with faltering in both last month and previous month
    gf2c AS (
        SELECT 
            cgm.creche_id, 
            COUNT(*) AS gf2
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabAnthropromatic Data` ad_lyear ON 
            ad_lyear.childenrollguid = ad.childenrollguid 
            AND ad_lyear.do_you_have_height_weight = 1
            AND YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
            AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
            AND ad.weight <= ad_lyear.weight
        INNER JOIN `tabAnthropromatic Data` ad_pyear ON 
            ad_pyear.childenrollguid = ad.childenrollguid 
            AND ad_pyear.do_you_have_height_weight = 1
            AND YEAR(ad_pyear.measurement_taken_date) = %(pyear)s 
            AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s 
            AND ad_lyear.weight <= ad_pyear.weight
        WHERE ad.do_you_have_height_weight = 1 
          AND YEAR(cgm.measurement_date) = %(year)s 
          AND MONTH(cgm.measurement_date) = %(month)s
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for growth faltering 1 (gf1) - children with faltering in last month but not previous month
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
            AND YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
            AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
            AND ad.weight <= ad_lyear.weight
        LEFT JOIN `tabAnthropromatic Data` ad_pyear ON 
            ad_pyear.childenrollguid = ad.childenrollguid 
            AND ad_pyear.do_you_have_height_weight = 1
            AND YEAR(ad_pyear.measurement_taken_date) = %(pyear)s 
            AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s 
            AND ad_lyear.weight <= ad_pyear.weight
        WHERE ad.do_you_have_height_weight = 1 
          AND YEAR(cgm.measurement_date) = %(year)s 
          AND MONTH(cgm.measurement_date) = %(month)s
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
          AND ad_pyear.name IS NULL
        GROUP BY cgm.creche_id
    ),
    
    -- CTE for red flagged children (rf) - complex condition
    rf AS (
        SELECT 
            tcgm.creche_id, 
            COUNT(ad.name) AS red_flag
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` tcgm ON ad.parent = tcgm.name 
        WHERE YEAR(ad.measurement_taken_date) = %(year)s 
          AND MONTH(ad.measurement_taken_date) = %(month)s
          AND (
              ad.weight_for_age = 1 
              OR ad.weight_for_height = 1
              OR ad.any_medical_major_illness = 1
              OR ad.childenrollguid IN (
                  SELECT ad_current.childenrollguid 
                  FROM `tabAnthropromatic Data` ad_current
                  INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad_current.parent
                  INNER JOIN `tabAnthropromatic Data` ad_lyear ON 
                      ad_lyear.childenrollguid = ad_current.childenrollguid 
                      AND ad_lyear.do_you_have_height_weight = 1 
                      AND YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
                      AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
                      AND ad_current.weight <= ad_lyear.weight
                  INNER JOIN `tabAnthropromatic Data` ad_pyear ON 
                      ad_pyear.childenrollguid = ad_current.childenrollguid 
                      AND ad_pyear.do_you_have_height_weight = 1 
                      AND YEAR(ad_pyear.measurement_taken_date) = %(pyear)s 
                      AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s 
                      AND ad_lyear.weight <= ad_pyear.weight
                  WHERE ad_current.do_you_have_height_weight = 1  
                    AND YEAR(ad_current.measurement_taken_date) = %(year)s
                    AND MONTH(ad_current.measurement_taken_date) = %(month)s
              )
          )
        GROUP BY tcgm.creche_id
    ),
    
    -- CTE for red flag follow-ups (rff)
    rff AS (
        SELECT 
            cep.creche_id, 
            COUNT(cr.name) AS red_flag_f
        FROM `tabChild Referral` cr
        INNER JOIN `tabChild Enrollment and Exit` cep ON cep.childenrollguid = cr.childenrolledguid
        WHERE cep.date_of_enrollment <= %(end_date)s 
          AND (cep.date_of_exit IS NULL OR cep.date_of_exit >= %(start_date)s)
          AND YEAR(cr.date_of_referral) = %(year)s 
          AND MONTH(cr.date_of_referral) = %(month)s
        GROUP BY cep.creche_id
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
        COALESCE(SUM(tf.other_reason), 0) AS other_reason,
        COALESCE(SUM(tf.red_flag), 0) AS red_flag,
        COALESCE(SUM(tf.red_flag_f), 0) AS red_flag_f,
        COALESCE(SUM(tf.hf), 0) AS hf,
        COALESCE(SUM(tf.nrc), 0) AS nrc,
        COALESCE(SUM(tf.vhnd), 0) AS vhnd,
        COALESCE(SUM(tf.gf2), 0) AS gf2,
        COALESCE(SUM(tf.gf1), 0) AS gf1,
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
            COALESCE(mr.child_not_in_creche, 0) AS child_not_in_creche,
            COALESCE(mr.child_not_in_village, 0) AS child_not_in_village,
            COALESCE(mr.child_is_sick, 0) AS child_is_sick,
            COALESCE(mr.other_reason, 0) AS other_reason,
            COALESCE(rf.red_flag, 0) AS red_flag,
            COALESCE(rff.red_flag_f, 0) AS red_flag_f,
            COALESCE(h.hf, 0) AS hf,
            COALESCE(nr.nrc, 0) AS nrc,
            COALESCE(vhn.vhnd, 0) AS vhnd,
            COALESCE(gf2c.gf2, 0) AS gf2,
            COALESCE(gf1c.gf1, 0) AS gf1,
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
        LEFT JOIN mr ON c.name = mr.creche_id
        LEFT JOIN gf2c ON c.name = gf2c.creche_id
        LEFT JOIN gf1c ON c.name = gf1c.creche_id
        LEFT JOIN rf ON c.name = rf.creche_id
        LEFT JOIN rff ON c.name = rff.creche_id
        LEFT JOIN h ON c.name = h.creche_id
        LEFT JOIN nr ON c.name = nr.creche_id
        LEFT JOIN vhn ON c.name = vhn.creche_id
        LEFT JOIN cfu ON c.name = cfu.creche_id
        LEFT JOIN gmd ON c.name = gmd.creche_id
        LEFT JOIN gme ON c.name = gme.creche_id
        
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
    total_child_not_in_creche = sum(int(row.get('child_not_in_creche', 0) or 0) for row in data)
    total_child_not_in_village = sum(int(row.get('child_not_in_village', 0) or 0) for row in data)
    total_child_is_sick = sum(int(row.get('child_is_sick', 0) or 0) for row in data)
    total_other_reason = sum(int(row.get('other_reason', 0) or 0) for row in data)
    total_red_flag = sum(int(row.get('red_flag', 0) or 0) for row in data)
    total_red_flag_f = sum(int(row.get('red_flag_f', 0) or 0) for row in data)
    total_hf = sum(int(row.get('hf', 0) or 0) for row in data)
    total_nrc = sum(int(row.get('nrc', 0) or 0) for row in data)
    total_cfu = sum(int(row.get('cfu', 0) or 0) for row in data)
    total_vhnd = sum(int(row.get('vhnd', 0) or 0) for row in data)

    total_gf1 = sum(int(row.get('gf1', 0) or 0) for row in data)
    total_gf2 = sum(int(row.get('gf2', 0) or 0) for row in data)
    
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
    "other_reason": f"<b>{total_other_reason}</b>",
    "red_flag": f"<b>{total_red_flag}</b>",
    "red_flag_f": f"<b>{total_red_flag_f}</b>",
    "hf": f"<b>{total_hf}</b>",
    "nrc": f"<b>{total_nrc}</b>",
    "cfu": f"<b>{total_cfu}</b>",    
    "vhnd": f"<b>{total_vhnd}</b>",

    "gf1": f"<b>{total_gf1}</b>",
    "gf2": f"<b>{total_gf2}</b>",
   
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

#         {"label": "Growth Faltering 1", "fieldname": "gf1", "fieldtype": "Data", "width": 150},
#         {"label": "Growth Faltering 2", "fieldname": "gf2", "fieldtype": "Data", "width": 150},
        
        
#         {"label": "Red Flagged Children", "fieldname": "red_flag", "fieldtype": "Data", "width": 250},
#         {"label": "Red Flagged Children Home Visits Done", "fieldname": "red_flag_f", "fieldtype": "Data", "width": 300},

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


#     query = f"""
#     SELECT
#         {", ".join(selected_fields)},
#         COUNT(*) AS op_creches,
#         SUM(tf.gm_entered) AS gm_entered,
#         SUM(tf.e_children) AS e_children,
#         SUM(tf.g_children) AS g_children,
#         CASE 
#             WHEN COALESCE(SUM(tf.e_children), 0) = 0 THEN 0 
#             ELSE FORMAT(LEAST((SUM(tf.g_children) * 100.0) / SUM(tf.e_children), 100), 2) 
#         END AS e_children_percentage,
#         SUM(tf.red_flag) AS red_flag,
#         SUM(tf.red_flag_f) AS red_flag_f,
#         SUM(tf.hf) AS hf,
#         SUM(tf.nrc) AS nrc,
#         SUM(tf.vhnd) AS vhnd,
#         SUM(tf.gf2) AS gf2,
#         SUM(tf.gf1) AS gf1,
#         SUM(tf.cfu) AS cfu,
#         tf.creche_id AS creche_id,
#         tf.creche_opening_date AS cr_open_date,
        
#         SUM(tf.weight_for_age_normal) as weight_for_age_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_normal) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_weight_for_age_normal,

#         SUM(tf.weight_for_age_moderate) as weight_for_age_moderate,
#          CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_moderate) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_weight_for_age_moderate,

#         SUM(tf.weight_for_age_severe) as weight_for_age_severe,
#          CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_age_severe) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_weight_for_age_severe,
        
#         SUM(tf.height_for_age_normal) as height_for_age_normal,
#          CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_normal) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_height_for_age_normal,

#         SUM(tf.height_for_age_moderate) as height_for_age_moderate,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_moderate) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_height_for_age_moderate,

#         SUM(tf.height_for_age_severe) as height_for_age_severe,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.height_for_age_severe) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_height_for_age_severe,
        
#         SUM(tf.weight_for_height_normal) as weight_for_height_normal,
#         CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_normal) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_weight_for_height_normal,

#         SUM(tf.weight_for_height_moderate) as weight_for_height_moderate,
#          CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_moderate) * 100.0) / SUM(tf.g_children),2) 
#         END AS per_weight_for_height_moderate,

#         SUM(tf.weight_for_height_severe) as weight_for_height_severe,
#          CASE 
#             WHEN COALESCE(SUM(tf.g_children), 0) = 0 THEN 0 
#             ELSE FORMAT((SUM(tf.weight_for_height_severe) * 100.0) / SUM(tf.g_children),2) 
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
#             c.creche_id as creche_id,
#             DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date,
#             IFNULL(ec.e_children, 0) AS e_children,
#             IFNULL(gc.g_children, 0) AS g_children,
            
#             IFNULL(rf.red_flag, 0) AS red_flag,
#             IFNULL(rff.red_flag_f, 0) AS red_flag_f,
#             IFNULL(h.hf, 0) AS hf,
#             IFNULL(nr.nrc, 0) AS nrc,
#             IFNULL(vhn.vhnd, 0) AS vhnd,
#             IFNULL(gf2c.gf2, 0) AS gf2,
#             IFNULL(gf1c.gf1, 0) AS gf1,
#             IFNULL(cfu.cfu, 0) AS cfu,
#             IFNULL(gmd.weight_for_age_normal, 0) AS weight_for_age_normal,
#             IFNULL(gmd.weight_for_age_moderate, 0) AS weight_for_age_moderate,
#             IFNULL(gmd.weight_for_age_severe, 0) AS weight_for_age_severe,
#             IFNULL(gmd.height_for_age_normal, 0) AS height_for_age_normal,
#             IFNULL(gmd.height_for_age_moderate, 0) AS height_for_age_moderate,
#             IFNULL(gmd.height_for_age_severe, 0) AS height_for_age_severe,
#             IFNULL(gmd.weight_for_height_normal, 0) AS weight_for_height_normal,
#             IFNULL(gmd.weight_for_height_moderate, 0) AS weight_for_height_moderate,
#             IFNULL(gmd.weight_for_height_severe, 0) AS weight_for_height_severe,
#             IFNULL((gme.gm_entered), 0) AS gm_entered
            
#         FROM 
#             `tabCreche` AS c 
       
#         LEFT JOIN (
#             SELECT cee.creche_id, COUNT(*) AS e_children
#             FROM `tabChild Enrollment and Exit` cee
#             INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
#             WHERE  (cee.date_of_enrollment <=  %(end_date)s and 
#            (cee.date_of_exit IS null or cee.date_of_exit >= %(start_date)s))
#             GROUP BY cee.creche_id
#         ) AS ec ON c.name = ec.creche_id

#         LEFT JOIN (
#             SELECT cgm.creche_id, COUNT(*) AS g_children
#             FROM `tabAnthropromatic Data` as ad
#             LEFT JOIN `tabChild Growth Monitoring` AS cgm on cgm.name = ad.parent
#             LEFT JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
#             WHERE 
#                 ad.do_you_have_height_weight = 1 
#                 AND YEAR(cgm.measurement_date) = %(year)s
#                 AND MONTH(cgm.measurement_date) = %(month)s
#                 AND cee.date_of_enrollment <= %(end_date)s
#                 AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#             GROUP BY cgm.creche_id
#         ) AS gc ON c.name = gc.creche_id

#         LEFT JOIN (
            
#             SELECT cgm.creche_id as creche_id, COUNT(*) AS gf2
#             FROM 
#                 `tabAnthropromatic Data` AS ad
#             INNER JOIN 
#                 `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
#             JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
#             INNER JOIN
#                 `tabAnthropromatic Data` AS ad_lyear ON 
#                     ad_lyear.childenrollguid = ad.childenrollguid AND 
#                     ad_lyear.do_you_have_height_weight = 1 AND
#                     YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
#                     MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
#                     ad.weight <= ad_lyear.weight
#             INNER JOIN
#                 `tabAnthropromatic Data` AS ad_pyear ON 
#                     ad_pyear.childenrollguid = ad.childenrollguid AND 
#                     ad_pyear.do_you_have_height_weight = 1 AND
#                     YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
#                     MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
#                     ad_lyear.weight <= ad_pyear.weight
#             WHERE 
#                 ad.do_you_have_height_weight = 1 AND 
#                 YEAR(cgm.measurement_date) = %(year)s AND 
#                 MONTH(cgm.measurement_date) = %(month)s
#                 AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
#             GROUP BY 
#                 cgm.creche_id
#         ) AS gf2c ON c.name = gf2c.creche_id

#         LEFT JOIN  (
            
#             SELECT cgm.creche_id as creche_id, COUNT(*) AS gf1  
#             FROM 
#                 `tabAnthropromatic Data` AS ad
#             INNER JOIN 
#                 `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
#             INNER JOIN
#                 `tabAnthropromatic Data` AS ad_lyear ON 
#                     ad_lyear.childenrollguid = ad.childenrollguid AND 
#                     ad_lyear.do_you_have_height_weight = 1 AND
#                     YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
#                     MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
#                     ad.weight <= ad_lyear.weight
#             JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
#             LEFT JOIN
#                 `tabAnthropromatic Data` AS ad_pyear ON 
#                     ad_pyear.childenrollguid = ad.childenrollguid AND 
#                     ad_pyear.do_you_have_height_weight = 1 AND
#                     YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
#                     MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
#                     ad_lyear.weight <= ad_pyear.weight
#             WHERE 
#                 ad.do_you_have_height_weight = 1 AND 
#                 YEAR(cgm.measurement_date) = %(year)s AND 
#                 MONTH(cgm.measurement_date) = %(month)s
#                 AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
#                 AND ad_pyear.name IS NULL
#             GROUP BY 
#                 cgm.creche_id
#         ) AS gf1c ON c.name = gf1c.creche_id

#         LEFT JOIN (     
#             SELECT  
#                 tcgm.creche_id, 
#                 COUNT(ad.name) AS red_flag
#             FROM `tabAnthropromatic Data` AS ad
#             INNER JOIN `tabChild Growth Monitoring` tcgm 
#                 ON ad.parent = tcgm.name 
#             WHERE YEAR(measurement_taken_date) = %(year)s 
#             AND MONTH(measurement_taken_date) = %(month)s
#             AND (
#                     ad.weight_for_age = 1 
#                     OR ad.weight_for_height = 1
#                     OR ad.any_medical_major_illness = 1
#                     OR ad.childenrollguid IN (
#                         SELECT ad_current.childenrollguid 
#                         FROM `tabAnthropromatic Data` AS ad_current
#                         INNER JOIN `tabChild Growth Monitoring` AS cgm 
#                             ON cgm.name = ad_current.parent
#                         INNER JOIN `tabAnthropromatic Data` AS ad_lyear 
#                             ON ad_lyear.childenrollguid = ad_current.childenrollguid 
#                             AND ad_lyear.do_you_have_height_weight = 1 
#                             AND YEAR(ad_lyear.measurement_taken_date) = %(lyear)s 
#                             AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s 
#                             AND ad_current.weight <= ad_lyear.weight
#                         INNER JOIN `tabAnthropromatic Data` AS ad_pyear 
#                             ON ad_pyear.childenrollguid = ad_current.childenrollguid 
#                             AND ad_pyear.do_you_have_height_weight = 1 
#                             AND YEAR(ad_pyear.measurement_taken_date) = %(pyear)s 
#                             AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s 
#                             AND ad_lyear.weight <= ad_pyear.weight
#                         WHERE ad_current.do_you_have_height_weight = 1  
#                         AND YEAR(ad_current.measurement_taken_date) = %(year)s
#                         AND MONTH(ad_current.measurement_taken_date) = %(month)s
#                     )
#                 )
#             GROUP BY tcgm.creche_id
#         ) AS rf ON c.name = rf.creche_id


#         LEFT JOIN (
#             SELECT cep.creche_id, COUNT(cr.name) AS red_flag_f
#             FROM `tabChild Referral` as cr
#             INNER JOIN `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
#             WHERE date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit  >=  %(start_date)s)
#             AND YEAR(cr.date_of_referral) = %(year)s AND MONTH(cr.date_of_referral) = %(month)s
#             GROUP BY cep.creche_id
#         ) AS rff ON c.name = rff.creche_id

#         LEFT JOIN (
#             SELECT 
#                 cep.creche_id, 
#                 COUNT(cr.name) AS hf
#             FROM `tabChild Referral` as cr
#             INNER JOIN `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
#             WHERE date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit  >=  %(start_date)s)
#                 AND cr.referred_to !=1 AND YEAR(cr.date_of_referral) = %(year)s AND MONTH(cr.date_of_referral) = %(month)s
#             GROUP BY cep.creche_id
#         ) AS h ON c.name = h.creche_id

#         LEFT JOIN (
#             SELECT 
#                 cep.creche_id, 
#                 COUNT(cr.name) AS nrc
#             FROM `tabChild Referral` as cr
#             INNER JOIN `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
#             WHERE date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit  >=  %(start_date)s)
#                 AND cr.referred_to = 4 AND YEAR(cr.date_of_referral) = %(year)s AND MONTH(cr.date_of_referral) = %(month)s
#             GROUP BY cep.creche_id
#         ) AS nr ON c.name = nr.creche_id
        
#         LEFT JOIN (
#             SELECT 
#                 cep.creche_id, 
#                 COUNT(vh.name) AS vhnd
#             FROM `tabChild Referral` as vh
#             INNER JOIN `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = vh.childenrolledguid
#             WHERE date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit  >=  %(start_date)s)
#                 AND vh.referred_to = 1 AND YEAR(vh.date_of_referral) = %(year)s AND MONTH(vh.date_of_referral) = %(month)s
#             GROUP BY cep.creche_id
#         ) AS vhn ON c.name = vhn.creche_id

#         LEFT JOIN (
#             SELECT 
#                 cep.creche_id, 
#                 COUNT(cr.name) AS cfu
#             FROM `tabChild Follow up` as cr
#             INNER JOIN `tabChild Enrollment and Exit` AS cep on cep.childenrollguid = cr.childenrolledguid
#             WHERE date_of_enrollment <= %(end_date)s and (date_of_exit IS null or date_of_exit  >=  %(start_date)s)
#                 AND YEAR(cr.followup_visit_date) = %(year)s AND MONTH(cr.followup_visit_date) = %(month)s
#             GROUP BY cep.creche_id
#         ) AS cfu ON c.name = cfu.creche_id
        
#         LEFT JOIN (
#             SELECT 
#                 cgm.creche_id,
#                 COUNT(CASE WHEN ad.weight_for_age = 3 THEN 1 END) AS weight_for_age_normal,
#                 COUNT(CASE WHEN ad.weight_for_age = 2 THEN 1 END) AS weight_for_age_moderate,
#                 COUNT(CASE WHEN ad.weight_for_age = 1 THEN 1 END) AS weight_for_age_severe,
                
#                 COUNT(CASE WHEN ad.height_for_age = 3 THEN 1 END) AS height_for_age_normal,
#                 COUNT(CASE WHEN ad.height_for_age = 2 THEN 1 END) AS height_for_age_moderate,
#                 COUNT(CASE WHEN ad.height_for_age = 1 THEN 1 END) AS height_for_age_severe,
                
#                 COUNT(CASE WHEN ad.weight_for_height = 3 THEN 1 END) AS weight_for_height_normal,
#                 COUNT(CASE WHEN ad.weight_for_height = 2 THEN 1 END) AS weight_for_height_moderate,
#                 COUNT(CASE WHEN ad.weight_for_height = 1 THEN 1 END) AS weight_for_height_severe
#             FROM 
#                 `tabAnthropromatic Data` ad
#             INNER JOIN 
#                 `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
#             INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
#             WHERE ad.do_you_have_height_weight = 1 AND YEAR(cgm.measurement_date) = %(year)s AND MONTH(cgm.measurement_date) = %(month)s
#             AND cee.date_of_enrollment <= %(end_date)s
#             AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#             GROUP BY cgm.creche_id
#         ) AS gmd ON c.name = gmd.creche_id
#         LEFT JOIN (
# 								SELECT cr.name AS creche_id, 
# 											COUNT(cgm.creche_id) AS gm_entered
# 								FROM `tabCreche` AS cr
# 								LEFT JOIN `tabChild Growth Monitoring` AS cgm ON cr.name = cgm.creche_id
# 								WHERE YEAR(cgm.measurement_date) =  %(year)s AND MONTH(cgm.measurement_date) = %(month)s            
# 								GROUP BY cr.name
#         ) AS gme ON gme.creche_id = c.name
        
#         JOIN `tabState` AS s ON c.state_id = s.name 
#         JOIN `tabDistrict` AS d ON c.district_id = d.name
#         JOIN `tabBlock` AS b ON c.block_id = b.name
#         JOIN `tabGram Panchayat` AS g ON c.gp_id = g.name
#         JOIN `tabVillage` AS v ON c.village_id = v.name
#         JOIN `tabPartner` AS p ON c.partner_id = p.name 
#         JOIN `tabUser` AS u ON u.name = c.supervisor_id
#         WHERE {where_clause} AND (
#             (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
#             OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
#         )
#     ) AS tf
    
#     GROUP BY {group_by_field}
#     ORDER BY {group_by_field}


#     """
#     data = frappe.db.sql(query, params, as_dict=True)
#     # total_e_children = sum(row.get('e_children', 0) for row in data)
#     # total_gm_done_children = sum(row.get('g_children', 0) for row in data)
#     # total_red_flag_children = sum(row.get('red_flag', 0) for row in data)
#     # total_red_flag_f_children = sum(row.get('red_flag_f', 0) for row in data)  
#     # total_hf = sum(row.get('hf', 0) for row in data)
#     # total_nrc = sum(row.get('nrc', 0) for row in data)
#     # total_cfu = sum(row.get('cfu', 0) for row in data)
    
#     total_act_creches = sum(int(row.get('op_creches', 0) or 0) for row in data)
#     total_gm_entered = sum(int(row.get('gm_entered', 0) or 0) for row in data)
#     total_e_children = sum(int(row.get('e_children', 0) or 0) for row in data)
#     total_e_children = sum(int(row.get('e_children', 0) or 0) for row in data)
#     total_g_children = sum(int(row.get('g_children', 0) or 0) for row in data)
#     total_red_flag = sum(int(row.get('red_flag', 0) or 0) for row in data)
#     total_red_flag_f = sum(int(row.get('red_flag_f', 0) or 0) for row in data)
#     total_hf = sum(int(row.get('hf', 0) or 0) for row in data)
#     total_nrc = sum(int(row.get('nrc', 0) or 0) for row in data)
#     total_cfu = sum(int(row.get('cfu', 0) or 0) for row in data)
#     total_vhnd = sum(int(row.get('vhnd', 0) or 0) for row in data)

#     total_gf1 = sum(int(row.get('gf1', 0) or 0) for row in data)
#     total_gf2 = sum(int(row.get('gf2', 0) or 0) for row in data)
    
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

#     "red_flag": f"<b>{total_red_flag}</b>",
#     "red_flag_f": f"<b>{total_red_flag_f}</b>",
#     "hf": f"<b>{total_hf}</b>",
#     "nrc": f"<b>{total_nrc}</b>",
#     "cfu": f"<b>{total_cfu}</b>",    
#     "vhnd": f"<b>{total_vhnd}</b>",

#     "gf1": f"<b>{total_gf1}</b>",
#     "gf2": f"<b>{total_gf2}</b>",
   
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


