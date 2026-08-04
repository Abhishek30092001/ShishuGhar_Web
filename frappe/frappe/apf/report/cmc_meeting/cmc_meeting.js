frappe.query_reports["CMC Meeting"] = {
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
			default: new Date().getMonth() + 1 < 10 ? '0' + (new Date().getMonth() + 1) : (new Date().getMonth() + 1).toString(),
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
				let filters = {};
				let gp = frappe.query_report.get_filter_value("gp");
				if (gp) {
					filters["gram_panchayat"] = gp;
				}
				return { filters: filters };
			},
		},
		{
			fieldname: "creche",
			label: __("Creche"),
			fieldtype: "Link",
			options: "Creche",
			get_query: function () {
				let filters = {"creche_status_id": "3"}; // Default to operational
				let gp = frappe.query_report.get_filter_value("gp");
				let supervisor = frappe.query_report.get_filter_value("supervisor_id");
				
				if (gp) {
					filters["gp_id"] = gp;
				}
				if (supervisor) {
					filters["supervisor_id"] = supervisor;
				}
				return { filters: filters };
			},
		},
		{
			"fieldname": "level",
			"label": __("Level"),
			"fieldtype": "Select",
			"options": [
				{ "value": "1", "label": __("Partner") },
				{ "value": "2", "label": __("State") },
				{ "value": "3", "label": __("District") },
				{ "value": "4", "label": __("Block") },
				{ "value": "5", "label": __("Supervisor") },
				{ "value": "6", "label": __("GP") },
				{ "value": "7", "label": __("Creche") },
			],
			"default": "7",
			"onchange": function () {
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
                { "value": "", "label": __("All") },
                { "value": "1", "label": __("Planned") },
                { "value": "2", "label": __("Plan dropped") },
                { "value": "3", "label": __("Active/Operational") },
                { "value": "4", "label": __("Closed") },
            ],
            "default": "3",
            "onchange": function () {
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
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "cr_opening_range_type",
            label: __("Creche Opening Date"),
            fieldtype: "Select",
            options: [
                { value: "", label: __("Select Filter Type") },
                { value: "between", label: __("Between") },
                { value: "before", label: __("Before") },
                { value: "after", label: __("After") },
                { value: "equal", label: __("Equal") }
            ],
            default: "",
            onchange: function () {
                toggleDateFields();
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "c_opening_range",
            label: __("Creche Opening Range"),
            fieldtype: "DateRange",
            depends_on: "eval:doc.cr_opening_range_type == 'between'"
        },
        {
            fieldname: "single_date",
            label: __("Creche Opening Date"),
            fieldtype: "Date",
            depends_on: "eval: doc.cr_opening_range_type && doc.cr_opening_range_type != '' && doc.cr_opening_range_type != 'between'"
        }
	],
    
    onload: function(report) {
        report.page.add_inner_button(__("Download Report"), function () {
            frappe.query_report.export_report("Excel");
        });

        // Initialize toggle function
        window.toggleDateFields = function() {
            const dateRangeType = frappe.query_report.get_filter_value("cr_opening_range_type");
            
            // Hide all date fields first
            frappe.query_report.toggle_filter_display("c_opening_range", dateRangeType === 'between');
            frappe.query_report.toggle_filter_display("single_date", dateRangeType && dateRangeType !== '' && dateRangeType !== 'between');
            
            // Clear values when hidden
            if (dateRangeType !== 'between') {
                frappe.query_report.set_filter_value("c_opening_range", "");
            }
            if (!dateRangeType || dateRangeType === '' || dateRangeType === 'between') {
                frappe.query_report.set_filter_value("single_date", "");
            }
        };
        
        // Initial toggle
        setTimeout(() => {
            toggleDateFields();
        }, 500);
        
        // Add click handler for file popups
        $(document).on('click', '.image-popup-link', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const url = $(this).attr('href');
            const filename = $(this).text().trim() || 'File';
            
            showFilePopup(url, filename);
        });
    },
    
    after_datatable_render: function(report) {
        // Re-attach click handlers after datatable refresh
        setTimeout(() => {
            $('.image-popup-link').off('click').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const url = $(this).attr('href');
                const filename = $(this).text().trim() || 'File';
                
                showFilePopup(url, filename);
            });
        }, 500);
    }
};

// Function to show file in popup
function showFilePopup(url, filename) {
    // Determine file type
    const isPDF = url.toLowerCase().endsWith('.pdf');
    const isImage = url.toLowerCase().match(/\.(jpeg|jpg|gif|png|webp|bmp)$/i);
    
    // Create popup content
    let content = '';
    
    if (isPDF) {
        // For PDF files, use iframe
        content = `
            <div style="width: 100%; height: 70vh;">
                <iframe src="${url}" style="width: 100%; height: 100%; border: none;"></iframe>
            </div>
        `;
    } else if (isImage) {
        // For images, use img tag with max dimensions
        content = `
            <div style="text-align: center; padding: 20px;">
                <img src="${url}" style="max-width: 100%; max-height: 70vh; object-fit: contain;" alt="${filename}">
            </div>
        `;
    } else {
        // For other files, provide download link
        content = `
            <div style="text-align: center; padding: 40px;">
                <p>${__('This file type cannot be previewed.')}</p>
                <a href="${url}" target="_blank" class="btn btn-primary">
                    <i class="fa fa-download"></i> ${__('Download File')}
                </a>
            </div>
        `;
    }
    
    // Create and show the popup dialog
    const dialog = new frappe.ui.Dialog({
        title: __(`View: ${filename}`),
        size: 'large', // 'small', 'large', 'extra-large'
        primary_action_label: __('Close'),
        primary_action: function() {
            dialog.hide();
        }
    });
    
    dialog.$body.html(content);
    dialog.show();
}

// Helper function to refresh report when filters change
function refreshReport() {
    frappe.query_report.refresh();
}