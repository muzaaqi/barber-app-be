from datetime import datetime, timedelta

def get_wib_time():
    return datetime.utcnow() + timedelta(hours=7)