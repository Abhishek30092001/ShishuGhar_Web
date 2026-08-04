# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class FireExtinguisher(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		block_id: DF.Link | None
		creche_id: DF.Link | None
		date_of_delivery: DF.Date | None
		date_of_expiry: DF.Date | None
		district_id: DF.Link | None
		fire_extingusher_status: DF.Literal["", "Available", "Not Available", "Gone for Refilling", "Other"]
		gp_id: DF.Link | None
		name: DF.Int | None
		other: DF.Data | None
		partner_id: DF.Link | None
		state_id: DF.Link | None
		village_id: DF.Link | None
	# end: auto-generated types

	pass
