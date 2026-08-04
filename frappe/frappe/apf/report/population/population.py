
import frappe
from frappe import _
from datetime import date

def execute(filters=None):
    columns = get_columns()
    data = get_summary_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 120},
        {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 120},
        {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 120},
        {"label": _("Gram Panchayat"), "fieldname": "gram_panchayat", "fieldtype": "Data", "width": 120},
        {"label": _("Village"), "fieldname": "village", "fieldtype": "Data", "width": 120},
        {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 150},
        {"label": _("Creche Name"), "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
        {"label": _("Population Q1(Jan-Mar)"), "fieldname": "population_q1", "fieldtype": "Int", "width": 200},
        {"label": _("Population Q2(April-June)"), "fieldname": "population_q2", "fieldtype": "Int", "width": 200},
        {"label": _("Population Q3(July-Sept)"), "fieldname": "population_q3", "fieldtype": "Int", "width": 200},
        {"label": _("Population Q4(Oct-Dec)"), "fieldname": "population_q4", "fieldtype": "Int", "width": 200}
    ]

def get_summary_data(filters=None):
    if not filters:
        filters = {}

    conditions = []
    values = {}

    # Passing raw year directly to let SQL CASE statement handle the mapping
    year = filters.get("year", str(date.today().year))
    values["year"] = int(year)

    # Dynamically build standard link filters
    filter_map = {
        "partner": "c.partner_id",
        "state": "c.state_id",
        "district": "c.district_id",
        "block": "c.block_id",
        "gp": "c.gp_id",
        "creche": "c.name",
        "supervisor_id": "c.supervisor_id",
        "creche_status_id": "c.creche_status_id"
    }

    for filter_key, db_field in filter_map.items():
        if filters.get(filter_key):
            conditions.append(f"{db_field} = %({filter_key})s")
            values[filter_key] = filters.get(filter_key)

    # Handle 'phases' MultiSelect filter properly
    if filters.get("phases"):
        phases = filters.get("phases")
        if isinstance(phases, str):
            phases = [x.strip() for x in phases.split(",")]
        if phases:
            conditions.append("c.phase IN %(phases)s")
            values["phases"] = tuple(phases)

    # Assemble final WHERE clause string
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT 
            p.partner_name AS partner,
            s.state_name AS state,
            d.district_name AS district,
            b.block_name AS block,
            gp.gp_name AS gram_panchayat,
            v.village_name AS village,
            u.full_name AS supervisor,        
            c.creche_name AS creche_name,

            COALESCE(demo_counts.population_q1, 0) AS population_q1,
            COALESCE(demo_counts.population_q2, 0) AS population_q2,
            COALESCE(demo_counts.population_q3, 0) AS population_q3,
            COALESCE(demo_counts.population_q4, 0) AS population_q4

        FROM `tabCreche` c

        LEFT JOIN `tabPartner` p ON c.partner_id = p.name
        LEFT JOIN `tabState` s ON c.state_id = s.name
        LEFT JOIN `tabDistrict` d ON c.district_id = d.name
        LEFT JOIN `tabBlock` b ON c.block_id = b.name
        LEFT JOIN `tabGram Panchayat` gp ON c.gp_id = gp.name
        LEFT JOIN `tabVillage` v ON c.village_id = v.name
        LEFT JOIN `tabUser` u ON c.supervisor_id = u.name  

        LEFT JOIN (
            SELECT 
                v_inner.name AS village_id,
                COALESCE(SUM(dd.population_q1), 0) AS population_q1,
                COALESCE(SUM(dd.population_q2), 0) AS population_q2,
                COALESCE(SUM(dd.population_q3), 0) AS population_q3,
                COALESCE(SUM(dd.population_q4), 0) AS population_q4
            FROM `tabDemographic Details` dd
            INNER JOIN `tabVillage` v_inner ON dd.parent = v_inner.name
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
            GROUP BY v_inner.name
        ) AS demo_counts ON demo_counts.village_id = c.village_id

        {where_clause}
    """

    # Actually execute the query against the database
    return frappe.db.sql(query, values, as_dict=True)










# import frappe
# from frappe import _
# from datetime import date

# def execute(filters=None):
#     columns = get_columns()
#     data = get_summary_data(filters)
#     return columns, data

# def get_columns():
#     return [
#         {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 120},
#         {"label": _("Partner"), "fieldname": "partner", "fieldtype": "Data", "width": 120},
#         {"label": _("District"), "fieldname": "district", "fieldtype": "Data", "width": 120},
#         {"label": _("Block"), "fieldname": "block", "fieldtype": "Data", "width": 120},
#         {"label": _("Gram Panchayat"), "fieldname": "gram_panchayat", "fieldtype": "Data", "width": 120},
#         {"label": _("Village"), "fieldname": "village", "fieldtype": "Data", "width": 120},
#         {"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Data", "width": 150},
#         {"label": _("Creche Name"), "fieldname": "creche_name", "fieldtype": "Data", "width": 150},
#         {"label": _("Population Q1(Jan-Mar)"), "fieldname": "population_q1", "fieldtype": "Int", "width": 200},
#         {"label": _("Population Q2(April-June)"), "fieldname": "population_q2", "fieldtype": "Int", "width": 200},
#         {"label": _("Population Q3(July-Sept)"), "fieldname": "population_q3", "fieldtype": "Int", "width": 200},
#         {"label": _("Population Q4(Oct-Dec)"), "fieldname": "population_q4", "fieldtype": "Int", "width": 200}
#     ]



# def get_summary_data(filters=None):
#     if not filters:
#         filters = {}

#     conditions = []
#     values = {}

#     # Map selected Year to internal year_id for Demographic Details
#     year = filters.get("year", str(date.today().year))
#     year_map = {"2027": 8, "2026": 7, "2025": 6, "2024": 5, "2023": 4, "2022": 3, "2021": 2, "2020": 1}
#     values["year_id"] = year_map.get(str(year), 0)

#     # Dynamically build standard link filters
#     filter_map = {
#         "partner": "c.partner_id",
#         "state": "c.state_id",
#         "district": "c.district_id",
#         "block": "c.block_id",
#         "gp": "c.gp_id",
#         "creche": "c.name",
#         "supervisor_id": "c.supervisor_id",
#         "creche_status_id": "c.creche_status_id"
#     }

#     for filter_key, db_field in filter_map.items():
#         if filters.get(filter_key):
#             conditions.append(f"{db_field} = %({filter_key})s")
#             values[filter_key] = filters.get(filter_key)

#     # Handle 'phases' MultiSelect filter properly
#     if filters.get("phases"):
#         phases = filters.get("phases")
#         if isinstance(phases, str):
#             phases = [x.strip() for x in phases.split(",")]
#         if phases:
#             conditions.append("c.phase IN %(phases)s")
#             values["phases"] = tuple(phases)

#     # Assemble final WHERE clause string
#     where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

#     query = f"""
#         SELECT 
#             p.partner_name AS partner,
#             s.state_name AS state,
#             d.district_name AS district,
#             b.block_name AS block,
#             gp.gp_name AS gram_panchayat,
#             v.village_name AS village,
#             u.full_name AS supervisor,         
#             c.creche_name AS creche_name,

#             COALESCE(dc.population_q1, 0) AS population_q1,
#             COALESCE(dc.population_q2, 0) AS population_q2,
#             COALESCE(dc.population_q3, 0) AS population_q3,
#             COALESCE(dc.population_q4, 0) AS population_q4

#         FROM `tabCreche` c

#         LEFT JOIN `tabPartner` p ON c.partner_id = p.name
#         LEFT JOIN `tabState` s ON c.state_id = s.name
#         LEFT JOIN `tabDistrict` d ON c.district_id = d.name
#         LEFT JOIN `tabBlock` b ON c.block_id = b.name
#         LEFT JOIN `tabGram Panchayat` gp ON c.gp_id = gp.name
#         LEFT JOIN `tabVillage` v ON c.village_id = v.name
#         LEFT JOIN `tabUser` u ON c.supervisor_id = u.name  

#         LEFT JOIN (
#             SELECT 
#                 dd.parent AS village_id,
#                 SUM(dd.population_q1) AS population_q1,
#                 SUM(dd.population_q2) AS population_q2,
#                 SUM(dd.population_q3) AS population_q3,
#                 SUM(dd.population_q4) AS population_q4
#             FROM `tabDemographic Details` dd
#             WHERE dd.year_id = %(year_id)s
#             GROUP BY dd.parent
#         ) dc ON dc.village_id = c.village_id

#         {where_clause}
#     """

#     # Actually execute the query against the database
#     return frappe.db.sql(query, values, as_dict=True)