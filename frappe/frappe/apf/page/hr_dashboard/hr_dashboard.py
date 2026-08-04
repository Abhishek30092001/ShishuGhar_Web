import frappe
from datetime import date
import calendar


@frappe.whitelist()
def hr_dashboard(partner_id=None, state_id=None, district_id=None, block_id=None, gp_id=None, creche_id=None, year=None, month=None, cstart_date=None, cend_date=None, is_active=None):

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
        "is_active": is_active
    }
    

    query = """

    SELECT
        HR.operational_creches AS "Operational Creches",
        HR.partners AS "Partners",
        HR.states AS "States",
        HR.districts AS "Districts",
        HR.blocks AS "Blocks",
        HR.program_managers AS "Program Managers",
        HR.cluster_coordinators AS "Cluster Coordinators",
        HR.logistic_coordinators AS "Logistic Coordinators",
        HR.capacity_building_manager AS "Capacity and Building Manager",
        HR.safety_coordinators AS "Safety Coordinators",
        HR.mis_coordinators AS "MIS Coordinators",
        HR.me_managers AS "M&E Managers",
        HR.creche_supervisors AS "Creche Supervisors",
        HR.creche_caregivers AS "Creche Caregivers"

    FROM (

        SELECT

        /* Operational Creches */
        (
            SELECT COUNT(*)
            FROM `tabCreche` tc
            WHERE tc.creche_status_id = 3
            AND (%(partner_id)s IS NULL OR tc.partner_id = %(partner_id)s)

            AND (
                (%(state_id)s IS NOT NULL AND tc.state_id = %(state_id)s)
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(tc.state_id,%(state_ids)s))
                OR (%(state_id)s IS NULL AND %(state_ids)s IS NULL)
            )

            AND (
                (%(district_id)s IS NOT NULL AND tc.district_id = %(district_id)s)
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(tc.district_id,%(district_ids)s))
                OR (%(district_id)s IS NULL AND %(district_ids)s IS NULL)
            )

            AND (
                (%(block_id)s IS NOT NULL AND tc.block_id = %(block_id)s)
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(tc.block_id,%(block_ids)s))
                OR (%(block_id)s IS NULL AND %(block_ids)s IS NULL)
            )
            AND (tc.creche_opening_date IS NULL OR ( %(end_date)s IS NOT NULL AND tc.creche_opening_date <= %(end_date)s ))
            AND (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL OR (tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))
        ) AS operational_creches,


        /* Partners */
        (
            SELECT COUNT(DISTINCT  p.partner_name)
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
        ) AS partners,


        /* States */
        (
            SELECT COUNT(DISTINCT s.state_name)
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
        ) AS states,


        /* Districts */
        (
            SELECT COUNT(DISTINCT d.district_name)
            FROM `tabDistrict` AS d
            LEFT JOIN `tabCreche` AS c ON d.name = c.district_id
            WHERE d.is_active = 1
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
        ) AS districts,


        /* Blocks */
        (
            SELECT COUNT(DISTINCT b.block_name)
            FROM `tabBlock` AS b
            LEFT JOIN `tabCreche` AS c ON b.name = c.block_id
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
        ) AS blocks,


        /* Program Managers */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm 
                ON ugm.parent = u.name
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
        ) AS program_managers,


        /* Cluster Coordinators */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
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
            AND (u.date_of_joining IS NULL OR ( %(end_date)s IS NOT NULL AND u.date_of_joining <= %(end_date)s ))
        ) AS cluster_coordinators,


        /* Logistic Coordinators */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
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
        ) AS logistic_coordinators,


        /* Capacity and Building Manager */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm  ON ugm.parent = u.name
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
        ) AS capacity_building_manager,


        /* Safety Coordinators */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
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
        ) AS safety_coordinators,


        /* MIS Coordinators */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
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
        ) AS mis_coordinators,


        /* M&E Manager */
        (SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
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
        ) AS me_managers,


        /* Creche Supervisors */
        (
            SELECT COUNT(DISTINCT u.name)
            FROM `tabUser` AS u
            LEFT JOIN `tabUser Geography Mapping` AS ugm ON ugm.parent = u.name
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
        ) AS creche_supervisors,

        /* Creche Caregivers */
        (
            SELECT COUNT(*)
            FROM `tabCreche Caregiver` ccg
            INNER JOIN `tabCreche` c ON c.name = ccg.parent
            WHERE ccg.is_active = 1
            AND c.creche_status_id = 3
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
        ) AS creche_caregivers

    ) HR

    """

    data = frappe.db.sql(query, params, as_dict=True)
    result = data[0] if data else {}

    sections = {
        "data": [
            "Operational Creches",
            "States",
            "Partners",
            "Districts",
            "Blocks",
            "Program Managers",
            "Cluster Coordinators",
            "Logistic Coordinators",
            "Capacity and Building Manager",
            "Safety Coordinators",
            "MIS Coordinators",
            "M&E Managers",
            "Creche Supervisors",
            "Creche Caregivers"
        ]
    }

    transformed_data = {
        section: [
            {"title": field, "value": result.get(field, 0)}
            for field in fields
        ]
        for section, fields in sections.items()
    }

    frappe.response["data"] = transformed_data