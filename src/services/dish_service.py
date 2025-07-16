from beanie import PydanticObjectId, Document
from typing import List, Optional
from models.dish import Dish, DishCreate, DishUpdate, DishStatus
from models.ingredient import Ingredient, IngredientStatus
from models.commons import Recipe, MealType

class DishService:
    async def create_dish(self, dish_data: DishCreate) -> Dish:
        """
        Creates a new dish.
        - Validates that the dish name is unique.
        - Validates that all ingredients in the recipe exist and are active.
        - Validates that the recipe has at least one ingredient.
        """
        if await Dish.find_one(Dish.name == dish_data.name):
            raise ValueError(f"Dish with name '{dish_data.name}' already exists.")

        # Validate that recipe has at least one ingredient
        if not dish_data.recipe or not dish_data.recipe.ingredients:
            raise ValueError("Dish recipe must have at least one ingredient.")

        await self._validate_recipe_ingredients(dish_data.recipe.ingredients)

        dish = Dish(**dish_data.model_dump())
        await dish.create()
        return dish

    async def get_dish(self, dish_id: PydanticObjectId) -> Optional[Dish]:
        """Retrieves a single dish by its ID."""
        return await Dish.get(dish_id)

    async def get_all_dishes(
        self,
        name: Optional[str] = None,
        status: Optional[DishStatus] = None,
        meal_type: Optional[MealType] = None
    ) -> List[Dish]:
        """
        Retrieves all dishes, with optional filtering.
        """
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if status:
            query["status"] = status
        if meal_type:
            # This query finds dishes where the meal_type is present in the compatible_meal_types list
            query["compatible_meal_types"] = meal_type
            
        return await Dish.find(query).to_list()

    async def update_dish(self, dish_id: PydanticObjectId, dish_data: DishUpdate) -> Optional[Dish]:
        """
        Updates an existing dish using an idiomatic Beanie approach.
        """
        dish = await self.get_dish(dish_id)
        if not dish:
            return None

        update_data = dish_data.model_dump(exclude_unset=True)

        if not update_data:
            return dish

        # Check for duplicate name if name is being updated
        if "name" in update_data and update_data["name"] != dish.name:
            existing_dish = await Dish.find_one({"name": update_data["name"], "_id": {"$ne": dish_id}})
            if existing_dish:
                raise ValueError(f"Dish with name '{update_data['name']}' already exists.")

        if "recipe" in update_data and update_data["recipe"]:
            new_recipe = Recipe(**update_data["recipe"])
            await self._validate_recipe_ingredients(new_recipe.ingredients)

        for field, value in update_data.items():
            setattr(dish, field, value)
        
        dish.update_timestamp()
        await dish.save()
        return dish

    async def delete_dish(self, dish_id: PydanticObjectId) -> dict:
        """
        Delete a dish by its ID.
        
        Args:
            dish_id: The dish ID to delete
            
        Returns:
            dict: Confirmation message with deleted dish details
            
        Raises:
            ValueError: If dish is used in active menu cycles or not found
        """
        dish = await self.get_dish(dish_id)
        if not dish:
            raise ValueError(f"Dish with id '{dish_id}' not found")
        
        # Check if dish is used in any menu cycles
        await self._validate_dish_not_in_use(dish_id, dish.name)
        
        # Store dish info for response before deletion
        dish_info = {
            "id": str(dish.id),
            "name": dish.name,
            "status": dish.status,
            "compatible_meal_types": [meal_type.value for meal_type in dish.compatible_meal_types]
        }
        
        # Perform the deletion
        await dish.delete()
        
        return {
            "message": f"Dish '{dish.name}' deleted successfully",
            "deleted_dish": dish_info
        }

    async def _validate_dish_not_in_use(self, dish_id: PydanticObjectId, dish_name: str):
        """
        Validate that a dish is not used in any menu cycles before deletion.
        
        Args:
            dish_id: The dish ID to check
            dish_name: The dish name for error messages
            
        Raises:
            ValueError: If dish is used in any menu cycles
        """
        # Import here to avoid circular imports
        from models.menu_cycle import MenuCycle
        
        # Check if dish is used in any menu cycles
        menu_cycles_using_dish = await MenuCycle.find({
            "$or": [
                {"daily_menus": {"$elemMatch": {"breakfast_dish_ids": dish_id}}},
                {"daily_menus": {"$elemMatch": {"lunch_dish_ids": dish_id}}},
                {"daily_menus": {"$elemMatch": {"snack_dish_ids": dish_id}}}
            ]
        }).to_list()
        
        if menu_cycles_using_dish:
            cycle_names = [cycle.name for cycle in menu_cycles_using_dish]
            raise ValueError(
                f"Cannot delete dish '{dish_name}' because it is used in menu cycles: {', '.join(cycle_names)}"
            )

    async def _validate_recipe_ingredients(self, recipe_ingredients: list):
        """
        Validates that all recipe ingredients exist and are active using a direct PyMongo query
        to bypass any potential Beanie-level issues.
        """
        if not recipe_ingredients:
            return

        ingredient_ids = [item.ingredient_id for item in recipe_ingredients]
        
        # Use a direct PyMongo query for maximum robustness
        ingredients_collection = Ingredient.get_motor_collection()
        
        ingredients_in_db_cursor = ingredients_collection.find({
            "_id": {"$in": ingredient_ids}
        })
        
        ingredients_in_db = await ingredients_in_db_cursor.to_list(length=len(ingredient_ids))

        found_ids = {ing["_id"] for ing in ingredients_in_db}
        required_ids = set(ingredient_ids)

        if missing_ids := required_ids - found_ids:
            # Convert ObjectIds to strings for a cleaner error message
            missing_ids_str = ', '.join(map(str, missing_ids))
            raise ValueError(f"Ingredients not found: {missing_ids_str}")

        for ingredient_doc in ingredients_in_db:
            if ingredient_doc.get("status") != IngredientStatus.ACTIVE:
                raise ValueError(f"Ingredient '{ingredient_doc.get('name')}' ({ingredient_doc.get('_id')}) is not active.")

dish_service = DishService() 