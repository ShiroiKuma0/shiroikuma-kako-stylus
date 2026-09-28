/**
 * shiroikuma fork: the per-site master switch.
 *
 * Upstream has two scopes and nothing between them. `disableAll` is the boss key — every style,
 * every page, one switch — and `exclusions` are per style, so turning this library off on one site
 * would mean opening the menu twenty-eight times. What was missing is the middle: *not here*.
 *
 * So this is `disableAll` with a guest list. The pref is a plain newline-separated list of hosts,
 * which is why it is named `disableAll.sites` — upstream already spells a per-site qualifier that
 * way (`exposeIframes.sites`, `patchCsp.sites`), and reading it as "disableAll, on these" is
 * exactly what it does.
 *
 * HOSTS, not URL globs, and that is deliberate. The popup writes the entry with one click and has
 * no way to ask what the user meant, so the entry has to be the least surprising thing the click
 * could mean: the host in the address bar, and nothing else. A path-scoped rule would silently
 * leave the rest of the site styled, which is the opposite of what "turn it off here" says. The
 * one wildcard is a leading `*.`, which a hand edit in Options can add to cover the subdomains;
 * `*.example.com` means example.com and everything under it, not "anything ending in that".
 *
 * Shared between the background (which decides what to inject) and the popup (which draws the
 * button), so it lives in `@/js/` and imports nothing.
 */

/** @param {string} str @returns {string[]} lowercased, deduped, blank lines dropped */
export function parseSites(str) {
  return [...new Set((str || '').toLowerCase().split(/\s+/).filter(Boolean))];
}

/** The host a one-click toggle writes for a page, or '' when the page has none
 * (about:, file:, and our own pages, where "this site" means nothing).
 * @param {string} url @returns {string} */
export function hostOf(url) {
  try {
    const u = new URL(url);
    return /^(https?|ftps?):$/.test(u.protocol) ? u.hostname.toLowerCase() : '';
  } catch {
    return '';
  }
}

/** @param {string} host @param {string} entry @returns {boolean} */
function hostMatches(host, entry) {
  return entry.startsWith('*.')
    ? host === entry.slice(2) || host.endsWith(entry.slice(1))
    : host === entry;
}

/** @param {string|string[]} sites - the pref value, or an already-parsed list
 * @param {string} url @returns {boolean} */
export function isSiteOff(sites, url) {
  const host = hostOf(url);
  if (!host) return false;
  const list = Array.isArray(sites) ? sites : parseSites(sites);
  for (const entry of list) if (hostMatches(host, entry)) return true;
  return false;
}

/** Add or remove a host, keeping the rest of the list as the user wrote it. Removing also drops
 * a `*.parent` entry that was covering this host, since a click that says "style this site again"
 * cannot mean "and leave it off". @param {string} str @param {string} host @param {boolean} off
 * @returns {string} the new pref value */
export function toggleSite(str, host, off) {
  const list = parseSites(str).filter(entry => !hostMatches(host, entry));
  if (off) list.push(host);
  return list.join('\n');
}
