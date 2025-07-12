from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime
from models.commons import DailyMenu

class MenuCycleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class MenuCycleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique name for the menu cycle")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    status: MenuCycleStatus = Field(default=MenuCycleStatus.ACTIVE, description="Status of the menu cycle")
    duration_days: int = Field(..., gt=0, description="Duration of the cycle in days (e.g., 7 for a week)")
    daily_menus: List[DailyMenu] = Field(..., description="List of daily menus for the duration of the cycle")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()


class MenuCycleCreate(MenuCycleBase):
    pass


class MenuCycleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[MenuCycleStatus] = None
    duration_days: Optional[int] = Field(None, gt=0)
    daily_menus: Optional[List[DailyMenu]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else v


class MenuCycle(Document, MenuCycleBase):
    name: Indexed(str, unique=True) = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "menu_cycles"
        indexes = [
            "name",
            "status",
            "duration_days"
        ]

    def update_timestamp(self):
        self.updated_at = datetime.utcnow()


class MenuCycleResponse(MenuCycleBase):
    id: PydanticObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True 