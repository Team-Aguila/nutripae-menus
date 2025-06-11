# pae_menus/api/ingredients.py
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import JSONResponse

from pae_menus.models.ingredient import (
    IngredientCreate, 
    IngredientUpdate, 
    IngredientResponse,
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
    description="Retrieve all ingredients with optional filtering and pagination."
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
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **status**: Filter by ingredient status (active/inactive)
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