"""
Tests for metrics utilities
"""
import pytest
import time
from datetime import datetime

from pyui_automation.utils.metrics import MetricsCollector, MetricPoint, metrics


class TestMetricPoint:
    """Test MetricPoint dataclass"""
    
    def test_metric_point_creation(self):
        """Test MetricPoint creation"""
        point = MetricPoint(value=42.5)
        assert point.value == 42.5
        assert isinstance(point.timestamp, datetime)
    
    def test_metric_point_with_custom_timestamp(self):
        """Test MetricPoint with custom timestamp"""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        point = MetricPoint(value=100.0, timestamp=custom_time)
        assert point.value == 100.0
        assert point.timestamp == custom_time


class TestMetricsCollector:
    """Test MetricsCollector class"""
    
    def test_init(self):
        """Test MetricsCollector initialization"""
        collector = MetricsCollector()
        assert collector._metrics == {}
        assert collector._timers == {}
    
    def test_record_value(self):
        """Test record_value method"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 42.5)
        
        assert "test_metric" in collector._metrics
        assert len(collector._metrics["test_metric"]) == 1
        assert collector._metrics["test_metric"][0].value == 42.5
    
    def test_record_multiple_values(self):
        """Test recording multiple values"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 10.0)
        collector.record_value("test_metric", 20.0)
        collector.record_value("test_metric", 30.0)
        
        assert len(collector._metrics["test_metric"]) == 3
        values = [point.value for point in collector._metrics["test_metric"]]
        assert values == [10.0, 20.0, 30.0]
    
    def test_start_timer(self):
        """Test start_timer method"""
        collector = MetricsCollector()
        collector.start_timer("test_timer")
        
        assert "test_timer" in collector._timers
        assert isinstance(collector._timers["test_timer"], float)
    
    def test_stop_timer(self):
        """Test stop_timer method"""
        collector = MetricsCollector()
        collector.start_timer("test_timer")
        
        # Small delay to ensure measurable time
        time.sleep(0.01)
        
        duration = collector.stop_timer("test_timer")
        assert duration is not None
        assert duration > 0
        assert "test_timer" not in collector._timers
    
    def test_stop_timer_not_started(self):
        """Test stop_timer when timer was not started"""
        collector = MetricsCollector()
        duration = collector.stop_timer("nonexistent_timer")
        assert duration is None
    
    def test_get_stats_with_data(self):
        """Test get_stats with data"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 10.0)
        collector.record_value("test_metric", 20.0)
        collector.record_value("test_metric", 30.0)
        
        stats = collector.get_stats("test_metric")
        assert stats["min"] == 10.0
        assert stats["max"] == 30.0
        assert stats["avg"] == 20.0
        assert stats["median"] == 20.0
        assert stats["count"] == 3
    
    def test_get_stats_empty(self):
        """Test get_stats with no data"""
        collector = MetricsCollector()
        stats = collector.get_stats("nonexistent_metric")
        assert stats == {}
    
    def test_clear(self):
        """Test clear method"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 42.5)
        collector.start_timer("test_timer")
        
        collector.clear()
        
        assert collector._metrics == {}
        assert collector._timers == {}
    
    def test_history_limit(self):
        """Test that history is limited to 1000 entries"""
        collector = MetricsCollector()
        
        # Add more than 1000 values
        for i in range(1100):
            collector.record_value("test_metric", float(i))
        
        assert len(collector._metrics["test_metric"]) == 1000
        # Should keep the most recent values
        assert collector._metrics["test_metric"][-1].value == 1099.0


class TestGlobalMetrics:
    """Test global metrics instance"""
    
    def test_global_metrics_instance(self):
        """Test that global metrics instance exists"""
        assert isinstance(metrics, MetricsCollector)
    
    def test_global_metrics_functionality(self):
        """Test global metrics functionality"""
        # Clear any existing data
        metrics.clear()
        
        # Test recording values
        metrics.record_value("global_test", 100.0)
        stats = metrics.get_stats("global_test")
        assert stats["min"] == 100.0
        assert stats["max"] == 100.0
        assert stats["count"] == 1 