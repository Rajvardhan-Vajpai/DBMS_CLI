# 💰 Wallet DBMS CLI

A command-line wallet management system built with Python and SQLite.
Features secure PIN authentication using bcrypt hashing.

## ✨ Features
- Create and manage user wallets via CLI
- Secure PIN storage using bcrypt hashing (no plaintext!)
- SQLite local database backend
- Demo script to test basic flows
- Interactive terminal interface

## 🛠 Tech Stack
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat&logo=sqlite&logoColor=white)

## 🚀 Quick Start

1. Clone the repo:
```bash
git clone https://github.com/Rajvardhan-Vajpai/DBMS_CLI.git
cd DBMS_CLI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the interactive wallet app:
```bash
python frontend.py
```

4. Or run the demo script:
```bash
python demo_run.py
```

## 🔐 Security
- PINs are stored as bcrypt hashes, never plaintext
- Local database file `dbms.sqlite3` is gitignored

## 📁 Project Structure

| File | Description |
|------|-------------|
| `frontend.py` | Interactive CLI interface |
| `app_sqlite.py` | SQLite database logic |
| `demo_run.py` | Demo script with test users |
| `requirements.txt` | Dependencies |
| `.gitignore` | Git ignore rules |

## 👨‍💻 Author
**Rajvardhan Vajpai** — [GitHub](https://github.com/Rajvardhan-Vajpai)
