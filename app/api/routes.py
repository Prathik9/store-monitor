from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
from app.models.report import ReportStatus
from app.services.report_service import trigger_report, get_report

router = APIRouter()

@router.post("/trigger_report", response_model=ReportStatus)
def trigger_report_endpoint(background_tasks: BackgroundTasks):
    return trigger_report(background_tasks)

@router.get("/get_report", response_model=ReportStatus)
def get_report_endpoint(report_id: str):
    file_or_status = get_report(report_id)
    if isinstance(file_or_status, FileResponse):
        return file_or_status
    return file_or_status