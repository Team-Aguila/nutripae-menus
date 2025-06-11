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

class Coverage(BaseModel):
    # Assuming location_id refers to a "Sede" or "Municipio"
    location_id: str = Field(..., description="Identifier for the location (e.g., Sede ID)")
    

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