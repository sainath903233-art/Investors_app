// static/js/theme.js
// Switches between light and dark theme and remembers the choice.

document.addEventListener("DOMContentLoaded", function () {
    const saved = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", saved);
    updateButton(saved);
});

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);   // remember for next time
    updateButton(next);
}

function updateButton(theme) {
    const btn = document.getElementById("themeBtn");
    if (btn) btn.textContent = theme === "light" ? "🌙 Dark" : "☀️ Light";
}
