import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, datetime
from pyui_automation.elements.calendar import Calendar


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_calendar_element():
    element = MagicMock()
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'selected_date': '2024-01-15',
        'minimum_date': '2024-01-01',
        'maximum_date': '2024-12-31',
        'displayed_month': '2024-01'
    }.get(prop)
    
    # Mock buttons
    mock_next = MagicMock()
    mock_prev = MagicMock()
    mock_today = MagicMock()
    mock_clear = MagicMock()
    mock_date = MagicMock()
    
    element.find_element.side_effect = lambda by, value: {
        'NextButton': mock_next,
        'PreviousButton': mock_prev,
        'TodayButton': mock_today,
        'ClearButton': mock_clear,
        '2024-01-20': mock_date
    }.get(value)
    
    return element

@pytest.fixture
def calendar(mock_calendar_element, mock_session):
    return Calendar(mock_calendar_element, mock_session)

def test_init(calendar, mock_calendar_element, mock_session):
    """Test calendar initialization."""
    assert calendar._element == mock_calendar_element
    assert calendar._session == mock_session

def test_selected_date(calendar, mock_calendar_element):
    """Test getting selected date."""
    assert calendar.selected_date == date(2024, 1, 15)
    mock_calendar_element.get_property.assert_called_with('selected_date')

def test_selected_date_none(calendar, mock_calendar_element):
    """Test getting selected date when none selected."""
    mock_calendar_element.get_property.side_effect = lambda prop: None if prop == 'selected_date' else ''
    assert calendar.selected_date is None

def test_minimum_date(calendar, mock_calendar_element):
    """Test getting minimum date."""
    assert calendar.minimum_date == date(2024, 1, 1)
    mock_calendar_element.get_property.assert_called_with('minimum_date')

def test_minimum_date_none(calendar, mock_calendar_element):
    """Test getting minimum date when none set."""
    mock_calendar_element.get_property.side_effect = lambda prop: None if prop == 'minimum_date' else ''
    assert calendar.minimum_date is None

def test_maximum_date(calendar, mock_calendar_element):
    """Test getting maximum date."""
    assert calendar.maximum_date == date(2024, 12, 31)
    mock_calendar_element.get_property.assert_called_with('maximum_date')

def test_maximum_date_none(calendar, mock_calendar_element):
    """Test getting maximum date when none set."""
    mock_calendar_element.get_property.side_effect = lambda prop: None if prop == 'maximum_date' else ''
    assert calendar.maximum_date is None

def test_displayed_month(calendar, mock_calendar_element):
    """Test getting displayed month."""
    assert calendar.displayed_month == date(2024, 1, 1)
    mock_calendar_element.get_property.assert_called_with('displayed_month')

def test_select_date_valid(calendar, mock_calendar_element):
    """Test selecting a valid date."""
    test_date = date(2024, 1, 20)
    calendar.select_date(test_date)
    mock_calendar_element.find_element.assert_called_with(by="date", value="2024-01-20")

def test_select_date_before_minimum(calendar):
    """Test selecting date before minimum."""
    with pytest.raises(ValueError, match="Date must not be before 2024-01-01"):
        calendar.select_date(date(2023, 12, 31))

def test_select_date_after_maximum(calendar):
    """Test selecting date after maximum."""
    with pytest.raises(ValueError, match="Date must not be after 2024-12-31"):
        calendar.select_date(date(2025, 1, 1))

def test_select_date_navigate_forward(calendar, mock_calendar_element):
    """Test selecting date requiring forward navigation."""
    # Setup mock to simulate month changes
    displayed_month = ['2024-01', '2024-02', '2024-03']
    current_month_index = 0
    
    def get_property_side_effect(prop):
        nonlocal current_month_index
        if prop == 'displayed_month':
            return displayed_month[current_month_index]
        return {
            'selected_date': None,
            'minimum_date': '2024-01-01',
            'maximum_date': '2024-12-31'
        }.get(prop)
    
    mock_calendar_element.get_property.side_effect = get_property_side_effect
    
    # Setup next month button click to advance the month
    def find_element_side_effect(by, value):
        nonlocal current_month_index
        element = MagicMock()
        if value == 'NextButton':
            def click_effect():
                nonlocal current_month_index
                if current_month_index < len(displayed_month) - 1:
                    current_month_index += 1
            element.click.side_effect = click_effect
        return element
    
    mock_calendar_element.find_element.side_effect = find_element_side_effect
    
    # Attempt to select date in March
    test_date = date(2024, 3, 15)
    calendar.select_date(test_date)
    
    # Verify that we navigated forward twice (Jan -> Feb -> Mar)
    next_button_calls = [call for call in mock_calendar_element.find_element.call_args_list 
                        if call[1]['value'] == 'NextButton']
    assert len(next_button_calls) == 2

def test_select_date_navigate_backward(calendar, mock_calendar_element):
    """Test selecting date requiring backward navigation."""
    # Setup mock to simulate month changes
    displayed_month = ['2024-03', '2024-02', '2024-01']
    current_month_index = 0
    
    def get_property_side_effect(prop):
        nonlocal current_month_index
        if prop == 'displayed_month':
            return displayed_month[current_month_index]
        return {
            'selected_date': None,
            'minimum_date': '2024-01-01',
            'maximum_date': '2024-12-31'
        }.get(prop)
    
    mock_calendar_element.get_property.side_effect = get_property_side_effect
    
    # Setup previous month button click to go back in months
    def find_element_side_effect(by, value):
        nonlocal current_month_index
        element = MagicMock()
        if value == 'PreviousButton':
            def click_effect():
                nonlocal current_month_index
                if current_month_index < len(displayed_month) - 1:
                    current_month_index += 1
            element.click.side_effect = click_effect
        return element
    
    mock_calendar_element.find_element.side_effect = find_element_side_effect
    
    # Attempt to select date in January
    test_date = date(2024, 1, 15)
    calendar.select_date(test_date)
    
    # Verify that we navigated backward twice (Mar -> Feb -> Jan)
    prev_button_calls = [call for call in mock_calendar_element.find_element.call_args_list 
                        if call[1]['value'] == 'PreviousButton']
    assert len(prev_button_calls) == 2

def test_next_month(calendar, mock_calendar_element):
    """Test navigating to next month."""
    calendar._next_month()
    mock_calendar_element.find_element.assert_called_with(by="name", value="NextButton")

def test_previous_month(calendar, mock_calendar_element):
    """Test navigating to previous month."""
    calendar._previous_month()
    mock_calendar_element.find_element.assert_called_with(by="name", value="PreviousButton")

def test_today(calendar, mock_calendar_element):
    """Test selecting today's date."""
    calendar.today()
    mock_calendar_element.find_element.assert_called_with(by="name", value="TodayButton")

def test_clear(calendar, mock_calendar_element):
    """Test clearing date selection."""
    calendar.clear()
    mock_calendar_element.find_element.assert_called_with(by="name", value="ClearButton")

def test_wait_until_date_selected(calendar, mock_session):
    """Test waiting for date to be selected."""
    test_date = date(2024, 1, 15)
    
    # Setup mock behavior for selected_date property
    selected_dates = [None, None, test_date]  # Simulate waiting before date is selected
    current_index = 0
    
    def get_selected_date():
        nonlocal current_index
        if current_index < len(selected_dates):
            result = selected_dates[current_index]
            current_index += 1
            return result
        return selected_dates[-1]
    
    with patch.object(calendar, 'selected_date', new_callable=PropertyMock) as mock_selected_date:
        mock_selected_date.side_effect = get_selected_date
        assert calendar.wait_until_date_selected(test_date, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()

def test_wait_until_month_displayed(calendar, mock_session):
    """Test waiting for month to be displayed."""
    target_month = date(2024, 1, 1)
    
    # Setup mock behavior for displayed_month property
    displayed_months = [date(2024, 2, 1), date(2024, 3, 1), target_month]  # Simulate waiting
    current_index = 0
    
    def get_displayed_month():
        nonlocal current_index
        if current_index < len(displayed_months):
            result = displayed_months[current_index]
            current_index += 1
            return result
        return displayed_months[-1]
    
    with patch.object(calendar, 'displayed_month', new_callable=PropertyMock) as mock_displayed_month:
        mock_displayed_month.side_effect = get_displayed_month
        assert calendar.wait_until_month_displayed(2024, 1, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
