// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Enrollment & Exit Report"] = {
    filters: [
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
            onchange: function () {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { "value": "01", "label": "January" },
                { "value": "02", "label": "February" },
                { "value": "03", "label": "March" },
                { "value": "04", "label": "April" },
                { "value": "05", "label": "May" },
                { "value": "06", "label": "June" },
                { "value": "07", "label": "July" },
                { "value": "08", "label": "August" },
                { "value": "09", "label": "September" },
                { "value": "10", "label": "October" },
                { "value": "11", "label": "November" },
                { "value": "12", "label": "December" }
            ],
            default: frappe.datetime.get_today().split('-')[1],
        },
        {
            fieldname: "partner",
            label: __("Partner"),
            fieldtype: "Link",
            options: "Partner",
        },
        {
            fieldname: "state",
            label: __("State"),
            fieldtype: "Link",
            options: "State",
            get_query: function () {
                return {
                    filters: {
                        "is_active": 1
                    }
                };
            },
            on_change: function () {
                frappe.query_report.set_filter_value("district", "");
                frappe.query_report.set_filter_value("block", "");
                frappe.query_report.set_filter_value("gp", "");
                frappe.query_report.set_filter_value("creche", "");
                frappe.query_report.set_filter_value("supervisor_id", "");
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "district",
            label: __("District"),
            fieldtype: "Link",
            options: "District",
            get_query: function () {
                let state = frappe.query_report.get_filter_value("state");
                return state ? { filters: { state_id: state } } : {};
            },
            on_change: function () {
                frappe.query_report.set_filter_value("block", "");
                frappe.query_report.set_filter_value("gp", "");
                frappe.query_report.set_filter_value("creche", "");
                frappe.query_report.set_filter_value("supervisor_id", "");
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "block",
            label: __("Block"),
            fieldtype: "Link",
            options: "Block",
            get_query: function () {
                let district = frappe.query_report.get_filter_value("district");
                return district ? { filters: { district_id: district } } : {};
            },
            on_change: function () {
                frappe.query_report.set_filter_value("gp", "");
                frappe.query_report.set_filter_value("creche", "");
                frappe.query_report.set_filter_value("supervisor_id", "");
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "gp",
            label: __("Gram Panchayat"),
            fieldtype: "Link",
            options: "Gram Panchayat",
            get_query: function () {
                let block = frappe.query_report.get_filter_value("block");
                return block ? { filters: { block_id: block } } : {};
            },
            on_change: function () {
                frappe.query_report.set_filter_value("creche", "");
                frappe.query_report.set_filter_value("supervisor_id", "");
                frappe.query_report.refresh();
            }
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
            fieldname: "creche",
            label: __("Creche"),
            fieldtype: "Link",
            options: "Creche",
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
        
        // Age of Creche Filter - Updated with auto-calculation logic
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
            default: "",
            on_change: function () {
                const dateRangeType = frappe.query_report.get_filter_value("cr_opening_range_type");
                toggleDateFields(dateRangeType);
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
        // {
        //  "fieldname": "is_exited",
        //  "label": __("Is Exited"),
        //  "fieldtype": "Select",
        //  "options": [
        //      { "value": "", "label": __("") },
        //      { "value": "1", "label": __("Yes") },
        //  ],
        //  "default": "",
        //  "reqd": 0,
        // }

        {
            fieldname: "is_exited",
            label: __("Is Exited"),
            fieldtype: "Check",
            default: 0
        }
    ],

    // Added onload to append the custom Download Report button
    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });
    }
};

// Helper function to sync creche_age with opening date filter
function syncCrecheAgeWithOpeningDate() {
    const value = frappe.query_report.get_filter_value("creche_age");
    const type_field = frappe.query_report.get_filter("cr_opening_range_type");
    const range_field = frappe.query_report.get_filter("c_opening_range");
    const single_field = frappe.query_report.get_filter("single_date");
    
    if (value) {
        // Map age ranges to approximate months (using the middle/starting point of each range)
        const months_map = {
            "0-6 Month": 3,    // Using 3 months as representative (middle of 0-6)
            "7-12 Month": 9,    // Using 9 months as representative (middle of 7-12)
            "13-18 Month": 15,  // Using 15 months as representative (middle of 13-18)
            "19-24 Month": 21,  // Using 21 months as representative (middle of 19-24)
            "24+ Month": 24     // Using 24 months as minimum
        };
        
        const n_months = months_map[value];
        
        if (n_months !== undefined) {
            // Get current year and month from filters, or use current date
            let curr_year = parseInt(frappe.query_report.get_filter_value("year")) || new Date().getFullYear();
            let curr_month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
            
            // Create date for the end of the selected month
            let current_date = new Date(curr_year, curr_month, 0);
            
            // Calculate past date by subtracting months
            let past_date = new Date(current_date);
            past_date.setMonth(past_date.getMonth() - n_months);
            
            // Format date as YYYY-MM-DD
            let date_str = past_date.getFullYear() + "-" +
                           String(past_date.getMonth() + 1).padStart(2, '0') + "-" +
                           String(past_date.getDate()).padStart(2, '0');
            
            // Set filter values
            frappe.query_report.set_filter_value("cr_opening_range_type", "after");
            frappe.query_report.set_filter_value("single_date", date_str);
            frappe.query_report.set_filter_value("c_opening_range", []);
            
            // Toggle field visibility
            toggleDateFields("after");
        }
    } else {
        // Clear all related filters when creche_age is cleared
        frappe.query_report.set_filter_value("cr_opening_range_type", "");
        frappe.query_report.set_filter_value("single_date", "");
        frappe.query_report.set_filter_value("c_opening_range", []);
        toggleDateFields("");
    }
}

// Helper function to toggle date fields based on selection
function toggleDateFields(dateRangeType) {
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
}