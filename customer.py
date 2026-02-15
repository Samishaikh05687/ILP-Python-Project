from database import get_connection
from datetime import datetime, timedelta
from utils import valid_email, valid_phone, validate_future_date

def customer_login():
    username = input("Enter UserName: ").strip()
    password = input("Enter Password: ").strip()
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT customer_id,active FROM customer
            WHERE username=? AND password=? 
        """, (username, password))

        row = cur.fetchone()

        if not row:
            print(f"\n✗ Please Enter Correct UserName and Password\n")
            return

        customer_id,active_status = row

        if active_status == 0:
            print(f"\n✗ Your account has been disabled. Please contact admin.\n")
            return

        print(f"\n ✓ Login Successful\n")
        customer_menu(customer_id)

    except Exception as e:
        print("Something went wrong - ",e)

    finally:
        conn.close()



def customer_registration():

    name = input("Name: ")
    if not name.isalpha():
        print(f"\n✗Name should contain only alphabets\n")
        return

    while True:
        email = input("Email: ").strip()
        if  valid_email(email):
            break
        print(f"\n✗ Invalid Email format!!! Enter Again\n")


    while True:
        phone = input("Phone: ").strip()
        if  valid_phone(phone):
            break
        print(f"\n✗ Phone number must be 10 digits. Enter Again \n")


    address = input("Address: ")
    username = input("Username: ")
    password = input("Password: ")



    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO customer
            (name,email,phone,address,username,password,active)
            VALUES (?,?,?,?,?,?,1)
        """, (name, email, phone, address,username, password))

        conn.commit()
        print(f"\n✓ Customer Registered Successfully\n")
    except Exception as e:
        print("Database Error:", e)
    finally:
        conn.close()

def customer_update(customer_id):

    name = input("Enter New Name: ")
    if not name.isalpha():
        print("Name should contain only alphabets")
        return

    while True:
        email = input("Enter New Email: ")
        if valid_email(email):
            break
        print("Invalid Email format!!! Enter Again")

    while True:
        phone = input("Enter New Phone: ")
        if valid_phone(phone):
            break
        print(f"\n✗ Phone number must be 10 digits. Enter Again \n")


    address = input("New Address: ")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE customer
            SET name=?, email=?, phone=?, address=?
            WHERE customer_id=?
        """, (name, email, phone, address, customer_id))
        conn.commit()
        print("Details Updated Successfully")
    except Exception as e:
        print("Database Error:", e)
    finally:
        conn.close()

def customer_soft_delete(customer_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE customer SET active=0 WHERE customer_id=?
        """, (customer_id,))
        conn.commit()
        print("Account Deactivated Successfully")
    except Exception as e:
        print("Database Error:", e)
    finally:
        conn.close()

def display_trains():
    origin = input("Origin Station: ").strip()
    destination = input("Destination Station: ").strip()
    travel_date = input("Travel Date (YYYY-MM-DD): ").strip()

    date_obj = datetime.strptime(travel_date, "%Y-%m-%d")
    if date_obj > datetime.now() + timedelta(days=90):
        print("Travel date must be within next 3 months")
        return

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT train_number, train_name, departure, arrival,
                   seat_capacity, available_seats
            FROM train
            WHERE route LIKE ? OR route LIKE ?
        """, (f"%{origin}%", f"%{destination}%"))

        rows = cur.fetchall()
        if not rows:
            print("x No Trains Available")
            return

        print("\n Available Trains For Your Journey")
        print("-"*80)
        print(f"{'No':<10}{'Name':<20}{'From':<15}{'To':<15}{'Seats':<10}")
        print("-"*80)

        for r in rows:
                print(f"{r[0]:<10}{r[1]:<20}{r[2]:<15}{r[3]:<15}{r[4]:<10}")
    except Exception as e:
        print("Database Error:", e)
    finally:
        conn.close()

from datetime import datetime

def train_ticket_booking(customer_id):
    try:
        train_number = input("Enter Train Number: ").strip()
        while True:
            journey_date = input("Travel Date (YYYY-MM-DD): ").strip()
            date_obj = validate_future_date(journey_date)
            if date_obj:
                break

        # Prevent past date booking
        if datetime.strptime(journey_date, "%Y-%m-%d").date() < datetime.now().date():
            print(" Cannot book tickets for past dates")
            return

        print("\nSelect Seat Type")
        print("1. AC       - ₹500 per seat")
        print("2. Sleeper  - ₹300 per seat")
        print("3. General  - ₹200 per seat")

        seat_prices = {
            '1': ('AC', 500),
            '2': ('Sleeper', 300),
            '3': ('General', 200)
        }

        seat_choice = input("Enter choice (1-3): ").strip()
        if seat_choice not in seat_prices:
            print(" Invalid Seat Type Selection")
            return

        seat_type, price_per_seat = seat_prices[seat_choice]

        seat_count = int(input("Number of Seats (Max 6): "))
        if seat_count <= 0 or seat_count > 6:
            print(" Seat count must be between 1 and 6")
            return

        conn = get_connection()
        cur = conn.cursor()

        # Fetch train details
        cur.execute("""
            SELECT train_name, departure, arrival, available_seats
            FROM train
            WHERE train_number=?
        """, (train_number,))
        train = cur.fetchone()

        if not train:
            print(f"\nx Invalid Train Number \n")
            return

        train_name, departure, arrival, available_seats = train

        if available_seats < seat_count:
            print(f"\n x Seats Not Available \n")
            return

        fare = seat_count * price_per_seat

        print("\n" + "=" * 60)
        print(f"{'TICKET DETAILS'.center(60)}")
        print("=" * 60)
        print(f"Route                    : {departure} → {arrival}")
        print(f"Journey Date             : {journey_date}")
        print(f"Seat Type                : {seat_type}")
        print(f"Number of Seats Booked   : {seat_count}")
        print(f"Fare per Seat            : ₹{price_per_seat}")
        print(f"Total Fare               : ₹{fare}")
        print("=" * 60)

        confirm = input("Confirm Booking (yes/no): ").lower()
        if confirm != "yes":
            print("x Booking Cancelled")
            return

        booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO booking
            (customer_id, train_number, journey_date, seat_type, seats, fare, status, booking_time)
            VALUES (?, ?, ?, ?, ?, ?, 'Booked', ?)
        """, (customer_id, train_number, journey_date, seat_type, seat_count, fare, booking_time))

        booking_id = cur.lastrowid

        cur.execute("""
            UPDATE train
            SET available_seats = available_seats - ?
            WHERE train_number=?
        """, (seat_count, train_number))

        conn.commit()

        # -------- BOOKING CONFIRMATION --------
        print("\n" + "-" * 60)
        print("          TICKET BOOKED SUCCESSFULLY")
        print("-" * 60)
        print(f"Booking ID     : {booking_id}")
        print(f"Passenger ID   : {customer_id}")
        print(f"Train          : {train_name} ({train_number})")
        print(f"Route          : {departure} → {arrival}")
        print(f"Journey Date   : {journey_date}")
        print(f"Seat Type      : {seat_type}")
        print(f"Seats Booked   : {seat_count}")
        print(f"Total Fare     : ₹{fare}")
        print(f"Booking Time   : {booking_time}")
        print("Status         : CONFIRMED")
        print("-" * 60)

    except Exception as e:
        print("x Database Error:", e)

    finally:
        conn.close()
       


def cancel_ticket(customer_id):
    booking_id = input("Enter Booking ID: ").strip()
    password = input("Enter your account password: ").strip()

    try:
        conn = get_connection()
        cur = conn.cursor()

      
        cur.execute("""
            SELECT password
            FROM customer
            WHERE customer_id=? AND active=1
        """, (customer_id,))
        user = cur.fetchone()

        if not user or user[0] != password:
            print(f"\n x Unauthorized cancellation. Incorrect password. \n")
            return

        
        cur.execute("""
            SELECT train_number, seats, fare, journey_date, booking_time
            FROM booking
            WHERE booking_id=? AND customer_id=? AND status='Booked'
        """, (booking_id, customer_id))

        row = cur.fetchone()

        if not row:
            print(" Invalid Booking ID or Ticket already cancelled.")
            return

        train_number, seats, fare, journey_date, booking_time = row

        journey_dt = datetime.strptime(journey_date, "%Y-%m-%d")

       
        if datetime.now() > journey_dt - timedelta(hours=24):
            print(" Cancellation not allowed within 24 hours of departure.")
            return

     
        refund_amount = fare * 0.80  # 80% refund

        
        print("\nTicket Details")
        print("-" * 40)
        print(f"Booking ID   : {booking_id}")
        print(f"Train Number : {train_number}")
        print(f"Journey Date : {journey_date}")
        print(f"Seats        : {seats}")
        print(f"Fare Paid    : ₹{fare}")
        print(f"Refund Amount: ₹{refund_amount}")
        print("-" * 40)

        confirm = input("Confirm cancellation? (yes/no): ").lower()
        if confirm != "yes":
            print(" Cancellation aborted by user.")
            return

     
        cur.execute("""
            UPDATE booking
            SET status='Cancelled'
            WHERE booking_id=?
        """, (booking_id,))

       
        cur.execute("""
            UPDATE train
            SET available_seats = available_seats + ?
            WHERE train_number=?
        """, (seats, train_number))

        conn.commit()

        print("\n Ticket Cancelled Successfully")
        print(f" Refund of ₹{refund_amount} will be processed to your account within 5-7 business days.")

    except Exception as e:
        print("x Database Error:", e)

    finally:
        conn.close()


def view_booking_history(customer_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                b.booking_id,
                b.journey_date,
                t.train_number,
                t.train_name,
                b.seat_type,
                b.seats,
                b.fare,
                b.status
            FROM booking b
            JOIN train t ON b.train_number = t.train_number
            WHERE b.customer_id=?
            ORDER BY b.journey_date DESC
        """, (customer_id,))

        rows = cur.fetchall()

        if not rows:
            print(f"\n xxxxx   No Booking History Found   xxxxx\n")
            return

        print("\nYOUR BOOKING HISTORY")
        print("=" * 120)
        print(
            f"{'Booking ID':<12}"
            f"{'Date':<14}"
            f"{'Train No':<12}"
            f"{'Train Name':<30}"
            f"{'Class':<10}"
            f"{'Seats':<8}"
            f"{'Fare(₹)':<10}"
            f"{'Status':<10}"
        )
        print("=" * 120)

        for r in rows:
            formatted_date = datetime.strptime(r[1], "%Y-%m-%d").strftime("%d-%m-%Y")

            print(
                f"{r[0]:<12}"
                f"{formatted_date:<14}"
                f"{r[2]:<12}"
                f"{r[3]:<30}"
                f"{r[4]:<10}"
                f"{r[5]:<8}"
                f"{r[6]:<10}"
                f"{r[7]:<10}"
            )

        print("=" * 120)

    except Exception as e:
        print("x Database Error:", e)

    finally:
        conn.close()

        


def customer_menu(customer_id):
    while True:
        print("\n" + "=" * 60)
        print("CUSTOMER MAIN MENU".center(60))
        print("=" * 60)
        print("""
1. Customer Details Update
2. Customer Soft Delete
3. Display Available Trains
4. Train Ticket Booking
5. Ticket Cancellation
6. View Booking History
7. Exit
        """)
        print("=" * 60)
        choice = input("Enter choice: ")

        if choice == '1':
            customer_update(customer_id)
        elif choice == '2':
            customer_soft_delete(customer_id)
            break
        elif choice == '3':
            display_trains()
        elif choice == '4':
            train_ticket_booking(customer_id)
        elif choice == '5':
            cancel_ticket(customer_id)
        elif choice == '6':
            view_booking_history(customer_id)
        elif choice == '7':
            print(f"\n Thank You! Have a safe journey!!! \n")
            break
        else:
            print("Invalid Option")