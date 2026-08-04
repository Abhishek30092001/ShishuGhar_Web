import frappe
from frappe import _
import math
from datetime import date, datetime, timedelta
import calendar
from frappe.utils import nowdate

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters=None):
    selected_level = filters.get("level", "8") if filters else "8"
    variable_columns = []
    
    if selected_level == "1":
        variable_columns.extend([
            {"label": _("Partner"), "fieldname": "partner_name", "width": 180},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}
        ])
    if selected_level == "2":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 150},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}    
        ])
    if selected_level == "3":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 150},
            {"label": _("District"), "fieldname": "district_name", "width": 150},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
        ])
    if selected_level == "4":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 150},
            {"label": _("District"), "fieldname": "district_name", "width": 150},
            {"label": _("Block"), "fieldname": "block_name", "width": 150},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
        ])
    if selected_level == "5":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 120},
            {"label": _("District"), "fieldname": "district_name", "width": 120},
            {"label": _("Block"), "fieldname": "block_name", "width": 120},
            {"label": "Supervisor", "fieldname": "supervisor_id", "width": 180},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
        ])
    if selected_level == "6":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 120},
            {"label": _("District"), "fieldname": "district_name", "width": 120},
            {"label": _("Block"), "fieldname": "block_name", "width": 120},
            {"label": "User", "fieldname": "appcreated_by", "width": 195},
            {"label": "Designation", "fieldname": "designation", "width": 245},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
        ])
    if selected_level == "7":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 120},
            {"label": _("District"), "fieldname": "district_name", "width": 120},
            {"label": _("Block"), "fieldname": "block_name", "width": 120},
            {"label": _("GP"), "fieldname": "gp_name", "width": 150},
            {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
        ])
    if selected_level == "8":
        variable_columns.extend([
            {"label": _("State"), "fieldname": "state_name", "width": 120},
            {"label": _("District"), "fieldname": "district_name", "width": 120},
            {"label": _("Block"), "fieldname": "block_name", "width": 120},
            {"label": _("GP"), "fieldname": "gp_name", "width": 120},
            {"label": _("Creche"), "fieldname": "creche_name", "width": 180},
            {"label": "Creche ID", "fieldname": "creche_id", "width": 150},
        ])

    # Define fixed columns differently for level 8 vs other levels
    if selected_level == "8":
        # For level 8, include creche_opening_date at the beginning
        fixed_columns = [
            {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "width": 150},
            {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
            {
                "label": _("> 50 m (%)"), 
                "fieldname": "above_50m_percentage", 
                "fieldtype": "Percent", 
                "width": 100,
                "align": "center"
            },
            {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
            {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
            {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
            {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
        ]
    else:
        # For other levels, do NOT include creche_opening_date in fixed columns
        fixed_columns = [
            {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
            {
                "label": _("> 50 m (%)"), 
                "fieldname": "above_50m_percentage", 
                "fieldtype": "Percent", 
                "width": 100,
                "align": "center"
            },
            {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
            {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
            {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
            {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
        ]

    return variable_columns + fixed_columns

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_data(filters=None):
    selected_level = filters.get("level", "8") if filters else "8"
    month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
    year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") if filters else current_user_partner
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",")) if filters and filters.get("phases") else None
    designation = filters.get("designation") if filters else None
    user = filters.get("user") if filters else None
    creche_name = filters.get("creche_name") if filters else None
    creche_age = filters.get("creche_age", "") if filters else ""
    
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

    conditions = []
    params = {
        "start_date": start_date,
        "end_date": end_date
    }

    # Partner filter
    if partner_id:
        conditions.append("cr.partner_id = %(partner)s")
        params["partner"] = partner_id

    # State filter with multiple geography handling
    if filters and filters.get("state"):
        conditions.append("cr.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
            params["state_ids"] = state_ids
            params["state"] = None

    # District filter with multiple geography handling
    if filters and filters.get("district"):
        conditions.append("cr.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
            params["district_ids"] = district_ids
            params["district"] = None

    # Block filter with multiple geography handling
    if filters and filters.get("block"):
        conditions.append("cr.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
            params["block_ids"] = block_ids
            params["block"] = None

    # GP filter with multiple geography handling
    if filters and filters.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
        params["gp_ids"] = None
    else:
        if gp_ids:
            conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
            params["gp_ids"] = gp_ids
            params["gp"] = None

    # Creche filter - FIXED
    if creche_name:
        conditions.append("cr.name = %(creche_name)s")
        params["creche_name"] = creche_name
        
    if creche_status_id:
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = creche_status_id
        
    if filters and filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
            params["phases"] = phases_cleaned
            
    if user:
        conditions.append("chi.appcreated_by = %(user)s")
        params["user"] = user

    if filters.get("designation"):
        conditions.append("tu_checkin.type = %(designation)s")
        params["designation"] = filters.get("designation")
    
    # Creche age filter
    params["creche_age"] = creche_age
    if creche_age:
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

    # Add condition for disabled users
    conditions.append("""
        (
            -- User is still enabled (enabled = 1)
            (tu_checkin.enabled = 1 OR tu_checkin.enabled IS NULL)
            OR
            -- User is disabled (enabled = 0) but checkin date is before or on the date they were disabled
            (
                tu_checkin.enabled = 0 
                AND chi.date_of_checkin <= DATE(tu_checkin.modified)
            )
        )
    """)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "tu_checkin.full_name", "tu_checkin.type"],
        "7": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name"],
        "8": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name", "cr.creche_name", "cr.creche_id"],
    }

    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_clause = "GROUP BY " + ", ".join(group_by_fields) if group_by_fields else ""

    creche_count_select = ""
    if selected_level != "8":
        creche_count_select = ", COUNT(DISTINCT cr.name) AS creche_count"

    # Check the actual column names in tabCreche table
    creche_columns = frappe.db.sql("DESC `tabCreche`", as_dict=True)
    creche_column_names = [col['Field'] for col in creche_columns]
    
    # Check if supervisor column exists in creche table
    supervisor_join = ""
    if 'supervisor' in creche_column_names:
        supervisor_join = "LEFT JOIN `tabUser` tu ON cr.supervisor = tu.name"
    elif 'app_created_by' in creche_column_names:
        supervisor_join = "LEFT JOIN `tabUser` tu ON cr.app_created_by = tu.name"
    else:
        # If no supervisor column exists, join with check-in table for user info
        supervisor_join = "LEFT JOIN `tabUser` tu ON chi.appcreated_by = tu.name"

    # Determine if we need checkin user join and what type
    checkin_join_type = "INNER JOIN" if selected_level == "6" else "LEFT JOIN"
    
    # Select fields based on level
    user_select_field = ""
    if selected_level == "5":
        user_select_field = "tu.full_name AS supervisor_id,"
    elif selected_level == "6":
        user_select_field = "tu_checkin.full_name AS appcreated_by, tu_checkin.type AS designation,"

    # Modified query with proper column references and user enabled check
    query = f"""
    SELECT 
        p.partner_name,
        s.state_name,
        d.district_name,
        b.block_name,
        gp.gp_name,
        cr.creche_name,
        cr.creche_id,
        {user_select_field}
        DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date,
        COUNT(chi.name) AS total_checkins,
        COALESCE(SUM(CASE WHEN 
            ROUND(6371000 * 2 * ASIN(SQRT(
                POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
                COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
                POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
            ))) <= 20 THEN 1 ELSE 0 END), 0) AS checkins_0_20m,
        COALESCE(SUM(CASE WHEN 
            ROUND(6371000 * 2 * ASIN(SQRT(
                POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
                COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
                POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
            ))) BETWEEN 21 AND 50 THEN 1 ELSE 0 END), 0) AS checkins_20_50m,
        COALESCE(SUM(CASE WHEN 
            ROUND(6371000 * 2 * ASIN(SQRT(
                POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
                COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
                POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
            ))) BETWEEN 51 AND 200 THEN 1 ELSE 0 END), 0) AS checkins_50_200m,
        COALESCE(SUM(CASE WHEN 
            ROUND(6371000 * 2 * ASIN(SQRT(
                POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
                COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
                POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
            ))) > 200 THEN 1 ELSE 0 END), 0) AS checkins_above_200m
        {creche_count_select}
    FROM `tabCreche` AS cr
    INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
    INNER JOIN `tabState` AS s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
    INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` AS gp ON gp.name = cr.gp_id
    {supervisor_join}
    {checkin_join_type} `tabCreche Check In` AS chi ON chi.creche_id = cr.name 
        AND chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s
    LEFT JOIN `tabUser` tu_checkin ON chi.appcreated_by = tu_checkin.email
    {where_clause}
    {group_by_clause}
    ORDER BY {", ".join(group_by_fields)}
    """

    results = frappe.db.sql(query, params, as_dict=True)

    data = []
    for row in results:
        total_checkins = (row.get('checkins_0_20m', 0) + row.get('checkins_20_50m', 0) + 
                        row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
        above_50m = (row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
        # Calculate percentage - show blank at creche level if no checkins
        # FIXED: Divide by 100 to convert from percentage to decimal for proper Percent fieldtype display
        if total_checkins > 0:
            above_50m_percentage = round((above_50m / total_checkins), 4)
        else:
            above_50m_percentage = (None if selected_level == "8" else 0)

        data_row = {
            "partner_name": row.get('partner_name', ''),
            "state_name": row.get('state_name', ''),
            "district_name": row.get('district_name', ''),
            "block_name": row.get('block_name', ''),
            "gp_name": row.get('gp_name', ''),
            "creche_name": row.get('creche_name', ''),
            "creche_id": row.get('creche_id', ''),
            "supervisor_id": row.get('supervisor_id', ''),
            "appcreated_by": row.get('appcreated_by', ''),
            "designation": row.get('designation', ''),
            "creche_opening_date": row.get('creche_opening_date', '') if selected_level == "8" else "",
            "total_checkins": total_checkins,
            "checkins_0_20m": row.get('checkins_0_20m', 0),
            "checkins_20_50m": row.get('checkins_20_50m', 0),
            "checkins_50_200m": row.get('checkins_50_200m', 0),
            "checkins_above_200m": row.get('checkins_above_200m', 0)
        }

        # Always add percentage for non-creche levels, only add for creche level if there are checkins
        if selected_level != "8" or (selected_level == "8" and total_checkins > 0):
            data_row["above_50m_percentage"] = above_50m_percentage

        # Add creche count for non-creche levels
        if selected_level != "8":
            data_row["creche_count"] = row.get('creche_count', 0)

        data.append(data_row)

    # Calculate totals with updated field names and make them bold
    if data:
        total_row = {
            "partner_name": "TOTAL",
            "state_name": "TOTAL",
            "district_name": "",
            "block_name": "",
            "gp_name": "",
            "creche_name": "",
            "creche_id": "",
            "supervisor_id": "",
            "appcreated_by": "",
            "designation": "",
            "creche_opening_date": "",
            "total_checkins": sum(row['total_checkins'] for row in data),
            "checkins_0_20m": sum(row['checkins_0_20m'] for row in data),
            "checkins_20_50m": sum(row['checkins_20_50m'] for row in data),
            "checkins_50_200m": sum(row['checkins_50_200m'] for row in data),
            "checkins_above_200m": sum(row['checkins_above_200m'] for row in data),
            "is_total_row": True
        }

        # Calculate total creche count and percentage for non-creche levels
        if selected_level != "8":
            total_creche_count = sum(row['creche_count'] for row in data if 'creche_count' in row)
            total_row["creche_count"] = total_creche_count
            
            # Calculate overall percentage for total row - FIXED: Divide by 100
            total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
            total_checkins = total_row['total_checkins']
            total_row["above_50m_percentage"] = round((total_above_50m / total_checkins), 4) if total_checkins > 0 else 0
        else:
            # For creche level, don't show percentage in total row if no checkins
            total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
            total_checkins = total_row['total_checkins']
            if total_checkins > 0:
                total_row["above_50m_percentage"] = round((total_above_50m / total_checkins), 4)
            
        data.append(total_row)

    return data

















#Backup Before age of Creche Filter
# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data

# def get_columns(filters=None):
#     selected_level = filters.get("level", "8") if filters else "8"
#     variable_columns = []
    
#     if selected_level == "1":
#         variable_columns.extend([
#             {"label": _("Partner"), "fieldname": "partner_name", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}
#         ])
#     if selected_level == "2":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}    
#         ])
#     if selected_level == "3":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "4":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("Block"), "fieldname": "block_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "5":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "Supervisor", "fieldname": "supervisor_id", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "6":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "User", "fieldname": "appcreated_by", "width": 195},
#             {"label": "Designation", "fieldname": "designation", "width": 245},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "7":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "8":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 120},
#             {"label": _("Creche"), "fieldname": "creche_name", "width": 180},
#             {"label": "Creche ID", "fieldname": "creche_id", "width": 150},
#         ])

#     # Define fixed columns differently for level 8 vs other levels
#     if selected_level == "8":
#         # For level 8, include creche_opening_date at the beginning
#         fixed_columns = [
#             {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "width": 150},
#             {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#             {
#                 "label": _("> 50 m (%)"), 
#                 "fieldname": "above_50m_percentage", 
#                 "fieldtype": "Percent", 
#                 "width": 100,
#                 "align": "center"
#             },
#             {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#             {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#         ]
#     else:
#         # For other levels, do NOT include creche_opening_date in fixed columns
#         fixed_columns = [
#             {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#             {
#                 "label": _("> 50 m (%)"), 
#                 "fieldname": "above_50m_percentage", 
#                 "fieldtype": "Percent", 
#                 "width": 100,
#                 "align": "center"
#             },
#             {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#             {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#         ]

#     return variable_columns + fixed_columns

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     selected_level = filters.get("level", "8") if filters else "8"
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") if filters else current_user_partner
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",")) if filters and filters.get("phases") else None
#     designation = filters.get("designation") if filters else None
#     user = filters.get("user") if filters else None
#     creche_name = filters.get("creche_name") if filters else None
    
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

#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }

#     # Partner filter
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     # State filter with multiple geography handling
#     if filters and filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     # District filter with multiple geography handling
#     if filters and filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     # Block filter with multiple geography handling
#     if filters and filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     # GP filter with multiple geography handling
#     if filters and filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None

#     # Creche filter - FIXED
#     if creche_name:
#         conditions.append("cr.name = %(creche_name)s")
#         params["creche_name"] = creche_name
        
#     if creche_status_id:
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = creche_status_id
        
#     if filters and filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#             params["phases"] = phases_cleaned
            
#     if user:
#         conditions.append("chi.appcreated_by = %(user)s")
#         params["user"] = user

#     if filters.get("designation"):
#         conditions.append("tu_checkin.type = %(designation)s")
#         params["designation"] = filters.get("designation")

#     # Add condition for disabled users
#     conditions.append("""
#         (
#             -- User is still enabled (enabled = 1)
#             (tu_checkin.enabled = 1 OR tu_checkin.enabled IS NULL)
#             OR
#             -- User is disabled (enabled = 0) but checkin date is before or on the date they were disabled
#             (
#                 tu_checkin.enabled = 0 
#                 AND chi.date_of_checkin <= DATE(tu_checkin.modified)
#             )
#         )
#     """)

#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "tu_checkin.full_name", "tu_checkin.type"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name"],
#         "8": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name", "cr.creche_name", "cr.creche_id"],
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_clause = "GROUP BY " + ", ".join(group_by_fields) if group_by_fields else ""

#     creche_count_select = ""
#     if selected_level != "8":
#         creche_count_select = ", COUNT(DISTINCT cr.name) AS creche_count"

#     # Check the actual column names in tabCreche table
#     creche_columns = frappe.db.sql("DESC `tabCreche`", as_dict=True)
#     creche_column_names = [col['Field'] for col in creche_columns]
    
#     # Check if supervisor column exists in creche table
#     supervisor_join = ""
#     if 'supervisor' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.supervisor = tu.name"
#     elif 'app_created_by' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.app_created_by = tu.name"
#     else:
#         # If no supervisor column exists, join with check-in table for user info
#         supervisor_join = "LEFT JOIN `tabUser` tu ON chi.appcreated_by = tu.name"

#     # Determine if we need checkin user join and what type
#     checkin_join_type = "INNER JOIN" if selected_level == "6" else "LEFT JOIN"
    
#     # Select fields based on level
#     user_select_field = ""
#     if selected_level == "5":
#         user_select_field = "tu.full_name AS supervisor_id,"
#     elif selected_level == "6":
#         user_select_field = "tu_checkin.full_name AS appcreated_by, tu_checkin.type AS designation,"

#     # Modified query with proper column references and user enabled check
#     query = f"""
#     SELECT 
#         p.partner_name,
#         s.state_name,
#         d.district_name,
#         b.block_name,
#         gp.gp_name,
#         cr.creche_name,
#         cr.creche_id,
#         {user_select_field}
#         DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date,
#         COUNT(chi.name) AS total_checkins,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) <= 20 THEN 1 ELSE 0 END), 0) AS checkins_0_20m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 21 AND 50 THEN 1 ELSE 0 END), 0) AS checkins_20_50m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 51 AND 200 THEN 1 ELSE 0 END), 0) AS checkins_50_200m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) > 200 THEN 1 ELSE 0 END), 0) AS checkins_above_200m
#         {creche_count_select}
#     FROM `tabCreche` AS cr
#     INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
#     INNER JOIN `tabState` AS s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = cr.gp_id
#     {supervisor_join}
#     {checkin_join_type} `tabCreche Check In` AS chi ON chi.creche_id = cr.name 
#         AND chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s
#     LEFT JOIN `tabUser` tu_checkin ON chi.appcreated_by = tu_checkin.email
#     {where_clause}
#     {group_by_clause}
#     ORDER BY {", ".join(group_by_fields)}
#     """

#     results = frappe.db.sql(query, params, as_dict=True)

#     data = []
#     for row in results:
#         total_checkins = (row.get('checkins_0_20m', 0) + row.get('checkins_20_50m', 0) + 
#                         row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         above_50m = (row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         # Calculate percentage - show blank at creche level if no checkins
#         # FIXED: Divide by 100 to convert from percentage to decimal for proper Percent fieldtype display
#         if total_checkins > 0:
#             above_50m_percentage = round((above_50m / total_checkins), 4)
#         else:
#             above_50m_percentage = (None if selected_level == "8" else 0)

#         data_row = {
#             "partner_name": row.get('partner_name', ''),
#             "state_name": row.get('state_name', ''),
#             "district_name": row.get('district_name', ''),
#             "block_name": row.get('block_name', ''),
#             "gp_name": row.get('gp_name', ''),
#             "creche_name": row.get('creche_name', ''),
#             "creche_id": row.get('creche_id', ''),
#             "supervisor_id": row.get('supervisor_id', ''),
#             "appcreated_by": row.get('appcreated_by', ''),
#             "designation": row.get('designation', ''),
#             "creche_opening_date": row.get('creche_opening_date', '') if selected_level == "8" else "",
#             "total_checkins": total_checkins,
#             "checkins_0_20m": row.get('checkins_0_20m', 0),
#             "checkins_20_50m": row.get('checkins_20_50m', 0),
#             "checkins_50_200m": row.get('checkins_50_200m', 0),
#             "checkins_above_200m": row.get('checkins_above_200m', 0)
#         }

#         # Always add percentage for non-creche levels, only add for creche level if there are checkins
#         if selected_level != "8" or (selected_level == "8" and total_checkins > 0):
#             data_row["above_50m_percentage"] = above_50m_percentage

#         # Add creche count for non-creche levels
#         if selected_level != "8":
#             data_row["creche_count"] = row.get('creche_count', 0)

#         data.append(data_row)

#     # Calculate totals with updated field names and make them bold
#     if data:
#         total_row = {
#             "partner_name": "TOTAL",
#             "state_name": "TOTAL",
#             "district_name": "",
#             "block_name": "",
#             "gp_name": "",
#             "creche_name": "",
#             "creche_id": "",
#             "supervisor_id": "",
#             "appcreated_by": "",
#             "designation": "",
#             "creche_opening_date": "",
#             "total_checkins": sum(row['total_checkins'] for row in data),
#             "checkins_0_20m": sum(row['checkins_0_20m'] for row in data),
#             "checkins_20_50m": sum(row['checkins_20_50m'] for row in data),
#             "checkins_50_200m": sum(row['checkins_50_200m'] for row in data),
#             "checkins_above_200m": sum(row['checkins_above_200m'] for row in data),
#             "is_total_row": True
#         }

#         # Calculate total creche count and percentage for non-creche levels
#         if selected_level != "8":
#             total_creche_count = sum(row['creche_count'] for row in data if 'creche_count' in row)
#             total_row["creche_count"] = total_creche_count
            
#             # Calculate overall percentage for total row - FIXED: Divide by 100
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             total_row["above_50m_percentage"] = round((total_above_50m / total_checkins), 4) if total_checkins > 0 else 0
#         else:
#             # For creche level, don't show percentage in total row if no checkins
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             if total_checkins > 0:
#                 total_row["above_50m_percentage"] = round((total_above_50m / total_checkins), 4)
            
#         data.append(total_row)

#     return data




















# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data

# def get_columns(filters=None):
#     selected_level = filters.get("level", "8") if filters else "8"
#     variable_columns = []
    
#     if selected_level == "1":
#         variable_columns.extend([
#             {"label": _("Partner"), "fieldname": "partner_name", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}
#         ])
#     if selected_level == "2":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}    
#         ])
#     if selected_level == "3":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "4":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("Block"), "fieldname": "block_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "5":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "Supervisor", "fieldname": "supervisor_id", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "6":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "User", "fieldname": "appcreated_by", "width": 195},
#             {"label": "Designation", "fieldname": "designation", "width": 245},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "7":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "8":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 120},
#             {"label": _("Creche"), "fieldname": "creche_name", "width": 180},
#             {"label": "Creche ID", "fieldname": "creche_id", "width": 150},
#         ])

#     # Define fixed columns differently for level 8 vs other levels
#     if selected_level == "8":
#         # For level 8, include creche_opening_date at the beginning
#         fixed_columns = [
#             {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "width": 150},
#             {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#             {
#                 "label": _("> 50 m (%)"), 
#                 "fieldname": "above_50m_percentage", 
#                 "fieldtype": "Percent", 
#                 "width": 100,
#                 "align": "center"
#             },
#             {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#             {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#         ]
#     else:
#         # For other levels, do NOT include creche_opening_date in fixed columns
#         fixed_columns = [
#             {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#             {
#                 "label": _("> 50 m (%)"), 
#                 "fieldname": "above_50m_percentage", 
#                 "fieldtype": "Percent", 
#                 "width": 100,
#                 "align": "center"
#             },
#             {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#             {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#         ]

#     return variable_columns + fixed_columns

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     selected_level = filters.get("level", "8") if filters else "8"
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") if filters else current_user_partner
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",")) if filters and filters.get("phases") else None
#     designation = filters.get("designation") if filters else None
#     user = filters.get("user") if filters else None
    
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

#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }

#     # Partner filter
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     # State filter with multiple geography handling
#     if filters and filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     # District filter with multiple geography handling
#     if filters and filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     # Block filter with multiple geography handling
#     if filters and filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     # GP filter with multiple geography handling
#     if filters and filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None
        
#     if creche_status_id:
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = creche_status_id
        
#     if filters and filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#             params["phases"] = phases_cleaned
            
#     if user:
#         conditions.append("chi.appcreated_by = %(user)s")
#         params["user"] = user

#     if filters.get("designation"):
#         conditions.append("tu_checkin.type = %(designation)s")
#         params["designation"] = filters.get("designation")

#     # Add condition for disabled users
#     conditions.append("""
#         (
#             -- User is still enabled (enabled = 1)
#             (tu_checkin.enabled = 1 OR tu_checkin.enabled IS NULL)
#             OR
#             -- User is disabled (enabled = 0) but checkin date is before or on the date they were disabled
#             (
#                 tu_checkin.enabled = 0 
#                 AND chi.date_of_checkin <= DATE(tu_checkin.modified)
#             )
#         )
#     """)

#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "tu_checkin.full_name", "tu_checkin.type"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name"],
#         "8": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name", "cr.creche_name", "cr.creche_id"],
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_clause = "GROUP BY " + ", ".join(group_by_fields) if group_by_fields else ""

#     creche_count_select = ""
#     if selected_level != "8":
#         creche_count_select = ", COUNT(DISTINCT cr.name) AS creche_count"

#     # Check the actual column names in tabCreche table
#     creche_columns = frappe.db.sql("DESC `tabCreche`", as_dict=True)
#     creche_column_names = [col['Field'] for col in creche_columns]
    
#     # Check if supervisor column exists in creche table
#     supervisor_join = ""
#     if 'supervisor' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.supervisor = tu.name"
#     elif 'app_created_by' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.app_created_by = tu.name"
#     else:
#         # If no supervisor column exists, join with check-in table for user info
#         supervisor_join = "LEFT JOIN `tabUser` tu ON chi.appcreated_by = tu.name"

#     # Determine if we need checkin user join and what type
#     checkin_join_type = "INNER JOIN" if selected_level == "6" else "LEFT JOIN"
    
#     # Select fields based on level
#     user_select_field = ""
#     if selected_level == "5":
#         user_select_field = "tu.full_name AS supervisor_id,"
#     elif selected_level == "6":
#         user_select_field = "tu_checkin.full_name AS appcreated_by, tu_checkin.type AS designation,"

#     # Modified query with proper column references and user enabled check
#     query = f"""
#     SELECT 
#         p.partner_name,
#         s.state_name,
#         d.district_name,
#         b.block_name,
#         gp.gp_name,
#         cr.creche_name,
#         cr.creche_id,
#         {user_select_field}
#         DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date,
#         COUNT(chi.name) AS total_checkins,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) <= 20 THEN 1 ELSE 0 END), 0) AS checkins_0_20m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 21 AND 50 THEN 1 ELSE 0 END), 0) AS checkins_20_50m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 51 AND 200 THEN 1 ELSE 0 END), 0) AS checkins_50_200m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) > 200 THEN 1 ELSE 0 END), 0) AS checkins_above_200m
#         {creche_count_select}
#     FROM `tabCreche` AS cr
#     INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
#     INNER JOIN `tabState` AS s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = cr.gp_id
#     {supervisor_join}
#     {checkin_join_type} `tabCreche Check In` AS chi ON chi.creche_id = cr.name 
#         AND chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s
#     LEFT JOIN `tabUser` tu_checkin ON chi.appcreated_by = tu_checkin.email
#     {where_clause}
#     {group_by_clause}
#     ORDER BY {", ".join(group_by_fields)}
#     """

#     results = frappe.db.sql(query, params, as_dict=True)

#     data = []
#     for row in results:
#         total_checkins = (row.get('checkins_0_20m', 0) + row.get('checkins_20_50m', 0) + 
#                         row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         above_50m = (row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         # Calculate percentage - show blank at creche level if no checkins
#         above_50m_percentage = round((above_50m / total_checkins * 100), 2) if total_checkins > 0 else (None if selected_level == "8" else 0)

#         data_row = {
#             "partner_name": row.get('partner_name', ''),
#             "state_name": row.get('state_name', ''),
#             "district_name": row.get('district_name', ''),
#             "block_name": row.get('block_name', ''),
#             "gp_name": row.get('gp_name', ''),
#             "creche_name": row.get('creche_name', ''),
#             "creche_id": row.get('creche_id', ''),
#             "supervisor_id": row.get('supervisor_id', ''),
#             "appcreated_by": row.get('appcreated_by', ''),
#             "designation": row.get('designation', ''),
#             "creche_opening_date": row.get('creche_opening_date', '') if selected_level == "8" else "",
#             "total_checkins": total_checkins,
#             "checkins_0_20m": row.get('checkins_0_20m', 0),
#             "checkins_20_50m": row.get('checkins_20_50m', 0),
#             "checkins_50_200m": row.get('checkins_50_200m', 0),
#             "checkins_above_200m": row.get('checkins_above_200m', 0)
#         }

#         # Always add percentage for non-creche levels, only add for creche level if there are checkins
#         if selected_level != "8" or (selected_level == "8" and total_checkins > 0):
#             data_row["above_50m_percentage"] = above_50m_percentage

#         # Add creche count for non-creche levels
#         if selected_level != "8":
#             data_row["creche_count"] = row.get('creche_count', 0)

#         data.append(data_row)

#     # Calculate totals with updated field names and make them bold
#     if data:
#         total_row = {
#             "partner_name": "TOTAL",
#             "state_name": "TOTAL",
#             "district_name": "",
#             "block_name": "",
#             "gp_name": "",
#             "creche_name": "",
#             "creche_id": "",
#             "supervisor_id": "",
#             "appcreated_by": "",
#             "designation": "",
#             "creche_opening_date": "",
#             "total_checkins": sum(row['total_checkins'] for row in data),
#             "checkins_0_20m": sum(row['checkins_0_20m'] for row in data),
#             "checkins_20_50m": sum(row['checkins_20_50m'] for row in data),
#             "checkins_50_200m": sum(row['checkins_50_200m'] for row in data),
#             "checkins_above_200m": sum(row['checkins_above_200m'] for row in data),
#             "is_total_row": True
#         }

#         # Calculate total creche count and percentage for non-creche levels
#         if selected_level != "8":
#             total_creche_count = sum(row['creche_count'] for row in data if 'creche_count' in row)
#             total_row["creche_count"] = total_creche_count
            
#             # Calculate overall percentage for total row
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             total_row["above_50m_percentage"] = round((total_above_50m / total_checkins * 100), 2) if total_checkins > 0 else 0
#         else:
#             # For creche level, don't show percentage in total row if no checkins
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             if total_checkins > 0:
#                 total_row["above_50m_percentage"] = round((total_above_50m / total_checkins * 100), 2)
            
#         data.append(total_row)

#     return data









# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data

# def get_columns(filters=None):
#     selected_level = filters.get("level", "8") if filters else "8"
#     variable_columns = []
    
#     if selected_level == "1":
#         variable_columns.extend([
#             {"label": _("Partner"), "fieldname": "partner_name", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}
#         ])
#     if selected_level == "2":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}    
#         ])
#     if selected_level == "3":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "4":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("Block"), "fieldname": "block_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "5":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "Supervisor", "fieldname": "supervisor_id", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "6":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "User", "fieldname": "appcreated_by", "width": 195},
#             {"label": "Designation", "fieldname": "designation", "width": 245},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "7":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "8":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 120},
#             {"label": _("Creche"), "fieldname": "creche_name", "width": 180},
#             {"label": "Creche ID", "fieldname": "creche_id", "width": 150},
#         ])

#     # Define fixed columns differently for level 8 vs other levels
#     if selected_level == "8":
#         # For level 8, include creche_opening_date at the beginning
#         fixed_columns = [
#             {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "width": 150},
#             {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#             {
#                 "label": _("> 50 m (%)"), 
#                 "fieldname": "above_50m_percentage", 
#                 "fieldtype": "Percent", 
#                 "width": 100,
#                 "align": "center"
#             },
#             {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#             {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#         ]
#     else:
#         # For other levels, do NOT include creche_opening_date in fixed columns
#         fixed_columns = [
#             {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#             {
#                 "label": _("> 50 m (%)"), 
#                 "fieldname": "above_50m_percentage", 
#                 "fieldtype": "Percent", 
#                 "width": 100,
#                 "align": "center"
#             },
#             {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#             {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#             {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#         ]

#     return variable_columns + fixed_columns

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     selected_level = filters.get("level", "8") if filters else "8"
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") if filters else current_user_partner
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",")) if filters and filters.get("phases") else None
#     designation = filters.get("designation") if filters else None
#     user = filters.get("user") if filters else None
    
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

#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }

#     # Partner filter
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     # State filter with multiple geography handling
#     if filters and filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     # District filter with multiple geography handling
#     if filters and filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     # Block filter with multiple geography handling
#     if filters and filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     # GP filter with multiple geography handling
#     if filters and filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None
        
#     if creche_status_id:
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = creche_status_id
        
#     if filters and filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#             params["phases"] = phases_cleaned
            
#     if user:
#         conditions.append("chi.appcreated_by = %(user)s")
#         params["user"] = user


#     if filters.get("designation"):
#         conditions.append("tu_checkin.type = %(designation)s")
#         params["designation"] = filters.get("designation")


#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "tu_checkin.full_name", "tu_checkin.type"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name"],
#         "8": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name", "cr.creche_name", "cr.creche_id"],
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_clause = "GROUP BY " + ", ".join(group_by_fields) if group_by_fields else ""

#     creche_count_select = ""
#     if selected_level != "8":
#         creche_count_select = ", COUNT(DISTINCT cr.name) AS creche_count"

#     # Check the actual column names in tabCreche table
#     creche_columns = frappe.db.sql("DESC `tabCreche`", as_dict=True)
#     creche_column_names = [col['Field'] for col in creche_columns]
    
#     # Check if supervisor column exists in creche table
#     supervisor_join = ""
#     if 'supervisor' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.supervisor = tu.name"
#     elif 'app_created_by' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.app_created_by = tu.name"
#     else:
#         # If no supervisor column exists, join with check-in table for user info
#         supervisor_join = "LEFT JOIN `tabUser` tu ON chi.appcreated_by = tu.name"

#     # Determine if we need checkin user join and what type
#     checkin_join_type = "INNER JOIN" if selected_level == "6" else "LEFT JOIN"
    
#     # Select fields based on level
#     user_select_field = ""
#     if selected_level == "5":
#         user_select_field = "tu.full_name AS supervisor_id,"
#     elif selected_level == "6":
#         user_select_field = "tu_checkin.full_name AS appcreated_by, tu_checkin.type AS designation,"

#     # Modified query with proper column references
#     query = f"""
#     SELECT 
#         p.partner_name,
#         s.state_name,
#         d.district_name,
#         b.block_name,
#         gp.gp_name,
#         cr.creche_name,
#         cr.creche_id,
#         {user_select_field}
#         DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date,
#         COUNT(chi.name) AS total_checkins,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) <= 20 THEN 1 ELSE 0 END), 0) AS checkins_0_20m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 21 AND 50 THEN 1 ELSE 0 END), 0) AS checkins_20_50m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 51 AND 200 THEN 1 ELSE 0 END), 0) AS checkins_50_200m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) > 200 THEN 1 ELSE 0 END), 0) AS checkins_above_200m
#         {creche_count_select}
#     FROM `tabCreche` AS cr
#     INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
#     INNER JOIN `tabState` AS s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = cr.gp_id
#     {supervisor_join}
#     {checkin_join_type} `tabCreche Check In` AS chi ON chi.creche_id = cr.name 
#         AND chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s
#     LEFT JOIN `tabUser` tu_checkin ON chi.appcreated_by = tu_checkin.email
#     {where_clause}
#     {group_by_clause}
#     ORDER BY {", ".join(group_by_fields)}
#     """

#     results = frappe.db.sql(query, params, as_dict=True)

#     data = []
#     for row in results:
#         total_checkins = (row.get('checkins_0_20m', 0) + row.get('checkins_20_50m', 0) + 
#                         row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         above_50m = (row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         # Calculate percentage - show blank at creche level if no checkins
#         above_50m_percentage = round((above_50m / total_checkins * 100), 2) if total_checkins > 0 else (None if selected_level == "8" else 0)

#         data_row = {
#             "partner_name": row.get('partner_name', ''),
#             "state_name": row.get('state_name', ''),
#             "district_name": row.get('district_name', ''),
#             "block_name": row.get('block_name', ''),
#             "gp_name": row.get('gp_name', ''),
#             "creche_name": row.get('creche_name', ''),
#             "creche_id": row.get('creche_id', ''),
#             "supervisor_id": row.get('supervisor_id', ''),
#             "appcreated_by": row.get('appcreated_by', ''),
#             "designation": row.get('designation', ''),
#             "creche_opening_date": row.get('creche_opening_date', '') if selected_level == "8" else "",
#             "total_checkins": total_checkins,
#             "checkins_0_20m": row.get('checkins_0_20m', 0),
#             "checkins_20_50m": row.get('checkins_20_50m', 0),
#             "checkins_50_200m": row.get('checkins_50_200m', 0),
#             "checkins_above_200m": row.get('checkins_above_200m', 0)
#         }

#         # Always add percentage for non-creche levels, only add for creche level if there are checkins
#         if selected_level != "8" or (selected_level == "8" and total_checkins > 0):
#             data_row["above_50m_percentage"] = above_50m_percentage

#         # Add creche count for non-creche levels
#         if selected_level != "8":
#             data_row["creche_count"] = row.get('creche_count', 0)

#         data.append(data_row)

#     # Calculate totals with updated field names and make them bold
#     if data:
#         total_row = {
#             "partner_name": "TOTAL",
#             "state_name": "TOTAL",
#             "district_name": "",
#             "block_name": "",
#             "gp_name": "",
#             "creche_name": "",
#             "creche_id": "",
#             "supervisor_id": "",
#             "appcreated_by": "",
#             "designation": "",
#             "creche_opening_date": "",
#             "total_checkins": sum(row['total_checkins'] for row in data),
#             "checkins_0_20m": sum(row['checkins_0_20m'] for row in data),
#             "checkins_20_50m": sum(row['checkins_20_50m'] for row in data),
#             "checkins_50_200m": sum(row['checkins_50_200m'] for row in data),
#             "checkins_above_200m": sum(row['checkins_above_200m'] for row in data),
#             "is_total_row": True
#         }

#         # Calculate total creche count and percentage for non-creche levels
#         if selected_level != "8":
#             total_creche_count = sum(row['creche_count'] for row in data if 'creche_count' in row)
#             total_row["creche_count"] = total_creche_count
            
#             # Calculate overall percentage for total row
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             total_row["above_50m_percentage"] = round((total_above_50m / total_checkins * 100), 2) if total_checkins > 0 else 0
#         else:
#             # For creche level, don't show percentage in total row if no checkins
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             if total_checkins > 0:
#                 total_row["above_50m_percentage"] = round((total_above_50m / total_checkins * 100), 2)
            
#         data.append(total_row)

#     return data




















# import frappe
# from frappe import _
# import math
# from datetime import date, datetime, timedelta
# import calendar
# from frappe.utils import nowdate

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data

# def get_columns(filters=None):
#     selected_level = filters.get("level", "7") if filters else "7"
#     variable_columns = []
    
#     if selected_level == "1":
#         variable_columns.extend([
#             {"label": _("Partner"), "fieldname": "partner_name", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}
#         ])
#     if selected_level == "2":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130}    
#         ])
#     if selected_level == "3":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "4":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 150},
#             {"label": _("District"), "fieldname": "district_name", "width": 150},
#             {"label": _("Block"), "fieldname": "block_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "5":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": "Supervisor", "fieldname": "supervisor_id", "width": 180},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "6":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 150},
#             {"label": _("No. of Creches"), "fieldname": "creche_count", "fieldtype": "Int", "width": 130},
#         ])
#     if selected_level == "7":
#         variable_columns.extend([
#             {"label": _("State"), "fieldname": "state_name", "width": 120},
#             {"label": _("District"), "fieldname": "district_name", "width": 120},
#             {"label": _("Block"), "fieldname": "block_name", "width": 120},
#             {"label": _("GP"), "fieldname": "gp_name", "width": 120},
#             {"label": _("Creche"), "fieldname": "creche_name", "width": 180},
#             {"label": "Creche ID", "fieldname": "creche_id", "width": 150}
#         ])

#     fixed_columns = [
#         {"label": _("Total Checkins"), "fieldname": "total_checkins", "fieldtype": "Int", "width": 130},
#         {
#             "label": _("> 50 m (%)"), 
#             "fieldname": "above_50m_percentage", 
#             "fieldtype": "Percent", 
#             "width": 100,
#             "align": "center"
#         },
#         {"label": _(" >200 m"), "fieldname": "checkins_above_200m", "fieldtype": "Int", "width": 100},
#         {"label": _("51-200 m"), "fieldname": "checkins_50_200m", "fieldtype": "Int", "width": 100},
#         {"label": _("21-50 m"), "fieldname": "checkins_20_50m", "fieldtype": "Int", "width": 100},
#         {"label": _("0-20 m"), "fieldname": "checkins_0_20m", "fieldtype": "Int", "width": 100},
#     ]

#     if selected_level == "7":
#         fixed_columns.insert(0, {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "width": 150})

#     return variable_columns + fixed_columns

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371000  
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c

# def get_data(filters=None):
#     selected_level = filters.get("level", "7") if filters else "7"
#     month = int(filters.get("month")) if filters and filters.get("month") else datetime.now().month
#     year = int(filters.get("year")) if filters and filters.get("year") else datetime.now().year
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") if filters else current_user_partner
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",")) if filters and filters.get("phases") else None
#     designation = filters.get("designation") if filters else None
#     user = filters.get("user") if filters else None
    
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

#     conditions = []
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }

#     # Partner filter
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     # State filter with multiple geography handling
#     if filters and filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#         params["state_ids"] = None
#     else:
#         if state_ids:
#             conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#             params["state_ids"] = state_ids
#             params["state"] = None

#     # District filter with multiple geography handling
#     if filters and filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#         params["district_ids"] = None
#     else:
#         if district_ids:
#             conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#             params["district_ids"] = district_ids
#             params["district"] = None

#     # Block filter with multiple geography handling
#     if filters and filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#         params["block_ids"] = None
#     else:
#         if block_ids:
#             conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#             params["block_ids"] = block_ids
#             params["block"] = None

#     # GP filter with multiple geography handling
#     if filters and filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#         params["gp_ids"] = None
#     else:
#         if gp_ids:
#             conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#             params["gp_ids"] = gp_ids
#             params["gp"] = None
        
#     if creche_status_id:
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = creche_status_id
        
#     if filters and filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#             params["phases"] = phases_cleaned
            
#     if user:
#         conditions.append("chi.app_created_by = %(user)s")
#         params["user"] = user

#     if designation:
#         conditions.append("tu.type = %(designation)s")
#         params["designation"] = designation

#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "tu.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "gp.gp_name", "cr.creche_name", "cr.creche_id"],
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_clause = "GROUP BY " + ", ".join(group_by_fields) if group_by_fields else ""

#     creche_count_select = ""
#     if selected_level != "7":
#         creche_count_select = ", COUNT(DISTINCT cr.name) AS creche_count"

#     # First, let's check the actual column names in tabCreche table
#     creche_columns = frappe.db.sql("DESC `tabCreche`", as_dict=True)
#     creche_column_names = [col['Field'] for col in creche_columns]
    
#     # Check if supervisor column exists in creche table
#     supervisor_join = ""
#     if 'supervisor' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.supervisor = tu.name"
#     elif 'app_created_by' in creche_column_names:
#         supervisor_join = "LEFT JOIN `tabUser` tu ON cr.app_created_by = tu.name"
#     else:
#         # If no supervisor column exists, join with check-in table for user info
#         supervisor_join = "LEFT JOIN `tabUser` tu ON chi.app_created_by = tu.name"

#     # Modified query with proper column references
#     query = f"""
#     SELECT 
#         p.partner_name,
#         s.state_name,
#         d.district_name,
#         b.block_name,
#         gp.gp_name,
#         cr.creche_name,
#         cr.creche_id,
#         tu.full_name AS supervisor_id,
#         DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date,
#         COUNT(chi.name) AS total_checkins,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) <= 20 THEN 1 ELSE 0 END), 0) AS checkins_0_20m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 20 AND 50 THEN 1 ELSE 0 END), 0) AS checkins_20_50m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) BETWEEN 50 AND 200 THEN 1 ELSE 0 END), 0) AS checkins_50_200m,
#         COALESCE(SUM(CASE WHEN 
#             ROUND(6371000 * 2 * ASIN(SQRT(
#                 POWER(SIN((RADIANS(cr.latitude) - RADIANS(chi.latitude))/2), 2) +
#                 COS(RADIANS(chi.latitude)) * COS(RADIANS(cr.latitude)) *
#                 POWER(SIN((RADIANS(cr.longitude) - RADIANS(chi.longitude))/2), 2)
#             ))) > 200 THEN 1 ELSE 0 END), 0) AS checkins_above_200m
#         {creche_count_select}
#     FROM `tabCreche` AS cr
#     INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
#     INNER JOIN `tabState` AS s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = cr.gp_id
#     {supervisor_join}
#     LEFT JOIN `tabCreche Check In` AS chi ON chi.creche_id = cr.name 
#         AND chi.date_of_checkin BETWEEN %(start_date)s AND %(end_date)s
#     {where_clause}
#     {group_by_clause}
#     ORDER BY {", ".join(group_by_fields)}
#     """

#     results = frappe.db.sql(query, params, as_dict=True)

#     data = []
#     for row in results:
#         total_checkins = (row.get('checkins_0_20m', 0) + row.get('checkins_20_50m', 0) + 
#                         row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         above_50m = (row.get('checkins_50_200m', 0) + row.get('checkins_above_200m', 0))
        
#         # Calculate percentage - show blank at creche level if no checkins
#         above_50m_percentage = round((above_50m / total_checkins * 100), 2) if total_checkins > 0 else (None if selected_level == "7" else 0)

#         data_row = {
#             "partner_name": row.get('partner_name', ''),
#             "state_name": row.get('state_name', ''),
#             "district_name": row.get('district_name', ''),
#             "block_name": row.get('block_name', ''),
#             "gp_name": row.get('gp_name', ''),
#             "creche_name": row.get('creche_name', ''),
#             "creche_id": row.get('creche_id', ''),
#             "supervisor_id": row.get('supervisor_id', ''),
#             "creche_opening_date": row.get('creche_opening_date', '') if selected_level == "7" else "",
#             "total_checkins": total_checkins,
#             "checkins_0_20m": row.get('checkins_0_20m', 0),
#             "checkins_20_50m": row.get('checkins_20_50m', 0),
#             "checkins_50_200m": row.get('checkins_50_200m', 0),
#             "checkins_above_200m": row.get('checkins_above_200m', 0)
#         }

#         # Always add percentage for non-creche levels, only add for creche level if there are checkins
#         if selected_level != "7" or (selected_level == "7" and total_checkins > 0):
#             data_row["above_50m_percentage"] = above_50m_percentage

#         # Add creche count for non-creche levels
#         if selected_level != "7":
#             data_row["creche_count"] = row.get('creche_count', 0)

#         data.append(data_row)

#     # Calculate totals with updated field names and make them bold
#     if data:
#         total_row = {
#             "partner_name": "TOTAL",
#             "state_name": "TOTAL",
#             "district_name": "",
#             "block_name": "",
#             "gp_name": "",
#             "creche_name": "",
#             "creche_id": "",
#             "supervisor_id": "",
#             "creche_opening_date": "",
#             "total_checkins": sum(row['total_checkins'] for row in data),
#             "checkins_0_20m": sum(row['checkins_0_20m'] for row in data),
#             "checkins_20_50m": sum(row['checkins_20_50m'] for row in data),
#             "checkins_50_200m": sum(row['checkins_50_200m'] for row in data),
#             "checkins_above_200m": sum(row['checkins_above_200m'] for row in data),
#             "is_total_row": True
#         }

#         # Calculate total creche count and percentage for non-creche levels
#         if selected_level != "7":
#             total_creche_count = sum(row['creche_count'] for row in data if 'creche_count' in row)
#             total_row["creche_count"] = total_creche_count
            
#             # Calculate overall percentage for total row
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             total_row["above_50m_percentage"] = round((total_above_50m / total_checkins * 100), 2) if total_checkins > 0 else 0
#         else:
#             # For creche level, don't show percentage in total row if no checkins
#             total_above_50m = total_row['checkins_50_200m'] + total_row['checkins_above_200m']
#             total_checkins = total_row['total_checkins']
#             if total_checkins > 0:
#                 total_row["above_50m_percentage"] = round((total_above_50m / total_checkins * 100), 2)
            
#         data.append(total_row)

#     return data