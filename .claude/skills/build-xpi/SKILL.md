---
name: build-xpi
description: Build 白い熊 Stylus (the Firefox MV2 add-on) into a .xpi in ~/tmp — unsigned for iterating, or AMO-signed with --sign at release. Handles the Node 24 / pnpm toolchain, the version stamping (upstream version + our build counter), the build counter bump, and the AMO credential handling. Use after any code change in this repo, or when 白い熊 says /build-xpi, "build it", "build the extension", "make an xpi", or asks for a signed build to publish.
---

# Build 白い熊 Stylus

Produces `~/tmp/shiroikuma-kako-stylus_<version>.xpi`. Read `CLAUDE.md` for the fork model and the
versioning rules; this skill is the mechanics.

> **`~/git` is outside the sandbox's write allowlist** — every command here needs
> `dangerouslyDisableSandbox: true`. A sandboxed write fails with `読み込み専用ファイルシステムです`.

## Toolchain

Upstream needs **Node ≥ 24** and **pnpm**; the system `node` is 18, so select 24 first — in *every*
shell, since shell state does not persist between calls:

```bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm use 24
```

`pnpm i` after a fresh clone, after `/upstream-new-version`, or whenever `pnpm-lock.yaml` moved.

## Iterating — build unsigned

```bash
cd ~/git/shiroikuma-kako-stylus
pnpm test                        # eslint + csslint; keep it green, upstream's max-len is 100
node tools/build-fork.mjs
```

That runs `pnpm build-firefox` into `dist-firefox-mv2/`, packages it with `web-ext build`, copies the
result to `~/tmp/shiroikuma-kako-stylus_<version>.xpi`, and **bumps `BUILD_NUMBER`** in
`fork.properties` for the next build.

**Do not sign while iterating.** 白い熊 火狐 desktop is built with `MOZ_REQUIRE_SIGNING` unset and
installs unsigned builds directly; loading `dist-firefox-mv2/` through `about:debugging` is faster
still. Every signing run is an AMO round-trip and burns a version number AMO will never accept again.

## Releasing — build signed

```bash
node tools/build-fork.mjs --sign
```

`web-ext sign --channel=unlisted`: Mozilla signs the `.xpi` and it installs in **any** Firefox,
including stock release builds, without being published or reviewed on AMO.

- Credentials come from the gitignored `amo.properties` (`AMO_JWT_ISSUER` / `AMO_JWT_SECRET`), passed
  through the environment so they never reach a log or a process listing. **Never echo them.**
- They are **per AMO account, shared by every extension fork**. Master record:
  `~/〇/[666] 私資料/[666][27] 暗号/firefox-amo-api-keys.org`. **Never generate a new pair** — it
  invalidates the existing one for every other extension at once.
- Our add-on ID `stylus@shiroikuma` is recorded in that file's "Extension IDs we own" table.
- **AMO rejects a version it has already seen**, so never re-sign the same number. The counter bump
  is automatic; just never reset it by hand outside `/upstream-new-version`.

Then hand off to `/publish-version`: tag `<version>` (no leading `v`), attach the signed `.xpi`,
refresh the README, and merge the changelog.

## Version stamping — how it works

One string everywhere: `<upstream version>.<BUILD_NUMBER>`, e.g. `2.4.10.3`. Firefox and AMO accept
only 1–4 plain dot-separated integers with no zero padding, so this fork carries **no `+NNN` form**.

- upstream's literal lives in `src/manifest.json` and is **never hand-edited**;
- `tools/fork.js` reads `fork.properties` and `makeManifest` appends the counter at build time;
- `build-fork.mjs` cross-checks the built manifest against what it expected and aborts on a mismatch.

## Delivery

The `.xpi` goes to `~/tmp/`. Desktop installs it directly. **Firefox for Android installs add-ons
only from AMO or a custom AMO collection**, and an unlisted-signed build cannot go into a collection —
so the Android install path is still an open question; ask 白い熊 rather than assuming `adb push`
will do anything useful.

### ⚠ Never delete an older build (hard rule)

Every `~/tmp/shiroikuma-kako-stylus_*.xpi` stays where it is. Do **not** remove, overwrite or tidy
away a previous version — not when a newer one supersedes it, not to "reduce confusion" at install
time, not because an earlier build turned out to be broken, and **not because 白い熊 asked you to
delete one once**. A one-off request to clear a specific file is exactly that: one file, that time.
It is never a standing licence to prune.

The build counter exists so versions accumulate: each `.xpi` is the only remaining record of the
source state that produced it, and once the tree has moved on it cannot be rebuilt. Keeping them is
what makes it possible to go back to a build that worked, or to compare two, when a change turns
out to have broken something.

Name the new build's full path in the handover and leave the rest alone.

## If the build breaks

- `Node <n> is too old` — the nvm line above was not run in *this* shell.
- `manifest says X but this build is Y` — `fork.properties` and the webpack manifest step disagree;
  check `tools/fork.js` survived the last rebase.
- eslint `max-len` / `indent` — upstream's config is strict; wrap at 100 columns.
- `web-ext produced nothing` — the webpack build failed earlier in the log; read up.

---

**No Claude attribution** in commits, PRs, README, changelog or release notes.
