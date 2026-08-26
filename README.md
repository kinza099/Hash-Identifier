# 🔐 Hash Identifier Tool

A lightweight, interactive web app built with **Python (Flask)** that takes any hash string as input and identifies which hashing algorithm(s) most likely generated it — no page reloads, dark mode by default, and support for 20+ hash types.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## ✨ Features

- ⚡ **Interactive GUI** — AJAX powered, no page reloads
- 🌗 **Dark mode (default) / Light mode** toggle
- 🔍 **Detects 20+ hash types** by length, character set, and known prefix patterns (e.g. `$2b$` for bcrypt, `$argon2id$` for Argon2)
- 📊 **Confidence indicator** for each match (high vs. shared/ambiguous length)
- 🕘 **Recent lookups** history panel with quick copy-to-clipboard
- 📋 **One-click clipboard paste & copy**
- 👤 Dedicated **Author** page
- 📱 Fully **responsive** design

## 🧬 Supported Hash Types

| Category | Types |
|---|---|
| Hex digest (length-based) | MD5, MD4, NTLM, SHA-1, RIPEMD-160, SHA-224, SHA-256, SHA-384, SHA-512, SHA3-224, SHA3-256, SHA3-384, SHA3-512 |
| Password hashing / KDF | bcrypt, scrypt, Argon2 (`argon2i`, `argon2id`, `argon2d`) |
| System / directory hashes | Cisco Type 5 (MD5-crypt), MySQL 4.1+ (SHA1-based), LDAP `{SHA}`, LDAP `{SSHA}` |

> Many algorithms share the same output length (e.g. MD5 and NTLM are both 32 hex characters), so the tool may return multiple possible matches — this is expected, normal behavior for pattern-based identification.

## 📁 Project Structure

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

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/kinza099/hash-identifier-tool.git
cd hash-identifier-tool

# 2. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Then open your browser at:

```
http://127.0.0.1:5000
```


## 🧠 How It Works

The tool checks the input hash against a set of pattern rules based on:

1. **Length** — e.g. 32 hex chars → MD5/MD4/NTLM, 64 hex chars → SHA-256/SHA3-256
2. **Character set** — hex vs. Base64 vs. custom alphabets
3. **Known prefixes** — e.g. `$2a$` / `$2b$` / `$2y$` → bcrypt, `*` + 40 hex → MySQL 4.1+, `$argon2id$` → Argon2

Each match is tagged with a confidence level:
- **High** — a unique/near-unique prefix or format (e.g. bcrypt, Argon2, Cisco Type 5)
- **Medium** — shared with other algorithms that produce the same output length

## 🔌 API Reference

The frontend talks to a small JSON API that can also be used directly.

**`POST /api/identify`**

Request body:
```json
{ "hash": "5f4dcc3b5aa765d61d8327deb882cf99" }
```

Response:
```json
{
  "input": "5f4dcc3b5aa765d61d8327deb882cf99",
  "length": 32,
  "is_hex": true,
  "valid": true,
  "match_count": 1,
  "matches": [
    {
      "types": ["MD5", "MD4", "NTLM"],
      "note": "32 hex characters",
      "confidence": "medium"
    }
  ]
}
```

## 🖼 Screenshots
> <img width="947" height="410" alt="image" src="https://github.com/user-attachments/assets/313b105a-381a-47c6-9d12-94e7b42f7997" />
> <img width="950" height="411" alt="image" src="https://github.com/user-attachments/assets/2cd1dc80-3874-4fb5-8626-58d163a5ef38" />



## 👤 Author

**Kinza**
- GitHub: [@kinza099](https://github.com/kinza099)

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

Made with ❤️ using Flask
