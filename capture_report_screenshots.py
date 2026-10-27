import subprocess
import time
import json
import urllib.request
import asyncio
import websockets
import base64
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
TMP_DIR = r"C:\Users\0xghost\AppData\Local\Temp\chrome_report_profile"
OUTPUT_DIR = r"report_assets"

os.makedirs(OUTPUT_DIR, exist_ok=True)

async def capture_all():
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1600,1000",
        f"--user-data-dir={TMP_DIR}",
        "http://127.0.0.1:5000/"
    ])

    try:
        time.sleep(2)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list").read().decode()
        targets = json.loads(resp)
        page = [t for t in targets if t.get("type") == "page"][0]
        ws_url = page["webSocketDebuggerUrl"]
        print(f"Connected to Chrome page: {ws_url}", flush=True)

        async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
            msg_id = 0
            async def call(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
                while True:
                    raw = await ws.recv()
                    data = json.loads(raw)
                    if data.get("id") == msg_id:
                        return data.get("result", {})

            await call("Runtime.enable")
            await call("Page.enable")
            await call("Emulation.setDeviceMetricsOverride", {
                "width": 1600,
                "height": 1050,
                "deviceScaleFactor": 1,
                "mobile": False
            })

            async def take_screenshot(filename):
                shot = await call("Page.captureScreenshot", {"format": "png"})
                img_data = base64.b64decode(shot["data"])
                out_path = os.path.join(OUTPUT_DIR, filename)
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"[SAVED] {out_path} ({len(img_data)/1024:.1f} KB)", flush=True)

            # -------------------------------------------------------------
            # 1. Single Hash Identifier
            # -------------------------------------------------------------
            print("\nCapturing 01_single_hash_identifier.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-identifier');
                    const inp = document.getElementById('hash-input');
                    inp.value = '5f4dcc3b5aa765d61d8327deb882cf99';
                    document.getElementById('identify-btn').click();
                    await new Promise(r => setTimeout(r, 400));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("01_single_hash_identifier.png")

            # -------------------------------------------------------------
            # 2. Batch Scanner
            # -------------------------------------------------------------
            print("\nCapturing 02_batch_scanner.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-batch');
                    const txt = document.getElementById('batch-input');
                    txt.value = [
                        '5f4dcc3b5aa765d61d8327deb882cf99',
                        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',
                        'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                        '$2b$12$e8cr0ym8zI6gkNVoU2k3QOD7O7sL6lC55kK3i8V1n6j6iH5W2kQ3e',
                        '31d6cfe0d16ae931b73c59d7e0c089c0'
                    ].join('\\n');
                    const scanBtn = document.getElementById('batch-scan-btn');
                    if (scanBtn) scanBtn.click();
                    await new Promise(r => setTimeout(r, 600));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("02_batch_scanner.png")

            # -------------------------------------------------------------
            # 3. Hash Generator
            # -------------------------------------------------------------
            print("\nCapturing 03_hash_generator.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-generator');
                    const inp = document.getElementById('gen-text-input');
                    inp.value = 'Antigravity_Digital_Forensics_Capstone_2026';
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    await new Promise(r => setTimeout(r, 400));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("03_hash_generator.png")

            # -------------------------------------------------------------
            # 4. File Hasher
            # -------------------------------------------------------------
            print("\nCapturing 04_file_hasher.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-file-hasher');
                    await new Promise(r => setTimeout(r, 300));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("04_file_hasher.png")

            # -------------------------------------------------------------
            # 5. Duplicate Detector
            # -------------------------------------------------------------
            print("\nCapturing 05_duplicate_detector.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-duplicates');
                    const inp = document.getElementById('dup-input');
                    inp.value = [
                        '5f4dcc3b5aa765d61d8327deb882cf99',
                        'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                        '5f4dcc3b5aa765d61d8327deb882cf99',
                        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',
                        '5f4dcc3b5aa765d61d8327deb882cf99',
                        'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
                    ].join('\\n');
                    const btn = document.getElementById('dup-find-btn');
                    if (btn) btn.click();
                    await new Promise(r => setTimeout(r, 400));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("05_duplicate_detector.png")

            # -------------------------------------------------------------
            # 6. Diff Analyzer
            # -------------------------------------------------------------
            print("\nCapturing 06_diff_analyzer.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-diff');
                    const a = document.getElementById('diff-list-a');
                    const b = document.getElementById('diff-list-b');
                    a.value = [
                        '5f4dcc3b5aa765d61d8327deb882cf99',
                        'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
                    ].join('\\n');
                    b.value = [
                        '5f4dcc3b5aa765d61d8327deb882cf99',
                        'd41d8cd98f00b204e9800998ecf8427e',
                        '31d6cfe0d16ae931b73c59d7e0c089c0'
                    ].join('\\n');
                    const btn = document.getElementById('diff-analyze-btn');
                    if (btn) btn.click();
                    await new Promise(r => setTimeout(r, 400));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("06_diff_analyzer.png")

            # -------------------------------------------------------------
            # 7. Manifest Tool
            # -------------------------------------------------------------
            print("\nCapturing 07_manifest_tool.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-manifest');
                    const inp = document.getElementById('manifest-input');
                    inp.value = [
                        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824  evidence_disk_image.raw',
                        '5f4dcc3b5aa765d61d8327deb882cf99a89d71c2b5368a2d1f974c83  incident_timeline.csv',
                        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  empty_decoy.bin'
                    ].join('\\n');
                    const btn = document.getElementById('manifest-verify-btn');
                    if (btn) btn.click();
                    await new Promise(r => setTimeout(r, 400));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(0.5)
            await take_screenshot("07_manifest_tool.png")

            # -------------------------------------------------------------
            # 8. Benchmark Tool
            # -------------------------------------------------------------
            print("\nCapturing 08_benchmark_tool.png...", flush=True)
            await call("Runtime.evaluate", {
                "expression": """
                (async () => {
                    window.switchToolkitTab('tab-benchmark');
                    const btn = document.getElementById('bench-run-btn');
                    if (btn) btn.click();
                    // Wait for benchmark iterations to complete
                    await new Promise(r => setTimeout(r, 1200));
                })()
                """,
                "awaitPromise": True
            })
            await asyncio.sleep(1.0)
            await take_screenshot("08_benchmark_tool.png")

            # -------------------------------------------------------------
            # 9. Authors Page
            # -------------------------------------------------------------
            print("\nCapturing 09_authors_page.png...", flush=True)
            await call("Page.navigate", {"url": "http://127.0.0.1:5000/authors"})
            await asyncio.sleep(1.5)
            await take_screenshot("09_authors_page.png")

            # -------------------------------------------------------------
            # 10. Security 404 Page
            # -------------------------------------------------------------
            print("\nCapturing 10_security_404_page.png...", flush=True)
            await call("Page.navigate", {"url": "http://127.0.0.1:5000/non-existent-page-forensics-audit"})
            await asyncio.sleep(1.5)
            await take_screenshot("10_security_404_page.png")

            print("\nAll 10 screenshots successfully captured!", flush=True)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(capture_all())
