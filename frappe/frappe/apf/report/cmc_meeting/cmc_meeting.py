import frappe
from frappe import _
from datetime import datetime, timedelta, date
import calendar
from frappe.utils import get_url

def execute(filters=None):
    selected_level = filters.get("level") or "7"
    
    # Determine the dynamic label for op_creche based on creche_status_id
    creche_status = filters.get("creche_status_id")
    op_creche_label = _("Operational Creches")  # Default
    if creche_status == "1":
        op_creche_label = _("Planned Creches")
    
    level_mapping = {
        "1": [
            {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
        ],
        "2": [
            {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 200},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
        ],
        "3": [
            {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
        ],
        "4": [
            {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
        ],
        "5": [
            {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
        ],
        "6": [
            {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
            {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
            {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
        ],
        "7": [
            {"label": _("Partner"), "fieldname": "partner_name", "fieldtype": "Data", "width": 180},
            {"label": _("State"), "fieldname": "state", "fieldtype": "HTML", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "HTML", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "HTML", "width": 180},
            {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "HTML", "width": 180},
            {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
            {"label": _("Creche"), "fieldname": "creche", "fieldtype": "HTML", "width": 180},
            {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 160},
            {"label": _("Age of Creche"), "fieldname": "creche_age", "fieldtype": "Data", "width": 160},
            {"label": _("CMC Meeting Conducted"), "fieldname": "meeting_conducted", "fieldtype": "Data", "width": 280},
            {"label": _("Meeting Date"), "fieldname": "meeting_date", "fieldtype": "Date", "width": 280},
            {"label": _("No. of Participants"), "fieldname": "participants", "fieldtype": "Int", "width": 280},
            {"label": _("Minutes Uploaded"), "fieldname": "minutes_uploaded", "fieldtype": "HTML", "width": 280},
        ]
    }
    
    columns = level_mapping.get(selected_level, level_mapping["7"])
    
    if selected_level == "7":
        data = get_creche_level_cmc_data(filters)
        if data:
            total_row = calculate_totals_row_level7_cmc(data)
            data.append(total_row)
    else:
        data = get_aggregate_level_cmc_data(filters, selected_level)
        if data:
            total_row = calculate_totals_row_cmc(data, selected_level)
            data.append(total_row)
    
    return columns, data


def calculate_totals_row_cmc(data, level):
    """Calculate totals row for levels 1-6"""
    total_op_creche = 0
    total_conducted = 0
    total_not_conducted = 0
    total_uploaded = 0
    total_not_uploaded = 0
    total_participants = 0
    
    for row in data:
        try:
            val = row.get("op_creche")
            if val is not None:
                total_op_creche += int(val)
        except:
            pass
            
        try:
            val = row.get("creches_conducted_meeting")
            if val is not None:
                total_conducted += int(val)
        except:
            pass
            
        try:
            val = row.get("creches_not_conducted_meeting")
            if val is not None:
                total_not_conducted += int(val)
        except:
            pass
            
        try:
            val = row.get("creches_uploaded_minutes")
            if val is not None:
                total_uploaded += int(val)
        except:
            pass
            
        try:
            val = row.get("creches_not_uploaded_minutes")
            if val is not None:
                total_not_uploaded += int(val)
        except:
            pass
            
        try:
            val = row.get("total_participants")
            if val is not None:
                total_participants += int(val)
        except:
            pass
    
    total_row = {}
    
    # For all levels the "Total" label goes in the first (leftmost) column.
    # Levels 2–6 now have "partner" as the first column.
    level_label_map = {
        "1": "partner",
        "2": "partner",
        "3": "partner",
        "4": "partner",
        "5": "partner",
        "6": "partner"
    }

    if level in level_label_map:
        total_row[level_label_map[level]] = "<b>Total</b>"
    
    total_row["op_creche"] = int(total_op_creche)
    total_row["creches_conducted_meeting"] = int(total_conducted)
    total_row["creches_not_conducted_meeting"] = int(total_not_conducted)
    total_row["creches_uploaded_minutes"] = int(total_uploaded)
    total_row["creches_not_uploaded_minutes"] = int(total_not_uploaded)
    total_row["total_participants"] = int(total_participants)
    
    return total_row


def calculate_totals_row_level7_cmc(data):
    """Calculate totals row for Level 7 (only summary totals)"""
    total_op_creche = 0
    total_conducted = 0
    total_not_conducted = 0
    total_uploaded = 0
    total_not_uploaded = 0
    total_participants = 0
    
    for row in data:
        try:
            if row.get("op_creche"):
                total_op_creche += 1
        except:
            pass
            
        try:
            if row.get("meeting_conducted") == "Yes":
                total_conducted += 1
            else:
                total_not_conducted += 1
        except:
            pass
            
        try:
            if row.get("minutes_uploaded") and row.get("minutes_uploaded") != "":
                total_uploaded += 1
            else:
                total_not_uploaded += 1
        except:
            pass
            
        try:
            val = row.get("participants")
            if val is not None:
                total_participants += int(val)
        except:
            pass
    
    total_row = {
        "creche": "<b>Summary</b>",
        "op_creche": total_op_creche,
        "meeting_conducted": f"Conducted: {total_conducted}, Not Conducted: {total_not_conducted}",
        "minutes_uploaded": f"Uploaded: {total_uploaded}, Not Uploaded: {total_not_uploaded}",
        "participants": total_participants
    }
    return total_row


def get_aggregate_level_cmc_data(filters, level):
    """Get aggregated CMC meeting data for levels 1-6"""
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    # Geography fallback (from the session user's geography mapping) is only
    # applied when there is NO partner resolved at all. Once a partner_id is
    # known — whether from the explicit filter or from the user's own profile —
    # the partner constraint already scopes the dataset. Adding the user's own
    # geo rows on top would hide states/districts/blocks/GPs that belong to the
    # partner but are not in the current user's geography mapping rows.
    state_ids = district_ids = block_ids = gp_ids = ()
    if not partner_id:
        state_query = """
            SELECT state_id, district_id, block_id, gp_id
            FROM `tabUser Geography Mapping`
            WHERE parent = %s
        """
        current_user_geo = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
        state_ids = tuple(set(g.get("state_id") for g in current_user_geo if g.get("state_id")))
        district_ids = tuple(set(g.get("district_id") for g in current_user_geo if g.get("district_id")))
        block_ids = tuple(set(g.get("block_id") for g in current_user_geo if g.get("block_id")))
        gp_ids = tuple(set(g.get("gp_id") for g in current_user_geo if g.get("gp_id")))

    # Build WHERE conditions
    conditions = ["1=1"]

    if partner_id:
        conditions.append("tc.partner_id = %(partner)s")
        params["partner"] = partner_id

    if filters.get("state"):
        conditions.append("tc.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        state_ids_str = ",".join([f"'{s}'" for s in state_ids])
        conditions.append(f"tc.state_id IN ({state_ids_str})")

    if filters.get("district"):
        conditions.append("tc.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids and not filters.get("state"):
        district_ids_str = ",".join([f"'{d}'" for d in district_ids])
        conditions.append(f"tc.district_id IN ({district_ids_str})")

    if filters.get("block"):
        conditions.append("tc.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids and not filters.get("district"):
        block_ids_str = ",".join([f"'{b}'" for b in block_ids])
        conditions.append(f"tc.block_id IN ({block_ids_str})")

    if filters.get("gp"):
        conditions.append("tc.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids and not filters.get("block"):
        gp_ids_str = ",".join([f"'{g}'" for g in gp_ids])
        conditions.append(f"tc.gp_id IN ({gp_ids_str})")

    if filters.get("supervisor_id"):
        conditions.append("tc.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")

    # Apply status filter based on creche_status_id
    if filters.get("creche_status_id"):
        conditions.append("tc.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")
    else:
        conditions.append("tc.creche_status_id = '3'")

    if filters.get("phases"):
        phases = filters.get("phases")
        if isinstance(phases, list):
            phases_str = ",".join([f"'{p}'" for p in phases])
            conditions.append(f"tc.phase IN ({phases_str})")
        else:
            conditions.append("tc.phase = %(phases)s")
            params["phases"] = phases

    # Creche opening date filters - only apply if status is NOT "1" (Planned)
    creche_status = filters.get("creche_status_id")
    if creche_status != "1":  # Ignore opening date filters for Planned status
        conditions.append("tc.creche_opening_date IS NOT NULL")
        conditions.append("tc.creche_opening_date <= %(end_date)s")
        
        # Add creche_age filter
        creche_age = filters.get("creche_age", "")
        if creche_age:
            conditions.append("""
                CASE
                    WHEN tc.creche_opening_date IS NULL THEN ''
                    WHEN TIMESTAMPDIFF(MONTH, tc.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                    WHEN TIMESTAMPDIFF(MONTH, tc.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                    WHEN TIMESTAMPDIFF(MONTH, tc.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                    WHEN TIMESTAMPDIFF(MONTH, tc.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                    WHEN TIMESTAMPDIFF(MONTH, tc.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                    ELSE ''
                END = %(creche_age)s
            """)
            params["creche_age"] = creche_age

    where_clause = " AND ".join(conditions)

    # CMC Meeting subquery
    cmc_sub = """
        SELECT 
            ccm.creche_id,
            COUNT(*) as meeting_count,
            SUM(ccm.number_of_participants) as total_participants,
            SUM(CASE WHEN ccm.image IS NOT NULL AND ccm.image != '' THEN 1 ELSE 0 END) as minutes_uploaded_count
        FROM `tabCreche Committee Meeting` ccm
        WHERE ccm.meeting_date BETWEEN %(start_date)s AND %(end_date)s
        GROUP BY ccm.creche_id
    """

    # Build queries for each level
    group_by_fields = {
        "1": "tp.partner_name",
        "2": "tp.partner_name, ts.state_name",
        "3": "tp.partner_name, ts.state_name, td.district_name",
        "4": "tp.partner_name, ts.state_name, td.district_name, tb.block_name",
        "5": "tp.partner_name, ts.state_name, td.district_name, tb.block_name, COALESCE(tu.full_name, 'Unassigned')",
        "6": "tp.partner_name, ts.state_name, td.district_name, tb.block_name, tg.gp_name"
    }

    select_fields = {
        "1": "tp.partner_name AS partner",
        "2": "tp.partner_name AS partner, ts.state_name AS state",
        "3": "tp.partner_name AS partner, ts.state_name AS state, td.district_name AS district",
        "4": "tp.partner_name AS partner, ts.state_name AS state, td.district_name AS district, tb.block_name AS block",
        "5": "tp.partner_name AS partner, ts.state_name AS state, td.district_name AS district, tb.block_name AS block, COALESCE(tu.full_name, 'Unassigned') AS supervisor",
        "6": "tp.partner_name AS partner, ts.state_name AS state, td.district_name AS district, tb.block_name AS block, tg.gp_name AS gp"
    }

    join_fields = {
        "1": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name",
        "2": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name INNER JOIN `tabState` ts ON tc.state_id = ts.name",
        "3": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name",
        "4": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name",
        "5": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name LEFT JOIN `tabUser` tu ON tc.supervisor_id = tu.name",
        "6": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name INNER JOIN `tabGram Panchayat` tg ON tc.gp_id = tg.name"
    }

    query = f"""
        SELECT
            {select_fields[level]},
            COUNT(DISTINCT tc.name) AS op_creche,
            COUNT(DISTINCT CASE WHEN cmc.creche_id IS NOT NULL THEN tc.name END) AS creches_conducted_meeting,
            COUNT(DISTINCT CASE WHEN cmc.creche_id IS NULL THEN tc.name END) AS creches_not_conducted_meeting,
            COUNT(DISTINCT CASE WHEN cmc.minutes_uploaded_count > 0 THEN tc.name END) AS creches_uploaded_minutes,
            COUNT(DISTINCT CASE WHEN cmc.creche_id IS NOT NULL AND cmc.minutes_uploaded_count = 0 THEN tc.name END) AS creches_not_uploaded_minutes,
            COALESCE(SUM(cmc.total_participants), 0) AS total_participants
        FROM
            `tabCreche` tc
            {join_fields[level]}
            LEFT JOIN ({cmc_sub}) AS cmc ON tc.name = cmc.creche_id
        WHERE
            {where_clause}
        GROUP BY
            {group_by_fields[level]}
        ORDER BY
            {group_by_fields[level]}
    """

    data = frappe.db.sql(query, params, as_dict=True)
    return data


def get_creche_level_cmc_data(filters):
    """Get Creche level CMC meeting data (Level 7)"""
    current_date = date.today()
    month = int(filters.get("month")) if filters.get("month") else current_date.month
    year = int(filters.get("year")) if filters.get("year") else current_date.year
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    conditions = ["1=1"]
    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    # Geography fallback (from the session user's geography mapping) is only
    # applied when there is NO partner resolved at all. Once a partner_id is
    # known — whether from the explicit filter or from the user's own profile —
    # the partner constraint already scopes the dataset. Adding the user's own
    # geo rows on top would hide states/districts/blocks/GPs that belong to the
    # partner but are not in the current user's geography mapping rows.
    state_ids = district_ids = block_ids = gp_ids = ()
    if not partner_id:
        state_query = """
            SELECT state_id, district_id, block_id, gp_id
            FROM `tabUser Geography Mapping`
            WHERE parent = %s
        """
        current_user_geo = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
        state_ids = tuple(set(g.get("state_id") for g in current_user_geo if g.get("state_id")))
        district_ids = tuple(set(g.get("district_id") for g in current_user_geo if g.get("district_id")))
        block_ids = tuple(set(g.get("block_id") for g in current_user_geo if g.get("block_id")))
        gp_ids = tuple(set(g.get("gp_id") for g in current_user_geo if g.get("gp_id")))

    if partner_id:
        conditions.append("c.partner_id = %(partner)s")
        params["partner"] = partner_id

    if filters.get("state"):
        conditions.append("c.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        state_ids_str = ",".join([f"'{s}'" for s in state_ids])
        conditions.append(f"c.state_id IN ({state_ids_str})")

    if filters.get("district"):
        conditions.append("c.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids and not filters.get("state"):
        district_ids_str = ",".join([f"'{d}'" for d in district_ids])
        conditions.append(f"c.district_id IN ({district_ids_str})")

    if filters.get("block"):
        conditions.append("c.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids and not filters.get("district"):
        block_ids_str = ",".join([f"'{b}'" for b in block_ids])
        conditions.append(f"c.block_id IN ({block_ids_str})")

    if filters.get("gp"):
        conditions.append("c.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids and not filters.get("block"):
        gp_ids_str = ",".join([f"'{g}'" for g in gp_ids])
        conditions.append(f"c.gp_id IN ({gp_ids_str})")

    if filters.get("supervisor_id"):
        conditions.append("c.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = filters.get("supervisor_id")

    if filters.get("creche"):
        conditions.append("c.name = %(creche)s")
        params["creche"] = filters.get("creche")

    # Apply status filter based on creche_status_id
    if filters.get("creche_status_id"):
        conditions.append("c.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = filters.get("creche_status_id")
    else:
        conditions.append("c.creche_status_id = '3'")

    if filters.get("phases"):
        phases = filters.get("phases")
        if isinstance(phases, list):
            phases_str = ",".join([f"'{p}'" for p in phases])
            conditions.append(f"c.phase IN ({phases_str})")
        else:
            conditions.append("c.phase = %(phases)s")
            params["phases"] = phases

    # Creche opening date filters - only apply if status is NOT "1" (Planned)
    creche_status = filters.get("creche_status_id")
    if creche_status != "1":  # Ignore opening date filters for Planned status
        conditions.append("c.creche_opening_date IS NOT NULL")
        conditions.append("c.creche_opening_date <= %(end_date)s")
        
        # Add creche_age filter
        creche_age = filters.get("creche_age", "")
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
            params["creche_age"] = creche_age

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            p.partner_name AS partner_name,
            s.name AS state_id,
            s.state_name AS state_display,
            d.name AS district_id,
            d.district_name AS district_display,
            b.name AS block_id,
            b.block_name AS block_display,
            g.name AS gp_id,
            g.gp_name AS gp_display,
            u.full_name AS supervisor,
            c.name AS creche_id_internal,
            c.creche_name AS creche_display,
            c.creche_id AS creche_id_external,
            CASE
                WHEN c.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                ELSE ''
            END AS creche_age,
            ccm.meeting_date,
            ccm.number_of_participants AS participants,
            ccm.image AS minutes_uploaded,
            CASE WHEN ccm.name IS NOT NULL THEN 'Yes' ELSE 'No' END AS meeting_conducted,
            1 AS op_creche
        FROM `tabCreche` c
        LEFT JOIN `tabPartner` p ON c.partner_id = p.name
        INNER JOIN `tabState` s ON c.state_id = s.name
        INNER JOIN `tabDistrict` d ON c.district_id = d.name
        INNER JOIN `tabBlock` b ON c.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        LEFT JOIN `tabUser` u ON c.supervisor_id = u.name
        LEFT JOIN `tabCreche Committee Meeting` ccm ON c.name = ccm.creche_id
            AND ccm.meeting_date BETWEEN %(start_date)s AND %(end_date)s
        WHERE {where_clause}
        ORDER BY p.partner_name, s.state_name, d.district_name, b.block_name, g.gp_name, u.full_name, c.creche_name
    """
    
    data = frappe.db.sql(query, params, as_dict=True)

    # Build HTML links for each row
    for row in data:
        row["state"] = f'<a href="/app/state/{row["state_id"]}" target="_blank">{row["state_display"]}</a>'
        row["district"] = f'<a href="/app/district/{row["district_id"]}" target="_blank">{row["district_display"]}</a>'
        row["block"] = f'<a href="/app/block/{row["block_id"]}" target="_blank">{row["block_display"]}</a>'
        row["gp"] = f'<a href="/app/gram-panchayat/{row["gp_id"]}" target="_blank">{row["gp_display"]}</a>'
        row["creche"] = f'<a href="/app/creche/{row["creche_id_internal"]}" target="_blank">{row["creche_display"]}</a>'
        row["creche_id"] = row["creche_id_external"]
        
        if row.get("minutes_uploaded"):
            path = row["minutes_uploaded"].strip()
            if not path.startswith(('/', 'http://', 'https://')):
                path = '/' + path.lstrip('/')
            full_url = get_url(path)
            filename = path.split('/')[-1] if '/' in path else path
            
            # Add file icon based on file type
            file_icon = ''
            if path.lower().endswith('.pdf'):
                file_icon = '<i class="fa fa-file-pdf-o" style="color: red; margin-right: 5px;"></i>'
            elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_icon = '<i class="fa fa-file-image-o" style="color: green; margin-right: 5px;"></i>'
            else:
                file_icon = '<i class="fa fa-file-o" style="margin-right: 5px;"></i>'
            
            row["minutes_uploaded"] = f'<a href="{full_url}" class="image-popup-link" style="cursor: pointer;">{file_icon}{filename}</a>'
        else:
            row["minutes_uploaded"] = ""

    return data











#backup - before age of creche filter
# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar
# from frappe.utils import get_url

# def execute(filters=None):
#     selected_level = filters.get("level") or "7"
    
#     # Determine the dynamic label for op_creche based on creche_status_id
#     creche_status = filters.get("creche_status_id")
#     op_creche_label = _("Operational Creches")  # Default
#     if creche_status == "1":
#         op_creche_label = _("Planned Creches")
    
#     level_mapping = {
#         "1": [
#             {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
#             {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "2": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 200},
#             {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "3": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "4": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
#             {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "5": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
#             {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#             {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "6": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
#             {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "Data", "width": 180},
#             {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "7": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "HTML", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "HTML", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "HTML", "width": 180},
#             {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "HTML", "width": 180},
#             {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#             {"label": _("Creche"), "fieldname": "creche", "fieldtype": "HTML", "width": 180},
#             {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 160},
#             {"label": _("CMC Meeting Conducted"), "fieldname": "meeting_conducted", "fieldtype": "Data", "width": 280},
#             {"label": _("Meeting Date"), "fieldname": "meeting_date", "fieldtype": "Date", "width": 280},
#             {"label": _("No. of Participants"), "fieldname": "participants", "fieldtype": "Int", "width": 280},
#             {"label": _("Minutes Uploaded"), "fieldname": "minutes_uploaded", "fieldtype": "HTML", "width": 280},
#         ]
#     }
    
#     columns = level_mapping.get(selected_level, level_mapping["7"])
    
#     if selected_level == "7":
#         data = get_creche_level_cmc_data(filters)
#         if data:
#             total_row = calculate_totals_row_level7_cmc(data)
#             data.append(total_row)
#     else:
#         data = get_aggregate_level_cmc_data(filters, selected_level)
#         if data:
#             total_row = calculate_totals_row_cmc(data, selected_level)
#             data.append(total_row)
    
#     return columns, data


# def calculate_totals_row_cmc(data, level):
#     """Calculate totals row for levels 1-6"""
#     total_op_creche = 0
#     total_conducted = 0
#     total_not_conducted = 0
#     total_uploaded = 0
#     total_not_uploaded = 0
#     total_participants = 0
    
#     for row in data:
#         try:
#             val = row.get("op_creche")
#             if val is not None:
#                 total_op_creche += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_conducted_meeting")
#             if val is not None:
#                 total_conducted += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_not_conducted_meeting")
#             if val is not None:
#                 total_not_conducted += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_uploaded_minutes")
#             if val is not None:
#                 total_uploaded += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_not_uploaded_minutes")
#             if val is not None:
#                 total_not_uploaded += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("total_participants")
#             if val is not None:
#                 total_participants += int(val)
#         except:
#             pass
    
#     total_row = {}
    
#     level_label_map = {
#         "1": "partner",
#         "2": "state",
#         "3": "district",
#         "4": "block",
#         "5": "supervisor",
#         "6": "gp"
#     }
    
#     if level in level_label_map:
#         total_row[level_label_map[level]] = "<b>Total</b>"
    
#     total_row["op_creche"] = int(total_op_creche)
#     total_row["creches_conducted_meeting"] = int(total_conducted)
#     total_row["creches_not_conducted_meeting"] = int(total_not_conducted)
#     total_row["creches_uploaded_minutes"] = int(total_uploaded)
#     total_row["creches_not_uploaded_minutes"] = int(total_not_uploaded)
#     total_row["total_participants"] = int(total_participants)
    
#     return total_row


# def calculate_totals_row_level7_cmc(data):
#     """Calculate totals row for Level 7 (only summary totals)"""
#     total_op_creche = 0
#     total_conducted = 0
#     total_not_conducted = 0
#     total_uploaded = 0
#     total_not_uploaded = 0
#     total_participants = 0
    
#     for row in data:
#         try:
#             if row.get("op_creche"):
#                 total_op_creche += 1
#         except:
#             pass
            
#         try:
#             if row.get("meeting_conducted") == "Yes":
#                 total_conducted += 1
#             else:
#                 total_not_conducted += 1
#         except:
#             pass
            
#         try:
#             if row.get("minutes_uploaded") and row.get("minutes_uploaded") != "":
#                 total_uploaded += 1
#             else:
#                 total_not_uploaded += 1
#         except:
#             pass
            
#         try:
#             val = row.get("participants")
#             if val is not None:
#                 total_participants += int(val)
#         except:
#             pass
    
#     total_row = {
#         "creche": "<b>Summary</b>",
#         "op_creche": total_op_creche,
#         "meeting_conducted": f"Conducted: {total_conducted}, Not Conducted: {total_not_conducted}",
#         "minutes_uploaded": f"Uploaded: {total_uploaded}, Not Uploaded: {total_not_uploaded}",
#         "participants": total_participants
#     }
#     return total_row


# def get_aggregate_level_cmc_data(filters, level):
#     """Get aggregated CMC meeting data for levels 1-6"""
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Fetch user's geography mapping
#     state_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#     """
#     current_user_geo = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
#     state_ids = tuple(set(g.get("state_id") for g in current_user_geo if g.get("state_id")))
#     district_ids = tuple(set(g.get("district_id") for g in current_user_geo if g.get("district_id")))
#     block_ids = tuple(set(g.get("block_id") for g in current_user_geo if g.get("block_id")))
#     gp_ids = tuple(set(g.get("gp_id") for g in current_user_geo if g.get("gp_id")))

#     # Build WHERE conditions
#     conditions = ["1=1"]
    
#     if partner_id:
#         conditions.append("tc.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     if filters.get("state"):
#         conditions.append("tc.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         state_ids_str = ",".join([f"'{s}'" for s in state_ids])
#         conditions.append(f"tc.state_id IN ({state_ids_str})")

#     if filters.get("district"):
#         conditions.append("tc.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids and not filters.get("state"):
#         district_ids_str = ",".join([f"'{d}'" for d in district_ids])
#         conditions.append(f"tc.district_id IN ({district_ids_str})")

#     if filters.get("block"):
#         conditions.append("tc.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids and not filters.get("district"):
#         block_ids_str = ",".join([f"'{b}'" for b in block_ids])
#         conditions.append(f"tc.block_id IN ({block_ids_str})")

#     if filters.get("gp"):
#         conditions.append("tc.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids and not filters.get("block"):
#         gp_ids_str = ",".join([f"'{g}'" for g in gp_ids])
#         conditions.append(f"tc.gp_id IN ({gp_ids_str})")

#     if filters.get("supervisor_id"):
#         conditions.append("tc.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")

#     # Apply status filter based on creche_status_id
#     if filters.get("creche_status_id"):
#         conditions.append("tc.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
#     else:
#         conditions.append("tc.creche_status_id = '3'")

#     if filters.get("phases"):
#         phases = filters.get("phases")
#         if isinstance(phases, list):
#             phases_str = ",".join([f"'{p}'" for p in phases])
#             conditions.append(f"tc.phase IN ({phases_str})")
#         else:
#             conditions.append("tc.phase = %(phases)s")
#             params["phases"] = phases

#     # Creche opening date filters - only apply if status is NOT "1" (Planned)
#     creche_status = filters.get("creche_status_id")
#     if creche_status != "1":  # Ignore opening date filters for Planned status
#         conditions.append("tc.creche_opening_date IS NOT NULL")
#         conditions.append("tc.creche_opening_date <= %(end_date)s")

#     where_clause = " AND ".join(conditions)

#     # CMC Meeting subquery
#     cmc_sub = """
#         SELECT 
#             ccm.creche_id,
#             COUNT(*) as meeting_count,
#             SUM(ccm.number_of_participants) as total_participants,
#             SUM(CASE WHEN ccm.image IS NOT NULL AND ccm.image != '' THEN 1 ELSE 0 END) as minutes_uploaded_count
#         FROM `tabCreche Committee Meeting` ccm
#         WHERE ccm.meeting_date BETWEEN %(start_date)s AND %(end_date)s
#         GROUP BY ccm.creche_id
#     """

#     # Build queries for each level
#     group_by_fields = {
#         "1": "tp.partner_name",
#         "2": "ts.state_name",
#         "3": "ts.state_name, td.district_name",
#         "4": "ts.state_name, td.district_name, tb.block_name",
#         "5": "ts.state_name, td.district_name, tb.block_name, COALESCE(tu.full_name, 'Unassigned')",
#         "6": "ts.state_name, td.district_name, tb.block_name, tg.gp_name"
#     }
    
#     select_fields = {
#         "1": "tp.partner_name AS partner",
#         "2": "ts.state_name AS state",
#         "3": "ts.state_name AS state, td.district_name AS district",
#         "4": "ts.state_name AS state, td.district_name AS district, tb.block_name AS block",
#         "5": "ts.state_name AS state, td.district_name AS district, tb.block_name AS block, COALESCE(tu.full_name, 'Unassigned') AS supervisor",
#         "6": "ts.state_name AS state, td.district_name AS district, tb.block_name AS block, tg.gp_name AS gp"
#     }
    
#     join_fields = {
#         "1": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name",
#         "2": "INNER JOIN `tabState` ts ON tc.state_id = ts.name",
#         "3": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name",
#         "4": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name",
#         "5": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name LEFT JOIN `tabUser` tu ON tc.supervisor_id = tu.name",
#         "6": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name INNER JOIN `tabGram Panchayat` tg ON tc.gp_id = tg.name"
#     }

#     query = f"""
#         SELECT
#             {select_fields[level]},
#             COUNT(DISTINCT tc.name) AS op_creche,
#             COUNT(DISTINCT CASE WHEN cmc.creche_id IS NOT NULL THEN tc.name END) AS creches_conducted_meeting,
#             COUNT(DISTINCT CASE WHEN cmc.creche_id IS NULL THEN tc.name END) AS creches_not_conducted_meeting,
#             COUNT(DISTINCT CASE WHEN cmc.minutes_uploaded_count > 0 THEN tc.name END) AS creches_uploaded_minutes,
#             COUNT(DISTINCT CASE WHEN cmc.creche_id IS NOT NULL AND cmc.minutes_uploaded_count = 0 THEN tc.name END) AS creches_not_uploaded_minutes,
#             COALESCE(SUM(cmc.total_participants), 0) AS total_participants
#         FROM
#             `tabCreche` tc
#             {join_fields[level]}
#             LEFT JOIN ({cmc_sub}) AS cmc ON tc.name = cmc.creche_id
#         WHERE
#             {where_clause}
#         GROUP BY
#             {group_by_fields[level]}
#         ORDER BY
#             {group_by_fields[level]}
#     """

#     data = frappe.db.sql(query, params, as_dict=True)
#     return data


# def get_creche_level_cmc_data(filters):
#     """Get Creche level CMC meeting data (Level 7)"""
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Fetch user's geography mapping
#     state_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#     """
#     current_user_geo = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
#     state_ids = tuple(set(g.get("state_id") for g in current_user_geo if g.get("state_id")))
#     district_ids = tuple(set(g.get("district_id") for g in current_user_geo if g.get("district_id")))
#     block_ids = tuple(set(g.get("block_id") for g in current_user_geo if g.get("block_id")))
#     gp_ids = tuple(set(g.get("gp_id") for g in current_user_geo if g.get("gp_id")))

#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         state_ids_str = ",".join([f"'{s}'" for s in state_ids])
#         conditions.append(f"c.state_id IN ({state_ids_str})")

#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids and not filters.get("state"):
#         district_ids_str = ",".join([f"'{d}'" for d in district_ids])
#         conditions.append(f"c.district_id IN ({district_ids_str})")

#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids and not filters.get("district"):
#         block_ids_str = ",".join([f"'{b}'" for b in block_ids])
#         conditions.append(f"c.block_id IN ({block_ids_str})")

#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids and not filters.get("block"):
#         gp_ids_str = ",".join([f"'{g}'" for g in gp_ids])
#         conditions.append(f"c.gp_id IN ({gp_ids_str})")

#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")

#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")

#     # Apply status filter based on creche_status_id
#     if filters.get("creche_status_id"):
#         conditions.append("c.creche_status_id = %(creche_status_id)s")
#         params["creche_status_id"] = filters.get("creche_status_id")
#     else:
#         conditions.append("c.creche_status_id = '3'")

#     if filters.get("phases"):
#         phases = filters.get("phases")
#         if isinstance(phases, list):
#             phases_str = ",".join([f"'{p}'" for p in phases])
#             conditions.append(f"c.phase IN ({phases_str})")
#         else:
#             conditions.append("c.phase = %(phases)s")
#             params["phases"] = phases

#     # Creche opening date filters - only apply if status is NOT "1" (Planned)
#     creche_status = filters.get("creche_status_id")
#     if creche_status != "1":  # Ignore opening date filters for Planned status
#         conditions.append("c.creche_opening_date IS NOT NULL")
#         conditions.append("c.creche_opening_date <= %(end_date)s")

#     where_clause = " AND ".join(conditions)

#     query = f"""
#         SELECT
#             s.name AS state_id,
#             s.state_name AS state_display,
#             d.name AS district_id,
#             d.district_name AS district_display,
#             b.name AS block_id,
#             b.block_name AS block_display,
#             g.name AS gp_id,
#             g.gp_name AS gp_display,
#             u.full_name AS supervisor,
#             c.name AS creche_id_internal,
#             c.creche_name AS creche_display,
#             c.creche_id AS creche_id_external,
#             ccm.meeting_date,
#             ccm.number_of_participants AS participants,
#             ccm.image AS minutes_uploaded,
#             CASE WHEN ccm.name IS NOT NULL THEN 'Yes' ELSE 'No' END AS meeting_conducted,
#             1 AS op_creche
#         FROM `tabCreche` c
#         INNER JOIN `tabState` s ON c.state_id = s.name
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         LEFT JOIN `tabUser` u ON c.supervisor_id = u.name
#         LEFT JOIN `tabCreche Committee Meeting` ccm ON c.name = ccm.creche_id 
#             AND ccm.meeting_date BETWEEN %(start_date)s AND %(end_date)s
#         WHERE {where_clause}
#         ORDER BY s.state_name, d.district_name, b.block_name, g.gp_name, u.full_name, c.creche_name
#     """
    
#     data = frappe.db.sql(query, params, as_dict=True)

#     # Build HTML links for each row
#     for row in data:
#         row["state"] = f'<a href="/app/state/{row["state_id"]}" target="_blank">{row["state_display"]}</a>'
#         row["district"] = f'<a href="/app/district/{row["district_id"]}" target="_blank">{row["district_display"]}</a>'
#         row["block"] = f'<a href="/app/block/{row["block_id"]}" target="_blank">{row["block_display"]}</a>'
#         row["gp"] = f'<a href="/app/gram-panchayat/{row["gp_id"]}" target="_blank">{row["gp_display"]}</a>'
#         row["creche"] = f'<a href="/app/creche/{row["creche_id_internal"]}" target="_blank">{row["creche_display"]}</a>'
#         row["creche_id"] = row["creche_id_external"]
        
#         if row.get("minutes_uploaded"):
#             path = row["minutes_uploaded"].strip()
#             if not path.startswith(('/', 'http://', 'https://')):
#                 path = '/' + path.lstrip('/')
#             full_url = get_url(path)
#             filename = path.split('/')[-1] if '/' in path else path
            
#             # Add file icon based on file type
#             file_icon = ''
#             if path.lower().endswith('.pdf'):
#                 file_icon = '<i class="fa fa-file-pdf-o" style="color: red; margin-right: 5px;"></i>'
#             elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
#                 file_icon = '<i class="fa fa-file-image-o" style="color: green; margin-right: 5px;"></i>'
#             else:
#                 file_icon = '<i class="fa fa-file-o" style="margin-right: 5px;"></i>'
            
#             row["minutes_uploaded"] = f'<a href="{full_url}" class="image-popup-link" style="cursor: pointer;">{file_icon}{filename}</a>'
#         else:
#             row["minutes_uploaded"] = ""

#     return data


















# import frappe
# from frappe import _
# from datetime import datetime, timedelta, date
# import calendar
# from frappe.utils import get_url

# def execute(filters=None):
#     selected_level = filters.get("level") or "7"
    
#     level_mapping = {
#         "1": [
#             {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 180},
#             {"label": _("Operational Creches"), "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "2": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 200},
#             {"label": _("Operational Creches"), "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "3": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Operational Creches"), "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "4": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
#             {"label": _("Operational Creches"), "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "5": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
#             {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#             {"label": _("Operational Creches"), "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "6": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
#             {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "Data", "width": 180},
#             {"label": _("Operational Creches"), "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
#             {"label": _("Creches Conducted CMC Meeting"), "fieldname": "creches_conducted_meeting", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Conducted CMC Meeting"), "fieldname": "creches_not_conducted_meeting", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Creches Uploaded Minutes"), "fieldname": "creches_uploaded_minutes", "fieldtype": "Int", "width": 250, "bold": 1},
#             {"label": _("Creches Not Uploaded Minutes"), "fieldname": "creches_not_uploaded_minutes", "fieldtype": "Int", "width": 270, "bold": 1},
#             {"label": _("Total Participants Attended"), "fieldname": "total_participants", "fieldtype": "Int", "width": 200, "bold": 1}
#         ],
#         "7": [
#             {"label": _("State"), "fieldname": "state", "fieldtype": "HTML", "width": 180},
#             {"label": _("District"), "fieldname": "district", "fieldtype": "HTML", "width": 180},
#             {"label": _("Block"), "fieldname": "block", "fieldtype": "HTML", "width": 180},
#             {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "HTML", "width": 180},
#             {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
#             {"label": _("Creche"), "fieldname": "creche", "fieldtype": "HTML", "width": 180},
#             {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 160},
#             {"label": _("CMC Meeting Conducted"), "fieldname": "meeting_conducted", "fieldtype": "Data", "width": 280},
#             {"label": _("Meeting Date"), "fieldname": "meeting_date", "fieldtype": "Date", "width": 280},
#             {"label": _("No. of Participants"), "fieldname": "participants", "fieldtype": "Int", "width": 280},
#             {"label": _("Minutes Uploaded"), "fieldname": "minutes_uploaded", "fieldtype": "HTML", "width": 280},
#         ]
#     }
    
#     columns = level_mapping.get(selected_level, level_mapping["7"])
    
#     if selected_level == "7":
#         data = get_creche_level_cmc_data(filters)
#         if data:
#             total_row = calculate_totals_row_level7_cmc(data)
#             data.append(total_row)
#     else:
#         data = get_aggregate_level_cmc_data(filters, selected_level)
#         if data:
#             total_row = calculate_totals_row_cmc(data, selected_level)
#             data.append(total_row)
    
#     return columns, data


# def calculate_totals_row_cmc(data, level):
#     """Calculate totals row for levels 1-6"""
#     total_op_creche = 0
#     total_conducted = 0
#     total_not_conducted = 0
#     total_uploaded = 0
#     total_not_uploaded = 0
#     total_participants = 0
    
#     for row in data:
#         try:
#             val = row.get("op_creche")
#             if val is not None:
#                 total_op_creche += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_conducted_meeting")
#             if val is not None:
#                 total_conducted += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_not_conducted_meeting")
#             if val is not None:
#                 total_not_conducted += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_uploaded_minutes")
#             if val is not None:
#                 total_uploaded += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("creches_not_uploaded_minutes")
#             if val is not None:
#                 total_not_uploaded += int(val)
#         except:
#             pass
            
#         try:
#             val = row.get("total_participants")
#             if val is not None:
#                 total_participants += int(val)
#         except:
#             pass
    
#     total_row = {}
    
#     level_label_map = {
#         "1": "partner",
#         "2": "state",
#         "3": "district",
#         "4": "block",
#         "5": "supervisor",
#         "6": "gp"
#     }
    
#     if level in level_label_map:
#         total_row[level_label_map[level]] = "<b>Total</b>"
    
#     total_row["op_creche"] = int(total_op_creche)
#     total_row["creches_conducted_meeting"] = int(total_conducted)
#     total_row["creches_not_conducted_meeting"] = int(total_not_conducted)
#     total_row["creches_uploaded_minutes"] = int(total_uploaded)
#     total_row["creches_not_uploaded_minutes"] = int(total_not_uploaded)
#     total_row["total_participants"] = int(total_participants)
    
#     return total_row


# def calculate_totals_row_level7_cmc(data):
#     """Calculate totals row for Level 7 (only summary totals)"""
#     total_op_creche = 0
#     total_conducted = 0
#     total_not_conducted = 0
#     total_uploaded = 0
#     total_not_uploaded = 0
#     total_participants = 0
    
#     for row in data:
#         try:
#             if row.get("op_creche"):
#                 total_op_creche += 1
#         except:
#             pass
            
#         try:
#             if row.get("meeting_conducted") == "Yes":
#                 total_conducted += 1
#             else:
#                 total_not_conducted += 1
#         except:
#             pass
            
#         try:
#             if row.get("minutes_uploaded") and row.get("minutes_uploaded") != "":
#                 total_uploaded += 1
#             else:
#                 total_not_uploaded += 1
#         except:
#             pass
            
#         try:
#             val = row.get("participants")
#             if val is not None:
#                 total_participants += int(val)
#         except:
#             pass
    
#     total_row = {
#         "creche": "<b>Summary</b>",
#         "op_creche": total_op_creche,
#         "meeting_conducted": f"Conducted: {total_conducted}, Not Conducted: {total_not_conducted}",
#         "minutes_uploaded": f"Uploaded: {total_uploaded}, Not Uploaded: {total_not_uploaded}",
#         "participants": total_participants
#     }
#     return total_row


# def get_aggregate_level_cmc_data(filters, level):
#     """Get aggregated CMC meeting data for levels 1-6"""
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Fetch user's geography mapping
#     state_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#     """
#     current_user_geo = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
#     state_ids = tuple(set(g.get("state_id") for g in current_user_geo if g.get("state_id")))
#     district_ids = tuple(set(g.get("district_id") for g in current_user_geo if g.get("district_id")))
#     block_ids = tuple(set(g.get("block_id") for g in current_user_geo if g.get("block_id")))
#     gp_ids = tuple(set(g.get("gp_id") for g in current_user_geo if g.get("gp_id")))

#     # Build WHERE conditions
#     conditions = ["1=1"]
    
#     if partner_id:
#         conditions.append("tc.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     if filters.get("state"):
#         conditions.append("tc.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         state_ids_str = ",".join([f"'{s}'" for s in state_ids])
#         conditions.append(f"tc.state_id IN ({state_ids_str})")

#     if filters.get("district"):
#         conditions.append("tc.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids and not filters.get("state"):
#         district_ids_str = ",".join([f"'{d}'" for d in district_ids])
#         conditions.append(f"tc.district_id IN ({district_ids_str})")

#     if filters.get("block"):
#         conditions.append("tc.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids and not filters.get("district"):
#         block_ids_str = ",".join([f"'{b}'" for b in block_ids])
#         conditions.append(f"tc.block_id IN ({block_ids_str})")

#     if filters.get("gp"):
#         conditions.append("tc.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids and not filters.get("block"):
#         gp_ids_str = ",".join([f"'{g}'" for g in gp_ids])
#         conditions.append(f"tc.gp_id IN ({gp_ids_str})")

#     if filters.get("supervisor_id"):
#         conditions.append("tc.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")

#     # Apply default status filter for operational creches
#     conditions.append("tc.creche_status_id = '3'")

#     if filters.get("phases"):
#         phases = filters.get("phases")
#         if isinstance(phases, list):
#             phases_str = ",".join([f"'{p}'" for p in phases])
#             conditions.append(f"tc.phase IN ({phases_str})")
#         else:
#             conditions.append("tc.phase = %(phases)s")
#             params["phases"] = phases

#     conditions.append("tc.creche_opening_date IS NOT NULL")
#     conditions.append("tc.creche_opening_date <= %(end_date)s")

#     where_clause = " AND ".join(conditions)

#     # CMC Meeting subquery
#     cmc_sub = """
#         SELECT 
#             ccm.creche_id,
#             COUNT(*) as meeting_count,
#             SUM(ccm.number_of_participants) as total_participants,
#             SUM(CASE WHEN ccm.image IS NOT NULL AND ccm.image != '' THEN 1 ELSE 0 END) as minutes_uploaded_count
#         FROM `tabCreche Committee Meeting` ccm
#         WHERE ccm.meeting_date BETWEEN %(start_date)s AND %(end_date)s
#         GROUP BY ccm.creche_id
#     """

#     # Build queries for each level
#     group_by_fields = {
#         "1": "tp.partner_name",
#         "2": "ts.state_name",
#         "3": "ts.state_name, td.district_name",
#         "4": "ts.state_name, td.district_name, tb.block_name",
#         "5": "ts.state_name, td.district_name, tb.block_name, COALESCE(tu.full_name, 'Unassigned')",
#         "6": "ts.state_name, td.district_name, tb.block_name, tg.gp_name"
#     }
    
#     select_fields = {
#         "1": "tp.partner_name AS partner",
#         "2": "ts.state_name AS state",
#         "3": "ts.state_name AS state, td.district_name AS district",
#         "4": "ts.state_name AS state, td.district_name AS district, tb.block_name AS block",
#         "5": "ts.state_name AS state, td.district_name AS district, tb.block_name AS block, COALESCE(tu.full_name, 'Unassigned') AS supervisor",
#         "6": "ts.state_name AS state, td.district_name AS district, tb.block_name AS block, tg.gp_name AS gp"
#     }
    
#     join_fields = {
#         "1": "LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name",
#         "2": "INNER JOIN `tabState` ts ON tc.state_id = ts.name",
#         "3": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name",
#         "4": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name",
#         "5": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name LEFT JOIN `tabUser` tu ON tc.supervisor_id = tu.name",
#         "6": "INNER JOIN `tabState` ts ON tc.state_id = ts.name INNER JOIN `tabDistrict` td ON tc.district_id = td.name INNER JOIN `tabBlock` tb ON tc.block_id = tb.name INNER JOIN `tabGram Panchayat` tg ON tc.gp_id = tg.name"
#     }

#     query = f"""
#         SELECT
#             {select_fields[level]},
#             COUNT(DISTINCT tc.name) AS op_creche,
#             COUNT(DISTINCT CASE WHEN cmc.creche_id IS NOT NULL THEN tc.name END) AS creches_conducted_meeting,
#             COUNT(DISTINCT CASE WHEN cmc.creche_id IS NULL THEN tc.name END) AS creches_not_conducted_meeting,
#             COUNT(DISTINCT CASE WHEN cmc.minutes_uploaded_count > 0 THEN tc.name END) AS creches_uploaded_minutes,
#             COUNT(DISTINCT CASE WHEN cmc.creche_id IS NOT NULL AND cmc.minutes_uploaded_count = 0 THEN tc.name END) AS creches_not_uploaded_minutes,
#             COALESCE(SUM(cmc.total_participants), 0) AS total_participants
#         FROM
#             `tabCreche` tc
#             {join_fields[level]}
#             LEFT JOIN ({cmc_sub}) AS cmc ON tc.name = cmc.creche_id
#         WHERE
#             {where_clause}
#         GROUP BY
#             {group_by_fields[level]}
#         ORDER BY
#             {group_by_fields[level]}
#     """

#     data = frappe.db.sql(query, params, as_dict=True)
#     return data


# def get_creche_level_cmc_data(filters):
#     """Get Creche level CMC meeting data (Level 7)"""
#     current_date = date.today()
#     month = int(filters.get("month")) if filters.get("month") else current_date.month
#     year = int(filters.get("year")) if filters.get("year") else current_date.year
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)

#     conditions = ["1=1"]
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#     }

#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     # Fetch user's geography mapping
#     state_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#     """
#     current_user_geo = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)
#     state_ids = tuple(set(g.get("state_id") for g in current_user_geo if g.get("state_id")))
#     district_ids = tuple(set(g.get("district_id") for g in current_user_geo if g.get("district_id")))
#     block_ids = tuple(set(g.get("block_id") for g in current_user_geo if g.get("block_id")))
#     gp_ids = tuple(set(g.get("gp_id") for g in current_user_geo if g.get("gp_id")))

#     if partner_id:
#         conditions.append("c.partner_id = %(partner)s")
#         params["partner"] = partner_id

#     if filters.get("state"):
#         conditions.append("c.state_id = %(state)s")
#         params["state"] = filters.get("state")
#     elif state_ids:
#         state_ids_str = ",".join([f"'{s}'" for s in state_ids])
#         conditions.append(f"c.state_id IN ({state_ids_str})")

#     if filters.get("district"):
#         conditions.append("c.district_id = %(district)s")
#         params["district"] = filters.get("district")
#     elif district_ids and not filters.get("state"):
#         district_ids_str = ",".join([f"'{d}'" for d in district_ids])
#         conditions.append(f"c.district_id IN ({district_ids_str})")

#     if filters.get("block"):
#         conditions.append("c.block_id = %(block)s")
#         params["block"] = filters.get("block")
#     elif block_ids and not filters.get("district"):
#         block_ids_str = ",".join([f"'{b}'" for b in block_ids])
#         conditions.append(f"c.block_id IN ({block_ids_str})")

#     if filters.get("gp"):
#         conditions.append("c.gp_id = %(gp)s")
#         params["gp"] = filters.get("gp")
#     elif gp_ids and not filters.get("block"):
#         gp_ids_str = ",".join([f"'{g}'" for g in gp_ids])
#         conditions.append(f"c.gp_id IN ({gp_ids_str})")

#     if filters.get("supervisor_id"):
#         conditions.append("c.supervisor_id = %(supervisor_id)s")
#         params["supervisor_id"] = filters.get("supervisor_id")

#     if filters.get("creche"):
#         conditions.append("c.name = %(creche)s")
#         params["creche"] = filters.get("creche")

#     # Apply default status filter for operational creches
#     conditions.append("c.creche_status_id = '3'")

#     if filters.get("phases"):
#         phases = filters.get("phases")
#         if isinstance(phases, list):
#             phases_str = ",".join([f"'{p}'" for p in phases])
#             conditions.append(f"c.phase IN ({phases_str})")
#         else:
#             conditions.append("c.phase = %(phases)s")
#             params["phases"] = phases

#     conditions.append("c.creche_opening_date IS NOT NULL")
#     conditions.append("c.creche_opening_date <= %(end_date)s")

#     where_clause = " AND ".join(conditions)

#     query = f"""
#         SELECT
#             s.name AS state_id,
#             s.state_name AS state_display,
#             d.name AS district_id,
#             d.district_name AS district_display,
#             b.name AS block_id,
#             b.block_name AS block_display,
#             g.name AS gp_id,
#             g.gp_name AS gp_display,
#             u.full_name AS supervisor,
#             c.name AS creche_id_internal,
#             c.creche_name AS creche_display,
#             c.creche_id AS creche_id_external,
#             ccm.meeting_date,
#             ccm.number_of_participants AS participants,
#             ccm.image AS minutes_uploaded,
#             CASE WHEN ccm.name IS NOT NULL THEN 'Yes' ELSE 'No' END AS meeting_conducted,
#             1 AS op_creche
#         FROM `tabCreche` c
#         INNER JOIN `tabState` s ON c.state_id = s.name
#         INNER JOIN `tabDistrict` d ON c.district_id = d.name
#         INNER JOIN `tabBlock` b ON c.block_id = b.name
#         INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#         LEFT JOIN `tabUser` u ON c.supervisor_id = u.name
#         LEFT JOIN `tabCreche Committee Meeting` ccm ON c.name = ccm.creche_id 
#             AND ccm.meeting_date BETWEEN %(start_date)s AND %(end_date)s
#         WHERE {where_clause}
#         ORDER BY s.state_name, d.district_name, b.block_name, g.gp_name, u.full_name, c.creche_name
#     """
    
#     data = frappe.db.sql(query, params, as_dict=True)

#     # Build HTML links for each row
#     for row in data:
#         row["state"] = f'<a href="/app/state/{row["state_id"]}" target="_blank">{row["state_display"]}</a>'
#         row["district"] = f'<a href="/app/district/{row["district_id"]}" target="_blank">{row["district_display"]}</a>'
#         row["block"] = f'<a href="/app/block/{row["block_id"]}" target="_blank">{row["block_display"]}</a>'
#         row["gp"] = f'<a href="/app/gram-panchayat/{row["gp_id"]}" target="_blank">{row["gp_display"]}</a>'
#         row["creche"] = f'<a href="/app/creche/{row["creche_id_internal"]}" target="_blank">{row["creche_display"]}</a>'
#         row["creche_id"] = row["creche_id_external"]
        
#         if row.get("minutes_uploaded"):
#             path = row["minutes_uploaded"].strip()
#             if not path.startswith(('/', 'http://', 'https://')):
#                 path = '/' + path.lstrip('/')
#             full_url = get_url(path)
#             filename = path.split('/')[-1] if '/' in path else path
            
#             # Add file icon based on file type
#             file_icon = ''
#             if path.lower().endswith('.pdf'):
#                 file_icon = '<i class="fa fa-file-pdf-o" style="color: red; margin-right: 5px;"></i>'
#             elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
#                 file_icon = '<i class="fa fa-file-image-o" style="color: green; margin-right: 5px;"></i>'
#             else:
#                 file_icon = '<i class="fa fa-file-o" style="margin-right: 5px;"></i>'
            
#             row["minutes_uploaded"] = f'<a href="{full_url}" class="image-popup-link" style="cursor: pointer;">{file_icon}{filename}</a>'
#         else:
#             row["minutes_uploaded"] = ""

#     return data