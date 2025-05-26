import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from datetime import timedelta
import json
from collections import defaultdict


class FinanceTracker:
    """A class to track personal finances, including income and expenses."""

    def __init__(self, filename="transactions.json"):
        self.transactions = []  # List to store all transactions
        self.predefined_categories = ["Salary", "Groceries", "Furniture", "Rent", "Recreation"]
        self.filename = filename
        self.load_transactions()

    def add_transaction(self, amount, category, date, transaction_type):
        """Adds a new transaction to the tracker."""
        transaction = {
            "amount": amount,
            "category": category,
            "date": date.isoformat(),
            "type": transaction_type,
        }
        self.transactions.append(transaction)
        self.save_transactions()

    def delete_transaction(self, index):
        """Deletes a transaction at a given index."""
        if 0 <= index < len(self.transactions):
            del self.transactions[index]
            self.save_transactions()

    def filter_transactions(self, category, transaction_type, start_date, end_date):
        """Filters transactions by category, type, and date range."""
        filtered = self.transactions

        # Filter by category
        if category == "Other":
            filtered = [t for t in filtered if t["category"] not in self.predefined_categories]
        elif category and category != "All":
            filtered = [t for t in filtered if t["category"] == category]

        # Filter by transaction type
        if transaction_type and transaction_type != "All":
            filtered = [t for t in filtered if t["type"] == transaction_type]

        # Filter by date range
        if start_date:
            filtered = [t for t in filtered if datetime.date.fromisoformat(t["date"]) >= start_date]
        if end_date:
            filtered = [t for t in filtered if datetime.date.fromisoformat(t["date"]) <= end_date]

        return filtered

    def calculate_totals(self, transactions):
        """Calculates the total income and total expenses for the given transactions."""
        total_income = sum(t["amount"] for t in transactions if t["type"] == "Income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "Expense")
        return total_income, total_expense

    def calculate_category_breakdown(self, transactions):
        """Calculates the percentage breakdown for income and expense categories."""
        income_totals = defaultdict(float)
        expense_totals = defaultdict(float)

        # Sum amounts by category
        for t in transactions:
            if t["type"] == "Income":
                income_totals[t["category"]] += t["amount"]
            elif t["type"] == "Expense":
                expense_totals[t["category"]] += t["amount"]

        # Calculate income percentages
        total_income = sum(income_totals.values())
        income_percentages = {
            category: (amount / total_income * 100) if total_income > 0 else 0
            for category, amount in income_totals.items()
        }

        # Calculate expense percentages
        total_expense = sum(expense_totals.values())
        expense_percentages = {
            category: (amount / total_expense * 100) if total_expense > 0 else 0
            for category, amount in expense_totals.items()
        }

        return income_percentages, expense_percentages

    def view_balance(self):
        """Calculates and returns the current balance."""
        income = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
        expenses = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
        return income - expenses

    def save_transactions(self):
        """Saves transactions to a JSON file."""
        with open(self.filename, "w") as file:
            json.dump(self.transactions, file, indent=4)

    def load_transactions(self):
        """Loads transactions from a JSON file."""
        try:
            with open(self.filename, "r") as file:
                self.transactions = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.transactions = []


class FinanceTrackerApp:
    """GUI application for Finance Tracker Pro."""

    def __init__(self, root):
        self.tracker = FinanceTracker()
        self.root = root
        self.root.title("Finance Tracker Pro")

        # Set background color
        self.root.configure(bg="#f0f8ff")

        # Create frames
        self.create_input_frame()
        self.create_filter_frame()
        self.create_output_frame()

        # Display all transactions at start and update balance
        self.show_all_transactions()
        self.update_balance()

    def create_input_frame(self):
        """Creates the input frame for adding transactions."""
        self.input_frame = tk.Frame(self.root, bg="#f0f8ff", pady=10)
        self.input_frame.pack(fill="x")

        tk.Label(self.input_frame, text="Add Transaction", font=("Arial", 14, "bold"), bg="#f0f8ff").grid(
            row=0, column=0, columnspan=4, pady=10
        )

        tk.Label(self.input_frame, text="Amount:", bg="#f0f8ff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = tk.Entry(self.input_frame)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.input_frame, text="Category:", bg="#f0f8ff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar(value="Salary")
        self.category_menu = ttk.Combobox(
            self.input_frame,
            textvariable=self.category_var,
            values=self.tracker.predefined_categories + ["Other"],
            state="readonly",
        )
        self.category_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.category_menu.bind("<<ComboboxSelected>>", self.check_custom_category)

        # Custom category widgets (hidden initially)
        self.custom_category_label = tk.Label(self.input_frame, text="Custom Category:", bg="#f0f8ff")
        self.custom_category_entry = tk.Entry(self.input_frame)

        tk.Label(self.input_frame, text="Date (MM/DD/YYYY):", bg="#f0f8ff").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        self.date_entry = tk.Entry(self.input_frame)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.input_frame, text="Type:", bg="#f0f8ff").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.type_var = tk.StringVar(value="Income")
        self.type_menu = ttk.Combobox(
            self.input_frame, textvariable=self.type_var, values=["Income", "Expense"], state="readonly"
        )
        self.type_menu.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Button(
            self.input_frame,
            text="Add Transaction",
            command=self.add_transaction,
            bg="#87cefa",
            fg="white",
            font=("Arial", 10, "bold"),
        ).grid(row=5, column=0, columnspan=4, pady=10)

    def create_filter_frame(self):
        """Creates the filter frame for filtering transactions."""
        self.filter_frame = tk.Frame(self.root, bg="#f0f8ff", pady=10)
        self.filter_frame.pack(fill="x")

        tk.Label(self.filter_frame, text="Filter Transactions", font=("Arial", 14, "bold"), bg="#f0f8ff").grid(
            row=0, column=0, columnspan=4, pady=10
        )

        tk.Label(self.filter_frame, text="Category:", bg="#f0f8ff").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.filter_category_var = tk.StringVar(value="All")
        self.filter_category_menu = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_category_var,
            values=["All"] + self.tracker.predefined_categories + ["Other"],
            state="readonly",
        )
        self.filter_category_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.filter_frame, text="Type:", bg="#f0f8ff").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.filter_type_var = tk.StringVar(value="All")
        self.filter_type_menu = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_type_var,
            values=["All", "Income", "Expense"],
            state="readonly",
        )
        self.filter_type_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.filter_frame, text="Start Date (MM/DD/YYYY):", bg="#f0f8ff").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        self.start_date_entry = tk.Entry(self.filter_frame)
        self.start_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.filter_frame, text="End Date (MM/DD/YYYY):", bg="#f0f8ff").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        self.end_date_entry = tk.Entry(self.filter_frame)
        self.end_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Button(
            self.filter_frame,
            text="Apply Filter",
            command=self.apply_filter,
            bg="#87cefa",
            fg="white",
            font=("Arial", 10, "bold"),
        ).grid(row=5, column=0, columnspan=2, pady=10)

        tk.Button(
            self.filter_frame,
            text="Show All Transactions",
            command=self.show_all_transactions,
            bg="#87cefa",
            fg="white",
            font=("Arial", 10, "bold"),
        ).grid(row=5, column=2, columnspan=2, pady=10)

    def create_output_frame(self):
        """Creates the output frame for displaying transactions and summaries."""
        self.output_frame = tk.Frame(self.root, bg="#f0f8ff", pady=10)
        self.output_frame.pack(fill="both", expand=True)

        self.balance_label = tk.Label(
            self.output_frame, text="Current Balance: $0.00", font=("Arial", 14, "bold"), bg="#f0f8ff"
        )
        self.balance_label.pack()

        self.transaction_list = ttk.Treeview(
            self.output_frame, columns=("Amount", "Category", "Date", "Type"), show="headings", height=10
        )
        self.transaction_list.heading("Amount", text="Amount")
        self.transaction_list.heading("Category", text="Category")
        self.transaction_list.heading("Date", text="Date")
        self.transaction_list.heading("Type", text="Type")
        self.transaction_list.pack(fill="both", expand=True, padx=10, pady=10)

        self.total_income_label = tk.Label(
            self.output_frame, text="Income over Selected Period: $0.00", font=("Arial", 12), bg="#f0f8ff"
        )
        self.total_income_label.pack()

        self.total_expense_label = tk.Label(
            self.output_frame, text="Expenses over Selected Period: $0.00", font=("Arial", 12), bg="#f0f8ff"
        )
        self.total_expense_label.pack()

        button_frame = tk.Frame(self.output_frame, bg="#f0f8ff")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Last Week",
            command=self.filter_last_week,
            bg="#32cd32",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Last Month",
            command=self.filter_last_month,
            bg="#32cd32",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
        ).pack(side="left", padx=5)

        tk.Button(
            button_frame,
            text="Last Year",
            command=self.filter_last_year,
            bg="#32cd32",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
        ).pack(side="left", padx=5)

        tk.Button(
            self.output_frame,
            text="Delete Selected Entry",
            command=self.delete_transaction,
            bg="#ff6347",
            fg="white",
            font=("Arial", 10, "bold"),
        ).pack(pady=5)

        tk.Button(
            self.output_frame,
            text="Generate Summary",
            command=self.generate_summary,
            bg="#32cd32",
            fg="white",
            font=("Arial", 12, "bold"),
        ).pack(pady=10)

    def check_custom_category(self, event=None):
        """Shows or hides the custom category entry field based on the selected category."""
        if self.category_var.get() == "Other":
            self.custom_category_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")
            self.custom_category_entry.grid(row=2, column=3, padx=5, pady=5, sticky="w")
        else:
            self.custom_category_label.grid_remove()
            self.custom_category_entry.grid_remove()

    def add_transaction(self):
        """Handles adding a new transaction."""
        try:
            amount = float(self.amount_entry.get())
            category = self.category_var.get()
            if category == "Other":
                category = self.custom_category_entry.get()
                if not category:
                    raise ValueError("Custom category cannot be empty!")
            date_str = self.date_entry.get()
            date = self.parse_date(date_str)
            if not date:
                return

            transaction_type = self.type_var.get()
            self.tracker.add_transaction(amount, category, date, transaction_type)
            self.update_balance()
            self.show_all_transactions()

            # Clear inputs
            self.amount_entry.delete(0, tk.END)
            self.category_menu.set("Salary")
            self.custom_category_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.type_var.set("Income")

            messagebox.showinfo("Success", "Transaction added successfully!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def apply_filter(self):
        """Applies the filter to the transactions."""
        category = self.filter_category_var.get()
        transaction_type = self.filter_type_var.get()
        start_date = self.parse_date(self.start_date_entry.get())
        end_date = self.parse_date(self.end_date_entry.get())

        if start_date is None and self.start_date_entry.get():
            return
        if end_date is None and self.end_date_entry.get():
            return

        self.filtered_transactions = self.tracker.filter_transactions(category, transaction_type, start_date, end_date)
        self.update_transaction_list(self.filtered_transactions)
        self.update_totals(self.filtered_transactions)

    def parse_date(self, date_str):
        """Parses a date string in MM/DD/YYYY format."""
        if not date_str:
            return None
        try:
            month, day, year = map(int, date_str.split("/"))
            return datetime.date(year, month, day)
        except ValueError:
            messagebox.showerror("Error", f"Invalid date format: {date_str}")
            return None

    def generate_summary(self):
        """Generates a summary for the filtered period."""
        total_income, total_expense = self.tracker.calculate_totals(self.filtered_transactions)
        income_breakdown, expense_breakdown = self.tracker.calculate_category_breakdown(self.filtered_transactions)

        summary_text = (
            f"Summary for Selected Period:\n"
            f"Total Income: ${total_income:.2f}\n"
            f"Total Expenses: ${total_expense:.2f}\n"
            f"Net Gain/Loss: ${total_income - total_expense:.2f}\n\n"
            f"Income Breakdown:\n"
        )

        for category, percentage in income_breakdown.items():
            summary_text += f"  {category}: {percentage:.2f}%\n"

        summary_text += "\nExpense Breakdown:\n"
        for category, percentage in expense_breakdown.items():
            summary_text += f"  {category}: {percentage:.2f}%\n"

        messagebox.showinfo("Summary", summary_text)

    def delete_transaction(self):
        """Deletes the selected transaction."""
        selected_item = self.transaction_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "No transaction selected!")
            return

        index = int(selected_item[0])  # Use the row ID as the index
        self.tracker.delete_transaction(index)
        self.update_balance()
        self.show_all_transactions()

    def filter_last_week(self):
        """Filters transactions for the last week."""
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=7)
        self.apply_date_filter(start_date, end_date)

    def filter_last_month(self):
        """Filters transactions for the last month."""
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=30)
        self.apply_date_filter(start_date, end_date)

    def filter_last_year(self):
        """Filters transactions for the last year."""
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=365)
        self.apply_date_filter(start_date, end_date)

    def apply_date_filter(self, start_date, end_date):
        """Applies a date filter to the transactions."""
        self.filtered_transactions = self.tracker.filter_transactions(
            self.filter_category_var.get(), self.filter_type_var.get(), start_date, end_date
        )
        self.update_transaction_list(self.filtered_transactions)
        self.update_totals(self.filtered_transactions)

    def update_transaction_list(self, transactions):
        """Updates the transaction list."""
        for row in self.transaction_list.get_children():
            self.transaction_list.delete(row)

        for i, t in enumerate(transactions):
            self.transaction_list.insert(
                "", "end",
                iid=i,  # Use the index as the unique identifier
                values=(
                    f"${t['amount']:.2f}",
                    t["category"],
                    datetime.date.fromisoformat(t["date"]).strftime("%m/%d/%Y"),  # Display date in MM/DD/YYYY
                    t["type"],
                ),
            )

    def update_totals(self, transactions):
        """Updates the total income and expense labels."""
        total_income, total_expense = self.tracker.calculate_totals(transactions)
        self.total_income_label.config(text=f"Income over Selected Period: ${total_income:.2f}")
        self.total_expense_label.config(text=f"Expenses over Selected Period: ${total_expense:.2f}")

    def update_balance(self):
        """Updates the balance label."""
        balance = self.tracker.view_balance()
        self.balance_label.config(text=f"Current Balance: ${balance:.2f}")

    def show_all_transactions(self):
        """Displays all transactions without any filters."""
        self.filtered_transactions = self.tracker.transactions
        self.update_transaction_list(self.filtered_transactions)
        self.update_totals(self.filtered_transactions)


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
