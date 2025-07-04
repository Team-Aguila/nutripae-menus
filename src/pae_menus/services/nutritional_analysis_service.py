from typing import List, Dict, Optional
from datetime import date as Date, datetime
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from collections import defaultdict

from pae_menus.models.menu_schedule import MenuSchedule
from pae_menus.models.menu_cycle import MenuCycle
from pae_menus.models.dish import Dish, DishType
from pae_menus.models.nutritional_analysis import (
    NutritionalAnalysisReport,
    LocationNutritionalSummary,
    DailyNutritionalSummary,
    FoodGroupSummary,
    NutrientSummary,
    SimplifiedNutritionalSummary,
    NutritionalRequirements,
    NutritionalComparisonReport
)


class NutritionalAnalysisService:
    """Service for nutritional analysis of scheduled menus"""

    @staticmethod
    async def analyze_menu_schedule(schedule_id: str) -> NutritionalAnalysisReport:
        """
        Analyze a menu schedule and generate a complete nutritional report
        
        Args:
            schedule_id: ID of the menu schedule to analyze
            
        Returns:
            NutritionalAnalysisReport: Complete nutritional analysis report
        """
        try:
            # Get the menu schedule
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )
            
            # Get the menu cycle
            menu_cycle = await MenuCycle.get(schedule.menu_cycle_id)
            if not menu_cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu cycle not found for schedule '{schedule_id}'"
                )
            
            # Calculate date range
            schedule_dates = []
            current_date = schedule.start_date
            while current_date <= schedule.end_date:
                schedule_dates.append(current_date)
                current_date = current_date.replace(day=current_date.day + 1)
            
            # Analyze each location
            location_summaries = []
            overall_nutrients = NutrientSummary()
            overall_food_groups = defaultdict(lambda: {"servings": 0, "dishes": 0, "dish_names": set()})
            
            for location_coverage in schedule.coverage:
                location_summary = await NutritionalAnalysisService._analyze_location(
                    location_coverage, schedule_dates, menu_cycle
                )
                location_summaries.append(location_summary)
                
                # Accumulate overall totals
                overall_nutrients = NutritionalAnalysisService._add_nutrients(
                    overall_nutrients, location_summary.period_totals
                )
                
                # Accumulate food groups
                for fg in location_summary.period_food_groups:
                    overall_food_groups[fg.food_group]["servings"] += fg.total_servings
                    overall_food_groups[fg.food_group]["dishes"] += fg.dish_count
                    overall_food_groups[fg.food_group]["dish_names"].update(fg.dish_names)
            
            # Convert food groups to list
            overall_food_groups_list = []
            for food_group, data in overall_food_groups.items():
                overall_food_groups_list.append(FoodGroupSummary(
                    food_group=food_group,
                    total_servings=data["servings"],
                    dish_count=data["dishes"],
                    dish_names=list(data["dish_names"])
                ))
            
            return NutritionalAnalysisReport(
                schedule_id=schedule_id,
                menu_cycle_name=menu_cycle.name,
                start_date=schedule.start_date,
                end_date=schedule.end_date,
                total_days=len(schedule_dates),
                locations=location_summaries,
                overall_summary=overall_nutrients,
                overall_food_groups=overall_food_groups_list,
                analysis_date=Date.today()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing menu schedule: {str(e)}"
            )

    @staticmethod
    async def _analyze_location(location_coverage, schedule_dates: List[Date], menu_cycle) -> LocationNutritionalSummary:
        """Analyze nutritional content for a specific location"""
        daily_summaries = []
        period_nutrients = NutrientSummary()
        period_food_groups = defaultdict(lambda: {"servings": 0, "dishes": set(), "dish_names": set()})
        
        for schedule_date in schedule_dates:
            # Calculate which day of the cycle this date corresponds to
            days_since_start = (schedule_date - schedule_dates[0]).days
            cycle_day = (days_since_start % menu_cycle.duration_days) + 1
            
            # Find the daily menu for this cycle day
            daily_menu = None
            for dm in menu_cycle.daily_menus:
                if dm.day == cycle_day:
                    daily_menu = dm
                    break
            
            if daily_menu:
                # Get all dish IDs for this day
                all_dish_ids = (
                    daily_menu.breakfast_dish_ids + 
                    daily_menu.lunch_dish_ids + 
                    daily_menu.snack_dish_ids
                )
                
                # Get dish details
                dishes = await Dish.find({"_id": {"$in": all_dish_ids}}).to_list()
                
                # Calculate daily nutritional summary
                daily_summary = await NutritionalAnalysisService._calculate_daily_summary(
                    schedule_date, cycle_day, dishes
                )
                daily_summaries.append(daily_summary)
                
                # Accumulate period totals
                period_nutrients = NutritionalAnalysisService._add_nutrients(
                    period_nutrients, daily_summary.nutrients
                )
                
                # Accumulate food groups
                for fg in daily_summary.food_groups:
                    period_food_groups[fg.food_group]["servings"] += fg.total_servings
                    period_food_groups[fg.food_group]["dishes"] += fg.dish_count
                    period_food_groups[fg.food_group]["dish_names"].update(fg.dish_names)
        
        # Convert food groups to list
        period_food_groups_list = []
        for food_group, data in period_food_groups.items():
            period_food_groups_list.append(FoodGroupSummary(
                food_group=food_group,
                total_servings=data["servings"],
                dish_count=data["dishes"],
                dish_names=list(data["dish_names"])
            ))
        
        return LocationNutritionalSummary(
            location_id=location_coverage.location_id,
            location_name=location_coverage.location_name,
            location_type=location_coverage.location_type.value,
            daily_summaries=daily_summaries,
            period_totals=period_nutrients,
            period_food_groups=period_food_groups_list
        )

    @staticmethod
    async def _calculate_daily_summary(schedule_date: Date, cycle_day: int, dishes: List[Dish]) -> DailyNutritionalSummary:
        """Calculate nutritional summary for a single day"""
        nutrients = NutrientSummary()
        food_groups = defaultdict(lambda: {"servings": 0, "dishes": set(), "dish_names": set()})
        
        for dish in dishes:
            # Add nutritional information
            if dish.nutritional_info:
                nutrients.total_calories += dish.nutritional_info.calories or 0
                nutrients.total_protein += dish.nutritional_info.protein or 0
                nutrients.total_carbohydrates += dish.nutritional_info.carbohydrates or 0
                nutrients.total_fat += dish.nutritional_info.fat or 0
                nutrients.total_fiber += dish.nutritional_info.fiber or 0
                nutrients.total_sodium += dish.nutritional_info.sodium or 0
                nutrients.total_calcium += dish.nutritional_info.calcium or 0
                nutrients.total_iron += dish.nutritional_info.iron or 0
                nutrients.total_vitamin_c += dish.nutritional_info.vitamin_c or 0
                nutrients.total_vitamin_a += dish.nutritional_info.vitamin_a or 0
            
            # Add food group information
            dish_type = dish.dish_type if hasattr(dish, 'dish_type') and dish.dish_type else DishType.OTHER
            food_groups[dish_type]["servings"] += 1
            food_groups[dish_type]["dishes"].add(dish.id)
            food_groups[dish_type]["dish_names"].add(dish.name)
        
        # Convert food groups to list
        food_groups_list = []
        for food_group, data in food_groups.items():
            food_groups_list.append(FoodGroupSummary(
                food_group=food_group,
                total_servings=data["servings"],
                dish_count=len(data["dishes"]),
                dish_names=list(data["dish_names"])
            ))
        
        return DailyNutritionalSummary(
            date=schedule_date,
            cycle_day=cycle_day,
            food_groups=food_groups_list,
            nutrients=nutrients,
            total_dishes=len(dishes),
            total_servings=sum(fg.total_servings for fg in food_groups_list)
        )

    @staticmethod
    def _add_nutrients(base: NutrientSummary, addition: NutrientSummary) -> NutrientSummary:
        """Add two nutrient summaries together"""
        return NutrientSummary(
            total_calories=base.total_calories + addition.total_calories,
            total_protein=base.total_protein + addition.total_protein,
            total_carbohydrates=base.total_carbohydrates + addition.total_carbohydrates,
            total_fat=base.total_fat + addition.total_fat,
            total_fiber=base.total_fiber + addition.total_fiber,
            total_sodium=base.total_sodium + addition.total_sodium,
            total_calcium=base.total_calcium + addition.total_calcium,
            total_iron=base.total_iron + addition.total_iron,
            total_vitamin_c=base.total_vitamin_c + addition.total_vitamin_c,
            total_vitamin_a=base.total_vitamin_a + addition.total_vitamin_a
        )

    @staticmethod
    async def get_simplified_summary(schedule_id: str) -> SimplifiedNutritionalSummary:
        """Get a simplified nutritional summary for quick overview"""
        try:
            # Get the full analysis
            full_analysis = await NutritionalAnalysisService.analyze_menu_schedule(schedule_id)
            
            # Calculate simplified metrics
            total_days = full_analysis.total_days
            total_locations = len(full_analysis.locations)
            
            # Extract food group servings
            food_group_servings = {
                DishType.CEREAL: 0,
                DishType.PROTEIN: 0,
                DishType.VEGETABLE: 0,
                DishType.FRUIT: 0,
                DishType.DAIRY: 0,
                DishType.OTHER: 0
            }
            
            for fg in full_analysis.overall_food_groups:
                food_group_servings[fg.food_group] = fg.total_servings
            
            # Calculate daily averages
            total_person_days = total_days * total_locations
            avg_daily_calories = full_analysis.overall_summary.total_calories / total_person_days if total_person_days > 0 else 0
            avg_daily_protein = full_analysis.overall_summary.total_protein / total_person_days if total_person_days > 0 else 0
            avg_daily_carbs = full_analysis.overall_summary.total_carbohydrates / total_person_days if total_person_days > 0 else 0
            avg_daily_fat = full_analysis.overall_summary.total_fat / total_person_days if total_person_days > 0 else 0
            
            # Calculate quality scores (simplified scoring)
            nutrition_score = NutritionalAnalysisService._calculate_nutrition_score(full_analysis.overall_summary, total_person_days)
            balance_score = NutritionalAnalysisService._calculate_balance_score(food_group_servings)
            variety_score = NutritionalAnalysisService._calculate_variety_score(full_analysis.overall_food_groups)
            
            return SimplifiedNutritionalSummary(
                schedule_id=schedule_id,
                menu_cycle_name=full_analysis.menu_cycle_name,
                period=f"{full_analysis.start_date} to {full_analysis.end_date}",
                total_locations=total_locations,
                grains_servings=food_group_servings[DishType.CEREAL],
                proteins_servings=food_group_servings[DishType.PROTEIN],
                vegetables_servings=food_group_servings[DishType.VEGETABLE],
                fruits_servings=food_group_servings[DishType.FRUIT],
                dairy_servings=food_group_servings[DishType.DAIRY],
                other_servings=food_group_servings[DishType.OTHER],
                avg_daily_calories=avg_daily_calories,
                avg_daily_protein=avg_daily_protein,
                avg_daily_carbs=avg_daily_carbs,
                avg_daily_fat=avg_daily_fat,
                nutrition_score=nutrition_score,
                balance_score=balance_score,
                variety_score=variety_score
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating simplified summary: {str(e)}"
            )

    @staticmethod
    def _calculate_nutrition_score(nutrients: NutrientSummary, total_person_days: int) -> float:
        """Calculate a basic nutrition score based on nutrient completeness"""
        if total_person_days == 0:
            return 0.0
        
        # Basic scoring based on recommended daily values
        daily_calories = nutrients.total_calories / total_person_days
        daily_protein = nutrients.total_protein / total_person_days
        daily_calcium = nutrients.total_calcium / total_person_days
        daily_iron = nutrients.total_iron / total_person_days
        daily_vitamin_c = nutrients.total_vitamin_c / total_person_days
        
        # Simple scoring (0-100)
        score = 0
        if daily_calories >= 1800:  # Minimum daily calories
            score += 20
        if daily_protein >= 50:     # Minimum daily protein
            score += 20
        if daily_calcium >= 800:    # Minimum daily calcium
            score += 20
        if daily_iron >= 10:        # Minimum daily iron
            score += 20
        if daily_vitamin_c >= 60:   # Minimum daily vitamin C
            score += 20
        
        return float(score)

    @staticmethod
    def _calculate_balance_score(food_group_servings: Dict[DishType, int]) -> float:
        """Calculate balance score based on food group distribution"""
        total_servings = sum(food_group_servings.values())
        if total_servings == 0:
            return 0.0
        
        # Ideal distribution percentages
        ideal_distribution = {
            DishType.CEREAL: 0.30,      # 30% grains
            DishType.PROTEIN: 0.25,     # 25% proteins
            DishType.VEGETABLE: 0.25,   # 25% vegetables
            DishType.FRUIT: 0.15,       # 15% fruits
            DishType.DAIRY: 0.15,       # 15% dairy
            DishType.OTHER: 0.05        # 5% other
        }
        
        # Calculate actual distribution
        actual_distribution = {
            food_group: servings / total_servings 
            for food_group, servings in food_group_servings.items()
        }
        
        # Calculate deviation from ideal
        total_deviation = sum(
            abs(actual_distribution.get(fg, 0) - ideal_distribution[fg]) 
            for fg in ideal_distribution
        )
        
        # Convert to score (0-100)
        balance_score = max(0, 100 - (total_deviation * 100))
        return float(balance_score)

    @staticmethod
    def _calculate_variety_score(food_groups: List[FoodGroupSummary]) -> float:
        """Calculate variety score based on number of different dishes"""
        total_dishes = sum(fg.dish_count for fg in food_groups)
        if total_dishes == 0:
            return 0.0
        
        # Simple variety scoring
        if total_dishes >= 20:
            return 100.0
        elif total_dishes >= 10:
            return 50.0 + (total_dishes - 10) * 4.0
        else:
            return total_dishes * 5.0 