# Changelog

This file carries **both histories**: 白い熊 Stylus' releases and, folded into each one, the notes
for the upstream [Stylus](https://github.com/openstyles/stylus) release it is built on. Upstream
ships no changelog file of its own — its notes live only on GitHub Releases — so this file is
entirely ours to maintain, newest first.

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
  documentation: `CLAUDE.md` still claimed nothing had ever been signed and that the add-on ID
  becomes permanent at the first signing run, so signing should wait. A session reading that would
  have refused to sign a release.

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
