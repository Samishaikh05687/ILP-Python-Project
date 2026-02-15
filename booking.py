from database import get_connection


# US009 – Display Available Trains
def show_trains():
    source = input("Enter Source Station: ")
    destination = input("Enter Destination Station: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT train_id, train_number, train_name, start_location, end_location
        FROM train
        WHERE start_location=? AND end_location=? AND status='Active'
    """, (source, destination))

    trains = cur.fetchall()

    if not trains:
        print("No trains available")
    else:
        print("\nAvailable Trains:")
        for t in trains:
            print(t)

    conn.close()

# US010 – Train Ticket Booking
def book_ticket(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    train_id = input("Enter Train ID: ")
    journey_date = input("Enter Journey Date (YYYY-MM-DD): ")
    price = float(input("Enter Ticket Price: "))
    tickets = int(input("Number of Tickets (max 6): "))

    if tickets > 6:
        print("Cannot book more than 6 tickets")
        conn.close()
        return

    for _ in range(tickets):
        cur.execute("""
            INSERT INTO booking (passenger_id, train_id, price, journey_date, status)
            VALUES (?, ?, ?, ?, 'Booked')
        """, (customer_id, train_id, price, journey_date))

    conn.commit()
    conn.close()
    print("Ticket(s) booked successfully")

# US011 – Ticket Cancellation
def cancel_ticket():
    booking_id = input("Enter Booking ID: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT status FROM booking WHERE booking_id=?", (booking_id,))
    record = cur.fetchone()

    if not record:
        print("Invalid Booking ID")
    elif record[0] == 'Cancelled':
        print("Ticket already cancelled")
    else:
        cur.execute("""
            UPDATE booking
            SET status='Cancelled'
            WHERE booking_id=?
        """, (booking_id,))
        conn.commit()
        print("Ticket cancelled successfully")

    conn.close()


# US012 – View Booking History
def booking_history(customer_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT booking_id, train_id, journey_date, price, status
        FROM booking
        WHERE passenger_id=?
    """, (customer_id,))

    bookings = cur.fetchall()

    if not bookings:
        print("No booking history found")
    else:
        print("\nBooking History:")
        for b in bookings:
            print(b)

    conn.close()