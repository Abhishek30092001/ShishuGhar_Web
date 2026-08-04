// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Enrollment Cumulative Report"] = {
    "filters": [
        {
            fieldname: "date_input_type",
            label: __("Date Input Type"),
            fieldtype: "Select",
            options: [
                { value: "date_range", label: __("Date Range") },
                { value: "month_year", label: __("Month/Year") }
            ],
            default: "date_range",
            on_change: function () {
                const dateInputType = frappe.query_report.get_filter_value("date_input_type");

                if (dateInputType === "date_range") {
                    // Reset year & month
                    frappe.query_report.set_filter_value("year", "");
                    frappe.query_report.set_filter_value("month", "");
                    frappe.query_report.set_filter_value("time_range", [frappe.datetime.month_start(), frappe.datetime.month_end()]);

                    // Remove month/year filters dynamically
                    frappe.query_report.get_filter("year").toggle(false);
                    frappe.query_report.get_filter("month").toggle(false);
                    frappe.query_report.get_filter("time_range").toggle(true);
                } else if (dateInputType === "month_year") {
                    // Reset date range
                    frappe.query_report.set_filter_value("time_range", "");

                    // Set default year & month
                    frappe.query_report.set_filter_value("year", frappe.datetime.get_today().split('-')[0]);
                    frappe.query_report.set_filter_value("month", frappe.datetime.get_today().split('-')[1]);

                    // Remove date range filter dynamically
                    frappe.query_report.get_filter("time_range").toggle(false);
                    frappe.query_report.get_filter("year").toggle(true);
                    frappe.query_report.get_filter("month").toggle(true);
                }

                // Refresh the report for changes to take effect
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "time_range",
            label: __("Date Range"),
            fieldtype: "DateRange",
            default: [frappe.datetime.month_start(), frappe.datetime.month_end()],
            hidden: 0 // Initially visible
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: ["2024", "2025","2026"],
            default: frappe.datetime.get_today().split('-')[0],
            hidden: 1 // Initially hidden
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            options: [
                { value: "01", label: "January" },
                { value: "02", label: "February" },
                { value: "03", label: "March" },
                { value: "04", label: "April" },
                { value: "05", label: "May" },
                { value: "06", label: "June" },
                { value: "07", label: "July" },
                { value: "08", label: "August" },
                { value: "09", label: "September" },
                { value: "10", label: "October" },
                { value: "11", label: "November" },
                { value: "12", label: "December" }
            ],
            default: frappe.datetime.get_today().split('-')[1],
            hidden: 1 // Initially hidden
        },
        {
            "fieldname": "partner",
            "label": __("Partner"),
            "fieldtype": "Link",
            "options": "Partner",
            "default": frappe.defaults.get_user_default("partner"),
            "on_change": function () {
                frappe.query_report.refresh();
            }
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
            "reqd": 0,
            "get_query": function () {
                let district_name = frappe.query_report.get_filter_value("district_name");
                return {
                    filters: {
                        district_id: district_name ? district_name : undefined
                    }
                };
            }
        },
        {
            "fieldname": "gp",
            "label": __("Gram Panchayat"),
            "fieldtype": "Link",
            "options": "Gram Panchayat",
            "reqd": 0,
            "get_query": function () {
                let block_name = frappe.query_report.get_filter_value("block_name");
                return {
                    filters: {
                        block_id: block_name ? block_name : undefined
                    }
                };
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
            "fieldname": "creche",
            "label": __("Creche"),
            "fieldtype": "Link",
            "options": "Creche",
            "reqd": 0
        },
        {
            "fieldname": "level",
            "label": __("Level"),
            "fieldtype": "Select",
            "options": [
                { "value": "", "label": __("Level") },
                { "value": "1", "label": __("Partner") },
                { "value": "2", "label": __("State") },
                { "value": "3", "label": __("District") },
                { "value": "4", "label": __("Block") },
                { "value": "5", "label": __("Supervisor") },
                { "value": "6", "label": __("GP") },
                { "value": "7", "label": __("Creche") },

            ],
            "default": "",
            "on_change": function () {
                frappe.query_report.refresh();
            }
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

    // Added onload to append the custom Download Report button
    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });
    },

// Added onload to append the custom Download Report button and Show Logic button
    onload: function (report) {
        // 1. Existing Download Report Button
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        // 2. New Show Logic Button
        report.page.add_inner_button(__("Logic"), function () {
            
            // Define the logic data array (used for both the HTML table and the CSV)
            const logicData = [
                ["Card Title", "Logic"],
                ["Operational Creches", "Total number of unique creches that were opened on or before the selected end date (respecting applied filters)."],
                ["Total No of Children (HH List)", "Total number of distinct children surveyed in the Household Child Form, specifically those where a Date of Birth (DOB) is recorded."],
                ["Cumulative Enrolled", "Total count of all child enrollment records where the date of enrollment is on or before the selected end date."],
                ["Cumulative Current Enrolled", "Total number of enrolled children who are currently active (no exit date, or exit date strictly after the selected end date)."],
                ["Cumulative Exit", "Total number of children who have left the creche (recorded exit date falls on or before the selected end date)."],
                ["Cumulative Migrated", "Total number of exited children (on or before end date) where reason for leaving is Migrated (Code 1)."],
                ["Cumulative Graduated", "Total number of exited children (on or before end date) where reason for leaving is Graduated (Code 2)."],
                ["Cumulative Not Willing to Stay", "Total number of exited children (on or before end date) where reason for leaving is Not Willing to Stay (Code 3)."],
                ["Cumulative Death", "Total number of exited children (on or before end date) where reason for leaving is Death (Code 4)."],
                ["Other", "Total number of exited children (on or before end date) where reason for leaving is Other (Code 5)."]
            ];

            // Build the HTML Table for the Popup
            let htmlTable = `<table class="table table-bordered" style="margin-bottom: 0;">
                <thead style="background-color: #f3f3f3;">
                    <tr>
                        <th style="width: 30%;">Card Title</th>
                        <th>Logic</th>
                    </tr>
                </thead>
                <tbody>`;
            
            for (let i = 1; i < logicData.length; i++) {
                htmlTable += `<tr>
                    <td><b>${logicData[i][0]}</b></td>
                    <td>${logicData[i][1]}</td>
                </tr>`;
            }
            htmlTable += `</tbody></table>`;

            // Create and show the Frappe Dialog
            let d = new frappe.ui.Dialog({
                title: __("Report Field Logic"),
                size: "extra-large", // Changed from "large" to "extra-large" to make it wider
                fields: [
                    {
                        fieldname: "logic_html",
                        fieldtype: "HTML",
                        options: htmlTable
                    }
                ],
                primary_action_label: __("Download CSV"),
                primary_action: function() {
                    // Logic to build and download the CSV
                    let csvContent = "data:text/csv;charset=utf-8,";
                    
                    logicData.forEach(function(rowArray) {
                        // Wrap text in double quotes to safely handle commas inside the text
                        let row = rowArray.map(str => '"' + str.replace(/"/g, '""') + '"').join(",");
                        csvContent += row + "\r\n";
                    });

                    // Trigger the browser download
                    let encodedUri = encodeURI(csvContent);
                    let link = document.createElement("a");
                    link.setAttribute("href", encodedUri);
                    link.setAttribute("download", "Report_Logic_Definitions.csv");
                    document.body.appendChild(link); // Required for Firefox
                    link.click();
                    link.remove();
                }
            });

            d.show();
        });
    }
};