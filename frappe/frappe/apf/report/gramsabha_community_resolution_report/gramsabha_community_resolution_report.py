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
            {"label": _("No. of creches submitted"), "fieldname": "with_att", "fieldtype": "HTML", "width": 250, "bold": 1},
            {"label": _("No. of creches Not submitted"), "fieldname": "without_att", "fieldtype": "HTML", "width": 270, "bold": 1}
        ],
        "2": [
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 200},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("No. of creches submitted"), "fieldname": "with_att", "fieldtype": "HTML", "width": 250, "bold": 1},
            {"label": _("No. of creches Not submitted"), "fieldname": "without_att", "fieldtype": "HTML", "width": 270, "bold": 1}
        ],
        "3": [
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("No. of creches submitted"), "fieldname": "with_att", "fieldtype": "HTML", "width": 250, "bold": 1},
            {"label": _("No. of creches Not submitted"), "fieldname": "without_att", "fieldtype": "HTML", "width": 270, "bold": 1}
        ],
        "4": [
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("No. of creches submitted"), "fieldname": "with_att", "fieldtype": "HTML", "width": 250, "bold": 1},
            {"label": _("No. of creches Not submitted"), "fieldname": "without_att", "fieldtype": "HTML", "width": 270, "bold": 1}
        ],
        "5": [
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("No. of creches submitted"), "fieldname": "with_att", "fieldtype": "HTML", "width": 250, "bold": 1},
            {"label": _("No. of creches Not submitted"), "fieldname": "without_att", "fieldtype": "HTML", "width": 270, "bold": 1}
        ],
        "6": [
            {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 180},
            {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "Data", "width": 180},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("No. of creches submitted"), "fieldname": "with_att", "fieldtype": "HTML", "width": 250, "bold": 1},
            {"label": _("No. of creches Not submitted"), "fieldname": "without_att", "fieldtype": "HTML", "width": 270, "bold": 1}
        ],
        "7": [
            {"label": _("State"), "fieldname": "state", "fieldtype": "HTML", "width": 180},
            {"label": _("District"), "fieldname": "district", "fieldtype": "HTML", "width": 180},
            {"label": _("Block"), "fieldname": "block", "fieldtype": "HTML", "width": 180},
            {"label": _("Gram Panchayat"), "fieldname": "gp", "fieldtype": "HTML", "width": 180},
            {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 180},
            {"label": _("Creche"), "fieldname": "creche", "fieldtype": "HTML", "width": 180},
            {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
            {"label": op_creche_label, "fieldname": "op_creche", "fieldtype": "Int", "width": 180, "bold": 1},
            {"label": _("Creche Opening Date"), "fieldname": "cr_open_date", "fieldtype": "Date", "width": 170},
            {"label": _("Gramsabha/Community resolution"), "fieldname": "image_links", "fieldtype": "HTML", "width": 300},
        ]
    }
    
    columns = level_mapping.get(selected_level, level_mapping["7"])
    
    if selected_level == "7":
        data = get_creche_level_data(filters)
        if data:
            total_row = calculate_totals_row_level7(data)
            data.append(total_row)
    else:
        data = get_aggregate_level_data(filters, selected_level)
        if data:
            total_row = calculate_totals_row(data, selected_level)
            
            # Format numbers, append percentages, and make fields clickable
            for row in data:
                op = row.get("op_creche") or 0
                w = row.get("with_att") or 0
                wo = row.get("without_att") or 0
                
                w_pct = int(round((w / op) * 100)) if op > 0 else 0
                wo_pct = int(round((wo / op) * 100)) if op > 0 else 0
                
                attrs = f"data-level='{selected_level}'"
                if "partner_id" in row: attrs += f" data-partner='{row.get('partner_id', '')}'"
                if "state_id" in row: attrs += f" data-state='{row.get('state_id', '')}'"
                if "district_id" in row: attrs += f" data-district='{row.get('district_id', '')}'"
                if "block_id" in row: attrs += f" data-block='{row.get('block_id', '')}'"
                if "gp_id" in row: attrs += f" data-gp='{row.get('gp_id', '')}'"
                if "supervisor_id_val" in row: attrs += f" data-supervisor='{row.get('supervisor_id_val', '')}'"
                
                row["with_att"] = f"<a href='javascript:void(0)' class='show-creche-list' data-type='with_att' {attrs}>{w} ({w_pct}%)</a>"
                row["without_att"] = f"<a href='javascript:void(0)' class='show-creche-list' data-type='without_att' {attrs}>{wo} ({wo_pct}%)</a>"
            
            # Add formatted totals row explicitly with clickability
            t_op = total_row.get("op_creche") or 0
            t_w = total_row.get("with_att") or 0
            t_wo = total_row.get("without_att") or 0
            
            t_w_pct = int(round((t_w / t_op) * 100)) if t_op > 0 else 0
            t_wo_pct = int(round((t_wo / t_op) * 100)) if t_op > 0 else 0
            
            total_attrs = f"data-level='{selected_level}'"
            
            # Note: Placed the <a> tag completely around the <b> tags so standard link clicking works flawlessly on the total row
            total_row["with_att"] = f"<a href='javascript:void(0)' class='show-creche-list' data-type='with_att' {total_attrs}><b>{t_w} ({t_w_pct}%)</b></a>"
            total_row["without_att"] = f"<a href='javascript:void(0)' class='show-creche-list' data-type='without_att' {total_attrs}><b>{t_wo} ({t_wo_pct}%)</b></a>"
            
            data.append(total_row)
    
    return columns, data


def calculate_totals_row(data, level):
    """Calculate totals row for levels 1-6"""
    total_op_creche = 0
    total_with_att = 0
    total_without_att = 0
    
    for row in data:
        try:
            val = row.get("op_creche")
            if val is not None:
                total_op_creche += int(val)
        except:
            pass
            
        try:
            val = row.get("with_att")
            if val is not None:
                total_with_att += int(val)
        except:
            pass
            
        try:
            val = row.get("without_att")
            if val is not None:
                total_without_att += int(val)
        except:
            pass
    
    total_row = {}
    
    level_label_map = {
        "1": "partner",
        "2": "state",
        "3": "district",
        "4": "block",
        "5": "supervisor",
        "6": "gp"
    }
    
    if level in level_label_map:
        total_row[level_label_map[level]] = "<b>Total</b>"
    
    total_row["op_creche"] = int(total_op_creche)
    total_row["with_att"] = int(total_with_att)
    total_row["without_att"] = int(total_without_att)
    
    return total_row


def calculate_totals_row_level7(data):
    """Calculate totals row for Level 7 (only op_creche is summed)"""
    total_op_creche = 0
    for row in data:
        try:
            val = row.get("op_creche")
            if val is not None:
                total_op_creche += int(val)
        except:
            pass
    
    total_row = {
        "creche": "<b>Total</b>",
        "op_creche": int(total_op_creche)
    }
    return total_row


def get_aggregate_level_data(filters, level):
    """Get aggregated data for levels 1-6 with exact counting of submitted/not submitted creches"""
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

    creche_status = filters.get("creche_status_id")
    if creche_status != "1":
        range_type = filters.get("cr_opening_range_type")
        if range_type:
            single_date = filters.get("single_date")
            date_range = filters.get("c_opening_range")
            
            if single_date and isinstance(single_date, str):
                single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
            if range_type == "between" and date_range and len(date_range) == 2:
                params["cstart_date"] = date_range[0]
                params["cend_date"] = date_range[1]
                conditions.append("tc.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
            elif range_type == "before" and single_date:
                params["cend_date"] = single_date - timedelta(days=1)
                conditions.append("tc.creche_opening_date <= %(cend_date)s")
            elif range_type == "after" and single_date:
                params["cstart_date"] = single_date + timedelta(days=1)
                conditions.append("tc.creche_opening_date >= %(cstart_date)s")
            elif range_type == "equal" and single_date:
                params["single_date"] = single_date
                conditions.append("tc.creche_opening_date = %(single_date)s")

        conditions.append("tc.creche_opening_date IS NOT NULL")
        conditions.append("tc.creche_opening_date <= %(end_date)s")

    creche_age = filters.get("creche_age", "")
    params["creche_age"] = creche_age
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

    where_clause = " AND ".join(conditions)

    if level == "1":
        query = f"""
            SELECT
                tp.name AS partner_id,
                tp.partner_name AS partner,
                COUNT(DISTINCT tc.name) AS op_creche,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NOT NULL AND tc.gram_consent_form != '' 
                    THEN 1 END) AS with_att,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NULL OR tc.gram_consent_form = '' 
                    THEN 1 END) AS without_att
            FROM
                `tabCreche` tc
                LEFT JOIN `tabPartner` tp ON tc.partner_id = tp.name
            WHERE
                {where_clause}
            GROUP BY
                tp.name, tp.partner_name
            ORDER BY
                tp.partner_name
        """

    elif level == "2":
        query = f"""
            SELECT
                ts.name AS state_id,
                ts.state_name AS state,
                COUNT(DISTINCT tc.name) AS op_creche,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NOT NULL AND tc.gram_consent_form != '' 
                    THEN 1 END) AS with_att,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NULL OR tc.gram_consent_form = '' 
                    THEN 1 END) AS without_att
            FROM
                `tabCreche` tc
                INNER JOIN `tabState` ts ON tc.state_id = ts.name
            WHERE
                {where_clause}
            GROUP BY
                ts.name, ts.state_name
            ORDER BY
                ts.state_name
        """

    elif level == "3":
        query = f"""
            SELECT
                ts.name AS state_id,
                ts.state_name AS state,
                td.name AS district_id,
                td.district_name AS district,
                COUNT(DISTINCT tc.name) AS op_creche,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NOT NULL AND tc.gram_consent_form != '' 
                    THEN 1 END) AS with_att,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NULL OR tc.gram_consent_form = '' 
                    THEN 1 END) AS without_att
            FROM
                `tabCreche` tc
                INNER JOIN `tabState` ts ON tc.state_id = ts.name
                INNER JOIN `tabDistrict` td ON tc.district_id = td.name
            WHERE
                {where_clause}
            GROUP BY
                ts.name, ts.state_name, td.name, td.district_name
            ORDER BY
                ts.state_name, td.district_name
        """

    elif level == "4":
        query = f"""
            SELECT
                ts.name AS state_id,
                ts.state_name AS state,
                td.name AS district_id,
                td.district_name AS district,
                tb.name AS block_id,
                tb.block_name AS block,
                COUNT(DISTINCT tc.name) AS op_creche,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NOT NULL AND tc.gram_consent_form != '' 
                    THEN 1 END) AS with_att,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NULL OR tc.gram_consent_form = '' 
                    THEN 1 END) AS without_att
            FROM
                `tabCreche` tc
                INNER JOIN `tabState` ts ON tc.state_id = ts.name
                INNER JOIN `tabDistrict` td ON tc.district_id = td.name
                INNER JOIN `tabBlock` tb ON tc.block_id = tb.name
            WHERE
                {where_clause}
            GROUP BY
                ts.name, ts.state_name, td.name, td.district_name, tb.name, tb.block_name
            ORDER BY
                ts.state_name, td.district_name, tb.block_name
        """

    elif level == "5":
        query = f"""
            SELECT
                ts.name AS state_id,
                ts.state_name AS state,
                td.name AS district_id,
                td.district_name AS district,
                tb.name AS block_id,
                tb.block_name AS block,
                tu.name AS supervisor_id_val,
                COALESCE(tu.full_name, 'Unassigned') AS supervisor,
                COUNT(DISTINCT tc.name) AS op_creche,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NOT NULL AND tc.gram_consent_form != '' 
                    THEN 1 END) AS with_att,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NULL OR tc.gram_consent_form = '' 
                    THEN 1 END) AS without_att
            FROM
                `tabCreche` tc
                INNER JOIN `tabState` ts ON tc.state_id = ts.name
                INNER JOIN `tabDistrict` td ON tc.district_id = td.name
                INNER JOIN `tabBlock` tb ON tc.block_id = tb.name
                LEFT JOIN `tabUser` tu ON tc.supervisor_id = tu.name
            WHERE
                {where_clause}
            GROUP BY
                ts.name, ts.state_name, td.name, td.district_name, tb.name, tb.block_name, tu.name, tu.full_name
            ORDER BY
                ts.state_name, td.district_name, tb.block_name, tu.full_name
        """

    elif level == "6":
        query = f"""
            SELECT
                ts.name AS state_id,
                ts.state_name AS state,
                td.name AS district_id,
                td.district_name AS district,
                tb.name AS block_id,
                tb.block_name AS block,
                tg.name AS gp_id,
                tg.gp_name AS gp,
                COUNT(DISTINCT tc.name) AS op_creche,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NOT NULL AND tc.gram_consent_form != '' 
                    THEN 1 END) AS with_att,
                COUNT(CASE 
                    WHEN tc.gram_consent_form IS NULL OR tc.gram_consent_form = '' 
                    THEN 1 END) AS without_att
            FROM
                `tabCreche` tc
                INNER JOIN `tabState` ts ON tc.state_id = ts.name
                INNER JOIN `tabDistrict` td ON tc.district_id = td.name
                INNER JOIN `tabBlock` tb ON tc.block_id = tb.name
                INNER JOIN `tabGram Panchayat` tg ON tc.gp_id = tg.name
            WHERE
                {where_clause}
            GROUP BY
                ts.name, ts.state_name, td.name, td.district_name, tb.name, tb.block_name, tg.name, tg.gp_name
            ORDER BY
                ts.state_name, td.district_name, tb.block_name, tg.gp_name
        """

    data = frappe.db.sql(query, params, as_dict=True)
    return data


def get_creche_level_data(filters):
    """Get Creche level data (Level 7) with op_creche = 1 per creche and default status filter"""
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

    creche_status = filters.get("creche_status_id")
    if creche_status != "1":
        range_type = filters.get("cr_opening_range_type")
        if range_type:
            single_date = filters.get("single_date")
            date_range = filters.get("c_opening_range")
            
            if single_date and isinstance(single_date, str):
                single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
            if range_type == "between" and date_range and len(date_range) == 2:
                params["cstart_date"] = date_range[0]
                params["cend_date"] = date_range[1]
                conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
            elif range_type == "before" and single_date:
                params["cend_date"] = single_date - timedelta(days=1)
                conditions.append("c.creche_opening_date <= %(cend_date)s")
            elif range_type == "after" and single_date:
                params["cstart_date"] = single_date + timedelta(days=1)
                conditions.append("c.creche_opening_date >= %(cstart_date)s")
            elif range_type == "equal" and single_date:
                params["single_date"] = single_date
                conditions.append("c.creche_opening_date = %(single_date)s")

        conditions.append("c.creche_opening_date IS NOT NULL")
        conditions.append("c.creche_opening_date <= %(end_date)s")

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

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            p.partner_name AS partner_display,
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
            c.creche_opening_date AS cr_open_date,
            c.gram_consent_form AS image_links,
            1 AS op_creche
        FROM `tabCreche` c
        LEFT JOIN `tabPartner` p ON c.partner_id = p.name
        INNER JOIN `tabState` s ON c.state_id = s.name
        INNER JOIN `tabDistrict` d ON c.district_id = d.name
        INNER JOIN `tabBlock` b ON c.block_id = b.name
        INNER JOIN `tabGram Panchayat` g ON c.gp_id = g.name
        LEFT JOIN `tabUser` u ON c.supervisor_id = u.name
        WHERE {where_clause}
        ORDER BY s.state_name, d.district_name, b.block_name, g.gp_name, u.full_name, c.creche_name
    """
    
    data = frappe.db.sql(query, params, as_dict=True)

    for row in data:
        row["state"] = f'<a href="/app/state/{row["state_id"]}" target="_blank">{row["state_display"]}</a>'
        row["district"] = f'<a href="/app/district/{row["district_id"]}" target="_blank">{row["district_display"]}</a>'
        row["block"] = f'<a href="/app/block/{row["block_id"]}" target="_blank">{row["block_display"]}</a>'
        row["gp"] = f'<a href="/app/gram-panchayat/{row["gp_id"]}" target="_blank">{row["gp_display"]}</a>'
        row["creche"] = f'<a href="/app/creche/{row["creche_id_internal"]}" target="_blank">{row["creche_display"]}</a>'
        row["creche_id"] = row["creche_id_external"]
        
        if row.get("image_links"):
            path = row["image_links"].strip()
            if not path.startswith(('/', 'http://', 'https://')):
                path = '/' + path.lstrip('/')
            full_url = get_url(path)
            filename = path.split('/')[-1] if '/' in path else path
            
            file_icon = ''
            if path.lower().endswith('.pdf'):
                file_icon = '<i class="fa fa-file-pdf-o" style="color: red; margin-right: 5px;"></i>'
            elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_icon = '<i class="fa fa-file-image-o" style="color: green; margin-right: 5px;"></i>'
            else:
                file_icon = '<i class="fa fa-file-o" style="margin-right: 5px;"></i>'
            
            row["image_links"] = f'<a href="{full_url}" class="image-popup-link" style="cursor: pointer;">{file_icon}{filename}</a>'
        else:
            row["image_links"] = ""

    return data

