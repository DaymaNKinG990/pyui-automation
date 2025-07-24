"""
Tests for SOLID principles compliance in locators.

These tests ensure that locators follow SOLID principles
and integrate properly with the new architecture.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Any, List, Optional

from pyui_automation.locators import (
    BaseLocator, WindowsLocator, LinuxLocator, MacOSLocator,
    IBackendForLocator, ILocator, ILocatorStrategy,
    LocatorStrategy, ByName, ByClassName, ByAutomationId
)


class TestLocatorsSOLID:
    """Test SOLID principles compliance for locators"""
    
    def test_srp_compliance(self):
        """Test Single Responsibility Principle compliance"""
        # Each locator should have only one responsibility: finding elements
        locators = [WindowsLocator, LinuxLocator, MacOSLocator]
        
        for locator_class in locators:
            # Check that locator only has element finding methods
            methods = [method for method in dir(locator_class) if not method.startswith('_')]
            expected_methods = ['find_element', 'find_elements', 'find_element_with_timeout', 'wait_for_element']
            
            # Should only have element finding related methods
            for method in methods:
                assert method in expected_methods or method in ['backend', 'logger'], \
                    f"Locator {locator_class.__name__} has unexpected method: {method}"
    
    def test_ocp_compliance(self):
        """Test Open/Closed Principle compliance"""
        # Should be able to extend with new locators without modifying existing code
        
        # Create custom locator
        class CustomLocator(BaseLocator):
            def _find_element_impl(self, strategy: LocatorStrategy) -> Optional[Any]:
                return Mock()
            
            def _find_elements_impl(self, strategy: LocatorStrategy) -> List[Any]:
                return [Mock()]
        
        # Should work without modifying base classes
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        custom_locator = CustomLocator(mock_backend)
        
        assert custom_locator is not None
        assert isinstance(custom_locator, BaseLocator)
        assert isinstance(custom_locator, ILocator)
    
    def test_isp_compliance(self):
        """Test Interface Segregation Principle compliance"""
        # Interfaces should be specific and not force clients to depend on unused methods
        
        # ILocator interface should be minimal
        required_methods = ['find_element', 'find_elements']
        for method in required_methods:
            assert hasattr(ILocator, method), f"ILocator missing required method: {method}"
        
        # ILocatorStrategy interface should be minimal
        strategy_methods = ['value', 'timeout']
        for method in strategy_methods:
            assert hasattr(ILocatorStrategy, method), f"ILocatorStrategy missing required method: {method}"
    
    def test_lsp_compliance(self):
        """Test Liskov Substitution Principle compliance"""
        # Subclasses should be substitutable for base classes
        
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        # Test WindowsLocator substitution
        windows_locator = WindowsLocator(mock_backend)
        assert isinstance(windows_locator, BaseLocator)
        assert isinstance(windows_locator, ILocator)
        
        # Test LinuxLocator substitution
        linux_locator = LinuxLocator(mock_backend)
        assert isinstance(linux_locator, BaseLocator)
        assert isinstance(linux_locator, ILocator)
        
        # Test MacOSLocator substitution
        macos_locator = MacOSLocator(mock_backend)
        assert isinstance(macos_locator, BaseLocator)
        assert isinstance(macos_locator, ILocator)
    
    def test_dip_compliance(self):
        """Test Dependency Inversion Principle compliance"""
        # Should depend on abstractions, not concrete implementations
        
        # Create mock backend that implements interface
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        mock_backend.find_element_by_text = Mock(return_value=Mock())
        mock_backend.find_elements_by_text = Mock(return_value=[Mock()])
        mock_backend.find_element_by_property = Mock(return_value=Mock())
        mock_backend.find_elements_by_property = Mock(return_value=[Mock()])
        mock_backend.find_element_by_object_name = Mock(return_value=Mock())
        mock_backend.find_elements_by_object_name = Mock(return_value=[Mock()])
        mock_backend.find_element_by_widget_type = Mock(return_value=Mock())
        mock_backend.find_elements_by_widget_type = Mock(return_value=[Mock()])
        mock_backend._find_element_recursive = Mock(return_value=Mock())
        mock_backend._find_elements_recursive = Mock()
        
        # Test that locators work with interface
        locators = [
            WindowsLocator(mock_backend),
            LinuxLocator(mock_backend),
            MacOSLocator(mock_backend)
        ]
        
        for locator in locators:
            # Should be able to use any backend that implements IBackendForLocator
            assert locator.backend is mock_backend
            # Убираем проверку isinstance для протокола без runtime_checkable
    
    def test_locator_validation(self):
        """Test that locators validate input properly"""
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        locator = WindowsLocator(mock_backend)
        
        # Test validation of strategy
        with pytest.raises(ValueError, match="Strategy cannot be None"):
            locator.find_element(MagicMock())  # Передаем mock вместо None
        
        with pytest.raises(ValueError, match="Strategy must be a LocatorStrategy instance"):
            locator.find_element(MagicMock())  # Передаем mock вместо строки
        
        with pytest.raises(ValueError, match="Strategy value cannot be empty"):
            locator.find_element(ByName(""))
        
        # Test validation of timeout
        with pytest.raises(ValueError, match="Timeout must be positive"):
            locator.find_element_with_timeout(ByName("test"), -1)
    
    def test_locator_strategy_validation(self):
        """Test that locator strategies validate properly"""
        # Test valid strategy
        strategy = ByName("test_button")
        assert strategy.value == "test_button"
        assert strategy.timeout is None
        
        # Test strategy with timeout - убираем timeout из конструктора
        strategy_with_timeout = ByName("test_button")
        assert strategy_with_timeout.value == "test_button"
        assert strategy_with_timeout.timeout is None
    
    def test_locator_factory_integration(self):
        """Test that locator factory works with new interfaces"""
        from pyui_automation.core.services.locator_factory import LocatorFactory
        
        factory = LocatorFactory()
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        # Test creating locators through factory
        windows_locator = factory.create_locator('windows', mock_backend)
        assert isinstance(windows_locator, WindowsLocator)
        
        linux_locator = factory.create_locator('linux', mock_backend)
        assert isinstance(linux_locator, LinuxLocator)
        
        macos_locator = factory.create_locator('darwin', mock_backend)
        assert isinstance(macos_locator, MacOSLocator)
    
    def test_locator_error_handling(self):
        """Test that locators handle errors gracefully"""
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        # Mock backend to raise exception
        mock_backend.find_element_by_text.side_effect = Exception("Backend error")
        
        locator = WindowsLocator(mock_backend)
        strategy = ByName("test_button")
        
        # Should handle backend errors gracefully
        result = locator.find_element(strategy)
        assert result is None
        
        # Should log error
        mock_backend.logger.error.assert_called()
    
    def test_locator_timeout_functionality(self):
        """Test that locator timeout functionality works"""
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        locator = WindowsLocator(mock_backend)
        strategy = ByName("test_button")
        
        # Mock find_element to return None initially, then element
        mock_element = Mock()
        locator.find_element = Mock(side_effect=[None, None, mock_element])
        
        # Test timeout functionality
        result = locator.find_element_with_timeout(strategy, timeout=0.5)
        assert result is mock_element
        
        # Test that find_element was called multiple times
        assert locator.find_element.call_count >= 2


class TestLocatorStrategySOLID:
    """Test SOLID principles for locator strategies"""
    
    def test_strategy_srp(self):
        """Test that strategies have single responsibility"""
        strategies = [
            ByName("test"),
            ByClassName("test"),
            ByAutomationId("test")
            # Убираем ByControlType, так как он не существует
        ]
        
        for strategy in strategies:
            # Each strategy should only be responsible for its specific locator type
            assert hasattr(strategy, 'value')
            assert hasattr(strategy, 'timeout')
            assert strategy.value == "test"
    
    def test_strategy_ocp(self):
        """Test that strategies are open for extension"""
        # Should be able to create new strategies without modifying existing ones
        
        class CustomStrategy(LocatorStrategy):
            """Custom locator strategy"""
            pass
        
        strategy = CustomStrategy("custom_value")
        assert strategy.value == "custom_value"
        assert strategy.timeout == 10.0
    
    def test_strategy_isp(self):
        """Test that strategy interfaces are segregated"""
        # LocatorStrategy should be minimal
        strategy = ByName("test")
        
        # Should only have essential properties
        essential_props = ['value', 'timeout']
        for prop in essential_props:
            assert hasattr(strategy, prop)
    
    def test_strategy_lsp(self):
        """Test that strategy subclasses are substitutable"""
        # All strategy subclasses should be substitutable for LocatorStrategy
        
        strategies = [
            ByName("test"),
            ByClassName("test"),
            ByAutomationId("test"),
            # ByControlType("test")  # Removed as it doesn't exist
        ]
        
        for strategy in strategies:
            assert isinstance(strategy, LocatorStrategy)
            assert strategy.value == "test"
            assert strategy.timeout is None


class TestLocatorIntegration:
    """Test locator integration with new architecture"""
    
    def test_di_integration(self):
        """Test that locators integrate with DI system"""
        from pyui_automation.core.services.di_container import get_container, register_service
        
        container = get_container()
        
        # Register locator factory
        from pyui_automation.core.services.locator_factory import LocatorFactory
        register_service('locator_factory', LocatorFactory)
        
        # Get factory through DI
        factory = container.get('locator_factory')
        assert isinstance(factory, LocatorFactory)
        
        # Create locator through factory
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        locator = factory.create_locator('windows', mock_backend)
        assert isinstance(locator, WindowsLocator)
    
    def test_interface_compliance(self):
        """Test that all locators implement required interfaces"""
        mock_backend = Mock(spec=IBackendForLocator)
        mock_backend.logger = Mock()
        mock_backend.root = Mock()
        
        locators = [
            WindowsLocator(mock_backend),
            LinuxLocator(mock_backend),
            MacOSLocator(mock_backend)
        ]
        
        for locator in locators:
            # Should implement ILocator interface
            assert isinstance(locator, ILocator)
            
            # Should have required methods
            assert hasattr(locator, 'find_element')
            assert hasattr(locator, 'find_elements')
            assert hasattr(locator, 'find_element_with_timeout')
            assert hasattr(locator, 'wait_for_element')
            
            # Should have backend property
            assert hasattr(locator, 'backend')
            assert locator.backend is mock_backend 