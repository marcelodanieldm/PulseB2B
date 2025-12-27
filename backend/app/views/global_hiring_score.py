from fastapi import APIRouter, Query
from typing import Optional
from app.services.global_hiring_score_service import GlobalHiringScoreCalculator

router = APIRouter(prefix="/global-hiring-score", tags=["Global Hiring Score"])

calculator = GlobalHiringScoreCalculator()

@router.get("/calculate", summary="Calcular Global Hiring Score (GHS)")
def calculate_ghs(
    funding_amount: float = Query(..., description="Total funding (USD)"),
    company_stage: str = Query("series_a", description="Etapa de funding"),
    urgency_level: str = Query("standard", description="Nivel de urgencia"),
    stated_headcount_goal: Optional[int] = Query(None, description="Meta de contrataciones"),
    current_team_size: Optional[int] = Query(None, description="Tamaño actual del equipo")
):
    """Calcula el Global Hiring Score y la recomendación de offshore hiring."""
    return calculator.calculate_ghs(
        funding_amount=funding_amount,
        company_stage=company_stage,
        urgency_level=urgency_level,
        stated_headcount_goal=stated_headcount_goal,
        current_team_size=current_team_size
    )

@router.get("/roi", summary="Calcular ROI de offshore hiring")
def calculate_roi(
    team_size: int = Query(..., description="Tamaño total del equipo"),
    offshore_percentage: float = Query(..., description="% offshore (0-100)"),
    project_duration_months: int = Query(12, description="Duración del proyecto en meses")
):
    """Calcula el ROI de una estrategia de offshore hiring."""
    return calculator.calculate_roi_offshore(
        team_size=team_size,
        offshore_percentage=offshore_percentage,
        project_duration_months=project_duration_months
    )
