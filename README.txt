TYRKLAND — DAÐI & KATA PWA v2.5

BREYTINGAR
- Aðalfliparnir eru Dagsplan, Hugmyndir og Heildarplan. Heildarplan er í tímaröð eftir degi og klukku, með dagsetningar fyrirsögnum.
- Ferðin, Innkaup, Stjörnumerkt og Memó eru í sérvalmynd.
- „Ferðin“ hefur yfirlit fyrir flug, samgöngur og gistingu fyrir alla ferðina, líka langt fram í tímann.
- Bókanir geyma brottför/innritun og komu/útritun, staði, heimilisfang, þjónustuaðila, flugnúmer/leið og bókunarnúmer. Athugasemdir og slóðir eru áfram í boði.
- Flug og samgöngur birtast á brottfarar- og komudegi í dagsplani. Gisting birtist alla daga frá innritun til útritunar, með útritunartíma síðasta daginn.
- Tímar bókana eru staðartímar á hvorum stað og eru ekki umbreyttir í eitt tímabelti. Dagatalstengillinn er því aðeins sýndur fyrir venjulega viðburði.
- Hugmyndir eru atriði án planned_date. Eldri ódagsett atriði birtast þar líka.
- Smelltu á heiti hugmyndar og veldu „Setja á plan“ til að velja dag og klukku.
- Staðan í breytingaglugganum leyfir líka að færa plan aftur í hugmyndir.
- Dagsplan á forsíðu hefur fyrri/næsta dag og „Aftur í dag“, án takmarks á dagafjölda.
- Innkaup eru í sérvalmynd. Rauð tala sýnir ókeypt og endurtekin atriði sem eru komin á tíma miðað við daginn í dag, óháð hvaða dagsplan er skoðað.
- Þéttar viðburðalínur hafa ör fyrir nánari upplýsingar. Heitið opnar allan viðburðinn; Breyta og Eyða eru þar inni.
- Klukka er valkvæð. Venjulegir viðburðir miðast við staðartíma í Tyrklandi (Europe/Istanbul). Tímasett atriði raðast eftir klukku; ótímasett fara aftast.
- Deilt efni úr öðrum öppum opnast sem ný hugmynd áður en það er vistað.
- JSON styður ideas, status: "idea", time/planned_time á forminu HH:MM og travel_details fyrir bókanir (sjá dæmi neðar).

UPPFÆRSLA Á NÚVERANDI UPPSETNINGU
1. Keyrðu migrations/001_planned_time.sql og síðan migrations/002_travel_details.sql í Supabase SQL Editor. Skrárnar má keyra oftar en einu sinni.
2. Birttu index.html og sw.js ásamt núverandi manifest.webmanifest, share.html, táknum og vendor/ á sömu HTTPS slóð og áður.
3. Opnaðu appið með nettengingu. Nýtt service-worker skyndiminni heitir travelapp-v2-5.

SQL skrefið þarf að framkvæma í Supabase; það er ekki keyrt af appinu. Eldri viðburðir virka án þess, en vistun klukku og bókunarupplýsinga sýnir skýr skilaboð ef nýju dálkana vantar. Innskráning, aðild og RLS-reglur núverandi Supabase verkefnis eru áfram notaðar. Þessi kóðageymsla inniheldur ekki grunnuppsetningu gagnagrunnsins eða raunverulegan boðskóða ferðarinnar. IZMIR-… í innskráningarglugganum er aðeins dæmi.

DÆMI UM JSON BÓKUN
{
  "travelapp": 1,
  "items": [{
    "title": "Flug til Izmir",
    "category": "flug",
    "date": "2026-10-10",
    "time": "22:30",
    "travel_details": {
      "kind": "flight",
      "from": "KEF",
      "to": "ADB",
      "company": "Flugfélag",
      "service": "AB123",
      "reference": "BÓKUNARNÚMER",
      "end_date": "2026-10-11",
      "end_time": "06:00"
    }
  }]
}

kind má vera flight, transport eða stay. Gisting notar address í stað from/to. Fyrir gistingu eru date/time innritun og end_date/end_time útritun. Þetta er aðeins dæmi, ekki raunverulegar bókunarupplýsingar.

ÁMINNINGAR
Tímasettur viðburður hefur „Opna í Google Calendar“. Það opnar tillögu; notandinn velur áminningu og vistar viðburðinn þar. Tillagan er ein klukkustund og lengd má breyta í dagatalinu. Dagatalsfærslan er afrit og samstillist ekki við síðari breytingar í appinu.

Appið sendir ekki eigin bakgrunnsáminningar. Áreiðanlegar tilkynningar þegar appið er lokað þurfa Push API, samþykki notanda, geymdar push-áskriftir og bakenda/tímaþjónustu sem sendir tilkynningar. JavaScript-tími í opnu appi tryggir ekki slíkar áminningar.
https://developer.mozilla.org/en-US/docs/Web/API/Push_API

DEILA Í APP Á ANDROID
Manifest hefur þegar share_target fyrir share.html. Heitið í Android deilingarvalmynd kemur úr manifest og er nú „Tyrkland“ / „Tyrkland — Daði & Kata“.

Chrome á Android getur uppfært WebAPK skráninguna sjálfkrafa; enduruppsetning er yfirleitt óþörf. Opnaðu appið með neti, lokaðu því svo og leyfðu uppfærslu á Wi-Fi með síma í hleðslu. Þetta getur tekið einn eða tvo daga.

Ef deilingarvalkosturinn vantar: í Chrome má opna chrome://webapks og velja Update fyrir appið ef það er í boði. Ef appið er aðeins flýtileið á heimaskjá, settu það upp sem app úr Chrome. Enduruppsetning úr Chrome er síðari úrræði ef skráning endurnýjast ekki.
https://web.dev/articles/manifest-updates
https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/share_target

SAMSTILLING OG OFFLINE
Gögn eru lesin úr Supabase á 15 sekúndna fresti og þegar appið fær fókus. Service worker geymir appskelina til að geta opnað hana án nets; ferðagögn eru ekki geymd offline. Lestur og breytingar á gögnum þurfa því nettengingu.

PRÓFANIR
python tests/test_app.py

Þarf Python Playwright og Microsoft Edge eða Playwright Chromium. Prófin nota aðskilin prófgögn og senda engar fyrirspurnir í raunverulegan Supabase gagnagrunn.
