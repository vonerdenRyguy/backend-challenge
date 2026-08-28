from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app import models


def seed_if_empty(db: Session) -> None:
    if db.query(models.Employee).first() is not None:
        return

    jsmith = models.Employee(username="jsmith")
    agupta = models.Employee(username="agupta")
    mchen = models.Employee(username="mchen")
    db.add_all([jsmith, agupta, mchen])
    db.flush()

    cases = [
        models.Case(
            patient_name="Jane Smith",
            modality=models.Modality.CT,
            study_date=date(2024, 11, 1),
            status=models.CaseStatus.PENDING,
        ),
        models.Case(
            patient_name="Robert Lee",
            modality=models.Modality.MRI,
            study_date=date(2024, 11, 2),
            status=models.CaseStatus.PENDING,
        ),
        models.Case(
            patient_name="Maria Gomez",
            modality=models.Modality.XR,
            study_date=date(2024, 11, 3),
            status=models.CaseStatus.PENDING,
        ),
        models.Case(
            patient_name="David Kim",
            modality=models.Modality.US,
            study_date=date(2024, 11, 4),
            status=models.CaseStatus.PENDING,
        ),
        models.Case(
            patient_name="Alice Brown",
            modality=models.Modality.CT,
            study_date=date(2024, 11, 5),
            status=models.CaseStatus.IN_PROGRESS,
            claimed_at=datetime(2024, 11, 5, 9, 30, tzinfo=timezone.utc),
            claimed_by_id=jsmith.id,
        ),
        models.Case(
            patient_name="Tom Nguyen",
            modality=models.Modality.MRI,
            study_date=date(2024, 11, 6),
            status=models.CaseStatus.IN_PROGRESS,
            claimed_at=datetime(2024, 11, 6, 10, 15, tzinfo=timezone.utc),
            claimed_by_id=agupta.id,
        ),
        models.Case(
            patient_name="Emily Davis",
            modality=models.Modality.XR,
            study_date=date(2024, 11, 7),
            status=models.CaseStatus.COMPLETED,
            claimed_at=datetime(2024, 11, 7, 8, 0, tzinfo=timezone.utc),
            claimed_by_id=mchen.id,
            report="Findings are consistent with a mild fracture of the distal radius.",
        ),
        models.Case(
            patient_name="Michael Johnson",
            modality=models.Modality.CT,
            study_date=date(2024, 11, 8),
            status=models.CaseStatus.COMPLETED,
            claimed_at=datetime(2024, 11, 8, 13, 45, tzinfo=timezone.utc),
            claimed_by_id=jsmith.id,
            report="No acute intracranial abnormality identified.",
        ),
    ]
    db.add_all(cases)
    db.commit()
