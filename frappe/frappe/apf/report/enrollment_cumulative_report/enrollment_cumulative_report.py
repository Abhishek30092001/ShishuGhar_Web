import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    columns = get_columns(filters)
    data = get_report_data(filters)
    return columns, data

def get_columns(filters):
    """Define report columns based on level filter"""
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
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 200})
        variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
    
    fixed_columns = [
        {"label": _("Operational Creches"), "fieldname": "op_creches", "fieldtype": "Int", "width": 250},
        {"label": _("Total No of Children (HH List)"), "fieldname": "total_children_hh", "fieldtype": "Int", "width": 230},
        {"label": _("Cumulative Enrolled"), "fieldname": "cumulative_enrolled", "fieldtype": "Int", "width": 170},
        {"label": _("Cumulative Current Enrolled"), "fieldname": "currently_active", "fieldtype": "Int", "width": 210},
        {"label": _("Cumulative Exit"), "fieldname": "cumulative_exit", "fieldtype": "Int", "width": 150},
        {"label": _("Cumulative Migrated"), "fieldname": "migrated", "fieldtype": "Int", "width": 170},
        {"label": _("Cumulative Graduated"), "fieldname": "graduated", "fieldtype": "Int", "width": 180},
        {"label": _("Cumulative Not Willing to Stay"), "fieldname": "not_willing_to_stay", "fieldtype": "Int", "width": 240},
        {"label": _("Cumulative Death"), "fieldname": "death", "fieldtype": "Int", "width": 160},
        {"label": _("Other"), "fieldname": "other", "fieldtype": "Int", "width": 120},
    ]
    
    columns = variable_columns + fixed_columns
    return columns

def get_report_data(filters):
    """Get report data based on filters"""
    
    # Date range logic
    start_date, end_date = get_date_range(filters)
    
    # Build conditions and parameters
    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    # Apply user geography restrictions
    apply_user_geography_filters(conditions, params, filters)
    
    # Apply other filters
    apply_other_filters(conditions, params, filters)
    
    # Apply creche opening date filters
    apply_creche_opening_filters(conditions, params, filters)
    
    # Apply creche_age filter
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
    
    # Build and execute query
    query = build_query(conditions, filters)
    data = frappe.db.sql(query, params, as_dict=True)
    
    return data

def get_date_range(filters):
    """Get date range from filters"""
    start_date, end_date = None, None
    
    if filters.get("time_range"):
        time_range = filters.get("time_range")
        if time_range and len(time_range) == 2:
            start_date, end_date = time_range
    elif filters.get("year") and filters.get("month"):
        current_date = date.today()
        month = int(filters.get("month")) if filters.get("month") else current_date.month
        year = int(filters.get("year")) if filters.get("year") else current_date.year
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    
    return start_date, end_date

def apply_user_geography_filters(conditions, params, filters):
    """Apply user geography mapping filters"""
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    # Get user's geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
    # Build comma-separated strings for FIND_IN_SET
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    
    # Apply partner filter if specified
    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        params["partner"] = partner_id
    
    # Apply geography filters if not overridden by user selection
    if not filters.get("state") and state_ids:
        conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
        params["state_ids"] = state_ids
    
    if not filters.get("district") and district_ids:
        conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
        params["district_ids"] = district_ids
    
    if not filters.get("block") and block_ids:
        conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
        params["block_ids"] = block_ids
    
    if not filters.get("gp") and gp_ids:
        conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
        params["gp_ids"] = gp_ids

def apply_other_filters(conditions, params, filters):
    """Apply other standard filters"""
    
    # Geography filters (overrides user mapping if specified)
    if filters.get("state"):
        conditions.append("c.state_id = %(state)s")
        params["state"] = filters.get("state")
    
    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        params["district"] = filters.get("district")
    
    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        params["block"] = filters.get("block")
    
    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    
    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
        params["creche"] = filters.get("creche")
    
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")
    
    if filters.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
        if phases_cleaned:
            conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
            params["phases"] = phases_cleaned

def apply_creche_opening_filters(conditions, params, filters):
    """Apply creche opening date filters"""
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
        
        if cstart_date or cend_date:
            conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
            params["cstart_date"] = cstart_date if cstart_date else None
            params["cend_date"] = cend_date if cend_date else None

def build_query(conditions, filters):
    """Build the main SQL query with level-based grouping"""
    where_clause = " AND ".join(conditions)
    
    # Define level mapping for GROUP BY and SELECT
    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "c.creche_name", "u.full_name"],
    }
    
    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)
    
    # Build SELECT fields based on level
    select_fields = [
        "p.partner_name AS partner",
        "s.state_name AS state",
        "d.district_name AS district",
        "b.block_name AS block",
        "u.full_name AS supervisor",
        "g.gp_name AS gp",
        "c.creche_name AS creche",
    ]
    
    selected_fields = []
    for field in select_fields:
        field_name = field.split(" AS ")[0].split(".")[1]
        if any(field_name in group_field for group_field in group_by_fields):
            selected_fields.append(field)
    
    # Add creche_opening_date only for level 7
    if selected_level == "7":
        selected_fields.append("DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date")
    
    # Fixed query using Creche as the main table like the original code
    query = f"""
        SELECT 
            {", ".join(selected_fields) if selected_fields else "1"},
            COUNT(DISTINCT c.name) AS op_creches,
            IFNULL(SUM(hh_counts.total_children_hh), 0) AS total_children_hh,
            IFNULL(SUM(enrollment_counts.cumulative_enrolled), 0) AS cumulative_enrolled,
            IFNULL(SUM(cuenroll.currently_active), 0) AS currently_active,
            IFNULL(SUM(exit_counts.cumulative_exit), 0) AS cumulative_exit,
            IFNULL(SUM(exit_counts.migrated), 0) AS migrated,
            IFNULL(SUM(exit_counts.graduated), 0) AS graduated,
            IFNULL(SUM(exit_counts.not_willing_to_stay), 0) AS not_willing_to_stay,
            IFNULL(SUM(exit_counts.death), 0) AS death,
            IFNULL(SUM(exit_counts.other), 0) AS other
        FROM `tabCreche` c
        INNER JOIN `tabState` s ON c.state_id = s.name
        INNER JOIN `tabDistrict` d ON c.district_id = d.name
        INNER JOIN `tabBlock` b ON c.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        INNER JOIN `tabPartner` p ON c.partner_id = p.name
        LEFT JOIN `tabUser` u ON u.name = c.supervisor_id
        LEFT JOIN (
            SELECT 
                hf.creche_id,
                COUNT(DISTINCT hc.name) AS total_children_hh
            FROM `tabHousehold Child Form` hc
            INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
            WHERE hc.is_dob_available = 1 
            GROUP BY hf.creche_id
        ) AS hh_counts ON hh_counts.creche_id = c.name
        LEFT JOIN (
            SELECT 
                creche_id,
                COUNT(*) AS cumulative_enrolled
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_enrollment <= %(end_date)s
            GROUP BY creche_id
        ) AS enrollment_counts ON enrollment_counts.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id, 
                   SUM(CASE WHEN date_of_exit IS NULL OR date_of_exit > %(end_date)s THEN 1 ELSE 0 END) AS currently_active
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_enrollment <= %(end_date)s
            GROUP BY creche_id
        ) AS cuenroll ON cuenroll.creche_id = c.name
        LEFT JOIN (
            SELECT 
                creche_id,
                SUM(CASE WHEN date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS cumulative_exit,
                SUM(CASE WHEN reason_for_exit = 1 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS migrated,
                SUM(CASE WHEN reason_for_exit = 2 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS graduated,
                SUM(CASE WHEN reason_for_exit = 3 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS not_willing_to_stay,
                SUM(CASE WHEN reason_for_exit = 4 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS death,
                SUM(CASE WHEN reason_for_exit = 5 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS other
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_exit <= %(end_date)s
            GROUP BY creche_id
        ) AS exit_counts ON exit_counts.creche_id = c.name
        WHERE {where_clause}
        AND (c.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s))
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}
    """
    
    return query













#Backup_before crecheage
# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_report_data(filters)
#     return columns, data

# def get_columns(filters):
#     """Define report columns based on level filter"""
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
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 200})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
    
#     fixed_columns = [
#         {"label": _("Operational Creches"), "fieldname": "op_creches", "fieldtype": "Int", "width": 250},
#         {"label": _("Total No of Children (HH List)"), "fieldname": "total_children_hh", "fieldtype": "Int", "width": 230},
#         {"label": _("Cumulative Enrolled"), "fieldname": "cumulative_enrolled", "fieldtype": "Int", "width": 170},
#         {"label": _("Cumulative Current Enrolled"), "fieldname": "currently_active", "fieldtype": "Int", "width": 210},
#         {"label": _("Cumulative Exit"), "fieldname": "cumulative_exit", "fieldtype": "Int", "width": 150},
#         {"label": _("Cumulative Migrated"), "fieldname": "migrated", "fieldtype": "Int", "width": 170},
#         {"label": _("Cumulative Graduated"), "fieldname": "graduated", "fieldtype": "Int", "width": 180},
#         {"label": _("Cumulative Not Willing to Stay"), "fieldname": "not_willing_to_stay", "fieldtype": "Int", "width": 240},
#         {"label": _("Cumulative Death"), "fieldname": "death", "fieldtype": "Int", "width": 160},
#         {"label": _("Other"), "fieldname": "other", "fieldtype": "Int", "width": 120},
#     ]
    
#     columns = variable_columns + fixed_columns
#     return columns

# def get_report_data(filters):
#     """Get report data based on filters"""
    
#     # Date range logic
#     start_date, end_date = get_date_range(filters)
    
#     # Build conditions and parameters
#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date
#     }
    
#     # Apply user geography restrictions
#     apply_user_geography_filters(conditions, params, filters)
    
#     # Apply other filters
#     apply_other_filters(conditions, params, filters)
    
#     # Apply creche opening date filters
#     apply_creche_opening_filters(conditions, params, filters)
    
#     # Build and execute query
#     query = build_query(conditions, filters)
#     data = frappe.db.sql(query, params, as_dict=True)
    
#     return data

# def get_date_range(filters):
#     """Get date range from filters"""
#     start_date, end_date = None, None
    
#     if filters.get("time_range"):
#         time_range = filters.get("time_range")
#         if time_range and len(time_range) == 2:
#             start_date, end_date = time_range
#     elif filters.get("year") and filters.get("month"):
#         current_date = date.today()
#         month = int(filters.get("month")) if filters.get("month") else current_date.month
#         year = int(filters.get("year")) if filters.get("year") else current_date.year
#         start_date = date(year, month, 1)
#         last_day = calendar.monthrange(year, month)[1]
#         end_date = date(year, month, last_day)
    
#     return start_date, end_date

# def apply_user_geography_filters(conditions, params, filters):
#     """Apply user geography mapping filters"""
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner
    
#     # Get user's geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
#     # Build comma-separated strings for FIND_IN_SET
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    
#     # Apply partner filter if specified
#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     # Apply geography filters if not overridden by user selection
#     if not filters.get("state") and state_ids:
#         conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#         params["state_ids"] = state_ids
    
#     if not filters.get("district") and district_ids:
#         conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#         params["district_ids"] = district_ids
    
#     if not filters.get("block") and block_ids:
#         conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#         params["block_ids"] = block_ids
    
#     if not filters.get("gp") and gp_ids:
#         conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#         params["gp_ids"] = gp_ids

# def apply_other_filters(conditions, params, filters):
#     """Apply other standard filters"""
    
#     # Geography filters (overrides user mapping if specified)
#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
    
#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
    
#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
    
#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
    
#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if phases_cleaned:
#             conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#             params["phases"] = phases_cleaned

# def apply_creche_opening_filters(conditions, params, filters):
#     """Apply creche opening date filters"""
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
        
#         if cstart_date or cend_date:
#             conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
#             params["cstart_date"] = cstart_date if cstart_date else None
#             params["cend_date"] = cend_date if cend_date else None

# def build_query(conditions, filters):
#     """Build the main SQL query with level-based grouping"""
#     where_clause = " AND ".join(conditions)
    
#     # Define level mapping for GROUP BY and SELECT
#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "c.creche_name"],
#     }
    
#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)
    
#     # Build SELECT fields based on level
#     select_fields = [
#         "p.partner_name AS partner",
#         "s.state_name AS state",
#         "d.district_name AS district",
#         "b.block_name AS block",
#         "u.full_name AS supervisor",
#         "g.gp_name AS gp",
#         "c.creche_name AS creche",
#     ]
    
#     selected_fields = []
#     for field in select_fields:
#         field_name = field.split(" AS ")[0].split(".")[1]
#         if any(field_name in group_field for group_field in group_by_fields):
#             selected_fields.append(field)
    
#     # Add creche_opening_date only for level 7
#     if selected_level == "7":
#         selected_fields.append("DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date")
    
#     # Fixed query using Creche as the main table like the original code
#     query = f"""
#         SELECT 
#             {", ".join(selected_fields) if selected_fields else "1"},
#             COUNT(DISTINCT c.name) AS op_creches,
#             IFNULL(SUM(hh_counts.total_children_hh), 0) AS total_children_hh,
#             IFNULL(SUM(enrollment_counts.cumulative_enrolled), 0) AS cumulative_enrolled,
#             IFNULL(SUM(cuenroll.currently_active), 0) AS currently_active,
#             IFNULL(SUM(exit_counts.cumulative_exit), 0) AS cumulative_exit,
#             IFNULL(SUM(exit_counts.migrated), 0) AS migrated,
#             IFNULL(SUM(exit_counts.graduated), 0) AS graduated,
#             IFNULL(SUM(exit_counts.not_willing_to_stay), 0) AS not_willing_to_stay,
#             IFNULL(SUM(exit_counts.death), 0) AS death,
#             IFNULL(SUM(exit_counts.other), 0) AS other
#         FROM `tabCreche` c
#         INNER JOIN `tabState` s ON c.state_id = s.name
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         INNER JOIN `tabPartner` p ON c.partner_id = p.name
#         LEFT JOIN `tabUser` u ON u.name = c.supervisor_id
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(DISTINCT hc.name) AS total_children_hh
#             FROM `tabHousehold Child Form` hc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
#             WHERE hc.is_dob_available = 1 
#             GROUP BY hf.creche_id
#         ) AS hh_counts ON hh_counts.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 creche_id,
#                 COUNT(*) AS cumulative_enrolled
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment <= %(end_date)s
#             GROUP BY creche_id
#         ) AS enrollment_counts ON enrollment_counts.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id, 
#                    SUM(CASE WHEN date_of_exit IS NULL OR date_of_exit > %(end_date)s THEN 1 ELSE 0 END) AS currently_active
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment <= %(end_date)s
#             GROUP BY creche_id
#         ) AS cuenroll ON cuenroll.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 creche_id,
#                 SUM(CASE WHEN date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS cumulative_exit,
#                 SUM(CASE WHEN reason_for_exit = 1 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS migrated,
#                 SUM(CASE WHEN reason_for_exit = 2 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS graduated,
#                 SUM(CASE WHEN reason_for_exit = 3 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS not_willing_to_stay,
#                 SUM(CASE WHEN reason_for_exit = 4 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS death,
#                 SUM(CASE WHEN reason_for_exit = 5 AND date_of_exit IS NOT NULL AND date_of_exit <= %(end_date)s THEN 1 ELSE 0 END) AS other
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_exit <= %(end_date)s
#             GROUP BY creche_id
#         ) AS exit_counts ON exit_counts.creche_id = c.name
#         WHERE {where_clause}
#         AND (c.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s))
#         GROUP BY {group_by_field}
#         ORDER BY {group_by_field}
#     """
    
#     return query









