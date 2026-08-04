// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Cashbook Report"] = {
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
        // {
        //     fieldname: "creche_age",
        //     label: __("Age of Creche"),
        //     fieldtype: "Select",
        //     options: [
        //         { value: "", label: __("") },
        //         { value: "0-6 Month", label: __("0-6 Month") },
        //         { value: "7-12 Month", label: __("7-12 Month") },
        //         { value: "13-18 Month", label: __("13-18 Month") },
        //         { value: "19-24 Month", label: __("19-24 Month") },
        //         { value: "24+ Month", label: __("24+ Month") }
        //     ],
        //     default: "",
        //     on_change: function () {
        //         frappe.query_report.refresh();
        //     }
        // },
        {
            fieldname: "cr_opening_range_type",
            label: __("Creche Opening Date"),
            fieldtype: "Select",
            options: [
                { value: "",      label: __("") },
                { value: "between", label: __("Between") },
                { value: "before",  label: __("Before") },
                { value: "after",   label: __("After") },
                { value: "equal",   label: __("Equal") }
            ],
            default: "",
            on_change: function () {
                const val = frappe.query_report.get_filter_value("cr_opening_range_type");
                toggleDateFields(val);
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "c_opening_range",
            label: __("Creche Opening Range"),
            fieldtype: "DateRange",
            hidden: 1,
            default: []
        },
        {
            fieldname: "single_date",
            label: __("Creche Opening Date"),
            fieldtype: "Date",
            hidden: 1,
            default: ""
        }
    ]
};

function syncCrecheAgeToDateFilter() {
    const ageRange = frappe.query_report.get_filter_value("creche_age");
    if (!ageRange) {
        // cleared → reset date filters
        frappe.query_report.set_filter_value("cr_opening_range_type", "");
        frappe.query_report.set_filter_value("c_opening_range", []);
        frappe.query_report.set_filter_value("single_date", "");
        toggleDateFields("");
        return;
    }

    const endDate = getEndOfReportMonth();   // last day of selected year + month

    // These match your SQL TIMESTAMPDIFF(MONTH, ...) BETWEEN logic
    const rangeMap = {
        "0-6 Month":   { min: 0,  max: 6  },
        "7-12 Month":  { min: 7,  max: 12 },
        "13-18 Month": { min: 13, max: 18 },
        "19-24 Month": { min: 19, max: 24 },
        "24+ Month":   { min: 25, max: null }   // 25 months and more
    };

    const range = rangeMap[ageRange];
    if (!range) return;

    let fromDate, toDate;

    if (range.max === null) {
        // 24+ months → opened on or before (end - 24 months)
        fromDate = null;
        toDate   = subtractMonths(endDate, 24);
        frappe.query_report.set_filter_value("cr_opening_range_type", "before");
        frappe.query_report.set_filter_value("single_date", toDate);
        frappe.query_report.set_filter_value("c_opening_range", []);
    } else {
        // Normal bucket: opened between (end - max) and (end - min)
        fromDate = subtractMonths(endDate, range.max);
        toDate   = subtractMonths(endDate, range.min);
        frappe.query_report.set_filter_value("cr_opening_range_type", "between");
        frappe.query_report.set_filter_value("c_opening_range", [fromDate, toDate]);
        frappe.query_report.set_filter_value("single_date", "");
    }

    toggleDateFields(frappe.query_report.get_filter_value("cr_opening_range_type"));
}

function getEndOfReportMonth() {
    let year  = parseInt(frappe.query_report.get_filter_value("year"))  || new Date().getFullYear();
    let month = parseInt(frappe.query_report.get_filter_value("month")) || (new Date().getMonth() + 1);
    // Last day of month
    return new Date(year, month, 0);
}

function subtractMonths(baseDate, months) {
    let d = new Date(baseDate);
    d.setMonth(d.getMonth() - months);
    return d.toISOString().split("T")[0];   // YYYY-MM-DD
}

function toggleDateFields(type) {
    const showRange  = type === "between";
    const showSingle = ["before", "after", "equal"].includes(type);

    frappe.query_report.get_filter("c_opening_range").toggle(showRange);
    frappe.query_report.get_filter("single_date").toggle(showSingle);

    if (showRange)  frappe.query_report.set_filter_value("single_date", "");
    if (showSingle) frappe.query_report.set_filter_value("c_opening_range", []);
}