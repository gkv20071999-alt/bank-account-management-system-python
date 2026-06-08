import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


DATA_FILE = Path("bank_data.json")


class Account(ABC):
    bank_name = "Python OOP Bank"

    def __init__(self, account_number, holder_name, balance=0):
        self.account_number = account_number
        self.holder_name = holder_name
        self._balance = balance
        self.transactions = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            print("Amount 0 se bada hona chahiye.")
            return

        self._balance += amount
        self.add_transaction("Deposit", amount)
        print(f"Rs {amount} deposit ho gaye.")

    def withdraw(self, amount):
        if amount <= 0:
            print("Amount 0 se bada hona chahiye.")
            return

        if amount > self._balance:
            print("Insufficient balance.")
            return

        self._balance -= amount
        self.add_transaction("Withdraw", amount)
        print(f"Rs {amount} withdraw ho gaye.")

    def add_transaction(self, transaction_type, amount):
        self.transactions.append(
            {
                "type": transaction_type,
                "amount": amount,
                "balance_after": self._balance,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def show_balance(self):
        print(f"Available Balance: Rs {self._balance}")

    def show_details(self):
        print("\nAccount Details")
        print("---------------")
        print("Bank Name:", self.bank_name)
        print("Account Number:", self.account_number)
        print("Holder Name:", self.holder_name)
        print("Account Type:", self.account_type())
        print("Available Balance:", self._balance)

    def show_transactions(self):
        print("\nTransaction History")
        print("-------------------")

        if not self.transactions:
            print("Abhi koi transaction nahi hai.")
            return

        for transaction in self.transactions:
            print(
                f"{transaction['time']} | "
                f"{transaction['type']} | "
                f"Rs {transaction['amount']} | "
                f"Balance: Rs {transaction['balance_after']}"
            )

    def to_dict(self):
        return {
            "account_type": self.account_type(),
            "account_number": self.account_number,
            "holder_name": self.holder_name,
            "balance": self._balance,
            "transactions": self.transactions,
        }

    @abstractmethod
    def account_type(self):
        pass

    @staticmethod
    def validate_amount(value):
        try:
            amount = float(value)
            return amount
        except ValueError:
            return None


class SavingsAccount(Account):
    def account_type(self):
        return "Savings"


class CurrentAccount(Account):
    def __init__(self, account_number, holder_name, balance=0, overdraft_limit=5000):
        super().__init__(account_number, holder_name, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            print("Amount 0 se bada hona chahiye.")
            return

        if amount > self._balance + self.overdraft_limit:
            print("Overdraft limit exceed ho gayi.")
            return

        self._balance -= amount
        self.add_transaction("Withdraw", amount)
        print(f"Rs {amount} withdraw ho gaye.")

    def show_details(self):
        super().show_details()
        print("Overdraft Limit:", self.overdraft_limit)

    def to_dict(self):
        data = super().to_dict()
        data["overdraft_limit"] = self.overdraft_limit
        return data

    def account_type(self):
        return "Current"


class Bank:
    def __init__(self):
        self.accounts = {}
        self.load_data()

    def create_account(self):
        print("\nCreate Account")
        print("1. Savings Account")
        print("2. Current Account")

        choice = input("Account type choose karo: ")
        holder_name = input("Holder name: ").strip()

        if not holder_name:
            print("Holder name empty nahi ho sakta.")
            return

        initial_amount = self.ask_amount("Initial amount: ")
        if initial_amount is None:
            return

        account_number = self.generate_account_number()

        if choice == "1":
            account = SavingsAccount(account_number, holder_name, initial_amount)
        elif choice == "2":
            account = CurrentAccount(account_number, holder_name, initial_amount)
        else:
            print("Invalid account type.")
            return

        account.add_transaction("Account Opened", initial_amount)
        self.accounts[account_number] = account
        self.save_data()

        print("\nAccount successfully create ho gaya.")
        print("Account Number:", account_number)

    def deposit_amount(self):
        account = self.find_account()
        if account is None:
            return

        amount = self.ask_amount("Deposit amount: ")
        if amount is None:
            return

        account.deposit(amount)
        self.save_data()

    def withdraw_amount(self):
        account = self.find_account()
        if account is None:
            return

        amount = self.ask_amount("Withdraw amount: ")
        if amount is None:
            return

        account.withdraw(amount)
        self.save_data()

    def check_balance(self):
        account = self.find_account()
        if account:
            account.show_balance()

    def show_account_details(self):
        account = self.find_account()
        if account:
            account.show_details()

    def show_transaction_history(self):
        account = self.find_account()
        if account:
            account.show_transactions()

    def show_all_accounts(self):
        if not self.accounts:
            print("Abhi koi account nahi hai.")
            return

        print("\nAll Accounts")
        print("------------")
        for account in self.accounts.values():
            print(
                f"{account.account_number} | "
                f"{account.holder_name} | "
                f"{account.account_type()} | "
                f"Rs {account.balance}"
            )

    def find_account(self):
        account_number = input("Account number: ").strip()
        account = self.accounts.get(account_number)

        if account is None:
            print("Account nahi mila.")
            return None

        return account

    def ask_amount(self, message):
        amount = Account.validate_amount(input(message))

        if amount is None:
            print("Invalid amount.")
            return None

        return amount

    def generate_account_number(self):
        if not self.accounts:
            return "1001"

        last_number = max(int(number) for number in self.accounts)
        return str(last_number + 1)

    def save_data(self):
        data = [account.to_dict() for account in self.accounts.values()]

        with DATA_FILE.open("w") as file:
            json.dump(data, file, indent=4)

    def load_data(self):
        if not DATA_FILE.exists():
            return

        with DATA_FILE.open("r") as file:
            data = json.load(file)

        for item in data:
            if item["account_type"] == "Savings":
                account = SavingsAccount(
                    item["account_number"],
                    item["holder_name"],
                    item["balance"],
                )
            elif item["account_type"] == "Current":
                account = CurrentAccount(
                    item["account_number"],
                    item["holder_name"],
                    item["balance"],
                    item.get("overdraft_limit", 5000),
                )
            else:
                continue

            account.transactions = item.get("transactions", [])
            self.accounts[account.account_number] = account


def main():
    bank = Bank()

    while True:
        print("\n===== Banking System =====")
        print("1. Create Account")
        print("2. Deposit Amount")
        print("3. Withdraw Amount")
        print("4. Check Available Balance")
        print("5. Account Details")
        print("6. Transaction History")
        print("7. Show All Accounts")
        print("8. Exit")

        choice = input("Apni choice enter karo: ")

        if choice == "1":
            bank.create_account()
        elif choice == "2":
            bank.deposit_amount()
        elif choice == "3":
            bank.withdraw_amount()
        elif choice == "4":
            bank.check_balance()
        elif choice == "5":
            bank.show_account_details()
        elif choice == "6":
            bank.show_transaction_history()
        elif choice == "7":
            bank.show_all_accounts()
        elif choice == "8":
            print("Thank you for using Python OOP Bank.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
