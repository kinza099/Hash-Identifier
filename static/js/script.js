// Theme toggle logic — persists choice in-memory for the session
(function () {
    const root = document.documentElement;
    const toggleBtn = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");

    // Default theme
    let currentTheme = root.getAttribute("data-theme") || "dark";

    function applyTheme(theme) {
        root.setAttribute("data-theme", theme);
        icon.textContent = theme === "dark" ? "🌙" : "☀️";
        currentTheme = theme;
        window.__hashToolTheme = theme; // keep in memory across page navigations in same tab session
    }

    // Restore theme if previously set in this browser session (memory var survives only same JS context,
    // so we also check a simple in-page flag set by server-render fallback)
    applyTheme(currentTheme);

    toggleBtn.addEventListener("click", function () {
        const next = currentTheme === "dark" ? "light" : "dark";
        applyTheme(next);
        window.dispatchEvent(new CustomEvent("themechange", { detail: { theme: next } }));
    });
})();
