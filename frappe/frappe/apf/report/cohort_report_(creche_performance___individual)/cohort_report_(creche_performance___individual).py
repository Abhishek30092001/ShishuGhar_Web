from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, date
import calendar
from dateutil.relativedelta import relativedelta

def execute(filters=None):
    if not filters:
        filters = {}
   
    target_year = int(filters.get("year")) if filters.get("year") else datetime.now().year
    target_month = int(filters.get("month")) if filters.get("month") else datetime.now().month
   
    target_date = date(target_year, target_month, 1)
    target_label = target_date.strftime("%b-%y")
   
    # Base columns that are always shown
    base_columns = [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
        {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
        {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
        {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 160},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 180},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 120},
        {"label": "Date of Enrollment", "fieldname": "enrollment_date", "fieldtype": "Data", "width": 150},
        {"label": "Date of Exit", "fieldname": "exit_date", "fieldtype": "Data", "width": 150},
        {"label": "First Measurement Date", "fieldname": "first_measurement_date", "fieldtype": "Data", "width": 260},
        {"label": "First Height (cm)", "fieldname": "first_height", "fieldtype": "Data", "width": 180},
        {"label": "First Weight (kg)", "fieldname": "first_weight", "fieldtype": "Data", "width": 180},
    ]
   
    # Z-score columns – shown only if the corresponding indicator is selected
    indicator = filters.get("indicator")
    first_wfa_col = {"label": "First WFA Z-Score", "fieldname": "first_wfa_zscore", "fieldtype": "Data", "width": 220}
    first_wfh_col = {"label": "First WFH Z-Score", "fieldname": "first_wfh_zscore", "fieldtype": "Data", "width": 220}
    last_wfa_col = {"label": f"Last WFA Z-Score ({target_label})", "fieldname": "last_wfa_zscore", "fieldtype": "Data", "width": 220}
    last_wfh_col = {"label": f"Last WFH Z-Score ({target_label})", "fieldname": "last_wfh_zscore", "fieldtype": "Data", "width": 220}
   
    # Columns after the first measurements (always shown)
    middle_columns = [
        {"label": f"Last Measurement Date ({target_label})", "fieldname": "last_measurement_date", "fieldtype": "Data", "width": 260},
        {"label": f"Last Height ({target_label})", "fieldname": "last_height", "fieldtype": "Data", "width": 180},
        {"label": f"Last Weight ({target_label})", "fieldname": "last_weight", "fieldtype": "Data", "width": 180},
    ]
   
    # New column for Average Attendance
    attendance_col = {"label": "Avg. Attendance (%)", "fieldname": "avg_attendance", "fieldtype": "Data", "width": 180}
   
    # Build final column list based on indicator
    columns = base_columns[:]
    if indicator == "weight_for_age":
        columns.append(first_wfa_col)
    elif indicator == "weight_for_height":
        columns.append(first_wfh_col)
    else:
        columns.append(first_wfa_col)
        columns.append(first_wfh_col)
   
    columns.extend(middle_columns)
   
    if indicator == "weight_for_age":
        columns.append(last_wfa_col)
    elif indicator == "weight_for_height":
        columns.append(last_wfh_col)
    else:
        columns.append(last_wfa_col)
        columns.append(last_wfh_col)
   
    # Attendance column at the very end
    columns.append(attendance_col)



    # ------------------------------------------------------------------
    # Indicator-based column hiding: for weight_for_age, remove height columns
    # ------------------------------------------------------------------
    if indicator == "weight_for_age":
        columns = [col for col in columns if col['fieldname'] not in ['first_height', 'last_height']]
   
    data = get_report_data(filters, target_month, target_year)
    
    # ------------------------------------------------------------
    # Attendance filter (backend)
    # ------------------------------------------------------------
    attendance_filter = filters.get("attedance")  # note the typo to match frontend fieldname
    if attendance_filter:
        # Remove any previously added total row (the last row if it's a total)
        if data and data[-1].get("is_total"):
            data.pop()
        
        filtered_data = []
        for row in data:
            avg_att = row.get("avg_attendance")
            if avg_att is None:
                continue
            try:
                avg_val = float(avg_att)
            except (ValueError, TypeError):
                continue
            if attendance_filter == "regular" and avg_val >= 70:
                filtered_data.append(row)
            elif attendance_filter == "irregular" and avg_val <= 50:
                filtered_data.append(row)
            # Otherwise skip the row
        data = filtered_data
        
        # Re‑add a correct total row if there is data
        if data:
            total_count = len(data)
            total_row = {
                "child_name": f"<b>Total Children: {total_count}</b>",
                "partner": "", "state": "", "district": "", "block": "", "gp": "",
                "supervisor_id": "", "creche": "", "creche_id": "", "child_id": "",
                "gender": "", "child_dob": "", "enrollment_date": "", "exit_date": "",
                "first_measurement_date": "", "first_height": "", "first_weight": "",
                "first_wfa_zscore": "", "first_wfh_zscore": "",
                "first_wfa": "", "first_wfh": "",
                "last_measurement_date": "", "last_height": "", "last_weight": "",
                "last_wfa_zscore": "", "last_wfh_zscore": "",
                "last_wfa": "", "last_wfh": "",
                "avg_attendance": "",
                "is_total": True
            }
            data.append(total_row)


    if indicator == "weight_for_height":
        # Only remove and re-add total row, do NOT filter rows
        if data and data[-1].get("is_total"):
            total_row = data.pop()
        else:
            total_row = None

        if total_row:
            data.append(total_row)
        
        # Re-add total row
        if data:
            total_count = len(data)
            total_row = {
                "child_name": f"<b>Total Children: {total_count}</b>",
                "partner": "", "state": "", "district": "", "block": "", "gp": "",
                "supervisor_id": "", "creche": "", "creche_id": "", "child_id": "",
                "gender": "", "child_dob": "", "enrollment_date": "", "exit_date": "",
                "first_measurement_date": "", "first_height": "", "first_weight": "",
                "first_wfa_zscore": "", "first_wfh_zscore": "",
                "first_wfa": "", "first_wfh": "",
                "last_measurement_date": "", "last_height": "", "last_weight": "",
                "last_wfa_zscore": "", "last_wfh_zscore": "",
                "last_wfa": "", "last_wfh": "",
                "avg_attendance": "",
                "is_total": True
            }
            data.append(total_row)
    # ------------------------------------------------------------
   
    data = apply_conditional_formatting(data, indicator)
   
    return columns, data


def get_report_data(filters, target_month, target_year):
    if not filters:
        filters = {}
    
    # --- Partner: default to current user's partner if not explicitly selected ---
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    # --- Geography: default to current user's geography mapping if not explicitly selected ---
    geography_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

    state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
    district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
    block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
    gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

    # 2. Date boundaries – exactly as in the reference summary report
    month_start = date(target_year, target_month, 1)                         # first day of selected month
    month_end_last = date(target_year, target_month,
                          calendar.monthrange(target_year, target_month)[1]) # last day of selected month

    next_month = target_month + 1 if target_month < 12 else 1
    next_year = target_year if target_month < 12 else target_year + 1
    month_end_first_next = date(next_year, next_month, 1)                   # first day of next month (for attendance <)

    if target_month > 1:
        fallback_month = target_month - 1
        fallback_year = target_year
    else:
        fallback_month = 12
        fallback_year = target_year - 1
    fallback_start = date(fallback_year, fallback_month, 1)                 # first day of previous month
    fallback_end = date(fallback_year, fallback_month,
                        calendar.monthrange(fallback_year, fallback_month)[1]) # last day of previous month

    # 3. Build parameters dictionary
    params = {
        "target_date": month_start,                    # for age group calculations
        "month_start": month_start,
        "month_end_last": month_end_last,              # last day of selected month (enrollment cutoff)
        "month_end_first_next": month_end_first_next,  # first day of next month (attendance cutoff)
        "fallback_start": fallback_start,
        "fallback_end": fallback_end,
        "partner": partner_id,
        "state": filters.get("state"),
        "district": filters.get("district"),
        "block": filters.get("block"),
        "gp": filters.get("gp"),
        "creche": filters.get("creche"),
        "supervisor_id": filters.get("supervisor_id"),
        "creche_status_id": filters.get("creche_status_id", "3"),
        "phases": filters.get("phases"),
        "gender": None,
        "cstart_date": filters.get("cstart_date"),
        "cend_date": filters.get("cend_date"),
        "creche_age": filters.get("creche_age"),
        "state_ids": tuple(state_ids_list) if state_ids_list else None,
        "district_ids": tuple(district_ids_list) if district_ids_list else None,
        "block_ids": tuple(block_ids_list) if block_ids_list else None,
        "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
    }

    # Gender mapping
    if filters.get("gender"):
        if filters["gender"] == "M":
            params["gender"] = "1"
        elif filters["gender"] == "F":
            params["gender"] = "2"
        else:
            params["gender"] = filters["gender"]

    # 4. Build WHERE conditions – same as summary report
    conditions = []

    conditions.append("cee.date_of_enrollment <= %(month_end_last)s")
    conditions.append("cr.name IS NOT NULL")

    if params.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status_id)s")
    else:
        conditions.append("cr.creche_status_id = 3")
        params["creche_status_id"] = 3

    if params.get("partner"):
        conditions.append("cr.partner_id = %(partner)s")

    if params.get("state"):
        conditions.append("cr.state_id = %(state)s")
    elif params.get("state_ids"):
        conditions.append("cr.state_id IN %(state_ids)s")

    if params.get("district"):
        conditions.append("cr.district_id = %(district)s")
    elif params.get("district_ids"):
        conditions.append("cr.district_id IN %(district_ids)s")

    if params.get("block"):
        conditions.append("cr.block_id = %(block)s")
    elif params.get("block_ids"):
        conditions.append("cr.block_id IN %(block_ids)s")

    if params.get("gp"):
        conditions.append("cr.gp_id = %(gp)s")
    elif params.get("gp_ids"):
        conditions.append("cr.gp_id IN %(gp_ids)s")

    if params.get("creche"):
        conditions.append("cr.name = %(creche)s")

    if params.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")

    if params.get("phases"):
        conditions.append("FIND_IN_SET(cr.phase, %(phases)s)")

    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"):
        conditions.append("DATE(cr.creche_opening_date) = %(cstart_date)s")

    # Creche Age filter – using first day of selected month as reference
    if params.get("creche_age"):
        conditions.append("""
            CASE 
                WHEN cr.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(month_start)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(month_start)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(month_start)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(month_start)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(month_start)s) >= 24 THEN '24+ Month'
                ELSE ''
            END = %(creche_age)s
        """)

    if params.get("gender"):
        conditions.append("cee.gender_id = %(gender)s")

    # --- Age group filter using TIMESTAMPDIFF ---
    age_filter_cond = ""
    if filters.get("age_group"):
        ag = filters["age_group"]
        if ag == "6m-11m":
            age_filter_cond = "AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date)s) BETWEEN 6 AND 11"
        elif ag == "12m-17m":
            age_filter_cond = "AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date)s) BETWEEN 12 AND 17"
        elif ag == "18m-23m":
            age_filter_cond = "AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date)s) BETWEEN 18 AND 23"
        elif ag == "24m-29m":
            age_filter_cond = "AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date)s) BETWEEN 24 AND 29"
        elif ag == "30m-36m":
            age_filter_cond = "AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date)s) BETWEEN 30 AND 36"
        elif ag == "> 36m":
            age_filter_cond = "AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date)s) > 36"
    if age_filter_cond:
        conditions.append(age_filter_cond[4:])  # remove 'AND '

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""


    indicator = filters.get("indicator")

    if indicator == "weight_for_height":
        indicator_field = "weight_for_height_zscore"
    else:
        indicator_field = "weight_for_age_zscore"

    # UPDATED QUERY with new measurement logic
    query = f"""
    SELECT DISTINCT
        cee.childenrollguid,
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

        DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS child_dob,
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS enrollment_date,
        DATE_FORMAT(cee.date_of_exit, '%%d-%%m-%%Y') AS exit_date,

        /* First measurement fields */
        DATE_FORMAT(m.first_date, '%%d-%%m-%%Y') AS first_measurement_date,
        ad_initial.height AS first_height,
        ad_initial.weight AS first_weight,
        ad_initial.weight_for_age_zscore AS first_wfa_zscore,
        ad_initial.weight_for_height_zscore AS first_wfh_zscore,
        ad_initial.weight_for_age AS first_wfa,
        ad_initial.weight_for_height AS first_wfh,

        /* Last measurement fields */
        DATE_FORMAT(m.last_date, '%%d-%%m-%%Y') AS last_measurement_date,
        ad_final.height AS last_height,
        ad_final.weight AS last_weight,
        ad_final.weight_for_age_zscore AS last_wfa_zscore,
        ad_final.weight_for_height_zscore AS last_wfh_zscore,
        ad_final.weight_for_age AS last_wfa,
        ad_final.weight_for_height AS last_wfh,

        attendance_avg.avg_monthly_attendance AS avg_attendance

    FROM `tabChild Enrollment and Exit` AS cee

    INNER JOIN `tabCreche` AS cr ON cee.creche_id = cr.name
    INNER JOIN `tabUser` AS usr ON cr.supervisor_id = usr.name
    INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
    INNER JOIN `tabState` AS s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
    INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` AS g ON g.name = cr.gp_id

    /* ---------- UPDATED Measurement Logic ---------- */
 
    LEFT JOIN (
        SELECT 
            childenrollguid,
            MIN(measurement_taken_date) AS first_date,
            MAX(measurement_taken_date) AS last_date
        FROM `tabAnthropromatic Data`
        WHERE do_you_have_height_weight = 1
            AND {indicator_field} IS NOT NULL
            AND TRIM({indicator_field}) <> ''
            AND measurement_taken_date <= %(month_end_last)s 
        GROUP BY childenrollguid
    ) m ON m.childenrollguid = cee.childenrollguid

    LEFT JOIN `tabAnthropromatic Data` ad_initial
        ON ad_initial.name = (
            SELECT name FROM `tabAnthropromatic Data` 
            WHERE childenrollguid = cee.childenrollguid 
            AND measurement_taken_date = m.first_date 

                AND do_you_have_height_weight = 1
                AND {indicator_field} IS NOT NULL
                AND TRIM({indicator_field}) <> ''
                AND measurement_taken_date <= %(month_end_last)s 
            ORDER BY name DESC LIMIT 1
        )

    LEFT JOIN `tabAnthropromatic Data` ad_final
        ON ad_final.name = (
            SELECT name FROM `tabAnthropromatic Data` 
            WHERE childenrollguid = cee.childenrollguid 
            AND measurement_taken_date = m.last_date 
            AND do_you_have_height_weight = 1
            AND {indicator_field} IS NOT NULL
            AND TRIM({indicator_field}) <> ''
            AND measurement_taken_date <= %(month_end_last)s 
            ORDER BY name DESC LIMIT 1
        )
    /* --------------------------------------------- */

    /* ---------- Attendance remains same ---------- */
    LEFT JOIN (
        SELECT 
            monthly.childenrolledguid,
            ROUND(AVG(monthly.monthly_attendance), 2) AS avg_monthly_attendance
        FROM (
            SELECT 
                cal.childenrolledguid,
                DATE_FORMAT(cal.date_of_attendance, '%%Y-%%m') AS ym,
                SUM(CASE WHEN cal.attendance = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS monthly_attendance
            FROM `tabChild Attendance List` cal
            INNER JOIN `tabChild Attendance` ca ON cal.parent = ca.name
            INNER JOIN `tabChild Enrollment and Exit` cee_att 
                ON cee_att.childenrollguid = cal.childenrolledguid
            WHERE 
                ca.is_shishu_ghar_is_closed_for_the_day = 0
                AND cal.date_of_attendance < %(month_end_first_next)s
                AND cal.date_of_attendance >= cee_att.date_of_enrollment
                AND (
                    cee_att.date_of_exit IS NULL 
                    OR cal.date_of_attendance <= cee_att.date_of_exit
                )
            GROUP BY cal.childenrolledguid, ym
        ) monthly
        GROUP BY monthly.childenrolledguid
    ) attendance_avg 
        ON attendance_avg.childenrolledguid = cee.childenrollguid

    {where_clause}

    ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name, cr.creche_name, cee.child_name;
    """

    data = frappe.db.sql(query, params, as_dict=True)

    # Add total row with child count in bold black
    if data:
        total_count = len(data)
        total_row = {
            "child_name": f"<b>Total Children: {total_count}</b>",
            # Leave other fields empty or set to None
            "partner": "", "state": "", "district": "", "block": "", "gp": "",
            "supervisor_id": "", "creche": "", "creche_id": "", "child_id": "",
            "gender": "", "child_dob": "", "enrollment_date": "", "exit_date": "",
            "first_measurement_date": "", "first_height": "", "first_weight": "",
            "first_wfa_zscore": "", "first_wfh_zscore": "",
            "first_wfa": "", "first_wfh": "",
            "last_measurement_date": "", "last_height": "", "last_weight": "",
            "last_wfa_zscore": "", "last_wfh_zscore": "",
            "last_wfa": "", "last_wfh": "",
            "avg_attendance": "",
            "is_total": True
        }
        data.append(total_row)

    return data


def apply_conditional_formatting(data, indicator):
    if indicator == "weight_for_age":
        status_fields = [("first_wfa", "first_wfa_zscore"), ("last_wfa", "last_wfa_zscore")]
    elif indicator == "weight_for_height":
        status_fields = [("first_wfh", "first_wfh_zscore"), ("last_wfh", "last_wfh_zscore")]
    else:
        status_fields = [
            ("first_wfa", "first_wfa_zscore"),
            ("first_wfh", "first_wfh_zscore"),
            ("last_wfa", "last_wfa_zscore"),
            ("last_wfh", "last_wfh_zscore")
        ]
   
    for row in data:
        if row.get("is_total"):
            continue
       
        for status_field, zscore_field in status_fields:
            status_value = row.get(status_field)
            zscore_value = row.get(zscore_field)
           
            if status_value is not None and status_value != '-' and zscore_value is not None and zscore_value != '-':
                try:
                    status = int(status_value)
                    zscore = float(zscore_value)
                   
                    if status == 1:
                        bg_color = "#FFCCCC"
                        text_color = "#CC0000"
                    elif status == 2:
                        bg_color = "#FFFFCC"
                        text_color = "#999900"
                    elif status == 3:
                        bg_color = "#CCFFCC"
                        text_color = "#006600"
                    else:
                        bg_color = "#E6E6E6"
                        text_color = "#666666"
                   
                    formatted_value = round(zscore, 2) if zscore is not None else '-'
                    row[zscore_field] = format_cell(formatted_value, bg_color, text_color)
                   
                except (ValueError, TypeError):
                    pass
   
    return data


def format_cell(value, bg_color, text_color):
    if value is None or value == '-':
        return value
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

