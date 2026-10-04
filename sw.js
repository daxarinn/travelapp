const C='travelapp-v2-1';
const A=['./','./index.html','./share.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(C).then(c=>c.addAll(A)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||e.request.url.includes('supabase.co'))return;e.respondWith(fetch(e.request).then(r=>{const q=r.clone();caches.open(C).then(c=>c.put(e.request,q));return r}).catch(()=>caches.match(e.request)))});
