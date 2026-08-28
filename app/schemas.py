from datetime import date, datetime

from pydantic import BaseModel

from app.models import CaseStatus, Modality


class EmployeeCreate(BaseModel):
    username: str


class EmployeeUpdate(BaseModel):
    username: str


class EmployeeOut(BaseModel):
    id: int
    username: str


class CaseOut(BaseModel):
    id: int
    patientName: str
    modality: Modality
    studyDate: date
    status: CaseStatus
    report: str | None
    claimedAt: datetime | None
    claimedBy: str | None


class ClaimRequest(BaseModel):
    claimedBy: str | None = None


class ReportRequest(BaseModel):
    author: str | None = None
    report: str | None = None
