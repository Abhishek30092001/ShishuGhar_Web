import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    columns = get_columns()
    data = get_report_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Link", "options": "Partner", "width": 180},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
        {"label": "Village", "fieldname": "village", "fieldtype": "Data", "width": 180},
        {"label": "Creche Name", "fieldname": "creche", "fieldtype": "Data", "width": 180},
        {"label": "Creche", "fieldname": "creche_idx", "fieldtype": "Data", "width": 150},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Data", "width": 150},
        {"label": "Date", "fieldname": "date", "fieldtype": "date", "width": 150}
    ]

def get_report_data(filters):
    current_date = date.today()
    month = int(filters.get("month") or current_date.month)
    year = int(filters.get("year") or current_date.year)
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    if month == 1:
        lmonth, plmonth, lyear, pyear = 12, 11, year - 1, year - 1
    elif month == 2:
        lmonth, plmonth, lyear, pyear = 1, 12, year, year - 1
    else:
        lmonth, plmonth, lyear, pyear = month - 1, month - 2, year, year

    params = {
        "start_date": start_date, "end_date": end_date,
        "year": year, "month": month, "lyear": lyear, "lmonth": lmonth,
        "plmonth": plmonth, "pyear": pyear,
        "partner": None, "state": None, "district": None, "block": None, "gp": None, "creche": None,
        "state_ids": None, "district_ids": None, "block_ids": None, "gp_ids": None
    }

    conditions = ["1=1"]

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    state_ids = ",".join([str(s["state_id"]) for s in current_user_state if s.get("state_id")])
    district_ids = ",".join([str(s["district_id"]) for s in current_user_state if s.get("district_id")])
    block_ids = ",".join([str(s["block_id"]) for s in current_user_state if s.get("block_id")])
    gp_ids = ",".join([str(s["gp_id"]) for s in current_user_state if s.get("gp_id")])

    if partner_id:
        conditions.append("cr.partner_id = %(partner)s")
        params["partner"] = partner_id

    if filters.get("state"):
        conditions.append("cr.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")
        params["state_ids"] = state_ids

    if filters.get("district"):
        conditions.append("cr.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids:
        conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")
        params["district_ids"] = district_ids

    if filters.get("block"):
        conditions.append("cr.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids:
        conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")
        params["block_ids"] = block_ids

    if filters.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids:
        conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")
        params["gp_ids"] = gp_ids

    if filters.get("creche"):
        conditions.append("cr.name = %(creche)s")
        params["creche"] = filters.get("creche")

    if filters.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")

    if filters.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            cr.partner_id AS partner,
            cr.state_id AS state,
            cr.district_id AS district,
            cr.block_id AS block,
            cr.gp_id AS gp,
            cr.village_id AS village,
            cr.creche_name AS creche,
            cr.name AS creche_idx,
            cr.creche_id AS creche_id
        FROM `tabCreche` AS cr
        WHERE {where_clause}
    """
    return frappe.db.sql(query, params, as_dict=True)
