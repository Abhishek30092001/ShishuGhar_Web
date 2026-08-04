import frappe
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date

def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)
    return columns, data

def get_columns():
    columns = [
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
        {"label": "Age (At enrollment)", "fieldname": "age", "fieldtype": "Data", "width": 180},
        {"label": "Current Age", "fieldname": "current_age", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
        {"label": "Height (cm)", "fieldname": "height", "fieldtype": "Data", "width": 130},
        {"label": "Weight (kg)", "fieldname": "weight", "fieldtype": "Data", "width": 130},
        {"label": "Measurement Date", "fieldname": "measurements_taken_date", "fieldtype": "Data", "width": 200},
        {"label": "Measurement Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 180},
        {"label": "Measurement Not Taken", "fieldname": "measurement_reason", "fieldtype": "Data", "width": 200},

        # {"label": "Weight for Age", "fieldname": "weight_for_age_status", "fieldtype": "Data", "width": 150},
        # {"label": "Weight for Height", "fieldname": "weight_for_height_status", "fieldtype": "Data", "width": 150},
        # {"label": "Height for Age", "fieldname": "height_for_age_status", "fieldtype": "Data", "width": 150},

        {"label": "Weight for Age (Z-score)", "fieldname": "weight_for_age_zscore", "fieldtype": "Data", "width": 200},
        {"label": "Weight for Height (Z-score)", "fieldname": "weight_for_height_zscore", "fieldtype": "Data", "width": 210},
        {"label": "Height for Age (Z-score)", "fieldname": "height_for_age_zscore", "fieldtype": "Data", "width": 200},

        {"label": "Growth Faltering 1", "fieldname": "growth_faltering_1", "fieldtype": "Data", "width": 160 , "align": "center"},
        {"label": "Growth Faltering 2", "fieldname": "growth_faltering_2", "fieldtype": "Data", "width": 160, "align": "center"},
        {"label": "Medical Complication ", "fieldname": "any_medical_major_illness", "fieldtype": "Data", "width": 170, "align": "center"},

        {"label": "Red Flag", "fieldname": "red_flag", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": "Home Visit", "fieldname": "red_flag_HV", "fieldtype": "Data", "width": 100, "align": "center"},
        {"label": "Followup", "fieldname": "follow_up", "fieldtype": "Data", "width": 120},
        {"label": "Taken to VHND", "fieldname": "vhsnd", "fieldtype": "Data", "width": 140},
        {"label": "Taken to PHC", "fieldname": "phc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to CHC", "fieldname": "chc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to NRC", "fieldname": "nrc", "fieldtype": "Data", "width": 120},
        {"label": "Taken to other Health Facility", "fieldname": "othr", "fieldtype": "Data", "width": 250}
    ]
    
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    # Date range setup
    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # Calculate previous months for growth faltering comparison
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

    # Initialize parameters
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
        "supervisor_id": None,
        "creche_status_id": None,
        "phases": None
    }

    # Get user's partner and geography mapping
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    # Get user's geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    # Handle creche opening date filters
    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            params['cstart_date'], params['cend_date'] = date_range
        elif range_type == "before" and single_date:
            params['cstart_date'] = date(2017, 1, 1)
            params['cend_date'] = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            params['cstart_date'] = single_date + timedelta(days=1)
            params['cend_date'] = date.today()
        elif range_type == "equal" and single_date:
            params['cstart_date'] = single_date

    # Apply filters
    if partner_id:
        params["partner"] = partner_id
    
    # Geography filters
    if filters.get("state"):
        params["state"] = filters.get("state")
    else:
        state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
        if state_ids:
            params["state_ids"] = ",".join(state_ids)

    if filters.get("district"):
        params["district"] = filters.get("district")
    else:
        district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
        if district_ids:
            params["district_ids"] = ",".join(district_ids)

    if filters.get("block"):
        params["block"] = filters.get("block")
    else:
        block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
        if block_ids:
            params["block_ids"] = ",".join(block_ids)

    if filters.get("gp"):
        params["gp"] = filters.get("gp")
    else:
        gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
        if gp_ids:
            params["gp_ids"] = ",".join(gp_ids)

    # Other filters
    if filters.get("creche"):
        params["creche"] = filters.get("creche")
    
    if filters.get("supervisor_id"):
        params["supervisor_id"] = filters.get("supervisor_id")
    
    if filters.get("creche_status_id"):
        params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            params["phases"] = phases_cleaned

    # Build conditions for geography filters
    conditions = []
    
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

    # Handle creche opening date conditions
    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"):  # For equal date case
        conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql_query = f"""
        SELECT DISTINCT
            cr.creche_name AS 'creche_name',
            usr.full_name AS 'supervisor',
            cee.child_id AS 'child_id',
            cr.creche_id AS 'creche_id',
            cee.child_name AS 'child_name',
            cee.age_at_enrollment_in_months AS 'age',
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS 'child_dob',
            CASE 
                WHEN DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m')
                THEN TIMESTAMPDIFF(MONTH, cee.child_dob, CURDATE())
                ELSE TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s)
            END AS current_age,

            (CASE 
                WHEN cee.gender_id = '1' THEN 'M' 
                WHEN cee.gender_id = '2' THEN 'F' 
                ELSE cee.gender_id 
            END) AS gender,
            ad.height AS 'height',
            ad.weight AS 'weight',
            ad.do_you_have_height_weight AS 'measurements_taken_raw',
            IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS 'measurements_taken',
            IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS 'measurements_taken_date',
            
            CASE 
                WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
                WHEN ad.measurement_reason = 2 THEN 'Child not in village'
                WHEN ad.measurement_reason = 3 THEN 'Child is sick'
                WHEN ad.measurement_reason = 4 THEN 'Others'
                ELSE ''
            END AS 'measurement_reason',
            
            CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
                CASE WHEN ad.childenrollguid IN (
                        SELECT 
                            ad_current.childenrollguid 
                        FROM 
                            `tabAnthropromatic Data` AS ad_current
                        INNER JOIN 
                            `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
                        INNER JOIN
                            `tabAnthropromatic Data` AS ad_lyear ON 
                                ad_lyear.childenrollguid = ad_current.childenrollguid AND 
                                ad_lyear.do_you_have_height_weight = 1 AND
                                YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                                MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                                ad_current.weight <= ad_lyear.weight
                        LEFT JOIN
                            `tabAnthropromatic Data` AS ad_pyear ON 
                                ad_pyear.childenrollguid = ad_current.childenrollguid AND 
                                ad_pyear.do_you_have_height_weight = 1 AND
                                YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                                MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                                ad_lyear.weight <= ad_pyear.weight
                        WHERE 
                            ad_current.do_you_have_height_weight = 1 AND 
                            YEAR(cgm.measurement_date) = %(year)s AND 
                            MONTH(cgm.measurement_date) = %(month)s AND
                            ad_pyear.name IS NULL
                    ) THEN 'Y'
                    ELSE 'N' 
                END 
            END AS 'growth_faltering_1',

            CASE WHEN ad.do_you_have_height_weight = 0 THEN 'N' ELSE
                CASE WHEN ad.childenrollguid IN (
                        SELECT 
                            ad_current.childenrollguid 
                        FROM 
                            `tabAnthropromatic Data` AS ad_current
                        INNER JOIN 
                            `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
                        INNER JOIN
                            `tabAnthropromatic Data` AS ad_lyear ON 
                                ad_lyear.childenrollguid = ad_current.childenrollguid AND 
                                ad_lyear.do_you_have_height_weight = 1 AND
                                YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                                MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                                ad_current.weight <= ad_lyear.weight
                        INNER JOIN
                            `tabAnthropromatic Data` AS ad_pyear ON 
                                ad_pyear.childenrollguid = ad_current.childenrollguid AND 
                                ad_pyear.do_you_have_height_weight = 1 AND
                                YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                                MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                                ad_lyear.weight <= ad_pyear.weight
                        WHERE ad_current.do_you_have_height_weight = 1  
                        AND YEAR(ad_current.measurement_taken_date) = %(year)s
                        AND MONTH(ad_current.measurement_taken_date) = %(month)s
                    ) THEN 'Y'
                    ELSE 'N'
                END 
            END AS 'growth_faltering_2',
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            cfud.follow_up AS follow_up,
            ad.any_medical_major_illness AS any_medical_major_illness,
            CASE 
                WHEN crfd.date_of_referral IS NOT NULL
                THEN 'Y' 
                ELSE '-' 
            END AS red_flag_HV,
            IFNULL(
                CASE 
                    WHEN crfd.referred_to = 5
                    THEN 'Y' 
                    ELSE '-' 
                END, '-'
            ) AS othr,
            CASE 
                WHEN crfd.referred_to = 4 
                THEN 'Y' 
                ELSE '-' 
            END AS nrc, 
            CASE 
                WHEN crfd.referred_to = 3 
                THEN 'Y' 
                ELSE '-' 
            END AS chc, 
            CASE 
                WHEN crfd.referred_to = 2
                THEN 'Y' 
                ELSE '-' 
            END AS phc,
            CASE 
                WHEN crfd.referred_to = 1 
                THEN 'Y' 
                ELSE '-' 
            END AS vhsnd, 

            CASE 
                WHEN (ad.weight_for_age = 1 
                    OR ad.weight_for_height = 1
                    OR ad.any_medical_major_illness = 1
                    OR ad.childenrollguid IN (
                        SELECT 
                            ad_current.childenrollguid 
                        FROM 
                            `tabAnthropromatic Data` AS ad_current
                        INNER JOIN 
                            `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
                        INNER JOIN
                            `tabAnthropromatic Data` AS ad_lyear ON 
                                ad_lyear.childenrollguid = ad_current.childenrollguid AND 
                                ad_lyear.do_you_have_height_weight = 1 AND
                                YEAR(ad_lyear.measurement_taken_date) = %(lyear)s AND 
                                MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s AND
                                ad_current.weight <= ad_lyear.weight
                        INNER JOIN
                            `tabAnthropromatic Data` AS ad_pyear ON 
                                ad_pyear.childenrollguid = ad_current.childenrollguid AND 
                                ad_pyear.do_you_have_height_weight = 1 AND
                                YEAR(ad_pyear.measurement_taken_date) = %(pyear)s AND 
                                MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s AND
                                ad_lyear.weight <= ad_pyear.weight
                        WHERE ad_current.do_you_have_height_weight = 1  
                        AND YEAR(ad_current.measurement_taken_date) = %(year)s
                        AND MONTH(ad_current.measurement_taken_date) = %(month)s
                    ))
                THEN 'Y' 
                ELSE 'N' 
            END AS red_flag,

            -- Weight for Age
            CASE 
                WHEN ad.weight_for_age = 3 THEN 'Normal'
                WHEN ad.weight_for_age = 2 THEN 'Moderate'
                WHEN ad.weight_for_age = 1 THEN 'Severe'
                ELSE '' 
            END AS weight_for_age_status,
            
            -- Height for Age
            CASE 
                WHEN ad.height = 0 THEN '-'
                WHEN ad.height_for_age = 3 THEN 'Normal'
                WHEN ad.height_for_age = 2 THEN 'Moderate'
                WHEN ad.height_for_age = 1 THEN 'Severe'
                ELSE '' 
            END AS height_for_age_status,
            
            -- Weight for Height
            CASE 
                WHEN ad.height = 0 THEN '-'
                WHEN ad.weight_for_height = 3 THEN 'Normal'
                WHEN ad.weight_for_height = 2 THEN 'Moderate'
                WHEN ad.weight_for_height = 1 THEN 'Severe'
                ELSE '' 
            END AS weight_for_height_status,
        ad.weight_for_age_zscore AS weight_for_age_zscore,
        ad.weight_for_height_zscore AS weight_for_height_zscore,
        ad.height_for_age_zscore AS height_for_age_zscore
        FROM  
            `tabAnthropromatic Data` AS ad 
        INNER JOIN 
            `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
        INNER JOIN 
            `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid 
        INNER JOIN 
            `tabCreche` AS cr ON cgm.creche_id = cr.name 
        INNER JOIN 
            `tabUser` AS usr ON cr.supervisor_id = usr.name 
        INNER JOIN 
            `tabPartner` AS p ON p.name = cr.partner_id
        INNER JOIN 
            `tabState` AS s ON s.name = cr.state_id
        INNER JOIN 
            `tabDistrict` AS d ON d.name = cr.district_id
        INNER JOIN 
            `tabBlock` AS b ON b.name = cr.block_id
        INNER JOIN 
            `tabGram Panchayat` AS g ON g.name = cr.gp_id
        LEFT JOIN (
            SELECT
                crf.childenrolledguid,
                crf.date_of_referral,
                crf.referred_to
            FROM
                `tabChild Referral` AS crf 
            WHERE 
                YEAR(crf.date_of_referral) = %(year)s
                AND MONTH(crf.date_of_referral) = %(month)s
                AND (%(partner)s IS NULL OR crf.partner_id = %(partner)s) 
                AND (%(state)s IS NULL OR crf.state_id = %(state)s) 
                AND (%(district)s IS NULL OR crf.district_id = %(district)s)
                AND (%(block)s IS NULL OR crf.block_id = %(block)s)
                AND (%(gp)s IS NULL OR crf.gp_id = %(gp)s) 
                AND (%(creche)s IS NULL OR crf.creche_id = %(creche)s)
            ) as crfd ON crfd.childenrolledguid = ad.childenrollguid
        LEFT JOIN(
            SELECT
            cfu.childenrolledguid,
            CASE WHEN cfu.followup_visit_date THEN 'Y' ELSE '-' END AS follow_up 
            FROM
                `tabChild Follow up` AS cfu 
            WHERE YEAR(cfu.followup_visit_date) = %(year)s
                AND MONTH(cfu.followup_visit_date) = %(month)s
                AND (%(partner)s IS NULL OR cfu.partner_id = %(partner)s) 
                AND (%(state)s IS NULL OR cfu.state_id = %(state)s) 
                AND (%(district)s IS NULL OR cfu.district_id = %(district)s)
                AND (%(block)s IS NULL OR cfu.block_id = %(block)s)
                AND (%(gp)s IS NULL OR cfu.gp_id = %(gp)s) 
                AND (%(creche)s IS NULL OR cfu.creche_id = %(creche)s)
            ) as cfud ON cfud.childenrolledguid = ad.childenrollguid
        WHERE 
            YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
            AND {where_clause}
        ORDER BY
            cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id, cr.supervisor_id, cr.name, cee.child_name;
    """
    
    data = frappe.db.sql(sql_query, params, as_dict=True)


    for row in data:
        # Format Weight for Age Z-score
        if 'weight_for_age_zscore' in row and row['weight_for_age_zscore'] is not None:
            status = row.get('weight_for_age_status', '').lower()
            row['weight_for_age_zscore'] = format_zscore_cell(row['weight_for_age_zscore'], status)
        
        # Format Weight for Height Z-score
        if 'weight_for_height_zscore' in row and row['weight_for_height_zscore'] is not None:
            status = row.get('weight_for_height_status', '').lower()
            row['weight_for_height_zscore'] = format_zscore_cell(row['weight_for_height_zscore'], status)
        
        # Format Height for Age Z-score
        if 'height_for_age_zscore' in row and row['height_for_age_zscore'] is not None:
            status = row.get('height_for_age_status', '').lower()
            row['height_for_age_zscore'] = format_zscore_cell(row['height_for_age_zscore'], status)

    # Calculate summary counts
    counts = {
        "child_name": 0,
        "measurements_taken": 0,
        "growth_faltering_1": 0,
        "growth_faltering_2": 0,
        "nrc": 0,
        "chc": 0,
        "vhsnd": 0,
        "follow_up": 0,
        "red_flag": 0,
        "red_flag_HV": 0,
        "phc": 0,
        "any_medical_major_illness": 0,
        "othr": 0
    }

    for row in data:
        # Initialize all expected keys with default values if they don't exist
        row.setdefault("othr", "-")
        row.setdefault("nrc", "-")
        row.setdefault("chc", "-")
        row.setdefault("vhsnd", "-")
        row.setdefault("follow_up", "-")
        row.setdefault("red_flag", "-")
        row.setdefault("red_flag_HV", "-")
        row.setdefault("phc", "-")
        row.setdefault("any_medical_major_illness", 0)

        counts["child_name"] += 1 
        if row.get("measurements_taken_raw") == 1:  # Changed to use raw value for counting
            counts["measurements_taken"] += 1
        if row.get("growth_faltering_1") == "Y":
            counts["growth_faltering_1"] += 1
        if row.get("growth_faltering_2") == "Y":
            counts["growth_faltering_2"] += 1
        if row.get("nrc") == "Y":
            counts["nrc"] += 1
        if row.get("phc") == "Y":
            counts["phc"] += 1
        if row.get("red_flag_HV") == "Y":
            counts["red_flag_HV"] += 1
        if row.get("othr") == "Y":
            counts["othr"] += 1
        if row.get("chc") == "Y":
            counts["chc"] += 1
        if row.get("vhsnd") == "Y":
            counts["vhsnd"] += 1
        if row.get("follow_up") == "Y":
            counts["follow_up"] += 1
        if row.get("red_flag") == "Y":
            counts["red_flag"] += 1
        if row.get("any_medical_major_illness") == 1:
            counts["any_medical_major_illness"] += 1

    # Add summary row
    summary_row = {
        "partner": "<b style='color:black;'>Total</b>",
        "child_name": counts['child_name'],
        "measurements_taken": counts['measurements_taken'],
        "growth_faltering_1": counts['growth_faltering_1'],
        "growth_faltering_2": counts['growth_faltering_2'],
        "nrc": counts['nrc'],
        "chc": counts['chc'],
        "vhsnd": counts['vhsnd'],
        "follow_up": counts['follow_up'],
        "phc": counts['phc'],
        "red_flag_HV": counts['red_flag_HV'],
        "red_flag": counts['red_flag'],
        "any_medical_major_illness": counts['any_medical_major_illness'],
        "othr": counts['othr']
    }
    data.append(summary_row)

    return data


def format_zscore_cell(value, status):
    """Format Z-score cell with color based on status"""
    if status == 'severe':
        return format_cell(value, "#FFCCCC", "#CC0000")  # Light red background, dark red text
    elif status == 'moderate':
        return format_cell(value, "#FFFFCC", "#999900")  # Light yellow background, dark yellow text
    elif status == 'normal':
        return format_cell(value, "#CCFFCC", "#006600")  # Light green background, dark green text
    else:
        return value  # Return as-is for unknown statuses

def format_cell(value, bg_color, text_color):
    """Helper function to format a cell with background and text color"""
    if value is None:
        return ""
    return f"""
        <div style='
            background-color: {bg_color};
            color: {text_color};
            border-radius: 3px;
            text-align: center;
            font-weight: bold;
            padding: 2px 5px;
        '>
            {value}
        </div>
    """