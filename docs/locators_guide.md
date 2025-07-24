# Locators Guide

Этот гайд описывает систему локаторов PyUI Automation для поиска UI элементов на разных платформах.

## Архитектура локаторов

Система локаторов построена на принципах SOLID и Clean Architecture:

- **BaseLocator** - абстрактный базовый класс для всех локаторов
- **LocatorStrategy** - стратегии поиска элементов
- **Платформо-зависимые локаторы** - WindowsLocator, LinuxLocator, MacOSLocator
- **Интерфейсы** - IBackendForLocator, ILocator, ILocatorStrategy

## Основные стратегии поиска

### ByName - поиск по имени элемента
```python
from pyui_automation.locators import ByName

# Поиск элемента по objectName
element = session.find_element(ByName("submitButton"))
```

### ByClassName - поиск по классу
```python
from pyui_automation.locators import ByClassName

# Поиск всех кнопок
buttons = session.find_elements(ByClassName("QPushButton"))
```

### ByAutomationId - поиск по Automation ID (Windows)
```python
from pyui_automation.locators import ByAutomationId

# Поиск по Automation ID
element = session.find_element(ByAutomationId("mainButton"))
```

### ByControlType - поиск по типу контрола
```python
from pyui_automation.locators import ByControlType

# Поиск всех текстовых полей
text_fields = session.find_elements(ByControlType("Edit"))
```

### ByXPath - поиск по XPath
```python
from pyui_automation.locators import ByXPath

# Поиск по XPath
element = session.find_element(ByXPath("//Button[@Name='Submit']"))
```

### ByAccessibilityId - поиск по Accessibility ID
```python
from pyui_automation.locators import ByAccessibilityId

# Поиск по Accessibility ID
element = session.find_element(ByAccessibilityId("mainButton"))
```

### ByRole - поиск по роли элемента
```python
from pyui_automation.locators import ByRole

# Поиск элементов с ролью "button"
buttons = session.find_elements(ByRole("button"))
```

### ByDescription - поиск по описанию
```python
from pyui_automation.locators import ByDescription

# Поиск по описанию
element = session.find_element(ByDescription("Submit form button"))
```

### ByPath - поиск по пути
```python
from pyui_automation.locators import ByPath

# Поиск по пути в дереве элементов
element = session.find_element(ByPath("MainWindow/ContentPanel/SubmitButton"))
```

### ByState - поиск по состоянию
```python
from pyui_automation.locators import ByState

# Поиск активных элементов
active_elements = session.find_elements(ByState("enabled"))
```

## Платформо-зависимые локаторы

### Windows Locator
```python
from pyui_automation.locators import WindowsLocator

# Создание Windows локатора
windows_locator = WindowsLocator(backend)

# Поиск элементов
element = windows_locator.find_element(ByName("mainButton"))
elements = windows_locator.find_elements(ByClassName("QPushButton"))
```

### Linux Locator
```python
from pyui_automation.locators import LinuxLocator

# Создание Linux локатора
linux_locator = LinuxLocator(backend)

# Поиск элементов
element = linux_locator.find_element(ByName("mainButton"))
elements = linux_locator.find_elements(ByClassName("QPushButton"))
```

### MacOS Locator
```python
from pyui_automation.locators import MacOSLocator

# Создание MacOS локатора
macos_locator = MacOSLocator(backend)

# Поиск элементов
element = macos_locator.find_element(ByName("mainButton"))
elements = macos_locator.find_elements(ByClassName("QPushButton"))
```

## Специфичные для платформы стратегии

### Windows-specific стратегии

#### ByAXIdentifier - поиск по AX Identifier
```python
from pyui_automation.locators import ByAXIdentifier

# Поиск по AX Identifier
element = session.find_element(ByAXIdentifier("mainButton"))
```

#### ByAXTitle - поиск по AX Title
```python
from pyui_automation.locators import ByAXTitle

# Поиск по AX Title
element = session.find_element(ByAXTitle("Submit Button"))
```

#### ByAXRole - поиск по AX Role
```python
from pyui_automation.locators import ByAXRole

# Поиск по AX Role
buttons = session.find_elements(ByAXRole("AXButton"))
```

#### ByAXDescription - поиск по AX Description
```python
from pyui_automation.locators import ByAXDescription

# Поиск по AX Description
element = session.find_element(ByAXDescription("Button to submit form"))
```

#### ByAXValue - поиск по AX Value
```python
from pyui_automation.locators import ByAXValue

# Поиск по AX Value
element = session.find_element(ByAXValue("Submit"))
```

## Использование через AutomationSession

### Базовый поиск
```python
from pyui_automation.core import AutomationSession
from pyui_automation.locators import ByName, ByClassName

session = AutomationSession(backend)

# Поиск одного элемента
button = session.find_element(ByName("submitButton"))

# Поиск нескольких элементов
buttons = session.find_elements(ByClassName("QPushButton"))
```

### Комбинированный поиск
```python
# Поиск кнопки в определенном контейнере
container = session.find_element(ByName("mainContainer"))
button = container.find_element(ByName("submitButton"))
```

### Поиск с ожиданием
```python
from pyui_automation.core.wait import wait_for_element

# Ожидание появления элемента
element = wait_for_element(session, ByName("dynamicButton"), timeout=10.0)
```

## Создание кастомных локаторов

### Расширение BaseLocator
```python
from pyui_automation.locators import BaseLocator, LocatorStrategy
from typing import Optional, List, Any

class CustomLocatorStrategy(LocatorStrategy):
    def __init__(self, custom_param: str):
        self.custom_param = custom_param
        super().__init__()

class CustomLocator(BaseLocator):
    def _find_element_impl(self, strategy: LocatorStrategy) -> Optional[Any]:
        if isinstance(strategy, CustomLocatorStrategy):
            # Реализация поиска
            return self.backend.find_element_by_custom(strategy.custom_param)
        return super()._find_element_impl(strategy)
    
    def _find_elements_impl(self, strategy: LocatorStrategy) -> List[Any]:
        if isinstance(strategy, CustomLocatorStrategy):
            # Реализация поиска
            return self.backend.find_elements_by_custom(strategy.custom_param)
        return super()._find_elements_impl(strategy)
```

### Регистрация кастомного локатора
```python
from pyui_automation.core.services import LocatorFactory

# Регистрация кастомного локатора
factory = LocatorFactory()
factory.register_custom_locator("custom", CustomLocator)

# Использование
locator = factory.create_locator("custom", backend)
```

## Best Practices

### Выбор стратегии поиска
- **ByName** - для элементов с уникальными именами
- **ByClassName** - для поиска элементов определенного типа
- **ByAutomationId** - для Windows приложений с настроенными Automation ID
- **ByXPath** - для сложных запросов поиска
- **ByPath** - для навигации по дереву элементов

### Производительность
- Используйте **find_element** вместо **find_elements** когда нужен один элемент
- Кэшируйте результаты поиска для часто используемых элементов
- Избегайте сложных XPath запросов в циклах

### Надежность
- Всегда проверяйте существование элемента перед взаимодействием
- Используйте wait_for_element для динамических элементов
- Добавляйте fallback стратегии поиска

### Платформо-зависимость
- Тестируйте локаторы на всех целевых платформах
- Используйте платформо-специфичные стратегии только при необходимости
- Создавайте абстракции для кроссплатформенного кода

## Примеры использования

### Поиск элементов в Notepad++
```python
from pyui_automation.core import AutomationSession
from pyui_automation.locators import ByName, ByClassName

session = AutomationSession(backend)

# Поиск главного окна
main_window = session.find_element(ByName("Notepad++"))

# Поиск текстового редактора
editor = session.find_element(ByClassName("Scintilla"))

# Поиск меню
menu_bar = session.find_element(ByClassName("QMenuBar"))
```

### Поиск элементов в игровом интерфейсе
```python
# Поиск панели здоровья
health_panel = session.find_element(ByName("HealthPanel"))

# Поиск всех слотов инвентаря
inventory_slots = session.find_elements(ByClassName("InventorySlot"))

# Поиск кнопки атаки
attack_button = session.find_element(ByName("AttackButton"))
```

### Комбинированный поиск
```python
# Поиск кнопки в определенной панели
settings_panel = session.find_element(ByName("SettingsPanel"))
save_button = settings_panel.find_element(ByName("SaveButton"))

# Поиск по нескольким критериям
def find_submit_button():
    # Попытка 1: по имени
    try:
        return session.find_element(ByName("submitButton"))
    except:
        pass
    
    # Попытка 2: по классу и тексту
    buttons = session.find_elements(ByClassName("QPushButton"))
    for button in buttons:
        if button.get_text() == "Submit":
            return button
    
    raise Exception("Submit button not found")
```

## Отладка локаторов

### Логирование
```python
import logging

# Включение подробного логирования
logging.getLogger("pyui_automation.locators").setLevel(logging.DEBUG)
```

### Валидация локаторов
```python
# Проверка существования элемента
try:
    element = session.find_element(ByName("nonExistentElement"))
except Exception as e:
    print(f"Element not found: {e}")
```

### Визуальная отладка
```python
# Снятие скриншота для анализа
screenshot = session.backend.capture_screenshot()
session.utils.save_image(screenshot, "debug_screenshot.png")
```

## Интеграция с тестированием

### Pytest фикстуры
```python
import pytest
from pyui_automation.core import AutomationSession

@pytest.fixture
def session():
    backend = BackendFactory.create_backend('windows')
    session = AutomationSession(backend)
    yield session
    session.terminate()

def test_button_click(session):
    button = session.find_element(ByName("testButton"))
    button.click()
    assert button.is_enabled()
```

### Page Object Model
```python
class LoginPage:
    def __init__(self, session):
        self.session = session
    
    @property
    def username_field(self):
        return self.session.find_element(ByName("username"))
    
    @property
    def password_field(self):
        return self.session.find_element(ByName("password"))
    
    @property
    def login_button(self):
        return self.session.find_element(ByName("loginButton"))
    
    def login(self, username: str, password: str):
        self.username_field.type_text(username)
        self.password_field.type_text(password)
        self.login_button.click()
``` 