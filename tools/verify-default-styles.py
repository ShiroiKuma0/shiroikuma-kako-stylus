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
# Allowlisted styles reach only their listed sites. They are still injected here, because this
# fixture tests what the CSS *does*; where it applies is decided by inclusions, not by the rules.
allowlisted = [s["name"] for s in lib if s.get("overridden")]

sheets = "\n".join(
    '<style data-name="%s" data-rules="%d">%s</style>'
    % (html.escape(s["name"]), s["sections"][0]["code"].count("{"), s["sections"][0]["code"])
    for s in globals_
)

PAGE = """<!doctype html><meta charset="utf-8"><title>verify</title>
<style id="page">
  /* a plausible site, including the `!important` fights that broke earlier versions */
  /* the forum.mobilism.org pattern: a light wallpaper on <body> that black paints behind */
  body { font-family: Georgia, serif; line-height: 1.8; color: #333;
         background: #fff linear-gradient(#ccc, #e8e8e8); }
  .fa { font-family: "Font Awesome 6 Free"; font-weight: 900; line-height: 1; }
  .material-icons { font-family: "Material Icons"; }
  .navIcon { font-family: "SiteIcons"; }
  .card { line-height: 1.6; background: #ffffff !important; border: 2px solid #d0d7de; }
  #sidebar { background: #ffffff !important; }
  .whiteBar { background: #ffffff !important; }
  .article { max-width: 320px !important; }
  /* the substack.com pattern: a centred column pinned by width, not max-width */
  .fixedCol { width: 300px; margin: 0 auto; }
  .glossBtn { background-image: linear-gradient(#fff, #ddd); }
  a { color: #0066cc; }
  a.styled { color: #0066cc !important; }
  .cta { background: #00cfff !important; color: #fff !important; border: 1px solid #000; }
  /* the alza.cz cookie pattern: the "accept" action is an <a>, not a <button> */
  .cookieAccept { background: #00cfff !important; color: #003 !important; border-radius: 6px; }
  hr { border: 0; border-top: 1px solid #d0d7de; }
  input.q { background: #fff !important; color: #111 !important; border: 1px solid #ccc; }
  img { max-width: 100%; }
  /* the alza.cz carousel pattern: a transparent ::before overlay inside a stacking context,
     used for a hover shade. Painting it black covers everything beneath it. */
  .tile { position: relative; isolation: isolate; width: 120px; height: 80px; }
  .tile::before { content: ""; position: absolute; inset: 0; background: transparent; }
  /* a transparent full-width host pinned to the bottom, the alza.cz #fixedBottom pattern */
  .pageOverlay { position: fixed; bottom: 0; width: 100%; height: 40px; pointer-events: none; }
  /* Material UI's clickable: the ripple layer is the LAST child and covers the item's own
     label, so painting it hides the label. alza.cz's category sidebar, all 24 rows of it. */
  .MuiButtonBase-root { position: relative; display: block; width: 200px; }
  .MuiTouchRipple-root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
  .gradientBar { background-image: linear-gradient(#fff, #eee) !important; height: 8px; }
  .spriteIcon { background-image: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="); }
  /* the jisho.org pattern: a logo drawn as a background behind text that is then hidden */
  /* the vBulletin pattern: a tiled gradient strip on a table cell that holds text */
  td.thead { background-image: linear-gradient(#6989b4, #4a6d99); }
  .brandLogo { background-image: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="); display: block; width: 88px; height: 42px; text-indent: -9999px; }
  /* reCAPTCHA's footer controls: an empty <button> whose entire label is a background
     image, drawn as black ink on transparency */
  .rc-button { background: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==") no-repeat center; width: 48px; height: 48px; }
  .iconClass { background-image: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="); width: 48px; height: 48px; }
  /* the floating-label field: an opaque label inset over the input, the Piano pattern */
  .fieldGroup { position: relative; display: block; width: 260px; }
  /* the room the site made for its leading envelope — ours must not shrink it */
  .fieldGroup input { padding-left: 34px; }
  .floatLabel { position: absolute; inset: 11px 0 0 3px; background: #ffffff; }
  .plainSpan { background: #eeeeee; }
  /* the design tokens a Tailwind v4 site declares, and a shadow-DOM widget then reads by
     inheritance — `:root` inside a shadow stylesheet matches nothing, so the value it sees is
     this one, which is why moving it here reaches inside the sealed tree */
  :root { --foreground: #0a0a0a; --muted-foreground: #737373; }
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
  <input type="submit" id="submit" value="Search">
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
  <div class="fixedCol" id="fixedcol">a column pinned by width</div>
  <button class="glossBtn" id="gloss">Search</button>
  <div class="tile" id="tile"><img id="tileimg" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></div>
  <div class="pageOverlay" id="overlay"></div>
  <!-- a component library's clickable, ripple layer last: MUI, Vuetify and Angular Material all
       build it as a transparent, pointer-events:none span laid over the item's own content -->
  <a class="MuiButtonBase-root MuiListItemButton-root" id="muiItem" href="#"
    ><span class="MuiListItemText-primary" id="muiLabel">Alza dny</span
    ><span class="MuiTouchRipple-root" id="muiRipple"></span></a>
  <!-- the other sense of the word: Material Components Web marks the button ITSELF, and that is
       a surface which must keep its ground rather than a layer to see through -->
  <button class="mdc-button mdc-ripple-upgraded" id="mdcBtn">Buy</button>
  <!-- an icon control: empty, and its background image is the only label it has -->
  <button class="rc-button rc-button-reload" id="iconBtn" title="Get a new challenge"></button>
  <!-- the other kind of icon control: the glyph is drawn with `color`, so its ground
       must stay black or a yellow glyph would land on mid grey -->
  <button class="iconClass" id="iconClsBtn" title="Close"></button>
  <!-- a floating-label field: the label FOLLOWS its input, because that is what makes
       `input:not(:placeholder-shown) + label` expressible, and is laid back over the input's own
       text line. unherd.com's registration box, where painting it swallowed every keystroke. -->
  <p class="fieldGroup" id="fieldGroup"><input id="flInput" type="text" value="typed text"
    ><span class="floatLabel" id="flLabel"><i class="mailIcon" id="flIcon"></i>Email address</span></p>
  <!-- ... while a span that follows no control is ordinary content and keeps its ground -->
  <div id="plainWrap"><input id="plainInp" type="text" value="nothing beside me"></div>
  <span class="plainSpan" id="plainSpan">not a field label</span>
  <!-- a widget sealed in a shadow root: nothing we inject reaches inside it, so the only route
       is what inherits through the host — which is what `ui: design tokens` exists for -->
  <div id="shadowHost"></div>
  <!-- an extension's in-page overlay, positioned and sized with inline styles -->
  <div id="inlineMark" style="position:absolute;width:41px;height:12px;border:1px solid yellow"></div>
  <div class="gradientBar" id="gradbar"></div>
  <span class="spriteIcon" id="sprite"></span>
  <h1 class="logoWrap"><a class="brandLogo" id="logo" href="#">Jisho</a></h1>
  <table><tr><td class="thead" id="thead">Forum header cell</td></tr></table>
  <div class="gradientBar" id="gradbar-ws">   </div>
  <img id="img" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
  <svg id="inline-svg" width="12" height="12"><rect width="12" height="12"/></svg>
<script>
const g = id => getComputedStyle(document.getElementById(id));
const g2 = sel => getComputedStyle(document.querySelector(sel));
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
t('the page wallpaper is cleared, not just painted behind',
  g2('body').backgroundImage, g2('body').backgroundImage === 'none');
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
t('input[type=submit] is treated as a button',
  g('submit').backgroundColor + ' / ' + g('submit').color + ' / ' + g('submit').outlineColor,
  g('submit').backgroundColor === BLACK && g('submit').color === YELLOW
    && g('submit').outlineColor === YELLOW);
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
t('an inline-sized overlay keeps its geometry (extension marks, tooltips, region selectors)',
  g('inlineMark').width, g('inlineMark').width === '41px');
t('a column pinned by width (not max-width) is released too',
  g('fixedcol').width, g('fixedcol').width !== '300px');
t('a control loses its gloss gradient, so black actually shows',
  g('gloss').backgroundImage, g('gloss').backgroundImage === 'none');
t('images keep their max-width', g('img').maxWidth, g('img').maxWidth !== 'none');

// --- decorative pseudo-elements --------------------------------------------
{
  const before = getComputedStyle(document.getElementById('tile'), '::before');
  t('a transparent ::before overlay is NOT painted black (it would cover the content)',
    before.backgroundColor, before.backgroundColor === 'rgba(0, 0, 0, 0)');
}

t('an element named as an overlay is left transparent, not painted into a sheet',
  g('overlay').backgroundColor, g('overlay').backgroundColor === 'rgba(0, 0, 0, 0)');

t('a ripple layer stays transparent (painted, it hides the label underneath it)',
  g('muiRipple').backgroundColor, g('muiRipple').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the label under the ripple still gets its own ground and colour',
  g('muiLabel').backgroundColor + ' / ' + g('muiLabel').color,
  g('muiLabel').backgroundColor === 'rgb(0, 0, 0)' && g('muiLabel').color === 'rgb(0, 255, 255)');
t('a button merely MARKED as a ripple surface keeps its ground',
  g('mdcBtn').backgroundColor, g('mdcBtn').backgroundColor === 'rgb(0, 0, 0)');

// --- icon controls: the image IS the label ---------------------------------
t('an empty control keeps the background image that IS its label',
  g('iconBtn').backgroundImage === 'none' ? 'none' : 'kept',
  g('iconBtn').backgroundImage !== 'none');
t('and gets a ground its ink can survive rather than black',
  g('iconBtn').backgroundColor, g('iconBtn').backgroundColor === 'rgb(128, 128, 128)');
t('a labelled control still loses its gloss gradient',
  g('gloss').backgroundImage, g('gloss').backgroundImage === 'none');
t('an empty control whose class says icon keeps the black ground (its glyph uses color)',
  g('iconClsBtn').backgroundColor + ' / ' + g('iconClsBtn').color,
  g('iconClsBtn').backgroundColor === BLACK && g('iconClsBtn').color === YELLOW);

// --- the field's own floating label ---------------------------------------
t('a floating label is NOT painted (painted, the field eats every keystroke)',
  g('flLabel').backgroundColor, g('flLabel').backgroundColor === 'rgba(0, 0, 0, 0)');
t('nor is the leading icon it carries',
  g('flIcon').backgroundColor, g('flIcon').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the field under it still shows what is typed',
  g('flInput').backgroundColor + ' / ' + g('flInput').color,
  g('flInput').backgroundColor === BLACK && g('flInput').color === YELLOW);
t('a field with a leading adornment keeps the room the site made for it',
  g('flInput').paddingLeft, g('flInput').paddingLeft === '34px');
t('a field with nothing beside it still gets the pill padding',
  g('plainInp').paddingLeft + ' vs 0.7em of ' + g('plainInp').fontSize,
  Math.abs(parseFloat(g('plainInp').paddingLeft) - 0.7 * parseFloat(g('plainInp').fontSize)) < 0.5);
t('a span that follows no control is content and keeps its ground',
  g('plainSpan').backgroundColor, g('plainSpan').backgroundColor === BLACK);

// --- design tokens, the only thing that crosses a shadow boundary ----------
const tok = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
t('the page ink token is moved off the site value', tok('--foreground'),
  tok('--foreground') === '#ffff00');
{
  // A CoEditor-shaped widget: its stylesheet lives inside the shadow root, where none of our
  // rules apply and its own `:root` matches nothing. Only the inherited token reaches it.
  const sr = document.getElementById('shadowHost').attachShadow({mode: 'open'});
  sr.innerHTML = '<style>:root{--foreground:#0a0a0a;--muted-foreground:#737373}'
    + '.text-foreground{color:var(--foreground)}'
    + '.text-muted-foreground{color:var(--muted-foreground)}</style>'
    + '<p class="text-foreground" id="sdBody">a comment body</p>'
    + '<p class="text-muted-foreground" id="sdTime">3d ago</p>'
    + '<p id="sdPlain">an author name, no colour class of its own</p>';
  const sd = id => getComputedStyle(sr.getElementById(id));
  t('shadow-DOM body text is reached through the token', sd('sdBody').color,
    sd('sdBody').color === YELLOW);
  t('shadow-DOM secondary text keeps a rank of its own', sd('sdTime').color,
    sd('sdTime').color === 'rgb(153, 153, 0)');
  t('shadow-DOM text with no colour class inherits through the host', sd('sdPlain').color,
    sd('sdPlain').color === YELLOW);
}

// --- transparent artwork ---------------------------------------------------
t('image ground is mid grey, so neither dark nor light ink can vanish',
  g('img').backgroundColor, g('img').backgroundColor === 'rgb(128, 128, 128)');
t('inline svg gets no ground (it follows currentColor already)',
  g('inline-svg').backgroundColor, g('inline-svg').backgroundColor === BLACK);
t('a decorative background-image is removed (strip-backdrops now ships on)',
  g('gradbar').backgroundImage, g('gradbar').backgroundImage === 'none');
t('a sprite icon keeps its background-image', g('sprite').backgroundImage,
  g('sprite').backgroundImage !== 'none');
t('a table cell loses its gradient strip (from bg blocks, not strip-backdrops)',
  g('thead').backgroundImage, g('thead').backgroundImage === 'none');
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
print("%s  <-  %s (%d enabled global styles; off by default: %s; allowlisted: %s)"
      % (out, os.path.basename(lib_path), len(globals_),
         ", ".join(disabled) or "none", ", ".join(allowlisted) or "none"))
