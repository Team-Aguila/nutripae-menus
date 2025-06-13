from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import date, datetime

class MenuScheduleStatus(str, Enum):
    ACTIVE = "active"
    FUTURE = "future"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LocationType(str, Enum):
    CAMPUS = "campus"
    TOWN = "town"

class Coverage(BaseModel):
    location_id: str = Field(..., description="Identifier for the location (Campus ID or Town ID)")
    location_type: LocationType = Field(..., description="Type of location - campus or town")
    location_name: str = Field(..., description="Display name of the location")

class CancellationInfo(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for cancellation")
    cancelled_at: datetime = Field(default_factory=datetime.utcnow)
    # user_id: Optional[str] = Field(None, description="User who cancelled the schedule")


class MenuScheduleBase(BaseModel):
    menu_cycle_id: PydanticObjectId = Field(..., description="Reference to the MenuCycle")
    coverage: List[Coverage] = Field(..., description="List of locations covered by this schedule")
    start_date: date = Field(..., description="Start date of the schedule")
    end_date: date = Field(..., description="End date of the schedule")
    status: MenuScheduleStatus = Field(default=MenuScheduleStatus.FUTURE, description="Status of the schedule")
    cancellation_info: Optional[CancellationInfo] = Field(None, description="Details if the schedule is cancelled")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, values):
        if 'start_date' in values.data and v < values.data['start_date']:
            raise ValueError('End date cannot be before start date')
        return v

    @field_validator('coverage')
    @classmethod
    def validate_coverage(cls, v):
        if not v:
            raise ValueError('At least one location must be selected')
        return v

class MenuScheduleAssignmentRequest(BaseModel):
    menu_cycle_id: str = Field(..., description="ID of the menu cycle to assign")
    campus_ids: List[str] = Field(default=[], description="List of campus IDs to assign")
    town_ids: List[str] = Field(default=[], description="List of town IDs to assign") 
    start_date: date = Field(..., description="Start date of the assignment")
    end_date: date = Field(..., description="End date of the assignment")

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, values):
        if 'start_date' in values.data and v < values.data['start_date']:
            raise ValueError('End date cannot be before start date')
        return v

    @field_validator('campus_ids', 'town_ids')
    @classmethod
    def validate_locations(cls, v, values):
        # Check that at least one campus or town is selected
        if 'campus_ids' in values.data and 'town_ids' in values.data:
            if not values.data['campus_ids'] and not values.data['town_ids']:
                raise ValueError('At least one campus or town must be selected')
        elif not v:  # If this is the first field being validated
            return v  # Let the other validator handle the check
        return v

class MenuScheduleCreate(MenuScheduleBase):
    pass


class MenuScheduleUpdate(BaseModel):
    coverage: Optional[List[Coverage]] = None
    end_date: Optional[date] = None
    status: Optional[MenuScheduleStatus] = None
    cancellation_info: Optional[CancellationInfo] = None
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, values):
        # In updates, we might not have the start_date, so this validation is tricky
        # It should be handled at the service level where we have the full object
        return v


class MenuSchedule(Document, MenuScheduleBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "menu_schedules"
        indexes = [
            "menu_cycle_id",
            "start_date",
            "end_date",
            "status",
        ]

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()

class MenuScheduleResponse(MenuScheduleBase):
    id: PydanticObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True 

class LocationInfo(BaseModel):
    id: str
    name: str
    location_type: LocationType

class MenuScheduleAssignmentSummary(BaseModel):
    menu_cycle_id: str
    menu_cycle_name: str
    locations: List[LocationInfo]
    start_date: date
    end_date: date
    duration_days: int
    schedule_id: str

# New models for citizen menu consultation
class DishInMenu(BaseModel):
    id: str = Field(..., description="Dish ID")
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Dish description")
    nutritional_info: Optional[dict] = Field(None, description="Nutritional information including calories, protein, and photo URL")

class MealMenuDetails(BaseModel):
    meal_type: str = Field(..., description="Type of meal (breakfast, lunch, snack)")
    dishes: List[DishInMenu] = Field(..., description="List of dishes for this meal")

class CitizenMenuResponse(BaseModel):
    location_id: str = Field(..., description="Location ID")
    location_name: str = Field(..., description="Location name") 
    location_type: str = Field(..., description="Location type (campus or town)")
    menu_date: date = Field(..., description="Date for which the menu is shown")
    menu_cycle_name: str = Field(..., description="Name of the menu cycle")
    breakfast: List[DishInMenu] = Field(..., description="Breakfast dishes")
    lunch: List[DishInMenu] = Field(..., description="Lunch dishes")
    snack: List[DishInMenu] = Field(..., description="Snack dishes")
    is_available: bool = Field(..., description="Whether a menu is available for this date and location")
    message: Optional[str] = Field(None, description="Additional information or reasons why menu might not be available") 