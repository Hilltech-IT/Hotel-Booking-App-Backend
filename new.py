from datetime import datetime

date_format = "%m/%d/%Y %H:%M"
string_text = "4/16/2015 16:00"
date = datetime.strptime(string_text, date_format)
print(date)
