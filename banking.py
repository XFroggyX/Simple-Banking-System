from random import randint
import sqlite3


class Bank_card:

    @classmethod
    def generating_checksum(cls, card_number):
        for i in range(0, len(card_number), 2):
            card_number[i] *= 2
            if card_number[i] > 9:
                card_number[i] -= 9

        checksum = 0
        while (sum(card_number) + checksum) % 10 != 0:
            checksum += 1

        return checksum

    def __init__(self, *save_users):
        if not save_users:
            self.card_number = []
            self.pin_code = None
            self.balance = 0

            self.card_number.append(4)
            self.card_number.extend([0 for _ in range(5)])
            self.card_number.extend([randint(0, 9) for _ in range(9)])
            self.card_number.append(self.generating_checksum(self.card_number[:]))

            self.pin_code = "".join([str(randint(0, 9)) for _ in range(4)])

            print("\nYour card has been created")
        else:
            self.card_number = [int(i) for i in save_users[0]]
            self.pin_code = save_users[1]
            self.balance = save_users[2]

    def get_card_number(self):
        return self.card_number

    def get_pin(self):
        return self.pin_code

    def get_balance(self):
        return self.balance

    def add_income(self, income):
        self.balance += income

    def del_income(self, income):
        self.balance -= income


class Banking_system:

    def add_save_user(self, connect, cursor):
        cursor.execute("""SELECT number, pin, balance FROM card""")
        save_users = cursor.fetchall()
        for save_user in save_users:
            self.list_clients.append(Bank_card(*list(save_user)))
        connect.commit()

    def __init__(self):
        self.list_clients = []
        """Создание или считывание базы данных"""
        connect = sqlite3.connect("card.s3db")
        cursor = connect.cursor()

        connect.commit()
        cursor.execute("""CREATE TABLE IF NOT EXISTS card (
                              id INTEGER,
                              number TEXT,
                              pin TEXT,
                              balance INTEGER DEFAULT 0
                               );""")
        connect.commit()

        self.add_save_user(connect, cursor)

    def create_account(self):
        self.list_clients.append(Bank_card())

        print("Your card number:")
        print("".join([str(p) for p in self.list_clients[-1].get_card_number()]))
        print("Your card PIN:")
        print(self.list_clients[-1].get_pin())

        connect = sqlite3.connect("card.s3db")
        cursor = connect.cursor()

        cursor.execute("INSERT INTO card VALUES (?, ?, ?, ?)",
                       (len(self.list_clients) - 1, "".join([str(p) for p in self.list_clients[-1].get_card_number()]),
                        self.list_clients[-1].get_pin(), 0))
        connect.commit()

    def _check_log(self, card_number, pin):
        for i in range(len(self.list_clients)):
            check_card_number = self.list_clients[i].get_card_number() == [int(i) for i in list(card_number)]
            check_pin = self.list_clients[i].get_pin() == pin

            if check_card_number and check_pin:
                return i
        return -1

    def enter_income(self, index):
        print("\nEnter income:")
        self.list_clients[index].add_income(int(input()))
        print("Income was added!")
        connect = sqlite3.connect("card.s3db")
        cursor = connect.cursor()

        balance = self.list_clients[index].get_balance()
        card_number = "".join([str(i) for i in self.list_clients[index].get_card_number()])
        cursor.execute("UPDATE card SET balance = ? WHERE number = ?", (balance, card_number))
        connect.commit()

    def do_transfer(self, index):
        print("Transfer\nEnter card number:")
        card_number = list(input())
        card_number = [int(i) for i in card_number]

        all_card_numbers = [client.get_card_number() for client in self.list_clients]
        if self.list_clients[index].generating_checksum(card_number[:-1]) != card_number[-1]:  # тут ошибка
            print("\nProbably you made mistake in the card number. Please try again!")
        else:
            if card_number not in all_card_numbers:
                print("\nSuch a card does not exist.")
            else:
                if self.list_clients[index].get_card_number() == card_number:
                    print("\nYou can't transfer money to the same account!")
                else:
                    print("Enter how much money you want to transfer:")
                    money = int(input())
                    if money > self.list_clients[index].get_balance():
                        print("Not enough money!")
                    else:
                        self.list_clients[all_card_numbers.index(card_number)].add_income(money)
                        self.list_clients[index].del_income(money)

                        connect = sqlite3.connect("card.s3db")
                        cursor = connect.cursor()

                        balance = self.list_clients[index].get_balance()
                        card_numbers = "".join([str(i) for i in self.list_clients[index].get_card_number()])
                        cursor.execute("UPDATE card SET balance = ? WHERE number = ?", (balance, card_numbers))

                        balance = self.list_clients[all_card_numbers.index(card_number)].get_balance()
                        add_index = all_card_numbers.index(card_number)
                        card_numbers = "".join([str(i) for i in self.list_clients[add_index].get_card_number()])
                        cursor.execute("UPDATE card SET balance = ? WHERE number = ?", (balance, card_numbers))

                        connect.commit()
                        print("Success!")

    def login_menu(self):
        print("\nEnter your card number:")
        card_number = input()
        print("Enter your PIN:")
        pin = input()

        index = self._check_log(card_number[:], pin)
        if index == -1:
            print("\nWrong card number or PIN!")
        else:
            print("\nYou have successfully logged in!\n")
            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")

                select_point = int(input())

                if select_point == 1:
                    print("\nBalance:", self.list_clients[index].get_balance())
                elif select_point == 2:
                    self.enter_income(index)
                elif select_point == 3:
                    self.do_transfer(index)
                elif select_point == 4:
                    connect = sqlite3.connect("card.s3db")
                    cursor = connect.cursor()

                    cursor.execute(f"""DELETE FROM card WHERE number = {card_number}""")
                    del self.list_clients[index]
                    self.add_save_user(connect, cursor)
                    break
                elif select_point == 5:
                    print("\nYou have successfully logged out!")
                    break
                elif select_point == 0:
                    print("\nBye!")
                    quit()
                print()

    def open_menu(self):
        while True:
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")

            select_point = int(input())

            if select_point == 1:
                self.create_account()
            elif select_point == 2:
                self.login_menu()
            elif select_point == 0:
                print("\nBye!")
                break
            print()


if __name__ == "__main__":
    my_bank = Banking_system()
    my_bank.open_menu()
