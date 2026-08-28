# CLAUDE.md — 白い熊 Stylus (`stylus@shiroikuma`)

Guidance for Claude Code in this repository. It captures the fork's facts so a fresh session can
pick up where the last one left off. For **syncing to a new upstream release**, the authoritative
procedure is `.claude/skills/upstream-new-version`; for **building and signing**, `.claude/skills/build-xpi`.

## Project

**白い熊 Stylus** — 白い熊's fork of [Stylus](https://github.com/openstyles/stylus), the userstyle
manager, for **白い熊 火狐** (`~/git/shiroikuma-kako`) on desktop and Android. A WebExtension: MV2 for
Firefox, MV3 for Chromium; we ship the **Firefox MV2** build only.

### ⚠ Read this before you touch anything: the upstream is Stylus, not Stylish

This repo was first requested as a fork of `stylish-userstyles/stylish`. That repo is the **original
XUL/XPCOM Stylish, dead since 2016** — `install.rdf` with `maxVersion 51.0`, `chrome.manifest`,
compiled `.xpt` typelibs, no `manifest.json` anywhere. Firefox dropped XUL add-ons in 57, so it cannot
load in 白い熊 火狐 (Firefox release 151) at all, and AMO cannot sign it. 白い熊 chose
`openstyles/stylus` instead on 2026-08-18 — the community's continuation of the same lineage, forked
from that same org's `stylish-chrome` after Stylish was sold to an analytics company. **Do not
"restore" the Stylish upstream.**

## Fork model

| Ref | Role | Update mode |
| --- | --- | --- |
| `origin` | `git@github.com:ShiroiKuma0/shiroikuma-kako-stylus.git` — our fork, push here | `git push` (only on 白い熊's explicit go-ahead) |
| `upstream` | `https://github.com/openstyles/stylus.git` — read-only; its push URL is deliberately set to `DISABLED_upstream_is_fetch_only` | `git fetch upstream` |
| `master` | pure mirror of `upstream/master`. **Fast-forward only — never develop here, never carry our work** | `git merge --ff-only upstream/master` |
| **`custom`** | **all fork work**, a small stack rebased onto each upstream **release tag**. This is the working branch | `git rebase --onto <newtag> <oldtag> custom` |

`custom` sits on upstream **release tags** (`v2.4.10`, …), not on `master`'s tip — upstream commits
several times a week, and a release is a stable base. `master` still mirrors the tip so a sync can see
what has landed.

## ⚠ "Stylus" is three different words — only one is ours to rename

A blind rename breaks style injection and gallery installs. This is the single most dangerous thing
in the tree.

| Sense | Where | Rule |
| --- | --- | --- |
| **The product** | manifest `name` / `default_title`, `options.html` title, editor window-title suffix, the links panel, crash reporter, the branded locale keys | **ours to rename** |
| **The CSS preprocessor language** | `src/js/worker/pre-stylus.js`, `loadStylusLang` / `stylusLang`, `src/edit/linter/defaults.js`, `src/cm/`, usercss `preprocessor: stylus`, `patchStylus` in `tools/wp-patch-codemirror.js`, the `stylus-lang-bundle` dependency | **never touch** |
| **Page-facing protocol** | `src/content/style-injector.js` `const CLASS = 'stylus'` (the class on every injected `<style>`), the `'stylus-uso'` event in `hook-uso.js`, `'usw-remove-stylus-button'`, the `html[stylus-iframe]` attribute and its two `optionsAdvancedExposeIframes*` strings, the `'Stylus'` gallery search category in `src/popup/search.js` | **never touch** — user styles and the galleries match on these |

Also left alone on purpose: `openstyles/*` entries in `package.json` `dependencies` (they are real
packages, not branding), upstream attribution comments such as `src/cm/css.js` "Modded by Stylus
Team" (GPL credit), and internal type names like `StylusClientData`.

## Our customizations

| What | Value | Where |
| --- | --- | --- |
| Add-on ID | `stylus@shiroikuma` | `src/manifest-mv2-firefox.json` → `browser_specific_settings.gecko.id` |
| Android compatibility | `gecko_android.strict_min_version: "120.0"` (upstream declares none) | same file |
| `gecko.strict_min_version` | left at upstream's `68.0` — `getBrowserTargets()` in `tools/util.js` feeds it to babel, so raising it silently changes transpilation | same file |
| Name, tooltip, homepage | 白い熊 Stylus, our repo | `src/manifest.json` |
| Package identity | name, description, `repository`, author 白い熊 | `package.json` (its `version` stays upstream's literal) |
| Icon | traced black-yellow, all 26 assets | `src/icon/`, from `graphics/icon.svg` via `graphics/make-icons.py` |
| Every user-facing link | our repo / wiki / issues | `src/manage.html` links panel, `src/edit.html` (Writing-styles, Writing-UserCSS), `src/popup/hotkeys.js` (Popup), `src/js/dom-error.js`, `src/background/usercss-template.js`. Only code comments citing an upstream issue number still point upstream — those are source citations, and our tracker has no such issues |
| Product name in the UI | 白い熊 Stylus | `src/options.html`, `src/edit/editor.js` (window title), `src/js/msg-api.js`, two console messages |
| Localized product name | renamed **at build time** | `tools/fork.js` → `BRANDED_KEYS` + `brandLocale`, wired into the `_locales/**` CopyPlugin pattern |
| Version | upstream's + our build counter | `tools/fork.js` → `BUILD`, appended in `makeManifest` |
| Build counter | `BUILD_NUMBER` | `fork.properties` |
| Credentials | AMO API key pair | `amo.properties` (**gitignored**) |
| Preinstalled styles | 白い熊's reading library — 23 styles, **synced to the build at every startup**, not seeded once | `src/background/fork-default-styles.json` (generated by `tools/make-default-styles.py`, never hand-edited) + `src/background/fork-default-styles.js`, which hooks itself onto `bgBusy`. Gated on a djb2 hash of the shipped JSON; on a change it matches **by name**, keeps `enabled`/`exclusions`/`inclusions`/`id` and replaces only the CSS, then withdraws marked styles the build no longer ships. ⚠ An earlier version seeded once and bailed whenever the DB was non-empty — every later build then shipped a corrected library that was silently discarded, and 2.4.10.4/.5 changed nothing on any page. Never gate this on `styleMap.size` alone. Behavioural test: `tools/verify-default-styles.py` |
| ⚠ `bg all` must never paint `::before`/`::after` | A pseudo-element with `content` is decoration, very often a transparent absolutely-positioned overlay for a hover shade; giving it a background paints an opaque sheet over whatever it covers. It blanked 24 overlays in alza.cz's product carousel — image, stars, name and price gone, while the z-indexed badge and the button outside the tile survived. Colour is safe (`fg all` keeps the pseudo-elements, since text in a pseudo must be yellow): painting can only hide, colouring cannot | `tools/make-default-styles.py` |
| ⚠ A control's floating label must never be painted | A floating label or fake placeholder is a `span`/`label` that **follows** its `input` — it has to, since that is what makes `input:not(:placeholder-shown) + label` expressible — and it is laid back *over* the input's own text line. Painted, it is an opaque bar across the field and the box swallows every keystroke in silence: unherd.com's registration box, where Piano draws `<p class=input-group><input><span class=placeholder>`. Reached by `bg all` at (1,0,0) and by `bg text` at (1,0,1), so it is not one style's doing. The repair lives in `ui: overlays` and is **sibling-scoped on purpose**: the first attempt asked for "anything inside an element holding a control", which a page card containing a search box also is, and it unpainted an `<hr>`, an inline `<svg>` and a cookie link rows away | `tools/make-default-styles.py` |
| ⚠ An empty box IS its background image | The `:empty` sweep in `ui: strip-backdrops` cannot tell a picture from a decorative strip, and its carve-out only knew the word *icon*. reCAPTCHA's privacy badge is `<div class="rc-anchor-logo-img rc-anchor-logo-img-large">` with `background: url(logo_48.png)` — nothing in `ICONS` comes near it, so the sweep erased the logo and left an empty box. Hence `ART`: the words that mean "this background is a picture" — logo, brand, badge, avatar, sprite, flag, thumb, img, photo, picture, and later poster, preview, cover — the same name-matching heuristic as `ICONS`, and governed by the same asymmetry: spare something wrongly and a decorative bar stays visible, which is cosmetic; strip something wrongly and content is simply gone. Note the badge needs **no** `ui: image-ground` grey — its ink measures `#b4b4b4`/`#4e8df5`, which is 10.1:1 on black and 1.9:1 on `#808080`; which ground helps depends on the ink, so do not reach for the grey by reflex | `tools/make-default-styles.py` |
| ⚠ An empty control's background image IS its label | `ui: controls` strips `background-image` from controls because a control's image is normally a gloss gradient that a black `background-color` would paint *behind* rather than over — the forum.mobilism.org Search button. But an **empty** control is the other case: reCAPTCHA's reload, audio and info controls are 48×48 `<button>`s carrying `background: url(refresh_2x.png)` and nothing inside, so stripping it left three blank rings and no way to ask for a new challenge. Two rules did it — `ui: controls` and `ui: strip-backdrops`, whose `*:empty` sweep an icon button matches by definition — so the carve-out is in **both**, since which style is on is per-profile. Restoring the image is only half: that ink is black on transparency (measured: pure `#000`), so on our black button it would be exactly as gone, and an empty control therefore takes the same mid grey `ui: image-ground` uses. Classes saying `icon` are excluded from the grey — those draw the glyph with `color`, already yellow. `:empty` is the whole discriminator, and it is exact for the wrong reasons too: an icon drawn as an inline `<svg>` child makes the button non-empty and needs none of this, while `input[type=submit\|button\|reset]` are void and so always `:empty`, which is why they are split out and stripped unconditionally | `tools/make-default-styles.py` |
| ⚠ An empty layer pinned over the viewport blanks the page | The worst failure this library can produce: two sites rendered **100 % black**, every pixel `#000`. Each leaves an empty, click-through, viewport-sized layer in the DOM — one a notification host (`fixed`, `inset: 0`, `z-index: 1060`, `pointer-events: none`, no children) waiting for a toast that never comes, the other a consent gate emptied on accept but never removed — and `bg all` at (1,0,0) or `bg div` at (1,0,1) turns it into an opaque sheet over the site. Either style **alone** does it. `ui: overlays` could not see them: it matches the words overlay/backdrop/scrim/ripple and neither element carries one, which is the same wall alza.cz's `#fixedBottom` and `.fabs-row` hit — those had to be named per site, and this cannot be. `pointer-events: none` also hides such a layer from `elementsFromPoint`, so it never appears in a hit-test — only a paint diff of every element's `background-color` before and after injection finds it. The discriminator is `:empty`, the one the rest of this file already trusts: an element with no content has nothing of its own to make legible, so painting it can only ever produce a sheet. The sweep lives in `ui: overlays` and every exclusion is load-bearing — controls (at (1,3,1) it would outrank the `#808080` ground given to an empty icon button), media (`img`/`iframe`/`video` are `:empty` by definition), links (an empty link is a picture, below) and `hr` (void, so always `:empty`, and `ui: borders` fills it yellow to draw the line) | `tools/make-default-styles.py` |
| ⚠ A frame is a window, not a surface | What you see through an `<iframe>` is the embedded document; the element's own background shows only through whatever that document leaves transparent. So painting it is either invisible or catastrophic, never useful. Invisible, because a page that paints its own ground covers ours — and a cross-origin document cannot be restyled at all, while a same-origin one gets our sheets injected into the frame itself, where `bg ground` blackens its `html`/`body` directly. Catastrophic, because the transparent frame is an idiom: a payment SDK parks a full-viewport `allowtransparency` frame in the DOM at `z-index: 2147483647` waiting for a card challenge that may never come, and an extension hangs its own UI in one the same way. Black, that frame is an opaque sheet over the whole viewport at the maximum z-index — nothing can be above it and the page renders 100 % `#000`, which is how a loading animation came to be reported as invisible. It is the empty-pinned-layer failure again and `ui: overlays` cannot reach it: its `:empty` sweep excludes media **because** an iframe is always `:empty`. The repair is a separate `background-color: transparent` rule rather than a `:not()` on the blanket, and that is load-bearing — a type selector inside `:not()` costs (0,0,1) and would lift `bg all` from (1,0,0) to (1,0,1), tying it with `ui: image-ground` so the grey behind every transparent PNG would come or go with the injection order. `object` and `embed` are the same in kind but stay out for that very reason: they already carry that grey at (1,0,1), and an overlay frame is an `iframe` in every case met | `tools/make-default-styles.py` |
| ⚠ An empty link's background image IS its wordmark | The same argument as the empty control, one element type further, and the case that shows where the name heuristic ends. A wordmark drawn as an empty `<a>` with the PNG as its background, under a CSS-in-JS hash for a class, gives `ART` no word to match at all, so the `:empty` sweep in `ui: strip-backdrops` simply erased it. Being **empty and interactive** is the whole tell — a page does not leave a transparent click-through layer on an `<a>`. The grey has to come with the picture, as ever: that wordmark is dark navy and handing it back on black leaves it just as invisible. An empty link with no picture cannot show a grey box either, having no content to give it width unless the page sized it — and a page only sizes an empty link to hold a picture | `tools/make-default-styles.py` |
| ⚠ A control that is a picture is not chrome | `ui: controls` reads `[role="button"]` as a button, and a site will put that role on anything — a video player is routinely `<div role="button">` around a `<video>`, in the case met here 624×351 and under a hashed class name that says nothing. `border-radius: 999px` clipped it to an **ellipse**, and the `<video>` inherited the radius with it. The poster frame went too: it is a `background-image` on the `<button>` covering the player — that one *is* named, `…placeholderWithPoster…` — and the `:empty` carve-out cannot save it because the button holds the play arrow. Two tests spare a control now, and only from the pill and the image strip — the black ground, the yellow ink and the trace still apply: a name that says picture (`ART`, which gained *poster*, *preview*, *cover* here) or a **media child**, `:not(:has(> img, > video, …))`. The media test is deliberately not on the image strip: `<button><img class=icon></button>` is an ordinary button and must still lose its gloss gradient, where losing the pill would only be cosmetic | `tools/make-default-styles.py` |
| ⚠ A `filter` repaints our ground along with the picture | `filter: brightness(0) invert(1)` is **the** idiom for "make this icon white", and a filter applies to the element's own background as well as to its content: `brightness(0)` takes `ui: image-ground`'s `#808080` to black, `invert(1)` takes it to white, and glyph and ground come out the same colour. What you see is a solid white block where the icon was, measured at `rgb(255,255,255)` on a download button's icon. Worse than doing nothing, since the white glyph would have been perfectly legible on our black. CSS cannot select on a computed filter, so the repair is to make the ground's contract unconditional instead: `ui: image-ground` sets `filter: none` alongside the grey, and every image then shows its own ink on a ground neither dark nor light can vanish into. The cost is a page's own blur-up placeholders and drop-shadows, which is the cosmetic side of the asymmetry | `tools/make-default-styles.py` |
| ⚠ Never recolour a CSS triangle's borders | A play arrow, a select caret, a tooltip point and a speech-bubble tail are all one idiom: two transparent borders and one coloured. `ui: borders` recoloured **every** side, so the transparent ones turned yellow and the triangle became a solid square — a white play arrow, a yellow block in the middle of a video poster. CSS cannot ask whether a border is transparent (a property has no access to its own current value, the same limit as the padding row below), so the only reachable discriminator is the name: `TRIANGLES`, matching arrow/caret/triangle/chevron/play/tooltip. Greedy on purpose — `[class*="play" i]` also catches *display*, *player* and *playlist* — and that costs only those keeping the border colour the site chose. Note the knock-on: the carve-out lifts the `ui: borders` blanket from (1,0,0) to (1,1,0), which would have tied with `ui: focus`, so the focus ring now carries a doubled guard at (2,1,0) to stay above every border rule | `tools/make-default-styles.py` |
| ⚠ Never shrink a field's padding | `ui: controls` gives text inputs `0.7em` of horizontal padding so the pill's rounded ends do not sit against the text. Forcing it is the bug: a site that pads a field generously is nearly always making room for a **leading icon**, and a smaller value walks the typed text straight underneath it — Piano pads its login field for the envelope, `0.7em` cut it back, and the first characters vanished behind the glyph. CSS has no "at least this much" for padding (a property cannot read its own current value), so the padding is now applied **only to a field with nothing beside it**: `*:not(:has(> :is(span, label, i, svg, img))) > input`. The test is on the parent's children, not the input's later siblings, so a leading icon written *before* the input counts too. Greedy on purpose, and here that is free — over-matching only means a field keeps the padding the site chose | `tools/make-default-styles.py` |
| ⚠ Shadow DOM is sealed — only tokens get in | Stylus has **no shadow-root injection**: `style-injector.js` writes to the page or to `document.adoptedStyleSheets`, and both stop at the host. Two things still cross, because they inherit: `color`, and custom properties. So a widget in a shadow root keeps its own light-theme colour classes on our black ground and goes dark-on-dark — unherd.com's CoEditor comments (`<div id=my-comments><template shadowrootmode=open>`) rendered every body at `#0a0a0a`, while author names survived because they have no colour class and inherit our yellow through the host. `ui: design tokens` is the answer and the only style that can reach inside one: Tailwind v4 declares its tokens on `:root`, `:root` inside a shadow stylesheet matches **nothing**, so the value the widget reads is the document's — set them on `html` and they land in the sealed tree. Only tokens used **alone** are moved (`--foreground`, `--muted-foreground`, the surfaces their ink sits on, the line colours); `--primary`/`--secondary`/`--accent`/`--destructive` travel with their own `-foreground` partner, a pair the site already made legible, and moving half of one is how you break a blue button. A hard-coded arbitrary value (CoEditor's `Reply` is `#6a7282` written into the class name) has no route in at all | `tools/make-default-styles.py` |
| ⚠ Never force a font on a `::before`/`::after` | Work out what the pseudo form of the sans blanket could ever *do* and it comes out a pure loss. `font-family` inherits, and a pseudo inherits from its originating element, so wherever the page declares no font on the pseudo it already has whatever we gave the element — Arial when that is prose, the icon face when the element is exempt. The rule therefore changes exactly one thing: it overrides a font the page put **on the pseudo itself** — and that is one idiom and one only, an icon font, whose glyph lives in the Private Use Area and exists in no other face. Forced to Arial the codepoint maps nowhere and Gecko draws the `.notdef` hex box: a video player's transport bar came out as five little boxes reading `E605`, `E60B`, `E606`, `E603`, `E601` where play, mute, quality, picture-in-picture and fullscreen belong. Nothing in `ICONS` could have caught them — the glyph is drawn on the `::before` of the control itself and the class names say `vjs-play-control`, nothing about icons — and no name list ever will, since which element carries an icon font is a fact about the page's *stylesheet*, not its markup. So the blanket simply stops at the element, which costs nothing anywhere and needs no `:not()`. The **element** side of it has no structural handle at all: Video.js declares the font on `.vjs-play-progress`/`.vjs-volume-level` and draws the scrubber and volume knobs in a `::before` that inherits it, so `vjs-` earns a line on the sans blanket's own exclusion list on the same terms as `.fa` and `octicon` — kept out of `ICONS` proper, whose list also drives the `:empty` sweeps and `ui: full-width` | `tools/make-default-styles.py` |
| ⚠ A shut drawer opens under `width: auto` — and takes the picture beside it | The most invasive rule in the library met the idiom that punishes it. A page that keeps a panel in the DOM at `width: 0` with `overflow: hidden` — a transcript drawer beside a podcast player, an off-canvas menu, anything that slides — is saying the panel is *closed*; `ui: full-width` releasing its width sizes it to the content it was hiding. On its own that would be an odd wide box, but such a drawer is nearly always `flex: none` beside a `flex: auto; min-width: 0` stage, so the space does not come out of the window: it comes out of the box next to it. And a stage frames its picture with an absolutely-positioned child, so it has **no intrinsic width of its own to defend with** and gives up everything — the `<video>` collapsed to 0 px wide and what remained was the player shell's own black 16:9 band, so every post on the newsletter host this style is allowlisted for rendered as a black rectangle under the header. `bg all` was not involved; the same collapse happens with the colour styles off. The repair splits the rule, and the split is the whole argument: lifting a **`max-width`** can only let a box grow, so that half stays global, while **`width`** is the half that can shrink one to nothing, so it stops at a box that *follows* a box framing media. Only DOM order after the frame — a drawer is appended, not prepended, and the mirrored arm would spare everything merely preceding a player, which on a flat page is most of it (the fixture's own column pinned by `width: 300px` is one). `img`/`picture` stay out: an image carries its own intrinsic width and cannot collapse. Note the syntax trap that cost a draft — `:has()` may not nest inside `:has()`, and `:not()` takes a **non-forgiving** list, so `:has(~ *:has(video))` silently dropped the entire rule and the fix appeared to work because nothing applied | `tools/make-default-styles.py` |
| ⚠ A value bar is empty because its content is its geometry | A volume slider, a scrubber, a progress bar and a level meter are one idiom: a track, and inside it a filled part whose width — or height, or `scaleX` — **is** the number. That part holds no text and no child, because it needs none, which is precisely the shape the `:empty` sweep in `ui: overlays` exists to neutralise on the premise that "an element with no content has nothing of its own to make legible". Here the premise is simply wrong. The sweep wiped the level's white, `bg all` and `bg div` painted the track black, and a volume slider that opens on hover came out as a black rectangle carrying no reading at all. So the **filled part** is given yellow ink of its own and the track is left black — the boundary between the two is the number back, and colouring the track as well would risk a grey box wherever a name matched something that is not a bar. The name is the only handle, as with `ICONS` and `ART`: a hashed class keeps its readable prefix (`volumeLevel-…`, `progress-…`) and Video.js spells it out (`vjs-volume-level`, `vjs-play-progress`); matched on the element **or its parent**, since a generic `<div class=fill>` inside `<div class=progress>` is as common as a named level. `range` and `track` are deliberately absent — they would catch *orange*, *tracking* and *soundtrack*. The doubled `#sk-never` guard is load-bearing: the sweep sits near (1,4,2) and no number of class terms would clear it. And the same list had to be added to `ui: full-width`'s width release for a second, sharper reason — a bar's width is its reading, and our `!important` beats the page's non-important `:hover` rule however specific that is, so the slider could never open again: it sat pinned at the content width of an empty div, which is nothing | `tools/make-default-styles.py` |
| ⚠ A whole-card click target is an invisible sheet | The card idiom every product grid, article teaser and video tile is built from: one `<a>` laid across the tile at `position: absolute; inset: 0; font-size: 0; color: transparent; background-color: transparent`, carrying the accessible name and drawing nothing. Every clause of that says the same thing — it is a hit area — and `bg all` paints it at (1,0,0) into an opaque sheet at the top of the card's stack. A bookshop's search results came out as rows holding a heart and a star rating and nothing else, the cover, author, title, format and price all behind it. Neither handle `ui: overlays` had could reach it: the class reads `element-link-toplevel`, a fact about the DOM rather than about painting, so no name list touches it; and it is **not** `:empty`, the accessible name being a text node with a data element beside it — links are out of that sweep anyway, deliberately, because an empty link is a wordmark. The structure is the handle: a link that holds **no picture of its own** and lies **beside one**. Both directions of the sibling axis, since the overlay is written before the content as often as after it, and spelled flat — `:has()` may not nest inside `:has()`. Greedy, and here nearly free: it also reaches the ordinary title link inside a tile (21 of them on the alza fixture), and unpainting a text link costs nothing when `bg all` has already blackened every ancestor. What it would cost is a pill link with a light ground of its own next to a picture; the ones naming themselves buttons are still painted by `ui: controls` at (2,1,1) | `tools/make-default-styles.py` |
| Specificity ladder in those styles | `:not(#sk-never)` — an id matching nothing, worth (1,0,0). An `!important` only beats another `!important` by specificity, so a bare `*` rule loses to any page `.card { background: #fff !important }`; that is why white cards and coloured buttons survived 2.4.10.3. Layers: (1,0,0) blankets, (1,0,1) element groups, (1,1,x) UI affordances. Typography stays at upstream weights on purpose | `tools/make-default-styles.py` |
| House theme for our own windows | black ground, yellow text, 16px base (upstream: 12px), cyan as the interactive accent, plus a legible palette for CodeMirror's `default` theme | `src/css/fork-theme.css`, imported by `src/js/dom-init.js` after both of upstream's globals. Everything hangs off `#stylus`, the id every page carries on `<html>`, because the per-page stylesheets load later and would win a `:root` tie. Preview: `tools/preview-ui-theme.py` |
| Upstream pref defaults we move | `popup.enabledFirst` → `false` (on, it re-sorts the popup whenever a style is disabled and so moves the digit positions the preinstalled library relies on). `show-badge` → `false` (the applied-count on the toolbar icon is noise once the library is global — every page shows the same number; upstream already ships the Options checkbox, only the default moves). Only non-default prefs are persisted, so both reach existing profiles too | `src/js/prefs.js` |

**`tools/fork.js` is the identity layer** — put new fork-wide constants and build-time rewrites there
rather than scattering edits, so the diff stays small and replays cleanly.

**`src/_locales/` must stay byte-identical to upstream.** Upstream re-pulls all 35 locales from
Transifex most weeks; renaming inside those files would conflict across 35 files at every sync. The
rename happens in `brandLocale` against an explicit key allowlist instead. To brand a newly-added
string, add its key to `BRANDED_KEYS` — and never add `optionsAdvancedExposeIframes*`, whose
"stylus" is the CSS attribute.

## Versioning — no `+NNN` in this repo

**One version string everywhere**: `<upstream version>.<our build number>`, e.g. `2.4.10.1`.

Firefox and AMO accept nothing else in a manifest — one to four plain dot-separated integers, no zero
padding, no build metadata. So this fork deliberately **does not** use the family's `+NNN` form, and
the counter is **never zero-padded**. The same string is the manifest version, the git tag, the
release title and the `.xpi` filename, so they can never disagree.

- Upstream's own version literal in `src/manifest.json` / `package.json` is **never hand-edited** — a
  rebase brings the new one in, and `tools/fork.js` appends our counter at build time.
- `BUILD_NUMBER` lives in `fork.properties`, is bumped by every build, and is **reset to 1** by
  `/upstream-new-version`. So `2.4.10.3` reads as "our 3rd build on upstream's 2.4.10".
- Output: `~/tmp/shiroikuma-kako-stylus_<version>.xpi`.

## Building

Needs **Node ≥ 24** and **pnpm**. The system `node` is 18, so every build must select 24 first:

```bash
. ~/.nvm/nvm.sh && nvm use 24
pnpm i                                  # once, or after a dependency change
node tools/build-fork.mjs               # unsigned: build -> ~/tmp/*.xpi, bump BUILD_NUMBER
node tools/build-fork.mjs --sign        # release only: AMO-signed .xpi (see below)
pnpm build-firefox                      # webpack only -> dist-firefox-mv2/
```

**Iterate unsigned.** 白い熊 火狐 desktop is built with `MOZ_REQUIRE_SIGNING` unset, so it installs
unsigned builds directly — load `dist-firefox-mv2/` via `about:debugging`. Sign only at release:
every signing run is an AMO round-trip and burns a version number AMO will never accept again.

## Signing

We sign through **addons.mozilla.org**, `--channel=unlisted`: Mozilla signs the `.xpi` and it installs
in any Firefox, including stock release builds, without being published or reviewed.

- Credentials are **per AMO account and shared by every extension fork** — `amo.properties`
  (`AMO_JWT_ISSUER` / `AMO_JWT_SECRET`), gitignored, mirroring `keystore.properties` in the Android
  forks. Master record: `~/〇/[666] 私資料/[666][27] 暗号/firefox-amo-api-keys.org`, which also holds
  the "Extension IDs we own" table.
- **Never generate a new key pair** — it invalidates the existing one for every other extension.
- **Never echo the credentials** into the chat, a log, or a process listing. `build-fork.mjs` passes
  them via the environment for exactly that reason.
- Bump the version on every upload; AMO rejects a version it has already seen.

## Icon

Yellow `#FFFF00` on black, **traced** from upstream's own `src/icon/128.png` with potrace — nothing
freehand, so it still reads as the same extension. `graphics/icon.svg` holds the two recovered
outlines (`id="silhouette"`, `id="interior"`); filling the silhouette with ink and laying the interior
over it in tile colour reproduces upstream's construction, with the letter falling out as a hole.

`python3 graphics/make-icons.py` regenerates all 26 PNGs plus `graphics/icon-512.png`. Needs
`rsvg-convert` (librsvg2-bin). Upstream's state model is kept one-for-one — `''` applied, `w` none on
this page, `x` all disabled, and the `light/` set for light toolbars — except that upstream's red `x`
becomes a dimmed `#666600`, since the house palette has no third colour.

## Changelog

Upstream ships **no `CHANGELOG.md`** — its release notes live only on GitHub Releases
(`gh release view <tag> -R openstyles/stylus`). Ours is therefore the whole file, in the
`/publish-version` shape: our releases newest-first, each naming the upstream release it is built on,
with the upstream notes for that release folded in.

## Open threads

One thing is still unfinished — the wiki — and it needs 白い熊's hand, not code. The section
below it records where signing and releasing stand.

### The wiki is not initialized

The extension's four Help links — the editor's **Writing-styles**, **Writing-UserCSS** and
**Applying-styles-to-specific-sites** (anchored at `#advanced-matching-with-regular-expressions`),
and the popup's **Popup** — point at this repository's wiki, which **does not exist yet**, so they
404. GitHub creates a repo's wiki git remote only after the first page is saved through the web UI;
there is no API for it and `git push` to `…​.wiki.git` fails until then.

**Five pages are already written and staged in the gitignored `.scratch/wiki/`** — `Home` plus one
per link, each describing the topic for this fork and pointing at upstream's page for the full text.
Once 白い熊 has created any first page at
<https://github.com/ShiroiKuma0/shiroikuma-kako-stylus/wiki>, push them:

```bash
git clone git@github.com:ShiroiKuma0/shiroikuma-kako-stylus.wiki.git /tmp/skwiki
cp .scratch/wiki/*.md /tmp/skwiki/ && cd /tmp/skwiki && git add -A && git commit && git push
```

### Signed and released

`stylus@shiroikuma` went through AMO on **2026-08-19** and the ID is now permanent. Two releases are
published — `2.4.10.11` and `2.4.10.24` — each a Mozilla-signed unlisted `.xpi` attached to a GitHub
release, with the repo's default branch on `custom`. Every signed build is delivered to the phone at
`/sdcard/tmp/` as a matter of course; see `.claude/skills/build-xpi`.

The "First signed" column in `~/〇/[666] 私資料/[666][27] 暗号/firefox-amo-api-keys.org` may still
read `pending` — that file is outside this repo and has not been updated.

## HARD RULES

- **Never `git push` without 白い熊's explicit go-ahead.** Build, let them test, and push only on
  "Push". Rebasing rewrites `custom`, so publishing after a sync is
  `git push --force-with-lease origin custom`; `master` is a plain fast-forward.
- **Never `git commit --amend` on published history**, and never force-push `master`.
- **No Claude/Anthropic attribution** in commits, PRs, the README, the changelog or release notes.
  End commit messages at the last line of the body. (Global rule: `~/.claude/CLAUDE.md`.)
- **`~/git` is outside the sandbox's write allowlist.** Reads work sandboxed; every write, build and
  git command in this repo needs `dangerouslyDisableSandbox: true`. A sandboxed write fails with
  `読み込み専用ファイルシステムです`.
- Keep the fork a **small, legible layer**: prefer new files and `tools/fork.js` over edits to
  upstream's, so each new release replays cleanly.
