# Copyright (c) 2025, Frappe Technologies and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Training(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.apf.doctype.caregiver_training.caregiver_training import CaregiverTraining
		from frappe.apf.doctype.organisations_training.organisations_training import Organisationstraining
		from frappe.apf.doctype.topic_multiselect.topic_multiselect import Topicmultiselect
		from frappe.apf.doctype.training_participants_others.training_participants_others import TrainingParticipantsOthers
		from frappe.types import DF

		batch_end_date: DF.Date | None
		batch_no: DF.Data | None
		batch_start_date: DF.Date
		created_at: DF.Data | None
		created_by: DF.Data | None
		creche_caregivers: DF.Table[CaregiverTraining]
		creche_id: DF.Link
		name: DF.Int | None
		organisations_giving_training: DF.TableMultiSelect[Organisationstraining]
		other_participants: DF.Table[TrainingParticipantsOthers]
		partner_id: DF.Link
		topic_covered: DF.TableMultiSelect[Topicmultiselect]
		training_of: DF.Literal["All", "Creche Caregiver"]
		training_type: DF.Literal["", "Initial", "Refesher"]
		updated_at: DF.Data | None
		updated_by: DF.Data | None
	# end: auto-generated types

	pass
