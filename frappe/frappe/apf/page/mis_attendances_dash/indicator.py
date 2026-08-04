import frappe
import calendar
import json
import hashlib
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ==============================================================================
# HELPER & CACHING UTILITIES
# ==============================================================================

def get_cache_key(api_name, kwargs):
    """Generates a unique MD5 hash for Redis caching based on the exact filters requested."""
    clean_kwargs = {k: v for k, v in kwargs.items() if k not in ("cmd", "_")}
    key_string = json.dumps(clean_kwargs, sort_keys=True, default=str)
    return f"dash_cache_{frappe.session.user}_{api_name}_{hashlib.md5(key_string.encode()).hexdigest()}"

def get_user_geography():
    """Fetches and caches the user's geographic permissions (Row-Level Security)."""
    mapping = frappe.db.sql(
        "SELECT state_id, district_id, block_id, gp_id FROM `tabUser Geography Mapping` WHERE parent = %s",
        frappe.session.user, 
        as_dict=True
    )
    return {
        "state_ids": tuple(str(s["state_id"]) for s in mapping if s.get("state_id")) or ('',),
        "district_ids": tuple(str(s["district_id"]) for s in mapping if s.get("district_id")) or ('',),
        "block_ids": tuple(str(s["block_id"]) for s in mapping if s.get("block_id")) or ('',),
        "gp_ids": tuple(str(s["gp_id"]) for s in mapping if s.get("gp_id")) or ('',)
    }

def append_geography_filters(kwargs, params, conditions, alias=""):
    """Safely appends geography conditions to the SQL query AND attaches the exact variables to params."""
    prefix = f"{alias}." if alias else ""
    user_geo = get_user_geography()

    for key in ["state_id", "district_id", "block_id", "gp_id"]:
        # If the user explicitly filtered by a specific ID
        if kwargs.get(key):
            conditions.append(f"{prefix}{key} = %({key})s")
            params[key] = kwargs.get(key)
        # Otherwise, restrict to their mapped locations (if any)
        else:
            geo_key = f"{key}s"
            if user_geo[geo_key] != ('',):
                conditions.append(f"{prefix}{key} IN %({geo_key})s")
                params[geo_key] = user_geo[geo_key]

# ==============================================================================
# HOUSEHOLD & ENROLLMENT APIs
# ==============================================================================

@frappe.whitelist()
def get_eligible_enrolled_data():
    cache_key = get_cache_key("get_eligible_enrolled_data", frappe.form_dict)
    
    def fetch_data():
        fd = frappe.form_dict
        start_date = datetime(int(fd.get("year", 2024)), int(fd.get("month", 12)), 1)
        dates, labels, eli_parts, enr_parts = [], [], [], []
        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

        for i in range(12):
            target = start_date - relativedelta(months=i)
            date_str = target.strftime("%Y-%m-%d")
            last_day_str = (target + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")
            month_label = f"{month_names[target.month - 1]}-{target.year}"
            
            dates.insert(0, (date_str, month_label))
            labels.insert(0, month_label)
            
            eli_parts.insert(0, f"SUM(CASE WHEN TIMESTAMPDIFF(MONTH, hhc.child_dob, '{date_str}') BETWEEN 6 AND 36 AND '{date_str}' <= CURDATE() THEN 1 ELSE 0 END) AS `{date_str}`")
            enr_parts.insert(0, f"SUM(CASE WHEN cee.is_active = 1 AND cee.date_of_enrollment <= '{last_day_str}' THEN 1 ELSE 0 END) AS `{date_str}`")

        eli_filters, enr_filters, params = ["hhc.is_dob_available = 1"], [], {}
        
        partner_id = fd.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            eli_filters.append("hf.partner_id = %(partner_id)s")
            enr_filters.append("cee.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id
            
        if fd.get("creche_id"):
            eli_filters.append("hf.creche_id = %(creche_id)s")
            enr_filters.append("cee.creche_id = %(creche_id)s")
            params["creche_id"] = fd.get("creche_id")

        append_geography_filters(fd, params, eli_filters, "hf")
        append_geography_filters(fd, params, enr_filters, "cee")

        eli_query = f"SELECT {', '.join(eli_parts)} FROM `tabHousehold Child Form` hhc JOIN `tabHousehold Form` hf ON hf.name = hhc.parent WHERE {' AND '.join(eli_filters)}"
        enr_query = f"SELECT {', '.join(enr_parts)} FROM `tabChild Enrollment and Exit` cee WHERE {' AND '.join(enr_filters) if enr_filters else '1=1'}"

        eli_res = frappe.db.sql(eli_query, params, as_dict=True)
        enr_res = frappe.db.sql(enr_query, params, as_dict=True)

        return {
            "labels": labels,
            "datasets": [
                {"name": "Eligible", "values": [int(v or 0) for v in eli_res[0].values()] if eli_res else [0] * 12},
                {"name": "Enrolled", "values": [int(v or 0) for v in enr_res[0].values()] if enr_res else [0] * 12},
            ]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def get_active_enrolled_data():
    cache_key = get_cache_key("get_active_enrolled_data", frappe.form_dict)

    def fetch_data():
        fd = frappe.form_dict
        start_date = datetime(int(fd.get("year", 2024)), int(fd.get("month", 12)), 1)
        labels, eli_parts, act_parts = [], [], []
        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

        for i in range(12):
            target = start_date - relativedelta(months=i)
            date_str = target.strftime("%Y-%m-%d")
            last_day_str = (target + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")
            month_label = f"{month_names[target.month - 1]}-{target.year}"
            
            labels.insert(0, month_label)
            eli_parts.insert(0, f"SUM(CASE WHEN TIMESTAMPDIFF(MONTH, hhc.child_dob, '{date_str}') BETWEEN 6 AND 36 AND '{date_str}' <= CURDATE() THEN 1 ELSE 0 END) AS `{date_str}`")
            act_parts.insert(0, f"SUM(CASE WHEN cee.is_active = 1 AND cee.date_of_enrollment <= '{last_day_str}' AND (cee.date_of_exit IS NULL OR cee.date_of_exit > '{last_day_str}') THEN 1 ELSE 0 END) AS `{date_str}`")

        eli_filters, enr_filters, params = ["hhc.is_dob_available = 1"], [], {}
        
        partner_id = fd.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            eli_filters.append("hf.partner_id = %(partner_id)s")
            enr_filters.append("cee.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id
            
        if fd.get("creche_id"):
            eli_filters.append("hf.creche_id = %(creche_id)s")
            enr_filters.append("cee.creche_id = %(creche_id)s")
            params["creche_id"] = fd.get("creche_id")

        append_geography_filters(fd, params, eli_filters, "hf")
        append_geography_filters(fd, params, enr_filters, "cee")

        eli_query = f"SELECT {', '.join(eli_parts)} FROM `tabHousehold Child Form` hhc JOIN `tabHousehold Form` hf ON hf.name = hhc.parent WHERE {' AND '.join(eli_filters)}"
        act_query = f"SELECT {', '.join(act_parts)} FROM `tabChild Enrollment and Exit` cee WHERE {' AND '.join(enr_filters) if enr_filters else '1=1'}"

        eli_res = frappe.db.sql(eli_query, params, as_dict=True)
        act_res = frappe.db.sql(act_query, params, as_dict=True)

        return {
            "labels": labels,
            "datasets": [
                {"name": "Eligible", "values": [int(v or 0) for v in eli_res[0].values()] if eli_res else [0] * 12},
                {"name": "Active Enrolled", "values": [int(v or 0) for v in act_res[0].values()] if act_res else [0] * 12},
            ]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def get_exit_childrens():
    cache_key = get_cache_key("get_exit_childrens", frappe.form_dict)

    def fetch_data():
        fd = frappe.form_dict
        start_date = datetime(int(fd.get("year", 2024)), int(fd.get("month", 12)), 1)
        labels, act_parts, ext_parts = [], [], []
        month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

        for i in range(12):
            target = start_date - relativedelta(months=i)
            start_str = target.strftime("%Y-%m-01")
            end_str = (target + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")
            month_label = f"{month_names[target.month - 1]}-{target.year}"
            
            labels.insert(0, month_label)
            act_parts.insert(0, f"SUM(CASE WHEN cees.date_of_enrollment BETWEEN '{start_str}' AND '{end_str}' THEN 1 ELSE 0 END) AS `{start_str}`")
            ext_parts.insert(0, f"SUM(CASE WHEN cee.date_of_exit BETWEEN '{start_str}' AND '{end_str}' THEN 1 ELSE 0 END) AS `{start_str}`")

        active_filters, exited_filters, params = [], [], {}
        
        partner_id = fd.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            active_filters.append("cees.partner_id = %(partner_id)s")
            exited_filters.append("cee.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id
            
        if fd.get("creche_id"):
            active_filters.append("cees.creche_id = %(creche_id)s")
            exited_filters.append("cee.creche_id = %(creche_id)s")
            params["creche_id"] = fd.get("creche_id")

        append_geography_filters(fd, params, active_filters, "cees")
        append_geography_filters(fd, params, exited_filters, "cee")

        act_query = f"SELECT {', '.join(act_parts)} FROM `tabChild Enrollment and Exit` cees WHERE {' AND '.join(active_filters) if active_filters else '1=1'}"
        ext_query = f"SELECT {', '.join(ext_parts)} FROM `tabChild Enrollment and Exit` cee WHERE {' AND '.join(exited_filters) if exited_filters else '1=1'}"

        act_res = frappe.db.sql(act_query, params, as_dict=True)
        ext_res = frappe.db.sql(ext_query, params, as_dict=True)

        return {
            "labels": labels,
            "datasets": [
                {"name": "Current Enrolled", "values": [int(v or 0) for v in act_res[0].values()] if act_res else [0] * 12},
                {"name": "Current Exited", "values": [int(v or 0) for v in ext_res[0].values()] if ext_res else [0] * 12},
            ]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def get_education_level_mother(**kwargs):
    cache_key = get_cache_key("get_education_level_mother", kwargs)

    def fetch_data():
        year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
        if not year or not month: 
            return {"labels": [], "datasets": []}
        
        end_date = date(year, month, 1) + relativedelta(months=1) - relativedelta(days=1)
        conditions, params = [], {"end_date": end_date}
        
        partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            conditions.append("cex.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id
            
        if kwargs.get("creche_id"):
            conditions.append("cex.creche_id = %(creche_id)s")
            params["creche_id"] = kwargs.get("creche_id")
            
        append_geography_filters(kwargs, params, conditions, "cp")
                
        if kwargs.get("c_status"):
            conditions.append("cr.creche_status_id = %(c_status)s")
            params["c_status"] = kwargs.get("c_status")
            
        if kwargs.get("phases"):
            phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
            if phases:
                conditions.append("cr.phase IN %(phases)s")
                params["phases"] = phases

        if kwargs.get("cstart_date") and kwargs.get("cend_date"):
            conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
            params.update({"cstart_date": kwargs.get("cstart_date"), "cend_date": kwargs.get("cend_date")})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"""
            SELECT IFNULL(tel.level,'Not Available') AS EducationLevelName, COUNT(*) AS Count
            FROM `tabChild Profile` cp 
            INNER JOIN `tabChild Enrollment and Exit` cex ON cex.hhcguid = cp.chhguid
            LEFT JOIN `tabCreche` cr ON cr.name = cex.creche_id
            LEFT JOIN `tabEducation Level` tel ON cp.education_level_of_parentscaregiver = tel.name
            WHERE {where_clause} AND (cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)
            GROUP BY cp.education_level_of_parentscaregiver, tel.level
        """
        
        data = frappe.db.sql(query, params, as_dict=True)
        education_levels = ['Not Literate', 'Class 5', 'Class 8', 'Class 10', 'Intermediate', 'Diploma', 'Graduate', 'PG and above', 'Not Available']
        counts_map = {row['EducationLevelName']: row['Count'] for row in data}
        
        return {
            "labels": education_levels, 
            "datasets": [{"values": [counts_map.get(lvl, 0) for lvl in education_levels]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def get_specially_abled_children(**kwargs):
    cache_key = get_cache_key("get_specially_abled_children", kwargs)

    def fetch_data():
        year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
        year_month = f"{year}-{month:02d}-30" if year and month else None
        
        conditions, params = ["cees.is_active = 1"], {}
        
        if year_month:
            conditions.append("cees.date_of_enrollment <= %(year_month)s")
            params["year_month"] = year_month
            
        partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            conditions.append("cees.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id
            
        if kwargs.get("creche_id"):
            conditions.append("cees.creche_id = %(creche_id)s")
            params["creche_id"] = kwargs.get("creche_id")
            
        append_geography_filters(kwargs, params, conditions, "cp")

        query = f""" 
            SELECT COUNT(DISTINCT cees.hhcguid) AS `enrolled_children`, 
                   COUNT(DISTINCT CASE WHEN cp.child_specially_abled = 1 THEN cp.chhguid END) AS `specially_abled`  
            FROM `tabChild Enrollment and Exit` cees
            JOIN `tabChild Profile` cp ON cees.hhcguid = cp.chhguid
            WHERE {" AND ".join(conditions)}
        """

        data = frappe.db.sql(query, params, as_dict=True)
        return {
            "labels": ["Enrolled Children", "Specially Abled"],
            "datasets": [{
                "name": "Children Count", 
                "values": [
                    data[0].get("enrolled_children", 0) if data else 0, 
                    data[0].get("specially_abled", 0) if data else 0
                ]
            }]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def age_in_months(**kwargs):
    cache_key = get_cache_key("age_in_months", kwargs)

    def fetch_data():
        year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
        year_month = f"{year}-{month:02d}-01" if year and month else None
        
        conditions, params = ["cee.is_exited = 0"], {}
        
        if year_month:
            conditions.append("cee.creation <= %(year_month)s")
            params["year_month"] = year_month

        partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            conditions.append("cee.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id
            
        if kwargs.get("creche_id"):
            conditions.append("cee.creche_id = %(creche_id)s")
            params["creche_id"] = kwargs.get("creche_id")
            
        append_geography_filters(kwargs, params, conditions, "cee")

        query = f"""
            SELECT 
                COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 6 AND 9 THEN 1 END) AS `6-9`,
                COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 10 AND 12 THEN 1 END) AS `9-12`,
                COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 13 AND 24 THEN 1 END) AS `12-24`,
                COUNT(CASE WHEN cee.age_at_enrollment_in_months BETWEEN 25 AND 36 THEN 1 END) AS `24-36`
            FROM `tabChild Enrollment and Exit` cee
            WHERE {" AND ".join(conditions)}
        """
        
        data = frappe.db.sql(query, params, as_dict=True)
        return {
            "labels": ["6-9 months", "9-12 months", "12-24 months", "24-36 months"],
            "datasets": [{
                "values": [
                    data[0]["6-9"], 
                    data[0]["9-12"], 
                    data[0]["12-24"], 
                    data[0]["24-36"]
                ] if data else [0] * 4
            }]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

# ==============================================================================
# DEMOGRAPHIC APIs
# ==============================================================================

def generic_household_aggregator(kwargs, select_clause, group_by_clause, order_clause=""):
    year, month = kwargs.get("year"), kwargs.get("month")
    year_month = f"{int(year)}-{int(month):02d}-01" if year and month else None
    
    conditions, params = [], {}
    
    if year_month:
        conditions.append("hh.creation <= %(year_month)s")
        params["year_month"] = year_month
        
    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("hh.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id
        
    append_geography_filters(kwargs, params, conditions, "hh")
            
    where = " AND ".join(conditions) if conditions else "1=1"
    query = f"SELECT {select_clause} FROM `tabHousehold Form` hh WHERE {where} {group_by_clause} {order_clause}"
    return frappe.db.sql(query, params, as_dict=True)


@frappe.whitelist()
def get_occupation_data(**kwargs):
    cache_key = get_cache_key("get_occupation_data", kwargs)
    
    def fetch_data():
        data = generic_household_aggregator(
            kwargs, 
            "po.primary_occupation, COUNT(hh.name) AS count", 
            "JOIN `tabPrimary Occupation` po ON hh.primary_occupation_id = po.name GROUP BY po.primary_occupation", 
            "ORDER BY LENGTH(po.primary_occupation) ASC"
        )
        return {
            "labels": [row["primary_occupation"] for row in data], 
            "datasets": [{"name": "values", "values": [row["count"] for row in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def get_caste_data(**kwargs):
    cache_key = get_cache_key("get_caste_data", kwargs)
    
    def fetch_data():
        select_clause = "CASE WHEN hh.social_category_id = 1 THEN 'General' WHEN hh.social_category_id = 2 THEN 'OBC' WHEN hh.social_category_id = 3 THEN 'SC' WHEN hh.social_category_id = 4 THEN 'ST' WHEN hh.social_category_id = 5 THEN 'Other' ELSE 'Not Available' END AS Caste, COUNT(hh.name) AS Count"
        data = generic_household_aggregator(kwargs, select_clause, "GROUP BY Caste")
        
        caste_labels = ['General', 'OBC', 'SC', 'ST', 'Other', 'Not Available']
        caste_counts = {label: 0 for label in caste_labels}
        for row in data:
            caste_counts[row["Caste"]] = row["Count"]
            
        return {"labels": caste_labels, "datasets": [{"values": [caste_counts[l] for l in caste_labels]}]}
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def get_religion_data(**kwargs):
    cache_key = get_cache_key("get_religion_data", kwargs)
    
    def fetch_data():
        select_clause = "COUNT(CASE WHEN hh.religion = 1 THEN hh.name END) AS Hindu, COUNT(CASE WHEN hh.religion = 2 THEN hh.name END) AS Muslim, COUNT(CASE WHEN hh.religion = 3 THEN hh.name END) AS Christian, COUNT(CASE WHEN hh.religion = 4 THEN hh.name END) AS Buddhism, COUNT(CASE WHEN hh.religion = 5 THEN hh.name END) AS Sikhism, COUNT(CASE WHEN hh.religion = 6 THEN hh.name END) AS Jainism, COUNT(CASE WHEN hh.religion = 7 THEN hh.name END) AS `Any Other`, COUNT(CASE WHEN hh.religion IS NULL THEN hh.name END) AS `Not Available`"
        data = generic_household_aggregator(kwargs, select_clause, "")
        
        religion_labels = ['Hindu', 'Muslim', 'Christian', 'Buddhism', 'Sikhism', 'Jainism', 'Any Other', 'Not Available']
        return {"labels": religion_labels, "datasets": [{"values": [data[0][l] for l in religion_labels] if data else [0] * 8}]}
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def hh_migration_data(**kwargs):
    cache_key = get_cache_key("hh_migration_data", kwargs)
    
    def fetch_data():
        select_clause = "COUNT(CASE WHEN hh.is_anyone_of_your_family_a_migrant_worker = 1 AND hh.no_of_months_the_migrants_were_away_last_year = 1 THEN hh.name END) AS HHMGE6M, COUNT(CASE WHEN hh.is_anyone_of_your_family_a_migrant_worker = 1 AND hh.no_of_months_the_migrants_were_away_last_year = 2 THEN hh.name END) AS HHML6M"
        data = generic_household_aggregator(kwargs, select_clause, "")
        
        return {
            "labels": ["HH >= 6 months", "HH < 6 months"], 
            "datasets": [{"name": "Migration Data", "values": [data[0].get("HHMGE6M", 0), data[0].get("HHML6M", 0)] if data else [0, 0]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

# ==============================================================================
# ATTENDANCE APIs & BAR CHART APIs WITH DRILL-DOWN LOGIC SUPPORT
# ==============================================================================

@frappe.whitelist()
def get_reg_HH(**kwargs):
    cache_key = get_cache_key("get_reg_HH", kwargs)
    
    def fetch_data():
        year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
        if not year or not month: 
            return {"labels": [], "datasets": []}

        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
        
        conditions = ["(hh.creation BETWEEN %(start_date)s AND %(end_date)s)"]
        params = {"start_date": start_date, "end_date": end_date}
        
        partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
        if partner_id:
            conditions.append("cr.partner_id = %(partner_id)s")
            params["partner_id"] = partner_id

        append_geography_filters(kwargs, params, conditions, "cr")
        
        if kwargs.get("creche_id"):
            conditions.append("hh.creche_id = %(creche_id)s")
            params["creche_id"] = kwargs.get("creche_id")

        join_clauses = ["INNER JOIN `tabCreche` cr ON cr.name = hh.creche_id"]
        
        level = kwargs.get("level")
        dl_group = kwargs.get("drilldown_group")
        dl_level = kwargs.get("drilldown_level")
        
        dimension_map = {
            1: ("p", "`tabPartner`", "partner_id", "partner_name"),
            2: ("s", "`tabState`", "state_id", "state_name"),
            3: ("d", "`tabDistrict`", "district_id", "district_name"),
            4: ("b", "`tabBlock`", "block_id", "block_name"),
            5: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
            6: ("cr", "`tabCreche`", "name", "creche_name")
        }

        tables_to_join = set()
        group_name_field = "'All Data'"
        is_month_wise = False

        if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
            prefix, table, fk, field = dimension_map[int(dl_level)]
            tables_to_join.add(int(dl_level))
            conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
            params["drilldown_group"] = dl_group
            level = None
            is_month_wise = True

        if level and str(level).isdigit() and int(level) in dimension_map:
            prefix, table, fk, field = dimension_map[int(level)]
            tables_to_join.add(int(level))
            group_name_field = f"{prefix}.{field}"
        elif not level:
            is_month_wise = True

        for tbl_id in tables_to_join:
            if tbl_id != 6:
                prefix, table, fk, field = dimension_map[tbl_id]
                join_clauses.append(f"INNER JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

        if not is_month_wise:
            query = f"""
                SELECT {group_name_field} AS group_name, COUNT(*) AS count
                FROM `tabHousehold Form` hh 
                {" ".join(join_clauses)}
                WHERE {" AND ".join(conditions)} 
                GROUP BY {group_name_field} 
                ORDER BY group_name
            """
            data = frappe.db.sql(query, params, as_dict=True)
            return {
                "labels": [str(r.get("group_name", "Unknown")) for r in data], 
                "datasets": [{
                    "name": start_date.strftime("%b-%Y").upper(), 
                    "values": [int(r.get("count", 0)) for r in data]
                }]
            }
            
        else:
            duration = kwargs.get("duration", "12_months")
            offset_map = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}
            offset = offset_map.get(duration, 11)
            
            start_date_dyn = end_date - relativedelta(months=offset)
            params["start_date"] = start_date_dyn
            
            months_select = []
            for i in range(offset + 1):
                m_date = start_date_dyn + relativedelta(months=i)
                m_start = m_date.strftime("%Y-%m-01")
                m_end = (m_date + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")
                month_label = m_date.strftime('%b-%Y').upper()
                months_select.append(f"SUM(CASE WHEN hh.creation BETWEEN '{m_start}' AND '{m_end}' THEN 1 ELSE 0 END) AS `{month_label}`")

            query = f"""
                SELECT {group_name_field} AS group_name, {", ".join(months_select)}
                FROM `tabHousehold Form` hh 
                {" ".join(join_clauses)}
                WHERE {" AND ".join(conditions)} 
                GROUP BY {group_name_field}
            """
            data = frappe.db.sql(query, params, as_dict=True)
            labels = [(start_date_dyn + relativedelta(months=i)).strftime("%b-%Y").upper() for i in range(offset + 1)]
            
            return {
                "labels": labels, 
                "datasets": [{
                    "name": "Registered Households", 
                    "values": [int(data[0].get(l, 0) or 0) for l in labels] if data else [0] * len(labels)
                }]
            }
            
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


def build_attendance_query(kwargs, select_expression, extra_joins=""):
    """
    A highly optimized query builder. It ONLY joins tables that are absolutely
    necessary based on the requested 'level' or 'drilldown', preventing massive Cartesian products.
    """
    year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
    if not year or not month: 
        frappe.throw("Year and month are required")

    last_day = calendar.monthrange(year, month)[1]
    end_date_ref = date(year, month, last_day)
    
    offset_map = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}
    duration = kwargs.get("duration", "12_months")
    start_date = date(year, month, 1) - relativedelta(months=offset_map.get(duration, 11))

    params = {"start_date": start_date, "end_date": end_date_ref}
    conditions = ["ca.is_shishu_ghar_is_closed_for_the_day = 0", "ca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s"]
    
    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("ca.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id

    append_geography_filters(kwargs, params, conditions, "ca")

    if kwargs.get("creche_id"):
        conditions.append("ca.creche_id = %(creche_id)s")
        params["creche_id"] = kwargs.get("creche_id")
        
    c_status_val = kwargs.get("c_status") or kwargs.get("creche_status_id")
    if c_status_val:
        conditions.append("cr.creche_status_id = %(creche_status)s")
        params["creche_status"] = c_status_val
            
    if kwargs.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = kwargs.get("supervisor_id")

    if kwargs.get("phases"):
        phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params["phases"] = phases

    conditions.append("(cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)")
    if kwargs.get("cstart_date") and kwargs.get("cend_date"):
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
        params.update({"cstart_date": kwargs.get("cstart_date"), "cend_date": kwargs.get("cend_date")})

    join_clauses = [
        "INNER JOIN `tabChild Attendance List` cal ON cal.parent = ca.name",
        "INNER JOIN `tabCreche` cr ON cr.name = ca.creche_id"
    ]
    
    child_age = kwargs.get("child_age")
    if kwargs.get("gender") or child_age:
        join_clauses.append("INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = cal.childenrolledguid")
        if kwargs.get("gender"):
            conditions.append("cee.gender_id = %(gender)s")
            params["gender"] = kwargs.get("gender")
            
        if child_age == "1_year": 
            conditions.append("DATEDIFF(%(end_date)s, cee.child_dob) <= 365")
        elif child_age == "1_2_year": 
            conditions.append("DATEDIFF(%(end_date)s, cee.child_dob) BETWEEN 365 AND 730")
        elif child_age == "2_3_year": 
            conditions.append("DATEDIFF(%(end_date)s, cee.child_dob) BETWEEN 731 AND 1095")

    if extra_joins: 
        join_clauses.append(extra_joins)

    level = kwargs.get("level")
    dl_level = kwargs.get("drilldown_level")
    dl_group = kwargs.get("drilldown_group")
    
    group_name_field = "DATE_FORMAT(ca.date_of_attendance, '%%b-%%Y')"
    order_clause = "ORDER BY MIN(ca.date_of_attendance)"
    
    dimension_map = {
        1: ("p", "`tabPartner`", "partner_id", "partner_name"),
        2: ("s", "`tabState`", "state_id", "state_name"),
        3: ("d", "`tabDistrict`", "district_id", "district_name"),
        4: ("b", "`tabBlock`", "block_id", "block_name"),
        5: ("u", "`tabUser`", "supervisor_id", "full_name"),
        6: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
        7: ("cr", "`tabCreche`", "name", "creche_name")
    }

    tables_to_join = set()

    if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(dl_level)]
        tables_to_join.add(int(dl_level))
        conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
        params["drilldown_group"] = dl_group
        level = None 

    if level and str(level).isdigit() and int(level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(level)]
        tables_to_join.add(int(level))
        group_name_field = f"{prefix}.{field}"
        order_clause = "ORDER BY group_name"

    for tbl_id in tables_to_join:
        prefix, table, fk, field = dimension_map[tbl_id]
        if tbl_id == 5:
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.email = cr.{fk}")
        elif tbl_id != 7:
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

    query = f"""
        SELECT {group_name_field} AS group_name, {select_expression} AS value
        FROM `tabChild Attendance` ca
        {" ".join(join_clauses)}
        WHERE {" AND ".join(conditions)}
        GROUP BY {group_name_field}
        {order_clause}
    """
    return frappe.db.sql(query, params, as_dict=True)



def build_child_band_query(kwargs, band_condition):
    year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
    last_day = calendar.monthrange(year, month)[1]
    end_date_ref = date(year, month, last_day)
    
    is_month_wise = False
    level = kwargs.get("level")
    dl_level = kwargs.get("drilldown_level")
    dl_group = kwargs.get("drilldown_group")
    
    if dl_group and dl_level and str(dl_level).isdigit():
        is_month_wise = True
        level = None
    elif not level:
        is_month_wise = True
        
    offset_map = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}
    duration = kwargs.get("duration", "12_months")
    
    if is_month_wise:
        start_date = date(year, month, 1) - relativedelta(months=offset_map.get(duration, 11))
    else:
        start_date = date(year, month, 1)

    params = {"start_date": start_date, "end_date": end_date_ref}
    conditions = [
        "ca.is_shishu_ghar_is_closed_for_the_day = 0", 
        "ca.date_of_attendance BETWEEN %(start_date)s AND %(end_date)s",
        "cee.date_of_enrollment <= %(end_date)s",
        "(cee.date_of_exit IS NULL OR cee.date_of_exit >= %(start_date)s)"
    ]
    
    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("ca.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id

    append_geography_filters(kwargs, params, conditions, "ca")

    if kwargs.get("creche_id"):
        conditions.append("ca.creche_id = %(creche_id)s")
        params["creche_id"] = kwargs.get("creche_id")
        
    c_status_val = kwargs.get("c_status") or kwargs.get("creche_status_id")
    if c_status_val:
        conditions.append("cr.creche_status_id = %(creche_status)s")
        params["creche_status"] = c_status_val
        
    if kwargs.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = kwargs.get("supervisor_id")
        
    if kwargs.get("phases"):
        phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params["phases"] = phases

    conditions.append("(cr.creche_opening_date IS NULL OR cr.creche_opening_date <= %(end_date)s)")
    if kwargs.get("cstart_date") and kwargs.get("cend_date"):
        conditions.append("cr.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s")
        params.update({"cstart_date": kwargs.get("cstart_date"), "cend_date": kwargs.get("cend_date")})

    join_clauses = [
        "INNER JOIN `tabChild Attendance List` cal ON cal.parent = ca.name",
        "INNER JOIN `tabCreche` cr ON cr.name = ca.creche_id",
        "INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = cal.childenrolledguid"
    ]
    
    child_age = kwargs.get("child_age")
    if kwargs.get("gender"):
        conditions.append("cee.gender_id = %(gender)s")
        params["gender"] = kwargs.get("gender")
    if child_age == "1_year": 
        conditions.append("DATEDIFF(%(end_date)s, cee.child_dob) <= 365")
    elif child_age == "1_2_year": 
        conditions.append("DATEDIFF(%(end_date)s, cee.child_dob) BETWEEN 365 AND 730")
    elif child_age == "2_3_year": 
        conditions.append("DATEDIFF(%(end_date)s, cee.child_dob) BETWEEN 731 AND 1095")

    dimension_map = {
        1: ("p", "`tabPartner`", "partner_id", "partner_name"),
        2: ("s", "`tabState`", "state_id", "state_name"),
        3: ("d", "`tabDistrict`", "district_id", "district_name"),
        4: ("b", "`tabBlock`", "block_id", "block_name"),
        5: ("u", "`tabUser`", "supervisor_id", "full_name"),
        6: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
        7: ("cr", "`tabCreche`", "name", "creche_name")
    }

    tables_to_join = set()
    group_name_field = "DATE_FORMAT(ca.date_of_attendance, '%%b-%%Y')"
    
    # [FIX]: Changed to use the exposed sort_date from the subquery
    order_clause = "ORDER BY MIN(sort_date)"

    if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(dl_level)]
        tables_to_join.add(int(dl_level))
        conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
        params["drilldown_group"] = dl_group

    if level and str(level).isdigit() and int(level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(level)]
        tables_to_join.add(int(level))
        group_name_field = f"{prefix}.{field}"
        order_clause = "ORDER BY group_name"

    for tbl_id in tables_to_join:
        prefix, table, fk, field = dimension_map[tbl_id]
        if tbl_id == 5:
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.email = cr.{fk}")
        elif tbl_id != 7:
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

    # [FIX]: Added MIN(ca.date_of_attendance) AS sort_date inside the subquery
    query = f"""
        SELECT group_name, COUNT(childenrolledguid) AS value
        FROM (
            SELECT {group_name_field} AS group_name, 
                   cal.childenrolledguid, 
                   SUM(cal.attendance) AS days_attended, 
                   COUNT(ca.name) AS eligible_days,
                   MIN(ca.date_of_attendance) AS sort_date
            FROM `tabChild Attendance` ca
            {" ".join(join_clauses)}
            WHERE {" AND ".join(conditions)}
            GROUP BY {group_name_field}, cal.childenrolledguid
        ) AS child_stats
        WHERE eligible_days > 0 AND {band_condition}
        GROUP BY group_name
        {order_clause}
    """
    
    data = frappe.db.sql(query, params, as_dict=True)

    if is_month_wise:
            offset = offset_map.get(duration, 11)
            labels = [(start_date + relativedelta(months=i)).strftime("%b-%Y").upper() for i in range(offset + 1)]
            # FIX: Added .upper() so 'Feb-2026' from DB becomes 'FEB-2026' and matches perfectly
            val_map = {str(r.get("group_name")).upper(): int(r.get("value") or 0) for r in data}
            return [{"group_name": l, "value": val_map.get(l, 0)} for l in labels]

    return data




@frappe.whitelist()
def avg_daily_attendance(**kwargs):
    cache_key = get_cache_key("avg_daily_attendance", frappe.form_dict)
    
    def fetch_data():
        select_expr = "CASE WHEN COUNT(DISTINCT ca.name) = 0 THEN 0 ELSE ROUND(SUM(cal.attendance) / COUNT(DISTINCT ca.name), 2) END"
        data = build_attendance_query(kwargs, select_expr)
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "Avg. Daily Attendance", "values": [float(r.get("value") or 0.0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def attendance_percentage(**kwargs):
    cache_key = get_cache_key("attendance_percentage", frappe.form_dict)
    
    def fetch_data():
        # Using the exact logic from your report:
        # COALESCE(ROUND(( SUM(attended) * 100.0 / NULLIF( SUM(eligible_days), 0)), 2), 0)
        select_expr = "COALESCE(ROUND((SUM(cal.attendance) * 100.0 / NULLIF(COUNT(cal.name), 0)), 2), 0)"
        
        data = build_attendance_query(kwargs, select_expr)
        
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [
                {
                    "name": "Attendance Percentage", 
                    # This formats the result exactly as requested: "48.21%"
                    "values": [f"{float(r.get('value') or 0.0):.2f}%" for r in data]
                }
            ]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)



@frappe.whitelist()
def full_attendance(**kwargs):
    cache_key = get_cache_key("full_attendance", frappe.form_dict)
    
    def fetch_data():
        data = build_child_band_query(kwargs, "days_attended = eligible_days")
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "100% Attendance Children", "values": [int(r.get("value") or 0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def zero_attendance(**kwargs):
    cache_key = get_cache_key("zero_attendance", frappe.form_dict)
    
    def fetch_data():
        data = build_child_band_query(kwargs, "days_attended = 0")
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "Zero Attendance Children", "values": [int(r.get("value") or 0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def seventy_attendance(**kwargs):
    cache_key = get_cache_key("seventy_attendance", frappe.form_dict)
    
    def fetch_data():
        data = build_child_band_query(kwargs, "(days_attended * 100.0 / eligible_days) >= 70")
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "Regular Children (>= 70%)", "values": [int(r.get("value") or 0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def fivety_attendance(**kwargs):
    cache_key = get_cache_key("fivety_attendance", frappe.form_dict)
    
    def fetch_data():
        data = build_child_band_query(kwargs, "(days_attended * 100.0 / eligible_days) <= 50")
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "<= 50% Attendance Children", "values": [int(r.get("value") or 0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def avg_suw_attendance_percent(**kwargs):
    cache_key = get_cache_key("avg_suw_attendance_percent", frappe.form_dict)
    
    def fetch_data():
        extra_joins = "INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = cal.childenrolledguid INNER JOIN `tabAnthropromatic Data` ad ON ad.childenrollguid = cal.childenrolledguid AND ad.weight_for_age = 1"
        select_expr = "ROUND((COUNT(CASE WHEN cal.attendance = 1 THEN 1 END) / NULLIF(COUNT(ad.name), 0)) * 100, 2)"
        data = build_attendance_query(kwargs, select_expr, extra_joins)
        
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "Avg. Attendance of SUW Children", "values": [float(r.get("value") or 0.0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


@frappe.whitelist()
def avg_sam_attendance_percent(**kwargs):
    cache_key = get_cache_key("avg_sam_attendance_percent", frappe.form_dict)
    
    def fetch_data():
        extra_joins = "INNER JOIN `tabChild Enrollment and Exit` cee ON cee.childenrollguid = cal.childenrolledguid INNER JOIN `tabAnthropromatic Data` ad ON ad.childenrollguid = cal.childenrolledguid AND ad.weight_for_height = 1"
        select_expr = "ROUND((SUM(CASE WHEN cal.attendance = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(ad.name), 0)) * 100, 2)"
        data = build_attendance_query(kwargs, select_expr, extra_joins)
        
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data], 
            "datasets": [{"name": "Avg. Attendance of SAM Children", "values": [float(r.get("value") or 0.0) for r in data]}]
        }
        
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)



# -----------------------------------------------------
# Enrollment APIS


import frappe
from datetime import date
import calendar
from dateutil.relativedelta import relativedelta


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_cache_key(endpoint, form_dict):
    import hashlib, json
    payload = json.dumps({k: str(v) for k, v in sorted(form_dict.items())}, sort_keys=True)
    return f"{endpoint}_{hashlib.md5(payload.encode()).hexdigest()}"


def _date_range(kwargs):
    """Return (start_date, end_date, year, month) from kwargs."""
    y = int(kwargs.get("year",  date.today().year))
    m = int(kwargs.get("month", date.today().month))
    return date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1]), y, m


OFFSET_MAP = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}

# Dimension map: level → (alias, table, fk_on_creche, display_field)
DIM_MAP = {
    1: ("p",  "`tabPartner`",        "partner_id",    "partner_name"),
    2: ("s",  "`tabState`",          "state_id",      "state_name"),
    3: ("d",  "`tabDistrict`",       "district_id",   "district_name"),
    4: ("b",  "`tabBlock`",          "block_id",      "block_name"),
    5: ("u",  "`tabUser`",           "supervisor_id", "full_name"),
    6: ("g",  "`tabGram Panchayat`", "gp_id",         "gp_name"),
    7: ("cr", "`tabCreche`",         "name",          "creche_name"),
}


def _geo_filters(kwargs, params, conds, a="cr"):
    """
    Append user-geography mapping restrictions + any explicit geography filters.
    Mirrors the logic in apply_user_geography_filters / apply_other_filters from
    the report file.
    """
    rows = frappe.db.sql(
        """SELECT state_id, district_id, block_id, gp_id
           FROM `tabState` ts
           JOIN `tabUser Geography Mapping` ugm ON ugm.state_id = ts.name
           WHERE ugm.parent = %s""",
        (frappe.session.user,), as_dict=True
    )

    def _ids(col):
        return ",".join(str(r[col]) for r in rows if r.get(col))

    geo_cols = [
        ("state_id",    "state"),
        ("district_id", "district"),
        ("block_id",    "block"),
        ("gp_id",       "gp"),
    ]
    for col, kw in geo_cols:
        val = _ids(col)
        # Fallback to user-mapped geography when no explicit filter provided
        if not kwargs.get(kw) and val:
            conds.append(f"FIND_IN_SET({a}.{col}, %({col}_list)s)")
            params[f"{col}_list"] = val
        # Explicit geography filter overrides mapping
        if kwargs.get(kw):
            conds.append(f"{a}.{col} = %({kw})s")
            params[kw] = kwargs[kw]


def _common_creche_filters(kwargs, params, conds, a="cr"):
    """
    Append partner, creche, supervisor, phases, creche-age, and
    creche opening-date filters. Mirrors apply_other_filters /
    apply_creche_opening_filters from the report file.
    """
    # Partner (resolved from user profile when not passed)
    pid = kwargs.get("partner_id") or frappe.db.get_value(
        "User", frappe.session.user, "partner"
    )
    if pid:
        conds.append(f"{a}.partner_id = %(partner_id)s")
        params["partner_id"] = pid

    if kwargs.get("creche_id"):
        conds.append(f"{a}.name = %(creche_id)s")
        params["creche_id"] = kwargs["creche_id"]

    if kwargs.get("supervisor_id"):
        conds.append(f"{a}.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = kwargs["supervisor_id"]

    if kwargs.get("creche_status_id"):
        conds.append(f"{a}.creche_status_id = %(creche_status_id)s")
        params["creche_status_id"] = kwargs["creche_status_id"]

    if kwargs.get("phases"):
        phases = tuple(
            p.strip() for p in kwargs["phases"].split(",") if p.strip().isdigit()
        )
        if phases:
            conds.append(f"{a}.phase IN %(phases)s")
            params["phases"] = phases

    # Only include creches that had opened by end_date
    conds.append(
        f"({a}.creche_opening_date IS NULL OR {a}.creche_opening_date <= %(end_date)s)"
    )

    # Optional creche-opening date range filter
    if kwargs.get("cstart_date") and kwargs.get("cend_date"):
        conds.append(
            f"{a}.creche_opening_date BETWEEN %(cstart_date)s AND %(cend_date)s"
        )
        params.update({
            "cstart_date": kwargs["cstart_date"],
            "cend_date":   kwargs["cend_date"],
        })


def _add_dim_join(joins_list, lvl):
    """Append the correct LEFT JOIN clause for a DIM_MAP level."""
    pre, tbl, fk, fld = DIM_MAP[lvl]
    if lvl == 5:                            # User joined by email
        joins_list.append(f"LEFT JOIN {tbl} {pre} ON {pre}.email = cr.{fk}")
    elif lvl != 7:                          # tabCreche is already the base
        joins_list.append(f"LEFT JOIN {tbl} {pre} ON {pre}.name = cr.{fk}")


def _resolve_dim(kwargs, conds, params, sort_date_expr):
    """
    Decide GROUP-BY dimension and extra JOINs.

    Returns (group_field_sql, extra_joins_sql, order_clause, is_month_wise).
    Mirrors the drilldown / level logic in build_child_band_query.
    """
    level    = kwargs.get("level")
    dl_level = kwargs.get("drilldown_level")
    dl_group = kwargs.get("drilldown_group")

    is_month_wise = (
        (dl_group and dl_level and str(dl_level).isdigit()) or not level
    )

    extra_joins  = []
    grp_field    = f"DATE_FORMAT({sort_date_expr}, '%%b-%%Y')"
    order_clause = f"ORDER BY MIN({sort_date_expr})"

    # Drilldown filter: restrict to a specific group, then show month-wise
    if (
        dl_group and dl_level and str(dl_level).isdigit()
        and int(dl_level) in DIM_MAP
    ):
        lvl = int(dl_level)
        pre, _, _, fld = DIM_MAP[lvl]
        _add_dim_join(extra_joins, lvl)
        conds.append(f"{pre}.{fld} = %(drilldown_group)s")
        params["drilldown_group"] = dl_group

    # Level-based grouping
    if level and str(level).isdigit() and int(level) in DIM_MAP:
        lvl = int(level)
        pre, _, _, fld = DIM_MAP[lvl]
        _add_dim_join(extra_joins, lvl)
        grp_field    = f"{pre}.{fld}"
        order_clause = "ORDER BY group_name"

    return grp_field, " ".join(extra_joins), order_clause, is_month_wise


def _month_fill(data, kwargs):
    """
    Ensure every month in the selected duration window appears in the result,
    filling missing months with 0. Mirrors the logic at the end of
    build_child_band_query.
    """
    y, m = (
        int(kwargs.get("year",  date.today().year)),
        int(kwargs.get("month", date.today().month)),
    )
    off    = OFFSET_MAP.get(kwargs.get("duration", "12_months"), 11)
    start  = date(y, m, 1) - relativedelta(months=off)
    labels = [
        (start + relativedelta(months=i)).strftime("%b-%Y").upper()
        for i in range(off + 1)
    ]
    val_map = {
        str(r.get("group_name", "")).upper(): int(r.get("value") or 0)
        for r in data
    }
    return [{"group_name": lbl, "value": val_map.get(lbl, 0)} for lbl in labels]


def _to_chart(data, dataset_name="Count"):
    """Convert [{group_name, value}] rows into the standard chart response."""
    return {
        "labels":   [str(r.get("group_name", "")) for r in data],
        "datasets": [
            {
                "name":   dataset_name,
                "values": [int(r.get("value") or 0) for r in data],
            }
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CORE QUERY BUILDERS
# (Logic sourced from the Enrollment Coverage report — build_query / subqueries)
# ═══════════════════════════════════════════════════════════════════════════════

# ── 1. Exit-based metrics (Total Exit, reasons 1-5) ──────────────────────────

def _build_exit_query(kwargs, reason=None):
    """
    Builds a time-series or level-grouped query against tabChild Enrollment and Exit.

    Source (report):
        nwexit  subquery  → new_exit  (all exits in date window)
        rext    subquery  → reason_1 … reason_5

    Args:
        reason: None → count ALL exits in window
                int   → count only rows where reason_for_exit = reason
    """
    s, e, y, m = _date_range(kwargs)
    off = OFFSET_MAP.get(kwargs.get("duration", "12_months"), 11)
    level, dl_level, dl_group = (
        kwargs.get("level"), kwargs.get("drilldown_level"), kwargs.get("drilldown_group")
    )
    is_mw = (dl_group and dl_level and str(dl_level).isdigit()) or not level
    if is_mw:
        s = date(y, m, 1) - relativedelta(months=off)

    params = {"start_date": s, "end_date": e}
    conds  = ["cee.date_of_exit BETWEEN %(start_date)s AND %(end_date)s"]
    if reason is not None:
        conds.append("cee.reason_for_exit = %(reason)s")
        params["reason"] = reason

    _geo_filters(kwargs, params, conds, "cr")
    _common_creche_filters(kwargs, params, conds, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds, params, "cee.date_of_exit"
    )

    query = f"""
        SELECT
            {grp}                      AS group_name,
            COUNT(*)                   AS value,
            MIN(cee.date_of_exit)      AS sort_date
        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
        {dim_joins}
        WHERE {" AND ".join(conds)}
        GROUP BY {grp}
        {order}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    return _month_fill(data, kwargs) if is_mw else data


# ── 2. New Enrollment (this month) ───────────────────────────────────────────

def _build_new_enrollment_query(kwargs):
    """
    Source (report): nwcuenroll_data subquery → new_enrollment_data
        WHERE date_of_enrollment BETWEEN %(start_date)s AND %(end_date)s
    """
    s, e, y, m = _date_range(kwargs)
    off = OFFSET_MAP.get(kwargs.get("duration", "12_months"), 11)
    level, dl_level, dl_group = (
        kwargs.get("level"), kwargs.get("drilldown_level"), kwargs.get("drilldown_group")
    )
    is_mw = (dl_group and dl_level and str(dl_level).isdigit()) or not level
    if is_mw:
        s = date(y, m, 1) - relativedelta(months=off)

    params = {"start_date": s, "end_date": e}
    conds  = ["cee.date_of_enrollment BETWEEN %(start_date)s AND %(end_date)s"]

    _geo_filters(kwargs, params, conds, "cr")
    _common_creche_filters(kwargs, params, conds, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds, params, "cee.date_of_enrollment"
    )

    query = f"""
        SELECT
            {grp}                           AS group_name,
            COUNT(*)                        AS value,
            MIN(cee.date_of_enrollment)     AS sort_date
        FROM `tabChild Enrollment and Exit` cee
        INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id
        {dim_joins}
        WHERE {" AND ".join(conds)}
        GROUP BY {grp}
        {order}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    return _month_fill(data, kwargs) if is_mw else data


# ── 3. Household Not-Enrolled (Migrated / Death / Outside Catchment) ─────────

def _build_hh_not_enrolled_query(kwargs, child_status):
    """
    Source (report): not_enrolled_counts subquery
        child_status = 1 → not_enrolled_death
        child_status = 2 → not_enrolled_migrated
        child_status = 3 → not_enrolled_outside

    Age gate mirrors the report: 6–36 months from end_date.
    These are point-in-time snapshot counts (no date window filtering).
    """
    _, e, _, _ = _date_range(kwargs)
    params = {"end_date": e, "child_status": child_status}
    conds  = [
        "hcf.is_dob_available = 1",
        "hcf.child_status = %(child_status)s",
        "hcf.child_dob <= DATE_SUB(%(end_date)s, INTERVAL 6 MONTH)",
        "hcf.child_dob >  DATE_SUB(%(end_date)s, INTERVAL 36 MONTH)",
    ]

    _geo_filters(kwargs, params, conds, "cr")
    _common_creche_filters(kwargs, params, conds, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds, params, "hf.creation"
    )

    query = f"""
        SELECT
            {grp}                           AS group_name,
            COUNT(DISTINCT hcf.hhcguid)     AS value
        FROM `tabHousehold Child Form` hcf
        INNER JOIN `tabHousehold Form` hf  ON hf.name   = hcf.parent
        INNER JOIN `tabCreche`         cr  ON cr.name   = hf.creche_id
        {dim_joins}
        WHERE {" AND ".join(conds)}
        GROUP BY {grp}
        {order}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    # For snapshot metrics, month-wise shows current count in the selected month
    if is_mw:
        data = _snapshot_to_month_series(data, kwargs)
    return data


def _snapshot_to_month_series(data, kwargs):
    """
    For point-in-time (snapshot) metrics, populate only the selected
    month with the actual count; all other months get 0.
    This signals 'current state' without implying spurious historical trend.
    """
    y, m = (
        int(kwargs.get("year",  date.today().year)),
        int(kwargs.get("month", date.today().month)),
    )
    off    = OFFSET_MAP.get(kwargs.get("duration", "12_months"), 11)
    start  = date(y, m, 1) - relativedelta(months=off)
    labels = [
        (start + relativedelta(months=i)).strftime("%b-%Y").upper()
        for i in range(off + 1)
    ]
    current_label = date(y, m, 1).strftime("%b-%Y").upper()
    total = sum(int(r.get("value") or 0) for r in data)
    return [
        {"group_name": lbl, "value": total if lbl == current_label else 0}
        for lbl in labels
    ]


# ── 4. To-Be-Enrolled ────────────────────────────────────────────────────────

def _build_to_be_enrolled_query(kwargs):
    """
    Source (report): tobe_counts subquery → to_be_enrolled

    Children aged 6–36 months from end_date who:
      • have no record in tabChild Enrollment and Exit (never enrolled)
      • have no child_status (not dead / migrated / outside)
      • is_dob_available = 1
    """
    _, e, _, _ = _date_range(kwargs)

    # Age reference: current date if end_date is in the current month,
    # otherwise end_date itself — mirrors the IF() in the report SQL.
    age_ref = (
        "IF(DATE_FORMAT(%(end_date)s,'%%Y-%%m') = DATE_FORMAT(CURDATE(),'%%Y-%%m'),"
        " CURDATE(), %(end_date)s)"
    )
    params = {"end_date": e}
    conds  = [
        "cee.hhcguid IS NULL",
        "(hcf.child_status IS NULL OR TRIM(hcf.child_status) = '')",
        "hcf.is_dob_available = 1",
        f"hcf.child_dob BETWEEN DATE_SUB({age_ref}, INTERVAL 36 MONTH)"
        f"                   AND DATE_SUB({age_ref}, INTERVAL 6 MONTH)",
    ]

    _geo_filters(kwargs, params, conds, "cr")
    _common_creche_filters(kwargs, params, conds, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds, params, "hf.creation"
    )

    query = f"""
        SELECT
            {grp}                           AS group_name,
            COUNT(DISTINCT hcf.hhcguid)     AS value
        FROM `tabHousehold Child Form` hcf
        INNER JOIN `tabHousehold Form`          hf  ON hf.name      = hcf.parent
        INNER JOIN `tabCreche`                  cr  ON cr.name       = hf.creche_id
        LEFT  JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid = hcf.hhcguid
        {dim_joins}
        WHERE {" AND ".join(conds)}
        GROUP BY {grp}
        {order}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    if is_mw:
        data = _snapshot_to_month_series(data, kwargs)
    return data


# ── 5. Total Not-Enrolled ─────────────────────────────────────────────────────

def _build_total_not_enrolled_query(kwargs):
    """
    Source (report):
        total_not_enrolled = not_enrolled_migrated + not_enrolled_death
                           + not_enrolled_outside + to_be_enrolled

    Runs a single combined query using conditional SUMs — mirrors the
    not_enrolled_counts + tobe_counts subqueries joined in the report.
    """
    _, e, _, _ = _date_range(kwargs)
    age_ref = (
        "IF(DATE_FORMAT(%(end_date)s,'%%Y-%%m') = DATE_FORMAT(CURDATE(),'%%Y-%%m'),"
        " CURDATE(), %(end_date)s)"
    )
    params = {"end_date": e}

    # We union two logical groups under one GROUP BY:
    #  (a) hh children with child_status IN (1,2,3) in age range
    #  (b) eligible children with no enrollment record at all

    conds_base = [
        "hcf.is_dob_available = 1",
        f"hcf.child_dob <= DATE_SUB({age_ref}, INTERVAL 6 MONTH)",
        f"hcf.child_dob >  DATE_SUB({age_ref}, INTERVAL 36 MONTH)",
    ]

    _geo_filters(kwargs, params, conds_base, "cr")
    _common_creche_filters(kwargs, params, conds_base, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds_base, params, "hf.creation"
    )

    where = " AND ".join(conds_base)

    query = f"""
        SELECT
            {grp} AS group_name,
            (
                -- Not-enrolled by status (migrated + death + outside)
                COUNT(DISTINCT CASE
                    WHEN hcf.child_status IN (1, 2, 3) THEN hcf.hhcguid
                END)
                +
                -- To-be-enrolled: eligible, no status, never enrolled
                COUNT(DISTINCT CASE
                    WHEN (hcf.child_status IS NULL OR TRIM(hcf.child_status) = '')
                         AND cee.hhcguid IS NULL
                    THEN hcf.hhcguid
                END)
            ) AS value
        FROM `tabHousehold Child Form` hcf
        INNER JOIN `tabHousehold Form`            hf  ON hf.name      = hcf.parent
        INNER JOIN `tabCreche`                    cr  ON cr.name       = hf.creche_id
        LEFT  JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid   = hcf.hhcguid
        {dim_joins}
        WHERE {where}
        GROUP BY {grp}
        {order}
    """
    data = frappe.db.sql(query, params, as_dict=True)
    if is_mw:
        data = _snapshot_to_month_series(data, kwargs)
    return data


# ── 6. Eligible vs Enrolled ───────────────────────────────────────────────────

def _build_eligible_enrolled_query(kwargs):
    """
    Source (report):
        ec subquery     → e_children   (eligible: 6–36 months, no child_status)
        nwcuenroll sub  → new_enrollment (enrolled by end_date, not yet exited)

    Returns a dual-dataset chart for side-by-side comparison.
    """
    _, e, _, _ = _date_range(kwargs)
    age_ref = (
        "IF(DATE_FORMAT(%(end_date)s,'%%Y-%%m') = DATE_FORMAT(CURDATE(),'%%Y-%%m'),"
        " CURDATE(), %(end_date)s)"
    )
    params = {"end_date": e}
    conds  = [
        "hcf.is_dob_available = 1",
        "(hcf.child_status IS NULL OR TRIM(hcf.child_status) = '')",
        f"hcf.child_dob BETWEEN DATE_SUB({age_ref}, INTERVAL 36 MONTH)"
        f"                   AND DATE_SUB({age_ref}, INTERVAL 6 MONTH)",
    ]

    _geo_filters(kwargs, params, conds, "cr")
    _common_creche_filters(kwargs, params, conds, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds, params, "hf.creation"
    )

    query = f"""
        SELECT
            {grp}                                           AS group_name,
            COUNT(DISTINCT hcf.hhcguid)                     AS eligible,
            COUNT(DISTINCT CASE
                WHEN cee.date_of_enrollment <= %(end_date)s
                     AND (cee.date_of_exit IS NULL OR cee.date_of_exit >= %(end_date)s)
                THEN cee.childenrollguid
            END)                                            AS enrolled
        FROM `tabHousehold Child Form` hcf
        INNER JOIN `tabHousehold Form`            hf  ON hf.name      = hcf.parent
        INNER JOIN `tabCreche`                    cr  ON cr.name       = hf.creche_id
        LEFT  JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid   = hcf.hhcguid
        {dim_joins}
        WHERE {" AND ".join(conds)}
        GROUP BY {grp}
        {order}
    """
    rows = frappe.db.sql(query, params, as_dict=True)

    # Build dual-dataset chart response
    labels   = [str(r.get("group_name", "")) for r in rows]
    eligible = [int(r.get("eligible") or 0) for r in rows]
    enrolled = [int(r.get("enrolled") or 0) for r in rows]

    return {
        "labels":   labels,
        "datasets": [
            {"name": "Eligible Children (6-36 months)", "values": eligible},
            {"name": "Enrolled Children",               "values": enrolled},
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# WHITELISTED API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@frappe.whitelist()
def get_eligible_enrolled_data(**kwargs):
    """
    Indicator 1: Eligible vs Enrolled (Unique Value)
    Returns a dual-dataset chart: eligible children (6–36 months) vs enrolled.
    """
    cache_key = get_cache_key("get_eligible_enrolled_data", frappe.form_dict)

    def fetch():
        return _build_eligible_enrolled_query(kwargs)

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_total_exited(**kwargs):
    """
    Indicator 2: Total Exited
    Report field: new_exit
    All children whose date_of_exit falls within the selected period.
    """
    cache_key = get_cache_key("get_total_exited", frappe.form_dict)

    def fetch():
        data = _build_exit_query(kwargs, reason=None)
        return _to_chart(data, "Total Exited")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_exit_graduated(**kwargs):
    """
    Indicator 3: Exit (Graduated)
    Report field: reason_2  (reason_for_exit = 2)
    """
    cache_key = get_cache_key("get_exit_graduated", frappe.form_dict)

    def fetch():
        data = _build_exit_query(kwargs, reason=2)
        return _to_chart(data, "Graduated")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_exit_migrated(**kwargs):
    """
    Indicator 4: Exit (Migrated)
    Report field: reason_1  (reason_for_exit = 1)
    """
    cache_key = get_cache_key("get_exit_migrated", frappe.form_dict)

    def fetch():
        data = _build_exit_query(kwargs, reason=1)
        return _to_chart(data, "Migrated")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_exit_not_willing(**kwargs):
    """
    Indicator 5: Exit (Not Willing to Stay)
    Report field: reason_3  (reason_for_exit = 3)
    """
    cache_key = get_cache_key("get_exit_not_willing", frappe.form_dict)

    def fetch():
        data = _build_exit_query(kwargs, reason=3)
        return _to_chart(data, "Not Willing to Stay")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_exit_death(**kwargs):
    """
    Indicator 6: Exit (Death)
    Report field: reason_4  (reason_for_exit = 4)
    """
    cache_key = get_cache_key("get_exit_death", frappe.form_dict)

    def fetch():
        data = _build_exit_query(kwargs, reason=4)
        return _to_chart(data, "Death")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_exit_other(**kwargs):
    """
    Indicator 7: Exit (Other)
    Report field: reason_5  (reason_for_exit = 5)
    """
    cache_key = get_cache_key("get_exit_other", frappe.form_dict)

    def fetch():
        data = _build_exit_query(kwargs, reason=5)
        return _to_chart(data, "Other")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_total_not_enrolled(**kwargs):
    """
    Indicator 8: Total Not Enrolled
    Report field: total_not_enrolled
    = not_enrolled_migrated + not_enrolled_death + not_enrolled_outside
      + to_be_enrolled
    """
    cache_key = get_cache_key("get_total_not_enrolled", frappe.form_dict)

    def fetch():
        data = _build_total_not_enrolled_query(kwargs)
        return _to_chart(data, "Total Not Enrolled")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_not_enrolled_migrated(**kwargs):
    """
    Indicator 9: Not Enrolled (Migrated)
    Report field: not_enrolled_migrated
    Source: tabHousehold Child Form WHERE child_status = 2, age 6–36 months.
    """
    cache_key = get_cache_key("get_not_enrolled_migrated", frappe.form_dict)

    def fetch():
        data = _build_hh_not_enrolled_query(kwargs, child_status=2)
        return _to_chart(data, "Not Enrolled (Migrated)")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_not_enrolled_death(**kwargs):
    """
    Indicator 10: Not Enrolled (Death)
    Report field: not_enrolled_death
    Source: tabHousehold Child Form WHERE child_status = 1, age 6–36 months.
    """
    cache_key = get_cache_key("get_not_enrolled_death", frappe.form_dict)

    def fetch():
        data = _build_hh_not_enrolled_query(kwargs, child_status=1)
        return _to_chart(data, "Not Enrolled (Death)")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_not_enrolled_outside_catchment(**kwargs):
    """
    Indicator 11: Not Enrolled (Outside Catchment Area)
    Report field: not_enrolled_outside
    Source: tabHousehold Child Form WHERE child_status = 3, age 6–36 months.
    """
    cache_key = get_cache_key("get_not_enrolled_outside_catchment", frappe.form_dict)

    def fetch():
        data = _build_hh_not_enrolled_query(kwargs, child_status=3)
        return _to_chart(data, "Not Enrolled (Outside Catchment)")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_to_be_enrolled(**kwargs):
    """
    Indicator 12: To Be Enrolled
    Report field: to_be_enrolled
    Eligible (6–36 months), no child_status, no enrollment record yet.
    """
    cache_key = get_cache_key("get_to_be_enrolled", frappe.form_dict)

    def fetch():
        data = _build_to_be_enrolled_query(kwargs)
        return _to_chart(data, "To Be Enrolled")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)


@frappe.whitelist()
def get_new_enrolment(**kwargs):
    """
    Indicator 13: New Enrolment (This Month)
    Report field: new_enrollment_data
    Children whose date_of_enrollment falls within the selected period.
    """
    cache_key = get_cache_key("get_new_enrolment", frappe.form_dict)

    def fetch():
        data = _build_new_enrollment_query(kwargs)
        return _to_chart(data, "New Enrolment")

    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch, shared=True)








# ==============================================================================
# NEW EXIT & ENROLLMENT APIs
# ==============================================================================

def build_new_kpi_query(kwargs, api_type, sub_type=None):
    """
    Unified query builder handling dynamic snapshots, month-wise trends, and geographical 
    drilldowns for Exits, Enrollments, and Not Enrolled parameters. 
    Matches standard API response format `{"labels": [...], "datasets": [...]}`.
    """
    year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
    if not year or not month: 
        return {"labels": [], "datasets": []}

    start_date = date(year, month, 1)
    end_date = start_date + relativedelta(months=1) - relativedelta(days=1)
    
    # Logic: IF(DATE_FORMAT(selected) = DATE_FORMAT(CURDATE), CURDATE(), selected_end)
    if end_date.strftime('%Y-%m') == date.today().strftime('%Y-%m'):
        ref_date_str = date.today().strftime('%Y-%m-%d')
    else:
        ref_date_str = end_date.strftime('%Y-%m-%d')

    params = {"ref_date": ref_date_str, "start_date": start_date.strftime('%Y-%m-%d')}
    conditions = []
    join_clauses = []

    if api_type == "exit":
        main_table = "`tabChild Enrollment and Exit` main"
        join_clauses.append("INNER JOIN `tabCreche` cr ON cr.name = main.creche_id")
        date_cond = "main.date_of_exit <= %(ref_date)s"
        
        if sub_type == "graduated": conditions.append("main.reason_for_exit = 2")
        elif sub_type == "migrated": conditions.append("main.reason_for_exit = 3")
        elif sub_type == "not_willing": conditions.append("main.reason_for_exit = 1")
        elif sub_type == "death": conditions.append("main.reason_for_exit = 4")
        elif sub_type == "other": conditions.append("main.reason_for_exit = 5")
        
        kpi_name = f"Exit ({sub_type.replace('_', ' ').title()})" if sub_type else "Total Exited"

    elif api_type == "not_enrolled":
        main_table = "`tabHousehold Child Form` main"
        join_clauses.append("INNER JOIN `tabHousehold Form` hf ON hf.name = main.parent")
        join_clauses.append("INNER JOIN `tabCreche` cr ON cr.name = hf.creche_id")
        
        if sub_type == "death": conditions.append("main.child_status = 1")
        elif sub_type == "migrated": conditions.append("main.child_status = 2")
        elif sub_type == "outside_catchment": conditions.append("main.child_status = 3")
        else: conditions.append("main.child_status IN (1, 2, 3)")
        
        date_cond = "main.creation <= %(ref_date)s" 
        kpi_name = f"Not Enrolled ({sub_type.replace('_', ' ').title()})" if sub_type else "Total Not Enrolled"

    elif api_type == "to_be_enrolled":
        main_table = "`tabHousehold Child Form` main"
        join_clauses.append("INNER JOIN `tabHousehold Form` hf ON hf.name = main.parent")
        join_clauses.append("LEFT JOIN `tabChild Enrollment and Exit` cee ON cee.hhcguid = main.hhcguid")
        join_clauses.append("INNER JOIN `tabCreche` cr ON cr.name = hf.creche_id")

        conditions.append("main.is_dob_available = 1")
        conditions.append("(main.child_status IS NULL OR TRIM(main.child_status) = '')")
        conditions.append("cee.hhcguid IS NULL")
        
        date_cond = "main.child_dob BETWEEN DATE_SUB(%(ref_date)s, INTERVAL 36 MONTH) AND DATE_SUB(%(ref_date)s, INTERVAL 6 MONTH)"
        kpi_name = "To be Enrolled"

    elif api_type == "new_enrolment":
        main_table = "`tabChild Enrollment and Exit` main"
        join_clauses.append("INNER JOIN `tabCreche` cr ON cr.name = main.creche_id")
        date_cond = "main.date_of_enrollment BETWEEN %(start_date)s AND %(ref_date)s"
        kpi_name = "New Enrolment"

    # Common Filters (Geography, Hierarchy, etc.)
    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("cr.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id

    append_geography_filters(kwargs, params, conditions, "cr")

    if kwargs.get("creche_id"):
        conditions.append("cr.name = %(creche_id)s")
        params["creche_id"] = kwargs.get("creche_id")

    if kwargs.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = kwargs.get("supervisor_id")

    c_status_val = kwargs.get("c_status") or kwargs.get("creche_status_id")
    if c_status_val:
        conditions.append("cr.creche_status_id = %(creche_status)s")
        params["creche_status"] = c_status_val
        
    if kwargs.get("phases"):
        phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params["phases"] = phases

    level = kwargs.get("level")
    dl_group = kwargs.get("drilldown_group")
    dl_level = kwargs.get("drilldown_level")

    dimension_map = {
        1: ("p", "`tabPartner`", "partner_id", "partner_name"),
        2: ("s", "`tabState`", "state_id", "state_name"),
        3: ("d", "`tabDistrict`", "district_id", "district_name"),
        4: ("b", "`tabBlock`", "block_id", "block_name"),
        5: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
        6: ("cr_dim", "`tabCreche`", "name", "creche_name"),
        7: ("u", "`tabUser`", "supervisor_id", "full_name")
    }

    tables_to_join = set()
    group_name_field = "'All Data'"
    is_month_wise = False

    if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(dl_level)]
        if int(dl_level) == 6:
            conditions.append(f"cr.name = %(drilldown_group)s")
        else:
            tables_to_join.add(int(dl_level))
            conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
        params["drilldown_group"] = dl_group
        level = None
        is_month_wise = True

    if level and str(level).isdigit() and int(level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(level)]
        if int(level) == 6:
            group_name_field = "cr.creche_name"
        else:
            tables_to_join.add(int(level))
            group_name_field = f"{prefix}.{field}"
    elif not level:
        is_month_wise = True

    for tbl_id in tables_to_join:
        prefix, table, fk, field = dimension_map[tbl_id]
        if table == "`tabUser`":
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.email = cr.{fk}")
        else:
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

    # Single Month / Level Based Selection
    if not is_month_wise:
        conditions.append(date_cond)
        query = f"""
            SELECT {group_name_field} AS group_name, COUNT(DISTINCT main.name) AS count
            FROM {main_table}
            {" ".join(join_clauses)}
            WHERE {" AND ".join(conditions)}
            GROUP BY {group_name_field}
            ORDER BY group_name
        """
        data = frappe.db.sql(query, params, as_dict=True)
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data],
            "datasets": [{"name": kpi_name, "values": [int(r.get("count", 0)) for r in data]}]
        }
    
    # Multi-month Series Logic 
    else:
        duration = kwargs.get("duration", "12_months")
        offset_map = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}
        offset = offset_map.get(duration, 11)

        start_date_dyn = end_date - relativedelta(months=offset)
        params["start_date_dyn"] = start_date_dyn

        months_select = []
        for i in range(offset + 1):
            m_date = start_date_dyn + relativedelta(months=i)
            m_start = m_date.strftime("%Y-%m-01")
            m_end = (m_date + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")
            
            # Dynamic referential tracking per month
            if m_end == date.today().strftime('%Y-%m-%d') or (m_date.year == date.today().year and m_date.month == date.today().month):
                m_ref = date.today().strftime('%Y-%m-%d')
            else:
                m_ref = m_end

            month_label = m_date.strftime('%b-%Y').upper()

            if api_type == "exit":
                m_cond = f"main.date_of_exit <= '{m_ref}'"
            elif api_type == "not_enrolled":
                m_cond = f"main.creation <= '{m_ref}'"
            elif api_type == "to_be_enrolled":
                m_cond = f"main.child_dob BETWEEN DATE_SUB('{m_ref}', INTERVAL 36 MONTH) AND DATE_SUB('{m_ref}', INTERVAL 6 MONTH)"
            elif api_type == "new_enrolment":
                m_cond = f"main.date_of_enrollment BETWEEN '{m_start}' AND '{m_ref}'"

            months_select.append(f"COUNT(DISTINCT CASE WHEN {m_cond} THEN main.name END) AS `{month_label}`")

        query = f"""
            SELECT {group_name_field} AS group_name, {", ".join(months_select)}
            FROM {main_table}
            {" ".join(join_clauses)}
            WHERE {" AND ".join(conditions) if conditions else "1=1"}
            GROUP BY {group_name_field}
        """
        data = frappe.db.sql(query, params, as_dict=True)
        labels = [(start_date_dyn + relativedelta(months=i)).strftime("%b-%Y").upper() for i in range(offset + 1)]

        return {
            "labels": labels,
            "datasets": [{
                "name": kpi_name,
                "values": [int(data[0].get(l, 0) or 0) for l in labels] if data else [0] * len(labels)
            }]
        }


# ------------- API ENDPOINTS ------------- #

@frappe.whitelist()
def get_total_exited(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_total_exited", params)
    def fetch_data(): return build_new_kpi_query(params, "exit")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_exit_graduated(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_exit_graduated", params)
    def fetch_data(): return build_new_kpi_query(params, "exit", "graduated")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_exit_migrated(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_exit_migrated", params)
    def fetch_data(): return build_new_kpi_query(params, "exit", "migrated")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_exit_not_willing(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_exit_not_willing", params)
    def fetch_data(): return build_new_kpi_query(params, "exit", "not_willing")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_exit_death(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_exit_death", params)
    def fetch_data(): return build_new_kpi_query(params, "exit", "death")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_exit_other(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_exit_other", params)
    def fetch_data(): return build_new_kpi_query(params, "exit", "other")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_total_not_enrolled(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_total_not_enrolled", params)
    def fetch_data(): return build_new_kpi_query(params, "not_enrolled")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_not_enrolled_migrated(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_not_enrolled_migrated", params)
    def fetch_data(): return build_new_kpi_query(params, "not_enrolled", "migrated")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_not_enrolled_death(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_not_enrolled_death", params)
    def fetch_data(): return build_new_kpi_query(params, "not_enrolled", "death")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_not_enrolled_outside_catchment(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_not_enrolled_outside_catchment", params)
    def fetch_data(): return build_new_kpi_query(params, "not_enrolled", "outside_catchment")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_to_be_enrolled(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_to_be_enrolled", params)
    def fetch_data(): return build_new_kpi_query(params, "to_be_enrolled")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_new_enrolment(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_new_enrolment", params)
    def fetch_data(): return build_new_kpi_query(params, "new_enrolment")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)



# ==============================================================================
# ANTHROPOMETRIC & MEASUREMENT APIs
# ==============================================================================

def anthro_core_query(kwargs, api_mode):
    """
    Centralized query builder for Anthropometric data.
    Handles Measured vs Enrolled %, Standard Indicators, and Stacked Data.
    """
    year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
    if not year or not month: return {"labels": [], "datasets": []}

    params = {}
    conditions = []

    # Common Filters
    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("cr.partner_id = %(partner_id)s")
        params["partner_id"] = partner_id

    append_geography_filters(kwargs, params, conditions, "cr")
    
    if kwargs.get("creche_id"):
        conditions.append("cr.name = %(creche_id)s")
        params["creche_id"] = kwargs.get("creche_id")

    if kwargs.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params["supervisor_id"] = kwargs.get("supervisor_id")

    c_status_val = kwargs.get("c_status") or kwargs.get("creche_status_id")
    if c_status_val:
        conditions.append("cr.creche_status_id = %(creche_status)s")
        params["creche_status"] = c_status_val

    if kwargs.get("phases"):
        phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params["phases"] = phases

    level = kwargs.get("level")
    dl_group = kwargs.get("drilldown_group")
    dl_level = kwargs.get("drilldown_level")

    dimension_map = {
        1: ("p", "`tabPartner`", "partner_id", "partner_name"),
        2: ("s", "`tabState`", "state_id", "state_name"),
        3: ("d", "`tabDistrict`", "district_id", "district_name"),
        4: ("b", "`tabBlock`", "block_id", "block_name"),
        5: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
        6: ("cr_dim", "`tabCreche`", "name", "creche_name"),
        7: ("u", "`tabUser`", "supervisor_id", "full_name")
    }

    tables_to_join = set()
    group_name_field = "'All Data'"
    is_month_wise = False

    if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(dl_level)]
        if int(dl_level) == 6:
            conditions.append("cr.name = %(drilldown_group)s")
        else:
            tables_to_join.add(int(dl_level))
            conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
        params["drilldown_group"] = dl_group
        level = None
        is_month_wise = True

    if level and str(level).isdigit() and int(level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(level)]
        if int(level) == 6:
            group_name_field = "cr.creche_name"
        else:
            tables_to_join.add(int(level))
            group_name_field = f"{prefix}.{field}"
    elif not level:
        is_month_wise = True

    join_clauses = ["INNER JOIN `tabCreche` cr ON cr.name = cee.creche_id"]
    for tbl_id in tables_to_join:
        prefix, table, fk, field = dimension_map[tbl_id]
        if table == "`tabUser`":
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.email = cr.{fk}")
        else:
            join_clauses.append(f"LEFT JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

    # Anthropometric specific joins
    join_clauses.append("""
        LEFT JOIN `tabAnthropromatic Data` ad 
        ON ad.childenrollguid = cee.childenrollguid 
        AND ad.do_you_have_height_weight = 1
    """)
    join_clauses.append("""
        LEFT JOIN `tabChild Growth Monitoring` cgm 
        ON cgm.name = ad.parent
    """)

    # --- 1. Month-Wise Drilldown Evaluation ---
    if is_month_wise:
        duration = kwargs.get("duration", "12_months")
        offset_map = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}
        offset = offset_map.get(duration, 11)

        start_date_dyn = date(year, month, 1) - relativedelta(months=offset)
        selects = []
        labels = []

        for i in range(offset + 1):
            m_date = start_date_dyn + relativedelta(months=i)
            m_start = m_date.strftime("%Y-%m-01")
            m_end = (m_date + relativedelta(months=1) - relativedelta(days=1)).strftime("%Y-%m-%d")
            m_label = m_date.strftime('%b-%Y').upper()
            labels.append(m_label)

            enr_cond = f"cee.date_of_enrollment <= '{m_end}' AND (cee.date_of_exit IS NULL OR cee.date_of_exit > '{m_end}')"
            meas_cond = f"COALESCE(cgm.measurement_date, ad.measurement_taken_date) BETWEEN '{m_start}' AND '{m_end}'"
            meas_taken_cond = f"cee.date_of_enrollment <= '{m_end}' AND (cee.date_of_exit IS NULL OR cee.date_of_exit > '{m_start}') AND {meas_cond}"

            if api_mode == "measured_data":
                selects.append(f"ROUND((COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} THEN cee.name END) * 100.0) / NULLIF(COUNT(DISTINCT CASE WHEN {enr_cond} THEN cee.name END), 0), 2) AS `{m_label}`")
                selects.append(f"COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS `meas_{m_label}`")
            elif api_mode == "enrolled_measured":
                selects.append(f"COUNT(DISTINCT CASE WHEN {enr_cond} THEN cee.name END) AS `enr_{m_label}`")
                selects.append(f"COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS `meas_{m_label}`")
            elif api_mode.endswith("_all"):
                col = {"wfa": "weight_for_age", "wfh": "weight_for_height", "hfa": "height_for_age"}[api_mode[:3]]
                selects.append(f"COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = 3 THEN cee.name END) AS `norm_{m_label}`")
                selects.append(f"COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = 2 THEN cee.name END) AS `mod_{m_label}`")
                selects.append(f"COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = 1 THEN cee.name END) AS `sev_{m_label}`")
                selects.append(f"COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS `meas_{m_label}`")
            else:
                cat, level_str = api_mode.split('_')
                col = {"wfa": "weight_for_age", "wfh": "weight_for_height", "hfa": "height_for_age"}[cat]
                lvl_val = {"normal": 3, "modrate": 2, "severe": 1}[level_str]
                selects.append(f"COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = {lvl_val} THEN cee.name END) AS `{m_label}`")
                selects.append(f"COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS `meas_{m_label}`")

        query = f"""
            SELECT {group_name_field} AS group_name, {', '.join(selects)} 
            FROM `tabChild Enrollment and Exit` cee 
            {' '.join(join_clauses)} 
            WHERE {' AND '.join(conditions) if conditions else '1=1'} 
            GROUP BY {group_name_field}
        """
        data = frappe.db.sql(query, params, as_dict=True)

        if api_mode == "measured_data":
            return {"labels": labels, "datasets": [{"name": "Measurement %", "values": [f"{data[0].get(l, 0) or 0}%" for l in labels] if data else [0] * len(labels)}], "extra": {"Measurement Taken": [data[0].get(f"meas_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)}}
        elif api_mode == "enrolled_measured":
            return {"labels": labels, "datasets": [{"name": "Enrolled", "values": [data[0].get(f"enr_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)}, {"name": "Measured", "values": [data[0].get(f"meas_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)}]}
        elif api_mode.endswith("_all"):
            return {"labels": labels, "datasets": [
                {"name": "Normal", "values": [data[0].get(f"norm_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)},
                {"name": "Moderate", "values": [data[0].get(f"mod_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)},
                {"name": "Severe", "values": [data[0].get(f"sev_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)}
            ], "extra": {"Measurement Taken": [data[0].get(f"meas_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)}}
        else:
            return {"labels": labels, "datasets": [{"name": "Value", "values": [data[0].get(l, 0) or 0 for l in labels] if data else [0] * len(labels)}], "extra": {"Measurement Taken": [data[0].get(f"meas_{l}", 0) or 0 for l in labels] if data else [0] * len(labels)}}

    # --- 2. Cross-Sectional Level Evaluation ---
    else:
        m_start = date(year, month, 1).strftime("%Y-%m-01")
        m_end = date(year, month, calendar.monthrange(year, month)[1]).strftime("%Y-%m-%d")

        enr_cond = f"cee.date_of_enrollment <= '{m_end}' AND (cee.date_of_exit IS NULL OR cee.date_of_exit > '{m_end}')"
        meas_cond = f"COALESCE(cgm.measurement_date, ad.measurement_taken_date) BETWEEN '{m_start}' AND '{m_end}'"
        meas_taken_cond = f"cee.date_of_enrollment <= '{m_end}' AND (cee.date_of_exit IS NULL OR cee.date_of_exit > '{m_start}') AND {meas_cond}"

        if api_mode == "measured_data":
            select_expr = f"""
                ROUND((COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} THEN cee.name END) * 100.0) / NULLIF(COUNT(DISTINCT CASE WHEN {enr_cond} THEN cee.name END), 0), 2) AS value,
                COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS measured
            """
        elif api_mode == "enrolled_measured":
            select_expr = f"COUNT(DISTINCT CASE WHEN {enr_cond} THEN cee.name END) AS enrolled, COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS measured"
        elif api_mode.endswith("_all"):
            col = {"wfa": "weight_for_age", "wfh": "weight_for_height", "hfa": "height_for_age"}[api_mode[:3]]
            select_expr = f"""
                COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = 3 THEN cee.name END) AS normal, 
                COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = 2 THEN cee.name END) AS moderate, 
                COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = 1 THEN cee.name END) AS severe,
                COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS measured
            """
        else:
            cat, level_str = api_mode.split('_')
            col = {"wfa": "weight_for_age", "wfh": "weight_for_height", "hfa": "height_for_age"}[cat]
            lvl_val = {"normal": 3, "modrate": 2, "severe": 1}[level_str]
            select_expr = f"""
                COUNT(DISTINCT CASE WHEN {enr_cond} AND {meas_cond} AND ad.{col} = {lvl_val} THEN cee.name END) AS value,
                COUNT(DISTINCT CASE WHEN {meas_taken_cond} THEN cee.name END) AS measured
            """

        query = f"""
            SELECT {group_name_field} AS group_name, {select_expr} 
            FROM `tabChild Enrollment and Exit` cee 
            {' '.join(join_clauses)} 
            WHERE {' AND '.join(conditions) if conditions else '1=1'} 
            GROUP BY {group_name_field} 
            ORDER BY group_name
        """
        data = frappe.db.sql(query, params, as_dict=True)

        labels = [str(r.get("group_name", "Unknown")) for r in data]

        if api_mode == "measured_data":
            return {"labels": labels, "datasets": [{"name": "Measurement %", "values": [f"{r.get('value', 0) or 0}%" for r in data]}], "extra": {"Measurement Taken": [int(r.get("measured", 0)) for r in data]}}
        elif api_mode == "enrolled_measured":
            return {"labels": labels, "datasets": [{"name": "Enrolled", "values": [int(r.get("enrolled", 0)) for r in data]}, {"name": "Measured", "values": [int(r.get("measured", 0)) for r in data]}]}
        elif api_mode.endswith("_all"):
            return {"labels": labels, "datasets": [{"name": "Normal", "values": [int(r.get("normal", 0)) for r in data]}, {"name": "Moderate", "values": [int(r.get("moderate", 0)) for r in data]}, {"name": "Severe", "values": [int(r.get("severe", 0)) for r in data]}], "extra": {"Measurement Taken": [int(r.get("measured", 0)) for r in data]}}
        else:
            return {"labels": labels, "datasets": [{"name": "Value", "values": [int(r.get("value", 0)) for r in data]}], "extra": {"Measurement Taken": [int(r.get("measured", 0)) for r in data]}}

# ------------- API Endpoints Wrapper ------------- #

@frappe.whitelist()
def get_measured_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_measured_data", params)
    def fetch_data(): return anthro_core_query(params, "measured_data")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_enrolled_measured(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_enrolled_measured", params)
    def fetch_data(): return anthro_core_query(params, "enrolled_measured")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_wfa_normal_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_wfa_normal_data", params)
    def fetch_data(): return anthro_core_query(params, "wfa_normal")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_wfa_modrate_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_wfa_modrate_data", params)
    def fetch_data(): return anthro_core_query(params, "wfa_modrate")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_wfa_severe_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_wfa_severe_data", params)
    def fetch_data(): return anthro_core_query(params, "wfa_severe")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_wfh_normal_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_wfh_normal_data", params)
    def fetch_data(): return anthro_core_query(params, "wfh_normal")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_wfh_modrate_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_wfh_modrate_data", params)
    def fetch_data(): return anthro_core_query(params, "wfh_modrate")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_wfh_severe_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_wfh_severe_data", params)
    def fetch_data(): return anthro_core_query(params, "wfh_severe")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_hfa_normal_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_hfa_normal_data", params)
    def fetch_data(): return anthro_core_query(params, "hfa_normal")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_hfa_modrate_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_hfa_modrate_data", params)
    def fetch_data(): return anthro_core_query(params, "hfa_modrate")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_hfa_severe_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_hfa_severe_data", params)
    def fetch_data(): return anthro_core_query(params, "hfa_severe")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_weight_age_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_weight_age_data", params)
    def fetch_data(): return anthro_core_query(params, "wfa_all")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_weight_height_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_weight_height_data", params)
    def fetch_data(): return anthro_core_query(params, "wfh_all")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_height_age_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_height_age_data", params)
    def fetch_data(): return anthro_core_query(params, "hfa_all")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)


# -------------------GF - ZNC apis------------------- #

# ==============================================================================
# GF, ZIG-ZAG & SNC APIs
# ==============================================================================

def _rollback_month(y, m, step):
    """Helper to step backwards by N months."""
    m = m - step
    while m <= 0:
        m += 12
        y -= 1
    return m, y

def _execute_gf_single_month(target_year, target_month, api_mode, group_name_field, dim_joins, base_conditions, params_base):
    """Executes the exact GF/SNC logic for a single target month to ensure complex JOIN math stays intact."""
    params = params_base.copy()
    params["year"] = target_year
    params["month"] = target_month
    params["start_date"] = date(target_year, target_month, 1)
    params["end_date"] = date(target_year, target_month, calendar.monthrange(target_year, target_month)[1])

    # GF1 Math
    gf1_prev_m, gf1_prev_y = _rollback_month(target_year, target_month, 1)
    gf1_fall_m, gf1_fall_y = _rollback_month(target_year, target_month, 2)
    # GF2 Math
    gf2_prio_m, gf2_prio_y = _rollback_month(target_year, target_month, 2)
    gf2_fall_m, gf2_fall_y = _rollback_month(target_year, target_month, 3)
    # Zig-Zag Math
    zz_m1_m, zz_m1_y = _rollback_month(target_year, target_month, 1)
    zz_m2_m, zz_m2_y = _rollback_month(target_year, target_month, 2)
    zz_m3_m, zz_m3_y = _rollback_month(target_year, target_month, 3)
    zz_m4_m, zz_m4_y = _rollback_month(target_year, target_month, 4)

    params.update({
        "gf1_prev_y": gf1_prev_y, "gf1_prev_m": gf1_prev_m,
        "gf1_fall_y": gf1_fall_y, "gf1_fall_m": gf1_fall_m,
        "gf2_prio_y": gf2_prio_y, "gf2_prio_m": gf2_prio_m,
        "gf2_fall_y": gf2_fall_y, "gf2_fall_m": gf2_fall_m,
        "zz_m1_y": zz_m1_y, "zz_m1_m": zz_m1_m,
        "zz_m2_y": zz_m2_y, "zz_m2_m": zz_m2_m,
        "zz_m3_y": zz_m3_y, "zz_m3_m": zz_m3_m,
        "zz_m4_y": zz_m4_y, "zz_m4_m": zz_m4_m
    })

    joins = [
        "INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent",
        "INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid",
        "INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id"
    ] + dim_joins

    conditions = [
        "ad_current.do_you_have_height_weight = 1",
        "ad_current.weight_for_age_zscore IS NOT NULL",
        "YEAR(cgm.measurement_date) = %(year)s",
        "MONTH(cgm.measurement_date) = %(month)s",
        "cee.date_of_enrollment <= %(end_date)s",
        "(cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)"
    ] + base_conditions

    # 1. GF1 specific logic
    gf1_joins = """
        LEFT JOIN `tabAnthropromatic Data` AS ad_prev 
            ON ad_prev.childenrollguid = ad_current.childenrollguid AND ad_prev.do_you_have_height_weight = 1 
            AND YEAR(ad_prev.measurement_taken_date) = %(gf1_prev_y)s AND MONTH(ad_prev.measurement_taken_date) = %(gf1_prev_m)s AND ad_prev.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_fallback 
            ON ad_fallback.childenrollguid = ad_current.childenrollguid AND ad_fallback.do_you_have_height_weight = 1 
            AND YEAR(ad_fallback.measurement_taken_date) = %(gf1_fall_y)s AND MONTH(ad_fallback.measurement_taken_date) = %(gf1_fall_m)s 
            AND ad_fallback.weight_for_age_zscore IS NOT NULL AND ad_prev.childenrollguid IS NULL
    """
    
    # 2. GF2 specific logic
    gf2_joins = """
        LEFT JOIN `tabAnthropromatic Data` AS ad_priority 
            ON ad_priority.childenrollguid = ad_current.childenrollguid AND ad_priority.do_you_have_height_weight = 1 
            AND YEAR(ad_priority.measurement_taken_date) = %(gf2_prio_y)s AND MONTH(ad_priority.measurement_taken_date) = %(gf2_prio_m)s AND ad_priority.weight_for_age_zscore IS NOT NULL
        LEFT JOIN `tabAnthropromatic Data` AS ad_fallback_2 
            ON ad_fallback_2.childenrollguid = ad_current.childenrollguid AND ad_fallback_2.do_you_have_height_weight = 1 
            AND YEAR(ad_fallback_2.measurement_taken_date) = %(gf2_fall_y)s AND MONTH(ad_fallback_2.measurement_taken_date) = %(gf2_fall_m)s 
            AND ad_fallback_2.weight_for_age_zscore IS NOT NULL AND ad_priority.childenrollguid IS NULL
    """

    # 3. Zig-Zag specific logic
    zz_joins = """
        INNER JOIN `tabAnthropromatic Data` AS ad_m1 ON ad_m1.childenrollguid = ad_current.childenrollguid AND ad_m1.do_you_have_height_weight = 1 AND YEAR(ad_m1.measurement_taken_date) = %(zz_m1_y)s AND MONTH(ad_m1.measurement_taken_date) = %(zz_m1_m)s AND ad_m1.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` AS ad_m2 ON ad_m2.childenrollguid = ad_current.childenrollguid AND ad_m2.do_you_have_height_weight = 1 AND YEAR(ad_m2.measurement_taken_date) = %(zz_m2_y)s AND MONTH(ad_m2.measurement_taken_date) = %(zz_m2_m)s AND ad_m2.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` AS ad_m3 ON ad_m3.childenrollguid = ad_current.childenrollguid AND ad_m3.do_you_have_height_weight = 1 AND YEAR(ad_m3.measurement_taken_date) = %(zz_m3_y)s AND MONTH(ad_m3.measurement_taken_date) = %(zz_m3_m)s AND ad_m3.weight_for_age_zscore IS NOT NULL
        INNER JOIN `tabAnthropromatic Data` AS ad_m4 ON ad_m4.childenrollguid = ad_current.childenrollguid AND ad_m4.do_you_have_height_weight = 1 AND YEAR(ad_m4.measurement_taken_date) = %(zz_m4_y)s AND MONTH(ad_m4.measurement_taken_date) = %(zz_m4_m)s AND ad_m4.weight_for_age_zscore IS NOT NULL
    """

    if api_mode == "gf1":
        joins.append(gf1_joins)
        conditions.append("(ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)")
        conditions.append("(COALESCE(ad_prev.weight_for_age_zscore, ad_fallback.weight_for_age_zscore) - ad_current.weight_for_age_zscore) > 0")

    elif api_mode == "gf1_plus":
        joins.append(gf1_joins)
        conditions.append("(ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)")
        conditions.append("(CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5")

    elif api_mode == "gf2":
        joins.append(gf2_joins)
        conditions.append("(ad_priority.weight_for_age_zscore IS NOT NULL OR ad_fallback_2.weight_for_age_zscore IS NOT NULL)")
        conditions.append("(CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback_2.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5")

    elif api_mode == "zig_zag":
        joins.append(zz_joins)
        conditions.append("cee.date_of_enrollment <= LAST_DAY(DATE_SUB(%(end_date)s, INTERVAL 4 MONTH))")
        conditions.append("""
            (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(
                CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)),
                CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))
            )) <= -0.5
        """)

    elif api_mode == "snc":
        # Left join everything for SNC
        joins.append(gf1_joins.replace("INNER JOIN", "LEFT JOIN"))
        joins.append(gf2_joins)
        joins.append(zz_joins.replace("INNER JOIN", "LEFT JOIN"))
        
        conditions.append("""
        (
            (
                (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
                AND (COALESCE(CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4))) - CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4))) > 0
            ) OR (
                (ad_prev.weight_for_age_zscore IS NOT NULL OR ad_fallback.weight_for_age_zscore IS NOT NULL)
                AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_prev.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
            ) OR (
                (ad_priority.weight_for_age_zscore IS NOT NULL OR ad_fallback_2.weight_for_age_zscore IS NOT NULL)
                AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - COALESCE(CAST(ad_priority.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_fallback_2.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
            ) OR (
                ad_m1.weight_for_age_zscore IS NOT NULL AND ad_m2.weight_for_age_zscore IS NOT NULL 
                AND ad_m3.weight_for_age_zscore IS NOT NULL AND ad_m4.weight_for_age_zscore IS NOT NULL
                AND (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) - GREATEST(CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)), CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)))) <= -0.5
                AND (
                    (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)) > CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                )
                AND (
                    (CAST(ad_current.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_m1.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_m2.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4))) OR (CAST(ad_m3.weight_for_age_zscore AS DECIMAL(10,4)) < CAST(ad_m4.weight_for_age_zscore AS DECIMAL(10,4)))
                )
            ) OR ad_current.weight_for_age = 1 OR ad_current.weight_for_height = 1
        )
        """)

    query = f"""
        SELECT {group_name_field} AS group_name, COUNT(DISTINCT ad_current.name) AS value
        FROM `tabAnthropromatic Data` AS ad_current
        {' '.join(joins)}
        WHERE {' AND '.join(conditions) if conditions else '1=1'}
        GROUP BY {group_name_field}
        ORDER BY group_name
    """
    
    base_conds_only = [
        "ad_current.do_you_have_height_weight = 1",
        "YEAR(cgm.measurement_date) = %(year)s",
        "MONTH(cgm.measurement_date) = %(month)s",
        "cee.date_of_enrollment <= %(end_date)s",
        "(cee.date_of_exit IS NULL OR cee.date_of_exit > %(start_date)s)"
    ] + base_conditions

    total_query = f"""
        SELECT {group_name_field} AS group_name, COUNT(DISTINCT cee.childenrollguid) AS total_measured
        FROM `tabAnthropromatic Data` AS ad_current
        INNER JOIN `tabChild Growth Monitoring` AS cgm ON cgm.name = ad_current.parent
        INNER JOIN `tabChild Enrollment and Exit` cee ON ad_current.childenrollguid = cee.childenrollguid
        INNER JOIN `tabCreche` AS cr ON cr.name = cgm.creche_id
        {' '.join(dim_joins)}
        WHERE {' AND '.join(base_conds_only) if base_conds_only else '1=1'}
        GROUP BY {group_name_field}
    """

    main_data = frappe.db.sql(query, params, as_dict=True)
    total_data = frappe.db.sql(total_query, params, as_dict=True)
    
    final_data = []
    main_map = {str(r.get("group_name", "Unknown")): int(r.get("value", 0)) for r in main_data}
    total_map = {str(r.get("group_name", "Unknown")): int(r.get("total_measured", 0)) for r in total_data}
    all_groups = set(total_map.keys()).union(set(main_map.keys()))
    
    for grp in sorted(list(all_groups)):
        final_data.append({
            "group_name": grp,
            "value": main_map.get(grp, 0),
            "total_measured": total_map.get(grp, 0)
        })
        
    return final_data

def gf_snc_core_query(kwargs, api_mode):
    """Orchestrates GF and SNC queries across months or groupings."""
    year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
    if not year or not month: return {"labels": [], "datasets": []}

    params_base = {}
    conditions = []

    # Filter logic execution
    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("cr.partner_id = %(partner_id)s")
        params_base["partner_id"] = partner_id

    append_geography_filters(kwargs, params_base, conditions, "cr")
    
    if kwargs.get("creche_id"):
        conditions.append("cr.name = %(creche_id)s")
        params_base["creche_id"] = kwargs.get("creche_id")

    if kwargs.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params_base["supervisor_id"] = kwargs.get("supervisor_id")

    if kwargs.get("c_status") or kwargs.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status)s")
        params_base["creche_status"] = kwargs.get("c_status") or kwargs.get("creche_status_id")

    if kwargs.get("phases"):
        phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params_base["phases"] = phases

    level = kwargs.get("level")
    dl_group = kwargs.get("drilldown_group")
    dl_level = kwargs.get("drilldown_level")

    dimension_map = {
        1: ("p", "`tabPartner`", "partner_id", "partner_name"),
        2: ("s", "`tabState`", "state_id", "state_name"),
        3: ("d", "`tabDistrict`", "district_id", "district_name"),
        4: ("b", "`tabBlock`", "block_id", "block_name"),
        5: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
        6: ("cr_dim", "`tabCreche`", "name", "creche_name"),
        7: ("u", "`tabUser`", "supervisor_id", "full_name")
    }

    tables_to_join = set()
    group_name_field = "'All Data'"
    is_month_wise = False

    if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(dl_level)]
        if int(dl_level) == 6:
            conditions.append("cr.name = %(drilldown_group)s")
        else:
            tables_to_join.add(int(dl_level))
            conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
        params_base["drilldown_group"] = dl_group
        level = None
        is_month_wise = True

    if level and str(level).isdigit() and int(level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(level)]
        if int(level) == 6:
            group_name_field = "cr.creche_name"
        else:
            tables_to_join.add(int(level))
            group_name_field = f"{prefix}.{field}"
    elif not level:
        is_month_wise = True

    dim_joins = []
    for tbl_id in tables_to_join:
        prefix, table, fk, field = dimension_map[tbl_id]
        if table == "`tabUser`":
            dim_joins.append(f"LEFT JOIN {table} {prefix} ON {prefix}.email = cr.{fk}")
        else:
            dim_joins.append(f"LEFT JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

    dataset_names = {
        "gf1": "Growth faltering 1", "gf1_plus": "Growth faltering 1+", 
        "gf2": "Growth faltering 2", "zig_zag": "Zig-Zag Pattern", "snc": "SNC"
    }
    label_name = dataset_names[api_mode]

    # Month-Wise Execution (Runs the query iteratively to ensure dynamic joins execute properly for each plotted month)
    if is_month_wise:
        duration = kwargs.get("duration", "12_months")
        offset = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}.get(duration, 11)
        
        start_date_dyn = date(year, month, 1) - relativedelta(months=offset)
        labels, values, totals = [], [], []

        for i in range(offset + 1):
            m_date = start_date_dyn + relativedelta(months=i)
            data = _execute_gf_single_month(m_date.year, m_date.month, api_mode, group_name_field, dim_joins, conditions, params_base)
            labels.append(m_date.strftime('%b-%Y').upper())
            values.append(int(data[0].get("value", 0)) if data else 0)
            totals.append(int(data[0].get("total_measured", 0)) if data else 0)

        return {
            "labels": labels, 
            "datasets": [{"name": label_name, "values": values}],
            "extra": {"Measurement Taken": totals}
        }

    # Cross Sectional Execution (Bar Chart Groupings)
    else:
        data = _execute_gf_single_month(year, month, api_mode, group_name_field, dim_joins, conditions, params_base)
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data],
            "datasets": [{"name": label_name, "values": [int(r.get("value", 0)) for r in data]}],
            "extra": {"Measurement Taken": [int(r.get("total_measured", 0)) for r in data]}
        }


# ------------- API Endpoints Wrapper ------------- #

@frappe.whitelist()
def get_gf_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_gf_data", params)
    def fetch_data(): return gf_snc_core_query(params, "gf1")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_gf_one_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_gf_one_data", params)
    def fetch_data(): return gf_snc_core_query(params, "gf1_plus")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_gf_two_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_gf_two_data", params)
    def fetch_data(): return gf_snc_core_query(params, "gf2")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_zig_zag_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_zig_zag_data", params)
    def fetch_data(): return gf_snc_core_query(params, "zig_zag")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_snc_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_snc_data", params)
    def fetch_data(): return gf_snc_core_query(params, "snc")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

# ==============================================================================
# COHORT APIs
# ==============================================================================

def _execute_cohort_single_month(target_year, target_month, api_mode, group_name_field, dim_joins, base_conditions, params_base):
    params = params_base.copy()
    params["year"] = target_year
    params["month"] = target_month
    end_date_first = date(target_year, target_month, 1)
    end_date_last = date(target_year, target_month, calendar.monthrange(target_year, target_month)[1])
    params["end_date_first"] = end_date_first
    params["end_date_last"] = end_date_last
    
    selected_indicator = params.get("indicator", "weight_for_age")
    gender = params.get("gender")
    
    case_expr = ""
    if api_mode == "md_nr":
        case_expr = "ad.initial_category = 'Moderate' AND ad.final_category = 'Normal'"
    elif api_mode == "sv_md":
        case_expr = "ad.initial_category = 'Severe' AND ad.final_category = 'Moderate'"
    elif api_mode == "sv_nr":
        case_expr = "ad.initial_category = 'Severe' AND ad.final_category = 'Normal'"
    elif api_mode == "total_recovery":
        case_expr = "(ad.initial_category = 'Moderate' AND ad.final_category = 'Normal') OR (ad.initial_category = 'Severe' AND ad.final_category = 'Moderate') OR (ad.initial_category = 'Severe' AND ad.final_category = 'Normal')"
    elif api_mode == "nr_md":
        case_expr = "ad.initial_category = 'Normal' AND ad.final_category = 'Moderate'"
    elif api_mode == "nr_sv":
        case_expr = "ad.initial_category = 'Normal' AND ad.final_category = 'Severe'"
    elif api_mode == "md_sv":
        case_expr = "ad.initial_category = 'Moderate' AND ad.final_category = 'Severe'"
    elif api_mode == "total_deterioration":
        case_expr = "(ad.initial_category = 'Normal' AND ad.final_category = 'Moderate') OR (ad.initial_category = 'Normal' AND ad.final_category = 'Severe') OR (ad.initial_category = 'Moderate' AND ad.final_category = 'Severe')"
    elif api_mode == "nr_nr":
        case_expr = "ad.initial_category = 'Normal' AND ad.final_category = 'Normal'"
    elif api_mode == "md_md":
        case_expr = "ad.initial_category = 'Moderate' AND ad.final_category = 'Moderate'"
    elif api_mode == "sv_sv":
        case_expr = "ad.initial_category = 'Severe' AND ad.final_category = 'Severe'"
    elif api_mode == "no_change":
        case_expr = "(ad.initial_category = 'Normal' AND ad.final_category = 'Normal') OR (ad.initial_category = 'Moderate' AND ad.final_category = 'Moderate') OR (ad.initial_category = 'Severe' AND ad.final_category = 'Severe')"
    
    select_expr = f"SUM(CASE WHEN {case_expr} AND ad.first_date != ad.last_date THEN 1 ELSE 0 END) AS value"
    
    gender_cond = f"AND cee.gender_id = %(gender)s" if gender else ""
    
    age_cond = ""
    ag = params.get("age_group")
    if ag == "6m-11m":
        age_cond = f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 6 AND 11"
    elif ag == "12m-17m":
        age_cond = f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 12 AND 17"
    elif ag == "18m-23m":
        age_cond = f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 18 AND 23"
    elif ag == "24m-29m":
        age_cond = f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 24 AND 29"
    elif ag == "30m-36m":
        age_cond = f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) BETWEEN 30 AND 36"
    elif ag == "> 36m":
        age_cond = f"AND TIMESTAMPDIFF(MONTH, cee.child_dob, %(end_date_first)s) > 36"
    
    query = f"""
        WITH RelevantChildren AS (
            SELECT childenrollguid, creche_id
            FROM `tabChild Enrollment and Exit` cee
            WHERE cee.date_of_enrollment <= %(end_date_last)s
            {gender_cond}
            {age_cond}
        ),
        AnthroStats AS (
            SELECT 
                a.childenrollguid,
                MIN(a.measurement_taken_date) as first_date,
                MAX(a.measurement_taken_date) as last_date,
                SUBSTRING_INDEX(GROUP_CONCAT(
                    CASE 
                        WHEN CAST(a.{selected_indicator}_zscore AS DECIMAL(10,2)) < -3 THEN 'Severe'
                        WHEN CAST(a.{selected_indicator}_zscore AS DECIMAL(10,2)) < -2 THEN 'Moderate'
                        ELSE 'Normal'
                    END 
                    ORDER BY a.measurement_taken_date ASC SEPARATOR ','
                ), ',', 1) as initial_category,
                SUBSTRING_INDEX(GROUP_CONCAT(
                    CASE 
                        WHEN CAST(a.{selected_indicator}_zscore AS DECIMAL(10,2)) < -3 THEN 'Severe'
                        WHEN CAST(a.{selected_indicator}_zscore AS DECIMAL(10,2)) < -2 THEN 'Moderate'
                        ELSE 'Normal'
                    END 
                    ORDER BY a.measurement_taken_date DESC SEPARATOR ','
                ), ',', 1) as final_category
            FROM `tabAnthropromatic Data` a
            INNER JOIN RelevantChildren rc ON rc.childenrollguid = a.childenrollguid
            WHERE a.do_you_have_height_weight = 1 
            AND a.{selected_indicator}_zscore IS NOT NULL
            AND TRIM(a.{selected_indicator}_zscore) <> ''
            AND a.measurement_taken_date <= %(end_date_last)s
            GROUP BY a.childenrollguid
        )
        SELECT {group_name_field} AS group_name, {select_expr}
        FROM `tabCreche` cr
        {' '.join(dim_joins)}
        LEFT JOIN RelevantChildren cee
            ON cee.creche_id = cr.name
        LEFT JOIN AnthroStats ad 
            ON ad.childenrollguid = cee.childenrollguid
        WHERE {' AND '.join(base_conditions) if base_conditions else '1=1'}
        GROUP BY {group_name_field}
        ORDER BY group_name
    """
    
    return frappe.db.sql(query, params, as_dict=True)

def cohort_core_query(kwargs, api_mode):
    year, month = int(kwargs.get("year", 0)), int(kwargs.get("month", 0))
    if not year or not month: return {"labels": [], "datasets": []}

    params_base = {}
    conditions = []

    partner_id = kwargs.get("partner_id") or frappe.db.get_value("User", frappe.session.user, "partner")
    if partner_id:
        conditions.append("cr.partner_id = %(partner_id)s")
        params_base["partner_id"] = partner_id

    append_geography_filters(kwargs, params_base, conditions, "cr")
    
    if kwargs.get("creche_id"):
        conditions.append("cr.name = %(creche_id)s")
        params_base["creche_id"] = kwargs.get("creche_id")

    if kwargs.get("supervisor_id"):
        conditions.append("cr.supervisor_id = %(supervisor_id)s")
        params_base["supervisor_id"] = kwargs.get("supervisor_id")

    if kwargs.get("c_status") or kwargs.get("creche_status_id"):
        conditions.append("cr.creche_status_id = %(creche_status)s")
        params_base["creche_status"] = kwargs.get("c_status") or kwargs.get("creche_status_id")

    if kwargs.get("phases"):
        phases = tuple(p.strip() for p in kwargs.get("phases").split(",") if p.strip().isdigit())
        if phases:
            conditions.append("cr.phase IN %(phases)s")
            params_base["phases"] = phases

    level = kwargs.get("level")
    dl_group = kwargs.get("drilldown_group")
    dl_level = kwargs.get("drilldown_level")

    dimension_map = {
        1: ("p", "`tabPartner`", "partner_id", "partner_name"),
        2: ("s", "`tabState`", "state_id", "state_name"),
        3: ("d", "`tabDistrict`", "district_id", "district_name"),
        4: ("b", "`tabBlock`", "block_id", "block_name"),
        5: ("g", "`tabGram Panchayat`", "gp_id", "gp_name"),
        6: ("cr_dim", "`tabCreche`", "name", "creche_name"),
        7: ("u", "`tabUser`", "supervisor_id", "full_name")
    }

    tables_to_join = set()
    group_name_field = "'All Data'"
    is_month_wise = False

    if dl_group and dl_level and str(dl_level).isdigit() and int(dl_level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(dl_level)]
        if int(dl_level) == 6:
            conditions.append("cr.name = %(drilldown_group)s")
        else:
            tables_to_join.add(int(dl_level))
            conditions.append(f"{prefix}.{field} = %(drilldown_group)s")
        params_base["drilldown_group"] = dl_group
        level = None
        is_month_wise = True

    if level and str(level).isdigit() and int(level) in dimension_map:
        prefix, table, fk, field = dimension_map[int(level)]
        if int(level) == 6:
            group_name_field = "cr.creche_name"
        else:
            tables_to_join.add(int(level))
            group_name_field = f"{prefix}.{field}"
    elif not level:
        is_month_wise = True

    dim_joins = []
    for tbl_id in tables_to_join:
        prefix, table, fk, field = dimension_map[tbl_id]
        if table == "`tabUser`":
            dim_joins.append(f"LEFT JOIN {table} {prefix} ON {prefix}.email = cr.{fk}")
        else:
            dim_joins.append(f"LEFT JOIN {table} {prefix} ON {prefix}.name = cr.{fk}")

    dataset_names = {
        "md_nr": "Moderate to Normal",
        "sv_md": "Severe to Moderate",
        "sv_nr": "Severe to Normal",
        "total_recovery": "Total Recovery",
        "nr_md": "Normal to Moderate",
        "nr_sv": "Normal to Severe",
        "md_sv": "Moderate to Severe",
        "total_deterioration": "Total Deterioration",
        "nr_nr": "Normal to Normal",
        "md_md": "Moderate to Moderate",
        "sv_sv": "Severe to Severe",
        "no_change": "No Change"
    }
    label_name = dataset_names[api_mode]
    params_base["indicator"] = kwargs.get("indicator", "weight_for_age")
    params_base["gender"] = kwargs.get("gender")
    params_base["age_group"] = kwargs.get("age_group")

    if is_month_wise:
        duration = kwargs.get("duration", "12_months")
        offset = {"3_months": 2, "6_months": 5, "9_months": 8, "12_months": 11}.get(duration, 11)
        
        start_date_dyn = date(year, month, 1) - relativedelta(months=offset)
        labels, values = [], []

        for i in range(offset + 1):
            m_date = start_date_dyn + relativedelta(months=i)
            data = _execute_cohort_single_month(m_date.year, m_date.month, api_mode, group_name_field, dim_joins, conditions, params_base)
            labels.append(m_date.strftime('%b-%Y').upper())
            values.append(int(data[0].get("value", 0)) if data else 0)

        return {
            "labels": labels, 
            "datasets": [{"name": label_name, "values": values}]
        }
    else:
        data = _execute_cohort_single_month(year, month, api_mode, group_name_field, dim_joins, conditions, params_base)
        return {
            "labels": [str(r.get("group_name", "Unknown")) for r in data],
            "datasets": [{"name": label_name, "values": [int(r.get("value", 0)) for r in data]}]
        }

@frappe.whitelist()
def get_cohort_moderate_to_normal(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_moderate_to_normal", params)
    def fetch_data(): return cohort_core_query(params, "md_nr")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_severe_to_moderate(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_severe_to_moderate", params)
    def fetch_data(): return cohort_core_query(params, "sv_md")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_severe_to_normal(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_severe_to_normal", params)
    def fetch_data(): return cohort_core_query(params, "sv_nr")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_total_recovery(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_total_recovery", params)
    def fetch_data(): return cohort_core_query(params, "total_recovery")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_normal_to_moderate(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_normal_to_moderate", params)
    def fetch_data(): return cohort_core_query(params, "nr_md")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_normal_to_severe(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_normal_to_severe", params)
    def fetch_data(): return cohort_core_query(params, "nr_sv")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_moderate_to_severe(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_moderate_to_severe", params)
    def fetch_data(): return cohort_core_query(params, "md_sv")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_total_deterioration(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_total_deterioration", params)
    def fetch_data(): return cohort_core_query(params, "total_deterioration")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_normal_to_normal(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_normal_to_normal", params)
    def fetch_data(): return cohort_core_query(params, "nr_nr")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_moderate_to_moderate(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_moderate_to_moderate", params)
    def fetch_data(): return cohort_core_query(params, "md_md")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_severe_to_severe(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_severe_to_severe", params)
    def fetch_data(): return cohort_core_query(params, "sv_sv")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_cohort_no_change(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_cohort_no_change", params)
    def fetch_data(): return cohort_core_query(params, "no_change")
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data, shared=True)

# ==============================================================================
# CRECHE PROFILE APIs
# ==============================================================================

def build_creche_categorical_query(kwargs, categories, is_snapshot=True):
    """
    categories: dict of { 'Dataset Name': 'SQL condition' }
    """
    _, e, y, m = _date_range(kwargs)
    params = {"end_date": e}
    conds = []

    _geo_filters(kwargs, params, conds, "cr")
    _common_creche_filters(kwargs, params, conds, "cr")

    grp, dim_joins, order, is_mw = _resolve_dim(
        kwargs, conds, params, "cr.creche_opening_date"
    )

    if "cr.creche_opening_date IS NOT NULL" not in conds:
        conds.append("cr.creche_opening_date IS NOT NULL")

    if not is_mw or not is_snapshot:
        select_parts = []
        for cat_name, cat_cond in categories.items():
            select_parts.append(f"SUM(CASE WHEN {cat_cond} THEN 1 ELSE 0 END) AS `{cat_name}`")

        select_sql = ", ".join(select_parts)
        where_sql = " AND ".join(conds) if conds else "1=1"

        query = f"""
            SELECT
                {grp} AS group_name,
                {select_sql}
            FROM `tabCreche` cr
            {dim_joins}
            WHERE {where_sql}
            GROUP BY {grp}
            {order}
        """

        data = frappe.db.sql(query, params, as_dict=True)

        if is_mw:
            off = OFFSET_MAP.get(kwargs.get("duration", "12_months"), 11)
            start = date(y, m, 1) - relativedelta(months=off)
            labels = [(start + relativedelta(months=i)).strftime("%b-%Y").upper() for i in range(off + 1)]
            
            filled_data = []
            val_map = {str(r.get("group_name", "")).upper(): r for r in data}
            for lbl in labels:
                row = {"group_name": lbl}
                for cat_name in categories.keys():
                    row[cat_name] = int(val_map.get(lbl, {}).get(cat_name, 0))
                filled_data.append(row)
            data = filled_data
        else:
            labels = [str(r.get("group_name", "Unknown")) for r in data]
            
    else:
        # CUMULATIVE MONTH-WISE SNAPSHOT
        off = OFFSET_MAP.get(kwargs.get("duration", "12_months"), 11)
        start = date(y, m, 1) - relativedelta(months=off)
        labels_dates = [
            (start + relativedelta(months=i), start + relativedelta(months=i) + relativedelta(months=1) - relativedelta(days=1)) 
            for i in range(off + 1)
        ]
        labels = [d[0].strftime("%b-%Y").upper() for d in labels_dates]
        
        data = []
        for month_start, month_end in labels_dates:
            mw_conds = conds.copy()
            mw_conds.append(f"cr.creche_opening_date <= '{month_end.strftime('%Y-%m-%d')}'")
            where_sql = " AND ".join(mw_conds)
            
            select_parts = []
            for cat_name, cat_cond in categories.items():
                cat_cond_mw = cat_cond.replace('CURDATE()', f"'{month_end.strftime('%Y-%m-%d')}'")
                select_parts.append(f"SUM(CASE WHEN {cat_cond_mw} THEN 1 ELSE 0 END) AS `{cat_name}`")
            select_sql = ", ".join(select_parts)
            
            query = f"""
                SELECT {select_sql}
                FROM `tabCreche` cr
                {dim_joins}
                WHERE {where_sql}
            """
            month_data = frappe.db.sql(query, params, as_dict=True)
            row = {"group_name": month_start.strftime("%b-%Y").upper()}
            if month_data and month_data[0]:
                for cat_name in categories.keys():
                    row[cat_name] = int(month_data[0].get(cat_name) or 0)
            else:
                for cat_name in categories.keys():
                    row[cat_name] = 0
            data.append(row)

    datasets = []
    for cat_name in categories.keys():
        datasets.append({
            "name": cat_name,
            "values": [int(r.get(cat_name, 0)) for r in data]
        })

    return {
        "labels": labels,
        "datasets": datasets
    }


@frappe.whitelist()
def get_creche_status_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    params.pop('c_status', None)
    params.pop('creche_status_id', None)
    cache_key = get_cache_key("get_creche_status_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Planned': 'cr.creche_status_id = 1',
            'Plan Dropped': 'cr.creche_status_id = 2',
            'Active / Operational': 'cr.creche_status_id = 3',
            'Closed': 'cr.creche_status_id = 4'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_gender_wise_distribution(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_gender_wise_distribution", params)
    def fetch_data():
        query = """
        SELECT
            CASE
                WHEN cee.gender_id = 1 THEN 'Male'
                WHEN cee.gender_id = 2 THEN 'Female'
                WHEN cee.gender_id = 3 THEN 'Other'
                ELSE 'Unknown'
            END AS gender,
            COUNT(*) AS total_children
        FROM `tabChild Enrollment and Exit` cee
        GROUP BY cee.gender_id
        ORDER BY cee.gender_id;
        """
        data = frappe.db.sql(query, as_dict=True)
        labels = [r.get("gender") for r in data]
        values = [r.get("total_children") for r in data]
        return {
            "labels": labels,
            "datasets": [{"name": "Gender-wise Distribution", "values": values}]
        }
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_age_wise_distribution(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_age_wise_distribution", params)
    def fetch_data():
        query = """
        SELECT
            CASE
                WHEN age_months <= 6 THEN '0-6 Month'
                WHEN age_months <= 12 THEN '7-12 Month'
                WHEN age_months <= 18 THEN '13-18 Month'
                WHEN age_months <= 24 THEN '19-24 Month'
                WHEN age_months <= 30 THEN '25-30 Month'
                WHEN age_months <= 36 THEN '31-36 Month'
                ELSE 'Above 36 Month'
            END AS age_group,
            COUNT(*) AS total_children
        FROM (
            SELECT TIMESTAMPDIFF(MONTH, child_dob, CURDATE()) AS age_months
            FROM `tabChild Enrollment and Exit`
            WHERE child_dob IS NOT NULL
        ) t
        GROUP BY age_group
        ORDER BY
            CASE age_group
                WHEN '0-6 Month' THEN 1
                WHEN '7-12 Month' THEN 2
                WHEN '13-18 Month' THEN 3
                WHEN '19-24 Month' THEN 4
                WHEN '25-30 Month' THEN 5
                WHEN '31-36 Month' THEN 6
                WHEN 'Above 36 Month' THEN 7
            END;
        """
        data = frappe.db.sql(query, as_dict=True)
        labels = [r.get("age_group") for r in data]
        values = [r.get("total_children") for r in data]
        return {
            "labels": labels,
            "datasets": [{"name": "Age-wise Distribution", "values": values}]
        }
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_creche_inauguration_trend_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_creche_inauguration_trend_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Inaugurated Creches': '1=1'
        }, is_snapshot=False)
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_type_of_creche_house_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_type_of_creche_house_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Rented House': 'cr.type_of_creche_house = 1',
            'Community Hall': 'cr.type_of_creche_house = 2',
            'Old School Building': 'cr.type_of_creche_house = 3',
            'Any Other': 'cr.type_of_creche_house = 4'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_type_of_building_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_type_of_building_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Kaccha': 'cr.type_of_building = 1',
            'Pakka': 'cr.type_of_building = 2'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_hard_to_reach_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_hard_to_reach_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Yes': 'cr.hard_to_reach = 1',
            'No': 'cr.hard_to_reach = 0'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_roof_type_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_roof_type_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Asbestos': 'cr.roof_type = 1',
            'Tin': 'cr.roof_type = 2',
            'Cemented': 'cr.roof_type = 3',
            'Khapra (Tile)': 'cr.roof_type = 4'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_source_of_power_supply_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_source_of_power_supply_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Electricity': 'cr.source_of_power_supply = 1',
            'Electricity + Inverter': 'cr.source_of_power_supply = 2',
            'Solar': 'cr.source_of_power_supply = 3'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_equipped_with_lightning_arrestor_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_equipped_with_lightning_arrestor_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Yes': 'cr.equipped_with_lightening_arrestor = 1',
            'No': 'cr.equipped_with_lightening_arrestor = 0'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_age_wise_creche_distribution_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_age_wise_creche_distribution_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Below 6 Months': 'TIMESTAMPDIFF(MONTH, cr.creche_opening_date, CURDATE()) < 6',
            '6-12 Months': 'TIMESTAMPDIFF(MONTH, cr.creche_opening_date, CURDATE()) BETWEEN 6 AND 11',
            '12-18 Months': 'TIMESTAMPDIFF(MONTH, cr.creche_opening_date, CURDATE()) BETWEEN 12 AND 17',
            '18-24 Months': 'TIMESTAMPDIFF(MONTH, cr.creche_opening_date, CURDATE()) BETWEEN 18 AND 23',
            'Above 24 Months': 'TIMESTAMPDIFF(MONTH, cr.creche_opening_date, CURDATE()) >= 24'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_independent_kitchen_room_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_independent_kitchen_room_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Yes': 'cr.independent_kitche_room = 1',
            'No': 'cr.independent_kitche_room = 0'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)

@frappe.whitelist()
def get_equipped_with_operational_toilet_data(**kwargs):
    params = frappe.form_dict.copy() if frappe.form_dict else kwargs
    cache_key = get_cache_key("get_equipped_with_operational_toilet_data", params)
    def fetch_data():
        return build_creche_categorical_query(params, {
            'Yes': 'cr.equipped_with_operational_toilet = 1',
            'No': 'cr.equipped_with_operational_toilet = 0'
        })
    frappe.response["data"] = frappe.cache().get_value(cache_key, fetch_data)