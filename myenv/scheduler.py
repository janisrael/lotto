# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time
from cron import run_lottery_job  # import your job logic

now = datetime.now()
test_day = now.strftime("%A")
test_time = (now + timedelta(minutes=1)).strftime("%H:%M")
# print(test_time,'test')


draw_schedules = {
    "lottoMax": {"days": ["Tuesday", "Friday"], "time": "22:30"},
    "lotto649": {"days": ["Wednesday", "Saturday"], "time": "22:30"},
    "dailyGrand": {"days": ["Monday", "Thursday"], "time": test_time},
}

def is_within_time_window(start_time_str, duration_minutes=120):
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    start_time = datetime.strptime(f"{today_str} {start_time_str}", "%Y-%m-%d %H:%M")
    end_time = start_time + timedelta(minutes=duration_minutes)
    # print(start_time, end_time)
    return start_time <= now <= end_time
# def should_run_now(start_time_str, interval_minutes=20):
def should_run_now(start_time_str, interval_minutes=20):
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    start_time = datetime.strptime(f"{today_str} {start_time_str}", "%Y-%m-%d %H:%M")
    if now < start_time:
        return False
    elapsed = (now - start_time).total_seconds() / 60
    # print(elapsed,'elapse')
    return elapsed % interval_minutes < 1

def run_scheduled_draws():
    now = datetime.now()
    current_day = now.strftime("%A")
    
    for draw_name, schedule in draw_schedules.items():

        if current_day in schedule["days"]:
          
            if is_within_time_window(schedule["time"], 120) and should_run_now(schedule["time"]):
                run_lottery_job(draw_name)
            else:
                print('false')

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scheduled_draws, 'interval', minutes=1)
    scheduler.start()
    print("✅ Scheduler started and running every 1 minute.")
