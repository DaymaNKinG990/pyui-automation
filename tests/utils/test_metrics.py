import time
from pyui_automation.utils.metrics import MetricsCollector

def test_record_and_get_stats():
    mc = MetricsCollector()
    for v in [1, 2, 3, 4, 5]:
        mc.record_value('test', v)
    stats = mc.get_stats('test')
    assert stats['min'] == 1
    assert stats['max'] == 5
    assert stats['avg'] == 3
    assert stats['median'] == 3
    assert stats['count'] == 5

def test_start_stop_timer():
    mc = MetricsCollector()
    mc.start_timer('op')
    time.sleep(0.01)
    duration = mc.stop_timer('op')
    assert duration is not None and duration > 0
    stats = mc.get_stats('op_duration')
    assert stats['count'] == 1

def test_stop_timer_without_start():
    mc = MetricsCollector()
    assert mc.stop_timer('nope') is None

def test_clear():
    mc = MetricsCollector()
    mc.record_value('a', 1)
    mc.start_timer('b')
    mc.clear()
    assert mc.get_stats('a') == {}
    assert mc._timers == {}

def test_history_limit():
    mc = MetricsCollector()
    for i in range(1100):
        mc.record_value('x', i)
    assert len(mc._metrics['x']) == 1000

def test_get_stats_empty():
    mc = MetricsCollector()
    assert mc.get_stats('none') == {} 