from pydantic import BaseModel
from typing import Optional

class ReportStatus(BaseModel):
    status: str
    report_id: str
    csv_file: Optional[str] = None