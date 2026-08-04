import frappe
from datetime import date
import calendar


@frappe.whitelist()
def hr_dashboard_details(partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None, year=None, month=None, cstart_date=None, cend_date=None, query_type="operational_creches", is_active=None):
    
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None
    
    if year and month:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    else:
        start_date = None
        end_date = None

    # Get current user's partner
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = partner_id or current_user_partner

    # Get current user's geography mapping
    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """

    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    # Extract allowed geography IDs for the current user
    state_ids = [str(x["state_id"]) for x in current_user_state if x.get("state_id")]
    district_ids = [str(x["district_id"]) for x in current_user_state if x.get("district_id")]
    block_ids = [str(x["block_id"]) for x in current_user_state if x.get("block_id")]
    gp_ids = [str(x["gp_id"]) for x in current_user_state if x.get("gp_id")]

    # Set filter values - use provided values or None if not provided
    partner_id = partner_id if partner_id else None
    state_id = state_id if state_id else None
    district_id = district_id if district_id else None
    block_id = block_id if block_id else None
    gp_id = gp_id if gp_id else None
    creche_id = creche_id if creche_id else None

    # Prepare parameters for SQL queries
    params = {
        "end_date": end_date,
        "start_date": start_date,
        "cstart_date": cstart_date, 
        "cend_date": cend_date,
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
        "year": year,
        "month": month,
        "query_type": query_type,
        "is_active": is_active
    }



    operational_creches = """
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
           AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
           AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
            AND tc.creche_status_id = 3
        ORDER BY 
            TRIM(CONVERT(p.partner_name USING utf8mb4)),
            TRIM(CONVERT(s.state_name USING utf8mb4)),
            TRIM(CONVERT(d.district_name USING utf8mb4)),
            TRIM(CONVERT(b.block_name USING utf8mb4)),
            TRIM(CONVERT(g.gp_name USING utf8mb4)),
            TRIM(CONVERT(tc.creche_name USING utf8mb4))

    """

    partners = """
        SELECT DISTINCT  
        p.partner_name as "Partners"
        FROM `tabPartner` as p
        LEFT JOIN `tabCreche` AS c ON p.name = c.partner_id
        WHERE p.is_active = 1
        AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)

        AND (
            (%(state_id)s IS NOT NULL AND c.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(c.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )

        AND (
            (%(district_id)s IS NOT NULL AND c.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(c.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )

        AND (
            (%(block_id)s IS NOT NULL AND c.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(c.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (c.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s ))
        AND (p.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND p.date_of_joining <= %(end_date)s ))
    
    """

    states = """
        SELECT DISTINCT
            s.state_code AS 'State ID',
            s.state_name AS 'State Name'
        FROM `tabState` AS s
        LEFT JOIN `tabCreche` AS c ON s.name = c.state_id
        WHERE s.is_active = 1
        AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)

        AND (
            (%(state_id)s IS NOT NULL AND c.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(c.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )

        AND (
            (%(district_id)s IS NOT NULL AND c.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(c.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )

        AND (
            (%(block_id)s IS NOT NULL AND c.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(c.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (c.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s ))
    """


    districts = """
        SELECT DISTINCT
            d.district_name AS 'District Name',
            d.district_code AS 'District ID',
            s.state_name AS 'State Name'
        FROM `tabDistrict` AS d
        LEFT JOIN `tabCreche` AS c ON d.name = c.district_id
        LEFT JOIN `tabState` AS s ON d.state_id = s.name
        WHERE d.is_active = 1
        AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND c.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(c.state_id, %(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND c.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(c.district_id, %(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND c.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(c.block_id, %(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (c.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s ))
        ;
    """


    blocks = """
        SELECT DISTINCT
            b.block_code AS 'Block ID',
            b.block_name AS 'Block Name',
            d.district_name AS 'District Name',
            s.state_name AS 'State Name'
        FROM `tabBlock` AS b
        LEFT JOIN `tabCreche` AS c ON b.name = c.block_id
        LEFT JOIN `tabDistrict` AS d ON b.district_id = d.name
        LEFT JOIN `tabState` AS s ON b.state_id = s.name
        WHERE b.is_active = 1
        AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND c.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(c.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND c.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(c.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND c.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(c.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (c.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s ))

        ;
    """


    program_managers = """
        SELECT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type AS "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            GROUP_CONCAT(DISTINCT s.state_name SEPARATOR ', ') AS "State"
        FROM `tabUser` AS u
        INNER JOIN `tabPartner` AS p ON p.name = u.partner
        LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
        LEFT JOIN `tabState` AS s ON s.name = ugm.state_id
        WHERE u.type = 'Program Manager'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )

        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        GROUP BY u.name;
    """


    cluster_coordinators = """
        SELECT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type AS "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            s.state_name AS "State",
            GROUP_CONCAT(DISTINCT d.district_name SEPARATOR ', ') AS "District",
            GROUP_CONCAT(DISTINCT b.block_name SEPARATOR ', ') AS "Block"
        FROM `tabUser` AS u
        INNER JOIN `tabPartner` AS p ON p.name = u.partner
        INNER JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
        INNER JOIN `tabState` AS s ON s.name = ugm.state_id
        LEFT JOIN `tabDistrict` AS d ON ugm.district_id = d.name
        LEFT JOIN `tabBlock` AS b ON ugm.block_id = b.name
        WHERE u.type = 'Cluster Coordinator'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s))
        GROUP BY u.name;
    
    """


    logistic_coordinators = """
        SELECT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type AS "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            s.state_name AS "State",
            GROUP_CONCAT(DISTINCT d.district_name SEPARATOR ', ') AS "District",
            GROUP_CONCAT(DISTINCT b.block_name SEPARATOR ', ') AS "Block"
        FROM `tabUser` AS u
        LEFT JOIN `tabPartner` AS p ON p.name = u.partner
        LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
        LEFT JOIN `tabState` AS s ON s.name = ugm.state_id
        LEFT JOIN `tabDistrict` AS d ON ugm.district_id = d.name
        LEFT JOIN `tabBlock` AS b ON ugm.block_id = b.name
        WHERE u.type = 'Accounts and Logistics Manager'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        GROUP BY u.name, p.partner_name, u.full_name, u.email, u.type, s.state_name;
    
    """



    capacity_and_building_manager = """
        SELECT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type AS "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            s.state_name AS "State",
            GROUP_CONCAT(DISTINCT d.district_name SEPARATOR ', ') AS "District",
            GROUP_CONCAT(DISTINCT b.block_name SEPARATOR ', ') AS "Block"
        FROM `tabUser` AS u
        LEFT JOIN `tabPartner` AS p ON p.name = u.partner
        LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
        LEFT JOIN `tabState` AS s ON s.name = ugm.state_id
        LEFT JOIN `tabDistrict` AS d ON ugm.district_id = d.name
        LEFT JOIN `tabBlock` AS b ON ugm.block_id = b.name
        WHERE u.type = 'Capacity and Building Manager'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        GROUP BY u.name, p.partner_name, u.full_name, u.email, u.type, s.state_name;
    
    """


    safety_coordinators = """
        SELECT DISTINCT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type as "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            s.state_name AS "State"
        FROM `tabUser` AS u
        INNER JOIN `tabPartner` AS p ON p.name = u.partner
        INNER JOIN `tabUser Geography Mapping` AS ugm  ON ugm.parent = u.name
        INNER JOIN `tabState` AS s ON s.name = ugm.state_id
        WHERE u.type = 'Safety Coordinator'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        ;
    
    """


    mis_coordinators = """
        SELECT DISTINCT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type as "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            s.state_name AS "State"
        FROM `tabUser` AS u
        INNER JOIN `tabPartner` AS p ON p.name = u.partner
        INNER JOIN `tabUser Geography Mapping` AS ugm  ON ugm.parent = u.name
        INNER JOIN `tabState` AS s ON s.name = ugm.state_id
        WHERE u.type = 'MIS Manager'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        ;
    
    """

    me_managers = """
        SELECT 
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type as "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            GROUP_CONCAT(DISTINCT s.state_name SEPARATOR ', ') AS "State"
        FROM `tabUser` AS u
        LEFT JOIN `tabPartner` AS p ON p.name = u.partner
        LEFT JOIN `tabUser Geography Mapping` AS ugm  ON ugm.parent = u.name
        LEFT JOIN `tabState` AS s ON s.name = ugm.state_id
        WHERE u.type = 'M&E Manager'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        GROUP BY 
            u.name, p.partner_name, u.full_name, u.email, u.type, u.enabled, u.date_of_joining, u.date_of_leaving
        ;
    """



    creche_supervisors = """
        SELECT
            p.partner_name AS "Partner",
            u.full_name AS "Username",
            u.email AS "Email",
            u.type AS "Role",
            CASE WHEN u.enabled = 1 THEN 'Active' ELSE 'Inactive' END AS "Is Active",
            u.date_of_joining AS "Date of Joining",
            u.date_of_leaving AS "Date of Leaving",
            s.state_name AS "State",
            GROUP_CONCAT(DISTINCT d.district_name SEPARATOR ', ') AS "District",
            GROUP_CONCAT(DISTINCT b.block_name SEPARATOR ', ') AS "Block",
            GROUP_CONCAT(DISTINCT g.gp_name SEPARATOR ', ') AS "Gram Panchayat"
        FROM `tabUser` AS u
        LEFT JOIN `tabPartner` AS p ON p.name = u.partner
        LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
        LEFT JOIN `tabState` AS s ON s.name = ugm.state_id
        LEFT JOIN `tabDistrict` AS d ON ugm.district_id = d.name
        LEFT JOIN `tabBlock` AS b ON ugm.block_id = b.name
        LEFT JOIN `tabGram Panchayat` AS g ON ugm.gp_id = g.name
        WHERE u.type = 'Creche Supervisor'
        AND (%(is_active)s = '2' OR u.enabled = 1)
        AND (%(partner_id)s IS NULL OR u.partner = %(partner_id)s)
        AND (
            (%(state_id)s IS NOT NULL AND ugm.state_id = %(state_id)s)
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(ugm.state_id,%(state_ids)s))
            OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
        )
        AND (
            (%(district_id)s IS NOT NULL AND ugm.district_id = %(district_id)s)
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(ugm.district_id,%(district_ids)s))
            OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
        )
        AND (
            (%(block_id)s IS NOT NULL AND ugm.block_id = %(block_id)s)
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(ugm.block_id,%(block_ids)s))
            OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
        )
        AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        GROUP BY u.name, p.partner_name, u.full_name, u.email, u.type, s.state_name;
    
    """


    creche_caregivers = """
        SELECT
            b.block_name AS "Block Name",
            c.creche_name AS "Creche Name",
            ccg.caregiver_code as 'Caregiver ID',
            ccg.caregiver_name as 'Caregiver Name',
            CASE WHEN ccg.is_active = 1 THEN 'Active' ELSE 'Inactive' END AS 'Is Active',
            ccg.date_of_joinning as 'Date of Joining',
            ccg.date_of_leaving as 'Date of Leaving',
            CASE
                WHEN ccg.reason_for_caregiver_exit = 1 THEN 'Permanent exit'
                WHEN ccg.reason_for_caregiver_exit = 2 THEN 'Maternity leave'
                WHEN ccg.reason_for_caregiver_exit = 3 THEN 'Illness'
                WHEN ccg.reason_for_caregiver_exit = 4 THEN 'Personal reasons'
            END AS 'Reason for Caregiver Exit'
        FROM `tabCreche Caregiver` ccg
        INNER JOIN `tabCreche` c ON c.name = ccg.parent
        LEFT JOIN `tabBlock` AS b ON b.name = c.block_id
        WHERE (%(is_active)s = '2' OR ccg.is_active = 1)
            AND (%(partner_id)s IS NULL OR c.partner_id = %(partner_id)s)
            AND (
                (%(state_id)s IS NOT NULL AND c.state_id = %(state_id)s)
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(c.state_id,%(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )
            AND (
                (%(district_id)s IS NOT NULL AND c.district_id = %(district_id)s)
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(c.district_id,%(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )
            AND (
                (%(block_id)s IS NOT NULL AND c.block_id = %(block_id)s)
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(c.block_id,%(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
        AND (ccg.date_of_joinning IS NULL OR ( %(end_date)s IS NOT NULL AND ccg.date_of_joinning <= %(end_date)s ))
        AND c.creche_status_id = 3;
    """





    if str(query_type) == "operational_creches":
        final_query = operational_creches
    elif str(query_type) == "states":
        final_query = states
    elif str(query_type) == "districts":
        final_query = districts
    elif str(query_type) == "blocks":
        final_query = blocks
    elif str(query_type) == "partners":
        final_query = partners
    elif str(query_type) == "program_managers":
        final_query = program_managers
    elif str(query_type) == "cluster_coordinators":
        final_query =   cluster_coordinators
    elif str(query_type) == "logistic_coordinators":
        final_query = logistic_coordinators
    elif str(query_type) == "capacity_and_building_manager":
        final_query = capacity_and_building_manager
    elif str(query_type) == "safety_coordinators":
        final_query = safety_coordinators
    elif str(query_type) == "mis_coordinators":
        final_query = mis_coordinators
    elif str(query_type) == "me_managers":
        final_query = me_managers
    elif str(query_type) == "creche_supervisors":
        final_query = creche_supervisors
    elif str(query_type) == "creche_caregivers":
        final_query = creche_caregivers


    else:
        frappe.response["Error"] = "Invalid query_type parameter"
        return
    
    result = frappe.db.sql(final_query, params, as_dict=True)
    frappe.response["data"] = result or []












