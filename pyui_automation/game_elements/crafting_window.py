from typing import Optional, Any, List, Tuple, TYPE_CHECKING, Dict
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class CraftingIngredient(UIElement):
    """Represents a crafting ingredient requirement"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def item_name(self) -> str:
        """
        Get ingredient item name.

        Returns:
            str: Item name
        """
        return self._element.get_property("item_name")

    @property
    def quantity(self) -> Tuple[int, int]:
        """
        Get required and available quantity.

        Returns:
            Tuple[int, int]: (required, available)
        """
        return (
            self._element.get_property("required_quantity"),
            self._element.get_property("available_quantity")
        )

    @property
    def is_satisfied(self) -> bool:
        """
        Check if requirement is satisfied.

        Returns:
            bool: True if enough ingredients available
        """
        required, available = self.quantity
        return available >= required

    def wait_until_satisfied(self, timeout: float = 10) -> bool:
        """
        Wait until ingredient requirement is satisfied.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if satisfied within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_satisfied,
            timeout=timeout,
            error_message=f"Not enough {self.item_name}"
        )


class CraftingRecipe(UIElement):
    """Represents a crafting recipe"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """
        Get recipe name.

        Returns:
            str: Recipe name
        """
        return self._element.get_property("name")

    @property
    def description(self) -> str:
        """
        Get recipe description.

        Returns:
            str: Recipe description
        """
        return self._element.get_property("description")

    @property
    def level(self) -> int:
        """
        Get required crafting level.

        Returns:
            int: Required level
        """
        return self._element.get_property("level")

    @property
    def ingredients(self) -> List[CraftingIngredient]:
        """
        Get recipe ingredients.

        Returns:
            List[CraftingIngredient]: List of ingredients
        """
        ingredients = self._element.find_elements(by="type", value="ingredient")
        return [CraftingIngredient(i, self._session) for i in ingredients]

    @property
    def output_quantity(self) -> int:
        """
        Get quantity produced per craft.

        Returns:
            int: Output quantity
        """
        return self._element.get_property("output_quantity") or 1

    @property
    def can_craft(self) -> bool:
        """
        Check if recipe can be crafted.

        Returns:
            bool: True if all requirements met
        """
        return all(i.is_satisfied for i in self.ingredients)

    def craft(self, quantity: int = 1) -> None:
        """
        Craft the recipe.

        Args:
            quantity (int): Number of times to craft

        Raises:
            ValueError: If recipe cannot be crafted
        """
        if not self.can_craft:
            raise ValueError("Missing required ingredients")

        quantity_input = self._element.find_element(by="type", value="quantity")
        if quantity_input:
            quantity_input.send_keys(str(quantity))

        craft_button = self._element.find_element(by="name", value="Craft")
        if craft_button:
            craft_button.click()

    def wait_until_craftable(self, timeout: float = 10) -> bool:
        """
        Wait until recipe can be crafted.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if craftable within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.can_craft,
            timeout=timeout,
            error_message=f"Recipe '{self.name}' cannot be crafted"
        )


class CraftingWindow(UIElement):
    """Represents a crafting interface window"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def crafting_level(self) -> int:
        """
        Get current crafting level.

        Returns:
            int: Crafting level
        """
        return self._element.get_property("level")

    @property
    def experience(self) -> Tuple[int, int]:
        """
        Get crafting experience progress.

        Returns:
            Tuple[int, int]: (current_xp, required_xp)
        """
        return (
            self._element.get_property("current_xp"),
            self._element.get_property("required_xp")
        )

    @property
    def categories(self) -> List[str]:
        """
        Get available crafting categories.

        Returns:
            List[str]: List of category names
        """
        return self._element.get_property("categories") or []

    @property
    def current_category(self) -> Optional[str]:
        """
        Get selected category.

        Returns:
            Optional[str]: Selected category or None
        """
        return self._element.get_property("current_category")

    def get_recipes(self, category: Optional[str] = None) -> List[CraftingRecipe]:
        """
        Get available recipes.

        Args:
            category (Optional[str]): Filter by category

        Returns:
            List[CraftingRecipe]: List of recipes
        """
        if category and category not in self.categories:
            return []

        recipes = self._element.find_elements(
            by="type",
            value="recipe",
            category=category
        )
        return [CraftingRecipe(r, self._session) for r in recipes]

    def get_recipe(self, name: str) -> Optional[CraftingRecipe]:
        """
        Find recipe by name.

        Args:
            name (str): Recipe name

        Returns:
            Optional[CraftingRecipe]: Found recipe or None
        """
        for recipe in self.get_recipes():
            if recipe.name == name:
                return recipe
        return None

    def select_category(self, category: str) -> None:
        """
        Select crafting category.

        Args:
            category (str): Category to select

        Raises:
            ValueError: If category not found
        """
        if category not in self.categories:
            raise ValueError(f"Category '{category}' not found")

        category_list = self._element.find_element(by="type", value="category_list")
        if category_list:
            category_item = category_list.find_element(by="name", value=category)
            if category_item:
                category_item.click()

    def search_recipes(self, query: str) -> List[CraftingRecipe]:
        """
        Search recipes by text.

        Args:
            query (str): Search query

        Returns:
            List[CraftingRecipe]: List of matching recipes
        """
        search_box = self._element.find_element(by="type", value="search")
        if search_box:
            search_box.send_keys(query)

        results = self._element.find_elements(by="type", value="search_result")
        return [CraftingRecipe(r, self._session) for r in results]

    def wait_until_level_up(self, timeout: float = 10) -> bool:
        """
        Wait until crafting level increases.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if leveled up within timeout, False otherwise
        """
        current_level = self.crafting_level
        return self._session.wait_for_condition(
            lambda: self.crafting_level > current_level,
            timeout=timeout,
            error_message="Crafting level did not increase"
        )

    def wait_until_recipe_unlocked(self, name: str, timeout: float = 10) -> bool:
        """
        Wait until recipe becomes available.

        Args:
            name (str): Recipe name
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if recipe unlocked within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.get_recipe(name) is not None,
            timeout=timeout,
            error_message=f"Recipe '{name}' was not unlocked"
        )
