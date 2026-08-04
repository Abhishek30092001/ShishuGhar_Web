from datetime import date
import frappe
import calendar
def format_query(query, params):
    for k, v in params.items():
        if v is None:
            v = "NULL"
        elif isinstance(v, str):
            v = f"'{v}'"
        elif hasattr(v, 'strftime'):
            v = f"'{v.strftime('%%Y-%%m-%%d')}'"
        query = query.replace(f"%({k})s", str(v))
    return query

@frappe.whitelist()
def fetch_card_data(partner_id=None, state_id=None, district_id=None, gp_id=None, block_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None, query_type="active_children", attendance_trend=0):
    year = int(year) if year and year.isdigit() else date.today().year
    month = int(month) if month and month.isdigit() else date.today().month

    try:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    except:
        today = date.today()
        year = today.year
        month = today.month
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

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
            phases = [p.strip() for p in phases.split(",") if p.strip().isdigit()]
            phases_str = ",".join(phases) if phases else None
        except:
            phases = None
            phases_str = None
    else:
        phases_str = None

    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    # ===== GF1/GF1+ Parameters (Previous Month) =====
    if month == 1:
        prev_priority_month = 12
        prev_priority_year = year - 1
    else:
        prev_priority_month = month - 1
        prev_priority_year = year
    
    # Fallback (2 months ago)
    if month == 1:
        prev_fallback_month = 11
        prev_fallback_year = year - 1
    elif month == 2:
        prev_fallback_month = 12
        prev_fallback_year = year - 1
    else:
        prev_fallback_month = month - 2
        prev_fallback_year = year

    # ===== GF2 Parameters (2 months ago priority, 3 months ago fallback) =====
    # Priority: 2 months ago
    if month <= 2:
        gf2_priority_year = year - 1
        gf2_priority_month = month + 10   # month 1 → 11, month 2 → 12
    else:
        gf2_priority_year = year
        gf2_priority_month = month - 2

    # Fallback: 3 months ago
    if month <= 3:
        gf2_fallback_year = year - 1
        gf2_fallback_month = month + 9    # month 1 → 10, month 2 → 11, month 3 → 12
    else:
        gf2_fallback_year = year
        gf2_fallback_month = month - 3

    # ===== Zig-Zag Parameters (T-1 to T-4) =====
    def rollback_month(y, m, step):
        m = m - step
        while m <= 0:
            m += 12
            y -= 1
        return m, y

    m1_month, m1_year = rollback_month(year, month, 1)
    m2_month, m2_year = rollback_month(year, month, 2)
    m3_month, m3_year = rollback_month(year, month, 3)
    m4_month, m4_year = rollback_month(year, month, 4)

    # ===== Build Params Dictionary =====
    params = {
        # Date parameters
        "end_date": end_date,
        "start_date": start_date,
        "year": year,
        "month": month,
        
        # Geography filters
        "partner_id": partner_id,
        "state_id": state_id,
        "state_ids": ",".join(state_ids) if state_ids else None,
        "district_id": district_id,
        "district_ids": ",".join(district_ids) if district_ids else None,
        "block_id": block_id,
        "block_ids": ",".join(block_ids) if block_ids else None,
        "gp_id": gp_id,
        "gp_ids": ",".join(gp_ids) if gp_ids else None,
        "creche_id": creche_id,
        "supervisor_id": supervisor_id,
        
        # Creche filters
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
        "c_status": c_status,
        "phases": phases_str,
        
        # GF1/GF1+ parameters
        "prev_priority_year": prev_priority_year,
        "prev_priority_month": prev_priority_month,
        "prev_fallback_year": prev_fallback_year,
        "prev_fallback_month": prev_fallback_month,
        
        # GF2 parameters (corrected fallback)
        "gf2_priority_year": gf2_priority_year,
        "gf2_priority_month": gf2_priority_month,
        "gf2_fallback_year": gf2_fallback_year,
        "gf2_fallback_month": gf2_fallback_month,
        
        # Zig-Zag parameters
        "m1_month": m1_month,
        "m1_year": m1_year,
        "m2_month": m2_month,
        "m2_year": m2_year,
        "m3_month": m3_month,
        "m3_year": m3_year,
        "m4_month": m4_month,
        "m4_year": m4_year,

        # Attendance trend month boundaries (T-1, T-2 and T-3)
        "m1_start_date": date(m1_year, m1_month, 1),
        "m1_end_date": date(m1_year, m1_month, calendar.monthrange(m1_year, m1_month)[1]),
        "m2_start_date": date(m2_year, m2_month, 1),
        "m2_end_date": date(m2_year, m2_month, calendar.monthrange(m2_year, m2_month)[1]),
        "m3_start_date": date(m3_year, m3_month, 1),
        "m3_end_date": date(m3_year, m3_month, calendar.monthrange(m3_year, m3_month)[1]),
    }


    # ===== Dynamic month names (mar-26 WAZ style) - ONLY change here, nothing else touched =====
    def get_month_name(m, y):
        abbr = calendar.month_abbr[m][:3].upper()
        yy = str(y)[-2:]
        return f"{abbr}-{yy} WAZ"

    m1_alias = get_month_name(m1_month, m1_year)
    m2_alias = get_month_name(m2_month, m2_year)
    m3_alias = get_month_name(m3_month, m3_year)
    m4_alias = get_month_name(m4_month, m4_year)
    gf1_prev_alias = get_month_name(prev_priority_month, prev_priority_year)
    gf2_prev_alias = get_month_name(gf2_priority_month, gf2_priority_year)

    # ===== Attendance percentage columns =====
    # Hidden by default. Only shown once the "Attendance Trend" button asks for
    # them (attendance_trend=1), in which case the selected filter month plus
    # the 2 months before it (T-1, T-2) are shown.
    show_attendance_trend = str(attendance_trend) in ("1", "True", "true", "yes")

    def get_attendance_alias(m, y):
        abbr = calendar.month_abbr[m][:3].upper()
        yy = str(y)[-2:]
        return f"Attendance Percentage ({abbr}-{yy})"

    attpct_cur_alias = get_attendance_alias(month, year)
    attpct_m1_alias = get_attendance_alias(m1_month, m1_year)
    attpct_m2_alias = get_attendance_alias(m2_month, m2_year)

    def attendance_pct_expr(att_alias, col_alias):
        return f"""
            ROUND(
                CASE
                    WHEN {att_alias}.eligible_open_days > 0
                    THEN ({att_alias}.days_attended * 100.0 / {att_alias}.eligible_open_days)
                    ELSE 0
                END, 2
            ) AS "{col_alias}\""""

    # SELECT-list fragment: current + last-2-months attendance percentage
    # columns, only populated when the trend toggle is on. Empty string otherwise.
    attendance_select = ""
    if show_attendance_trend:
        attendance_select = f"""
            ,IFNULL(att.eligible_open_days, 0) AS "Eligible Open Days"
            ,IFNULL(att.days_attended, 0) AS "Days Attended"
            ,{attendance_pct_expr('att', attpct_cur_alias)}
            ,{attendance_pct_expr('att_m1', attpct_m1_alias)}
            ,{attendance_pct_expr('att_m2', attpct_m2_alias)}"""

    def attendance_join(att_alias, start_param, end_param, guid_col):
        return f"""
        LEFT JOIN (
            SELECT
                cal.childenrolledguid,
                SUM(cal.attendance) AS days_attended,
                COUNT(ca.date_of_attendance) AS eligible_open_days
            FROM `tabChild Attendance` AS ca
            INNER JOIN `tabChild Attendance List` AS cal
                ON cal.parent = ca.name
            WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
            AND ca.date_of_attendance BETWEEN %({start_param})s AND %({end_param})s
            GROUP BY cal.childenrolledguid
        ) AS {att_alias} ON {att_alias}.childenrolledguid = {guid_col}"""

    def attendance_joins(guid_col):
        if not show_attendance_trend:
            return ""
        joins = attendance_join("att", "start_date", "end_date", guid_col)
        joins += attendance_join("att_m1", "m1_start_date", "m1_end_date", guid_col)
        joins += attendance_join("att_m2", "m2_start_date", "m2_end_date", guid_col)
        return joins

    # The child-enrollment GUID differs per query depending on table aliasing.
    attendance_joins_cee = attendance_joins("cee.childenrollguid")


    active_children = """
        -- Active Children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN `tabHousehold Form` hf ON hf.hhguid = cee.hhguid
        WHERE cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(end_date)s)
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
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    enrolled_children = """
        -- Enrolled Children --
        SELECT
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN `tabHousehold Form` hf ON hf.hhguid = cee.hhguid
        WHERE((cee.date_of_exit BETWEEN %(start_date)s AND %(end_date)s) OR
        (cee.date_of_enrollment <= %(end_date)s AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(end_date)s)))
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
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    enrolled_children_this_month = """
        -- Enrolled Children This Month --
        SELECT 
            cees.child_id as "Child ID",
            cees.child_name as "Child Name",
            DATE_FORMAT(cees.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cees.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cees.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cees.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche ",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        
        FROM `tabChild Enrollment and Exit` cees
        JOIN `tabCreche` cr ON cr.name = cees.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN `tabHousehold Form` hf ON hf.hhguid = cees.hhguid
        WHERE YEAR(cees.date_of_enrollment) = %(year)s  
        AND MONTH(cees.date_of_enrollment) = %(month)s 
        AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cees.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cees.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cees.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cees.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cees.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )               
        AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) 
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cees.child_name USING utf8mb4))
    """

    current_eligible_children = """
        SELECT
            hhc.hhcguid AS "HHCGUID",
            hhc.child_name as "Child Name",
            DATE_FORMAT(hhc.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, hhc.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN hhc.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            CASE
                WHEN COUNT(cee.name) = 0 THEN 'No'
                WHEN MIN(cee.is_exited) = 0 THEN 'Yes'
                ELSE 'No'
            END AS "Is Enrolled?",
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
          
        FROM `tabHousehold Child Form` AS hhc
        JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
        JOIN `tabCreche` AS cr ON cr.name = hf.creche_id
        LEFT JOIN `tabChild Enrollment and Exit` AS cee ON hhc.hhcguid = cee.hhcguid
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        WHERE hhc.is_dob_available = 1
        AND (hhc.child_status IS NULL OR TRIM(hhc.child_status) = '')
        AND (
            hhc.child_dob BETWEEN
                DATE_SUB(
                    IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'),
                        CURDATE(),
                        %(end_date)s
                    ),
                    INTERVAL 36 MONTH
                )
                AND
                DATE_SUB(
                    IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'),
                        CURDATE(),
                        %(end_date)s
                    ),
                    INTERVAL 6 MONTH
                )
        )
        AND (%(partner_id)s IS NULL OR hf.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND hf.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(hf.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND hf.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(hf.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND hf.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(hf.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND hf.gp_id = %(gp_id)s)
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(hf.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(creche_id)s IS NULL OR hf.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (
            %(c_status)s = 1
            OR (
                %(c_status)s != 1
                AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
                AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
                    OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            )
        )
        GROUP BY
            hhc.hhcguid,
            hhc.child_name,
            hhc.child_dob,
            hhc.gender_id,
            cr.creche_id,
            cr.creche_name,
            g.gp_name,
            b.block_name,
            d.district_name,
            s.state_name,
            p.partner_name
        ORDER BY
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)),
            TRIM(CONVERT(hhc.child_name USING utf8mb4))
    """
    
    exited_children_this_month = """
    -- exited children this month --
    SELECT
        cee.child_id as "Child ID",
        cee.child_name as "Child Name",
        DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
        TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
        CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
        DATE_FORMAT(cee.date_of_exit, '%%d-%%m-%%Y') AS "Date Of Exit",
        CASE cee.reason_for_exit
            WHEN 1 THEN 'Migrated'
            WHEN 2 THEN 'Graduated'
            WHEN 3 THEN 'Not willing to Stay'
            WHEN 4 THEN 'Death'
            WHEN 5 THEN 'Other'
            ELSE 'Unknown'
        END AS "Reason For Exit",
        cr.creche_id as "Creche ID",
        cr.creche_name as "Creche",
        g.gp_name as "GP",
        b.block_name as "Block",
        d.district_name as "District",
        s.state_name as "State",
        p.partner_name as "Partner"
    FROM `tabChild Enrollment and Exit` cee
    LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
    JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
    INNER JOIN `tabPartner` p ON p.name = cr.partner_id
    INNER JOIN `tabState` s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` d ON d.name = cr.district_id
    INNER JOIN `tabBlock` b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
    WHERE YEAR(date_of_exit) = %(year)s
    AND MONTH(date_of_exit) = %(month)s  
    AND (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s)  
    AND (
        (%(state_id)s IS NOT NULL AND cee.state_id = %(state_id)s) 
        OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cee.state_id, %(state_ids)s))
        OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
    )
    AND (
        (%(district_id)s IS NOT NULL AND cee.district_id = %(district_id)s) 
        OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cee.district_id, %(district_ids)s))
        OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
    )
    AND (
        (%(block_id)s IS NOT NULL AND cee.block_id = %(block_id)s) 
        OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cee.block_id, %(block_ids)s))
        OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
    )
    AND (
        (%(gp_id)s IS NOT NULL AND cee.gp_id = %(gp_id)s) 
        OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cee.gp_id, %(gp_ids)s))
        OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
    )
    AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
    AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
    AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
    AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
    AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
        TRIM(CONVERT(p.partner_name USING utf8mb4)),
        TRIM(CONVERT(s.state_name USING utf8mb4)),
        TRIM(CONVERT(d.district_name USING utf8mb4)),
        TRIM(CONVERT(b.block_name USING utf8mb4)),
        TRIM(CONVERT(g.gp_name USING utf8mb4)),
        TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
        TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    moderately_underweight = f"""
    -- moderly underweight children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.weight_for_age_zscore as "Weight for Age (Z-Score)"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
{attendance_joins_cee}

        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND ad.do_you_have_height_weight = 1
        AND ad.weight_for_age = 2
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    moderately_wasted = f"""

    -- moderly wasted --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.weight_for_height_zscore as "Weight for Height (Z-Score)"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
{attendance_joins_cee}
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND ad.do_you_have_height_weight = 1
        AND ad.weight_for_height = 2
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    moderately_stunted = f"""
    -- moderly stunted --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.height_for_age_zscore as "Height for Age (Z-Score)"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
{attendance_joins_cee}
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND ad.do_you_have_height_weight = 1
        AND ad.height_for_age = 2
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    severly_underweight = f"""

    -- Total Severely Underweight Children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.weight_for_age_zscore as "Weight for Age (Z-Score)"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
{attendance_joins_cee}
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND ad.do_you_have_height_weight = 1
        AND ad.weight_for_age = 1
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))    
    """
    severly_wasted = f"""
    -- Total_SAM_children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.weight_for_height_zscore as "Weight for Height (Z-Score)"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
{attendance_joins_cee}
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND ad.do_you_have_height_weight = 1
        AND ad.weight_for_height = 1
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
    severly_stunted = f"""
    -- Severely Stunted Children --
        SELECT
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.height_for_age_zscore as "Height for Age (Z-Score)"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche Name",
            g.gp_name as "GP Name",
            b.block_name as "Block Name",
            d.district_name as "District Name",
            s.state_name as "State Name",
            p.partner_name as "Partner Name"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
{attendance_joins_cee}
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND ad.do_you_have_height_weight = 1
        AND ad.height_for_age = 1
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    anthro_data_submitted = """
        SELECT 
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche",
            CASE 
                WHEN cr.creche_status_id = 1 THEN 'Planned'
                WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
                WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN cr.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabChild Growth Monitoring` cgm
        JOIN `tabCreche` cr on cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s) 
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s) 
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (
            (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s) 
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4))
            
        """
    

    anthro_data_not_submitted = """
        SELECT 
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche",
            CASE 
                WHEN cr.creche_status_id = 1 THEN 'Planned'
                WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
                WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN cr.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner"

        FROM `tabCreche` cr
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id

        WHERE NOT EXISTS (
            SELECT 1
            FROM `tabChild Growth Monitoring` cgm
            WHERE cgm.creche_id = cr.name
            AND YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
        )

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
        AND (
            cr.creche_opening_date IS NULL 
            OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s)
        )
        AND (
            (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
        )

        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4))
        """
    no_of_creches = """


        SELECT 
            tc.creche_id as "Creche ID",
            tc.creche_name as "Creche",
            CASE 
                WHEN tc.creche_status_id = 1 THEN 'Planned'
                WHEN tc.creche_status_id = 2 THEN 'Plan dropped'
                WHEN tc.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN tc.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(tc.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"

        FROM `tabCreche` tc
            LEFT JOIN `tabPartner` p ON p.name = tc.partner_id
            LEFT JOIN `tabState` s ON s.name = tc.state_id
            LEFT JOIN `tabDistrict` d ON d.name = tc.district_id
            LEFT JOIN `tabBlock` b ON b.name = tc.block_id
            LEFT JOIN `tabGram Panchayat` g ON g.name = tc.gp_id
            WHERE (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s) 
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s) 
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s) 
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND tc.gp_id = %(gp_id)s) 
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(tc.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
                AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
                AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
                AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)    
                AND (%(phases)s IS NULL OR FIND_IN_SET(tc.phase, %(phases)s))  
                AND (
                    %(c_status)s = 1
                    OR (
                        %(c_status)s != 1
                        AND (tc.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s))
                        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                            OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
                    )
                )
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(tc.creche_name USING utf8mb4))

    """

    no_creche_attendance_submitted = """

    -- no_creche_attendance_submitted --

    SELECT 
        cr.creche_id AS "Creche ID", 
        cr.creche_name AS "Creche Name",
        CASE 
            WHEN cr.creche_status_id = 1 THEN 'Planned'
            WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
            WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
            WHEN cr.creche_status_id = 4 THEN 'Closed'
            ELSE 'Unknown'
        END AS "Creche Status",
        DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
        g.gp_name AS "GP",
        b.block_name AS "Block",
        d.district_name AS "District",
        s.state_name AS "State",
        p.partner_name AS "Partner"
    FROM (
        SELECT 
            tc.name, 
            DATEDIFF(
                CASE 
                    WHEN DATE_FORMAT(CURRENT_DATE(), '%%Y-%%m') = DATE_FORMAT(%(end_date)s, '%%Y-%%m')
                    THEN CURRENT_DATE() 
                    ELSE %(end_date)s 
                END, 
                CASE 
                    WHEN tc.creche_opening_date < %(start_date)s 
                    THEN %(start_date)s
                    ELSE tc.creche_opening_date 
                END
            ) + 1 AS elgdays, 
            IFNULL(att.attdays, 0) AS attdays
        FROM 
            `tabCreche` tc 
        LEFT JOIN (
            SELECT 
                tca.creche_id, 
                COUNT(*) AS attdays 
            FROM 
                `tabChild Attendance` tca 
            WHERE 
                tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s 
            GROUP BY 
                tca.creche_id
        ) AS att 
        ON tc.name = att.creche_id 
        WHERE 
            tc.creche_opening_date IS NOT NULL 
            AND tc.creche_opening_date <= %(end_date)s
    ) AS FT
    JOIN `tabCreche` cr ON cr.name = FT.name
    INNER JOIN `tabPartner` p ON cr.partner_id = p.name
    INNER JOIN `tabState` s ON cr.state_id = s.name
    INNER JOIN `tabDistrict` d ON cr.district_id = d.name
    INNER JOIN `tabBlock` b ON cr.block_id = b.name
    INNER JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
    WHERE FT.elgdays <= FT.attdays
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
    AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
    AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4))
    """

    measurement_data_submitted = """


        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner"
        FROM `tabAnthropromatic Data` AS ad
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        INNER JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
        INNER JOIN `tabGram Panchayat` AS g ON g.name = cr.gp_id
        INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
        INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
        INNER JOIN `tabState` AS s ON s.name = cr.state_id
        INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
        WHERE ad.do_you_have_height_weight = 1
            AND YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (
                cr.creche_opening_date IS NULL 
                OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s)
            )
            AND (
                (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
            )
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))



    """

    no_of_creches_not_submitted_attendance = """
        SELECT 
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche Name",
            CASE 
                WHEN cr.creche_status_id = 1 THEN 'Planned'
                WHEN cr.creche_status_id = 2 THEN 'Plan dropped'
                WHEN cr.creche_status_id = 3 THEN 'Active/ Operational'
                WHEN cr.creche_status_id = 4 THEN 'Closed'
                ELSE 'Unknown'
            END AS "Creche Status",
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner"
        FROM (
            SELECT 
                tc.name, 
                DATEDIFF(
                    CASE 
                        WHEN DATE_FORMAT(CURRENT_DATE(), '%%Y-%%m') = DATE_FORMAT(%(end_date)s, '%%Y-%%m')
                        THEN CURRENT_DATE() 
                        ELSE %(end_date)s 
                    END, 
                    CASE 
                        WHEN tc.creche_opening_date < %(start_date)s 
                        THEN %(start_date)s
                        ELSE tc.creche_opening_date 
                    END
                ) + 1 AS elgdays, 
                IFNULL(att.attdays, 0) AS attdays
            FROM 
                `tabCreche` tc 
            LEFT JOIN (
                SELECT 
                    tca.creche_id, 
                    COUNT(*) AS attdays 
                FROM 
                    `tabChild Attendance` tca 
                WHERE 
                    tca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s 
                GROUP BY 
                    tca.creche_id
            ) AS att 
            ON tc.name = att.creche_id 
            WHERE 
                tc.creche_opening_date IS NOT NULL 
                AND tc.creche_opening_date <= %(end_date)s
        ) AS FT
        JOIN `tabCreche` cr ON cr.name = FT.name
        INNER JOIN `tabPartner` p ON cr.partner_id = p.name
        INNER JOIN `tabState` s ON cr.state_id = s.name
        INNER JOIN `tabDistrict` d ON cr.district_id = d.name
        INNER JOIN `tabBlock` b ON cr.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
        WHERE FT.elgdays > FT.attdays  -- Changed from `elgdays <= attdays` to `elgdays > attdays`
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
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
                TRIM(CONVERT(p.partner_name USING utf8mb4)),
                TRIM(CONVERT(s.state_name USING utf8mb4)),
                TRIM(CONVERT(d.district_name USING utf8mb4)),
                TRIM(CONVERT(b.block_name USING utf8mb4)),
                TRIM(CONVERT(g.gp_name USING utf8mb4)),
                TRIM(CONVERT(cr.creche_name USING utf8mb4))


"""

    measurement_data_not_submitted ="""
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner"
        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        LEFT JOIN (
            SELECT DISTINCT ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
            WHERE ad.do_you_have_height_weight = 1
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
        ) submitted ON submitted.childenrollguid = cee.childenrollguid
        WHERE cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
            AND submitted.childenrollguid IS NULL
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
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
            AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
            """

    red_flag = """
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner"
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        WHERE
            (
                ad.weight_for_age = 1
                OR ad.weight_for_height = 1
                OR ad.any_medical_major_illness = 1
                OR ad.childenrollguid IN (
                    SELECT ad_current.childenrollguid
                    FROM `tabAnthropromatic Data` AS ad_current
                    INNER JOIN `tabChild Growth Monitoring` AS cgm2
                        ON cgm2.name = ad_current.parent
                    INNER JOIN `tabAnthropromatic Data` AS ad_lyear
                        ON ad_lyear.childenrollguid = ad_current.childenrollguid
                        AND ad_lyear.do_you_have_height_weight = 1
                        AND YEAR(ad_lyear.measurement_taken_date) = %(lyear)s
                        AND MONTH(ad_lyear.measurement_taken_date) = %(lmonth)s
                        AND ad_current.weight <= ad_lyear.weight
                    INNER JOIN `tabAnthropromatic Data` AS ad_pyear
                        ON ad_pyear.childenrollguid = ad_current.childenrollguid
                        AND ad_pyear.do_you_have_height_weight = 1
                        AND YEAR(ad_pyear.measurement_taken_date) = %(pyear)s
                        AND MONTH(ad_pyear.measurement_taken_date) = %(plmonth)s
                        AND ad_lyear.weight <= ad_pyear.weight
                    WHERE ad_current.do_you_have_height_weight = 1
                    AND YEAR(ad_current.measurement_taken_date) = %(year)s
                    AND MONTH(ad_current.measurement_taken_date) = %(month)s
                )
            )
            AND YEAR(ad.measurement_taken_date) = %(year)s
            AND MONTH(ad.measurement_taken_date) = %(month)s
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
            AND (%(partner_id)s IS NULL OR cgm.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND cgm.state_id = %(state_id)s)
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cgm.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND cgm.district_id = %(district_id)s)
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cgm.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND cgm.block_id = %(block_id)s)
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cgm.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (
                (%(gp_id)s IS NOT NULL AND cgm.gp_id = %(gp_id)s)
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cgm.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))
            AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        GROUP BY cee.childenrollguid
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """


    gf1 = f"""
    SELECT
        cee.child_id AS "Child ID",
        cee.child_name AS "Child Name",
        DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
        TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
        CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
        DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
        ad.height_for_age_zscore AS "Height for Age (Z-Score)",
        ad.weight_for_height_zscore AS "Weight for Height (Z-Score)",
        ad.weight_for_age_zscore AS "Weight for Age (Z-Score)",
        ROUND(COALESCE(
            CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
            CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
        ), 2) as "{gf1_prev_alias}"{attendance_select},
        cr.creche_id AS "Creche ID",
        cr.creche_name AS "Creche",
        g.gp_name AS "GP",
        b.block_name AS "Block",
        d.district_name AS "District",
        s.state_name AS "State",
        p.partner_name AS "Partner"
    FROM
        `tabAnthropromatic Data` AS ad
    INNER JOIN
        `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
    INNER JOIN
        `tabCreche` AS cr ON cr.name = cgm.creche_id
    INNER JOIN
        `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
    LEFT JOIN
        `tabPartner` p ON p.name = cr.partner_id
    LEFT JOIN
        `tabState` s ON s.name = cr.state_id
    LEFT JOIN
        `tabDistrict` d ON d.name = cr.district_id
    LEFT JOIN
        `tabBlock` b ON b.name = cr.block_id
    LEFT JOIN
        `tabGram Panchayat` g ON g.name = cr.gp_id
    LEFT JOIN `tabAnthropromatic Data` AS ad_prev
        ON ad_prev.childenrollguid = ad.childenrollguid
        AND ad_prev.do_you_have_height_weight = 1
        AND YEAR(ad_prev.measurement_taken_date) = %(prev_priority_year)s
        AND MONTH(ad_prev.measurement_taken_date) = %(prev_priority_month)s
        AND ad_prev.weight_for_age_zscore IS NOT NULL
    LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
        ON ad_fallback.childenrollguid = ad.childenrollguid
        AND ad_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_fallback.measurement_taken_date) = %(prev_fallback_year)s
        AND MONTH(ad_fallback.measurement_taken_date) = %(prev_fallback_month)s
        AND ad_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_prev.childenrollguid IS NULL
{attendance_joins_cee}
    WHERE
        ad.do_you_have_height_weight = 1
        AND ad.weight_for_age_zscore IS NOT NULL
        AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
        AND YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        -- GF1 condition: previous WAZ - current WAZ > 0
        AND (
            COALESCE(
                CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
            )
            - CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
        ) > 0
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
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
        -- Match the date filter from the count query:
        AND (
            (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
        )
    ORDER BY
        TRIM(CONVERT(p.partner_name USING utf8mb4)),
        TRIM(CONVERT(s.state_name USING utf8mb4)),
        TRIM(CONVERT(d.district_name USING utf8mb4)),
        TRIM(CONVERT(b.block_name USING utf8mb4)),
        TRIM(CONVERT(g.gp_name USING utf8mb4)),
        TRIM(CONVERT(cr.creche_name USING utf8mb4)),
        TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
   
    # ===== GF1+ Query =====
    gf1_plus = f"""
            SELECT
                cee.child_id as "Child ID",
                cee.child_name as "Child Name",
                DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
                TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
                CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
                DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
                ad_current.height_for_age_zscore as "Height for Age (Z-Score)",
                ad_current.weight_for_height_zscore as "Weight for Height (Z-Score)",
                ad_current.weight_for_age_zscore as "Weight for Age (Z-Score)",
                ROUND(COALESCE(
                    CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                ), 2) as "{gf1_prev_alias}",
                ROUND(
                    COALESCE(
                        CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                        CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                    )
                    - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                , 2) as "WAZ Drop"{attendance_select},
                cr.creche_id as "Creche ID",
                cr.creche_name as "Creche",
                g.gp_name as "GP",
                b.block_name as "Block",
                d.district_name as "District",
                s.state_name as "State",
                p.partner_name as "Partner"
            FROM
                `tabAnthropromatic Data` AS ad_current
            INNER JOIN
                `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
            INNER JOIN
                `tabCreche` AS cr ON cr.name = cgm.creche_id
            INNER JOIN
                `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad_current.childenrollguid
            LEFT JOIN
                `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
            INNER JOIN
                `tabPartner` p ON p.name = cr.partner_id
            INNER JOIN
                `tabState` s ON s.name = cr.state_id
            INNER JOIN
                `tabDistrict` d ON d.name = cr.district_id
            INNER JOIN
                `tabBlock` b ON b.name = cr.block_id
            INNER JOIN
                `tabGram Panchayat` g ON g.name = cr.gp_id
            LEFT JOIN `tabAnthropromatic Data` AS ad_prev
                ON ad_prev.childenrollguid = ad_current.childenrollguid
                AND ad_prev.do_you_have_height_weight = 1
                AND YEAR(ad_prev.measurement_taken_date) = %(prev_priority_year)s
                AND MONTH(ad_prev.measurement_taken_date) = %(prev_priority_month)s
                AND ad_prev.weight_for_age_zscore IS NOT NULL
            LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
                ON ad_fallback.childenrollguid = ad_current.childenrollguid
                AND ad_fallback.do_you_have_height_weight = 1
                AND YEAR(ad_fallback.measurement_taken_date) = %(prev_fallback_year)s
                AND MONTH(ad_fallback.measurement_taken_date) = %(prev_fallback_month)s
                AND ad_fallback.weight_for_age_zscore IS NOT NULL
                AND ad_prev.childenrollguid IS NULL
{attendance_joins_cee}
            WHERE
                ad_current.do_you_have_height_weight = 1
                AND ad_current.weight_for_age_zscore IS NOT NULL
                AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
                AND (
                    CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                    -
                    COALESCE(
                        CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                        CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                    )
                ) <= -0.5
               
                AND YEAR(cgm.measurement_date) = %(year)s
                AND MONTH(cgm.measurement_date) = %(month)s
                AND cee.date_of_enrollment <= %(end_date)s
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
                AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
                AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
                AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
                AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
                AND (
                    (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
                    OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
                )
            ORDER BY
                TRIM(CONVERT(p.partner_name USING utf8mb4)),
                TRIM(CONVERT(s.state_name USING utf8mb4)),
                TRIM(CONVERT(d.district_name USING utf8mb4)),
                TRIM(CONVERT(b.block_name USING utf8mb4)),
                TRIM(CONVERT(g.gp_name USING utf8mb4)),
                TRIM(CONVERT(cr.creche_name USING utf8mb4)),
                TRIM(CONVERT(cee.child_name USING utf8mb4))
        """
    gf2 = f"""
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad.height_for_age_zscore AS "Height for Age (Z-Score)",
            ad.weight_for_height_zscore AS "Weight for Height (Z-Score)",
            ad.weight_for_age_zscore AS "Weight for Age (Z-Score)",
            ROUND(COALESCE(
                CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
            ), 2) as "{gf2_prev_alias}"{attendance_select},
            cr.creche_id AS "Creche ID",
            cr.creche_name AS "Creche",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner"
        FROM `tabAnthropromatic Data` AS ad
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabPartner` p ON p.name = cr.partner_id
        LEFT JOIN `tabState` s ON s.name = cr.state_id
        LEFT JOIN `tabDistrict` d ON d.name = cr.district_id
        LEFT JOIN `tabBlock` b ON b.name = cr.block_id
        LEFT JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        /* ===== GF2 PRIORITY (2 Months Ago) ===== */
        LEFT JOIN `tabAnthropromatic Data` AS ad_priority
            ON ad_priority.childenrollguid = ad.childenrollguid
            AND ad_priority.do_you_have_height_weight = 1
            AND YEAR(ad_priority.measurement_taken_date) = %(gf2_priority_year)s
            AND MONTH(ad_priority.measurement_taken_date) = %(gf2_priority_month)s
            AND ad_priority.weight_for_age_zscore IS NOT NULL
        /* ===== GF2 FALLBACK (3 Months Ago) ===== */
        LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
            ON ad_fallback.childenrollguid = ad.childenrollguid
            AND ad_fallback.do_you_have_height_weight = 1
            AND YEAR(ad_fallback.measurement_taken_date) = %(gf2_fallback_year)s
            AND MONTH(ad_fallback.measurement_taken_date) = %(gf2_fallback_month)s
            AND ad_fallback.weight_for_age_zscore IS NOT NULL
            AND ad_priority.childenrollguid IS NULL
{attendance_joins_cee}
        WHERE
            ad.do_you_have_height_weight = 1
            AND ad.weight_for_age_zscore IS NOT NULL
            /* Must have previous measurement */
            AND (
                ad_priority.weight_for_age_zscore IS NOT NULL
                OR ad_fallback.weight_for_age_zscore IS NOT NULL
            )
            /* ===== GF2 LOGIC ===== */

            AND (
                CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
                -
                COALESCE(
                    CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                )
            ) <= -0.5
            /* Current month measurement */
            AND YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            /* Active child */
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
            /* Partner Filter */
            AND (%(partner_id)s IS NULL OR cr.partner_id = %(partner_id)s)
            /* State Filter */
            AND (
                (%(state_id)s IS NOT NULL AND cr.state_id = %(state_id)s)
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            /* District Filter */
            AND (
                (%(district_id)s IS NOT NULL AND cr.district_id = %(district_id)s)
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cr.district_id, %(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            /* Block Filter */
            AND (
                (%(block_id)s IS NOT NULL AND cr.block_id = %(block_id)s)
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cr.block_id, %(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            /* GP Filter */
            AND (
                (%(gp_id)s IS NOT NULL AND cr.gp_id = %(gp_id)s)
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
                OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
            )
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
            /* Correct Date Filter */
            AND (%(cstart_date)s IS NULL OR cr.creche_opening_date >= %(cstart_date)s)
            AND (%(cend_date)s IS NULL OR cr.creche_opening_date <= %(cend_date)s)
        ORDER BY
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)),
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """
# ===== Zig-Zag Query =====
    zigzag = f"""
        SELECT
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad_current.height_for_age_zscore as "Height for Age (Z-Score)",
            ad_current.weight_for_height_zscore as "Weight for Height (Z-Score)",
            ad_current.weight_for_age_zscore as "Weight for Age (Z-Score)",
            ROUND(CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)), 2) as "{m1_alias}",
            ROUND(CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), 2) as "{m2_alias}",
            ROUND(CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)), 2) as "{m3_alias}",
            ROUND(CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)), 2) as "{m4_alias}",
            ROUND(
                CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                -
                GREATEST(
                    CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))
                )
            , 2) as "Net Drop"{attendance_select},
            cr.creche_id as "Creche ID",
            cr.creche_name as "Creche",
            g.gp_name as "GP",
            b.block_name as "Block",
            d.district_name as "District",
            s.state_name as "State",
            p.partner_name as "Partner"
        FROM
            `tabAnthropromatic Data` AS ad_current
        INNER JOIN
            `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
        INNER JOIN
            `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN
            `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad_current.childenrollguid
        LEFT JOIN
            `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        INNER JOIN
            `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN
            `tabState` s ON s.name = cr.state_id
        INNER JOIN
            `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN
            `tabBlock` b ON b.name = cr.block_id
        INNER JOIN
            `tabGram Panchayat` g ON g.name = cr.gp_id
        INNER JOIN `tabAnthropromatic Data` AS ad_m1
            ON ad_m1.childenrollguid = ad_current.childenrollguid
            AND ad_m1.do_you_have_height_weight = 1
            AND YEAR(ad_m1.measurement_taken_date) = %(m1_year)s
            AND MONTH(ad_m1.measurement_taken_date) = %(m1_month)s
            AND ad_m1.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` AS ad_m2
            ON ad_m2.childenrollguid = ad_current.childenrollguid
            AND ad_m2.do_you_have_height_weight = 1
            AND YEAR(ad_m2.measurement_taken_date) = %(m2_year)s
            AND MONTH(ad_m2.measurement_taken_date) = %(m2_month)s
            AND ad_m2.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` AS ad_m3
            ON ad_m3.childenrollguid = ad_current.childenrollguid
            AND ad_m3.do_you_have_height_weight = 1
            AND YEAR(ad_m3.measurement_taken_date) = %(m3_year)s
            AND MONTH(ad_m3.measurement_taken_date) = %(m3_month)s
            AND ad_m3.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` AS ad_m4
            ON ad_m4.childenrollguid = ad_current.childenrollguid
            AND ad_m4.do_you_have_height_weight = 1
            AND YEAR(ad_m4.measurement_taken_date) = %(m4_year)s
            AND MONTH(ad_m4.measurement_taken_date) = %(m4_month)s
            AND ad_m4.weight_for_age_zscore IS NOT NULL
{attendance_joins_cee}
        WHERE
            ad_current.do_you_have_height_weight = 1
            AND ad_current.weight_for_age_zscore IS NOT NULL
            AND YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
            AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
            AND (
                (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
                OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
            )
            AND cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))
           
            -- Zig-Zag Condition: current month - highest of prior 4 months <= -0.5
            AND (
                CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                -
                GREATEST(
                    CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))
                )
            ) <= -0.5
           
        ORDER BY
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)),
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """


    snc = f"""
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS "Current Age",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            ad_current.height_for_age_zscore AS "Height for Age (Z-Score)",
            ad_current.weight_for_height_zscore AS "Weight for Height (Z-Score)",
            ad_current.weight_for_age_zscore AS "Weight for Age (Z-Score)"{attendance_select},
            cr.creche_id AS "Creche ID",
            cr.creche_name AS "Creche",
            g.gp_name AS "GP",
            b.block_name AS "Block",
            d.district_name AS "District",
            s.state_name AS "State",
            p.partner_name AS "Partner",

            /* ===== GF1 Flag ===== */
            CASE WHEN (
                COALESCE(gf1.prev_zscore, gf1.fallback_zscore) IS NOT NULL
                AND (
                    COALESCE(gf1.prev_zscore, gf1.fallback_zscore)
                    - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                ) > 0
            ) THEN 'Yes' ELSE 'No' END AS "GF1",

            /* ===== GF1+ Flag ===== */
            CASE WHEN (
                COALESCE(gf1.prev_zscore, gf1.fallback_zscore) IS NOT NULL
                AND (
                    CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                    - COALESCE(gf1.prev_zscore, gf1.fallback_zscore)
                ) <= -0.5
            ) THEN 'Yes' ELSE 'No' END AS "GF1+",

            /* ===== GF2 Flag ===== */
            CASE WHEN (
                COALESCE(gf2.priority_zscore, gf2.fallback_zscore) IS NOT NULL
                AND (
                    CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                    - COALESCE(gf2.priority_zscore, gf2.fallback_zscore)
                ) <= -0.5
            ) THEN 'Yes' ELSE 'No' END AS "GF2",

            /* ===== Zig-Zag Flag ===== */
            CASE WHEN (
                zz.m1_zscore IS NOT NULL
                AND zz.m2_zscore IS NOT NULL
                AND zz.m3_zscore IS NOT NULL
                AND zz.m4_zscore IS NOT NULL
                AND (
                    CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                    - GREATEST(zz.m4_zscore, zz.m3_zscore, zz.m2_zscore, zz.m1_zscore)
                ) <= -0.5
                AND (
                    (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > zz.m1_zscore)
                    OR (zz.m1_zscore > zz.m2_zscore)
                    OR (zz.m2_zscore > zz.m3_zscore)
                    OR (zz.m3_zscore > zz.m4_zscore)
                )
                AND (
                    (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < zz.m1_zscore)
                    OR (zz.m1_zscore < zz.m2_zscore)
                    OR (zz.m2_zscore < zz.m3_zscore)
                    OR (zz.m3_zscore < zz.m4_zscore)
                )
            ) THEN 'Yes' ELSE 'No' END AS "Zig-Zag",

            /* ===== SUW Flag ===== */
            CASE WHEN ad_current.weight_for_age = 1
            THEN 'Yes' ELSE 'No' END AS "SUW",

            /* ===== SAM Flag ===== */
            CASE WHEN ad_current.weight_for_height = 1
            THEN 'Yes' ELSE 'No' END AS "SAM",

            /* ===== SNC Flag ===== */
            CASE WHEN (
                (
                    COALESCE(gf1.prev_zscore, gf1.fallback_zscore) IS NOT NULL
                    AND (COALESCE(gf1.prev_zscore, gf1.fallback_zscore) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))) > 0
                )
                OR (
                    COALESCE(gf1.prev_zscore, gf1.fallback_zscore) IS NOT NULL
                    AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(gf1.prev_zscore, gf1.fallback_zscore)) <= -0.5
                )
                OR (
                    COALESCE(gf2.priority_zscore, gf2.fallback_zscore) IS NOT NULL
                    AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(gf2.priority_zscore, gf2.fallback_zscore)) <= -0.5
                )
                OR (
                    zz.m1_zscore IS NOT NULL AND zz.m2_zscore IS NOT NULL
                    AND zz.m3_zscore IS NOT NULL AND zz.m4_zscore IS NOT NULL
                    AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(zz.m4_zscore, zz.m3_zscore, zz.m2_zscore, zz.m1_zscore)) <= -0.5
                    AND (
                        (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > zz.m1_zscore)
                        OR (zz.m1_zscore > zz.m2_zscore)
                        OR (zz.m2_zscore > zz.m3_zscore)
                        OR (zz.m3_zscore > zz.m4_zscore)
                    )
                    AND (
                        (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < zz.m1_zscore)
                        OR (zz.m1_zscore < zz.m2_zscore)
                        OR (zz.m2_zscore < zz.m3_zscore)
                        OR (zz.m3_zscore < zz.m4_zscore)
                    )
                )
                OR ad_current.weight_for_age = 1
                OR ad_current.weight_for_height = 1
            ) THEN 'Yes' ELSE 'No' END AS "SNC"

        FROM `tabAnthropromatic Data` AS ad_current
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid
        INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
{attendance_joins_cee}

        /* ===================================================
        GF1 / GF1+: ONE row per child, prev month preferred,
        fallback to month-2 only when prev is absent.
        MAX() on DECIMAL safely picks the one value present.
        =================================================== */
        LEFT JOIN (
            SELECT
                childenrollguid,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(prev_priority_year)s
                    AND MONTH(measurement_taken_date) = %(prev_priority_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS prev_zscore,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(prev_fallback_year)s
                    AND MONTH(measurement_taken_date) = %(prev_fallback_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS fallback_zscore
            FROM `tabAnthropromatic Data`
            WHERE do_you_have_height_weight = 1
            AND weight_for_age_zscore IS NOT NULL
            AND (
                (YEAR(measurement_taken_date) = %(prev_priority_year)s AND MONTH(measurement_taken_date) = %(prev_priority_month)s)
                OR (YEAR(measurement_taken_date) = %(prev_fallback_year)s  AND MONTH(measurement_taken_date) = %(prev_fallback_month)s)
            )
            GROUP BY childenrollguid
        ) AS gf1
            -- Honour the fallback rule: use fallback only when prev month absent
            ON gf1.childenrollguid = ad_current.childenrollguid

        /* ===================================================
        GF2: ONE row per child, month-2 preferred,
        fallback to month-3 only when month-2 absent.
        =================================================== */
        LEFT JOIN (
            SELECT
                childenrollguid,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(gf2_priority_year)s
                    AND MONTH(measurement_taken_date) = %(gf2_priority_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS priority_zscore,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(gf2_fallback_year)s
                    AND MONTH(measurement_taken_date) = %(gf2_fallback_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS fallback_zscore
            FROM `tabAnthropromatic Data`
            WHERE do_you_have_height_weight = 1
            AND weight_for_age_zscore IS NOT NULL
            AND (
                (YEAR(measurement_taken_date) = %(gf2_priority_year)s AND MONTH(measurement_taken_date) = %(gf2_priority_month)s)
                OR (YEAR(measurement_taken_date) = %(gf2_fallback_year)s  AND MONTH(measurement_taken_date) = %(gf2_fallback_month)s)
            )
            GROUP BY childenrollguid
        ) AS gf2 ON gf2.childenrollguid = ad_current.childenrollguid

        /* ===================================================
        Zig-Zag: ONE row per child covering all 4 months.
        =================================================== */
        LEFT JOIN (
            SELECT
                childenrollguid,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(m1_year)s
                    AND MONTH(measurement_taken_date) = %(m1_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS m1_zscore,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(m2_year)s
                    AND MONTH(measurement_taken_date) = %(m2_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS m2_zscore,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(m3_year)s
                    AND MONTH(measurement_taken_date) = %(m3_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS m3_zscore,
                MAX(CASE
                    WHEN YEAR(measurement_taken_date) = %(m4_year)s
                    AND MONTH(measurement_taken_date) = %(m4_month)s
                    THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                END) AS m4_zscore
            FROM `tabAnthropromatic Data`
            WHERE do_you_have_height_weight = 1
            AND weight_for_age_zscore IS NOT NULL
            AND (
                (YEAR(measurement_taken_date) = %(m1_year)s AND MONTH(measurement_taken_date) = %(m1_month)s)
                OR (YEAR(measurement_taken_date) = %(m2_year)s AND MONTH(measurement_taken_date) = %(m2_month)s)
                OR (YEAR(measurement_taken_date) = %(m3_year)s AND MONTH(measurement_taken_date) = %(m3_month)s)
                OR (YEAR(measurement_taken_date) = %(m4_year)s AND MONTH(measurement_taken_date) = %(m4_month)s)
            )
            GROUP BY childenrollguid
        ) AS zz ON zz.childenrollguid = ad_current.childenrollguid

        WHERE ad_current.do_you_have_height_weight = 1
        AND ad_current.weight_for_age_zscore IS NOT NULL
        AND YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
        AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
        AND (%(cstart_date)s IS NULL OR cr.creche_opening_date >= %(cstart_date)s)
        AND (%(cend_date)s IS NULL OR cr.creche_opening_date <= %(cend_date)s)

        /* ===== SNC WHERE filter ===== */
        AND (
            (
                COALESCE(gf1.prev_zscore, gf1.fallback_zscore) IS NOT NULL
                AND (COALESCE(gf1.prev_zscore, gf1.fallback_zscore) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))) > 0
            )
            OR (
                COALESCE(gf1.prev_zscore, gf1.fallback_zscore) IS NOT NULL
                AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(gf1.prev_zscore, gf1.fallback_zscore)) <= -0.5
            )
            OR (
                COALESCE(gf2.priority_zscore, gf2.fallback_zscore) IS NOT NULL
                AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(gf2.priority_zscore, gf2.fallback_zscore)) <= -0.5
            )
            OR (
                zz.m1_zscore IS NOT NULL AND zz.m2_zscore IS NOT NULL
                AND zz.m3_zscore IS NOT NULL AND zz.m4_zscore IS NOT NULL
                AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(zz.m4_zscore, zz.m3_zscore, zz.m2_zscore, zz.m1_zscore)) <= -0.5
                AND (
                    (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > zz.m1_zscore)
                    OR (zz.m1_zscore > zz.m2_zscore)
                    OR (zz.m2_zscore > zz.m3_zscore)
                    OR (zz.m3_zscore > zz.m4_zscore)
                )
                AND (
                    (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < zz.m1_zscore)
                    OR (zz.m1_zscore < zz.m2_zscore)
                    OR (zz.m2_zscore < zz.m3_zscore)
                    OR (zz.m3_zscore < zz.m4_zscore)
                )
            )
            OR ad_current.weight_for_age = 1
            OR ad_current.weight_for_height = 1
        )

        ORDER BY
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)),
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """

    # Choose query based on type
    if str(query_type) == "active_children":
         final_query = active_children
    elif str(query_type) == "enrolled_children":
         final_query = enrolled_children
    elif str(query_type) == "enrolled_children_this_month":
        final_query = enrolled_children_this_month
    elif str(query_type) == "current_eligible_children":
        final_query = current_eligible_children
    elif str(query_type) == "exited_children_this_month":
        final_query = exited_children_this_month
    elif str(query_type) == "moderately_underweight":
        final_query = moderately_underweight
    elif str(query_type) == "moderately_wasted":
        final_query = moderately_wasted
    elif str(query_type) == "moderately_stunted":
        final_query = moderately_stunted
    elif str(query_type) == "gf1":
        final_query = gf1
    elif str(query_type) == "severly_underweight":
        final_query = severly_underweight
    elif str(query_type) == "severly_wasted":
        final_query = severly_wasted
    elif str(query_type) == "severly_stunted":
        final_query = severly_stunted
    elif str(query_type) == "gf1_plus" or str(query_type) == "gf1+":
        final_query = gf1_plus
    elif str(query_type) == "gf2":
        final_query = gf2
    elif str(query_type) == "zigzag":
        final_query = zigzag
    elif str(query_type) == "snc":
        final_query = snc
    elif str(query_type) == "no_creche_attendance_submitted":
        final_query = no_creche_attendance_submitted
    elif str(query_type) == "anthro_data_submitted":
        final_query = anthro_data_submitted
    elif str(query_type) == "anthro_data_not_submitted":
        final_query = anthro_data_not_submitted
    elif str(query_type) == "no_of_creches":
        final_query = no_of_creches
    elif str(query_type) == "measurement_data_submitted":
        final_query = measurement_data_submitted
    elif str(query_type) == "no_of_creches_not_submitted_attendance":
        final_query = no_of_creches_not_submitted_attendance
    elif str(query_type) == "measurement_data_not_submitted":
        final_query = measurement_data_not_submitted
    elif str(query_type) == "red_flag":
        final_query = red_flag

    else:
        frappe.response["Error"] = "Invalid query_type parameter"
        return


    result = frappe.db.sql(final_query, params, as_dict=True)
    if str(query_type) == "current_eligible_children":
        for record in result:
            if 'HHCGUID' in record:
                del record['HHCGUID']

    frappe.response["data"] = result or []




