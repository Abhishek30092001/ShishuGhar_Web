import frappe
from frappe import _
from datetime import date


def execute(filters=None):
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
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})

    fixed_columns = [
        {"label": "No of Creches", "fieldname": "no_of_creches", "fieldtype": "Data", "width": 150},
        {"label": "Supplied Fuel Source", "fieldname": "supplied_fuel_source", "fieldtype": "Data", "width": 180},
        {"label": "If LPG, What Type?", "fieldname": "if_lpg_what_type", "fieldtype": "Data", "width": 240},
        {"label": "Current Source of Fuel", "fieldname": "current_source_of_fuel", "fieldtype": "Data", "width": 240},
        {"label": "If Alternative then what is the Source", "fieldname": "alternative_source", "fieldtype": "Data", "width": 280},
        {"label": "No of Creches Running on Alternative Fuel", "fieldname": "alt_fuel_creches", "fieldtype": "Data", "width": 280},
        {"label": "Available Fuel for Month (0-1 Month)", "fieldname": "fuel_0_1_month", "fieldtype": "Data", "width": 240},
        {"label": "Available Fuel for Month (1-2 Months)", "fieldname": "fuel_1_2_month", "fieldtype": "Data", "width": 280},
        {"label": "Available Fuel for Month (2-3 Months)", "fieldname": "fuel_2_3_month", "fieldtype": "Data", "width": 280},
        {"label": "Available Fuel for Month (3+ Months)", "fieldname": "fuel_3_plus_month", "fieldtype": "Data", "width": 280},
    ]

    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
    return columns, data


def get_report_data(filters):
    current_date = date.today()

    conditions = ["c.creche_status_id = 3"]
    params = {
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
        "today": current_date,
    }

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
    state_ids    = ",".join(str(s["state_id"])    for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids    = ",".join(str(s["block_id"])    for s in current_user_state if s.get("block_id"))
    gp_ids       = ",".join(str(s["gp_id"])       for s in current_user_state if s.get("gp_id"))

    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        params["partner"] = partner_id
    if filters.get("state"):
        conditions.append("c.state_id = %(state)s")
        params["state"] = filters.get("state")
        params["state_ids"] = None
    else:
        if state_ids:
            conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
            params["state_ids"] = state_ids
            params["state"] = None

    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        params["district"] = filters.get("district")
        params["district_ids"] = None
    else:
        if district_ids:
            conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
            params["district_ids"] = district_ids
            params["district"] = None

    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        params["block"] = filters.get("block")
        params["block_ids"] = None
    else:
        if block_ids:
            conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
            params["block_ids"] = block_ids
            params["block"] = None

    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
        params["gp_ids"] = None
    else:
        if gp_ids:
            conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
            params["gp_ids"] = gp_ids
            params["gp"] = None

    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
        params["creche"] = filters.get("creche")
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")

    level_mapping = {
        "1": ["tf.partner"],
        "2": ["tf.state"],
        "3": ["tf.state", "tf.district"],
        "4": ["tf.state", "tf.district", "tf.block"],
        "5": ["tf.state", "tf.district", "tf.block", "tf.supervisor"],
        "6": ["tf.state", "tf.district", "tf.block", "tf.gp"],
        "7": ["tf.state", "tf.district", "tf.block", "tf.gp", "tf.supervisor", "tf.creche", "tf.creche_id"],
    }

    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field  = ", ".join(group_by_fields)

    select_fields = [
        "tf.partner AS partner",
        "tf.state AS state",
        "tf.district AS district",
        "tf.block AS block",
        "tf.supervisor AS supervisor",
        "tf.gp AS gp",
        "tf.creche AS creche",
        "tf.creche_id AS creche_id",
    ]
    selected_fields = []
    for field in select_fields:
        alias = field.split(" AS ")[0].split(".")[1]
        if any(alias in gbf for gbf in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT
        {", ".join(selected_fields)},
        COUNT(DISTINCT tf.creche_id_raw) AS no_of_creches,
        tf.supplied_fuel_source AS supplied_fuel_source,
        tf.if_lpg_what_type AS if_lpg_what_type,
        tf.current_source_of_fuel AS current_source_of_fuel,
        tf.alternative_source AS alternative_source,
        COUNT(DISTINCT CASE WHEN tf.has_alternative = 1 THEN tf.creche_id_raw END) AS alt_fuel_creches,

        -- Available Fuel: only for LPG-supplied creches not on alternative fuel
        COUNT(DISTINCT CASE
            WHEN tf.supplied_fuel_source = 'LPG'
             AND tf.has_alternative = 0
             AND DATEDIFF(%(today)s, tf.date_of_supply) BETWEEN 0 AND 30
            THEN tf.creche_id_raw
        END) AS fuel_0_1_month,

        COUNT(DISTINCT CASE
            WHEN tf.supplied_fuel_source = 'LPG'
             AND tf.has_alternative = 0
             AND DATEDIFF(%(today)s, tf.date_of_supply) BETWEEN 31 AND 60
            THEN tf.creche_id_raw
        END) AS fuel_1_2_month,

        COUNT(DISTINCT CASE
            WHEN tf.supplied_fuel_source = 'LPG'
             AND tf.has_alternative = 0
             AND DATEDIFF(%(today)s, tf.date_of_supply) BETWEEN 61 AND 90
            THEN tf.creche_id_raw
        END) AS fuel_2_3_month,

        COUNT(DISTINCT CASE
            WHEN tf.supplied_fuel_source = 'LPG'
             AND tf.has_alternative = 0
             AND DATEDIFF(%(today)s, tf.date_of_supply) > 90
            THEN tf.creche_id_raw
        END) AS fuel_3_plus_month

    FROM (
        SELECT
            p.partner_name                  AS partner,
            s.state_name                    AS state,
            d.district_name                 AS district,
            b.block_name                    AS block,
            gp.gp_name                      AS gp,
            u.full_name                     AS supervisor,
            c.creche_name                   AS creche,
            c.creche_id                     AS creche_id,
            c.name                          AS creche_id_raw,
            l.supplied_fuel_source          AS supplied_fuel_source,
            l.if_lpg_what_type              AS if_lpg_what_type,
            l.current_source_of_fuel        AS current_source_of_fuel,
            l.other                         AS alternative_source,
            l.date_of_supply                AS date_of_supply,
            CASE
                WHEN l.current_source_of_fuel IS NOT NULL
                 AND l.current_source_of_fuel != ''
                 AND l.current_source_of_fuel != l.supplied_fuel_source
                THEN 1
                ELSE 0
            END                             AS has_alternative

        FROM `tabLPG` AS l
        LEFT JOIN `tabCreche` AS c ON l.creche_id = c.name
        LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
        LEFT JOIN `tabPartner` AS p ON p.name = c.partner_id
        LEFT JOIN `tabState` AS s ON s.name = c.state_id
        LEFT JOIN `tabDistrict` AS d ON d.name = c.district_id
        LEFT JOIN `tabBlock` AS b ON b.name = c.block_id
        LEFT JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id
        WHERE {where_clause}
    ) AS tf

    GROUP BY
        {group_by_field},
        tf.supplied_fuel_source,
        tf.if_lpg_what_type,
        tf.current_source_of_fuel,
        tf.alternative_source

    ORDER BY {group_by_field}
    """

    data = frappe.db.sql(query, params, as_dict=True)

    # Totals row
    total_creches       = sum(int(row.get("no_of_creches", 0) or 0) for row in data)
    total_alt_creches   = sum(int(row.get("alt_fuel_creches", 0) or 0) for row in data)
    total_fuel_0_1      = sum(int(row.get("fuel_0_1_month", 0) or 0) for row in data)
    total_fuel_1_2      = sum(int(row.get("fuel_1_2_month", 0) or 0) for row in data)
    total_fuel_2_3      = sum(int(row.get("fuel_2_3_month", 0) or 0) for row in data)
    total_fuel_3_plus   = sum(int(row.get("fuel_3_plus_month", 0) or 0) for row in data)

    total_row = {
        "partner":               "<b style='color:black;'>Total</b>",
        "state":                 "<b style='color:black;'>Total</b>",
        "no_of_creches":         f"<b>{total_creches}</b>",
        "supplied_fuel_source":  "",
        "if_lpg_what_type":      "",
        "current_source_of_fuel": "",
        "alternative_source":    "",
        "alt_fuel_creches":      f"<b>{total_alt_creches}</b>",
        "fuel_0_1_month":        f"<b>{total_fuel_0_1}</b>",
        "fuel_1_2_month":        f"<b>{total_fuel_1_2}</b>",
        "fuel_2_3_month":        f"<b>{total_fuel_2_3}</b>",
        "fuel_3_plus_month":     f"<b>{total_fuel_3_plus}</b>",
    }

    data.append(total_row)
    return data


@frappe.whitelist()
def get_alternative_fuel_details(partner="", state="", district="", block="", gp="", supervisor="", creche_id=""):
    conditions = [
        "c.creche_status_id = 3",
        "l.current_source_of_fuel IS NOT NULL",
        "l.current_source_of_fuel != ''",
        "l.current_source_of_fuel != l.supplied_fuel_source",
    ]
    params = {}

    if creche_id:
        conditions.append("c.creche_id = %(creche_id)s")
        params["creche_id"] = creche_id
    else:
        if partner and "<b>" not in partner:
            conditions.append("p.partner_name = %(partner)s")
            params["partner"] = partner
        if state and "<b>" not in state:
            conditions.append("s.state_name = %(state)s")
            params["state"] = state
        if district and "<b>" not in district:
            conditions.append("d.district_name = %(district)s")
            params["district"] = district
        if block and "<b>" not in block:
            conditions.append("b.block_name = %(block)s")
            params["block"] = block
        if gp and "<b>" not in gp:
            conditions.append("gp.gp_name = %(gp)s")
            params["gp"] = gp
        if supervisor and "<b>" not in supervisor:
            conditions.append("u.full_name = %(supervisor)s")
            params["supervisor"] = supervisor

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            c.creche_name               AS creche,
            c.creche_id                 AS creche_id,
            l.supplied_fuel_source      AS supplied_fuel_source,
            l.current_source_of_fuel    AS current_source_of_fuel,
            l.other                     AS alternative_source,
            l.date_of_supply            AS date_of_supply
        FROM `tabLPG` AS l
        LEFT JOIN `tabCreche` AS c ON l.creche_id = c.name
        LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
        LEFT JOIN `tabPartner` AS p ON p.name = c.partner_id
        LEFT JOIN `tabState` AS s ON s.name = c.state_id
        LEFT JOIN `tabDistrict` AS d ON d.name = c.district_id
        LEFT JOIN `tabBlock` AS b ON b.name = c.block_id
        LEFT JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id
        WHERE {where_clause}
        ORDER BY c.creche_name
    """

    return frappe.db.sql(query, params, as_dict=True)
