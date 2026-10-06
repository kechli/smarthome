const CACHE_NAME = 'smarthome-v2'; // Αλλάξαμε την έκδοση σε v2 για να διαγραφεί η παλιά cache

self.addEventListener('install', (event) => {
  self.skipWaiting(); // Ενεργοποίηση αμέσως
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache); // Διαγραφή παλιάς μνήμης
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});