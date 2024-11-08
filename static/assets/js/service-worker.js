const CACHE_NAME = 'jr-catering-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/assets/css/style.css',
    '/static/assets/js/script.js',
    '/static/assets/images/img1.webp',
    // Add other critical assets
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS_TO_CACHE))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
}); 