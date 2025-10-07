const CACHE_NAME = 'medibot-ai-v2.0.0';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/enhanced-chat.js',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
  'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
  'https://code.jquery.com/jquery-3.7.1.min.js'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Caching MediBot resources');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('❌ Cache installation failed:', error);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }

        // For API calls, always try network first
        if (event.request.url.includes('/get') || event.request.url.includes('/feedback')) {
          return fetch(event.request);
        }

        return fetch(event.request);
      })
      .catch(() => {
        // If both cache and network fail, return offline page for navigation requests
        if (event.request.mode === 'navigate') {
          return new Response(`
            <!DOCTYPE html>
            <html>
            <head>
              <title>MediBot AI - Offline</title>
              <style>
                body { font-family: 'Inter', sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .offline-container { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); }
                .pulse { animation: pulse 2s ease-in-out infinite alternate; }
                @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); } }
              </style>
            </head>
            <body>
              <div class="offline-container">
                <div class="pulse">🏥</div>
                <h1>MediBot AI</h1>
                <h3>You're currently offline</h3>
                <p>Please check your internet connection to use MediBot AI.</p>
                <button onclick="window.location.reload()" style="padding: 10px 20px; border: none; border-radius: 25px; background: white; color: #667eea; font-weight: bold; cursor: pointer;">
                  Try Again
                </button>
              </div>
            </body>
            </html>
          `, {
            headers: { 'Content-Type': 'text/html' }
          });
        }
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Handle background sync (for future offline functionality)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('🔄 Background sync triggered');
    // Handle offline actions when back online
  }
});

// Handle push notifications (for future notification features)
self.addEventListener('push', (event) => {
  if (event.data) {
    const options = {
      body: event.data.text(),
      icon: '/static/icon-192x192.png',
      badge: '/static/badge-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: 1
      }
    };

    event.waitUntil(
      self.registration.showNotification('MediBot AI', options)
    );
  }
});
