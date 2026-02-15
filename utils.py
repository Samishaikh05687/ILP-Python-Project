import re
from datetime import datetime, timedelta

def valid_email(email):
	return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))


def valid_phone(phone):
	return phone.isdigit() and len(phone) == 10 	



def validate_future_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        
        if date_obj.date() < datetime.now().date():
            print(" Travel date cannot be in the past.")
            return None

        
        if date_obj > datetime.now() + timedelta(days=90):
            print(" Travel date must be within next 3 months.")
            return None

        return date_obj

    except ValueError:
        print(" Invalid date. Please enter a valid date in YYYY-MM-DD format.")
        return None
