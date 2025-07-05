#!/usr/bin/env python3
"""
Database management script for PAE Menus application.

This script provides utilities for database management including
seeding, backup, restore, and maintenance operations.
"""

import asyncio
import argparse
import logging
from pathlib import Path

from pae_menus.database import init_db, close_db_connection
from pae_menus.scripts.seed_database import DatabaseSeeder
from pae_menus.scripts.export_database import DatabaseExporter
from pae_menus.scripts.import_database import DatabaseImporter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_command(args):
    """Handle seed command"""
    logger.info("Starting database seeding...")
    
    seeder = DatabaseSeeder()
    await seeder.seed_all(clear_existing=args.clear)
    
    logger.info("Database seeding completed!")


async def export_command(args):
    """Handle export command"""
    logger.info("Starting database export...")
    
    exporter = DatabaseExporter(args.output_dir)
    
    if args.compact:
        compact_file = await exporter.export_compact()
        logger.info(f"Compact export saved to: {compact_file}")
    else:
        await exporter.export_all()
    
    logger.info("Database export completed!")


async def import_command(args):
    """Handle import command"""
    logger.info(f"Starting database import from: {args.file}")
    
    importer = DatabaseImporter()
    await importer.import_from_file(args.file, args.clear)
    
    logger.info("Database import completed!")


async def clear_command(args):
    """Handle clear command"""
    if not args.confirm:
        print("This will permanently delete all data from the database!")
        print("Use --confirm flag to proceed.")
        return
    
    logger.warning("Clearing all database data...")
    
    from pae_menus.models import MenuSchedule, MenuCycle, Dish, Ingredient
    
    await MenuSchedule.delete_all()
    await MenuCycle.delete_all()
    await Dish.delete_all()
    await Ingredient.delete_all()
    
    logger.info("Database cleared successfully!")


async def status_command(args):
    """Handle status command"""
    logger.info("Checking database status...")
    
    from pae_menus.models import Ingredient, Dish, MenuCycle, MenuSchedule
    
    # Get counts
    ingredients_count = await Ingredient.count()
    dishes_count = await Dish.count()
    cycles_count = await MenuCycle.count()
    schedules_count = await MenuSchedule.count()
    
    print("\n=== Database Status ===")
    print(f"Ingredients: {ingredients_count}")
    print(f"Dishes: {dishes_count}")
    print(f"Menu Cycles: {cycles_count}")
    print(f"Menu Schedules: {schedules_count}")
    print(f"Total Records: {ingredients_count + dishes_count + cycles_count + schedules_count}")
    
    # Get recent records
    recent_ingredients = await Ingredient.find().sort(-Ingredient.created_at).limit(3).to_list()
    recent_dishes = await Dish.find().sort(-Dish.created_at).limit(3).to_list()
    
    if recent_ingredients:
        print("\nRecent Ingredients:")
        for ing in recent_ingredients:
            print(f"  - {ing.name} ({ing.created_at.strftime('%Y-%m-%d %H:%M')})")
    
    if recent_dishes:
        print("\nRecent Dishes:")
        for dish in recent_dishes:
            print(f"  - {dish.name} ({dish.created_at.strftime('%Y-%m-%d %H:%M')})")


async def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description="PAE Menus Database Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Seed command
    seed_parser = subparsers.add_parser('seed', help='Seed database with sample data')
    seed_parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export database data')
    export_parser.add_argument('--output-dir', default='database_exports', help='Output directory')
    export_parser.add_argument('--compact', action='store_true', help='Create compact export file')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import database data')
    import_parser.add_argument('file', help='Import file path')
    import_parser.add_argument('--clear', action='store_true', help='Clear existing data before import')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all database data')
    clear_parser.add_argument('--confirm', action='store_true', help='Confirm deletion')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show database status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize database connection
        await init_db()
        
        # Execute command
        if args.command == 'seed':
            await seed_command(args)
        elif args.command == 'export':
            await export_command(args)
        elif args.command == 'import':
            await import_command(args)
        elif args.command == 'clear':
            await clear_command(args)
        elif args.command == 'status':
            await status_command(args)
        
    except Exception as e:
        logger.error(f"Command failed: {e}")
        raise
    finally:
        # Close database connection
        await close_db_connection()


if __name__ == "__main__":
    asyncio.run(main()) 