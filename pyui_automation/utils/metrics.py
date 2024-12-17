"""Модуль для сбора метрик производительности."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import statistics

@dataclass
class MetricPoint:
    """Точка метрики."""
    value: float
    timestamp: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    """Сборщик метрик производительности."""
    
    def __init__(self):
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._timers: Dict[str, float] = {}
    
    def record_value(self, name: str, value: float):
        """
        Записать значение метрики.
        
        Args:
            name: Имя метрики
            value: Значение метрики
        """
        self._metrics[name].append(MetricPoint(value))
        
        # Ограничиваем историю метрик
        if len(self._metrics[name]) > 1000:
            self._metrics[name] = self._metrics[name][-1000:]
    
    def start_timer(self, name: str):
        """
        Запустить таймер для метрики.
        
        Args:
            name: Имя метрики
        """
        self._timers[name] = time.perf_counter()
    
    def stop_timer(self, name: str) -> Optional[float]:
        """
        Остановить таймер и записать длительность.
        
        Args:
            name: Имя метрики
            
        Returns:
            Длительность операции в секундах или None, если таймер не был запущен
        """
        start_time = self._timers.pop(name, None)
        if start_time is not None:
            duration = time.perf_counter() - start_time
            self.record_value(f"{name}_duration", duration)
            return duration
        return None
    
    def get_stats(self, name: str) -> dict:
        """
        Получить статистику по метрике.
        
        Args:
            name: Имя метрики
            
        Returns:
            Словарь со статистикой (min, max, avg, median)
        """
        values = [point.value for point in self._metrics.get(name, [])]
        if not values:
            return {}
            
        return {
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'count': len(values)
        }
    
    def clear(self):
        """Очистить все метрики."""
        self._metrics.clear()
        self._timers.clear()

# Глобальный экземпляр для использования во всем приложении
metrics = MetricsCollector()
