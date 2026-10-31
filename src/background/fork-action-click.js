/**
 * shiroikuma fork: a click on the toolbar icon switches every style off, or back on.
 *
 * Upstream opens its menu on a click and keeps the boss key one level down, inside it. With the
 * preinstalled library applying everywhere, the boss key is the thing reached for most — a page
 * that reads wrong is checked against its own colours in one click, and the same click puts them
 * back. So the click is the switch, and the menu moves to where a menu is expected:
 *
 * - **Right-click** shows the browser's own context menu on the icon, and its first entry opens
 *   the menu. A WebExtension cannot replace that native menu or learn of a right-click any other
 *   way, so one entry in it is as close as the platform allows.
 * - **Middle-click** opens the menu directly — `onClicked` reports the button, and nothing else
 *   was using it.
 *
 * The icon already shows the state: `disableAll` draws the dimmed `x` set.
 *
 * On Android the action is an entry in the browser's own menu, which stock Firefox lets you only
 * tap — no right-click, no middle-click — so there a tap goes on opening the menu, or it could not
 * be reached at all. 白い熊 火狐 adds a long-press to that entry which opens the manifest's
 * `default_popup` whatever `setPopup` says, so there the tap is the switch as on desktop and the
 * long-press is the menu. `inKako()` tells the two apart.
 *
 * It stands aside while upstream's `popup.sidePanel` option is on, which takes the same click to
 * open the menu in the sidebar.
 */
import {kDisableAll} from '@/js/consts';
import * as prefs from '@/js/prefs';
import {FIREFOX, MOBILE} from '@/js/ua';
import {browserAction, ignoreChromeError} from '@/js/util-webext';
import {bgInit} from './common';

const MENU_ID = 'fork-open-menu';
const POPUP = 'popup.html';
const GECKO = (__.B_FIREFOX || __.B_ANY && FIREFOX) && !__.MV3 && browserAction;

if (GECKO && !MOBILE) {
  // ahead of upstream's initContextMenus, which runs after bgInit, so the entry comes first
  bgInit.push(() => {
    chrome.contextMenus?.create({
      id: MENU_ID,
      title: 'Open the menu',
      contexts: ['browser_action'],
    }, ignoreChromeError);
  });
  chrome.contextMenus?.onClicked.addListener(info => {
    if (info.menuItemId === MENU_ID) openMenu();
  });
  takeTheClick();
} else if (GECKO) {
  inKako().then(yes => yes && takeTheClick());
}

function takeTheClick() {
  prefs.subscribe('popup.sidePanel', (key, sidePanel) => {
    browserAction.onClicked.removeListener(onClick);
    if (!sidePanel) {
      browserAction.setPopup({popup: ''});
      browserAction.onClicked.addListener(onClick);
    }
  }, true);
}

/** 白い熊 火狐 adds `fork` to getBrowserInfo() (from 157.0+004), and its presence also means a
 * long-press on the action opens the menu. Stock Firefox leaves it undefined. */
async function inKako() {
  try {
    return (await browser.runtime.getBrowserInfo()).fork === 'shiroikuma-kako';
  } catch {
    return false;
  }
}

/** @param {chrome.tabs.Tab} tab @param {{button?: number}} [info] */
function onClick(tab, info) {
  if (info?.button === 1) openMenu();
  else prefs.set(kDisableAll, !prefs.__values[kDisableAll]);
}

/** Both calls go out synchronously, inside the click that asked for them: openPopup needs the
 * user's gesture, and the two are delivered in order, so the popup is set before it is opened.
 * Clearing it again afterwards leaves the open menu alone and gives the next click back to us. */
function openMenu() {
  browserAction.setPopup({popup: POPUP});
  browserAction.openPopup()
    .catch(console.error)
    .finally(() => prefs.__values['popup.sidePanel'] || browserAction.setPopup({popup: ''}));
}
