"""Модуль для экспорта результатов тестов в различные форматы."""

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import jinja2
import markdown
import plotly.graph_objects as go
from dataclasses import asdict

from .types import TestResult, TestSuite, TestStatus
from .analytics import TestAnalytics

class BaseExporter:
    """Базовый класс для экспортеров."""
    
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            output_dir = str(Path(__file__).parent.parent / 'reports')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

class JSONExporter(BaseExporter):
    """Экспорт в JSON формат."""
    
    async def export_suite(self, suite: TestSuite, filename: Optional[str] = None) -> str:
        """
        Экспорт набора тестов в JSON.
        
        Args:
            suite: Набор тестов
            filename: Имя файла (опционально)
            
        Returns:
            Путь к созданному файлу
        """
        if filename is None:
            filename = f"suite_{suite.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        output_path = self.output_dir / filename
        
        # Добавляем аналитику
        data = asdict(suite)
        data['analytics'] = TestAnalytics.analyze_suite(suite)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            
        return str(output_path)

class CSVExporter(BaseExporter):
    """Экспорт в CSV формат."""
    
    async def export_results(self, results: List[TestResult], filename: Optional[str] = None) -> str:
        """
        Экспорт результатов в CSV.
        
        Args:
            results: Список результатов
            filename: Имя файла (опционально)
            
        Returns:
            Путь к созданному файлу
        """
        if filename is None:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
        output_path = self.output_dir / filename
        
        fieldnames = ['id', 'name', 'status', 'duration', 'timestamp', 
                     'error_message', 'traceback']
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'id': result.id,
                    'name': result.name,
                    'status': result.status.name,
                    'duration': result.duration,
                    'timestamp': result.timestamp.isoformat(),
                    'error_message': result.error_message,
                    'traceback': result.traceback
                })
                
        return str(output_path)

class JUnitExporter(BaseExporter):
    """Экспорт в формат JUnit XML."""
    
    async def export_suite(self, suite: TestSuite, filename: Optional[str] = None) -> str:
        """
        Экспорт набора тестов в JUnit XML.
        
        Args:
            suite: Набор тестов
            filename: Имя файла (опционально)
            
        Returns:
            Путь к созданному файлу
        """
        if filename is None:
            filename = f"junit_{suite.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml"
            
        output_path = self.output_dir / filename
        
        # Создаем XML
        testsuite = ET.Element('testsuite')
        testsuite.set('name', suite.name)
        testsuite.set('tests', str(len(suite.results)))
        testsuite.set('time', str(sum(r.duration for r in suite.results)))
        
        for result in suite.results:
            testcase = ET.SubElement(testsuite, 'testcase')
            testcase.set('name', result.name)
            testcase.set('time', str(result.duration))
            
            if result.status != TestStatus.PASSED:
                failure = ET.SubElement(testcase, 'failure')
                failure.set('message', result.error_message or '')
                failure.text = result.traceback or ''
                
        tree = ET.ElementTree(testsuite)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return str(output_path)

class HTMLExporter(BaseExporter):
    """Экспорт в HTML формат."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_dir = Path(__file__).parent / 'templates'
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self._create_default_template()
        
    def _create_default_template(self):
        """Создание шаблона по умолчанию."""
        template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ suite.name }} - Test Results</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { margin-bottom: 20px; }
                .test-result { margin-bottom: 10px; padding: 10px; border-radius: 5px; }
                .passed { background-color: #dff0d8; }
                .failed { background-color: #f2dede; }
                .error { background-color: #fcf8e3; }
                .chart { margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>{{ suite.name }}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {{ analytics.total_tests }}</p>
                <p>Success Rate: {{ "%.2f"|format(analytics.success_rate) }}%</p>
                <p>Total Duration: {{ "%.2f"|format(analytics.total_duration) }}s</p>
            </div>
            
            <div id="statusChart" class="chart"></div>
            <div id="durationChart" class="chart"></div>
            
            <h2>Test Results</h2>
            {% for result in suite.results %}
            <div class="test-result {{ result.status.name.lower() }}">
                <h3>{{ result.name }}</h3>
                <p>Status: {{ result.status.name }}</p>
                <p>Duration: {{ "%.2f"|format(result.duration) }}s</p>
                {% if result.error_message %}
                <p>Error: {{ result.error_message }}</p>
                {% endif %}
            </div>
            {% endfor %}
            
            <script>
                // Status Chart
                var statusData = {{ status_chart|tojson }};
                Plotly.newPlot('statusChart', [{
                    values: statusData.values,
                    labels: statusData.labels,
                    type: 'pie',
                    title: 'Test Status Distribution'
                }]);
                
                // Duration Chart
                var durationData = {{ duration_chart|tojson }};
                Plotly.newPlot('durationChart', [{
                    x: durationData.names,
                    y: durationData.durations,
                    type: 'bar',
                    title: 'Test Durations'
                }]);
            </script>
        </body>
        </html>
        '''
        
        template_path = self.template_dir / 'default.html'
        if not template_path.exists():
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
    
    async def export_suite(self, suite: TestSuite, filename: Optional[str] = None,
                          template: Optional[str] = None) -> str:
        """
        Экспорт набора тестов в HTML.
        
        Args:
            suite: Набор тестов
            filename: Имя файла (опционально)
            template: Путь к шаблону (опционально)
            
        Returns:
            Путь к созданному файлу
        """
        if filename is None:
            filename = f"report_{suite.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
        output_path = self.output_dir / filename
        
        # Подготавливаем данные
        analytics = TestAnalytics.analyze_suite(suite)
        
        # Данные для графиков
        status_counts = analytics['status_counts']
        status_chart = {
            'values': list(status_counts.values()),
            'labels': [s.name for s in status_counts.keys()]
        }
        
        duration_chart = {
            'names': [r.name for r in suite.results],
            'durations': [r.duration for r in suite.results]
        }
        
        # Загружаем шаблон
        template_path = template or self.template_dir / 'default.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Рендерим HTML
        template = jinja2.Template(template_content)
        html = template.render(
            suite=suite,
            analytics=analytics,
            status_chart=status_chart,
            duration_chart=duration_chart
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        return str(output_path)

class MarkdownExporter(BaseExporter):
    """Экспорт в Markdown формат."""
    
    async def export_suite(self, suite: TestSuite, filename: Optional[str] = None) -> str:
        """
        Экспорт набора тестов в Markdown.
        
        Args:
            suite: Набор тестов
            filename: Имя файла (опционально)
            
        Returns:
            Путь к созданному файлу
        """
        if filename is None:
            filename = f"report_{suite.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
        output_path = self.output_dir / filename
        
        analytics = TestAnalytics.analyze_suite(suite)
        
        # Создаем markdown
        md = f"""# {suite.name}

## Summary
- Total Tests: {analytics['total_tests']}
- Success Rate: {analytics['success_rate']:.2f}%
- Total Duration: {analytics['total_duration']:.2f}s
- Average Duration: {analytics['avg_duration']:.2f}s

## Status Distribution
{self._create_status_table(analytics['status_counts'])}

## Test Results
"""
        
        # Добавляем результаты тестов
        for result in suite.results:
            md += f"""
### {result.name}
- Status: {result.status.name}
- Duration: {result.duration:.2f}s
"""
            if result.error_message:
                md += f"- Error: {result.error_message}\n"
                if result.traceback:
                    md += f"```\n{result.traceback}\n```\n"
                    
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)
            
        return str(output_path)
        
    def _create_status_table(self, status_counts: Dict[TestStatus, int]) -> str:
        """Создание таблицы статусов в markdown."""
        table = "| Status | Count |\n|--------|-------|\n"
        for status, count in status_counts.items():
            table += f"| {status.name} | {count} |\n"
        return table
