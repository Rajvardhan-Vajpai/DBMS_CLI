import app_sqlite as db
from decimal import Decimal
from datetime import datetime

# --- STYLING CONSTANTS ---
G = '\033[92m'  # GREEN
R = '\033[91m'  # RED
B = '\033[94m'  # BLUE
C = '\033[96m'  # CYAN
Y = '\033[93m'  # YELLOW/GOLD
RE = '\033[0m'  # RESET
BOLD = '\033[1m'

# Using SQLite backend (app_sqlite.py)
DB_CONFIG = None

# --- DATABASE CONNECTION (SQLite via app_sqlite) ---

def get_db_connection():
    # kept for compatibility; SQLite functions are used directly via `db` module
    return None


def initialize_database():
    try:
        return db.initialize_database()
    except Exception as e:
        print(f"{R}Failed to initialize database: {e}{RE}")
        return False

# --- ACCOUNT HELPERS ---

def fetch_user_by_phone(phone):
    return db.fetch_user_by_phone(phone)


def create_user(full_name, phone, pin, initial_balance=0.0):
    return db.create_user(full_name, phone, pin, initial_balance)


def add_money_to_wallet(user_id, amount):
    return db.add_money_to_wallet(user_id, amount)


def spend_at_merchant(user_id, merchant_name, amount):
    ok, msg = db.spend_at_merchant(user_id, merchant_name, amount)
    if ok:
        return f"{G}✔ {msg}{RE}"
    return f"{R}{msg}{RE}"


def transfer_money(sender_id, receiver_phone, amount):
    ok, msg = db.transfer_money(sender_id, receiver_phone, amount)
    if ok:
        return f"{G}✔ {msg}{RE}"
    return f"{R}{msg}{RE}"


def show_mini_statement(user_id):
    rows = db.show_mini_statement(user_id)
    print(f"\n{BOLD}RECENT TRANSACTIONS{RE}")
    print(Y + "┌" + "─"*20 + "┬" + "─"*15 + "┬" + "─"*12 + "┐" + RE)
    print(f"│ {'DATE':<18} │ {'TYPE':<13} │ {'AMOUNT':>10} │")
    print(Y + "├" + "─"*20 + "┼" + "─"*15 + "┼" + "─"*12 + "┤" + RE)
    for t in rows:
        color = R if 'OUT' in t['txn_type'] or 'SPEND' in t['txn_type'] else G
        # txn_time is stored as text; try parsing
        try:
            dt = datetime.fromisoformat(t['txn_time'])
            date_s = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            date_s = t['txn_time']
        print(f"│ {date_s:<18} │ {color}{t['txn_type']:<13}{RE} │ {color}{t['amount']:>10.2f}{RE} │")
    print(Y + "└" + "─"*20 + "┴" + "─"*15 + "┴" + "─"*12 + "┘" + RE)


def change_pin(user_id):
    print(Y + BOLD + "\n=== CHANGE PIN ===" + RE)
    while True:
        new_pin = input("Enter new 4-digit PIN: ").strip()
        confirm_pin = input("Confirm new PIN: ").strip()
        if new_pin != confirm_pin:
            print(f"{R}PINs do not match. Try again.{RE}")
            continue
        if len(new_pin) != 4 or not new_pin.isdigit():
            print(f"{R}PIN must be exactly 4 digits.{RE}")
            continue
        break

    db.change_pin(user_id, new_pin)
    print(f"{G}PIN updated successfully.{RE}")


def show_account_info(user):
    print(Y + BOLD + "\n=== ACCOUNT INFORMATION ===" + RE)
    print(f"Name       : {user['full_name']}")
    print(f"Phone      : {user['phone']}")
    print(f"Status     : {user['status']}")
    print(f"Balance    : {G}${float(user['wallet_balance']):,.2f}{RE}")


def login_user():
    print(Y + BOLD + "\n=== LOGIN ===" + RE)
    phone = input("Phone: ")
    user = fetch_user_by_phone(phone)
    if not user:
        print(f"{R}Account not found.{RE}")
        return None
    if user['status'] == 'BLOCKED':
        print(f"{R}Account is blocked. Contact support.{RE}")
        return None

    for attempt in range(3):
        pin = input("Enter 4-digit PIN: ")
        verified = db.verify_pin(phone, pin)
        if verified:
            return verified
        print(f"{R}Incorrect PIN ({attempt + 1}/3).{RE}")

    # block user after too many attempts
    db.block_user(user['user_id'])
    print(f"{R}Too many failed attempts. Account blocked.{RE}")
    return None


def register_new_user():
    print(Y + BOLD + "\n=== REGISTER NEW ACCOUNT ===" + RE)
    full_name = input("Full Name: ").strip()
    phone = input("Phone Number: ").strip()
    if fetch_user_by_phone(phone):
        print(f"{R}A user with this phone already exists.{RE}")
        return None

    while True:
        pin = input("Create 4-digit PIN: ").strip()
        confirm_pin = input("Confirm PIN: ").strip()
        if pin != confirm_pin:
            print(f"{R}PINs do not match. Try again.{RE}")
            continue
        if len(pin) != 4 or not pin.isdigit():
            print(f"{R}PIN must be exactly 4 digits.{RE}")
            continue
        break

    initial_deposit = 0.0
    deposit_input = input("Initial deposit (optional, press Enter to skip): ").strip()
    if deposit_input:
        try:
            initial_deposit = float(deposit_input)
            if initial_deposit < 0:
                print(f"{R}Initial deposit cannot be negative. Setting to 0.{RE}")
                initial_deposit = 0.0
        except ValueError:
            print(f"{R}Invalid deposit amount. Starting with 0.{RE}")
            initial_deposit = 0.0

    user_id = create_user(full_name, phone, pin, initial_deposit)
    if user_id:
        print(f"{G}Account created successfully!{RE}")
        return fetch_user_by_phone(phone)
    return None


def main():
    print(Y + BOLD + "\n==========================================")
    print("      FULL WALLET DBMS APPLICATION")
    print("==========================================" + RE)

    if initialize_database():
        print(f"{G}Database tables are ready.{RE}")
    else:
        print(f"{R}Database initialization failed. Check the SQLite backend and run again.{RE}")
        return

    user = None
    while not user:
        print(Y + "\n1. Login")
        print("2. Register New Account")
        print("3. Exit" + RE)
        startup_choice = input(f"{BOLD}Choose an option: {RE}")

        if startup_choice == '1':
            user = login_user()
        elif startup_choice == '2':
            user = register_new_user()
            if user:
                print(f"{G}You can now login with your phone and PIN.{RE}")
                user = login_user()
        elif startup_choice == '3':
            print(f"{Y}Goodbye!{RE}")
            return
        else:
            print(f"{R}Please select a valid option.{RE}")

    while True:
        # Refresh the user from the SQLite backend
        user = db.fetch_user_by_phone(user['phone'])

        current_bal = float(user['wallet_balance'])
        print(Y + "\n" + "═"*45 + RE)
        print(f"  {BOLD}Welcome, {C}{user['full_name']}{RE}")
        print(f"  Balance: {G}${current_bal:.2f}{RE}")
        print(Y + "─"*45 + RE)
        print(f"  1. {B}Check Balance{RE}  2. {B}Add Money{RE}")
        print(f"  3. {B}Pay Merchant{RE}   4. {B}Transfer Funds{RE}")
        print(f"  5. {B}Mini Statement{RE}  6. {B}Change PIN{RE}")
        print(f"  7. {B}Account Info{RE} 8. {R}Logout{RE}")
        print(Y + "═"*45 + RE)
        
        choice = input(f"{BOLD}Select Option: {RE}")

        if choice == '1':
            print(f"\n{C}Current Balance: ${current_bal:.2f}{RE}")
        elif choice == '2':
            amount = input("Enter amount to add: ")
            try:
                value = float(amount)
                if value > 0:
                    if add_money_to_wallet(user['user_id'], value):
                        print(f"{G}Money added successfully!{RE}")
                    else:
                        print(f"{R}Unable to add money.{RE}")
                else:
                    print(f"{R}Amount must be greater than 0.{RE}")
            except ValueError:
                print(f"{R}Please enter a valid number.{RE}")
        elif choice == '3':
            merchant = input("Merchant Name: ").strip()
            amount = input("Amount: ")
            try:
                print(spend_at_merchant(user['user_id'], merchant, float(amount)))
            except ValueError:
                print(f"{R}Please enter a valid amount.{RE}")
        elif choice == '4':
            rp = input("Receiver Phone: ")
            a = input("Amount: ")
            try:
                print(transfer_money(user['user_id'], rp, float(a)))
            except ValueError:
                print(f"{R}Please enter a valid amount.{RE}")
        elif choice == '5':
            show_mini_statement(user['user_id'])
        elif choice == '6':
            change_pin(user['user_id'])
        elif choice == '7':
            show_account_info(user)
        elif choice == '8':
            print(f"{Y}Logged out successfully.{RE}")
            break
        else:
            print(f"{R}Please choose a valid option.{RE}")

        input(f"\n{C}Press Enter to continue...{RE}")

if __name__ == "__main__":
    main()
