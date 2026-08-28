import enum

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Modality(str, enum.Enum):
    CT = "CT"
    MRI = "MRI"
    XR = "XR"
    US = "US"


class CaseStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    cases: Mapped[list["Case"]] = relationship(back_populates="claimed_by")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_name: Mapped[str] = mapped_column(String, nullable=False)
    modality: Mapped[Modality] = mapped_column(Enum(Modality), nullable=False)
    study_date: Mapped["Date"] = mapped_column(Date, nullable=False)
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus), nullable=False, default=CaseStatus.PENDING
    )
    report: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    claimed_at: Mapped["DateTime | None"] = mapped_column(DateTime, nullable=True, default=None)
    claimed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True, default=None
    )

    claimed_by: Mapped["Employee | None"] = relationship(back_populates="cases")
