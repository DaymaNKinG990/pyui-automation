class TestResultsManager {
    constructor() {
        this.results = new Map();
        this.summaryStats = {
            total: 0,
            passed: 0,
            failed: 0,
            skipped: 0,
            duration: 0
        };
        this.setupWebSocket();
        this.setupDOMElements();
    }

    setupDOMElements() {
        this.resultsContainer = document.getElementById('test-results');
        this.summaryContainer = document.getElementById('summary');
        if (!this.resultsContainer || !this.summaryContainer) {
            console.error('Required DOM elements not found');
            return;
        }
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connection established');
            this.updateConnectionStatus(true);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.updateConnectionStatus(false);
            // Попытка переподключения через 5 секунд
            setTimeout(() => this.setupWebSocket(), 5000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus(false);
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'test_update') {
                    this.handleTestUpdate(data);
                } else if (data.type === 'suite_complete') {
                    this.handleSuiteComplete(data);
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        };
    }

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.textContent = connected ? 'Connected' : 'Disconnected';
            statusEl.className = connected ? 'status-passed' : 'status-failed';
        }
    }

    handleTestUpdate(data) {
        const { test_id, name, status, duration, error } = data;
        
        this.results.set(test_id, {
            name,
            status,
            duration,
            error
        });

        this.updateTestDisplay(test_id);
        this.updateSummary();
    }

    handleSuiteComplete(data) {
        this.summaryStats = data.summary;
        this.updateSummary();
    }

    updateTestDisplay(testId) {
        const test = this.results.get(testId);
        if (!test) return;

        let testEl = document.getElementById(`test-${testId}`);
        if (!testEl) {
            testEl = document.createElement('div');
            testEl.id = `test-${testId}`;
            testEl.className = 'test-card';
            this.resultsContainer.appendChild(testEl);
        }

        testEl.innerHTML = `
            <div class="test-status status-${test.status.toLowerCase()}">${test.status}</div>
            <h3>${test.name}</h3>
            <div class="test-details">
                <div class="test-time">Duration: ${test.duration.toFixed(2)}s</div>
                ${test.error ? `<div class="error-details">${test.error}</div>` : ''}
            </div>
        `;
    }

    updateSummary() {
        this.summaryContainer.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-label">Total Tests</div>
                    <div class="summary-value">${this.summaryStats.total}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Passed</div>
                    <div class="summary-value">${this.summaryStats.passed}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Failed</div>
                    <div class="summary-value">${this.summaryStats.failed}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Skipped</div>
                    <div class="summary-value">${this.summaryStats.skipped}</div>
                </div>
                <div class="summary-item">
                    <div class="summary-label">Duration</div>
                    <div class="summary-value">${this.summaryStats.duration.toFixed(2)}s</div>
                </div>
            </div>
        `;
    }
}

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    window.testManager = new TestResultsManager();
});
