import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

# Mapping of specific fields where the `_other` suffix does not perfectly match the field name
OTHER_FIELDS_MAP = {
    "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche": "edge_cutters_or_machinery_kept_away_from_the_creche_other",
    "is_the_structural_safety_of_the_creches_roof_and_walls_ensured": "structural_safety_of_the_creches_roof_and_walls_ensured_other"
}

# ADDED LEVEL "6"
LEVEL_GROUP_FIELDS = {
    "1": ["partner"],
    "2": ["state"],
    "3": ["state", "district"],
    "4": ["state", "district", "block"],
    "5": ["state", "district", "block", "gp"],
    "6": ["partner", "state", "supervisor"],
}

# ADDED SUPERVISOR META
GROUP_FIELD_META = {
    "partner": {"label": "Partner", "name_col": "p.partner_name", "id_col": "cr.partner_id"},
    "state": {"label": "State", "name_col": "s.state_name", "id_col": "cr.state_id"},
    "district": {"label": "District", "name_col": "d.district_name", "id_col": "cr.district_id"},
    "block": {"label": "Block", "name_col": "b.block_name", "id_col": "cr.block_id"},
    "gp": {"label": "Gram Panchayat", "name_col": "g.gp_name", "id_col": "cr.gp_id"},
    "supervisor": {"label": "Supervisor", "name_col": "sup.full_name", "id_col": "cr.supervisor_id"},
}

ANSWER_COUNT_META = ((1, "yes", "Yes"), (2, "no", "No"), (3, "not", "Not Observed"), (4, "other", "Other"))

def execute(filters=None):
    selected_level = filters.get("level") or ""
    selected_category = filters.get("safety_indicators", "1")
    
    fixed_columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
        {"label": "User", "fieldname": "user", "fieldtype": "Data", "width": 180},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 180},
        {"label": "Date of Visit", "fieldname": "date_of_visit", "fieldtype": "Date", "width": 120},
    ]

    categories = {
        "0": [
            {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
            {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
            {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
            {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
            {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
            {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
            {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
            {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
            {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
            {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
            {"field": "positioned_above_cylinder_height", "label": "Is there a separate slab or table for the gas stove positioned above cylinder height?"},
            {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
            {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
            {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
            {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
            {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
            {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
            {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
            {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
            {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
            {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
            {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
            {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
            {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
            {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
        ],
        "1": [
            {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
            {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
            {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
            {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
            {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
        ],
        "2": [
            {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
            {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
            {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
            {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
            {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
        ],
        "3": [
            {"field": "positioned_above_cylinder_height", "label": "Is there a separate slab or table for the gas stove positioned above cylinder height?"},
            {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
            {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
            {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
        ],
        "4": [
            {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
            {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
            {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
            {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
        ],
        "5": [
            {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
            {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
            {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
            {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
        ],
        "6": [
            {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
            {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
            {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
        ],
    }

    questions = categories.get(selected_category, categories["1"])

    if selected_level in LEVEL_GROUP_FIELDS:
        return get_grouped_report(filters, selected_level, questions)

    dynamic_columns = []
    for q in questions:
        dynamic_columns.append({
            "label": q["label"], 
            "fieldname": q["field"], 
            "fieldtype": "Data", 
            "width": 500
        })

    columns = fixed_columns + dynamic_columns
    data = get_report_data(filters, questions)
    
    if data:
        total_row = {"partner": "<b>Total</b>"}
        for q in questions:
            field = q["field"]
            yes_count = sum(1 for row in data if str(row.get(field, '')) == 'Yes')
            no_count = sum(1 for row in data if str(row.get(field, '')) == 'No')
            not_observed_count = sum(1 for row in data if str(row.get(field, '')) == 'Not Observed')
            other_count = sum(1 for row in data if str(row.get(field, '')).startswith('Other'))
            
            total_row[field] = format_total_cell(yes_count, no_count, not_observed_count, other_count)
        
        data.append(total_row)
    
    data = apply_conditional_formatting(data, questions)
    return columns, data

def get_report_data(filters, questions):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping` ugm 
        WHERE ugm.parent = %s
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type")

    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
        elif range_type == "before" and single_date:
            cstart_date = date(2017, 1, 1)
            cend_date = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            cstart_date = single_date + timedelta(days=1)
            cend_date = date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    question_fields = []
    for q in questions:
        field = q["field"]
        other_field = OTHER_FIELDS_MAP.get(field, f"{field}_other")
        question_fields.append(f"""
            CASE 
                WHEN si.{field} = 1 THEN 'Yes'
                WHEN si.{field} = 2 THEN 'No'
                WHEN si.{field} = 3 THEN 'Not Observed'
                WHEN si.{field} = 4 THEN CONCAT('Other: ', COALESCE(si.{other_field}, ''))
                ELSE 'N/A'
            END AS {field}
        """)

    question_select = ",\n".join(question_fields) if question_fields else ""

    query = f"""
    SELECT
        si.date_of_visit,
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block,
        g.gp_name AS gp,
        sup.full_name AS supervisor,
        u.full_name AS user,
        u.type AS designation,
        cr.creche_name AS creche,
        cr.creche_id AS creche_id,
        cr.creche_opening_date AS cr_open_date,
        {question_select}
    FROM `tabSafety Indicators` si
    INNER JOIN `tabCreche` cr ON cr.name = si.creche_id
    INNER JOIN `tabPartner` p ON p.name = cr.partner_id
    INNER JOIN `tabState` s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` d ON d.name = cr.district_id
    INNER JOIN `tabBlock` b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
    LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
    LEFT JOIN `tabUser` u ON u.name = si.owner
    WHERE si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
    """

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    if partner_id:
        query += " AND cr.partner_id = %(partner)s"
        params["partner"] = partner_id
    
    if filters.get("state"):
        query += " AND cr.state_id = %(state)s"
        params["state"] = filters.get("state")
    elif state_ids:
        query += " AND cr.state_id IN %(state_ids)s"
        params["state_ids"] = tuple(state_ids) if state_ids else ('',)

    if filters.get("district"):
        query += " AND cr.district_id = %(district)s"
        params["district"] = filters.get("district")
    elif district_ids:
        query += " AND cr.district_id IN %(district_ids)s"
        params["district_ids"] = tuple(district_ids) if district_ids else ('',)

    if filters.get("block"):
        query += " AND cr.block_id = %(block)s"
        params["block"] = filters.get("block")
    elif block_ids:
        query += " AND cr.block_id IN %(block_ids)s"
        params["block_ids"] = tuple(block_ids) if block_ids else ('',)

    if filters.get("gp"):
        query += " AND cr.gp_id = %(gp)s"
        params["gp"] = filters.get("gp")
    elif gp_ids:
        query += " AND cr.gp_id IN %(gp_ids)s"
        params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

    if filters.get("creche"):
        query += " AND cr.name = %(creche)s"
        params["creche"] = filters.get("creche")
    
    if filters.get("supervisor_id"):
        query += " AND cr.supervisor_id = %(supervisor_id)s"
        params["supervisor_id"] = filters.get("supervisor_id")
        
    if filters.get("user"):
        query += " AND si.owner = %(user)s"
        params["user"] = filters.get("user")

    if filters.get("designation"):
        query += " AND u.type = %(designation)s"
        params["designation"] = filters.get("designation")
    
    if filters.get("creche_status_id"):
        query += " AND cr.creche_status_id = %(creche_status_id)s"
        params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
        if phases:
            query += " AND cr.phase IN %(phases)s"
            params["phases"] = tuple(phases)
    
    if cstart_date or cend_date:
        query += " AND cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
        params["cstart_date"] = cstart_date
        params["cend_date"] = cend_date

    creche_age = filters.get("creche_age", "")
    params["creche_age"] = creche_age
    if creche_age:
        query += """
            AND (
                CASE
                    WHEN cr.creche_opening_date IS NULL THEN ''
                    WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                    WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                    WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                    WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                    WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                    ELSE ''
                END = %(creche_age)s
            )
        """

    query += " ORDER BY si.date_of_visit DESC, p.partner_name, s.state_name, d.district_name"

    try:
        data = frappe.db.sql(query, params, as_dict=True)
        if not data:
            frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
    except Exception as e:
        frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
        data = []

    return data

def get_grouped_report(filters, selected_level, questions):
    group_fields = LEVEL_GROUP_FIELDS[selected_level]

    columns = [
        {"label": GROUP_FIELD_META[f]["label"], "fieldname": f, "fieldtype": "Data", "width": 180}
        for f in group_fields
    ]
    
    # Add Total Creches column after Supervisor field for level 6
    if selected_level == "6":
        columns.append({
            "label": "Total Creches",
            "fieldname": "total_creches",
            "fieldtype": "Data",
            "width": 120
        })
    
    for q in questions:
        columns.append({
            "label": q["label"],
            "fieldname": q["field"],
            "fieldtype": "Data",
            "width": 500
        })

    data = get_grouped_report_data(filters, group_fields, questions, selected_level)
    return columns, data

def get_grouped_report_data(filters, group_fields, questions, selected_level=""):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping` ugm
        WHERE ugm.parent = %s
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)

    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type")

    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()

        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
        elif range_type == "before" and single_date:
            cstart_date = date(2017, 1, 1)
            cend_date = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            cstart_date = single_date + timedelta(days=1)
            cend_date = date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    if partner_id:
        conditions.append("cr.partner_id = %(partner)s")
        params["partner"] = partner_id

    if filters.get("state"):
        conditions.append("cr.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        conditions.append("cr.state_id IN %(state_ids)s")
        params["state_ids"] = tuple(state_ids)

    if filters.get("district"):
        conditions.append("cr.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids:
        conditions.append("cr.district_id IN %(district_ids)s")
        params["district_ids"] = tuple(district_ids)

    if filters.get("block"):
        conditions.append("cr.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids:
        conditions.append("cr.block_id IN %(block_ids)s")
        params["block_ids"] = tuple(block_ids)

    if filters.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids:
        conditions.append("cr.gp_id IN %(gp_ids)s")
        params["gp_ids"] = tuple(gp_ids)

    if filters.get("creche"):
        conditions.append("cr.name = %(creche)s")
        params["creche"] = filters.get("creche")

    if filters.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")

    if filters.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")

    if filters.get("phases"):
        phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params["phases"] = tuple(phases)

    if cstart_date or cend_date:
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
        params["cstart_date"] = cstart_date
        params["cend_date"] = cend_date

    creche_age = filters.get("creche_age", "")
    if creche_age:
        params["creche_age"] = creche_age
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

    # For level 6 (Supervisor), handle grouping differently to avoid duplicates
    if selected_level == "6":
        # Group by full hierarchy including supervisor to ensure each combination appears once
        select_parts = [f'{GROUP_FIELD_META[f]["name_col"]} AS {f}' for f in group_fields]
        select_parts += [f'MIN({GROUP_FIELD_META[f]["id_col"]}) AS {f}_link_id' for f in group_fields]
        select_parts.append('COUNT(DISTINCT cr.name) AS total_creches')
        
        for q in questions:
            fn = q["field"]
            for value, suffix, _ in ANSWER_COUNT_META:
                select_parts.append(f"COALESCE(SUM(CASE WHEN si.{fn} = {value} THEN 1 ELSE 0 END), 0) AS {fn}_{suffix}")
        
        select_clause = ",\n        ".join(select_parts)
        group_by = ", ".join(GROUP_FIELD_META[f]["name_col"] for f in group_fields)
    else:
        # For other levels, use standard grouping with full hierarchy
        select_parts = [f'{GROUP_FIELD_META[f]["name_col"]} AS {f}' for f in group_fields]
        select_parts += [f'MIN({GROUP_FIELD_META[f]["id_col"]}) AS {f}_link_id' for f in group_fields]

        for q in questions:
            fn = q["field"]
            for value, suffix, _ in ANSWER_COUNT_META:
                select_parts.append(f"COALESCE(SUM(CASE WHEN si.{fn} = {value} THEN 1 ELSE 0 END), 0) AS {fn}_{suffix}")

        select_clause = ",\n        ".join(select_parts)
        group_by = ", ".join(GROUP_FIELD_META[f]["name_col"] for f in group_fields)
    
    where_clause = " AND ".join(conditions)

    # ADDED: LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id so group_by works!
    query = f"""
    SELECT
        {select_clause}
    FROM `tabCreche` cr
    INNER JOIN `tabPartner` p ON p.name = cr.partner_id
    INNER JOIN `tabState` s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` d ON d.name = cr.district_id
    INNER JOIN `tabBlock` b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
    LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
    LEFT JOIN `tabSafety Indicators` si ON si.creche_id = cr.name
        AND si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
    WHERE {where_clause}
    GROUP BY {group_by}
    ORDER BY {group_by}
    """

    try:
        data = frappe.db.sql(query, params, as_dict=True)
        if not data:
            frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
    except Exception as e:
        frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
        data = []

    if data:
        total_row = {group_fields[0]: "<b>Total</b>"}
        for q in questions:
            fn = q["field"]
            for _, suffix, _ in ANSWER_COUNT_META:
                total_row[f"{fn}_{suffix}"] = sum(int(row.get(f"{fn}_{suffix}") or 0) for row in data)
            total_row[fn] = "__total__"
        
        # Add total creches count for level 6
        if selected_level == "6":
            total_row["total_creches"] = sum(int(row.get("total_creches") or 0) for row in data)

        data.append(total_row)

    return data

def apply_conditional_formatting(data, questions):
    for row in data:
        if row.get("partner") == "<b>Total</b>":
            continue
            
        for q in questions:
            field = q["field"]
            value = str(row.get(field, ''))
            
            if value == 'Yes':
                row[field] = format_cell(value, "#CCFFCC", "#006600")
            elif value == 'No':
                row[field] = format_cell(value, "#FFCCCC", "#CC0000")
            elif value == 'Not Observed':
                row[field] = format_cell(value, "#FFFFCC", "#999900")
            elif value.startswith('Other'):
                row[field] = format_cell(value, "#FFE5CC", "#CC6600")
            elif value in ('-', 'N/A'):
                row[field] = format_cell(value, "#E6E6E6", "#666666")
    
    return data

def format_cell(value, bg_color, text_color):
    return f"""
        <div style='
            background-color: {bg_color};
            color: {text_color};
            border-radius: 3px;
            text-align: center;
            font-weight: bold;
            padding: 5px 10px;
        '>
            {value}
        </div>
    """

def format_total_cell(yes_count, no_count, not_observed_count, other_count):
    return f"""
        <div style='
            background-color: #E6F3FF;
            border-radius: 3px;
            padding: 8px 5px;
            font-size: 13px;
            text-align: center;
            white-space: nowrap;
        '>
            <span style='color: #006600;'><b>Yes:</b> {yes_count}</span> <span style='color: #666;'>||</span> 
            <span style='color: #CC0000;'><b>No:</b> {no_count}</span> <span style='color: #666;'>||</span> 
            <span style='color: #999900;'><b>Not Observed:</b> {not_observed_count}</span> <span style='color: #666;'>||</span> 
            <span style='color: #CC6600;'><b>Other:</b> {other_count}</span>
        </div>
    """