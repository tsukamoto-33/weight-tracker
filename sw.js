const CACHE_NAME = 'weight-tracker-v1'; // バージョンアップ時はここをインクリメント（例: v2）
const ASSETS = [
  './',
  './index.html',
  './main.py',
  './manifest.json',
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js',
  'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.asm.js',
  'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide-core.capnp',
  'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.asm.wasm',
  'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/packages.json'
];

// インストール時にキャッシュを生成
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Caching assets');
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

// 古いキャッシュをクリア
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('Removing old cache', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// オフライン時のリクエスト処理（キャッシュ優先）
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      return cachedResponse || fetch(event.request);
    })
  );
});