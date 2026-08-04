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
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 150},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
    
        {"label": "Opening Balance", "fieldname": "opening_balance", "fieldtype": "Currency", "options": "currency", "width": 180},
        {"label": "Amount Transferred (This Month)", "fieldname": "amount_transferred", "fieldtype": "Currency", "options": "currency", "width": 260},
        {"label": "Total Balance", "fieldname": "total_balance", "fieldtype": "Currency", "options": "currency", "width": 180},
        
        {"label": "Expenditure (Week-1)", "fieldname": "expenditure_w1", "fieldtype": "Currency", "options": "currency", "width": 240},
        {"label": "Balance (Week-1)", "fieldname": "balance_w1", "fieldtype": "Currency", "options": "currency", "width": 215},
        
        {"label": "Expenditure (Week-2)", "fieldname": "expenditure_w2", "fieldtype": "Currency", "options": "currency", "width": 240},
        {"label": "Balance (Week-2)", "fieldname": "balance_w2", "fieldtype": "Currency", "options": "currency", "width": 215},
        
        {"label": "Expenditure (Week-3)", "fieldname": "expenditure_w3", "fieldtype": "Currency", "options": "currency", "width": 240},
        {"label": "Balance (Week-3)", "fieldname": "balance_w3", "fieldtype": "Currency", "options": "currency", "width": 215},
        
        {"label": "Expenditure (Week-4)", "fieldname": "expenditure_w4", "fieldtype": "Currency", "options": "currency", "width": 240},
        {"label": "Balance (Week-4)", "fieldname": "balance_w4", "fieldtype": "Currency", "options": "currency", "width": 215},
        
        {"label": "Expenditure (Week-5)", "fieldname": "expenditure_w5", "fieldtype": "Currency", "options": "currency", "width": 240},
        {"label": "Balance (Week-5)", "fieldname": "balance_w5", "fieldtype": "Currency", "options": "currency", "width": 215},
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
    end_date = date(year, month, last_day)
    
    # FUTURE WEEK MASKING LOGIC
    if year == current_date.year and month == current_date.month:
        max_day = current_date.day
    elif year > current_date.year or (year == current_date.year and month > current_date.month):
        max_day = 0 # Future month
    else:
        max_day = 31 # Past month
    
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
        "end_date": end_date,
        "year": year,
        "month": month,
        "max_day": max_day, 
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
    
    return params

def build_where_clause(filters, params):
    conditions = ["1=1"]
    
    if params.get("partner"):
        conditions.append("c.partner_id = %(partner)s")
    if params.get("state"):
        conditions.append("c.state_id = %(state)s")
    elif params.get("state_ids"):
        conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
    if params.get("district"):
        conditions.append("c.district_id = %(district)s")
    elif params.get("district_ids"):
        conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
    if params.get("block"):
        conditions.append("c.block_id = %(block)s")
    elif params.get("block_ids"):
        conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
    if params.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
    elif params.get("gp_ids"):
        conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
    if params.get("creche"):
        conditions.append("c.name = %(creche)s")
    if params.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
    if params.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
    if params.get("phases"):
        conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
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
    sql_query = """
        SELECT 
            partner, state, district, block, gp, supervisor, creche_id, creche_name, currency,
            
            opening_balance, 
            amount_transferred, 
            total_balance,
            
            expenditure_w1,
            CASE WHEN %(max_day)s >= 1 THEN (total_balance - expenditure_w1) ELSE 0 END AS balance_w1,
            
            expenditure_w2,
            CASE WHEN %(max_day)s >= 8 THEN (total_balance - expenditure_w1 - expenditure_w2) ELSE 0 END AS balance_w2,
            
            expenditure_w3,
            CASE WHEN %(max_day)s >= 15 THEN (total_balance - expenditure_w1 - expenditure_w2 - expenditure_w3) ELSE 0 END AS balance_w3,
            
            expenditure_w4,
            CASE WHEN %(max_day)s >= 22 THEN (total_balance - expenditure_w1 - expenditure_w2 - expenditure_w3 - expenditure_w4) ELSE 0 END AS balance_w4,
            
            expenditure_w5,
            CASE WHEN %(max_day)s >= 29 THEN (total_balance - expenditure_w1 - expenditure_w2 - expenditure_w3 - expenditure_w4 - expenditure_w5) ELSE 0 END AS balance_w5

        FROM (
            SELECT 
                p.partner_name AS partner,
                s.state_name AS state,
                d.district_name AS district,
                b.block_name AS block,
                gp.gp_name AS gp,
                sup.full_name AS supervisor,
                c.creche_id AS creche_id,
                c.creche_name AS creche_name,
                'INR' AS currency,
                
                -- BRAIN FIX: CARRY-FORWARD ROLLED OVER BALANCE
                -- Initial Saved Opening Balance + All Previous Receipts - All Previous Expenses
                (COALESCE(he.max_initial_balance, 0) + COALESCE(hr.past_receipts, 0) - COALESCE(he.past_expenses, 0)) AS opening_balance,
                
                -- THIS MONTH'S RECEIVED AMOUNT
                COALESCE(hr.current_receipts, 0) AS amount_transferred,
                
                -- TOTAL AMOUNT AVAILABLE FOR THIS MONTH
                ((COALESCE(he.max_initial_balance, 0) + COALESCE(hr.past_receipts, 0) - COALESCE(he.past_expenses, 0)) + COALESCE(hr.current_receipts, 0)) AS total_balance,
                
                CASE WHEN %(max_day)s >= 1 THEN COALESCE(e.expenditure_w1, 0) ELSE 0 END AS expenditure_w1,
                CASE WHEN %(max_day)s >= 8 THEN COALESCE(e.expenditure_w2, 0) ELSE 0 END AS expenditure_w2,
                CASE WHEN %(max_day)s >= 15 THEN COALESCE(e.expenditure_w3, 0) ELSE 0 END AS expenditure_w3,
                CASE WHEN %(max_day)s >= 22 THEN COALESCE(e.expenditure_w4, 0) ELSE 0 END AS expenditure_w4,
                CASE WHEN %(max_day)s >= 29 THEN COALESCE(e.expenditure_w5, 0) ELSE 0 END AS expenditure_w5
                
            FROM `tabCreche` c
            
            -- HISTORICAL & CURRENT RECEIPTS
            LEFT JOIN (
                SELECT 
                    creche_id,
                    SUM(CASE WHEN date < %(start_date)s THEN COALESCE(amount, 0) ELSE 0 END) AS past_receipts,
                    SUM(CASE WHEN YEAR(date) = %(year)s AND MONTH(date) = %(month)s THEN COALESCE(amount, 0) ELSE 0 END) AS current_receipts
                FROM `tabCashbook Receipt`
                GROUP BY creche_id
            ) hr ON c.name = hr.creche_id
            
            -- HISTORICAL EXPENSES & INITIAL SEED BALANCE
            LEFT JOIN (
                SELECT 
                    creche_id,
                    MAX(opening_balance) AS max_initial_balance,
                    SUM(CASE WHEN date < %(start_date)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS past_expenses
                FROM `tabCashbook`
                GROUP BY creche_id
            ) he ON c.name = he.creche_id
            
            -- CURRENT MONTH EXPENSES BY WEEK
            LEFT JOIN (
                SELECT 
                    creche_id,
                    SUM(CASE WHEN DAY(date) BETWEEN 1 AND 7 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w1,
                    SUM(CASE WHEN DAY(date) BETWEEN 8 AND 14 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w2,
                    SUM(CASE WHEN DAY(date) BETWEEN 15 AND 21 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w3,
                    SUM(CASE WHEN DAY(date) BETWEEN 22 AND 28 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w4,
                    SUM(CASE WHEN DAY(date) >= 29 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w5
                FROM `tabCashbook`
                WHERE YEAR(date) = %(year)s AND MONTH(date) = %(month)s
                GROUP BY creche_id
            ) e ON c.name = e.creche_id
            
            LEFT JOIN `tabPartner` p ON c.partner_id = p.name
            LEFT JOIN `tabState` s ON c.state_id = s.name
            LEFT JOIN `tabDistrict` d ON c.district_id = d.name
            LEFT JOIN `tabBlock` b ON c.block_id = b.name
            LEFT JOIN `tabGram Panchayat` gp ON c.gp_id = gp.name
            LEFT JOIN `tabUser` sup ON c.supervisor_id = sup.name
            
            WHERE {where_clause} 
              AND (
                  hr.creche_id IS NOT NULL 
                  OR he.creche_id IS NOT NULL 
                  OR e.creche_id IS NOT NULL
              )
        ) AS base_data
        
        ORDER BY creche_name
    """.format(where_clause=where_clause)
    
    return frappe.db.sql(sql_query, params, as_dict=True)









# import frappe
# from frappe.utils import nowdate
# import calendar
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
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 120},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
    
#         {"label": "Opening Balance", "fieldname": "opening_balance", "fieldtype": "Currency", "options": "currency", "width": 180},
#         {"label": "Amount Transferred (This Month)", "fieldname": "amount_transferred", "fieldtype": "Currency", "options": "currency", "width": 260},
#         {"label": "Total Balance", "fieldname": "total_balance", "fieldtype": "Currency", "options": "currency", "width": 180},
        
#         {"label": "Expenditure (Week-1)", "fieldname": "expenditure_w1", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-1)", "fieldname": "balance_w1", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-2)", "fieldname": "expenditure_w2", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-2)", "fieldname": "balance_w2", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-3)", "fieldname": "expenditure_w3", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-3)", "fieldname": "balance_w3", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-4)", "fieldname": "expenditure_w4", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-4)", "fieldname": "balance_w4", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-5)", "fieldname": "expenditure_w5", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-5)", "fieldname": "balance_w5", "fieldtype": "Currency", "options": "currency", "width": 215},
#     ]

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     params = prepare_parameters(filters)
#     where_clause = build_where_clause(filters, params)
#     data = execute_main_query(params, where_clause)
#     return data

# def prepare_parameters(filters):
#     current_date = date.today()
#     month = int(filters.get("month", current_date.month))
#     year = int(filters.get("year", current_date.year))
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     # FUTURE WEEK MASKING LOGIC
#     if year == current_date.year and month == current_date.month:
#         max_day = current_date.day
#     elif year > current_date.year or (year == current_date.year and month > current_date.month):
#         max_day = 0 # Future month
#     else:
#         max_day = 31 # Past month
    
#     if month == 1:
#         lmonth, plmonth = 12, 11
#         lyear, pyear = year - 1, year - 1
#     elif month == 2:
#         lmonth, plmonth = 1, 12
#         lyear, pyear = year, year - 1
#     else:
#         lmonth, plmonth = month - 1, month - 2
#         lyear, pyear = year, year
    
#     l2month = plmonth
#     l2year = pyear
#     if plmonth == 1:
#         l2month = 12
#         l2year = pyear - 1
#     else:
#         l2month = plmonth - 1
#         l2year = pyear
    
#     l3month = l2month
#     l3year = l2year
#     if l2month == 1:
#         l3month = 12
#         l3year = l2year - 1
#     else:
#         l3month = l2month - 1
#         l3year = l2year
    
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "max_day": max_day, 
#         "lyear": lyear,
#         "lmonth": lmonth,
#         "plmonth": plmonth,
#         "pyear": pyear,
#         "l2month": l2month,
#         "l2year": l2year,
#         "l3month": l3month,
#         "l3year": l3year,
#         "cstart_date": None,
#         "cend_date": None,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#         "supervisor_id": None,
#         "creche_status_id": None,
#         "phases": None,
#         "creche_age": None,
#     }
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     params["partner"] = filters.get("partner") or current_user_partner
    
#     user_geo = frappe.db.sql("""
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
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
    
#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if cleaned:
#             params["phases"] = cleaned
#     if filters.get("creche_age"):
#         params["creche_age"] = filters.get("creche_age")
    
#     return params

# def build_where_clause(filters, params):
#     conditions = ["1=1"]
    
#     if params.get("partner"):
#         conditions.append("c.partner_id = %(partner)s")
#     if params.get("state"):
#         conditions.append("c.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#     if params.get("district"):
#         conditions.append("c.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#     if params.get("block"):
#         conditions.append("c.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#     if params.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#     if params.get("creche"):
#         conditions.append("c.name = %(creche)s")
#     if params.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if params.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
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
#     sql_query = """
#         SELECT 
#             partner, state, district, block, gp, creche_id, creche_name, currency,
            
#             opening_balance, 
#             amount_transferred, 
#             total_balance,
            
#             expenditure_w1,
#             CASE WHEN %(max_day)s >= 1 THEN (total_balance - expenditure_w1) ELSE 0 END AS balance_w1,
            
#             expenditure_w2,
#             CASE WHEN %(max_day)s >= 8 THEN (total_balance - expenditure_w1 - expenditure_w2) ELSE 0 END AS balance_w2,
            
#             expenditure_w3,
#             CASE WHEN %(max_day)s >= 15 THEN (total_balance - expenditure_w1 - expenditure_w2 - expenditure_w3) ELSE 0 END AS balance_w3,
            
#             expenditure_w4,
#             CASE WHEN %(max_day)s >= 22 THEN (total_balance - expenditure_w1 - expenditure_w2 - expenditure_w3 - expenditure_w4) ELSE 0 END AS balance_w4,
            
#             expenditure_w5,
#             CASE WHEN %(max_day)s >= 29 THEN (total_balance - expenditure_w1 - expenditure_w2 - expenditure_w3 - expenditure_w4 - expenditure_w5) ELSE 0 END AS balance_w5

#         FROM (
#             SELECT 
#                 p.partner_name AS partner,
#                 s.state_name AS state,
#                 d.district_name AS district,
#                 b.block_name AS block,
#                 gp.gp_name AS gp,
#                 c.creche_id AS creche_id,
#                 c.creche_name AS creche_name,
#                 'INR' AS currency,
                
#                 -- BRAIN FIX: CARRY-FORWARD ROLLED OVER BALANCE
#                 -- Initial Saved Opening Balance + All Previous Receipts - All Previous Expenses
#                 (COALESCE(he.max_initial_balance, 0) + COALESCE(hr.past_receipts, 0) - COALESCE(he.past_expenses, 0)) AS opening_balance,
                
#                 -- THIS MONTH'S RECEIVED AMOUNT
#                 COALESCE(hr.current_receipts, 0) AS amount_transferred,
                
#                 -- TOTAL AMOUNT AVAILABLE FOR THIS MONTH
#                 ((COALESCE(he.max_initial_balance, 0) + COALESCE(hr.past_receipts, 0) - COALESCE(he.past_expenses, 0)) + COALESCE(hr.current_receipts, 0)) AS total_balance,
                
#                 CASE WHEN %(max_day)s >= 1 THEN COALESCE(e.expenditure_w1, 0) ELSE 0 END AS expenditure_w1,
#                 CASE WHEN %(max_day)s >= 8 THEN COALESCE(e.expenditure_w2, 0) ELSE 0 END AS expenditure_w2,
#                 CASE WHEN %(max_day)s >= 15 THEN COALESCE(e.expenditure_w3, 0) ELSE 0 END AS expenditure_w3,
#                 CASE WHEN %(max_day)s >= 22 THEN COALESCE(e.expenditure_w4, 0) ELSE 0 END AS expenditure_w4,
#                 CASE WHEN %(max_day)s >= 29 THEN COALESCE(e.expenditure_w5, 0) ELSE 0 END AS expenditure_w5
                
#             FROM `tabCreche` c
            
#             -- HISTORICAL & CURRENT RECEIPTS
#             LEFT JOIN (
#                 SELECT 
#                     creche_id,
#                     SUM(CASE WHEN date < %(start_date)s THEN COALESCE(amount, 0) ELSE 0 END) AS past_receipts,
#                     SUM(CASE WHEN YEAR(date) = %(year)s AND MONTH(date) = %(month)s THEN COALESCE(amount, 0) ELSE 0 END) AS current_receipts
#                 FROM `tabCashbook Receipt`
#                 GROUP BY creche_id
#             ) hr ON c.name = hr.creche_id
            
#             -- HISTORICAL EXPENSES & INITIAL SEED BALANCE
#             LEFT JOIN (
#                 SELECT 
#                     creche_id,
#                     MAX(opening_balance) AS max_initial_balance,
#                     SUM(CASE WHEN date < %(start_date)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS past_expenses
#                 FROM `tabCashbook`
#                 GROUP BY creche_id
#             ) he ON c.name = he.creche_id
            
#             -- CURRENT MONTH EXPENSES BY WEEK
#             LEFT JOIN (
#                 SELECT 
#                     creche_id,
#                     SUM(CASE WHEN DAY(date) BETWEEN 1 AND 7 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w1,
#                     SUM(CASE WHEN DAY(date) BETWEEN 8 AND 14 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w2,
#                     SUM(CASE WHEN DAY(date) BETWEEN 15 AND 21 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w3,
#                     SUM(CASE WHEN DAY(date) BETWEEN 22 AND 28 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w4,
#                     SUM(CASE WHEN DAY(date) >= 29 AND DAY(date) <= %(max_day)s THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w5
#                 FROM `tabCashbook`
#                 WHERE YEAR(date) = %(year)s AND MONTH(date) = %(month)s
#                 GROUP BY creche_id
#             ) e ON c.name = e.creche_id
            
#             LEFT JOIN `tabPartner` p ON c.partner_id = p.name
#             LEFT JOIN `tabState` s ON c.state_id = s.name
#             LEFT JOIN `tabDistrict` d ON c.district_id = d.name
#             LEFT JOIN `tabBlock` b ON c.block_id = b.name
#             LEFT JOIN `tabGram Panchayat` gp ON c.gp_id = gp.name
            
#             WHERE {where_clause} 
#               AND (
#                   hr.creche_id IS NOT NULL 
#                   OR he.creche_id IS NOT NULL 
#                   OR e.creche_id IS NOT NULL
#               )
#         ) AS base_data
        
#         ORDER BY creche_name
#     """.format(where_clause=where_clause)
    
#     return frappe.db.sql(sql_query, params, as_dict=True)






















# import frappe
# from frappe.utils import nowdate
# import calendar
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
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 120},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
    
#         {"label": "Opening Balance", "fieldname": "opening_balance", "fieldtype": "Currency", "options": "currency", "width": 180},
#         {"label": "Amount Transferred (This Month)", "fieldname": "amount_transferred", "fieldtype": "Currency", "options": "currency", "width": 260},
#         {"label": "Total Balance", "fieldname": "total_balance", "fieldtype": "Currency", "options": "currency", "width": 180},
        
#         {"label": "Expenditure (Week-1)", "fieldname": "expenditure_w1", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-1)", "fieldname": "balance_w1", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-2)", "fieldname": "expenditure_w2", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-2)", "fieldname": "balance_w2", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-3)", "fieldname": "expenditure_w3", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-3)", "fieldname": "balance_w3", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-4)", "fieldname": "expenditure_w4", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-4)", "fieldname": "balance_w4", "fieldtype": "Currency", "options": "currency", "width": 215},
        
#         {"label": "Expenditure (Week-5)", "fieldname": "expenditure_w5", "fieldtype": "Currency", "options": "currency", "width": 240},
#         {"label": "Balance (Week-5)", "fieldname": "balance_w5", "fieldtype": "Currency", "options": "currency", "width": 215},
#     ]

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     params = prepare_parameters(filters)
#     where_clause = build_where_clause(filters, params)
#     data = execute_main_query(params, where_clause)
#     return data

# def prepare_parameters(filters):
#     current_date = date.today()
#     month = int(filters.get("month", current_date.month))
#     year = int(filters.get("year", current_date.year))
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     if month == 1:
#         lmonth, plmonth = 12, 11
#         lyear, pyear = year - 1, year - 1
#     elif month == 2:
#         lmonth, plmonth = 1, 12
#         lyear, pyear = year, year - 1
#     else:
#         lmonth, plmonth = month - 1, month - 2
#         lyear, pyear = year, year
    
#     l2month = plmonth
#     l2year = pyear
#     if plmonth == 1:
#         l2month = 12
#         l2year = pyear - 1
#     else:
#         l2month = plmonth - 1
#         l2year = pyear
    
#     l3month = l2month
#     l3year = l2year
#     if l2month == 1:
#         l3month = 12
#         l3year = l2year - 1
#     else:
#         l3month = l2month - 1
#         l3year = l2year
    
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "lyear": lyear,
#         "lmonth": lmonth,
#         "plmonth": plmonth,
#         "pyear": pyear,
#         "l2month": l2month,
#         "l2year": l2year,
#         "l3month": l3month,
#         "l3year": l3year,
#         "cstart_date": None,
#         "cend_date": None,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#         "supervisor_id": None,
#         "creche_status_id": None,
#         "phases": None,
#         "creche_age": None,
#     }
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     params["partner"] = filters.get("partner") or current_user_partner
    
#     user_geo = frappe.db.sql("""
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
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
    
#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if cleaned:
#             params["phases"] = cleaned
#     if filters.get("creche_age"):
#         params["creche_age"] = filters.get("creche_age")
    
#     return params

# def build_where_clause(filters, params):
#     conditions = ["1=1"]
    
#     if params.get("partner"):
#         conditions.append("c.partner_id = %(partner)s")
#     if params.get("state"):
#         conditions.append("c.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#     if params.get("district"):
#         conditions.append("c.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#     if params.get("block"):
#         conditions.append("c.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#     if params.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#     if params.get("creche"):
#         conditions.append("c.name = %(creche)s")
#     if params.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if params.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
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
#     sql_query = """
#         SELECT 
#             p.partner_name AS partner,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             gp.gp_name AS gp,
#             c.creche_id AS creche_id,
#             c.creche_name AS creche_name,
#             -- Fixed Currency Field: Ensures the ₹ symbol shows instead of System Default (AED)
#             'INR' AS currency,
            
#             COALESCE(e.opening_balance, 0) AS opening_balance,
#             COALESCE(r.total_amount, 0) AS amount_transferred,
#             (COALESCE(e.opening_balance, 0) + COALESCE(r.total_amount, 0)) AS total_balance,
            
#             COALESCE(e.expenditure_w1, 0) AS expenditure_w1,
#             (COALESCE(e.opening_balance, 0) + COALESCE(r.total_amount, 0)) - COALESCE(e.expenditure_w1, 0) AS balance_w1,
            
#             COALESCE(e.expenditure_w2, 0) AS expenditure_w2,
#             (COALESCE(e.opening_balance, 0) + COALESCE(r.total_amount, 0)) - (COALESCE(e.expenditure_w1, 0) + COALESCE(e.expenditure_w2, 0)) AS balance_w2,
            
#             COALESCE(e.expenditure_w3, 0) AS expenditure_w3,
#             (COALESCE(e.opening_balance, 0) + COALESCE(r.total_amount, 0)) - (COALESCE(e.expenditure_w1, 0) + COALESCE(e.expenditure_w2, 0) + COALESCE(e.expenditure_w3, 0)) AS balance_w3,
            
#             COALESCE(e.expenditure_w4, 0) AS expenditure_w4,
#             (COALESCE(e.opening_balance, 0) + COALESCE(r.total_amount, 0)) - (COALESCE(e.expenditure_w1, 0) + COALESCE(e.expenditure_w2, 0) + COALESCE(e.expenditure_w3, 0) + COALESCE(e.expenditure_w4, 0)) AS balance_w4,
            
#             COALESCE(e.expenditure_w5, 0) AS expenditure_w5,
#             (COALESCE(e.opening_balance, 0) + COALESCE(r.total_amount, 0)) - (COALESCE(e.expenditure_w1, 0) + COALESCE(e.expenditure_w2, 0) + COALESCE(e.expenditure_w3, 0) + COALESCE(e.expenditure_w4, 0) + COALESCE(e.expenditure_w5, 0)) AS balance_w5
            
#         FROM `tabCreche` c
        
#         -- PRE-AGGREGATED RECEIPTS
#         LEFT JOIN (
#             SELECT 
#                 creche_id,
#                 SUM(amount) AS total_amount
#             FROM `tabCashbook Receipt`
#             WHERE YEAR(date) = %(year)s AND MONTH(date) = %(month)s
#             GROUP BY creche_id
#         ) r ON c.name = r.creche_id
        
#         -- PRE-AGGREGATED EXPENSES BY WEEK
#         LEFT JOIN (
#             SELECT 
#                 creche_id,
#                 MAX(opening_balance) AS opening_balance,
#                 SUM(CASE WHEN DAY(date) BETWEEN 1 AND 7 THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w1,
#                 SUM(CASE WHEN DAY(date) BETWEEN 8 AND 14 THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w2,
#                 SUM(CASE WHEN DAY(date) BETWEEN 15 AND 21 THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w3,
#                 SUM(CASE WHEN DAY(date) BETWEEN 22 AND 28 THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w4,
#                 SUM(CASE WHEN DAY(date) >= 29 THEN COALESCE(expense_amount, 0) ELSE 0 END) AS expenditure_w5
#             FROM `tabCashbook`
#             WHERE YEAR(date) = %(year)s AND MONTH(date) = %(month)s
#             GROUP BY creche_id
#         ) e ON c.name = e.creche_id
        
#         LEFT JOIN `tabPartner` p ON c.partner_id = p.name
#         LEFT JOIN `tabState` s ON c.state_id = s.name
#         LEFT JOIN `tabDistrict` d ON c.district_id = d.name
#         LEFT JOIN `tabBlock` b ON c.block_id = b.name
#         LEFT JOIN `tabGram Panchayat` gp ON c.gp_id = gp.name
        
#         WHERE {where_clause} 
#           AND (r.creche_id IS NOT NULL OR e.creche_id IS NOT NULL)
        
#         ORDER BY c.name
#     """.format(where_clause=where_clause)
#     return frappe.db.sql(sql_query, params, as_dict=True)









# import frappe
# from frappe.utils import nowdate
# import calendar
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
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
#         {"label": "Creche Name", "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
#         {"label": "Opening Balance", "fieldname": "opening_balance", "fieldtype": "Currency", "width": 180},
#         {"label": "Amount Transferred (This Month)", "fieldname": "amount_transferred", "fieldtype": "Currency", "width": 260},
#         {"label": "Total Balance", "fieldname": "total_balance", "fieldtype": "Currency", "width": 180},
        
#         {"label": "Expenditure (Week-1)", "fieldname": "expenditure_w1", "fieldtype": "Currency", "width": 240},
#         {"label": "Balance (Week-1)", "fieldname": "balance_w1", "fieldtype": "Currency", "width": 215},
        
#         {"label": "Expenditure (Week-2)", "fieldname": "expenditure_w2", "fieldtype": "Currency", "width": 240},
#         {"label": "Balance (Week-2)", "fieldname": "balance_w2", "fieldtype": "Currency", "width": 215},
        
#         {"label": "Expenditure (Week-3)", "fieldname": "expenditure_w3", "fieldtype": "Currency", "width": 240},
#         {"label": "Balance (Week-3)", "fieldname": "balance_w3", "fieldtype": "Currency", "width": 215 },
        
#         {"label": "Expenditure (Week-4)", "fieldname": "expenditure_w4", "fieldtype": "Currency", "width": 240},
#         {"label": "Balance (Week-4)", "fieldname": "balance_w4", "fieldtype": "Currency", "width": 215},
        
#         {"label": "Expenditure (Week-5)", "fieldname": "expenditure_w5", "fieldtype": "Currency", "width": 240},
#         {"label": "Balance (Week-5)", "fieldname": "balance_w5", "fieldtype": "Currency", "width": 215},
#     ]


# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     params = prepare_parameters(filters)
#     where_clause = build_where_clause(filters, params)
#     data = execute_main_query(params, where_clause)
#     return data


# def prepare_parameters(filters):
#     current_date = date.today()
#     month = int(filters.get("month", current_date.month))
#     year = int(filters.get("year", current_date.year))
    
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     if month == 1:
#         lmonth, plmonth = 12, 11
#         lyear, pyear = year - 1, year - 1
#     elif month == 2:
#         lmonth, plmonth = 1, 12
#         lyear, pyear = year, year - 1
#     else:
#         lmonth, plmonth = month - 1, month - 2
#         lyear, pyear = year, year
    
#     l2month = plmonth
#     l2year = pyear
#     if plmonth == 1:
#         l2month = 12
#         l2year = pyear - 1
#     else:
#         l2month = plmonth - 1
#         l2year = pyear
    
#     l3month = l2month
#     l3year = l2year
#     if l2month == 1:
#         l3month = 12
#         l3year = l2year - 1
#     else:
#         l3month = l2month - 1
#         l3year = l2year
    
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "lyear": lyear,
#         "lmonth": lmonth,
#         "plmonth": plmonth,
#         "pyear": pyear,
#         "l2month": l2month,
#         "l2year": l2year,
#         "l3month": l3month,
#         "l3year": l3year,
#         "cstart_date": None,
#         "cend_date": None,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#         "supervisor_id": None,
#         "creche_status_id": None,
#         "phases": None,
#         "creche_age": None,
#     }
    
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     params["partner"] = filters.get("partner") or current_user_partner
    
#     user_geo = frappe.db.sql("""
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
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
    
#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
#     if filters.get("phases"):
#         cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if cleaned:
#             params["phases"] = cleaned
#     if filters.get("creche_age"):
#         params["creche_age"] = filters.get("creche_age")
    
#     return params


# def build_where_clause(filters, params):
#     conditions = ["1=1"]
    
#     if params.get("partner"):
#         conditions.append("cr.partner_id = %(partner)s")
#     if params.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#     elif params.get("state_ids"):
#         conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
#     if params.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#     elif params.get("district_ids"):
#         conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
#     if params.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#     elif params.get("block_ids"):
#         conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
#     if params.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#     elif params.get("gp_ids"):
#         conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
#     if params.get("creche"):
#         conditions.append("cr.name = %(creche)s")
#     if params.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#     if params.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):
#         conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")
#     if params.get("creche_age"):
#         conditions.append("""
#             CASE
#                 WHEN cr.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
    
#     return " AND ".join(conditions)


# def execute_main_query(params, where_clause):
#     sql_query = """
#         SELECT 
#             p.partner_name AS partner,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             c.creche_id AS creche_id,
#             c.creche_name AS creche_name,
#             cb.opening_balance AS opening_balance,
#             cr.amount AS amount_transferred,
#             (COALESCE(cb.opening_balance, 0) + COALESCE(cr.amount, 0)) AS total_balance,
            
#             -- WEEK 1 (Days 1 to 7)
#             SUM(CASE WHEN DAY(cb.date) BETWEEN 1 AND 7 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS expenditure_w1,
#             (COALESCE(cb.opening_balance, 0) + COALESCE(cr.amount, 0)) - 
#                 SUM(CASE WHEN DAY(cb.date) BETWEEN 1 AND 7 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS balance_w1,

#             -- WEEK 2 (Days 8 to 14)
#             SUM(CASE WHEN DAY(cb.date) BETWEEN 8 AND 14 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS expenditure_w2,
#             (COALESCE(cb.opening_balance, 0) + COALESCE(cr.amount, 0)) - 
#                 SUM(CASE WHEN DAY(cb.date) BETWEEN 1 AND 14 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS balance_w2,

#             -- WEEK 3 (Days 15 to 21)
#             SUM(CASE WHEN DAY(cb.date) BETWEEN 15 AND 21 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS expenditure_w3,
#             (COALESCE(cb.opening_balance, 0) + COALESCE(cr.amount, 0)) - 
#                 SUM(CASE WHEN DAY(cb.date) BETWEEN 1 AND 21 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS balance_w3,

#             -- WEEK 4 (Days 22 to 28)
#             SUM(CASE WHEN DAY(cb.date) BETWEEN 22 AND 28 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS expenditure_w4,
#             (COALESCE(cb.opening_balance, 0) + COALESCE(cr.amount, 0)) - 
#                 SUM(CASE WHEN DAY(cb.date) BETWEEN 1 AND 28 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS balance_w4,

#             -- WEEK 5 (Days 29+)
#             SUM(CASE WHEN DAY(cb.date) >= 29 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS expenditure_w5,
#             (COALESCE(cb.opening_balance, 0) + COALESCE(cr.amount, 0)) - 
#                 SUM(CASE WHEN DAY(cb.date) >= 1 THEN COALESCE(cb.expense_amount, 0) ELSE 0 END) AS balance_w5

#         FROM `tabCashbook Receipt` cr
#         LEFT JOIN `tabCashbook` cb ON cb.cashbook_guid = cr.cashbook_receipt_guid 
#         LEFT JOIN `tabPartner` p ON cr.partner_id = p.name
#         LEFT JOIN `tabState` s ON cr.state_id = s.name
#         LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
#         LEFT JOIN `tabBlock` b ON cr.block_id = b.name
#         LEFT JOIN `tabGram Panchayat` gp ON cr.gp_id = gp.name
#         LEFT JOIN `tabCreche` c ON cr.creche_id = c.name
#         WHERE 
#             {where_clause}
#         GROUP BY p.partner_name, s.state_name,d.district_name, b.block_name, c.creche_id, c.creche_name, cb.opening_balance, cr.amount
#     """.format(where_clause=where_clause)
#     return frappe.db.sql(sql_query, params, as_dict=True)