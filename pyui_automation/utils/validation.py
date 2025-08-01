from typing import Any, Callable, Optional, Type, Union, List, Tuple
import re


def validate_type(value: Any, expected_type: Union[Type[Any], Tuple[Type[Any], ...]]) -> bool:
    """
    Validate that a given value is of the expected type or types.

    Args:
        value: The value to be checked.
        expected_type: The expected type(s) that the value should be an instance of. 
                       It can be a single type or a tuple of types.

    Returns:
        bool: True if the value is an instance of the expected type(s), False otherwise.
    """
    return isinstance(value, expected_type)

def validate_not_none(value: Any) -> bool:
    """
    Validate that a given value is not None.

    Args:
        value: The value to be checked.

    Returns:
        bool: True if the value is not None, False otherwise.
    """
    return value is not None

def validate_string_not_empty(value: Optional[str]) -> bool:
    """
    Validate string is not empty.

    Args:
        value: The string to be checked.

    Returns:
        bool: True if the string is not empty, False otherwise.
    """
    if value is None:
        return False
    return bool(value.strip())

def validate_number_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None
) -> bool:
    """
    Validate that a given number is within a specified range.

    Args:
        value: The number to be validated.
        min_value: The minimum allowable value (inclusive). If None, no lower bound is enforced.
        max_value: The maximum allowable value (inclusive). If None, no upper bound is enforced.

    Returns:
        bool: True if the value is within the specified range, False otherwise.
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def validate_regex(value: str, pattern: str) -> bool:
    """
    Validate that a string matches a regular expression pattern.
    
    Args:
        value: The string to validate
        pattern: The regex pattern to match against
        
    Returns:
        bool: True if the string matches the pattern, False otherwise
    """
    try:
        return bool(re.match(pattern, value))
    except re.error:
        return False


def validate_callable(value: Any) -> bool:
    """
    Validate that a value is callable.
    
    Args:
        value: The value to check
        
    Returns:
        bool: True if the value is callable, False otherwise
    """
    return callable(value)


def validate_iterable(value: Any) -> bool:
    """
    Validate that a value is iterable.
    
    Args:
        value: The value to check
        
    Returns:
        bool: True if the value is iterable, False otherwise
    """
    try:
        iter(value)
        return True  # Strings are iterable too
    except TypeError:
        return False


def validate_all(validators: List[Callable[[Any], bool]], value: Any) -> bool:
    """
    Validate that a value passes all validators.
    
    Args:
        validators: List of validator functions
        value: The value to validate
        
    Returns:
        bool: True if all validators pass, False otherwise
    """
    return all(validator(value) for validator in validators)


def validate_any(validators: List[Callable[[Any], bool]], value: Any) -> bool:
    """
    Validate that a value passes at least one validator.
    
    Args:
        validators: List of validator functions
        value: The value to validate
        
    Returns:
        bool: True if any validator passes, False otherwise
    """
    return any(validator(value) for validator in validators)
