from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    if not filters:
        filters = {}
        
    selected_indicator = filters.get("indicator", "weight_for_age")
    selected_category = filters.get("category", "all")
    
    # Get date range from filters
    initial_month = int(filters.get("initial_month")) if filters.get("initial_month") else 1
    initial_year = int(filters.get("initial_year")) if filters.get("initial_year") else 2023
    final_month = int(filters.get("final_month")) if filters.get("final_month") else datetime.now().month
    final_year = int(filters.get("final_year")) if filters.get("final_year") else datetime.now().year

    # Define columns
    fixed_columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
        {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 120},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 120},
        {"label": "Age at Enrollment (In Months)", "fieldname": "age", "fieldtype": "Int", "width": 250},
        {"label": "Date of Enrollment", "fieldname": "enrollment_date", "fieldtype": "date", "width": 150},
        {"label": "Date of Exit", "fieldname": "date_of_exit", "fieldtype": "date", "width": 120},
        {"label": "Current Age (In Months)", "fieldname": "current_age", "fieldtype": "Data", "width": 186},
    ]
    dynamic_columns = generate_monthly_columns(initial_month, initial_year, final_month, final_year, selected_indicator)
    
    columns = fixed_columns + dynamic_columns
    data = get_report_data(filters, initial_month, initial_year, final_month, final_year, selected_indicator)
    data = apply_conditional_formatting(data, initial_month, initial_year, final_month, final_year, selected_indicator)
    
    return columns, data

def generate_monthly_columns(start_month, start_year, end_month, end_year, indicator):
    columns = []
    current_date = date(start_year, start_month, 1)
    end_date = date(end_year, end_month, 1)
    
    indicator_columns = {
        "weight_for_age": [
            ("Weight (kg)", "weight", "data", 160),
            ("Height (cm)", "height", "data", 170),
            ("Weight for Age z-score", "weight_for_age_zscore", "data", 250),
            ("Weight for Age Status", "weight_for_age", "data", 200),  # Added status field
            ("Remarks", "remarks", "Data", 200)
        ],
        "height_for_age": [
            ("Height (cm)", "height", "data", 165),
            ("Height for Age z-score", "height_for_age_zscore", "data", 250),
            ("Height for Age Status", "height_for_age", "data", 200),  # Added status field
            ("Remarks", "remarks", "Data", 200)
        ],
        "weight_for_height": [
            ("Weight (kg)", "weight", "data", 160),
            ("Height (cm)", "height", "data", 170),
            ("Weight for Height z-score", "weight_for_height_zscore", "data", 250),
            ("Weight for Height Status", "weight_for_height", "data", 200),  # Added status fiel
            ("Remarks", "remarks", "Data", 210)
        ]
    }
    
    column_templates = indicator_columns.get(indicator, indicator_columns["weight_for_age"])
    
    while current_date <= end_date:
        month_year = current_date.strftime("%b-%y")
        for template in column_templates:
            label = f"{month_year} {template[0]}"
            fieldname = f"{current_date.month}_{current_date.year}_{template[1]}"
            columns.append({
                "label": label,
                "fieldname": fieldname,
                "fieldtype": template[2],
                "width": template[3]
            })
        
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
    return columns

def get_report_data(filters, initial_month, initial_year, final_month, final_year, selected_indicator):
    if not filters:
        filters = {}
        
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    # Get geography filters
    geography_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
    """
    current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)
    state_ids = [g["state_id"] for g in current_user_geography if g.get("state_id")]
    district_ids = [g["district_id"] for g in current_user_geography if g.get("district_id")]
    block_ids = [g["block_id"] for g in current_user_geography if g.get("block_id")]
    gp_ids = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]
    
    selected_category = filters.get("category", "all")    
    # Build base query
    query = """
        SELECT 
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            cr.creche_name AS creche,
            usr.full_name AS supervisor_id,
            cr.creche_id AS creche_id,
            cee.child_id AS child_id,
            cee.child_name AS child_name,
            CASE 
                WHEN cee.gender_id = '1' THEN 'M' 
                WHEN cee.gender_id = '2' THEN 'F' 
                ELSE cee.gender_id 
            END AS gender,
            cee.age_at_enrollment_in_months AS age,
            CASE 
                WHEN cee.child_dob IS NULL THEN '-'
                ELSE DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y')
            END AS child_dob,
            cee.age_at_enrollment_in_months AS age,
            IFNULL(NULLIF(DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y'), ''), '-') AS enrollment_date,
            IFNULL(NULLIF(DATE_FORMAT(cee.date_of_exit, '%%d-%%m-%%Y'), ''), '-') AS date_of_exit,
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(final_date)s) AS current_age,
            cee.is_exited,
            cee.reason_for_exit
    """
    
    # Add dynamic fields for each month
    current_date = date(initial_year, initial_month, 1)
    end_date = date(final_year, final_month, 1)
    
    while current_date <= end_date:
        month = current_date.month
        year = current_date.year
        month_start = current_date.strftime('%Y-%m-01')

        month_end_day = calendar.monthrange(current_date.year, current_date.month)[1]
        month_end = current_date.strftime('%Y-%m-') + str(month_end_day)
        
        query += f""",
            MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} 
                THEN IFNULL(NULLIF(ROUND(ad.weight, 2), 0), '-') END) AS {month}_{year}_weight,
            MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} 
                THEN IFNULL(NULLIF(ROUND(ad.height, 2), 0), '-') END) AS {month}_{year}_height,
            MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_age_zscore END) AS {month}_{year}_weight_for_age_zscore,
            MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.height_for_age_zscore END) AS {month}_{year}_height_for_age_zscore,
            MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_height_zscore END) AS {month}_{year}_weight_for_height_zscore,
         

            CASE 
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_age END) = 1 THEN 'Severe'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_age END) = 2 THEN 'Moderate'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_age END) = 3 THEN 'Normal'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_age END) = 4 THEN 'Overweight'
       
            END AS {month}_{year}_weight_for_age,
            CASE 
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.height_for_age END) = 1 THEN 'Severe'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.height_for_age END) = 2 THEN 'Moderate'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.height_for_age END) = 3 THEN 'Normal'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.height_for_age END) = 4 THEN 'Overweight'
                
            END AS {month}_{year}_height_for_age,
            CASE 
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_height END) = 1 THEN 'Severe'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_height END) = 2 THEN 'Moderate'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_height END) = 3 THEN 'Normal'
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.weight_for_height END) = 4 THEN 'Overweight'
                
            END AS {month}_{year}_weight_for_height,

            MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.do_you_have_height_weight END) AS {month}_{year}_measured,
            CASE 
                WHEN cee.date_of_exit IS NOT NULL AND cee.date_of_exit <= '{month_end}' THEN 
                    CASE 
                        WHEN cee.reason_for_exit = 3 THEN 'Graduated'
                        WHEN cee.reason_for_exit = 4 THEN 'Migrated'
                        WHEN cee.is_exited = 1 THEN 'Exited'
                        ELSE 'Others'
                    END
                WHEN MAX(CASE WHEN MONTH(cgm.measurement_date) = {month} AND YEAR(cgm.measurement_date) = {year} THEN ad.do_you_have_height_weight ELSE 0 END) = 1 
                THEN 'Measured'
                ELSE 'Absent During Measurement'
            END AS `{month}_{year}_remarks`
        """
        
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
    # Complete the query
    query += """
        FROM `tabAnthropromatic Data` AS ad
        LEFT JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        LEFT JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabCreche` AS cr ON cee.creche_id = cr.name
        LEFT JOIN `tabUser` AS usr ON cr.supervisor_id = usr.name
        LEFT JOIN `tabPartner` AS p ON p.name = cr.partner_id
        LEFT JOIN `tabState` AS s ON s.name = cr.state_id
        LEFT JOIN `tabDistrict` AS d ON d.name = cr.district_id
        LEFT JOIN `tabBlock` AS b ON b.name = cr.block_id
        LEFT JOIN `tabGram Panchayat` AS g ON g.name = cr.gp_id
    """
    
    initial_date = date(initial_year, initial_month, 1)
    final_date = date(final_year, final_month, calendar.monthrange(final_year, final_month)[1])
    initial_month_final_date = date(initial_year, initial_month, calendar.monthrange(initial_year, initial_month)[1])
    
    conditions = []
    params = {
        "initial_date": initial_date,
        "final_date": final_date,
        "initial_month_final_date": initial_month_final_date,
        "age_group": filters.get("age_group"),
        "partner_id": partner_id
    }

    # Age group condition
    age_group_condition = ""
    if params.get("age_group"):
        if params["age_group"] == "6m-11m":
            age_group_condition = "AND ROUND(DATEDIFF(%(initial_date)s, cee.child_dob)/30, 0) BETWEEN 6 AND 11"
        elif params["age_group"] == "12m-17m":
            age_group_condition = "AND ROUND(DATEDIFF(%(initial_date)s, cee.child_dob)/30, 0) BETWEEN 12 AND 17"
        elif params["age_group"] == "18m-23m":
            age_group_condition = "AND ROUND(DATEDIFF(%(initial_date)s, cee.child_dob)/30, 0) BETWEEN 18 AND 23"
        elif params["age_group"] == "24m-29m":
            age_group_condition = "AND ROUND(DATEDIFF(%(initial_date)s, cee.child_dob)/30, 0) BETWEEN 24 AND 29"
        elif params["age_group"] == "30m-36m":
            age_group_condition = "AND ROUND(DATEDIFF(%(initial_date)s, cee.child_dob)/30, 0) BETWEEN 30 AND 36"
        elif params["age_group"] == "> 36m":
            age_group_condition = "AND ROUND(DATEDIFF(%(initial_date)s, cee.child_dob)/30, 0) > 36"

    # Geography filters
    if partner_id:
        conditions.append("cr.partner_id = %(partner_id)s")
    
    if filters.get("state"):
        conditions.append("cr.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        conditions.append("cr.state_id IN %(state_ids)s")
        params["state_ids"] = state_ids
    
    if filters.get("district"):
        conditions.append("cr.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids:
        conditions.append("cr.district_id IN %(district_ids)s")
        params["district_ids"] = district_ids
    
    if filters.get("block"):
        conditions.append("cr.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids:
        conditions.append("cr.block_id IN %(block_ids)s")
        params["block_ids"] = block_ids
    
    if filters.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids:
        conditions.append("cr.gp_id IN %(gp_ids)s")
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

    if filters.get("gender"):
        conditions.append("cee.gender_id = %(gender)s")
        params["gender"] = filters.get("gender")

    # Category filter
    if selected_category != "all":
        category_mapping = {"Severe": 1, "Moderate": 2, "Normal": 3}
        status_value = category_mapping.get(selected_category)
        status_field = {
            "weight_for_age": "ad.weight_for_age",
            "height_for_age": "ad.height_for_age",
            "weight_for_height": "ad.weight_for_height"
        }.get(selected_indicator)
        conditions.append(f"{status_field} = {status_value}")

    where_clause = ""
    if conditions or age_group_condition:
        where_clause = " WHERE "
        if conditions:
            where_clause += " AND ".join(conditions)
        if age_group_condition:
            if conditions:  # If there are already conditions, add AND
                where_clause += " " + age_group_condition
            else:  # If no other conditions, just add the age group condition
                where_clause += age_group_condition
        where_clause += " AND cee.date_of_enrollment <= %(initial_month_final_date)s"

    query += where_clause

    # Group and filter
    query += """
        GROUP BY 
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name,
            cr.creche_name, usr.full_name, cr.creche_id,
            cee.child_id, cee.child_name, cee.gender_id, cee.child_dob, 
            cee.age_at_enrollment_in_months, cee.is_exited, cee.date_of_exit, cee.reason_for_exit
        HAVING 1=1
    """
    
    if selected_category != "all":
        query += f" AND MAX({status_field}) = {status_value}"

    query += """
        ORDER BY   
            p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name,
            cr.creche_name, usr.full_name, cr.creche_id,
            cee.child_id, cee.child_name, cee.gender_id, cee.child_dob
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data

def apply_conditional_formatting(data, start_month, start_year, end_month, end_year, indicator):
    current_date = date(start_year, start_month, 1)
    end_date = date(end_year, end_month, 1)
    
    while current_date <= end_date:
        month = current_date.month
        year = current_date.year
        
        for row in data:
            if indicator == "weight_for_age":
                status_field = f"{month}_{year}_weight_for_age"
                zscore_field = f"{month}_{year}_weight_for_age_zscore"
            elif indicator == "height_for_age":
                status_field = f"{month}_{year}_height_for_age"
                zscore_field = f"{month}_{year}_height_for_age_zscore"
            else:  # weight_for_height
                status_field = f"{month}_{year}_weight_for_height"
                zscore_field = f"{month}_{year}_weight_for_height_zscore"
            
            status_value = row.get(status_field)
            zscore_value = row.get(zscore_field)
            
            if zscore_value is not None and status_value is not None:
                if status_value == 'Severe':  # Severe
                    row[zscore_field] = format_cell(zscore_value, "#FFCCCC", "#CC0000")
                elif status_value == 'Moderate':  # Moderate
                    row[zscore_field] = format_cell(zscore_value, "#FFFFCC", "#999900")
                elif status_value == 'Normal':  # Normal
                    row[zscore_field] = format_cell(zscore_value, "#CCFFCC", "#006600")
                elif status_value == 'Overweight':  # Overweight
                    row[status_field] = format_cell(status_value, "#E6E6E6", "#666666")

             # Format status field with the same conditional formatting
            if status_value is not None:
                if status_value == "Severe":
                    row[status_field] = format_cell(status_value, "#FFCCCC", "#CC0000")
                elif status_value == "Moderate":
                    row[status_field] = format_cell(status_value, "#FFFFCC", "#999900")
                elif status_value == "Normal":
                    row[status_field] = format_cell(status_value, "#CCFFCC", "#006600")
                elif status_value == "Overweight":
                    row[status_field] = format_cell(status_value, "#E6E6E6", "#666666")
                    
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
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