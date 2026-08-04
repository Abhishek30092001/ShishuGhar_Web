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
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 150},
        {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 140},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": "Date of Birth", "fieldname": "date_of_birth", "fieldtype": "Data", "width": 120},

        {"label": "Date of Enrollment", "fieldname": "date_of_enrolment", "fieldtype": "Data", "width": 180},
        {"label": "Current Age", "fieldname": "current_age", "fieldtype": "Data", "width": 150},
        {"label": "Age (At Enrollment)", "fieldname": "age_at_enrolment", "fieldtype": "Data", "width": 180},
        {"label": "Date of Exit", "fieldname": "date_of_exit", "fieldtype": "Data", "width": 120},
        {"label": "Age (At Exit)", "fieldname": "age_at_exit", "fieldtype": "Data", "width": 120},
        {"label": "Is the child enrolled in AWC after 3 years for preschool?", "fieldname": "enrolled_in_awc", "fieldtype": "Data", "width": 400},
        {"label": "Date of Measurement (At Enrollment)", "fieldname": "date_of_measurement_enrolment", "fieldtype": "Data", "width": 300},
        {"label": "Measurement Equipment (At Enrollment)", "fieldname": "measurement_equipment_enrolment", "fieldtype": "Data", "width": 310},
        {"label": "Measurement Position (At Enrollment)", "fieldname": "measurement_position_enrolment", "fieldtype": "Data", "width": 300},
        {"label": "Weight (At Enrollment)", "fieldname": "weight_enrolment", "fieldtype": "Data", "width": 200},
        {"label": "Height (At Enrollment)", "fieldname": "height_enrolment", "fieldtype": "Data", "width": 200},
        {"label": "Date of Measurement (At Exit)", "fieldname": "date_of_measurement_exit", "fieldtype": "Data", "width": 250},
        {"label": "Measurement Equipment (At Exit)", "fieldname": "measurement_equipment_exit", "fieldtype": "Data", "width": 240},
        {"label": "Measurement Position (At Exit)", "fieldname": "measurement_position_exit", "fieldtype": "Data", "width": 240},
        {"label": "Weight (At Exit)", "fieldname": "weight_exit", "fieldtype": "Data", "width": 170},
        {"label": "Height (At Exit)", "fieldname": "height_exit", "fieldtype": "Data", "width": 170},
        {"label": "Is Exited", "fieldname": "is_exited", "fieldtype": "Data", "width": 150},
        {"label": "Reason for Exit", "fieldname": "reason_for_exit", "fieldtype": "Data", "width": 150},
        {"label": "Reason for Exit Other", "fieldname": "reason_for_exit_other", "fieldtype": "Data", "width": 200},
    ]


@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    params = prepare_parameters(filters)
    where_clause = build_where_clause(filters, params)
    data = execute_main_query(params, where_clause)
    
    return data


def prepare_parameters(filters):
    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day) # End date is generated here based on Month/Year filters
    
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
        "end_date": end_date, # Passed to the query via params
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
        "creche_age": None,
        "is_exited": None, 
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
    if filters.get("creche_age"):
        params["creche_age"] = filters.get("creche_age")
    if filters.get("is_exited"):
        params["is_exited"] = filters.get("is_exited")
    
    return params


def build_where_clause(filters, params):
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
    if params.get("creche_age"):
        conditions.append("""
            CASE
                WHEN cr.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                ELSE ''
            END = %(creche_age)s
        """)
    if params.get("is_exited"):
        conditions.append("cee.date_of_exit IS NOT NULL")
    
    return " AND ".join(conditions)


def execute_main_query(params, where_clause):
    sql_query = """
        SELECT 
            s.state_name AS state,
            p.partner_name AS partner,
            d.district_name AS district,
            b.block_name AS block,
            usr.full_name AS supervisor,
            cr.creche_name AS creche_name,

            cee.child_id AS child_id,
            cee.child_name AS child_name,

            -- Gender
            CASE 
                WHEN cee.gender_id = 1 THEN 'M'
                WHEN cee.gender_id = 2 THEN 'F'
                ELSE 'Other'
            END AS gender,

            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS date_of_birth,
            
            -- Current Age (calculated dynamically against %(end_date)s generated from filters)
            CASE 
                WHEN cee.child_dob IS NOT NULL
                THEN CONCAT(
                    TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s), 
                    ' (', 
                    TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s), 
                    ')'
                )
                ELSE NULL
            END AS current_age,

            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS date_of_enrolment,
            
            -- Age at Enrollment: Months (Days)
            CASE 
                WHEN cee.date_of_enrollment IS NOT NULL AND cee.child_dob IS NOT NULL
                THEN CONCAT(
                    TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment), 
                    ' (', 
                    TIMESTAMPDIFF(DAY, cee.child_dob, cee.date_of_enrollment), 
                    ')'
                )
                ELSE NULL
            END AS age_at_enrolment,

            DATE_FORMAT(cee.date_of_exit, '%%d-%%m-%%Y') AS date_of_exit,

            -- Age at Exit: Months (Days)
            CASE 
                WHEN cee.date_of_exit IS NOT NULL AND cee.child_dob IS NOT NULL
                THEN CONCAT(
                    TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_exit), 
                    ' (', 
                    TIMESTAMPDIFF(DAY, cee.child_dob, cee.date_of_exit), 
                    ')'
                )
                ELSE NULL
            END AS age_at_exit,

            CASE 
                WHEN cee.is_child_enrolled_awc = 1 THEN 'Yes' 
                ELSE 'No' 
            END AS enrolled_in_awc,

            DATE_FORMAT(cee.measurement_date, '%%d-%%m-%%Y') AS date_of_measurement_enrolment,

            CASE 
                WHEN cee.measurement_equipment = 1 THEN 'Stadiometer'
                WHEN cee.measurement_equipment = 2 THEN 'Infantometer'
                ELSE '-'
            END AS measurement_equipment_enrolment,
            
            CASE 
                WHEN cee.measurement_equipment = 1 THEN 'Standing'
                WHEN cee.measurement_equipment = 2 THEN 'Lying'
                ELSE '-'
            END AS measurement_position_enrolment,
            
            COALESCE(FORMAT(NULLIF(cee.weight, 0), 2), '-') AS weight_enrolment,
            COALESCE(FORMAT(NULLIF(cee.height, 0), 2), '-') AS height_enrolment,

            CASE 
                WHEN cee.measurement_equipment_exit = 1 THEN 'Stadiometer'
                WHEN cee.measurement_equipment_exit = 2 THEN 'Infantometer'
                ELSE '-'
            END AS measurement_equipment_exit,
            
            CASE 
                WHEN cee.measurement_equipment_exit = 1 THEN 'Standing'
                WHEN cee.measurement_equipment_exit = 2 THEN 'Lying'
                ELSE '-'
            END AS measurement_position_exit,

            COALESCE(FORMAT(NULLIF(cee.weight_exit, 0), 2), '-') AS weight_exit,
            COALESCE(FORMAT(NULLIF(cee.height_exit, 0), 2), '-') AS height_exit,

            -- Exit flag
            CASE
                WHEN cee.date_of_exit IS NOT NULL THEN 'Yes'
                ELSE 'No'
            END AS is_exited,

            CASE
                WHEN cee.reason_for_exit = 1 THEN 'Migrated'
                WHEN cee.reason_for_exit = 2 THEN 'Graduated'
                WHEN cee.reason_for_exit = 3 THEN 'Not willing to stay'
                WHEN cee.reason_for_exit = 4 THEN 'Death'
                WHEN cee.reason_for_exit = 5 THEN 'Other'
                ELSE '-'
            END AS reason_for_exit,

            CASE
                WHEN cee.reason_for_exit = 5 THEN COALESCE(cee.other_reason, '-')
                ELSE '-'
            END AS reason_for_exit_other

        FROM 
            `tabChild Enrollment and Exit` cee

        INNER JOIN `tabCreche` cr ON cee.creche_id = cr.name
        INNER JOIN `tabUser` usr ON cr.supervisor_id = usr.name
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id

        WHERE 
            {where_clause}
    """.format(where_clause=where_clause)
    
    return frappe.db.sql(sql_query, params, as_dict=True)




