// Shishughar Theme — JS enhancements
// 1. App title next to the navbar logo
// 2. Search placeholder text
// 3. Sidebar footer: clickable user card (opens the user's profile)
// 4. Colorful emoji icons for workspace sidebar items

(function () {
	const APP_TITLE = "Shishughar Management System";

	// Workspace opened by default when landing on /app.
	// Must exactly match the workspace title.
	const DEFAULT_WORKSPACE = "Reports Menu";

	// The workspace view falls back to localStorage.current_page when no
	// workspace is in the route — set it before the router resolves.
	try {
		localStorage.current_page = DEFAULT_WORKSPACE;
		localStorage.is_current_page_public = "true";
	} catch (e) {
		// localStorage unavailable — ignore
	}

	// Keyword → emoji. First match wins (checked top to bottom).
	const ICON_MAP = [
		["report", "📊"],
		["creche", "🏡"],
		["organization", "🏢"],
		["cc menu", "👮"],
		["cs menu", "👷"],
		["account", "🪙"],
		["capacity", "🏛️"],
		["safety", "🛡️"],
		["to do", "📝"],
		["todo", "📝"],
		["hr", "🧑‍💼"],
		["home", "🏠"],
		["tool", "🛠️"],
		["setting", "⚙️"],
		["user", "👤"],
		["integration", "🔗"],
		["build", "🧱"],
	];

	function emoji_for(title) {
		const t = (title || "").toLowerCase();
		for (const [key, emoji] of ICON_MAP) {
			if (t.includes(key)) return emoji;
		}
		return "📁";
	}

	function enhance_navbar() {
		const $brand = $("header.navbar .navbar-brand.navbar-home");
		if (!$brand.length || $("header.navbar .sg-app-title").length) return;
		$(`<span class="sg-app-title"></span>`).text(__(APP_TITLE)).insertAfter($brand);
		$("#navbar-search").attr("placeholder", __("Search menus & reports..."));
	}

	function colorize_sidebar_icons() {
		$(".desk-sidebar .standard-sidebar-item .sidebar-item-icon").each(function () {
			const $icon = $(this);
			if ($icon.find(".sg-emoji").length) return;
			const title =
				$icon.closest(".item-anchor").attr("title") ||
				$icon.siblings(".sidebar-item-label").text() ||
				$icon.closest(".sidebar-item-container").attr("item-name");
			$(`<span class="sg-emoji"></span>`).text(emoji_for(title)).appendTo($icon.empty());
		});
	}

	function build_sidebar_footer() {
		const $sidebar = $(".layout-side-section .list-sidebar.overlay-sidebar");
		if (!$sidebar.length) return false;
		if ($sidebar.find(".sg-sidebar-footer").length) return true;

		const fullname = frappe.session.user_fullname || frappe.session.user;
		const $footer = $(`
			<div class="sg-sidebar-footer">
				<div class="sg-divider"></div>
				<div class="sg-user-card" title="${__("Open profile")}">
					<div class="sg-user-avatar">${frappe.avatar(frappe.session.user, "avatar-medium")}</div>
					<div class="sg-user-info">
						<div class="sg-user-name"></div>
						<div class="sg-user-role"></div>
					</div>
				</div>
			</div>
		`);
		$footer.find(".sg-user-name").text(fullname);
		$footer.find(".sg-user-role").text(frappe.session.user);
		$footer.appendTo($sidebar);

		// Open the logged-in user's profile on click
		$footer.find(".sg-user-card").on("click", () => {
			frappe.set_route("Form", "User", frappe.session.user);
		});
		return true;
	}

	function observe_sidebar() {
		const sidebar = document.querySelector(".desk-sidebar");
		if (!sidebar || sidebar._sg_observed) return;
		sidebar._sg_observed = true;
		// Re-apply emoji icons whenever the sidebar re-renders (e.g. edit mode)
		const observer = new MutationObserver(
			frappe.utils.debounce(() => colorize_sidebar_icons(), 100)
		);
		observer.observe(sidebar, { childList: true, subtree: true });
	}

	function enhance_sidebar() {
		const ok = build_sidebar_footer();
		if (ok) {
			colorize_sidebar_icons();
			observe_sidebar();
		}
		return ok;
	}

	function try_enhance_sidebar(retries = 10) {
		if (enhance_sidebar() || retries <= 0) return;
		setTimeout(() => try_enhance_sidebar(retries - 1), 400);
	}

	$(document).on("app_ready", () => {
		enhance_navbar();
		try_enhance_sidebar();
		// The workspace sidebar is created lazily — retry on route changes too
		frappe.router && frappe.router.on("change", () => try_enhance_sidebar(5));
	});
})();
