import frappe
from datetime import date
import calendar


def execute(filters=None):
    columns = get_columns()
    data = get_report_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Creche Name", "fieldname": "creche", "fieldtype": "Data", "width": 200},
        {"label": "Creche", "fieldname": "creche_idx", "fieldtype": "Data", "width": 150},
        {"label": "Supplied Fuel Source", "fieldname": "supplied_fuel_source", "fieldtype": "Data", "width": 180},
        {"label": "If LPG, What Type?", "fieldname": "if_lpg_what_type", "fieldtype": "Data", "width": 180},
        {"label": "Current Source of Fuel", "fieldname": "current_source_of_fuel", "fieldtype": "Data", "width": 180},
        {"label": "Other", "fieldname": "other", "fieldtype": "Data", "width": 180},
        {"label": "Date of Supply", "fieldname": "date_of_supply", "fieldtype": "Date", "width": 150},
    ]


def get_report_data(filters):
    current_date = date.today()

    month = int(filters.get("month") or current_date.month)
    year = int(filters.get("year") or current_date.year)

    start_date = date(year, month, 1)
    end_date = date(year, month, calendar.monthrange(year, month)[1])

    params = {
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
        "supervisor_id": None,
        "creche_status_id": None,
        "state_ids": None,
        "district_ids": None,
        "block_ids": None,
        "gp_ids": None,
    }

    conditions = ["1=1"]

    current_user_partner = frappe.db.get_value(
        "User", frappe.session.user, "partner"
    )

    partner_id = filters.get("partner") or current_user_partner

    geography = frappe.db.sql(
        """
        SELECT
            state_id,
            district_id,
            block_id,
            gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        """,
        (frappe.session.user,),
        as_dict=True,
    )

    state_ids = ",".join(
        [row.state_id for row in geography if row.get("state_id")]
    )
    district_ids = ",".join(
        [row.district_id for row in geography if row.get("district_id")]
    )
    block_ids = ",".join(
        [row.block_id for row in geography if row.get("block_id")]
    )
    gp_ids = ",".join(
        [row.gp_id for row in geography if row.get("gp_id")]
    )

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
            cr.creche_name AS creche,
            cr.name AS creche_idx,

            '' AS supplied_fuel_source,
            '' AS if_lpg_what_type,
            '' AS current_source_of_fuel,
            '' AS other,
            NULL AS date_of_supply

        FROM `tabCreche` cr

        WHERE {where_clause}

        ORDER BY cr.creche_name
    """

    return frappe.db.sql(query, params, as_dict=True)