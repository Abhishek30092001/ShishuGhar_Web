// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Cohort Exited and Graduated"] = {
	"filters": [
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			options: (() => {
				const start_year = 2022;
				const current_year = new Date().getFullYear();
				return Array.from(
					{ length: current_year - start_year + 1 },
					(_, i) => (start_year + i).toString()
				);
			})(),
			default: new Date().getFullYear().toString(),
		},
		{
			"fieldname": "month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": [
				{ "value": "1", "label": __("January") },
				{ "value": "2", "label": __("February") },
				{ "value": "3", "label": __("March") },
				{ "value": "4", "label": __("April") },
				{ "value": "5", "label": __("May") },
				{ "value": "6", "label": __("June") },
				{ "value": "7", "label": __("July") },
				{ "value": "8", "label": __("August") },
				{ "value": "9", "label": __("September") },
				{ "value": "10", "label": __("October") },
				{ "value": "11", "label": __("November") },
				{ "value": "12", "label": __("December") }
			],
			"default": (new Date().getMonth() + 1).toString(),
		},
		{
			"fieldname": "partner",
			"label": __("Partner"),
			"fieldtype": "Link",
			"options": "Partner",
			"default": frappe.defaults.get_user_default("partner"),
		},
		{
			"fieldname": "state",
			"label": __("State"),
			"fieldtype": "Link",
			"options": "State",
			"get_query": function () {
				return {
					filters: {
						"is_active": 1
					}
				};
			},
			"on_change": function () {
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "district",
			"label": __("District"),
			"fieldtype": "Link",
			"options": "District",
			get_query: function () {
				let state = frappe.query_report.get_filter_value("state")
				return state ? { filters: { state_id: state } } : {};
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("block", "");
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "block",
			"label": __("Block"),
			"fieldtype": "Link",
			"options": "Block",
			"get_query": function () {
				let district = frappe.query_report.get_filter_value("district");
				return { filters: { district: district || undefined } };
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("gp", "");
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "gp",
			"label": __("Gram Panchayat"),
			"fieldtype": "Link",
			"options": "Gram Panchayat",
			"get_query": function () {
				let block = frappe.query_report.get_filter_value("block");
				return { filters: { block: block || undefined } };
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("creche", "");
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "creche",
			"label": __("Creche"),
			"fieldtype": "Link",
			"options": "Creche",
			"get_query": function () {
				let gp = frappe.query_report.get_filter_value("gp");
				return { filters: { gp: gp || undefined } };
			},
			"on_change": function () {
				frappe.query_report.set_filter_value("supervisor_id", "");
				frappe.query_report.refresh();
			}
		},
		{
			"fieldname": "supervisor_id",
			"label": __("Supervisor"),
			"fieldtype": "Link",
			"options": "User",
			"get_query": function () {
				let creche = frappe.query_report.get_filter_value("creche");
				return creche ? { filters: { creche: creche } } : {};
			},
		},
		{
			"fieldname": "phases",
			"label": __("Phase"),
			"fieldtype": "MultiSelect",
			"options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
			"reqd": 0,
			"default": ""
		},
		{
			"fieldname": "creche_status_id",
			"label": __("Creche Status"),
			"fieldtype": "Select",
			"options": [
				{ "value": "", "label": __("") },
				{ "value": "1", "label": __("Planned") },
				{ "value": "2", "label": __("Plan dropped") },
				{ "value": "3", "label": __("Active/Operational") },
				{ "value": "4", "label": __("Closed") },
			],
			"default": "3",
		},
		{
			fieldname: "gender",
			label: __("Gender"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "1", label: __("Male") },
				{ value: "2", label: __("Female") },
			],
			default: "",
			on_change() {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "duration_of_stay",
			label: __("Period of Stay (Months)"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "6m", label: __("6m") },
				{ value: "12m", label: __("12m") },
				{ value: "18m", label: __("18m") },
				{ value: "24m", label: __("24m") },
				{ value: "30m", label: __("30m") },
				{ value: "36m", label: __("36m") }
			],
			default: "",
			on_change() {
				frappe.query_report.refresh();
			}
		},
        {
            fieldname: "creche_age",
            label: __("Age of Creche"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("") },
                { value: "0-6 Month", label: __("0-6 Month") },
                { value: "7-12 Month", label: __("7-12 Month") },
                { value: "13-18 Month", label: __("13-18 Month") },
                { value: "19-24 Month", label: __("19-24 Month") },
                { value: "24+ Month", label: __("24+ Month") }
            ],
            default: "",
            on_change: function () {
                frappe.query_report.refresh();
            }
        },
		{
			fieldname: "indicator",
			label: __("Indicator"),
			fieldtype: "Select",
			options: [
				{ value: "weight_for_age", label: __("Weight for Age (WFA)") },
				{ value: "weight_for_height", label: __("Weight for Height (WFH)") },
				{ value: "height_for_age", label: __("Height for Age (HFA)") }
			],
			default: "weight_for_age",
			on_change() {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "category",
			label: __("Category"),
			fieldtype: "Select",
			options: [
				{ value: "all", label: __("All Categories") },
				{ value: "Normal", label: __("Normal") },
				{ value: "Moderate", label: __("Moderate") },
				{ value: "Severe", label: __("Severe") }
			],
			default: "all",
			on_change() {
				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "cr_opening_range_type",
			label: __("Creche Opening Date"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "between", label: __("Between") },
				{ value: "before", label: __("Before") },
				{ value: "after", label: __("After") },
				{ value: "equal", label: __("Equal") }
			],
			// default: "",
			on_change: function () {
				const dateRangeType = frappe.query_report.get_filter_value("cr_opening_range_type");

				const isBetween = dateRangeType === "between";
				const isSingleDate = ["before", "after", "equal"].includes(dateRangeType);
				const isCleared = dateRangeType === "";

				frappe.query_report.get_filter("c_opening_range").toggle(isBetween);
				frappe.query_report.get_filter("single_date").toggle(isSingleDate);

				if (isBetween) {
					frappe.query_report.set_filter_value("single_date", "");
				} else if (isSingleDate) {
					frappe.query_report.set_filter_value("c_opening_range", []);
				}

				if (isCleared) {
					frappe.query_report.set_filter_value("c_opening_range", []);
					frappe.query_report.set_filter_value("single_date", "");
				}

				frappe.query_report.refresh();
			}
		},
		{
			fieldname: "c_opening_range",
			label: __("Creche Opening Range"),
			fieldtype: "DateRange",
			hidden: 1
		},
		{
			fieldname: "single_date",
			label: __("Creche Opening Date"),
			fieldtype: "Date",
			hidden: 1
		},
		{
			fieldname: "reason_of_exit",
			label: __("Graduated"),
			fieldtype: "Select",
			options: [
				{ value: "", label: __("") },
				{ value: "2", label: __("Graduated") }
			],
			default: "",
			on_change() {
				frappe.query_report.refresh();
			}
		}
	],

    // Added onload to append the custom Download Report button
    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });
    }

};
