// Multi-Algorithm Text Hash Generator Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const textInput = document.getElementById("gen-text-input");
    const generateBtn = document.getElementById("gen-submit-btn");
    const clearBtn = document.getElementById("gen-clear-btn");
    const copyAllBtn = document.getElementById("gen-copy-all-btn");
    const resultsGrid = document.getElementById("gen-results-grid");
    const charCountEl = document.getElementById("gen-char-count");
    const byteCountEl = document.getElementById("gen-byte-count");

    const ALGORITHMS = [
        {
            id: "md5",
            name: "MD5",
            bitLen: 128,
            hexLen: 32,
            warning: "Educational & Legacy Use: MD5 is cryptographically broken by practical collision attacks. Do not use for security-sensitive verification or digital signatures.",
            legacy: true,
        },
        {
            id: "sha1",
            name: "SHA-1",
            bitLen: 160,
            hexLen: 40,
            warning: "Educational & Legacy Use: SHA-1 is vulnerable to collision attacks (SHAttered). Deprecated by NIST.",
            legacy: true,
        },
        {
            id: "sha256",
            name: "SHA-256",
            bitLen: 256,
            hexLen: 64,
            warning: "Recommended Industry Standard: Robust, collision-resistant cryptographic hash (NIST FIPS 180-4).",
            legacy: false,
        },
        {
            id: "sha384",
            name: "SHA-384",
            bitLen: 384,
            hexLen: 96,
            warning: "High-Assurance Standard: CNSA / NSA Suite B approved 384-bit cryptographic digest.",
            legacy: false,
        },
        {
            id: "sha512",
            name: "SHA-512",
            bitLen: 512,
            hexLen: 128,
            warning: "High-Performance 64-bit Standard: 512-bit maximum security hash.",
            legacy: false,
        },
    ];

    let currentHashes = {};

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

    function updateCounts() {
        const text = textInput.value;
        const charLen = text.length;
        const utf8Bytes = (window.CryptoEngine && window.CryptoEngine.stringToUtf8Bytes)
            ? window.CryptoEngine.stringToUtf8Bytes(text).length
            : new TextEncoder().encode(text).length;

        charCountEl.textContent = `${charLen} characters`;
        byteCountEl.textContent = `${utf8Bytes} bytes (UTF-8)`;
    }

    function generate() {
        const text = textInput.value; // May be empty string: explicitly supported!
        updateCounts();

        // Calculate using local CryptoEngine
        if (window.CryptoEngine && window.CryptoEngine.hashText) {
            currentHashes = window.CryptoEngine.hashText(text);
            renderGrid(text);
        } else {
            // Fallback to backend API
            fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text }),
            })
                .then((r) => r.json())
                .then((data) => {
                    const hMap = {};
                    for (const [k, v] of Object.entries(data.hashes || {})) {
                        hMap[k] = v.hash;
                    }
                    currentHashes = hMap;
                    renderGrid(text);
                });
        }
    }

    function renderGrid(text) {
        resultsGrid.style.display = "grid";
        copyAllBtn.style.display = "inline-flex";

        resultsGrid.innerHTML = ALGORITHMS.map((alg) => {
            const digest = currentHashes[alg.id] || "";
            const warningHtml = alg.legacy
                ? `<div class="alg-card-warning"><span class="material-symbols-outlined">warning</span> ${escapeHtml(alg.warning)}</div>`
                : "";

            return `
                <div class="gen-card ${alg.legacy ? 'card-legacy' : ''}">
                    <div class="gen-card-header">
                        <div class="gen-card-title">
                            <span class="gen-alg-name">${escapeHtml(alg.name)}</span>
                            <span class="gen-alg-len">${alg.bitLen}-bit (${alg.hexLen} hex)</span>
                        </div>
                        <button class="btn-copy-hash" data-alg="${escapeHtml(alg.name)}" data-hash="${escapeHtml(digest)}" title="Copy ${escapeHtml(alg.name)} hash">
                            <span class="material-symbols-outlined">content_copy</span> Copy
                        </button>
                    </div>
                    <div class="gen-hash-box">
                        <code class="gen-hash-val">${escapeHtml(digest)}</code>
                    </div>
                    ${warningHtml}
                </div>
            `;
        }).join("");

        // Attach individual copy buttons
        resultsGrid.querySelectorAll(".btn-copy-hash").forEach((btn) => {
            btn.addEventListener("click", async () => {
                const digest = btn.getAttribute("data-hash");
                const algName = btn.getAttribute("data-alg");
                if (digest) {
                    await navigator.clipboard.writeText(digest);
                    showToast(`${algName} hash copied to clipboard`);
                }
            });
        });
    }

    function copyAll() {
        if (!currentHashes || Object.keys(currentHashes).length === 0) return;

        const lines = ALGORITHMS.map((alg) => `${alg.name.padEnd(8)}: ${currentHashes[alg.id] || ""}`);
        const fullReport = [
            "=== Multi-Algorithm Cryptographic Hashes ===",
            `Input Characters: ${textInput.value.length}`,
            `Encoding: UTF-8`,
            "",
            ...lines,
        ].join("\n");

        navigator.clipboard.writeText(fullReport).then(() => {
            showToast("All 5 algorithm hashes copied to clipboard!");
        });
    }

    function escapeHtml(str) {
        if (str == null) return "";
        const div = document.createElement("div");
        div.textContent = String(str);
        return div.innerHTML;
    }

    generateBtn.addEventListener("click", generate);
    textInput.addEventListener("input", () => {
        updateCounts();
        generate();
    });

    clearBtn.addEventListener("click", () => {
        textInput.value = "";
        updateCounts();
        generate();
        textInput.focus();
    });

    copyAllBtn.addEventListener("click", copyAll);

    // Initial render for empty string so user immediately sees canonical baseline empty hashes
    updateCounts();
    generate();
})();
