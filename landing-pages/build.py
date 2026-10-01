#!/usr/bin/env python3
"""Build the Haus Techs landing pages.

    python3 landing-pages/build.py

Reads the page content in pages.py, the shared CSS/JS in src/, and writes ready-to-upload
files to dist/. Upload everything in dist/ to the site root (next to the existing lp-images/
folder and send-lead.php). File names, form field names, hidden lead-source values and
tracking IDs are kept exactly as on the live pages.
"""
import html
import json
import os
import re
import shutil

from pages import PAGES, THANK_YOU, CONTACT

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
ASSET_VER = "2"

e = html.escape


def icon_sprite():
    out = []
    for fn in sorted(os.listdir(os.path.join(SRC, "icons"))):
        if not fn.endswith(".svg"):
            continue
        svg = open(os.path.join(SRC, "icons", fn), encoding="utf-8").read()
        inner = re.sub(r"^.*?<svg[^>]*>|</svg>\s*$", "", svg, flags=re.S)
        out.append(f'<symbol id="i-{fn[:-4]}" viewBox="0 0 256 256">{inner}</symbol>')
    return '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(out) + "</svg>"


def ico(name, cls=""):
    return f'<svg class="ico {cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


# ---------------------------------------------------------------- head / tracking (verbatim IDs)
TRACK_HEAD = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-K9JTX44J');</script>
<!-- End Google Tag Manager -->
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "omu8kikjv8");
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLJNQ52W0P"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-VLJNQ52W0P');
  gtag('config', 'AW-16469942753');
</script>"""

GTM_NOSCRIPT = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-K9JTX44J"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

FONTS_EN = "family=Cormorant+Garamond:ital,wght@0,300;0,400;1,400&family=Inter:wght@300;400;500"
FONTS_AR = FONTS_EN + "&family=Amiri:wght@400;700&family=IBM+Plex+Sans+Arabic:wght@300;400;500"


def head(p, extra=""):
    fonts = FONTS_AR if p.get("rtl") else FONTS_EN
    hero = p.get("hero", {}).get("img")
    preload = f'<link rel="preload" as="image" href="{e(hero)}" fetchpriority="high">' if hero else ""
    return f"""<!doctype html>
<html lang="{p['lang']}"{' dir="rtl"' if p.get('rtl') else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{TRACK_HEAD}
<title>{e(p['title'])}</title>
{f'<meta name="description" content="{e(p["desc"])}">' if p.get('desc') else ''}
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#F0E9DC">
<meta property="og:title" content="{e(p['title'])}">
{f'<meta property="og:description" content="{e(p["desc"])}">' if p.get('desc') else ''}
{f'<meta property="og:image" content="{e(hero)}">' if hero and hero.startswith('http') else ''}
<link rel="icon" type="image/png" sizes="192x192" href="https://haustechs.ae/wp-content/uploads/2026/04/cropped-cropped-IMG_7040-192x192.png">
<link rel="apple-touch-icon" href="https://haustechs.ae/wp-content/uploads/2026/04/cropped-cropped-IMG_7040-192x192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
{preload}
<link rel="stylesheet" href="lp-assets/haus.css?v={ASSET_VER}">
{extra}
</head>"""


WORK_DIMS = {}


def work_dims(name):
    if name not in WORK_DIMS:
        from PIL import Image
        WORK_DIMS[name] = Image.open(os.path.join(SRC, "work", name + ".jpg")).size
    return WORK_DIMS[name]


def img(src, alt, cls="", lazy=True, soft=False, w=None, h=None, sizes="(max-width: 760px) 92vw, 50vw"):
    if src.startswith("work/"):
        name = src[5:]
        w, h = work_dims(name)
        base = f"lp-images/work/{name}"
        attrs = [f'src="{base}.jpg"', f'srcset="{base}-sm.jpg 800w, {base}.jpg {w}w"', f'sizes="{sizes}"',
                 f'alt="{e(alt)}"', f'width="{w}" height="{h}"']
        if cls:
            attrs.append(f'class="{cls}"')
        attrs.append('loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"')
        return "<img " + " ".join(attrs) + ">"
    attrs = [f'src="{e(src)}"', f'alt="{e(alt)}"']
    if cls:
        attrs.append(f'class="{cls}"')
    attrs.append('loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"')
    if soft or src.startswith("lp-images/"):
        attrs.append("data-soft")
    if w and h:
        attrs.append(f'width="{w}" height="{h}"')
    return "<img " + " ".join(attrs) + ">"


# ---------------------------------------------------------------- blocks
def nav(p, t):
    return f"""<a class="skip" href="#main">{t['skip']}</a>
<div class="pbar" aria-hidden="true"></div>
<header class="nav"><div class="nav-in">
  <a href="https://haustechs.ae" aria-label="Haus Techs"><img class="logo" src="https://haustechs.ae/wp-content/uploads/2026/04/logo-002.png" alt="Haus Techs" width="160" height="40"></a>
  <div class="nav-actions">
    <a class="nav-tel" href="tel:{CONTACT['tel']}" aria-label="{t['call']} {CONTACT['tel_disp']}">{ico('phone')}<span dir="ltr">{CONTACT['tel_disp']}</span></a>
    <a class="btn btn-sm" href="#quote"><span>{t['nav_cta']}</span><span class="orb">{ico('arrow-right', 'flip')}</span></a>
  </div>
</div></header>"""


def form(p, t, fid, compact=False):
    f = p["form"]
    opts = "".join(f"<option>{e(o)}</option>" for o in f["detail_opts"])
    contact_opts = "".join(f"<option>{e(o)}</option>" for o in t["contact_opts"])
    loc_req = " required" if f.get("location_required", True) else ""
    star = lambda req: "" if req else f' <span class="opt">{t["optional"]}</span>'
    msg = "" if compact else f"""
      <div class="field full"><label for="{fid}-message">{t['message']}{star(False)}</label>
        <textarea id="{fid}-message" name="message" placeholder="{e(f.get('message_ph', t['message_ph']))}"></textarea></div>"""
    hidden_first = p.get("hidden_order") == "source-first"
    hid_subject = f'<input type="hidden" name="subject" value="{e(p["subject"])}">'
    hid_source = f'<input type="hidden" name="source" value="{e(p["source"])}">'
    hidden = (hid_source + hid_subject) if hidden_first else (hid_subject + hid_source)
    return f"""<form class="lead form" id="{fid}" action="send-lead.php" method="POST" novalidate>
    {hidden}
    <h3>{t['form_h']}</h3>
    <p class="sub">{t['form_sub']}</p>
    <div class="fgrid">
      <div class="field"><label for="{fid}-name">{t['name']}</label>
        <input id="{fid}-name" name="name" autocomplete="name" placeholder="{t['name_ph']}" required>
        <span class="err">{t['err_name']}</span></div>
      <div class="field"><label for="{fid}-phone">{t['phone']}</label>
        <input id="{fid}-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" dir="ltr" placeholder="+971 5x xxx xxxx" required>
        <span class="err">{t['err_phone']}</span></div>
      <div class="field"><label for="{fid}-email">{t['email']}{star(False)}</label>
        <input id="{fid}-email" name="email" type="email" autocomplete="email" dir="ltr" placeholder="you@email.com">
        <span class="err">{t['err_email']}</span></div>
      <div class="field"><label for="{fid}-contact">{t['contact']}</label>
        <select id="{fid}-contact" name="contact">{contact_opts}</select></div>
      <div class="field"><label for="{fid}-location">{e(f['location_label'])}{star(bool(loc_req))}</label>
        <input id="{fid}-location" name="location" placeholder="{e(f['location_ph'])}"{loc_req}>
        <span class="err">{t['err_location']}</span></div>
      <div class="field"><label for="{fid}-detail">{e(f['detail_label'])}</label>
        <select id="{fid}-detail" name="detail">{opts}</select></div>{msg}
    </div>
    <div class="form-actions">
      <button class="btn" type="submit"><span>{t['submit']}</span><span class="orb"><span class="spin" aria-hidden="true"></span>{ico('arrow-right', 'flip')}</span></button>
      <div class="or">{t['or']}</div>
      <button class="btn btn-light" type="button" data-wa-form><span>{t['send_wa']}</span><span class="orb">{ico('whatsapp-logo')}</span></button>
    </div>
    <p class="form-note">{t['form_note']}</p>
  </form>"""


def hero(p, t):
    h = p["hero"]
    rating = ""
    if t["rating"]:
        g = '<a href="https://www.google.com/search?q=haus+techs+dubai+reviews" target="_blank" rel="noopener">Google</a>'
        rating = f'<p class="hero-rating rv" style="--d:4"><span class="stars" aria-hidden="true">{ico("star") * 5}</span><span>{t["rating"].format(who=e(p.get("rating_who", "")), google=g)}</span></p>'
    form_html = f'<div class="hero-form shell rv" style="--d:3"><div class="core">{form(p, t, "f1", compact=True)}</div></div>' if p.get("hero_form", True) else ""
    return f"""<section class="hero" aria-labelledby="h1">
  <span id="top-sentinel" style="position:absolute;top:0;height:1px;width:1px" aria-hidden="true"></span>
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="kicker rv">{e(h['kicker'])}</p>
      <h1 id="h1" class="rv" style="--d:1">{e(h['h1a'])}<span class="it">{e(h['h1b'])}</span></h1>
      <p class="lede rv" style="--d:2">{e(h['sub'])}</p>
      <div class="hero-ctas rv" style="--d:3">
        <a class="btn" href="{e(p['wa_url'])}" target="_blank" rel="noopener">{t['wa_cta']}<span class="orb">{ico('whatsapp-logo')}</span></a>
        <a class="link" href="#calculator">{t['calc_cta']} {ico('arrow-right', 'flip')}</a>
      </div>
      {rating}
    </div>
    <div class="hero-visual">
      <div class="brackets"><div class="hero-photo rv">{img(h['img'], h['img_alt'], lazy=False, w=1200, h=1000)}</div></div>
      {form_html}
    </div>
  </div>
</section>"""


def proof(p, t):
    stats = "".join(
        f'<div class="stat rv" style="--d:{i}"><b class="tnum"><span data-n="{n}">{n}</span>{f"<sup>{e(pre)}</sup>" if pre else ""}</b><span>{e(lbl)}</span></div>'
        for i, (n, pre, lbl) in enumerate(p.get("stats", t["stats"]))
    )
    group = "".join(f'<span class="mq-item">{e(x)}</span>' for x in p["promises"])
    clients = ""
    if p.get("clients"):
        clients = '<div class="clients rv"><small>' + e(p["clients"][0]) + "</small>" + "".join(f"<span>{e(c)}</span>" for c in p["clients"][1]) + "</div>"
    return f"""<section class="sec-tight" aria-label="{t['proof_label']}">
  <div class="wrap"><div class="stats">{stats}</div>{clients}</div>
  <div class="marquee" aria-label="{t['promises_label']}"><div class="mq-track"><div class="mq-group">{group}</div><div class="mq-group" aria-hidden="true">{group}</div></div></div>
</section>"""


def calculator(p, t):
    c = p["calc"]
    types = "".join(f"<option>{e(x)}</option>" for x in c["types"])
    ticks = "".join(f"<li>{ico('check')}<span>{e(x)}</span></li>" for x in t["calc_ticks"])
    fins = "".join(
        f'<button type="button" data-f="{k}" aria-pressed="{str(k == "premium").lower()}"><b>{e(a)}</b><span>{e(b)}</span></button>'
        for k, a, b in t["finishes"]
    )
    mn, mx, st, val = c["range"]
    return f"""<section class="sec calc" id="calculator" aria-labelledby="calc-h">
  <div class="wrap calc-grid">
    <div>
      <p class="kicker rv">{e(c['kicker'])}</p>
      <h2 id="calc-h" class="rv" style="--d:1">{t['calc_h']}</h2>
      <p class="lede rv" style="--d:2">{t['calc_lede']}</p>
      <ul class="ticks rv" style="--d:3">{ticks}</ul>
    </div>
    <div class="shell rv" style="--d:2"><div class="core">
      <div class="seg" role="group" aria-label="{t['calc_mode']}">
        <button type="button" data-mode="reno" aria-pressed="true">{t['mode_reno']}</button>
        <button type="button" data-mode="design" aria-pressed="false">{t['mode_design']}</button>
      </div>
      <div class="calc-row"><label for="calc-type">{t['ptype']}</label>
        <div class="field"><select id="calc-type">{types}</select></div></div>
      <div class="calc-row"><label for="calc-sqm">{t['size']} <output id="calc-sqm-val" for="calc-sqm" class="tnum">{val} {t['unit']}</output></label>
        <input type="range" id="calc-sqm" min="{mn}" max="{mx}" step="{st}" value="{val}"></div>
      <div class="calc-row"><span class="lbl" id="fin-l">{t['finish']}</span>
        <div class="fin" id="calc-finish" role="group" aria-labelledby="fin-l">{fins}</div></div>
      <div class="calc-out" aria-live="polite">
        <small id="calc-label">{t['est_reno']}</small>
        <span class="calc-num tnum" id="calc-result"{'' if p.get('rtl') else ' dir="ltr"'}>-</span>
        <p>{t['calc_note']}</p>
      </div>
      <div class="calc-actions">
        <a class="btn" href="#quote"><span>{t['nav_cta']}</span><span class="orb">{ico('arrow-right', 'flip')}</span></a>
        <button class="link" type="button" id="calc-wa" style="background:none;border-top:0;border-left:0;border-right:0;cursor:pointer">{ico('whatsapp-logo')} {t['calc_wa']}</button>
      </div>
    </div></div>
  </div>
</section>"""


def included(p, t):
    s = p.get("included")
    if not s:
        return ""
    tiles = []
    for i, (src, alt, h3, desc) in enumerate(s["tiles"]):
        tiles.append(f"""<article class="tile rv" style="--d:{i % 3}">{img(src, alt)}<div class="tx"><h3>{e(h3)}</h3><p>{e(desc)}</p></div></article>""")
    return f"""<section class="sec" aria-labelledby="inc-h">
  <div class="wrap">
    <div class="head"><h2 id="inc-h" class="rv">{e(s['h2'])}</h2><p class="lede rv" style="--d:1">{e(s['lede'])}</p></div>
    <div class="bento">{''.join(tiles)}</div>
  </div>
</section>"""


def communities(p, t):
    s = p.get("communities")
    if not s:
        return ""
    items = "".join(f'<div class="comm rv" style="--d:{i % 2}"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(s["items"]))
    return f"""<section class="sec" aria-labelledby="comm-h">
  <div class="wrap">
    <div class="head"><h2 id="comm-h" class="rv">{e(s['h2a'])}<span class="it">{e(s['h2b'])}</span></h2><p class="lede rv" style="--d:1">{e(s['lede'])}</p></div>
    <div class="comms">{items}</div>
  </div>
</section>"""


def sectors(p, t):
    s = p.get("sectors")
    if not s:
        return ""
    tabs, panels = [], []
    for i, sec in enumerate(s["tabs"]):
        sel = i == 0
        tabs.append(f'<button role="tab" id="tab-{sec["id"]}" aria-controls="pan-{sec["id"]}" aria-selected="{str(sel).lower()}" tabindex="{0 if sel else -1}">{e(sec["tab"])}</button>')
        items = "".join(
            f'<div class="sector-item">{img(src, alt)}<div class="tx"><h3>{e(h3)}</h3>{f"<p>{e(d)}</p>" if d else ""}</div></div>'
            for src, alt, h3, d in sec["items"]
        )
        panels.append(f"""<div class="panel" role="tabpanel" id="pan-{sec['id']}" aria-labelledby="tab-{sec['id']}"{'' if sel else ' hidden'}>
      <div class="sector"><div class="sector-intro"><h3 style="font-size:clamp(30px,3vw,42px);font-weight:300">{e(sec['h3'])}</h3><p>{e(sec['p'])}</p></div><div class="sector-list">{items}</div></div>
    </div>""")
    return f"""<section class="sec" id="offices" aria-labelledby="sec-h">
  <div class="wrap">
    <div class="head"><h2 id="sec-h" class="rv">{e(s['h2'])}</h2><p class="lede rv" style="--d:1">{e(s['lede'])}</p></div>
    <div class="tabs rv" role="tablist" aria-label="{e(s['h2'])}">{''.join(tabs)}</div>
    {''.join(panels)}
  </div>
</section>"""


def jphotos(st):
    if not st.get("photos"):
        return ""
    figs = "".join(f'<figure>{img(src, alt, sizes="(max-width: 640px) 30vw, 180px")}</figure>' for src, alt in st["photos"])
    return f'<div class="jphotos">{figs}</div><p class="jcap">{e(st.get("photos_cap", ""))}</p>'


def journey(p, t):
    steps = []
    for i, st in enumerate(p.get("journey", t["journey"]), 1):
        when = f'<p class="jwhen">{e(st["when"])}</p>' if st.get("when") else ""
        steps.append(f"""<div class="jstep"><div class="jdot">{i}</div><div>{when}<h3>{e(st['h3'])}</h3><p>{e(st['p'])}</p>
      <div class="jroles"><div><b>{t['you_do']}</b>{e(st['you'])}</div><div class="we"><b>{t['we_do']}</b>{e(st['we'])}</div></div>{jphotos(st)}</div></div>""")
    return f"""<section class="sec journey" id="journey" aria-labelledby="j-h">
  <div class="wrap">
    <div class="head"><p class="kicker rv">{t['j_kicker']}</p><h2 id="j-h" class="rv" style="--d:1">{t['j_h2a']}<span class="it">{t['j_h2b']}</span></h2><p class="lede rv" style="--d:2">{t['j_lede']}</p></div>
    <div class="jgrid"><div class="jline" aria-hidden="true"><div class="jfill"></div></div>{''.join(steps)}</div>
  </div>
</section>"""


def work(p, t):
    w = p["work"]
    figs = "".join(
        f'<figure><button class="ph" type="button" aria-label="{t["view"]}: {e(cap)}">{img(src, alt or cap, sizes="(max-width: 760px) 78vw, 420px")}</button><figcaption>{e(cap)}</figcaption></figure>'
        for src, cap, alt in w["figs"]
    )
    return f"""<section class="sec" id="work" aria-labelledby="w-h" data-rail>
  <div class="wrap rail-head">
    <div class="head"><h2 id="w-h" class="rv">{e(w['h2'])}</h2><p class="lede rv" style="--d:1">{e(w['lede'])}</p></div>
    <div class="rail-nav"><button type="button" data-prev aria-label="{t['prev']}">{ico('caret-left', 'flip')}</button><button type="button" data-next aria-label="{t['next']}">{ico('caret-right', 'flip')}</button></div>
  </div>
  <div class="rail" tabindex="0" aria-label="{e(w['h2'])}">{figs}</div>
</section>"""


def before_after(p, t):
    ba = p.get("before_after")
    if not ba:
        return ""
    tabs, panes = [], []
    for i, (label, before, after, alt) in enumerate(ba["pairs"]):
        sel = i == 0
        tabs.append(f'<button type="button" data-ba="{i}" aria-pressed="{str(sel).lower()}">{e(label)}</button>')
        panes.append(f"""<div class="ba-pane"{'' if sel else ' hidden'} data-pane="{i}">
        <div class="ba-stage" style="--pos:50%">
          {img(after, t['after'] + ': ' + alt, cls='ba-after', sizes='(max-width: 760px) 92vw, 560px')}
          <div class="ba-before-wrap">{img(before, t['before'] + ': ' + alt, cls='ba-before', sizes='(max-width: 760px) 92vw, 560px')}</div>
          <span class="ba-tag ba-tag-b">{t['before']}</span><span class="ba-tag ba-tag-a">{t['after']}</span>
          <span class="ba-handle" aria-hidden="true">{ico('caret-left')}{ico('caret-right')}</span>
          <input class="ba-range" type="range" min="0" max="100" value="50" aria-label="{t['ba_slider']}">
        </div>
      </div>""")
    return f"""<section class="sec ba" aria-labelledby="ba-h">
  <div class="wrap ba-grid">
    <div>
      <h2 id="ba-h" class="rv">{e(ba['h2a'])}<span class="it">{e(ba['h2b'])}</span></h2>
      <p class="lede rv" style="--d:1">{e(ba['lede'])}</p>
      <div class="seg ba-tabs rv" style="--d:2" role="group" aria-label="{e(ba['h2a'])}">{''.join(tabs)}</div>
      <p class="ba-note rv" style="--d:3">{e(ba['note'])}</p>
    </div>
    <div class="rv" style="--d:1">{''.join(panes)}</div>
  </div>
</section>"""


def concepts(p, t):
    c = p.get("concepts")
    if not c:
        return ""
    figs = "".join(
        f'<figure class="cg-{i}"><button class="ph" type="button" aria-label="{t["view"]}: {e(cap)}">{img(src, cap, sizes="(max-width: 760px) 92vw, 40vw")}</button><figcaption>{e(cap)}</figcaption></figure>'
        for i, (src, cap) in enumerate(c["figs"])
    )
    return f"""<section class="sec concepts" aria-labelledby="cg-h">
  <div class="wrap">
    <div class="head"><h2 id="cg-h" class="rv">{e(c['h2a'])}<span class="it">{e(c['h2b'])}</span></h2><p class="lede rv" style="--d:1">{e(c['lede'])}</p></div>
    <div class="cgrid rv">{figs}</div>
  </div>
</section>"""


def video(p, t):
    v = p.get("video")
    if not v:
        return ""
    return f"""<section class="sec-tight" aria-labelledby="v-hd" style="padding-bottom:var(--sec)">
  <div class="wrap vid-grid">
    <div><h2 id="v-hd" class="rv">{e(v['h2a'])}<span class="it">{e(v['h2b'])}</span></h2><p class="lede rv" style="--d:1">{e(v['lede'])}</p></div>
    <div class="vid rv" style="--d:1" data-drive="{e(v['drive_id'])}">
      {img(v['poster'], v['poster_alt'], sizes='(max-width: 760px) 92vw, 50vw')}
      <button type="button" class="vid-play" aria-label="{t['play']}: {e(v['h2a'])}"><span>{ico('caret-right')}</span>{t['play']}</button>
    </div>
  </div>
</section>"""


def reviews(p, t):
    r = p.get("reviews")
    if not r:
        return ""
    cards = []
    for i, (q, name) in enumerate(r["items"]):
        cards.append(f"""<figure class="rev{' feat' if i == 0 else ''} rv" style="--d:{i}"><span class="stars" aria-label="5 stars">{ico('star') * 5}</span><blockquote>“{e(q)}”</blockquote>
      <figcaption><div><b>{e(name)}</b><span>{t['g_review']}</span></div>{ico('google-logo', 'g')}</figcaption></figure>""")
    return f"""<section class="sec-tight" aria-labelledby="r-h" style="padding-bottom:var(--sec)">
  <div class="wrap">
    <div class="head"><h2 id="r-h" class="rv">{e(r['h2'])}</h2></div>
    <div class="reviews">{''.join(cards)}</div>
  </div>
</section>"""


def band(p, t):
    b = p.get("band")
    if not b:
        return ""
    gains = "".join(f'<div class="gain rv" style="--d:{i}"><b>{e(a)}</b><span>{e(c)}</span></div>' for i, (a, c) in enumerate(b["gains"]))
    return f"""<section class="band" aria-labelledby="b-h">
  {img(b['img'], b['img_alt'])}
  <div class="wrap">
    <h2 id="b-h" class="rv">{e(b['h2a'])}<span class="it">{e(b['h2b'])}</span></h2>
    <p class="rv" style="--d:1">{e(b['p'])}</p>
    <a class="btn rv" style="--d:2" href="#quote"><span>{t['nav_cta']}</span><span class="orb">{ico('arrow-right', 'flip')}</span></a>
    <h3 class="rv" style="margin-top:clamp(72px,9vw,120px);color:var(--cream)">{e(b['gains_h'])}</h3>
    <div class="gains">{gains}</div>
  </div>
</section>"""


def versus(p, t):
    old = "".join(f"<li>{ico('x')}<span>{e(x)}</span></li>" for x in t["v_old"])
    new = "".join(f"<li>{ico('check')}<span>{e(x)}</span></li>" for x in t["v_new"])
    return f"""<section class="sec" aria-labelledby="v-h">
  <div class="wrap">
    <div class="head"><h2 id="v-h" class="rv">{t['v_h2']}</h2><p class="lede rv" style="--d:1">{t['v_lede']}</p></div>
    <div class="versus">
      <div class="vcol v-old rv"><h3>{t['v_old_h']}</h3><ul>{old}</ul></div>
      <div class="vcol v-new rv" style="--d:1"><h3>{t['v_new_h']}</h3><ul>{new}</ul></div>
    </div>
    <p class="promise rv">{t['promise']}</p>
  </div>
</section>"""


def quote(p, t):
    q = p["quote"]
    contacts = [
        (p["wa_url"], "whatsapp-logo", t["wa_cta"], CONTACT["tel_disp"], True),
        (f"tel:{CONTACT['tel']}", "phone", t["call"], CONTACT["tel_disp"], False),
        (p["visit_url"], "map-pin", t["visit"], t["visit_sub"], True),
        (f"mailto:{CONTACT['email']}", "envelope-simple", t["email_l"], CONTACT["email"], False),
    ]
    rows = "".join(
        f'<a class="contact" href="{e(h)}"{" target=_blank rel=noopener" if blank else ""}><span class="ci">{ico(i)}</span><span><b>{e(a)}</b><span dir="ltr" style="unicode-bidi:plaintext">{e(b)}</span></span>{ico("arrow-up-right", "flip")}</a>'
        for h, i, a, b, blank in contacts
    )
    return f"""<section class="sec quote" id="quote" aria-labelledby="q-h">
  <div class="wrap quote-grid">
    <div>
      <p class="kicker rv">{t['q_kicker']}</p>
      <h2 id="q-h" class="rv" style="--d:1">{e(q['h2'])}</h2>
      <p class="lede rv" style="--d:2">{t['q_lede']}</p>
      <div class="contacts rv" style="--d:3">{rows}</div>
    </div>
    <div class="shell rv" style="--d:1"><div class="core">{form(p, t, 'f2')}</div></div>
  </div>
</section>"""


def faq(p, t):
    f = p.get("faq")
    if not f:
        return ""
    qa = "".join(f'<div class="qa rv"><h3>{e(q)}</h3><p>{e(a)}</p></div>' for q, a in f)
    return f"""<section class="sec" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="head"><h2 id="faq-h" class="rv">{t['faq_h']}</h2></div>
    <div class="faq">{qa}</div>
  </div>
</section>"""


def final(p, t):
    return f"""<section class="sec final" aria-labelledby="fin-h" style="padding-top:calc(var(--sec)*.4)">
  <div class="wrap">
    <h2 id="fin-h" class="rv">{e(p['final'])}</h2>
    <p class="lede rv" style="--d:1">{t['final_lede']}</p>
    <div class="hero-ctas rv" style="--d:2">
      <a class="btn" href="{e(p['wa_url'])}" target="_blank" rel="noopener">{t['wa_cta']}<span class="orb">{ico('whatsapp-logo')}</span></a>
      <a class="link" href="tel:{CONTACT['tel']}">{ico('phone')} {t['call']} <span dir="ltr">{CONTACT['tel_disp']}</span></a>
    </div>
  </div>
</section>"""


def footer(p, t):
    return f"""<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div><img class="logo" src="https://haustechs.ae/wp-content/uploads/2026/04/logo-002.png" alt="Haus Techs" width="184" height="46" loading="lazy">
        <address>{t['company']}<br>{t['address']}</address></div>
      <div class="foot-links">
        <a href="tel:{CONTACT['tel']}">{ico('phone')}<span dir="ltr">{CONTACT['tel_disp']}</span></a>
        <a href="{e(p['wa_url'])}" target="_blank" rel="noopener">{ico('whatsapp-logo')}{t['wa_cta']}</a>
        <a href="mailto:{CONTACT['email']}">{ico('envelope-simple')}{CONTACT['email']}</a>
        <a href="https://haustechs.ae">{ico('arrow-up-right', 'flip')}haustechs.ae</a>
      </div>
      <div><div class="socials">
        <a href="https://www.instagram.com/haus_techs/" target="_blank" rel="noopener" aria-label="Instagram">{ico('instagram-logo')}</a>
        <a href="https://www.linkedin.com/company/haus-techs/" target="_blank" rel="noopener" aria-label="LinkedIn">{ico('linkedin-logo')}</a>
      </div></div>
    </div>
    <div class="foot-base"><span>© 2026 {t['company']}</span><span>{t['tagline']}</span></div>
  </div>
</footer>
<div class="lb" id="lb" aria-hidden="true" role="dialog" aria-label="{t['view']}"><button class="lb-close" type="button" aria-label="{t['close']}">{ico('x')}</button><img alt=""><p></p></div>
<nav class="mbar" aria-label="{t['quick']}">
  <a href="tel:{CONTACT['tel']}">{ico('phone')}{t['call']}</a>
  <a class="hl" href="{e(p['wa_url'])}" target="_blank" rel="noopener">{ico('whatsapp-logo')}WhatsApp</a>
  <a href="#quote">{t['quote_short']}</a>
</nav>"""


def page_script(p):
    cfg = {
        "page": p["file"].replace(".html", ""),
        "wa": CONTACT["wa"],
        "rtl": bool(p.get("rtl")),
        "calc": {k: v for k, v in p["calc"].items() if k in ("rates", "min")},
    }
    t = p["T"]
    cfg["calc"].update({
        "designRate": 90, "designMin": 15000,
        "unit": t["unit"], "cur": t["cur"], "suffix": t.get("cur_suffix", ""),
        "labelReno": t["est_reno"], "labelDesign": t["est_design"], "designName": t["mode_design"],
    })
    return f"""<script>
window.HT = {json.dumps(cfg, ensure_ascii=False)};
HT.calc.waMsg = {p['calc_wa_js']};
HT.formWa = {p['form_wa_js']};
</script>
<script src="lp-assets/haus.js?v={ASSET_VER}" defer></script>"""


def build_page(p):
    t = p["T"]
    sections = [hero(p, t), proof(p, t), calculator(p, t)]
    sections += [sectors(p, t), communities(p, t), included(p, t), before_after(p, t), journey(p, t), work(p, t),
                 video(p, t), concepts(p, t), reviews(p, t), band(p, t), versus(p, t), quote(p, t), faq(p, t), final(p, t)]
    body = "\n".join(s for s in sections if s)
    return f"""{head(p)}
<body>
{GTM_NOSCRIPT}
{icon_sprite()}
{nav(p, t)}
<main id="main">
{body}
</main>
{footer(p, t)}
{page_script(p)}
</body>
</html>
"""


def build_thank_you(p):
    t = p["T"]
    return f"""{head(p)}
<body class="ty">
{GTM_NOSCRIPT}
{icon_sprite()}
<main id="main" class="wrap" style="min-height:100dvh;display:grid;align-content:center;justify-items:start;padding-block:64px">
  <a href="https://haustechs.ae"><img src="https://haustechs.ae/wp-content/uploads/2026/04/logo-002.png" alt="Haus Techs" width="184" height="46" style="height:46px;width:auto"></a>
  <div class="brackets" style="margin-top:clamp(56px,9vw,96px);padding:clamp(28px,5vw,56px) clamp(4px,2vw,24px);max-width:760px">
    <h1 style="max-width:16ch">{e(p['h1a'])}<span class="it">{e(p['h1b'])}</span></h1>
    <p class="lede">{e(p['p'])}</p>
    <div class="hero-ctas">
      <a class="btn" href="{e(p['wa_url'])}" target="_blank" rel="noopener">{t['wa_cta']}<span class="orb">{ico('whatsapp-logo')}</span></a>
      <a class="link" href="https://haustechs.ae">{e(p['back'])} {ico('arrow-right')}</a>
    </div>
  </div>
  <p class="muted" style="margin-top:56px;font-size:14px">{t['company']} · <a href="tel:{CONTACT['tel']}">{CONTACT['tel_disp']}</a> · <a href="mailto:{CONTACT['email']}">{CONTACT['email']}</a></p>
</main>
<!-- Event snippet for conversion page -->
<script>
  gtag('event', 'conversion', {{'send_to': 'AW-16469942753/B_1FCPKFzc4cEOHDva09'}});
</script>
</body>
</html>
"""


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "lp-assets"))
    for fn in ("haus.css", "haus.js"):
        shutil.copy(os.path.join(SRC, fn), os.path.join(DIST, "lp-assets", fn))
    shutil.copytree(os.path.join(SRC, "work"), os.path.join(DIST, "lp-images", "work"))
    for p in PAGES:
        open(os.path.join(DIST, p["file"]), "w", encoding="utf-8").write(build_page(p))
        print("built", p["file"])
    open(os.path.join(DIST, THANK_YOU["file"]), "w", encoding="utf-8").write(build_thank_you(THANK_YOU))
    print("built", THANK_YOU["file"])


if __name__ == "__main__":
    main()
