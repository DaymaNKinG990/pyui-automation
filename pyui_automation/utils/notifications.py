"""Модуль для отправки уведомлений о результатах тестов."""

import smtplib
import asyncio
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .types import TestResult, TestSuite, TestStatus
from .analytics import TestAnalytics

@dataclass
class NotificationConfig:
    """Конфигурация уведомлений."""
    email_enabled: bool = False
    email_from: Optional[str] = None
    email_to: List[str] = None
    email_server: str = "smtp.gmail.com"
    email_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_ids: List[str] = None
    
    notification_threshold: float = 80.0  # Порог успешности для уведомлений

class NotificationManager:
    """Менеджер уведомлений."""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self._session = None
        
    async def start(self):
        """Инициализация менеджера."""
        if self.config.slack_enabled or self.config.telegram_enabled:
            self._session = aiohttp.ClientSession()
            
    async def stop(self):
        """Остановка менеджера."""
        if self._session:
            await self._session.close()
            
    async def notify_suite_completion(self, suite: TestSuite):
        """
        Отправка уведомлений о завершении набора тестов.
        
        Args:
            suite: Завершенный набор тестов
        """
        analytics = TestAnalytics.analyze_suite(suite)
        success_rate = analytics['success_rate']
        
        # Проверяем, нужно ли отправлять уведомление
        if success_rate >= self.config.notification_threshold:
            return
            
        message = self._create_notification_message(suite, analytics)
        
        tasks = []
        if self.config.email_enabled:
            tasks.append(self._send_email(message))
        if self.config.slack_enabled:
            tasks.append(self._send_slack(message))
        if self.config.telegram_enabled:
            tasks.append(self._send_telegram(message))
            
        await asyncio.gather(*tasks)
        
    def _create_notification_message(self, suite: TestSuite, 
                                   analytics: Dict[str, Any]) -> Dict[str, str]:
        """Создание сообщения для уведомления."""
        status_counts = analytics['status_counts']
        
        text = f"""
Test Suite: {suite.name}
Status: {'❌ Failed' if analytics['success_rate'] < self.config.notification_threshold else '✅ Passed'}

Summary:
- Total Tests: {analytics['total_tests']}
- Success Rate: {analytics['success_rate']:.2f}%
- Total Duration: {analytics['total_duration']:.2f}s

Status Distribution:
{self._format_status_counts(status_counts)}

Failed Tests:
{self._format_failed_tests(suite.results)}
"""
        
        html = f"""
<h2>Test Suite: {suite.name}</h2>
<p>Status: {'❌ Failed' if analytics['success_rate'] < self.config.notification_threshold else '✅ Passed'}</p>

<h3>Summary</h3>
<ul>
    <li>Total Tests: {analytics['total_tests']}</li>
    <li>Success Rate: {analytics['success_rate']:.2f}%</li>
    <li>Total Duration: {analytics['total_duration']:.2f}s</li>
</ul>

<h3>Status Distribution</h3>
{self._format_status_counts_html(status_counts)}

<h3>Failed Tests</h3>
{self._format_failed_tests_html(suite.results)}
"""
        
        return {
            'text': text.strip(),
            'html': html.strip()
        }
        
    def _format_status_counts(self, counts: Dict[TestStatus, int]) -> str:
        """Форматирование статистики для текстового сообщения."""
        return '\n'.join(f"- {status.name}: {count}" 
                        for status, count in counts.items())
        
    def _format_status_counts_html(self, counts: Dict[TestStatus, int]) -> str:
        """Форматирование статистики для HTML."""
        return '<ul>' + ''.join(
            f"<li>{status.name}: {count}</li>"
            for status, count in counts.items()
        ) + '</ul>'
        
    def _format_failed_tests(self, results: List[TestResult]) -> str:
        """Форматирование списка упавших тестов для текстового сообщения."""
        failed = [r for r in results if r.status != TestStatus.PASSED]
        if not failed:
            return "No failed tests"
            
        return '\n'.join(
            f"- {result.name}: {result.error_message or 'No error message'}"
            for result in failed
        )
        
    def _format_failed_tests_html(self, results: List[TestResult]) -> str:
        """Форматирование списка упавших тестов для HTML."""
        failed = [r for r in results if r.status != TestStatus.PASSED]
        if not failed:
            return "<p>No failed tests</p>"
            
        return '<ul>' + ''.join(
            f"<li>{result.name}: {result.error_message or 'No error message'}</li>"
            for result in failed
        ) + '</ul>'
        
    async def _send_email(self, message: Dict[str, str]):
        """Отправка email уведомления."""
        if not all([self.config.email_from, self.config.email_to,
                   self.config.email_username, self.config.email_password]):
            return
            
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        msg['From'] = self.config.email_from
        msg['To'] = ', '.join(self.config.email_to)
        
        msg.attach(MIMEText(message['text'], 'plain'))
        msg.attach(MIMEText(message['html'], 'html'))
        
        try:
            server = smtplib.SMTP(self.config.email_server, self.config.email_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")
            
    async def _send_slack(self, message: Dict[str, str]):
        """Отправка уведомления в Slack."""
        if not self.config.slack_webhook_url or not self._session:
            return
            
        try:
            async with self._session.post(
                self.config.slack_webhook_url,
                json={'text': message['text']}
            ) as response:
                if response.status != 200:
                    print(f"Failed to send Slack notification: {await response.text()}")
        except Exception as e:
            print(f"Failed to send Slack notification: {e}")
            
    async def _send_telegram(self, message: Dict[str, str]):
        """Отправка уведомления в Telegram."""
        if not all([self.config.telegram_bot_token, 
                   self.config.telegram_chat_ids, self._session]):
            return
            
        api_url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        
        for chat_id in self.config.telegram_chat_ids:
            try:
                async with self._session.post(api_url, json={
                    'chat_id': chat_id,
                    'text': message['text'],
                    'parse_mode': 'HTML'
                }) as response:
                    if response.status != 200:
                        print(f"Failed to send Telegram notification: {await response.text()}")
            except Exception as e:
                print(f"Failed to send Telegram notification: {e}")
