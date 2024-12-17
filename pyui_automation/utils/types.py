"""Типы данных и константы для системы отчетов."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any

class TestStatus(Enum):
    """Статусы выполнения тестов."""
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()
    ERROR = auto()
    RUNNING = auto()

class MessageType(Enum):
    """Типы сообщений WebSocket."""
    TEST_RESULT = "test_result"
    INITIAL_RESULTS = "initial_results"
    METRICS = "metrics"
    PING = "ping"
    PONG = "pong"
    ACK = "ack"
    ERROR = "error"

@dataclass
class TestResult:
    """Результат выполнения теста."""
    id: str
    name: str
    status: TestStatus
    duration: float
    timestamp: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestSuite:
    """Набор тестов."""
    id: str
    name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Длительность выполнения набора тестов."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def status_counts(self) -> Dict[TestStatus, int]:
        """Подсчет результатов по статусам."""
        counts = {status: 0 for status in TestStatus}
        for result in self.results:
            counts[result.status] += 1
        return counts

@dataclass
class WebSocketMessage:
    """Сообщение WebSocket."""
    type: MessageType
    data: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

# Константы
MAX_QUEUE_SIZE = 1000
CLEANUP_INTERVAL = 3600  # 1 час
MAX_RESULT_AGE = 86400  # 24 часа
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 1.0  # секунды
ACK_TIMEOUT = 10.0  # секунды
PING_INTERVAL = 30.0  # секунды
WEBSOCKET_CLOSE_TIMEOUT = 5.0  # секунды
