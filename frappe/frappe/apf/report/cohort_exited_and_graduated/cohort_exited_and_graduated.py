import frappe
from frappe.utils import nowdate, getdate, date_diff
from datetime import date
import calendar

def execute(filters=None):
    if not filters:
        filters = {}
    
    # Calculate date range if month and year are provided
    if filters.get("year") and filters.get("month"):
        year = int(filters["year"])
        month = int(filters["month"])
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        filters["end_date"] = end_date
    
    columns = get_columns(filters)
    data = get_exit_data(filters)
    data = apply_conditional_formatting(data, filters)
    return columns, data

def get_columns(filters):
    base_columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Supervisor", "fieldname": "supervisor_name", "fieldtype": "Data", "width": 120},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 150},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 150},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": "Age (In Months at Exit)", "fieldname": "age_in_months", "fieldtype": "Int", "width": 175},
        {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Date", "width": 150},
        {"label": "Date of Exit", "fieldname": "date_of_exit", "fieldtype": "Date", "width": 130},
        {"label": "Reason of Exit", "fieldname": "reason_of_exit", "fieldtype": "Data", "width": 150},
        {"label": "Period of Stay (Months)", "fieldname": "duration_of_stay", "fieldtype": "Int", "width": 190},
        {"label": "Weight at Enrollment (kg)", "fieldname": "weight_at_enrollment", "fieldtype": "Data", "width": 200, "align": "right"},
        {"label": "Height at Enrollment (cm)", "fieldname": "height_at_enrollment", "fieldtype": "Data", "width": 200, "align": "right"},
        {"label": "Weight at Exit (kg)", "fieldname": "weight_at_exit", "fieldtype": "Data", "width": 200, "align": "right"},
        {"label": "Height at Exit (cm)", "fieldname": "height_at_exit", "fieldtype": "Data", "width": 200, "align": "right"},
        {"label": "Measurement Status (At Exit)", "fieldname": "measurement_status", "fieldtype": "Data", "width": 250},
    ]
    
    # Add indicator-specific columns
    indicator_columns = {
        "weight_for_age": [
            {"label": "Weight For Age Z Score (At Enrollment)", "fieldname": "weight_for_age_zscore_en", "fieldtype": "Data", "width": 340},
            {"label": "Weight For Age Z Score (At Exit)", "fieldname": "weight_for_age_zscore_ex", "fieldtype": "Data", "width": 260},
        ],
        "weight_for_height": [
            {"label": "Weight For Height Z Score (At Enrollment)", "fieldname": "weight_for_height_zscore_en", "fieldtype": "Data", "width": 370},
            {"label": "Weight For Height Z Score (At Exit)", "fieldname": "weight_for_height_zscore_ex", "fieldtype": "Data", "width": 260},
        ],
        "height_for_age": [
            {"label": "Height For Age Z Score (Enrollment)", "fieldname": "height_for_age_zscore_en", "fieldtype": "Data", "width": 340},
            {"label": "Height For Age Z Score (At Exit)", "fieldname": "height_for_age_zscore_ex", "fieldtype": "Data", "width": 260},
        ]
    }
    
    selected_indicator = filters.get("indicator", "weight_for_age")
    base_columns.extend(indicator_columns.get(selected_indicator, indicator_columns["weight_for_age"]))
    
    return base_columns

def get_exit_data(filters):
    if not filters:
        filters = {}
    
    conditions = []
    params = {}
    
    # Date filters
    if filters.get("year"):
        conditions.append("YEAR(ce.date_of_exit) = %(year)s")
        params["year"] = filters.get("year")
    
    if filters.get("month"):
        conditions.append("MONTH(ce.date_of_exit) = %(month)s")
        params["month"] = filters.get("month")
    
    # Geography filters
    geo_fields = ["state", "district", "block", "gp", "creche", "partner"]
    for field in geo_fields:
        if filters.get(field):
            conditions.append(f"ce.{field}_id = %({field})s")
            params[field] = filters.get(field)
    
    # Other filters
    if filters.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")
    
    if filters.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")
        
    if filters.get("phases"):
        phases = [p.strip() for p in filters["phases"].split(",") if p.strip()]
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params["phases"] = phases
    
    if filters.get("gender"):
        conditions.append("ce.gender_id = %(gender)s")
        params["gender"] = filters.get("gender")

    if filters.get("reason_of_exit"):
        conditions.append("ce.reason_for_exit = %(reason_of_exit)s")
        params["reason_of_exit"] = filters.get("reason_of_exit")
    
    if filters.get("duration_of_stay"):
        age_months = int(filters["duration_of_stay"].replace("m", ""))
        conditions.append("""
            TIMESTAMPDIFF(MONTH, ce.date_of_enrollment, ce.date_of_exit) = %(age_months)s
        """)
        params["age_months"] = age_months
    
    # Creche age filter
    creche_age = filters.get("creche_age", "")
    params["creche_age"] = creche_age
    if creche_age:
        conditions.append("""
            CASE
                WHEN c.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                ELSE ''
            END = %(creche_age)s
        """)
    
    # Category filter
    selected_category = filters.get("category", "all")
    selected_indicator = filters.get("indicator", "weight_for_age")
    
    if selected_category != "all":
        category_mapping = {
            "Severe": 1,
            "Moderate": 2,
            "Normal": 3
        }
        status_value = category_mapping.get(selected_category)
        
        indicator_field_map = {
            "weight_for_age": "weight_for_age",
            "weight_for_height": "weight_for_height",
            "height_for_age": "height_for_age"
        }
        
        field = indicator_field_map.get(selected_indicator, "weight_for_age")
        conditions.append(f"(enrollment_data.{field} = %(status_value)s OR exit_data.{field} = %(status_value)s)")
        params["status_value"] = status_value
        
    # Build the query
    conditions_sql = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT
        st.state_name AS state,
        p.partner_name AS partner,
        d.district_name AS district,
        b.block_name AS block,
        gp.gp_name AS gp,
        cr.creche_name AS creche,
        ce.child_id AS child_id,
        ce.child_name AS child_name,
        u.full_name AS supervisor_name,
        CASE WHEN ce.gender_id = 1 THEN 'M' ELSE 'F' END AS gender,
        ce.date_of_enrollment AS date_of_enrollment,
        ce.date_of_exit AS date_of_exit,
        ce.reason_for_exit AS reason_for_exit,
        
        /* Enrollment data */
        CASE 
            WHEN IFNULL(enrollment_data.weight, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(enrollment_data.weight, 2), 2)
        END AS weight_at_enrollment,
        CASE 
            WHEN IFNULL(enrollment_data.height, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(enrollment_data.height, 2), 2)
        END AS height_at_enrollment,
        
        /* All z-scores at enrollment */
        CASE 
            WHEN IFNULL(enrollment_data.weight_for_age_zscore, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(enrollment_data.weight_for_age_zscore, 2), 2)
        END AS weight_for_age_zscore_en,
        CASE 
            WHEN IFNULL(enrollment_data.weight_for_height_zscore, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(enrollment_data.weight_for_height_zscore, 2), 2)
        END AS weight_for_height_zscore_en,
        CASE 
            WHEN IFNULL(enrollment_data.height_for_age_zscore, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(enrollment_data.height_for_age_zscore, 2), 2)
        END AS height_for_age_zscore_en,
        
        /* Status at enrollment */
        enrollment_data.weight_for_age AS weight_for_age_status_en,
        enrollment_data.weight_for_height AS weight_for_height_status_en,
        enrollment_data.height_for_age AS height_for_age_status_en,
        
        /* Exit data */
        CASE 
            WHEN IFNULL(exit_data.weight, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(exit_data.weight, 2), 2)
        END AS weight_at_exit,
        CASE 
            WHEN IFNULL(exit_data.height, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(exit_data.height, 2), 2)
        END AS height_at_exit,
        
        /* All z-scores at exit */
        CASE 
            WHEN IFNULL(exit_data.weight_for_age_zscore, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(exit_data.weight_for_age_zscore, 2), 2)
        END AS weight_for_age_zscore_ex,
        CASE 
            WHEN IFNULL(exit_data.weight_for_height_zscore, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(exit_data.weight_for_height_zscore, 2), 2)
        END AS weight_for_height_zscore_ex,
        CASE 
            WHEN IFNULL(exit_data.height_for_age_zscore, 0) = 0 THEN '-'
            ELSE FORMAT(ROUND(exit_data.height_for_age_zscore, 2), 2)
        END AS height_for_age_zscore_ex,
        
        /* Status at exit */
        exit_data.weight_for_age AS weight_for_age_status_ex,
        exit_data.weight_for_height AS weight_for_height_status_ex,
        exit_data.height_for_age AS height_for_age_status_ex,
        
        /* Measurement status */
        CASE
            WHEN IFNULL(exit_data.weight, 0) = 0 AND IFNULL(exit_data.height, 0) = 0 THEN 'Not Available'
            WHEN IFNULL(exit_data.weight, 0) = 0 THEN 'Weight at exit not available'
            WHEN IFNULL(exit_data.height, 0) = 0 THEN 'Height at exit not available'
            ELSE 'Available'
        END AS measurement_status,
        
        TIMESTAMPDIFF(MONTH, ce.child_dob, %(end_date)s) AS age_in_months,
        TIMESTAMPDIFF(MONTH, ce.date_of_enrollment, ce.date_of_exit) AS duration_of_stay,
        CASE ce.reason_for_exit
            WHEN 1 THEN 'Migrated'
            WHEN 2 THEN 'Graduated'
            WHEN 3 THEN 'Not willing to stay'
            WHEN 4 THEN 'Death'
            WHEN 5 THEN 'Other'
            ELSE 'Unknown'
        END AS reason_of_exit
    FROM
        `tabChild Enrollment and Exit` ce
    JOIN
        `tabCreche` cr ON ce.creche_id = cr.name
    LEFT JOIN
        `tabPartner` p ON cr.partner_id = p.name
    LEFT JOIN
        `tabState` st ON cr.state_id = st.name
    LEFT JOIN
        `tabDistrict` d ON cr.district_id = d.name
    LEFT JOIN
        `tabBlock` b ON cr.block_id = b.name
    LEFT JOIN
        `tabGram Panchayat` gp ON cr.gp_id = gp.name
    LEFT JOIN 
        `tabUser` AS u ON u.name = cr.supervisor_id

    /* Enrollment data join */
    LEFT JOIN `tabAnthropromatic Data` as enrollment_data 
        ON ce.childenrollguid = enrollment_data.childenrollguid
        AND MONTH(enrollment_data.measurement_taken_date) = MONTH(ce.date_of_enrollment)
        AND YEAR(enrollment_data.measurement_taken_date) = YEAR(ce.date_of_enrollment)
    LEFT JOIN `tabChild Growth Monitoring` as cgm_enroll 
        ON cgm_enroll.name = enrollment_data.parent
        
    /* Exit data join */
    LEFT JOIN `tabAnthropromatic Data` as exit_data 
        ON ce.childenrollguid = exit_data.childenrollguid
        AND MONTH(exit_data.measurement_taken_date) = MONTH(ce.date_of_exit)
        AND YEAR(exit_data.measurement_taken_date) = YEAR(ce.date_of_exit)
    LEFT JOIN `tabChild Growth Monitoring` as cgm_exit 
        ON cgm_exit.name = exit_data.parent
    
    WHERE
        ce.date_of_exit IS NOT NULL
        AND {conditions_sql}
    ORDER BY
        p.partner_name, st.state_name, d.district_name,
        b.block_name, gp.gp_name, cr.creche_name, ce.child_name, ce.date_of_exit
"""
    
    # Add end_date to params if it exists in filters
    if "end_date" in filters:
        params["end_date"] = filters["end_date"]
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data

def apply_conditional_formatting(data, filters):
    if not data:
        return data

    selected_indicator = filters.get("indicator", "weight_for_age")
    selected_category = filters.get("category", "all").lower()

    category_map = {
        "severe": 1,
        "moderate": 2,
        "normal": 3,
        "all": "all"
    }
    target_status = category_map.get(selected_category)

    filtered_data = []

    for row in data:
        include_row = False

        def process(field_prefix):
            nonlocal include_row
            for suffix in ["en", "ex"]:
                status_key = f"{field_prefix}_status_{suffix}"
                zscore_key = f"{field_prefix}_zscore_{suffix}"

                status = row.get(status_key)
                zscore = row.get(zscore_key)

                if status is None or zscore is None:
                    continue

                if target_status == "all" or status == target_status:
                    include_row = True
                    row[zscore_key] = format_zscore_cell(zscore, status)
                else:
                    row[zscore_key] = "-"

        if selected_indicator == "weight_for_age":
            process("weight_for_age")
        elif selected_indicator == "weight_for_height":
            process("weight_for_height")
        elif selected_indicator == "height_for_age":
            process("height_for_age")

        if include_row or target_status == "all":
            filtered_data.append(row)

    return filtered_data

def format_zscore_cell(value, status):
    if value in (None, "-", "0", 0, "0.00"):
        return value
    
    color_map = {
        1: {"bg": "#FFCCCC", "text": "#CC0000"},  # Red for Severe
        2: {"bg": "#FFFFCC", "text": "#999900"},  # Yellow for Moderate
        3: {"bg": "#CCFFCC", "text": "#006600"},  # Green for Normal
    }
    
    colors = color_map.get(status, {"bg": "", "text": ""})
    
    if not colors["bg"]:
        return value
        
    return f"""
        <div style='
            background-color: {colors["bg"]};
            color: {colors["text"]};
            border-radius: 3px;
            text-align: center;
            font-weight: bold;
            padding: 2px 5px;
        '>
            {value}
        </div>
    """


















#backup Before age of creche Filter
# import frappe
# from frappe.utils import nowdate, getdate, date_diff
# from datetime import date
# import calendar

# def execute(filters=None):
#     if not filters:
#         filters = {}
    
#     # Calculate date range if month and year are provided
#     if filters.get("year") and filters.get("month"):
#         year = int(filters["year"])
#         month = int(filters["month"])
#         start_date = date(year, month, 1)
#         last_day = calendar.monthrange(year, month)[1]
#         end_date = date(year, month, last_day)
#         filters["end_date"] = end_date
    
#     columns = get_columns(filters)
#     data = get_exit_data(filters)
#     data = apply_conditional_formatting(data, filters)
#     return columns, data

# def get_columns(filters):
#     base_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
#         {"label": "Supervisor", "fieldname": "supervisor_name", "fieldtype": "Data", "width": 120},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 150},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 150},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
#         {"label": "Age (In Months at Exit)", "fieldname": "age_in_months", "fieldtype": "Int", "width": 175},
#         {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Date", "width": 150},
#         {"label": "Date of Exit", "fieldname": "date_of_exit", "fieldtype": "Date", "width": 130},
#         {"label": "Reason of Exit", "fieldname": "reason_of_exit", "fieldtype": "Data", "width": 150},
#         {"label": "Period of Stay (Months)", "fieldname": "duration_of_stay", "fieldtype": "Int", "width": 190},
#         {"label": "Weight at Enrollment (kg)", "fieldname": "weight_at_enrollment", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Height at Enrollment (cm)", "fieldname": "height_at_enrollment", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Weight at Exit (kg)", "fieldname": "weight_at_exit", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Height at Exit (cm)", "fieldname": "height_at_exit", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Measurement Status (At Exit)", "fieldname": "measurement_status", "fieldtype": "Data", "width": 250},
#     ]
    
#     # Add indicator-specific columns
#     indicator_columns = {
#         "weight_for_age": [
#             {"label": "Weight For Age Z Score (At Enrollment)", "fieldname": "weight_for_age_zscore_en", "fieldtype": "Data", "width": 340},
#             {"label": "Weight For Age Z Score (At Exit)", "fieldname": "weight_for_age_zscore_ex", "fieldtype": "Data", "width": 260},
#         ],
#         "weight_for_height": [
#             {"label": "Weight For Height Z Score (At Enrollment)", "fieldname": "weight_for_height_zscore_en", "fieldtype": "Data", "width": 370},
#             {"label": "Weight For Height Z Score (At Exit)", "fieldname": "weight_for_height_zscore_ex", "fieldtype": "Data", "width": 260},
#         ],
#         "height_for_age": [
#             {"label": "Height For Age Z Score (Enrollment)", "fieldname": "height_for_age_zscore_en", "fieldtype": "Data", "width": 340},
#             {"label": "Height For Age Z Score (At Exit)", "fieldname": "height_for_age_zscore_ex", "fieldtype": "Data", "width": 260},
#         ]
#     }
    
#     selected_indicator = filters.get("indicator", "weight_for_age")
#     base_columns.extend(indicator_columns.get(selected_indicator, indicator_columns["weight_for_age"]))
    
#     return base_columns

# def get_exit_data(filters):
#     if not filters:
#         filters = {}
    
#     conditions = []
#     params = {}
    
#     # Date filters
#     if filters.get("year"):
#         conditions.append("YEAR(ce.date_of_exit) = %(year)s")
#         params["year"] = filters.get("year")
    
#     if filters.get("month"):
#         conditions.append("MONTH(ce.date_of_exit) = %(month)s")
#         params["month"] = filters.get("month")
    
#     # Geography filters
#     geo_fields = ["state", "district", "block", "gp", "creche", "partner"]
#     for field in geo_fields:
#         if filters.get(field):
#             conditions.append(f"ce.{field}_id = %({field})s")
#             params[field] = filters.get(field)
    
#     # Other filters
#     if filters.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
        
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip()]
#         if phases:
#             conditions.append("cr.phase IN %(phases)s")
#             params["phases"] = phases
    
#     if filters.get("gender"):
#         conditions.append("ce.gender_id = %(gender)s")
#         params["gender"] = filters.get("gender")

#     if filters.get("reason_of_exit"):
#         conditions.append("ce.reason_for_exit = %(reason_of_exit)s")
#         params["reason_of_exit"] = filters.get("reason_of_exit")
    
#     if filters.get("duration_of_stay"):
#         age_months = int(filters["duration_of_stay"].replace("m", ""))
#         conditions.append("""
#             TIMESTAMPDIFF(MONTH, ce.date_of_enrollment, ce.date_of_exit) = %(age_months)s
#         """)
#         params["age_months"] = age_months
    
#     # Category filter
#     selected_category = filters.get("category", "all")
#     selected_indicator = filters.get("indicator", "weight_for_age")
    
#     if selected_category != "all":
#         category_mapping = {
#             "Severe": 1,
#             "Moderate": 2,
#             "Normal": 3
#         }
#         status_value = category_mapping.get(selected_category)
        
#         indicator_field_map = {
#             "weight_for_age": "weight_for_age",
#             "weight_for_height": "weight_for_height",
#             "height_for_age": "height_for_age"
#         }
        
#         field = indicator_field_map.get(selected_indicator, "weight_for_age")
#         conditions.append(f"(enrollment_data.{field} = %(status_value)s OR exit_data.{field} = %(status_value)s)")
#         params["status_value"] = status_value
        
#     # Build the query
#     conditions_sql = " AND ".join(conditions) if conditions else "1=1"
    
#     query = f"""
#     SELECT
#         st.state_name AS state,
#         p.partner_name AS partner,
#         d.district_name AS district,
#         b.block_name AS block,
#         gp.gp_name AS gp,
#         cr.creche_name AS creche,
#         ce.child_id AS child_id,
#         ce.child_name AS child_name,
#         u.full_name AS supervisor_name,
#         CASE WHEN ce.gender_id = 1 THEN 'M' ELSE 'F' END AS gender,
#         ce.date_of_enrollment AS date_of_enrollment,
#         ce.date_of_exit AS date_of_exit,
#         ce.reason_for_exit AS reason_for_exit,
        
#         /* Enrollment data */
#         CASE 
#             WHEN IFNULL(enrollment_data.weight, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.weight, 2), 2)
#         END AS weight_at_enrollment,
#         CASE 
#             WHEN IFNULL(enrollment_data.height, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.height, 2), 2)
#         END AS height_at_enrollment,
        
#         /* All z-scores at enrollment */
#         CASE 
#             WHEN IFNULL(enrollment_data.weight_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.weight_for_age_zscore, 2), 2)
#         END AS weight_for_age_zscore_en,
#         CASE 
#             WHEN IFNULL(enrollment_data.weight_for_height_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.weight_for_height_zscore, 2), 2)
#         END AS weight_for_height_zscore_en,
#         CASE 
#             WHEN IFNULL(enrollment_data.height_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.height_for_age_zscore, 2), 2)
#         END AS height_for_age_zscore_en,
        
#         /* Status at enrollment */
#         enrollment_data.weight_for_age AS weight_for_age_status_en,
#         enrollment_data.weight_for_height AS weight_for_height_status_en,
#         enrollment_data.height_for_age AS height_for_age_status_en,
        
#         /* Exit data */
#         CASE 
#             WHEN IFNULL(exit_data.weight, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.weight, 2), 2)
#         END AS weight_at_exit,
#         CASE 
#             WHEN IFNULL(exit_data.height, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.height, 2), 2)
#         END AS height_at_exit,
        
#         /* All z-scores at exit */
#         CASE 
#             WHEN IFNULL(exit_data.weight_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.weight_for_age_zscore, 2), 2)
#         END AS weight_for_age_zscore_ex,
#         CASE 
#             WHEN IFNULL(exit_data.weight_for_height_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.weight_for_height_zscore, 2), 2)
#         END AS weight_for_height_zscore_ex,
#         CASE 
#             WHEN IFNULL(exit_data.height_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.height_for_age_zscore, 2), 2)
#         END AS height_for_age_zscore_ex,
        
#         /* Status at exit */
#         exit_data.weight_for_age AS weight_for_age_status_ex,
#         exit_data.weight_for_height AS weight_for_height_status_ex,
#         exit_data.height_for_age AS height_for_age_status_ex,
        
#         /* Measurement status */
#         CASE
#             WHEN IFNULL(exit_data.weight, 0) = 0 AND IFNULL(exit_data.height, 0) = 0 THEN 'Not Available'
#             WHEN IFNULL(exit_data.weight, 0) = 0 THEN 'Weight at exit not available'
#             WHEN IFNULL(exit_data.height, 0) = 0 THEN 'Height at exit not available'
#             ELSE 'Available'
#         END AS measurement_status,
        
#         TIMESTAMPDIFF(MONTH, ce.child_dob, %(end_date)s) AS age_in_months,
#         TIMESTAMPDIFF(MONTH, ce.date_of_enrollment, ce.date_of_exit) AS duration_of_stay,
#         CASE ce.reason_for_exit
#             WHEN 1 THEN 'Migrated'
#             WHEN 2 THEN 'Graduated'
#             WHEN 3 THEN 'Not willing to stay'
#             WHEN 4 THEN 'Death'
#             WHEN 5 THEN 'Other'
#             ELSE 'Unknown'
#         END AS reason_of_exit
#     FROM
#         `tabChild Enrollment and Exit` ce
#     JOIN
#         `tabCreche` cr ON ce.creche_id = cr.name
#     LEFT JOIN
#         `tabPartner` p ON cr.partner_id = p.name
#     LEFT JOIN
#         `tabState` st ON cr.state_id = st.name
#     LEFT JOIN
#         `tabDistrict` d ON cr.district_id = d.name
#     LEFT JOIN
#         `tabBlock` b ON cr.block_id = b.name
#     LEFT JOIN
#         `tabGram Panchayat` gp ON cr.gp_id = gp.name
#     LEFT JOIN 
#         `tabUser` AS u ON u.name = cr.supervisor_id

#     /* Enrollment data join */
#     LEFT JOIN `tabAnthropromatic Data` as enrollment_data 
#         ON ce.childenrollguid = enrollment_data.childenrollguid
#         AND MONTH(enrollment_data.measurement_taken_date) = MONTH(ce.date_of_enrollment)
#         AND YEAR(enrollment_data.measurement_taken_date) = YEAR(ce.date_of_enrollment)
#     LEFT JOIN `tabChild Growth Monitoring` as cgm_enroll 
#         ON cgm_enroll.name = enrollment_data.parent
        
#     /* Exit data join */
#     LEFT JOIN `tabAnthropromatic Data` as exit_data 
#         ON ce.childenrollguid = exit_data.childenrollguid
#         AND MONTH(exit_data.measurement_taken_date) = MONTH(ce.date_of_exit)
#         AND YEAR(exit_data.measurement_taken_date) = YEAR(ce.date_of_exit)
#     LEFT JOIN `tabChild Growth Monitoring` as cgm_exit 
#         ON cgm_exit.name = exit_data.parent
    
#     WHERE
#         ce.date_of_exit IS NOT NULL
#         AND {conditions_sql}
#     ORDER BY
#         p.partner_name, st.state_name, d.district_name,
#         b.block_name, gp.gp_name, cr.creche_name, ce.child_name, ce.date_of_exit
# """
    
#     # Add end_date to params if it exists in filters
#     if "end_date" in filters:
#         params["end_date"] = filters["end_date"]
    
#     data = frappe.db.sql(query, params, as_dict=True)
#     return data

# def apply_conditional_formatting(data, filters):
#     if not data:
#         return data

#     selected_indicator = filters.get("indicator", "weight_for_age")
#     selected_category = filters.get("category", "all").lower()

#     category_map = {
#         "severe": 1,
#         "moderate": 2,
#         "normal": 3,
#         "all": "all"
#     }
#     target_status = category_map.get(selected_category)

#     filtered_data = []

#     for row in data:
#         include_row = False

#         def process(field_prefix):
#             nonlocal include_row
#             for suffix in ["en", "ex"]:
#                 status_key = f"{field_prefix}_status_{suffix}"
#                 zscore_key = f"{field_prefix}_zscore_{suffix}"

#                 status = row.get(status_key)
#                 zscore = row.get(zscore_key)

#                 if status is None or zscore is None:
#                     continue

#                 if target_status == "all" or status == target_status:
#                     include_row = True
#                     row[zscore_key] = format_zscore_cell(zscore, status)
#                 else:
#                     row[zscore_key] = "-"

#         if selected_indicator == "weight_for_age":
#             process("weight_for_age")
#         elif selected_indicator == "weight_for_height":
#             process("weight_for_height")
#         elif selected_indicator == "height_for_age":
#             process("height_for_age")

#         if include_row or target_status == "all":
#             filtered_data.append(row)

#     return filtered_data

# def format_zscore_cell(value, status):
#     if value in (None, "-", "0", 0, "0.00"):
#         return value
    
#     color_map = {
#         1: {"bg": "#FFCCCC", "text": "#CC0000"},  # Red for Severe
#         2: {"bg": "#FFFFCC", "text": "#999900"},  # Yellow for Moderate
#         3: {"bg": "#CCFFCC", "text": "#006600"},  # Green for Normal
#     }
    
#     colors = color_map.get(status, {"bg": "", "text": ""})
    
#     if not colors["bg"]:
#         return value
        
#     return f"""
#         <div style='
#             background-color: {colors["bg"]};
#             color: {colors["text"]};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 2px 5px;
#         '>
#             {value}
#         </div>
#     """














# # (04-07-2025 backup)
# import frappe
# from frappe.utils import nowdate, getdate, date_diff
# from datetime import date

# def execute(filters=None):
#     if not filters:
#         filters = {}
    
#     columns = get_columns(filters)
#     data = get_exit_data(filters)
#     data = apply_conditional_formatting(data, filters)
#     return columns, data

# def get_columns(filters):
#     base_columns = [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
#         {"label": "Supervisor", "fieldname": "supervisor_name", "fieldtype": "Data", "width": 120},
#         {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 150},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 150},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
#         {"label": "Age (In Months at Exit)", "fieldname": "age_in_months", "fieldtype": "Int", "width": 175},
#         {"label": "Date of Enrollment", "fieldname": "date_of_enrollment", "fieldtype": "Date", "width": 150},
#         {"label": "Date of Exit", "fieldname": "date_of_exit", "fieldtype": "Date", "width": 130},
#         {"label": "Reason of Exit", "fieldname": "reason_of_exit", "fieldtype": "Data", "width": 150},
#         {"label": "Period of Stay (Months)", "fieldname": "duration_of_stay", "fieldtype": "Int", "width": 190},
        
#         {"label": "Weight at Enrollment (kg)", "fieldname": "weight_at_enrollment", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Height at Enrollment (cm)", "fieldname": "height_at_enrollment", "fieldtype": "Data", "width": 200, "align": "right"},
      
#         {"label": "Weight at Exit (kg)", "fieldname": "weight_at_exit", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Height at Exit (cm)", "fieldname": "height_at_exit", "fieldtype": "Data", "width": 200, "align": "right"},
#         {"label": "Measurement Status (At Exit)", "fieldname": "measurement_status", "fieldtype": "Data", "width": 250},
#     ]
    
#     # Get selected indicator or default to weight_for_age
#     selected_indicator = filters.get("indicator", "weight_for_age")
    
#     # Add indicator-specific columns
#     if selected_indicator == "weight_for_age":
#         base_columns.extend([
#             {"label": "Weight For Age Z Score (At Enrollment)", "fieldname": "weight_for_age_zscore_en", "fieldtype": "Data", "width": 290},
#             {"label": "Weight For Age Z Score (At Exit)", "fieldname": "weight_for_age_zscore_ex", "fieldtype": "Data", "width": 250},
#         ])
#     elif selected_indicator == "weight_for_height":
#         base_columns.extend([
#             {"label": "Weight For Height Z Score (At Enrollment)", "fieldname": "weight_for_height_zscore_en", "fieldtype": "Data", "width": 290},
#             {"label": "Weight For Height Z Score (At Exit)", "fieldname": "weight_for_height_zscore_ex", "fieldtype": "Data", "width": 250},
#         ])
#     elif selected_indicator == "height_for_age":
#         base_columns.extend([
#             {"label": "Height For Age Z Score (At Enrollment)", "fieldname": "height_for_age_zscore_en", "fieldtype": "Data", "width": 290},
#             {"label": "Height For Age Z Score (At Exit)", "fieldname": "height_for_age_zscore_ex", "fieldtype": "Data", "width": 250},
#         ])
    
#     return base_columns

# def get_exit_data(filters):
#     if not filters:
#         filters = {}
    
#     conditions = []
#     params = {}
    
#     # Date filters
#     if filters.get("year"):
#         conditions.append("YEAR(ce.date_of_exit) = %(year)s")
#         params["year"] = filters.get("year")
    
#     if filters.get("month"):
#         conditions.append("MONTH(ce.date_of_exit) = %(month)s")
#         params["month"] = filters.get("month")
    
#     # Geography filters
#     if filters.get("state"):
#         conditions.append("cr.state = %(state)s")
#         params["state"] = filters.get("state")
    
#     if filters.get("district"):
#         conditions.append("cr.district = %(district)s")
#         params["district"] = filters.get("district")
    
#     if filters.get("block"):
#         conditions.append("cr.block = %(block)s")
#         params["block"] = filters.get("block")
    
#     if filters.get("gp"):
#         conditions.append("cr.gp = %(gp)s")
#         params["gp"] = filters.get("gp")
    
#     if filters.get("creche"):
#         conditions.append("ce.creche_id = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("partner"):
#         conditions.append("cr.partner = %(partner)s")
#         params["partner"] = filters.get("partner")
    
#     # Other filters
#     if filters.get("supervisor_id"):
#         conditions.append("cr.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("cr.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
        
#     if filters.get("phases"):
#         phases = [p.strip() for p in filters["phases"].split(",") if p.strip()]
#         if phases:
#             conditions.append("cr.phase IN %(phases)s")
#             params["phases"] = phases
            	
#     if filters.get("gender"):
#         conditions.append("ce.gender_id = %(gender)s")
#         params["gender"] = filters.get("gender")
    
#     if filters.get("duration_of_stay"):
#         age_months = int(filters["duration_of_stay"].replace("m", ""))
#         conditions.append("""
#             TIMESTAMPDIFF(MONTH, ce.child_dob, STR_TO_DATE(CONCAT(%(year)s, '-', %(month)s, '-01'), '%%Y-%%m-%%d')) = %(age_months)s
#         """)
#         params["age_months"] = age_months
    
#     # Category filter - Add to WHERE conditions
#     selected_category = filters.get("category", "all")
#     selected_indicator = filters.get("indicator", "weight_for_age")
    
#     if selected_category != "all":
#         # Map category names to status values (1=Severe, 2=Moderate, 3=Normal)
#         category_mapping = {
#             "Severe": 1,
#             "Moderate": 2,
#             "Normal": 3
#         }
#         status_value = category_mapping.get(selected_category)
        
#         # Determine which status field to filter based on selected indicator
#         if selected_indicator == "weight_for_age":
#             conditions.append("(enrollment_data.weight_for_age = %(status_value)s OR exit_data.weight_for_age = %(status_value)s)")
#         elif selected_indicator == "weight_for_height":
#             conditions.append("(enrollment_data.weight_for_height = %(status_value)s OR exit_data.weight_for_height = %(status_value)s)")
#         elif selected_indicator == "height_for_age":
#             conditions.append("(enrollment_data.height_for_age = %(status_value)s OR exit_data.height_for_age = %(status_value)s)")
        
#         params["status_value"] = status_value
        
#     # Build the query with proper table joins
#     conditions_sql = " AND ".join(conditions) if conditions else "1=1"
    
#     query = f"""
#     SELECT
#         st.state_name AS state,
#         p.partner_name AS partner,
#         d.district_name AS district,
#         b.block_name AS block,
#         gp.gp_name AS gp,
#         cr.creche_name AS creche,
#         ce.child_id AS child_id,
#         ce.child_name AS child_name,
#         u.full_name AS supervisor_name,
#         CASE WHEN ce.gender_id = 1 THEN 'M' ELSE 'F' END AS gender,
#         ce.date_of_enrollment AS date_of_enrollment,
#         ce.date_of_exit AS date_of_exit,
        
#         /* Enrollment data */
#         CASE 
#             WHEN IFNULL(enrollment_data.weight, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.weight, 2), 2)
#         END AS weight_at_enrollment,
#         CASE 
#             WHEN IFNULL(enrollment_data.height, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.height, 2), 2)
#         END AS height_at_enrollment,
        
#         /* All z-scores at enrollment */
#         CASE 
#             WHEN IFNULL(enrollment_data.weight_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.weight_for_age_zscore, 2), 2)
#         END AS weight_for_age_zscore_en,
#         CASE 
#             WHEN IFNULL(enrollment_data.weight_for_height_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.weight_for_height_zscore, 2), 2)
#         END AS weight_for_height_zscore_en,
#         CASE 
#             WHEN IFNULL(enrollment_data.height_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(enrollment_data.height_for_age_zscore, 2), 2)
#         END AS height_for_age_zscore_en,
        
#         /* Status at enrollment */
#         enrollment_data.weight_for_age AS weight_for_age_status_en,
#         enrollment_data.weight_for_height AS weight_for_height_status_en,
#         enrollment_data.height_for_age AS height_for_age_status_en,
        
#         /* Exit data */
#         CASE 
#             WHEN IFNULL(exit_data.weight, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.weight, 2), 2)
#         END AS weight_at_exit,
#         CASE 
#             WHEN IFNULL(exit_data.height, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.height, 2), 2)
#         END AS height_at_exit,
        
#         /* All z-scores at exit */
#         CASE 
#             WHEN IFNULL(exit_data.weight_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.weight_for_age_zscore, 2), 2)
#         END AS weight_for_age_zscore_ex,
#         CASE 
#             WHEN IFNULL(exit_data.weight_for_height_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.weight_for_height_zscore, 2), 2)
#         END AS weight_for_height_zscore_ex,
#         CASE 
#             WHEN IFNULL(exit_data.height_for_age_zscore, 0) = 0 THEN '-'
#             ELSE FORMAT(ROUND(exit_data.height_for_age_zscore, 2), 2)
#         END AS height_for_age_zscore_ex,
        
#         /* Status at exit */
#         exit_data.weight_for_age AS weight_for_age_status_ex,
#         exit_data.weight_for_height AS weight_for_height_status_ex,
#         exit_data.height_for_age AS height_for_age_status_ex,

#         /* Measurement status */
#         CASE
#             WHEN IFNULL(exit_data.weight, 0) = 0 AND IFNULL(exit_data.height, 0) = 0 THEN 'Not Available'
#             WHEN IFNULL(exit_data.weight, 0) = 0 THEN 'Weight at exit not available'
#             WHEN IFNULL(exit_data.height, 0) = 0 THEN 'Height at exit not available'
#             ELSE 'Available'
#         END AS measurement_status,
        
#         TIMESTAMPDIFF(MONTH, ce.child_dob, STR_TO_DATE(CONCAT(%(year)s, '-', %(month)s, '-01'), '%%Y-%%m-%%d')) AS age_in_months,
#         TIMESTAMPDIFF(MONTH, ce.date_of_enrollment, ce.date_of_exit) AS duration_of_stay,
#         CASE ce.reason_for_exit
#             WHEN 1 THEN 'Migrated'
#             WHEN 2 THEN 'Graduated'
#             WHEN 3 THEN 'Not willing to stay'
#             WHEN 4 THEN 'Death'
#             WHEN 5 THEN 'Other'
#             ELSE 'Unknown'
#         END AS reason_of_exit
#     FROM
#         `tabChild Enrollment and Exit` ce
#     JOIN
#         `tabCreche` cr ON ce.creche_id = cr.name
#     LEFT JOIN
#         `tabPartner` p ON cr.partner_id = p.name
#     LEFT JOIN
#         `tabState` st ON cr.state_id = st.name
#     LEFT JOIN
#         `tabDistrict` d ON cr.district_id = d.name
#     LEFT JOIN
#         `tabBlock` b ON cr.block_id = b.name
#     LEFT JOIN
#         `tabGram Panchayat` gp ON cr.gp_id = gp.name
#     LEFT JOIN 
#         `tabUser` AS u ON u.name = cr.supervisor_id

#     /* Enrollment data join */
#     LEFT JOIN `tabAnthropromatic Data` as enrollment_data 
#         ON ce.childenrollguid = enrollment_data.childenrollguid
#         AND MONTH(enrollment_data.measurement_taken_date) = MONTH(ce.date_of_enrollment)
#         AND YEAR(enrollment_data.measurement_taken_date) = YEAR(ce.date_of_enrollment)
#     LEFT JOIN `tabChild Growth Monitoring` as cgm_enroll 
#         ON cgm_enroll.name = enrollment_data.parent
        
#     /* Exit data join */
#     LEFT JOIN `tabAnthropromatic Data` as exit_data 
#         ON ce.childenrollguid = exit_data.childenrollguid
#         AND MONTH(exit_data.measurement_taken_date) = %(month)s
#         AND YEAR(exit_data.measurement_taken_date) = %(year)s
#     LEFT JOIN `tabChild Growth Monitoring` as cgm_exit 
#         ON cgm_exit.name = exit_data.parent
    
#     WHERE
#         ce.date_of_exit IS NOT NULL
#         AND {conditions_sql}
#     ORDER BY
#         p.partner_name, st.state_name, d.district_name,
#         b.block_name, gp.gp_name, cr.creche_name, ce.child_name, ce.date_of_exit
# """
    
#     data = frappe.db.sql(query, params, as_dict=True)
#     return data

# def apply_conditional_formatting(data, filters):
#     if not data:
#         return data

#     selected_indicator = filters.get("indicator", "weight_for_age")
#     selected_category = filters.get("category", "all").lower()

#     category_map = {
#         "severe": 1,
#         "moderate": 2,
#         "normal": 3,
#         "all": "all"
#     }
#     target_status = category_map.get(selected_category)

#     filtered_data = []

#     for row in data:
#         include_row = False

#         def process(field_prefix):
#             nonlocal include_row
#             for suffix in ["en", "ex"]:
#                 status_key = f"{field_prefix}_status_{suffix}"
#                 zscore_key = f"{field_prefix}_zscore_{suffix}"

#                 status = row.get(status_key)
#                 zscore = row.get(zscore_key)

#                 if status is None or zscore is None:
#                     continue

#                 if target_status == "all" or status == target_status:
#                     include_row = True
#                     row[zscore_key] = format_zscore_cell(zscore, status)
#                 else:
#                     # Clear value so unwanted categories appear blank
#                     row[zscore_key] = "-"  # Or just leave it None

#         if selected_indicator == "weight_for_age":
#             process("weight_for_age")
#         elif selected_indicator == "weight_for_height":
#             process("weight_for_height")
#         elif selected_indicator == "height_for_age":
#             process("height_for_age")

#         if include_row:
#             filtered_data.append(row)

#     return filtered_data



# def format_zscore_cell(value, status):
#     if value in (None, "-", "0", 0, "0.00"):
#         return value
    
#     # Define colors based on status (1=Red, 2=Yellow, 3=Green)
#     color_map = {
#         1: {"bg": "#FFCCCC", "text": "#CC0000"},  # Red for Severe
#         2: {"bg": "#FFFFCC", "text": "#999900"},  # Yellow for Moderate
#         3: {"bg": "#CCFFCC", "text": "#006600"},  # Green for Normal
#     }
    
#     colors = color_map.get(status, {"bg": "", "text": ""})
    
#     if not colors["bg"]:
#         return value
        
#     return f"""
#         <div style='
#             background-color: {colors["bg"]};
#             color: {colors["text"]};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#             padding: 2px 5px;
#         '>
#             {value}
#         </div>
#     """


