import sys


class Bank():
    bankName = "SBI"

    def __init__(self, name, balance=0.0):
        self.name = name
        self.balance = balance

    def deposit(self, amount):
        self.balance = self.balance + amount
        print("balance after deposit:%s", self.balance)

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insfficient funds can not perform operation")
            sys.exit()
        self.balance = self.balance - amount
        print("balance after withdraw:%s", self.balance)


print("Welcome to bank", Bank.bankName)
name = input("Enter your name:")
pav = Bank(name)

while True:
    print("Press 1 for diposit \nPress 2 for withdraw \nPress 3 for exit")
    option = input("Please enter your option:")
    if option == '1':
        print("enter your amount to diposte")
        amount = float(input("Enter amount:"))
        pav.deposit(amount)
    elif option == '2':
        print("Please enter amount to withdraw")
        amount = float(input("enter amount:"))
        pav.withdraw(amount)
    elif option == '3':
        print("Thanks for using banking")
        sys.exit()
    else:
        print("Please enter valid option please try again latter")
        sys.exit()
