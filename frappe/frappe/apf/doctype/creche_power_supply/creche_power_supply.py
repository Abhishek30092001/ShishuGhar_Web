# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CrechePowerSupply(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		creche_power_supply_data: DF.Data | None
		creche_power_supply_data_hi: DF.Data | None
		creche_power_supply_data_kn: DF.Data | None
		creche_power_supply_data_od: DF.Data | None
		creche_power_supply_data_tn: DF.Data | None
		name: DF.Int | None
		seq_id: DF.Int
	# end: auto-generated types

	pass
