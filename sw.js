const C='travelapp-v2-5';
const A=['./','./index.html','./share.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./vendor/supabase-2.117.2.js'];
const shellURLs=new Set(A.map(path=>new URL(path,self.registration.scope).href));
self.addEventListener('install',e=>e.waitUntil(caches.open(C).then(c=>c.addAll(A)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith('travelapp-')&&x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 const url=new URL(e.request.url);
 // Only the local app shell is cacheable; API/auth and CDN requests pass through.
 if(e.request.method!=='GET'||url.origin!==self.location.origin)return;
 url.search='';
 if(!shellURLs.has(url.href))return;
 e.respondWith((async()=>{
  const cache=await caches.open(C);
  try{
   const response=await fetch(e.request);
   if(response.ok)await cache.put(url.href,response.clone());
   return response;
  }catch(error){
   const cached=await cache.match(url.href);
   if(cached)return cached;
   throw error;
  }
 })());
});
