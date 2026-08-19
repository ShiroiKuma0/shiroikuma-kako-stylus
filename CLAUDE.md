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

Three things are deliberately unfinished. None is blocking; all three need 白い熊's input.

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

### The Android install path is unsettled

Firefox for Android installs add-ons only from AMO or a **custom AMO collection**, and an
unlisted-signed `.xpi` cannot be put in a collection. Desktop is fine — 白い熊 火狐 takes the `.xpi`
directly. How the build reaches the phone is an open question: **ask, do not assume `adb push` does
anything useful there.**

### Nothing is signed or released yet

`stylus@shiroikuma` has never been through AMO — the "First signed" column in the key file's
"Extension IDs we own" table still reads `pending`. **The ID becomes permanent at the moment of the
first signing run**, so settle the Android question before signing. `2.4.10.1` exists only as an
unsigned build in `~/tmp`; no tag has been cut and no release published.

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
