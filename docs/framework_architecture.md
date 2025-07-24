# Детальная архитектурная диаграмма PyUI Automation Framework

```mermaid
classDiagram


    %% Core модули
    class AutomationManager {
        -__sessions: Dict[str, AutomationSession]
        -__backend: BaseBackend
        -__config: Dict[str, Any]
        +create_session(backend_type): AutomationSession
        +get_session(session_id): AutomationSession
        +close_session(session_id): void
        +close_all_sessions(): void
        +get_screen_size(): Tuple[int, int]
        +set_config(key, value): void
        +get_config(key, default): Any
        +cleanup(): void
    }

    class AutomationSession {
        -__backend: BaseBackend
        -__locator: BaseLocator
        -__session_id: str
        -__waits: ElementWaits
        -__visual_tester: VisualTester
        -__performance_monitor: PerformanceTest
        -__config: AutomationConfig
        -__keyboard: Keyboard
        -__mouse: Mouse
        +backend: BaseBackend
        +locator: BaseLocator
        +session_id: str
        +waits: ElementWaits
        +visual_tester: VisualTester
        +keyboard: Keyboard
        +mouse: Mouse
        +ocr: OCREngine
        +find_element_by_object_name(name): BaseElement
        +find_element_by_text(text): BaseElement
        +find_element_by_widget_type(widget_type): BaseElement
        +take_screenshot(): np.ndarray
        +capture_baseline(name, element): bool
        +compare_visual(name, element): Dict[str, Any]
        +start_performance_monitoring(interval): void
        +get_performance_metrics(): Dict[str, Any]
        +cleanup(): void
    }

    class AutomationLogger {
        -__logger: Logger
        -__name: str
        +info(message): void
        +debug(message): void
        +warning(message): void
        +error(message): void
        +critical(message): void
        +add_file_handler(log_file): void
        +set_level(level): void
    }

    %% Backends
    class BaseBackend {
        <<abstract>>
        +find_element_by_object_name(name): BaseElement
        +find_element_by_text(text): BaseElement
        +find_element_by_widget_type(type): BaseElement
        +find_element_by_property(prop, value): BaseElement
        +capture_screenshot(): np.ndarray
        +get_window_handle(pid): object
        +get_active_window(): object
        +get_window_handles(): List[int]
    }

    class WindowsBackend {
        -__uia: UIAutomation
        +find_element_by_object_name(name): WindowsElement
        +find_element_by_text(text): WindowsElement
        +capture_screenshot(): np.ndarray
        +get_window_handle(pid): object
    }

    class LinuxBackend {
        -__atspi: ATSPI
        +find_element_by_object_name(name): LinuxElement
        +find_element_by_text(text): LinuxElement
        +capture_screenshot(): np.ndarray
        +get_window_handle(pid): object
    }

    class MacOSBackend {
        -__accessibility: AccessibilityAPI
        +find_element_by_object_name(name): MacOSElement
        +find_element_by_text(text): MacOSElement
        +capture_screenshot(): np.ndarray
        +get_window_handle(pid): object
    }



    %% Elements
    class BaseElement {
        -__element: Any
        -__session: AutomationSession
        +native_element: Any
        +session: AutomationSession
        +control_type: str
        +text: str
        +location: Dict[str, int]
        +size: Dict[str, int]
        +name: str
        +visible: bool
        +value: str
        +is_checked: bool
        +is_expanded: bool
        +selected_item: str
        +is_selected: bool
        +automation_id: str
        +class_name: str
        +get_attribute(name): str
        +get_property(name): Any
        +is_displayed(): bool
        +is_enabled(): bool
        +click(): void
        +double_click(): void
        +right_click(): void
        +hover(): void
        +send_keys(*keys): void
        +clear(): void
        +focus(): void
        +select_all(): void
        +copy(): void
        +paste(): void
        +is_pressed(): bool
        +wait_until_enabled(timeout): bool
        +wait_until_clickable(timeout): bool
        +safe_click(timeout): bool
        +check(): void
        +uncheck(): void
        +toggle(): void
        +expand(): void
        +collapse(): void
        +select_item(item_text): void
        +wait_until_checked(timeout): bool
        +wait_until_unchecked(timeout): bool
        +wait_until_expanded(timeout): bool
        +wait_until_collapsed(timeout): bool
        +wait_until_value_is(expected_value, timeout): bool
        +capture_screenshot(): np.ndarray
        +drag_and_drop(target): void
        +scroll_into_view(): void
        +wait_for_enabled(timeout): bool
        +wait_for_visible(timeout): bool
        +get_parent(): BaseElement
        +get_children(): List[BaseElement]
        +take_screenshot(): np.ndarray
        +get_attributes(): Dict[str, str]
        +get_properties(): Dict[str, Any]
        +rect: Dict[str, int]
        +center: Dict[str, int]
    }

    %% Input
    class Keyboard {
        -__backend: BaseBackend
        +type_text(text, interval): bool
        +press_key(key): bool
        +release_key(key): bool
        +press_keys(*keys): bool
        +release_keys(*keys): bool
        +send_keys(keys): bool
    }

    class Mouse {
        -__backend: BaseBackend
        +move(x, y): bool
        +click(x, y, button): bool
        +double_click(x, y, button): bool
        +right_click(x, y): bool
        +drag(start_x, start_y, end_x, end_y, button): bool
        +get_position(): Tuple[int, int]
    }



    %% Services
    class PerformanceMonitor {
        -__application: Application
        -__metrics: List[PerformanceMetric]
        -__is_monitoring: bool
        +start_monitoring(interval): void
        +stop_monitoring(): Dict[str, Any]
        +record_metric(response_time): void
        +get_average_metrics(): Dict[str, float]
        +get_metrics_history(): Dict[str, List[float]]
        +generate_report(output_path): void
        +plot_metrics(file_path): void
    }

    class PerformanceMetric {
        +timestamp: float
        +cpu_usage: float
        +memory_usage: float
        +response_time: float
    }

    class PerformanceTest {
        -__application: Application
        -__monitor: PerformanceMonitor
        +start_monitoring(interval): void
        +stop_monitoring(): List[PerformanceMetric]
        +measure_action(action, name, warmup_runs, test_runs): Dict[str, Union[str, float]]
        +stress_test(action, duration, interval): Dict[str, Union[float, bool]]
        +detect_regression(action, baseline_metrics, test_runs, threshold_std): Dict[str, Any]
    }

    class OCREngine {
        -__paddle_ocr: PaddleOCR
        -__languages: List[str]
        +set_languages(languages): void
        +recognize_text(image_path, preprocess): str
        +read_text_from_element(element, preprocess): str
        +find_text_location(element, text, confidence_threshold): List[Tuple[int, int, int, int]]
        +get_all_text(element, confidence_threshold): List[Dict[str, Any]]
        +verify_text_presence(element, text, confidence_threshold): bool
    }

    %% Visual Testing
    class VisualTester {
        -__baseline_dir: Path
        -__threshold: float
        -__baseline_cache: Dict[str, np.ndarray]
        +baseline_dir: Path
        +similarity_threshold: float
        +capture_baseline(name, image): bool
        +read_baseline(name): np.ndarray
        +compare_with_baseline(name, current): Tuple[bool, float]
        +compare(current, baseline, resize, roi): Dict[str, Any]
        +verify_hash(name, current): bool
        +calculate_phash(image, hash_size): np.ndarray
        +generate_report(differences, name, output_dir): void
        +find_element(template): Tuple[int, int]
        +find_all_elements(template, threshold): List[Dict[str, Any]]
        +generate_diff_report(img1, img2, output_path): void
        +verify_visual_state(baseline): Dict[str, Any]
    }

    %% Core Components
    class Application {
        -__path: Path
        -__process: psutil.Process
        -__platform: str
        -__backend: BaseBackend
        -__window_handle: int
        +path: Path
        +process: psutil.Process
        +platform: str
        +pid: int
        +launch(path, args, cwd, env): Application
        +attach(pid_or_name): Application
        +terminate(timeout): void
        +kill(): void
        +is_running(): bool
        +get_memory_usage(): float
        +get_cpu_usage(): float
        +get_child_processes(): List[psutil.Process]
        +wait_for_window(title, timeout): object
        +get_window(title): object
        +get_main_window(): object
        +get_window_handles(): List[int]
        +get_active_window(): object
    }

    class OptimizationManager {
        -__platform: str
        -__cache_dir: Path
        -__element_cache: Dict[str, Dict[str, Any]]
        -__cache_lock: threading.Lock
        -__optimizations: Dict[str, Any]
        +platform: str
        +cache_dir: Path
        +element_cache: Dict[str, Dict[str, Any]]
        +cache_element(element_id, element_data, ttl): void
        +get_cached_element(element_id): Dict[str, Any]
        +clear_cache(): void
        +save_cache(): void
        +get_optimization(key): Any
        +set_optimization(key, value): void
        +optimize_process(process_id): void
        +configure_platform_optimizations(**kwargs): void
        +platform_config: Dict[str, Any]
    }

    class AutomationLogger {
        -__logger: logging.Logger
        +add_file_handler(filepath): void
        +set_level(level): void
        +debug(msg): void
        +info(msg): void
        +warning(msg): void
        +error(msg): void
        +critical(msg): void
        +exception(msg): void
    }

    class ElementWaits {
        -__automation: AutomationSession
        +wait_until(condition, timeout, poll_frequency, error_message): bool
        +for_element_by_object_name(object_name, timeout): BaseElement
        +for_element_by_widget_type(widget_type, timeout): BaseElement
        +for_element_by_text(text, timeout): BaseElement
        +for_element_by_property(property_name, value, timeout): BaseElement
        +for_element_pattern(element, pattern_name, timeout): bool
    }


        +save_cache(): void
        +get_optimization(key): Any
        +set_optimization(key, value): void
        +optimize_process(process_id): void
        +configure_platform_optimizations(**kwargs): void
    }

    class MetricsCollector {
        -__metrics: Dict[str, List[MetricPoint]]
        -__timers: Dict[str, float]
        +record_value(name, value): void
        +start_timer(name): void
        +stop_timer(name): float
        +get_stats(name): Dict[str, float]
        +clear(): void
    }

    class MetricPoint {
        +value: float
        +timestamp: datetime
    }

    %% Utils Functions
    class CoreUtils {
        +retry(attempts, delay, exceptions): Callable
        +get_temp_path(): Path
    }

    class ImageUtils {
        +load_image(path): np.ndarray
        +save_image(image, path): bool
        +resize_image(image, width, height): np.ndarray
        +compare_images(img1, img2, threshold): bool
        +find_template(image, template, threshold): List[Tuple[int, int, float]]
        +highlight_region(image, x, y, width, height, color, thickness): np.ndarray
        +crop_image(image, x, y, width, height): np.ndarray
    }

    class FileUtils {
        +ensure_dir(path): Path
        +get_temp_dir(): Path
        +safe_remove(path): bool
    }

    class ValidationUtils {
        +validate_type(value, expected_type): bool
        +validate_not_none(value): bool
        +validate_string_not_empty(value): bool
        +validate_number_range(value, min_value, max_value): bool
    }

    %% Exceptions
    class AutomationError {
        +message: str
    }

    class ElementNotFoundError {
        +element_name: str
    }

    class ElementStateError {
        +element_name: str
        +expected_state: str
        +actual_state: str
    }

    class TimeoutError {
        +operation: str
        +timeout: float
    }

    class BackendError {
        +backend_type: str
        +operation: str
    }

    class OCRError {
        +operation: str
        +image_path: str
    }

    class VisualError {
        +operation: str
        +baseline_path: str
    }

    %% Связи
    AutomationManager --> AutomationSession : manages
    AutomationManager --> BaseBackend : creates

    BaseBackend <|-- WindowsBackend : extends
    BaseBackend <|-- LinuxBackend : extends
    BaseBackend <|-- MacOSBackend : extends

    AutomationSession --> BaseBackend : uses
    AutomationSession --> ElementWaits : has
    AutomationSession --> VisualTester : has
    AutomationSession --> PerformanceTest : has
    AutomationSession --> Keyboard : has
    AutomationSession --> Mouse : has
    AutomationSession --> OCREngine : has
    AutomationSession --> OptimizationManager : uses
    AutomationSession --> AutomationLogger : uses

    %% BaseElement is the only element class in the framework
    AutomationSession --> BaseElement : creates

    Application --> BaseBackend : uses

    PerformanceMonitor --> Application : monitors
    PerformanceMonitor --> PerformanceMetric : creates
    PerformanceTest --> PerformanceMonitor : uses

    OCREngine --> BaseElement : reads_text_from

    VisualTester --> BaseElement : compares

    ElementWaits --> AutomationSession : uses

    OptimizationManager --> Application : optimizes

    MetricsCollector --> MetricPoint : creates

    %% Exceptions
    AutomationError <|-- ElementNotFoundError : extends
    AutomationError <|-- ElementStateError : extends
    AutomationError <|-- TimeoutError : extends
    AutomationError <|-- BackendError : extends
    AutomationError <|-- OCRError : extends
    AutomationError <|-- VisualError : extends

    %% Поток выполнения автоматизации
    class AutomationFlow {
        +1. AutomationManager.create_session()
        +2. BackendFactory.create_backend()
        +3. Application.launch()
        +4. AutomationSession.find_element()
        +5. BaseElement.click()
        +6. PerformanceMonitor.record_metric()
        +7. AutomationSession.cleanup()
    }
```

## Детальное объяснение архитектуры

### Основные архитектурные слои:

1. **Core** - ядро фреймворка (менеджеры, сессии, приложения, логирование, оптимизация, ожидания)
2. **Backends** - платформо-зависимые реализации автоматизации
3. **Elements** - представление UI элементов
4. **Services** - сервисы (OCR, производительность)
5. **Input** - управление вводом (клавиатура, мышь)
6. **Utils** - вспомогательные утилиты

### Ключевые паттерны проектирования:

- **Factory** - BackendFactory создает платформо-зависимые backends
- **Manager** - AutomationManager, OptimizationManager
- **Session** - AutomationSession управляет жизненным циклом автоматизации
- **Logger** - AutomationLogger для централизованного логирования
- **Strategy** - различные backends для разных платформ
- **Observer** - PerformanceMonitor отслеживает метрики
- **Template Method** - BaseElement определяет общий интерфейс
- **Singleton** - AutomationManager для глобального доступа

### Структура UI элементов:

```
BaseElement (единственный класс элементов)
├── Универсальный интерфейс для всех платформ
├── Поддержка Windows UIA, Linux AT-SPI2, macOS Accessibility API
├── Встроенные методы для работы с UI
├── Автоматическое определение платформы
└── Единый API для всех типов элементов
```

### Поддерживаемые платформы:

1. **Windows** - UI Automation, WinForms, WPF, UWP
2. **Linux** - AT-SPI2, GTK, Qt, Tkinter
3. **macOS** - Accessibility API, Cocoa, Qt

### Система мониторинга:

**PerformanceMonitor** собирает метрики:
- CPU usage
- Memory usage
- Response time
- Custom metrics

**MetricsCollector** обеспечивает:
- Глобальный сбор метрик
- Таймеры для операций
- Статистический анализ
- Экспорт данных

### OCR и Visual Testing:

**OCREngine** поддерживает:
- Распознавание текста с PaddleOCR
- Многоязычность
- Предобработка изображений
- Поиск текста в элементах

**VisualTester** обеспечивает:
- Сравнение с baseline
- Template matching
- Поиск элементов по изображению
- Генерация отчетов о различиях

### Utils:

**Утилиты включают:**
- Core: retry, temp paths
- Image: загрузка, сохранение, сравнение
- File: безопасная работа с файлами
- Validation: валидация данных
- Metrics: сбор и анализ метрик

### Поток выполнения автоматизации:

```
1. Создание сессии автоматизации
2. Выбор backend для платформы
3. Запуск приложения
4. Поиск UI элементов
5. Выполнение действий
6. Сбор метрик производительности
7. Закрытие сессии
```

### Обработка ошибок:

Система исключений включает:
- **AutomationError** - базовое исключение
- **ElementNotFoundError** - элемент не найден
- **ElementStateError** - неверное состояние элемента
- **TimeoutError** - превышение времени ожидания
- **BackendError** - ошибки backend
- **OCRError** - ошибки OCR
- **VisualError** - ошибки визуального тестирования

Архитектура обеспечивает:

- **Кроссплатформенность** - единый API для всех платформ
- **Модульность** - четкое разделение ответственности
- **Расширяемость** - легко добавлять новые backends и элементы
- **Надежность** - retry механизмы и валидация
- **Мониторинг** - детальный сбор метрик
- **Удобство** - простой API для автоматизации
- **Производительность** - оптимизация и кэширование
- **Тестируемость** - визуальное тестирование и OCR 