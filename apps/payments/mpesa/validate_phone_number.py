def validate_phone_number(value):
    validated_phone_number = value
    if value[0] in [2, "2"]:
        validated_phone_number = value
    elif value[0] == "+":
        validated_phone_number = value[1:]
    elif value[0] in ["0", 0]:
        validated_phone_number = "254" + value[1:]

    return validated_phone_number
