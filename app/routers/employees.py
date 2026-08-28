from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[schemas.EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return [crud.employee_to_out(e) for e in crud.list_employees(db)]


@router.post("", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(body: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    try:
        employee = crud.create_employee(db, body.username)
    except crud.ApiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return crud.employee_to_out(employee)


@router.put("/{employee_id}", response_model=schemas.EmployeeOut)
def update_employee(employee_id: int, body: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    try:
        employee = crud.update_employee(db, employee_id, body.username)
    except crud.ApiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return crud.employee_to_out(employee)


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, force: bool = False, db: Session = Depends(get_db)):
    try:
        crud.delete_employee(db, employee_id, force=force)
    except crud.ApiError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
