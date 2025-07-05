# Database Management Scripts

This directory contains Python scripts for managing the PAE Menus database.

## Scripts Overview

### `seed_database.py`
Seeds the database with comprehensive sample data including ingredients, dishes, menu cycles, and schedules.

```bash
# Direct usage
python -m pae_menus.scripts.seed_database

# With Poetry
poetry run poe seed
```

### `export_database.py`
Exports database data to JSON files for backup and sharing.

```bash
# Direct usage
python -m pae_menus.scripts.export_database

# With Poetry
poetry run poe export-db
```

### `import_database.py`
Imports database data from JSON export files.

```bash
# Direct usage
python -m pae_menus.scripts.import_database path/to/export.json

# With Poetry
poetry run poe import-db path/to/export.json
```

### `manage_database.py`
Main management script with all database operations.

```bash
# Direct usage
python -m pae_menus.scripts.manage_database <command>

# With Poetry
poetry run poe manage-db <command>
```

## Quick Commands

```bash
# Seed fresh database
poetry run poe seed-fresh

# Check database status
poetry run poe db-status

# Create backup
poetry run poe db-backup

# Import from backup
poetry run poe import-db path/to/backup.json
```

## Requirements

- MongoDB running in Docker container `pae-menu-db`
- Poetry environment activated
- Proper database configuration 