# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Relation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		is_active: DF.Check
		name: DF.Int | None
		relation_hi: DF.Data | None
		relation_kn: DF.Data | None
		relation_name: DF.Data | None
		relation_od: DF.Data | None
		relation_tn: DF.Data | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
