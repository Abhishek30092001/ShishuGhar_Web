frappe.query_reports["Cohort Report (Creche Performance - Summary)"] = {
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
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": [
                { "value": "1", "label": "January" },
                { "value": "2", "label": "February" },
                { "value": "3", "label": "March" },
                { "value": "4", "label": "April" },
                { "value": "5", "label": "May" },
                { "value": "6", "label": "June" },
                { "value": "7", "label": "July" },
                { "value": "8", "label": "August" },
                { "value": "9", "label": "September" },
                { "value": "10", "label": "October" },
                { "value": "11", "label": "November" },
                { "value": "12", "label": "December" }
            ],
            "default": (new Date().getMonth() + 1).toString(),
            "on_change": function () {
                frappe.query_report.refresh();
            }
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
            fieldname: "level",
            label: __("Level"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("Level") },
                { value: "1", label: __("Partner") },
                { value: "2", label: __("State") },
                { value: "3", label: __("District") },
                { value: "4", label: __("Block") },
                { value: "5", label: __("Supervisor") },
                { value: "6", label: __("GP") },
                { value: "7", label: __("Creche") },
                { value: "8", label: __("Age of creche") },
                { value: "9", label: __("Gender") },
                { value: "10", label: __("Age of Child") },
                { value: "11", label: __("Age at Enrollment") },
                { value: "12", label: __("Tenure of Stay at Creche") },
                { value: "13", label: __("Attendance") }
            ],
            default: "",
            on_change() {
                frappe.query_report.refresh();
            }
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
                { value: "normal", label: __("Normal") },
                { value: "moderate", label: __("Moderate") },
                { value: "severe", label: __("Severe") }
            ],
            default: "all",
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

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Skip formatting for header row or if no data
        if (!data || column.is_tree) return value;
        
        // Define the numeric fields that should have their last value bold black
        const numericFields = [
            'operational_creches', 'enrolled_children', 'measurements_taken', 
            'exited_children', 'measurements_data_not_available'
        ];
        
        // Check if this is the Total row by checking the 'is_total' field
        const isTotalRow = !!data.is_total;

        // Apply bold black formatting for numeric fields in the Total row
        if (isTotalRow && numericFields.includes(column.fieldname)) {
            return `<span style="font-weight: bold; color: #000;">${value}</span>`;
        }
        
        // Define color scheme for transition display fields
        const highlightColors = {
            // Positive transitions (improvement) - Green shades
            'sv_md_display': '#FFFACD',    // Severe to Moderate (Light Yellow)
            'md_nr_display': '#90EE90',    // Moderate to Normal (Light Green)
            'sv_nr_display': '#90EE90',    // Severe to Normal (Light Green)
            
            // Negative transitions (worsening) - Red shades
            'nr_md_display': '#FFCCCB',    // Normal to Moderate (Light Red)
            'md_sv_display': '#FFCCCB',    // Moderate to Severe (Light Red)
            'nr_sv_display': '#FFCCCB',    // Normal to Severe (Light Red)
            
            // No Change breakdown - Different shades for each category
            'sv_sv_display': '#FFE4E1',    // Severe to Severe (Light Pink)
            'md_md_display': '#FFFACD',    // Moderate to Moderate (Light Yellow)
            'nr_nr_display': '#E6F3FF',    // Normal to Normal (Light Blue)
            
            // Data not available - Light gray
            'measurements_data_not_available': '#F5F5F5'
        };
        
        // Apply formatting for transition display fields
        if (highlightColors[column.fieldname]) {
            const style = isTotalRow ? 
                'font-weight: bold; color: #000; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;' :
                `background-color: ${highlightColors[column.fieldname]}; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;`;
            return `<div style="${style}">${value}</div>`;
        }
        
        // Default formatting for other columns
        return value;
    },

    // UI Professional & Scrollable Popup Code (WITH FIXED PRINT LOGIC)
    onload: function(report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        report.page.add_inner_button(__("Logic"), function() {
            
            const html_content = `
                <style>
                    .logic-popup-container {
                        max-height: 65vh; /* Makes it vertically scrollable */
                        overflow-y: auto;
                        overflow-x: auto; /* Makes it responsive on mobile */
                        border: 1px solid var(--border-color, #d1d8dd);
                        border-radius: 8px;
                        background-color: var(--card-bg, #ffffff);
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    }
                    .logic-popup-table { 
                        width: 100%; 
                        border-collapse: collapse; 
                        font-family: inherit; 
                        font-size: 13px;
                        min-width: 700px; /* Prevents text crunching on small screens */
                    }
                    .logic-popup-table th, .logic-popup-table td { 
                        border-bottom: 1px solid var(--border-color, #e2e8f0); 
                        padding: 12px 16px; 
                        text-align: left; 
                        vertical-align: middle;
                        line-height: 1.5;
                    }
                    /* Sticky Header Configuration */
                    .logic-popup-table thead th { 
                        position: sticky;
                        top: 0;
                        background-color: #d99694; 
                        color: #ffffff; 
                        font-weight: 600; 
                        z-index: 10;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        letter-spacing: 0.5px;
                    }
                    .logic-popup-table tbody tr:hover { 
                        background-color: var(--table-row-hover, #f8fafc); 
                    }
                    
                    /* Professional Soft Color Indicators */
                    .row-green { background-color: rgba(146, 208, 80, 0.1); }
                    .row-green td:first-child { border-left: 4px solid #92d050; }
                    
                    .row-red { background-color: rgba(255, 80, 80, 0.08); }
                    .row-red td:first-child { border-left: 4px solid #ff5050; }
                    
                    .row-blue { background-color: rgba(91, 155, 213, 0.1); }
                    .row-blue td:first-child { border-left: 4px solid #5b9bd5; }
                    
                    /* Column Widths and Typography */
                    .logic-popup-table td:first-child { 
                        font-weight: 600; 
                        width: 28%; 
                        color: var(--text-color, #1e293b); 
                    }
                    .logic-popup-table td:nth-child(2) { 
                        width: 42%; 
                        color: var(--text-muted, #475569); 
                    }
                    .logic-popup-table td:nth-child(3) { 
                        width: 30%; 
                        color: var(--text-color, #0f172a); 
                        background: rgba(0,0,0,0.02);
                    }
                </style>
                <div class="logic-popup-container">
                    <table class="logic-popup-table">
                        <thead>
                            <tr>
                                <th>FIELDS</th>
                                <th>LOGICS</th>
                                <th>CALCULATION</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Operational Creches</td><td>No of Active/operational creches</td><td></td></tr>
                            <tr><td>Cumulative Enrolled Children</td><td>Total children enrolled from starting date to selected date</td><td></td></tr>
                            <tr><td>Total Universe (Measured Atleast Twice)</td><td>Those children whose first and last measurement is there</td><td></td></tr>
                            <tr><td>Universe (Normal)</td><td>From the first measurement those children who are in Normal</td><td></td></tr>
                            <tr><td>Universe (Moderate)</td><td>From the first measurement those children who are in Moderate</td><td></td></tr>
                            <tr><td>Universe (Severe)</td><td>From the first measurement those children who are in Severe</td><td></td></tr>
                            <tr><td>Universe (Recovery)</td><td>Universe Severe + Universe Moderate</td><td></td></tr>
                            <tr><td>Universe (Deterioration)</td><td>Universe Normal + Universe Moderate</td><td></td></tr>
                            <tr class="row-green"><td>Moderate to Normal</td><td>Changed category from moderate (first measurement) to Normal (last measurement)</td><td>total no (moderate to normal) / Universe(Moderate) * 100</td></tr>
                            <tr class="row-green"><td>Severe to Moderate</td><td>Changed category from severe (first measurement) to moderate (last measurement)</td><td>total no (severe to moderate) / Universe(severe) * 100</td></tr>
                            <tr class="row-green"><td>Severe to Normal</td><td>Changed category from severe (first measurement) to Normal (last measurement)</td><td>total no (severe to normal) / Universe(severe) * 100</td></tr>
                            <tr><td>Total Recovery</td><td>moderate to normal + severe to moderate + severe to normal</td><td>total recovery no / Universe(Recovery) * 100</td></tr>
                            <tr class="row-red"><td>Normal to Moderate</td><td>Changed category from normal (first measurement) to moderate (last measurement)</td><td>total no (normal to moderate) / Universe(normal) * 100</td></tr>
                            <tr class="row-red"><td>Normal to Severe</td><td>Changed category from normal (first measurement) to severe (last measurement)</td><td>total no (normal to severe) / Universe(normal) * 100</td></tr>
                            <tr class="row-red"><td>Moderate to Severe</td><td>Changed category from moderate (first measurement) to severe (last measurement)</td><td>total no (moderate to severe) / Universe(moderate) * 100</td></tr>
                            <tr><td>Total Deterioration</td><td>normal to moderate + normal to severe + moderate to severe</td><td>total deterioration no / Universe(Deterioration) * 100</td></tr>
                            <tr><td>No Change</td><td>severe to severe + moderate to moderate + normal to normal</td><td>total no change no / Total Universe(Measured Atleast Twice) * 100</td></tr>
                            <tr class="row-blue"><td>(No Change) Severe to Severe</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (severe to severe) / Universe(severe) * 100</td></tr>
                            <tr class="row-blue"><td>(No Change) Moderate to Moderate</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (moderate to moderate) / Universe(Moderate) * 100</td></tr>
                            <tr class="row-blue"><td>(No Change) Normal to Normal</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (normal to normal) / Universe(normal) * 100</td></tr>
                        </tbody>
                    </table>
                </div>
            `;

            let dialog = new frappe.ui.Dialog({
                title: __('Field Logic'),
                size: 'extra-large',
                fields: [
                    {
                        fieldname: 'logic_html',
                        fieldtype: 'HTML',
                        options: html_content
                    }
                ]
            });
            
            dialog.show();

            // Insert Download PDF button in the header, left of the 'X' (Close) button
            let $download_btn = $('<button class="btn btn-default btn-xs" style="margin-right: 15px;">' + __('Download Logic') + '</button>');
            
            // Target the standard Frappe close button in the header
            let $close_btn = dialog.$wrapper.find('.modal-header .btn-modal-close, .modal-header .close, .modal-header [data-dismiss="modal"]');
            
            if ($close_btn.length) {
                $download_btn.insertBefore($close_btn);
            } else {
                // Fallback if the specific structure isn't found
                dialog.$wrapper.find('.modal-header').append($download_btn);
            }

            // Handle print-to-pdf layout rendering
            $download_btn.on('click', function() {
                let print_window = window.open('', '_blank');
                print_window.document.write(`
                    <html>
                        <head>
                            <title>Field Logic</title>
                            <style>
                                /* PRINT SPECIFIC FIXES */
                                @media print {
                                    body { 
                                        margin: 0; 
                                        padding: 20px;
                                        font-family: Arial, sans-serif;
                                    }
                                    .logic-popup-container {
                                        max-height: none !important; /* Removes the scroll limit */
                                        overflow: visible !important; /* Forces all content to show */
                                        border: none !important; /* Cleans up border for PDF */
                                        box-shadow: none !important;
                                    }
                                    .logic-popup-table {
                                        page-break-inside: auto;
                                    }
                                    .logic-popup-table tr {
                                        page-break-inside: avoid; /* Prevents a row from splitting across pages */
                                        page-break-after: auto;
                                    }
                                    .logic-popup-table thead {
                                        display: table-header-group; /* Repeats the table header on new pages */
                                    }
                                    /* Forces browsers to print background colors properly */
                                    * {
                                        -webkit-print-color-adjust: exact !important;
                                        print-color-adjust: exact !important;
                                    }
                                }
                            </style>
                        </head>
                        <body>
                            ${html_content}
                            <script>
                                setTimeout(function() {
                                    window.print();
                                    window.close();
                                }, 500); // Increased timeout slightly to ensure styling is applied before printing
                            </script>
                        </body>
                    </html>
                `);
                print_window.document.close();
            });
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
            "7-12 Month": 9,   // Using 9 months as representative (middle of 7-12)
            "13-18 Month": 15, // Using 15 months as representative (middle of 13-18)
            "19-24 Month": 21, // Using 21 months as representative (middle of 19-24)
            "24+ Month": 24    // Using 24 months as minimum
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


// // Copyright (c) 2026, Frappe Technologies and contributors
// // For license information, please see license.txt

// frappe.query_reports["Cohort Report (Creche Performance - Summary)"] = {
//     filters: [
//         {
//             fieldname: "year",
//             label: __("Year"),
//             fieldtype: "Select",
//             options: (() => {
//                 const start_year = 2022;
//                 const current_year = new Date().getFullYear();
//                 return Array.from(
//                     { length: current_year - start_year + 1 },
//                     (_, i) => (start_year + i).toString()
//                 );
//             })(),
//             default: new Date().getFullYear().toString(),
//             onchange: function () {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             "fieldname": "month",
//             "label": __("Month"),
//             "fieldtype": "Select",
//             "options": [
//                 { "value": "1", "label": "January" },
//                 { "value": "2", "label": "February" },
//                 { "value": "3", "label": "March" },
//                 { "value": "4", "label": "April" },
//                 { "value": "5", "label": "May" },
//                 { "value": "6", "label": "June" },
//                 { "value": "7", "label": "July" },
//                 { "value": "8", "label": "August" },
//                 { "value": "9", "label": "September" },
//                 { "value": "10", "label": "October" },
//                 { "value": "11", "label": "November" },
//                 { "value": "12", "label": "December" }
//             ],
//             "default": (new Date().getMonth() + 1).toString(),
//             "on_change": function () {
//                 frappe.query_report.refresh();
//             }
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
//             fieldname: "level",
//             label: __("Level"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("Level") },
//                 { value: "1", label: __("Partner") },
//                 { value: "2", label: __("State") },
//                 { value: "3", label: __("District") },
//                 { value: "4", label: __("Block") },
//                 { value: "5", label: __("Supervisor") },
//                 { value: "6", label: __("GP") },
//                 { value: "7", label: __("Creche") },
//                 { value: "8", label: __("Age of creche") },
//                 { value: "9", label: __("Gender") },
//                 { value: "10", label: __("Age of Child") },
//                 { value: "11", label: __("Age at Enrollment") },
//                 { value: "12", label: __("Tenure of Stay at Creche") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
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
//                 { value: "normal", label: __("Normal") },
//                 { value: "moderate", label: __("Moderate") },
//                 { value: "severe", label: __("Severe") }
//             ],
//             default: "all",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         // {
//         //      fieldname: "attedance",
//         //      label: __("Attendance"),
//         //      fieldtype: "Select",
//         //      options: [
//         //          { value: "", label: __("") },
//         //          { value: "regular", label: __("Regular(=≥ 70%)") },
//         //          { value: "irregular", label: __("Irregular(=≤ 50%)") }
//         //      ],
//         //      default: "",
//         //      on_change() {
//         //          frappe.query_report.refresh();
//         //      }
//         // },
//         {
//             fieldname: "creche_age",
//             label: __("Age of Creche"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("") },
//                 { value: "0-6 Month", label: __("0-6 Month") },
//                 { value: "7-12 Month", label: __("7-12 Month") },
//                 { value: "13-18 Month", label: __("13-18 Month") },
//                 { value: "19-24 Month", label: __("19-24 Month") },
//                 { value: "24+ Month", label: __("24+ Month") }
//             ],
//             default: "",
//             on_change: function () {
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

//     formatter(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);
        
//         // Skip formatting for header row or if no data
//         if (!data || column.is_tree) return value;
        
//         // Define the numeric fields that should have their last value bold black
//         const numericFields = [
//             'operational_creches', 'enrolled_children', 'measurements_taken', 
//             'exited_children', 'measurements_data_not_available'
//         ];
        
//         // Check if this is the Total row by checking the 'is_total' field
//         const isTotalRow = !!data.is_total;

//         // Apply bold black formatting for numeric fields in the Total row
//         if (isTotalRow && numericFields.includes(column.fieldname)) {
//             return `<span style="font-weight: bold; color: #000;">${value}</span>`;
//         }
        
//         // Define color scheme for transition display fields
//         const highlightColors = {
//             // Positive transitions (improvement) - Green shades
//             'sv_md_display': '#FFFACD',    // Severe to Moderate (Light Yellow)
//             'md_nr_display': '#90EE90',    // Moderate to Normal (Light Green)
//             'sv_nr_display': '#90EE90',    // Severe to Normal (Light Green)
            
//             // Negative transitions (worsening) - Red shades
//             'nr_md_display': '#FFCCCB',    // Normal to Moderate (Light Red)
//             'md_sv_display': '#FFCCCB',    // Moderate to Severe (Light Red)
//             'nr_sv_display': '#FFCCCB',    // Normal to Severe (Light Red)
            
//             // No Change breakdown - Different shades for each category
//             'sv_sv_display': '#FFE4E1',    // Severe to Severe (Light Pink)
//             'md_md_display': '#FFFACD',    // Moderate to Moderate (Light Yellow)
//             'nr_nr_display': '#E6F3FF',    // Normal to Normal (Light Blue)
            
//             // Data not available - Light gray
//             'measurements_data_not_available': '#F5F5F5'
//         };
        
//         // Apply formatting for transition display fields
//         if (highlightColors[column.fieldname]) {
//             const style = isTotalRow ? 
//                 'font-weight: bold; color: #000; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;' :
//                 `background-color: ${highlightColors[column.fieldname]}; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;`;
//             return `<div style="${style}">${value}</div>`;
//         }
        
//         // Default formatting for other columns
//         return value;
//     },

//     // UI Professional & Scrollable Popup Code
//     onload: function(report) {
//         report.page.add_inner_button(__("Logic"), function() {
            
//             const html_content = `
//                 <style>
//                     .logic-popup-container {
//                         max-height: 65vh; /* Makes it vertically scrollable */
//                         overflow-y: auto;
//                         overflow-x: auto; /* Makes it responsive on mobile */
//                         border: 1px solid var(--border-color, #d1d8dd);
//                         border-radius: 8px;
//                         background-color: var(--card-bg, #ffffff);
//                         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
//                     }
//                     .logic-popup-table { 
//                         width: 100%; 
//                         border-collapse: collapse; 
//                         font-family: inherit; 
//                         font-size: 13px;
//                         min-width: 700px; /* Prevents text crunching on small screens */
//                     }
//                     .logic-popup-table th, .logic-popup-table td { 
//                         border-bottom: 1px solid var(--border-color, #e2e8f0); 
//                         padding: 12px 16px; 
//                         text-align: left; 
//                         vertical-align: middle;
//                         line-height: 1.5;
//                     }
//                     /* Sticky Header Configuration */
//                     .logic-popup-table thead th { 
//                         position: sticky;
//                         top: 0;
//                         background-color: #d99694; 
//                         color: #ffffff; 
//                         font-weight: 600; 
//                         z-index: 10;
//                         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
//                         letter-spacing: 0.5px;
//                     }
//                     .logic-popup-table tbody tr:hover { 
//                         background-color: var(--table-row-hover, #f8fafc); 
//                     }
                    
//                     /* Professional Soft Color Indicators */
//                     .row-green { background-color: rgba(146, 208, 80, 0.1); }
//                     .row-green td:first-child { border-left: 4px solid #92d050; }
                    
//                     .row-red { background-color: rgba(255, 80, 80, 0.08); }
//                     .row-red td:first-child { border-left: 4px solid #ff5050; }
                    
//                     .row-blue { background-color: rgba(91, 155, 213, 0.1); }
//                     .row-blue td:first-child { border-left: 4px solid #5b9bd5; }
                    
//                     /* Column Widths and Typography */
//                     .logic-popup-table td:first-child { 
//                         font-weight: 600; 
//                         width: 28%; 
//                         color: var(--text-color, #1e293b); 
//                     }
//                     .logic-popup-table td:nth-child(2) { 
//                         width: 42%; 
//                         color: var(--text-muted, #475569); 
//                     }
//                     .logic-popup-table td:nth-child(3) { 
//                         width: 30%; 
//                         color: var(--text-color, #0f172a); 
//                         background: rgba(0,0,0,0.02);
//                     }
//                 </style>
//                 <div class="logic-popup-container">
//                     <table class="logic-popup-table">
//                         <thead>
//                             <tr>
//                                 <th>FIELDS</th>
//                                 <th>LOGICS</th>
//                                 <th>CALCULATION</th>
//                             </tr>
//                         </thead>
//                         <tbody>
//                             <tr><td>Operational Creches</td><td>No of Active/operational creches</td><td></td></tr>
//                             <tr><td>Cumulative Enrolled Children</td><td>Total children enrolled from starting date to selected date</td><td></td></tr>
//                             <tr><td>Total Universe (Measured Atleast Twice)</td><td>Those children whose first and last measurement is there</td><td></td></tr>
//                             <tr><td>Universe (Normal)</td><td>From the first measurement those children who are in Normal</td><td></td></tr>
//                             <tr><td>Universe (Moderate)</td><td>From the first measurement those children who are in Moderate</td><td></td></tr>
//                             <tr><td>Universe (Severe)</td><td>From the first measurement those children who are in Severe</td><td></td></tr>
//                             <tr><td>Universe (Recovery)</td><td>Universe Severe + Universe Moderate</td><td></td></tr>
//                             <tr><td>Universe (Deterioration)</td><td>Universe Normal + Universe Moderate</td><td></td></tr>
//                             <tr class="row-green"><td>Moderate to Normal</td><td>Changed category from moderate (first measurement) to Normal (last measurement)</td><td>total no (moderate to normal) / Universe(Moderate) * 100</td></tr>
//                             <tr class="row-green"><td>Severe to Moderate</td><td>Changed category from severe (first measurement) to moderate (last measurement)</td><td>total no (severe to moderate) / Universe(severe) * 100</td></tr>
//                             <tr class="row-green"><td>Severe to Normal</td><td>Changed category from severe (first measurement) to Normal (last measurement)</td><td>total no (severe to normal) / Universe(severe) * 100</td></tr>
//                             <tr><td>Total Recovery</td><td>moderate to normal + severe to moderate + severe to normal</td><td>total recovery no / Universe(Recovery) * 100</td></tr>
//                             <tr class="row-red"><td>Normal to Moderate</td><td>Changed category from normal (first measurement) to moderate (last measurement)</td><td>total no (normal to moderate) / Universe(normal) * 100</td></tr>
//                             <tr class="row-red"><td>Normal to Severe</td><td>Changed category from normal (first measurement) to severe (last measurement)</td><td>total no (normal to severe) / Universe(normal) * 100</td></tr>
//                             <tr class="row-red"><td>Moderate to Severe</td><td>Changed category from moderate (first measurement) to severe (last measurement)</td><td>total no (moderate to severe) / Universe(moderate) * 100</td></tr>
//                             <tr><td>Total Deterioration</td><td>normal to moderate + normal to severe + moderate to severe</td><td>total deterioration no / Universe(Deterioration) * 100</td></tr>
//                             <tr><td>No Change</td><td>severe to severe + moderate to moderate + normal to normal</td><td>total no change no / Total Universe(Measured Atleast Twice) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Severe to Severe</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (severe to severe) / Universe(severe) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Moderate to Moderate</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (moderate to moderate) / Universe(Moderate) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Normal to Normal</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (normal to normal) / Universe(normal) * 100</td></tr>
//                         </tbody>
//                     </table>
//                 </div>
//             `;

//             let dialog = new frappe.ui.Dialog({
//                 title: __('Field Logic'),
//                 size: 'extra-large',
//                 fields: [
//                     {
//                         fieldname: 'logic_html',
//                         fieldtype: 'HTML',
//                         options: html_content
//                     }
//                 ]
//             });
            
//             dialog.show();

//             // Insert Download PDF button in the header, left of the 'X' (Close) button
//             let $download_btn = $('<button class="btn btn-default btn-xs" style="margin-right: 15px;">' + __('Download Logic') + '</button>');
            
//             // Target the standard Frappe close button in the header
//             let $close_btn = dialog.$wrapper.find('.modal-header .btn-modal-close, .modal-header .close, .modal-header [data-dismiss="modal"]');
            
//             if ($close_btn.length) {
//                 $download_btn.insertBefore($close_btn);
//             } else {
//                 // Fallback if the specific structure isn't found
//                 dialog.$wrapper.find('.modal-header').append($download_btn);
//             }

//             // Handle print-to-pdf layout rendering
//             $download_btn.on('click', function() {
//                 let print_window = window.open('', '_blank');
//                 print_window.document.write(`
//                     <html>
//                         <head>
//                             <title>Field Logic</title>
//                         </head>
//                         <body>
//                             ${html_content}
//                             <script>
//                                 setTimeout(function() {
//                                     window.print();
//                                     window.close();
//                                 }, 250);
//                             </script>
//                         </body>
//                     </html>
//                 `);
//                 print_window.document.close();
//             });
//         });
//     }
// };


// // Helper function to sync creche_age with opening date filter
// function syncCrecheAgeWithOpeningDate() {
//     const value = frappe.query_report.get_filter_value("creche_age");
//     const type_field = frappe.query_report.get_filter("cr_opening_range_type");
//     const range_field = frappe.query_report.get_filter("c_opening_range");
//     const single_field = frappe.query_report.get_filter("single_date");
    
//     if (value) {
//         // Map age ranges to approximate months (using the middle/starting point of each range)
//         const months_map = {
//             "0-6 Month": 3,    // Using 3 months as representative (middle of 0-6)
//             "7-12 Month": 9,   // Using 9 months as representative (middle of 7-12)
//             "13-18 Month": 15, // Using 15 months as representative (middle of 13-18)
//             "19-24 Month": 21, // Using 21 months as representative (middle of 19-24)
//             "24+ Month": 24    // Using 24 months as minimum
//         };
        
//         const n_months = months_map[value];
        
//         if (n_months !== undefined) {
//             // Get current year and month from filters, or use current date
//             let curr_year = parseInt(frappe.query_report.get_filter_value("year")) || new Date().getFullYear();
//             let curr_month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
            
//             // Create date for the end of the selected month
//             let current_date = new Date(curr_year, curr_month, 0);
            
//             // Calculate past date by subtracting months
//             let past_date = new Date(current_date);
//             past_date.setMonth(past_date.getMonth() - n_months);
            
//             // Format date as YYYY-MM-DD
//             let date_str = past_date.getFullYear() + "-" +
//                            String(past_date.getMonth() + 1).padStart(2, '0') + "-" +
//                            String(past_date.getDate()).padStart(2, '0');
            
//             // Set filter values
//             frappe.query_report.set_filter_value("cr_opening_range_type", "after");
//             frappe.query_report.set_filter_value("single_date", date_str);
//             frappe.query_report.set_filter_value("c_opening_range", []);
            
//             // Toggle field visibility
//             toggleDateFields("after");
//         }
//     } else {
//         // Clear all related filters when creche_age is cleared
//         frappe.query_report.set_filter_value("cr_opening_range_type", "");
//         frappe.query_report.set_filter_value("single_date", "");
//         frappe.query_report.set_filter_value("c_opening_range", []);
//         toggleDateFields("");
//     }
// }

// // Helper function to toggle date fields based on selection
// function toggleDateFields(dateRangeType) {
//     const isBetween = dateRangeType === "between";
//     const isSingleDate = ["before", "after", "equal"].includes(dateRangeType);
//     const isCleared = dateRangeType === "";

//     frappe.query_report.get_filter("c_opening_range").toggle(isBetween);
//     frappe.query_report.get_filter("single_date").toggle(isSingleDate);

//     if (isBetween) {
//         frappe.query_report.set_filter_value("single_date", "");
//     } else if (isSingleDate) {
//         frappe.query_report.set_filter_value("c_opening_range", []);
//     }

//     if (isCleared) {
//         frappe.query_report.set_filter_value("c_opening_range", []);
//         frappe.query_report.set_filter_value("single_date", "");
//     }
// }







// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

// frappe.query_reports["Cohort Report (Creche Performance - Summary)"] = {
//     filters: [
//         {
//             fieldname: "year",
//             label: __("Year"),
//             fieldtype: "Select",
//             options: (() => {
//                 const start_year = 2022;
//                 const current_year = new Date().getFullYear();
//                 return Array.from(
//                     { length: current_year - start_year + 1 },
//                     (_, i) => (start_year + i).toString()
//                 );
//             })(),
//             default: new Date().getFullYear().toString(),
//             onchange: function () {
//                 frappe.query_report.refresh();
//             }
//         },
//         {
//             "fieldname": "month",
//             "label": __("Month"),
//             "fieldtype": "Select",
//             "options": [
//                 { "value": "1", "label": "January" },
//                 { "value": "2", "label": "February" },
//                 { "value": "3", "label": "March" },
//                 { "value": "4", "label": "April" },
//                 { "value": "5", "label": "May" },
//                 { "value": "6", "label": "June" },
//                 { "value": "7", "label": "July" },
//                 { "value": "8", "label": "August" },
//                 { "value": "9", "label": "September" },
//                 { "value": "10", "label": "October" },
//                 { "value": "11", "label": "November" },
//                 { "value": "12", "label": "December" }
//             ],
//             "default": (new Date().getMonth() + 1).toString(),
//             "on_change": function () {
//                 frappe.query_report.refresh();
//             }
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
//             fieldname: "level",
//             label: __("Level"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("Level") },
//                 { value: "1", label: __("Partner") },
//                 { value: "2", label: __("State") },
//                 { value: "3", label: __("District") },
//                 { value: "4", label: __("Block") },
//                 { value: "5", label: __("Supervisor") },
//                 { value: "6", label: __("GP") },
//                 { value: "7", label: __("Creche") },
//                 { value: "8", label: __("Age of creche") },
//                 { value: "9", label: __("Gender") },
//                 { value: "10", label: __("Age of Child") },
//                 { value: "11", label: __("Age at Enrollment") },
//                 { value: "12", label: __("Tenure of Stay at Creche") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
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
//                 { value: "normal", label: __("Normal") },
//                 { value: "moderate", label: __("Moderate") },
//                 { value: "severe", label: __("Severe") }
//             ],
//             default: "all",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         // {
//         //     fieldname: "attedance",
//         //     label: __("Attendance"),
//         //     fieldtype: "Select",
//         //     options: [
//         //         { value: "", label: __("") },
//         //         { value: "regular", label: __("Regular(=≥ 70%)") },
//         //         { value: "irregular", label: __("Irregular(=≤ 50%)") }
//         //     ],
//         //     default: "",
//         //     on_change() {
//         //         frappe.query_report.refresh();
//         //     }
//         // },
//         {
//             fieldname: "creche_age",
//             label: __("Age of Creche"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("") },
//                 { value: "0-6 Month", label: __("0-6 Month") },
//                 { value: "7-12 Month", label: __("7-12 Month") },
//                 { value: "13-18 Month", label: __("13-18 Month") },
//                 { value: "19-24 Month", label: __("19-24 Month") },
//                 { value: "24+ Month", label: __("24+ Month") }
//             ],
//             default: "",
//             on_change: function () {
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

//     formatter(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);
        
//         // Skip formatting for header row or if no data
//         if (!data || column.is_tree) return value;
        
//         // Define the numeric fields that should have their last value bold black
//         const numericFields = [
//             'operational_creches', 'enrolled_children', 'measurements_taken', 
//             'exited_children', 'measurements_data_not_available'
//         ];
        
//         // Check if this is the Total row by checking the 'is_total' field
//         const isTotalRow = !!data.is_total;

//         // Apply bold black formatting for numeric fields in the Total row
//         if (isTotalRow && numericFields.includes(column.fieldname)) {
//             return `<span style="font-weight: bold; color: #000;">${value}</span>`;
//         }
        
//         // Define color scheme for transition display fields
//         const highlightColors = {
//             // Positive transitions (improvement) - Green shades
//             'sv_md_display': '#FFFACD',    // Severe to Moderate (Light Yellow)
//             'md_nr_display': '#90EE90',    // Moderate to Normal (Light Green)
//             'sv_nr_display': '#90EE90',    // Severe to Normal (Light Green)
            
//             // Negative transitions (worsening) - Red shades
//             'nr_md_display': '#FFCCCB',    // Normal to Moderate (Light Red)
//             'md_sv_display': '#FFCCCB',    // Moderate to Severe (Light Red)
//             'nr_sv_display': '#FFCCCB',    // Normal to Severe (Light Red)
            
//             // No Change breakdown - Different shades for each category
//             'sv_sv_display': '#FFE4E1',    // Severe to Severe (Light Pink)
//             'md_md_display': '#FFFACD',    // Moderate to Moderate (Light Yellow)
//             'nr_nr_display': '#E6F3FF',    // Normal to Normal (Light Blue)
            
//             // Data not available - Light gray
//             'measurements_data_not_available': '#F5F5F5'
//         };
        
//         // Apply formatting for transition display fields
//         if (highlightColors[column.fieldname]) {
//             const style = isTotalRow ? 
//                 'font-weight: bold; color: #000; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;' :
//                 `background-color: ${highlightColors[column.fieldname]}; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;`;
//             return `<div style="${style}">${value}</div>`;
//         }
        
//         // Default formatting for other columns
//         return value;
//     },

//     // UI Professional & Scrollable Popup Code
//     onload: function(report) {
//         report.page.add_inner_button(__("Logic"), function() {
            
//             const html_content = `
//                 <style>
//                     .logic-popup-container {
//                         max-height: 65vh; /* Makes it vertically scrollable */
//                         overflow-y: auto;
//                         overflow-x: auto; /* Makes it responsive on mobile */
//                         border: 1px solid var(--border-color, #d1d8dd);
//                         border-radius: 8px;
//                         background-color: var(--card-bg, #ffffff);
//                         box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
//                     }
//                     .logic-popup-table { 
//                         width: 100%; 
//                         border-collapse: collapse; 
//                         font-family: inherit; 
//                         font-size: 13px;
//                         min-width: 700px; /* Prevents text crunching on small screens */
//                     }
//                     .logic-popup-table th, .logic-popup-table td { 
//                         border-bottom: 1px solid var(--border-color, #e2e8f0); 
//                         padding: 12px 16px; 
//                         text-align: left; 
//                         vertical-align: middle;
//                         line-height: 1.5;
//                     }
//                     /* Sticky Header Configuration */
//                     .logic-popup-table thead th { 
//                         position: sticky;
//                         top: 0;
//                         background-color: #d99694; 
//                         color: #ffffff; 
//                         font-weight: 600; 
//                         z-index: 10;
//                         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
//                         letter-spacing: 0.5px;
//                     }
//                     .logic-popup-table tbody tr:hover { 
//                         background-color: var(--table-row-hover, #f8fafc); 
//                     }
                    
//                     /* Professional Soft Color Indicators */
//                     .row-green { background-color: rgba(146, 208, 80, 0.1); }
//                     .row-green td:first-child { border-left: 4px solid #92d050; }
                    
//                     .row-red { background-color: rgba(255, 80, 80, 0.08); }
//                     .row-red td:first-child { border-left: 4px solid #ff5050; }
                    
//                     .row-blue { background-color: rgba(91, 155, 213, 0.1); }
//                     .row-blue td:first-child { border-left: 4px solid #5b9bd5; }
                    
//                     /* Column Widths and Typography */
//                     .logic-popup-table td:first-child { 
//                         font-weight: 600; 
//                         width: 28%; 
//                         color: var(--text-color, #1e293b); 
//                     }
//                     .logic-popup-table td:nth-child(2) { 
//                         width: 42%; 
//                         color: var(--text-muted, #475569); 
//                     }
//                     .logic-popup-table td:nth-child(3) { 
//                         width: 30%; 
//                         color: var(--text-color, #0f172a); 
//                         background: rgba(0,0,0,0.02);
//                     }
//                 </style>
//                 <div class="logic-popup-container">
//                     <table class="logic-popup-table">
//                         <thead>
//                             <tr>
//                                 <th>FIELDS</th>
//                                 <th>LOGICS</th>
//                                 <th>CALCULATION</th>
//                             </tr>
//                         </thead>
//                         <tbody>
//                             <tr><td>Operational Creches</td><td>No of Active/operational creches</td><td></td></tr>
//                             <tr><td>Cumulative Enrolled Children</td><td>Total children enrolled from starting date to selected date</td><td></td></tr>
//                             <tr><td>Total Universe (Measured Atleast Twice)</td><td>Those children whose first and last measurement is there</td><td></td></tr>
//                             <tr><td>Universe (Normal)</td><td>From the first measurement those children who are in Normal</td><td></td></tr>
//                             <tr><td>Universe (Moderate)</td><td>From the first measurement those children who are in Moderate</td><td></td></tr>
//                             <tr><td>Universe (Severe)</td><td>From the first measurement those children who are in Severe</td><td></td></tr>
//                             <tr><td>Universe (Recovery)</td><td>Universe Severe + Universe Moderate</td><td></td></tr>
//                             <tr><td>Universe (Deterioration)</td><td>Universe Normal + Universe Moderate</td><td></td></tr>
//                             <tr class="row-green"><td>Moderate to Normal</td><td>Changed category from moderate (first measurement) to Normal (last measurement)</td><td>total no (moderate to normal) / Universe(Moderate) * 100</td></tr>
//                             <tr class="row-green"><td>Severe to Moderate</td><td>Changed category from severe (first measurement) to moderate (last measurement)</td><td>total no (severe to moderate) / Universe(severe) * 100</td></tr>
//                             <tr class="row-green"><td>Severe to Normal</td><td>Changed category from severe (first measurement) to Normal (last measurement)</td><td>total no (severe to normal) / Universe(severe) * 100</td></tr>
//                             <tr><td>Total Recovery</td><td>moderate to normal + severe to moderate + severe to normal</td><td>total recovery no / Universe(Recovery) * 100</td></tr>
//                             <tr class="row-red"><td>Normal to Moderate</td><td>Changed category from normal (first measurement) to moderate (last measurement)</td><td>total no (normal to moderate) / Universe(normal) * 100</td></tr>
//                             <tr class="row-red"><td>Normal to Severe</td><td>Changed category from normal (first measurement) to severe (last measurement)</td><td>total no (normal to severe) / Universe(normal) * 100</td></tr>
//                             <tr class="row-red"><td>Moderate to Severe</td><td>Changed category from moderate (first measurement) to severe (last measurement)</td><td>total no (moderate to severe) / Universe(moderate) * 100</td></tr>
//                             <tr><td>Total Deterioration</td><td>normal to moderate + normal to severe + moderate to severe</td><td>total deterioration no / Universe(Deterioration) * 100</td></tr>
//                             <tr><td>No Change</td><td>severe to severe + moderate to moderate + normal to normal</td><td>total no change no / Total Universe(Measured Atleast Twice) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Severe to Severe</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (severe to severe) / Universe(severe) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Moderate to Moderate</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (moderate to moderate) / Universe(Moderate) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Normal to Normal</td><td>Remains in same category (first measurement to last measurement)</td><td>total no (normal to normal) / Universe(normal) * 100</td></tr>
//                         </tbody>
//                     </table>
//                 </div>
//             `;

//             let dialog = new frappe.ui.Dialog({
//                 title: __('Field Logic'),
//                 size: 'extra-large',
//                 fields: [
//                     {
//                         fieldname: 'logic_html',
//                         fieldtype: 'HTML',
//                         options: html_content
//                     }
//                 ]
//             });
            
//             dialog.show();
//         });
//     }
// };


// // Helper function to sync creche_age with opening date filter
// function syncCrecheAgeWithOpeningDate() {
//     const value = frappe.query_report.get_filter_value("creche_age");
//     const type_field = frappe.query_report.get_filter("cr_opening_range_type");
//     const range_field = frappe.query_report.get_filter("c_opening_range");
//     const single_field = frappe.query_report.get_filter("single_date");
    
//     if (value) {
//         // Map age ranges to approximate months (using the middle/starting point of each range)
//         const months_map = {
//             "0-6 Month": 3,    // Using 3 months as representative (middle of 0-6)
//             "7-12 Month": 9,   // Using 9 months as representative (middle of 7-12)
//             "13-18 Month": 15, // Using 15 months as representative (middle of 13-18)
//             "19-24 Month": 21, // Using 21 months as representative (middle of 19-24)
//             "24+ Month": 24    // Using 24 months as minimum
//         };
        
//         const n_months = months_map[value];
        
//         if (n_months !== undefined) {
//             // Get current year and month from filters, or use current date
//             let curr_year = parseInt(frappe.query_report.get_filter_value("year")) || new Date().getFullYear();
//             let curr_month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
            
//             // Create date for the end of the selected month
//             let current_date = new Date(curr_year, curr_month, 0);
            
//             // Calculate past date by subtracting months
//             let past_date = new Date(current_date);
//             past_date.setMonth(past_date.getMonth() - n_months);
            
//             // Format date as YYYY-MM-DD
//             let date_str = past_date.getFullYear() + "-" +
//                            String(past_date.getMonth() + 1).padStart(2, '0') + "-" +
//                            String(past_date.getDate()).padStart(2, '0');
            
//             // Set filter values
//             frappe.query_report.set_filter_value("cr_opening_range_type", "after");
//             frappe.query_report.set_filter_value("single_date", date_str);
//             frappe.query_report.set_filter_value("c_opening_range", []);
            
//             // Toggle field visibility
//             toggleDateFields("after");
//         }
//     } else {
//         // Clear all related filters when creche_age is cleared
//         frappe.query_report.set_filter_value("cr_opening_range_type", "");
//         frappe.query_report.set_filter_value("single_date", "");
//         frappe.query_report.set_filter_value("c_opening_range", []);
//         toggleDateFields("");
//     }
// }

// // Helper function to toggle date fields based on selection
// function toggleDateFields(dateRangeType) {
//     const isBetween = dateRangeType === "between";
//     const isSingleDate = ["before", "after", "equal"].includes(dateRangeType);
//     const isCleared = dateRangeType === "";

//     frappe.query_report.get_filter("c_opening_range").toggle(isBetween);
//     frappe.query_report.get_filter("single_date").toggle(isSingleDate);

//     if (isBetween) {
//         frappe.query_report.set_filter_value("single_date", "");
//     } else if (isSingleDate) {
//         frappe.query_report.set_filter_value("c_opening_range", []);
//     }

//     if (isCleared) {
//         frappe.query_report.set_filter_value("c_opening_range", []);
//         frappe.query_report.set_filter_value("single_date", "");
//     }
// }













// frappe.query_reports["Cohort Report (Creche Performance - Summary)"] = {
//     filters: [
// 		{
// 			fieldname: "year",
// 			label: __("Year"),
// 			fieldtype: "Select",
// 			options: (() => {
// 				const start_year = 2022;
// 				const current_year = new Date().getFullYear();
// 				return Array.from(
// 					{ length: current_year - start_year + 1 },
// 					(_, i) => (start_year + i).toString()
// 				);
// 			})(),
// 			default: new Date().getFullYear().toString(),
//             onchange: function () {
//                 frappe.query_report.refresh();
//             }
// 		},
// 		{
// 			"fieldname": "month",
// 			"label": __("Month"),
// 			"fieldtype": "Select",
// 			"options": [
// 				{ "value": "1", "label": "January" },
// 				{ "value": "2", "label": "February" },
// 				{ "value": "3", "label": "March" },
// 				{ "value": "4", "label": "April" },
// 				{ "value": "5", "label": "May" },
// 				{ "value": "6", "label": "June" },
// 				{ "value": "7", "label": "July" },
// 				{ "value": "8", "label": "August" },
// 				{ "value": "9", "label": "September" },
// 				{ "value": "10", "label": "October" },
// 				{ "value": "11", "label": "November" },
// 				{ "value": "12", "label": "December" }
// 			],
// 			"default": (new Date().getMonth() + 1).toString(),
// 			"on_change": function () {
// 				frappe.query_report.refresh();
// 			}
// 		},
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
//             fieldname: "level",
//             label: __("Level"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("Level") },
//                 { value: "1", label: __("Partner") },
//                 { value: "2", label: __("State") },
//                 { value: "3", label: __("District") },
//                 { value: "4", label: __("Block") },
//                 { value: "5", label: __("Supervisor") },
//                 { value: "6", label: __("GP") },
//                 { value: "7", label: __("Creche") },
//                 { value: "8", label: __("Age of creche") },
//                 { value: "9", label: __("Gender") },
//                 { value: "10", label: __("Age of Child") },
//                 { value: "11", label: __("Age at Enrollment") },
//                 { value: "12", label: __("Tenure of Stay at Creche") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
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
//                 { value: "normal", label: __("Normal") },
//                 { value: "moderate", label: __("Moderate") },
//                 { value: "severe", label: __("Severe") }
//             ],
//             default: "all",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
//         // {
//         //     fieldname: "attedance",
//         //     label: __("Attendance"),
//         //     fieldtype: "Select",
//         //     options: [
//         //         { value: "", label: __("") },
//         //         { value: "regular", label: __("Regular(=≥ 70%)") },
//         //         { value: "irregular", label: __("Irregular(=≤ 50%)") }
//         //     ],
//         //     default: "",
//         //     on_change() {
//         //         frappe.query_report.refresh();
//         //     }
//         // },
//         {
//             fieldname: "creche_age",
//             label: __("Age of Creche"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("") },
//                 { value: "0-6 Month", label: __("0-6 Month") },
//                 { value: "7-12 Month", label: __("7-12 Month") },
//                 { value: "13-18 Month", label: __("13-18 Month") },
//                 { value: "19-24 Month", label: __("19-24 Month") },
//                 { value: "24+ Month", label: __("24+ Month") }
//             ],
//             default: "",
//             on_change: function () {
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

//     formatter(value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);
        
//         // Skip formatting for header row or if no data
//         if (!data || column.is_tree) return value;
        
//         // Define the numeric fields that should have their last value bold black
//         const numericFields = [
//             'operational_creches', 'enrolled_children', 'measurements_taken', 
//             'exited_children', 'measurements_data_not_available'
//         ];
        
//         // Check if this is the Total row by checking the 'is_total' field
//         const isTotalRow = !!data.is_total;

        
//         // Apply bold black formatting for numeric fields in the Total row
//         if (isTotalRow && numericFields.includes(column.fieldname)) {
//             return `<span style="font-weight: bold; color: #000;">${value}</span>`;
//         }
        
//         // Define color scheme for transition display fields
//         const highlightColors = {
//             // Positive transitions (improvement) - Green shades
//             'sv_md_display': '#FFFACD',    // Severe to Moderate (Light Yellow)
//             'md_nr_display': '#90EE90',    // Moderate to Normal (Light Green)
//             'sv_nr_display': '#90EE90',    // Severe to Normal (Light Green)
            
//             // Negative transitions (worsening) - Red shades
//             'nr_md_display': '#FFCCCB',    // Normal to Moderate (Light Red)
//             'md_sv_display': '#FFCCCB',    // Moderate to Severe (Light Red)
//             'nr_sv_display': '#FFCCCB',    // Normal to Severe (Light Red)
            
//             // No Change breakdown - Different shades for each category
//             'sv_sv_display': '#FFE4E1',    // Severe to Severe (Light Pink)
//             'md_md_display': '#FFFACD',    // Moderate to Moderate (Light Yellow)
//             'nr_nr_display': '#E6F3FF',    // Normal to Normal (Light Blue)
            
//             // Data not available - Light gray
//             'measurements_data_not_available': '#F5F5F5'
//         };
        
//         // Apply formatting for transition display fields
//         if (highlightColors[column.fieldname]) {
//             const style = isTotalRow ? 
//                 'font-weight: bold; color: #000; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;' :
//                 `background-color: ${highlightColors[column.fieldname]}; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;`;
//             return `<div style="${style}">${value}</div>`;
//         }
        
//         // Default formatting for other columns
//         return value;
//     }

// };


// // Helper function to sync creche_age with opening date filter
// function syncCrecheAgeWithOpeningDate() {
//     const value = frappe.query_report.get_filter_value("creche_age");
//     const type_field = frappe.query_report.get_filter("cr_opening_range_type");
//     const range_field = frappe.query_report.get_filter("c_opening_range");
//     const single_field = frappe.query_report.get_filter("single_date");
    
//     if (value) {
//         // Map age ranges to approximate months (using the middle/starting point of each range)
//         const months_map = {
//             "0-6 Month": 3,    // Using 3 months as representative (middle of 0-6)
//             "7-12 Month": 9,    // Using 9 months as representative (middle of 7-12)
//             "13-18 Month": 15,  // Using 15 months as representative (middle of 13-18)
//             "19-24 Month": 21,  // Using 21 months as representative (middle of 19-24)
//             "24+ Month": 24     // Using 24 months as minimum
//         };
        
//         const n_months = months_map[value];
        
//         if (n_months !== undefined) {
//             // Get current year and month from filters, or use current date
//             let curr_year = parseInt(frappe.query_report.get_filter_value("year")) || new Date().getFullYear();
//             let curr_month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
            
//             // Create date for the end of the selected month
//             let current_date = new Date(curr_year, curr_month, 0);
            
//             // Calculate past date by subtracting months
//             let past_date = new Date(current_date);
//             past_date.setMonth(past_date.getMonth() - n_months);
            
//             // Format date as YYYY-MM-DD
//             let date_str = past_date.getFullYear() + "-" +
//                            String(past_date.getMonth() + 1).padStart(2, '0') + "-" +
//                            String(past_date.getDate()).padStart(2, '0');
            
//             // Set filter values
//             frappe.query_report.set_filter_value("cr_opening_range_type", "after");
//             frappe.query_report.set_filter_value("single_date", date_str);
//             frappe.query_report.set_filter_value("c_opening_range", []);
            
//             // Toggle field visibility
//             toggleDateFields("after");
//         }
//     } else {
//         // Clear all related filters when creche_age is cleared
//         frappe.query_report.set_filter_value("cr_opening_range_type", "");
//         frappe.query_report.set_filter_value("single_date", "");
//         frappe.query_report.set_filter_value("c_opening_range", []);
//         toggleDateFields("");
//     }
// }

// // Helper function to toggle date fields based on selection
// function toggleDateFields(dateRangeType) {
//     const isBetween = dateRangeType === "between";
//     const isSingleDate = ["before", "after", "equal"].includes(dateRangeType);
//     const isCleared = dateRangeType === "";

//     frappe.query_report.get_filter("c_opening_range").toggle(isBetween);
//     frappe.query_report.get_filter("single_date").toggle(isSingleDate);

//     if (isBetween) {
//         frappe.query_report.set_filter_value("single_date", "");
//     } else if (isSingleDate) {
//         frappe.query_report.set_filter_value("c_opening_range", []);
//     }

//     if (isCleared) {
//         frappe.query_report.set_filter_value("c_opening_range", []);
//         frappe.query_report.set_filter_value("single_date", "");
//     }
// }