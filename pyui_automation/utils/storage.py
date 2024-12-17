"""Модуль для хранения результатов тестов."""

import aiosqlite
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .types import TestResult, TestSuite, TestStatus

class TestResultStorage:
    """Хранилище результатов тестов в SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / 'data' / 'test_results.db')
        self.db_path = db_path
        self._ensure_db_dir()
        
    def _ensure_db_dir(self):
        """Создание директории для базы данных."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Инициализация базы данных."""
        async with aiosqlite.connect(self.db_path) as db:
            # Создаем таблицу для наборов тестов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS test_suites (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Создаем таблицу для результатов тестов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id TEXT PRIMARY KEY,
                    suite_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    error_message TEXT,
                    traceback TEXT,
                    metadata TEXT,
                    FOREIGN KEY (suite_id) REFERENCES test_suites(id)
                )
            ''')
            
            # Создаем индексы
            await db.execute('CREATE INDEX IF NOT EXISTS idx_suite_start ON test_suites(start_time)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_result_suite ON test_results(suite_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_result_timestamp ON test_results(timestamp)')
            
            await db.commit()
            
    async def save_suite(self, suite: TestSuite):
        """
        Сохранение набора тестов.
        
        Args:
            suite: Набор тестов для сохранения
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO test_suites (id, name, start_time, end_time, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                suite.id,
                suite.name,
                suite.start_time.isoformat(),
                suite.end_time.isoformat() if suite.end_time else None,
                json.dumps(suite.metadata) if hasattr(suite, 'metadata') else None
            ))
            await db.commit()
            
    async def save_result(self, result: TestResult, suite_id: str):
        """
        Сохранение результата теста.
        
        Args:
            result: Результат теста
            suite_id: ID набора тестов
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO test_results 
                (id, suite_id, name, status, duration, timestamp, error_message, traceback, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.id,
                suite_id,
                result.name,
                result.status.name,
                result.duration,
                result.timestamp.isoformat(),
                result.error_message,
                result.traceback,
                json.dumps(result.metadata)
            ))
            await db.commit()
            
    async def get_suite(self, suite_id: str) -> Optional[TestSuite]:
        """
        Получение набора тестов по ID.
        
        Args:
            suite_id: ID набора тестов
            
        Returns:
            Набор тестов или None, если не найден
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM test_suites WHERE id = ?',
                (suite_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return TestSuite(
                        id=row['id'],
                        name=row['name'],
                        start_time=datetime.fromisoformat(row['start_time']),
                        end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    )
        return None
            
    async def get_suite_results(self, suite_id: str) -> List[TestResult]:
        """
        Получение всех результатов для набора тестов.
        
        Args:
            suite_id: ID набора тестов
            
        Returns:
            Список результатов тестов
        """
        results = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM test_results WHERE suite_id = ? ORDER BY timestamp',
                (suite_id,)
            ) as cursor:
                async for row in cursor:
                    results.append(TestResult(
                        id=row['id'],
                        name=row['name'],
                        status=TestStatus[row['status']],
                        duration=row['duration'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        error_message=row['error_message'],
                        traceback=row['traceback'],
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    ))
        return results
    
    async def get_recent_suites(self, limit: int = 10) -> List[TestSuite]:
        """
        Получение последних наборов тестов.
        
        Args:
            limit: Максимальное количество наборов
            
        Returns:
            Список наборов тестов
        """
        suites = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM test_suites ORDER BY start_time DESC LIMIT ?',
                (limit,)
            ) as cursor:
                async for row in cursor:
                    suites.append(TestSuite(
                        id=row['id'],
                        name=row['name'],
                        start_time=datetime.fromisoformat(row['start_time']),
                        end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                        metadata=json.loads(row['metadata']) if row['metadata'] else {}
                    ))
        return suites
    
    async def cleanup_old_data(self, days: int = 30):
        """
        Удаление старых данных.
        
        Args:
            days: Количество дней хранения
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            # Удаляем старые результаты
            await db.execute(
                'DELETE FROM test_results WHERE timestamp < ?',
                (cutoff,)
            )
            # Удаляем старые наборы
            await db.execute(
                'DELETE FROM test_suites WHERE start_time < ?',
                (cutoff,)
            )
            await db.commit()
