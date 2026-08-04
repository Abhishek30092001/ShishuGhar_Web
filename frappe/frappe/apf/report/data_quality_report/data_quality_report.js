// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

// WHO plausible weight/height ranges by age in completed months (6-36 months).
// Used to show the per-month "Data Range Value" (Age / Plausible Range) in the
// reduction-cell popup, independent of gender lookups done server-side.
const WHO_WEIGHT_RANGE_JS = {
    M: {
        6: [5.1, 11.0], 7: [5.4, 11.4], 8: [5.6, 11.9], 9: [5.8, 12.3],
        10: [5.9, 12.7], 11: [6.1, 13.0], 12: [6.2, 13.3], 13: [6.3, 13.7],
        14: [6.5, 14.0], 15: [6.6, 14.3], 16: [6.7, 14.6], 17: [6.8, 14.9],
        18: [6.9, 15.1], 19: [7.1, 15.4], 20: [7.2, 15.7], 21: [7.3, 16.0],
        22: [7.4, 16.2], 23: [7.6, 16.5], 24: [7.7, 16.8], 25: [7.8, 17.1],
        26: [7.9, 17.3], 27: [8.0, 17.6], 28: [8.1, 17.9], 29: [8.2, 18.2],
        30: [8.3, 18.4], 31: [8.4, 18.7], 32: [8.5, 19.0], 33: [8.6, 19.3],
        34: [8.7, 19.6], 35: [8.8, 19.8], 36: [8.9, 20.1],
    },
    F: {
        6: [4.5, 10.2], 7: [4.7, 10.6], 8: [4.9, 11.1], 9: [5.0, 11.4],
        10: [5.2, 11.8], 11: [5.3, 12.2], 12: [5.4, 12.5], 13: [5.6, 12.8],
        14: [5.7, 13.1], 15: [5.8, 13.4], 16: [5.9, 13.7], 17: [6.0, 14.0],
        18: [6.1, 14.3], 19: [6.2, 14.6], 20: [6.3, 14.9], 21: [6.5, 15.2],
        22: [6.6, 15.5], 23: [6.7, 15.8], 24: [6.8, 16.1], 25: [6.9, 16.4],
        26: [7.0, 16.7], 27: [7.1, 17.0], 28: [7.2, 17.3], 29: [7.3, 17.6],
        30: [7.4, 17.9], 31: [7.5, 18.2], 32: [7.6, 18.5], 33: [7.7, 18.8],
        34: [7.8, 19.1], 35: [7.9, 19.4], 36: [8.0, 19.7],
    },
};

const WHO_HEIGHT_RANGE_JS = {
    M: {
        6: [60.4, 75.4], 7: [61.7, 77.1], 8: [63.0, 78.7], 9: [64.3, 80.3],
        10: [65.4, 81.7], 11: [66.5, 83.2], 12: [67.6, 84.5], 13: [68.6, 85.9],
        14: [69.6, 87.1], 15: [70.6, 88.4], 16: [71.6, 89.6], 17: [72.5, 90.8],
        18: [73.4, 92.0], 19: [74.3, 93.1], 20: [75.2, 94.2], 21: [76.0, 95.3],
        22: [76.8, 96.4], 23: [77.7, 97.4], 24: [78.0, 97.7], 25: [78.6, 98.7],
        26: [79.3, 99.6], 27: [79.9, 100.5], 28: [80.5, 101.4], 29: [81.1, 102.3],
        30: [81.7, 103.1], 31: [82.3, 104.0], 32: [82.8, 104.8], 33: [83.4, 105.6],
        34: [83.9, 106.4], 35: [84.4, 107.2], 36: [85.0, 108.0],
    },
    F: {
        6: [58.6, 73.5], 7: [59.9, 75.3], 8: [61.2, 76.9], 9: [62.5, 78.5],
        10: [63.7, 80.0], 11: [64.9, 81.5], 12: [66.0, 82.9], 13: [67.0, 84.3],
        14: [68.0, 85.7], 15: [69.0, 87.0], 16: [70.0, 88.2], 17: [70.9, 89.4],
        18: [71.8, 90.7], 19: [72.8, 91.9], 20: [73.7, 93.1], 21: [74.5, 94.2],
        22: [75.2, 95.4], 23: [76.0, 96.5], 24: [76.0, 96.9], 25: [76.8, 98.0],
        26: [77.5, 99.0], 27: [78.1, 100.1], 28: [78.8, 101.1], 29: [79.5, 102.0],
        30: [80.1, 103.0], 31: [80.7, 103.9], 32: [81.3, 104.9], 33: [81.9, 105.8],
        34: [82.5, 106.7], 35: [83.1, 107.5], 36: [83.6, 108.4],
    },
};

function get_who_range(kind, gender, age) {
    if (age === null || age === undefined) return null;
    const table = kind === "height" ? WHO_HEIGHT_RANGE_JS : WHO_WEIGHT_RANGE_JS;
    const gender_key = gender === "Male" ? "M" : "F";
    return table[gender_key][age] || null;
}

frappe.query_reports["Data Quality Report"] = {
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
            onchange: function () {
                frappe.query_report.refresh();
            }
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
                    filters: { "is_active": 1 }
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
        // {
        //     fieldname: "level",
        //     label: __("Level"),
        //     fieldtype: "Select",
        //     options: [
        //         { "value": "", "label": __("Level") },
        //         { "value": "1", "label": __("Partner") },
        //         { "value": "2", "label": __("State") },
        //         { "value": "3", "label": __("District") },
        //         { "value": "4", "label": __("Block") },
        //         { "value": "5", "label": __("Supervisor") },
        //         { "value": "6", "label": __("GP") },
        //         { "value": "7", "label": __("Creche") },
        //     ],
        //     default: "",
        //     on_change: function () {
        //         frappe.query_report.refresh();
        //     }
        // },
        {
            fieldname: "phases",
            label: __("Phase"),
            fieldtype: "MultiSelect",
            options: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            reqd: 0,
            default: ""
        },
        {
            fieldname: "creche_status_id",
            label: __("Creche Status"),
            fieldtype: "Select",
            options: [
                { "value": "", "label": __("") },
                { "value": "1", "label": __("Planned") },
                { "value": "2", "label": __("Plan dropped") },
                { "value": "3", "label": __("Active/Operational") },
                { "value": "4", "label": __("Closed") },
            ],
            default: "3",
            on_change: function () {
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
                syncCrecheAgeWithOpeningDate();
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "duration",
            label: __("Child Age (Months)"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("") },
                { value: "3", label: __("3 Month") },
                { value: "6", label: __("6 Month") },
                { value: "9", label: __("9 Month") },
                { value: "12", label: __("12 Month") }
            ],
            default: "",
            on_change: function () {
                frappe.query_report.refresh();
            }
        },

        {
            fieldname: "weight_height",
            label: __("Weight/Height"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("All") },
                { value: "1", label: __("Height") },
                { value: "2", label: __("Weight") }
            ],
            default: "",
            on_change: function () {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "data_availability",
            label: __("Data Availability"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("") },
                { value: "1", label: __("All") },
                { value: "2", label: __("Available Data") },
                { value: "3", label: __("No Data") }
            ],
            default: "1",
            on_change: function () {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "duration_h_w",
            label: __("Duration for Height/Weight Data"),
            fieldtype: "Select",
            options: [
                { value: "3", label: __("3 Month") },
                { value: "6", label: __("6 Month") },
                { value: "9", label: __("9 Month") },
                { value: "12", label: __("12 Month") }
            ],
            default: "3",
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
        }
    ],
    formatter: function (value, row, column, data, default_formatter) {
        const fieldname = column.fieldname || "";

        // Match measurement value columns (height_mN / weight_mN).
        const slot_match = fieldname.match(/^(?:height|weight)_(m\d+)$/);
        const slot = slot_match ? slot_match[1] : null;

        if (slot && data) {
            const is_missing = (value === null || value === undefined || value === "");
            if (is_missing) {
                // Only the hyphen is clickable.
                const details = {
                    child_name: data.child_name || "-",
                    reason: data[`measurement_reason_${slot}`] || "No reason recorded"
                };
                const encoded_details = encodeURIComponent(JSON.stringify(details));
                return `<a href="#" class="measurement-cell-link" data-details="${encoded_details}">-</a>`;
            }
            // Data value is present — render as plain text (not clickable).
            return default_formatter(value, row, column, data);
        }

        // Match reduction columns (height_redN / weight_redN).
        const red_match = fieldname.match(/^(height|weight)_red(\d+)$/);
        if (red_match && data) {
            const kind = red_match[1]; // "height" or "weight"

            // Collect all slots present in this row for this metric (m1, m2, ...).
            const all_slots = [];
            let i = 1;
            while (data.hasOwnProperty(`${kind}_m${i}`) || data.hasOwnProperty(`measurement_date_m${i}`)) {
                all_slots.push(`m${i}`);
                i++;
            }

            // Age at m1 (the selected/newest month). Each older slot is one month less.
            const base_age = (data.age !== null && data.age !== undefined) ? Number(data.age) : null;
            const unit = kind === "height" ? "cm" : "kg";

            const months = all_slots.map((slot, idx) => {
                const date = data[`measurement_date_${slot}`] || "-";
                const slot_age = base_age !== null ? base_age - idx : null;
                const range = get_who_range(kind, data.gender, slot_age);
                return {
                    slot: slot,
                    value: data[`${kind}_${slot}`],
                    date: date,
                    child_age: slot_age,
                    age: slot_age,
                    range: range,
                    unit: unit
                };
            });

            const details = {
                child_name: data.child_name || "-",
                kind: kind,
                months: months
            };
            const encoded_details = encodeURIComponent(JSON.stringify(details));
            // Wrap the already-formatted arrow HTML in a clickable anchor.
            const display_value = (value === null || value === undefined || value === "") ? "-" : value;
            return `<a href="#" class="reduction-cell-link" data-details="${encoded_details}">${display_value}</a>`;
        }

        return default_formatter(value, row, column, data);
    },
    onload: function (report) {
        // Hide the default Frappe Export menu to prevent JSON downloads
        const style = document.createElement("style");
        style.innerHTML = `
            [data-label="Export"],
            [data-original-title="Export"] {
                display: none !important;
            }
        `;
        document.head.appendChild(style);

        // Add your custom direct-to-Excel button
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        // ── Data Range button: shows WHO plausible range tables ──────────────
        report.page.add_inner_button(__("Data Range"), function () {
            var WHO_WEIGHT_BOYS = {
                6:  [5.1, 11.0],  7:  [5.4, 11.4],  8:  [5.6, 11.9],  9:  [5.8, 12.3],
                10: [5.9, 12.7],  11: [6.1, 13.0],  12: [6.2, 13.3],  13: [6.3, 13.7],
                14: [6.5, 14.0],  15: [6.6, 14.3],  16: [6.7, 14.6],  17: [6.8, 14.9],
                18: [6.9, 15.1],  19: [7.1, 15.4],  20: [7.2, 15.7],  21: [7.3, 16.0],
                22: [7.4, 16.2],  23: [7.6, 16.5],  24: [7.7, 16.8],  25: [7.8, 17.1],
                26: [7.9, 17.3],  27: [8.0, 17.6],  28: [8.1, 17.9],  29: [8.2, 18.2],
                30: [8.3, 18.4],  31: [8.4, 18.7],  32: [8.5, 19.0],  33: [8.6, 19.3],
                34: [8.7, 19.6],  35: [8.8, 19.8],  36: [8.9, 20.1]
            };
            var WHO_WEIGHT_GIRLS = {
                6:  [4.5, 10.2],  7:  [4.7, 10.6],  8:  [4.9, 11.1],  9:  [5.0, 11.4],
                10: [5.2, 11.8],  11: [5.3, 12.2],  12: [5.4, 12.5],  13: [5.6, 12.8],
                14: [5.7, 13.1],  15: [5.8, 13.4],  16: [5.9, 13.7],  17: [6.0, 14.0],
                18: [6.1, 14.3],  19: [6.2, 14.6],  20: [6.3, 14.9],  21: [6.5, 15.2],
                22: [6.6, 15.5],  23: [6.7, 15.8],  24: [6.8, 16.1],  25: [6.9, 16.4],
                26: [7.0, 16.7],  27: [7.1, 17.0],  28: [7.2, 17.3],  29: [7.3, 17.6],
                30: [7.4, 17.9],  31: [7.5, 18.2],  32: [7.6, 18.5],  33: [7.7, 18.8],
                34: [7.8, 19.1],  35: [7.9, 19.4],  36: [8.0, 19.7]
            };
            var WHO_HEIGHT_BOYS = {
                6:  [60.4, 75.4],  7:  [61.7, 77.1],  8:  [63.0, 78.7],  9:  [64.3, 80.3],
                10: [65.4, 81.7],  11: [66.5, 83.2],  12: [67.6, 84.5],  13: [68.6, 85.9],
                14: [69.6, 87.1],  15: [70.6, 88.4],  16: [71.6, 89.6],  17: [72.5, 90.8],
                18: [73.4, 92.0],  19: [74.3, 93.1],  20: [75.2, 94.2],  21: [76.0, 95.3],
                22: [76.8, 96.4],  23: [77.7, 97.4],  24: [78.0, 97.7],  25: [78.6, 98.7],
                26: [79.3, 99.6],  27: [79.9, 100.5], 28: [80.5, 101.4], 29: [81.1, 102.3],
                30: [81.7, 103.1], 31: [82.3, 104.0], 32: [82.8, 104.8], 33: [83.4, 105.6],
                34: [83.9, 106.4], 35: [84.4, 107.2], 36: [85.0, 108.0]
            };
            var WHO_HEIGHT_GIRLS = {
                6:  [58.6, 73.5],  7:  [59.9, 75.3],  8:  [61.2, 76.9],  9:  [62.5, 78.5],
                10: [63.7, 80.0],  11: [64.9, 81.5],  12: [66.0, 82.9],  13: [67.0, 84.3],
                14: [68.0, 85.7],  15: [69.0, 87.0],  16: [70.0, 88.2],  17: [70.9, 89.4],
                18: [71.8, 90.7],  19: [72.8, 91.9],  20: [73.7, 93.1],  21: [74.5, 94.2],
                22: [75.2, 95.4],  23: [76.0, 96.5],  24: [76.0, 96.9],  25: [76.8, 98.0],
                26: [77.5, 99.0],  27: [78.1, 100.1], 28: [78.8, 101.1], 29: [79.5, 102.0],
                30: [80.1, 103.0], 31: [80.7, 103.9], 32: [81.3, 104.9], 33: [81.9, 105.8],
                34: [82.5, 106.7], 35: [83.1, 107.5], 36: [83.6, 108.4]
            };

            var WHO_WEIGHT_MEDIAN_BOYS   = { 6:7.9,  7:8.3,  8:8.6,  9:9.0,  10:9.2, 11:9.4, 12:9.6, 13:9.9, 14:10.1,15:10.3,16:10.5,17:10.7,18:10.9,19:11.1,20:11.3,21:11.5,22:11.8,23:12.0,24:12.2,25:12.4,26:12.5,27:12.7,28:12.9,29:13.1,30:13.3,31:13.5,32:13.7,33:13.8,34:14.0,35:14.2,36:14.3 };
            var WHO_WEIGHT_MEDIAN_GIRLS  = { 6:7.3,  7:7.6,  8:7.9,  9:8.2,  10:8.5, 11:8.7, 12:8.9, 13:9.2, 14:9.4, 15:9.6, 16:9.8, 17:10.0,18:10.2,19:10.4,20:10.6,21:10.9,22:11.1,23:11.3,24:11.5,25:11.7,26:11.9,27:12.1,28:12.3,29:12.5,30:12.7,31:12.9,32:13.1,33:13.3,34:13.5,35:13.7,36:13.9 };
            var WHO_HEIGHT_MEDIAN_BOYS   = { 6:67.6, 7:69.2, 8:70.6, 9:72.0, 10:73.3,11:74.5,12:75.7,13:76.9,14:78.0,15:79.1,16:80.2,17:81.2,18:82.3,19:83.2,20:84.2,21:85.1,22:86.0,23:86.9,24:87.8,25:88.0,26:88.8,27:89.6,28:90.4,29:91.2,30:92.0,31:92.7,32:93.4,33:94.1,34:94.8,35:95.4,36:96.1 };
            var WHO_HEIGHT_MEDIAN_GIRLS  = { 6:65.7, 7:67.3, 8:68.7, 9:70.1, 10:71.5,11:72.8,12:74.0,13:75.2,14:76.4,15:77.5,16:78.6,17:79.7,18:80.7,19:81.7,20:82.7,21:83.7,22:84.6,23:85.5,24:86.4,25:86.6,26:87.4,27:88.3,28:89.1,29:89.9,30:90.7,31:91.4,32:92.2,33:92.9,34:93.6,35:94.4,36:95.1 };

            var WHO_WEIGHT_NORMAL_BOYS   = { 6:[6.0,9.8],   7:[6.3,10.3],  8:[6.6,10.7],  9:[6.9,11.1],  10:[7.1,11.5], 11:[7.3,11.8], 12:[7.5,12.1], 13:[7.7,12.5], 14:[7.9,12.8], 15:[8.0,13.1], 16:[8.2,13.4], 17:[8.3,13.7], 18:[8.4,14.0], 19:[8.6,14.3], 20:[8.7,14.6], 21:[8.9,14.9], 22:[9.0,15.2], 23:[9.2,15.5], 24:[9.3,15.8], 25:[9.5,16.0], 26:[9.6,16.3], 27:[9.8,16.6], 28:[9.9,16.9], 29:[10.1,17.2],30:[10.2,17.5],31:[10.3,17.7],32:[10.5,18.0],33:[10.6,18.3],34:[10.7,18.6],35:[10.9,18.9],36:[11.0,19.1] };
            var WHO_WEIGHT_NORMAL_GIRLS  = { 6:[5.4,9.1],   7:[5.7,9.5],   8:[5.9,9.9],   9:[6.1,10.3],  10:[6.3,10.6], 11:[6.5,11.0], 12:[6.6,11.3], 13:[6.8,11.6], 14:[6.9,11.9], 15:[7.1,12.2], 16:[7.2,12.5], 17:[7.4,12.8], 18:[7.5,13.1], 19:[7.7,13.4], 20:[7.8,13.7], 21:[8.0,14.0], 22:[8.2,14.3], 23:[8.3,14.6], 24:[8.5,14.9], 25:[8.6,15.2], 26:[8.8,15.5], 27:[8.9,15.8], 28:[9.1,16.1], 29:[9.2,16.4], 30:[9.4,16.7], 31:[9.5,17.1], 32:[9.7,17.4], 33:[9.8,17.7], 34:[10.0,18.0],35:[10.1,18.3],36:[10.3,18.6] };
            var WHO_HEIGHT_NORMAL_BOYS   = { 6:[63.6,71.6], 7:[65.1,73.2], 8:[66.5,74.8], 9:[67.7,76.2], 10:[69.0,77.6],11:[70.2,78.9],12:[71.3,80.2],13:[72.4,81.4],14:[73.5,82.7],15:[74.5,83.9],16:[75.5,84.9],17:[76.5,85.9],18:[77.4,87.0],19:[78.4,88.0],20:[79.3,88.9],21:[80.2,89.8],22:[81.0,90.7],23:[81.9,91.6],24:[82.5,92.3],25:[82.8,93.0],26:[83.5,93.8],27:[84.2,94.5],28:[84.9,95.2],29:[85.5,96.0],30:[86.1,96.7],31:[86.7,97.4],32:[87.3,98.0],33:[87.9,98.7],34:[88.4,99.4],35:[89.0,100.0],36:[89.5,100.6] };
            var WHO_HEIGHT_NORMAL_GIRLS  = { 6:[61.8,69.8], 7:[63.3,71.3], 8:[64.7,72.8], 9:[66.0,74.2], 10:[67.2,75.6],11:[68.4,76.9],12:[69.6,78.2],13:[70.6,79.5],14:[71.7,80.7],15:[72.8,81.9],16:[73.8,83.0],17:[74.9,84.1],18:[75.9,85.2],19:[76.9,86.2],20:[77.9,87.2],21:[78.8,88.2],22:[79.7,89.2],23:[80.6,90.1],24:[81.5,91.0],25:[81.7,91.8],26:[82.5,92.6],27:[83.3,93.4],28:[84.1,94.2],29:[84.9,95.0],30:[85.6,95.8],31:[86.3,96.5],32:[87.0,97.3],33:[87.7,98.0],34:[88.4,98.7],35:[89.1,99.4],36:[89.8,100.2] };

            // Structured datasets for XLSX export
            var datasets = [
                { label: "Weight for Age - Boys (kg)",  unit: "kg", data: WHO_WEIGHT_BOYS,  medians: WHO_WEIGHT_MEDIAN_BOYS,  normals: WHO_WEIGHT_NORMAL_BOYS  },
                { label: "Weight for Age - Girls (kg)", unit: "kg", data: WHO_WEIGHT_GIRLS, medians: WHO_WEIGHT_MEDIAN_GIRLS, normals: WHO_WEIGHT_NORMAL_GIRLS },
                { label: "Height for Age - Boys (cm)",  unit: "cm", data: WHO_HEIGHT_BOYS,  medians: WHO_HEIGHT_MEDIAN_BOYS,  normals: WHO_HEIGHT_NORMAL_BOYS  },
                { label: "Height for Age - Girls (cm)", unit: "cm", data: WHO_HEIGHT_GIRLS, medians: WHO_HEIGHT_MEDIAN_GIRLS, normals: WHO_HEIGHT_NORMAL_GIRLS },
            ];

            function buildWHOTable(label, unit, data, medians, normals) {
                var ages = Object.keys(data).map(Number).sort(function(a,b){return a-b;});
                var rows = ages.map(function(age) {
                    var range    = data[age];
                    var median   = medians[age] != null ? medians[age].toFixed(1) : "-";
                    var normal   = normals[age] ? normals[age][0].toFixed(1) + " – " + normals[age][1].toFixed(1) : "-";
                    var flagLow  = range ? "< " + range[0].toFixed(1) : "-";
                    var flagHigh = range ? "> " + range[1].toFixed(1) : "-";
                    var plausible = range ? range[0].toFixed(1) + " – " + range[1].toFixed(1) : "-";
                    return '<tr>'
                        + '<td style="padding:5px 10px;border:1px solid #ddd;text-align:center;font-weight:600;">' + age + '</td>'
                        + '<td style="padding:5px 10px;border:1px solid #ddd;text-align:center;">' + median + ' ' + unit + '</td>'
                        + '<td style="padding:5px 10px;border:1px solid #ddd;text-align:center;">' + plausible + ' ' + unit + '</td>'
                        + '<td style="padding:5px 10px;border:1px solid #ddd;text-align:center;background:#fff3f3;color:#cc0000;">' + flagLow + ' ' + unit + '</td>'
                        + '<td style="padding:5px 10px;border:1px solid #ddd;text-align:center;background:#f0fff4;color:#006600;">' + normal + ' ' + unit + '</td>'
                        + '<td style="padding:5px 10px;border:1px solid #ddd;text-align:center;background:#fff3f3;color:#cc0000;">' + flagHigh + ' ' + unit + '</td>'
                        + '</tr>';
                }).join('');

                var hs = 'padding:6px 10px;border:1px solid #ccc;background:#f0f0f0;text-align:center;font-weight:700;font-size:12px;position:sticky;top:0;z-index:1;';
                return '<div style="margin-bottom:28px;">'
                    + '<div style="font-size:14px;font-weight:700;color:#333;margin-bottom:6px;padding:6px 10px;background:#e8f4fd;border-left:4px solid #2196F3;border-radius:2px;">' + label + '</div>'
                    + '<div style="overflow-x:auto;">'
                    + '<table style="width:100%;border-collapse:collapse;font-size:12px;">'
                    + '<thead><tr>'
                    + '<th style="' + hs + '">Age<br>(Months)</th>'
                    + '<th style="' + hs + '">WHO Median</th>'
                    + '<th style="' + hs + '">Plausible Range<br>(-4 SD to +3 SD)</th>'
                    + '<th style="' + hs + 'background:#ffe0e0;">Flag Below<br>(Likely Error)</th>'
                    + '<th style="' + hs + 'background:#e0f4e8;">Normal Zone<br>(-2 SD to +2 SD)</th>'
                    + '<th style="' + hs + 'background:#ffe0e0;">Flag Above<br>(Likely Error)</th>'
                    + '</tr></thead>'
                    + '<tbody>' + rows + '</tbody>'
                    + '</table></div></div>';
            }

            var html = '<div style="font-family:Arial,sans-serif;">'
                + buildWHOTable("Weight for Age — Boys (kg)",   "kg", WHO_WEIGHT_BOYS,  WHO_WEIGHT_MEDIAN_BOYS,  WHO_WEIGHT_NORMAL_BOYS)
                + buildWHOTable("Weight for Age — Girls (kg)",  "kg", WHO_WEIGHT_GIRLS, WHO_WEIGHT_MEDIAN_GIRLS, WHO_WEIGHT_NORMAL_GIRLS)
                + buildWHOTable("Height for Age — Boys (cm)",   "cm", WHO_HEIGHT_BOYS,  WHO_HEIGHT_MEDIAN_BOYS,  WHO_HEIGHT_NORMAL_BOYS)
                + buildWHOTable("Height for Age — Girls (cm)",  "cm", WHO_HEIGHT_GIRLS, WHO_HEIGHT_MEDIAN_GIRLS, WHO_HEIGHT_NORMAL_GIRLS)
                + '</div>';

            // ── XLSX export: load SheetJS on demand if not already present ───
            function _withXLSX(callback) {
                if (typeof XLSX !== "undefined") {
                    callback(XLSX);
                    return;
                }
                var script = document.createElement("script");
                script.src = "https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js";
                script.onload = function() { callback(window.XLSX); };
                script.onerror = function() {
                    frappe.msgprint(__("Could not load XLSX library. Please check your internet connection."));
                };
                document.head.appendChild(script);
            }

            function downloadXLSX() {
                _withXLSX(function(XLSX) {
                    var wb = XLSX.utils.book_new();
                    var headers = ["Age (Months)", "WHO Median", "Plausible Range (-4 SD to +3 SD)", "Flag Below (Likely Error)", "Normal Zone (-2 SD to +2 SD)", "Flag Above (Likely Error)"];

                    datasets.forEach(function(ds) {
                        var ages = Object.keys(ds.data).map(Number).sort(function(a,b){return a-b;});
                        var sheetData = [headers];
                        ages.forEach(function(age) {
                            var range     = ds.data[age];
                            var median    = ds.medians[age] != null ? ds.medians[age].toFixed(1) + " " + ds.unit : "-";
                            var normal    = ds.normals[age] ? ds.normals[age][0].toFixed(1) + " - " + ds.normals[age][1].toFixed(1) + " " + ds.unit : "-";
                            var flagLow   = range ? "< " + range[0].toFixed(1) + " " + ds.unit : "-";
                            var flagHigh  = range ? "> " + range[1].toFixed(1) + " " + ds.unit : "-";
                            var plausible = range ? range[0].toFixed(1) + " - " + range[1].toFixed(1) + " " + ds.unit : "-";
                            sheetData.push([age, median, plausible, flagLow, normal, flagHigh]);
                        });
                        var ws = XLSX.utils.aoa_to_sheet(sheetData);
                        ws['!cols'] = headers.map(function(h, i) {
                            var max = h.length;
                            sheetData.slice(1).forEach(function(r) {
                                if (r[i] && String(r[i]).length > max) max = String(r[i]).length;
                            });
                            return { wch: max + 4 };
                        });
                        var sheetName = ds.label.replace(/[:\\\/?*\[\]]/g, "").substring(0, 31);
                        XLSX.utils.book_append_sheet(wb, ws, sheetName);
                    });

                    XLSX.writeFile(wb, "WHO_Data_Ranges.xlsx");
                });
            }

            // ── PDF export via print-targeted hidden iframe ───────────────────
            function downloadPDF() {
                var printStyles = [
                    '@page { size: A4 landscape; margin: 15mm; }',
                    'body { font-family: Arial, sans-serif; font-size: 11px; color: #000; }',
                    'h1 { font-size: 14px; margin: 0 0 16px 0; color: #1a1a2e; }',
                    '.section-title { font-size: 12px; font-weight: 700; color: #333;',
                    '  padding: 5px 8px; background: #e8f4fd; border-left: 4px solid #2196F3;',
                    '  margin: 20px 0 6px 0; }',
                    'table { width: 100%; border-collapse: collapse; margin-bottom: 8px; page-break-inside: avoid; }',
                    'th, td { border: 1px solid #bbb; padding: 4px 8px; text-align: center; font-size: 10px; }',
                    'th { background: #f0f0f0; font-weight: 700; }',
                    'th.flag { background: #ffe0e0; }',
                    'th.normal { background: #e0f4e8; }',
                    'td.flag { background: #fff3f3; color: #cc0000; }',
                    'td.normal { background: #f0fff4; color: #006600; }',
                    'td.age { font-weight: 600; }',
                ].join('\n');

                var buildPrintTable = function(ds) {
                    var ages = Object.keys(ds.data).map(Number).sort(function(a,b){return a-b;});
                    var rows = ages.map(function(age) {
                        var range     = ds.data[age];
                        var median    = ds.medians[age] != null ? ds.medians[age].toFixed(1) + " " + ds.unit : "-";
                        var normal    = ds.normals[age] ? ds.normals[age][0].toFixed(1) + " – " + ds.normals[age][1].toFixed(1) + " " + ds.unit : "-";
                        var flagLow   = range ? "< " + range[0].toFixed(1) + " " + ds.unit : "-";
                        var flagHigh  = range ? "> " + range[1].toFixed(1) + " " + ds.unit : "-";
                        var plausible = range ? range[0].toFixed(1) + " – " + range[1].toFixed(1) + " " + ds.unit : "-";
                        return '<tr>'
                            + '<td class="age">' + age + '</td>'
                            + '<td>' + median + '</td>'
                            + '<td>' + plausible + '</td>'
                            + '<td class="flag">' + flagLow + '</td>'
                            + '<td class="normal">' + normal + '</td>'
                            + '<td class="flag">' + flagHigh + '</td>'
                            + '</tr>';
                    }).join('');
                    return '<div class="section-title">' + ds.label + '</div>'
                        + '<table>'
                        + '<thead><tr>'
                        + '<th>Age (Months)</th>'
                        + '<th>WHO Median</th>'
                        + '<th>Plausible Range (-4 SD to +3 SD)</th>'
                        + '<th class="flag">Flag Below (Likely Error)</th>'
                        + '<th class="normal">Normal Zone (-2 SD to +2 SD)</th>'
                        + '<th class="flag">Flag Above (Likely Error)</th>'
                        + '</tr></thead>'
                        + '<tbody>' + rows + '</tbody>'
                        + '</table>';
                };

                var printBody = '<h1>WHO Plausible Data Ranges (6 – 36 Months)</h1>'
                    + datasets.map(buildPrintTable).join('');

                var iframe = document.createElement('iframe');
                iframe.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:0;height:0;border:0;';
                document.body.appendChild(iframe);

                var doc = iframe.contentWindow.document;
                doc.open();
                doc.write('<!DOCTYPE html><html><head><meta charset="UTF-8">'
                    + '<title>WHO Data Ranges</title>'
                    + '<style>' + printStyles + '</style>'
                    + '</head><body>' + printBody + '</body></html>');
                doc.close();

                iframe.contentWindow.focus();
                setTimeout(function() {
                    iframe.contentWindow.print();
                    setTimeout(function() { document.body.removeChild(iframe); }, 1000);
                }, 400);
            }

            var d = new frappe.ui.Dialog({
                title: __("WHO Plausible Data Ranges (6 – 36 Months)"),
                fields: [{ fieldtype: "HTML", fieldname: "range_html" }],
                size: "extra-large",
                primary_action_label: __("Download .xlsx"),
                primary_action: function() { downloadXLSX(); },
                secondary_action_label: __("Download PDF"),
                secondary_action: function() { downloadPDF(); },
            });

            // Make the dialog body scrollable with a fixed max height
            d.$wrapper.find(".modal-body").css({
                "max-height": "65vh",
                "overflow-y": "auto",
                "overflow-x": "hidden",
                "padding-right": "4px",
            });

            d.fields_dict.range_html.$wrapper.html(html);
            d.show();
        });

        $(report.page.main).on("click", "a.measurement-cell-link", function (e) {
            e.preventDefault();

            const encoded_details = $(this).attr("data-details");
            if (!encoded_details) return;

            const details = JSON.parse(decodeURIComponent(encoded_details));
            show_measurement_dialog(details);
        });

        $(report.page.main).on("click", "a.reduction-cell-link", function (e) {
            e.preventDefault();

            const encoded_details = $(this).attr("data-details");
            if (!encoded_details) return;

            const details = JSON.parse(decodeURIComponent(encoded_details));
            show_reduction_dialog(details);
        });
    }
};

function show_measurement_dialog(details) {
    const table_html = `
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>${__("Child Name")}</th>
                    <th>${__("Reason")}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>${details.child_name}</td>
                    <td>${details.reason}</td>
                </tr>
            </tbody>
        </table>
    `;

    const dialog = new frappe.ui.Dialog({
        title: __("Measurement Details"),
        fields: [
            { fieldname: "details_html", fieldtype: "HTML", options: table_html }
        ]
    });
    dialog.show();
}

function show_reduction_dialog(details) {
    const metric = details.kind === "height" ? __("Height") : __("Weight");
    const unit = details.kind === "height" ? "cm" : "kg";

    const rows_html = details.months.map((m, idx) => {
        const metric_val = (m.value !== null && m.value !== undefined && m.value !== "")
            ? `${m.value} ${unit}` : "-";
        const name_cell = idx === 0
            ? `<td rowspan="${details.months.length}" style="padding:8px 14px;border:1px solid #ddd;vertical-align:middle;">${details.child_name}</td>`
            : "";
        const child_age = (m.child_age !== null && m.child_age !== undefined) ? m.child_age : "-";
        const data_range_value = (m.age !== null && m.age !== undefined && m.range)
            ? `${__("Age")} ${m.age}${__("m")}: ${m.range[0]} – ${m.range[1]} ${m.unit}`
            : "-";

        return `<tr>${name_cell}`
            + `<td style="padding:8px 14px;border:1px solid #ddd;text-align:center;">${child_age}</td>`
            + `<td style="padding:8px 14px;border:1px solid #ddd;white-space:nowrap;">${data_range_value}</td>`
            + `<td style="padding:8px 14px;border:1px solid #ddd;text-align:center;">${m.date}</td>`
            + `<td style="padding:8px 14px;border:1px solid #ddd;text-align:center;">${metric_val}</td>`
            + `</tr>`;
    }).join("");

    const table_html = `
        <div style="overflow-x:auto;">
            <table style="width:100%;min-width:640px;border-collapse:collapse;font-size:13px;">
                <thead>
                    <tr style="background:#f5f5f5;">
                        <th style="padding:8px 14px;border:1px solid #ddd;text-align:left;">${__("Child Name")}</th>
                        <th style="padding:8px 14px;border:1px solid #ddd;">${__("Child Age (in Months)")}</th>
                        <th style="padding:8px 14px;border:1px solid #ddd;text-align:left;">${__("Data Range Value")}</th>
                        <th style="padding:8px 14px;border:1px solid #ddd;">${__("Measurement Date")}</th>
                        <th style="padding:8px 14px;border:1px solid #ddd;">${__("{0} Value", [metric])}</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows_html}
                </tbody>
            </table>
        </div>
    `;

    const dialog = new frappe.ui.Dialog({
        title: __("{0} Details", [metric]),
        size: "large",
        fields: [
            { fieldname: "details_html", fieldtype: "HTML", options: table_html }
        ]
    });
    dialog.$wrapper.find(".modal-dialog").css({ "max-width": "900px" });
    dialog.$wrapper.find(".modal-body").css({
        "max-height": "65vh",
        "overflow-y": "auto",
        "overflow-x": "hidden",
        "padding-right": "4px",
    });
    dialog.show();
}

function syncCrecheAgeWithOpeningDate() {
    const value = frappe.query_report.get_filter_value("creche_age");
    
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