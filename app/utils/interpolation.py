from datetime import timedelta, datetime
from app.utils.time_utils import parse_utc

def interpolate_polls(polls, interval_start, interval_end):
    points = []
    # Add virtual points at interval boundaries if needed
    if polls:
        first_time = parse_utc(polls[0]["timestamp_utc"])
        if first_time > interval_start:
            points.append({"timestamp_utc": interval_start.strftime("%Y-%m-%d %H:%M:%S UTC"),
                           "status": polls[0]["status"]})
        points.extend(polls)
        last_time = parse_utc(polls[-1]["timestamp_utc"])
        if last_time < interval_end:
            points.append({"timestamp_utc": interval_end.strftime("%Y-%m-%d %H:%M:%S UTC"),
                           "status": polls[-1]["status"]})
    else:
        # No polls in this interval, assume always active
        points = [
            {"timestamp_utc": interval_start.strftime("%Y-%m-%d %H:%M:%S UTC"), "status": "active"},
            {"timestamp_utc": interval_end.strftime("%Y-%m-%d %H:%M:%S UTC"), "status": "active"},
        ]
    uptime = timedelta()
    downtime = timedelta()
    for i in range(len(points) - 1):
        t1 = parse_utc(points[i]["timestamp_utc"])
        t2 = parse_utc(points[i+1]["timestamp_utc"])
        delta = t2 - t1
        if points[i]["status"] == "active":
            uptime += delta
        else:
            downtime += delta
    return uptime, downtime