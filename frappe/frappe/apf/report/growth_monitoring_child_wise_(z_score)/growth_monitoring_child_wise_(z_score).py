import frappe
import math
from frappe.utils import nowdate
import calendar
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict


def calculate_z_score(value, M, L, S):
    if L == 0:
        raise ValueError("L should not be zero to avoid division errors.")

    ratio = float(value / M)
    ratio_to_L = float(math.pow(ratio, L))
    numerator = float(ratio_to_L - 1)
    denominator = float(S * L)
    z_score = float(numerator / denominator)

    if z_score <= -3:
        sd3neg = float(M * math.pow(1 + L * S * (-3), 1 / L))
        sd2neg = float(M * math.pow(1 + L * S * (-2), 1 / L))
        sd23neg = float(sd2neg - sd3neg)
        z_score = float(-3 + (value - sd3neg) / sd23neg)

    elif z_score >= 3:
        sd3pos = float(M * math.pow(1 + L * S * (3), 1 / L))
        sd2pos = float(M * math.pow(1 + L * S * (2), 1 / L))
        sd23pos = float(sd3pos - sd2pos)
        z_score = float(3 + (value - sd3pos) / sd23pos)

    return round(z_score, 2)


def weight_for_age_boys_table():
    fields_to_fetch = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    records = frappe.get_all("Weight for age Boys", fields=fields_to_fetch)
    return {row["age_in_days"]: row for row in records}


def weight_for_age_girls_table():
    fields_to_fetch = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    records = frappe.get_all("Weight for age Girls", fields=fields_to_fetch)
    return {row["age_in_days"]: row for row in records}


def weight_to_height_boys():
    fields = [
        "age_type", "length", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    try:
        records = frappe.get_all("Weight to Height Boys", fields=fields, limit=0)
        data = defaultdict(list)
        for row in records:
            data[row["length"]].append(row)
        return dict(data)
    except Exception as e:
        frappe.log_error(f"Error loading boys data: {str(e)}")
        return {}


def weight_to_height_girls():
    fields = [
        "age_type", "length", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    try:
        records = frappe.get_all("Weight to Height Girls", fields=fields, limit=0)
        data = defaultdict(list)
        for row in records:
            data[row["length"]].append(row)
        return dict(data)
    except Exception as e:
        frappe.log_error(f"Error loading girls data: {str(e)}")
        return {}


def height_for_age_boys():
    fields_to_fetch = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    records = frappe.get_all("Height for age Boys", fields=fields_to_fetch)
    return {row["age_in_days"]: row for row in records}


def height_for_age_girls():
    fields_to_fetch = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    records = frappe.get_all("Height for age Girls", fields=fields_to_fetch)
    return {row["age_in_days"]: row for row in records}


def get_columns():
    return [
        {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
        {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
        {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
        {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
        {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
        {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
        {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
        {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 150},
        # {"label": "DOB at Measurement", "fieldname": "mbob", "fieldtype": "Data", "width": 180},
        {"label": "Measurement Date", "fieldname": "measurements_taken_date", "fieldtype": "Data", "width": 200},
        {"label": "Age (in Days)", "fieldname": "age_months", "fieldtype": "Data", "width": 200},
        {"label": "Measurement Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 180},
        {"label": "Measurement Equipment", "fieldname": "measurement_equipment_type", "fieldtype": "Data", "width": 180},
        {"label": "Weight (kg)", "fieldname": "weight", "fieldtype": "Data", "width": 130},
        {"label": "Height (cm)", "fieldname": "height", "fieldtype": "Data", "width": 130},
        {"label": "Weight for Age", "fieldname": "weight_for_age_status", "fieldtype": "Data", "width": 150},
        {"label": "Weight for Height", "fieldname": "weight_for_height_status", "fieldtype": "Data", "width": 150},
        {"label": "Height for Age", "fieldname": "height_for_age_status", "fieldtype": "Data", "width": 150},
        {"label": "Weight for Age Category", "fieldname": "weight_for_age_status_cat", "fieldtype": "Data", "width": 200},
        {"label": "Weight for Height Category", "fieldname": "weight_for_height_status_cat", "fieldtype": "Data", "width": 200},
        {"label": "Height for Age Category", "fieldname": "height_for_age_status_cat", "fieldtype": "Data", "width": 200}
    ]


@frappe.whitelist()
def get_summary_data(filters=None):
    month = int(filters.get("month") if filters else nowdate().split('-')[1])
    year = int(filters.get("year") if filters else nowdate().split('-')[0])
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    # Get current user's partner and geography mapping
    current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
    state_query = """ 
        SELECT state_id, district_id, block_id, gp_id
        FROM `tabUser Geography Mapping`
        WHERE parent = %s
        ORDER BY state_id, district_id, block_id, gp_id
    """
    current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
    # Initialize filter parameters
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "year": year,
        "month": month,
        "partner": filters.get("partner") if filters else current_user_partner,
        "state": filters.get("state") if filters else None,
        "district": filters.get("district") if filters else None,
        "block": filters.get("block") if filters else None,
        "gp": filters.get("gp") if filters else None,
        "creche": filters.get("creche") if filters else None,
        "supervisor_id": filters.get("supervisor_id") if filters else None,
        "creche_status_id": filters.get("creche_status_id") if filters else None,
        "mea_taken": filters.get("mea_taken") if filters else None,
        "phases": None,
        "cstart_date": None,
        "cend_date": None,
        "state_ids": None,
        "district_ids": None,
        "block_ids": None,
        "gp_ids": None,
        "creche_age": filters.get("creche_age") if filters else None
    }
    
    # Handle phases filter
    if filters and filters.get("phases"):
        phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
        params["phases"] = phases_cleaned
    
    # Handle creche opening date range filter
    range_type = filters.get("cr_opening_range_type") if filters else None
    if range_type:
        single_date = filters.get("single_date")
        date_range = filters.get("c_opening_range")

        if single_date and isinstance(single_date, str):
            single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
        if range_type == "between" and date_range and len(date_range) == 2:
            params["cstart_date"], params["cend_date"] = date_range
        elif range_type == "before" and single_date:
            params["cstart_date"], params["cend_date"] = date(2017, 1, 1), single_date - timedelta(days=1)
        elif range_type == "after" and single_date:
            params["cstart_date"], params["cend_date"] = single_date + timedelta(days=1), date.today()
        elif range_type == "equal" and single_date:
            params["cstart_date"] = params["cend_date"] = single_date
    
    # Handle default geography if no explicit filters
    if not any([params["state"], params["district"], params["block"], params["gp"]]):
        if current_user_state:
            state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
            district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
            block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
            gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
            
            if state_ids:
                params["state_ids"] = state_ids
            if district_ids:
                params["district_ids"] = district_ids
            if block_ids:
                params["block_ids"] = block_ids
            if gp_ids:
                params["gp_ids"] = gp_ids
    
    # Calculate previous months for any potential future use
    if month == 1:
        params.update({
            "lmonth": 12,
            "plmonth": 11,
            "lyear": year - 1,
            "pyear": year - 1
        })
    elif month == 2:
        params.update({
            "lmonth": 1,
            "plmonth": 12,
            "lyear": year,
            "pyear": year - 1
        })
    else:
        params.update({
            "lmonth": month - 1,
            "plmonth": month - 2,
            "lyear": year,
            "pyear": year
        })

    sql_query = """
        SELECT p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            g.gp_name AS gp,
            cr.creche_name AS 'creche_name',
            usr.full_name AS 'supervisor',
            cee.child_id AS 'child_id',
            cr.creche_id AS 'creche_id',
            cee.child_name AS 'child_name',
            cee.age_at_enrollment_in_months AS 'age',
            DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS 'child_dob',
            CASE WHEN ad.do_you_have_height_weight = 1 THEN
            DATE_FORMAT(DATE_SUB(ad.measurement_taken_date, INTERVAL ad.age_months DAY), '%%d-%%m-%%Y') ELSE '-' END AS mbob,
            (CASE 
                WHEN cee.gender_id = '1' THEN 'M'
                WHEN cee.gender_id = '2' THEN 'F'
                ELSE 'Other'
            END) AS gender,
            ad.height AS 'height',
            ad.weight AS 'weight',
            IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS 'measurements_taken',
            IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS 'measurements_taken_date',
            CASE WHEN ad.do_you_have_height_weight = 1 THEN ad.age_months ELSE '-' END AS age_months,
            cee.gender_id as gender_id,
            CASE 
                WHEN ad.measurement_equipment = 1 THEN 'Stadiometer'
                WHEN ad.measurement_equipment = 2 THEN 'Infantometer'
                ELSE '-'
            END AS measurement_equipment_type,
            cr.creche_opening_date
        FROM  
            `tabAnthropromatic Data` AS ad 
        INNER JOIN 
            `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
        INNER JOIN 
            `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid 
        INNER JOIN 
            `tabCreche` AS cr ON cgm.creche_id = cr.name 
        INNER JOIN 
            `tabUser` AS usr ON cr.supervisor_id = usr.name 
        INNER JOIN 
            `tabPartner` AS p ON p.name = cr.partner_id
        INNER JOIN 
            `tabState` AS s ON s.name = cr.state_id
        INNER JOIN 
            `tabDistrict` AS d ON d.name = cr.district_id
        INNER JOIN 
            `tabBlock` AS b ON b.name = cr.block_id
        INNER JOIN 
            `tabGram Panchayat` AS g ON g.name = cr.gp_id
        WHERE 
            YEAR(cgm.measurement_date) = %(year)s
            AND MONTH(cgm.measurement_date) = %(month)s
            AND (%(partner)s IS NULL OR cr.partner_id = %(partner)s) 
            AND (
                (%(state)s IS NULL AND %(state_ids)s IS NULL) 
                OR cr.state_id = %(state)s 
                OR (%(state)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
            )
            AND (
                (%(district)s IS NULL AND %(district_ids)s IS NULL) 
                OR cr.district_id = %(district)s 
                OR (%(district)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cr.district_id, %(district_ids)s))
            )
            AND (
                (%(block)s IS NULL AND %(block_ids)s IS NULL) 
                OR cr.block_id = %(block)s 
                OR (%(block)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cr.block_id, %(block_ids)s))
            )
            AND (
                (%(gp)s IS NULL AND %(gp_ids)s IS NULL) 
                OR cr.gp_id = %(gp)s 
                OR (%(gp)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
            )
            AND (%(creche)s IS NULL OR cr.name = %(creche)s)
            AND (%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)
            AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
            AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
            AND (%(mea_taken)s IS NULL OR ad.do_you_have_height_weight = %(mea_taken)s)
            AND cee.date_of_enrollment <= %(end_date)s
            AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
            AND (
                (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
                OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
            )
            AND (
                %(creche_age)s IS NULL OR (
                    CASE
                        WHEN cr.creche_opening_date IS NULL THEN ''
                        WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 0 AND 6 THEN '0-6 Month'
                        WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 7 AND 12 THEN '7-12 Month'
                        WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 13 AND 18 THEN '13-18 Month'
                        WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) BETWEEN 19 AND 24 THEN '19-24 Month'
                        WHEN TIMESTAMPDIFF(MONTH, cr.creche_opening_date, %(end_date)s) >= 24 THEN '24+ Month'
                        ELSE ''
                    END = %(creche_age)s
                )
            )
        ORDER BY
            cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id, cr.supervisor_id, cr.name, cee.child_name

    """
    data = frappe.db.sql(sql_query, params, as_dict=True)

    # Calculate summary counts
    counts = {
        "child_name": len(data),
        "measurements_taken": sum(1 for row in data if row.get("measurements_taken") == "Y")
    }

    # Add summary row
    summary_row = {
        "partner": "<b style='color:black;'>Total</b>",
        "child_name": counts['child_name'],
        "measurements_taken": counts['measurements_taken']
    }
    data.append(summary_row)

    return data


def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)

    # Load all growth reference data
    weight_for_age_boys_data = weight_for_age_boys_table()
    weight_for_age_girls_data = weight_for_age_girls_table()
    weight_to_height_boys_data = weight_to_height_boys()
    weight_to_height_girls_data = weight_to_height_girls()
    height_for_age_boys_data = height_for_age_boys()
    height_for_age_girls_data = height_for_age_girls()
    
    for row in data:
        if not isinstance(row, dict):  # Skip summary row
            continue
            
        age_months = row.get("age_months")
        gender_id = row.get("gender_id")
        weight = row.get("weight")
        height = row.get("height")
        measurement_equipment = row.get("measurement_equipment_type")
        measurement_date = row.get("measurements_taken_date")
        
        # Initialize all status fields
        row["weight_for_age_status"] = None
        row["weight_for_height_status"] = None
        row["height_for_age_status"] = None
        row["weight_for_age_status_cat"] = None
        row["weight_for_height_status_cat"] = None
        row["height_for_age_status_cat"] = None
        
        # Calculate weight-for-age status
        if age_months is not None and weight is not None and weight > 0 and gender_id in ('1', '2'):
            try:
                age_in_days = int(age_months)
                weight = float(weight)
                
                growth_data = weight_for_age_boys_data.get(age_in_days) if gender_id == '1' else weight_for_age_girls_data.get(age_in_days)
                    
                if growth_data:
                    try:
                        L = float(growth_data.get("l", 0))
                        M = float(growth_data.get("m", 0))
                        S = float(growth_data.get("s", 0))
                        z_score = calculate_z_score(weight, M, L, S)                        
                        sd3neg = float(growth_data.get("sd3neg", 0))
                        sd2neg = float(growth_data.get("sd2neg", 0))
                        sd2 = float(growth_data.get("sd2", 0))
                        
                        if weight < sd3neg:
                            color = "#FFCCCC"  # Light red
                            text_color = "#CC0000"  # Dark red
                            category = "Severe"
                        elif weight >= sd3neg and weight < sd2neg:
                            color = "#FFFFCC"  # Light yellow
                            text_color = "#999900"  # Dark yellow
                            category = "Moderate"
                        elif weight >= sd2neg and weight <= sd2:
                            color = "#CCFFCC"  # Light green
                            text_color = "#006600"  # Dark green
                            category = "Normal"
                        else:
                            color = "#E6E6E6"  # Light gray for above normal
                            text_color = "#666666"  # Dark gray
                            category = "Overweight/Obese"

                        row["weight_for_age_status"] = format_cell(z_score, color, text_color)
                        row["weight_for_age_status_cat"] = format_cell(category, color, text_color)
                            
                    except (ValueError, TypeError):
                        pass
            except (ValueError, TypeError):
                pass
                
        # Calculate weight-for-height status
        if height is not None and weight is not None and weight > 0 and height > 0 and gender_id in ('1', '2'):
            try:
                height_rounded = round(height,1)
                weight = float(weight)
                age_in_days = int(age_months)
                
                age_type_0_boys = {
                    height: next(
                        (record for record in records if str(record.get('age_type')).strip() in ['0', '0.0']),
                        None
                    )
                    for height, records in weight_to_height_boys_data.items()
                }

                age_type_24_boys = {
                    height: next(
                        (record for record in records if str(record.get('age_type')).strip() in ['24', '24.0']),
                        None
                    )
                    for height, records in weight_to_height_boys_data.items()
                }

                age_type_0_girls = {
                    height: next(
                        (record for record in records if str(record.get('age_type')).strip() in ['0', '0.0']),
                        None
                    )
                    for height, records in weight_to_height_girls_data.items()
                }

                age_type_24_girls = {
                    height: next(
                        (record for record in records if str(record.get('age_type')).strip() in ['24', '24.0']),
                        None
                    )
                    for height, records in weight_to_height_girls_data.items()
                }

                wfh_growth_data = None
                if age_in_days < 730:
                    if measurement_equipment == 'Stadiometer':
                        height_rounded = round(height_rounded + 0.7,1)

                if age_in_days > 730:
                    if measurement_equipment == 'Infantometer':
                        height_rounded = round(height_rounded - 0.7,1)

                if age_in_days <= 730:
                    if gender_id == '1':
                        wfh_growth_data = age_type_0_boys.get(height_rounded)
                    else:
                        wfh_growth_data = age_type_0_girls.get(height_rounded)

                if age_in_days > 730:
                    if gender_id == '1':
                        wfh_growth_data = age_type_24_boys.get(height_rounded)
                    else:
                        wfh_growth_data = age_type_24_girls.get(height_rounded)

                if wfh_growth_data:
                    try:
                        L = float(wfh_growth_data.get("l", 0))
                        M = float(wfh_growth_data.get("m", 0))
                        S = float(wfh_growth_data.get("s", 0))
                        z_score = calculate_z_score(weight, M, L, S)
                        
                        sd3neg = float(wfh_growth_data.get("sd3neg", 0))
                        sd2neg = float(wfh_growth_data.get("sd2neg", 0))
                        sd2 = float(wfh_growth_data.get("sd2", 0))

                        if weight < sd3neg:
                            color = "#FFCCCC"  # Light red
                            text_color = "#CC0000"  # Dark red
                            category = "Severe"
                        elif weight >= sd3neg and weight < sd2neg:
                            color = "#FFFFCC"  # Light yellow
                            text_color = "#999900"  # Dark yellow
                            category = "Moderate"
                        elif weight >= sd2neg and weight <= sd2:
                            color = "#CCFFCC"  # Light green
                            text_color = "#006600"  # Dark green
                            category = "Normal"
                        else:
                            color = "#E6E6E6"  # Light gray for above normal
                            text_color = "#666666"  # Dark gray
                            category = "Overweight/Obese"
                        
                        row["weight_for_height_status"] = format_cell(z_score, color, text_color)
                        row["weight_for_height_status_cat"] = format_cell(category, color, text_color)
                    except (ValueError, TypeError):
                        pass
            except (ValueError, TypeError):
                pass

        # Calculate height-for-age status
        if age_months is not None and height is not None and height > 0 and gender_id in ('1', '2'):
            try:
                age_in_days = int(age_months)
                height = float(height)
                
                if measurement_equipment and measurement_date:
                    measurement_date = datetime.strptime(measurement_date, "%d-%m-%Y").date()
                    two_years_ago = measurement_date - relativedelta(months=24)
                    dob = measurement_date - timedelta(days=age_in_days)
                    if dob > two_years_ago:
                        if measurement_equipment == 'Stadiometer':
                            height = round(height + 0.7, 1)

                    else:
                        if measurement_equipment == 'Infantometer':
                            height = round(height - 0.7, 1)

                
                # Get growth data
                growth_data = height_for_age_boys_data.get(age_in_days) if gender_id == '1' else height_for_age_girls_data.get(age_in_days)
                
                if growth_data:
                    try:
                        L = float(growth_data.get("l", 0))
                        M = float(growth_data.get("m", 0))
                        S = float(growth_data.get("s", 0))
                        z_score = calculate_z_score(height, M, L, S)
                        
                        sd3neg = float(growth_data.get("sd3neg", 0))
                        sd2neg = float(growth_data.get("sd2neg", 0))
                        sd2 = float(growth_data.get("sd2", 0))
                        
                        if height < sd3neg:
                            color = "#FFCCCC"  # Light red
                            text_color = "#CC0000"  # Dark red
                            category = "Severe"
                        elif height >= sd3neg and height < sd2neg:
                            color = "#FFFFCC"  # Light yellow
                            text_color = "#999900"  # Dark yellow
                            category = "Moderate"
                        elif height >= sd2neg and height <= sd2:
                            color = "#CCFFCC"  # Light green
                            text_color = "#006600"  # Dark green
                            category = "Normal"
                        else:
                            color = "#E6E6E6"  # Light gray for above normal
                            text_color = "#666666"  # Dark gray
                            category = "Above Normal/Very Tall"

                        row["height_for_age_status"] = format_cell(z_score, color, text_color)
                        row["height_for_age_status_cat"] = format_cell(category, color, text_color)   
                    except (ValueError, TypeError):
                        pass
            except (ValueError, TypeError):
                pass

    return columns, data


def format_cell(value, bg_color, text_color):
    """Helper function to format cells consistently"""
    return f"""
        <div style='
            background-color: {bg_color};
            color: {text_color};
            border-radius: 3px;
            text-align: center;
            font-weight: bold;
        '>
            {value}
        </div>
    """









#backup-Before age of Creche filter
# import frappe
# import math
# from frappe.utils import nowdate
# import calendar
# from datetime import datetime, timedelta, date
# from dateutil.relativedelta import relativedelta
# from collections import defaultdict


# def calculate_z_score(value, M, L, S):
#     if L == 0:
#         raise ValueError("L should not be zero to avoid division errors.")

#     ratio = float(value / M)
#     ratio_to_L = float(math.pow(ratio, L))
#     numerator = float(ratio_to_L - 1)
#     denominator = float(S * L)
#     z_score = float(numerator / denominator)

#     if z_score <= -3:
#         sd3neg = float(M * math.pow(1 + L * S * (-3), 1 / L))
#         sd2neg = float(M * math.pow(1 + L * S * (-2), 1 / L))
#         sd23neg = float(sd2neg - sd3neg)
#         z_score = float(-3 + (value - sd3neg) / sd23neg)

#     elif z_score >= 3:
#         sd3pos = float(M * math.pow(1 + L * S * (3), 1 / L))
#         sd2pos = float(M * math.pow(1 + L * S * (2), 1 / L))
#         sd23pos = float(sd3pos - sd2pos)
#         z_score = float(3 + (value - sd3pos) / sd23pos)

#     return round(z_score, 2)


# def weight_for_age_boys_table():
#     fields_to_fetch = [
#         "age_in_days", "green", "l", "m", "s",
#         "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
#         "sd1", "sd2", "sd3", "sd4"
#     ]
#     records = frappe.get_all("Weight for age Boys", fields=fields_to_fetch)
#     return {row["age_in_days"]: row for row in records}


# def weight_for_age_girls_table():
#     fields_to_fetch = [
#         "age_in_days", "green", "l", "m", "s",
#         "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
#         "sd1", "sd2", "sd3", "sd4"
#     ]
#     records = frappe.get_all("Weight for age Girls", fields=fields_to_fetch)
#     return {row["age_in_days"]: row for row in records}


# def weight_to_height_boys():
#     fields = [
#         "age_type", "length", "green", "l", "m", "s",
#         "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
#         "sd1", "sd2", "sd3", "sd4"
#     ]
#     try:
#         records = frappe.get_all("Weight to Height Boys", fields=fields, limit=0)
#         data = defaultdict(list)
#         for row in records:
#             data[row["length"]].append(row)
#         return dict(data)
#     except Exception as e:
#         frappe.log_error(f"Error loading boys data: {str(e)}")
#         return {}


# def weight_to_height_girls():
#     fields = [
#         "age_type", "length", "green", "l", "m", "s",
#         "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
#         "sd1", "sd2", "sd3", "sd4"
#     ]
#     try:
#         records = frappe.get_all("Weight to Height Girls", fields=fields, limit=0)
#         data = defaultdict(list)
#         for row in records:
#             data[row["length"]].append(row)
#         return dict(data)
#     except Exception as e:
#         frappe.log_error(f"Error loading girls data: {str(e)}")
#         return {}


# def height_for_age_boys():
#     fields_to_fetch = [
#         "age_in_days", "green", "l", "m", "s",
#         "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
#         "sd1", "sd2", "sd3", "sd4"
#     ]
#     records = frappe.get_all("Height for age Boys", fields=fields_to_fetch)
#     return {row["age_in_days"]: row for row in records}


# def height_for_age_girls():
#     fields_to_fetch = [
#         "age_in_days", "green", "l", "m", "s",
#         "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
#         "sd1", "sd2", "sd3", "sd4"
#     ]
#     records = frappe.get_all("Height for age Girls", fields=fields_to_fetch)
#     return {row["age_in_days"]: row for row in records}


# def get_columns():
#     return [
#         {"label": "Partner", "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": "State", "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": "District", "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": "Block", "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": "GP", "fieldname": "gp", "fieldtype": "Data", "width": 120},
#         {"label": "Creche ID", "fieldname": "creche_id", "fieldtype": "Data", "width": 150},
#         {"label": "Creche", "fieldname": "creche_name", "fieldtype": "Data", "width": 200},
#         {"label": "Supervisor", "fieldname": "supervisor", "fieldtype": "Data", "width": 200},
#         {"label": "Child ID", "fieldname": "child_id", "fieldtype": "Data", "width": 150},
#         {"label": "Child Name", "fieldname": "child_name", "fieldtype": "Data", "width": 200},
#         {"label": "Gender", "fieldname": "gender", "fieldtype": "Data", "width": 100},
#         {"label": "Date of Birth", "fieldname": "child_dob", "fieldtype": "Data", "width": 150},
#         # {"label": "DOB at Measurement", "fieldname": "mbob", "fieldtype": "Data", "width": 180},
#         {"label": "Measurement Date", "fieldname": "measurements_taken_date", "fieldtype": "Data", "width": 200},
#         {"label": "Age (in Days)", "fieldname": "age_months", "fieldtype": "Data", "width": 200},
#         {"label": "Measurement Taken", "fieldname": "measurements_taken", "fieldtype": "Data", "width": 180},
#         {"label": "Measurement Equipment", "fieldname": "measurement_equipment_type", "fieldtype": "Data", "width": 180},
#         {"label": "Weight (kg)", "fieldname": "weight", "fieldtype": "Data", "width": 130},
#         {"label": "Height (cm)", "fieldname": "height", "fieldtype": "Data", "width": 130},
#         {"label": "Weight for Age", "fieldname": "weight_for_age_status", "fieldtype": "Data", "width": 150},
#         {"label": "Weight for Height", "fieldname": "weight_for_height_status", "fieldtype": "Data", "width": 150},
#         {"label": "Height for Age", "fieldname": "height_for_age_status", "fieldtype": "Data", "width": 150},
#         {"label": "Weight for Age Category", "fieldname": "weight_for_age_status_cat", "fieldtype": "Data", "width": 200},
#         {"label": "Weight for Height Category", "fieldname": "weight_for_height_status_cat", "fieldtype": "Data", "width": 200},
#         {"label": "Height for Age Category", "fieldname": "height_for_age_status_cat", "fieldtype": "Data", "width": 200}
#     ]


# @frappe.whitelist()
# def get_summary_data(filters=None):
#     month = int(filters.get("month") if filters else nowdate().split('-')[1])
#     year = int(filters.get("year") if filters else nowdate().split('-')[0])
#     start_date = date(year, month, 1)
#     last_day = calendar.monthrange(year, month)[1]
#     end_date = date(year, month, last_day)
    
#     # Get current user's partner and geography mapping
#     current_user_partner = frappe.db.get_value("User", frappe.session.user, "partner")
#     state_query = """ 
#         SELECT state_id, district_id, block_id, gp_id
#         FROM `tabUser Geography Mapping`
#         WHERE parent = %s
#         ORDER BY state_id, district_id, block_id, gp_id
#     """
#     current_user_state = frappe.db.sql(state_query, frappe.session.user, as_dict=True)
    
#     # Initialize filter parameters
#     params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         "year": year,
#         "month": month,
#         "partner": filters.get("partner") if filters else current_user_partner,
#         "state": filters.get("state") if filters else None,
#         "district": filters.get("district") if filters else None,
#         "block": filters.get("block") if filters else None,
#         "gp": filters.get("gp") if filters else None,
#         "creche": filters.get("creche") if filters else None,
#         "supervisor_id": filters.get("supervisor_id") if filters else None,
#         "creche_status_id": filters.get("creche_status_id") if filters else None,
#         "mea_taken": filters.get("mea_taken") if filters else None,
#         "phases": None,
#         "cstart_date": None,
#         "cend_date": None,
#         "state_ids": None,
#         "district_ids": None,
#         "block_ids": None,
#         "gp_ids": None
#     }
    
#     # Handle phases filter
#     if filters and filters.get("phases"):
#         phases_cleaned = ",".join(p.strip() for p in filters["phases"].split(",") if p.strip().isdigit())
#         params["phases"] = phases_cleaned
    
#     # Handle creche opening date range filter
#     range_type = filters.get("cr_opening_range_type") if filters else None
#     if range_type:
#         single_date = filters.get("single_date")
#         date_range = filters.get("c_opening_range")

#         if single_date and isinstance(single_date, str):
#             single_date = datetime.strptime(single_date, "%Y-%m-%d").date()
            
#         if range_type == "between" and date_range and len(date_range) == 2:
#             params["cstart_date"], params["cend_date"] = date_range
#         elif range_type == "before" and single_date:
#             params["cstart_date"], params["cend_date"] = date(2017, 1, 1), single_date - timedelta(days=1)
#         elif range_type == "after" and single_date:
#             params["cstart_date"], params["cend_date"] = single_date + timedelta(days=1), date.today()
#         elif range_type == "equal" and single_date:
#             params["cstart_date"] = params["cend_date"] = single_date
    
#     # Handle default geography if no explicit filters
#     if not any([params["state"], params["district"], params["block"], params["gp"]]):
#         if current_user_state:
#             state_ids = ",".join(str(s["state_id"]) for s in current_user_state if s.get("state_id"))
#             district_ids = ",".join(str(s["district_id"]) for s in current_user_state if s.get("district_id"))
#             block_ids = ",".join(str(s["block_id"]) for s in current_user_state if s.get("block_id"))
#             gp_ids = ",".join(str(s["gp_id"]) for s in current_user_state if s.get("gp_id"))
            
#             if state_ids:
#                 params["state_ids"] = state_ids
#             if district_ids:
#                 params["district_ids"] = district_ids
#             if block_ids:
#                 params["block_ids"] = block_ids
#             if gp_ids:
#                 params["gp_ids"] = gp_ids
    
#     # Calculate previous months for any potential future use
#     if month == 1:
#         params.update({
#             "lmonth": 12,
#             "plmonth": 11,
#             "lyear": year - 1,
#             "pyear": year - 1
#         })
#     elif month == 2:
#         params.update({
#             "lmonth": 1,
#             "plmonth": 12,
#             "lyear": year,
#             "pyear": year - 1
#         })
#     else:
#         params.update({
#             "lmonth": month - 1,
#             "plmonth": month - 2,
#             "lyear": year,
#             "pyear": year
#         })

#     sql_query = """
#         SELECT p.partner_name AS partner,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             g.gp_name AS gp,
#             cr.creche_name AS 'creche_name',
#             usr.full_name AS 'supervisor',
#             cee.child_id AS 'child_id',
#             cr.creche_id AS 'creche_id',
#             cee.child_name AS 'child_name',
#             cee.age_at_enrollment_in_months AS 'age',
#             DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS 'child_dob',
#             CASE WHEN ad.do_you_have_height_weight = 1 THEN
#             DATE_FORMAT(DATE_SUB(ad.measurement_taken_date, INTERVAL ad.age_months DAY), '%%d-%%m-%%Y') ELSE '-' END AS mbob,
#             (CASE 
#                 WHEN cee.gender_id = '1' THEN 'M'
#                 WHEN cee.gender_id = '2' THEN 'F'
#                 ELSE 'Other'
#             END) AS gender,
#             ad.height AS 'height',
#             ad.weight AS 'weight',
#             IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS 'measurements_taken',
#             IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS 'measurements_taken_date',
#             CASE WHEN ad.do_you_have_height_weight = 1 THEN ad.age_months ELSE '-' END AS age_months,
#             cee.gender_id as gender_id,
#             CASE 
#                 WHEN ad.measurement_equipment = 1 THEN 'Stadiometer'
#                 WHEN ad.measurement_equipment = 2 THEN 'Infantometer'
#                 ELSE '-'
#             END AS measurement_equipment_type
#         FROM  
#             `tabAnthropromatic Data` AS ad 
#         INNER JOIN 
#             `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
#         INNER JOIN 
#             `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid 
#         INNER JOIN 
#             `tabCreche` AS cr ON cgm.creche_id = cr.name 
#         INNER JOIN 
#             `tabUser` AS usr ON cr.supervisor_id = usr.name 
#         INNER JOIN 
#             `tabPartner` AS p ON p.name = cr.partner_id
#         INNER JOIN 
#             `tabState` AS s ON s.name = cr.state_id
#         INNER JOIN 
#             `tabDistrict` AS d ON d.name = cr.district_id
#         INNER JOIN 
#             `tabBlock` AS b ON b.name = cr.block_id
#         INNER JOIN 
#             `tabGram Panchayat` AS g ON g.name = cr.gp_id
#         WHERE 
#             YEAR(cgm.measurement_date) = %(year)s
#             AND MONTH(cgm.measurement_date) = %(month)s
#             AND (%(partner)s IS NULL OR cr.partner_id = %(partner)s) 
#             AND (
#                 (%(state)s IS NULL AND %(state_ids)s IS NULL) 
#                 OR cr.state_id = %(state)s 
#                 OR (%(state)s IS NULL AND %(state_ids)s IS NOT NULL AND FIND_IN_SET(cr.state_id, %(state_ids)s))
#             )
#             AND (
#                 (%(district)s IS NULL AND %(district_ids)s IS NULL) 
#                 OR cr.district_id = %(district)s 
#                 OR (%(district)s IS NULL AND %(district_ids)s IS NOT NULL AND FIND_IN_SET(cr.district_id, %(district_ids)s))
#             )
#             AND (
#                 (%(block)s IS NULL AND %(block_ids)s IS NULL) 
#                 OR cr.block_id = %(block)s 
#                 OR (%(block)s IS NULL AND %(block_ids)s IS NOT NULL AND FIND_IN_SET(cr.block_id, %(block_ids)s))
#             )
#             AND (
#                 (%(gp)s IS NULL AND %(gp_ids)s IS NULL) 
#                 OR cr.gp_id = %(gp)s 
#                 OR (%(gp)s IS NULL AND %(gp_ids)s IS NOT NULL AND FIND_IN_SET(cr.gp_id, %(gp_ids)s))
#             )
#             AND (%(creche)s IS NULL OR cr.name = %(creche)s)
#             AND (%(creche_status_id)s IS NULL OR cr.creche_status_id = %(creche_status_id)s)
#             AND (%(phases)s IS NULL OR FIND_IN_SET(cr.phase, %(phases)s))
#             AND (%(supervisor_id)s IS NULL OR cr.supervisor_id = %(supervisor_id)s)
#             AND (%(mea_taken)s IS NULL OR ad.do_you_have_height_weight = %(mea_taken)s)
#             AND cee.date_of_enrollment <= %(end_date)s
#             AND (cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)
#             AND (
#                 (%(cstart_date)s IS NULL AND %(cend_date)s IS NULL) 
#                 OR (cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s)
#             )
#         ORDER BY
#             cr.partner_id, cr.state_id, cr.district_id, cr.block_id, cr.gp_id, cr.supervisor_id, cr.name, cee.child_name

#     """
#     data = frappe.db.sql(sql_query, params, as_dict=True)

#     # Calculate summary counts
#     counts = {
#         "child_name": len(data),
#         "measurements_taken": sum(1 for row in data if row.get("measurements_taken") == "Y")
#     }

#     # Add summary row
#     summary_row = {
#         "partner": "<b style='color:black;'>Total</b>",
#         "child_name": counts['child_name'],
#         "measurements_taken": counts['measurements_taken']
#     }
#     data.append(summary_row)

#     return data


# def execute(filters=None):
#     columns = get_columns()
#     data = get_summary_data(filters)

#     # Load all growth reference data
#     weight_for_age_boys_data = weight_for_age_boys_table()
#     weight_for_age_girls_data = weight_for_age_girls_table()
#     weight_to_height_boys_data = weight_to_height_boys()
#     weight_to_height_girls_data = weight_to_height_girls()
#     height_for_age_boys_data = height_for_age_boys()
#     height_for_age_girls_data = height_for_age_girls()
    
#     for row in data:
#         if not isinstance(row, dict):  # Skip summary row
#             continue
            
#         age_months = row.get("age_months")
#         gender_id = row.get("gender_id")
#         weight = row.get("weight")
#         height = row.get("height")
#         measurement_equipment = row.get("measurement_equipment_type")
#         measurement_date = row.get("measurements_taken_date")
        
#         # Initialize all status fields
#         row["weight_for_age_status"] = None
#         row["weight_for_height_status"] = None
#         row["height_for_age_status"] = None
#         row["weight_for_age_status_cat"] = None
#         row["weight_for_height_status_cat"] = None
#         row["height_for_age_status_cat"] = None
        
#         # Calculate weight-for-age status
#         if age_months is not None and weight is not None and weight > 0 and gender_id in ('1', '2'):
#             try:
#                 age_in_days = int(age_months)
#                 weight = float(weight)
                
#                 growth_data = weight_for_age_boys_data.get(age_in_days) if gender_id == '1' else weight_for_age_girls_data.get(age_in_days)
                    
#                 if growth_data:
#                     try:
#                         L = float(growth_data.get("l", 0))
#                         M = float(growth_data.get("m", 0))
#                         S = float(growth_data.get("s", 0))
#                         z_score = calculate_z_score(weight, M, L, S)                        
#                         sd3neg = float(growth_data.get("sd3neg", 0))
#                         sd2neg = float(growth_data.get("sd2neg", 0))
#                         sd2 = float(growth_data.get("sd2", 0))
                        
#                         if weight < sd3neg:
#                             color = "#FFCCCC"  # Light red
#                             text_color = "#CC0000"  # Dark red
#                             category = "Severe"
#                         elif weight >= sd3neg and weight < sd2neg:
#                             color = "#FFFFCC"  # Light yellow
#                             text_color = "#999900"  # Dark yellow
#                             category = "Moderate"
#                         elif weight >= sd2neg and weight <= sd2:
#                             color = "#CCFFCC"  # Light green
#                             text_color = "#006600"  # Dark green
#                             category = "Normal"
#                         else:
#                             color = "#E6E6E6"  # Light gray for above normal
#                             text_color = "#666666"  # Dark gray
#                             category = "Overweight/Obese"

#                         row["weight_for_age_status"] = format_cell(z_score, color, text_color)
#                         row["weight_for_age_status_cat"] = format_cell(category, color, text_color)
                            
#                     except (ValueError, TypeError):
#                         pass
#             except (ValueError, TypeError):
#                 pass
                
#         # Calculate weight-for-height status
#         if height is not None and weight is not None and weight > 0 and height > 0 and gender_id in ('1', '2'):
#             try:
#                 height_rounded = round(height,1)
#                 weight = float(weight)
#                 age_in_days = int(age_months)
                
#                 age_type_0_boys = {
#                     height: next(
#                         (record for record in records if str(record.get('age_type')).strip() in ['0', '0.0']),
#                         None
#                     )
#                     for height, records in weight_to_height_boys_data.items()
#                 }

#                 age_type_24_boys = {
#                     height: next(
#                         (record for record in records if str(record.get('age_type')).strip() in ['24', '24.0']),
#                         None
#                     )
#                     for height, records in weight_to_height_boys_data.items()
#                 }

#                 age_type_0_girls = {
#                     height: next(
#                         (record for record in records if str(record.get('age_type')).strip() in ['0', '0.0']),
#                         None
#                     )
#                     for height, records in weight_to_height_girls_data.items()
#                 }

#                 age_type_24_girls = {
#                     height: next(
#                         (record for record in records if str(record.get('age_type')).strip() in ['24', '24.0']),
#                         None
#                     )
#                     for height, records in weight_to_height_girls_data.items()
#                 }

#                 wfh_growth_data = None
#                 if age_in_days < 730:
#                     if measurement_equipment == 'Stadiometer':
#                         height_rounded = round(height_rounded + 0.7,1)

#                 if age_in_days > 730:
#                     if measurement_equipment == 'Infantometer':
#                         height_rounded = round(height_rounded - 0.7,1)

#                 if age_in_days <= 730:
#                     if gender_id == '1':
#                         wfh_growth_data = age_type_0_boys.get(height_rounded)
#                     else:
#                         wfh_growth_data = age_type_0_girls.get(height_rounded)

#                 if age_in_days > 730:
#                     if gender_id == '1':
#                         wfh_growth_data = age_type_24_boys.get(height_rounded)
#                     else:
#                         wfh_growth_data = age_type_24_girls.get(height_rounded)

#                 if wfh_growth_data:
#                     try:
#                         L = float(wfh_growth_data.get("l", 0))
#                         M = float(wfh_growth_data.get("m", 0))
#                         S = float(wfh_growth_data.get("s", 0))
#                         z_score = calculate_z_score(weight, M, L, S)
                        
#                         sd3neg = float(wfh_growth_data.get("sd3neg", 0))
#                         sd2neg = float(wfh_growth_data.get("sd2neg", 0))
#                         sd2 = float(wfh_growth_data.get("sd2", 0))

#                         if weight < sd3neg:
#                             color = "#FFCCCC"  # Light red
#                             text_color = "#CC0000"  # Dark red
#                             category = "Severe"
#                         elif weight >= sd3neg and weight < sd2neg:
#                             color = "#FFFFCC"  # Light yellow
#                             text_color = "#999900"  # Dark yellow
#                             category = "Moderate"
#                         elif weight >= sd2neg and weight <= sd2:
#                             color = "#CCFFCC"  # Light green
#                             text_color = "#006600"  # Dark green
#                             category = "Normal"
#                         else:
#                             color = "#E6E6E6"  # Light gray for above normal
#                             text_color = "#666666"  # Dark gray
#                             category = "Overweight/Obese"
                        
#                         row["weight_for_height_status"] = format_cell(z_score, color, text_color)
#                         row["weight_for_height_status_cat"] = format_cell(category, color, text_color)
#                     except (ValueError, TypeError):
#                         pass
#             except (ValueError, TypeError):
#                 pass

#         # Calculate height-for-age status
#         if age_months is not None and height is not None and height > 0 and gender_id in ('1', '2'):
#             try:
#                 age_in_days = int(age_months)
#                 height = float(height)
                
#                 if measurement_equipment and measurement_date:
#                     measurement_date = datetime.strptime(measurement_date, "%d-%m-%Y").date()
#                     two_years_ago = measurement_date - relativedelta(months=24)
#                     dob = measurement_date - timedelta(days=age_in_days)
#                     if dob > two_years_ago:
#                         if measurement_equipment == 'Stadiometer':
#                             height = round(height + 0.7, 1)

#                     else:
#                         if measurement_equipment == 'Infantometer':
#                             height = round(height - 0.7, 1)

                
#                 # Get growth data
#                 growth_data = height_for_age_boys_data.get(age_in_days) if gender_id == '1' else height_for_age_girls_data.get(age_in_days)
                
#                 if growth_data:
#                     try:
#                         L = float(growth_data.get("l", 0))
#                         M = float(growth_data.get("m", 0))
#                         S = float(growth_data.get("s", 0))
#                         z_score = calculate_z_score(height, M, L, S)
                        
#                         sd3neg = float(growth_data.get("sd3neg", 0))
#                         sd2neg = float(growth_data.get("sd2neg", 0))
#                         sd2 = float(growth_data.get("sd2", 0))
                        
#                         if height < sd3neg:
#                             color = "#FFCCCC"  # Light red
#                             text_color = "#CC0000"  # Dark red
#                             category = "Severe"
#                         elif height >= sd3neg and height < sd2neg:
#                             color = "#FFFFCC"  # Light yellow
#                             text_color = "#999900"  # Dark yellow
#                             category = "Moderate"
#                         elif height >= sd2neg and height <= sd2:
#                             color = "#CCFFCC"  # Light green
#                             text_color = "#006600"  # Dark green
#                             category = "Normal"
#                         else:
#                             color = "#E6E6E6"  # Light gray for above normal
#                             text_color = "#666666"  # Dark gray
#                             category = "Above Normal/Very Tall"

#                         row["height_for_age_status"] = format_cell(z_score, color, text_color)
#                         row["height_for_age_status_cat"] = format_cell(category, color, text_color)   
#                     except (ValueError, TypeError):
#                         pass
#             except (ValueError, TypeError):
#                 pass

#     return columns, data


# def format_cell(value, bg_color, text_color):
#     """Helper function to format cells consistently"""
#     return f"""
#         <div style='
#             background-color: {bg_color};
#             color: {text_color};
#             border-radius: 3px;
#             text-align: center;
#             font-weight: bold;
#         '>
#             {value}
#         </div>
#     """