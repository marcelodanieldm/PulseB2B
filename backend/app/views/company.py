from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.company_service import CompanyService
from app.schemas.company import CompanySchema
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/companies", response_model=List[CompanySchema])
def list_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = CompanyService(db)
    return service.get_companies(skip=skip, limit=limit)

@router.get("/companies/{company_id}", response_model=CompanySchema)
def get_company(company_id: int, db: Session = Depends(get_db)):
    service = CompanyService(db)
    company = service.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
