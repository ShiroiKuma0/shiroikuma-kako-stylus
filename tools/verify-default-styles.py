#!/usr/bin/env python3
"""Behavioural test for the fork's preinstalled style library.

Builds .scratch/verify.html -- a fixture page that fights back the way real sites do: its own
Font Awesome and Material Icons, a hand-rolled icon font, a narrow article column, grey dividers,
and a set of `!important` rules at class and id specificity trying to stay white.  The library's
global styles are injected over it and the resulting computed styles are asserted.

Run the page in both engines:

  chromium --headless --disable-gpu --no-sandbox --virtual-time-budget=3000 \\
    --dump-dom "file://$PWD/.scratch/verify.html"
  firefox --headless --profile "$PWD/.scratch/ffprof" --window-size=1000,900 \\
    --screenshot "$PWD/.scratch/verify-gecko.png" "file://$PWD/.scratch/verify.html"

Gecko is the engine that ships, so its answer is the one that counts.
"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lib_path = os.path.join(ROOT, "src", "background", "fork-default-styles.json")
lib = json.load(open(lib_path, encoding="utf-8"))
# Only the global styles apply on an arbitrary page — and only the ones shipped enabled.
globals_ = [s for s in lib if not s["sections"][0]["domains"] and s["enabled"]]
disabled = [s["name"] for s in lib if not s["enabled"]]

sheets = "\n".join(
    '<style data-name="%s" data-rules="%d">%s</style>'
    % (html.escape(s["name"]), s["sections"][0]["code"].count("{"), s["sections"][0]["code"])
    for s in globals_
)

PAGE = """<!doctype html><meta charset="utf-8"><title>verify</title>
<style id="page">
  /* a plausible site, including the `!important` fights that broke earlier versions */
  body { font-family: Georgia, serif; line-height: 1.8; color: #333; background: #fff; }
  .fa { font-family: "Font Awesome 6 Free"; font-weight: 900; line-height: 1; }
  .material-icons { font-family: "Material Icons"; }
  .navIcon { font-family: "SiteIcons"; }
  .card { line-height: 1.6; background: #ffffff !important; border: 2px solid #d0d7de; }
  #sidebar { background: #ffffff !important; }
  .whiteBar { background: #ffffff !important; }
  .article { max-width: 320px !important; }
  a { color: #0066cc; }
  a.styled { color: #0066cc !important; }
  .cta { background: #00cfff !important; color: #fff !important; border: 1px solid #000; }
  /* the alza.cz cookie pattern: the "accept" action is an <a>, not a <button> */
  .cookieAccept { background: #00cfff !important; color: #003 !important; border-radius: 6px; }
  hr { border: 0; border-top: 1px solid #d0d7de; }
  input.q { background: #fff !important; color: #111 !important; border: 1px solid #ccc; }
  img { max-width: 100%; }
  .gradientBar { background-image: linear-gradient(#fff, #eee) !important; height: 8px; }
  .spriteIcon { background-image: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="); }
  /* the jisho.org pattern: a logo drawn as a background behind text that is then hidden */
  .brandLogo { background-image: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="); display: block; width: 88px; height: 42px; text-indent: -9999px; }
</style>
__SHEETS__
<body>
  <div class="card" id="card">
    <p id="para">Body copy here.</p>
    <i class="fa fa-user" id="icon-fa" aria-hidden="true"></i>
    <span class="material-icons" id="icon-mat">search</span>
    <span class="navIcon" id="icon-nav"><span id="icon-child">child</span></span>
    <svg id="icon-svg" width="16" height="16"><rect width="16" height="16"/></svg>
    <i id="italic">genuinely italic prose</i>
    <a href="https://example.com/unvisited-xyz" id="link"><span id="link-span">link text</span>
      <i class="fa fa-star" id="link-icon"></i></a>
    <a href="https://example.com/o" class="styled" id="link-styled">page-important link</a>
    <button id="btn">Press</button>
    <button class="cta" id="cta">Rozum&iacute;m</button>
  <a class="cookieAccept" id="jslink" href="javascript:acceptAll();">Rozum&iacute;m</a>
  <a class="btn-primary" id="clslink" href="/x">Podrobn&eacute; nastaven&iacute;</a>
    <input id="inp" class="q" placeholder="type">
    <textarea id="ta" placeholder="type more"></textarea>
    <hr id="rule">
    <pre id="pre"><code id="code">const <span id="code-span">x</span> = 1;</code></pre>
  </div>
  <div id="sidebar">sidebar</div>
  <div class="whiteBar" id="whitebar">top bar</div>
  <div class="article" id="article">a narrow article column</div>
  <div class="gradientBar" id="gradbar"></div>
  <span class="spriteIcon" id="sprite"></span>
  <h1 class="logoWrap"><a class="brandLogo" id="logo" href="#">Jisho</a></h1>
  <div class="gradientBar" id="gradbar-ws">   </div>
  <img id="img" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
  <svg id="inline-svg" width="12" height="12"><rect width="12" height="12"/></svg>
<script>
const g = id => getComputedStyle(document.getElementById(id));
const fs = id => getComputedStyle(document.getElementById(id)).fontSize;
const BLACK = 'rgb(0, 0, 0)', YELLOW = 'rgb(255, 255, 0)', CYAN = 'rgb(0, 255, 255)';
const checks = [];
const t = (name, got, ok) => checks.push({name, got: String(got), ok: !!ok});

// --- did the engine accept every rule we wrote? --------------------------
let dropped = [];
for (const el of document.querySelectorAll('style[data-name]')) {
  const want = +el.dataset.rules, got = el.sheet ? el.sheet.cssRules.length : -1;
  if (got !== want) dropped.push(`${el.dataset.name}: wrote ${want}, engine kept ${got}`);
}
t('every rule accepted by the engine', dropped.join(' | ') || 'all kept', !dropped.length);

// --- the blanket, now against pages that fight back ----------------------
t('prose colour is yellow', g('para').color, g('para').color === YELLOW);
t('div background is black', g('card').backgroundColor, g('card').backgroundColor === BLACK);
t('beats .card{background !important}', g('card').backgroundColor,
  g('card').backgroundColor === BLACK);
t('beats #sidebar{background !important}', g('sidebar').backgroundColor,
  g('sidebar').backgroundColor === BLACK);
t('beats .whiteBar{background !important}', g('whitebar').backgroundColor,
  g('whitebar').backgroundColor === BLACK);
t('prose font is Arial', g('para').fontFamily, /Arial/.test(g('para').fontFamily));
t('prose line-height is 1em', g('para').lineHeight + ' vs ' + fs('para'),
  g('para').lineHeight === fs('para'));

// --- borders and dividers -------------------------------------------------
t('card border is yellow', g('card').borderTopColor, g('card').borderTopColor === YELLOW);
t('hr is yellow', g('rule').borderTopColor + ' / ' + g('rule').backgroundColor,
  g('rule').borderTopColor === YELLOW && g('rule').backgroundColor === YELLOW);

// --- icon repair ----------------------------------------------------------
t('FA icon keeps its font', g('icon-fa').fontFamily, /Font Awesome/.test(g('icon-fa').fontFamily));
t('Material icon keeps its font', g('icon-mat').fontFamily, /Material Icons/.test(g('icon-mat').fontFamily));
t('site icon class keeps its font', g('icon-nav').fontFamily, /SiteIcons/.test(g('icon-nav').fontFamily));
t('FA icon line-height is normal', g('icon-fa').lineHeight, g('icon-fa').lineHeight === 'normal');
t('svg line-height is normal', g('icon-svg').lineHeight, g('icon-svg').lineHeight === 'normal');
t('child of an icon still gets Arial (:not is per-element)',
  g('icon-child').fontFamily, /Arial/.test(g('icon-child').fontFamily));

// --- links ----------------------------------------------------------------
t('link is cyan', g('link').color, g('link').color === CYAN);
t('span inside link is cyan', g('link-span').color, g('link-span').color === CYAN);
t('icon inside a link stays yellow', g('link-icon').color, g('link-icon').color === YELLOW);
t('beats page .styled{color !important}', g('link-styled').color, g('link-styled').color === CYAN);

// --- controls -------------------------------------------------------------
t('button is black with a yellow trace',
  g('btn').backgroundColor + ' / ' + g('btn').outlineColor + ' ' + g('btn').outlineWidth,
  g('btn').backgroundColor === BLACK && g('btn').outlineColor === YELLOW
    && g('btn').outlineWidth === '1px');
t('beats .cta{background+color !important}',
  g('cta').backgroundColor + ' / ' + g('cta').color,
  g('cta').backgroundColor === BLACK && g('cta').color === YELLOW);
t('button trace costs no layout', g('btn').outlineOffset, g('btn').outlineOffset === '-1px');
t('buttons are pills', g('btn').borderRadius, g('btn').borderRadius === '999px');
t('a href="javascript:" is treated as a button, not a link',
  g('jslink').backgroundColor + ' / ' + g('jslink').color + ' / ' + g('jslink').borderRadius
    + ' / ' + g('jslink').outlineColor,
  g('jslink').backgroundColor === BLACK && g('jslink').color === YELLOW
    && g('jslink').borderRadius === '999px' && g('jslink').outlineColor === YELLOW);
t('a.btn-* likewise', g('clslink').color + ' / ' + g('clslink').borderRadius,
  g('clslink').color === YELLOW && g('clslink').borderRadius === '999px');
t('an ordinary link is NOT turned into a button',
  g('link').borderRadius + ' / ' + g('link').color,
  g('link').borderRadius !== '999px' && g('link').color === CYAN);
t('text input is a traced yellow pill',
  g('inp').backgroundColor + ' / ' + g('inp').color + ' / ' + g('inp').borderRadius
    + ' / ' + g('inp').outlineColor + ' ' + g('inp').outlineWidth,
  g('inp').backgroundColor === BLACK && g('inp').color === YELLOW
    && g('inp').borderRadius === '999px' && g('inp').outlineColor === YELLOW
    && g('inp').outlineWidth === '1px');
t('input pill beats input.q{...!important}', g('inp').backgroundColor,
  g('inp').backgroundColor === BLACK);
t('textarea stays a traced black box',
  g('ta').backgroundColor + ' / ' + g('ta').color,
  g('ta').backgroundColor === BLACK && g('ta').color === YELLOW);

// --- code -----------------------------------------------------------------
t('code is monospace', g('code').fontFamily, /Mono|monospace|Consolas/.test(g('code').fontFamily));
t('code is grey not yellow', g('code').color, g('code').color === 'rgb(224, 224, 224)');
t('span inside code inherits grey', g('code-span').color, g('code-span').color === 'rgb(224, 224, 224)');

// --- full width -----------------------------------------------------------
t('narrow column is released', g('article').maxWidth, g('article').maxWidth === 'none');
t('images keep their max-width', g('img').maxWidth, g('img').maxWidth !== 'none');

// --- transparent artwork ---------------------------------------------------
t('image ground is mid grey, so neither dark nor light ink can vanish',
  g('img').backgroundColor, g('img').backgroundColor === 'rgb(128, 128, 128)');
t('inline svg gets no ground (it follows currentColor already)',
  g('inline-svg').backgroundColor, g('inline-svg').backgroundColor === BLACK);
t('a decorative background-image is LEFT ALONE by default (strip-backdrops ships off)',
  g('gradbar').backgroundImage, g('gradbar').backgroundImage !== 'none');
t('a sprite icon keeps its background-image', g('sprite').backgroundImage,
  g('sprite').backgroundImage !== 'none');
t('a logo drawn as a background behind text SURVIVES (the jisho.org pattern)',
  g('logo').backgroundImage, g('logo').backgroundImage !== 'none');
checks.push({name: 'NOTE :empty vs whitespace-only element', ok: true,
             got: g('gradbar-ws').backgroundImage === 'none' ? 'whitespace ignored, stripped'
                                                             : 'whitespace counts, kept'});

// --- known trade-off, reported not asserted -------------------------------
checks.push({name: 'NOTE italic <i> keeps page font (accepted trade-off)',
             got: g('italic').fontFamily, ok: true});

const fails = checks.filter(c => !c.ok);
const out = document.createElement('pre');
out.id = 'results';
out.textContent = checks.map(c => (c.ok ? 'PASS  ' : 'FAIL  ') + c.name + '  ->  ' + c.got).join('\\n')
  + '\\n\\n' + (fails.length ? fails.length + ' FAILED' : 'ALL ' + checks.length + ' PASSED');
out.setAttribute('style', 'all:initial;display:block;white-space:pre;font:13px monospace;'
  + 'background:#000;color:' + (fails.length ? '#ff5555' : '#00ff00') + ';padding:12px');
document.body.replaceChildren(out);
</script>
"""
out = os.path.join(ROOT, ".scratch", "verify.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(PAGE.replace("__SHEETS__", sheets))
print("%s  <-  %s (%d enabled global styles; off by default: %s)"
      % (out, os.path.basename(lib_path), len(globals_), ", ".join(disabled) or "none"))
