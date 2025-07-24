# Configuration Guide

Этот гайд описывает все аспекты конфигурации PyUI Automation, включая настройки, переменные окружения и файлы конфигурации.

## Основы конфигурации

PyUI Automation поддерживает несколько уровней конфигурации:
- **Переменные окружения** - для системных настроек
- **Файлы конфигурации** - для проектных настроек
- **Программная конфигурация** - для динамических настроек
- **Dependency Injection конфигурация** - для настройки сервисов

## Переменные окружения

### Основные переменные
```bash
# Платформа (windows, linux, macos)
PYUI_PLATFORM=windows

# Уровень логирования (DEBUG, INFO, WARNING, ERROR)
PYUI_LOG_LEVEL=INFO

# Путь к файлу логов
PYUI_LOG_FILE=pyui_automation.log

# Таймауты (в секундах)
PYUI_DEFAULT_TIMEOUT=10
PYUI_ELEMENT_TIMEOUT=5
PYUI_WINDOW_TIMEOUT=15

# Настройки OCR
PYUI_OCR_ENGINE=paddle_ocr
PYUI_OCR_LANGUAGES=en,ru
PYUI_OCR_CONFIDENCE_THRESHOLD=0.8

# Настройки визуального тестирования
PYUI_VISUAL_THRESHOLD=0.95
PYUI_VISUAL_BASELINE_DIR=visual_baseline/
PYUI_VISUAL_REPORTS_DIR=reports/

# Настройки производительности
PYUI_PERFORMANCE_MONITORING=true
PYUI_PERFORMANCE_INTERVAL=1.0
PYUI_MEMORY_LEAK_DETECTION=true

# Настройки тестирования
PYUI_TEST_RETRY_COUNT=3
PYUI_TEST_RETRY_DELAY=1.0
PYUI_TEST_SCREENSHOT_ON_FAILURE=true
```

### Переменные для разработки
```bash
# Отладка
PYUI_DEBUG=true
PYUI_VERBOSE=true

# Тестовые настройки
PYUI_TEST_MODE=true
PYUI_MOCK_BACKEND=false

# CI/CD настройки
PYUI_CI_MODE=true
PYUI_HEADLESS=true
```

## Файлы конфигурации

### Основной файл конфигурации (pyui_config.yaml)
```yaml
# Основные настройки
platform: windows
log_level: INFO
log_file: logs/pyui_automation.log

# Таймауты
timeouts:
  default: 10
  element: 5
  window: 15
  visual: 30

# Настройки OCR
ocr:
  engine: paddle_ocr
  languages: [en, ru]
  confidence_threshold: 0.8
  preprocess: true
  denoise: false

# Настройки визуального тестирования
visual:
  threshold: 0.95
  baseline_dir: visual_baseline/
  reports_dir: reports/
  ignore_regions: []
  resize_threshold: 1920
  compression_quality: 85

# Настройки производительности
performance:
  monitoring: true
  interval: 1.0
  memory_leak_detection: true
  cpu_threshold: 80.0
  memory_threshold: 85.0

# Настройки тестирования
testing:
  retry_count: 3
  retry_delay: 1.0
  screenshot_on_failure: true
  video_recording: false
  parallel_execution: true

# Настройки backend
backend:
  windows:
    ui_automation: true
    accessibility: true
    screenshot_format: png
  linux:
    x11: true
    wayland: false
  macos:
    accessibility: true
    screen_capture: true

# Настройки локаторов
locators:
  default_strategy: ByName
  fallback_strategies: [ByClassName, ByText]
  custom_locators: {}

# Настройки DI контейнера
di:
  auto_discovery: true
  lazy_loading: true
  singleton_services: [BackendService, OCRService, PerformanceMonitor]
```

### Конфигурация для тестов (test_config.yaml)
```yaml
# Настройки для тестового окружения
platform: windows
log_level: DEBUG
test_mode: true

# Настройки тестов
testing:
  retry_count: 2
  retry_delay: 0.5
  screenshot_on_failure: true
  video_recording: false
  parallel_execution: false

# Настройки мокирования
mocking:
  backend: false
  ocr: false
  performance: false

# Настройки отчетов
reports:
  html: true
  json: true
  junit: true
  coverage: true
```

### Конфигурация для CI/CD (ci_config.yaml)
```yaml
# Настройки для CI/CD
platform: linux
log_level: INFO
ci_mode: true
headless: true

# Настройки тестов
testing:
  retry_count: 1
  retry_delay: 0.1
  screenshot_on_failure: true
  video_recording: false
  parallel_execution: true

# Настройки отчетов
reports:
  html: true
  json: true
  junit: true
  coverage: true
  artifacts_dir: artifacts/

# Настройки производительности
performance:
  monitoring: false
  memory_leak_detection: false
```

## Программная конфигурация

### Создание конфигурации программно
```python
from pyui_automation.core.config import Config

# Создание конфигурации
config = Config()

# Настройка основных параметров
config.platform = "windows"
config.log_level = "INFO"
config.default_timeout = 10

# Настройка OCR
config.ocr.engine = "paddle_ocr"
config.ocr.languages = ["en", "ru"]
config.ocr.confidence_threshold = 0.8

# Настройка визуального тестирования
config.visual.threshold = 0.95
config.visual.baseline_dir = "visual_baseline/"

# Настройка производительности
config.performance.monitoring = True
config.performance.interval = 1.0

# Применение конфигурации
session = AutomationSession(backend, config=config)
```

### Загрузка конфигурации из файла
```python
from pyui_automation.core.config import Config

# Загрузка из YAML файла
config = Config.from_file("pyui_config.yaml")

# Загрузка из JSON файла
config = Config.from_file("pyui_config.json")

# Загрузка с переопределением
config = Config.from_file("pyui_config.yaml", overrides={
    "platform": "linux",
    "log_level": "DEBUG"
})
```

### Создание конфигурации из словаря
```python
config_dict = {
    "platform": "windows",
    "log_level": "INFO",
    "timeouts": {
        "default": 10,
        "element": 5
    },
    "ocr": {
        "engine": "paddle_ocr",
        "languages": ["en", "ru"]
    }
}

config = Config.from_dict(config_dict)
```

## Dependency Injection конфигурация

### Настройка DI контейнера
```python
from pyui_automation.core.di_manager import DIAutomationManager

# Создание менеджера с конфигурацией
manager = DIAutomationManager()

# Регистрация сервисов с конфигурацией
manager.register_service(
    "BackendService",
    WindowsBackend,
    config={"ui_automation": True, "accessibility": True}
)

manager.register_service(
    "OCRService",
    UnifiedOCREngine,
    config={"engine": "paddle_ocr", "languages": ["en", "ru"]}
)

manager.register_service(
    "PerformanceMonitor",
    PerformanceMonitor,
    config={"interval": 1.0, "memory_leak_detection": True}
)
```

### Конфигурация через файл
```yaml
# di_config.yaml
services:
  BackendService:
    class: pyui_automation.backends.windows.WindowsBackend
    config:
      ui_automation: true
      accessibility: true
    singleton: true

  OCRService:
    class: pyui_automation.services.ocr.UnifiedOCREngine
    config:
      engine: paddle_ocr
      languages: [en, ru]
      confidence_threshold: 0.8
    singleton: true

  PerformanceMonitor:
    class: pyui_automation.core.services.performance_monitor.PerformanceMonitor
    config:
      interval: 1.0
      memory_leak_detection: true
    singleton: true

  LocatorFactory:
    class: pyui_automation.core.services.locator_factory.LocatorFactory
    singleton: true
```

```python
# Загрузка DI конфигурации
manager = DIAutomationManager.from_config("di_config.yaml")
```

## Конфигурация для разных сценариев

### Конфигурация для разработки
```python
dev_config = Config(
    platform="windows",
    log_level="DEBUG",
    debug=True,
    verbose=True,
    testing={
        "retry_count": 3,
        "screenshot_on_failure": True
    }
)
```

### Конфигурация для продакшена
```python
prod_config = Config(
    platform="linux",
    log_level="WARNING",
    debug=False,
    performance={
        "monitoring": True,
        "interval": 5.0
    },
    testing={
        "retry_count": 1,
        "screenshot_on_failure": False
    }
)
```

### Конфигурация для игровой автоматизации
```python
game_config = Config(
    platform="windows",
    log_level="INFO",
    visual={
        "threshold": 0.9,
        "baseline_dir": "game_baseline/"
    },
    ocr={
        "engine": "paddle_ocr",
        "languages": ["en"],
        "confidence_threshold": 0.7
    },
    performance={
        "monitoring": True,
        "interval": 0.5
    }
)
```

## Валидация конфигурации

### Проверка конфигурации
```python
from pyui_automation.core.config import ConfigValidator

# Создание валидатора
validator = ConfigValidator()

# Проверка конфигурации
config = Config.from_file("pyui_config.yaml")
errors = validator.validate(config)

if errors:
    print("Configuration errors:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Configuration is valid")
```

### Схема валидации
```python
# Схема для валидации конфигурации
config_schema = {
    "type": "object",
    "properties": {
        "platform": {
            "type": "string",
            "enum": ["windows", "linux", "macos"]
        },
        "log_level": {
            "type": "string",
            "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]
        },
        "timeouts": {
            "type": "object",
            "properties": {
                "default": {"type": "number", "minimum": 1},
                "element": {"type": "number", "minimum": 1}
            }
        }
    },
    "required": ["platform", "log_level"]
}
```

## Переопределение конфигурации

### Переопределение через переменные окружения
```python
# Конфигурация будет переопределена переменными окружения
config = Config.from_file("pyui_config.yaml")
config.apply_environment_overrides()
```

### Переопределение программно
```python
# Базовая конфигурация
config = Config.from_file("pyui_config.yaml")

# Переопределение для конкретного теста
test_config = config.override({
    "log_level": "DEBUG",
    "testing": {
        "retry_count": 1,
        "screenshot_on_failure": True
    }
})
```

### Переопределение через командную строку
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--platform", default="windows")
parser.add_argument("--log-level", default="INFO")
parser.add_argument("--config-file", default="pyui_config.yaml")

args = parser.parse_args()

config = Config.from_file(args.config_file)
config.platform = args.platform
config.log_level = args.log_level
```

## Мониторинг конфигурации

### Логирование конфигурации
```python
import logging

# Логирование загруженной конфигурации
logger = logging.getLogger("pyui_automation.config")
logger.info(f"Loaded configuration: {config.to_dict()}")
```

### Валидация во время выполнения
```python
# Проверка конфигурации во время выполнения
def validate_runtime_config(config):
    if config.platform == "windows" and not config.backend.windows.ui_automation:
        raise ValueError("UI Automation must be enabled for Windows platform")
    
    if config.visual.threshold < 0.5:
        raise ValueError("Visual threshold too low")
```

## Best Practices

### Организация конфигурации
- Используйте отдельные файлы для разных окружений
- Версионируйте конфигурационные файлы
- Документируйте все параметры конфигурации
- Используйте переменные окружения для секретных данных

### Безопасность
- Не храните секретные данные в конфигурационных файлах
- Используйте переменные окружения для паролей и ключей
- Валидируйте конфигурацию перед использованием
- Логируйте только нечувствительные данные

### Производительность
- Кэшируйте загруженную конфигурацию
- Используйте lazy loading для тяжелых компонентов
- Оптимизируйте конфигурацию для целевой платформы
- Мониторьте время загрузки конфигурации

### Поддержка
- Создавайте шаблоны конфигурации для новых проектов
- Автоматизируйте проверку конфигурации в CI/CD
- Создавайте fallback конфигурации
- Документируйте изменения в конфигурации 