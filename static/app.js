function parseChartData(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        return null;
    }

    try {
        return JSON.parse(element.textContent);
    } catch (error) {
        return null;
    }
}

function buildChart(canvasId, configuration) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || typeof Chart === "undefined") {
        return null;
    }

    return new Chart(canvas, configuration);
}

function defaultFontFamily() {
    return "'Aptos', 'Trebuchet MS', 'Segoe UI', sans-serif";
}

function setChartDefaults() {
    if (typeof Chart === "undefined") {
        return;
    }

    Chart.defaults.font.family = defaultFontFamily();
    Chart.defaults.color = "#54697f";
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 16;
}

function buildDoughnutChart(canvasId, labels, values, colors) {
    return buildChart(canvasId, {
        type: "doughnut",
        data: {
            labels,
            datasets: [
                {
                    data: values,
                    backgroundColor: colors,
                    borderColor: "#ffffff",
                    borderWidth: 4,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            cutout: "68%",
        },
    });
}

function buildBarChart(canvasId, labels, values, colors, label = "Records") {
    return buildChart(canvasId, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label,
                    data: values,
                    borderRadius: 14,
                    backgroundColor: colors,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                    },
                    grid: {
                        color: "rgba(84, 105, 127, 0.12)",
                    },
                },
            },
        },
    });
}

function buildLineChart(canvasId, labels, values, label = "Updated records") {
    return buildChart(canvasId, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label,
                    data: values,
                    borderColor: "#2f6fed",
                    backgroundColor: "rgba(47, 111, 237, 0.14)",
                    fill: true,
                    borderWidth: 3,
                    tension: 0.35,
                    pointRadius: 4,
                    pointHoverRadius: 5,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                },
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                    },
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0,
                    },
                    grid: {
                        color: "rgba(84, 105, 127, 0.12)",
                    },
                },
            },
        },
    });
}

function initDashboardCharts() {
    const chartData = parseChartData("dashboard-chart-data");
    if (!chartData) {
        return;
    }

    buildDoughnutChart(
        "dashboardModuleChart",
        chartData.modules.labels,
        chartData.modules.values,
        ["#bfd3ff", "#85d6ff", "#a4e0c2", "#ffd79d"]
    );

    buildBarChart(
        "dashboardStageChart",
        chartData.stages.labels,
        chartData.stages.values,
        ["#d9e4fb", "#b7cdfb", "#9ec0ff", "#84d3ff", "#7dc9b1", "#ffcf94", "#f3a6a6"],
        "Projects"
    );

    buildBarChart(
        "dashboardSeverityChart",
        chartData.severity.labels,
        chartData.severity.values,
        ["#f39f9f", "#f6c28f", "#9ec0ff", "#d9e4fb", "#cde6db"],
        "Open issues"
    );
}

function initReportCharts() {
    const chartData = parseChartData("report-chart-data");
    if (!chartData) {
        return;
    }

    buildDoughnutChart(
        "reportModuleChart",
        chartData.modules.labels,
        chartData.modules.values,
        ["#bfd3ff", "#85d6ff", "#a4e0c2", "#ffd79d"]
    );

    buildBarChart(
        "reportStageChart",
        chartData.stages.labels,
        chartData.stages.values,
        ["#d9e4fb", "#b7cdfb", "#9ec0ff", "#84d3ff", "#7dc9b1", "#ffcf94", "#f3a6a6"],
        "Projects"
    );

    buildBarChart(
        "reportSeverityChart",
        chartData.severity.labels,
        chartData.severity.values,
        ["#f39f9f", "#f6c28f", "#9ec0ff", "#d9e4fb", "#cde6db"],
        "Issues"
    );

    buildLineChart(
        "reportMonthlyChart",
        chartData.monthly.labels,
        chartData.monthly.values,
        "Updated records"
    );
}

function initModuleCharts() {
    const chartData = parseChartData("module-chart-data");
    if (!chartData) {
        return;
    }

    buildBarChart(
        "modulePrimaryChart",
        chartData.primary.labels,
        chartData.primary.values,
        ["#bfd3ff", "#85d6ff", "#a4e0c2", "#ffd79d", "#f3a6a6", "#d9e4fb", "#c9d7ee", "#e8eff8"],
        "Records"
    );

    buildDoughnutChart(
        "moduleSecondaryChart",
        chartData.secondary.labels,
        chartData.secondary.values,
        ["#bfd3ff", "#85d6ff", "#a4e0c2", "#f3a6a6"]
    );
}

function initCreateModal() {
    const modalShell = document.getElementById("createModalShell");
    if (!modalShell) {
        return;
    }

    const body = document.body;
    const titleInput = document.getElementById("createModalTitleInput");
    const categorySelect = document.getElementById("createModalCategory");
    const statusSelect = document.getElementById("createModalStatus");
    const fullEditorLink = document.getElementById("createModalFullEditor");
    const footerEditorLink = document.getElementById("createModalOpenEditor");
    const form = modalShell.querySelector(".create-modal-form");
    const moreFieldsButton = document.getElementById("createModalMoreFields");
    const extraFields = document.getElementById("createModalExtraFields");
    const createLinks = document.querySelectorAll("a[href*='/records/new'], a[href*='/tasks/new']");

    if (!form || !titleInput || !categorySelect || !statusSelect) {
        return;
    }

    const defaultCategory = categorySelect.value;
    const defaultStatus = statusSelect.value;

    function buildEditorUrl(params) {
        const url = new URL(form.action, window.location.origin);

        if (params.category) {
            url.searchParams.set("category", params.category);
        }

        if (params.status) {
            url.searchParams.set("status", params.status);
        }

        return `${url.pathname}${url.search}`;
    }

    function setEditorLinks(params) {
        const editorUrl = buildEditorUrl(params);

        if (fullEditorLink) {
            fullEditorLink.href = editorUrl;
        }

        if (footerEditorLink) {
            footerEditorLink.href = editorUrl;
        }
    }

    function openModal(params = {}) {
        form.reset();
        categorySelect.value = params.category || defaultCategory;
        statusSelect.value = params.status || defaultStatus;
        setEditorLinks(params);

        if (extraFields) {
            extraFields.hidden = true;
        }

        if (moreFieldsButton) {
            moreFieldsButton.textContent = "+ Create new field";
        }

        modalShell.hidden = false;
        body.classList.add("modal-open");

        window.requestAnimationFrame(() => {
            titleInput.focus();
        });
    }

    function closeModal() {
        modalShell.hidden = true;
        body.classList.remove("modal-open");
    }

    categorySelect.addEventListener("change", () => {
        setEditorLinks({
            category: categorySelect.value,
            status: statusSelect.value,
        });
    });

    statusSelect.addEventListener("change", () => {
        setEditorLinks({
            category: categorySelect.value,
            status: statusSelect.value,
        });
    });

    createLinks.forEach((link) => {
        if (link.hasAttribute("data-create-modal-bypass")) {
            return;
        }

        link.addEventListener("click", (event) => {
            const href = link.getAttribute("href");
            if (!href) {
                return;
            }

            const url = new URL(href, window.location.origin);

            if (!["/records/new", "/tasks/new"].includes(url.pathname)) {
                return;
            }

            event.preventDefault();
            openModal({
                category: url.searchParams.get("category") || "",
                status: url.searchParams.get("status") || "",
            });
        });
    });

    modalShell.querySelectorAll("[data-create-modal-close]").forEach((element) => {
        element.addEventListener("click", closeModal);
    });

    if (moreFieldsButton && extraFields) {
        moreFieldsButton.addEventListener("click", () => {
            extraFields.hidden = !extraFields.hidden;
            moreFieldsButton.textContent = extraFields.hidden ? "+ Create new field" : "Hide extra fields";
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !modalShell.hidden) {
            closeModal();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setChartDefaults();
    initDashboardCharts();
    initReportCharts();
    initModuleCharts();
    initCreateModal();
});
