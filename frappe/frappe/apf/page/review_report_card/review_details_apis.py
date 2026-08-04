from datetime import date
import frappe
import calendar

@frappe.whitelist()
def fetch_card_data(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None, query_type="get_creche_attendance_not_submitted_data"):
    selected_year = int(year) if year and str(year).isdigit() else date.today().year
    selected_month = int(month) if month and str(month).isdigit() else date.today().month
    
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

    # ==========================================================
    # 2. GEOGRAPHY & PERMISSION FILTERS
    # ==========================================================
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner
    
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

    if phases:
        try:
            phases_list = [p.strip() for p in phases.split(",") if p.strip().isdigit()]
            phases_str = ",".join(phases_list) if phases_list else None
        except Exception:
            phases_str = None
    else:
        phases_str = None

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    params = {
        "end_date": end_date, "start_date": start_date,
        "trend_start_date": trend_start_date, "trend_end_date": trend_end_date,
        "partner_id": partner_id, "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id, "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id, "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id, "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id, "supervisor_id": supervisor_id,
        "cstart_date": cstart_date, "cend_date": cend_date,
        "c_status": c_status, "phases": phases_str
    }

    common_filters = """
        AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cr.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cr.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cr.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cr.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cr.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cr.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
    """

    final_query = None
    query_type_str = str(query_type)

    if query_type_str == "get_creche_attendance_not_submitted_data":
        final_query = f"""
            SELECT 
                cr.creche_id AS "Creche ID", cr.creche_name AS "Creche Name",
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
            WHERE 1=1 {common_filters}
            AND cr.creche_opening_date IS NOT NULL 
            AND cr.creche_opening_date <= %(end_date)s
            AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            AND (DATEDIFF(
                CASE WHEN %(end_date)s > CURRENT_DATE() THEN CURRENT_DATE() ELSE %(end_date)s END, 
                CASE WHEN cr.creche_opening_date < %(start_date)s THEN %(start_date)s ELSE cr.creche_opening_date END
            ) + 1) > IFNULL(att.attdays, 0)
            ORDER BY 
                TRIM(CONVERT(p.partner_name USING utf8mb4)),
                TRIM(CONVERT(s.state_name USING utf8mb4)),
                TRIM(CONVERT(d.district_name USING utf8mb4)),
                TRIM(CONVERT(b.block_name USING utf8mb4)),
                TRIM(CONVERT(g.gp_name USING utf8mb4)),
                TRIM(CONVERT(cr.creche_name USING utf8mb4))
        """

    elif query_type_str == "get_creche_24_data":
        final_query = f"""
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
            WHERE 1=1 {common_filters}
            LIMIT 100;
        """

    elif query_type_str in ["get_attendance_deteriorating_data", "get_attendance_improving_data", "get_attendance_no_change_data"]:
        month_cases = []
        month_names = []
        for y, m in past_months:
            m_name = calendar.month_abbr[m]
            month_names.append(m_name)
            case_statement = f"COUNT(DISTINCT CASE WHEN YEAR(date_of_attendance) = {y} AND MONTH(date_of_attendance) = {m} THEN date_of_attendance END) AS `{m_name}`"
            month_cases.append(case_statement)
        
        month_cases_sql = ",\n                ".join(month_cases)
        q1_names, q2_names = month_names[:3], month_names[3:]
        q1_avg_sql = f"ROUND((`{q1_names[0]}` + `{q1_names[1]}` + `{q1_names[2]}`) / 3.0, 1)"
        q2_avg_sql = f"ROUND((`{q2_names[0]}` + `{q2_names[1]}` + `{q2_names[2]}`) / 3.0, 1)"
        q1_select = ",\n            ".join([f"CONCAT(IFNULL(agg.`{m}`, 0), '%%') AS `{m}`" for m in q1_names])
        q2_select = ",\n            ".join([f"CONCAT(IFNULL(agg.`{m}`, 0), '%%') AS `{m}`" for m in q2_names])

        trend_base_query = f"""
            SELECT 
                usr.full_name AS Supervisor, cr.creche_name AS "Creche Name",
                {q1_select}, IFNULL({q1_avg_sql}, 0) AS "Q1 Avg",
                {q2_select}, IFNULL({q2_avg_sql}, 0) AS "Q2 Avg",
                {{trend_label}} AS Trend
            FROM `tabCreche` cr
            LEFT JOIN `tabUser` usr ON usr.name = cr.supervisor_id
            LEFT JOIN (
                SELECT creche_id, {month_cases_sql}
                FROM `tabChild Attendance`
                WHERE date_of_attendance BETWEEN %(trend_start_date)s AND %(trend_end_date)s
                  AND is_shishu_ghar_is_closed_for_the_day = 0
                GROUP BY creche_id
            ) agg ON cr.name = agg.creche_id
            WHERE cr.creche_status_id = 3 {common_filters}
            HAVING IFNULL({{trend_condition}}, FALSE)
            ORDER BY Supervisor, "Creche Name"
        """
        
        if query_type_str == "get_attendance_deteriorating_data":
            final_query = trend_base_query.format(trend_label="'Deteriorating'", trend_condition=f"{q2_avg_sql} < {q1_avg_sql}")
        elif query_type_str == "get_attendance_improving_data":
            final_query = trend_base_query.format(trend_label="'Improving'", trend_condition=f"{q2_avg_sql} > {q1_avg_sql}")
        elif query_type_str == "get_attendance_no_change_data":
            final_query = trend_base_query.format(trend_label="'No change'", trend_condition=f"{q2_avg_sql} = {q1_avg_sql}")

    elif query_type_str in [
        "get_attendance_trend_deteriorating_data", "get_attendance_trend_improving_data", "get_attendance_trend_no_change_data",
        "get_attendance_below_25_data", "get_attendance_below_50_data", "get_attendance_below_75_data", "get_attendance_below_100_data",
        "get_avg_daily_attendance_10_data"
    ]:
        m1_y, m1_m = past_months[3]
        m2_y, m2_m = past_months[4]
        m3_y, m3_m = past_months[5]

        m1_name = calendar.month_abbr[m1_m]
        m2_name = calendar.month_abbr[m2_m]
        m3_name = calendar.month_abbr[m3_m]

        params["q2_start_date"] = date(m1_y, m1_m, 1)
        params["q2_end_date"] = end_date

        if query_type_str in ["get_attendance_trend_deteriorating_data", "get_attendance_trend_improving_data", "get_attendance_trend_no_change_data"]:
            trend_pivot_base = f"""
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
                    WHERE 1=1 {common_filters}
                    GROUP BY cr.name, usr.full_name, cr.creche_name
                ) AS FinalData
                WHERE `Trend Attendance %%` = '{{trend_symbol}}'
                ORDER BY "Supervisor", "Creche Name"
            """
            if query_type_str == "get_attendance_trend_deteriorating_data":
                final_query = trend_pivot_base.replace("{trend_symbol}", "↓")
            elif query_type_str == "get_attendance_trend_improving_data":
                final_query = trend_pivot_base.replace("{trend_symbol}", "↑")
            elif query_type_str == "get_attendance_trend_no_change_data":
                final_query = trend_pivot_base.replace("{trend_symbol}", "-")

        elif query_type_str in ["get_attendance_below_25_data", "get_attendance_below_50_data", "get_attendance_below_75_data", "get_attendance_below_100_data"]:
            bucket_pivot_base = f"""
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
                WHERE 1=1 {common_filters}
                AND {{bucket_condition}}
                ORDER BY "SUPERVISOR", "CRECHE"
            """
            if query_type_str == "get_attendance_below_25_data":
                final_query = bucket_pivot_base.replace("{bucket_condition}", "cma.cma_pct < 25")
            elif query_type_str == "get_attendance_below_50_data":
                final_query = bucket_pivot_base.replace("{bucket_condition}", "cma.cma_pct >= 25 AND cma.cma_pct < 50")
            elif query_type_str == "get_attendance_below_75_data":
                final_query = bucket_pivot_base.replace("{bucket_condition}", "cma.cma_pct >= 50 AND cma.cma_pct < 75")
            elif query_type_str == "get_attendance_below_100_data":
                final_query = bucket_pivot_base.replace("{bucket_condition}", "cma.cma_pct >= 75")

        elif query_type_str == "get_avg_daily_attendance_10_data":
            final_query = f"""
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
                    WHERE 1=1 {common_filters}
                    GROUP BY cr.name, usr.full_name, cr.creche_name, elig.eligible_count, enr.total_enrolled
                ) AS FinalConcat
                WHERE m3_avg_att < 10
                ORDER BY `SUPERVISOR`, `CRECHE`;
            """

    SAFETY_FIELDS = [
        'is_the_structural_safety_of_the_creches_roof_and_walls_ensured', 'is_the_creche_protected_from_rainwater_leakage',
        'is_any_welltube_well_within_20_m_radius_of_the_creche', 'properly_covered_with_iron_net_inside_out_side',
        'are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche', 'external_fencing_around',
        'safety_the_main_entrance', 'safety_gate_kitchen_entrance', 'creche_secured_against_animals',
        'parents_recorded_visitor_register', 'positioned_above_cylinder_height', 'fire_extinguisher_available_working_condition',
        'kitchen_fire_related_emergencies', 'confident_handling_pressure_cooker', 'electrical_connections_positioned_out_children_reach',
        'fans_and_lights_installed_safe_location_height', 'solar_batteries_kept_out_children_reach', 'lightening_installed_creche',
        'food_utilized_first_out_manner', 'egg_floating_tests_doneperiodically_check_quality_eggs', 'is_leftover_food_disposed_of_properly_every_day',
        'water_filter_being_safe_drinking_water', 'creche_running_two_caregivers', 'first_aid_available_creche',
        'emergency_contact_numbers_clearly_displayed'
    ]

    def get_safety_base_cte(start_p, end_p):
        selects = ", ".join([f"si.{f}" for f in SAFETY_FIELDS])
        return f"""
        WITH LastVisitCurr AS (
            SELECT si.creche_id, si.date_of_visit, {selects},
                   ROW_NUMBER() OVER(PARTITION BY si.creche_id ORDER BY si.date_of_visit DESC) as rn
            FROM `tabSafety Indicators` si
            WHERE si.date_of_visit BETWEEN %({start_p})s AND %({end_p})s
        ), LastVisitPrev AS (
            SELECT si.creche_id, si.date_of_visit, {selects},
                   ROW_NUMBER() OVER(PARTITION BY si.creche_id ORDER BY si.date_of_visit DESC) as rn
            FROM `tabSafety Indicators` si
            WHERE si.date_of_visit < %({start_p})s
        )
        """

    def get_safety_detail_query(condition_template, start_p="start_date", end_p="end_date"):
        cte = get_safety_base_cte(start_p, end_p)
        sum_expr = " + ".join([f"CASE WHEN {condition_template.format(field=f)} THEN 1 ELSE 0 END" for f in SAFETY_FIELDS])
        concat_expr = "CONCAT_WS(', ', " + ", ".join([f"CASE WHEN {condition_template.format(field=f)} THEN '{f}' ELSE NULL END" for f in SAFETY_FIELDS]) + ")"
        return f"""
            {cte}
            SELECT s.state_name AS "State", d.district_name AS "District", b.block_name AS "Block",
                   usr.full_name AS "Supervisor", cr.creche_name AS "Creche",
                   ({sum_expr}) AS "Safety Issues",
                   ({concat_expr}) AS "_safety_issues_list"
            FROM `tabCreche` cr
            INNER JOIN LastVisitCurr curr ON cr.name = curr.creche_id AND curr.rn = 1
            LEFT JOIN LastVisitPrev prev ON cr.name = prev.creche_id AND prev.rn = 1
            LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
            LEFT JOIN `tabState` s ON cr.state_id = s.name
            LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
            LEFT JOIN `tabBlock` b ON cr.block_id = b.name
            WHERE 1=1 {common_filters}
            HAVING `Safety Issues` > 0
            ORDER BY "Safety Issues" DESC, "Creche" ASC
        """

    def get_safety_cat_detail_query(cat_fields, start_p="start_date", end_p="end_date"):
        cte = get_safety_base_cte(start_p, end_p)
        where_clause = " OR ".join([f"curr.{f} = 2" for f in cat_fields])
        sum_expr = " + ".join([f"CASE WHEN curr.{f} = 2 THEN 1 ELSE 0 END" for f in cat_fields])
        concat_expr = "CONCAT_WS(', ', " + ", ".join([f"CASE WHEN curr.{f} = 2 THEN '{f}' ELSE NULL END" for f in cat_fields]) + ")"
        return f"""
            {cte}
            SELECT s.state_name AS "State", d.district_name AS "District", b.block_name AS "Block",
                   usr.full_name AS "Supervisor", cr.creche_name AS "Creche",
                   ({sum_expr}) AS "Safety Issues",
                   ({concat_expr}) AS "_safety_issues_list"
            FROM `tabCreche` cr
            INNER JOIN LastVisitCurr curr ON cr.name = curr.creche_id AND curr.rn = 1
            LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
            LEFT JOIN `tabState` s ON cr.state_id = s.name
            LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
            LEFT JOIN `tabBlock` b ON cr.block_id = b.name
            WHERE 1=1 {common_filters} AND ({where_clause})
            ORDER BY "Safety Issues" DESC, "Creche" ASC
        """

    if query_type_str == "get_safety_submitted_data":
        cte = get_safety_base_cte("start_date", "end_date")
        final_query = f"""
            {cte}
            SELECT s.state_name AS "State", d.district_name AS "District", b.block_name AS "Block",
                   usr.full_name AS "Supervisor", cr.creche_name AS "Creche"
            FROM `tabCreche` cr
            INNER JOIN LastVisitCurr curr ON cr.name = curr.creche_id AND curr.rn = 1
            LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
            LEFT JOIN `tabState` s ON cr.state_id = s.name
            LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
            LEFT JOIN `tabBlock` b ON cr.block_id = b.name
            WHERE 1=1 {common_filters}
        """
    elif query_type_str == "get_safety_not_submitted_data":
        final_query = f"""
            SELECT s.state_name AS "State", d.district_name AS "District", b.block_name AS "Block",
                   usr.full_name AS "Supervisor", cr.creche_name AS "Creche"
            FROM `tabCreche` cr 
            LEFT JOIN `tabSafety Indicators` si ON cr.name = si.creche_id AND si.date_of_visit BETWEEN %(start_date)s AND %(end_date)s
            LEFT JOIN `tabUser` usr ON cr.supervisor_id = usr.name
            LEFT JOIN `tabState` s ON cr.state_id = s.name
            LEFT JOIN `tabDistrict` d ON cr.district_id = d.name
            LEFT JOIN `tabBlock` b ON cr.block_id = b.name
            WHERE si.name IS NULL {common_filters}
        """
    elif query_type_str == "get_safety_issues_identified_month_data":
        final_query = get_safety_detail_query("curr.{field} = 2")
    elif query_type_str == "get_safety_issues_resolved_month_data":
        final_query = get_safety_detail_query("prev.{field} = 2 AND curr.{field} = 1")
    elif query_type_str == "get_safety_issues_unresolved_month_data":
        final_query = get_safety_detail_query("prev.{field} = 2 AND curr.{field} = 2")
    elif query_type_str == "get_safety_issues_identified_quarter_data":
        params["q2_start_date"] = start_date # Assuming previous queries did not set q2_start_date, but wait! The previous APIs use trend_start_date or q2_start_date.
        # Let's map them to trend_start_date since that's defined in review_details_apis.py (line 31) as the last 6 months start. Wait, the quarter APIs in review_apis.py used q2_start_date.
        # In review_details_apis.py, past_months has 6 months. past_months[0] is month - 5, past_months[5] is month.
        # Quarter is last 3 months, so past_months[3] to past_months[5].
        q2_start = f"{past_months[3][0]}-{past_months[3][1]:02d}-01"
        params["q2_start_date"] = q2_start
        params["q2_end_date"] = end_date
        final_query = get_safety_detail_query("curr.{field} = 2", "q2_start_date", "q2_end_date")
    elif query_type_str == "get_safety_issues_resolved_quarter_data":
        q2_start = f"{past_months[3][0]}-{past_months[3][1]:02d}-01"
        params["q2_start_date"] = q2_start
        params["q2_end_date"] = end_date
        final_query = get_safety_detail_query("prev.{field} = 2 AND curr.{field} = 1", "q2_start_date", "q2_end_date")
    elif query_type_str == "get_safety_issues_unresolved_quarter_data":
        q2_start = f"{past_months[3][0]}-{past_months[3][1]:02d}-01"
        params["q2_start_date"] = q2_start
        params["q2_end_date"] = end_date
        final_query = get_safety_detail_query("prev.{field} = 2 AND curr.{field} = 2", "q2_start_date", "q2_end_date")
    elif query_type_str == "get_safety_issues_unresolved_3_months_data":
        q2_start = f"{past_months[3][0]}-{past_months[3][1]:02d}-01"
        params["q2_start_date"] = q2_start
        params["q2_end_date"] = end_date
        final_query = get_safety_detail_query("prev.{field} = 2 AND curr.{field} = 2", "q2_start_date", "q2_end_date")
    elif query_type_str == "get_safety_issues_unresolved_6_months_data":
        final_query = get_safety_detail_query("prev.{field} = 2 AND curr.{field} = 2", "trend_start_date", "trend_end_date")
    elif query_type_str == "get_safety_issues_infra_data":
        final_query = get_safety_cat_detail_query(['is_the_structural_safety_of_the_creches_roof_and_walls_ensured', 'is_the_creche_protected_from_rainwater_leakage', 'is_any_welltube_well_within_20_m_radius_of_the_creche', 'properly_covered_with_iron_net_inside_out_side', 'are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche'])
    elif query_type_str == "get_safety_issues_physical_data":
        final_query = get_safety_cat_detail_query(['external_fencing_around', 'safety_the_main_entrance', 'safety_gate_kitchen_entrance', 'creche_secured_against_animals', 'parents_recorded_visitor_register'])
    elif query_type_str == "get_safety_issues_fire_data":
        final_query = get_safety_cat_detail_query(['positioned_above_cylinder_height', 'fire_extinguisher_available_working_condition', 'kitchen_fire_related_emergencies', 'confident_handling_pressure_cooker'])
    elif query_type_str == "get_safety_issues_electrical_data":
        final_query = get_safety_cat_detail_query(['electrical_connections_positioned_out_children_reach', 'fans_and_lights_installed_safe_location_height', 'solar_batteries_kept_out_children_reach', 'lightening_installed_creche'])
    elif query_type_str == "get_safety_issues_food_data":
        final_query = get_safety_cat_detail_query(['food_utilized_first_out_manner', 'egg_floating_tests_doneperiodically_check_quality_eggs', 'is_leftover_food_disposed_of_properly_every_day', 'water_filter_being_safe_drinking_water'])
    elif query_type_str == "get_safety_issues_other_data":
        final_query = get_safety_cat_detail_query(['creche_running_two_caregivers', 'first_aid_available_creche', 'emergency_contact_numbers_clearly_displayed'])

    if not final_query:
        frappe.response["Error"] = "Invalid query_type parameter"
        return

    result = frappe.db.sql(final_query, params, as_dict=True)
    frappe.response["data"] = result or []




