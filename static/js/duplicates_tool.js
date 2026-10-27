// Duplicate Hash Detection Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const inputArea = document.getElementById("dup-input");
    const fileInput = document.getElementById("dup-file-input");
    const dropzone = document.getElementById("dup-dropzone");
    const scanBtn = document.getElementById("dup-scan-btn");
    const clearBtn = document.getElementById("dup-clear-btn");
    const caseToggle = document.getElementById("dup-case-toggle");

    const summarySection = document.getElementById("dup-summary");
    const totalLinesEl = document.getElementById("dup-total-lines");
    const uniqueCountEl = document.getElementById("dup-unique-count");
    const dupGroupsEl = document.getElementById("dup-groups-count");
    const repeatedTotalEl = document.getElementById("dup-repeated-total");

    const filterView = document.getElementById("dup-filter-view");
    const searchInput = document.getElementById("dup-search-input");
    const resultsContainer = document.getElementById("dup-results-container");
    const resultsList = document.getElementById("dup-results-list");

    const exportUniqueBtn = document.getElementById("dup-export-unique");
    const exportDupsBtn = document.getElementById("dup-export-dups");

    let currentData = null;

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

    if (dropzone) {
        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });
        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("dragover");
        });
        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFile(e.target.files[0]);
            }
        });
    }

    function handleFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            inputArea.value = e.target.result;
            showToast(`Loaded ${file.name}`);
        };
        reader.readAsText(file);
    }

    async function findDuplicates() {
        if (!inputArea) return;
        const text = inputArea.value.trim();
        if (!text) {
            showToast("Please enter or upload a list of hashes.");
            inputArea.focus();
            return;
        }

        if (scanBtn) {
            scanBtn.disabled = true;
            scanBtn.textContent = "Scanning...";
        }

        try {
            const isCaseSens = caseToggle ? caseToggle.checked : false;
            const res = await fetch("/api/duplicates", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text, case_sensitive: isCaseSens }),
            });
            const data = await res.json();
            currentData = data;
            renderSummary(data);
            renderList();
            if (summarySection) summarySection.style.display = "flex";
            if (resultsContainer) resultsContainer.style.display = "block";
        } catch (err) {
            showToast("Error processing duplicates.");
        } finally {
            if (scanBtn) {
                scanBtn.disabled = false;
                scanBtn.textContent = "Find Duplicates";
            }
        }
    }

    function renderSummary(data) {
        if (totalLinesEl) totalLinesEl.textContent = data.total_lines;
        if (uniqueCountEl) uniqueCountEl.textContent = data.unique_count;
        if (dupGroupsEl) dupGroupsEl.textContent = data.duplicate_groups_count;
        if (repeatedTotalEl) repeatedTotalEl.textContent = data.repeated_occurrences_count;
    }

    function renderList() {
        if (!currentData) return;

        const view = filterView.value; // 'all', 'duplicates_only', 'unique_only'
        const query = searchInput.value.trim().toLowerCase();

        let itemsToShow = [];

        if (view === "duplicates_only") {
            itemsToShow = currentData.duplicate_groups;
        } else if (view === "unique_only") {
            itemsToShow = currentData.unique_items;
        } else {
            // All items (duplicates first, then single unique)
            itemsToShow = [...currentData.duplicate_groups, ...currentData.unique_items];
        }

        if (query) {
            itemsToShow = itemsToShow.filter((it) => it.display_hash.toLowerCase().includes(query));
        }

        if (itemsToShow.length === 0) {
            resultsList.innerHTML = `<div class="table-empty">No items matching current view filter.</div>`;
            return;
        }

        resultsList.innerHTML = itemsToShow.map((item) => {
            const isDup = item.count > 1;
            const badge = isDup
                ? `<span class="badge-dup-count">${item.count} occurrences</span>`
                : `<span class="badge-unique">Unique (1 occurrence)</span>`;

            const lineList = item.lines.join(", ");

            return `
                <div class="dup-item-card ${isDup ? 'is-dup' : 'is-unique'}">
                    <div class="dup-header">
                        <div class="dup-hash-col">
                            <code class="dup-hash-text">${escapeHtml(item.display_hash)}</code>
                            <button class="table-copy-btn" data-val="${escapeHtml(item.display_hash)}" title="Copy Hash"><span class="material-symbols-outlined">content_copy</span></button>
                        </div>
                        ${badge}
                    </div>
                    <div class="dup-meta">
                        <span>Original Line${item.lines.length > 1 ? 's' : ''}: <strong>${escapeHtml(lineList)}</strong></span>
                    </div>
                </div>
            `;
        }).join("");

        resultsList.querySelectorAll(".table-copy-btn").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const val = btn.getAttribute("data-val");
                if (val) {
                    await (window.copyToClipboard ? window.copyToClipboard(val) : navigator.clipboard.writeText(val));
                    showToast("Hash copied to clipboard");
                }
            });
        });
    }

    function exportUnique() {
        if (!currentData) return;
        const allUniqueHashes = [
            ...currentData.duplicate_groups.map((g) => g.display_hash),
            ...currentData.unique_items.map((u) => u.display_hash),
        ];

        const textContent = allUniqueHashes.join("\r\n");
        downloadBlob(textContent, "unique_hashes_list.txt", "text/plain;charset=utf-8;");
    }

    function exportDuplicates() {
        if (!currentData || currentData.duplicate_groups.length === 0) {
            showToast("No duplicate groups to export.");
            return;
        }

        const headers = ["Hash", "Occurrence_Count", "Original_Lines"];
        const rows = currentData.duplicate_groups.map((g) => [
            `"${g.display_hash.replace(/"/g, '""')}"`,
            g.count,
            `"${g.lines.join(', ')}"`
        ]);

        const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\r\n");
        downloadBlob(csvContent, "duplicate_hashes_report.csv", "text/csv;charset=utf-8;");
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

    if (scanBtn) scanBtn.addEventListener("click", findDuplicates);
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (inputArea) {
                inputArea.value = "";
                inputArea.focus();
            }
            currentData = null;
            if (summarySection) summarySection.style.display = "none";
            if (resultsContainer) resultsContainer.style.display = "none";
        });
    }

    if (filterView) filterView.addEventListener("change", renderList);
    if (searchInput) searchInput.addEventListener("input", renderList);
    if (caseToggle) caseToggle.addEventListener("change", findDuplicates);

    if (exportUniqueBtn) exportUniqueBtn.addEventListener("click", exportUnique);
    if (exportDupsBtn) exportDupsBtn.addEventListener("click", exportDuplicates);
})();
