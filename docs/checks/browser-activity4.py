"""Pruebas de navegador opcionales: usa Playwright si ya está instalado.
No instala dependencias. Sirve los archivos locales bajo el prefijo de Pages,
sin API ni servidor externo. Capturas nuevas en /tmp/continuity-activity4/.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import unittest
from playwright.sync_api import sync_playwright

DOCS = Path(__file__).resolve().parents[1]
BASE = 'http://continuity.test/spartan-01-continuity/'
KEY = 'DemoContinuitY12!'


class Activity4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1000})
        self.page = self.context.new_page()
        self.errors, self.missing = [], []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.context.route('**/*', self.serve)
        self.page.goto(BASE + '#requisitos/RF01/E')
        self.page.locator('#demo-auth').wait_for()

    def serve(self, route):
        path = unquote(urlsplit(route.request.url).path)
        prefix = '/spartan-01-continuity/'
        target = (DOCS / (path[len(prefix):] or 'index.html')).resolve()
        if not path.startswith(prefix) or not target.is_relative_to(DOCS) or not target.is_file():
            self.missing.append(path)
            route.abort()
        else:
            route.fulfill(path=str(target))

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(self.missing, [])
        self.context.close()

    def click(self, selector):
        self.page.locator(selector).click()

    def auth(self, email='a@example.test', password=KEY):
        self.page.locator('#demo-email').fill(email)
        self.page.locator('#demo-password').fill(password)

    def register(self, email='a@example.test', name='Persona ficticia'):
        self.click('#tab-register')
        self.page.locator('#demo-name').fill(name)
        self.auth(email)
        self.page.locator('#demo-confirm').fill(KEY)
        self.click('#demo-auth button[type=submit]')
        self.assertIn('Cuenta creada correctamente', self.page.locator('#demo-feedback').inner_text())

    def login(self, email='a@example.test'):
        self.auth(email)
        self.click('#demo-auth button[type=submit]')
        self.page.locator('#demo-logout').wait_for()

    def company(self, name='Empresa ficticia'):
        self.click('#demo-show-company')
        self.page.locator('#company-name').fill(name)
        self.page.locator('#company-city').fill('Bogotá')
        self.click('#demo-company button[type=submit]')
        self.page.locator('#company-value-name').wait_for()

    def test_01_full_flow_isolation_and_private_views(self):
        self.assertEqual(self.page.locator('#demo-logout').count(), 0)
        self.register()
        self.login()
        self.assertEqual(self.page.locator('#demo-account-email').inner_text(), 'a@example.test')
        self.company()
        self.assertEqual(self.page.locator('#demo-company').count(), 0)
        self.click('#demo-back')
        self.click('#demo-show-company')
        self.assertEqual(self.page.locator('#company-value-name').inner_text(), 'Empresa ficticia')
        self.click('#demo-logout')
        self.assertEqual(self.page.locator('#demo-company-panel').count(), 0)
        self.register('b@example.test')
        self.login('b@example.test')
        self.click('#demo-show-company')
        self.assertEqual(self.page.locator('#demo-company').count(), 1)
        self.click('#demo-logout')
        self.login()
        self.click('#demo-show-company')
        self.assertEqual(self.page.locator('#company-value-name').inner_text(), 'Empresa ficticia')
        self.assertEqual(self.page.evaluate('localStorage.length + sessionStorage.length'), 0)
        self.page.reload()
        self.assertEqual(self.page.locator('#demo-logout').count(), 0)
        self.auth()
        self.click('#demo-auth button[type=submit]')
        self.assertIn('incorrectos', self.page.locator('#demo-feedback').inner_text())

    def test_02_registration_and_login_errors(self):
        self.click('#tab-register')
        self.click('#demo-auth button[type=submit]')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'demo-name')
        self.page.locator('#demo-name').fill('   ')
        self.auth()
        self.page.locator('#demo-confirm').fill(KEY)
        self.click('#demo-auth button[type=submit]')
        self.assertIn('nombre ficticio', self.page.locator('#demo-feedback').inner_text())
        self.page.locator('#demo-name').fill('Demo')
        self.page.locator('#demo-email').fill('no-es-correo')
        self.click('#demo-auth button[type=submit]')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'demo-email')
        self.auth()
        self.page.locator('#demo-password').fill('corta')
        self.click('#demo-auth button[type=submit]')
        self.assertIn('12 y 1024', self.page.locator('#demo-feedback').inner_text())
        self.auth()
        self.page.locator('#demo-confirm').fill('distinta')
        self.click('#demo-auth button[type=submit]')
        self.assertIn('coincidir', self.page.locator('#demo-feedback').inner_text())
        self.page.locator('#demo-confirm').fill(KEY)
        self.click('#demo-auth button[type=submit]')
        self.click('#tab-register')
        self.page.locator('#demo-name').fill('Demo')
        self.auth('A@EXAMPLE.TEST')
        self.page.locator('#demo-confirm').fill(KEY)
        self.click('#demo-auth button[type=submit]')
        self.assertIn('ya está registrado', self.page.locator('#demo-feedback').inner_text())
        self.click('#tab-login')
        self.auth(password='incorrecta')
        self.click('#demo-auth button[type=submit]')
        self.assertIn('incorrectos', self.page.locator('#demo-feedback').inner_text())
        self.assertEqual(self.page.locator('#demo-logout').count(), 0)

    def test_03_company_constraints_and_safe_text(self):
        self.register(name='<img src=x onerror=alert(1)>')
        self.login()
        self.assertIn('<img', self.page.locator('#demo-account-name').inner_text())
        self.click('#demo-show-company')
        self.click('#demo-company button[type=submit]')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'company-name')
        self.page.locator('#company-name').fill('   ')
        self.page.locator('#company-city').fill('Cali')
        self.click('#demo-company button[type=submit]')
        self.assertIn('nombre', self.page.locator('#demo-feedback').inner_text())
        for field, limit in [('name',150),('city',100),('nit',20),('sector',100)]:
            node = self.page.locator('#company-'+field)
            self.assertEqual(node.get_attribute('maxlength'), str(limit))
            node.evaluate('(el,n) => el.value="x".repeat(n)', limit+1)
            self.click('#demo-company button[type=submit]')
            self.assertIn({'name':'nombre','city':'ciudad','nit':'nit','sector':'sector'}[field], self.page.locator('#demo-feedback').inner_text())
            node.fill('Cali' if field == 'city' else ('Demo' if field == 'name' else ''))
        self.page.locator('#company-name').fill('<svg onload=alert(1)>')
        self.click('#demo-company button[type=submit]')
        self.assertEqual(self.page.locator('#company-value-name').inner_text(), '<svg onload=alert(1)>')
        self.assertEqual(self.page.locator('#company-value-nit').inner_text(), 'No informado')
        self.assertEqual(self.page.locator('#company-value-sector').inner_text(), 'No informado')
        self.assertEqual(self.page.locator('.prototype img,.prototype svg').count(), 0)

    def test_04_responsive_all_views(self):
        def check(view):
            for width in [320,375,768,1024,1440]:
                self.page.set_viewport_size({'width':width,'height':1000})
                self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (view,width))
                if view == 'login':
                    self.assertEqual(self.page.locator('.prototype .screen-title .highlight').evaluate('(el) => el.getClientRects().length'), 1, ('Palabra infraestructura fragmentada', width))
                for node in self.page.locator('.prototype input, .prototype button').all():
                    box = node.bounding_box()
                    self.assertGreaterEqual(box['x'], 0)
                    self.assertLessEqual(box['x']+box['width'], width)
                if width in [375,1440]:
                    folder = Path('/tmp/continuity-activity4')
                    folder.mkdir(exist_ok=True)
                    self.page.locator('.prototype').screenshot(path=str(folder/f'{view}-{width}.png'))
        check('login')
        self.click('#tab-register')
        check('register')
        self.click('#tab-login')
        self.register()
        self.login()
        check('access')
        self.click('#demo-show-company')
        check('company-form')
        self.page.locator('#company-name').fill('Empresa ficticia')
        self.page.locator('#company-city').fill('Bogotá')
        self.click('#demo-company button[type=submit]')
        check('company-details')

    def test_05_keyboard_labels_focus_and_academic_navigation(self):
        self.page.locator('#demo-email').focus()
        self.page.keyboard.press('Tab')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'demo-password')
        self.page.keyboard.press('Tab')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'demo-visibility')
        self.page.keyboard.press('Enter')
        self.assertEqual(self.page.locator('#demo-password').get_attribute('type'), 'text')
        self.assertEqual(self.page.locator('#demo-visibility').get_attribute('aria-pressed'), 'true')
        self.page.keyboard.press('Enter')
        self.assertEqual(self.page.locator('#demo-password').get_attribute('type'), 'password')
        self.click('#tab-register')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'demo-title')
        for node in self.page.locator('.prototype input').all():
            self.assertEqual(self.page.locator('label[for="'+node.get_attribute('id')+'"]').count(), 1)
        self.assertEqual(self.page.locator('#demo-feedback').get_attribute('aria-live'), 'polite')
        for rf in ['RF01','RF02']:
            for part in 'ABCDEF':
                self.page.goto(BASE+'#requisitos/'+rf+'/'+part)
                self.assertEqual(self.page.locator('h1').count(), 1)
                self.assertEqual(self.page.locator('#apartado-'+part).count(), 1)
            self.page.locator('#eval-observations').fill('Revisión ficticia')
            self.click('#evaluation-form button[type=submit]')
            self.assertIn('guardada', self.page.locator('#eval-feedback').inner_text())
        self.page.goto(BASE+'#inicio')
        self.assertIn('ACTIVIDAD 4', self.page.locator('main').inner_text())
        self.page.goto(BASE+'#requisitos/RF02/F')
        self.assertEqual(self.page.locator('#eval-observations').input_value(), 'Revisión ficticia')


if __name__ == '__main__':
    unittest.main(verbosity=2)
