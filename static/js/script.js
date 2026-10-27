// Global Theme Toggle and Toolkit Tab Navigation
// Author: Kinza | https://github.com/kinza099

(function () {
    const root = document.documentElement;
    const toggleBtn = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");

    // 1. Theme Management (persisted in localStorage and memory)
    const urlParams = new URLSearchParams(window.location.search);
    const themeParam = urlParams.get("theme");
    let currentTheme = (themeParam === "light" || themeParam === "dark")
        ? themeParam
        : (localStorage.getItem("hash_toolkit_theme") || root.getAttribute("data-theme") || "dark");

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
                    if (typeof tab.scrollIntoView === "function") {
                        tab.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
                    }
                } else {
                    tab.classList.remove("active");
                }
            });

            // Update URL hash without jumping
            if (window.history && window.history.replaceState) {
                history.replaceState(null, "", "#" + cleanId.replace(/^tab-/, ""));
            }
        }
    }

    window.switchToolkitTab = switchToolkitTab;

    navTabs.forEach((tab) => {
        tab.addEventListener("click", () => {
            const target = tab.getAttribute("data-tab");
            switchToolkitTab(target);
        });
    });

    // Check URL hash immediately and on page load (e.g. #file-hasher, #batch, etc.)
    if (window.location && window.location.hash) {
        switchToolkitTab(window.location.hash.slice(1));
    }

    function initToolkitState() {
        if (urlParams.get("tab")) {
            switchToolkitTab(urlParams.get("tab"));
        } else if (window.location && window.location.hash) {
            switchToolkitTab(window.location.hash.slice(1));
        }
        const hashQuery = urlParams.get("hash");
        if (hashQuery) {
            setTimeout(() => {
                if (typeof window.inspectSingleHash === "function") {
                    window.inspectSingleHash(hashQuery);
                }
            }, 300);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initToolkitState);
    } else {
        initToolkitState();
    }

    // Handle browser back/forward buttons
    window.addEventListener("hashchange", () => {
        const hash = window.location.hash;
        if (hash) {
            switchToolkitTab(hash.slice(1));
        }
    });

    // Universal Clipboard Copy Helper (works in secure HTTPS, localhost, AND non-secure HTTP LAN IP contexts)
    async function copyToClipboard(text) {
        if (text == null) return false;
        text = String(text);

        // 1. Try modern async Clipboard API if available in secure context
        if (window.isSecureContext && navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
            try {
                await navigator.clipboard.writeText(text);
                return true;
            } catch (err) {
                console.warn("navigator.clipboard.writeText failed, falling back to execCommand:", err);
            }
        }

        // 2. Fallback: document.execCommand('copy') via temporary textarea (universal HTTP/LAN support)
        try {
            const textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.style.position = "fixed";
            textarea.style.top = "0";
            textarea.style.left = "0";
            textarea.style.width = "2em";
            textarea.style.height = "2em";
            textarea.style.padding = "0";
            textarea.style.border = "none";
            textarea.style.outline = "none";
            textarea.style.boxShadow = "none";
            textarea.style.background = "transparent";
            textarea.style.opacity = "0.01";
            textarea.style.zIndex = "-1";
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            if (typeof textarea.setSelectionRange === "function") {
                textarea.setSelectionRange(0, textarea.value.length);
            }
            const successful = document.execCommand("copy");
            document.body.removeChild(textarea);
            return !!successful;
        } catch (err) {
            console.error("document.execCommand fallback failed:", err);
            return false;
        }
    }

    window.copyToClipboard = copyToClipboard;

})();
