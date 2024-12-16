import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.progressbar import ProgressBar


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_progressbar_element():
    element = MagicMock()
    
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'value': 50.0,
        'minimum': 0.0,
        'maximum': 100.0,
        'indeterminate': False,
        'status': 'Processing...'
    }.get(prop)
    
    return element


@pytest.fixture
def progressbar(mock_progressbar_element, mock_session):
    return ProgressBar(mock_progressbar_element, mock_session)


def test_progressbar_init(progressbar, mock_progressbar_element, mock_session):
    """Test progress bar initialization."""
    assert progressbar._element == mock_progressbar_element
    assert progressbar._session == mock_session


def test_progressbar_value(progressbar, mock_progressbar_element):
    """Test getting current progress value."""
    assert progressbar.value == 50.0
    mock_progressbar_element.get_property.assert_called_with('value')


def test_progressbar_minimum(progressbar, mock_progressbar_element):
    """Test getting minimum value."""
    assert progressbar.minimum == 0.0
    mock_progressbar_element.get_property.assert_called_with('minimum')


def test_progressbar_maximum(progressbar, mock_progressbar_element):
    """Test getting maximum value."""
    assert progressbar.maximum == 100.0
    mock_progressbar_element.get_property.assert_called_with('maximum')


def test_progressbar_percentage_normal(progressbar):
    """Test getting progress percentage in normal case."""
    assert progressbar.percentage == 50.0


def test_progressbar_percentage_zero_range(progressbar, mock_progressbar_element):
    """Test getting progress percentage when min equals max."""
    mock_progressbar_element.get_property.side_effect = lambda prop: {
        'value': 10.0,
        'minimum': 10.0,
        'maximum': 10.0,
        'indeterminate': False,
        'status': 'Processing...'
    }.get(prop)
    
    assert progressbar.percentage == 0.0


def test_progressbar_percentage_custom_range(progressbar, mock_progressbar_element):
    """Test getting progress percentage with custom range."""
    mock_progressbar_element.get_property.side_effect = lambda prop: {
        'value': 75.0,
        'minimum': 50.0,
        'maximum': 150.0,
        'indeterminate': False,
        'status': 'Processing...'
    }.get(prop)
    
    assert progressbar.percentage == 25.0  # (75 - 50) / (150 - 50) * 100


def test_progressbar_is_indeterminate(progressbar, mock_progressbar_element):
    """Test checking if progress bar is indeterminate."""
    assert not progressbar.is_indeterminate
    mock_progressbar_element.get_property.assert_called_with('indeterminate')


def test_progressbar_status_text(progressbar, mock_progressbar_element):
    """Test getting status text."""
    assert progressbar.status_text == 'Processing...'
    mock_progressbar_element.get_property.assert_called_with('status')


def test_progressbar_status_text_none(progressbar, mock_progressbar_element):
    """Test getting status text when not available."""
    mock_progressbar_element.get_property.side_effect = lambda prop: {
        'value': 50.0,
        'minimum': 0.0,
        'maximum': 100.0,
        'indeterminate': False,
        'status': None
    }.get(prop)
    
    assert progressbar.status_text is None
    mock_progressbar_element.get_property.assert_called_with('status')


def test_progressbar_wait_until_complete(progressbar, mock_session):
    """Test waiting for progress to complete."""
    assert progressbar.wait_until_complete(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different progress values
    with patch.object(progressbar, 'value', 100.0):
        assert condition_func()
    with patch.object(progressbar, 'value', 99.9):
        assert not condition_func()


def test_progressbar_wait_until_value(progressbar, mock_session):
    """Test waiting for specific progress value."""
    target_value = 75.0
    assert progressbar.wait_until_value(target_value, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different progress values
    with patch.object(progressbar, 'value', 80.0):
        assert condition_func()
    with patch.object(progressbar, 'value', 70.0):
        assert not condition_func()


def test_progressbar_wait_until_percentage(progressbar, mock_session):
    """Test waiting for specific progress percentage."""
    target_percentage = 75.0
    assert progressbar.wait_until_percentage(target_percentage, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different percentages
    with patch.object(progressbar, 'percentage', 80.0):
        assert condition_func()
    with patch.object(progressbar, 'percentage', 70.0):
        assert not condition_func()


def test_progressbar_wait_until_percentage_invalid(progressbar):
    """Test waiting for invalid percentage value."""
    with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
        progressbar.wait_until_percentage(150.0)
    
    with pytest.raises(ValueError, match="Percentage must be between 0 and 100"):
        progressbar.wait_until_percentage(-10.0)


def test_progressbar_wait_until_status(progressbar, mock_session):
    """Test waiting for specific status text."""
    target_status = 'Completed'
    assert progressbar.wait_until_status(target_status, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different status texts
    with patch.object(progressbar, 'status_text', 'Completed'):
        assert condition_func()
    with patch.object(progressbar, 'status_text', 'Processing...'):
        assert not condition_func()
