#!/usr/bin/env python3
"""
Database seeding script for PAE Menus application.

This script creates sample data for all models to help developers
get started with a populated database.
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import List
from beanie import PydanticObjectId

from pae_menus.database import init_db, close_db_connection
from pae_menus.models import (
    Ingredient, Dish, MenuCycle, MenuSchedule
)
from pae_menus.models.ingredient import IngredientStatus
from pae_menus.models.dish import DishStatus, DishType
from pae_menus.models.menu_cycle import MenuCycleStatus
from pae_menus.models.menu_schedule import MenuScheduleStatus, LocationType, Coverage
from pae_menus.models.commons import (
    MealType, Recipe, Portion, DailyMenu, NutritionalInfo
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """Database seeding utility class"""
    
    def __init__(self):
        self.created_ingredients = []
        self.created_dishes = []
        self.created_menu_cycles = []
        self.created_menu_schedules = []
    
    async def seed_ingredients(self) -> List[Ingredient]:
        """Seed ingredients with comprehensive categories"""
        logger.info("Seeding ingredients...")
        
        ingredients_data = [
            # Proteins
            {"name": "Pollo", "base_unit_of_measure": "kg", "category": "Proteínas", "description": "Pollo fresco"},
            {"name": "Carne de Res", "base_unit_of_measure": "kg", "category": "Proteínas", "description": "Carne de res fresca"},
            {"name": "Pescado", "base_unit_of_measure": "kg", "category": "Proteínas", "description": "Pescado fresco"},
            {"name": "Huevos", "base_unit_of_measure": "unidad", "category": "Proteínas", "description": "Huevos frescos"},
            {"name": "Lentejas", "base_unit_of_measure": "kg", "category": "Proteínas", "description": "Lentejas secas"},
            {"name": "Frijoles", "base_unit_of_measure": "kg", "category": "Proteínas", "description": "Frijoles secos"},
            {"name": "Garbanzos", "base_unit_of_measure": "kg", "category": "Proteínas", "description": "Garbanzos secos"},
            
            # Cereals and Grains
            {"name": "Arroz", "base_unit_of_measure": "kg", "category": "Cereales", "description": "Arroz blanco"},
            {"name": "Pasta", "base_unit_of_measure": "kg", "category": "Cereales", "description": "Pasta italiana"},
            {"name": "Pan", "base_unit_of_measure": "unidad", "category": "Cereales", "description": "Pan fresco"},
            {"name": "Quinoa", "base_unit_of_measure": "kg", "category": "Cereales", "description": "Quinoa"},
            {"name": "Avena", "base_unit_of_measure": "kg", "category": "Cereales", "description": "Avena en hojuelas"},
            
            # Vegetables
            {"name": "Tomate", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Tomate fresco"},
            {"name": "Cebolla", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Cebolla blanca"},
            {"name": "Zanahoria", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Zanahoria fresca"},
            {"name": "Lechuga", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Lechuga fresca"},
            {"name": "Brócoli", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Brócoli fresco"},
            {"name": "Espinaca", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Espinaca fresca"},
            {"name": "Pepino", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Pepino fresco"},
            {"name": "Pimentón", "base_unit_of_measure": "kg", "category": "Verduras", "description": "Pimentón rojo"},
            
            # Fruits
            {"name": "Manzana", "base_unit_of_measure": "kg", "category": "Frutas", "description": "Manzana fresca"},
            {"name": "Banano", "base_unit_of_measure": "kg", "category": "Frutas", "description": "Banano maduro"},
            {"name": "Naranja", "base_unit_of_measure": "kg", "category": "Frutas", "description": "Naranja fresca"},
            {"name": "Papaya", "base_unit_of_measure": "kg", "category": "Frutas", "description": "Papaya fresca"},
            {"name": "Piña", "base_unit_of_measure": "kg", "category": "Frutas", "description": "Piña fresca"},
            {"name": "Mango", "base_unit_of_measure": "kg", "category": "Frutas", "description": "Mango maduro"},
            
            # Dairy
            {"name": "Leche", "base_unit_of_measure": "L", "category": "Lácteos", "description": "Leche fresca"},
            {"name": "Queso", "base_unit_of_measure": "kg", "category": "Lácteos", "description": "Queso fresco"},
            {"name": "Yogur", "base_unit_of_measure": "kg", "category": "Lácteos", "description": "Yogur natural"},
            
            # Condiments and Spices
            {"name": "Sal", "base_unit_of_measure": "kg", "category": "Condimentos", "description": "Sal marina"},
            {"name": "Aceite", "base_unit_of_measure": "L", "category": "Condimentos", "description": "Aceite vegetal"},
            {"name": "Ajo", "base_unit_of_measure": "kg", "category": "Condimentos", "description": "Ajo fresco"},
            {"name": "Cilantro", "base_unit_of_measure": "kg", "category": "Condimentos", "description": "Cilantro fresco"},
            {"name": "Perejil", "base_unit_of_measure": "kg", "category": "Condimentos", "description": "Perejil fresco"},
        ]
        
        ingredients = []
        for ingredient_data in ingredients_data:
            ingredient = Ingredient(**ingredient_data)
            await ingredient.save()
            ingredients.append(ingredient)
            logger.info(f"Created ingredient: {ingredient.name}")
        
        self.created_ingredients = ingredients
        return ingredients
    
    async def seed_dishes(self) -> List[Dish]:
        """Seed dishes with recipes and nutritional information"""
        logger.info("Seeding dishes...")
        
        if not self.created_ingredients:
            logger.error("No ingredients available. Seed ingredients first.")
            return []
        
        # Create a mapping of ingredient names to IDs for easier recipe creation
        ingredient_map = {ing.name: ing.id for ing in self.created_ingredients}
        
        dishes_data = [
            # Breakfast dishes
            {
                "name": "Huevos Revueltos",
                "description": "Huevos revueltos con verduras",
                "compatible_meal_types": [MealType.BREAKFAST],
                "dish_type": DishType.PROTEIN,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Huevos"], quantity=2, unit="unidad"),
                    Portion(ingredient_id=ingredient_map["Cebolla"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Tomate"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Aceite"], quantity=0.02, unit="L"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=250, protein=18, carbohydrates=5, fat=18, fiber=2
                )
            },
            {
                "name": "Avena con Frutas",
                "description": "Avena preparada con frutas frescas",
                "compatible_meal_types": [MealType.BREAKFAST],
                "dish_type": DishType.CEREAL,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Avena"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Leche"], quantity=0.3, unit="L"),
                    Portion(ingredient_id=ingredient_map["Banano"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Manzana"], quantity=0.1, unit="kg"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=320, protein=12, carbohydrates=55, fat=8, fiber=8
                )
            },
            
            # Lunch dishes
            {
                "name": "Pollo a la Plancha",
                "description": "Pollo a la plancha con vegetales",
                "compatible_meal_types": [MealType.LUNCH],
                "dish_type": DishType.PROTEIN,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Pollo"], quantity=0.15, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Ajo"], quantity=0.01, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Sal"], quantity=0.005, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Aceite"], quantity=0.02, unit="L"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=280, protein=35, carbohydrates=2, fat=14, fiber=0
                )
            },
            {
                "name": "Arroz con Verduras",
                "description": "Arroz preparado con verduras mixtas",
                "compatible_meal_types": [MealType.LUNCH],
                "dish_type": DishType.CEREAL,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Arroz"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Zanahoria"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Brócoli"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Cebolla"], quantity=0.03, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Aceite"], quantity=0.02, unit="L"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=220, protein=5, carbohydrates=45, fat=4, fiber=3
                )
            },
            {
                "name": "Lentejas Guisadas",
                "description": "Lentejas guisadas con verduras",
                "compatible_meal_types": [MealType.LUNCH],
                "dish_type": DishType.PROTEIN,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Lentejas"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Tomate"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Cebolla"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Zanahoria"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Ajo"], quantity=0.01, unit="kg"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=180, protein=12, carbohydrates=30, fat=2, fiber=10
                )
            },
            {
                "name": "Ensalada Mixta",
                "description": "Ensalada fresca con vegetales variados",
                "compatible_meal_types": [MealType.LUNCH],
                "dish_type": DishType.VEGETABLE,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Lechuga"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Tomate"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Pepino"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Zanahoria"], quantity=0.05, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Aceite"], quantity=0.01, unit="L"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=45, protein=2, carbohydrates=8, fat=1, fiber=4
                )
            },
            
            # Snack dishes
            {
                "name": "Fruta Picada",
                "description": "Mezcla de frutas frescas picadas",
                "compatible_meal_types": [MealType.SNACK],
                "dish_type": DishType.FRUIT,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Manzana"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Banano"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Papaya"], quantity=0.1, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Piña"], quantity=0.1, unit="kg"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=85, protein=1, carbohydrates=22, fat=0, fiber=4
                )
            },
            {
                "name": "Yogur con Cereales",
                "description": "Yogur natural con cereales",
                "compatible_meal_types": [MealType.SNACK],
                "dish_type": DishType.DAIRY,
                "recipe": Recipe(ingredients=[
                    Portion(ingredient_id=ingredient_map["Yogur"], quantity=0.15, unit="kg"),
                    Portion(ingredient_id=ingredient_map["Avena"], quantity=0.02, unit="kg"),
                ]),
                "nutritional_info": NutritionalInfo(
                    calories=150, protein=8, carbohydrates=22, fat=4, fiber=2
                )
            },
        ]
        
        dishes = []
        for dish_data in dishes_data:
            dish = Dish(**dish_data)
            await dish.save()
            dishes.append(dish)
            logger.info(f"Created dish: {dish.name}")
        
        self.created_dishes = dishes
        return dishes
    
    async def seed_menu_cycles(self) -> List[MenuCycle]:
        """Seed menu cycles with daily menus"""
        logger.info("Seeding menu cycles...")
        
        if not self.created_dishes:
            logger.error("No dishes available. Seed dishes first.")
            return []
        
        # Separate dishes by meal type
        breakfast_dishes = [d for d in self.created_dishes if MealType.BREAKFAST in d.compatible_meal_types]
        lunch_dishes = [d for d in self.created_dishes if MealType.LUNCH in d.compatible_meal_types]
        snack_dishes = [d for d in self.created_dishes if MealType.SNACK in d.compatible_meal_types]
        
        # Create a 7-day menu cycle
        daily_menus = []
        for day in range(1, 8):
            daily_menu = DailyMenu(
                day=day,
                breakfast_dish_ids=[breakfast_dishes[day % len(breakfast_dishes)].id],
                lunch_dish_ids=[
                    lunch_dishes[day % len(lunch_dishes)].id,
                    lunch_dishes[(day + 1) % len(lunch_dishes)].id
                ],
                snack_dish_ids=[snack_dishes[day % len(snack_dishes)].id]
            )
            daily_menus.append(daily_menu)
        
        menu_cycles_data = [
            {
                "name": "Ciclo Semanal Universidad",
                "description": "Ciclo de menús semanal para restaurantes universitarios",
                "duration_days": 7,
                "daily_menus": daily_menus
            },
            {
                "name": "Ciclo Especial Estudiantes",
                "description": "Ciclo de menús especial enfocado en estudiantes",
                "duration_days": 5,
                "daily_menus": daily_menus[:5]  # First 5 days only
            }
        ]
        
        menu_cycles = []
        for cycle_data in menu_cycles_data:
            cycle = MenuCycle(**cycle_data)
            await cycle.save()
            menu_cycles.append(cycle)
            logger.info(f"Created menu cycle: {cycle.name}")
        
        self.created_menu_cycles = menu_cycles
        return menu_cycles
    
    async def seed_menu_schedules(self) -> List[MenuSchedule]:
        """Seed menu schedules with coverage information"""
        logger.info("Seeding menu schedules...")
        
        if not self.created_menu_cycles:
            logger.error("No menu cycles available. Seed menu cycles first.")
            return []
        
        # Sample coverage locations
        campus_locations = [
            {"location_id": "campus_001", "location_name": "Campus Principal", "location_type": LocationType.CAMPUS},
            {"location_id": "campus_002", "location_name": "Campus Norte", "location_type": LocationType.CAMPUS},
        ]
        
        town_locations = [
            {"location_id": "town_001", "location_name": "Medellín Centro", "location_type": LocationType.TOWN},
            {"location_id": "town_002", "location_name": "Bogotá Chapinero", "location_type": LocationType.TOWN},
        ]
        
        schedules_data = [
            {
                "menu_cycle_id": self.created_menu_cycles[0].id,
                "coverage": [
                    Coverage(**campus_locations[0]),
                    Coverage(**campus_locations[1]),
                ],
                "start_date": date.today() + timedelta(days=1),
                "end_date": date.today() + timedelta(days=14),
                "status": MenuScheduleStatus.FUTURE
            },
            {
                "menu_cycle_id": self.created_menu_cycles[1].id,
                "coverage": [
                    Coverage(**town_locations[0]),
                    Coverage(**town_locations[1]),
                ],
                "start_date": date.today() + timedelta(days=15),
                "end_date": date.today() + timedelta(days=25),
                "status": MenuScheduleStatus.FUTURE
            },
            {
                "menu_cycle_id": self.created_menu_cycles[0].id,
                "coverage": [
                    Coverage(**campus_locations[0]),
                ],
                "start_date": date.today() - timedelta(days=14),
                "end_date": date.today() - timedelta(days=1),
                "status": MenuScheduleStatus.COMPLETED
            }
        ]
        
        schedules = []
        for schedule_data in schedules_data:
            schedule = MenuSchedule(**schedule_data)
            await schedule.save()
            schedules.append(schedule)
            logger.info(f"Created menu schedule for cycle: {schedule.menu_cycle_id}")
        
        self.created_menu_schedules = schedules
        return schedules
    
    async def seed_all(self, clear_existing: bool = False):
        """Seed all data in the correct order"""
        logger.info("Starting database seeding...")
        
        if clear_existing:
            await self.clear_all_data()
        
        # Seed in dependency order
        await self.seed_ingredients()
        await self.seed_dishes()
        await self.seed_menu_cycles()
        await self.seed_menu_schedules()
        
        logger.info("Database seeding completed successfully!")
        logger.info(f"Created {len(self.created_ingredients)} ingredients")
        logger.info(f"Created {len(self.created_dishes)} dishes")
        logger.info(f"Created {len(self.created_menu_cycles)} menu cycles")
        logger.info(f"Created {len(self.created_menu_schedules)} menu schedules")
    
    async def clear_all_data(self):
        """Clear all existing data (use with caution!)"""
        logger.warning("Clearing all existing data...")
        
        await MenuSchedule.delete_all()
        await MenuCycle.delete_all()
        await Dish.delete_all()
        await Ingredient.delete_all()
        
        logger.info("All data cleared successfully")


async def main():
    """Main seeding function"""
    try:
        # Initialize database connection
        await init_db()
        
        # Create seeder instance
        seeder = DatabaseSeeder()
        
        # Seed all data (clear existing data first)
        await seeder.seed_all(clear_existing=True)
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        # Close database connection
        await close_db_connection()


if __name__ == "__main__":
    asyncio.run(main()) 