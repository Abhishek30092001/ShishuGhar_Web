from datetime import date
import frappe
import calendar
import json
import requests
from concurrent.futures import ThreadPoolExecutor
import hashlib
from urllib.parse import urlencode

# Global mapping to enforce exact grid positions (1-28 layout)
CARD_ORDER_MAPPING = {
    "No. of creches": 1,
    "Enrolled children": 2,
    "Children exited this month": 3,
    "Cumulative enrolled children": 4,
    "Current eligible children": 5,
    "Current enrolled children": 6,
    "Children enrolled this month": 7,
    "Cumulative exit children": 8,
    "No. of creches submitted attendance (All Days)": 9,
    "Anthro data submitted": 10,
    "Moderately underweight": 11,
    "Severely underweight": 12,
    "No. of creches not submitted attendance (All Days)": 13,
    "Anthro data not submitted": 14,
    "Moderately wasted": 15,
    "Severely wasted": 16,
    "Avg. no. of days creche opened": 17,
    "No. of Children measurement taken": 18,
    "Moderately stunted": 19,
    "Severely stunted": 20,
    "Maximum attendance in a day": 21,
    "Children measurement not taken": 22,
    "Growth faltering 1": 23,
    "Growth faltering 1+": 24,
    "Avg. attendance per day": 25,
    "Special Nutrition Care": 26,
    "Growth faltering 2": 27,
    "Zig-Zag Pattern": 28
}


@frappe.whitelist()
def dashboard_section_one(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None,
                village_id=None, creche_id=None, year=None, month=None, supervisor_id=None,
                c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):

    site_url = frappe.utils.get_url().rstrip('/')
    auth_header = frappe.get_request_header("Authorization")
    
    # API methods to call
    methods = [
        "dashboard_section_1", 
        "dashboard_section_2",
        "dashboard_section_3",
        "dashboard_section_4",
        "dashboard_section_5",
        "dashboard_section_6",
        "dashboard_section_7"
    ]

    # Prepare query parameters from all input parameters
    params = {
        "partner_id": partner_id,
        "state_id": state_id,
        "district_id": district_id,
        "gp_id": gp_id,
        "block_id": block_id,
        "village_id": village_id,
        "creche_id": creche_id,
        "year": year,
        "month": month,
        "supervisor_id": supervisor_id,
        "c_status": c_status,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "usr": usr,
        "pw": pw
    }
    
    # Remove None values to keep URLs clean
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    # Build query string
    query_string = urlencode(filtered_params)
    
    endpoints = []
    for method in methods:
        endpoint = f"{site_url}/api/method/frappe.val.ph_report_card.{method}"
        if query_string:
            endpoint += f"?{query_string}"
        endpoints.append(endpoint)

    def call_api(url):
        try:
            headers = {"Authorization": auth_header} if auth_header else {}
            response = requests.get(url, headers=headers, timeout=1200, verify=True)
            response.raise_for_status()
            return response.json()
        except:
            # Return empty data array if API call fails to maintain format
            return {"data": []}

    # Run all API calls in parallel
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(call_api, endpoints))

    # Merge all data arrays from different sections
    merged_data = []
    for result in results:
        if result and "data" in result and isinstance(result["data"], list):
            merged_data.extend(result["data"])

    # Sort merged data exactly by the new mapped ID sequence
    merged_data = sorted(merged_data, key=lambda x: x.get("ID", 99))
    
    frappe.response["data"] = merged_data


@frappe.whitelist()
def dashboard_section_1(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
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
        
    if creche_id:
        supervisor_id = None
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": None  # Safeguard for the enrolled_children subquery
    }
    # Query for section 1
    query = """
    SELECT
        IFNULL(FR.creche_no, 0) AS "No. of creches",
        IFNULL(FR.enrolled_children, 0) AS "Enrolled children",
        CASE
            WHEN FR.creche_no = 0 OR FR.creche_no IS NULL THEN 0
            ELSE CEIL(IFNULL(FR.no_days_creche_opened, 0) / FR.creche_no)
        END AS "Avg. no. of days creche opened",
        CASE
            WHEN FR.no_days_creche_opened = 0 OR FR.no_days_creche_opened IS NULL THEN 0
            ELSE ROUND(IFNULL(FR.no_children_present_creche_opened, 0) / FR.no_days_creche_opened, 1)
        END AS "Avg. attendance per day",
        IFNULL(FR.no_children_curr_active, 0) AS "Current enrolled children"
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
            AND (%(village_id)s IS NULL OR tc.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
            AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
            AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
            ) AS creche_no,

            -- Enrolled Children
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

            -- Count of Days Creche Opened
            (SELECT IFNULL(COUNT(*), 0)
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
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS no_days_creche_opened,

            -- Total Attendance when Creche Opened
            (SELECT IFNULL(COUNT(cal.name), 0)
            FROM `tabChild Attendance List` cal
            JOIN `tabChild Attendance` ca ON ca.name = cal.parent
            JOIN `tabCreche` cr ON cr.name = ca.creche_id
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
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS no_children_present_creche_opened,

            -- Currently active children
            (SELECT COUNT(*)
            FROM `tabChild Enrollment and Exit` cee
            INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
            WHERE (cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(end_date)s))
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
            AND (%(village_id)s IS NULL OR cee.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS no_children_curr_active
    ) FR;
    """
    
    transformed_data = frappe.db.sql(query, params, as_dict=True)
    query_status_mapping = {
        "Enrolled children": "enrolled_children",
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted" : "anthro_data_submitted",
        "No. of Children measurement taken" : "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)" : "no_of_creches_not_submitted_attendance",
        "Children measurement not taken" : "measurement_data_not_submitted",
        "Anthro data not submitted" : "anthro_data_not_submitted",
        "No. of creches" : "no_of_creches",
        "Growth faltering 1+" : "gf1_plus",
        "Zig-Zag Pattern" : "zig_zag",
        "Special Nutrition Care" : "snc"
    }
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}

@frappe.whitelist()
def dashboard_section_2(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
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
        
    if creche_id:
        supervisor_id = None
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status
    }
    # Query for section 2
    query = """
    SELECT
        IFNULL(FR.no_creche_attendance_submitted, 0) AS "No. of creches submitted attendance (All Days)",
        FR.no_creche_attendance_not_submitted AS "No. of creches not submitted attendance (All Days)",
        FR.Max_Attendance_in_a_Day AS "Maximum attendance in a day"
    FROM (
        SELECT
            -- Count of Active Creches (duplicated for dependency)
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
            AND (%(village_id)s IS NULL OR tc.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
            AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
            AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
            AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
            ) AS creche_no,
            -- Count of creches whose attendance submitted for all days
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
                    AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
                    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            ) AS creche_attendance
            WHERE elgdays <= attdays
            ) AS no_creche_attendance_submitted,
            -- Maximum Attendance in a Day
            IFNULL((
                SELECT MAX(daily_attendance)
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
                    AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
                    AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
                    AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                    AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                    
                    AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
                    GROUP BY ca.date_of_attendance
                ) AS daily_data
            ), 0) AS Max_Attendance_in_a_Day,
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
            AND (%(village_id)s IS NULL OR ca.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR ca.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS No_of_days_creche_attendance_submitted,
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
                    AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
                    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            ) AS creche_attendance
            WHERE elgdays > attdays
            ) AS no_creche_attendance_not_submitted
    ) FR;
    """
    
    transformed_data = frappe.db.sql(query, params, as_dict=True)
    query_status_mapping = {
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted" : "anthro_data_submitted",
        "No. of Children measurement taken" : "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)" : "no_of_creches_not_submitted_attendance",
        "Children measurement not taken" : "measurement_data_not_submitted",
        "Anthro data not submitted" : "anthro_data_not_submitted",
        "No. of creches" : "no_of_creches",
        "Growth faltering 1+" : "gf1_plus",
        "Zig-Zag Pattern" : "zig_zag",
        "Special Nutrition Care" : "snc"
    }
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}

@frappe.whitelist()
def dashboard_section_3(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
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
        
    if creche_id:
        supervisor_id = None
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status
    }
    # Query for section 3
   
    query="""

    SELECT
    FR.measurement_data_submitted AS "No. of Children measurement taken",
    FR.measurement_data_not_submitted AS "Children measurement not taken",
    FR.Total_Anthro_data_submitted AS "Anthro data submitted",
    FR.Total_Anthro_data_not_submitted AS "Anthro data not submitted"
FROM (
    SELECT
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
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS Total_Anthro_data_submitted,

        ( SELECT
            COUNT(DISTINCT cee.childenrollguid)
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
            AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
         
        ) AS measurement_data_submitted,

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
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(end_date)s)
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
            AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
            AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS measurement_data_not_submitted,
        
        (SELECT COUNT(*) AS Total_Anthro_data_not_submitted
        FROM `tabCreche` cr
        WHERE cr.creche_status_id = IFNULL(%(c_status)s, cr.creche_status_id)
        AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
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
) AS FR;
"""


    transformed_data = frappe.db.sql(query, params, as_dict=True)
    query_status_mapping = {
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted" : "anthro_data_submitted",
        "No. of Children measurement taken" : "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)" : "no_of_creches_not_submitted_attendance",
        "Children measurement not taken" : "measurement_data_not_submitted",
        "Anthro data not submitted" : "anthro_data_not_submitted",
        "No. of creches" : "no_of_creches",
        "Growth faltering 1+" : "gf1_plus",
        "Zig-Zag Pattern" : "zig_zag",
        "Special Nutrition Care" : "snc"
    }
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}

@frappe.whitelist()
def dashboard_section_4(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
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
        
    if creche_id:
        supervisor_id = None
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status
    }
    # # Query for section 4
    
    query="""
    SELECT
    FR.current_enrolled_children AS "Children enrolled this month",
    FR.cur_eligible_children AS "Current eligible children",
    FR.Total_Current_exit_children AS "Children exited this month",
    FR.cumm_enrolled_children AS "Cumulative enrolled children",
    FR.Total_Cumulative_exit_children AS "Cumulative exit children"
FROM (
    SELECT
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
        AND (%(village_id)s IS NULL OR cees.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS current_enrolled_children,

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
        AND (%(village_id)s IS NULL OR hf.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR hf.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (
            %(c_status)s = 1
            OR (
                %(c_status)s != 1
                AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
                AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                    OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )
        )
        ) AS cur_eligible_children,

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
        AND (%(village_id)s IS NULL OR cec.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cec.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS Total_Current_exit_children,

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
        AND (%(village_id)s IS NULL OR cee.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS cumm_enrolled_children,

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
        AND (%(village_id)s IS NULL OR cmec.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cmec.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        ) AS Total_Cumulative_exit_children
) AS FR
"""

    transformed_data = frappe.db.sql(query, params, as_dict=True)
    query_status_mapping = {
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted" : "anthro_data_submitted",
        "No. of Children measurement taken" : "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)" : "no_of_creches_not_submitted_attendance",
        "Children measurement not taken" : "measurement_data_not_submitted",
        "Anthro data not submitted" : "anthro_data_not_submitted",
        "No. of creches" : "no_of_creches",
        "Growth faltering 1+" : "gf1_plus",
        "Zig-Zag Pattern" : "zig_zag",
        "Special Nutrition Care" : "snc"
    }
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}


@frappe.whitelist()
def dashboard_section_5(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
    
    # Calculate previous month and fallback month
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
        
    if creche_id:
        supervisor_id = None
    
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status
    }
    
    # Query for section 5
    query = """
    SELECT
        FR.Total_Underweight_children AS "Moderately underweight",
        FR.Total_MAM_children AS "Moderately wasted",
        FR.Total_Stunted_children AS "Moderately stunted",
        FR.Total_Severely_stunted_children AS "Severely stunted"
    FROM (
        SELECT
            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.weight_for_age = 2
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Underweight_children,

            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.weight_for_height = 2
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_MAM_children,

            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.height_for_age = 2
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s) 
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
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Stunted_children,

            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.height_for_age = 1
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Severely_stunted_children
    ) AS FR;
    """

    transformed_data = frappe.db.sql(query, params, as_dict=True)
    
    query_status_mapping = {
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted": "anthro_data_submitted",
        "No. of Children measurement taken": "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)": "no_of_creches_not_submitted_attendance",
        "Children measurement not taken": "measurement_data_not_submitted",
        "Anthro data not submitted": "anthro_data_not_submitted",
        "No. of creches": "no_of_creches",
        "Growth faltering 1+": "gf1_plus",
        "Zig-Zag Pattern": "zig_zag",
        "Special Nutrition Care": "snc"
    }
    
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []} 



@frappe.whitelist()
def dashboard_section_6(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):

    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
    
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

    # Compute fallback month/year (three months ago) for GF2
    if month <= 2:
        priority_month = month + 10
        priority_year = year - 1
    else:
        priority_month = month - 2
        priority_year = year

    if month <= 3:
        fallback_month = month + 9
        fallback_year = year - 1
    else:
        fallback_month = month - 3
        fallback_year = year

    if creche_id:
        supervisor_id = None
    
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "priority_year": priority_year,
        "priority_month": priority_month,
        "fallback_year": fallback_year,
        "fallback_month": fallback_month,
        "supervisor_id": supervisor_id,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "c_status": c_status
    }
    
    # Query for section 6
    query = """
    SELECT
        FR.Total_Severely_underweight_children AS "Severely underweight",
        FR.Total_SAM_children AS "Severely wasted",
        FR.Total_GF1 AS "Growth faltering 1",
        FR.Total_GF2 AS "Growth faltering 2"
    FROM (
        SELECT
            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.weight_for_age = 1
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_Severely_underweight_children,

            (SELECT COUNT(ad.name)
            FROM `tabAnthropromatic Data` AS ad
            JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            WHERE YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND ad.do_you_have_height_weight = 1
            AND ad.weight_for_height = 1
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            ) AS Total_SAM_children,

            -- CORRECTED: GF1 logic now matches dashboard_section_gf exactly
            (SELECT COUNT(ad.childenrollguid) AS gf1
            FROM `tabAnthropromatic Data` AS ad
            INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            LEFT JOIN `tabAnthropromatic Data` AS ad_prev
                ON ad_prev.childenrollguid = ad.childenrollguid
                AND ad_prev.do_you_have_height_weight = 1
                AND YEAR(ad_prev.measurement_taken_date) = %(lyear)s
                AND MONTH(ad_prev.measurement_taken_date) = %(lmonth)s
                AND ad_prev.weight_for_age_zscore IS NOT NULL
            LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
                ON ad_fallback.childenrollguid = ad.childenrollguid
                AND ad_fallback.do_you_have_height_weight = 1
                AND YEAR(ad_fallback.measurement_taken_date) = %(pyear)s
                AND MONTH(ad_fallback.measurement_taken_date) = %(plmonth)s
                AND ad_fallback.weight_for_age_zscore IS NOT NULL
                AND ad_prev.childenrollguid IS NULL
            WHERE
                ad.do_you_have_height_weight = 1
                AND ad.weight_for_age_zscore IS NOT NULL
                AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
                AND (COALESCE(ad_prev.weight_for_age_zscore, ad_fallback.weight_for_age_zscore) - ad.weight_for_age_zscore) > 0
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND cee.date_of_enrollment <= %(end_date)s
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
                AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
            ) AS Total_GF1,

            /* GF2 LOGIC - Unchanged */
            (SELECT COUNT(*)
            FROM `tabAnthropromatic Data` AS ad
            INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            LEFT JOIN `tabAnthropromatic Data` AS ad_priority ON
                ad_priority.childenrollguid = ad.childenrollguid
                AND ad_priority.do_you_have_height_weight = 1
                AND YEAR(ad_priority.measurement_taken_date) = %(priority_year)s
                AND MONTH(ad_priority.measurement_taken_date) = %(priority_month)s
                AND ad_priority.weight_for_age_zscore IS NOT NULL
            LEFT JOIN `tabAnthropromatic Data` AS ad_fallback ON
                ad_fallback.childenrollguid = ad.childenrollguid
                AND ad_fallback.do_you_have_height_weight = 1
                AND YEAR(ad_fallback.measurement_taken_date) = %(fallback_year)s
                AND MONTH(ad_fallback.measurement_taken_date) = %(fallback_month)s
                AND ad_fallback.weight_for_age_zscore IS NOT NULL
                AND ad_priority.childenrollguid IS NULL
            WHERE
                ad.do_you_have_height_weight = 1
                AND ad.weight_for_age_zscore IS NOT NULL
                AND (ad_priority.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
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
                AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                AND (%(cstart_date)s IS NULL OR cr.creche_opening_date >= %(cstart_date)s)
                AND (%(cend_date)s IS NULL OR cr.creche_opening_date <= %(cend_date)s)
            ) AS Total_GF2
    ) AS FR;
    """

    transformed_data = frappe.db.sql(query, params, as_dict=True)
    query_status_mapping = {
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted": "anthro_data_submitted",
        "No. of Children measurement taken": "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)": "no_of_creches_not_submitted_attendance",
        "Children measurement not taken": "measurement_data_not_submitted",
        "Anthro data not submitted": "anthro_data_not_submitted",
        "No. of creches": "no_of_creches",
        "Growth faltering 1+": "gf1_plus",
        "Zig-Zag Pattern": "zig_zag",
        "Special Nutrition Care": "snc"
    }
    
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}


@frappe.whitelist()
def dashboard_section_7(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, c_status=None, cstart_date=None, cend_date=None, usr=None, pw=None):
    
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
    year = int(year)
    month = int(month)
    
    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    
    # Initialize empty lists for geography filters
    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    
    # Fetch geography mapping if email is provided and no specific geography filters are set
    if usr and not (state_id or district_id or block_id or gp_id):
        geography_query = """
            SELECT
                ugm.state_id,
                ugm.district_id,
                ugm.block_id,
                ugm.gp_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent
            WHERE u.email = %s
        """
        current_user_geography = frappe.db.sql(geography_query, usr, as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
    
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
    
    if creche_id:
        supervisor_id = None
    
    # Convert lists to comma-separated strings if they exist, otherwise set to None
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    
    params = {
        "end_date": end_date,
        "year": year,
        "month": month,
        "start_date": start_date,
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "creche_id": creche_id,
        "village_id": village_id,
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
        "c_status": c_status
    }
    
    # Query for section 7 - GF1, GF1+, GF2, Zig-Zag Pattern, and SNC
    query = """
    SELECT
        FR.Total_GF1_Plus AS "Growth faltering 1+",
        FR.Total_Zig_Zag AS "Zig-Zag Pattern",
        FR.Total_SNC AS "Special Nutrition Care"
    FROM (
        SELECT
            (SELECT COUNT(ad.childenrollguid)
            FROM `tabAnthropromatic Data` AS ad
            INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            LEFT JOIN `tabAnthropromatic Data` AS ad_prev1 ON
                ad_prev1.childenrollguid = ad.childenrollguid
                AND ad_prev1.do_you_have_height_weight = 1
                AND YEAR(ad_prev1.measurement_taken_date) = %(gf1_prev_year)s
                AND MONTH(ad_prev1.measurement_taken_date) = %(gf1_prev_month)s
                AND ad_prev1.weight_for_age_zscore IS NOT NULL
            LEFT JOIN `tabAnthropromatic Data` AS ad_prev2 ON
                ad_prev2.childenrollguid = ad.childenrollguid
                AND ad_prev2.do_you_have_height_weight = 1
                AND YEAR(ad_prev2.measurement_taken_date) = %(gf1_fallback_year)s
                AND MONTH(ad_prev2.measurement_taken_date) = %(gf1_fallback_month)s
                AND ad_prev2.weight_for_age_zscore IS NOT NULL
                AND ad_prev1.childenrollguid IS NULL
            WHERE
                ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND ad.weight_for_age_zscore IS NOT NULL
                AND cee.date_of_enrollment <= %(end_date)s
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
                AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
                AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                AND (ad_prev1.weight_for_age_zscore IS NOT NULL OR ad_prev2.weight_for_age_zscore IS NOT NULL)
                AND (
                    CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
                    -
                    COALESCE(
                        CAST(ad_prev1.weight_for_age_zscore AS DECIMAL(10,4)),
                        CAST(ad_prev2.weight_for_age_zscore AS DECIMAL(10,4))
                    )
                ) <= -0.5
            ) AS Total_GF1_Plus,

            (SELECT COUNT(*)
            FROM `tabAnthropromatic Data` AS ad_current
            INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid
            INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
            INNER JOIN `tabAnthropromatic Data` AS ad_m1
                ON ad_m1.childenrollguid = ad_current.childenrollguid
                AND ad_m1.do_you_have_height_weight = 1
                AND YEAR(ad_m1.measurement_taken_date) = %(zz_m1_year)s
                AND MONTH(ad_m1.measurement_taken_date) = %(zz_m1_month)s
                AND ad_m1.weight_for_age_zscore IS NOT NULL
            INNER JOIN `tabAnthropromatic Data` AS ad_m2
                ON ad_m2.childenrollguid = ad_current.childenrollguid
                AND ad_m2.do_you_have_height_weight = 1
                AND YEAR(ad_m2.measurement_taken_date) = %(zz_m2_year)s
                AND MONTH(ad_m2.measurement_taken_date) = %(zz_m2_month)s
                AND ad_m2.weight_for_age_zscore IS NOT NULL
            INNER JOIN `tabAnthropromatic Data` AS ad_m3
                ON ad_m3.childenrollguid = ad_current.childenrollguid
                AND ad_m3.do_you_have_height_weight = 1
                AND YEAR(ad_m3.measurement_taken_date) = %(zz_m3_year)s
                AND MONTH(ad_m3.measurement_taken_date) = %(zz_m3_month)s
                AND ad_m3.weight_for_age_zscore IS NOT NULL
            INNER JOIN `tabAnthropromatic Data` AS ad_m4
                ON ad_m4.childenrollguid = ad_current.childenrollguid
                AND ad_m4.do_you_have_height_weight = 1
                AND YEAR(ad_m4.measurement_taken_date) = %(zz_m4_year)s
                AND MONTH(ad_m4.measurement_taken_date) = %(zz_m4_month)s
                AND ad_m4.weight_for_age_zscore IS NOT NULL
            WHERE ad_current.do_you_have_height_weight = 1
              AND ad_current.weight_for_age_zscore IS NOT NULL
              AND YEAR(cgm.measurement_date) = %(year)s
              AND MONTH(cgm.measurement_date) = %(month)s
              AND cee.date_of_enrollment <= %(end_date)s
              AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
              AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
              AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
              AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
              AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
              AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
              AND (%(cstart_date)s IS NULL OR cr.creche_opening_date >= %(cstart_date)s)
              AND (%(cend_date)s IS NULL OR cr.creche_opening_date <= %(cend_date)s)
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
            ) AS Total_Zig_Zag,

            (SELECT COUNT(DISTINCT ad_current.name)
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
              AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
              AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
              AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
              AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
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
            ) AS Total_SNC
    ) AS FR;
    """

    transformed_data = frappe.db.sql(query, params, as_dict=True)
    
    query_status_mapping = {
        "Current enrolled children": "active_children",
        "Children enrolled this month": "enrolled_children_this_month",
        "Current eligible children": "current_eligible_children",
        "Children exited this month": "exited_children_this_month",
        "Moderately underweight": "moderately_underweight",
        "Moderately wasted": "moderately_wasted",
        "Moderately stunted": "moderately_stunted",
        "Growth faltering 1": "gf1",
        "Severely underweight": "severly_underweight",
        "Severely wasted": "severly_wasted",
        "Severely stunted": "severly_stunted",
        "Growth faltering 2": "gf2",
        "No. of creches submitted attendance (All Days)": "no_creche_attendance_submitted",
        "Anthro data submitted": "anthro_data_submitted",
        "No. of Children measurement taken": "measurement_data_submitted",
        "No. of creches not submitted attendance (All Days)": "no_of_creches_not_submitted_attendance",
        "Children measurement not taken": "measurement_data_not_submitted",
        "Anthro data not submitted": "anthro_data_not_submitted",
        "No. of creches": "no_of_creches",
        "Growth faltering 1+": "gf1_plus",
        "Zig-Zag Pattern": "zig_zag",
        "Special Nutrition Care": "snc"
    }
    
    if transformed_data:
        flat_data = transformed_data[0]
        formatted_data = []
        for key in flat_data:
            item = {
                "ID": CARD_ORDER_MAPPING.get(key, 99),
                "title": key,
                "value": flat_data[key]
            }
            if key in query_status_mapping:
                item["query_status"] = query_status_mapping[key]
            formatted_data.append(item)
        frappe.response["data"] = formatted_data
    else:
        frappe.response["data"] = {"data": []}