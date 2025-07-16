from typing import List, Optional
from datetime import date, timedelta
from beanie import PydanticObjectId
from fastapi import HTTPException, status

from models.menu_schedule import (
    MenuSchedule,
    MenuScheduleCreate,
    MenuScheduleUpdate,
    MenuScheduleResponse,
    MenuScheduleStatus,
    MenuScheduleAssignmentRequest,
    MenuScheduleAssignmentSummary,
    Coverage,
    LocationType,
    LocationInfo,
    CitizenMenuResponse,
    DishInMenu
)
from models.menu_cycle import MenuCycle, MenuCycleStatus
from services.coverage_service import coverage_service, CoverageService

class MenuScheduleService:
    """Service class for menu schedule management operations"""

    def __init__(self, coverage_svc: CoverageService = coverage_service):
        self.coverage_service = coverage_svc

    async def assign_menu_cycle(self, assignment_request: MenuScheduleAssignmentRequest) -> MenuScheduleAssignmentSummary:
        """
        Assign a menu cycle to locations for a specific date range
        
        Args:
            assignment_request: The assignment request with cycle, locations, and dates
            
        Returns:
            MenuScheduleAssignmentSummary: Summary of the created assignment
            
        Raises:
            HTTPException: If validation fails or assignment cannot be created
        """
        
        # 1. Validate menu cycle exists and is active
        try:
            menu_cycle = await MenuCycle.get(PydanticObjectId(assignment_request.menu_cycle_id))
            if not menu_cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu cycle with id '{assignment_request.menu_cycle_id}' not found"
                )
            
            if menu_cycle.status != MenuCycleStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot assign inactive menu cycle"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu cycle ID format"
            )

        # 2. Validate that at least one location is provided
        if not assignment_request.campus_ids and not assignment_request.town_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one campus or town must be selected"
            )

        # 3. Validate locations exist
        validated_campuses = []
        validated_towns = []
        
        if assignment_request.campus_ids:
            validated_campuses = await self.coverage_service.validate_campus_ids(assignment_request.campus_ids)
        
        if assignment_request.town_ids:
            validated_towns = await self.coverage_service.validate_town_ids(assignment_request.town_ids)

        # 4. Check for overlapping schedules
        await self._check_overlapping_schedules(
            assignment_request.campus_ids,
            assignment_request.town_ids,
            assignment_request.start_date,
            assignment_request.end_date
        )

        # 5. Create coverage list
        coverage = []
        location_infos = []
        
        for campus in validated_campuses:
            coverage.append(Coverage(
                location_id=str(campus.id),
                location_type=LocationType.CAMPUS,
                location_name=campus.name
            ))
            location_infos.append(LocationInfo(
                id=str(campus.id),
                name=campus.name,
                location_type=LocationType.CAMPUS
            ))
        
        for town in validated_towns:
            coverage.append(Coverage(
                location_id=str(town.id),
                location_type=LocationType.TOWN,
                location_name=town.name
            ))
            location_infos.append(LocationInfo(
                id=str(town.id),
                name=town.name,
                location_type=LocationType.TOWN
            ))

        # 6. Create menu schedule
        schedule_data = MenuScheduleCreate(
            menu_cycle_id=menu_cycle.id,
            coverage=coverage,
            start_date=assignment_request.start_date,
            end_date=assignment_request.end_date,
            status=MenuScheduleStatus.FUTURE if assignment_request.start_date > date.today() else MenuScheduleStatus.ACTIVE
        )
        
        schedule = MenuSchedule(**schedule_data.model_dump())
        await schedule.insert()

        # 7. Calculate duration and return summary
        duration_days = (assignment_request.end_date - assignment_request.start_date).days + 1
        
        return MenuScheduleAssignmentSummary(
            menu_cycle_id=str(menu_cycle.id),
            menu_cycle_name=menu_cycle.name,
            locations=location_infos,
            start_date=assignment_request.start_date,
            end_date=assignment_request.end_date,
            duration_days=duration_days,
            schedule_id=str(schedule.id)
        )

    async def _check_overlapping_schedules(
        self,
        campus_ids: List[str],
        town_ids: List[str],
        start_date: date,
        end_date: date,
        exclude_schedule_id: Optional[str] = None
    ):
        """Check for overlapping schedules for the same locations"""
        
        location_ids = campus_ids + town_ids
        
        # Build query to find existing schedules that overlap with the requested date range
        query = {
            "coverage.location_id": {"$in": location_ids},
            "status": {"$in": [MenuScheduleStatus.ACTIVE, MenuScheduleStatus.FUTURE]},
            "$or": [
                # Schedule starts before our end date and ends after our start date
                {"start_date": {"$lte": end_date}, "end_date": {"$gte": start_date}}
            ]
        }
        
        # Exclude the current schedule if this is an update operation
        if exclude_schedule_id:
            query["_id"] = {"$ne": PydanticObjectId(exclude_schedule_id)}
        
        overlapping_schedules = await MenuSchedule.find(query).to_list()

        if overlapping_schedules:
            conflicting_locations = set()
            for schedule in overlapping_schedules:
                for coverage in schedule.coverage:
                    if coverage.location_id in location_ids:
                        conflicting_locations.add(coverage.location_name)
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Schedule conflict detected for locations: {', '.join(conflicting_locations)}. "
                       f"There are already active or future schedules for these locations in the requested date range."
            )

    async def get_all_schedules(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[MenuScheduleStatus] = None,
        menu_cycle_id: Optional[str] = None,
        location_id: Optional[str] = None,
        location_type: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        end_date_from: Optional[date] = None,
        end_date_to: Optional[date] = None
    ) -> List[MenuScheduleResponse]:
        """Get all menu schedules with enhanced filtering for administrators"""
        
        query = {}
        
        # Status filter
        if status_filter:
            query["status"] = status_filter.value
        
        # Menu cycle filter
        if menu_cycle_id:
            try:
                query["menu_cycle_id"] = PydanticObjectId(menu_cycle_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid menu cycle ID format"
                )
        
        # Location coverage filter
        if location_id and location_type:
            query["coverage"] = {
                "$elemMatch": {
                    "location_id": location_id,
                    "location_type": location_type.lower()
                }
            }
        elif location_id:  # Search in any location type
            query["coverage.location_id"] = location_id
        
        # Date range filters
        date_conditions = []
        if start_date_from:
            date_conditions.append({"start_date": {"$gte": start_date_from}})
        if start_date_to:
            date_conditions.append({"start_date": {"$lte": start_date_to}})
        if end_date_from:
            date_conditions.append({"end_date": {"$gte": end_date_from}})
        if end_date_to:
            date_conditions.append({"end_date": {"$lte": end_date_to}})
        
        if date_conditions:
            query["$and"] = date_conditions

        schedules = await MenuSchedule.find(
            query,
            skip=skip,
            limit=limit
        ).sort("-created_at").to_list()

        return [
            MenuScheduleResponse(
                id=str(schedule.id),
                **schedule.model_dump(exclude={"id"})
            )
            for schedule in schedules
        ]

    async def get_schedule_by_id(self, schedule_id: str) -> MenuScheduleResponse:
        """Get a specific menu schedule by ID"""
        
        try:
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )
            
            return MenuScheduleResponse(
                id=str(schedule.id),
                **schedule.model_dump(exclude={"id"})
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule ID format"
            )

    async def get_schedule_detailed_view(self, schedule_id: str) -> "ScheduleDetailedResponse":
        """Get detailed schedule view with daily effective menus for administrators"""
        from models.menu_schedule import ScheduleDetailedResponse, DailyMenuByLocation
        from models.menu_cycle import MenuCycle
        from datetime import timedelta
        
        try:
            # Get the schedule
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )
            
            # Get the menu cycle
            menu_cycle = await MenuCycle.get(schedule.menu_cycle_id)
            if not menu_cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Associated menu cycle not found"
                )
            
            # Calculate all dates in the schedule
            schedule_dates = []
            current_date = schedule.start_date
            while current_date <= schedule.end_date:
                schedule_dates.append(current_date)
                current_date += timedelta(days=1)
            
            # Generate daily menus for each location and date
            daily_menus = []
            
            for coverage in schedule.coverage:
                for schedule_date in schedule_dates:
                    # Calculate which day of the cycle corresponds to this date
                    days_since_start = (schedule_date - schedule.start_date).days
                    cycle_day = (days_since_start % menu_cycle.duration_days) + 1
                    
                    # Find the daily menu for this day
                    daily_menu_data = None
                    for dm in menu_cycle.daily_menus:
                        if dm.day == cycle_day:
                            daily_menu_data = dm
                            break
                    
                    # Get dish details for each meal type
                    breakfast_dishes = []
                    lunch_dishes = []
                    snack_dishes = []
                    
                    if daily_menu_data:
                        breakfast_dishes = await self._get_dish_details_simple(daily_menu_data.breakfast_dish_ids)
                        lunch_dishes = await self._get_dish_details_simple(daily_menu_data.lunch_dish_ids)
                        snack_dishes = await self._get_dish_details_simple(daily_menu_data.snack_dish_ids)
                    
                    daily_menu = DailyMenuByLocation(
                        date=schedule_date,
                        location_id=coverage.location_id,
                        location_name=coverage.location_name,
                        location_type=coverage.location_type,
                        cycle_day=cycle_day,
                        breakfast_dishes=breakfast_dishes,
                        lunch_dishes=lunch_dishes,
                        snack_dishes=snack_dishes
                    )
                    
                    daily_menus.append(daily_menu)
            
            return ScheduleDetailedResponse(
                id=str(schedule.id),
                menu_cycle_id=str(schedule.menu_cycle_id),
                menu_cycle_name=menu_cycle.name,
                coverage=schedule.coverage,
                start_date=schedule.start_date,
                end_date=schedule.end_date,
                status=schedule.status,
                daily_menus=daily_menus,
                created_at=schedule.created_at,
                updated_at=schedule.updated_at
            )
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving schedule details: {str(e)}"
            )

    async def update_schedule(
        self,
        schedule_id: str,
        schedule_data: MenuScheduleUpdate
    ) -> MenuScheduleResponse:
        """Update a menu schedule with comprehensive validation"""
        
        try:
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )

            # 1. Validate that only ACTIVE or FUTURE schedules can be edited
            if schedule.status not in [MenuScheduleStatus.ACTIVE, MenuScheduleStatus.FUTURE]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot edit schedule with status '{schedule.status.value}'. "
                           f"Only active or future schedules can be modified."
                )

            # 2. Validate date consistency if end_date is being updated
            if schedule_data.end_date and schedule_data.end_date < schedule.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date cannot be before start date"
                )

            # 3. Validate and process coverage if being updated
            validated_coverage = schedule.coverage  # Default to existing coverage
            if schedule_data.coverage is not None:
                # Validate that at least one location is provided
                if not schedule_data.coverage:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="At least one location must be selected"
                    )

                # Extract location IDs for validation
                campus_ids = []
                town_ids = []
                for coverage in schedule_data.coverage:
                    if coverage.location_type == LocationType.CAMPUS:
                        campus_ids.append(coverage.location_id)
                    elif coverage.location_type == LocationType.TOWN:
                        town_ids.append(coverage.location_id)

                # Validate that all locations exist in the coverage service
                if campus_ids:
                    await self.coverage_service.validate_campus_ids(campus_ids)
                if town_ids:
                    await self.coverage_service.validate_town_ids(town_ids)

                validated_coverage = schedule_data.coverage

            # 4. Check for overlapping schedules if coverage or end_date is being updated
            if schedule_data.coverage is not None or schedule_data.end_date is not None:
                # Extract location IDs from validated coverage
                campus_ids = []
                town_ids = []
                for coverage in validated_coverage:
                    if coverage.location_type == LocationType.CAMPUS:
                        campus_ids.append(coverage.location_id)
                    elif coverage.location_type == LocationType.TOWN:
                        town_ids.append(coverage.location_id)

                # Use updated end_date if provided, otherwise use existing end_date
                check_end_date = schedule_data.end_date if schedule_data.end_date else schedule.end_date

                await self._check_overlapping_schedules(
                    campus_ids=campus_ids,
                    town_ids=town_ids,
                    start_date=schedule.start_date,
                    end_date=check_end_date,
                    exclude_schedule_id=schedule_id
                )

            # 5. Update the schedule
            update_data = schedule_data.model_dump(exclude_unset=True)
            await schedule.update({"$set": update_data})
            schedule.update_timestamp()
            await schedule.save()
            
            return MenuScheduleResponse(
                id=str(schedule.id),
                **schedule.model_dump(exclude={"id"})
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule ID format"
            )

    async def cancel_schedule(self, schedule_id: str, reason: Optional[str] = None) -> MenuScheduleResponse:
        """Cancel a menu schedule"""
        
        try:
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )

            if schedule.status == MenuScheduleStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Schedule is already cancelled"
                )

            if schedule.status == MenuScheduleStatus.COMPLETED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot cancel completed schedule"
                )

            from models.menu_schedule import CancellationInfo
            schedule.status = MenuScheduleStatus.CANCELLED
            schedule.cancellation_info = CancellationInfo(reason=reason)
            schedule.update_timestamp()
            await schedule.save()
            
            return MenuScheduleResponse(
                id=str(schedule.id),
                **schedule.model_dump(exclude={"id"})
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule ID format"
            )

    async def uncancel_schedule(self, schedule_id: str, reason: Optional[str] = None) -> MenuScheduleResponse:
        """Uncancel a menu schedule and restore it to its appropriate status"""
        
        try:
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )

            if schedule.status != MenuScheduleStatus.CANCELLED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot uncancel schedule with status '{schedule.status.value}'. "
                           f"Only cancelled schedules can be uncancelled."
                )

            # Determine the appropriate status based on dates
            # When uncancelling, we prioritize making the schedule editable
            today = date.today()
            if schedule.start_date > today:
                # If the start date is in the future, it should be future
                new_status = MenuScheduleStatus.FUTURE
            else:
                # If start date is today or in the past, make it ACTIVE so it can be edited
                # This allows administrators to update dates and make necessary adjustments
                new_status = MenuScheduleStatus.ACTIVE

            # Check for overlapping schedules before uncancelling
            # Extract location IDs for validation
            campus_ids = []
            town_ids = []
            for coverage in schedule.coverage:
                if coverage.location_type == LocationType.CAMPUS:
                    campus_ids.append(coverage.location_id)
                elif coverage.location_type == LocationType.TOWN:
                    town_ids.append(coverage.location_id)

            # Only check for overlaps if the schedule would be active or future
            if new_status in [MenuScheduleStatus.ACTIVE, MenuScheduleStatus.FUTURE]:
                await self._check_overlapping_schedules(
                    campus_ids=campus_ids,
                    town_ids=town_ids,
                    start_date=schedule.start_date,
                    end_date=schedule.end_date,
                    exclude_schedule_id=schedule_id
                )

            # Clear cancellation info and update status
            schedule.status = new_status
            schedule.cancellation_info = None
            schedule.update_timestamp()
            await schedule.save()
            
            return MenuScheduleResponse(
                id=str(schedule.id),
                **schedule.model_dump(exclude={"id"})
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule ID format"
            )

    async def delete_schedule(self, schedule_id: str) -> dict:
        """Delete a menu schedule"""
        
        try:
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )

            # Store schedule info for response before deletion
            schedule_info = {
                "id": str(schedule.id),
                "menu_cycle_id": str(schedule.menu_cycle_id),
                "start_date": schedule.start_date.isoformat(),
                "end_date": schedule.end_date.isoformat(),
                "status": schedule.status.value,
                "coverage_count": len(schedule.coverage)
            }

            # Perform the deletion
            await schedule.delete()
            
            return {
                "message": f"Menu schedule '{schedule_id}' has been successfully deleted",
                "deleted_schedule": schedule_info
            }
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid schedule ID format"
            )

    async def get_effective_menu_for_citizen(
        self, 
        location_id: str, 
        location_type: str, 
        query_date: date
    ) -> "CitizenMenuResponse":
        """
        Get the effective menu for a specific location and date for citizen consultation.
        
        This method:
        1. Finds the active menu schedule for the location and date
        2. Gets the corresponding menu cycle
        3. Calculates which day of the cycle corresponds to the requested date
        4. Retrieves dish details for breakfast, lunch, and snack
        5. Returns organized menu information
        
        Args:
            location_id: The campus or town ID
            location_type: Either "campus" or "town"
            query_date: The date for which to get the menu
            
        Returns:
            CitizenMenuResponse: The effective menu for the date and location
        """
        from models.menu_cycle import MenuCycle
        from models.dish import Dish
        
        try:
            # 1. Find active menu schedule for this location and date
            query = {
                "coverage.location_id": location_id,
                "coverage.location_type": location_type.lower(),
                "start_date": {"$lte": query_date},
                "end_date": {"$gte": query_date},
                "status": {"$in": [MenuScheduleStatus.ACTIVE, MenuScheduleStatus.FUTURE]}
            }
            
            schedule = await MenuSchedule.find_one(query)
            
            if not schedule:
                # Try to get location name from coverage service for better response
                location_name = "Unknown Location"
                try:
                    if location_type.lower() == "campus":
                        campuses = await self.coverage_service.validate_campus_ids([location_id])
                        if campuses:
                            location_name = campuses[0].name
                    elif location_type.lower() == "town":
                        towns = await self.coverage_service.validate_town_ids([location_id])
                        if towns:
                            location_name = towns[0].name
                except:
                    pass  # Keep default location name if validation fails
                
                return CitizenMenuResponse(
                    location_id=location_id,
                    location_name=location_name,
                    location_type=location_type,
                    menu_date=query_date,
                    menu_cycle_name="",
                    breakfast=[],
                    lunch=[],
                    snack=[],
                    is_available=False,
                    message=f"No menu schedule found for this location and date. Please check if the date is within an active menu period."
                )
            
            # Get location name from the schedule coverage
            location_name = "Unknown Location"
            for coverage in schedule.coverage:
                if coverage.location_id == location_id:
                    location_name = coverage.location_name
                    break
            
            # 2. Get the menu cycle
            menu_cycle = await MenuCycle.get(schedule.menu_cycle_id)
            if not menu_cycle:
                return CitizenMenuResponse(
                    location_id=location_id,
                    location_name=location_name,
                    location_type=location_type,
                    menu_date=query_date,
                    menu_cycle_name="",
                    breakfast=[],
                    lunch=[],
                    snack=[],
                    is_available=False,
                    message="Menu cycle not found. Please contact administration."
                )
            
            # 3. Calculate which day of the cycle corresponds to the requested date
            days_since_start = (query_date - schedule.start_date).days
            cycle_day = (days_since_start % menu_cycle.duration_days) + 1
            
            # 4. Find the daily menu for this day
            daily_menu = None
            for dm in menu_cycle.daily_menus:
                if dm.day == cycle_day:
                    daily_menu = dm
                    break
            
            if not daily_menu:
                return CitizenMenuResponse(
                    location_id=location_id,
                    location_name=location_name,
                    location_type=location_type,
                    menu_date=query_date,
                    menu_cycle_name=menu_cycle.name,
                    breakfast=[],
                    lunch=[],
                    snack=[],
                    is_available=False,
                    message=f"No menu configured for day {cycle_day} of the cycle."
                )
            
            # 5. Get dish details for each meal type
            breakfast_dishes = await self._get_dish_details(daily_menu.breakfast_dish_ids)
            lunch_dishes = await self._get_dish_details(daily_menu.lunch_dish_ids)
            snack_dishes = await self._get_dish_details(daily_menu.snack_dish_ids)
            
            return CitizenMenuResponse(
                location_id=location_id,
                location_name=location_name,
                location_type=location_type,
                menu_date=query_date,
                menu_cycle_name=menu_cycle.name,
                breakfast=breakfast_dishes,
                lunch=lunch_dishes,
                snack=snack_dishes,
                is_available=True,
                message=None
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving menu: {str(e)}"
            )
    
    async def _get_dish_details(self, dish_ids: List[PydanticObjectId]) -> List["DishInMenu"]:
        """Helper method to get dish details and convert to DishInMenu format"""
        from models.dish import Dish
        
        if not dish_ids:
            return []
        
        dishes = await Dish.find({"_id": {"$in": dish_ids}}).to_list()
        
        dish_in_menu_list = []
        for dish in dishes:
            nutritional_info = None
            if dish.nutritional_info:
                nutritional_info = {
                    "calories": dish.nutritional_info.calories,
                    "protein": dish.nutritional_info.protein,
                    "photo_url": dish.nutritional_info.photo_url
                }
            
            dish_in_menu_list.append(DishInMenu(
                id=str(dish.id),
                name=dish.name,
                description=dish.description,
                nutritional_info=nutritional_info
            ))
        
        return dish_in_menu_list

# Create singleton instance
menu_schedule_service = MenuScheduleService() 