// Service worker: la app funciona sin conexión.
// Estrategia "red primero": si hay internet se usa la versión más nueva
// (las actualizaciones llegan solas); si no, se sirve la copia guardada.
const CACHE = 'gastos-casa-v1';
const ASSETS = ['.', 'index.html', 'manifest.json', 'icon-192.png', 'icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // Solo la propia app y las librerías de Firebase (los datos van aparte, nunca se cachean)
  const cacheable = url.origin === location.origin || url.host === 'www.gstatic.com';
  if (!cacheable) return;
  e.respondWith(
    fetch(e.request).then(r => {
      const copy = r.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return r;
    }).catch(() =>
      caches.match(e.request, { ignoreSearch: true })
        .then(m => m || caches.match('index.html'))
    )
  );
});
