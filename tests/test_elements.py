import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements import UIElement

@pytest.fixture
def mock_automation():
    automation = MagicMock()
    automation.mouse = MagicMock()
    automation.keyboard = MagicMock()
    return automation

@pytest.fixture
def mock_element_with_current():
    element = MagicMock()
    # Set default attribute values
    element.CurrentAutomationId = "test_id"
    element.CurrentName = "test_name"
    element.CurrentIsEnabled = True
    element.CurrentIsOffscreen = False
    element.CurrentBoundingRectangle = (10, 20, 110, 120)  # x, y, right, bottom
    return element

@pytest.fixture
def mock_element_with_get():
    element = MagicMock()
    # Set up method return values
    element.get_id.return_value = "test_id"
    element.get_text.return_value = "test text"
    element.get_name.return_value = "test name"
    element.get_location.return_value = (30, 40)
    element.get_size.return_value = (50, 60)
    element.is_enabled.return_value = True
    element.is_visible.return_value = True
    # Remove Current* attributes
    del element.CurrentAutomationId
    del element.CurrentName
    del element.CurrentIsEnabled
    del element.CurrentIsOffscreen
    del element.CurrentBoundingRectangle
    return element

class TestUIElement:
    def test_id_with_automation_id(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        assert ui_element.id == "test_id"

    def test_id_with_get_id(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.id == "test_id"
        mock_element_with_get.get_id.assert_called_once()

    def test_id_without_id(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.id is None

    def test_text_with_get_text(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.text == "test text"
        mock_element_with_get.get_text.assert_called_once()

    def test_text_without_text(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.text == ""

    def test_name_with_current_name(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        assert ui_element.name == "test_name"

    def test_name_with_get_name(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.name == "test name"
        mock_element_with_get.get_name.assert_called_once()

    def test_name_without_name(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.name == ""

    def test_location_with_bounding_rectangle(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        assert ui_element.location == (10, 20)

    def test_location_with_get_location(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.location == (30, 40)
        mock_element_with_get.get_location.assert_called_once()

    def test_location_without_location(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.location == (0, 0)

    def test_size_with_bounding_rectangle(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        assert ui_element.size == (100, 100)  # 110-10, 120-20

    def test_size_with_get_size(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.size == (50, 60)
        mock_element_with_get.get_size.assert_called_once()

    def test_size_without_size(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.size == (0, 0)

    def test_enabled_with_current_is_enabled(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        assert ui_element.enabled is True

    def test_enabled_with_is_enabled(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.enabled is True
        mock_element_with_get.is_enabled.assert_called_once()

    def test_enabled_without_enabled(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.enabled is False

    def test_visible_with_current_is_offscreen(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        assert ui_element.visible is True

    def test_visible_with_is_visible(self, mock_element_with_get, mock_automation):
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.visible is True
        mock_element_with_get.is_visible.assert_called_once()

    def test_visible_without_visible(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.visible is False

    def test_click_enabled_and_visible(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        ui_element.click()
        mock_automation.mouse.move.assert_called_once()
        mock_automation.mouse.click.assert_called_once()

    def test_click_disabled(self, mock_element_with_current, mock_automation):
        mock_element_with_current.CurrentIsEnabled = False
        ui_element = UIElement(mock_element_with_current, mock_automation)
        ui_element.click()
        mock_automation.mouse.move.assert_not_called()
        mock_automation.mouse.click.assert_not_called()

    def test_double_click_enabled_and_visible(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        ui_element.double_click()
        mock_automation.mouse.move.assert_called_once()
        mock_automation.mouse.double_click.assert_called_once()

    def test_right_click_enabled_and_visible(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        ui_element.right_click()
        mock_automation.mouse.move.assert_called_once()
        mock_automation.mouse.click.assert_called_once_with(button='right')

    def test_type_text_enabled_and_visible(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        ui_element.type_text("test text", 0.1)
        mock_automation.mouse.move.assert_called_once()
        mock_automation.mouse.click.assert_called_once()
        mock_automation.keyboard.type_text.assert_called_once_with("test text", 0.1)

    def test_clear(self, mock_element_with_current, mock_automation):
        ui_element = UIElement(mock_element_with_current, mock_automation)
        ui_element.clear()
        mock_element_with_current.clear.assert_called_once()

    def test_get_attribute_with_attribute(self, mock_element_with_get, mock_automation):
        mock_element_with_get.get_attribute.return_value = "test value"
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.get_attribute("test_attr") == "test value"
        mock_element_with_get.get_attribute.assert_called_once_with("test_attr")

    def test_get_attribute_without_attribute(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.get_attribute("test_attr") is None

    def test_get_property_with_property(self, mock_element_with_get, mock_automation):
        mock_element_with_get.get_property.return_value = "test value"
        ui_element = UIElement(mock_element_with_get, mock_automation)
        assert ui_element.get_property("test_prop") == "test value"
        mock_element_with_get.get_property.assert_called_once_with("test_prop")

    def test_get_property_without_property(self, mock_automation):
        element = MagicMock(spec=[])
        ui_element = UIElement(element, mock_automation)
        assert ui_element.get_property("test_prop") is None
