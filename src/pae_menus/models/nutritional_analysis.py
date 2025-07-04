from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date as Date
from enum import Enum
from .dish import DishType


class FoodGroupSummary(BaseModel):
    """Summary of servings by food group"""
    food_group: DishType = Field(..., description="Food group type")
    total_servings: int = Field(0, description="Total number of servings")
    dish_count: int = Field(0, description="Number of different dishes")
    dish_names: List[str] = Field(default=[], description="Names of dishes in this group")


class NutrientSummary(BaseModel):
    """Summary of major nutrients"""
    total_calories: float = Field(0.0, description="Total calories")
    total_protein: float = Field(0.0, description="Total protein (grams)")
    total_carbohydrates: float = Field(0.0, description="Total carbohydrates (grams)")
    total_fat: float = Field(0.0, description="Total fat (grams)")
    total_fiber: float = Field(0.0, description="Total fiber (grams)")
    total_sodium: float = Field(0.0, description="Total sodium (mg)")
    total_calcium: float = Field(0.0, description="Total calcium (mg)")
    total_iron: float = Field(0.0, description="Total iron (mg)")
    total_vitamin_c: float = Field(0.0, description="Total vitamin C (mg)")
    total_vitamin_a: float = Field(0.0, description="Total vitamin A (IU)")


class DailyNutritionalSummary(BaseModel):
    """Nutritional summary for a specific day"""
    date: Date = Field(..., description="Date of the nutritional summary")
    cycle_day: int = Field(..., description="Day number in the menu cycle")
    food_groups: List[FoodGroupSummary] = Field(default=[], description="Food group summaries")
    nutrients: NutrientSummary = Field(..., description="Nutrient totals")
    total_dishes: int = Field(0, description="Total number of dishes")
    total_servings: int = Field(0, description="Total number of servings across all meals")


class LocationNutritionalSummary(BaseModel):
    """Nutritional summary for a specific location"""
    location_id: str = Field(..., description="Location ID")
    location_name: str = Field(..., description="Location name")
    location_type: str = Field(..., description="Location type (campus or town)")
    daily_summaries: List[DailyNutritionalSummary] = Field(default=[], description="Daily nutritional summaries")
    period_totals: NutrientSummary = Field(..., description="Total nutrients for the entire period")
    period_food_groups: List[FoodGroupSummary] = Field(default=[], description="Food group summaries for the entire period")


class NutritionalAnalysisReport(BaseModel):
    """Complete nutritional analysis report for scheduled menus"""
    schedule_id: str = Field(..., description="Menu schedule ID")
    menu_cycle_name: str = Field(..., description="Menu cycle name")
    start_date: Date = Field(..., description="Start date of the analysis period")
    end_date: Date = Field(..., description="End date of the analysis period")
    total_days: int = Field(..., description="Total number of days analyzed")
    locations: List[LocationNutritionalSummary] = Field(default=[], description="Nutritional summaries by location")
    overall_summary: NutrientSummary = Field(..., description="Overall nutrient totals across all locations and dates")
    overall_food_groups: List[FoodGroupSummary] = Field(default=[], description="Overall food group summaries")
    analysis_date: Date = Field(..., description="Date when this analysis was generated")


class NutritionalRequirements(BaseModel):
    """Nutritional requirements for comparison"""
    daily_calories: float = Field(..., description="Daily caloric requirement")
    daily_protein: float = Field(..., description="Daily protein requirement (grams)")
    daily_carbohydrates: float = Field(..., description="Daily carbohydrate requirement (grams)")
    daily_fat: float = Field(..., description="Daily fat requirement (grams)")
    daily_fiber: float = Field(..., description="Daily fiber requirement (grams)")
    daily_sodium: float = Field(..., description="Daily sodium limit (mg)")
    daily_calcium: float = Field(..., description="Daily calcium requirement (mg)")
    daily_iron: float = Field(..., description="Daily iron requirement (mg)")
    daily_vitamin_c: float = Field(..., description="Daily vitamin C requirement (mg)")
    daily_vitamin_a: float = Field(..., description="Daily vitamin A requirement (IU)")
    target_population: str = Field(..., description="Target population for these requirements")


class NutritionalComparisonReport(BaseModel):
    """Nutritional analysis report with requirements comparison"""
    analysis_report: NutritionalAnalysisReport = Field(..., description="Base nutritional analysis")
    requirements: NutritionalRequirements = Field(..., description="Nutritional requirements for comparison")
    compliance_percentage: Dict[str, float] = Field(default={}, description="Percentage compliance with requirements")
    recommendations: List[str] = Field(default=[], description="Recommendations for improvement")
    coverage_gaps: List[str] = Field(default=[], description="Areas where nutritional coverage is insufficient")


class SimplifiedNutritionalSummary(BaseModel):
    """Simplified nutritional summary for quick overview"""
    schedule_id: str = Field(..., description="Menu schedule ID")
    menu_cycle_name: str = Field(..., description="Menu cycle name")
    period: str = Field(..., description="Analysis period (e.g., '2024-01-01 to 2024-01-07')")
    total_locations: int = Field(..., description="Number of locations covered")
    
    # Food group breakdown
    grains_servings: int = Field(0, description="Total servings of grains/cereals")
    proteins_servings: int = Field(0, description="Total servings of proteins")
    vegetables_servings: int = Field(0, description="Total servings of vegetables")
    fruits_servings: int = Field(0, description="Total servings of fruits")
    dairy_servings: int = Field(0, description="Total servings of dairy")
    other_servings: int = Field(0, description="Total servings of other foods")
    
    # Key nutrients (daily averages)
    avg_daily_calories: float = Field(0.0, description="Average daily calories per person")
    avg_daily_protein: float = Field(0.0, description="Average daily protein per person (grams)")
    avg_daily_carbs: float = Field(0.0, description="Average daily carbohydrates per person (grams)")
    avg_daily_fat: float = Field(0.0, description="Average daily fat per person (grams)")
    
    # Quality indicators
    nutrition_score: float = Field(0.0, description="Overall nutrition score (0-100)")
    balance_score: float = Field(0.0, description="Food group balance score (0-100)")
    variety_score: float = Field(0.0, description="Dish variety score (0-100)") 