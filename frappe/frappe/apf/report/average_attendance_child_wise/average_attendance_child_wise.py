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
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 150},
        {"label": "Child Name", "fieldname": "name", "fieldtype": "Data", "width": 160},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Age (At the time of enrollment)", "fieldname": "age", "fieldtype": "Data", "width": 212},
        {"label": "Date of Enrollment", "fieldname": "date_of_enrollments", "fieldtype": "Date", "width": 160},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 85},
        {"label": "Eligible Open Days", "fieldname": "eligible_open_days", "fieldtype": "Data", "width": 150},
        {"label": "Days Attended", "fieldname": "days_attended", "fieldtype": "Data", "width": 130},
        {"label": "Attendance (%)", "fieldname": "attendance_percentage", "fieldtype": "Data", "width": 130, "align": "right"}
    ]
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    # Date range setup
    month = int(filters.get("month") if filters.get("month") else nowdate().split('-')[1])
    year = int(filters.get("year") if filters.get("year") else nowdate().split('-')[0])
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

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
    
    # Initialize parameters
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
        "band": None,
        "supervisor_id": None,
        "creche_status_id": None,
        "phases": None,
        "cstart_date": None,
        "cend_date": None,
        "creche_age": None
    }

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
    
    # Geography filters - handle multiple selections
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
    
    if filters.get("band"):
        params["band"] = filters.get("band")
    
    if filters.get("supervisor_id"):
        params["supervisor_id"] = filters.get("supervisor_id")
    
    if filters.get("creche_status_id"):
        params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            params["phases"] = phases_cleaned

    # Get creche_age filter
    creche_age = filters.get("creche_age", "")
    params["creche_age"] = creche_age

    # Build conditions for geography filters
    conditions = []
    
    if params.get("partner"):
        conditions.append("c.partner_id = %(partner)s")
    
    # State conditions
    if params.get("state"):
        conditions.append("c.state_id = %(state)s")
    elif params.get("state_ids"):
        conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")

    # District conditions
    if params.get("district"):
        conditions.append("c.district_id = %(district)s")
    elif params.get("district_ids"):
        conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")

    # Block conditions
    if params.get("block"):
        conditions.append("c.block_id = %(block)s")
    elif params.get("block_ids"):
        conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")

    # GP conditions
    if params.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
    elif params.get("gp_ids"):
        conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")

    # Other conditions
    if params.get("creche"):
        conditions.append("c.name = %(creche)s")
    
    if params.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
    
    if params.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
    
    if params.get("phases"):
        conditions.append("FIND_IN_SET(c.phase, %(phases)s)")

    # Handle creche opening date conditions
    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"):  # For equal date case
        conditions.append("DATE(c.creche_opening_date) = %(cstart_date)s")

    # Add creche_age condition
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

    # Enrollment date condition
    conditions.append("cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit >= %(start_date)s)")

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql_query = f"""
        SELECT * FROM (
            SELECT *,
                CASE 
                    WHEN attendance_percentage = 0 THEN 1
                    WHEN attendance_percentage < 25 THEN 2
                    WHEN attendance_percentage < 50 THEN 3 
                    WHEN attendance_percentage < 75 THEN 4
                    WHEN attendance_percentage < 100 THEN 5
                    WHEN attendance_percentage = 100 THEN 6
                    ELSE 0 
                END AS band
            FROM (
                SELECT 
                    p.partner_name AS partner,
                    s.state_name AS state,
                    d.district_name AS district,
                    b.block_name AS block,
                    g.gp_name AS gp,
                    usr.full_name AS supervisor,
                    c.creche_name AS creche,
                    c.creche_id AS creche_id,
                    c.creche_opening_date AS cr_open_date,
                    cee.date_of_enrollment AS date_of_enrollments,
                    c.creche_closing_date AS creche_closing_date,
                    cee.child_name AS name,
                    cee.child_id AS child_id,
                    cee.age_at_enrollment_in_months AS age,
                    cee.date_of_enrollment as date_of_enrollment,
                    (CASE 
                        WHEN cee.gender_id = '1' THEN 'M' 
                        WHEN cee.gender_id = '2' THEN 'F' 
                        ELSE cee.gender_id 
                    END) AS gender,
                    IFNULL(att.eligible_open_days,0) AS eligible_open_days,
                    IFNULL(att.days_attended,0) AS days_attended,
                    ROUND(
                        CASE 
                            WHEN att.eligible_open_days > 0 
                            THEN (att.days_attended * 100.0 / att.eligible_open_days) 
                            ELSE 0 
                        END, 2
                    ) AS attendance_percentage
                FROM 
                    `tabChild Enrollment and Exit` AS cee
                JOIN 
                    `tabCreche` AS c ON c.name = cee.creche_id
                JOIN 
                    `tabPartner` AS p ON p.name = c.partner_id
                JOIN 
                    `tabState` AS s ON s.name = c.state_id
                JOIN 
                    `tabDistrict` AS d ON d.name = c.district_id
                JOIN 
                    `tabBlock` AS b ON b.name = c.block_id
                JOIN
                    `tabGram Panchayat` AS g ON g.name = c.gp_id
                LEFT JOIN
                    `tabUser` AS usr ON usr.name = c.supervisor_id
                LEFT JOIN (
                    SELECT 
                        cal.childenrolledguid,
                        SUM(cal.attendance) AS days_attended,
                        COUNT(ca.date_of_attendance) AS eligible_open_days
                    FROM `tabChild Attendance` AS ca
                    INNER JOIN `tabChild Attendance List` AS cal 
                        ON cal.parent = ca.name
                    WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
                    AND ca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
                    GROUP BY cal.childenrolledguid
                ) AS att ON att.childenrolledguid = cee.childenrollguid
                WHERE 
                    {where_clause}
            ) AS FDT
            ORDER BY partner, state, district, block, gp, creche, date_of_enrollment
        ) AS FT  
        WHERE (%(band)s IS NULL OR band = %(band)s)
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)

    total_eligible_open_days = 0
    total_days_attended = 0
    total_attendance_percentage = 0

    for row in data:
        total_eligible_open_days += row.get("eligible_open_days", 0)
        total_days_attended += row.get("days_attended", 0)

    total_attendance_percentage = round((total_days_attended * 100.0 / total_eligible_open_days) if total_eligible_open_days > 0 else 0, 2)

    def get_attendance_percentage_style(total_attendance_percentage):
        if total_attendance_percentage is None:
            return "background-color: gray; color: black;"
        elif total_attendance_percentage == 0:
            return "background-color: #FF474D; color: black;"
        elif total_attendance_percentage < 25:
            return "background-color: #FF7074; color: black;"
        elif total_attendance_percentage < 50:
            return "background-color: #FFBD54; color: black;"
        elif total_attendance_percentage < 75:
            return "background-color: #FFE762; color: black;"
        elif total_attendance_percentage < 100:
            return "background-color: #8DFF92; color: black;"
        elif total_attendance_percentage == 100:
            return "background-color: #54FF5C; color: black;"
        return "background-color: gray; color: black;"

    attendance_style = get_attendance_percentage_style(total_attendance_percentage)
    attendance_html = f"<b style='{attendance_style} padding: 5px; border-radius: 3px;'>{total_attendance_percentage}%</b>"
    summary_row = {
        "gender": "<b style='color:black;'>Total</b>",
        "eligible_open_days": f"<b style='color:black;'>{total_eligible_open_days}</b>",
        "days_attended": f"<b style='color:black;'>{total_days_attended}</b>",
        "attendance_percentage": attendance_html
        
    }
    data.append(summary_row)
    return data














#backup Before age of Creche Filter
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
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 150},
#         {"label": "Child Name", "fieldname": "name", "fieldtype": "Data", "width": 160},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Age (in months)", "fieldname": "age", "fieldtype": "Data", "width": 142},
#         {"label": "Date of Enrollment", "fieldname": "date_of_enrollments", "fieldtype": "Date", "width": 160},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 85},
#         {"label": "Eligible Open Days", "fieldname": "eligible_open_days", "fieldtype": "Data", "width": 150},
#         {"label": "Days Attended", "fieldname": "days_attended", "fieldtype": "Data", "width": 130},
#         {"label": "Attendance (%)", "fieldname": "attendance_percentage", "fieldtype": "Data", "width": 130, "align": "right"}
#     ]
#     return columns

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     # Date range setup
#     month = int(filters.get("month") if filters.get("month") else nowdate().split('-')[1])
#     year = int(filters.get("year") if filters.get("year") else nowdate().split('-')[0])
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

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
    
#     # Initialize parameters
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#         "band": None,
#         "supervisor_id": None,
#         "creche_status_id": None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None
#     }

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
    
#     # Geography filters - handle multiple selections
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
    
#     if filters.get("band"):
#         params["band"] = filters.get("band")
    
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
#         conditions.append("c.partner_id = %(partner)s")
    
#     # State conditions
#     if params.get("state"):
#         conditions.append("c.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")

#     # District conditions
#     if params.get("district"):
#         conditions.append("c.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")

#     # Block conditions
#     if params.get("block"):
#         conditions.append("c.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")

#     # GP conditions
#     if params.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")

#     # Other conditions
#     if params.get("creche"):
#         conditions.append("c.name = %(creche)s")
    
#     if params.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
    
#     if params.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
    
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(c.phase, %(phases)s)")

#     # Handle creche opening date conditions
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):  # For equal date case
#         conditions.append("DATE(c.creche_opening_date) = %(cstart_date)s")

#     # Enrollment date condition
#     conditions.append("cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit >= %(start_date)s)")

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     sql_query = f"""
#         SELECT * FROM (
#             SELECT *,
#                 CASE 
#                     WHEN attendance_percentage = 0 THEN 1
#                     WHEN attendance_percentage < 25 THEN 2
#                     WHEN attendance_percentage < 50 THEN 3 
#                     WHEN attendance_percentage < 75 THEN 4
#                     WHEN attendance_percentage < 100 THEN 5
#                     WHEN attendance_percentage = 100 THEN 6
#                     ELSE 0 
#                 END AS band
#             FROM (
#                 SELECT 
#                     p.partner_name AS partner,
#                     s.state_name AS state,
#                     d.district_name AS district,
#                     b.block_name AS block,
#                     g.gp_name AS gp,
#                     c.creche_name AS creche,
#                     c.creche_id AS creche_id,
#                     c.creche_opening_date AS cr_open_date,
#                     cee.date_of_enrollment AS date_of_enrollments,
#                     c.creche_closing_date AS creche_closing_date,
#                     cee.child_name AS name,
#                     cee.child_id AS child_id,
#                     cee.age_at_enrollment_in_months AS age,
#                     cee.date_of_enrollment as date_of_enrollment,
#                     (CASE 
#                         WHEN cee.gender_id = '1' THEN 'M' 
#                         WHEN cee.gender_id = '2' THEN 'F' 
#                         ELSE cee.gender_id 
#                     END) AS gender,
#                     IFNULL(att.eligible_open_days,0) AS eligible_open_days,
#                     IFNULL(att.days_attended,0) AS days_attended,
#                     ROUND(
#                         CASE 
#                             WHEN att.eligible_open_days > 0 
#                             THEN (att.days_attended * 100.0 / att.eligible_open_days) 
#                             ELSE 0 
#                         END, 2
#                     ) AS attendance_percentage
#                 FROM 
#                     `tabChild Enrollment and Exit` AS cee
#                 JOIN 
#                     `tabCreche` AS c ON c.name = cee.creche_id
#                 JOIN 
#                     `tabPartner` AS p ON p.name = c.partner_id
#                 JOIN 
#                     `tabState` AS s ON s.name = c.state_id
#                 JOIN 
#                     `tabDistrict` AS d ON d.name = c.district_id
#                 JOIN 
#                     `tabBlock` AS b ON b.name = c.block_id
#                 JOIN 
#                     `tabGram Panchayat` AS g ON g.name = c.gp_id
#                 LEFT JOIN (
#                     SELECT 
#                         cal.childenrolledguid,
#                         SUM(cal.attendance) AS days_attended,
#                         COUNT(ca.date_of_attendance) AS eligible_open_days
#                     FROM `tabChild Attendance` AS ca
#                     INNER JOIN `tabChild Attendance List` AS cal 
#                         ON cal.parent = ca.name
#                     WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
#                     AND ca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
#                     GROUP BY cal.childenrolledguid
#                 ) AS att ON att.childenrolledguid = cee.childenrollguid
#                 WHERE 
#                     {where_clause}
#             ) AS FDT
#             ORDER BY partner, state, district, block, gp, creche, date_of_enrollment
#         ) AS FT  
#         WHERE (%(band)s IS NULL OR band = %(band)s)
#     """

#     data = frappe.db.sql(sql_query, params, as_dict=True)

#     total_eligible_open_days = 0
#     total_days_attended = 0
#     total_attendance_percentage = 0

#     for row in data:
#         total_eligible_open_days += row.get("eligible_open_days", 0)
#         total_days_attended += row.get("days_attended", 0)

#     total_attendance_percentage = round((total_days_attended * 100.0 / total_eligible_open_days) if total_eligible_open_days > 0 else 0, 2)

#     def get_attendance_percentage_style(total_attendance_percentage):
#         if total_attendance_percentage is None:
#             return "background-color: gray; color: black;"
#         elif total_attendance_percentage == 0:
#             return "background-color: #FF474D; color: black;"
#         elif total_attendance_percentage < 25:
#             return "background-color: #FF7074; color: black;"
#         elif total_attendance_percentage < 50:
#             return "background-color: #FFBD54; color: black;"
#         elif total_attendance_percentage < 75:
#             return "background-color: #FFE762; color: black;"
#         elif total_attendance_percentage < 100:
#             return "background-color: #8DFF92; color: black;"
#         elif total_attendance_percentage == 100:
#             return "background-color: #54FF5C; color: black;"
#         return "background-color: gray; color: black;"

#     attendance_style = get_attendance_percentage_style(total_attendance_percentage)
#     attendance_html = f"<b style='{attendance_style} padding: 5px; border-radius: 3px;'>{total_attendance_percentage}%</b>"
#     summary_row = {
#         "gender": "<b style='color:black;'>Total</b>",
#         "eligible_open_days": f"<b style='color:black;'>{total_eligible_open_days}</b>",
#         "days_attended": f"<b style='color:black;'>{total_days_attended}</b>",
#         "attendance_percentage": attendance_html
        
#     }
#     data.append(summary_row)
#     return data







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
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 120},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 150},
#         {"label": "Child Name", "fieldname": "name", "fieldtype": "Data", "width": 160},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Age (in months)", "fieldname": "age", "fieldtype": "Data", "width": 142},
#         {"label": "Date of Enrollment", "fieldname": "date_of_enrollments", "fieldtype": "Date", "width": 160},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 85},
#         {"label": "Eligible Open Days", "fieldname": "eligible_open_days", "fieldtype": "Data", "width": 150},
#         {"label": "Days Attended", "fieldname": "days_attended", "fieldtype": "Data", "width": 130},
#         {"label": "Attendance (%)", "fieldname": "attendance_percentage", "fieldtype": "Data", "width": 130, "align": "right"}
#     ]
#     return columns

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     month = int(filters.get("month") if filters else nowdate().split('-')[1])
#     year = int(filters.get("year") if filters else nowdate().split('-')[0])
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     # filters logic for cr_opening ends here

#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner = filters.get("partner") or current_user_partner

#     state_query = """ 
#         SELECT DISTINCT ts.name AS state_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s 
#         ORDER BY ts.state_name
#     """
#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)

#     state = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)
#     district = filters.get("district") if filters else None
#     block = filters.get("block") if filters else None
#     gp = filters.get("gp") if filters else None
#     creche = filters.get("creche") if filters else None
#     band = filters.get("band") if filters else None
#     supervisor_id = filters.get("supervisor_id") if filters else None
    
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None


#     # filters logic for cr_opening starts here
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
    
#     partner = None if not partner else partner
#     state = None if not state else state

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "partner": partner,
#         "state": state,
#         "district": district,
#         "block": block,
#         "gp": gp,
#         "creche": creche,
#         "band": band,
#         "supervisor_id": supervisor_id,
#         "year": year,
#         "month": month,
#         "cstart_date": cstart_date,
#         "cend_date": cend_date,
#         "phases": phases_cleaned,
#         "creche_status_id": creche_status_id
#     }

#     sql_query = """
#         SELECT * FROM (
#             SELECT *,
#                 CASE 
#                     WHEN attendance_percentage = 0 THEN 1
#                     WHEN attendance_percentage < 25 THEN 2
#                     WHEN attendance_percentage < 50 THEN 3 
#                     WHEN attendance_percentage < 75 THEN 4
#                     WHEN attendance_percentage < 100 THEN 5
#                     WHEN attendance_percentage = 100 THEN 6
#                     ELSE 0 
#                 END AS band
#             FROM (
#                 SELECT 
#                     p.partner_name AS partner,
#                     s.state_name AS state,
#                     d.district_name AS district,
#                     b.block_name AS block,
#                     g.gp_name AS gp,
#                     c.creche_name AS creche,
#                     c.creche_id AS creche_id,
#                     c.creche_opening_date AS cr_open_date,
#                     cee.date_of_enrollment AS date_of_enrollments,
#                     c.creche_closing_date AS creche_closing_date,
#                     cee.child_name AS name,
#                     cee.child_id AS child_id,
#                     cee.age_at_enrollment_in_months AS age,
#                     cee.date_of_enrollment as date_of_enrollment,
#                     (CASE 
#                         WHEN cee.gender_id = '1' THEN 'M' 
#                         WHEN cee.gender_id = '2' THEN 'F' 
#                         ELSE cee.gender_id 
#                     END) AS gender,
#                     IFNULL(att.eligible_open_days,0) AS eligible_open_days,
#                     IFNULL(att.days_attended,0) AS days_attended,
#                     ROUND(
#                         CASE 
#                             WHEN att.eligible_open_days > 0 
#                             THEN (att.days_attended * 100.0 / att.eligible_open_days) 
#                             ELSE 0 
#                         END, 2
#                     ) AS attendance_percentage
#                 FROM 
#                     `tabChild Enrollment and Exit` AS cee
#                 JOIN 
#                     `tabCreche` AS c ON c.name = cee.creche_id
#                 JOIN 
#                     `tabPartner` AS p ON p.name = c.partner_id
#                 JOIN 
#                     `tabState` AS s ON s.name = c.state_id
#                 JOIN 
#                     `tabDistrict` AS d ON d.name = c.district_id
#                 JOIN 
#                     `tabBlock` AS b ON b.name = c.block_id
#                 JOIN 
#                     `tabGram Panchayat` AS g ON g.name = c.gp_id
#                 LEFT JOIN (
#                     SELECT 
#                         cal.childenrolledguid,
#                         SUM(cal.attendance) AS days_attended,
#                         COUNT(ca.date_of_attendance) AS eligible_open_days
#                     FROM `tabChild Attendance` AS ca
#                     INNER JOIN `tabChild Attendance List` AS cal 
#                         ON cal.parent = ca.name
#                     WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
#                     AND ca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
#                     GROUP BY cal.childenrolledguid
#                 ) AS att ON att.childenrolledguid = cee.childenrollguid
#                 WHERE 
#                     (%(partner)s IS NULL OR c.partner_id = %(partner)s) 
#                     AND (%(state)s IS NULL OR c.state_id = %(state)s) 
#                     AND (%(district)s IS NULL OR c.district_id = %(district)s)
#                     AND (%(block)s IS NULL OR c.block_id = %(block)s)
#                     AND (%(gp)s IS NULL OR c.gp_id = %(gp)s) 
#                     AND (%(creche)s IS NULL OR c.name = %(creche)s)
#                     AND (%(supervisor_id)s IS NULL OR c.supervisor_id = %(supervisor_id)s)
#                     AND (%(creche_status_id)s IS NULL OR c.creche_status_id = %(creche_status_id)s)
#                     AND (%(phases)s IS NULL OR FIND_IN_SET(c.phase, %(phases)s))
#                     AND cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit >=  %(start_date)s)
#                     AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) AS FDT
#                     ORDER BY partner, state, district, block, gp, creche,date_of_enrollment
#         ) AS FT  
#         WHERE (%(band)s IS NULL OR band = %(band)s)
#     """

#     data = frappe.db.sql(sql_query, params, as_dict=True)

#     total_eligible_open_days = 0
#     total_days_attended = 0
#     total_attendance_percentage = 0

#     for row in data:
#         total_eligible_open_days += row.get("eligible_open_days", 0)
#         total_days_attended += row.get("days_attended", 0)

#     total_attendance_percentage = round((total_days_attended * 100.0 / total_eligible_open_days) if total_eligible_open_days > 0 else 0, 2)

#     def get_attendance_percentage_style(total_attendance_percentage):
#         if total_attendance_percentage is None:
#             return "background-color: gray; color: black;"
#         elif total_attendance_percentage == 0:
#             return "background-color: #FF474D; color: black;"
#         elif total_attendance_percentage < 25:
#             return "background-color: #FF7074; color: black;"
#         elif total_attendance_percentage < 50:
#             return "background-color: #FFBD54; color: black;"
#         elif total_attendance_percentage < 75:
#             return "background-color: #FFE762; color: black;"
#         elif total_attendance_percentage < 100:
#             return "background-color: #8DFF92; color: black;"
#         elif total_attendance_percentage == 100:
#             return "background-color: #54FF5C; color: black;"
#         return "background-color: gray; color: black;"

#     attendance_style = get_attendance_percentage_style(total_attendance_percentage)
#     attendance_html = f"<b style='{attendance_style} padding: 5px; border-radius: 3px;'>{total_attendance_percentage}%</b>"
#     summary_row = {
#         "gender": "<b style='color:black;'>Total</b>",
#         "eligible_open_days": f"<b style='color:black;'>{total_eligible_open_days}</b>",
#         "days_attended": f"<b style='color:black;'>{total_days_attended}</b>",
#         "attendance_percentage": attendance_html
        
#     }
#     data.append(summary_row)
#     return data