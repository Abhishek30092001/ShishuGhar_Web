frappe.pages["report-card"].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Report Card',
        single_column: true
    });


    frappe.require("https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js");
    frappe.require("https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js");
    frappe.require("https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js");

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
            "fieldname": "partner",
            "label": __("Partner"),
            "fieldtype": "Link",
            "options": "Partner",
            "default": frappe.defaults.get_user_default("partner"),
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
                let state = page.fields_dict["state"].get_value();
                let filters = { "is_active": 1 };
                if (state) {
                    filters["state_id"] = state;
                }
                return { filters };
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
            "fieldname": "gp",
            "label": __("Gram Panchayat"),
            "fieldtype": "Link",
            "options": "Gram Panchayat",
            "get_query": function () {
                let block = page.fields_dict["block"].get_value();
                if (block) {
                    return {
                        filters: {
                            block_id: block
                        }
                    };
                }
                return {};
            }
        },
        {
            "fieldname": "supervisor_id",
            "label": __("Supervisor"),
            "fieldtype": "Link",
            "options": "User",
            "get_query": function () {
                let creche = page.fields_dict["creche"].get_value();
                return creche ? { filters: { creche: creche } } : {};
            },
        },
        {
            "fieldname": "creche",
            "label": __("Creche"),
            "fieldtype": "Link",
            "options": "Creche",
            "get_query": function () {
                let gp = page.fields_dict["gp"].get_value();
                if (gp) {
                    return {
                        filters: {
                            gp_id: gp
                        }
                    };
                }
                return {};
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
        }
    ];

    filters.forEach(filter => {
        page.add_field(filter);
    });

    let cr_opening_range_type = page.add_field({
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
        default: ""
    });

    let c_opening_range = page.add_field({
        fieldname: "c_opening_range",
        label: __("Creche Opening Range"),
        fieldtype: "DateRange",
        hidden: 1
    });

    let single_date = page.add_field({
        fieldname: "single_date",
        label: __("Creche Opening Date"),
        fieldtype: "Date",
        hidden: 1
    });

    cr_opening_range_type.$input.on("change", function () {
        let selected_value = cr_opening_range_type.get_value();
        c_opening_range.toggle(selected_value === "between");
        single_date.toggle(["before", "after", "equal"].includes(selected_value));

        if (selected_value === "between") {
            single_date.set_value(null);
        } else if (["before", "after", "equal"].includes(selected_value)) {
            c_opening_range.set_value(null);
        }
    });

    function resetForwardFilters(currentFilter) {
        let currentIndex = filters.findIndex(filter => filter.fieldname === currentFilter);
        if (currentIndex === -1) return;

        for (let i = currentIndex + 1; i < filters.length; i++) {
            if (page.fields_dict[filters[i].fieldname].df.fieldname == "creche_status_id" || page.fields_dict[filters[i].fieldname].df.fieldname == "phases")
                continue;
            page.fields_dict[filters[i].fieldname].set_value("");
        }
    }

    filters.forEach(filter => {
        if ((filter.fieldtype === "Link" || filter.fieldtype === "Select") && filter.fieldname != "year" && filter.fieldname != "month") {
            const input = page.fields_dict[filter.fieldname].input;
            if (input) {
                input.addEventListener("change", () => {
                    resetForwardFilters(filter.fieldname);
                });
            }
        }
    });

    let toolbarLoader = $(`
        <div id="rcToolbarLoader" style="display:none; align-items:center; gap:8px; margin-right:10px; font-size:13px; color:#5979aa; font-weight:600; white-space:nowrap;">
            <span id="rcToolbarLoaderSpinner" style="width:14px; height:14px; border:2px solid #dce6f5; border-top:2px solid #5979aa; border-radius:50%; display:inline-block; animation:rcToolbarSpin 0.8s linear infinite;"></span>
            <span id="rcToolbarLoaderText">Loading... (0/0)</span>
            <span id="rcToolbarLoaderTimer" style="color:#7a879c; font-weight:500;">(0s)</span>
        </div>
    `);
    page.wrapper.find('.custom-actions').prepend(toolbarLoader);

    let searchBtn = page.add_button(`Search`, async () => {
        searchBtn.text('Searching....');
        searchBtn.prop('disabled', true);
        await renderCards();
        searchBtn.text('Search');
        searchBtn.prop('disabled', false);
    });

    let resetBtn = page.add_button(`Reset`, async () => {
        resetBtn.prop('disabled', true);
        location.reload();
    });

    searchBtn.addClass('rc-search-btn').css({
        "background-color": "#5979aa",
        "color": "white",
        "border": "1px solid #5979aa",
        "border-radius": "4px",
        "padding": "5px 16px",
        "font-weight": "500",
        "font-size": "14px"
    });
    resetBtn.addClass('rc-reset-btn').css({
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
            <div class="dropdown-menu" style="display: none; position: absolute; top: 100%; left: 0; background-color: white; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 1000; min-width: 100%; margin-top: 5px; padding: 0;">
                <a href="#" class="dropdown-item" id="dl-png" style="display: block; padding: 8px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee;">PNG</a>
                <a href="#" class="dropdown-item" id="dl-xlsx" style="display: block; padding: 8px 16px; color: #333; text-decoration: none; border-bottom: 1px solid #eee;">XLSX</a>
                <a href="#" class="dropdown-item" id="dl-pdf" style="display: block; padding: 8px 16px; color: #333; text-decoration: none;">PDF</a>
            </div>
        </div>
    `);

    page.wrapper.find('.custom-actions').append(downloadDropdown);

    // Add Logic Button next to Download Button
    let logicBtn = $(`
        <button class="btn btn-default btn-sm logic-btn" type="button" style="background-color: #5979aa; color: white; border: 1px solid #5979aa; border-radius: 4px; padding: 5px 16px; font-weight: 500; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; margin-left: 5px;">
            <span>Logic</span>
        </button>
    `);

    page.wrapper.find('.custom-actions').append(logicBtn);

    // Mobile three-dot (kebab) menu — shown only on screens ≤600px
    let mobileKebab = $(`
        <div id="mobile-kebab" style="display:none; position:relative;">
            <button id="mob-kebab-btn" type="button" style="
                background:#5979aa; color:white; border:1px solid #5979aa;
                border-radius:4px; padding:4px 10px; font-size:20px; line-height:1;
                cursor:pointer; display:inline-flex; align-items:center; justify-content:center;">
                &#8942;
            </button>
            <div id="mob-kebab-dropdown" style="
                display:none; position:absolute; right:0; top:calc(100% + 4px);
                background:white; border:1px solid #ddd; border-radius:6px;
                box-shadow:0 4px 12px rgba(0,0,0,0.12); z-index:9999; min-width:160px; padding:4px 0;">
                <a href="#" id="mob-search-btn" style="display:block;padding:9px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">Search</a>
                <a href="#" id="mob-reset-btn"  style="display:block;padding:9px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">Reset</a>
                <a href="#" id="mob-dl-png-btn" style="display:block;padding:9px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">Download PNG</a>
                <a href="#" id="mob-dl-xlsx-btn" style="display:block;padding:9px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">Download XLSX</a>
                <a href="#" id="mob-dl-pdf-btn" style="display:block;padding:9px 16px;color:#333;text-decoration:none;border-bottom:1px solid #eee;">Download PDF</a>
                <a href="#" id="mob-logic-btn" style="display:block;padding:9px 16px;color:#333;text-decoration:none;">Logic</a>
            </div>
        </div>
    `);
    page.wrapper.find('.custom-actions').append(mobileKebab);

    mobileKebab.find('#mob-kebab-btn').on('click', function (e) {
        e.stopPropagation();
        mobileKebab.find('#mob-kebab-dropdown').toggle();
    });
    $(document).on('click.mob-kebab', function () {
        mobileKebab.find('#mob-kebab-dropdown').hide();
    });
    mobileKebab.find('#mob-search-btn').on('click', async function (e) {
        e.preventDefault();
        mobileKebab.find('#mob-kebab-dropdown').hide();
        const $a = $(this);
        $a.text('Searching...');
        await renderCards();
        $a.text('Search');
    });
    mobileKebab.find('#mob-reset-btn').on('click', function (e) {
        e.preventDefault();
        location.reload();
    });
    mobileKebab.find('#mob-dl-png-btn').on('click', async function (e) {
        e.preventDefault();
        mobileKebab.find('#mob-kebab-dropdown').hide();
        const $a = $(this);
        $a.text('Downloading...');
        await downloadCardsPNG();
        $a.text('Download PNG');
    });
    mobileKebab.find('#mob-dl-xlsx-btn').on('click', async function (e) {
        e.preventDefault();
        mobileKebab.find('#mob-kebab-dropdown').hide();
        const $a = $(this);
        $a.text('Downloading...');
        await downloadCardsXLSX();
        $a.text('Download XLSX');
    });
    mobileKebab.find('#mob-dl-pdf-btn').on('click', async function (e) {
        e.preventDefault();
        mobileKebab.find('#mob-kebab-dropdown').hide();
        const $a = $(this);
        $a.text('Downloading...');
        await downloadCardsPDF();
        $a.text('Download PDF');
    });
    mobileKebab.find('#mob-logic-btn').on('click', function (e) {
        e.preventDefault();
        mobileKebab.find('#mob-kebab-dropdown').hide();
        openLogicModal();
    });
    // Hover highlight for mobile menu items
    mobileKebab.find('a').hover(
        function () { $(this).css('background-color', '#f5f5f5'); },
        function () { $(this).css('background-color', 'white'); }
    );

    downloadDropdown.find('.dropdown-item').hover(
        function () { $(this).css('background-color', '#f5f5f5'); },
        function () { $(this).css('background-color', 'white'); }
    );

    downloadDropdown.find('button').on('click', function (e) {
        e.stopPropagation();
        const menu = $(this).siblings('.dropdown-menu');
        $('.dropdown-menu').not(menu).hide();
        menu.toggle();
    });

    $(document).on('click', function () {
        downloadDropdown.find('.dropdown-menu').hide();
    });

    function buildFilterSummaryEl(captureWidth) {
        const monthNames = {
            "1": "January", "2": "February", "3": "March", "4": "April",
            "5": "May", "6": "June", "7": "July", "8": "August",
            "9": "September", "10": "October", "11": "November", "12": "December"
        };
        const statusLabels = {
            "1": "Planned", "2": "Plan dropped", "3": "Active/Operational", "4": "Closed"
        };

        const fieldDefs = [
            { key: "year", label: "Year" },
            { key: "month", label: "Month", map: monthNames },
            { key: "partner", label: "Partner", isLink: true },
            { key: "state", label: "State", isLink: true },
            { key: "district", label: "District", isLink: true },
            { key: "block", label: "Block", isLink: true },
            { key: "gp", label: "Gram Panchayat", isLink: true },
            { key: "supervisor_id", label: "Supervisor", isLink: true },
            { key: "creche", label: "Creche", isLink: true },
            { key: "phases", label: "Phase" },
            { key: "creche_status_id", label: "Creche Status", map: statusLabels },
        ];

        const chips = [];
        fieldDefs.forEach(({ key, label, map, isLink }) => {
            const field = page.fields_dict[key];
            if (!field) return;

            // For Link fields use the displayed input text (human-readable name).
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

        // Date range filter
        const rangeType = page.fields_dict["cr_opening_range_type"] && page.fields_dict["cr_opening_range_type"].get_value();
        if (rangeType) {
            const singleDate = page.fields_dict["single_date"] && page.fields_dict["single_date"].get_value();
            const dateRange = page.fields_dict["c_opening_range"] && page.fields_dict["c_opening_range"].get_value();
            let dateVal = "";
            if (rangeType === "between" && dateRange && dateRange.length === 2)
                dateVal = `${dateRange[0]} to ${dateRange[1]}`;
            else if (singleDate)
                dateVal = `${rangeType} ${singleDate}`;
            if (dateVal)
                chips.push(`<span style="
                    display:inline-block;
                    background:#eef2f8;
                    border:1px solid #c8d5e8;
                    border-radius:4px;
                    padding:3px 10px;
                    font-size:12px;
                    color:#333;
                    margin:3px 4px 3px 0;
                "><b style="color:#5979aa;">Opening Date:</b> ${dateVal}</span>`);
        }

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

            const cardsArea = container.parentElement;
            const captureWidth = Math.max(cardsArea.scrollWidth, 1200);

            // Off-screen wrapper: filter summary on top, cards below
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
                        if (element.id === 'dataModal' || element.id === 'logicModal' || (element.classList && element.classList.contains('spinner-container'))) {
                            return true;
                        }
                        return false;
                    }
                }).then(canvas => {
                    document.body.removeChild(wrapper);
                    window.scrollTo(originalScrollX, originalScrollY);
                    canvas.toBlob(function (blob) {
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement("a");
                        link.href = url;
                        link.download = "report_cards.png";
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

    async function downloadCardsXLSX() {
        return new Promise((resolve) => {
            try {
                const cards = document.querySelectorAll('.card');
                const rows = Array.from(cards).map(card => {
                    const titleElement = card.querySelector('div:nth-child(2)');
                    const valueElement = card.querySelector('.number-loader');
                    const extraElement = card.querySelector('.extra-line');

                    let title = titleElement ? titleElement.textContent.trim() : '';
                    let value = valueElement ? valueElement.textContent.trim() : '';
                    let extra = extraElement ? extraElement.textContent.trim() : '';

                    return { "Card Title": title, "Value": value, "Extra Information": extra };
                });

                if (rows.length > 0) {
                    const worksheet = XLSX.utils.json_to_sheet(rows);
                    const workbook = XLSX.utils.book_new();
                    XLSX.utils.book_append_sheet(workbook, worksheet, "Creche Report Cards");
                    XLSX.writeFile(workbook, "creche_report_cards.xlsx");
                }
                resolve();
            } catch (err) {
                console.error("Error generating XLSX", err);
                resolve();
            }
        });
    }

    async function downloadCardsPDF() {
        return new Promise((resolve) => {
            const container = document.querySelector('.cards-container');
            if (!container) return resolve();

            if (typeof html2canvas === 'undefined') {
                frappe.msgprint("Image generation library is still loading. Please try again in a moment.");
                return resolve();
            }

            if (typeof window.jspdf === 'undefined' && typeof jsPDF === 'undefined') {
                frappe.msgprint("PDF generation library is still loading. Please try again in a moment.");
                return resolve();
            }

            const cardsArea = container.parentElement;
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
                        if (element.id === 'dataModal' || element.id === 'logicModal' || (element.classList && element.classList.contains('spinner-container'))) {
                            return true;
                        }
                        return false;
                    }
                }).then(canvas => {
                    document.body.removeChild(wrapper);
                    window.scrollTo(originalScrollX, originalScrollY);

                    const imgData = canvas.toDataURL('image/png');
                    const imgWidth = canvas.width;
                    const imgHeight = canvas.height;

                    // A4 landscape if wide, portrait if tall
                    const { jsPDF: JSPDF } = window.jspdf || {};
                    const JsPDF = JSPDF || window.jsPDF;

                    const pdfW = 297; // A4 landscape width in mm
                    const pdfH = 210; // A4 landscape height in mm
                    const ratio = imgWidth / imgHeight;
                    const pdfImgW = pdfW;
                    const pdfImgH = pdfW / ratio;

                    const orientation = pdfImgH <= pdfH ? 'landscape' : 'portrait';
                    const doc = new JsPDF({ orientation, unit: 'mm', format: 'a4' });

                    const pageW = doc.internal.pageSize.getWidth();
                    const pageH = doc.internal.pageSize.getHeight();

                    const scaledW = pageW;
                    const scaledH = pageW / ratio;

                    let yOffset = 0;
                    let remaining = scaledH;

                    while (remaining > 0) {
                        const sliceH = Math.min(remaining, pageH);
                        const srcY = yOffset * (imgHeight / scaledH);
                        const srcH = sliceH * (imgHeight / scaledH);

                        const sliceCanvas = document.createElement('canvas');
                        sliceCanvas.width = imgWidth;
                        sliceCanvas.height = srcH;
                        const ctx = sliceCanvas.getContext('2d');
                        ctx.drawImage(canvas, 0, srcY, imgWidth, srcH, 0, 0, imgWidth, srcH);

                        const sliceData = sliceCanvas.toDataURL('image/png');
                        if (yOffset > 0) doc.addPage();
                        doc.addImage(sliceData, 'PNG', 0, 0, scaledW, sliceH);

                        yOffset += sliceH;
                        remaining -= sliceH;
                    }

                    doc.save('report_cards.pdf');
                    resolve();
                }).catch(err => {
                    document.body.removeChild(wrapper);
                    window.scrollTo(originalScrollX, originalScrollY);
                    console.error("Error generating PDF", err);
                    if (frappe && frappe.msgprint) {
                        frappe.msgprint("Error generating PDF.");
                    }
                    resolve();
                });
            }, 100);
        });
    }

    downloadDropdown.find('#dl-png').on('click', function (e) {
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

    downloadDropdown.find('#dl-xlsx').on('click', function (e) {
        e.preventDefault();
        const btn = downloadDropdown.find('button');
        const btnSpan = btn.find('span');
        const originalText = btnSpan.text();
        btnSpan.text('Downloading...');
        btn.prop('disabled', true);

        setTimeout(async () => {
            await downloadCardsXLSX();
            btnSpan.text(originalText);
            btn.prop('disabled', false);
        }, 50);
    });

    downloadDropdown.find('#dl-pdf').on('click', function (e) {
        e.preventDefault();
        const btn = downloadDropdown.find('button');
        const btnSpan = btn.find('span');
        const originalText = btnSpan.text();
        btnSpan.text('Downloading...');
        btn.prop('disabled', true);

        setTimeout(async () => {
            await downloadCardsPDF();
            btnSpan.text(originalText);
            btn.prop('disabled', false);
        }, 50);
    });

    $(document).ready(function () {
        // Responsive header — kebab on mobile, desktop buttons otherwise
        function applyResponsiveHeader() {
            if ($(window).width() <= 600) {
                mobileKebab.show();
                searchBtn.hide();
                resetBtn.hide();
                downloadDropdown.hide();
                logicBtn.hide();
            } else {
                mobileKebab.hide();
                searchBtn.show();
                resetBtn.show();
                downloadDropdown.show();
                logicBtn.show();
            }
        }
        applyResponsiveHeader();
        $(window).on('resize.rc-header', applyResponsiveHeader);
    });

    page.wrapper.find('.custom-actions').removeClass('hidden-xs hidden-md').css({
        "display": "flex",
        "flex-wrap": "nowrap",
        "align-items": "center",
        "gap": "5px"
    });
    page.wrapper.find(".menu-btn-group ").removeClass('show"').css({
        "display": "none"
    });

    page.main.append(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Creche Report</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
                    margin-bottom: 10px !important;
                    padding-bottom: 2px !important;
                    padding-top: 2px !important;
                }
                .page-body {
                    margin-top: 6px !important;
                }
                #page-report-card > div.page-head.flex {
                    padding-top: 0 !important;
                    padding-bottom: 0 !important;
                    margin-bottom: 0 !important;
                    min-height: unset !important;
                    height: auto !important;
                    border-bottom: none !important;
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
                margin-top: 4px;
                margin-bottom: 20px;
            }
        
            @media (max-width: 1024px) {
                .cards-container {
                    grid-template-columns: repeat(4, 1fr); /* 4 cards in a row for medium screens */
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
            .total-creche-card{
               display: grid;
                grid-template-columns: repeat(4, 1fr);
                margin-top: 4px;
                gap: 20px;
            }
             @media (max-width: 768px) {
                .total-creche-card {
                    grid-template-columns: repeat(1, 1fr);
                }
            }
            .filter-desc{
            margin-top:5px;
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
                width: 3px;             /* Thinner scrollbar */
                height: 3px;            /* Optional: thin horizontal scrollbar */
            }

            #modalTableContainer::-webkit-scrollbar-thumb {
                background-color: rgba(0, 0, 0, 0.3);  /* Scroll thumb color */
                border-radius: 4px;
            }

            #modalTableContainer::-webkit-scrollbar-track {
                background-color: transparent;        /* Track stays invisible */
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
            

            </style>
        </head>
        <body>
            <div style="display: flex; flex-direction: column;">
                <div class="filter-desc"></div>
                <div class="total-creche-card"></div>
        
                <div class="cards-container"></div>
        
            </div>
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

                        <div class="search-desktop" style="position: relative; flex: 1; min-width: 250px;">
                            <input class="modal-search-input" type="text" placeholder="Search by Creche or Child Name..." 
                                style="width: 100%; outline: none; padding: 6px 32px 8px 10px; border: 1px solid #ccc; border-radius: 4px;">
                            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888;">🔍</span>
                        </div>

                    <button id="attendanceTrendBtn" style="display: none; padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Attendance Trend
                    </button>

                    <button id="downloadDataBtn" style="padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        Download Data
                    </button>

                    <button class="close-btn" aria-label="Close">&times;</button>
                    </div>
                    <div class="search-mobile" style="position: relative; flex: 1; min-width: 250px; margin-bottom: 10px;">
                            <input class="modal-search-input" type="text" placeholder="Search by Creche or Child Name..." 
                                style="width: 100%; padding: 6px 32px 8px 10px; border: 1px solid #ccc; border-radius: 4px;">
                            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #888;">🔍</span>
                        </div>
                    <div id="modalTableContainer"></div>
                </div>
            </div>

            <div id="logicModal" style="display: none; position: fixed; z-index: 10000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0, 0, 0, 0.5); backdrop-filter: blur(3px);">
                <div id="logicModalContent" class="modal-content" style="background-color: #fff; margin: 5% auto; padding: 20px; border-radius: 12px; width: 90%; max-width: 1200px; max-height: 90vh; overflow: hidden; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2); position: relative; display: flex; flex-direction: column; animation: slideDown 0.3s ease;">
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 15px;">
                        <h2 style="flex: 1; margin: 0; font-size: 1.45rem; color: #5979aa;">Card Logic</h2>
                        <button id="downloadLogicXlsxBtn" style="padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">Download XLSX</button>
                        <button id="downloadLogicPngBtn" style="padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">Download PNG</button>
                        <button id="downloadLogicPdfBtn" style="padding: 6px 12px; background-color: #5979aa; color: white; border: none; border-radius: 4px; cursor: pointer;">Download PDF</button>
                        <button class="logic-close-btn" aria-label="Close" style="width: 36px; height: 36px; background: rgba(0,0,0,0.05); border: none; border-radius: 5px; font-size: 24px; cursor: pointer; display: flex; align-items: center; justify-content: center;">&times;</button>
                    </div>
                    
                    <div id="logicTableWrapper" style="overflow-y: auto; max-height: 70vh; border-radius: 8px; border: 1px solid #ddd; background: white; padding: 10px;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px; text-align: left;">
                            <thead style="position: sticky; top: -10px; background-color: #5979aa; color: white; z-index: 1;">
                                <tr>
                                    <th style="padding: 12px; border: 1px solid #ccc; width: 30%;">Card Title</th>
                                    <th style="padding: 12px; border: 1px solid #ccc; width: 70%;">Logic</th>
                                </tr>
                            </thead>
                            <tbody id="logicTableBody">
                                </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </body>
        </html>
        `);

    const BASE_URL = "https://shishughar.in/";
    const cardReferences = {};

    function createCardWithLoader(cardId, title) {
        const card = document.createElement('div');
        card.classList.add('card');
        card.dataset.cardId = cardId;
        card.style.padding = '20px';
        card.style.minHeight = '150px';
        card.style.border = '1px solid #ccc';
        card.style.borderRadius = '8px';
        card.style.backgroundColor = '#ffffff';
        card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        card.style.textAlign = 'center';
        card.style.position = 'relative';

        card.innerHTML = `
            <div class="card-content" style="position: relative; z-index: 1;">
                <div class="number-loader" style="font-size: 36px; font-weight: bold; color: #333; min-height: 48px; display: flex; align-items: center; justify-content: center;">
                    <span class="mini-loader" style="width: 24px; height: 24px; border: 2px solid #f3f3f3; border-top: 2px solid #5979aa; border-radius: 50%; animation: spin 1s linear infinite;"></span>
                </div>
                <div style="font-size: 18px; color: #666;">${title}</div>
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
    function updateCardData(cardId, value, extraLine = '') {
        const card = cardReferences[cardId];
        if (!card) return;

        const numberElement = card.querySelector('.number-loader');
        const extraLineElement = card.querySelector('.extra-line');

        numberElement.innerHTML = formatNumber(value);
        numberElement.style.minHeight = 'auto';

        if (extraLine) {
            extraLineElement.innerHTML = extraLine;
        } else {
            extraLineElement.innerHTML = '';
        }

        if (cardIdToQueryTypeMap[cardId] && value) {
            card.style.cursor = "pointer";
            card.addEventListener("click", () => handleCardClick(cardId, { id: cardId, value: value, title: card.querySelector('div:nth-child(2)').textContent }, card));
        }
    }

    // Function to create all card placeholders
    function createAllCardPlaceholders() {
        const container = document.querySelector('.cards-container');
        const totalCreche = document.querySelector('.total-creche-card');
        container.innerHTML = '';
        totalCreche.innerHTML = '';

        // Create columns
        for (let i = 1; i <= 4; i++) {
            const column = document.createElement('div');
            column.id = `column-${i}`;
            column.style.flex = '1';
            column.style.display = 'flex';
            column.style.flexDirection = 'column';
            column.style.gap = '20px';
            column.style.backgroundColor = 'transparent';
            column.style.borderRadius = '8px';
            container.appendChild(column);
        }

        // Updated Structure mapping everything accurately 
        const cardStructure = {
            Col0: [], // Empty since all cards are now distributed across the 4 main columns
            Col1: ["cre-983d", "curelichi-99bf", "cresubatt-611c", "crenotsubatt-169a", "daycreope-8fa8", "maxattday-0e61", "attperday-c539"],
            Col2: ["enrchi-a4c9", "curactchi-9abe", "antdatsub-4b97", "antdatnotsub-07f2", "chimeatak-74d7", "chimeanottak-ea05", "snc-57aa"],
            Col3: ["chiexithimon-ce95", "chienrthimon-c6c5", "modund-2ce9", "modwas-6828", "modstu-3599", "grofal-02c8", "grofal-975f"],
            Col4: ["cumenrchi-845b", "cumexichi-3df2", "sevund-55ab", "sevwas-ffdb", "sevstu-3cf6", "grofal-8a20", "pat-f32a"]
        };

        const cardTitles = {
            "cre-983d": "No. of creches",
            "curactchi-9abe": "Current enrolled children",
            "enrchi-a4c9": "Enrolled children",
            "cresubatt-611c": "No. of creches submitted attendance (All Days)",
            "crenotsubatt-169a": "No. of creches not submitted attendance (All Days)",
            "chimeatak-74d7": "Children measurement taken",
            "chimeanottak-ea05": "Children measurement not taken",
            "daycreope-8fa8": "Avg. no. of days creche opened",
            "attperday-c539": "Avg. attendance per day",
            "antdatsub-4b97": "Anthro data submitted",
            "antdatnotsub-07f2": "Anthro data not submitted",
            "curelichi-99bf": "Current eligible children",
            "chienrthimon-c6c5": "Children enrolled this month",
            "chiexithimon-ce95": "Children exited this month",
            "cumenrchi-845b": "Cumulative enrolled children",
            "cumexichi-3df2": "Cumulative exit children",
            "snc-57aa": "Special Nutrition Care",
            "modund-2ce9": "Moderately underweight",
            "modwas-6828": "Moderately wasted",
            "modstu-3599": "Moderately stunted",
            "grofal-02c8": "Growth faltering 1",
            "grofal-8a20": "Growth faltering 1+",
            "sevund-55ab": "Severely underweight",
            "sevwas-ffdb": "Severely wasted",
            "sevstu-3cf6": "Severely stunted",
            "grofal-975f": "Growth faltering 2",
            "pat-f32a": "Zig-Zag",
            "maxattday-0e61": "Maximum attendance in a day",
            "dayattsub-e0a5": "Avg. no. of days attendance submitted"
        };

        const cardColors = {
            // Blue
            "cre-983d": "#cde4f7", "curelichi-99bf": "#cde4f7", "enrchi-a4c9": "#cde4f7", "curactchi-9abe": "#cde4f7",
            "chiexithimon-ce95": "#cde4f7", "chienrthimon-c6c5": "#cde4f7", "cumenrchi-845b": "#cde4f7", "cumexichi-3df2": "#cde4f7",
            // Peach/Pink
            "cresubatt-611c": "#ead3ce", "crenotsubatt-169a": "#ead3ce", "daycreope-8fa8": "#ead3ce",
            "dayattsub-e0a5": "#ead3ce", "maxattday-0e61": "#ead3ce", "attperday-c539": "#ead3ce",
            // Green
            "antdatsub-4b97": "#cde8ce", "antdatnotsub-07f2": "#cde8ce",
            "chimeatak-74d7": "#cde8ce", "chimeanottak-ea05": "#cde8ce",
            // Orange
            "snc-57aa": "#edb64b",
            // Yellow
            "modund-2ce9": "#fef5c5", "modwas-6828": "#fef5c5", "modstu-3599": "#fef5c5", "grofal-02c8": "#fef5c5",
            "grofal-975f": "#fef5c5", "sevund-55ab": "#fef5c5", "sevwas-ffdb": "#fef5c5", "sevstu-3cf6": "#fef5c5",
            "grofal-8a20": "#fef5c5", "pat-f32a": "#fef5c5"
        };

        // Create cards for columns
        for (let i = 1; i <= 4; i++) {
            const column = document.getElementById(`column-${i}`);
            const colKey = `Col${i}`;

            if (cardStructure[colKey]) {
                cardStructure[colKey].forEach(cardId => {
                    const card = createCardWithLoader(cardId, cardTitles[cardId] || cardId);
                    card.style.backgroundColor = cardColors[cardId] || '#ffffff';
                    column.appendChild(card);
                });
            }
        }
    }


    // ── Inline toolbar loader: driven by how many dashboard sections have returned ──
    const rcLoading = {
        total: 0,
        done: 0,
        seconds: 0,
        timerId: null,

        el() { return document.getElementById("rcToolbarLoader"); },

        start(total) {
            const el = this.el();
            if (!el) return;

            this.total = total || 0;
            this.done = 0;
            this.seconds = 0;

            clearInterval(this.timerId);
            this.timerId = setInterval(() => {
                this.seconds++;
                this.paint();
            }, 1000);

            el.style.display = "inline-flex";
            this.paint();
        },

        step() {
            if (this.done < this.total) this.done++;
            this.paint();
        },

        paint() {
            const el = this.el();
            if (!el) return;

            const textEl = document.getElementById("rcToolbarLoaderText");
            const timerEl = document.getElementById("rcToolbarLoaderTimer");

            if (textEl) textEl.textContent = `Loading... (${this.done}/${this.total})`;
            if (timerEl) timerEl.textContent = `(${this.seconds}s)`;
        },

        finish() {
            clearInterval(this.timerId);
            this.timerId = null;
            this.done = this.total;
            this.paint();

            const el = this.el();
            if (el) el.style.display = "none";
        }
    };


    async function fetchDashboardData() {
        const baseUrl = `${BASE_URL}/api/method/frappe.apf.page.report_card.dashboard`;

        const apiParams = {
            partner_id: null,
            state_id: null,
            district_id: null,
            gp_id: null,
            block_id: null,
            supervisor_id: null,
            creche_id: null,
            year: null,
            month: null,
            cstart_date: null,
            cend_date: null,
            c_status: null,
            phases: null
        };

        const filterToApiKeyMap = {
            partner: "partner_id",
            state: "state_id",
            district: "district_id",
            gp: "gp_id",
            block: "block_id",
            supervisor_id: "supervisor_id",
            creche: "creche_id",
            year: "year",
            month: "month",
            creche_status_id: "c_status",
            phases: "phases"
        };

        Object.entries(filterToApiKeyMap).forEach(([fieldname, apiKey]) => {
            const field = page.fields_dict[fieldname];
            if (field) {
                apiParams[apiKey] = field.get_value();
            }
        });

        const rangeType = page.fields_dict["cr_opening_range_type"].get_value();
        const singleDate = page.fields_dict["single_date"].get_value();
        const dateRange = page.fields_dict["c_opening_range"].get_value();

        if (rangeType) {
            if (rangeType === "between" && dateRange && dateRange.length === 2) {
                apiParams.cstart_date = dateRange[0];
                apiParams.cend_date = dateRange[1];
            } else if (rangeType === "before" && singleDate) {
                apiParams.cstart_date = "2017-01-01";
                apiParams.cend_date = singleDate;
            } else if (rangeType === "after" && singleDate) {
                apiParams.cstart_date = singleDate;
                apiParams.cend_date = new Date().toISOString().split("T")[0];
            } else if (rangeType === "equal" && singleDate) {
                apiParams.cstart_date = singleDate;
                apiParams.cend_date = singleDate;
            }
        }

        const constructApiUrl = (section) => {
            const apiUrl = new URL(`${baseUrl}.${section}`);
            Object.entries(apiParams).forEach(([key, value]) => {
                if (value) {
                    apiUrl.searchParams.append(key, value);
                }
            });
            return apiUrl.toString();
        };

        try {
            const apiSections = [
                "dashboard_section_one",
                "dashboard_section_one2",
                "dashboard_section_two",
                "dashboard_section_three",
                "dashboard_section_four",
                "dashboard_section_gf",
                "dashboard_section_gf_one",
                "dashboard_section_gf_two",
                "dashboard_section_zig_zag",
                "dashboard_section_snc"
            ];

            const apiEndpoints = apiSections.map(section => constructApiUrl(section));

            createAllCardPlaceholders();
            rcLoading.start(apiEndpoints.length);

            // Store all data for final processing
            const allData = await Promise.all(apiEndpoints.map((url, index) =>
                fetch(url, {
                    method: "GET",
                    credentials: "same-origin",
                })
                    .then(response => response.json())
                    .then(data => {
                        rcLoading.step();
                        // First pass: Show cards immediately with "Calculating..." for percentages
                        if (data.data) {
                            Object.keys(data.data).forEach(colKey => {
                                if (data.data[colKey] && Array.isArray(data.data[colKey])) {
                                    data.data[colKey].forEach(item => {
                                        if (item && item.id && item.value !== undefined) {
                                            let extraLine = '';

                                            // Show "Calculating..." for cards that need percentages
                                            if (
                                                item.id === "curactchi-9abe" ||
                                                item.id === "cumexichi-3df2" ||
                                                item.id === "modund-2ce9" ||
                                                item.id === "modwas-6828" ||
                                                item.id === "modstu-3599" ||
                                                item.id === "grofal-02c8" ||
                                                item.id === "grofal-8a20" ||
                                                item.id === "sevund-55ab" ||
                                                item.id === "sevwas-ffdb" ||
                                                item.id === "sevstu-3cf6" ||
                                                item.id === "grofal-975f" ||
                                                item.id === "pat-f32a" ||
                                                item.id === "chimeatak-74d7" ||
                                                item.id === "chimeanottak-ea05" ||
                                                item.id === "chiexithimon-ce95"
                                            ) {
                                                extraLine = '(Calculating percentage...)';
                                            }

                                            if (item.id === "enrchi-a4c9") {
                                                extraLine = '(Current Enrolled + Children Exited this month)';
                                            }

                                            updateCardData(item.id, item.value, extraLine);
                                        }
                                    });
                                }
                            });
                        }
                        return data;
                    })
            ));

            // Second pass: After all data is loaded, calculate and update percentages
            let current_eligible_children = 0;
            let current_active_children = 0;
            let child_measurement_taken = 0;
            let cumm_enrolled_children = 0;
            let enrolled_children = 0;

            // Find the values we need for calculations across all returned columns
            allData.forEach(data => {
                if (data.data) {
                    Object.keys(data.data).forEach(colKey => {
                        const items = data.data[colKey];
                        if (Array.isArray(items)) {
                            const eligibleItem = items.find(i => i.id === "curelichi-99bf");
                            if (eligibleItem) current_eligible_children = eligibleItem.value;

                            const enrolledItem = items.find(i => i.id === "cumenrchi-845b");
                            if (enrolledItem) cumm_enrolled_children = enrolledItem.value;

                            const measurementItem = items.find(i => i.id === "chimeatak-74d7");
                            if (measurementItem) child_measurement_taken = measurementItem.value;

                            const activeItem = items.find(i => i.id === "curactchi-9abe");
                            if (activeItem) current_active_children = activeItem.value;

                            const enrolledChildrenItem = items.find(i => i.id === "enrchi-a4c9");
                            if (enrolledChildrenItem) enrolled_children = enrolledChildrenItem.value;
                        }
                    });
                }
            });

            // Update percentages for all relevant cards
            allData.forEach(data => {
                if (data.data) {
                    Object.keys(data.data).forEach(colKey => {
                        if (data.data[colKey] && Array.isArray(data.data[colKey])) {
                            data.data[colKey].forEach(item => {
                                if (item && item.id && item.value !== undefined) {
                                    let extraLine = '';

                                    // Calculate actual percentages now that we have all data
                                    if (item.id === "curactchi-9abe") {
                                        const percentage = current_eligible_children && item.value ?
                                            ((item.value / current_eligible_children) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of current eligible children)`;
                                    }
                                    else if (item.id === "enrchi-a4c9") {
                                        extraLine = '(Current Enrolled + Children Exited this month)';
                                    }
                                    else if (item.id === "modund-2ce9") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "modwas-6828") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "modstu-3599") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "sevund-55ab") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "sevwas-ffdb") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "sevstu-3cf6") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "cumexichi-3df2") {
                                        const percentage = cumm_enrolled_children && item.value ?
                                            ((item.value / cumm_enrolled_children) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of cumulative enrolled children)`;
                                    }
                                    else if (item.id === "chiexithimon-ce95") {
                                        const percentage = current_active_children && item.value ?
                                            ((item.value / current_active_children) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of active children)`;
                                    }
                                    else if (item.id === "grofal-02c8") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "grofal-8a20") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "grofal-975f") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "pat-f32a") {
                                        const percentage = child_measurement_taken && item.value ?
                                            ((item.value / child_measurement_taken) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of children measurement taken)`;
                                    }
                                    else if (item.id === "chimeatak-74d7") {
                                        const percentage = enrolled_children && item.value ?
                                            ((item.value / enrolled_children) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of enrolled children)`;
                                    }
                                    else if (item.id === "chimeanottak-ea05") {
                                        const percentage = enrolled_children && item.value ?
                                            ((item.value / enrolled_children) * 100) : 0;
                                        extraLine = `(${percentage.toFixed(1)}% of enrolled children)`;
                                    }

                                    // Only update if we have a percentage to show
                                    if (extraLine) {
                                        updateCardData(item.id, item.value, extraLine);
                                    }
                                }
                            });
                        }
                    });
                }
            });

        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            // Always dismiss, even if a section failed, so the page is never
            // left behind a stuck overlay.
            rcLoading.finish();
        }
    }

    function formatNumber(number) {
        return new Intl.NumberFormat("en-IN").format(number);
    }

    const cardIdToQueryTypeMap = {
        "curactchi-9abe": "active_children",
        "cresubatt-611c": "no_creche_attendance_submitted",
        "curelichi-99bf": "current_eligible_children",
        "chienrthimon-c6c5": "enrolled_children_this_month",
        "enrchi-a4c9": "enrolled_children",
        "chiexithimon-ce95": "exited_children_this_month",
        "modund-2ce9": "moderately_underweight",
        "modwas-6828": "moderately_wasted",
        "modstu-3599": "moderately_stunted",
        "grofal-02c8": "gf1",
        "grofal-8a20": "gf1_plus",
        "sevund-55ab": "severly_underweight",
        "sevwas-ffdb": "severly_wasted",
        "sevstu-3cf6": "severly_stunted",
        "grofal-975f": "gf2",
        "pat-f32a": "zigzag",
        "antdatsub-4b97": "anthro_data_submitted",
        "antdatnotsub-07f2": "anthro_data_not_submitted",
        "cre-983d": "no_of_creches",
        "chimeatak-74d7": "measurement_data_submitted",
        "crenotsubatt-169a": "no_of_creches_not_submitted_attendance",
        "chimeanottak-ea05": "measurement_data_not_submitted",
        "snc-57aa": "snc"
    };

    // Query types whose detail table carries the attendance columns, and so can
    // show the 3-month "Attendance Trend" view.
    const attendanceTrendQueryTypes = new Set([
        "moderately_underweight",
        "moderately_wasted",
        "moderately_stunted",
        "severly_underweight",
        "severly_wasted",
        "severly_stunted",
        "gf1",
        "gf1_plus",
        "gf2",
        "zigzag",
        "snc"
    ]);


    async function handleCardClick(cardId, item, cardElement, attendanceTrend = 0) {
        const overlay = cardElement.querySelector('.card-overlay');

        // Show the overlay with spinner
        if (overlay) {
            overlay.style.display = 'flex';
            setTimeout(() => {
                overlay.style.opacity = '1';
            }, 10);
        }

        const queryType = cardIdToQueryTypeMap[cardId];
        const year = page.fields_dict["year"].get_value() || 2024;
        const month = page.fields_dict["month"].get_value() || 10;
        const partner = page.fields_dict["partner"].get_value();
        const state = page.fields_dict["state"].get_value();
        const district = page.fields_dict["district"].get_value();
        const block = page.fields_dict["block"].get_value();
        const gp = page.fields_dict["gp"].get_value();
        const supervisor_id = page.fields_dict["supervisor_id"].get_value();
        const creche = page.fields_dict["creche"].get_value();
        const phases = page.fields_dict["phases"].get_value();
        const creche_status_id = page.fields_dict["creche_status_id"].get_value();
        const rangeType = page.fields_dict["cr_opening_range_type"].get_value();
        const singleDate = page.fields_dict["single_date"].get_value();
        const dateRange = page.fields_dict["c_opening_range"].get_value();

        let cstart_date = null;
        let cend_date = null;

        if (rangeType) {
            if (rangeType === "between" && dateRange && dateRange.length === 2) {
                cstart_date = dateRange[0];
                cend_date = dateRange[1];
            } else if (rangeType === "before" && singleDate) {
                cstart_date = "2017-01-01";
                cend_date = singleDate;
            } else if (rangeType === "after" && singleDate) {
                cstart_date = singleDate;
                cend_date = new Date().toISOString().split("T")[0];
            } else if (rangeType === "equal" && singleDate) {
                cstart_date = singleDate;
                cend_date = singleDate;
            }
        }

        const rawParams = {
            year,
            month,
            query_type: queryType,
            partner_id: partner,
            state_id: state,
            district_id: district,
            block_id: block,
            gp_id: gp,
            supervisor_id,
            creche_id: creche,
            phases,
            c_status: creche_status_id,
            cstart_date,
            cend_date,
            attendance_trend: attendanceTrend ? 1 : 0
        };

        const params = new URLSearchParams();
        for (const key in rawParams) {
            if (rawParams[key] !== null && rawParams[key] !== undefined && rawParams[key] !== "") {
                params.append(key, rawParams[key]);
            }
        }

        const apiUrl = `${BASE_URL}/api/method/frappe.apf.page.report_card.web_report_card_detail.fetch_card_data?${params.toString()}`;
        const title = item.title;

        // Remember what produced this table so the "Attendance Trend" button can
        // re-run the same request with the 3-month columns switched on.
        const modalContext = {
            cardId,
            item,
            cardElement,
            attendanceTrend,
            supportsTrend: attendanceTrendQueryTypes.has(queryType)
        };

        try {
            const res = await fetch(apiUrl, { credentials: "same-origin" });
            const result = await res.json();

            if (result && result.data && result.data.length > 0) {
                const columns = Object.keys(result.data[0]);
                const rows = result.data.map(entry => columns.map(key => entry[key]));
                openModalWithTable(columns, rows, title, modalContext);
            } else {
                openModalWithTable([""], [["No record found"]], title, modalContext);
            }
        } catch (err) {
            console.error("Error fetching card data:", err);
            openModalWithTable([""], [["Error fetching data"]], title, modalContext);
        }
        finally {
            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.style.display = 'none';
                }, 300); // Match the transition duration
            }
        }
    }

    // Cache for document name lookups to avoid repeated API calls
    const docNameCache = {
        child: new Map(),
        creche: new Map()
    };

    // Prefetch document names for visible rows
    async function prefetchDocNames(data, columns) {
        const childIdIndex = columns.findIndex(col =>
            col && (col.toLowerCase() === "child id" ||
                col.toLowerCase() === "child_id" ||
                col.toLowerCase() === "id" ||
                col.toLowerCase().includes("child"))
        );

        const crecheIdIndex = columns.findIndex(col =>
            col && (col.toLowerCase() === "creche id" ||
                col.toLowerCase() === "creche_id" ||
                col.toLowerCase() === "creche")
        );

        if (childIdIndex === -1 || crecheIdIndex === -1) return;

        // Get unique IDs from first 50 rows for prefetching
        const uniqueChildIds = new Set();
        const uniqueCrecheIds = new Set();

        data.slice(0, 50).forEach(row => {
            const childId = row[childIdIndex];
            const crecheId = row[crecheIdIndex];
            if (childId) uniqueChildIds.add(childId);
            if (crecheId) uniqueCrecheIds.add(crecheId);
        });

        // Batch fetch child doc names
        if (uniqueChildIds.size > 0) {
            const childIds = Array.from(uniqueChildIds);
            const childIdFilter = childIds.map(id => `["child_id","=","${id}"]`).join(',');

            try {
                const response = await fetch(`/api/resource/Child Enrollment and Exit?filters=[["child_id","in",[${childIds.map(id => `"${id}"`).join(',')}]]]&fields=["name","child_id"]&limit_page_length=999`, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'X-Frappe-CSRF-Token': frappe.csrf_token
                    }
                });

                const result = await response.json();
                if (result.data) {
                    result.data.forEach(item => {
                        if (item.child_id && item.name) {
                            docNameCache.child.set(item.child_id, item.name);
                        }
                    });
                }
            } catch (error) {
                console.error('Error prefetching child doc names:', error);
            }
        }

        // Batch fetch creche doc names
        if (uniqueCrecheIds.size > 0) {
            const crecheIds = Array.from(uniqueCrecheIds);

            try {
                const response = await fetch(`/api/resource/Creche?filters=[["creche_id","in",[${crecheIds.map(id => `"${id}"`).join(',')}]]]&fields=["name","creche_id"]&limit_page_length=999`, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'X-Frappe-CSRF-Token': frappe.csrf_token
                    }
                });

                const result = await response.json();
                if (result.data) {
                    result.data.forEach(item => {
                        if (item.creche_id && item.name) {
                            docNameCache.creche.set(item.creche_id, item.name);
                        }
                    });
                }
            } catch (error) {
                console.error('Error prefetching creche doc names:', error);
            }
        }
    }

    // Get cached or fetch document name
    async function getDocName(type, identifier) {
        const cache = type === 'child' ? docNameCache.child : docNameCache.creche;

        // Return from cache if available
        if (cache.has(identifier)) {
            return cache.get(identifier);
        }

        // Fetch if not in cache
        try {
            const docType = type === 'child' ? 'Child Enrollment and Exit' : 'Creche';
            const filterField = type === 'child' ? 'child_id' : 'creche_id';

            const response = await fetch(`/api/resource/${docType}?filters=[["${filterField}","=","${identifier}"]]&fields=["name"]&limit_page_length=1`, {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                }
            });

            const result = await response.json();

            if (result.data && result.data.length > 0) {
                const docName = result.data[0].name;
                cache.set(identifier, docName);
                return docName;
            }
        } catch (error) {
            console.error(`Error fetching ${type} doc name:`, error);
        }

        return identifier; // fallback
    }

    function openModalWithTable(columns, data, title, context = null) {
        const modal = document.getElementById("dataModal");
        const container = document.getElementById("modalTableContainer");
        const titleElement = modal.querySelector("h2");
        const closeBtn = modal.querySelector(".close-btn");

        modal.currentData = { columns, data, title };
        modal.trendContext = context;

        // Only cards that carry attendance columns get the trend toggle.
        const trendBtn = document.getElementById("attendanceTrendBtn");
        if (trendBtn) {
            if (context && context.supportsTrend) {
                trendBtn.style.display = "";
                trendBtn.disabled = false;
                trendBtn.textContent = context.attendanceTrend
                    ? "Hide Attendance Trend"
                    : "Attendance Trend";
            } else {
                trendBtn.style.display = "none";
            }
        }

        titleElement.textContent = title;
        document.body.classList.add("modal-open");
        modal.style.display = "block";

        container.innerHTML = "";
        container.appendChild(createSkeletonTable(columns.length + 1, 10));

        // Start prefetching doc names in background
        if (title !== "Current eligible children") {
            prefetchDocNames(data, columns).catch(err =>
                console.error('Prefetch error:', err)
            );
        }

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

            // Find column indices once
            const childNameIndex = columns.findIndex(col =>
                col && col.toLowerCase().includes("child name")
            );

            const childIdIndex = columns.findIndex(col =>
                col && (col.toLowerCase() === "child id" ||
                    col.toLowerCase() === "child_id" ||
                    col.toLowerCase() === "id" ||
                    col.toLowerCase().includes("child"))
            );

            const crecheIdIndex = columns.findIndex(col =>
                col && (col.toLowerCase() === "creche id" ||
                    col.toLowerCase() === "creche_id" ||
                    col.toLowerCase() === "creche")
            );

            const isChildNameClickable = title !== "Current eligible children" &&
                childNameIndex !== -1 &&
                childIdIndex !== -1 &&
                crecheIdIndex !== -1;

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

                            // Check if this is a clickable child name
                            if (isChildNameClickable && cellIndex === childNameIndex && cell) {
                                const childIdentifier = dataset[rowIndex][childIdIndex];
                                const crecheIdentifier = dataset[rowIndex][crecheIdIndex];

                                if (childIdentifier && crecheIdentifier) {
                                    const link = document.createElement('a');
                                    link.href = '#';
                                    link.textContent = cell;
                                    link.style.color = '#5979aa';
                                    link.style.textDecoration = 'underline';
                                    link.style.cursor = 'pointer';

                                    link.addEventListener('click', async function (e) {
                                        e.preventDefault();
                                        e.stopPropagation();

                                        // Show loading state
                                        const originalText = link.textContent;
                                        link.textContent = 'Loading...';
                                        link.style.cursor = 'wait';

                                        try {
                                            // Use cached or fetch doc names (parallel fetching)
                                            const [childDocName, crecheDocName] = await Promise.all([
                                                getDocName('child', childIdentifier),
                                                getDocName('creche', crecheIdentifier)
                                            ]);

                                            // Open Growth Monitoring page
                                            const url = `https://shishughar.in/app/growth-monitoring-ch?creche_id=${crecheDocName}&child_id=${childDocName}`;
                                            window.open(url, '_blank');

                                        } catch (error) {
                                            console.error('Error opening growth monitoring:', error);
                                            // Fallback: use the original identifiers
                                            const url = `https://shishughar.in/app/growth-monitoring-ch?creche_id=${crecheIdentifier}&child_id=${childIdentifier}`;
                                            window.open(url, '_blank');
                                        } finally {
                                            // Restore the link text
                                            link.textContent = originalText;
                                            link.style.cursor = 'pointer';
                                        }
                                    });

                                    td.appendChild(link);
                                } else {
                                    td.textContent = cell;
                                }
                            } else {
                                td.textContent = cell;
                            }

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

            // Fix for duplicate search inputs (mobile & desktop views matching the same event listener)
            const searchInputs = modal.querySelectorAll(".modal-search-input");
            
            searchInputs.forEach(searchInput => {
                const newSearchInput = searchInput.cloneNode(true);
                newSearchInput.value = ""; // start with empty search
                if (searchInput.parentNode) {
                    searchInput.parentNode.replaceChild(newSearchInput, searchInput);
                }

                newSearchInput.addEventListener("input", function () {
                    clearTimeout(searchTimeout);
                    const q = this.value.toLowerCase();

                    // Keep mobile and desktop inputs in sync
                    const allInputs = modal.querySelectorAll(".modal-search-input");
                    allInputs.forEach(input => {
                        if (input !== this) {
                            input.value = this.value;
                        }
                    });

                    searchTimeout = setTimeout(() => {
                        if (q === '') {
                            filteredData = [...data];
                        } else {
                            filteredData = data.filter(row =>
                                row.some(cell =>
                                    // Make sure numeric IDs and other datatypes can be searched too
                                    cell != null && String(cell).toLowerCase().includes(q)
                                )
                            );
                        }
                        renderTableRows(filteredData);
                    }, 150); // Debounce by 150ms
                });
            });

        }, 300);
    }

    // Optional: Clear cache when modal closes to free memory
    function clearDocNameCache() {
        docNameCache.child.clear();
        docNameCache.creche.clear();
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
        // Clear all search input instances (mobile & desktop)
        const searchInputs = document.querySelectorAll(".modal-search-input");
        searchInputs.forEach(input => input.value = "");
        
        document.getElementById("dataModal").style.display = "none";
        document.body.classList.remove("modal-open");
    }

    document.querySelector(".close-btn").addEventListener("click", closeModal);
    window.addEventListener("click", (event) => {
        if (event.target === document.getElementById("dataModal")) {
            closeModal();
        }
    });

    document.addEventListener("click", async function (e) {
        if (e.target && e.target.id === "attendanceTrendBtn") {
            const modal = document.getElementById("dataModal");
            const context = modal.trendContext;
            if (!context || !context.supportsTrend) return;

            const btn = e.target;
            btn.disabled = true;
            btn.textContent = "Loading...";

            // Re-run the same card query with the trend flag flipped.
            await handleCardClick(
                context.cardId,
                context.item,
                context.cardElement,
                context.attendanceTrend ? 0 : 1
            );
            return;
        }

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

    // -------- Logic Features --------
    const logicDataList = [
        { "title": "No. of Creches", "logic": "Total number of creches that are active and operational (status = active, or if other status then opened on or before the selected month end)" },
        { "title": "Current Eligible Children", "logic": "Number of children from household records aged between 6 and 36 months at the end of the selected month, with no child status and belonging to the filtered creches" },
        { "title": "No. of Creches Submitted Attendance (All Days)", "logic": "Number of creches that have submitted attendance for every eligible operational day in the month (i.e., recorded attendance days ≥ eligible days)" },
        { "title": "No. of Creches Not Submitted Attendance (All Days)", "logic": "Number of creches where attendance has not been submitted for all eligible operational days (recorded days < eligible days)" },
        { "title": "Avg. No. of Days Creche Opened", "logic": "Total number of days creches were open (marked as not closed) across all creches divided by the total number of creches, rounded up (average days opened per creche)" },
        { "title": "Maximum Attendance in a Day", "logic": "Maximum count of children present in a single day across all creches (on days when creches were open)" },
        { "title": "Avg. Attendance per Day", "logic": "Average number of children present per day when creches were open, calculated as total child attendance count / total creche open days, rounded to 1 decimal" },
        { "title": "Enrolled Children", "logic": "Total distinct children who were either active (enrolled and not exited) or exited during the selected month" },
        { "title": "Current Enrolled Children", "logic": "Number of children currently enrolled (active) as of the end of the selected month (enrolled on or before month end and not exited)" },
        { "title": "Anthro Data Submitted", "logic": "Number of growth monitoring (anthropometric) records submitted in the selected month" },
        { "title": "Anthro Data Not Submitted", "logic": "Number of creches for which no growth monitoring data was submitted in the selected month" },
        { "title": "Children Measurement Taken", "logic": "Number of children for whom anthropometric measurements (height/weight) were recorded this month" },
        { "title": "Children Measurement Not Taken", "logic": "Number of currently enrolled children for whom no anthropometric measurement was recorded this month" },
        { "title": "Special Nutrition Care", "logic": "Number of children requiring special nutrition care: those with any growth faltering (decline in weight‑for‑age Z‑score over 1‑3 months, zig‑zag pattern) or classified as severely underweight or severely wasted" },
        { "title": "Children Exited This Month", "logic": "Number of children who exited the programme during the selected month" },
        { "title": "Children Enrolled This Month", "logic": "Number of children newly enrolled during the selected month" },
        { "title": "Moderately Underweight", "logic": "Number of children classified as moderately underweight (weight‑for‑age = Modrate) based on this month’s measurements" },
        { "title": "Moderately Wasted", "logic": "Number of children classified as moderately wasted (weight‑for‑height = Modrate) based on this month’s measurements" },
        { "title": "Moderately Stunted", "logic": "Number of children classified as moderately stunted (height‑for‑age = Modrate) based on this month’s measurements" },
        { "title": "Growth Faltering 1", "logic": "Number of children whose weight‑for‑age Z‑score has declined (any decrease) compared to the previous month (or 2 months ago if previous data is missing)" },
        { "title": "Growth Faltering 2", "logic": "Number of children whose weight‑for‑age Z‑score has declined by at least 0.5 compared to 2 months ago (or 3 months ago if 2‑month data is missing)" },
        { "title": "Cumulative Enrolled Children", "logic": "Total number of children enrolled up to the end of the selected month" },
        { "title": "Cumulative Exit Children", "logic": "Total number of children who have exited up to the end of the selected month" },
        { "title": "Severely Underweight", "logic": "Number of children classified as severely underweight (weight‑for‑age = Severe) based on this month’s measurements" },
        { "title": "Severely Wasted", "logic": "Number of children classified as severely wasted (weight‑for‑height = Severe) based on this month’s measurements" },
        { "title": "Severely Stunted", "logic": "Number of children classified as severely stunted (height‑for‑age = Severe) based on this month’s measurements" },
        { "title": "Growth Faltering 1+", "logic": "Number of children whose weight‑for‑age Z‑score has declined by at least 0.5 compared to the previous month (or 2 months ago if previous data is missing)" },
        { "title": "Zig-Zag", "logic": "Number of children whose weight‑for‑age Z‑score has dropped by at least 0.5 compared to the maximum Z‑score of the past 4 months, while also showing a fluctuating (zig‑zag) pattern with at least one increase and one decrease in consecutive months over the last 5 months" }
    ];

    function populateLogicTable() {
        const tbody = document.getElementById("logicTableBody");
        if (tbody.innerHTML.trim() !== "") return; // Avoid repopulating

        let rowsHtml = "";
        logicDataList.forEach((row, index) => {
            const bgClass = index % 2 === 0 ? "background-color: #f9f9f9;" : "background-color: #ffffff;";
            rowsHtml += `
                <tr style="${bgClass}">
                    <td style="padding: 10px 12px; border: 1px solid #ddd; font-weight: 600; color: #333; white-space: normal;">${row.title}</td>
                    <td style="padding: 10px 12px; border: 1px solid #ddd; color: #555; white-space: normal; line-height: 1.5;">${row.logic}</td>
                </tr>
            `;
        });
        tbody.innerHTML = rowsHtml;
    }

    function openLogicModal() {
        populateLogicTable();
        document.getElementById("logicModal").style.display = "block";
        document.body.classList.add("modal-open");
    }

    function closeLogicModal() {
        document.getElementById("logicModal").style.display = "none";
        document.body.classList.remove("modal-open");
    }

    logicBtn.on('click', function (e) {
        e.preventDefault();
        openLogicModal();
    });

    $(document).on("click", ".logic-close-btn", closeLogicModal);
    window.addEventListener("click", (event) => {
        if (event.target === document.getElementById("logicModal")) {
            closeLogicModal();
        }
    });

    $(document).on("click", "#downloadLogicXlsxBtn", function (e) {
        e.preventDefault();
        const btn = $(this);
        const originalText = btn.text();
        btn.text('Downloading...');
        btn.prop('disabled', true).css({ opacity: 0.6, cursor: 'not-allowed' });

        setTimeout(() => {
            try {
                const rows = logicDataList.map(row => {
                    return { "Card Title": row.title, "Logic": row.logic };
                });

                if (rows.length > 0) {
                    const worksheet = XLSX.utils.json_to_sheet(rows);
                    const workbook = XLSX.utils.book_new();
                    XLSX.utils.book_append_sheet(workbook, worksheet, "Card Logic");
                    XLSX.writeFile(workbook, "card_logic.xlsx");
                }
            } catch (err) {
                console.error("Error generating Logic XLSX", err);
                if (frappe && frappe.msgprint) frappe.msgprint("Error generating XLSX.");
            } finally {
                btn.text(originalText);
                btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
            }
        }, 100);
    });

    $(document).on("click", "#downloadLogicPngBtn", function (e) {
        e.preventDefault();
        const btn = $(this);
        const originalText = btn.text();
        btn.text('Downloading...');
        btn.prop('disabled', true).css({ opacity: 0.6, cursor: 'not-allowed' });

        setTimeout(() => {
            const targetElement = document.getElementById('logicModalContent');
            const wrapper = document.getElementById('logicTableWrapper');
            if (targetElement && wrapper) {
                // Save original styles
                const wrapperOrigMaxHeight = wrapper.style.maxHeight;
                const wrapperOrigOverflowY = wrapper.style.overflowY;
                const modalOrigMaxHeight = targetElement.style.maxHeight;
                const modalOrigOverflow = targetElement.style.overflow;

                // Expand completely
                wrapper.style.maxHeight = 'none';
                wrapper.style.overflowY = 'visible';
                targetElement.style.maxHeight = 'none';
                targetElement.style.overflow = 'visible';

                html2canvas(targetElement, { 
                    scale: 2,
                    windowHeight: targetElement.scrollHeight,
                    scrollY: -window.scrollY
                }).then(canvas => {
                    canvas.toBlob(function(blob) {
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement("a");
                        link.href = url;
                        link.download = "card_logic.png";
                        link.click();
                        URL.revokeObjectURL(url);
                        
                        // Restore styles
                        wrapper.style.maxHeight = wrapperOrigMaxHeight;
                        wrapper.style.overflowY = wrapperOrigOverflowY;
                        targetElement.style.maxHeight = modalOrigMaxHeight;
                        targetElement.style.overflow = modalOrigOverflow;
                        btn.text(originalText);
                        btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
                    }, "image/png");
                }).catch(err => {
                    console.error("Error generating Logic PNG", err);
                    if (frappe && frappe.msgprint) frappe.msgprint("Error generating PNG.");
                    
                    // Restore styles
                    wrapper.style.maxHeight = wrapperOrigMaxHeight;
                    wrapper.style.overflowY = wrapperOrigOverflowY;
                    targetElement.style.maxHeight = modalOrigMaxHeight;
                    targetElement.style.overflow = modalOrigOverflow;
                    btn.text(originalText);
                    btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
                });
            } else {
                btn.text(originalText);
                btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
            }
        }, 100);
    });

    $(document).on("click", "#downloadLogicPdfBtn", function (e) {
        e.preventDefault();
        const btn = $(this);
        const originalText = btn.text();
        btn.text('Downloading...');
        btn.prop('disabled', true).css({ opacity: 0.6, cursor: 'not-allowed' });

        setTimeout(() => {
            const targetElement = document.getElementById('logicModalContent');
            const wrapper = document.getElementById('logicTableWrapper');
            if (targetElement && wrapper) {
                const wrapperOrigMaxHeight = wrapper.style.maxHeight;
                const wrapperOrigOverflowY = wrapper.style.overflowY;
                const modalOrigMaxHeight = targetElement.style.maxHeight;
                const modalOrigOverflow = targetElement.style.overflow;

                wrapper.style.maxHeight = 'none';
                wrapper.style.overflowY = 'visible';
                targetElement.style.maxHeight = 'none';
                targetElement.style.overflow = 'visible';

                html2canvas(targetElement, {
                    scale: 2,
                    windowHeight: targetElement.scrollHeight,
                    scrollY: -window.scrollY
                }).then(canvas => {
                    const { jsPDF: JSPDF } = window.jspdf || {};
                    const JsPDF = JSPDF || window.jsPDF;

                    const imgWidth = canvas.width;
                    const imgHeight = canvas.height;
                    const ratio = imgWidth / imgHeight;

                    // A4 portrait, fit width
                    const doc = new JsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
                    const pageW = doc.internal.pageSize.getWidth();
                    const pageH = doc.internal.pageSize.getHeight();
                    const scaledW = pageW;
                    const scaledH = scaledW / ratio;

                    let yOffset = 0;
                    let remaining = scaledH;

                    while (remaining > 0) {
                        const sliceH = Math.min(remaining, pageH);
                        const srcY = yOffset * (imgHeight / scaledH);
                        const srcH = sliceH * (imgHeight / scaledH);

                        const sliceCanvas = document.createElement('canvas');
                        sliceCanvas.width = imgWidth;
                        sliceCanvas.height = srcH;
                        const ctx = sliceCanvas.getContext('2d');
                        ctx.drawImage(canvas, 0, srcY, imgWidth, srcH, 0, 0, imgWidth, srcH);

                        if (yOffset > 0) doc.addPage();
                        doc.addImage(sliceCanvas.toDataURL('image/png'), 'PNG', 0, 0, scaledW, sliceH);

                        yOffset += sliceH;
                        remaining -= sliceH;
                    }

                    doc.save('card_logic.pdf');

                    wrapper.style.maxHeight = wrapperOrigMaxHeight;
                    wrapper.style.overflowY = wrapperOrigOverflowY;
                    targetElement.style.maxHeight = modalOrigMaxHeight;
                    targetElement.style.overflow = modalOrigOverflow;
                    btn.text(originalText);
                    btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
                }).catch(err => {
                    console.error("Error generating Logic PDF", err);
                    if (frappe && frappe.msgprint) frappe.msgprint("Error generating PDF.");

                    wrapper.style.maxHeight = wrapperOrigMaxHeight;
                    wrapper.style.overflowY = wrapperOrigOverflowY;
                    targetElement.style.maxHeight = modalOrigMaxHeight;
                    targetElement.style.overflow = modalOrigOverflow;
                    btn.text(originalText);
                    btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
                });
            } else {
                btn.text(originalText);
                btn.prop('disabled', false).css({ opacity: 1, cursor: 'pointer' });
            }
        }, 100);
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

    // Add CSS for mini loader animation + responsive header
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes rcToolbarSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 600px) {
            #rcToolbarLoader { display: none !important; }
        }

        /* ── Compact header ── */
        #page-report-card > div.page-head.flex {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            margin-bottom: 0 !important;
            min-height: unset !important;
            height: auto !important;
            line-height: 1 !important;
        }
        #page-report-card > div.page-head.flex .page-head-content {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
            min-height: unset !important;
            align-items: center !important;
        }
        #page-report-card > div.page-head.flex .title-area,
        #page-report-card > div.page-head.flex .page-title {
            padding: 0 !important;
            margin: 0 !important;
            line-height: 1.2 !important;
        }
        #page-report-card > div.page-head.flex h1.title-text {
            font-size: 1.1rem !important;
            line-height: 1.2 !important;
            margin: 0 !important;
        }

        /* ── Filter → page-body gap ── */
        #page-report-card .page-form {
            margin-bottom: 10px !important;
        }
        #page-report-card .page-body {
            margin-top: 6px !important;
        }

        /* ── Mobile: hide desktop buttons, show kebab ── */
        @media (max-width: 600px) {
            .rc-search-btn,
            .rc-reset-btn,
            .custom-dropdown,
            .logic-btn {
                display: none !important;
            }
            #mobile-kebab {
                display: inline-block !important;
            }
            .page-form .frappe-control {
                flex: 1 1 calc(50% - 8px) !important;
                min-width: 120px !important;
            }
        }
    `;
    document.head.appendChild(style);

    frappe.after_ajax(() => {
        renderCards();
    });
};

