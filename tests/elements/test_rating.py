import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.rating import Rating


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_rating_element():
    element = MagicMock()
    
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': False,
        'half_stars': True,
        'star_width': 20
    }.get(prop)
    
    return element


@pytest.fixture
def rating(mock_rating_element, mock_session):
    return Rating(mock_rating_element, mock_session)


def test_rating_init(rating, mock_rating_element, mock_session):
    """Test rating initialization."""
    assert rating._element == mock_rating_element
    assert rating._session == mock_session


def test_rating_value(rating, mock_rating_element):
    """Test getting current rating value."""
    assert rating.value == 3.0
    mock_rating_element.get_property.assert_called_with('value')


def test_rating_maximum(rating, mock_rating_element):
    """Test getting maximum rating value."""
    assert rating.maximum == 5
    mock_rating_element.get_property.assert_called_with('maximum')


def test_rating_is_readonly(rating, mock_rating_element):
    """Test checking if rating is read-only."""
    assert not rating.is_readonly
    mock_rating_element.get_property.assert_called_with('readonly')


def test_rating_allows_half_stars(rating, mock_rating_element):
    """Test checking if half-star ratings are allowed."""
    assert rating.allows_half_stars
    mock_rating_element.get_property.assert_called_with('half_stars')


def test_rating_set_rating_valid(rating, mock_rating_element):
    """Test setting valid rating value."""
    rating.set_rating(4.5)
    
    # Verify click position calculation
    mock_rating_element.get_property.assert_called_with('star_width')
    rating._element.click_at_offset.assert_called_once_with(90, 0)  # 4.5 * 20


def test_rating_set_rating_out_of_range(rating):
    """Test setting rating value out of range."""
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        rating.set_rating(6.0)
    
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        rating.set_rating(-1.0)


def test_rating_set_rating_half_stars_not_allowed(rating, mock_rating_element):
    """Test setting half-star rating when not allowed."""
    mock_rating_element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': False,
        'half_stars': False,
        'star_width': 20
    }.get(prop)
    
    with pytest.raises(ValueError, match="Half-star ratings are not allowed"):
        rating.set_rating(3.5)


def test_rating_set_rating_readonly(rating, mock_rating_element):
    """Test setting rating when read-only."""
    mock_rating_element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': True,
        'half_stars': True,
        'star_width': 20
    }.get(prop)
    
    rating.set_rating(4.0)
    rating._element.click_at_offset.assert_not_called()


def test_rating_clear(rating):
    """Test clearing rating."""
    rating.clear()
    rating._element.click_at_offset.assert_called_once_with(0, 0)


def test_rating_clear_readonly(rating, mock_rating_element):
    """Test clearing rating when read-only."""
    mock_rating_element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': True,
        'half_stars': True,
        'star_width': 20
    }.get(prop)
    
    rating.clear()
    rating._element.click_at_offset.assert_not_called()


def test_rating_hover_rating_valid(rating, mock_rating_element):
    """Test hovering over valid rating value."""
    rating.hover_rating(4.5)
    
    mock_rating_element.get_property.assert_called_with('star_width')
    rating._element.hover_at_offset.assert_called_once_with(90, 0)  # 4.5 * 20


def test_rating_hover_rating_out_of_range(rating):
    """Test hovering over out of range rating value."""
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        rating.hover_rating(6.0)
    
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        rating.hover_rating(-1.0)


def test_rating_wait_until_value(rating, mock_session):
    """Test waiting for specific rating value."""
    assert rating.wait_until_value(4.0, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different values
    with patch.object(rating, 'value', 4.0):
        assert condition_func()
    with patch.object(rating, 'value', 3.0):
        assert not condition_func()
    # Test with close enough value (within 0.1)
    with patch.object(rating, 'value', 4.05):
        assert condition_func()


def test_rating_wait_until_interactive(rating, mock_session):
    """Test waiting for rating to become interactive."""
    assert rating.wait_until_interactive(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different readonly states
    with patch.object(rating, 'is_readonly', False):
        assert condition_func()
    with patch.object(rating, 'is_readonly', True):
        assert not condition_func()
