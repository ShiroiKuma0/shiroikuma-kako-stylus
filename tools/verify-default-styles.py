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
  /* a video player's transport bar: the icon-font codepoint is drawn on the ::before of the
     CONTROL itself, under class names that say nothing at all -- play-control, mute-control */
  .pl-control { position: relative; width: 36px; height: 36px; display: inline-block; }
  .pl-control.pl-button::before { position: absolute; top: 50%; left: 50%;
      content: "\\e605"; font-family: "PlayerIcons", sans-serif; font-size: 24px; }
  /* ...and the element side of it: the font is declared on the ELEMENT and the knob drawn in a
     ::before that inherits it, which is why `vjs-` is on the sans blanket's exclusion list */
  .vjs-volume-level { font-family: "VideoJS"; }
  .vjs-volume-level::before { content: "\\f116"; }
  /* ...while a pseudo the page gave no font of its own is prose decoration, and must still come
     out Arial -- by inheritance from its originating element, not from a rule of ours */
  .pullquote::before { content: "\\201C"; }
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
  /* the other layer that blanks a page outright, and the one ui: overlays cannot reach: a payment
     SDK parks a transparent full-viewport iframe at the top of the stack, waiting for a card
     challenge that may never come. Black, it is an opaque sheet nothing can be above. */
  .payFrame { position: fixed; inset: 0; width: 100%; height: 100%; z-index: 2147483647;
              border: 0; }
  /* the layer that blanks a page outright: empty, click-through, the size of the viewport, and
     left in the DOM for a toast that never comes or a gate already dismissed, and named
     nothing a style could match */
  .toastHost { position: fixed; inset: 0; z-index: 1060; pointer-events: none; }
  /* a product tile, and the two ways it turns black. The whole-card click target is one <a>
     laid over the tile showing nothing of its own -- and NOT :empty, because the accessible name
     is a text node with a data element beside it. The cover under it is stacked behind the page
     with z-index:-1, which works only while every ancestor is transparent. */
  .tileCard { position: relative; display: block; width: 160px; }
  .cardLink { position: absolute; top: 0; left: 0; width: 100%; height: 100%;
              font-size: 0; color: transparent; background-color: transparent; }
  .cardCover { position: relative; z-index: -1; display: block; background: #ffffff; }
  /* a value bar: a track, and inside it an empty filled part whose width IS the reading.
     Substack's volume slider, hashed class and all, plus its seek bar */
  .volumeBar-N1rUCF { background-color: #d0d0d066; width: 0; height: 4px; position: relative;
      overflow: hidden; transition: width .3s ease-in-out; }
  .volRow.hovered .volumeBar-N1rUCF { width: 100px; }
  .volumeLevel-VDMLnw { background-color: #fff; height: 4px; }
  .timelineTrack { background-color: #d0d0d066; width: 300px; height: 4px; position: relative; }
  .progress-K0IenH { background-color: #fff; position: absolute; inset: 0 auto 0 0; width: 40%; }
  /* a video player: role=button around the <video>, with the poster frame drawn as a background
     image on the button that covers it until you press play */
  .playerRoot { position: relative; width: 320px; height: 180px; border-radius: 8px; }
  .videoPlaceholderWithPoster { width: 320px; height: 180px; border-radius: 8px;
      background: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==") center/cover; }
  /* the CSS-triangle idiom: two transparent borders and one coloured */
  .playArrow { width: 0; height: 0; border-top: 9px solid transparent;
               border-bottom: 9px solid transparent; border-left: 15px solid #fff; }
  /* an emotion-hashed wordmark: an empty link whose whole content is a background image, and
     not one word in the class for the picture vocabulary to match */
  .css-1qz4h9b { display: block; width: 150px; height: 32px;
                 background: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==") no-repeat; }
  /* the standard "make this icon white": a filter repaints the element's own background too */
  .dlGlyph { filter: brightness(0) invert(1); }
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
  /* reCAPTCHA's privacy badge: an empty div whose whole content is a logo, and nothing
     in the icon vocabulary comes near the word "logo" */
  .siteLogo { background-image: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="); width: 44px; height: 44px; }
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
  <!-- a picture drawn as an empty box: logo, badge, sprite, avatar, flag -->
  <div class="siteLogo" id="logoDiv"></div>
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
  <img id="filtIcon" class="dlGlyph" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
  <div class="toastHost" id="toastHost"></div>
  <ul><li class="tileCard" id="tileCard"
    ><a class="cardLink" id="cardLink" href="#">Bekenntnisse<card-data></card-data></a
    ><picture class="cardCover" id="cardCover"><img id="cardImg"
      src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></picture
    ><div id="cardDetails"><strong id="cardTitle">Card title</strong></div></li></ul>
  <div class="volRow hovered"><div class="volumeBar-N1rUCF" id="volTrack"
    ><div style="width:70%" class="volumeLevel-VDMLnw" id="volLevel"></div></div></div>
  <div class="timelineTrack" id="seekTrack"><div class="progress-K0IenH" id="seekPlayed"></div></div>
  <iframe class="payFrame" id="payFrame" title="3D Secure Flow Modal"
    srcdoc="&lt;html&gt;&lt;/html&gt;" allowtransparency="true"></iframe>
  <object id="objFrame" type="text/html"></object>
  <div class="playerRoot" id="playerRoot" role="button" tabindex="0"
    ><video id="playerVideo" width="320" height="180"></video
    ><button class="videoPlaceholderWithPoster" id="posterBtn"
      ><span class="playArrow" id="playArrow"></span></button></div>
  <a class="css-1qz4h9b" id="wordmark" href="#"></a>
  <button class="pl-play-control pl-control pl-button" id="plPlay"
    ><span class="pl-control-text" id="plText">Play</span></button>
  <div class="vjs-volume-level" id="plKnob"><span class="vjs-control-text"></span></div>
  <p class="pullquote" id="pullquote">a pulled quote</p>
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
{
  // The glyph a player draws on the control's OWN ::before. No name list can reach it, so the
  // sans blanket simply stops at the element; forced to Arial the PUA codepoint maps nowhere
  // and Gecko draws the .notdef hex box in place of play, mute, quality, PiP and fullscreen.
  const b = getComputedStyle(document.getElementById('plPlay'), '::before');
  t('an icon glyph drawn on the control itself keeps its font (no name says "icon")',
    b.fontFamily, /PlayerIcons/.test(b.fontFamily));
  t('the control around it still gets Arial', g('plPlay').fontFamily,
    /Arial/.test(g('plPlay').fontFamily));
  t('its text label gets Arial too', g('plText').fontFamily, /Arial/.test(g('plText').fontFamily));
  const q = getComputedStyle(document.getElementById('pullquote'), '::before');
  t('a pseudo with no font of its own still comes out Arial (by inheritance)',
    q.fontFamily, /Arial/.test(q.fontFamily));
  // The element side: no rule of ours can see that a class carries a webfont, so the one handle
  // left is the library's own name.
  t('a player element carrying an icon font keeps it', g('plKnob').fontFamily,
    /VideoJS/.test(g('plKnob').fontFamily));
  const k = getComputedStyle(document.getElementById('plKnob'), '::before');
  t('so the knob drawn in its ::before inherits that font, not Arial', k.fontFamily,
    /VideoJS/.test(k.fontFamily));
}

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

// --- the layer that blanks a page: empty, pinned, click-through ------------
t('an EMPTY pinned layer stays transparent (painted, the whole page goes black)',
  g('toastHost').backgroundColor, g('toastHost').backgroundColor === 'rgba(0, 0, 0, 0)');

// --- a value bar: empty on purpose, because its content is its geometry ----
t('the filled part of a value bar gets ink of its own (swept, it carries no reading)',
  g('volLevel').backgroundColor, g('volLevel').backgroundColor === YELLOW);
t('its track stays black, so the boundary between the two IS the number',
  g('volTrack').backgroundColor, g('volTrack').backgroundColor === BLACK);
t('and the bar can still open, `width: auto !important` having stopped short of it',
  g('volTrack').width, g('volTrack').width === '100px');
t('a seek bar is the same idiom and reads the same way',
  g('seekPlayed').backgroundColor + ' / ' + g('seekTrack').backgroundColor,
  g('seekPlayed').backgroundColor === YELLOW && g('seekTrack').backgroundColor === BLACK);
t('an empty layer that is NOT a value bar keeps the sweep, not the ink',
  g('toastHost').backgroundColor, g('toastHost').backgroundColor === 'rgba(0, 0, 0, 0)');

// --- a frame is a window onto another document, never a surface of this one ---
t('the whole-card click target is left transparent (painted it boards up the tile)',
  g('cardLink').backgroundColor, g('cardLink').backgroundColor === 'rgba(0, 0, 0, 0)');
t('a link with no picture beside it keeps its ground',
  g('link').backgroundColor, g('link').backgroundColor === BLACK);
t('a frame is never painted (a parked overlay frame would board up the whole page)',
  g('payFrame').backgroundColor, g('payFrame').backgroundColor === 'rgba(0, 0, 0, 0)');
t('but an <object> keeps image-ground grey — equal weight, so it must not be contested',
  g('objFrame').backgroundColor, g('objFrame').backgroundColor === 'rgb(128, 128, 128)');
t('and the blanket stays at (1,0,0), so an image keeps its grey rather than tying with it',
  g('img').backgroundColor, g('img').backgroundColor === 'rgb(128, 128, 128)');

// --- a player is a picture wearing a control's clothes ---------------------
t('a poster frame survives on the button that carries it',
  g('posterBtn').backgroundImage === 'none' ? 'none' : 'kept',
  g('posterBtn').backgroundImage !== 'none');
t('and neither the poster nor the player it sits in is clipped to a pill',
  g('posterBtn').borderRadius + ' / ' + g('playerRoot').borderRadius,
  g('posterBtn').borderRadius === '8px' && g('playerRoot').borderRadius === '8px');
t('a CSS triangle keeps its transparent sides (recoloured, it is a solid square)',
  g('playArrow').borderTopColor + ' / ' + g('playArrow').borderLeftColor,
  g('playArrow').borderTopColor === 'rgba(0, 0, 0, 0)'
    && g('playArrow').borderLeftColor === 'rgb(255, 255, 255)');

// --- an empty link is a picture, exactly as an empty control is ------------
t('an empty link keeps the background image that IS its wordmark',
  g('wordmark').backgroundImage === 'none' ? 'none' : 'kept',
  g('wordmark').backgroundImage !== 'none');
t('and gets the same ground, its ink being as likely to be dark',
  g('wordmark').backgroundColor, g('wordmark').backgroundColor === 'rgb(128, 128, 128)');

// --- a filter would repaint the ground along with the picture --------------
t('an image the page monochromes keeps our ground (filtered, glyph and ground merge)',
  g('filtIcon').filter + ' / ' + g('filtIcon').backgroundColor,
  g('filtIcon').filter === 'none' && g('filtIcon').backgroundColor === 'rgb(128, 128, 128)');

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
t('an empty box named as a picture keeps it (logo, badge, sprite, avatar)',
  g('logoDiv').backgroundImage === 'none' ? 'none' : 'kept',
  g('logoDiv').backgroundImage !== 'none');
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
