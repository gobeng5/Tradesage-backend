from apscheduler.schedulers.background import BackgroundScheduler
from signal_generator import generate_signals

def scheduled_task():
    print("Running market analysis...")
    results = generate_signals()
    print("Generated signals:", results)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_task, "interval", minutes=15)
    scheduler.start()
