# Troubleshooting Guide

Этот гайд содержит решения для наиболее частых проблем, возникающих при использовании PyUI Automation.

## Общие проблемы

### Проблема: ElementNotFoundError - элемент не найден

**Симптомы:**
```
ElementNotFoundError: Element 'submitButton' not found using strategy ByName
```

**Возможные причины:**
1. Элемент еще не загружен
2. Неправильное имя элемента
3. Элемент скрыт или перекрыт
4. Платформо-зависимые различия

**Решения:**

```python
# 1. Ожидание появления элемента
from pyui_automation.core.wait import wait_for_element

try:
    element = wait_for_element(session, ByName("submitButton"), timeout=10.0)
except TimeoutError:
    print("Element did not appear within timeout")

# 2. Проверка доступных элементов
try:
    element = session.find_element(ByName("submitButton"))
except ElementNotFoundError as e:
    print(f"Available elements: {e.available_elements}")
    
    # Попытка найти по другим стратегиям
    try:
        element = session.find_element(ByClassName("QPushButton"))
    except ElementNotFoundError:
        try:
            element = session.find_element(ByText("Submit"))
        except ElementNotFoundError:
            raise

# 3. Проверка видимости элемента
element = session.find_element(ByName("submitButton"))
if not element.is_visible():
    print("Element is not visible")
    # Попытка прокрутки к элементу
    element.scroll_into_view()

# 4. Отладка с помощью скриншота
screenshot = session.backend.capture_screenshot()
session.utils.save_image(screenshot, "debug_screenshot.png")
print("Screenshot saved for debugging")
```

### Проблема: TimeoutError - превышение времени ожидания

**Симптомы:**
```
TimeoutError: Operation timed out after 10.0 seconds
```

**Возможные причины:**
1. Медленная загрузка приложения
2. Сетевые задержки
3. Недостаточно ресурсов системы
4. Неправильные таймауты

**Решения:**

```python
# 1. Увеличение таймаута
element = wait_for_element(session, ByName("slowElement"), timeout=30.0)

# 2. Проверка состояния системы
import psutil

cpu_percent = psutil.cpu_percent()
memory_percent = psutil.virtual_memory().percent

if cpu_percent > 90 or memory_percent > 90:
    print("System resources are low, increasing timeout")
    timeout = 60.0
else:
    timeout = 10.0

# 3. Адаптивные таймауты
def adaptive_wait(session, locator, base_timeout=10.0):
    """Адаптивное ожидание в зависимости от состояния системы"""
    system_load = psutil.cpu_percent() / 100.0
    adjusted_timeout = base_timeout * (1 + system_load)
    
    return wait_for_element(session, locator, timeout=adjusted_timeout)

# 4. Проверка готовности приложения
def wait_for_app_ready(session):
    """Ожидание готовности приложения"""
    indicators = [
        ByName("loadingIndicator"),
        ByClassName("LoadingSpinner"),
        ByText("Loading...")
    ]
    
    for indicator in indicators:
        try:
            element = session.find_element(indicator)
            if element.is_visible():
                wait_for_condition(
                    lambda: not element.is_visible(),
                    timeout=30.0
                )
        except ElementNotFoundError:
            continue
```

### Проблема: BackendError - ошибка backend

**Симптомы:**
```
BackendError: Failed to capture screenshot
BackendError: UI Automation not available
```

**Возможные причины:**
1. Недостаточно прав доступа
2. Неподдерживаемая платформа
3. Проблемы с драйверами
4. Конфликты с антивирусом

**Решения:**

```python
# 1. Проверка прав доступа (Windows)
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("WARNING: Running without admin privileges")
    print("Some features may not work properly")

# 2. Проверка поддержки платформы
import platform

current_platform = platform.system().lower()
supported_platforms = ['windows', 'linux', 'darwin']

if current_platform not in supported_platforms:
    raise PlatformNotSupportedError(f"Platform {current_platform} not supported")

# 3. Проверка доступности UI Automation (Windows)
def check_ui_automation():
    """Проверка доступности UI Automation"""
    try:
        import uiautomation as auto
        auto.GetRootControl()
        return True
    except Exception as e:
        print(f"UI Automation not available: {e}")
        return False

# 4. Переинициализация backend
try:
    screenshot = session.backend.capture_screenshot()
except BackendError:
    print("Reinitializing backend...")
    session.backend.reinitialize()
    screenshot = session.backend.capture_screenshot()
```

## Проблемы с OCR

### Проблема: Низкая точность распознавания

**Симптомы:**
```
OCRException: Low confidence (0.3) for text recognition
```

**Возможные причины:**
1. Плохое качество изображения
2. Неправильные языки
3. Сложный шрифт
4. Низкое разрешение

**Решения:**

```python
# 1. Предобработка изображения
def improve_ocr_accuracy(session, element):
    """Улучшение точности OCR"""
    # Попытка с предобработкой
    try:
        text = session.ocr.read_text_from_element(element, preprocess=True)
        if session.ocr.get_last_confidence() > 0.8:
            return text
    except OCRException:
        pass
    
    # Попытка с другим OCR engine
    original_engine = session.ocr.get_current_engine()
    for engine in ['paddle_ocr', 'tesseract', 'easy_ocr']:
        try:
            session.ocr.set_engine(engine)
            text = session.ocr.read_text_from_element(element)
            if session.ocr.get_last_confidence() > 0.7:
                return text
        except OCRException:
            continue
    
    # Восстановление оригинального engine
    session.ocr.set_engine(original_engine)
    raise OCRException("All OCR engines failed")

# 2. Настройка языков
def setup_optimal_languages(session):
    """Настройка оптимальных языков для OCR"""
    # Определение языка по контексту
    context_text = session.find_element(ByName("contextElement")).get_text()
    
    if any(char in context_text for char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"):
        languages = ['ru', 'en']
    elif any(char in context_text for char in "áéíóúñü"):
        languages = ['es', 'en']
    else:
        languages = ['en']
    
    session.ocr.set_languages(languages)

# 3. Улучшение качества изображения
def enhance_image_for_ocr(session, element):
    """Улучшение качества изображения для OCR"""
    from pyui_automation.utils import enhance_image
    
    # Снятие скриншота элемента
    screenshot = element.capture_screenshot()
    
    # Улучшение изображения
    enhanced = enhance_image(screenshot, {
        'contrast': 1.5,
        'brightness': 1.2,
        'denoise': True,
        'sharpen': True
    })
    
    # Распознавание с улучшенного изображения
    return session.ocr.recognize_text(enhanced)
```

### Проблема: OCR engine не найден

**Симптомы:**
```
OCRException: OCR engine 'paddle_ocr' not available
```

**Возможные причины:**
1. OCR engine не установлен
2. Проблемы с зависимостями
3. Неправильная конфигурация

**Решения:**

```python
# 1. Проверка доступности OCR engines
def check_ocr_engines():
    """Проверка доступности OCR engines"""
    available_engines = []
    
    engines_to_check = ['paddle_ocr', 'tesseract', 'easy_ocr']
    
    for engine in engines_to_check:
        try:
            session.ocr.set_engine(engine)
            available_engines.append(engine)
        except OCRException:
            continue
    
    if not available_engines:
        raise OCRException("No OCR engines available")
    
    print(f"Available OCR engines: {available_engines}")
    return available_engines

# 2. Автоматическая установка зависимостей
def install_ocr_dependencies():
    """Установка зависимостей для OCR"""
    import subprocess
    
    dependencies = [
        'paddlepaddle',
        'paddleocr',
        'pytesseract',
        'easyocr'
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
            print(f"Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {dep}")

# 3. Fallback на базовые методы
def fallback_text_extraction(session, element):
    """Fallback извлечение текста без OCR"""
    try:
        # Попытка получить текст через accessibility
        return element.get_text()
    except:
        try:
            # Попытка получить текст через свойства
            return element.get_property("text")
        except:
            # Последняя попытка - OCR с любым доступным engine
            available_engines = check_ocr_engines()
            for engine in available_engines:
                try:
                    session.ocr.set_engine(engine)
                    return session.ocr.read_text_from_element(element)
                except OCRException:
                    continue
            
            raise Exception("No text extraction method available")
```

## Проблемы с визуальным тестированием

### Проблема: Ложные срабатывания визуальных тестов

**Симптомы:**
```
Visual test failed despite no actual changes
```

**Возможные причины:**
1. Динамические элементы (время, счетчики)
2. Различия в разрешении
3. Антиалиасинг
4. Цветовые различия

**Решения:**

```python
# 1. Игнорирование динамических областей
def setup_visual_test_with_ignored_regions(session):
    """Настройка визуального теста с игнорированием областей"""
    ignore_regions = [
        # Область с временем
        {"x": 100, "y": 50, "width": 150, "height": 30},
        # Область со счетчиком
        {"x": 800, "y": 100, "width": 100, "height": 25},
        # Область со статусом
        {"x": 1200, "y": 200, "width": 80, "height": 20}
    ]
    
    session.init_visual_testing("baseline/", ignore_regions=ignore_regions)

# 2. Адаптивный порог схожести
def adaptive_visual_comparison(session, test_name):
    """Адаптивное сравнение с динамическим порогом"""
    # Первая попытка с высоким порогом
    result = session.compare_visual(test_name, threshold=0.95)
    
    if not result["match"]:
        # Вторая попытка с более низким порогом
        result = session.compare_visual(test_name, threshold=0.85)
        
        if not result["match"]:
            # Анализ различий
            print(f"Visual differences detected:")
            for diff in result["differences"]:
                print(f"  - {diff['type']} at {diff['position']}")
            
            # Автоматическое обновление baseline для небольших различий
            if result["similarity"] > 0.8:
                print("Updating baseline automatically")
                session.capture_visual_baseline(test_name)
                return True
    
    return result["match"]

# 3. Нормализация изображений
def normalize_image_for_comparison(session, image):
    """Нормализация изображения для сравнения"""
    from pyui_automation.utils import normalize_image
    
    # Нормализация размера
    normalized = normalize_image(image, target_size=(1920, 1080))
    
    # Нормализация яркости и контраста
    normalized = normalize_image(normalized, normalize_brightness=True)
    
    return normalized
```

### Проблема: Baseline изображения отсутствуют

**Симптомы:**
```
VisualTestError: Baseline image not found
```

**Возможные причины:**
1. Baseline не создан
2. Неправильный путь
3. Повреждение файлов
4. Проблемы с правами доступа

**Решения:**

```python
# 1. Автоматическое создание baseline
def ensure_baseline_exists(session, test_name):
    """Обеспечение существования baseline"""
    baseline_path = f"visual_baseline/{test_name}.png"
    
    if not os.path.exists(baseline_path):
        print(f"Creating baseline for {test_name}")
        session.capture_visual_baseline(test_name)
        return True
    
    return False

# 2. Валидация baseline
def validate_baseline(session, test_name):
    """Валидация baseline изображения"""
    baseline_path = f"visual_baseline/{test_name}.png"
    
    if not os.path.exists(baseline_path):
        raise VisualTestError(f"Baseline {test_name} not found")
    
    # Проверка целостности файла
    try:
        from PIL import Image
        with Image.open(baseline_path) as img:
            img.verify()
    except Exception as e:
        print(f"Baseline {test_name} is corrupted: {e}")
        # Пересоздание baseline
        session.capture_visual_baseline(test_name)

# 3. Резервное копирование baseline
def backup_baseline(test_name):
    """Резервное копирование baseline"""
    import shutil
    from datetime import datetime
    
    baseline_path = f"visual_baseline/{test_name}.png"
    backup_path = f"visual_baseline/backup/{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    if os.path.exists(baseline_path):
        os.makedirs("visual_baseline/backup", exist_ok=True)
        shutil.copy2(baseline_path, backup_path)
        print(f"Baseline backed up to {backup_path}")
```

## Проблемы с производительностью

### Проблема: Высокое потребление CPU/памяти

**Симптомы:**
```
PerformanceWarning: High CPU usage detected (95%)
PerformanceWarning: High memory usage detected (90%)
```

**Возможные причины:**
1. Неоптимизированные операции
2. Утечки памяти
3. Слишком частый мониторинг
4. Неэффективные алгоритмы

**Решения:**

```python
# 1. Оптимизация мониторинга производительности
def optimize_performance_monitoring(session):
    """Оптимизация мониторинга производительности"""
    # Увеличение интервала мониторинга
    session.start_performance_monitoring(interval=5.0)
    
    # Отключение детального мониторинга в продакшене
    if os.getenv('ENVIRONMENT') == 'production':
        session.performance_monitor.disable_detailed_monitoring()
    
    # Установка порогов предупреждений
    session.performance_monitor.set_thresholds(
        cpu_threshold=80.0,
        memory_threshold=85.0
    )

# 2. Кэширование результатов
class CachedElementFinder:
    """Кэшированный поиск элементов"""
    
    def __init__(self, session):
        self.session = session
        self.cache = {}
        self.cache_ttl = 60  # секунды
    
    def find_element(self, locator):
        """Поиск элемента с кэшированием"""
        cache_key = str(locator)
        
        if cache_key in self.cache:
            cached_time, cached_element = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_element
        
        element = self.session.find_element(locator)
        self.cache[cache_key] = (time.time(), element)
        return element

# 3. Оптимизация OCR
def optimize_ocr_usage(session):
    """Оптимизация использования OCR"""
    # Использование OCR только когда необходимо
    def smart_ocr_read(element):
        # Сначала попытка получить текст через accessibility
        try:
            return element.get_text()
        except:
            # Fallback на OCR
            return session.ocr.read_text_from_element(element)
    
    return smart_ocr_read

# 4. Очистка ресурсов
def cleanup_resources(session):
    """Очистка ресурсов"""
    # Остановка мониторинга
    session.stop_performance_monitoring()
    
    # Очистка кэша
    if hasattr(session, 'cache'):
        session.cache.clear()
    
    # Закрытие соединений
    session.backend.cleanup()
```

### Проблема: Утечки памяти

**Симптомы:**
```
MemoryLeakDetected: Memory usage increased by 50MB over 10 minutes
```

**Возможные причины:**
1. Неосвобожденные ресурсы
2. Циклические ссылки
3. Неправильное управление изображениями
4. Накопление данных в кэше

**Решения:**

```python
# 1. Автоматическое обнаружение утечек
def setup_memory_leak_detection(session):
    """Настройка обнаружения утечек памяти"""
    session.performance_monitor.enable_memory_leak_detection(
        threshold_mb=50,
        time_window_minutes=10
    )
    
    # Обработчик утечек
    def on_memory_leak_detected(report):
        print(f"Memory leak detected: {report['leak_size']} MB")
        print(f"Leak rate: {report['leak_rate']} MB/s")
        
        # Автоматическая очистка
        cleanup_resources(session)
    
    session.performance_monitor.set_leak_callback(on_memory_leak_detected)

# 2. Контекстный менеджер для ресурсов
from contextlib import contextmanager

@contextmanager
def managed_session():
    """Контекстный менеджер для сессии"""
    session = None
    try:
        backend = BackendFactory.create_backend('windows')
        session = AutomationSession(backend)
        yield session
    finally:
        if session:
            cleanup_resources(session)
            session.terminate()

# Использование
with managed_session() as session:
    # Выполнение операций
    element = session.find_element(ByName("testElement"))
    element.click()
```

## Проблемы с платформо-зависимостью

### Проблема: Различия между платформами

**Симптомы:**
```
ElementNotFoundError: Element not found on Linux (works on Windows)
```

**Возможные причины:**
1. Разные имена элементов
2. Разные API для автоматизации
3. Разные стили отображения
4. Разные разрешения

**Решения:**

```python
# 1. Платформо-зависимые локаторы
def get_platform_specific_locator(element_name):
    """Получение платформо-зависимого локатора"""
    import platform
    
    platform_name = platform.system().lower()
    
    platform_locators = {
        'windows': {
            'submitButton': ByName("submitButton"),
            'usernameField': ByName("usernameField")
        },
        'linux': {
            'submitButton': ByClassName("QPushButton"),
            'usernameField': ByClassName("QLineEdit")
        },
        'darwin': {
            'submitButton': ByAccessibilityId("submitButton"),
            'usernameField': ByAccessibilityId("usernameField")
        }
    }
    
    return platform_locators.get(platform_name, {}).get(element_name, ByName(element_name))

# 2. Адаптивные стратегии поиска
def adaptive_element_search(session, element_name):
    """Адаптивный поиск элементов"""
    strategies = [
        lambda: session.find_element(get_platform_specific_locator(element_name)),
        lambda: session.find_element(ByName(element_name)),
        lambda: session.find_element(ByClassName("QPushButton")),
        lambda: session.find_element(ByText(element_name))
    ]
    
    for strategy in strategies:
        try:
            return strategy()
        except ElementNotFoundError:
            continue
    
    raise ElementNotFoundError(f"Element {element_name} not found on any platform")

# 3. Платформо-зависимая конфигурация
def get_platform_config():
    """Получение платформо-зависимой конфигурации"""
    import platform
    
    platform_name = platform.system().lower()
    
    configs = {
        'windows': {
            'timeout': 10.0,
            'ocr_engine': 'paddle_ocr',
            'visual_threshold': 0.95
        },
        'linux': {
            'timeout': 15.0,
            'ocr_engine': 'tesseract',
            'visual_threshold': 0.90
        },
        'darwin': {
            'timeout': 12.0,
            'ocr_engine': 'easy_ocr',
            'visual_threshold': 0.92
        }
    }
    
    return configs.get(platform_name, configs['windows'])
```

## Диагностика и отладка

### Инструменты диагностики

```python
def diagnose_session(session):
    """Диагностика состояния сессии"""
    print("=== Session Diagnosis ===")
    
    # Проверка backend
    try:
        session.backend.validate_state()
        print("✓ Backend: OK")
    except Exception as e:
        print(f"✗ Backend: {e}")
    
    # Проверка OCR
    try:
        session.ocr.validate_state()
        print("✓ OCR: OK")
    except Exception as e:
        print(f"✗ OCR: {e}")
    
    # Проверка визуального тестирования
    try:
        session.visual.validate_state()
        print("✓ Visual Testing: OK")
    except Exception as e:
        print(f"✗ Visual Testing: {e}")
    
    # Проверка производительности
    try:
        metrics = session.get_performance_metrics()
        print(f"✓ Performance: CPU {metrics['cpu_usage']:.1f}%, Memory {metrics['memory_usage']:.1f}%")
    except Exception as e:
        print(f"✗ Performance: {e}")

# Использование
diagnose_session(session)
```

### Логирование для отладки

```python
import logging

def setup_debug_logging():
    """Настройка логирования для отладки"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pyui_debug.log'),
            logging.StreamHandler()
        ]
    )
    
    # Включение логирования для всех компонентов
    loggers = [
        'pyui_automation.core',
        'pyui_automation.backends',
        'pyui_automation.locators',
        'pyui_automation.ocr',
        'pyui_automation.visual'
    ]
    
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.DEBUG)

# Использование
setup_debug_logging()
```

## Best Practices для предотвращения проблем

### Общие рекомендации
1. **Всегда используйте try-catch блоки** для обработки исключений
2. **Устанавливайте разумные таймауты** для операций
3. **Используйте retry логику** для нестабильных операций
4. **Мониторьте производительность** в продакшене
5. **Версионируйте baseline изображения** вместе с кодом

### Специфичные рекомендации
1. **Запускайте Windows тесты с правами администратора**
2. **Используйте платформо-зависимые локаторы** для кроссплатформенности
3. **Настройте OCR engines** в зависимости от языка контента
4. **Игнорируйте динамические области** в визуальном тестировании
5. **Регулярно очищайте ресурсы** для предотвращения утечек памяти 