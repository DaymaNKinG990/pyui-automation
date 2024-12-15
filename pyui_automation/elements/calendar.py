from typing import Optional, Any
from datetime import date, datetime
from .base import UIElement


class Calendar(UIElement):
    """Represents a calendar control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def selected_date(self) -> Optional[date]:
        """
        Get the currently selected date.

        Returns:
            Optional[date]: Selected date or None if none selected
        """
        value = self._element.get_property("selected_date")
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None

    @property
    def minimum_date(self) -> Optional[date]:
        """
        Get the minimum allowed date.

        Returns:
            Optional[date]: Minimum date or None if no minimum
        """
        value = self._element.get_property("minimum_date")
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None

    @property
    def maximum_date(self) -> Optional[date]:
        """
        Get the maximum allowed date.

        Returns:
            Optional[date]: Maximum date or None if no maximum
        """
        value = self._element.get_property("maximum_date")
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None

    @property
    def displayed_month(self) -> date:
        """
        Get the first day of the currently displayed month.

        Returns:
            date: First day of displayed month
        """
        value = self._element.get_property("displayed_month")
        return datetime.strptime(value, "%Y-%m").date()

    def select_date(self, date_value: date) -> None:
        """
        Select a specific date.

        Args:
            date_value (date): Date to select

        Raises:
            ValueError: If date out of range
        """
        if self.minimum_date and date_value < self.minimum_date:
            raise ValueError(f"Date must not be before {self.minimum_date}")
        if self.maximum_date and date_value > self.maximum_date:
            raise ValueError(f"Date must not be after {self.maximum_date}")

        # Navigate to the correct month if needed
        while self.displayed_month.year < date_value.year or \
              (self.displayed_month.year == date_value.year and 
               self.displayed_month.month < date_value.month):
            self._next_month()

        while self.displayed_month.year > date_value.year or \
              (self.displayed_month.year == date_value.year and 
               self.displayed_month.month > date_value.month):
            self._previous_month()

        # Find and click the date
        day_element = self._element.find_element(
            by="date",
            value=date_value.strftime("%Y-%m-%d")
        )
        if day_element:
            day_element.click()
        else:
            raise ValueError(f"Could not find element for date {date_value}")

    def _next_month(self) -> None:
        """Navigate to the next month"""
        next_button = self._element.find_element(by="name", value="NextButton")
        if next_button:
            next_button.click()

    def _previous_month(self) -> None:
        """Navigate to the previous month"""
        prev_button = self._element.find_element(by="name", value="PreviousButton")
        if prev_button:
            prev_button.click()

    def today(self) -> None:
        """Select today's date"""
        today_button = self._element.find_element(by="name", value="TodayButton")
        if today_button:
            today_button.click()

    def clear(self) -> None:
        """Clear the date selection"""
        clear_button = self._element.find_element(by="name", value="ClearButton")
        if clear_button:
            clear_button.click()

    def wait_until_date_selected(self, date_value: date, timeout: float = 10) -> bool:
        """
        Wait until a specific date is selected.

        Args:
            date_value (date): Date to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if date was selected within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.selected_date == date_value,
            timeout=timeout,
            error_message=f"Date {date_value} was not selected"
        )

    def wait_until_month_displayed(self, year: int, month: int, timeout: float = 10) -> bool:
        """
        Wait until a specific month is displayed.

        Args:
            year (int): Year to wait for
            month (int): Month to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if month was displayed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.displayed_month.year == year and self.displayed_month.month == month,
            timeout=timeout,
            error_message=f"Month {year}-{month} was not displayed"
        )
