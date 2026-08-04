import frappe
from collections import defaultdict
from datetime import datetime
import calendar
from datetime import datetime, timedelta
from frappe.utils import getdate


# Standard data fetchers
@frappe.whitelist()
def get_boys_weight_for_age():
    return weight_for_age_boys_table()

@frappe.whitelist()
def get_girls_weight_for_age():
    return weight_for_age_girls_table()

@frappe.whitelist()
def get_boys_height_for_age():
    return height_for_age_boys()

@frappe.whitelist()
def get_girls_height_for_age():
    return height_for_age_girls()

@frappe.whitelist()
def get_boys_weight_for_height():
    return weight_to_height_boys()

@frappe.whitelist()
def get_girls_weight_for_height():
    return weight_to_height_girls()

def weight_to_height_boys():
    fields = [
        "age_type", "length", "green", "l", "m", "s","sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0","sd1", "sd2", "sd3", "sd4"]
    try:
        records = frappe.get_all("Weight to Height Boys", fields=fields, limit=0)
        data = defaultdict(list)
        for row in records:
            # Convert length to string to ensure consistent key type
            data[str(row["length"])].append(row)
        return dict(data)
    except Exception as e:
        frappe.log_error(f"Error loading boys weight-for-height data: {str(e)}")
        return {}

def weight_to_height_girls():
    fields = ["age_type", "length", "green", "l", "m", "s","sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0","sd1", "sd2", "sd3", "sd4"]
    try:
        records = frappe.get_all("Weight to Height Girls", fields=fields, limit=0)
        data = defaultdict(list)
        for row in records:
            # Convert length to string to ensure consistent key type
            data[str(row["length"])].append(row)
        return dict(data)
    except Exception as e:
        frappe.log_error(f"Error loading girls weight-for-height data: {str(e)}")
        return {}
    

def weight_for_age_boys_table():
    fields = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    try:
        records = frappe.get_all(
            "Weight for age Boys",
            fields=fields,
            filters={"age_in_days": ("<=", 1200)},  # restrict here
            order_by="age_in_days asc",
            limit=0
        )
        return {row["age_in_days"]: row for row in records}
    except Exception as e:
        frappe.log_error(f"Error loading boys weight-for-age data: {str(e)}")
        return {}

def weight_for_age_girls_table():
    fields = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    try:
        records = frappe.get_all(
            "Weight for age Girls",
            fields=fields,
            filters={"age_in_days": ("<=", 1200)},  # restrict here
            order_by="age_in_days asc",
            limit=0
        )
        return {row["age_in_days"]: row for row in records}
    except Exception as e:
        frappe.log_error(f"Error loading girls weight-for-age data: {str(e)}")
        return {}

def height_for_age_boys():
    fields = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    try:
        records = frappe.get_all(
            "Height for age Boys",
            fields=fields,
            filters={"age_in_days": ("<=", 1200)},  # restrict here
            order_by="age_in_days asc",
            limit=0
        )
        return {row["age_in_days"]: row for row in records}
    except Exception as e:
        frappe.log_error(f"Error loading boys height-for-age data: {str(e)}")
        return {}

def height_for_age_girls():
    fields = [
        "age_in_days", "green", "l", "m", "s",
        "sd4neg", "sd3neg", "sd2neg", "sd1neg", "sd0",
        "sd1", "sd2", "sd3", "sd4"
    ]
    try:
        records = frappe.get_all(
            "Height for age Girls",
            fields=fields,
            filters={"age_in_days": ("<=", 1200)},  # restrict here
            order_by="age_in_days asc",
            limit=0
        )
        return {row["age_in_days"]: row for row in records}
    except Exception as e:
        frappe.log_error(f"Error loading girls height-for-age data: {str(e)}")
        return {}



@frappe.whitelist()
def growth_chart_data(year=None, month=None, partner_id=None, state_id=None,
                     district_id=None, block_id=None, gp_id=None,
                     creche_id=None, child_name=None, gender_id=None, supervisor_id=None):
    """Get filtered growth chart data for the table view"""
    conditions = []
    filters = {}

    if year:
        conditions.append("YEAR(cgm.measurement_date) = %(year)s")
        filters["year"] = year
    if month:
        conditions.append("MONTH(cgm.measurement_date) = %(month)s")
        filters["month"] = month
    if partner_id:
        conditions.append("cgm.partner_id = %(partner_id)s")
        filters["partner_id"] = partner_id
    if state_id:
        conditions.append("cgm.state_id = %(state_id)s")
        filters["state_id"] = state_id
    if district_id:
        conditions.append("cgm.district_id = %(district_id)s")
        filters["district_id"] = district_id
    if block_id:
        conditions.append("cgm.block_id = %(block_id)s")
        filters["block_id"] = block_id
    if gp_id:
        conditions.append("cgm.gp_id = %(gp_id)s")
        filters["gp_id"] = gp_id
    if creche_id:
        conditions.append("cee.creche_id = %(creche_id)s")
        filters["creche_id"] = creche_id
    if child_name:
        conditions.append("cee.name = %(child_name)s")
        filters["child_name"] = child_name
    if gender_id:
        conditions.append("cee.gender_id = %(gender_id)s")
        filters["gender_id"] = gender_id
    if supervisor_id:
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        filters["supervisor_id"] = supervisor_id

    condition_sql = " AND ".join(conditions) if conditions else "1 = 1"

    # Derive rolling-month parameters needed for SNC sub-joins
    _year  = int(year)  if year  else datetime.today().year
    _month = int(month) if month else datetime.today().month

    def _rollback(y, m, step):
        m -= step
        while m <= 0:
            m += 12
            y -= 1
        return m, y

    prev_priority_month = _month - 1 if _month > 1 else 12
    prev_priority_year  = _year if _month > 1 else _year - 1
    prev_fallback_month = _month - 2 if _month > 2 else (_month + 10 if _month == 1 else 11)
    prev_fallback_year  = _year if _month > 2 else (_year - 1)

    gf2_priority_month = _month - 2 if _month > 2 else _month + 10
    gf2_priority_year  = _year if _month > 2 else _year - 1
    gf2_fallback_month = _month - 3 if _month > 3 else _month + 9
    gf2_fallback_year  = _year if _month > 3 else _year - 1

    m1_month, m1_year = _rollback(_year, _month, 1)
    m2_month, m2_year = _rollback(_year, _month, 2)
    m3_month, m3_year = _rollback(_year, _month, 3)
    m4_month, m4_year = _rollback(_year, _month, 4)

    filters.update({
        "prev_priority_year": prev_priority_year, "prev_priority_month": prev_priority_month,
        "prev_fallback_year": prev_fallback_year, "prev_fallback_month": prev_fallback_month,
        "gf2_priority_year":  gf2_priority_year,  "gf2_priority_month":  gf2_priority_month,
        "gf2_fallback_year":  gf2_fallback_year,  "gf2_fallback_month":  gf2_fallback_month,
        "m1_month": m1_month, "m1_year": m1_year,
        "m2_month": m2_month, "m2_year": m2_year,
        "m3_month": m3_month, "m3_year": m3_year,
        "m4_month": m4_month, "m4_year": m4_year,
    })

    try:
        data = frappe.db.sql(f"""
            SELECT
                cr.creche_name AS creche_name,
                p.partner_name AS partner_name,
                usr.full_name AS 'supervisor',
                cee.child_id AS child_id,
                cr.creche_id AS creche_id,
                cee.child_name AS child_name,
                cee.name AS child_idx,
                DATE_FORMAT(cee.date_of_enrollment, '%%d-%%m-%%Y') AS date_of_enrollment,
                cee.age_at_enrollment_in_months AS age,
                DATE_FORMAT(cee.child_dob, '%%d-%%m-%%Y') AS child_dob,
                CASE
                    WHEN ad.do_you_have_height_weight = 1
                    THEN DATE_FORMAT(DATE_SUB(ad.measurement_taken_date, INTERVAL ad.age_months DAY), '%%d-%%m-%%Y')
                    ELSE '-'
                END AS mbob,
                CASE
                    WHEN cee.gender_id = '1' THEN 'Male'
                    WHEN cee.gender_id = '2' THEN 'Female'
                    ELSE cee.gender_id
                END AS gender,
                ad.height AS height,
                ad.weight AS weight,
                IF(ad.do_you_have_height_weight = 1, 'Y', 'N') AS measurements_taken,
                IFNULL(DATE_FORMAT(ad.measurement_taken_date, '%%d-%%m-%%Y'), '-') AS measurements_taken_date,
                CASE
                    WHEN ad.do_you_have_height_weight = 1 THEN ad.age_months
                    ELSE '-'
                END AS age_months,
                cee.gender_id AS gender_id,
                CASE
                    WHEN ad.measurement_equipment = 1 THEN 'Stadiometer'
                    WHEN ad.measurement_equipment = 2 THEN 'Infantometer'
                    ELSE '-'
                END AS measurement_equipment_type,
                CASE
                    WHEN ad.measurement_position = 1 THEN 'Standing'
                    WHEN ad.measurement_position = 2 THEN 'Lying'
                    ELSE '-'
                END AS measurement_position_type,
                ad.weight_for_age_zscore,
                ad.height_for_age_zscore,
                ad.weight_for_height_zscore,
                
                CASE 
                    WHEN (ad.weight_for_age_zscore IS NOT NULL AND CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) <= -3)
                      OR (ad.height_for_age_zscore IS NOT NULL AND CAST(ad.height_for_age_zscore AS DECIMAL(10,4)) <= -3)
                      OR (ad.weight_for_height_zscore IS NOT NULL AND CAST(ad.weight_for_height_zscore AS DECIMAL(10,4)) <= -3)
                    THEN 1 
                    ELSE 0 
                END AS is_severe,

                CASE WHEN (
                    (
                        COALESCE(snc_gf1.prev_zscore, snc_gf1.fallback_zscore) IS NOT NULL
                        AND (COALESCE(snc_gf1.prev_zscore, snc_gf1.fallback_zscore) - CAST(ad.weight_for_age_zscore AS DECIMAL(10,4))) > 0
                    )
                    OR (
                        COALESCE(snc_gf1.prev_zscore, snc_gf1.fallback_zscore) IS NOT NULL
                        AND (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(snc_gf1.prev_zscore, snc_gf1.fallback_zscore)) <= -0.5
                    )
                    OR (
                        COALESCE(snc_gf2.priority_zscore, snc_gf2.fallback_zscore) IS NOT NULL
                        AND (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(snc_gf2.priority_zscore, snc_gf2.fallback_zscore)) <= -0.5
                    )
                    OR (
                        snc_zz.m1_zscore IS NOT NULL AND snc_zz.m2_zscore IS NOT NULL
                        AND snc_zz.m3_zscore IS NOT NULL AND snc_zz.m4_zscore IS NOT NULL
                        AND (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(snc_zz.m4_zscore, snc_zz.m3_zscore, snc_zz.m2_zscore, snc_zz.m1_zscore)) <= -0.5
                        AND (
                            (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) > snc_zz.m1_zscore)
                            OR (snc_zz.m1_zscore > snc_zz.m2_zscore)
                            OR (snc_zz.m2_zscore > snc_zz.m3_zscore)
                            OR (snc_zz.m3_zscore > snc_zz.m4_zscore)
                        )
                        AND (
                            (CAST(ad.weight_for_age_zscore AS DECIMAL(10,4)) < snc_zz.m1_zscore)
                            OR (snc_zz.m1_zscore < snc_zz.m2_zscore)
                            OR (snc_zz.m2_zscore < snc_zz.m3_zscore)
                            OR (snc_zz.m3_zscore < snc_zz.m4_zscore)
                        )
                    )
                    OR ad.weight_for_age = 1
                    OR ad.weight_for_height = 1
                ) THEN 1 ELSE 0 END AS is_snc
            FROM
                `tabAnthropromatic Data` AS ad
            INNER JOIN `tabChild Growth Monitoring` AS cgm ON ad.parent = cgm.name
            INNER JOIN `tabChild Enrollment and Exit` AS cee ON cee.childenrollguid = ad.childenrollguid
            INNER JOIN `tabCreche` AS cr ON cgm.creche_id = cr.name
            INNER JOIN `tabUser` AS usr ON cr.supervisor_id = usr.name
            INNER JOIN `tabPartner` AS p ON p.name = cr.partner_id
            INNER JOIN `tabState` AS s ON s.name = cr.state_id
            INNER JOIN `tabDistrict` AS d ON d.name = cr.district_id
            INNER JOIN `tabBlock` AS b ON b.name = cr.block_id
            INNER JOIN `tabGram Panchayat` AS g ON g.name = cr.gp_id
            LEFT JOIN (
                SELECT
                    childenrollguid,
                    MAX(CASE
                        WHEN YEAR(measurement_taken_date) = %(prev_priority_year)s
                        AND MONTH(measurement_taken_date) = %(prev_priority_month)s
                        THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                    END) AS prev_zscore,
                    MAX(CASE
                        WHEN YEAR(measurement_taken_date) = %(prev_fallback_year)s
                        AND MONTH(measurement_taken_date) = %(prev_fallback_month)s
                        THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                    END) AS fallback_zscore
                FROM `tabAnthropromatic Data`
                WHERE do_you_have_height_weight = 1
                AND weight_for_age_zscore IS NOT NULL
                AND (
                    (YEAR(measurement_taken_date) = %(prev_priority_year)s AND MONTH(measurement_taken_date) = %(prev_priority_month)s)
                    OR (YEAR(measurement_taken_date) = %(prev_fallback_year)s AND MONTH(measurement_taken_date) = %(prev_fallback_month)s)
                )
                GROUP BY childenrollguid
            ) AS snc_gf1 ON snc_gf1.childenrollguid = ad.childenrollguid
            LEFT JOIN (
                SELECT
                    childenrollguid,
                    MAX(CASE
                        WHEN YEAR(measurement_taken_date) = %(gf2_priority_year)s
                        AND MONTH(measurement_taken_date) = %(gf2_priority_month)s
                        THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                    END) AS priority_zscore,
                    MAX(CASE
                        WHEN YEAR(measurement_taken_date) = %(gf2_fallback_year)s
                        AND MONTH(measurement_taken_date) = %(gf2_fallback_month)s
                        THEN CAST(weight_for_age_zscore AS DECIMAL(10,4))
                    END) AS fallback_zscore
                FROM `tabAnthropromatic Data`
                WHERE do_you_have_height_weight = 1
                AND weight_for_age_zscore IS NOT NULL
                AND (
                    (YEAR(measurement_taken_date) = %(gf2_priority_year)s AND MONTH(measurement_taken_date) = %(gf2_priority_month)s)
                    OR (YEAR(measurement_taken_date) = %(gf2_fallback_year)s AND MONTH(measurement_taken_date) = %(gf2_fallback_month)s)
                )
                GROUP BY childenrollguid
            ) AS snc_gf2 ON snc_gf2.childenrollguid = ad.childenrollguid
            LEFT JOIN (
                SELECT
                    childenrollguid,
                    MAX(CASE WHEN YEAR(measurement_taken_date) = %(m1_year)s AND MONTH(measurement_taken_date) = %(m1_month)s THEN CAST(weight_for_age_zscore AS DECIMAL(10,4)) END) AS m1_zscore,
                    MAX(CASE WHEN YEAR(measurement_taken_date) = %(m2_year)s AND MONTH(measurement_taken_date) = %(m2_month)s THEN CAST(weight_for_age_zscore AS DECIMAL(10,4)) END) AS m2_zscore,
                    MAX(CASE WHEN YEAR(measurement_taken_date) = %(m3_year)s AND MONTH(measurement_taken_date) = %(m3_month)s THEN CAST(weight_for_age_zscore AS DECIMAL(10,4)) END) AS m3_zscore,
                    MAX(CASE WHEN YEAR(measurement_taken_date) = %(m4_year)s AND MONTH(measurement_taken_date) = %(m4_month)s THEN CAST(weight_for_age_zscore AS DECIMAL(10,4)) END) AS m4_zscore
                FROM `tabAnthropromatic Data`
                WHERE do_you_have_height_weight = 1
                AND weight_for_age_zscore IS NOT NULL
                AND (
                    (YEAR(measurement_taken_date) = %(m1_year)s AND MONTH(measurement_taken_date) = %(m1_month)s)
                    OR (YEAR(measurement_taken_date) = %(m2_year)s AND MONTH(measurement_taken_date) = %(m2_month)s)
                    OR (YEAR(measurement_taken_date) = %(m3_year)s AND MONTH(measurement_taken_date) = %(m3_month)s)
                    OR (YEAR(measurement_taken_date) = %(m4_year)s AND MONTH(measurement_taken_date) = %(m4_month)s)
                )
                GROUP BY childenrollguid
            ) AS snc_zz ON snc_zz.childenrollguid = ad.childenrollguid
            WHERE {condition_sql}
        """, filters, as_dict=True)

        return data

    except Exception as e:
        frappe.log_error(f"Error in growth_chart_data: {str(e)}")
        frappe.throw("Failed to fetch growth chart data. Please try again later.")



@frappe.whitelist()
def get_child_growth_history(child_name, year=None, month=None):
    try:
        conditions = ["ad.childenrollguid = cee.childenrollguid", "cee.name = %(child_name)s"]
        filters = {"child_name": child_name}
        
        if year:
            conditions.append("YEAR(ad.measurement_taken_date) = %(year)s")
            filters["year"] = int(year)
        if month:
            conditions.append("MONTH(ad.measurement_taken_date) <= %(month)s")
            filters["month"] = int(month)
            
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # FIXED: Calculate age in days properly using child's DOB
        records = frappe.db.sql(f"""
            SELECT
                ad.height, 
                ad.weight, 
                ad.measurement_taken_date, 
                DATEDIFF(ad.measurement_taken_date, cee.child_dob) as age_in_days,
                ad.weight_for_age_zscore, 
                ad.height_for_age_zscore, 
                ad.weight_for_height_zscore,
                ad.age_months as stored_age_months  -- Keep original for reference
            FROM `tabAnthropromatic Data` ad
            INNER JOIN `tabChild Enrollment and Exit` cee ON ad.childenrollguid = cee.childenrollguid
            WHERE {where_clause}
            ORDER BY ad.measurement_taken_date ASC
        """, filters, as_dict=True)
        
        return records
    except Exception as e:
        frappe.log_error(f"Error getting growth history for child {child_name}: {str(e)}")
        return []


@frappe.whitelist()
def get_growth_chart_for_child(child_name, chart_type="weight_for_age", year=None, month=None):
    try:
        try:
            child = frappe.get_doc("Child Enrollment and Exit", child_name)
        except frappe.DoesNotExistError:
            children = frappe.get_all(
                "Child Enrollment and Exit",
                filters={"child_name": child_name},
                fields=["name"],
                limit=1
            )
            if not children:
                frappe.throw(f"Child '{child_name}' not found in Child Enrollment and Exit")
            child = frappe.get_doc("Child Enrollment and Exit", children[0].name)
            
        gender = child.gender_id
        
        # Get appropriate WHO standards based on chart type and gender
        if chart_type == "height_for_age":
            standards = height_for_age_boys() if gender == "1" else height_for_age_girls()
            y_label = "Height (cm)"
            x_label = "Age (Days)"
            status_field = "height_for_age_zscore"
        elif chart_type == "weight_for_age":
            standards = weight_for_age_boys_table() if gender == "1" else weight_for_age_girls_table()
            y_label = "Weight (kg)"
            x_label = "Age (Days)"
            status_field = "weight_for_age_zscore"
        elif chart_type == "weight_for_height":
            standards = weight_to_height_boys() if gender == "1" else weight_to_height_girls()
            y_label = "Weight (kg)"
            x_label = "Height (cm)"
            status_field = "weight_for_height_zscore"
        else:
            frappe.throw("Invalid chart type specified")
        
        # Process standards into coordinate points
        processed_standards = {
            "green_cor": [],  # Normal (SD2)
            "yellow_max": [], # Moderate (SD2neg)
            "red_cor": [],    # Severe (SD3neg)
            "age_in_days": [],
            "value_max": [],
            "value_min": []
        }

        # Process standards data
        if chart_type == "weight_for_height":
            for height_cm, records in standards.items():
                try:
                    for record in records:
                        sd2 = float(record.get("sd2", record.get("green", 0)))
                        sd2neg = float(record.get("sd2neg", record.get("yellow", 0)))
                        sd3neg = float(record.get("sd3neg", record.get("red", 0)))
                        
                        if sd2 > 0 and sd2neg > 0 and sd3neg > 0:
                            height_float = float(height_cm)
                            processed_standards["age_in_days"].append(height_float)
                            processed_standards["value_max"].append(sd2)
                            processed_standards["value_min"].append(sd3neg)
                            
                            processed_standards["green_cor"].append({"x": height_float, "y": sd2})
                            processed_standards["yellow_max"].append({"x": height_float, "y": sd2neg})
                            processed_standards["red_cor"].append({"x": height_float, "y": sd3neg})
                            break
                except (ValueError, AttributeError) as e:
                    frappe.log_error(f"Error processing weight-for-height standards data: {str(e)}")
                    continue
        else:
            for age_days, data in standards.items():
                try:
                    sd2 = float(data.get("sd2", data.get("green", 0)))
                    sd2neg = float(data.get("sd2neg", data.get("yellow", 0)))
                    sd3neg = float(data.get("sd3neg", data.get("red", 0)))
                    
                    if sd2 > 0 and sd2neg > 0 and sd3neg > 0:
                        age_days_float = float(age_days)
                        processed_standards["age_in_days"].append(age_days_float)
                        processed_standards["value_max"].append(sd2)
                        processed_standards["value_min"].append(sd3neg)
                        
                        processed_standards["green_cor"].append({"x": age_days_float, "y": sd2})
                        processed_standards["yellow_max"].append({"x": age_days_float, "y": sd2neg})
                        processed_standards["red_cor"].append({"x": age_days_float, "y": sd3neg})
                    
                except (ValueError, AttributeError) as e:
                    frappe.log_error(f"Error processing standards data: {str(e)}")
                    continue

        # Process child measurements with year/month filtering
        child_measurements = []
        history = get_child_growth_history(child.name, year, month)
        
        # Determine which fields to use based on chart type
        if chart_type == "height_for_age":
            value_field = "height"
            zscore_field = "height_for_age_zscore"
        elif chart_type == "weight_for_age":
            value_field = "weight"
            zscore_field = "weight_for_age_zscore"
        elif chart_type == "weight_for_height":
            value_field = "weight"
            zscore_field = "weight_for_height_zscore"
        
        # FIXED: Process measurements with proper age calculation
        for record in history:
            try:
                if record.get(value_field) and float(record.get(value_field, 0)) > 0:
                    if chart_type == "weight_for_height":
                        if not record.get("height") or float(record.get("height", 0)) <= 0:
                            continue
                        x_value = float(record.get("height", 0))
                    else:
                        # FIXED: Use properly calculated age_in_days instead of stored age_months
                        if record.get("age_in_days") and record.get("age_in_days") > 0:
                            x_value = float(record.get("age_in_days"))
                        else:
                            # Fallback: calculate from dates if age_in_days is not available
                            if record.get("measurement_taken_date") and child.child_dob:
                                age_days = (record.get("measurement_taken_date") - child.child_dob).days
                                x_value = float(age_days)
                            else:
                                continue  # Skip if we can't calculate age

                    zscore = float(record.get(zscore_field, 0)) if record.get(zscore_field) else 0
                    
                    if zscore < -3:
                        status = 1  # Severe
                    elif zscore < -2:
                        status = 2  # Moderate
                    else:
                        status = 3  # Normal
                    
                    child_measurements.append({
                        "x": x_value,
                        "y": float(record.get(value_field, 0)),
                        "date": record.get("measurement_taken_date").strftime("%Y-%m-%d") if record.get("measurement_taken_date") else None,
                        "type": "monitoring",
                        "zscore": zscore,
                        "status": status
                    })
            except (ValueError, AttributeError) as e:
                frappe.log_error(f"Error processing measurement data: {str(e)}")
                continue
        
        # Add enrollment data if available (only if no year/month filter or if enrollment is within filter)
        if chart_type != "weight_for_height":
            try:
                if child.child_dob and child.date_of_enrollment and child.weight:
                    enrollment_age_days = (child.date_of_enrollment - child.child_dob).days
                    if enrollment_age_days > 0 and float(child.weight) > 0:
                        # Check if enrollment should be included based on year/month filter
                        include_enrollment = True
                        if year:
                            if child.date_of_enrollment.year != int(year):
                                include_enrollment = False
                        if month and include_enrollment:
                            if child.date_of_enrollment.month > int(month):
                                include_enrollment = False
                                
                        if include_enrollment:
                                y_value = float(child.weight)  # Default to weight
                                if chart_type == "height_for_age":
                                    if child.height and float(child.height) > 40:  # Only use height if valid
                                        y_value = float(child.height)
                                
                                child_measurements.append({
                                    "x": float(enrollment_age_days),
                                    "y": y_value,
                                    "date": child.date_of_enrollment.strftime("%Y-%m-%d"),
                                    "type": "enrollment",
                                    "zscore": 0,
                                    "status": 3
                                })
            except Exception as e:
                frappe.log_error(f"Error adding enrollment data: {str(e)}")
        
        try:
            if chart_type == "weight_for_height":
                min_x, max_x = 45, 120
                min_y, max_y = 0, 27.2
            else:
                all_x = [m["x"] for m in child_measurements] + [p["x"] for p in processed_standards["green_cor"]]
                all_y = [m["y"] for m in child_measurements] + [p["y"] for p in processed_standards["green_cor"]]
                
                max_x = max(all_x) if all_x else 1820
                max_y = max(all_y) if all_y else (20 if chart_type != "height_for_age" else 120)
                
                min_x = 0
                min_y = 0
                
                max_x = max_x * 1.1 if max_x > 0 else 1820
                max_y = max_y * 1.1 if max_y > 0 else (20 if chart_type != "height_for_age" else 120)

            current_status = {
                "weight_for_age": None,
                "height_for_age": None,
                "weight_for_height": None
            }
            
            if child_measurements:
                last_measurement = child_measurements[-1]
                if chart_type == "weight_for_age":
                    current_status["weight_for_age"] = last_measurement["status"]
                elif chart_type == "height_for_age":
                    current_status["height_for_age"] = last_measurement["status"]
                elif chart_type == "weight_for_height":
                    current_status["weight_for_height"] = last_measurement["status"]
            
            # FIXED: Sort measurements by date to maintain chronological order
            sorted_measurements = sorted(child_measurements, key=lambda x: x["date"] if x["date"] else "")
            
            return {
                "standards": processed_standards,
                "measurements": sorted_measurements,
                "child_info": {
                    "child_id": child.child_id,
                    "child_name": child.child_name,
                    "gender_id": child.gender_id,
                    "creche_id": child.creche_id,
                    "childenrollguid": child.childenrollguid,
                    "current_status": current_status,
                    "dob": child.child_dob.strftime("%Y-%m-%d") if child.child_dob else None
                },
                "chart_meta": {
                    "maxX": max_x,
                    "maxY": max_y,
                    "minX": min_x,
                    "minY": min_y,
                    "chart_type": chart_type,
                    "bottom_label": x_label,
                    "left_label": y_label,
                    "status_mapping": {
                        "1": {"label": "Severe", "color": "#ff0400"},
                        "2": {"label": "Moderate", "color": "#f6c23e"},
                        "3": {"label": "Normal", "color": "#04e80c"}
                    },
                    "fixed_axis": {
                        "x": [45, 60, 80, 100, 120] if chart_type == "weight_for_height" else None,
                        "y": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 27.2] if chart_type == "weight_for_height" else None
                    },
                },
                "success": True
            }
            
        except Exception as e:
            frappe.log_error(f"Error calculating chart boundaries: {str(e)}")
            frappe.throw("Error preparing chart data. Please check the logs for details.")
            
    except Exception as e:
        frappe.log_error(f"Error in get_growth_chart_for_child: {str(e)}", "Growth Chart Error")
        frappe.throw(f"Failed to prepare growth chart data: {str(e)}")



@frappe.whitelist()
def get_monthly_attendance_summary(child_name, year=None, month=None):
    import calendar
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    now = datetime.now()
    is_current_month = False

    # Determine limit_date (end date for query)
    if year and month:
        try:
            year = int(year)
            month = int(month)
            last_day = calendar.monthrange(year, month)[1]
            limit_date = datetime(year, month, last_day)
            
            # Check if this is the current month
            if year == now.year and month == now.month:
                is_current_month = True
                limit_date = now  # Use current date instead of month end
        except ValueError:
            return {"error": "Invalid year/month"}
    else:
        limit_date = now
        is_current_month = True

    # Calculate start_date (exactly 6 months before limit_date)
    start_date = (limit_date.replace(day=1) - relativedelta(months=5))

    # Fetch aggregated data
    data = frappe.db.sql("""
        SELECT 
            YEAR(ca.date_of_attendance) AS y,
            MONTH(ca.date_of_attendance) AS m,
            DAY(LAST_DAY(ca.date_of_attendance)) AS total_days_in_month,
            SUM(CASE WHEN ca.is_shishu_ghar_is_closed_for_the_day = 0 THEN 1 ELSE 0 END) AS creche_opened_days,
            SUM(CASE WHEN cal.attendance = 1 THEN 1 ELSE 0 END) AS present_days
        FROM `tabChild Attendance List` cal
        INNER JOIN `tabChild Attendance` ca ON cal.parent = ca.name
        WHERE cal.child_profile_id = %s
            AND ca.date_of_attendance BETWEEN %s AND %s
        GROUP BY y, m
        ORDER BY y DESC, m DESC
    """, (child_name, start_date.strftime('%Y-%m-%d'), limit_date.strftime('%Y-%m-%d')), as_dict=True)

    # Post-process the data
    for row in data:
        # Use limit_date's day count for the last month in the range
        if row['y'] == limit_date.year and row['m'] == limit_date.month:
            row["total_days"] = limit_date.day
        else:
            row["total_days"] = row["total_days_in_month"]

        row["month"] = f"{calendar.month_abbr[row['m']]}-{row['y']}"
        row["absent_days"] = row["creche_opened_days"] - row["present_days"]
        del row["total_days_in_month"]

    return data











