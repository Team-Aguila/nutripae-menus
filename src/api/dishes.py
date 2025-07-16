from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId
from typing import List, Optional

from models.dish import Dish, DishCreate, DishUpdate, DishResponse, DishStatus
from models.commons import MealType
from services.dish_service import dish_service, DishService
from core.dependencies import require_list, require_read, require_update, require_create, require_delete

router = APIRouter(
    tags=["Dishes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[DishResponse], summary="Get all dishes with filtering")
async def get_all_dishes(
    name: Optional[str] = Query(None, description="Filter by dish name (case-insensitive substring match)"),
    status: Optional[DishStatus] = Query(None, description="Filter by dish status"),
    meal_type: Optional[MealType] = Query(None, description="Filter by compatible meal type"),
    service: DishService = Depends(lambda: dish_service),
    current_user: dict = Depends(require_list()),
):
    """
    Retrieve a list of all dishes, with optional filters for name, status, and meal type.
    """
    return await service.get_all_dishes(name=name, status=status, meal_type=meal_type)

@router.get("/{dish_id}", response_model=DishResponse, summary="Get a single dish by ID")
async def get_dish(
    dish_id: PydanticObjectId,
    service: DishService = Depends(lambda: dish_service),
    current_user: dict = Depends(require_read()),
):
    """
    Retrieve the details of a single dish by its unique ID.
    """
    dish = await service.get_dish(dish_id)
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
    return dish

@router.post(
    "/",
    response_model=DishResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new dish",
)
async def create_dish(
    dish_data: DishCreate,
    service: DishService = Depends(lambda: dish_service),
    current_user: dict = Depends(require_create()),
):
    """
    Create a new dish with nutritional information and a recipe.
    - **name**: Must be unique.
    - **recipe**: List of ingredients and their quantities. All ingredients must exist and be active.
    """
    try:
        return await service.create_dish(dish_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions without wrapping them
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@router.put(
    "/{dish_id}",
    response_model=DishResponse,
    summary="Update an existing dish",
)
async def update_dish(
    dish_id: PydanticObjectId,
    dish_data: DishUpdate,
    service: DishService = Depends(lambda: dish_service),
    current_user: dict = Depends(require_update()),
):
    """
    Update an existing dish's properties, including its recipe.
    """
    try:
        updated_dish = await service.update_dish(dish_id, dish_data)
        if not updated_dish:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
        return updated_dish
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions without wrapping them
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@router.delete(
    "/{dish_id}",
    summary="Delete a dish",
    description="Delete a dish by its ID. Dish cannot be deleted if it's used in any menu cycles."
)
async def delete_dish(
    dish_id: PydanticObjectId,
    service: DishService = Depends(lambda: dish_service),
    current_user: dict = Depends(require_delete()),
) -> JSONResponse:
    """
    Delete a dish.
    
    This action permanently removes the dish from the system.
    
    **WARNING**: This is a permanent action and cannot be undone.
    
    Business Rules:
    - Dishes cannot be deleted if they are used in any menu cycles
    - Deletion removes all dish data including recipe and nutritional information
    - Returns confirmation with deleted dish details
    
    **dish_id**: The unique identifier of the dish to delete
    
    Returns:
    - Confirmation message with details of the deleted dish
    """
    try:
        result = await service.delete_dish(dish_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        # Re-raise HTTPExceptions without wrapping them
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}") 