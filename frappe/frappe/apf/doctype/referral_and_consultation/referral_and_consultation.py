# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ReferralandConsultation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.referral_reason_child_table.referral_reason_child_table import ReferralReasonchildtable
		from frappe.types import DF

		app_updated_by: DF.Data | None
		app_updated_on: DF.Data | None
		appcreated_by: DF.Data | None
		appcreated_on: DF.Data | None
		block_id: DF.Link
		cgmguid: DF.Data | None
		child_id: DF.Data | None
		child_name: DF.Data | None
		child_status: DF.Int
		childenrollguid: DF.Data | None
		creche_id: DF.Link
		date_of_identification: DF.Date | None
		date_of_referral: DF.Date | None
		district_id: DF.Link
		gender_id: DF.Link | None
		gp_id: DF.Link
		haz_at_identification: DF.Data | None
		haz_at_identification_cat: DF.Float
		heightlength_at_growth_monitoring_cm: DF.Float
		if_noother: DF.Data | None
		if_noreason: DF.TableMultiSelect[ReferralReasonchildtable]
		if_other: DF.Data | None
		name: DF.Int | None
		name_of_the_condition: DF.Data | None
		parent_counseling_done_before_referral: DF.Check
		parents_consented_to_visit_a_doctor: DF.Check
		partner_id: DF.Link
		r_c_guid: DF.Data | None
		referral_to: DF.Link | None
		schedule_date: DF.Data | None
		sick_condition_present: DF.Check
		state_id: DF.Link
		village_id: DF.Link
		visit_count: DF.Int
		waz_at_identification: DF.Data | None
		waz_at_identification_cat: DF.Float
		weight_at_growth_monitoring_kg: DF.Float
		whz_at_identification: DF.Data | None
		whz_at_identification_cat: DF.Float
	# end: auto-generated types

	pass
