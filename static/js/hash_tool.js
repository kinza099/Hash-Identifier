// Hash Identifier — Single Hash Analysis Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const input = document.getElementById("hash-input");
    const btn = document.getElementById("identify-btn");
    const clearBtn = document.getElementById("clear-btn");
    const resultsSection = document.getElementById("results");
    const resultsList = document.getElementById("results-list");
    const confidenceBadge = document.getElementById("confidence-badge");
    const metaRow = document.getElementById("meta-row");
    const metaLength = document.getElementById("meta-length");
    const metaHex = document.getElementById("meta-hex");
    const metaCharset = document.getElementById("meta-charset");
    const strengthWrap = document.getElementById("strength-bar-wrap");
    const strengthFill = document.getElementById("strength-fill");
    const historyCard = document.getElementById("history-card");
    const historyList = document.getElementById("history-list");
    const historyClearBtn = document.getElementById("history-clear");

    let history = [];

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

    async function identify() {
        const value = input.value.trim();
        if (!value) {
            resultsSection.style.display = "none";
            metaRow.style.display = "none";
            strengthWrap.style.display = "none";
            return;
        }

        btn.disabled = true;
        btn.textContent = "Analyzing...";

        try {
            const res = await fetch("/api/identify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ hash: value }),
            });
            const data = await res.json();
            renderResults(data);
            addToHistory(data);
        } catch (err) {
            resultsList.innerHTML = `<div class="no-match"><span class="material-symbols-outlined">warning</span> Network or server error occurred. Please try again.</div>`;
            resultsSection.style.display = "block";
        } finally {
            btn.disabled = false;
            btn.textContent = "Identify";
        }
    }

    function renderResults(data) {
        metaRow.style.display = "flex";
        metaRow.innerHTML = "";

        const charset = data.charset_info || {};
        const lengthSpan = document.createElement("span");
        lengthSpan.id = "meta-length";
        lengthSpan.textContent = `Length: ${data.length ?? 0} chars`;
        metaRow.appendChild(lengthSpan);

        const hexSpan = document.createElement("span");
        hexSpan.id = "meta-hex";
        hexSpan.textContent = data.is_hex ? "Format: Hexadecimal" : "Format: Non-hex / Structured";
        metaRow.appendChild(hexSpan);

        const charsetSpan = document.createElement("span");
        charsetSpan.id = "meta-charset";
        charsetSpan.textContent = charset.charset_description ? `Charset: ${charset.charset_description}` : (data.is_hex ? "Charset: 0-9, a-f" : "Charset: mixed");
        metaRow.appendChild(charsetSpan);

        if (charset.entropy) {
            const entropySpan = document.createElement("span");
            entropySpan.textContent = `Entropy: ${charset.entropy} bits/char`;
            metaRow.appendChild(entropySpan);
        }

        if (charset.estimated_bits) {
            const bitsSpan = document.createElement("span");
            bitsSpan.textContent = `Est. Digest: ${charset.estimated_bits}-bit (${charset.estimated_bytes} bytes)`;
            metaRow.appendChild(bitsSpan);
        }

        strengthWrap.style.display = "block";
        const pct = Math.min(100, Math.round(((data.length || 0) / 128) * 100));
        strengthFill.style.width = pct + "%";

        resultsSection.style.display = "block";

        if (!data.matches || data.matches.length === 0) {
            confidenceBadge.textContent = "No match";
            confidenceBadge.className = "confidence-badge none";
            resultsList.innerHTML = `
                <div class="no-match">
                    <p><span class="material-symbols-outlined">cancel</span> ${escapeHtml(data.message || "No known hash format matched.")}</p>
                    <p class="no-match-tip">Tip: Ensure no leading/trailing quotes or incomplete paste. You can also search the Local Reference Database.</p>
                </div>`;
            return;
        }

        const hasHigh = data.matches.some((m) => m.confidence === "high");
        confidenceBadge.textContent = hasHigh ? "High confidence" : "Medium / Shared Format";
        confidenceBadge.className = "confidence-badge " + (hasHigh ? "high" : "medium");

        let html = "";

        // Ambiguity Warning alert if present
        if (data.ambiguity_warning) {
            html += `
                <div class="alert-box alert-warning">
                    <div class="alert-title"><span class="material-symbols-outlined">warning</span> Format Ambiguity Notice</div>
                    <div class="alert-body">${escapeHtml(data.ambiguity_warning)}</div>
                </div>
            `;
        }

        html += data.matches
            .map((m) => {
                const confClass = m.confidence === "high" ? "high" : (m.confidence === "low" ? "low" : "medium");
                const confLabel = m.confidence === "high" ? "High Confidence" : (m.confidence === "low" ? "Low Confidence" : "Shared Format");
                const scoreText = m.score ? `<span class="score-pill">${m.score}% Match</span>` : "";

                const tags = m.types.map((t) => `<span class="type-tag">${escapeHtml(t)}</span>`).join("");

                let algDetailsHtml = "";
                if (m.algorithm_details && m.algorithm_details.length > 0) {
                    algDetailsHtml = `
                        <div class="alg-details-grid">
                            ${m.algorithm_details.map((alg) => `
                                <div class="alg-detail-card">
                                    <div class="alg-name">${escapeHtml(alg.name)} 
                                        ${alg.security ? `<span class="sec-badge ${getSecClass(alg.security)}">${escapeHtml(alg.security)}</span>` : ""}
                                    </div>
                                    <div class="alg-summary">${escapeHtml(alg.summary || "")}</div>
                                    ${alg.common_in ? `<div class="alg-common"><strong>Common in:</strong> ${escapeHtml(alg.common_in)}</div>` : ""}
                                </div>
                            `).join("")}
                        </div>
                    `;
                }

                return `
                    <div class="result-item ${confClass}">
                        <div class="result-item-header">
                            <div class="types">${tags}</div>
                            <div class="header-badges">
                                ${scoreText}
                                <span class="confidence-mini ${confClass}">${confLabel}</span>
                            </div>
                        </div>
                        <div class="note">${escapeHtml(m.note)}</div>
                        ${m.rationale ? `<div class="rationale"><strong>Rationale:</strong> ${escapeHtml(m.rationale)}</div>` : ""}
                        ${m.ambiguity_note ? `<div class="ambiguity-note"><strong>Ambiguity:</strong> ${escapeHtml(m.ambiguity_note)}</div>` : ""}
                        ${algDetailsHtml}
                    </div>
                `;
            })
            .join("");

        resultsList.innerHTML = html;
    }

    function getSecClass(secStr) {
        const s = secStr.toLowerCase();
        if (s.includes("secure") || s.includes("standard")) return "sec-secure";
        if (s.includes("weak")) return "sec-weak";
        if (s.includes("broken")) return "sec-broken";
        return "sec-neutral";
    }

    function addToHistory(data) {
        if (!data.input) return;
        history = history.filter((h) => h.input !== data.input);
        history.unshift(data);
        history = history.slice(0, 8);
        renderHistory();
    }

    function renderHistory() {
        if (history.length === 0) {
            historyCard.style.display = "none";
            return;
        }
        historyCard.style.display = "block";
        historyList.innerHTML = history
            .map((h) => {
                const typeLabel =
                    h.matches && h.matches.length
                        ? h.matches[0].types.join(", ") + (h.matches.length > 1 ? " +" + (h.matches.length - 1) : "")
                        : "No match";
                const short = h.input.length > 28 ? h.input.slice(0, 28) + "…" : h.input;
                return `<div class="history-item" data-value="${escapeHtml(h.input)}" title="Click to reload this lookup">
                            <span class="history-hash">${escapeHtml(short)}</span>
                            <span class="history-types">${escapeHtml(typeLabel)}</span>
                            <button class="history-copy-btn" data-value="${escapeHtml(h.input)}" title="Copy full hash"><span class="material-symbols-outlined">content_copy</span></button>
                        </div>`;
            })
            .join("");

        historyList.querySelectorAll(".history-item").forEach((el) => {
            el.addEventListener("click", (e) => {
                if (e.target.closest(".history-copy-btn")) return;
                input.value = el.getAttribute("data-value");
                identify();
            });
        });

        historyList.querySelectorAll(".history-copy-btn").forEach((el) => {
            el.addEventListener("click", async (e) => {
                e.stopPropagation();
                const value = el.getAttribute("data-value");
                try {
                    await navigator.clipboard.writeText(value);
                    showToast("Hash copied to clipboard");
                } catch (err) {
                    showToast("Could not copy automatically — select manually");
                }
            });
        });
    }

    function escapeHtml(str) {
        if (str == null) return "";
        const div = document.createElement("div");
        div.textContent = String(str);
        return div.innerHTML;
    }

    btn.addEventListener("click", identify);
    input.addEventListener("keyup", function (e) {
        if (e.key === "Enter") identify();
    });
    clearBtn.addEventListener("click", function () {
        input.value = "";
        resultsSection.style.display = "none";
        metaRow.style.display = "none";
        strengthWrap.style.display = "none";
        input.focus();
    });
    historyClearBtn.addEventListener("click", function () {
        history = [];
        renderHistory();
    });

    // Expose identify function globally so other tools (Batch Scanner, Lookup DB) can link directly to it
    window.inspectSingleHash = function (hashStr) {
        if (window.switchToolkitTab) {
            window.switchToolkitTab("tab-identifier");
        }
        input.value = hashStr;
        identify();
        window.scrollTo({ top: 0, behavior: "smooth" });
    };
})();
