# Changelog

This file carries **both histories**: 白い熊 Stylus' releases and, folded into each one, the notes
for the upstream [Stylus](https://github.com/openstyles/stylus) release it is built on. Upstream
ships no changelog file of its own — its notes live only on GitHub Releases — so this file is
entirely ours to maintain, newest first.

## 白い熊 Stylus 2.4.10.69 — 2026-09-24

Built on upstream 2.4.10. One report — a page of a scanned book rendered as a black rectangle with
yellow text on it — and **one repair**, which turns out to reach every viewer of scanned pages on
the web. The behavioural fixture grew from 165 checks to 176. Note the version jump: 2.4.10.68 was
an unsigned iteration build.

The text on the black rectangle was not the book. It was the OCR reading of it, which is how the
diagnosis started: a title page from 1852 was announcing itself as *MAY 2f 1987NOVOČESKÁ*.

### A transcription is the picture's own words, and it is invisible on purpose

Every viewer of scanned pages lays a transcription over the picture. BookReader writes
`<div class="BRPageLayer BRtextLayer">` across each `<img class="BRpageimage">` — sized to the scan,
2700×4696, and scaled down onto it, one absolutely-positioned `<p>` per OCR paragraph, each word a
`<span>` stretched by an inline `letter-spacing` to the width of the scanned word beneath it, and
`color: transparent` throughout — and PDF.js lays `.textLayer` over its `<canvas>` exactly the same
way. The layer exists so that a picture's words can be selected, searched and read aloud; it is
invisible because the picture underneath is already showing them.

Painted, it is an opaque sheet at precisely the size of the page, and the ink painters then make the
OCR the only thing left to read: `bg div` blackens the layer, `bg text` the paragraphs, `bg all`
every word span, and `fg all` turns the transparent words yellow. The scan itself was never touched
— it sat intact behind the sheet the whole time.

Nothing structural could see it, and each near miss is instructive. It is not `:empty`: it holds the
paragraphs. The wrapper-chain rule wants a box whose whole content is **one** box, and this one holds
ten. The player rules want a `<video>`. And a badge row over a thumbnail has exactly this shape — a
box of text over a picture — and has to keep its ground, so no test on *holds content, lies over a
picture* can ever separate them. The one thing that does is that the page made this one's ink
transparent, and CSS cannot ask what colour an element already has, any more than it can ask about
the `pointer-events: none` this layer also carries.

So it is **named**, on the terms the icon and artwork lists are named: the word names an idiom and
the two libraries most of the web embeds for paged documents, never a site. And it is spared
**whole** — ground, ink and metrics — because every one of those is measured against the picture.

The metrics are the partial half, and the limit is worth stating. The exclusion keeps what the page
*declares* on the layer: BookReader's per-line `line-height: 112px`, PDF.js's per-span
`font-family`, and the `start` alignment that is the right edge of an RTL book. What it cannot keep
is an **inherited** face — `font-family` comes down from `<body>`, which the sans blanket has
already set to Arial, and no value means "the font this page wanted". So a viewer that declares no
face of its own still narrows by about a tenth (one title word measured 388px against the scan and
349px after), and a selection highlight sits slightly narrow on the words it covers. The words
themselves stay right, and invisible, which is what the ground and ink halves are for.

Zero-weight `:where()` throughout, so the ink guard, the ground guard and all three typography
blankets each gain it without a single rule moving on the specificity ladder.

### Verification

Twelve new assertions in the fixture and a note recording the inherited face, 176 in all, passing in
both engines. A pixel A/B of the shipped library against this one, old and new in the same page
load: zero changed pixels on three healthy pages, and the scan back on the fourth. Then the real
extension, loaded into 白い熊 火狐 156 — the layer, its paragraphs and every one of its words
transparent, and the line height back to the page's own.

One thing learned that is not a rule change: a page whose own Content-Security-Policy carries
`style-src 'self'` cannot be paint-tested at all. The injected sheet's `.sheet` is `null`, the A/B
reports no change, and it proves nothing — the standalone PDF.js viewer is exactly that page.

## 白い熊 Stylus 2.4.10.67 — 2026-09-18

Built on upstream 2.4.10. Two reports — a marketplace's offer page and a broadcaster's episode page
— and **five repairs** to the library, all structural, no site named in a rule. The behavioural
fixture grew from 154 checks to 165. Note the version jump: 2.4.10.64 to .66 were unsigned
iteration builds.

One of them was found only after 白い熊 pointed out that the testing was being done in the wrong
browser. The library had been measured in stock Firefox with the CSS hand-injected; the bug lives in
白い熊 火狐 with the extension actually loaded, and — worse — only while the pointer is over the
film. Every headless screenshot had shown a healthy player.

### A control that HOLDS a control is a surface wearing the role

A player hangs `role="button"` on the 1400×788 box carrying the episode's poster as its **background
image**, with the real `<button>` for the play arrow two levels inside it. `ui: controls` read the
outer box as a button: it stripped the poster as a gloss gradient — the one case the name list
exists to prevent — and `border-radius: 999px` clipped the player into a **giant ellipse**.

Neither existing escape could save it. The class is `ctpl_6uqqq21`, a CSS-in-JS hash, so the picture
names matched nothing; and the media-child test asks for a **direct** `<img>`/`<video>` child, where
this box holds four `<div>`s and, before you press play, no video at all.

The structure is exact: **a control never nests a control** — the platform forbids interactive
content inside a button, and ARIA has no use for it — so a role that wraps one is on a *surface*, and
the thing inside is the control. Element selectors only (`button, select, textarea`), which is
load-bearing twice: at (0,0,1) it leaves the weight of every line it joins where it was, and a real
`<button>` inside proves the outer box is not one, where a second `[role="button"]` might only mean a
page that hangs the role on everything. `<input>` is deliberately absent, and a pixel A/B is what
caught that: `input[type="hidden"]` is not a control but a data carrier with no box, and a Q&A site
puts one inside every *Follow* button on the page — with `input` in the list, all of them stopped
being buttons and lost their pill.

### A wrapper chain over a thumbnail

Forty episode thumbnails, every one a black rectangle with a play arrow on it. The card lays its
chrome across the picture the way a player does: an aspect-ratio box holding an absolutely
positioned `<picture>` and, beside it, four nested `<div>`s of which **the outer three each hold
exactly one box**, the innermost reaching the play badge and the duration pill.

Nothing could reach them — not the `:empty` sweep, since each box holds the next; not the drag
layer's test, whose child must be *empty*; not the carousel nav strip, which reads direct children
and finds a `<div>` four levels above the chrome; not the player rule, scoped to a box holding a
`<video>`. The premise is the family's own, one step further: **a box whose whole content is a single
box has nothing of its own to make legible**, the emptiness having moved down a level rather than
away. Scoped to **inside a picture's frame**, where such a box can only ever be a layer.

Two guards, both found by the fixture on the first run. The empty term is `SHELL_KINDS` rather than
`*`, because **any leaf element is `:empty`** — an `<svg>` holding one `<path>` matched and lost the
ground asserted for it. And a value bar is excluded, because an empty box that is a value bar is not
nothing at all: it is the reading. A box holding **two** children is left alone, which is what spares
the badge row — so a restored thumbnail wears a black strip along its bottom fifth, with the play
arrow and the duration legible on it.

### A box holding a control deep below it is still a layer

The playing page, and a correction to the player rule's own exclusion. That rule spares a box which
holds a control anywhere inside, on the argument that such a box is chrome — a transport bar — and
keeps its ground. This player puts one `<div>` at `position: absolute; inset: 0; z-index: 2` across
the **entire** film, holding four boxes with the actual `<button>`s three and four levels down. The
descendant test read the whole sheet as chrome, and the film played behind an opaque black rectangle.

So the test is **direct-child scoped**: a box that *directly* holds a control is the bar the control
sits on and keeps its ground, where a box that merely contains one somewhere below is a layer that
happens to have chrome inside it — and the bars within it keep their own grounds by the very same
test, one level down.

### ...and a layer inside that layer is still a layer

The one that survived three rounds, because **it only exists while the pointer is over the film**.
The transport bar is mounted on hover as a *grandchild* of the player — the control layer holds it,
and it is itself absolutely positioned at the full size of the player, 1025×577 against a player of
1025×577. At rest the film plays; the moment the pointer crosses it the picture goes **97 % `#000`**.

Depth alone is not the answer: widening to a plain descendant combinator takes the **cue box** with
it, and a subtitle then sits on the film instead of on black. What separates them is what they hold —
**a box whose element children are all boxes** is holding structure, not content, and inside a player
structure is stacked over the film by construction. The cue box holds a text node and no element, so
it keeps its ground; a bar holding its `<button>`s directly keeps its ground too, a button not being
a box; a badge holding an `<img>` keeps the grey behind the picture. Scoped to a player, and
deliberately **not** widened to pictures, which is what keeps the thumbnail badge row painted.

### A slider's parts are a reading, like a colour sample

The progress line: a black strip with nothing in it. The played length, the buffered length and the
chapter ticks are **empty boxes whose width is the number and whose colour is the only thing that
renders them** — the value-bar idiom, but under CSS-in-JS hashes, so the name list has nothing to
match. Ink cannot be the answer: the structure cannot tell played from buffered from a chapter list,
and yellow on all three reads as 100 % played. So it is the **colour sample's** answer — do not match
them, and let the page's own colours stand, since the page already made them legible against its own
track. `[role="slider"]`/`[role="progressbar"]` is the handle, and it is the markup's own word for
*this box carries a number*; ground painters and both `:empty` sweeps only, an empty box having no
ink.

### Verification

**ALL 165 PASSED** in Gecko, eleven assertions new. Measured on the live pages in 白い熊 火狐 with the
extension loaded: hovered, the film goes from 97.4 % black to 21.5 %, and the played bar returns to
the broadcaster's red `#ED1C24` on the rail's black; the offer page's main photo, thumbnail row and
both recommendation carousels render. Pixel A/B of the shipped library against this one: **zero
changed pixels** on Wikipedia, GitHub, alza.cz, Hacker News, BBC News and Stack Overflow.

## 白い熊 Stylus 2.4.10.63 — 2026-09-17

Built on upstream 2.4.10. A marketplace's offer page rendered **98 % `#000`**, and two separate
sheets were doing it. Two repairs to the library, both structural, no site named in a rule. The
behavioural fixture grew from 151 checks to 154. Note the version jump: 2.4.10.62 was the unsigned
iteration build.

The page also needed a new way to be looked at. Its bot wall serves headless Chromium *and*
headless Firefox an empty interstitial — a 1.6 KB document with no challenge to solve — so neither
engine could see the bug at all. A **windowed** Firefox on a virtual display loads it for real, and
that is how both sheets were measured.

### An empty box marked `aria-hidden` is a layer twice over, not an icon

The worst failure this library can produce, met again through the one exclusion nobody had argued
for. `ICONS` carries `[aria-hidden="true"]` because a decorative icon does, and the `:empty` sweep
in `ui: overlays` — the sweep that exists precisely to neutralise an empty layer left pinned over
the viewport — inherited the whole list.

But that attribute is a statement about the **accessibility tree**, never about painting. Every
other term in `ICONS` names an icon system (`fa-`, `octicon`, `[class*="icon"]`) or an icon element
(`i`, `svg`, `use`), and `[role="img"]` says outright that the box is a picture. `aria-hidden` says
only *ignore me* — and a scrim says it too. The site parks one per slide-over drawer, shut:
`<div aria-hidden="true"></div>`, `position: fixed`, `inset: 0`, `z-index: 4000`,
`pointer-events: none`, **fourteen of them in the DOM at once**. Every one was spared, and `bg all`,
`bg div` or `bg blocks` — any of the three **alone** — made the first an opaque sheet at the top of
the stack. `pointer-events: none` keeps such a layer out of every hit test, so only a paint diff
finds it.

Put beside `:empty` the attribute reverses: no content **and** no meaning is the strongest statement
a page can make that an element is a layer rather than a surface. Measured across four real pages
the term spared nothing else that draws — a 1px decorative rule, and boxes with no box at all — and
what it costs is bounded by the page's own declaration, since whatever an `aria-hidden` element was
drawing, the page has already said a reader loses nothing by not perceiving it.

Out of **this** sweep only. In `ui: strip-backdrops` the same word stays, because there the sweep
takes a background *image*, and an erased picture is content simply gone. Specificity is unchanged
either way — `[class*="icon" i]` keeps the list at (0,1,0) — so no rule moves on the ladder.

### Chrome is not only controls — it is also nothing, one level down

With the scrims gone the page came back, all but the **main product photo**, which was still one
black rectangle. A second layer, and the nav strip's sibling.

A carousel that can be **dragged** lays another layer over the very same viewport:
`position: absolute; inset: 0; overflow-x: scroll`, holding one oversized **empty** box and nothing
else, so that dragging it scrolls and the slides follow. It draws nothing by construction — the
layer is transparent, the spacer inside it is transparent, and the whole point of the arrangement is
that the picture shows through. Neither test could reach it: not the `:empty` sweep, because the
layer is not empty, it holds the spacer; and not the carousel nav strip, because a spacer is not a
control.

So the strip's content test becomes **controls, or boxes with nothing in them**. A box whose whole
content is chrome, or is nothing, has no ground of its own to defend, and beside a picture that
ground can only ever be a sheet over it — the emptiness has simply moved one level down, and the
premise the `:empty` sweep rests on moves with it.

Two things keep it honest, and the fixture found both on the first run. The empty term is
`SHELL_KINDS` (`div`, `section`, …) rather than `*`, because **any leaf element is `:empty`**: an
`<svg>` holding one `<path>` matched `*:empty` and lost the ground asserted for it. And it carries
`NOT_VALUE_BAR`, because an empty box that is a value bar is not nothing at all — it is the reading,
the one documented exception to the whole `:empty` premise, and a seek bar's track holds one empty
`progress-…` div and went transparent. The weight is unchanged: `:empty` and `[class*="volume" i]`
are both (0,1,0), exactly what `[role="button"]` already contributed. And an `<img>` is `:empty` by
definition, so it is `NO_OWN_MEDIA` — already there for the nav strip — that keeps a box holding a
picture out of this, load-bearing twice over now.

### Verification

Three new assertions in the fixture — the `aria-hidden` scrim, the icon beside it that keeps its
ground because its **name** says icon, and the drag layer over a photo. **ALL 154 PASSED** in Gecko.
Pixel A/B of the shipped library against this one, injected into the same loaded page: **zero
changed pixels** on Wikipedia, GitHub, alza.cz, Hacker News, BBC News and Stack Overflow. On the
reported page the main photo, the thumbnail row, both recommendation carousels, the price column and
the parameter table all render.

## 白い熊 Stylus 2.4.10.61 — 2026-09-17

Built on upstream 2.4.10. A streaming site's live player rendered as one black rectangle with the
page around it untouched. One repair to the library, structural, no site named in a rule. The
behavioural fixture grew from 147 checks to 151. Note the version jump: 2.4.10.60 was the unsigned
iteration build.

### A layer inside a player is unpainted: it is a window onto the picture

The sheet was Video.js' **caption layer** — a `<div class="vjs-text-track-display">` at
`position: absolute; left/right/top: 0; bottom: 1em; pointer-events: none`, measured 890×2109
against a player of 890×2116, holding the cue window and nothing else. `bg all` paints it at
(1,0,0) and `bg div` at (1,0,1); either style **alone** boards the film up.

Every handle `ui: overlays` had walks straight past it. Not `:empty`, since it holds the cue window
— and it has to go on holding cue boxes with text in them whenever captions are switched on, so
**no** test on its content could ever hold. Not a name: `vjs-text-track-display` carries no word the
overlay list matches, and the library prefix is no use either, `vjs-` being on the transport bar
too, which needs its ground. Not the control strip, which asks for a box whose children are
controls, where this one holds none at all. And `pointer-events: none` keeps it out of every hit
test, so only a paint diff finds it — the notification host and the carousel nav strip again.

The structure carries it instead, one step up from the element: a box that **directly** holds a
`<video>` is a player, the video is laid across the whole of that box, and every other child is
therefore stacked over the picture by construction. So inside a player, a child that is neither the
media, nor a control, nor a box holding one is a layer — whatever it is named and whatever is
inside it. Unpainted at (2,2,4): above the bg blankets, and above `ui: image-ground`'s grey at
(1,0,1), which inside a player is right, a watermark laid over the film being meant to be over the
film.

Two things it deliberately does not reach. `<body>` is not a player: a `<video>` that is a child of
the page is a background film, and there the siblings are the page's own content, so unpainting
them would show the film through every word. And the wrapped player, whose `<video>` sits in a
wrapper of its own and whose caption layer is then a nephew rather than a sibling — `:has(video)`
would reach it and reach every ancestor up to the root along with it, while the sibling arms of
`beside_media` would reach half the boxes of every card on the page. Direct children are what the
met case needs and all that can be argued for; a second case can widen it.

What it costs, asserted by name in the fixture: a box inside a player that holds no control loses a
ground of its own, so an error panel shows its words over the film rather than on black.

Four new assertions in the fixture: the caption layer, the cue box inside it, the transport bar
beside it, and a page with a background film. ALL 151 PASSED in both engines. On the reported page
the shipped library measures the caption layer at `rgba(0, 0, 0, 0)`, with the transport bar still
black and the big play button still on its `#808080`; across three saved pages carrying eight
players between them the rule reaches those five Video.js layers, one 16×16 link laid over a
lecture player, and nothing else.

## 白い熊 Stylus 2.4.10.59 — 2026-09-15

Built on upstream 2.4.10. An operator's homepage rendered as one black sheet — header, hero, tiles,
all of it — with only a "call me back" tab showing at the right edge. One repair to the library,
structural, no site named in a rule. The behavioural fixture grew from 142 checks to 147. Note the
version jump: 2.4.10.58 was the unsigned iteration build.

### A dialog's shell is unpainted: its ground is its scrim

The sheet was that widget's **shell** — a `<div role="dialog" aria-modal="true">` at
`position: fixed; inset: 0; z-index: 999; pointer-events: none`, sitting in the DOM on every page
from load, shut. Its ground is the scrim: nothing while the dialog is shut, a 40 % black once it
opens. Its three children — a `<style>`, the hidden panel and the tab — are all `fixed` themselves,
so the shell's own box holds nothing in flow, and `bg all` painted it at (1,0,0). It is the
empty‑pinned‑layer failure one element type further, and every handle `ui: overlays` had missed it
again: not `:empty`, since it holds the panel and the tab; named nothing safe to match (`floating`
also names sticky headers); and click‑through, so no hit test sees it. The paint diff found it.

The role is the handle and the **children** tell shell from window. A shell holds nothing but boxes
— the panel, a launcher, its own `<style>` — where a window holds a heading, a close button, a
paragraph, a picture, a field. So a `[role=dialog]` or `[role=alertdialog]` whose element children
are all containers (`div`, `section`, `article`, `aside`, `form`, `style`, `script`, `template`) is
left transparent at (1,2,1), above `bg all` and `bg div`; nothing of ours paints a dialog on purpose,
so nothing ties. One thing more the markup says: a scrim host is modal by construction, so a dialog
declaring `aria-modal="false"` is a window over a live page and keeps its ground — a component
library's cookie notice is exactly that, one `Paper[role=dialog]` holding a stack of boxes, and it
was the only thing on six pages the first draft touched, the page showing through its padding.

What it costs, asserted by name in the fixture: a modal window built of nothing but `<div>`s loses
the ground under its padding. Its children are boxes too and take the same blankets, so its words
still sit on black.

Five new assertions in the fixture: a shell holding only boxes, the panel inside it, a window with a
heading and a close button, a window of divs alone, and a non‑modal one. ALL 147 PASSED in both
engines. A pixel A/B of the old library against the new at rest on six unrelated pages — two shops,
two dailies, and the modal docs of two component libraries — changed nothing anywhere but the
reported site, where the sheet is gone and the built extension measures the shell at
`rgba(0, 0, 0, 0)`.

## 白い熊 Stylus 2.4.10.57 — 2026-09-15

Built on upstream 2.4.10. A discussion site's feed came back with the title and the first lines of
text of most posts hidden under a black rectangle, and every crosspost card blank; with those
visible again, the text in them was link‑cyan where a reader expects prose. Two repairs to the
library, both structural, no site named in a rule. The behavioural fixture grew from 127 checks to
142. Note the version jump: 2.4.10.55 and 2.4.10.56 were the unsigned iteration builds.

### A card's click target is unpainted among blocks, not only beside a picture

The sheet was the whole‑card click target — one `<a class="absolute inset-0">` laid across each
post — and the repair for exactly that shape could not see it. It asked for a **picture beside the
link**, and the feed's previews are web components whose thumbnail is a background inside the
embed's shadow root, out of reach of `:has()`. Whether the sheet was painted then turned on the
**author**: a default avatar is an `<img>` in the credit bar and the sibling test found it; a
custom one is an inline `<svg>` and the test found nothing. Eleven of the thirty posts on the page
were boarded up, and a crosspost card's own stretched link has nothing but `<div>`s beside it, so
those went on every load.

The test widens from "beside a picture" to **"beside a picture, or among blocks"**. A link in a
sentence has inline neighbours — a span, an emphasis, another link, a line break — and never a
block, because a paragraph cannot hold one; a link with a `div`, a `p` or a heading beside it is
laid among the boxes of a card or of the page's chrome, and there its ground is never its own to
keep: transparent, it shows the ancestor's, which got the same treatment it did. A pixel A/B of the
old library against the new at rest, on six unrelated pages, changed nothing anywhere but the feed.

What it costs is the cyan hover **fill** on links that sit among blocks — a footer column's links,
a header's sign‑up link beside the nav — so the cue moves: the hovered twin now draws a 2 px cyan
frame inside the link's box, around the words of a text link and around the whole card on a
stretched one, whose own text is hidden and never showed the fill anyway. It covers `:focus-visible`
too, since `ui: links` fills on focus as on hover and a tabbed‑to title link beside a picture had
been going black on black.

### A link's label is never a paragraph

The feed wraps each post's text preview — the first lines of the body, `<p>`s in a `div.md` — in
one link to the post, and `ui: links` colours every descendant of a link cyan, because modern sites
wrap link text in a span. So every preview was a wall of link colour; it had been so all along, the
sheet had merely been hiding it. Prose elements inside a link — `p`, `li`, `dd`, `dt`,
`blockquote`, `pre`, `figcaption` — are prose the link *carries*, and take the yellow back; a
heading in the same link stays cyan, being the label; a link written inside that prose is a link
again. The rule is weighed to sit exactly between the two forms it must respect — above the
descendant form, so the tie goes to prose, and below the hover form, so a hovered preview still
inverts to black on cyan.

Fifteen new assertions in the fixture: a feed post with its picture in a declarative shadow root and
an `<svg>` avatar, a crosspost card, the hovered sheet and its frame, a focused title link, a link
in a sentence keeping its ground and its fill, and a card link whose paragraph, emphasis and list
item are yellow while its heading stays cyan. ALL 142 PASSED in both engines; the built extension on
the live feed in Gecko measured 0 of 30 stretched links black, all 85 preview paragraphs
`rgb(255,255,0)`, all 28 titles cyan, in the card view, the compact view and at phone width.

## 白い熊 Stylus 2.4.10.54 — 2026-09-13

Built on upstream 2.4.10. A sports federation's site — the one that carries the results of every
tournament — came out black on black on every page: profile cards, the bout results, the schedule.
The cause was not a rule but a **seed**, and the repair is mostly to the sync that had made the seed
permanent. The behavioural fixture grew from 119 checks to 127. Note the version jump: 2.4.10.53
was the unsigned iteration build.

### Take back an ink-only exclusion

The first library carried the old Stylish export's per-site tuning as its seed, and one entry was an
exclusion of the five `fg` styles alone from that site — with the `bg` blankets left on. Every card
there was painted black at (1,0,0) and the site's own `#2c2c2c` ink stayed put. An ink exclusion
without its ground exclusion is never what a reader wants, and the glob is withdrawn from those five
styles and from `ui: design tokens`, whose own rule is to follow the blankets.

Withdrawing it in the generator alone would have changed nothing on any existing profile, and that
is the finding. The sync kept a profile's `exclusions` and `inclusions` **wholesale** whenever it had
any, on the reasoning that they are 白い熊's tuning — which they are, except for the ones the build
put there itself, and nothing told the two apart. So the sync now **stamps what it seeded**
(`_forkSeed`) and merges each list three ways against that stamp: a glob the profile has is kept if
this build still ships it or no build ever did; one the previous build shipped and this one does
not is withdrawn; one this build ships for the first time arrives, unless it was seeded before and
removed by hand. A profile older than the stamp has no seed to compare against, so the generator
carries `withdrawn` per style — what earlier builds shipped and this one does not — read for that
bootstrap only and never stored.

Verified in a stock Firefox rather than in a unit test alone: a profile seeded by the signed
2.4.10.52, hand tuning added the way the popup would add it, then this build loaded over it. The
site glob was gone from all six styles, the hand-added glob was kept beside the seed, a seed removed
by hand stayed removed, and every style carried its stamp.

### A mark is an empty span in a table cell, and its colour is the result

With the ink back the results board was still unreadable. The winner of each bout is
`<td><span></span></td>` carrying a red gradient, and the head-to-head record is a row of
`span.siro` / `span.kuro` circles, hollow for a win and filled for a loss — empty spans in table
cells whose whole content is their colour, the colour sample's cousin with no inline style to give
it away. `bg text` painted them, `ui: strip-backdrops` took the gradient and `ui: overlays` the
fill, and the board showed every name and no result.

Nothing could see them: no class on the bar at all, `siro`/`kuro` name nothing a list would carry,
no inline style for `SAMPLE`, and no ink. The structure is the handle. A span is inline, so an empty
one has no size unless the page gave it some, and a page sizes an empty span in a cell to draw
something. It cannot be a sheet — a sheet is a block pinned over the viewport — and it is not a
cell: `<td></td>` keeps the sweep, or its empty white would be a hole in the row. So `MARK` joins
`SAMPLE` in the `:where()` on the **ground** painters and both `:empty` sweeps, at no cost to the
specificity ladder; the ink painters are left alone, since a glyph drawn in the span's `::before`
must still come out yellow.

The limit is a fill the site chose dark for a white page: `kuro` is `#2c2c2c`, 1.3:1 against black,
and no rule can know a fill is dark without knowing it is a fill. That one is named on the site, in
a one-line `site: sumo.or.jp` — the one place that knows — so a loss now reads as a filled yellow
disc and a win as a hollow ring.

Eight new assertions in the fixture: the bar keeps its picture and takes no ground, the filled
circle keeps its fill, the hollow one stays hollow, the ring is yellow on both, and the three
neighbours — an empty cell, an empty `div` in a cell, an empty span outside one — keep the sweep.
ALL 127 PASSED in both engines, and the real extension on the real site in Gecko measured the bar's
gradient intact, text `rgb(255,255,0)` on `rgb(0,0,0)`, the loss mark yellow, the win mark hollow.

Two things on that site are left as they are, for want of a handle: the ticket pages' banner
picture, whose text wrapper is a transparent `div` laid over a `background-image` on its parent,
and the side buttons' background icons, which sit on links that name themselves buttons and so take
the pill and lose the picture — the label survives.

## 白い熊 Stylus 2.4.10.52 — 2026-09-12

Built on upstream 2.4.10. An encyclopaedia's election article shows three maps, each with a key
beneath it, and every key came out black: five swatches with their labels beside them and no
colour in any of them, so the maps could not be read against their legend. The repair is the
smallest mechanism the library has yet had to reach for — nothing is painted or recoloured; the
painters are taught what not to touch — and it rests on a fact about the cascade that had not been
established before. The behavioural fixture grew from 108 checks to 119.

### Leave a colour sample alone: its colour is its content

Each key is a blank `<span style="background-color:#94C5DE; color:#94C5DE">` holding four
non-breaking spaces. `bg all` at (1,0,0) and `bg text` at (1,0,1) both beat that inline
declaration, which is not `!important`, and nothing in the library could see the element: no class,
so no name list — the same site's other legend templates say `legend-color`, this one says nothing
— and not `:empty`, since the spaces are text nodes and one of the site's two parsers wraps each in
a child span besides.

The finding underneath is that **no repair of ours can hand an inline value back once a rule has
matched**. Nothing declared `!important` can defer to a page's *normal* declaration: `revert-layer`
was measured in both engines and rolls back to the UA origin, past the style attribute, never into
it. So the only mechanism is for the painters not to match, and `:where()` is what makes that
affordable — it contributes zero specificity, so the blanket stays at (1,0,0) and the ladder above
it is untouched. A `:not()` in the blanket itself would lift it to (1,1,0) and over `ui: controls`,
which is why the file has always refused one.

What counts as a colour sample is the idiom, spelled structurally, and each clause was chosen
against a neighbour that must stay painted:

- a `span`, `td` or `th` — never a `div`. A framework writes its containers with inline style
  objects, and sparing those would leave whole white panels on the page; a span is inline
  content, and a cell is one cell.
- a ground written inline **as a number** — `#…`, `rgb(`, `hsl(` — and not with alpha zero.
  `transparent` is the one that bites: a Google-Docs paste puts
  `color:#000000;background-color:transparent` on every span, and sparing that pair would be black
  ink on our black ground. Named colours (`background:yellow`) are not matched, and that is the safe
  direction — a sample missed is painted as it is today.
- and **either** the ink is written inline too — the pair the page already made legible: a legend
  key, a colour-coded results cell, a chip — **or** the element is `:empty`, a stripe cell with no
  ink to worry about. A ground with text and no inline ink stays painted: on a kept light ground our
  yellow would vanish, and black would be a guess that goes wrong on every dark site.

Descendants stop with it. The child spans one parser writes cover the swatch, and a link in a
colour-coded cell must show the page's own blue on the page's own pale rather than our cyan, which
on that pale measures 1.3:1. So every rule that sets a ground or an ink carries the exclusion — the
ten bg/fg painters, both `:empty` sweeps, `ui: links` in every state, and the code inks, which are
split from the monospace face so the face still applies. Chrome and typography do not: a button in
a coloured cell is still a button, and the text in it is still Arial.

The visible consequence beyond the legend is that the article's colour-coded result cells —
`td style="color:black;background-color:#B0CEFF"`, a thousand of them on that page — come back pale
with black ink, the page's own pair, so which party leads each poll is readable at a glance again.
Known limit: a sample drawn with `color` alone — a party stripe is
`<span style="color:#E81B23">▌</span>` — cannot be told from a newsletter's `<span style="color:#333">`
paragraph, and sparing the latter is dark ink on black. The stripe stays yellow.

Eleven new assertions in the fixture: the key in both parser shapes and the named form, the coded
cell and the link inside it at rest and hovered, the empty stripe cell, and the three neighbours — a
`div` pair, the Google-Docs paste and a ground-only highlight — all still painted. ALL 119 PASSED in
both engines.

## 白い熊 Stylus 2.4.10.50 — 2026-09-10

Built on upstream 2.4.10. A daily's article page showed its opener photo at rest and lost it the
moment the mouse crossed it: the whole picture went to a single flat sheet, cyan, which on a photo
reads as white. The library already knew the shape that was doing it; what it had never considered
is that a hover is a state, and a fill applied in that state is a painter. The behavioural fixture
now tests hover, and grew from 98 checks to 108.

### Never let a hover fill paint what the overlays leave transparent

The click target laid across the photo is one `<a>` at `position: absolute; width: 100%;
height: 100%; z-index: 2`, its own background a transparent 1×1 GIF, holding nothing but the
gallery badge in its corner. That is the whole-card click target `ui: overlays` learned in
2.4.10.46, and at rest it was handled: the card-link rule unpainted it at (1,0,3), enough to beat
the bg blankets, and the photo showed. But `ui: links` fills a hovered link cyan at (1,2,1), which
outranks (1,0,3) — so under the mouse the link became an opaque cyan sheet over the whole picture.
Nothing about hover had been thought about at all.

The general statement is that **a hover fill paints exactly as `bg all` does, and nothing
`ui: overlays` leaves transparent may take it**. Running the whole fixture in a hovered state found
a second victim of the same thing: the descendant form `a:hover *` had carried a mechanically
doubled guard at (2,2,1) since the first version — above the named-overlay rule at (2,1,0), so a
hovered Material UI row filled its own ripple span and the label under it went behind a cyan sheet,
and above every other repair in that style too. Nothing ever needed that weight.

Two edits follow. The descendant hover and focus forms in `ui: links` drop to one guard, (1,2,1):
what they have to beat is the text blankets at (1,0,1) and their own rest form, which they do by
being later in the sheet, and at a painter's weight every repair in `ui: overlays` now sits above
them — the ladder reads as it was always meant to, painters at (1,x,y) and repairs above. And the
card link goes to a doubled guard, (2,2,4), so it holds in every state. That makes explicit the two
things the old weight had been losing to on purpose: `:not(:empty)`, since an empty link is a
wordmark and keeps `ui: image-ground`'s grey at (1,1,1), and `:not(LINK_BUTTONS)`, since a link
naming itself a button keeps its `ui: controls` pill at (2,1,1) and its yellow hover at (2,2,1).

The ink has to come back with the ground. The fill also turns the link's text black, which on a
cyan ground is the point and on a now-transparent one, over the black of every ancestor, is black
on black: the ordinary title link beside a picture — the greedy case the card link has always
reached — would vanish while hovered. So a hovered twin restores cyan. Hover only, so `:visited`
keeps its magenta at rest; and the link alone, since `a:hover *` still fills a span or a badge
inside it, and that is the hover cue — the gallery badge comes up black on cyan while the photo
under it stays a photo. The one trade-off: a bare-text title link beside a picture now shows no
visible change under the mouse, cyan on black in both states — legible, and cue-less.

The fixture tests hover from here on. A headless run cannot move a mouse, so every `:hover` in the
injected sheets is rewritten to a class of the same weight, (0,1,0), which makes the cascade
byte-for-byte the one a real hover resolves, and the elements meant to be under the mouse carry the
class. Ten assertions: the sheet, the badge it holds, a hovered title link beside a picture, an
ordinary hovered link and the span the site wrapped its text in, the pill link in both states, the
wordmark's grey, and the hovered ripple. ALL 108 PASSED in both engines.

## 白い熊 Stylus 2.4.10.48 — 2026-08-29

Built on upstream 2.4.10. A sports-equipment shop's product page came back with every picture on
it gone: the main product photo, the thumbnail row under it, and two whole recommendation
carousels, five black rectangles where the pictures had been. One element does all five, and it is
the sixth kind of layer this style has had to learn. The behavioural fixture grew from 93 checks
to 98.

### Never board up a picture with the strip of chrome that drives it

A carousel's nav is one `<div>` stretched over the entire viewport of the carousel —
`position: absolute; inset: 0; z-index: 9; pointer-events: none` — holding the previous and next
buttons and nothing else. Every clause of that says the same thing: it is chrome *for* the picture
underneath, and it is click-through precisely so the picture stays reachable. Painted at (1,0,0),
it is an opaque sheet across the whole photo. `pointer-events: none` also hides it from
`elementsFromPoint`, so a hit test at the centre of the photo reports the `<img>` on top and
nothing above it; only a paint diff of every element's `background-color` names the culprit.

Neither handle `ui: overlays` had could reach it. It is not `:empty` — it holds the two buttons —
and it is not named anything a list could match: the classes read `carousel-navs carousel-def
car-load-hide abs`, which describe the widget, not the painting. `pointer-events: none` is the
honest tell and CSS cannot select on it, a property having no access to its own computed value —
the same wall the padding rule and the CSS triangle already hit.

So the structure carries it: **it holds a control, holds nothing but controls, holds no picture,
and lies beside one**. The sibling test is the one the whole-card click target already uses, and it
applies for the same reason — a strip of chrome and the picture it drives are siblings by
construction. A box whose whole content is chrome has nothing of its own to make legible, which is
the `:empty` argument one step up.

Two clauses are load-bearing in ways worth naming. `:has(> control)` is not redundant beside
`:not(:has(> :not(control)))`: the second is vacuously true of an element with no element children
at all, so without the first every `:empty` layer on the page would match. And "children" there
means **element** children — `:has(> :not(…))` cannot see a text node, so a row of prose with a
button in it is matched as well as a bare strip. That is the rule's real boundary and a mild one:
such a row loses a ground of its own, its ancestors are already black, and its words are already
yellow. A `<span>` around the words puts it back.

Links stay out of the control list, and that was measured rather than assumed. Widening it to the
`LINK_BUTTONS` forms stopped the rule being about chrome: on the video fixture it took a
`bottombar` the page had grounded at `#1a1a1a` and a pagination row — real surfaces of the page's
own making. The met case is `[role="button"]`, and a box holding only links is a menu.

*Measured, Gecko, full page: ink 507 253 px → 1 278 002 px of 9 300 000, and the page's black falls
from 94.5 % to 86.3 %. Across the three older fixtures the new rule reaches 8 elements and moves no
content at all — the bookshop and the newsletter host differ by antialiasing alone, and a second
shop page gains 16 px of a divider that now draws its full width.*

## 白い熊 Stylus 2.4.10.46 — 2026-08-28

Built on upstream 2.4.10. One page, two failures, and each was hiding the other. A bookshop's
search results came back as rows holding a heart and a star rating and nothing else — cover,
author, title, format and price all missing — and repairing the first fault only uncovered the
second. Neither is about colour, and neither was reachable by any rule the library had. The
behavioural fixture grew from 89 checks to 93.

### Never board up a card with its own click target

Every result tile opens with the whole-card click target: one `<a>` laid across the tile at
`position: absolute; inset: 0; font-size: 0; color: transparent; background-color: transparent`,
carrying the accessible name and drawing nothing at all. Every clause of that declaration says the
same thing — it is a hit area. Being absolutely positioned, it paints above every static sibling in
the card, so `bg all` painting it at (1,0,0) turns it into an opaque sheet at the top of the tile's
stack. It is the card idiom every product grid, article teaser and video tile is built from.

Neither handle `ui: overlays` had was ever going to reach it. The class reads
`element-link-toplevel`, which is a fact about the DOM rather than about painting, so no name list
touches it; and it is **not** `:empty`, the accessible name being a text node with a data element
beside it. Links are excluded from that sweep anyway, deliberately, because an empty link is a
wordmark.

The structure is the handle that is left, and it is a good one: **a link that holds no picture of
its own and lies beside one**. Both directions of the sibling axis, because the overlay is written
before the content as often as after it, and spelled out flat — `:has()` may not be nested inside
`:has()`.

Greedy, and here very nearly free. It also reaches the ordinary title link inside a tile, 21 of
them on the alza fixture, and unpainting a text link costs nothing: `bg all` has already blackened
every ancestor, and the link's own box was doing no more than showing that black through. What it
would cost is a pill link carrying a light ground of its own next to a picture — and the ones that
name themselves buttons are still painted by `ui: controls` at (2,1,1), which is where most of that
shape lives.

### Stop burying a picture the page stacked behind itself

With the click target unpainted the tiles got their text back and still showed a blank band where
every cover had been. The second half of the same failure, and this one is ours outright: we bury
the picture.

`z-index: -1` on an in-flow image wrapper is an everyday idiom — it is how a card puts its cover
under the layer that has to stay clickable — and it works only because everything above it is
transparent. Painting order is what makes that fragile. A negative-z child is drawn at step 2 of
its nearest ancestor **stacking context**, while the grounds of ordinary block descendants are
drawn at step 3, above it. That context is `<html>` whenever nothing in between is positioned with
a z-index of its own, so every box we paint between the picture and the root buries it. `<body>`
alone is enough, which means even `bg ground` on its own does it.

The repair goes on the **parent**, and the choice of element is the whole argument. Raising the
picture's own z-index would fix this case and break its mirror: a full-bleed backdrop is
`position: absolute; inset: 0; z-index: -1` behind its section's text, and lifting it paints it
*over* the words. A stacking context around the card asks for exactly what is wanted and nothing
more — the picture is trapped inside its own card, above that card's ground, still below its
siblings, and out of reach of every ancestor. `isolation` rather than `position: relative;
z-index: 0`, because it creates the context without becoming a containing block for anything
positioned inside it, and it leaves `position: fixed` alone, which only transform, filter and
will-change disturb.

The cost is a stacking context around every box that holds a picture directly: a positioned
descendant with a large z-index can no longer escape it, so a dropdown hanging out of such a card
could fall behind the next one. Cosmetic, and narrow — the direct-child test keeps it off the deep
wrappers where those layers usually live — against a cover that is simply gone.

*Measured, Gecko, on the saved page: ink in the results row 5 394 px → 213 211 px of 415 950, and
the page's black falls from 97.8 % to 71.6 %. Every cover, author, title, format, price and rating
is back.*

## 白い熊 Stylus 2.4.10.44 — 2026-08-28

Built on upstream 2.4.10. Two repairs from one page, and neither is about colour: the first is a
layout collapse that rendered a whole domain as a black rectangle, the second an empty box whose
emptiness was the point. The behavioural fixture grew from 84 checks to 89.

### Stop a shut drawer from taking the picture beside it

Every post on an allowlisted newsletter host rendered as a black band under the header — the
viewport, in practice, since header plus band is the whole of it. Switching every colour style off
changed nothing, which is what named the culprit: this was never paint.

`ui: full-width` is the most invasive rule in the library. It fires `width: auto !important` at
every element so a narrow reading column can use the window, and it ships as an allowlist for
exactly that reason. Here it met the idiom that punishes it. A page that keeps a panel in the DOM
at `width: 0` with `overflow: hidden` — a transcript drawer beside a podcast player, an off-canvas
menu, anything that slides — is saying the panel is **closed**. Releasing its width sizes it to the
content it was hiding.

On its own that would be an odd wide box. But such a drawer is nearly always `flex: none` beside a
`flex: auto; min-width: 0` stage, so the space does not come out of the window — it comes out of the
box next to it. And a stage frames its picture with an absolutely-positioned child, so it has **no
intrinsic width of its own to defend with**, and it gives up everything. Measured on a saved post:
the `<video>` collapsed to 0 px wide and what stayed on screen was the player shell's own black 16:9
band.

The repair splits the rule, and the split is the whole argument:

- lifting a **`max-width`** can only ever let a box grow, so that half stays global;
- **`width`** is the half that can shrink a box to nothing, so it now stops at a box that *follows*
  a box framing media.

The row that frames a picture is a geometry the page computed, and nothing in it can be widened
except by taking from the frame.

Two limits are deliberate. Only DOM order **after** the frame, because that is where a drawer is
written — it is appended, not prepended — and the mirrored arm would spare every element that
merely precedes a player, which on a flat page is most of them; the fixture's own column pinned by
`width: 300px` is one, and it caught the greedier draft immediately. And `img`/`picture` stay out:
an image carries its own intrinsic width and cannot collapse, so its neighbours are not part of
this.

One syntax trap cost a draft and is worth recording. `:has()` may not be nested inside `:has()`, and
`:not()` takes a **non-forgiving** selector list — so a single invalid arm silently drops the entire
rule. The first attempt wrote `:has(~ *:has(video))`, the engine kept three of the style's four
rules, and the page appeared fixed precisely because nothing applied at all. The fixture's "every
rule accepted by the engine" check is what caught it.

*Measured, Gecko, on the saved post: hero ink 0 → 58 574, black pixels 93.5 % → 54.5 %, and the
article column keeps exactly the width it had.*

### Give a value bar back the reading it carries

Hovering the volume button slid the time counter aside and opened a volume bar that was entirely
black — no level, no reading, nothing.

A volume slider, a scrubber, a progress bar and a level meter are one idiom: a track, and inside it
a filled part whose width — or height, or `scaleX` — **is** the number. That part holds no text and
no child, because it needs none: its content is its geometry.

Which is exactly the shape the `:empty` sweep in `ui: overlays` exists to neutralise, on the premise
that *an element with no content has nothing of its own to make legible, so painting it can only
produce a sheet*. That premise is what stops an empty pinned layer blanking a page, and here it is
simply wrong. The sweep wiped the level's own white; `bg all` and `bg div` painted the track black;
and the bar opened carrying nothing at all.

So the filled part is given yellow ink of its own — and **only** the filled part. The track stays
black, and the boundary between the two is the number back; colouring the track as well would risk a
grey box wherever a name matched something that is not a bar.

The name is the only handle, as with the icon and artwork lists before it: a hashed class keeps its
readable prefix (`volumeLevel-…`, `progress-…`) and Video.js spells it out (`vjs-volume-level`,
`vjs-play-progress`). It matches on the element **or on its parent**, since a generic
`<div class=fill>` inside `<div class=progress>` is as common as a named level. `range` and `track`
are deliberately absent — they would catch *orange*, *tracking* and *soundtrack* — and the same
media, control and icon guards the sweep uses are kept, so a void `<input type=range>` never takes
the ink. The doubled `#sk-never` guard is load-bearing: the sweep sits near (1,4,2), and no number
of class terms would have cleared it.

The same list had to go on `ui: full-width`'s width release too, for a second and sharper reason: a
bar's width **is** its reading, and our `!important` beats the page's non-important `:hover` rule
however specific that rule is. The slider could never have opened again — it sat pinned at the
content width of an empty div, which is nothing.

*Five new fixture assertions cover it, including that an empty layer which is NOT a value bar still
keeps the sweep rather than the ink. On the saved post both the volume level and the seek progress
compute `rgb(255,255,0)` on a black track, and the slider opens to its full width again.*

### Upstream

No upstream change: still built on Stylus 2.4.10, the same release 2.4.10.41 was built on.

## 白い熊 Stylus 2.4.10.41 — 2026-08-22

Built on upstream 2.4.10. Two repairs, and both are the same kind of mistake: a blanket that
claimed a property the page had already spent on something we cannot see. One hid an icon font, the
other hid an entire site. The behavioural fixture grew from 77 checks to 84.

### Never force a font on a pseudo-element

A video player's transport bar rendered as five little boxes reading `E605`, `E60B`, `E606`, `E603`
and `E601` where play, mute, quality, picture-in-picture and fullscreen belong. Those are Private
Use Area codepoints: the glyphs of an icon font, drawn through `content` on the `::before` of each
control. `sans-serif` forced Arial onto them, Arial has nothing at those codepoints, and Gecko drew
the `.notdef` hex box.

Nothing in `ICONS` could have caught it. The glyph is not on an element named *icon* — it is on the
`::before` of the control itself, whose class says `play-control`, `mute-control`, `fullscreen-control`.
And no name list ever will, because which element carries an icon font is a fact about the page's
*stylesheet*, not about its markup.

So the repair is not another exclusion. Work out what the pseudo form of that blanket could ever
**do** and it comes out a pure loss:

- `font-family` inherits, and a pseudo-element inherits from its originating element. Wherever the
  page declares no font on the pseudo, it already has whatever we gave the element — Arial when
  that element is prose, the icon face when the element is exempt, since `*:not(<icons>)::before`
  skips an exempt element's pseudo too.
- The rule therefore changes exactly one thing: it overrides a font the page put **on the pseudo
  itself**. And setting a font on a pseudo-element is one idiom and one only — an icon font.

A rule whose only reachable effect is to break icon fonts has no defence. The blanket now stops at
the element, needs no `:not()` list, and costs nothing anywhere. The fixture proves the last part:
a pseudo with no font of its own still comes out Arial, by inheritance.

The **element** side of the same failure has no structural handle at all. Video.js declares
`font-family: VideoJS` on `.vjs-play-progress` and `.vjs-volume-level` and draws the scrubber and
volume knobs in a `::before` that inherits it, so forcing Arial on the element takes the pseudo with
it. `vjs-` therefore earns a line on the sans blanket's own exclusion list, on the same terms as
`.fa` and `octicon` already there — a library, not a site. It is kept out of `ICONS` proper because
that list also drives the `:empty` background sweeps and `ui: full-width`, where exempting every
element of a player would have consequences worth arguing about; here the whole cost of a wrong
guess is that an element keeps the font the page chose.

### Never paint a frame

A page reported as showing nothing but its loading animation turned out to be rendering **100 %
black** — measured, one colour, 378 000 pixels. The animation was painting correctly the whole
time. What could not be seen was the entire site.

The sheet was an `<iframe>`. A payment SDK parks a full-viewport `allowtransparency` frame in the
DOM at `z-index: 2147483647`, waiting for a card challenge that may never come; `bg all` painted it
black, and nothing can be above the maximum z-index. A hit-test at the animation's centre put that
frame at the top of an eleven-deep stack, and removing `bg all` alone brought the page back. A
browser extension hangs its own UI in a frame the same way — 白い熊's own SurfingKeys fork was
being blackened by this rule too, and only escaped notice because its frame is `height: 0`.

What you see through an iframe is the **embedded document**; the element's own background shows only
through whatever that document leaves transparent. So painting it is either invisible or
catastrophic, never useful:

- Invisible, because a page that paints its own ground covers ours. A cross-origin document cannot
  be restyled at all, and a same-origin one gets our sheets injected into the frame itself, where
  `bg ground` blackens its `html`/`body` directly. Either way the element's background is dead
  paint.
- Catastrophic, in exactly the way above.

It is the empty-pinned-layer failure of 2.4.10.38 again, and `ui: overlays` cannot reach it: that
sweep excludes media **because** an iframe is always `:empty`. `bg all` now hands every `iframe`
`background-color: transparent`.

Two things about the shape of that repair are load-bearing:

- It is a **separate rule**, not a `:not()` on the blanket. A type selector inside `:not()` costs
  (0,0,1), which would lift `bg all` from (1,0,0) to (1,0,1) and tie it with `ui: image-ground` —
  and the grey behind every transparent PNG would then come or go with the injection order. The
  fixture now fails if the blanket ever leaves (1,0,0).
- `object` and `embed` are the same in kind but stay **out** of it, for that very reason: they
  already carry `ui: image-ground`'s grey at (1,0,1), and contesting it would be the same tie. A
  transparent overlay is an `iframe` in every case met; a plugin element is artwork, and artwork is
  what the grey is for.

## 白い熊 Stylus 2.4.10.38 — 2026-08-21

Built on upstream 2.4.10. Five repairs, and the first is the worst failure this library can
produce: two sites rendered **completely black** — every pixel `#000`, no text, no images, nothing
at all. The other four came out of one saved page whose video preview and download icon had both
vanished. The behavioural fixture grew from 68 checks to 75.

### An empty layer pinned over the viewport blanks the page

A site leaves a layer in the DOM and forgets it. One is a notification host — `position: fixed`,
`inset: 0`, `z-index: 1060`, `pointer-events: none`, and no children — waiting for a toast that
never comes. The other is a consent gate: emptied the moment you accept, given a class that makes
it transparent and click-through, and never removed. Both are the size of the window. `bg all` at
(1,0,0) paints one black, `bg div` at (1,0,1) paints the other, and either style **on its own**
puts an opaque sheet over the entire site.

`ui: overlays` could not see them. It matches the words *overlay*, *backdrop*, *scrim* and
*ripple*, and neither element carries one — the same wall alza.cz's `#fixedBottom` and `.fabs-row`
hit, and those had to be named per site. `pointer-events: none` also keeps such a layer out of
every hit test, so `elementsFromPoint` walks straight past it; the only thing that finds it is a
diff of every element's computed `background-color` before and after injection.

The discriminator is `:empty`, and it is the one the rest of the library already trusts: an element
with no content has nothing of its own to make legible, so painting it can only ever produce a
sheet. `ui: overlays` now sweeps them:

    *:empty:not(#sk-never):not(<icons>):not(<media>):not(<controls>):not(a, [role="link"]):not(hr)
      { background-color: transparent !important }

Every exclusion is load-bearing. Controls: at (1,3,1) this would outrank the `#808080` ground
`ui: controls` gives an empty icon button. Media: `<img>`, `<iframe>` and `<video>` are `:empty` by
definition and `ui: image-ground`'s grey has to survive. Links: an empty link is a picture, treated
below. `<hr>`: void, so always `:empty`, and `ui: borders` fills it yellow to draw the line.

And the asymmetry holds as it does everywhere in this library — spare a decorative bar wrongly and
it stays visible, which is cosmetic; paint a layer wrongly and the page is simply gone.

### An empty link's background image is its wordmark

The same argument as the empty control, one element type further, and the case that shows where the
name heuristic ends. A site draws its wordmark as an empty `<a>` with the PNG as a background —
under a CSS-in-JS hash for a class, so `ART` has not one word to match, and the `:empty` sweep in
`ui: strip-backdrops` erased the logo outright. Being **empty and interactive** is the whole tell: a
page does not leave a transparent click-through layer on a link.

Handing the picture back is only half of it, exactly as with an icon control. That wordmark is dark
navy, so on black it would be as invisible as it was missing; an empty link therefore takes the same
mid grey `ui: image-ground` uses. An empty link with *no* picture cannot show a grey box either — it
has no content to give it width unless the page sized it, and a page only sizes an empty link to
hold a picture.

### A control that is a picture is not chrome

`ui: controls` reads `[role="button"]` as a button, and a site will put that role on anything: a
video player is routinely a `<div role="button">` wrapped around a `<video>`. At 624×351,
`border-radius: 999px` clipped it to an **ellipse** — and the `<video>` inherited the radius with
it, so the whole player went oval. The poster frame went too: it is a `background-image` on the
`<button>` covering the player, and the `:empty` carve-out cannot save it, because that button holds
the play arrow.

Two tests now spare a control, and only from the pill and the image strip — the black ground, the
yellow ink and the yellow trace still apply: a class that says its background is a picture (`ART`,
which gained *poster*, *preview* and *cover* here), or a media child, `:not(:has(> img, > video, …))`.

The media test is deliberately **not** applied to the image strip. `<button><img class=icon></button>`
is an ordinary button and must still lose its gloss gradient, or yellow text lands on white; losing
the pill instead is merely cosmetic.

### A `filter` repaints our ground along with the picture

`filter: brightness(0) invert(1)` is *the* idiom for "make this icon white", and a filter applies to
the element's own background as well as to its content. `brightness(0)` takes `ui: image-ground`'s
`#808080` to black; `invert(1)` takes it to white — and the glyph with it. What you see is a solid
white block where the icon was, measured at `rgb(255, 255, 255)` on a download button's icon. That
is worse than doing nothing: the white glyph would have been perfectly legible on our black.

CSS cannot select on a computed filter, so the repair is to make the ground's contract
unconditional. `ui: image-ground` now sets `filter: none` alongside the grey, and every image shows
its own ink on a ground into which neither dark nor light can vanish. The cost is a page's own
blur-up placeholders and drop-shadows on images — the cosmetic side of the asymmetry again.

### Never recolour a CSS triangle's borders

A play arrow, a select caret, a tooltip point and a speech-bubble tail are all one idiom: two
transparent borders and one coloured. `ui: borders` recoloured **every** side, so the transparent
ones turned yellow and the triangle became a solid square — a white play arrow, reduced to a yellow
block in the middle of a video poster.

CSS cannot ask whether a border is transparent — a property has no access to its own current value,
the same limit that governs the field-padding rule — so the only reachable discriminator is the
name: `TRIANGLES`, matching *arrow*, *caret*, *triangle*, *chevron*, *play* and *tooltip*. Greedy on
purpose: `[class*="play" i]` also catches *display*, *player* and *playlist*, and all that costs is
those keeping the border colour the site chose.

One knock-on worth recording: the carve-out lifts the `ui: borders` blanket from (1,0,0) to (1,1,0),
which would have tied with `ui: focus` and left the choice between cyan and yellow to injection
order. The focus ring therefore carries a doubled guard now, at (2,1,0), above every border rule.

### Upstream 2.4.10

No upstream change in this release — 2.4.10 is the same base as 2.4.10.11 through 2.4.10.36.

## 白い熊 Stylus 2.4.10.36 — 2026-08-20

Built on upstream 2.4.10. Five builds on one theme in four disguises: our own paint landing on top
of the very thing it was meant to make readable. Each was found from a saved page or from the
site's own stylesheet rather than by reading ours, and the behavioural fixture grew from 53 checks
to 68 in step.

### A field's floating label is a bar across the field

Type into unherd.com's registration box and nothing appears. Piano draws the field as
`<p class=input-group><input><span class=placeholder><i class=icon-email>`, and that span is
`position: absolute`, inset over the input's own text line and exactly as wide as it — 588px across
a 588px field, measured in 白い熊's saved copy of the page. Painted black it is an opaque bar over
the field, and the box swallows every keystroke in silence. Not one style's doing either: `bg all`
reaches that span at (1,0,0) and `bg text` at (1,0,1).

A floating label always *follows* its control — that is what makes `input:not(:placeholder-shown) +
label` expressible, so every implementation of the pattern puts it there — and `ui: overlays` now
leaves such a span or label, and whatever it carries, unpainted:

    :is(input, textarea, select):not(#sk-never) ~ :is(span, label):not(#sk-never),
    :is(input, textarea, select):not(#sk-never) ~ :is(span, label):not(#sk-never) *:not(#sk-never)
      { background-color: transparent !important }

Transparency is safe here in a way it is not elsewhere, and the reason is worth keeping hold of:
the control underneath is itself painted by `ui: controls`, so an unpainted label reveals the
field's own black, never the page behind it.

Sibling-scoped, and that took a wrong turn to establish. The first attempt asked instead for
"anything inside an element that holds a control", which reads well and is far too greedy — a page
card that merely contains a search box is such an element, and the fixture caught it unpainting an
`<hr>`, an inline `<svg>` and a cookie-accept link several rows away from the input.

### A shadow root is sealed, and only its tokens get in

Every comment on unherd.com was invisible: bodies and timestamps at rgb(10,10,10) on our black,
while the author names were correctly yellow. CoEditor mounts into
`<div id=my-comments><template shadowrootmode=open>`, and a widget in a shadow root is sealed
against everything we inject — there is no shadow-root injection, and both of `style-injector`'s
routes stop at the host. Two things still cross, because they inherit: `color`, and custom
properties. That is exactly why the names survived — they carry no colour class of their own and
inherit our yellow through the host — while anything with `.text-foreground` kept its light-theme
`#0a0a0a`.

`ui: design tokens` is the answer, and the only style in the library that can reach inside such a
widget. Tailwind v4 declares its tokens on `:root`; `:root` inside a shadow stylesheet matches
**nothing**, because a shadow tree has no root element, so the value the widget reads is the
document's — set them on `<html>` and they land in the sealed tree. Verified against the archive:
62 comment bodies and 266 timestamps, all reached.

Only the tokens that get used **alone** are moved — `--foreground`, `--muted-foreground`, the
surfaces their ink sits on, and the line colours. `--primary`, `--secondary`, `--accent` and
`--destructive` travel with their own `-foreground` partner, a pair the site has already made
legible and that a black ground cannot disturb; moving half of one is how you break a blue button.
Secondary text goes to `#999900` rather than flattening to body yellow, so it keeps a rank of its
own. What no token can reach is a hard-coded arbitrary value: CoEditor's `Reply` is `#6a7282`
written into the class name, and it stays grey.

### An empty control's background image is its label

A control's background image is normally a gloss gradient, which a black `background-color` paints
*behind* rather than over — hence the strip, which is what finally blackened the Search button on
forum.mobilism.org. An **empty** control is the opposite case: the image is the only label it has.
reCAPTCHA's reload, audio and info controls are 48×48 `<button>`s carrying
`background: url(refresh_2x.png)` and nothing at all inside, so the strip left three blank rings and
no way to ask for a new challenge or the audio version.

Two rules were erasing it and the carve-out had to go in both — `ui: controls`, and
`ui: strip-backdrops`, whose `*:empty` sweep an icon button matches by definition. Which of the two
a profile has switched on is not ours to assume.

Restoring the image was only half of it. That ink is black on transparency — reCAPTCHA's measures
as pure `#000` — so on a black button it would have been exactly as gone as before, and an empty
control now takes the same mid grey `ui: image-ground` uses, for the same reason: it is the one
value where neither dark nor light ink can disappear. Classes that say `icon` are left out of the
grey, since those draw their glyph with `color` and it is already yellow.

`:empty` carries the whole distinction and is exact at both ends: an icon drawn as an inline `<svg>`
child makes the button non-empty and needs none of this, while `input[type=submit|button|reset]` are
void elements and therefore always empty, so they are split out and keep being stripped
unconditionally.

Still open at the time of this release: the three controls in reCAPTCHA's *image challenge* footer
are unfixed, and not for this reason — the shipped build demonstrably keeps their picture, and the
same mechanism visibly works on unherd.com's own dialog close button. That one needs the real DOM
of the challenge frame, which is generated at runtime and cannot be read from the release's static
files.

### Never shrink the room a field made for its icon

The pill's rounded ends want a little horizontal padding so the text does not sit against them, and
forcing that was the mistake: a site that pads a field generously is nearly always making room for a
leading icon. Piano pads its login field 16px for the envelope, `0.7em` cut it to 9.8px — less than
the glyph is wide — and the first characters of what you type went behind it.

CSS has no way to say "at least this much", since a property cannot read its own current value, so
the only safe move is not to touch a field that has an adornment to make room for:

    *:not(:has(> :is(span, label, i, svg, img))):not(#sk-never) > input:not(#sk-never):is(…)

The test is on the parent's children rather than on the input's later siblings, which catches a
leading icon written before the input as well as after it. Greedy on purpose, and here that costs
nothing, unlike everywhere else in the library: over-matching only means a field keeps the padding
the site chose, which is by definition what the site wanted.

### An empty box IS its picture

`ui: strip-backdrops` erases the background image of every `:empty` element, because an empty box
carrying only a gradient is a decorative strip. An empty box carrying only a `url()` is the
opposite — it *is* the picture — and CSS cannot tell the two apart, so the style leans on what the
thing is named. Its carve-out knew only the word *icon*.

reCAPTCHA's privacy badge is `<div class="rc-anchor-logo-img rc-anchor-logo-img-large">` with
`background: url(logo_48.png)` and nothing else, so the sweep took the logo and left an empty box in
the corner of the page. `ART` now carries the rest of the vocabulary — logo, brand, badge, avatar,
sprite, flag, thumb, img, photo, picture — and the asymmetry that governs the whole library decides
how generous to be: spare something wrongly and a decorative bar stays visible, which is cosmetic;
strip something wrongly and content is simply gone.

No mid-grey ground for this one, and the measurement is the reason: the badge's ink is `#b4b4b4` and
`#4e8df5`, which is 10.1:1 against black and 1.9:1 against `#808080`. Which ground rescues artwork
depends on its ink, so the grey is never a reflex.

## 白い熊 Stylus 2.4.10.31 — 2026-08-20

Built on upstream 2.4.10. One fix, and one investigation that ended with nothing to change here.

### A ripple layer is a sheet over the thing it decorates

alza.cz's category sidebar — the whole left column of the home page, twenty-four rows — rendered as
a solid black block: no label, no icon, nothing but the yellow trace around each row. The cause is a
component library's decoration. Material UI ends every clickable with
`<span class="MuiTouchRipple-root">`, absolutely positioned, `inset: 0`, `pointer-events: none`, and
the **last child** of the item, so the moment it is given a background it becomes an opaque sheet
over the item's own text and icon.

`pointer-events: none` is also why it hides from investigation: it never answers a hit test, so
probing the black pixels returns the label that is *underneath* it and everything looks correct.
What named it was a bisect of the twenty style blocks 白い熊's saved copy of the page carried, each
combination re-rendered in Gecko: `bg all` alone blanked the sidebar, `bg text` alone blanked it, and
`bg div` never did. The one thing the first two share and the third lacks is `span`.

The rule went to `ui: overlays`, which exists for precisely this class of element — one whose class
name says it is a transparent layer over the page — and whose doubled guard puts it at (2,1,0),
above every `bg` rule without lifting the blankets themselves:

    span[class*="ripple" i]:not(#sk-never):not(#sk-never) { background-color: transparent !important }

It is restricted to `span` deliberately. Vuetify (`v-ripple__container`) and Angular Material
(`mat-ripple-element`) build their layer as a span as well, but Material Components Web puts
`mdc-ripple-upgraded` on the **button itself** — a surface that has to keep its ground, not a layer
to see through. Three assertions hold the distinction: the layer stays transparent, the label under
it keeps its own ground and colour, and a button merely marked as a ripple surface is left alone.

### Black boxes in 白い熊 SurfingKeys' URL prompt — diagnosed, and not ours to fix

The 白い熊 SurfingKeys session reported black rectangles on the focused row of its search list,
traced them to `bg all` and `ui: full-width`, and asked for the library to be excluded from
`moz-extension://` documents. The exclusion would have changed nothing, because no add-on page is
reachable from here in the first place: the single content script matches `<all_urls>`, and Gecko
expands that to exactly `{http, https, ws, wss, file, ftp, data}` — `PermittedSchemes` in
`toolkit/components/extensions/MatchPattern.cpp`. `moz-extension` is not in the set.

What was on screen was not the omnibar in that add-on's iframe but its own URL prompt, which appends
its `<style>` and its container to the **host page's** document with no shadow root, unlike the rest
of its chrome — page content, indistinguishable from a card on a news site, and painted as designed.
Its own reset, `#sk_shiroikuma_urlbar * { all: unset !important }`, is worth (1,0,0), which `bg text`
and `bg div` outrank at (1,0,1); its `li.focused` at (1,1,0) outranks `bg all` and survived, which is
why the row colours were right and only their children went black. This library injects author-origin
`<style>` elements always — `styleViaAPI` is reached only for XML documents in Firefox and passes no
`cssOrigin` — so a page can outrank it, and that session did, by doubling its widget's id.

No carve-out was added here for it: naming one id in the generator protects that id only until it is
renamed, whereas the doubled id travels with the widget that needs it.

## 白い熊 Stylus 2.4.10.29 — 2026-08-19

Five builds on from 2.4.10.24, all of them driven by page archives rather than by reading CSS.

### Colour paints behind an image — the fourth instalment

vBulletin forums paint every `.thead`/`.tcat`/`.tfoot` bar with a tiled gradient strip, which is
where `mobileread.com`'s light-blue bars and the white strips under yellow text came from. `bg
blocks` already painted those same elements black; it now clears their background image too, so it
stops leaving its own work half done.

The rule was first put in `ui: strip-backdrops`, and that was a mistake worth recording. That style
ships **enabled**, but the sync deliberately preserves each profile's own on/off state — so on a
profile where it had been switched off, the fix could never run. The archive settled it: `:empty`
appears zero times in the CSS Stylus injected into that page. The verification suite now runs twice,
once as shipped and once with `strip-backdrops` removed, so no rule can silently become dependent on
a style that a given profile has turned off.

### `ui: full-width` is now an allowlist

`width: auto` on every element is too invasive to inflict on every site, so the style is enabled
with `overridden` set and inclusions limited to `substack.com` and `unherd.com`. Adding a site is
one keystroke — the popup's ☰, then `+` on the domain row. The sync preserves `overridden` once a
profile has an opinion about it, so an update cannot re-tick a box that was deliberately cleared.

It also skips `[style*="width"]`. An `!important` author rule outranks a **non-important inline
style**, so `width: auto !important` was beating `style="width: 41px"` and collapsing
absolutely-positioned overlays to zero width — reported by the 白い熊 SurfingKeys session, whose
in-page search marks had become 1px hairlines. Any extension that draws overlays into the page and
sizes them inline was affected, and the failure looks like *that* extension is broken. Measured
0px → 41px, with a permanent assertion against regression.

### Delivery and documentation

- Every Mozilla-signed `.xpi` now goes to the phone automatically; unsigned builds never leave the
  PC and are named `…-unsigned.xpi` so the two can never be confused at the moment of installing.
- The Android open question is dropped, and with it a genuinely dangerous piece of stale
  documentation: the fork's own guidance file still claimed nothing had ever been signed and that
  the add-on ID becomes permanent at the first signing run, so signing should wait — advice that
  would have stopped a release being cut at all.

## 白い熊 Stylus 2.4.10.24 — 2026-08-19

Thirteen builds of fixes to the preinstalled library, all of them found by measuring real pages
rather than reading CSS. The library is now 26 styles: 21 global and 5 site-specific.

### Stop painting over things that were never painted

A run of faults with one shape — an element transparent by design, given a background and turned
into an opaque sheet over whatever it covered.

- **`bg all` no longer touches `::before`/`::after`.** A pseudo-element carrying `content` is
  decoration, very often a transparent absolutely-positioned overlay for a hover shade. Painting
  them blanked **24 overlays** in alza.cz's product carousel, taking the image, stars, name and
  price with them while the z-indexed badge and the buttons outside the tile survived. Colour still
  reaches pseudo-elements, because text drawn in one has to be yellow: painting can only hide,
  colouring cannot.
- **New `ui: overlays`** leaves anything whose class says `overlay`, `backdrop` or `scrim` with its
  own background. The same heuristic as the icon list — match how a thing is named. The asymmetry
  justifies it: a light scrim staying light is cosmetic, a painted one hides the page.
- Three transparent, `pointer-events: none` hosts on alza.cz — `#fixedBottom`, `.js-cookies-info`
  and `.fabs-row` — each of which became a black band across the bottom of every page.

### Colour paints behind an image, never over it

- **`bg ground` clears the page wallpaper.** A `linear-gradient(#ccc, #e8e8e8)` on `<body>` was what
  showed down both margins on forum.mobilism.org, untouched by any amount of `background-color`.
- **Controls clear their gloss gradient**, which is what kept that site's Search button white even
  once the selector was reaching it, and `input[type=submit|button|reset]` are now treated as the
  buttons they are.
- A **mid-grey ground behind transparent artwork** rather than white: white fixes dark ink and
  destroys light ink, which erased a set of nav icons. `#808080` is the one value where neither can
  disappear.

### Width

`ui: full-width` neutralises `width`, not only `max-width` — neither page that prompted the style
was constrained by `max-width` at all. substack.com pins its column with `width: 728px` and auto
margins; it now fills the window. The style keeps a `1em` gutter on `<body>` so released text does
not sit against the window edge, and ships with jisho.org excluded.

### Per-site rules, where no selector can generalise

- **alza.cz** — `#detailItem`'s section texture; the three transparent bottom hosts above.
- **unherd.com** — the article is a `flex: 0 0 50%` column in a row that only adds up to 75%. The
  column is grown and the tag sidebar hidden, taking body text from 944px to the full row.

### Specificity, and the ladder

An `!important` beats another `!important` only on specificity, so a blanket `*` rule loses to any
page `.card { background: #fff !important }`. Every rule that must win such a fight carries
`:not(#sk-never)`, an id matching nothing: **(1,0,0)** for the blankets, **(1,0,1)** for element
groups, **(1,1,x)** for UI affordances, **(2,0,0)** for site rules that have to clear them all.

### Elsewhere

- The **running build is stamped at the foot of the popup**, read from the manifest. A screenshot
  that does not say which version produced it costs a whole round trip.
- **Unsigned builds are named `…-unsigned.xpi`.** Only a signed build may go to the phone, and only
  a signed build installs in a stock Firefox; the file name is the only thing visible when
  installing.
- The behavioural test is up to **48 assertions**, run in both Gecko and Blink, and now honours the
  shipped `enabled` flag so a style that ships off is not tested as though it were live.

## 白い熊 Stylus 2.4.10.11 — 2026-08-19

The first published release, on upstream **v2.4.10**. Two layers: an identity layer that makes this
its own add-on, and a reading layer — a style library and a themed UI that arrive already set up.

### Preinstalled style library

- **23 styles installed on first run**, no import step. Ten of them form a matrix — black background
  and yellow text, each split by selector group (`all`, `html/body`, `div`, block containers, text
  elements) — so a site can be told to drop the yellow on `div` without losing it everywhere. They
  sort into popup positions 1–9 and 0, making per-site tuning a three-key gesture: hold `Enter`,
  tap the digit, press `Shift-1` to exclude the domain.
- **The library is synced to every build, not seeded once.** Gated on a hash of the shipped set, the
  sync matches styles by name, keeps the id, the on/off state and the per-site exclusions and
  inclusions, and replaces only the CSS; styles it shipped before and no longer ships are withdrawn.
  Per-site tuning therefore survives an update untouched.
- **Icon fonts keep working.** `font-family` cannot be repaired by overriding — no value means "the
  font this page wanted", and `revert` drops to the UA default — so icons are excluded from the
  blanket by selector. `line-height` is repaired the other way, by handing icons, controls and media
  `line-height: normal`, which is recomputed per element and so cannot be inherited as a stale
  length. One shared list drives both, matching how icon systems are built rather than which site
  uses them.
- **A specificity ladder.** An `!important` beats another `!important` only on specificity, so a
  blanket `*` rule loses to any page `.card { background: #fff !important }`. Every rule that has to
  win such a fight carries `:not(#sk-never)`, an id matching nothing: (1,0,0) for the blankets,
  (1,0,1) for element groups, (1,1,x) for the UI affordances that must beat both.
- Cyan links, distinct from body text, with icons inside links exempted so they stay yellow.
  Monospace and a readable grey for code. Traced yellow pills for buttons, for links that act as
  buttons (`href="javascript:"`, `class*="btn"`), and for single-line text inputs. A cyan focus
  ring. Yellow borders, rules and dividers throughout. `max-width: none` to hand narrow article
  columns the full window. A mid-grey ground behind transparent artwork, so neither dark nor light
  ink can disappear on a black page.
- One style, **`ui: strip-backdrops`**, ships **disabled**: removing background images clears
  decorative pale bars but cannot be told apart from content, and it cost a site logo and a product
  carousel before being switched off. Enable it per site where the trade is worth it.
- Generated by `tools/make-default-styles.py` and covered by `tools/verify-default-styles.py`, which
  builds a fixture page that fights back the way real sites do and asserts 42 computed styles in
  both Gecko and Blink.

### The extension's own windows

- The popup, manager, options page and editor are **black and yellow** at a 16px base, up from
  upstream's 12px. Upstream drives its UI from tokens, so this is largely a re-declaration of them:
  the neutral ramp becomes black-to-yellow, cyan stays the interactive accent.
- CodeMirror's built-in theme is restated — its default token colours are close to invisible on
  black — while leaving a theme chosen in the editor settings free to win.
- Scheme-independent by design: forcing the dark scheme would have been shorter, but that preference
  also decides which user styles apply.
- Two upstream defaults moved: **“display enabled styles before disabled styles” off**, because it
  re-sorts the popup and moves the digit positions the library depends on, and **“show number of
  styles” off**, the badge being the same number on every page once the library is global.

### Identity

- Our own permanent add-on ID, **`stylus@shiroikuma`**, replacing upstream's
  `{7a7a4a92-a2a0-41d1-9fd7-1e92480d612d}`. AMO will not sign an ID registered to somebody else,
  add-on updates are keyed to the ID forever, and owning it is what lets this build install
  **alongside** an unmodified Stylus in the same profile.
- Declared for **Firefox on Android** via `gecko_android` (`strict_min_version 120.0`); upstream
  ships no such key, which marks its build desktop-only.
- `gecko.strict_min_version` deliberately left at upstream's `68.0` — the build feeds it to babel as
  a browser target, so raising it would silently change transpilation.

### Branding

- Named **白い熊 Stylus** in the manifest, the browser-action tooltip, the options page title, the
  editor's window title, the connection-failure message and the injector's console messages.
- **Every user-facing link points at this repository** — the links panel, the editor's
  style-writing and UserCSS documentation icons, the popup's hotkeys wiki link, the crash reporter's
  issue search and report links, and the UserCSS template's `@namespace`. Upstream's Transifex link
  is dropped — this fork has no translation project of its own. Only code comments citing an
  upstream issue number still point upstream, those being source citations rather than links a user
  can follow.
- Localized strings are renamed **at build time** from an explicit allowlist of message keys
  (`tools/fork.js`), so `src/_locales/` stays byte-identical to upstream and its weekly Transifex
  churn never conflicts with the fork.
- Nothing renamed in the other two senses of "Stylus": the CSS preprocessor language, and the
  page-facing identifiers user styles and the galleries match on — the injected `style.stylus` class,
  the `stylus-uso` and `usw-remove-stylus-button` events, the `html[stylus-iframe]` attribute and the
  `Stylus` gallery search category.

### Icon

- A black-and-yellow icon **traced** from upstream's own artwork with potrace — pure yellow
  `#FFFF00` on black, nothing freehand, so it still reads as the same extension.
- All 26 assets regenerate from one master SVG via `graphics/make-icons.py`, including upstream's
  washed-out and all-disabled toolbar states and the whole `light/` set. Upstream's red "all styles
  disabled" state becomes a dimmed `#666600`, the house palette having no third colour.

### Packaging

- Version scheme `<upstream version>.<our build>` — one string for the manifest, the tag, the release
  title and the `.xpi` filename. Firefox and AMO accept only 1–4 plain dot-separated integers, so this
  fork carries no `+NNN` form and never zero-pads.
- `tools/build-fork.mjs` builds, packages and stamps the version, drops the `.xpi` in `~/tmp`, and
  bumps the counter; `--sign` produces the AMO-signed unlisted build attached to this release.
- AMO credentials live in a gitignored `amo.properties`, mirroring `keystore.properties` in the
  Android forks.

### Upstream v2.4.10 (2026-08-08)

- editor: fix infinite loop when clicking "+" to add a new section
- editor: fix flicker on opening in MV2/Firefox
