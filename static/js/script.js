// Global Theme Toggle and Toolkit Tab Navigation
// Author: Kinza | https://github.com/kinza099

(function () {
    const root = document.documentElement;
    const toggleBtn = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");

    // 1. Theme Management (persisted in localStorage and memory)
    let currentTheme = localStorage.getItem("hash_toolkit_theme") || root.getAttribute("data-theme") || "dark";

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
        if (icon) {
            icon.textContent = theme === "dark" ? "dark_mode" : "light_mode";
        }
        currentTheme = theme;
        try {
            localStorage.setItem("hash_toolkit_theme", theme);
        } catch (e) {}
        window.__hashToolTheme = theme;
    }

    applyTheme(currentTheme);

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            const next = currentTheme === "dark" ? "light" : "dark";
            applyTheme(next);
            window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: next } }));
        });
    }

    // 2. Toolkit Tab Navigation
    const navTabs = document.querySelectorAll(".toolkit-tab-btn");
    const toolPanels = document.querySelectorAll(".tool-panel");

    function switchToolkitTab(targetTabId) {
        if (!targetTabId) return;

        // Clean ID format
        const cleanId = targetTabId.replace(/^#/, "");
        const panelId = cleanId.startsWith("tab-") ? cleanId : "tab-" + cleanId;

        let found = false;
        toolPanels.forEach((panel) => {
            if (panel.id === panelId) {
                panel.classList.add("active");
                panel.style.display = "block";
                found = true;
            } else {
                panel.classList.remove("active");
                panel.style.display = "none";
            }
        });

        if (found) {
            navTabs.forEach((tab) => {
                const tabTarget = tab.getAttribute("data-tab");
                if (tabTarget === panelId || tabTarget === cleanId) {
                    tab.classList.add("active");
                    // Scroll tab into view if horizontal scroll container exists
                    tab.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
                } else {
                    tab.classList.remove("active");
                }
            });

            // Update URL hash without jumping
            history.replaceState(null, "", "#" + cleanId.replace(/^tab-/, ""));
        }
    }

    window.switchToolkitTab = switchToolkitTab;

    navTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            const target = tab.getAttribute("data-tab");
            switchToolkitTab(target);
        });
    });

    // Check URL hash on page load (e.g. #file-hasher, #batch, etc.)
    window.addEventListener("DOMContentLoaded", () => {
        const hash = window.location.hash;
        if (hash) {
            switchToolkitTab(hash.slice(1));
        }
    });

    // Handle browser back/forward buttons
    window.addEventListener("hashchange", () => {
        const hash = window.location.hash;
        if (hash) {
            switchToolkitTab(hash.slice(1));
        }
    });
})();
