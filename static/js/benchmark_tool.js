// Hash Performance Benchmark Frontend Logic
// Author: Kinza | https://github.com/kinza099

(function () {
    const sizeSelect = document.getElementById("bench-size-select");
    const iterSelect = document.getElementById("bench-iter-select");
    const targetSelect = document.getElementById("bench-target-select"); // 'browser' or 'backend'
    const startBtn = document.getElementById("bench-start-btn");
    const progressText = document.getElementById("bench-progress-text");

    const resultsCard = document.getElementById("bench-results-card");
    const resultsTableBody = document.getElementById("bench-table-body");
    const chartContainer = document.getElementById("bench-chart-container");
    const envInfoEl = document.getElementById("bench-env-info");

    const exportCsvBtn = document.getElementById("bench-export-csv");
    const exportJsonBtn = document.getElementById("bench-export-json");

    let currentBenchmarkResults = null;

    const ALGORITHMS = [
        { id: "md5", name: "MD5" },
        { id: "sha1", name: "SHA-1" },
        { id: "sha256", name: "SHA-256" },
        { id: "sha384", name: "SHA-384" },
        { id: "sha512", name: "SHA-512" },
    ];

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

    async function runBenchmark() {
        startBtn.disabled = true;
        startBtn.textContent = "Benchmarking...";
        resultsCard.style.display = "none";

        const sizeBytes = parseInt(sizeSelect.value, 10);
        const iterations = parseInt(iterSelect.value, 10);
        const engineTarget = targetSelect ? targetSelect.value : "browser";

        progressText.textContent = `Running benchmark (${sizeBytes < 1048576 ? sizeBytes / 1024 + ' KB' : (sizeBytes / 1048576).toFixed(1) + ' MB'}, ${iterations} iterations)...`;

        if (engineTarget === "backend") {
            try {
                const res = await fetch("/api/benchmark", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ size_bytes: sizeBytes, iterations: iterations }),
                });
                const data = await res.json();
                currentBenchmarkResults = data;
                renderResults(data);
            } catch (err) {
                showToast("Backend benchmark failed.");
            } finally {
                startBtn.disabled = false;
                startBtn.textContent = "Start Benchmark";
                progressText.textContent = "";
            }
            return;
        }

        // Run client-side in browser using CryptoEngine with high-precision timing
        setTimeout(async () => {
            try {
                // Generate deterministic test payload
                const chunk = new Uint8Array(65536);
                for (let i = 0; i < chunk.length; i++) {
                    chunk[i] = (i * 31 + 17) & 0xff;
                }
                const blocksNeeded = Math.ceil(sizeBytes / chunk.length);
                const testPayload = new Uint8Array(sizeBytes);
                for (let b = 0; b < blocksNeeded; b++) {
                    const dest = b * chunk.length;
                    const len = Math.min(chunk.length, sizeBytes - dest);
                    testPayload.set(chunk.subarray(0, len), dest);
                }

                // Warmup runs
                for (const alg of ALGORITHMS) {
                    const h = window.CryptoEngine.createHasher(alg.id);
                    h.update(testPayload.subarray(0, Math.min(65536, testPayload.length)));
                    h.digest("hex");
                }

                const algResults = [];

                for (const alg of ALGORITHMS) {
                    progressText.textContent = `Testing ${alg.name}...`;
                    const times = [];

                    for (let iter = 0; iter < iterations; iter++) {
                        const h = window.CryptoEngine.createHasher(alg.id);
                        const t0 = performance.now();
                        h.update(testPayload);
                        h.digest("hex");
                        const t1 = performance.now();
                        times.push(t1 - t0);
                        // small yield
                        await new Promise((r) => setTimeout(r, 0));
                    }

                    const totalTime = times.reduce((a, b) => a + b, 0);
                    const avgTime = totalTime / times.length;
                    const minTime = Math.min(...times);
                    const maxTime = Math.max(...times);

                    // Throughput in MB/s
                    const throughputMbs = avgTime > 0
                        ? (sizeBytes / (1024 * 1024)) / (avgTime / 1000)
                        : 0;

                    algResults.push({
                        algorithm: alg.name,
                        alg_key: alg.id,
                        iterations: iterations,
                        bytes_per_iteration: sizeBytes,
                        total_bytes_processed: sizeBytes * iterations,
                        avg_time_ms: Math.round(avgTime * 100) / 100,
                        min_time_ms: Math.round(minTime * 100) / 100,
                        max_time_ms: Math.round(maxTime * 100) / 100,
                        total_time_ms: Math.round(totalTime * 100) / 100,
                        throughput_mbs: Math.round(throughputMbs * 100) / 100,
                    });
                }

                // Sort by throughput descending
                algResults.sort((a, b) => b.throughput_mbs - a.throughput_mbs);

                currentBenchmarkResults = {
                    status: "COMPLETED",
                    engine: "Browser Client Engine (WebAssembly/JS)",
                    size_bytes: sizeBytes,
                    size_label: sizeBytes >= 1048576 ? `${(sizeBytes / 1048576).toFixed(1)} MB` : `${sizeBytes / 1024} KB`,
                    iterations: iterations,
                    environment: {
                        userAgent: navigator.userAgent,
                        platform: navigator.platform || "Unknown",
                        cores: navigator.hardwareConcurrency || "Unknown",
                        timestamp: new Date().toISOString(),
                    },
                    results: algResults,
                };

                renderResults(currentBenchmarkResults);
            } catch (err) {
                showToast("Benchmark encountered error: " + err.message);
            } finally {
                startBtn.disabled = false;
                startBtn.textContent = "Start Benchmark";
                progressText.textContent = "";
            }
        }, 50);
    }

    function renderResults(data) {
        resultsCard.style.display = "block";

        // Environment info
        const env = data.environment || {};
        envInfoEl.innerHTML = `
            <strong>Environment:</strong> ${escapeHtml(data.engine || 'Host Runtime')} | 
            Cores: <strong>${escapeHtml(env.cores || env.architecture || 'N/A')}</strong> | 
            Payload Size: <strong>${data.size_label}</strong> | 
            Iterations: <strong>${data.iterations}</strong>
        `;

        // Render Table
        resultsTableBody.innerHTML = data.results.map((r, idx) => `
            <tr>
                <td><strong>#${idx + 1}</strong></td>
                <td><strong>${escapeHtml(r.algorithm)}</strong></td>
                <td>${r.avg_time_ms} ms</td>
                <td>${r.min_time_ms} ms</td>
                <td>${r.max_time_ms} ms</td>
                <td><strong class="bench-throughput">${r.throughput_mbs} MB/s</strong></td>
            </tr>
        `).join("");

        // Render Bar Chart
        renderChart(data.results);
    }

    function renderChart(results) {
        const maxThroughput = Math.max(...results.map((r) => r.throughput_mbs), 1);

        chartContainer.innerHTML = results.map((r) => {
            const pct = Math.max(8, Math.round((r.throughput_mbs / maxThroughput) * 100));
            return `
                <div class="chart-row">
                    <div class="chart-label">${escapeHtml(r.algorithm)}</div>
                    <div class="chart-bar-wrap">
                        <div class="chart-bar-fill" style="width: ${pct}%;">
                            <span class="chart-bar-text">${r.throughput_mbs} MB/s</span>
                        </div>
                    </div>
                </div>
            `;
        }).join("");
    }

    function exportCsv() {
        if (!currentBenchmarkResults) return;
        const headers = ["Algorithm", "Avg_Time_ms", "Min_Time_ms", "Max_Time_ms", "Throughput_MB_s", "Payload_Bytes", "Iterations"];
        const rows = currentBenchmarkResults.results.map((r) => [
            `"${r.algorithm}"`,
            r.avg_time_ms,
            r.min_time_ms,
            r.max_time_ms,
            r.throughput_mbs,
            r.bytes_per_iteration,
            r.iterations
        ]);
        const csv = [headers.join(","), ...rows.map(r => r.join(","))].join("\r\n");
        downloadBlob(csv, "hash_benchmark_results.csv", "text/csv;charset=utf-8;");
    }

    function exportJson() {
        if (!currentBenchmarkResults) return;
        downloadBlob(JSON.stringify(currentBenchmarkResults, null, 2), "hash_benchmark_results.json", "application/json;charset=utf-8;");
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

    startBtn.addEventListener("click", runBenchmark);
    exportCsvBtn.addEventListener("click", exportCsv);
    exportJsonBtn.addEventListener("click", exportJson);
})();
