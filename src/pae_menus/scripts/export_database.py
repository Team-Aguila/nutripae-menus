#!/usr/bin/env python3
"""
Database export script for PAE Menus application.

This script exports all database data to JSON files for backup
and sharing between developers.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from pae_menus.database import init_db, close_db_connection
from pae_menus.models import Ingredient, Dish, MenuCycle, MenuSchedule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseExporter:
    """Database export utility class"""
    
    def __init__(self, output_dir: str = "database_exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    async def export_ingredients(self) -> Dict[str, Any]:
        """Export all ingredients to JSON"""
        logger.info("Exporting ingredients...")
        
        ingredients = await Ingredient.find_all().to_list()
        export_data = {
            "collection": "ingredients",
            "count": len(ingredients),
            "exported_at": datetime.now().isoformat(),
            "data": []
        }
        
        for ingredient in ingredients:
            ingredient_dict = ingredient.model_dump(by_alias=True)
            # Convert ObjectId to string for JSON serialization
            ingredient_dict["_id"] = str(ingredient_dict["_id"])
            export_data["data"].append(ingredient_dict)
        
        # Save to file
        filename = self.output_dir / f"ingredients_{self.export_timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Exported {len(ingredients)} ingredients to {filename}")
        return export_data
    
    async def export_dishes(self) -> Dict[str, Any]:
        """Export all dishes to JSON"""
        logger.info("Exporting dishes...")
        
        dishes = await Dish.find_all().to_list()
        export_data = {
            "collection": "dishes",
            "count": len(dishes),
            "exported_at": datetime.now().isoformat(),
            "data": []
        }
        
        for dish in dishes:
            dish_dict = dish.model_dump(by_alias=True)
            # Convert ObjectId to string for JSON serialization
            dish_dict["_id"] = str(dish_dict["_id"])
            
            # Handle recipe ingredients ObjectIds
            if "recipe" in dish_dict and "ingredients" in dish_dict["recipe"]:
                for ingredient in dish_dict["recipe"]["ingredients"]:
                    ingredient["ingredient_id"] = str(ingredient["ingredient_id"])
            
            export_data["data"].append(dish_dict)
        
        # Save to file
        filename = self.output_dir / f"dishes_{self.export_timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Exported {len(dishes)} dishes to {filename}")
        return export_data
    
    async def export_menu_cycles(self) -> Dict[str, Any]:
        """Export all menu cycles to JSON"""
        logger.info("Exporting menu cycles...")
        
        menu_cycles = await MenuCycle.find_all().to_list()
        export_data = {
            "collection": "menu_cycles",
            "count": len(menu_cycles),
            "exported_at": datetime.now().isoformat(),
            "data": []
        }
        
        for cycle in menu_cycles:
            cycle_dict = cycle.model_dump(by_alias=True)
            # Convert ObjectId to string for JSON serialization
            cycle_dict["_id"] = str(cycle_dict["_id"])
            
            # Handle daily menus dish IDs
            if "daily_menus" in cycle_dict:
                for daily_menu in cycle_dict["daily_menus"]:
                    daily_menu["breakfast_dish_ids"] = [str(id) for id in daily_menu["breakfast_dish_ids"]]
                    daily_menu["lunch_dish_ids"] = [str(id) for id in daily_menu["lunch_dish_ids"]]
                    daily_menu["snack_dish_ids"] = [str(id) for id in daily_menu["snack_dish_ids"]]
            
            export_data["data"].append(cycle_dict)
        
        # Save to file
        filename = self.output_dir / f"menu_cycles_{self.export_timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Exported {len(menu_cycles)} menu cycles to {filename}")
        return export_data
    
    async def export_menu_schedules(self) -> Dict[str, Any]:
        """Export all menu schedules to JSON"""
        logger.info("Exporting menu schedules...")
        
        menu_schedules = await MenuSchedule.find_all().to_list()
        export_data = {
            "collection": "menu_schedules",
            "count": len(menu_schedules),
            "exported_at": datetime.now().isoformat(),
            "data": []
        }
        
        for schedule in menu_schedules:
            schedule_dict = schedule.model_dump(by_alias=True)
            # Convert ObjectId to string for JSON serialization
            schedule_dict["_id"] = str(schedule_dict["_id"])
            schedule_dict["menu_cycle_id"] = str(schedule_dict["menu_cycle_id"])
            
            export_data["data"].append(schedule_dict)
        
        # Save to file
        filename = self.output_dir / f"menu_schedules_{self.export_timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Exported {len(menu_schedules)} menu schedules to {filename}")
        return export_data
    
    async def export_all(self) -> Dict[str, Any]:
        """Export all database data"""
        logger.info("Starting full database export...")
        
        export_summary = {
            "export_timestamp": self.export_timestamp,
            "export_started_at": datetime.now().isoformat(),
            "collections": {}
        }
        
        # Export all collections
        ingredients_data = await self.export_ingredients()
        dishes_data = await self.export_dishes()
        menu_cycles_data = await self.export_menu_cycles()
        menu_schedules_data = await self.export_menu_schedules()
        
        export_summary["collections"] = {
            "ingredients": ingredients_data["count"],
            "dishes": dishes_data["count"],
            "menu_cycles": menu_cycles_data["count"],
            "menu_schedules": menu_schedules_data["count"]
        }
        
        export_summary["export_completed_at"] = datetime.now().isoformat()
        export_summary["total_records"] = sum(export_summary["collections"].values())
        
        # Save export summary
        summary_filename = self.output_dir / f"export_summary_{self.export_timestamp}.json"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(export_summary, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info("Database export completed successfully!")
        logger.info(f"Total records exported: {export_summary['total_records']}")
        logger.info(f"Export files saved to: {self.output_dir}")
        
        return export_summary
    
    async def export_compact(self) -> str:
        """Export all data to a single compact JSON file"""
        logger.info("Creating compact export...")
        
        # Get all data
        ingredients = await Ingredient.find_all().to_list()
        dishes = await Dish.find_all().to_list()
        menu_cycles = await MenuCycle.find_all().to_list()
        menu_schedules = await MenuSchedule.find_all().to_list()
        
        # Create compact export
        compact_data = {
            "export_info": {
                "timestamp": self.export_timestamp,
                "exported_at": datetime.now().isoformat(),
                "version": "1.0",
                "description": "PAE Menus database export"
            },
            "collections": {
                "ingredients": [self._serialize_document(ing) for ing in ingredients],
                "dishes": [self._serialize_document(dish) for dish in dishes],
                "menu_cycles": [self._serialize_document(cycle) for cycle in menu_cycles],
                "menu_schedules": [self._serialize_document(schedule) for schedule in menu_schedules]
            },
            "counts": {
                "ingredients": len(ingredients),
                "dishes": len(dishes),
                "menu_cycles": len(menu_cycles),
                "menu_schedules": len(menu_schedules),
                "total": len(ingredients) + len(dishes) + len(menu_cycles) + len(menu_schedules)
            }
        }
        
        # Save compact export
        compact_filename = self.output_dir / f"pae_menus_export_{self.export_timestamp}.json"
        with open(compact_filename, 'w', encoding='utf-8') as f:
            json.dump(compact_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Compact export saved to: {compact_filename}")
        return str(compact_filename)
    
    def _serialize_document(self, document) -> Dict[str, Any]:
        """Serialize a document for export"""
        doc_dict = document.model_dump(by_alias=True)
        
        # Convert ObjectId to string
        if "_id" in doc_dict:
            doc_dict["_id"] = str(doc_dict["_id"])
        
        # Handle specific ObjectId fields
        if "menu_cycle_id" in doc_dict:
            doc_dict["menu_cycle_id"] = str(doc_dict["menu_cycle_id"])
        
        # Handle recipe ingredients
        if "recipe" in doc_dict and "ingredients" in doc_dict["recipe"]:
            for ingredient in doc_dict["recipe"]["ingredients"]:
                ingredient["ingredient_id"] = str(ingredient["ingredient_id"])
        
        # Handle daily menus
        if "daily_menus" in doc_dict:
            for daily_menu in doc_dict["daily_menus"]:
                daily_menu["breakfast_dish_ids"] = [str(id) for id in daily_menu["breakfast_dish_ids"]]
                daily_menu["lunch_dish_ids"] = [str(id) for id in daily_menu["lunch_dish_ids"]]
                daily_menu["snack_dish_ids"] = [str(id) for id in daily_menu["snack_dish_ids"]]
        
        return doc_dict


async def main():
    """Main export function"""
    try:
        # Initialize database connection
        await init_db()
        
        # Create exporter instance
        exporter = DatabaseExporter()
        
        # Export all data
        await exporter.export_all()
        
        # Also create compact export
        compact_file = await exporter.export_compact()
        
        print(f"\nDatabase export completed!")
        print(f"Files saved to: {exporter.output_dir}")
        print(f"Compact export: {compact_file}")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise
    finally:
        # Close database connection
        await close_db_connection()


if __name__ == "__main__":
    asyncio.run(main()) 