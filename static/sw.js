const CACHE_NAME = 'hill-life-v1.0.0';
const urlsToCache = [
  '/',
  '/static/css/bootstrap.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/chart.min.js',
  '/login',
  '/register',
  '/dashboard',
  '/add_workout',
  '/workouts',
  '/social_feed',
  '/fitness_goals',
  '/manifest.json'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Background sync for offline workout logging
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync-workout') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Handle offline workout submissions when back online
  return new Promise((resolve, reject) => {
    // Implementation for syncing offline data
    console.log('Background sync triggered');
    resolve();
  });
}

// Push notifications for workout reminders
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'Time to reach your pinnacle!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'log-workout',
        title: 'Log Adventure',
        icon: '/static/icons/action-log.png'
      },
      {
        action: 'view-progress',
        title: 'View Progress',
        icon: '/static/icons/action-progress.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Hill Life', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'log-workout') {
    event.waitUntil(
      clients.openWindow('/add_workout')
    );
  } else if (event.action === 'view-progress') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  } else {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});
