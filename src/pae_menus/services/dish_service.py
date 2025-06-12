from beanie import PydanticObjectId, Document
from typing import List, Optional
from ..models.dish import Dish, DishCreate, DishUpdate
from ..models.ingredient import Ingredient, IngredientStatus
from ..models.commons import Recipe

class DishService:
    async def create_dish(self, dish_data: DishCreate) -> Dish:
        """
        Creates a new dish.
        - Validates that the dish name is unique.
        - Validates that all ingredients in the recipe exist and are active.
        """
        if await Dish.find_one(Dish.name == dish_data.name):
            raise ValueError(f"Dish with name '{dish_data.name}' already exists.")

        if dish_data.recipe and dish_data.recipe.ingredients:
            await self._validate_recipe_ingredients(dish_data.recipe.ingredients)

        dish = Dish(**dish_data.model_dump())
        await dish.create()
        return dish

    async def get_dish(self, dish_id: PydanticObjectId) -> Optional[Dish]:
        """Retrieves a single dish by its ID."""
        return await Dish.get(dish_id)

    async def get_all_dishes(self) -> List[Dish]:
        """Retrieves all dishes."""
        return await Dish.find_all().to_list()

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

        if "recipe" in update_data and update_data["recipe"]:
            new_recipe = Recipe(**update_data["recipe"])
            await self._validate_recipe_ingredients(new_recipe.ingredients)

        dish.set(update_data)
        dish.update_timestamp()
        await dish.save()
        return dish

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