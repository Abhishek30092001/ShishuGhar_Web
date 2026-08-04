# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RoofType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		name: DF.Int | None
		roof_type_data: DF.Data | None
		roof_type_data_hi: DF.Data | None
		roof_type_data_kn: DF.Data | None
		roof_type_data_od: DF.Data | None
		roof_type_data_tn: DF.Data | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
