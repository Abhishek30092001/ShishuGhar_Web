import frappe
from frappe import _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import calendar
import json

# WHO plausible weight/height ranges by age in completed months (6-36 months).
# Values outside these ranges are considered data-entry errors (implausible).
WHO_WEIGHT_RANGE = {
    "M": {
        6: (5.1, 11.0), 7: (5.4, 11.4), 8: (5.6, 11.9), 9: (5.8, 12.3),
        10: (5.9, 12.7), 11: (6.1, 13.0), 12: (6.2, 13.3), 13: (6.3, 13.7),
        14: (6.5, 14.0), 15: (6.6, 14.3), 16: (6.7, 14.6), 17: (6.8, 14.9),
        18: (6.9, 15.1), 19: (7.1, 15.4), 20: (7.2, 15.7), 21: (7.3, 16.0),
        22: (7.4, 16.2), 23: (7.6, 16.5), 24: (7.7, 16.8), 25: (7.8, 17.1),
        26: (7.9, 17.3), 27: (8.0, 17.6), 28: (8.1, 17.9), 29: (8.2, 18.2),
        30: (8.3, 18.4), 31: (8.4, 18.7), 32: (8.5, 19.0), 33: (8.6, 19.3),
        34: (8.7, 19.6), 35: (8.8, 19.8), 36: (8.9, 20.1),
    },
    "F": {
        6: (4.5, 10.2), 7: (4.7, 10.6), 8: (4.9, 11.1), 9: (5.0, 11.4),
        10: (5.2, 11.8), 11: (5.3, 12.2), 12: (5.4, 12.5), 13: (5.6, 12.8),
        14: (5.7, 13.1), 15: (5.8, 13.4), 16: (5.9, 13.7), 17: (6.0, 14.0),
        18: (6.1, 14.3), 19: (6.2, 14.6), 20: (6.3, 14.9), 21: (6.5, 15.2),
        22: (6.6, 15.5), 23: (6.7, 15.8), 24: (6.8, 16.1), 25: (6.9, 16.4),
        26: (7.0, 16.7), 27: (7.1, 17.0), 28: (7.2, 17.3), 29: (7.3, 17.6),
        30: (7.4, 17.9), 31: (7.5, 18.2), 32: (7.6, 18.5), 33: (7.7, 18.8),
        34: (7.8, 19.1), 35: (7.9, 19.4), 36: (8.0, 19.7),
    },
}

WHO_HEIGHT_RANGE = {
    "M": {
        6: (60.4, 75.4), 7: (61.7, 77.1), 8: (63.0, 78.7), 9: (64.3, 80.3),
        10: (65.4, 81.7), 11: (66.5, 83.2), 12: (67.6, 84.5), 13: (68.6, 85.9),
        14: (69.6, 87.1), 15: (70.6, 88.4), 16: (71.6, 89.6), 17: (72.5, 90.8),
        18: (73.4, 92.0), 19: (74.3, 93.1), 20: (75.2, 94.2), 21: (76.0, 95.3),
        22: (76.8, 96.4), 23: (77.7, 97.4), 24: (78.0, 97.7), 25: (78.6, 98.7),
        26: (79.3, 99.6), 27: (79.9, 100.5), 28: (80.5, 101.4), 29: (81.1, 102.3),
        30: (81.7, 103.1), 31: (82.3, 104.0), 32: (82.8, 104.8), 33: (83.4, 105.6),
        34: (83.9, 106.4), 35: (84.4, 107.2), 36: (85.0, 108.0),
    },
    "F": {
        6: (58.6, 73.5), 7: (59.9, 75.3), 8: (61.2, 76.9), 9: (62.5, 78.5),
        10: (63.7, 80.0), 11: (64.9, 81.5), 12: (66.0, 82.9), 13: (67.0, 84.3),
        14: (68.0, 85.7), 15: (69.0, 87.0), 16: (70.0, 88.2), 17: (70.9, 89.4),
        18: (71.8, 90.7), 19: (72.8, 91.9), 20: (73.7, 93.1), 21: (74.5, 94.2),
        22: (75.2, 95.4), 23: (76.0, 96.5), 24: (76.0, 96.9), 25: (76.8, 98.0),
        26: (77.5, 99.0), 27: (78.1, 100.1), 28: (78.8, 101.1), 29: (79.5, 102.0),
        30: (80.1, 103.0), 31: (80.7, 103.9), 32: (81.3, 104.9), 33: (81.9, 105.8),
        34: (82.5, 106.7), 35: (83.1, 107.5), 36: (83.6, 108.4),
    },
}


def get_month_dates(year, month, n_months):
    """Return a list of `n_months` month-end dates ordered NEWEST -> OLDEST.

    The first element (slot m1) is the selected month; each subsequent slot
    steps one month further back in time.
    """
    selected = date(year, month, calendar.monthrange(year, month)[1])
    months = [selected]
    for _i in range(1, n_months):
        prev_raw = months[-1] - relativedelta(months=1)
        prev = date(prev_raw.year, prev_raw.month, calendar.monthrange(prev_raw.year, prev_raw.month)[1])
        months.append(prev)
    return months  # months[0] = newest (selected), months[-1] = oldest


def build_dq_flags(row, slots):
    """Return a list of implausible/flagged entries for one child row.

    Checks, per measurement slot:
      - WHO age-based plausible weight/height range.
      - Reduction (decrease) vs. the next-older slot.
    """
    flags = []
    gender_key = "M" if row.get("gender") == "Male" else "F"
    base_age = row.get("age")

    for i, slot in enumerate(slots):
        # Age in completed months at this slot's month (m1 = base_age, m2 = base_age - 1, ...).
        slot_age = (base_age - i) if base_age is not None else None
        raw_measurement_date = row.get(f"measurement_date_{slot}")
        measurement_date = frappe.utils.formatdate(raw_measurement_date) if raw_measurement_date else "-"

        weight_val = row.get(f"weight_{slot}")
        weight_val = float(weight_val) if weight_val not in (None, "") else weight_val
        height_val = row.get(f"height_{slot}")
        height_val = float(height_val) if height_val not in (None, "") else height_val

        if slot_age is not None and slot_age in WHO_WEIGHT_RANGE[gender_key] and weight_val not in (None, ""):
            lo, hi = WHO_WEIGHT_RANGE[gender_key][slot_age]
            if weight_val < lo or weight_val > hi:
                flags.append({
                    "child_name": row.get("child_name") or "-",
                    "child_age": slot_age,
                    "kind": "weight",
                    "age": slot_age,
                    "range": [lo, hi],
                    "unit": "kg",
                    "measurement_date": measurement_date,
                    "weight": weight_val,
                })

        if slot_age is not None and slot_age in WHO_HEIGHT_RANGE[gender_key] and height_val not in (None, ""):
            lo, hi = WHO_HEIGHT_RANGE[gender_key][slot_age]
            if height_val < lo or height_val > hi:
                flags.append({
                    "child_name": row.get("child_name") or "-",
                    "child_age": slot_age,
                    "kind": "height",
                    "age": slot_age,
                    "range": [lo, hi],
                    "unit": "cm",
                    "measurement_date": measurement_date,
                    "weight": weight_val,
                })

    # Reduction checks: newer slot value < older slot value.
    who_range = {"weight": WHO_WEIGHT_RANGE, "height": WHO_HEIGHT_RANGE}
    for kind in ("weight", "height"):
        for k in range(1, len(slots)):
            newer_slot, older_slot = slots[k - 1], slots[k]
            newer_val = row.get(f"{kind}_{newer_slot}")
            older_val = row.get(f"{kind}_{older_slot}")
            if newer_val is None or older_val is None:
                continue
            newer_val, older_val = float(newer_val), float(older_val)
            if newer_val < older_val:
                unit = "kg" if kind == "weight" else "cm"
                raw_newer_date = row.get(f"measurement_date_{newer_slot}")
                newer_weight = row.get(f"weight_{newer_slot}")
                newer_slot_age = (base_age - (k - 1)) if base_age is not None else None
                age_range = who_range[kind][gender_key].get(newer_slot_age) if newer_slot_age is not None else None
                flags.append({
                    "child_name": row.get("child_name") or "-",
                    "child_age": newer_slot_age,
                    "kind": kind,
                    "age": newer_slot_age,
                    "range": list(age_range) if age_range else None,
                    "unit": unit,
                    "measurement_date": frappe.utils.formatdate(raw_newer_date) if raw_newer_date else "-",
                    "weight": float(newer_weight) if newer_weight is not None else None,
                })

    return flags


def execute(filters=None):
    if not filters:
        filters = {}

    current_date = date.today()
    month = int(filters.get("month", current_date.month))
    year = int(filters.get("year", current_date.year))

    # Number of months of Height/Weight data to show. Defaults to 3.
    try:
        n_months = int(filters.get("duration_h_w") or 3)
    except (ValueError, TypeError):
        n_months = 3
    if n_months not in (3, 6, 9, 12):
        n_months = 3

    # month_dates ordered NEWEST -> OLDEST. month_dates[0] = selected month.
    month_dates = get_month_dates(year, month, n_months)
    # Slot names m1..mN map to month_dates[0..N-1] (newest -> oldest).
    slots = [f"m{i + 1}" for i in range(n_months)]

    columns = get_columns(filters, month_dates, slots)
    data = get_data(filters, month_dates, slots)

    # --- Detect implausible / flagged entries (WHO range + reduction) before ---
    # --- measurement dates/reduction fields below get reformatted into HTML. ---
    for row in data:
        row["_dq_flags_json"] = json.dumps(build_dq_flags(row, slots))

    for row in data:
        for slot in slots:
            measurement_date = row.get(f"measurement_date_{slot}")
            row[f"measurement_date_{slot}"] = frappe.utils.formatdate(measurement_date) if measurement_date else "-"
            if not row.get(f"measurement_reason_{slot}"):
                row[f"measurement_reason_{slot}"] = "No reason recorded"

    # =====================================================================
    # --- Filter by Data Availability (Strict Zero/Null Handling) ---
    # =====================================================================
    data_availability = filters.get("data_availability", "1")
    wh_filter = filters.get("weight_height", "")

    if data_availability in ["2", "3"]:
        filtered_data = []

        # Determine which fields to check based on the Weight/Height filter
        if wh_filter == "1":
            check_fields = [f"height_{s}" for s in slots]
        elif wh_filter == "2":
            check_fields = [f"weight_{s}" for s in slots]
        else:
            check_fields = [f"height_{s}" for s in slots] + [f"weight_{s}" for s in slots]

        for row in data:
            has_data = False
            for field in check_fields:
                val = row.get(field)
                # Safely parse the value and ensure it is strictly greater than 0
                if val is not None and val != "":
                    try:
                        if float(val) > 0:
                            has_data = True
                            break  # Exit loop early to save processing time
                    except (ValueError, TypeError):
                        pass

            # Option 2: Available Data (Has at least one valid >0 value in visible columns)
            if data_availability == "2" and has_data:
                filtered_data.append(row)

            # Option 3: No Data (All visible columns are empty, None, or 0)
            elif data_availability == "3" and not has_data:
                filtered_data.append(row)

        # Replace the original data list with our strictly filtered list
        data = filtered_data
    # =====================================================================

    # --- Format the Reduction columns with arrows ---
    # Reduction "red{k}" sits between the newer month (slot k) and the older
    # month (slot k+1). Value = newer - older (so positive = the child grew).
    for row in data:
        for kind in ("height", "weight"):
            for k in range(1, n_months):
                field = f"{kind}_red{k}"
                if row.get(field) is None:
                    continue

                val = row[field]
                newer_date = month_dates[k - 1]
                older_date = month_dates[k]

                # Whether this pair falls inside the "valid" highlight window.
                if kind == "height":
                    # Both months within the selected filter year.
                    is_within_filter = (older_date.year == year and newer_date.year == year)
                else:
                    # Both months within (or after) April of the filter year.
                    is_within_filter = (older_date >= date(year, 4, 1))

                if val > 0:
                    # value INCREASED over time (grew) -> green up arrow
                    row[field] = f"{abs(val)} <strong style='color:green; font-weight:900; font-size:20px; line-height:1; -webkit-text-stroke:0.4px green; font-family: Arial, sans-serif;'>&#8593;</strong>"
                elif val < 0:
                    # value DECREASED over time -> down arrow (red if within filter window)
                    if is_within_filter:
                        row[field] = f"{abs(val)} <strong style='color:red; font-weight:900; font-size:20px; line-height:1; -webkit-text-stroke:0.4px red; font-family: Arial, sans-serif;'>&#8595;</strong>"
                    else:
                        row[field] = f"{abs(val)} <strong style='color:black; font-weight:900; font-size:20px; line-height:1; -webkit-text-stroke:0.4px black; font-family: Arial, sans-serif;'>&#8595;</strong>"
                else:
                    # No change
                    row[field] = f"{abs(val)} ➖"

    child_count = len(data)
    yes_count = sum(1 for row in data if row.get("measurement_taken_yn") == "Y")
    no_count = sum(1 for row in data if row.get("measurement_taken_yn") == "N")

    total_row = {"child_name": f"Total Children: {child_count}", "measurement_taken_yn": f"Yes: {yes_count} / No: {no_count}"}
    data.append(total_row)

    return columns, data


def get_columns(filters, month_dates, slots):
    """Generate dynamic columns for the N-month comparison (newest -> oldest)."""

    labels = [d.strftime("%b-%y") for d in month_dates]  # newest -> oldest
    wh_filter = filters.get("weight_height", "")

    # Base Columns
    columns = [
        {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 140},
        {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": _("Gram Panchayat"), "fieldname": "gram_panchayat", "fieldtype": "Data", "width": 140},
        {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 150},
        {"label": _("Creche"), "fieldname": "creche", "fieldtype": "Data", "width": 150},
        {"label": _("Creche ID"), "fieldname": "creche_id", "fieldtype": "Data", "width": 120},
        {"label": _("Child Name"), "fieldname": "child_name", "fieldtype": "Data", "width": 140},
        {"label": _("Gender"), "fieldname": "gender", "fieldtype": "Data", "width": 80},
        {"label": _("Age (Months)"), "fieldname": "age", "fieldtype": "Int", "width": 130},
        {"label": _("Age in Days"), "fieldname": "age_in_days", "fieldtype": "Int", "width": 140},
        {"label": _("Date of Enrollment"), "fieldname": "date_of_enrollment", "fieldtype": "Data", "width": 160},
        {"label": _("Date of Exit"), "fieldname": "date_of_exit", "fieldtype": "Data", "width": 150},
        {"label": _("Measurement Taken"), "fieldname": "measurement_taken_yn", "fieldtype": "Data", "width": 185},
    ]

    # Hidden per-slot measurement date / reason columns (used by the popup).
    for slot in slots:
        columns.append({"label": _(f"Measurement Date {slot.upper()}"), "fieldname": f"measurement_date_{slot}", "fieldtype": "Data", "width": 0, "hidden": 1})
    for slot in slots:
        columns.append({"label": _(f"Measurement Reason {slot.upper()}"), "fieldname": f"measurement_reason_{slot}", "fieldtype": "Data", "width": 0, "hidden": 1})

    # Hidden column carrying the JSON list of implausible/flagged entries for this child (used by the Date Range popup).
    columns.append({"label": _("DQ Flags"), "fieldname": "_dq_flags_json", "fieldtype": "Data", "width": 0, "hidden": 1})

    def value_columns(kind, prefix_label):
        """Build alternating value/reduction columns newest -> oldest for one metric."""
        cols = []
        for i, slot in enumerate(slots):
            cols.append({
                "label": f"{prefix_label} ({labels[i]})",
                "fieldname": f"{kind}_{slot}",
                "fieldtype": "Data",
                "width": 220,
            })
            # Reduction column after each month except the last (oldest) one.
            if i < len(slots) - 1:
                red_lbl = f"Reduction ({labels[i]} → {labels[i + 1]})"
                cols.append({
                    "label": f"{prefix_label} {red_lbl}",
                    "fieldname": f"{kind}_red{i + 1}",
                    "fieldtype": "Data",
                    "width": 260,
                })
        return cols

    if wh_filter == "1":
        columns.extend(value_columns("height", "Height"))
    elif wh_filter == "2":
        columns.extend(value_columns("weight", "Weight"))
    else:
        columns.extend(value_columns("height", "Height"))
        columns.extend(value_columns("weight", "Weight"))

    return columns


def get_data(filters, month_dates, slots):
    """Fetch data handling the N-month aggregation for height and weight."""

    n_months = len(slots)
    selected_date = month_dates[0]   # newest / selected month
    oldest_date = month_dates[-1]    # oldest month in the window

    conditions = [
        "cgm.measurement_date BETWEEN %(sel_start)s AND %(sel_end)s",
        "cee.date_of_enrollment <= %(sel_end)s",
        "(cee.date_of_exit IS NULL OR cee.date_of_exit > %(sel_start)s)",
    ]

    params = {
        "target_date_str": selected_date.strftime("%Y-%m-%d"),
        # Selected-month bounds drive the base row set (the m1 / selected month).
        "sel_start": selected_date.replace(day=1).strftime("%Y-%m-%d"),
        "sel_end": selected_date.strftime("%Y-%m-%d"),
        # Full pivot window: oldest month start .. selected month end.
        "win_start": oldest_date.replace(day=1).strftime("%Y-%m-%d"),
        "win_end": selected_date.strftime("%Y-%m-%d"),
    }
    # Per-month boundaries used by the pivot to populate each slot.
    for i, slot in enumerate(slots):
        d = month_dates[i]
        params[f"{slot}_start"] = d.replace(day=1).strftime("%Y-%m-%d")
        params[f"{slot}_end"] = d.strftime("%Y-%m-%d")

    # 1. User Geography Mapping Logic
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    partner_id = filters.get("partner") or current_user_partner

    state_query = """
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping` ugm
        WHERE ugm.parent = %s
    """
    current_user_state = frappe.db.sql(state_query, (frappe.session.user,), as_dict=True)

    state_ids = [str(s["state_id"]) for s in current_user_state if s.get("state_id")]
    district_ids = [str(s["district_id"]) for s in current_user_state if s.get("district_id")]
    block_ids = [str(s["block_id"]) for s in current_user_state if s.get("block_id")]
    gp_ids = [str(s["gp_id"]) for s in current_user_state if s.get("gp_id")]

    # Core Geographics & Partner
    if partner_id:
        conditions.append("cee.partner_id = %(partner)s")
        params["partner"] = partner_id

    if filters.get("state"):
        conditions.append("cee.state_id = %(state)s")
        params["state"] = filters.get("state")
    elif state_ids:
        conditions.append(f"cee.state_id IN %(state_ids)s")
        params["state_ids"] = tuple(state_ids) if state_ids else ('',)

    if filters.get("district"):
        conditions.append("cee.district_id = %(district)s")
        params["district"] = filters.get("district")
    elif district_ids:
        conditions.append(f"cee.district_id IN %(district_ids)s")
        params["district_ids"] = tuple(district_ids) if district_ids else ('',)

    if filters.get("block"):
        conditions.append("cee.block_id = %(block)s")
        params["block"] = filters.get("block")
    elif block_ids:
        conditions.append(f"cee.block_id IN %(block_ids)s")
        params["block_ids"] = tuple(block_ids) if block_ids else ('',)

    if filters.get("gp"):
        conditions.append("cee.gp_id = %(gp)s")
        params["gp"] = filters.get("gp")
    elif gp_ids:
        conditions.append(f"cee.gp_id IN %(gp_ids)s")
        params["gp_ids"] = tuple(gp_ids) if gp_ids else ('',)

    # Granular Filters
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
        phases_list = filters.get("phases")
        if isinstance(phases_list, str):
            phases = [p.strip() for p in phases_list.split(",") if p.strip()]
        else:
            phases = [str(p) for p in phases_list]

        if phases:
            conditions.append("c.phase IN %(phases)s")
            params["phases"] = tuple(phases)

    # 2. Duration / Child Age Filter
    if filters.get("duration"):
        conditions.append("TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date_str)s) = %(duration)s")
        params["duration"] = int(filters.get("duration"))

    # 3. Creche Age Filter Logic
    creche_age = filters.get("creche_age", "")
    if creche_age:
        params["creche_age"] = creche_age
        conditions.append("""
            CASE
                WHEN c.creche_opening_date IS NULL THEN ''
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(target_date_str)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(target_date_str)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(target_date_str)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(target_date_str)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                WHEN TIMESTAMPDIFF(MONTH, c.creche_opening_date, %(target_date_str)s) >= 24 THEN '24+ Month'
                ELSE ''
            END = %(creche_age)s
        """)

    # 4. Creche Opening Date Rules
    cstart_date, cend_date = None, None
    range_type = filters.get("cr_opening_range_type")

    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()

        if range_type == "between" and date_range and len(date_range) == 2:
            cstart_date, cend_date = date_range
        elif range_type == "before" and single_date:
            cstart_date = date(2017, 1, 1)
            cend_date = single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            cstart_date = single_date + timedelta(days=1)
            cend_date = date.today()
        elif range_type == "equal" and single_date:
            cstart_date = cend_date = single_date

    if cstart_date or cend_date:
        conditions.append("c.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
        params["cstart_date"] = cstart_date
        params["cend_date"] = cend_date

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # ------------------------------------------------------------------
    # Build the dynamic pivot SELECT lines (one set of expressions per slot).
    # ------------------------------------------------------------------
    reason_case = """
                    CASE
                        WHEN ad.measurement_reason = 1 THEN 'Child not in creche'
                        WHEN ad.measurement_reason = 2 THEN 'Child not in village'
                        WHEN ad.measurement_reason = 3 THEN 'Child is sick'
                        WHEN ad.measurement_reason = 4 THEN 'Any other'
                        ELSE ''
                    END"""

    pivot_lines = []
    for slot in slots:
        rng = f"cgm.measurement_date BETWEEN %({slot}_start)s AND %({slot}_end)s"
        pivot_lines.append(f"MAX(CASE WHEN ad.do_you_have_height_weight = 1 AND {rng} THEN ad.height END) AS height_{slot}")
        pivot_lines.append(f"MAX(CASE WHEN ad.do_you_have_height_weight = 1 AND {rng} THEN ad.weight END) AS weight_{slot}")
        pivot_lines.append(f"MAX(CASE WHEN {rng} THEN ad.measurement_taken_date END) AS measurement_date_{slot}")
        pivot_lines.append(f"MAX(CASE WHEN {rng} THEN {reason_case} END) AS measurement_reason_{slot}")
    pivot_select = ",\n                ".join(pivot_lines)

    # Outer SELECT: per-slot value columns + reduction columns (newer - older).
    outer_lines = []
    for slot in slots:
        outer_lines.append(f"ROUND(pv.height_{slot}, 2) AS height_{slot}")
    for k in range(1, n_months):
        newer, older = slots[k - 1], slots[k]
        outer_lines.append(f"ROUND(pv.height_{newer} - pv.height_{older}, 2) AS height_red{k}")
    for slot in slots:
        outer_lines.append(f"ROUND(pv.weight_{slot}, 2) AS weight_{slot}")
    for k in range(1, n_months):
        newer, older = slots[k - 1], slots[k]
        outer_lines.append(f"ROUND(pv.weight_{newer} - pv.weight_{older}, 2) AS weight_red{k}")
    for slot in slots:
        outer_lines.append(f"pv.measurement_date_{slot} AS measurement_date_{slot}")
    for slot in slots:
        outer_lines.append(f"pv.measurement_reason_{slot} AS measurement_reason_{slot}")
    outer_select = ",\n            ".join(outer_lines)

    query = f"""
        WITH ad_pivot AS (
            SELECT
                ad.childenrollguid AS childenrollguid,
                {pivot_select}
            FROM `tabAnthropromatic Data` as ad
            INNER JOIN `tabChild Growth Monitoring` as cgm ON cgm.name = ad.parent
            WHERE cgm.measurement_date BETWEEN %(win_start)s AND %(win_end)s
            GROUP BY ad.childenrollguid
        )

        SELECT
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            gp.gp_name AS gram_panchayat,
            u.full_name AS supervisor,
            c.creche_name AS creche,
            c.creche_id AS creche_id,
            cee.child_name AS child_name,
            CASE WHEN cee.gender_id = 1 THEN 'Male' ELSE 'Female' END AS gender,
            TIMESTAMPDIFF(MONTH, cee.child_dob, %(target_date_str)s) AS age,
            DATEDIFF(%(target_date_str)s, cee.child_dob) AS age_in_days,
            DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS date_of_enrollment,
            DATE_FORMAT(cee.date_of_exit, '%%d-%%m-%%Y') AS date_of_exit,

            -- Measurement Taken for the SELECTED month (same logic as malnutrition report)
            IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS measurement_taken_yn,

            {outer_select}

        FROM `tabAnthropromatic Data` as ad
        INNER JOIN `tabChild Growth Monitoring` as cgm on cgm.name = ad.parent
        INNER JOIN `tabChild Enrollment and Exit` as cee on cee.childenrollguid = ad.childenrollguid
        INNER JOIN `tabCreche` as c on c.name = cee.creche_id
        LEFT JOIN ad_pivot as pv on pv.childenrollguid = ad.childenrollguid
        LEFT JOIN `tabUser` as u on u.name = c.supervisor_id
        LEFT JOIN `tabPartner` as p on p.name = cee.partner_id
        LEFT JOIN `tabState` as s on s.name = cee.state_id
        LEFT JOIN `tabDistrict` as d on d.name = cee.district_id
        LEFT JOIN `tabBlock` as b on b.name = cee.block_id
        LEFT JOIN `tabGram Panchayat` as gp on gp.name = cee.gp_id

        WHERE
            {where_clause}

        GROUP BY ad.name, cgm.name, cee.name, c.name, u.name, p.name, s.name, d.name, b.name, gp.name
        ORDER BY cee.partner_id, cee.state_id, cee.district_id, cee.block_id, cee.gp_id,
            c.supervisor_id, c.name, cee.child_name
    """

    return frappe.db.sql(query, params, as_dict=True)
