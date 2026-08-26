# 🔐 Hash Identifier Tool

A full interactive web-based tool built with **Python (Flask)** that takes any
hash string as input and identifies which hashing algorithm(s) likely
generated it (MD5, SHA-1, SHA-256, SHA-512, bcrypt, and more).

**Author:** Kinza
**GitHub:** https://github.com/kinza099
**Email:** kinzapython@gmail.com

## Features
- Interactive GUI (no page reloads — AJAX powered)
- Dark mode (default) and Light mode toggle
- Detects 20+ hash types by length, character set, and known prefixes
  (e.g. `$2b$` for bcrypt, `$6$` for SHA-512 crypt)
- Dedicated Author page
- Fully responsive design

## Project Structure
```
hash_identifier/
├── app.py                  # Flask backend + hash detection logic
├── requirements.txt
├── templates/
│   ├── base.html           # Shared layout (navbar, footer, theme toggle)
│   ├── index.html          # Main tool page
│   └── author.html         # Author info page
└── static/
    ├── css/style.css       # Dark/Light theme styling
    └── js/
        ├── script.js       # Theme toggle logic
        └── hash_tool.js    # Hash identification frontend logic
```

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```
   > ⚠️ Use `127.0.0.1` or `localhost` (not a network/LAN IP like `192.168.x.x`) —
   > the 📋 clipboard-paste button only works in a browser "secure context"
   > (HTTPS or localhost). On a LAN IP or in Firefox (which disables clipboard
   > read by default), the button will show a message asking you to paste
   > manually with **Ctrl+V**, which always works regardless of browser.

## How It Works
The tool checks your input hash against a set of pattern rules based on:
- **Length** (e.g. 32 hex chars → MD5/NTLM, 64 hex chars → SHA-256)
- **Character set** (hex vs base64 vs custom)
- **Known prefixes** (e.g. `$2a$`/`$2b$`/`$2y$` → bcrypt, `*` + 40 hex → MySQL5)

Since many hash algorithms produce output of the same length (e.g. MD5 and
NTLM are both 32 hex characters), the tool may show multiple possible
matches — this is expected and normal for pattern-based identification.

---
Made with ❤️ by Kinza
