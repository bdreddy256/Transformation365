const CACHE_NAME = 'countdown-timer-pwa-v1';
const assetsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    '/icon.png'
];

// Install Service Worker and Cache Files
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Caching app assets');
                return cache.addAll(assetsToCache);
            })
    );
});

// Fetch Cached Assets
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});

// Activate Service Worker and Clear Old Caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => 
            Promise.all(
                cacheNames.filter(cache => cache !== CACHE_NAME)
                          .map(cache => caches.delete(cache))
            )
        )
    );
});
