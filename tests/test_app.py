"""UI regression checks with an isolated in-memory Supabase fixture.

Run: python tests/test_app.py
Requires Python Playwright and Microsoft Edge (or Playwright Chromium).
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse
import tempfile

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def check_travel(page):
    depart=page.evaluate('addDays(today(),60)')
    arrive=page.evaluate('addDays(today(),61)')
    checkout=page.evaluate('addDays(today(),64)')
    page.evaluate("document.getElementById('importDlg').close()")
    page.locator('#moreLabel').click()
    page.locator('[data-k="journey"]').click()
    expect(page.locator('#moreMenu')).not_to_have_attribute('open', '')
    expect(page.locator('#moreLabel')).to_contain_text('☰ Ferðin')
    page.get_by_role('button',name='+ Flug',exact=True).click()
    page.locator('#title').fill('Outbound flight')
    page.locator('#date').fill(depart)
    page.locator('#time').fill('22:30')
    page.locator('#travelFrom').fill('KEF')
    page.locator('#travelTo').fill('ADB')
    page.locator('#travelCompany').fill('Airline')
    page.locator('#travelService').fill('AB123')
    page.locator('#travelReference').fill('FLIGHT-REF')
    page.locator('#endDate').fill(arrive)
    page.locator('#endTime').fill('06:00')
    page.get_by_role('button',name='Vista',exact=True).click()
    expect(page.locator('#formDlg')).not_to_be_visible()
    expect(page.locator('#content')).to_contain_text('FLIGHT-REF')
    page.get_by_role('button',name='Outbound flight',exact=True).click()
    expect(page.locator('#eventContent')).to_contain_text('AB123')
    expect(page.locator('#eventContent')).to_contain_text('KEF')
    expect(page.locator('#eventContent')).to_contain_text('ADB')
    expect(page.locator('#eventContent .calendar-link')).to_have_count(0)
    page.locator('#eventDlg').get_by_role('button',name='Breyta',exact=True).click()
    expect(page.locator('#endTime')).to_have_value('06:00')
    expect(page.locator('#travelFrom')).to_have_value('KEF')
    page.locator('#travelReference').fill('UPDATED-REF')
    page.get_by_role('button',name='Vista',exact=True).click()
    expect(page.locator('#formDlg')).not_to_be_visible()
    expect(page.locator('#content')).to_contain_text('UPDATED-REF')

    page.get_by_role('button',name='+ Samgöngur',exact=True).click()
    page.locator('#title').fill('Airport transfer')
    page.locator('#date').fill(arrive)
    page.locator('#time').fill('07:00')
    page.locator('#travelFrom').fill('Airport')
    page.locator('#travelTo').fill('Hotel')
    page.locator('#travelService').fill('Bus')
    page.get_by_role('button',name='Vista',exact=True).click()
    expect(page.locator('#formDlg')).not_to_be_visible()

    page.get_by_role('button',name='+ Gisting',exact=True).click()
    page.locator('#title').fill('Holiday hotel')
    page.locator('#date').fill(arrive)
    page.locator('#time').fill('14:00')
    page.locator('#travelAddress').fill('Hotel street 1')
    page.locator('#travelReference').fill('HOTEL-REF')
    expect(page.locator('#routeFields')).not_to_be_visible()
    page.locator('#endDate').fill(depart)
    page.get_by_role('button',name='Vista',exact=True).click()
    expect(page.locator('#formDlg')).to_be_visible()
    assert not page.evaluate('testDB.items.some(x=>x.title==="Holiday hotel")')
    page.locator('#endDate').fill(checkout)
    page.locator('#endTime').fill('11:00')
    page.get_by_role('button',name='Vista',exact=True).click()
    expect(page.locator('#formDlg')).not_to_be_visible()
    expect(page.locator('.journey-card')).to_have_count(3)
    expect(page.locator('#content')).to_contain_text('Hotel street 1')
    expect(page.locator('#content')).to_contain_text('HOTEL-REF')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(Path(tempfile.gettempdir())/'travelapp-journey-mobile.png'),full_page=True)

    page.evaluate("tab='today';dayOffset=61;render()")
    expect(page.locator('.event-title')).to_have_text(['Outbound flight','Airport transfer','Holiday hotel'])
    expect(page.locator('.event-time').first).to_have_text('06:00')
    page.evaluate('dayOffset=62;render()')
    expect(page.locator('.event-title')).to_have_text(['Holiday hotel'])
    expect(page.locator('.event-time')).to_have_count(0)
    page.evaluate('dayOffset=64;render()')
    expect(page.locator('.event-title')).to_have_text(['Holiday hotel'])
    expect(page.locator('.event-time')).to_have_text('11:00')
    page.evaluate('dayOffset=65;render()')
    expect(page.locator('.event-title')).to_have_count(0)

    page.evaluate('testMissingTravel=true;newEntity("flight")')
    page.locator('#title').fill('Missing migration')
    alerts=[]
    page.once('dialog',lambda dialog:(alerts.append(dialog.message),dialog.accept()))
    page.get_by_role('button',name='Vista',exact=True).click()
    expect(page.locator('#formDlg')).to_be_visible()
    assert alerts and '002_travel_details.sql' in alerts[0]
    assert not page.evaluate('testDB.items.some(x=>x.title==="Missing migration")')
    page.get_by_role('button',name='Hætta við',exact=True).click()
    page.evaluate('testMissingTravel=false')


def run():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel='msedge')
            except Exception:
                browser = p.chromium.launch()
            context = browser.new_context(viewport={'width':390,'height':844}, service_workers='block')
            context.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            context.add_init_script(path=str(ROOT/'tests/mock-supabase.js'))
            page = context.new_page()
            errors=[]
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(origin)
            expect(page.locator('#sync')).to_have_text('● Samstillt')
            expect(page.locator('#tabs button')).to_have_text(['Dagsplan','Hugmyndir','Heildarplan'])
            expect(page.locator('[data-k="journey"]')).to_be_hidden()
            expect(page.locator('[data-k="shopping"]')).to_be_hidden()
            page.locator('[data-k="plans"]').click()
            expect(page.locator('.event-title')).to_have_text(['Morning event','Evening event','Unscheduled time','Tomorrow event'])
            expect(page.locator('#content h2')).to_have_count(2)
            page.locator('[data-k="today"]').click()
            expect(page.locator('.event-title')).to_have_text(['Morning event','Evening event','Unscheduled time'])
            expect(page.locator('[data-k="shopping"] .count')).to_have_text('2')
            expect(page.locator('#moreLabel .count')).to_have_text('2')
            expect(page.locator('#content .actions')).to_have_count(0)
            expect(page.locator('#content')).not_to_contain_text('Milk')
            expect(page.locator('.event-details').first).to_be_hidden()
            page.locator('.expand').first.click()
            expect(page.locator('.event-details').first).to_be_visible()
            page.evaluate('render()')
            expect(page.locator('.expand').first).to_have_attribute('aria-expanded','true')
            assert page.locator('.event-row').first.bounding_box()['height'] <= 42
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            screenshot=Path(tempfile.gettempdir())/'travelapp-v2-5-mobile.png'
            page.screenshot(path=str(screenshot),full_page=True)

            page.get_by_role('button', name='Sjá næsta dag', exact=True).click()
            expect(page.locator('.event-title')).to_have_text(['Tomorrow event'])
            for _ in range(35):
                page.get_by_role('button', name='Sjá næsta dag', exact=True).click()
            expect(page.locator('.empty')).to_have_text('Ekkert plan þennan dag.')
            page.get_by_role('button',name='Aftur í dag').click()
            page.locator('.event-title').first.click()
            expect(page.locator('#eventTitle')).to_have_text('Morning event')
            params=parse_qs(urlparse(page.locator('.calendar-link').get_attribute('href')).query)
            assert params['ctz']==['Europe/Istanbul']
            assert params['dates'][0].split('/')[0].endswith('T090000')
            assert params['dates'][0].split('/')[1].endswith('T100000')
            page.locator('#eventDlg').get_by_role('button',name='Breyta',exact=True).click()
            page.locator('#time').fill('10:15')
            page.locator('#formDlg').get_by_role('button',name='Vista',exact=True).click()
            expect(page.locator('#formDlg')).not_to_be_visible()
            expect(page.locator('.event-time').first).to_have_text('10:15')

            page.locator('[data-k="ideas"]').click()
            expect(page.locator('.event-title')).to_have_text(['Existing idea'])
            page.locator('.event-title').click()
            page.get_by_role('button',name='Setja á plan',exact=True).click()
            expect(page.locator('#itemMode')).to_have_value('planned')
            expect(page.locator('.link-row .lu')).to_have_value('https://maps.google.com/')
            page.locator('#time').fill('08:30')
            page.get_by_role('button',name='Vista',exact=True).click()
            expect(page.locator('#formDlg')).not_to_be_visible()
            expect(page.locator('.event-title')).to_have_count(0)
            page.locator('[data-k="today"]').click()
            expect(page.locator('.event-title').first).to_have_text('Existing idea')
            page.locator('.event-title').first.click()
            page.locator('#eventDlg').get_by_role('button',name='Breyta',exact=True).click()
            page.locator('#itemMode').select_option('idea')
            page.get_by_role('button',name='Vista',exact=True).click()
            expect(page.locator('#formDlg')).not_to_be_visible()
            assert page.evaluate('testDB.items.find(x=>x.id===3).planned_time') is None

            page.locator('#add').click()
            page.locator('[data-new="idea"]').click()
            expect(page.locator('#date')).to_be_disabled()
            page.locator('#title').fill('New idea')
            page.get_by_role('button',name='Vista',exact=True).click()
            expect(page.locator('#formDlg')).not_to_be_visible()
            page.locator('[data-k="ideas"]').click()
            expect(page.locator('.event-title')).to_have_text(['Existing idea','New idea'])
            page.locator('.event-title').last.click()
            page.once('dialog',lambda dialog:dialog.dismiss())
            page.locator('#eventDlg').get_by_role('button',name='Eyða',exact=True).click()
            expect(page.locator('#eventDlg')).to_be_visible()
            page.once('dialog',lambda dialog:dialog.accept())
            page.locator('#eventDlg').get_by_role('button',name='Eyða',exact=True).click()
            expect(page.locator('#eventDlg')).not_to_be_visible()
            expect(page.locator('.event-title')).to_have_count(1)

            page.locator('#moreLabel').click()
            page.locator('[data-k="shopping"]').click()
            expect(page.locator('#moreLabel')).to_contain_text('☰ Innkaup')
            expect(page.locator('[data-k="journey"]')).to_be_hidden()
            page.locator('#content .card').click()
            page.locator('.card').filter(has=page.get_by_text('Milk',exact=True)).locator('.check').click()
            expect(page.locator('[data-k="shopping"] .count')).to_have_text('1')
            expect(page.locator('#moreLabel .count')).to_have_text('1')
            assert page.evaluate("testDB.shopping_items.find(x=>x.id==='milk').next_due_date === addDays(today(),2)")
            page.locator('.card').filter(has=page.get_by_text('Bread',exact=True)).locator('.check').click()
            expect(page.locator('[data-k="shopping"] .count')).to_have_count(0)
            expect(page.locator('#moreLabel .count')).to_have_count(0)
            page.evaluate("testDB.shopping_items.find(x=>x.id==='milk').next_due_date=today();refresh()")
            expect(page.locator('[data-k="shopping"] .count')).to_have_text('1')
            expect(page.locator('#moreLabel .count')).to_have_text('1')

            page.evaluate("localStorage.setItem('travelapp_pending_share', JSON.stringify({title:'Shared place',text:'Look https://maps.google.com/',url:''}));handleShare()")
            expect(page.locator('#itemMode')).to_have_value('idea')
            expect(page.locator('#date')).to_be_disabled()
            expect(page.locator('.link-row .lu')).to_have_value('https://maps.google.com/')
            page.get_by_role('button',name='Hætta við',exact=True).click()

            page.evaluate('newEntity("item");testMissingTime=true')
            page.locator('#title').fill('Schema failure')
            page.locator('#time').fill('12:00')
            alerts=[]
            page.once('dialog',lambda dialog:(alerts.append(dialog.message),dialog.accept()))
            page.get_by_role('button',name='Vista',exact=True).click()
            expect(page.locator('#formDlg')).to_be_visible()
            assert alerts and '001_planned_time.sql' in alerts[0]
            assert not page.evaluate('testDB.items.some(x=>x.title==="Schema failure")')
            page.get_by_role('button',name='Hætta við',exact=True).click()
            page.evaluate('testMissingTime=false')

            # Existing databases work for ideas and untimed events without the migration.
            page.evaluate('for(const x of testDB.items)delete x.planned_time;newEntity("idea")')
            page.locator('#title').fill('Legacy schema idea')
            page.get_by_role('button',name='Vista',exact=True).click()
            expect(page.locator('#formDlg')).not_to_be_visible()
            assert page.evaluate('testDB.items.some(x=>x.title==="Legacy schema idea" && x.planned_date===null)')

            # Imports preserve times and can explicitly supply ideas.
            page.evaluate('openJsonImport()')
            page.locator('#jsonText').fill('{"ideas":[{"title":"Imported idea"}],"items":[{"title":"Imported plan","date":"tomorrow","time":"11:20"}]}')
            page.locator('#jsonPreview').click()
            expect(page.locator('#jsonImport')).to_be_enabled()
            page.locator('#jsonImport').click()
            page.wait_for_function('testDB.items.some(x=>x.title==="Imported plan" && x.planned_time==="11:20")')
            assert page.evaluate('testDB.items.some(x=>x.title==="Imported idea" && x.planned_date===null)')
            check_travel(page)
            assert page.evaluate('addDays("2026-12-31",1)')=='2027-01-01'
            assert page.evaluate('addDays("2028-02-28",1)')=='2028-02-29'
            assert errors==[], errors

            # App-shell update and offline caching, with real service workers.
            shell_context = browser.new_context(service_workers='allow')
            shell_context.add_init_script(path=str(ROOT/'tests/mock-supabase.js'))
            shell_page = shell_context.new_page()
            shell_page.goto(origin)
            shell_page.evaluate('navigator.serviceWorker.ready')
            shell_page.wait_for_function('navigator.serviceWorker.controller !== null')
            assert shell_page.evaluate('caches.keys()')==['travelapp-v2-5']
            shell_context.set_offline(True)
            shell_page.reload()
            expect(shell_page.locator('#sync')).to_have_text('● Samstillt')
            expect(shell_page.locator('.event-title')).to_have_count(3)
            shell_context.close()
            browser.close()
            print('PASS: days, ideas, times, shopping recurrence, share, imports, migration fallback, mobile layout, flights, transport, lodging, PWA shell cache.')
            print('Mobile screenshot:',screenshot)
    finally:
        server.shutdown()
        server.server_close()


if __name__=='__main__':
    run()
