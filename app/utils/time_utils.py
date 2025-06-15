from datetime import datetime, timedelta
import pytz

def get_tz(store_tz):
    return pytz.timezone(store_tz)

def parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=pytz.UTC)

def as_utc(dt):
    if dt.tzinfo is None:
        return pytz.UTC.localize(dt)
    return dt.astimezone(pytz.UTC)

def local_to_utc(date, time_str, tz):
    """date: datetime.date, time_str: HH:MM, tz: pytz timezone"""
    local_dt = tz.localize(datetime.combine(date, datetime.strptime(time_str, "%H:%M").time()))
    return local_dt.astimezone(pytz.UTC)

def next_day(dt):
    return dt + timedelta(days=1)