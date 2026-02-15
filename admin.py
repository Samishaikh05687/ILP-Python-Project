from database import get_connection
import json
from datetime import datetime


def admin_login():

    user = input("Enter Username: ")
    pwd = input("Enter Password: ")


    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, pwd))


    if cur.fetchone():

        print(f"\n✓ Login Successful\n")
        admin_menu()
    else:
        print(f"\n Please Enter Correct UserName and Password \n")


    conn.close()


def admin_menu():
    while True:
        print("\n" + "=" * 60)
        print("ADMIN MENU".center(60))
        print("=" * 60)
        print("1) Admin Train Registration")
        print("2) Train Details Update by Admin")
        print("3) Delete Train by Admin")
        print("4) View All Trains")
        print("5) Exit")
        print("=" * 60)


        ch = input("Choice: ")

        match ch:
            case '1':
                print("Admin Train Registration")
                add_train()
            case '2':
                print("Train Details Update by Admin")
                update_train()
            case '3':
                print("Delete Train by Admin")
                delete_train()
            case '4':
                print("View All Train by Admin")
                view_all_train()
            case '5':
                print("Good Bye User!!. Terminating the Program")
                import sys
                sys.exit(0)
            case _:
                print("You have selected an inappropriate option. Kindly select an appropriate option.")

def add_train():
    conn = get_connection()
    cur = conn.cursor()

    # Basic inputs
    tn = input("Train Number: ").strip()
    if not tn:
        print("Train number cannot be empty.")
        conn.close()
        return

    # check uniqueness
    cur.execute("SELECT 1 FROM train WHERE train_number=?", (tn,))
    if cur.fetchone():
        print("Train number already exists. Please use a unique train number.")
        conn.close()
        return

    name = input("Train Name: ").strip()
    if not name:
        print("Train name cannot be empty.")
        conn.close()
        return

    # Route and schedule input
    try:
        n_stations = int(input("Number of stations (including origin and destination): "))
        if n_stations < 2:
            print("Please enter at least 2 stations (origin and destination).")
            conn.close()
            return
    except ValueError:
        print("Invalid number of stations.")
        conn.close()
        return

    route = []
    schedule = []
    print("Enter station details in order from origin to destination:")
    for i in range(n_stations):
        station = input(f"  Station {i+1} name: ").strip()
        if not station:
            print("Station name cannot be empty.")
            conn.close()
            return
        # arrival time: skip for origin
        if i == 0:
            arrival = ""
        else:
            arrival = input(f"    Arrival time at {station} (HH:MM): ").strip()
            if not arrival:
                print("Arrival time cannot be empty for intermediate/destination stations.")
                conn.close()
                return
        # departure time: skip for destination
        if i == n_stations - 1:
            departure = ""
        else:
            departure = input(f"    Departure time from {station} (HH:MM): ").strip()
            if not departure:
                print("Departure time cannot be empty for origin/intermediate stations.")
                conn.close()
                return

        route.append(station)
        schedule.append({"station": station, "arrival": arrival, "departure": departure})

    start = route[0]
    end = route[-1]

    while True:
        seat_capacity = int(input("Total seat capacity: "))
        if seat_capacity > 0:
            break
        print("Seat capacity must be a positive number.")

    # insert into database
    try:
        cur.execute(
            "INSERT INTO train (train_number, train_name, departure, arrival, route, schedule,seat_capacity,available_seats, status) VALUES (?,?,?,?,?,?,?,?,'Active')",
            (tn, name, start, end, json.dumps(route), json.dumps(schedule),seat_capacity,seat_capacity)
        )
        conn.commit()
        print(f"\n✓ Train added successfully \n")
    except Exception as e:
        print("Error adding train:", e)
    finally:
        conn.close()



def update_train():
    conn = get_connection()
    cur = conn.cursor()

    tid = input("Train Number to update (search): ").strip()
    if not tid:
        print("Train number cannot be empty.")
        conn.close()
        return

    cur.execute("SELECT train_number, train_name, departure, arrival, route, schedule FROM train WHERE train_number=?", (tid,))
    row = cur.fetchone()
    if not row:
        print("No train found with the given train number.")
        conn.close()
        return

    # unpack current values
    cur_tn, cur_name, cur_start, cur_end, cur_route_json, cur_schedule_json = row
    try:
        cur_route = json.loads(cur_route_json) if cur_route_json else []
    except Exception:
        cur_route = []
    try:
        cur_schedule = json.loads(cur_schedule_json) if cur_schedule_json else []
    except Exception:
        cur_schedule = []

    print("Current Train Details:")
    print("  Train Number:", cur_tn)
    print("  Train Name:", cur_name)
    print("  Origin:", cur_start)
    print("  Destination:", cur_end)
    if cur_route:
        print("  Route:", " -> ".join(cur_route))
    if cur_schedule:
        print("  Schedule:")
        for s in cur_schedule:
            print("    ", s)

    print("\nSelect field to update:")
    print("1) Train Name")
    print("2) Route and Schedule")
    print("3) Cancel")
    choice = input("Choice: ").strip()

    def valid_time(t: str) -> bool:
        try:
            datetime.strptime(t, "%H:%M")
            return True
        except Exception:
            return False

    if choice == '1':
        new_name = input("New Train Name: ").strip()
        if not new_name:
            print("Train name cannot be empty.")
            conn.close()
            return
        try:
            cur.execute("UPDATE train SET train_name=? WHERE train_number=?", (new_name, tid))
            conn.commit()
            print("Train details have been updated")
        except Exception as e:
            print("Error updating train:", e)
        finally:
            conn.close()
        return

    if choice == '2':
        # collect new route/schedule similar to add_train
        try:
            n_stations = int(input("Number of stations (including origin and destination): "))
            if n_stations < 2:
                print("Please enter at least 2 stations (origin and destination).")
                conn.close()
                return
        except ValueError:
            print("Invalid number of stations.")
            conn.close()
            return

        route = []
        schedule = []
        print("Enter station details in order from origin to destination:")
        for i in range(n_stations):
            station = input(f"  Station {i+1} name: ").strip()
            if not station:
                print("Station name cannot be empty.")
                conn.close()
                return
            if i == 0:
                arrival = ""
            else:
                arrival = input(f"    Arrival time at {station} (HH:MM): ").strip()
                if not arrival or not valid_time(arrival):
                    print("Invalid arrival time. Use HH:MM format.")
                    conn.close()
                    return
            if i == n_stations - 1:
                departure = ""
            else:
                departure = input(f"    Departure time from {station} (HH:MM): ").strip()
                if not departure or not valid_time(departure):
                    print("Invalid departure time. Use HH:MM format.")
                    conn.close()
                    return

            route.append(station)
            schedule.append({"station": station, "arrival": arrival, "departure": departure})

        new_start = route[0]
        new_end = route[-1]
        # departure at origin and arrival at destination
        new_departure_origin = schedule[0].get('departure', '')
        new_arrival_dest = schedule[-1].get('arrival', '')

        # conflict check: any other train with same origin+destination and same departure+arrival
        cur.execute("SELECT train_number, schedule FROM train WHERE start_location=? AND end_location=? AND train_number!=?", (new_start, new_end, tid))
        conflicts = []
        for other_tn, other_schedule_json in cur.fetchall():
            try:
                other_schedule = json.loads(other_schedule_json) if other_schedule_json else []
            except Exception:
                other_schedule = []
            if not other_schedule:
                continue
            other_departure = other_schedule[0].get('departure', '')
            other_arrival = other_schedule[-1].get('arrival', '')
            if other_departure == new_departure_origin and other_arrival == new_arrival_dest:
                conflicts.append(other_tn)

        if conflicts:
            print("Schedule conflict detected with other trains:", ", ".join(conflicts))
            print("Two different trains cannot have the same departure and arrival times for the same origin and destination.")
            conn.close()
            return

        # perform update
        try:
            cur.execute(
                "UPDATE train SET departure=?, arrival=?, route=?, schedule=? WHERE train_number=?",
                (new_start, new_end, json.dumps(route), json.dumps(schedule), tid)
            )
            conn.commit()

            print(f"\n✓ Train details have been updated\n")

        except Exception as e:
            print("Error updating train:", e)
        finally:
            conn.close()
        return


    print(f"\n✗ Update cancelled\n")
    conn.close()



def delete_train():
    conn = get_connection()
    cur = conn.cursor()
    tn = input("Train Number to delete: ").strip()
    if not tn:
        print("Train number cannot be empty.")
        conn.close()
        return

    cur.execute("SELECT train_id, train_number, train_name FROM train WHERE train_number=?", (tn,))
    row = cur.fetchone()
    if not row:
        print("No train found with the given train number.")
        conn.close()
        return

    train_id, train_number, train_name = row
    print(f"Found Train: {train_number} - {train_name}")
    confirm = input("Are you sure you want to delete this train? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Deletion cancelled.")
        conn.close()
        return

    try:
        # mark associated bookings as cancelled
        cur.execute("UPDATE booking SET status='Cancelled' WHERE train_id=?", (train_id,))
        # delete train record
        cur.execute("DELETE FROM train WHERE train_id=?", (train_id,))
        conn.commit()
        print(f"\n✗ Train deleted and associated bookings marked as cancelled\n")
    except Exception as e:
        print("Error deleting train:", e)
    finally:
        conn.close()


def view_all_train():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT train_id,train_number, train_name, departure, arrival, seat_capacity, available_seats FROM train ORDER BY train_id"
        )

        rows = cur.fetchall()

        if not rows:
            print("No train found with the given train number.")
            return

        print("\n ALL Trains")
        print("-" * 100)
        print(f"{'ID':<5}{'Train No':<10}{'Name':<20}{'From':<15}{'To':<15}{'Capacity':<10}{'Available Seats':<10}")
        print("-" * 100)

        for r in rows:
            print(f"{r[0]:<5}{r[1]:<10}{r[2]:<20}{r[3]:<15}{r[4]:<15}{r[5]:<10}{r[6]:<10}")

    except Exception as e:
        print("Error viewing all trains:", e)

    finally:
        conn.close()