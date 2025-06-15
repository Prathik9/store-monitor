import csv
from datetime import timedelta
from app.db.mongo import db
from app.utils.time_utils import get_tz, parse_utc, local_to_utc, next_day
from app.utils.interpolation import interpolate_polls

def get_timezone(store_id):
    tz = db["timezones"].find_one({"store_id": store_id})
    return tz.get("timezone_str", "America/Chicago") if tz else "America/Chicago"

def get_business_hours(store_id):
    hours = list(db["business_hours"].find({"store_id": store_id}))
    if not hours:
        # 24*7 default
        return [
            {"dayOfWeek": i, "start_time_local": "00:00", "end_time_local": "23:59"} for i in range(7)
        ]
    return hours

def get_status_polls(store_id, start_utc, end_utc):
    return list(db["status"].find({
        "store_id": store_id,
        "timestamp_utc": {
            "$gte": start_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "$lte": end_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    }).sort("timestamp_utc", 1))

def biz_intervals(store_id, start_utc, end_utc, store_tz):
    intervals = []
    biz_hours = get_business_hours(store_id)
    tz = get_tz(store_tz)
    cur = start_utc.date()
    while cur <= end_utc.date():
        for entry in biz_hours:
            if entry["dayOfWeek"] == cur.weekday():
                st_utc = local_to_utc(cur, entry["start_time_local"], tz)
                et_utc = local_to_utc(cur, entry["end_time_local"], tz)
                if et_utc <= st_utc:
                    et_utc = local_to_utc(next_day(cur), entry["end_time_local"], tz)
                # Clamp
                interval_start = max(st_utc, start_utc)
                interval_end = min(et_utc, end_utc)
                if interval_end > interval_start:
                    intervals.append((interval_start, interval_end))
        cur = next_day(cur)
    return intervals

def compute_report(now_utc, report_path):
    store_ids = db["status"].distinct("store_id")
    rows = []
    for store_id in store_ids:
        store_tz = get_timezone(store_id)
        intervals = {
            "last_hour": (now_utc - timedelta(hours=1), now_utc),
            "last_day": (now_utc - timedelta(days=1), now_utc),
            "last_week": (now_utc - timedelta(days=7), now_utc),
        }
        out = {}
        for key, (start, end) in intervals.items():
            biz_intvls = biz_intervals(store_id, start, end, store_tz)
            polls = get_status_polls(store_id, start, end)
            up_total = timedelta()
            down_total = timedelta()
            for interval_start, interval_end in biz_intvls:
                sub_polls = [p for p in polls if interval_start <= parse_utc(p["timestamp_utc"]) <= interval_end]
                up, down = interpolate_polls(sub_polls, interval_start, interval_end)
                up_total += up
                down_total += down
            if key == "last_hour":
                out["uptime_last_hour"] = int(up_total.total_seconds() // 60)
                out["downtime_last_hour"] = int(down_total.total_seconds() // 60)
            else:
                out[f"uptime_{key}"] = round(up_total.total_seconds() / 3600, 2)
                out[f"downtime_{key}"] = round(down_total.total_seconds() / 3600, 2)
        rows.append({
            "store_id": store_id,
            "uptime_last_hour(in minutes)": out.get("uptime_last_hour", 0),
            "uptime_last_day(in hours)": out.get("uptime_last_day", 0.0),
            "uptime_last_week(in hours)": out.get("uptime_last_week", 0.0),
            "downtime_last_hour(in minutes)": out.get("downtime_last_hour", 0),
            "downtime_last_day(in hours)": out.get("downtime_last_day", 0.0),
            "downtime_last_week(in hours)": out.get("downtime_last_week", 0.0),
        })
    cols = [
        "store_id",
        "uptime_last_hour(in minutes)",
        "uptime_last_day(in hours)",
        "uptime_last_week(in hours)",
        "downtime_last_hour(in minutes)",
        "downtime_last_day(in hours)",
        "downtime_last_week(in hours)",
    ]
    with open(report_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)