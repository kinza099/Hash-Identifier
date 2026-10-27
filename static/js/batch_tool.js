// Batch Hash Scanner Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const inputArea = document.getElementById("batch-input");
    const fileInput = document.getElementById("batch-file-input");
    const scanBtn = document.getElementById("batch-scan-btn");
    const clearBtn = document.getElementById("batch-clear-btn");
    const dropzone = document.getElementById("batch-dropzone");

    const summarySection = document.getElementById("batch-summary");
    const totalCountEl = document.getElementById("batch-total-count");
    const validCountEl = document.getElementById("batch-valid-count");
    const invalidCountEl = document.getElementById("batch-invalid-count");
    const duplicateCountEl = document.getElementById("batch-duplicate-count");
    const uniqueCountEl = document.getElementById("batch-unique-count");

    const searchInput = document.getElementById("batch-search-input");
    const filterValidity = document.getElementById("batch-filter-validity");
    const filterConfidence = document.getElementById("batch-filter-confidence");
    const resultsTableBody = document.getElementById("batch-table-body");
    const resultsContainer = document.getElementById("batch-results-container");

    const exportCsvBtn = document.getElementById("batch-export-csv");
    const exportJsonBtn = document.getElementById("batch-export-json");

    let currentBatchData = null;
    let filteredResults = [];

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

    // Drag and drop handling
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
        reader.onload = function (e) {
            inputArea.value = e.target.result;
            showToast(`Loaded ${file.name} (${formatBytes(file.size)})`);
        };
        reader.readAsText(file);
    }

    function formatBytes(bytes) {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    async function runBatchScan() {
        if (!inputArea) return;
        const text = inputArea.value.trim();
        if (!text) {
            showToast("Please paste hashes or upload a TXT/CSV file first.");
            inputArea.focus();
            return;
        }

        if (scanBtn) {
            scanBtn.disabled = true;
            scanBtn.textContent = "Scanning Batch...";
        }

        try {
            const isCsv = text.includes(",") && (text.includes("\n") || text.includes("\r"));
            const res = await fetch("/api/batch-identify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text, is_csv: isCsv }),
            });
            const data = await res.json();
            currentBatchData = data;
            renderBatchSummary(data);
            applyFilters();
            if (resultsContainer) resultsContainer.style.display = "block";
            if (summarySection) summarySection.style.display = "flex";
        } catch (err) {
            showToast("Error scanning batch. Please verify input format.");
        } finally {
            if (scanBtn) {
                scanBtn.disabled = false;
                scanBtn.textContent = "Scan Hashes";
            }
        }
    }

    function renderBatchSummary(data) {
        if (totalCountEl) totalCountEl.textContent = data.total_entries;
        if (validCountEl) validCountEl.textContent = data.valid_count;
        if (invalidCountEl) invalidCountEl.textContent = data.invalid_count;
        if (duplicateCountEl) duplicateCountEl.textContent = data.total_duplicate_entries;
        if (uniqueCountEl) uniqueCountEl.textContent = data.unique_hashes_count;
    }

    function applyFilters() {
        if (!currentBatchData || !currentBatchData.results) return;

        const query = searchInput.value.trim().toLowerCase();
        const validity = filterValidity.value; // 'all', 'valid', 'invalid'
        const confidence = filterConfidence.value; // 'all', 'high', 'medium', 'none'

        filteredResults = currentBatchData.results.filter((item) => {
            if (query && !item.input.toLowerCase().includes(query)) {
                return false;
            }
            if (validity === "valid" && !item.valid) return false;
            if (validity === "invalid" && item.valid) return false;

            if (confidence !== "all" && item.confidence !== confidence) return false;

            return true;
        });

        renderBatchTable(filteredResults);
    }

    function renderBatchTable(items) {
        if (!items || items.length === 0) {
            resultsTableBody.innerHTML = `<tr><td colspan="7" class="table-empty">No matching entries found.</td></tr>`;
            return;
        }

        resultsTableBody.innerHTML = items
            .map((item) => {
                const statusBadge = item.valid
                    ? `<span class="badge-status valid">Valid</span>`
                    : (item.status === "EMPTY" ? `<span class="badge-status empty">Empty</span>` : `<span class="badge-status invalid">Invalid</span>`);

                const confBadge = item.confidence !== "none"
                    ? `<span class="badge-conf ${item.confidence}">${escapeHtml(item.confidence)}</span>`
                    : `<span class="badge-conf none">—</span>`;

                const dupBadge = item.is_duplicate
                    ? `<span class="badge-dup" title="Appears on lines: ${item.duplicate_lines ? item.duplicate_lines.join(', ') : ''}">${item.duplicate_occurrences}x</span>`
                    : "";

                const scorePill = item.score ? `<span class="table-score">${item.score}%</span>` : "";

                const displayHash = item.input
                    ? (item.input.length > 28 ? item.input.slice(0, 26) + "…" : item.input)
                    : "(blank line)";

                const ambiguityWarningIcon = item.ambiguity_warning
                    ? `<span class="warning-icon" title="${escapeHtml(item.ambiguity_warning)}"><span class="material-symbols-outlined">warning</span></span>`
                    : "";

                return `
                    <tr class="${item.valid ? '' : 'row-invalid'}">
                        <td class="col-line">${item.line_number}</td>
                        <td class="col-hash">
                            <code class="hash-code" title="${escapeHtml(item.input)}">${escapeHtml(displayHash)}</code>
                            ${dupBadge}
                            <button class="table-copy-btn" data-value="${escapeHtml(item.input)}" title="Copy full hash"><span class="material-symbols-outlined">content_copy</span></button>
                        </td>
                        <td class="col-algs">${escapeHtml(item.primary_algorithm)} ${ambiguityWarningIcon}</td>
                        <td class="col-conf">${confBadge} ${scorePill}</td>
                        <td class="col-status">${statusBadge}</td>
                        <td class="col-actions">
                            ${item.input ? `<button class="btn-inspect" data-hash="${escapeHtml(item.input)}" title="Inspect in Single Identifier"><span class="material-symbols-outlined">search</span> Inspect</button>` : ""}
                        </td>
                    </tr>
                `;
            })
            .join("");

        // Attach action events
        resultsTableBody.querySelectorAll(".table-copy-btn").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const val = btn.getAttribute("data-value");
                if (val) {
                    await (window.copyToClipboard ? window.copyToClipboard(val) : navigator.clipboard.writeText(val));
                    showToast("Hash copied to clipboard");
                }
            });
        });

        resultsTableBody.querySelectorAll(".btn-inspect").forEach((btn) => {
            btn.addEventListener("click", () => {
                const val = btn.getAttribute("data-hash");
                if (window.inspectSingleHash && val) {
                    window.inspectSingleHash(val);
                }
            });
        });
    }

    function exportToCsv() {
        if (!currentBatchData || !currentBatchData.results) {
            showToast("No scan results to export.");
            return;
        }

        const headers = ["Line", "Hash", "Valid", "Primary_Algorithm", "Confidence", "Score", "Duplicate_Count", "Ambiguity_Warning"];
        const rows = currentBatchData.results.map((r) => [
            r.line_number,
            `"${(r.input || '').replace(/"/g, '""')}"`,
            r.valid,
            `"${(r.primary_algorithm || '').replace(/"/g, '""')}"`,
            r.confidence,
            r.score,
            r.duplicate_occurrences || 1,
            `"${(r.ambiguity_warning || '').replace(/"/g, '""')}"`
        ]);

        const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\r\n");
        downloadBlob(csvContent, "batch_hash_scan_results.csv", "text/csv;charset=utf-8;");
    }

    function exportToJson() {
        if (!currentBatchData) {
            showToast("No scan results to export.");
            return;
        }
        const jsonContent = JSON.stringify(currentBatchData, null, 2);
        downloadBlob(jsonContent, "batch_hash_scan_results.json", "application/json;charset=utf-8;");
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

    if (scanBtn) scanBtn.addEventListener("click", runBatchScan);
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            if (inputArea) {
                inputArea.value = "";
                inputArea.focus();
            }
            currentBatchData = null;
            if (resultsContainer) resultsContainer.style.display = "none";
            if (summarySection) summarySection.style.display = "none";
        });
    }

    if (searchInput) searchInput.addEventListener("input", applyFilters);
    if (filterValidity) filterValidity.addEventListener("change", applyFilters);
    if (filterConfidence) filterConfidence.addEventListener("change", applyFilters);

    if (exportCsvBtn) exportCsvBtn.addEventListener("click", exportToCsv);
    if (exportJsonBtn) exportJsonBtn.addEventListener("click", exportToJson);
})();
