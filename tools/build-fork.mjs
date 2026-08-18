#!/usr/bin/env node
/**
 * 白い熊 Stylus — build the fork's Firefox add-on.
 *
 *   node tools/build-fork.mjs            unsigned build, for iterating
 *   node tools/build-fork.mjs --sign     upload to AMO and fetch the signed .xpi (release only)
 *
 * Either way the package lands in ~/tmp as `shiroikuma-kako-stylus_<version>.xpi`, and
 * BUILD_NUMBER in fork.properties is bumped afterwards so the next build gets a fresh version.
 *
 * Do NOT sign while iterating: 白い熊 火狐 is built with MOZ_REQUIRE_SIGNING unset and installs
 * unsigned builds directly, whereas every signing run costs an AMO round-trip and burns a
 * version number that AMO will never accept again.
 */

import {execFileSync} from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
import {fileURLToPath} from 'url';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const DIST = path.join(ROOT, 'dist-firefox-mv2');
const ARTIFACTS = path.join(ROOT, 'web-ext-artifacts');
const OUT_DIR = path.join(os.homedir(), 'tmp');
const PROPS = path.join(ROOT, 'fork.properties');
const SIGN = process.argv.includes('--sign');

const die = msg => {
  console.error('\n' + msg + '\n');
  process.exit(1);
};

if (+process.versions.node.split('.')[0] < 24) {
  die(`Node ${process.versions.node} is too old — upstream needs >= 24.\n` +
    'Run:  . ~/.nvm/nvm.sh && nvm use 24');
}

const props = fs.readFileSync(PROPS, 'utf8');
const build = Number(props.match(/^BUILD_NUMBER\s*=\s*(\d+)\s*$/m)?.[1]);
if (!Number.isInteger(build) || build < 1) {
  die('fork.properties: BUILD_NUMBER must be a positive integer');
}

const upstream = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/manifest.json'), 'utf8')).version;
const version = `${upstream}.${build}`;
const run = (cmd, args, opts) =>
  execFileSync(cmd, args, {cwd: ROOT, stdio: 'inherit', ...opts});

console.log(`\n=== 白い熊 Stylus ${version}  (upstream ${upstream}, build ${build}) ===\n`);

run('pnpm', ['build-firefox']);

const built = JSON.parse(fs.readFileSync(path.join(DIST, 'manifest.json'), 'utf8'));
if (built.version !== version) {
  die(`manifest says ${built.version} but this build is ${version} — fork.properties and the ` +
      'webpack manifest step disagree.');
}

fs.rmSync(ARTIFACTS, {recursive: true, force: true});
let packaged;

if (SIGN) {
  const amo = path.join(ROOT, 'amo.properties');
  if (!fs.existsSync(amo)) {
    die('amo.properties is missing. Copy AMO_JWT_ISSUER / AMO_JWT_SECRET into it from\n' +
        '~/〇/[666] 私資料/[666][27] 暗号/firefox-amo-api-keys.org — never generate a new pair.');
  }
  const cfg = Object.fromEntries(fs.readFileSync(amo, 'utf8')
    .split('\n').filter(l => l && !l.startsWith('#'))
    .map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
  // Credentials go through argv-free env so they never reach a log or a process listing.
  run('web-ext', [
    'sign', '--channel=unlisted', `--source-dir=${DIST}`, `--artifacts-dir=${ARTIFACTS}`,
  ], {
    env: {
      ...process.env,
      WEB_EXT_API_KEY: cfg.AMO_JWT_ISSUER,
      WEB_EXT_API_SECRET: cfg.AMO_JWT_SECRET,
    },
  });
  packaged = fs.readdirSync(ARTIFACTS).find(f => f.endsWith('.xpi'));
} else {
  run('web-ext', [
    'build', `--source-dir=${DIST}`, `--artifacts-dir=${ARTIFACTS}`, '--overwrite-dest',
  ]);
  packaged = fs.readdirSync(ARTIFACTS).find(f => f.endsWith('.zip') || f.endsWith('.xpi'));
}
if (!packaged) die(`web-ext produced nothing in ${ARTIFACTS}`);

fs.mkdirSync(OUT_DIR, {recursive: true});
const out = path.join(OUT_DIR, `shiroikuma-kako-stylus_${version}.xpi`);
fs.copyFileSync(path.join(ARTIFACTS, packaged), out);

fs.writeFileSync(PROPS, props.replace(/^BUILD_NUMBER\s*=\s*\d+\s*$/m, `BUILD_NUMBER=${build + 1}`));

console.log(`\n${SIGN ? 'SIGNED' : 'unsigned'} build ready:\n  ${out}\n` +
            `fork.properties bumped to BUILD_NUMBER=${build + 1}\n`);
