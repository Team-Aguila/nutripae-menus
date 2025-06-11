# pae_menus/services/ingredient_service.py
from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from pae_menus.models.ingredient import (
    Ingredient, 
    IngredientCreate, 
    IngredientUpdate, 
    IngredientResponse
)


class IngredientService:
    """Service class for ingredient management operations"""

    @staticmethod
    async def create_ingredient(ingredient_data: IngredientCreate) -> IngredientResponse:
        """
        Create a new ingredient with uniqueness validation
        
        Args:
            ingredient_data: The ingredient data to create
            
        Returns:
            IngredientResponse: The created ingredient
            
        Raises:
            HTTPException: If name already exists or creation fails
        """
        try:
            # Check if ingredient with same name already exists
            existing = await Ingredient.find_one({"name": {"$regex": f"^{ingredient_data.name}$", "$options": "i"}})
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingredient with name '{ingredient_data.name}' already exists"
                )
            
            # Create new ingredient
            ingredient = Ingredient(**ingredient_data.model_dump())
            await ingredient.insert()
            
            return IngredientResponse(
                id=str(ingredient.id),
                **ingredient.model_dump(exclude={"id"})
            )
            
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient with name '{ingredient_data.name}' already exists"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating ingredient: {str(e)}"
            )

    @staticmethod
    async def get_ingredient_by_id(ingredient_id: str) -> IngredientResponse:
        """
        Get an ingredient by its ID
        
        Args:
            ingredient_id: The ingredient ID
            
        Returns:
            IngredientResponse: The ingredient data
            
        Raises:
            HTTPException: If ingredient not found
        """
        try:
            ingredient = await Ingredient.get(PydanticObjectId(ingredient_id))
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id '{ingredient_id}' not found"
                )
            
            return IngredientResponse(
                id=str(ingredient.id),
                **ingredient.model_dump(exclude={"id"})
            )
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ingredient ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving ingredient: {str(e)}"
            )

    @staticmethod
    async def get_all_ingredients(
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[IngredientResponse]:
        """
        Get all ingredients with optional filtering and pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status_filter: Filter by ingredient status
            category_filter: Filter by ingredient category
            search: Search term for ingredient name
            
        Returns:
            List[IngredientResponse]: List of ingredients
        """
        try:
            # Build query
            query = {}
            
            if status_filter:
                query["status"] = status_filter
                
            if category_filter:
                query["category"] = category_filter
                
            if search:
                query["name"] = {"$regex": search, "$options": "i"}
            
            # Execute query
            ingredients = await Ingredient.find(query).skip(skip).limit(limit).to_list()
            
            return [
                IngredientResponse(
                    id=str(ingredient.id),
                    **ingredient.model_dump(exclude={"id"})
                )
                for ingredient in ingredients
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving ingredients: {str(e)}"
            )

    @staticmethod
    async def update_ingredient(ingredient_id: str, ingredient_data: IngredientUpdate) -> IngredientResponse:
        """
        Update an existing ingredient
        
        Args:
            ingredient_id: The ingredient ID to update
            ingredient_data: The updated ingredient data
            
        Returns:
            IngredientResponse: The updated ingredient
            
        Raises:
            HTTPException: If ingredient not found or name already exists
        """
        try:
            # Get existing ingredient
            ingredient = await Ingredient.get(PydanticObjectId(ingredient_id))
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id '{ingredient_id}' not found"
                )
            
            # Check name uniqueness if name is being updated
            update_data = ingredient_data.model_dump(exclude_unset=True)
            if "name" in update_data and update_data["name"] != ingredient.name:
                existing = await Ingredient.find_one({
                    "name": {"$regex": f"^{update_data['name']}$", "$options": "i"},
                    "_id": {"$ne": ingredient.id}
                })
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Ingredient with name '{update_data['name']}' already exists"
                    )
            
            # Update ingredient
            for field, value in update_data.items():
                setattr(ingredient, field, value)
            
            ingredient.update_timestamp()
            await ingredient.save()
            
            return IngredientResponse(
                id=str(ingredient.id),
                **ingredient.model_dump(exclude={"id"})
            )
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ingredient ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating ingredient: {str(e)}"
            )

    @staticmethod
    async def delete_ingredient(ingredient_id: str) -> dict:
        """
        Delete an ingredient by its ID
        
        Args:
            ingredient_id: The ingredient ID to delete
            
        Returns:
            dict: Confirmation message
            
        Raises:
            HTTPException: If ingredient not found
        """
        try:
            ingredient = await Ingredient.get(PydanticObjectId(ingredient_id))
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id '{ingredient_id}' not found"
                )
            
            await ingredient.delete()
            return {"message": f"Ingredient '{ingredient.name}' deleted successfully"}
            
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ingredient ID format"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting ingredient: {str(e)}"
            )

    @staticmethod
    async def check_name_uniqueness(name: str, exclude_id: Optional[str] = None) -> bool:
        """
        Check if an ingredient name is unique
        
        Args:
            name: The name to check
            exclude_id: Optional ID to exclude from check (for updates)
            
        Returns:
            bool: True if name is unique, False otherwise
        """
        try:
            query = {"name": {"$regex": f"^{name}$", "$options": "i"}}
            
            if exclude_id:
                query["_id"] = {"$ne": PydanticObjectId(exclude_id)}
            
            existing = await Ingredient.find_one(query)
            return existing is None
            
        except Exception:
            return False 