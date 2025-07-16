import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.crafting_window import CraftingIngredient, CraftingRecipe, CraftingWindow

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'item_name': 'Iron Ore',
        'required_quantity': 2,
        'available_quantity': 3,
        'name': 'Iron Sword',
        'description': 'A basic sword',
        'level': 5,
        'output_quantity': 1,
        'categories': ['Weapon', 'Armor'],
        'current_category': 'Weapon',
        'current_xp': 10,
        'required_xp': 20,
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None, **kwargs: []
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    s.find_element.return_value = MagicMock()
    return s

@pytest.fixture
def ingredient(mock_element, mock_session):
    return CraftingIngredient(mock_element, mock_session)

@pytest.fixture
def recipe(mock_element, mock_session):
    return CraftingRecipe(mock_element, mock_session)

@pytest.fixture
def crafting_window(mock_element, mock_session):
    return CraftingWindow(mock_element, mock_session)

def test_ingredient_properties(ingredient):
    assert ingredient.item_name == 'Iron Ore'
    assert ingredient.quantity == (2, 3)
    assert ingredient.is_satisfied is True

def test_ingredient_wait_until_satisfied(ingredient, mock_session):
    assert ingredient.wait_until_satisfied(timeout=1.0) is True

def test_ingredient_is_satisfied_false(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 2 if key == 'required_quantity' else 1 if key == 'available_quantity' else 'x'
    ing = CraftingIngredient(mock_element, mock_session)
    assert ing.is_satisfied is False

def test_recipe_properties(recipe):
    assert recipe.name == 'Iron Sword'
    assert recipe.description == 'A basic sword'
    assert recipe.level == 5
    assert recipe.output_quantity == 1

def test_recipe_ingredients(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    rec = CraftingRecipe(mock_element, mock_session)
    ings = rec.ingredients
    assert all(isinstance(i, CraftingIngredient) for i in ings)

def test_recipe_can_craft(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    ing_el.get_property.side_effect = lambda key: 2 if key == 'required_quantity' else 3 if key == 'available_quantity' else None
    ing = CraftingIngredient(ing_el, mock_session)
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    rec = CraftingRecipe(mock_element, mock_session)
    assert rec.can_craft is True

def test_recipe_can_craft_false(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    ing_el.get_property.side_effect = lambda key: 2 if key == 'required_quantity' else 1 if key == 'available_quantity' else None
    ing = CraftingIngredient(ing_el, mock_session)
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    rec = CraftingRecipe(mock_element, mock_session)
    assert rec.can_craft is False

def test_recipe_craft_success(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    ing_el.get_property.side_effect = lambda key: 1 if key == 'required_quantity' else 2 if key == 'available_quantity' else None
    ing = CraftingIngredient(ing_el, mock_session)
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    quantity_input = MagicMock()
    craft_btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: quantity_input if value == 'quantity' else craft_btn if value == 'Craft' else None
    rec = CraftingRecipe(mock_element, mock_session)
    rec.craft(quantity=2)
    assert quantity_input.send_keys.called
    assert craft_btn.click.called

def test_recipe_craft_fail(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    ing_el.get_property.side_effect = lambda key: 2 if key == 'required_quantity' else 1 if key == 'available_quantity' else None
    ing = CraftingIngredient(ing_el, mock_session)
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    rec = CraftingRecipe(mock_element, mock_session)
    with pytest.raises(ValueError):
        rec.craft()

def test_recipe_wait_until_craftable(recipe, mock_session):
    assert recipe.wait_until_craftable(timeout=1.0) is True

def test_crafting_window_properties(crafting_window):
    assert crafting_window.crafting_level == 5
    assert crafting_window.experience == (10, 20)
    assert crafting_window.categories == ['Weapon', 'Armor']
    assert crafting_window.current_category == 'Weapon'

def test_crafting_window_get_recipes(crafting_window, mock_element, mock_session):
    rec_el = MagicMock()
    mock_element.get_property.side_effect = lambda key: ['Weapon', 'Armor'] if key == 'categories' else 'Weapon' if key == 'current_category' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [rec_el] if value == 'recipe' else []
    win = CraftingWindow(mock_element, mock_session)
    recs = win.get_recipes(category='Weapon')
    assert all(isinstance(r, CraftingRecipe) for r in recs)

def test_crafting_window_get_recipes_wrong_category(crafting_window, mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: ['Weapon', 'Armor'] if key == 'categories' else 'x'
    win = CraftingWindow(mock_element, mock_session)
    recs = win.get_recipes(category='Alchemy')
    assert recs == []

def test_crafting_window_get_recipe_found(crafting_window, mock_element, mock_session):
    rec_el = MagicMock()
    rec_el.get_property.side_effect = lambda key: 'Iron Sword' if key == 'name' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [rec_el] if value == 'recipe' else []
    win = CraftingWindow(mock_element, mock_session)
    rec = win.get_recipe('Iron Sword')
    assert rec is not None
    assert rec.name == 'Iron Sword'

def test_crafting_window_get_recipe_not_found(crafting_window, mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: []
    win = CraftingWindow(mock_element, mock_session)
    rec = win.get_recipe('NotExist')
    assert rec is None 

def test_crafting_window_search_recipes(crafting_window, mock_element, mock_session):
    rec_el = MagicMock()
    rec_el.get_property.side_effect = lambda key: 'Iron Sword' if key == 'name' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [rec_el] if value == 'recipe' else []
    win = CraftingWindow(mock_element, mock_session)
    recs = win.search_recipes('Iron')
    assert all(isinstance(r, CraftingRecipe) for r in recs)

def test_crafting_window_search_recipes_no_results(crafting_window, mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: []
    win = CraftingWindow(mock_element, mock_session)
    recs = win.search_recipes('NotExist')
    assert recs == []

def test_crafting_window_wait_until_level_up_success(crafting_window, mock_session):
    mock_session.wait_for_condition.return_value = True
    crafting_window._session = mock_session
    assert crafting_window.wait_until_level_up(timeout=1.0) is True

def test_crafting_window_wait_until_level_up_fail(crafting_window, mock_session):
    mock_session.wait_for_condition.return_value = False
    crafting_window._session = mock_session
    assert crafting_window.wait_until_level_up(timeout=1.0) is False

def test_crafting_window_wait_until_recipe_unlocked_success(crafting_window, mock_session):
    mock_session.wait_for_condition.return_value = True
    crafting_window._session = mock_session
    assert crafting_window.wait_until_recipe_unlocked('Iron Sword', timeout=1.0) is True

def test_crafting_window_wait_until_recipe_unlocked_fail(crafting_window, mock_session):
    mock_session.wait_for_condition.return_value = False
    crafting_window._session = mock_session
    assert crafting_window.wait_until_recipe_unlocked('Iron Sword', timeout=1.0) is False

def test_recipe_craft_no_quantity_input(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    ing_el.get_property.side_effect = lambda key: 1 if key == 'required_quantity' else 2 if key == 'available_quantity' else None
    ing = CraftingIngredient(ing_el, mock_session)
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    mock_element.find_element.side_effect = lambda by=None, value=None: None if value == 'quantity' else MagicMock() if value == 'Craft' else None
    rec = CraftingRecipe(mock_element, mock_session)
    rec.craft(quantity=2)  # Не должно быть исключения

def test_recipe_craft_no_craft_button(recipe, mock_element, mock_session):
    ing_el = MagicMock()
    ing_el.get_property.side_effect = lambda key: 1 if key == 'required_quantity' else 2 if key == 'available_quantity' else None
    ing = CraftingIngredient(ing_el, mock_session)
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [ing_el] if value == 'ingredient' else []
    mock_element.find_element.side_effect = lambda by=None, value=None: MagicMock() if value == 'quantity' else None
    rec = CraftingRecipe(mock_element, mock_session)
    rec.craft(quantity=2)  # Не должно быть исключения 