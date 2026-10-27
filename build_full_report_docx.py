import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import os

DOC_FILENAME = "Hash_Identifier_Comprehensive_Project_Report.docx"
ASSETS_DIR = "report_assets"

# Brand Color Palette
HEX_NAVY = "0F4C81"       # Primary Cyber Blue
HEX_SLATE_DARK = "1E293B"   # Text Main
HEX_MUTED = "64748B"        # Subtitles / Captions
HEX_LIGHT_BG = "F8FAFC"     # Callout / Table Alt
HEX_BORDER = "CBD5E1"       # Clean Border
HEX_EMERALD = "059669"      # Success / Verified
HEX_AMBER = "D97706"        # Alert / Warning

COLOR_NAVY = RGBColor(15, 76, 129)
COLOR_SLATE_DARK = RGBColor(30, 41, 59)
COLOR_MUTED = RGBColor(100, 116, 139)
COLOR_EMERALD = RGBColor(5, 150, 105)

def create_report():
    doc = Document()

    # 1. Page Setup: Standard Letter, 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

        # Header for subsequent pages
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Hash Identifier & Analysis Toolkit  |  Applied Cryptography & Forensics Engineering Report")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_MUTED

        # Footer for subsequent pages
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun_left = fp.add_run("Mehran University of Engineering and Technology (MUET) — Department of Cyber Security")
        frun_left.font.name = "Calibri"
        frun_left.font.size = Pt(8.5)
        frun_left.font.color.rgb = COLOR_MUTED

    # Helpers
    def set_cell_background(cell, hex_color):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_callout_border(cell, hex_border_color=HEX_NAVY):
        border_xml = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="none"/>'
            f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{hex_border_color}"/>'
            f'<w:bottom w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'</w:tcBorders>'
        )
        cell._tc.get_or_add_tcPr().append(border_xml)

    def add_callout(text, prefix="KEY FORENSIC PRINCIPLE:", border_color=HEX_NAVY):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, HEX_LIGHT_BG)
        set_callout_border(cell, border_color)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.15)
        p.paragraph_format.right_indent = Inches(0.15)
        
        prun = p.add_run(f"{prefix} ")
        prun.bold = True
        prun.font.name = "Calibri"
        prun.font.size = Pt(9.5)
        prun.font.color.rgb = COLOR_NAVY if border_color == HEX_NAVY else COLOR_EMERALD

        trun = p.add_run(text)
        trun.font.name = "Calibri"
        trun.font.size = Pt(9.5)
        trun.font.color.rgb = COLOR_SLATE_DARK
        
        # Add space after table
        sp = doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(4)

    def add_styled_heading(text, level=1):
        h = doc.add_heading(level=level)
        h.paragraph_format.keep_with_next = True
        run = h.add_run(text)
        run.font.name = "Calibri"
        if level == 1:
            h.paragraph_format.space_before = Pt(18)
            h.paragraph_format.space_after = Pt(6)
            run.font.size = Pt(17)
            run.bold = True
            run.font.color.rgb = COLOR_NAVY
        elif level == 2:
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            run.font.size = Pt(13.5)
            run.bold = True
            run.font.color.rgb = COLOR_SLATE_DARK
        elif level == 3:
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(2)
            run.font.size = Pt(11)
            run.bold = True
            run.font.color.rgb = COLOR_MUTED
        return h

    def add_body_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            bp = p.add_run(bold_prefix)
            bp.bold = True
            bp.font.name = "Calibri"
            bp.font.size = Pt(10.5)
            bp.font.color.rgb = COLOR_SLATE_DARK
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_SLATE_DARK
        return p

    def add_bullet_item(bold_label, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        br = p.add_run(bold_label)
        br.bold = True
        br.font.name = "Calibri"
        br.font.size = Pt(10)
        br.font.color.rgb = COLOR_SLATE_DARK
        tr = p.add_run(" " + text)
        tr.font.name = "Calibri"
        tr.font.size = Pt(10)
        tr.font.color.rgb = COLOR_SLATE_DARK
        return p

    def add_figure(img_filename, caption_text):
        img_path = os.path.join(ASSETS_DIR, img_filename)
        if not os.path.exists(img_path):
            print(f"Warning: Image {img_path} not found!")
            return
        
        # Center image paragraph
        ip = doc.add_paragraph()
        ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ip.paragraph_format.space_before = Pt(8)
        ip.paragraph_format.space_after = Pt(4)
        ip.paragraph_format.keep_with_next = True
        run = ip.add_run()
        run.add_picture(img_path, width=Inches(6.2))

        # Caption paragraph
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(12)
        c_run = cp.add_run(caption_text)
        c_run.font.name = "Calibri"
        c_run.font.size = Pt(9)
        c_run.italic = True
        c_run.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # 1. FORMAL COVER PAGE
    # =========================================================================
    cover_top = doc.add_paragraph()
    cover_top.paragraph_format.space_before = Pt(40)
    cover_top.paragraph_format.space_after = Pt(4)
    run_inst = cover_top.add_run("MEHRAN UNIVERSITY OF ENGINEERING AND TECHNOLOGY (MUET)")
    run_inst.font.name = "Calibri"
    run_inst.font.size = Pt(11)
    run_inst.bold = True
    run_inst.font.color.rgb = COLOR_MUTED
    
    dept_p = doc.add_paragraph()
    dept_p.paragraph_format.space_after = Pt(40)
    dept_r = dept_p.add_run("Department of Cyber Security • Jamshoro, Sindh, Pakistan")
    dept_r.font.name = "Calibri"
    dept_r.font.size = Pt(10)
    dept_r.font.color.rgb = COLOR_MUTED

    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_after = Pt(12)
    t_run = title_p.add_run("HASH IDENTIFIER & ANALYSIS TOOLKIT")
    t_run.font.name = "Calibri"
    t_run.font.size = Pt(28)
    t_run.bold = True
    t_run.font.color.rgb = COLOR_NAVY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(36)
    sub_r = sub_p.add_run("A Defense-Grade, In-Browser Cryptographic Triage, Structural Identification, Integrity Verification & Multi-Algorithm Analysis Framework")
    sub_r.font.name = "Calibri"
    sub_r.font.size = Pt(13)
    sub_r.font.color.rgb = COLOR_SLATE_DARK

    # Metadata Table
    meta_table = doc.add_table(rows=6, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.LEFT
    meta_rows = [
        ("Project Capstone Domain:", "Applied Cryptography, Digital Forensics & SOC Triage Engineering"),
        ("Lead Security Creator:", "Kinza (Creator & Lead Security Developer)"),
        ("System & Security Architect:", "Salman Mallah (Co-Author, Research & Systems Architecture)"),
        ("Institutional Affiliation:", "Mehran University of Engineering and Technology (MUET)"),
        ("Production System Version:", "Version 2.4 Production Release (Client In-Browser Zero-Leakage Engine)"),
        ("Publication Date:", "October 2026"),
    ]
    for idx, (label, val) in enumerate(meta_rows):
        row = meta_table.rows[idx]
        c0 = row.cells[0]
        c1 = row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(3)
        r0 = p0.add_run(label)
        r0.bold = True
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = COLOR_NAVY
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(val)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_SLATE_DARK

    doc.add_page_break()

    # =========================================================================
    # 2. EXECUTIVE SUMMARY & ABSTRACT
    # =========================================================================
    add_styled_heading("Executive Summary & Abstract", level=1)
    
    add_body_p(
        "Modern Security Operations Centers (SOCs), incident response teams, and digital forensics laboratories handle millions of cryptographic digests daily. Hashes serve as fundamental, immutable indicators of compromise (IOCs), evidentiary baseline checkpoints, and authentication tokens. However, digital forensic triage routinely encounters severe operational friction: forensic investigators encounter unknown hash strings without contextual metadata, hash algorithm lengths collide across historical standards (e.g., 32 hexadecimal characters can indicate MD5, NTLM, MD4, or LM), and legacy web-based lookup services introduce critical data leakage hazards by transmitting sensitive proprietary hashes across third-party cloud infrastructure."
    )
    add_body_p(
        "To decisively solve these foundational operational vulnerabilities, the Hash Identifier & Analysis Toolkit was designed and engineered as a defense-grade, comprehensive cryptographic triage suite. Built under the Department of Cyber Security at Mehran University of Engineering and Technology (MUET) by Kinza and Salman Mallah, the framework provides an end-to-end local capability covering: (1) single hash structural identification with ranked confidence and ambiguity advisories; (2) high-throughput batch list triage; (3) multi-algorithm hash generation with strict canonical UTF-8 encoding; (4) chunked in-browser multi-gigabyte file integrity hashing; (5) duplicate threat IOC clustering; (6) forensic baseline diff analysis (List A vs. List B); (7) RFC-compliant SHA-256 integrity manifest generation; and (8) hardware cryptographic throughput benchmarking."
    )

    add_callout(
        "Zero Cloud Transmission Guarantee: The Hash Identifier & Analysis Toolkit implements a client-in-browser privacy-first paradigm. Cryptographic parsing, regex scoring, and chunked file hashing execute entirely within the client's local memory sandbox via HTML5 Web Cryptography APIs and FileReader chunking, guaranteeing zero payload leakage across external networks.",
        prefix="CORE ARCHITECTURAL ASSURANCE:",
        border_color=HEX_EMERALD
    )

    # =========================================================================
    # 3. PROBLEM STATEMENT & BACKGROUND
    # =========================================================================
    add_styled_heading("Chapter 1: Problem Statement & Forensic Background", level=1)
    
    add_styled_heading("1.1 The Operational Problem in Digital Forensics & SOC Triage", level=2)
    add_body_p(
        "During live cyber incident response and post-mortem digital investigations, analysts routinely extract hundreds or thousands of unlabelled hash strings from endpoint memory artifacts, web server access logs, firewall telemetry, and database breach dumps. Investigators face three critical systemic dilemmas:"
    )
    add_bullet_item("1. The Hash Ambiguity / Length Collision Dilemma:", "Cryptographic hash algorithms produce fixed-length digests. Because multiple distinct algorithms share identical output lengths (e.g., 128-bit digests are exactly 32 hex characters for MD5, NTLM, MD4, and LM; 256-bit digests produce 64 hex characters for SHA-256, SHA3-256, BLAKE2s, and GOST R 34.11-94), an analyst cannot identify the generating algorithm purely by observing digest length. Misidentifying an NTLM password hash as an MD5 digest causes massive delays in credential auditing and forensic attribution.")
    add_bullet_item("2. Cryptographic Vulnerability Ignorance:", "Legacy algorithms such as MD5 (RFC 1321) and SHA-1 (FIPS 180-1) suffer from catastrophic practical collision attacks (e.g., Flame malware collision, SHAttered attack). Analysts without real-time vulnerability contextualization frequently accept collision-vulnerable hashes as authoritative proof of binary integrity, introducing severe chain-of-custody risks.")
    add_bullet_item("3. Data Leakage via Cloud-Based Lookup Utilities:", "Traditional analysts frequently copy-paste unknown hashes into commercial SaaS lookup engines or public multi-scanner portals. In sensitive breach investigations, submitting internal password hashes, custom proprietary malware digests, or classified database keys directly alerts adversaries through threat-intel telemetry feeds and exposes private organizational assets.")

    add_styled_heading("1.2 Strategic Objectives & Core Value Proposition", level=2)
    add_body_p(
        "The primary purpose of developing this toolkit was to replace disparate, insecure, and ambiguous tools with a consolidated, defense-grade platform. The project delivers quantifiable advantages:"
    )
    add_bullet_item("Client-Side Sandboxing:", "100% of cryptographic identification, file streaming, and digest generation executes locally in browser runtime with zero outbound server transmission.")
    add_bullet_item("Evidence-Based Ambiguity Scoring:", "Algorithms are scored using a multi-factor heuristics engine considering bit length, exact character sets, salt markers, and regex signatures, clearly warning analysts whenever length collision exists.")
    add_bullet_item("End-to-End Triage Ecosystem:", "Integrates 8 specialized forensic tools under a single unified cyber-themed interface, eliminating the need to pivot across command-line utilities.")

    # =========================================================================
    # 4. SYSTEM ARCHITECTURE & PRIVACY-FIRST DEFENSE ENGINE
    # =========================================================================
    add_styled_heading("Chapter 2: System Architecture & Cryptographic Engine", level=1)
    
    add_body_p(
        "The toolkit is engineered on a resilient dual-tier architecture combining modern client-side Web Cryptography standards with an optional Python Flask backend for automated server-side batch scripting."
    )

    add_styled_heading("2.1 Client In-Browser Cryptographic Engine", level=2)
    add_body_p(
        "The primary execution layer resides entirely within the client browser. Implemented across static/js/crypto_engine.js and specialized tool modules, this engine leverages:"
    )
    add_bullet_item("HTML5 Web Cryptography API (crypto.subtle):", "Provides hardware-accelerated, native implementations of SHA-256, SHA-384, and SHA-512 directly accessing CPU cryptographic acceleration (e.g., Intel SHA Extensions, ARMv8 Crypto).")
    add_bullet_item("Lightweight Pure JS Primitives:", "For legacy algorithms not exposed by subtle crypto (MD5, SHA-1), optimized client-side bitwise transformation routines execute with zero external third-party dependencies.")
    add_bullet_item("Chunked HTML5 FileReader Pipeline:", "Processes multi-gigabyte disk images and binary files in sequential 2MB memory chunks without exhausting browser heap memory or stalling the main UI event loop.")

    add_styled_heading("2.2 Dual-Tier Architecture Model", level=2)
    
    # Arch Table
    arch_table = doc.add_table(rows=5, cols=3)
    arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Component", "Execution Context", "Forensic Responsibilities"]
    for i, h in enumerate(headers):
        cell = arch_table.cell(0, i)
        set_cell_background(cell, HEX_NAVY)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    arch_data = [
        ("Frontend Client Engine", "Client Browser Sandbox (JS / Web Crypto)", "Instant hash generation, single identification, FileReader streaming, clipboard operations, dynamic UI responsiveness."),
        ("Flask REST API Tier", "Python 3.14 / Flask (Localhost / LAN)", "High-throughput server-side batch evaluation, headless automation endpoints, SQLite reference database management."),
        ("Core Detection Rules", "Hybrid (core/detector.py & crypto_engine.js)", "Comprehensive regex pattern library matching 30+ algorithm signatures, confidence scoring, collision risk tagging."),
        ("Persistence & Reference", "Local SQLite Engine (hash_lookup.db)", "Local hash lookup dictionary, custom database search, provenance metadata tracking, zero cloud synchronization.")
    ]
    for row_idx, data in enumerate(arch_data, start=1):
        for col_idx, text in enumerate(data):
            cell = arch_table.cell(row_idx, col_idx)
            set_cell_background(cell, HEX_LIGHT_BG if row_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_SLATE_DARK

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)

    # =========================================================================
    # 5. DETAILED FEATURE BREAKDOWN WITH EMBEDDED SCREENSHOTS
    # =========================================================================
    add_styled_heading("Chapter 3: Comprehensive Page-by-Page & Feature Forensic Breakdown", level=1)
    
    add_body_p(
        "This chapter examines each of the 8 core operational tools and 2 administrative views within the framework. For every component, this report documents: (1) why it was built (Purpose / Objective); (2) its operational and forensic value (Benefits); (3) its underlying technical mechanics; and (4) its captured production UI state."
    )

    # -------------------------------------------------------------------------
    # Tool 1: Single Hash Identifier
    # -------------------------------------------------------------------------
    add_styled_heading("3.1 Tool 1: Single Hash Identifier & Structural Analysis", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Investigators frequently recover isolated, unlabelled cryptographic digests from memory dumps, config files, or network logs. In traditional workflows, identifying candidate algorithms requires manual length counting or invoking separate command-line utilities. Tool 1 was created to provide instant, real-time structural analysis of any entered hash, automatically calculating string length, character set distribution, entropy, and matching against over 30 forensic signatures with evidence-based match scoring."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Ambiguity Warning System:", "Instantly alerts investigators when a digest's length produces multiple valid candidates (e.g., 32-hex ambiguity between MD5, NTLM, and MD4), preventing misdirected investigative actions.")
    add_bullet_item("NIST Collision Risk Advisories:", "Highlights algorithms compromised by practical collision vulnerabilities (MD5, SHA-1) with prominent visual warning chips.")
    add_bullet_item("Real-Time Structural Feedback:", "Dynamically measures hexadecimal validity, character length, and renders a visual strength and complexity bar.")

    add_figure("01_single_hash_identifier.png", "Figure 1: Production UI of Single Hash Identifier analyzing an MD5 digest (5f4dcc3b5aa765d61d8327deb882cf99) with Ambiguity Alert and NIST Collision Advisory.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "When an analyst inputs a hash string, the input triggers sanitizeHashInput() to strip accidental whitespace and quotation marks. The engine evaluates: (1) byte and bit length; (2) hexadecimal conformance (/^[a-fA-F0-9]+$/); (3) Base64 markers; and (4) specific modular crypt format prefixes (e.g., $2b$, $6$, $argon2id$). Candidate algorithms are scored out of 100 based on length accuracy, character distribution, and cryptographic context. Results are sorted hierarchically, with the top match badge highlighted."
    )

    # -------------------------------------------------------------------------
    # Tool 2: Batch Hash Scanner
    # -------------------------------------------------------------------------
    add_styled_heading("3.2 Tool 2: Batch Hash Scanner", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Incident response triage rarely involves single hashes; analysts routinely receive threat intelligence reports, SIEM query exports, or EDR telemetry dumps containing hundreds or thousands of unclassified hashes. Evaluating them individually is operationally impossible. Tool 2 was developed to ingest multi-thousand-line text streams or uploaded TXT/CSV files, performing concurrent batch identification in sub-second time."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("High-Throughput Bulk Triage:", "Parses and classifies bulk lists of heterogeneous hashes in parallel, drastically reducing initial incident triage time from hours to seconds.")
    add_bullet_item("Interactive Sorting & Filtering:", "Analysts can filter the entire batch result set by candidate algorithm (e.g., isolate all MD5s or all SHA-256s) and confidence thresholds.")
    add_bullet_item("Forensic CSV Export:", "Generates timestamped, structured CSV and TXT audit exports ready for direct attachment to formal incident response case dossiers.")

    add_figure("02_batch_scanner.png", "Figure 2: Batch Hash Scanner processing a heterogeneous multi-hash list with algorithm categorization, confidence tags, and export options.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "The batch engine splits input streams across newline boundaries, strips control characters, and applies multi-threaded regex matching. Each entry receives an indexed record detailing line number, raw string, length, character set, top candidate algorithm, confidence tier (High, Medium, Low), and ambiguity count. Summary counters provide an executive overview of parsed versus invalid entries."
    )

    # -------------------------------------------------------------------------
    # Tool 3: Multi-Algorithm Hash Generator
    # -------------------------------------------------------------------------
    add_styled_heading("3.3 Tool 3: Multi-Algorithm Hash Generator", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Security engineers, penetration testers, and forensics developers constantly need baseline reference hashes of specific strings (known passwords, tokens, Canary seeds, or configuration headers) across multiple standard algorithms simultaneously. Tool 3 was engineered to generate MD5, SHA-1, SHA-256, SHA-384, and SHA-512 digests concurrently in real-time from arbitrary plaintext or Unicode inputs."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Multi-Algorithm Simultaneous Computation:", "Eliminates switching between multiple terminal commands (md5sum, sha256sum, sha512sum) by displaying all 5 canonical digests in parallel cards.")
    add_bullet_item("Strict Canonical UTF-8 Byte Conversion:", "Enforces canonical UTF-8 byte serialization, guaranteeing identical cross-platform digest outputs matching NIST standards.")
    add_bullet_item("Universal One-Click 'Copy All Hashes':", "Features a specialized universal clipboard copy handler that formats a standardized report table and copies it seamlessly across both HTTPS and insecure LAN HTTP origins.")

    add_figure("03_hash_generator.png", "Figure 3: Multi-Algorithm Hash Generator displaying real-time concurrent digests across 5 algorithms with the active 'Copy All Hashes' action.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "As the user types into the plaintext field, input event listeners trigger stringToUtf8Bytes() encoding. Digits are computed via window.CryptoEngine.hashText(text) synchronously on the client. MD5 (128-bit) and SHA-1 (160-bit) cards are explicitly styled with amber legacy warnings, while SHA-2 family digests reflect modern collision-resistant cryptographic strength. Empty strings explicitly generate canonical zero-byte digests (e.g., MD5 d41d8cd98f00b204e9800998ecf8427e)."
    )

    # -------------------------------------------------------------------------
    # Tool 4: File Hash Calculator & Integrity Verifier
    # -------------------------------------------------------------------------
    add_styled_heading("3.4 Tool 4: File Hash Calculator & Integrity Verifier", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Establishing file integrity is the cornerstone of forensic chain of custody. Calculating file hashes through cloud-based utilities risks severe data breach by transmitting confidential evidence over external WANs, while uploading multi-gigabyte forensic disk images (E01, RAW) over web forms is technically infeasible. Tool 4 was engineered to stream and hash multi-gigabyte files directly inside browser client memory with zero server transmission."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("100% Privacy & Zero Network Latency:", "Files never leave the investigator's local workstation. Multi-gigabyte binaries and disk images process at native drive read speeds.")
    add_bullet_item("Automated Integrity Verification:", "Analysts can paste an expected vendor checksum (e.g., from a forensic software release or chain-of-custody log); the tool compares it against the computed digest, displaying an immediate high-visibility green 'MATCH VERIFIED' or red 'TAMPERED / MISMATCH' status.")
    add_bullet_item("Multi-Algorithm Selection:", "Supports SHA-256 (default forensic standard), SHA-512, SHA-384, SHA-1, and MD5.")

    add_figure("04_file_hasher.png", "Figure 4: File Hash Calculator & Integrity Verifier featuring local drag-and-drop file ingestion, algorithm selection, and verification controls.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "The file hasher utilizes an HTML5 FileReader chunking loop with a 2MB chunk window. Binary chunks are read as ArrayBuffers and fed iteratively into the cryptographic engine. A dynamic progress bar and throughput counter keep the UI responsive throughout processing."
    )

    # -------------------------------------------------------------------------
    # Tool 5: Duplicate Hash Detection
    # -------------------------------------------------------------------------
    add_styled_heading("3.5 Tool 5: Duplicate Hash Detection", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "In enterprise forensic audits, investigators aggregate hashes from multiple endpoint logs and disk scans. Redundant hashes clutter analysis, bloat SIEM rule sets, and obscure unique artifacts. Tool 5 was built to instantly identify repeated hash strings, track exact line occurrences, and calculate distribution frequency."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Threat Frequency & Persistence Profiling:", "A hash appearing dozens of times across endpoints often indicates wide-scale malware persistence or lateral movement.")
    add_bullet_item("SIEM & EDR Rule Set Optimization:", "Enables analysts to strip duplicates and copy a unique, deduplicated list for ingestion into security information systems.")
    add_bullet_item("Traceable Provenance:", "Lists exact input line numbers where each duplicate occurred, streamlining forensic cross-referencing.")

    add_figure("05_duplicate_detector.png", "Figure 5: Duplicate Hash Detection tool displaying grouped repeat entries, occurrence frequencies, and exact source line references.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "The duplicate engine maps normalized hash strings into a hash table in O(N) time complexity, recording occurrence arrays. Groups with frequency >= 2 are sorted in descending order of occurrence and rendered with visual badges and deduplicated export shortcuts."
    )

    # -------------------------------------------------------------------------
    # Tool 6: Hash List Diff Analyzer
    # -------------------------------------------------------------------------
    add_styled_heading("3.6 Tool 6: Hash List Diff Analyzer", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Differential analysis is among the most powerful methodologies in incident triage: comparing a known-good baseline (Golden Image system files, pre-incident logs) against an infected system state. Manual diffing across thousands of hashes is intensely error-prone. Tool 6 was created to execute set-theoretic comparative analysis between two distinct hash lists (List A vs. List B)."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Rapid Unauthorized Binary Detection:", "The 'Unique to List B' set immediately isolates files introduced during the attack window.")
    add_bullet_item("File Deletion / Tampering Detection:", "The 'Unique to List A' set highlights baseline system binaries that were deleted or modified by threat actors.")
    add_bullet_item("Confirmed Unaltered Baselines:", "The 'Common / Intersecting' set verifies intact system components, allowing investigators to narrow their focus to modified artifacts.")

    add_figure("06_diff_analyzer.png", "Figure 6: Hash List Diff Analyzer comparing List A vs List B with breakdown cards for Common, Unique to A, and Unique to B.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        r"Input lists are parsed into sanitized sets: Set A and Set B. The engine computes: (1) Intersection (A ∩ B); (2) Set Difference (A \ B); and (3) Set Difference (B \ A). Results are rendered in distinct color-coded panels with individual export buttons."
    )

    # -------------------------------------------------------------------------
    # Tool 7: Hash Manifest Generator & Verifier
    # -------------------------------------------------------------------------
    add_styled_heading("3.7 Tool 7: Hash Manifest Generator & Verifier", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Digital evidence handling requires formal integrity manifests compliant with NIST and RFC standards. Checksum files in GNU coreutils format (<hash>  <filename>) are universally recognized in courtrooms and forensic labs. Tool 7 was engineered to validate, verify, and format SHA-256 integrity manifests."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Courtroom Chain of Custody Compliance:", "Enforces standard 2-space GNU delimiter syntax for seamless interoperability with sha256sum -c.")
    add_bullet_item("Automated Syntax & Hash Validation:", "Flags malformed checksum entries, invalid hexadecimal lengths, and illegal characters before evidence dissemination.")
    add_bullet_item("Multi-Format Export:", "Exports verified manifests as formatted TXT or CSV files.")

    add_figure("07_manifest_tool.png", "Figure 7: Hash Manifest Generator & Verifier checking GNU-format SHA-256 manifests with status badges and format options.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "Manifest text is parsed using regular expression /^([a-fA-F0-9]{64})\\s+[* ]?(.+)$/mg. Valid records are validated against length and charset constraints, with metrics detailing total files, valid manifests, and formatting anomalies."
    )

    # -------------------------------------------------------------------------
    # Tool 8: Cryptographic Benchmark & Throughput Analyzer
    # -------------------------------------------------------------------------
    add_styled_heading("3.8 Tool 8: Cryptographic Benchmark & Throughput Analyzer", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Forensic engineers need empirical data on how fast specific cryptographic algorithms execute on host hardware to accurately plan large-scale hashing operations (e.g., hashing a 2TB disk image). Tool 8 was created to dynamically benchmark algorithm throughput (MB/s) and execution latency across algorithms under controlled payload conditions."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Empirical Hardware Capacity Planning:", "Measures real-world host throughput, allowing investigators to calculate accurate completion times for multi-terabyte evidence acquisitions.")
    add_bullet_item("Security vs. Speed Optimization Guidance:", "Demonstrates that while MD5/SHA-1 exhibit high throughput due to simpler round functions, modern algorithms like SHA-256 and SHA-512 provide superior security with negligible performance penalties on modern SIMD hardware.")
    add_bullet_item("Comparative Benchmarking Cards:", "Renders comparative visual metrics showing throughput, operations per second, and elapsed execution time in milliseconds.")

    add_figure("08_benchmark_tool.png", "Figure 8: Cryptographic Benchmark Tool displaying measured execution throughput (MB/s) and timing across cryptographic algorithms.")

    add_body_p(
        "Detailed Technical Mechanics:", bold_prefix="• "
    )
    add_body_p(
        "The benchmark allocates a calibrated 1MB memory buffer in client memory. It executes warm-up runs followed by 5 timed iterations per algorithm, measuring durations via high-resolution performance.now() timestamps. Throughput is computed as: Throughput (MB/s) = (Payload_Bytes * Iterations) / (Elapsed_Seconds * 1,000,000)."
    )

    # -------------------------------------------------------------------------
    # Administrative & Credits Pages
    # -------------------------------------------------------------------------
    add_styled_heading("3.9 Authors & Technical Credits View (/authors)", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "To establish academic rigor, intellectual provenance, and engineering accountability. Designed under the auspices of the Department of Cyber Security at Mehran University of Engineering and Technology (MUET), Jamshoro, this page formally attributes project leadership, technical roles, institutional credentials, and defense-grade system specifications."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Institutional Trust & Academic Heritage:", "Documents the academic foundation at MUET Jamshoro, showcasing developer competencies in cyber security, applied cryptography, and web defense.")
    add_bullet_item("Architectural Disclosures:", "Publicly articulates the 100% in-browser privacy guarantee, client-side streaming engine, and RFC/NIST compliance.")
    add_bullet_item("Developer Transparency:", "Integrates direct GitHub profiles, institutional degree chips, and verified developer badges for peer review.")

    add_figure("09_authors_page.png", "Figure 9: Authors & Technical Credits page highlighting MUET Cyber Security affiliation, developer credentials, and technical architecture specifications.")

    # -------------------------------------------------------------------------
    # 404 Defense Page
    # -------------------------------------------------------------------------
    add_styled_heading("3.10 Error Handling & 404 Security Defense Page (/404)", level=2)
    add_body_p(
        "Kyun Banaya Gaya (Purpose / Objective):", bold_prefix="• "
    )
    add_body_p(
        "Default web framework 404 error handlers frequently disclose sensitive server banners, internal file system paths, and framework versions—a major security flaw (OWASP Information Disclosure). The 404 Defense Page was developed to suppress all server stack information and present a secure, themed interface that guides users back to active triage tools."
    )
    add_body_p(
        "Iska Faida & Forensic Value (Key Benefits):", bold_prefix="• "
    )
    add_bullet_item("Eliminates Information Disclosure:", "Suppresses framework error stack traces, internal paths, and Python/Werkzeug version banners.")
    add_bullet_item("Intuitive User Recovery:", "Provides direct shortcut navigation buttons to return to the Identifier, Batch Scanner, Generator, and Authors pages.")

    add_figure("10_security_404_page.png", "Figure 10: Custom branded 404 Security Error Handler suppressing server disclosure and providing navigation recovery.")

    # =========================================================================
    # 6. CRYPTOGRAPHIC STANDARDS & COMPARATIVE SPECIFICATIONS
    # =========================================================================
    add_styled_heading("Chapter 4: Cryptographic Standards Compliance & Algorithm Matrix", level=1)
    
    add_body_p(
        "The Hash Identifier & Analysis Toolkit strictly conforms to international cryptographic and digital forensic standards established by the National Institute of Standards and Technology (NIST) and the Internet Engineering Task Force (IETF)."
    )

    # Matrix Table
    spec_table = doc.add_table(rows=8, cols=5)
    spec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    spec_headers = ["Algorithm", "Digest Bits", "Hex Length", "NIST / FIPS Status", "Forensic Recommended Use"]
    for i, h in enumerate(spec_headers):
        cell = spec_table.cell(0, i)
        set_cell_background(cell, HEX_NAVY)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    spec_data = [
        ("MD5", "128 bits", "32 hex", "Deprecated (RFC 1321)", "Legacy identification only; prohibited for digital evidence integrity."),
        ("SHA-1", "160 bits", "40 hex", "Deprecated (FIPS 180-1)", "Legacy triage; collision attacks proven (SHAttered, 2017)."),
        ("SHA-256", "256 bits", "64 hex", "Standard (FIPS 180-4)", "Primary forensic gold standard; digital evidence chain of custody."),
        ("SHA-384", "384 bits", "96 hex", "Standard (FIPS 180-4)", "High-security digital signatures, federal compliance, Top Secret triage."),
        ("SHA-512", "512 bits", "128 hex", "Standard (FIPS 180-4)", "Maximum security binary integrity, 64-bit architecture optimization."),
        ("NTLM", "128 bits", "32 hex", "Insecure (MS-NLMP)", "Windows SAM database extraction; length collision with MD5."),
        ("Bcrypt", "184 bits", "60 chars", "Standard (RFC 2898 / OpenBSD)", "Adaptive key-stretched password hashing with salt and cost factor.")
    ]
    for row_idx, data in enumerate(spec_data, start=1):
        for col_idx, text in enumerate(data):
            cell = spec_table.cell(row_idx, col_idx)
            set_cell_background(cell, HEX_LIGHT_BG if row_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(text)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_SLATE_DARK

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(6)

    # =========================================================================
    # 7. QUALITY ASSURANCE & MULTI-AGENT UI AUDIT
    # =========================================================================
    add_styled_heading("Chapter 5: Quality Assurance & Multi-Agent UI Audit", level=1)
    
    add_body_p(
        "To ensure uncompromising production quality and cross-platform usability, the project underwent an intensive 15-agent automated UI and functional audit. Autonomous agents deployed across desktop, mobile, dark theme, light theme, and error boundary states identified and resolved key layout anomalies:"
    )
    add_bullet_item("Horizontal Viewport Overflow Elimination:", "Resolved a horizontal scrolling bug on mobile viewports (< 768px) by enforcing overflow-x: hidden on root containers and wrapping tab navigation in a smooth touch-scrolling container.")
    add_bullet_item("Author Avatar Status Badge Clipping:", "Fixed an overflow-clipping defect where the active presence indicator badge was clipped by the circular avatar container, refactoring badges into an unconstrained sibling wrapper.")
    add_bullet_item("Universal Clipboard Copy Implementation:", "Resolved clipboard access failures on unencrypted HTTP LAN IPs (e.g., 192.168.100.39:5000) where modern navigator.clipboard is disabled, establishing a robust textarea-based execCommand fallback.")
    add_bullet_item("Script Asset Caching & URL Encoding Fix:", "Corrected a Flask URL parameter encoding bug that caused script.js and generator_tool.js to return 404, restoring seamless tab switching and copy operations.")

    # =========================================================================
    # 8. CONCLUSION & ROADMAP
    # =========================================================================
    add_styled_heading("Chapter 6: Conclusion & Future Engineering Roadmap", level=1)
    
    add_body_p(
        "The Hash Identifier & Analysis Toolkit successfully achieves its core mandate: delivering a private, defense-grade, multi-faceted cryptographic triage suite that eliminates ambiguity, preserves data privacy, and accelerates digital forensics workflows. By uniting structural identification, batch processing, generator utilities, in-browser file streaming, diffing, and manifest verification, the application serves as a comprehensive capstone reference for academic and operational cybersecurity environments."
    )
    add_body_p(
        "Future architectural enhancements scheduled for subsequent iterations include:"
    )
    add_bullet_item("WebAssembly (Wasm) Engine Integration:", "Compiling native C/Rust cryptographic implementations into Wasm to achieve near-native file hashing speeds.")
    add_bullet_item("VirusTotal & AlienVault OTX Threat Feeds (Opt-In):", "Adding optional, user-consented threat intelligence enrichment for non-sensitive public hashes.")
    add_bullet_item("Forensic Case Management Export:", "Direct integration with open-source digital forensic platforms (Autopsy, DFIR Iris) for automated case artifact importing.")

    # Save document
    doc.save(DOC_FILENAME)
    print(f"\n[SUCCESS] Document saved successfully as: {DOC_FILENAME}")
    size = os.path.getsize(DOC_FILENAME)
    print(f"[FILE SIZE] {size / (1024*1024):.2f} MB ({size:,} bytes)")

if __name__ == "__main__":
    create_report()
