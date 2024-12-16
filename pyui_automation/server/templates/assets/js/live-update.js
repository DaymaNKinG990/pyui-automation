// Регистрация Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/assets/js/sw.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
            })
            .catch(err => {
                console.error('ServiceWorker registration failed:', err);
            });
    });
}

// Функция для логирования с временной меткой
function logWithTimestamp(message, data = null) {
    const timestamp = new Date().toISOString();
    if (data) {
        console.log(`[${timestamp}] ${message}:`, data);
    } else {
        console.log(`[${timestamp}] ${message}`);
    }
}

class LiveUpdateClient {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.results = new Map();
        this.filters = {
            status: 'all',
            search: ''
        };
        this.observers = new Set();
        
        // Настройки обновления
        this.config = {
            updateInterval: 2000,  // Интервал обновления 2 секунды
            retryInterval: 5000,   // Интервал повторных попыток при ошибке
            maxRetries: 3,         // Максимальное количество попыток
            debounceDelay: 300,    // Задержка для debounce
            notificationTimeout: 5000,
            baseUrl: window.location.origin
        };
        
        // Состояние
        this.state = {
            currentRetries: 0,
            lastUpdateTime: null,
            lastResults: null,
            updateTimer: null,
            isUpdating: false,
            isTestRunning: false,
            totalTests: 0,
            completedTests: 0,
            expandedTests: new Set(),
            currentFilter: '',
            currentStatus: 'all'
        };

        logWithTimestamp('LiveUpdateClient: Инициализация');
        // Инициализация после создания
        this.initialize();
    }

    initialize() {
        logWithTimestamp('LiveUpdateClient: Инициализация WebSocket');
        this.initializeWebSocket();
        logWithTimestamp('LiveUpdateClient: Инициализация UI');
        this.initializeUI();
    }

    // Инициализация WebSocket соединения
    initializeWebSocket() {
        try {
            const wsUrl = `ws://${window.location.hostname}:${window.location.port}`;
            logWithTimestamp('LiveUpdateClient: Подключение к WebSocket:', wsUrl);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                logWithTimestamp('LiveUpdateClient: WebSocket соединение установлено');
                this.reconnectAttempts = 0;
                this.updateConnectionStatus('connected');
                // Отправляем тестовое сообщение
                this.ws.send(JSON.stringify({ type: 'hello' }));
            };
            
            this.ws.onclose = () => {
                logWithTimestamp('LiveUpdateClient: WebSocket соединение закрыто');
                this.updateConnectionStatus('disconnected');
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnect();
                } else {
                    this.notify('Не удалось восстановить соединение', 'error');
                }
            };
            
            this.ws.onerror = (error) => {
                logWithTimestamp('LiveUpdateClient: WebSocket ошибка:', error);
                this.notify('Произошла ошибка соединения', 'error');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    logWithTimestamp('LiveUpdateClient: Получено сообщение:', data);
                    this.handleMessage(data);
                } catch (e) {
                    logWithTimestamp('LiveUpdateClient: Ошибка обработки сообщения:', e);
                }
            };
            
        } catch (error) {
            logWithTimestamp('LiveUpdateClient: Ошибка инициализации WebSocket:', error);
            this.notify('Ошибка инициализации соединения', 'error');
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            logWithTimestamp(`LiveUpdateClient: Попытка переподключения ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            setTimeout(() => this.initializeWebSocket(), this.reconnectDelay);
        } else {
            logWithTimestamp('LiveUpdateClient: Достигнут лимит попыток переподключения');
            this.updateConnectionStatus('error');
            this.notify('Не удалось восстановить соединение', 'error');
        }
    }

    // Инициализация UI элементов
    initializeUI() {
        this.elements = {
            results: document.getElementById('test-results'),
            filters: document.getElementById('filters'),
            search: document.getElementById('search'),
            statusFilter: document.getElementById('status-filter'),
            connectionStatus: document.getElementById('connection-status'),
            reloadButton: document.getElementById('reload'),
            lastUpdate: document.getElementById('last-update'),
            expandAll: document.getElementById('expand-all'),
            collapseAll: document.getElementById('collapse-all'),
            notification: document.getElementById('notification'),
            notificationMessage: document.querySelector('.notification-message'),
            notificationClose: document.querySelector('.notification-close'),
            statusIcon: document.querySelector('.status-icon'),
            statusText: document.querySelector('.status-text'),
            testProgress: document.querySelector('.test-progress'),
            progressBar: document.querySelector('.progress-fill'),
            progressText: document.querySelector('.progress-text'),
            counters: {
                passed: document.querySelector('.counter.passed .count'),
                failed: document.querySelector('.counter.failed .count'),
                skipped: document.querySelector('.counter.skipped .count'),
                total: document.querySelector('.counter.total .count')
            }
        };

        // Добавляем слушатели событий
        this.setupEventListeners();

        // Инициализация наблюдателя за изменениями
        this.initializeIntersectionObserver();
    }

    // Настройка обработчиков событий
    setupEventListeners() {
        this.elements.search?.addEventListener('input', this.debounce(this.handleSearchInput.bind(this), this.config.debounceDelay));
        this.elements.statusFilter?.addEventListener('change', this.handleStatusFilterChange.bind(this));
        this.elements.reloadButton?.addEventListener('click', this.handleReload.bind(this));
        this.elements.expandAll?.addEventListener('click', () => this.toggleAllTests(true));
        this.elements.collapseAll?.addEventListener('click', () => this.toggleAllTests(false));
        this.elements.notificationClose?.addEventListener('click', () => this.hideNotification());

        // Делегирование событий для тестовых элементов
        this.elements.results?.addEventListener('click', (e) => {
            const testElement = e.target.closest('.test-case');
            if (testElement) {
                this.toggleResultDetails(testElement);
            }
        });
    }

    // Обработчики WebSocket событий
    handleMessage(data) {
        logWithTimestamp('LiveUpdateClient: Обработка сообщения:', data);
        
        switch (data.type) {
            case 'test_update':
                this.handleTestUpdate(data.data);
                break;
            case 'suite_complete':
                this.handleSuiteComplete(data.data);
                break;
            case 'pong':
                logWithTimestamp('LiveUpdateClient: Получен pong от сервера');
                break;
            case 'update':
                this.updateResults(data.content);
                break;
            default:
                logWithTimestamp('LiveUpdateClient: Неизвестный тип сообщения:', data.type);
        }
    }

    // Обработка обновления теста
    handleTestUpdate(testData) {
        const testElement = this.createOrUpdateTestElement(testData);
        this.updateTestStatus(testElement, testData);
        this.updateSummary();
    }

    // Обработка завершения набора тестов
    handleSuiteComplete(summary) {
        this.updateSummary(summary);
        this.notify('Тестирование завершено', 'success');
    }

    // Создание или обновление элемента теста
    createOrUpdateTestElement(testData) {
        const testId = `test-${testData.nodeid.replace(/[^a-zA-Z0-9]/g, '-')}`;
        let testElement = document.getElementById(testId);
        
        if (!testElement) {
            testElement = document.createElement('div');
            testElement.id = testId;
            testElement.className = 'test-item';
            document.querySelector('.test-results').appendChild(testElement);
        }
        
        return testElement;
    }

    // Обновление статуса теста
    updateTestStatus(element, testData) {
        const statusClass = testData.outcome === 'passed' ? 'success' : 'error';
        const duration = testData.duration.toFixed(2);
        
        element.className = `test-item ${statusClass}`;
        element.innerHTML = `
            <div class="test-header">
                <span class="test-name">${testData.name}</span>
                <span class="test-duration">${duration}s</span>
            </div>
            ${testData.longrepr ? `<pre class="test-error">${testData.longrepr}</pre>` : ''}
        `;
    }

    // Обновление сводки
    updateSummary(summary = null) {
        const summaryElement = document.querySelector('.summary') || this.createSummaryElement();
        
        if (summary) {
            summaryElement.innerHTML = `
                <div>Всего: ${summary.total}</div>
                <div class="success">Успешно: ${summary.passed}</div>
                <div class="error">Ошибок: ${summary.failed}</div>
                <div>Пропущено: ${summary.skipped}</div>
                <div>Время: ${summary.duration.toFixed(2)}s</div>
            `;
        } else {
            const tests = document.querySelectorAll('.test-item');
            const passed = document.querySelectorAll('.test-item.success').length;
            const failed = document.querySelectorAll('.test-item.error').length;
            
            summaryElement.innerHTML = `
                <div>Всего: ${tests.length}</div>
                <div class="success">Успешно: ${passed}</div>
                <div class="error">Ошибок: ${failed}</div>
            `;
        }
    }

    // Создание элемента сводки
    createSummaryElement() {
        const summaryElement = document.createElement('div');
        summaryElement.className = 'summary';
        document.querySelector('.test-results').insertBefore(
            summaryElement,
            document.querySelector('.test-results').firstChild
        );
        return summaryElement;
    }

    // Обновление результатов
    updateResults(data) {
        if (Array.isArray(data)) {
            data.forEach(result => {
                this.results.set(result.id, result);
            });
        } else {
            this.results.set(data.id, data);
        }

        this.updateUI();
        this.updateLastUpdateTime();
        this.updateTestProgress();
    }

    // Обновление UI
    updateUI() {
        const filteredResults = this.getFilteredResults();
        this.updateResultsList(filteredResults);
        this.updateCounters();
    }

    updateResultsList(results) {
        const fragment = document.createDocumentFragment();
        results.forEach(result => {
            const element = this.createResultElement(result);
            fragment.appendChild(element);
        });

        this.elements.results.innerHTML = '';
        this.elements.results.appendChild(fragment);
    }

    createResultElement(result) {
        const element = document.createElement('div');
        element.className = `test-case ${result.status}`;
        element.setAttribute('data-id', result.id);
        
        element.innerHTML = `
            <h3>${this.escapeHtml(result.name)}</h3>
            <div class="test-meta">
                <span class="status">${result.status}</span>
                <span class="duration">${result.duration}ms</span>
            </div>
            ${result.error ? `<pre class="error">${this.escapeHtml(result.error)}</pre>` : ''}
            ${result.output ? `<pre class="output">${this.escapeHtml(result.output)}</pre>` : ''}
        `;

        element.addEventListener('click', () => this.toggleResultDetails(element));
        return element;
    }

    // Вспомогательные методы
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    toggleResultDetails(element) {
        element.classList.toggle('expanded');
        const resultId = element.getAttribute('data-id');
        
        if (element.classList.contains('expanded')) {
            this.state.expandedTests.add(resultId);
            this.loadResultDetails(element);
        } else {
            this.state.expandedTests.delete(resultId);
        }
    }

    toggleAllTests(expand) {
        const testElements = this.elements.results.querySelectorAll('.test-case');
        testElements.forEach(element => {
            const isExpanded = element.classList.contains('expanded');
            if (expand && !isExpanded) {
                this.toggleResultDetails(element);
            } else if (!expand && isExpanded) {
                this.toggleResultDetails(element);
            }
        });
    }

    updateCounters() {
        const counts = {
            passed: 0,
            failed: 0,
            skipped: 0,
            total: this.results.size
        };

        this.results.forEach(result => {
            if (counts.hasOwnProperty(result.status)) {
                counts[result.status]++;
            }
        });

        Object.entries(counts).forEach(([status, count]) => {
            if (this.elements.counters[status]) {
                this.elements.counters[status].textContent = count;
            }
        });
    }

    updateConnectionStatus(status) {
        this.elements.connectionStatus.className = `status-indicator ${status}`;
        this.elements.connectionStatus.textContent = status === 'connected' ? 'Подключено' : 'Отключено';
    }

    updateLastUpdateTime() {
        const now = new Date();
        this.state.lastUpdateTime = now;
        if (this.elements.lastUpdate) {
            this.elements.lastUpdate.textContent = `Последнее обновление: ${now.toLocaleTimeString()}`;
        }
    }

    updateTestProgress() {
        if (!this.elements.testProgress) return;

        const total = this.results.size;
        const completed = Array.from(this.results.values()).filter(r => r.status !== 'running').length;
        
        this.state.totalTests = total;
        this.state.completedTests = completed;
        
        if (total > 0) {
            const progress = (completed / total) * 100;
            this.elements.testProgress.classList.remove('hidden');
            this.elements.progressBar.style.width = `${progress}%`;
            this.elements.progressText.textContent = `${completed}/${total} тестов`;
        } else {
            this.elements.testProgress.classList.add('hidden');
        }
    }

    // Фильтрация результатов
    getFilteredResults() {
        return Array.from(this.results.values()).filter(result => {
            const matchesStatus = this.filters.status === 'all' || result.status === this.filters.status;
            const matchesSearch = !this.filters.search || 
                result.name.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                (result.error && result.error.toLowerCase().includes(this.filters.search.toLowerCase()));
            return matchesStatus && matchesSearch;
        });
    }

    handleSearchInput(event) {
        this.filters.search = event.target.value;
        this.updateUI();
    }

    handleStatusFilterChange(event) {
        this.filters.status = event.target.value;
        this.updateUI();
    }

    handleReload() {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'reload' }));
            this.elements.reloadButton.classList.add('loading');
            setTimeout(() => {
                this.elements.reloadButton.classList.remove('loading');
            }, 1000);
        }
    }

    // Уведомления
    notify(message, type = 'info') {
        if (!this.elements.notification) return;

        this.elements.notification.className = `notification ${type}`;
        this.elements.notificationMessage.textContent = message;
        this.elements.notification.classList.remove('hidden');

        if (this.notificationTimeout) {
            clearTimeout(this.notificationTimeout);
        }

        this.notificationTimeout = setTimeout(() => {
            this.hideNotification();
        }, this.config.notificationTimeout);
    }

    hideNotification() {
        if (!this.elements.notification) return;
        this.elements.notification.classList.add('hidden');
    }

    // Ленивая загрузка результатов
    initializeIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '20px',
            threshold: 0.1
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    this.loadResultDetails(element);
                    this.observer.unobserve(element);
                }
            });
        }, options);
    }

    loadResultDetails(element) {
        const resultId = element.getAttribute('data-id');
        const result = this.results.get(resultId);
        
        if (result && !element.classList.contains('loaded')) {
            this.ws.send(JSON.stringify({
                type: 'get_details',
                id: resultId
            }));
            element.classList.add('loaded');
        }
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    logWithTimestamp('LiveUpdateClient: Загрузка страницы завершена');
    window.testResults = new LiveUpdateClient();
});