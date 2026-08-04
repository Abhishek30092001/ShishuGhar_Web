# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SafetyIndicators(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		appcreated_by: DF.Data | None
		appupdated_by: DF.Data | None
		are_sharp_edge_cutters_or_machinery_kept_away_from_the_creche: DF.Link
		block_id: DF.Link
		confident_handling_pressure_cooker: DF.Link
		confident_handling_pressure_cooker_other: DF.Data | None
		creche_id: DF.Link
		creche_running_two_caregivers: DF.Link
		creche_running_two_caregivers_other: DF.Data | None
		creche_secured_against_animals: DF.Link
		creche_secured_against_animals_other: DF.Data | None
		date_of_visit: DF.Date
		district_id: DF.Link
		edge_cutters_or_machinery_kept_away_from_the_creche_other: DF.Data | None
		egg_floating_tests_doneperiodically_check_quality_eggs: DF.Link
		egg_floating_tests_doneperiodically_check_quality_eggs_other: DF.Data | None
		electrical_connections_positioned_out_children_reach: DF.Link
		electrical_connections_positioned_out_children_reach_other: DF.Data | None
		emergency_contact_numbers_clearly_displayed: DF.Link
		emergency_contact_numbers_clearly_displayed_other: DF.Data | None
		entry_time: DF.Time | None
		exit_time: DF.Time | None
		external_fencing_around: DF.Link
		external_fencing_around_other: DF.Data | None
		fans_and_lights_installed_safe_location_height: DF.Link
		fans_and_lights_installed_safe_location_height_other: DF.Data | None
		fire_extinguisher_available_working_condition: DF.Link
		fire_extinguisher_available_working_condition_other: DF.Data | None
		first_aid_available_creche: DF.Link
		first_aid_available_creche_other: DF.Data | None
		food_utilized_first_out_manner: DF.Link
		food_utilized_first_out_manner_other: DF.Data | None
		gp_id: DF.Link
		is_any_welltube_well_within_20_m_radius_of_the_creche: DF.Link
		is_any_welltube_well_within_20_m_radius_of_the_creche_other: DF.Data | None
		is_leftover_food_disposed_of_properly_every_day: DF.Link
		is_leftover_food_disposed_of_properly_every_day_other: DF.Data | None
		is_the_creche_protected_from_rainwater_leakage: DF.Link
		is_the_creche_protected_from_rainwater_leakage_other: DF.Data | None
		is_the_structural_safety_of_the_creches_roof_and_walls_ensured: DF.Link
		kitchen_fire_related_emergencies: DF.Link
		kitchen_fire_related_emergencies_other: DF.Data | None
		lightening_installed_creche: DF.Link
		lightening_installed_creche_other: DF.Data | None
		name: DF.Int | None
		parents_recorded_visitor_register: DF.Link
		parents_recorded_visitor_register_other: DF.Data | None
		partner_id: DF.Link
		positioned_above_cylinder_height: DF.Link
		positioned_above_cylinder_height_other: DF.Data | None
		properly_covered_with_iron_net_inside_out_side: DF.Link | None
		properly_covered_with_iron_net_inside_out_side_other: DF.Data | None
		safety_gate_kitchen_entrance: DF.Link
		safety_gate_kitchen_entrance_other: DF.Data | None
		safety_the_main_entrance: DF.Link
		safety_the_main_entrance_other: DF.Data | None
		smguid: DF.Data | None
		solar_batteries_kept_out_children_reach: DF.Link
		solar_batteries_kept_out_children_reach_other: DF.Data | None
		state_id: DF.Link
		structural_safety_of_the_creches_roof_and_walls_ensured_other: DF.Data | None
		village_id: DF.Link
		water_filter_being_safe_drinking_water: DF.Link
		water_filter_being_safe_drinking_water_other: DF.Data | None
	# end: auto-generated types

	pass
