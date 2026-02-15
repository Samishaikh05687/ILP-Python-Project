import sqlite3

def get_connection():
	return sqlite3.connect("train.db")


def create_tables():
	conn = get_connection()
	cur = conn.cursor()

	cur.execute("""
	CREATE TABLE IF NOT EXISTS admin (
		admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
		username TEXT UNIQUE,
		password TEXT
	)
	""")

	cur.execute("INSERT OR IGNORE INTO admin (admin_id, username, password) VALUES (1, 'admin', 'admin123')")

	cur.execute("""
	CREATE TABLE IF NOT EXISTS customer (
		customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT,
		email TEXT UNIQUE,
		phone TEXT,
		address TEXT,
		username TEXT UNIQUE,
		password TEXT,
		active INTEGER DEFAULT 1
	)
	""")

	cur.execute("""
	CREATE TABLE IF NOT EXISTS passenger (
		customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
		first_name TEXT NOT NULL,
		last_name TEXT NOT NULL,
		age INTEGER CHECK(age > 0),
		gender TEXT CHECK(gender IN ('M','F','O')),
		seat_number TEXT
	)
	""")

	cur.execute("""
	CREATE TABLE IF NOT EXISTS train (
		train_id INTEGER PRIMARY KEY AUTOINCREMENT,
		train_number TEXT UNIQUE,
		train_name TEXT,
		departure TEXT,
		arrival TEXT,
		route TEXT,
		schedule TEXT,
		seat_capacity INTEGER,
		available_seats INTEGER,
		status TEXT CHECK(status IN ('Active','Inactive'))
	)
	""")

	cur.execute("""
CREATE TABLE IF NOT EXISTS booking (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    train_number TEXT,
    journey_date TEXT,
    seat_type TEXT,
    seats INTEGER,
    fare REAL,
    status TEXT DEFAULT 'Booked',
    booking_time TEXT,
    FOREIGN KEY(customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY(train_number) REFERENCES train(train_number)
)
""")

	conn.commit()
	conn.close()