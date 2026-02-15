from database import create_tables
from admin import admin_login
from customer import customer_registration, customer_login


create_tables()

title="WELCOME TO TRAIN MANAGEMENT SYSTEM"

print("\n" + "-" * 50)
print(f"{title:^50}")
print("-" * 50)

while True:
    print("-" * 50)
    print("MAIN MENU".center(50))
    print("-" * 50)
    print("1. Administrator Login")
    print("2. customer Registration")
    print("3. customer Login")
    print("4. Exit")
    print("-" * 50)

    ch = input("Enter your choice (1-4): ").strip()

    match ch:
        case '1':
            admin_login()
        case '2':
            customer_registration()
        case '3':
            customer_login()
        case '4':
            print("\nExiting the system. Thank you.")
            break
        case _:
            print("\nInvalid choice. Please enter a valid option (1-4).")