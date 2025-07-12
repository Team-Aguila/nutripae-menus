from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from models.menu_cycle import (
    MenuCycle,
    MenuCycleCreate,
    MenuCycleUpdate,
    MenuCycleResponse,
    MenuCycleStatus
)

class MenuCycleService:
    """Service class for menu cycle management operations"""

    @staticmethod
    async def create_menu_cycle(menu_cycle_data: MenuCycleCreate) -> MenuCycleResponse:
        """
        Create a new menu cycle with uniqueness validation
        
        Args:
            menu_cycle_data: The menu cycle data to create
            
        Returns:
            MenuCycleResponse: The created menu cycle
            
        Raises:
            HTTPException: If name already exists or creation fails
        """
        try:
            # Validate that all days have at least one dish per meal type
            for daily_menu in menu_cycle_data.daily_menus:
                if not daily_menu.breakfast_dish_ids and not daily_menu.lunch_dish_ids and not daily_menu.snack_dish_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Day {daily_menu.day} must have at least one dish assigned"
                    )

            menu_cycle = MenuCycle(**menu_cycle_data.model_dump())
            await menu_cycle.insert()
            
            return MenuCycleResponse(
                id=str(menu_cycle.id),
                **menu_cycle.model_dump(exclude={"id"})
            )
            
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu cycle with name '{menu_cycle_data.name}' already exists"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating menu cycle: {str(e)}"
            )

    @staticmethod
    async def get_menu_cycle_by_id(menu_cycle_id: str) -> MenuCycleResponse:
        """
        Get a menu cycle by its ID
        
        Args:
            menu_cycle_id: The menu cycle ID
            
        Returns:
            MenuCycleResponse: The menu cycle data
            
        Raises:
            HTTPException: If menu cycle not found
        """
        try:
            menu_cycle = await MenuCycle.get(PydanticObjectId(menu_cycle_id))
            if not menu_cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu cycle with id '{menu_cycle_id}' not found"
                )
            
            return MenuCycleResponse(
                id=str(menu_cycle.id),
                **menu_cycle.model_dump(exclude={"id"})
            )
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu cycle ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving menu cycle: {str(e)}"
            )

    @staticmethod
    async def get_all_menu_cycles(
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[MenuCycleResponse]:
        """
        Get all menu cycles with optional filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status_filter: Filter by status
            search: Search term for name
            
        Returns:
            List[MenuCycleResponse]: List of menu cycles
        """
        try:
            query = {}
            
            if status_filter:
                query["status"] = status_filter
                
            if search:
                query["name"] = {"$regex": search, "$options": "i"}
            
            menu_cycles = await MenuCycle.find(
                query,
                skip=skip,
                limit=limit
            ).to_list()
            
            return [
                MenuCycleResponse(
                    id=str(menu_cycle.id),
                    **menu_cycle.model_dump(exclude={"id"})
                )
                for menu_cycle in menu_cycles
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving menu cycles: {str(e)}"
            )

    @staticmethod
    async def update_menu_cycle(
        menu_cycle_id: str,
        menu_cycle_data: MenuCycleUpdate
    ) -> MenuCycleResponse:
        """
        Update a menu cycle
        
        Args:
            menu_cycle_id: The menu cycle ID
            menu_cycle_data: The update data
            
        Returns:
            MenuCycleResponse: The updated menu cycle
            
        Raises:
            HTTPException: If menu cycle not found or update fails
        """
        try:
            menu_cycle = await MenuCycle.get(PydanticObjectId(menu_cycle_id))
            if not menu_cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu cycle with id '{menu_cycle_id}' not found"
                )

            # If updating daily menus, validate that all days have at least one dish
            if menu_cycle_data.daily_menus:
                for daily_menu in menu_cycle_data.daily_menus:
                    if not daily_menu.breakfast_dish_ids and not daily_menu.lunch_dish_ids and not daily_menu.snack_dish_ids:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Day {daily_menu.day} must have at least one dish assigned"
                        )

            update_data = menu_cycle_data.model_dump(exclude_unset=True)
            await menu_cycle.update({"$set": update_data})
            menu_cycle.update_timestamp()
            await menu_cycle.save()
            
            return MenuCycleResponse(
                id=str(menu_cycle.id),
                **menu_cycle.model_dump(exclude={"id"})
            )
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu cycle ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating menu cycle: {str(e)}"
            )

    @staticmethod
    async def deactivate_menu_cycle(menu_cycle_id: str) -> MenuCycleResponse:
        """
        Deactivate a menu cycle
        
        Args:
            menu_cycle_id: The menu cycle ID
            
        Returns:
            MenuCycleResponse: The deactivated menu cycle
            
        Raises:
            HTTPException: If menu cycle not found or deactivation fails
        """
        try:
            menu_cycle = await MenuCycle.get(PydanticObjectId(menu_cycle_id))
            if not menu_cycle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu cycle with id '{menu_cycle_id}' not found"
                )

            # Check if menu cycle is assigned to any active or future schedules
            from pae_menus.models.menu_schedule import MenuSchedule, MenuScheduleStatus
            active_schedules = await MenuSchedule.find({
                "menu_cycle_id": menu_cycle.id,
                "status": {"$in": [MenuScheduleStatus.ACTIVE, MenuScheduleStatus.FUTURE]}
            }).to_list()

            if active_schedules:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate menu cycle that is assigned to active or future schedules"
                )

            menu_cycle.status = MenuCycleStatus.INACTIVE
            menu_cycle.update_timestamp()
            await menu_cycle.save()
            
            return MenuCycleResponse(
                id=str(menu_cycle.id),
                **menu_cycle.model_dump(exclude={"id"})
            )
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu cycle ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deactivating menu cycle: {str(e)}"
            )

# Create a singleton instance
menu_cycle_service = MenuCycleService() 