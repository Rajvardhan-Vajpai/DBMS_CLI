import os
from pathlib import Path
import app_sqlite as db


def run_demo():
    db_path = Path(__file__).parent / "dbms.sqlite3"
    if db_path.exists():
        print("Resetting demo database...")
        db_path.unlink()

    print("Initializing database...")
    db.initialize_database()

    print("Creating test users Alice and Bob...")
    alice_id = db.create_user("Alice Demo", "1111", "1234", 0.0)
    bob_id = db.create_user("Bob Demo", "2222", "4321", 0.0)
    print(f"Alice id={alice_id}, Bob id={bob_id}")
    if alice_id is None or bob_id is None:
        print("User creation failed; aborting demo.")
        return

    print("Adding $100 to Alice's wallet...")
    added = db.add_money_to_wallet(alice_id, 100.0)
    print("Add money result:", added)

    alice = db.fetch_user_by_phone("1111")
    bob = db.fetch_user_by_phone("2222")
    print(f"Balances -> Alice: {alice['wallet_balance']}, Bob: {bob['wallet_balance']}")

    print("Attempting a spend of $25 from Alice at 'Amazon'...")
    ok, msg = db.spend_at_merchant(alice_id, 'Amazon', 25.0)
    print("Spend result:", ok, msg)

    print("Transferring $30 from Alice to Bob...")
    ok, msg = db.transfer_money(alice_id, '2222', 30.0)
    print("Transfer result:", ok, msg)

    print("Mini-statement for Alice:")
    rows = db.show_mini_statement(alice_id)
    for r in rows:
        print(r)

    print("Changing Alice PIN to 9999...")
    db.change_pin(alice_id, '9999')

    alice = db.fetch_user_by_phone("1111")
    bob = db.fetch_user_by_phone("2222")
    print(f"Final Balances -> Alice: {alice['wallet_balance']}, Bob: {bob['wallet_balance']}")


if __name__ == '__main__':
    run_demo()
