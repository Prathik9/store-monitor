from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from datetime import datetime, timedelta
from app.db.mongo import db
from app.models.report import ReportStatus
from app.utils.csv_utils import compute_report
from app.config import REPORTS_DIR

def get_latest_timestamp():
    obs = db["status"].find({}, {"timestamp_utc": 1})
    latest = max(
        (datetime.strptime(x["timestamp_utc"], "%Y-%m-%d %H:%M:%S UTC") for x in obs),
        default=None,
    )
    return latest

def generate_report_task(report_id):
    try:
        db["reports"].update_one({"report_id": report_id}, {"$set": {"status": "Running"}}, upsert=True)
        now_utc = get_latest_timestamp()
        path = f"{REPORTS_DIR}/{report_id}.csv"
        compute_report(now_utc, path)
        db["reports"].update_one(
            {"report_id": report_id},
            {"$set": {"status": "Complete", "csv_file": path}},
        )
    except Exception as e:
        db["reports"].update_one(
            {"report_id": report_id},
            {"$set": {"status": "Error", "error": str(e)}},
        )

def trigger_report(background_tasks: BackgroundTasks):
    report_id = str(uuid4())
    db["reports"].insert_one({"report_id": report_id, "status": "Running"})
    background_tasks.add_task(generate_report_task, report_id)
    return ReportStatus(status="Running", report_id=report_id)

def get_report(report_id: str):
    report = db["reports"].find_one({"report_id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if report["status"] == "Complete":
        return FileResponse(report["csv_file"], media_type='text/csv', filename=f"{report_id}.csv")
    return ReportStatus(status=report["status"], report_id=report_id)