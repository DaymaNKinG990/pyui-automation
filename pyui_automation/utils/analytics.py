"""Модуль для анализа результатов тестов."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics

from .types import TestResult, TestSuite, TestStatus

class TestAnalytics:
    """Анализ результатов тестов."""
    
    @staticmethod
    def analyze_suite(suite: TestSuite) -> Dict[str, Any]:
        """
        Анализ результатов набора тестов.
        
        Args:
            suite: Набор тестов для анализа
            
        Returns:
            Словарь с метриками
        """
        if not suite.results:
            return {}
            
        # Подсчет результатов по статусам
        status_counts = defaultdict(int)
        for result in suite.results:
            status_counts[result.status] += 1
            
        # Расчет времени выполнения
        durations = [r.duration for r in suite.results]
        total_duration = sum(durations)
        
        # Анализ ошибок
        errors = [r for r in suite.results if r.error_message]
        error_types = defaultdict(int)
        for error in errors:
            error_type = error.error_message.split(':')[0] if error.error_message else 'Unknown'
            error_types[error_type] += 1
            
        return {
            'total_tests': len(suite.results),
            'status_counts': dict(status_counts),
            'success_rate': (status_counts[TestStatus.PASSED] / len(suite.results)) * 100,
            'total_duration': total_duration,
            'avg_duration': statistics.mean(durations),
            'median_duration': statistics.median(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'error_count': len(errors),
            'error_types': dict(error_types)
        }
    
    @staticmethod
    def find_flaky_tests(suites: List[TestSuite], threshold: float = 0.2) -> List[Dict[str, Any]]:
        """
        Поиск нестабильных тестов.
        
        Args:
            suites: Список наборов тестов
            threshold: Порог нестабильности (доля неудачных запусков)
            
        Returns:
            Список нестабильных тестов с метриками
        """
        test_results = defaultdict(list)
        
        # Собираем результаты по каждому тесту
        for suite in suites:
            for result in suite.results:
                test_results[result.name].append(result)
                
        flaky_tests = []
        for test_name, results in test_results.items():
            if len(results) < 2:
                continue
                
            # Подсчет результатов
            status_counts = defaultdict(int)
            for result in results:
                status_counts[result.status] += 1
                
            total_runs = len(results)
            failure_rate = (total_runs - status_counts[TestStatus.PASSED]) / total_runs
            
            if failure_rate > threshold:
                durations = [r.duration for r in results]
                flaky_tests.append({
                    'name': test_name,
                    'total_runs': total_runs,
                    'failure_rate': failure_rate * 100,
                    'status_counts': dict(status_counts),
                    'avg_duration': statistics.mean(durations),
                    'duration_stddev': statistics.stdev(durations) if len(durations) > 1 else 0
                })
                
        return sorted(flaky_tests, key=lambda x: x['failure_rate'], reverse=True)
    
    @staticmethod
    def analyze_trends(suites: List[TestSuite], window_days: int = 7) -> Dict[str, Any]:
        """
        Анализ трендов в результатах тестов.
        
        Args:
            suites: Список наборов тестов
            window_days: Размер окна для анализа в днях
            
        Returns:
            Словарь с трендами
        """
        # Сортируем наборы по времени
        sorted_suites = sorted(suites, key=lambda s: s.start_time)
        if not sorted_suites:
            return {}
            
        # Разбиваем на периоды
        now = datetime.now()
        periods = defaultdict(list)
        for suite in sorted_suites:
            days_ago = (now - suite.start_time).days
            period = days_ago // window_days
            periods[period].append(suite)
            
        # Анализируем каждый период
        trends = []
        for period, period_suites in sorted(periods.items()):
            metrics = {
                'period_start': (now - timedelta(days=period * window_days)).date(),
                'total_suites': len(period_suites),
                'total_tests': sum(len(s.results) for s in period_suites),
                'success_rate': 0,
                'avg_duration': 0
            }
            
            total_passed = 0
            total_duration = 0
            total_results = 0
            
            for suite in period_suites:
                for result in suite.results:
                    total_results += 1
                    if result.status == TestStatus.PASSED:
                        total_passed += 1
                    total_duration += result.duration
                    
            if total_results > 0:
                metrics['success_rate'] = (total_passed / total_results) * 100
                metrics['avg_duration'] = total_duration / total_results
                
            trends.append(metrics)
            
        # Рассчитываем изменения
        changes = {}
        if len(trends) >= 2:
            current = trends[-1]
            previous = trends[-2]
            changes = {
                'success_rate_change': current['success_rate'] - previous['success_rate'],
                'duration_change': current['avg_duration'] - previous['avg_duration'],
                'volume_change': ((current['total_tests'] - previous['total_tests']) 
                                / previous['total_tests'] * 100 if previous['total_tests'] > 0 else 0)
            }
            
        return {
            'trends': trends,
            'changes': changes
        }
