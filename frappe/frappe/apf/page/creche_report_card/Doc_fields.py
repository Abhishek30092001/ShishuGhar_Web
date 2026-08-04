import frappe

@frappe.whitelist(allow_guest=True)
def inject_tamil_into_core_json():
    """
    Injects Tamil fields directly into the core DocType (DocField table)
    so they write to the custom app's .json files. Skips existing fields.
    """
    if not frappe.conf.developer_mode:
        frappe.throw("Developer Mode must be enabled to rewrite DocType JSON files.")

    doctypes_mapping = [
        ("Partner", "partner_kn", "partner_tn", "Partner TN"),
        ("Gender", "gender_kn", "gender_tn", "Gender TN"),
        ("Social Category", "social_category_kn", "social_category_tn", "Social Category TN"),
        ("Primary Occupation", "primary_occupation", "primary_occupation_tn", "Primary Occupation TN"),
        ("Verfication Status", "verfication_status_name", "verfication_status_tn", "Verification Status TN"),
        ("No of Months", "no_of_months", "no_of_months_tn", "No of Months TN"),
        ("Relation", "relation_kn", "relation_tn", "Relation TN"),
        ("YesNo", "option_name", "option_name_tn", "YesNo TN"),
        ("Illness", "illness", "illness_tn", "Illness TN"),
        ("Option", "option", "option_tn", "Option TN"),
        ("Weight For Height", "weight_for_height", "weight_for_height_tn", "Weight For Height TN"),
        ("Lives in", "family_lives_in", "family_lives_in_tn", "Lives in TN"),
        ("House Type", "house_type", "house_type_tn", "House Type TN"),
        ("Source of Water", "source", "source_tn", "Source of Water TN"),
        ("Education Level", "level", "level_tn", "Education Level TN"),
        ("Entitlement", "entitlement_kn", "entitlement_tn", "Entitlement TN"),
        ("Days Of Week", "day_name", "day_name_tn", "Days Of Week TN"),
        ("Reason for child exit", "reason_for_child_exit_kn", "reason_for_child_exit_tn", "Reason for child exit TN"),
        ("CC Verification status", "verification_status", "verification_status_tn", "CC Verification status TN"),
        ("Reason for Closure", "add_reason_for_closure", "add_reason_for_closure_tn", "Reason for Closure TN"),
        ("Grievance Status", "grievance_status_kn", "grievance_status_tn", "Grievance Status TN"),
        ("Fan in Creche", "add_fan", "add_fan_tn", "Fan in Creche TN"),
        ("Fencing at creche", "add_fencing", "add_fencing_tn", "Fencing at creche TN"),
        ("Assets", "assets_kn", "assets_tn", "Assets TN"),
        ("Water purification", "water_purification_kn", "water_purification_tn", "Water purification TN"),
        ("Status of toilet facility", "add_status", "add_status_tn", "Status of toilet facility TN"),
        ("Source of Electricity", "add_electricity", "add_electricity_tn", "Source of Electricity TN"),
        ("Register", "add_register", "add_register_tn", "Register TN"),
        ("Cleanliness", "add_cleanliness", "add_cleanliness_tn", "Cleanliness TN"),
        ("Caregivers Hygiene", "add_hygiene", "add_hygiene_tn", "Caregivers Hygiene TN"),
        ("Childrens Hygiene", "add_children_hygiene", "add_children_hygiene_tn", "Childrens Hygiene TN"),
        ("Hygiene YesNo", "add_yes_no", "add_yes_no_tn", "Hygiene YesNo TN"),
        ("Anganwadi yesno", "add_yes_no", "add_yes_no_tn", "Anganwadi yesno TN"),
        ("Anganwadi immunisation", "add_immunization", "add_immunization_tn", "Anganwadi immunisation TN"),
        ("Anganwadi Vitamin", "add_vitamin", "add_vitamin_tn", "Anganwadi Vitamin TN"),
        ("Anganwadi deworming", "add_deworming", "add_deworming_tn", "Anganwadi deworming TN"),
        ("Anthropromatric equipment", "add_equipment", "add_equipment_tn", "Anthropromatric equipment TN"),
        ("Register cms", "add_cms", "add_cms_tn", "Register cms TN"),
        ("Assets first aid kit", "add_assets_aid", "add_assets_aid_tn", "Assets first aid kit TN"),
        ("Longterm Illness", "longterm_illness_kn", "longterm_illness_tn", "Longterm Illness TN"),
        ("Diagnosis", "diagnosis", "diagnosis_tn", "Diagnosis TN"),
        ("Referral reason", "referral_reason", "referral_reason_tn", "Referral reason TN"),
        ("Referral to", "referral_to", "referral_to_tn", "Referral to TN"),
        ("Treatment details NRC", "add_treatment_details_nrc", "add_treatment_details_nrc_tn", "Treatment details NRC TN"),
        ("Treatment details", "treatment_detail", "treatment_detail_tn", "Treatment details TN"),
        ("Attendees", "attendees_kn", "attendees_tn", "Attendees TN"),
        ("Measurement Equipment", "measurement_equipment", "measurement_equipment_tn", "Measurement Equipment TN"),
        ("Available Not Available", "available_not_available", "available_not_available_tn", "Available Not Available TN"),
        ("Grievance Subject", "grievance_subject", "grievance_subject_tn", "Grievance Subject TN"),
        ("Months", "months", "months_tn", "Months TN"),
        ("Money Received by Caregiver", "money_received", "money_received_tn", "Money Received by Caregiver TN"),
        ("Item", "add_item", "add_item_tn", "Item TN"),
        ("Year", "year", "year_tn", "Year TN"),
        ("Type of creche house", "type_of_creche_house", "type_of_creche_house_tn", "Type of creche house TN"),
        ("Priority", "priority_kn", "priority_tn", "Priority TN"),
        ("Caste", "caste_id", "caste_id_tn", "Caste TN"),
        ("Disability", "disability_kn", "disability_tn", "Disability TN"),
        ("Red Flag Child Action taken", "action_taken", "action_taken_tn", "Red Flag Child Action taken TN"),
        ("Religion", "religion", "religion_tn", "Religion TN"),
        ("VHSND", "vhsnd_kn", "vhsnd_tn", "VHSND TN"),
        ("Visit Purpose", "add_visit_purpose_kn", "add_visit_purpose_tn", "Visit Purpose TN"),
        ("Reason for caregiver exit", "caregiver_exit", "caregiver_exit_tn", "Reason for caregiver exit TN"),
        ("Child Status", "child_status", "child_status_tn", "Child Status TN"),
        ("Measurement Taken", "measurement_taken_kn", "measurement_taken_tn", "Measurement Taken TN"),
        ("Reason Child is not available", "reason_child_is_not_available_kn", "reason_child_is_not_available_tn", "Reason Child Not Available TN"),
        ("Master Stock", "master_stock_hi", "master_stock_tn", "Master Stock TN"),
        ("Partner Stock", "partner_stock_kn", "partner_stock_tn", "Partner Stock TN"),
        ("Creche Status", "creche_status_kn", "creche_status_tn", "Creche Status TN"),
        ("Phase", "phase_kn", "phase_tn", "Phase TN"),
        ("Language Master", "language_name", "language_name_tn", "Language Master TN"),
        ("Demographic data", "add_demographic_data", "add_demographic_data_tn", "Demographic data TN"),
        ("HH Child Status", "hh_child_status_kn", "hh_child_status_tn", "HH Child Status TN"),
        ("Yes No observed", "yes_no_note_observed_kn", "yes_no_note_observed_tn", "Yes No Observed TN"),
        ("Measurement Position", "measurement_position_kn", "measurement_position_tn", "Measurement Position TN")
    ]

    added_count = 0
    skipped = []
    errors = []

    for doctype_name, insert_after, fieldname, label in doctypes_mapping:
        if not frappe.db.exists("DocType", doctype_name):
            continue
            
        try:
            doc = frappe.get_doc("DocType", doctype_name)
            
            # 1. STRICT CHECK: If the field is already in the Doctype, skip it entirely
            if any(f.fieldname == fieldname for f in doc.fields):
                skipped.append(f"{doctype_name}: '{fieldname}' already exists.")
                continue

            # 2. Find the exact list index of the Kannada field
            target_idx = len(doc.fields)
            for i, f in enumerate(doc.fields):
                if f.fieldname == insert_after:
                    target_idx = i + 1 # We want to insert immediately AFTER it
                    break
            
            # 3. Use Frappe's append to create the proper DocField object
            new_row = doc.append("fields", {
                "fieldname": fieldname,
                "label": label,
                "fieldtype": "Data",
                "translatable": 1
            })
            
            # 4. 'append' places it at the very end. Move it to our target_idx.
            doc.fields.remove(new_row)
            doc.fields.insert(target_idx, new_row)
            
            # 5. Re-index the row numbering (idx) for the entire table so the UI is stable
            for i, f in enumerate(doc.fields):
                f.idx = i + 1
                
            # 6. Save the Doctype to write changes to the .json file!
            doc.flags.ignore_permissions = True
            doc.save()
            added_count += 1
            
        except Exception as e:
            errors.append(f"Failed on {doctype_name}: {str(e)}")

    frappe.db.commit()
    
    return {
        "status": "success",
        "message": f"Setup complete. Added {added_count} fields. Skipped {len(skipped)} fields.",
        "details": {
            "added_count": added_count,
            "skipped": skipped,
            "errors": errors
        }
    }