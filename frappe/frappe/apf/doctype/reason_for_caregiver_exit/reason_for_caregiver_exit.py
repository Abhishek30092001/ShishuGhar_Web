# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Reasonforcaregiverexit(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		caregiver_exit: DF.Data | None
		caregiver_exit_tn: DF.Data | None
		is_active: DF.Check
		name: DF.Int | None
		reason_for_caregiver_exit_kn: DF.Data | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
