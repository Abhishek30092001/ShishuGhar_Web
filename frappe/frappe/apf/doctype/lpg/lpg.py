# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LPG(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		block_id: DF.Link
		creche_id: DF.Link
		current_source_of_fuel: DF.Literal["", "Wood", "LPG", "Induction", "Smokeless Chulha", "Other"]
		date_of_supply: DF.Date
		district_id: DF.Link
		gp_id: DF.Link
		if_lpg_what_type: DF.Literal["", "Commercial", "Domestic"]
		name: DF.Int | None
		other: DF.Data | None
		partner_id: DF.Link
		state_id: DF.Link
		supplied_fuel_source: DF.Literal["", "Wood", "LPG", "Induction"]
		village_id: DF.Link
	# end: auto-generated types

	pass
