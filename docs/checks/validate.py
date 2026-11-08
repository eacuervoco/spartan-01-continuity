"""Portal checks with stdlib + Node only; run from any directory. No backend imports."""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit
import json
import re
import subprocess
import xml.etree.ElementTree as ET

DOCS = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.elements = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def verify(markup, rendered=False):
    elements = Page(markup).elements
    ids = [a['id'] for _, a in elements if 'id' in a]
    assert len(ids) == len(set(ids)), 'Duplicate IDs'
    if rendered:
        assert sum(t == 'h1' for t, _ in elements) == 1
    labels = {a.get('for') for t, a in elements if t == 'label'}
    for tag, attrs in elements:
        if tag in ('input', 'select', 'textarea'):
            assert attrs.get('id') in labels, f'Label missing: {attrs}'
        for attr in ('src', 'href'):
            if attr not in attrs:
                continue
            url = urlsplit(attrs[attr])
            assert not url.scheme and not url.netloc, f'External resource: {attrs[attr]}'
            assert not url.path.startswith('/'), f'Absolute path: {url.path}'
            if url.path:
                target = (DOCS / unquote(url.path)).resolve()
                assert target.is_relative_to(DOCS) and target.is_file(), f'Missing resource: {url.path}'
                if url.fragment and target.suffix == '.md':
                    headings = re.findall(r'^#+ (.+)$', target.read_text(), flags=re.M)
                    slugs = {re.sub(r'[^\w\s-]', '', h.lower()).replace(' ', '-') for h in headings}
                    assert unquote(url.fragment) in slugs, f'Missing anchor: {attrs[attr]}'


with TemporaryDirectory(prefix='continuity-portal-') as temporary:
    snapshots_path = Path(temporary) / 'views.json'
    subprocess.run(['node', str(DOCS/'checks/portal.test.cjs'), '--snapshots', str(snapshots_path)], check=True)
    snapshots = json.loads(snapshots_path.read_text())
    for markup in snapshots:
        verify(markup, rendered=True)
    verify((DOCS/'index.html').read_text())
    ET.parse(DOCS/'assets/data-model.svg')
    for script in (DOCS/'js').glob('*.js'):
        subprocess.run(['node', '--check', str(script)], check=True)
    # Public additions must contain no live API calls, private keys, trackers or remote assets.
    for source in [DOCS/'index.html', *(DOCS/'js').glob('*.js'), *(DOCS/'css').glob('*.css')]:
        text = source.read_text()
        assert not re.search(r'fetch\s*\(|XMLHttpRequest|https?://|BEGIN .*PRIVATE KEY|postgres(?:ql)?://', text), source
    for original, view in [('usuarios','RF01'), ('empresas','RF02'), ('credenciales','RF01'), ('sesiones','RF01')]:
        assert f'public.{original}' in '\n'.join(p.read_text() for p in (DOCS.parent/'database').glob('*.sql'))
    print(f'Portal: {len(snapshots)} rendered snapshots checked; relative resources, labels, H1, SVG and JS syntax OK.')
    print('DOM simulated. Visual/mobile/WCAG checks in a real browser remain pending.')
