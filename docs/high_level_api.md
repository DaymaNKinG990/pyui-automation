# High-Level API Guide

## 🚀 **Обзор высокоуровневого API**

`PyUIAutomation` - это упрощенный интерфейс для QA Automation инженеров, который скрывает сложность фреймворка и предоставляет простые методы для автоматизации.

## 📦 **Основные компоненты**

### **PyUIAutomation** - главный класс
### **SimplePage** - упрощенные Page Objects
### **TestHelper** - вспомогательные методы для тестов
### **app_session** - context manager для автоматического управления сессией

## 🛠️ **Установка и импорт**

```python
from pyui_automation import PyUIAutomation, SimplePage, TestHelper, app_session
```

## 🚀 **Быстрый старт**

### **Простое использование**
```python
# Создание и запуск приложения
app = PyUIAutomation("notepad++.exe", "Notepad++")

# Базовые действия
app.click("loginButton")
app.type_text("username", "admin")
app.type_text("password", "123456")
app.click("submitButton")

# Закрытие приложения
app.close()
```

### **Использование с context manager**
```python
# Автоматическое закрытие приложения
with app_session("notepad++.exe", "Notepad++") as app:
    app.click("loginButton")
    app.type_text("username", "admin")
    app.type_text("password", "123456")
    app.click("submitButton")
```

## 🎯 **Основные методы PyUIAutomation**

### **Инициализация и запуск**
```python
# Создание без запуска
app = PyUIAutomation()

# Создание с запуском
app = PyUIAutomation("app.exe", "App Window")

# Запуск позже
app.launch("app.exe", "App Window")

# Указание платформы
app = PyUIAutomation("app.exe", platform="windows")
```

### **Поиск и взаимодействие с элементами**
```python
# Клики
app.click("buttonName")
app.double_click("buttonName")
app.right_click("buttonName")

# Ввод текста
app.type_text("inputField", "Hello World")

# Получение текста
text = app.get_text("elementName")

# Проверка состояния
is_visible = app.is_visible("elementName")
is_enabled = app.is_enabled("elementName")
```

### **Ожидание элементов**
```python
# Ожидание появления элемента
element = app.wait_for_element("elementName", timeout=10.0)

# Ожидание текста в элементе
app.wait_for_text("elementName", "Expected Text", timeout=10.0)
```

### **Поиск элементов**
```python
# Поиск по классу
elements = app.find_elements_by_class("QPushButton")

# Поиск по тексту
element = app.find_element_by_text("Button Text")
```

## 📸 **Визуальное тестирование**

```python
# Создание скриншота
app.capture_screenshot("test_step")

# Создание baseline
app.capture_baseline("main_window")

# Сравнение с baseline
app.assert_visual_match("main_window", threshold=0.95)
```

## 🔤 **OCR (распознавание текста)**

```python
# Настройка языков
app.ocr_set_languages(['en', 'ru'])

# Чтение текста из элемента
text = app.get_ocr_text("elementName")

# Распознавание текста из изображения
text = app.ocr_recognize_text("image.png")
```

## 📊 **Мониторинг производительности**

```python
# Запуск мониторинга
app.start_performance_monitoring(interval=1.0)

# Выполнение действий
for i in range(10):
    app.click(f"button_{i}")

# Остановка и получение метрик
metrics = app.stop_performance_monitoring()
print(f"CPU: {metrics['avg_cpu_usage']:.2f}%")
print(f"Memory: {metrics['avg_memory_usage']:.2f} MB")

# Измерение производительности действия
def test_action():
    app.click("button")
    app.type_text("input", "test")

performance = app.measure_action_performance(test_action, runs=3)
print(f"Average time: {performance['avg_time']:.3f}s")

# Стресс-тестирование
stress_result = app.run_stress_test(test_action, duration=60.0)

# Проверка утечек памяти
leak_result = app.check_memory_leaks(test_action, iterations=100)
```

## ♿ **Accessibility проверки**

```python
# Проверка accessibility
violations = app.check_accessibility()

if violations:
    print(f"Found {len(violations)} violations:")
    for violation in violations:
        print(f"- {violation['type']}: {violation['description']}")

# Генерация отчета
app.generate_accessibility_report("reports/accessibility.html")
```

## ⌨️ **Клавиатура и мышь**

### **Клавиатура**
```python
# Ввод текста
app.keyboard_type("Hello World", interval=0.1)

# Нажатие клавиш
app.keyboard_press_key("ctrl")
app.keyboard_release_key("ctrl")

# Комбинации клавиш
app.keyboard_send_keys("ctrl", "c")  # Copy
app.keyboard_send_keys("ctrl", "v")  # Paste
```

### **Мышь**
```python
# Перемещение мыши
app.mouse_move(100, 200)

# Клики
app.mouse_click(100, 200, button="left")
app.mouse_double_click(100, 200, button="left")
app.mouse_right_click(100, 200)

# Перетаскивание
app.mouse_drag(100, 200, 300, 400, button="left")

# Получение позиции
x, y = app.get_mouse_position()
```

## 🪟 **Управление окнами**

```python
# Получение размера экрана
width, height = app.get_screen_size()

# Получение handle окна
handle = app.get_window_handle("Window Title")

# Управление окном
app.focus_window("Window Title")
app.minimize_window("Window Title")
app.maximize_window("Window Title")
app.close_window("Window Title")
```

## 📄 **SimplePage - упрощенные Page Objects**

```python
# Создание страницы
page = SimplePage(app)

# Логин
page.login("admin", "123456")

# Логаут
page.logout()

# Навигация
page.navigate_to("Settings")

# Заполнение формы
form_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890"
}
page.fill_form(form_data)
page.submit_form("submitButton")
```

## 🧪 **TestHelper - вспомогательные методы**

```python
# Создание помощника
helper = TestHelper(app)

# Логирование шагов с скриншотами
helper.log_step("Login to application")
helper.log_step("Navigate to settings")

# Assertions
helper.assert_text_equals("title", "Expected Title")
helper.assert_text_contains("content", "Expected Text")
helper.assert_visible("button")
helper.assert_enabled("input")

# Ожидание и проверка
helper.wait_and_assert("result", "Success", timeout=10.0)
```

## 🔗 **Method Chaining (цепочка методов)**

```python
# Все методы возвращают self для цепочки
app.click("button1").click("button2").type_text("input", "text")
```

## 🎯 **Примеры использования**

### **Тест логина**
```python
def test_login():
    with app_session("app.exe", "Login Window") as app:
        app.type_text("username", "admin")
        app.type_text("password", "123456")
        app.click("loginButton")
        
        # Проверка успешного логина
        assert app.is_visible("dashboard")
        assert app.get_text("welcome") == "Welcome, admin!"
```

### **Тест с производительностью**
```python
def test_performance():
    app = PyUIAutomation("app.exe")
    
    # Запуск мониторинга
    app.start_performance_monitoring()
    
    # Выполнение действий
    for i in range(100):
        app.click("button")
        app.type_text("input", f"test_{i}")
    
    # Анализ результатов
    metrics = app.stop_performance_monitoring()
    
    # Проверка производительности
    assert metrics['avg_cpu_usage'] < 50.0
    assert metrics['avg_memory_usage'] < 100.0
    
    app.close()
```

### **Тест с визуальным сравнением**
```python
def test_visual():
    with app_session("app.exe") as app:
        # Создание baseline
        app.capture_baseline("main_screen")
        
        # Выполнение действий
        app.click("settings")
        
        # Сравнение с baseline
        app.assert_visual_match("main_screen")
```

### **Тест с OCR**
```python
def test_ocr():
    app = PyUIAutomation("app.exe")
    
    # Настройка OCR
    app.ocr_set_languages(['en', 'ru'])
    
    # Распознавание текста
    text = app.get_ocr_text("imageElement")
    assert "Expected Text" in text
    
    app.close()
```

## 🚨 **Важные замечания**

1. **Windows**: Для UI Automation требуется запуск с правами администратора
2. **Платформы**: Поддерживаются Windows, Linux, macOS
3. **Автоматическое закрытие**: Используйте context manager для автоматического закрытия приложений
4. **Таймауты**: Все методы поиска элементов имеют таймауты по умолчанию
5. **Обработка ошибок**: Методы автоматически обрабатывают ошибки и предоставляют понятные сообщения

## 🎯 **Best Practices**

1. **Используйте context manager** для автоматического управления ресурсами
2. **Указывайте таймауты** для стабильности тестов
3. **Логируйте шаги** с помощью TestHelper
4. **Мониторьте производительность** для долгих сценариев
5. **Создавайте baseline** для визуального тестирования
6. **Проверяйте accessibility** для соответствия стандартам
7. **Используйте method chaining** для читаемости кода

## 📚 **Следующие шаги**

1. Изучите [Core Concepts](./core_concepts.md) для понимания архитектуры
2. Ознакомьтесь с [API Reference](./api_reference.md) для детального описания методов
3. Посмотрите [Examples](./examples.md) для практических примеров
4. Изучите [Testing Guide](./testing_guide.md) для интеграции с тестовыми фреймворками 