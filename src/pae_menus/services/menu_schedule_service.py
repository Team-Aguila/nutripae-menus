from typing import List, Optional
from datetime import date, timedelta
from beanie import PydanticObjectId
from fastapi import HTTPException, status

from pae_menus.models.menu_schedule import (
    MenuSchedule,
    MenuScheduleCreate,
    MenuScheduleUpdate,
    MenuScheduleResponse,
    MenuScheduleStatus,
    MenuScheduleAssignmentRequest,
    MenuScheduleAssignmentSummary,
    Coverage,
    LocationType,
    LocationInfo
)
from pae_menus.models.menu_cycle import MenuCycle, MenuCycleStatus
from pae_menus.services.coverage_service import coverage_service, CoverageService

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
        end_date: date
    ):
        """Check for overlapping schedules for the same locations"""
        
        location_ids = campus_ids + town_ids
        
        # Find existing schedules that overlap with the requested date range
        overlapping_schedules = await MenuSchedule.find({
            "coverage.location_id": {"$in": location_ids},
            "status": {"$in": [MenuScheduleStatus.ACTIVE, MenuScheduleStatus.FUTURE]},
            "$or": [
                # Schedule starts before our end date and ends after our start date
                {"start_date": {"$lte": end_date}, "end_date": {"$gte": start_date}}
            ]
        }).to_list()

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
        status_filter: Optional[MenuScheduleStatus] = None
    ) -> List[MenuScheduleResponse]:
        """Get all menu schedules with optional filtering"""
        
        query = {}
        if status_filter:
            query["status"] = status_filter.value

        schedules = await MenuSchedule.find(
            query,
            skip=skip,
            limit=limit
        ).to_list()

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

    async def update_schedule(
        self,
        schedule_id: str,
        schedule_data: MenuScheduleUpdate
    ) -> MenuScheduleResponse:
        """Update a menu schedule"""
        
        try:
            schedule = await MenuSchedule.get(PydanticObjectId(schedule_id))
            if not schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu schedule with id '{schedule_id}' not found"
                )

            # Validate date consistency if end_date is being updated
            if schedule_data.end_date and schedule_data.end_date < schedule.start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date cannot be before start date"
                )

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

            from pae_menus.models.menu_schedule import CancellationInfo
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

# Create singleton instance
menu_schedule_service = MenuScheduleService() 