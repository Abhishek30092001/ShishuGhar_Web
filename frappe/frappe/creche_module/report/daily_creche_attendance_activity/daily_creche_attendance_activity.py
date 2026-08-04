import frappe
import calendar
from frappe.utils import nowdate
from datetime import datetime, date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_summary_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 150},
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 160},
        {"label": "Supervisor", "fieldname": "supervisor_name", "fieldtype": "Data", "width": 160},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Creche IDX", "fieldname": "creche_idx", "fieldtype": "Data", "width": 150, "hidden": 1},
        {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170},
        {"label": "Total Days Submitted", "fieldname": "submitted", "fieldtype": "Int", "width": 200},
        {"label": "Total Days Not Submitted", "fieldname": "not_submitted", "fieldtype": "Int", "width": 200},
        {"label": "Total Days Closed", "fieldname": "closed", "fieldtype": "Int", "width": 200},
    ]
    
    month = int(filters.get("month", nowdate().split('-')[1]))
    year = int(filters.get("year", nowdate().split('-')[0]))
    last_day = calendar.monthrange(year, month)[1]

    for day in range(1, last_day + 1):
        columns.append({
            "label": f"{day:02d}-{month:02d}-{year}",
            "fieldname": f"day_{day}",
            "fieldtype": "Data",
            "width": 120
        })
        
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    partner = frappe.db.get_value("User", frappe.session.user, "partner")
    month = int(filters.get("month", nowdate().split('-')[1]))
    year = int(filters.get("year", nowdate().split('-')[0]))
    last_day = calendar.monthrange(year, month)[1]
    current_date = date.today()

    # Get user geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    conditions = ["1=1"]
    conditions_att = ["1=1"]
    params = {
        'selected_partner': partner if partner else filters.get('partner'),
        'state': filters.get('state'),
        'district': filters.get('district'),
        'block': filters.get('block'),
        'gp': filters.get('gp'),
        'creche': filters.get('creche'),
        'supervisor_id': filters.get('supervisor_id'),
        'month': month,
        'year': year,
        'current_date': current_date,
        'creche_status_id': filters.get('creche_status_id'),
        'phases': ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
    }

    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            params['cstart_date'], params['cend_date'] = date_range
            conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
        elif range_type == "before" and single_date:
            conditions.append("cr.creche_opening_date < %(single_date)s")
            params['single_date'] = single_date
        elif range_type == "after" and single_date:
            conditions.append("cr.creche_opening_date > %(single_date)s")
            params['single_date'] = single_date
        elif range_type == "equal" and single_date:
            conditions.append("DATE(cr.creche_opening_date) = %(single_date)s")
            params['single_date'] = single_date

    if params.get('selected_partner'):
        conditions.append("cr.partner_id = %(selected_partner)s")
        conditions_att.append("tca.partner_id = %(selected_partner)s")
        
    if params.get('state'):
        conditions.append("cr.state_id = %(state)s")
        conditions_att.append("tca.state_id = %(state)s")
    elif current_user_state:
        state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
        if state_ids:
            params['state_ids'] = ",".join(state_ids)
            conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
            conditions_att.append("FIND_IN_SET(tca.state_id, %(state_ids)s)")

    if params.get('district'):
        conditions.append("cr.district_id = %(district)s")
        conditions_att.append("tca.district_id = %(district)s")
    elif current_user_state:
        district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
        if district_ids:
            params['district_ids'] = ",".join(district_ids)
            conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
            conditions_att.append("FIND_IN_SET(tca.district_id, %(district_ids)s)")

    if params.get('block'):
        conditions.append("cr.block_id = %(block)s")
        conditions_att.append("tca.block_id = %(block)s")
    elif current_user_state:
        block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
        if block_ids:
            params['block_ids'] = ",".join(block_ids)
            conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
            conditions_att.append("FIND_IN_SET(tca.block_id, %(block_ids)s)")

    if params.get('gp'):
        conditions.append("cr.gp_id = %(gp)s")
        conditions_att.append("tca.gp_id = %(gp)s")
    elif current_user_state:
        gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
        if gp_ids:
            params['gp_ids'] = ",".join(gp_ids)
            conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
            conditions_att.append("FIND_IN_SET(tca.gp_id, %(gp_ids)s)")

    if params.get('creche'):
        conditions.append("cr.name = %(creche)s")
        conditions_att.append("tca.creche_id = %(creche)s")
        
    if params.get('supervisor_id'):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        
    if params.get('phases'):
        conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")

    if params.get('creche_status_id'):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")

    daily_columns = []
    daily_columns_pc = []
    
    for day in range(1, last_day + 1):
        daily_columns.append(f"""
            CASE
                WHEN cr.creche_opening_date IS NULL THEN 'N/A'
                WHEN DATE('{year}-{month:02d}-{day:02d}') < cr.creche_opening_date THEN 'N/A'
                WHEN DATE('{year}-{month:02d}-{day:02d}') > DATE('{current_date}') THEN 'N/A'
                WHEN catt.day_{day} IS NULL THEN 'Not Submitted'
                WHEN catt.day_{day} = 'Closed' THEN 'Closed'
                ELSE 'Open'
            END AS day_{day}
        """)
        
        daily_columns_pc.append(f"""
            MAX(
                CASE
                    WHEN DAY(date_of_attendance) = {day} AND is_shishu_ghar_is_closed_for_the_day = 1 THEN 'Closed'
                    WHEN DAY(date_of_attendance) = {day} THEN 'Open'
                END
            ) AS day_{day}
        """)
    
    sql_query = f"""
    SELECT
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block,
        g.gp_name AS gp,
        cr.creche_name AS creche_name,
        cr.creche_id AS creche_id,
        sup.full_name AS supervisor_name,
        cr.name AS creche_idx,
        DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS 'creche_opening_date',
        {", ".join(daily_columns)}
    FROM `tabCreche` cr
    LEFT JOIN (
        SELECT creche_id, {", ".join(daily_columns_pc)}
        FROM `tabChild Attendance` tca
        WHERE YEAR(date_of_attendance) = %(year)s 
        AND MONTH(date_of_attendance) = %(month)s 
        AND {' AND '.join(conditions_att)}
        GROUP BY creche_id
    ) AS catt ON catt.creche_id = cr.name
    JOIN `tabState` s ON cr.state_id = s.name
    JOIN `tabDistrict` d ON cr.district_id = d.name
    JOIN `tabBlock` b ON cr.block_id = b.name
    JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
    JOIN `tabVillage` v ON cr.village_id = v.name
    JOIN `tabPartner` p ON cr.partner_id = p.name
    LEFT JOIN `tabUser` sup ON cr.supervisor_id = sup.name
    WHERE {' AND '.join(conditions)}
    ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, cr.creche_name
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)

    for row in data:
        submitted_count = 0
        not_submitted_count = 0
        closed_count = 0

        for day in range(1, last_day + 1):
            day_status = row.get(f"day_{day}")
            if day_status == "Closed":
                closed_count += 1
                submitted_count += 1
            elif day_status == "Open":
                submitted_count += 1
            elif day_status == "Not Submitted":
                not_submitted_count += 1

        row["submitted"] = submitted_count
        row["not_submitted"] = not_submitted_count
        row["closed"] = closed_count

    daily_totals = {f"day_{day}": 0 for day in range(1, last_day + 1)}
    for row in data:
        for day in range(1, last_day + 1):
            if row.get(f"day_{day}") in ["Open", "Closed"]:
                daily_totals[f"day_{day}"] += 1

    summary_row = {
        "creche_name": "<b style='color:black;'>Total</b>",
        "submitted": sum(row.get("submitted", 0) for row in data),
        "not_submitted": sum(row.get("not_submitted", 0) for row in data),
        "closed": sum(row.get("closed", 0) for row in data),
    }
    summary_row.update(daily_totals)
    data.append(summary_row)
    
    return data



# import frappe
# import calendar
# from frappe.utils import nowdate
# from datetime import datetime, timedelta, date

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_summary_data(filters)
#     return columns, data

# def get_columns(filters):
#     columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 150},
#         {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 160},
#         {"label": "Supervisor", "fieldname": "supervisor_name", "fieldtype": "Data", "width": 160},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche IDX", "fieldname": "creche_idx", "fieldtype": "Data", "width": 150, "hidden": 1},
#         {"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170},
#         {"label": "Total Days Submitted", "fieldname": "submitted", "fieldtype": "Int", "width": 200},
#         {"label": "Total Days Not Submitted", "fieldname": "not_submitted", "fieldtype": "Int", "width": 200},
#     ]
    
#     month = int(filters.get("month", nowdate().split('-')[1]))
#     year = int(filters.get("year", nowdate().split('-')[0]))
#     last_day = calendar.monthrange(year, month)[1]

#     for day in range(1, last_day + 1):
#         columns.append({
#             "label": f"{day:02d}-{month:02d}-{year}",
#             "fieldname": f"day_{day}",
#             "fieldtype": "Data",
#             "width": 120
#         })
        
#     return columns

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     month = int(filters.get("month", nowdate().split('-')[1]))
#     year = int(filters.get("year", nowdate().split('-')[0]))
#     last_day = calendar.monthrange(year, month)[1]
#     current_date = date.today()

#     # Get user geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
#     # Prepare filter conditions
#     conditions = ["1=1"]
#     conditions_att = ["1=1"]
#     params = {
#         'selected_partner': partner if partner else filters.get('partner'),
#         'state': filters.get('state'),
#         'district': filters.get('district'),
#         'block': filters.get('block'),
#         'gp': filters.get('gp'),
#         'creche': filters.get('creche'),
#         'supervisor_id': filters.get('supervisor_id'),
#         'month': month,
#         'year': year,
#         'current_date': current_date,
#         'creche_status_id': filters.get('creche_status_id'),
#         'phases': ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
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
#             conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#         elif range_type == "before" and single_date:
#             conditions.append("cr.creche_opening_date < %(single_date)s")
#             params['single_date'] = single_date
#         elif range_type == "after" and single_date:
#             conditions.append("cr.creche_opening_date > %(single_date)s")
#             params['single_date'] = single_date
#         elif range_type == "equal" and single_date:
#             conditions.append("DATE(cr.creche_opening_date) = %(single_date)s")
#             params['single_date'] = single_date

#     # Partner filter
#     if params.get('selected_partner'):
#         conditions.append("cr.partner_id = %(selected_partner)s")
#         conditions_att.append("tca.partner_id = %(selected_partner)s")
        
#     # Geography filters
#     if params.get('state'):
#         conditions.append("cr.state_id = %(state)s")
#         conditions_att.append("tca.state_id = %(state)s")
#     elif current_user_state:
#         state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#         if state_ids:
#             params['state_ids'] = ",".join(state_ids)
#             conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#             conditions_att.append("FIND_IN_SET(tca.state_id, %(state_ids)s)")

#     if params.get('district'):
#         conditions.append("cr.district_id = %(district)s")
#         conditions_att.append("tca.district_id = %(district)s")
#     elif current_user_state:
#         district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#         if district_ids:
#             params['district_ids'] = ",".join(district_ids)
#             conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#             conditions_att.append("FIND_IN_SET(tca.district_id, %(district_ids)s)")

#     if params.get('block'):
#         conditions.append("cr.block_id = %(block)s")
#         conditions_att.append("tca.block_id = %(block)s")
#     elif current_user_state:
#         block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#         if block_ids:
#             params['block_ids'] = ",".join(block_ids)
#             conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#             conditions_att.append("FIND_IN_SET(tca.block_id, %(block_ids)s)")

#     if params.get('gp'):
#         conditions.append("cr.gp_id = %(gp)s")
#         conditions_att.append("tca.gp_id = %(gp)s")
#     elif current_user_state:
#         gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
#         if gp_ids:
#             params['gp_ids'] = ",".join(gp_ids)
#             conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#             conditions_att.append("FIND_IN_SET(tca.gp_id, %(gp_ids)s)")

#     if params.get('creche'):
#         conditions.append("cr.name = %(creche)s")
#         conditions_att.append("tca.creche_id = %(creche)s")
        
#     if params.get('supervisor_id'):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
        
#     if params.get('phases'):
#         conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")

#     if params.get('creche_status_id'):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")

#     # Prepare daily columns
#     daily_columns = []
#     daily_columns_pc = []
    
#     for day in range(1, last_day + 1):
#         daily_columns.append(f"""
#             CASE
#                 WHEN cr.creche_opening_date IS NULL THEN 'N/A'
#                 WHEN DATE('{year}-{month:02d}-{day:02d}') < cr.creche_opening_date THEN 'N/A'
#                 WHEN DATE('{year}-{month:02d}-{day:02d}') > DATE('{current_date}') THEN 'N/A'
#                 WHEN catt.day_{day} IS NULL THEN 'Not Submitted'
#                 WHEN catt.day_{day} = 'Closed' THEN 'Closed'
#                 ELSE 'Open'
#             END AS day_{day}
#         """)
        
#         daily_columns_pc.append(f"""
#             MAX(
#                 CASE
#                     WHEN DAY(date_of_attendance) = {day} AND is_shishu_ghar_is_closed_for_the_day = 1 THEN 'Closed'
#                     WHEN DAY(date_of_attendance) = {day} THEN 'Open'
#                 END
#             ) AS day_{day}
#         """)
    
#     # Build the main query
#     sql_query = f"""
#     SELECT
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block,
#         g.gp_name AS gp,
#         cr.creche_name AS creche_name,
#         cr.creche_id AS creche_id,
#         sup.full_name AS supervisor_name,
#         cr.name AS creche_idx,
#         DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS 'creche_opening_date',
#         {", ".join(daily_columns)}
#     FROM `tabCreche` cr
#     LEFT JOIN (
#         SELECT creche_id, {", ".join(daily_columns_pc)}
#         FROM `tabChild Attendance` tca
#         WHERE YEAR(date_of_attendance) = %(year)s 
#         AND MONTH(date_of_attendance) = %(month)s 
#         AND {' AND '.join(conditions_att)}
#         GROUP BY creche_id
#     ) AS catt ON catt.creche_id = cr.name
#     JOIN `tabState` s ON cr.state_id = s.name
#     JOIN `tabDistrict` d ON cr.district_id = d.name
#     JOIN `tabBlock` b ON cr.block_id = b.name
#     JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
#     JOIN `tabVillage` v ON cr.village_id = v.name
#     JOIN `tabPartner` p ON cr.partner_id = p.name
#     LEFT JOIN `tabUser` sup ON cr.supervisor_id = sup.name
#     WHERE {' AND '.join(conditions)}
#     ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, cr.creche_name
#     """

#     data = frappe.db.sql(sql_query, params, as_dict=True)
    
#     # Calculate submitted and not submitted counts
#     for row in data:
#         submitted_count = 0
#         not_submitted_count = 0
        
#         for day in range(1, last_day + 1):
#             day_status = row.get(f"day_{day}")
#             if day_status in ["Open", "Closed"]:
#                 submitted_count += 1
#             elif day_status == "Not Submitted":
#                 not_submitted_count += 1
                
#         row["submitted"] = submitted_count
#         row["not_submitted"] = not_submitted_count

#     # Calculate daily totals for summary row
#     daily_totals = {f"day_{day}": 0 for day in range(1, last_day + 1)}
#     for row in data:
#         for day in range(1, last_day + 1):
#             if row.get(f"day_{day}") in ["Open", "Closed"]:
#                 daily_totals[f"day_{day}"] += 1

#     # Add summary row
#     summary_row = {
#         "creche_name": "<b style='color:black;'>Total</b>",
#         "submitted": sum(row.get("submitted", 0) for row in data),
#         "not_submitted": sum(row.get("not_submitted", 0) for row in data),
#     }
#     summary_row.update(daily_totals)
#     data.append(summary_row)
    
#     return data