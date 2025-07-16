from typing import Optional, Any, List, TYPE_CHECKING, Dict
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class TableCell(UIElement):
    """Represents a table cell element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def text(self) -> str:
        """
        Get the text content of the cell.

        Returns:
            str: Cell text content
        """
        return self._element.get_property("text")

    @property
    def row_index(self) -> int:
        """
        Get the row index of the cell.

        Returns:
            int: Row index
        """
        return self._element.get_property("row_index")

    @property
    def column_index(self) -> int:
        """
        Get the column index of the cell.

        Returns:
            int: Column index
        """
        return self._element.get_property("column_index")

    @property
    def is_selected(self) -> bool:
        """
        Check if the cell is selected.

        Returns:
            bool: True if selected, False otherwise
        """
        return self._element.get_property("selected")

    def select(self) -> None:
        """Select the cell"""
        self.click()


class Table(UIElement):
    """Represents a table/grid control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def row_count(self) -> int:
        """
        Get the number of rows in the table.

        Returns:
            int: Number of rows
        """
        return self._element.get_property("row_count")

    @property
    def column_count(self) -> int:
        """
        Get the number of columns in the table.

        Returns:
            int: Number of columns
        """
        return self._element.get_property("column_count")

    @property
    def selected_cells(self) -> List[TableCell]:
        """
        Get all currently selected cells.

        Returns:
            List[TableCell]: List of selected cells
        """
        cells = self._element.find_elements(by="state", value="selected")
        return [TableCell(cell, self._session) for cell in cells]

    def get_cell(self, row: int, column: int) -> Optional[TableCell]:
        """
        Get a cell by its row and column indices.

        Args:
            row (int): Row index
            column (int): Column index

        Returns:
            Optional[TableCell]: The cell at the specified position or None if not found
        """
        if row < 0 or row >= self.row_count or column < 0 or column >= self.column_count:
            return None
        
        cell = self._element.find_element(
            by="position",
            value={"row": row, "column": column}
        )
        return TableCell(cell, self._session) if cell else None

    def get_cell_by_text(self, text: str) -> Optional[TableCell]:
        """Get first cell containing text"""
        cells = self.get_cells_by_text(text)
        return cells[0] if cells else None

    def get_cells_by_text(self, text: str) -> List[TableCell]:
        """
        Get all cells containing the specified text.

        Args:
            text (str): Text to search for

        Returns:
            List[TableCell]: List of cells containing the text
        """
        cells = self._element.find_elements(by="text", value=text)
        return [TableCell(cell, self._session) for cell in cells]

    def get_column_header(self, column: int) -> Optional[str]:
        """
        Get the header text for a specific column.

        Args:
            column (int): Column index

        Returns:
            Optional[str]: Column header text or None if not found
        """
        if column < 0 or column >= self.column_count:
            return None
        
        header = self._element.find_element(
            by="type",
            value="columnheader",
            index=column
        )
        return header.get_property("text") if header else None

    def select_cell(self, row: int, column: int) -> None:
        """
        Select a cell by its row and column indices.

        Args:
            row (int): Row index
            column (int): Column index

        Raises:
            ValueError: If cell not found
        """
        cell = self.get_cell(row, column)
        if cell:
            cell.select()
        else:
            raise ValueError(f"Cell at row {row}, column {column} not found")

    def select_cells_by_text(self, text: str) -> None:
        """
        Select all cells containing the specified text.

        Args:
            text (str): Text to search for
        """
        cells = self.get_cells_by_text(text)
        for cell in cells:
            cell.select()

    def wait_until_cell_value(self, row: int, column: int, value: str, timeout: float = 10) -> bool:
        """
        Wait until a cell contains a specific value.

        Args:
            row (int): Row index
            column (int): Column index
            value (str): Value to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if cell contained value within timeout, False otherwise
        """
        def check_value():
            cell = self.get_cell(row, column)
            return cell and cell.text == value

        return self._session.wait_for_condition(
            check_value,
            timeout=timeout,
            error_message=f"Cell at row {row}, column {column} did not contain value '{value}'"
        )
