import time
def generate_payment_reference(booking_type, booking_id, user_id):
    timestamp = int(time.time())
    payment_reference = f"{booking_type}_{user_id}_{booking_id}_{str(timestamp)}"
    return payment_reference