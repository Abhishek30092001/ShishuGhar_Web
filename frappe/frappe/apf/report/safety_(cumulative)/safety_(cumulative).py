import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    selected_level = filters.get("level", "7")
    selected_category = filters.get("safety_indicators", "1")
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
        variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 180})

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
            {"field": "positioned_above_cylinder_height", "label": " Is there a separate slab or table for the gas stove positioned above  cylinder height?"},
            {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
            {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
            {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
            {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
            {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
            {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
            {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
            {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
            {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
            {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day? "},
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
            {"field": "positioned_above_cylinder_height", "label": " Is there a separate slab or table for the gas stove positioned above  cylinder height?"},
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
            {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day? "},
            {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
        ],
        "6": [
            {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
            {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
            {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
        ],
    }

    questions = categories.get(selected_category, categories["1"])

    fixed_columns = []
    for q in questions:
        base_fn = q["field"]
        fixed_columns.append({"label": q["label"] + " - (Yes)", "fieldname": base_fn + "_yes", "fieldtype": "Int", "width": 500})
        fixed_columns.append({"label": q["label"] + " - (No)", "fieldname": base_fn + "_no", "fieldtype": "Int", "width": 500})
        fixed_columns.append({"label": q["label"] + " - (Not Observed)", "fieldname": base_fn + "_not", "fieldtype": "Int", "width": 500})
        fixed_columns.append({"label": q["label"] + " - (Other)", "fieldname": base_fn + "_other", "fieldtype": "Int", "width": 500})

    columns = variable_columns + fixed_columns
    data = get_report_data(filters, selected_level, questions)
    return columns, data

def get_report_data(filters, selected_level, questions):
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
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
    }

    # Handle user permissions
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    # Get user geography mapping
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

    # Handle creche opening date range
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

    # Build conditions
    if partner_id:
        conditions.append("cr.partner_id = %(partner)s")
        params["partner"] = partner_id
    
    # State filter
    if filters.get("state"):
        conditions.append("cr.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        conditions.append(f"cr.state_id IN %(state_ids)s")
        params["state_ids"] = tuple(state_ids) if state_ids else ('',)

    # District filter
    if filters.get("district"):
        conditions.append("cr.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids:
        conditions.append(f"cr.district_id IN %(district_ids)s")
        params["district_ids"] = tuple(district_ids) if district_ids else ('',)

    # Block filter
    if filters.get("block"):
        conditions.append("cr.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids:
        conditions.append(f"cr.block_id IN %(block_ids)s")
        params["block_ids"] = tuple(block_ids) if block_ids else ('',)

    # GP filter
    if filters.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids:
        conditions.append(f"cr.gp_id IN %(gp_ids)s")
        params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

    # Other filters
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

    # Add creche_age filter
    creche_age = filters.get("creche_age", "")
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

    level_mapping = {
        "1": ["partner"],
        "2": ["state"],
        "3": ["state", "district"],
        "4": ["state", "district", "block"],
        "5": ["state", "district", "block", "supervisor"],
        "6": ["state", "district", "block", "gp"],
        "7": ["state", "district", "block", "gp", "supervisor", "creche", "creche_id", "cr_open_date"],
    }

    field_to_select = {
        "partner": "p.partner_name AS partner",
        "state": "s.state_name AS state",
        "district": "d.district_name AS district",
        "block": "b.block_name AS block",
        "gp": "g.gp_name AS gp",
        "supervisor": "sup.full_name AS supervisor",
        "creche": "cr.creche_name AS creche",
        "creche_id": "cr.creche_id AS creche_id",
        "cr_open_date": "cr.creche_opening_date AS cr_open_date",
    }

    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    
    # Build SELECT clause
    select_parts = []
    for field in group_by_fields:
        if field in field_to_select:
            select_parts.append(f"        {field_to_select[field]}")
    
    select_group = ",\n".join(select_parts) if select_parts else ""
    
    # Build GROUP BY clause
    group_by_parts = []
    for field in group_by_fields:
        if field in field_to_select:
            group_by_parts.append(field_to_select[field].split(" AS ")[0])
    
    group_by = ", ".join(group_by_parts) if group_by_parts else "cr.name"

    # Build COUNT fields
    select_counts = ""
    for q in questions:
        fn = q["field"]
        select_counts += f"""
        COALESCE(SUM(CASE WHEN si.{fn} = 1 THEN 1 ELSE 0 END), 0) AS {fn}_yes,
        COALESCE(SUM(CASE WHEN si.{fn} = 2 THEN 1 ELSE 0 END), 0) AS {fn}_no,
        COALESCE(SUM(CASE WHEN si.{fn} = 3 THEN 1 ELSE 0 END), 0) AS {fn}_not,
        COALESCE(SUM(CASE WHEN si.{fn} = 4 THEN 1 ELSE 0 END), 0) AS {fn}_other,"""

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Main query - Use LEFT JOIN to include all creches even if no safety indicators
    query = f"""
    SELECT
{select_group}{"," if select_group and select_counts else ""}
{select_counts.rstrip(",")}
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
        
        # If no data found, try a simpler query to debug
        if not data:
            frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report")
            
            # Debug query to check if any safety indicators exist
            debug_query = """
            SELECT COUNT(*) as count 
            FROM `tabSafety Indicators` 
            WHERE date_of_visit BETWEEN %(start_date)s AND %(end_date)s
            """
            debug_result = frappe.db.sql(debug_query, params, as_dict=True)
            if debug_result:
                frappe.log_error(f"Safety Indicators count: {debug_result[0].get('count', 0)}", "Safety Indicators Report")
        
    except Exception as e:
        frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report")
        data = []

    # Add total row only if there's data
    if data:
        count_fields = []
        for q in questions:
            fn = q["field"]
            count_fields.extend([f"{fn}_yes", f"{fn}_no", f"{fn}_not", f"{fn}_other"])

        total_row = {}
        # Set first grouping field to "Total" if it exists
        if group_by_fields and group_by_fields[0] in field_to_select:
            field_name = field_to_select[group_by_fields[0]].split(" AS ")[1]
            total_row[field_name] = "<b>Total</b>"
        
        for field in count_fields:
            sum_val = sum(int(row.get(field, 0)) for row in data)
            total_row[field] = f"<b>{sum_val}</b>"

        data.append(total_row)
    
    return data



















# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_level = filters.get("level", "7")
#     selected_category = filters.get("safety_indicators", "1")
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
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 180})

#     categories = {
#         "0": [
#             {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
#             {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
#             {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
#             {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
#             {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
#             {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
#             {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
#             {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
#             {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
#             {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
#             {"field": "positioned_above_cylinder_height", "label": " Is there a separate slab or table for the gas stove positioned above  cylinder height?"},
#             {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#             {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#             {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
#             {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#             {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#             {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#             {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
#             {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#             {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day? "},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#         "1": [
#             {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
#             {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
#             {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
#             {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
#             {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
#         ],
#         "2": [
#             {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
#             {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
#             {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
#             {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
#             {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
#         ],
#         "3": [
#             {"field": "positioned_above_cylinder_height", "label": " Is there a separate slab or table for the gas stove positioned above  cylinder height?"},
#             {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#             {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#             {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
#         ],
#         "4": [
#             {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#             {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#             {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#             {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
#         ],
#         "5": [
#             {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#             {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day? "},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     questions = categories.get(selected_category, categories["1"])

#     fixed_columns = []
#     for q in questions:
#         base_fn = q["field"]
#         fixed_columns.append({"label": q["label"] + " - (Yes)", "fieldname": base_fn + "_yes", "fieldtype": "Int", "width": 500})
#         fixed_columns.append({"label": q["label"] + " - (No)", "fieldname": base_fn + "_no", "fieldtype": "Int", "width": 500})
#         fixed_columns.append({"label": q["label"] + " - (Not Observed)", "fieldname": base_fn + "_not", "fieldtype": "Int", "width": 500})

#     columns = variable_columns + fixed_columns
#     data = get_report_data(filters, selected_level, questions)
#     return columns, data

# def get_report_data(filters, selected_level, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#     }

#     # Handle user permissions
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Get user geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping` ugm 
#         WHERE ugm.parent = %s
#     """
    
#     current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    
#     state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#     district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#     block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#     gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

#     # Handle creche opening date range
#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type")

#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range
#         elif range_type == "before" and single_date:
#             cstart_date = date(2017, 1, 1)
#             cend_date = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             cstart_date = single_date + timedelta(days=1)
#             cend_date = date.today()
#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date

#     # Build conditions
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     # State filter
#     if filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         conditions.append(f"cr.state_id IN %(state_ids)s")
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     # District filter
#     if filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids:
#         conditions.append(f"cr.district_id IN %(district_ids)s")
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     # Block filter
#     if filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids:
#         conditions.append(f"cr.block_id IN %(block_ids)s")
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     # GP filter
#     if filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         conditions.append(f"cr.gp_id IN %(gp_ids)s")
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     # Other filters
#     if filters.get("creche"):
#         conditions.append("cr.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             conditions.append("cr.phase IN %(phases)s")
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     # Add creche_age filter
#     creche_age = filters.get("creche_age", "")
#     params["creche_age"] = creche_age
#     if creche_age:
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

#     level_mapping = {
#         "1": ["partner"],
#         "2": ["state"],
#         "3": ["state", "district"],
#         "4": ["state", "district", "block"],
#         "5": ["state", "district", "block", "supervisor"],
#         "6": ["state", "district", "block", "gp"],
#         "7": ["state", "district", "block", "gp", "supervisor", "creche", "creche_id", "cr_open_date"],
#     }

#     field_to_select = {
#         "partner": "p.partner_name AS partner",
#         "state": "s.state_name AS state",
#         "district": "d.district_name AS district",
#         "block": "b.block_name AS block",
#         "gp": "g.gp_name AS gp",
#         "supervisor": "sup.full_name AS supervisor",
#         "creche": "cr.creche_name AS creche",
#         "creche_id": "cr.creche_id AS creche_id",
#         "cr_open_date": "cr.creche_opening_date AS cr_open_date",
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    
#     # Build SELECT clause
#     select_parts = []
#     for field in group_by_fields:
#         if field in field_to_select:
#             select_parts.append(f"        {field_to_select[field]}")
    
#     select_group = ",\n".join(select_parts) if select_parts else ""
    
#     # Build GROUP BY clause
#     group_by_parts = []
#     for field in group_by_fields:
#         if field in field_to_select:
#             group_by_parts.append(field_to_select[field].split(" AS ")[0])
    
#     group_by = ", ".join(group_by_parts) if group_by_parts else "cr.name"

#     # Build COUNT fields
#     select_counts = ""
#     for q in questions:
#         fn = q["field"]
#         select_counts += f"""
#         COALESCE(SUM(CASE WHEN si.{fn} = 1 THEN 1 ELSE 0 END), 0) AS {fn}_yes,
#         COALESCE(SUM(CASE WHEN si.{fn} = 2 THEN 1 ELSE 0 END), 0) AS {fn}_no,
#         COALESCE(SUM(CASE WHEN si.{fn} = 3 THEN 1 ELSE 0 END), 0) AS {fn}_not,"""

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     # Main query - Use LEFT JOIN to include all creches even if no safety indicators
#     query = f"""
#     SELECT
# {select_group}{"," if select_group and select_counts else ""}
# {select_counts.rstrip(",")}
#     FROM `tabCreche` cr
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     LEFT JOIN `tabSafety Indicators` si ON si.creche_id = cr.name 
#         AND si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     WHERE {where_clause}
#     GROUP BY {group_by}
#     ORDER BY {group_by}
#     """

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         # If no data found, try a simpler query to debug
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report")
            
#             # Debug query to check if any safety indicators exist
#             debug_query = """
#             SELECT COUNT(*) as count 
#             FROM `tabSafety Indicators` 
#             WHERE date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#             """
#             debug_result = frappe.db.sql(debug_query, params, as_dict=True)
#             if debug_result:
#                 frappe.log_error(f"Safety Indicators count: {debug_result[0].get('count', 0)}", "Safety Indicators Report")
        
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report")
#         data = []

#     # Add total row only if there's data
#     if data:
#         count_fields = []
#         for q in questions:
#             fn = q["field"]
#             count_fields.extend([f"{fn}_yes", f"{fn}_no", f"{fn}_not"])

#         total_row = {}
#         # Set first grouping field to "Total" if it exists
#         if group_by_fields and group_by_fields[0] in field_to_select:
#             field_name = field_to_select[group_by_fields[0]].split(" AS ")[1]
#             total_row[field_name] = "<b>Total</b>"
        
#         for field in count_fields:
#             sum_val = sum(int(row.get(field, 0)) for row in data)
#             total_row[field] = f"<b>{sum_val}</b>"

#         data.append(total_row)
    
#     return data










#backup before age of creche filter
# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_level = filters.get("level", "7")
#     selected_category = filters.get("safety_indicators", "1")
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
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 180})

#     categories = {
#         "1": [
#             {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
#             {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
#             {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
#             {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
#             {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
#         ],
#         "2": [
#             {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
#             {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
#             {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
#             {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
#             {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
#         ],
#         "3": [
#             {"field": "positioned_above_cylinder_height", "label": " Is there a separate slab or table for the gas stove positioned above  cylinder height?"},
#             {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#             {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#             {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
#         ],
#         "4": [
#             {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#             {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#             {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#             {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
#         ],
#         "5": [
#             {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#             {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day? "},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     questions = categories.get(selected_category, categories["1"])

#     fixed_columns = []
#     for q in questions:
#         base_fn = q["field"]
#         fixed_columns.append({"label": q["label"] + " - (Yes)", "fieldname": base_fn + "_yes", "fieldtype": "Int", "width": 500})
#         fixed_columns.append({"label": q["label"] + " - (No)", "fieldname": base_fn + "_no", "fieldtype": "Int", "width": 500})
#         fixed_columns.append({"label": q["label"] + " - (Not Observed)", "fieldname": base_fn + "_not", "fieldtype": "Int", "width": 500})

#     columns = variable_columns + fixed_columns
#     data = get_report_data(filters, selected_level, questions)
#     return columns, data

# def get_report_data(filters, selected_level, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#     }

#     # Handle user permissions
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Get user geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping` ugm 
#         WHERE ugm.parent = %s
#     """
    
#     current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    
#     state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#     district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#     block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#     gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

#     # Handle creche opening date range
#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type")

#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range
#         elif range_type == "before" and single_date:
#             cstart_date = date(2017, 1, 1)
#             cend_date = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             cstart_date = single_date + timedelta(days=1)
#             cend_date = date.today()
#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date

#     # Build conditions
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     # State filter
#     if filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         conditions.append(f"cr.state_id IN %(state_ids)s")
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     # District filter
#     if filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids:
#         conditions.append(f"cr.district_id IN %(district_ids)s")
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     # Block filter
#     if filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids:
#         conditions.append(f"cr.block_id IN %(block_ids)s")
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     # GP filter
#     if filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         conditions.append(f"cr.gp_id IN %(gp_ids)s")
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     # Other filters
#     if filters.get("creche"):
#         conditions.append("cr.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             conditions.append("cr.phase IN %(phases)s")
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     level_mapping = {
#         "1": ["partner"],
#         "2": ["state"],
#         "3": ["state", "district"],
#         "4": ["state", "district", "block"],
#         "5": ["state", "district", "block", "supervisor"],
#         "6": ["state", "district", "block", "gp"],
#         "7": ["state", "district", "block", "gp", "supervisor", "creche", "creche_id", "cr_open_date"],
#     }

#     field_to_select = {
#         "partner": "p.partner_name AS partner",
#         "state": "s.state_name AS state",
#         "district": "d.district_name AS district",
#         "block": "b.block_name AS block",
#         "gp": "g.gp_name AS gp",
#         "supervisor": "sup.full_name AS supervisor",
#         "creche": "cr.creche_name AS creche",
#         "creche_id": "cr.creche_id AS creche_id",
#         "cr_open_date": "cr.creche_opening_date AS cr_open_date",
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    
#     # Build SELECT clause
#     select_parts = []
#     for field in group_by_fields:
#         if field in field_to_select:
#             select_parts.append(f"        {field_to_select[field]}")
    
#     select_group = ",\n".join(select_parts) if select_parts else ""
    
#     # Build GROUP BY clause
#     group_by_parts = []
#     for field in group_by_fields:
#         if field in field_to_select:
#             group_by_parts.append(field_to_select[field].split(" AS ")[0])
    
#     group_by = ", ".join(group_by_parts) if group_by_parts else "cr.name"

#     # Build COUNT fields
#     select_counts = ""
#     for q in questions:
#         fn = q["field"]
#         select_counts += f"""
#         COALESCE(SUM(CASE WHEN si.{fn} = 1 THEN 1 ELSE 0 END), 0) AS {fn}_yes,
#         COALESCE(SUM(CASE WHEN si.{fn} = 2 THEN 1 ELSE 0 END), 0) AS {fn}_no,
#         COALESCE(SUM(CASE WHEN si.{fn} = 3 THEN 1 ELSE 0 END), 0) AS {fn}_not,"""

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     # Main query - Use LEFT JOIN to include all creches even if no safety indicators
#     query = f"""
#     SELECT
# {select_group}{"," if select_group and select_counts else ""}
# {select_counts.rstrip(",")}
#     FROM `tabCreche` cr
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     LEFT JOIN `tabSafety Indicators` si ON si.creche_id = cr.name 
#         AND si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     WHERE {where_clause}
#     GROUP BY {group_by}
#     ORDER BY {group_by}
#     """

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         # If no data found, try a simpler query to debug
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report")
            
#             # Debug query to check if any safety indicators exist
#             debug_query = """
#             SELECT COUNT(*) as count 
#             FROM `tabSafety Indicators` 
#             WHERE date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#             """
#             debug_result = frappe.db.sql(debug_query, params, as_dict=True)
#             if debug_result:
#                 frappe.log_error(f"Safety Indicators count: {debug_result[0].get('count', 0)}", "Safety Indicators Report")
        
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report")
#         data = []

#     # Add total row only if there's data
#     if data:
#         count_fields = []
#         for q in questions:
#             fn = q["field"]
#             count_fields.extend([f"{fn}_yes", f"{fn}_no", f"{fn}_not"])

#         total_row = {}
#         # Set first grouping field to "Total" if it exists
#         if group_by_fields and group_by_fields[0] in field_to_select:
#             field_name = field_to_select[group_by_fields[0]].split(" AS ")[1]
#             total_row[field_name] = "<b>Total</b>"
        
#         for field in count_fields:
#             sum_val = sum(int(row.get(field, 0)) for row in data)
#             total_row[field] = f"<b>{sum_val}</b>"

#         data.append(total_row)
    
#     return data








# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_level = filters.get("level", "7")
#     selected_category = filters.get("safety_indicators", "1")
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
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Data", "width": 150})

#     categories = {
#         "1": [
#             {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
#             {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
#             {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
#             {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
#             {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
#         ],
#         "2": [
#             {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
#             {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
#             {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
#             {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
#             {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
#         ],
#         "3": [
#             {"field": "positioned_above_cylinder_height", "label": "Is there a separate slab or table for the gas stove positioned above cylinder height?"},
#             {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#             {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#             {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
#         ],
#         "4": [
#             {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#             {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#             {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#             {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
#         ],
#         "5": [
#             {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#             {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day? "},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     questions = categories.get(selected_category, categories["1"])

#     # Create columns with question as header and Yes/No/Not Observed as sub-headers
#     fixed_columns = []
#     for q in questions:
#         # Main question column (will show the question text)
#         fixed_columns.append({
#             "label": q["label"],
#             "fieldname": q["field"],
#             "fieldtype": "Data",
#             "width": 300,
#             "align": "left"
#         })
        
#         # Yes sub-column
#         fixed_columns.append({
#             "label": "Yes",
#             "fieldname": q["field"] + "_yes",
#             "fieldtype": "Int",
#             "width": 80
#         })
        
#         # No sub-column
#         fixed_columns.append({
#             "label": "No",
#             "fieldname": q["field"] + "_no",
#             "fieldtype": "Int",
#             "width": 80
#         })
        
#         # Not Observed sub-column
#         fixed_columns.append({
#             "label": "Not Observed",
#             "fieldname": q["field"] + "_not",
#             "fieldtype": "Int",
#             "width": 120
#         })

#     columns = variable_columns + fixed_columns
#     data = get_report_data(filters, selected_level, questions)
#     return columns, data

# def get_report_data(filters, selected_level, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "partner": None,
#         "state": None,
#         "district": None,
#         "block": None,
#         "gp": None,
#         "creche": None,
#     }

#     # Handle user permissions
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Get user geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping` ugm 
#         WHERE ugm.parent = %s
#     """
    
#     current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
    
#     state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#     district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#     block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#     gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

#     # Handle creche opening date range
#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type")

#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range
#         elif range_type == "before" and single_date:
#             cstart_date = date(2017, 1, 1)
#             cend_date = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             cstart_date = single_date + timedelta(days=1)
#             cend_date = date.today()
#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date

#     # Build conditions
#     if partner_id:
#         conditions.append("cr.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     # State filter
#     if filters.get("state"):
#         conditions.append("cr.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         conditions.append(f"cr.state_id IN %(state_ids)s")
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     # District filter
#     if filters.get("district"):
#         conditions.append("cr.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids:
#         conditions.append(f"cr.district_id IN %(district_ids)s")
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     # Block filter
#     if filters.get("block"):
#         conditions.append("cr.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids:
#         conditions.append(f"cr.block_id IN %(block_ids)s")
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     # GP filter
#     if filters.get("gp"):
#         conditions.append("cr.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         conditions.append(f"cr.gp_id IN %(gp_ids)s")
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     # Other filters
#     if filters.get("creche"):
#         conditions.append("cr.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             conditions.append("cr.phase IN %(phases)s")
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     level_mapping = {
#         "1": ["partner"],
#         "2": ["state"],
#         "3": ["state", "district"],
#         "4": ["state", "district", "block"],
#         "5": ["state", "district", "block", "supervisor"],
#         "6": ["state", "district", "block", "gp"],
#         "7": ["state", "district", "block", "gp", "supervisor", "creche", "creche_id", "cr_open_date"],
#     }

#     field_to_select = {
#         "partner": "p.partner_name AS partner",
#         "state": "s.state_name AS state",
#         "district": "d.district_name AS district",
#         "block": "b.block_name AS block",
#         "gp": "g.gp_name AS gp",
#         "supervisor": "sup.full_name AS supervisor",
#         "creche": "cr.creche_name AS creche",
#         "creche_id": "cr.name AS creche_id",
#         "cr_open_date": "cr.creche_opening_date AS cr_open_date",
#     }

#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    
#     # Build SELECT clause
#     select_parts = []
#     for field in group_by_fields:
#         if field in field_to_select:
#             select_parts.append(f"        {field_to_select[field]}")
    
#     select_group = ",\n".join(select_parts) if select_parts else ""
    
#     # Build GROUP BY clause
#     group_by_parts = []
#     for field in group_by_fields:
#         if field in field_to_select:
#             group_by_parts.append(field_to_select[field].split(" AS ")[0])
    
#     group_by = ", ".join(group_by_parts) if group_by_parts else "cr.name"

#     # Build COUNT fields - Now we need to include the question field itself
#     select_counts = ""
#     for q in questions:
#         fn = q["field"]
#         select_counts += f"""
#         '' AS {fn},
#         COALESCE(SUM(CASE WHEN si.{fn} = 1 THEN 1 ELSE 0 END), 0) AS {fn}_yes,
#         COALESCE(SUM(CASE WHEN si.{fn} = 2 THEN 1 ELSE 0 END), 0) AS {fn}_no,
#         COALESCE(SUM(CASE WHEN si.{fn} = 3 THEN 1 ELSE 0 END), 0) AS {fn}_not,"""

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     # Main query - Use LEFT JOIN to include all creches even if no safety indicators
#     query = f"""
#     SELECT
# {select_group}{"," if select_group and select_counts else ""}
# {select_counts.rstrip(",")}
#     FROM `tabCreche` cr
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     LEFT JOIN `tabSafety Indicators` si ON si.creche_id = cr.name 
#         AND si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     WHERE {where_clause}
#     GROUP BY {group_by}
#     ORDER BY {group_by}
#     """

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         # Process the data to show the question text in the first column of each question group
#         if data:
#             for row in data:
#                 for q in questions:
#                     # Set the question field to the question label for display
#                     row[q["field"]] = q["label"]
        
#         # If no data found, try a simpler query to debug
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report")
            
#             # Debug query to check if any safety indicators exist
#             debug_query = """
#             SELECT COUNT(*) as count 
#             FROM `tabSafety Indicators` 
#             WHERE date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#             """
#             debug_result = frappe.db.sql(debug_query, params, as_dict=True)
#             if debug_result:
#                 frappe.log_error(f"Safety Indicators count: {debug_result[0].get('count', 0)}", "Safety Indicators Report")
        
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report")
#         data = []

#     # Add total row only if there's data
#     if data:
#         count_fields = []
#         for q in questions:
#             fn = q["field"]
#             count_fields.extend([f"{fn}_yes", f"{fn}_no", f"{fn}_not"])

#         total_row = {}
#         # Set first grouping field to "Total" if it exists
#         if group_by_fields and group_by_fields[0] in field_to_select:
#             field_name = field_to_select[group_by_fields[0]].split(" AS ")[1]
#             total_row[field_name] = "<b>Total</b>"
        
#         # Add empty strings for question fields in total row
#         for q in questions:
#             total_row[q["field"]] = ""
        
#         for field in count_fields:
#             sum_val = sum(int(row.get(field, 0)) for row in data)
#             total_row[field] = f"<b>{sum_val}</b>"

#         data.append(total_row)
    
#     return data