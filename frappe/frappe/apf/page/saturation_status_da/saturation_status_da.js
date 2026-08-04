frappe.pages['saturation-status-da'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Saturation Status Dashboard',
        single_column: true
    });
    frappe.require([
        "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js",
        "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
        "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
        "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
    ]);

    let filters = [
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            options: (() => {
                const start_year = 2024;
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
                { "value": "1", "label": __("January") },
                { "value": "2", "label": __("February") },
                { "value": "3", "label": __("March") },
                { "value": "4", "label": __("April") },
                { "value": "5", "label": __("May") },
                { "value": "6", "label": __("June") },
                { "value": "7", "label": __("July") },
                { "value": "8", "label": __("August") },
                { "value": "9", "label": __("September") },
                { "value": "10", "label": __("October") },
                { "value": "11", "label": __("November") },
                { "value": "12", "label": __("December") }
            ],
            "default": (new Date().getMonth() + 1).toString(),
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
            "fieldname": "block",
            "label": __("Block"),
            "fieldtype": "Link",
            "options": "Block",
            "get_query": function () {
                let district = page.fields_dict["district"].get_value();
                if (district) {
                    return {
                        filters: {
                            district_id: district
                        }
                    };
                }
                return {};
            }
        },
        {
            fieldname: "level",
            label: __("Level"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("Level") },
                { value: "2", label: __("State") },
                { value: "3", label: __("District") },
                { value: "4", label: __("Block") }
            ],
            default: "2",
            onchange: function () {
                updateFilterDesc();
            }
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
        }
    ];

    filters.forEach(f => {
        delete f.onchange;
        delete f.on_change;
        page.add_field(f);
    });

    function resetForwardFilters(currentFilter) {
        let currentIndex = filters.findIndex(filter => filter.fieldname === currentFilter);
        if (currentIndex === -1) return;

        for (let i = currentIndex + 1; i < filters.length; i++) {
            if (filters[i].fieldname == "creche_status_id" || filters[i].fieldname == "phases")
                continue;
            if (page.fields_dict[filters[i].fieldname]) {
                page.fields_dict[filters[i].fieldname].set_value("");
            }
        }
    }

    filters.forEach(filter => {
        if ((filter.fieldtype === "Link" || filter.fieldtype === "Select") && filter.fieldname != "year" && filter.fieldname != "month") {
            const input = page.fields_dict[filter.fieldname] ? page.fields_dict[filter.fieldname].$input : null;
            if (input) {
                input.on("change", () => {
                    resetForwardFilters(filter.fieldname);
                });
            }
        }
    });

    let searchBtn = page.add_button(`Search`, () => {
        searchBtn.text('Searching....');
        searchBtn.prop('disabled', true);
        load_data(() => {
            searchBtn.text('Search');
            searchBtn.prop('disabled', false);
        });
    });

    let resetBtn = page.add_button(`Reset`, () => {
        resetBtn.prop('disabled', true);
        location.reload();
    });

    searchBtn.css({
        "background-color": "#5979aa",
        "color": "white",
        "border": "1px solid #5979aa",
        "border-radius": "4px",
        "padding": "5px 16px",
        "font-weight": "500",
        "font-size": "14px"
    });
    resetBtn.css({
        "background-color": "#f9fafb",
        "color": "#1f2937",
        "border": "1px solid #d1d5db",
        "border-radius": "4px",
        "padding": "5px 16px",
        "font-weight": "500",
        "font-size": "14px"
    });

    let downloadDropdown = $(`
        <div class="dropdown custom-dropdown" style="display:inline-block; position: relative;">
            <button class="btn btn-default btn-sm dropdown-toggle" type="button" style="background-color: #5979aa; color: white; border: 1px solid #5979aa; border-radius: 4px; padding: 5px 16px; font-weight: 500; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center;">
                <span>Download</span>
            </button>
            <div class="dropdown-menu" style="display: none; position: absolute; top: 100%; left: 0; background-color: white; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; min-width: 100%; margin-top: 0; padding: 5px 0;">
                <a href="#" class="dropdown-item" id="dl-png" style="display: block; padding: 8px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee;">PNG</a>
                <a href="#" class="dropdown-item" id="dl-csv" style="display: block; padding: 8px 16px; color: #333; text-decoration: none;">CSV</a>
            </div>
        </div>
    `);

    page.page_actions.append(downloadDropdown);

    let hideTimeout;
    downloadDropdown.hover(
        function () {
            clearTimeout(hideTimeout);
            $(this).find('.dropdown-menu').show();
        },
        function () {
            let menu = $(this).find('.dropdown-menu');
            hideTimeout = setTimeout(() => {
                menu.hide();
            }, 150);
        }
    );

    downloadDropdown.find('.dropdown-item').hover(
        function () { $(this).css('background-color', '#f5f5f5'); },
        function () { $(this).css('background-color', 'white'); }
    );

    let map_container = $('<div class="map-view-container" style="background-color: #f4f5f6; min-height: 500px;"></div>').appendTo(page.main);

    if (!document.getElementById('map-label-style')) {
        let style = document.createElement('style');
        style.id = 'map-label-style';
        style.innerHTML = `
            .leaflet-tooltip.map-label {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                font-family: 'Calibri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
                font-size: 11px !important;
                padding: 0 !important;
                white-space: nowrap;
                text-shadow: none !important;
            }
            .leaflet-tooltip.map-label::before,
            .leaflet-tooltip-left.map-label::before,
            .leaflet-tooltip-right.map-label::before,
            .leaflet-tooltip-top.map-label::before,
            .leaflet-tooltip-bottom.map-label::before { 
                display: none !important; 
            }
            .leaflet-overlay-pane svg {
                filter: drop-shadow(5px 5px 8px rgba(0,0,0,0.6));
            }
        `;
        document.head.appendChild(style);
    }

    function load_data(callback) {
        let values = {};
        for (let key in page.fields_dict) {
            if (page.fields_dict[key] && typeof page.fields_dict[key].get_value === 'function') {
                values[key] = page.fields_dict[key].get_value();
            }
        }

        if (values.level === "3" && !values.state) {
            frappe.msgprint(__("Please select a State to view the District level map."));
            if (typeof callback === 'function') callback();
            return;
        }

        if (values.level === "4" && !values.district) {
            frappe.msgprint(__("Please select a District to view the Block level map."));
            if (typeof callback === 'function') callback();
            return;
        }

        frappe.call({
            method: "frappe.apf.page.saturation_status_da.api_data.get_creche_master_data",
            args: {
                year: values.year,
                month: values.month,
                c_status: values.creche_status_id,
                partner: values.partner,
                state: values.state,
                district: values.district,
                block: values.block,
                gp: values.gp,
                village: values.village,
                supervisor_id: values.supervisor_id,
                creche: values.creche,
                phases: values.phases
            },
            callback: function (r) {
                if (r.message && r.message.data) {
                    render_map_view(r.message.data, values.level);

                    setTimeout(() => {
                        let mapElem = document.getElementById('export-map-container');
                        if (mapElem) {
                            mapElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 100);
                }
                if (typeof callback === 'function') callback();
            }
        });
    }

    function render_map_view(data, level) {
        map_container.empty();

        if (!level) {
            map_container.html('<div class="text-center text-muted" style="margin-top: 50px; font-size: 16px;">Please select a Level to view the map data.</div>');
            return;
        }

        let level_map = {
            "1": { key: "partner", label: "Partner" },
            "2": { key: "state", label: "State" },
            "3": { key: "district", label: "District" },
            "4": { key: "block", label: "Block" },
            "5": { key: "supervisor", label: "Creche Supervisor" },
            "6": { key: "gram_panchayat", label: "Gram Panchayat" },
            "8": { key: "village", label: "Village" },
            "7": { key: "creche", label: "Creche" }
        };

        let selected_level = level_map[level];
        if (!selected_level) return;

        let group_key = selected_level.key;
        let group_label = selected_level.label;

        window.currentMapData = data;
        window.currentMapGroupKey = group_key;

        // Build display-name → internal-id maps for drill-down navigation
        window._stateNameToId = {};
        window._districtNameToId = {};
        data.forEach(row => {
            if (row.state && row.state_id) window._stateNameToId[row.state] = row.state_id;
            if (row.district && row.district_id) window._districtNameToId[row.district] = row.district_id;
        });

        window.showDetailView = function (name) {
            if (!window.currentMapData) return;
            let filtered_data = window.currentMapData.filter(row => (row[window.currentMapGroupKey] || 'Unknown') === name);

            let rowsHTML = filtered_data.map((r, i) => `
                <tr class="detail-view-row">
                    <td style="padding: 8px; border: 1px solid #e5e7eb; text-align: center;">${i + 1}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.state_name || r.state || ''}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.district || ''}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.block || ''}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.gram_panchayat || ''}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.village || ''}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.creche || ''}</td>
                    <td style="padding: 8px; border: 1px solid #e5e7eb;">${r.creche_id || ''}</td>
                </tr>
            `).join('');

            let tableHTML = `
                <div style="margin-bottom: 12px; display: flex; gap: 10px;">
                    <input type="text" id="detail-view-search" placeholder="Search across all columns..." 
                        style="flex: 1; padding: 8px 12px; border-radius: 4px; border: 1px solid #d1d5db; outline: none; font-family: 'Calibri', sans-serif; font-size: 13px;"
                        onkeyup="
                            let filter = this.value.toLowerCase();
                            let rows = document.querySelectorAll('.detail-view-row');
                            rows.forEach(row => {
                                let text = row.innerText.toLowerCase();
                                row.style.display = text.includes(filter) ? '' : 'none';
                            });
                        ">
                    <button onclick="
                        if (typeof XLSX === 'undefined') { frappe.msgprint('Export library not loaded'); return; }
                        let wb = XLSX.utils.table_to_book(document.getElementById('detail-view-table'), {sheet: 'Details'});
                        XLSX.writeFile(wb, 'Detail_View_${name.replace(/[^a-zA-Z0-9]/g, '_')}.xlsx');
                    " style="background-color: #10b981; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 600; font-family: 'Calibri', sans-serif; display: flex; align-items: center; gap: 6px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        Download
                    </button>
                </div>
                <div style="max-height: 55vh; overflow: auto;">
                    <table id="detail-view-table" style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; font-family: 'Calibri', sans-serif;">
                        <thead style="position: sticky; top: 0; background-color: #f3f4f6; z-index: 10;">
                            <tr>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151; width: 50px;">Sr No.</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">State</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">District</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">Block</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">GP</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">Village</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">Creche</th>
                                <th style="padding: 8px; border: 1px solid #e5e7eb; color: #374151;">Creche ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHTML}
                        </tbody>
                    </table>
                </div>
            `;

            let d = new frappe.ui.Dialog({
                title: __('Details for ') + name,
                fields: [
                    {
                        fieldname: 'html_data',
                        fieldtype: 'HTML',
                        options: tableHTML
                    }
                ],
                size: 'extra-large',
                primary_action_label: __('Close'),
                primary_action(values) {
                    d.hide();
                }
            });
            d.show();
        };

        let grouped_data = {};
        let total_creches = new Set();
        let total_gps = new Set();
        let total_villages = new Set();

        data.forEach(row => {
            let name = row[group_key] || 'Unknown';
            if (!grouped_data[name]) {
                grouped_data[name] = {
                    creches: new Set(),
                    gps: new Set(),
                    villages: new Set()
                };
            }
            if (row.creche_id) {
                grouped_data[name].creches.add(row.creche_id);
                total_creches.add(row.creche_id);
            }
            if (row.gram_panchayat) {
                grouped_data[name].gps.add(row.gram_panchayat);
                total_gps.add(row.gram_panchayat);
            }
            if (row.village) {
                grouped_data[name].villages.add(row.village);
                total_villages.add(row.village);
            }
        });

        let pastel_colors = [
            '#e57373', '#f06292', '#ba68c8', '#9575cd', '#7986cb', '#64b5f6',
            '#4fc3f7', '#4dd0e1', '#4db6ac', '#81c784', '#aed581', '#dce775',
            '#fff176', '#ffd54f', '#ffb74d', '#ff8a65', '#a1887f', '#e0e0e0', '#90a4ae',
            '#ff5252', '#ff4081', '#e040fb', '#7c4dff', '#536dfe', '#448aff',
            '#40c4ff', '#18ffff', '#64ffda', '#69f0ae', '#b2ff59', '#eeff41',
            '#ffd740', '#ffab40', '#ff6e40'
        ];

        let table_html = `
            <div style="background-color: #5979aa; color: white; text-align: center; font-weight: 600; padding: 12px; font-size: 14px; text-transform: uppercase; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                COLOUR CODING DEPICTS THE ${group_label}S
            </div>
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-family: 'Calibri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #f3f4f6; color: #374151; font-weight: 600; font-size: 11px; border-bottom: 2px solid #e5e7eb;">
                        <th style="padding: 10px; border: 1px solid #e5e7eb; width: 34%;">${group_label.toUpperCase()}</th>
                        <th style="padding: 10px; border: 1px solid #e5e7eb; width: 22%;">CRECHE</th>
                        <th style="padding: 10px; border: 1px solid #e5e7eb; width: 22%;">GP</th>
                        <th style="padding: 10px; border: 1px solid #e5e7eb; width: 22%;">VILLAGE</th>
                    </tr>
                </thead>
                <tbody>
        `;

        let i = 0;
        for (let name in grouped_data) {
            let stats = grouped_data[name];
            let color = pastel_colors[i % pastel_colors.length];
            let text_color = (color === '#f1c40f') ? '#000' : '#fff';
            table_html += `
                <tr style="font-weight: 500; font-size: 13px;">
                    <td style="padding: 10px; border: 1px solid #e5e7eb; background-color: ${color}; color: ${text_color};">${name}</td>
                    <td style="padding: 10px; border: 1px solid #e5e7eb; background-color: #fff; color: #1f2937;">${stats.creches.size}</td>
                    <td style="padding: 10px; border: 1px solid #e5e7eb; background-color: #fff; color: #1f2937;">${stats.gps.size}</td>
                    <td style="padding: 10px; border: 1px solid #e5e7eb; background-color: #fff; color: #1f2937;">${stats.villages.size}</td>
                </tr>
            `;
            i++;
        }

        table_html += `
                </tbody>
            </table>
        `;

        let summary_table_html = `
            <table style="width: 100%; border-collapse: collapse; text-align: center; font-family: 'Calibri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-weight: 600; font-size: 14px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                <tbody>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px; background-color: #5979aa; color: white; width: 70%; text-align: left;">Total No of Operational Creche</td>
                        <td style="padding: 12px; background-color: #5979aa; color: white; width: 30%; font-size: 15px;">${total_creches.size}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #e5e7eb;">
                        <td style="padding: 12px; background-color: #fef08a; color: #1f2937; text-align: left;">Total No of GP</td>
                        <td style="padding: 12px; background-color: #fff; color: #1f2937; font-size: 15px;">${total_gps.size}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background-color: #fef08a; color: #1f2937; text-align: left;">Total No of Village</td>
                        <td style="padding: 12px; background-color: #fff; color: #1f2937; font-size: 15px;">${total_villages.size}</td>
                    </tr>
                </tbody>
            </table>
        `;

        let state_val = page.fields_dict["state"].get_value();
        let state_name = page.fields_dict["state"].$input ? page.fields_dict["state"].$input.val() : state_val;
        if (!state_name) state_name = state_val || '';
        let header_title = state_name ? `Dashboard Map View - ${state_name}` : `Dashboard Map View`;

        let full_html = `
            <div style="display: flex; flex-wrap: wrap; width: 100%; justify-content: space-between; align-items: stretch; padding: 20px; gap: 20px; background-color: #f4f6f8;">
                <div id="export-map-container" style="flex: 3 1 500px; min-width: 280px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; border-radius: 8px; position: relative; overflow: hidden; background-color: #e2f0f4;">
                    <div style="background-color: #5979aa; color: white; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-family: 'Calibri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 16px; z-index: 2; position: relative;">
                        <span>${header_title}</span>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <input type="text" id="map-text-filter" placeholder="Search by Name..." style="padding: 5px 12px; border-radius: 4px; border: 1px solid #60a5fa; background-color: #eff6ff; color: #5979aa; font-size: 12px; outline: none; width: 200px; font-weight: 500;">
                        </div>
                    </div>
                    <div id="leaflet-map" style="height: 70vh; min-height: 400px; max-height: 800px; width: 100%; background-color: transparent; z-index: 1;"></div>
                    <div id="map-legend-container" style="position: absolute; bottom: 15px; left: 15px; background: rgba(255,255,255,0.95); padding: 10px 15px; border: 1px solid #e5e7eb; border-radius: 6px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); font-family: 'Calibri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 12px; font-weight: 600; text-align: left; z-index: 999; max-height: 250px; overflow-y: auto; display: flex; flex-direction: column;">
                        <div style="display: flex; justify-content: space-between; align-items: center; cursor: pointer;" onclick="document.getElementById('map-legend-items').style.display = document.getElementById('map-legend-items').style.display === 'none' ? 'block' : 'none';">
                            <span style="color: #4b5563; font-size: 11px; text-transform: uppercase; margin-right: 20px;">Colour Legend</span>
                            <span style="font-size: 10px;">👁️</span>
                        </div>
                        <div id="map-legend-items" style="display: block; margin-top: 8px;">
                            ${Object.keys(grouped_data).map((name, idx) => `
                                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                    <span style="display: inline-block; width: 16px; height: 16px; background-color: ${pastel_colors[idx % pastel_colors.length]}; margin-right: 8px; border-radius: 4px;"></span>
                                    <span style="font-size: 12px; color: #1f2937;">${name}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
                <div style="flex: 1 1 250px; min-width: 250px; display: flex; flex-direction: column; gap: 15px;">
                    ${summary_table_html}
                    <div style="border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); max-height: 400px; overflow-y: auto; background-color: #fff;">
                        ${table_html}
                    </div>
                </div>
            </div>
        `;

        map_container.html(full_html);

        $('#map-text-filter').off('keyup').on('keyup', function () {
            let term = $(this).val().toLowerCase();

            // Filter table rows
            $(this).closest('.map-view-container').find('table:last tbody tr').each(function () {
                let text = $(this).find('td:first').text().toLowerCase();
                $(this).toggle(text.includes(term));
            });

            // Filter map features and zoom
            if (window.dashboardMap && window.dashboardMapFeatures) {
                let visibleBounds = [];
                window.dashboardMapFeatures.forEach(f => {
                    if (!f.featureName) return;
                    let text = f.featureName.toLowerCase();
                    if (text.includes(term)) {
                        if (!window.dashboardMap.hasLayer(f)) window.dashboardMap.addLayer(f);
                        if (f.getLatLng) {
                            visibleBounds.push([f.getLatLng().lat, f.getLatLng().lng]);
                        } else if (f.getBounds) {
                            let b = f.getBounds();
                            visibleBounds.push([b.getSouthWest().lat, b.getSouthWest().lng]);
                            visibleBounds.push([b.getNorthEast().lat, b.getNorthEast().lng]);
                        }
                    } else {
                        if (window.dashboardMap.hasLayer(f)) window.dashboardMap.removeLayer(f);
                    }
                });

                if (term.length > 0 && visibleBounds.length > 0) {
                    let latlngs = visibleBounds.map(b => L.latLng(b[0], b[1]));
                    let bounds = L.latLngBounds(latlngs);
                    window.dashboardMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
                }
            }
        });

        $('#dl-csv').off('click').on('click', function (e) {
            e.preventDefault();
            let dropdownMenu = $(this).closest('.dropdown-menu');
            dropdownMenu.hide();

            let toggleBtn = $(this).closest('.dropdown').find('.dropdown-toggle');
            let mainBtn = toggleBtn.find('span');
            let originalText = mainBtn.text();

            mainBtn.text("Downloading...");
            toggleBtn.prop('disabled', true);

            setTimeout(() => {
                let csvContent = "Level,Name,No of Creche Centre,No of GP,No of Village\n";
                for (let name in grouped_data) {
                    let stats = grouped_data[name];
                    let safeName = name.replace(/"/g, '""');
                    csvContent += `${group_label},"${safeName}",${stats.creches.size},${stats.gps.size},${stats.villages.size}\n`;
                }
                let blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                let url = URL.createObjectURL(blob);
                let link = document.createElement("a");
                link.setAttribute("href", url);
                link.setAttribute("download", "map_data.csv");
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                mainBtn.text(originalText);
                toggleBtn.prop('disabled', false);
            }, 500);
        });

        $('#dl-png').off('click').on('click', function (e) {
            e.preventDefault();
            let dropdownMenu = $(this).closest('.dropdown-menu');
            dropdownMenu.hide();

            let toggleBtn = $(this).closest('.dropdown').find('.dropdown-toggle');
            let mainBtn = toggleBtn.find('span');
            let originalText = mainBtn.text();

            mainBtn.text("Downloading...");
            toggleBtn.prop('disabled', true);

            let mapNode = document.getElementById('export-map-container');
            if (window.html2canvas) {
                html2canvas(mapNode, { useCORS: true, logging: false }).then(canvas => {
                    let link = document.createElement("a");
                    link.download = "map_view.png";
                    link.href = canvas.toDataURL("image/png");
                    link.click();
                    mainBtn.text(originalText);
                    toggleBtn.prop('disabled', false);
                }).catch(err => {
                    frappe.msgprint("Error exporting map: " + err);
                    mainBtn.text(originalText);
                    toggleBtn.prop('disabled', false);
                });
            } else {
                frappe.msgprint("PNG Export library not loaded yet.");
                mainBtn.text(originalText);
                toggleBtn.prop('disabled', false);
            }
        });

        // Initialize Map
        window.dashboardMapFeatures = [];

        // Navigate to District View from a state polygon click:
        // sets State filter (by internal ID) + Level=District, then reloads data.
        window.drillToDistrictView = function (stateName) {
            let stateId = (window._stateNameToId || {})[stateName] || stateName;
            if (page.fields_dict["state"]) {
                page.fields_dict["state"].set_value(stateId);
            }
            if (page.fields_dict["level"]) {
                page.fields_dict["level"].set_value("3");
            }
            ["district", "block"].forEach(fn => {
                if (page.fields_dict[fn]) page.fields_dict[fn].set_value("");
            });
            setTimeout(() => { load_data(); }, 200);
        };

        // Navigate to Block View from a district polygon click:
        // sets District filter (by internal ID) + Level=Block, then reloads data.
        window.drillToBlockView = function (districtName) {
            let districtId = (window._districtNameToId || {})[districtName] || districtName;
            if (page.fields_dict["district"]) {
                page.fields_dict["district"].set_value(districtId);
            }
            if (page.fields_dict["level"]) {
                page.fields_dict["level"].set_value("4");
            }
            if (page.fields_dict["block"]) page.fields_dict["block"].set_value("");
            setTimeout(() => { load_data(); }, 200);
        };

        // Load geolocation config from Python API (cached)
        function loadGeolocation() {
            if (window._geolocationData) {
                return Promise.resolve(window._geolocationData);
            }
            return new Promise((resolve, reject) => {
                frappe.call({
                    method: "frappe.apf.page.saturation_status_da.api_data.get_geolocation_config",
                    async: true,
                    callback: function (r) {
                        if (r.message) {
                            window._geolocationData = r.message;
                            resolve(r.message);
                        } else {
                            reject(new Error("No geolocation config returned"));
                        }
                    },
                    error: function (e) {
                        reject(e);
                    }
                });
            });
        }

        // Fetch boundary GeoJSON via server-side API (handles local ADM3 for blocks)
        function fetchBoundaryGeoJSON(level) {
            let stateVal = page.fields_dict["state"] ? page.fields_dict["state"].get_value() : "";
            let districtVal = page.fields_dict["district"] ? page.fields_dict["district"].get_value() : "";
            return new Promise((resolve, reject) => {
                frappe.call({
                    method: "frappe.apf.page.saturation_status_da.api_data.get_boundary_geojson",
                    args: { level: level, state: stateVal, district: districtVal },
                    async: true,
                    callback: function (r) {
                        if (r.message) {
                            resolve(r.message);
                        } else {
                            reject(new Error("No boundary GeoJSON returned"));
                        }
                    },
                    error: function (e) { reject(e); }
                });
            });
        }

        // Strip ADM3 suffixes from block shapeNames so they match DB block names
        function stripBlockSuffix(name) {
            return (name || "").replace(/\s*\bcd\s+block\b|\s*\bblock\b|\s*\(pt\.?\)|\s*\(part\)|\s*\btaluk\b|\s*\btehsil\b|\s*\bmandal\b/gi, "").trim();
        }

        // Returns true if a GeoJSON feature belongs to the currently selected scope
        // Acts as a client-side guard in case the backend returns more than needed.
        function isInScope(feature, level) {
            let p = feature.properties || {};
            let clean = s => (s || "").toLowerCase().replace(/[^a-z0-9]/g, "");

            if (level === "3") {
                // District GeoJSON: NAME_1 holds the state name
                let selectedState = page.fields_dict["state"].$input
                    ? page.fields_dict["state"].$input.val()
                    : (page.fields_dict["state"].get_value() || "");
                if (!selectedState) return true; // no filter applied
                let featState = p.NAME_1 || p.state || "";
                let cs = clean(selectedState), cf = clean(featState);
                // allow Orissa↔Odisha, Uttaranchal↔Uttarakhand
                let aliases = { "odisha": "orissa", "uttarakhand": "uttaranchal", "orissa": "odisha", "uttaranchal": "uttarakhand" };
                return cs === cf || aliases[cs] === cf || cs === aliases[cf];
            }
            return true;
        }

        // Get feature name based on level and GeoJSON source properties
        function getFeatureName(feature, level) {
            let p = feature.properties || {};
            if (level === "2") return p.ST_NM || p.name || p.NAME_1 || "";
            if (level === "3") return p.NAME_2 || p.district || "";
            if (level === "4") {
                let raw = p.shapeName || p.NAME_3 || p.taluk || p.tehsil || p.subdistrict || p.block || "";
                return stripBlockSuffix(raw);
            }
            return "";
        }

        // Get initial map center and zoom from geolocation.json metadata
        function getMapCenter(geoConfig, level) {
            let defaults = geoConfig.defaults || { center: [22.8, 83.9], zoom: 5 };
            let inputState = page.fields_dict["state"].$input ? page.fields_dict["state"].$input.val() : "";
            if (!inputState) inputState = page.fields_dict["state"].get_value() || "";
            let inputDistrict = page.fields_dict["district"].$input ? page.fields_dict["district"].$input.val() : "";
            if (!inputDistrict) inputDistrict = page.fields_dict["district"].get_value() || "";

            if (level === "3" && inputState && geoConfig.states) {
                let cleanInput = inputState.toLowerCase().replace(/[^a-z0-9]/g, '');
                for (let sName in geoConfig.states) {
                    let cleanS = sName.toLowerCase().replace(/[^a-z0-9]/g, '');
                    if (cleanS === cleanInput) {
                        return { center: geoConfig.states[sName].center, zoom: geoConfig.states[sName].zoom || 8 };
                    }
                }
            } else if (level === "4" && inputDistrict && geoConfig.districts) {
                let cleanInput = inputDistrict.toLowerCase().replace(/[^a-z0-9]/g, '');
                for (let dName in geoConfig.districts) {
                    let cleanD = dName.toLowerCase().replace(/[^a-z0-9]/g, '');
                    if (cleanD === cleanInput) {
                        return { center: geoConfig.districts[dName].center, zoom: geoConfig.districts[dName].zoom || 10 };
                    }
                }
            }

            return { center: defaults.center, zoom: defaults.zoom };
        }

        setTimeout(() => {
            if (typeof L !== 'undefined') {
                let map = L.map('leaflet-map', { scrollWheelZoom: false }).setView([22.8, 83.9], 5);
                window.dashboardMap = map;

                // Fix for URL changing to #close when a popup is closed
                map.on('popupopen', function (e) {
                    let closeBtn = e.popup._container.querySelector('.leaflet-popup-close-button');
                    if (closeBtn) {
                        closeBtn.removeAttribute('href');
                        closeBtn.style.cursor = 'pointer';
                    }
                });

                let bounds = [];

                function plotPoints() {
                    let pointBounds = [];
                    data.forEach(row => {
                        if (row.latitude && row.longitude) {
                            let name = row[group_key] || 'Unknown';
                            let colorIdx = Object.keys(grouped_data).indexOf(name);
                            let color = pastel_colors[colorIdx % pastel_colors.length];

                            let marker = L.circleMarker([row.latitude, row.longitude], {
                                radius: 6,
                                fillColor: color,
                                color: "#000",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            }).addTo(map);

                            marker.bindPopup(`
                                <div style="font-family: 'Calibri', sans-serif;">
                                    <b>${row.creche || 'Unnamed Creche'}</b><br>
                                    ${group_label}: ${name}<br>
                                    GP: ${row.gram_panchayat || 'N/A'}<br>
                                    Village: ${row.village || 'N/A'}<br>
                                    Status: ${row.creche_status_id || 'N/A'}<br>
                                    <button onclick="window.showDetailView('${name.replace(/'/g, "\\'")}')" style="margin-top: 8px; width: 100%; background-color: #5979aa; color: white; border: none; padding: 6px; border-radius: 4px; font-size: 12px; cursor: pointer; font-weight: 600;">Detail View</button>
                                </div>
                            `);
                            marker.bindTooltip(name, { permanent: true, direction: "top", className: "map-label" });

                            marker.featureName = name;
                            window.dashboardMapFeatures.push(marker);

                            pointBounds.push([row.latitude, row.longitude]);
                        }
                    });

                    if (pointBounds.length > 0) {
                        let mapBounds = L.latLngBounds(pointBounds);
                        // Using maxZoom to prevent zooming to infinity if there's only 1 point.
                        map.fitBounds(mapBounds, { padding: [20, 20], maxZoom: 14 });
                    }
                }

                if (level === "2" || level === "3" || level === "4") {
                    // Load geolocation config (for map center/zoom metadata)
                    loadGeolocation().then(geoConfig => {

                        // Set initial map view from JSON center/zoom
                        let mapCenter = getMapCenter(geoConfig, level);
                        map.setView(mapCenter.center, mapCenter.zoom);

                        // Fetch boundary GeoJSON via server API (uses local ADM3 for block level)
                        fetchBoundaryGeoJSON(level).then(geoData => {

                            // Fuzzy matching function to handle Indian naming variations
                            const getMatchedName = (featureName) => {
                                if (!featureName) return null;
                                let keys = Object.keys(grouped_data);
                                let cleanGeo = featureName.toLowerCase().replace(/[^a-z0-9]/g, '');

                                // 1. Exact alphanumeric match
                                let match = keys.find(k => k.toLowerCase().replace(/[^a-z0-9]/g, '') === cleanGeo);
                                if (match) return match;

                                // 2. Transliteration match (ignore 'h' for singh/sing, pore->pur)
                                let altGeo = cleanGeo.replace(/h/g, '').replace(/pore/g, 'pur');
                                match = keys.find(k => {
                                    let altK = k.toLowerCase().replace(/[^a-z0-9]/g, '').replace(/h/g, '').replace(/pore/g, 'pur');
                                    return altK === altGeo;
                                });
                                if (match) return match;

                                // 3. Substring match (e.g., "Kalyansingpur" inside "Kalyansingpur Block")
                                match = keys.find(k => {
                                    let cleanK = k.toLowerCase().replace(/[^a-z0-9]/g, '');
                                    return (cleanK.length > 4 && cleanGeo.includes(cleanK)) || (cleanGeo.length > 4 && cleanK.includes(cleanGeo));
                                });

                                return match || null;
                            };

                            let geoLayer = L.geoJSON(geoData, {
                                style: function (feature) {
                                    if (!isInScope(feature, level)) return { weight: 0, color: 'transparent', fillOpacity: 0, opacity: 0 };

                                    let featureName = getFeatureName(feature, level);
                                    if (!featureName) return { weight: 0, color: 'transparent', fillOpacity: 0, opacity: 0 };

                                    let matchName = getMatchedName(featureName);

                                    if (matchName) {
                                        let colorIdx = Object.keys(grouped_data).indexOf(matchName);
                                        let color = pastel_colors[colorIdx % pastel_colors.length];
                                        return { fillColor: color, weight: 1, color: '#555555', fillOpacity: 1, opacity: 1 };
                                    } else {
                                        // In-scope boundary with no data: neutral gray
                                        return { fillColor: '#e2e8f0', weight: 1, color: '#94a3b8', fillOpacity: 1, opacity: 1 };
                                    }
                                },
                                onEachFeature: function (feature, layer) {
                                    if (!isInScope(feature, level)) return;

                                    let featureName = getFeatureName(feature, level);
                                    if (!featureName) return;

                                    let matchName = getMatchedName(featureName);

                                    if (matchName) {
                                        let stats = grouped_data[matchName];

                                        let tooltipContent = `
                                            <div style="display: flex; align-items: center; gap: 2px;">
                                                <span style="width: 6px; height: 6px; background-color: #f472b6; border: 1px solid #9f1239; border-radius: 50%; display: inline-block;"></span>
                                                <span style="font-size: 10px; font-weight: 500; color: #000;">${matchName}</span>
                                            </div>
                                        `;
                                        layer.bindTooltip(tooltipContent, { permanent: true, direction: "center", className: "map-label" });

                                        // Build drill-down button based on current level
                                        let drillBtn = "";
                                        if (level === "2") {
                                            drillBtn = `<button onclick="window.drillToDistrictView('${matchName.replace(/'/g, "\\'")}')" style="margin-top: 4px; width: 100%; background-color: #0d9488; color: white; border: none; padding: 6px; border-radius: 4px; font-size: 12px; cursor: pointer; font-weight: 600;">District View</button>`;
                                        } else if (level === "3") {
                                            drillBtn = `<button onclick="window.drillToBlockView('${matchName.replace(/'/g, "\\'")}')" style="margin-top: 4px; width: 100%; background-color: #7c3aed; color: white; border: none; padding: 6px; border-radius: 4px; font-size: 12px; cursor: pointer; font-weight: 600;">Block View</button>`;
                                        }

                                        layer.bindPopup(`
                                            <div style="font-family: 'Calibri', sans-serif; min-width: 150px;">
                                                <div style="font-weight: 600; font-size: 14px; margin-bottom: 8px; color: #1f2937; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">
                                                    ${matchName}
                                                </div>
                                                <div style="font-size: 13px; color: #4b5563;">
                                                    <div style="margin-bottom: 4px;"><b>Creches:</b> ${stats.creches.size}</div>
                                                    <div style="margin-bottom: 4px;"><b>GPs:</b> ${stats.gps.size}</div>
                                                    <div style="margin-bottom: 8px;"><b>Villages:</b> ${stats.villages.size}</div>
                                                </div>
                                                <button onclick="window.showDetailView('${matchName.replace(/'/g, "\\'")}')" style="width: 100%; background-color: #5979aa; color: white; border: none; padding: 6px; border-radius: 4px; font-size: 12px; cursor: pointer; font-weight: 600;">Detail View</button>
                                                ${drillBtn}
                                            </div>
                                        `);

                                        layer.featureName = matchName;
                                        window.dashboardMapFeatures.push(layer);
                                        bounds.push(layer.getBounds());
                                    } else {
                                        // No data: visible gray boundary, counts for zoom but no tooltip/popup
                                        bounds.push(layer.getBounds());
                                    }
                                }
                            }).addTo(map);

                            if (bounds.length > 0) {
                                let mapBounds = L.latLngBounds(bounds[0].getSouthWest(), bounds[0].getNorthEast());
                                for (let i = 1; i < bounds.length; i++) { mapBounds.extend(bounds[i]); }
                                map.fitBounds(mapBounds, { padding: [20, 20], maxZoom: 14 });
                            } else {
                                plotPoints();
                            }
                        }).catch(e => {
                            console.error("Failed to load boundary GeoJSON", e);
                            plotPoints();
                        });
                    }).catch(e => {
                        console.error("Failed to load geolocation config", e);
                        plotPoints();
                    });
                } else {
                    plotPoints();
                }
            } else {
                console.warn("Leaflet map library is not loaded.");
            }
        }, 500);
    }

    setTimeout(load_data, 500);
}