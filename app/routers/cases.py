from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[schemas.CaseOut])
def list_cases(
    status: models.CaseStatus | None = None,
    claimedBy: str | None = None,
    db: Session = Depends(get_db),
):
    cases = crud.list_cases(db, status=status, claimed_by=claimedBy)
    return [crud.case_to_out(c) for c in cases]


@router.get("/{case_id}", response_model=schemas.CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return crud.case_to_out(case)


@router.post("/{case_id}/claim", response_model=schemas.CaseOut)
def claim_case(case_id: int, body: schemas.ClaimRequest, db: Session = Depends(get_db)):
    try:
        case = crud.claim_case(db, case_id, body.claimedBy)
    except crud.ApiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return crud.case_to_out(case)


@router.post("/{case_id}/report", response_model=schemas.CaseOut)
def submit_report(case_id: int, body: schemas.ReportRequest, db: Session = Depends(get_db)):
    try:
        case = crud.submit_report(db, case_id, body.author, body.report)
    except crud.ApiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return crud.case_to_out(case)
