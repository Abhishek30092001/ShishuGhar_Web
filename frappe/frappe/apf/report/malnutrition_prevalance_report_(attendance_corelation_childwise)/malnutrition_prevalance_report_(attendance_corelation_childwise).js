// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Malnutrition Prevalance Report (Attendance Corelation Childwise)"] = {
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
        // {
        //  fieldname: "gp",
        //  label: __("Gram Panchayat"),
        //  fieldtype: "Link",
        //  options: "Gram Panchayat",
        //  get_query: function () {
        //      let block = frappe.query_report.get_filter_value("block");
        //      return block ? { filters: { block_id: block } } : {};
        //  },
        //  on_change: function () {
        //      frappe.query_report.set_filter_value("creche", "");
        //      frappe.query_report.set_filter_value("supervisor_id", "");
        //      frappe.query_report.refresh();
        //  }
        // },
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
            fieldname: "duration",
            label: __("Duration"),
            fieldtype: "Select",
            options: [
            { value: "", label: __("") },
            { value: "3_months", label: __("3 Month") },
            { value: "6_months", label: __("6 Month") },
            { value: "12_months", label: __("12 Month") },
            ],
            onchange: function () {
            updateFilterDesc();
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
        }
    ],

    formatter: function (value, row, column, data, default_formatter) {
        // First format with default formatter
        value = default_formatter(value, row, column, data);

        // Check if this is one of our status columns
        const fieldname = column.fieldname;

        // Define our status field patterns and their corresponding color code fields
        const fieldPatterns = {
            'underweight_status_': 'weight_for_age_',
            'wasting_status_': 'weight_for_height_',
            'stuning_status_': 'height_for_age_'
        };

        // Find which pattern matches (if any)
        let matchedPattern = null;
        for (const pattern in fieldPatterns) {
            if (fieldname.startsWith(pattern)) {
                matchedPattern = pattern;
                break;
            }
        }

        if (matchedPattern) {
            // Extract the date part (e.g., "2025_01")
            const datePart = fieldname.replace(matchedPattern, '');
            const colorCodeField = fieldPatterns[matchedPattern] + datePart;

            // Get the color code (1=red, 2=yellow, 3=green)
            const colorCode = data[colorCodeField];

            if (colorCode) {
                let backgroundColor = '';
                let textColor = '#000000';
                let fontWeight = 'bold'; // All cases bold now

                switch (parseInt(colorCode)) {
                    case 1: // Red
                        backgroundColor = '#FFCCCB';
                        textColor = '#8B0000'; // Dark red
                        break;
                    case 2: // Yellow
                        backgroundColor = '#FFFACD';
                        textColor = '#CC9900'; // Dark yellow/gold
                        break;
                    case 3: // Green
                        backgroundColor = '#90EE90';
                        textColor = '#006400'; // Dark green
                        break;
                }

                if (backgroundColor) {
                    value = `<div style="background-color: ${backgroundColor}; 
                              color: ${textColor};
                              width: 100%; 
                              height: 100%; 
                              padding: 4px;
                              text-align: center;
                              border-radius: 3px;
                              font-weight: ${fontWeight};
                              display: flex;
                              align-items: center;
                              justify-content: center;">${value}</div>`;
                }
            }
        }

        // Hide the color code columns completely
        if (fieldname.startsWith('weight_for_age_') ||
            fieldname.startsWith('weight_for_height_') ||
            fieldname.startsWith('height_for_age_')) {
            return '';
        }

        return value;
    },

    // Added onload to append the custom Download Report button
    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });
    }
};