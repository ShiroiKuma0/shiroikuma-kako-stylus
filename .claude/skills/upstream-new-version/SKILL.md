---
name: upstream-new-version
description: Bring 白い熊 Stylus onto a NEW upstream Stylus release (openstyles/stylus) and rebuild. Checks upstream for a newer release tag, ALWAYS presents a proceed-gated tabular description of what the new upstream version introduces BEFORE any fast-forwarding or rebasing, then — only after 白い熊 says proceed — fast-forwards the `master` mirror, rebases our `custom` stack onto the new release tag, resets the build counter, folds upstream's release notes into CHANGELOG.md, verifies every customization survived, and builds the new .1. Use when 白い熊 runs /upstream-new-version, says a new Stylus/upstream version is out, or asks to update/sync/bump the fork to upstream, rebase onto upstream, or rebase-and-rebuild the fork.
---

# Sync 白い熊 Stylus onto a new upstream Stylus release

Upstream is [openstyles/stylus](https://github.com/openstyles/stylus), the `upstream` remote (fetch
only — its push URL is deliberately `DISABLED_upstream_is_fetch_only`). Read `CLAUDE.md` first; this
skill assumes its fork model, the three-senses-of-"Stylus" table, and the versioning rules.

> **Never `git push` unprompted.** The rebase and the build are this skill's job; **landing and
> pushing are not**. Stop after the build and wait for 白い熊 to test and say **"Push"**. Because the
> rebase rewrites `custom`, publishing it is `git push --force-with-lease origin custom`; `master` is
> a plain fast-forward.
>
> **`~/git` is outside the sandbox's write allowlist** — every git, build and write command here
> needs `dangerouslyDisableSandbox: true`.

## 1. Preflight

```bash
cd ~/git/shiroikuma-kako-stylus
git status --porcelain          # must be empty — never reset --hard over uncommitted work
git branch --show-current       # note it; end back on custom
git fetch upstream --tags
git fetch origin
```

`amo.properties`, `node_modules/`, `dist-*/` and `web-ext-artifacts/` are gitignored, so a clean tree
means clean.

## 2. Detect the new release

Upstream tags releases `vX.Y.Z` on `master`. Take upstream's version from **upstream's own refs**,
never from a bare `git tag` listing:

```bash
gh release view -R openstyles/stylus --json tagName,publishedAt,body
git for-each-ref --sort=creatordate --format='%(creatordate:short) %(refname:short)' \
  'refs/tags/v*' | tail -5
```

**Our current base** is the upstream version literal in `src/manifest.json` (e.g. `2.4.10` → tag
`v2.4.10`) — never `fork.properties`, which only holds our counter. If the newest upstream tag is not
newer than our base, report "already on the latest upstream release (vX.Y.Z), nothing to do" and
**stop**. Syncing is not a scheduled chore.

## 3. ⛔ GATE — describe what the new version brings, then wait

**This gate is mandatory and comes before any branch is touched.** Never fast-forward, rebase or
build before 白い熊 has said proceed.

Gather the substance from upstream itself — the release notes of **every** release between our base
and the new one (not just the newest), plus the commit range when the notes are thin:

```bash
gh release list -R openstyles/stylus -L 20            # find every release since our base
gh release view <tag> -R openstyles/stylus --json body -q .body   # for each one
git log --oneline v<OLD>..v<NEW>
```

Then present a **table**, one row per user-visible change, newest release first:

| Release | Change | What it means for us |
| --- | --- | --- |
| v2.5.0 | *(concrete feature, named — never "various improvements")* | *(does it touch anything we patch? any conflict expected?)* |

Follow the table with:

- old base `v<OLD>` → new release `v<NEW>` and its date;
- **the stack size, captured now**: `OLD_COUNT=$(git rev-list --count v<OLD>..custom)` — step 7
  compares against it to prove no commit was silently dropped;
- anything in the range that touches our customization sites (`src/manifest*.json`, `src/icon/`,
  `tools/webpack.config.js`, `src/manage.html`, `src/options.html`, `src/js/dom-error.js`,
  `package.json`) — those are where conflicts will land;
- **whether upstream renamed or moved a `BRANDED_KEYS` message**, which would silently drop a rename;
- the plan: FF `master`, back up `custom`, rebase onto `v<NEW>`, reset the counter, rebuild.

Ask for the go-ahead with `AskUserQuestion`. Proceed only on a clear yes.

## 4. Fast-forward the mirror and back up the stack

```bash
git checkout master && git merge --ff-only upstream/master
git branch custom-pre-v<NEW> custom      # e.g. custom-pre-v2.5.0
```

If `master` cannot fast-forward, upstream rewrote history — **stop and discuss**.

## 5. Rebase `custom` onto the new release

```bash
git checkout custom
git rebase --onto v<NEW> v<OLD> custom
```

Conflict-prone files, in order of likelihood: `tools/webpack.config.js` (our three insertions),
`src/manifest.json`, `package.json`, `src/manage.html`, `src/js/dom-error.js`.

- **Small** conflicts (context drift, an obvious re-application of a known edit) → resolve inline and
  `git rebase --continue`.
- **Significant** conflicts (upstream refactored, renamed or deleted a file we patch; the shape of an
  edit site changed; many commits conflict) → **stop, do not improvise.** Bring 白い熊 a concrete
  plan via `AskUserQuestion` (resolve together / re-implement on the new base / defer) and act on
  their choice. `git rebase --abort` restores `custom`; `master` stays fast-forwarded, which is
  harmless.

Take upstream's side for anything in `src/_locales/` — our diff there must stay **empty**.

## 6. Reset the build counter

`fork.properties` → `BUILD_NUMBER=1`, so the first build on the new upstream line reads `.1`.

**Never hand-edit the upstream version literal** in `src/manifest.json` or `package.json`; the rebase
brings the new one in, and `tools/fork.js` appends our counter at build time.

## 7. Verify our customizations survived

| What | Expected | Where |
| --- | --- | --- |
| Add-on ID | `stylus@shiroikuma` | `src/manifest-mv2-firefox.json` |
| Android compat | `gecko_android.strict_min_version` present | same file |
| Name / tooltip / homepage | 白い熊 Stylus, our repo | `src/manifest.json` |
| Version plumbing | `base.version += '.' + fork.BUILD` in `makeManifest` | `tools/webpack.config.js` |
| Locale rename | `transform: fork.brandLocale` on the `_locales/**` pattern | `tools/webpack.config.js` |
| Identity links | our repo | `src/manage.html`, `src/js/dom-error.js`, `src/background/usercss-template.js` |
| Icon | ours, 26 assets | `src/icon/` — `python3 graphics/make-icons.py` must produce no diff |
| `_locales/` | **byte-identical to upstream** | `git diff v<NEW>..custom -- src/_locales` is empty |

Also confirm nothing was dropped: `git rev-list --count v<NEW>..custom` equals `OLD_COUNT` from step
3, and skim `git log --oneline v<NEW>..custom`.

Then re-check the three senses of "Stylus" (CLAUDE.md): if upstream added a new user-visible product
string, add its key to `BRANDED_KEYS` in `tools/fork.js` — and never add a page-facing identifier.

## 8. Fold the upstream release notes into CHANGELOG.md

Upstream ships **no `CHANGELOG.md`**; its notes live only on GitHub Releases. Ours is the whole file.
Add a section for the new upstream release with its notes (from step 3) beneath our own entry for the
build, newest-first, each entry naming the upstream release it is built on. Our blocks stay at the
top of the file. See the `/publish-version` skill for the exact shape.

## 9. Build the new `.1`

```bash
. ~/.nvm/nvm.sh && nvm use 24
pnpm i                          # upstream bumps dependencies often — do this every sync
pnpm test                       # eslint + csslint must pass
node tools/build-fork.mjs       # -> ~/tmp/shiroikuma-kako-stylus_<newver>.1.xpi
```

**Unsigned.** Signing is a release step (`--sign`), not a sync step — see the `build-xpi` skill.

## 10. Stop

Report what landed, hand over the `.xpi` path, and let 白い熊 test. Commit and push only on their
explicit **"Push"**.

---

**Commit convention — no Claude attribution.** Never add a `Co-Authored-By: Claude …` trailer nor a
"Generated with Claude Code" line to commits or PR bodies. End the message at the last line of the
body. (Global rule: `~/.claude/CLAUDE.md`.)
