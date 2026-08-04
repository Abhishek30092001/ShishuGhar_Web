# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class YesNoobserved(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		name: DF.Int | None
		seq_id: DF.Int
		yes_no_note_observed: DF.Data | None
		yes_no_note_observed_hi: DF.Data | None
		yes_no_note_observed_kn: DF.Data | None
		yes_no_note_observed_od: DF.Data | None
		yes_no_note_observed_tn: DF.Data | None
	# end: auto-generated types

	pass
