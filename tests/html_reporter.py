import os
import shutil
from pathlib import Path
import pytest
from datetime import datetime

class HTMLReporter:
    def __init__(self, config):
        self.config = config
        self.report_dir = Path('report')
        self.report_path = self.report_dir / 'report.html'
        self.template_path = Path(__file__).parent.parent / 'templates' / 'report.html'
        
    def pytest_configure(self, config):
        # Create report directory
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.report_dir / 'assets' / 'js', exist_ok=True)
        os.makedirs(self.report_dir / 'assets' / 'css', exist_ok=True)
        os.makedirs(self.report_dir / 'results', exist_ok=True)
        
        # Copy assets
        assets_dir = Path(__file__).parent.parent / 'assets'
        
        # Copy JavaScript files
        for js_file in (assets_dir / 'js').glob('*.js'):
            shutil.copy2(js_file, self.report_dir / 'assets' / 'js' / js_file.name)
            
        # Copy CSS files
        for css_file in (assets_dir / 'css').glob('*.css'):
            shutil.copy2(css_file, self.report_dir / 'assets' / 'css' / css_file.name)
            
        # Create initial report from template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
            
        report = template.replace('{{ datetime }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        report = report.replace('{{ pytest_html_version }}', pytest.__version__)
        report = report.replace('{{ duration }}', '0.00 seconds')
        report = report.replace('{{ summary }}', 'Tests running...')
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
    def pytest_unconfigure(self, config):
        pass  # We don't need to do anything here

@pytest.hookimpl(hookwrapper=True)
def pytest_configure(config):
    reporter = HTMLReporter(config)
    config.pluginmanager.register(reporter)
    yield
