#!/usr/bin/env python3
"""
fleet_images.py: downloads Infinite Flight's livery pictures for every aircraft + livery in your logbook.

Run it from the top folder of your website repo (the folder that contains logbook.html):

    python3 fleet_images.py              download what's missing into images/fleet/
    python3 fleet_images.py --dry-run    only show what it would download

Then commit the images/fleet folder (copy it into both repos).
Re-run it after flying new liveries. Pictures you already have are skipped.

Pictures are saved as  images/fleet/<aircraft type>/<livery>.webp, named after your sheet,
e.g. "787-9" + "British Airways"  ->  images/fleet/787-9/british-airways.webp.
logbook.html shows that picture under RMK; if there isn't one, it shows nothing.

Anything it couldn't match is listed at the end (and in fleet_report.txt). To fix one, add it to
AIRCRAFT_PAGES or LIVERY_NAMES below and run the script again.
Only needs Python 3. Nothing to install.
"""

import argparse, csv, difflib, html.parser, io, os, re, shutil, ssl, subprocess, sys, tempfile, time, unicodedata, urllib.error, urllib.parse, urllib.request

LOGBOOK_CSV = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vRlxVfQ2tN8yza3eILYJ-KO9A3h5w_IygXl0fgKAmLNWyovhQkGbfO_u15d3NDf6pOaPn8guj1qVIoF'
               '/pub?output=csv')
FLEET = 'https://infiniteflight.com/fleet'

# Aircraft -> the Infinite Flight fleet page, when they don't match on their own
# (the page is the last part of the address, e.g. infiniteflight.com/fleet/challenger-350).
# Write the aircraft either as just the type ('747-8i') or as the report shows it ('Boeing 747-8i').
AIRCRAFT_PAGES = {
    'CL350': 'challenger-350',
    'Boeing 747-8i': '747-8',
    'Cessna c172' : '172',
    'Cessna c208' : '208-caravan',
    'Boeing F/A-18' : 'f-a-18e-super-hornet',
    'Piper PA28' : 'pa-28-archer',
    'Supermarine Spitfire' :  'spitfire-mk-viii',
    'Boeing VC-25' : '747-200',
}

# Your sheet's livery name -> the caption Infinite Flight uses, when they differ.
# Key is "aircraft | livery in your sheet", copied from the report. Examples:
#   'CL350 | Luxaviation Belgium': 'Luxaviation',
#   'Boeing 787-9 | United Airlines - 2019': 'United Airlines',
LIVERY_NAMES = {
    '208 Caravan | Private 1' : 'N208LD',
    '208 Caravan | Westwind' :  'Westwind Aviation',
    '717-200 | AirTran' : 'AirTran - Atlanta Falcons',
    '737-800 | Southwest' : 'Southwest - Heart',
    '737-800 | XiamenAir' : 'Xiamen Airlines',
    '737-900 | Korean Airlines' : 'Korean Air',
    '737-900 | Ukraine International' : 'Ukraine International Airlines',
    '747-200 | SAS' : 'Scandinavian Airlines',
    '757-200 | American Airlines' : 'American Airlines - 2013',
    '757-200 | DHL' : 'Generic',
    '757-200 | Ghana Airways' : 'Ghana International Airlines',
    '757-200 | Uzbekistan' : 'Uzbekistan Airways',
    '777-200ER | Infinite Flight' : 'Infinite Flight - 2019',
    '777-200ER | Korean Airlines' : 'Korean Air',
    '777-200LR | Boeing House' : 'Boeing',
    '777-200ER | Taag Angola Airlines' : 'TAAG Angola Airlines',
    '777-300ER | Swiss' : 'Swiss International Air Lines',
    '777-300ER | United Airlines' : 'United Airlines - 2019',
    '777F | Emirates Sky Cargo' : 'Emirates SkyCargo',
    '787-8 | Boeing House' : 'Boeing',
    '787-9 | Scoot Airlines' : 'Scoot',
    'A-10 | 66th WS Nellis AFB' : 'US Air Force - 66th WS',
    'A-10 | 75th FS Moody AFB' : 'US Air Force - 75th FS',
    'A220-300 | Breeze' : 'Breeze Airways',
    'A220-300 | Swiss' : 'Swiss International Air Lines',
    'A320-200 | Allegiant' : 'Allegiant Air',
    'A320-200 | Frontier' : 'Frontier - Ozzy',
    'A320-200 | SAS' : 'Scandinavian Airlines',
    'A321-200 | Frontier' : 'Frontier - Virginia the Wolf',
    'A321-200 | Swiss' : 'Swiss International Air Lines',
    'A330-200F | Turkish Cargo' : 'Turkish Airlines Cargo',
    'A330-300 | AirAsia X' : 'Generic',
    'A330-300 | Edelweiss' : 'Edelweiss Air',
    'A330-300 | Korean Airlines' : 'Generic',
    'A330-300 | SAS' : 'Scandinavian Airlines',
    'A330-300 | Sri Lankan Airlines' : "Srilankan Airlines",
    'A330-300 | Swiss' : 'Swiss International Air Lines',
    'A330-300 | WOW Air' : 'Generic',
    'A330-900neo | TAP Air Portugual' : 'TAP Air Portugal',
    'A340-600 | Etihad Airways (Grand Prix)' : 'Etihad Airways - Formula One',
    'A350-900 | Infinite Flight'  : 'Infinite Flight - 2019',
    'A380-800 | Emirates' : 'Emirates - 2023',
    'A380-800 | Korean Airlines' : 'Korean Air',
    'C-130J | USAF - Moody AFB' : 'US Air Force - Moody AFB',
    'C-130J | United States Coast Guard' : 'US Coast Guard',
    'CRJ-1000 | Iberia' : 'Iberia - New Air Nostrum',
    'CRJ-1000 | Iberia - retro' : 'Iberia - Retro Air Nostrum',
    'CRJ-200 | Infinite Flight' : 'Infinite Flight - 2018',
    'CRJ-200 | United Express' : 'United Express - Old',
    'CRJ-700 | Air France Hop' : 'HOP!',
    'CRJ-900 | Lufthansa - 2018' : 'Lufthansa CityLine- 2018',
    'Dash-8 Q400 | Austrian' : 'Austrian Airlines',
    'Dash-8 Q400 | Widerøe'  : 'Wideroe',
    'DC-10F | KC-10 Extender USAF' : 'US Air Force - KC-10 Extender',
    'E175 | American Eagle'  : 'American Airlines',
    'E190 | BA Cityflyer' : 'British Airways - BA CityFlyer',
    'E190 | British Airways' : 'British Airways - BA CityFlyer',
    'E190 | KLM' : 'KLM Cityhopper',
    'F-16C | Default' : 'US Air Force',
    'TBM-930 | Stevo1kinevo' : 'White, Red and Black',
    'TBM-930 | French Air Force' : 'French Army',
    'TBM-930 | Infinite Flight -  Light + Infinite Flight -  Dark' : 'Infinite Flight - Light',
    'TBM-930 | N930TX' :  'Charcoal',
    'TBM-930 | N960DH'  : 'N930DH',
    'XCub | Launch Edition N500XC' : 'Launch Edition',
    'XCub | N17XC' : 'Black & Gray',
    'Boeing 737-8 MAX | Southwest - Heart' : 'Southwest Airlines',
    'Boeing 737-800 | Avelo Airlines' : 'Avelo',
    'Boeing 737-800 | Norwegian Airlines' : 'Norwegian Air Shuttle',
    'Airbus A319-100 | Swiss' : 'Swiss International Air Lines',
    'Cessna c208 | Private 1' : 'Generic',
    'Cessna c208 | Private 2' : 'Generic',
    'Cessna c208 | Southern Air' : 'Southern Airways Express',
    'Cessna c208 | Westwind' : 'Westwind Aviation',
    'Bombardier CRJ-900 | Air Canada' : 'Air Canada Express',
    'Embraer E190 | Air Canada' : 'Air Canada Express',
    'Embraer E175 | Air Canada' : 'Air Canada Express',
    'Boeing F/A-18 | Maverick' : 'US Navy - Maverick',
    'Boeing F/A-18 | Unknown' : 'Generic Aggressor',
    'Supermarine Spitfire | Spitfire' : 'Royal Australian Air Force'
}

USER_AGENT = 'Mozilla/5.0 (logbook fleet image sync)'
PAUSE = 0.3   # seconds between requests, to be polite to their server


# ── Names -> file names. logbook.html does exactly the same, so keep these two in step. ──
def slug(text):
    text = unicodedata.normalize('NFKD', str(text))
    text = ''.join(c for c in text if not unicodedata.combining(c)).lower().replace('&', ' and ')
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', text)).strip('-')


def norm(name):
    """Looser form used to compare your livery names with Infinite Flight's captions."""
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]+', ' ', slug(name).replace('-', ' '))).strip()


def _urllib_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _curl_get(url):
    # macOS's own curl uses the Mac's certificates, so it works even when Python's are missing
    fd, tmp = tempfile.mkstemp()
    os.close(fd)
    try:
        p = subprocess.run(['curl', '-sSL', '--max-time', '30', '-A', USER_AGENT, '-o', tmp, '-w', '%{http_code}', url],
                           capture_output=True, text=True)
        if p.returncode != 0:
            raise urllib.error.URLError(p.stderr.strip() or 'curl failed')
        code = int(p.stdout.strip() or 0)
        if code >= 400:
            raise urllib.error.HTTPError(url, code, 'HTTP %d' % code, {}, None)
        with open(tmp, 'rb') as fh:
            return fh.read()
    finally:
        os.remove(tmp)


_use_curl = False

def get(url, binary=False):
    global _use_curl
    data = None
    if not _use_curl:
        try:
            data = _urllib_get(url)
        except urllib.error.URLError as e:
            if isinstance(getattr(e, 'reason', None), ssl.SSLCertVerificationError) and shutil.which('curl'):
                _use_curl = True
                print('  (Python is missing its security certificates, so using macOS curl instead.\n'
                      '   To fix Python itself, run:  open "/Applications/Python %d.%d/Install Certificates.command")'
                      % sys.version_info[:2])
            else:
                raise
    if _use_curl:
        data = _curl_get(url)
    time.sleep(PAUSE)
    return data if binary else data.decode('utf-8', 'replace')


# ── Reading Infinite Flight's pages ──
LIVERY_IMG = re.compile(r'webcdn\.infiniteflight\.com/thumbnails/liveries/([0-9a-fA-F-]{36})\.webp')


class ImgCollector(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs = []
    def handle_starttag(self, tag, attrs):
        if tag in ('img', 'source'):
            self.imgs.append(dict(attrs))


def liveries_on_page(page_html):
    """[(livery caption, image url)] from a fleet page. Captions come from the image alt text,
    e.g. "Air Berlin livery on the Airbus A319-100." -> "Air Berlin"."""
    p = ImgCollector()
    p.feed(page_html)
    found, seen = [], set()
    for a in p.imgs:
        blob = urllib.parse.unquote(' '.join(str(a.get(k) or '') for k in ('src', 'data-src', 'srcset', 'data-srcset')))
        m = LIVERY_IMG.search(blob)
        alt = (a.get('alt') or '').strip()
        if not m or not alt:
            continue
        name = re.sub(r'\s+livery\s+on\s+(the\s+)?.*$', '', alt, flags=re.I).strip().rstrip('.')
        url = 'https://webcdn.infiniteflight.com/thumbnails/liveries/%s.webp' % m.group(1).lower()
        if name and url not in seen:
            seen.add(url)
            found.append((name, url))
    return found


def fleet_slugs(index_html):
    """Aircraft page names listed on infiniteflight.com/fleet (from links or the aircraft pictures)."""
    s = set(re.findall(r'/fleet/([a-z0-9][a-z0-9-]*)(?=["\'/?#.])', index_html))
    s |= set(re.findall(r'/aircraft/fleet/([a-z0-9][a-z0-9-]*)\.', index_html))
    return s


def lookup(table, *keys):
    """Find an entry whether it was written as 'type' or 'Manufacturer type' (case and spacing don't matter)."""
    t = {re.sub(r'\s+', ' ', k).strip().lower(): v for k, v in table.items()}
    for k in keys:
        k = re.sub(r'\s+', ' ', k).strip().lower()
        if k in t:
            return t[k]
    return None


def page_candidates(mfr, typ):
    c = []
    alias = lookup(AIRCRAFT_PAGES, typ, mfr + ' ' + typ)
    if alias:
        c.append(alias)
    c += [slug(typ), slug(mfr + ' ' + typ), slug(typ.replace(' ', ''))]
    return list(dict.fromkeys(x for x in c if x))


# ── Main ──
def main():
    ap = argparse.ArgumentParser(description='Download Infinite Flight livery pictures for your logbook.')
    ap.add_argument('--out', default=os.path.join('images', 'fleet'), help='folder to save into (default: images/fleet)')
    ap.add_argument('--dry-run', action='store_true', help="don't download, just report")
    args = ap.parse_args()

    print('Reading your logbook...')
    rows = list(csv.reader(io.StringIO(get(LOGBOOK_CSV))))[2:]
    pairs = {}
    for r in rows:
        if len(r) < 5:
            continue
        mfr, typ, liv = (r[2] or '').strip(), (r[3] or '').strip(), (r[4] or '').strip()
        if typ and liv:
            pairs.setdefault((mfr, typ), set()).add(liv)
    total = sum(len(v) for v in pairs.values())
    print('  %d aircraft types, %d aircraft + livery combinations' % (len(pairs), total))

    try:
        known = fleet_slugs(get(FLEET))
    except Exception as e:
        known = set()
        print('  (could not read the fleet list: %s, will try each aircraft page directly)' % e)

    saved = skipped = 0
    missing_aircraft, missing_liveries, debug = [], [], []
    for (mfr, typ), livs in sorted(pairs.items(), key=lambda kv: kv[0][1].lower()):
        folder = os.path.join(args.out, slug(typ))
        todo = [l for l in sorted(livs) if not os.path.exists(os.path.join(folder, slug(l) + '.webp'))]
        skipped += len(livs) - len(todo)
        if not todo:
            continue

        page, page_slug = None, None
        cands = page_candidates(mfr, typ)
        ordered = [c for c in cands if c in known] + [c for c in cands if c not in known]
        for c in ordered:          # pages in their fleet list first, then the other guesses
            try:
                page, page_slug = get('%s/%s' % (FLEET, c)), c
                break
            except urllib.error.HTTPError:
                continue
            except Exception as e:
                print('  ! %s: %s' % (c, e))
        if page is None:
            missing_aircraft.append('%s %s  (%d liveries)' % (mfr, typ, len(todo)))
            continue

        on_page = liveries_on_page(page)
        if not on_page:
            dbg = 'fleet_debug_%s.html' % page_slug
            with open(dbg, 'w', encoding='utf-8') as fh:
                fh.write(page)
            debug.append(dbg)
            missing_aircraft.append('%s %s  (page /fleet/%s had no liveries I could read, saved %s)' % (mfr, typ, page_slug, dbg))
            continue
        by_name = {norm(n): u for n, u in on_page}
        print('%s %s  ->  /fleet/%s  (%d liveries on their site)' % (mfr, typ, page_slug, len(on_page)))

        for liv in todo:
            want = lookup(LIVERY_NAMES, '%s | %s' % (typ, liv), '%s %s | %s' % (mfr, typ, liv)) or liv
            url = by_name.get(norm(want))
            if not url:
                close = difflib.get_close_matches(norm(want), list(by_name), n=3, cutoff=0.72)
                names = {norm(n): n for n, _ in on_page}
                hint = ('  maybe: ' + ' / '.join('"%s"' % names[c] for c in close)) if close else ''
                missing_liveries.append('%s %s | %s%s' % (mfr, typ, liv, hint))
                continue
            dest = os.path.join(folder, slug(liv) + '.webp')
            if args.dry_run:
                print('   would save  %s' % dest)
                saved += 1
                continue
            try:
                data = get(url, binary=True)
                os.makedirs(folder, exist_ok=True)
                with open(dest, 'wb') as fh:
                    fh.write(data)
                saved += 1
                print('   saved  %s  (%.1f KB)' % (dest, len(data) / 1024))
            except Exception as e:
                missing_liveries.append('%s %s | %s  (download failed: %s)' % (mfr, typ, liv, e))

    lines = ['', '%s %d new picture(s), %d already there.' % ('Would save' if args.dry_run else 'Saved', saved, skipped)]
    if missing_aircraft:
        lines += ['', 'Aircraft not found on infiniteflight.com/fleet (add to AIRCRAFT_PAGES if it is there under another name):']
        lines += ['  - ' + x for x in missing_aircraft]
    if missing_liveries:
        lines += ['', 'Liveries not found (retired, or named differently; copy the line into LIVERY_NAMES as  \'aircraft | your name\': \'their name\'):']
        lines += ['  - ' + x for x in missing_liveries]
    if debug:
        lines += ['', 'If a page could not be read at all, send me the fleet_debug_*.html file(s) it saved.']
    report = '\n'.join(lines)
    print(report)
    with open('fleet_report.txt', 'w', encoding='utf-8') as fh:
        fh.write(report.strip() + '\n')
    print('\n(Also written to fleet_report.txt)')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)