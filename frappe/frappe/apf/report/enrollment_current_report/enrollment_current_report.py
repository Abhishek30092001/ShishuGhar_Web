import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):
    columns = get_columns(filters)
    data = get_report_data(filters)
    
    # Add total row based on selected level
    selected_level = filters.get("level", "7")
    data = add_total_row(data, selected_level)
    
    return columns, data

def get_columns(filters):
    """Define report columns based on level filter"""
    selected_level = filters.get("level", "7")
    variable_columns = []
    
    if selected_level == "1":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
    if selected_level == "2":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
    if selected_level == "3":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
    if selected_level == "4":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
    if selected_level == "5":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
    if selected_level == "7":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
        variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
    
    fixed_columns = [
        {"label": _("Operational Creches"), "fieldname": "op_creches", "fieldtype": "Int", "width": 200},
        # {"label": _("Population Q1(Jan-Mar)"), "fieldname": "population_q1", "fieldtype": "Int", "width": 220},
        # {"label": _("Population Q2(April-June)"), "fieldname": "population_q2", "fieldtype": "Int", "width": 220},
        # {"label": _("Population Q3(July-Sept)"), "fieldname": "population_q3", "fieldtype": "Int", "width": 220},
        # {"label": _("Population Q4(Oct-Dec)"), "fieldname": "population_q4", "fieldtype": "Int", "width": 220},
        {"label": _("Total No of Children (HH List)"), "fieldname": "total_children_hh", "fieldtype": "Int", "width": 230},
        {"label": _("No of Pregnant Women"), "fieldname": "pregnant_women", "fieldtype": "Int", "width": 200},
        {"label": _("(0-6) Months"), "fieldname": "children_0_6", "fieldtype": "Int", "width": 150},
        {"label": _("Current Eligible Children(6-36)"), "fieldname": "e_children", "fieldtype": "Int", "width": 230},
        {"label": _("Enrolled Children"), "fieldname": "new_enrollment", "fieldtype": "Int", "width": 200},
        {"label": _("Enrolled (%)"), "fieldname": "new_enrollment_percentage", "fieldtype": "float", "width": 110},
        {"label": _("Current Enrolled Children"), "fieldname": "currently_active", "fieldtype": "Int", "width": 200},
        {"label": _("Active (%)"), "fieldname": "currently_active_percentage", "fieldtype": "float", "width": 110},
        {"label": _("Total Exit (This Month)"), "fieldname": "new_exit", "fieldtype": "Int", "width": 200},
        {"label": _("Migrated (This Month)"), "fieldname": "reason_1", "fieldtype": "Int", "width": 190},
        {"label": _("Graduated (This Month)"), "fieldname": "reason_2", "fieldtype": "Int", "width": 190},
        {"label": _("Not Willing to Stay (This Month)"), "fieldname": "reason_3", "fieldtype": "Int", "width": 240},
        {"label": _("Death (This Month)"), "fieldname": "reason_4", "fieldtype": "Int", "width": 170},
        {"label": _("Other (This Month)"), "fieldname": "reason_5", "fieldtype": "Int", "width": 150},
        {"label": _("Not Enrolled (Migrated)"), "fieldname": "not_enrolled_migrated", "fieldtype": "Int", "width": 200},
        {"label": _("Not Enrolled (Death)"), "fieldname": "not_enrolled_death", "fieldtype": "Int", "width": 180},
        {"label": _("Not Enrolled (Out Side Catchment Area)"), "fieldname": "not_enrolled_outside", "fieldtype": "Int", "width": 300},
        {"label": _("Not Enrolled (Not willing to send)"), "fieldname": "not_willing_to_send", "fieldtype": "Int", "width": 300},
        {"label": _("Total Not Enrolled"), "fieldname": "total_not_enrolled", "fieldtype": "Int", "width": 150},
        {"label": _("To Be Enrolled"), "fieldname": "to_be_enrolled", "fieldtype": "Int", "width": 150},
        {"label": _("New Enrollment (This Month)"), "fieldname": "new_enrollment_data", "fieldtype": "Int", "width": 250},
    ]
    
    columns = variable_columns + fixed_columns
    return columns

def get_report_data(filters):
    """Get report data based on filters"""
    
    # Date range logic
    start_date, end_date = get_date_range(filters)
    
    # Build conditions and parameters
    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": filters.get("year") 
    }
    
    # Apply user geography restrictions
    apply_user_geography_filters(conditions, params, filters)
    
    # Apply other filters
    apply_other_filters(conditions, params, filters)
    
    # Apply creche opening date filters
    apply_creche_opening_filters(conditions, params, filters)
    
    # Build and execute query
    query = build_query(conditions, filters)
    data = frappe.db.sql(query, params, as_dict=True)
    
    return data

def get_date_range(filters):
    """Get date range from filters"""
    start_date, end_date = None, None
    
    if filters.get("time_range"):
        time_range = filters.get("time_range")
        if time_range and len(time_range) == 2:
            start_date, end_date = time_range
    elif filters.get("year") and filters.get("month"):
        current_date = date.today()
        month = int(filters.get("month")) if filters.get("month") else current_date.month
        year = int(filters.get("year")) if filters.get("year") else current_date.year
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
    
    return start_date, end_date

def apply_user_geography_filters(conditions, params, filters):
    """Apply user geography mapping filters"""
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    # Get user's geography mapping
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
    # Build comma-separated strings for FIND_IN_SET
    state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
    district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
    block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
    gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    
    # Apply partner filter if specified
    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        params["partner"] = partner_id
    
    # Apply geography filters if not overridden by user selection
    if not filters.get("state") and state_ids:
        conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
        params["state_ids"] = state_ids
    
    if not filters.get("district") and district_ids:
        conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
        params["district_ids"] = district_ids
    
    if not filters.get("block") and block_ids:
        conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
        params["block_ids"] = block_ids
    
    if not filters.get("gp") and gp_ids:
        conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
        params["gp_ids"] = gp_ids

def apply_other_filters(conditions, params, filters):
    """Apply other standard filters"""
    
    # Geography filters (overrides user mapping if specified)
    if filters.get("state"):
        conditions.append("c.state_id = %(state)s")
        params["state"] = filters.get("state")
    
    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        params["district"] = filters.get("district")
    
    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        params["block"] = filters.get("block")
    
    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    
    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
        params["creche"] = filters.get("creche")
    
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")
    
    if filters.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
        if phases_cleaned:
            conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
            params["phases"] = phases_cleaned

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

def apply_creche_opening_filters(conditions, params, filters):
    """Apply creche opening date filters"""
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None
    
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")
        
        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
        elif range_type == "before" and single_date:
            cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            cstart_date, cend_date = single_date + timedelta(days=1), date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date
        
        if cstart_date or cend_date:
            conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
            params["cstart_date"] = cstart_date if cstart_date else None
            params["cend_date"] = cend_date if cend_date else None

def build_query(conditions, filters):
    """Build the main SQL query with level-based grouping"""
    where_clause = " AND ".join(conditions)
    
    # Define level mapping for GROUP BY and SELECT
    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
    }
    
    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)
    
    # Build SELECT fields based on level
    select_fields_map = {
        "partner": "p.partner_name AS partner",
        "state": "s.state_name AS state",
        "district": "d.district_name AS district",
        "block": "b.block_name AS block",
        "supervisor": "u.full_name AS supervisor",
        "gp": "g.gp_name AS gp",
        "creche": "c.creche_name AS creche",
        "creche_id": "c.creche_id AS creche_id"
    }
    
    # Determine which fields to include based on selected level
    selected_fields = []
    if selected_level == "1":
        selected_fields.append(select_fields_map["partner"])
    if selected_level in ["2", "3", "4", "5", "6", "7"]:
        selected_fields.append(select_fields_map["state"])
    if selected_level in ["3", "4", "5", "6", "7"]:
        selected_fields.append(select_fields_map["district"])
    if selected_level in ["4", "5", "6", "7"]:
        selected_fields.append(select_fields_map["block"])
    if selected_level in ["5", "7"]:
        selected_fields.append(select_fields_map["supervisor"])
    if selected_level in ["6", "7"]:
        selected_fields.append(select_fields_map["gp"])
    if selected_level == "7":
        selected_fields.append(select_fields_map["creche"])
        selected_fields.append(select_fields_map["creche_id"])
        selected_fields.append("DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date")
    
    query = f"""
        SELECT
            {', '.join(selected_fields)},
            COALESCE(SUM(hh_counts.total_children_hh), 0) AS total_children_hh,
            COALESCE(SUM(nwcuenroll.new_enrollment), 0) AS new_enrollment,
            COALESCE(SUM(nwcuenroll_data.new_enrollment_data), 0) AS new_enrollment_data,
            COALESCE(SUM(cuenroll.currently_active), 0) AS currently_active,
            COALESCE(SUM(hh_counts.pregnant_women), 0) AS pregnant_women,
            COALESCE(SUM(nwexit.new_exit), 0) AS new_exit,
            COALESCE(SUM(rext.reason_1), 0) AS reason_1,
            COALESCE(SUM(rext.reason_2), 0) AS reason_2,
            COALESCE(SUM(rext.reason_3), 0) AS reason_3,
            COALESCE(SUM(rext.reason_4), 0) AS reason_4,
            COALESCE(SUM(rext.reason_5), 0) AS reason_5,
            COALESCE(SUM(c06.children_0_6), 0) AS children_0_6,
            COALESCE(SUM(ec.e_children), 0) AS e_children,
            COALESCE(COUNT(*), 0) AS op_creches,
            COALESCE(SUM(not_enrolled_counts.not_enrolled_migrated), 0) AS not_enrolled_migrated,
            COALESCE(SUM(not_enrolled_counts.not_enrolled_death), 0) AS not_enrolled_death,
            COALESCE(SUM(not_enrolled_counts.not_enrolled_outside), 0) AS not_enrolled_outside,
            COALESCE(SUM(not_enrolled_counts.not_willing_to_send), 0) AS not_willing_to_send,
            (COALESCE(SUM(ec.e_children), 0) - COALESCE(SUM(cuenroll.currently_active), 0)) AS to_be_enrolled,
            COALESCE(SUM(demo_counts.population_q1), 0) AS population_q1,
            COALESCE(SUM(demo_counts.population_q2), 0) AS population_q2,
            COALESCE(SUM(demo_counts.population_q3), 0) AS population_q3,
            COALESCE(SUM(demo_counts.population_q4), 0) AS population_q4,
            (COALESCE(SUM(not_enrolled_counts.not_enrolled_migrated),0)+COALESCE(SUM(not_enrolled_counts.not_enrolled_death),0)+COALESCE(SUM(not_enrolled_counts.not_enrolled_outside),0)+COALESCE(SUM(tobe_counts.to_be_enrolled),0)) AS total_not_enrolled,
            CASE WHEN SUM(ec.e_children)=0 THEN '0%%' ELSE CONCAT(FORMAT((SUM(nwcuenroll.new_enrollment)/SUM(ec.e_children))*100,2),'%%') END AS new_enrollment_percentage,
            CASE WHEN SUM(ec.e_children)=0 THEN '0%%' ELSE CONCAT(FORMAT((SUM(cuenroll.currently_active)/SUM(ec.e_children))*100,2),'%%') END AS currently_active_percentage
        FROM `tabCreche` c
        INNER JOIN `tabState` s ON c.state_id = s.name
        INNER JOIN `tabDistrict` d ON c.district_id = d.name
        INNER JOIN `tabBlock` b ON c.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        INNER JOIN `tabVillage` cc ON cc.name = c.village_id
        INNER JOIN `tabUser` u ON u.name = c.supervisor_id
        INNER JOIN `tabPartner` p ON c.partner_id = p.name
        LEFT JOIN (
            SELECT 
                hf.creche_id,
                COUNT(DISTINCT hc.name) AS total_children_hh,
                SUM(CASE WHEN hf.no_of_pregnant_women IS NOT NULL THEN hf.no_of_pregnant_women ELSE 0 END) AS pregnant_women
            FROM `tabHousehold Child Form` hc
            INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
            WHERE hc.is_dob_available = 1 
            GROUP BY hf.creche_id
        ) AS hh_counts ON hh_counts.creche_id = c.name

        LEFT JOIN (
            SELECT 
                hf.creche_id,
                COUNT(*) AS children_0_6
            FROM `tabHousehold Child Form` hc
            INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
            WHERE hc.is_dob_available = 1
            AND (hc.child_status IS NULL OR TRIM(hc.child_status) = '')
            AND hc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
            GROUP BY hf.creche_id
        ) AS c06 ON c06.creche_id = c.name


        LEFT JOIN (
            SELECT creche_id, 
                   SUM(CASE WHEN date_of_exit IS NULL OR date_of_exit > %(end_date)s THEN 1 ELSE 0 END) AS currently_active
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_enrollment <= %(end_date)s
            GROUP BY creche_id
        ) AS cuenroll ON cuenroll.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS new_enrollment
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_enrollment <= %(end_date)s 
            AND (date_of_exit IS NULL OR date_of_exit >= %(start_date)s)
            GROUP BY creche_id
        ) AS nwcuenroll ON nwcuenroll.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id, COUNT(*) AS new_enrollment_data
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_enrollment BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY creche_id
        ) AS nwcuenroll_data ON nwcuenroll_data.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id,
                   SUM(CASE WHEN date_of_exit IS NOT NULL THEN 1 ELSE 0 END) AS new_exit
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_exit BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY creche_id
        ) AS nwexit ON nwexit.creche_id = c.name
        LEFT JOIN (
            SELECT creche_id,
                   SUM(CASE WHEN reason_for_exit = 1 THEN 1 ELSE 0 END) AS reason_1,
                   SUM(CASE WHEN reason_for_exit = 2 THEN 1 ELSE 0 END) AS reason_2,
                   SUM(CASE WHEN reason_for_exit = 3 THEN 1 ELSE 0 END) AS reason_3,
                   SUM(CASE WHEN reason_for_exit = 4 THEN 1 ELSE 0 END) AS reason_4,
                   SUM(CASE WHEN reason_for_exit = 5 THEN 1 ELSE 0 END) AS reason_5
            FROM `tabChild Enrollment and Exit`
            WHERE date_of_exit BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY creche_id
        ) AS rext ON rext.creche_id = c.name
        LEFT JOIN (
            SELECT hf.creche_id, COUNT(hhc.hhcguid) AS e_children
            FROM `tabHousehold Child Form` AS hhc 
            JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
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
            GROUP BY hf.creche_id
        ) AS ec ON ec.creche_id = c.name
        LEFT JOIN (
            SELECT 
                hf.creche_id,
                SUM(CASE 
                    WHEN hhc.is_dob_available = 1 
                    AND hhc.child_status = 2
                    AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
                    AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
                    THEN 1 ELSE 0 
                END) AS not_enrolled_migrated,
                SUM(CASE 
                    WHEN hhc.is_dob_available = 1 
                    AND hhc.child_status = 1
                    AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
                    AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
                    THEN 1 ELSE 0 
                END) AS not_enrolled_death,
                SUM(CASE 
                    WHEN hhc.is_dob_available = 1 
                    AND hhc.child_status = 3
                    AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
                    AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
                    THEN 1 ELSE 0 
                END) AS not_enrolled_outside,
                SUM(CASE 
                    WHEN hhc.is_dob_available = 1 
                    AND hhc.child_status = 4
                    AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
                    AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
                    THEN 1 ELSE 0 
                END) AS not_willing_to_send
            FROM `tabHousehold Child Form` hhc
            INNER JOIN `tabHousehold Form` hf ON hf.name = hhc.parent
            WHERE hhc.is_dob_available = 1 
            AND hhc.child_status IN (1, 2, 3)
            GROUP BY hf.creche_id
        ) AS not_enrolled_counts ON not_enrolled_counts.creche_id = c.name
        LEFT JOIN (
            SELECT 
                hf.creche_id,
                COUNT(DISTINCT hcf.hhcguid) AS to_be_enrolled
            FROM `tabHousehold Child Form` hcf
            INNER JOIN `tabHousehold Form` hf ON hf.name = hcf.parent
            LEFT JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid = hcf.hhcguid
            LEFT JOIN `tabCreche` cr ON cr.name = hf.creche_id
            WHERE cee.hhcguid IS NULL
            AND (hcf.child_status IS NULL OR TRIM(hcf.child_status) = '')
            AND hcf.is_dob_available = 1
            AND (
                hcf.child_dob BETWEEN 
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
            AND (%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)
            GROUP BY hf.creche_id
        ) AS tobe_counts ON tobe_counts.creche_id = c.name
        LEFT JOIN (
            SELECT 
                v.name AS village_id,
                COALESCE(SUM(dd.population_q1), 0) AS population_q1,
                COALESCE(SUM(dd.population_q2), 0) AS population_q2,
                COALESCE(SUM(dd.population_q3), 0) AS population_q3,
                COALESCE(SUM(dd.population_q4), 0) AS population_q4
            FROM `tabDemographic Details` dd
            INNER JOIN `tabVillage` v ON dd.parent = v.name
            WHERE dd.year_id = CASE 
                WHEN %(year)s = 2027 THEN 8
                WHEN %(year)s = 2026 THEN 7
                WHEN %(year)s = 2025 THEN 6
                WHEN %(year)s = 2024 THEN 5
                WHEN %(year)s = 2023 THEN 4
                WHEN %(year)s = 2022 THEN 3
                WHEN %(year)s = 2021 THEN 2
                WHEN %(year)s = 2020 THEN 1
                ELSE NULL
            END
            GROUP BY v.name
        ) AS demo_counts ON demo_counts.village_id = c.village_id
        WHERE {where_clause}
        AND (c.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s))
        GROUP BY {group_by_field}
        ORDER BY {group_by_field}
    """
    
    return query

def add_total_row(data, selected_level):
    if not data:
        return data
    numeric_fields = [
        "op_creches",
        "population_q1", "population_q2", "population_q3", "population_q4",
        "total_children_hh",
        "pregnant_women",
        "children_0_6",
        "e_children",
        "new_enrollment",
        "new_enrollment_data",
        "currently_active",
        "new_exit",
        "reason_1", "reason_2", "reason_3", "reason_4", "reason_5",
        "total_exits",
        "not_enrolled_migrated",
        "not_enrolled_death",
        "not_enrolled_outside",
        "total_not_enrolled",
        "to_be_enrolled"
    ]
    total_row = {}
    # Set identifier column based on level
    level_labels = {
        "1": "partner",
        "2": "state", 
        "3": "district",
        "4": "block",
        "5": "supervisor",
        "6": "gp",
        "7": "state"
    }
    label_field = level_labels.get(selected_level, "state")
    total_row[label_field] = "<b>Total</b>"
    if data:
        for column in data[0].keys():
            if column not in total_row:
                if column in ["creche_id", "creche_opening_date", "creche", "district", "block", "gp", "supervisor", "partner"]:
                    total_row[column] = ""
                else:
                    total_row[column] = None
    # Sum numeric fields
    for field in numeric_fields:
        if field in total_row:
            total_row[field] = sum((row.get(field) or 0) for row in data if field in row)
    # Calculate and format percentages to match main query format
    if total_row.get("e_children", 0) > 0:
        enrollment_pct = (total_row.get("new_enrollment", 0) / total_row["e_children"]) * 100
        active_pct = (total_row.get("currently_active", 0) / total_row["e_children"]) * 100
        # Format to match the SQL query: "12.34%"
        total_row["new_enrollment_percentage"] = f"{enrollment_pct:.2f}%"
        total_row["currently_active_percentage"] = f"{active_pct:.2f}%"
    else:
        total_row["new_enrollment_percentage"] = "0%"
        total_row["currently_active_percentage"] = "0%"
    # Also recalculate derived totals
    total_row["total_exits"] = (
        (total_row.get("reason_1", 0) or 0) +
        (total_row.get("reason_2", 0) or 0) +
        (total_row.get("reason_3", 0) or 0) +
        (total_row.get("reason_4", 0) or 0) +
        (total_row.get("reason_5", 0) or 0)
    )
    total_row["total_not_enrolled"] = (
        (total_row.get("not_enrolled_migrated", 0) or 0) +
        (total_row.get("not_enrolled_death", 0) or 0) +
        (total_row.get("not_enrolled_outside", 0) or 0) +
        (total_row.get("to_be_enrolled", 0) or 0)
    )
    data.append(total_row)
    return data











# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_report_data(filters)
    
#     # Add total row based on selected level
#     selected_level = filters.get("level", "7")
#     data = add_total_row(data, selected_level)
    
#     return columns, data

# def get_columns(filters):
#     """Define report columns based on level filter"""
#     selected_level = filters.get("level", "7")
#     variable_columns = []
    
#     if selected_level == "1":
#         variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
#     if selected_level == "2":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#     if selected_level == "3":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#     if selected_level == "4":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#     if selected_level == "5":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#     if selected_level == "6":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#     if selected_level == "7":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
    
#     fixed_columns = [
#         {"label": _("Operational Creches"), "fieldname": "op_creches", "fieldtype": "Int", "width": 200},
#         # {"label": _("Population Q1(Jan-Mar)"), "fieldname": "population_q1", "fieldtype": "Int", "width": 220},
#         # {"label": _("Population Q2(April-June)"), "fieldname": "population_q2", "fieldtype": "Int", "width": 220},
#         # {"label": _("Population Q3(July-Sept)"), "fieldname": "population_q3", "fieldtype": "Int", "width": 220},
#         # {"label": _("Population Q4(Oct-Dec)"), "fieldname": "population_q4", "fieldtype": "Int", "width": 220},
#         {"label": _("Total No of Children (HH List)"), "fieldname": "total_children_hh", "fieldtype": "Int", "width": 230},
#         {"label": _("No of Pregnant Women"), "fieldname": "pregnant_women", "fieldtype": "Int", "width": 200},
#         {"label": _("(0-6) Months"), "fieldname": "children_0_6", "fieldtype": "Int", "width": 150},
#         {"label": _("Current Eligible Children(6-36)"), "fieldname": "e_children", "fieldtype": "Int", "width": 230},
#         {"label": _("Enrolled Children"), "fieldname": "new_enrollment", "fieldtype": "Int", "width": 200},
#         {"label": _("Enrolled (%)"), "fieldname": "new_enrollment_percentage", "fieldtype": "float", "width": 110},
#         {"label": _("Current Enrolled Children"), "fieldname": "currently_active", "fieldtype": "Int", "width": 200},
#         {"label": _("Active (%)"), "fieldname": "currently_active_percentage", "fieldtype": "float", "width": 110},
#         {"label": _("Total Exit (This Month)"), "fieldname": "new_exit", "fieldtype": "Int", "width": 200},
#         {"label": _("Migrated (This Month)"), "fieldname": "reason_1", "fieldtype": "Int", "width": 190},
#         {"label": _("Graduated (This Month)"), "fieldname": "reason_2", "fieldtype": "Int", "width": 190},
#         {"label": _("Not Willing to Stay (This Month)"), "fieldname": "reason_3", "fieldtype": "Int", "width": 240},
#         {"label": _("Death (This Month)"), "fieldname": "reason_4", "fieldtype": "Int", "width": 170},
#         {"label": _("Other (This Month)"), "fieldname": "reason_5", "fieldtype": "Int", "width": 150},
#         {"label": _("Not Enrolled (Migrated)"), "fieldname": "not_enrolled_migrated", "fieldtype": "Int", "width": 200},
#         {"label": _("Not Enrolled (Death)"), "fieldname": "not_enrolled_death", "fieldtype": "Int", "width": 180},
#         {"label": _("Not Enrolled (Out Side Catchment Area)"), "fieldname": "not_enrolled_outside", "fieldtype": "Int", "width": 300},
#         {"label": _("Total Not Enrolled"), "fieldname": "total_not_enrolled", "fieldtype": "Int", "width": 150},
#         {"label": _("To Be Enrolled"), "fieldname": "to_be_enrolled", "fieldtype": "Int", "width": 150},
#         {"label": _("New Enrollment (This Month)"), "fieldname": "new_enrollment_data", "fieldtype": "Int", "width": 250},
#     ]
    
#     columns = variable_columns + fixed_columns
#     return columns

# def get_report_data(filters):
#     """Get report data based on filters"""
    
#     # Date range logic
#     start_date, end_date = get_date_range(filters)
    
#     # Build conditions and parameters
#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": filters.get("year") 
#     }
    
#     # Apply user geography restrictions
#     apply_user_geography_filters(conditions, params, filters)
    
#     # Apply other filters
#     apply_other_filters(conditions, params, filters)
    
#     # Apply creche opening date filters
#     apply_creche_opening_filters(conditions, params, filters)
    
#     # Build and execute query
#     query = build_query(conditions, filters)
#     data = frappe.db.sql(query, params, as_dict=True)
    
#     return data

# def get_date_range(filters):
#     """Get date range from filters"""
#     start_date, end_date = None, None
    
#     if filters.get("time_range"):
#         time_range = filters.get("time_range")
#         if time_range and len(time_range) == 2:
#             start_date, end_date = time_range
#     elif filters.get("year") and filters.get("month"):
#         current_date = date.today()
#         month = int(filters.get("month")) if filters.get("month") else current_date.month
#         year = int(filters.get("year")) if filters.get("year") else current_date.year
#         start_date = date(year, month, 1)
#         last_day = calendar.monthrange(year, month)[1]
#         end_date = date(year, month, last_day)
    
#     return start_date, end_date

# def apply_user_geography_filters(conditions, params, filters):
#     """Apply user geography mapping filters"""
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner
    
#     # Get user's geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
#     # Build comma-separated strings for FIND_IN_SET
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    
#     # Apply partner filter if specified
#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     # Apply geography filters if not overridden by user selection
#     if not filters.get("state") and state_ids:
#         conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#         params["state_ids"] = state_ids
    
#     if not filters.get("district") and district_ids:
#         conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#         params["district_ids"] = district_ids
    
#     if not filters.get("block") and block_ids:
#         conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#         params["block_ids"] = block_ids
    
#     if not filters.get("gp") and gp_ids:
#         conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#         params["gp_ids"] = gp_ids

# def apply_other_filters(conditions, params, filters):
#     """Apply other standard filters"""
    
#     # Geography filters (overrides user mapping if specified)
#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
    
#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
    
#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
    
#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
    
#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if phases_cleaned:
#             conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#             params["phases"] = phases_cleaned

#     creche_age = filters.get("creche_age", "")
#     params["creche_age"] = creche_age
#     if creche_age:
#         conditions.append("""
#             CASE
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)

# def apply_creche_opening_filters(conditions, params, filters):
#     """Apply creche opening date filters"""
#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None
    
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")
        
#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range
#         elif range_type == "before" and single_date:
#             cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             cstart_date, cend_date = single_date + timedelta(days=1), date.today()
#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date
        
#         if cstart_date or cend_date:
#             conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
#             params["cstart_date"] = cstart_date if cstart_date else None
#             params["cend_date"] = cend_date if cend_date else None

# def build_query(conditions, filters):
#     """Build the main SQL query with level-based grouping"""
#     where_clause = " AND ".join(conditions)
    
#     # Define level mapping for GROUP BY and SELECT
#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }
    
#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)
    
#     # Build SELECT fields based on level
#     select_fields_map = {
#         "partner": "p.partner_name AS partner",
#         "state": "s.state_name AS state",
#         "district": "d.district_name AS district",
#         "block": "b.block_name AS block",
#         "supervisor": "u.full_name AS supervisor",
#         "gp": "g.gp_name AS gp",
#         "creche": "c.creche_name AS creche",
#         "creche_id": "c.creche_id AS creche_id"
#     }
    
#     # Determine which fields to include based on selected level
#     selected_fields = []
#     if selected_level == "1":
#         selected_fields.append(select_fields_map["partner"])
#     if selected_level in ["2", "3", "4", "5", "6", "7"]:
#         selected_fields.append(select_fields_map["state"])
#     if selected_level in ["3", "4", "5", "6", "7"]:
#         selected_fields.append(select_fields_map["district"])
#     if selected_level in ["4", "5", "6", "7"]:
#         selected_fields.append(select_fields_map["block"])
#     if selected_level in ["5", "7"]:
#         selected_fields.append(select_fields_map["supervisor"])
#     if selected_level in ["6", "7"]:
#         selected_fields.append(select_fields_map["gp"])
#     if selected_level == "7":
#         selected_fields.append(select_fields_map["creche"])
#         selected_fields.append(select_fields_map["creche_id"])
#         selected_fields.append("DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date")
    
#     query = f"""
#         SELECT
#             {', '.join(selected_fields)},
#             COALESCE(SUM(hh_counts.total_children_hh), 0) AS total_children_hh,
#             COALESCE(SUM(nwcuenroll.new_enrollment), 0) AS new_enrollment,
#             COALESCE(SUM(nwcuenroll_data.new_enrollment_data), 0) AS new_enrollment_data,
#             COALESCE(SUM(cuenroll.currently_active), 0) AS currently_active,
#             COALESCE(SUM(hh_counts.pregnant_women), 0) AS pregnant_women,
#             COALESCE(SUM(nwexit.new_exit), 0) AS new_exit,
#             COALESCE(SUM(rext.reason_1), 0) AS reason_1,
#             COALESCE(SUM(rext.reason_2), 0) AS reason_2,
#             COALESCE(SUM(rext.reason_3), 0) AS reason_3,
#             COALESCE(SUM(rext.reason_4), 0) AS reason_4,
#             COALESCE(SUM(rext.reason_5), 0) AS reason_5,
#             COALESCE(SUM(c06.children_0_6), 0) AS children_0_6,
#             COALESCE(SUM(ec.e_children), 0) AS e_children,
#             COALESCE(COUNT(*), 0) AS op_creches,
#             COALESCE(SUM(not_enrolled_counts.not_enrolled_migrated), 0) AS not_enrolled_migrated,
#             COALESCE(SUM(not_enrolled_counts.not_enrolled_death), 0) AS not_enrolled_death,
#             COALESCE(SUM(not_enrolled_counts.not_enrolled_outside), 0) AS not_enrolled_outside,
#             COALESCE(SUM(tobe_counts.to_be_enrolled), 0) AS to_be_enrolled,
#             COALESCE(SUM(demo_counts.population_q1), 0) AS population_q1,
#             COALESCE(SUM(demo_counts.population_q2), 0) AS population_q2,
#             COALESCE(SUM(demo_counts.population_q3), 0) AS population_q3,
#             COALESCE(SUM(demo_counts.population_q4), 0) AS population_q4,
#             (COALESCE(SUM(not_enrolled_counts.not_enrolled_migrated),0)+COALESCE(SUM(not_enrolled_counts.not_enrolled_death),0)+COALESCE(SUM(not_enrolled_counts.not_enrolled_outside),0)+COALESCE(SUM(tobe_counts.to_be_enrolled),0)) AS total_not_enrolled,
#             CASE WHEN SUM(ec.e_children)=0 THEN '0%%' ELSE CONCAT(FORMAT((SUM(nwcuenroll.new_enrollment)/SUM(ec.e_children))*100,2),'%%') END AS new_enrollment_percentage,
#             CASE WHEN SUM(ec.e_children)=0 THEN '0%%' ELSE CONCAT(FORMAT((SUM(cuenroll.currently_active)/SUM(ec.e_children))*100,2),'%%') END AS currently_active_percentage
#         FROM `tabCreche` c
#         INNER JOIN `tabState` s ON c.state_id = s.name
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         INNER JOIN `tabVillage` cc ON cc.name = c.village_id
#         INNER JOIN `tabUser` u ON u.name = c.supervisor_id
#         INNER JOIN `tabPartner` p ON c.partner_id = p.name
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(DISTINCT hc.name) AS total_children_hh,
#                 SUM(CASE WHEN hf.no_of_pregnant_women IS NOT NULL THEN hf.no_of_pregnant_women ELSE 0 END) AS pregnant_women
#             FROM `tabHousehold Child Form` hc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
#             WHERE hc.is_dob_available = 1 
#             GROUP BY hf.creche_id
#         ) AS hh_counts ON hh_counts.creche_id = c.name

#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(*) AS children_0_6
#             FROM `tabHousehold Child Form` hc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
#             WHERE hc.is_dob_available = 1
#             AND (hc.child_status IS NULL OR TRIM(hc.child_status) = '')
#             AND hc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#             GROUP BY hf.creche_id
#         ) AS c06 ON c06.creche_id = c.name


#         LEFT JOIN (
#             SELECT creche_id, 
#                    SUM(CASE WHEN date_of_exit IS NULL OR date_of_exit > %(end_date)s THEN 1 ELSE 0 END) AS currently_active
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment <= %(end_date)s
#             GROUP BY creche_id
#         ) AS cuenroll ON cuenroll.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id, COUNT(*) AS new_enrollment
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment <= %(end_date)s 
#             AND (date_of_exit IS NULL OR date_of_exit >= %(start_date)s)
#             GROUP BY creche_id
#         ) AS nwcuenroll ON nwcuenroll.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id, COUNT(*) AS new_enrollment_data
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment BETWEEN %(start_date)s AND %(end_date)s
#             GROUP BY creche_id
#         ) AS nwcuenroll_data ON nwcuenroll_data.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id,
#                    SUM(CASE WHEN date_of_exit IS NOT NULL THEN 1 ELSE 0 END) AS new_exit
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_exit BETWEEN %(start_date)s AND %(end_date)s
#             GROUP BY creche_id
#         ) AS nwexit ON nwexit.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id,
#                    SUM(CASE WHEN reason_for_exit = 1 THEN 1 ELSE 0 END) AS reason_1,
#                    SUM(CASE WHEN reason_for_exit = 2 THEN 1 ELSE 0 END) AS reason_2,
#                    SUM(CASE WHEN reason_for_exit = 3 THEN 1 ELSE 0 END) AS reason_3,
#                    SUM(CASE WHEN reason_for_exit = 4 THEN 1 ELSE 0 END) AS reason_4,
#                    SUM(CASE WHEN reason_for_exit = 5 THEN 1 ELSE 0 END) AS reason_5
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_exit BETWEEN %(start_date)s AND %(end_date)s
#             GROUP BY creche_id
#         ) AS rext ON rext.creche_id = c.name
#         LEFT JOIN (
#             SELECT hf.creche_id, COUNT(hhc.hhcguid) AS e_children
#             FROM `tabHousehold Child Form` AS hhc 
#             JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
#             WHERE hhc.is_dob_available = 1 
#             AND (hhc.child_status IS NULL OR TRIM(hhc.child_status) = '')
#             AND (
#                 hhc.child_dob BETWEEN 
#                     DATE_SUB(
#                         IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
#                             CURDATE(), 
#                             %(end_date)s
#                         ), 
#                         INTERVAL 36 MONTH
#                     )
#                     AND 
#                     DATE_SUB(
#                         IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
#                             CURDATE(), 
#                             %(end_date)s
#                         ), 
#                         INTERVAL 6 MONTH
#                     )
#             )
#             GROUP BY hf.creche_id
#         ) AS ec ON ec.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 SUM(CASE 
#                     WHEN hhc.is_dob_available = 1 
#                     AND hhc.child_status = 2
#                     AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#                     AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#                     THEN 1 ELSE 0 
#                 END) AS not_enrolled_migrated,
#                 SUM(CASE 
#                     WHEN hhc.is_dob_available = 1 
#                     AND hhc.child_status = 1
#                     AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#                     AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#                     THEN 1 ELSE 0 
#                 END) AS not_enrolled_death,
#                 SUM(CASE 
#                     WHEN hhc.is_dob_available = 1 
#                     AND hhc.child_status = 3
#                     AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#                     AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#                     THEN 1 ELSE 0 
#                 END) AS not_enrolled_outside
#             FROM `tabHousehold Child Form` hhc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hhc.parent
#             WHERE hhc.is_dob_available = 1 
#             AND hhc.child_status IN (1, 2, 3)
#             GROUP BY hf.creche_id
#         ) AS not_enrolled_counts ON not_enrolled_counts.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(DISTINCT hcf.hhcguid) AS to_be_enrolled
#             FROM `tabHousehold Child Form` hcf
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hcf.parent
#             LEFT JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid = hcf.hhcguid
#             LEFT JOIN `tabCreche` cr ON cr.name = hf.creche_id
#             WHERE cee.hhcguid IS NULL
#             AND (hcf.child_status IS NULL OR TRIM(hcf.child_status) = '')
#             AND hcf.is_dob_available = 1
#             AND (
#                 hcf.child_dob BETWEEN 
#                     DATE_SUB(
#                         IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
#                             CURDATE(), 
#                             %(end_date)s
#                         ), 
#                         INTERVAL 36 MONTH
#                     )
#                     AND 
#                     DATE_SUB(
#                         IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
#                             CURDATE(), 
#                             %(end_date)s
#                         ), 
#                         INTERVAL 6 MONTH
#                     )
#             )
#             AND (%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)
#             GROUP BY hf.creche_id
#         ) AS tobe_counts ON tobe_counts.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 v.name AS village_id,
#                 COALESCE(SUM(dd.population_q1), 0) AS population_q1,
#                 COALESCE(SUM(dd.population_q2), 0) AS population_q2,
#                 COALESCE(SUM(dd.population_q3), 0) AS population_q3,
#                 COALESCE(SUM(dd.population_q4), 0) AS population_q4
#             FROM `tabDemographic Details` dd
#             INNER JOIN `tabVillage` v ON dd.parent = v.name
#             WHERE dd.year_id = CASE 
#                 WHEN %(year)s = 2027 THEN 8
#                 WHEN %(year)s = 2026 THEN 7
#                 WHEN %(year)s = 2025 THEN 6
#                 WHEN %(year)s = 2024 THEN 5
#                 WHEN %(year)s = 2023 THEN 4
#                 WHEN %(year)s = 2022 THEN 3
#                 WHEN %(year)s = 2021 THEN 2
#                 WHEN %(year)s = 2020 THEN 1
#                 ELSE NULL
#             END
#             GROUP BY v.name
#         ) AS demo_counts ON demo_counts.village_id = c.village_id
#         WHERE {where_clause}
#         AND (c.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s))
#         GROUP BY {group_by_field}
#         ORDER BY {group_by_field}
#     """
    
#     return query

# def add_total_row(data, selected_level):
#     if not data:
#         return data
#     numeric_fields = [
#         "op_creches",
#         "population_q1", "population_q2", "population_q3", "population_q4",
#         "total_children_hh",
#         "pregnant_women",
#         "children_0_6",
#         "e_children",
#         "new_enrollment",
#         "new_enrollment_data",
#         "currently_active",
#         "new_exit",
#         "reason_1", "reason_2", "reason_3", "reason_4", "reason_5",
#         "total_exits",
#         "not_enrolled_migrated",
#         "not_enrolled_death",
#         "not_enrolled_outside",
#         "total_not_enrolled",
#         "to_be_enrolled"
#     ]
#     total_row = {}
#     # Set identifier column based on level
#     level_labels = {
#         "1": "partner",
#         "2": "state", 
#         "3": "district",
#         "4": "block",
#         "5": "supervisor",
#         "6": "gp",
#         "7": "state"
#     }
#     label_field = level_labels.get(selected_level, "state")
#     total_row[label_field] = "<b>Total</b>"
#     if data:
#         for column in data[0].keys():
#             if column not in total_row:
#                 if column in ["creche_id", "creche_opening_date", "creche", "district", "block", "gp", "supervisor", "partner"]:
#                     total_row[column] = ""
#                 else:
#                     total_row[column] = None
#     # Sum numeric fields
#     for field in numeric_fields:
#         if field in total_row:
#             total_row[field] = sum((row.get(field) or 0) for row in data if field in row)
#     # Calculate and format percentages to match main query format
#     if total_row.get("e_children", 0) > 0:
#         enrollment_pct = (total_row.get("new_enrollment", 0) / total_row["e_children"]) * 100
#         active_pct = (total_row.get("currently_active", 0) / total_row["e_children"]) * 100
#         # Format to match the SQL query: "12.34%"
#         total_row["new_enrollment_percentage"] = f"{enrollment_pct:.2f}%"
#         total_row["currently_active_percentage"] = f"{active_pct:.2f}%"
#     else:
#         total_row["new_enrollment_percentage"] = "0%"
#         total_row["currently_active_percentage"] = "0%"
#     # Also recalculate derived totals
#     total_row["total_exits"] = (
#         (total_row.get("reason_1", 0) or 0) +
#         (total_row.get("reason_2", 0) or 0) +
#         (total_row.get("reason_3", 0) or 0) +
#         (total_row.get("reason_4", 0) or 0) +
#         (total_row.get("reason_5", 0) or 0)
#     )
#     total_row["total_not_enrolled"] = (
#         (total_row.get("not_enrolled_migrated", 0) or 0) +
#         (total_row.get("not_enrolled_death", 0) or 0) +
#         (total_row.get("not_enrolled_outside", 0) or 0) +
#         (total_row.get("to_be_enrolled", 0) or 0)
#     )
#     data.append(total_row)
#     return data



















# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar

# def execute(filters=None):
#     columns = get_columns(filters)
#     data = get_report_data(filters)
    
#     # Add total row based on selected level
#     selected_level = filters.get("level", "7")
#     data = add_total_row(data, selected_level)
    
#     return columns, data

# def get_columns(filters):
#     """Define report columns based on level filter"""
#     selected_level = filters.get("level", "7")
#     variable_columns = []
    
#     if selected_level == "1":
#         variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
#     if selected_level == "2":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#     if selected_level == "3":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#     if selected_level == "4":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#     if selected_level == "5":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#     if selected_level == "6":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#     if selected_level == "7":
#         variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
#         variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150})
#         variable_columns.append({"label": "Creche Opening Date", "fieldname": "creche_opening_date", "fieldtype": "Data", "width": 170})
    
#     fixed_columns = [
#         {"label": _("Operational Creches"), "fieldname": "op_creches", "fieldtype": "Int", "width": 200},
#         {"label": _("Population Q1 (Jan-Mar)"), "fieldname": "population_q1", "fieldtype": "Int", "width": 170},
#         {"label": _("Population Q2 (April-June)"), "fieldname": "population_q2", "fieldtype": "Int", "width": 170},
#         {"label": _("Population Q3 (July-Sept)"), "fieldname": "population_q3", "fieldtype": "Int", "width": 170},
#         {"label": _("Population Q4 (Oct-Dec)"), "fieldname": "population_q4", "fieldtype": "Int", "width": 170},
#         {"label": _("Total No of Children (HH List)"), "fieldname": "total_children_hh", "fieldtype": "Int", "width": 230},
#         {"label": _("No of Pregnant Women"), "fieldname": "pregnant_women", "fieldtype": "Int", "width": 200},
#         {"label": _("(0-6) Months"), "fieldname": "children_0_6", "fieldtype": "Int", "width": 150},
#         {"label": _("Current Eligible Children"), "fieldname": "e_children", "fieldtype": "Int", "width": 200},
#         {"label": _("Enrolled Children"), "fieldname": "new_enrollment", "fieldtype": "Int", "width": 200},
#         {"label": _("Enrolled (%)"), "fieldname": "new_enrollment_percentage", "fieldtype": "float", "width": 110},
#         {"label": _("Current Enrolled Children"), "fieldname": "currently_active", "fieldtype": "Int", "width": 200},
#         {"label": _("Active (%)"), "fieldname": "currently_active_percentage", "fieldtype": "float", "width": 110},
#         {"label": _("Total Exit (This Month)"), "fieldname": "new_exit", "fieldtype": "Int", "width": 200},
#         {"label": _("Migrated (This Month)"), "fieldname": "reason_1", "fieldtype": "Int", "width": 190},
#         {"label": _("Graduated (This Month)"), "fieldname": "reason_2", "fieldtype": "Int", "width": 190},
#         {"label": _("Not Willing to Stay (This Month)"), "fieldname": "reason_3", "fieldtype": "Int", "width": 240},
#         {"label": _("Death (This Month)"), "fieldname": "reason_4", "fieldtype": "Int", "width": 170},
#         {"label": _("Other (This Month)"), "fieldname": "reason_5", "fieldtype": "Int", "width": 150},
#         {"label": _("Not Enrolled (Migrated)"), "fieldname": "not_enrolled_migrated", "fieldtype": "Int", "width": 200},
#         {"label": _("Not Enrolled (Death)"), "fieldname": "not_enrolled_death", "fieldtype": "Int", "width": 180},
#         {"label": _("Not Enrolled (Out Side Catchment Area)"), "fieldname": "not_enrolled_outside", "fieldtype": "Int", "width": 300},
#         {"label": _("Total Not Enrolled"), "fieldname": "total_not_enrolled", "fieldtype": "Int", "width": 150},
#         {"label": _("To Be Enrolled"), "fieldname": "to_be_enrolled", "fieldtype": "Int", "width": 150}
#     ]
    
#     columns = variable_columns + fixed_columns
#     return columns

# def get_report_data(filters):
#     """Get report data based on filters"""
    
#     # Date range logic
#     start_date, end_date = get_date_range(filters)
    
#     # Build conditions and parameters
#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": filters.get("year") 
#     }
    
#     # Apply user geography restrictions
#     apply_user_geography_filters(conditions, params, filters)
    
#     # Apply other filters
#     apply_other_filters(conditions, params, filters)
    
#     # Apply creche opening date filters
#     apply_creche_opening_filters(conditions, params, filters)
    
#     # Build and execute query
#     query = build_query(conditions, filters)
#     data = frappe.db.sql(query, params, as_dict=True)
    
#     return data

# def get_date_range(filters):
#     """Get date range from filters"""
#     start_date, end_date = None, None
    
#     if filters.get("time_range"):
#         time_range = filters.get("time_range")
#         if time_range and len(time_range) == 2:
#             start_date, end_date = time_range
#     elif filters.get("year") and filters.get("month"):
#         current_date = date.today()
#         month = int(filters.get("month")) if filters.get("month") else current_date.month
#         year = int(filters.get("year")) if filters.get("year") else current_date.year
#         start_date = date(year, month, 1)
#         last_day = calendar.monthrange(year, month)[1]
#         end_date = date(year, month, last_day)
    
#     return start_date, end_date

# def apply_user_geography_filters(conditions, params, filters):
#     """Apply user geography mapping filters"""
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner
    
#     # Get user's geography mapping
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabState` ts 
#         JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
#         WHERE ugm.parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     state_params = (frappe.session.user,)
#     current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    
#     # Build comma-separated strings for FIND_IN_SET
#     state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#     district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#     block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#     gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
    
#     # Apply partner filter if specified
#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id
    
#     # Apply geography filters if not overridden by user selection
#     if not filters.get("state") and state_ids:
#         conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
#         params["state_ids"] = state_ids
    
#     if not filters.get("district") and district_ids:
#         conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
#         params["district_ids"] = district_ids
    
#     if not filters.get("block") and block_ids:
#         conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
#         params["block_ids"] = block_ids
    
#     if not filters.get("gp") and gp_ids:
#         conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
#         params["gp_ids"] = gp_ids

# def apply_other_filters(conditions, params, filters):
#     """Apply other standard filters"""
    
#     # Geography filters (overrides user mapping if specified)
#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
    
#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
    
#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
    
#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
    
#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")
    
#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")
    
#     if filters.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
    
#     if filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         if phases_cleaned:
#             conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#             params["phases"] = phases_cleaned

# def apply_creche_opening_filters(conditions, params, filters):
#     """Apply creche opening date filters"""
#     cstart_date, cend_date = None, None
#     range_type = filters.get("cr_opening_range_type") if filters.get("cr_opening_range_type") else None
    
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")
        
#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             cstart_date, cend_date = date_range
#         elif range_type == "before" and single_date:
#             cstart_date, cend_date = date(2017, 1, 1), single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             cstart_date, cend_date = single_date + timedelta(days=1), date.today()
#         elif range_type == "equal" and single_date:
#             cstart_date = cend_date = single_date
        
#         if cstart_date or cend_date:
#             conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")
#             params["cstart_date"] = cstart_date if cstart_date else None
#             params["cend_date"] = cend_date if cend_date else None

# def build_query(conditions, filters):
#     """Build the main SQL query with level-based grouping"""
#     where_clause = " AND ".join(conditions)
    
#     # Define level mapping for GROUP BY and SELECT
#     level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }
    
#     selected_level = filters.get("level", "7")
#     group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
#     group_by_field = ", ".join(group_by_fields)
    
#     # Build SELECT fields based on level
#     select_fields_map = {
#         "partner": "p.partner_name AS partner",
#         "state": "s.state_name AS state",
#         "district": "d.district_name AS district",
#         "block": "b.block_name AS block",
#         "supervisor": "u.full_name AS supervisor",
#         "gp": "g.gp_name AS gp",
#         "creche": "c.creche_name AS creche",
#         "creche_id": "c.creche_id AS creche_id"
#     }
    
#     # Determine which fields to include based on selected level
#     selected_fields = []
#     if selected_level == "1":
#         selected_fields.append(select_fields_map["partner"])
#     if selected_level in ["2", "3", "4", "5", "6", "7"]:
#         selected_fields.append(select_fields_map["state"])
#     if selected_level in ["3", "4", "5", "6", "7"]:
#         selected_fields.append(select_fields_map["district"])
#     if selected_level in ["4", "5", "6", "7"]:
#         selected_fields.append(select_fields_map["block"])
#     if selected_level in ["5", "7"]:
#         selected_fields.append(select_fields_map["supervisor"])
#     if selected_level in ["6", "7"]:
#         selected_fields.append(select_fields_map["gp"])
#     if selected_level == "7":
#         selected_fields.append(select_fields_map["creche"])
#         selected_fields.append(select_fields_map["creche_id"])
#         selected_fields.append("DATE_FORMAT(c.creche_opening_date, '%%d-%%m-%%Y') AS creche_opening_date")
    
#     query = f"""
#         SELECT
#             {', '.join(selected_fields)},
#             COALESCE(SUM(hh_counts.total_children_hh), 0) AS total_children_hh,
#             COALESCE(SUM(nwcuenroll.new_enrollment), 0) AS new_enrollment,
#             COALESCE(SUM(cuenroll.currently_active), 0) AS currently_active,
#             COALESCE(SUM(hh_counts.pregnant_women), 0) AS pregnant_women,
#             COALESCE(SUM(nwexit.new_exit), 0) AS new_exit,
#             COALESCE(SUM(rext.reason_1), 0) AS reason_1,
#             COALESCE(SUM(rext.reason_2), 0) AS reason_2,
#             COALESCE(SUM(rext.reason_3), 0) AS reason_3,
#             COALESCE(SUM(rext.reason_4), 0) AS reason_4,
#             COALESCE(SUM(rext.reason_5), 0) AS reason_5,
#             COALESCE(SUM(c06.children_0_6), 0) AS children_0_6,
#             COALESCE(SUM(ec.e_children), 0) AS e_children,
#             COALESCE(COUNT(*), 0) AS op_creches,
#             COALESCE(SUM(not_enrolled_counts.not_enrolled_migrated), 0) AS not_enrolled_migrated,
#             COALESCE(SUM(not_enrolled_counts.not_enrolled_death), 0) AS not_enrolled_death,
#             COALESCE(SUM(not_enrolled_counts.not_enrolled_outside), 0) AS not_enrolled_outside,
#             COALESCE(SUM(tobe_counts.to_be_enrolled), 0) AS to_be_enrolled,
#             COALESCE(SUM(demo_counts.population_q1), 0) AS population_q1,
#             COALESCE(SUM(demo_counts.population_q2), 0) AS population_q2,
#             COALESCE(SUM(demo_counts.population_q3), 0) AS population_q3,
#             COALESCE(SUM(demo_counts.population_q4), 0) AS population_q4,
#             (COALESCE(SUM(not_enrolled_counts.not_enrolled_migrated),0)+COALESCE(SUM(not_enrolled_counts.not_enrolled_death),0)+COALESCE(SUM(not_enrolled_counts.not_enrolled_outside),0)) AS total_not_enrolled,
#             CASE WHEN SUM(ec.e_children)=0 THEN '0%%' ELSE CONCAT(FORMAT((SUM(nwcuenroll.new_enrollment)/SUM(ec.e_children))*100,2),'%%') END AS new_enrollment_percentage,
#             CASE WHEN SUM(ec.e_children)=0 THEN '0%%' ELSE CONCAT(FORMAT((SUM(cuenroll.currently_active)/SUM(ec.e_children))*100,2),'%%') END AS currently_active_percentage
#         FROM `tabCreche` c
#         INNER JOIN `tabState` s ON c.state_id = s.name
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         INNER JOIN `tabVillage` cc ON cc.name = c.village_id
#         INNER JOIN `tabUser` u ON u.name = c.supervisor_id
#         INNER JOIN `tabPartner` p ON c.partner_id = p.name
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(DISTINCT hc.name) AS total_children_hh,
#                 SUM(CASE WHEN hf.no_of_pregnant_women IS NOT NULL THEN hf.no_of_pregnant_women ELSE 0 END) AS pregnant_women
#             FROM `tabHousehold Child Form` hc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
#             WHERE hc.is_dob_available = 1 
#             GROUP BY hf.creche_id
#         ) AS hh_counts ON hh_counts.creche_id = c.name

#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(*) AS children_0_6
#             FROM `tabHousehold Child Form` hc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hc.parent
#             WHERE hc.is_dob_available = 1
#             AND (hc.child_status IS NULL OR TRIM(hc.child_status) = '')
#             AND hc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#             GROUP BY hf.creche_id
#         ) AS c06 ON c06.creche_id = c.name


#         LEFT JOIN (
#             SELECT creche_id, 
#                    SUM(CASE WHEN date_of_exit IS NULL OR date_of_exit > %(end_date)s THEN 1 ELSE 0 END) AS currently_active
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment <= %(end_date)s
#             GROUP BY creche_id
#         ) AS cuenroll ON cuenroll.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id, COUNT(*) AS new_enrollment
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_enrollment <= %(end_date)s 
#             AND (date_of_exit IS NULL OR date_of_exit >= %(start_date)s)
#             GROUP BY creche_id
#         ) AS nwcuenroll ON nwcuenroll.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id,
#                    SUM(CASE WHEN date_of_exit IS NOT NULL THEN 1 ELSE 0 END) AS new_exit
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_exit BETWEEN %(start_date)s AND %(end_date)s
#             GROUP BY creche_id
#         ) AS nwexit ON nwexit.creche_id = c.name
#         LEFT JOIN (
#             SELECT creche_id,
#                    SUM(CASE WHEN reason_for_exit = 1 THEN 1 ELSE 0 END) AS reason_1,
#                    SUM(CASE WHEN reason_for_exit = 2 THEN 1 ELSE 0 END) AS reason_2,
#                    SUM(CASE WHEN reason_for_exit = 3 THEN 1 ELSE 0 END) AS reason_3,
#                    SUM(CASE WHEN reason_for_exit = 4 THEN 1 ELSE 0 END) AS reason_4,
#                    SUM(CASE WHEN reason_for_exit = 5 THEN 1 ELSE 0 END) AS reason_5
#             FROM `tabChild Enrollment and Exit`
#             WHERE date_of_exit BETWEEN %(start_date)s AND %(end_date)s
#             GROUP BY creche_id
#         ) AS rext ON rext.creche_id = c.name
#         LEFT JOIN (
#             SELECT hf.creche_id, COUNT(hhc.hhcguid) AS e_children
#             FROM `tabHousehold Child Form` AS hhc 
#             JOIN `tabHousehold Form` AS hf ON hf.name = hhc.parent
#             WHERE hhc.is_dob_available = 1 
#             AND (hhc.child_status IS NULL OR TRIM(hhc.child_status) = '')
#             AND (
#                 hhc.child_dob BETWEEN 
#                     DATE_SUB(
#                         IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
#                             CURDATE(), 
#                             %(end_date)s
#                         ), 
#                         INTERVAL 36 MONTH
#                     )
#                     AND 
#                     DATE_SUB(
#                         IF(DATE_FORMAT(%(end_date)s, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 
#                             CURDATE(), 
#                             %(end_date)s
#                         ), 
#                         INTERVAL 6 MONTH
#                     )
#             )
#             GROUP BY hf.creche_id
#         ) AS ec ON ec.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 SUM(CASE 
#                     WHEN hhc.is_dob_available = 1 
#                     AND hhc.child_status = 2
#                     AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#                     AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#                     THEN 1 ELSE 0 
#                 END) AS not_enrolled_migrated,
#                 SUM(CASE 
#                     WHEN hhc.is_dob_available = 1 
#                     AND hhc.child_status = 1
#                     AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#                     AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#                     THEN 1 ELSE 0 
#                 END) AS not_enrolled_death,
#                 SUM(CASE 
#                     WHEN hhc.is_dob_available = 1 
#                     AND hhc.child_status = 3
#                     AND hhc.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#                     AND hhc.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#                     THEN 1 ELSE 0 
#                 END) AS not_enrolled_outside
#             FROM `tabHousehold Child Form` hhc
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hhc.parent
#             WHERE hhc.is_dob_available = 1 
#             AND hhc.child_status IN (1, 2, 3)
#             GROUP BY hf.creche_id
#         ) AS not_enrolled_counts ON not_enrolled_counts.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 hf.creche_id,
#                 COUNT(DISTINCT hcf.hhcguid) AS to_be_enrolled
#             FROM `tabHousehold Child Form` hcf
#             INNER JOIN `tabHousehold Form` hf ON hf.name = hcf.parent
#             LEFT JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid = hcf.hhcguid
#             WHERE cee.hhcguid IS NULL
#             AND hcf.is_dob_available = 1
#             AND hcf.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)
#             AND hcf.child_dob > DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)
#             GROUP BY hf.creche_id
#         ) AS tobe_counts ON tobe_counts.creche_id = c.name
#         LEFT JOIN (
#             SELECT 
#                 v.name AS village_id,
#                 COALESCE(SUM(dd.population_q1), 0) AS population_q1,
#                 COALESCE(SUM(dd.population_q2), 0) AS population_q2,
#                 COALESCE(SUM(dd.population_q3), 0) AS population_q3,
#                 COALESCE(SUM(dd.population_q4), 0) AS population_q4
#             FROM `tabDemographic Details` dd
#             INNER JOIN `tabVillage` v ON dd.parent = v.name
#             WHERE dd.year_id = CASE 
#                 WHEN %(year)s = 2027 THEN 8
#                 WHEN %(year)s = 2026 THEN 7
#                 WHEN %(year)s = 2025 THEN 6
#                 WHEN %(year)s = 2024 THEN 5
#                 WHEN %(year)s = 2023 THEN 4
#                 WHEN %(year)s = 2022 THEN 3
#                 WHEN %(year)s = 2021 THEN 2
#                 WHEN %(year)s = 2020 THEN 1
#                 ELSE NULL
#             END
#             GROUP BY v.name
#         ) AS demo_counts ON demo_counts.village_id = c.village_id
#         WHERE {where_clause}
#         AND (c.creche_opening_date IS NULL OR (%(end_date)s IS NOT NULL AND c.creche_opening_date <= %(end_date)s))
#         GROUP BY {group_by_field}
#         ORDER BY {group_by_field}
#     """
    
#     return query

# def add_total_row(data, selected_level):
#     if not data:
#         return data
#     numeric_fields = [
#         "op_creches",
#         "population_q1", "population_q2", "population_q3", "population_q4",
#         "total_children_hh",
#         "pregnant_women",
#         "children_0_6",
#         "e_children",
#         "new_enrollment",
#         "currently_active",
#         "new_exit",
#         "reason_1", "reason_2", "reason_3", "reason_4", "reason_5",
#         "total_exits",
#         "not_enrolled_migrated",
#         "not_enrolled_death",
#         "not_enrolled_outside",
#         "total_not_enrolled",
#         "to_be_enrolled"
#     ]
#     total_row = {}
#     # Set identifier column based on level
#     level_labels = {
#         "1": "partner",
#         "2": "state", 
#         "3": "district",
#         "4": "block",
#         "5": "supervisor",
#         "6": "gp",
#         "7": "state"
#     }
#     label_field = level_labels.get(selected_level, "state")
#     total_row[label_field] = "<b>Total</b>"
#     if data:
#         for column in data[0].keys():
#             if column not in total_row:
#                 if column in ["creche_id", "creche_opening_date", "creche", "district", "block", "gp", "supervisor", "partner"]:
#                     total_row[column] = ""
#                 else:
#                     total_row[column] = None
#     # Sum numeric fields
#     for field in numeric_fields:
#         if field in total_row:
#             total_row[field] = sum((row.get(field) or 0) for row in data if field in row)
#     # Calculate and format percentages to match main query format
#     if total_row.get("e_children", 0) > 0:
#         enrollment_pct = (total_row.get("new_enrollment", 0) / total_row["e_children"]) * 100
#         active_pct = (total_row.get("currently_active", 0) / total_row["e_children"]) * 100
#         # Format to match the SQL query: "12.34%"
#         total_row["new_enrollment_percentage"] = f"{enrollment_pct:.2f}%"
#         total_row["currently_active_percentage"] = f"{active_pct:.2f}%"
#     else:
#         total_row["new_enrollment_percentage"] = "0%"
#         total_row["currently_active_percentage"] = "0%"
#     # Also recalculate derived totals
#     total_row["total_exits"] = (
#         (total_row.get("reason_1", 0) or 0) +
#         (total_row.get("reason_2", 0) or 0) +
#         (total_row.get("reason_3", 0) or 0) +
#         (total_row.get("reason_4", 0) or 0) +
#         (total_row.get("reason_5", 0) or 0)
#     )
#     total_row["total_not_enrolled"] = (
#         (total_row.get("not_enrolled_migrated", 0) or 0) +
#         (total_row.get("not_enrolled_death", 0) or 0) +
#         (total_row.get("not_enrolled_outside", 0) or 0)
#     )
#     data.append(total_row)
#     return data