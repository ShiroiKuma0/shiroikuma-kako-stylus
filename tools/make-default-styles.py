#!/usr/bin/env python3
"""Generate the fork's default style library for 白い熊 Stylus.

A bg/fg matrix of ten global styles that occupy popup positions 1-9 and 0, three typography
globals, five UI-affordance globals, and the site-specific leftovers from the old Stylish export.
Per-site tuning is Stylus' own per-style exclusions.

Shipped preinstalled: src/background/fork-default-styles.json, imported by
src/background/fork-default-styles.js on the first start of a profile.  Pass --tmp to also drop a
stamped copy in ~/tmp for hand-importing into a profile that already exists.

### The specificity ladder

An `!important` declaration only beats another `!important` by specificity, so a blanket `*` rule
at (0,0,0) loses to any page rule as ordinary as `.card { background: #fff !important }`.  That is
why white sidebars, white cards and coloured buttons survived earlier versions of this library.

Every rule that has to win such a fight therefore carries `:not(#sk-never)` — an id that matches
nothing, worth (1,0,0) — and the layers are kept apart deliberately:

    (1,0,0)   the bg/fg/border blankets            *:not(#sk-never)
    (1,0,1)   their element groups                 div:not(#sk-never)
    (1,1,x)   UI affordances that must beat both   button:not(#sk-never), a:any-link:not(...)

Typography is left at upstream weights: nothing competes with it, and lifting it would mean
lifting the icon carve-outs in step for no gain.
"""
import json
import os
import sys
from datetime import datetime

# --- the specificity guard -------------------------------------------------
NEVER = ":not(#sk-never)"      # (1,0,0) — beats page `!important` up to class level
NEVER_CLS = ":not(.sk-never)"  # (0,1,0) — where only class level is needed

# --- selector groups -------------------------------------------------------
ALL = ["*"]
GROUND = ["html", "body"]
DIV = ["div"]
BLOCKS = ["section", "article", "main", "aside", "nav", "header", "footer", "form",
          "ul", "ol", "table", "thead", "tbody", "tfoot", "tr"]
TEXT = ["p", "span", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6",
        "blockquote", "dt", "dd", "figcaption", "label"]
EVERY = GROUND + DIV + BLOCKS + TEXT

# --- the shared "not prose" list -------------------------------------------
# Matches how icon systems are built rather than which site is using them.
# [class*="icon" i] is the workhorse: case-insensitive substring catches icon,
# Icon, nav-icon, IconButton, icon-search and most styled-components output.
# [aria-hidden="true"] is the other high-yield one: decorative icons carry it.
ICONS = [
    "i", "svg", "use", "symbol",
    '[class*="icon" i]', '[class*="glyph" i]', '[class*="symbol" i]', '[class*="ico-" i]',
    ".fa", '[class*="fa-"]', '[class*="material-icons"]', '[class*="material-symbols"]',
    '[class*="octicon"]', '[class*="bi-"]', '[class*="emoji" i]',
    '[role="img"]', '[aria-hidden="true"]',
]
CONTROLS = [
    "button", "input", "select", "textarea", "option", "optgroup",
    "progress", "meter", "summary",
    '[role="button"]', '[role="tab"]', '[role="menuitem"]',
    '[role="switch"]', '[role="checkbox"]', '[role="radio"]',
]
MEDIA = ["img", "picture", "video", "canvas", "object", "embed", "iframe"]
# The pseudo-element variants: * never matches ::before/::after, so a glyph drawn
# in a pseudo would otherwise inherit the parent's forced length.
ICON_PSEUDOS = [
    "i::before", "i::after",
    '[class*="icon" i]::before', '[class*="icon" i]::after',
    '[class*="fa-"]::before', '[class*="fa-"]::after',
    '[class*="material-icons"]::before', '[class*="material-symbols"]::before',
    '[class*="octicon"]::before', '[class*="bi-"]::before',
]
# Links that are really buttons. A cookie banner's "accept" is routinely an <a>, so the control
# rules never reached it — alza.cz uses `href="javascript:…"`, which is a precise signal that the
# link is an action rather than navigation; the class-name forms cover the rest. Kept to `a` so
# the blast radius stays on links, and carrying a doubled guard so these outrank `ui: links`,
# whose own (1,2,1) hover would otherwise repaint them cyan.
LINK_BUTTONS = ['a[href^="javascript:" i]', 'a[class*="btn" i]', 'a[class*="button" i]']

# Single-line text entry — the things that become a yellow pill.
TEXT_INPUTS = ('[type=text], [type=search], [type=email], [type=url], [type=tel],\n'
               '  [type=password], [type=number], [type=date], [type=datetime-local],\n'
               '  :not([type])')

# --- exclusion globs -------------------------------------------------------
# The leading `*.` makes the subdomain optional, so one pattern covers both the
# bare host and any subdomain.  See buildOverrideRe() in
# src/background/style-manager/matcher.js.
SUMO = "*://*.sumo.or.jp/*"
CLAUDE = "*://*.claude.ai/*"
OWNCLOUD = "*://*.owncloud.online/*"

YELLOW = "#ffff00"
DIM_YELLOW = "#999900"   # text-legible cousin of the icon's #666600 disabled state
CYAN = "#00ffff"
MAGENTA = "#ff80ff"
CODE_GREY = "#e0e0e0"


def wrap(items, per_line=4, sep=",\n"):
    out, line = [], []
    for it in items:
        line.append(it)
        if len(line) == per_line:
            out.append(", ".join(line))
            line = []
    if line:
        out.append(", ".join(line))
    return sep.join(out)


def guarded(items, guard=NEVER, pseudo="", per_line=3):
    """`div, p` -> `div:not(#sk-never), p:not(#sk-never)` at the given pseudo-element."""
    return wrap([it + guard + pseudo for it in items], per_line)


def blanket(guard=NEVER):
    """The universal selector plus its two pseudo-elements, all guarded."""
    return guarded(ALL, guard) + ",\n" + guarded(ALL, guard, "::before") + \
        ",\n" + guarded(ALL, guard, "::after")


def rule(selectors, *decls):
    body = "".join("    %s !important;\n" % d for d in decls)
    return "%s {\n%s}\n" % (selectors, body)


def style(name, code, exclusions=(), domains=(), enabled=True):
    return {
        "name": name,
        "enabled": enabled,
        "sections": [{
            "code": code,
            "urls": [],
            "urlPrefixes": [],
            "domains": list(domains),
            "regexps": [],
        }],
        "exclusions": list(exclusions),
        "inclusions": [],
        "updateUrl": None,
    }


BG = "background-color: black"
FG = "color: yellow"
SANS = "font-family: Arial, Helvetica, sans-serif"
MONO = 'font-family: "DejaVu Sans Mono", "Liberation Mono", Consolas, monospace'

# --- line-height -----------------------------------------------------------
# `1em` on * is equivalent to unitless 1 -- every element resolves it against its own font-size.
# The repair is an override rather than a :not() exclusion, because `normal` IS a universally safe
# value: it is recomputed per element from its own font metrics, so unlike a length it cannot be
# inherited into a child with a larger font-size.
LINE_HEIGHT = (
    rule(wrap(["*", "*::before", "*::after"], 3), "line-height: 1em")
    + "\n"
    + rule(wrap(EVERY), "line-height: 1em")
    + "\n/* icons, controls and media keep their own metrics */\n"
    + rule(wrap(ICONS + CONTROLS + MEDIA + ICON_PSEUDOS), "line-height: normal")
)

# --- sans-serif ------------------------------------------------------------
# Here the repair MUST be a :not() exclusion: there is no value meaning "the font this page
# wanted" -- `revert` drops to the UA default, not the page's.  :not() is per-element, so an
# exempt .fa keeps its icon font while an ordinary span inside it still gets Arial.
NOT_ICONS = ":not(%s)" % ", ".join(ICONS)
NOT_MEDIA = ":not(%s)" % ", ".join(MEDIA)
CODE_TAGS = ["pre", "code", "kbd", "samp", "tt"]
# These sit on the id ladder too, and have to: they carry a colour, so they compete with the
# `fg all` blanket at (1,0,0), and the descendant form competes with `fg text` at (1,0,1) —
# hence the doubled guard there rather than relying on which style happens to be injected last.
CODE_SELF = ", ".join(t + NEVER for t in CODE_TAGS)
CODE_KIDS = ", ".join(t + NEVER + " " + NEVER for t in ("pre", "code"))
SANS_SERIF = (
    rule("*%s,\n*%s::before,\n*%s::after" % (NOT_ICONS, NOT_ICONS, NOT_ICONS), SANS)
    + "\n/* Code keeps a monospace face and a colour that is not body-yellow. #sk-never is an id\n"
      "   that matches nothing; it exists purely to put these rules on the same specificity\n"
      "   ladder as the bg/fg blankets, which would otherwise repaint the code yellow. */\n"
    + rule(CODE_SELF, MONO, "color: %s" % CODE_GREY)
    + "\n"
    + rule(CODE_KIDS, MONO, "color: inherit")
)

styles = [
    # --- background: black, global with exceptions -------------------------
    style("bg all", rule(blanket(), BG), [CLAUDE, OWNCLOUD]),
    style("bg blocks", rule(guarded(BLOCKS), BG)),
    style("bg div", rule(guarded(DIV), BG), [CLAUDE]),
    style("bg ground", rule(guarded(GROUND), BG), [CLAUDE]),
    style("bg text", rule(guarded(TEXT), BG)),

    # --- colour: yellow, global with exceptions ----------------------------
    style("fg all", rule(blanket(), FG), [SUMO, CLAUDE]),
    style("fg blocks", rule(guarded(BLOCKS), FG), [SUMO, CLAUDE]),
    style("fg div", rule(guarded(DIV), FG), [SUMO, CLAUDE]),
    style("fg ground", rule(guarded(GROUND), FG), [SUMO]),
    style("fg text", rule(guarded(TEXT), FG), [SUMO]),

    # --- typography --------------------------------------------------------
    style("line-height", LINE_HEIGHT),
    style("sans-serif", SANS_SERIF),
    style("text-align", rule(wrap(TEXT), "text-align: left")),

    # --- UI affordances ----------------------------------------------------
    # Every frame, rule and divider on the page becomes yellow. border-color on an element whose
    # border-style is none paints nothing, so this is inert everywhere a border was not already
    # drawn -- it recolours, it does not add.
    style("ui: borders",
          rule(blanket(),
               "border-color: %s" % YELLOW,
               "outline-color: %s" % YELLOW,
               "column-rule-color: %s" % YELLOW,
               "caret-color: %s" % YELLOW)
          + "\n"
          + rule("hr" + NEVER,
                 "border-color: %s" % YELLOW,
                 "background-color: %s" % YELLOW,
                 "color: %s" % YELLOW)),

    # `outline` rather than `border`: an outline is drawn outside the layout box, so a visible
    # edge on every control costs no reflow and cannot shift a single pixel of the page.
    style("ui: controls",
          "/* buttons and selects: black ground, yellow trace, pill */\n"
          + rule(guarded(["button", "select", '[role="button"]',
                          '[role="tab"]', '[role="switch"]'], per_line=2),
                 "background-color: #000000",
                 "color: %s" % YELLOW,
                 "outline: 1px solid %s" % YELLOW,
                 "outline-offset: -1px",
                 "border-radius: 999px")
          + "\n/* the same treatment for links that act as buttons */\n"
          + rule(guarded(LINK_BUTTONS, NEVER + NEVER, per_line=1),
                 "background-color: #000000",
                 "color: %s" % YELLOW,
                 "outline: 1px solid %s" % YELLOW,
                 "outline-offset: -1px",
                 "border-radius: 999px",
                 "padding: 0.25em 0.9em")
          + "\n/* single-line text entry: a yellow pill, traced rather than filled. The outline\n"
            "   follows border-radius, and being an outline it adds no layout of its own — only\n"
            "   the padding does, which the rounded ends need so text is not clipped. */\n"
          + rule("input%s:is(%s)" % (NEVER, TEXT_INPUTS),
                 "background-color: #000000",
                 "color: %s" % YELLOW,
                 "caret-color: %s" % YELLOW,
                 "border: none",
                 "border-radius: 999px",
                 "outline: 1px solid %s" % YELLOW,
                 "outline-offset: -1px",
                 "padding-left: 0.7em",
                 "padding-right: 0.7em")
          + "\n"
          + rule("input%s::placeholder" % NEVER, "color: %s" % DIM_YELLOW)
          + "\n/* a textarea is not a pill — it keeps the traced-box treatment */\n"
          + rule("textarea" + NEVER,
                 "background-color: #000000",
                 "color: %s" % YELLOW,
                 "caret-color: %s" % YELLOW,
                 "outline: 1px solid %s" % YELLOW,
                 "outline-offset: -1px")
          + "\n"
          + rule("textarea%s::placeholder" % NEVER, "color: %s" % DIM_YELLOW)
          + "\n"
          + rule('input%s:is([type=checkbox], [type=radio])' % NEVER,
                 "accent-color: %s" % YELLOW)
          + "\n"
          + rule(wrap(["button%s:hover" % NEVER, '[role="button"]%s:hover' % NEVER,
                       'input%s:is([type=submit], [type=button]):hover' % NEVER]
                      + [b + NEVER + NEVER + ":hover" for b in LINK_BUTTONS], 1),
                 "background-color: %s" % YELLOW,
                 "color: #000000")),

    # Artwork drawn on transparency expects a page of some colour; on our black ground whichever
    # ink it uses can vanish. A ground behind the replaced element restores it, and costs nothing
    # behind an opaque photo, which covers it completely.
    #
    # The ground is mid grey, NOT white. White fixes dark ink and destroys light ink — a white
    # icon on a white square is exactly as invisible as a black one on black, which is what
    # happened to the nav icons on forum.mobilism.org. #808080 is the one value where neither can
    # disappear: roughly 5:1 against black ink and 4:1 against white.
    #
    # Inline <svg> is deliberately absent: it follows currentColor and is already yellow, so a
    # grey box behind every icon would be pure noise.
    style("ui: image-ground",
          rule(guarded(["img", "picture", "object", "embed"], per_line=2),
               "background-color: #808080")),

    # background-color cannot remove a background *image*, so decorative gradients and banner
    # textures survive the blanket and keep painting pale bars across otherwise-black pages.
    #
    # SHIPPED DISABLED, and renamed so the sync withdraws the enabled copy an earlier build
    # installed — the sync deliberately preserves a style's on/off state, so shipping the same
    # name disabled would have changed nothing on a profile that already had it on.
    #
    # It is off because there is no way in CSS to tell a decorative gradient from a content
    # image, and the attempts cost real content twice: unrestricted, it erased the jisho.org
    # logo (`h1.logo a { background: url(…) }` behind hidden text); restricted to `:empty`, it
    # erased every product thumbnail in alza.cz's carousels, which are empty elements carrying a
    # background image. Enable it per site — tick "only apply to included sites" and add the
    # domain — where a pale bar is worth more than whatever else it takes with it.
    style("ui: strip-backdrops",
          rule("*:empty%s%s%s" % (NEVER, NOT_ICONS, NOT_MEDIA),
               "background-image: none"),
          enabled=False),

    style("ui: focus",
          rule(":focus-visible" + NEVER,
               "outline: 2px solid %s" % CYAN,
               "outline-offset: 0")),

    # Sites constrain article text to a narrow column with max-width; this hands the window back.
    # Media keeps its own max-width, which is what stops an oversized image overflowing.
    style("ui: full-width",
          rule("*%s:not(%s)" % (NEVER, ", ".join(MEDIA)), "max-width: none")),

    # a:any-link and its descendants, lifted over the fg blanket. The descendant term is what does
    # the real work — modern sites wrap link text in a span — but it must skip icons, or every
    # icon sitting inside a link turns cyan instead of staying yellow.
    # :visited is listed after :any-link so the tie resolves to it. Firefox restricts :visited to
    # colour properties on the <a> itself and never on descendants — a privacy rule, not a bug.
    style("ui: links",
          rule("a:any-link%s,\n[role=\"link\"]%s,\n"
               "a:any-link *%s%s,\n[role=\"link\"] *%s%s" % (
                   NEVER, NEVER, NEVER, NOT_ICONS, NEVER, NOT_ICONS),
               "color: %s" % CYAN)
          + "\n"
          + rule("a:visited" + NEVER, "color: %s" % MAGENTA)
          + "\n"
          + rule("a:any-link%s:hover, a:any-link%s:hover *%s,\n"
                 "a:any-link%s:focus-visible, a:any-link%s:focus-visible *%s,\n"
                 '[role="link"]%s:hover, [role="link"]%s:hover *%s' % (
                     NEVER, NEVER, NEVER, NEVER, NEVER, NEVER, NEVER, NEVER, NEVER),
                 "color: #000000",
                 "background-color: %s" % CYAN)),

    # --- site-specific leftovers -------------------------------------------
    style("site: casopisargument.cz",
          rule(wrap(["*", "*::before", "*::after"], 3), "font-size: 16px")
          + "\n" + rule(wrap(EVERY), "font-size: 16px"),
          domains=["casopisargument.cz"]),
    # pre/code colour is global now; only the block metrics remain site-specific
    style("site: claude.ai",
          rule("pre.code-block__code", "padding: 4px 8px", "margin: 2px 0"),
          domains=["claude.ai"]),
    style("site: nikkansports.com",
          rule(wrap(EVERY), "font-size: 30px") + "\n" + rule("h1", "font-size: 40px"),
          domains=["nikkansports.com"]),
]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
outs = [os.path.join(ROOT, "src", "background", "fork-default-styles.json")]
if "--tmp" in sys.argv:
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outs.append(os.path.expanduser("~/tmp/stylus-library_%s.json" % stamp))
for out in outs:
    with open(out, "w", encoding="utf-8") as f:
        json.dump(styles, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(out)
