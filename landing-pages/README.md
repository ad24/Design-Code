# Haus Techs landing pages (v2)

A redesign of the six live campaign pages on haustechs.ae, built to the Haus Techs brand guidelines (cream / stone / charcoal / gold, Cormorant Garamond + Inter, quiet editorial voice).

| File | Live URL | Campaign |
|---|---|---|
| `villa-renovation-dubai.html` | haustechs.ae/villa-renovation-dubai.html | Villa (EN) |
| `apartment-renovation-dubai.html` | haustechs.ae/apartment-renovation-dubai.html | Apartment (EN) |
| `palm-jumeirah-renovation.html` | haustechs.ae/palm-jumeirah-renovation.html | Palm Jumeirah (paused, live for WhatsApp/organic) |
| `commercial-fitout-dubai.html` | haustechs.ae/commercial-fitout-dubai.html | Commercial fitout (EN) |
| `villa-renovation-dubai-ar.html` | haustechs.ae/villa-renovation-dubai-ar.html | Villa (Arabic, RTL) |
| `thank-you.html` | haustechs.ae/thank-you.html | Conversion page |

## Deploy

Upload everything inside `dist/` to the site root, next to the existing `lp-images/` folder and `send-lead.php`:

```
dist/*.html          -> site root (replaces the current pages)
dist/lp-assets/      -> site root /lp-assets/ (new: shared CSS + JS)
dist/lp-images/work/ -> site root /lp-images/work/ (new: project photos, keep the existing lp-images/ files)
```

Keep a copy of the current live pages before replacing them.

## What did not change (on purpose)

- File names and URLs.
- Form `action="send-lead.php"`, method POST, and every field name and order: `subject, source, name, phone, email, contact, location, detail, message` (Arabic page: `source, subject, ...` as before).
- Hidden `subject` / `source` values, so leads keep their campaign labels.
- Tracking: GTM `GTM-K9JTX44J`, GA4 `G-VLJNQ52W0P`, Google Ads `AW-16469942753`, Clarity `omu8kikjv8`, and the thank-you conversion `AW-16469942753/B_1FCPKFzc4cEOHDva09`.
- Calculator rates, minimums and slider ranges.
- `noindex, nofollow`.

New (additive) dataLayer events for GTM if you want them: `ht_whatsapp_click`, `ht_call_click`, `ht_email_click`, `ht_form_start`, `ht_form_submit`, `ht_form_whatsapp`, `ht_calc_whatsapp`.

## Editing

All copy, photos, rates and FAQs live in `pages.py`. Shared styles in `src/haus.css`, behaviour in `src/haus.js`. After editing:

```
python3 landing-pages/build.py
```

and upload `dist/` again. Bump `ASSET_VER` in `build.py` when the CSS/JS changes so browsers fetch the new files.

## Project photos

`src/work/` holds the photos used on the pages, taken from the "Work Sample" Drive folder, resized (1600px and 800px), with location data removed. Real project photos get a light warm grade to match the brand guide; 3D renders are left as they are.

- Real, delivered work: G17 Al Waha (including the before/after pairs), Villa 91 Al Ain, crew photos from Living Legends.
- 3D design concepts (always captioned as such): the residential concepts, BLVD Heights, Al Barari, Omniyat, Mazaya JLT, Ivory Hospital, Gia Hyu Land, Acino.

The Palm page plays the Shoreline Apartments video from Google Drive (the Drive file must stay shared as "Anyone with the link").

To use new project photos: upload them to `lp-images/` on the server (or the WordPress media library) and change the image paths in `pages.py`.

Icons: Phosphor Icons (MIT), see `src/icons/LICENSE-phosphor.txt`.
