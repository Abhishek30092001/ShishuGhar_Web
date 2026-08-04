import frappe
from frappe import _
from datetime import datetime, date, timedelta
import calendar


def execute(filters=None):
    try:
        selected_level = filters.get("level", "7")
        selected_indicator = filters.get("indicator", "weight_for_age")

        level_mapping = {
            "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
            "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
            "3": [
                {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
                {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
            ],
            "4": [
                {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
                {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
                {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
            ],
            "5": [
                {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
                {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
                {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
                {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
            ],
            "6": [
                {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
                {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
                {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
                {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
            ],
            "7": [
                {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
                {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
                {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
                {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
                {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
                {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
                {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
                {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
            ],
            "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
            "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
            "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
            "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
            "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
            "13": [{"label": "Attendance", "fieldname": "attendance_slab", "fieldtype": "Data", "width": 220}],
        }

        variable_columns = level_mapping.get(selected_level, level_mapping["7"])

        fixed_columns = [
            {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
            {"label": "Total Universe (Measured Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 290},
            {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
            {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
            {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
            # {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
            {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
            {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
            {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
            {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
            {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
            {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
            {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
            {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
            {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
            {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
            {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
            {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
            {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
            {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
        ]

        # Add Operational Creches column only for geographical levels (1-7)
        if selected_level not in ["8", "9", "10", "11", "12", "13"]:
            fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

        columns = variable_columns + fixed_columns
        data = get_report_data(filters)

        # Calculate totals row
        if data:
            totals_row = calculate_totals_row(data, filters, variable_columns)
            data.append(totals_row)

        return columns, data

    except Exception as e:
        frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
        frappe.throw(_(f"Error in report: {str(e)}"))
        return [], []


def calculate_totals_row(data, filters, variable_columns):
    selected_level = filters.get("level", "7")

    totals_row = {'is_total': True, 'indent': 0}

    # Set label for totals row
    level_field_map = {
        "1": "partner", "2": "state", "3": "district",
        "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
        "8": "creche_age",
        "9": "gender",
        "10": "age_group",
        "11": "age_at_enrollment",
        "12": "tenure_bucket",
        "13": "attendance_slab",
    }

    if selected_level in level_field_map:
        totals_row[level_field_map[selected_level]] = "Total"
    else:
        for col in variable_columns:
            totals_row[col['fieldname']] = "Total"

    # Include all numeric columns
    total_keys = [
        'operational_creches', 'enrolled_children', 'measured_twice',
        'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
        'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
        'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
    ]

    totals = {k: 0 for k in total_keys}
    for row in data:
        for key in totals:
            if key in row:
                totals[key] += row.get(key, 0) or 0

    # Compute uni_recovery and uni_deterioration for totals row
    totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
    totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

    # Format functions
    def fmt(cnt, x):
        pct = round((cnt / x) * 100, 2) if x > 0 else 0
        return f"{int(cnt)} ({pct:.2f}%)"

    def fmt_bold(cnt):
        return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

    def fmt_green(cnt, x):
        pct = round((cnt / x) * 100, 2) if x > 0 else 0
        return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

    def fmt_red(cnt, x):
        pct = round((cnt / x) * 100, 2) if x > 0 else 0
        return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

    def fmt_gray(cnt, x):
        pct = round((cnt / x) * 100, 2) if x > 0 else 0
        return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

    # Calculate transition totals
    t_md_nr = totals['md_nr_cnt']
    t_sv_md = totals['sv_md_cnt']
    t_sv_nr = totals['sv_nr_cnt']
    t_nr_md = totals['nr_md_cnt']
    t_nr_sv = totals['nr_sv_cnt']
    t_md_sv = totals['md_sv_cnt']
    t_sv_sv = totals['sv_sv_cnt']
    t_md_md = totals['md_md_cnt']
    t_nr_nr = totals['nr_nr_cnt']

    t_recovery = t_md_nr + t_sv_md + t_sv_nr
    t_deterioration = t_nr_md + t_nr_sv + t_md_sv
    t_no_change = t_sv_sv + t_md_md + t_nr_nr

    # Calculate display values
    md_nr_display = fmt(t_md_nr, totals['moderate_first'])
    sv_md_display = fmt(t_sv_md, totals['severe_first'])
    sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
    total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
    nr_md_display = fmt(t_nr_md, totals['normal_first'])
    nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
    md_sv_display = fmt(t_md_sv, totals['moderate_first'])
    total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
    no_change_display = fmt_gray(t_no_change, totals['normal_first'] + totals['moderate_first'] + totals['severe_first'])
    sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
    md_md_display = fmt(t_md_md, totals['moderate_first'])
    nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

    # Populate totals row
    if selected_level not in ["8", "9", "10", "11", "12", "13"]:
        totals_row['operational_creches'] = totals['operational_creches']
    totals_row['enrolled_children'] = totals['enrolled_children']
    totals_row['measured'] = fmt_bold(totals['measured_twice'])
    totals_row['normal_first'] = fmt_bold(totals['normal_first'])
    totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
    totals_row['severe_first'] = fmt_bold(totals['severe_first'])
    totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
    totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
    totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

    totals_row['md_nr_display'] = md_nr_display
    totals_row['sv_md_display'] = sv_md_display
    totals_row['sv_nr_display'] = sv_nr_display
    totals_row['total_recovery_display'] = total_recovery_display
    totals_row['nr_md_display'] = nr_md_display
    totals_row['nr_sv_display'] = nr_sv_display
    totals_row['md_sv_display'] = md_sv_display
    totals_row['total_deterioration_display'] = total_deterioration_display
    totals_row['no_change_display'] = no_change_display
    totals_row['sv_sv_display'] = sv_sv_display
    totals_row['md_md_display'] = md_md_display
    totals_row['nr_nr_display'] = nr_nr_display

    return totals_row


def get_report_data(filters):
    try:
        params = build_query_params(filters)
        query = build_main_query(filters, params)

        # Execute query
        data = frappe.db.sql(query, params, as_dict=True)

        for row in data:
            # Compute uni_recovery and uni_deterioration for each row
            row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
            row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

            # Measured now counts children with both initial and final measurements on different dates
            row['measured'] = row.get('measured_twice', 0) or 0

            md_nr = row.get('md_nr_cnt', 0) or 0
            sv_md = row.get('sv_md_cnt', 0) or 0
            sv_nr = row.get('sv_nr_cnt', 0) or 0
            nr_md = row.get('nr_md_cnt', 0) or 0
            nr_sv = row.get('nr_sv_cnt', 0) or 0
            md_sv = row.get('md_sv_cnt', 0) or 0
            sv_sv = row.get('sv_sv_cnt', 0) or 0
            md_md = row.get('md_md_cnt', 0) or 0
            nr_nr = row.get('nr_nr_cnt', 0) or 0

            def fmt(cnt, x):
                pct = round((cnt / x) * 100, 2) if x > 0 else 0
                return f"{int(cnt)} ({pct:.2f}%)"

            def fmt_green(cnt, x):
                pct = round((cnt / x) * 100, 2) if x > 0 else 0
                return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

            def fmt_red(cnt, x):
                pct = round((cnt / x) * 100, 2) if x > 0 else 0
                return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

            def fmt_gray(cnt, x):
                pct = round((cnt / x) * 100, 2) if x > 0 else 0
                return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

            total_recovery = md_nr + sv_md + sv_nr
            total_deterioration = nr_md + nr_sv + md_sv
            no_change = sv_sv + md_md + nr_nr

            row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
            row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
            row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
            row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
            row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
            row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
            row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
            row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
            row['no_change_display'] = fmt_gray(no_change, (row.get('normal_first', 0) + row.get('moderate_first', 0) + row.get('severe_first', 0)) or 0)
            row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
            row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
            row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

        return data

    except Exception as e:
        frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
        raise


def build_query_params(filters):
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    geography_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

    end_month = int(filters.get("month", datetime.now().month))
    end_year = int(filters.get("year", datetime.now().year))
    end_date_first = date(end_year, end_month, 1)
    end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

    state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
    district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
    block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
    gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

    params = {
        "end_month": end_month,
        "end_year": end_year,
        "end_date_first": end_date_first,
        "end_date_last": end_date_last,
        "partner": partner_id,
        "state": filters.get("state"),
        "district": filters.get("district"),
        "block": filters.get("block"),
        "gp": filters.get("gp"),
        "creche": filters.get("creche"),
        "supervisor_id": filters.get("supervisor_id"),
        "creche_status_id": filters.get("creche_status_id", "3"),
        "state_ids": tuple(state_ids_list) if state_ids_list else None,
        "district_ids": tuple(district_ids_list) if district_ids_list else None,
        "block_ids": tuple(block_ids_list) if block_ids_list else None,
        "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
        "phases": None,
        "cstart_date": None,
        "cend_date": None,
        "age_group": filters.get("age_group"),
        "indicator": filters.get("indicator", "weight_for_age"),
        "gender": filters.get("gender"),
        "creche_age": filters.get("creche_age"),
    }

    handle_date_filters(filters, params)

    if filters.get("phases"):
        try:
            phases_cleaned = ",".join(
                ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
            )
            if phases_cleaned:
                params["phases"] = phases_cleaned
        except (AttributeError, TypeError):
            pass

    return params


def handle_date_filters(filters, params):
    cr_opening_range_type = filters.get("cr_opening_range_type")
    if cr_opening_range_type == "between":
        c_opening_range = filters.get("c_opening_range", [None, None])
        params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
        params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
    elif cr_opening_range_type in ["before", "after", "equal"]:
        single_date = filters.get("single_date")
        if single_date:
            if isinstance(single_date, str):
                try:
                    single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
                except ValueError:
                    single_date = date.today()
            if cr_opening_range_type == "before":
                params["cstart_date"] = date(2017, 1, 1)
                params["cend_date"] = single_date - timedelta(days=1)
            elif cr_opening_range_type == "after":
                params["cstart_date"] = single_date + timedelta(days=1)
                params["cend_date"] = date.today()
            elif cr_opening_range_type == "equal":
                params["cstart_date"] = single_date
                params["cend_date"] = single_date


def build_main_query(filters, params):
    selected_level = filters.get("level", "7")
    selected_indicator = params["indicator"]

    geo_level_mapping = {
        "1": ["p.partner_name"],
        "2": ["s.state_name"],
        "3": ["s.state_name", "d.district_name"],
        "4": ["s.state_name", "d.district_name", "b.block_name"],
        "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
        "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
        "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
              "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
    }

    field_map = {
        "p.partner_name": "p.partner_name AS partner",
        "s.state_name": "s.state_name AS state",
        "d.district_name": "d.district_name AS district",
        "b.block_name": "b.block_name AS block",
        "g.gp_name": "g.gp_name AS gp",
        "u.full_name": "u.full_name AS supervisor_id",
        "c.creche_name": "c.creche_name AS creche",
        "c.creche_id": "c.creche_id AS creche_id"
    }

    additional_select = ""
    group_by_clause = ""
    order_by_clause = ""
    select_fields_str = ""
    group_by_fields = []

    if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
        group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
        select_fields = [field_map[f] for f in group_by_fields if f in field_map]
        select_fields_str = ",\n ".join(select_fields)
        group_by_clause = ", ".join(group_by_fields)
        order_by_clause = group_by_clause
    else:
        group_expr = ""
        sort_key_expr = ""
        alias = ""
        if selected_level == "8":
            group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
            alias = "creche_age"
            sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
            additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
            order_by_clause = "sort_key"
        elif selected_level == "9":
            group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
            alias = "gender"
            additional_select = ",\n " + group_expr + " AS " + alias
            order_by_clause = alias
        elif selected_level == "10":
            group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
            alias = "age_group"
            sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
            additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
            order_by_clause = "sort_key"
        elif selected_level == "11":
            group_expr = """CASE 
                WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
                ELSE 'Above 36'
            END"""
            alias = "age_at_enrollment"
            sort_key_expr = """CASE 
                WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
                WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
                ELSE 6
            END AS sort_key"""
            additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
            order_by_clause = "sort_key"
        elif selected_level == "12":
            # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
            group_expr = """CASE 
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
                ELSE '36+ months'
            END"""
            alias = "tenure_bucket"
            sort_key_expr = """CASE 
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
                WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
                ELSE 6
            END AS sort_key"""
            additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
            order_by_clause = "sort_key"
        elif selected_level == "13":
            # Attendance percentage reused from average_attendance_child_wise.py:
            # days_attended * 100 / eligible_open_days for the selected month (0 when no eligible open days)
            attendance_pct_expr = "ROUND(CASE WHEN IFNULL(att.eligible_open_days, 0) > 0 THEN (IFNULL(att.days_attended, 0) * 100.0 / att.eligible_open_days) ELSE 0 END, 2)"
            group_expr = f"""CASE
                WHEN {attendance_pct_expr} = 0 THEN 'Attendance (0%%)'
                WHEN {attendance_pct_expr} < 25 THEN 'Attendance (> 0%% to < 25%%)'
                WHEN {attendance_pct_expr} < 50 THEN 'Attendance (25%% to < 50%%)'
                WHEN {attendance_pct_expr} < 75 THEN 'Attendance (50%% to < 75%%)'
                WHEN {attendance_pct_expr} < 100 THEN 'Attendance (75%% to < 100%%)'
                WHEN {attendance_pct_expr} = 100 THEN 'Attendance (100%%)'
                ELSE 'Attendance (0%%)'
            END"""
            alias = "attendance_slab"
            sort_key_expr = f"""CASE
                WHEN {attendance_pct_expr} = 0 THEN 1
                WHEN {attendance_pct_expr} < 25 THEN 2
                WHEN {attendance_pct_expr} < 50 THEN 3
                WHEN {attendance_pct_expr} < 75 THEN 4
                WHEN {attendance_pct_expr} < 100 THEN 5
                WHEN {attendance_pct_expr} = 100 THEN 6
                ELSE 1
            END AS sort_key"""
            additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
            order_by_clause = "sort_key"
        group_by_clause = group_expr

    if not select_fields_str and additional_select:
        additional_select = additional_select.lstrip(',\n ')

    geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
    if geo_part:
        geo_part += ","

    operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12", "13"] else ""

    p = params

    where_conditions = ["1=1"]
    if p["partner"]:
        where_conditions.append("c.partner_id = %(partner)s")
    if p["state"]:
        where_conditions.append("c.state_id = %(state)s")
    elif p["state_ids"]:
        where_conditions.append("c.state_id IN %(state_ids)s")
    if p["district"]:
        where_conditions.append("c.district_id = %(district)s")
    elif p["district_ids"]:
        where_conditions.append("c.district_id IN %(district_ids)s")
    if p["block"]:
        where_conditions.append("c.block_id = %(block)s")
    elif p["block_ids"]:
        where_conditions.append("c.block_id IN %(block_ids)s")
    if p["gp"]:
        where_conditions.append("c.gp_id = %(gp)s")
    elif p["gp_ids"]:
        where_conditions.append("c.gp_id IN %(gp_ids)s")
    if p["creche"]:
        where_conditions.append("c.name = %(creche)s")
    if p["supervisor_id"]:
        where_conditions.append("c.supervisor_id = %(supervisor_id)s")
    if p["creche_status_id"]:
        where_conditions.append("c.creche_status_id = %(creche_status_id)s")
    if p["phases"]:
        where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
    if p["creche_age"]:
        where_conditions.append("""
            CASE 
                WHEN c.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
                ELSE ''
            END = %(creche_age)s
        """)
    where_conditions.append(
        "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
        "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
    )
    if selected_level == "10":
        where_conditions.append(
            "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
        )
    if selected_level == "12":
        # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
        where_conditions.append(
            "cee.date_of_enrollment IS NOT NULL"
        )
    if selected_level == "13":
        # Same enrollment window as average_attendance_child_wise.py:
        # enrolled on/before month end (already in the cee join) and not exited before month start
        where_conditions.append(
            "cee.name IS NOT NULL AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(end_date_first)s)"
        )

    def age_filter(alias_dob, alias_date):
        ag = p.get("age_group")
        if ag == "6m-11m":
            return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
        elif ag == "12m-17m":
            return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
        elif ag == "18m-23m":
            return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
        elif ag == "24m-29m":
            return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
        elif ag == "30m-36m":
            return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
        elif ag == "> 36m":
            return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
        return ""

    # Z-SCORE CATEGORIZATION LOGIC
    # Severe: z-score < -3
    # Moderate: -3 <= z-score < -2
    # Normal: -2 <= z-score <= 2
    # Overweight/Obese: z-score > 2
    
    # INITIAL MEASUREMENT: First recorded entry ever (earliest measurement_taken_date)
    initial_measurement_subquery = f"""
    LEFT JOIN (
        SELECT * FROM (
            SELECT 
                childenrollguid, 
                {selected_indicator}_zscore,
                measurement_taken_date AS measurement_date,
                CASE 
                    WHEN CAST({selected_indicator}_zscore AS DECIMAL(10,2)) < -3 THEN 'Severe'
                    WHEN CAST({selected_indicator}_zscore AS DECIMAL(10,2)) < -2 THEN 'Moderate'
                    ELSE 'Normal'
                END AS category,
                ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date ASC) as rn
            FROM `tabAnthropromatic Data`
            WHERE do_you_have_height_weight = 1 
            AND {selected_indicator}_zscore IS NOT NULL
            AND TRIM({selected_indicator}_zscore) <> ''
            AND measurement_taken_date <= %(end_date_last)s
        ) x WHERE x.rn = 1
    ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
    """

    # FINAL MEASUREMENT: Most recent entry ever (latest measurement_taken_date)
    final_measurement_subquery = f"""
    LEFT JOIN (
        SELECT * FROM (
            SELECT 
                childenrollguid, 
                {selected_indicator}_zscore,
                measurement_taken_date AS measurement_date,
                CASE 
                    WHEN CAST({selected_indicator}_zscore AS DECIMAL(10,2)) < -3 THEN 'Severe'
                    WHEN CAST({selected_indicator}_zscore AS DECIMAL(10,2)) < -2 THEN 'Moderate'
                    ELSE 'Normal'
                END AS category,
                ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date DESC) as rn
            FROM `tabAnthropromatic Data`
            WHERE do_you_have_height_weight = 1 
            AND {selected_indicator}_zscore IS NOT NULL
            AND TRIM({selected_indicator}_zscore) <> ''
            AND measurement_taken_date <= %(end_date_last)s
        ) y WHERE y.rn = 1
    ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
    """

    # ATTENDANCE (Level 13 only): per-child days attended / eligible open days for the
    # selected month, reused from average_attendance_child_wise.py
    attendance_join = ""
    if selected_level == "13":
        attendance_join = """
    LEFT JOIN (
        SELECT
            cal.childenrolledguid,
            SUM(cal.attendance) AS days_attended,
            COUNT(ca.date_of_attendance) AS eligible_open_days
        FROM `tabChild Attendance` AS ca
        INNER JOIN `tabChild Attendance List` AS cal
            ON cal.parent = ca.name
        WHERE ca.is_shishu_ghar_is_closed_for_the_day = 0
        AND ca.date_of_attendance BETWEEN %(end_date_first)s AND %(end_date_last)s
        GROUP BY cal.childenrolledguid
    ) AS att ON att.childenrolledguid = cee.childenrollguid
    """

    query = f"""
    SELECT
        {geo_part}
        {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
        COUNT(DISTINCT 
            CASE 
                WHEN ad_initial.measurement_date != ad_final.measurement_date 
                THEN cee.childenrollguid 
            END
        ) AS measured_twice,
        SUM(CASE WHEN ad_initial.category = 'Normal' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS normal_first,
        SUM(CASE WHEN ad_initial.category = 'Moderate' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS moderate_first,
        SUM(CASE WHEN ad_initial.category = 'Severe' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS severe_first,

        SUM(CASE WHEN ad_initial.category = 'Moderate' AND ad_final.category = 'Normal' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS md_nr_cnt,
        SUM(CASE WHEN ad_initial.category = 'Severe' AND ad_final.category = 'Moderate' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS sv_md_cnt,
        SUM(CASE WHEN ad_initial.category = 'Severe' AND ad_final.category = 'Normal' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS sv_nr_cnt,
        SUM(CASE WHEN ad_initial.category = 'Normal' AND ad_final.category = 'Moderate' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS nr_md_cnt,
        SUM(CASE WHEN ad_initial.category = 'Moderate' AND ad_final.category = 'Severe' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS md_sv_cnt,
        SUM(CASE WHEN ad_initial.category = 'Normal' AND ad_final.category = 'Severe' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS nr_sv_cnt,
        SUM(CASE WHEN ad_initial.category = 'Severe' AND ad_final.category = 'Severe' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS sv_sv_cnt,
        SUM(CASE WHEN ad_initial.category = 'Moderate' AND ad_final.category = 'Moderate' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS md_md_cnt,
        SUM(CASE WHEN ad_initial.category = 'Normal' AND ad_final.category = 'Normal' AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS nr_nr_cnt
        
    FROM `tabCreche` c
    JOIN `tabState` s ON c.state_id = s.name
    JOIN `tabPartner` p ON c.partner_id = p.name
    JOIN `tabDistrict` d ON c.district_id = d.name
    JOIN `tabBlock` b ON c.block_id = b.name
    JOIN `tabGram Panchayat` g ON c.gp_id = g.name
    JOIN `tabUser` u ON u.name = c.supervisor_id
    LEFT JOIN `tabChild Enrollment and Exit` cee
        ON cee.creche_id = c.name
        AND cee.date_of_enrollment <= %(end_date_last)s
        {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
        {age_filter("cee.child_dob", "%(end_date_first)s")}
    {initial_measurement_subquery}
    {final_measurement_subquery}
    {attendance_join}
    WHERE {" AND ".join(where_conditions)}
    GROUP BY {group_by_clause}
    ORDER BY {order_by_clause}
    """

    return query

















# import frappe
# from frappe import _
# from datetime import datetime, date, timedelta
# import calendar


# def execute(filters=None):
#     try:
#         selected_level = filters.get("level", "7")
#         selected_indicator = filters.get("indicator", "weight_for_age")

#         level_mapping = {
#             "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
#             "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
#             "3": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
#             ],
#             "4": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
#             ],
#             "5": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
#             ],
#             "6": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
#             ],
#             "7": [
#                 {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
#             ],
#             "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
#             "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
#             "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
#             "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
#             "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
#         }

#         variable_columns = level_mapping.get(selected_level, level_mapping["7"])

#         fixed_columns = [
#             {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
#             {"label": "Total Universe (Measured Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 290},
#             {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
#             # {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
#             {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
#             {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
#             {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
#             {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
#         ]

#         # Add Operational Creches column only for geographical levels (1-7)
#         if selected_level not in ["8", "9", "10", "11", "12"]:
#             fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

#         columns = variable_columns + fixed_columns
#         data = get_report_data(filters)

#         # Calculate totals row
#         if data:
#             totals_row = calculate_totals_row(data, filters, variable_columns)
#             data.append(totals_row)

#         return columns, data

#     except Exception as e:
#         frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
#         frappe.throw(_(f"Error in report: {str(e)}"))
#         return [], []


# def calculate_totals_row(data, filters, variable_columns):
#     selected_level = filters.get("level", "7")

#     totals_row = {'is_total': True, 'indent': 0}

#     # Set label for totals row
#     level_field_map = {
#         "1": "partner", "2": "state", "3": "district",
#         "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
#         "8": "creche_age",
#         "9": "gender",
#         "10": "age_group",
#         "11": "age_at_enrollment",
#         "12": "tenure_bucket",
#     }

#     if selected_level in level_field_map:
#         totals_row[level_field_map[selected_level]] = "Total"
#     else:
#         for col in variable_columns:
#             totals_row[col['fieldname']] = "Total"

#     # Include all numeric columns
#     total_keys = [
#         'operational_creches', 'enrolled_children', 'measured_twice',
#         'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
#         'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
#         'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
#     ]

#     totals = {k: 0 for k in total_keys}
#     for row in data:
#         for key in totals:
#             if key in row:
#                 totals[key] += row.get(key, 0) or 0

#     # Compute uni_recovery and uni_deterioration for totals row
#     totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

#     # Format functions
#     def fmt(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"{int(cnt)} ({pct:.2f}%)"

#     def fmt_bold(cnt):
#         return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

#     def fmt_green(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_red(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_gray(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     # Calculate transition totals
#     t_md_nr = totals['md_nr_cnt']
#     t_sv_md = totals['sv_md_cnt']
#     t_sv_nr = totals['sv_nr_cnt']
#     t_nr_md = totals['nr_md_cnt']
#     t_nr_sv = totals['nr_sv_cnt']
#     t_md_sv = totals['md_sv_cnt']
#     t_sv_sv = totals['sv_sv_cnt']
#     t_md_md = totals['md_md_cnt']
#     t_nr_nr = totals['nr_nr_cnt']

#     t_recovery = t_md_nr + t_sv_md + t_sv_nr
#     t_deterioration = t_nr_md + t_nr_sv + t_md_sv
#     t_no_change = t_sv_sv + t_md_md + t_nr_nr

#     # Calculate display values
#     md_nr_display = fmt(t_md_nr, totals['moderate_first'])
#     sv_md_display = fmt(t_sv_md, totals['severe_first'])
#     sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
#     total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
#     nr_md_display = fmt(t_nr_md, totals['normal_first'])
#     nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
#     md_sv_display = fmt(t_md_sv, totals['moderate_first'])
#     total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
#     no_change_display = fmt_gray(t_no_change, totals['normal_first'] + totals['moderate_first'] + totals['severe_first'])
#     sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
#     md_md_display = fmt(t_md_md, totals['moderate_first'])
#     nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

#     # Populate totals row
#     if selected_level not in ["8", "9", "10", "11", "12"]:
#         totals_row['operational_creches'] = totals['operational_creches']
#     totals_row['enrolled_children'] = totals['enrolled_children']
#     totals_row['measured'] = fmt_bold(totals['measured_twice'])
#     totals_row['normal_first'] = fmt_bold(totals['normal_first'])
#     totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
#     totals_row['severe_first'] = fmt_bold(totals['severe_first'])
#     totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
#     totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
#     totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

#     totals_row['md_nr_display'] = md_nr_display
#     totals_row['sv_md_display'] = sv_md_display
#     totals_row['sv_nr_display'] = sv_nr_display
#     totals_row['total_recovery_display'] = total_recovery_display
#     totals_row['nr_md_display'] = nr_md_display
#     totals_row['nr_sv_display'] = nr_sv_display
#     totals_row['md_sv_display'] = md_sv_display
#     totals_row['total_deterioration_display'] = total_deterioration_display
#     totals_row['no_change_display'] = no_change_display
#     totals_row['sv_sv_display'] = sv_sv_display
#     totals_row['md_md_display'] = md_md_display
#     totals_row['nr_nr_display'] = nr_nr_display

#     return totals_row


# def get_report_data(filters):
#     try:
#         params = build_query_params(filters)
#         query = build_main_query(filters, params)

#         # Execute query
#         data = frappe.db.sql(query, params, as_dict=True)

#         for row in data:
#             # Compute uni_recovery and uni_deterioration for each row
#             row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
#             row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

#             # Measured now counts children with both initial and final measurements on different dates
#             row['measured'] = row.get('measured_twice', 0) or 0

#             md_nr = row.get('md_nr_cnt', 0) or 0
#             sv_md = row.get('sv_md_cnt', 0) or 0
#             sv_nr = row.get('sv_nr_cnt', 0) or 0
#             nr_md = row.get('nr_md_cnt', 0) or 0
#             nr_sv = row.get('nr_sv_cnt', 0) or 0
#             md_sv = row.get('md_sv_cnt', 0) or 0
#             sv_sv = row.get('sv_sv_cnt', 0) or 0
#             md_md = row.get('md_md_cnt', 0) or 0
#             nr_nr = row.get('nr_nr_cnt', 0) or 0

#             def fmt(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"{int(cnt)} ({pct:.2f}%)"

#             def fmt_green(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_red(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_gray(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             total_recovery = md_nr + sv_md + sv_nr
#             total_deterioration = nr_md + nr_sv + md_sv
#             no_change = sv_sv + md_md + nr_nr

#             row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
#             row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
#             row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
#             row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
#             row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
#             row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
#             row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
#             row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
#             row['no_change_display'] = fmt_gray(no_change, (row.get('normal_first', 0) + row.get('moderate_first', 0) + row.get('severe_first', 0)) or 0)
#             row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
#             row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
#             row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

#         return data

#     except Exception as e:
#         frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
#         raise


# def build_query_params(filters):
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     geography_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

#     end_month = int(filters.get("month", datetime.now().month))
#     end_year = int(filters.get("year", datetime.now().year))
#     end_date_first = date(end_year, end_month, 1)
#     end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

#     state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
#     district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
#     block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
#     gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

#     params = {
#         "end_month": end_month,
#         "end_year": end_year,
#         "end_date_first": end_date_first,
#         "end_date_last": end_date_last,
#         "partner": partner_id,
#         "state": filters.get("state"),
#         "district": filters.get("district"),
#         "block": filters.get("block"),
#         "gp": filters.get("gp"),
#         "creche": filters.get("creche"),
#         "supervisor_id": filters.get("supervisor_id"),
#         "creche_status_id": filters.get("creche_status_id", "3"),
#         "state_ids": tuple(state_ids_list) if state_ids_list else None,
#         "district_ids": tuple(district_ids_list) if district_ids_list else None,
#         "block_ids": tuple(block_ids_list) if block_ids_list else None,
#         "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "age_group": filters.get("age_group"),
#         "indicator": filters.get("indicator", "weight_for_age"),
#         "gender": filters.get("gender"),
#         "creche_age": filters.get("creche_age"),
#     }

#     handle_date_filters(filters, params)

#     if filters.get("phases"):
#         try:
#             phases_cleaned = ",".join(
#                 ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
#             )
#             if phases_cleaned:
#                 params["phases"] = phases_cleaned
#         except (AttributeError, TypeError):
#             pass

#     return params


# def handle_date_filters(filters, params):
#     cr_opening_range_type = filters.get("cr_opening_range_type")
#     if cr_opening_range_type == "between":
#         c_opening_range = filters.get("c_opening_range", [None, None])
#         params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
#         params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
#     elif cr_opening_range_type in ["before", "after", "equal"]:
#         single_date = filters.get("single_date")
#         if single_date:
#             if isinstance(single_date, str):
#                 try:
#                     single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     single_date = date.today()
#             if cr_opening_range_type == "before":
#                 params["cstart_date"] = date(2017, 1, 1)
#                 params["cend_date"] = single_date - timedelta(days=1)
#             elif cr_opening_range_type == "after":
#                 params["cstart_date"] = single_date + timedelta(days=1)
#                 params["cend_date"] = date.today()
#             elif cr_opening_range_type == "equal":
#                 params["cstart_date"] = single_date
#                 params["cend_date"] = single_date


# def build_main_query(filters, params):
#     selected_level = filters.get("level", "7")
#     selected_indicator = params["indicator"]

#     geo_level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
#               "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }

#     field_map = {
#         "p.partner_name": "p.partner_name AS partner",
#         "s.state_name": "s.state_name AS state",
#         "d.district_name": "d.district_name AS district",
#         "b.block_name": "b.block_name AS block",
#         "g.gp_name": "g.gp_name AS gp",
#         "u.full_name": "u.full_name AS supervisor_id",
#         "c.creche_name": "c.creche_name AS creche",
#         "c.creche_id": "c.creche_id AS creche_id"
#     }

#     additional_select = ""
#     group_by_clause = ""
#     order_by_clause = ""
#     select_fields_str = ""
#     group_by_fields = []

#     if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
#         group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
#         select_fields = [field_map[f] for f in group_by_fields if f in field_map]
#         select_fields_str = ",\n ".join(select_fields)
#         group_by_clause = ", ".join(group_by_fields)
#         order_by_clause = group_by_clause
#     else:
#         group_expr = ""
#         sort_key_expr = ""
#         alias = ""
#         if selected_level == "8":
#             group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
#             alias = "creche_age"
#             sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "9":
#             group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
#             alias = "gender"
#             additional_select = ",\n " + group_expr + " AS " + alias
#             order_by_clause = alias
#         elif selected_level == "10":
#             group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
#             alias = "age_group"
#             sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "11":
#             group_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
#                 ELSE 'Above 36'
#             END"""
#             alias = "age_at_enrollment"
#             sort_key_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "12":
#             # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
#             group_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
#                 ELSE '36+ months'
#             END"""
#             alias = "tenure_bucket"
#             sort_key_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         group_by_clause = group_expr

#     if not select_fields_str and additional_select:
#         additional_select = additional_select.lstrip(',\n ')

#     geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
#     if geo_part:
#         geo_part += ","

#     operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12"] else ""

#     p = params

#     where_conditions = ["1=1"]
#     if p["partner"]:
#         where_conditions.append("c.partner_id = %(partner)s")
#     if p["state"]:
#         where_conditions.append("c.state_id = %(state)s")
#     elif p["state_ids"]:
#         where_conditions.append("c.state_id IN %(state_ids)s")
#     if p["district"]:
#         where_conditions.append("c.district_id = %(district)s")
#     elif p["district_ids"]:
#         where_conditions.append("c.district_id IN %(district_ids)s")
#     if p["block"]:
#         where_conditions.append("c.block_id = %(block)s")
#     elif p["block_ids"]:
#         where_conditions.append("c.block_id IN %(block_ids)s")
#     if p["gp"]:
#         where_conditions.append("c.gp_id = %(gp)s")
#     elif p["gp_ids"]:
#         where_conditions.append("c.gp_id IN %(gp_ids)s")
#     if p["creche"]:
#         where_conditions.append("c.name = %(creche)s")
#     if p["supervisor_id"]:
#         where_conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if p["creche_status_id"]:
#         where_conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if p["phases"]:
#         where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#     if p["creche_age"]:
#         where_conditions.append("""
#             CASE 
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
#     where_conditions.append(
#         "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
#         "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
#     )
#     if selected_level == "10":
#         where_conditions.append(
#             "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
#         )
#     if selected_level == "12":
#         # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
#         where_conditions.append(
#             "cee.date_of_enrollment IS NOT NULL"
#         )

#     def age_filter(alias_dob, alias_date):
#         ag = p.get("age_group")
#         if ag == "6m-11m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
#         elif ag == "12m-17m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
#         elif ag == "18m-23m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
#         elif ag == "24m-29m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
#         elif ag == "30m-36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
#         elif ag == "> 36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
#         return ""

#     # INITIAL MEASUREMENT: First recorded entry ever (earliest measurement_taken_date)
#     initial_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 {selected_indicator}_zscore,
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date ASC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#             AND {selected_indicator}_zscore IS NOT NULL
#             AND TRIM({selected_indicator}_zscore) <> ''
#             AND measurement_taken_date <= %(end_date_last)s
#         ) x WHERE x.rn = 1
#     ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
#     """

#     # FINAL MEASUREMENT: Most recent entry ever (latest measurement_taken_date)
#     final_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 {selected_indicator}_zscore,
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date DESC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#             AND {selected_indicator}_zscore IS NOT NULL
#             AND TRIM({selected_indicator}_zscore) <> ''
#             AND measurement_taken_date <= %(end_date_last)s
#         ) y WHERE y.rn = 1
#     ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
#     """

#     query = f"""
#     SELECT
#         {geo_part}
#         {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
#         COUNT(DISTINCT 
#             CASE 
#                 WHEN ad_initial.measurement_date != ad_final.measurement_date 
#                 THEN cee.childenrollguid 
#             END
#         ) AS measured_twice,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS normal_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS moderate_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS severe_first,

#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} >= 3 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS md_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 2 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS sv_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} >= 3 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS sv_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_final.{selected_indicator} = 2 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS nr_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 1 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS md_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_final.{selected_indicator} = 1 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS nr_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 1 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS sv_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 2 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS md_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_final.{selected_indicator} >= 3 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS nr_nr_cnt
        
#     FROM `tabCreche` c
#     JOIN `tabState` s ON c.state_id = s.name
#     JOIN `tabPartner` p ON c.partner_id = p.name
#     JOIN `tabDistrict` d ON c.district_id = d.name
#     JOIN `tabBlock` b ON c.block_id = b.name
#     JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#     JOIN `tabUser` u ON u.name = c.supervisor_id
#     LEFT JOIN `tabChild Enrollment and Exit` cee
#         ON cee.creche_id = c.name
#         AND cee.date_of_enrollment <= %(end_date_last)s
#         {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
#         {age_filter("cee.child_dob", "%(end_date_first)s")}
#     {initial_measurement_subquery}
#     {final_measurement_subquery}
#     WHERE {" AND ".join(where_conditions)}
#     GROUP BY {group_by_clause}
#     ORDER BY {order_by_clause}
#     """

#     return query












#pankaj Fixed
# import frappe
# from frappe import _
# from datetime import datetime, date, timedelta
# import calendar


# def execute(filters=None):
#     try:
#         selected_level = filters.get("level", "7")
#         selected_indicator = filters.get("indicator", "weight_for_age")

#         level_mapping = {
#             "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
#             "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
#             "3": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
#             ],
#             "4": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
#             ],
#             "5": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
#             ],
#             "6": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
#             ],
#             "7": [
#                 {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
#             ],
#             "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
#             "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
#             "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
#             "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
#             "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
#         }

#         variable_columns = level_mapping.get(selected_level, level_mapping["7"])

#         fixed_columns = [
#             {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
#             {"label": "Total Universe (Measured Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 290},
#             {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
#             # {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
#             {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
#             {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
#             {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
#             {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
#         ]

#         # Add Operational Creches column only for geographical levels (1-7)
#         if selected_level not in ["8", "9", "10", "11", "12"]:
#             fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

#         columns = variable_columns + fixed_columns
#         data = get_report_data(filters)

#         # Calculate totals row
#         if data:
#             totals_row = calculate_totals_row(data, filters, variable_columns)
#             data.append(totals_row)

#         return columns, data

#     except Exception as e:
#         frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
#         frappe.throw(_(f"Error in report: {str(e)}"))
#         return [], []


# def calculate_totals_row(data, filters, variable_columns):
#     selected_level = filters.get("level", "7")

#     totals_row = {'is_total': True, 'indent': 0}

#     # Set label for totals row
#     level_field_map = {
#         "1": "partner", "2": "state", "3": "district",
#         "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
#         "8": "creche_age",
#         "9": "gender",
#         "10": "age_group",
#         "11": "age_at_enrollment",
#         "12": "tenure_bucket",
#     }

#     if selected_level in level_field_map:
#         totals_row[level_field_map[selected_level]] = "Total"
#     else:
#         for col in variable_columns:
#             totals_row[col['fieldname']] = "Total"

#     # Include all numeric columns
#     total_keys = [
#         'operational_creches', 'enrolled_children', 'measured_twice',
#         'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
#         'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
#         'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
#     ]

#     totals = {k: 0 for k in total_keys}
#     for row in data:
#         for key in totals:
#             if key in row:
#                 totals[key] += row.get(key, 0) or 0

#     # Compute uni_recovery and uni_deterioration for totals row
#     totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

#     # Format functions
#     def fmt(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"{int(cnt)} ({pct:.2f}%)"

#     def fmt_bold(cnt):
#         return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

#     def fmt_green(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_red(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_gray(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     # Calculate transition totals
#     t_md_nr = totals['md_nr_cnt']
#     t_sv_md = totals['sv_md_cnt']
#     t_sv_nr = totals['sv_nr_cnt']
#     t_nr_md = totals['nr_md_cnt']
#     t_nr_sv = totals['nr_sv_cnt']
#     t_md_sv = totals['md_sv_cnt']
#     t_sv_sv = totals['sv_sv_cnt']
#     t_md_md = totals['md_md_cnt']
#     t_nr_nr = totals['nr_nr_cnt']

#     t_recovery = t_md_nr + t_sv_md + t_sv_nr
#     t_deterioration = t_nr_md + t_nr_sv + t_md_sv
#     t_no_change = t_sv_sv + t_md_md + t_nr_nr

#     # Calculate display values
#     md_nr_display = fmt(t_md_nr, totals['moderate_first'])
#     sv_md_display = fmt(t_sv_md, totals['severe_first'])
#     sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
#     total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
#     nr_md_display = fmt(t_nr_md, totals['normal_first'])
#     nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
#     md_sv_display = fmt(t_md_sv, totals['moderate_first'])
#     total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
#     no_change_display = fmt_gray(t_no_change, totals['normal_first'] + totals['moderate_first'] + totals['severe_first'])
#     sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
#     md_md_display = fmt(t_md_md, totals['moderate_first'])
#     nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

#     # Populate totals row
#     if selected_level not in ["8", "9", "10", "11", "12"]:
#         totals_row['operational_creches'] = totals['operational_creches']
#     totals_row['enrolled_children'] = totals['enrolled_children']
#     totals_row['measured'] = fmt_bold(totals['measured_twice'])
#     totals_row['normal_first'] = fmt_bold(totals['normal_first'])
#     totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
#     totals_row['severe_first'] = fmt_bold(totals['severe_first'])
#     totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
#     totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
#     totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

#     totals_row['md_nr_display'] = md_nr_display
#     totals_row['sv_md_display'] = sv_md_display
#     totals_row['sv_nr_display'] = sv_nr_display
#     totals_row['total_recovery_display'] = total_recovery_display
#     totals_row['nr_md_display'] = nr_md_display
#     totals_row['nr_sv_display'] = nr_sv_display
#     totals_row['md_sv_display'] = md_sv_display
#     totals_row['total_deterioration_display'] = total_deterioration_display
#     totals_row['no_change_display'] = no_change_display
#     totals_row['sv_sv_display'] = sv_sv_display
#     totals_row['md_md_display'] = md_md_display
#     totals_row['nr_nr_display'] = nr_nr_display

#     return totals_row


# def get_report_data(filters):
#     try:
#         params = build_query_params(filters)
#         query = build_main_query(filters, params)

#         # Execute query
#         data = frappe.db.sql(query, params, as_dict=True)

#         for row in data:
#             # Compute uni_recovery and uni_deterioration for each row
#             row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
#             row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

#             # Measured now counts children with both initial and final measurements on different dates
#             row['measured'] = row.get('measured_twice', 0) or 0

#             md_nr = row.get('md_nr_cnt', 0) or 0
#             sv_md = row.get('sv_md_cnt', 0) or 0
#             sv_nr = row.get('sv_nr_cnt', 0) or 0
#             nr_md = row.get('nr_md_cnt', 0) or 0
#             nr_sv = row.get('nr_sv_cnt', 0) or 0
#             md_sv = row.get('md_sv_cnt', 0) or 0
#             sv_sv = row.get('sv_sv_cnt', 0) or 0
#             md_md = row.get('md_md_cnt', 0) or 0
#             nr_nr = row.get('nr_nr_cnt', 0) or 0

#             def fmt(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"{int(cnt)} ({pct:.2f}%)"

#             def fmt_green(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_red(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_gray(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             total_recovery = md_nr + sv_md + sv_nr
#             total_deterioration = nr_md + nr_sv + md_sv
#             no_change = sv_sv + md_md + nr_nr

#             row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
#             row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
#             row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
#             row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
#             row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
#             row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
#             row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
#             row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
#             row['no_change_display'] = fmt_gray(no_change, (row.get('normal_first', 0) + row.get('moderate_first', 0) + row.get('severe_first', 0)) or 0)
#             row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
#             row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
#             row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

#         return data

#     except Exception as e:
#         frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
#         raise


# def build_query_params(filters):
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     geography_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

#     end_month = int(filters.get("month", datetime.now().month))
#     end_year = int(filters.get("year", datetime.now().year))
#     end_date_first = date(end_year, end_month, 1)
#     end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

#     state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
#     district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
#     block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
#     gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

#     params = {
#         "end_month": end_month,
#         "end_year": end_year,
#         "end_date_first": end_date_first,
#         "end_date_last": end_date_last,
#         "partner": partner_id,
#         "state": filters.get("state"),
#         "district": filters.get("district"),
#         "block": filters.get("block"),
#         "gp": filters.get("gp"),
#         "creche": filters.get("creche"),
#         "supervisor_id": filters.get("supervisor_id"),
#         "creche_status_id": filters.get("creche_status_id", "3"),
#         "state_ids": tuple(state_ids_list) if state_ids_list else None,
#         "district_ids": tuple(district_ids_list) if district_ids_list else None,
#         "block_ids": tuple(block_ids_list) if block_ids_list else None,
#         "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "age_group": filters.get("age_group"),
#         "indicator": filters.get("indicator", "weight_for_age"),
#         "gender": filters.get("gender"),
#         "creche_age": filters.get("creche_age"),
#     }

#     handle_date_filters(filters, params)

#     if filters.get("phases"):
#         try:
#             phases_cleaned = ",".join(
#                 ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
#             )
#             if phases_cleaned:
#                 params["phases"] = phases_cleaned
#         except (AttributeError, TypeError):
#             pass

#     return params


# def handle_date_filters(filters, params):
#     cr_opening_range_type = filters.get("cr_opening_range_type")
#     if cr_opening_range_type == "between":
#         c_opening_range = filters.get("c_opening_range", [None, None])
#         params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
#         params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
#     elif cr_opening_range_type in ["before", "after", "equal"]:
#         single_date = filters.get("single_date")
#         if single_date:
#             if isinstance(single_date, str):
#                 try:
#                     single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     single_date = date.today()
#             if cr_opening_range_type == "before":
#                 params["cstart_date"] = date(2017, 1, 1)
#                 params["cend_date"] = single_date - timedelta(days=1)
#             elif cr_opening_range_type == "after":
#                 params["cstart_date"] = single_date + timedelta(days=1)
#                 params["cend_date"] = date.today()
#             elif cr_opening_range_type == "equal":
#                 params["cstart_date"] = single_date
#                 params["cend_date"] = single_date


# def build_main_query(filters, params):
#     selected_level = filters.get("level", "7")
#     selected_indicator = params["indicator"]

#     geo_level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
#               "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }

#     field_map = {
#         "p.partner_name": "p.partner_name AS partner",
#         "s.state_name": "s.state_name AS state",
#         "d.district_name": "d.district_name AS district",
#         "b.block_name": "b.block_name AS block",
#         "g.gp_name": "g.gp_name AS gp",
#         "u.full_name": "u.full_name AS supervisor_id",
#         "c.creche_name": "c.creche_name AS creche",
#         "c.creche_id": "c.creche_id AS creche_id"
#     }

#     additional_select = ""
#     group_by_clause = ""
#     order_by_clause = ""
#     select_fields_str = ""
#     group_by_fields = []

#     if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
#         group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
#         select_fields = [field_map[f] for f in group_by_fields if f in field_map]
#         select_fields_str = ",\n ".join(select_fields)
#         group_by_clause = ", ".join(group_by_fields)
#         order_by_clause = group_by_clause
#     else:
#         group_expr = ""
#         sort_key_expr = ""
#         alias = ""
#         if selected_level == "8":
#             group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
#             alias = "creche_age"
#             sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "9":
#             group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
#             alias = "gender"
#             additional_select = ",\n " + group_expr + " AS " + alias
#             order_by_clause = alias
#         elif selected_level == "10":
#             group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
#             alias = "age_group"
#             sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "11":
#             group_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
#                 ELSE 'Above 36'
#             END"""
#             alias = "age_at_enrollment"
#             sort_key_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "12":
#             # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
#             group_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
#                 ELSE '36+ months'
#             END"""
#             alias = "tenure_bucket"
#             sort_key_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         group_by_clause = group_expr

#     if not select_fields_str and additional_select:
#         additional_select = additional_select.lstrip(',\n ')

#     geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
#     if geo_part:
#         geo_part += ","

#     operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12"] else ""

#     p = params

#     where_conditions = ["1=1"]
#     if p["partner"]:
#         where_conditions.append("c.partner_id = %(partner)s")
#     if p["state"]:
#         where_conditions.append("c.state_id = %(state)s")
#     elif p["state_ids"]:
#         where_conditions.append("c.state_id IN %(state_ids)s")
#     if p["district"]:
#         where_conditions.append("c.district_id = %(district)s")
#     elif p["district_ids"]:
#         where_conditions.append("c.district_id IN %(district_ids)s")
#     if p["block"]:
#         where_conditions.append("c.block_id = %(block)s")
#     elif p["block_ids"]:
#         where_conditions.append("c.block_id IN %(block_ids)s")
#     if p["gp"]:
#         where_conditions.append("c.gp_id = %(gp)s")
#     elif p["gp_ids"]:
#         where_conditions.append("c.gp_id IN %(gp_ids)s")
#     if p["creche"]:
#         where_conditions.append("c.name = %(creche)s")
#     if p["supervisor_id"]:
#         where_conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if p["creche_status_id"]:
#         where_conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if p["phases"]:
#         where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#     if p["creche_age"]:
#         where_conditions.append("""
#             CASE 
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
#     where_conditions.append(
#         "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
#         "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
#     )
#     if selected_level == "10":
#         where_conditions.append(
#             "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
#         )
#     if selected_level == "12":
#         # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
#         where_conditions.append(
#             "cee.date_of_enrollment IS NOT NULL"
#         )

#     def age_filter(alias_dob, alias_date):
#         ag = p.get("age_group")
#         if ag == "6m-11m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
#         elif ag == "12m-17m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
#         elif ag == "18m-23m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
#         elif ag == "24m-29m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
#         elif ag == "30m-36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
#         elif ag == "> 36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
#         return ""

#     # INITIAL MEASUREMENT: First recorded entry ever (earliest measurement_taken_date)
#     initial_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 {selected_indicator}_zscore,
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date ASC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#             AND {selected_indicator}_zscore IS NOT NULL
#             AND TRIM({selected_indicator}_zscore) <> ''

#               AND measurement_taken_date <= %(end_date_last)s
#         ) x WHERE x.rn = 1
#     ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
#     """

#     # FINAL MEASUREMENT: Most recent entry ever (latest measurement_taken_date)
#     final_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 {selected_indicator}_zscore,
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date DESC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#                 AND {selected_indicator}_zscore IS NOT NULL
#                 AND TRIM({selected_indicator}_zscore) <> ''
#               AND measurement_taken_date <= %(end_date_last)s
#         ) y WHERE y.rn = 1
#     ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
#     """

#     query = f"""
#     SELECT
#         {geo_part}
#         {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
#         COUNT(DISTINCT 
#             CASE 
#                 WHEN ad_initial.measurement_date != ad_final.measurement_date 
#                 THEN cee.childenrollguid 
#             END
#         ) AS measured_twice,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS normal_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS moderate_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS severe_first,

#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} >= 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} >= 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS sv_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS md_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} >= 3 AND ad_final.{selected_indicator} >= 3 THEN 1 ELSE 0 END) AS nr_nr_cnt
        
#     FROM `tabCreche` c
#     JOIN `tabState` s ON c.state_id = s.name
#     JOIN `tabPartner` p ON c.partner_id = p.name
#     JOIN `tabDistrict` d ON c.district_id = d.name
#     JOIN `tabBlock` b ON c.block_id = b.name
#     JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#     JOIN `tabUser` u ON u.name = c.supervisor_id
#     LEFT JOIN `tabChild Enrollment and Exit` cee
#         ON cee.creche_id = c.name
#         AND cee.date_of_enrollment <= %(end_date_last)s
#         {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
#         {age_filter("cee.child_dob", "%(end_date_first)s")}
#     {initial_measurement_subquery}
#     {final_measurement_subquery}
#     WHERE {" AND ".join(where_conditions)}
#     GROUP BY {group_by_clause}
#     ORDER BY {order_by_clause}
#     """

#     return query
















# import frappe
# from frappe import _
# from datetime import datetime, date, timedelta
# import calendar


# def execute(filters=None):
#     try:
#         selected_level = filters.get("level", "7")
#         selected_indicator = filters.get("indicator", "weight_for_age")

#         level_mapping = {
#             "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
#             "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
#             "3": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
#             ],
#             "4": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
#             ],
#             "5": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
#             ],
#             "6": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
#             ],
#             "7": [
#                 {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
#             ],
#             "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
#             "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
#             "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
#             "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
#             "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
#         }

#         variable_columns = level_mapping.get(selected_level, level_mapping["7"])

#         fixed_columns = [
#             {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
#             {"label": "Total Universe (Measured Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 290},
#             {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
#             {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
#             {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
#             {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
#             {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
#             {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
#         ]

#         # Add Operational Creches column only for geographical levels (1-7)
#         if selected_level not in ["8", "9", "10", "11", "12"]:
#             fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

#         columns = variable_columns + fixed_columns
#         data = get_report_data(filters)

#         # Calculate totals row
#         if data:
#             totals_row = calculate_totals_row(data, filters, variable_columns)
#             data.append(totals_row)

#         return columns, data

#     except Exception as e:
#         frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
#         frappe.throw(_(f"Error in report: {str(e)}"))
#         return [], []


# def calculate_totals_row(data, filters, variable_columns):
#     selected_level = filters.get("level", "7")

#     totals_row = {'is_total': True, 'indent': 0}

#     # Set label for totals row
#     level_field_map = {
#         "1": "partner", "2": "state", "3": "district",
#         "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
#         "8": "creche_age",
#         "9": "gender",
#         "10": "age_group",
#         "11": "age_at_enrollment",
#         "12": "tenure_bucket",
#     }

#     if selected_level in level_field_map:
#         totals_row[level_field_map[selected_level]] = "Total"
#     else:
#         for col in variable_columns:
#             totals_row[col['fieldname']] = "Total"

#     # Include all numeric columns
#     total_keys = [
#         'operational_creches', 'enrolled_children', 'measured_twice',
#         'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
#         'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
#         'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
#     ]

#     totals = {k: 0 for k in total_keys}
#     for row in data:
#         for key in totals:
#             if key in row:
#                 totals[key] += row.get(key, 0) or 0

#     # Compute uni_recovery and uni_deterioration for totals row
#     totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

#     # Format functions
#     def fmt(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"{int(cnt)} ({pct:.2f}%)"

#     def fmt_bold(cnt):
#         return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

#     def fmt_green(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_red(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_gray(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     # Calculate transition totals
#     t_md_nr = totals['md_nr_cnt']
#     t_sv_md = totals['sv_md_cnt']
#     t_sv_nr = totals['sv_nr_cnt']
#     t_nr_md = totals['nr_md_cnt']
#     t_nr_sv = totals['nr_sv_cnt']
#     t_md_sv = totals['md_sv_cnt']
#     t_sv_sv = totals['sv_sv_cnt']
#     t_md_md = totals['md_md_cnt']
#     t_nr_nr = totals['nr_nr_cnt']

#     t_recovery = t_md_nr + t_sv_md + t_sv_nr
#     t_deterioration = t_nr_md + t_nr_sv + t_md_sv
#     t_no_change = t_sv_sv + t_md_md + t_nr_nr

#     # Calculate display values
#     md_nr_display = fmt(t_md_nr, totals['moderate_first'])
#     sv_md_display = fmt(t_sv_md, totals['severe_first'])
#     sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
#     total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
#     nr_md_display = fmt(t_nr_md, totals['normal_first'])
#     nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
#     md_sv_display = fmt(t_md_sv, totals['moderate_first'])
#     total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
#     no_change_display = fmt_gray(t_no_change, totals['normal_first'] + totals['moderate_first'] + totals['severe_first'])
#     sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
#     md_md_display = fmt(t_md_md, totals['moderate_first'])
#     nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

#     # Populate totals row
#     if selected_level not in ["8", "9", "10", "11", "12"]:
#         totals_row['operational_creches'] = totals['operational_creches']
#     totals_row['enrolled_children'] = totals['enrolled_children']
#     totals_row['measured'] = fmt_bold(totals['measured_twice'])
#     totals_row['normal_first'] = fmt_bold(totals['normal_first'])
#     totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
#     totals_row['severe_first'] = fmt_bold(totals['severe_first'])
#     totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
#     totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
#     totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

#     totals_row['md_nr_display'] = md_nr_display
#     totals_row['sv_md_display'] = sv_md_display
#     totals_row['sv_nr_display'] = sv_nr_display
#     totals_row['total_recovery_display'] = total_recovery_display
#     totals_row['nr_md_display'] = nr_md_display
#     totals_row['nr_sv_display'] = nr_sv_display
#     totals_row['md_sv_display'] = md_sv_display
#     totals_row['total_deterioration_display'] = total_deterioration_display
#     totals_row['no_change_display'] = no_change_display
#     totals_row['sv_sv_display'] = sv_sv_display
#     totals_row['md_md_display'] = md_md_display
#     totals_row['nr_nr_display'] = nr_nr_display

#     return totals_row


# def get_report_data(filters):
#     try:
#         params = build_query_params(filters)
#         query = build_main_query(filters, params)

#         # Execute query
#         data = frappe.db.sql(query, params, as_dict=True)

#         for row in data:
#             # Compute uni_recovery and uni_deterioration for each row
#             row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
#             row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

#             # Measured now counts children with both initial and final measurements on different dates
#             row['measured'] = row.get('measured_twice', 0) or 0

#             md_nr = row.get('md_nr_cnt', 0) or 0
#             sv_md = row.get('sv_md_cnt', 0) or 0
#             sv_nr = row.get('sv_nr_cnt', 0) or 0
#             nr_md = row.get('nr_md_cnt', 0) or 0
#             nr_sv = row.get('nr_sv_cnt', 0) or 0
#             md_sv = row.get('md_sv_cnt', 0) or 0
#             sv_sv = row.get('sv_sv_cnt', 0) or 0
#             md_md = row.get('md_md_cnt', 0) or 0
#             nr_nr = row.get('nr_nr_cnt', 0) or 0

#             def fmt(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"{int(cnt)} ({pct:.2f}%)"

#             def fmt_green(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_red(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_gray(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             total_recovery = md_nr + sv_md + sv_nr
#             total_deterioration = nr_md + nr_sv + md_sv
#             no_change = sv_sv + md_md + nr_nr

#             row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
#             row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
#             row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
#             row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
#             row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
#             row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
#             row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
#             row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
#             row['no_change_display'] = fmt_gray(no_change, (row.get('normal_first', 0) + row.get('moderate_first', 0) + row.get('severe_first', 0)) or 0)
#             row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
#             row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
#             row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

#         return data

#     except Exception as e:
#         frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
#         raise


# def build_query_params(filters):
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     geography_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

#     end_month = int(filters.get("month", datetime.now().month))
#     end_year = int(filters.get("year", datetime.now().year))
#     end_date_first = date(end_year, end_month, 1)
#     end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

#     state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
#     district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
#     block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
#     gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

#     params = {
#         "end_month": end_month,
#         "end_year": end_year,
#         "end_date_first": end_date_first,
#         "end_date_last": end_date_last,
#         "partner": partner_id,
#         "state": filters.get("state"),
#         "district": filters.get("district"),
#         "block": filters.get("block"),
#         "gp": filters.get("gp"),
#         "creche": filters.get("creche"),
#         "supervisor_id": filters.get("supervisor_id"),
#         "creche_status_id": filters.get("creche_status_id", "3"),
#         "state_ids": tuple(state_ids_list) if state_ids_list else None,
#         "district_ids": tuple(district_ids_list) if district_ids_list else None,
#         "block_ids": tuple(block_ids_list) if block_ids_list else None,
#         "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "age_group": filters.get("age_group"),
#         "indicator": filters.get("indicator", "weight_for_age"),
#         "gender": filters.get("gender"),
#         "creche_age": filters.get("creche_age"),
#     }

#     handle_date_filters(filters, params)

#     if filters.get("phases"):
#         try:
#             phases_cleaned = ",".join(
#                 ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
#             )
#             if phases_cleaned:
#                 params["phases"] = phases_cleaned
#         except (AttributeError, TypeError):
#             pass

#     return params


# def handle_date_filters(filters, params):
#     cr_opening_range_type = filters.get("cr_opening_range_type")
#     if cr_opening_range_type == "between":
#         c_opening_range = filters.get("c_opening_range", [None, None])
#         params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
#         params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
#     elif cr_opening_range_type in ["before", "after", "equal"]:
#         single_date = filters.get("single_date")
#         if single_date:
#             if isinstance(single_date, str):
#                 try:
#                     single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     single_date = date.today()
#             if cr_opening_range_type == "before":
#                 params["cstart_date"] = date(2017, 1, 1)
#                 params["cend_date"] = single_date - timedelta(days=1)
#             elif cr_opening_range_type == "after":
#                 params["cstart_date"] = single_date + timedelta(days=1)
#                 params["cend_date"] = date.today()
#             elif cr_opening_range_type == "equal":
#                 params["cstart_date"] = single_date
#                 params["cend_date"] = single_date


# def build_main_query(filters, params):
#     selected_level = filters.get("level", "7")
#     selected_indicator = params["indicator"]

#     geo_level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
#               "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }

#     field_map = {
#         "p.partner_name": "p.partner_name AS partner",
#         "s.state_name": "s.state_name AS state",
#         "d.district_name": "d.district_name AS district",
#         "b.block_name": "b.block_name AS block",
#         "g.gp_name": "g.gp_name AS gp",
#         "u.full_name": "u.full_name AS supervisor_id",
#         "c.creche_name": "c.creche_name AS creche",
#         "c.creche_id": "c.creche_id AS creche_id"
#     }

#     additional_select = ""
#     group_by_clause = ""
#     order_by_clause = ""
#     select_fields_str = ""
#     group_by_fields = []

#     if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
#         group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
#         select_fields = [field_map[f] for f in group_by_fields if f in field_map]
#         select_fields_str = ",\n ".join(select_fields)
#         group_by_clause = ", ".join(group_by_fields)
#         order_by_clause = group_by_clause
#     else:
#         group_expr = ""
#         sort_key_expr = ""
#         alias = ""
#         if selected_level == "8":
#             group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
#             alias = "creche_age"
#             sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "9":
#             group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
#             alias = "gender"
#             additional_select = ",\n " + group_expr + " AS " + alias
#             order_by_clause = alias
#         elif selected_level == "10":
#             group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
#             alias = "age_group"
#             sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "11":
#             group_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
#                 ELSE 'Above 36'
#             END"""
#             alias = "age_at_enrollment"
#             sort_key_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "12":
#             # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
#             group_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
#                 ELSE '36+ months'
#             END"""
#             alias = "tenure_bucket"
#             sort_key_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         group_by_clause = group_expr

#     if not select_fields_str and additional_select:
#         additional_select = additional_select.lstrip(',\n ')

#     geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
#     if geo_part:
#         geo_part += ","

#     operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12"] else ""

#     p = params

#     where_conditions = ["1=1"]
#     if p["partner"]:
#         where_conditions.append("c.partner_id = %(partner)s")
#     if p["state"]:
#         where_conditions.append("c.state_id = %(state)s")
#     elif p["state_ids"]:
#         where_conditions.append("c.state_id IN %(state_ids)s")
#     if p["district"]:
#         where_conditions.append("c.district_id = %(district)s")
#     elif p["district_ids"]:
#         where_conditions.append("c.district_id IN %(district_ids)s")
#     if p["block"]:
#         where_conditions.append("c.block_id = %(block)s")
#     elif p["block_ids"]:
#         where_conditions.append("c.block_id IN %(block_ids)s")
#     if p["gp"]:
#         where_conditions.append("c.gp_id = %(gp)s")
#     elif p["gp_ids"]:
#         where_conditions.append("c.gp_id IN %(gp_ids)s")
#     if p["creche"]:
#         where_conditions.append("c.name = %(creche)s")
#     if p["supervisor_id"]:
#         where_conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if p["creche_status_id"]:
#         where_conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if p["phases"]:
#         where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#     if p["creche_age"]:
#         where_conditions.append("""
#             CASE 
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
#     where_conditions.append(
#         "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
#         "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
#     )
#     if selected_level == "10":
#         where_conditions.append(
#             "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
#         )
#     if selected_level == "12":
#         # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
#         where_conditions.append(
#             "cee.date_of_enrollment IS NOT NULL"
#         )

#     def age_filter(alias_dob, alias_date):
#         ag = p.get("age_group")
#         if ag == "6m-11m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
#         elif ag == "12m-17m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
#         elif ag == "18m-23m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
#         elif ag == "24m-29m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
#         elif ag == "30m-36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
#         elif ag == "> 36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
#         return ""

#     # INITIAL MEASUREMENT: First recorded entry ever (earliest measurement_taken_date)
#     initial_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date ASC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#             AND {selected_indicator}_zscore IS NOT NULL
#             AND TRIM({selected_indicator}_zscore) <> ''

#               AND measurement_taken_date <= %(end_date_last)s
#         ) x WHERE x.rn = 1
#     ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
#     """

    

#     # FINAL MEASUREMENT: Most recent entry ever (latest measurement_taken_date)
#     final_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date DESC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#                 AND {selected_indicator}_zscore IS NOT NULL
#                 AND TRIM({selected_indicator}_zscore) <> ''
#               AND measurement_taken_date <= %(end_date_last)s
#         ) y WHERE y.rn = 1
#     ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
#     """

#     query = f"""
#     SELECT
#         {geo_part}
#         {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
#         COUNT(DISTINCT 
#             CASE 
#                 WHEN ad_initial.measurement_date != ad_final.measurement_date 
#                 THEN cee.childenrollguid 
#             END
#         ) AS measured_twice,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS normal_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS moderate_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS severe_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} NOT IN (1,2,3) AND ad_initial.measurement_date != ad_final.measurement_date THEN 1 ELSE 0 END) AS outlier_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS sv_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS md_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS nr_nr_cnt
#     FROM `tabCreche` c
#     JOIN `tabState` s ON c.state_id = s.name
#     JOIN `tabPartner` p ON c.partner_id = p.name
#     JOIN `tabDistrict` d ON c.district_id = d.name
#     JOIN `tabBlock` b ON c.block_id = b.name
#     JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#     JOIN `tabUser` u ON u.name = c.supervisor_id
#     LEFT JOIN `tabChild Enrollment and Exit` cee
#         ON cee.creche_id = c.name
#         AND cee.date_of_enrollment <= %(end_date_last)s
#         {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
#         {age_filter("cee.child_dob", "%(end_date_first)s")}
#     {initial_measurement_subquery}
#     {final_measurement_subquery}
#     WHERE {" AND ".join(where_conditions)}
#     GROUP BY {group_by_clause}
#     ORDER BY {order_by_clause}
#     """

#     return query

















# import frappe
# from frappe import _
# from datetime import datetime, date, timedelta
# import calendar


# def execute(filters=None):
#     try:
#         selected_level = filters.get("level", "7")
#         selected_indicator = filters.get("indicator", "weight_for_age")

#         level_mapping = {
#             "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
#             "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
#             "3": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
#             ],
#             "4": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
#             ],
#             "5": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
#             ],
#             "6": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
#             ],
#             "7": [
#                 {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
#             ],
#             "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
#             "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
#             "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
#             "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
#             "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
#         }

#         variable_columns = level_mapping.get(selected_level, level_mapping["7"])

#         fixed_columns = [
#             {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
#             {"label": "Total Universe (Measured Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 290},
#             {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
#             # {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
#             {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
#             {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
#             {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
#             {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
#         ]

#         # Add Operational Creches column only for geographical levels (1-7)
#         if selected_level not in ["8", "9", "10", "11", "12"]:
#             fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

#         columns = variable_columns + fixed_columns
#         data = get_report_data(filters)

#         # Calculate totals row
#         if data:
#             totals_row = calculate_totals_row(data, filters, variable_columns)
#             data.append(totals_row)

#         return columns, data

#     except Exception as e:
#         frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
#         frappe.throw(_(f"Error in report: {str(e)}"))
#         return [], []


# def calculate_totals_row(data, filters, variable_columns):
#     selected_level = filters.get("level", "7")

#     totals_row = {'is_total': True, 'indent': 0}

#     # Set label for totals row
#     level_field_map = {
#         "1": "partner", "2": "state", "3": "district",
#         "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
#         "8": "creche_age",
#         "9": "gender",
#         "10": "age_group",
#         "11": "age_at_enrollment",
#         "12": "tenure_bucket",
#     }

#     if selected_level in level_field_map:
#         totals_row[level_field_map[selected_level]] = "Total"
#     else:
#         for col in variable_columns:
#             totals_row[col['fieldname']] = "Total"

#     # Include all numeric columns
#     total_keys = [
#         'operational_creches', 'enrolled_children', 'measured_twice',
#         'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
#         'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
#         'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
#     ]

#     totals = {k: 0 for k in total_keys}
#     for row in data:
#         for key in totals:
#             if key in row:
#                 totals[key] += row.get(key, 0) or 0

#     # Compute universe fields for totals row
#     totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

#     # Format functions
#     def fmt(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"{int(cnt)} ({pct:.2f}%)"

#     def fmt_bold(cnt):
#         return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

#     def fmt_green(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_red(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_gray(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     # Calculate transition totals
#     t_md_nr = totals['md_nr_cnt']
#     t_sv_md = totals['sv_md_cnt']
#     t_sv_nr = totals['sv_nr_cnt']
#     t_nr_md = totals['nr_md_cnt']
#     t_nr_sv = totals['nr_sv_cnt']
#     t_md_sv = totals['md_sv_cnt']
#     t_sv_sv = totals['sv_sv_cnt']
#     t_md_md = totals['md_md_cnt']
#     t_nr_nr = totals['nr_nr_cnt']

#     t_recovery = t_md_nr + t_sv_md + t_sv_nr
#     t_deterioration = t_nr_md + t_nr_sv + t_md_sv
#     t_no_change = t_sv_sv + t_md_md + t_nr_nr

#     # Calculate display values
#     md_nr_display = fmt(t_md_nr, totals['moderate_first'])
#     sv_md_display = fmt(t_sv_md, totals['severe_first'])
#     sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
#     total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
#     nr_md_display = fmt(t_nr_md, totals['normal_first'])
#     nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
#     md_sv_display = fmt(t_md_sv, totals['moderate_first'])
#     total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
#     no_change_display = fmt_gray(t_no_change, totals['normal_first'] + totals['moderate_first'] + totals['severe_first'])
#     sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
#     md_md_display = fmt(t_md_md, totals['moderate_first'])
#     nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

#     # Populate totals row
#     if selected_level not in ["8", "9", "10", "11", "12"]:
#         totals_row['operational_creches'] = totals['operational_creches']
#     totals_row['enrolled_children'] = totals['enrolled_children']
#     totals_row['measured'] = fmt_bold(totals['measured_twice'])
#     totals_row['normal_first'] = fmt_bold(totals['normal_first'])
#     totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
#     totals_row['severe_first'] = fmt_bold(totals['severe_first'])
#     totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
#     totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
#     totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

#     totals_row['md_nr_display'] = md_nr_display
#     totals_row['sv_md_display'] = sv_md_display
#     totals_row['sv_nr_display'] = sv_nr_display
#     totals_row['total_recovery_display'] = total_recovery_display
#     totals_row['nr_md_display'] = nr_md_display
#     totals_row['nr_sv_display'] = nr_sv_display
#     totals_row['md_sv_display'] = md_sv_display
#     totals_row['total_deterioration_display'] = total_deterioration_display
#     totals_row['no_change_display'] = no_change_display
#     totals_row['sv_sv_display'] = sv_sv_display
#     totals_row['md_md_display'] = md_md_display
#     totals_row['nr_nr_display'] = nr_nr_display

#     return totals_row


# def get_report_data(filters):
#     try:
#         params = build_query_params(filters)
#         query = build_main_query(filters, params)

#         # Execute query
#         data = frappe.db.sql(query, params, as_dict=True)

#         for row in data:
#             # Compute uni_recovery and uni_deterioration for each row
#             row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
#             row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

#             # Measured now counts children with both initial and final measurements on different dates
#             row['measured'] = row.get('measured_twice', 0) or 0

#             md_nr = row.get('md_nr_cnt', 0) or 0
#             sv_md = row.get('sv_md_cnt', 0) or 0
#             sv_nr = row.get('sv_nr_cnt', 0) or 0
#             nr_md = row.get('nr_md_cnt', 0) or 0
#             nr_sv = row.get('nr_sv_cnt', 0) or 0
#             md_sv = row.get('md_sv_cnt', 0) or 0
#             sv_sv = row.get('sv_sv_cnt', 0) or 0
#             md_md = row.get('md_md_cnt', 0) or 0
#             nr_nr = row.get('nr_nr_cnt', 0) or 0

#             def fmt(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"{int(cnt)} ({pct:.2f}%)"

#             def fmt_green(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_red(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_gray(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             total_recovery = md_nr + sv_md + sv_nr
#             total_deterioration = nr_md + nr_sv + md_sv
#             no_change = sv_sv + md_md + nr_nr

#             row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
#             row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
#             row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
#             row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
#             row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
#             row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
#             row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
#             row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
#             row['no_change_display'] = fmt_gray(no_change, (row.get('normal_first', 0) + row.get('moderate_first', 0) + row.get('severe_first', 0)) or 0)
#             row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
#             row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
#             row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

#         return data

#     except Exception as e:
#         frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
#         raise


# def build_query_params(filters):
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     geography_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

#     end_month = int(filters.get("month", datetime.now().month))
#     end_year = int(filters.get("year", datetime.now().year))
#     end_date_first = date(end_year, end_month, 1)
#     end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

#     state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
#     district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
#     block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
#     gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

#     params = {
#         "end_month": end_month,
#         "end_year": end_year,
#         "end_date_first": end_date_first,
#         "end_date_last": end_date_last,
#         "partner": partner_id,
#         "state": filters.get("state"),
#         "district": filters.get("district"),
#         "block": filters.get("block"),
#         "gp": filters.get("gp"),
#         "creche": filters.get("creche"),
#         "supervisor_id": filters.get("supervisor_id"),
#         "creche_status_id": filters.get("creche_status_id", "3"),
#         "state_ids": tuple(state_ids_list) if state_ids_list else None,
#         "district_ids": tuple(district_ids_list) if district_ids_list else None,
#         "block_ids": tuple(block_ids_list) if block_ids_list else None,
#         "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "age_group": filters.get("age_group"),
#         "indicator": filters.get("indicator", "weight_for_age"),
#         "gender": filters.get("gender"),
#         "creche_age": filters.get("creche_age"),
#     }

#     handle_date_filters(filters, params)

#     if filters.get("phases"):
#         try:
#             phases_cleaned = ",".join(
#                 ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
#             )
#             if phases_cleaned:
#                 params["phases"] = phases_cleaned
#         except (AttributeError, TypeError):
#             pass

#     return params


# def handle_date_filters(filters, params):
#     cr_opening_range_type = filters.get("cr_opening_range_type")
#     if cr_opening_range_type == "between":
#         c_opening_range = filters.get("c_opening_range", [None, None])
#         params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
#         params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
#     elif cr_opening_range_type in ["before", "after", "equal"]:
#         single_date = filters.get("single_date")
#         if single_date:
#             if isinstance(single_date, str):
#                 try:
#                     single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     single_date = date.today()
#             if cr_opening_range_type == "before":
#                 params["cstart_date"] = date(2017, 1, 1)
#                 params["cend_date"] = single_date - timedelta(days=1)
#             elif cr_opening_range_type == "after":
#                 params["cstart_date"] = single_date + timedelta(days=1)
#                 params["cend_date"] = date.today()
#             elif cr_opening_range_type == "equal":
#                 params["cstart_date"] = single_date
#                 params["cend_date"] = single_date


# def build_main_query(filters, params):
#     selected_level = filters.get("level", "7")
#     selected_indicator = params["indicator"]

#     geo_level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
#               "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }

#     field_map = {
#         "p.partner_name": "p.partner_name AS partner",
#         "s.state_name": "s.state_name AS state",
#         "d.district_name": "d.district_name AS district",
#         "b.block_name": "b.block_name AS block",
#         "g.gp_name": "g.gp_name AS gp",
#         "u.full_name": "u.full_name AS supervisor_id",
#         "c.creche_name": "c.creche_name AS creche",
#         "c.creche_id": "c.creche_id AS creche_id"
#     }

#     additional_select = ""
#     group_by_clause = ""
#     order_by_clause = ""
#     select_fields_str = ""
#     group_by_fields = []

#     if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
#         group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
#         select_fields = [field_map[f] for f in group_by_fields if f in field_map]
#         select_fields_str = ",\n ".join(select_fields)
#         group_by_clause = ", ".join(group_by_fields)
#         order_by_clause = group_by_clause
#     else:
#         group_expr = ""
#         sort_key_expr = ""
#         alias = ""
#         if selected_level == "8":
#             group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
#             alias = "creche_age"
#             sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "9":
#             group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
#             alias = "gender"
#             additional_select = ",\n " + group_expr + " AS " + alias
#             order_by_clause = alias
#         elif selected_level == "10":
#             group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
#             alias = "age_group"
#             sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "11":
#             group_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
#                 ELSE 'Above 36'
#             END"""
#             alias = "age_at_enrollment"
#             sort_key_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "12":
#             # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
#             group_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
#                 ELSE '36+ months'
#             END"""
#             alias = "tenure_bucket"
#             sort_key_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         group_by_clause = group_expr

#     if not select_fields_str and additional_select:
#         additional_select = additional_select.lstrip(',\n ')

#     geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
#     if geo_part:
#         geo_part += ","

#     operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12"] else ""

#     p = params

#     where_conditions = ["1=1"]
#     if p["partner"]:
#         where_conditions.append("c.partner_id = %(partner)s")
#     if p["state"]:
#         where_conditions.append("c.state_id = %(state)s")
#     elif p["state_ids"]:
#         where_conditions.append("c.state_id IN %(state_ids)s")
#     if p["district"]:
#         where_conditions.append("c.district_id = %(district)s")
#     elif p["district_ids"]:
#         where_conditions.append("c.district_id IN %(district_ids)s")
#     if p["block"]:
#         where_conditions.append("c.block_id = %(block)s")
#     elif p["block_ids"]:
#         where_conditions.append("c.block_id IN %(block_ids)s")
#     if p["gp"]:
#         where_conditions.append("c.gp_id = %(gp)s")
#     elif p["gp_ids"]:
#         where_conditions.append("c.gp_id IN %(gp_ids)s")
#     if p["creche"]:
#         where_conditions.append("c.name = %(creche)s")
#     if p["supervisor_id"]:
#         where_conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if p["creche_status_id"]:
#         where_conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if p["phases"]:
#         where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#     if p["creche_age"]:
#         where_conditions.append("""
#             CASE 
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
#     where_conditions.append(
#         "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
#         "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
#     )
#     if selected_level == "10":
#         where_conditions.append(
#             "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
#         )
#     if selected_level == "12":
#         # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
#         where_conditions.append(
#             "cee.date_of_enrollment IS NOT NULL"
#         )

#     def age_filter(alias_dob, alias_date):
#         ag = p.get("age_group")
#         if ag == "6m-11m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
#         elif ag == "12m-17m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
#         elif ag == "18m-23m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
#         elif ag == "24m-29m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
#         elif ag == "30m-36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
#         elif ag == "> 36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
#         return ""

#     # INITIAL MEASUREMENT: First recorded entry ever (earliest measurement_taken_date)
#     initial_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date ASC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#               AND {selected_indicator} IS NOT NULL
#               AND measurement_taken_date <= %(end_date_last)s
#         ) x WHERE x.rn = 1
#     ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
#     """

#     # FINAL MEASUREMENT: Most recent entry ever (latest measurement_taken_date)
#     final_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date DESC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#               AND {selected_indicator} IS NOT NULL
#               AND measurement_taken_date <= %(end_date_last)s
#         ) y WHERE y.rn = 1
#     ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
#     """

#     query = f"""
#     SELECT
#         {geo_part}
#         {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
#         COUNT(DISTINCT 
#             CASE 
#                 WHEN ad_initial.measurement_date != ad_final.measurement_date 
#                 THEN cee.childenrollguid 
#             END
#         ) AS measured_twice,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS normal_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS moderate_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS severe_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} NOT IN (1,2,3) AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS outlier_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS sv_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS md_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS nr_nr_cnt
#     FROM `tabCreche` c
#     JOIN `tabState` s ON c.state_id = s.name
#     JOIN `tabPartner` p ON c.partner_id = p.name
#     JOIN `tabDistrict` d ON c.district_id = d.name
#     JOIN `tabBlock` b ON c.block_id = b.name
#     JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#     JOIN `tabUser` u ON u.name = c.supervisor_id
#     LEFT JOIN `tabChild Enrollment and Exit` cee
#         ON cee.creche_id = c.name
#         AND cee.date_of_enrollment <= %(end_date_last)s
#         {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
#         {age_filter("cee.child_dob", "%(end_date_first)s")}
#     {initial_measurement_subquery}
#     {final_measurement_subquery}
#     WHERE {" AND ".join(where_conditions)}
#     GROUP BY {group_by_clause}
#     ORDER BY {order_by_clause}
#     """

#     return query
















# import frappe
# from frappe import _
# from datetime import datetime, date, timedelta
# import calendar


# def execute(filters=None):
#     try:
#         selected_level = filters.get("level", "7")
#         selected_indicator = filters.get("indicator", "weight_for_age")

#         level_mapping = {
#             "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
#             "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
#             "3": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
#             ],
#             "4": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
#             ],
#             "5": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
#             ],
#             "6": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
#             ],
#             "7": [
#                 {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
#             ],
#             "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
#             "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
#             "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
#             "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
#             "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
#         }

#         variable_columns = level_mapping.get(selected_level, level_mapping["7"])

#         fixed_columns = [
#             {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
#             {"label": "Measured (Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 200},
#             {"label": "Total Universe","fieldname": "total_universe", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
#             {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
#             {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
#             {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
#             {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
#             {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
#         ]

#         # Add Operational Creches column only for geographical levels (1-7)
#         if selected_level not in ["8", "9", "10", "11", "12"]:
#             fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

#         columns = variable_columns + fixed_columns
#         data = get_report_data(filters)

#         # Calculate totals row
#         if data:
#             totals_row = calculate_totals_row(data, filters, variable_columns)
#             data.append(totals_row)

#         return columns, data

#     except Exception as e:
#         frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
#         frappe.throw(_(f"Error in report: {str(e)}"))
#         return [], []


# def calculate_totals_row(data, filters, variable_columns):
#     selected_level = filters.get("level", "7")

#     totals_row = {'is_total': True, 'indent': 0}

#     # Set label for totals row
#     level_field_map = {
#         "1": "partner", "2": "state", "3": "district",
#         "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
#         "8": "creche_age",
#         "9": "gender",
#         "10": "age_group",
#         "11": "age_at_enrollment",
#         "12": "tenure_bucket",
#     }

#     if selected_level in level_field_map:
#         totals_row[level_field_map[selected_level]] = "Total"
#     else:
#         for col in variable_columns:
#             totals_row[col['fieldname']] = "Total"

#     # Include all numeric columns
#     total_keys = [
#         'operational_creches', 'enrolled_children', 'measured_twice',
#         'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
#         'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
#         'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
#     ]

#     totals = {k: 0 for k in total_keys}
#     for row in data:
#         for key in totals:
#             if key in row:
#                 totals[key] += row.get(key, 0) or 0

#     # Compute universe fields for totals row
#     totals_row['total_universe'] = totals['normal_first'] + totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

#     # Format functions
#     def fmt(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"{int(cnt)} ({pct:.2f}%)"

#     def fmt_bold(cnt):
#         return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

#     def fmt_green(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_red(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_gray(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     # Calculate transition totals
#     t_md_nr = totals['md_nr_cnt']
#     t_sv_md = totals['sv_md_cnt']
#     t_sv_nr = totals['sv_nr_cnt']
#     t_nr_md = totals['nr_md_cnt']
#     t_nr_sv = totals['nr_sv_cnt']
#     t_md_sv = totals['md_sv_cnt']
#     t_sv_sv = totals['sv_sv_cnt']
#     t_md_md = totals['md_md_cnt']
#     t_nr_nr = totals['nr_nr_cnt']

#     t_recovery = t_md_nr + t_sv_md + t_sv_nr
#     t_deterioration = t_nr_md + t_nr_sv + t_md_sv
#     t_no_change = t_sv_sv + t_md_md + t_nr_nr

#     # Calculate display values BEFORE formatting universe fields
#     md_nr_display = fmt(t_md_nr, totals['moderate_first'])
#     sv_md_display = fmt(t_sv_md, totals['severe_first'])
#     sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
#     total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
#     nr_md_display = fmt(t_nr_md, totals['normal_first'])
#     nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
#     md_sv_display = fmt(t_md_sv, totals['moderate_first'])
#     total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
#     no_change_display = fmt_gray(t_no_change, totals_row['total_universe'])
#     sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
#     md_md_display = fmt(t_md_md, totals['moderate_first'])
#     nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

#     # Populate totals row
#     if selected_level not in ["8", "9", "10", "11", "12"]:
#         totals_row['operational_creches'] = totals['operational_creches']
#     totals_row['enrolled_children'] = totals['enrolled_children']
#     totals_row['measured'] = fmt_bold(totals['measured_twice'])
#     totals_row['normal_first'] = fmt_bold(totals['normal_first'])
#     totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
#     totals_row['severe_first'] = fmt_bold(totals['severe_first'])
#     totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
#     totals_row['total_universe'] = fmt_bold(totals_row['total_universe'])
#     totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
#     totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

#     totals_row['md_nr_display'] = md_nr_display
#     totals_row['sv_md_display'] = sv_md_display
#     totals_row['sv_nr_display'] = sv_nr_display
#     totals_row['total_recovery_display'] = total_recovery_display
#     totals_row['nr_md_display'] = nr_md_display
#     totals_row['nr_sv_display'] = nr_sv_display
#     totals_row['md_sv_display'] = md_sv_display
#     totals_row['total_deterioration_display'] = total_deterioration_display
#     totals_row['no_change_display'] = no_change_display
#     totals_row['sv_sv_display'] = sv_sv_display
#     totals_row['md_md_display'] = md_md_display
#     totals_row['nr_nr_display'] = nr_nr_display

#     return totals_row


# def get_report_data(filters):
#     try:
#         params = build_query_params(filters)
#         query = build_main_query(filters, params)

#         # Execute query
#         data = frappe.db.sql(query, params, as_dict=True)

#         for row in data:
#             # Compute total_universe for each row
#             row['total_universe'] = (row.get('normal_first', 0) or 0) + (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)

#             # Compute uni_recovery and uni_deterioration for each row
#             row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
#             row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

#             # Measured now counts children with both initial and final measurements on different dates
#             row['measured'] = row.get('measured_twice', 0) or 0

#             md_nr = row.get('md_nr_cnt', 0) or 0
#             sv_md = row.get('sv_md_cnt', 0) or 0
#             sv_nr = row.get('sv_nr_cnt', 0) or 0
#             nr_md = row.get('nr_md_cnt', 0) or 0
#             nr_sv = row.get('nr_sv_cnt', 0) or 0
#             md_sv = row.get('md_sv_cnt', 0) or 0
#             sv_sv = row.get('sv_sv_cnt', 0) or 0
#             md_md = row.get('md_md_cnt', 0) or 0
#             nr_nr = row.get('nr_nr_cnt', 0) or 0

#             def fmt(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"{int(cnt)} ({pct:.2f}%)"

#             def fmt_green(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_red(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_gray(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             total_recovery = md_nr + sv_md + sv_nr
#             total_deterioration = nr_md + nr_sv + md_sv
#             no_change = sv_sv + md_md + nr_nr

#             row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
#             row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
#             row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
#             row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
#             row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
#             row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
#             row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
#             row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
#             row['no_change_display'] = fmt_gray(no_change, row.get('total_universe', 0) or 0)
#             row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
#             row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
#             row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

#         return data

#     except Exception as e:
#         frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
#         raise


# def build_query_params(filters):
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     geography_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

#     end_month = int(filters.get("month", datetime.now().month))
#     end_year = int(filters.get("year", datetime.now().year))
#     end_date_first = date(end_year, end_month, 1)
#     end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

#     state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
#     district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
#     block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
#     gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

#     params = {
#         "end_month": end_month,
#         "end_year": end_year,
#         "end_date_first": end_date_first,
#         "end_date_last": end_date_last,
#         "partner": partner_id,
#         "state": filters.get("state"),
#         "district": filters.get("district"),
#         "block": filters.get("block"),
#         "gp": filters.get("gp"),
#         "creche": filters.get("creche"),
#         "supervisor_id": filters.get("supervisor_id"),
#         "creche_status_id": filters.get("creche_status_id", "3"),
#         "state_ids": tuple(state_ids_list) if state_ids_list else None,
#         "district_ids": tuple(district_ids_list) if district_ids_list else None,
#         "block_ids": tuple(block_ids_list) if block_ids_list else None,
#         "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "age_group": filters.get("age_group"),
#         "indicator": filters.get("indicator", "weight_for_age"),
#         "gender": filters.get("gender"),
#         "creche_age": filters.get("creche_age"),
#     }

#     handle_date_filters(filters, params)

#     if filters.get("phases"):
#         try:
#             phases_cleaned = ",".join(
#                 ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
#             )
#             if phases_cleaned:
#                 params["phases"] = phases_cleaned
#         except (AttributeError, TypeError):
#             pass

#     return params


# def handle_date_filters(filters, params):
#     cr_opening_range_type = filters.get("cr_opening_range_type")
#     if cr_opening_range_type == "between":
#         c_opening_range = filters.get("c_opening_range", [None, None])
#         params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
#         params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
#     elif cr_opening_range_type in ["before", "after", "equal"]:
#         single_date = filters.get("single_date")
#         if single_date:
#             if isinstance(single_date, str):
#                 try:
#                     single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     single_date = date.today()
#             if cr_opening_range_type == "before":
#                 params["cstart_date"] = date(2017, 1, 1)
#                 params["cend_date"] = single_date - timedelta(days=1)
#             elif cr_opening_range_type == "after":
#                 params["cstart_date"] = single_date + timedelta(days=1)
#                 params["cend_date"] = date.today()
#             elif cr_opening_range_type == "equal":
#                 params["cstart_date"] = single_date
#                 params["cend_date"] = single_date


# def build_main_query(filters, params):
#     selected_level = filters.get("level", "7")
#     selected_indicator = params["indicator"]

#     geo_level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
#               "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }

#     field_map = {
#         "p.partner_name": "p.partner_name AS partner",
#         "s.state_name": "s.state_name AS state",
#         "d.district_name": "d.district_name AS district",
#         "b.block_name": "b.block_name AS block",
#         "g.gp_name": "g.gp_name AS gp",
#         "u.full_name": "u.full_name AS supervisor_id",
#         "c.creche_name": "c.creche_name AS creche",
#         "c.creche_id": "c.creche_id AS creche_id"
#     }

#     additional_select = ""
#     group_by_clause = ""
#     order_by_clause = ""
#     select_fields_str = ""
#     group_by_fields = []

#     if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
#         group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
#         select_fields = [field_map[f] for f in group_by_fields if f in field_map]
#         select_fields_str = ",\n ".join(select_fields)
#         group_by_clause = ", ".join(group_by_fields)
#         order_by_clause = group_by_clause
#     else:
#         group_expr = ""
#         sort_key_expr = ""
#         alias = ""
#         if selected_level == "8":
#             group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
#             alias = "creche_age"
#             sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "9":
#             group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
#             alias = "gender"
#             additional_select = ",\n " + group_expr + " AS " + alias
#             order_by_clause = alias
#         elif selected_level == "10":
#             group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
#             alias = "age_group"
#             sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "11":
#             group_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
#                 ELSE 'Above 36'
#             END"""
#             alias = "age_at_enrollment"
#             sort_key_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "12":
#             # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
#             group_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
#                 ELSE '36+ months'
#             END"""
#             alias = "tenure_bucket"
#             sort_key_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         group_by_clause = group_expr

#     if not select_fields_str and additional_select:
#         additional_select = additional_select.lstrip(',\n ')

#     geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
#     if geo_part:
#         geo_part += ","

#     operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12"] else ""

#     p = params

#     where_conditions = ["1=1"]
#     if p["partner"]:
#         where_conditions.append("c.partner_id = %(partner)s")
#     if p["state"]:
#         where_conditions.append("c.state_id = %(state)s")
#     elif p["state_ids"]:
#         where_conditions.append("c.state_id IN %(state_ids)s")
#     if p["district"]:
#         where_conditions.append("c.district_id = %(district)s")
#     elif p["district_ids"]:
#         where_conditions.append("c.district_id IN %(district_ids)s")
#     if p["block"]:
#         where_conditions.append("c.block_id = %(block)s")
#     elif p["block_ids"]:
#         where_conditions.append("c.block_id IN %(block_ids)s")
#     if p["gp"]:
#         where_conditions.append("c.gp_id = %(gp)s")
#     elif p["gp_ids"]:
#         where_conditions.append("c.gp_id IN %(gp_ids)s")
#     if p["creche"]:
#         where_conditions.append("c.name = %(creche)s")
#     if p["supervisor_id"]:
#         where_conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if p["creche_status_id"]:
#         where_conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if p["phases"]:
#         where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#     if p["creche_age"]:
#         where_conditions.append("""
#             CASE 
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
#     where_conditions.append(
#         "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
#         "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
#     )
#     if selected_level == "10":
#         where_conditions.append(
#             "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
#         )
#     if selected_level == "12":
#         # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
#         where_conditions.append(
#             "cee.date_of_enrollment IS NOT NULL"
#         )

#     def age_filter(alias_dob, alias_date):
#         ag = p.get("age_group")
#         if ag == "6m-11m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
#         elif ag == "12m-17m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
#         elif ag == "18m-23m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
#         elif ag == "24m-29m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
#         elif ag == "30m-36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
#         elif ag == "> 36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
#         return ""

#     # INITIAL MEASUREMENT: First recorded entry ever (earliest measurement_taken_date)
#     initial_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date ASC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#               AND {selected_indicator} IS NOT NULL
#               AND measurement_taken_date <= %(end_date_last)s
#         ) x WHERE x.rn = 1
#     ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
#     """

#     # FINAL MEASUREMENT: Most recent entry ever (latest measurement_taken_date)
#     final_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT * FROM (
#             SELECT 
#                 childenrollguid, 
#                 {selected_indicator},
#                 measurement_taken_date AS measurement_date,
#                 ROW_NUMBER() OVER (PARTITION BY childenrollguid ORDER BY measurement_taken_date DESC) as rn
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#               AND {selected_indicator} IS NOT NULL
#               AND measurement_taken_date <= %(end_date_last)s
#         ) y WHERE y.rn = 1
#     ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
#     """

#     query = f"""
#     SELECT
#         {geo_part}
#         {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
#         COUNT(DISTINCT 
#             CASE 
#                 WHEN ad_initial.measurement_date != ad_final.measurement_date 
#                 THEN cee.childenrollguid 
#             END
#         ) AS measured_twice,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS normal_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS moderate_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS severe_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} NOT IN (1,2,3) AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS outlier_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS sv_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS md_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS nr_nr_cnt
#     FROM `tabCreche` c
#     JOIN `tabState` s ON c.state_id = s.name
#     JOIN `tabPartner` p ON c.partner_id = p.name
#     JOIN `tabDistrict` d ON c.district_id = d.name
#     JOIN `tabBlock` b ON c.block_id = b.name
#     JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#     JOIN `tabUser` u ON u.name = c.supervisor_id
#     LEFT JOIN `tabChild Enrollment and Exit` cee
#         ON cee.creche_id = c.name
#         AND cee.date_of_enrollment <= %(end_date_last)s
#         {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
#         {age_filter("cee.child_dob", "%(end_date_first)s")}
#     {initial_measurement_subquery}
#     {final_measurement_subquery}
#     WHERE {" AND ".join(where_conditions)}
#     GROUP BY {group_by_clause}
#     ORDER BY {order_by_clause}
#     """

#     return query





















# import frappe
# from frappe import _
# from datetime import datetime, date, timedelta
# import calendar


# def execute(filters=None):
#     try:
#         selected_level = filters.get("level", "7")
#         selected_indicator = filters.get("indicator", "weight_for_age")

#         level_mapping = {
#             "1": [{"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180}],
#             "2": [{"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180}],
#             "3": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180}
#             ],
#             "4": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180}
#             ],
#             "5": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180}
#             ],
#             "6": [
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180}
#             ],
#             "7": [
#                 {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 180},
#                 {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 180},
#                 {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 180},
#                 {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 180},
#                 {"label": "Gram Panchayat", "fieldname": "gp", "fieldtype": "Data", "width": 180},
#                 {"label": "Supervisor", "fieldname": "supervisor_id", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche", "fieldname": "creche", "fieldtype": "Data", "width": 180},
#                 {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 180}
#             ],
#             "8": [{"label": "Age of Creche", "fieldname": "creche_age", "fieldtype": "Data", "width": 180}],
#             "9": [{"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 180}],
#             "10": [{"label": "Age of Child", "fieldname": "age_group", "fieldtype": "Data", "width": 180}],
#             "11": [{"label": "Age at Enrollment", "fieldname": "age_at_enrollment", "fieldtype": "Data", "width": 180}],
#             "12": [{"label": "Tenure of Stay at Creche", "fieldname": "tenure_bucket", "fieldtype": "Data", "width": 200}],
#         }

#         variable_columns = level_mapping.get(selected_level, level_mapping["7"])

#         fixed_columns = [
#             {"label": "Cumulative Enrolled Children", "fieldname": "enrolled_children", "fieldtype": "Int", "width": 240},
#             {"label": "Measured (Atleast Twice)", "fieldname": "measured", "fieldtype": "Data", "width": 200},
#             {"label": "Total Universe","fieldname": "total_universe", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Normal)","fieldname": "normal_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Moderate)","fieldname": "moderate_first", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Severe)","fieldname": "severe_first", "fieldtype": "Data", "width": 180},
#             {"label": "Outlier (First value)", "fieldname": "outlier_first", "fieldtype": "Data", "width": 200},
#             {"label": "Universe (Recovery)","fieldname": "uni_recovery", "fieldtype": "Data", "width": 180},
#             {"label": "Universe (Deterioration)","fieldname": "uni_deterioration", "fieldtype": "Data", "width": 200},
#             {"label": "Moderate to Normal", "fieldname": "md_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Moderate", "fieldname": "sv_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Severe to Normal", "fieldname": "sv_nr_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Recovery", "fieldname": "total_recovery_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Moderate", "fieldname": "nr_md_display", "fieldtype": "Data", "width": 180},
#             {"label": "Normal to Severe", "fieldname": "nr_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Moderate to Severe", "fieldname": "md_sv_display", "fieldtype": "Data", "width": 180},
#             {"label": "Total Deterioration", "fieldname": "total_deterioration_display", "fieldtype": "Data", "width": 200},
#             {"label": "No Change", "fieldname": "no_change_display", "fieldtype": "Data", "width": 180},
#             {"label": "(No Change) Severe to Severe", "fieldname": "sv_sv_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Moderate to Moderate", "fieldname": "md_md_display", "fieldtype": "Data", "width": 250},
#             {"label": "(No Change) Normal to Normal", "fieldname": "nr_nr_display", "fieldtype": "Data", "width": 250},
#         ]

#         # Add Operational Creches column only for geographical levels (1-7)
#         if selected_level not in ["8", "9", "10", "11", "12"]:
#             fixed_columns.insert(0, {"label": "Operational Creches", "fieldname": "operational_creches", "fieldtype": "Int", "width": 180})

#         columns = variable_columns + fixed_columns
#         data = get_report_data(filters)

#         # Calculate totals row
#         if data:
#             totals_row = calculate_totals_row(data, filters, variable_columns)
#             data.append(totals_row)

#         return columns, data

#     except Exception as e:
#         frappe.log_error(f"Report Error: {str(e)}", "Growth Transition Error")
#         frappe.throw(_(f"Error in report: {str(e)}"))
#         return [], []


# def calculate_totals_row(data, filters, variable_columns):
#     selected_level = filters.get("level", "7")

#     totals_row = {'is_total': True, 'indent': 0}

#     # Set label for totals row
#     level_field_map = {
#         "1": "partner", "2": "state", "3": "district",
#         "4": "block", "5": "supervisor_id", "6": "gp", "7": "partner",
#         "8": "creche_age",
#         "9": "gender",
#         "10": "age_group",
#         "11": "age_at_enrollment",
#         "12": "tenure_bucket",
#     }

#     if selected_level in level_field_map:
#         totals_row[level_field_map[selected_level]] = "Total"
#     else:
#         for col in variable_columns:
#             totals_row[col['fieldname']] = "Total"

#     # Include all numeric columns
#     total_keys = [
#         'operational_creches', 'enrolled_children', 'measured',
#         'normal_first', 'moderate_first', 'severe_first', 'outlier_first',
#         'md_nr_cnt', 'sv_md_cnt', 'sv_nr_cnt', 'nr_md_cnt', 'nr_sv_cnt', 'md_sv_cnt',
#         'sv_sv_cnt', 'md_md_cnt', 'nr_nr_cnt'
#     ]

#     totals = {k: 0 for k in total_keys}
#     for row in data:
#         for key in totals:
#             if key in row:
#                 totals[key] += row.get(key, 0) or 0

#     # Compute universe fields for totals row
#     totals_row['total_universe'] = totals['normal_first'] + totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_recovery'] = totals['moderate_first'] + totals['severe_first']
#     totals_row['uni_deterioration'] = totals['moderate_first'] + totals['normal_first']

#     # Format functions
#     def fmt(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"{int(cnt)} ({pct:.2f}%)"

#     def fmt_bold(cnt):
#         return f"<span style='font-weight:600;color:#000000;'>{int(cnt)}</span>"

#     def fmt_green(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_red(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     def fmt_gray(cnt, x):
#         pct = round((cnt / x) * 100, 2) if x > 0 else 0
#         return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#     # Calculate transition totals
#     t_md_nr = totals['md_nr_cnt']
#     t_sv_md = totals['sv_md_cnt']
#     t_sv_nr = totals['sv_nr_cnt']
#     t_nr_md = totals['nr_md_cnt']
#     t_nr_sv = totals['nr_sv_cnt']
#     t_md_sv = totals['md_sv_cnt']
#     t_sv_sv = totals['sv_sv_cnt']
#     t_md_md = totals['md_md_cnt']
#     t_nr_nr = totals['nr_nr_cnt']

#     t_recovery = t_md_nr + t_sv_md + t_sv_nr
#     t_deterioration = t_nr_md + t_nr_sv + t_md_sv
#     t_no_change = t_sv_sv + t_md_md + t_nr_nr

#     # Calculate display values BEFORE formatting universe fields
#     md_nr_display = fmt(t_md_nr, totals['moderate_first'])
#     sv_md_display = fmt(t_sv_md, totals['severe_first'])
#     sv_nr_display = fmt(t_sv_nr, totals['severe_first'])
#     total_recovery_display = fmt_green(t_recovery, totals_row['uni_recovery'])
#     nr_md_display = fmt(t_nr_md, totals['normal_first'])
#     nr_sv_display = fmt(t_nr_sv, totals['normal_first'])
#     md_sv_display = fmt(t_md_sv, totals['moderate_first'])
#     total_deterioration_display = fmt_red(t_deterioration, totals_row['uni_deterioration'])
#     no_change_display = fmt_gray(t_no_change, totals_row['total_universe'])
#     sv_sv_display = fmt(t_sv_sv, totals['severe_first'])
#     md_md_display = fmt(t_md_md, totals['moderate_first'])
#     nr_nr_display = fmt(t_nr_nr, totals['normal_first'])

#     # Populate totals row
#     if selected_level not in ["8", "9", "10", "11", "12"]:
#         totals_row['operational_creches'] = totals['operational_creches']
#     totals_row['enrolled_children'] = totals['enrolled_children']
#     totals_row['measured'] = fmt_bold(totals['measured'])
#     totals_row['normal_first'] = fmt_bold(totals['normal_first'])
#     totals_row['moderate_first'] = fmt_bold(totals['moderate_first'])
#     totals_row['severe_first'] = fmt_bold(totals['severe_first'])
#     totals_row['outlier_first'] = fmt_bold(totals['outlier_first'])
#     totals_row['total_universe'] = fmt_bold(totals_row['total_universe'])
#     totals_row['uni_recovery'] = fmt_bold(totals_row['uni_recovery'])
#     totals_row['uni_deterioration'] = fmt_bold(totals_row['uni_deterioration'])

#     totals_row['md_nr_display'] = md_nr_display
#     totals_row['sv_md_display'] = sv_md_display
#     totals_row['sv_nr_display'] = sv_nr_display
#     totals_row['total_recovery_display'] = total_recovery_display
#     totals_row['nr_md_display'] = nr_md_display
#     totals_row['nr_sv_display'] = nr_sv_display
#     totals_row['md_sv_display'] = md_sv_display
#     totals_row['total_deterioration_display'] = total_deterioration_display
#     totals_row['no_change_display'] = no_change_display
#     totals_row['sv_sv_display'] = sv_sv_display
#     totals_row['md_md_display'] = md_md_display
#     totals_row['nr_nr_display'] = nr_nr_display

#     return totals_row


# def get_report_data(filters):
#     try:
#         params = build_query_params(filters)
#         query = build_main_query(filters, params)

#         # Execute query
#         data = frappe.db.sql(query, params, as_dict=True)

#         for row in data:
#             # Compute total_universe for each row
#             row['total_universe'] = (row.get('normal_first', 0) or 0) + (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)

#             # Compute uni_recovery and uni_deterioration for each row
#             row['uni_recovery'] = (row.get('moderate_first', 0) or 0) + (row.get('severe_first', 0) or 0)
#             row['uni_deterioration'] = (row.get('moderate_first', 0) or 0) + (row.get('normal_first', 0) or 0)

#             # Measured now counts children with both initial and final measurements
#             row['measured'] = row.get('measured_twice', 0) or 0

#             md_nr = row.get('md_nr_cnt', 0) or 0
#             sv_md = row.get('sv_md_cnt', 0) or 0
#             sv_nr = row.get('sv_nr_cnt', 0) or 0
#             nr_md = row.get('nr_md_cnt', 0) or 0
#             nr_sv = row.get('nr_sv_cnt', 0) or 0
#             md_sv = row.get('md_sv_cnt', 0) or 0
#             sv_sv = row.get('sv_sv_cnt', 0) or 0
#             md_md = row.get('md_md_cnt', 0) or 0
#             nr_nr = row.get('nr_nr_cnt', 0) or 0

#             def fmt(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"{int(cnt)} ({pct:.2f}%)"

#             def fmt_green(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#b7eb8f;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_red(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#ffccc7;color:#000000;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             def fmt_gray(cnt, x):
#                 pct = round((cnt / x) * 100, 2) if x > 0 else 0
#                 return f"<span style='background-color:#f0f0f0;color:#595959;padding:2px 6px;border-radius:3px;font-weight:600;display:inline-block;width:100%;text-align:center'>{int(cnt)} ({pct:.2f}%)</span>"

#             total_recovery = md_nr + sv_md + sv_nr
#             total_deterioration = nr_md + nr_sv + md_sv
#             no_change = sv_sv + md_md + nr_nr

#             row['md_nr_display'] = fmt(md_nr, row.get('moderate_first', 0) or 0)
#             row['sv_md_display'] = fmt(sv_md, row.get('severe_first', 0) or 0)
#             row['sv_nr_display'] = fmt(sv_nr, row.get('severe_first', 0) or 0)
#             row['total_recovery_display'] = fmt_green(total_recovery, row.get('uni_recovery', 0) or 0)
#             row['nr_md_display'] = fmt(nr_md, row.get('normal_first', 0) or 0)
#             row['nr_sv_display'] = fmt(nr_sv, row.get('normal_first', 0) or 0)
#             row['md_sv_display'] = fmt(md_sv, row.get('moderate_first', 0) or 0)
#             row['total_deterioration_display'] = fmt_red(total_deterioration, row.get('uni_deterioration', 0) or 0)
#             row['no_change_display'] = fmt_gray(no_change, row.get('total_universe', 0) or 0)
#             row['sv_sv_display'] = fmt(sv_sv, row.get('severe_first', 0) or 0)
#             row['md_md_display'] = fmt(md_md, row.get('moderate_first', 0) or 0)
#             row['nr_nr_display'] = fmt(nr_nr, row.get('normal_first', 0) or 0)

#         return data

#     except Exception as e:
#         frappe.log_error(f"Database Error in get_report_data: {str(e)}", "Growth Transition DB Error")
#         raise


# def build_query_params(filters):
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     partner_id = filters.get("partner") or current_user_partner

#     geography_query = """
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_geography = frappe.db.sql(geography_query, (frappe.session.user,), as_dict=True)

#     end_month = int(filters.get("month", datetime.now().month))
#     end_year = int(filters.get("year", datetime.now().year))
#     end_date_first = date(end_year, end_month, 1)
#     end_date_last = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

#     if end_month > 1:
#         fallback_month = end_month - 1
#         fallback_year = end_year
#     else:
#         fallback_month = 12
#         fallback_year = end_year - 1
#     fallback_start = date(fallback_year, fallback_month, 1)

#     # Initial month = previous month, Final month = selected month
#     initial_start = fallback_start
#     initial_end = date(fallback_year, fallback_month, calendar.monthrange(fallback_year, fallback_month)[1])

#     state_ids_list = [g["state_id"] for g in current_user_geography if g.get("state_id")]
#     district_ids_list = [g["district_id"] for g in current_user_geography if g.get("district_id")]
#     block_ids_list = [g["block_id"] for g in current_user_geography if g.get("block_id")]
#     gp_ids_list = [g["gp_id"] for g in current_user_geography if g.get("gp_id")]

#     params = {
#         "end_month": end_month,
#         "end_year": end_year,
#         "end_date_first": end_date_first,
#         "end_date_last": end_date_last,
#         "fallback_start": fallback_start,
#         "initial_start": initial_start,
#         "initial_end": initial_end,
#         "final_start": end_date_first,
#         "final_end": end_date_last,
#         "partner": partner_id,
#         "state": filters.get("state"),
#         "district": filters.get("district"),
#         "block": filters.get("block"),
#         "gp": filters.get("gp"),
#         "creche": filters.get("creche"),
#         "supervisor_id": filters.get("supervisor_id"),
#         "creche_status_id": filters.get("creche_status_id", "3"),
#         "state_ids": tuple(state_ids_list) if state_ids_list else None,
#         "district_ids": tuple(district_ids_list) if district_ids_list else None,
#         "block_ids": tuple(block_ids_list) if block_ids_list else None,
#         "gp_ids": tuple(gp_ids_list) if gp_ids_list else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "age_group": filters.get("age_group"),
#         "indicator": filters.get("indicator", "weight_for_age"),
#         "gender": filters.get("gender"),
#         "creche_age": filters.get("creche_age"),
#     }

#     handle_date_filters(filters, params)

#     if filters.get("phases"):
#         try:
#             phases_cleaned = ",".join(
#                 ph.strip() for ph in filters["phases"].split(",") if ph.strip().isdigit()
#             )
#             if phases_cleaned:
#                 params["phases"] = phases_cleaned
#         except (AttributeError, TypeError):
#             pass

#     return params


# def handle_date_filters(filters, params):
#     cr_opening_range_type = filters.get("cr_opening_range_type")
#     if cr_opening_range_type == "between":
#         c_opening_range = filters.get("c_opening_range", [None, None])
#         params["cstart_date"] = c_opening_range[0] if c_opening_range and len(c_opening_range) > 0 else None
#         params["cend_date"] = c_opening_range[1] if c_opening_range and len(c_opening_range) > 1 else None
#     elif cr_opening_range_type in ["before", "after", "equal"]:
#         single_date = filters.get("single_date")
#         if single_date:
#             if isinstance(single_date, str):
#                 try:
#                     single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
#                 except ValueError:
#                     single_date = date.today()
#             if cr_opening_range_type == "before":
#                 params["cstart_date"] = date(2017, 1, 1)
#                 params["cend_date"] = single_date - timedelta(days=1)
#             elif cr_opening_range_type == "after":
#                 params["cstart_date"] = single_date + timedelta(days=1)
#                 params["cend_date"] = date.today()
#             elif cr_opening_range_type == "equal":
#                 params["cstart_date"] = single_date
#                 params["cend_date"] = single_date


# def build_main_query(filters, params):
#     selected_level = filters.get("level", "7")
#     selected_indicator = params["indicator"]

#     geo_level_mapping = {
#         "1": ["p.partner_name"],
#         "2": ["s.state_name"],
#         "3": ["s.state_name", "d.district_name"],
#         "4": ["s.state_name", "d.district_name", "b.block_name"],
#         "5": ["s.state_name", "d.district_name", "b.block_name", "u.full_name"],
#         "6": ["s.state_name", "d.district_name", "b.block_name", "g.gp_name"],
#         "7": ["p.partner_name", "s.state_name", "d.district_name", "b.block_name",
#               "g.gp_name", "u.full_name", "c.creche_name", "c.creche_id"],
#     }

#     field_map = {
#         "p.partner_name": "p.partner_name AS partner",
#         "s.state_name": "s.state_name AS state",
#         "d.district_name": "d.district_name AS district",
#         "b.block_name": "b.block_name AS block",
#         "g.gp_name": "g.gp_name AS gp",
#         "u.full_name": "u.full_name AS supervisor_id",
#         "c.creche_name": "c.creche_name AS creche",
#         "c.creche_id": "c.creche_id AS creche_id"
#     }

#     additional_select = ""
#     group_by_clause = ""
#     order_by_clause = ""
#     select_fields_str = ""
#     group_by_fields = []

#     if selected_level in ["1", "2", "3", "4", "5", "6", "7"]:
#         group_by_fields = geo_level_mapping.get(selected_level, geo_level_mapping["7"])
#         select_fields = [field_map[f] for f in group_by_fields if f in field_map]
#         select_fields_str = ",\n ".join(select_fields)
#         group_by_clause = ", ".join(group_by_fields)
#         order_by_clause = group_by_clause
#     else:
#         group_expr = ""
#         sort_key_expr = ""
#         alias = ""
#         if selected_level == "8":
#             group_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 'Unknown' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month' WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month' ELSE '' END"
#             alias = "creche_age"
#             sort_key_expr = "CASE WHEN c.creche_opening_date IS NULL THEN 6 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN 1 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN 2 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN 3 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN 4 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN 5 ELSE 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "9":
#             group_expr = "CASE WHEN cee.gender_id = '1' THEN 'Male' WHEN cee.gender_id = '2' THEN 'Female' ELSE 'Other' END"
#             alias = "gender"
#             additional_select = ",\n " + group_expr + " AS " + alias
#             order_by_clause = alias
#         elif selected_level == "10":
#             group_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN '6m-11m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN '12m-17m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN '18m-23m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN '24m-29m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN '30m-36m' WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN '> 36m' END"
#             alias = "age_group"
#             sort_key_expr = "CASE WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11 THEN 1 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17 THEN 2 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23 THEN 3 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29 THEN 4 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36 THEN 5 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36 THEN 6 END AS sort_key"
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "11":
#             group_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 'Outlier'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN '6-12m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN '12-18m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN '18-24m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN '24-30m'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN '30-36m'
#                 ELSE 'Above 36'
#             END"""
#             alias = "age_at_enrollment"
#             sort_key_expr = """CASE 
#                 WHEN cee.child_dob IS NULL OR cee.date_of_enrollment IS NULL OR cee.date_of_enrollment < cee.child_dob THEN 7
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.child_dob, cee.date_of_enrollment) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         elif selected_level == "12":
#             # Use end_date_last as the cutoff; if date_of_exit is NULL, use end_date_last.
#             group_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN '6-11 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN '12-17 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN '18-23 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN '24-29 months'
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN '30-36 months'
#                 ELSE '36+ months'
#             END"""
#             alias = "tenure_bucket"
#             sort_key_expr = """CASE 
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 6 AND 11 THEN 1
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 12 AND 17 THEN 2
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 18 AND 23 THEN 3
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 24 AND 29 THEN 4
#                 WHEN TIMESTAMPDIFF(MONTH, cee.date_of_enrollment, LEAST(COALESCE(cee.date_of_exit, %(end_date_last)s), %(end_date_last)s)) BETWEEN 30 AND 36 THEN 5
#                 ELSE 6
#             END AS sort_key"""
#             additional_select = ",\n " + group_expr + " AS " + alias + ",\n " + sort_key_expr
#             order_by_clause = "sort_key"
#         group_by_clause = group_expr

#     if not select_fields_str and additional_select:
#         additional_select = additional_select.lstrip(',\n ')

#     geo_part = f"{select_fields_str}{additional_select}".rstrip(",")
#     if geo_part:
#         geo_part += ","

#     operational_part = "COUNT(DISTINCT c.name) AS operational_creches,\n " if selected_level not in ["8", "9", "10", "11", "12"] else ""

#     p = params

#     where_conditions = ["1=1"]
#     if p["partner"]:
#         where_conditions.append("c.partner_id = %(partner)s")
#     if p["state"]:
#         where_conditions.append("c.state_id = %(state)s")
#     elif p["state_ids"]:
#         where_conditions.append("c.state_id IN %(state_ids)s")
#     if p["district"]:
#         where_conditions.append("c.district_id = %(district)s")
#     elif p["district_ids"]:
#         where_conditions.append("c.district_id IN %(district_ids)s")
#     if p["block"]:
#         where_conditions.append("c.block_id = %(block)s")
#     elif p["block_ids"]:
#         where_conditions.append("c.block_id IN %(block_ids)s")
#     if p["gp"]:
#         where_conditions.append("c.gp_id = %(gp)s")
#     elif p["gp_ids"]:
#         where_conditions.append("c.gp_id IN %(gp_ids)s")
#     if p["creche"]:
#         where_conditions.append("c.name = %(creche)s")
#     if p["supervisor_id"]:
#         where_conditions.append("c.supervisor_id = %(supervisor_id)s")
#     if p["creche_status_id"]:
#         where_conditions.append("c.creche_status_id = %(creche_status_id)s")
#     if p["phases"]:
#         where_conditions.append("FIND_IN_SET(c.phase, %(phases)s)")
#     if p["creche_age"]:
#         where_conditions.append("""
#             CASE 
#                 WHEN c.creche_opening_date IS NULL THEN ''
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 0 AND 6 THEN '0-6 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 7 AND 12 THEN '7-12 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 13 AND 18 THEN '13-18 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) BETWEEN 19 AND 24 THEN '19-24 Month'
#                 WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(end_date_first)s) >= 24 THEN '24+ Month'
#                 ELSE ''
#             END = %(creche_age)s
#         """)
#     where_conditions.append(
#         "((%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) "
#         "OR (c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s))"
#     )
#     if selected_level == "10":
#         where_conditions.append(
#             "cee.child_dob IS NOT NULL AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) >= 6"
#         )
#     if selected_level == "12":
#         # Allow NULL date_of_exit (still enrolled) and include all children with enrollment date.
#         where_conditions.append(
#             "cee.date_of_enrollment IS NOT NULL"
#         )

#     def age_filter(alias_dob, alias_date):
#         ag = p.get("age_group")
#         if ag == "6m-11m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 6 AND 11"
#         elif ag == "12m-17m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 12 AND 17"
#         elif ag == "18m-23m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 18 AND 23"
#         elif ag == "24m-29m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 24 AND 29"
#         elif ag == "30m-36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) BETWEEN 30 AND 36"
#         elif ag == "> 36m":
#             return f"AND TIMESTAMPDIFF(MONTH, {alias_dob}, {alias_date}) > 36"
#         return ""

#     final_measurement_subquery = f"""
#     LEFT JOIN (
#         SELECT 
#             ad.childenrollguid,
#             MAX(ad.{selected_indicator}) AS {selected_indicator},
#             ld.max_date AS measurement_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN (
#             SELECT 
#                 childenrollguid, 
#                 MAX(measurement_taken_date) AS max_date
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#               AND {selected_indicator} IS NOT NULL
#               AND measurement_taken_date <= %(final_end)s
#             GROUP BY childenrollguid
#         ) ld ON ld.childenrollguid = ad.childenrollguid 
#            AND ad.measurement_taken_date = ld.max_date
#         WHERE ad.do_you_have_height_weight = 1 
#           AND ad.{selected_indicator} IS NOT NULL
#         GROUP BY ad.childenrollguid
#     ) ad_final ON ad_final.childenrollguid = cee.childenrollguid
#     """

#     query = f"""
#     SELECT
#         {geo_part}
#         {operational_part}COUNT(DISTINCT cee.name) AS enrolled_children,
#         COUNT(DISTINCT CASE WHEN ad_initial.childenrollguid IS NOT NULL AND ad_final.childenrollguid IS NOT NULL THEN cee.childenrollguid END) AS measured_twice,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS normal_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS moderate_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS severe_first,
#         SUM(CASE WHEN ad_initial.{selected_indicator} NOT IN (1,2,3) AND ad_final.childenrollguid IS NOT NULL THEN 1 ELSE 0 END) AS outlier_first,
#         COUNT(DISTINCT CASE WHEN ad_initial.childenrollguid IS NOT NULL THEN ad_initial.childenrollguid END) AS measurements_taken_initial,
#         COUNT(DISTINCT CASE WHEN ad_final.childenrollguid IS NOT NULL THEN ad_final.childenrollguid END) AS measurements_taken_final,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS md_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS sv_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS sv_nr_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS nr_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS md_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS nr_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 1 AND ad_final.{selected_indicator} = 1 THEN 1 ELSE 0 END) AS sv_sv_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 2 AND ad_final.{selected_indicator} = 2 THEN 1 ELSE 0 END) AS md_md_cnt,
#         SUM(CASE WHEN ad_initial.{selected_indicator} = 3 AND ad_final.{selected_indicator} = 3 THEN 1 ELSE 0 END) AS nr_nr_cnt
#     FROM `tabCreche` c
#     JOIN `tabState` s ON c.state_id = s.name
#     JOIN `tabPartner` p ON c.partner_id = p.name
#     JOIN `tabDistrict` d ON c.district_id = d.name
#     JOIN `tabBlock` b ON c.block_id = b.name
#     JOIN `tabGram Panchayat` g ON c.gp_id = g.name
#     JOIN `tabUser` u ON u.name = c.supervisor_id
#     LEFT JOIN `tabChild Enrollment and Exit` cee
#         ON cee.creche_id = c.name
#         AND cee.date_of_enrollment <= %(final_end)s
#         {f"AND cee.gender_id = %(gender)s" if p["gender"] else ""}
#         {age_filter("cee.child_dob", "%(end_date_first)s")}
#     LEFT JOIN (
#         SELECT 
#             ad.childenrollguid,
#             MAX(ad.{selected_indicator}) AS {selected_indicator},
#             id.max_date AS measurement_date
#         FROM `tabAnthropromatic Data` ad
#         INNER JOIN (
#             SELECT 
#                 childenrollguid, 
#                 MAX(measurement_taken_date) AS max_date
#             FROM `tabAnthropromatic Data`
#             WHERE do_you_have_height_weight = 1 
#               AND {selected_indicator} IS NOT NULL
#               AND measurement_taken_date BETWEEN %(initial_start)s AND %(initial_end)s
#             GROUP BY childenrollguid
#         ) id ON id.childenrollguid = ad.childenrollguid 
#            AND ad.measurement_taken_date = id.max_date
#         WHERE ad.do_you_have_height_weight = 1 
#           AND ad.{selected_indicator} IS NOT NULL
#         GROUP BY ad.childenrollguid
#     ) ad_initial ON ad_initial.childenrollguid = cee.childenrollguid
#     {final_measurement_subquery}
#     WHERE {" AND ".join(where_conditions)}
#     GROUP BY {group_by_clause}
#     ORDER BY {order_by_clause}
#     """

#     return query


