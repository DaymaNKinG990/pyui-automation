# Performance Monitoring - Мониторинг производительности

## 🏗️ **Архитектура мониторинга производительности**

Система мониторинга производительности построена на принципах SOLID и использует единую основу для сбора метрик:

### **📊 Иерархия компонентов:**

```
utils/metrics.py (основа)
├── MetricsCollector - универсальный сборщик метрик
├── MetricPoint - универсальная точка метрики
└── metrics - глобальный экземпляр

core/services/ (специализированные сервисы)
├── PerformanceMonitor - мониторинг производительности
├── PerformanceAnalyzer - анализ метрик
├── PerformanceTester - тестирование производительности
└── MemoryLeakDetector - детекция утечек памяти
```

### **🎯 Принципы архитектуры:**

1. **Единая основа** - `utils/metrics.py` используется всеми сервисами
2. **Специализация** - каждый сервис фокусируется на своей области
3. **Переиспользование** - нет дублирования кода
4. **Расширяемость** - легко добавлять новые типы метрик

## 🚀 **Использование**

### **Базовый мониторинг производительности**
```python
from pyui_automation import AutomationSession

session = AutomationSession(backend)

# Запуск мониторинга
session.start_performance_monitoring(interval=1.0)

# Выполнение действий
session.click("button")
session.type_text("input", "text")

# Остановка и получение метрик
metrics = session.stop_performance_monitoring()

# Анализ результатов
for metric in metrics:
    print(f"CPU: {metric.cpu_usage}%, Memory: {metric.memory_usage} bytes")
```

### **Детальный мониторинг**
```python
# Получение статистики
stats = session.get_performance_stats()
print(f"CPU Usage - Avg: {stats['cpu_usage']['avg']:.2f}%")
print(f"Memory Usage - Max: {stats['memory_usage']['max']} bytes")
print(f"Response Time - Avg: {stats['response_time']['avg']:.3f}s")

# Измерение конкретных операций
session.performance_service.start_performance_timer("button_click")
session.click("button")
duration = session.performance_service.stop_performance_timer("button_click")
print(f"Button click took: {duration:.3f}s")

# Запись кастомных метрик
session.performance_service.record_custom_metric("custom_metric", 42.0)
```

### **Тестирование производительности**
```python
# Измерение производительности действия
result = session.measure_action_performance(
    lambda: session.click("button"), 
    runs=10
)

print(f"Average time: {result['average']:.3f}s")
print(f"Min time: {result['min']:.3f}s")
print(f"Max time: {result['max']:.3f}s")

# Стресс-тестирование
stress_result = session.run_stress_test(
    lambda: session.click("button"),
    duration=60.0
)

print(f"Operations completed: {stress_result['operations']}")
print(f"Average time: {stress_result['average_time']:.3f}s")
```

### **Детекция утечек памяти**
```python
# Проверка на утечки памяти
leak_result = session.check_memory_leaks(
    lambda: session.click("button"),
    iterations=100
)

if leak_result['memory_leak_detected']:
    print(f"Memory leak detected! Growth: {leak_result['memory_growth']} bytes")
else:
    print("No memory leaks detected")
```

## 📊 **Типы метрик**

### **Автоматически собираемые метрики:**
- **CPU Usage** - процент использования процессора
- **Memory Usage** - использование памяти в байтах
- **Response Time** - время отклика операций
- **Timestamp** - временная метка

### **Кастомные метрики:**
```python
# Запись любых метрик
session.performance_service.record_custom_metric("page_load_time", 2.5)
session.performance_service.record_custom_metric("api_response_time", 0.8)
session.performance_service.record_custom_metric("database_query_time", 0.1)
```

## 🔧 **Продвинутое использование**

### **Прямой доступ к MetricsCollector**
```python
# Получение базового сборщика метрик
collector = session.performance_service.get_metrics_collector()

# Использование всех возможностей MetricsCollector
collector.record_value("custom_metric", 123.45)
collector.start_timer("operation")
# ... операция ...
duration = collector.stop_timer("operation")

# Получение статистики
stats = collector.get_stats("custom_metric")
print(f"Custom metric stats: {stats}")
```

### **Интеграция с глобальными метриками**
```python
from pyui_automation.utils import metrics

# Использование глобального сборщика
metrics.record_value("global_metric", 999.0)
metrics.start_timer("global_operation")
# ... операция ...
duration = metrics.stop_timer("global_operation")

# Синхронизация с PerformanceMonitor
session.performance_service.record_custom_metric("global_metric", 999.0)
```

## 📈 **Анализ результатов**

### **Базовый анализ**
```python
def analyze_performance(metrics):
    """Анализ метрик производительности"""
    
    # Статистика CPU
    cpu_values = [m.cpu_usage for m in metrics]
    avg_cpu = sum(cpu_values) / len(cpu_values)
    max_cpu = max(cpu_values)
    
    print(f"CPU Usage - Avg: {avg_cpu:.2f}%, Max: {max_cpu:.2f}%")
    
    # Статистика памяти
    memory_values = [m.memory_usage for m in metrics]
    avg_memory = sum(memory_values) / len(memory_values)
    max_memory = max(memory_values)
    
    print(f"Memory Usage - Avg: {avg_memory/1024/1024:.2f}MB, Max: {max_memory/1024/1024:.2f}MB")
    
    # Анализ трендов
    if memory_values[-1] > memory_values[0] * 1.5:
        print("⚠️  Potential memory leak detected!")
    
    if avg_cpu > 80:
        print("⚠️  High CPU usage detected!")
```

### **Детальный анализ с PerformanceAnalyzer**
```python
# Получение детальной статистики
stats = session.get_performance_stats()

# Анализ CPU
cpu_stats = stats['cpu_usage']
if cpu_stats['avg'] > 80:
    print("🚨 High average CPU usage")
if cpu_stats['max'] > 95:
    print("🚨 CPU usage spikes detected")

# Анализ памяти
memory_stats = stats['memory_usage']
memory_growth = memory_stats['max'] - memory_stats['min']
if memory_growth > 100 * 1024 * 1024:  # 100MB
    print("🚨 Significant memory growth detected")

# Анализ времени отклика
response_stats = stats['response_time']
if response_stats['avg'] > 1.0:
    print("🚨 Slow response times detected")
```

## 🧪 **Примеры тестов**

### **Тест производительности UI операций**
```python
def test_ui_performance():
    """Тест производительности UI операций"""
    
    session = AutomationSession(backend)
    
    # Запуск мониторинга
    session.start_performance_monitoring(interval=0.5)
    
    try:
        # Выполнение UI операций
        session.click("login_button")
        session.type_text("username", "test_user")
        session.type_text("password", "test_pass")
        session.click("submit_button")
        
        # Ожидание загрузки
        session.wait_for_element("dashboard", timeout=10)
        
    finally:
        # Остановка мониторинга
        metrics = session.stop_performance_monitoring()
    
    # Анализ результатов
    stats = session.get_performance_stats()
    
    # Проверки
    assert stats['cpu_usage']['avg'] < 50, "CPU usage too high"
    assert stats['memory_usage']['max'] < 500 * 1024 * 1024, "Memory usage too high"  # 500MB
    assert stats['response_time']['avg'] < 2.0, "Response time too slow"
```

### **Тест на утечки памяти**
```python
def test_memory_leaks():
    """Тест на утечки памяти"""
    
    session = AutomationSession(backend)
    
    # Проверка утечек при повторных операциях
    leak_result = session.check_memory_leaks(
        lambda: session.click("refresh_button"),
        iterations=50
    )
    
    # Проверки
    assert not leak_result['memory_leak_detected'], "Memory leak detected"
    assert leak_result['memory_growth'] < 10 * 1024 * 1024, "Excessive memory growth"  # 10MB
```

### **Стресс-тестирование**
```python
def test_stress_performance():
    """Стресс-тестирование производительности"""
    
    session = AutomationSession(backend)
    
    # Стресс-тест в течение 30 секунд
    stress_result = session.run_stress_test(
        lambda: session.click("action_button"),
        duration=30.0
    )
    
    # Проверки
    assert stress_result['operations'] > 100, "Too few operations completed"
    assert stress_result['average_time'] < 0.5, "Operations too slow"
    assert stress_result['memory_growth'] < 50 * 1024 * 1024, "Excessive memory growth"  # 50MB
```

## 🔧 **Конфигурация**

### **Настройка интервалов мониторинга**
```python
# Частый мониторинг для детального анализа
session.start_performance_monitoring(interval=0.1)  # 100ms

# Редкий мониторинг для долгосрочного наблюдения
session.start_performance_monitoring(interval=5.0)  # 5s
```

### **Настройка порогов**
```python
# Кастомные пороги для анализа
def custom_performance_check(metrics):
    for metric in metrics:
        if metric.cpu_usage > 90:
            print("🚨 Critical CPU usage!")
        if metric.memory_usage > 1 * 1024 * 1024 * 1024:  # 1GB
            print("🚨 High memory usage!")
```

## 📚 **Лучшие практики**

### **1. Выбор правильного интервала**
```python
# Для быстрых операций - частый мониторинг
session.start_performance_monitoring(interval=0.1)

# Для долгих операций - редкий мониторинг
session.start_performance_monitoring(interval=1.0)
```

### **2. Очистка метрик**
```python
# Очистка перед новым тестом
session.performance_service.clear_metrics()

# Или полная очистка
session.performance_service.get_metrics_collector().clear()
```

### **3. Анализ трендов**
```python
# Анализ роста памяти
memory_values = [m.memory_usage for m in metrics]
if memory_values[-1] > memory_values[0] * 2:
    print("🚨 Memory usage doubled!")
```

### **4. Интеграция с CI/CD**
```python
# Автоматические проверки в CI
def ci_performance_check():
    session = AutomationSession(backend)
    session.start_performance_monitoring()
    
    # Выполнение тестов
    run_all_tests()
    
    metrics = session.stop_performance_monitoring()
    stats = session.get_performance_stats()
    
    # CI проверки
    assert stats['cpu_usage']['avg'] < 70, "CPU usage exceeds threshold"
    assert stats['memory_usage']['max'] < 1 * 1024 * 1024 * 1024, "Memory usage exceeds threshold"
```

## 🎯 **Заключение**

Система мониторинга производительности обеспечивает:

- **Единую основу** - все сервисы используют `utils/metrics.py`
- **Специализацию** - каждый сервис фокусируется на своей области
- **Переиспользование** - нет дублирования кода
- **Расширяемость** - легко добавлять новые типы метрик
- **Производительность** - эффективный сбор и анализ метрик
- **Интеграцию** - работает с глобальными метриками

Архитектура соответствует принципам SOLID и обеспечивает надежный мониторинг производительности для автоматизации UI. 