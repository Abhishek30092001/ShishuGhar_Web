import frappe
from frappe.utils import nowdate
import calendar
import json
from html import escape
from datetime import datetime, timedelta, date


def _clickable_count(value, metric, level, row_ctx, bold=False, extra=None):
    """Render a count cell as a clickable link that carries enough context for
    the detail popup (get_count_details) to re-query the same subset.

    metric  : "creches", "children" or "vaccine"
    level   : the report level (string)
    row_ctx : {group_column_label: display_value} identifying this row's group
    extra   : optional extra context (e.g. {"vaccine": "IPV 1"})
    bold    : render the label bold (used on Total rows)
    """
    ctx = {"metric": metric, "level": str(level), "group": row_ctx or {}}
    if extra:
        ctx.update(extra)
    data_attr = escape(json.dumps(ctx), quote=True)
    label = str(value)
    if bold:
        label = f"<b>{label}</b>"
    # Normal text styling (no blue) — looks like plain text, clickable on hover.
    return (
        f"<a href='#' class='vaccine-count-link' "
        f"data-ctx=\"{data_attr}\" "
        f"style='color:inherit;cursor:pointer;text-decoration:none;'>"
        f"{label}</a>"
    )

VACCINE_LIST = [
    "IPV 1", "IPV 2", "IPV 3",
    "Vitamin A (Dose 1)", "Vitamin A (Dose 2)", "Vitamin A (Dose 3)", "Vitamin A (Dose 4)", "Vitamin A (Dose 5)",
    "PCV Booster", "PCV 1", "PCV 2",
    "JE 1", "JE 2",
    "Albendazole 1", "Albendazole 2", "Albendazole 3", "Albendazole 4",
    "Rota 1", "Rota 2", "Rota 3",
    "DPT Booster", "Pentavalent 1", "Pentavalent 2", "Pentavalent 3",
    "Measles 1 (MR)", "Measles 2 (MR)",
    "OPV Booster", "OPV 0", "OPV 1", "OPV 2", "OPV 3",
    "BCG", "Hepatitis B 0"
]

# Maps each vaccine to (v_data column alias, eligibility threshold in days),
# mirroring the CASE logic in the main report query. Used by the detail popup
# to compute a single vaccine's status (Yes / No / Overdue / Not Eligible).
VACCINE_STATUS_MAP = {
    "IPV 1": ("v_ipv_1", 42),
    "IPV 2": ("v_ipv_2", 98),
    "IPV 3": ("v_ipv_3", 270),
    "Vitamin A (Dose 1)": ("v_vit_1", 270),
    "Vitamin A (Dose 2)": ("v_vit_2", 540),
    "Vitamin A (Dose 3)": ("v_vit_3", 720),
    "Vitamin A (Dose 4)": ("v_vit_4", 900),
    "Vitamin A (Dose 5)": ("v_vit_5", 1080),
    "PCV Booster": ("v_pcv_b", 270),
    "PCV 1": ("v_pcv_1", 42),
    "PCV 2": ("v_pcv_2", 98),
    "JE 1": ("v_je_1", 270),
    "JE 2": ("v_je_2", 480),
    "Albendazole 1": ("v_alb_1", 540),
    "Albendazole 2": ("v_alb_2", 720),
    "Albendazole 3": ("v_alb_3", 900),
    "Albendazole 4": ("v_alb_4", 1080),
    "Rota 1": ("v_rota_1", 42),
    "Rota 2": ("v_rota_2", 70),
    "Rota 3": ("v_rota_3", 98),
    "DPT Booster": ("v_dpt_b", 480),
    "Pentavalent 1": ("v_pent_1", 42),
    "Pentavalent 2": ("v_pent_2", 70),
    "Pentavalent 3": ("v_pent_3", 98),
    "Measles 1 (MR)": ("v_meas_1", 270),
    "Measles 2 (MR)": ("v_meas_2", 480),
    "OPV Booster": ("v_opv_b", 480),
    "OPV 0": ("v_opv_0", 0),
    "OPV 1": ("v_opv_1", 42),
    "OPV 2": ("v_opv_2", 70),
    "OPV 3": ("v_opv_3", 98),
    "BCG": ("v_bcg", 0),
    "Hepatitis B 0": ("v_hep_0", 0),
}

# The vaccine subquery used by the main report; reused for the vaccine popup.
_VACCINE_SUBQUERY = """
    LEFT JOIN (
        SELECT
            ci.childenrolledguid,
            MAX(CASE WHEN vv.vaccine = 'IPV 1' THEN vd.vaccinated END) AS v_ipv_1,
            MAX(CASE WHEN vv.vaccine = 'IPV 2' THEN vd.vaccinated END) AS v_ipv_2,
            MAX(CASE WHEN vv.vaccine = 'IPV 3' THEN vd.vaccinated END) AS v_ipv_3,
            MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 1)' THEN vd.vaccinated END) AS v_vit_1,
            MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 2)' THEN vd.vaccinated END) AS v_vit_2,
            MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 3)' THEN vd.vaccinated END) AS v_vit_3,
            MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 4)' THEN vd.vaccinated END) AS v_vit_4,
            MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 5)' THEN vd.vaccinated END) AS v_vit_5,
            MAX(CASE WHEN vv.vaccine = 'PCV Booster' THEN vd.vaccinated END) AS v_pcv_b,
            MAX(CASE WHEN vv.vaccine = 'PCV 1' THEN vd.vaccinated END) AS v_pcv_1,
            MAX(CASE WHEN vv.vaccine = 'PCV 2' THEN vd.vaccinated END) AS v_pcv_2,
            MAX(CASE WHEN vv.vaccine = 'JE 1' THEN vd.vaccinated END) AS v_je_1,
            MAX(CASE WHEN vv.vaccine = 'JE 2' THEN vd.vaccinated END) AS v_je_2,
            MAX(CASE WHEN vv.vaccine = 'Albendazole 1' THEN vd.vaccinated END) AS v_alb_1,
            MAX(CASE WHEN vv.vaccine = 'Albendazole 2' THEN vd.vaccinated END) AS v_alb_2,
            MAX(CASE WHEN vv.vaccine = 'Albendazole 3' THEN vd.vaccinated END) AS v_alb_3,
            MAX(CASE WHEN vv.vaccine = 'Albendazole 4' THEN vd.vaccinated END) AS v_alb_4,
            MAX(CASE WHEN vv.vaccine = 'Rota 1' THEN vd.vaccinated END) AS v_rota_1,
            MAX(CASE WHEN vv.vaccine = 'Rota 2' THEN vd.vaccinated END) AS v_rota_2,
            MAX(CASE WHEN vv.vaccine = 'Rota 3' THEN vd.vaccinated END) AS v_rota_3,
            MAX(CASE WHEN vv.vaccine = 'DPT Booster' THEN vd.vaccinated END) AS v_dpt_b,
            MAX(CASE WHEN vv.vaccine = 'Pentavalent 1' THEN vd.vaccinated END) AS v_pent_1,
            MAX(CASE WHEN vv.vaccine = 'Pentavalent 2' THEN vd.vaccinated END) AS v_pent_2,
            MAX(CASE WHEN vv.vaccine = 'Pentavalent 3' THEN vd.vaccinated END) AS v_pent_3,
            MAX(CASE WHEN vv.vaccine = 'Measles 1 (MR)' THEN vd.vaccinated END) AS v_meas_1,
            MAX(CASE WHEN vv.vaccine = 'Measles 2 (MR)' THEN vd.vaccinated END) AS v_meas_2,
            MAX(CASE WHEN vv.vaccine = 'OPV Booster' THEN vd.vaccinated END) AS v_opv_b,
            MAX(CASE WHEN vv.vaccine = 'OPV 0' THEN vd.vaccinated END) AS v_opv_0,
            MAX(CASE WHEN vv.vaccine = 'OPV 1' THEN vd.vaccinated END) AS v_opv_1,
            MAX(CASE WHEN vv.vaccine = 'OPV 2' THEN vd.vaccinated END) AS v_opv_2,
            MAX(CASE WHEN vv.vaccine = 'OPV 3' THEN vd.vaccinated END) AS v_opv_3,
            MAX(CASE WHEN vv.vaccine = 'BCG' THEN vd.vaccinated END) AS v_bcg,
            MAX(CASE WHEN vv.vaccine = 'Hepatitis B 0' THEN vd.vaccinated END) AS v_hep_0
        FROM `tabChild Immunization` AS ci
        INNER JOIN `tabVaccine Details` AS vd ON vd.parent = ci.name
        INNER JOIN `tabVaccines` AS vv ON vv.name = vd.vaccine_id
        GROUP BY ci.childenrolledguid
    ) AS v_data ON v_data.childenrolledguid = cee.childenrollguid
"""


def get_active_vaccines(filters):
    if not filters:
        return VACCINE_LIST
        
    indicator = str(filters.get("safety_indicators", "0"))
    
    vaccine_map = {
        "1": ["IPV 1", "IPV 2", "IPV 3"],
        "2": ["Vitamin A (Dose 1)", "Vitamin A (Dose 2)", "Vitamin A (Dose 3)", "Vitamin A (Dose 4)", "Vitamin A (Dose 5)"],
        "3": ["PCV Booster"],
        "4": ["PCV 1", "PCV 2"],
        "5": ["JE 1", "JE 2"],
        "6": ["Albendazole 1", "Albendazole 2", "Albendazole 3", "Albendazole 4"],
        "7": ["Rota 1", "Rota 2", "Rota 3"],
        "8": ["DPT Booster"],
        "9": ["Pentavalent 1", "Pentavalent 2", "Pentavalent 3"],
        "10": ["Measles 1 (MR)", "Measles 2 (MR)"],
        "11": ["OPV Booster"],
        "12": ["BCG"],
        "13": ["Hepatitis B 0"]
    }
    
    return vaccine_map.get(indicator, VACCINE_LIST)

def execute(filters=None):
    if not filters:
        filters = {}
    columns = get_columns(filters)
    data = get_summary_data(filters)
    return columns, data

def get_columns(filters=None):
    filters = filters or {}
    level = str(filters.get("level", ""))
    active_vaccines = get_active_vaccines(filters)

    if not level or level == "8":
        columns = [
            {"label": "Partner", "fieldname": "Partner", "fieldtype": "Data" ,"width": 120},
            {"label": "State", "fieldname": "State", "fieldtype": "Data","width": 120},
            {"label": "District", "fieldname": "District", "fieldtype": "Data","width": 120},
            {"label": "Block", "fieldname": "Block", "fieldtype": "Data","width": 120},
            {"label": "Gram Panchayat", "fieldname": "Gram Panchayat", "fieldtype": "Data","width": 150},
            {"label": "Supervisor", "fieldname": "Supervisor", "fieldtype": "Data","width": 150},
            {"label": "Creche ID", "fieldname": "Creche ID", "fieldtype": "Data","width": 150},
            {"label": "Creche", "fieldname": "Creche", "fieldtype": "Data","width": 150},
            {"label": "Child ID", "fieldname": "Child ID", "fieldtype": "Data","width": 150},
            {"label": "Child Name", "fieldname": "Child Name", "fieldtype": "Data","width": 160},
            {"label": "Current Age (In Months)", "fieldname": "Current Age (In Months)", "fieldtype": "Data","width": 200},
        ]
        for vaccine in active_vaccines:
            columns.append({"label": vaccine, "fieldname": vaccine, "fieldtype": "Data","width": 330})
        return columns

    columns = []
    group_by_cols = []
    
    if level == "1": group_by_cols = ["Partner"]
    elif level == "2": group_by_cols = ["State"] 
    elif level == "3": group_by_cols = ["Partner", "State", "District"]
    elif level == "4": group_by_cols = ["Partner", "State", "District", "Block"]
    elif level == "5": group_by_cols = ["Partner", "State", "District", "Block", "Supervisor"]
    elif level == "6": group_by_cols = ["Partner", "State", "District", "Block", "Gram Panchayat", "Supervisor"]
    elif level == "7": group_by_cols = ["Partner", "State", "District", "Block", "Gram Panchayat", "Supervisor", "Creche"]

    for col in group_by_cols:
        columns.append({"label": col, "fieldname": col, "fieldtype": "Data","width": 220})

    if level != "7":
        columns.append({"label": "No of Creche", "fieldname": "No of Creche", "fieldtype": "Data","width": 160	})

    columns.append({"label": "Enrolled Children", "fieldname": "Enrolled Children", "fieldtype": "Data","width": 170})

    for vaccine in active_vaccines:
        columns.append({
            "label": f"{vaccine} Vaccinated (Eligible)",
            "fieldname": vaccine,
            "fieldtype": "Data",
            "width": 330
        })

    return columns

def _build_conditions(filters):
    """Build the shared WHERE conditions + params used by both the main report
    query and the detail-popup query, so the two never diverge.

    Returns: (conditions list, params dict, start_date, end_date)
    """
    month = int(filters.get("month") if filters.get("month") else nowdate().split('-')[1])
    year = int(filters.get("year") if filters.get("year") else nowdate().split('-')[0])
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "partner": None,
        "state": None,
        "district": None,
        "block": None,
        "gp": None,
        "creche": None,
        "band": None,
        "supervisor_id": None,
        "creche_status_id": None,
        "phases": None,
        "cstart_date": None,
        "cend_date": None,
        "creche_age": None
    }

    range_type = filters.get("cr_opening_range_type")
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            params['cstart_date'], params['cend_date'] = date_range
        elif range_type == "before" and single_date:
            params['cstart_date'] = date(2017, 1, 1)
            params['cend_date'] = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            params['cstart_date'] = single_date + timedelta(days=1)
            params['cend_date'] = date.today()
        elif range_type == "equal" and single_date:
            params['cstart_date'] = single_date

    if partner_id: params["partner"] = partner_id
    
    if filters.get("state"):
        params["state"] = filters.get("state")
    else:
        state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
        if state_ids: params["state_ids"] = ",".join(state_ids)

    if filters.get("district"):
        params["district"] = filters.get("district")
    else:
        district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
        if district_ids: params["district_ids"] = ",".join(district_ids)

    if filters.get("block"):
        params["block"] = filters.get("block")
    else:
        block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
        if block_ids: params["block_ids"] = ",".join(block_ids)

    if filters.get("gp"):
        params["gp"] = filters.get("gp")
    else:
        gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]
        if gp_ids: params["gp_ids"] = ",".join(gp_ids)

    if filters.get("creche"): params["creche"] = filters.get("creche")
    if filters.get("band"): params["band"] = filters.get("band")
    if filters.get("supervisor_id"): params["supervisor_id"] = filters.get("supervisor_id")
    if filters.get("creche_status_id"): params["creche_status_id"] = filters.get("creche_status_id")
    
    if filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())  
        if phases_cleaned:  
            params["phases"] = phases_cleaned

    creche_age = filters.get("creche_age", "")
    params["creche_age"] = creche_age

    conditions = []
    
    if params.get("partner"): conditions.append("c.partner_id = %(partner)s")
    if params.get("state"): conditions.append("c.state_id = %(state)s")
    elif params.get("state_ids"): conditions.append("FIND_IN_SET(c.state_id, %(state_ids)s)")
    if params.get("district"): conditions.append("c.district_id = %(district)s")
    elif params.get("district_ids"): conditions.append("FIND_IN_SET(c.district_id, %(district_ids)s)")
    if params.get("block"): conditions.append("c.block_id = %(block)s")
    elif params.get("block_ids"): conditions.append("FIND_IN_SET(c.block_id, %(block_ids)s)")
    if params.get("gp"): conditions.append("c.gp_id = %(gp)s")
    elif params.get("gp_ids"): conditions.append("FIND_IN_SET(c.gp_id, %(gp_ids)s)")
    if params.get("creche"): conditions.append("c.name = %(creche)s")
    if params.get("supervisor_id"): conditions.append("c.supervisor_id = %(supervisor_id)s")
    if params.get("creche_status_id"): conditions.append("c.creche_status_id = %(creche_status_id)s")
    if params.get("phases"): conditions.append("FIND_IN_SET(c.phase, %(phases)s)")

    if params.get("cstart_date") and params.get("cend_date"):
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
    elif params.get("cstart_date"): 
        conditions.append("DATE(c.creche_opening_date) = %(cstart_date)s")

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

    # Match dashboard: only count creches/children whose creche opened on or before
    # the end of the selected month (or has no opening date yet).
    conditions.append("""
        (
            c.creche_opening_date IS NULL
            OR c.creche_opening_date <= %(end_date)s
        )
    """)

    # The above are all creche-level (geo/partner/status/phase/opening) filters.
    # The enrollment-window condition below only applies to enrollment-based
    # queries (children / the main vaccine query), NOT to the creche count.
    enrollment_window = """
        (
            (cee.date_of_exit BETWEEN %(start_date)s AND %(end_date)s)
            OR
            (
                cee.date_of_enrollment <= %(end_date)s
                AND (
                    cee.date_of_exit IS NULL
                    OR cee.date_of_exit >= %(end_date)s
                )
            )
        )
    """

    return conditions, params, start_date, end_date, enrollment_window


# Maps a group column display label to (alias.column) used for SELECT/GROUP BY
# in the dashboard-matching count queries.
_GROUP_COL_SELECT = {
    "Partner": "p.partner_name",
    "State": "s.state_name",
    "District": "d.district_name",
    "Block": "b.block_name",
    "Gram Panchayat": "gp.gp_name",
    "Supervisor": "u.full_name",
    "Creche": "c.creche_name",
}

_COUNT_JOINS = """
    LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
    LEFT JOIN `tabPartner` AS p ON p.name = c.partner_id
    LEFT JOIN `tabState` AS s ON s.name = c.state_id
    LEFT JOIN `tabDistrict` AS d ON d.name = c.district_id
    LEFT JOIN `tabBlock` AS b ON b.name = c.block_id
    LEFT JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id
"""


def _get_dashboard_counts(filters, group_by_cols):
    """Compute 'No of Creche' and 'Enrolled Children' counts using the SAME
    logic as the dashboard (creche_no / enrolled_children), grouped by the
    report level's columns.

    Returns: (creche_by_group, child_by_group, total_creches, total_children)
    where *_by_group are dicts keyed by a tuple of group display values.
    """
    conditions, params, _s, _e, enrollment_window = _build_conditions(filters)

    select_cols = ", ".join(_GROUP_COL_SELECT[c] for c in group_by_cols) if group_by_cols else ""
    group_clause = f"GROUP BY {select_cols}" if select_cols else ""
    select_prefix = (select_cols + ", ") if select_cols else ""

    creche_where = " AND ".join(conditions) if conditions else "1=1"
    child_where = " AND ".join(conditions + [enrollment_window]) if conditions else "1=1"

    # --- No of Creche (straight from tabCreche, no enrolled-children requirement) ---
    creche_sql = f"""
        SELECT {select_prefix} COUNT(DISTINCT c.name) AS cnt
        FROM `tabCreche` AS c
        {_COUNT_JOINS}
        WHERE {creche_where}
        {group_clause}
    """

    # --- Enrolled Children (distinct enrollment records within the window) ---
    child_sql = f"""
        SELECT {select_prefix} COUNT(DISTINCT cee.name) AS cnt
        FROM `tabChild Enrollment and Exit` AS cee
        LEFT JOIN `tabCreche` AS c ON c.name = cee.creche_id
        {_COUNT_JOINS}
        WHERE {child_where}
        {group_clause}
    """

    creche_rows = frappe.db.sql(creche_sql, params, as_dict=False)
    child_rows = frappe.db.sql(child_sql, params, as_dict=False)

    n = len(group_by_cols)

    def to_map(rows):
        m = {}
        total = 0
        for r in rows:
            key = tuple(str(r[i] or "") for i in range(n))
            cnt = r[n] or 0
            m[key] = cnt
            total += cnt
        return m, total

    creche_by_group, total_creches = to_map(creche_rows)
    child_by_group, total_children = to_map(child_rows)

    return creche_by_group, child_by_group, total_creches, total_children


@frappe.whitelist()
def get_summary_data(filters=None):
    if not filters:
        filters = {}

    conditions, params, start_date, end_date, enrollment_window = _build_conditions(filters)
    # The main vaccine query is enrollment-based, so it includes the window.
    where_clause = " AND ".join(conditions + [enrollment_window]) if conditions else "1=1"

    # OPTIMIZED SQL: We resolve the vaccines in a compact subquery first to stop row multiplication
    sql_query = f"""
        SELECT 
            p.partner_name AS "Partner",
            s.state_name AS "State",
            d.district_name AS "District",
            b.block_name AS "Block",
            gp.gp_name AS "Gram Panchayat",
            u.full_name AS "Supervisor",
            c.creche_id AS "Creche ID",
            c.creche_name AS "Creche",
            cee.name AS "Enrollment ID",
            cee.child_id AS "Child ID",
            cee.child_name AS "Child Name",
            
            CAST(TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS CHAR) AS "Current Age (In Months)",

            -- Vaccine Status Output
            IFNULL(CASE WHEN v_data.v_ipv_1 = 1 THEN 'Yes' WHEN v_data.v_ipv_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 42 THEN 'Overdue' ELSE 'Not Eligible' END) AS "IPV 1",
            IFNULL(CASE WHEN v_data.v_ipv_2 = 1 THEN 'Yes' WHEN v_data.v_ipv_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 98 THEN 'Overdue' ELSE 'Not Eligible' END) AS "IPV 2",
            IFNULL(CASE WHEN v_data.v_ipv_3 = 1 THEN 'Yes' WHEN v_data.v_ipv_3 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 270 THEN 'Overdue' ELSE 'Not Eligible' END) AS "IPV 3",

            IFNULL(CASE WHEN v_data.v_vit_1 = 1 THEN 'Yes' WHEN v_data.v_vit_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 270 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Vitamin A (Dose 1)",
            IFNULL(CASE WHEN v_data.v_vit_2 = 1 THEN 'Yes' WHEN v_data.v_vit_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 540 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Vitamin A (Dose 2)",
            IFNULL(CASE WHEN v_data.v_vit_3 = 1 THEN 'Yes' WHEN v_data.v_vit_3 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 720 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Vitamin A (Dose 3)",
            IFNULL(CASE WHEN v_data.v_vit_4 = 1 THEN 'Yes' WHEN v_data.v_vit_4 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 900 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Vitamin A (Dose 4)",
            IFNULL(CASE WHEN v_data.v_vit_5 = 1 THEN 'Yes' WHEN v_data.v_vit_5 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 1080 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Vitamin A (Dose 5)",

            IFNULL(CASE WHEN v_data.v_pcv_b = 1 THEN 'Yes' WHEN v_data.v_pcv_b = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 270 THEN 'Overdue' ELSE 'Not Eligible' END) AS "PCV Booster",
            IFNULL(CASE WHEN v_data.v_pcv_1 = 1 THEN 'Yes' WHEN v_data.v_pcv_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 42 THEN 'Overdue' ELSE 'Not Eligible' END) AS "PCV 1",
            IFNULL(CASE WHEN v_data.v_pcv_2 = 1 THEN 'Yes' WHEN v_data.v_pcv_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 98 THEN 'Overdue' ELSE 'Not Eligible' END) AS "PCV 2",

            IFNULL(CASE WHEN v_data.v_je_1 = 1 THEN 'Yes' WHEN v_data.v_je_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 270 THEN 'Overdue' ELSE 'Not Eligible' END) AS "JE 1",
            IFNULL(CASE WHEN v_data.v_je_2 = 1 THEN 'Yes' WHEN v_data.v_je_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 480 THEN 'Overdue' ELSE 'Not Eligible' END) AS "JE 2",

            IFNULL(CASE WHEN v_data.v_alb_1 = 1 THEN 'Yes' WHEN v_data.v_alb_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 540 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Albendazole 1",
            IFNULL(CASE WHEN v_data.v_alb_2 = 1 THEN 'Yes' WHEN v_data.v_alb_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 720 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Albendazole 2",
            IFNULL(CASE WHEN v_data.v_alb_3 = 1 THEN 'Yes' WHEN v_data.v_alb_3 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 900 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Albendazole 3",
            IFNULL(CASE WHEN v_data.v_alb_4 = 1 THEN 'Yes' WHEN v_data.v_alb_4 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 1080 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Albendazole 4",

            IFNULL(CASE WHEN v_data.v_rota_1 = 1 THEN 'Yes' WHEN v_data.v_rota_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 42 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Rota 1",
            IFNULL(CASE WHEN v_data.v_rota_2 = 1 THEN 'Yes' WHEN v_data.v_rota_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 70 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Rota 2",
            IFNULL(CASE WHEN v_data.v_rota_3 = 1 THEN 'Yes' WHEN v_data.v_rota_3 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 98 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Rota 3",

            IFNULL(CASE WHEN v_data.v_dpt_b = 1 THEN 'Yes' WHEN v_data.v_dpt_b = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 480 THEN 'Overdue' ELSE 'Not Eligible' END) AS "DPT Booster",
            IFNULL(CASE WHEN v_data.v_pent_1 = 1 THEN 'Yes' WHEN v_data.v_pent_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 42 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Pentavalent 1",
            IFNULL(CASE WHEN v_data.v_pent_2 = 1 THEN 'Yes' WHEN v_data.v_pent_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 70 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Pentavalent 2",
            IFNULL(CASE WHEN v_data.v_pent_3 = 1 THEN 'Yes' WHEN v_data.v_pent_3 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 98 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Pentavalent 3",

            IFNULL(CASE WHEN v_data.v_meas_1 = 1 THEN 'Yes' WHEN v_data.v_meas_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 270 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Measles 1 (MR)",
            IFNULL(CASE WHEN v_data.v_meas_2 = 1 THEN 'Yes' WHEN v_data.v_meas_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 480 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Measles 2 (MR)",

            IFNULL(CASE WHEN v_data.v_opv_b = 1 THEN 'Yes' WHEN v_data.v_opv_b = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 480 THEN 'Overdue' ELSE 'Not Eligible' END) AS "OPV Booster",
            IFNULL(CASE WHEN v_data.v_opv_0 = 1 THEN 'Yes' WHEN v_data.v_opv_0 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 0 THEN 'Overdue' ELSE 'Not Eligible' END) AS "OPV 0",
            IFNULL(CASE WHEN v_data.v_opv_1 = 1 THEN 'Yes' WHEN v_data.v_opv_1 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 42 THEN 'Overdue' ELSE 'Not Eligible' END) AS "OPV 1",
            IFNULL(CASE WHEN v_data.v_opv_2 = 1 THEN 'Yes' WHEN v_data.v_opv_2 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 70 THEN 'Overdue' ELSE 'Not Eligible' END) AS "OPV 2",
            IFNULL(CASE WHEN v_data.v_opv_3 = 1 THEN 'Yes' WHEN v_data.v_opv_3 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 98 THEN 'Overdue' ELSE 'Not Eligible' END) AS "OPV 3",

            IFNULL(CASE WHEN v_data.v_bcg = 1 THEN 'Yes' WHEN v_data.v_bcg = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 0 THEN 'Overdue' ELSE 'Not Eligible' END) AS "BCG",
            IFNULL(CASE WHEN v_data.v_hep_0 = 1 THEN 'Yes' WHEN v_data.v_hep_0 = 0 THEN 'No' END, CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= 0 THEN 'Overdue' ELSE 'Not Eligible' END) AS "Hepatitis B 0"

        FROM `tabChild Enrollment and Exit` AS cee
        LEFT JOIN `tabCreche` AS c ON c.name = cee.creche_id
        LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
        LEFT JOIN `tabPartner` AS p ON p.name = c.partner_id
        LEFT JOIN `tabState` AS s ON s.name = c.state_id
        LEFT JOIN `tabDistrict` AS d  ON d.name = c.district_id
        LEFT JOIN `tabBlock` AS b  ON b.name = c.block_id
        LEFT JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id
        
        -- The isolated vaccine subquery keeps row limits purely 1:1 with children
        LEFT JOIN (
            SELECT
                ci.childenrolledguid,
                MAX(CASE WHEN vv.vaccine = 'IPV 1' THEN vd.vaccinated END) AS v_ipv_1,
                MAX(CASE WHEN vv.vaccine = 'IPV 2' THEN vd.vaccinated END) AS v_ipv_2,
                MAX(CASE WHEN vv.vaccine = 'IPV 3' THEN vd.vaccinated END) AS v_ipv_3,
                MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 1)' THEN vd.vaccinated END) AS v_vit_1,
                MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 2)' THEN vd.vaccinated END) AS v_vit_2,
                MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 3)' THEN vd.vaccinated END) AS v_vit_3,
                MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 4)' THEN vd.vaccinated END) AS v_vit_4,
                MAX(CASE WHEN vv.vaccine = 'Vitamin A (Dose 5)' THEN vd.vaccinated END) AS v_vit_5,
                MAX(CASE WHEN vv.vaccine = 'PCV Booster' THEN vd.vaccinated END) AS v_pcv_b,
                MAX(CASE WHEN vv.vaccine = 'PCV 1' THEN vd.vaccinated END) AS v_pcv_1,
                MAX(CASE WHEN vv.vaccine = 'PCV 2' THEN vd.vaccinated END) AS v_pcv_2,
                MAX(CASE WHEN vv.vaccine = 'JE 1' THEN vd.vaccinated END) AS v_je_1,
                MAX(CASE WHEN vv.vaccine = 'JE 2' THEN vd.vaccinated END) AS v_je_2,
                MAX(CASE WHEN vv.vaccine = 'Albendazole 1' THEN vd.vaccinated END) AS v_alb_1,
                MAX(CASE WHEN vv.vaccine = 'Albendazole 2' THEN vd.vaccinated END) AS v_alb_2,
                MAX(CASE WHEN vv.vaccine = 'Albendazole 3' THEN vd.vaccinated END) AS v_alb_3,
                MAX(CASE WHEN vv.vaccine = 'Albendazole 4' THEN vd.vaccinated END) AS v_alb_4,
                MAX(CASE WHEN vv.vaccine = 'Rota 1' THEN vd.vaccinated END) AS v_rota_1,
                MAX(CASE WHEN vv.vaccine = 'Rota 2' THEN vd.vaccinated END) AS v_rota_2,
                MAX(CASE WHEN vv.vaccine = 'Rota 3' THEN vd.vaccinated END) AS v_rota_3,
                MAX(CASE WHEN vv.vaccine = 'DPT Booster' THEN vd.vaccinated END) AS v_dpt_b,
                MAX(CASE WHEN vv.vaccine = 'Pentavalent 1' THEN vd.vaccinated END) AS v_pent_1,
                MAX(CASE WHEN vv.vaccine = 'Pentavalent 2' THEN vd.vaccinated END) AS v_pent_2,
                MAX(CASE WHEN vv.vaccine = 'Pentavalent 3' THEN vd.vaccinated END) AS v_pent_3,
                MAX(CASE WHEN vv.vaccine = 'Measles 1 (MR)' THEN vd.vaccinated END) AS v_meas_1,
                MAX(CASE WHEN vv.vaccine = 'Measles 2 (MR)' THEN vd.vaccinated END) AS v_meas_2,
                MAX(CASE WHEN vv.vaccine = 'OPV Booster' THEN vd.vaccinated END) AS v_opv_b,
                MAX(CASE WHEN vv.vaccine = 'OPV 0' THEN vd.vaccinated END) AS v_opv_0,
                MAX(CASE WHEN vv.vaccine = 'OPV 1' THEN vd.vaccinated END) AS v_opv_1,
                MAX(CASE WHEN vv.vaccine = 'OPV 2' THEN vd.vaccinated END) AS v_opv_2,
                MAX(CASE WHEN vv.vaccine = 'OPV 3' THEN vd.vaccinated END) AS v_opv_3,
                MAX(CASE WHEN vv.vaccine = 'BCG' THEN vd.vaccinated END) AS v_bcg,
                MAX(CASE WHEN vv.vaccine = 'Hepatitis B 0' THEN vd.vaccinated END) AS v_hep_0
            FROM `tabChild Immunization` AS ci
            INNER JOIN `tabVaccine Details` AS vd ON vd.parent = ci.name
            INNER JOIN `tabVaccines` AS vv ON vv.name = vd.vaccine_id
            GROUP BY ci.childenrolledguid
        ) AS v_data ON v_data.childenrolledguid = cee.childenrollguid
        
        WHERE {where_clause}
    """

    raw_data = frappe.db.sql(sql_query, params, as_dict=True)
    active_vaccines = get_active_vaccines(filters)
    level = str(filters.get("level", ""))

    if not raw_data:
        return []

    # --- SINGLE PASS OPTIMIZATION FOR TOTALS ---
    totals_agg = {vac: {"yes": 0, "no": 0, "not_elig": 0, "overdue": 0} for vac in active_vaccines}
    total_creches = set()
    total_children = set()

    for row in raw_data:
        if row.get("Creche ID"): total_creches.add(row.get("Creche ID"))
        # Match dashboard: Enrolled Children = COUNT(DISTINCT enrollment record)
        if row.get("Enrollment ID"): total_children.add(row.get("Enrollment ID"))
        
        for vac in active_vaccines:
            val = row.get(vac)
            if val == "Yes": totals_agg[vac]["yes"] += 1
            elif val == "No": totals_agg[vac]["no"] += 1
            elif val == "Not Eligible": totals_agg[vac]["not_elig"] += 1
            elif val == "Overdue": totals_agg[vac]["overdue"] += 1

    # --- IF NO LEVEL OR LEVEL 8 (CHILD) IS SELECTED: RETURN DETAILED ROW VIEW ---
    if not level or level == "8":
        # Use dashboard-matching grand totals for the Total row.
        _, _, dash_total_creches, dash_total_children = _get_dashboard_counts(filters, [])
        summary_row = {
            "Partner": "<b><span style='color:black;'>Total</span></b>",
            "State": "", "District": "", "Block": "", "Gram Panchayat": "",
            "Supervisor": "", "Creche ID": "",
            "Creche": f"<b><span style='color:black;'>Total: {dash_total_creches}</span></b>",
            "Enrollment ID": "", "Child ID": "",
            "Child Name": f"<b><span style='color:black;'>Total: {dash_total_children}</span></b>",
            "Current Age (In Months)": ""
        }

        for vaccine in active_vaccines:
            st = totals_agg[vaccine]
            summary_row[vaccine] = f"<b><span style='color:black;'>Yes:{st['yes']} | No:{st['no']} | Not Elig:{st['not_elig']} | Overdue:{st['overdue']}</span></b>"

        raw_data.append(summary_row)
        return raw_data

    # --- IF LEVEL 1-7 SELECTED: PROCESS AGGREGATION IN PYTHON ---
    group_by_cols = []
    if level == "1": group_by_cols = ["Partner"]
    elif level == "2": group_by_cols = ["State"]
    elif level == "3": group_by_cols = ["Partner", "State", "District"]
    elif level == "4": group_by_cols = ["Partner", "State", "District", "Block"]
    elif level == "5": group_by_cols = ["Partner", "State", "District", "Block", "Supervisor"]
    elif level == "6": group_by_cols = ["Partner", "State", "District", "Block", "Gram Panchayat", "Supervisor"]
    elif level == "7": group_by_cols = ["Partner", "State", "District", "Block", "Gram Panchayat", "Supervisor", "Creche"]

    # Dashboard-matching counts for No of Creche / Enrolled Children, keyed by
    # the same group tuple the report builds below.
    creche_by_group, child_by_group, dash_total_creches, dash_total_children = \
        _get_dashboard_counts(filters, group_by_cols)

    grouped_data = {}

    # Process grouping in single pass
    for row in raw_data:
        key_values = [str(row.get(col) or "") for col in group_by_cols]
        key = tuple(key_values)
        
        if key not in grouped_data:
            grouped_data[key] = {col: row.get(col) for col in group_by_cols}
            grouped_data[key]["creches"] = set()
            grouped_data[key]["children"] = set()
            for vac in active_vaccines:
                grouped_data[key][f"{vac}_vac"] = 0
                grouped_data[key][f"{vac}_elig"] = 0

        grouped_data[key]["creches"].add(row.get("Creche ID"))
        grouped_data[key]["children"].add(row.get("Enrollment ID"))
        
        for vac in active_vaccines:
            status = row.get(vac)
            if status in ["Yes", "No", "Overdue"]:
                grouped_data[key][f"{vac}_elig"] += 1
                if status == "Yes":
                    grouped_data[key][f"{vac}_vac"] += 1

    final_data = []
    for key, agg in grouped_data.items():
        out_row = {col: agg[col] for col in group_by_cols}

        # Context describing exactly which group this row represents, so the
        # detail popup can re-query the same subset.
        row_ctx = {col: (agg[col] or "") for col in group_by_cols}
        group_key = tuple(str(agg[col] or "") for col in group_by_cols)

        if level != "7":
            # Dashboard-matching creche count (falls back to children-derived
            # set only if the count query returns nothing for this group).
            creche_cnt = creche_by_group.get(group_key, len(agg["creches"]))
            out_row["No of Creche"] = _clickable_count(
                creche_cnt, "creches", level, row_ctx
            )

        child_cnt = child_by_group.get(group_key, len(agg["children"]))
        out_row["Enrolled Children"] = _clickable_count(
            child_cnt, "children", level, row_ctx
        )

        for vac in active_vaccines:
            label = f"{agg[f'{vac}_vac']}({agg[f'{vac}_elig']})"
            out_row[vac] = _clickable_count(
                label, "vaccine", level, row_ctx, extra={"vaccine": vac}
            )

        final_data.append(out_row)

    # --- AGGREGATED TOTAL SUMMARY ROW ---
    summary_row = {col: "" for col in group_by_cols}
    summary_row[group_by_cols[0]] = "<b><span style='color:black;'>Total</span></b>" 
    
    if level != "7":
        summary_row["No of Creche"] = _clickable_count(
            dash_total_creches, "creches", level, {}, bold=True
        )
    summary_row["Enrolled Children"] = _clickable_count(
        dash_total_children, "children", level, {}, bold=True
    )

    for vac in active_vaccines:
        st = totals_agg[vac]
        t_vac = st["yes"]
        t_elig = st["yes"] + st["no"] + st["overdue"]
        summary_row[vac] = _clickable_count(
            f"{t_vac}({t_elig})", "vaccine", level, {}, bold=True, extra={"vaccine": vac}
        )

    final_data.append(summary_row)
    
    return final_data


# Maps the display label of each group column to the SQL expression used to
# narrow the detail query down to exactly the clicked row's group.
_GROUP_COL_SQL = {
    "Partner": "p.partner_name",
    "State": "s.state_name",
    "District": "d.district_name",
    "Block": "b.block_name",
    "Gram Panchayat": "gp.gp_name",
    "Supervisor": "u.full_name",
    "Creche": "c.creche_name",
}


@frappe.whitelist()
def get_count_details(filters=None, ctx=None):
    """Return the detailed records behind a clicked count cell.

    filters : the current report filters (same dict the report runs with)
    ctx     : {"metric": "creches"|"children", "level": str, "group": {label: value}}

    Returns: {"metric", "title", "columns", "rows", "total"}
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    if isinstance(ctx, str):
        ctx = json.loads(ctx)
    filters = filters or {}
    ctx = ctx or {}

    metric = ctx.get("metric", "children")
    group = ctx.get("group", {}) or {}
    vac_filter = None

    conditions, params, _start, _end, enrollment_window = _build_conditions(filters)

    # Narrow to the clicked row's group (e.g. a specific State + District).
    for idx, (label, value) in enumerate(group.items()):
        col_sql = _GROUP_COL_SQL.get(label)
        if not col_sql:
            continue
        pkey = f"grp_{idx}"
        if value == "":
            conditions.append(f"({col_sql} IS NULL OR {col_sql} = '')")
        else:
            conditions.append(f"{col_sql} = %({pkey})s")
            params[pkey] = value

    base_join = """
        LEFT JOIN `tabUser` AS u ON u.name = c.supervisor_id
        LEFT JOIN `tabPartner` AS p ON p.name = c.partner_id
        LEFT JOIN `tabState` AS s ON s.name = c.state_id
        LEFT JOIN `tabDistrict` AS d ON d.name = c.district_id
        LEFT JOIN `tabBlock` AS b ON b.name = c.block_id
        LEFT JOIN `tabGram Panchayat` AS gp ON gp.name = c.gp_id
    """

    if metric == "vaccine":
        # Child records for the group, showing the selected vaccine's status.
        vaccine = ctx.get("vaccine")
        vinfo = VACCINE_STATUS_MAP.get(vaccine)
        if not vinfo:
            return {"metric": metric, "title": "Details", "columns": [], "rows": [], "total": 0}
        vcol, vdays = vinfo
        params["v_days"] = vdays

        # Popup sub-filter: "vaccinated" (got the vaccine) or "eligible"
        # (eligible denominator = Yes/No/Overdue). Defaults to "vaccinated".
        vac_filter = str(ctx.get("vac_filter", "vaccinated")).lower()
        if vac_filter not in ("vaccinated", "eligible", "not_vaccinated"):
            vac_filter = "vaccinated"

        status_expr = f"""
            IFNULL(
                CASE WHEN v_data.{vcol} = 1 THEN 'Yes' WHEN v_data.{vcol} = 0 THEN 'No' END,
                CASE WHEN TIMESTAMPDIFF(DAY, cee.child_dob, %(end_date)s) >= %(v_days)s
                     THEN 'Overdue' ELSE 'Not Eligible' END
            )
        """

        # Restrict rows to match the clicked cell's "Vaccinated(Eligible)" numbers:
        #   vaccinated -> Status = 'Yes'          (the first number)
        #   eligible   -> Status IN Yes/No/Overdue (the parenthesised number)
        if vac_filter == "vaccinated":
            status_having = "HAVING `Status` = 'Yes'"
        elif vac_filter == "not_vaccinated":
            status_having = "HAVING `Status` IN ('No', 'Overdue')"
        else:
            status_having = "HAVING `Status` IN ('Yes', 'No', 'Overdue')"

        where_clause = " AND ".join(conditions + [enrollment_window]) if conditions else "1=1"
        sql = f"""
            SELECT
                p.partner_name     AS "Partner",
                s.state_name       AS "State",
                d.district_name    AS "District",
                b.block_name       AS "Block",
                gp.gp_name         AS "Gram Panchayat",
                c.creche_name      AS "Creche Name",
                c.creche_id        AS "Creche ID",
                cee.child_name     AS "Child Name",
                cee.child_id       AS "Child ID",
                CAST(TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS CHAR) AS "Age (Months)",
                {status_expr}      AS "Status"
            FROM `tabChild Enrollment and Exit` AS cee
            LEFT JOIN `tabCreche` AS c ON c.name = cee.creche_id
            {base_join}
            {_VACCINE_SUBQUERY}
            WHERE {where_clause}
            GROUP BY cee.name
            {status_having}
            ORDER BY cee.child_name
        """
        columns = [
            "Partner", "State", "District", "Block", "Gram Panchayat",
            "Creche Name", "Creche ID", "Child Name", "Child ID",
            "Age (Months)", "Status",
        ]
        if vac_filter == "vaccinated":
            vac_label = "Vaccinated"
        elif vac_filter == "not_vaccinated":
            vac_label = "Not Vaccinated"
        else:
            vac_label = "Eligible"
        title = f"{vaccine} — {vac_label} Children"
    elif metric == "creches":
        # Matches dashboard creche_no: count creches straight from tabCreche,
        # WITHOUT requiring enrolled children (no enrollment-window filter).
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"""
            SELECT
                c.creche_id        AS "Creche ID",
                c.creche_name      AS "Creche Name",
                p.partner_name     AS "Partner",
                s.state_name       AS "State",
                d.district_name    AS "District",
                b.block_name       AS "Block",
                gp.gp_name         AS "Gram Panchayat",
                u.full_name        AS "Supervisor"
            FROM `tabCreche` AS c
            {base_join}
            WHERE {where_clause}
            GROUP BY c.name
            ORDER BY c.creche_name
        """
        columns = [
            "Creche ID", "Creche Name", "Partner", "State",
            "District", "Block", "Gram Panchayat", "Supervisor",
        ]
        title = "Creche Details"
    else:
        # Matches dashboard enrolled_children: one row per distinct enrollment
        # record within the enrollment window.
        where_clause = " AND ".join(conditions + [enrollment_window]) if conditions else "1=1"
        sql = f"""
            SELECT
                cee.child_id       AS "Child ID",
                cee.child_name     AS "Child Name",
                c.creche_id        AS "Creche ID",
                c.creche_name      AS "Creche Name",
                CAST(TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date)s) AS CHAR) AS "Age (Months)",
                cee.date_of_enrollment AS "Enrolled On",
                p.partner_name     AS "Partner",
                s.state_name       AS "State",
                d.district_name    AS "District",
                b.block_name       AS "Block",
                gp.gp_name         AS "Gram Panchayat"
            FROM `tabChild Enrollment and Exit` AS cee
            LEFT JOIN `tabCreche` AS c ON c.name = cee.creche_id
            {base_join}
            WHERE {where_clause}
            GROUP BY cee.name
            ORDER BY cee.child_name
        """
        columns = [
            "Child ID", "Child Name", "Creche ID", "Creche Name",
            "Age (Months)", "Enrolled On", "Partner", "State",
            "District", "Block", "Gram Panchayat",
        ]
        title = "Child Details"

    rows = frappe.db.sql(sql, params, as_dict=True)

    return {
        "metric": metric,
        "title": title,
        "columns": columns,
        "rows": rows,
        "total": len(rows),
        "vac_filter": vac_filter if metric == "vaccine" else None,
        "vaccine": ctx.get("vaccine") if metric == "vaccine" else None,
    }


@frappe.whitelist()
def download_count_details_xlsx(filters=None, ctx=None):
    """Build and stream the popup's detail records as a real .xlsx file.

    Re-runs get_count_details with the same args so the export always matches
    the popup (including the Vaccinated/Eligible sub-filter and group).
    """
    from frappe.utils.xlsxutils import make_xlsx

    result = get_count_details(filters=filters, ctx=ctx)
    columns = result.get("columns", [])
    rows = result.get("rows", [])
    title = result.get("title") or "Details"

    # Header row + data rows as a list of lists.
    data = [columns]
    for row in rows:
        data.append([row.get(col, "") for col in columns])

    xlsx_file = make_xlsx(data, "Details")

    safe_name = "".join(ch for ch in title if ch.isalnum() or ch in " -_").strip() or "details"

    frappe.response["filename"] = f"{safe_name}.xlsx"
    frappe.response["filecontent"] = xlsx_file.getvalue()
    frappe.response["type"] = "binary"


