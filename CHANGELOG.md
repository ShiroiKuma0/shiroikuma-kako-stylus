# Changelog

This file carries **both histories**: 白い熊 Stylus' releases and, folded into each one, the notes
for the upstream [Stylus](https://github.com/openstyles/stylus) release it is built on. Upstream
ships no changelog file of its own — its notes live only on GitHub Releases — so this file is
entirely ours to maintain, newest first.

## 白い熊 Stylus 2.4.10.1 — 2026-08-18

The first build of the fork, on upstream **v2.4.10**. A pure identity layer: no upstream behaviour is
patched, which keeps the diff small enough to replay cleanly onto each new release.

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
- The links panel, the crash reporter's issue search and report links, and the UserCSS template's
  `@namespace` all point at this repository. Upstream's Transifex link is dropped — this fork has no
  translation project of its own.
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
  bumps the counter; `--sign` produces an AMO-signed unlisted build for release.
- AMO credentials live in a gitignored `amo.properties`, mirroring `keystore.properties` in the
  Android forks.

### Upstream v2.4.10 (2026-08-08)

- editor: fix infinite loop when clicking "+" to add a new section
- editor: fix flicker on opening in MV2/Firefox
