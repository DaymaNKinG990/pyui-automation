import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.table import Table, TableCell


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_cell_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'text': 'Cell Text',
        'row_index': 1,
        'column_index': 2,
        'selected': False
    }.get(prop)
    return element


@pytest.fixture
def mock_table_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'row_count': 5,
        'column_count': 3
    }.get(prop)
    
    cell = MagicMock()
    element.find_elements.return_value = [cell]
    element.find_element.return_value = cell
    
    return element


@pytest.fixture
def table_cell(mock_cell_element, mock_session):
    return TableCell(mock_cell_element, mock_session)


@pytest.fixture
def table(mock_table_element, mock_session):
    return Table(mock_table_element, mock_session)


def test_cell_text(table_cell, mock_cell_element):
    """Test getting cell text."""
    assert table_cell.text == 'Cell Text'
    mock_cell_element.get_property.assert_called_with('text')


def test_cell_row_index(table_cell, mock_cell_element):
    """Test getting cell row index."""
    assert table_cell.row_index == 1
    mock_cell_element.get_property.assert_called_with('row_index')


def test_cell_column_index(table_cell, mock_cell_element):
    """Test getting cell column index."""
    assert table_cell.column_index == 2
    mock_cell_element.get_property.assert_called_with('column_index')


def test_cell_is_selected(table_cell, mock_cell_element):
    """Test checking if cell is selected."""
    assert not table_cell.is_selected
    mock_cell_element.get_property.assert_called_with('selected')


def test_cell_select(table_cell):
    """Test selecting a cell."""
    table_cell.select()
    table_cell._element.click.assert_called_once()


def test_table_row_count(table, mock_table_element):
    """Test getting row count."""
    assert table.row_count == 5
    mock_table_element.get_property.assert_called_with('row_count')


def test_table_column_count(table, mock_table_element):
    """Test getting column count."""
    assert table.column_count == 3
    mock_table_element.get_property.assert_called_with('column_count')


def test_table_selected_cells(table, mock_table_element):
    """Test getting selected cells."""
    cells = table.selected_cells
    assert len(cells) == 1
    assert isinstance(cells[0], TableCell)
    mock_table_element.find_elements.assert_called_with(by='state', value='selected')


def test_get_cell(table, mock_table_element):
    """Test getting cell by row and column."""
    cell = table.get_cell(1, 2)
    assert isinstance(cell, TableCell)
    mock_table_element.find_element.assert_called_once()


def test_get_cell_invalid(table, mock_table_element):
    """Test getting cell with invalid indices."""
    mock_table_element.find_element.return_value = None
    cell = table.get_cell(10, 10)
    assert cell is None


def test_get_cell_by_text(table, mock_table_element):
    """Test getting cell by text."""
    cell = table.get_cell_by_text('Cell Text')
    assert isinstance(cell, TableCell)
    mock_table_element.find_element.assert_called_once()


def test_get_cell_by_text_not_found(table, mock_table_element):
    """Test getting cell by text when not found."""
    mock_table_element.find_element.return_value = None
    cell = table.get_cell_by_text('Nonexistent')
    assert cell is None
