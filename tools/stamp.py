"""Give every page's links to shared files (mm-*.js, mm-*.css, vendor/…) one new version stamp, so
browsers fetch the new files together instead of mixing cached old ones with new ones.

    python3 tools/stamp.py            # stamp = now (UTC), e.g. ?v=2026-11-08.1530
    python3 tools/stamp.py --check    # exit 1 if pages disagree (CI runs this)

Run it whenever a shared file changes; CI fails a pull request that changes a shared file without it.
"""
import re, sys, glob, datetime, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = re.compile(r'((?:src|href)="(?!https?:)[^"?]+\.(?:js|css))\?v=([^"]+)"')
pages = sorted(glob.glob(os.path.join(ROOT, '*.html')))

def stamps():
    return {os.path.basename(p): set(m.group(2) for m in REF.finditer(open(p).read())) for p in pages}

if '--check' in sys.argv:
    s = stamps(); allv = set().union(*s.values())
    unstamped = [(os.path.basename(p), m) for p in pages for m in re.findall(r'(?:src|href)="((?!https?:)[^"?]+\.(?:js|css))"', open(p).read())]
    if len(allv) > 1 or unstamped:
        print('Version stamps differ between pages:', {k: sorted(v) for k, v in s.items()})
        if unstamped: print('Shared files linked without a stamp:', unstamped)
        print('Run: python3 tools/stamp.py'); sys.exit(1)
    print('stamp', allv.pop() if allv else '(none)'); sys.exit(0)

v = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d.%H%M')
for p in pages:
    s = open(p).read()
    s2 = REF.sub(lambda m: f'{m.group(1)}?v={v}"', s)
    s2 = re.sub(r'((?:src|href)="(?!https?:)[^"?]+\.(?:js|css))"', lambda m: f'{m.group(1)}?v={v}"', s2)
    if s2 != s: open(p, 'w').write(s2)
print('stamped', v)
