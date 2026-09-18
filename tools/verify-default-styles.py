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

Hover is tested too.  A headless run cannot move a mouse, so every `:hover` in the injected sheets
is rewritten to the class `.sk-hover` — a pseudo-class and a class weigh the same, (0,1,0), so the
cascade is byte-for-byte the one a real hover resolves — and the elements meant to be under the
mouse carry that class in the markup.  `:focus-visible` becomes `.sk-focus` the same way.  Nothing
else in the fixture is touched by the rewrite.
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
    % (html.escape(s["name"]), s["sections"][0]["code"].count("{"),
       s["sections"][0]["code"].replace(":hover", ".sk-hover").replace(":focus-visible", ".sk-focus"))
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
  /* ...and the same layer wearing the one attribute that used to spare it. A slide-over drawer
     keeps its scrim in the DOM shut, hidden from the accessibility tree with aria-hidden, and a
     marketplace parks fourteen of them at once. ICONS carries that attribute because a
     decorative icon does, so every one was spared and the page went black under the first. */
  .drawerScrim { position: fixed; inset: 0; z-index: 4000; pointer-events: none; }
  /* a dialog's SHELL: the role on a fixed, inset-0, click-through layer holding the shut panel
     and the tab that opens it, both fixed themselves. Its ground is the scrim, nothing at rest.
     Painted, it is the sheet above with a widget inside it, and :empty cannot see it. */
  .leadShell { position: fixed; inset: 0; z-index: 999; pointer-events: none; }
  .leadShell.is-active { background-color: rgba(0, 0, 0, .4); }
  .leadPanel { position: fixed; top: 50%; right: 24px; width: 200px; opacity: 0;
               pointer-events: none; background-color: #fff; }
  .leadTab { position: fixed; top: 50%; right: 4px; pointer-events: auto; }
  /* ...and a dialog WINDOW, a panel the page grounded white, with its own heading and close
     button, and one built of nothing but divs */
  .dialogWin, .dialogDivs { background-color: #fff !important; padding: 24px; }
  /* a product tile, and the two ways it turns black. The whole-card click target is one <a>
     laid over the tile showing nothing of its own -- and NOT :empty, because the accessible name
     is a text node with a data element beside it. The cover under it is stacked behind the page
     with z-index:-1, which works only while every ancestor is transparent. */
  .tileCard { position: relative; display: block; width: 160px; }
  .cardLink { position: absolute; top: 0; left: 0; width: 100%; height: 100%;
              font-size: 0; color: transparent; background-color: transparent; }
  .cardCover { position: relative; z-index: -1; display: block; background: #ffffff; }
  /* a daily's opener photo: the click target is one <a> laid across the picture, its own
     background a transparent 1x1 GIF, holding nothing but the gallery badge in its corner. It
     shows the photo at rest and must go on showing it with the mouse over it. */
  .openerFoto { position: relative; width: 320px; height: 180px; }
  .openerFoto .overlap { position: absolute; top: 0; left: 0; z-index: 2; width: 100%;
      height: 100%; background: url("data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7") repeat; text-decoration: none; }
  .moreGallery { position: absolute; bottom: 1rem; right: 1rem; z-index: 10; display: flex; }
  .moreGallery u { background: #122E5Be5; color: #fff; padding: .5rem; }
  /* the same tile, hovered, with a title link beside the cover; and the two shapes the card
     link deliberately leaves alone: a pill link and a wordmark, each beside a picture */
  .pillLink { background: #00cfff !important; }
  /* a discussion site's feed: the same stretched link across every post, the preview a web
     component with its picture in a shadow root, the avatar an inline <svg> -- no picture in the
     light DOM anywhere for the sibling test to find. And a crosspost card, whose own stretched
     link has nothing but <div>s beside it. */
  .feedPost, .xCard { position: relative; display: block; width: 300px; }
  x-sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  /* a carousel's nav: one absolutely-positioned strip stretched over the whole viewport of the
     carousel, click-through so the photo underneath stays reachable, holding the prev and next
     buttons and nothing else. Painted, it boards the photo up. */
  .carShell { position: relative; width: 160px; height: 90px; }
  .carNavs { position: absolute; inset: 0; z-index: 9; pointer-events: none; }
  .carNav { pointer-events: auto; }
  /* the OTHER layer over the same carousel: the one you drag. An absolutely positioned
     `overflow-x: scroll` box laid across the picture, holding one oversized empty spacer and
     nothing else, so that dragging it scrolls and the slides follow. It is chrome that is not a
     control -- nothing in it draws, and the point of the whole arrangement is that the picture
     shows through. */
  .dragLayer { position: absolute; inset: 0; z-index: 2; overflow-x: scroll; overflow-y: hidden; }
  .dragSpacer { width: 200%; height: 100%; }
  /* the same shape with something of its own to say — a row that is not only chrome — and the
     same shape with no picture beside it. Both must keep their ground. */
  .actionRow { display: flex; }
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
  /* ...and the layers a player stacks over that picture. The caption layer is pinned across the
     film and holds the cue window; the transport bar runs along the bottom and holds controls */
  .capLayer { position: absolute; inset: 0 0 1em 0; pointer-events: none; }
  .cueWindow { position: absolute; inset: 0; margin: 1.5%; }
  .cueBox { background-color: rgba(0, 0, 0, .8); color: #fff; }
  .transportBar { position: absolute; left: 0; right: 0; bottom: 0; height: 24px;
      background-color: rgba(43, 51, 63, .7); }
  /* ...and the layer a broadcaster's player lays over the whole film: inset 0, the size of the
     player, holding a top bar and a bottom bar with the actual buttons two levels down. Its own
     ground must go -- painted, the film plays behind a black rectangle -- while the bars inside
     it, which hold their controls as children, keep theirs. */
  .ovLayer { position: absolute; inset: 0; z-index: 2; }
  .ovBar { position: absolute; left: 0; right: 0; height: 20px;
      background-color: rgba(16, 22, 34, .8); }
  .ovBar.is-top { top: 0; }
  .ovBar.is-bottom { bottom: 0; }
  /* a seek bar under CSS-in-JS hashes: no name a list could match, so only role=slider says this
     box carries a number. Its parts are empty boxes whose width IS the reading and whose colour
     is the only thing that renders them -- the page already made them legible on its own track. */
  .ctpl_178sn8c1 { position: relative; width: 300px; height: 4px; }
  .ctpl_9vxwfz1 { background-color: rgba(255, 255, 255, .3); height: 4px; }
  .ctpl_1gmgbia3 { background-color: rgb(170, 170, 170); height: 4px; width: 60%; }
  .ctpl_1gmgbia2 { background-color: rgb(255, 255, 255); height: 4px; width: 40%; }
  /* ...and the SAME player with no name to go on: role=button on the box carrying the poster,
     under a CSS-in-JS hash, with the real <button> for the play arrow inside it. A control never
     nests a control, so the role is on a surface. */
  .ctpl_6uqqq21 { position: absolute; width: 320px; height: 180px;
      background: url("data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==") center/cover; }
  /* a thumbnail card: an aspect-ratio box holding an absolutely-positioned <picture>, and beside
     it a chain of boxes each holding exactly one box, reaching a badge row at the bottom edge */
  .thumbFrame { position: relative; width: 216px; height: 122px; }
  .thumbPic { position: absolute; inset: 0; }
  .thumbOver { position: absolute; inset: 0; }
  .thumbMid { position: relative; width: 200px; height: 106px; }
  .thumbRow { position: absolute; bottom: 0; height: 24px; }
  .thumbBadge { background-color: rgba(16, 22, 34, .8); color: #fff; }
  /* a page with a background film: <body> holds the <video>, so its other children are the
     page's own content and not layers over a picture */
  .bgFilm { position: fixed; inset: 0; width: 100%; height: 100%; }
  .pageBlock { background-color: #fff; }
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
  /* a sports federation's results board: the winner of each bout is an empty span in a cell
     carrying a red gradient, and the head-to-head record is a row of circles, hollow for a win
     and filled for a loss. No class on the bar at all, and the circles' classes name nothing. */
  .boutWin span { display: block; height: 26px;
      background: linear-gradient(0deg, #94080d 0%, #f00621 50%, #94080d 100%); }
  .siro, .kuro { display: block; width: 18px; height: 18px; border-radius: 9px;
      border: 1px solid #2c2c2c; margin: 0 auto; }
  .kuro { background: #2c2c2c; }
  /* ...and the empty boxes around them, white on the page, whose sweep must stay */
  .boardCell { background: #ffffff; }
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
  <!-- a results board: the marks are empty spans in cells, and their colour is the result -->
  <table class="board"><tr class="boutWin"><td id="winCell"><span id="winBar"></span></td
    ><td class="boardCell" id="lossCell"></td></tr>
    <tr><th id="recCell"><span class="siro" id="siroMark"></span></th
    ><td><span class="kuro" id="kuroMark"></span></td
    ><td><div class="boardCell" id="cellDiv"></div></td></tr></table>
  <!-- an empty span outside a cell is not a mark, and keeps the sweep -->
  <p><span class="boardCell" id="looseSpan"></span></p>
  <!-- a map's legend: each key is a blank span whose inline colour IS the content. Both parser
       shapes -- bare non-breaking spaces, and each space wrapped in a child span -- and the
       named form the same site's other legend template writes -->
  <p><span id="keyLegacy" style="border:none; background-color:#94C5DE; color:#94C5DE;">&nbsp;&nbsp;&nbsp;&nbsp;</span>&nbsp;Democratic
     <span id="keyParsoid" style="border:none; background-color:#CA0020; color:#CA0020;"><span id="keyEntity">&nbsp;</span><span>&nbsp;</span></span>&nbsp;Republican
     <span class="legend-color mw-no-invert" id="keyNamed" style="background-color:#D3D3D3; color:black; print-color-adjust: exact;">&nbsp;</span>&nbsp;No election</p>
  <!-- a colour-coded results cell, with the candidate's name a link, and a party stripe cell
       beside it that is empty by construction -->
  <table><tr><td id="cellPair" style="color:black;background-color:#B0CEFF"><a id="cellLink" href="/c">Candidate</a> 45.9%</td
    ><td id="cellPairHov" style="color:black;background-color:#FFB6B6"><a class="sk-hover" id="cellLinkHov" href="/d">Hovered</a></td
    ><td id="stripeCell" style="background-color:#0671B0; width:5px"></td></tr></table>
  <!-- ...and the three neighbours that must stay painted: a framework container written with an
       inline style object, a Google-Docs paste (`background-color:transparent` on every span, and
       the ink black), and a highlight that wrote a ground and no ink -->
  <div id="divPair" style="background-color:#ffffff; color:#333333"><p id="divPairText">a whole panel</p></div>
  <p><span id="gdocs" style="font-size:11pt;font-family:Arial;color:#000000;background-color:transparent;font-weight:400;">pasted from a document</span>
     <span id="hilite" style="background-color:#ffff00">highlighted words</span></p>
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
  <!-- the same sheet, hidden from the accessibility tree: still a sheet. And beside it the icon
       that attribute exists to protect, which says icon by NAME and keeps its ground. -->
  <div class="drawerScrim" id="drawerScrim" aria-hidden="true"></div>
  <span class="spriteIcon" id="ariaSprite" aria-hidden="true"></span>
  <!-- a dialog's shell, only boxes inside -- the panel, the tab, its own <style> -- so it is
       unpainted; a dialog window whose heading and close button say it is the window, so it
       keeps its ground; and the trade-off, a window built of divs alone -->
  <div class="leadShell" id="leadShell" role="dialog" aria-modal="true" tabindex="-1"
    ><style>.leadShell .never { color: inherit; }</style
    ><div class="leadPanel" id="leadPanel"><div><h4>An offer worth your attention</h4
      ><input placeholder="Your phone number"></div></div
    ><div class="leadTab" id="leadTab"><div id="leadTabBtn" role="button">Call me</div></div></div>
  <div class="dialogWin" id="dialogWin" role="dialog" aria-modal="true"
    ><button id="dialogClose">&times;</button><h2>Are you sure?</h2><div><p>Body</p></div></div>
  <div class="dialogDivs" id="dialogDivs" role="dialog"
    ><div class="hd">Title</div><div class="bd" id="dialogDivsBody">Body</div></div>
  <!-- the same shape declaring itself NON-modal: a floating window over a live page, a component
       library's cookie notice, and it keeps its ground -->
  <div class="dialogDivs" id="dialogNonModal" role="dialog" aria-modal="false"
    ><div class="stack"><div>Cookie preferences</div></div></div>
  <ul><li class="tileCard" id="tileCard"
    ><a class="cardLink" id="cardLink" href="#">Bekenntnisse<card-data></card-data></a
    ><picture class="cardCover" id="cardCover"><img id="cardImg"
      src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></picture
    ><div id="cardDetails"><strong id="cardTitle">Card title</strong></div></li></ul>
  <!-- the opener photo under the mouse: the sheet laid over it, and the badge it holds -->
  <figure class="openerFoto" id="openerFoto"><div id="openerWrap"
    ><img id="openerImg" src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    ><a class="overlap sk-hover" id="overlapHov" href="/foto"
      ><span class="moreGallery" id="galleryBadge"><u id="galleryWord">Fotogalerie</u><b>13</b></span
    ></a></div></figure>
  <!-- a title link beside a cover, hovered: unpainted, its ink must not go black on black -->
  <div class="tileCard" id="tileHov"><img id="tileHovImg"
      src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    ><a class="sk-hover" id="titleHov" href="/x">Title beside a picture</a></div>
  <!-- an ordinary link under the mouse, nowhere near a picture: the fill must still happen,
       on the link and on the span the site wrapped its text in. Wrapped, because at body level
       the sibling test would find the tile above it: that is the rule's stated greed. -->
  <p><a class="sk-hover" id="linkHov" href="/y"><span id="linkHovSpan">hovered link</span></a></p>
  <!-- the two shapes the card link leaves alone: a link that names itself a button keeps its
       pill in both states, and an empty wordmark keeps its grey -->
  <div class="tileCard" id="pillTile"><img id="pillImg"
      src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    ><a class="pillLink btn-buy" id="pillLink" href="/buy">Buy</a
    ><a class="pillLink btn-buy sk-hover" id="pillLinkHov" href="/buy">Buy</a
    ><a class="css-1qz4h9b" id="wordmarkBeside" href="#"></a></div>
  <!-- the feed post: nothing beside the stretched link but a span holding an <svg>, the title
       link, and a div whose picture is inside a shadow root -->
  <article class="feedPost" id="feedPost"
    ><a class="cardLink" id="postLink" href="/post"><x-sr-only>Post title</x-sr-only></a
    ><span id="creditBar"><svg width="24" height="24"><circle r="12" cx="12" cy="12"/></svg> u/author</span
    ><a id="postTitle" href="/post">Post title</a
    ><div id="postMedia"><x-embed id="embedHost"><template shadowrootmode="open"><div id="shadowPic"
      style="width:300px;height:100px;background-image:url(data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==)"></div
    ></template></x-embed></div></article>
  <!-- the crosspost card: the stretched link's neighbours are divs and nothing else -->
  <div class="xCard" id="xCard"
    ><a class="cardLink" id="xLink" href="/x"><x-sr-only>Crossposted title</x-sr-only></a
    ><div id="xCredit">r/elsewhere</div><div><p id="xText">Crossposted body</p></div></div>
  <!-- the same post under the mouse: the sheet must stay transparent and the cue is a frame -->
  <article class="feedPost" id="feedPostHov"
    ><a class="cardLink sk-hover" id="postLinkHov" href="/post"><x-sr-only>Post title</x-sr-only></a
    ><div id="postBodyHov">Post body</div></article>
  <!-- a title link beside a picture, tabbed to: `ui: links` fills on focus as it does on hover -->
  <div class="tileCard" id="tileFocus"><img id="tileFocusImg"
      src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    ><a class="sk-focus" id="titleFocus" href="/x">Title beside a picture, focused</a></div>
  <!-- a link in a sentence: inline neighbours only, so it keeps its ground and its hover fill -->
  <p id="prose">Read <a id="proseLink" href="/p">this</a>, <em>then</em> <a class="sk-hover"
    id="proseHov" href="/q">that</a><br>and <span>more</span>.</p>
  <!-- a card that wraps its whole body in one link: the heading is the label, the paragraph is
       prose the link carries. A feed's text preview is exactly this shape. -->
  <a class="tileCard" id="bodyLink" href="/post"><h3 id="bodyHead">Card title</h3
    ><div class="md"><p id="bodyPara">First lines of the <em id="bodyEm">body</em>
      <i class="fa fa-star" id="bodyIcon"></i></p><ol><li id="bodyItem">a list item</li></ol></div></a>
  <a class="tileCard sk-hover" id="bodyLinkHov" href="/post"><p id="bodyParaHov">hovered body</p></a>
  <!-- the ARIA form of the same, with a real link written inside the prose -->
  <div role="link" id="roleLink"><p id="rolePara">Read <a id="innerLink" href="/i"><span
    id="innerSpan">this</span></a> now</p></div>
  <!-- the Material UI row hovered: the ripple span is still a layer, the label still under it -->
  <a class="MuiButtonBase-root MuiListItemButton-root sk-hover" id="muiItemHov" href="#"
    ><span class="MuiListItemText-primary" id="muiLabelHov">Alza dny</span
    ><span class="MuiTouchRipple-root" id="muiRippleHov"></span></a>
  <div class="carShell" id="carShell"
    ><div class="carInner" id="carInner"><img id="carPhoto"
      src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="></div
    ><div class="carNavs" id="carNavs"
      ><div class="carNav" id="carPrev" role="button">&#8249;</div
      ><div class="carNav" id="carNext" role="button">&#8250;</div></div
    ><div class="actionRow" id="actionRow"><span id="rowLabel">Sdílet</span
      ><button id="rowBtn">Buy</button></div
    ><div class="actionRow" id="textRow">Sdílet<button id="textBtn">Buy</button></div
    ><div class="dragLayer" id="dragLayer"><div class="dragSpacer" id="dragSpacer"></div></div></div>
  <div id="loneWrap"><div class="actionRow" id="loneRow"><button id="loneBtn">Buy</button></div></div>
  <div class="volRow hovered"><div class="volumeBar-N1rUCF" id="volTrack"
    ><div style="width:70%" class="volumeLevel-VDMLnw" id="volLevel"></div></div></div>
  <div class="timelineTrack" id="seekTrack"><div class="progress-K0IenH" id="seekPlayed"></div></div>
  <div class="ctpl_178sn8c1" id="hashSlider" role="slider" aria-valuenow="40"
    ><div class="ctpl_9vxwfz1" id="hashRail"
      ><div class="ctpl_1gmgbia3" id="hashBuffered"></div
      ><div class="ctpl_1gmgbia2" id="hashPlayed"></div></div></div>
  <iframe class="payFrame" id="payFrame" title="3D Secure Flow Modal"
    srcdoc="&lt;html&gt;&lt;/html&gt;" allowtransparency="true"></iframe>
  <object id="objFrame" type="text/html"></object>
  <div class="playerRoot" id="playerRoot" role="button" tabindex="0"
    ><video id="playerVideo" width="320" height="180"></video
    ><button class="videoPlaceholderWithPoster" id="posterBtn"
      ><span class="playArrow" id="playArrow"></span></button
    ><div class="capLayer" id="capLayer"><div class="cueWindow" id="cueWindow"
      ><div class="cueBox" id="cueBox">a caption cue</div></div></div
    ><div class="transportBar" id="transportBar"><button id="tbPlay">Play</button
      ><span id="tbTime">0:00</span></div
    ><div class="ovLayer" id="ovLayer"
      ><div class="ovBar is-top" id="ovTop"><button id="ovBack">Back</button></div
      ><div class="ovBar is-bottom" id="ovBottom"><button id="ovPlay">Play</button></div></div></div>
  <div class="playerRoot" id="hashPlayer" role="button" tabindex="0"
    ><div class="ctpl_6uqqq21" id="hashPoster" role="button" tabindex="0"
      ><div id="hashInner"><button id="hashPlay"><span>Play</span></button></div></div></div>
  <!-- a thumbnail card: the picture, and the wrapper chain laid across it -->
  <div class="thumbFrame" id="thumbFrame"
    ><picture class="thumbPic" id="thumbPic"><img id="thumbImg"
        src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw="></picture
    ><div class="thumbOver" id="thumbOver"><div class="thumbMid" id="thumbMid"
      ><div class="thumbRow" id="thumbRow"><div id="thumbBadges"
        ><div class="thumbBadge" id="thumbPlay">&#9654;</div
        ><div class="thumbBadge" id="thumbLen">50 min</div></div></div></div></div></div>
  <video class="bgFilm" id="bgFilm"></video>
  <div class="pageBlock" id="pageBlock">page content over a background film</div>
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
t('...and so does one marked aria-hidden (a scrim, shut: no content AND no meaning)',
  g('drawerScrim').backgroundColor, g('drawerScrim').backgroundColor === 'rgba(0, 0, 0, 0)');
t('an empty icon marked aria-hidden still keeps its ground (the NAME is what spares it)',
  g('ariaSprite').backgroundColor + ' / ' + g('ariaSprite').backgroundImage,
  g('ariaSprite').backgroundColor === BLACK && g('ariaSprite').backgroundImage !== 'none');

// --- the seventh layer: a dialog's shell, nothing but boxes inside -----------
t('a dialog SHELL holding nothing but boxes is left transparent (painted, the page is a sheet)',
  g('leadShell').backgroundColor, g('leadShell').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the panel inside it is a box, and keeps the black ground',
  g('leadPanel').backgroundColor, g('leadPanel').backgroundColor === BLACK);
t('a dialog WINDOW with a heading and a close button of its own keeps its ground',
  g('dialogWin').backgroundColor, g('dialogWin').backgroundColor === BLACK);
t('a window built of divs alone is read as a shell: unpainted, its children black (the trade-off)',
  g('dialogDivs').backgroundColor + ' / ' + g('dialogDivsBody').backgroundColor,
  g('dialogDivs').backgroundColor === 'rgba(0, 0, 0, 0)' && g('dialogDivsBody').backgroundColor === BLACK);
t('but one declaring itself NON-modal is a window over a live page, and keeps its ground',
  g('dialogNonModal').backgroundColor, g('dialogNonModal').backgroundColor === BLACK);

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
t('a hashed seek bar keeps the colours the page gave its parts (no name to match)',
  g('hashPlayed').backgroundColor + ' / ' + g('hashBuffered').backgroundColor,
  g('hashPlayed').backgroundColor === 'rgb(255, 255, 255)'
    && g('hashBuffered').backgroundColor === 'rgb(170, 170, 170)');
t('an empty layer that is NOT a value bar keeps the sweep, not the ink',
  g('toastHost').backgroundColor, g('toastHost').backgroundColor === 'rgba(0, 0, 0, 0)');

// --- a frame is a window onto another document, never a surface of this one ---
t('the whole-card click target is left transparent (painted it boards up the tile)',
  g('cardLink').backgroundColor, g('cardLink').backgroundColor === 'rgba(0, 0, 0, 0)');

// --- ...and hovered: a hover fill is a painter, and no layer may take it -----
t('the click target over a photo stays transparent UNDER THE MOUSE (filled, the photo is a cyan sheet)',
  g('overlapHov').backgroundColor, g('overlapHov').backgroundColor === 'rgba(0, 0, 0, 0)');
t('while the badge it holds takes the fill, so the hover still shows',
  g('galleryWord').backgroundColor + ' / ' + g('galleryWord').color,
  g('galleryWord').backgroundColor === CYAN && g('galleryWord').color === BLACK);
t('a hovered title link beside a picture is unpainted AND keeps cyan ink (black would vanish)',
  g('titleHov').backgroundColor + ' / ' + g('titleHov').color,
  g('titleHov').backgroundColor === 'rgba(0, 0, 0, 0)' && g('titleHov').color === CYAN);
t('an ordinary hovered link is still filled cyan with black ink',
  g('linkHov').backgroundColor + ' / ' + g('linkHov').color,
  g('linkHov').backgroundColor === CYAN && g('linkHov').color === BLACK);
t('and so is the span the site wrapped its text in (one guard is enough for that)',
  g('linkHovSpan').backgroundColor + ' / ' + g('linkHovSpan').color,
  g('linkHovSpan').backgroundColor === CYAN && g('linkHovSpan').color === BLACK);
t('a link naming itself a button keeps its pill beside a picture (excluded by name, not weight)',
  g('pillLink').backgroundColor + ' / ' + g('pillLink').borderRadius,
  g('pillLink').backgroundColor === BLACK && g('pillLink').borderRadius === '999px');
t('and its yellow hover', g('pillLinkHov').backgroundColor + ' / ' + g('pillLinkHov').color,
  g('pillLinkHov').backgroundColor === YELLOW && g('pillLinkHov').color === BLACK);
t('an empty wordmark beside a picture keeps its grey (an empty link is a picture, not a sheet)',
  g('wordmarkBeside').backgroundColor, g('wordmarkBeside').backgroundColor === 'rgb(128, 128, 128)');
t('a ripple layer inside a HOVERED row stays transparent (filled, it hides the label)',
  g('muiRippleHov').backgroundColor, g('muiRippleHov').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and the label under it takes the fill', g('muiLabelHov').backgroundColor + ' / ' + g('muiLabelHov').color,
  g('muiLabelHov').backgroundColor === CYAN && g('muiLabelHov').color === BLACK);
t('a carousel nav strip is left transparent (painted it boards up the photo it drives)',
  g('carNavs').backgroundColor, g('carNavs').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and its buttons still carry their own ground, so the strip never takes one with it',
  g('carPrev').backgroundColor, g('carPrev').backgroundColor === BLACK);
t('a drag layer over the same photo is transparent too (its whole content is one empty box)',
  g('dragLayer').backgroundColor, g('dragLayer').backgroundColor === 'rgba(0, 0, 0, 0)');
t('a row beside a picture holding anything but controls keeps its ground',
  g('actionRow').backgroundColor, g('actionRow').backgroundColor === BLACK);
checks.push({name: 'NOTE :has(> :not(control)) sees ELEMENTS, so a bare text node does not count',
             ok: true, got: g('textRow').backgroundColor === BLACK
               ? 'text counts, row keeps its ground' : 'text ignored, row unpainted'});
t('and a strip of chrome with no picture beside it keeps its ground too',
  g('loneRow').backgroundColor, g('loneRow').backgroundColor === BLACK);
t('a link among blocks is unpainted, picture or no picture (its ancestors are black already)',
  g('link').backgroundColor, g('link').backgroundColor === 'rgba(0, 0, 0, 0)');
t('a link in a sentence keeps its ground (inline neighbours are not blocks)',
  g('proseLink').backgroundColor, g('proseLink').backgroundColor === BLACK);
t('and its hover fill', g('proseHov').backgroundColor + ' / ' + g('proseHov').color,
  g('proseHov').backgroundColor === CYAN && g('proseHov').color === BLACK);
t('a paragraph inside a link is prose: yellow, not link cyan (a feed preview is one link)',
  g('bodyPara').color, g('bodyPara').color === YELLOW);
t('and so is an emphasis inside that paragraph', g('bodyEm').color, g('bodyEm').color === YELLOW);
t('and a list item', g('bodyItem').color, g('bodyItem').color === YELLOW);
t('while the heading in the same link stays cyan: it is the label',
  g('bodyHead').color, g('bodyHead').color === CYAN);
t('an icon in that paragraph keeps its exemption (yellow either way)',
  g('bodyIcon').color, g('bodyIcon').color === YELLOW);
t('hovered, the prose still takes the fill: black on cyan',
  g('bodyParaHov').color + ' / ' + g('bodyParaHov').backgroundColor,
  g('bodyParaHov').color === BLACK && g('bodyParaHov').backgroundColor === CYAN);
t('a paragraph inside a role=link is prose too', g('rolePara').color, g('rolePara').color === YELLOW);
t('but a link written inside that prose is a link again, label and all',
  g('innerLink').color + ' / ' + g('innerSpan').color,
  g('innerLink').color === CYAN && g('innerSpan').color === CYAN);
t('a stretched link over a post whose picture is in a shadow root is left transparent',
  g('postLink').backgroundColor, g('postLink').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and the one over a crosspost card, with nothing but <div>s beside it',
  g('xLink').backgroundColor, g('xLink').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the post title link among blocks is unpainted too',
  g('postTitle').backgroundColor, g('postTitle').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the stretched link UNDER THE MOUSE stays transparent and frames the card in cyan',
  g('postLinkHov').backgroundColor + ' / ' + g('postLinkHov').outlineColor + ' '
    + g('postLinkHov').outlineWidth + ' ' + g('postLinkHov').outlineOffset,
  g('postLinkHov').backgroundColor === 'rgba(0, 0, 0, 0)' && g('postLinkHov').outlineColor === CYAN
    && g('postLinkHov').outlineWidth === '2px' && g('postLinkHov').outlineOffset === '-2px');
t('a title link beside a picture TABBED TO keeps cyan ink (the focus fill would go black on black)',
  g('titleFocus').backgroundColor + ' / ' + g('titleFocus').color,
  g('titleFocus').backgroundColor === 'rgba(0, 0, 0, 0)' && g('titleFocus').color === CYAN);
t('the box around a cover is isolated, so a z-index:-1 picture is not buried by our own ground',
  g('tileCard').isolation, g('tileCard').isolation === 'isolate');
t('and the cover still gets the image ground under it',
  g('cardCover').backgroundColor, g('cardCover').backgroundColor === 'rgb(128, 128, 128)');
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
// --- a control that HOLDS a control is a surface wearing the role ----------
t('a role=button under a hashed class keeps its poster (it holds the real button)',
  g('hashPoster').backgroundImage === 'none' ? 'none' : 'kept',
  g('hashPoster').backgroundImage !== 'none');
t('...and is not clipped to a pill either',
  g('hashPoster').borderRadius, g('hashPoster').borderRadius === '0px');
t('the real button inside it is still a control: pill, black ground, yellow trace',
  g('hashPlay').borderRadius + ' / ' + g('hashPlay').backgroundColor + ' / ' + g('hashPlay').color,
  g('hashPlay').borderRadius === '999px' && g('hashPlay').backgroundColor === BLACK
    && g('hashPlay').color === YELLOW);
t('and an ordinary labelled button, holding no control, keeps the pill',
  g('cta').borderRadius, g('cta').borderRadius === '999px');
// --- the ninth layer: the wrapper chain over a thumbnail -------------------
t('the wrapper laid across a thumbnail is transparent (painted, the picture is gone)',
  g('thumbOver').backgroundColor, g('thumbOver').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and so is every box in the chain below it',
  g('thumbMid').backgroundColor + ' / ' + g('thumbRow').backgroundColor,
  g('thumbMid').backgroundColor === 'rgba(0, 0, 0, 0)'
    && g('thumbRow').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the badge row holds TWO badges, so it keeps its ground and they stay legible',
  g('thumbBadges').backgroundColor, g('thumbBadges').backgroundColor === BLACK);
t('the picture underneath keeps the image ground',
  g('thumbImg').backgroundColor, g('thumbImg').backgroundColor === 'rgb(128, 128, 128)');
// --- a layer inside a player is a window onto the picture ------------------
t('a caption layer inside a player keeps no ground of its own, cue text and all',
  g('capLayer').backgroundColor, g('capLayer').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and the cue box inside it keeps one, so a subtitle sits on black and not on the film',
  g('cueBox').backgroundColor, g('cueBox').backgroundColor === BLACK);
t('a layer over the whole film is unpainted even though controls sit deep inside it',
  g('ovLayer').backgroundColor, g('ovLayer').backgroundColor === 'rgba(0, 0, 0, 0)');
t('...while the bars within it, holding their buttons as CHILDREN, keep their grounds',
  g('ovTop').backgroundColor + ' / ' + g('ovBottom').backgroundColor,
  g('ovTop').backgroundColor === BLACK && g('ovBottom').backgroundColor === BLACK);
t('the transport bar holds a control, so it is chrome and keeps its ground',
  g('transportBar').backgroundColor, g('transportBar').backgroundColor === BLACK);
t('<body> is not a player: a page with a background film still paints its own content',
  g('pageBlock').backgroundColor, g('pageBlock').backgroundColor === BLACK);

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

// --- colour samples --------------------------------------------------------
// A legend key is a blank span whose inline colour is the content, and nothing of ours may match
// it -- no `!important` of ours can defer to the page's normal inline value, so the painters
// stop at it with a `:where()` that costs no specificity.
t('a legend key keeps its inline colour (bare non-breaking spaces)',
  g('keyLegacy').backgroundColor, g('keyLegacy').backgroundColor === 'rgb(148, 197, 222)');
t('...and when the parser wraps each space in a child span', g('keyParsoid').backgroundColor,
  g('keyParsoid').backgroundColor === 'rgb(202, 0, 32)');
t('the child spans inside it are not painted either (they cover the swatch)',
  g('keyEntity').backgroundColor, g('keyEntity').backgroundColor === 'rgba(0, 0, 0, 0)');
t('the named form keeps its colour too', g('keyNamed').backgroundColor,
  g('keyNamed').backgroundColor === 'rgb(211, 211, 211)');
t('a colour-coded cell keeps the pair the page made legible',
  g('cellPair').backgroundColor + ' / ' + g('cellPair').color,
  g('cellPair').backgroundColor === 'rgb(176, 206, 255)' && g('cellPair').color === BLACK);
t('a link in it shows the colour the page gave links, not cyan on pale',
  g('cellLink').color + ' / ' + g('cellLink').backgroundColor,
  g('cellLink').color === 'rgb(0, 102, 204)' && g('cellLink').backgroundColor === 'rgba(0, 0, 0, 0)');
t('...and hovered it takes no fill (a hover fill paints too)',
  g('cellLinkHov').backgroundColor + ' / ' + g('cellLinkHov').color,
  g('cellLinkHov').backgroundColor === 'rgba(0, 0, 0, 0)' && g('cellLinkHov').color === 'rgb(0, 102, 204)');
t('an empty stripe cell keeps its ground (no ink to worry about)',
  g('stripeCell').backgroundColor, g('stripeCell').backgroundColor === 'rgb(6, 113, 176)');
t('a <div> with an inline pair is still painted (a framework container is not a sample)',
  g('divPair').backgroundColor + ' / ' + g('divPairText').color,
  g('divPair').backgroundColor === BLACK && g('divPairText').color === YELLOW);
t('a Google-Docs paste (transparent ground, black ink) is still painted, ink yellow',
  g('gdocs').backgroundColor + ' / ' + g('gdocs').color,
  g('gdocs').backgroundColor === BLACK && g('gdocs').color === YELLOW);
t('a ground with text and no inline ink is still painted',
  g('hilite').backgroundColor + ' / ' + g('hilite').color,
  g('hilite').backgroundColor === BLACK && g('hilite').color === YELLOW);

// --- marks: an empty span in a table cell, whose colour IS the result ------
t('a win bar (an empty span in a cell carrying a red gradient) keeps its picture',
  g('winBar').backgroundImage === 'none' ? 'none' : 'kept', g('winBar').backgroundImage !== 'none');
t('and is not painted under it either', g('winBar').backgroundColor,
  g('winBar').backgroundColor === 'rgba(0, 0, 0, 0)');
t('a filled circle keeps its fill', g('kuroMark').backgroundColor,
  g('kuroMark').backgroundColor === 'rgb(44, 44, 44)');
t('a hollow one stays hollow', g('siroMark').backgroundColor,
  g('siroMark').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and the ring around both is yellow (a border is chrome, and chrome is recoloured)',
  g('siroMark').borderTopColor + ' / ' + g('kuroMark').borderTopColor,
  g('siroMark').borderTopColor === YELLOW && g('kuroMark').borderTopColor === YELLOW);
t('an empty CELL beside them keeps the sweep (its white would be a hole in the row)',
  g('lossCell').backgroundColor, g('lossCell').backgroundColor === 'rgba(0, 0, 0, 0)');
t('so does an empty div in a cell (a mark is a span)',
  g('cellDiv').backgroundColor, g('cellDiv').backgroundColor === 'rgba(0, 0, 0, 0)');
t('and an empty span outside a cell',
  g('looseSpan').backgroundColor, g('looseSpan').backgroundColor === 'rgba(0, 0, 0, 0)');

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
