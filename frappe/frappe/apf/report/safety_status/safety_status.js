// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Safety status"] = {
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
            "fieldname": "level",
            "label": __("Level"),
            "fieldtype": "Select",
            "options": [
                { "value": "", "label": __(" ") },
                { "value": "1", "label": __("Partner") },
                { "value": "2", "label": __("State") },
                { "value": "3", "label": __("District") },
                { "value": "4", "label": __("Block") },
                { "value": "5", "label": __("Gram Panchayat") },
                { "value": "6", "label": __("Supervisor") },
                { "value": "", "label": __("Creche") },
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
            "fieldname": "safety_indicators",
            "label": __("Safety indicators"),
            "fieldtype": "Select",
            "options": [
                { "value": "0", "label": __("ALL") },
                { "value": "1", "label": __("Infrastructural & Environmental Safety") },
                { "value": "2", "label": __("Physical Safety & Security") },
                { "value": "3", "label": __("Fire Safety") },
                { "value": "4", "label": __("Electrical Safety") },
                { "value": "5", "label": __("Food Safety") },
                { "value": "6", "label": __("Others") },
            ],
            "default": "1",
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
        const fn = column.fieldname || "";

        // Grouped level columns: one column per question, counts stored as fn_yes/no/not/other in data
        if (data && (data[fn + "_yes"] !== undefined || data[fn + "_no"] !== undefined)) {
            const is_total = value === "__total__";
            const label = column.label || "";
            const filters = {};
            if (!is_total) {
                Object.keys(SAFETY_DRILL_FILTER_MAP).forEach(function (key) {
                    if (data[key]) filters[SAFETY_DRILL_FILTER_MAP[key]] = data[key];
                });
            }

            const parts = [
                { answer: "yes",   text: "Yes",          color: "#006600", fw: is_total ? "800" : "600" },
                { answer: "no",    text: "No",           color: "#CC0000", fw: is_total ? "800" : "600" },
                { answer: "not",   text: "Not Observed", color: "#999900", fw: is_total ? "800" : "600" },
                { answer: "other", text: "Other",        color: "#CC6600", fw: is_total ? "800" : "600" },
            ];

            const sep = `<span style="color:#666; margin: 0 4px;">||</span>`;

            return parts.map(function (p) {
                const count = parseInt(data[fn + "_" + p.answer] || 0, 10);
                const ctx = { field: fn, label: label, answer: p.answer, filters: filters };
                return `<span class="safety-count-link"
                    data-ctx="${encodeURIComponent(JSON.stringify(ctx))}"
                    title="${__("Click to view details")}"
                    style="cursor:pointer; color:${p.color}; font-weight:${p.fw}; text-decoration:underline;"
                ><b>${p.text}:</b> ${count}</span>`;
            }).join(sep);
        }

        // Individual (suffix) columns – kept for backward compat if ever used
        const match = /_(yes|no|not|other)$/.exec(fn);
        if (!match || value === undefined || value === null || value === "") {
            return default_formatter(value, row, column, data);
        }

        const answer = match[1];
        const meta = SAFETY_ANSWER_META[answer];
        const is_total = /<b>/i.test(String(value));
        const count = String(value).replace(/<[^>]*>/g, "").trim();

        const ctx = {
            field: fn.replace(/_(yes|no|not|other)$/, ""),
            label: (column.label || "").replace(/\s*-\s*\((Yes|No|Not Observed|Other)\)\s*$/, ""),
            answer: answer,
            filters: {},
        };

        if (data && !is_total) {
            Object.keys(SAFETY_DRILL_FILTER_MAP).forEach(function (key) {
                if (data[key]) ctx.filters[SAFETY_DRILL_FILTER_MAP[key]] = data[key];
            });
        }

        return `<span class="safety-count-link"
            data-ctx="${encodeURIComponent(JSON.stringify(ctx))}"
            title="${__("Click to view details")}"
            style="cursor: pointer; color: ${meta.color}; font-weight: ${is_total ? "800" : "600"}; text-decoration: underline;">${count}</span>`;
    },

    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        $(report.page.wrapper)
            .off("click.safety_drill")
            .on("click.safety_drill", ".safety-count-link", function () {
                const ctx = JSON.parse(decodeURIComponent($(this).attr("data-ctx")));
                show_safety_detail_popup(ctx);
            });
    }

};

const SAFETY_ANSWER_META = {
    yes: { text: "Yes", bg: "#CCFFCC", color: "#006600" },
    no: { text: "No", bg: "#FFCCCC", color: "#CC0000" },
    not: { text: "Not Observed", bg: "#FFFFCC", color: "#999900" },
    other: { text: "Other", bg: "#FFE5CC", color: "#CC6600" },
};

// ADDED: supervisor_link_id to map supervisor for drill-down popup
const SAFETY_DRILL_FILTER_MAP = {
    partner_link_id: "partner",
    state_link_id: "state",
    district_link_id: "district",
    block_link_id: "block",
    gp_link_id: "gp",
    supervisor_link_id: "supervisor_id",
};

function show_safety_detail_popup(ctx) {
    const meta = SAFETY_ANSWER_META[ctx.answer];

    const dialog = new frappe.ui.Dialog({
        title: __("Safety Status Details"),
        size: "extra-large",
    });

    dialog.$body.html(`
        <div style="margin-bottom: 12px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${frappe.utils.escape_html(ctx.label)}</div>
            <span style="background-color: ${meta.bg}; color: ${meta.color}; border-radius: 3px; font-weight: bold; padding: 4px 12px;">${__(meta.text)}</span>
        </div>
        <div class="safety-detail-body text-muted" style="padding: 20px; text-align: center;">${__("Loading...")}</div>
    `);
    dialog.show();

    dialog.$wrapper.find('.modal-dialog').css({
        'max-width': '90vw',
        'width': '90vw'
    });

    const filters = Object.assign({}, frappe.query_report.get_filter_values(), ctx.filters);
    delete filters.level;

    frappe.call({
        method: "frappe.desk.query_report.run",
        args: {
            report_name: "Safety (Individual)",
            filters: filters,
            ignore_prepared_report: 1,
        },
        callback: function (r) {
            const result = (r.message && r.message.result) || [];
            const rows = result.filter(function (row) {
                if (!row || Array.isArray(row)) return false;
                if (String(row.partner || "").includes("Total")) return false;
                const text = $("<div>").html(String(row[ctx.field] || "")).text().trim();
                return ctx.answer === "other" ? text.indexOf("Other") === 0 : text === meta.text;
            });
            render_safety_detail_rows(dialog, ctx, rows);
        },
        error: function () {
            dialog.$body
                .find(".safety-detail-body")
                .html(`<div class="text-danger">${__("Unable to load details.")}</div>`);
        },
    });
}

function get_safety_detail_columns(ctx) {
    const esc = frappe.utils.escape_html;
    return [
        { label: __("Date of Visit"), get: (row) => esc(frappe.datetime.str_to_user(row.date_of_visit) || "") },
        { label: __("Partner"), get: (row) => esc(row.partner || "") },
        { label: __("State"), get: (row) => esc(row.state || "") },
        { label: __("District"), get: (row) => esc(row.district || "") },
        { label: __("Block"), get: (row) => esc(row.block || "") },
        { label: __("Gram Panchayat"), get: (row) => esc(row.gp || "") },
        { label: __("Supervisor"), get: (row) => esc(row.supervisor || "") },
        { label: __("User"), get: (row) => esc(row.user || "") },
        { label: __("Designation"), get: (row) => esc(row.designation || "") },
        { label: __("Creche"), get: (row) => esc(row.creche || "") },
        { label: __("Creche ID"), get: (row) => esc(row.creche_id || "") },
        { label: __("Response"), get: (row) => row[ctx.field] || "" },
    ];
}

function render_safety_detail_rows(dialog, ctx, rows) {
    const $body = dialog.$body.find(".safety-detail-body");

    if (!rows.length) {
        $body.html(`<div class="text-muted">${__("No matching records found.")}</div>`);
        return;
    }

    const detail_columns = get_safety_detail_columns(ctx);

    const head = detail_columns
        .map((c) => `<th style="white-space: nowrap;">${c.label}</th>`)
        .join("");
    const body_rows = rows
        .map(function (row, i) {
            const cells = detail_columns.map((c) => `<td style="vertical-align: middle; white-space: nowrap;">${c.get(row)}</td>`).join("");
            return `<tr><td style="vertical-align: middle; white-space: nowrap;">${i + 1}</td>${cells}</tr>`;
        })
        .join("");

    $body.removeClass("text-muted").css({ padding: 0, "text-align": "left" }).html(`
        <div style="margin-bottom: 8px; font-size: 13px;">${__("Total records")}: <b>${rows.length}</b></div>
        <div style="max-height: 60vh; max-width: 100%; overflow-x: auto; overflow-y: auto; border: 1px solid var(--border-color, #d1d8dd); border-radius: 4px;">
            <table class="table table-bordered" style="margin: 0;">
                <thead style="position: sticky; top: 0; background: var(--card-bg, #fff); z-index: 1;">
                    <tr><th style="white-space: nowrap;">No.</th>${head}</tr>
                </thead>
                <tbody>${body_rows}</tbody>
            </table>
        </div>
    `);

    dialog.set_primary_action(__("Download PDF"), function () {
        download_safety_detail_pdf(ctx, rows);
    });

    let $excel_btn = $('<button class="btn btn-default btn-sm" style="margin-right: 8px;">Download Excel</button>');
    $excel_btn.on('click', function() {
        download_safety_detail_excel(ctx, rows);
    });
    
    dialog.get_primary_btn().before($excel_btn);
}

function download_safety_detail_pdf(ctx, rows) {
    const meta = SAFETY_ANSWER_META[ctx.answer];
    const esc = frappe.utils.escape_html;
    const detail_columns = get_safety_detail_columns(ctx);

    const head = detail_columns.map((c) => `<th>${c.label}</th>`).join("");
    const body_rows = rows
        .map(function (row, i) {
            const cells = detail_columns.map((c) => `<td>${c.get(row)}</td>`).join("");
            return `<tr><td>${i + 1}</td>${cells}</tr>`;
        })
        .join("");

    const html = `<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, Helvetica, sans-serif; font-size: 11px; color: #36414c; }
                .title { font-size: 16px; font-weight: bold; margin-bottom: 8px; }
                .question { font-size: 13px; font-weight: bold; margin-bottom: 6px; }
                .answer-chip { display: inline-block; background-color: ${meta.bg}; color: ${meta.color}; border-radius: 3px; font-weight: bold; padding: 3px 10px; margin-bottom: 10px; }
                .total { margin-bottom: 8px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #d1d8dd; padding: 4px 6px; text-align: left; vertical-align: middle; }
                th { background-color: #f5f7fa; }
            </style>
        </head>
        <body>
            <div class="title">${__("Safety Status Details")}</div>
            <div class="question">${esc(ctx.label)}</div>
            <div class="answer-chip">${__(meta.text)}</div>
            <div class="total">${__("Total records")}: <b>${rows.length}</b></div>
            <table>
                <thead><tr><th>No.</th>${head}</tr></thead>
                <tbody>${body_rows}</tbody>
            </table>
        </body>
        </html>`;

    open_url_post(frappe.request.url, {
        cmd: "frappe.utils.print_format.report_to_pdf",
        html: html,
        orientation: "Landscape",
    });
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

function download_safety_detail_excel(ctx, rows) {
    frappe.require('https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js', function() {
        const detail_columns = get_safety_detail_columns(ctx);
        
        const headers = detail_columns.map(c => c.label || "");
        
        const data = rows.map(row => {
            return detail_columns.map(c => {
                let val = c.get(row) || "";
                if (typeof val === "string") {
                    val = $("<div>").html(val).text().trim();
                }
                return val;
            });
        });
        
        const sheetData = [headers, ...data];
        
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.aoa_to_sheet(sheetData);
        
        const colWidths = headers.map(h => ({ wch: Math.max(h.length + 5, 15) }));
        ws['!cols'] = colWidths;
        
        XLSX.utils.book_append_sheet(wb, ws, "Safety Details");
        XLSX.writeFile(wb, `${ctx.label.replace(/[^a-z0-9\s]/gi, '')} - Safety Details.xlsx`);
    });
}