// Hash List Diff Analyzer Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const listAInput = document.getElementById("diff-list-a");
    const listBInput = document.getElementById("diff-list-b");
    const fileAInput = document.getElementById("diff-file-a");
    const fileBInput = document.getElementById("diff-file-b");
    const compareBtn = document.getElementById("diff-compare-btn");
    const clearBtn = document.getElementById("diff-clear-btn");
    const caseToggle = document.getElementById("diff-case-toggle");

    const summarySection = document.getElementById("diff-summary");
    const commonCountEl = document.getElementById("diff-common-count");
    const addedCountEl = document.getElementById("diff-added-count");
    const removedCountEl = document.getElementById("diff-removed-count");
    const dupCountAEl = document.getElementById("diff-dups-a");
    const dupCountBEl = document.getElementById("diff-dups-b");

    const tabCommonBtn = document.getElementById("diff-tab-common");
    const tabAddedBtn = document.getElementById("diff-tab-added");
    const tabRemovedBtn = document.getElementById("diff-tab-removed");

    const searchInput = document.getElementById("diff-search-input");
    const resultsContainer = document.getElementById("diff-results-container");
    const resultsList = document.getElementById("diff-results-list");

    const exportCsvBtn = document.getElementById("diff-export-csv");
    const exportJsonBtn = document.getElementById("diff-export-json");

    let currentDiffData = null;
    let activeTab = "common"; // 'common', 'added', 'removed'

    function showToast(msg) {
        let toast = document.querySelector(".toast");
        if (!toast) {
            toast = document.createElement("div");
            toast.className = "toast";
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.classList.add("show");
        clearTimeout(toast._timer);
        toast._timer = setTimeout(() => toast.classList.remove("show"), 2000);
    }

    if (fileAInput) {
        fileAInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => { listAInput.value = ev.target.result; showToast(`Loaded List A: ${e.target.files[0].name}`); };
                reader.readAsText(e.target.files[0]);
            }
        });
    }

    if (fileBInput) {
        fileBInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => { listBInput.value = ev.target.result; showToast(`Loaded List B: ${e.target.files[0].name}`); };
                reader.readAsText(e.target.files[0]);
            }
        });
    }

    async function runDiff() {
        const textA = listAInput ? listAInput.value.trim() : "";
        const textB = listBInput ? listBInput.value.trim() : "";

        if (!textA && !textB) {
            showToast("Please provide at least one list to analyze.");
            return;
        }

        if (compareBtn) {
            compareBtn.disabled = true;
            compareBtn.textContent = "Comparing...";
        }

        try {
            const isCaseSens = caseToggle ? caseToggle.checked : false;
            const res = await fetch("/api/diff", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    list_a: textA,
                    list_b: textB,
                    case_sensitive: isCaseSens,
                }),
            });
            const data = await res.json();
            currentDiffData = data;
            renderSummary(data.summary);
            renderTab();
            if (summarySection) summarySection.style.display = "flex";
            if (resultsContainer) resultsContainer.style.display = "block";
        } catch (err) {
            showToast("Error comparing hash lists.");
        } finally {
            if (compareBtn) {
                compareBtn.disabled = false;
                compareBtn.textContent = "Compare Lists";
            }
        }
    }

    function renderSummary(summary) {
        if (!summary) return;
        if (commonCountEl) commonCountEl.textContent = summary.common_count;
        if (addedCountEl) addedCountEl.textContent = summary.added_count;
        if (removedCountEl) removedCountEl.textContent = summary.removed_count;
        if (dupCountAEl) dupCountAEl.textContent = `${summary.duplicate_occurrences_a} dups in A`;
        if (dupCountBEl) dupCountBEl.textContent = `${summary.duplicate_occurrences_b} dups in B`;

        if (tabCommonBtn) tabCommonBtn.textContent = `Common (${summary.common_count})`;
        if (tabAddedBtn) tabAddedBtn.textContent = `Added in B (${summary.added_count})`;
        if (tabRemovedBtn) tabRemovedBtn.textContent = `Removed from A (${summary.removed_count})`;
    }

    function setTab(tabName) {
        activeTab = tabName;
        [tabCommonBtn, tabAddedBtn, tabRemovedBtn].forEach((b) => {
            if (b) b.classList.remove("active");
        });
        if (tabName === "common" && tabCommonBtn) tabCommonBtn.classList.add("active");
        else if (tabName === "added" && tabAddedBtn) tabAddedBtn.classList.add("active");
        else if (tabName === "removed" && tabRemovedBtn) tabRemovedBtn.classList.add("active");
        renderTab();
    }

    function renderTab() {
        if (!currentDiffData) return;

        const query = searchInput.value.trim().toLowerCase();
        let items = currentDiffData[activeTab] || [];

        if (query) {
            items = items.filter((it) => it.hash.toLowerCase().includes(query));
        }

        if (items.length === 0) {
            resultsList.innerHTML = `<div class="table-empty">No hashes found in ${activeTab.toUpperCase()} section.</div>`;
            return;
        }

        resultsList.innerHTML = items.map((item) => {
            let metaHtml = "";
            let badgeClass = "badge-common";
            let badgeText = "In Both Lists";

            if (activeTab === "common") {
                metaHtml = `
                    <span>Lines in A: <strong>${item.lines_in_a.join(", ")}</strong></span>
                    <span>Lines in B: <strong>${item.lines_in_b.join(", ")}</strong></span>
                `;
            } else if (activeTab === "added") {
                badgeClass = "badge-added";
                badgeText = "Added (+)";
                metaHtml = `<span>Lines in B: <strong>${item.lines_in_b.join(", ")}</strong></span>`;
            } else if (activeTab === "removed") {
                badgeClass = "badge-removed";
                badgeText = "Removed (-)";
                metaHtml = `<span>Lines in A: <strong>${item.lines_in_a.join(", ")}</strong></span>`;
            }

            return `
                <div class="diff-item-row ${activeTab}">
                    <div class="diff-hash-info">
                        <span class="diff-badge ${badgeClass}">${badgeText}</span>
                        <code class="diff-hash-val">${escapeHtml(item.hash)}</code>
                        <button class="table-copy-btn" data-val="${escapeHtml(item.hash)}" title="Copy Hash"><span class="material-symbols-outlined">content_copy</span></button>
                    </div>
                    <div class="diff-lines-info">
                        ${metaHtml}
                    </div>
                </div>
            `;
        }).join("");

        resultsList.querySelectorAll(".table-copy-btn").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const val = btn.getAttribute("data-val");
                if (val) {
                    await navigator.clipboard.writeText(val);
                    showToast("Hash copied to clipboard");
                }
            });
        });
    }

    function exportCsv() {
        if (!currentDiffData) return;

        const headers = ["Category", "Hash", "Lines_in_A", "Lines_in_B"];
        const rows = [];

        currentDiffData.common.forEach((c) => {
            rows.push(["COMMON", `"${c.hash.replace(/"/g, '""')}"`, `"${c.lines_in_a.join(';')}"`, `"${c.lines_in_b.join(';')}"`]);
        });
        currentDiffData.added.forEach((a) => {
            rows.push(["ADDED_IN_B", `"${a.hash.replace(/"/g, '""')}"`, '""', `"${a.lines_in_b.join(';')}"`]);
        });
        currentDiffData.removed.forEach((r) => {
            rows.push(["REMOVED_FROM_A", `"${r.hash.replace(/"/g, '""')}"`, `"${r.lines_in_a.join(';')}"`, '""']);
        });

        const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\r\n");
        downloadBlob(csvContent, "hash_list_diff_report.csv", "text/csv;charset=utf-8;");
    }

    function exportJson() {
        if (!currentDiffData) return;
        const jsonContent = JSON.stringify(currentDiffData, null, 2);
        downloadBlob(jsonContent, "hash_list_diff_report.json", "application/json;charset=utf-8;");
    }

    function downloadBlob(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast(`Exported ${filename}`);
    }

    function escapeHtml(str) {
        if (str == null) return "";
        const div = document.createElement("div");
        div.textContent = String(str);
        return div.innerHTML;
    }

    if (compareBtn) compareBtn.addEventListener("click", runDiff);
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (listAInput) listAInput.value = "";
            if (listBInput) listBInput.value = "";
            currentDiffData = null;
            if (summarySection) summarySection.style.display = "none";
            if (resultsContainer) resultsContainer.style.display = "none";
        });
    }

    if (tabCommonBtn) tabCommonBtn.addEventListener("click", () => setTab("common"));
    if (tabAddedBtn) tabAddedBtn.addEventListener("click", () => setTab("added"));
    if (tabRemovedBtn) tabRemovedBtn.addEventListener("click", () => setTab("removed"));

    if (searchInput) searchInput.addEventListener("input", renderTab);
    if (caseToggle) caseToggle.addEventListener("change", runDiff);

    if (exportCsvBtn) exportCsvBtn.addEventListener("click", exportCsv);
    if (exportJsonBtn) exportJsonBtn.addEventListener("click", exportJson);
})();
