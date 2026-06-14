// MediPredict AI - Chart.js Styling Configurations
// Provides global overrides for dark mode synchronization on canvas renderings

const ChartStyleHelper = {
    // Sync chart theme colors based on html elements
    getThemeColors: function() {
        const isDark = document.documentElement.getAttribute("data-bs-theme") === "dark";
        return {
            textColor: isDark ? "#94a3b8" : "#64748b",
            gridColor: isDark ? "#334155" : "#e2e8f0",
            primaryColor: "#0d6efd",
            dangerColor: "#dc3545",
            successColor: "#198754"
        };
    },
    
    // Apply styling overrides globally to Chart.js
    applyGlobalTheme: function(ChartInstance) {
        if (!ChartInstance) return;
        
        const colors = this.getThemeColors();
        ChartInstance.defaults.color = colors.textColor;
        ChartInstance.defaults.scale.grid.color = colors.gridColor;
    }
};
