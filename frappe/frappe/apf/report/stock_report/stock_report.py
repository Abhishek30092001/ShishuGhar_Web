import frappe
import json
import calendar
from frappe.utils import nowdate
from datetime import datetime, timedelta, date

def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 140},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
        {"label": "Items", "fieldname": "view_items", "fieldtype": "Data", "width": 250},
        {"label": "Items JSON", "fieldname": "items_json", "fieldtype": "Data", "hidden": 1},
    ]

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    params = prepare_parameters(filters)
    where_clause = build_where_clause(filters, params)
    raw_data = execute_main_query(params, where_clause)
    
    grouped_data = {}
    for row in raw_data:
        key = (
            row["Partner"], row["State"], row["District"], 
            row["Block"], row["Gram Panchayat"], 
            row["Creche ID"], row["Creche"]
        )
        
        if key not in grouped_data:
            grouped_data[key] = {
                "partner": row["Partner"],
                "state": row["State"],
                "district": row["District"],
                "block": row["Block"],
                "gp": row["Gram Panchayat"],
                "creche_id": row["Creche ID"],
                "creche_name": row["Creche"],
                "view_items": "View Items",
                "items_list": []
            }
        
        grouped_data[key]["items_list"].append({
            "item": row["Item"],
            "last_month_supplied": row["Last Month Supplied Amount"] or 0,
            "last_month_remaining": row["Last Month remaining Amount"] or 0,
            "required_this_month": row["Required this month"] or 0,
            "supplied_this_month": row["Supplied this month"] or 0
        })
    
    final_data = []
    for key, val in grouped_data.items():
        val["items_json"] = json.dumps(val.pop("items_list"))
        final_data.append(val)
        
    return final_data

def prepare_parameters(filters):
    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))
    
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    # FUTURE WEEK MASKING LOGIC
    if year == current_date.year and month == current_date.month:
        max_day = current_date.day
    elif year > current_date.year or (year == current_date.year and month > current_date.month):
        max_day = 0 
    else:
        max_day = 31 
    
    # LAST MONTH CALCULATION
    if month == 1:
        lmonth = 12
        lyear = year - 1
    else:
        lmonth = month - 1
        lyear = year
        
    # --- STATIC MAPPING FOR YEAR MASTER ---
    # Maps the calculated 'lyear' to the Database ID shown in your screenshot
    year_master_map = {
        2020: 1, 2021: 2, 2022: 3, 2023: 4,
        2024: 5, 2025: 6, 2026: 7, 2027: 8,
        2028: 9, 2029: 10, 2030: 11
    }
    # Fetch mapped ID (Defaults to math calculation lyear - 2019 if year is not in dict)
    lyear_id = year_master_map.get(lyear, lyear - 2019)
    
    params = {
        "start_date": start_date, "end_date": end_date, 
        "year": year, "month": month, "max_day": max_day, 
        "lyear": lyear, "lyear_id": lyear_id, "lmonth": lmonth,
        "cstart_date": None, "cend_date": None, "partner": None, "state": None,
        "district": None, "block": None, "gp": None, "creche": None,
        "supervisor_id": None, "creche_status_id": None, "phases": None, "creche_age": None,
    }
    
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    params["partner"] = filters.get("partner") or current_user_partner
    
    user_geo = frappe.db.sql("""
        SELECT state_id, district_id, block_id, gp_id FROM `tabUser Geography Mapping` WHERE parent = %s
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
    
    if filters.get("creche"): params["creche"] = filters.get("creche")
    if filters.get("supervisor_id"): params["supervisor_id"] = filters.get("supervisor_id")
    if filters.get("creche_status_id"): params["creche_status_id"] = filters.get("creche_status_id")
    if filters.get("phases"):
        cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
        if cleaned: params["phases"] = cleaned
    if filters.get("creche_age"): params["creche_age"] = filters.get("creche_age")
    
    return params

def build_where_clause(filters, params):
    conditions = ["1=1"]
    
    if params.get("partner"): conditions.append("c.partner_id = %(partner)s")
    if params.get("state"): conditions.append("c.state_id = %(state)s")
    elif params.get("state_ids"): conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
    if params.get("district"): conditions.append("c.district_id = %(district)s")
    elif params.get("district_ids"): conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
    if params.get("block"): conditions.append("c.block_id = %(block)s")
    elif params.get("block_ids"): conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
    if params.get("gp"): conditions.append("c.gp_id = %(gp)s")
    elif params.get("gp_ids"): conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
    if params.get("creche"): conditions.append("c.name = %(creche)s")
    if params.get("supervisor_id"): conditions.append("c.supervisor_id = %(supervisor_id)s")
    if params.get("creche_status_id"): conditions.append("c.creche_status_id = %(creche_status_id)s")
    if params.get("phases"): conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
    
    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"):
        conditions.append("DATE(c.creche_opening_date) = %(cstart_date)s")
        
    if params.get("creche_age"):
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
    
    return " AND ".join(conditions)

def execute_main_query(params, where_clause):
    sql_query = f"""
    SELECT
        p.partner_name         AS Partner,
        s.state_name           AS State,
        d.district_name        AS District,
        b.block_name           AS Block,
        gp.gp_name             AS "Gram Panchayat",
        c.creche_name          AS Creche,
        c.creche_id            AS "Creche ID",
        ps.items               AS "Item",

        /* FIX: Wrapped in aggregate functions to prevent duplicate item rows.
         Using IFNULL to gracefully handle empty previous month records.
        */
        SUM(IFNULL(csc.quantity_received, 0))  AS "Last Month Supplied Amount",
        MAX(IFNULL(csc.closing_stock, 0))      AS "Last Month remaining Amount",

        SUM(crc.quantity_required)  AS "Required this month",
        SUM(crc.quantity_supplied)  AS "Supplied this month"

    FROM `tabCreche Requisition` AS cr
    INNER JOIN `tabRequisition Child table` AS crc ON crc.parent = cr.name
    INNER JOIN `tabPartner Stock` AS ps  ON ps.name = crc.requistion_item
    INNER JOIN `tabCreche` AS c ON c.name = cr.creche_id
    INNER JOIN `tabPartner` AS p ON p.name = c.partner_id
    INNER JOIN `tabState` AS s  ON s.name = c.state_id
    INNER JOIN `tabDistrict` AS d ON d.name = c.district_id
    INNER JOIN `tabBlock` AS b ON b.name = c.block_id
    INNER JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id

    LEFT JOIN `tabCreche Stock` AS cs  
        ON cs.creche_id = cr.creche_id
    LEFT JOIN `tabStock Child table` AS csc 
        ON csc.parent = cs.name 
        AND csc.stock_item = crc.requistion_item
        AND csc.year = %(lyear_id)s 
        AND csc.month = %(lmonth)s

    WHERE 
        crc.supply_date BETWEEN %(start_date)s AND %(end_date)s
        AND {where_clause}

    GROUP BY 
        p.partner_name, s.state_name, d.district_name, b.block_name, 
        gp.gp_name, c.creche_name, c.creche_id, ps.items;
    """
    
    return frappe.db.sql(sql_query, params, as_dict=True)
















# import frappe
# import json
# import calendar
# from frappe.utils import nowdate
# from datetime import datetime, timedelta, date

# def execute(filters=None):
#     columns = get_columns()
#     data = get_summary_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 130},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 250},
#         {"label": "Items", "fieldname": "view_items", "fieldtype": "Data", "width": 150},
#         {"label": "Items JSON", "fieldname": "items_json", "fieldtype": "Data", "hidden": 1},
#     ]

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     params = prepare_parameters(filters)
#     where_clause = build_where_clause(filters, params)
#     raw_data = execute_main_query(params, where_clause)
    
#     grouped_data = {}
#     for row in raw_data:
#         key = (
#             row["Partner"], row["State"], row["District"], 
#             row["Block"], row["Gram Panchayat"], 
#             row["Creche ID"], row["Creche"]
#         )
        
#         if key not in grouped_data:
#             grouped_data[key] = {
#                 "partner": row["Partner"],
#                 "state": row["State"],
#                 "district": row["District"],
#                 "block": row["Block"],
#                 "gp": row["Gram Panchayat"],
#                 "creche_id": row["Creche ID"],
#                 "creche_name": row["Creche"],
#                 "view_items": "View Items",
#                 "items_list": []
#             }
        
#         grouped_data[key]["items_list"].append({
#             "item": row["Item"],
#             "required_this_month": row["Required this month"] or 0,
#             "supplied_this_month": row["Supplied this month"] or 0
#         })
    
#     final_data = []
#     for key, val in grouped_data.items():
#         val["items_json"] = json.dumps(val.pop("items_list"))
#         final_data.append(val)
        
#     return final_data

# def prepare_parameters(filters):
#     current_date = date.today()
#     month = int(filters.get("month", current_date.month))
#     year = int(filters.get("year", current_date.year))
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     params = {
#         "start_date": start_date, "end_date": end_date, "year": year, "month": month,
#         "cstart_date": None, "cend_date": None, "partner": None, "state": None,
#         "district": None, "block": None, "gp": None, "creche": None,
#         "supervisor_id": None, "creche_status_id": None, "phases": None, "creche_age": None,
#     }
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     params["partner"] = filters.get("partner") or current_user_partner
    
#     user_geo = frappe.db.sql("""
#         SELECT state_id, district_id, block_id, gp_id FROM `tabUser Geography Mapping` WHERE parent = %s
#     """, frappe.session.user, as_dict=True)
    
#     for key in ["state", "district", "block", "gp"]:
#         if filters.get(key):
#             params[key] = filters.get(key)
#         else:
#             ids = [str(s[f"{key}_id"]) for s in user_geo if s.get(f"{key}_id")]
#             if ids:
#                 params[f"{key}_ids"] = ",".join(ids)
    
#     range_type = filters.get("cr_opening_range_type")
#     if range_type:
#         single_date = filters.get("single_date")
#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
        
#         if range_type == "between" and filters.get("c_opening_range"):
#             params["cstart_date"], params["cend_date"] = filters["c_opening_range"]
#         elif range_type == "before" and single_date:
#             params["cstart_date"] = date(2017, 1, 1)
#             params["cend_date"] = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             params["cstart_date"] = single_date + timedelta(days=1)
#             params["cend_date"] = date.today()
#         elif range_type == "equal" and single_date:
#             params["cstart_date"] = params["cend_date"] = single_date
    
#     if filters.get("creche"): params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"): params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"): params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if cleaned: params["phases"] = cleaned
#     if filters.get("creche_age"): params["creche_age"] = filters.get("creche_age")
    
#     return params

# def build_where_clause(filters, params):
#     conditions = ["1=1"]
    
#     if params.get("partner"): conditions.append("c.partner_id = %(partner)s")
#     if params.get("state"): conditions.append("c.state_id = %(state)s")
#     elif params.get("state_ids"): conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#     if params.get("district"): conditions.append("c.district_id = %(district)s")
#     elif params.get("district_ids"): conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#     if params.get("block"): conditions.append("c.block_id = %(block)s")
#     elif params.get("block_ids"): conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#     if params.get("gp"): conditions.append("c.gp_id = %(gp)s")
#     elif params.get("gp_ids"): conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#     if params.get("creche"): conditions.append("c.name = %(creche)s")
#     if params.get("supervisor_id"): conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if params.get("creche_status_id"): conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if params.get("phases"): conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
    
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):
#         conditions.append("DATE(c.creche_opening_date) = %(cstart_date)s")
        
#     if params.get("creche_age"):
#         conditions.append("""
#             CASE
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
    
#     return " AND ".join(conditions)

# def execute_main_query(params, where_clause):
#     sql_query = f"""
#     SELECT
#         p.partner_name         AS Partner,
#         s.state_name           AS State,
#         d.district_name        AS District,
#         b.block_name           AS Block,
#         gp.gp_name             AS "Gram Panchayat",
#         c.creche_name          AS Creche,
#         c.creche_id            AS "Creche ID",
#         ps.items               AS "Item",

#         SUM(crc.quantity_required)  AS "Required this month",
#         SUM(crc.quantity_supplied)  AS "Supplied this month"

#     FROM `tabCreche Requisition` AS cr
#     INNER JOIN `tabRequisition Child table` AS crc ON crc.parent = cr.name
#     INNER JOIN `tabPartner Stock` AS ps  ON ps.name = crc.requistion_item
#     INNER JOIN `tabCreche` AS c ON c.name = cr.creche_id
#     INNER JOIN `tabPartner` AS p ON p.name = c.partner_id
#     INNER JOIN `tabState` AS s  ON s.name = c.state_id
#     INNER JOIN `tabDistrict` AS d ON d.name = c.district_id
#     INNER JOIN `tabBlock` AS b ON b.name = c.block_id
#     INNER JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id

#     WHERE 
#         crc.supply_date BETWEEN %(start_date)s AND %(end_date)s
#         AND {where_clause}
        
#     GROUP BY 
#         p.partner_name, s.state_name, d.district_name, b.block_name, 
#         gp.gp_name, c.creche_name, c.creche_id, ps.items;
#     """
    
#     return frappe.db.sql(sql_query, params, as_dict=True)