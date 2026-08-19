<div align="center">

<img src="graphics/icon-512.png" width="128" alt="白い熊 Stylus">

# 白い熊 Stylus

**Restyle the web with your own CSS — in 白い熊 火狐, on the desktop and on Android.**

A personal fork of [Stylus](https://github.com/openstyles/stylus), the userstyle manager,
carrying its own add-on ID and its own black-and-yellow identity so it installs **alongside**
an unmodified Stylus rather than replacing it.

📥 **[Latest release](https://github.com/ShiroiKuma0/shiroikuma-kako-stylus/releases/latest)** —
a Mozilla-signed `.xpi` that installs in any Firefox.

</div>

## What it does

Inject your own CSS into any site, matched per URL, domain or regexp, each style switchable on
and off from the toolbar. A full CodeMirror editor with live Stylelint / CSSLint linting, one-click
installs from the style galleries, **UserCSS** styles with per-style configuration from any raw
URL, automatic style updates, and library sync to Dropbox, Google Drive, OneDrive or any WebDAV
server. No analytics, no tracking — upstream's founding principle, kept.

## What this fork changes

Two layers: an **identity layer**, so this build is its own add-on rather than a copy of somebody
else's, and a **reading layer** — a style library and a themed UI that arrive already set up. Both
are kept small and mostly additive, because the smaller the diff, the more cleanly it replays onto
each new upstream release.

### 📚 A reading library, preinstalled

A fresh profile arrives with **23 styles already installed** — no import, no setup. Ten of them are
a matrix: black background and yellow text, each split by selector group (`all`, `html/body`, `div`,
block containers, text elements) so that turning the yellow off for `div` **on one site** does not
lose it everywhere. They occupy popup positions 1–9 and 0, so tuning a site is a three-key gesture:
hold `Enter`, tap the digit, press `Shift-1`.

Alongside them: forced sans-serif and a tight line height, both with a carve-out that keeps icon
fonts working; monospace and a readable grey for code; cyan links that stay distinct from body text;
traced yellow pills for buttons and text fields; a visible focus ring; a grey ground behind
transparent artwork so neither dark nor light ink can vanish on a black page.

The library is **synced to every build**, matching by name and replacing only the CSS — your
per-site exclusions, and which styles you have switched off, survive an update untouched.

### 🖤 The extension's own windows, in the house palette

The popup, the manager, the options page and the editor are black-and-yellow too, at a larger base
font, with CodeMirror's syntax colours restated so they are legible on black.

### 🆔 Its own add-on identity

`stylus@shiroikuma`, permanently ours. AMO will not sign an ID registered to somebody else, add-on
updates are keyed to the ID forever, and owning it is what lets this build sit beside an unmodified
Stylus in the same profile.

### 🎨 A traced black-and-yellow icon

Upstream's own icon, run through potrace and redrawn in the house palette — pure yellow `#FFFF00`
on black. Nothing is freehand, so it still reads as the same extension. All 26 assets, including
upstream's washed-out and all-disabled toolbar states and the whole `light/` set for light
toolbars, regenerate from one master SVG via `graphics/make-icons.py`.

### 🤖 Declared for Firefox on Android

Upstream ships no `gecko_android` key at all; this fork declares one, so the build is a first-class
Android add-on rather than a desktop-only one.

### 🔗 Our name and our links throughout

The extension name, the browser-action tooltip, the editor's window title, the options page title,
the links panel and the crash reporter all carry this fork's name and point at this repository.
Localized strings are renamed **at build time** from an explicit key allowlist, so `src/_locales/`
stays byte-identical to upstream and its weekly Transifex churn never conflicts with us.

### 🔢 A version that says which upstream it is

`<upstream version>.<our build>` — `2.4.10.1` is our first build on upstream's 2.4.10.

## Building

Needs **Node ≥ 24** and **pnpm**.

```bash
pnpm i
pnpm build-firefox        # -> dist-firefox-mv2/
node tools/build-fork.mjs # bump the counter, build, and drop the .xpi in ~/tmp
```

Load `dist-firefox-mv2/` through `about:debugging` while iterating — 白い熊 火狐 is built with
`MOZ_REQUIRE_SIGNING` unset, so it takes unsigned extensions directly and no AMO round-trip is
needed until release.

## Credits and licence

Built on [Stylus](https://github.com/openstyles/stylus) by the Stylus Team, which is itself the
community's continuation of Jason Barnabe's original Stylish after that name was sold to an
analytics company. This fork's [wiki](https://github.com/ShiroiKuma0/shiroikuma-kako-stylus/wiki)
carries the style-writing reference, which upstream's own wiki documents in full.

### Licence: [GPLv3](./LICENSE)

* Copyright &copy; 2026 白い熊, for the changes in this fork.
* Copyright &copy; 2017-2025 [Stylus Team](https://github.com/openstyles/stylus/graphs/contributors).
* Copyright &copy; 2005-2014 Jason Barnabe, for the ever diminishing parts of the original
  [Stylish](https://github.com/stylish-userstyles/stylish/).
* Licences of modified external libraries: [vendor-overwrites](./src/vendor-overwrites).
