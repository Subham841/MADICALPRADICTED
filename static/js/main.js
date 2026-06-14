// MediPredict AI - Main Javascript Operations

document.addEventListener("DOMContentLoaded", function () {
    // 1. Dark Mode / Theme Toggle System
    const themeToggleBtn = document.getElementById("theme-toggle");
    const themeToggleIcon = document.getElementById("theme-toggle-icon");
    const htmlElement = document.documentElement;

    // Load saved theme or fall back to system preferences
    const savedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (systemPrefersDark) {
        setTheme("dark");
    } else {
        setTheme("light");
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            const currentTheme = htmlElement.getAttribute("data-bs-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            setTheme(newTheme);
        });
    }

    function setTheme(theme) {
        htmlElement.setAttribute("data-bs-theme", theme);
        localStorage.setItem("theme", theme);
        
        // Update toggler icon
        if (themeToggleIcon) {
            if (theme) {
                if (theme === "dark") {
                    themeToggleIcon.className = "fa-solid fa-sun fs-5 text-warning";
                } else {
                    themeToggleIcon.className = "fa-solid fa-moon fs-5 text-secondary";
                }
            }
        }
    }

    // 2. Auto-Dismiss Flash Alerts
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Check if BS dismiss works, otherwise standard transition fade
            const bsAlert = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000); // Fades alerts after 5 seconds
    });

    // 3. HTML5 Bootstrap Form Validation
    const validationForms = document.querySelectorAll(".needs-validation");
    Array.from(validationForms).forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        }, false);
    });
});
