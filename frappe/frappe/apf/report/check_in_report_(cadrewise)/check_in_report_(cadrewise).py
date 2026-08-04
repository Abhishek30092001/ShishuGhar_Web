import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate
import calendar
from datetime import datetime, timedelta, date


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters=None):
    selected_level = filters.get("level", "7")
    variable_columns = []

    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 160})
    if selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
    if selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
    if selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
    if selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
    if selected_level == "7":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
        variable_columns.append({"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
        
    fixed_columns = [
        {"label": _("No. of Creches"), "fieldname": "no_of_creches", "fieldtype": "Data", "width": 180},
        {"label": _("No. of Checkins by Supervisor"), "fieldname": "sup_checkins", "fieldtype": "Data", "width": 250},
        {"label": _("No. of Checkins by CC"), "fieldname": "cc_checkins", "fieldtype": "Data", "width": 250},
        {"label": _("No. of Checkins by CBC"), "fieldname": "cbm_checkins", "fieldtype": "Data", "width": 250},
        {"label": _("No. of Checkins by ALC"), "fieldname": "alm_checkins", "fieldtype": "Data", "width": 250},
        {"label": _("No. of Checkins by MIS"), "fieldname": "mis_checkins", "fieldtype": "Data", "width": 290},
        {"label": _("No. of Checkins by Safety Coordinator"), "fieldname": "safety_checkins", "fieldtype": "Data", "width": 290},

        {"label": _("Avg. Checkins per creche by Supervisor"), "fieldname": "avg_sup", "fieldtype": "float", "width": 300},
        {"label": _("Avg. Checkins per creche by CC"), "fieldname": "avg_cc", "fieldtype": "float", "width": 250},
        {"label": _("Avg. Checkins per creche by CBC"), "fieldname": "avg_cbm", "fieldtype": "float", "width": 250},
        {"label": _("Avg. Checkins per creche by ALC"), "fieldname": "avg_alm", "fieldtype": "float", "width": 250},
        {"label": _("Avg. Checkins per creche by MIS"), "fieldname": "avg_mis", "fieldtype": "float", "width": 250},
        {"label": _("Avg. Checkins per creche by Safety Coordinator"), "fieldname": "avg_safety", "fieldtype": "float", "width": 300},
    ]

    columns = variable_columns + fixed_columns
    return columns


def get_data(filters):
    conditions = get_conditions(filters)
    level_mapping = {
        "1": ["partner.partner_name"],
        "2": ["state.state_name"],
        "3": ["state.state_name", "district.district_name"],
        "4": ["state.state_name", "district.district_name", "block.block_name"],
        "5": ["state.state_name", "district.district_name", "block.block_name", "usr.full_name"],
        "6": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name"],
        "7": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name", "creche.creche_name", "creche.creche_id","usr.full_name"]
    }
    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "partner.partner_name AS partner", 
        "state.state_name AS state", 
        "district.district_name AS district", 
        "block.block_name AS block",
        "gp.gp_name AS gp", 
        "usr.full_name AS supervisor", 
        "creche.creche_name AS creche_name", 
        "creche.creche_id AS creche_id", 
    ]
    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

    # date range logic starts here
    start_date, end_date = None, None

    if(filters.get("time_range")):
        time_range = filters.get("time_range") if filters else None
        start_date, end_date = (time_range if time_range else (None, None))
    
    elif(filters.get("year") and filters.get("month")):
        current_date = date.today()
        month = int(filters.get("month")) if filters.get("month") else current_date.month
        year = int(filters.get("year")) if filters.get("year") else current_date.year
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)    

    query = f"""
        SELECT 
            {",".join(selected_fields)},
            SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) AS sup_checkins,
            SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) AS cc_checkins,
            SUM(CASE WHEN tu.type = 'Capacity and Building Manager' THEN 1 ELSE 0 END) AS cbm_checkins,
            SUM(CASE WHEN tu.type = 'Accounts and Logistics Manager' THEN 1 ELSE 0 END) AS alm_checkins,
            SUM(CASE WHEN tu.type = 'Safety Coordinator' THEN 1 ELSE 0 END) AS safety_checkins,
            SUM(CASE WHEN tu.type IN ('MIS Manager', 'Partner Administrator') THEN 1 ELSE 0 END) AS mis_checkins,
            DATE_FORMAT(creche.creche_opening_date, '%d-%m-%Y') AS creche_opening_date,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_sup,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_cc,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Capacity and Building Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_cbm,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Accounts and Logistics Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_alm,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'Safety Coordinator' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_safety,

            ROUND(
                CASE 
                    WHEN COUNT(creche.name) > 0 
                    THEN SUM(CASE WHEN tu.type = 'MIS Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
                    ELSE 0 
                END, 1
            ) AS avg_mis,

            COUNT(DISTINCT creche.name) AS no_of_creches
        FROM 
            `tabCreche` creche
        JOIN 
            `tabPartner` partner ON creche.partner_id = partner.name
        JOIN 
            `tabState` state ON creche.state_id = state.name
        JOIN 
            `tabDistrict` district ON creche.district_id = district.name
        JOIN 
            `tabBlock` block ON creche.block_id = block.name
        JOIN 
            `tabGram Panchayat` gp ON creche.gp_id = gp.name   
        JOIN 
            `tabUser` usr ON usr.name = creche.supervisor_id      
        LEFT JOIN 
            `tabCreche Check In` checkin ON creche.name = checkin.creche_id
            AND checkin.date_of_checkin BETWEEN '{start_date}' AND '{end_date}'
        LEFT JOIN 
            `tabUser` tu ON checkin.appcreated_by = tu.name 
        WHERE 
            {conditions}
            AND (creche.creche_opening_date IS NULL OR ( '{end_date}' IS NOT NULL AND creche.creche_opening_date <= '{end_date}' ))
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}
    """

    data = frappe.db.sql(query, as_dict=True)

    total_creches = int(sum(row.get('no_of_creches', 0) for row in data))
    total_sup_checkins = int(sum(row.get('sup_checkins', 0) for row in data))
    total_cc_checkins = int(sum(row.get('cc_checkins', 0) for row in data))
    total_cbm_checkins = int(sum(row.get('cbm_checkins', 0) for row in data))
    total_alm_checkins = int(sum(row.get('alm_checkins', 0) for row in data))
    total_safety_checkins = int(sum(row.get('safety_checkins', 0) for row in data))
    total_mis_checkins = int(sum(row.get('mis_checkins', 0) for row in data))

    avg_sup = round((total_sup_checkins/ total_creches), 1) if total_creches else 0
    avg_cc = round((total_cc_checkins/ total_creches), 1) if total_creches else 0
    avg_cbm = round((total_cbm_checkins/ total_creches), 1) if total_creches else 0
    avg_alm = round((total_alm_checkins/ total_creches), 1) if total_creches else 0
    avg_safety = round((total_safety_checkins/ total_creches), 1) if total_creches else 0
    avg_mis = round((total_mis_checkins/ total_creches), 1) if total_creches else 0

    total_row = {
        "partner": "<b style='color:black;'>Total</b>",
        "state": "<b style='color:black;'>Total</b>",
        "no_of_creches": f"<b>{total_creches}</b>",
        "sup_checkins": f"<b>{total_sup_checkins}</b>",
        "cc_checkins": f"<b>{total_cc_checkins}</b>",
        "cbm_checkins": f"<b>{total_cbm_checkins}</b>",
        "alm_checkins": f"<b>{total_alm_checkins}</b>",
        "safety_checkins": f"<b>{total_safety_checkins}</b>",
        "mis_checkins": f"<b>{total_mis_checkins}</b>",
        "avg_sup": f"<b>{avg_sup}</b>",
        "avg_cc": f"<b>{avg_cc}</b>",
        "avg_cbm": f"<b>{avg_cbm}</b>",
        "avg_alm": f"<b>{avg_alm}</b>",
        "avg_safety": f"<b>{avg_safety}</b>",
        "avg_mis": f"<b>{avg_mis}</b>"
    }

    data.append(total_row)

    return data


def get_conditions(filters):
    conditions = "1 = 1"
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

    partner = frappe.db.get_value("User", frappe.session.user, "partner")
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """

    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    creche_status_id = filters.get("creche_status_id") if filters else None
    phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
    state_id = None

    if filters.get('partner'):
        partner = filters.get('partner')
    if partner:
        conditions += f" AND partner.name = '{partner}'"
    if filters.get("partner"):
        conditions += f" AND partner.name = '{filters.get('partner')}'"

    if filters.get("state"):
        state = filters.get("state")
        conditions += f" AND state.name = '{state}'"
    elif state_ids:
        conditions += f" AND FIND_IN_SET(state.name, '{state_ids}')"

    if filters.get("district"):
        district = filters.get("district")
        conditions += f" AND district.name = '{district}'"
    elif district_ids:
        conditions += f" AND FIND_IN_SET(district.name, '{district_ids}')"
    if filters.get("block"):
        block = filters.get("block")
        conditions += f" AND block.name = '{block}'"
    elif block_ids:
        conditions += f" AND FIND_IN_SET(block.name, '{block_ids}')"
    if filters.get("gp"):
        gp = filters.get("gp")
        conditions += f" AND gp.name = '{gp}'"
    elif gp_ids:
        conditions += f" AND FIND_IN_SET(gp.name, '{gp_ids}')"
    if filters.get("creche"):
        conditions += f" AND creche.name = '{filters.get('creche')}'"
    if filters.get("supervisor_id"):
        conditions += f" AND creche.supervisor_id = '{filters.get('supervisor_id')}'"
    if cstart_date and cend_date:
        conditions += f" AND creche.creche_opening_date BETWEEN {frappe.db.escape(cstart_date)} AND {frappe.db.escape(cend_date)}"
    if filters.get("creche_status_id"):
        conditions += f" AND creche.creche_status_id = '{creche_status_id}'"
    if phases_cleaned:
        conditions += f" AND FIND_IN_SET(creche.phase, {frappe.db.escape(phases_cleaned)})"
    
    creche_age = filters.get("creche_age", "")
    if creche_age:
        conditions += f"""
            AND CASE
                WHEN creche.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, creche.creche_opening_date, CURDATE()) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, creche.creche_opening_date, CURDATE()) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, creche.creche_opening_date, CURDATE()) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, creche.creche_opening_date, CURDATE()) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, creche.creche_opening_date, CURDATE()) >= 24 THEN '24+ Month'
                ELSE ''
            END = '{creche_age}'
        """

    return conditions








#backup before age of Creche Filter
# import frappe
# from frappe import _
# from frappe.utils import flt, getdate, nowdate
# import calendar
# from datetime import datetime, timedelta, date


# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data


# def get_columns(filters=None):
#     selected_level = filters.get("level", "7")
#     variable_columns = []

#     if selected_level == "1":
#         variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 160})
#     if selected_level == "2":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#     if selected_level == "3":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#     if selected_level == "4":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#     if selected_level == "5":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
#     if selected_level == "6":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
#     if selected_level == "7":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
        
#     fixed_columns = [
#         {"label": _("No. of Creches"), "fieldname": "no_of_creches", "fieldtype": "Data", "width": 180},
#         {"label": _("No. of Checkins by Supervisor"), "fieldname": "sup_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by CC"), "fieldname": "cc_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by CBC"), "fieldname": "cbm_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by ALC"), "fieldname": "alm_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by MIS"), "fieldname": "mis_checkins", "fieldtype": "Data", "width": 290},
#         {"label": _("No. of Checkins by Safety Coordinator"), "fieldname": "safety_checkins", "fieldtype": "Data", "width": 290},

#         {"label": _("Avg. Checkins per creche by Supervisor"), "fieldname": "avg_sup", "fieldtype": "float", "width": 300},
#         {"label": _("Avg. Checkins per creche by CC"), "fieldname": "avg_cc", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by CBC"), "fieldname": "avg_cbm", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by ALC"), "fieldname": "avg_alm", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by MIS"), "fieldname": "avg_mis", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by Safety Coordinator"), "fieldname": "avg_safety", "fieldtype": "float", "width": 300},
#     ]

#     columns = variable_columns + fixed_columns
#     return columns


# def get_data(filters):
#     conditions = get_conditions(filters)
#     level_mapping = {
#         "1": ["partner.partner_name"],
#         "2": ["state.state_name"],
#         "3": ["state.state_name", "district.district_name"],
#         "4": ["state.state_name", "district.district_name", "block.block_name"],
#         "5": ["state.state_name", "district.district_name", "block.block_name", "usr.full_name"],
#         "6": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name"],
#         "7": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name", "creche.creche_name", "creche.creche_id","usr.full_name"]
#     }
#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)

#     select_fields = [
#         "partner.partner_name AS partner", 
#         "state.state_name AS state", 
#         "district.district_name AS district", 
#         "block.block_name AS block",
#         "gp.gp_name AS gp", 
#         "usr.full_name AS supervisor", 
#         "creche.creche_name AS creche_name", 
#         "creche.creche_id AS creche_id", 
#     ]
#     selected_fields = []
#     for field in select_fields:
#         if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
#             selected_fields.append(field)

#     # date range logic starts here
#     start_date, end_date = None, None

#     if(filters.get("time_range")):
#         time_range = filters.get("time_range") if filters else None
#         start_date, end_date = (time_range if time_range else (None, None))
    
#     elif(filters.get("year") and filters.get("month")):
#         current_date = date.today()
#         month = int(filters.get("month")) if filters.get("month") else current_date.month
#         year = int(filters.get("year")) if filters.get("year") else current_date.year
#         start_date = date(year, month, 1)
#         last_day = calendar.monthrange(year, month)[1]
#         end_date = date(year, month, last_day)    

#     query = f"""
#         SELECT 
#             {",".join(selected_fields)},
#             SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) AS sup_checkins,
#             SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) AS cc_checkins,
#             SUM(CASE WHEN tu.type = 'Capacity and Building Manager' THEN 1 ELSE 0 END) AS cbm_checkins,
#             SUM(CASE WHEN tu.type = 'Accounts and Logistics Manager' THEN 1 ELSE 0 END) AS alm_checkins,
#             SUM(CASE WHEN tu.type = 'Safety Coordinator' THEN 1 ELSE 0 END) AS safety_checkins,
#             SUM(CASE WHEN tu.type = 'MIS Manager' THEN 1 ELSE 0 END) AS mis_checkins,
#             DATE_FORMAT(creche.creche_opening_date, '%d-%m-%Y') AS creche_opening_date,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_sup,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_cc,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Capacity and Building Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_cbm,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Accounts and Logistics Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_alm,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Safety Coordinator' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_safety,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'MIS Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_mis,

#             COUNT(DISTINCT creche.name) AS no_of_creches
#         FROM 
#             `tabCreche` creche
#         JOIN 
#             `tabPartner` partner ON creche.partner_id = partner.name
#         JOIN 
#             `tabState` state ON creche.state_id = state.name
#         JOIN 
#             `tabDistrict` district ON creche.district_id = district.name
#         JOIN 
#             `tabBlock` block ON creche.block_id = block.name
#         JOIN 
#             `tabGram Panchayat` gp ON creche.gp_id = gp.name   
#         JOIN 
#             `tabUser` usr ON usr.name = creche.supervisor_id      
#         LEFT JOIN 
#             `tabCreche Check In` checkin ON creche.name = checkin.creche_id
#             AND checkin.date_of_checkin BETWEEN '{start_date}' AND '{end_date}'
#         LEFT JOIN 
#             `tabUser` tu ON checkin.appcreated_by = tu.name 
#         WHERE 
#             {conditions}
#             AND (creche.creche_opening_date IS NULL OR ( '{end_date}' IS NOT NULL AND creche.creche_opening_date <= '{end_date}' ))
#         GROUP BY {group_by_field}
#         ORDER BY {group_by_field}
#     """

#     data = frappe.db.sql(query, as_dict=True)

#     total_creches = int(sum(row.get('no_of_creches', 0) for row in data))
#     total_sup_checkins = int(sum(row.get('sup_checkins', 0) for row in data))
#     total_cc_checkins = int(sum(row.get('cc_checkins', 0) for row in data))
#     total_cbm_checkins = int(sum(row.get('cbm_checkins', 0) for row in data))
#     total_alm_checkins = int(sum(row.get('alm_checkins', 0) for row in data))
#     total_safety_checkins = int(sum(row.get('safety_checkins', 0) for row in data))
#     total_mis_checkins = int(sum(row.get('mis_checkins', 0) for row in data))

#     avg_sup = round((total_sup_checkins/ total_creches), 1) if total_creches else 0
#     avg_cc = round((total_cc_checkins/ total_creches), 1) if total_creches else 0
#     avg_cbm = round((total_cbm_checkins/ total_creches), 1) if total_creches else 0
#     avg_alm = round((total_alm_checkins/ total_creches), 1) if total_creches else 0
#     avg_safety = round((total_safety_checkins/ total_creches), 1) if total_creches else 0
#     avg_mis = round((total_mis_checkins/ total_creches), 1) if total_creches else 0

#     total_row = {
#         "partner": "<b style='color:black;'>Total</b>",
#         "state": "<b style='color:black;'>Total</b>",
#         "no_of_creches": f"<b>{total_creches}</b>",
#         "sup_checkins": f"<b>{total_sup_checkins}</b>",
#         "cc_checkins": f"<b>{total_cc_checkins}</b>",
#         "cbm_checkins": f"<b>{total_cbm_checkins}</b>",
#         "alm_checkins": f"<b>{total_alm_checkins}</b>",
#         "safety_checkins": f"<b>{total_safety_checkins}</b>",
#         "mis_checkins": f"<b>{total_mis_checkins}</b>",
#         "avg_sup": f"<b>{avg_sup}</b>",
#         "avg_cc": f"<b>{avg_cc}</b>",
#         "avg_cbm": f"<b>{avg_cbm}</b>",
#         "avg_alm": f"<b>{avg_alm}</b>",
#         "avg_safety": f"<b>{avg_safety}</b>",
#         "avg_mis": f"<b>{avg_mis}</b>"
#     }

#     data.append(total_row)

#     return data


# def get_conditions(filters):
#     conditions = "1 = 1"
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

#     partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """

#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
#     state_id = None

#     if filters.get('partner'):
#         partner = filters.get('partner')
#     if partner:
#         conditions += f" AND partner.name = '{partner}'"
#     if filters.get("partner"):
#         conditions += f" AND partner.name = '{filters.get('partner')}'"

#     if filters.get("state"):
#         state = filters.get("state")
#         conditions += f" AND state.name = '{state}'"
#     elif state_ids:
#         conditions += f" AND FIND_IN_SET(state.name, '{state_ids}')"

#     if filters.get("district"):
#         district = filters.get("district")
#         conditions += f" AND district.name = '{district}'"
#     elif district_ids:
#         conditions += f" AND FIND_IN_SET(district.name, '{district_ids}')"
#     if filters.get("block"):
#         block = filters.get("block")
#         conditions += f" AND block.name = '{block}'"
#     elif block_ids:
#         conditions += f" AND FIND_IN_SET(block.name, '{block_ids}')"
#     if filters.get("gp"):
#         gp = filters.get("gp")
#         conditions += f" AND gp.name = '{gp}'"
#     elif gp_ids:
#         conditions += f" AND FIND_IN_SET(gp.name, '{gp_ids}')"
#     if filters.get("creche"):
#         conditions += f" AND creche.name = '{filters.get('creche')}'"
#     if filters.get("supervisor_id"):
#         conditions += f" AND creche.supervisor_id = '{filters.get('supervisor_id')}'"
#     if cstart_date and cend_date:
#         conditions += f" AND creche.creche_opening_date BETWEEN {frappe.db.escape(cstart_date)} AND {frappe.db.escape(cend_date)}"
#     if filters.get("creche_status_id"):
#         conditions += f" AND creche.creche_status_id = '{creche_status_id}'"
#     if phases_cleaned:
#         conditions += f" AND FIND_IN_SET(creche.phase, {frappe.db.escape(phases_cleaned)})"

#     return conditions















# import frappe
# from frappe import _
# from frappe.utils import flt, getdate, nowdate
# import calendar
# from datetime import datetime, timedelta, date


# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_data(filters)
#     return columns, data


# def get_columns(filters=None):
#     selected_level = filters.get("level", "7")
#     variable_columns = []

#     if selected_level == "1":
#         variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 160})
#     if selected_level == "2":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#     if selected_level == "3":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#     if selected_level == "4":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#     if selected_level == "5":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
#     if selected_level == "6":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
#     if selected_level == "7":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 160})
#         variable_columns.append({"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 160})
        
#     fixed_columns = [
#         {"label": _("No. of Creches"), "fieldname": "no_of_creches", "fieldtype": "Data", "width": 180},
#         {"label": _("No. of Checkins by Supervisor"), "fieldname": "sup_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by CC"), "fieldname": "cc_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by CBC"), "fieldname": "cbm_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by ALC"), "fieldname": "alm_checkins", "fieldtype": "Data", "width": 250},
#         {"label": _("No. of Checkins by MIS"), "fieldname": "mis_checkins", "fieldtype": "Data", "width": 290},
#         {"label": _("Avg. Checkins per creche by Supervisor"), "fieldname": "avg_sup", "fieldtype": "float", "width": 300},
#         {"label": _("Avg. Checkins per creche by CC"), "fieldname": "avg_cc", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by CBC"), "fieldname": "avg_cbm", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by ALC"), "fieldname": "avg_alm", "fieldtype": "float", "width": 250},
#         {"label": _("Avg. Checkins per creche by MIS"), "fieldname": "avg_mis", "fieldtype": "float", "width": 250},
#     ]

#     columns = variable_columns + fixed_columns
#     return columns


# def get_data(filters):
#     conditions = get_conditions(filters)
#     level_mapping = {
#         "1": ["partner.partner_name"],
#         "2": ["state.state_name"],
#         "3": ["state.state_name", "district.district_name"],
#         "4": ["state.state_name", "district.district_name", "block.block_name"],
#         "5": ["state.state_name", "district.district_name", "block.block_name", "usr.full_name"],
#         "6": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name"],
#         "7": ["state.state_name", "district.district_name", "block.block_name", "gp.gp_name", "creche.creche_name", "creche.creche_id","usr.full_name"]
#     }
#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)

#     select_fields = [
#         "partner.partner_name AS partner", 
#         "state.state_name AS state", 
#         "district.district_name AS district", 
#         "block.block_name AS block",
#         "gp.gp_name AS gp", 
#         "usr.full_name AS supervisor", 
#         "creche.creche_name AS creche_name", 
#         "creche.creche_id AS creche_id", 
#     ]
#     selected_fields = []
#     for field in select_fields:
#         if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
#             selected_fields.append(field)

#     # date range logic starts here
#     start_date, end_date = None, None

#     if(filters.get("time_range")):
#         time_range = filters.get("time_range") if filters else None
#         start_date, end_date = (time_range if time_range else (None, None))
    
#     elif(filters.get("year") and filters.get("month")):
#         current_date = date.today()
#         month = int(filters.get("month")) if filters.get("month") else current_date.month
#         year = int(filters.get("year")) if filters.get("year") else current_date.year
#         start_date = date(year, month, 1)
#         last_day = calendar.monthrange(year, month)[1]
#         end_date = date(year, month, last_day)    

#     query = f"""
#         SELECT 
#             {",".join(selected_fields)},
#             SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) AS sup_checkins,
#             SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) AS cc_checkins,
#             SUM(CASE WHEN tu.type = 'Capacity and Building Manager' THEN 1 ELSE 0 END) AS cbm_checkins,
#             SUM(CASE WHEN tu.type = 'Accounts and Logistics Manager' THEN 1 ELSE 0 END) AS alm_checkins,
#             SUM(CASE WHEN tu.type = 'MIS Manager' THEN 1 ELSE 0 END) AS mis_checkins,
#             DATE_FORMAT(creche.creche_opening_date, '%d-%m-%Y') AS creche_opening_date,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Creche Supervisor' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_sup,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Cluster Coordinator' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_cc,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Capacity and Building Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_cbm,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'Accounts and Logistics Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_alm,

#             ROUND(
#                 CASE 
#                     WHEN COUNT(creche.name) > 0 
#                     THEN SUM(CASE WHEN tu.type = 'MIS Manager' THEN 1 ELSE 0 END) / COUNT(DISTINCT creche.name) 
#                     ELSE 0 
#                 END, 1
#             ) AS avg_mis,

#             COUNT(DISTINCT creche.name) AS no_of_creches
#         FROM 
#             `tabCreche` creche
#         JOIN 
#             `tabPartner` partner ON creche.partner_id = partner.name
#         JOIN 
#             `tabState` state ON creche.state_id = state.name
#         JOIN 
#             `tabDistrict` district ON creche.district_id = district.name
#         JOIN 
#             `tabBlock` block ON creche.block_id = block.name
#         JOIN 
#             `tabGram Panchayat` gp ON creche.gp_id = gp.name   
#         JOIN 
#             `tabUser` usr ON usr.name = creche.supervisor_id      
#         LEFT JOIN 
#             `tabCreche Check In` checkin ON creche.name = checkin.creche_id
#             AND checkin.date_of_checkin BETWEEN '{start_date}' AND '{end_date}'
#         LEFT JOIN 
#             `tabUser` tu ON checkin.appcreated_by = tu.name 
#         WHERE 
#             {conditions}
#             AND (creche.creche_opening_date IS NULL OR ( '{end_date}' IS NOT NULL AND creche.creche_opening_date <= '{end_date}' ))
#         GROUP BY {group_by_field}
#         ORDER BY {group_by_field}
#     """

#     data = frappe.db.sql(query, as_dict=True)

#     total_creches = int(sum(row.get('no_of_creches', 0) for row in data))
#     total_sup_checkins = int(sum(row.get('sup_checkins', 0) for row in data))
#     total_cc_checkins = int(sum(row.get('cc_checkins', 0) for row in data))
#     total_cbm_checkins = int(sum(row.get('cbm_checkins', 0) for row in data))
#     total_alm_checkins = int(sum(row.get('alm_checkins', 0) for row in data))
#     total_mis_checkins = int(sum(row.get('mis_checkins', 0) for row in data))

#     avg_sup = round((total_sup_checkins/ total_creches), 1) if total_creches else 0
#     avg_cc = round((total_cc_checkins/ total_creches), 1) if total_creches else 0
#     avg_cbm = round((total_cbm_checkins/ total_creches), 1) if total_creches else 0
#     avg_alm = round((total_alm_checkins/ total_creches), 1) if total_creches else 0
#     avg_mis = round((total_mis_checkins/ total_creches), 1) if total_creches else 0

#     total_row = {
#         "partner": "<b style='color:black;'>Total</b>",
#         "state": "<b style='color:black;'>Total</b>",
#         "no_of_creches": f"<b>{total_creches}</b>",
#         "sup_checkins": f"<b>{total_sup_checkins}</b>",
#         "cc_checkins": f"<b>{total_cc_checkins}</b>",
#         "cbm_checkins": f"<b>{total_cbm_checkins}</b>",
#         "alm_checkins": f"<b>{total_alm_checkins}</b>",
#         "mis_checkins": f"<b>{total_mis_checkins}</b>",
#         "avg_sup": f"<b>{avg_sup}</b>",
#         "avg_cc": f"<b>{avg_cc}</b>",
#         "avg_cbm": f"<b>{avg_cbm}</b>",
#         "avg_alm": f"<b>{avg_alm}</b>",
#         "avg_mis": f"<b>{avg_mis}</b>"
#     }

#     data.append(total_row)

#     return data


# def get_conditions(filters):
#     conditions = "1 = 1"
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

#     partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """

#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
#     creche_status_id = filters.get("creche_status_id") if filters else None
#     phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()) if filters.get("phases") else None
#     state_id = None

#     if filters.get('partner'):
#         partner = filters.get('partner')
#     if partner:
#         conditions += f" AND partner.name = '{partner}'"
#     if filters.get("partner"):
#         conditions += f" AND partner.name = '{filters.get('partner')}'"

#     if filters.get("state"):
#         state = filters.get("state")
#         conditions += f" AND state.name = '{state}'"
#     elif state_ids:
#         conditions += f" AND FIND_IN_SET(state.name, '{state_ids}')"

#     if filters.get("district"):
#         district = filters.get("district")
#         conditions += f" AND district.name = '{district}'"
#     elif district_ids:
#         conditions += f" AND FIND_IN_SET(district.name, '{district_ids}')"
#     if filters.get("block"):
#         block = filters.get("block")
#         conditions += f" AND block.name = '{block}'"
#     elif block_ids:
#         conditions += f" AND FIND_IN_SET(block.name, '{block_ids}')"
#     if filters.get("gp"):
#         gp = filters.get("gp")
#         conditions += f" AND gp.name = '{gp}'"
#     elif gp_ids:
#         conditions += f" AND FIND_IN_SET(gp.name, '{gp_ids}')"
#     if filters.get("creche"):
#         conditions += f" AND creche.name = '{filters.get('creche')}'"
#     if filters.get("supervisor_id"):
#         conditions += f" AND creche.supervisor_id = '{filters.get('supervisor_id')}'"
#     if cstart_date and cend_date:
#         conditions += f" AND creche.creche_opening_date BETWEEN {frappe.db.escape(cstart_date)} AND {frappe.db.escape(cend_date)}"
#     if filters.get("creche_status_id"):
#         conditions += f" AND creche.creche_status_id = '{creche_status_id}'"
#     if phases_cleaned:
#         conditions += f" AND FIND_IN_SET(creche.phase, {frappe.db.escape(phases_cleaned)})"

#     return conditions


