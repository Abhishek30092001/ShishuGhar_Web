from frappe import query_builder
from frappe import query_builder
import frappe
import calendar
import json
from datetime import date

CACHE_TTL = 900 

# =========================================================
# 1. Master Filter & Helper Functions
# =========================================================

def get_cache_key(api_name, kwargs):
    ignore_keys = ['cmd', '_']
    safe_kwargs = {k: str(v) for k, v in kwargs.items() if k not in ignore_keys}
    filter_string = json.dumps(safe_kwargs, sort_keys=True)
    current_user = frappe.session.user
    return f"dashboard_{api_name}_{current_user}_{filter_string}"

def get_master_filters(kwargs):
    # Helper to convert UI empty strings into true Python None types
    def clean_val(v):
        if v in [None, "", "null", "undefined", "None"]:
            return None
        return str(v).strip()

    year = clean_val(kwargs.get("year"))
    month = clean_val(kwargs.get("month"))
    
    selected_year = int(year) if year and year.isdigit() else date.today().year
    selected_month = int(month) if month and month.isdigit() else date.today().month
    
    target_m = selected_month
    target_y = selected_year

    start_date = date(target_y, target_m, 1)
    last_day = calendar.monthrange(target_y, target_m)[1]
    end_date = date(target_y, target_m, last_day)

    past_months = []
    curr_y = selected_year
    curr_m = selected_month
    
    past_months.append((curr_y, curr_m))
    for _ in range(5):
        curr_m -= 1
        if curr_m == 0:
            curr_m = 12
            curr_y -= 1
        past_months.append((curr_y, curr_m))
    
    past_months.reverse() 
    trend_start_date = date(past_months[0][0], past_months[0][1], 1)
    trend_end_date = end_date

    m1_y, m1_m = past_months[3]
    q2_start_date = date(m1_y, m1_m, 1)
    q2_end_date = end_date
    
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = clean_val(kwargs.get("partner_id")) or clean_val(current_user_partner)

    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    # Helper to safely flatten geography mappings and remove duplicates
    def get_clean_csv(data_list, key):
        values = list(set([str(s[key]).strip() for s in data_list if s.get(key)]))
        return ",".join(values) if values else None

    state_ids = get_clean_csv(current_user_state, "state_id")
    district_ids = get_clean_csv(current_user_state, "district_id")
    block_ids = get_clean_csv(current_user_state, "block_id")
    gp_ids = get_clean_csv(current_user_state, "gp_id")

    phases = clean_val(kwargs.get("phases"))
    phases = ",".join(p.strip() for p in phases.split(",") if p.strip().isdigit()) if phases else None

    c_status_val = clean_val(kwargs.get("c_status"))

    params = {
        "end_date": end_date, "start_date": start_date,
        "year": target_y, "month": target_m,
        "trend_start_date": trend_start_date, "trend_end_date": trend_end_date,
        "q2_start_date": q2_start_date, "q2_end_date": q2_end_date,
        "partner_id": partner_id,
        "state_id": clean_val(kwargs.get("state_id")), "state_ids": state_ids,
        "district_id": clean_val(kwargs.get("district_id")), "district_ids": district_ids,
        "block_id": clean_val(kwargs.get("block_id")), "block_ids": block_ids,
        "gp_id": clean_val(kwargs.get("gp_id")), "gp_ids": gp_ids,
        "creche_id": clean_val(kwargs.get("creche_id")),
        "supervisor_id": clean_val(kwargs.get("supervisor_id")),
        "cstart_date": clean_val(kwargs.get("cstart_date")),
        "cend_date": clean_val(kwargs.get("cend_date")),
        "c_status": int(c_status_val) if c_status_val else 3,
        "phases": phases
    }

    # FIXED: Split logic securely into UI Filter constraints AND User Role Profile constraints
    common_filters_cr = """
        AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
        
        /* 1. UI Selected Filters */
        AND (%(state_id)s IS NULL OR cr.state_id = %(state_id)s)
        AND (%(district_id)s IS NULL OR cr.district_id = %(district_id)s)
        AND (%(block_id)s IS NULL OR cr.block_id = %(block_id)s)
        AND (%(gp_id)s IS NULL OR cr.gp_id = %(gp_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        
        /* 2. User Geography Profile Enforcements (Prevents UI bypasses) */
        AND (%(state_ids)s IS NULL OR FIND_IN_SET(cr.state_id, %(state_ids)s))
        AND (%(district_ids)s IS NULL OR FIND_IN_SET(cr.district_id, %(district_ids)s))
        AND (%(block_ids)s IS NULL OR FIND_IN_SET(cr.block_id, %(block_ids)s))
        AND (%(gp_ids)s IS NULL OR FIND_IN_SET(cr.gp_id, %(gp_ids)s))
    """

    return params, common_filters_cr, past_months

def return_count(data):
    result = data[0] if data else {}
    return result.get("count", 0)

# =========================================================
# 2. SQL Generators
# =========================================================

def get_avg_creche_opened_query(common_filters_cr):
    return f"""
        SELECT
            CASE
                WHEN FR.creche_no = 0 THEN 0
                ELSE CEIL(FR.no_days_creche_opened / FR.creche_no)
            END AS count
        FROM (
            SELECT
                (SELECT COUNT(*)
                 FROM `tabCreche` cr
                 WHERE 1=1
                 {common_filters_cr}
                 AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                 AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                ) AS creche_no,

                (SELECT COUNT(*)
                 FROM `tabChild Attendance` ca
                 JOIN `tabCreche` cr ON cr.name = ca.creche_id
                 WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
                   AND YEAR(ca.date_of_attendance) = %(year)s
                   AND MONTH(ca.date_of_attendance) = %(month)s
                   {common_filters_cr}
                   AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                   AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                ) AS no_days_creche_opened
        ) FR;
    """

def get_avg_creche_closed_query(common_filters_cr):
    return f"""
        SELECT
            CASE
                WHEN FR.creche_no = 0 THEN 0
                ELSE CEIL(FR.no_days_creche_closed / FR.creche_no)
            END AS count
        FROM (
            SELECT
                (SELECT COUNT(*)
                 FROM `tabCreche` cr
                 WHERE 1=1
                 {common_filters_cr}
                 AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                 AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                ) AS creche_no,

                (SELECT COUNT(*)
                 FROM `tabChild Attendance` ca
                 JOIN `tabCreche` cr ON cr.name = ca.creche_id
                 WHERE ca.is_shishu_ghar_is_closed_for_the_day = 1
                   AND YEAR(ca.date_of_attendance) = %(year)s
                   AND MONTH(ca.date_of_attendance) = %(month)s
                   {common_filters_cr}
                   AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                   AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                ) AS no_days_creche_closed
        ) FR;
    """

def get_code1_not_submitted_query(common_filters_cr):
    return f"""
        SELECT cr.creche_id AS "Creche ID", cr.creche_name AS "Creche Name",
            CASE 
                WHEN cr.creche_status_id = 1 THEN 'Planned'
                WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
                WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN cr.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name AS "GP", b.block_name AS "Block", d.district_name AS "District",
            s.state_name AS "State", p.partner_name AS "Partner"
        FROM `tabCreche` cr
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS attdays 
            FROM `tabChild Attendance`
            WHERE date_of_attendance BETWEEN %(start_date)s AND %(end_date)s 
            GROUP BY creche_id
        ) att ON cr.name = att.creche_id
        INNER JOIN `tabPartner` p ON cr.partner_id = p.name
        INNER JOIN `tabState` s ON cr.state_id = s.name
        INNER JOIN `tabDistrict` d ON cr.district_id = d.name
        INNER JOIN `tabBlock` b ON cr.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
        WHERE 1=1 {common_filters_cr}
        AND cr.creche_opening_date IS NOT NULL 
        AND cr.creche_opening_date <= %(end_date)s
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        AND (DATEDIFF(
            CASE WHEN %(end_date)s > CURRENT_DATE() THEN CURRENT_DATE() ELSE %(end_date)s END, 
            CASE WHEN cr.creche_opening_date < %(start_date)s THEN %(start_date)s ELSE cr.creche_opening_date END
        ) + 1) > IFNULL(att.attdays, 0)
    """

def get_code1_creche_24_query(common_filters_cr):
    return f"""
        SELECT 
            usr.full_name as "Supervisor", cr.creche_name as "Creche Name ",
            IFNULL(agg.total_opened, 0) AS "Total No of Day Creche Opened",
            agg.date_of_closing AS "Date of Closing",
            rfc.add_reason_for_closure AS "Reason for Closer"
        FROM `tabCreche` cr
        INNER JOIN (
            SELECT creche_id, 
                   SUM(CASE WHEN is_shishu_ghar_is_closed_for_the_day = 0 THEN 1 ELSE 0 END) AS total_opened,
                   MAX(CASE WHEN is_shishu_ghar_is_closed_for_the_day = 1 THEN date_of_attendance ELSE NULL END) as date_of_closing,
                   MAX(reason_for_closure_id) as reason_id
            FROM `tabChild Attendance`
            WHERE date_of_attendance BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY creche_id
        ) agg ON cr.name = agg.creche_id
        LEFT JOIN `tabUser` usr ON usr.name = cr.supervisor_id
        LEFT JOIN `tabReason for Closure` rfc ON rfc.name = agg.reason_id
        WHERE 1=1 {common_filters_cr}
    """

def get_code1_trend_query(past_months, trend_condition, trend_label, common_filters_cr):
    month_cases = []
    month_names = []
    for y, m in past_months:
        m_name = calendar.month_abbr[m]
        month_names.append(m_name)
        case_statement = f"COUNT(DISTINCT CASE WHEN YEAR(date_of_attendance) = {y} AND MONTH(date_of_attendance) = {m} THEN date_of_attendance END) AS `{m_name}`"
        month_cases.append(case_statement)
    
    month_cases_sql = ",\n                ".join(month_cases)
    q1_names = month_names[:3]
    q2_names = month_names[3:]

    q1_avg_sql = f"ROUND((`{q1_names[0]}` + `{q1_names[1]}` + `{q1_names[2]}`) / 3.0, 1)"
    q2_avg_sql = f"ROUND((`{q2_names[0]}` + `{q2_names[1]}` + `{q2_names[2]}`) / 3.0, 1)"
    
    q1_select = ",\n            ".join([f"CONCAT(IFNULL(agg.`{m}`, 0), '%%') AS `{m}`" for m in q1_names])
    q2_select = ",\n            ".join([f"CONCAT(IFNULL(agg.`{m}`, 0), '%%') AS `{m}`" for m in q2_names])

    return f"""
        SELECT 
            usr.full_name AS Supervisor, 
            cr.creche_name AS "Creche Name",
            {q1_select}, 
            IFNULL({q1_avg_sql}, 0) AS "Q1 Avg",
            {q2_select}, 
            IFNULL({q2_avg_sql}, 0) AS "Q2 Avg",
            {trend_label} AS Trend
        FROM `tabCreche` cr
        LEFT JOIN `tabUser` usr ON usr.name = cr.supervisor_id
        LEFT JOIN (
            SELECT creche_id, {month_cases_sql}
            FROM `tabChild Attendance`
            WHERE date_of_attendance BETWEEN %(trend_start_date)s AND %(trend_end_date)s
              AND is_shishu_ghar_is_closed_for_the_day = 0
            GROUP BY creche_id
        ) agg ON cr.name = agg.creche_id
        WHERE cr.creche_status_id = 3 {common_filters_cr}
        HAVING IFNULL({trend_condition.replace('Q1_Avg', q1_avg_sql).replace('Q2_Avg', q2_avg_sql)}, FALSE)
    """

def get_bucket_pivot_query(common_filters_cr, past_months, bucket_condition):
    m1_y, m1_m = past_months[3]
    m2_y, m2_m = past_months[4]
    m3_y, m3_m = past_months[5]

    m1_name = calendar.month_abbr[m1_m]
    m2_name = calendar.month_abbr[m2_m]
    m3_name = calendar.month_abbr[m3_m]

    return f"""
        SELECT 
            usr.full_name AS "SUPERVISOR", cr.creche_name AS "CRECHE",
            COALESCE(ec.total_enrolled, 0) AS "TOTAL ENROLED CHILDREN",
            COALESCE(mb.m1_below_25, 0) AS "{m1_name} Below 25 %%",
            COALESCE(mb.m1_25_50, 0) AS "{m1_name} 25 - 50 %%",
            COALESCE(mb.m1_50_75, 0) AS "{m1_name} 50 - 75 %%",
            COALESCE(mb.m1_75_100, 0) AS "{m1_name} 75 - 100 %%",
            COALESCE(mb.m2_below_25, 0) AS "{m2_name} Below 25 %%",
            COALESCE(mb.m2_25_50, 0) AS "{m2_name} 25 - 50 %%",
            COALESCE(mb.m2_50_75, 0) AS "{m2_name} 50 - 75 %%",
            COALESCE(mb.m2_75_100, 0) AS "{m2_name} 75 - 100 %%",
            COALESCE(mb.m3_below_25, 0) AS "{m3_name} Below 25 %%",
            COALESCE(mb.m3_25_50, 0) AS "{m3_name} 25 - 50 %%",
            COALESCE(mb.m3_50_75, 0) AS "{m3_name} 50 - 75 %%",
            COALESCE(mb.m3_75_100, 0) AS "{m3_name} 75 - 100 %%"
        FROM `tabCreche` cr
        LEFT JOIN `tabUser` usr ON usr.name = cr.supervisor_id
        LEFT JOIN (
            SELECT creche_id, COUNT(DISTINCT name) AS total_enrolled
            FROM `tabChild Enrollment and Exit`
            WHERE (date_of_exit BETWEEN %(q2_start_date)s AND %(q2_end_date)s) 
               OR (date_of_enrollment <= %(q2_end_date)s AND (date_of_exit IS NULL OR date_of_exit >= %(q2_end_date)s))
            GROUP BY creche_id
        ) ec ON ec.creche_id = cr.name
        LEFT JOIN (
            SELECT creche_id,
                COUNT(CASE WHEN month_num = {m1_m} AND pct < 25 THEN 1 END) AS m1_below_25,
                COUNT(CASE WHEN month_num = {m1_m} AND pct >= 25 AND pct < 50 THEN 1 END) AS m1_25_50,
                COUNT(CASE WHEN month_num = {m1_m} AND pct >= 50 AND pct < 75 THEN 1 END) AS m1_50_75,
                COUNT(CASE WHEN month_num = {m1_m} AND pct >= 75 THEN 1 END) AS m1_75_100,
                COUNT(CASE WHEN month_num = {m2_m} AND pct < 25 THEN 1 END) AS m2_below_25,
                COUNT(CASE WHEN month_num = {m2_m} AND pct >= 25 AND pct < 50 THEN 1 END) AS m2_25_50,
                COUNT(CASE WHEN month_num = {m2_m} AND pct >= 50 AND pct < 75 THEN 1 END) AS m2_50_75,
                COUNT(CASE WHEN month_num = {m2_m} AND pct >= 75 THEN 1 END) AS m2_75_100,
                COUNT(CASE WHEN month_num = {m3_m} AND pct < 25 THEN 1 END) AS m3_below_25,
                COUNT(CASE WHEN month_num = {m3_m} AND pct >= 25 AND pct < 50 THEN 1 END) AS m3_25_50,
                COUNT(CASE WHEN month_num = {m3_m} AND pct >= 50 AND pct < 75 THEN 1 END) AS m3_50_75,
                COUNT(CASE WHEN month_num = {m3_m} AND pct >= 75 THEN 1 END) AS m3_75_100
            FROM (
                SELECT ca.creche_id, MONTH(ca.date_of_attendance) AS month_num, cal.childenrolledguid,
                       (SUM(cal.attendance) * 100.0 / NULLIF(COUNT(ca.name), 0)) AS pct
                FROM `tabChild Attendance` ca
                JOIN `tabChild Attendance List` cal ON cal.parent = ca.name
                WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0 AND ca.date_of_attendance BETWEEN %(q2_start_date)s AND %(q2_end_date)s
                GROUP BY ca.creche_id, cal.childenrolledguid, MONTH(ca.date_of_attendance)
            ) child_att
            GROUP BY creche_id
        ) mb ON mb.creche_id = cr.name
        LEFT JOIN (
            SELECT ca.creche_id, COALESCE(ROUND((SUM(cal.attendance) * 100.0 / NULLIF(COUNT(ca.name), 0)), 2), 0) AS cma_pct
            FROM `tabChild Attendance` ca
            JOIN `tabChild Attendance List` cal ON cal.parent = ca.name
            WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0 AND MONTH(ca.date_of_attendance) = {m3_m} AND YEAR(ca.date_of_attendance) = {m3_y}
            GROUP BY ca.creche_id
        ) cma ON cma.creche_id = cr.name
        WHERE 1=1 {common_filters_cr}
        AND {bucket_condition.replace('cma.attendance_percentage', 'cma.cma_pct')}
        ORDER BY "SUPERVISOR", "CRECHE"
    """

def get_trend_pivot_query(common_filters_cr, past_months, trend_symbol):
    m1_y, m1_m = past_months[3]
    m2_y, m2_m = past_months[4]
    m3_y, m3_m = past_months[5]

    m1_name = calendar.month_abbr[m1_m]
    m2_name = calendar.month_abbr[m2_m]
    m3_name = calendar.month_abbr[m3_m]

    return f"""
        SELECT * FROM (
            SELECT 
                usr.full_name AS "Supervisor", cr.creche_name AS "Creche Name",
                MAX(CASE WHEN m.month_num = {m1_m} THEN m.attendance_percentage ELSE 0 END) AS "{m1_name} Attendance %%",
                MAX(CASE WHEN m.month_num = {m1_m} THEN m.avg_attendance_per_day ELSE 0 END) AS "{m1_name} Av.Attendance Per Day",
                MAX(CASE WHEN m.month_num = {m2_m} THEN m.attendance_percentage ELSE 0 END) AS "{m2_name} Attendance %%",
                MAX(CASE WHEN m.month_num = {m2_m} THEN m.avg_attendance_per_day ELSE 0 END) AS "{m2_name} Av.Attendance Per Day",
                MAX(CASE WHEN m.month_num = {m3_m} THEN m.attendance_percentage ELSE 0 END) AS "{m3_name} Attendance %%",
                MAX(CASE WHEN m.month_num = {m3_m} THEN m.avg_attendance_per_day ELSE 0 END) AS "{m3_name} Av.Attendance Per Day",
                CASE 
                    WHEN MAX(CASE WHEN m.month_num = {m3_m} THEN m.attendance_percentage ELSE 0 END) > MAX(CASE WHEN m.month_num = {m2_m} THEN m.attendance_percentage ELSE 0 END) THEN '↑'
                    WHEN MAX(CASE WHEN m.month_num = {m3_m} THEN m.attendance_percentage ELSE 0 END) < MAX(CASE WHEN m.month_num = {m2_m} THEN m.attendance_percentage ELSE 0 END) THEN '↓'
                    ELSE '-'
                END AS "Trend Attendance %%",
                CASE 
                    WHEN MAX(CASE WHEN m.month_num = {m3_m} THEN m.avg_attendance_per_day ELSE 0 END) > MAX(CASE WHEN m.month_num = {m2_m} THEN m.avg_attendance_per_day ELSE 0 END) THEN '↑'
                    WHEN MAX(CASE WHEN m.month_num = {m3_m} THEN m.avg_attendance_per_day ELSE 0 END) < MAX(CASE WHEN m.month_num = {m2_m} THEN m.avg_attendance_per_day ELSE 0 END) THEN '↓'
                    ELSE '-'
                END AS "Trend Av.Attendance Per Day"
            FROM `tabCreche` cr
            LEFT JOIN `tabUser` usr ON usr.name = cr.supervisor_id
            LEFT JOIN (
                SELECT 
                    a.creche_id, a.month_num,
                    COALESCE(ROUND((a.days_attended * 100.0 / NULLIF(a.eligible_open_days, 0)), 2), 0) AS attendance_percentage,
                    CASE WHEN c.no_days = 0 THEN 0 ELSE ROUND(a.days_attended / c.no_days, 1) END AS avg_attendance_per_day
                FROM (
                    SELECT ca.creche_id, MONTH(ca.date_of_attendance) AS month_num, SUM(cal.attendance) AS days_attended, COUNT(ca.name) AS eligible_open_days
                    FROM `tabChild Attendance` ca
                    JOIN `tabChild Attendance List` cal ON cal.parent = ca.name
                    WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0 AND ca.date_of_attendance BETWEEN %(q2_start_date)s AND %(q2_end_date)s
                    GROUP BY ca.creche_id, MONTH(ca.date_of_attendance)
                ) a
                LEFT JOIN (
                    SELECT creche_id, MONTH(date_of_attendance) AS month_num, COUNT(*) AS no_days
                    FROM `tabChild Attendance` 
                    WHERE is_shishu_ghar_is_closed_for_the_day = 0 AND date_of_attendance BETWEEN %(q2_start_date)s AND %(q2_end_date)s
                    GROUP BY creche_id, MONTH(date_of_attendance)
                ) c ON a.creche_id = c.creche_id AND a.month_num = c.month_num
            ) m ON m.creche_id = cr.name
            WHERE 1=1 {common_filters_cr}
            GROUP BY cr.name, usr.full_name, cr.creche_name
        ) AS FinalData
        WHERE `Trend Attendance %%` = '{trend_symbol}'
        ORDER BY "Supervisor", "Creche Name"
    """

def get_avg_daily_10_query(common_filters_cr, past_months):
    m1_y, m1_m = past_months[3]
    m2_y, m2_m = past_months[4]
    m3_y, m3_m = past_months[5]

    m1_name = calendar.month_abbr[m1_m]
    m2_name = calendar.month_abbr[m2_m]
    m3_name = calendar.month_abbr[m3_m]

    return f"""
        SELECT 
            `SUPERVISOR`, `CRECHE`, `ENROLED CHILDREN`, `ELLIGIBLE CHILDREN`, 
            `{m1_name} ATTENDANCE %% (Av. Attendance Per Day)`,
            `{m2_name} ATTENDANCE %% (Av. Attendance Per Day)`,
            `{m3_name} ATTENDANCE %% (Av. Attendance Per Day)`
        FROM (
            SELECT 
                usr.full_name AS `SUPERVISOR`, cr.creche_name AS `CRECHE`,
                COALESCE(enr.total_enrolled, 0) AS `ENROLED CHILDREN`,
                COALESCE(elig.eligible_count, 0) AS `ELLIGIBLE CHILDREN`,
                IFNULL(MAX(CASE WHEN m.month_num = {m1_m} THEN CONCAT(m.attendance_percentage, ' (', m.avg_attendance_per_day, ')') END), '') AS `{m1_name} ATTENDANCE %% (Av. Attendance Per Day)`,
                IFNULL(MAX(CASE WHEN m.month_num = {m2_m} THEN CONCAT(m.attendance_percentage, ' (', m.avg_attendance_per_day, ')') END), '') AS `{m2_name} ATTENDANCE %% (Av. Attendance Per Day)`,
                IFNULL(MAX(CASE WHEN m.month_num = {m3_m} THEN CONCAT(m.attendance_percentage, ' (', m.avg_attendance_per_day, ')') END), '') AS `{m3_name} ATTENDANCE %% (Av. Attendance Per Day)`,
                MAX(CASE WHEN m.month_num = {m3_m} THEN m.avg_attendance_per_day ELSE 0 END) AS m3_avg_att
            FROM `tabCreche` cr
            LEFT JOIN `tabUser` usr ON usr.name = cr.supervisor_id
            LEFT JOIN (
                SELECT hf.creche_id, COUNT(DISTINCT hhc.name) AS eligible_count
                FROM `tabHousehold Child Form` hhc
                JOIN `tabHousehold Form` hf ON hf.name = hhc.parent
                WHERE hhc.is_dob_available = 1 AND (hhc.child_status IS NULL OR TRIM(hhc.child_status) = '')
                AND hhc.child_dob BETWEEN 
                    DATE_SUB(IF(DATE_FORMAT(%(q2_end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), CURDATE(), %(q2_end_date)s), INTERVAL 36 MONTH)
                    AND DATE_SUB(IF(DATE_FORMAT(%(q2_end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), CURDATE(), %(q2_end_date)s), INTERVAL 6 MONTH)
                GROUP BY hf.creche_id
            ) elig ON elig.creche_id = cr.name
            LEFT JOIN (
                SELECT creche_id, COUNT(DISTINCT name) AS total_enrolled
                FROM `tabChild Enrollment and Exit`
                WHERE (date_of_exit BETWEEN %(q2_start_date)s AND %(q2_end_date)s) OR (date_of_enrollment <= %(q2_end_date)s AND (date_of_exit IS NULL OR date_of_exit >= %(q2_end_date)s))
                GROUP BY creche_id
            ) enr ON enr.creche_id = cr.name
            LEFT JOIN (
                SELECT 
                    a.creche_id, a.month_num,
                    COALESCE(ROUND((a.days_attended * 100.0 / NULLIF(a.eligible_open_days, 0)), 0), 0) AS attendance_percentage,
                    CASE WHEN c.no_days = 0 THEN 0 ELSE ROUND(a.days_attended / c.no_days, 1) END AS avg_attendance_per_day
                FROM (
                    SELECT ca.creche_id, MONTH(ca.date_of_attendance) AS month_num, SUM(cal.attendance) AS days_attended, COUNT(ca.name) AS eligible_open_days
                    FROM `tabChild Attendance` ca
                    JOIN `tabChild Attendance List` cal ON cal.parent = ca.name
                    WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0 AND ca.date_of_attendance BETWEEN %(q2_start_date)s AND %(q2_end_date)s
                    GROUP BY ca.creche_id, MONTH(ca.date_of_attendance)
                ) a
                LEFT JOIN (
                    SELECT creche_id, MONTH(date_of_attendance) AS month_num, COUNT(*) AS no_days
                    FROM `tabChild Attendance` 
                    WHERE is_shishu_ghar_is_closed_for_the_day = 0 AND date_of_attendance BETWEEN %(q2_start_date)s AND %(q2_end_date)s
                    GROUP BY creche_id, MONTH(date_of_attendance)
                ) c ON a.creche_id = c.creche_id AND a.month_num = c.month_num
            ) m ON m.creche_id = cr.name
            WHERE 1=1 {common_filters_cr}
            GROUP BY cr.name, usr.full_name, cr.creche_name, elig.eligible_count, enr.total_enrolled
        ) AS FinalConcat
        WHERE m3_avg_att < 10
        ORDER BY `SUPERVISOR`, `CRECHE`
    """

# =========================================================
# 3. API Endpoints
# =========================================================

@frappe.whitelist()
def get_avg_creche_opened(**kwargs):
    cache_key = get_cache_key("avg_creche_opened", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, _ = get_master_filters(kwargs)
    query = get_avg_creche_opened_query(common_filters_cr)
    result = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL)
    return result

@frappe.whitelist()
def get_avg_creche_closed(**kwargs):
    cache_key = get_cache_key("avg_creche_closed", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, _ = get_master_filters(kwargs)
    query = get_avg_creche_closed_query(common_filters_cr)
    result = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL)
    return result

@frappe.whitelist()
def get_creche_attendance_not_submitted(**kwargs):
    cache_key = get_cache_key("cnt_not_submitted", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, _ = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_code1_not_submitted_query(common_filters_cr)}) AS matched_count_subq"
    result = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL)
    return result

@frappe.whitelist()
def get_creche_24(**kwargs):
    cache_key = get_cache_key("cnt_creche_24", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, _ = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_code1_creche_24_query(common_filters_cr)}) AS matched_count_subq"
    result = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL)
    return result

@frappe.whitelist()
def get_attendance_deteriorating(**kwargs):
    cache_key = get_cache_key("cnt_trend_q_det", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    data_query = get_code1_trend_query(past_months, "Q2_Avg < Q1_Avg", "'Deteriorating'", common_filters_cr)
    query = f"SELECT COUNT(*) AS count FROM ({data_query}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_improving(**kwargs):
    cache_key = get_cache_key("cnt_trend_q_imp", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    data_query = get_code1_trend_query(past_months, "Q2_Avg > Q1_Avg", "'Improving'", common_filters_cr)
    query = f"SELECT COUNT(*) AS count FROM ({data_query}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_no_change(**kwargs):
    cache_key = get_cache_key("cnt_trend_q_no", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    data_query = get_code1_trend_query(past_months, "Q2_Avg = Q1_Avg", "'No change'", common_filters_cr)
    query = f"SELECT COUNT(*) AS count FROM ({data_query}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_avg_daily_attendance_10(**kwargs):
    cache_key = get_cache_key("cnt_avg_daily_10", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_avg_daily_10_query(common_filters_cr, past_months)}) AS matched_count_subq"
    result = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, result, expires_in_sec=CACHE_TTL)
    return result

@frappe.whitelist()
def get_attendance_below_25(**kwargs):
    cache_key = get_cache_key("cnt_att_below_25", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_bucket_pivot_query(common_filters_cr, past_months, 'cma_pct < 25')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_50(**kwargs):
    cache_key = get_cache_key("cnt_att_below_50", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_bucket_pivot_query(common_filters_cr, past_months, 'cma_pct >= 25 AND cma_pct < 50')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_75(**kwargs):
    cache_key = get_cache_key("cnt_att_below_75", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_bucket_pivot_query(common_filters_cr, past_months, 'cma_pct >= 50 AND cma_pct < 75')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_100(**kwargs):
    cache_key = get_cache_key("cnt_att_below_100", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_bucket_pivot_query(common_filters_cr, past_months, 'cma_pct >= 75')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_trend_deteriorating(**kwargs):
    cache_key = get_cache_key("cnt_trend_m_det", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_trend_pivot_query(common_filters_cr, past_months, '↓')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_trend_improving(**kwargs):
    cache_key = get_cache_key("cnt_trend_m_imp", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_trend_pivot_query(common_filters_cr, past_months, '↑')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_trend_no_change(**kwargs):
    cache_key = get_cache_key("cnt_trend_m_no", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"SELECT COUNT(*) AS count FROM ({get_trend_pivot_query(common_filters_cr, past_months, '-')}) AS matched_count_subq"
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_creche_attendance_not_submitted_data(**kwargs):
    cache_key = get_cache_key("data_not_submitted", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, _ = get_master_filters(kwargs)
    res = frappe.db.sql(get_code1_not_submitted_query(common_filters_cr), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_creche_24_data(**kwargs):
    cache_key = get_cache_key("data_creche_24", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, _ = get_master_filters(kwargs)
    res = frappe.db.sql(get_code1_creche_24_query(common_filters_cr), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_deteriorating_data(**kwargs):
    cache_key = get_cache_key("data_trend_q_det", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_code1_trend_query(past_months, "Q2_Avg < Q1_Avg", "'Deteriorating'", common_filters_cr)
    res = frappe.db.sql(query, params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_improving_data(**kwargs):
    cache_key = get_cache_key("data_trend_q_imp", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_code1_trend_query(past_months, "Q2_Avg > Q1_Avg", "'Improving'", common_filters_cr)
    res = frappe.db.sql(query, params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_no_change_data(**kwargs):
    cache_key = get_cache_key("data_trend_q_no", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_code1_trend_query(past_months, "Q2_Avg = Q1_Avg", "'No change'", common_filters_cr)
    res = frappe.db.sql(query, params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_avg_daily_attendance_10_data(**kwargs):
    cache_key = get_cache_key("data_avg_daily_10", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_avg_daily_10_query(common_filters_cr, past_months), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_25_data(**kwargs):
    cache_key = get_cache_key("data_att_below_25", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_bucket_pivot_query(common_filters_cr, past_months, "cma.cma_pct < 25"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_50_data(**kwargs):
    cache_key = get_cache_key("data_att_below_50", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_bucket_pivot_query(common_filters_cr, past_months, "cma.cma_pct >= 25 AND cma.cma_pct < 50"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_75_data(**kwargs):
    cache_key = get_cache_key("data_att_below_75", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_bucket_pivot_query(common_filters_cr, past_months, "cma.cma_pct >= 50 AND cma.cma_pct < 75"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_below_100_data(**kwargs):
    cache_key = get_cache_key("data_att_below_100", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_bucket_pivot_query(common_filters_cr, past_months, "cma.cma_pct >= 75"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_trend_deteriorating_data(**kwargs):
    cache_key = get_cache_key("data_trend_m_det", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_trend_pivot_query(common_filters_cr, past_months, "↓"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_trend_improving_data(**kwargs):
    cache_key = get_cache_key("data_trend_m_imp", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_trend_pivot_query(common_filters_cr, past_months, "↑"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_attendance_trend_no_change_data(**kwargs):
    cache_key = get_cache_key("data_trend_m_no", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    res = frappe.db.sql(get_trend_pivot_query(common_filters_cr, past_months, "-"), params, as_dict=True)
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

# =========================================================
# SAFETY APIs
# =========================================================

SAFETY_FIELDS = [
    'is_the_structural_safety_of_the_creches_roof_and_walls_ensured',
    'is_the_creche_protected_from_rainwater_leakage',
    'is_any_welltube_well_within_20_m_radius_of_the_creche',
    'properly_covered_with_iron_net_inside_out_side',
    'are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche',
    'external_fencing_around',
    'safety_the_main_entrance',
    'safety_gate_kitchen_entrance',
    'creche_secured_against_animals',
    'parents_recorded_visitor_register',
    'positioned_above_cylinder_height',
    'fire_extinguisher_available_working_condition',
    'kitchen_fire_related_emergencies',
    'confident_handling_pressure_cooker',
    'electrical_connections_positioned_out_children_reach',
    'fans_and_lights_installed_safe_location_height',
    'solar_batteries_kept_out_children_reach',
    'lightening_installed_creche',
    'food_utilized_first_out_manner',
    'egg_floating_tests_doneperiodically_check_quality_eggs',
    'is_leftover_food_disposed_of_properly_every_day',
    'water_filter_being_safe_drinking_water',
    'creche_running_two_caregivers',
    'first_aid_available_creche',
    'emergency_contact_numbers_clearly_displayed',
]

def get_safety_base_cte(start_date_param, end_date_param):
    selects = ", ".join([f"si.{f}" for f in SAFETY_FIELDS])
    return f"""
    WITH LastVisitCurr AS (
        SELECT si.creche_id, si.date_of_visit, {selects},
               ROW_NUMBER() OVER(PARTITION BY si.creche_id ORDER BY si.date_of_visit DESC) as rn
        FROM `tabSafety Indicators` si
        WHERE si.date_of_visit BETWEEN %({start_date_param})s AND %({end_date_param})s
    ),
    LastVisitPrev AS (
        SELECT si.creche_id, si.date_of_visit, {selects},
               ROW_NUMBER() OVER(PARTITION BY si.creche_id ORDER BY si.date_of_visit DESC) as rn
        FROM `tabSafety Indicators` si
        WHERE si.date_of_visit < %({start_date_param})s
    )
    """

def get_safety_base_query(common_filters_cr, select_clause, having_clause="", start_date_param="start_date", end_date_param="end_date"):
    cte = get_safety_base_cte(start_date_param, end_date_param)
    return f"""
        {cte}
        SELECT {select_clause}
        FROM `tabCreche` cr
        INNER JOIN LastVisitCurr curr ON cr.name = curr.creche_id AND curr.rn = 1
        LEFT JOIN LastVisitPrev prev ON cr.name = prev.creche_id AND prev.rn = 1
        LEFT JOIN `tabPartner` p ON cr.partner_id = p.name
        LEFT JOIN `tabState` s ON cr.state_id = s.name
        LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
        LEFT JOIN `tabBlock` b ON cr.block_id = b.name
        LEFT JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
        LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
        WHERE 1=1 {common_filters_cr}
        {having_clause}
    """

def get_safety_sum_query(common_filters_cr, condition_template, start_date_param="start_date", end_date_param="end_date"):
    select_parts = []
    for f in SAFETY_FIELDS:
        condition = condition_template.format(field=f)
        select_parts.append(f"CASE WHEN {condition} THEN 1 ELSE 0 END")
    sum_expr = " + ".join(select_parts)
    
    cte = get_safety_base_cte(start_date_param, end_date_param)
    return f"""
        {cte}
        SELECT IFNULL(SUM({sum_expr}), 0) as count
        FROM `tabCreche` cr
        INNER JOIN LastVisitCurr curr ON cr.name = curr.creche_id AND curr.rn = 1
        LEFT JOIN LastVisitPrev prev ON cr.name = prev.creche_id AND prev.rn = 1
        LEFT JOIN `tabPartner` p ON cr.partner_id = p.name
        LEFT JOIN `tabState` s ON cr.state_id = s.name
        LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
        LEFT JOIN `tabBlock` b ON cr.block_id = b.name
        LEFT JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
        LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
        WHERE 1=1 {common_filters_cr}
    """

def get_safety_category_query(common_filters_cr, fields_list, start_date_param="start_date", end_date_param="end_date"):
    condition_parts = [f"curr.{f} = 2" for f in fields_list]
    where_clause = " OR ".join(condition_parts)
    return get_safety_base_query(common_filters_cr, "COUNT(DISTINCT curr.creche_id) as count", f"AND ({where_clause})", start_date_param, end_date_param)

@frappe.whitelist()
def get_safety_submitted(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_submitted_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_base_query(common_filters_cr, 'COUNT(DISTINCT curr.creche_id) as count', '')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_not_submitted(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_not_submitted_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = f"""
        SELECT COUNT(DISTINCT cr.name) as count 
        FROM `tabCreche` cr 
        LEFT JOIN `tabSafety Indicators` si ON cr.name = si.creche_id AND si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
        LEFT JOIN `tabPartner` p ON cr.partner_id = p.name
        LEFT JOIN `tabState` s ON cr.state_id = s.name
        LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
        LEFT JOIN `tabBlock` b ON cr.block_id = b.name
        LEFT JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
        LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
        WHERE si.name IS NULL {common_filters_cr}
    """
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_identified_month(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_identified_month_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'curr.{field} = 2')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_resolved_month(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_resolved_month_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'prev.{field} = 2 AND curr.{field} = 1')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_unresolved_month(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_unresolved_month_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'prev.{field} = 2 AND curr.{field} = 2')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_identified_quarter(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_identified_quarter_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'curr.{field} = 2', 'q2_start_date', 'q2_end_date')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_resolved_quarter(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_resolved_quarter_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'prev.{field} = 2 AND curr.{field} = 1', 'q2_start_date', 'q2_end_date')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_unresolved_quarter(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_unresolved_quarter_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'prev.{field} = 2 AND curr.{field} = 2', 'q2_start_date', 'q2_end_date')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_unresolved_3_months(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_unresolved_3_months_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'curr.{field} = 2 AND prev.{field} = 2', 'q2_start_date', 'q2_end_date')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_unresolved_6_months(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_unresolved_6_months_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    query = get_safety_sum_query(common_filters_cr, 'curr.{field} = 2 AND prev.{field} = 2', 'trend_start_date', 'trend_end_date')
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_infra(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_infra_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    cat_fields = ['is_the_structural_safety_of_the_creches_roof_and_walls_ensured', 'is_the_creche_protected_from_rainwater_leakage', 'is_any_welltube_well_within_20_m_radius_of_the_creche', 'properly_covered_with_iron_net_inside_out_side', 'are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche']
    query = get_safety_category_query(common_filters_cr, cat_fields)
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_physical(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_physical_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    cat_fields = ['external_fencing_around', 'safety_the_main_entrance', 'safety_gate_kitchen_entrance', 'creche_secured_against_animals', 'parents_recorded_visitor_register']
    query = get_safety_category_query(common_filters_cr, cat_fields)
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_fire(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_fire_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    cat_fields = ['positioned_above_cylinder_height', 'fire_extinguisher_available_working_condition', 'kitchen_fire_related_emergencies', 'confident_handling_pressure_cooker']
    query = get_safety_category_query(common_filters_cr, cat_fields)
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_electrical(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_electrical_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    cat_fields = ['electrical_connections_positioned_out_children_reach', 'fans_and_lights_installed_safe_location_height', 'solar_batteries_kept_out_children_reach', 'lightening_installed_creche']
    query = get_safety_category_query(common_filters_cr, cat_fields)
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_food(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_food_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    cat_fields = ['food_utilized_first_out_manner', 'egg_floating_tests_doneperiodically_check_quality_eggs', 'is_leftover_food_disposed_of_properly_every_day', 'water_filter_being_safe_drinking_water']
    query = get_safety_category_query(common_filters_cr, cat_fields)
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res

@frappe.whitelist()
def get_safety_issues_other(**kwargs):
    cache_key = get_cache_key("v2_" + "get_safety_issues_other_data", kwargs)
    cached = frappe.cache().get_value(cache_key)
    if cached is not None: return cached
    params, common_filters_cr, past_months = get_master_filters(kwargs)
    cat_fields = ['creche_running_two_caregivers', 'first_aid_available_creche', 'emergency_contact_numbers_clearly_displayed']
    query = get_safety_category_query(common_filters_cr, cat_fields)
    res = return_count(frappe.db.sql(query, params, as_dict=True))
    frappe.cache().set_value(cache_key, res, expires_in_sec=CACHE_TTL)
    return res
