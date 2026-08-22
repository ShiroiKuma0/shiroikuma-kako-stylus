# Changelog

This file carries **both histories**: 白い熊 Stylus' releases and, folded into each one, the notes
for the upstream [Stylus](https://github.com/openstyles/stylus) release it is built on. Upstream
ships no changelog file of its own — its notes live only on GitHub Releases — so this file is
entirely ours to maintain, newest first.

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
