# IMPORTS AND SETUP
import json
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# DATA FILE SETUP
def get_data_file():
    """Create or select JSON file for the current month."""
    today = datetime.today()
    file_name = f"transactions_{today.strftime('%Y_%m')}.json"
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump({"transactions": [], "archived": []}, f, indent=4)
    return file_name

DATA_FILE = get_data_file()

# DATA HANDLING
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def archive_old_transactions():
    """Archive transactions from previous months."""
    files = [f for f in os.listdir() if f.startswith("transactions_") and f.endswith(".json")]
    for file in files:
        if file != DATA_FILE:
            with open(file, "r") as f:
                data = json.load(f)
            archived_file = f"archived_{file}"
            if os.path.exists(archived_file):
                with open(archived_file, "r") as f:
                    archived_data = json.load(f)
                archived_data["archived"].extend(data["transactions"])
            else:
                archived_data = {"archived": data["transactions"]}
            with open(archived_file, "w") as f:
                json.dump(archived_data, f, indent=4)
            os.remove(file)

archive_old_transactions()

# TRANSACTION NUMBER GENERATOR
def generate_transaction_number():
    today = datetime.today()
    today_str = today.strftime("%m%d%y")
    data = load_data()
    today_txns = [t for t in data["transactions"] if t["transaction_number"].startswith(today_str)]
    increment = len(today_txns) + 1
    return f"{today_str}{increment:02d}"

# FEE CALCULATION
def calculate_fee(document_type):
    fees = {
        "Certificate of Indigency": 0,
        "Cedula": 50,
        "Barangay Clearance": 40,
        "Certificate of Good Conduct": 0
    }
    return fees.get(document_type, 0)

# DASHBOARD
def show_dashboard():
    data = load_data()
    total = len(data["transactions"])
    pending = sum(1 for t in data["transactions"] if t["status"] == "Pending")
    completed = sum(1 for t in data["transactions"] if t["status"] == "Completed")

    print(Fore.CYAN + "\n===================================================")
    print("Good day! Welcome to Barangay San Pascual Document Request Dashboard.")
    print("You may request barangay issued documents accordingly!")
    print("===================================================")
    print(f"Total Requests Submitted: {total}")
    print(f"Pending Requests: {pending}")
    print(f"Completed Requests: {completed}")
    print("===================================================\n")

# DOCUMENT REQUEST
def select_address():
    print("\nChoose Address:")
    house = input("Enter House Number: ")
    streets = ["San Bartolome St.", "Sta. Cruz", "Nazareno", "San Juan", "Sto. Nino", "Delarosa"]
    for i, s in enumerate(streets, 1):
        print(f"{i}. {s}")
    while True:
        choice = input("Select your street (1-6): ")
        if choice.isdigit() and 1 <= int(choice) <= len(streets):
            street = streets[int(choice) - 1]
            break
        print("Invalid selection.")
    return f"{house} {street} San Pascual Obando Bulacan"

def new_transaction():
    data = load_data()
    transaction_number = generate_transaction_number()
    documents = []

    while True:
        print("\nPlease select the document you want to request:")
        print("1. Certificate of Indigency (Earning ₱20,000 below)-FREE")
        print("2. Cedula -₱50")
        print("3. Barangay Clearance -₱40")
        print("4. Certificate of Good Conduct -FREE")

        choice = input("Enter your choice (1-4): ")
        doc_types = {
            "1": "Certificate of Indigency",
            "2": "Cedula",
            "3": "Barangay Clearance",
            "4": "Certificate of Good Conduct"
        }
        document_type = doc_types.get(choice)
        if not document_type:
            print(Fore.RED + "Invalid selection.")
            continue

        print(f"\n--- Enter details for {document_type} ---")
        firstname = input("First Name: ")
        lastname = input("Last Name: ")
        doc = {
            "type": document_type,
            "First Name": firstname,
            "Last Name": lastname,
            "Address": select_address(),
            "Age": input("Age: "),
            "Purpose": input("Purpose: ")
        }

        if document_type in ["Certificate of Indigency", "Cedula"]:
            while True:
                try:
                    income = float(input("Monthly Income: "))
                    if document_type == "Certificate of Indigency" and income > 20000:
                        print(Fore.RED + "\n⚠️ Income exceeds ₱20,000. Cannot request Indigency Certificate.\n")
                        return
                    doc["Monthly Income"] = income
                    break
                except ValueError:
                    print("Invalid input. Enter numeric value.")

        doc["Fee"] = calculate_fee(document_type)
        documents.append(doc)

        another = input("\nRequest another document in same transaction? (y/n): ").lower()
        if another != 'y':
            break

    total_fee = sum(d["Fee"] for d in documents)
    transaction = {
        "transaction_number": transaction_number,
        "documents": documents,
        "total_fee": total_fee,
        "status": "Pending",
        "date_created": datetime.today().date().isoformat()
    }

    data["transactions"].append(transaction)
    save_data(data)

    print(Fore.GREEN + f"\nYour Transaction Number is: {transaction_number}")
    print(f"Total Fee: ₱{total_fee}")
    print("Request successfully recorded!\n")

# VIEW TRANSACTIONS
def view_transactions():
    data = load_data()
    if not data["transactions"]:
        print(Fore.YELLOW + "\nNo transactions available.")
        return

    print("\nView transactions for:")
    print("1. Today")
    print("2. This Month")
    choice = input("Enter choice (1-2): ").strip()

    today = datetime.today().date()
    if choice == "1":
        filtered = [t for t in data["transactions"] if t["date_created"] == today.isoformat()]
        header = f"--- Transactions for Today ({today.isoformat()}) ---"
    elif choice == "2":
        current_month = today.month
        current_year = today.year
        filtered = [t for t in data["transactions"]
                    if datetime.fromisoformat(t["date_created"]).month == current_month
                    and datetime.fromisoformat(t["date_created"]).year == current_year]
        header = f"--- Transactions for {today.strftime('%B %Y')} ---"
    else:
        print(Fore.RED + "Invalid choice.")
        return

    if not filtered:
        print(Fore.YELLOW + "No transactions found for the selected period.")
        return

    print(Fore.CYAN + f"\n{header}")
    for t in filtered:
        status_color = Fore.GREEN if t['status'] == "Completed" else Fore.YELLOW
        print(f"Transaction #: {t['transaction_number']} | Status: {status_color}{t['status']}{Fore.CYAN} | Total Fee: ₱{t['total_fee']}")
        for i, doc in enumerate(t["documents"], 1):
            print(f"  Document {i}: {doc['type']}")
            for k, v in doc.items():
                if k != "type":
                    print(f"    {k}: {v}")
    print("-----------------------------")

# SEARCH, UPDATE, MARK COMPLETE (COMBINED)
def manage_transaction():
    data = load_data()
    print("\nSearch Transaction by:")
    print("1. Transaction Number")
    print("2. Status")
    print("3. Date Created")
    choice = input("Enter choice (1-3): ").strip()

    if choice == "1":
        txn_num = input("Enter Transaction Number: ").strip()
        filtered = [t for t in data["transactions"] if t["transaction_number"] == txn_num]
    elif choice == "2":
        print("Statuses: Pending, Completed")
        status = input("Enter Status: ").capitalize()
        filtered = [t for t in data["transactions"] if t["status"] == status]
    elif choice == "3":
        date_str = input("Enter Date (YYYY-MM-DD): ").strip()
        filtered = [t for t in data["transactions"] if t["date_created"] == date_str]
    else:
        print(Fore.RED + "Invalid choice.")
        return

    if not filtered:
        print(Fore.YELLOW + "No matching transactions found.")
        return

    # Display results
    for t in filtered:
        print(Fore.CYAN + f"\nTransaction #: {t['transaction_number']} | Status: {t['status']} | Total Fee: ₱{t['total_fee']}")
        for i, doc in enumerate(t["documents"], 1):
            print(f"  Document {i}: {doc['type']}")
            for k, v in doc.items():
                if k != "type":
                    print(f"    {k}: {v}")

    # Determine transaction to manage
    if len(filtered) == 1:
        transaction = filtered[0]  # skip asking txn number
    else:
        txn_num = input("\nEnter Transaction Number to manage: ").strip()
        transaction = next((t for t in data["transactions"] if t["transaction_number"] == txn_num), None)
        if not transaction:
            print(Fore.RED + "Transaction not found.")
            return

    # Update or mark complete
    print("\n1. Update Transaction")
    print("2. Mark as Complete")
    action = input("Choose action (1-2): ").strip()

    if action == "1":
        print("\nWhich document to update?")
        for i, doc in enumerate(transaction["documents"], 1):
            print(f"{i}. {doc['type']}")
        doc_choice = input("Enter document number: ")
        if not doc_choice.isdigit() or int(doc_choice) not in range(1, len(transaction["documents"]) + 1):
            print(Fore.RED + "Invalid selection.")
            return
        doc = transaction["documents"][int(doc_choice) - 1]
        # Allow changing document type
        print("\nSelect new document type:")
        doc_types = ["Certificate of Indigency", "Cedula", "Barangay Clearance", "Certificate of Good Conduct"]
        for i, d in enumerate(doc_types, 1):
            print(f"{i}. {d}")
        new_type_choice = input("Enter choice: ")
        if new_type_choice.isdigit() and 1 <= int(new_type_choice) <= 4:
            doc["type"] = doc_types[int(new_type_choice) - 1]
            doc["Fee"] = calculate_fee(doc["type"])
        for field in doc.keys():
            if field not in ["type", "Fee"]:
                new_val = input(f"Enter new {field} (leave blank to keep '{doc[field]}'): ")
                if new_val.strip():
                    doc[field] = new_val
        transaction["total_fee"] = sum(d["Fee"] for d in transaction["documents"])
        save_data(data)
        print(Fore.GREEN + "Transaction updated successfully.")
    elif action == "2":
        transaction["status"] = "Completed"
        save_data(data)
        print(Fore.GREEN + "Transaction marked as completed successfully.")
    else:
        print(Fore.RED + "Invalid action.")

# MAIN MENU
def main():
    while True:
        show_dashboard()
        print("Menu Options:")
        print("1. New Transaction")
        print("2. View Transactions")
        print("3. Search / Update / Complete Transaction")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            new_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            manage_transaction()
        elif choice == "4":
            print(Fore.CYAN + "\nThank you for using the Barangay San Pascual Document Request System.")
            break
        else:
            print(Fore.RED + "Invalid choice.")

        input(Fore.CYAN + "\nPress Enter to return to the dashboard...")

if __name__ == "__main__":
    main()
