// Hash Manifest Generator & Verifier Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    // Mode Switching: Generate vs Verify
    const modeGenBtn = document.getElementById("manifest-mode-gen");
    const modeVerBtn = document.getElementById("manifest-mode-ver");
    const genSection = document.getElementById("manifest-gen-section");
    const verSection = document.getElementById("manifest-ver-section");

    // Generator elements
    const genFilesInput = document.getElementById("manifest-gen-files");
    const genFolderInput = document.getElementById("manifest-gen-folder");
    const genDropzone = document.getElementById("manifest-gen-dropzone");
    const genSelectedCount = document.getElementById("manifest-gen-count");
    const genStartBtn = document.getElementById("manifest-gen-start-btn");
    const genProgressWrap = document.getElementById("manifest-gen-progress-wrap");
    const genProgressFill = document.getElementById("manifest-gen-progress-fill");
    const genProgressText = document.getElementById("manifest-gen-progress-text");
    const genResultsCard = document.getElementById("manifest-gen-results");
    const genTableBody = document.getElementById("manifest-gen-table-body");
    const genDownloadJsonBtn = document.getElementById("manifest-download-json");
    const genDownloadCsvBtn = document.getElementById("manifest-download-csv");

    // Verifier elements
    const verManifestInput = document.getElementById("manifest-ver-file-input");
    const verManifestText = document.getElementById("manifest-ver-text");
    const verTargetFilesInput = document.getElementById("manifest-ver-targets");
    const verTargetFolderInput = document.getElementById("manifest-ver-target-folder");
    const verTargetDropzone = document.getElementById("manifest-ver-dropzone");
    const verTargetCount = document.getElementById("manifest-ver-count");
    const verStartBtn = document.getElementById("manifest-ver-start-btn");
    const verProgressWrap = document.getElementById("manifest-ver-progress-wrap");
    const verProgressFill = document.getElementById("manifest-ver-progress-fill");
    const verProgressText = document.getElementById("manifest-ver-progress-text");
    const verResultsCard = document.getElementById("manifest-ver-results");
    const verStatusBox = document.getElementById("manifest-ver-status-box");
    const verTableBody = document.getElementById("manifest-ver-table-body");
    const verExportCsvBtn = document.getElementById("manifest-ver-export-csv");
    const verExportJsonBtn = document.getElementById("manifest-ver-export-json");

    let selectedFilesToGen = [];
    let generatedManifest = null;

    let selectedTargetFiles = [];
    let verificationResult = null;

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

    function formatBytes(bytes) {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    // Mode Toggle
    if (modeGenBtn && modeVerBtn) {
        modeGenBtn.addEventListener("click", () => {
            modeGenBtn.classList.add("active");
            modeVerBtn.classList.remove("active");
            if (genSection) genSection.style.display = "block";
            if (verSection) verSection.style.display = "none";
        });

        modeVerBtn.addEventListener("click", () => {
            modeVerBtn.classList.add("active");
            modeGenBtn.classList.remove("active");
            if (genSection) genSection.style.display = "none";
            if (verSection) verSection.style.display = "block";
        });
    }

    // -------------------------------------------------------------------------
    // Manifest Generation
    // -------------------------------------------------------------------------
    function addFilesToGen(fileList) {
        for (let i = 0; i < fileList.length; i++) {
            selectedFilesToGen.push(fileList[i]);
        }
        updateGenCount();
    }

    function updateGenCount() {
        if (genSelectedCount) genSelectedCount.textContent = `${selectedFilesToGen.length} file(s) selected`;
        if (genStartBtn) genStartBtn.disabled = selectedFilesToGen.length === 0;
    }

    if (genFilesInput) genFilesInput.addEventListener("change", (e) => addFilesToGen(e.target.files));
    if (genFolderInput) genFolderInput.addEventListener("change", (e) => addFilesToGen(e.target.files));

    if (genDropzone) {
        genDropzone.addEventListener("dragover", (e) => { e.preventDefault(); genDropzone.classList.add("dragover"); });
        genDropzone.addEventListener("dragleave", () => genDropzone.classList.remove("dragover"));
        genDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            genDropzone.classList.remove("dragover");
            if (e.dataTransfer.files) addFilesToGen(e.dataTransfer.files);
        });
    }

    if (genStartBtn) {
        genStartBtn.addEventListener("click", async () => {
            if (selectedFilesToGen.length === 0) return;

            genStartBtn.disabled = true;
            if (genProgressWrap) genProgressWrap.style.display = "block";
            if (genResultsCard) genResultsCard.style.display = "none";

            const manifestEntries = [];
            const total = selectedFilesToGen.length;

            for (let i = 0; i < total; i++) {
                const file = selectedFilesToGen[i];
                const pct = Math.round(((i) / total) * 100);
                if (genProgressFill) genProgressFill.style.width = pct + "%";
                if (genProgressText) genProgressText.textContent = `Hashing file ${i + 1} of ${total}: ${file.name} (${formatBytes(file.size)})`;

                const { hashes } = await window.CryptoEngine.hashFileStreaming(file, ["sha256"]);
                const relPath = file.webkitRelativePath || file.name;

                manifestEntries.push({
                    path: relPath.replace(/\\/g, "/"),
                    name: file.name,
                    size: file.size,
                    algorithm: "SHA-256",
                    hash: hashes.sha256,
                });
            }

            if (genProgressFill) genProgressFill.style.width = "100%";
            if (genProgressText) genProgressText.textContent = `Completed SHA-256 manifest generation for ${total} file(s).`;

            generatedManifest = {
                version: "1.0",
                created_at: new Date().toISOString(),
                algorithm: "SHA-256",
                total_files: manifestEntries.length,
                files: manifestEntries,
            };

            renderGenTable(manifestEntries);
            if (genResultsCard) genResultsCard.style.display = "block";
            genStartBtn.disabled = false;
        });
    }

    function renderGenTable(entries) {
        if (!genTableBody) return;
        genTableBody.innerHTML = entries.map((entry, idx) => `
            <tr>
                <td>${idx + 1}</td>
                <td><code>${escapeHtml(entry.path)}</code></td>
                <td>${formatBytes(entry.size)}</td>
                <td><span class="badge-status valid">SHA-256</span></td>
                <td><code class="hash-code" title="${escapeHtml(entry.hash)}">${escapeHtml(entry.hash.slice(0, 16))}…${escapeHtml(entry.hash.slice(-8))}</code></td>
            </tr>
        `).join("");
    }

    if (genDownloadJsonBtn) {
        genDownloadJsonBtn.addEventListener("click", () => {
            if (!generatedManifest) return;
            downloadBlob(JSON.stringify(generatedManifest, null, 2), "manifest_sha256.json", "application/json;charset=utf-8;");
        });
    }

    if (genDownloadCsvBtn) {
        genDownloadCsvBtn.addEventListener("click", () => {
            if (!generatedManifest) return;
            const headers = ["path", "name", "size_bytes", "algorithm", "sha256_hash"];
            const rows = generatedManifest.files.map((f) => [
                `"${f.path.replace(/"/g, '""')}"`,
                `"${f.name.replace(/"/g, '""')}"`,
                f.size,
                "SHA-256",
                `"${f.hash}"`
            ]);
            const csv = [headers.join(","), ...rows.map(r => r.join(","))].join("\r\n");
            downloadBlob(csv, "manifest_sha256.csv", "text/csv;charset=utf-8;");
        });
    }

    // -------------------------------------------------------------------------
    // Manifest Verification
    // -------------------------------------------------------------------------
    if (verManifestInput) {
        verManifestInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    verManifestText.value = ev.target.result;
                    showToast(`Loaded manifest: ${e.target.files[0].name}`);
                };
                reader.readAsText(e.target.files[0]);
            }
        });
    }

    function addTargetFiles(fileList) {
        for (let i = 0; i < fileList.length; i++) {
            selectedTargetFiles.push(fileList[i]);
        }
        if (verTargetCount) verTargetCount.textContent = `${selectedTargetFiles.length} file(s) loaded for verification`;
    }

    if (verTargetFilesInput) verTargetFilesInput.addEventListener("change", (e) => addTargetFiles(e.target.files));
    if (verTargetFolderInput) verTargetFolderInput.addEventListener("change", (e) => addTargetFiles(e.target.files));

    if (verTargetDropzone) {
        verTargetDropzone.addEventListener("dragover", (e) => { e.preventDefault(); verTargetDropzone.classList.add("dragover"); });
        verTargetDropzone.addEventListener("dragleave", () => verTargetDropzone.classList.remove("dragover"));
        verTargetDropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            verTargetDropzone.classList.remove("dragover");
            if (e.dataTransfer.files) addTargetFiles(e.dataTransfer.files);
        });
    }

    if (verStartBtn) {
        verStartBtn.addEventListener("click", async () => {
            const manifestStr = verManifestText ? verManifestText.value.trim() : "";
            if (!manifestStr) {
                showToast("Please provide or load the reference manifest first.");
                if (verManifestText) verManifestText.focus();
                return;
            }

            if (selectedTargetFiles.length === 0) {
                showToast("Please select the target files or directory to verify.");
                return;
            }

            verStartBtn.disabled = true;
            if (verProgressWrap) verProgressWrap.style.display = "block";
            if (verResultsCard) verResultsCard.style.display = "none";

            const currentFilesData = [];
            const total = selectedTargetFiles.length;

            for (let i = 0; i < total; i++) {
                const file = selectedTargetFiles[i];
                const pct = Math.round(((i) / total) * 100);
                if (verProgressFill) verProgressFill.style.width = pct + "%";
                if (verProgressText) verProgressText.textContent = `Verifying file ${i + 1} of ${total}: ${file.name}`;

                const { hashes } = await window.CryptoEngine.hashFileStreaming(file, ["sha256"]);
                const relPath = file.webkitRelativePath || file.name;

                currentFilesData.push({
                    path: relPath.replace(/\\/g, "/"),
                    name: file.name,
                    size: file.size,
                    hash: hashes.sha256,
                });
            }

            if (verProgressFill) verProgressFill.style.width = "100%";
            if (verProgressText) verProgressText.textContent = "Comparing digests with reference manifest...";

            try {
                const res = await fetch("/api/manifest/verify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        manifest: manifestStr,
                        current_files: currentFilesData,
                    }),
                });
                const data = await res.json();
                verificationResult = data;
                renderVerificationResults(data);
                if (verResultsCard) verResultsCard.style.display = "block";
            } catch (err) {
                showToast("Verification failed: invalid manifest structure.");
            } finally {
                verStartBtn.disabled = false;
            }
        });
    }

    function renderVerificationResults(data) {
        if (!data || !data.summary) return;
        const sum = data.summary;
        const isOk = data.fully_intact;

        if (verStatusBox) {
            verStatusBox.className = isOk ? "alert-box alert-match" : "alert-box alert-mismatch";
            verStatusBox.innerHTML = `
                <div class="alert-title">${isOk ? '<span class="material-symbols-outlined">check_circle</span> MANIFEST VERIFICATION SUCCESSFUL' : '<span class="material-symbols-outlined">warning</span> MANIFEST DISCREPANCIES DETECTED'}</div>
                <div class="alert-body">
                    ${escapeHtml(data.verification_statement)}
                    <div class="manifest-metrics">
                        <span class="m-pill">Unchanged: <strong>${sum.unchanged_count}</strong></span>
                        <span class="m-pill">Modified: <strong>${sum.modified_count}</strong></span>
                        <span class="m-pill">Missing: <strong>${sum.missing_count}</strong></span>
                        <span class="m-pill">Newly Added: <strong>${sum.newly_added_count}</strong></span>
                    </div>
                </div>
            `;
        }

        const allRows = [];

        (data.modified || []).forEach((m) => {
            allRows.push({
                path: m.path,
                status: "MODIFIED",
                statusClass: "badge-danger",
                msg: `Expected ${(m.expected_hash || '').slice(0, 10)}…, calculated ${(m.actual_hash || '').slice(0, 10)}…`
            });
        });

        (data.missing || []).forEach((m) => {
            allRows.push({
                path: m.path,
                status: "MISSING",
                statusClass: "badge-warning",
                msg: "Listed in manifest but not supplied for verification."
            });
        });

        (data.newly_added || []).forEach((a) => {
            allRows.push({
                path: a.path,
                status: "NEWLY_ADDED",
                statusClass: "badge-info",
                msg: "Present in local target set but absent from reference manifest."
            });
        });

        (data.unchanged || []).forEach((u) => {
            allRows.push({
                path: u.path,
                status: "UNCHANGED",
                statusClass: "badge-success",
                msg: "SHA-256 digest verified strictly identical."
            });
        });

        if (verTableBody) {
            verTableBody.innerHTML = allRows.map((r, idx) => `
                <tr>
                    <td>${idx + 1}</td>
                    <td><code>${escapeHtml(r.path)}</code></td>
                    <td><span class="badge-status ${r.status.toLowerCase()}">${escapeHtml(r.status)}</span></td>
                    <td>${escapeHtml(r.msg)}</td>
                </tr>
            `).join("");
        }
    }

    if (verExportCsvBtn) {
        verExportCsvBtn.addEventListener("click", () => {
            if (!verificationResult) return;
            const headers = ["Path", "Status", "Details"];
            const rows = [];
            (verificationResult.modified || []).forEach(m => rows.push([`"${m.path}"`, "MODIFIED", `"${m.message}"`]));
            (verificationResult.missing || []).forEach(m => rows.push([`"${m.path}"`, "MISSING", `"${m.message}"`]));
            (verificationResult.newly_added || []).forEach(a => rows.push([`"${a.path}"`, "NEWLY_ADDED", `"${a.message}"`]));
            (verificationResult.unchanged || []).forEach(u => rows.push([`"${u.path}"`, "UNCHANGED", `"${u.message}"`]));

            const csv = [headers.join(","), ...rows.map(r => r.join(","))].join("\r\n");
            downloadBlob(csv, "manifest_verification_report.csv", "text/csv;charset=utf-8;");
        });
    }

    if (verExportJsonBtn) {
        verExportJsonBtn.addEventListener("click", () => {
            if (!verificationResult) return;
            downloadBlob(JSON.stringify(verificationResult, null, 2), "manifest_verification_report.json", "application/json;charset=utf-8;");
        });
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
})();
