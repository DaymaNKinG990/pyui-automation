import pytest
from unittest.mock import MagicMock, patch
import time
from pyui_automation.performance import PerformanceMonitor, PerformanceMetric
import json


@pytest.fixture
def mock_process():
    """Create a mock process for testing"""
    process = MagicMock()
    process.pid = 12345
    process.name.return_value = "test_app.exe"
    process.cpu_percent.return_value = 10.0
    
    # Create memory info mock with fixed value
    memory_info = MagicMock()
    memory_info.rss = MagicMock(return_value=100 * 1024 * 1024)  # 100MB
    process.memory_info.return_value = memory_info
    return process


@pytest.fixture
def perf_monitor(mock_process):
    """Create PerformanceMonitor instance"""
    monitor = PerformanceMonitor(mock_process)
    monitor.metrics = []  # Ensure clean state
    monitor.is_monitoring = False  # Start in non-monitoring state
    return monitor


def test_start_monitoring(perf_monitor):
    """Test starting performance monitoring"""
    perf_monitor.start_monitoring()
    assert perf_monitor.is_monitoring
    assert perf_monitor.start_time is not None


def test_stop_monitoring(perf_monitor):
    """Test stopping performance monitoring"""
    perf_monitor.start_monitoring()
    time.sleep(0.1)  # Small delay to ensure metrics are collected
    metrics = perf_monitor.stop_monitoring()
    
    assert not perf_monitor.is_monitoring
    assert isinstance(metrics, dict)
    assert "duration" in metrics
    assert metrics["duration"] > 0


def test_get_cpu_usage(perf_monitor, mock_process):
    """Test getting CPU usage"""
    mock_process.cpu_percent.return_value = 5.0
    
    cpu_usage = perf_monitor.get_cpu_usage()
    assert isinstance(cpu_usage, float)
    assert cpu_usage == 5.0
    mock_process.cpu_percent.assert_called_once()


def test_get_memory_usage(perf_monitor, mock_process):
    """Test getting memory usage"""
    memory_size = 100 * 1024 * 1024  # 100MB
    memory_info = MagicMock()
    memory_info.rss = MagicMock(return_value=memory_size)
    mock_process.memory_info.return_value = memory_info

    memory_usage = perf_monitor.get_memory_usage()
    assert isinstance(memory_usage, int)
    assert memory_usage == memory_size


def test_get_response_time(perf_monitor):
    """Test measuring response time"""
    with patch('time.time', side_effect=[0, 1.5]):  # Mock 1.5 second delay
        response_time = perf_monitor.measure_response_time(lambda: None)
    
    assert isinstance(response_time, float)
    assert response_time == 1.5


def test_generate_report(perf_monitor, temp_dir):
    """Test generating performance report"""
    # Add some test metrics
    perf_monitor.metrics = [
        PerformanceMetric(
            timestamp=time.time(),
            cpu_usage=5.0,
            memory_usage=100 * 1024 * 1024,  # 100MB
            response_time=0.1
        ),
        PerformanceMetric(
            timestamp=time.time() + 1,
            cpu_usage=6.0,
            memory_usage=110 * 1024 * 1024,  # 110MB
            response_time=0.2
        )
    ]
    
    report_path = temp_dir / "performance_report.html"
    perf_monitor.generate_report(str(report_path))
    
    assert report_path.exists()
    assert report_path.with_suffix('.png').exists()


def test_collect_metrics(perf_monitor, mock_process):
    """Test collecting all performance metrics"""
    cpu_value = 5.0
    memory_size = 100 * 1024 * 1024  # 100MB
    
    memory_info = MagicMock()
    memory_info.rss = MagicMock(return_value=memory_size)
    mock_process.cpu_percent.return_value = cpu_value
    mock_process.memory_info.return_value = memory_info

    metrics = perf_monitor.collect_metrics()

    assert isinstance(metrics, dict)
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert metrics["cpu_usage"] == cpu_value
    assert metrics["memory_usage"] == memory_size


def test_measure_operation_time(perf_monitor):
    """Test measuring operation execution time"""
    def test_operation():
        time.sleep(0.1)
        return "test"
    
    result, duration = perf_monitor.measure_operation_time(test_operation)
    
    assert result == "test"
    assert duration >= 0.1


def test_monitor_resource_usage(perf_monitor):
    """Test monitoring resource usage over time"""
    perf_monitor.start_monitoring()
    time.sleep(0.2)  # Collect some data points
    metrics = perf_monitor.stop_monitoring()
    
    assert "cpu_usage_history" in metrics
    assert "memory_usage_history" in metrics
    assert len(metrics["cpu_usage_history"]) > 0
    assert len(metrics["memory_usage_history"]) > 0


def test_performance_threshold_check(perf_monitor):
    """Test checking performance against thresholds"""
    # Set thresholds
    perf_monitor.set_threshold("cpu_usage", 80.0)
    perf_monitor.set_threshold("memory_usage", 200 * 1024 * 1024)  # 200MB
    
    # Add a test metric that exceeds CPU threshold
    perf_monitor.metrics = [
        PerformanceMetric(
            timestamp=time.time(),
            cpu_usage=90.0,  # Exceeds threshold
            memory_usage=100 * 1024 * 1024,  # Below threshold
            response_time=0.5
        )
    ]

    alerts = perf_monitor.check_thresholds()
    assert "cpu_usage" in alerts
    assert alerts["cpu_usage"] is True
    assert alerts.get("memory_usage", False) is False


def test_record_metric(perf_monitor, mock_process):
    """Test recording a single performance metric"""
    # Set up mock process
    memory_size = 100 * 1024 * 1024  # 100MB
    memory_info = MagicMock()
    memory_info.rss = MagicMock(return_value=memory_size)
    mock_process.memory_info.return_value = memory_info
    mock_process.cpu_percent.return_value = 5.0

    # Start monitoring and record metric
    perf_monitor.start_monitoring()
    perf_monitor.record_metric()

    assert len(perf_monitor.metrics) == 1
    assert perf_monitor.metrics[0].memory_usage == memory_size
    assert perf_monitor.metrics[0].cpu_usage == 5.0


def test_analyze_metrics(perf_monitor):
    """Test analyzing collected metrics"""
    metrics = [
        PerformanceMetric(time.time(), 5.0, 100.0, 0.1),
        PerformanceMetric(time.time(), 10.0, 150.0, 0.2),
        PerformanceMetric(time.time(), 7.0, 120.0, 0.15)
    ]
    perf_monitor.metrics = metrics

    analysis = perf_monitor.analyze_metrics()
    assert isinstance(analysis, dict)
    assert "cpu_usage" in analysis
    assert "memory_usage" in analysis
    assert "response_time" in analysis
    
    cpu_stats = analysis["cpu_usage"]
    assert cpu_stats["min"] == 5.0
    assert cpu_stats["max"] == 10.0
    assert 7.0 <= cpu_stats["avg"] <= 8.0


def test_export_metrics(perf_monitor, tmp_path):
    """Test exporting metrics to file"""
    metrics = [
        PerformanceMetric(time.time(), 5.0, 100.0, 0.1),
        PerformanceMetric(time.time(), 10.0, 150.0, 0.2)
    ]
    perf_monitor.metrics = metrics

    export_path = tmp_path / "metrics.json"
    perf_monitor.export_metrics(export_path)

    assert export_path.exists()
    with open(export_path) as f:
        data = json.load(f)
        assert "metrics" in data
        assert "analysis" in data
        assert len(data["metrics"]) == 2
        assert "cpu_usage" in data["metrics"][0]


def test_plot_metrics(perf_monitor, tmp_path):
    """Test plotting performance metrics"""
    metrics = [
        PerformanceMetric(time.time(), 5.0, 100.0, 0.1),
        PerformanceMetric(time.time(), 10.0, 150.0, 0.2),
        PerformanceMetric(time.time(), 7.0, 120.0, 0.15)
    ]
    perf_monitor.metrics = metrics
    
    plot_path = tmp_path / "performance.png"
    perf_monitor.plot_metrics(plot_path)
    assert plot_path.exists()


@pytest.fixture
def perf_test(mock_process):
    """Create PerformanceTest instance"""
    from pyui_automation.performance import PerformanceTest
    return PerformanceTest(mock_process)


def test_measure_action(perf_test):
    """Test measuring action performance"""
    def test_action():
        time.sleep(0.1)
        return True
    
    results = perf_test.measure_action(
        test_action,
        name="test_operation",
        warmup_runs=1,
        test_runs=3
    )
    
    assert isinstance(results, dict)
    assert results["name"] == "test_operation"
    assert results["min_time"] >= 0.1
    assert results["max_time"] >= 0.1
    assert results["avg_time"] >= 0.1
    assert "std_dev" in results


def test_stress_test(perf_test):
    """Test stress testing"""
    def test_action():
        time.sleep(0.01)
        return True
    
    results = perf_test.stress_test(
        test_action,
        duration=1,
        interval=0.1
    )
    
    assert isinstance(results, dict)
    assert results["duration"] >= 1.0
    assert results["actions_performed"] > 0
    assert results["errors"] == 0
    assert results["actions_per_second"] > 0
    assert results["error_rate"] == 0


def test_stress_test_with_errors(perf_test):
    """Test stress testing with failing actions"""
    call_count = 0
    def test_action():
        nonlocal call_count
        call_count += 1
        if call_count % 2 == 0:
            raise Exception("Test error")
        return True
    
    results = perf_test.stress_test(
        test_action,
        duration=1,
        interval=0.1
    )
    
    assert results["errors"] > 0
    assert results["error_rate"] > 0


def test_memory_leak_test(perf_test):
    """Test memory leak detection"""
    # Mock increasing memory usage
    memory_values = []
    base_memory = 100 * 1024 * 1024  # Start at 100MB
    
    def get_memory():
        memory_value = base_memory + len(memory_values) * 10 * 1024 * 1024  # Increase by 10MB each call
        memory_values.append(memory_value)
        return memory_value
    
    perf_test.application.get_memory_usage = get_memory
    
    def leaky_action():
        time.sleep(0.01)
    
    results = perf_test.memory_leak_test(
        leaky_action,
        iterations=10,
        threshold_mb=5.0
    )
    
    assert isinstance(results, dict)
    assert "has_leak" in results
    assert "memory_growth_mb" in results
    assert "growth_rate_mb_per_iteration" in results
    assert results["has_leak"] is True
    assert results["memory_growth_mb"] > 5.0  # Should show growth of more than 5MB


def test_memory_leak_test_no_leak(perf_test):
    """Test memory leak detection with no leak"""
    # Mock stable memory usage
    stable_memory = 100 * 1024 * 1024  # Constant 100MB
    perf_test.application.get_memory_usage = lambda: stable_memory
    
    def stable_action():
        time.sleep(0.01)
    
    results = perf_test.memory_leak_test(
        stable_action,
        iterations=10,
        threshold_mb=5.0
    )
    
    assert isinstance(results, dict)
    assert not results["has_leak"]
    assert results["memory_growth_mb"] == 0


def test_performance_metric_dataclass():
    """Test PerformanceMetric dataclass"""
    timestamp = time.time()
    metric = PerformanceMetric(
        timestamp=timestamp,
        cpu_usage=5.0,
        memory_usage=100.0,
        response_time=0.1
    )
    
    assert metric.timestamp == timestamp
    assert metric.cpu_usage == 5.0
    assert metric.memory_usage == 100.0
    assert metric.response_time == 0.1


def test_monitor_cleanup(perf_monitor):
    """Test monitor cleanup"""
    perf_monitor.start_monitoring()
    perf_monitor.record_metric()
    perf_monitor.cleanup()
    
    assert not perf_monitor.is_monitoring
    assert len(perf_monitor.metrics) == 0


@pytest.mark.parametrize("interval", [0.1, 0.5, 1.0])
def test_monitoring_intervals(perf_monitor, interval):
    """Test monitoring with different intervals"""
    perf_monitor.start_monitoring(interval=interval)
    time.sleep(interval * 2)  # Wait for at least 2 intervals
    metrics = perf_monitor.stop_monitoring()
    
    assert len(perf_monitor.metrics) >= 1


def test_concurrent_monitoring(perf_monitor):
    """Test concurrent monitoring operations"""
    import threading
    
    def monitoring_thread():
        perf_monitor.start_monitoring(interval=0.1)
        time.sleep(0.3)
        perf_monitor.stop_monitoring()
    
    threads = [threading.Thread(target=monitoring_thread) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # Only the first monitoring session should have succeeded
    assert len(perf_monitor.metrics) > 0


def test_error_handling(perf_monitor, mock_process):
    """Test error handling in metric collection"""
    mock_process.cpu_percent.side_effect = Exception("CPU error")
    mock_process.memory_info.side_effect = Exception("Memory error")

    # Start monitoring before recording metrics
    perf_monitor.start_monitoring()
    perf_monitor.record_metric()
    
    assert len(perf_monitor.metrics) == 1
    metric = perf_monitor.metrics[0]
    assert metric.cpu_usage == 0.0
    assert metric.memory_usage == 0


def test_resource_threshold_alerts(perf_monitor):
    """Test resource usage threshold alerts"""
    perf_monitor.set_threshold("cpu_usage", 80.0)
    perf_monitor.set_threshold("memory_usage", 1000.0)

    # Start monitoring and record a metric with high CPU usage
    perf_monitor.start_monitoring()
    with patch.object(perf_monitor, 'get_cpu_usage', return_value=90.0):
        perf_monitor.record_metric()
        alerts = perf_monitor.check_thresholds()

    assert "cpu_usage" in alerts
    assert alerts["cpu_usage"] is True  # CPU usage exceeds threshold


def test_detect_regression(perf_test):
    """Test performance regression detection"""
    # Mock baseline metrics
    baseline_metrics = {
        'response_time': {'avg': 0.1, 'std': 0.02},
        'memory_usage': {'avg': 100 * 1024 * 1024, 'std': 10 * 1024 * 1024},
        'cpu_usage': {'avg': 5.0, 'std': 1.0}
    }
    
    # Mock a slow action that would cause regression
    def slow_action():
        time.sleep(0.2)  # Much slower than baseline
    
    # Configure mock memory and CPU values
    perf_test.application.get_memory_usage = lambda: 150 * 1024 * 1024  # Higher memory usage
    perf_test.application.get_cpu_usage = lambda: 8.0  # Higher CPU usage
    
    results = perf_test.detect_regression(
        slow_action,
        baseline_metrics,
        test_runs=3,
        threshold_std=2.0
    )
    
    assert isinstance(results, dict)
    assert 'has_regression' in results
    assert 'metrics' in results
    assert 'deviations' in results
    assert results['has_regression'] is True
    
    # Test with stable performance
    def stable_action():
        time.sleep(0.1)  # Matches baseline
    
    perf_test.application.get_memory_usage = lambda: 100 * 1024 * 1024
    perf_test.application.get_cpu_usage = lambda: 5.0
    
    results = perf_test.detect_regression(
        stable_action,
        baseline_metrics,
        test_runs=3,
        threshold_std=2.0
    )
    
    assert results['has_regression'] is False
