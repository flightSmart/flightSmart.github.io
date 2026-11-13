#!/usr/bin/env python3
"""
airports_flown.py: makes small airport and runway files with just the airports in your logbook,
so logbook.html can draw the map without first downloading the whole world's airports (about 5 MB).

Run it from the top folder of your website repo (the folder that contains logbook.html):

    python3 airports_flown.py

It writes  data/airports-flown.csv  and  data/runways-flown.csv  (together around 75 KB over the wire).
Commit the data folder (copy it into both repos). Re-run it now and then, e.g. whenever you run
fleet_images.py. The site keeps working between runs: a new airport is filled in from the full
world list, which the page still loads in the background, just a few seconds later.
Only needs Python 3. Nothing to install.
"""

import csv, io, os, shutil, ssl, subprocess, sys, tempfile, urllib.error, urllib.request

LOGBOOK_CSV = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vRlxVfQ2tN8yza3eILYJ-KO9A3h5w_IygXl0fgKAmLNWyovhQkGbfO_u15d3NDf6pOaPn8guj1qVIoF/pub?gid=1016795298&single=true&output=csv')
ATC_CSV = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vRU1VT5H_li0QNytw6EDCNINd4jlyLuAT1CJiwyy7-EdjwqClCdPMseakuTPbJgQJ3yUDCQ-YBQ4TIz'
           '/pub?output=csv')
AIRPORTS_CSV = 'https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv'
RUNWAYS_CSV = 'https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv'

# Same as codeAliases in logbook.html: codes in your sheet that the airport database knows by another code.
CODE_ALIASES = {
    'EGOD': 'EGFD',
    'NZIR': 'NZWD',
    'O5U': '05U',
    'VHHX': 'VHHH',
}

# Only the columns logbook.html reads
AIRPORT_COLUMNS = ['ident', 'type', 'name', 'latitude_deg', 'longitude_deg', 'continent', 'iso_country',
                   'municipality', 'gps_code', 'iata_code', 'local_code']
RUNWAY_COLUMNS = ['airport_ident', 'length_ft', 'closed', 'le_ident', 'le_latitude_deg', 'le_longitude_deg',
                  'le_heading_degT', 'he_ident', 'he_latitude_deg', 'he_longitude_deg', 'he_heading_degT']

USER_AGENT = 'Mozilla/5.0 (logbook airport sync)'


# ── Downloading (falls back to macOS curl when Python is missing its security certificates) ──
def _urllib_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _curl_get(url):
    fd, tmp = tempfile.mkstemp()
    os.close(fd)
    try:
        p = subprocess.run(['curl', '-sSL', '--max-time', '120', '-A', USER_AGENT, '-o', tmp, '-w', '%{http_code}', url],
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

def get(url):
    global _use_curl
    data = None
    if not _use_curl:
        try:
            data = _urllib_get(url)
        except urllib.error.URLError as e:
            if isinstance(getattr(e, 'reason', None), ssl.SSLCertVerificationError) and shutil.which('curl'):
                _use_curl = True
                print('  (Python is missing its security certificates, so using macOS curl instead)')
            else:
                raise
    if _use_curl:
        data = _curl_get(url)
    return data.decode('utf-8', 'replace')


def rows(url):
    return list(csv.reader(io.StringIO(get(url))))


def write_csv(path, columns, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(columns)
        for r in records:
            w.writerow([r.get(c, '') for c in columns])
    return os.path.getsize(path)


def main():
    print('Reading your logbook...')
    codes = set()
    for r in rows(LOGBOOK_CSV)[2:]:                       # flights: Depart (F) and Dest (G)
        for c in (r[5:7] if len(r) >= 7 else []):
            c = c.strip().upper()
            if c:
                codes.add(CODE_ALIASES.get(c, c))
    for r in rows(ATC_CSV)[1:]:                           # ATC sessions: Airport (D)
        if len(r) >= 4 and r[3].strip() and r[0].strip().lower() != 'date':
            c = r[3].strip().upper()
            codes.add(CODE_ALIASES.get(c, c))
    print('  %d airport codes' % len(codes))

    print('Downloading the world airport list...')
    airports = list(csv.DictReader(io.StringIO(get(AIRPORTS_CSV))))
    # Keep every airport known by one of your codes (as its ident, GPS, IATA or local code),
    # in the original order, so the page picks exactly the same airport as with the full list.
    keep, found = [], set()
    for a in airports:
        mine = {(a.get(k) or '').strip().upper() for k in ('ident', 'gps_code', 'iata_code', 'local_code')} & codes
        if mine:
            keep.append(a)
            found |= mine
    idents = {(a.get('ident') or '').strip().upper() for a in keep}

    print('Downloading the world runway list...')
    runways = [r for r in csv.DictReader(io.StringIO(get(RUNWAYS_CSV)))
               if (r.get('airport_ident') or '').strip().upper() in idents]

    size_a = write_csv(os.path.join('data', 'airports-flown.csv'), AIRPORT_COLUMNS, keep)
    size_r = write_csv(os.path.join('data', 'runways-flown.csv'), RUNWAY_COLUMNS, runways)

    print('')
    print('Saved data/airports-flown.csv  (%d airports, %.0f KB)' % (len(keep), size_a / 1024))
    print('Saved data/runways-flown.csv   (%d runways, %.0f KB)' % (len(runways), size_r / 1024))
    missing = sorted(codes - found)
    if missing:
        print('')
        print('%d code(s) are not in the airport database, so they are not on the map (same as before):' % len(missing))
        print('  ' + ', '.join(missing))
        print('  If one is a typo or an old code, add it to CODE_ALIASES here and in logbook.html.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
