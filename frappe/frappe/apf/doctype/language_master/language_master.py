# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class LanguageMaster(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		english_label: DF.Data | None
		is_active: DF.Check
		language_name: DF.Data | None
		language_name_hi: DF.Data | None
		language_name_kn: DF.Data | None
		language_name_od: DF.Data | None
		language_name_tn: DF.Data | None
		name: DF.Int | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
