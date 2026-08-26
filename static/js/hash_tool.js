// Hash Identifier — frontend logic
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
        toast._timer = setTimeout(() => toast.classList.remove("show"), 1800);
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
        btn.textContent = "Identifying...";

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
            resultsList.innerHTML = `<div class="no-match">⚠️ Something went wrong. Please try again.</div>`;
            resultsSection.style.display = "block";
        } finally {
            btn.disabled = false;
            btn.textContent = "Identify";
        }
    }

    function renderResults(data) {
        metaRow.style.display = "flex";
        metaLength.textContent = `Length: ${data.length ?? 0} chars`;
        metaHex.textContent = data.is_hex ? "Format: Hexadecimal" : "Format: Non-hex / mixed";
        metaCharset.textContent = data.is_hex ? "Charset: 0-9, a-f" : "Charset: mixed / special chars";

        strengthWrap.style.display = "block";
        const pct = Math.min(100, Math.round(((data.length || 0) / 128) * 100));
        strengthFill.style.width = pct + "%";

        resultsSection.style.display = "block";

        if (!data.matches || data.matches.length === 0) {
            confidenceBadge.textContent = "No match";
            confidenceBadge.className = "confidence-badge none";
            resultsList.innerHTML = `<div class="no-match">❌ ${data.message || "No known hash format matched."}</div>`;
            return;
        }

        const hasHigh = data.matches.some((m) => m.confidence === "high");
        confidenceBadge.textContent = hasHigh ? "High confidence" : "Medium confidence";
        confidenceBadge.className = "confidence-badge " + (hasHigh ? "high" : "medium");

        resultsList.innerHTML = data.matches
            .map((m) => {
                const tags = m.types.map((t) => `<span class="type-tag">${escapeHtml(t)}</span>`).join("");
                const confLabel = m.confidence === "high" ? "High" : "Medium";
                return `
                    <div class="result-item ${m.confidence}">
                        <div class="types">${tags}<span class="confidence-mini ${m.confidence}">${confLabel}</span></div>
                        <div class="note">${escapeHtml(m.note)}</div>
                    </div>
                `;
            })
            .join("");
    }

    function addToHistory(data) {
        if (!data.input) return;
        history = history.filter((h) => h.input !== data.input);
        history.unshift(data);
        history = history.slice(0, 6);
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
                const short = h.input.length > 24 ? h.input.slice(0, 24) + "…" : h.input;
                return `<div class="history-item" data-value="${escapeHtml(h.input)}">
                            <span class="history-hash">${escapeHtml(short)}</span>
                            <span class="history-types">${escapeHtml(typeLabel)}</span>
                            <button class="history-copy-btn" data-value="${escapeHtml(h.input)}" title="Copy full hash">📋</button>
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
                    showToast("Could not copy — try manually");
                }
            });
        });
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
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
})();
