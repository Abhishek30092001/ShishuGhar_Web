import frappe
from frappe import _
import math
from datetime import date, datetime, timedelta
import calendar
from frappe.utils import nowdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("State"), "fieldname": "state_name", "fieldtype": "Data", "width": 120},
        {"label": _("District"), "fieldname": "district_name", "fieldtype": "Data", "width": 120},
        {"label": _("Block"), "fieldname": "block_name", "fieldtype": "Data", "width": 120},
        {"label": _("GP"), "fieldname": "gp_name", "fieldtype": "Data", "width": 120},
        {"label": _("Creche"), "fieldname": "creche_name", "fieldtype": "Data", "width": 180},
        {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": _("User"), "fieldname": "full_name", "fieldtype": "Data", "width": 150},
        {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 150},
        {"label": _("Check-in Date"), "fieldname": "date_of_checkin", "fieldtype": "Date", "width": 120},
        {"label": _("Check-in Time"), "fieldname": "check_in_time", "fieldtype": "Data", "width": 130},
        {"label": _("Distance (m)"), "fieldname": "distance", "fieldtype": "Int", "width": 120},
        {
            "label": _(">200 m"), 
            "fieldname": "category_above_200", 
            "fieldtype": "HTML", 
            "width": 95,
            "align": "center"
        },
        {
            "label": _("51-200 m"), 
            "fieldname": "category_50_200", 
            "fieldtype": "HTML", 
            "width": 95,
            "align": "center"
        },
        {
            "label": _("21-50 m"), 
            "fieldname": "category_20_50", 
            "fieldtype": "HTML", 
            "width": 95,
            "align": "center"
        },
        {
            "label": _("0-20 m"), 
            "fieldname": "category_0_20", 
            "fieldtype": "HTML", 
            "width": 95,
            "align": "center"
        },
    ]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_data(filters=None):
    month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
    year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") if filters else current_user_partner

    conditions = []
    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    # Creche Age Filter
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

    # User Geography Mapping filter
    # Get user's geography mapping for multiple states/districts/blocks/GPs
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
    # Create comma-separated strings for multiple geography IDs
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))

    conditions.append("chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s")

    # Partner filter
    if partner_id:
        conditions.append("chi.partner_id = %(partner)s")
        params["partner"] = partner_id

    # State filter with multiple geography handling
    if filters and filters.get("state"):
        conditions.append("chi.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(chi.state_id, %(state_ids)s)")
            params["state_ids"] = state_ids
            params["state"] = None

    # District filter with multiple geography handling
    if filters and filters.get("district"):
        conditions.append("chi.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(chi.district_id, %(district_ids)s)")
            params["district_ids"] = district_ids
            params["district"] = None

    # Block filter with multiple geography handling
    if filters and filters.get("block"):
        conditions.append("chi.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(chi.block_id, %(block_ids)s)")
            params["block_ids"] = block_ids
            params["block"] = None

    # GP filter with multiple geography handling
    if filters and filters.get("gp"):
        conditions.append("chi.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
        params["gp_ids"] = None
    else:
        if gp_ids:
            conditions.append("FIND_IN_SET(chi.gp_id, %(gp_ids)s)")
            params["gp_ids"] = gp_ids
            params["gp"] = None
        
    if filters.get("creche"):
        conditions.append("chi.creche_id = %(creche)s")
        params["creche"] = filters.get("creche")
        
    if filters.get("user"):
        conditions.append("chi.appcreated_by = %(user)s")
        params["user"] = filters.get("user")

    if filters.get("designation"):
        conditions.append("u.type = %(designation)s")
        params["designation"] = filters.get("designation")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Query to get all individual check-ins with user details
    query = f"""
    SELECT 
        chi.name as checkin_id,
        chi.date_of_checkin,
        DATE_FORMAT(chi.appcreated_on, '%%h:%%i %%p') AS check_in_time,
        chi.appcreated_by,
        u.full_name,
        u.type as designation,
        cr.creche_name,
        cr.creche_id,
        b.block_name,
        gp.gp_name,
        s.state_name,
        d.district_name,
        chi.latitude as check_in_lat,
        chi.longitude as check_in_lon,
        cr.latitude as creche_lat,
        cr.longitude as creche_lon
    FROM `tabCreche Check In` AS chi
    INNER JOIN `tabUser` u ON chi.appcreated_by = u.name
    INNER JOIN `tabCreche` cr ON cr.name = chi.creche_id
    INNER JOIN `tabState` s ON s.name = chi.state_id
    INNER JOIN `tabDistrict` d ON d.name = chi.district_id
    INNER JOIN `tabBlock` AS b ON b.name = chi.block_id
    INNER JOIN `tabGram Panchayat` AS gp ON gp.name = chi.gp_id
    {where_clause}
    ORDER BY s.state_name, d.district_name, b.block_name, gp.gp_name, cr.creche_name, u.full_name, u.type, chi.date_of_checkin
    """
    checkin_records = frappe.db.sql(query, params, as_dict=True)
    data = []

    # Initialize counters for total row
    total_0_20 = 0
    total_20_50 = 0
    total_50_200 = 0
    total_above_200 = 0

    for record in checkin_records:
        # Calculate distance
        distance = None
        try:
            lat1 = float(record['check_in_lat']) if record.get('check_in_lat') else None
            lon1 = float(record['check_in_lon']) if record.get('check_in_lon') else None
            lat2 = float(record['creche_lat']) if record.get('creche_lat') else None
            lon2 = float(record['creche_lon']) if record.get('creche_lon') else None
            
            if all(v is not None for v in [lat1, lon1, lat2, lon2]):
                distance = round(haversine(lat1, lon1, lat2, lon2))
        except:
            distance = None

        # Create HTML for distance indicators and update counters
        if distance is not None:
            if distance <= 20:
                cat_0_20 = """<span style="color: #4CAF50; font-weight: bold; font-size: 16px;">✓</span>"""
                cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
                cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
                cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
                total_0_20 += 1
            elif 20 < distance <= 50:
                cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
                cat_20_50 = """<span style="color: #FFEB3B; font-weight: bold; font-size: 16px;">✓</span>"""
                cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
                cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
                total_20_50 += 1
            elif 50 < distance <= 200:
                cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
                cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
                cat_50_200 = """<span style="color: #FF9800; font-weight: bold; font-size: 16px;">✓</span>"""
                cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
                total_50_200 += 1
            else:
                cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
                cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
                cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
                cat_above_200 = """<span style="color: #F44336; font-weight: bold; font-size: 16px;">✓</span>"""
                total_above_200 += 1
        else:
            cat_0_20 = cat_20_50 = cat_50_200 = cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""

        data.append({
            "date_of_checkin": record.get('date_of_checkin'),
            "check_in_time": record.get('check_in_time'),
            "full_name": record.get('full_name'),
            "designation": record.get('designation'),
            "creche_name": record.get('creche_name'),
            "creche_id": record.get('creche_id'),
            "state_name": record.get('state_name'),
            "district_name": record.get('district_name'),
            "block_name": record.get('block_name'),
            "gp_name": record.get('gp_name'),
            "distance": distance,
            "category_0_20": cat_0_20,
            "category_20_50": cat_20_50,
            "category_50_200": cat_50_200,
            "category_above_200": cat_above_200
        })
    # Add TOTAL row at the end if there are records
    if data:
        total_row = {
            "full_name": """<b style="font-size: 14px;">TOTAL</b>""",
            "designation": "",
            "state_name": "",
            "district_name": "",
            "block_name": "",
            "gp_name": "",
            "creche_name": "",
            "creche_id": "",
            "date_of_checkin": "",
            "check_in_time": "",
            "category_0_20": f"""<b style="font-size: 14px;">{total_0_20}</b>""",
            "category_20_50": f"""<b style="font-size: 14px;">{total_20_50}</b>""",
            "category_50_200": f"""<b style="font-size: 14px;">{total_50_200}</b>""",
            "category_above_200": f"""<b style="font-size: 14px;">{total_above_200}</b>""",
            "is_total_row": True  # This can be used for additional styling if needed
        }
        data.append(total_row)
    return data










#Backup Before age of creche filter
# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("State"), "fieldname": "state_name", "fieldtype": "Data", "width": 120},
#         {"label": _("District"), "fieldname": "district_name", "fieldtype": "Data", "width": 120},
#         {"label": _("Block"), "fieldname": "block_name", "fieldtype": "Data", "width": 120},
#         {"label": _("GP"), "fieldname": "gp_name", "fieldtype": "Data", "width": 120},
#         {"label": _("Creche"), "fieldname": "creche_name", "fieldtype": "Data", "width": 180},
#         {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": _("User"), "fieldname": "full_name", "fieldtype": "Data", "width": 150},
#         {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 150},
#         {"label": _("Check-in Date"), "fieldname": "date_of_checkin", "fieldtype": "Date", "width": 120},
#         {"label": _("Check-in Time"), "fieldname": "check_in_time", "fieldtype": "Data", "width": 130},
#         {"label": _("Distance (m)"), "fieldname": "distance", "fieldtype": "Int", "width": 120},
#         {
#             "label": _(">200 m"), 
#             "fieldname": "category_above_200", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },
#         {
#             "label": _("51-200 m"), 
#             "fieldname": "category_50_200", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },
#         {
#             "label": _("21-50 m"), 
#             "fieldname": "category_20_50", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },
#         {
#             "label": _("0-20 m"), 
#             "fieldname": "category_0_20", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },



#     ]

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  # Earth radius in meters
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") if filters else current_user_partner

#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }



#     # User Geography Mapping filter
#     # Get user's geography mapping for multiple states/districts/blocks/GPs
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
#     # Create comma-separated strings for multiple geography IDs
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))


#     conditions.append("chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s")

#     # Partner filter
#     if partner_id:
#         conditions.append("chi.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     # State filter with multiple geography handling
#     if filters and filters.get("state"):
#         conditions.append("chi.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(chi.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     # District filter with multiple geography handling
#     if filters and filters.get("district"):
#         conditions.append("chi.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(chi.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     # Block filter with multiple geography handling
#     if filters and filters.get("block"):
#         conditions.append("chi.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(chi.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     # GP filter with multiple geography handling
#     if filters and filters.get("gp"):
#         conditions.append("chi.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(chi.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None
        
#     if filters.get("creche"):
#         conditions.append("chi.creche_id = %(creche)s")
#         params["creche"] = filters.get("creche")
        
#     if filters.get("user"):
#         conditions.append("chi.appcreated_by = %(user)s")
#         params["user"] = filters.get("user")

#     if filters.get("designation"):
#         conditions.append("u.type = %(designation)s")
#         params["designation"] = filters.get("designation")

#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     # Query to get all individual check-ins with user details
#     query = f"""
#     SELECT 
#         chi.name as checkin_id,
#         chi.date_of_checkin,
#         DATE_FORMAT(chi.appcreated_on, '%%h:%%i %%p') AS check_in_time,
#         chi.appcreated_by,
#         u.full_name,
#         u.type as designation,
#         cr.creche_name,
#         cr.creche_id,
#         b.block_name,
#         gp.gp_name,
#         s.state_name,
#         d.district_name,
#         chi.latitude as check_in_lat,
#         chi.longitude as check_in_lon,
#         cr.latitude as creche_lat,
#         cr.longitude as creche_lon
#     FROM `tabCreche Check In` AS chi
#     INNER JOIN `tabUser` u ON chi.appcreated_by = u.name
#     INNER JOIN `tabCreche` cr ON cr.name = chi.creche_id
#     INNER JOIN `tabState` s ON s.name = chi.state_id
#     INNER JOIN `tabDistrict` d ON d.name = chi.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = chi.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = chi.gp_id
#     {where_clause}
#     ORDER BY s.state_name, d.district_name, b.block_name, gp.gp_name, cr.creche_name, u.full_name, u.type, chi.date_of_checkin
#     """
#     checkin_records = frappe.db.sql(query, params, as_dict=True)
#     data = []

#     # Initialize counters for total row
#     total_0_20 = 0
#     total_20_50 = 0
#     total_50_200 = 0
#     total_above_200 = 0

#     for record in checkin_records:
#         # Calculate distance
#         distance = None
#         try:
#             lat1 = float(record['check_in_lat']) if record.get('check_in_lat') else None
#             lon1 = float(record['check_in_lon']) if record.get('check_in_lon') else None
#             lat2 = float(record['creche_lat']) if record.get('creche_lat') else None
#             lon2 = float(record['creche_lon']) if record.get('creche_lon') else None
            
#             if all(v is not None for v in [lat1, lon1, lat2, lon2]):
#                 distance = round(haversine(lat1, lon1, lat2, lon2))
#         except:
#             distance = None

#         # Create HTML for distance indicators and update counters
#         if distance is not None:
#             if distance <= 20:
#                 cat_0_20 = """<span style="color: #4CAF50; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 total_0_20 += 1
#             elif 20 < distance <= 50:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #FFEB3B; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 total_20_50 += 1
#             elif 50 < distance <= 200:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #FF9800; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 total_50_200 += 1
#             else:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #F44336; font-weight: bold; font-size: 16px;">✓</span>"""
#                 total_above_200 += 1
#         else:
#             cat_0_20 = cat_20_50 = cat_50_200 = cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""

#         data.append({
#             "date_of_checkin": record.get('date_of_checkin'),
#             "check_in_time": record.get('check_in_time'),
#             "full_name": record.get('full_name'),
#             "designation": record.get('designation'),
#             "creche_name": record.get('creche_name'),
#             "creche_id": record.get('creche_id'),
#             "state_name": record.get('state_name'),
#             "district_name": record.get('district_name'),
#             "block_name": record.get('block_name'),
#             "gp_name": record.get('gp_name'),
#             "distance": distance,
#             "category_0_20": cat_0_20,
#             "category_20_50": cat_20_50,
#             "category_50_200": cat_50_200,
#             "category_above_200": cat_above_200
#         })
#     # Add TOTAL row at the end if there are records
#     if data:
#         total_row = {
#             "full_name": """<b style="font-size: 14px;">TOTAL</b>""",
#             "designation": "",
#             "state_name": "",
#             "district_name": "",
#             "block_name": "",
#             "gp_name": "",
#             "creche_name": "",
#             "creche_id": "",
#             "date_of_checkin": "",
#             "check_in_time": "",
#             "category_0_20": f"""<b style="font-size: 14px;">{total_0_20}</b>""",
#             "category_20_50": f"""<b style="font-size: 14px;">{total_20_50}</b>""",
#             "category_50_200": f"""<b style="font-size: 14px;">{total_50_200}</b>""",
#             "category_above_200": f"""<b style="font-size: 14px;">{total_above_200}</b>""",
#             "is_total_row": True  # This can be used for additional styling if needed
#         }
#         data.append(total_row)
#     return data





#13-09-2024
# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("State"), "fieldname": "state_name", "fieldtype": "Data", "width": 120},
#         {"label": _("District"), "fieldname": "district_name", "fieldtype": "Data", "width": 120},
#         {"label": _("Block"), "fieldname": "block_name", "fieldtype": "Data", "width": 120},
#         {"label": _("GP"), "fieldname": "gp_name", "fieldtype": "Data", "width": 120},
#         {"label": _("Creche"), "fieldname": "creche_name", "fieldtype": "Data", "width": 180},
#         {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": _("User"), "fieldname": "full_name", "fieldtype": "Data", "width": 150},
#         {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 150},
#         {"label": _("Check-in Date"), "fieldname": "date_of_checkin", "fieldtype": "Date", "width": 120},
#         {"label": _("Check-in Time"), "fieldname": "check_in_time", "fieldtype": "Data", "width": 130},
#         {"label": _("Distance (m)"), "fieldname": "distance", "fieldtype": "Int", "width": 120},
#         {
#             "label": _(">200 m"), 
#             "fieldname": "category_above_200", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },
#         {
#             "label": _("51-200 m"), 
#             "fieldname": "category_50_200", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },
#         {
#             "label": _("21-50 m"), 
#             "fieldname": "category_20_50", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },
#         {
#             "label": _("0-20 m"), 
#             "fieldname": "category_0_20", 
#             "fieldtype": "HTML", 
#             "width": 95,
#             "align": "center"
#         },



#     ]

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  # Earth radius in meters
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     # Process filters
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
#     # Create date range for the selected month and year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     # Initialize filters
#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }

#     conditions.append("chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s")

#     if filters.get("state"):
#         conditions.append("chi.state_id = %(state)s")
#         params["state"] = filters.get("state")
        
#     if filters.get("district"):
#         conditions.append("chi.district_id = %(district)s")
#         params["district"] = filters.get("district")
        
#     if filters.get("block"):
#         conditions.append("chi.block_id = %(block)s")
#         params["block"] = filters.get("block")
        
#     if filters.get("gp"):
#         conditions.append("chi.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
        
#     if filters.get("creche"):
#         conditions.append("chi.creche_id = %(creche)s")
#         params["creche"] = filters.get("creche")
        
#     if filters.get("user"):
#         conditions.append("chi.appcreated_by = %(user)s")
#         params["user"] = filters.get("user")

#     if filters.get("designation"):
#         conditions.append("u.type = %(designation)s")
#         params["designation"] = filters.get("designation")

#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     # Query to get all individual check-ins with user details
#     query = f"""
#     SELECT 
#         chi.name as checkin_id,
#         chi.date_of_checkin,
#         DATE_FORMAT(chi.appcreated_on, '%%h:%%i %%p') AS check_in_time,
#         chi.appcreated_by,
#         u.full_name,
#         u.type as designation,
#         cr.creche_name,
#         cr.creche_id,
#         b.block_name,
#         gp.gp_name,
#         s.state_name,
#         d.district_name,
#         chi.latitude as check_in_lat,
#         chi.longitude as check_in_lon,
#         cr.latitude as creche_lat,
#         cr.longitude as creche_lon
#     FROM `tabCreche Check In` AS chi
#     INNER JOIN `tabUser` u ON chi.appcreated_by = u.name
#     INNER JOIN `tabCreche` cr ON cr.name = chi.creche_id
#     INNER JOIN `tabState` s ON s.name = chi.state_id
#     INNER JOIN `tabDistrict` d ON d.name = chi.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = chi.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = chi.gp_id
#     {where_clause}
#     ORDER BY s.state_name, d.district_name, b.block_name, gp.gp_name, cr.creche_name, u.full_name, u.type, chi.date_of_checkin
#     """
#     checkin_records = frappe.db.sql(query, params, as_dict=True)
#     data = []

#     # Initialize counters for total row
#     total_0_20 = 0
#     total_20_50 = 0
#     total_50_200 = 0
#     total_above_200 = 0

#     for record in checkin_records:
#         # Calculate distance
#         distance = None
#         try:
#             lat1 = float(record['check_in_lat']) if record.get('check_in_lat') else None
#             lon1 = float(record['check_in_lon']) if record.get('check_in_lon') else None
#             lat2 = float(record['creche_lat']) if record.get('creche_lat') else None
#             lon2 = float(record['creche_lon']) if record.get('creche_lon') else None
            
#             if all(v is not None for v in [lat1, lon1, lat2, lon2]):
#                 distance = round(haversine(lat1, lon1, lat2, lon2))
#         except:
#             distance = None

#         # Create HTML for distance indicators and update counters
#         if distance is not None:
#             if distance <= 20:
#                 cat_0_20 = """<span style="color: #4CAF50; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 total_0_20 += 1
#             elif 20 < distance <= 50:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #FFEB3B; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 total_20_50 += 1
#             elif 50 < distance <= 200:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #FF9800; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 total_50_200 += 1
#             else:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #F44336; font-weight: bold; font-size: 16px;">✓</span>"""
#                 total_above_200 += 1
#         else:
#             cat_0_20 = cat_20_50 = cat_50_200 = cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""

#         data.append({
#             "date_of_checkin": record.get('date_of_checkin'),
#             "check_in_time": record.get('check_in_time'),
#             "full_name": record.get('full_name'),
#             "designation": record.get('designation'),
#             "creche_name": record.get('creche_name'),
#             "creche_id": record.get('creche_id'),
#             "state_name": record.get('state_name'),
#             "district_name": record.get('district_name'),
#             "block_name": record.get('block_name'),
#             "gp_name": record.get('gp_name'),
#             "distance": distance,
#             "category_0_20": cat_0_20,
#             "category_20_50": cat_20_50,
#             "category_50_200": cat_50_200,
#             "category_above_200": cat_above_200
#         })
#     # Add TOTAL row at the end if there are records
#     if data:
#         total_row = {
#             "full_name": """<b style="font-size: 14px;">TOTAL</b>""",
#             "designation": "",
#             "state_name": "",
#             "district_name": "",
#             "block_name": "",
#             "gp_name": "",
#             "creche_name": "",
#             "creche_id": "",
#             "date_of_checkin": "",
#             "check_in_time": "",
#             "category_0_20": f"""<b style="font-size: 14px;">{total_0_20}</b>""",
#             "category_20_50": f"""<b style="font-size: 14px;">{total_20_50}</b>""",
#             "category_50_200": f"""<b style="font-size: 14px;">{total_50_200}</b>""",
#             "category_above_200": f"""<b style="font-size: 14px;">{total_above_200}</b>""",
#             "is_total_row": True  # This can be used for additional styling if needed
#         }
#         data.append(total_row)
#     return data













# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("User"), "fieldname": "full_name", "fieldtype": "Data", "width": 150},
#         {"label": _("Designation"), "fieldname": "designation", "fieldtype": "Data", "width": 150},
#         {"label": _("State"), "fieldname": "state_name", "fieldtype": "Data", "width": 120},
#         {"label": _("District"), "fieldname": "district_name", "fieldtype": "Data", "width": 120},
#         {"label": _("Block"), "fieldname": "block_name", "fieldtype": "Data", "width": 120},
#         {"label": _("GP"), "fieldname": "gp_name", "fieldtype": "Data", "width": 120},
#         {"label": _("Creche"), "fieldname": "creche_name", "fieldtype": "Data", "width": 180},
#         {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": _("Check-in Date"), "fieldname": "date_of_checkin", "fieldtype": "Date", "width": 120},
#         {"label": _("Check-in Time"), "fieldname": "check_in_time", "fieldtype": "Data", "width": 130},
#         {"label": _("Distance (m)"), "fieldname": "distance", "fieldtype": "Int", "width": 120},
#         {
#             "label": _("0-20 m"), 
#             "fieldname": "category_0_20", 
#             "fieldtype": "HTML", 
#             "width": 80,
#             "align": "center"
#         },
#         {
#             "label": _("21-50 m"), 
#             "fieldname": "category_20_50", 
#             "fieldtype": "HTML", 
#             "width": 80,
#             "align": "center"
#         },
#         {
#             "label": _("51-200 m"), 
#             "fieldname": "category_50_200", 
#             "fieldtype": "HTML", 
#             "width": 80,
#             "align": "center"
#         },
#         {
#             "label": _(">200 m"), 
#             "fieldname": "category_above_200", 
#             "fieldtype": "HTML", 
#             "width": 80,
#             "align": "center"
#         },
#     ]

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  # Earth radius in meters
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     # Process filters
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
#     # Create date range for the selected month and year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     # Initialize filters
#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }

#     conditions.append("chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s")

#     if filters.get("state"):
#         conditions.append("chi.state_id = %(state)s")
#         params["state"] = filters.get("state")
        
#     if filters.get("district"):
#         conditions.append("chi.district_id = %(district)s")
#         params["district"] = filters.get("district")
        
#     if filters.get("block"):
#         conditions.append("chi.block_id = %(block)s")
#         params["block"] = filters.get("block")
        
#     if filters.get("gp"):
#         conditions.append("chi.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
        
#     if filters.get("creche"):
#         conditions.append("chi.creche_id = %(creche)s")
#         params["creche"] = filters.get("creche")
        
#     if filters.get("user"):
#         conditions.append("chi.appcreated_by = %(user)s")
#         params["user"] = filters.get("user")

#     if filters.get("designation"):
#         conditions.append("u.type = %(designation)s")
#         params["designation"] = filters.get("designation")

#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     # Query to get all individual check-ins with user details
#     query = f"""
#     SELECT 
#         chi.name as checkin_id,
#         chi.date_of_checkin,
#         DATE_FORMAT(chi.creation, '%%h:%%i %%p') AS check_in_time,
#         chi.appcreated_by,
#         u.full_name,
#         u.type as designation,
#         cr.creche_name,
#         cr.creche_id,
#         b.block_name,
#         gp.gp_name,
#         s.state_name,
#         d.district_name,
#         chi.latitude as check_in_lat,
#         chi.longitude as check_in_lon,
#         cr.latitude as creche_lat,
#         cr.longitude as creche_lon
#     FROM `tabCreche Check In` AS chi
#     INNER JOIN `tabUser` u ON chi.appcreated_by = u.name
#     INNER JOIN `tabCreche` cr ON cr.name = chi.creche_id
#     INNER JOIN `tabState` s ON s.name = chi.state_id
#     INNER JOIN `tabDistrict` d ON d.name = chi.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = chi.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = chi.gp_id
#     {where_clause}
#     ORDER BY chi.date_of_checkin, chi.creation
#     """

#     checkin_records = frappe.db.sql(query, params, as_dict=True)
#     data = []

#     for record in checkin_records:
#         # Calculate distance
#         distance = None
#         try:
#             lat1 = float(record['check_in_lat']) if record.get('check_in_lat') else None
#             lon1 = float(record['check_in_lon']) if record.get('check_in_lon') else None
#             lat2 = float(record['creche_lat']) if record.get('creche_lat') else None
#             lon2 = float(record['creche_lon']) if record.get('creche_lon') else None
            
#             if all(v is not None for v in [lat1, lon1, lat2, lon2]):
#                 distance = round(haversine(lat1, lon1, lat2, lon2))
#         except:
#             distance = None

#         # Create HTML for distance indicators
#         if distance is not None:
#             if distance <= 20:
#                 cat_0_20 = """<span style="color: #4CAF50; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#             elif 20 < distance <= 50:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #FFEB3B; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#             elif 50 < distance <= 200:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #FF9800; font-weight: bold; font-size: 16px;">✓</span>"""
#                 cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""
#             else:
#                 cat_0_20 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_20_50 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_50_200 = """<span style="color: #9E9E9E;">-</span>"""
#                 cat_above_200 = """<span style="color: #F44336; font-weight: bold; font-size: 16px;">✓</span>"""
#         else:
#             cat_0_20 = cat_20_50 = cat_50_200 = cat_above_200 = """<span style="color: #9E9E9E;">-</span>"""

#         data.append({
#             "date_of_checkin": record.get('date_of_checkin'),
#             "check_in_time": record.get('check_in_time'),
#             "full_name": record.get('full_name'),
#             "designation": record.get('designation'),
#             "creche_name": record.get('creche_name'),
#             "creche_id": record.get('creche_id'),
#             "state_name": record.get('state_name'),
#             "district_name": record.get('district_name'),
#             "block_name": record.get('block_name'),
#             "gp_name": record.get('gp_name'),
#             "distance": distance,
#             "category_0_20": cat_0_20,
#             "category_20_50": cat_20_50,
#             "category_50_200": cat_50_200,
#             "category_above_200": cat_above_200
#         })

#     return data


