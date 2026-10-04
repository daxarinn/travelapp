TYRKLAND — DAÐI & KATA PWA v1

INNIHALD
- index.html
- manifest.webmanifest
- sw.js
- icon-192.png
- icon-512.png
- SEED.sql

UPPSETNING
1. Búðu til nýtt GitHub repo, t.d. "tyrkland".
2. Upload-aðu index.html, manifest.webmanifest, sw.js, icon-192.png og icon-512.png í root.
3. Kveiktu á GitHub Pages: Settings > Pages > Deploy from branch > main / root.
4. Í Supabase SQL Editor: keyrðu SEED.sql EINU SINNI.
5. Opnið GitHub Pages slóðina í símunum og veljið Install app / Add to Home screen.

SYNC
- Appið les og skrifar sama Supabase items-table hjá ykkur báðum.
- Það endurles sjálfkrafa á 12 sekúndna fresti og þegar appið fær fókus.
- Síðasta lesna staða er geymd localt svo listinn sé sýnilegur offline.
- Breytingar þurfa net í þessari V1.

ÖRYGGI
- V1 notar publishable/anon key og þær opnu RLS-reglur sem voru settar upp.
- Ekki geyma viðkvæmar persónuupplýsingar í appinu.
- Sá sem fær Project URL + publishable key gæti, samkvæmt núverandi RLS-reglum, lesið/breytt listanum.
