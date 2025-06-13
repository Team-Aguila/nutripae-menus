from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import date

from ..models.menu_schedule import (
    MenuScheduleAssignmentRequest,
    MenuScheduleAssignmentSummary,
    MenuScheduleResponse,
    MenuScheduleUpdate,
    MenuScheduleStatus,
    CitizenMenuResponse,
    LocationType,
    ScheduleDetailedResponse
)
from ..services.menu_schedule_service import menu_schedule_service, MenuScheduleService
from ..services.coverage_service import coverage_service, CoverageService

router = APIRouter(
    tags=["Menu Schedules"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/assign",
    response_model=MenuScheduleAssignmentSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Assign menu cycle to locations",
    description="Assign an active menu cycle to campuses/towns for a specific date range."
)
async def assign_menu_cycle(
    assignment_request: MenuScheduleAssignmentRequest,
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> MenuScheduleAssignmentSummary:
    """
    Assign a menu cycle to locations for a date range.
    
    This endpoint creates a new menu schedule assignment with:
    - Active menu cycle validation
    - Location validation (campuses and/or towns)
    - Date range validation (start < end)
    - Overlap conflict detection
    
    **assignment_request**: The assignment data including:
    - menu_cycle_id: ID of the active menu cycle to assign
    - campus_ids: List of campus IDs (optional)
    - town_ids: List of town IDs (optional)
    - start_date: Assignment start date
    - end_date: Assignment end date
    
    Returns a summary with assigned locations, dates, and the created schedule ID.
    """
    return await service.assign_menu_cycle(assignment_request)

@router.get(
    "/",
    response_model=List[MenuScheduleResponse],
    summary="Get all menu schedules",
    description="Retrieve all menu schedules with optional filtering and pagination."
)
async def get_all_schedules(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[MenuScheduleStatus] = Query(None, description="Filter by schedule status"),
    menu_cycle_id: Optional[str] = Query(None, description="Filter by menu cycle ID"),
    location_id: Optional[str] = Query(None, description="Filter by location ID (campus or town)"),
    location_type: Optional[LocationType] = Query(None, description="Filter by location type"),
    start_date_from: Optional[date] = Query(None, description="Filter schedules starting from this date"),
    start_date_to: Optional[date] = Query(None, description="Filter schedules starting up to this date"),
    end_date_from: Optional[date] = Query(None, description="Filter schedules ending from this date"),
    end_date_to: Optional[date] = Query(None, description="Filter schedules ending up to this date"),
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> List[MenuScheduleResponse]:
    """
    Get all menu schedules with enhanced filtering for administrators.
    
    This endpoint returns menu schedules based on filtering criteria:
    - Pagination (skip/limit)
    - Status filter (active/future/completed/cancelled)
    - Menu cycle filter (by cycle ID)
    - Location filter (by location ID and/or type)
    - Date range filters (start and end dates)
    
    **skip**: Number of records to skip for pagination
    **limit**: Maximum number of records to return
    **status**: Filter by schedule status
    **menu_cycle_id**: Filter by specific menu cycle
    **location_id**: Filter by specific location (campus or town)
    **location_type**: Filter by location type (campus/town)
    **start_date_from/to**: Filter by schedule start date range
    **end_date_from/to**: Filter by schedule end date range
    """
    location_type_value = location_type.value if location_type else None
    return await service.get_all_schedules(
        skip=skip,
        limit=limit,
        status_filter=status,
        menu_cycle_id=menu_cycle_id,
        location_id=location_id,
        location_type=location_type_value,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        end_date_from=end_date_from,
        end_date_to=end_date_to
    )

@router.get(
    "/{schedule_id}",
    response_model=MenuScheduleResponse,
    summary="Get menu schedule by ID",
    description="Retrieve a specific menu schedule by its ID."
)
async def get_schedule(
    schedule_id: str,
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> MenuScheduleResponse:
    """
    Get a specific menu schedule by ID.
    
    This endpoint returns detailed information about a menu schedule including:
    - Menu cycle reference
    - Coverage locations (campuses/towns)
    - Date range and status
    - Creation and update timestamps
    
    **schedule_id**: The unique identifier of the menu schedule
    """
    return await service.get_schedule_by_id(schedule_id)

@router.get(
    "/{schedule_id}/detailed",
    response_model=ScheduleDetailedResponse,
    summary="Get detailed schedule view with daily effective menus",
    description="Get comprehensive schedule details with daily effective menus for administrators."
)
async def get_schedule_detailed(
    schedule_id: str,
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> ScheduleDetailedResponse:
    """
    Get detailed schedule view with daily effective menus for administrators.
    
    This endpoint provides a comprehensive view of a menu schedule including:
    - Basic schedule information (dates, status, coverage)
    - Menu cycle details
    - Daily effective menus for each location and date
    - Dishes served (breakfast, lunch, snack) for each day and location
    - Nutritional information when available
    - Summary statistics (total days, total locations)
    
    This is specifically designed for administrators, planners, and supervisors
    to supervise and validate the execution of scheduled menus.
    
    **schedule_id**: The unique identifier of the menu schedule
    
    The response includes:
    - Complete schedule metadata
    - Daily breakdown showing what dishes are served on each date
    - Location-specific menu information
    - Cycle day calculations
    - Summary totals for easy overview
    """
    return await service.get_schedule_detailed_view(schedule_id)

@router.patch(
    "/{schedule_id}",
    response_model=MenuScheduleResponse,
    summary="Update a menu schedule",
    description="Update an existing menu schedule's information."
)
async def update_schedule(
    schedule_id: str,
    schedule_data: MenuScheduleUpdate,
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> MenuScheduleResponse:
    """
    Update a menu schedule.
    
    This endpoint allows updating active or future schedules with:
    - Coverage locations (validates location existence and checks for overlaps)
    - End date (must be after start date, validates no overlaps)
    - Status
    - Cancellation information
    
    Business Rules:
    - Only ACTIVE or FUTURE schedules can be edited
    - Updates to coverage or end date trigger overlap validation
    - At least one location must be selected if coverage is updated
    - All location IDs must exist in the coverage service
    
    **schedule_id**: The unique identifier of the menu schedule to update
    **schedule_data**: The update data
    """
    return await service.update_schedule(schedule_id, schedule_data)

@router.patch(
    "/{schedule_id}/cancel",
    response_model=MenuScheduleResponse,
    summary="Cancel a menu schedule",
    description="Cancel a menu schedule with optional reason."
)
async def cancel_schedule(
    schedule_id: str,
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> MenuScheduleResponse:
    """
    Cancel a menu schedule.
    
    This action:
    - Marks the schedule as cancelled
    - Records cancellation reason and timestamp
    - Prevents the schedule from being executed
    
    **schedule_id**: The unique identifier of the menu schedule to cancel
    **reason**: Optional reason for cancellation
    """
    return await service.cancel_schedule(schedule_id, reason)

@router.patch(
    "/{schedule_id}/uncancel",
    response_model=MenuScheduleResponse,
    summary="Uncancel a menu schedule",
    description="Restore a cancelled menu schedule to its appropriate status."
)
async def uncancel_schedule(
    schedule_id: str,
    reason: Optional[str] = Query(None, description="Reason for uncancelling"),
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> MenuScheduleResponse:
    """
    Uncancel a menu schedule.
    
    This action:
    - Restores a cancelled schedule to an editable status
    - Clears cancellation information
    - Validates that no overlapping schedules exist before restoration
    - Sets status to FUTURE (if start date is future) or ACTIVE (if start date is today/past)
    
    Business Rules:
    - Only cancelled schedules can be uncancelled
    - Validates no overlapping schedules exist for the same locations and dates
    - Prioritizes making the schedule editable for administrative adjustments
    - ACTIVE status allows immediate editing of dates and coverage
    
    **schedule_id**: The unique identifier of the menu schedule to uncancel
    **reason**: Optional reason for uncancelling (for audit purposes)
    """
    return await service.uncancel_schedule(schedule_id, reason)

@router.get(
    "/citizen/menu",
    response_model=CitizenMenuResponse,
    summary="Get effective menu for citizens",
    description="Get the effective menu for a specific location and date for citizen consultation."
)
async def get_citizen_menu(
    location_id: str = Query(..., description="Location ID (campus or town ID)"),
    location_type: LocationType = Query(..., description="Location type: 'campus' or 'town'"),
    date: date = Query(..., description="Date to get the menu for (YYYY-MM-DD format)"),
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> CitizenMenuResponse:
    """
    Get the effective menu for a specific location and date.
    
    This endpoint allows citizens to consult what menu is being served
    at a specific location (campus or town) on a given date.
    
    The response includes:
    - Breakfast dishes with details
    - Lunch dishes with details  
    - Snack dishes with details
    - Nutritional information when available
    - Location and date information
    - Availability status and helpful messages
    
    **location_id**: The unique identifier of the campus or town
    **location_type**: Must be either 'campus' or 'town'
    **date**: The date to query in YYYY-MM-DD format
    
    The system will:
    1. Find the active menu schedule for the location and date
    2. Determine which day of the menu cycle corresponds to the date
    3. Return the breakfast, lunch, and snack dishes for that day
    4. Include dish details like name, description, and nutritional info
    
    If no menu is available for the specified location and date,
    the response will indicate this with is_available=false and
    provide a helpful message explaining why.
    """
    return await service.get_effective_menu_for_citizen(location_id, location_type.value, date)

@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a menu schedule",
    description="Permanently delete a menu schedule from the system."
)
async def delete_schedule(
    schedule_id: str,
    service: MenuScheduleService = Depends(lambda: menu_schedule_service)
) -> dict:
    """
    Delete a menu schedule.
    
    This action permanently removes the menu schedule from the system.
    
    **WARNING**: This is a permanent action and cannot be undone.
    
    Business Rules:
    - Schedules in any status can be deleted (ACTIVE, FUTURE, COMPLETED, CANCELLED)
    - Deletion removes all schedule data including coverage and cancellation information
    - Returns confirmation with deleted schedule details
    
    **schedule_id**: The unique identifier of the menu schedule to delete
    
    Returns:
    - Confirmation message with details of the deleted schedule
    """
    return await service.delete_schedule(schedule_id)

 