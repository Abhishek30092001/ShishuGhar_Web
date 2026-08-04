from datetime import date
import frappe
import calendar

@frappe.whitelist()
def fetch_card_data(usr=None, pw=None, partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, village_id=None, creche_id=None, year=None, month=None, supervisor_id=None, cstart_date=None, cend_date=None, c_status=None, phases=None, query_type="active_children"):
    year = int(year) if year and str(year).isdigit() else date.today().year
    month = int(month) if month and str(month).isdigit() else date.today().month
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

    # Resolve User Context (handles both API 'usr' and internal 'frappe.session.user')
    current_user = usr or frappe.session.user
    
    # Get current user's partner if not provided explicitly
    if not partner_id:
        partner_id = frappe.db.get_value("User", current_user, "partner")

    state_ids = []
    district_ids = []
    block_ids = []
    gp_ids = []
    village_ids = []

    # Fetch user's geography mapping
    if current_user and not (state_id or district_id or block_id or gp_id):
        geography_query = """ 
            SELECT 
                ugm.state_id, 
                ugm.district_id, 
                ugm.block_id, 
                ugm.gp_id,
                ugm.village_id
            FROM `tabUser Geography Mapping` AS ugm
            LEFT JOIN `tabUser` AS u ON u.name = ugm.parent 
            WHERE u.email = %s OR u.name = %s
        """
        current_user_geography = frappe.db.sql(geography_query, (current_user, current_user), as_dict=True)
        
        if current_user_geography:
            state_ids = [str(g["state_id"]) for g in current_user_geography if g.get("state_id")]
            district_ids = [str(g["district_id"]) for g in current_user_geography if g.get("district_id")]
            block_ids = [str(g["block_id"]) for g in current_user_geography if g.get("block_id")]
            gp_ids = [str(g["gp_id"]) for g in current_user_geography if g.get("gp_id")]
            village_ids = [str(g["village_id"]) for g in current_user_geography if g.get("village_id")]

    # Parse phases parameter
    if phases:
        try:
            phases_list = [p.strip() for p in phases.split(",") if p.strip().isdigit()]
            phases_str = ",".join(phases_list) if phases_list else None
        except:
            phases_str = None
    else:
        phases_str = None

    # Overrides and Normalization
    if creche_id:
        supervisor_id = None
        
    partner_id = None if not partner_id else partner_id
    state_id = None if not state_id else state_id

    # ===== MONTH CALCULATIONS =====
    
    # 1. Standard Fallback Months (lmonth, lyear, plmonth, pyear) -> REQUIRED BY "REST" CARDS
    if month == 1:
        lmonth = 12
        plmonth = 11
        lyear = year - 1
        pyear = year - 1
    elif month == 2:
        lmonth = 1
        plmonth = 12
        lyear = year
        pyear = year - 1
    else:
        lmonth = month - 1
        plmonth = month - 2
        lyear = year
        pyear = year

    # 2. GF1/GF1+ Parameters
    prev_priority_month = lmonth
    prev_priority_year = lyear
    prev_fallback_month = plmonth
    prev_fallback_year = pyear

    # 3. GF2 & Extended Fallback Parameters (prev3, prev4)
    if month <= 2:
        gf2_priority_year = year - 1
        gf2_priority_month = month + 10
        gf2_fallback_year = year - 1
        gf2_fallback_month = month + 9
    elif month == 3:
        gf2_priority_year = year
        gf2_priority_month = 1
        gf2_fallback_year = year - 1
        gf2_fallback_month = 12
    else:
        gf2_priority_year = year
        gf2_priority_month = month - 2
        gf2_fallback_year = year
        gf2_fallback_month = month - 3

    # Ensure prev3 logic for standard fallback aligns
    prev3_month = gf2_fallback_month
    prev3_year = gf2_fallback_year
    
    if month <= 4:
        if month == 1:
            prev4_month = 9
            prev4_year = year - 1
        elif month == 2:
            prev4_month = 10
            prev4_year = year - 1
        elif month == 3:
            prev4_month = 11
            prev4_year = year - 1
        else:  # month == 4
            prev4_month = 12
            prev4_year = year - 1
    else:
        prev4_month = month - 4
        prev4_year = year

    # 4. Zig-Zag Parameters: T-1 to T-4
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

    def get_month_name(m, y):
        """Generate month alias like 'JAN-25 WAZ'"""
        abbr = calendar.month_abbr[m][:3].upper()
        yy = str(y)[-2:]
        return f"{abbr}-{yy} WAZ"

    m1_alias = get_month_name(m1_month, m1_year)
    m2_alias = get_month_name(m2_month, m2_year)
    m3_alias = get_month_name(m3_month, m3_year)
    m4_alias = get_month_name(m4_month, m4_year)
    gf1_prev_alias = get_month_name(prev_priority_month, prev_priority_year)
    gf2_prev_alias = get_month_name(gf2_priority_month, gf2_priority_year)

    # Convert lists to comma-separated strings
    state_ids_str = ",".join(state_ids) if state_ids else None
    district_ids_str = ",".join(district_ids) if district_ids else None
    block_ids_str = ",".join(block_ids) if block_ids else None
    gp_ids_str = ",".join(gp_ids) if gp_ids else None
    village_ids_str = ",".join(village_ids) if village_ids else None

    # ===== BUILD PARAMETERS DICTIONARY =====
    params = {
        # Core & Date parameters
        "end_date": end_date,
        "start_date": start_date,
        "year": year,
        "month": month,
        
        # Standard Fallback variables (Fixes Server Error for generic cards)
        "lyear": lyear,
        "lmonth": lmonth,
        "plmonth": plmonth,
        "pyear": pyear,
        "prev3_year": prev3_year,
        "prev3_month": prev3_month,
        "prev4_year": prev4_year,
        "prev4_month": prev4_month,
        
        # Geography filters
        "partner_id": partner_id,
        "partner_ids": None,
        "state_id": state_id,
        "state_ids": state_ids_str,
        "district_id": district_id,
        "district_ids": district_ids_str,
        "block_id": block_id,
        "block_ids": block_ids_str,
        "gp_id": gp_id,
        "gp_ids": gp_ids_str,
        "village_id": village_id,
        "village_ids": village_ids_str,
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
        
        # GF2 parameters
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
        
        # Aliases
        "m1_alias": m1_alias,
        "m2_alias": m2_alias,
        "m3_alias": m3_alias,
        "m4_alias": m4_alias,
        "gf1_prev_alias": gf1_prev_alias,
        "gf2_prev_alias": gf2_prev_alias
    }


    # ---------- Existing queries (unchanged) ----------
    no_of_creches = """
    SELECT 
        tc.creche_id AS "Creche ID",
        tc.creche_name AS "Creche Name",
        CASE 
            WHEN tc.creche_status_id = 1 THEN 'Planned'
            WHEN tc.creche_status_id = 2 THEN 'Plan dropped'
            WHEN tc.creche_status_id = 3 THEN 'Active/ Operational'
            WHEN tc.creche_status_id = 4 THEN 'Closed'
            ELSE 'Unknown'
        END AS "Creche Status",
        DATE_FORMAT(tc.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date"
    FROM `tabCreche` AS tc
    WHERE 
        (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)
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
        AND (%(village_id)s IS NULL OR tc.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR tc.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR tc.name = %(creche_id)s)
        AND (%(c_status)s IS NULL OR tc.creche_status_id = %(c_status)s)
        AND (tc.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s))
        AND (
            (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR
            (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
        );
    """

    active_children = """
        -- Active Children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"

        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id 
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
        AND (%(village_id)s IS NULL OR cr.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
            OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ORDER BY cee.child_id, cee.child_name  
    """

    enrolled_children_this_month = """
        -- Enrolled Children This Month --
        SELECT 
            cees.child_id as "Child ID",
            cees.child_name as "Child Name",
            DATE_FORMAT(cees.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cees.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cees.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
        
        FROM `tabChild Enrollment and Exit` cees
        JOIN `tabCreche` cr ON cr.name = cees.creche_id
        LEFT JOIN `tabHousehold Form` hf ON hf.hhguid = cees.hhguid
        WHERE YEAR(cees.date_of_enrollment) = %(year)s  
        AND MONTH(cees.date_of_enrollment) = %(month)s 
        AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cees.state_id, %(state_ids)s))
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
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cees.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )            
        AND (%(village_id)s IS NULL OR cees.village_id = %(village_id)s)
        AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)) 
    """



    enrolled_children = """
        -- Enrolled Children --
        SELECT 
            cees.child_id as "Child ID",
            cees.child_name as "Child Name",
            DATE_FORMAT(cees.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cees.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cees.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
        FROM `tabChild Enrollment and Exit` AS cees
        INNER JOIN `tabCreche` AS cr ON cr.name = cees.creche_id
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cees.hhguid
        WHERE ((cees.date_of_exit BETWEEN %(start_date)s AND %(end_date)s) OR
        (cees.date_of_enrollment <= %(end_date)s AND (cees.date_of_exit IS NULL OR cees.date_of_exit >= %(end_date)s)))
        AND (%(partner_id)s IS NULL OR cees.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND cees.state_id = %(state_id)s) 
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cees.state_id, %(state_ids)s))
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
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cees.gp_id, %(gp_ids)s))
            OR (%(gp_id)s IS NULL AND %(gp_ids)s IS NULL)
        )
        AND (%(creche_id)s IS NULL OR cees.creche_id = %(creche_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
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
        ORDER BY cees.child_id, cees.child_name
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
            cr.creche_name as "Creche"
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
            cr.creche_name
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
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name AS "Household Head Name",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche Name"
        FROM `tabChild Enrollment and Exit` AS cee
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        JOIN `tabCreche` AS cr ON cr.name = cee.creche_id
        WHERE 
            YEAR(cee.date_of_exit) = %(year)s AND  
            MONTH(cee.date_of_exit) = %(month)s AND  
            (%(partner_id)s IS NULL OR cee.partner_id = %(partner_id)s)
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
            AND (%(village_id)s IS NULL OR cee.village_id = %(village_id)s)
            AND (%(creche_id)s IS NULL OR cee.creche_id = %(creche_id)s)
            AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)    
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
    """
    moderately_underweight = """
    -- moderly underweight children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id

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
        AND (%(village_id)s IS NULL OR cr.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """
    moderately_wasted = """
    -- moderly wasted --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
            
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND ad.do_you_have_height_weight = 1
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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
        AND (%(village_id)s IS NULL OR cr.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """
    moderately_stunted = """
    -- moderly stunted --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
        WHERE YEAR(cgm.measurement_date) = %(year)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
        AND MONTH(cgm.measurement_date) = %(month)s
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
        AND (%(village_id)s IS NULL OR cr.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """

    severly_underweight = """
    -- Total Severely Underweight Children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
        
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """
    severly_wasted = """
    -- Total_SAM_children --
        SELECT 
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"

        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """
    severly_stunted = """
    -- Severely Stunted Children --
        SELECT
            cee.child_id as "Child ID",
            cee.child_name as "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "Child DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            hf.hosuehold_head_name as "Household Head Name",
            cr.creche_id as "Creche ID", 
            cr.creche_name as "Creche Name"
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        LEFT JOIN`tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabHousehold Form` AS hf ON hf.hhguid = cee.hhguid
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
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
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
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date"
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
        AND (%(village_id)s IS NULL OR cr.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cr.name = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """
   
    anthro_data_submitted = """
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
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date"
        FROM `tabChild Growth Monitoring` AS cgm
        JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
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
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
        AND (%(creche_id)s IS NULL OR cgm.creche_id = %(creche_id)s)
        AND (%(c_status)s IS NULL OR cr.creche_status_id = %(c_status)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
        AND ((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
    """

    measurement_data_submitted = """
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche"
        FROM `tabAnthropromatic Data` AS ad
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
        INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id
        INNER JOIN `tabBlock` b ON b.name = cr.block_id
        INNER JOIN `tabDistrict` d ON d.name = cr.district_id
        INNER JOIN `tabState` s ON s.name = cr.state_id
        INNER JOIN `tabPartner` p ON p.name = cr.partner_id
    WHERE ad.do_you_have_height_weight = 1
        AND YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
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
        AND (%(village_id)s IS NULL OR cgm.village_id = %(village_id)s)
        AND (cr.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s ))
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

    measurement_data_not_submitted ="""
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche"
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
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(end_date)s)
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
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date"
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
            DATE_FORMAT(cr.creche_opening_date, '%%d-%%m-%%Y') AS "Opening Date"

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

    red_flag = """
        SELECT
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS "DOB",
            CASE WHEN cee.gender_id = 1 THEN 'M' ELSE 'F' END AS "Gender",
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS "Date Of Enrollment",
            cr.creche_id AS "Creche ID", 
            cr.creche_name AS "Creche"
        FROM `tabAnthropromatic Data` ad
        INNER JOIN `tabChild Growth Monitoring` cgm ON cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
        INNER JOIN `tabCreche` cr ON cr.name = cgm.creche_id
        INNER JOIN `tabPartner` p ON cr.partner_id = p.name
        INNER JOIN `tabState` s ON cr.state_id = s.name
        INNER JOIN `tabDistrict` d ON cr.district_id = d.name
        INNER JOIN `tabBlock` b ON cr.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON cr.gp_id = g.name
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
            AND (cr.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND cr.creche_opening_date <= %(end_date)s))

        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(cr.creche_name USING utf8mb4)), 
            TRIM(CONVERT(cee.child_name USING utf8mb4))
    """ 

# ===== GF1 QUERY (IMPROVEMENT: prev - current > 0) =====
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
        ), 2) as "{gf1_prev_alias}",
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
    WHERE
        ad.do_you_have_height_weight = 1
        AND ad.weight_for_age_zscore IS NOT NULL
        AND (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
        AND YEAR(cgm.measurement_date) = %(year)s
        AND MONTH(cgm.measurement_date) = %(month)s
        AND cee.date_of_enrollment <= %(end_date)s
        AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
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

    # ===== GF1+ QUERY (DECLINE <= -0.5 FROM PREVIOUS MONTH) =====
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
        cr.creche_id as "Creche ID",
        cr.creche_name as "Creche",
        g.gp_name as "GP",
        b.block_name as "Block",
        d.district_name as "District",
        s.state_name as "State",
        p.partner_name as "Partner",
        ROUND(COALESCE(
            CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
            CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
        ), 2) as "{gf1_prev_alias}",
        ROUND(
            CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
            -
            COALESCE(
                CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
            )
        , 2) as "WAZ Drop"
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

    # ===== GF2 QUERY (DECLINE <= -0.5 FROM 2-3 MONTHS AGO) =====
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
        ), 2) as "{gf2_prev_alias}",
        ROUND(
            CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
            -
            COALESCE(
                CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))
            )
        , 2) as "WAZ Drop",
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
    LEFT JOIN `tabAnthropromatic Data` AS ad_priority
        ON ad_priority.childenrollguid = ad.childenrollguid
        AND ad_priority.do_you_have_height_weight = 1
        AND YEAR(ad_priority.measurement_taken_date) = %(gf2_priority_year)s
        AND MONTH(ad_priority.measurement_taken_date) = %(gf2_priority_month)s
        AND ad_priority.weight_for_age_zscore IS NOT NULL
    LEFT JOIN `tabAnthropromatic Data` AS ad_fallback
        ON ad_fallback.childenrollguid = ad.childenrollguid
        AND ad_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_fallback.measurement_taken_date) = %(gf2_fallback_year)s
        AND MONTH(ad_fallback.measurement_taken_date) = %(gf2_fallback_month)s
        AND ad_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_priority.childenrollguid IS NULL
    WHERE
        ad.do_you_have_height_weight = 1
        AND ad.weight_for_age_zscore IS NOT NULL
        AND (
            ad_priority.weight_for_age_zscore IS NOT NULL
            OR ad_fallback.weight_for_age_zscore IS NOT NULL
        )
        AND (
            CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))
            -
            COALESCE(
                CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)),
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

    # ===== ZIG-ZAG QUERY (PATTERN WITH ALTERNATING INCREASES/DECREASES AND NET DROP <= -0.5) =====
    zig_zag = f"""
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
        cr.creche_id as "Creche ID",
        cr.creche_name as "Creche",
        g.gp_name as "GP",
        b.block_name as "Block",
        d.district_name as "District",
        s.state_name as "State",
        p.partner_name as "Partner",
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
        , 2) as "Net Drop"
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
    # ===== SNC QUERY (UNION OF ALL CATEGORIES: GF1+, GF2, ZIG-ZAG, AND SEVERE MALNUTRITION) =====

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
        ad_current.weight_for_age_zscore AS "Weight for Age (Z-Score)",
        cr.creche_id AS "Creche ID",
        cr.creche_name AS "Creche",
        g.gp_name AS "GP",
        b.block_name AS "Block",
        d.district_name AS "District",
        s.state_name AS "State",
        p.partner_name AS "Partner",

        /* ===== NEWLY ADDED STATUS FIELDS (Yes / No) ===== */
        CASE WHEN (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
                  AND (COALESCE(CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))) > 0
             THEN 'Yes' ELSE 'No' END AS "Gf1",

        CASE WHEN (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
                  AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
             THEN 'Yes' ELSE 'No' END AS "GF1+",

        CASE WHEN (ad_gf2_priority.weight_for_age_zscore IS NOT NULL OR ad_gf2_fallback.weight_for_age_zscore IS NOT NULL)
                  AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_gf2_priority.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_gf2_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
             THEN 'Yes' ELSE 'No' END AS "Gf2",

        CASE WHEN ad_zz_m1.weight_for_age_zscore IS NOT NULL 
                  AND ad_zz_m2.weight_for_age_zscore IS NOT NULL
                  AND ad_zz_m3.weight_for_age_zscore IS NOT NULL 
                  AND ad_zz_m4.weight_for_age_zscore IS NOT NULL
                  AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
                  AND (
                      (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                  )
                  AND (
                      (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                  )
             THEN 'Yes' ELSE 'No' END AS "Zig-Zag",

        CASE WHEN CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < -2 
                  AND CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) >= -3 
             THEN 'Yes' ELSE 'No' END AS "SAM",

        CASE WHEN CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < -3 
                  OR ad_current.weight_for_age = 1 
             THEN 'Yes' ELSE 'No' END AS "SUW"

    FROM `tabAnthropromatic Data` AS ad_current
    INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
    INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid
    INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
    INNER JOIN `tabPartner` p ON p.name = cr.partner_id
    INNER JOIN `tabState` s ON s.name = cr.state_id
    INNER JOIN `tabDistrict` d ON d.name = cr.district_id
    INNER JOIN `tabBlock` b ON b.name = cr.block_id
    INNER JOIN `tabGram Panchayat` g ON g.name = cr.gp_id

    -- ===== GF1 & GF1+: Previous month (1 month ago or fallback 2 months) =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_prev
        ON ad_gf1_prev.childenrollguid = ad_current.childenrollguid
        AND ad_gf1_prev.do_you_have_height_weight = 1
        AND YEAR(ad_gf1_prev.measurement_taken_date) = %(prev_priority_year)s
        AND MONTH(ad_gf1_prev.measurement_taken_date) = %(prev_priority_month)s
        AND ad_gf1_prev.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_gf1_fallback
        ON ad_gf1_fallback.childenrollguid = ad_current.childenrollguid
        AND ad_gf1_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_gf1_fallback.measurement_taken_date) = %(prev_fallback_year)s
        AND MONTH(ad_gf1_fallback.measurement_taken_date) = %(prev_fallback_month)s
        AND ad_gf1_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_gf1_prev.childenrollguid IS NULL

    -- ===== GF2: Priority (2 months ago) and Fallback (3 months ago) =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_priority
        ON ad_gf2_priority.childenrollguid = ad_current.childenrollguid
        AND ad_gf2_priority.do_you_have_height_weight = 1
        AND YEAR(ad_gf2_priority.measurement_taken_date) = %(gf2_priority_year)s
        AND MONTH(ad_gf2_priority.measurement_taken_date) = %(gf2_priority_month)s
        AND ad_gf2_priority.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_gf2_fallback
        ON ad_gf2_fallback.childenrollguid = ad_current.childenrollguid
        AND ad_gf2_fallback.do_you_have_height_weight = 1
        AND YEAR(ad_gf2_fallback.measurement_taken_date) = %(gf2_fallback_year)s
        AND MONTH(ad_gf2_fallback.measurement_taken_date) = %(gf2_fallback_month)s
        AND ad_gf2_fallback.weight_for_age_zscore IS NOT NULL
        AND ad_gf2_priority.childenrollguid IS NULL

    -- ===== Zig-Zag: 4 Previous Months (T-1 to T-4) =====
    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m1
        ON ad_zz_m1.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m1.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m1.measurement_taken_date) = %(m1_year)s
        AND MONTH(ad_zz_m1.measurement_taken_date) = %(m1_month)s
        AND ad_zz_m1.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m2
        ON ad_zz_m2.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m2.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m2.measurement_taken_date) = %(m2_year)s
        AND MONTH(ad_zz_m2.measurement_taken_date) = %(m2_month)s
        AND ad_zz_m2.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m3
        ON ad_zz_m3.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m3.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m3.measurement_taken_date) = %(m3_year)s
        AND MONTH(ad_zz_m3.measurement_taken_date) = %(m3_month)s
        AND ad_zz_m3.weight_for_age_zscore IS NOT NULL

    LEFT JOIN `tabAnthropromatic Data` AS ad_zz_m4
        ON ad_zz_m4.childenrollguid = ad_current.childenrollguid
        AND ad_zz_m4.do_you_have_height_weight = 1
        AND YEAR(ad_zz_m4.measurement_taken_date) = %(m4_year)s
        AND MONTH(ad_zz_m4.measurement_taken_date) = %(m4_month)s
        AND ad_zz_m4.weight_for_age_zscore IS NOT NULL

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
    AND (
        (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL)
        OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
    )
    
    /* ===== Unified SNC Logic Block - ALL CONDITIONS ===== */
    AND (
        -- CONDITION 1: GF1 - ANY Decline > 0 from previous month (or fallback)
        (
            (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
            AND (
                COALESCE(
                    CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                ) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
            ) > 0
        )
        OR
        -- CONDITION 2: GF1+ - Decline <= -0.5 from previous month (or fallback)
        (
            (ad_gf1_prev.weight_for_age_zscore IS NOT NULL OR ad_gf1_fallback.weight_for_age_zscore IS NOT NULL)
            AND (
                CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                -
                COALESCE(
                    CAST(ad_gf1_prev.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_gf1_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                )
            ) <= -0.5
        )
        OR
        -- CONDITION 3: GF2 - Decline <= -0.5 from 2-3 months ago
        (
            (ad_gf2_priority.weight_for_age_zscore IS NOT NULL OR ad_gf2_fallback.weight_for_age_zscore IS NOT NULL)
            AND (
                CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                -
                COALESCE(
                    CAST(ad_gf2_priority.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_gf2_fallback.weight_for_age_zscore AS DECIMAL(10,4))
                )
            ) <= -0.5
        )
        OR
        -- CONDITION 4: Zig-Zag Pattern - Alternating increases/decreases with net decline <= -0.5
        (
            ad_zz_m1.weight_for_age_zscore IS NOT NULL 
            AND ad_zz_m2.weight_for_age_zscore IS NOT NULL
            AND ad_zz_m3.weight_for_age_zscore IS NOT NULL 
            AND ad_zz_m4.weight_for_age_zscore IS NOT NULL
            AND (
                CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))
                -
                GREATEST(
                    CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)),
                    CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4))
                )
            ) <= -0.5
            -- Alternating increases
            AND (
                (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))
                OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)))
                OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)))
                OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
            )
            -- Alternating decreases
            AND (
                (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)))
                OR (CAST(ad_zz_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)))
                OR (CAST(ad_zz_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)))
                OR (CAST(ad_zz_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_zz_m4.weight_for_age_zscore AS DECIMAL(10,4)))
            )
        )
        OR
        -- CONDITION 5: Severe Malnutrition - Direct flags
        ad_current.weight_for_height = 1
        OR
        ad_current.weight_for_age = 1
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


    # ----- Choose query based on type -----
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
    elif str(query_type) == "gf1_plus":
        final_query = gf1_plus
    elif str(query_type) == "severly_underweight":
        final_query = severly_underweight
    elif str(query_type) == "severly_wasted":
        final_query = severly_wasted
    elif str(query_type) == "severly_stunted":
        final_query = severly_stunted
    elif str(query_type) == "gf2":
        final_query = gf2
    elif str(query_type) == "zig_zag":
        final_query = zig_zag
    elif str(query_type) == "snc":
        final_query = snc
    elif str(query_type) == "no_creche_attendance_submitted":
        final_query = no_creche_attendance_submitted
    elif str(query_type) == "anthro_data_submitted":
        final_query = anthro_data_submitted
    elif str(query_type) == "no_of_creches":
        final_query = no_of_creches
    elif str(query_type) == "measurement_data_submitted":
        final_query = measurement_data_submitted
    elif str(query_type) == "no_of_creches_not_submitted_attendance":
        final_query = no_of_creches_not_submitted_attendance
    elif str(query_type) == "measurement_data_not_submitted":
        final_query = measurement_data_not_submitted
    elif str(query_type) == "anthro_data_not_submitted":
        final_query = anthro_data_not_submitted
    elif str(query_type) == "red_flag":
        final_query = red_flag
    else:
        frappe.response["Error"] = "Invalid query_type parameter"
        return

    result = frappe.db.sql(final_query, params, as_dict=True)
    frappe.response["data"] = result or []