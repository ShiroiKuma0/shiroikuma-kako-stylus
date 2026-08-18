#!/usr/bin/env python3
"""Generate 白い熊 Stylus' icon set.

The artwork is a trace of upstream Stylus' own icon. `graphics/icon.svg` holds two outlines
recovered by running potrace over upstream's `src/icon/128.png`: the silhouette (the rounded
tile, its two side tabs, and the S) and the tile interior (which carries the S as a hole).
Nothing is freehand — the fork stays recognisably the same extension, redrawn in the house
palette of pure yellow on black, the treatment `shiroikuma-kuchusen` gives its launcher icon.

Filling the silhouette with the INK colour and laying the interior over it in the TILE colour
reproduces upstream's own construction exactly: the border, the side tabs and the letter are
ink; everything the interior covers is tile.

    python3 graphics/make-icons.py

rewrites every PNG in `src/icon/`. Needs `rsvg-convert` (librsvg2-bin).
"""

import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
ICONS = REPO / "src" / "icon"

BLACK = "#000000"
YELLOW = "#FFFF00"
# The one tone that is not full-strength yellow: the "all styles disabled" state exists to look
# switched off. It stays on the yellow hue rather than introducing a third colour — upstream
# turns this state red, which the house palette has no room for.
DIM = "#666600"

# Upstream's own icon states, kept one for one:
#   ''  styles are applied here          'w'  no styles for this page (washed out)
#   'x' all styles disabled              light/  the same set for a light browser toolbar
#
# Upstream names them "<dir><size><state>.png", e.g. 32w.png, light/32x.png.
#
#          dir       state   ink     tile    opacity
STATES = [
    ("",       "",    YELLOW, BLACK,  1.0),
    ("",       "w",   YELLOW, BLACK,  0.5),
    ("",       "x",   DIM,    BLACK,  1.0),
    ("light/", "",    BLACK,  YELLOW, 1.0),
    ("light/", "w",   BLACK,  YELLOW, 0.5),
    ("light/", "x",   BLACK,  DIM,    1.0),
]

# what src/icon/ needs: the toolbar sizes in every state, plus the two plain store sizes
SIZES = [16, 19, 32, 38]
PLAIN = [48, 128]


def outlines():
    """The two traced path outlines, read back from the master SVG."""
    svg = (HERE / "icon.svg").read_text()
    found = dict(re.findall(r'id="(silhouette|interior)"\s+d="([^"]+)"', svg))
    if len(found) != 2:
        sys.exit("graphics/icon.svg: expected paths id=silhouette and id=interior")
    return found["silhouette"], found["interior"]


def svg(ink, tile, opacity):
    sil, interior = OUTLINES
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">\n'
        '  <g opacity="%g">\n'
        '    <path d="%s" fill="%s"/>\n'
        '    <path d="%s" fill="%s" fill-rule="evenodd"/>\n'
        '  </g>\n'
        '</svg>\n' % (opacity, sil, ink, interior, tile)
    )


def render(body, out, px):
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), "-o", str(out)],
                   input=body.encode(), check=True)


OUTLINES = outlines()


def main():
    n = 0
    for folder, state, ink, tile, opacity in STATES:
        body = svg(ink, tile, opacity)
        for px in SIZES + (PLAIN if not folder and not state else []):
            render(body, ICONS / ("%s%d%s.png" % (folder, px, state)), px)
            n += 1
    print("wrote %d PNGs under %s" % (n, ICONS))

    # a large flat preview for the README and for release pages
    render(svg(YELLOW, BLACK, 1.0), HERE / "icon-512.png", 512)
    print("wrote graphics/icon-512.png")


if __name__ == "__main__":
    try:
        subprocess.run(["rsvg-convert", "--version"], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        sys.exit("rsvg-convert not found — install librsvg2-bin")
    main()
