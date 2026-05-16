# Wallet DBMS

This project implements a simple wallet DBMS CLI using SQLite for local development.

Security:
- Do not commit the local database file `dbms.sqlite3`.
- PINs are stored as bcrypt hashes, not plaintext.

Quick start:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the interactive wallet app:

```bash
python frontend.py
```

3. Or run the demo script to create test users and exercise basic flows:

```bash
python demo_run.py
```

Push to GitHub safely:

```bash
git add .gitignore README.md requirements.txt frontend.py app_sqlite.py demo_run.py
git commit -m "Secure wallet app: hash PINs, ignore local secrets, use SQLite backend"
git push origin main
```
