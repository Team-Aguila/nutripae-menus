from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from typing import List
from pydantic import BaseModel, Field

from pae_menus.models.nutritional_analysis import (
    NutritionalAnalysisReport,
    SimplifiedNutritionalSummary,
    NutritionalRequirements,
    NutritionalComparisonReport
)
from pae_menus.services.nutritional_analysis_service import NutritionalAnalysisService

router = APIRouter(prefix="/nutritional-analysis", tags=["Nutritional Analysis"])


@router.get(
    "/schedule/{schedule_id}",
    response_model=NutritionalAnalysisReport,
    summary="Get comprehensive nutritional analysis for a menu schedule",
    description="Generate a detailed nutritional analysis report for a specific menu schedule."
)
async def get_nutritional_analysis(schedule_id: str) -> NutritionalAnalysisReport:
    """
    Get comprehensive nutritional analysis for a menu schedule.
    
    This endpoint provides detailed nutritional analysis including:
    - Food group summaries (grains, legumes, dairy, fruits, vegetables, protein)
    - Major nutrient totals (energy, protein, vitamins, minerals)
    - Daily and location-specific breakdowns
    - Overall summary across all locations and dates
    
    Perfect for nutritionists to validate that planned menus adequately cover nutritional requirements.
    """
    try:
        return await NutritionalAnalysisService.analyze_menu_schedule(schedule_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating nutritional analysis: {str(e)}"
        )


@router.get(
    "/schedule/{schedule_id}/summary",
    response_model=SimplifiedNutritionalSummary,
    summary="Get simplified nutritional summary for quick overview",
    description="Get a simplified nutritional summary perfect for dashboard views."
)
async def get_nutritional_summary(schedule_id: str) -> SimplifiedNutritionalSummary:
    """
    Get simplified nutritional summary for quick overview.
    
    This endpoint provides a condensed view of nutritional information including:
    - Food group serving counts
    - Average daily nutrients per person
    - Quality scores (nutrition, balance, variety)
    - Key metrics for quick assessment
    
    Perfect for dashboard views and quick nutritional validation.
    """
    try:
        return await NutritionalAnalysisService.get_simplified_summary(schedule_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating nutritional summary: {str(e)}"
        )


@router.post(
    "/schedule/{schedule_id}/compare",
    response_model=NutritionalComparisonReport,
    summary="Compare nutritional analysis with requirements",
    description="Compare the nutritional content of a menu schedule against specific nutritional requirements."
)
async def compare_with_requirements(
    schedule_id: str,
    requirements: NutritionalRequirements = Body(..., description="Nutritional requirements to compare against")
) -> NutritionalComparisonReport:
    """
    Compare nutritional analysis with specific requirements.
    
    This endpoint allows nutritionists to compare the planned menu against specific
    nutritional requirements for their target population.
    """
    try:
        # Get the full analysis
        analysis = await NutritionalAnalysisService.analyze_menu_schedule(schedule_id)
        
        # Calculate daily averages
        total_person_days = analysis.total_days * len(analysis.locations)
        if total_person_days == 0:
            total_person_days = 1  # Prevent division by zero
        
        daily_avg_calories = analysis.overall_summary.total_calories / total_person_days
        daily_avg_protein = analysis.overall_summary.total_protein / total_person_days
        daily_avg_carbs = analysis.overall_summary.total_carbohydrates / total_person_days
        daily_avg_fat = analysis.overall_summary.total_fat / total_person_days
        daily_avg_fiber = analysis.overall_summary.total_fiber / total_person_days
        daily_avg_sodium = analysis.overall_summary.total_sodium / total_person_days
        daily_avg_calcium = analysis.overall_summary.total_calcium / total_person_days
        daily_avg_iron = analysis.overall_summary.total_iron / total_person_days
        daily_avg_vitamin_c = analysis.overall_summary.total_vitamin_c / total_person_days
        daily_avg_vitamin_a = analysis.overall_summary.total_vitamin_a / total_person_days
        
        # Calculate compliance percentages
        compliance = {
            "calories": (daily_avg_calories / requirements.daily_calories * 100) if requirements.daily_calories > 0 else 0,
            "protein": (daily_avg_protein / requirements.daily_protein * 100) if requirements.daily_protein > 0 else 0,
            "carbohydrates": (daily_avg_carbs / requirements.daily_carbohydrates * 100) if requirements.daily_carbohydrates > 0 else 0,
            "fat": (daily_avg_fat / requirements.daily_fat * 100) if requirements.daily_fat > 0 else 0,
            "fiber": (daily_avg_fiber / requirements.daily_fiber * 100) if requirements.daily_fiber > 0 else 0,
            "sodium": (daily_avg_sodium / requirements.daily_sodium * 100) if requirements.daily_sodium > 0 else 0,
            "calcium": (daily_avg_calcium / requirements.daily_calcium * 100) if requirements.daily_calcium > 0 else 0,
            "iron": (daily_avg_iron / requirements.daily_iron * 100) if requirements.daily_iron > 0 else 0,
            "vitamin_c": (daily_avg_vitamin_c / requirements.daily_vitamin_c * 100) if requirements.daily_vitamin_c > 0 else 0,
            "vitamin_a": (daily_avg_vitamin_a / requirements.daily_vitamin_a * 100) if requirements.daily_vitamin_a > 0 else 0,
        }
        
        # Generate recommendations
        recommendations = []
        coverage_gaps = []
        
        for nutrient, percentage in compliance.items():
            if percentage < 80:  # Less than 80% of requirement
                coverage_gaps.append(f"{nutrient.title()} is only {percentage:.1f}% of required amount")
                if percentage < 50:
                    recommendations.append(f"Significantly increase {nutrient.replace('_', ' ')} content in menus")
                else:
                    recommendations.append(f"Moderately increase {nutrient.replace('_', ' ')} content in menus")
            elif percentage > 150:  # More than 150% of requirement
                if nutrient == "sodium":
                    recommendations.append(f"Consider reducing sodium content ({percentage:.1f}% of limit)")
                elif nutrient == "fat":
                    recommendations.append(f"Consider reducing fat content ({percentage:.1f}% of recommendation)")
        
        return NutritionalComparisonReport(
            analysis_report=analysis,
            requirements=requirements,
            compliance_percentage=compliance,
            recommendations=recommendations,
            coverage_gaps=coverage_gaps
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing with requirements: {str(e)}"
        )


@router.get(
    "/",
    summary="Get nutritional analysis endpoints information",
    description="Get information about available nutritional analysis endpoints."
)
async def get_nutritional_analysis_info() -> JSONResponse:
    """Get information about available nutritional analysis endpoints."""
    info = {
        "title": "Nutritional Analysis API",
        "description": "Comprehensive nutritional analysis for menu schedules",
        "features": [
            "Food group analysis (grains, legumes, dairy, fruits, vegetables, protein)",
            "Major nutrient calculation (energy, protein, vitamins, minerals)",
            "Daily and location-specific breakdowns",
            "Simplified summaries for quick overview",
            "Comparison with nutritional requirements",
            "Recommendations for improvement"
        ],
        "endpoints": {
            "GET /schedule/{schedule_id}": "Get comprehensive nutritional analysis",
            "GET /schedule/{schedule_id}/summary": "Get simplified nutritional summary",
            "POST /schedule/{schedule_id}/compare": "Compare with nutritional requirements"
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=info
    )


class NutritionalRequirementsPreset(BaseModel):
    """Predefined nutritional requirements for common populations"""
    name: str = Field(..., description="Name of the requirements preset")
    description: str = Field(..., description="Description of the target population")
    requirements: NutritionalRequirements = Field(..., description="Nutritional requirements")


@router.get(
    "/requirements/presets",
    response_model=List[NutritionalRequirementsPreset],
    summary="Get predefined nutritional requirements",
    description="Get a list of predefined nutritional requirements for common populations."
)
async def get_nutritional_requirements_presets() -> List[NutritionalRequirementsPreset]:
    """Get predefined nutritional requirements for common populations."""
    presets = [
        NutritionalRequirementsPreset(
            name="Adult General Population",
            description="General nutritional requirements for healthy adults (18-50 years)",
            requirements=NutritionalRequirements(
                daily_calories=2000,
                daily_protein=50,
                daily_carbohydrates=225,
                daily_fat=65,
                daily_fiber=25,
                daily_sodium=2300,
                daily_calcium=1000,
                daily_iron=18,
                daily_vitamin_c=90,
                daily_vitamin_a=3000,
                target_population="Adults 18-50 years"
            )
        ),
        NutritionalRequirementsPreset(
            name="School Age Children",
            description="Nutritional requirements for school-age children (6-12 years)",
            requirements=NutritionalRequirements(
                daily_calories=1800,
                daily_protein=35,
                daily_carbohydrates=200,
                daily_fat=50,
                daily_fiber=20,
                daily_sodium=1900,
                daily_calcium=800,
                daily_iron=10,
                daily_vitamin_c=75,
                daily_vitamin_a=2500,
                target_population="Children 6-12 years"
            )
        ),
        NutritionalRequirementsPreset(
            name="Elderly Population",
            description="Nutritional requirements for elderly adults (65+ years)",
            requirements=NutritionalRequirements(
                daily_calories=1800,
                daily_protein=60,
                daily_carbohydrates=180,
                daily_fat=55,
                daily_fiber=30,
                daily_sodium=1500,
                daily_calcium=1200,
                daily_iron=15,
                daily_vitamin_c=100,
                daily_vitamin_a=3500,
                target_population="Adults 65+ years"
            )
        )
    ]
    
    return presets 