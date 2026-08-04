frappe.query_reports["Test Script Report"] = {
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
                { value: "12", label: __("Tenure of Stay at Creche") }
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
            fieldname: "attedance",
            label: __("Attendance"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("") },
                { value: "regular", label: __("Regular(=≥ 70%)") },
                { value: "irregular", label: __("Irregular(=≤ 50%)") }
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
        
        if (!data || column.is_tree) return value;
        
        const numericFields = [
            'operational_creches', 'enrolled_children', 'measurements_taken', 
            'exited_children', 'measurements_data_not_available'
        ];
        
        const isTotalRow = !!data.is_total;

        if (isTotalRow && numericFields.includes(column.fieldname)) {
            return `<span style="font-weight: bold; color: #000;">${value}</span>`;
        }
        
        const highlightColors = {
            'sv_md_display': '#FFFACD',
            'md_nr_display': '#90EE90',
            'sv_nr_display': '#90EE90',
            'nr_md_display': '#FFCCCB',
            'md_sv_display': '#FFCCCB',
            'nr_sv_display': '#FFCCCB',
            'sv_sv_display': '#FFE4E1',
            'md_md_display': '#FFFACD',
            'nr_nr_display': '#E6F3FF',
            'measurements_data_not_available': '#F5F5F5'
        };
        
        if (highlightColors[column.fieldname]) {
            const style = isTotalRow ? 
                'font-weight: bold; color: #000; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;' :
                `background-color: ${highlightColors[column.fieldname]}; text-align: center; height: 100%; width: 100%; display: flex; align-items: center; justify-content: center; padding: 5px; border-radius: 3px; border: 1px solid #eee;`;
            return `<div style="${style}">${value}</div>`;
        }
        
        return value;
    },

    // MODERN REACT-LIKE UI FOR POPUP
    onload: function(report) {
        report.page.add_inner_button(__("Logic"), function() {
            
            const html_content = `
                <style>
                    .react-modal-wrapper {
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                        display: flex;
                        flex-direction: column;
                        gap: 16px;
                        padding: 4px;
                    }
                    .modal-header-actions {
                        display: flex;
                        justify-content: flex-end;
                    }
                    .btn-react-download {
                        background-color: #2563eb;
                        color: #ffffff;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 6px;
                        font-size: 14px;
                        font-weight: 500;
                        cursor: pointer;
                        display: inline-flex;
                        align-items: center;
                        gap: 8px;
                        transition: all 0.2s ease-in-out;
                        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                    }
                    .btn-react-download:hover {
                        background-color: #1d4ed8;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        transform: translateY(-1px);
                    }
                    .btn-react-download svg {
                        width: 16px;
                        height: 16px;
                    }
                    .table-scroll-container {
                        max-height: 60vh;
                        overflow-y: auto;
                        overflow-x: auto;
                        border-radius: 8px;
                        border: 1px solid #e2e8f0;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        background-color: #ffffff;
                    }
                    .modern-react-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 13px;
                        min-width: 700px;
                    }
                    .modern-react-table th, .modern-react-table td {
                        padding: 12px 16px;
                        border-bottom: 1px solid #e2e8f0;
                        border-right: 1px solid #e2e8f0;
                        text-align: left;
                        line-height: 1.5;
                    }
                    .modern-react-table th:last-child, .modern-react-table td:last-child {
                        border-right: none;
                    }
                    .modern-react-table thead th {
                        position: sticky;
                        top: 0;
                        background-color: #d99694; 
                        color: #111827;
                        font-weight: 600;
                        z-index: 10;
                        box-shadow: 0 1px 0 #e2e8f0;
                        backdrop-filter: blur(8px);
                    }
                    .modern-react-table tbody tr:last-child td {
                        border-bottom: none;
                    }
                    /* Base row styling */
                    .modern-react-table td:first-child { font-weight: 600; color: #1e293b; width: 25%; }
                    .modern-react-table td:nth-child(2) { color: #334155; width: 45%; }
                    .modern-react-table td:nth-child(3) { color: #475569; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; width: 30%; background-color: #f8fafc; }
                    
                    /* Modern subtle background colors */
                    .row-green td { background-color: #dcfce7 !important; color: #166534 !important; }
                    .row-red td { background-color: #fee2e2 !important; color: #991b1b !important; }
                    .row-blue td { background-color: #e0f2fe !important; color: #075985 !important; }

                    /* Maintain formula background visibility on colored rows */
                    .row-green td:nth-child(3) { background-color: #bbf7d0 !important; }
                    .row-red td:nth-child(3) { background-color: #fecaca !important; }
                    .row-blue td:nth-child(3) { background-color: #bae6fd !important; }
                </style>

                <div class="react-modal-wrapper">
                    <div class="modal-header-actions">
                        <button id="downloadPdfBtn" class="btn-react-download">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                            Download PDF
                        </button>
                    </div>
                    
                    <div class="table-scroll-container" id="printableTableContent">
                        <table class="modern-react-table">
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
                                
                                <tr class="row-green"><td>Moderate to Normal</td><td>changed category from moderate(first measurement) to Normal(last measurement)</td><td>total no(moderate to normal)/Universe(Moderate)*100</td></tr>
                                <tr class="row-green"><td>Severe to Moderate</td><td>changed category from severe(first measurement) to moderate(last measurement)</td><td>total no(severe to moderate)/Universe(severe)*100</td></tr>
                                <tr class="row-green"><td>Severe to Normal</td><td>changed category from severe(first measurement) to Normal(last measurement)</td><td>total no(severe to normal)/Universe(severe)*100</td></tr>
                                <tr><td>Total Recovery</td><td>moderate to normal + severe to moderate + severe to normal</td><td>total recovery no/Universe(Recovery)*100</td></tr>
                                
                                <tr class="row-red"><td>Normal to Moderate</td><td>changed category from normal(first measurement) to moderate(last measurement)</td><td>total no(normal to moderate)/Universe(normal)*100</td></tr>
                                <tr class="row-red"><td>Normal to Severe</td><td>changed category from normal(first measurement) to severe(last measurement)</td><td>total no(normal to severe)/Universe(normal)*100</td></tr>
                                <tr class="row-red"><td>Moderate to Severe</td><td>changed category from moderate(first measurement) to severe(last measurement)</td><td>total no(moderate to severe)/Universe(moderate)*100</td></tr>
                                <tr><td>Total Deterioration</td><td>normal to moderate + normal to severe + moderate to severe</td><td>total deterioration no/Universe(Deterioration)*100</td></tr>
                                <tr><td>No Change</td><td>severe to severe + moderate to moderate + normal to normal</td><td>total no change no/Total Universe(Measured Atleast Twice)*100</td></tr>
                                
                                <tr class="row-blue"><td>(No Change) Severe to Severe</td><td>remains in same category (first measurement to last measurement)</td><td>total no(severe to severe)/Universe(severe)*100</td></tr>
                                <tr class="row-blue"><td>(No Change) Moderate to Moderate</td><td>remains in same category (first measurement to last measurement)</td><td>total no(moderate to moderate)/Universe(Moderate)*100</td></tr>
                                <tr class="row-blue"><td>(No Change) Normal to Normal</td><td>remains in same category (first measurement to last measurement)</td><td>total no(normal to normal)/Universe(normal)*100</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            `;

            let dialog = new frappe.ui.Dialog({
                title: __('Child Nutrition Metrics Logic'),
                size: 'extra-large',
                fields: [{ fieldname: 'logic_html', fieldtype: 'HTML', options: html_content }]
            });
            
            dialog.show();

            // Bind PDF Download Event after dialog opens
            setTimeout(() => {
                document.getElementById('downloadPdfBtn').addEventListener('click', function() {
                    let printWindow = window.open('', '_blank', 'height=800,width=1200');
                    let tableHTML = document.getElementById('printableTableContent').innerHTML;
                    
                    printWindow.document.write(`
                        <!DOCTYPE html>
                        <html>
                            <head>
                                <title>Metrics Logic PDF</title>
                                <style>
                                    body { font-family: -apple-system, sans-serif; padding: 20px; }
                                    h2 { color: #1f2937; text-align: center; margin-bottom: 20px; }
                                    table { width: 100%; border-collapse: collapse; font-size: 12px; }
                                    th, td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; }
                                    th { background-color: #d99694 !important; color: black; font-weight: bold; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                                    td:first-child { font-weight: bold; width: 25%; }
                                    td:nth-child(2) { width: 45%; }
                                    td:nth-child(3) { width: 30%; }
                                    
                                    /* Force background colors for printing */
                                    .row-green td { background-color: #92d050 !important; color: black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                                    .row-red td { background-color: #ff5050 !important; color: black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                                    .row-blue td { background-color: #5b9bd5 !important; color: black !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                                </style>
                            </head>
                            <body>
                                <h2>Child Nutrition Metrics Logic</h2>
                                ${tableHTML}
                                <script>
                                    window.onload = function() {
                                        setTimeout(function() {
                                            window.print();
                                            window.close();
                                        }, 500); // Small delay to ensure styles apply before printing
                                    };
                                </script>
                            </body>
                        </html>
                    `);
                    printWindow.document.close();
                });
            }, 500);
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
        const months_map = {
            "0-6 Month": 3,   
            "7-12 Month": 9,  
            "13-18 Month": 15, 
            "19-24 Month": 21, 
            "24+ Month": 24   
        };
        
        const n_months = months_map[value];
        
        if (n_months !== undefined) {
            let curr_year = parseInt(frappe.query_report.get_filter_value("year")) || new Date().getFullYear();
            let curr_month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
            
            let current_date = new Date(curr_year, curr_month, 0);
            let past_date = new Date(current_date);
            past_date.setMonth(past_date.getMonth() - n_months);
            
            let date_str = past_date.getFullYear() + "-" +
                           String(past_date.getMonth() + 1).padStart(2, '0') + "-" +
                           String(past_date.getDate()).padStart(2, '0');
            
            frappe.query_report.set_filter_value("cr_opening_range_type", "after");
            frappe.query_report.set_filter_value("single_date", date_str);
            frappe.query_report.set_filter_value("c_opening_range", []);
            
            toggleDateFields("after");
        }
    } else {
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






// frappe.query_reports["Test Script Report"] = {
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
//         {
//             fieldname: "attedance",
//             label: __("Attendance"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("") },
//                 { value: "regular", label: __("Regular(=≥ 70%)") },
//                 { value: "irregular", label: __("Irregular(=≤ 50%)") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
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
//                 title: __('Child Nutrition Metrics Logic'),
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











// frappe.query_reports["Test Script Report"] = {
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
//         {
//             fieldname: "attedance",
//             label: __("Attendance"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("") },
//                 { value: "regular", label: __("Regular(=≥ 70%)") },
//                 { value: "irregular", label: __("Irregular(=≤ 50%)") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
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

//     // ONLOAD FUNCTION WITH PROFESSIONAL UI
//     onload: function(report) {
//         report.page.add_inner_button(__("Logic"), function() {
            
//             // Professional UI HTML & CSS
//             const html_content = `
//                 <style>
//                     .logic-card {
//                         background: #ffffff;
//                         border-radius: 8px;
//                         overflow: hidden;
//                         border: 1px solid #e5e7eb;
//                         margin-bottom: 15px;
//                     }
//                     .logic-table {
//                         width: 100%;
//                         border-collapse: collapse;
//                         font-family: inherit; /* Adopts Frappe's system font */
//                         font-size: 13px;
//                         color: #374151;
//                     }
//                     .logic-table th, .logic-table td {
//                         padding: 12px 16px;
//                         border-bottom: 1px solid #f3f4f6;
//                         text-align: left;
//                         vertical-align: top;
//                     }
//                     .logic-table thead th {
//                         background-color: #f9fafb;
//                         font-weight: 600;
//                         color: #111827;
//                         text-transform: uppercase;
//                         font-size: 11px;
//                         letter-spacing: 0.05em;
//                         border-bottom: 2px solid #e5e7eb;
//                     }
//                     .logic-table tbody tr:last-child td {
//                         border-bottom: none;
//                     }
//                     .logic-table td:first-child {
//                         font-weight: 500;
//                         color: #111827;
//                         width: 25%;
//                     }
//                     .logic-table td:nth-child(2) {
//                         width: 45%;
//                         line-height: 1.5;
//                     }
//                     .logic-table td:nth-child(3) {
//                         width: 30%;
//                         font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
//                         font-size: 12px;
//                         color: #4b5563;
//                         background-color: #f9fafb; /* Slight highlight for code/formulas */
//                     }
                    
//                     /* Soft Modern Status Colors */
//                     .row-green { background-color: #f0fdf4; } /* Emerald-50 */
//                     .row-red { background-color: #fef2f2; }   /* Red-50 */
//                     .row-blue { background-color: #eff6ff; }  /* Blue-50 */
                    
//                     /* Optional: slight left border for extra clarity */
//                     .row-green td:first-child { border-left: 3px solid #22c55e; }
//                     .row-red td:first-child { border-left: 3px solid #ef4444; }
//                     .row-blue td:first-child { border-left: 3px solid #3b82f6; }
//                 </style>
                
//                 <div class="logic-card">
//                     <table class="logic-table">
//                         <thead>
//                             <tr>
//                                 <th>Fields</th>
//                                 <th>Logics</th>
//                                 <th>Calculation</th>
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
                            
//                             <tr class="row-green"><td>Moderate to Normal</td><td>Changed category from moderate (first measurement) to Normal (last measurement)</td><td>(moderate_to_normal / Universe_Moderate) * 100</td></tr>
//                             <tr class="row-green"><td>Severe to Moderate</td><td>Changed category from severe (first measurement) to moderate (last measurement)</td><td>(severe_to_moderate / Universe_Severe) * 100</td></tr>
//                             <tr class="row-green"><td>Severe to Normal</td><td>Changed category from severe (first measurement) to Normal (last measurement)</td><td>(severe_to_normal / Universe_Severe) * 100</td></tr>
                            
//                             <tr><td>Total Recovery</td><td>moderate to normal + severe to moderate + severe to normal</td><td>(total_recovery / Universe_Recovery) * 100</td></tr>
                            
//                             <tr class="row-red"><td>Normal to Moderate</td><td>Changed category from normal (first measurement) to moderate (last measurement)</td><td>(normal_to_moderate / Universe_Normal) * 100</td></tr>
//                             <tr class="row-red"><td>Normal to Severe</td><td>Changed category from normal (first measurement) to severe (last measurement)</td><td>(normal_to_severe / Universe_Normal) * 100</td></tr>
//                             <tr class="row-red"><td>Moderate to Severe</td><td>Changed category from moderate (first measurement) to severe (last measurement)</td><td>(moderate_to_severe / Universe_Moderate) * 100</td></tr>
                            
//                             <tr><td>Total Deterioration</td><td>normal to moderate + normal to severe + moderate to severe</td><td>(total_deterioration / Universe_Deterioration) * 100</td></tr>
//                             <tr><td>No Change</td><td>severe to severe + moderate to moderate + normal to normal</td><td>(total_no_change / Total_Universe) * 100</td></tr>
                            
//                             <tr class="row-blue"><td>(No Change) Severe to Severe</td><td>Remains in same category (first measurement to last measurement)</td><td>(severe_to_severe / Universe_Severe) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Moderate to Moderate</td><td>Remains in same category (first measurement to last measurement)</td><td>(moderate_to_moderate / Universe_Moderate) * 100</td></tr>
//                             <tr class="row-blue"><td>(No Change) Normal to Normal</td><td>Remains in same category (first measurement to last measurement)</td><td>(normal_to_normal / Universe_Normal) * 100</td></tr>
//                         </tbody>
//                     </table>
//                 </div>
//             `;

//             let dialog = new frappe.ui.Dialog({
//                 title: __('Logics'),
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
//             "0-6 Month": 3,    
//             "7-12 Month": 9,   
//             "13-18 Month": 15, 
//             "19-24 Month": 21, 
//             "24+ Month": 24    
//         };
        
//         const n_months = months_map[value];
        
//         if (n_months !== undefined) {
//             let curr_year = parseInt(frappe.query_report.get_filter_value("year")) || new Date().getFullYear();
//             let curr_month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
            
//             let current_date = new Date(curr_year, curr_month, 0);
            
//             let past_date = new Date(current_date);
//             past_date.setMonth(past_date.getMonth() - n_months);
            
//             let date_str = past_date.getFullYear() + "-" +
//                            String(past_date.getMonth() + 1).padStart(2, '0') + "-" +
//                            String(past_date.getDate()).padStart(2, '0');
            
//             frappe.query_report.set_filter_value("cr_opening_range_type", "after");
//             frappe.query_report.set_filter_value("single_date", date_str);
//             frappe.query_report.set_filter_value("c_opening_range", []);
            
//             toggleDateFields("after");
//         }
//     } else {
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

// // Copyright (c) 2025, Frappe Technologies and contributors
// // For license information, please see license.txt

// frappe.query_reports["Test Script Report"] = {
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
//         {
//             fieldname: "attedance",
//             label: __("Attendance"),
//             fieldtype: "Select",
//             options: [
//                 { value: "", label: __("") },
//                 { value: "regular", label: __("Regular(=≥ 70%)") },
//                 { value: "irregular", label: __("Irregular(=≤ 50%)") }
//             ],
//             default: "",
//             on_change() {
//                 frappe.query_report.refresh();
//             }
//         },
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