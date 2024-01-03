tx_ref = "ticket_778200"

if tx_ref.startswith("ticket_"):
    print("This is an event ticket")
elif tx_ref.startswith("room_"):
    print("This is a room ticket")