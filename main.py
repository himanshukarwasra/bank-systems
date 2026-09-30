import json
import random
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("accounts.json")


def load_accounts():
    """Load account data from accounts.json."""
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read account data. Starting with empty data.")
        return {}


def save_accounts(accounts):
    """Save account data to accounts.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(accounts, file, indent=4)


def generate_account_number(accounts):
    """Generate a unique 10-digit account number."""
    while True:
        account_number = str(random.randint(1000000000, 9999999999))
        if account_number not in accounts:
            return account_number


def get_positive_amount(prompt):
    """Read a positive money amount."""
    while True:
        try:
            amount = float(input(prompt))
            if amount <= 0:
                print("Amount must be greater than 0.")
            else:
                return round(amount, 2)
        except ValueError:
            print("Please enter a valid number.")


def add_transaction(account, transaction_type, amount, details=""):
    """Add a transaction with date and time."""
    transaction = {
        "type": transaction_type,
        "amount": round(amount, 2),
        "details": details,
        "date_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    }
    account["transactions"].append(transaction)


def create_account(accounts):
    print("\n========== CREATE ACCOUNT ==========")

    name = input("Enter your name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    phone = input("Enter phone number: ").strip()
    if not phone:
        print("Phone number cannot be empty.")
        return

    while True:
        pin = input("Create a 4-digit PIN: ").strip()
        if pin.isdigit() and len(pin) == 4:
            confirm_pin = input("Confirm PIN: ").strip()
            if pin == confirm_pin:
                break
            print("PINs do not match.")
        else:
            print("PIN must contain exactly 4 digits.")

    account_number = generate_account_number(accounts)

    accounts[account_number] = {
        "name": name,
        "phone": phone,
        "pin": pin,
        "balance": 0.0,
        "transactions": []
    }

    save_accounts(accounts)

    print("\nAccount created successfully!")
    print(f"Your Account Number is: {account_number}")
    print("Keep your account number and PIN safe.")


def login(accounts):
    print("\n=============== LOGIN ===============")

    account_number = input("Enter account number: ").strip()
    pin = input("Enter PIN: ").strip()

    account = accounts.get(account_number)

    if account and account["pin"] == pin:
        print(f"\nLogin successful. Welcome, {account['name']}!")
        return account_number

    print("Invalid account number or PIN.")
    return None


def check_balance(account):
    print("\n========== ACCOUNT BALANCE ==========")
    print(f"Account Holder : {account['name']}")
    print(f"Balance       : ₹{account['balance']:.2f}")


def deposit(account, accounts):
    print("\n============== DEPOSIT ==============")
    amount = get_positive_amount("Enter amount to deposit: ₹")

    account["balance"] += amount
    add_transaction(account, "Deposit", amount, "Money deposited")
    save_accounts(accounts)

    print(f"₹{amount:.2f} deposited successfully.")
    print(f"New balance: ₹{account['balance']:.2f}")


def withdraw(account, accounts):
    print("\n============= WITHDRAW ==============")
    amount = get_positive_amount("Enter amount to withdraw: ₹")

    if amount > account["balance"]:
        print("Insufficient balance.")
        return

    account["balance"] -= amount
    add_transaction(account, "Withdrawal", amount, "Money withdrawn")
    save_accounts(accounts)

    print(f"₹{amount:.2f} withdrawn successfully.")
    print(f"New balance: ₹{account['balance']:.2f}")


def transfer(account_number, account, accounts):
    print("\n============= TRANSFER =============")

    receiver_number = input("Enter receiver account number: ").strip()

    if receiver_number == account_number:
        print("You cannot transfer money to your own account.")
        return

    if receiver_number not in accounts:
        print("Receiver account not found.")
        return

    amount = get_positive_amount("Enter amount to transfer: ₹")

    if amount > account["balance"]:
        print("Insufficient balance.")
        return

    receiver = accounts[receiver_number]

    account["balance"] -= amount
    receiver["balance"] += amount

    add_transaction(
        account,
        "Transfer",
        amount,
        f"Transferred to account {receiver_number}"
    )

    add_transaction(
        receiver,
        "Received",
        amount,
        f"Received from account {account_number}"
    )

    save_accounts(accounts)

    print(f"₹{amount:.2f} transferred successfully.")
    print(f"New balance: ₹{account['balance']:.2f}")


def transaction_history(account):
    print("\n========== TRANSACTION HISTORY ==========")

    transactions = account["transactions"]

    if not transactions:
        print("No transactions found.")
        return

    for index, transaction in enumerate(transactions, start=1):
        print(f"\nTransaction #{index}")
        print(f"Date & Time : {transaction['date_time']}")
        print(f"Type       : {transaction['type']}")
        print(f"Amount     : ₹{transaction['amount']:.2f}")
        print(f"Details    : {transaction['details']}")


def change_pin(account, accounts):
    print("\n============== CHANGE PIN ==============")

    old_pin = input("Enter old PIN: ").strip()

    if old_pin != account["pin"]:
        print("Incorrect old PIN.")
        return

    while True:
        new_pin = input("Enter new 4-digit PIN: ").strip()

        if not new_pin.isdigit() or len(new_pin) != 4:
            print("PIN must contain exactly 4 digits.")
            continue

        confirm_pin = input("Confirm new PIN: ").strip()

        if new_pin != confirm_pin:
            print("PINs do not match.")
            continue

        if new_pin == old_pin:
            print("New PIN must be different from the old PIN.")
            continue

        break

    account["pin"] = new_pin
    save_accounts(accounts)

    print("PIN changed successfully.")


def account_menu(account_number, accounts):
    while True:
        account = accounts[account_number]

        print("\n========================================")
        print("              ACCOUNT MENU")
        print("========================================")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Transfer")
        print("5. Transaction History")
        print("6. Change PIN")
        print("7. Logout")
        print("========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            check_balance(account)
        elif choice == "2":
            deposit(account, accounts)
        elif choice == "3":
            withdraw(account, accounts)
        elif choice == "4":
            transfer(account_number, account, accounts)
        elif choice == "5":
            transaction_history(account)
        elif choice == "6":
            change_pin(account, accounts)
        elif choice == "7":
            print("Logged out successfully.")
            break
        else:
            print("Invalid choice. Please select 1-7.")


def main():
    accounts = load_accounts()

    while True:
        print("\n========================================")
        print("          BANKING MANAGEMENT SYSTEM")
        print("========================================")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        print("========================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_account(accounts)
        elif choice == "2":
            account_number = login(accounts)
            if account_number:
                account_menu(account_number, accounts)
        elif choice == "3":
            print("Thank you for using the Banking Management System.")
            break
        else:
            print("Invalid choice. Please select 1-3.")


if __name__ == "__main__":
    main()
