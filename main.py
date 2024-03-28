from datetime import datetime, timezone
import pytz

print(datetime.now(pytz.timezone('Europe/Moscow')))