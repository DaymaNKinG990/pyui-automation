# Utils Guide - Утилиты фреймворка

## 📦 **Обзор утилит**

Модуль `@/utils` предоставляет набор полезных функций для работы с изображениями, файлами, валидацией и метриками. Все утилиты доступны как напрямую, так и через `session.utils`.

## 🖼️ **Image Utils - Работа с изображениями**

### **Загрузка и сохранение**
```python
from pyui_automation.utils import load_image, save_image

# Загрузка изображения
image = load_image("screenshot.png")
if image is not None:
    print(f"Image loaded: {image.shape}")

# Сохранение изображения
success = save_image(image, "output.png")
print(f"Image saved: {success}")
```

### **Изменение размера**
```python
from pyui_automation.utils import resize_image

# Изменение размера с сохранением пропорций
resized = resize_image(image, width=800)  # По ширине
resized = resize_image(image, height=600)  # По высоте
resized = resize_image(image, width=800, height=600)  # Точный размер
```

### **Сравнение изображений**
```python
from pyui_automation.utils import compare_images

# Сравнение с порогом схожести
is_similar = compare_images(img1, img2, threshold=0.95)
print(f"Images are similar: {is_similar}")
```

### **Поиск шаблона**
```python
from pyui_automation.utils import find_template

# Поиск шаблона в изображении
template = load_image("button_template.png")
matches = find_template(screenshot, template, threshold=0.8)

for x, y, confidence in matches:
    print(f"Found at ({x}, {y}) with confidence {confidence:.2f}")
```

### **Выделение областей**
```python
from pyui_automation.utils import highlight_region, crop_image

# Выделение области прямоугольником
highlighted = highlight_region(image, x=100, y=100, width=200, height=100, 
                             color=(0, 255, 0), thickness=3)

# Обрезка области
cropped = crop_image(image, x=100, y=100, width=200, height=100)
```

### **Предобработка изображений**
```python
from pyui_automation.utils import preprocess_image, enhance_image, create_mask

# Базовая предобработка (шумоподавление + контраст)
processed = preprocess_image(image)

# Улучшение контраста
enhanced = enhance_image(image, method="contrast")

# Улучшение яркости
brightened = enhance_image(image, method="brightness")

# Улучшение резкости
sharpened = enhance_image(image, method="sharpness")

# Создание цветовой маски
mask = create_mask(image, lower=(0, 100, 100), upper=(10, 255, 255))  # Красный цвет
```

## 📁 **File Utils - Работа с файлами**

### **Создание директорий**
```python
from pyui_automation.utils import ensure_dir, get_temp_dir

# Создание директории
path = ensure_dir("reports/screenshots")
print(f"Directory created: {path}")

# Получение временной директории
temp_dir = get_temp_dir()
print(f"Temp directory: {temp_dir}")
```

### **Безопасное удаление**
```python
from pyui_automation.utils import safe_remove

# Безопасное удаление файла
success = safe_remove("old_file.txt")
print(f"File removed: {success}")

# Безопасное удаление директории
success = safe_remove("old_directory")
print(f"Directory removed: {success}")
```

### **Временные файлы**
```python
from pyui_automation.utils import get_temp_path

# Создание временного файла
temp_file = get_temp_path(".png")
print(f"Temp file: {temp_file}")
```

## ✅ **Validation Utils - Валидация данных**

### **Проверка типов**
```python
from pyui_automation.utils import validate_type, validate_not_none, validate_string_not_empty

# Проверка типа
is_valid = validate_type(value, str)
is_valid = validate_type(value, (int, float))

# Проверка на None
is_valid = validate_not_none(value)

# Проверка строки
is_valid = validate_string_not_empty("hello")  # True
is_valid = validate_string_not_empty("")       # False
is_valid = validate_string_not_empty(None)     # False
```

### **Проверка диапазонов**
```python
from pyui_automation.utils import validate_number_range

# Проверка диапазона
is_valid = validate_number_range(5, min_value=0, max_value=10)  # True
is_valid = validate_number_range(15, min_value=0, max_value=10) # False
is_valid = validate_number_range(5, min_value=0)                # True (только минимум)
```

## 📊 **Metrics Utils - Сбор метрик**

### **Сборщик метрик**
```python
from pyui_automation.utils import MetricsCollector, MetricPoint

# Создание сборщика
collector = MetricsCollector()

# Запись значений
collector.record_value("response_time", 0.5)
collector.record_value("memory_usage", 1024)

# Измерение времени
collector.start_timer("operation")
# ... выполнение операции ...
duration = collector.stop_timer("operation")

# Получение статистики
stats = collector.get_stats("response_time")
print(f"Min: {stats['min']}, Max: {stats['max']}, Avg: {stats['avg']}")
```

### **Глобальный сборщик**
```python
from pyui_automation.utils import metrics

# Использование глобального сборщика
metrics.record_value("global_metric", 42)
metrics.start_timer("global_operation")
# ... операция ...
duration = metrics.stop_timer("global_operation")
```

## 🔄 **Retry Utils - Повторные попытки**

### **Декоратор retry**
```python
from pyui_automation.utils import retry

@retry(attempts=3, delay=1.0, exceptions=(ConnectionError,))
def unreliable_function():
    # Функция, которая может упасть
    import random
    if random.random() < 0.7:
        raise ConnectionError("Connection failed")
    return "Success"

# Автоматические повторные попытки
result = unreliable_function()
```

## 🎯 **Использование через session.utils**

### **Доступ к утилитам через сессию**
```python
from pyui_automation import AutomationSession

session = AutomationSession(backend)

# Работа с изображениями
image = session.utils.load_image("screenshot.png")
session.utils.save_image(image, "output.png")
resized = session.utils.resize_image(image, width=800)

# Валидация
is_valid = session.utils.validate_type(value, str)
is_valid = session.utils.validate_number_range(value, 0, 100)

# Файловые операции
temp_dir = session.utils.get_temp_dir()
session.utils.ensure_dir("reports")
```

### **Создание разностного изображения**
```python
# Создание разностного изображения
diff_image = session.utils.create_difference_image(img1, img2)
session.utils.save_image(diff_image, "difference.png")
```

## 🧪 **Примеры использования в тестах**

### **Визуальное тестирование**
```python
def test_visual_comparison():
    # Захват скриншота
    screenshot = session.capture_screenshot()
    
    # Загрузка базового изображения
    baseline = session.utils.load_image("baseline.png")
    
    # Сравнение
    is_similar = session.utils.compare_images(screenshot, baseline, threshold=0.95)
    assert is_similar, "Visual regression detected"
    
    # Сохранение для отладки
    if not is_similar:
        session.utils.save_image(screenshot, "failed_test.png")
```

### **Поиск элементов по шаблону**
```python
def test_find_button():
    # Захват экрана
    screenshot = session.capture_screenshot()
    
    # Загрузка шаблона кнопки
    button_template = session.utils.load_image("templates/button.png")
    
    # Поиск кнопки
    matches = session.utils.find_template(screenshot, button_template, threshold=0.8)
    
    assert len(matches) > 0, "Button not found"
    
    # Клик по найденной кнопке
    x, y, confidence = matches[0]
    session.mouse_click(x, y)
```

### **Сбор метрик производительности**
```python
def test_performance():
    collector = session.utils.create_metrics_collector()
    
    for i in range(10):
        collector.start_timer("operation")
        # Выполнение операции
        session.click("button")
        duration = collector.stop_timer("operation")
        collector.record_value("response_time", duration)
    
    # Анализ результатов
    stats = collector.get_stats("response_time")
    assert stats['avg'] < 1.0, f"Average response time too high: {stats['avg']}"
```

## 🔧 **Лучшие практики**

### **1. Обработка ошибок**
```python
# Всегда проверяйте результат загрузки изображения
image = session.utils.load_image("file.png")
if image is None:
    raise FileNotFoundError("Failed to load image")

# Проверяйте результат сохранения
if not session.utils.save_image(image, "output.png"):
    raise IOError("Failed to save image")
```

### **2. Валидация входных данных**
```python
# Валидируйте параметры перед использованием
if not session.utils.validate_number_range(threshold, 0.0, 1.0):
    raise ValueError("Threshold must be between 0 and 1")

if not session.utils.validate_string_not_empty(filename):
    raise ValueError("Filename cannot be empty")
```

### **3. Использование временных файлов**
```python
# Используйте временные файлы для промежуточных результатов
temp_file = session.utils.get_temp_path(".png")
session.utils.save_image(image, temp_file)

try:
    # Обработка файла
    process_image(temp_file)
finally:
    # Очистка
    session.utils.safe_remove(temp_file)
```

### **4. Сбор метрик**
```python
# Собирайте метрики для анализа производительности
collector = session.utils.create_metrics_collector()

for test_case in test_cases:
    collector.start_timer("test_case")
    # Выполнение теста
    duration = collector.stop_timer("test_case")
    collector.record_value("test_duration", duration)

# Анализ результатов
stats = collector.get_stats("test_duration")
print(f"Average test duration: {stats['avg']:.2f}s")
```

## 📚 **Заключение**

Утилиты `@/utils` предоставляют мощный набор функций для работы с изображениями, файлами, валидацией и метриками. Они доступны как напрямую, так и через `session.utils`, что обеспечивает удобство использования в различных сценариях автоматизации.

Все утилиты следуют принципам SOLID и обеспечивают надежную работу с обработкой ошибок и валидацией входных данных. 