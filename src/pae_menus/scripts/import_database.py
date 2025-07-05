#!/usr/bin/env python3
"""
Database import script for PAE Menus application.

This script imports database data from JSON export files.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from beanie import PydanticObjectId
from pae_menus.database import init_db, close_db_connection
from pae_menus.models import Ingredient, Dish, MenuCycle, MenuSchedule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Database import utility class"""
    
    def __init__(self):
        self.imported_counts = {
            "ingredients": 0,
            "dishes": 0,
            "menu_cycles": 0,
            "menu_schedules": 0
        }
    
    async def import_from_file(self, file_path: str, clear_existing: bool = False):
        """Import data from a compact JSON export file"""
        logger.info(f"Importing data from: {file_path}")
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Import file not found: {file_path}")
        
        if clear_existing:
            await self.clear_all_data()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate file format
        if "collections" not in data:
            raise ValueError("Invalid import file format")
        
        collections = data["collections"]
        
        # Import in dependency order
        await self._import_ingredients(collections.get("ingredients", []))
        await self._import_dishes(collections.get("dishes", []))
        await self._import_menu_cycles(collections.get("menu_cycles", []))
        await self._import_menu_schedules(collections.get("menu_schedules", []))
        
        logger.info("Database import completed successfully!")
        logger.info(f"Imported counts: {self.imported_counts}")
    
    async def _import_ingredients(self, ingredients_data: List[Dict[str, Any]]):
        """Import ingredients"""
        logger.info("Importing ingredients...")
        
        for ingredient_data in ingredients_data:
            # Remove _id to let MongoDB generate new ones
            ingredient_data.pop("_id", None)
            
            try:
                ingredient = Ingredient(**ingredient_data)
                await ingredient.save()
                self.imported_counts["ingredients"] += 1
            except Exception as e:
                logger.error(f"Error importing ingredient {ingredient_data.get('name', 'unknown')}: {e}")
    
    async def _import_dishes(self, dishes_data: List[Dict[str, Any]]):
        """Import dishes"""
        logger.info("Importing dishes...")
        
        for dish_data in dishes_data:
            # Remove _id to let MongoDB generate new ones
            dish_data.pop("_id", None)
            
            try:
                # Convert ingredient IDs in recipe
                if "recipe" in dish_data and "ingredients" in dish_data["recipe"]:
                    for ingredient in dish_data["recipe"]["ingredients"]:
                        ingredient["ingredient_id"] = PydanticObjectId(ingredient["ingredient_id"])
                
                dish = Dish(**dish_data)
                await dish.save()
                self.imported_counts["dishes"] += 1
            except Exception as e:
                logger.error(f"Error importing dish {dish_data.get('name', 'unknown')}: {e}")
    
    async def _import_menu_cycles(self, cycles_data: List[Dict[str, Any]]):
        """Import menu cycles"""
        logger.info("Importing menu cycles...")
        
        for cycle_data in cycles_data:
            # Remove _id to let MongoDB generate new ones
            cycle_data.pop("_id", None)
            
            try:
                # Convert dish IDs in daily menus
                if "daily_menus" in cycle_data:
                    for daily_menu in cycle_data["daily_menus"]:
                        daily_menu["breakfast_dish_ids"] = [PydanticObjectId(id) for id in daily_menu["breakfast_dish_ids"]]
                        daily_menu["lunch_dish_ids"] = [PydanticObjectId(id) for id in daily_menu["lunch_dish_ids"]]
                        daily_menu["snack_dish_ids"] = [PydanticObjectId(id) for id in daily_menu["snack_dish_ids"]]
                
                cycle = MenuCycle(**cycle_data)
                await cycle.save()
                self.imported_counts["menu_cycles"] += 1
            except Exception as e:
                logger.error(f"Error importing menu cycle {cycle_data.get('name', 'unknown')}: {e}")
    
    async def _import_menu_schedules(self, schedules_data: List[Dict[str, Any]]):
        """Import menu schedules"""
        logger.info("Importing menu schedules...")
        
        for schedule_data in schedules_data:
            # Remove _id to let MongoDB generate new ones
            schedule_data.pop("_id", None)
            
            try:
                # Convert menu_cycle_id
                schedule_data["menu_cycle_id"] = PydanticObjectId(schedule_data["menu_cycle_id"])
                
                schedule = MenuSchedule(**schedule_data)
                await schedule.save()
                self.imported_counts["menu_schedules"] += 1
            except Exception as e:
                logger.error(f"Error importing menu schedule: {e}")
    
    async def clear_all_data(self):
        """Clear all existing data"""
        logger.warning("Clearing all existing data...")
        
        await MenuSchedule.delete_all()
        await MenuCycle.delete_all()
        await Dish.delete_all()
        await Ingredient.delete_all()
        
        logger.info("All data cleared successfully")


async def main():
    """Main import function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_database.py <export_file_path> [--clear-existing]")
        return
    
    file_path = sys.argv[1]
    clear_existing = "--clear-existing" in sys.argv
    
    try:
        # Initialize database connection
        await init_db()
        
        # Create importer instance
        importer = DatabaseImporter()
        
        # Import data
        await importer.import_from_file(file_path, clear_existing)
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise
    finally:
        # Close database connection
        await close_db_connection()


if __name__ == "__main__":
    asyncio.run(main()) 