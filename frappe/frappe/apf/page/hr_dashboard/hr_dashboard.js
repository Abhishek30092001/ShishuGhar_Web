frappe.pages['hr-dashboard'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'HR Dashboard',
        single_column: true
    });
    frappe.require("https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js");
    // 1. Added html2canvas dependency for PNG download
    frappe.require("https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js");
    
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
                renderCards();
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
            "onchange": function () {
                renderCards();
            }
        },
        {
            "fieldname": "partner",
            "label": __("Partner"),
            "fieldtype": "Link",
            "options": "Partner",
            "default": frappe.defaults.get_user_default("partner"),
            "onchange": function () {
                renderCards();
            }
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
                renderCards();
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
                renderCards();
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
            },
            "onchange": function () {
                renderCards();
            }
        },
        {
            "fieldname": "is_active",
            "label": __("Is Active"),
            "fieldtype": "Select",
            "options": [
                { "value": "", "label": __("") },
                { "value": "1", "label": __("Is Active") },
                { "value": "2", "label": __("Active & Inactive") }
            ],
            "default": "1",
            "onchange": function () {
                renderCards();
            }

        },
    ];
    filters.forEach(filter => {
        page.add_field(filter);
    });
    function resetForwardFilters(currentFilter) {
        let currentIndex = filters.findIndex(filter => filter.fieldname === currentFilter);
        if (currentIndex === -1) return;
        for (let i = currentIndex + 1; i < filters.length; i++) {
            page.fields_dict[filters[i].fieldname].set_value("");
        }
    }
    filters.forEach(filter => {
        if ((filter.fieldtype === "Link" || filter.fieldtype === "Select") && filter.fieldname != "year" && filter.fieldname != "month") {
            const input = page.fields_dict[filter.fieldname].input;
            if (input) {
                input.addEventListener("change", () => {
                    resetForwardFilters(filter.fieldname);
                    renderCards();
                });
            }
        }
    });

    // Add buttons
    let searchBtn = page.add_button(__("Search"), async () => {
        searchBtn.prop('disabled', true);
        searchBtn.text("Loading...");
        searchBtn.css("opacity", "0.7");
        await renderCards();
        searchBtn.text("Search");
        searchBtn.prop('disabled', false);
        searchBtn.css("opacity", "1");
    });

    let resetBtn = page.add_button(__("Reset"), async () => {
        resetBtn.prop('disabled', true);
        resetBtn.css("opacity", "0.7");
        location.reload();
    });

    searchBtn.css({
        "background-color": "#5979aa",
        "color": "white",
        "border-radius": "4px",
        "padding": "6px 16px",
        "font-weight": "500",
        "border": "none",
        "cursor": "pointer",
        "transition": "all 0.2s ease",
        "font-size": "12px",
        "margin-right": "5px"
    });

    resetBtn.css({
        "background-color": "#f5f5f5",
        "color": "#333",
        "border-radius": "4px",
        "padding": "6px 16px",
        "font-weight": "500",
        "border": "1px solid #ddd",
        "cursor": "pointer",
        "transition": "all 0.2s ease",
        "font-size": "12px"
    });

    $(document).ready(function () {
        if ($(window).width() < 450) {
            $(".page-head.flex").css("padding-bottom", "10px");
        }
    });
    page.wrapper.find('.custom-actions').removeClass('hidden-xs hidden-md').css({
        "display": "flex",
        "gap": "8px"
    });
    page.wrapper.find(".menu-btn-group ").removeClass('show"').css({
        "display": "none"
    });
    page.main.append(`
<style>
/* General Styles */
body {
margin: 0;
font-family: 'Arial', sans-serif;
background-color: #fff;
color: #333;
}
/* Filters Section */
.filters {
display: flex;
flex-wrap: wrap;
gap: 15px;
padding: 30px 20px;
background-color: white;
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
border-radius: 10px;
}
select {
width: 160px;
padding: 8px;
font-size: 1em;
border: 1px solid #ddd;
border-radius: 4px;
background-color: #fff;
color: #333;
}
/* Filter Buttons */
.filter-buttons {
display: flex;
gap: 10px;
}
                .page-form{
                    border-radius:8px;
                }
.modern-btn {
padding: 0px 20px;
font-size: 16px;
border: none;
border-radius: 5px;
cursor: pointer;
transition: all 0.3s ease;
                    min-height: 30px;
}
.reset-btn {
background-color: #5979aa; /* Red */
color: white;
}
.reset-btn:hover {
background-color: #5072A7; /* Darker Red */
}
.search-btn {
background-color: #4CAF50; /* Green */
color: white;
}
.search-btn:hover {
background-color: #388E3C; /* Darker Green */
}
.cards-container {
display: grid;
grid-template-columns: repeat(4, 1fr); /* 4 cards in a row for large screens */
gap: 20px;
margin-top: 20px;
margin-bottom: 20px;
}
@media (max-width: 1024px) {
.cards-container {
grid-template-columns: repeat(4, 1fr); /* 3 cards in a row for medium screens */
}
}
@media (max-width: 768px) {
.cards-container {
grid-template-columns: repeat(1, 1fr); /* 1 card in a row for small screens */
}
}
.card {
background-color: #fff;
padding:5px 20px;
border-radius: 12px;
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
text-align: left;
transition: transform 0.3s ease-in-out, box-shadow 0.3s ease;
}
.card:hover {
transform: translateY(-5px);
box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
.card h3 {
font-size: 1.2em;
color: #333;
margin-bottom: 10px;
}
.card p {
font-size: 2em;
font-weight: bold;
color: #000;
}
.card span {
font-size: 0.9em;
color: #666;
}
.spinner-container {
                margin:auto !important;
                display: none;
                flex-direction: column; /* Add this */
                justify-content: center;
                align-items: center;
                height: 100vh;
                width: 100%;
                }
      
            .percentage-text {
            display:none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 10px;
            font-weight: bold;
            color: #333;
            z-index: 10;
            }
            .loader {
                width: 48px;
                height: 48px;
                border: 5px dotted #FFF;
                border-radius: 50%;
                display: none;
                position: relative;
                box-sizing: border-box;
                animation: rotation 2s linear infinite;
                }
                @keyframes rotation {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
            }
            }
          
@keyframes rotation {
  0% {
transform: rotate(0deg);
  }
  100% {
transform: rotate(360deg);
  }
}
@keyframes rotationBack {
  0% {
transform: rotate(0deg);
  }
  100% {
transform: rotate(-360deg);
  }
}
.filter-desc{
margin-top:20px;
}
            /* Modal Styles */
          #dataModal {
                display: none;
                position: fixed;
                z-index: 9999;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(3px);
            }
            /* Disable background scroll when modal is open */
            body.modal-open {
                overflow: hidden;
            }
            /* Modal Box */
            .modal-content {
                background-color: #fff;
                margin: 5% auto;
                padding: 20px;
                border-radius: 12px;
                width: 90%;
                max-width: 95vw;
                max-height: 95vh;
                overflow: hidden;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                position: relative;
                animation: slideDown 0.3s ease;
            }
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            /* Table Wrapper with Scroll */
            #modalTableContainer {
                max-height: 400px;
                overflow-y: auto;
                margin-top: 20px;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            /* Table Styles */
            #modalTableContainer table {
                width: 100%;
                border-collapse: collapse;
                table-layout: auto;
                border: 1px solid #ccc;
            }
            /* Sticky Table Header */
            #modalTableContainer thead th {
                white-space: nowrap;
                text-align: center;
                width: 1%;
                position: sticky;
                top: 0;
                background-color: #5979aa;
                color: white;
                z-index: 1;
            }
            #modalTableContainer::-webkit-scrollbar {
                width: 3px; /* Thinner scrollbar */
                height: 3px; /* Optional: thin horizontal scrollbar */
            }
            #modalTableContainer::-webkit-scrollbar-thumb {
                background-color: rgba(0, 0, 0, 0.3); /* Scroll thumb color */
                border-radius: 4px;
            }
            #modalTableContainer::-webkit-scrollbar-track {
                background-color: transparent; /* Track stays invisible */
            }
            /* Cell Styles */
            #modalTableContainer th,
            #modalTableContainer td {
                padding: 12px;
                text-align: center;
                border-bottom: 1px solid #eee;
                white-space: nowrap;
                border: 1px solid #ccc;
            }
            /* CSS */
            .close-btn {
            width: 36px;
            height: 36px;
            padding: 0;
            background: rgba(0, 0, 0, 0.05);
            border: none;
            border-radius:5%;
            font-size: 24px;
            color: #333;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background 0.2s, transform 0.2s;
            }
            .close-btn:hover {
            background: #ffe5e9;;
            transform: rotate(90deg);
            }
            .close-btn:active {
            background: rgba(0, 0, 0, 0.15);
            transform: scale(0.9);
            }
            /* Responsive Table Text */
            @media (max-width: 768px) {
                .modal-content {
                    width: 95%;
                    padding: 15px;
                }
                #modalTableContainer th,
                #modalTableContainer td {
                    padding: 10px 6px;
                    font-size: 14px;
                }
            }
            .skeleton-table {
                width: 100%;
                border-collapse: collapse;
            }
            .skeleton-table th,
            .skeleton-table td {
                padding: 8px;
                border: 1px solid #ddd;
            }
            .skeleton-box {
                height: 16px;
                background: linear-gradient(90deg, #e0e0e0 25%, #f5f5f5 50%, #e0e0e0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.2s infinite;
                border-radius: 4px;
            }
            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            /* desktop: hide the "mobile" search, show the header one */
            .search-mobile { display: none; }
            .search-desktop { display: block; }
            @media (max-width: 600px) {
                /* mobile: hide the header search, show the one below */
                .search-desktop { display: none; }
                .search-mobile { display: block; }
            }
@keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
</style>
<!-- Main Content -->
<div style="display: flex; flex-direction: column;">
<!--filter-desc-->
<div class="filter-desc"></div>
<div class="spinner-container" style="margin: auto;">
                    <div class="loader-wrapper">
                        <span class="loader"></span>
                        <div class="percentage-text">0%</div>
                    </div>
                </div>
<!-- Card Section -->
<div class="cards-container"></div>
</div>
           <!-- Modal -->
            <div id="dataModal">
                <div class="modal-content" style="position: relative; padding-top: 30px;">
                    <div id="modalHeaderWrapper" style="
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        align-items: center;
                        margin-bottom: 10px;
                    ">
                        <h2 style="flex: 1; min-width: 200px; margin: 0; font-size : 1.45rem; ">Current active children</h2>
                        <div class="search-desktop" class="" style="position: relative; flex: 1; min-width: 250px;">
                            <input id="modalSearchInput" type="text" placeholder="Search..."
                                style="width: 100%; outline: none; padding: 6px 32px 8px 10px; border: 1px solid #ccc; border-radius: 4px;">
                            <!-- 🔍 Icon -->
                            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888;">🔍</span>
                        </div>
                    <!-- Download Data Button -->
                    <button id="downloadDataBtn" style="padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Download Data
                    </button>
                    <button class="close-btn" aria-label="Close">&times;</button>
                    </div>
                    <div class="search-mobile" style="position: relative; flex: 1; min-width: 250px;">
                            <input type="text" placeholder="Search by Creche or Child Name..."
                                style="width: 100%; padding: 6px 32px 8px 10px; border: 1px solid #ccc; border-radius: 4px;">
                            <!-- 🔍 Icon -->
                            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888;">🔍</span>
                        </div>
                    <div id="modalTableContainer"></div>
                </div>
            </div>
`);

    // ==========================================
    // PNG AND CSV DOWNLOAD IMPLEMENTATION
    // ==========================================
    
    function buildFilterSummaryEl(captureWidth) {
        const monthNames = {
            "1":"January","2":"February","3":"March","4":"April",
            "5":"May","6":"June","7":"July","8":"August",
            "9":"September","10":"October","11":"November","12":"December"
        };
        const activeLabels = {
            "1": "Is Active", "2": "Active & Inactive"
        };

        const fieldDefs = [
            { key: "year",       label: "Year" },
            { key: "month",      label: "Month",    map: monthNames },
            { key: "partner",    label: "Partner",  isLink: true },
            { key: "state",      label: "State",    isLink: true },
            { key: "district",   label: "District", isLink: true },
            { key: "block",      label: "Block",    isLink: true },
            { key: "is_active",  label: "Is Active", map: activeLabels }
        ];

        const chips = [];
        fieldDefs.forEach(({ key, label, map, isLink }) => {
            const field = page.fields_dict[key];
            if (!field) return;

            let val = isLink
                ? (field.$input && field.$input.val ? field.$input.val().trim() : field.get_value())
                : field.get_value();

            if (!val && val !== 0) return;
            if (map && map[val]) val = map[val];
            chips.push(`<span style="
                display:inline-block;
                background:#eef2f8;
                border:1px solid #c8d5e8;
                border-radius:4px;
                padding:3px 10px;
                font-size:12px;
                color:#333;
                margin:3px 4px 3px 0;
            "><b style="color:#5979aa;">${label}:</b> ${val}</span>`);
        });

        const el = document.createElement('div');
        el.style.cssText = `
            width:${captureWidth}px;
            background:#f8fafd;
            border:1px solid #dce6f0;
            border-radius:8px;
            padding:10px 14px;
            margin-bottom:14px;
            box-sizing:border-box;
            font-family:Arial,sans-serif;
        `;
        el.innerHTML = `
            <div style="font-size:13px;font-weight:700;color:#5979aa;margin-bottom:6px;">Applied Filters</div>
            <div>${chips.length ? chips.join('') : '<span style="font-size:12px;color:#888;">No filters applied</span>'}</div>
        `;
        return el;
    }

    async function downloadCardsPNG() {
        return new Promise((resolve) => {
            const container = document.querySelector('.cards-container');
            if (!container) return resolve();

            if (typeof html2canvas === 'undefined') {
                frappe.msgprint("Image generation library is still loading. Please try again in a moment.");
                return resolve();
            }

            const cardsArea    = container.parentElement;
            const captureWidth = Math.max(cardsArea.scrollWidth, 1200);

            const wrapper = document.createElement('div');
            wrapper.style.cssText = [
                'position:absolute',
                'top:0',
                'left:-99999px',
                'background:#fff',
                `width:${captureWidth}px`,
                'padding:16px',
                'box-sizing:border-box',
                'font-family:Arial,sans-serif'
            ].join(';');

            wrapper.appendChild(buildFilterSummaryEl(captureWidth - 32));

            const cardsClone = cardsArea.cloneNode(true);
            wrapper.appendChild(cardsClone);

            document.body.appendChild(wrapper);

            const originalScrollX = window.scrollX;
            const originalScrollY = window.scrollY;
            window.scrollTo(0, 0);

            setTimeout(() => {
                html2canvas(wrapper, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: "#ffffff",
                    logging: false,
                    scrollX: 0,
                    scrollY: 0,
                    width: wrapper.scrollWidth,
                    height: wrapper.scrollHeight,
                    windowWidth: document.documentElement.scrollWidth,
                    windowHeight: document.documentElement.scrollHeight,
                    ignoreElements: (element) => {
                        if (element.id === 'dataModal' || (element.classList && element.classList.contains('spinner-container'))) {
                            return true;
                        }
                        return false;
                    }
                }).then(canvas => {
                    document.body.removeChild(wrapper);
                    window.scrollTo(originalScrollX, originalScrollY);
                    canvas.toBlob(function(blob) {
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement("a");
                        link.href = url;
                        link.download = "hr_dashboard_cards.png";
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        URL.revokeObjectURL(url);
                        resolve();
                    }, 'image/png');
                }).catch(err => {
                    document.body.removeChild(wrapper);
                    window.scrollTo(originalScrollX, originalScrollY);
                    console.error("Error generating PNG", err);
                    if (frappe && frappe.msgprint) {
                        frappe.msgprint("Error generating PNG.");
                    }
                    resolve();
                });
            }, 100);
        });
    }

    async function downloadCardsCSV() {
        return new Promise((resolve) => {
            try {
                const cards = document.querySelectorAll('.card');
                let csvContent = "Card Title,Value,Extra Information\n";
                
                const rows = Array.from(cards).map(card => {
                    // Cleaner extraction utilizing dataset since createCardWithLoader binds it:
                    let title = card.dataset.title || '';
                    const valueElement = card.querySelector('.number-loader');
                    const extraElement = card.querySelector('.extra-line');

                    let value = valueElement ? valueElement.textContent.trim() : '';
                    let extra = extraElement ? extraElement.textContent.trim() : '';

                    title = title.replace(/"/g, '""');
                    value = value.replace(/"/g, '""');
                    extra = extra.replace(/"/g, '""');

                    return `"${title}","${value}","${extra}"`;
                });
                
                csvContent += rows.join('\n');
                
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.setAttribute("href", url);
                link.setAttribute("download", "hr_dashboard_cards.csv");
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                resolve();
            } catch (err) {
                console.error("Error generating CSV", err);
                resolve();
            }
        });
    }

    let downloadDropdown = $(`
        <div class="dropdown custom-dropdown" style="display:inline-block; position: relative;">
            <button class="btn btn-default btn-sm dropdown-toggle" type="button" style="background-color: #5979aa; color: white; border: 1px solid #5979aa; border-radius: 4px; padding: 5px 16px; font-weight: 500; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center;">
                <span>Download</span>
            </button>
            <div class="dropdown-menu" style="display: none; position: absolute; top: 100%; left: 0; background-color: white; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; min-width: 100%; margin-top: 5px; padding: 0;">
                <a href="#" class="dropdown-item" id="dl-png" style="display: block; padding: 8px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee;">PNG</a>
                <a href="#" class="dropdown-item" id="dl-csv" style="display: block; padding: 8px 16px; color: #333; text-decoration: none;">CSV</a>
            </div>
        </div>
    `);
    
    page.wrapper.find('.custom-actions').append(downloadDropdown);

    downloadDropdown.find('.dropdown-item').hover(
        function() { $(this).css('background-color', '#f5f5f5'); },
        function() { $(this).css('background-color', 'white'); }
    );

    downloadDropdown.find('button').on('click', function(e) {
        e.stopPropagation();
        const menu = $(this).siblings('.dropdown-menu');
        $('.dropdown-menu').not(menu).hide();
        menu.toggle();
    });

    $(document).on('click', function() {
        downloadDropdown.find('.dropdown-menu').hide();
    });

    downloadDropdown.find('#dl-png').on('click', function(e) {
        e.preventDefault();
        const btn = downloadDropdown.find('button');
        const btnSpan = btn.find('span');
        const originalText = btnSpan.text();
        btnSpan.text('Downloading...');
        btn.prop('disabled', true);
        
        setTimeout(async () => {
            await downloadCardsPNG();
            btnSpan.text(originalText);
            btn.prop('disabled', false);
        }, 50);
    });

    downloadDropdown.find('#dl-csv').on('click', function(e) {
        e.preventDefault();
        const btn = downloadDropdown.find('button');
        const btnSpan = btn.find('span');
        const originalText = btnSpan.text();
        btnSpan.text('Downloading...');
        btn.prop('disabled', true);
        
        setTimeout(async () => {
            await downloadCardsCSV();
            btnSpan.text(originalText);
            btn.prop('disabled', false);
        }, 50);
    });

    // ==========================================
    // END OF DOWNLOAD IMPLEMENTATION
    // ==========================================

    const titleToIcon = {
        "Operational Creches": "🏠",
        "States": "🗺️",
        "Partners": "🤝",
        "Districts": "📍",
        "Blocks": "🧱",
        "Program Managers": "📋",
        "Cluster Coordinators": "🔗",
        "Logistic Coordinators": "🚛",
        "Capacity and Building Manager": "🏗️",
        "Safety Coordinators": "⛑️",
        "MIS Coordinators": "📊",
        "M&E Managers": "📊",
        "Creche Supervisors": "👩‍💼",
        "Creche Caregivers": "👨‍👩‍👧‍👦"
    };
    const BASE_URL = "https://shishughar.in";
    const cardReferences = {};
    const expectedTitles = [
        "Operational Creches",
        "States",
        "Partners",
        "Districts",
        "Blocks",
        "Program Managers",
        "Cluster Coordinators",
        "Logistic Coordinators",
        "Capacity and Building Manager",
        "Safety Coordinators",
        "MIS Coordinators",
        "M&E Managers",
        "Creche Supervisors",
        "Creche Caregivers"
    ];
    const columnColors = [
        '#E8E8E8',  // Gray
        '#cfe5fc',  // Light blue
        '#ebfced',  // Light green
        '#fce9cf',  // Light orange
        '#fcd9d9'   // Light red
    ];
    function createCardWithLoader(cardId, title, color) {
        const icon = titleToIcon[title] || '📊'; // Default icon if not found
        const card = document.createElement('div');
        card.classList.add('card');
        card.dataset.cardId = cardId;
        card.dataset.title = title;
        card.style.padding = '20px';
        card.style.minHeight = '150px';
        card.style.border = '1px solid #ccc';
        card.style.borderRadius = '8px';
        card.style.backgroundColor = color || '#ffffff';
        card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        card.style.textAlign = 'center';
        card.style.position = 'relative';
        card.innerHTML = `
            <div class="card-content" style="position: relative; z-index: 1;">
                <div class="number-loader" style="font-size: 36px; font-weight: bold; color: #333; min-height: 48px; display: flex; align-items: center; justify-content: center;">
                    <span class="mini-loader" style="width: 24px; height: 24px; border: 2px solid #f3f3f3; border-top: 2px solid #5979aa; border-radius: 50%; animation: spin 1s linear infinite;"></span>
                </div>
                <div style="font-size: 18px; color: #666; margin-top: 10px;">${title} ${icon}</div>
                <div class="extra-line" style="font-size: 10px; color: #000; font-style: italic; font-weight: 600;"></div>
            </div>
            <div class="card-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(211, 211, 211, 0.7); border-radius: 8px; display: none; align-items: center; justify-content: center; z-index: 2; opacity: 0; transition: opacity 0.3s ease;">
                <span class="overlay-loader" style="width: 32px; height: 32px; border: 3px solid #f3f3f3; border-top: 3px solid #5979aa; border-radius: 50%; animation: spin 1s linear infinite;"></span>
            </div>
        `;
        cardReferences[cardId] = card;
        return card;
    }
    // Function to update card with actual data
    function updateCardData(cardId, value) {
        const card = cardReferences[cardId];
        if (!card) return;
        const numberElement = card.querySelector('.number-loader');
        const extraLineElement = card.querySelector('.extra-line');
        numberElement.innerHTML = formatNumber(value);
        numberElement.style.minHeight = 'auto';
        extraLineElement.innerHTML = '';
        const title = card.dataset.title;
        card.style.cursor = "pointer";
        card.onclick = () => handleCardClick(cardId, { title: title, value: value }, card);
    }
    // Function to create all card placeholders
    function createAllCardPlaceholders() {
        const container = document.querySelector('.cards-container');
        container.innerHTML = '';
        expectedTitles.forEach((title, index) => {
            const cardId = title.toLowerCase().replace(/\s+/g, '-');
            const colorIndex = Math.floor(index / 4) % columnColors.length; // Group by 4 cards per color
            const color = columnColors[colorIndex];
            const card = createCardWithLoader(cardId, title, color);
            container.appendChild(card);
        });
    }
    async function fetchDashboardData() {
        const year = page.fields_dict["year"].get_value() || new Date().getFullYear().toString();
        const month = page.fields_dict["month"].get_value() || (new Date().getMonth() + 1).toString();
        const partner = page.fields_dict["partner"].get_value();
        const state = page.fields_dict["state"].get_value();
        const district = page.fields_dict["district"].get_value();
        const block = page.fields_dict["block"].get_value();
        const is_active = page.fields_dict["is_active"].get_value();
        const params = new URLSearchParams({ year, month });
        if (partner) params.append("partner_id", partner);
        if (state) params.append("state_id", state);
        if (district) params.append("district_id", district);
        if (block) params.append("block_id", block);
        if (is_active) params.append("is_active", is_active);
        const url = `${BASE_URL}/api/method/frappe.apf.page.hr_dashboard.hr_dashboard.hr_dashboard?${params}`;
        try {
            createAllCardPlaceholders();
            const res = await fetch(url, {
                credentials: "include",
                headers: { "X-Frappe-CSRF-Token": frappe.csrf_token }
            });
            const result = await res.json();
            console.log("API Response:", result); // Debug log
            if (result.data && result.data.data && Array.isArray(result.data.data)) {
                result.data.data.forEach(item => {
                    const cardId = item.title.toLowerCase().replace(/\s+/g, '-');
                    updateCardData(cardId, item.value);
                });
            }
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    }
    function formatNumber(number) {
        return new Intl.NumberFormat("en-IN").format(number);
    }
    async function handleCardClick(cardId, item, cardElement) {
        const overlay = cardElement.querySelector('.card-overlay');
        // Show the overlay with spinner
        if (overlay) {
            overlay.style.display = 'flex';
            setTimeout(() => {
                overlay.style.opacity = '1';
            }, 10);
        }
        const { title, value } = item;
        const queryType = title.toLowerCase().replace(/&/g, '').replace(/\s+/g, '_');
        const year = page.fields_dict["year"].get_value() || new Date().getFullYear().toString();
        const month = page.fields_dict["month"].get_value() || (new Date().getMonth() + 1).toString();
        const partner = page.fields_dict["partner"].get_value();
        const state = page.fields_dict["state"].get_value();
        const district = page.fields_dict["district"].get_value();
        const block = page.fields_dict["block"].get_value();
        const is_active = page.fields_dict["is_active"].get_value();
        const rawParams = {
            year,
            month,
            query_type: queryType,
            partner_id: partner,
            state_id: state,
            district_id: district,
            block_id: block,
            is_active: is_active
        };
        const params = new URLSearchParams();
        for (const [key, val] of Object.entries(rawParams)) {
            if (val !== null && val !== undefined && val !== "") {
                params.append(key, val);
            }
        }
        const apiUrl = `${BASE_URL}/api/method/frappe.apf.page.hr_dashboard.hr_dashboard_details.hr_dashboard_details?${params.toString()}`;
        try {
            const res = await fetch(apiUrl, {
                credentials: "include",
                headers: { "X-Frappe-CSRF-Token": frappe.csrf_token }
            });
            const result = await res.json();
            console.log("Details API Response:", result); // Debug log
            if (result && result.data && result.data.length > 0) {
                const columns = Object.keys(result.data[0]);
                const rows = result.data.map(entry => columns.map(key => entry[key] || ''));
                openModalWithTable(columns, rows, title);
            } else {
                openModalWithTable(["Message"], [["No records found"]], title);
            }
        } catch (err) {
            console.error("Error fetching card data:", err);
            openModalWithTable(["Error"], [["Error fetching data"]], title);
        } finally {
            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.style.display = 'none';
                }, 300);
            }
        }
    }
    function openModalWithTable(columns, data, title) {
        const modal = document.getElementById("dataModal");
        const container = document.getElementById("modalTableContainer");
        const titleElement = modal.querySelector("h2");
        let searchInput;
        if (window.matchMedia("(max-width: 600px)").matches) {
            searchInput = modal.querySelector('.search-mobile input');
        } else {
            searchInput = document.getElementById("modalSearchInput");
        }
        const closeBtn = modal.querySelector(".close-btn");
        modal.currentData = { columns, data, title };
        titleElement.textContent = title;
        document.body.classList.add("modal-open");
        modal.style.display = "block";
        container.innerHTML = "";
        container.appendChild(createSkeletonTable(columns.length + 1, 10));
        setTimeout(() => {
            container.innerHTML = "";
            const table = document.createElement("table");
            table.className = "data-table";
            const thead = table.createTHead();
            const headerRow = thead.insertRow();
            const serialTh = document.createElement("th");
            serialTh.textContent = "S.No.";
            headerRow.appendChild(serialTh);
            columns.forEach(col => {
                const th = document.createElement("th");
                th.textContent = col;
                headerRow.appendChild(th);
            });
            const tbody = table.createTBody();
            container.appendChild(table);
            // Optimized batch size for better performance
            const batchSize = 100;
            let currentRenderId = 0;
            function renderTableRows(dataset) {
                const renderId = ++currentRenderId;
                tbody.innerHTML = "";
                let rowIndex = 0;

                function renderChunk() {
                    if (renderId !== currentRenderId) return;
                    const end = Math.min(rowIndex + batchSize, dataset.length);
                    const fragment = document.createDocumentFragment();
                    for (; rowIndex < end; rowIndex++) {
                        const tr = document.createElement('tr');

                        // Serial number cell
                        const serialCell = document.createElement('td');
                        serialCell.textContent = rowIndex + 1;
                        tr.appendChild(serialCell);
                        // Data cells
                        dataset[rowIndex].forEach((cell, cellIndex) => {
                            const td = document.createElement('td');
                            td.style.textAlign = "left";

                            td.textContent = cell;

                            tr.appendChild(td);
                        });
                        fragment.appendChild(tr);
                    }
                    tbody.appendChild(fragment);
                    if (rowIndex < dataset.length) {
                        requestAnimationFrame(renderChunk);
                    }
                }
                renderChunk();
            }
            let filteredData = [...data];
            renderTableRows(filteredData);
            let searchTimeout;

            // Remove existing event listener and add new one to avoid duplicates
            const newSearchInput = searchInput.cloneNode(true);
            if (searchInput.parentNode) {
                searchInput.parentNode.replaceChild(newSearchInput, searchInput);
            }

            newSearchInput.addEventListener("input", function () {
                clearTimeout(searchTimeout);
                const q = this.value.toLowerCase();

                searchTimeout = setTimeout(() => {
                    if (q === '') {
                        filteredData = [...data];
                    } else {
                        filteredData = data.filter(row =>
                            row.some(cell =>
                                typeof cell === "string" && cell.toLowerCase().includes(q)
                            )
                        );
                    }
                    renderTableRows(filteredData);
                }, 150); // Debounce by 150ms
            });

        }, 300);
    }
    function createSkeletonTable(colCount, rowCount) {
        const table = document.createElement("table");
        table.className = "skeleton-table";
        const thead = table.createTHead();
        const headerRow = thead.insertRow();
        for (let i = 0; i < colCount; i++) {
            const th = document.createElement("th");
            th.innerHTML = `<div class="skeleton-box"></div>`;
            headerRow.appendChild(th);
        }
        const tbody = table.createTBody();
        for (let i = 0; i < rowCount; i++) {
            const tr = tbody.insertRow();
            for (let j = 0; j < colCount; j++) {
                const td = tr.insertCell();
                td.innerHTML = `<div class="skeleton-box"></div>`;
            }
        }
        return table;
    }
    function closeModal() {
        document.querySelectorAll('input[placeholder="Search by Creche or Child Name..."]').forEach(input => input.value = "");
        document.getElementById("dataModal").style.display = "none";
        document.body.classList.remove("modal-open");
    }
    document.querySelector(".close-btn").addEventListener("click", closeModal);
    window.addEventListener("click", (event) => {
        if (event.target === document.getElementById("dataModal")) {
            closeModal();
        }
    });
    document.addEventListener("click", function (e) {
        if (e.target && e.target.id === "downloadDataBtn") {
            const modal = document.getElementById("dataModal");
            if (modal.currentData) {
                const { columns, data, title } = modal.currentData;
                exportToExcel(["S.No.", ...columns], data.map((row, index) => [index + 1, ...row]), title);
            } else {
                alert("No data available to download");
            }
        }
    });
    function exportToExcel(columns, data, title) {
        const wb = XLSX.utils.book_new();
        const excelData = [columns, ...data];
        const ws = XLSX.utils.aoa_to_sheet(excelData);
        XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
        XLSX.writeFile(wb, `${title.replace(/ /g, '_')}.xlsx`);
    }
    async function renderCards() {
        await fetchDashboardData();
    }
    // Add CSS for mini loader animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    frappe.after_ajax(() => {
        renderCards();
    });
};








