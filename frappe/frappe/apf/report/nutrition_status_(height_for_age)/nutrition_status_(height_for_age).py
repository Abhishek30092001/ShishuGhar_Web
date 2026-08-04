

import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar

def execute(filters=None):

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
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180})
    if selected_level == "6":
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
    if selected_level == "7":
        variable_columns.append({"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180})
        variable_columns.append({"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180})

    # Get initial and final dates from filters
    initial_month = int(filters.get("initial_month")) if filters.get("initial_month") else 1
    initial_year = int(filters.get("initial_year")) if filters.get("initial_year") else 2023
    final_month = int(filters.get("final_month")) if filters.get("final_month") else datetime.now().month
    final_year = int(filters.get("final_year")) if filters.get("final_year") else datetime.now().year
    
    initial_date = date(initial_year, initial_month, 1)
    final_date = date(final_year, final_month, calendar.monthrange(final_year, final_month)[1])
    month_col_heading = calendar.month_name[int(initial_month)]

    fixed_columns = [
        {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180},
        {"label": f"Enrolled till ({month_col_heading}/{initial_year})", 
         "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
        {"label": f"Measurements taken ({month_col_heading}/{initial_year})", 
         "fieldname": "measurements_taken", "fieldtype": "Int", "width": 260},
        {"label": f"Exited ({month_col_heading}/{initial_year} - {calendar.month_name[final_month]}/{final_year})", 
         "fieldname": "exited_children", "fieldtype": "Int", "width": 300},
        {"label": "Moderate to Normal", "fieldname": "md_nr_cnt", "fieldtype": "Data", "width": 175},
        {"label": "Severe to Normal", "fieldname": "sv_nr_cnt", "fieldtype": "Data", "width": 175},
        {"label": "Severe to Moderate", "fieldname": "sv_md_cnt", "fieldtype": "Data", "width": 175},
        {"label": "Normal to Moderate", "fieldname": "nr_md_cnt", "fieldtype": "Data", "width": 175},
        {"label": "Moderate to Severe", "fieldname": "md_sv_cnt", "fieldtype": "Data", "width": 175},
        {"label": "Normal to Severe", "fieldname": "nr_sv_cnt", "fieldtype": "Data", "width": 175},
        {"label": "No Change", "fieldname": "no_change", "fieldtype": "Int", "width": 165},
        {"label": "Total Improvement", "fieldname": "total_improvement", "fieldtype": "Data", "width": 175},
        {"label": "Total Faltering", "fieldname": "total_faltering", "fieldtype": "Data", "width": 175},
    ]

    columns = variable_columns + fixed_columns
    data = get_report_data(filters)
    
    # Calculate percentages for total improvement and faltering
    for row in data:
        total_children = row.get('measurements_taken', 0)
        
        sv_md_cnt = row.get('sv_md_cnt', 0) or 0
        md_nr_cnt = row.get('md_nr_cnt', 0) or 0
        sv_nr_cnt = row.get('sv_nr_cnt', 0) or 0
        nr_md_cnt = row.get('nr_md_cnt', 0) or 0
        md_sv_cnt = row.get('md_sv_cnt', 0) or 0
        nr_sv_cnt = row.get('nr_sv_cnt', 0) or 0
        
        improvement_count = int(sv_md_cnt + md_nr_cnt + sv_nr_cnt)
        improvement_percent = (improvement_count / total_children * 100) if total_children else 0
        
        faltering_count = int(nr_md_cnt + md_sv_cnt + nr_sv_cnt)
        faltering_percent = (faltering_count / total_children * 100) if total_children else 0
        
        row['total_improvement'] = f"{improvement_count} ({improvement_percent:.1f}%)"
        row['total_faltering'] = f"{faltering_count} ({faltering_percent:.1f}%)"
        
    return columns, data

def get_report_data(filters):
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner
    
    state_query = """ 
        SELECT DISTINCT ts.name AS state_id
        FROM `tabState` ts 
        JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
        WHERE ugm.parent = %s 
        ORDER BY ts.state_name
    """
    state_params = (frappe.session.user,)
    current_user_state = frappe.db.sql(state_query, state_params, as_dict=True)
    state_id = filters.get("state") or (current_user_state[0]['state_id'] if current_user_state else None)
    
    # Get initial and final dates from filters
    initial_month = int(filters.get("initial_month")) if filters.get("initial_month") else 1
    initial_year = int(filters.get("initial_year")) if filters.get("initial_year") else 2023
    final_month = int(filters.get("final_month")) if filters.get("final_month") else datetime.now().month
    final_year = int(filters.get("final_year")) if filters.get("final_year") else datetime.now().year
    
    initial_date = date(initial_year, initial_month, 1)
    initial_month_final_date = date(initial_year, initial_month, calendar.monthrange(initial_year, initial_month)[1])
    final_date = date(final_year, final_month, calendar.monthrange(final_year, final_month)[1])
    


    conditions = ["1=1"]
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

    params = {
        "initial_date": initial_date,
        "final_date": final_date,
        "initial_month_final_date":initial_month_final_date,
        "initial_month": initial_month,
        "initial_year": initial_year,
        "final_month": final_month,
        "final_year": final_year,
        "cstart_date": cstart_date,
        "cend_date": cend_date,
        "partner": partner_id,
        "state": state_id,
        "district": filters.get("district"),
        "block": filters.get("block"),
        "gp": filters.get("gp"),
        "creche": filters.get("creche"),
        "supervisor_id": filters.get("supervisor_id"),
        "creche_status_id": filters.get("creche_status_id"),
    }

    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
    if state_id:
        conditions.append("c.state_id = %(state)s")
    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
    if filters.get("creche_status_id"):
        conditions.append("(c.creche_status_id = %(creche_status_id)s)")
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
            params["phases"] = phases_cleaned    
    if cstart_date or cend_date:
        conditions.append("(c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)")

    level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name","u.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["p.partner_name","s.state_name", "d.district_name", "b.block_name", "g.gp_name", "u.full_name","c.creche_name","c.creche_id"],
    }

    selected_level = filters.get("level", "7")
    group_by_fields = level_mapping.get(selected_level, level_mapping["7"])
    group_by_field = ", ".join(group_by_fields)

    select_fields = [
        "p.partner_name AS partner",
        "s.state_name AS state",
        "d.district_name AS district",
        "b.block_name AS block",
        "g.gp_name AS gp",
        "u.full_name AS supervisor_id",
        "c.creche_name AS creche",
        "c.creche_id AS creche_id",
    ]

    selected_fields = []
    for field in select_fields:
        if any(field.split(" AS ")[0].split(".")[1] in group_by_field for group_by_field in group_by_fields):
            selected_fields.append(field)

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT
        {", ".join(selected_fields)},
        COUNT(DISTINCT c.name) AS operational_creches,
        COALESCE(ec.enrolled_children, 0) AS enrolled_children,
        COALESCE(mt.measurements_taken, 0) AS measurements_taken,
        COALESCE(exited.exited_count, 0) AS exited_children,
        COALESCE(transitions.sv_md_cnt, 0) AS sv_md_cnt,
        COALESCE(transitions.md_nr_cnt, 0) AS md_nr_cnt,
        COALESCE(transitions.sv_nr_cnt, 0) AS sv_nr_cnt,
        COALESCE(transitions.nr_md_cnt, 0) AS nr_md_cnt,
        COALESCE(transitions.md_sv_cnt, 0) AS md_sv_cnt,
        COALESCE(transitions.nr_sv_cnt, 0) AS nr_sv_cnt,
        COALESCE(transitions.no_change_cnt, 0) AS no_change
    FROM `tabCreche` c
    JOIN `tabState` s ON c.state_id = s.name
    LEFT JOIN `tabPartner` p ON c.partner_id = p.name
    LEFT JOIN `tabDistrict` d ON c.district_id = d.name 
    LEFT JOIN `tabBlock` b ON c.block_id = b.name 
    LEFT JOIN `tabGram Panchayat` g ON c.gp_id = g.name
    LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
    
    -- Enrolled children up to initial month/year......
    LEFT JOIN (
        SELECT cee.creche_id, COUNT(*) AS enrolled_children
        FROM `tabChild Enrollment and Exit` cee
        JOIN `tabCreche` cr ON cr.name = cee.creche_id
        WHERE cee.date_of_enrollment <= %(initial_month_final_date)s
          AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(initial_month_final_date)s)
        GROUP BY cee.creche_id
    ) ec ON c.name = ec.creche_id

    -- Children who exited between initial and final period
    LEFT JOIN (
        SELECT 
            creche_id, 
            COUNT(*) AS exited_count
        FROM `tabChild Enrollment and Exit`
        WHERE ((YEAR(date_of_enrollment) < %(initial_year)s) OR 
              (YEAR(date_of_enrollment) = %(initial_year)s AND 
               MONTH(date_of_enrollment) <= %(initial_month)s))
        AND date_of_exit IS NOT NULL
        AND date_of_exit BETWEEN %(initial_date)s AND %(final_date)s
       
        GROUP BY creche_id
    ) exited ON c.name = exited.creche_id

    -- Children with measurements in initial period 
    LEFT JOIN (
        SELECT 
            cgm.creche_id,
            COUNT(ad.chhguid) AS measurements_taken
        FROM `tabAnthropromatic Data` AS ad
        JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
        JOIN `tabChild Enrollment and Exit` cee ON (
            cee.childenrollguid = ad.childenrollguid 
            AND cee.creche_id = cgm.creche_id
            AND ((YEAR(cee.date_of_enrollment) < %(initial_year)s) OR 
                (YEAR(cee.date_of_enrollment) = %(initial_year)s AND 
                 MONTH(cee.date_of_enrollment) <= %(initial_month)s))
        )
        WHERE 
            MONTH(ad.measurement_taken_date) = %(initial_month)s 
            AND YEAR(ad.measurement_taken_date) = %(initial_year)s
          
        GROUP BY cgm.creche_id
    ) AS mt ON c.name = mt.creche_id

    -- Transitions query (only children who were still active in final period)
    LEFT JOIN (
        SELECT 
            final.creche_id,
            SUM(CASE WHEN initial.height_for_age = 1 AND final.height_for_age = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
            SUM(CASE WHEN initial.height_for_age = 2 AND final.height_for_age = 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
            SUM(CASE WHEN initial.height_for_age = 1 AND final.height_for_age = 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
            SUM(CASE WHEN initial.height_for_age = 3 AND final.height_for_age = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
            SUM(CASE WHEN initial.height_for_age = 2 AND final.height_for_age = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
            SUM(CASE WHEN initial.height_for_age = 3 AND final.height_for_age = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
            SUM(CASE WHEN initial.height_for_age = final.height_for_age THEN 1 ELSE 0 END) AS no_change_cnt
        FROM (
            -- Final measurements (must be enrolled by initial period and active at final period)
            SELECT 
                cgm.creche_id, 
                ad.chhguid, 
                ad.height_for_age,
                ad.childenrollguid
            FROM `tabAnthropromatic Data` ad
            JOIN `tabChild Growth Monitoring` cgm ON ad.parent = cgm.name
            JOIN `tabChild Enrollment and Exit` cee ON (
                cee.childenrollguid = ad.childenrollguid
                AND cee.creche_id = cgm.creche_id
                AND ((YEAR(cee.date_of_enrollment) < %(initial_year)s) OR 
                    (YEAR(cee.date_of_enrollment) = %(initial_year)s AND 
                    MONTH(cee.date_of_enrollment) <= %(initial_month)s))
                AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(final_date)s)
            )
            WHERE 
                YEAR(ad.measurement_taken_date) = %(final_year)s 
                AND MONTH(ad.measurement_taken_date) = %(final_month)s
               
        ) final
        JOIN (
            -- Initial measurements 
            SELECT 
                tad.chhguid, 
                tcgm.creche_id,
                tad.height_for_age,
                tad.childenrollguid
            FROM `tabChild Growth Monitoring` tcgm 
            JOIN `tabAnthropromatic Data` tad ON tcgm.name = tad.parent
            JOIN `tabChild Enrollment and Exit` cee ON (
                cee.childenrollguid = tad.childenrollguid
                AND cee.creche_id = tcgm.creche_id
                AND ((YEAR(cee.date_of_enrollment) < %(initial_year)s) OR 
                    (YEAR(cee.date_of_enrollment) = %(initial_year)s AND 
                     MONTH(cee.date_of_enrollment) <= %(initial_month)s))
            )
            WHERE  
                MONTH(tad.measurement_taken_date) = %(initial_month)s
                AND YEAR(tad.measurement_taken_date) = %(initial_year)s
               
        ) initial ON final.chhguid = initial.chhguid 
                AND final.creche_id = initial.creche_id
        GROUP BY final.creche_id
    ) AS transitions ON transitions.creche_id = c.name

    WHERE {where_clause}
    GROUP BY {group_by_field}
    ORDER BY {group_by_field}
    """

    data = frappe.db.sql(query, params, as_dict=True)
    
    # Final validation
    for row in data:
        measured = row.get('measurements_taken', 0)
        
        total_transitions = sum([
            row.get('sv_md_cnt', 0),
            row.get('md_nr_cnt', 0),
            row.get('sv_nr_cnt', 0),
            row.get('nr_md_cnt', 0),
            row.get('md_sv_cnt', 0),
            row.get('nr_sv_cnt', 0),
            row.get('no_change', 0)
        ])
        
        if measured > 0 and total_transitions == 0:
            row['no_change'] = measured
        
        
    return data
  
