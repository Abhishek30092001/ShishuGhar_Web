// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Fire Extinguisher Status"] = {
    filters: [
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
                return { filters: { "is_active": 1 } };
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
                { "value": "",  "label": __("Level") },
                { "value": "1", "label": __("Partner") },
                { "value": "2", "label": __("State") },
                { "value": "3", "label": __("District") },
                { "value": "4", "label": __("Block") },
                { "value": "5", "label": __("Supervisor") },
                { "value": "6", "label": __("GP") },
                { "value": "7", "label": __("Creche") },
            ],
            default: "",
            on_change: function () {
                frappe.query_report.refresh();
            }
        },
    ],

    onload: function (report) {
        const style = document.createElement("style");
        style.innerHTML = `
            [data-label="Export"],
            [data-original-title="Export"] {
                display: none !important;
            }
            .fe-popup-overlay {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.5); z-index: 9998;
                display: flex; align-items: center; justify-content: center;
            }
            .fe-popup-box {
                background: #fff; border-radius: 6px; padding: 20px;
                max-width: 900px; width: 95%; max-height: 80vh;
                overflow-y: auto; z-index: 9999; position: relative;
                box-shadow: 0 8px 30px rgba(0,0,0,0.25);
            }
            .fe-popup-box h5 {
                margin: 0 0 12px; font-size: 15px; font-weight: 600; color: #333;
            }
            .fe-popup-close {
                position: absolute; top: 12px; right: 16px;
                cursor: pointer; font-size: 20px; color: #666; line-height: 1;
            }
            .fe-popup-close:hover { color: #000; }
            .fe-popup-table {
                width: 100%; border-collapse: collapse; font-size: 13px;
            }
            .fe-popup-table th {
                background: #f0f0f0; padding: 8px 10px;
                text-align: left; border: 1px solid #ddd; white-space: nowrap;
            }
            .fe-popup-table td {
                padding: 7px 10px; border: 1px solid #eee;
            }
            .fe-popup-table tr:nth-child(even) td { background: #fafafa; }
            .fe-popup-link { text-decoration: none; color: #2490ef; }
            .fe-popup-link:hover { text-decoration: underline; }
        `;
        document.head.appendChild(style);

        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        // Delegate click on popup links in the report table
        $(report.wrapper).on("click", ".fe-popup-link", function (e) {
            e.preventDefault();
            const status   = $(this).data("status");
            const rawPopup = this.getAttribute("data-popup");
            let rows = [];
            try {
                rows = JSON.parse(rawPopup.replace(/&quot;/g, '"').replace(/&#39;/g, "'"));
            } catch (_) {}
            show_fe_popup(status, rows);
        });
    }
};

function show_fe_popup(status, rows) {
    $(".fe-popup-overlay").remove();

    const headers = ["Sr.No", "Partner", "State", "District", "Block", "Gram Panchayat", "Creche", "Creche ID"];
    const keys    = ["sr_no", "partner", "state", "district", "block", "gp", "creche", "creche_id"];

    let thead = "<tr>" + headers.map(h => `<th>${h}</th>`).join("") + "</tr>";
    let tbody = rows.map(row =>
        "<tr>" + keys.map(k => `<td>${row[k] || ""}</td>`).join("") + "</tr>"
    ).join("");

    const html = `
        <div class="fe-popup-overlay">
            <div class="fe-popup-box">
                <span class="fe-popup-close">&times;</span>
                <h5>Fire Extinguisher Status: ${frappe.utils.escape_html(status)} (${rows.length} record${rows.length !== 1 ? "s" : ""})</h5>
                <table class="fe-popup-table">
                    <thead>${thead}</thead>
                    <tbody>${tbody}</tbody>
                </table>
            </div>
        </div>
    `;

    const $overlay = $(html).appendTo("body");

    $overlay.on("click", function (e) {
        if ($(e.target).hasClass("fe-popup-overlay") || $(e.target).hasClass("fe-popup-close")) {
            $overlay.remove();
        }
    });

    $(document).one("keydown.fe_popup", function (e) {
        if (e.key === "Escape") {
            $overlay.remove();
            $(document).off("keydown.fe_popup");
        }
    });
}
