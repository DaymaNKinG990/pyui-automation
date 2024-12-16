"""
Пакет для запуска сервера отчетов о тестировании.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .server import TestReportServer, run_server

__all__ = ['TestReportServer', 'run_server']
