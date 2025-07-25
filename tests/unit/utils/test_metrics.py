"""
Tests for metrics utilities
"""
import pytest
import time
from datetime import datetime

from pyui_automation.utils.metrics import (
    PerformanceMetrics, MetricsCollector, MetricsReporter
)


class TestMetricsCollector:
    """Tests for MetricsCollector class"""
    
    def test_metrics_collector_creation(self, mocker):
        """Test MetricsCollector creation"""
        collector = MetricsCollector()
        assert collector is not None
        assert hasattr(collector, '_metrics')
        assert hasattr(collector, '_timers')
    
    def test_record_value(self, mocker):
        """Test recording a value"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 42.5)
        
        stats = collector.get_stats("test_metric")
        assert stats['count'] == 1
        assert stats['min'] == 42.5
        assert stats['max'] == 42.5
        assert stats['avg'] == 42.5
    
    def test_record_multiple_values(self, mocker):
        """Test recording multiple values"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 10.0)
        collector.record_value("test_metric", 20.0)
        collector.record_value("test_metric", 30.0)
        
        stats = collector.get_stats("test_metric")
        assert stats['count'] == 3
        assert stats['min'] == 10.0
        assert stats['max'] == 30.0
        assert stats['avg'] == 20.0
        assert stats['median'] == 20.0
    
    def test_start_stop_timer(self, mocker):
        """Test timer functionality"""
        collector = MetricsCollector()
        
        collector.start_timer("test_timer")
        time.sleep(0.01)  # Small delay
        duration = collector.stop_timer("test_timer")
        
        assert duration is not None
        assert duration > 0.0
        
        # Check that duration was recorded
        stats = collector.get_stats("test_timer_duration")
        assert stats['count'] == 1
        assert stats['min'] > 0.0
    
    def test_stop_timer_without_start(self, mocker):
        """Test stopping timer without starting it"""
        collector = MetricsCollector()
        
        duration = collector.stop_timer("nonexistent_timer")
        
        assert duration is None
    
    def test_get_stats_empty_metric(self, mocker):
        """Test getting stats for empty metric"""
        collector = MetricsCollector()
        
        stats = collector.get_stats("nonexistent_metric")
        
        assert stats == {}
    
    def test_clear_metrics(self, mocker):
        """Test clearing all metrics"""
        collector = MetricsCollector()
        collector.record_value("test_metric", 42.5)
        collector.start_timer("test_timer")
        
        collector.clear()
        
        stats = collector.get_stats("test_metric")
        assert stats == {}
        
        # Timer should also be cleared
        duration = collector.stop_timer("test_timer")
        assert duration is None


class TestMetricPoint:
    """Tests for MetricPoint dataclass"""
    
    def test_metric_point_creation(self, mocker):
        """Test MetricPoint creation"""
        point = MetricPoint(value=42.5)
        
        assert point.value == 42.5
        assert isinstance(point.timestamp, datetime)
    
    def test_metric_point_with_custom_timestamp(self, mocker):
        """Test MetricPoint with custom timestamp"""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        point = MetricPoint(value=42.5, timestamp=custom_time)
        
        assert point.value == 42.5
        assert point.timestamp == custom_time


class TestGlobalMetrics:
    """Tests for global metrics instance"""
    
    def test_global_metrics_instance(self, mocker):
        """Test global metrics instance"""
        assert metrics is not None
        assert isinstance(metrics, MetricsCollector)
    
    def test_global_metrics_functionality(self, mocker):
        """Test global metrics functionality"""
        # Clear any existing metrics
        metrics.clear()
        
        metrics.record_value("global_test", 100.0)
        
        stats = metrics.get_stats("global_test")
        assert stats['count'] == 1
        assert stats['avg'] == 100.0 