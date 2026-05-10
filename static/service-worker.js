const CACHE = 'fruity-flicks-v2';
const PRECACHE = [
  '/static/img/logo.jpg',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Stale-while-revalidate for static assets: show cached immediately, fetch in
// background, and update the cache so the next load gets fresh content.
function staleWhileRevalidate(request) {
  return caches.open(CACHE).then((cache) =>
    cache.match(request).then((cached) => {
      const fresh = fetch(request)
        .then((response) => {
          if (response && response.status === 200) cache.put(request, response.clone());
          return response;
        })
        .catch(() => cached);
      return cached || fresh;
    })
  );
}

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;

  if (url.pathname.startsWith('/static/')) {
    e.respondWith(staleWhileRevalidate(e.request));
    return;
  }
  // Network-first for HTML/data so the dashboard always reflects the latest records.
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
