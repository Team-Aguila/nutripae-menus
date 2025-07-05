# PAE Menus Database Seeding System

This document explains how to use the database seeding system for the PAE Menus application.

## Overview

The database seeding system provides tools for:
- Seeding the database with sample data
- Exporting database data for backup and sharing
- Importing database data from exports
- Managing database operations

## Prerequisites

1. MongoDB running in Docker container `pae-menu-db`
2. Poetry installed and dependencies ready
3. Database connection configured in settings

## Quick Start

### 1. Seed Database with Sample Data

```bash
# Seed database with sample data (preserves existing data)
poetry run poe seed

# Seed with fresh data (clears existing data first)
poetry run poe seed-fresh
```

### 2. Check Database Status

```bash
poetry run poe db-status
```

### 3. Export Database Data

```bash
# Export to separate JSON files
poetry run poe export-db

# Create compact backup file
poetry run poe db-backup
```

### 4. Import Database Data

```bash
# Import from export file
poetry run poe import-db path/to/export.json

# Import with clear (replaces all data)
poetry run poe import-db path/to/export.json --clear
```

## Detailed Usage

### Database Management Command

The main management command supports multiple operations:

```bash
# Using the manage-db command
poetry run poe manage-db <command> [options]

# Available commands:
poetry run poe manage-db seed          # Seed database
poetry run poe manage-db export        # Export database
poetry run poe manage-db import        # Import database
poetry run poe manage-db clear         # Clear database
poetry run poe manage-db status        # Show status
```

### Seeding Options

```bash
# Seed preserving existing data
poetry run poe manage-db seed

# Seed with fresh data (clears first)
poetry run poe manage-db seed --clear
```

### Export Options

```bash
# Export to separate files
poetry run poe manage-db export

# Export to custom directory
poetry run poe manage-db export --output-dir my_exports

# Create compact export
poetry run poe manage-db export --compact
```

### Import Options

```bash
# Import from file
poetry run poe manage-db import path/to/export.json

# Import with clear existing data
poetry run poe manage-db import path/to/export.json --clear
```

### Clear Database (Dangerous!)

```bash
# Clear all data (requires confirmation)
poetry run poe manage-db clear --confirm
```

## Sample Data Structure

The seeding system creates comprehensive sample data including:

### Ingredients (32 items)
- **Proteins**: Pollo, Carne de Res, Pescado, Huevos, Lentejas, Frijoles, Garbanzos
- **Cereals**: Arroz, Pasta, Pan, Quinoa, Avena
- **Vegetables**: Tomate, Cebolla, Zanahoria, Lechuga, Brócoli, Espinaca, Pepino, Pimentón
- **Fruits**: Manzana, Banano, Naranja, Papaya, Piña, Mango
- **Dairy**: Leche, Queso, Yogur
- **Condiments**: Sal, Aceite, Ajo, Cilantro, Perejil

### Dishes (7 items)
- **Breakfast**: Huevos Revueltos, Avena con Frutas
- **Lunch**: Pollo a la Plancha, Arroz con Verduras, Lentejas Guisadas, Ensalada Mixta
- **Snack**: Fruta Picada, Yogur con Cereales

Each dish includes:
- Complete recipe with ingredient portions
- Nutritional information
- Meal type compatibility
- Food group classification

### Menu Cycles (2 items)
- **7-day University Cycle**: Complete week menu
- **5-day Student Special**: Weekday menu

### Menu Schedules (3 items)
- Future schedules for different locations
- Completed schedules for history
- Campus and town coverage examples

## File Structure

```
src/pae_menus/scripts/
├── __init__.py
├── seed_database.py          # Main seeding script
├── export_database.py        # Database export utility
├── import_database.py        # Database import utility
└── manage_database.py        # Main management command

database_exports/             # Export files directory
├── ingredients_YYYYMMDD_HHMMSS.json
├── dishes_YYYYMMDD_HHMMSS.json
├── menu_cycles_YYYYMMDD_HHMMSS.json
├── menu_schedules_YYYYMMDD_HHMMSS.json
├── export_summary_YYYYMMDD_HHMMSS.json
└── pae_menus_export_YYYYMMDD_HHMMSS.json  # Compact export
```

## Best Practices

### For Development Team

1. **Initial Setup**: Use `poetry run poe seed-fresh` for first-time setup
2. **Data Sharing**: Use `poetry run poe db-backup` to create shareable exports
3. **Clean Testing**: Use `poetry run poe manage-db clear --confirm` then seed
4. **Status Monitoring**: Use `poetry run poe db-status` to check data state

### For Production

1. **Never use** `--clear` options in production
2. **Always backup** before making changes
3. **Test imports** in development first
4. **Use compact exports** for efficiency

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MongoDB container is running: `docker ps | grep pae-menu-db`
   - Check connection settings in `src/pae_menus/core/config.py`

2. **Import Failures**
   - Ensure export file format is correct
   - Check file permissions
   - Verify MongoDB is accessible

3. **Seeding Errors**
   - Check for existing data conflicts
   - Use `--clear` option if needed
   - Verify all dependencies are installed

### Getting Help

1. Check database status: `poetry run poe db-status`
2. View logs for detailed error messages
3. Ensure Docker container is running properly
4. Check MongoDB logs: `docker logs pae-menu-db`

## Security Notes

- Never commit database export files to version control
- Use `.gitignore` to exclude `database_exports/` directory
- Be careful with `--clear` options
- Always backup production data before operations

## Data Validation

The seeding system includes validation for:
- Ingredient and dish name uniqueness
- Recipe ingredient references
- Menu cycle dish references
- Date range validations in schedules
- Nutritional information formats

## Performance Considerations

- Seeding creates realistic data volumes for testing
- Export/import operations are optimized for large datasets
- Use compact exports for faster transfers
- Consider database indexing for production use 