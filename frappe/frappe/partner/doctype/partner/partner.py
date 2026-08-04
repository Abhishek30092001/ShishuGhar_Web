# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Partner(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.creche_module.doctype.partner_state.partner_state import PartnerState
		from frappe.types import DF

		date_of_joining: DF.Date | None
		is_active: DF.Check
		name: DF.Int | None
		partner_code: DF.Data
		partner_kn: DF.Data | None
		partner_name: DF.Data
		partner_state: DF.Table[PartnerState]
		partner_tn: DF.Data | None
	# end: auto-generated types

	pass
