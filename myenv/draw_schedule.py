import pytz
from datetime import datetime

draw_schedules = {
    "lottoMax": {"days": ["Tuesday", "Friday"], "time": "22:30"},
    "lotto649": {"days": ["Wednesday", "Saturday"], "time": "22:30"},
    "dailyGrand": {"days": ["Monday", "Thursday"], "time": "22:30"},
}

alberta_tz = pytz.timezone("America/Edmonton")

def get_local_time():
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_time = utc_now.astimezone(alberta_tz)
    return local_time

def is_draw_day(lottery):
    today = get_local_time()
    current_day = today.strftime("%A")
    return current_day in draw_schedules[lottery]["days"]

def is_draw_time(lottery):
    now = get_local_time()
    target_time = draw_schedules[lottery]["time"]
    target_hour, target_minute = map(int, target_time.split(":"))
    return now.hour == target_hour and now.minute == target_minute
