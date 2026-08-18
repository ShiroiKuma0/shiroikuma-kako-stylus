'use strict';

/**
 * 白い熊 Stylus — the fork's identity layer.
 *
 * Everything that renames upstream or re-points its links lives here so the diff against
 * openstyles/stylus stays a thin, legible layer that replays onto each new release.
 *
 * ⚠ "Stylus" is three different words in this tree and only one of them is ours to rename:
 * the product (ours), the CSS preprocessor language (upstream's dependency), and the
 * page-facing identifiers that user styles and the galleries match on. See CLAUDE.md.
 * Nothing in this file touches anything but the product name.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.dirname(__dirname.replaceAll('\\', '/')) + '/';

const NAME = '白い熊 Stylus';
const REPO = 'https://github.com/ShiroiKuma0/shiroikuma-kako-stylus';

/**
 * Our build counter, appended to upstream's version as a fourth component (2.4.10 -> 2.4.10.3).
 * Firefox and AMO accept nothing else there — 1 to 4 plain dot-separated integers, no zero
 * padding, no build metadata — so this fork carries no "+NNN" form anywhere.
 */
const BUILD = (() => {
  const txt = fs.readFileSync(ROOT + 'fork.properties', 'utf8');
  const n = Number(txt.match(/^BUILD_NUMBER\s*=\s*(\d+)\s*$/m)?.[1]);
  if (!Number.isInteger(n) || n < 1) {
    throw new Error('fork.properties: BUILD_NUMBER must be a positive integer');
  }
  return n;
})();

/**
 * Locale message keys whose text names the product. Upstream re-pulls `_locales/` from
 * Transifex most weeks, so renaming inside those files would conflict across 35 locales at
 * every sync; the rename happens at build time instead and our diff to `_locales/` stays empty.
 *
 * Deliberately absent: `optionsAdvancedExposeIframes` and its `…Note`. Their "stylus" is the
 * CSS attribute `html[stylus-iframe]` that user styles match on — page-facing protocol, not
 * branding. Renaming it would silently break every style using the iframe hook.
 */
const BRANDED_KEYS = [
  'dbError',
  'description',
  'optionTargetIconsNote',
  'optionsStylusThemes',
  'parseUsercssError',
  'publishRetry',
  'shortcutsNoteFF',
  'stylusUnavailableForURL',
  'syncErrorRelogin',
  'unreachableCSP',
  'unreachableFileHint',
  'unreachableOpera',
];

/** Every locale spells the product in Latin script, so one word-boundary match covers all 35. */
const RX_PRODUCT = /\bStylus\b/g;

/** CopyPlugin transform for `_locales/**`. */
function brandLocale(content) {
  const json = JSON.parse(content.toString());
  let hit = 0;
  for (const key of BRANDED_KEYS) {
    const entry = json[key];
    if (!entry || typeof entry.message !== 'string') continue;
    const renamed = entry.message.replace(RX_PRODUCT, NAME);
    if (renamed !== entry.message) {
      entry.message = renamed;
      hit++;
    }
  }
  return hit ? Buffer.from(JSON.stringify(json, null, 2)) : content;
}

module.exports = {BUILD, BRANDED_KEYS, NAME, REPO, brandLocale};
