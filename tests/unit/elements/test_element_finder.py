"""
Tests for ElementFinder class
"""

import pytest
from pyui_automation.elements.element_finder import ElementFinder
from pyui_automation.elements.properties import StringProperty


@pytest.fixture
def element_finder(mock_native_element):
    """Create an ElementFinder for testing"""
    return ElementFinder(mock_native_element)


@pytest.fixture
def mock_children(mocker):
    """Create mock children for testing"""
    child1 = mocker.Mock()
    child2 = mocker.Mock()
    child3 = mocker.Mock()
    return [child1, child2, child3]


@pytest.fixture
def mock_string_property(mocker):
    """Create a mock StringProperty for testing"""
    mock_property = mocker.Mock(spec=StringProperty)
    return mock_property


class TestElementFinder:
    """Test ElementFinder class"""
    
    def test_init(self, element_finder, mock_native_element):
        """Test ElementFinder initialization"""
        assert element_finder._element == mock_native_element
        assert element_finder._logger is not None

    def test_find_child_by_property_success(self, element_finder, mock_children, mock_string_property, mocker):
        """Test successful child finding by property"""
        element_finder._element.get_children.return_value = mock_children
        mock_string_property.get_value.return_value = "expected_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_string_property)
        result = element_finder.find_child_by_property("test_property", "expected_value")
        
        assert result == mock_children[0]
        mock_string_property.get_value.assert_called()

    def test_find_child_by_property_not_found(self, element_finder, mock_children, mock_string_property, mocker):
        """Test child finding by property when not found"""
        element_finder._element.get_children.return_value = mock_children
        mock_string_property.get_value.return_value = "different_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_string_property)
        result = element_finder.find_child_by_property("test_property", "expected_value")
        
        assert result is None

    def test_find_child_by_property_no_children(self, element_finder):
        """Test child finding by property when no children"""
        element_finder._element.get_children.return_value = []
        
        result = element_finder.find_child_by_property("test_property", "expected_value")
        
        assert result is None

    def test_find_child_by_property_exception(self, element_finder):
        """Test child finding by property with exception"""
        element_finder._element.get_children.side_effect = Exception("Test exception")
        
        result = element_finder.find_child_by_property("test_property", "expected_value")
        
        assert result is None

    def test_find_children_by_property_success(self, element_finder, mock_children, mock_string_property, mocker):
        """Test successful children finding by property"""
        element_finder._element.get_children.return_value = mock_children
        mock_string_property.get_value.side_effect = ["expected_value", "different_value", "expected_value"]
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_string_property)
        result = element_finder.find_children_by_property("test_property", "expected_value")
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[2] in result

    def test_find_children_by_property_empty_result(self, element_finder, mock_children, mock_string_property, mocker):
        """Test children finding by property with empty result"""
        element_finder._element.get_children.return_value = mock_children
        mock_string_property.get_value.return_value = "different_value"
        
        mocker.patch('pyui_automation.elements.element_finder.StringProperty', return_value=mock_string_property)
        result = element_finder.find_children_by_property("test_property", "expected_value")
        
        assert len(result) == 0

    def test_find_child_by_name_exact_match_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by name with exact match"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_name"
        mock_children[1].get_attribute.return_value = "other_name"
        mock_children[2].get_attribute.return_value = "another_name"
        
        result = element_finder.find_child_by_name("target_name", exact_match=True)
        
        assert result == mock_children[0]

    def test_find_child_by_name_partial_match_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by name with partial match"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_name"
        mock_children[1].get_attribute.return_value = "other_name"
        mock_children[2].get_attribute.return_value = "another_name"
        
        result = element_finder.find_child_by_name("target", exact_match=False)
        
        assert result == mock_children[0]

    def test_find_children_by_name_exact_match_success(self, element_finder, mock_children, mocker):
        """Test successful children finding by name with exact match"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_name"
        mock_children[1].get_attribute.return_value = "target_name"
        mock_children[2].get_attribute.return_value = "other_name"
        
        result = element_finder.find_children_by_name("target_name", exact_match=True)
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[1] in result

    def test_find_child_by_text_exact_match_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by text with exact match"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_text"
        mock_children[1].get_attribute.return_value = "other_text"
        mock_children[2].get_attribute.return_value = "another_text"
        
        result = element_finder.find_child_by_text("target_text", exact_match=True)
        
        assert result == mock_children[0]

    def test_find_child_by_text_partial_match_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by text with partial match"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_text"
        mock_children[1].get_attribute.return_value = "other_text"
        mock_children[2].get_attribute.return_value = "another_text"
        
        result = element_finder.find_child_by_text("target", exact_match=False)
        
        assert result == mock_children[0]

    def test_find_child_by_text_case_insensitive(self, element_finder, mock_children, mocker):
        """Test child finding by text with case insensitive matching"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "TARGET_TEXT"
        mock_children[1].get_attribute.return_value = "other_text"
        mock_children[2].get_attribute.return_value = "another_text"
        
        result = element_finder.find_child_by_text("target_text", exact_match=False, case_sensitive=False)
        
        assert result == mock_children[0]

    def test_find_children_by_text_exact_match_success(self, element_finder, mock_children, mocker):
        """Test successful children finding by text with exact match"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_text"
        mock_children[1].get_attribute.return_value = "target_text"
        mock_children[2].get_attribute.return_value = "other_text"
        
        result = element_finder.find_children_by_text("target_text", exact_match=True)
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[1] in result

    def test_find_child_by_automation_id_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by automation ID"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_id"
        mock_children[1].get_attribute.return_value = "other_id"
        mock_children[2].get_attribute.return_value = "another_id"
        
        result = element_finder.find_child_by_automation_id("target_id")
        
        assert result == mock_children[0]

    def test_find_children_by_automation_id_success(self, element_finder, mock_children, mocker):
        """Test successful children finding by automation ID"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_id"
        mock_children[1].get_attribute.return_value = "target_id"
        mock_children[2].get_attribute.return_value = "other_id"
        
        result = element_finder.find_children_by_automation_id("target_id")
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[1] in result

    def test_find_child_by_control_type_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by control type"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_type"
        mock_children[1].get_attribute.return_value = "other_type"
        mock_children[2].get_attribute.return_value = "another_type"
        
        result = element_finder.find_child_by_control_type("target_type")
        
        assert result == mock_children[0]

    def test_find_children_by_control_type_success(self, element_finder, mock_children, mocker):
        """Test successful children finding by control type"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "target_type"
        mock_children[1].get_attribute.return_value = "target_type"
        mock_children[2].get_attribute.return_value = "other_type"
        
        result = element_finder.find_children_by_control_type("target_type")
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[1] in result

    def test_find_child_by_predicate_success(self, element_finder, mock_children, mocker):
        """Test successful child finding by predicate"""
        element_finder._element.get_children.return_value = mock_children
        
        def predicate(child):
            return child.get_attribute.return_value == "target_value"
        
        mock_children[0].get_attribute.return_value = "target_value"
        mock_children[1].get_attribute.return_value = "other_value"
        mock_children[2].get_attribute.return_value = "another_value"
        
        result = element_finder.find_child_by_predicate(predicate)
        
        assert result == mock_children[0]

    def test_find_child_by_predicate_not_found(self, element_finder, mock_children, mocker):
        """Test child finding by predicate when not found"""
        element_finder._element.get_children.return_value = mock_children
        
        def predicate(child):
            return child.get_attribute.return_value == "nonexistent_value"
        
        mock_children[0].get_attribute.return_value = "value1"
        mock_children[1].get_attribute.return_value = "value2"
        mock_children[2].get_attribute.return_value = "value3"
        
        result = element_finder.find_child_by_predicate(predicate)
        
        assert result is None

    def test_find_child_by_predicate_exception(self, element_finder, mock_children, mocker):
        """Test child finding by predicate with exception"""
        element_finder._element.get_children.return_value = mock_children
        
        def predicate(child):
            raise Exception("Predicate exception")
        
        result = element_finder.find_child_by_predicate(predicate)
        
        assert result is None

    def test_find_children_by_predicate_success(self, element_finder, mock_children, mocker):
        """Test successful children finding by predicate"""
        element_finder._element.get_children.return_value = mock_children
        
        def predicate(child):
            return child.get_attribute.return_value == "target_value"
        
        mock_children[0].get_attribute.return_value = "target_value"
        mock_children[1].get_attribute.return_value = "target_value"
        mock_children[2].get_attribute.return_value = "other_value"
        
        result = element_finder.find_children_by_predicate(predicate)
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[1] in result

    def test_find_visible_children_success(self, element_finder, mock_children, mocker):
        """Test successful visible children finding"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].is_displayed.return_value = True
        mock_children[1].is_displayed.return_value = False
        mock_children[2].is_displayed.return_value = True
        
        result = element_finder.find_visible_children()
        
        assert len(result) == 2
        assert mock_children[0] in result
        assert mock_children[2] in result

    def test_find_enabled_children_success(self, element_finder, mock_children, mocker):
        """Test successful enabled children finding"""
        element_finder._element.get_children.return_value = mock_children
        
        # Mock is_enabled method for each child
        for child in mock_children:
            child.is_enabled.return_value = True
        
        result = element_finder.find_enabled_children()
        
        assert len(result) == 3
        assert all(child in result for child in mock_children)

    def test_find_enabled_children_exception(self, element_finder, mock_children, mocker):
        """Test enabled children finding with exception"""
        element_finder._element.get_children.return_value = mock_children
        
        # Mock is_enabled method to raise exception
        mock_children[0].is_enabled.side_effect = Exception("Test exception")
        mock_children[1].is_enabled.return_value = True
        mock_children[2].is_enabled.return_value = True
        
        result = element_finder.find_enabled_children()
        
        assert len(result) == 2
        assert mock_children[1] in result
        assert mock_children[2] in result

    def test_find_enabled_children_no_is_enabled_method(self, element_finder, mock_children, mocker):
        """Test enabled children finding when is_enabled method is not available"""
        element_finder._element.get_children.return_value = mock_children
        
        # Remove is_enabled method from children
        for child in mock_children:
            child.is_enabled = None
        
        result = element_finder.find_enabled_children()
        
        assert len(result) == 3
        assert all(child in result for child in mock_children)

    def test_get_children_using_get_children_method(self, element_finder, mock_children, mocker):
        """Test get_children using get_children method"""
        element_finder._element.get_children.return_value = mock_children
        
        result = element_finder.get_children()
        
        assert result == mock_children

    def test_get_children_using_findall_method(self, element_finder, mock_children, mocker):
        """Test get_children using findall method"""
        element_finder._element.get_children = None
        element_finder._element.findall.return_value = mock_children
        
        result = element_finder.get_children()
        
        assert result == mock_children

    def test_get_children_using_children_attribute(self, element_finder, mock_children, mocker):
        """Test get_children using children attribute"""
        element_finder._element.get_children = None
        element_finder._element.findall = None
        element_finder._element.children = mock_children
        
        result = element_finder.get_children()
        
        assert result == mock_children

    def test_get_children_no_methods_available(self, element_finder, mocker):
        """Test get_children when no methods are available"""
        element_finder._element.get_children = None
        element_finder._element.findall = None
        element_finder._element.children = None
        
        result = element_finder.get_children()
        
        assert result == []

    def test_get_children_exception(self, element_finder, mocker):
        """Test get_children with exception"""
        element_finder._element.get_children.side_effect = Exception("Test exception")
        
        result = element_finder.get_children()
        
        assert result == []

    def test_detect_property_type_unknown_property(self, element_finder, mocker):
        """Test detect_property_type with unknown property"""
        result = element_finder.detect_property_type("unknown_property")
        assert result == "string"

    def test_detect_property_type_known_property(self, element_finder, mocker):
        """Test detect_property_type with known property"""
        result = element_finder.detect_property_type("name")
        assert result == "string"

    def test_detect_property_type_exception(self, element_finder, mocker):
        """Test detect_property_type with exception"""
        # Mock _property_type_mapping to raise exception
        element_finder._property_type_mapping = None
        
        result = element_finder.detect_property_type("test_property")
        assert result == "string"

    def test_find_child_by_property_with_custom_type(self, element_finder, mock_children, mocker):
        """Test find_child_by_property with custom property type"""
        element_finder._element.get_children.return_value = mock_children
        mock_children[0].get_attribute.return_value = "expected_value"
        
        result = element_finder.find_child_by_property("custom_property", "expected_value")
        
        assert result == mock_children[0] 