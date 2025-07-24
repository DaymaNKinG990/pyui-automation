# Visual Testing Guide

Этот гайд описывает возможности визуального тестирования в PyUI Automation, включая baseline тестирование, сравнение изображений и генерацию отчетов.

## Основы визуального тестирования

Визуальное тестирование позволяет:
- Сравнивать текущий вид UI с эталонными изображениями
- Обнаруживать визуальные регрессии
- Автоматизировать проверку UI изменений
- Генерировать отчеты о различиях

## Инициализация визуального тестирования

### Базовая настройка
```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory

backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Инициализация визуального тестирования
session.init_visual_testing("visual_baseline/")
```

### Настройка с параметрами
```python
# Настройка с дополнительными параметрами
session.init_visual_testing(
    baseline_dir="visual_baseline/",
    threshold=0.95,  # Порог схожести (0.0 - 1.0)
    ignore_regions=[],  # Области для игнорирования
    output_dir="reports/"  # Папка для отчетов
)
```

## Создание baseline изображений

### Создание baseline для всего экрана
```python
# Создание baseline для главного окна
session.capture_visual_baseline("main_window")

# Создание baseline для конкретного элемента
button = session.find_element(ByName("submitButton"))
session.capture_visual_baseline("submit_button", element=button)
```

### Создание baseline для нескольких состояний
```python
# Baseline для разных состояний приложения
session.capture_visual_baseline("login_page")
session.capture_visual_baseline("dashboard_page")
session.capture_visual_baseline("settings_page")

# Baseline для разных разрешений
session.capture_visual_baseline("main_window_1920x1080")
session.capture_visual_baseline("main_window_1366x768")
```

### Создание baseline для игровых элементов
```python
# Baseline для игровых UI элементов
session.capture_visual_baseline("health_bar_full")
session.capture_visual_baseline("health_bar_low")
session.capture_visual_baseline("inventory_empty")
session.capture_visual_baseline("inventory_full")
```

## Сравнение с baseline

### Базовое сравнение
```python
# Сравнение текущего состояния с baseline
result = session.compare_visual("main_window")

if result["match"]:
    print("Visual test passed!")
else:
    print(f"Visual test failed! Similarity: {result['similarity']}")
    print(f"Differences found: {len(result['differences'])}")
```

### Сравнение с порогом схожести
```python
# Сравнение с кастомным порогом
result = session.compare_visual("main_window", threshold=0.98)

if result["similarity"] >= 0.98:
    print("High similarity - test passed")
else:
    print(f"Low similarity - test failed: {result['similarity']}")
```

### Сравнение конкретного элемента
```python
# Сравнение конкретного элемента
button = session.find_element(ByName("submitButton"))
result = session.compare_visual("submit_button", element=button)

if not result["match"]:
    print("Button appearance changed!")
```

## Обработка результатов сравнения

### Анализ различий
```python
result = session.compare_visual("main_window")

if not result["match"]:
    print(f"Similarity: {result['similarity']}")
    print(f"Total differences: {len(result['differences'])}")
    
    for i, diff in enumerate(result['differences']):
        print(f"Difference {i+1}:")
        print(f"  Position: {diff['position']}")
        print(f"  Size: {diff['size']}")
        print(f"  Type: {diff['type']}")
```

### Генерация отчетов
```python
# Генерация отчета о различиях
if not result["match"]:
    session.generate_visual_report(
        "main_window",
        result["differences"],
        "reports/visual_differences/"
    )
```

### Автоматическое принятие изменений
```python
# Автоматическое обновление baseline при небольших различиях
if result["similarity"] > 0.95:
    session.capture_visual_baseline("main_window")  # Обновляем baseline
    print("Baseline updated automatically")
```

## Продвинутые техники

### Игнорирование областей
```python
# Игнорирование динамических областей
ignore_regions = [
    {"x": 100, "y": 200, "width": 50, "height": 30},  # Область с временем
    {"x": 500, "y": 100, "width": 100, "height": 20}   # Область с счетчиком
]

result = session.compare_visual(
    "main_window",
    ignore_regions=ignore_regions
)
```

### Сравнение с маской
```python
# Создание маски для сравнения
from pyui_automation.utils import create_mask

# Создание маски для игнорирования определенных областей
mask = create_mask(1920, 1080)
mask.add_rectangle(100, 200, 50, 30)  # Игнорируемая область

result = session.compare_visual("main_window", mask=mask)
```

### Сравнение с шаблоном
```python
# Поиск и сравнение с шаблоном
from pyui_automation.utils import find_template

# Поиск кнопки в изображении
template = session.utils.load_image("templates/button.png")
position = find_template(screenshot, template)

if position:
    print(f"Template found at: {position}")
else:
    print("Template not found")
```

## Интеграция с тестированием

### Pytest тесты
```python
import pytest
from pyui_automation.core import AutomationSession

@pytest.fixture
def visual_session():
    backend = BackendFactory.create_backend('windows')
    session = AutomationSession(backend)
    session.init_visual_testing("tests/visual_baseline/")
    yield session
    session.terminate()

def test_main_window_appearance(visual_session):
    # Тест внешнего вида главного окна
    result = visual_session.compare_visual("main_window")
    assert result["match"], f"Visual test failed: {result['similarity']}"

def test_button_states(visual_session):
    # Тест состояний кнопки
    button = visual_session.find_element(ByName("submitButton"))
    
    # Тест нормального состояния
    result = visual_session.compare_visual("submit_button_normal", element=button)
    assert result["match"]
    
    # Тест состояния при наведении
    button.hover()
    result = visual_session.compare_visual("submit_button_hover", element=button)
    assert result["match"]
```

### CI/CD интеграция
```python
# Скрипт для CI/CD
def run_visual_tests():
    session = AutomationSession(backend)
    session.init_visual_testing("baseline/")
    
    # Список тестов для выполнения
    visual_tests = [
        "main_window",
        "login_form",
        "dashboard",
        "settings_page"
    ]
    
    failed_tests = []
    
    for test_name in visual_tests:
        try:
            result = session.compare_visual(test_name)
            if not result["match"]:
                failed_tests.append({
                    "test": test_name,
                    "similarity": result["similarity"],
                    "differences": len(result["differences"])
                })
        except Exception as e:
            failed_tests.append({
                "test": test_name,
                "error": str(e)
            })
    
    # Генерация отчета
    if failed_tests:
        generate_failure_report(failed_tests, "reports/visual_failures.html")
        return False
    
    return True
```

## Работа с изображениями

### Утилиты для работы с изображениями
```python
from pyui_automation.utils import (
    load_image, save_image, resize_image, 
    compare_images, highlight_region, crop_image
)

# Загрузка изображения
image = load_image("screenshot.png")

# Изменение размера
resized = resize_image(image, width=800, height=600)

# Сохранение
save_image(resized, "resized_screenshot.png")

# Сравнение двух изображений
similarity = compare_images(image1, image2)

# Выделение области
highlighted = highlight_region(image, x=100, y=200, width=50, height=30)

# Обрезка изображения
cropped = crop_image(image, x=100, y=200, width=300, height=200)
```

### Предобработка изображений
```python
# Предобработка для улучшения сравнения
from pyui_automation.utils import preprocess_image

# Нормализация яркости
normalized = preprocess_image(image, normalize_brightness=True)

# Удаление шума
denoised = preprocess_image(image, denoise=True)

# Улучшение контраста
enhanced = preprocess_image(image, enhance_contrast=True)
```

## Мониторинг производительности визуального тестирования

### Измерение времени выполнения
```python
import time

# Измерение времени создания baseline
start_time = time.time()
session.capture_visual_baseline("main_window")
baseline_time = time.time() - start_time
print(f"Baseline creation time: {baseline_time:.2f}s")

# Измерение времени сравнения
start_time = time.time()
result = session.compare_visual("main_window")
compare_time = time.time() - start_time
print(f"Comparison time: {compare_time:.2f}s")
```

### Оптимизация производительности
```python
# Оптимизация для больших изображений
session.init_visual_testing(
    baseline_dir="baseline/",
    resize_threshold=1920,  # Автоматическое уменьшение больших изображений
    compression_quality=85   # Качество сжатия
)
```

## Отладка визуального тестирования

### Логирование
```python
import logging

# Включение подробного логирования
logging.getLogger("pyui_automation.visual").setLevel(logging.DEBUG)
```

### Сохранение отладочной информации
```python
# Сохранение скриншотов для отладки
if not result["match"]:
    # Сохранение текущего скриншота
    session.utils.save_image(
        session.backend.capture_screenshot(),
        f"debug/current_{test_name}.png"
    )
    
    # Сохранение baseline для сравнения
    baseline_path = f"baseline/{test_name}.png"
    if os.path.exists(baseline_path):
        session.utils.save_image(
            session.utils.load_image(baseline_path),
            f"debug/baseline_{test_name}.png"
        )
```

### Визуальная отладка
```python
# Создание изображения с выделенными различиями
if not result["match"]:
    diff_image = session.utils.create_difference_image(
        current_screenshot,
        baseline_image,
        result["differences"]
    )
    session.utils.save_image(diff_image, f"debug/diff_{test_name}.png")
```

## Best Practices

### Организация baseline
- Храните baseline изображения в отдельной папке
- Используйте понятные имена для baseline
- Группируйте baseline по функциональности
- Версионируйте baseline вместе с кодом

### Надежность тестов
- Используйте стабильные элементы для baseline
- Игнорируйте динамические области (время, счетчики)
- Устанавливайте разумные пороги схожести
- Добавляйте retry логику для нестабильных тестов

### Производительность
- Оптимизируйте размер изображений
- Используйте кэширование для часто используемых baseline
- Параллелизуйте визуальные тесты
- Мониторьте время выполнения тестов

### Поддержка
- Регулярно обновляйте baseline
- Документируйте изменения в baseline
- Автоматизируйте процесс обновления baseline
- Создавайте fallback стратегии для критических тестов 