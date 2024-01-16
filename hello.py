from datetime import datetime, timedelta


def get_date_range(checkin_date, checkout_date):
    # Parse input strings to datetime objects
    checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d")
    checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d")

    # Calculate the number of days in the range
    delta = checkout_date - checkin_date

    # Generate the list of dates
    date_range = [checkin_date + timedelta(days=i) for i in range(delta.days + 1)]

    # Convert the dates back to string format
    date_range_str = [date.strftime("%Y-%m-%d") for date in date_range]

    return date_range_str

# Example usage:
checkin_date = "2024-01-20"
checkout_date = "2024-01-25"
result = get_date_range(checkin_date, checkout_date)
print(result)
