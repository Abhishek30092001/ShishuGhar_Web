frappe.pages['home'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: ' ',
        single_column: true
    });
    $(wrapper).prepend(`
        <style>
            /* Completely hide Frappe's default Chrome/Navbar to achieve true full screen */
            header.navbar,
            .standard-sidebar,
            .page-head,
            footer {
                display: none !important;
            }

            body {
                padding: 0 !important;
                margin: 0 !important;
                overflow: hidden !important; 
            }

            .page-wrapper {
                margin-top: 0 !important;
            }

            .container,
            .page-body,
            .page-content {
                max-width: 100% !important;
                width: 100% !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            .layout-main-section {
                padding: 0 !important;
                border: none !important;
            }
        </style>
    `);

    // ==========================================
    // 2. INJECT APP CSS & HTML
    // ==========================================
    $(wrapper).find('.layout-main-section').html(`
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

            * { margin: 0; padding: 0; box-sizing: border-box; }

            :root {
                --bg-main: #f5f7fb;
                --bg-sidebar: #ffffff;
                --bg-card: #ffffff;
                --text-primary: #2d3748;
                --text-secondary: #4a5568;
                --border-color: #e2e8f0;
                --border-card: rgba(200, 210, 220, 0.4);
                --header-bg: #5979aa;
                --card-shadow: 0 2px 6px rgba(0,0,0,0.03);
                --card-hover-shadow: 0 8px 20px rgba(0,0,0,0.06);
                --sidebar-hover: #f1f5f9;
                --link-bg: rgba(255, 255, 255, 0.6);
                --link-hover: #ffffff;
                --no-result-bg: white;
                
                /* Professional UI Colors */
                --mgmt-card-bg: #ffffff;
                --mgmt-item-bg: #f8fafc;
                --mgmt-item-hover: #ffffff;
                --mgmt-item-border: transparent;
                --mgmt-item-border-hover: #93c5fd;
                --mgmt-icon-bg: #eff6ff;
                --mgmt-icon-color: #3b82f6;
            }

            /* STRICT BLACK DARK MODE */
            .dark-mode {
                --bg-main: #000000;        
                --bg-sidebar: #0a0a0a;    
                --bg-card: #141414;        
                --text-primary: #ffffff;
                --text-secondary: #a3a3a3;
                --border-color: #262626;
                --border-card: #262626;
                --header-bg: #0a0a0a;      
                --card-shadow: 0 4px 15px rgba(0,0,0,0.8);
                --card-hover-shadow: 0 8px 25px rgba(0,0,0,0.9);
                --sidebar-hover: #1f1f1f;
                --link-bg: rgba(255, 255, 255, 0.05); 
                --link-hover: rgba(255, 255, 255, 0.1);
                --no-result-bg: #0a0a0a;

                /* Dark Mode Professional UI */
                --mgmt-card-bg: #141414;
                --mgmt-item-bg: #0a0a0a;
                --mgmt-item-hover: #1f1f1f;
                --mgmt-item-border-hover: #3b82f6;
                --mgmt-icon-bg: #1f1f1f;
                --mgmt-icon-color: #ffffff;
            }

            /* Locks the entire UI to cover the Frappe interface */
            .shishu-app-container { 
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999;
                display: flex; flex-direction: column; 
                font-family: "Inter", sans-serif; background: var(--bg-main); 
                overflow: hidden; transition: background 0.3s; 
            }
            
            /* --- Header & Navigation --- */
            .top-header { 
                height: 76px; background: var(--header-bg); display: flex; 
                justify-content: space-between; align-items: center; padding: 0 24px; 
                flex-shrink: 0; z-index: 20; box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
                transition: background 0.3s; border-bottom: 1px solid var(--border-color); 
            }
            .header-left { display: flex; align-items: center; gap: 16px; }
            .sidebar-toggle-btn { background: transparent; border: none; color: white; font-size: 26px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: transform 0.2s; padding: 4px; }
            .sidebar-toggle-btn:hover { transform: scale(1.1); }
            
            .brand-section { display: flex; align-items: center; gap: 12px; }
            .brand-logo { height: 60px; width: 60px; object-fit: contain; border-radius: 8px; background: rgba(255, 255, 255, 0.95); padding: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .brand-text { display: flex; flex-direction: column; overflow: hidden; max-width: 100%; }
            .brand-name { display: flex; align-items: baseline; gap: 8px; overflow: hidden; max-width: 100%; }
            .brand-en { font-family: "Poppins", sans-serif; font-size: 24px; font-weight: 700; color: #ffffff; line-height: 1.1; letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
            .brand-hi { font-family: "Poppins", sans-serif; font-size: 18px; font-weight: 600; color: #e8f4e8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
            .brand-subtitle { font-size: 11px; font-weight: 500; color: rgba(255, 255, 255, 0.85); text-transform: uppercase; letter-spacing: 0.5px; }
            
            .header-right { display: flex; align-items: center; gap: 20px; }
            
            /* Search Bar */
            .search-wrapper { position: relative; display: flex; align-items: center; width: 350px; }
            .search-input { width: 100%; padding: 10px 40px; font-size: 0.9rem; font-family: "Inter", sans-serif; border: 1px solid var(--border-color); border-radius: 30px; background: var(--bg-card); color: var(--text-primary); outline: none; transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .search-input::placeholder { color: var(--text-secondary); }
            .search-input:focus { box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-color: #5979aa; }
            .search-icon { position: absolute; left: 14px; font-size: 16px; opacity: 0.5; color: var(--text-primary); pointer-events: none; }
            .search-clear { position: absolute; right: 14px; font-size: 16px; cursor: pointer; opacity: 0; color: var(--text-secondary); display: none; }
            .search-clear.visible { opacity: 0.7; display: block; }

            /* --- Header Actions (Notifications & Profile) --- */
            .header-actions-container { display: flex; align-items: center; gap: 16px; }
            
            .icon-btn { 
                background: transparent; border: none; cursor: pointer; 
                color: #ffffff; position: relative; transition: 0.2s; 
                display: flex; align-items: center; justify-content: center; 
                width: 38px; height: 38px; border-radius: 50%; 
            }
            .dark-mode .icon-btn { color: var(--text-primary); }
            .icon-btn:hover { background: rgba(255,255,255,0.15); }
            .dark-mode .icon-btn:hover { background: var(--sidebar-hover); }
            .icon-btn svg { width: 20px; height: 20px; }
            .notif-badge { position: absolute; top: 6px; right: 8px; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; border: 1px solid var(--header-bg); }

            /* --- Custom Dropdowns --- */
            .dropdown-container { position: relative; }
            .notif-dropdown-menu {
                position: absolute; right: -50px; top: calc(100% + 12px);
                background: var(--bg-card); width: 380px; border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 1px solid var(--border-color);
                display: none; flex-direction: column; z-index: 100;
                animation: slideInDown 0.2s ease forwards;
            }
            .notif-dropdown-menu.show { display: flex; }
            .notif-header { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1px solid var(--border-color); padding: 0 16px; }
            .notif-tabs { display: flex; gap: 20px; }
            .notif-tab { padding: 14px 0 12px 0; font-size: 0.95rem; font-weight: 500; color: var(--text-secondary); cursor: pointer; border-bottom: 2px solid transparent; }
            .notif-tab.active { color: var(--text-primary); border-bottom-color: var(--text-primary); font-weight: 600; }
            .notif-actions { display: flex; gap: 16px; color: var(--text-secondary); font-size: 1.1rem; padding-bottom: 12px; }
            .notif-actions svg { width: 18px; height: 18px; cursor: pointer; transition: 0.2s; }
            .notif-actions svg:hover { color: var(--text-primary); }
            
            .notif-body { max-height: 400px; overflow-y: auto; scrollbar-width: thin; }
            .notif-item { display: flex; padding: 14px 16px; border-bottom: 1px solid var(--border-color); align-items: flex-start; cursor: pointer; transition: background 0.2s; }
            .notif-item:hover { background: var(--sidebar-hover); }
            .notif-unread-dot { color: #0f172a; font-size: 14px; margin-right: 12px; line-height: 1.5; opacity: 0; }
            .notif-item.unread .notif-unread-dot { opacity: 1; }
            .dark-mode .notif-unread-dot { color: #f8fafc; }
            
            .notif-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 14px; flex-shrink: 0; font-size: 0.9rem; }
            
            .notif-content { display: flex; flex-direction: column; flex-grow: 1; }
            .notif-subject { font-size: 0.9rem; color: var(--text-primary); line-height: 1.4; margin-bottom: 6px; }
            .notif-time { font-size: 0.8rem; color: var(--text-secondary); }

            /* --- Header Profile Dropdown --- */
            .header-avatar { 
                width: 38px; height: 38px; border-radius: 50%; cursor: pointer; 
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); color: #2d3748; 
                display: flex; align-items: center; justify-content: center; 
                font-weight: 700; overflow: hidden; border: 2px solid transparent; 
                transition: border-color 0.2s, box-shadow 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header-avatar img { width: 100%; height: 100%; object-fit: cover; }
            .header-avatar:hover { border-color: #ffffff; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
            
            .profile-dropdown-menu { 
                position: absolute; right: 0; top: calc(100% + 12px); 
                background: var(--bg-card); width: 220px; border-radius: 12px; 
                box-shadow: 0 10px 25px rgba(0,0,0,0.15); border: 1px solid var(--border-color); 
                display: none; flex-direction: column; z-index: 100; overflow: hidden; 
                animation: slideInDown 0.2s ease forwards;
            }
            @keyframes slideInDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
            .profile-dropdown-menu.show { display: flex; }
            .dropdown-header { padding: 16px; display: flex; flex-direction: column; background: var(--sidebar-hover); }
            #dd-user-name { font-weight: 600; color: var(--text-primary); font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            #dd-user-id { font-size: 0.75rem; color: var(--text-secondary); margin-top: 2px; }
            .dropdown-divider { height: 1px; background: var(--border-color); }
            .dropdown-item { 
                padding: 12px 16px; display: flex; align-items: center; gap: 12px; 
                background: transparent; border: none; width: 100%; text-align: left; 
                cursor: pointer; font-size: 0.85rem; font-weight: 500; 
                color: var(--text-primary); transition: 0.2s; font-family: "Inter", sans-serif;
            }
            .dropdown-item svg { width: 16px; height: 16px; opacity: 0.7; }
            .dropdown-item:hover { background: var(--sidebar-hover); }
            .dropdown-item:hover svg { opacity: 1; }
            .dropdown-item.text-danger { color: #ef4444; }
            .dropdown-item.text-danger svg { color: #ef4444; }
            .dropdown-item.text-danger:hover { background: #fef2f2; }
            .dark-mode .dropdown-item.text-danger:hover { background: rgba(239, 68, 68, 0.1); }

            /* --- Sidebar --- */
            .app-body { display: flex; flex-grow: 1; height: calc(100vh - 76px); position: relative; overflow: hidden; }
            .shishu-sidebar { width: 270px; background: var(--bg-sidebar); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; flex-shrink: 0; transition: width 0.3s ease, background 0.3s, border-color 0.3s; z-index: 10; }
            .shishu-sidebar.collapsed { width: 0px; border-right: none; overflow: hidden; }
            
            .sidebar-menu-container { flex: 1; padding: 20px 14px; overflow-y: auto; scrollbar-width: none; }
            .sidebar-menu-container::-webkit-scrollbar { width: 5px; }
            .sidebar-menu-container::-webkit-scrollbar-thumb { background: transparent; border-radius: 10px; }
            .shishu-sidebar:hover .sidebar-menu-container { scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.15) transparent; }
            .shishu-sidebar:hover .sidebar-menu-container::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); }

            .sidebar-menu { display: flex; flex-direction: column; gap: 8px; }
            .sidebar-item { padding: 10px 14px; text-decoration: none; color: var(--text-secondary); font-weight: 600; font-size: 0.81rem; border-radius: 8px; transition: all 0.2s ease; display: flex; align-items: center; gap: 12px; cursor: pointer; line-height: 1.35; }
            .sidebar-icon { font-size: 1.1rem; flex-shrink: 0; width: 24px; text-align: center; }
            .sidebar-item:hover { background: var(--sidebar-hover); color: var(--text-primary); }
            .sidebar-item.active { background: #5979aa; color: #ffffff; box-shadow: 0 2px 8px rgba(106, 139, 206, 0.3); }

            /* --- Sidebar Footer & Fixed Bottom Profile --- */
            .sidebar-footer { border-top: 1px solid var(--border-color); padding: 16px 14px; display: flex; flex-direction: column; gap: 16px; background: var(--bg-sidebar); flex-shrink: 0; transition: background 0.3s, border-color 0.3s; }
            .toggle-row { display: flex; align-items: center; justify-content: space-between; padding: 0 4px; }
            .toggle-label { font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; user-select: none; }
            .theme-switch { position: relative; width: 54px; height: 28px; flex-shrink: 0; cursor: pointer; }
            .theme-switch input { opacity: 0; width: 0; height: 0; position: absolute; }
            .theme-track { position: absolute; inset: 0; border-radius: 50px; background: #dde1ef; transition: background 0.4s; box-shadow: inset 0 1px 4px rgba(0,0,0,0.15); }
            .dark-mode .theme-track { background: #333333; }
            .theme-knob { position: absolute; top: 2px; left: 2px; width: 24px; height: 24px; border-radius: 50%; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.3s; }
            .dark-mode .theme-knob { transform: translateX(26px); background: #1a1a1a; }

            /* Fixed Bottom User Profile Panel */
            .sidebar-footer-profile {
                display: flex; align-items: center; padding: 12px;
                background: #f8fafc; border-radius: 12px; border: 1px solid #f1f5f9;
                cursor: pointer; transition: all 0.2s; gap: 12px;
            }
            .dark-mode .sidebar-footer-profile { background: #1e293b; border-color: #334155; }
            .sidebar-footer-profile:hover { border-color: #cbd5e1; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
            .sfp-avatar {
                width: 42px; height: 42px; border-radius: 50%;
                background: #5c72a6; color: white; display: flex;
                align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700;
                flex-shrink: 0;
            }
            .sfp-info { display: flex; flex-direction: column; overflow: hidden; }
            .sfp-name { font-size: 0.95rem; font-weight: 700; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .dark-mode .sfp-name { color: #f8fafc; }
            .sfp-role { font-size: 0.8rem; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
            .dark-mode .sfp-role { color: #94a3b8; }

            /* --- General Loading Spinner --- */
            .shishu-spinner {
                width: 40px; height: 40px; border: 4px solid var(--border-color);
                border-top: 4px solid var(--mgmt-icon-color); border-radius: 50%;
                animation: spin 1s linear infinite; margin: 0 auto 16px auto;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 200px; color: var(--text-secondary); font-weight: 500; font-size: 0.95rem; }

            /* --- Main Content Area Architecture (Fixed Double Scroll) --- */
            .main-content { flex-grow: 1; background: var(--bg-main); position: relative; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
            
            #view-dashboard { overflow-y: auto; flex-grow: 1; height: 100%; scrollbar-width: thin; }
            #view-dashboard::-webkit-scrollbar { width: 6px; } 
            #view-dashboard::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; }
            .dark-mode #view-dashboard::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); }
            
            #view-list { display: flex; flex-direction: column; height: 100%; width: 100%; overflow: hidden; }
            
            #view-detail { overflow-y: auto; display: flex; flex-direction: column; height: 100%; width: 100%; scrollbar-width: thin; }
            #view-detail::-webkit-scrollbar { width: 6px; } 
            #view-detail::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 10px; }
            .dark-mode #view-detail::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); }

            /* --- Grid Common --- */
            .grid-container { display: grid; gap: 20px; align-items: stretch; grid-template-columns: repeat(4, 1fr); padding: 24px 30px;}
            @media (max-width: 1450px) { .grid-container { grid-template-columns: repeat(3, 1fr); } }
            @media (max-width: 1050px) { .grid-container { grid-template-columns: repeat(2, 1fr); } }
            @media (max-width: 650px) { .grid-container { grid-template-columns: 1fr; } }
            .hidden-card { display: none !important; }
            .no-results { grid-column: 1 / -1; text-align: center; padding: 40px; margin: 24px 30px; background: var(--no-result-bg); color: var(--text-secondary); border-radius: 12px; box-shadow: var(--card-shadow); }

            /* --- The Report Menu CSS --- */
            .report-group-card { 
                height: 100%; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; 
                box-shadow: var(--card-shadow); border: 1px solid var(--border-card); 
                transition: transform 0.2s, box-shadow 0.2s, background 0.3s; position: relative; overflow: hidden; 
            }
            .report-group-card:nth-child(1) { background: linear-gradient(135deg, #f8fafc 0%, #FFB0AB 100%); }
            .report-group-card:nth-child(2) { background: linear-gradient(135deg, #f8fafc 0%, #77A7ED 100%); }
            .report-group-card:nth-child(3) { background: linear-gradient(135deg, #f8fafc 0%, #eef4f8 100%); }
            .report-group-card:nth-child(4) { background: linear-gradient(135deg, #f8fafc 0%, #52CC78 100%); }
            .report-group-card:nth-child(5) { background: linear-gradient(135deg, #ddeeff 0%, #d4e8f8 100%); }
            .report-group-card:nth-child(6) { background: linear-gradient(135deg, #e6f5e6 0%, #dff0df 100%); }
            .report-group-card:nth-child(7) { background: linear-gradient(135deg, #fdf3dc 0%, #faeecf 100%); }
            .report-group-card:nth-child(8) { background: linear-gradient(135deg, #fde8e8 0%, #fadede 100%); }
            .report-group-card:nth-child(9) { background: linear-gradient(135deg, #eef3fb 0%, #e5ecf5 100%); }
            .report-group-card:nth-child(10) { background: linear-gradient(135deg, #f3eeff 0%, #ece5fa 100%); }
            .report-group-card:nth-child(11) { background: linear-gradient(135deg, #D1ECFF 0%, #c5e2f8 100%); }
            .report-group-card:nth-child(12) { background: linear-gradient(135deg, #ffe8d9 0%, #ffddd0 100%); }

            .dark-mode .report-group-card, .dark-mode .report-group-card:nth-child(n) { background: #141414 !important; border-color: #262626 !important; }
            .report-group-card:hover { box-shadow: var(--card-hover-shadow); transform: translateY(-2px); }
            
            .group-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid var(--border-color); }
            .group-header-left { display: flex; align-items: center; gap: 10px; }
            .group-icon { font-size: 16px; background: rgba(255, 255, 255, 0.9); width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .dark-mode .group-icon { background: rgba(255,255,255,0.08); color: #fff; }
            .group-title { font-size: 0.88rem; font-weight: 700; color: var(--text-primary); transition: color 0.3s; }
            .header-sort-btn { padding: 4px 8px; font-size: 10px; font-weight: 700; border: 1px solid var(--border-color); border-radius: 20px; background: transparent; cursor: pointer; color: var(--text-secondary); transition: 0.3s; }
            .header-sort-btn:hover { background: var(--link-bg); color: var(--text-primary); }

            .group-links { display: flex; flex-direction: column; gap: 6px; max-height: 220px; overflow-y: auto; padding-right: 4px; scrollbar-width: none; }
            .group-links::-webkit-scrollbar { width: 5px; }
            .group-links::-webkit-scrollbar-thumb { background: transparent; border-radius: 10px; }
            .report-group-card:hover .group-links { scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.15) transparent; }
            .report-group-card:hover .group-links::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); }
            
            .report-link { display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: var(--link-bg); border-radius: 6px; text-decoration: none; color: var(--text-secondary); font-size: 0.78rem; font-weight: 500; transition: 0.2s; border: 1px solid transparent; }
            .report-link::before { content: "→"; font-size: 11px; opacity: 0.4; flex-shrink: 0; }
            .report-link:hover { background: var(--link-hover); border-color: var(--border-color); transform: translateX(3px); color: var(--text-primary); }

            /* --- The Management CSS --- */
            @keyframes slideInUp { 0% { opacity: 0; transform: translateY(15px); } 100% { opacity: 1; transform: translateY(0); } }

            .mgmt-card { 
                background: var(--mgmt-card-bg); border-radius: 14px; 
                border: 1px solid var(--border-card); 
                border-left: 5px solid var(--card-accent, #3b82f6);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); padding: 18px; 
                display: flex; flex-direction: column; gap: 14px; opacity: 0; 
                animation: slideInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; 
                transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
            }
            .mgmt-card:hover { 
                border-color: var(--card-accent, #3b82f6); 
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08); 
                transform: translateY(-4px); 
            }
            
            /* Dynamic Accents */
            .mgmt-card:nth-child(1n) { --card-accent: #3b82f6; --mgmt-icon-bg: #eff6ff; --mgmt-icon-color: #3b82f6; }
            .mgmt-card:nth-child(2n) { --card-accent: #10b981; --mgmt-icon-bg: #ecfdf5; --mgmt-icon-color: #10b981; }
            .mgmt-card:nth-child(3n) { --card-accent: #8b5cf6; --mgmt-icon-bg: #f5f3ff; --mgmt-icon-color: #8b5cf6; }
            .mgmt-card:nth-child(4n) { --card-accent: #f59e0b; --mgmt-icon-bg: #fffbeb; --mgmt-icon-color: #f59e0b; }
            .mgmt-card:nth-child(5n) { --card-accent: #ef4444; --mgmt-icon-bg: #fef2f2; --mgmt-icon-color: #ef4444; }
            .mgmt-card:nth-child(6n) { --card-accent: #06b6d4; --mgmt-icon-bg: #ecfeff; --mgmt-icon-color: #06b6d4; }
            .mgmt-card:nth-child(7n) { --card-accent: #ec4899; --mgmt-icon-bg: #fdf2f8; --mgmt-icon-color: #ec4899; }
            
            .dark-mode .mgmt-card:nth-child(1n) { --mgmt-icon-bg: rgba(59, 130, 246, 0.15); }
            .dark-mode .mgmt-card:nth-child(2n) { --mgmt-icon-bg: rgba(16, 185, 129, 0.15); }
            .dark-mode .mgmt-card:nth-child(3n) { --mgmt-icon-bg: rgba(139, 92, 246, 0.15); }
            .dark-mode .mgmt-card:nth-child(4n) { --mgmt-icon-bg: rgba(245, 158, 11, 0.15); }
            .dark-mode .mgmt-card:nth-child(5n) { --mgmt-icon-bg: rgba(239, 68, 68, 0.15); }
            .dark-mode .mgmt-card:nth-child(6n) { --mgmt-icon-bg: rgba(6, 182, 212, 0.15); }
            .dark-mode .mgmt-card:nth-child(7n) { --mgmt-icon-bg: rgba(236, 72, 153, 0.15); }

            .mgmt-card-header { display: flex; align-items: center; gap: 14px; padding-bottom: 12px; border-bottom: 1px dashed var(--border-color); }
            .mgmt-card-icon { width: 42px; height: 42px; border-radius: 10px; background: var(--mgmt-icon-bg); color: var(--mgmt-icon-color); display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
            .mgmt-card-title { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em; margin: 0; }
            
            .mgmt-actions-list { display: flex; flex-direction: column; gap: 8px; max-height: 250px; overflow-y: auto; padding-right: 4px; scrollbar-width: none; }
            .mgmt-actions-list::-webkit-scrollbar { width: 5px; }
            .mgmt-actions-list::-webkit-scrollbar-thumb { background: transparent; border-radius: 10px; }
            .mgmt-card:hover .mgmt-actions-list { scrollbar-width: thin; scrollbar-color: rgba(0,0,0,0.1) transparent; }
            .mgmt-card:hover .mgmt-actions-list::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); }

            .mgmt-action-btn { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; background: var(--mgmt-item-bg); border: 1px solid var(--mgmt-item-border); border-radius: 8px; text-decoration: none; transition: all 0.2s ease; cursor: pointer; }
            .mgmt-action-left { display: flex; align-items: center; gap: 12px; }
            .mgmt-action-icon { font-size: 16px; width: 20px; text-align: center; }
            .mgmt-action-text { color: var(--text-primary); font-size: 0.82rem; font-weight: 600; }
            .mgmt-action-chevron { color: var(--text-secondary); opacity: 0.4; font-size: 12px; transition: 0.2s; font-weight: bold; }

            .mgmt-action-btn:hover { background: var(--mgmt-item-hover); border-color: var(--mgmt-item-border-hover); box-shadow: 0 4px 10px rgba(59, 130, 246, 0.08); transform: translateX(2px); }
            .mgmt-action-btn:hover .mgmt-action-chevron { opacity: 1; color: var(--mgmt-icon-color); transform: translateX(3px); }

            /* --- Custom List & Detail View CSS --- */
            .cv-header-container { display: flex; justify-content: space-between; align-items: center; padding: 20px 30px; border-bottom: 1px solid var(--border-color); background: var(--bg-card); flex-shrink: 0; box-shadow: 0 1px 4px rgba(0,0,0,0.02);}
            .cv-left { display: flex; align-items: center; gap: 16px; min-width: 0; }
            .cv-right { display: flex; align-items: center; gap: 16px; }
            .cv-back-btn { background: var(--mgmt-item-bg); border: 1px solid var(--border-color); padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: 600; color: var(--text-primary); transition: 0.2s; font-family: "Inter", sans-serif; font-size: 0.85rem; flex-shrink: 0; }
            .cv-back-btn:hover { background: var(--border-color); }
            .cv-title { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
            
            /* Enhanced Dynamic Filters */
            .filter-control { display: flex; flex-direction: column; flex: 1; min-width: 140px; max-width: 200px; }
            .filter-control .frappe-control { margin: 0; }
            .filter-control .frappe-control .help-box,
            .filter-control .frappe-control .control-label { display: none; }
            
            /* SOLID AND CLEAN FILTER INPUTS */
            .filter-select, .filter-input, .filter-control .frappe-control input, .cv-filter-input, .cv-select { 
                background: #ffffff !important; 
                border: 1px solid #d1d5db !important; 
                color: #111827 !important; 
                font-family: "Inter", sans-serif !important; 
                font-size: 0.85rem !important; 
                font-weight: 500 !important;
                outline: none !important; 
                transition: 0.2s !important; 
                border-radius: 8px !important; 
                padding: 10px 14px !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; 
                height: 38px !important; 
            }
            .dark-mode .filter-select, .dark-mode .filter-input, .dark-mode .filter-control .frappe-control input, .dark-mode .cv-filter-input, .dark-mode .cv-select { 
                background: #141414 !important; 
                border-color: var(--border-color) !important;
                color: #f9fafb !important;
            }
            .filter-select:focus, .filter-input:focus, .filter-control .frappe-control input:focus, .cv-filter-input:focus, .cv-select:focus { 
                box-shadow: 0 0 0 2px var(--mgmt-icon-color) !important; 
                border-color: var(--mgmt-icon-color) !important;
            }

            .cv-btn { padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; font-family: "Inter", sans-serif; font-size: 0.85rem; transition: background 0.2s, transform 0.1s;}
            .cv-btn.primary { background: var(--mgmt-icon-color); color: white; box-shadow: 0 2px 5px rgba(59, 130, 246, 0.3); }
            .cv-btn.primary:hover { background: #2563eb; transform: translateY(-1px); }
            .cv-btn.secondary { background: #e2e8f0; color: var(--text-primary); border: 1px solid var(--border-color); }
            .cv-btn.secondary:hover { background: #cbd5e1; }
            .dark-mode .cv-btn.primary { background: #3b82f6; color: white; }
            .dark-mode .cv-btn.primary:hover { background: #2563eb; }
            .dark-mode .cv-btn.secondary { background: #1f1f1f; color: #fff; border-color: var(--border-color); }
            .dark-mode .cv-btn.secondary:hover { background: #333333; }

            /* Footer for Limit Settings */
            .cv-footer-container {display: flex;justify-content: flex-end;align-items: center;gap: 8px;padding: 8px 20px; border-top: 1px solid var(--border-color); background: var(--bg-card); flex-shrink: 0; margin-top: auto;}
            .cv-footer-label {font-size: 0.75rem; line-height: 1.2;color: var(--text-secondary);font-weight: 500;}

            /* --- Data Table Enhancements & Sticky Header --- */
            .cv-body { flex-grow: 1; overflow: hidden; display: flex; flex-direction: column; background: var(--bg-main); min-height: 0; width: 100%; -webkit-overflow-scrolling: touch; }
            
            .custom-table-wrapper { 
                overflow: auto; 
                flex-grow: 1; 
                padding: 0 30px 24px 30px; 
                scrollbar-width: thin;
                min-height: 0;
                width: 100%;
                -webkit-overflow-scrolling: touch;
            }
            .custom-table-wrapper::-webkit-scrollbar { width: 6px; height: 6px; }
            .custom-table-wrapper::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 10px; }
            .dark-mode .custom-table-wrapper::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); }

            .custom-table { width: 100%; border-collapse: separate; border-spacing: 0 10px; text-align: left; }
            
            .custom-table th { 
                position: sticky; 
                top: 0; 
                z-index: 5; /* Lowered to 5 to prevent it from overlapping Awesomplete */
                background-color: var(--header-bg);
                color: white; 
                font-weight: 600; 
                padding: 12px 20px; 
                font-size: 0.85rem; 
                border-bottom: none; 
                white-space: nowrap; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
            }
            .custom-table th:first-child { border-top-left-radius: 8px; border-bottom-left-radius: 8px; }
            .custom-table th:last-child { border-top-right-radius: 8px; border-bottom-right-radius: 8px; }

            .custom-table tbody tr { background: var(--bg-card); box-shadow: 0 2px 6px rgba(0,0,0,0.03); border-radius: 12px; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
            .custom-table tbody tr:hover { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.06); }
            .custom-table td { padding: 16px 20px; font-size: 0.9rem; color: var(--text-primary); border-top: 1px solid var(--border-card); border-bottom: 1px solid var(--border-card); background: var(--bg-card); white-space: nowrap; }
            .custom-table td:first-child { border-left: 1px solid var(--border-card); border-top-left-radius: 12px; border-bottom-left-radius: 12px; }
            .custom-table td:last-child { border-right: 1px solid var(--border-card); border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
            .dark-mode .custom-table tbody tr { background: #141414; border-color: var(--border-color); box-shadow: 0 2px 6px rgba(0,0,0,0.4); }
            .dark-mode .custom-table td { background: #141414; border-color: var(--border-color); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color);}
            .dark-mode .custom-table td:first-child { border-left: 1px solid var(--border-color); }
            .dark-mode .custom-table td:last-child { border-right: 1px solid var(--border-color); }

            /* Checkbox Row Selecting */
            input[type="checkbox"].row-select-chk, input[type="checkbox"]#select-all-rows {
                width: 16px; height: 16px; cursor: pointer;
            }

            /* --- Child Table Box Layout (FIXED FOR SCROLLING) --- */
            .child-table-box { width: 100%; border: 1px solid var(--border-color); border-radius: 8px; overflow-x: auto; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
            .box-table { width: 100%; min-width: 600px; border-collapse: collapse; text-align: left; background: var(--bg-card); white-space: nowrap; }
            .box-table th { background: #f3f4f6; color: var(--text-primary); padding: 10px 14px; font-size: 0.8rem; font-weight: 600; border-bottom: 1px solid var(--border-color); border-right: 1px solid var(--border-color); }
            .box-table td { padding: 10px 14px; font-size: 0.85rem; border-bottom: 1px solid var(--border-color); border-right: 1px solid var(--border-color); color: var(--text-primary); }
            .box-table th:last-child, .box-table td:last-child { border-right: none; }
            .box-table tr:last-child td { border-bottom: none; }
            .dark-mode .box-table th { background: #1a1a1a; border-color: var(--border-color); }
            .dark-mode .box-table td, .dark-mode .child-table-box { border-color: var(--border-color); }

            /* Tabs */
            .cv-tabs { display: flex; gap: 16px; padding: 0 30px; border-bottom: 1px solid var(--border-color); background: var(--bg-card); overflow-x: auto; flex-shrink: 0; }
            .cv-tab { padding: 14px 4px; font-size: 0.9rem; font-weight: 600; color: var(--text-secondary); cursor: pointer; border-bottom: 2px solid transparent; transition: 0.2s; white-space: nowrap; user-select: none;}
            .cv-tab:hover { color: var(--text-primary); }
            .cv-tab.active { color: var(--mgmt-icon-color); border-bottom-color: var(--mgmt-icon-color); }
            
            /* Modernized Detail Page Form Grid */
            .form-section-card { 
                background: var(--bg-card); 
                border-radius: 16px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.04); 
                margin: 24px 30px; 
                padding: 32px; 
                border: none;
                transition: box-shadow 0.2s ease;
            }
            .form-section-card:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.06); }
            .dark-mode .form-section-card { box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
            
            .section-heading { 
                font-size: 1.25rem; font-weight: 700; color: var(--text-primary); 
                margin: 0 0 24px 0; padding-bottom: 12px; border-bottom: 2px solid var(--border-color); 
                font-family: "Inter", sans-serif; 
            }
            
            .form-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; border: none !important; }
            .form-field { display: flex; flex-direction: column; gap: 8px; }
            .form-field.full-width { grid-column: 1 / -1; }
            
            .form-label { 
                font-size: 0.8rem; font-weight: 800; color: var(--text-primary); letter-spacing: 0.03em;
            }
            .form-value { 
                font-size: 0.95rem; color: #6b7280; padding: 12px 16px; 
                background: #f9fafb; border-radius: 10px; border: none; 
                min-height: 46px; word-break: break-word; font-weight: 500; 
            }
            .dark-mode .form-label { color: #f8fafc; }
            .dark-mode .form-value { color: #9ca3af; background: #0a0a0a; }
            
            .link-val { color: var(--mgmt-icon-color); font-weight: 600; text-decoration: underline; cursor: pointer; }

            /* Mobile Overlay */
            .mobile-overlay { position: absolute; inset: 0; background: rgba(0, 0, 0, 0.5); z-index: 15; display: none; opacity: 0; transition: opacity 0.3s; }

            @media (max-width: 900px) {
                .top-header { padding: 0 16px; height: 66px; }
                .app-body { height: calc(100vh - 66px); }
                .shishu-sidebar { position: absolute; top: 0; left: 0; height: 100%; z-index: 20; transform: translateX(-100%); width: 280px; box-shadow: none; }
                .shishu-sidebar.mobile-open { transform: translateX(0); box-shadow: 4px 0 15px rgba(0,0,0,0.4); }
                .mobile-overlay.visible { display: block; opacity: 1; }
                .cv-header-container { flex-direction: column; align-items: stretch; gap: 16px; padding: 16px 20px; }
                .cv-left, .cv-right { width: 100%; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
                .cv-btn, .cv-filter-input { flex-grow: 1; }
                #list-dynamic-filters { padding: 12px 20px 10px 20px !important; display: grid !important; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
                .filter-control { min-width: 0 !important; max-width: 100% !important; flex-shrink: 1; }
                .custom-table-wrapper { padding: 0 20px 24px 20px; min-height: 0; }
                .form-section-card { margin: 16px 20px; padding: 16px; }
                .section-heading { margin: 0 0 16px 0; }
                .cv-tabs { padding: 0 20px; }
                .no-results { margin: 16px 20px; }
                .search-wrapper { width: 220px; }
            }
            @media (max-width: 600px) {
                .form-grid { grid-template-columns: 1fr; } /* Force 1 column on mobile forms */
            }
            @media (max-width: 580px) {
                .brand-name { flex-direction: column; gap: 0px; }
                .brand-subtitle, .search-wrapper { display: none; }
                .header-actions-container { margin-left: auto; }
                .brand-en { font-size: 16px; white-space: normal; line-height: 1.2; }
                .brand-hi { font-size: 13px; white-space: normal; }
                .brand-logo { height: 44px; width: 44px; }
            }
        </style>

        <div class="shishu-app-container" id="app-container">
            <header class="top-header">
                <div class="header-left">
                    <button class="sidebar-toggle-btn" id="sidebar-toggle">☰</button>
                    <div class="brand-section" style="cursor: pointer;" onclick="window.location.href='/app/home'">
                        <img src="/files/logo_1.png" alt="Logo" class="brand-logo" onerror="this.src='https://frappe.io/files/frappe-framework-logo.svg'">
                        <div class="brand-text">
                            <div class="brand-name"><span class="brand-en">Shishughar Management System</span></div>
                        </div>
                    </div>
                </div>
                
                <div class="header-right">
                    <div class="search-wrapper">
                        <input type="text" id="report-search-local" class="search-input" placeholder="Search menus & reports..." autocomplete="off">
                        <span class="search-icon">🔍</span>
                        <span class="search-clear" id="search-clear-btn">✕</span>
                    </div>

                    <div class="header-actions-container">
                        
                        <div class="dropdown-container">
                            <button class="icon-btn" id="header-notification-btn" title="Notifications">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                                <div class="notif-badge" style="display:none;" id="notif-badge"></div>
                            </button>
                            
                            <div class="notif-dropdown-menu" id="notif-dropdown-menu">
                                <div class="notif-header">
                                    <div class="notif-tabs">
                                        <span class="notif-tab active">Notifications</span>
                                        <span class="notif-tab">Today's Events</span>
                                    </div>
                                    <div class="notif-actions">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" title="Mark all as read" id="mark-all-read-btn"><polyline points="20 6 9 17 4 12"></polyline></svg>
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" title="Settings" id="notif-settings-btn"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                                    </div>
                                </div>
                                <div class="notif-body" id="notif-list-container">
                                    <div style="padding: 20px; text-align: center; color: var(--text-secondary);">Loading...</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dropdown-container">
                            <div class="header-avatar" id="header-avatar-btn" title="Profile Menu"></div>
                            
                            <div class="profile-dropdown-menu" id="profile-dropdown-menu">
                                <div class="dropdown-header">
                                    <span id="dd-user-name">Loading...</span>
                                    <span id="dd-user-id">Loading...</span>
                                </div>
                                <div class="dropdown-divider"></div>
                                <button class="dropdown-item" id="btn-my-profile">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                                    My Profile
                                </button>
                                <button class="dropdown-item text-danger" id="btn-logout">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                                    Log out
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <div class="app-body">
                <div class="mobile-overlay" id="mobile-overlay"></div>
                
                <nav class="shishu-sidebar" id="app-sidebar">
                    <div class="sidebar-menu-container">
                        <div class="sidebar-menu">
                            <div class="sidebar-item active" data-target="report-menu" data-workspace="Reports View" style="display: none;"><span class="sidebar-icon">📊</span> Report Menu</div>
                            <div class="sidebar-item" data-target="creche-management" data-workspace="Creche Management System" style="display: none;"><span class="sidebar-icon">🏡</span> Creche Management System</div>
                            <div class="sidebar-item" data-target="organization-menu" data-workspace="Organization Menu" style="display: none;"><span class="sidebar-icon">🏢</span> Organization Menu</div>
                            <div class="sidebar-item" data-target="cc-menu" data-workspace="CC Menu" style="display: none;"><span class="sidebar-icon">👮</span> CC Menu</div>
                            <div class="sidebar-item" data-target="cs-menu" data-workspace="CS Menu" style="display: none;"><span class="sidebar-icon">👷‍♂️</span> CS Menu</div>
                            <div class="sidebar-item" data-target="accounts-management" data-workspace="Accounts Management" style="display: none;"><span class="sidebar-icon">🪙</span> Accounts Management</div>
                            <div class="sidebar-item" data-target="capacity-building" data-workspace="Capacity Building Manager" style="display: none;"><span class="sidebar-icon">🏦</span> Capacity Building Manager</div>
                            <div class="sidebar-item" data-target="safety-menu" data-workspace="Safety Menu" style="display: none;"><span class="sidebar-icon">🛡️</span> Safety Menu</div>
                        </div>
                    </div>

                    <div class="sidebar-footer">
                        <div class="toggle-row">
                            <span class="toggle-label"><span id="mode-icon">☀️</span> <span id="mode-text">Day Mode</span></span>
                            <label class="theme-switch">
                                <input type="checkbox" id="theme-checkbox">
                                <div class="theme-track"></div>
                                <div class="theme-knob" id="theme-knob">☀️</div>
                            </label>
                        </div>
                        
                        <div class="sidebar-footer-profile" id="sidebar-bottom-profile">
                            <div class="sfp-avatar" id="sfp-avatar-img">A</div>
                            <div class="sfp-info">
                                <div class="sfp-name" id="sfp-user-name">Administrator</div>
                                <div class="sfp-role" id="sfp-user-role">Administrator</div>
                            </div>
                        </div>
                    </div>
                </nav>

                <main class="main-content">
                    
                    <div id="view-dashboard" style="display: block;">
                        <div class="grid-container" id="card-container"></div>
                        <div class="no-results" id="no-results" style="display: none;">
                            <span>🔎</span>
                            <p>No results found matching "<span id="search-term"></span>"</p>
                        </div>
                    </div>

                    <div id="view-list" style="display: none;">
                        <div class="cv-header-container">
                            <div class="cv-left">
                                <button class="cv-back-btn" id="list-back-btn">← Back</button>
                                <h2 class="cv-title" id="list-title">Loading...</h2>
                            </div>
                            <div class="cv-right">
                                <input type="text" id="list-quick-filter" class="cv-filter-input" placeholder="🔍 Search this list...">
                                <button class="cv-btn primary" id="list-create-btn">+ New</button>
                                <button class="cv-btn secondary" id="list-export-btn" title="Export to Excel">⬇ Export</button>
                                <button class="cv-btn secondary" id="list-refresh-btn" title="Refresh">↻</button>
                                
                                <div class="dropdown-container">
                                    <button class="cv-btn secondary" id="list-sort-btn" style="display:flex; align-items:center; gap:6px;">
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><polyline points="19 12 12 19 5 12"></polyline></svg>
                                        <span id="current-sort-label">Last Updated On</span>
                                    </button>
                                    <div class="profile-dropdown-menu" id="sort-menu" style="width: 250px; top: 100%; right: 0;">
                                        <button class="dropdown-item" data-sort="modified desc">Last Updated On (Newest)</button>
                                        <button class="dropdown-item" data-sort="modified asc">Last Updated On (Oldest)</button>
                                        <button class="dropdown-item" data-sort="name asc">Name/ID (A-Z)</button>
                                        <button class="dropdown-item" data-sort="name desc">Name/ID (Z-A)</button>
                                        <button class="dropdown-item" data-sort="creation desc">Created On</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Fixed Filter Wrapper Layering (z-index: 20) -->
                        <div id="list-dynamic-filters" style="display: flex; gap: 16px; padding: 20px 30px 0 30px; flex-wrap: wrap; background: var(--bg-main); position: relative; z-index: 20;"></div>
                        
                        <div class="cv-body" id="list-table-container"></div>
                        
                        <div class="cv-footer-container">
                            <span class="cv-footer-label">Records per page: </span>
                            <select id="list-limit-select" class="cv-select"></select>
                        </div>
                    </div>

                    <div id="view-detail" style="display: none;">
                        <div class="cv-header-container">
                            <div class="cv-left">
                                <button class="cv-back-btn" id="detail-back-btn">← Back to List</button>
                                <h2 class="cv-title" id="detail-title">Loading...</h2>
                            </div>
                            <div class="cv-right">
                                <button class="cv-btn primary" id="detail-edit-btn">✏️ Edit</button>
                            </div>
                        </div>
                        <div class="cv-tabs" id="detail-tabs-container"></div>
                        <div class="cv-body" id="detail-body-container" style="overflow-y: auto;"></div>
                    </div>

                </main>
            </div>
        </div>
    `);

    // ==========================================
    // 3. INJECT JAVASCRIPT LOGIC
    // ==========================================
    (function () {
        'use strict';

        // --- CENTRALIZED CONFIGURATION ---
        const SHISHU_CONFIG = {
            limits: [20, 50, 100, 300, 500, 1000, 999999], // Added 999999 for 'All'
            defaultLimit: 100,
            doctypes: {
                'Creche': { filters: [['docstatus', '<', 2]] },
                'Child Profile': { filters: [['docstatus', '<', 2]] },
                'Household Form': { filters: [] }
            }
        };

        const wrapperEl = wrapper;
        const appContainer = wrapperEl.querySelector('#app-container');
        const container = wrapperEl.querySelector('#card-container');

        // --- Helper to format Nutrition values into colored badges ---
        function formatNutritionStatus(val) {
            if (val == null || val === '') return '';
            let num = parseFloat(val);

            if (num === 3) return '<span style="color: #059669; font-weight: 700; background: #d1fae5; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; border: 1px solid #10b981;">Normal</span>';
            if (num === 2) return '<span style="color: #d97706; font-weight: 700; background: #fef3c7; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; border: 1px solid #f59e0b;">Moderate</span>';
            if (num === 1) return '<span style="color: #dc2626; font-weight: 700; background: #fee2e2; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; border: 1px solid #ef4444;">Severe</span>';

            return val;
        }

        // --- Helper to format Table MultiSelect values into neat badges ---
        function formatMultiSelect(val, df) {
            if (!val) return '';
            let items = [];
            let targetDoctype = df ? (df.multiselectlink || null) : null;

            if (Array.isArray(val)) {
                if (val.length === 0) return '';
                if (!targetDoctype && df && df.options) {
                    let childMeta = frappe.get_meta(df.options);
                    if (childMeta) {
                        let linkField = childMeta.fields.find(f => f.fieldtype === 'Link');
                        if (linkField) targetDoctype = linkField.options;
                    }
                }

                let validKeys = Object.keys(val[0]).filter(k => !['name', 'owner', 'creation', 'modified', 'modified_by', 'parent', 'parentfield', 'parenttype', 'idx', 'docstatus'].includes(k));
                if (validKeys.length > 0) {
                    let linkKey = validKeys[0];
                    if (df && df.options) {
                        let childMeta = frappe.get_meta(df.options);
                        if (childMeta) {
                            let linkField = childMeta.fields.find(f => f.fieldtype === 'Link');
                            if (linkField) linkKey = linkField.fieldname;
                        }
                    }
                    items = val.map(v => v[linkKey]).filter(Boolean);
                }
            } else if (typeof val === 'string') {
                items = val.split(',').map(v => v.trim()).filter(Boolean);
            }

            return items.map(item => {
                let baseStyle = 'display:inline-block; background: #f1f5f9; border: 1px solid #cbd5e1; color: #334155; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; margin: 2px 4px 2px 0; font-weight: 500;';
                if (targetDoctype) {
                    return `<span class="async-link-val multiselect-badge" style="${baseStyle}" data-doctype="${targetDoctype}" data-val="${item}">${item}</span>`;
                }
                return `<span class="multiselect-badge" style="${baseStyle}">${item}</span>`;
            }).join('');
        }

        // --- Core Interactions ---
        const sidebar = wrapperEl.querySelector('#app-sidebar');
        const toggleBtn = wrapperEl.querySelector('#sidebar-toggle');
        const overlay = wrapperEl.querySelector('#mobile-overlay');

        if (toggleBtn && sidebar && overlay) {
            toggleBtn.addEventListener('click', () => {
                if (window.innerWidth <= 900) {
                    sidebar.classList.toggle('mobile-open'); overlay.classList.toggle('visible');
                } else {
                    sidebar.classList.toggle('collapsed');
                }
            });
            overlay.addEventListener('click', () => {
                sidebar.classList.remove('mobile-open'); overlay.classList.remove('visible');
            });
        }

        // --- Theme Logic ---
        const themeCheckbox = wrapperEl.querySelector('#theme-checkbox');
        let savedTheme = localStorage.getItem('shishu_theme') || 'light';
        applyTheme(savedTheme);

        if (themeCheckbox) {
            themeCheckbox.addEventListener('change', () => {
                applyTheme(appContainer.classList.contains('dark-mode') ? 'light' : 'dark');
            });
        }

        function applyTheme(theme) {
            const isDark = theme === 'dark';
            appContainer.classList.toggle('dark-mode', isDark);
            if (themeCheckbox) themeCheckbox.checked = isDark;
            wrapperEl.querySelector('#mode-icon').textContent = isDark ? '🌙' : '☀️';
            wrapperEl.querySelector('#theme-knob').textContent = isDark ? '🌙' : '☀️';
            wrapperEl.querySelector('#mode-text').textContent = isDark ? 'Night Mode' : 'Day Mode';
            localStorage.setItem('shishu_theme', theme);
        }

        // --- GLOBAL USER IDENTIFICATION ---
        const uid = frappe.session.user || 'Guest';
        const info = frappe.boot && frappe.boot.user_info && frappe.boot.user_info[uid];
        const fullName = (info && info.full_name) ? info.full_name : uid;
        const img = info && info.image;
        const userInitial = fullName.charAt(0).toUpperCase();

        function initBottomProfile() {
            const avatarDiv = wrapperEl.querySelector('#sfp-avatar-img');
            avatarDiv.innerHTML = img ? `<img src="${img}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">` : userInitial;
            wrapperEl.querySelector('#sfp-user-name').textContent = fullName;
            wrapperEl.querySelector('#sfp-user-role').textContent = uid === 'Administrator' ? 'Administrator' : uid;

            wrapperEl.querySelector('#sidebar-bottom-profile').addEventListener('click', () => {
                if (uid !== 'Guest') frappe.set_route('user', uid);
            });
        }
        initBottomProfile();

        function initHeaderProfile() {
            const avatarBtn = wrapperEl.querySelector('#header-avatar-btn');
            avatarBtn.innerHTML = img ? `<img src="${img}">` : `<span>${userInitial}</span>`;

            wrapperEl.querySelector('#dd-user-name').textContent = fullName;
            wrapperEl.querySelector('#dd-user-id').textContent = uid;

            const profileDropdown = wrapperEl.querySelector('#profile-dropdown-menu');
            avatarBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                profileDropdown.classList.toggle('show');
                wrapperEl.querySelector('#notif-dropdown-menu').classList.remove('show');
            });

            wrapperEl.querySelector('#btn-my-profile').addEventListener('click', () => {
                if (uid !== 'Guest') frappe.set_route('user', uid);
            });

            wrapperEl.querySelector('#btn-logout').addEventListener('click', () => {
                frappe.app.logout();
            });
        }
        initHeaderProfile();

        function initNotificationDropdown() {
            const notifBtn = wrapperEl.querySelector('#header-notification-btn');
            const notifDropdown = wrapperEl.querySelector('#notif-dropdown-menu');
            const notifListContainer = wrapperEl.querySelector('#notif-list-container');
            const badge = wrapperEl.querySelector('#notif-badge');

            notifBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isShowing = notifDropdown.classList.toggle('show');
                wrapperEl.querySelector('#profile-dropdown-menu').classList.remove('show');
                if (isShowing) fetchNotifications();
            });

            wrapperEl.querySelector('#notif-settings-btn').addEventListener('click', () => {
                frappe.set_route('Form', 'Notification Settings', frappe.session.user);
            });
            wrapperEl.querySelector('#mark-all-read-btn').addEventListener('click', () => {
                frappe.call({
                    method: 'frappe.client.set_value',
                    args: { doctype: 'Notification Log', name: '*', fieldname: 'read', value: 1 },
                    callback: function () { fetchNotifications(); }
                });
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('.dropdown-container')) {
                    notifDropdown.classList.remove('show');
                    wrapperEl.querySelector('#profile-dropdown-menu').classList.remove('show');
                }
            });

            function timeAgo(dateString) {
                const date = new Date(dateString);
                const seconds = Math.floor((new Date() - date) / 1000);
                let interval = seconds / 2592000;
                if (interval > 1) return Math.floor(interval) + " month" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
                interval = seconds / 86400;
                if (interval > 1) return Math.floor(interval) + " day" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
                interval = seconds / 3600;
                if (interval > 1) return Math.floor(interval) + " hour" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
                interval = seconds / 60;
                if (interval > 1) return Math.floor(interval) + " minute" + (Math.floor(interval) > 1 ? "s" : "") + " ago";
                return "Just now";
            }

            function fetchNotifications() {
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: { doctype: 'Notification Log', fields: ['name', 'subject', 'from_user', 'creation', 'read', 'document_type', 'document_name'], limit_page_length: 10, order_by: 'creation desc' },
                    callback: function (r) {
                        if (!r.message || r.message.length === 0) {
                            notifListContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No new notifications</div>';
                            badge.style.display = 'none';
                            return;
                        }

                        let unreadCount = r.message.filter(n => !n.read).length;
                        badge.style.display = unreadCount > 0 ? 'block' : 'none';

                        notifListContainer.innerHTML = r.message.map(n => {
                            let init = n.from_user ? n.from_user.substring(0, 2).toUpperCase() : 'NA';
                            let avatarColor = n.read ? '#94a3b8' : '#e7a88e';
                            let avatarBg = n.read ? '#f1f5f9' : '#fef3eb';

                            return `
                                <div class="notif-item ${n.read ? 'read' : 'unread'}" data-doc="${n.document_type || ''}" data-name="${n.document_name || ''}" data-log="${n.name}">
                                    <div class="notif-unread-dot">●</div>
                                    <div class="notif-avatar" style="background:${avatarBg}; color:${avatarColor};">${init}</div>
                                    <div class="notif-content">
                                        <div class="notif-subject">${n.subject}</div>
                                        <div class="notif-time">${timeAgo(n.creation)}</div>
                                    </div>
                                </div>
                            `;
                        }).join('');

                        notifListContainer.querySelectorAll('.notif-item').forEach(item => {
                            item.addEventListener('click', (e) => {
                                const dt = e.currentTarget.dataset.doc;
                                const dn = e.currentTarget.dataset.name;
                                const logName = e.currentTarget.dataset.log;

                                frappe.call({ method: 'frappe.client.set_value', args: { doctype: 'Notification Log', name: logName, fieldname: 'read', value: 1 } });

                                if (dt && dn) frappe.set_route('Form', dt, dn);
                                else frappe.set_route('List', 'Notification Log');

                                notifDropdown.classList.remove('show');
                            });
                        });
                    }
                });
            }
            fetchNotifications();
        }
        initNotificationDropdown();

        // --- REPORT & MANAGEMENT RENDER DATA ---
        let allCards = [];
        const searchInput = wrapperEl.querySelector('#report-search-local');
        const searchClearBtn = wrapperEl.querySelector('#search-clear-btn');
        const noResultsDiv = wrapperEl.querySelector('#no-results');

        const reportData = {
            "Report Card": [{ name: "Creche Report Card", url: "/app/creche_report_card" }, { name: "Growth Monitoring Child", url: "/app/growth-monitoring-ch" }, { name: "HR Dashboard", url: "/app/hr-dashboard" }],
            "Enrollment Reports": [{ name: "Enrollment Cumulative Report", url: "/app/query-report/Enrollment%20Cumulative%20Report" }, { name: "Enrollment Current Report", url: "/app/query-report/Enrollment%20Current%20Report" }],
            "Malnutrition Prevalance Reports": [{ name: "Malnutrition prevalance report (Summary)", url: "/app/query-report/Malnutrition%20prevalance%20report%20(Summary)" }, { name: "Malnutrition prevalance report (Childwise)", url: "/app/query-report/Malnutrition%20prevalance%20report%20(Childwise)" }, { name: "Attendance Correlation Childwise", url: "/app/query-report/Attendance%20Corelation%20Childwise" }],
            "Attendance Reports": [{ name: "Average Attendance Summary", url: "/app/query-report/Average%20Attendance%20Summary" }, { name: "Average Attendance Child Wise", url: "/app/query-report/Average%20Attendance%20Child%20Wise" }, { name: "Attendance Gap", url: "/app/query-report/Attendance%20Gap" }],
            "Cohort Reports": [{ name: "Cohort Summary", url: "/app/query-report/Cohort%20Summary" }, { name: "Cohort Child Wise", url: "/app/query-report/Cohort%20Child%20Wise" }, { name: "Cohort Exited and Graduated", url: "/app/query-report/Cohort%20Exited%20and%20Graduated" }, { name: "Cohort Report (Creche Performance - Summary)", url: "/app/query-report/Cohort%20Report%20(Creche%20Performance%20-%20Summary)" }, { name: "Cohort Report (Creche Performance - Individual)", url: "/app/query-report/Cohort%20Report%20(Creche%20Performance%20-%20Individual)" }],
            "Check-in Reports": [{ name: "Check-in Report (Cadrewise)", url: "/app/query-report/Check-in%20Report%20(Cadrewise)" }, { name: "Check-in Report (Summary)", url: "/app/query-report/Checkin%20Report%20(Summary)" }, { name: "Check-in Report Individual", url: "/app/query-report/Checkin%20Report%20Individual" }],
            "Safety Checklist": [{ name: "Safety (Cumulative)", url: "/app/query-report/Safety%20(Cumulative)" }, { name: "Safety (Individual)", url: "/app/query-report/Safety%20(Individual)" }],
            "Other Reports": [{ name: "Daily Creche Attendance Activity", url: "/app/query-report/Daily%20Creche%20Attendance%20Activity" }, { name: "Active Children Report", url: "/app/query-report/Active%20Children%20Report" }, { name: "Creche Attendance", url: "/app/query-report/Creche%20Attendance" }, { name: "Child Exit", url: "/app/query-report/Child%20Exit" }, { name: "Creche Committee Meeting", url: "/app/query-report/Creche%20Committee%20Meeting" }, { name: "Creche Opening Report", url: "/app/query-report/Creche%20Opening%20Report" }, { name: "Daily Attendance Child Wise", url: "/app/query-report/Daily%20Attendance%20Child%20Wise" }, { name: "Daily Attendance Creche Wise", url: "/app/query-report/Daily%20Attendance%20Creche%20Wise" }, { name: "Daily Creche Attendance", url: "/app/query-report/Daily%20Creche%20Attendance" }, { name: "Daily Meal Tracker", url: "/app/query-report/Daily%20Meal%20Tracker" }, { name: "Enrollment Report", url: "/app/query-report/Enrollment%20Report" }, { name: "Enrollment Summary Report", url: "/app/query-report/Enrollment%20Summary%20Report" }, { name: "Govt Linkage Report", url: "/app/query-report/Govt%20Linkage%20Report" }, { name: "Household Details", url: "/app/query-report/Household%20Details" }, { name: "Immunization Over all", url: "/app/query-report/Immunization%20Over%20all" }, { name: "Meals at Creche", url: "/app/query-report/Meals%20at%20Creche" }, { name: "Monthly Meal Tracker", url: "/app/query-report/Monthly%20Meal%20Tracker" }, { name: "Visit Report", url: "/app/query-report/Visit%20Report" }, { name: "Cashbook Import", url: "/app/query-report/Cashbook%20Import" }, { name: "Growth Monitoring Summary", url: "/app/query-report/Growth%20Monitoring%20Summary" }, { name: "Growth Monitoring Child wise", url: "/app/query-report/Growth%20Monitoring%20Child%20wise" }, { name: "Growth Monitoring Child wise (Z Score)", url: "/app/query-report/Growth%20Monitoring%20Child%20wise%20(Z%20Score)" }],
            "Creche Profile Reports": [{ name: "Gram Sabha Resolution Report", url: "/app/query-report/Gram%20Sabha%20Resolution%20Report" }, { name: "CMC Meeting", url: "/app/query-report/CMC%20Meeting" }],
            "Beta version Reports": [{ name: "MIS Dashboard", url: "/app/mis_dashboard" }, { name: "Enrollment & Exit Report", url: "/app/query-report/Enrollment%20%26%20Exit%20Report" }, { name: "Cashbook Report", url: "/app/query-report/Stock%20Report" }],
            "Release Notes": [{ name: "Release Notes", url: "/releasenotes" }],
            "MIS Dashboard": [{ name: "MIS Dashboard V2", url: "/app/mis-attendances-dash" }]
        };
        const categoryIcons = {
            "Report Card": "📋", "Enrollment Reports": "📊", "Malnutrition Prevalance Reports": "📉",
            "Attendance Reports": "📅", "Cohort Reports": "👥", "Check-in Reports": "📍",
            "Safety Checklist": "✅", "Other Reports": "📁", "Creche Profile": "📜",
            "Beta version Reports": "🧪", "Release Notes": "📝"
        };

        // URLs REMOVED - Dynamic Doctype matching according to Frappe Default Workspace rules

        // 1. Report Rendering
        function renderReports() {
            container.innerHTML = '';
            allCards.length = 0;
            const fragment = document.createDocumentFragment();

            Object.keys(reportData).forEach((groupName) => {
                const groupCard = document.createElement('div');
                groupCard.className = 'report-group-card';
                groupCard.dataset.category = groupName.toLowerCase();

                const icon = categoryIcons[groupName] || '📁';
                const headerDiv = document.createElement('div');
                headerDiv.className = 'group-header';
                headerDiv.innerHTML = `
                    <div class="group-header-left">
                        <div class="group-icon">${icon}</div>
                        <h4 class="group-title">${groupName}</h4>
                    </div>
                    <button class="header-sort-btn">A-Z</button>
                `;
                const sortBtn = headerDiv.querySelector('.header-sort-btn');
                groupCard.appendChild(headerDiv);

                let currentData = [...reportData[groupName]];
                let isAscending = true;

                const linksContainer = document.createElement('div');
                linksContainer.className = 'group-links';

                const renderLinks = () => {
                    const sorted = [...currentData].sort((a, b) => {
                        if (a.name < b.name) return isAscending ? -1 : 1;
                        if (a.name > b.name) return isAscending ? 1 : -1;
                        return 0;
                    });
                    linksContainer.innerHTML = sorted.map(subReport => `
                        <a href="${subReport.url}" target="_blank" rel="noopener" class="report-link" data-report-name="${subReport.name.toLowerCase()}">
                            <span>${subReport.name}</span>
                        </a>
                    `).join('');
                };

                sortBtn.addEventListener('click', (e) => {
                    e.preventDefault(); e.stopPropagation();
                    isAscending = !isAscending;
                    sortBtn.textContent = isAscending ? 'A-Z' : 'Z-A';
                    renderLinks();
                });

                renderLinks();
                groupCard.appendChild(linksContainer);
                fragment.appendChild(groupCard);

                allCards.push({
                    element: groupCard, category: groupName, linksContainer: linksContainer,
                    links: Array.from(linksContainer.querySelectorAll('a'))
                });
            });
            container.appendChild(fragment);
        }

        // 2. Management Cards Rendering
        function renderManagementCards(targetMenu, workspaceName) {
            container.innerHTML = `
                <div class="loader-container" style="grid-column: 1 / -1;">
                    <div class="shishu-spinner"></div>
                    <div>Loading Workspace...</div>
                </div>`;
            allCards.length = 0;

            if (!workspaceName) {
                container.innerHTML = '';
                return;
            }

            frappe.call({
                method: 'frappe.client.get',
                args: { doctype: 'Workspace', name: workspaceName },
                callback: function (r) {
                    container.innerHTML = '';
                    if (!r.message) {
                        if (noResultsDiv) {
                            noResultsDiv.style.display = 'block';
                            noResultsDiv.querySelector('p').innerHTML = `Workspace not found.`;
                        }
                        return;
                    }

                    const workspace = r.message;
                    let sections = [];
                    let currentSection = null;

                    const iconMap = {
                        'User & Role': '👥', 'Household': '🏠', 'Partner': '🤝', 'Stock': '📦', 'Creche': '🏫', 'Geography Masters': '🗺️', 'Anthropometric Data Set': '⏲️', 'Visit Note': '📝', 'Creche Planned': '📅', 'Ticket Support': '🎫', 'Grievance': '📢', 'Cashbook': '📉', 'App Release Note': '📱',
                        'User List': '👤', 'User': '👤', 'Role List': '🛡️', 'Role': '🛡️', 'Household List': '🏠', 'Household Form': '🏠', 'Creche Stock': '📦', 'Creche Requisition': '📋', 'Creche List': '🏫', 'Child Profile': '👦', 'Child Enrollment and Exit': '🚪', 'Child Attendance': '📅', 'Child Growth Monitoring': '📈', 'Creche Check In': '✅', 'Child Health': '🏥', 'Child Event': '🎉', 'Child Immunization': '💉', 'Child Referral': '🚩', 'Child Follow up': '👣', 'Creche Committee Meeting': '👥', 'State List': '🗺️', 'State': '🗺️', 'District List': '📍', 'District': '📍', 'Block List': '🏢', 'Block': '🏢', 'Gram Panchayat List': '🏛️', 'Gram Panchayat': '🏛️', 'Village List': '🏘️', 'Village': '🏘️', 'Weight for age Boys': '⏲️', 'Weight for age Girls': '⏲️', 'Height for age Boys': '📏', 'Height for age Girls': '📏', 'Weight to Height Boys': '📐', 'Weight to Height Girls': '📐', 'Creche Monitoring Checklist': '📝', 'Creche Monitoring Checklist CC': '📝', 'Creche Monitoring Checklist ALM': '📋', 'Creche Monitoring Checklist CBM': '📊', 'Safety Indicators': '🛡️', 'Review Meetings': '🔄', 'Cashbook Receipt': '🧾', 'Mobile App Version Release': '📱', 'Web Version Release': '💻'
                    };

                    if (workspace.links && workspace.links.length > 0) {
                        workspace.links.forEach(link => {
                            if (link.type === 'Card Break') {
                                if (currentSection) sections.push(currentSection);
                                currentSection = {
                                    title: link.label,
                                    icon: link.icon || iconMap[link.label] || '📁',
                                    cards: []
                                };
                            } else if (link.type === 'Link' && currentSection) {
                                currentSection.cards.push({
                                    title: link.label,
                                    doctype: link.link_to,
                                    icon: link.icon || iconMap[link.label] || iconMap[link.link_to] || '📄'
                                });
                            }
                        });
                        if (currentSection) sections.push(currentSection);
                    }

                    if (sections.length === 0) {
                        if (noResultsDiv) {
                            noResultsDiv.style.display = 'block';
                            noResultsDiv.querySelector('p').innerHTML = `No sections configured in this workspace.`;
                        }
                        return;
                    }

                    const fragment = document.createDocumentFragment();

                    sections.forEach((section, index) => {
                        const card = document.createElement('div');
                        card.className = 'mgmt-card';
                        card.dataset.category = section.title.toLowerCase();
                        card.style.animationDelay = `${index * 0.05}s`;

                        card.innerHTML = `
                            <div class="mgmt-card-header">
                                <div class="mgmt-card-icon">${section.icon}</div>
                                <h4 class="mgmt-card-title">${section.title}</h4>
                            </div>
                            <div class="mgmt-actions-list">
                                ${section.cards.map(act => `
                                    <div class="mgmt-action-btn" data-doctype="${act.doctype}" data-report-name="${act.title.toLowerCase()}">
                                        <div class="mgmt-action-left">
                                            <span class="mgmt-action-icon">${act.icon}</span>
                                            <span class="mgmt-action-text">${act.title}</span>
                                        </div>
                                        <span class="mgmt-action-chevron">❯</span>
                                    </div>
                                `).join('')}
                            </div>
                        `;

                        card.querySelectorAll('.mgmt-action-btn').forEach(btn => {
                            btn.addEventListener('click', (e) => {
                                const doctypeTarget = e.currentTarget.dataset.doctype;
                                if (doctypeTarget) {
                                    openListView(doctypeTarget);
                                }
                            });
                        });

                        fragment.appendChild(card);
                        allCards.push({
                            element: card, category: section.title,
                            linksContainer: card.querySelector('.mgmt-actions-list'),
                            links: Array.from(card.querySelectorAll('.mgmt-action-btn'))
                        });
                    });

                    container.appendChild(fragment);
                }
            });
        }

        const sidebarLinks = wrapperEl.querySelectorAll('.sidebar-item');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                sidebarLinks.forEach(l => l.classList.remove('active'));
                e.currentTarget.classList.add('active');

                const target = e.currentTarget.dataset.target;
                const workspace = e.currentTarget.dataset.workspace;
                if (noResultsDiv) noResultsDiv.style.display = 'none';

                document.getElementById('view-list').style.display = 'none';
                document.getElementById('view-detail').style.display = 'none';
                document.getElementById('view-dashboard').style.display = 'block';

                if (target === 'report-menu') renderReports();
                else renderManagementCards(target, workspace);

                if (window.innerWidth <= 900) {
                    sidebar.classList.remove('mobile-open'); overlay.classList.remove('visible');
                }
            });
        });

        if (searchInput) {
            const raf = window.requestAnimationFrame || ((cb) => setTimeout(cb, 16));
            const debounce = (func, wait) => { let t; return (...args) => { clearTimeout(t); t = setTimeout(() => func(...args), wait); }; };

            searchInput.addEventListener('keydown', (e) => { if (e.key === 'Escape') clearSearch(); e.stopPropagation(); });
            searchInput.addEventListener('keyup', (e) => e.stopPropagation());
            searchInput.addEventListener('input', (e) => {
                e.stopPropagation();
                const val = e.target.value;
                filterCards(val);
                searchClearBtn.classList.toggle('visible', val.length > 0);
            });

            const clearSearch = () => {
                searchInput.value = ''; filterCards(''); searchClearBtn.classList.remove('visible'); searchInput.focus();
            };
            if (searchClearBtn) searchClearBtn.addEventListener('click', clearSearch);

            const filterCards = debounce((searchTerm) => {
                const term = searchTerm.toLowerCase().trim();
                let visibleCount = 0;

                raf(() => {
                    allCards.forEach(card => {
                        const categoryMatch = card.category.toLowerCase().includes(term);
                        let linkMatchCount = 0;

                        card.links.forEach(link => {
                            const name = link.dataset.reportName || link.textContent.toLowerCase();
                            if (term === '' || name.includes(term) || categoryMatch) {
                                link.style.display = 'flex'; linkMatchCount++;
                            } else {
                                link.style.display = 'none';
                            }
                        });

                        if (linkMatchCount > 0 || categoryMatch || term === '') {
                            card.element.classList.remove('hidden-card'); visibleCount++;
                        } else {
                            card.element.classList.add('hidden-card');
                        }
                    });

                    if (noResultsDiv) {
                        if (term) noResultsDiv.querySelector('p').innerHTML = `No results found matching "<span id="search-term">${term}</span>"`;
                        noResultsDiv.style.display = (visibleCount === 0 && term !== '') ? 'block' : 'none';
                    }
                });
            }, 150);
        }

        // ==========================================
        // DYNAMIC LIST & DETAIL VIEWS
        // ==========================================

        let currentDoctype = null;
        let currentMeta = null;
        let currentLimit = SHISHU_CONFIG.defaultLimit;
        let dynamicFilterValues = {};
        let activeFilterControls = {};
        let currentSort = 'modified desc'; // Default sorting mechanism

        // Setup Sort Logic Interactions
        document.getElementById('list-sort-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            document.getElementById('sort-menu').classList.toggle('show');
        });

        document.querySelectorAll('#sort-menu .dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                currentSort = e.target.dataset.sort;
                document.getElementById('current-sort-label').textContent = e.target.textContent;
                document.getElementById('sort-menu').classList.remove('show');
                fetchListData();
            });
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('#list-sort-btn') && !e.target.closest('#sort-menu')) {
                document.getElementById('sort-menu').classList.remove('show');
            }
        });

        // Initialize Pagination Limit Dropdown
        const limitSelect = document.getElementById('list-limit-select');
        SHISHU_CONFIG.limits.forEach(l => {
            limitSelect.innerHTML += `<option value="${l}">${l === 999999 ? 'All' : l + ' per page'}</option>`;
        });
        limitSelect.value = currentLimit;
        limitSelect.addEventListener('change', (e) => {
            currentLimit = parseInt(e.target.value);
            fetchListData();
        });

        // Setup Checkbox Row Selecting Logic
        document.addEventListener('change', (e) => {
            if (e.target.id === 'select-all-rows') {
                const isChecked = e.target.checked;
                document.querySelectorAll('.row-select-chk').forEach(chk => chk.checked = isChecked);
            }
            if (e.target.classList.contains('row-select-chk')) {
                const total = document.querySelectorAll('.row-select-chk').length;
                const checked = document.querySelectorAll('.row-select-chk:checked').length;
                const selectAll = document.getElementById('select-all-rows');
                if (selectAll) selectAll.checked = (total === checked && total > 0);
            }
        });

        // Initialize Quick Search Filter logic
        const listFilterInput = document.getElementById('list-quick-filter');
        listFilterInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#list-table-container tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });

        // Setup Buttons 
        document.getElementById('list-back-btn').addEventListener('click', () => {
            document.getElementById('view-list').style.display = 'none';
            document.getElementById('view-dashboard').style.display = 'block';
        });
        document.getElementById('list-refresh-btn').addEventListener('click', fetchListData);

        // Use Native Frappe Form route directly
        document.getElementById('list-create-btn').addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (currentDoctype) {
                frappe.set_route('Form', currentDoctype);
            }
        });

        // Export Excel with Selection Functionality
        document.getElementById('list-export-btn').addEventListener('click', () => {
            if (!currentDoctype || !currentMeta) return;
            let table = document.querySelector('.custom-table');
            if (!table) return;

            let checkedBoxes = table.querySelectorAll('.row-select-chk:checked');
            let exportAll = checkedBoxes.length === 0;

            let csv = [];
            let rows = table.querySelectorAll('tr');

            for (let i = 0; i < rows.length; i++) {
                if (i > 0 && !exportAll) {
                    let chk = rows[i].querySelector('.row-select-chk');
                    if (!chk || !chk.checked) continue;
                }

                let row = [], cols = rows[i].querySelectorAll('td, th');
                for (let j = 1; j < cols.length; j++) {
                    let textData = cols[j].innerText.replace(/"/g, '""');
                    row.push('"' + textData + '"');
                }
                csv.push(row.join(','));
            }

            let csvFile = new Blob([csv.join('\n')], { type: 'text/csv;charset=utf-8;' });
            let downloadLink = document.createElement('a');
            downloadLink.download = `${currentDoctype}_Export.csv`;
            downloadLink.href = window.URL.createObjectURL(csvFile);
            downloadLink.style.display = 'none';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        });

        document.getElementById('detail-back-btn').addEventListener('click', () => {
            document.getElementById('view-detail').style.display = 'none';
            document.getElementById('view-list').style.display = 'flex';
        });

        function openListView(doctype) {
            currentDoctype = doctype;
            document.getElementById('view-dashboard').style.display = 'none';
            document.getElementById('view-detail').style.display = 'none';
            document.getElementById('view-list').style.display = 'flex';
            document.getElementById('list-title').textContent = doctype;

            document.getElementById('list-create-btn').style.display = 'block';

            listFilterInput.value = '';
            document.getElementById('list-dynamic-filters').innerHTML = '';
            dynamicFilterValues = {};

            const container = document.getElementById('list-table-container');
            container.innerHTML = `
                <div class="loader-container">
                    <div class="shishu-spinner"></div>
                    <div>Fetching Metadata...</div>
                </div>`;

            frappe.model.with_doctype(currentDoctype, () => {
                currentMeta = frappe.get_meta(currentDoctype);
                if (!currentMeta) {
                    container.innerHTML = '<div style="padding: 40px; color: #ef4444; text-align: center;">Failed to load Doctype Metadata.</div>';
                    return;
                }

                renderDynamicFilters(currentMeta);
                fetchListData();
            });
        }

        function renderDynamicFilters(meta) {
            const filterContainer = document.getElementById('list-dynamic-filters');
            filterContainer.innerHTML = '';
            activeFilterControls = {};

            const filterFields = meta.fields.filter(f => f.in_standard_filter || f.in_list_filter);
            if (filterFields.length === 0) {
                filterContainer.style.display = 'none';
                return;
            }

            filterContainer.style.display = 'flex';

            filterFields.forEach(f => {
                let wrapper = document.createElement('div');
                wrapper.className = 'filter-control';
                filterContainer.appendChild(wrapper);

                let df = Object.assign({}, f);
                df.placeholder = f.label;

                df.onchange = function () {
                    dynamicFilterValues = {};
                    Object.keys(activeFilterControls).forEach(fieldname => {
                        let control = activeFilterControls[fieldname];
                        if (control && control.get_value) {
                            let val = control.get_value();
                            if (val) {
                                dynamicFilterValues[fieldname] = val;
                            }
                        }
                    });
                    fetchListData();
                };

                let control = frappe.ui.form.make_control({
                    df: df,
                    parent: wrapper,
                    only_input: true,
                    render_input: true
                });
                activeFilterControls[f.fieldname] = control;
            });
        }

        function fetchListData() {
            if (!currentMeta) return;
            const container = document.getElementById('list-table-container');
            container.innerHTML = `
                <div class="loader-container">
                    <div class="shishu-spinner"></div>
                    <div>Fetching records...</div>
                </div>`;

            const config = SHISHU_CONFIG.doctypes[currentDoctype] || {};
            let filters = config.filters ? [...config.filters] : [];

            Object.keys(dynamicFilterValues).forEach(fieldname => {
                const fieldMeta = currentMeta.fields.find(f => f.fieldname === fieldname);
                if (fieldMeta && (fieldMeta.fieldtype === 'Select' || fieldMeta.fieldtype === 'Link')) {
                    filters.push([fieldname, '=', dynamicFilterValues[fieldname]]);
                } else {
                    filters.push([fieldname, 'like', `%${dynamicFilterValues[fieldname]}%`]);
                }
            });

            let listFields = currentMeta.fields
                .filter(f => f.in_list_view)
                .map(f => f.fieldname);

            if (listFields.length === 0) listFields = ['name'];
            if (!listFields.includes('name')) listFields.unshift('name');

            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: currentDoctype,
                    fields: listFields,
                    filters: filters,
                    limit_page_length: currentLimit,
                    order_by: currentSort // Applies dynamic sort
                },
                callback: function (r) {
                    renderListTable(r.message || [], listFields, currentMeta);
                }
            });
        }

        function renderListTable(data, fields, meta) {
            const container = document.getElementById('list-table-container');
            const selectAll = document.getElementById('select-all-rows');
            if (selectAll) selectAll.checked = false;

            if (data.length === 0) {
                container.innerHTML = '<div style="padding: 40px; text-align:center; color: var(--text-secondary);">No records found matching criteria.</div>';
                return;
            }

            const headers = fields.map(fn => {
                if (fn === 'name') return 'ID';
                const df = meta.fields.find(f => f.fieldname === fn);
                return df ? df.label : fn;
            });

            let html = '<div class="custom-table-wrapper"><table class="custom-table"><thead><tr>';
            html += '<th style="width: 40px; text-align: center;"><input type="checkbox" id="select-all-rows" title="Select All"></th>';
            html += headers.map(h => `<th>${h}</th>`).join('');
            html += '</tr></thead><tbody>';

            data.forEach(row => {
                html += `<tr data-name="${row.name}">`;
                html += `<td style="text-align: center;" onclick="event.stopPropagation()"><input type="checkbox" class="row-select-chk" value="${row.name}"></td>`;
                fields.forEach(fn => {
                    let val = row[fn] == null ? '' : row[fn];
                    const df = meta.fields.find(f => f.fieldname === fn);

                    if (['weight_for_age', 'weight_for_height', 'height_for_age'].includes(fn)) {
                        val = formatNutritionStatus(val);
                    } else if (df && df.fieldtype === 'Table MultiSelect') {
                        val = formatMultiSelect(val, df);
                    } else if (df && df.fieldtype === 'Link' && val) {
                        val = `<span class="async-link-val" data-doctype="${df.options}" data-val="${val}">${val}</span>`;
                    }

                    html += `<td>${val}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';

            container.innerHTML = html;

            container.querySelectorAll('tbody tr').forEach(tr => {
                tr.addEventListener('click', () => openDetailView(currentDoctype, tr.dataset.name));
            });

            const term = listFilterInput.value.toLowerCase();
            if (term) {
                container.querySelectorAll('tbody tr').forEach(row => {
                    row.style.display = row.textContent.toLowerCase().includes(term) ? '' : 'none';
                });
            }

            resolveLinkTitles(container);
        }

        function openDetailView(doctype, docname) {
            document.getElementById('view-list').style.display = 'none';
            document.getElementById('view-detail').style.display = 'flex';
            document.getElementById('detail-title').textContent = `${docname}`;

            const tabsContainer = document.getElementById('detail-tabs-container');
            const bodyContainer = document.getElementById('detail-body-container');
            tabsContainer.innerHTML = '';
            bodyContainer.innerHTML = `
                <div class="loader-container">
                    <div class="shishu-spinner"></div>
                    <div>Loading Document Data...</div>
                </div>`;

            frappe.model.with_doc(doctype, docname, () => {
                const doc = frappe.get_doc(doctype, docname);
                const meta = frappe.get_meta(doctype);

                let tabs = [];
                let currentTab = { label: 'Details', sections: [] };
                let currentSection = { label: '', fields: [] };

                tabs.push(currentTab);
                currentTab.sections.push(currentSection);

                meta.fields.forEach(f => {
                    if (f.hidden === 1) return;

                    if (f.fieldtype === 'Tab Break') {
                        currentTab = { label: f.label || 'Tab', sections: [] };
                        currentSection = { label: '', fields: [] };
                        currentTab.sections.push(currentSection);
                        tabs.push(currentTab);
                    } else if (f.fieldtype === 'Section Break') {
                        currentSection = { label: f.label || '', fields: [] };
                        currentTab.sections.push(currentSection);
                    } else if (f.fieldtype !== 'Column Break') {
                        currentSection.fields.push(f);
                    }
                });

                tabs = tabs.filter(t => {
                    t.sections = t.sections.filter(s => s.fields.length > 0);
                    return t.sections.length > 0;
                });

                tabsContainer.innerHTML = tabs.map((t, i) =>
                    `<div class="cv-tab ${i === 0 ? 'active' : ''}" data-target="tab-${i}">${t.label}</div>`
                ).join('');

                let html = '';
                tabs.forEach((tab, i) => {
                    html += `<div class="cv-tab-content" id="tab-${i}" style="display: ${i === 0 ? 'block' : 'none'};">`;

                    tab.sections.forEach((sec, sIdx) => {
                        html += `<div class="form-section-card">`;
                        if (sec.label) {
                            html += `<h4 class="section-heading">${sec.label}</h4>`;
                        }

                        html += `<div class="form-grid">`;
                        sec.fields.forEach(df => {
                            let val = doc[df.fieldname] == null ? '' : doc[df.fieldname];

                            if (df.fieldtype === 'Table') {
                                html += `</div>`;
                                html += renderChildTable(val, df.options);
                                html += `<div class="form-grid">`;
                            } else {
                                let displayVal = val;

                                if (['weight_for_age', 'weight_for_height', 'height_for_age'].includes(df.fieldname)) {
                                    displayVal = formatNutritionStatus(val);
                                } else if (df.fieldtype === 'Table MultiSelect') {
                                    displayVal = formatMultiSelect(val, df);
                                } else if (df.fieldtype === 'Link' && val) {
                                    displayVal = `<span class="async-link-val" data-doctype="${df.options}" data-val="${val}">${val}</span>`;
                                } else if (df.fieldtype === 'Check') {
                                    displayVal = val ? '<span style="color:green; font-weight:bold;">✔</span>' : '<span style="color:red; font-weight:bold;">✘</span>';
                                } else if (['Attach Image', 'Image'].includes(df.fieldtype) && val) {
                                    displayVal = `<img src="${val}" style="max-height: 120px; border-radius:8px; border: 1px solid var(--border-color); cursor:pointer;" onclick="window.open('${val}', '_blank')">`;
                                } else if (['Attach'].includes(df.fieldtype) && val) {
                                    displayVal = `<a href="${val}" target="_blank" style="color: var(--mgmt-icon-color); font-weight:600;">View Attachment</a>`;
                                } else if (df.fieldtype === 'Button') {
                                    displayVal = `<button class="cv-btn primary" onclick="frappe.set_route('Form', '${doctype}', '${docname}')">${df.label || 'Action'}</button> <br><small style="color:var(--text-secondary); font-size:11px;">(Executes in Standard Form)</small>`;
                                }

                                let isFullWidth = ['Text Editor', 'Table', 'Table MultiSelect', 'HTML', 'Code', 'Small Text', 'Text', 'Long Text'].includes(df.fieldtype);
                                html += `
                                    <div class="form-field ${isFullWidth ? 'full-width' : ''}">
                                        <span class="form-label">${df.label || df.fieldname}</span>
                                        <div class="form-value">${displayVal}</div>
                                    </div>
                                `;
                            }
                        });
                        html += `</div></div>`;
                    });

                    html += `</div>`;
                });

                bodyContainer.innerHTML = html;

                tabsContainer.querySelectorAll('.cv-tab').forEach(tab => {
                    tab.addEventListener('click', () => {
                        tabsContainer.querySelectorAll('.cv-tab').forEach(t => t.classList.remove('active'));
                        bodyContainer.querySelectorAll('.cv-tab-content').forEach(c => c.style.display = 'none');
                        tab.classList.add('active');
                        document.getElementById(tab.dataset.target).style.display = 'block';
                    });
                });

                resolveLinkTitles(bodyContainer);

                const editBtn = document.getElementById('detail-edit-btn');
                editBtn.style.display = 'block';
                editBtn.textContent = `✏️ Edit ${doctype}`;
                editBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    frappe.set_route('Form', doctype, docname);
                };
            });
        }

        // Updated Box-Style layout for Child Tables
        function renderChildTable(rows, childDoctype) {
            if (!rows || rows.length === 0) return `<div style="padding: 10px 30px; color: var(--text-secondary); font-size: 0.85rem;">No data entries added.</div>`;

            let fields = [];
            const meta = frappe.get_meta(childDoctype);
            if (meta) fields = meta.fields.filter(f => !['Section Break', 'Column Break', 'Tab Break', 'HTML', 'Button'].includes(f.fieldtype) && !f.hidden).map(f => f.fieldname);

            if (fields.length === 0 && rows.length > 0) {
                fields = Object.keys(rows[0]).filter(k => !['name', 'owner', 'creation', 'modified', 'modified_by', 'parent', 'parentfield', 'parenttype', 'idx', 'docstatus'].includes(k));
            }

            let html = '<div class="child-table-box"><table class="box-table"><thead><tr>';
            html += '<th style="width: 40px; text-align:center;">No.</th>';
            html += fields.map(f => {
                let lbl = f;
                if (meta) {
                    let df = meta.fields.find(x => x.fieldname === f);
                    if (df) lbl = df.label;
                }
                return `<th>${lbl}</th>`;
            }).join('');
            html += '</tr></thead><tbody>';

            rows.forEach((row, index) => {
                html += '<tr>';
                html += `<td style="text-align:center;">${index + 1}</td>`;
                fields.forEach(f => {
                    let val = row[f] == null ? '' : row[f];
                    const df = meta ? meta.fields.find(x => x.fieldname === f) : null;

                    if (['weight_for_age', 'weight_for_height', 'height_for_age'].includes(f)) {
                        val = formatNutritionStatus(val);
                    } else {
                        if (df && df.fieldtype === 'Table MultiSelect') val = formatMultiSelect(val, df);
                        else if (df && df.fieldtype === 'Link' && val) val = `<span class="async-link-val" data-doctype="${df.options}" data-val="${val}">${val}</span>`;
                        else if (df && df.fieldtype === 'Check') val = val ? '✔' : '';
                    }
                    html += `<td>${val}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            return html;
        }

        // --- ENHANCED Link Title Resolver ---
        // Converts numerical/hash IDs to actual Display Names using batch API calling
        function resolveLinkTitles(container) {
            const linkEls = container.querySelectorAll('.async-link-val');
            if (linkEls.length === 0) return;

            const queries = {};
            linkEls.forEach(el => {
                const dt = el.dataset.doctype;
                const val = el.dataset.val;
                if (!dt || !val) return;
                if (!queries[dt]) queries[dt] = new Set();
                queries[dt].add(String(val));
            });

            Object.keys(queries).forEach(dt => {
                const names = Array.from(queries[dt]);
                if (names.length === 0) return;

                frappe.model.with_doctype(dt, () => {
                    const meta = frappe.get_meta(dt);
                    if (!meta) return;

                    let titleField = meta.title_field;

                    // Fallback to commonly used display names if standard title_field is omitted
                    if (!titleField) {
                        const fallbacks = ['full_name', 'company_name', 'partner_name', 'title'];
                        for (let pt of fallbacks) {
                            if (meta.fields.find(f => f.fieldname === pt)) {
                                titleField = pt;
                                break;
                            }
                        }
                    }

                    if (!titleField || titleField === 'name') return;

                    // Batching requests to prevent URI Too Long server rejections
                    const chunkSize = 100;
                    for (let i = 0; i < names.length; i += chunkSize) {
                        const chunk = names.slice(i, i + chunkSize);
                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: { doctype: dt, filters: [['name', 'in', chunk]], fields: ['name', titleField] },
                            callback: function (r) {
                                if (r.message) {
                                    const titleMap = {};
                                    r.message.forEach(row => { titleMap[String(row.name)] = row[titleField] || row.name; });

                                    linkEls.forEach(el => {
                                        if (el.dataset.doctype === dt && titleMap[String(el.dataset.val)]) {
                                            el.textContent = titleMap[String(el.dataset.val)];
                                        }
                                    });
                                }
                            }
                        });
                    }
                });
            });
        }

        function applyWorkspacePermissions() {
            let allowedWorkspaces = [];
            const isAdmin = frappe.session.user === 'Administrator' || (frappe.user_roles && frappe.user_roles.includes('System Manager'));

            const applyVisibility = (allowed) => {
                let firstVisible = null;
                wrapperEl.querySelectorAll('.sidebar-item').forEach(item => {
                    const wsName = item.dataset.workspace;
                    if (isAdmin || allowed.includes(wsName)) {
                        item.style.display = 'flex';
                        if (!firstVisible) firstVisible = item;
                    } else {
                        item.style.display = 'none';
                    }
                });

                if (firstVisible) {
                    firstVisible.click();
                } else {
                    const noAccessDiv = document.createElement('div');
                    noAccessDiv.style = 'padding: 40px; text-align:center; color: var(--text-secondary); grid-column: 1 / -1; width: 100%;';
                    noAccessDiv.innerHTML = '<h3>Access Denied</h3><p>You do not have access to any workspaces.</p>';
                    container.innerHTML = '';
                    container.appendChild(noAccessDiv);
                }
            };

            if (frappe.boot && frappe.boot.allowed_workspaces && frappe.boot.allowed_workspaces.length > 0) {
                allowedWorkspaces = frappe.boot.allowed_workspaces.map(w => (typeof w === 'string' ? w : (w.name || w.title)));
                applyVisibility(allowedWorkspaces);
            } else {
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: { doctype: 'Workspace', fields: ['name', 'title'] },
                    callback: function (r) {
                        if (r.message) {
                            allowedWorkspaces = r.message.map(w => w.name).concat(r.message.map(w => w.title));
                        }
                        applyVisibility(allowedWorkspaces);
                    }
                });
            }
        }

        applyWorkspacePermissions();
    })();
};












