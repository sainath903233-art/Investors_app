function toggleTheme() {

    const html = document.documentElement;
    const button = document.getElementById("themeBtn");

    const currentTheme = html.getAttribute("data-theme");

    if (currentTheme === "dark") {

        html.setAttribute("data-theme", "light");

        if (button) {
            button.textContent = "🌙";
            button.title = "Dark Mode";
        }

        localStorage.setItem("theme", "light");

    } else {

        html.setAttribute("data-theme", "dark");

        if (button) {
            button.textContent = "☀️";
            button.title = "Light Mode";
        }

        localStorage.setItem("theme", "dark");
    }
}


/* Load saved theme when page opens */

document.addEventListener("DOMContentLoaded", function () {

    const html = document.documentElement;
    const button = document.getElementById("themeBtn");

    const savedTheme =
        localStorage.getItem("theme") || "light";

    html.setAttribute("data-theme", savedTheme);

    if (button) {

        if (savedTheme === "dark") {
            button.textContent = "☀️";
            button.title = "Light Mode";
        } else {
            button.textContent = "🌙";
            button.title = "Dark Mode";
        }

    }

});