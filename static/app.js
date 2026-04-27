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

function initCrmAutoSubmitFilters() {
    document.querySelectorAll("[data-auto-submit='true']").forEach((form) => {
        form.querySelectorAll("select, input[type='date']").forEach((field) => {
            field.addEventListener("change", () => {
                form.requestSubmit();
            });
        });
    });
}

function initCrmDeleteConfirmation() {
    document.querySelectorAll("[data-confirm-delete]").forEach((element) => {
        element.addEventListener("click", (event) => {
            const message = element.getAttribute("data-confirm-delete") || "Are you sure?";
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });
}

function initCrmGanttToggles() {
    document.querySelectorAll("[data-gantt-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const groupId = button.getAttribute("data-gantt-toggle");
            const isExpanded = button.getAttribute("aria-expanded") !== "false";
            const nextExpanded = !isExpanded;

            button.setAttribute("aria-expanded", String(nextExpanded));
            button.classList.toggle("is-collapsed", !nextExpanded);

            document.querySelectorAll(`[data-gantt-child="${groupId}"]`).forEach((row) => {
                row.hidden = !nextExpanded;
            });
        });
    });
}

function showCrmToast(message, type = "success") {
    let toast = document.querySelector("[data-crm-toast]");

    if (!toast) {
        toast = document.createElement("div");
        toast.setAttribute("data-crm-toast", "true");
        document.body.appendChild(toast);
    }

    toast.className = `crm-board-toast is-${type} is-visible`;
    toast.textContent = message;

    window.clearTimeout(toast.hideTimer);
    toast.hideTimer = window.setTimeout(() => {
        toast.classList.remove("is-visible");
    }, 2200);
}

function parseCrmDate(value) {
    if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        return null;
    }

    const [year, month, day] = value.split("-").map(Number);
    const parsed = new Date(year, month - 1, day);

    if (
        parsed.getFullYear() !== year ||
        parsed.getMonth() !== month - 1 ||
        parsed.getDate() !== day
    ) {
        return null;
    }

    return parsed;
}

function formatCrmDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function addCrmDays(date, days) {
    const next = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    next.setDate(next.getDate() + days);
    return next;
}

function diffCrmDays(startDate, endDate) {
    const startValue = Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
    const endValue = Date.UTC(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
    return Math.round((endValue - startValue) / 86400000);
}

function clampNumber(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function initCrmGanttSchedule() {
    const board = document.querySelector("[data-gantt-board]");
    if (!board) {
        return;
    }

    const timelineStart = parseCrmDate(board.getAttribute("data-gantt-start"));
    const dayCount = parseInt(board.getAttribute("data-gantt-days") || "0", 10);

    if (!timelineStart || !dayCount) {
        return;
    }

    let activeDrag = null;

    function getCellWidth(grid) {
        const rect = grid.getBoundingClientRect();
        return rect.width / dayCount;
    }

    function getBarRange(bar) {
        const startDate = parseCrmDate(bar.getAttribute("data-start-date"));
        const dueDate = parseCrmDate(bar.getAttribute("data-due-date"));

        if (!startDate || !dueDate) {
            return null;
        }

        const startIndex = clampNumber(diffCrmDays(timelineStart, startDate), 0, dayCount - 1);
        const endIndex = clampNumber(diffCrmDays(timelineStart, dueDate), 0, dayCount - 1);
        return {
            startIndex: Math.min(startIndex, endIndex),
            endIndex: Math.max(startIndex, endIndex),
        };
    }

    function captureBarSnapshot(bar) {
        return {
            gridColumn: bar.style.gridColumn,
            startDate: bar.getAttribute("data-start-date"),
            dueDate: bar.getAttribute("data-due-date"),
            ariaLabel: bar.getAttribute("aria-label") || "",
        };
    }

    function restoreBarSnapshot(bar, snapshot) {
        bar.style.gridColumn = snapshot.gridColumn;
        bar.setAttribute("data-start-date", snapshot.startDate);
        bar.setAttribute("data-due-date", snapshot.dueDate);
        bar.setAttribute("aria-label", snapshot.ariaLabel);
        bar.classList.remove("is-dirty");
        delete bar.dataset.pendingStartDate;
        delete bar.dataset.pendingDueDate;
    }

    function setBarRange(bar, startIndex, endIndex) {
        const nextStart = Math.min(startIndex, endIndex);
        const nextEnd = Math.max(startIndex, endIndex);
        const span = nextEnd - nextStart + 1;
        const startValue = formatCrmDate(addCrmDays(timelineStart, nextStart));
        const dueValue = formatCrmDate(addCrmDays(timelineStart, nextEnd));

        bar.style.gridColumn = `${nextStart + 1} / span ${span}`;
        bar.dataset.pendingStartDate = startValue;
        bar.dataset.pendingDueDate = dueValue;
        bar.setAttribute("aria-label", `Schedule ${startValue} to ${dueValue}`);
        bar.classList.add("is-dirty");
    }

    async function persistBarRange(bar, snapshot) {
        const updateUrl = bar.getAttribute("data-update-url");
        const startDate = bar.dataset.pendingStartDate;
        const dueDate = bar.dataset.pendingDueDate;

        if (!updateUrl || !startDate || !dueDate) {
            return;
        }

        bar.classList.add("is-saving");

        try {
            const response = await fetch(updateUrl, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    start_date: startDate,
                    due_date: dueDate,
                }),
            });
            const result = await response.json().catch(() => ({}));

            if (!response.ok || result.ok === false) {
                throw new Error(result.message || "Timeline could not be updated.");
            }

            bar.setAttribute("data-start-date", result.start_date || startDate);
            bar.setAttribute("data-due-date", result.due_date || dueDate);
            bar.classList.remove("is-dirty", "is-clipped-start", "is-clipped-end");
            delete bar.dataset.pendingStartDate;
            delete bar.dataset.pendingDueDate;
            showCrmToast("Timeline updated.");
        } catch (error) {
            restoreBarSnapshot(bar, snapshot);
            showCrmToast(error.message || "Could not update timeline.", "error");
        } finally {
            bar.classList.remove("is-saving");
        }
    }

    function startBarDrag(event, bar) {
        if (event.button !== 0) {
            return;
        }

        const grid = bar.closest("[data-gantt-grid]");
        const range = getBarRange(bar);
        if (!grid || !range) {
            return;
        }

        const handle = event.target.closest("[data-gantt-handle]");
        activeDrag = {
            bar,
            grid,
            mode: handle ? handle.getAttribute("data-gantt-handle") : "move",
            pointerId: event.pointerId,
            originX: event.clientX,
            cellWidth: getCellWidth(grid),
            startIndex: range.startIndex,
            endIndex: range.endIndex,
            snapshot: captureBarSnapshot(bar),
            changed: false,
        };

        bar.classList.add("is-dragging");
        bar.setPointerCapture(event.pointerId);
        event.preventDefault();
    }

    function updateBarDrag(event) {
        if (!activeDrag || event.pointerId !== activeDrag.pointerId) {
            return;
        }

        const delta = Math.round((event.clientX - activeDrag.originX) / activeDrag.cellWidth);
        let nextStart = activeDrag.startIndex;
        let nextEnd = activeDrag.endIndex;

        if (activeDrag.mode === "start") {
            nextStart = clampNumber(activeDrag.startIndex + delta, 0, nextEnd);
        } else if (activeDrag.mode === "end") {
            nextEnd = clampNumber(activeDrag.endIndex + delta, nextStart, dayCount - 1);
        } else {
            const span = activeDrag.endIndex - activeDrag.startIndex;
            nextStart = clampNumber(activeDrag.startIndex + delta, 0, dayCount - 1 - span);
            nextEnd = nextStart + span;
        }

        if (nextStart === activeDrag.startIndex && nextEnd === activeDrag.endIndex) {
            return;
        }

        activeDrag.changed = true;
        setBarRange(activeDrag.bar, nextStart, nextEnd);
    }

    async function finishBarDrag(event) {
        if (!activeDrag || event.pointerId !== activeDrag.pointerId) {
            return;
        }

        const drag = activeDrag;
        activeDrag = null;

        drag.bar.classList.remove("is-dragging");
        if (drag.bar.hasPointerCapture(event.pointerId)) {
            drag.bar.releasePointerCapture(event.pointerId);
        }

        if (drag.changed) {
            await persistBarRange(drag.bar, drag.snapshot);
        } else if (drag.mode === "move") {
            openBarDetail(drag.bar);
        }
    }

    function cancelBarDrag(event) {
        if (!activeDrag || event.pointerId !== activeDrag.pointerId) {
            return;
        }

        const drag = activeDrag;
        activeDrag = null;
        drag.bar.classList.remove("is-dragging");
        restoreBarSnapshot(drag.bar, drag.snapshot);
    }

    async function nudgeBar(bar, mode, direction) {
        const range = getBarRange(bar);
        if (!range) {
            return;
        }

        const snapshot = captureBarSnapshot(bar);
        let nextStart = range.startIndex;
        let nextEnd = range.endIndex;

        if (mode === "start") {
            nextStart = clampNumber(range.startIndex + direction, 0, range.endIndex);
        } else if (mode === "end") {
            nextEnd = clampNumber(range.endIndex + direction, range.startIndex, dayCount - 1);
        } else {
            const span = range.endIndex - range.startIndex;
            nextStart = clampNumber(range.startIndex + direction, 0, dayCount - 1 - span);
            nextEnd = nextStart + span;
        }

        if (nextStart === range.startIndex && nextEnd === range.endIndex) {
            return;
        }

        setBarRange(bar, nextStart, nextEnd);
        await persistBarRange(bar, snapshot);
    }

    function openBarDetail(bar) {
        const detailUrl = bar.getAttribute("data-detail-url");
        if (detailUrl) {
            window.location.href = detailUrl;
        }
    }

    board.querySelectorAll("[data-gantt-bar]").forEach((bar) => {
        bar.addEventListener("pointerdown", (event) => startBarDrag(event, bar));
        bar.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openBarDetail(bar);
                return;
            }

            const direction = event.key === "ArrowLeft" ? -1 : event.key === "ArrowRight" ? 1 : 0;
            if (!direction) {
                return;
            }

            event.preventDefault();
            const mode = event.altKey ? "start" : event.shiftKey ? "end" : "move";
            nudgeBar(bar, mode, direction);
        });
    });

    document.addEventListener("pointermove", updateBarDrag);
    document.addEventListener("pointerup", finishBarDrag);
    document.addEventListener("pointercancel", cancelBarDrag);
}

function initCrmBoardDragAndDrop() {
    const board = document.querySelector("[data-board]");
    if (!board) {
        return;
    }

    let draggedCard = null;
    let sourceDropzone = null;
    let sourceNextSibling = null;
    let dropped = false;

    function getColumn(element) {
        return element ? element.closest("[data-board-column]") : null;
    }

    function getDropzone(column) {
        return column ? column.querySelector("[data-board-dropzone]") : null;
    }

    function refreshColumn(column) {
        if (!column) {
            return;
        }

        const cards = column.querySelectorAll("[data-board-card]");
        const count = column.querySelector("[data-board-count]");
        const emptyState = column.querySelector("[data-board-empty]");

        if (count) {
            count.textContent = String(cards.length);
        }

        if (emptyState) {
            emptyState.hidden = cards.length > 0;
        }
    }

    function refreshAllColumns() {
        board.querySelectorAll("[data-board-column]").forEach(refreshColumn);
    }

    function showBoardToast(message, type = "success") {
        let toast = document.querySelector("[data-board-toast]");

        if (!toast) {
            toast = document.createElement("div");
            toast.setAttribute("data-board-toast", "true");
            document.body.appendChild(toast);
        }

        toast.className = `crm-board-toast is-${type} is-visible`;
        toast.textContent = message;

        window.clearTimeout(toast.hideTimer);
        toast.hideTimer = window.setTimeout(() => {
            toast.classList.remove("is-visible");
        }, 2200);
    }

    function getDropBeforeCard(dropzone, pointerY) {
        const cards = [...dropzone.querySelectorAll("[data-board-card]:not(.is-dragging)")];

        return cards.reduce(
            (closest, card) => {
                const rect = card.getBoundingClientRect();
                const offset = pointerY - rect.top - rect.height / 2;

                if (offset < 0 && offset > closest.offset) {
                    return { offset, element: card };
                }

                return closest;
            },
            { offset: Number.NEGATIVE_INFINITY, element: null }
        ).element;
    }

    function placeCard(dropzone, card, beforeCard = null) {
        const emptyState = dropzone.querySelector("[data-board-empty]");
        dropzone.insertBefore(card, beforeCard || emptyState);
    }

    function restoreCard(card, previousDropzone, previousNextSibling) {
        if (!card || !previousDropzone) {
            return;
        }

        previousDropzone.insertBefore(card, previousNextSibling);
        refreshColumn(getColumn(previousDropzone));
    }

    async function persistStatus(card, newStatus) {
        const actionId = card.getAttribute("data-action-id");
        const previousStatus = card.getAttribute("data-current-status");

        if (!actionId || !newStatus || previousStatus === newStatus) {
            return true;
        }

        card.classList.add("is-saving");

        try {
            const response = await fetch(`/actions/${encodeURIComponent(actionId)}/status`, {
                method: "POST",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ action_status: newStatus }),
            });
            const result = await response.json().catch(() => ({}));

            if (!response.ok || result.ok === false) {
                throw new Error(result.message || "Status could not be updated.");
            }

            card.setAttribute("data-current-status", result.action_status || newStatus);

            if (newStatus === "Completed") {
                const chipRow = card.querySelector(".crm-chip-row");
                if (chipRow) {
                    chipRow.innerHTML = "";
                }
            }

            showBoardToast("Status updated. Other views now use the same synced data.");
            return true;
        } catch (error) {
            showBoardToast(error.message || "Could not update status. Card was moved back.", "error");
            return false;
        } finally {
            card.classList.remove("is-saving");
        }
    }

    board.querySelectorAll("[data-board-card]").forEach((card) => {
        card.addEventListener("dragstart", (event) => {
            if (
                event.target instanceof Element &&
                event.target.closest("[data-board-no-drag], a, button, input, select, textarea")
            ) {
                event.preventDefault();
                return;
            }

            draggedCard = card;
            sourceDropzone = card.parentElement;
            sourceNextSibling = card.nextElementSibling;
            dropped = false;

            card.classList.add("is-dragging");

            if (event.dataTransfer) {
                event.dataTransfer.effectAllowed = "move";
                event.dataTransfer.setData("text/plain", card.getAttribute("data-action-id") || "");
            }
        });

        card.addEventListener("dragend", () => {
            if (!dropped) {
                restoreCard(draggedCard, sourceDropzone, sourceNextSibling);
            }

            if (draggedCard) {
                draggedCard.classList.remove("is-dragging");
            }

            board.querySelectorAll(".is-drag-over").forEach((column) => {
                column.classList.remove("is-drag-over");
            });

            refreshAllColumns();
            draggedCard = null;
            sourceDropzone = null;
            sourceNextSibling = null;
            dropped = false;
        });
    });

    board.querySelectorAll("[data-board-column]").forEach((column) => {
        const dropzone = getDropzone(column);

        if (!dropzone) {
            return;
        }

        column.addEventListener("dragover", (event) => {
            if (!draggedCard) {
                return;
            }

            event.preventDefault();
            column.classList.add("is-drag-over");

            if (event.dataTransfer) {
                event.dataTransfer.dropEffect = "move";
            }
        });

        column.addEventListener("dragleave", (event) => {
            if (!column.contains(event.relatedTarget)) {
                column.classList.remove("is-drag-over");
            }
        });

        column.addEventListener("drop", async (event) => {
            if (!draggedCard) {
                return;
            }

            event.preventDefault();
            dropped = true;
            column.classList.remove("is-drag-over");

            const card = draggedCard;
            const previousDropzone = sourceDropzone;
            const previousNextSibling = sourceNextSibling;
            const previousColumn = getColumn(previousDropzone);
            const beforeCard = getDropBeforeCard(dropzone, event.clientY);
            const newStatus = column.getAttribute("data-board-column") || "";

            placeCard(dropzone, card, beforeCard);
            refreshColumn(previousColumn);
            refreshColumn(column);

            const saved = await persistStatus(card, newStatus);
            if (!saved) {
                restoreCard(card, previousDropzone, previousNextSibling);
                refreshColumn(column);
            }
        });
    });

    refreshAllColumns();
}

function initCrmCreateModals() {
    const modalMap = {
        project: document.getElementById("crmProjectModal"),
        action: document.getElementById("crmActionModal"),
    };
    const body = document.body;
    let activeModal = null;

    function focusFirstField(modal) {
        const field = modal.querySelector("input:not([type='hidden']), select, textarea, button");
        if (field) {
            field.focus();
        }
    }

    function closeModal() {
        if (!activeModal) {
            return;
        }

        activeModal.hidden = true;
        activeModal = null;
        body.classList.remove("modal-open");
    }

    function openModal(type, trigger) {
        const modal = modalMap[type];
        if (!modal) {
            return;
        }

        Object.values(modalMap).forEach((item) => {
            if (item) {
                item.hidden = true;
            }
        });

        const form = modal.querySelector("form");
        if (form) {
            form.reset();
        }

        if (type === "action" && trigger) {
            const projectId = trigger.getAttribute("data-crm-project-id");
            const projectSelect = modal.querySelector("[data-crm-action-project-select]");
            if (projectId && projectSelect) {
                projectSelect.value = projectId;
            }
        }

        modal.hidden = false;
        activeModal = modal;
        body.classList.add("modal-open");

        window.requestAnimationFrame(() => focusFirstField(modal));
    }

    document.querySelectorAll("[data-crm-modal-open]").forEach((trigger) => {
        trigger.addEventListener("click", (event) => {
            const type = trigger.getAttribute("data-crm-modal-open");
            if (!modalMap[type]) {
                return;
            }

            event.preventDefault();
            openModal(type, trigger);
        });
    });

    Object.values(modalMap).forEach((modal) => {
        if (!modal) {
            return;
        }

        modal.querySelectorAll("[data-crm-modal-close]").forEach((element) => {
            element.addEventListener("click", closeModal);
        });
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeModal();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initCrmAutoSubmitFilters();
    initCrmDeleteConfirmation();
    initCrmGanttToggles();
    initCrmGanttSchedule();
    initCrmBoardDragAndDrop();
    initCrmCreateModals();
});
