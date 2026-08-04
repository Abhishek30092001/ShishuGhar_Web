from datetime import date
import frappe
import calendar

import hashlib

def generate_id(field):
    base_id = "".join(word[:3].lower() for word in field.split() if word.isalpha() and len(word) >= 3)
    
    unique_suffix = hashlib.md5(field.encode()).hexdigest()[:4]
    return f"{base_id}-{unique_suffix}"


@frappe.whitelist()
def dashboard_section_one(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):

    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None


    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


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

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
        "c_status": c_status,
        "phases":phases
    }
    
    query = """
SELECT 
    FR.creche_no AS "No. of creches", 
    CASE WHEN FR.creche_no = 0 THEN 0 ELSE CEIL(FR.no_days_creche_opened / FR.creche_no) END AS "Avg. no. of days creche opened",
    CASE WHEN FR.no_days_creche_opened = 0 THEN 0 ELSE ROUND(FR.no_children_present_creche_opened / FR.no_days_creche_opened, 1) END AS "Avg. attendance per day",
    FR.no_children_curr_active AS "Current active children",
    FR.no_creche_attendance_submitted AS "No. of creches submitted attendance (All Days)",
    FR.no_creche_attendance_not_submitted AS "No. of creches not submitted attendance (All Days)"
FROM (
    SELECT 
        -- Count of Active Creches
        (SELECT COUNT(*)
         FROM `tabCreche` tc
         WHERE 
           (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
           AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)    
           AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))  
            AND (
                %(c_status)s = 1
                OR (
                    %(c_status)s != 1
                    AND (tc.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s))
                    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                        OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                )
            )


        ) AS creche_no,

        -- count of creche whoose attendance submitted
        (SELECT COUNT(*) 
        FROM (
            SELECT 
                tc.name, 
                tc.creche_opening_date,  
                DATEDIFF(
                    CASE 
                        WHEN DATE_FORMAT(CURRENT_DATE(), '%%Y-%%m') = DATE_FORMAT(%(start_date)s, '%%Y-%%m') 
                        THEN CURRENT_DATE() 
                        ELSE %(end_date)s 
                    END, 
                    CASE 
                        WHEN tc.creche_opening_date < %(start_date)s 
                        THEN %(start_date)s 
                        ELSE tc.creche_opening_date 
                    END
                ) + 1 AS elgdays, 
                IFNULL(att.attdays, 0) AS attdays
            FROM 
                `tabCreche` tc 
            LEFT JOIN (
                SELECT 
                    tca.creche_id, 
                    COUNT(*) AS attdays 
                FROM 
                    `tabChild Attendance` tca 
                WHERE 
                    tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s 
                GROUP BY 
                    tca.creche_id
            ) AS att 
            ON tc.name = att.creche_id 
            WHERE 
                tc.creche_opening_date IS NOT NULL 
                AND tc.creche_opening_date <= %(end_date)s
                AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
                AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
                AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))
                AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
                AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS creche_attendance
        WHERE elgdays <= attdays
        ) AS no_creche_attendance_submitted,

(SELECT COUNT(*) 
        FROM (
            SELECT 
                tc.name, 
                tc.creche_opening_date,  
                DATEDIFF(
                    CASE 
                        WHEN DATE_FORMAT(CURRENT_DATE(), '%%Y-%%m') = DATE_FORMAT(%(start_date)s, '%%Y-%%m') 
                        THEN CURRENT_DATE() 
                        ELSE %(end_date)s 
                    END, 
                    CASE 
                        WHEN tc.creche_opening_date < %(start_date)s 
                        THEN %(start_date)s 
                        ELSE tc.creche_opening_date 
                    END
                ) + 1 AS elgdays, 
                IFNULL(att.attdays, 0) AS attdays
            FROM 
                `tabCreche` tc 
            LEFT JOIN (
                SELECT 
                    tca.creche_id, 
                    COUNT(*) AS attdays 
                FROM 
                    `tabChild Attendance` tca 
                WHERE 
                    tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s 
                GROUP BY 
                    tca.creche_id
            ) AS att 
            ON tc.name = att.creche_id 
            WHERE 
                tc.creche_opening_date IS NOT NULL 
                AND tc.creche_opening_date <= %(end_date)s
                AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
                AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
                AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))
                AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
                AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS creche_attendance
        WHERE elgdays > attdays
        ) AS no_creche_attendance_not_submitted,


        -- Count of Days Creche Opened
        (SELECT COUNT(*)
         FROM `tabChild Attendance` ca
         JOIN `tabCreche` cr ON cr.name = ca.creche_id
         WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
           AND YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

        ) AS no_days_creche_opened,

        -- Total Attendance when Creche Opened @time
        (SELECT COUNT(cal.name)
         FROM `tabChild Attendance List` cal
         JOIN `tabChild Attendance` ca ON ca.name = cal.parent
         JOIN `tabCreche` cr on cr.name = ca.creche_id
         WHERE cal.attendance = 1
           AND ca.is_shishu_ghar_is_closed_for_the_day = 0
           AND YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS no_children_present_creche_opened,

        -- currently active children
        (SELECT COUNT(*)
         FROM `tabChild Enrollment and Exit` cee
         INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
         WHERE  (cee.date_of_enrollment <=  %(end_date)s and 
           (cee.date_of_exit IS null or cee.date_of_exit > %(end_date)s))
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
           AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS no_children_curr_active

) FR;
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}
    sections = {

    "Col0":[
        "No. of creches",
        "Current active children",
        "No. of creches submitted attendance (All Days)",
        "No. of creches not submitted attendance (All Days)"
    ],
    "Col1": [
        "Avg. no. of days creche opened",
        "Avg. attendance per day"
    ]
}

    transformed_data = {
        section: [
        { "id": generate_id(field), "title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data


@frappe.whitelist()
def dashboard_section_one2(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


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

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": phases
    }
    
    query = """
SELECT 
        FR.Max_Attendance_in_a_Day AS "Maximum attendance in a day",
        CASE WHEN FR.creche_no = 0 THEN 0 ELSE CEIL(FR.No_of_days_creche_attendance_submitted / FR.creche_no) 
        END AS "Avg. no. of days attendance submitted",
        FR.Total_Anthro_data_submitted AS "Anthro data submitted",
        FR.Total_Anthro_data_not_submitted AS "Anthro data not submitted"
FROM (
    SELECT 
     -- Count of Active Creches
        (SELECT COUNT(*)
         FROM `tabCreche` tc
         WHERE 
           (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
           AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))
           AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

        ) AS creche_no,
        
        -- Maximum Attendance in a Day @time p2 start
        (SELECT MAX(daily_attendance) 
         FROM (
            SELECT COUNT(cal.name) AS daily_attendance
            FROM `tabChild Attendance` ca
            JOIN `tabChild Attendance List` cal ON ca.name = cal.parent
            JOIN `tabCreche` cr on cr.name = ca.creche_id
            WHERE cal.attendance = 1
              AND ca.is_shishu_ghar_is_closed_for_the_day = 0
              AND YEAR(ca.date_of_attendance) = %(year)s
              AND MONTH(ca.date_of_attendance) = %(month)s
              AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
                AND (
                    (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )
              AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
              AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
              AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
              AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
              AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
              AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))

            GROUP BY ca.date_of_attendance
         ) AS daily_data
        ) AS Max_Attendance_in_a_Day,

        -- Count of Days Attendance Submitted
        (SELECT COUNT(*)
         FROM `tabChild Attendance` ca
         JOIN `tabCreche` cr on cr.name = ca.creche_id
         WHERE YEAR(ca.date_of_attendance) = %(year)s
           AND MONTH(ca.date_of_attendance) = %(month)s
           AND (%(partner_id)s IS NULL OR ca.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND ca.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ca.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND ca.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ca.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND ca.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ca.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND ca.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(ca.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS No_of_days_creche_attendance_submitted,

        -- Total Anthropometric Data Submitted
        (SELECT COUNT(*)
         FROM `tabChild Growth Monitoring` cgm
         JOIN `tabCreche` cr on cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Anthro_data_submitted,

        (
            SELECT COUNT(*) AS Total_Anthro_data_not_submitted
            FROM `tabCreche` cr
            WHERE cr.creche_status_id = IFNULL(%(c_status)s, cr.creche_status_id)
            AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
            AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
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
            AND NOT EXISTS (
                SELECT 1
                FROM `tabChild Growth Monitoring` cgm
                WHERE cgm.creche_id = cr.name
                    AND YEAR(cgm.measurement_date) = %(year)s
                    AND MONTH(cgm.measurement_date) = %(month)s
            )
        ) AS Total_Anthro_data_not_submitted
) FR;


    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {

    "Col1": [
        "Maximum attendance in a day",
        "Avg. no. of days attendance submitted",
        "Anthro data submitted",
        "Anthro data not submitted"
    ]
}

    transformed_data = {
        section: [
        { "id": generate_id(field), "title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist()
def dashboard_section_two(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,supervisor_id=None, year=None, month=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    if not year or not month:
        frappe.throw("Year and Month are required and must be valid numbers.")
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    
    # Get user geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    
    # Process phases parameter
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    
    # Set None for empty parameters
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id
    district_id = None if not district_id else district_id
    block_id = None if not block_id else block_id
    gp_id = None if not gp_id else gp_id
    creche_id = None if not creche_id else creche_id
    supervisor_id = None if not supervisor_id else supervisor_id

    # Calculate previous months
    if month == 1:
        lmonth, plmonth, lyear, pyear = 12, 11, year - 1, year - 1
    elif month == 2:
        lmonth, plmonth, lyear, pyear = 1, 12, year, year - 1
    else:
        lmonth, plmonth, lyear, pyear = month - 1, month - 2, year, year

    # Prepare parameters
    params = {
        "end_date": end_date,
        "start_date": start_date,
        "year": year,
        "month": month,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "supervisor_id": supervisor_id,
        "c_status": c_status,
        "phases": phases,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear
    }

    # Optimized query with corrected Red Flag section
    query = """
    SELECT 
        FR.current_enrolled_children AS "Children enrolled this month",
        FR.enrolled_children AS "Enrolled children",
        FR.cur_eligible_children AS "Current eligible children",
        FR.Total_Current_exit_children AS "Children exited this month",
        FR.cumm_enrolled_children AS "Cumulative enrolled children",
        FR.Total_Cumulative_exit_children AS "Cumulative exit children",
        FR.red_flag AS "Red flag children"
    FROM (
        SELECT 
            (SELECT COUNT(DISTINCT cees.name)
            FROM `tabChild Enrollment and Exit` AS cees
            INNER JOIN `tabCreche` AS cr ON cr.name = cees.creche_id
            WHERE((cees.date_of_exit BETWEEN %(start_date)s AND %(end_date)s) OR
            (cees.date_of_enrollment <= %(end_date)s AND (cees.date_of_exit IS NULL OR cees.date_of_exit >= %(end_date)s)))
            AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cees.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND cees.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cees.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND cees.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cees.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND cees.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cees.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
            AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (
                cr.creche_opening_date IS NULL 
                OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s)
            )
            AND (
                (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
            )
        ) AS enrolled_children,


            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` AS cees
             JOIN `tabCreche` AS cr ON cr.name = cees.creche_id
             WHERE YEAR(cees.date_of_enrollment) = %(year)s  
               AND MONTH(cees.date_of_enrollment) = %(month)s 
               AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
               AND (
                    (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cees.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cees.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cees.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cees.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cees.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cees.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cees.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )                  
               AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) 
            )  
            AS current_enrolled_children,

            (SELECT COUNT(hhc.name)
             FROM `tabHousehold Child Form` AS hhc 
             JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
             JOIN `tabCreche` AS cr ON cr.name = hf.creche_id
             WHERE hhc.is_dob_available = 1 
             AND (hhc.child_status IS NULL OR TRIM(hhc.child_status) = '')
            AND (
                hhc.child_dob BETWEEN 
                    DATE_SUB(
                        IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
                            CURDATE(), 
                            %(end_date)s
                        ), 
                        INTERVAL 36 MONTH
                    )
                    AND 
                    DATE_SUB(
                        IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
                            CURDATE(), 
                            %(end_date)s
                        ), 
                        INTERVAL 6 MONTH
                    )
            )
               AND (%(partner_id)s IS NULL OR hf.partner_id = %(partner_id)s)
               AND (
                    (%(state_id)s IS NOT NULL AND hf.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(hf.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND hf.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(hf.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND hf.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(hf.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND hf.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(hf.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )   
               AND (%(creche_id)s IS NULL OR hf.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
                AND (
                    %(c_status)s = 1
                    OR (
                        %(c_status)s != 1
                        AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
                        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                    )
                )
            )AS cur_eligible_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` cec 
             JOIN `tabCreche` AS cr ON cr.name = cec.creche_id
             WHERE YEAR(date_of_exit) = %(year)s  
               AND MONTH(date_of_exit) = %(month)s  
               AND (%(partner_id)s IS NULL OR cec.partner_id = %(partner_id)s)  
               AND (
                    (%(state_id)s IS NOT NULL AND cec.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cec.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cec.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cec.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cec.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cec.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cec.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cec.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )   
               AND (%(creche_id)s IS NULL OR cec.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS Total_Current_exit_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` AS cee
             JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
             WHERE cee.date_of_enrollment <= %(end_date)s
               AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s) 
               AND (
                    (%(state_id)s IS NOT NULL AND cee.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cee.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cee.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cee.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cee.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cee.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cee.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cee.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )                 
               AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS cumm_enrolled_children,

            (SELECT COUNT(*) 
             FROM `tabChild Enrollment and Exit` cmec  
             JOIN `tabCreche` AS cr ON cr.name = cmec.creche_id
             WHERE date_of_exit <= %(end_date)s  
               AND (%(partner_id)s IS NULL OR cmec.partner_id = %(partner_id)s)  
               AND (
                    (%(state_id)s IS NOT NULL AND cmec.state_id = %(state_id)s) 
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cmec.state_id, %(state_ids)s))
                    OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
                )
                AND (
                    (%(district_id)s IS NOT NULL AND cmec.district_id = %(district_id)s) 
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cmec.district_id, %(district_ids)s))
                    OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
                )
                AND (
                    (%(block_id)s IS NOT NULL AND cmec.block_id = %(block_id)s) 
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cmec.block_id, %(block_ids)s))
                    OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
                )
                AND (
                    (%(gp_id)s IS NOT NULL AND cmec.gp_id = %(gp_id)s) 
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cmec.gp_id, %(gp_ids)s))
                    OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
                )   
               AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
               AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
               AND (%(creche_id)s IS NULL OR cmec.creche_id = %(creche_id)s)
               AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
               AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
               AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )AS Total_Cumulative_exit_children,

            (   SELECT COUNT(DISTINCT cee.childenrollguid) as red_flag 
                FROM `tabAnthropromatic Data` ad
                INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
                INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
                INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
                INNER JOIN `tabUser` AS usr ON cr.supervisor_id = usr.name 
                INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
                INNER JOIN `tabState` AS s ON s.name = cr.state_id
                INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
                INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
                INNER JOIN `tabGram Panchayat` AS g ON g.name = cr.gp_id
                WHERE
                    (
                        ad.weight_for_age = 1
                        OR ad.weight_for_height = 1
                        OR ad.any_medical_major_illness = 1
                        OR ad.childenrollguid IN (
                            SELECT DISTINCT ad_current.childenrollguid
                            FROM `tabAnthropromatic Data` AS ad_current
                            INNER JOIN `tabChild Growth Monitoring` AS cgm2 ON cgm2.name = ad_current.parent
                            INNER JOIN `tabAnthropromatic Data` AS ad_lyear
                                ON ad_lyear.childenrollguid = ad_current.childenrollguid
                                AND ad_lyear.do_you_have_height_weight = 1
                                AND YEAR(ad_lyear.measurement_taken_date) = %(lyear)s
                                AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s
                                AND ad_current.weight <= ad_lyear.weight
                            INNER JOIN `tabAnthropromatic Data` AS ad_pyear
                                ON ad_pyear.childenrollguid = ad_current.childenrollguid
                                AND ad_pyear.do_you_have_height_weight = 1
                                AND YEAR(ad_pyear.measurement_taken_date) = %(pyear)s
                                AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s
                                AND ad_lyear.weight <= ad_pyear.weight
                            WHERE ad_current.do_you_have_height_weight = 1
                            AND YEAR(ad_current.measurement_taken_date) = %(year)s
                            AND MONTH(ad_current.measurement_taken_date) = %(month)s
                        )
                    )
                    AND YEAR(ad.measurement_taken_date) = %(year)s
                    AND MONTH(ad.measurement_taken_date) = %(month)s
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
                    AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
                    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                ) as red_flag


    ) AS FR
    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {
        "Col2": [
            "Enrolled children",
            "Children enrolled this month",
            "Current eligible children",
            "Children exited this month",
            "Cumulative enrolled children",
            "Cumulative exit children",
            "Red flag children"
        ]
    }

    transformed_data = {
        section: [
            { "id": generate_id(field), "title": field, "value": result.get(field, "")} for field in fields
        ]
        for section, fields in sections.items()
    }

    frappe.response["data"] = transformed_data


@frappe.whitelist()
def dashboard_section_three(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


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

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "c_status": c_status,
        "phases": phases    
    }
    

    query = """
    SELECT
        COUNT(cee.childenrollguid) AS "Children measurement taken",
        SUM(CASE WHEN ad.weight_for_age = 2 THEN 1 ELSE 0 END) AS "Moderately underweight",
        SUM(CASE WHEN ad.weight_for_height = 2 THEN 1 ELSE 0 END) AS "Moderately wasted",
        SUM(CASE WHEN ad.height_for_age = 2 THEN 1 ELSE 0 END) AS "Moderately stunted"
    FROM `tabAnthropromatic Data` AS ad
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
    WHERE ad.do_you_have_height_weight = 1
        AND YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
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
        AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """


    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {
    "Col3": [
        "Children measurement taken",
        "Moderately underweight",
        "Moderately wasted",
        "Moderately stunted"
    ]
}

    transformed_data = {
        section: [
        {"id": generate_id(field), "title": field, "value": result.get(field, "")}
        for field in fields
    ]
    for section, fields in sections.items()
}

    frappe.response["data"] = transformed_data

@frappe.whitelist()
def dashboard_section_four(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None,year=None,month=None,supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
    creche_id = creche_id or None  
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id


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

    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": phases
    }
    

    query = """
SELECT 
    FR.measurement_data_not_submitted AS "Children measurement not taken",
    FR.Total_Severely_underweight_children AS "Severely underweight",
    FR.Total_SAM_children AS "Severely wasted",
    FR.Total_Severely_stunted_children AS "Severely stunted"
FROM (
    SELECT 


    (SELECT COUNT(DISTINCT cee.childenrollguid)
        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
        LEFT JOIN (
            SELECT DISTINCT ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
        ) submitted ON submitted.childenrollguid = cee.childenrollguid
        WHERE cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
            AND submitted.childenrollguid IS NULL

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
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
            AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS measurement_data_not_submitted,

        -- "Total Severely Underweight Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
           AND cee.date_of_enrollment <= %(end_date)s
           AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_age = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Severely_underweight_children,

        -- "Total SAM Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
         INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
           AND ad.do_you_have_height_weight = 1
           AND ad.weight_for_height = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_SAM_children,

        -- "Total Severely Stunted Children"
        (SELECT COUNT(ad.name)
         FROM `tabAnthropromatic Data` AS ad
         JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
         JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
         WHERE YEAR(cgm.measurement_date) = %(year)s
           AND MONTH(cgm.measurement_date) = %(month)s
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
           AND ad.do_you_have_height_weight = 1
           AND ad.height_for_age = 1
           AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
           AND (
               (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
               OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
           )
           AND (
               (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
               OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
           )
           AND (
               (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
               OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
           )
           AND (
               (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
               OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
           )
           AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
           AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
           AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
           AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
           AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS Total_Severely_stunted_children
) AS FR;

    """

    data = frappe.db.sql(query, params, as_dict=True)

    result = data[0] if data else {}

    sections = {


    "Col4": [
        "Children measurement not taken",
        "Severely underweight",
        "Severely wasted",
        "Severely stunted"
    ]
}

    transformed_data = {
        section: [
            {
                "id": generate_id(field),
                "title": field, 
                "value": result.get(field, "")
            } 
            for field in fields
        ]
        for section, fields in sections.items()
    }
    frappe.response["data"] = transformed_data

@frappe.whitelist()
def dashboard_section_gf(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id")) or None
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id")) or None
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id")) or None
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id")) or None

    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    if month == 1:
        fallback_month = 11
        fallback_year = year - 1
    elif month == 2:
        fallback_month = 12
        fallback_year = year - 1
    else:
        fallback_month = month - 2
        fallback_year = year

    params = {
        "end_date": end_date, "year": year, "month": month, "start_date": start_date,
        "partner_id": partner_id, "state_id": state_id,
        "state_ids": state_ids, "district_id": district_id, "district_ids": district_ids,
        "block_id": block_id, "block_ids": block_ids,
        "gp_id": gp_id, "gp_ids": gp_ids,
        "creche_id": creche_id or None,
        "prev_year": prev_year, "prev_month": prev_month,
        "fallback_year": fallback_year, "fallback_month": fallback_month,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, "cend_date": cend_date,
        "c_status": c_status, "phases": phases
    }

    query = """
    SELECT COUNT(*) AS `Growth faltering 1`
    FROM `tabAnthropromatic Data` AS ad
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id

    LEFT JOIN `tabAnthropromatic Data` AS ad_prev
        ON ad_prev.childenrollguid = ad.childenrollguid
        AND ad_prev.do_you_have_height_weight = 1
        AND YEAR(ad_prev.measurement_taken_date) = %(prev_year)s
        AND MONTH(ad_prev.measurement_taken_date) = %(prev_month)s
        AND ad_prev.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
        ON ad_fallback.childenrollguid = ad.childenrollguid
        AND ad_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_fallback.measurement_taken_date) = %(fallback_year)s
        AND MONTH(ad_fallback.measurement_taken_date) = %(fallback_month)s
        AND ad_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_prev.childenrollguid IS NULL

    WHERE ad.do_you_have_height_weight = 1
      AND ad.weight_for_age_zscore IS NOT NULL
      AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
      AND (COALESCE(ad_prev.weight_for_age_zscore, ad_fallback.weight_for_age_zscore) - ad.weight_for_age_zscore) > 0

      AND YEAR(cgm.measurement_date) = %(year)s
      AND MONTH(cgm.measurement_date) = %(month)s
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
    """

    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}

    sections = {"Col3": ["Growth faltering 1"]}
    transformed_data = {
        section: [
            {"id": generate_id(field), "title": field, "value": result.get(field, 0)}
            for field in fields
        ]
        for section, fields in sections.items()
    }
    frappe.response["data"] = transformed_data

@frappe.whitelist()
def dashboard_section_gf_one(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id")) or None
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id")) or None
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id")) or None
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id")) or None

    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    if month == 1:
        fallback_month = 11
        fallback_year = year - 1
    elif month == 2:
        fallback_month = 12
        fallback_year = year - 1
    else:
        fallback_month = month - 2
        fallback_year = year

    params = {
        "end_date": end_date, "year": year, "month": month, "start_date": start_date,
        "partner_id": partner_id, "state_id": state_id,
        "state_ids": state_ids, "district_id": district_id, "district_ids": district_ids,
        "block_id": block_id, "block_ids": block_ids,
        "gp_id": gp_id, "gp_ids": gp_ids,
        "creche_id": creche_id or None,
        "prev_year": prev_year, "prev_month": prev_month,
        "fallback_year": fallback_year, "fallback_month": fallback_month,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, "cend_date": cend_date,
        "c_status": c_status, "phases": phases
    }

    query = """
    SELECT COUNT(*) AS `Growth faltering 1+`
    FROM `tabAnthropromatic Data` AS ad
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id

    LEFT JOIN `tabAnthropromatic Data` AS ad_prev
        ON ad_prev.childenrollguid = ad.childenrollguid
        AND ad_prev.do_you_have_height_weight = 1
        AND YEAR(ad_prev.measurement_taken_date) = %(prev_year)s
        AND MONTH(ad_prev.measurement_taken_date) = %(prev_month)s
        AND ad_prev.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
        ON ad_fallback.childenrollguid = ad.childenrollguid
        AND ad_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_fallback.measurement_taken_date) = %(fallback_year)s
        AND MONTH(ad_fallback.measurement_taken_date) = %(fallback_month)s
        AND ad_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_prev.childenrollguid IS NULL

    WHERE ad.do_you_have_height_weight = 1
      AND ad.weight_for_age_zscore IS NOT NULL
      AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
      AND (
        CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
        -
        COALESCE(
            CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
            CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
        )
    ) <= -0.5

      AND YEAR(cgm.measurement_date) = %(year)s
      AND MONTH(cgm.measurement_date) = %(month)s
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
    """

    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}

    sections = {"Col3": ["Growth faltering 1+"]}
    transformed_data = {
        section: [
            {"id": generate_id(field), "title": field, "value": result.get(field, 0)}
            for field in fields
        ]
        for section, fields in sections.items()
    }
    frappe.response["data"] = transformed_data


@frappe.whitelist()
def dashboard_section_gf_two(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    
    # Safety: if year/month missing, return empty (prevents crash)
    if not year or not month:
        transformed_data = {"Col4": [{"id": "growth_faltering_2", "title": "Growth faltering 2", "value": 0}]}
        frappe.response["data"] = transformed_data
        return

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id")) or None
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id")) or None
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id")) or None
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id")) or None

    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    # Priority (2 months ago) and fallback (3 months ago) logic
    if month <= 2:
        priority_year = year - 1
        priority_month = month + 10
    else:
        priority_year = year
        priority_month = month - 2

    if month <= 3:
        fallback_year = year - 1
        fallback_month = month + 9
    else:
        fallback_year = year
        fallback_month = month - 3

    params = {
        "end_date": end_date, "year": year, "month": month, "start_date": start_date,
        "partner_id": partner_id, "state_id": state_id,
        "state_ids": state_ids, "district_id": district_id, "district_ids": district_ids,
        "block_id": block_id, "block_ids": block_ids,
        "gp_id": gp_id, "gp_ids": gp_ids,
        "creche_id": creche_id or None,
        "priority_year": priority_year, "priority_month": priority_month,
        "fallback_year": fallback_year, "fallback_month": fallback_month,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, "cend_date": cend_date,
        "c_status": c_status, "phases": phases
    }

    query = """
    SELECT COUNT(*) AS `Growth faltering 2`
    FROM `tabAnthropromatic Data` AS ad
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id

    LEFT JOIN `tabAnthropromatic Data` AS ad_priority
        ON ad_priority.childenrollguid = ad.childenrollguid
        AND ad_priority.do_you_have_height_weight = 1
        AND YEAR(ad_priority.measurement_taken_date) = %(priority_year)s
        AND MONTH(ad_priority.measurement_taken_date) = %(priority_month)s
        AND ad_priority.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
        ON ad_fallback.childenrollguid = ad.childenrollguid
        AND ad_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_fallback.measurement_taken_date) = %(fallback_year)s
        AND MONTH(ad_fallback.measurement_taken_date) = %(fallback_month)s
        AND ad_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_priority.childenrollguid IS NULL

    WHERE ad.do_you_have_height_weight = 1
      AND ad.weight_for_age_zscore IS NOT NULL
      AND (ad_priority.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
      
      /* FIXED: Explicit CAST to DECIMAL handles BOTH positive AND negative z-scores reliably 
         (even if the DB column is stored as VARCHAR/TEXT in some setups) */
        AND (
            CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
            -
            COALESCE(
                CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
            )
        ) <= -0.5

      AND YEAR(cgm.measurement_date) = %(year)s
      AND MONTH(cgm.measurement_date) = %(month)s
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
      
      /* IMPROVED date filter: now correctly handles partial ranges (only start, only end, both, or none) */
      AND (%(cstart_date)s IS NULL OR cr.creche_opening_date >= %(cstart_date)s)
      AND (%(cend_date)s IS NULL OR cr.creche_opening_date <= %(cend_date)s)
    """

    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}

    sections = {"Col4": ["Growth faltering 2"]}
    transformed_data = {
        section: [
            {"id": generate_id(field), "title": field, "value": result.get(field, 0)}
            for field in fields
        ]
        for section, fields in sections.items()
    }
    frappe.response["data"] = transformed_data


@frappe.whitelist()
def dashboard_section_zig_zag(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id")) or None
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id")) or None
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id")) or None
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id")) or None

    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    def _rollback_month(y, m, step):
        m = m - step
        while m <= 0:
            m += 12
            y -= 1
        return m, y

    m1_month, m1_year = _rollback_month(year, month, 1)
    m2_month, m2_year = _rollback_month(year, month, 2)
    m3_month, m3_year = _rollback_month(year, month, 3)
    m4_month, m4_year = _rollback_month(year, month, 4)

    params = {
        "end_date": end_date, "year": year, "month": month, "start_date": start_date,
        "partner_id": partner_id, "state_id": state_id,
        "state_ids": state_ids, "district_id": district_id, "district_ids": district_ids,
        "block_id": block_id, "block_ids": block_ids,
        "gp_id": gp_id, "gp_ids": gp_ids,
        "creche_id": creche_id or None,
        "m1_month": m1_month, "m1_year": m1_year,
        "m2_month": m2_month, "m2_year": m2_year,
        "m3_month": m3_month, "m3_year": m3_year,
        "m4_month": m4_month, "m4_year": m4_year,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, "cend_date": cend_date,
        "c_status": c_status, "phases": phases
    }

    query = """
    SELECT COUNT(*) AS `Zig-Zag Pattern`
    FROM `tabAnthropromatic Data` AS ad_current
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id

    INNER JOIN `tabAnthropromatic Data` AS ad_m1
        ON ad_m1.childenrollguid = ad_current.childenrollguid
        AND ad_m1.do_you_have_height_weight = 1
        AND YEAR(ad_m1.measurement_taken_date) = %(m1_year)s
        AND MONTH(ad_m1.measurement_taken_date) = %(m1_month)s
        AND ad_m1.weight_for_age_zscore IS NOT NULL

    INNER JOIN `tabAnthropromatic Data` AS ad_m2
        ON ad_m2.childenrollguid = ad_current.childenrollguid
        AND ad_m2.do_you_have_height_weight = 1
        AND YEAR(ad_m2.measurement_taken_date) = %(m2_year)s
        AND MONTH(ad_m2.measurement_taken_date) = %(m2_month)s
        AND ad_m2.weight_for_age_zscore IS NOT NULL

    INNER JOIN `tabAnthropromatic Data` AS ad_m3
        ON ad_m3.childenrollguid = ad_current.childenrollguid
        AND ad_m3.do_you_have_height_weight = 1
        AND YEAR(ad_m3.measurement_taken_date) = %(m3_year)s
        AND MONTH(ad_m3.measurement_taken_date) = %(m3_month)s
        AND ad_m3.weight_for_age_zscore IS NOT NULL

    INNER JOIN `tabAnthropromatic Data` AS ad_m4
        ON ad_m4.childenrollguid = ad_current.childenrollguid
        AND ad_m4.do_you_have_height_weight = 1
        AND YEAR(ad_m4.measurement_taken_date) = %(m4_year)s
        AND MONTH(ad_m4.measurement_taken_date) = %(m4_month)s
        AND ad_m4.weight_for_age_zscore IS NOT NULL

    WHERE ad_current.do_you_have_height_weight = 1
      AND ad_current.weight_for_age_zscore IS NOT NULL
      AND YEAR(cgm.measurement_date) = %(year)s
      AND MONTH(cgm.measurement_date) = %(month)s
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
      AND cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))
      AND (
          CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
          -
          GREATEST(
              CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)),
              CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
              CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)),
              CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))
          )
      ) <= -0.5

    """

    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}

    sections = {"Col4": ["Zig-Zag Pattern"]}
    transformed_data = {
        section: [
            {"id": generate_id(field), "title": field, "value": result.get(field, 0)}
            for field in fields
        ]
        for section, fields in sections.items()
    }
    frappe.response["data"] = transformed_data


@frappe.whitelist()
def dashboard_section_snc(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None):

    
    # Parse year and month
    year = int(year) if year and str(year).isdigit() else None
    month = int(month) if month and str(month).isdigit() else None
    
    # Safety check: if year/month missing, return empty
    if not year or not month:
        transformed_data = {"Col1": [{"id": "snc_id", "title": "SNC", "value": 0}]}
        frappe.response["data"] = transformed_data
        return
    
    # Calculate date range for current month
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    # Get current user's partner
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner

    # Get user's geography mapping
    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    # Build comma-separated lists for geography filters
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id")) or None
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id")) or None
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id")) or None
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id")) or None

    # Parse phases
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None

    # Normalize empty strings to None
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    # ============= MONTH CALCULATIONS FOR DIFFERENT GF TYPES =============
    
    # GF1 & GF1+: Previous month (1 month ago)
    if month == 1:
        gf1_prev_month = 12
        gf1_prev_year = year - 1
    else:
        gf1_prev_month = month - 1
        gf1_prev_year = year

    # GF1 & GF1+: Fallback (2 months ago) if previous month data not available
    if month <= 2:
        gf1_fallback_month = month + 10
        gf1_fallback_year = year - 1
    else:
        gf1_fallback_month = month - 2
        gf1_fallback_year = year

    # GF2: Priority (2 months ago)
    if month <= 2:
        gf2_priority_month = month + 10
        gf2_priority_year = year - 1
    else:
        gf2_priority_month = month - 2
        gf2_priority_year = year

    # GF2: Fallback (3 months ago) if priority not available
    if month <= 3:
        gf2_fallback_month = month + 9
        gf2_fallback_year = year - 1
    else:
        gf2_fallback_month = month - 3
        gf2_fallback_year = year

    # Zig-Zag: Previous 4 months
    def _rollback_month(y, m, step):
        m = m - step
        while m <= 0:
            m += 12
            y -= 1
        return m, y

    zz_m1_month, zz_m1_year = _rollback_month(year, month, 1)
    zz_m2_month, zz_m2_year = _rollback_month(year, month, 2)
    zz_m3_month, zz_m3_year = _rollback_month(year, month, 3)
    zz_m4_month, zz_m4_year = _rollback_month(year, month, 4)

    # Prepare parameters for query
    params = {
        "end_date": end_date, 
        "year": year, 
        "month": month, 
        "start_date": start_date,
        "partner_id": partner_id, 
        "state_id": state_id,
        "state_ids": state_ids, 
        "district_id": district_id, 
        "district_ids": district_ids,
        "block_id": block_id, 
        "block_ids": block_ids,
        "gp_id": gp_id, 
        "gp_ids": gp_ids,
        "creche_id": creche_id or None,
        # GF1 & GF1+ months
        "gf1_prev_year": gf1_prev_year, 
        "gf1_prev_month": gf1_prev_month,
        "gf1_fallback_year": gf1_fallback_year, 
        "gf1_fallback_month": gf1_fallback_month,
        # GF2 months
        "gf2_priority_year": gf2_priority_year, 
        "gf2_priority_month": gf2_priority_month,
        "gf2_fallback_year": gf2_fallback_year, 
        "gf2_fallback_month": gf2_fallback_month,
        # Zig-Zag months
        "zz_m1_year": zz_m1_year, 
        "zz_m1_month": zz_m1_month,
        "zz_m2_year": zz_m2_year, 
        "zz_m2_month": zz_m2_month,
        "zz_m3_year": zz_m3_year, 
        "zz_m3_month": zz_m3_month,
        "zz_m4_year": zz_m4_year, 
        "zz_m4_month": zz_m4_month,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
        "c_status": c_status, 
        "phases": phases
    }

    # ============= MAIN QUERY =============
    query = """
    SELECT COUNT(DISTINCT ad_current.name) AS `SNC`
    FROM `tabAnthropromatic Data` AS ad_current
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id

    -- ===== GF1 & GF1+: Previous month data =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_prev
        ON ad_gf1_prev.childenrollguid = ad_current.childenrollguid
        AND ad_gf1_prev.do_you_have_height_weight = 1
        AND YEAR(ad_gf1_prev.measurement_taken_date) = %(gf1_prev_year)s
        AND MONTH(ad_gf1_prev.measurement_taken_date) = %(gf1_prev_month)s
        AND ad_gf1_prev.weight_for_age_zscore IS NOT NULL

    -- ===== GF1 & GF1+: Fallback (2 months ago) =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_fallback
        ON ad_gf1_fallback.childenrollguid = ad_current.childenrollguid
        AND ad_gf1_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_gf1_fallback.measurement_taken_date) = %(gf1_fallback_year)s
        AND MONTH(ad_gf1_fallback.measurement_taken_date) = %(gf1_fallback_month)s
        AND ad_gf1_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_gf1_prev.childenrollguid IS NULL

    -- ===== GF2: Priority (2 months ago) =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_priority
        ON ad_gf2_priority.childenrollguid = ad_current.childenrollguid
        AND ad_gf2_priority.do_you_have_height_weight = 1
        AND YEAR(ad_gf2_priority.measurement_taken_date) = %(gf2_priority_year)s
        AND MONTH(ad_gf2_priority.measurement_taken_date) = %(gf2_priority_month)s
        AND ad_gf2_priority.weight_for_age_zscore IS NOT NULL

    -- ===== GF2: Fallback (3 months ago) =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_fallback
        ON ad_gf2_fallback.childenrollguid = ad_current.childenrollguid
        AND ad_gf2_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_gf2_fallback.measurement_taken_date) = %(gf2_fallback_year)s
        AND MONTH(ad_gf2_fallback.measurement_taken_date) = %(gf2_fallback_month)s
        AND ad_gf2_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_gf2_priority.childenrollguid IS NULL

    -- ===== Zig-Zag: 4 Previous Months =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m1
        ON ad_zz_m1.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m1.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m1.measurement_taken_date) = %(zz_m1_year)s
        AND MONTH(ad_zz_m1.measurement_taken_date) = %(zz_m1_month)s
        AND ad_zz_m1.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m2
        ON ad_zz_m2.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m2.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m2.measurement_taken_date) = %(zz_m2_year)s
        AND MONTH(ad_zz_m2.measurement_taken_date) = %(zz_m2_month)s
        AND ad_zz_m2.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m3
        ON ad_zz_m3.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m3.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m3.measurement_taken_date) = %(zz_m3_year)s
        AND MONTH(ad_zz_m3.measurement_taken_date) = %(zz_m3_month)s
        AND ad_zz_m3.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m4
        ON ad_zz_m4.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m4.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m4.measurement_taken_date) = %(zz_m4_year)s
        AND MONTH(ad_zz_m4.measurement_taken_date) = %(zz_m4_month)s
        AND ad_zz_m4.weight_for_age_zscore IS NOT NULL

    WHERE ad_current.do_you_have_height_weight = 1
      AND ad_current.weight_for_age_zscore IS NOT NULL
      AND YEAR(cgm.measurement_date) = %(year)s
      AND MONTH(cgm.measurement_date) = %(month)s
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
      AND (%(cstart_date)s IS NULL OR cr.creche_opening_date >= %(cstart_date)s)
      AND (%(cend_date)s IS NULL OR cr.creche_opening_date <= %(cend_date)s)

      -- ===== SNC CONDITION: ANY of these conditions must be TRUE =====
      AND (
          -- CONDITION 1: GF1 - Decline > 0 from previous month (or fallback)
          (
              (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
              AND (
                  COALESCE(
                      CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                      CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                  ) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
              ) > 0
          )
          
          -- CONDITION 2: GF1+ - Decline <= -0.5 from previous month (or fallback)
          OR (
              (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
              AND (
                  CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                  -
                  COALESCE(
                      CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                      CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                  )
              ) <= -0.5
          )
          
          -- CONDITION 3: GF2 - Decline <= -0.5 from 2-3 months ago
          OR (
              (ad_gf2_priority.weight_for_age_zscore IS NOT NULL OR ad_gf2_fallback.weight_for_age_zscore IS NOT NULL)
              AND (
                  CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                  -
                  COALESCE(
                      CAST(ad_gf2_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                      CAST(ad_gf2_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                  )
              ) <= -0.5
          )
          
          -- CONDITION 4: Zig-Zag Pattern - Decline <= -0.5 from max of 4 previous months with alternating trend
          OR (
              ad_zz_m1.weight_for_age_zscore IS NOT NULL 
              AND ad_zz_m2.weight_for_age_zscore IS NOT NULL
              AND ad_zz_m3.weight_for_age_zscore IS NOT NULL 
              AND ad_zz_m4.weight_for_age_zscore IS NOT NULL
              AND (
                  CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                  -
                  GREATEST(
                      CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)),
                      CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                      CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)),
                      CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))
                  )
              ) <= -0.5
              -- Alternating increases
              AND (
                  (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))
                  OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)))
                  OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)))
                  OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
              )
              -- Alternating decreases
              AND (
                  (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))
                  OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)))
                  OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)))
                  OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
              )
          )
          OR ad_current.weight_for_age = 1
          OR ad_current.weight_for_height = 1
      )
    """

    # Execute query
    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}

    sections = {"Col1": ["SNC"]}
    transformed_data = {
        section: [
            {"id": generate_id(field), "title": field, "value": result.get(field, 0)}
            for field in fields
        ]
        for section, fields in sections.items()
    }
    frappe.response["data"] = transformed_data


