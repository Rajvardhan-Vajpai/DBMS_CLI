import sqlite3
import os
from decimal import Decimal
from datetime import datetime
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), 'dbms.sqlite3')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        pin TEXT NOT NULL,
        wallet_balance REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS merchants (
        merchant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_name TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS wallet_transactions (
        txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        txn_time TEXT DEFAULT CURRENT_TIMESTAMP,
        txn_type TEXT NOT NULL,
        amount REAL NOT NULL,
        balance_after REAL NOT NULL,
        related_user_id INTEGER,
        remarks TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)

    # seed merchants
    merchants = ['Amazon', 'Flipkart', 'Grocery Store']
    for m in merchants:
        try:
            cur.execute("INSERT INTO merchants (merchant_name, status) VALUES (?, ?)", (m, 'ACTIVE'))
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    return True

def fetch_user_by_phone(phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(full_name, phone, pin, initial_balance=0.0):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # hash the PIN before storing
        hashed = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO users (full_name, phone, pin, wallet_balance, status) VALUES (?, ?, ?, ?, 'ACTIVE')",
                    (full_name, phone, hashed.decode('utf-8'), float(initial_balance)))
        uid = cur.lastrowid
        conn.commit()
        return uid
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()

def add_money_to_wallet(user_id, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT wallet_balance FROM users WHERE user_id = ?", (user_id,))
        bal = cur.fetchone()[0]
        new_bal = float(bal) + float(amount)
        cur.execute("UPDATE users SET wallet_balance = ? WHERE user_id = ?", (new_bal, user_id))
        cur.execute("INSERT INTO wallet_transactions (user_id, txn_type, amount, balance_after, remarks) VALUES (?, 'ADD_MONEY', ?, ?, 'Deposit')",
                    (user_id, float(amount), new_bal))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def spend_at_merchant(user_id, merchant_name, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM merchants WHERE merchant_name = ? AND status = 'ACTIVE'", (merchant_name,))
        if not cur.fetchone():
            return False, 'Merchant not found or inactive.'
        cur.execute("SELECT wallet_balance FROM users WHERE user_id = ?", (user_id,))
        res = cur.fetchone()
        if not res:
            return False, 'User not found.'
        balance = Decimal(str(res[0]))
        amt = Decimal(str(amount))
        if balance < amt:
            return False, 'Insufficient funds.'
        new_bal = float(balance - amt)
        cur.execute("UPDATE users SET wallet_balance = ? WHERE user_id = ?", (new_bal, user_id))
        cur.execute("INSERT INTO wallet_transactions (user_id, txn_type, amount, balance_after, remarks) VALUES (?, 'SPEND', ?, ?, ?)",
                    (user_id, float(amt), new_bal, f'Paid to {merchant_name}'))
        conn.commit()
        return True, 'Payment successful.'
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def transfer_money(sender_id, receiver_phone, amount):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id, wallet_balance, phone FROM users WHERE phone = ?", (receiver_phone,))
        receiver = cur.fetchone()
        if not receiver:
            return False, 'Receiver not found.'
        r_id = receiver[0]
        if r_id == sender_id:
            return False, 'Cannot transfer to yourself.'
        cur.execute("SELECT wallet_balance, phone FROM users WHERE user_id = ?", (sender_id,))
        sender = cur.fetchone()
        s_bal = Decimal(str(sender[0]))
        amt = Decimal(str(amount))
        if s_bal < amt:
            return False, 'Insufficient funds.'
        new_sender = float(s_bal - amt)
        # receiver[1] is wallet_balance in this select ordering; fix receiving balance lookup
        cur.execute("SELECT wallet_balance FROM users WHERE user_id = ?", (r_id,))
        rbal = cur.fetchone()[0]
        new_receiver = float(Decimal(str(rbal)) + amt)
        cur.execute("UPDATE users SET wallet_balance = ? WHERE user_id = ?", (new_sender, sender_id))
        cur.execute("UPDATE users SET wallet_balance = ? WHERE user_id = ?", (new_receiver, r_id))
        cur.execute("INSERT INTO wallet_transactions (user_id, txn_type, amount, balance_after, related_user_id, remarks) VALUES (?, 'TRANSFER_OUT', ?, ?, ?, ?)",
                    (sender_id, float(amt), new_sender, r_id, f'Sent to {receiver_phone}'))
        cur.execute("INSERT INTO wallet_transactions (user_id, txn_type, amount, balance_after, related_user_id, remarks) VALUES (?, 'TRANSFER_IN', ?, ?, ?, ?)",
                    (r_id, float(amt), new_receiver, sender_id, f'Received from {sender[1]}'))
        conn.commit()
        return True, 'Transfer successful.'
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def show_mini_statement(user_id, limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT txn_time, txn_type, amount, remarks FROM wallet_transactions WHERE user_id = ? ORDER BY txn_time DESC LIMIT ?", (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def change_pin(user_id, new_pin):
    conn = get_conn()
    cur = conn.cursor()
    hashed = bcrypt.hashpw(new_pin.encode('utf-8'), bcrypt.gensalt())
    cur.execute("UPDATE users SET pin = ? WHERE user_id = ?", (hashed.decode('utf-8'), user_id))
    conn.commit()
    conn.close()
    return True


def verify_pin(phone, plain_pin):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    hashed = row['pin']
    try:
        if bcrypt.checkpw(plain_pin.encode('utf-8'), hashed.encode('utf-8')):
            return dict(row)
    except Exception:
        return None
    return None


def block_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET status = 'BLOCKED' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    print('Initializing SQLite DB...')
    ok = initialize_database()
    print('Initialized.' if ok else 'Initialization failed')
