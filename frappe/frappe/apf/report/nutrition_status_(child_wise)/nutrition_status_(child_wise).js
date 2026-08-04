// // Copyright (c) 2025, Frappe Technologies and contributors
// // For license information, please see license.txt

frappe.query_reports["Nutrition Status (Child Wise)"] = {
    filters: [
        {
            fieldname: "initial_month",
            label: "Initial Month",
            fieldtype: "Select",
            options: [
                { value: "1", label: "January" },
                { value: "2", label: "February" },
                { value: "3", label: "March" },
                { value: "4", label: "April" },
                { value: "5", label: "May" },
                { value: "6", label: "June" },
                { value: "7", label: "July" },
                { value: "8", label: "August" },
                { value: "9", label: "September" },
                { value: "10", label: "October" },
                { value: "11", label: "November" },
                { value: "12", label: "December" }
            ],
            default: (() => {
                let finalMonth = new Date().getMonth() + 1;
                let initialMonth = finalMonth - 3;
                return (initialMonth <= 0 ? initialMonth + 12 : initialMonth).toString();
            })()
        },
        {
            fieldname: "initial_year",
            label: "Initial Year",
            fieldtype: "Select",
            options: ["2022", "2023", "2024", "2025", "2026"],
            default: (() => {
                let finalMonth = new Date().getMonth() + 1;
                let currentYear = new Date().getFullYear();
                return (finalMonth - 3 <= 0 ? currentYear - 1 : currentYear).toString();
            })()
        },
        {
            fieldname: "final_month",
            label: "Final Month",
            fieldtype: "Select",
            options: [
                { value: "1", label: "January" },
                { value: "2", label: "February" },
                { value: "3", label: "March" },
                { value: "4", label: "April" },
                { value: "5", label: "May" },
                { value: "6", label: "June" },
                { value: "7", label: "July" },
                { value: "8", label: "August" },
                { value: "9", label: "September" },
                { value: "10", label: "October" },
                { value: "11", label: "November" },
                { value: "12", label: "December" }
            ],
            default: (new Date().getMonth() + 1).toString()
        },
        {
            fieldname: "final_year",
            label: "Final Year",
            fieldtype: "Select",
            options: ["2022", "2023", "2024", "2025","2026"],
            default: new Date().getFullYear().toString()
        },
        {
            fieldname: "partner",
            label: __("Partner"),
            fieldtype: "Link",
            options: "Partner",
            default: frappe.defaults.get_user_default("partner"),
            on_change() {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "state",
            label: __("State"),
            fieldtype: "Link",
            options: "State",
            get_query: () => ({ filters: { is_active: 1 } }),
            on_change() {
                ["district", "block", "gp", "creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "district",
            label: __("District"),
            fieldtype: "Link",
            options: "District",
            get_query() {
                const state = frappe.query_report.get_filter_value("state");
                return state ? { filters: { state_id: state } } : {};
            },
            on_change() {
                ["block", "gp", "creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "block",
            label: __("Block"),
            fieldtype: "Link",
            options: "Block",
            get_query() {
                const district = frappe.query_report.get_filter_value("district");
                return district ? { filters: { district_id: district } } : {};
            },
            on_change() {
                ["gp", "creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "gp",
            label: __("Gram Panchayat"),
            fieldtype: "Link",
            options: "Gram Panchayat",
            get_query() {
                const block = frappe.query_report.get_filter_value("block");
                return block ? { filters: { block_id: block } } : {};
            },
            on_change() {
                ["creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "creche",
            "label": __("Creche"),
            "fieldtype": "Link",
            "options": "Creche",
            "reqd": 0
        },
        {
            fieldname: "phases",
            label: __("Phase"),
            fieldtype: "MultiSelect",
            options: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        },
        {
            fieldname: "creche_status_id",
            label: __("Creche Status"),
            fieldtype: "Select",
            options: [
                { value: "", label: "" },
                { value: "1", label: __("Planned") },
                { value: "2", label: __("Plan dropped") },
                { value: "3", label: __("Active/Operational") },
                { value: "4", label: __("Closed") }
            ],
            default: "3"
        },
        {
            fieldname: "supervisor_id",
            label: __("Supervisor"),
            fieldtype: "Link",
            options: "User",
            get_query: function () {
                let creche = frappe.query_report.get_filter_value("creche");
                return creche ? { filters: { creche: creche } } : {};
            },
        },
        {
            fieldname: "age_group",
            label: __("Age Group"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("All Age Groups") },
                { value: "6m-11m", label: __("6m-11m") },
                { value: "12m-17m", label: __("12m-17m") },
                { value: "18m-23m", label: __("18m-23m") },
                { value: "24m-29m", label: __("24m-29m") },
                { value: "30m-36m", label: __("30m-36m") },
                { value: "> 36m", label: __("> 36m") }
            ],
            default: "",
            on_change() {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "gender",
            label: __("Gender"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("Gender") },
                { value: "1", label: __("Male") },
                { value: "2", label: __("Female") },
            ],
            default: "",
            on_change() {
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
                { value: "", label: "" },
                { value: "between", label: __("Between") },
                { value: "before", label: __("Before") },
                { value: "after", label: __("After") },
                { value: "equal", label: __("Equal") }
            ],
            default: "",
            on_change() {
                const type = frappe.query_report.get_filter_value("cr_opening_range_type");
                frappe.query_report.get_filter("c_opening_range").toggle(type === "between");
                frappe.query_report.get_filter("single_date").toggle(["before", "after", "equal"].includes(type));

                if (type === "") {
                    frappe.query_report.set_filter_value("c_opening_range", []);
                    frappe.query_report.set_filter_value("single_date", "");
                } else if (type === "between") {
                    frappe.query_report.set_filter_value("single_date", "");
                } else {
                    frappe.query_report.set_filter_value("c_opening_range", []);
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
        }
    ],

    onload: function(report) {
        // Hide export/print buttons
        $('.page-actions .btn-primary[data-label="Download Report"]').remove();
        $('.page-actions .btn-primary[data-label="Print"]').remove();
        
        // Or hide the entire menu if needed
        $('.menu-btn-group .dropdown-toggle').parent().hide();
    }


};








// frappe.query_reports["Nutrition Status (Child Wise)"] = {
//     filters: [
//         {
//             fieldname: "initial_month",
//             label: "Initial Month",
//             fieldtype: "Select",
//             options: [
//                 { value: "1", label: "January" },
//                 { value: "2", label: "February" },
//                 { value: "3", label: "March" },
//                 { value: "4", label: "April" },
//                 { value: "5", label: "May" },
//                 { value: "6", label: "June" },
//                 { value: "7", label: "July" },
//                 { value: "8", label: "August" },
//                 { value: "9", label: "September" },
//                 { value: "10", label: "October" },
//                 { value: "11", label: "November" },
//                 { value: "12", label: "December" }
//             ],
//             default: (() => {
//                 let finalMonth = new Date().getMonth() + 1;
//                 let initialMonth = finalMonth - 3;
//                 return (initialMonth <= 0 ? initialMonth + 12 : initialMonth).toString();
//             })()
//         },
//         {
//             fieldname: "initial_year",
//             label: "Initial Year",
//             fieldtype: "Select",
//             options: ["2022", "2023", "2024", "2025"],
//             default: (() => {
//                 let finalMonth = new Date().getMonth() + 1;
//                 let currentYear = new Date().getFullYear();
//                 return (finalMonth - 3 <= 0 ? currentYear - 1 : currentYear).toString();
//             })()
//         },
//         {
//             fieldname: "final_month",
//             label: "Final Month",
//             fieldtype: "Select",
//             options: [
//                 { value: "1", label: "January" },
//                 { value: "2", label: "February" },
//                 { value: "3", label: "March" },
//                 { value: "4", label: "April" },
//                 { value: "5", label: "May" },
//                 { value: "6", label: "June" },
//                 { value: "7", label: "July" },
//                 { value: "8", label: "August" },
//                 { value: "9", label: "September" },
//                 { value: "10", label: "October" },
//                 { value: "11", label: "November" },
//                 { value: "12", label: "December" }
//             ],
//             default: (new Date().getMonth() + 1).toString()
//         },
//         {
//             fieldname: "final_year",
//             label: "Final Year",
//             fieldtype: "Select",
//             options: ["2022", "2023", "2024", "2025"],
//             default: new Date().getFullYear().toString()
//         },
//         {
//             fieldname: "partner",
//             label: __("Partner"),
//             fieldtype: "Link",
//             options: "Partner",
//             default: frappe.defaults.get_user_default("partner"),
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "state",
//             label: __("State"),
//             fieldtype: "Link",
//             options: "State",
//             get_query: () => ({ filters: { is_active: 1 } }),
//             on_change() {
//                 ["district", "block", "gp", "creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "district",
//             label: __("District"),
//             fieldtype: "Link",
//             options: "District",
//             get_query() {
//                 const state = frappe.query_report.get_filter_value("state");
//                 return state ? { filters: { state_id: state } } : {};
//             },
//             on_change() {
//                 ["block", "gp", "creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "block",
//             label: __("Block"),
//             fieldtype: "Link",
//             options: "Block",
//             get_query() {
//                 const district = frappe.query_report.get_filter_value("district");
//                 return district ? { filters: { district_id: district } } : {};
//             },
//             on_change() {
//                 ["gp", "creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "gp",
//             label: __("Gram Panchayat"),
//             fieldtype: "Link",
//             options: "Gram Panchayat",
//             get_query() {
//                 const block = frappe.query_report.get_filter_value("block");
//                 return block ? { filters: { block_id: block } } : {};
//             },
//             on_change() {
//                 ["creche", "supervisor_id"].forEach(f => frappe.query_report.set_filter_value(f, ""));
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             "fieldname": "creche",
//             "label": __("Creche"),
//             "fieldtype": "Link",
//             "options": "Creche",
//             "reqd": 0
//         },
//         {
//             fieldname: "phases",
//             label: __("Phase"),
//             fieldtype: "MultiSelect",
//             options: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
//         },
//         {
//             fieldname: "creche_status_id",
//             label: __("Creche Status"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: "" },
//                 { value: "1", label: __("Planned") },
//                 { value: "2", label: __("Plan dropped") },
//                 { value: "3", label: __("Active/Operational") },
//                 { value: "4", label: __("Closed") }
//             ],
//             default: "3"
//         },
//         {
//             fieldname: "supervisor_id",
//             label: __("Supervisor"),
//             fieldtype: "Link",
//             options: "User",
//             get_query: function () {
//                 let creche = frappe.query_report.get_filter_value("creche");
//                 return creche ? { filters: { creche: creche } } : {};
//             },
//         },
//         {
//             fieldname: "age_group",
//             label: __("Age Group"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("All Age Groups") },
//                 { value: "6m-11m", label: __("6m-11m") },
//                 { value: "12m-17m", label: __("12m-17m") },
//                 { value: "18m-23m", label: __("18m-23m") },
//                 { value: "24m-29m", label: __("24m-29m") },
//                 { value: "30m-36m", label: __("30m-36m") },
//                 { value: "> 36m", label: __("> 36m") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "gender",
//             label: __("Gender"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("Gender") },
//                 { value: "1", label: __("Male") },
//                 { value: "2", label: __("Female") },
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "indicator",
//             label: __("Indicator"),
//             fieldtype: "Select",
//             options: [
//                 { value: "weight_for_age", label: __("Weight for Age (WFA)") },
//                 { value: "weight_for_height", label: __("Weight for Height (WFH)") },
//                 { value: "height_for_age", label: __("Height for Age (HFA)") }
//             ],
//             default: "weight_for_age",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "category",
//             label: __("Category"),
//             fieldtype: "Select",
//             options: [
//                 { value: "all", label: __("All Categories") },
//                 { value: "Normal", label: __("Normal") },
//                 { value: "Moderate", label: __("Moderate") },
//                 { value: "Severe", label: __("Severe") }
//             ],
//             default: "all",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "cr_opening_range_type",
//             label: __("Creche Opening Date"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: "" },
//                 { value: "between", label: __("Between") },
//                 { value: "before", label: __("Before") },
//                 { value: "after", label: __("After") },
//                 { value: "equal", label: __("Equal") }
//             ],
//             default: "",
//             on_change() {
//                 const type = frappe.query_report.get_filter_value("cr_opening_range_type");
//                 frappe.query_report.get_filter("c_opening_range").toggle(type === "between");
//                 frappe.query_report.get_filter("single_date").toggle(["before", "after", "equal"].includes(type));

//                 if (type === "") {
//                     frappe.query_report.set_filter_value("c_opening_range", []);
//                     frappe.query_report.set_filter_value("single_date", "");
//                 } else if (type === "between") {
//                     frappe.query_report.set_filter_value("single_date", "");
//                 } else {
//                     frappe.query_report.set_filter_value("c_opening_range", []);
//                 }

//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             fieldname: "c_opening_range",
//             label: __("Creche Opening Range"),
//             fieldtype: "DateRange",
//             hidden: 1
//         },
//         {
//             fieldname: "single_date",
//             label: __("Creche Opening Date"),
//             fieldtype: "Date",
//             hidden: 1
//         }
//     ],


// };