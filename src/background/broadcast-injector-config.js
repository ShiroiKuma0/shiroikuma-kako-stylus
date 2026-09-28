import {pDisableAll, pDisableSites, pExposeIframes, pKeepAlive, pStyleViaASS} from '@/js/consts';
import * as prefs from '@/js/prefs';
import {broadcast} from './broadcast';
import {bgBusy, onSchemeChange} from './common';

let cfg;
let sentCfg = {};
const INJECTOR_CONFIG_MAP = {
  [pExposeIframes]: 'top',
  [pDisableAll]: 'off',
  // shiroikuma fork: the per-site list answers the same question, so it sends the same key
  [pDisableSites]: 'off',
  [pKeepAlive]: 'wake',
  [pStyleViaASS]: 'ass',
};

bgBusy.then(() => {
  prefs.subscribe(Object.keys(INJECTOR_CONFIG_MAP), broadcastInjectorConfig);
});
onSchemeChange.add(broadcastInjectorConfig.bind(null, 'dark'));

export default function broadcastInjectorConfig(key, val) {
  /* shiroikuma fork: a change to the host list carries the GLOBAL answer here — doBroadcast is
     where the per-tab one is worked out, because only there is a tab's url in hand. And it must
     skip the dedupe below: that compares the value, and the value is exactly what has NOT
     changed. Dropping it would leave every tab on the site still styled. */
  const perSite = key === pDisableSites;
  key = INJECTOR_CONFIG_MAP[key] || key;
  if (key === pKeepAlive)
    val = val >= 0;
  if (perSite)
    val = prefs.__values[pDisableAll];
  if (!cfg) {
    cfg = {};
    cfg[key] = val;
    setTimeout(throttle);
  } else if (!perSite && sentCfg[key] === val) {
    delete cfg[key];
  } else {
    cfg[key] = val;
  }
}

function throttle() {
  if (Object.keys(cfg).length)
    broadcast(null, cfg);
  sentCfg = cfg;
  cfg = null;
}
