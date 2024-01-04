from datetime import datetime

date_format = "%m/%d/%Y %H:%M"


def fix_date_str(string_text):
    time_part = [x for x in string_text.split()][1]
    date_part = [x.split("/") for x in string_text.split()][0]
    date_part[-1] = "2015"

    date_part = f'{"/".join(date_part)} {time_part}'

    return date_part

string_text = "4/16/15 16:00"
x = fix_date_str(string_text)
date = datetime.strptime(x, date_format)
print(date)