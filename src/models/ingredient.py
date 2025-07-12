from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime


class IngredientStatus(str, Enum):
    """
    Ingredient status values.
    
    Values:
    - active: Ingredient is available for use in menus
    - inactive: Ingredient is not available for new menus (soft deleted)
    """
    ACTIVE = "active"
    INACTIVE = "inactive"


class MenuUsageInfo(BaseModel):
    """Menu usage information for an ingredient"""
    dish_count: int = Field(0, description="Number of dishes using this ingredient")
    menu_cycle_count: int = Field(0, description="Number of menu cycles using this ingredient")
    dish_names: List[str] = Field(default=[], description="Names of dishes using this ingredient")
    last_used_date: Optional[datetime] = Field(None, description="Last date this ingredient was used in a menu")


class IngredientBase(BaseModel):
    """Base ingredient schema for request/response"""
    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name")
    base_unit_of_measure: str = Field(..., min_length=1, max_length=50, description="Base unit of measure (e.g., kg, L, units)")
    status: IngredientStatus = Field(default=IngredientStatus.ACTIVE, description="Ingredient status")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    category: Optional[str] = Field(None, max_length=100, description="Optional category")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()

    @field_validator('base_unit_of_measure')
    @classmethod
    def validate_unit(cls, v):
        if not v.strip():
            raise ValueError('Base unit of measure cannot be empty')
        return v.strip()


class IngredientCreate(IngredientBase):
    """Schema for creating an ingredient"""
    pass


class IngredientUpdate(BaseModel):
    """Schema for updating an ingredient"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    base_unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[IngredientStatus] = None
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else v

    @field_validator('base_unit_of_measure')
    @classmethod
    def validate_unit(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Base unit of measure cannot be empty')
        return v.strip() if v else v


class Ingredient(Document, IngredientBase):
    """Ingredient document model for MongoDB"""
    name: Indexed(str, unique=True) = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "ingredients"
        indexes = [
            "name",
            "status",
            "category",
            "created_at"
        ]

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()


class IngredientResponse(IngredientBase):
    """Schema for ingredient response"""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class IngredientDetailedResponse(IngredientBase):
    """Schema for detailed ingredient response with menu usage information"""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    menu_usage: MenuUsageInfo = Field(default_factory=MenuUsageInfo, description="Menu usage details")

    class Config:
        populate_by_name = True 