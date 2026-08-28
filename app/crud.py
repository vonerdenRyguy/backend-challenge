from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import models, schemas


def case_to_out(case: models.Case) -> schemas.CaseOut:
    return schemas.CaseOut(
        id=case.id,
        patientName=case.patient_name,
        modality=case.modality,
        studyDate=case.study_date,
        status=case.status,
        report=case.report,
        claimedAt=case.claimed_at,
        claimedBy=case.claimed_by.username if case.claimed_by else None,
    )


def employee_to_out(employee: models.Employee) -> schemas.EmployeeOut:
    return schemas.EmployeeOut(id=employee.id, username=employee.username)


def get_employee_by_username(db: Session, username: str) -> models.Employee | None:
    return db.query(models.Employee).filter(models.Employee.username == username).first()


def list_cases(
    db: Session, status: models.CaseStatus | None = None, claimed_by: str | None = None
) -> list[models.Case]:
    query = db.query(models.Case)

    if status is not None:
        query = query.filter(models.Case.status == status)

    if claimed_by is not None:
        employee = get_employee_by_username(db, claimed_by)
        if employee is None:
            return []
        query = query.filter(models.Case.claimed_by_id == employee.id)

    return query.order_by(models.Case.study_date.asc()).all()


def get_case(db: Session, case_id: int) -> models.Case | None:
    return db.get(models.Case, case_id)


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def claim_case(db: Session, case_id: int, username: str | None) -> models.Case:
    case = get_case(db, case_id)
    if case is None:
        raise ApiError(404, "Case not found")

    if not username or not username.strip():
        raise ApiError(400, "claimedBy username is required")

    employee = get_employee_by_username(db, username)
    if employee is None:
        raise ApiError(400, f"No employee found with username '{username}'")

    if case.status != models.CaseStatus.PENDING:
        raise ApiError(409, f"Case is not PENDING (current status: {case.status.value})")

    case.status = models.CaseStatus.IN_PROGRESS
    case.claimed_at = datetime.now(timezone.utc)
    case.claimed_by_id = employee.id
    db.commit()
    db.refresh(case)
    return case


def submit_report(
    db: Session, case_id: int, author_username: str | None, report_text: str | None
) -> models.Case:
    case = get_case(db, case_id)
    if case is None:
        raise ApiError(404, "Case not found")

    if not author_username or not author_username.strip():
        raise ApiError(400, "author username is required")

    employee = get_employee_by_username(db, author_username)
    if employee is None:
        raise ApiError(400, f"No employee found with username '{author_username}'")

    if not report_text or not report_text.strip():
        raise ApiError(400, "report text is required")

    if case.status != models.CaseStatus.IN_PROGRESS:
        raise ApiError(409, f"Case is not IN_PROGRESS (current status: {case.status.value})")

    if case.claimed_by_id != employee.id:
        raise ApiError(403, "Only the employee who claimed this case may submit its report")

    case.status = models.CaseStatus.COMPLETED
    case.report = report_text
    db.commit()
    db.refresh(case)
    return case


def list_employees(db: Session) -> list[models.Employee]:
    return db.query(models.Employee).order_by(models.Employee.id.asc()).all()


def create_employee(db: Session, username: str | None) -> models.Employee:
    if not username or not username.strip():
        raise ApiError(400, "username is required")
    if get_employee_by_username(db, username) is not None:
        raise ApiError(409, f"username '{username}' is already taken")
    employee = models.Employee(username=username)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee_id: int, username: str | None) -> models.Employee:
    employee = db.get(models.Employee, employee_id)
    if employee is None:
        raise ApiError(404, "Employee not found")
    if not username or not username.strip():
        raise ApiError(400, "username is required")
    existing = get_employee_by_username(db, username)
    if existing is not None and existing.id != employee_id:
        raise ApiError(409, f"username '{username}' is already taken")
    employee.username = username
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee_id: int, force: bool) -> None:
    employee = db.get(models.Employee, employee_id)
    if employee is None:
        raise ApiError(404, "Employee not found")

    linked_case_ids = [
        case_id
        for (case_id,) in db.query(models.Case.id)
        .filter(models.Case.claimed_by_id == employee_id)
        .all()
    ]

    if linked_case_ids and not force:
        raise ApiError(
            409,
            "Employee has claimed case(s) "
            f"{linked_case_ids}. Pass ?force=true to delete anyway "
            "(those cases will have claimedBy cleared).",
        )

    if linked_case_ids:
        db.query(models.Case).filter(models.Case.claimed_by_id == employee_id).update(
            {models.Case.claimed_by_id: None}
        )

    db.delete(employee)
    db.commit()
