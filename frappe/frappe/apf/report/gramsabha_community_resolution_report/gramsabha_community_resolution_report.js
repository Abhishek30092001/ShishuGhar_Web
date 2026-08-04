// Copyright (c) 2026, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Gramsabha-Community resolution Report"] = {
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
    
    onload: function(report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        $(document).off('click', '.image-popup-link').on('click', '.image-popup-link', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const url = $(this).attr('href');
            const filename = $(this).text();

            showFilePopup(url, filename);
        });
    },
    
    after_datatable_render: function(datatable) {
        setTimeout(() => {
            $('.image-popup-link').off('click').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const url = $(this).attr('href');
                const filename = $(this).text();
                
                showFilePopup(url, filename);
            });

            // Handle the creche list popup display
            $('.show-creche-list').off('click').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const $el = $(this);
                const type = $el.attr('data-type');
                
                // Fetch the base report filters
                let filter_values = Object.assign({}, frappe.query_report.get_values());
                
                // Append exact mapped entity filters based on the clicked link's row
                const attrs = ['partner', 'state', 'district', 'block', 'gp', 'supervisor'];
                attrs.forEach(attr => {
                    let val = $el.attr('data-' + attr);
                    if (val && val !== 'None' && val !== 'undefined' && val !== '') {
                        if (attr === 'supervisor') {
                            filter_values['supervisor_id'] = val;
                        } else {
                            filter_values[attr] = val;
                        }
                    }
                });
                
                // Force report to run at Level 7 to retrieve granular creche data
                filter_values.level = "7";
                
                frappe.call({
                    method: "frappe.desk.query_report.run",
                    args: {
                        report_name: "Gram Sabha Resolution Report",
                        filters: filter_values
                    },
                    callback: function(r) {
                        if (r.message && r.message.result) {
                            let creches = r.message.result;
                            
                            // Filter specifically by 'with_att' / 'without_att'
                            let filtered_creches = creches.filter(c => {
                                if (c.creche && c.creche.includes('<b>Total</b>')) return false;
                                let has_att = c.image_links && c.image_links.trim() !== '';
                                return type === 'with_att' ? has_att : !has_att;
                            });
                            
                            showCrecheListPopup(filtered_creches, type);
                        }
                    }
                });
            });
        }, 500);
    }
};

function showCrecheListPopup(data, type) {
    let title = type === 'with_att' ? __('Creches Submitted') : __('Creches Not Submitted');
    
    let html = `
        <div class="form-group mb-3" style="display: flex; gap: 10px;">
            <input type="text" id="creche-search-input" class="form-control" placeholder="${__('Search Creches...')}">
            <button id="download-creche-excel" class="btn btn-default" style="min-width: 150px;">
                <i class="fa fa-download"></i> ${__('Download Excel')}
            </button>
        </div>
        <div style="max-height: 50vh; overflow-y: auto;">
            <table class="table table-bordered table-hover" id="creche-list-table">
                <thead>
                    <tr>
                        <th>${__('Sr. No.')}</th>
                        <th>${__('Partner')}</th>
                        <th>${__('State')}</th>
                        <th>${__('District')}</th>
                        <th>${__('Block')}</th>
                        <th>${__('Gram Panchayat')}</th>
                        <th>${__('Creche Name')}</th>
                        <th>${__('Creche ID')}</th>
                        <th>${__('Creche Opening Date')}</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    let sr_no = 1;
    data.forEach(row => {
        let stripHtml = (str) => {
            if (!str) return "";
            let tmp = document.createElement("DIV");
            tmp.innerHTML = str;
            return tmp.textContent || tmp.innerText || "";
        };
        
        html += `
            <tr>
                <td>${sr_no++}</td>
                <td>${stripHtml(row.partner_display)}</td>
                <td>${stripHtml(row.state)}</td>
                <td>${stripHtml(row.district)}</td>
                <td>${stripHtml(row.block)}</td>
                <td>${stripHtml(row.gp)}</td>
                <td>${stripHtml(row.creche)}</td>
                <td>${stripHtml(row.creche_id)}</td>
                <td>${stripHtml(row.cr_open_date)}</td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    const dialog = new frappe.ui.Dialog({
        title: title,
        size: 'extra-large',
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'creche_list_html',
                options: html
            }
        ],
        primary_action_label: __('Close'),
        primary_action: function() {
            dialog.hide();
        }
    });
    
    dialog.show();

    // Set custom width for the dialog wrapper to make it wider
    dialog.$wrapper.find('.modal-dialog').css({
        'max-width': '90vw',
        'width': '90vw'
    });
    
    // Fixed Search Functionality
    dialog.$wrapper.find('#creche-search-input').on('input', function() {
        let value = $(this).val().toLowerCase();
        dialog.$wrapper.find('#creche-list-table tbody tr').each(function() {
            let rowText = $(this).text().toLowerCase();
            $(this).toggle(rowText.indexOf(value) > -1);
        });
    });

    // Excel Download Functionality
    dialog.$wrapper.find('#download-creche-excel').on('click', function() {
        let csvData = [];
        let headers = [];
        
        dialog.$wrapper.find('#creche-list-table thead th').each(function() {
            headers.push('"' + $(this).text().replace(/"/g, '""') + '"');
        });
        csvData.push(headers.join(","));

        dialog.$wrapper.find('#creche-list-table tbody tr:visible').each(function() {
            let row = [];
            $(this).find('td').each(function() {
                row.push('"' + $(this).text().replace(/"/g, '""') + '"');
            });
            csvData.push(row.join(","));
        });

        let csvString = csvData.join("\n");
        let blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        let url = URL.createObjectURL(blob);
        let link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", title.replace(/[^a-zA-Z0-9]/g, '_') + ".csv");
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
}

function showFilePopup(url, filename) {
    if (window.currentFileDialog) {
        window.currentFileDialog.hide();
    }
    
    const isPDF = url.toLowerCase().endsWith('.pdf');
    const isImage = url.match(/\.(jpeg|jpg|gif|png|webp|bmp)$/i);
    
    let content = '';
    
    if (isPDF) {
        content = `
            <div style="width: 100%; height: 80vh;">
                <iframe src="${url}" style="width: 100%; height: 100%; border: none;"></iframe>
            </div>
        `;
    } else if (isImage) {
        content = `
            <div style="text-align: center; padding: 20px;">
                <img src="${url}" style="max-width: 100%; max-height: 70vh; object-fit: contain;" alt="${filename}">
            </div>
        `;
    } else {
        content = `
            <div style="text-align: center; padding: 40px;">
                <p>${__('This file type cannot be previewed.')}</p>
                <a href="${url}" target="_blank" class="btn btn-primary">
                    <i class="fa fa-download"></i> ${__('Download File')}
                </a>
            </div>
        `;
    }
    
    const dialog = new frappe.ui.Dialog({
        title: __(`View: ${filename}`),
        size: 'extra-large',
        primary_action_label: __('Close'),
        primary_action: function() {
            dialog.hide();
            window.currentFileDialog = null;
        }
    });
    
    window.currentFileDialog = dialog;
    
    dialog.$body.html(content);
    dialog.show();
    
    dialog.$wrapper.find('.modal-header').css({
        'position': 'relative',
        'padding': '15px 45px 15px 15px', 
        'min-height': '50px'
    });
    
    dialog.$wrapper.find('.modal-header .close').off('click').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dialog.hide();
        window.currentFileDialog = null;
    });
    
    dialog.$wrapper.find('.modal-header .btn-modal-close').off('click').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dialog.hide();
        window.currentFileDialog = null;
    });
    
    dialog.$wrapper.on('hide.bs.modal', function() {
        window.currentFileDialog = null;
    });
}
