/* Haus Techs landing pages: shared behaviour.
   No scroll listeners: IntersectionObserver + CSS scroll-driven animations only.
   Page-specific data comes from window.HT (set inline by each page). */
(function () {
  'use strict';
  var HT = window.HT || {};
  var doc = document.documentElement;
  var lb = document.getElementById('lb');
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  doc.classList.add('js');

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function track(ev, data) { try { (window.dataLayer = window.dataLayer || []).push(Object.assign({ event: ev }, data || {})); } catch (e) {} }
  function wa(text) { return 'https://wa.me/' + HT.wa + '?text=' + encodeURIComponent(text); }

  /* hero intro plays once the first slide image is ready */
  var markLoaded = function () { doc.classList.add('loaded'); };
  var first = $('.hs-slide.is-on img');
  if (first && !first.complete) { first.addEventListener('load', markLoaded); setTimeout(markLoaded, 1200); } else { requestAnimationFrame(markLoaded); }

  /* nav: light logo over the dark hero, solid cream once the hero has scrolled away */
  var nav = $('.nav'), heroEl = $('.hero');
  if (nav && heroEl && 'IntersectionObserver' in window) {
    nav.classList.add('on-dark');
    new IntersectionObserver(function (es) {
      var r = es[0];
      var over = r.isIntersecting && r.boundingClientRect.bottom > 90;
      nav.classList.toggle('on-dark', over); nav.classList.toggle('solid', !over);
    }, { threshold: [0, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1], rootMargin: '-80px 0px 0px 0px' }).observe(heroEl);
  }

  /* ---------- hero slider ---------- */
  $$('[data-slider]').forEach(function (hs) {
    var hero = hs.closest('.hero'), slides = $$('.hs-slide', hs), dots = $$('.hs-dot', hero), n = slides.length, i = 0, timer = null, DUR = 6500;
    if (hero) hero.style.setProperty('--n', n);
    if (n < 2) { dots.forEach(function (d) { d.hidden = true; }); return; }
    hero.style.setProperty('--dur', DUR + 'ms');
    var go = function (k, user) {
      i = (k + n) % n;
      slides.forEach(function (s, x) { s.classList.toggle('is-on', x === i); var im = $('img', s); if (x === i && im.loading === 'lazy') im.loading = 'eager'; });
      dots.forEach(function (d, x) { d.classList.remove('is-on'); if (x === i) { void d.offsetWidth; d.classList.add('is-on'); } d.setAttribute('aria-current', String(x === i)); });
      var nx = $('img', slides[(i + 1) % n]); if (nx && nx.loading === 'lazy') nx.loading = 'eager';
      if (user) track('ht_hero_slide', { page: HT.page, slide: i });
      restart();
    };
    var restart = function () { clearTimeout(timer); if (!RM && !hero.classList.contains('paused')) timer = setTimeout(function () { go(i + 1); }, DUR); };
    dots.forEach(function (d, x) { d.addEventListener('click', function () { go(x, true); }); });
    hero.addEventListener('mouseenter', function () { if (matchMedia('(hover: hover)').matches) { hero.classList.add('paused'); clearTimeout(timer); } });
    hero.addEventListener('mouseleave', function () { hero.classList.remove('paused'); restart(); });
    document.addEventListener('visibilitychange', function () { if (document.hidden) clearTimeout(timer); else restart(); });
    var sx = null;
    hs.parentNode.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
    hs.parentNode.addEventListener('touchend', function (e) {
      if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; sx = null;
      if (Math.abs(dx) > 50 && !e.target.closest('form')) go(i + ((dx < 0) !== !!HT.rtl ? 1 : -1), true);
    }, { passive: true });
    hero.addEventListener('keydown', function (e) {
      if (!e.target.closest('.hs-nav')) return;
      if (e.key === 'ArrowRight') go(i + (HT.rtl ? -1 : 1), true);
      if (e.key === 'ArrowLeft') go(i + (HT.rtl ? 1 : -1), true);
    });
    go(0);
  });

  /* ---------- parallax (transform only, one rAF per frame) ---------- */
  var px = $$('[data-parallax]');
  if (px.length && !RM) {
    var ticking = false;
    var paint = function () {
      ticking = false;
      var vh = innerHeight;
      px.forEach(function (el) {
        var r = el.parentNode.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) return;
        var k = parseFloat(el.getAttribute('data-parallax'));
        var c = (r.top + r.height / 2) - vh / 2;
        el.style.transform = 'translate3d(0,' + (c * k).toFixed(1) + 'px,0)';
      });
    };
    addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(paint); } }, { passive: true });
    addEventListener('resize', paint); paint();
  }

  /* ---------- magnetic buttons + photo cursor (fine pointers only) ---------- */
  if (!RM && matchMedia('(hover: hover) and (pointer: fine)').matches) {
    $$('.btn').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * .14).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * .22).toFixed(1) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
    var cur = document.createElement('div'); cur.className = 'cur'; cur.setAttribute('aria-hidden', 'true'); cur.textContent = HT.rtl ? 'عرض' : 'View'; document.body.appendChild(cur);
    document.addEventListener('pointermove', function (e) {
      cur.style.setProperty('--x', e.clientX + 'px'); cur.style.setProperty('--y', e.clientY + 'px');
      cur.classList.toggle('on', !!(e.target.closest && e.target.closest('button.ph')) && !(lb && lb.classList.contains('open')));
    }, { passive: true });
  }

  /* ---------- drag-to-scroll galleries with the mouse ---------- */
  $$('.rail').forEach(function (rail) {
    var down = false, x0 = 0, s0 = 0, moved = false;
    rail.addEventListener('pointerdown', function (e) { if (e.pointerType !== 'mouse') return; down = true; moved = false; x0 = e.clientX; s0 = rail.scrollLeft; });
    addEventListener('pointermove', function (e) { if (!down) return; var dx = e.clientX - x0; if (Math.abs(dx) > 6) { moved = true; rail.classList.add('drag'); } rail.scrollLeft = s0 - dx; });
    addEventListener('pointerup', function () { if (!down) return; down = false; setTimeout(function () { rail.classList.remove('drag'); }, 0); });
    rail.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; } }, true);
  });


  /* mobile action bar appears after the hero, hides again while the quote form is on screen */
  var bar = $('.mbar'), hero = $('.hero'), quote = $('#quote');
  if (bar && hero && 'IntersectionObserver' in window) {
    var past = false, atQuote = false;
    var sync = function () { bar.classList.toggle('show', past && !atQuote); };
    new IntersectionObserver(function (es) { past = !es[0].isIntersecting; sync(); }, { threshold: 0.15 }).observe(hero);
    if (quote) new IntersectionObserver(function (es) { atQuote = es[0].isIntersecting; sync(); }, { threshold: 0.2 }).observe(quote);
  }

  /* reveal on enter, once */
  var rv = $$('.rv, .rvm, .rvi');
  if (!RM && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    rv.forEach(function (el) { io.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add('in'); });
  }

  /* stat count-up: communicates scale once, then rests */
  var nums = $$('[data-n]');
  function setN(el, v) { el.firstChild.nodeValue = String(v); }
  if (!RM && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        co.unobserve(e.target);
        var el = e.target, end = parseInt(el.getAttribute('data-n'), 10), t0 = null;
        function step(t) {
          if (!t0) t0 = t;
          var p = Math.min((t - t0) / 1200, 1);
          setN(el, Math.round(end * (1 - Math.pow(1 - p, 4))));
          if (p < 1) requestAnimationFrame(step);
        }
        setN(el, 0);
        requestAnimationFrame(step);
      });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { co.observe(el); });
  }

  /* journey steps light up as they pass the middle of the screen */
  var steps = $$('.jstep');
  if ('IntersectionObserver' in window) {
    var jo = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) e.target.classList.add('on'); });
    }, { rootMargin: '-35% 0px -45% 0px' });
    steps.forEach(function (s) { jo.observe(s); });
  } else { steps.forEach(function (s) { s.classList.add('on'); }); }

  /* tracked contact clicks (adds to, never replaces, the existing GTM setup) */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var h = a.getAttribute('href');
    if (h.indexOf('wa.me') > -1) track('ht_whatsapp_click', { page: HT.page });
    else if (h.indexOf('tel:') === 0) track('ht_call_click', { page: HT.page });
    else if (h.indexOf('mailto:') === 0) track('ht_email_click', { page: HT.page });
  });

  /* ---------- calculator (rates are editable per page in HT.calc) ---------- */
  var C = HT.calc, calc = $('#calculator');
  if (C && calc) {
    var mode = 'reno', fin = 'premium';
    var sqm = $('#calc-sqm'), sqmOut = $('#calc-sqm-val'), type = $('#calc-type');
    var res = $('#calc-result'), lbl = $('#calc-label'), finRow = $('#calc-finish');
    var fmtN = function (n) { n = Math.round(n / 1000) * 1000; return n.toLocaleString('en-US'); };
    var money = function (a, b) { return (C.cur ? C.cur + ' ' : '') + fmtN(a) + ' - ' + fmtN(b) + (C.suffix || ''); };
    var last = '';
    var run = function () {
      var v = parseInt(sqm.value, 10);
      sqmOut.textContent = v + ' ' + C.unit;
      var pct = (v - sqm.min) / (sqm.max - sqm.min) * 100;
      sqm.style.setProperty('--fill', pct + '%');
      var out;
      if (mode === 'design') {
        var fee = Math.max(v * C.designRate, C.designMin);
        out = money(fee * 0.9, fee * 1.15);
      } else {
        var t = type.value, rate = (C.rates[t] || C.rates[Object.keys(C.rates)[0]])[fin];
        var est = Math.max(v * rate, (C.min && C.min[t]) || 0);
        out = money(est * 0.88, est * 1.12);
      }
      if (out === last) return;
      last = out;
      if (RM) { res.textContent = out; return; }
      res.classList.add('swap');
      clearTimeout(run.t);
      run.t = setTimeout(function () { res.textContent = out; res.classList.remove('swap'); }, 90);
    };
    $$('[data-mode]', calc).forEach(function (b) {
      b.addEventListener('click', function () {
        mode = b.getAttribute('data-mode');
        $$('[data-mode]', calc).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        finRow.classList.toggle('off', mode === 'design');
        lbl.textContent = mode === 'design' ? C.labelDesign : C.labelReno;
        run();
      });
    });
    $$('[data-f]', calc).forEach(function (b) {
      b.addEventListener('click', function () {
        fin = b.getAttribute('data-f');
        $$('[data-f]', calc).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        run();
      });
    });
    sqm.addEventListener('input', run);
    type.addEventListener('change', run);
    run();
    var calcWa = $('#calc-wa');
    if (calcWa) calcWa.addEventListener('click', function () {
      track('ht_calc_whatsapp', { page: HT.page });
      var finName = $('[data-f="' + fin + '"] b', calc).textContent;
      window.open(wa(C.waMsg(type.value, sqm.value, mode === 'design' ? C.designName : finName, res.textContent)), '_blank', 'noopener');
    });
  }

  /* ---------- forms: inline validation, native POST to send-lead.php ---------- */
  $$('form.lead').forEach(function (f) {
    var started = false;
    f.addEventListener('focusin', function () { if (!started) { started = true; track('ht_form_start', { page: HT.page, form: f.id }); } });
    function check(field) {
      var el = $('input,select,textarea', field); if (!el) return true;
      var ok = el.checkValidity();
      if (ok && el.name === 'phone') ok = (el.value.replace(/\D/g, '').length >= 7);
      field.classList.toggle('bad', !ok);
      el.setAttribute('aria-invalid', String(!ok));
      return ok;
    }
    $$('.field', f).forEach(function (fd) {
      var el = $('input,select,textarea', fd);
      if (el) el.addEventListener('blur', function () { if (el.value) check(fd); });
      if (el) el.addEventListener('input', function () { if (fd.classList.contains('bad')) check(fd); });
    });
    f.addEventListener('submit', function (e) {
      var bad = $$('.field', f).filter(function (fd) { return !check(fd); });
      if (bad.length) { e.preventDefault(); var el = $('input,select,textarea', bad[0]); el && el.focus(); return; }
      if (HT.preview) { e.preventDefault(); var n = $('.form-note', f); if (n) n.textContent = 'Preview: the form checks passed. On the live site this goes to your project desk.'; return; }
      var b = $('button[type=submit]', f);
      b.classList.add('sending'); b.disabled = true;
      setTimeout(function () { b.disabled = false; b.classList.remove('sending'); }, 6000);
      track('ht_form_submit', { page: HT.page, form: f.id });
    });
    var waBtn = $('[data-wa-form]', f);
    if (waBtn) waBtn.addEventListener('click', function () {
      var d = {}; ['name', 'phone', 'location', 'detail', 'message'].forEach(function (n) { var el = f.elements[n]; d[n] = el ? el.value : ''; });
      track('ht_form_whatsapp', { page: HT.page, form: f.id });
      window.open(wa(HT.formWa(d)), '_blank', 'noopener');
    });
  });

  /* ---------- work rail ---------- */
  $$('[data-rail]').forEach(function (wrap) {
    var rail = $('.rail', wrap), prev = $('[data-prev]', wrap), next = $('[data-next]', wrap);
    if (!rail || !prev) return;
    var dir = HT.rtl ? -1 : 1;
    var stepBy = function () { var f = $('figure', rail); return f ? f.getBoundingClientRect().width + 16 : 400; };
    prev.addEventListener('click', function () { rail.scrollBy({ left: -stepBy() * dir, behavior: RM ? 'auto' : 'smooth' }); });
    next.addEventListener('click', function () { rail.scrollBy({ left: stepBy() * dir, behavior: RM ? 'auto' : 'smooth' }); });
    var figs = $$('figure', rail);
    if ('IntersectionObserver' in window && figs.length) {
      var seen = {};
      var ro = new IntersectionObserver(function (es) {
        es.forEach(function (e) { seen[figs.indexOf(e.target)] = e.intersectionRatio > 0.9; });
        prev.disabled = !!seen[0]; next.disabled = !!seen[figs.length - 1];
      }, { root: rail, threshold: [0, 0.9, 1] });
      figs.forEach(function (f) { ro.observe(f); });
    }
  });

  /* ---------- lightbox ---------- */
  if (lb) {
    var lbImg = $('img', lb), lbCap = $('p', lb), lastFocus = null;
    var close = function () { lb.classList.remove('open'); lb.setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); };
    $$('button.ph').forEach(function (b) {
      b.addEventListener('click', function () {
        var im = $('img', b); lastFocus = b;
        lbImg.src = im.currentSrc || im.src; lbImg.alt = im.alt;
        var cap = b.parentNode.querySelector('figcaption'); lbCap.textContent = cap ? cap.textContent : '';
        lb.classList.add('open'); lb.setAttribute('aria-hidden', 'false'); document.body.style.overflow = 'hidden';
        $('.lb-close', lb).focus();
      });
    });
    lb.addEventListener('click', function (e) { if (e.target !== lbImg) close(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && lb.classList.contains('open')) close(); });
  }

  /* ---------- tabs (commercial sectors) ---------- */
  $$('[role=tablist]').forEach(function (tl) {
    var tabs = $$('[role=tab]', tl);
    var show = function (t, focus) {
      tabs.forEach(function (x) {
        var on = x === t; x.setAttribute('aria-selected', String(on)); x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute('aria-controls')).hidden = !on;
      });
      if (focus) t.focus();
    };
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(t); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = null;
        if (k === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (k === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (n) { e.preventDefault(); show(n, true); }
      });
    });
  });


  /* ---------- before / after: range input drives a clip-path (keyboard + touch accessible) ---------- */
  $$('.ba').forEach(function (sec) {
    $$('.ba-range', sec).forEach(function (r) {
      var stage = r.closest('.ba-stage');
      var set = function () { var v = HT.rtl ? 100 - r.value : r.value; stage.style.setProperty('--pos', v + '%'); };
      r.addEventListener('input', set); set();
    });
    if (!RM && 'IntersectionObserver' in window) {
      var hint = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return; hint.disconnect();
        var r = $('.ba-pane:not([hidden]) .ba-range', sec); if (!r) return;
        var keys = [50, 22, 78, 50], k = 0, from = 50, t0 = null;
        var step = function (t) {
          if (!t0) t0 = t; var p = Math.min((t - t0) / 700, 1), ease = 1 - Math.pow(1 - p, 3);
          r.value = from + (keys[k + 1] - from) * ease; r.dispatchEvent(new Event('input'));
          if (p < 1) return requestAnimationFrame(step);
          k++; from = keys[k]; t0 = null; if (k < keys.length - 1) requestAnimationFrame(step);
        };
        setTimeout(function () { requestAnimationFrame(step); }, 500);
      }, { threshold: 0.5 });
      hint.observe(sec);
    }
    $$('[data-ba]', sec).forEach(function (b) {
      b.addEventListener('click', function () {
        var i = b.getAttribute('data-ba');
        $$('[data-ba]', sec).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        $$('[data-pane]', sec).forEach(function (p) { p.hidden = p.getAttribute('data-pane') !== i; });
        track('ht_before_after', { page: HT.page, pair: i });
      });
    });
  });

  /* ---------- video: Drive player loads only on demand ---------- */
  $$('.vid[data-drive]').forEach(function (v) {
    var btn = $('.vid-play', v);
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://drive.google.com/file/d/' + v.getAttribute('data-drive') + '/preview';
      f.allow = 'autoplay; fullscreen'; f.setAttribute('allowfullscreen', ''); f.title = btn.getAttribute('aria-label');
      v.appendChild(f); btn.remove();
      track('ht_video_play', { page: HT.page });
    });
  });

  /* hide a work photo whose file is missing, so a broken image never shows */
  $$('img[data-soft]').forEach(function (im) {
    var hide = function () { var f = im.closest('figure') || im.closest('.tile'); if (f) f.style.display = 'none'; };
    im.addEventListener('error', hide);
    if (im.complete && im.naturalWidth === 0) hide();
  });
})();
