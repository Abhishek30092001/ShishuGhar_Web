# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrecheBuildingType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		creche_building_type_data: DF.Data | None
		creche_building_type_hi: DF.Data | None
		creche_building_type_kn: DF.Data | None
		creche_building_type_od: DF.Data | None
		creche_building_type_tn: DF.Data | None
		name: DF.Int | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
