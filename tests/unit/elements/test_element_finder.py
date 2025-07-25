"""
Tests for ElementFinder class
"""
import pytest
from typing import List, Any

from pyui_automation.elements.element_finder import ElementFinder
from pyui_automation.elements.properties import StringProperty


class TestElementFinder:
    """Test ElementFinder class"""
    
    def test_init(self, mocker):
        """Test ElementFinder initialization"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        assert self.finder._element == self.mock_element
        assert self.finder._logger is not None

    def test_find_child_by_property_success(self, mocker):
        """Test successful child finding by property"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.return_value = "expected_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_property("test_property", "expected_value")
        
        assert result == child1
        mock_property.get_value.assert_called()

    def test_find_child_by_property_not_found(self, mocker):
        """Test child finding by property when not found"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.return_value = "different_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_property("test_property", "expected_value")
        
        assert result is None

    def test_find_child_by_property_no_children(self, mocker):
        """Test child finding by property when no children"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        self.mock_element.get_children.return_value = []
        
        result = self.finder.find_child_by_property("test_property", "expected_value")
        
        assert result is None

    def test_find_child_by_property_exception(self, mocker):
        """Test child finding by property with exception"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        self.mock_element.get_children.side_effect = Exception("Test exception")
        
        result = self.finder.find_child_by_property("test_property", "expected_value")
        
        assert result is None

    def test_find_children_by_property_success(self, mocker):
        """Test successful children finding by property"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["expected_value", "different_value", "expected_value"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_children_by_property("test_property", "expected_value")
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_children_by_property_empty_result(self, mocker):
        """Test children finding by property with empty result"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.return_value = "different_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_children_by_property("test_property", "expected_value")
        
        assert len(result) == 0

    def test_find_child_by_name_exact_match_success(self, mocker):
        """Test successful child finding by name with exact match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["exact_name", "different_name"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_name("exact_name", exact_match=True)
        
        assert result == child1

    def test_find_child_by_name_partial_match_success(self, mocker):
        """Test successful child finding by name with partial match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["partial_name_test", "different_name"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_name("partial_name", exact_match=False)
        
        assert result == child1

    def test_find_children_by_name_exact_match_success(self, mocker):
        """Test successful children finding by name with exact match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["exact_name", "different_name", "exact_name"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_children_by_name("exact_name", exact_match=True)
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_child_by_text_exact_match_success(self, mocker):
        """Test successful child finding by text with exact match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["exact_text", "different_text"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_text("exact_text", exact_match=True)
        
        assert result == child1

    def test_find_child_by_text_partial_match_success(self, mocker):
        """Test successful child finding by text with partial match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["partial_text_content", "different_text"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_text("partial_text", exact_match=False)
        
        assert result == child1

    def test_find_child_by_text_case_insensitive(self, mocker):
        """Test child finding by text with case insensitive match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["UPPERCASE_TEXT", "different_text"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_text("uppercase_text", exact_match=True, case_sensitive=False)
        
        assert result == child1

    def test_find_children_by_text_exact_match_success(self, mocker):
        """Test successful children finding by text with exact match"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["exact_text", "different_text", "exact_text"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_children_by_text("exact_text", exact_match=True)
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_child_by_automation_id_success(self, mocker):
        """Test successful child finding by automation ID"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["test_id", "different_id"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_automation_id("test_id")
        
        assert result == child1

    def test_find_children_by_automation_id_success(self, mocker):
        """Test successful children finding by automation ID"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["test_id", "different_id", "test_id"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_children_by_automation_id("test_id")
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_child_by_control_type_success(self, mocker):
        """Test successful child finding by control type"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["Button", "Text"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_control_type("Button")
        
        assert result == child1

    def test_find_children_by_control_type_success(self, mocker):
        """Test successful children finding by control type"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock property
        mock_property = mocker.Mock(spec=StringProperty)
        mock_property.get_value.side_effect = ["Button", "Text", "Button"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_children_by_control_type("Button")
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_child_by_predicate_success(self, mocker):
        """Test successful child finding by predicate"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock predicate
        predicate = mocker.Mock()
        predicate.side_effect = [True, False]
        
        result = self.finder.find_child_by_predicate(predicate)
        
        assert result == child1
        predicate.assert_called()

    def test_find_child_by_predicate_not_found(self, mocker):
        """Test child finding by predicate when not found"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock predicate
        predicate = mocker.Mock()
        predicate.return_value = False
        
        result = self.finder.find_child_by_predicate(predicate)
        
        assert result is None

    def test_find_child_by_predicate_exception(self, mocker):
        """Test child finding by predicate with exception"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1]
        
        # Mock predicate
        predicate = mocker.Mock()
        predicate.side_effect = Exception("Test exception")
        
        result = self.finder.find_child_by_predicate(predicate)
        
        assert result is None

    def test_find_children_by_predicate_success(self, mocker):
        """Test successful children finding by predicate"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock predicate
        predicate = mocker.Mock()
        predicate.side_effect = [True, False, True]
        
        result = self.finder.find_children_by_predicate(predicate)
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_visible_children_success(self, mocker):
        """Test successful visible children finding"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock BoolProperty for visible property
        mock_property = mocker.Mock()
        mock_property.get_value.side_effect = [True, False, True]
        
        mocker.patch('pyui_automation.elements.element_finder.BoolProperty', return_value=mock_property)
        result = self.finder.find_visible_children()
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_enabled_children_success(self, mocker):
        """Test successful enabled children finding"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        child3 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2, child3]
        
        # Mock is_enabled method for children
        child1.is_enabled.return_value = True
        child2.is_enabled.return_value = False
        child3.is_enabled.return_value = True
        
        result = self.finder.find_enabled_children()
        
        assert len(result) == 2
        assert child1 in result
        assert child3 in result

    def test_find_enabled_children_exception(self, mocker):
        """Test enabled children finding with exception"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1]
        
        # Mock is_enabled method to raise exception
        child1.is_enabled.side_effect = Exception("Test exception")
        
        result = self.finder.find_enabled_children()
        
        assert len(result) == 0

    def test_find_enabled_children_no_is_enabled_method(self, mocker):
        """Test enabled children finding when is_enabled method not available"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Remove is_enabled method to simulate it not being available
        del child1.is_enabled
        del child2.is_enabled
        
        result = self.finder.find_enabled_children()
        
        assert len(result) == 0

    def test_get_children_using_get_children_method(self, mocker):
        """Test getting children using get_children method"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        result = self.finder._get_children()
        
        assert result == [child1, child2]
        self.mock_element.get_children.assert_called_once()

    def test_get_children_using_findall_method(self, mocker):
        """Test getting children using findall method"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Remove get_children method
        del self.mock_element.get_children
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.findall.return_value = [child1, child2]
        
        result = self.finder._get_children()
        
        assert result == [child1, child2]
        self.mock_element.findall.assert_called_once()

    def test_get_children_using_children_attribute(self, mocker):
        """Test getting children using children attribute"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Remove methods
        del self.mock_element.get_children
        del self.mock_element.findall
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.children = [child1, child2]
        
        result = self.finder._get_children()
        
        assert result == [child1, child2]

    def test_get_children_no_methods_available(self, mocker):
        """Test getting children when no methods available"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Remove all methods and attributes
        del self.mock_element.get_children
        del self.mock_element.findall
        del self.mock_element.children
        
        result = self.finder._get_children()
        
        assert result == []

    def test_get_children_exception(self, mocker):
        """Test getting children with exception"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        self.mock_element.get_children.side_effect = Exception("Test exception")
        
        result = self.finder._get_children()
        
        assert result == []

    def test_detect_property_type_unknown_property(self, mocker):
        """Test detecting property type for unknown property"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        
        result = self.finder._detect_property_type("unknown_property")
        
        assert result == StringProperty

    def test_detect_property_type_known_property(self, mocker):
        """Test detecting property type for known property"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        
        result = self.finder._detect_property_type("Name")
        
        assert result == StringProperty

    def test_detect_property_type_exception(self, mocker):
        """Test detecting property type with exception"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        
        result = self.finder._detect_property_type("test_property")
        
        assert result == StringProperty

    def test_find_child_by_property_with_custom_type(self, mocker):
        """Test child finding by property with custom property type"""
        self.mock_element = mocker.Mock()
        self.finder = ElementFinder(self.mock_element)
        # Mock children
        child1 = mocker.Mock()
        child2 = mocker.Mock()
        self.mock_element.get_children.return_value = [child1, child2]
        
        # Mock custom property
        mock_property = mocker.Mock()
        mock_property.get_value.return_value = "expected_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_property)
        result = self.finder.find_child_by_property("test_property", "expected_value", property_type=StringProperty)
        
        assert result == child1
        mock_property.get_value.assert_called() 