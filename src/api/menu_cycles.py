from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional

from models.menu_cycle import MenuCycleCreate, MenuCycleUpdate, MenuCycleResponse, MenuCycleStatus
from services.menu_cycle_service import menu_cycle_service, MenuCycleService
from core.dependencies import require_create, require_list, require_update, require_delete, require_read

router = APIRouter(
    tags=["Menu Cycles"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=MenuCycleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new menu cycle",
    description="Create a new menu cycle with unique name, duration, and daily menu assignments."
)
async def create_menu_cycle(
    menu_cycle_data: MenuCycleCreate,
    service: MenuCycleService = Depends(lambda: menu_cycle_service),
    current_user: dict = Depends(require_create()),
) -> MenuCycleResponse:
    """
    Create a new menu cycle.
    
    This endpoint creates a new menu cycle with:
    - Unique name
    - Duration in days
    - Daily menu assignments for each meal type
    
    The request will be validated to ensure:
    - Name uniqueness
    - At least one dish per day
    - Valid duration
    
    - **menu_cycle_data**: The menu cycle data to create
    """
    return await service.create_menu_cycle(menu_cycle_data)

@router.get(
    "/",
    response_model=List[MenuCycleResponse],
    summary="Get all menu cycles",
    description="Retrieve all menu cycles with optional filtering and pagination."
)
async def get_all_menu_cycles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[MenuCycleStatus] = Query(None, description="Filter by menu cycle status"),
    search: Optional[str] = Query(None, description="Search term for menu cycle name"),
    service: MenuCycleService = Depends(lambda: menu_cycle_service),
    current_user: dict = Depends(require_list()),
) -> List[MenuCycleResponse]:
    """
    Get all menu cycles with optional filtering.
    
    This endpoint returns menu cycles based on filtering criteria:
    - Pagination (skip/limit)
    - Status filter (active/inactive)
    - Name search
    
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    - **status**: Filter by menu cycle status
    - **search**: Search term for menu cycle name (case-insensitive)
    """
    return await service.get_all_menu_cycles(
        skip=skip,
        limit=limit,
        status_filter=status.value if status else None,
        search=search
    )

@router.get(
    "/{menu_cycle_id}",
    response_model=MenuCycleResponse,
    summary="Get menu cycle by ID",
    description="Retrieve a specific menu cycle by its ID."
)
async def get_menu_cycle(
    menu_cycle_id: str,
    service: MenuCycleService = Depends(lambda: menu_cycle_service),
    current_user: dict = Depends(require_read()),
) -> MenuCycleResponse:
    """
    Get a specific menu cycle by ID.
    
    This endpoint returns detailed information about a menu cycle including:
    - Basic information (name, status, duration)
    - Daily menu assignments
    - Creation and update timestamps
    
    - **menu_cycle_id**: The unique identifier of the menu cycle
    """
    return await service.get_menu_cycle_by_id(menu_cycle_id)

@router.patch(
    "/{menu_cycle_id}",
    response_model=MenuCycleResponse,
    summary="Update a menu cycle",
    description="Update an existing menu cycle's information and daily menu assignments."
)
async def update_menu_cycle(
    menu_cycle_id: str,
    menu_cycle_data: MenuCycleUpdate,
    service: MenuCycleService = Depends(lambda: menu_cycle_service),
    current_user: dict = Depends(require_update()),
) -> MenuCycleResponse:
    """
    Update a menu cycle.
    
    This endpoint allows updating:
    - Basic information (name, description, status)
    - Duration
    - Daily menu assignments
    
    The update will be validated to ensure:
    - Name uniqueness (if name is being updated)
    - At least one dish per day (if daily menus are being updated)
    - Valid duration (if duration is being updated)
    
    - **menu_cycle_id**: The unique identifier of the menu cycle to update
    - **menu_cycle_data**: The update data
    """
    return await service.update_menu_cycle(menu_cycle_id, menu_cycle_data)

@router.patch(
    "/{menu_cycle_id}/deactivate",
    response_model=MenuCycleResponse,
    summary="Deactivate a menu cycle",
    description="Deactivate a menu cycle, preventing its use in new schedules."
)
async def deactivate_menu_cycle(
    menu_cycle_id: str,
    service: MenuCycleService = Depends(lambda: menu_cycle_service),
    current_user: dict = Depends(require_delete()),
) -> MenuCycleResponse:
    """
    Deactivate a menu cycle.
    
    This action:
    - Marks the menu cycle as inactive
    - Prevents its use in new schedules
    - Validates that it's not assigned to any active or future schedules
    
    - **menu_cycle_id**: The unique identifier of the menu cycle to deactivate
    """
    return await service.deactivate_menu_cycle(menu_cycle_id)

@router.delete(
    "/{menu_cycle_id}",
    summary="Delete a menu cycle",
    description="Delete a menu cycle by its ID."
)
async def delete_menu_cycle(
    menu_cycle_id: str,
    service: MenuCycleService = Depends(lambda: menu_cycle_service),
    current_user: dict = Depends(require_delete()),
) -> dict:
    """
    Delete a menu cycle.
    
    This action permanently removes the menu cycle from the system.
    
    **WARNING**: This is a permanent action and cannot be undone.
    
    Business Rules:
    - Menu cycles cannot be deleted if assigned to any schedules
    - Deletion removes all menu cycle data including daily menu assignments
    - Returns confirmation with deleted menu cycle details
    
    **menu_cycle_id**: The unique identifier of the menu cycle to delete
    
    Returns:
    - Confirmation message with details of the deleted menu cycle
    """
    return await service.delete_menu_cycle(menu_cycle_id) 