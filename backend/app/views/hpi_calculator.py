
"""FastAPI router for HPI Calculator endpoints."""

from fastapi import APIRouter, UploadFile, File
from typing import Dict, Any
import pandas as pd
from ..services.hpi_calculator_service import hpi_calculator

router = APIRouter(prefix="/hpi", tags=["Hiring Potential Index"])

@router.post("/calculate", response_model=Dict[str, Any])
def calculate_hpi(company_data: Dict[str, Any]):
    """Calculate HPI for a single company."""
    return hpi_calculator.calculate_hpi(company_data)

@router.post("/batch-calculate")
def batch_calculate_hpi(file: UploadFile = File(...)):
    """Batch calculate HPI for companies from uploaded CSV file."""
    df = pd.read_csv(file.file)
    results_df = hpi_calculator.batch_calculate(df)
    return results_df.to_dict(orient="records")

@router.post("/summary-stats")
def hpi_summary_stats(file: UploadFile = File(...)):
    """Generate summary statistics for HPI results from uploaded CSV file."""
    df = pd.read_csv(file.file)
    results_df = hpi_calculator.batch_calculate(df)
    return hpi_calculator.generate_summary_stats(results_df)
