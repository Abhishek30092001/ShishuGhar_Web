import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    # Initialize filters with defaults
    selected_level = filters.get("level", "7")
    selected_indicator = filters.get("indicator", "weight_for_age")
    selected_category = filters.get("category", "all")
  
    # Define variable columns based on level
    variable_columns = []
    level_mapping = {
        "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
        "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
        "3": [
            {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
        ],
        "4": [
            {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
        ],
        "5": [
            {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
        ],
        "6": [
            {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
        ],
        "7": [
            {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
            {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
            {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
            {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
        ]
    }
    variable_columns = level_mapping.get(selected_level, level_mapping["7"])
   
    # Get date parameters
    initial_month = int(filters.get("initial_month", 1))
    initial_year = int(filters.get("initial_year", 2023))
    final_month = int(filters.get("final_month", datetime.now().month))
    final_year = int(filters.get("final_year", datetime.now().year))
    month_col_heading = calendar.month_name[int(initial_month)]
   
    # Define fixed columns
    fixed_columns = [
        {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 175},
        {"label": f"Active children till ({month_col_heading}/{initial_year})",
         "fieldname": "enrolled_children", "fieldtype": "Int", "width": 280},
        {"label": f"Measurements taken ({month_col_heading}/{initial_year})",
         "fieldname": "measurements_taken", "fieldtype": "Int", "width": 280},
        {"label": f"Exited ({month_col_heading}/{initial_year} - {calendar.month_name[final_month]}/{final_year})",
         "fieldname": "exited_children", "fieldtype": "Int", "width": 280}
    ]
   
    # Add transition columns with percentage display
    transition_columns = {
        "all": [
            {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 170},
            {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 170},
            {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 170},
            {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 170},
            {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 170},
            {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 170},
        ],
        "normal": [
            {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 170},
            {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 170},
        ],
        "moderate": [
            {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 170},
            {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 170},
        ],
        "severe": [
            {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 170},
            {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 170},
        ]
    }
    fixed_columns.extend(transition_columns.get(selected_category, []))
   
    # Add No Change breakdown columns
    no_change_columns = [
        {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 270},
        {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 270},
        {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 270}
    ]
    fixed_columns.extend(no_change_columns)
   
    # Add common columns
    fixed_columns.extend([
        {"label": f"Measurements Not Available ({calendar.month_name[final_month]}/{final_year})",
         "fieldname": "measurements_data_not_available", "fieldtype": "Int", "width": 280}
    ])
   
    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
   
    # Process data to add percentage display and calculate totals
    totals = {
        'operational_creches': 0,
        'enrolled_children': 0,
        'measurements_taken': 0,
        'exited_children': 0,
        'md_nr_cnt': 0,
        'sv_nr_cnt': 0,
        'sv_md_cnt': 0,
        'nr_md_cnt': 0,
        'md_sv_cnt': 0,
        'nr_sv_cnt': 0,
        'sv_sv_cnt': 0,
        'md_md_cnt': 0,
        'nr_nr_cnt': 0,
        'measurements_data_not_available': 0
    }
   
    for row in data:
        # Calculate percentages and create display strings for transition columns
        measurements_taken = row.get('measurements_taken', 0)
       
        if measurements_taken > 0:
            for field in ['md_nr', 'sv_nr', 'sv_md', 'nr_md', 'md_sv', 'nr_sv', 'sv_sv', 'md_md', 'nr_nr']:
                cnt = row.get(f'{field}_cnt', 0)
                percent = round((cnt / measurements_taken) * 100, 2) if measurements_taken > 0 else 0
                row[f'{field}_display'] = f"{int(cnt)} ({percent:.2f}%)"
        else:
            for field in ['md_nr', 'sv_nr', 'sv_md', 'nr_md', 'md_sv', 'nr_sv', 'sv_sv', 'md_md', 'nr_nr']:
                row[f'{field}_display'] = "0 (0.00%)"
       
        # Sum up for totals
        for key in totals:
            if key in row:
                totals[key] += row.get(key, 0)
   
    # Add totals row
    if data:
        totals_row = {'is_total': True, 'indent': 0}
        level_field_map = {
            "1": "partner","2": "state","3": "district","4": "block","5": "supervisor_id","6": "gp","7": "partner"
        }

        if selected_level in level_field_map:
            totals_row[level_field_map[selected_level]] = "Total"
        else:
            for col in variable_columns:
                totals_row[col['fieldname']] = "Total"

       
        for key in totals:
            if key.endswith('_cnt'):
                # Handle transition counts with percentages
                total_percent = round((totals[key] / totals['measurements_taken']) * 100, 2) if totals['measurements_taken'] > 0 else 0
                display_key = key.replace('_cnt', '_display')
                totals_row[display_key] = f"{int(totals[key])} ({total_percent:.2f}%)"
            else:
                totals_row[key] = totals[key]
       
        data.append(totals_row)
   
    return columns, data

def get_report_data(filters):
    # Optimized query building with parameter handling
    params = build_query_params(filters)
    query = build_main_query(filters, params)
   
    try:
        data = frappe.db.sql(query, params, as_dict=True)
       
        # Calculate measurements not available
        for row in data:
            measured = row.get('measurements_taken', 0)
            transitions_sum = sum([
                row.get('sv_md_cnt', 0),
                row.get('md_nr_cnt', 0),
                row.get('sv_nr_cnt', 0),
                row.get('nr_md_cnt', 0),
                row.get('md_sv_cnt', 0),
                row.get('nr_sv_cnt', 0),
                row.get('sv_sv_cnt', 0),
                row.get('md_md_cnt', 0),
                row.get('nr_nr_cnt', 0)
            ])
            row['measurements_data_not_available'] = max(0, measured - transitions_sum)
       
        return data
    except Exception as e:
        frappe.log_error(f"Error in Growth Transition Report: {str(e)}")
        return []

def build_query_params(filters):
    # Get user's default partner and geography
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
   
    # Get geography mapping
    geography_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)
   
    # Set date parameters
    initial_month = int(filters.get("initial_month", 1))
    initial_year = int(filters.get("initial_year", 2023))
    final_month = int(filters.get("final_month", datetime.now().month))
    final_year = int(filters.get("final_year", datetime.now().year))
   
    initial_date = date(initial_year, initial_month, 1)
    initial_month_final_date = date(initial_year, initial_month, calendar.monthrange(initial_year, initial_month)[1])
    final_date = date(final_year, final_month, calendar.monthrange(final_year, final_month)[1])
    last_day = calendar.monthrange(initial_year, initial_month)[1]
    initial_last_day = date(initial_year, initial_month, last_day)
   
    # Prepare parameters
    params = {
        "initial_date": initial_date,
        "final_date": final_date,
        "initial_month_final_date": initial_month_final_date,
        "initial_month": initial_month,
        "initial_year": initial_year,
        "final_month": final_month,
        "final_year": final_year,
        "partner": partner_id,
        "state": filters.get("state"),
        "district": filters.get("district"),
        "block": filters.get("block"),
        "gp": filters.get("gp"),
        "creche": filters.get("creche"),
        "supervisor_id": filters.get("supervisor_id"),
        "creche_status_id": filters.get("creche_status_id", "3"),
        "state_ids": [g["state_id"] for g in current_user_geography if g.get("state_id")] or None,
        "district_ids": [g["district_id"] for g in current_user_geography if g.get("district_id")] or None,
        "block_ids": [g["block_id"] for g in current_user_geography if g.get("block_id")] or None,
        "gp_ids": [g["gp_id"] for g in current_user_geography if g.get("gp_id")] or None,
        "phases": None,
        "cstart_date": None,
        "cend_date": None,
        "age_group": filters.get("age_group"),
        "indicator": filters.get("indicator", "weight_for_age"),
        "gender": filters.get("gender"),
        "initial_last_day": initial_last_day
    }
   
    # Handle creche opening date filters
    handle_date_filters(filters, params)
   
    # Handle phases filter
    if filters.get("phases"):
        try:
            phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
            if phases_cleaned:
                params["phases"] = phases_cleaned
        except (AttributeError, TypeError):
            pass
   
    return params

def handle_date_filters(filters, params):
    cr_opening_range_type = filters.get("cr_opening_range_type")
    if cr_opening_range_type == "between":
        c_opening_range = filters.get("c_opening_range", [None, None])
        params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
        params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
    elif cr_opening_range_type in ["before", "after", "equal"]:
        single_date = filters.get("single_date")
        if single_date:
            # Convert string date to datetime.date object
            if isinstance(single_date, str):
                try:
                    single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
                except ValueError:
                    # If parsing fails, use today's date as fallback
                    single_date = date.today()
            
            if cr_opening_range_type == "before":
                params["cstart_date"] = date(2017, 1, 1)
                params["cend_date"] = single_date - timedelta(days=1)
            elif cr_opening_range_type == "after":
                params["cstart_date"] = single_date + timedelta(days=1)
                params["cend_date"] = date.today()
            elif cr_opening_range_type == "equal":
                params["cstart_date"] = single_date
                params["cend_date"] = single_date

def build_main_query(filters, params):
    selected_level = filters.get("level", "7")
    selected_indicator = params["indicator"]
   
    # Define group by fields based on level
    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name", "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
    }
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
   
    # Build SELECT fields
    select_fields = []
    field_map = {
        "p.partner_name": "p.partner_name AS partner",
        "s.state_name": "s.state_name AS state",
        "d.district_name": "d.district_name AS district",
        "b.block_name": "b.block_name AS block",
        "g.gp_name": "g.gp_name AS gp",
        "u.full_name": "u.full_name AS supervisor_id",
        "c.creche_name": "c.creche_name AS creche",
        "c.creche_id": "c.creche_id AS creche_id"
    }
    for field in group_by_fields:
        if field in field_map:
            select_fields.append(field_map[field])
   
    # Add common fields
    select_fields.extend([
        "COUNT(DISTINCT c.name) AS operational_creches",
        "SUM(COALESCE(ec.enrolled_children, 0)) AS enrolled_children",
        "SUM(COALESCE(mt.measurements_taken, 0)) AS measurements_taken",
        "SUM(COALESCE(exited.exited_count, 0)) AS exited_children"
    ])
   
    # Add transition fields
    selected_category = filters.get("category", "all")
    transition_fields = {
        "all": [
            "sv_md_cnt", "md_nr_cnt", "sv_nr_cnt",
            "nr_md_cnt", "md_sv_cnt", "nr_sv_cnt"
        ],
        "normal": ["md_nr_cnt", "sv_nr_cnt"],
        "moderate": ["sv_md_cnt", "nr_md_cnt"],
        "severe": ["md_sv_cnt", "nr_sv_cnt"]
    }
    for field in transition_fields.get(selected_category, []):
        select_fields.append(f"SUM(COALESCE(transitions.{field}, 0)) AS {field}")
   
    # Add no change breakdown fields
    select_fields.extend([
        "SUM(COALESCE(transitions.sv_sv_cnt, 0)) AS sv_sv_cnt",
        "SUM(COALESCE(transitions.md_md_cnt, 0)) AS md_md_cnt",
        "SUM(COALESCE(transitions.nr_nr_cnt, 0)) AS nr_nr_cnt"
    ])
   
    # Build WHERE conditions
    where_conditions = ["1=1"]
    if params["partner"]:
        where_conditions.append("c.partner_id = %(partner)s")
    if params["state"]:
        where_conditions.append("c.state_id = %(state)s")
    elif params["state_ids"]:
        where_conditions.append("c.state_id IN %(state_ids)s")
    if params["district"]:
        where_conditions.append("c.district_id = %(district)s")
    elif params["district_ids"]:
        where_conditions.append("c.district_id IN %(district_ids)s")
    if params["block"]:
        where_conditions.append("c.block_id = %(block)s")
    elif params["block_ids"]:
        where_conditions.append("c.block_id IN %(block_ids)s")
    if params["gp"]:
        where_conditions.append("c.gp_id = %(gp)s")
    elif params["gp_ids"]:
        where_conditions.append("c.gp_id IN %(gp_ids)s")
    if params["creche"]:
        where_conditions.append("c.name = %(creche)s")
    if params["supervisor_id"]:
        where_conditions.append("c.supervisor_id = %(supervisor_id)s")
    if params["creche_status_id"]:
        where_conditions.append("c.creche_status_id = %(creche_status_id)s")
    if params["phases"]:
        where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
   
    where_conditions.extend([
        "(c.creche_opening_date IS NULL OR ( %(initial_last_day)s IS NOT NULL AND c.creche_opening_date <= %(initial_last_day)s ))",
        "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
    ])
   
    # Build GROUP BY and ORDER BY clauses
    group_by_clause = ", ".join(group_by_fields)
    order_by_clause = group_by_clause
   
    # Build the complete query
    query = f"""
    SELECT
        {", ".join(select_fields)}
    FROM `tabCreche` c
    JOIN `tabState` s ON c.state_id = s.name
    JOIN `tabPartner` p ON c.partner_id = p.name
    JOIN `tabDistrict` d ON c.district_id = d.name
    JOIN `tabBlock` b ON c.block_id = b.name
    JOIN `tabGram Panchayat` g ON c.gp_id = g.name
    JOIN `tabUser` AS u ON u.name = c.supervisor_id
   
    -- Enrolled children subquery
    LEFT JOIN (
        SELECT
            cee.creche_id,
            COUNT(*) AS enrolled_children
        FROM `tabChild Enrollment and Exit` cee
        JOIN `tabCreche` cr ON cr.name = cee.creche_id
        WHERE (cee.date_of_enrollment <= %(initial_month_final_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(initial_month_final_date)s))
            AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(initial_month_final_date)s)
            {f"AND cr.partner_id = %(partner)s" if params["partner"] else ""}
            {f"AND cee.state_id = %(state)s" if params["state"] else f"AND cee.state_id IN %(state_ids)s" if params["state_ids"] else ""}
            {f"AND cee.district_id = %(district)s" if params["district"] else f"AND cee.district_id IN %(district_ids)s" if params["district_ids"] else ""}
            {f"AND cee.block_id = %(block)s" if params["block"] else f"AND cee.block_id IN %(block_ids)s" if params["block_ids"] else ""}
            {f"AND cee.gp_id = %(gp)s" if params["gp"] else f"AND cee.gp_id IN %(gp_ids)s" if params["gp_ids"] else ""}
            {f"AND cee.creche_id = %(creche)s" if params["creche"] else ""}
            {f"AND cr.supervisor_id = %(supervisor_id)s" if params["supervisor_id"] else ""}
            {f"AND cr.creche_status_id = %(creche_status_id)s" if params["creche_status_id"] else ""}
            {f"AND cee.gender_id = %(gender)s" if params["gender"] else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 6 AND 11"
            if params.get("age_group") == "6m-11m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 12 AND 17"
            if params.get("age_group") == "12m-17m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 18 AND 23"
            if params.get("age_group") == "18m-23m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 24 AND 29"
            if params.get("age_group") == "24m-29m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 30 AND 36"
            if params.get("age_group") == "30m-36m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) > 36"
            if params.get("age_group") == "> 36m" else ""}
        GROUP BY cee.creche_id
    ) ec ON c.name = ec.creche_id
   
    -- Exited children subquery
    LEFT JOIN (
        SELECT
            creche_id,
            COUNT(*) AS exited_count
        FROM `tabChild Enrollment and Exit` as cee
        WHERE cee.date_of_exit BETWEEN %(initial_date)s AND %(final_date)s
        {f"AND cee.partner_id = %(partner)s" if params["partner"] else ""}
        {f"AND cee.state_id = %(state)s" if params["state"] else f"AND cee.state_id IN %(state_ids)s" if params["state_ids"] else ""}
        {f"AND cee.district_id = %(district)s" if params["district"] else f"AND cee.district_id IN %(district_ids)s" if params["district_ids"] else ""}
        {f"AND cee.block_id = %(block)s" if params["block"] else f"AND cee.block_id IN %(block_ids)s" if params["block_ids"] else ""}
        {f"AND cee.gp_id = %(gp)s" if params["gp"] else f"AND cee.gp_id IN %(gp_ids)s" if params["gp_ids"] else ""}
        {f"AND cee.creche_id = %(creche)s" if params["creche"] else ""}
        {f"AND cee.gender_id = %(gender)s" if params["gender"] else ""}
        {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 6 AND 11"
        if params.get("age_group") == "6m-11m" else ""}
        {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 12 AND 17"
        if params.get("age_group") == "12m-17m" else ""}
        {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 18 AND 23"
        if params.get("age_group") == "18m-23m" else ""}
        {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 24 AND 29"
        if params.get("age_group") == "24m-29m" else ""}
        {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 30 AND 36"
        if params.get("age_group") == "30m-36m" else ""}
        {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) > 36"
        if params.get("age_group") == "> 36m" else ""}
        GROUP BY creche_id
    ) exited ON c.name = exited.creche_id
   
    -- Measurements taken subquery
    LEFT JOIN (
        SELECT
            cgm.creche_id,
            COUNT(ad.chhguid) AS measurements_taken
        FROM `tabAnthropromatic Data` ad
        JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
        JOIN `tabChild Enrollment and Exit` cee ON (
            cee.childenrollguid = ad.childenrollguid
            AND cee.creche_id = cgm.creche_id
            AND ((YEAR(cee.date_of_enrollment) < %(initial_year)s) OR
                (YEAR(cee.date_of_enrollment) = %(initial_year)s AND
                MONTH(cee.date_of_enrollment) <= %(initial_month)s))
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(initial_date)s)
        )
        WHERE
            MONTH(ad.measurement_taken_date) = %(initial_month)s
            AND YEAR(ad.measurement_taken_date) = %(initial_year)s
            {f"AND cgm.partner_id = %(partner)s" if params["partner"] else ""}
            {f"AND cgm.state_id = %(state)s" if params["state"] else f"AND cgm.state_id IN %(state_ids)s" if params["state_ids"] else ""}
            {f"AND cgm.district_id = %(district)s" if params["district"] else f"AND cgm.district_id IN %(district_ids)s" if params["district_ids"] else ""}
            {f"AND cgm.block_id = %(block)s" if params["block"] else f"AND cgm.block_id IN %(block_ids)s" if params["block_ids"] else ""}
            {f"AND cgm.gp_id = %(gp)s" if params["gp"] else f"AND cgm.gp_id IN %(gp_ids)s" if params["gp_ids"] else ""}
            {f"AND cgm.creche_id = %(creche)s" if params["creche"] else ""}
            {f"AND cee.gender_id = %(gender)s" if params["gender"] else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 6 AND 11"
            if params.get("age_group") == "6m-11m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 12 AND 17"
            if params.get("age_group") == "12m-17m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 18 AND 23"
            if params.get("age_group") == "18m-23m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 24 AND 29"
            if params.get("age_group") == "24m-29m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 30 AND 36"
            if params.get("age_group") == "30m-36m" else ""}
            {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) > 36"
            if params.get("age_group") == "> 36m" else ""}
        GROUP BY cgm.creche_id
    ) mt ON c.name = mt.creche_id
   
    -- Transitions subquery
    LEFT JOIN (
        SELECT
            final.creche_id,
            SUM(CASE WHEN initial.{selected_indicator} = 1 AND final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 2 AND final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 1 AND final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 3 AND final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 2 AND final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 3 AND final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 1 AND final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS sv_sv_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 2 AND final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS md_md_cnt,
            SUM(CASE WHEN initial.{selected_indicator} = 3 AND final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS nr_nr_cnt
        FROM (
            SELECT
                cee.creche_id AS creche_id,
                ad.chhguid,
                ad.{selected_indicator},
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
            JOIN `tabChild Enrollment and Exit` cee ON (
                cee.childenrollguid = ad.childenrollguid
                AND cee.creche_id = cgm.creche_id
                AND ((YEAR(cee.date_of_enrollment) < %(initial_year)s) OR
                    (YEAR(cee.date_of_enrollment) = %(initial_year)s AND
                    MONTH(cee.date_of_enrollment) <= %(initial_month)s))
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(initial_date)s)
                {f"AND cee.partner_id = %(partner)s" if params["partner"] else ""}
                {f"AND cee.state_id = %(state)s" if params["state"] else f"AND cee.state_id IN %(state_ids)s" if params["state_ids"] else ""}
                {f"AND cee.district_id = %(district)s" if params["district"] else f"AND cee.district_id IN %(district_ids)s" if params["district_ids"] else ""}
                {f"AND cee.block_id = %(block)s" if params["block"] else f"AND cee.block_id IN %(block_ids)s" if params["block_ids"] else ""}
                {f"AND cee.gp_id = %(gp)s" if params["gp"] else f"AND cee.gp_id IN %(gp_ids)s" if params["gp_ids"] else ""}
                {f"AND cee.creche_id = %(creche)s" if params["creche"] else ""}
                {f"AND cee.gender_id = %(gender)s" if params["gender"] else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 6 AND 11"
                if params.get("age_group") == "6m-11m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 12 AND 17"
                if params.get("age_group") == "12m-17m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 18 AND 23"
                if params.get("age_group") == "18m-23m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 24 AND 29"
                if params.get("age_group") == "24m-29m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 30 AND 36"
                if params.get("age_group") == "30m-36m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) > 36"
                if params.get("age_group") == "> 36m" else ""}
            )
            WHERE
                YEAR(ad.measurement_taken_date) = %(final_year)s
                AND MONTH(ad.measurement_taken_date) = %(final_month)s
        ) final
        JOIN (
            SELECT
                tad.chhguid,
                cee.creche_id,
                tad.{selected_indicator},
                tad.childenrollguid
            FROM `tabChild Growth Monitoring` tcgm
            JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent
            JOIN `tabChild Enrollment and Exit` cee ON (
                cee.childenrollguid = tad.childenrollguid
                AND cee.creche_id = tcgm.creche_id
                AND ((YEAR(cee.date_of_enrollment) < %(initial_year)s) OR
                    (YEAR(cee.date_of_enrollment) = %(initial_year)s AND
                    MONTH(cee.date_of_enrollment) <= %(initial_month)s))
            )
            WHERE
                MONTH(tad.measurement_taken_date) = %(initial_month)s
                AND YEAR(tad.measurement_taken_date) = %(initial_year)s
                {f"AND tcgm.partner_id = %(partner)s" if params["partner"] else ""}
                {f"AND tcgm.state_id = %(state)s" if params["state"] else f"AND tcgm.state_id IN %(state_ids)s" if params["state_ids"] else ""}
                {f"AND tcgm.district_id = %(district)s" if params["district"] else f"AND tcgm.district_id IN %(district_ids)s" if params["district_ids"] else ""}
                {f"AND tcgm.block_id = %(block)s" if params["block"] else f"AND tcgm.block_id IN %(block_ids)s" if params["block_ids"] else ""}
                {f"AND tcgm.gp_id = %(gp)s" if params["gp"] else f"AND tcgm.gp_id IN %(gp_ids)s" if params["gp_ids"] else ""}
                {f"AND tcgm.creche_id = %(creche)s" if params["creche"] else ""}
                {f"AND cee.gender_id = %(gender)s" if params["gender"] else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 6 AND 11"
                if params.get("age_group") == "6m-11m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 12 AND 17"
                if params.get("age_group") == "12m-17m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 18 AND 23"
                if params.get("age_group") == "18m-23m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 24 AND 29"
                if params.get("age_group") == "24m-29m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) BETWEEN 30 AND 36"
                if params.get("age_group") == "30m-36m" else ""}
                {f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(initial_date)s) > 36"
                if params.get("age_group") == "> 36m" else ""}
        ) initial ON final.chhguid = initial.chhguid AND final.creche_id = initial.creche_id
        GROUP BY final.creche_id
    ) transitions ON c.name = transitions.creche_id
    WHERE {" AND ".join(where_conditions)}
    GROUP BY {group_by_clause}
    ORDER BY {order_by_clause}
    """
   
    return query