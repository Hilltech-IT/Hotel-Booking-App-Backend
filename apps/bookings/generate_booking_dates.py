from datetime import datetime, timedelta


def generate_booked_dates(start_date_str, end_date_str):
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    date_list = []
    current = start
    while current <= end:
        date_list.append(current.isoformat())
        current += timedelta(days=1)

    return date_list


def calculate_days_booked(start_date_str, end_date_str):
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    return (end - start).days + 1
