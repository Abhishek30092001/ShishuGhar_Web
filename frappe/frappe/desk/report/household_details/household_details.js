frappe.query_reports["Household Details"] = {
    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        // Force default behaviour on load
        report.set_filter_value("date_input_type", "month_year");

        // Hide date range
        report.get_filter("time_range").toggle(false);

        // Show year & month
        report.get_filter("year").toggle(true);
        report.get_filter("month").toggle(true);

        // Set current year & month
        const today = frappe.datetime.get_today().split("-");
        report.set_filter_value("year", today[0]);
        report.set_filter_value("month", today[1]);

        report.refresh();
    },

    filters: [
    {
        fieldname: "date_input_type",
        label: __("Date Input Type"),
        fieldtype: "Select",
        options: [
            { value: "month_year", label: __("Month/Year") },
            { value: "date_range", label: __("Date Range") }
        ],
        default: "month_year",
        on_change: function () {
            const type = frappe.query_report.get_filter_value("date_input_type");

            if (type === "date_range") {
                frappe.query_report.set_filter_value(
                    "time_range",
                    [frappe.datetime.month_start(), frappe.datetime.month_end()]
                );

                frappe.query_report.get_filter("year").toggle(false);
                frappe.query_report.get_filter("month").toggle(false);
                frappe.query_report.get_filter("time_range").toggle(true);
            } 
            else {
                frappe.query_report.set_filter_value("time_range", "");

                const today = frappe.datetime.get_today().split("-");
                frappe.query_report.set_filter_value("year", today[0]);
                frappe.query_report.set_filter_value("month", today[1]);

                frappe.query_report.get_filter("time_range").toggle(false);
                frappe.query_report.get_filter("year").toggle(true);
                frappe.query_report.get_filter("month").toggle(true);
            }

            frappe.query_report.refresh();
        }
    },
    {
        fieldname: "time_range",
        label: __("Date Range"),
        fieldtype: "DateRange",
        hidden: 1
    },
    {
        fieldname: "year",
        label: __("Year"),
        fieldtype: "Select",
        options: ["2024", "2025", "2026"],
        hidden: 0
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
        hidden: 0
    },

    {
        "fieldname": "partner",
        "label": __("Partner"),
        "fieldtype": "Link",
        "options": "Partner",
        "reqd": 0
    },
    {
        "fieldname": "state",
        "label": __("State"),
        "fieldtype": "Link",
        "options": "State",
        "reqd": 0
    },
    {
        "fieldname": "district",
        "label": __("District"),
        "fieldtype": "Link",
        "options": "District",
        "reqd": 0
    },
    {
        "fieldname": "block",
        "label": __("Block"),
        "fieldtype": "Link",
        "options": "Block",
        "reqd": 0
    },
    {
        "fieldname": "gp",
        "label": __("Gram Panchayat"),
        "fieldtype": "Link",
        "options": "Gram Panchayat",
        "reqd": 0
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
    ]
};
