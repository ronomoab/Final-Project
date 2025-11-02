import json
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# ==========================================================
# FILE HANDLING & SETUP
# ==========================================================
ARCHIVE_FILE = "archived_transactions.json"

def get_current_data_file():
    now = datetime.now()
    return f"barangay_data_{now.year}_{now.month:02d}.json"

def load_data():
    data_file = get_current_data_file()
    archive_old_data_files()

    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            json.dump({"transactions": [], "archived": []}, f, indent=4)
    with open(data_file, "r") as f:
        return json.load(f)

def save_data(data):
    with open(get_current_data_file(), "w") as f:
        json.dump(data, f, indent=4)

def archive_old_data_files():
    current_file = get_current_data_file()
    if not os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "w") as f:
            json.dump({"archived": []}, f, indent=4)

    for file in os.listdir():
        if file.startswith("barangay_data_") and file.endswith(".json") and file != current_file:
            with open(file, "r") as f:
                old_data = json.load(f)
            with open(ARCHIVE_FILE, "r") as af:
                archive = json.load(af)

            archive["archived"].extend(old_data.get("transactions", []))
            with open(ARCHIVE_FILE, "w") as af:
                json.dump(archive, af, indent=4)

            os.remove(file)

# ==========================================================
# UTILITIES
# ==========================================================
def generate_transaction_number():
    today = datetime.now().strftime("%m%d%y")
    data = load_data()
    existing_today = [t for t in data["transactions"] if t["transaction_number"].startswith(today)]
    next_num = len(existing_today) + 1
    return f"{today}-{next_num:02d}"

def calculate_fee(document_type):
    fees = {
        "Certificate of Indigency": 0,
        "Cedula": 50,
        "Barangay Clearance": 40,
        "Certificate of Good Conduct": 0
    }
    return fees.get(document_type, 0)

def get_address():
    print(Fore.CYAN + "\nEnter your address details:")
    house_number = input(Fore.WHITE + "Enter House Number: ").strip()
    print("\nChoose your street:")
    streets = ["San Bartolome St.", "Sta. Cruz", "Nazareno", "San Juan", "Sto. Nino", "Delarosa"]

    for i, st in enumerate(streets, 1):
        print(f"{i}. {st}")
    while True:
        choice = input(Fore.WHITE + "Enter your choice (1-6): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= 6:
            street = streets[int(choice) - 1]
            break
        else:
            print(Fore.RED + "Invalid choice. Please select a valid street number.")
    return f"{house_number} {street}, San Pascual, Obando, Bulacan"

# ==========================================================
# DASHBOARD
# ==========================================================
def show_dashboard():
    data = load_data()
    total = len(data["transactions"])
    pending = sum(1 for t in data["transactions"] if t["status"] == "Pending")
    completed = sum(1 for t in data["transactions"] if t["status"] == "Completed")

    print(Fore.CYAN + "\n===================================================")
    print("Barangay San Pascual Document Request Dashboard")
    print("===================================================")
    print(Fore.WHITE + f"Total Requests: {total}")
    print(Fore.YELLOW + f"Pending Requests: {pending}")
    print(Fore.GREEN + f"Completed Requests: {completed}")
    print(Fore.CYAN + "===================================================\n")

# ==========================================================
# CORE FUNCTIONS
# ==========================================================
def new_transaction():
    data = load_data()
    transaction_number = generate_transaction_number()
    documents = []

    while True:
        print(Fore.CYAN + "\nSelect document to request:")
        print("1. Certificate of Indigency (₱20,000 below) - FREE")
        print("2. Cedula - ₱50")
        print("3. Barangay Clearance - ₱40")
        print("4. Certificate of Good Conduct - FREE")

        choice = input(Fore.WHITE + "Enter your choice (1-4): ").strip()
        doc_types = {
            "1": "Certificate of Indigency",
            "2": "Cedula",
            "3": "Barangay Clearance",
            "4": "Certificate of Good Conduct"
        }
        document_type = doc_types.get(choice)
        if not document_type:
            print(Fore.RED + "Invalid choice. Try again.")
            continue

        print(Fore.CYAN + f"\n--- Enter details for {document_type} ---")
        first_name = input(Fore.WHITE + "First Name: ").strip()
        last_name = input(Fore.WHITE + "Last Name: ").strip()
        home_address = get_address()
        age = input("Age: ").strip()
        purpose = input("Purpose: ").strip()

        doc = {
            "type": document_type,
            "First Name": first_name,
            "Last Name": last_name,
            "Home Address": home_address,
            "Age": age,
            "Purpose": purpose
        }

        if document_type in ["Certificate of Indigency", "Cedula"]:
            while True:
                try:
                    income = float(input(Fore.WHITE + "Monthly Income: "))
                    if document_type == "Certificate of Indigency" and income > 20000:
                        print(Fore.RED + "❌ You are not qualified for Certificate of Indigency.")
                        return
                    doc["Monthly Income"] = income
                    break
                except ValueError:
                    print(Fore.RED + "Please enter a valid number.")

        doc["Fee"] = calculate_fee(document_type)
        documents.append(doc)

        if input(Fore.WHITE + "Request another document? (y/n): ").lower() != 'y':
            break

    transaction = {
        "transaction_number": transaction_number,
        "documents": documents,
        "total_fee": sum(d["Fee"] for d in documents),
        "status": "Pending",
        "date_created": datetime.now().strftime("%Y-%m-%d")
    }

    data["transactions"].append(transaction)
    save_data(data)

    print(Fore.GREEN + "\n========================================")
    print(f"Transaction #: {transaction_number}")
    print(f"Total Fee: ₱{transaction['total_fee']}")
    print("Your request has been successfully recorded!")
    print("========================================\n")

# ==========================================================
# VIEWING
# ==========================================================
def view_today_transactions():
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    today_txns = [t for t in data["transactions"] if t["date_created"] == today]

    print(Fore.CYAN + "\n--- Today's Transactions ---")
    if not today_txns:
        print(Fore.YELLOW + "No transactions for today.")
        return
    for t in today_txns:
        print(f"{t['transaction_number']} | {t['status']} | ₱{t['total_fee']}")
    print(Fore.CYAN + "-----------------------------")

def view_monthly_transactions():
    data = load_data()
    print(Fore.CYAN + "\n--- Transactions for This Month ---")
    if not data["transactions"]:
        print(Fore.YELLOW + "No transactions this month.")
        return
    for t in data["transactions"]:
        print(f"{t['transaction_number']} | Date: {t['date_created']} | Status: {t['status']} | ₱{t['total_fee']}")
    print(Fore.CYAN + "-----------------------------")

# ==========================================================
# SEARCH / UPDATE / COMPLETE
# ==========================================================
def search_update_transaction():
    data = load_data()

    print(Fore.CYAN + "\nSearch by:")
    print("1. Transaction Number")
    print("2. Date Created")
    print("3. Status")
    choice = input(Fore.WHITE + "Enter choice (1-3): ").strip()

    found = None
    if choice == "1":
        txn_num = input("Enter Transaction Number: ").strip()
        found = next((t for t in data["transactions"] if t["transaction_number"] == txn_num), None)
    elif choice == "2":
        date = input("Enter Date (YYYY-MM-DD): ").strip()
        results = [t for t in data["transactions"] if t["date_created"] == date]
        found = results[0] if results else None
    elif choice == "3":
        status = input("Enter Status (Pending/Completed): ").strip().capitalize()
        results = [t for t in data["transactions"] if t["status"] == status]
        found = results[0] if results else None
    else:
        print(Fore.RED + "Invalid choice.")
        return

    if not found:
        print(Fore.RED + "Transaction not found.")
        return

    print(Fore.CYAN + f"\nTransaction #: {found['transaction_number']} | Status: {found['status']} | ₱{found['total_fee']}")
    for i, doc in enumerate(found["documents"], 1):
        print(f"\nDocument {i}: {doc['type']}")
        print(f"  Name: {doc.get('First Name', '')} {doc.get('Last Name', '')}")
        for k, v in doc.items():
            if k not in ["type", "First Name", "Last Name"]:
                print(f"  {k}: {v}")

    print(Fore.CYAN + "\n1. Update Transaction\n2. Mark as Completed\n3. Cancel")
    action = input(Fore.WHITE + "Choose action (1-3): ").strip()

    if action == "1":
        for doc in found["documents"]:
            print(Fore.CYAN + "\n--- Update Document Details ---")

            # ✅ Allow changing document type
            print(Fore.WHITE + "Change Document Type?")
            print("1. Certificate of Indigency")
            print("2. Cedula")
            print("3. Barangay Clearance")
            print("4. Certificate of Good Conduct")
            change_doc = input("Enter new type (1-4) or press Enter to keep current: ").strip()
            doc_types = {
                "1": "Certificate of Indigency",
                "2": "Cedula",
                "3": "Barangay Clearance",
                "4": "Certificate of Good Conduct"
            }
            if change_doc in doc_types:
                doc["type"] = doc_types[change_doc]
                doc["Fee"] = calculate_fee(doc["type"])

            # Update name, purpose, address
            for field in ["First Name", "Last Name", "Purpose"]:
                new_val = input(f"Enter new {field} (leave blank to keep '{doc[field]}'): ").strip()
                if new_val:
                    doc[field] = new_val

            update_address = input("Change address? (y/n): ").lower()
            if update_address == 'y':
                doc["Home Address"] = get_address()

        found["total_fee"] = sum(d["Fee"] for d in found["documents"])
        save_data(data)
        print(Fore.GREEN + "Transaction updated successfully!")

    elif action == "2":
        found["status"] = "Completed"
        save_data(data)
        print(Fore.GREEN + "Transaction marked as completed.")
    else:
        print(Fore.YELLOW + "Cancelled.")

# ==========================================================
# MAIN MENU
# ==========================================================
def main():
    while True:
        show_dashboard()
        print(Fore.CYAN + "Menu Options:")
        print("1. New Transaction")
        print("2. View Today's Transactions")
        print("3. View Monthly Transactions")
        print("4. Search / Update / Complete Transaction")
        print("5. Exit")

        choice = input(Fore.WHITE + "Enter your choice: ").strip()

        if choice == "1":
            new_transaction()
        elif choice == "2":
            view_today_transactions()
        elif choice == "3":
            view_monthly_transactions()
        elif choice == "4":
            search_update_transaction()
        elif choice == "5":
            print(Fore.GREEN + "\nThank you for using the Barangay San Pascual Document Request System.")
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")

        input(Fore.WHITE + "\nPress ENTER to return to the dashboard...")

# ==========================================================
# ENTRY POINT
# ==========================================================
if __name__ == "__main__":
    main()
