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
    mock_rating_element.get_property.assert_any_call('value')


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
    rating.click_at_offset = MagicMock()
    # Гарантируем, что readonly=False
    mock_rating_element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': False,
        'half_stars': True,
        'star_width': 20
    }.get(prop)
    rating.set_rating(4.5)
    # Verify click position calculation
    mock_rating_element.get_property.assert_any_call('star_width')
    rating.click_at_offset.assert_called_once_with(90, 0)  # 4.5 * 20


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
    rating.click_at_offset = MagicMock()
    rating._readonly = True
    rating.set_rating(4.0)
    rating.click_at_offset.assert_not_called()


def test_rating_clear(rating, mock_rating_element):
    """Test clearing rating."""
    rating.click_at_offset = MagicMock()
    # Гарантируем, что readonly=False
    mock_rating_element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': False,
        'half_stars': True,
        'star_width': 20
    }.get(prop)
    rating.clear()
    rating.click_at_offset.assert_called_once_with(0, 0)


def test_rating_clear_readonly(rating, mock_rating_element):
    """Test clearing rating when read-only."""
    mock_rating_element.get_property.side_effect = lambda prop: {
        'value': 3.0,
        'maximum': 5,
        'readonly': True,
        'half_stars': True,
        'star_width': 20
    }.get(prop)
    rating.click_at_offset = MagicMock()
    rating._readonly = True
    rating.clear()
    rating.click_at_offset.assert_not_called()


def test_rating_hover_rating_valid(rating, mock_rating_element):
    """Test hovering over valid rating value."""
    rating.hover_at_offset = MagicMock()
    rating.hover_rating(4.5)
    
    mock_rating_element.get_property.assert_called_with('star_width')
    rating.hover_at_offset.assert_called_once_with(90, 0)  # 4.5 * 20


def test_rating_hover_rating_out_of_range(rating):
    """Test hovering over out of range rating value."""
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        rating.hover_rating(6.0)
    
    with pytest.raises(ValueError, match="Rating must be between 0 and 5"):
        rating.hover_rating(-1.0)


class RatingMock(Rating):
    def __init__(self, native_element, session, value=3.0):
        super().__init__(native_element, session)
        self._mock_value = value
    @property
    def value(self):
        return self._mock_value

def test_rating_wait_until_value(mock_rating_element, mock_session):
    """Test waiting for specific rating value (без patch.object, через double)."""
    rating = RatingMock(mock_rating_element, mock_session, value=4.0)
    assert rating.wait_until_value(4.0, timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    rating._mock_value = 4.0
    assert condition_func()
    rating._mock_value = 3.0
    assert not condition_func()
    rating._mock_value = 4.05
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


class TestRatingProperty:
    def setup_method(self):
        self.rating = Rating(MagicMock(), MagicMock())

    def test_value_setter(self):
        self.rating.value = 7
        assert self.rating.value == 7

    def test_value_deleter(self):
        self.rating.value = 5
        del self.rating.value
        assert self.rating.value == 0

    def test_is_readonly_setter(self):
        self.rating.is_readonly = True
        assert self.rating.is_readonly is True

    def test_is_readonly_deleter(self):
        self.rating.is_readonly = False
        del self.rating.is_readonly
        assert self.rating.is_readonly is True
