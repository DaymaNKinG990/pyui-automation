const CACHE_NAME = 'windsurf-test-results-v1.0.0';
const ASSETS = [
    '/',
    '/assets/css/live-update.css',
    '/assets/js/live-update.js',
    '/assets/icons/favicon-32x32.png'
];

// Установка service worker и кэширование статических ресурсов
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS))
            .then(() => self.skipWaiting())
    );
});

// Активация и очистка старых кэшей
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(name => name !== CACHE_NAME)
                        .map(name => caches.delete(name))
                );
            })
            .then(() => self.clients.claim())
    );
});

// Стратегия кэширования: сначала кэш, потом сеть
self.addEventListener('fetch', event => {
    // Пропускаем запросы к API
    if (event.request.url.includes('/result')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }

                // Клонируем запрос, так как он может быть использован только один раз
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest).then(response => {
                    // Проверяем валидность ответа
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Клонируем ответ, так как он может быть использован только один раз
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                });
            })
    );
});
