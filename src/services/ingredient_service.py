# pae_menus/services/ingredient_service.py
from typing import List, Optional
from beanie import PydanticObjectId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from models.ingredient import (
    Ingredient, 
    IngredientCreate, 
    IngredientUpdate, 
    IngredientResponse,
    IngredientDetailedResponse,
    MenuUsageInfo,
    IngredientStatus
)
from models.dish import Dish
from models.menu_cycle import MenuCycle


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
            
            # Refresh from database to ensure consistency
            created_ingredient = await Ingredient.get(ingredient.id)
            if not created_ingredient:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create ingredient - database consistency error"
                )
            
            return IngredientResponse(
                id=str(created_ingredient.id),
                **created_ingredient.model_dump(exclude={"id"})
            )
            
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient with name '{ingredient_data.name}' already exists"
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {str(e)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {str(e)}"
            )
        except HTTPException:
            # Re-raise HTTPExceptions without wrapping them
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating ingredient: {str(e)}"
            )

    @staticmethod
    async def get_active_ingredients(
        skip: int = 0, 
        limit: int = 100, 
        category_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[IngredientResponse]:
        """
        Get only active ingredients available for menu creation.
        This method specifically filters out inactive ingredients to ensure
        they don't appear when creating new menus.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            category_filter: Filter by ingredient category
            search: Search term for ingredient name
            
        Returns:
            List[IngredientResponse]: List of active ingredients only
        """
        try:
            # Build query - always filter for active status
            query = {"status": IngredientStatus.ACTIVE.value}
            
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
                detail=f"Error retrieving active ingredients: {str(e)}"
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
            HTTPException: If ingredient not found or is used in dishes
        """
        try:
            ingredient = await Ingredient.get(PydanticObjectId(ingredient_id))
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id '{ingredient_id}' not found"
                )
            
            # Check if ingredient is used in any dishes
            dishes_using_ingredient = await Dish.find({
                "recipe.ingredients.ingredient_id": ingredient.id
            }).to_list()
            
            if dishes_using_ingredient:
                dish_names = [dish.name for dish in dishes_using_ingredient]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete ingredient '{ingredient.name}' because it is used in dishes: {', '.join(dish_names)}"
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

    @staticmethod
    async def inactivate_ingredient(ingredient_id: str) -> IngredientResponse:
        """
        Inactivate an ingredient (soft delete) by setting its status to INACTIVE.
        This performs a logical deletion - the ingredient will not be available for new menus
        but existing menu associations remain intact.
        
        Args:
            ingredient_id: The ingredient ID to inactivate
            
        Returns:
            IngredientResponse: The inactivated ingredient
            
        Raises:
            HTTPException: If ingredient not found or already inactive
        """
        try:
            # Get existing ingredient
            ingredient = await Ingredient.get(PydanticObjectId(ingredient_id))
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id '{ingredient_id}' not found"
                )
            
            # Check if already inactive
            if ingredient.status == IngredientStatus.INACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingredient '{ingredient.name}' is already inactive"
                )
            
            # Inactivate ingredient
            ingredient.status = IngredientStatus.INACTIVE
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
                detail=f"Error inactivating ingredient: {str(e)}"
            )

    @staticmethod
    async def activate_ingredient(ingredient_id: str) -> IngredientResponse:
        """
        Activate an ingredient by setting its status to ACTIVE.
        
        Args:
            ingredient_id: The ingredient ID to activate
            
        Returns:
            IngredientResponse: The activated ingredient
            
        Raises:
            HTTPException: If ingredient not found or already active
        """
        try:
            # Get existing ingredient
            ingredient = await Ingredient.get(PydanticObjectId(ingredient_id))
            if not ingredient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ingredient with id '{ingredient_id}' not found"
                )
            
            # Check if already active
            if ingredient.status == IngredientStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingredient '{ingredient.name}' is already active"
                )
            
            # activate ingredient
            ingredient.status = IngredientStatus.ACTIVE
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
                detail=f"Error reactivating ingredient: {str(e)}"
            )

    @staticmethod
    async def get_available_categories() -> List[str]:
        """
        Get all available ingredient categories for filtering
        
        Returns:
            List[str]: List of unique categories used by ingredients
        """
        try:
            categories = await Ingredient.distinct("category")
            # Filter out None values and empty strings
            return [cat for cat in categories if cat and cat.strip()]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving categories: {str(e)}"
            )

    @staticmethod
    async def get_ingredient_statistics() -> dict:
        """
        Get ingredient statistics for dashboard purposes
        
        Returns:
            dict: Statistics including total count, active/inactive counts, categories count
        """
        try:
            total_count = await Ingredient.count()
            active_count = await Ingredient.find({"status": IngredientStatus.ACTIVE}).count()
            inactive_count = await Ingredient.find({"status": IngredientStatus.INACTIVE}).count()
            categories = await Ingredient.distinct("category")
            category_count = len([cat for cat in categories if cat and cat.strip()])
            
            return {
                "total_ingredients": total_count,
                "active_ingredients": active_count,
                "inactive_ingredients": inactive_count,
                "total_categories": category_count,
                "categories": [cat for cat in categories if cat and cat.strip()]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving statistics: {str(e)}"
            )

    @staticmethod
    async def get_detailed_ingredients(
        skip: int = 0, 
        limit: int = 100, 
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[IngredientDetailedResponse]:
        """
        Get ingredients with detailed information including menu usage
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status_filter: Filter by ingredient status
            category_filter: Filter by ingredient category
            search: Search term for ingredient name
            
        Returns:
            List[IngredientDetailedResponse]: List of ingredients with menu usage details
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
            
            # Get menu usage for each ingredient
            detailed_ingredients = []
            for ingredient in ingredients:
                menu_usage = await IngredientService._get_menu_usage_info(ingredient.id)
                
                detailed_ingredients.append(
                    IngredientDetailedResponse(
                        id=str(ingredient.id),
                        menu_usage=menu_usage,
                        **ingredient.model_dump(exclude={"id"})
                    )
                )
            
            return detailed_ingredients
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving detailed ingredients: {str(e)}"
            )

    @staticmethod
    async def get_detailed_ingredient_by_id(ingredient_id: str) -> IngredientDetailedResponse:
        """
        Get a single ingredient with detailed information including menu usage
        
        Args:
            ingredient_id: The ingredient ID
            
        Returns:
            IngredientDetailedResponse: The ingredient with menu usage details
            
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
            
            # Get menu usage information
            menu_usage = await IngredientService._get_menu_usage_info(ingredient.id)
            
            return IngredientDetailedResponse(
                id=str(ingredient.id),
                menu_usage=menu_usage,
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
                detail=f"Error retrieving detailed ingredient: {str(e)}"
            )

    @staticmethod
    async def _get_menu_usage_info(ingredient_id: PydanticObjectId) -> MenuUsageInfo:
        """
        Get menu usage information for a specific ingredient
        
        Args:
            ingredient_id: The ingredient ID to check usage for
            
        Returns:
            MenuUsageInfo: Usage information including dish count, menu cycles, etc.
        """
        try:
            # Find dishes that use this ingredient
            dishes_using_ingredient = await Dish.find({
                "recipe.ingredients.ingredient_id": ingredient_id,
                "status": "active"
            }).to_list()
            
            dish_names = [dish.name for dish in dishes_using_ingredient]
            dish_count = len(dishes_using_ingredient)
            
            # Find menu cycles that include dishes using this ingredient
            dish_ids = [dish.id for dish in dishes_using_ingredient]
            
            menu_cycles_count = 0
            last_used_date = None
            
            if dish_ids:
                # Query menu cycles that contain any of these dishes
                menu_cycles = await MenuCycle.find({
                    "$or": [
                        {"daily_menus": {"$elemMatch": {"breakfast_dish_ids": {"$in": dish_ids}}}},
                        {"daily_menus": {"$elemMatch": {"lunch_dish_ids": {"$in": dish_ids}}}},
                        {"daily_menus": {"$elemMatch": {"snack_dish_ids": {"$in": dish_ids}}}}
                    ]
                }).to_list()
                
                menu_cycles_count = len(menu_cycles)
                
                # Find the most recent usage
                if menu_cycles:
                    latest_cycle = max(menu_cycles, key=lambda x: x.updated_at)
                    last_used_date = latest_cycle.updated_at
            
            return MenuUsageInfo(
                dish_count=dish_count,
                menu_cycle_count=menu_cycles_count,
                dish_names=dish_names,
                last_used_date=last_used_date
            )
            
        except Exception as e:
            # Return empty usage info if error occurs
            return MenuUsageInfo()

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