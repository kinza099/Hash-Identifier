// Local Hash Reference Database Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const searchBtn = document.getElementById("db-search-btn");
    const databasePanel = document.getElementById("database-panel") || document.getElementById("tab-database");

    // Guard: exit immediately without error if #db-search-btn or database panel does not exist in the DOM
    if (!searchBtn || !databasePanel) {
        return;
    }

    const searchInput = document.getElementById("db-search-input");
    const searchResultBox = document.getElementById("db-search-result");

    const recordListBody = document.getElementById("db-records-body");
    const addFormToggleBtn = document.getElementById("db-add-toggle-btn");
    const addFormContainer = document.getElementById("db-add-container");
    const addSubmitBtn = document.getElementById("db-add-submit");
    const addCancelBtn = document.getElementById("db-add-cancel");

    const addHashInput = document.getElementById("db-add-hash");
    const addAlgInput = document.getElementById("db-add-alg");
    const addSourceInput = document.getElementById("db-add-source");
    const addTagInput = document.getElementById("db-add-tag");
    const addNotesInput = document.getElementById("db-add-notes");

    const exportCsvBtn = document.getElementById("db-export-csv");
    const exportJsonBtn = document.getElementById("db-export-json");
    const importFileInput = document.getElementById("db-import-file");

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

    async function loadRecords() {
        try {
            const res = await fetch("/api/db/records?limit=100");
            const data = await res.json();
            renderTable(data.records || []);
        } catch (err) {
            recordListBody.innerHTML = `<tr><td colspan="6" class="table-empty">Could not load database records.</td></tr>`;
        }
    }

    function renderTable(records) {
        if (!records || records.length === 0) {
            recordListBody.innerHTML = `<tr><td colspan="6" class="table-empty">No reference records stored in local database yet.</td></tr>`;
            return;
        }

        recordListBody.innerHTML = records.map((r) => {
            const tagClass = getTagClass(r.tag);
            return `
                <tr>
                    <td class="col-hash">
                        <code class="hash-code" title="${escapeHtml(r.hash)}">${escapeHtml(r.hash.length > 24 ? r.hash.slice(0, 22) + '…' : r.hash)}</code>
                        <button class="table-copy-btn" data-val="${escapeHtml(r.hash)}" title="Copy Hash"><span class="material-symbols-outlined">content_copy</span></button>
                    </td>
                    <td><span class="badge-status valid">${escapeHtml(r.algorithm || 'Unknown')}</span></td>
                    <td><span class="tag-pill ${tagClass}">${escapeHtml(r.tag || 'General')}</span></td>
                    <td><strong>${escapeHtml(r.source || 'User Entry')}</strong></td>
                    <td class="col-notes">${escapeHtml(r.notes || '')}</td>
                    <td class="col-actions">
                        <button class="btn-delete" data-id="${r.id}" title="Delete Record"><span class="material-symbols-outlined">delete</span></button>
                    </td>
                </tr>
            `;
        }).join("");

        recordListBody.querySelectorAll(".table-copy-btn").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const val = btn.getAttribute("data-val");
                if (val) {
                    await navigator.clipboard.writeText(val);
                    showToast("Hash copied to clipboard");
                }
            });
        });

        recordListBody.querySelectorAll(".btn-delete").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const id = btn.getAttribute("data-id");
                if (confirm("Delete this reference record from database?")) {
                    await fetch(`/api/db/records/${id}`, { method: "DELETE" });
                    showToast("Record removed.");
                    loadRecords();
                }
            });
        });
    }

    function getTagClass(tagStr) {
        if (!tagStr) return "tag-neutral";
        const t = tagStr.toLowerCase();
        if (t.includes("malware") || t.includes("malicious")) return "tag-danger";
        if (t.includes("benign") || t.includes("baseline")) return "tag-success";
        if (t.includes("test")) return "tag-info";
        if (t.includes("password")) return "tag-warning";
        return "tag-neutral";
    }

    async function searchExactHash() {
        const query = searchInput.value.trim();
        if (!query) {
            searchResultBox.style.display = "none";
            return;
        }

        try {
            const res = await fetch(`/api/db/search?hash=${encodeURIComponent(query)}`);
            const data = await res.json();
            renderSearchResult(data);
        } catch (err) {
            showToast("Search failed.");
        }
    }

    function renderSearchResult(data) {
        searchResultBox.style.display = "block";

        if (!data.found || data.records.length === 0) {
            searchResultBox.className = "alert-box alert-warning";
            searchResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">search</span> No Local Match Found</div>
                <div class="alert-body">
                    The hash <code>${escapeHtml(data.query)}</code> was not found in your local reference database.
                    <div class="db-disclaimer">
                        <strong>Provenance Note:</strong> Absence from the local database only indicates it has not been cataloged in your local records.
                        It does NOT prove the file or string is safe or unknown globally.
                    </div>
                </div>
            `;
            return;
        }

        searchResultBox.className = "alert-box alert-match";
        const matchesHtml = data.records.map((r) => `
            <div class="db-match-card">
                <div class="db-match-header">
                    <span class="badge-status valid">${escapeHtml(r.algorithm)}</span>
                    <span class="tag-pill ${getTagClass(r.tag)}">${escapeHtml(r.tag)}</span>
                    <span class="db-source">Source: <strong>${escapeHtml(r.source)}</strong></span>
                </div>
                <div class="db-match-notes">${escapeHtml(r.notes || "No additional notes provided.")}</div>
                <div class="db-match-date">Added: ${escapeHtml(r.created_at)}</div>
            </div>
        `).join("");

        searchResultBox.innerHTML = `
            <div class="alert-title"><span class="material-symbols-outlined">check_circle</span> Exact Local Match Found (${data.match_count} record${data.match_count > 1 ? 's' : ''})</div>
            <div class="alert-body">
                ${matchesHtml}
                <div class="db-disclaimer">
                    <strong>Trust & Provenance Notice:</strong> A database match is only as reliable as its recorded source and provenance. Always verify signatures against primary vendor releases.
                </div>
            </div>
        `;
    }

    async function addRecord() {
        const hashVal = addHashInput.value.trim();
        if (!hashVal) {
            showToast("Hash value is required.");
            addHashInput.focus();
            return;
        }

        const payload = {
            hash: hashVal,
            algorithm: addAlgInput.value.trim() || "Unknown",
            source: addSourceInput.value.trim() || "User Entry",
            tag: addTagInput.value.trim() || "General",
            notes: addNotesInput.value.trim(),
        };

        try {
            const res = await fetch("/api/db/records", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (res.ok) {
                showToast("Reference record saved to local database!");
                addHashInput.value = "";
                addNotesInput.value = "";
                addFormContainer.style.display = "none";
                loadRecords();
            } else {
                const err = await res.json();
                showToast("Error saving record: " + (err.error || "failed"));
            }
        } catch (ex) {
            showToast("Network error saving record.");
        }
    }

    if (importFileInput) {
        importFileInput.addEventListener("change", async (e) => {
            if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];
                const reader = new FileReader();
                reader.onload = async (ev) => {
                    const text = ev.target.result;
                    const res = await fetch("/api/db/import", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ data: text }),
                    });
                    const d = await res.json();
                    showToast(`Imported ${d.imported} records into database.`);
                    loadRecords();
                };
                reader.readAsText(file);
            }
        });
    }

    function exportDb(format) {
        window.location.href = `/api/db/export?format=${format}`;
    }

    if (searchBtn) searchBtn.addEventListener("click", searchExactHash);
    if (searchInput) {
        searchInput.addEventListener("keyup", (e) => {
            if (e.key === "Enter") searchExactHash();
        });
    }

    if (addFormToggleBtn) {
        addFormToggleBtn.addEventListener("click", () => {
            if (!addFormContainer) return;
            const isHidden = addFormContainer.style.display === "none";
            addFormContainer.style.display = isHidden ? "block" : "none";
            if (isHidden && addHashInput) addHashInput.focus();
        });
    }

    if (addCancelBtn) {
        addCancelBtn.addEventListener("click", () => {
            if (addFormContainer) addFormContainer.style.display = "none";
        });
    }

    if (addSubmitBtn) addSubmitBtn.addEventListener("click", addRecord);

    if (exportCsvBtn) exportCsvBtn.addEventListener("click", () => exportDb("csv"));
    if (exportJsonBtn) exportJsonBtn.addEventListener("click", () => exportDb("json"));

    // Initial load
    if (recordListBody) {
        loadRecords();
    }
})();
