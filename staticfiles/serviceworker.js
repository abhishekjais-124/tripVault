const CACHE_NAME = 'tripvault-v1';
const BASE_PATH = '/tripvault';

// Assets to cache on install
const urlsToCache = [
  `${BASE_PATH}/`,
  `${BASE_PATH}/plan/`,
  `${BASE_PATH}/saved/`,
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[ServiceWorker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - cache-first strategy with network fallback
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Ignore Django dynamic URLs (do not cache or intercept)
  const dynamicPatterns = [
    /\/expense\/group\/[0-9]+\//,
    /\/expense\/group\/[0-9]+\/expenses\//,
    /\/expense\/group\/[0-9]+\/expenses\//,
    /\/user\//,
    /\/trip\//,
    /\/group\//
  ];
  const urlPath = new URL(event.request.url).pathname;
  if (dynamicPatterns.some((re) => re.test(urlPath))) {
    // Let the network handle these requests
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          console.log('[ServiceWorker] Found in cache:', event.request.url);
          return response;
        }
        const fetchRequest = event.request.clone();
        return fetch(fetchRequest).then((response) => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              if (event.request.method === 'GET') {
                cache.put(event.request, responseToCache);
              }
            });
          return response;
        }).catch((error) => {
          console.log('[ServiceWorker] Fetch failed:', error);
        });
      })
  );
});
