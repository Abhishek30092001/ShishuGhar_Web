// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["LPG Report"] = {
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
                return {
                    filters: { "is_active": 1 }
                };
            },
            on_change: function () {
                frappe.query_report.set_filter_value("district", "");
                frappe.query_report.set_filter_value("block", "");
                frappe.query_report.set_filter_value("gp", "");
                frappe.query_report.set_filter_value("creche", "");
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
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "creche",
            label: __("Creche"),
            fieldtype: "Link",
            options: "Creche",
        },
        {
            fieldname: "supervisor_id",
            label: __("Supervisor"),
            fieldtype: "Link",
            options: "User",
        },
        {
            fieldname: "level",
            label: __("Level"),
            fieldtype: "Select",
            options: [
                { "value": "", "label": __("Level") },
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

    get_datatable_options(options) {
        return Object.assign(options, {
            cellClick: function (e, cell) {
                if (!cell || cell.column === undefined) return;

                const col = frappe.query_report.columns[cell.column - 1];
                if (!col || col.fieldname !== "alt_fuel_creches") return;

                const raw = (cell.content || "").toString().replace(/<[^>]*>/g, "").trim();
                if (!raw || raw === "0") return;

                const row = frappe.query_report.data[cell.rowIndex - 1];
                if (!row) return;

                frappe.call({
                    method: "shishughar.shishughar.report.lpg_report.lpg_report.get_alternative_fuel_details",
                    args: {
                        partner:    row.partner    || "",
                        state:      row.state      || "",
                        district:   row.district   || "",
                        block:      row.block      || "",
                        gp:         row.gp         || "",
                        supervisor: row.supervisor || "",
                        creche_id:  row.creche_id  || "",
                    },
                    callback: function (r) {
                        if (!r.message || !r.message.length) {
                            frappe.msgprint(__("No alternative fuel creches found."));
                            return;
                        }

                        const rows = r.message.map(d => `
                            <tr>
                                <td>${d.creche || ""}</td>
                                <td>${d.creche_id || ""}</td>
                                <td>${d.supplied_fuel_source || ""}</td>
                                <td>${d.current_source_of_fuel || ""}</td>
                                <td>${d.alternative_source || ""}</td>
                                <td>${d.date_of_supply || ""}</td>
                            </tr>
                        `).join("");

                        frappe.msgprint({
                            title: __("Creches Running on Alternative Fuel"),
                            message: `
                                <table class="table table-bordered table-condensed">
                                    <thead>
                                        <tr>
                                            <th>${__("Creche")}</th>
                                            <th>${__("Creche ID")}</th>
                                            <th>${__("Supplied Fuel Source")}</th>
                                            <th>${__("Current Source of Fuel")}</th>
                                            <th>${__("Alternative Source")}</th>
                                            <th>${__("Date of Supply")}</th>
                                        </tr>
                                    </thead>
                                    <tbody>${rows}</tbody>
                                </table>
                            `,
                            wide: true
                        });
                    }
                });
            }
        });
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
    }
};

