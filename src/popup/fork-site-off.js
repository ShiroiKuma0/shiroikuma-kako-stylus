/**
 * shiroikuma fork: the popup's one-click "not on this site".
 *
 * It sits next to the `+` that writes a style for the same host, because it is the other half of
 * the same thought: that button says *something else here*, this one says *nothing here*. One
 * click writes the host into `disableAll.sites` and the background stops injecting on it; one
 * click takes it out again. Nothing else on any other site moves.
 *
 * The state is drawn three ways, so it can never be a surprise: the button lights up, the popup
 * takes `html.site-disabled` (which strikes the style names through exactly as the boss key's
 * `all-disabled` does), and the toolbar icon wears the dimmed `x`. The list itself stays — what
 * WOULD apply here is worth seeing while it does not.
 *
 * The strings are English literals rather than locale keys on purpose: `src/_locales` is a byte
 * copy of upstream's, re-pulled from Transifex most weeks, and a key added there would conflict
 * across 35 files at every sync. Same reason the product name is hard-coded in `options.html`.
 */
import {pDisableSites} from '@/js/consts';
import {$rootCL} from '@/js/dom';
import {hostOf, isSiteOff, toggleSite} from '@/js/fork-site-off';
import * as prefs from '@/js/prefs';
import {tabUrl} from '.';

const OFF_TITLE = h => `Turn 白い熊 Stylus back on for ${h}`;
const ON_TITLE = h => `Turn 白い熊 Stylus off for ${h}\n` +
  'Only this site; everything else is untouched.';

let el, host;

/** `init()` in index.js re-enters on every port message, so the subscription is made once and
 * everything after that is a redraw. */
export function initSiteOff() {
  host = hostOf(tabUrl || '');
  if (el) return render();
  if (!(el = $id('fork-site-off'))) return;
  el.onclick = () => {
    if (!host) return;
    const val = prefs.__values[pDisableSites];
    prefs.set(pDisableSites, toggleSite(val, host, !isSiteOff(val, tabUrl)));
  };
  el.on('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      el.onclick();
    }
  });
  prefs.subscribe(pDisableSites, render, true);
}

function render() {
  if (!el) return;
  // about:, file:, our own pages — "this site" means nothing there, so there is nothing to offer
  el.hidden = !host;
  const off = !!host && isSiteOff(prefs.__values[pDisableSites], tabUrl);
  $rootCL.toggle('site-disabled', off);
  el.classList.toggle('site-off', off);
  el.setAttribute('aria-pressed', off);
  if (host) el.title = (off ? OFF_TITLE : ON_TITLE)(host);
}
