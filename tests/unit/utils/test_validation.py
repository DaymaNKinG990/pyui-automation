"""
Tests for validation utilities
"""
import pytest



class TestValidateNotNone:
    """Tests for validate_not_none function"""
    
    @pytest.mark.parametrize("value", [
        "test", 0, False, [], {}, np.array([1, 2, 3])
    ])
    def test_validate_not_none_with_valid_values(self, value):
        """Test validate_not_none with valid non-None values"""
        assert validate_not_none(value) is True
    
    def test_validate_not_none_with_none(self):
        """Test validate_not_none with None value"""
        assert validate_not_none(None) is False


class TestValidateStringNotEmpty:
    """Tests for validate_string_not_empty function"""
    
    @pytest.mark.parametrize("value", [
        "test", "hello world", "123", "a"
    ])
    def test_validate_string_not_empty_with_valid_strings(self, value):
        """Test validate_string_not_empty with valid non-empty strings"""
        assert validate_string_not_empty(value) is True
    
    @pytest.mark.parametrize("value", [
        "", "   ", "\t\n", None
    ])
    def test_validate_string_not_empty_with_invalid_strings(self, value):
        """Test validate_string_not_empty with invalid strings"""
        assert validate_string_not_empty(value) is False


class TestValidateType:
    """Tests for validate_type function"""
    
    def test_validate_type_with_correct_type(self):
        """Test validate_type with correct type"""
        assert validate_type("test", str) is True
        assert validate_type(123, int) is True
        assert validate_type([1, 2, 3], list) is True
    
    def test_validate_type_with_incorrect_type(self):
        """Test validate_type with incorrect type"""
        assert validate_type("test", int) is False
        assert validate_type(123, str) is False
        assert validate_type([1, 2, 3], dict) is False
    
    def test_validate_type_with_none(self):
        """Test validate_type with None value"""
        assert validate_type(None, str) is False
    
    def test_validate_type_with_tuple_of_types(self):
        """Test validate_type with tuple of types"""
        assert validate_type("test", (str, int)) is True
        assert validate_type(123, (str, int)) is True
        assert validate_type([1, 2, 3], (str, int)) is False


class TestValidateNumberRange:
    """Tests for validate_number_range function"""
    
    @pytest.mark.parametrize("value,min_val,max_val", [
        (5, 0, 10),
        (0, 0, 10),
        (10, 0, 10),
        (5, None, 10),
        (5, 0, None),
        (5, None, None),
        (5.5, 0.0, 10.0),
        (-5, -10, 0)
    ])
    def test_validate_number_range_with_valid_values(self, value, min_val, max_val):
        """Test validate_number_range with valid values"""
        assert validate_number_range(value, min_val, max_val) is True
    
    @pytest.mark.parametrize("value,min_val,max_val", [
        (-1, 0, 10),
        (11, 0, 10),
        (5, 10, 0),  # min > max
        (5.1, 0, 5.0)
    ])
    def test_validate_number_range_with_invalid_values(self, value, min_val, max_val):
        """Test validate_number_range with invalid values"""
        assert validate_number_range(value, min_val, max_val) is False


class TestValidateRegex:
    """Tests for validate_regex function"""
    
    @pytest.mark.parametrize("value,pattern", [
        ("test123", r"^[a-z]+\d+$"),
        ("hello", r"^h.*o$"),
        ("123", r"^\d+$"),
        ("", r"^$")
    ])
    def test_validate_regex_with_valid_patterns(self, value, pattern):
        """Test validate_regex with valid patterns"""
        assert validate_regex(value, pattern) is True
    
    @pytest.mark.parametrize("value,pattern", [
        ("test", r"^\d+$"),
        ("123", r"^[a-z]+$"),
        ("hello", r"^world$"),
        ("test", r"[invalid[pattern")
    ])
    def test_validate_regex_with_invalid_patterns(self, value, pattern):
        """Test validate_regex with invalid patterns"""
        assert validate_regex(value, pattern) is False


class TestValidateCallable:
    """Tests for validate_callable function"""
    
    def test_validate_callable_with_function(self):
        """Test validate_callable with function"""
        def test_func():
            pass
        assert validate_callable(test_func) is True
    
    def test_validate_callable_with_lambda(self):
        """Test validate_callable with lambda"""
        assert validate_callable(lambda x: x) is True
    
    def test_validate_callable_with_class(self):
        """Test validate_callable with class"""
        class TestClass:
            pass
        assert validate_callable(TestClass) is True
    
    def test_validate_callable_with_method(self):
        """Test validate_callable with method"""
        class TestClass:
            def test_method(self):
                pass
        assert validate_callable(TestClass().test_method) is True
    
    def test_validate_callable_with_non_callable(self):
        """Test validate_callable with non-callable"""
        assert validate_callable("not_callable") is False
        assert validate_callable(123) is False
        assert validate_callable([]) is False


class TestValidateIterable:
    """Tests for validate_iterable function"""
    
    @pytest.mark.parametrize("value", [
        [1, 2, 3],
        (1, 2, 3),
        {1, 2, 3},
        {"a": 1, "b": 2},
        "string",
        range(5),
        np.array([1, 2, 3])
    ])
    def test_validate_iterable_with_iterable_values(self, value):
        """Test validate_iterable with iterable values"""
        assert validate_iterable(value) is True
    
    @pytest.mark.parametrize("value", [
        123,
        3.14,
        True,
        False,
        None
    ])
    def test_validate_iterable_with_non_iterable_values(self, value):
        """Test validate_iterable with non-iterable values"""
        assert validate_iterable(value) is False


class TestValidateAll:
    """Tests for validate_all function"""
    
    def test_validate_all_with_all_passing(self):
        """Test validate_all with all validators passing"""
        validators = [
            lambda x: isinstance(x, str),
            lambda x: len(x) > 0,
            lambda x: x.isalpha()
        ]
        assert validate_all(validators, "hello") is True
    
    def test_validate_all_with_some_failing(self):
        """Test validate_all with some validators failing"""
        validators = [
            lambda x: isinstance(x, str),
            lambda x: len(x) > 10,  # This will fail
            lambda x: x.isalpha()
        ]
        assert validate_all(validators, "hello") is False
    
    def test_validate_all_with_empty_list(self):
        """Test validate_all with empty validators list"""
        assert validate_all([], "test") is True
    
    def test_validate_all_with_all_failing(self):
        """Test validate_all with all validators failing"""
        validators = [
            lambda x: isinstance(x, int),
            lambda x: x > 100
        ]
        assert validate_all(validators, "hello") is False


class TestValidateAny:
    """Tests for validate_any function"""
    
    def test_validate_any_with_some_passing(self):
        """Test validate_any with some validators passing"""
        validators = [
            lambda x: isinstance(x, int),
            lambda x: isinstance(x, str),
            lambda x: isinstance(x, list)
        ]
        assert validate_any(validators, "hello") is True
    
    def test_validate_any_with_all_failing(self):
        """Test validate_any with all validators failing"""
        validators = [
            lambda x: x > 100,
            lambda x: x < 0,
            lambda x: x == 50
        ]
        # Use integer value instead of string for numeric comparison
        assert validate_any(validators, 25) is False
    
    def test_validate_any_with_empty_list(self):
        """Test validate_any with empty validators list"""
        assert validate_any([], "test") is False
    
    def test_validate_any_with_all_passing(self):
        """Test validate_any with all validators passing"""
        validators = [
            lambda x: isinstance(x, str),
            lambda x: len(x) > 0,
            lambda x: x.isalpha()
        ]
        assert validate_any(validators, "hello") is True


class TestValidationEdgeCases:
    """Test edge cases in validation functions"""
    
    def test_validate_string_not_empty_with_single_character(self):
        """Test validate_string_not_empty with single character"""
        result = validate_string_not_empty("a")
        assert result is True
    
    def test_validate_string_not_empty_with_special_characters(self):
        """Test validate_string_not_empty with special characters"""
        result = validate_string_not_empty("!@#$%^&*()")
        assert result is True
    
    def test_validate_string_not_empty_with_unicode(self):
        """Test validate_string_not_empty with unicode characters"""
        result = validate_string_not_empty("привет мир")
        assert result is True
    
    def test_validate_string_not_empty_with_emoji(self):
        """Test validate_string_not_empty with emoji"""
        result = validate_string_not_empty("Hello 👋")
        assert result is True
    
    def test_validate_number_range_with_zero(self):
        """Test validate_number_range with zero"""
        result = validate_number_range(0, 0, 10)
        assert result is True
    
    def test_validate_number_range_with_negative(self):
        """Test validate_number_range with negative number"""
        result = validate_number_range(-123, -200, 0)
        assert result is True
    
    def test_validate_number_range_with_large_number(self):
        """Test validate_number_range with large number"""
        result = validate_number_range(999999999, 0, 1000000000)
        assert result is True
    
    def test_validate_number_range_with_float(self):
        """Test validate_number_range with float"""
        result = validate_number_range(3.14, 0.0, 10.0)
        assert result is True
    
    def test_validate_number_range_with_negative_float(self):
        """Test validate_number_range with negative float"""
        result = validate_number_range(-3.14, -10.0, 0.0)
        assert result is True
    
    def test_validate_regex_with_complex_pattern(self):
        """Test validate_regex with complex pattern"""
        result = validate_regex("test@example.com", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        assert result is True
    
    def test_validate_regex_with_invalid_email(self):
        """Test validate_regex with invalid email"""
        result = validate_regex("invalid-email", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        assert result is False
    
    def test_validate_iterable_with_generator(self):
        """Test validate_iterable with generator"""
        def gen():
            yield 1
            yield 2
            yield 3
        result = validate_iterable(gen())
        assert result is True
    
    def test_validate_iterable_with_iterator(self):
        """Test validate_iterable with iterator"""
        result = validate_iterable(iter([1, 2, 3]))
        assert result is True 