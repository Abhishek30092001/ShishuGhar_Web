# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HHChildStatus(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		hh_child_status: DF.Data | None
		hh_child_status_hi: DF.Data | None
		hh_child_status_kn: DF.Data | None
		hh_child_status_od: DF.Data | None
		hh_child_status_tn: DF.Data | None
		name: DF.Int | None
		seq_no: DF.Int
	# end: auto-generated types

	pass
