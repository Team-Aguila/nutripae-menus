# pae_menus/api/ingredients.py
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import JSONResponse

from pae_menus.models.ingredient import (
    IngredientCreate, 
    IngredientUpdate, 
    IngredientResponse,
    IngredientDetailedResponse,
    IngredientStatus
)
from pae_menus.services.ingredient_service import IngredientService

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post(
    "/",
    response_model=IngredientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ingredient",
    description="Create a new ingredient with name uniqueness validation. Returns the created ingredient with generated ID."
)
async def create_ingredient(ingredient_data: IngredientCreate) -> IngredientResponse:
    """
    Create a new ingredient.
    
    - **name**: Unique ingredient name (required)
    - **base_unit_of_measure**: Unit of measure like kg, L, units (required)
    - **status**: Active or inactive status (defaults to active)
    - **description**: Optional description
    - **category**: Optional category
    """
    ingredient = await IngredientService.create_ingredient(ingredient_data)
    return ingredient


@router.get(
    "/",
    response_model=List[IngredientResponse],
    summary="Get all ingredients",
    description="Retrieve all ingredients with optional filtering and pagination. Use '/active' endpoint for menu creation to exclude inactive ingredients."
)
async def get_ingredients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[IngredientStatus] = Query(None, description="Filter by ingredient status"),
    category: Optional[str] = Query(None, description="Filter by ingredient category"),
    search: Optional[str] = Query(None, description="Search term for ingredient name")
) -> List[IngredientResponse]:
    """
    Get all ingredients with optional filtering.
    
    This endpoint returns both active and inactive ingredients based on filtering.
    For menu creation, use the '/active' endpoint instead to exclude inactive ingredients.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **status**: Filter by ingredient status (active/inactive). Leave empty to get all.
    - **category**: Filter by ingredient category
    - **search**: Search term for ingredient name (case-insensitive)
    """
    ingredients = await IngredientService.get_all_ingredients(
        skip=skip,
        limit=limit,
        status_filter=status.value if status else None,
        category_filter=category,
        search=search
    )
    return ingredients


@router.get(
    "/active",
    response_model=List[IngredientResponse],
    summary="Get active ingredients for menu creation",
    description="Retrieve only active ingredients available for creating new menus. Inactive ingredients are excluded."
)
async def get_active_ingredients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by ingredient category"),
    search: Optional[str] = Query(None, description="Search term for ingredient name")
) -> List[IngredientResponse]:
    """
    Get only active ingredients for menu creation.
    
    This endpoint specifically filters out inactive ingredients to ensure
    they don't appear when creating new menus, implementing the soft deletion logic.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **category**: Filter by ingredient category
    - **search**: Search term for ingredient name (case-insensitive)
    """
    ingredients = await IngredientService.get_active_ingredients(
        skip=skip,
        limit=limit,
        category_filter=category,
        search=search
    )
    return ingredients


@router.get(
    "/detailed",
    response_model=List[IngredientDetailedResponse],
    summary="Get detailed ingredients with menu usage",
    description="Retrieve ingredients with comprehensive details including menu usage information. Perfect for nutritionist/administrator dashboard views."
)
async def get_detailed_ingredients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[IngredientStatus] = Query(None, description="Filter by ingredient status"),
    category: Optional[str] = Query(None, description="Filter by ingredient category"),
    search: Optional[str] = Query(None, description="Search term for ingredient name")
) -> List[IngredientDetailedResponse]:
    """
    Get detailed ingredients with menu usage information.
    
    This endpoint provides comprehensive ingredient details including:
    - Basic ingredient information (name, status, category, etc.)
    - Menu usage statistics (dish count, menu cycle count)
    - List of dishes using each ingredient
    - Last usage date in menu cycles
    
    Perfect for nutritionist/administrator views where understanding ingredient usage is critical.
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **status**: Filter by ingredient status (active/inactive)
    - **category**: Filter by ingredient category
    - **search**: Search term for ingredient name (case-insensitive)
    """
    ingredients = await IngredientService.get_detailed_ingredients(
        skip=skip,
        limit=limit,
        status_filter=status.value if status else None,
        category_filter=category,
        search=search
    )
    return ingredients


@router.get(
    "/categories",
    response_model=List[str],
    summary="Get available ingredient categories",
    description="Retrieve all available categories for filtering ingredients."
)
async def get_ingredient_categories() -> List[str]:
    """
    Get all available ingredient categories for filtering purposes.
    
    Returns a list of unique categories that are currently used by ingredients.
    Useful for populating dropdown filters in the UI.
    """
    categories = await IngredientService.get_available_categories()
    return categories


@router.get(
    "/statistics",
    summary="Get ingredient statistics",
    description="Get comprehensive statistics about ingredients for dashboard views."
)
async def get_ingredient_statistics() -> JSONResponse:
    """
    Get comprehensive ingredient statistics.
    
    Returns statistics including:
    - Total ingredient count
    - Active vs inactive ingredient counts
    - Number of categories
    - List of all categories
    
    Perfect for dashboard summary views.
    """
    stats = await IngredientService.get_ingredient_statistics()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=stats
    )


@router.get(
    "/validate/name-uniqueness",
    summary="Check name uniqueness",
    description="Real-time validation endpoint to check if an ingredient name is unique."
)
async def check_name_uniqueness(
    name: str = Query(..., description="The ingredient name to check"),
    exclude_id: Optional[str] = Query(None, description="ID to exclude from uniqueness check (for updates)")
) -> JSONResponse:
    """
    Check if an ingredient name is unique.
    
    - **name**: The ingredient name to validate
    - **exclude_id**: Optional ID to exclude from check (useful for updates)
    """
    is_unique = await IngredientService.check_name_uniqueness(name, exclude_id)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "is_unique": is_unique,
            "message": "Name is available" if is_unique else f"Name '{name}' is already taken"
        }
    )


@router.get(
    "/{ingredient_id}",
    response_model=IngredientResponse,
    summary="Get ingredient by ID",
    description="Retrieve a specific ingredient by its ID."
)
async def get_ingredient(ingredient_id: str) -> IngredientResponse:
    """
    Get a specific ingredient by ID.
    
    - **ingredient_id**: The unique identifier of the ingredient
    """
    ingredient = await IngredientService.get_ingredient_by_id(ingredient_id)
    return ingredient


@router.get(
    "/{ingredient_id}/detailed",
    response_model=IngredientDetailedResponse,
    summary="Get detailed ingredient by ID with menu usage",
    description="Retrieve a specific ingredient with comprehensive details including menu usage information."
)
async def get_detailed_ingredient(ingredient_id: str) -> IngredientDetailedResponse:
    """
    Get a specific ingredient with detailed menu usage information.
    
    This endpoint provides comprehensive details for a single ingredient including:
    - Basic ingredient information
    - Menu usage statistics
    - List of dishes using this ingredient
    - Last usage date in menu cycles
    
    - **ingredient_id**: The unique identifier of the ingredient
    """
    ingredient = await IngredientService.get_detailed_ingredient_by_id(ingredient_id)
    return ingredient


@router.put(
    "/{ingredient_id}",
    response_model=IngredientResponse,
    summary="Update an ingredient",
    description="Update an existing ingredient. Name uniqueness is validated if name is changed."
)
async def update_ingredient(
    ingredient_id: str, 
    ingredient_data: IngredientUpdate
) -> IngredientResponse:
    """
    Update an existing ingredient.
    
    - **ingredient_id**: The unique identifier of the ingredient
    - **name**: New ingredient name (must be unique if changed)
    - **base_unit_of_measure**: New unit of measure
    - **status**: New status (active/inactive)
    - **description**: New description
    - **category**: New category
    """
    ingredient = await IngredientService.update_ingredient(ingredient_id, ingredient_data)
    return ingredient


@router.delete(
    "/{ingredient_id}",
    summary="Delete an ingredient",
    description="Delete an ingredient by its ID."
)
async def delete_ingredient(ingredient_id: str) -> JSONResponse:
    """
    Delete an ingredient.
    
    - **ingredient_id**: The unique identifier of the ingredient to delete
    """
    result = await IngredientService.delete_ingredient(ingredient_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result
    )


@router.patch(
    "/{ingredient_id}/inactivate",
    response_model=IngredientResponse,
    summary="Inactivate an ingredient",
    description="Mark an ingredient as inactive (soft delete). The ingredient will no longer be available for new menus but existing menu associations remain intact."
)
async def inactivate_ingredient(ingredient_id: str) -> IngredientResponse:
    """
    Inactivate an ingredient (soft delete).
    
    This action:
    - Marks the ingredient status as INACTIVE
    - Prevents the ingredient from being available for new menus
    - Preserves existing menu associations (they are not removed)
    - Performs logical deletion (record remains in database)
    
    - **ingredient_id**: The unique identifier of the ingredient to inactivate
    """
    ingredient = await IngredientService.inactivate_ingredient(ingredient_id)
    return ingredient


@router.patch(
    "/{ingredient_id}/reactivate",
    response_model=IngredientResponse,
    summary="Reactivate an ingredient",
    description="Mark an inactive ingredient as active again, making it available for new menus."
)
async def reactivate_ingredient(ingredient_id: str) -> IngredientResponse:
    """
    Reactivate an ingredient.
    
    This action:
    - Marks the ingredient status as ACTIVE
    - Makes the ingredient available for new menus again
    - Updates the timestamp
    
    - **ingredient_id**: The unique identifier of the ingredient to reactivate
    """
    ingredient = await IngredientService.reactivate_ingredient(ingredient_id)
    return ingredient 