// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Vaccine Report"] = {
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
				{ "value": "", "label": __("Level") },
				{ "value": "1", "label": __("Partner") },
				{ "value": "2", "label": __("State") },
				{ "value": "3", "label": __("District") },
				{ "value": "4", "label": __("Block") },
				{ "value": "5", "label": __("Supervisor") },
				{ "value": "6", "label": __("GP") },
				{ "value": "7", "label": __("Creche") },
				{ "value": "8", "label": __("Child") },
			],
			"default": "8",
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
            "fieldname": "safety_indicators",
            "label": __("Safety indicators"),
            "fieldtype": "Select",
            "options": [
                { "value": "0", "label": __("All") },
                { "value": "1", "label": __("IPV") },
                { "value": "2", "label": __("Vitamin A") },
                { "value": "3", "label": __("PCV Booster") },
                { "value": "4", "label": __("PCV") },
                { "value": "5", "label": __("JE") },
                { "value": "6", "label": __("Albendazole") },
                { "value": "7", "label": __("Rota") },
                { "value": "8", "label": __("DPT Booster") },
                { "value": "9", "label": __("Pentavalent") },
                { "value": "10", "label": __("Measles") },
                { "value": "11", "label": __("OPV Booster") },
                { "value": "12", "label": __("BCG") },
                { "value": "13", "label": __("Hepatitis") }
            ],
            "default": "1",
        },
        // Age of Creche Filter
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

    // Added onload to append the custom Download Report button
    onload: function (report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        inject_vaccine_count_styles();

        // Delegate clicks on the clickable count links rendered in the report.
        // Bind once per report load on the report's wrapper.
        const $wrapper = report.page.main || $(report.wrapper);
        $wrapper.off("click.vaccineCount").on(
            "click.vaccineCount",
            "a.vaccine-count-link",
            function (e) {
                e.preventDefault();
                e.stopPropagation();
                let ctx;
                try {
                    ctx = JSON.parse($(this).attr("data-ctx"));
                } catch (err) {
                    frappe.msgprint(__("Unable to read count details."));
                    return;
                }
                show_count_details_dialog(ctx);
            }
        );
    }
};

// Clickable counts look like plain text; underline + pointer only on hover.
function inject_vaccine_count_styles() {
    if (document.getElementById("vaccine-count-link-style")) return;
    const style = document.createElement("style");
    style.id = "vaccine-count-link-style";
    style.textContent = `
        a.vaccine-count-link { color: inherit !important; text-decoration: none !important; cursor: pointer; }
        a.vaccine-count-link:hover { text-decoration: underline !important; }
        .vaccine-details-wrap { width: 100%; }
        .vaccine-details-wrap table { margin-bottom: 0; white-space: nowrap; border-collapse: separate; border-spacing: 0; }
        .vaccine-details-scroll { max-height: 60vh; overflow: auto; }
        /* Freeze the header row while scrolling. */
        .vaccine-details-scroll thead th {
            position: sticky;
            top: 0;
            z-index: 2;
            background: #f5f5f5;
            box-shadow: inset 0 -1px 0 #ddd, inset 0 1px 0 #ddd;
        }
    `;
    document.head.appendChild(style);
}

const POPUP_CHUNK_SIZE = 200;

function show_count_details_dialog(ctx) {
    const filters = frappe.query_report.get_filter_values(true) || {};
    const esc = frappe.utils.escape_html;

    // For the vaccine popup, "Vaccinated" is the default sub-filter.
    if (ctx.metric === "vaccine" && !ctx.vac_filter) {
        ctx.vac_filter = "vaccinated";
    }

    const dialog = new frappe.ui.Dialog({
        title: __("Loading..."),
        size: "extra-large",
        fields: [{ fieldtype: "HTML", fieldname: "details_html" }]
    });

    // Make the dialog noticeably wider than the default extra-large.
    dialog.$wrapper.find(".modal-dialog").css({ "max-width": "92vw", "width": "92vw" });

    const $body = dialog.fields_dict.details_html.$wrapper;

    // Renders one server response into the dialog body.
    const render_response = (res) => {
        const columns = res.columns || [];
        const rows = res.rows || [];
        const total = res.total != null ? res.total : rows.length;
        const title = res.title || __("Details");

        dialog.set_title(`${title} (${total})`);

        const header_html = columns.map(c => `<th>${esc(c)}</th>`).join("");

        // Vaccinated / Eligible sub-filter (only for the vaccine popup).
        let filter_html = "";
        if (res.metric === "vaccine") {
            const vf = res.vac_filter || "vaccinated";
            filter_html = `
                <div class="vaccine-details-filter" style="padding:4px 2px 10px;">
                    <label style="margin-right:8px;font-weight:600;">${__("Show")}:</label>
                    <select class="form-control input-sm vaccine-vac-filter" style="width:auto;display:inline-block;">
                        <option value="vaccinated" ${vf === "vaccinated" ? "selected" : ""}>${__("Vaccinated")}</option>
                        <option value="eligible" ${vf === "eligible" ? "selected" : ""}>${__("Eligible")}</option>
                        <option value="not_vaccinated" ${vf === "not_vaccinated" ? "selected" : ""}>${__("Not Vaccinated")}</option>
                    </select>
                </div>`;
        }

        $body.html(`
            <div class="vaccine-details-wrap">
                ${filter_html}
                <div class="vaccine-details-scroll">
                    <table class="table table-bordered table-sm">
                        <thead><tr>${header_html}</tr></thead>
                        <tbody class="vaccine-details-body"></tbody>
                        <tfoot class="vaccine-details-foot"></tfoot>
                    </table>
                </div>
                <div class="vaccine-details-status text-muted small" style="padding:6px 2px;"></div>
            </div>
        `);

        const $tbody = $body.find(".vaccine-details-body");
        const $tfoot = $body.find(".vaccine-details-foot");
        const $status = $body.find(".vaccine-details-status");

        if (rows.length === 0) {
            $tbody.html(
                `<tr><td colspan="${columns.length || 1}" style="text-align:center;">${__("No records found")}</td></tr>`
            );
        } else {
            // --- Chunked / lazy rendering to avoid freezing on big datasets ---
            let rendered = 0;
            const $scroll = $body.find(".vaccine-details-scroll");

            const render_chunk = () => {
                const end = Math.min(rendered + POPUP_CHUNK_SIZE, rows.length);
                let chunk_html = "";
                for (let i = rendered; i < end; i++) {
                    const row = rows[i];
                    const cells = columns.map(c => {
                        let val = row[c];
                        if (val === null || val === undefined) val = "";
                        return `<td>${esc(String(val))}</td>`;
                    }).join("");
                    chunk_html += `<tr>${cells}</tr>`;
                }
                $tbody.append(chunk_html);
                rendered = end;

                if (rendered < rows.length) {
                    $status.text(__("Showing {0} of {1} — scroll for more", [rendered, rows.length]));
                } else {
                    $status.text(__("Showing all {0} records", [rows.length]));
                }
            };

            render_chunk();

            $scroll.on("scroll", function () {
                if (rendered >= rows.length) return;
                const el = this;
                if (el.scrollTop + el.clientHeight >= el.scrollHeight - 80) {
                    render_chunk();
                }
            });
        }

        // Total row: show the actual count, not just the word "Total".
        let total_label;
        if (res.metric === "creches") {
            total_label = __("Total Creches");
        } else if (res.metric === "vaccine") {
            if (res.vac_filter === "eligible") total_label = __("Total Eligible");
            else if (res.vac_filter === "not_vaccinated") total_label = __("Total Not Vaccinated");
            else total_label = __("Total Vaccinated");
        } else {
            total_label = __("Total Children");
        }
        $tfoot.html(`
            <tr style="font-weight:bold;background:#f5f5f5;">
                <td colspan="${Math.max(columns.length - 1, 1)}" style="text-align:right;">${esc(total_label)}:</td>
                <td>${total}</td>
            </tr>
        `);

        // Re-fetch when the Vaccinated/Eligible filter changes.
        $body.find(".vaccine-vac-filter").on("change", function () {
            ctx.vac_filter = $(this).val();
            fetch_and_render();
        });

        // Download button (XLSX) at the bottom-right of the popup.
        dialog.set_primary_action(__("Download (XLSX)"), function () {
            download_details_xlsx(filters, ctx);
        });
        dialog.$wrapper.find(".modal-footer").css("text-align", "right");
    };

    // Fetches data for the current ctx (including any vac_filter) and renders it.
    const fetch_and_render = () => {
        frappe.call({
            method: "frappe.apf.report.vaccine_report.vaccine_report.get_count_details",
            args: {
                filters: JSON.stringify(filters),
                ctx: JSON.stringify(ctx)
            },
            freeze: true,
            freeze_message: __("Loading details..."),
            callback: function (r) {
                render_response(r.message || {});
            }
        });
    };

    dialog.show();
    fetch_and_render();
}

// Export the popup's dataset as a true .xlsx file. The server re-runs the same
// query and streams an Excel workbook, so the download always matches the popup.
function download_details_xlsx(filters, ctx) {
    open_url_post(
        "/api/method/frappe.apf.report.vaccine_report.vaccine_report.download_count_details_xlsx",
        {
            filters: JSON.stringify(filters),
            ctx: JSON.stringify(ctx)
        }
    );
}

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
            "7-12 Month": 9,    // Using 9 months as representative (middle of 7-12)
            "13-18 Month": 15,  // Using 15 months as representative (middle of 13-18)
            "19-24 Month": 21,  // Using 21 months as representative (middle of 19-24)
            "24+ Month": 24     // Using 24 months as minimum
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