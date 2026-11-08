# Logbook website: owner's guide

*Written November 2026. Keep this file in the repo so it's always next to the site.*

The flight log map is **one file, `logbook.html`**. It reads your Google Sheet and draws every flight on a map. It is published twice, from two GitHub repos:

| Site | Repo |
|---|---|
| https://flightsmart.github.io/logbook.html | folder `flightsmart.github.io` |
| https://flightsmart.tools/logbook.html | folder `flightSmart` |

Both repo folders sit side by side in **iCloud Drive › Documents › GitHub › flightsmart** (my GitHub account folder, not a repo itself):
 
```
GitHub/flightsmart/
├── flightSmart/              → flightsmart.tools
└── flightSmart.github.io/    → flightsmart.github.io
```
 
Both repos need the same files. Whenever you change something, change it in **both**.
 
---

## 1. How it works, in one minute

1. **Original Google Sheet(s) are the database.** The page downloads two published CSV versions of it: your flights (<u>Infinite Flight Logbook</u>) and your ATC sessions (<u>IFATC Logbook</u>). Nothing about your flights is stored on GitHub. Add a row to the sheet and it shows up on the site the next time the page is opened (Google can take a few minutes to update the published CSV). The "daydreamers" tab in <u>Infinite Flight Logbook</u> is not read.
2. **The page looks up airports and runways** to know where to draw things. It first loads a small file of just airports you have flown to (`data/airports-flown.csv`) so the map appears quickly. Then it quietly downloads the full world list in the background.
3. **The LOG button** sends a new flight to a small Google Apps Script (`Code.gs`) that lives inside your <u>Infinite Flight Logbook</u> Google Sheet. That script **only ever adds one new row** to the "Logbook" tab and emails you a confirmation. It never edits or deletes anything.
4. **Pictures** (airline logos and Infinite Flight aircraft pictures) are plain image files in the repo's `images` folder.

---

## 2. Files and folders

Everything sits in the top folder of each repo (the folder that contains `logbook.html`).
Either `flightsmart/flightsmart.github.io/` or `flightsmart/flightsmart/`. 

```
flightsmart.github.io/
├── logbook.html
├── Infinite Flight Aircraft Livery List.csv
├── fleet_images.py
├── airports_flown.py
├── fleet_report.txt
├── LOGBOOK-GUIDE.md
├── data/
│   ├── airports-flown.csv
│   └── runways-flown.csv
└── images/
    ├── favicon_logbook.png
    ├── pfp.png
    ├── logos/
    └── fleet/
```

### What each file does

| File or folder | What it's for | Where it comes from |
|---|---|---|
| `logbook.html` | The whole website (HTML, CSS and JavaScript in one file) | You edit it |
| `Infinite Flight Aircraft Livery List.csv` | Livery colours, and which logo to show for each one | You edit it |
| `fleet_images.py` | Downloads the aircraft pictures into `images/fleet/` * | Script |
| `airports_flown.py` | Makes the two small files in `data/` * | Script |
| `fleet_report.txt` | List of aircraft the picture script couldn't match (optional) | Made by `fleet_images.py` |
| `LOGBOOK-GUIDE.md` | This guide | You edit it |
| `data/airports-flown.csv` | Only the airports you've flown to | Made by `airports_flown.py` |
| `data/runways-flown.csv` | The runways at those airports | Made by `airports_flown.py` |
| `images/favicon_logbook.png` | The little icon in the browser tab | You add it |
| `images/pfp.png` | Small profile picture in the page header | You add it |
| `images/logos/` | Folder: Airline logos shown in the routes table. Each file is named as in the livery list CSV | You add them |
| `images/fleet/` | Folder: Infinite Flight aircraft pictures, stored as `<aircraft-type>/<livery>.webp`, e.g. `fleet/787-9/british-airways.webp` | Made by `fleet_images.py` |

*Note: the two python files are helper scripts not needed for the website to run. They are only in the flightsmart.github.io/ repository.
**Not in the repo, but needed:**

- **`Code.gs`** lives inside the Google Sheet: open the sheet, then **Extensions → Apps Script**. Keep a copy somewhere safe too.
- **Script Properties** (settings stored inside that Apps Script, not on the website):
  - `LOGBOOK_PASSWORD`: the "signature" you type in the LOG form.
  - `NOTIFY_EMAIL`: where confirmation emails go.
  - `LOGBOOK_SETTINGS`: your Live Orgs and airframes list. It is written automatically when you use the ○ settings window, so don't edit it by hand.

**What happens if something is missing:**

| Missing | Result |
|---|---|
| `data/` files | Still works, just slower (downloads the full ~5 MB world list first). |
| `images/fleet/…` picture | No fleet picture for that flight |
| A logo in `images/logos/` | The livery name is shown as text instead. |
| `Infinite Flight Aircraft Livery List.csv` | No color swatches or logos, just livery names. |

### The livery list CSV (columns the page reads)

| Column | What it does |
|---|---|
| `Infinite Flight Livery Name` | Must match the livery name in your sheet exactly. |
| `Color 1`, `Color 2`, `Color 3` | The little color swatch next to the livery in Light Mode, only used in GA / Military Liveries. It is also shown if the logo for an airline is not present. |
| `Logo or Wordmark` (the typo `Logol or Wordmark` also works) | File name inside `images/logos/`. |
| `Include Name` | `T` = logo **and** name, `F` = logo only. |
| `Dark Logo` | How the logo looks in dark mode: `knockout` (default), `mono`, or `outline`. Optional there is `color`, `chip` but they are not used currently. Mono is better for logos that work as a silhouette. Knockout is better for logos that would not work as a silhoutte such as United or UPS.|

---

## 3. Outside services the site depends on

If one of these ever disappears, this is the list to check.

| What | Used for | Link |
|---|---|---|
| Google Sheet: <u>Infinite Flight Logbook</u> (published CSV*) | All your flights | [flights CSV](https://docs.google.com/spreadsheets/d/e/2PACX-1vRlxVfQ2tN8yza3eILYJ-KO9A3h5w_IygXl0fgKAmLNWyovhQkGbfO_u15d3NDf6pOaPn8guj1qVIoF/pub?output=csv) |
| Google Sheet: <u>IFATC Logbook</u> (published CSV*) | ATC circles and sessions | [ATC CSV](https://docs.google.com/spreadsheets/d/e/2PACX-1vRU1VT5H_li0QNytw6EDCNINd4jlyLuAT1CJiwyy7-EdjwqClCdPMseakuTPbJgQJ3yUDCQ-YBQ4TIz/pub?output=csv) |
| Google Apps Script web app | The LOG button (adds a row and sends the email) | [script.google.com](https://script.google.com) (your projects). The web app address is `LOGBOOK_API_URL` in `logbook.html`. |
| OurAirports data | Airport positions/names, runways (traffic patterns) | [ourairports.com/data](https://ourairports.com/data/) · [airports.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv) · [runways.csv](https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/runways.csv) |
| Infinite Flight fleet pages | Source of the aircraft pictures (used only by `fleet_images.py`) | [infiniteflight.com/fleet](https://infiniteflight.com/fleet) |
| Leaflet 1.9.4 | The map itself | [leafletjs.com](https://leafletjs.com) · loaded from [unpkg](https://unpkg.com/leaflet@1.9.4/dist/leaflet.js) |
| PapaParse 5.4.1 | Reads the CSV files | [papaparse.com](https://www.papaparse.com) · loaded from [cdnjs](https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js) |
| Esri / ArcGIS map tiles | Dark and light grey base maps | [Dark Gray](https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer) · [Light Gray](https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer) |
| Google Fonts | B612 Mono (main font), Montserrat | [B612 Mono](https://fonts.google.com/specimen/B612+Mono) · [Montserrat](https://fonts.google.com/specimen/Montserrat) |
| Caveat font | Handwriting in the LOG form and remarks | Built into `logbook.html` itself, so no download is needed. [Caveat](https://fonts.google.com/specimen/Caveat) |


**\* About the sheet:** both CSVs come from **File → Share → Publish to web** in Google Sheets. If you ever un-publish the sheet, the site goes empty. The page expects these layouts:

- **Flights:** the first 2 rows are headers. Columns A–L are Date, Flight Time, Aircraft Manufacturer, Aircraft Type, Airline / Livery, Depart, Dest, Ldgs, Unique Session?, Organization, Airframe, Remarks.
- **ATC:** the first row is a header. Columns are Date, Duration, Station, Airport, Ops, Reports, Additional Controllers, Remarks…

---

## 4. Everyday jobs

### 4a. Open Terminal in the repo folder

1. In **Finder**, go to **iCloud Drive › Documents › Github › flightsmart › flightsmart.github.io**.
2. If you don't see the path bar at the bottom of the Finder window: **View → Show Path Bar**.
3. **Right-click `flightsmart.github.io` in the path bar → Open in Terminal.**

   *If that option isn't there:* open Terminal, type `cd ` (with a space), drag the folder from Finder into the Terminal window, and press Return.

   *Or paste this into Terminal:*
   ```
   cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/Documents/Github/flightsmart/flightsmart.github.io
   ```

To check you're in the right place, type `ls` and press Return. You should see `logbook.html` in the list.

### 4b. Run the Python scripts

Both scripts only need Python 3, which Macs already have. If the Mac asks to install "command line developer tools", say yes. Both scripts read your published sheet, so they always see your latest flights.

**`airports_flown.py`** makes the map load fast. Run it every month or two, or after flying somewhere new:

```
python3 airports_flown.py
```

- **What it does:** rewrites `data/airports-flown.csv` and `data/runways-flown.csv`.
- **At the end** it lists any airport codes in your sheet that the airport database doesn't know. Those flights can't be drawn. Usually it's a typo in the sheet or an old code (see *Fix an airport that won't draw* below).
- **If you skip it,** nothing breaks. New airports just appear a few seconds later than the rest.

**`fleet_images.py`** downloads Infinite Flight pictures for every aircraft + livery you've flown. Run it after flying new liveries:

```
python3 fleet_images.py            # download whatever is missing
python3 fleet_images.py --dry-run  # only show what it would download
```

- **What it does:** saves pictures into `images/fleet/`, skipping any you already have.
- **At the end** it lists what it couldn't match (also saved to `fleet_report.txt`). To fix one, open `fleet_images.py` in a text editor and add a line near the top. Then run it again.
  - `AIRCRAFT_PAGES` when the aircraft doesn't match. Example: `'CL350': 'challenger-350',`. The right side is the end of the address on infiniteflight.com/fleet/…
  - `LIVERY_NAMES` when the livery name differs from Infinite Flight's. Example: `'CL350 | Luxaviation Belgium': 'Luxaviation',`
- If you see `CERTIFICATE_VERIFY_FAILED`, the script automatically retries with the Mac's own `curl`, so it should carry on by itself. If it still fails, open **Applications → Python 3.x → Install Certificates.command** once.

### 4c. Copy changes to the second repo

The scripts only write into the folder you ran them in. After running them in `flightsmart.github.io`, bring the changes over to the flightsmart.tools repo folder:

- **`data/`:** copy the whole folder over and choose **Replace**.
- **`images/fleet/`:** copy it into the other repo's `images` folder and choose **Replace**. Don't replace the whole `images` folder unless both repos' `images` folders are identical.
- **`logbook.html`:** copy it if you changed it, and choose **Replace**.

*(Or simply run the same scripts again in the other repo folder. It works the same way.)*

### 4d. Publish with GitHub Desktop

1. Open **GitHub Desktop**.
2. Top left, **Current Repository** → pick **flightsmart.github.io**.
3. The **Changes** list (left) shows every new or changed file. Check it looks right.
4. Bottom left: type a short summary (e.g. `New fleet pictures`), then click **Commit to main**.
5. Top bar: click **Push origin**. (Before you start, if the button says **Fetch origin** or **Pull origin**, click it first.)
6. Repeat steps 2–5 for the **flightsmart.tools** repo.
7. Wait about a minute, open the site, and hard-refresh (**Cmd + Shift + R**) so the browser doesn't show an old copy.

### 4e. Test the page on your Mac before publishing

Double-clicking `logbook.html` **won't work properly**, because it looks for files like `/images/...` and `/data/...` on a web server. Instead, start a tiny local server:

1. Open Terminal in the repo folder (4a).
2. Run:
   ```
   python3 -m http.server 8000
   ```
3. Open http://localhost:8000/logbook.html in your browser.
4. Press **Ctrl + C** in Terminal to stop the server.

---

## 5. The LOG button (adding flights from the website)

- **Using it:**
  1. Click **LOG** (between the random-flight button and FILTERS).
  2. Fill in the card and type your password in **Signature**.
  3. Click **FILE**.
  4. The receipt prints and ends with "FILED, GOOD DAY." and a confirmation email arrives.
  5. **NEW ENTRY** clears the card for another flight. Only **✕** closes the card.
- **Live Orgs / airframes:** the small **○** dot on the card opens the settings window. Choosing an airframe fills in Aircraft and Livery automatically. These settings are stored in the Apps Script, not in the sheet.
- **Safety:** the script refuses to write anything if:
  - the "Logbook" tab's header row (row 2, columns A–L) doesn't match what it expects;
  - the row it is about to fill isn't completely empty;
  - the password is wrong (5 wrong tries in 15 minutes pause logging).

  It only writes columns A–L of one new row.
- **Change the password:** spreadsheet → Extensions → Apps Script → ⚙ Project Settings → Script Properties → edit `LOGBOOK_PASSWORD`. Takes effect immediately; no redeploy needed. The same goes for `NOTIFY_EMAIL`.
- **If you edit `Code.gs`:** save, then **Deploy → Manage deployments → ✏️ → Version: New version → Deploy**. The web address stays the same, so `logbook.html` doesn't need changing.
- **If you ever make a brand-new deployment** (new address): paste the new `/exec` address into `LOGBOOK_API_URL` in `logbook.html` in **both** repos.
- **If confirmation emails stop:** in the Apps Script editor, pick **testEmail** from the function menu and click **▶ Run**, then allow the permissions Google asks for.
- **If you rename or move columns in the sheet:** the LOG button will refuse to write. That's on purpose. Either put the headers back, or update `EXPECTED_HEADERS` at the top of `Code.gs` and deploy a new version. The map side also reads columns by position (see section 3), so moving columns affects it too.
- **Privacy:** the website never contains your password or email address. Visitors can't see either. The script address in `logbook.html` is public, but without the password it can't write anything.

---

## 6. Finding your way around `logbook.html`

It's one long file in three parts: **CSS** (the look) at the top, **HTML** (the buttons and panels) in the middle, **JavaScript** (the behaviour) at the bottom. Line numbers change over time, so use **Find (Cmd + F)** with these words:

| To change… | Search for |
|---|---|
| The sheet addresses | `googleSheetUrl`, `atcSheetUrl` |
| The LOG script address | `LOGBOOK_API_URL` |
| Airport code fixes | `codeAliases` (keep it the same as `CODE_ALIASES` in `airports_flown.py`) |
| Colours (dark mode) | `:root {` (e.g. `--accent-green`) |
| Colours (light mode) | `[data-theme="light"] {` |
| Map buttons | `class="map-btn"` |
| The LOG card text (`darkeyes · N2DE` etc.) | `lb-meta-pilot` |
| The timeline | `Timeline` |
| Airport/runway loading | `FLOWN_AIRPORTS_URL`, `FULL_AIRPORTS_URL`, `runways-flown` |
| Aircraft picture file names | `fleetSlug` (must match `slug()` in `fleet_images.py`) |
| Sidebar flight details (DEPART, ARRIVAL, TYPE…) | `details-row` |

**What's on the page** (map buttons, left to right):

- **< ROUTES**: the routes table.
- **v TIMELINE**: monthly bar chart. Click a month to filter by it. Hidden on phones.
- **Traffic patterns**: show or hide.
- **ATC circles**: show or hide.
- **ICAO labels**: show or hide.
- **Airport mode**: cycles through the airport display modes.
- **Light/dark**: switches the theme.
- **Random flight**.
- **LOG**: opens the log form (section 5).
- **FILTERS >**: the filter sidebar.

Click a row in the table to open its details: airports, aircraft, livery, remarks and the Infinite Flight picture. **Escape** undoes your last filter, including a timeline month.

---

## 7. Fix-it list

- **Site shows nothing / stuck loading:** open the two sheet CSV links in section 3. If they don't download, the sheet was un-published (File → Share → Publish to web).
- **My change isn't showing:** wait a minute after pushing, then hard-refresh with Cmd + Shift + R. Old copies love to hang around.
- **Fix an airport that won't draw:**
  1. Run `python3 airports_flown.py` and read its "not in the database" list.
  2. Look the airport up on [ourairports.com](https://ourairports.com).
  3. If it's a typo, fix it in the sheet.
  4. If the database uses a different code, add a line like `'OLD': 'NEW',` to **both** `codeAliases` in `logbook.html` and `CODE_ALIASES` in `airports_flown.py`.
- **No aircraft picture for a flight:** run `fleet_images.py` and check its report (section 4b).
- **A logo doesn't appear:** the file name in the livery list CSV must exactly match the file in `images/logos/`, including capital letters (GitHub is case-sensitive, your Mac is not).
- **A library link dies one day (unpkg, cdnjs):** search the web for the library name and version (e.g. "leaflet 1.9.4 cdn") and swap the address near the top of `logbook.html`.
- **OurAirports moves its files:** update the addresses in `logbook.html` (`FULL_AIRPORTS_URL`, `FULL_RUNWAYS_URL`) and in `airports_flown.py` (`AIRPORTS_CSV`, `RUNWAYS_CSV`).