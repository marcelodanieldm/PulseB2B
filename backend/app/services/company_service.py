from app.models.company import Company
from app.schemas.company import CompanySchema
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from typing import List

# Example service for company data
class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def get_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        return self.db.query(Company).offset(skip).limit(limit).all()

    def get_company(self, company_id: int) -> Company:
        return self.db.query(Company).filter(Company.id == company_id).first()

    def create_company(self, company: CompanySchema) -> Company:
        db_company = Company(**company.dict())
        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company
