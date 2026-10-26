// File Hash Calculator & Integrity Verifier Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const fileInput = document.getElementById("file-upload-input");
    const dropzone = document.getElementById("file-dropzone");
    const selectedFileCard = document.getElementById("selected-file-card");
    const fileNameEl = document.getElementById("selected-file-name");
    const fileSizeEl = document.getElementById("selected-file-size");
    const fileRemoveBtn = document.getElementById("selected-file-remove");

    const algButtons = document.querySelectorAll(".alg-select-btn");
    const selectedAlgLabel = document.getElementById("current-selected-alg-label");

    const generateBtn = document.getElementById("file-generate-btn");
    const livePreviewEmptyState = document.getElementById("file-empty-preview");

    const progressWrap = document.getElementById("file-progress-wrap");
    const progressFill = document.getElementById("file-progress-fill");
    const progressText = document.getElementById("file-progress-text");

    const resultsCard = document.getElementById("file-results-card");
    const resultsContainer = document.getElementById("file-results-container");
    const exportTxtBtn = document.getElementById("file-export-txt");
    const exportCsvBtn = document.getElementById("file-export-csv");

    // Integrity Verification elements
    const refHashInput = document.getElementById("file-ref-hash-input");
    const verifyIntegrityBtn = document.getElementById("file-verify-btn");
    const verifyResultBox = document.getElementById("file-verify-result");

    let currentFile = null;
    let selectedAlgorithm = "sha256"; // default
    let calculatedResults = null; // { md5, sha1, sha256, sha384, sha512 }

    const ALG_LENGTHS = {
        md5: 32,
        sha1: 40,
        sha256: 64,
        sha384: 96,
        sha512: 128,
    };

    const ALG_NAMES = {
        md5: "MD5",
        sha1: "SHA-1",
        sha256: "SHA-256",
        sha384: "SHA-384",
        sha512: "SHA-512",
        all: "All Algorithms",
    };

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
        const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    // Drag & Drop
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
                onFileSelected(e.dataTransfer.files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                onFileSelected(e.target.files[0]);
            }
        });
    }

    function onFileSelected(file) {
        currentFile = file;
        calculatedResults = null;

        // Hide empty preview state
        if (livePreviewEmptyState) livePreviewEmptyState.style.display = "none";

        // Display selected file details before hashing
        if (selectedFileCard) selectedFileCard.style.display = "flex";
        if (fileNameEl) fileNameEl.textContent = file.name;
        if (fileSizeEl) fileSizeEl.textContent = `${formatBytes(file.size)} (${file.size.toLocaleString()} bytes)`;

        // Reset progress and results
        if (progressWrap) progressWrap.style.display = "none";
        if (resultsCard) resultsCard.style.display = "none";
        if (verifyResultBox) verifyResultBox.style.display = "none";
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.textContent = "Generate Hash";
        }
    }

    if (fileRemoveBtn) {
        fileRemoveBtn.addEventListener("click", () => {
            currentFile = null;
            calculatedResults = null;
            if (fileInput) fileInput.value = "";
            if (selectedFileCard) selectedFileCard.style.display = "none";
            if (progressWrap) progressWrap.style.display = "none";
            if (resultsCard) resultsCard.style.display = "none";
            if (verifyResultBox) verifyResultBox.style.display = "none";
            if (livePreviewEmptyState) livePreviewEmptyState.style.display = "block";
        });
    }

    // Algorithm selection
    algButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            algButtons.forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            selectedAlgorithm = btn.getAttribute("data-alg");
            if (selectedAlgLabel) {
                selectedAlgLabel.textContent = `Selected algorithm: ${ALG_NAMES[selectedAlgorithm] || selectedAlgorithm.toUpperCase()}`;
            }

            // Re-verify if integrity hash was already entered
            if (calculatedResults && refHashInput && refHashInput.value.trim()) {
                verifyIntegrity();
            }
        });
    });

    // Hash Calculation via incremental chunked streaming
    async function calculateFileHash() {
        if (!currentFile) {
            showToast("Please select a file to hash first.");
            return;
        }

        generateBtn.disabled = true;
        generateBtn.textContent = "Processing File...";
        progressWrap.style.display = "block";
        progressFill.style.width = "0%";
        progressText.textContent = "Initializing stream...";
        resultsCard.style.display = "none";
        verifyResultBox.style.display = "none";

        const targetAlgs = selectedAlgorithm === "all"
            ? ["md5", "sha1", "sha256", "sha384", "sha512"]
            : [selectedAlgorithm];

        try {
            const onProgress = ({ percent, bytesProcessed, totalBytes }) => {
                progressFill.style.width = percent + "%";
                progressText.textContent = `Hashing file in chunks... ${percent}% (${formatBytes(bytesProcessed)} of ${formatBytes(totalBytes)})`;
            };

            // Process locally in browser chunks
            const startTime = performance.now();
            const { hashes } = await window.CryptoEngine.hashFileStreaming(currentFile, targetAlgs, onProgress);
            const elapsedMs = Math.round(performance.now() - startTime);

            calculatedResults = hashes;
            progressText.textContent = `Hashing completed in ${elapsedMs} ms (${formatBytes(currentFile.size)})`;

            renderResults(hashes, elapsedMs);

            // If reference hash is already entered, trigger integrity verification automatically
            if (refHashInput.value.trim()) {
                verifyIntegrity();
            }
        } catch (err) {
            progressText.innerHTML = `<span class="material-symbols-outlined">warning</span> Error hashing file: ${escapeHtml(err.message)}`;
            showToast("Hashing failed: " + err.message);
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = "Generate Hash";
        }
    }

    function renderResults(hashes, elapsedMs) {
        resultsCard.style.display = "block";
        resultsContainer.innerHTML = "";

        const algList = Object.keys(hashes);

        resultsContainer.innerHTML = algList.map((algKey) => {
            const algName = ALG_NAMES[algKey] || algKey.toUpperCase();
            const digest = hashes[algKey];
            const isLegacy = algKey === "md5" || algKey === "sha1";
            const warningText = isLegacy
                ? `<span class="res-warn-badge"><span class="material-symbols-outlined">warning</span> Not recommended for security-sensitive tampering checks</span>`
                : `<span class="res-sec-badge"><span class="material-symbols-outlined">check_circle</span> Secure Digest</span>`;

            return `
                <div class="file-hash-result-row">
                    <div class="row-header">
                        <div class="row-title">
                            <strong>${escapeHtml(algName)}</strong>
                            ${warningText}
                        </div>
                        <button class="file-copy-btn" data-hash="${escapeHtml(digest)}" data-alg="${escapeHtml(algName)}">
                            <span class="material-symbols-outlined">content_copy</span> Copy Hash
                        </button>
                    </div>
                    <div class="row-hash-box">
                        <code class="file-digest-code">${escapeHtml(digest)}</code>
                    </div>
                </div>
            `;
        }).join("");

        resultsContainer.querySelectorAll(".file-copy-btn").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const digest = btn.getAttribute("data-hash");
                const name = btn.getAttribute("data-alg");
                await navigator.clipboard.writeText(digest);
                showToast(`${name} hash copied to clipboard!`);
            });
        });
    }

    // Integrity Verification
    function verifyIntegrity() {
        const refRaw = refHashInput.value.trim();
        if (!refRaw) {
            verifyResultBox.style.display = "none";
            return;
        }

        if (!calculatedResults) {
            verifyResultBox.style.display = "block";
            verifyResultBox.className = "alert-box alert-warning";
            verifyResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">warning</span> Hash Not Yet Calculated</div>
                <div class="alert-body">Click <strong>Generate Hash</strong> first to calculate the file's hash before verifying.</div>
            `;
            return;
        }

        // Determine verification algorithm
        let verifyAlg = selectedAlgorithm;
        if (verifyAlg === "all") {
            // Infer algorithm from reference hash length if valid hex
            const cleanRef = refRaw.replace(/\s+/g, "").toLowerCase();
            const len = cleanRef.length;
            if (len === 32) verifyAlg = "md5";
            else if (len === 40) verifyAlg = "sha1";
            else if (len === 64) verifyAlg = "sha256";
            else if (len === 96) verifyAlg = "sha384";
            else if (len === 128) verifyAlg = "sha512";
            else verifyAlg = "sha256"; // fallback
        }

        const expectedLen = ALG_LENGTHS[verifyAlg];
        const algName = ALG_NAMES[verifyAlg] || verifyAlg.toUpperCase();

        // Normalization: trim surrounding whitespace and normalize hex case to lowercase
        const normalizedRef = refRaw.replace(/\s+/g, "").toLowerCase();

        // Pre-validation 1: Format check (must be valid hex)
        if (!/^[0-9a-f]+$/.test(normalizedRef)) {
            verifyResultBox.style.display = "block";
            verifyResultBox.className = "alert-box alert-warning";
            verifyResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">warning</span> Invalid Reference Hash Format</div>
                <div class="alert-body">
                    The reference hash contains non-hexadecimal characters. Valid ${algName} hashes contain only digits <code>0-9</code> and letters <code>a-f</code>.
                </div>
            `;
            return;
        }

        // Pre-validation 2: Expected length check
        if (expectedLen && normalizedRef.length !== expectedLen) {
            verifyResultBox.style.display = "block";
            verifyResultBox.className = "alert-box alert-warning";
            verifyResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">warning</span> Algorithm Length Mismatch</div>
                <div class="alert-body">
                    The reference hash length is <strong>${normalizedRef.length} characters</strong>, but <strong>${algName}</strong> expects exactly <strong>${expectedLen} characters</strong>.
                    Please select the matching algorithm button above to avoid a false mismatch.
                </div>
            `;
            return;
        }

        const calculated = calculatedResults[verifyAlg];
        if (!calculated) {
            verifyResultBox.style.display = "block";
            verifyResultBox.className = "alert-box alert-warning";
            verifyResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">warning</span> ${algName} Not Calculated</div>
                <div class="alert-body">Please click <strong>Generate Hash</strong> with ${algName} or All Algorithms selected.</div>
            `;
            return;
        }

        const isMatch = (calculated.toLowerCase() === normalizedRef);
        verifyResultBox.style.display = "block";

        if (isMatch) {
            verifyResultBox.className = "alert-box alert-match";
            verifyResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">check_circle</span> INTEGRITY MATCH CONFIRMED (${algName})</div>
                <div class="alert-body">
                    The calculated file digest strictly matches the expected reference hash.
                    <div class="verify-disclaimer">
                        <strong>Integrity Verification Note:</strong> A cryptographic hash match confirms content equality under the ${algName} algorithm.
                        It proves the file matches the expected byte-for-byte state, but does not independently establish that the file is safe, trustworthy, or benign.
                    </div>
                </div>
            `;
        } else {
            verifyResultBox.className = "alert-box alert-mismatch";
            verifyResultBox.innerHTML = `
                <div class="alert-title"><span class="material-symbols-outlined">error</span> INTEGRITY MISMATCH DETECTED (${algName})</div>
                <div class="alert-body">
                    The calculated file digest does NOT match the reference hash.
                    <div class="mismatch-diff">
                        <div><strong>Calculated:</strong> <code>${calculated}</code></div>
                        <div><strong>Reference:</strong> &nbsp;<code>${normalizedRef}</code></div>
                    </div>
                    <div class="verify-disclaimer">
                        Possible causes: incomplete file download, file modification, corruption, or reference hash from a different version.
                    </div>
                </div>
            `;
        }
    }

    function exportReportTxt() {
        if (!currentFile || !calculatedResults) {
            showToast("No calculated hashes to export.");
            return;
        }

        const lines = [
            "==================================================",
            "FILE HASH & INTEGRITY REPORT",
            "==================================================",
            `Generated by: Hash Identifier Toolkit`,
            `Date:         ${new Date().toISOString()}`,
            `Filename:     ${currentFile.name}`,
            `File Size:    ${currentFile.size.toLocaleString()} bytes (${formatBytes(currentFile.size)})`,
            "--------------------------------------------------",
        ];

        for (const [alg, digest] of Object.entries(calculatedResults)) {
            lines.push(`${(ALG_NAMES[alg] || alg).padEnd(10)}: ${digest}`);
        }

        if (refHashInput.value.trim()) {
            lines.push("--------------------------------------------------");
            lines.push(`Reference Hash:  ${refHashInput.value.trim()}`);
            lines.push(`Verified Status: ${verifyResultBox.textContent.includes("MATCH CONFIRMED") ? "MATCH" : "MISMATCH"}`);
        }

        lines.push("==================================================");

        const content = lines.join("\r\n");
        downloadBlob(content, `${currentFile.name}_hashes.txt`, "text/plain;charset=utf-8;");
    }

    function exportReportCsv() {
        if (!currentFile || !calculatedResults) {
            showToast("No calculated hashes to export.");
            return;
        }

        const headers = ["Filename", "File_Size_Bytes", "Algorithm", "Calculated_Hash", "Reference_Hash", "Match_Status"];
        const refVal = refHashInput.value.trim().replace(/\s+/g, "").toLowerCase();
        const rows = Object.entries(calculatedResults).map(([alg, digest]) => {
            const isMatch = refVal ? (digest.toLowerCase() === refVal ? "MATCH" : "MISMATCH") : "N/A";
            return [
                `"${currentFile.name.replace(/"/g, '""')}"`,
                currentFile.size,
                `"${ALG_NAMES[alg] || alg}"`,
                `"${digest}"`,
                `"${refVal}"`,
                isMatch
            ];
        });

        const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\r\n");
        downloadBlob(csvContent, `${currentFile.name}_hashes.csv`, "text/csv;charset=utf-8;");
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

    if (generateBtn) generateBtn.addEventListener("click", calculateFileHash);
    if (verifyIntegrityBtn) verifyIntegrityBtn.addEventListener("click", verifyIntegrity);
    if (refHashInput) refHashInput.addEventListener("input", verifyIntegrity);

    if (exportTxtBtn) exportTxtBtn.addEventListener("click", exportReportTxt);
    if (exportCsvBtn) exportCsvBtn.addEventListener("click", exportReportCsv);
})();
