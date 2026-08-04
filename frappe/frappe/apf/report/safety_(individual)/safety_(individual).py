import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

# Mapping of specific fields where the `_other` suffix does not perfectly match the field name
OTHER_FIELDS_MAP = {
    "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche": "edge_cutters_or_machinery_kept_away_from_the_creche_other",
    "is_the_structural_safety_of_the_creches_roof_and_walls_ensured": "structural_safety_of_the_creches_roof_and_walls_ensured_other"
}

def execute(filters=None):
    selected_category = filters.get("safety_indicators", "1")
    
    # Fixed columns with visit and creche information
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

    # All safety indicators questions organized by categories
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

    # Get questions for selected category
    questions = categories.get(selected_category, categories["1"])

    # Dynamic columns for selected questions
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
    
    # Add total row if there's data
    if data:
        total_row = {"partner": "<b>Total</b>"}
        
        # For each question field, count occurrences of Yes, No, Not Observed, and Other
        for q in questions:
            field = q["field"]
            yes_count = sum(1 for row in data if str(row.get(field, '')) == 'Yes')
            no_count = sum(1 for row in data if str(row.get(field, '')) == 'No')
            not_observed_count = sum(1 for row in data if str(row.get(field, '')) == 'Not Observed')
            other_count = sum(1 for row in data if str(row.get(field, '')).startswith('Other'))
            
            # Format the total cell with summary
            total_row[field] = format_total_cell(yes_count, no_count, not_observed_count, other_count)
        
        data.append(total_row)
    
    # Apply conditional formatting to show Yes/No/Not Observed/Other/N/A with colors
    data = apply_conditional_formatting(data, questions)
    
    return columns, data

def get_report_data(filters, questions):
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year

    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

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

    # Build the SELECT clause for selected questions only
    question_fields = []
    for q in questions:
        field = q["field"]
        # Determine the name of the `_other` field
        other_field = OTHER_FIELDS_MAP.get(field, f"{field}_other")
        
        # Convert numeric values to readable text, including mapping value 4 to "Other: [Text]"
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

    # Main query to get individual visit records 
    # [FIX] Added u.full_name AS user, u.type AS designation, and tabUser u JOIN
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

    # Add filters
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
        
    # [FIX] Added User Filter
    if filters.get("user"):
        query += " AND si.owner = %(user)s"
        params["user"] = filters.get("user")

    # [FIX] Added Designation Filter
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

    # Add creche_age filter
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

def apply_conditional_formatting(data, questions):
    """Apply colors to Yes/No/Not Observed/Other/N/A values"""
    
    for row in data:
        # Skip formatting for total row
        if row.get("partner") == "<b>Total</b>":
            continue
            
        for q in questions:
            field = q["field"]
            value = str(row.get(field, ''))
            
            if value == 'Yes':
                row[field] = format_cell(value, "#CCFFCC", "#006600")  # Green
            elif value == 'No':
                row[field] = format_cell(value, "#FFCCCC", "#CC0000")  # Red
            elif value == 'Not Observed':
                row[field] = format_cell(value, "#FFFFCC", "#999900")  # Yellow
            elif value.startswith('Other'):
                row[field] = format_cell(value, "#FFE5CC", "#CC6600")  # Orange (for Other)
            elif value in ('-', 'N/A'):
                row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
    
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
    """Format the total cell with horizontal counts for all statuses"""
    
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















# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# # Mapping of specific fields where the `_other` suffix does not perfectly match the field name
# OTHER_FIELDS_MAP = {
#     "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche": "edge_cutters_or_machinery_kept_away_from_the_creche_other",
#     "is_the_structural_safety_of_the_creches_roof_and_walls_ensured": "structural_safety_of_the_creches_roof_and_walls_ensured_other"
# }

# def execute(filters=None):
#     selected_category = filters.get("safety_indicators", "1")
    
#     # Fixed columns with visit and creche information
#     fixed_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 180},
#         {"label": "Date of Visit", "fieldname": "date_of_visit", "fieldtype": "Date", "width": 120},
#     ]

#     # All safety indicators questions organized by categories
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
#             {"field": "positioned_above_cylinder_height", "label": "Is there a separate slab or table for the gas stove positioned above cylinder height?"},
#             {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#             {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#             {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
#             {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#             {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#             {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#             {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
#             {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#             {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
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
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     # Get questions for selected category
#     questions = categories.get(selected_category, categories["1"])

#     # Dynamic columns for selected questions
#     dynamic_columns = []
#     for q in questions:
#         dynamic_columns.append({
#             "label": q["label"], 
#             "fieldname": q["field"], 
#             "fieldtype": "Data", 
#             "width": 500
#         })

#     columns = fixed_columns + dynamic_columns
#     data = get_report_data(filters, questions)
    
#     # Add total row if there's data
#     if data:
#         total_row = {"partner": "<b>Total</b>"}
        
#         # For each question field, count occurrences of Yes, No, Not Observed, and Other
#         for q in questions:
#             field = q["field"]
#             yes_count = sum(1 for row in data if str(row.get(field, '')) == 'Yes')
#             no_count = sum(1 for row in data if str(row.get(field, '')) == 'No')
#             not_observed_count = sum(1 for row in data if str(row.get(field, '')) == 'Not Observed')
#             other_count = sum(1 for row in data if str(row.get(field, '')).startswith('Other'))
            
#             # Format the total cell with summary
#             total_row[field] = format_total_cell(yes_count, no_count, not_observed_count, other_count)
        
#         data.append(total_row)
    
#     # Apply conditional formatting to show Yes/No/Not Observed/Other/N/A with colors
#     data = apply_conditional_formatting(data, questions)
    
#     return columns, data

# def get_report_data(filters, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

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

#     # Build the SELECT clause for selected questions only
#     question_fields = []
#     for q in questions:
#         field = q["field"]
#         # Determine the name of the `_other` field
#         other_field = OTHER_FIELDS_MAP.get(field, f"{field}_other")
        
#         # Convert numeric values to readable text, including mapping value 4 to "Other: [Text]"
#         question_fields.append(f"""
#             CASE 
#                 WHEN si.{field} = 1 THEN 'Yes'
#                 WHEN si.{field} = 2 THEN 'No'
#                 WHEN si.{field} = 3 THEN 'Not Observed'
#                 WHEN si.{field} = 4 THEN CONCAT('Other: ', COALESCE(si.{other_field}, ''))
#                 ELSE 'N/A'
#             END AS {field}
#         """)

#     question_select = ",\n".join(question_fields) if question_fields else ""

#     # Main query to get individual visit records
#     query = f"""
#     SELECT
#         si.date_of_visit,
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block,
#         g.gp_name AS gp,
#         sup.full_name AS supervisor,
#         cr.creche_name AS creche,
#         cr.creche_id AS creche_id,
#         cr.creche_opening_date AS cr_open_date,
#         {question_select}
#     FROM `tabSafety Indicators` si
#     INNER JOIN `tabCreche` cr ON cr.name = si.creche_id
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     WHERE si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     """

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     # Add filters
#     if partner_id:
#         query += " AND cr.partner_id = %(partner)s"
#         params["partner"] = partner_id
    
#     if filters.get("state"):
#         query += " AND cr.state_id = %(state)s"
#         params["state"] = filters.get("state")
#     elif state_ids:
#         query += " AND cr.state_id IN %(state_ids)s"
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     if filters.get("district"):
#         query += " AND cr.district_id = %(district)s"
#         params["district"] = filters.get("district")
#     elif district_ids:
#         query += " AND cr.district_id IN %(district_ids)s"
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     if filters.get("block"):
#         query += " AND cr.block_id = %(block)s"
#         params["block"] = filters.get("block")
#     elif block_ids:
#         query += " AND cr.block_id IN %(block_ids)s"
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     if filters.get("gp"):
#         query += " AND cr.gp_id = %(gp)s"
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         query += " AND cr.gp_id IN %(gp_ids)s"
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     if filters.get("creche"):
#         query += " AND cr.name = %(creche)s"
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         query += " AND cr.supervisor_id = %(supervisor_id)s"
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         query += " AND cr.creche_status_id = %(creche_status_id)s"
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             query += " AND cr.phase IN %(phases)s"
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         query += " AND cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     # Add creche_age filter
#     creche_age = filters.get("creche_age", "")
#     params["creche_age"] = creche_age
#     if creche_age:
#         query += """
#             AND (
#                 CASE
#                     WHEN cr.creche_opening_date IS NULL THEN ''
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
#                     ELSE ''
#                 END = %(creche_age)s
#             )
#         """

#     query += " ORDER BY si.date_of_visit DESC, p.partner_name, s.state_name, d.district_name"

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
            
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
#         data = []

#     return data

# def apply_conditional_formatting(data, questions):
#     """Apply colors to Yes/No/Not Observed/Other/N/A values"""
    
#     for row in data:
#         # Skip formatting for total row
#         if row.get("partner") == "<b>Total</b>":
#             continue
            
#         for q in questions:
#             field = q["field"]
#             value = str(row.get(field, ''))
            
#             if value == 'Yes':
#                 row[field] = format_cell(value, "#CCFFCC", "#006600")  # Green
#             elif value == 'No':
#                 row[field] = format_cell(value, "#FFCCCC", "#CC0000")  # Red
#             elif value == 'Not Observed':
#                 row[field] = format_cell(value, "#FFFFCC", "#999900")  # Yellow
#             elif value.startswith('Other'):
#                 row[field] = format_cell(value, "#FFE5CC", "#CC6600")  # Orange (for Other)
#             elif value in ('-', 'N/A'):
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
    
#     return data

# def format_cell(value, bg_color, text_color):
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 5px 10px;
#         '>
#             {value}
#         </div>
#     """

# def format_total_cell(yes_count, no_count, not_observed_count, other_count):
#     """Format the total cell with horizontal counts for all statuses"""
    
#     return f"""
#         <div style='
#             background-color: #E6F3FF;
#             border-radius: 3px;
#             padding: 8px 5px;
#             font-size: 13px;
#             text-align: center;
#             white-space: nowrap;
#         '>
#             <span style='color: #006600;'><b>Yes:</b> {yes_count}</span> <span style='color: #666;'>||</span> 
#             <span style='color: #CC0000;'><b>No:</b> {no_count}</span> <span style='color: #666;'>||</span> 
#             <span style='color: #999900;'><b>Not Observed:</b> {not_observed_count}</span> <span style='color: #666;'>||</span> 
#             <span style='color: #CC6600;'><b>Other:</b> {other_count}</span>
#         </div>
#     """




















# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_category = filters.get("safety_indicators", "1")
    
#     # Fixed columns with visit and creche information
#     fixed_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 180},
#         {"label": "Date of Visit", "fieldname": "date_of_visit", "fieldtype": "Date", "width": 120},
#     ]

#     # All safety indicators questions organized by categories
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
#             {"field": "positioned_above_cylinder_height", "label": "Is there a separate slab or table for the gas stove positioned above cylinder height?"},
#             {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#             {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#             {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
#             {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#             {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#             {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#             {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
#             {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#             {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
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
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     # Get questions for selected category
#     questions = categories.get(selected_category, categories["1"])

#     # Dynamic columns for selected questions
#     dynamic_columns = []
#     for q in questions:
#         dynamic_columns.append({
#             "label": q["label"], 
#             "fieldname": q["field"], 
#             "fieldtype": "Data", 
#             "width": 500
#         })

#     columns = fixed_columns + dynamic_columns
#     data = get_report_data(filters, questions)
    
#     # Add total row if there's data
#     if data:
#         total_row = {"partner": "<b>Total</b>"}
        
#         # For each question field, count occurrences of Yes, No, Not Observed
#         for q in questions:
#             field = q["field"]
#             yes_count = sum(1 for row in data if row.get(field) == 'Yes')
#             no_count = sum(1 for row in data if row.get(field) == 'No')
#             not_observed_count = sum(1 for row in data if row.get(field) == 'Not Observed')
            
#             # Format the total cell with summary
#             total_row[field] = format_total_cell(yes_count, no_count, not_observed_count)
        
#         data.append(total_row)
    
#     # Apply conditional formatting to show Yes/No/Not Observed/N/A with colors
#     data = apply_conditional_formatting(data, questions)
    
#     return columns, data

# def get_report_data(filters, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

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

#     # Build the SELECT clause for selected questions only
#     question_fields = []
#     for q in questions:
#         field = q["field"]
#         # Convert numeric values to readable text
#         question_fields.append(f"""
#             CASE 
#                 WHEN si.{field} = 1 THEN 'Yes'
#                 WHEN si.{field} = 2 THEN 'No'
#                 WHEN si.{field} = 3 THEN 'Not Observed'
#                 ELSE 'N/A'
#             END AS {field}
#         """)

#     question_select = ",\n".join(question_fields) if question_fields else ""

#     # Main query to get individual visit records
#     query = f"""
#     SELECT
#         si.date_of_visit,
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block,
#         g.gp_name AS gp,
#         sup.full_name AS supervisor,
#         cr.creche_name AS creche,
#         cr.creche_id AS creche_id,
#         cr.creche_opening_date AS cr_open_date,
#         {question_select}
#     FROM `tabSafety Indicators` si
#     INNER JOIN `tabCreche` cr ON cr.name = si.creche_id
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     WHERE si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     """

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     # Add filters
#     if partner_id:
#         query += " AND cr.partner_id = %(partner)s"
#         params["partner"] = partner_id
    
#     if filters.get("state"):
#         query += " AND cr.state_id = %(state)s"
#         params["state"] = filters.get("state")
#     elif state_ids:
#         query += " AND cr.state_id IN %(state_ids)s"
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     if filters.get("district"):
#         query += " AND cr.district_id = %(district)s"
#         params["district"] = filters.get("district")
#     elif district_ids:
#         query += " AND cr.district_id IN %(district_ids)s"
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     if filters.get("block"):
#         query += " AND cr.block_id = %(block)s"
#         params["block"] = filters.get("block")
#     elif block_ids:
#         query += " AND cr.block_id IN %(block_ids)s"
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     if filters.get("gp"):
#         query += " AND cr.gp_id = %(gp)s"
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         query += " AND cr.gp_id IN %(gp_ids)s"
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     if filters.get("creche"):
#         query += " AND cr.name = %(creche)s"
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         query += " AND cr.supervisor_id = %(supervisor_id)s"
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         query += " AND cr.creche_status_id = %(creche_status_id)s"
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             query += " AND cr.phase IN %(phases)s"
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         query += " AND cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     # Add creche_age filter
#     creche_age = filters.get("creche_age", "")
#     params["creche_age"] = creche_age
#     if creche_age:
#         query += """
#             AND (
#                 CASE
#                     WHEN cr.creche_opening_date IS NULL THEN ''
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                     WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
#                     ELSE ''
#                 END = %(creche_age)s
#             )
#         """

#     query += " ORDER BY si.date_of_visit DESC, p.partner_name, s.state_name, d.district_name"

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
            
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
#         data = []

#     return data

# def apply_conditional_formatting(data, questions):
#     """Apply colors to Yes/No/Not Observed/N/A values"""
    
#     for row in data:
#         # Skip formatting for total row
#         if row.get("partner") == "<b>Total</b>":
#             continue
            
#         for q in questions:
#             field = q["field"]
#             value = row.get(field)
            
#             if value == 'Yes':
#                 row[field] = format_cell(value, "#CCFFCC", "#006600")  # Green
#             elif value == 'No':
#                 row[field] = format_cell(value, "#FFCCCC", "#CC0000")  # Red
#             elif value == 'Not Observed':
#                 row[field] = format_cell(value, "#FFFFCC", "#999900")  # Yellow
#             elif value == '-':
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
#             elif value == 'N/A':
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
    
#     return data

# def format_cell(value, bg_color, text_color):
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 5px 10px;
#         '>
#             {value}
#         </div>
#     """

# def format_total_cell(yes_count, no_count, not_observed_count):
#     """Format the total cell with counts for Yes, No, and Not Observed"""
#     total = yes_count + no_count + not_observed_count
    
#     return f"""
#         <div style='
#             background-color: #E6F3FF;
#             border-radius: 3px;
#             padding: 5px;
#             font-size: 12px;
#         '>
#             <div style='color: #006600;'><b>Yes:</b> {yes_count}</div>
#             <div style='color: #CC0000;'><b>No:</b> {no_count}</div>
#             <div style='color: #999900;'><b>Not Observed:</b> {not_observed_count}</div>
#             <div style='border-top: 1px solid #99CCFF; margin-top: 3px; padding-top: 3px; color: #0066CC;'><b>Total:</b> {total}</div>
#         </div>
#     """










#backup Before age of creche Filter
# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_category = filters.get("safety_indicators", "1")
    
#     # Fixed columns with visit and creche information
#     fixed_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 180},
#         {"label": "Date of Visit", "fieldname": "date_of_visit", "fieldtype": "Date", "width": 120},
#     ]

#     # All safety indicators questions organized by categories
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
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     # Get questions for selected category
#     questions = categories.get(selected_category, categories["1"])

#     # Dynamic columns for selected questions
#     dynamic_columns = []
#     for q in questions:
#         dynamic_columns.append({
#             "label": q["label"], 
#             "fieldname": q["field"], 
#             "fieldtype": "Data", 
#             "width": 500
#         })

#     columns = fixed_columns + dynamic_columns
#     data = get_report_data(filters, questions)
    
#     # Add total row if there's data
#     if data:
#         total_row = {"partner": "<b>Total</b>"}
        
#         # For each question field, count occurrences of Yes, No, Not Observed
#         for q in questions:
#             field = q["field"]
#             yes_count = sum(1 for row in data if row.get(field) == 'Yes')
#             no_count = sum(1 for row in data if row.get(field) == 'No')
#             not_observed_count = sum(1 for row in data if row.get(field) == 'Not Observed')
            
#             # Format the total cell with summary
#             total_row[field] = format_total_cell(yes_count, no_count, not_observed_count)
        
#         data.append(total_row)
    
#     # Apply conditional formatting to show Yes/No/Not Observed/N/A with colors
#     data = apply_conditional_formatting(data, questions)
    
#     return columns, data

# def get_report_data(filters, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

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

#     # Build the SELECT clause for selected questions only
#     question_fields = []
#     for q in questions:
#         field = q["field"]
#         # Convert numeric values to readable text
#         question_fields.append(f"""
#             CASE 
#                 WHEN si.{field} = 1 THEN 'Yes'
#                 WHEN si.{field} = 2 THEN 'No'
#                 WHEN si.{field} = 3 THEN 'Not Observed'
#                 ELSE 'N/A'
#             END AS {field}
#         """)

#     question_select = ",\n".join(question_fields) if question_fields else ""

#     # Main query to get individual visit records
#     query = f"""
#     SELECT
#         si.date_of_visit,
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block,
#         g.gp_name AS gp,
#         sup.full_name AS supervisor,
#         cr.creche_name AS creche,
#         cr.creche_id AS creche_id,
#         cr.creche_opening_date AS cr_open_date,
#         {question_select}
#     FROM `tabSafety Indicators` si
#     INNER JOIN `tabCreche` cr ON cr.name = si.creche_id
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     WHERE si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     """

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     # Add filters
#     if partner_id:
#         query += " AND cr.partner_id = %(partner)s"
#         params["partner"] = partner_id
    
#     if filters.get("state"):
#         query += " AND cr.state_id = %(state)s"
#         params["state"] = filters.get("state")
#     elif state_ids:
#         query += " AND cr.state_id IN %(state_ids)s"
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     if filters.get("district"):
#         query += " AND cr.district_id = %(district)s"
#         params["district"] = filters.get("district")
#     elif district_ids:
#         query += " AND cr.district_id IN %(district_ids)s"
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     if filters.get("block"):
#         query += " AND cr.block_id = %(block)s"
#         params["block"] = filters.get("block")
#     elif block_ids:
#         query += " AND cr.block_id IN %(block_ids)s"
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     if filters.get("gp"):
#         query += " AND cr.gp_id = %(gp)s"
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         query += " AND cr.gp_id IN %(gp_ids)s"
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     if filters.get("creche"):
#         query += " AND cr.name = %(creche)s"
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         query += " AND cr.supervisor_id = %(supervisor_id)s"
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         query += " AND cr.creche_status_id = %(creche_status_id)s"
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             query += " AND cr.phase IN %(phases)s"
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         query += " AND cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     query += " ORDER BY si.date_of_visit DESC, p.partner_name, s.state_name, d.district_name"

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
            
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
#         data = []

#     return data

# def apply_conditional_formatting(data, questions):
#     """Apply colors to Yes/No/Not Observed/N/A values"""
    
#     for row in data:
#         # Skip formatting for total row
#         if row.get("partner") == "<b>Total</b>":
#             continue
            
#         for q in questions:
#             field = q["field"]
#             value = row.get(field)
            
#             if value == 'Yes':
#                 row[field] = format_cell(value, "#CCFFCC", "#006600")  # Green
#             elif value == 'No':
#                 row[field] = format_cell(value, "#FFCCCC", "#CC0000")  # Red
#             elif value == 'Not Observed':
#                 row[field] = format_cell(value, "#FFFFCC", "#999900")  # Yellow
#             elif value == '-':
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
#             elif value == 'N/A':
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
    
#     return data

# def format_cell(value, bg_color, text_color):
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 5px 10px;
#         '>
#             {value}
#         </div>
#     """

# def format_total_cell(yes_count, no_count, not_observed_count):
#     """Format the total cell with counts for Yes, No, and Not Observed"""
#     total = yes_count + no_count + not_observed_count
    
#     return f"""
#         <div style='
#             background-color: #E6F3FF;
#             border-radius: 3px;
#             padding: 5px;
#             font-size: 12px;
#         '>
#             <div style='color: #006600;'><b>Yes:</b> {yes_count}</div>
#             <div style='color: #CC0000;'><b>No:</b> {no_count}</div>
#             <div style='color: #999900;'><b>Not Observed:</b> {not_observed_count}</div>
#             <div style='border-top: 1px solid #99CCFF; margin-top: 3px; padding-top: 3px; color: #0066CC;'><b>Total:</b> {total}</div>
#         </div>
#     """
















# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     selected_category = filters.get("safety_indicators", "1")
    
#     # Fixed columns with visit and creche information
#     fixed_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 180},
#         {"label": "Date of Visit", "fieldname": "date_of_visit", "fieldtype": "Date", "width": 120},
#     ]

#     # All safety indicators questions organized by categories
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
#             {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
#             {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
#         ],
#         "6": [
#             {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#             {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#             {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#         ],
#     }

#     # Get questions for selected category
#     questions = categories.get(selected_category, categories["1"])

#     # Dynamic columns for selected questions
#     dynamic_columns = []
#     for q in questions:
#         dynamic_columns.append({
#             "label": q["label"], 
#             "fieldname": q["field"], 
#             "fieldtype": "Data", 
#             "width": 500
#         })

#     columns = fixed_columns + dynamic_columns
#     data = get_report_data(filters, questions)
    
#     # Add total row if there's data
#     if data:
#         total_row = {"partner": "<b>Total</b>"}
        
#         # For each question field, count occurrences of Yes, No, Not Observed
#         for q in questions:
#             field = q["field"]
#             yes_count = sum(1 for row in data if row.get(field) == 'Yes')
#             no_count = sum(1 for row in data if row.get(field) == 'No')
#             not_observed_count = sum(1 for row in data if row.get(field) == 'Not Observed')
            
#             # Format the total cell with summary
#             total_row[field] = format_total_cell(yes_count, no_count, not_observed_count)
        
#         data.append(total_row)
    
#     # Apply conditional formatting to show Yes/No/Not Observed with colors
#     data = apply_conditional_formatting(data, questions)
    
#     return columns, data

# def get_report_data(filters, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

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

#     # Build the SELECT clause for selected questions only
#     question_fields = []
#     for q in questions:
#         field = q["field"]
#         # Convert numeric values to readable text
#         question_fields.append(f"""
#             CASE 
#                 WHEN si.{field} = 1 THEN 'Yes'
#                 WHEN si.{field} = 2 THEN 'No'
#                 WHEN si.{field} = 3 THEN 'Not Observed'
#                 ELSE 'N/A'
#             END AS {field}
#         """)

#     question_select = ",\n".join(question_fields) if question_fields else ""

#     # Main query to get individual visit records
#     query = f"""
#     SELECT
#         si.date_of_visit,
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block,
#         g.gp_name AS gp,
#         sup.full_name AS supervisor,
#         cr.creche_name AS creche,
#         cr.creche_id AS creche_id,
#         cr.creche_opening_date AS cr_open_date,
#         {question_select}
#     FROM `tabSafety Indicators` si
#     INNER JOIN `tabCreche` cr ON cr.name = si.creche_id
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     WHERE si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     """

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     # Add filters
#     if partner_id:
#         query += " AND cr.partner_id = %(partner)s"
#         params["partner"] = partner_id
    
#     if filters.get("state"):
#         query += " AND cr.state_id = %(state)s"
#         params["state"] = filters.get("state")
#     elif state_ids:
#         query += " AND cr.state_id IN %(state_ids)s"
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     if filters.get("district"):
#         query += " AND cr.district_id = %(district)s"
#         params["district"] = filters.get("district")
#     elif district_ids:
#         query += " AND cr.district_id IN %(district_ids)s"
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     if filters.get("block"):
#         query += " AND cr.block_id = %(block)s"
#         params["block"] = filters.get("block")
#     elif block_ids:
#         query += " AND cr.block_id IN %(block_ids)s"
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     if filters.get("gp"):
#         query += " AND cr.gp_id = %(gp)s"
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         query += " AND cr.gp_id IN %(gp_ids)s"
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     if filters.get("creche"):
#         query += " AND cr.name = %(creche)s"
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         query += " AND cr.supervisor_id = %(supervisor_id)s"
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         query += " AND cr.creche_status_id = %(creche_status_id)s"
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             query += " AND cr.phase IN %(phases)s"
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         query += " AND cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     query += " ORDER BY si.date_of_visit DESC, p.partner_name, s.state_name, d.district_name"

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
            
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
#         data = []

#     return data

# def apply_conditional_formatting(data, questions):
#     """Apply colors to Yes/No/Not Observed values"""
    
#     for row in data:
#         # Skip formatting for total row
#         if row.get("partner") == "<b>Total</b>":
#             continue
            
#         for q in questions:
#             field = q["field"]
#             value = row.get(field)
            
#             if value == 'Yes':
#                 row[field] = format_cell(value, "#CCFFCC", "#006600")  # Green
#             elif value == 'No':
#                 row[field] = format_cell(value, "#FFCCCC", "#CC0000")  # Red
#             elif value == 'Not Observed':
#                 row[field] = format_cell(value, "#FFFFCC", "#999900")  # Yellow
#             elif value == '-':
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
    
#     return data

# def format_cell(value, bg_color, text_color):
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 5px 10px;
#         '>
#             {value}
#         </div>
#     """

# def format_total_cell(yes_count, no_count, not_observed_count):
#     """Format the total cell with counts for Yes, No, and Not Observed"""
#     total = yes_count + no_count + not_observed_count
    
#     return f"""
#         <div style='
#             background-color: #E6F3FF;
#             border-radius: 3px;
#             padding: 5px;
#             font-size: 12px;
#         '>
#             <div style='color: #006600;'><b>Yes:</b> {yes_count}</div>
#             <div style='color: #CC0000;'><b>No:</b> {no_count}</div>
#             <div style='color: #999900;'><b>Not Observed:</b> {not_observed_count}</div>
#             <div style='border-top: 1px solid #99CCFF; margin-top: 3px; padding-top: 3px; color: #0066CC;'><b>Total:</b> {total}</div>
#         </div>
#     """














# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     # Fixed columns with visit and creche information
#     fixed_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#         {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche Opening Date", "fieldname": "cr_open_date", "fieldtype": "Date", "width": 180},
#         {"label": "Date of Visit", "fieldname": "date_of_visit", "fieldtype": "Date", "width": 120},
#     ]

#     # All safety indicators questions from all categories
#     all_questions = [
#         # Category 1: Infrastructural & Environmental Safety
#         {"field": "is_the_structural_safety_of_the_creches_roof_and_walls_ensured", "label": "Is the structural safety of the creche's roof and walls ensured?"},
#         {"field": "is_the_creche_protected_from_rainwater_leakage", "label": "Is the creche protected from rainwater leakage?"},
#         {"field": "is_any_welltube_well_within_20_m_radius_of_the_creche", "label": "Is any well/tube well within 20 m radius of the creche?"},
#         {"field": "properly_covered_with_iron_net_inside_out_side", "label": "If yes is it properly covered with an iron net (inside & outside)?"},
#         {"field": "are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche", "label": "Are sharp edge cutters or machinery kept away from the creche?"},
        
#         # Category 2: Physical Safety & Security
#         {"field": "external_fencing_around", "label": "Is there external fencing around the creche?"},
#         {"field": "safety_the_main_entrance", "label": "Is there a safety gate at the main entrance?"},
#         {"field": "safety_gate_kitchen_entrance", "label": "Is there a safety gate at the kitchen entrance?"},
#         {"field": "creche_secured_against_animals", "label": "Is the creche secured against the entry of poisonous animals (snakes, scorpions) as well as domestic animals (dogs, cats, cows, hens)?"},
#         {"field": "parents_recorded_visitor_register", "label": "Is the entry of any person other than parents in the creche recorded in the visitor’s register?"},
        
#         # Category 3: Fire Safety
#         {"field": "positioned_above_cylinder_height", "label": "Is there a separate slab or table for the gas stove positioned above cylinder height?"},
#         {"field": "fire_extinguisher_available_working_condition", "label": "Is a fire extinguisher available and in working condition?"},
#         {"field": "kitchen_fire_related_emergencies", "label": "Are fire blankets and fire buckets available in the kitchen for fire related emergencies?"},
#         {"field": "confident_handling_pressure_cooker", "label": "Is the caregiver confident in handling a pressure cooker?"},
        
#         # Category 4: Electrical Safety
#         {"field": "electrical_connections_positioned_out_children_reach", "label": "Are all electrical connections positioned out of children's reach?"},
#         {"field": "fans_and_lights_installed_safe_location_height", "label": "Are fans and lights installed at a safe location and height?"},
#         {"field": "solar_batteries_kept_out_children_reach", "label": "Are solar panels or batteries kept out of children’s reach?"},
#         {"field": "lightening_installed_creche", "label": "Is lightening arrestors installed in the creche building"},
        
#         # Category 5: Food Safety
#         {"field": "food_utilized_first_out_manner", "label": "Are food grains and rice utilized in first come first out manner?"},
#         {"field": "egg_floating_tests_doneperiodically_check_quality_eggs", "label": "Are egg floating tests done periodically to check the quality of eggs?"},
#         {"field": "is_leftover_food_disposed_of_properly_every_day", "label": "Is leftover food disposed of properly every day?"},
#         {"field": "water_filter_being_safe_drinking_water", "label": "Is water filter being used for safe drinking water?"},
        
#         # Category 6: Others
#         {"field": "creche_running_two_caregivers", "label": "During your visit, is the creche running with two caregivers?"},
#         {"field": "first_aid_available_creche", "label": "Is a fully equipped first-aid box available in the creche?"},
#         {"field": "emergency_contact_numbers_clearly_displayed", "label": "Are emergency contact numbers clearly displayed?"},
#     ]

#     # Dynamic columns for all questions
#     dynamic_columns = []
#     for q in all_questions:
#         dynamic_columns.append({
#             "label": q["label"], 
#             "fieldname": q["field"], 
#             "fieldtype": "Data", 
#             "width": 500
#         })

#     columns = fixed_columns + dynamic_columns
#     data = get_report_data(filters, all_questions)
    
#     # Apply conditional formatting to show Yes/No/Not Observed with colors
#     data = apply_conditional_formatting(data, all_questions)
    
#     return columns, data

# def get_report_data(filters, questions):
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year

#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

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

#     # Build the SELECT clause for all questions
#     question_fields = []
#     for q in questions:
#         field = q["field"]
#         # Convert numeric values to readable text
#         question_fields.append(f"""
#             CASE 
#                 WHEN si.{field} = 1 THEN 'Yes'
#                 WHEN si.{field} = 2 THEN 'No'
#                 WHEN si.{field} = 3 THEN 'Not Observed'
#                 ELSE '-'
#             END AS {field}
#         """)

#     question_select = ",\n".join(question_fields) if question_fields else ""

#     # Main query to get individual visit records
#     query = f"""
#     SELECT
#         si.date_of_visit,
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block,
#         g.gp_name AS gp,
#         sup.full_name AS supervisor,
#         cr.creche_name AS creche,
#         cr.creche_id AS creche_id,
#         cr.creche_opening_date AS cr_open_date,
#         {question_select}
#     FROM `tabSafety Indicators` si
#     INNER JOIN `tabCreche` cr ON cr.name = si.creche_id
#     INNER JOIN `tabPartner` p ON p.name = cr.partner_id
#     INNER JOIN `tabState` s ON s.name = cr.state_id
#     INNER JOIN `tabDistrict` d ON d.name = cr.district_id
#     INNER JOIN `tabBlock` b ON b.name = cr.block_id
#     INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
#     LEFT JOIN `tabUser` sup ON sup.name = cr.supervisor_id
#     WHERE si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
#     """

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     # Add filters
#     if partner_id:
#         query += " AND cr.partner_id = %(partner)s"
#         params["partner"] = partner_id
    
#     if filters.get("state"):
#         query += " AND cr.state_id = %(state)s"
#         params["state"] = filters.get("state")
#     elif state_ids:
#         query += " AND cr.state_id IN %(state_ids)s"
#         params["state_ids"] = tuple(state_ids) if state_ids else ('',)

#     if filters.get("district"):
#         query += " AND cr.district_id = %(district)s"
#         params["district"] = filters.get("district")
#     elif district_ids:
#         query += " AND cr.district_id IN %(district_ids)s"
#         params["district_ids"] = tuple(district_ids) if district_ids else ('',)

#     if filters.get("block"):
#         query += " AND cr.block_id = %(block)s"
#         params["block"] = filters.get("block")
#     elif block_ids:
#         query += " AND cr.block_id IN %(block_ids)s"
#         params["block_ids"] = tuple(block_ids) if block_ids else ('',)

#     if filters.get("gp"):
#         query += " AND cr.gp_id = %(gp)s"
#         params["gp"] = filters.get("gp")
#     elif gp_ids:
#         query += " AND cr.gp_id IN %(gp_ids)s"
#         params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

#     if filters.get("creche"):
#         query += " AND cr.name = %(creche)s"
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         query += " AND cr.supervisor_id = %(supervisor_id)s"
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         query += " AND cr.creche_status_id = %(creche_status_id)s"
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip().isdigit()]
#         if phases:
#             query += " AND cr.phase IN %(phases)s"
#             params["phases"] = tuple(phases)
    
#     if cstart_date or cend_date:
#         query += " AND cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
#         params["cstart_date"] = cstart_date
#         params["cend_date"] = cend_date

#     query += " ORDER BY si.date_of_visit DESC, p.partner_name, s.state_name, d.district_name"

#     try:
#         data = frappe.db.sql(query, params, as_dict=True)
        
#         if not data:
#             frappe.log_error(f"No data found for query: {query}", "Safety Indicators Report - Individual")
            
#     except Exception as e:
#         frappe.log_error(f"Query error: {str(e)}\nQuery: {query}", "Safety Indicators Report - Individual")
#         data = []

#     return data

# def apply_conditional_formatting(data, questions):
#     """Apply colors to Yes/No/Not Observed values"""
    
#     for row in data:
#         for q in questions:
#             field = q["field"]
#             value = row.get(field)
            
#             if value == 'Yes':
#                 row[field] = format_cell(value, "#CCFFCC", "#006600")  # Green
#             elif value == 'No':
#                 row[field] = format_cell(value, "#FFCCCC", "#CC0000")  # Red
#             elif value == 'Not Observed':
#                 row[field] = format_cell(value, "#FFFFCC", "#999900")  # Yellow
#             elif value == '-':
#                 row[field] = format_cell(value, "#E6E6E6", "#666666")  # Grey
    
#     return data

# def format_cell(value, bg_color, text_color):
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 5px 10px;
#         '>
#             {value}
#         </div>
#     """