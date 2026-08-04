frappe.query_reports["Average Attendance Summary"] = {
    filters: [
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
            ],
            default: "",
            on_change: function () {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "band",
            label: __("Attendance (%) Slab"),
            fieldtype: "Select",
            options: [
                { value: " ", label: __("Attendance (%) Slab") },
                { value: "1", label: __("0 to 25") },
                { value: "2", label: __("26 to 50") },
                { value: "3", label: __("51 to 75") },
                { value: "4", label: __("76 to 100") },
            ],
            default: "",
            on_change: function () {
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

        report.page.add_inner_button(__("Logic"), function () {
            const logicData = [
                { field: "Active Creches", logic: "The total number of daycare centers currently open and operating." },
                { field: "Eligible Children", logic: "The total number of children in the surrounding area who are the right age to attend." },
                { field: "Enrolled Children", logic: "The total number of children officially registered at the center." },
                { field: "Enrolled Children (%)", logic: "What percentage of the eligible neighborhood kids are actually signed up. (Are we reaching the community?)" },
                { field: "Children Attended Creche atleast one day", logic: "The number of registered children who actually showed up at least once during the selected time frame." },
                { field: "Children Attended (%)", logic: "What percentage of the registered kids actually came in. (If this is low, kids are registered on paper but not attending)." },
                { field: "Sum of Open Days for All Individual Children", logic: "The maximum total days kids could have been there. (Calculated by multiplying the number of enrolled children by the days the center was open)." },
                { field: "Sum of Days Attended", logic: "The actual total number of days all children sat in the center combined." },
                { field: "Attendance (%)", logic: "The overall health metric. How \"full\" the center was compared to its absolute maximum capacity." },
                { field: "Avg. Attendance Per Day", logic: "The average number of children present on a typical open day." },
                { field: "Min. Attendance", logic: "The lowest headcount on any single open day. (e.g., The quietest day of the month)." },
                { field: "Mean Attendance", logic: "The typical, average daily headcount you can expect." },
                { field: "Max. Attendance", logic: "The highest headcount on any single open day. (e.g., The busiest day)." },
                { field: "Attendance (0%)", logic: "Children who are officially registered but missed every single day." },
                { field: "Attendance (> 0% to < 25%)", logic: "Children who rarely visit (attended less than a quarter of the time)." },
                { field: "Attendance (25% to < 50%)", logic: "Occasional drop-ins (absent more often than they are present)." },
                { field: "Attendance (50% to < 75%)", logic: "Regular attendees who show up more than half the time." },
                { field: "Attendance (75% to < 100%)", logic: "Highly committed children who are there almost every day." },
                { field: "Attendance (100%)", logic: "Children with perfect attendance who did not miss a single open day." }
            ];

            let tableRows = logicData.map((item, idx) =>
                `<tr style="background:${idx % 2 === 0 ? '#f4f6fb' : '#ffffff'};">
                    <td style="padding:9px 12px; border:1px solid #dce3f0; font-weight:600; vertical-align:top; word-break:break-word;">${item.field}</td>
                    <td style="padding:9px 12px; border:1px solid #dce3f0; vertical-align:top; word-break:break-word;">${item.logic}</td>
                </tr>`
            ).join("");

            let tableHtml = `
                <style>
                    .logic-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
                    .logic-table { width: 100%; border-collapse: collapse; font-size: 13px; font-family: sans-serif; table-layout: fixed; }
                    .logic-table th, .logic-table td { word-break: break-word; overflow-wrap: break-word; }
                    .logic-table th:first-child, .logic-table td:first-child { width: 30%; }
                    .logic-table th:last-child,  .logic-table td:last-child  { width: 70%; }
                    @media (max-width: 600px) {
                        .logic-table { table-layout: auto; font-size: 12px; }
                        .logic-table th:first-child, .logic-table td:first-child { width: auto; }
                        .logic-table th:last-child,  .logic-table td:last-child  { width: auto; }
                    }
                </style>
                <div class="logic-wrap">
                    <table class="logic-table">
                        <thead>
                            <tr style="background:#273e9d; color:#fff;">
                                <th style="padding:10px 12px; border:1px solid #1e3080; text-align:left;">Field Name</th>
                                <th style="padding:10px 12px; border:1px solid #1e3080; text-align:left;">Simple Business Logic</th>
                            </tr>
                        </thead>
                        <tbody>${tableRows}</tbody>
                    </table>
                </div>`;

            let d = new frappe.ui.Dialog({
                title: __("Field Logic Details"),
                size: "extra-large",
                fields: [
                    {
                        fieldtype: "HTML",
                        fieldname: "logic_table",
                        options: tableHtml
                    }
                ],
                primary_action_label: __("Download PDF"),
                primary_action: function () {
                    const { jsPDF } = window.jspdf;
                    const doc = new jsPDF({ orientation: "landscape", unit: "pt", format: "a4" });

                    const pageWidth = doc.internal.pageSize.getWidth();
                    const margin = 30;
                    const colWidths = [180, pageWidth - margin * 2 - 180];
                    const rowHeight = 14;
                    const headerHeight = 20;
                    const cellPadding = 6;
                    const fontSize = 9;
                    const lineHeight = fontSize * 1.4;

                    doc.setFontSize(13);
                    doc.setFont("helvetica", "bold");
                    doc.setTextColor(40, 40, 40);
                    doc.text("Average Attendance Summary – Field Logic Details", margin, margin);

                    let y = margin + 20;

                    // Header row
                    doc.setFillColor(39, 62, 157);
                    doc.setTextColor(255, 255, 255);
                    doc.setFontSize(fontSize);
                    doc.setFont("helvetica", "bold");
                    doc.rect(margin, y, colWidths[0], headerHeight, "F");
                    doc.rect(margin + colWidths[0], y, colWidths[1], headerHeight, "F");
                    doc.text("Field Name", margin + cellPadding, y + headerHeight - cellPadding);
                    doc.text("Simple Business Logic", margin + colWidths[0] + cellPadding, y + headerHeight - cellPadding);
                    y += headerHeight;

                    doc.setFont("helvetica", "normal");
                    doc.setTextColor(40, 40, 40);

                    logicData.forEach(function (item, idx) {
                        const isEven = idx % 2 === 0;
                        doc.setFillColor(isEven ? 249 : 255, isEven ? 249 : 255, isEven ? 249 : 255);

                        // Wrap logic text
                        const wrappedLogic = doc.splitTextToSize(item.logic, colWidths[1] - cellPadding * 2);
                        const wrappedField = doc.splitTextToSize(item.field, colWidths[0] - cellPadding * 2);
                        const cellHeight = Math.max(wrappedLogic.length, wrappedField.length) * lineHeight + cellPadding * 2;

                        // Page break check
                        if (y + cellHeight > doc.internal.pageSize.getHeight() - margin) {
                            doc.addPage();
                            y = margin;
                        }

                        doc.rect(margin, y, colWidths[0], cellHeight, "F");
                        doc.rect(margin + colWidths[0], y, colWidths[1], cellHeight, "F");

                        // Borders
                        doc.setDrawColor(200, 200, 200);
                        doc.rect(margin, y, colWidths[0], cellHeight);
                        doc.rect(margin + colWidths[0], y, colWidths[1], cellHeight);

                        doc.setFont("helvetica", "bold");
                        doc.text(wrappedField, margin + cellPadding, y + cellPadding + lineHeight - 2);
                        doc.setFont("helvetica", "normal");
                        doc.text(wrappedLogic, margin + colWidths[0] + cellPadding, y + cellPadding + lineHeight - 2);

                        y += cellHeight;
                    });

                    doc.save("Field_Logic_Details.pdf");
                }
            });

            // Load jsPDF if not already loaded, then show dialog
            if (typeof window.jspdf === "undefined") {
                let script = document.createElement("script");
                script.src = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
                script.onload = function () { d.show(); };
                document.head.appendChild(script);
            } else {
                d.show();
            }
        });
    },

    formatter: function (value, row, column, data, default_formatter) {
        if (value === undefined || value === null) {
            return "";
        }

        // 2️⃣ Attendance percentage ke liye color-coded background
        if (column.fieldname === "attendance_percentage" && data) {
            let percentage = parseFloat(value);
            let bgColor = "white"; // Default
            if (percentage >= 0 && percentage <= 25) {
                bgColor = "#FFADB0"; // Red
            } else if (percentage > 25 && percentage <= 50) {
                bgColor = "#FDC483"; // Orange
            } else if (percentage > 50 && percentage <= 75) {
                bgColor = "#f6fc82"; // Yellow
            } else if (percentage > 75 && percentage <= 100) {
                bgColor = "#D7FD9A"; // Green
            }
            return `<div style="background-color: ${bgColor}; color: black; width: 100%; height: 100%; padding: 5px; display: flex; align-items: center; justify-content: center; font-weight: bold;">${value}</div>`;
        }

        if (data && data.state && data.state.includes("Total")) {
            return `<b style="color: black;">${value}</b>`;
        }

        return default_formatter(value, row, column, data);
    }
};

