from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime
from .commons import Recipe, MealType

class DishStatus(str, Enum):
    """
    Dish status values.
    
    Values:
    - active: Dish is available for use in menus
    - inactive: Dish is not available for new menus (soft deleted)
    """
    ACTIVE = "active"
    INACTIVE = "inactive"

class DishType(str, Enum):
    """
    Dish type categories for nutritional classification.
    
    Values:
    - protein: Protein-rich dishes (meat, fish, eggs, legumes)
    - cereal: Cereal and grain-based dishes (rice, pasta, bread)
    - vegetable: Vegetable-based dishes and salads
    - fruit: Fruit-based dishes and desserts
    - dairy: Dairy-based dishes (yogurt, cheese, milk)
    - other: Other types not covered by main categories
    """
    PROTEIN = "protein"
    CEREAL = "cereal"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    DAIRY = "dairy"
    OTHER = "other"


class DishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Dish name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description of the dish")
    status: DishStatus = Field(default=DishStatus.ACTIVE, description="Dish status")
    dish_type: DishType = Field(..., description="Type of dish")
    recipe: Recipe = Field(..., description="Recipe of the dish")
    nutritional_info: Optional[dict] = Field({}, description="Nutritional information per serving")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip()


class DishCreate(DishBase):
    pass


class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[DishStatus] = None
    dish_type: Optional[DishType] = None
    recipe: Optional[Recipe] = None
    nutritional_info: Optional[dict] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else v


class Dish(Document, DishBase):
    name: Indexed(str, unique=True) = Field(..., min_length=1, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "dishes"
        indexes = [
            "name",
            "status",
            "dish_type",
        ]
    
    def update_timestamp(self):
        self.updated_at = datetime.utcnow()


class DishResponse(DishBase):
    id: PydanticObjectId = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True 