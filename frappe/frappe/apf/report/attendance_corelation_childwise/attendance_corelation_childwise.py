import frappe
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date

def execute(filters=None):
    columns = get_columns(filters)
    data = get_summary_data(filters)
    data = apply_conditional_formatting(data, filters)
    return columns, data

def get_columns(filters=None):
    month = int(filters.get("month") if filters else date.today().month)
    year = int(filters.get("year") if filters else date.today().year)
    selected_indicator = filters.get("indicator", "weight_for_age") if filters else "weight_for_age"
    duration = filters.get("duration", "12_months") if filters else "12_months"

    # Determine number of months based on duration
    num_months = 12  # default
    if duration == "3_months":
        num_months = 3
    elif duration == "6_months":
        num_months = 6
    elif duration == "12_months":
        num_months = 12

    months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]

    columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
        {"label": "Creche Opening date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 200},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Data", "width": 200},
        {"label": "Age (in month)", "fieldname": "age", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
    ]

    # Define column templates for each indicator - SIMILAR TO FIRST CODE
    indicator_columns = {
        "weight_for_age": [
            ("Weight (kg)", "weight", "Data", 190),
            ("Height (cm)", "height", "Data", 190),
            ("WFA Z-Score", "underweight_status", "Data", 200),
            # ("WFA Status", "weight_for_age_status", "Data", 200)
        ],
        "height_for_age": [
            ("Weight (kg)", "weight", "Data", 190),
            ("Height (cm)", "height", "Data", 190),
            ("HFA Z-Score", "stuning_status", "Data", 200),
            # ("HFA Status", "height_for_age_status", "Data", 220)
        ],
        "weight_for_height": [
            ("Weight (kg)", "weight", "Data", 190),
            ("Height (cm)", "height", "Data", 190),
            ("WFH Z-Score", "wasting_status", "Data", 220),
            # ("WFH Status", "weight_for_height_status", "Data", 220)
        ]
    }
    
    # Get the column templates for the selected indicator
    column_templates = indicator_columns.get(selected_indicator, indicator_columns["weight_for_age"])

    for y, m in months:
        month_name = date(y, m, 1).strftime("%b")  
        year_month = f"{y}_{m:02d}"
        
        # Add attendance column
        columns.append({
            "label": f"Attendance-[{month_name} {y}]",
            "fieldname": f"attendance_percentage_{year_month}",
            "fieldtype": "Data",
            "width": 190,
            "default": "-" 
        })
        
        # Add columns based on the template - SIMILAR TO FIRST CODE'S LOGIC
        for template in column_templates:
            label = f"{template[0]}-[{month_name} {y}]"
            fieldname = f"{template[1]}_{year_month}"
            
            columns.append({
                "label": label,
                "fieldname": fieldname,
                "fieldtype": template[2],
                "width": template[3]
            })
    
    return columns

@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}
    
    # Date range setup
    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    selected_indicator = filters.get("indicator", "weight_for_age")
    selected_category = filters.get("category", "all")
    duration = filters.get("duration", "12_months")
    creche_age = filters.get("creche_age", "")

    # Determine number of months based on duration
    num_months = 12  # default
    if duration == "3_months":
        num_months = 3
    elif duration == "6_months":
        num_months = 6
    elif duration == "12_months":
        num_months = 12

    # Initialize parameters
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
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
        "gender": None,
        "status_value": None,  # Added for category filter
        "creche_age": creche_age  # Added for creche_age filter
    }

    # Get user's partner and geography mapping
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    # Get user's geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    # Handle creche opening date filters
    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            params['cstart_date'], params['cend_date'] = date_range
        elif range_type == "before" and single_date:
            params['cstart_date'] = date(2017, 1, 1)
            params['cend_date'] = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            params['cstart_date'] = single_date + timedelta(days=1)
            params['cend_date'] = date.today()
        elif range_type == "equal" and single_date:
            params['cstart_date'] = single_date

    # Apply filters
    if partner_id:
        params["partner"] = partner_id
    
    # Geography filters
    if filters.get("state"):
        params["state"] = filters.get("state")
    else:
        state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
        if state_ids:
            params["state_ids"] = ",".join(state_ids)

    if filters.get("district"):
        params["district"] = filters.get("district")
    else:
        district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
        if district_ids:
            params["district_ids"] = ",".join(district_ids)

    if filters.get("block"):
        params["block"] = filters.get("block")
    else:
        block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
        if block_ids:
            params["block_ids"] = ",".join(block_ids)

    if filters.get("gp"):
        params["gp"] = filters.get("gp")
    else:
        gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
        if gp_ids:
            params["gp_ids"] = ",".join(gp_ids)

    # Other filters
    if filters.get("creche"):
        params["creche"] = filters.get("creche")
    
    if filters.get("supervisor_id"):
        params["supervisor_id"] = filters.get("supervisor_id")
    
    if filters.get("creche_status_id"):
        params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            params["phases"] = phases_cleaned

    if filters.get("gender"):
        params["gender"] = filters.get("gender")

    # Build conditions for geography filters
    conditions = []
    
    if params.get("partner"):
        conditions.append("cr.partner_id = %(partner)s")
    
    if params.get("state"):
        conditions.append("cr.state_id = %(state)s")
    elif params.get("state_ids"):
        conditions.append("FIND_IN_SET(cr.state_id, %(state_ids)s)")

    if params.get("district"):
        conditions.append("cr.district_id = %(district)s")
    elif params.get("district_ids"):
        conditions.append("FIND_IN_SET(cr.district_id, %(district_ids)s)")

    if params.get("block"):
        conditions.append("cr.block_id = %(block)s")
    elif params.get("block_ids"):
        conditions.append("FIND_IN_SET(cr.block_id, %(block_ids)s)")

    if params.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
    elif params.get("gp_ids"):
        conditions.append("FIND_IN_SET(cr.gp_id, %(gp_ids)s)")

    if params.get("creche"):
        conditions.append("cr.name = %(creche)s")
    
    if params.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
    
    if params.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
    
    if params.get("phases"):
        conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
    
    if params.get("gender"):
        conditions.append("cee.gender_id = %(gender)s")

    # Handle creche opening date conditions
    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"):
        conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

    # Add creche_age filter condition
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

    # Enrollment date condition
    conditions.append("cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit >= %(start_date)s)")

    # Category filter - SIMILAR TO FIRST CODE
    if selected_category != "all":
        category_mapping = {"Severe": 1, "Moderate": 2, "Normal": 3}
        status_value = category_mapping.get(selected_category)
        status_field = {
            "weight_for_age": "tad.weight_for_age",
            "height_for_age": "tad.height_for_age",
            "weight_for_height": "tad.weight_for_height"
        }.get(selected_indicator)
        
        # We'll add this to the anthropometric subquery conditions
        params["status_value"] = status_value
        params["status_field"] = status_field

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    def generate_attendance_percentage_query(year, month, num_months):
        months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]
        select_clause = ["cal.childenrolledguid"]
        
        for y, m in months:
            select_clause.append(f"""
                CONCAT(
                    CASE 
                        WHEN COUNT(*) = 0 THEN '0'
                        ELSE FORMAT(
                            (IFNULL(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
                                                AND MONTH(ca.date_of_attendance) = {m} 
                                                AND cal.attendance = 1 THEN 1 END), 0) 
                            / NULLIF(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
                                                AND MONTH(ca.date_of_attendance) = {m} THEN 1 END), 0)) * 100, 2
                        ) 
                    END, 
                    '%% (',
                    IFNULL(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
                                    AND MONTH(ca.date_of_attendance) = {m} 
                                    AND cal.attendance = 1 THEN 1 END), 0),
                    ')'
                ) AS attendance_percentage_{y}_{m:02d}
            """)
        
        select_clause_str = ",\n    ".join(select_clause)
        
        query = f"""
            SELECT 
                {select_clause_str}
            FROM `tabChild Attendance` AS ca
            INNER JOIN `tabChild Attendance List` AS cal ON cal.parent = ca.name
            WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
            GROUP BY cal.childenrolledguid
        """
        return query

    def generate_anthropometric_data_query(year, month, num_months, selected_indicator, selected_category, params):
        months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]
        select_clause = ["tad.childenrollguid"]
        
        for y, m in months:
            year_month = f"{y}_{m:02d}"
            
            # Weight and Height for all indicators
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        THEN IFNULL(NULLIF(ROUND(tad.weight, 2), 0), '-')
                        ELSE '-'
                    END
                ) AS weight_{year_month}
            """)
            
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        THEN IFNULL(NULLIF(ROUND(tad.height, 2), 0), '-')
                        ELSE '-'
                    END
                ) AS height_{year_month}
            """)
            
            # Weight for Age - Z-Score
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        AND tad.weight_for_age_zscore IS NOT NULL
                        THEN ROUND(tad.weight_for_age_zscore, 2)
                        ELSE NULL
                    END
                ) AS underweight_status_{year_month}
            """)
            
            # Weight for Age - Status Code (with CASE statement to convert to text)
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        THEN 
                            CASE 
                                WHEN tad.weight_for_age = 1 THEN 'Severe'
                                WHEN tad.weight_for_age = 2 THEN 'Moderate'
                                WHEN tad.weight_for_age = 3 THEN 'Normal'
                                WHEN tad.weight_for_age = 4 THEN 'Overweight'
                                ELSE NULL
                            END
                        ELSE NULL
                    END
                ) AS weight_for_age_{year_month}
            """)
            
            # Weight for Height - Z-Score
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        AND tad.weight_for_height_zscore IS NOT NULL
                        THEN ROUND(tad.weight_for_height_zscore, 2)
                        ELSE NULL
                    END
                ) AS wasting_status_{year_month}
            """)
            
            # Weight for Height - Status Code (with CASE statement to convert to text)
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        THEN 
                            CASE 
                                WHEN tad.weight_for_height = 1 THEN 'Severe'
                                WHEN tad.weight_for_height = 2 THEN 'Moderate'
                                WHEN tad.weight_for_height = 3 THEN 'Normal'
                                WHEN tad.weight_for_height = 4 THEN 'Overweight'
                                ELSE NULL
                            END
                        ELSE NULL
                    END
                ) AS weight_for_height_{year_month}
            """)
            
            # Height for Age - Z-Score
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        AND tad.height_for_age_zscore IS NOT NULL
                        THEN ROUND(tad.height_for_age_zscore, 2)
                        ELSE NULL
                    END
                ) AS stuning_status_{year_month}
            """)
            
            # Height for Age - Status Code (with CASE statement to convert to text)
            select_clause.append(f"""
                MAX(
                    CASE 
                        WHEN YEAR(tad.measurement_taken_date) = {y} 
                        AND MONTH(tad.measurement_taken_date) = {m} 
                        THEN 
                            CASE 
                                WHEN tad.height_for_age = 1 THEN 'Severe'
                                WHEN tad.height_for_age = 2 THEN 'Moderate'
                                WHEN tad.height_for_age = 3 THEN 'Normal'
                                WHEN tad.height_for_age = 4 THEN 'Overweight'
                                ELSE NULL
                            END
                        ELSE NULL
                    END
                ) AS height_for_age_{year_month}
            """)
        
        select_clause_str = ",\n    ".join(select_clause)
        
        # Build WHERE clause - SIMILAR TO FIRST CODE'S LOGIC
        where_conditions = ["tad.measurement_taken_date IS NOT NULL"]
        
        # Category filter - SIMILAR TO FIRST CODE
        if selected_category != "all" and "status_field" in params and "status_value" in params:
            status_field = params["status_field"]
            status_value = params["status_value"]
            where_conditions.append(f"{status_field} = {status_value}")
        
        where_clause_inner = " AND ".join(where_conditions)
        
        query = f"""
            SELECT 
                {select_clause_str}
            FROM `tabAnthropromatic Data` tad 
            INNER JOIN `tabChild Growth Monitoring` tcgm ON tad.parent = tcgm.name 
            WHERE {where_clause_inner}
            GROUP BY tad.childenrollguid
        """
        return query

    attendance_percentage_query = generate_attendance_percentage_query(year, month, num_months)
    anthropometric_data_query = generate_anthropometric_data_query(year, month, num_months, selected_indicator, selected_category, params)

    sql_query = f"""
    SELECT    
        cr.creche_name AS 'creche_name',
        DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS 'creche_opening_date',
        cr.creche_id AS 'creche_id',
        usr.full_name AS 'supervisor',
        cee.child_id AS 'child_id',
        cee.child_name AS 'child_name',
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS 'date_of_enrollment',
        cee.age_at_enrollment_in_months AS 'age',
        
        -- Dynamic attendance percentages
        opx.*,
        
        -- Dynamic anthropometric data
        ad.*,
        
        (CASE 
            WHEN cee.gender_id = '1' THEN 'M' 
            WHEN cee.gender_id = '2' THEN 'F' 
            ELSE cee.gender_id 
        END) AS gender,
        p.partner_name AS partner,
        s.state_name AS state,
        d.district_name AS district,
        b.block_name AS block
    FROM  
        `tabChild Enrollment and Exit` AS cee  
    LEFT JOIN (
        {attendance_percentage_query}
    ) AS opx ON opx.childenrolledguid = cee.childenrollguid    
    INNER JOIN (
        {anthropometric_data_query}
    ) AS ad ON ad.childenrollguid = cee.childenrollguid    
    INNER JOIN 
        `tabCreche` AS cr ON cee.creche_id = cr.name 
    INNER JOIN 
        `tabUser` AS usr ON cr.supervisor_id = usr.name 
    INNER JOIN 
        `tabPartner` AS p ON p.name = cr.partner_id
    INNER JOIN 
        `tabState` AS s ON s.name = cr.state_id
    INNER JOIN 
        `tabDistrict` AS d ON d.name = cr.district_id
    INNER JOIN 
        `tabBlock` AS b ON b.name = cr.block_id
    WHERE 
        {where_clause}
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
    ORDER BY
        partner, state, district, block, supervisor, creche_name, child_name
    """

    data = frappe.db.sql(sql_query, params, as_dict=True)
    return data

def apply_conditional_formatting(data, filters):
    if not filters:
        return data
        
    month = int(filters.get("month", date.today().month))
    year = int(filters.get("year", date.today().year))
    selected_indicator = filters.get("indicator", "weight_for_age")
    duration = filters.get("duration", "12_months")
    
    # Determine number of months based on duration
    num_months = 12  # default
    if duration == "3_months":
        num_months = 3
    elif duration == "6_months":
        num_months = 6
    elif duration == "12_months":
        num_months = 12
    
    months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]
    
    for row in data:
        for y, m in months:
            year_month = f"{y}_{m:02d}"
            
            # Determine which fields to format based on selected indicator
            if selected_indicator == "weight_for_age":
                status_field = f"weight_for_age_{year_month}"
                zscore_field = f"underweight_status_{year_month}"
                status_display_field = f"weight_for_age_status_{year_month}"
            elif selected_indicator == "height_for_age":
                status_field = f"height_for_age_{year_month}"
                zscore_field = f"stuning_status_{year_month}"
                status_display_field = f"height_for_age_status_{year_month}"
            else:  # weight_for_height
                status_field = f"weight_for_height_{year_month}"
                zscore_field = f"wasting_status_{year_month}"
                status_display_field = f"weight_for_height_status_{year_month}"
            
            status_value = row.get(status_field)
            zscore_value = row.get(zscore_field)
            
            # Apply formatting to z-score field - SIMILAR TO FIRST CODE
            if zscore_value is not None and status_value:
                if status_value == 'Severe':
                    row[zscore_field] = format_cell(zscore_value, "#FFCCCC", "#CC0000")
                elif status_value == 'Moderate':
                    row[zscore_field] = format_cell(zscore_value, "#FFFFCC", "#999900")
                elif status_value == 'Normal':
                    row[zscore_field] = format_cell(zscore_value, "#CCFFCC", "#006600")
                elif status_value == 'Overweight':
                    row[zscore_field] = format_cell(zscore_value, "#E6E6E6", "#666666")
            
            # Apply formatting to status display field - SIMILAR TO FIRST CODE
            if status_value:
                if status_value == 'Severe':
                    row[status_display_field] = format_cell(status_value, "#FFCCCC", "#CC0000")
                elif status_value == 'Moderate':
                    row[status_display_field] = format_cell(status_value, "#FFFFCC", "#999900")
                elif status_value == 'Normal':
                    row[status_display_field] = format_cell(status_value, "#CCFFCC", "#006600")
                elif status_value == 'Overweight':
                    row[status_display_field] = format_cell(status_value, "#E6E6E6", "#666666")
            else:
                row[status_display_field] = "-"
    
    return data

def format_cell(value, bg_color, text_color):
    return f"""
        <div style='
            background-color: {bg_color};
            color: {text_color};
            border-radius: 3px;
            text-align: center;
            font-weight: bold;
            padding: 2px 5px;
        '>
            {value}
        </div>
    """























#backup-Before age of creche filter
# import frappe
# from frappe.utils import nowdate
# import calendar
# from datetime import datetime, timedelta, date

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_summary_data(filters)
#     data = apply_conditional_formatting(data, filters)
#     return columns, data

# def get_columns(filters=None):
#     month = int(filters.get("month") if filters else date.today().month)
#     year = int(filters.get("year") if filters else date.today().year)
#     selected_indicator = filters.get("indicator", "weight_for_age") if filters else "weight_for_age"
#     duration = filters.get("duration", "12_months") if filters else "12_months"

#     # Determine number of months based on duration
#     num_months = 12  # default
#     if duration == "3_months":
#         num_months = 3
#     elif duration == "6_months":
#         num_months = 6
#     elif duration == "12_months":
#         num_months = 12

#     months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]

#     columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
#         {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
#         {"label": "Creche Opening date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 200},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Data", "width": 200},
#         {"label": "Age (in month)", "fieldname": "age", "fieldtype": "Data", "width": 150},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
#     ]

#     # Define column templates for each indicator - SIMILAR TO FIRST CODE
#     indicator_columns = {
#         "weight_for_age": [
#             ("Weight (kg)", "weight", "Data", 190),
#             ("Height (cm)", "height", "Data", 190),
#             ("WFA Z-Score", "underweight_status", "Data", 200),
#             # ("WFA Status", "weight_for_age_status", "Data", 200)
#         ],
#         "height_for_age": [
#             ("Weight (kg)", "weight", "Data", 190),
#             ("Height (cm)", "height", "Data", 190),
#             ("HFA Z-Score", "stuning_status", "Data", 200),
#             # ("HFA Status", "height_for_age_status", "Data", 220)
#         ],
#         "weight_for_height": [
#             ("Weight (kg)", "weight", "Data", 190),
#             ("Height (cm)", "height", "Data", 190),
#             ("WFH Z-Score", "wasting_status", "Data", 220),
#             # ("WFH Status", "weight_for_height_status", "Data", 220)
#         ]
#     }
    
#     # Get the column templates for the selected indicator
#     column_templates = indicator_columns.get(selected_indicator, indicator_columns["weight_for_age"])

#     for y, m in months:
#         month_name = date(y, m, 1).strftime("%b")  
#         year_month = f"{y}_{m:02d}"
        
#         # Add attendance column
#         columns.append({
#             "label": f"Attendance-[{month_name} {y}]",
#             "fieldname": f"attendance_percentage_{year_month}",
#             "fieldtype": "Data",
#             "width": 190,
#             "default": "-" 
#         })
        
#         # Add columns based on the template - SIMILAR TO FIRST CODE'S LOGIC
#         for template in column_templates:
#             label = f"{template[0]}-[{month_name} {y}]"
#             fieldname = f"{template[1]}_{year_month}"
            
#             columns.append({
#                 "label": label,
#                 "fieldname": fieldname,
#                 "fieldtype": template[2],
#                 "width": template[3]
#             })
    
#     return columns

# @frappe.whitelist()
# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}
    
#     # Date range setup
#     current_date = date.today()
#     month = int(filters.get("month", current_date.month))
#     year = int(filters.get("year", current_date.year))
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     selected_indicator = filters.get("indicator", "weight_for_age")
#     selected_category = filters.get("category", "all")
#     duration = filters.get("duration", "12_months")

#     # Determine number of months based on duration
#     num_months = 12  # default
#     if duration == "3_months":
#         num_months = 3
#     elif duration == "6_months":
#         num_months = 6
#     elif duration == "12_months":
#         num_months = 12

#     # Initialize parameters
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
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
#         "gender": None,
#         "status_value": None  # Added for category filter
#     }

#     # Get user's partner and geography mapping
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Get user's geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
#     # Handle creche opening date filters
#     range_type = filters.get("cr_opening_range_type")
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             params['cstart_date'], params['cend_date'] = date_range
#         elif range_type == "before" and single_date:
#             params['cstart_date'] = date(2017, 1, 1)
#             params['cend_date'] = single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             params['cstart_date'] = single_date + timedelta(days=1)
#             params['cend_date'] = date.today()
#         elif range_type == "equal" and single_date:
#             params['cstart_date'] = single_date

#     # Apply filters
#     if partner_id:
#         params["partner"] = partner_id
    
#     # Geography filters
#     if filters.get("state"):
#         params["state"] = filters.get("state")
#     else:
#         state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
#         if state_ids:
#             params["state_ids"] = ",".join(state_ids)

#     if filters.get("district"):
#         params["district"] = filters.get("district")
#     else:
#         district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
#         if district_ids:
#             params["district_ids"] = ",".join(district_ids)

#     if filters.get("block"):
#         params["block"] = filters.get("block")
#     else:
#         block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
#         if block_ids:
#             params["block_ids"] = ",".join(block_ids)

#     if filters.get("gp"):
#         params["gp"] = filters.get("gp")
#     else:
#         gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
#         if gp_ids:
#             params["gp_ids"] = ",".join(gp_ids)

#     # Other filters
#     if filters.get("creche"):
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
#         if phases_cleaned:  
#             params["phases"] = phases_cleaned

#     if filters.get("gender"):
#         params["gender"] = filters.get("gender")

#     # Build conditions for geography filters
#     conditions = []
    
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
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
    
#     if params.get("phases"):
#         conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")
    
#     if params.get("gender"):
#         conditions.append("cee.gender_id = %(gender)s")

#     # Handle creche opening date conditions
#     if params.get("cstart_date") and params.get("cend_date"):
#         conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
#     elif params.get("cstart_date"):
#         conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

#     # Enrollment date condition
#     conditions.append("cee.date_of_enrollment <= %(end_date)s and (cee.date_of_exit IS null or cee.date_of_exit >= %(start_date)s)")

#     # Category filter - SIMILAR TO FIRST CODE
#     if selected_category != "all":
#         category_mapping = {"Severe": 1, "Moderate": 2, "Normal": 3}
#         status_value = category_mapping.get(selected_category)
#         status_field = {
#             "weight_for_age": "tad.weight_for_age",
#             "height_for_age": "tad.height_for_age",
#             "weight_for_height": "tad.weight_for_height"
#         }.get(selected_indicator)
        
#         # We'll add this to the anthropometric subquery conditions
#         params["status_value"] = status_value
#         params["status_field"] = status_field

#     where_clause = " AND ".join(conditions) if conditions else "1=1"

#     def generate_attendance_percentage_query(year, month, num_months):
#         months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]
#         select_clause = ["cal.childenrolledguid"]
        
#         for y, m in months:
#             select_clause.append(f"""
#                 CONCAT(
#                     CASE 
#                         WHEN COUNT(*) = 0 THEN '0'
#                         ELSE FORMAT(
#                             (IFNULL(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
#                                                 AND MONTH(ca.date_of_attendance) = {m} 
#                                                 AND cal.attendance = 1 THEN 1 END), 0) 
#                             / NULLIF(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
#                                                 AND MONTH(ca.date_of_attendance) = {m} THEN 1 END), 0)) * 100, 2
#                         ) 
#                     END, 
#                     '%% (',
#                     IFNULL(SUM(CASE WHEN YEAR(ca.date_of_attendance) = {y} 
#                                     AND MONTH(ca.date_of_attendance) = {m} 
#                                     AND cal.attendance = 1 THEN 1 END), 0),
#                     ')'
#                 ) AS attendance_percentage_{y}_{m:02d}
#             """)
        
#         select_clause_str = ",\n    ".join(select_clause)
        
#         query = f"""
#             SELECT 
#                 {select_clause_str}
#             FROM `tabChild Attendance` AS ca
#             INNER JOIN `tabChild Attendance List` AS cal ON cal.parent = ca.name
#             WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
#             GROUP BY cal.childenrolledguid
#         """
#         return query

#     def generate_anthropometric_data_query(year, month, num_months, selected_indicator, selected_category, params):
#         months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]
#         select_clause = ["tad.childenrollguid"]
        
#         for y, m in months:
#             year_month = f"{y}_{m:02d}"
            
#             # Weight and Height for all indicators
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         THEN IFNULL(NULLIF(ROUND(tad.weight, 2), 0), '-')
#                         ELSE '-'
#                     END
#                 ) AS weight_{year_month}
#             """)
            
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         THEN IFNULL(NULLIF(ROUND(tad.height, 2), 0), '-')
#                         ELSE '-'
#                     END
#                 ) AS height_{year_month}
#             """)
            
#             # Weight for Age - Z-Score
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         AND tad.weight_for_age_zscore IS NOT NULL
#                         THEN ROUND(tad.weight_for_age_zscore, 2)
#                         ELSE NULL
#                     END
#                 ) AS underweight_status_{year_month}
#             """)
            
#             # Weight for Age - Status Code (with CASE statement to convert to text)
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         THEN 
#                             CASE 
#                                 WHEN tad.weight_for_age = 1 THEN 'Severe'
#                                 WHEN tad.weight_for_age = 2 THEN 'Moderate'
#                                 WHEN tad.weight_for_age = 3 THEN 'Normal'
#                                 WHEN tad.weight_for_age = 4 THEN 'Overweight'
#                                 ELSE NULL
#                             END
#                         ELSE NULL
#                     END
#                 ) AS weight_for_age_{year_month}
#             """)
            
#             # Weight for Height - Z-Score
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         AND tad.weight_for_height_zscore IS NOT NULL
#                         THEN ROUND(tad.weight_for_height_zscore, 2)
#                         ELSE NULL
#                     END
#                 ) AS wasting_status_{year_month}
#             """)
            
#             # Weight for Height - Status Code (with CASE statement to convert to text)
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         THEN 
#                             CASE 
#                                 WHEN tad.weight_for_height = 1 THEN 'Severe'
#                                 WHEN tad.weight_for_height = 2 THEN 'Moderate'
#                                 WHEN tad.weight_for_height = 3 THEN 'Normal'
#                                 WHEN tad.weight_for_height = 4 THEN 'Overweight'
#                                 ELSE NULL
#                             END
#                         ELSE NULL
#                     END
#                 ) AS weight_for_height_{year_month}
#             """)
            
#             # Height for Age - Z-Score
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         AND tad.height_for_age_zscore IS NOT NULL
#                         THEN ROUND(tad.height_for_age_zscore, 2)
#                         ELSE NULL
#                     END
#                 ) AS stuning_status_{year_month}
#             """)
            
#             # Height for Age - Status Code (with CASE statement to convert to text)
#             select_clause.append(f"""
#                 MAX(
#                     CASE 
#                         WHEN YEAR(tad.measurement_taken_date) = {y} 
#                         AND MONTH(tad.measurement_taken_date) = {m} 
#                         THEN 
#                             CASE 
#                                 WHEN tad.height_for_age = 1 THEN 'Severe'
#                                 WHEN tad.height_for_age = 2 THEN 'Moderate'
#                                 WHEN tad.height_for_age = 3 THEN 'Normal'
#                                 WHEN tad.height_for_age = 4 THEN 'Overweight'
#                                 ELSE NULL
#                             END
#                         ELSE NULL
#                     END
#                 ) AS height_for_age_{year_month}
#             """)
        
#         select_clause_str = ",\n    ".join(select_clause)
        
#         # Build WHERE clause - SIMILAR TO FIRST CODE'S LOGIC
#         where_conditions = ["tad.measurement_taken_date IS NOT NULL"]
        
#         # Category filter - SIMILAR TO FIRST CODE
#         if selected_category != "all" and "status_field" in params and "status_value" in params:
#             status_field = params["status_field"]
#             status_value = params["status_value"]
#             where_conditions.append(f"{status_field} = {status_value}")
        
#         where_clause_inner = " AND ".join(where_conditions)
        
#         query = f"""
#             SELECT 
#                 {select_clause_str}
#             FROM `tabAnthropromatic Data` tad 
#             INNER JOIN `tabChild Growth Monitoring` tcgm ON tad.parent = tcgm.name 
#             WHERE {where_clause_inner}
#             GROUP BY tad.childenrollguid
#         """
#         return query

#     attendance_percentage_query = generate_attendance_percentage_query(year, month, num_months)
#     anthropometric_data_query = generate_anthropometric_data_query(year, month, num_months, selected_indicator, selected_category, params)

#     sql_query = f"""
#     SELECT    
#         cr.creche_name AS 'creche_name',
#         DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS 'creche_opening_date',
#         cr.creche_id AS 'creche_id',
#         usr.full_name AS 'supervisor',
#         cee.child_id AS 'child_id',
#         cee.child_name AS 'child_name',
#         DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS 'date_of_enrollment',
#         cee.age_at_enrollment_in_months AS 'age',
        
#         -- Dynamic attendance percentages
#         opx.*,
        
#         -- Dynamic anthropometric data
#         ad.*,
        
#         (CASE 
#             WHEN cee.gender_id = '1' THEN 'M' 
#             WHEN cee.gender_id = '2' THEN 'F' 
#             ELSE cee.gender_id 
#         END) AS gender,
#         p.partner_name AS partner,
#         s.state_name AS state,
#         d.district_name AS district,
#         b.block_name AS block
#     FROM  
#         `tabChild Enrollment and Exit` AS cee  
#     LEFT JOIN (
#         {attendance_percentage_query}
#     ) AS opx ON opx.childenrolledguid = cee.childenrollguid    
#     INNER JOIN (
#         {anthropometric_data_query}
#     ) AS ad ON ad.childenrollguid = cee.childenrollguid    
#     INNER JOIN 
#         `tabCreche` AS cr ON cee.creche_id = cr.name 
#     INNER JOIN 
#         `tabUser` AS usr ON cr.supervisor_id = usr.name 
#     INNER JOIN 
#         `tabPartner` AS p ON p.name = cr.partner_id
#     INNER JOIN 
#         `tabState` AS s ON s.name = cr.state_id
#     INNER JOIN 
#         `tabDistrict` AS d ON d.name = cr.district_id
#     INNER JOIN 
#         `tabBlock` AS b ON b.name = cr.block_id
#     WHERE 
#         {where_clause}
#         AND cee.date_of_enrollment <= %(end_date)s
#         AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#     ORDER BY
#         partner, state, district, block, supervisor, creche_name, child_name
#     """

#     data = frappe.db.sql(sql_query, params, as_dict=True)
#     return data

# def apply_conditional_formatting(data, filters):
#     if not filters:
#         return data
        
#     month = int(filters.get("month", date.today().month))
#     year = int(filters.get("year", date.today().year))
#     selected_indicator = filters.get("indicator", "weight_for_age")
#     duration = filters.get("duration", "12_months")
    
#     # Determine number of months based on duration
#     num_months = 12  # default
#     if duration == "3_months":
#         num_months = 3
#     elif duration == "6_months":
#         num_months = 6
#     elif duration == "12_months":
#         num_months = 12
    
#     months = [(year - (month - i <= 0), (month - i - 1) % 12 + 1) for i in range(num_months)]
    
#     for row in data:
#         for y, m in months:
#             year_month = f"{y}_{m:02d}"
            
#             # Determine which fields to format based on selected indicator
#             if selected_indicator == "weight_for_age":
#                 status_field = f"weight_for_age_{year_month}"
#                 zscore_field = f"underweight_status_{year_month}"
#                 status_display_field = f"weight_for_age_status_{year_month}"
#             elif selected_indicator == "height_for_age":
#                 status_field = f"height_for_age_{year_month}"
#                 zscore_field = f"stuning_status_{year_month}"
#                 status_display_field = f"height_for_age_status_{year_month}"
#             else:  # weight_for_height
#                 status_field = f"weight_for_height_{year_month}"
#                 zscore_field = f"wasting_status_{year_month}"
#                 status_display_field = f"weight_for_height_status_{year_month}"
            
#             status_value = row.get(status_field)
#             zscore_value = row.get(zscore_field)
            
#             # Apply formatting to z-score field - SIMILAR TO FIRST CODE
#             if zscore_value is not None and status_value:
#                 if status_value == 'Severe':
#                     row[zscore_field] = format_cell(zscore_value, "#FFCCCC", "#CC0000")
#                 elif status_value == 'Moderate':
#                     row[zscore_field] = format_cell(zscore_value, "#FFFFCC", "#999900")
#                 elif status_value == 'Normal':
#                     row[zscore_field] = format_cell(zscore_value, "#CCFFCC", "#006600")
#                 elif status_value == 'Overweight':
#                     row[zscore_field] = format_cell(zscore_value, "#E6E6E6", "#666666")
            
#             # Apply formatting to status display field - SIMILAR TO FIRST CODE
#             if status_value:
#                 if status_value == 'Severe':
#                     row[status_display_field] = format_cell(status_value, "#FFCCCC", "#CC0000")
#                 elif status_value == 'Moderate':
#                     row[status_display_field] = format_cell(status_value, "#FFFFCC", "#999900")
#                 elif status_value == 'Normal':
#                     row[status_display_field] = format_cell(status_value, "#CCFFCC", "#006600")
#                 elif status_value == 'Overweight':
#                     row[status_display_field] = format_cell(status_value, "#E6E6E6", "#666666")
#             else:
#                 row[status_display_field] = "-"
    
#     return data

# def format_cell(value, bg_color, text_color):
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 2px 5px;
#         '>
#             {value}
#         </div>
#     """
