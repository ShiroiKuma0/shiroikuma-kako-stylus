#!/usr/bin/env python3
"""Generate the fork's default style library for 白い熊 Stylus.

A bg/fg matrix of ten global styles that occupy popup positions 1-9 and 0, three typography
globals, nine UI-affordance globals, and the site-specific leftovers from the old Stylish export.
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
# The one element of MEDIA that is a window onto another document rather than a surface of this
# one. `object` and `embed` are the same in kind, but they are NOT in this list: `ui: image-ground`
# already hands them its mid grey at (1,0,1), the very weight this carve-out needs, and two rules
# of equal weight are decided by whichever sheet was injected last. A transparent overlay is an
# iframe in every case met; a plugin element is artwork, and artwork is what the grey is for.
FRAMES = ["iframe"]
# An icon is not the only thing a site draws as an empty box with a background image, and the
# `:empty` sweep in `ui: strip-backdrops` cannot tell such a picture from a decorative strip. Same
# heuristic as ICONS — match how the thing is NAMED — carrying the words that mean "this
# background is a picture": reCAPTCHA's privacy badge is
# `<div class="rc-anchor-logo-img rc-anchor-logo-img-large">` with `background: url(logo_48.png)`,
# and nothing in ICONS comes close to it, so the sweep erased the logo and left an empty box.
# The asymmetry that governs the whole file applies here too: guess wrong sparing something and a
# decorative bar stays visible, which is cosmetic; guess wrong stripping something and content is
# simply gone.
# `poster`, `preview` and `cover` were added when the same heuristic had to serve a second
# rule: a video player's poster frame is a background image on the <button> that covers the
# player until you press it, and the class carrying it says so — `…placeholderWithPoster…`.
ART = ['[class*="logo" i]', '[class*="brand" i]', '[class*="badge" i]', '[class*="avatar" i]',
       '[class*="sprite" i]', '[class*="flag" i]', '[class*="thumb" i]', '[class*="img" i]',
       '[class*="photo" i]', '[class*="picture" i]', '[class*="poster" i]',
       '[class*="preview" i]', '[class*="cover" i]']
# The things that look and behave like a button. Split from the void `input` forms because
# `:empty` is always true of a void element and so can tell you nothing about it.
BUTTONS = ["button", "select", '[role="button"]', '[role="tab"]', '[role="switch"]']
BUTTON_INPUTS = ['input[type="submit"]', 'input[type="button"]', 'input[type="reset"]']
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

# A floating label or a fake placeholder is a span or a label that FOLLOWS its control, and that
# order is not a coincidence: it is what makes `input:not(:placeholder-shown) + label` expressible,
# so every implementation of the pattern puts it there. It is then laid back over the control's
# own text line, which is why painting it matters so much more than painting anything else.
#
# Sibling-scoped, and that took a wrong turn to establish. The first version asked instead for
# "anything inside an element that holds a control", which reads well and is far too greedy: a
# page card that merely contains a search box is such an element, and in the fixture it unpainted
# an <hr>, an inline <svg> and a cookie-accept link several rows away from the input.
CONTROLS_OWNING = ["input", "textarea", "select"]
ADORNMENTS = ["span", "label"]
ADORNMENT_SEL = ":is(%s)%s ~ :is(%s)%s" % (", ".join(CONTROLS_OWNING), NEVER,
                                           ", ".join(ADORNMENTS), NEVER)

# --- design tokens ---------------------------------------------------------
# The shadcn/ui vocabulary, which Tailwind v4 sites declare on :root.  Only the tokens that get
# used ALONE are moved, and that restriction is the whole design.  `--foreground` and
# `--muted-foreground` are ink applied to whatever ground happens to be there — a timestamp is
# `text-muted-foreground` on nothing — so on our black they must move or go dark-on-dark.
# `--primary`, `--secondary`, `--accent` and `--destructive` travel with their own `-foreground`
# partner (`bg-primary text-primary-foreground`), a pair the site has already made legible and
# that a black ground cannot disturb; moving half of one would be how you break a blue button.
# `--accent` in particular is a hover band, and left alone it keeps the hover cue visible.
#
# The surfaces below are moved because their ink partners are: a card must be black if
# `--card-foreground` is yellow.  The line colours have no partner at all, and match `ui: borders`
# — inside a shadow root the token is the ONLY way to reach a border, since no rule of ours does.
TOKENS_SURFACE = ["--background", "--card", "--popover", "--muted", "--sidebar"]
TOKENS_INK = ["--foreground", "--card-foreground", "--popover-foreground", "--sidebar-foreground"]
TOKENS_DIM = ["--muted-foreground"]
TOKENS_LINE = ["--border", "--input", "--ring", "--sidebar-border", "--sidebar-ring"]

# --- exclusion globs -------------------------------------------------------
# The leading `*.` makes the subdomain optional, so one pattern covers both the
# bare host and any subdomain.  See buildOverrideRe() in
# src/background/style-manager/matcher.js.
SUMO = "*://*.sumo.or.jp/*"
SUBSTACK = "*://*.substack.com/*"
UNHERD = "*://*.unherd.com/*"
CLAUDE = "*://*.claude.ai/*"
OWNCLOUD = "*://*.owncloud.online/*"
ALZA = "*://*.alza.cz/*"

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


def style(name, code, exclusions=(), domains=(), enabled=True, only_on=()):
    """`only_on` turns the style into an allowlist: Stylus applies it to those sites and nowhere
    else. That is `inclusions` plus the `overridden` flag — the "only apply to included sites"
    checkbox — see cache.js:41. Adding a site later is one keystroke in the popup: the menu's
    `+` on the domain row."""
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
        "inclusions": list(only_on),
        "overridden": bool(only_on),
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
NOT_CONTROLS = ":not(%s)" % ", ".join(CONTROLS)
NOT_ART = ":not(%s)" % ", ".join(ART)
# A link is interactive, so it is never one of the transparent layers the `:empty` sweep is after,
# and its background image is its label exactly as a control's is.
LINKS = ["a", '[role="link"]']
NOT_LINKS = ":not(%s)" % ", ".join(LINKS)
# A control that holds a picture is a media surface wearing a control's clothes, and no name says
# so: a player is routinely `<div role="button">` wrapped around a <video>, under a hashed class
# name that says nothing at all.  The child is the tell.
NOT_MEDIA_HOST = ":not(:has(%s))" % ", ".join("> " + m for m in MEDIA)
# ⚠ A shut drawer is `width: 0`, and `width: auto` re-opens it.  A page that keeps a panel in the
# DOM at `width: 0` with `overflow: hidden` — the transcript drawer beside a podcast player, an
# off-canvas menu, any panel that slides — is saying the panel is closed; releasing its width sizes
# it to the content it was hiding.  On its own that would be only an odd wide box, but such a
# drawer is nearly always `flex: none` beside a `flex: auto; min-width: 0` stage, and then the
# space does not come out of the window: it comes out of the box next to it.  A stage frames a
# picture with an absolutely-positioned child, so it has NO intrinsic width of its own to defend
# with, and it gives up everything — the video collapsed to 0 px wide and what was left was the
# player shell's own black 16:9 band, which is how every post on a whole domain came to render as
# a black rectangle under the header.  So: never release the width of a box that follows a box
# framing media.  The row that frames a picture is a geometry the page computed, and nothing in it
# can be widened except by taking from the frame.
#
# Two deliberate limits.  Only DOM order after the frame, because that is where a drawer is
# written — it is appended, not prepended — and the mirrored arm would spare every element that
# merely precedes a player, which on a flat page is most of them; the fixture's own column pinned
# by `width: 300px` is one.  And `img`/`picture` stay out: an image carries its own intrinsic
# width and cannot collapse to nothing, so its neighbours are not part of this.
#
# `:has()` may not be nested inside `:has()`, and `:not()` takes a NON-forgiving list, so one
# invalid arm silently drops the whole rule — the first draft wrote `:has(~ *:has(video))` and the
# engine kept 3 of this style's 4 rules.  Hence the flat form: framed media as the sibling itself,
# and framed media inside the sibling, spelled out separately.
FRAMED = ["video", "iframe", "canvas", "object", "embed"]
NOT_FRAME_NEIGHBOUR = ":not(%s)" % ", ".join(
    ["*:has(%s) ~ *" % ", ".join(FRAMED)] + ["%s ~ *" % m for m in FRAMED])
# ⚠ A stretched link is an invisible sheet over the card it belongs to.  The whole-card click
# target is one <a> laid across the tile — `position: absolute; inset: 0; font-size: 0;
# color: transparent; background-color: transparent` — and every clause of that says the same
# thing: it is a hit area, and it draws nothing.  Painted, it is an opaque sheet at the top of the
# card's stack, and a bookshop's search results came out as rows holding a heart and a star rating
# and nothing else: cover, author, title, format and price all behind it.
#
# `ui: overlays` could not reach it, and neither of its two handles was ever going to.  The class
# reads `element-link-toplevel`, which is a fact about the DOM rather than about painting, so no
# name list touches it; and it is not `:empty`, since the accessible name is a text node with a
# data element beside it — and links are excluded from that sweep anyway, deliberately, because an
# empty link is a wordmark.  The structure is the only handle left, and it is a good one: the link
# holds no picture of its own and lies BESIDE one, which is the card idiom wherever it appears —
# a product grid, an article teaser, a video tile.  Both directions of the sibling axis, because
# the overlay is written before the content as often as after it, and spelled out flat: `:has()`
# may not be nested inside `:has()`.
#
# Greedy, and here that is very nearly free.  It also reaches the ordinary title link inside a
# tile — 21 of them on the alza fixture — and unpainting a text link costs nothing, because
# `bg all` has already painted every ancestor black and the link's own box was doing no more than
# showing that black through.  What it would cost is a pill link carrying a light ground of its
# own next to a picture; the ones that name themselves buttons are still painted by `ui: controls`
# at (2,1,1), which is where most of that shape lives.
IS_MEDIA = ":is(%s)" % ", ".join(MEDIA)
NO_OWN_MEDIA = ":not(:has(%s))" % ", ".join(MEDIA)


def beside_media(sel):
    """The four arms of "this box lies beside a picture", written flat.

    Both directions of the sibling axis, because a layer is written before the content as often as
    after it, and the media may be the sibling itself or anywhere inside it. Flat because `:has()`
    may not be nested inside `:has()` — and `:not()` takes a NON-forgiving list, so one invalid arm
    would silently drop the whole rule.
    """
    return ",\n".join([
        "%s:has(~ %s)" % (sel, IS_MEDIA),
        "%s:has(~ * %s)" % (sel, IS_MEDIA),
        "%s ~ %s" % (IS_MEDIA, sel),
        "*:has(%s) ~ %s" % (IS_MEDIA, sel),
    ])


CARD_LINK = "a" + NEVER + NO_OWN_MEDIA
CARD_LINK_SEL = beside_media(CARD_LINK)
# ⚠ A box whose whole content is controls has nothing of its own to make legible.  The carousel
# nav strip is the shape that says it plainly: one absolutely-positioned layer stretched over the
# entire carousel viewport, `pointer-events: none` so the picture underneath stays clickable, and
# inside it nothing but the prev and next buttons, which take their own pointer events back.  It
# is chrome FOR the picture, and painting it boards the picture up — a shop's product page came
# back with the main photo, the thumbnail row and two whole recommendation carousels gone, five
# black rectangles where every picture on the page had been.
#
# Neither handle `ui: overlays` had could reach it.  Not `:empty` — it holds the two buttons — and
# not a name: the classes read `carousel-navs carousel-def car-load-hide abs`, which describe the
# widget, not the painting.  `pointer-events: none` is the honest tell and CSS cannot select on it
# (a property has no access to its own computed value, the same wall the padding and the CSS
# triangle hit), so the structure has to carry it: holds a control, holds NOTHING but controls,
# holds no picture, and lies beside one — the same sibling test the card click target uses, since
# a strip of chrome and the picture it drives are siblings by construction.
#
# `:has(> control)` is not redundant beside `:not(:has(> :not(control)))`: the second is vacuously
# true of an element with no element children at all, and every `:empty` layer on the page would
# match it.  Between them they say "its children are controls, and it has some".
#
# And "children" there means ELEMENT children — `:has(> :not(...))` cannot see a text node, so a
# row of prose with a button in it is matched as well as a bare strip of chrome.  That is the
# rule's real boundary and it is a mild one: what such a row loses is a ground of its own, and its
# ancestors are already black; its words are already yellow.  A `<span>` around those words puts
# it back, since a span is an element and not a control.
#
# LINK_BUTTONS is deliberately NOT in the list.  Widening it to links was tried and it stopped
# being a strip of chrome: on the video fixture it took a `bottombar` the page had grounded at
# `#1a1a1a` and a pagination row — real surfaces, of the page's own making.  The met case is
# `[role="button"]`, and a box holding only links is a menu.
#
# Greedy in the same nearly-free way the card link is: it also reaches an in-flow row of buttons
# sitting beside a picture, and all that costs is the row showing the black of its ancestors
# instead of its own.  The controls inside keep the black ground and yellow trace `ui: controls`
# gives them at (2,1,1), so a button never goes missing with the strip.
CONTROL_KINDS = ":is(%s)" % ", ".join(BUTTONS + BUTTON_INPUTS)
CONTROL_STRIP = "*%s:not(:has(> :not(%s))):has(> %s)%s" % (
    NEVER, CONTROL_KINDS, CONTROL_KINDS, NO_OWN_MEDIA)
CONTROL_STRIP_SEL = beside_media(CONTROL_STRIP)
# ⚠ A picture stacked behind the page is a picture we bury ourselves.  `z-index: -1` on an in-flow
# image wrapper is an ordinary idiom — it is how a card puts its cover under the layer that has to
# stay clickable — and it works only because everything above it is transparent.  Painting order
# is what makes that fragile: a negative-z child is drawn at step 2 of its nearest ancestor
# STACKING CONTEXT, while the backgrounds of ordinary block descendants are drawn at step 3, above
# it.  When that context is <html>, as it is whenever no ancestor is positioned with a z-index of
# its own, the picture ends up beneath the ground of every box between it and the root — <body>
# alone is enough, so even `bg ground` on its own buries it.  On the bookshop's grid it left a
# blank band where every cover had been, with the tile's text back in place around it.
#
# The repair goes on the PARENT, not on the picture.  Lifting the picture's own z-index would fix
# this case and break the other one: a full-bleed backdrop is `position: absolute; inset: 0;
# z-index: -1` behind its section's text, and raising it paints it OVER the words.  Making the
# parent a stacking context asks for exactly what is wanted and nothing more — the picture is
# trapped inside its own card, painted above that card's ground and still below its siblings, and
# no ancestor can bury it any more.  `isolation` was chosen over `position: relative; z-index: 0`
# because it creates the context without touching the containing block a descendant may be
# positioned against; it does not affect `position: fixed` either, which only transform, filter
# and will-change do.
#
# The cost is a stacking context around every box holding a picture directly: a positioned
# descendant with a large z-index can no longer escape it, so a dropdown hanging out of a card
# that has a direct media child could fall behind the next card.  Cosmetic, and narrow — the
# direct-child test keeps it off the deep wrappers where those layers usually live — against a
# cover that is simply gone.
MEDIA_PARENT = "*%s:has(> %s)" % (NEVER, IS_MEDIA)
# ⚠ The CSS-triangle idiom: two transparent borders and one coloured, which is how a play arrow,
# a select caret, a tooltip point and a speech-bubble tail are all drawn.  Recolouring every side
# turns the triangle into a solid square — a white play arrow becomes a yellow block.  CSS
# cannot ask whether a border is transparent (a property has no access to its own value), so the
# only reachable discriminator is the name.  Greedy on purpose: `[class*="play" i]` also catches
# `display`, `player` and `playlist`, and all that costs is those keeping the border colour the
# site chose, which is the cosmetic side of the asymmetry.
TRIANGLES = ['[class*="arrow" i]', '[class*="caret" i]', '[class*="triangle" i]',
             '[class*="chevron" i]', '[class*="play" i]', '[class*="tooltip" i]']
NOT_TRIANGLES = ":not(%s)" % ", ".join(TRIANGLES)
# ⚠ A value bar's reading IS the boundary between two colours, and it is empty on purpose.
# A volume slider, a scrubber, a progress bar and a level meter are all one idiom: a track, and
# inside it a filled part whose width (or height, or scaleX) is the number.  The filled part holds
# no text and no child, because it does not need any — its content is its geometry.  That is
# exactly the shape the `:empty` sweep in `ui: overlays` was built to neutralise, on the premise
# that "an element with no content has nothing of its own to make legible", and here the premise is
# simply wrong: the sweep wiped the level's own white, `bg all` and `bg div` painted the track
# black, and a volume bar that slides open on hover came out as a black rectangle with no reading
# in it at all.  So the filled part is given ink of its own, and only the filled part — a yellow
# level on the black track is the boundary back, and touching the track as well would risk a grey
# box wherever a name matched something that is not a bar.
# The name is the only handle, as with ICONS and ART: a hashed class keeps its readable prefix
# (`volumeLevel-VDMLnw`, `progress-K0IenH`) and Video.js spells it out (`vjs-volume-level`,
# `vjs-play-progress`).  Matched on the element or on its parent, since a generic `<div class=fill>`
# inside `<div class=progress>` is just as common as a named level.  `range` and `track` are
# deliberately absent — they would catch *orange*, *tracking* and *soundtrack* — and the same
# media/control/icon guards the sweep uses are kept, so a void <input type=range> or an <img> never
# takes the ink.
VALUE_BARS = ['[class*="volume" i]', '[class*="progress" i]', '[class*="scrub" i]',
              '[class*="seek" i]', '[class*="slider" i]', '[class*="played" i]',
              '[class*="buffer" i]', '[class*="meter" i]', '[class*="gauge" i]',
              '[class*="level" i]', '[role="progressbar"]', '[role="slider"]']
IS_VALUE_BAR = ":is(%s)" % ", ".join(VALUE_BARS)
NOT_VALUE_BAR = ":not(%s)" % ", ".join(VALUE_BARS)
# The doubled guard is load-bearing: the `:empty` sweep it has to beat sits near (1,4,2), which no
# amount of class terms would clear, and the same trick already puts the named-overlay rules above
# every bg blanket.  Two ids make it (2,x,y) and the argument is over.
VALUE_BAR_SELF = "*:empty%s%s%s%s%s%s" % (NEVER, NEVER, NOT_ICONS, NOT_MEDIA,
                                          NOT_CONTROLS, IS_VALUE_BAR)
VALUE_BAR_KID = "%s%s > *:empty%s%s%s%s%s" % (IS_VALUE_BAR, NEVER, NEVER, NEVER,
                                              NOT_ICONS, NOT_MEDIA, NOT_CONTROLS)
CODE_TAGS = ["pre", "code", "kbd", "samp", "tt"]
# These sit on the id ladder too, and have to: they carry a colour, so they compete with the
# `fg all` blanket at (1,0,0), and the descendant form competes with `fg text` at (1,0,1) —
# hence the doubled guard there rather than relying on which style happens to be injected last.
CODE_SELF = ", ".join(t + NEVER for t in CODE_TAGS)
CODE_KIDS = ", ".join(t + NEVER + " " + NEVER for t in ("pre", "code"))
# The element side of the same failure, and the one place a name list is still the only handle.
# Video.js declares `.video-js .vjs-play-progress, .video-js .vjs-volume-level { font-family:
# VideoJS }` on the ELEMENT and draws the round scrubber and volume knobs in its ::before, which
# inherits — so forcing Arial on the element hands the pseudo Arial too and both knobs come out as
# hex boxes.  Dropping the pseudo form cannot help here and nothing structural can: which element
# carries a webfont is a fact about the page's stylesheet, and CSS cannot ask.  `vjs-` earns a line
# on the same terms as `.fa`, `octicon` and `bi-` in ICONS — it names a library, not a site, and it
# is one of the two players most of the web embeds.  It is kept out of ICONS proper because that
# list also drives the `:empty` background sweeps and `ui: full-width`, where exempting every
# element of a player would have consequences worth arguing about; here the whole cost of a wrong
# guess is that an element keeps the font the page chose.
FONT_HOSTS = ['[class*="vjs-" i]']
NOT_FONT_HOSTS = ":not(%s)" % ", ".join(FONT_HOSTS)
# ⚠ The blanket stops at the element: it must never reach ::before/::after.  Work out what the
# pseudo form could ever DO and it comes out a pure loss.  `font-family` inherits, and a pseudo
# inherits from its originating element, so wherever the page declares no font on the pseudo it
# already gets whatever we gave the element — Arial when the element is prose, the icon face when
# the element is exempt (`*:not(ICONS)::before` skips an exempt element's pseudo too).  The rule
# therefore changes exactly one thing: it overrides a font the page put ON the pseudo itself.  And
# setting a font on a pseudo is one idiom and one only — an icon font, whose glyph lives in the
# Private Use Area and exists in no other face.  Forced to Arial the codepoint maps nowhere and
# Gecko draws the .notdef hex box: a video player's transport bar came out as five little boxes
# reading `E605`, `E60B`, `E606`, `E603`, `E601` where play, mute, quality, picture-in-picture and
# fullscreen should be.  Nothing in ICONS could have caught them — the glyph is drawn on the
# ::before of the control itself and the class names say `vjs-play-control`, `vjs-mute-control`,
# nothing about icons — and no name list ever will, since which element carries an icon font is a
# fact about the page's stylesheet, not about its markup.  Dropping the pseudo form fixes every
# such site at once and costs nothing anywhere, which is why there is no :not() list here.
SANS_SERIF = (
    rule("*%s%s" % (NOT_ICONS, NOT_FONT_HOSTS), SANS)
    + "\n/* Code keeps a monospace face and a colour that is not body-yellow. #sk-never is an id\n"
      "   that matches nothing; it exists purely to put these rules on the same specificity\n"
      "   ladder as the bg/fg blankets, which would otherwise repaint the code yellow. */\n"
    + rule(CODE_SELF, MONO, "color: %s" % CODE_GREY)
    + "\n"
    + rule(CODE_KIDS, MONO, "color: inherit")
)

styles = [
    # --- background: black, global with exceptions -------------------------
    # Note `guarded(ALL)` and not `blanket()`: the background blanket deliberately does NOT reach
    # ::before/::after. A pseudo-element with `content` is decoration — very often a transparent
    # absolutely-positioned overlay for a hover shade — and giving it a background paints an
    # opaque sheet over whatever it covers. That is what blanked the product tiles in alza.cz's
    # carousel: image, stars, name and price vanished under the tile's own ::before, while the
    # discount badge (z-index 1) and the button outside the tile box survived.
    #
    # Colour is different: `fg all` keeps the pseudo-elements, because text drawn in a pseudo has
    # to be yellow like any other text. Painting a pseudo can only hide; colouring one cannot.
    #
    # ⚠ And it must not paint a frame. An <iframe> is a WINDOW, not a surface: what you see through
    # it is the embedded document, and the element's own background shows only through the parts
    # that document leaves transparent. So painting it is either invisible or catastrophic, never
    # useful. Invisible, because a page that paints its own ground covers ours — and we cannot
    # restyle a cross-origin document anyway, while a same-origin one gets our sheets injected into
    # the frame itself, where `bg ground` blackens its html/body directly. Catastrophic, because
    # the transparent frame is an idiom: a payment SDK parks a full-viewport `allowtransparency`
    # frame in the DOM at `z-index: 2147483647` waiting for a card challenge that may never come,
    # and an extension hangs its own UI in one the same way. Black, that frame is an opaque sheet
    # over the entire viewport at the maximum z-index — nothing can be above it, and the page
    # renders 100 % `#000`. It is the empty-pinned-layer failure again, but `ui: overlays` cannot
    # reach it: its `:empty` sweep excludes media precisely because an iframe is always `:empty`.
    # The repair is a rule rather than a `:not()` on the blanket, and that is load-bearing — a type
    # selector inside `:not()` costs (0,0,1) and would lift `bg all` from (1,0,0) to (1,0,1), where
    # it would tie with `ui: image-ground` and the grey behind every transparent PNG would come or
    # go with the injection order — the same tie that keeps `object` and `embed` out of FRAMES.
    style("bg all",
          rule(guarded(ALL), BG)
          + "\n/* a frame is a window onto another document; painting it can only board it up */\n"
          + rule(guarded(FRAMES, per_line=3), "background-color: transparent"),
          [CLAUDE, OWNCLOUD]),
    # The table rule lives HERE, not in ui: strip-backdrops, and that placement is the point.
    # A background image on a table cell or row is a tiled gradient strip in every case I have met
    # — vBulletin paints every .thead/.tcat/.tfoot bar that way, which is where mobileread.com's
    # light-blue bars and the white strips under yellow text came from — and colour paints behind
    # an image, so `bg blocks` was leaving its own work half done. Putting it in strip-backdrops
    # first was a mistake: that style ships enabled but the sync preserves each profile's own
    # on/off state, so on a profile where it had been switched off the fix could never run.
    style("bg blocks",
          rule(guarded(BLOCKS), BG)
          + "\n"
          + rule(guarded(["table", "thead", "tbody", "tfoot", "tr", "td", "th"], NEVER, per_line=4),
                 "background-image: none")),
    style("bg div", rule(guarded(DIV), BG), [CLAUDE]),
    # The page ground also drops its background *image*. background-color paints behind an image,
    # never over it, so a body wallpaper keeps showing through wherever the content wrapper does
    # not cover it — the light bands down both margins on forum.mobilism.org are a
    # `linear-gradient(#ccc, #e8e8e8)` on <body>. Safe to generalise, unlike the same fix
    # elsewhere: a background image on <html> or <body> is page decoration by definition, and it
    # is precisely the thing a black ground is meant to replace.
    style("bg ground", rule(guarded(GROUND), BG, "background-image: none"), [CLAUDE]),
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
          rule(blanket(NEVER + NOT_TRIANGLES),
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
          # input[type=submit|button|reset] are buttons too. Leaving them out is what left the
          # Search button unpainted on forum.mobilism.org.
          + rule(guarded(BUTTONS + BUTTON_INPUTS, per_line=2),
                 "background-color: #000000",
                 "color: %s" % YELLOW,
                 "outline: 1px solid %s" % YELLOW,
                 "outline-offset: -1px")
          + "\n/* ⚠ The pill is chrome, and only a chrome-sized control should wear it. A 624x351\n"
            "   `<div role=\"button\">` wrapping a <video> is a control by ARIA and a picture by\n"
            "   every other measure, and 999px turns it into an ellipse — the poster is clipped to\n"
            "   an oval and the <video> inherits the radius with it, so the whole player goes.\n"
            "   Spared by the same two tests the background image is spared by:\n"
            "   a name that says picture, or a media child. The void input forms cannot hold a\n"
            "   child at all, so they keep the pill unconditionally. */\n"
          + rule(wrap([b + NEVER + NOT_ART + NOT_MEDIA_HOST for b in BUTTONS]
                      + [b + NEVER for b in BUTTON_INPUTS], 1),
                 "border-radius: 999px")
          + "\n/* A control's background image is a gloss gradient, and colour paints behind an\n"
            "   image rather than over it, so without this the button stays white — that is what\n"
            "   left the Search button light on forum.mobilism.org even once it was targeted.\n"
            "   EXCEPT when the control is empty, and then the image is the only label it has:\n"
            "   reCAPTCHA's reload, audio and info controls are 48x48 <button>s carrying\n"
            "   `background: url(refresh_2x.png)` and nothing at all inside, so stripping it left\n"
            "   three blank rings and no way to ask for a new challenge. An icon drawn as an\n"
            "   inline <svg> child never enters into it: a child makes the button non-empty.\n"
            "   EXCEPT, again, when the class says the background is a picture: a player's poster\n"
            "   frame is exactly that — a background image on a <button> that is not empty,\n"
            "   because it holds the play arrow. `:empty` cannot see it; the name can. */\n"
          + rule(wrap([b + NEVER + ":not(:empty)" + NOT_ART for b in BUTTONS], 1),
                 "background-image: none")
          + "\n/* the button-shaped inputs are void elements, so `:empty` is always true of them\n"
            "   and can say nothing; their label is the `value`, never a picture */\n"
          + rule(guarded(BUTTON_INPUTS, per_line=2), "background-image: none")
          + "\n/* And such an icon is drawn on transparency — reCAPTCHA's is pure #000 — so on a\n"
            "   black button it would be exactly as gone as when we were erasing it. Same answer\n"
            "   as `ui: image-ground`, and the same mid grey, for the same reason: it is the one\n"
            "   value where neither dark nor light ink can disappear. Elements whose class says\n"
            "   `icon` are left out, because those draw the glyph with `color`, already yellow. */\n"
          + rule(wrap([b + NEVER + ":empty" + NOT_ICONS for b in BUTTONS], 1),
                 "background-color: #808080")
          + "\n/* the same treatment for links that act as buttons */\n"
          + rule(guarded(LINK_BUTTONS, NEVER + NEVER, per_line=1),
                 "background-color: #000000",
                 "background-image: none",
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
                 "background-image: none",
                 "color: %s" % YELLOW,
                 "caret-color: %s" % YELLOW,
                 "border: none",
                 "border-radius: 999px",
                 "outline: 1px solid %s" % YELLOW,
                 "outline-offset: -1px")
          + "\n/* ⚠ and the padding ONLY where the field has nothing else in it. A site that pads a\n"
            "   field generously is usually making room for a leading icon, and overriding that\n"
            "   with a smaller value walks the text straight underneath it: Piano pads its login\n"
            "   field for the envelope, we cut it to 0.7em, and the first characters of what you\n"
            "   type disappear behind the glyph. CSS cannot say \"at least this much\" — padding\n"
            "   has no access to its own current value — so the only safe move is not to touch a\n"
            "   field that has an adornment to make room for.\n"
            "   The test is on the PARENT's children rather than on the input's later siblings,\n"
            "   which catches a leading icon written before the input as well as after it. Being\n"
            "   greedy costs nothing here, unlike everywhere else in this file: over-matching only\n"
            "   means a field keeps the padding the site chose, which is by definition what the\n"
            "   site wanted. */\n"
          + rule("*:not(:has(> :is(span, label, i, svg, img)))%s > input%s:is(%s)"
                 % (NEVER, NEVER, TEXT_INPUTS),
                 "padding-left: 0.7em",
                 "padding-right: 0.7em")
          + "\n"
          + rule("input%s::placeholder" % NEVER, "color: %s" % DIM_YELLOW)
          + "\n/* a textarea is not a pill — it keeps the traced-box treatment */\n"
          + rule("textarea" + NEVER,
                 "background-color: #000000",
                 "background-image: none",
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
                 "color: #000000")
          + "\n/* ⚠ The filled part of a value bar, which is empty because its content is its\n"
            "   geometry — see VALUE_BARS. Left alone it is swept transparent by `ui: overlays`\n"
            "   and sits on a track `bg all` painted black, so the number it carries is simply\n"
            "   gone: a volume slider opened as a black rectangle. Only the level is coloured;\n"
            "   the track stays black, and yellow on black is the boundary back. */\n"
          + rule(wrap([VALUE_BAR_SELF, VALUE_BAR_KID], 1),
                 "background-color: %s" % YELLOW)),

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
    # ⚠ `filter: none` belongs to the same promise, and without it the grey is worse than
    # nothing.  `filter: brightness(0) invert(1)` is THE idiom for "make this icon white", and a
    # filter is applied to the element's own background as well as to its picture: brightness(0)
    # takes our grey to black, invert(1) takes it to white, and glyph and ground come out the
    # same colour.  What you see is a solid white square where the icon was — measured at
    # rgb(255,255,255), measured on a download button's icon.  CSS cannot select on a computed
    # filter, so
    # the answer is to make the ground's contract unconditional: every image sits on mid grey and
    # shows its own ink.  The cost is a page's own blur-up placeholders and drop-shadows, which
    # is cosmetic, against an icon that is simply gone, which is not.
    style("ui: image-ground",
          rule(guarded(["img", "picture", "object", "embed"], per_line=2),
               "background-color: #808080",
               "filter: none")
          + "\n/* An empty link is the other half of `an empty control's picture is its label`.\n"
            "   A wordmark drawn as an empty <a> with the PNG as its background, under a\n"
            "   CSS-in-JS hash for a class, gives ART no word to match at all: the name\n"
            "   heuristic has run out. Being empty and interactive is the whole tell.\n"
            "   And the grey has to come with it: that wordmark is dark navy, so handing the\n"
            "   picture back on black would leave it just as invisible. An empty link that has no\n"
            "   picture cannot show a grey box either — with no content it has no width to fill,\n"
            "   unless the page sized it, and a page only sizes an empty link to hold a picture. */\n"
          + rule(wrap([l + NEVER + ":empty" + NOT_ICONS for l in LINKS], 1),
                 "background-color: #808080")
          + "\n/* ⚠ And the picture has to be somewhere we can still see it. A card that stacks its\n"
            "   cover behind the layer over it — `position: relative; z-index: -1`, an everyday\n"
            "   idiom — is drawn at step 2 of its nearest ancestor stacking context, which is\n"
            "   <html> unless something between is positioned with a z-index of its own. The\n"
            "   grounds of ordinary blocks are drawn at step 3, above that: so every box we paint\n"
            "   between the picture and the root buries it, and <body> alone is enough. A\n"
            "   bookshop's search grid lost every cover to this and kept the text around them.\n"
            "   Isolating the PARENT is the whole repair, and the choice of element is the\n"
            "   argument: raising the picture's own z-index would lift a full-bleed backdrop over\n"
            "   the text it belongs behind, where a stacking context around its card traps it\n"
            "   there — above that card's ground, still below its siblings, and out of reach of\n"
            "   every ancestor. `isolation` rather than a z-index because it makes the context\n"
            "   without becoming a containing block for anything positioned inside it. */\n"
          + rule(MEDIA_PARENT, "isolation: isolate")),

    # background-color cannot remove a background *image*, so decorative gradients and banner
    # textures survive the blanket and keep painting pale bars across otherwise-black pages.
    #
    # The `:empty` restriction is what makes this safe enough to ship on. Unrestricted it erased
    # the jisho.org logo (`h1.logo a { background: url(…) }` behind hidden text) and every product
    # thumbnail in alza.cz's carousels; both are now provably spared — the logo because its <a>
    # holds text, the thumbnails because they are <img> and media is excluded — and the behavioural
    # test asserts each of them while this style is active.
    #
    # What it still cannot survive is content that genuinely IS an empty element with only a
    # background: alza.cz's rating histogram bars are empty 150x10 divs whose whole content is
    # `linear-gradient(270deg, #3cb2f5, #0094e7)`. Nothing distinguishes that from a decorative
    # strip, so alza.cz is seeded as an exclusion rather than pretending a cleverer selector
    # exists. That is also the answer to "shouldn't the site rule override the global one": Stylus
    # has no scope precedence — one author-origin cascade, specificity then injection order — and
    # `background-image: none` cannot be undone anyway, since `revert` lands on the UA value, which
    # is also none. "Global except here" is spelled with an exclusion.
    #
    # Earlier history, for the record: restricted to `:empty`, an unrestricted ancestor rule
    # also took pseudo-element overlays before `bg all` stopped painting those.
    # Controls are excluded here as well as in `ui: controls`, and the second exclusion is not
    # redundant: this style sweeps `:empty` elements, and an icon button is empty by definition,
    # so on its own it would go on erasing reCAPTCHA's reload and audio controls no matter what
    # `ui: controls` had decided. Which style is switched on is a per-profile matter, so the
    # carve-out has to hold in both.
    style("ui: strip-backdrops",
          rule("*:empty%s%s%s%s%s%s" % (NEVER, NOT_ICONS, NOT_MEDIA, NOT_CONTROLS,
                                        NOT_LINKS, NOT_ART),
               "background-image: none")
          ,
          [ALZA]),

    # Elements whose class says outright that they are a transparent layer over the page. Painting
    # one turns it into a sheet that hides everything beneath — the same failure as the ::before
    # overlays, and the reason a black bar appeared across the bottom of alza.cz.
    #
    # This is the ICONS heuristic applied again: match how the thing is named, not which site it
    # is on. The asymmetry justifies it — if the guess is wrong, a light scrim stays light, which
    # is cosmetic; if we paint one that should be transparent, page content disappears.
    #
    # A separate style rather than a :not() on the bg blankets, deliberately: adding a :not() there
    # would lift them from (1,0,0) to (1,1,0) and they would start outranking `ui: controls` at
    # (1,0,1). The doubled guard here puts this at (2,1,0), above every bg rule, and leaves the
    # ladder untouched.
    # `span[class*="ripple" i]` is the same thing wearing a component library's name. Material UI
    # ends every clickable with `<span class="MuiTouchRipple-root">` — absolutely positioned, inset
    # 0, pointer-events none, and the LAST child, so it paints over the item's own text and icon.
    # It blanked all 24 rows of alza.cz's category sidebar: `bg text` reaches it through `span` at
    # (1,0,1), `bg all` at (1,0,0), while `bg div` never did, which is what named it. Vuetify
    # (`v-ripple__container`) and Angular Material (`mat-ripple-element`) build theirs as spans too.
    # Kept to `span` on purpose: Material Components Web puts `mdc-ripple-upgraded` on the *button*,
    # which is a surface that should keep its ground, not a layer over one.
    # The third kind of layer carries no telltale class name and is found by structure instead: a
    # field's own floating label, absolutely positioned back across the input's text line. Painted
    # black it is a bar over the field, and the box swallows every keystroke in silence — you
    # type, and nothing appears. unherd.com's registration box is the case that named it, where
    # Piano draws `<p class=input-group><input><span class=placeholder><i class=icon-email>`.
    # Not one style's doing: `bg all` reaches that span at (1,0,0) and `bg text` at (1,0,1).
    #
    # Transparency is safe here in a way it is not elsewhere, and for a reason worth keeping hold
    # of: the control underneath is itself painted by `ui: controls`, so an unpainted label reveals
    # the field's own black, never the page behind it. The descendant term carries the leading
    # icon, which lives one level inside the label rather than beside it.
    style("ui: overlays",
          rule(guarded(['[class*="overlay" i]', '[class*="backdrop" i]', '[class*="scrim" i]',
                        'span[class*="ripple" i]'],
                       NEVER + NEVER, per_line=1),
               "background-color: transparent")
          + "\n/* a control's own floating label, and whatever it carries */\n"
          + rule("%s,\n%s *%s" % (ADORNMENT_SEL, ADORNMENT_SEL, NEVER),
                 "background-color: transparent")
          + "\n/* ⚠ The fourth kind of layer, and the one that blanks a page outright: an EMPTY\n"
            "   element left pinned over the viewport. Two sites went completely black on this,\n"
            "   every pixel of them: a notification host (fixed, inset 0, z-index 1060,\n"
            "   pointer-events none, no children) waiting for a toast that never comes, and a\n"
            "   consent gate emptied on accept but never removed. Neither carries a word this\n"
            "   style could match, and `pointer-events:none` hides such a layer from\n"
            "   elementsFromPoint too, so they only surface in a paint diff.\n"
            "   `:empty` is the discriminator, and it is the same one the rest of the file\n"
            "   already trusts: an element with no content has nothing of its own to make\n"
            "   legible, so painting it can only ever produce a sheet.\n"
            "   Every exclusion is load-bearing. Controls: at (1,3,1) this would outrank the\n"
            "   #808080 ground `ui: controls` gives an empty icon button. Media: <img>, <iframe>\n"
            "   and <video> are :empty by definition and `ui: image-ground` must survive. Links:\n"
            "   an empty link is a picture, treated just above. <hr>: void, so always :empty, and\n"
            "   `ui: borders` fills it yellow to draw the line. */\n"
          + rule("*:empty%s%s%s%s%s:not(hr)" % (NEVER, NOT_ICONS, NOT_MEDIA,
                                                NOT_CONTROLS, NOT_LINKS),
                 "background-color: transparent")
          + "\n/* ⚠ The fifth kind of layer, and the one the sweep above is built to miss: the\n"
            "   whole-card click target. One <a> laid across the tile at `position: absolute;\n"
            "   inset: 0; font-size: 0; color: transparent`, holding the accessible name and\n"
            "   nothing that draws. It is not :empty — that text node is the name — and links are\n"
            "   out of the sweep anyway, because an empty link is a wordmark. Painted, it boards\n"
            "   up the card: a bookshop's results kept a heart and a star rating and lost the\n"
            "   cover, the author, the title, the format and the price behind one black sheet.\n"
            "   The handle is that the link holds no picture of its own and lies beside one,\n"
            "   which is the card idiom everywhere it appears. Flat on both sides of the sibling\n"
            "   axis: the overlay is written before the content as often as after it, and `:has()`\n"
            "   may not be nested inside `:has()`. */\n"
          + rule(CARD_LINK_SEL, "background-color: transparent")
          + "\n/* ⚠ The sixth kind of layer: a strip of chrome pinned over the picture it drives.\n"
            "   A carousel's nav is one absolutely-positioned layer stretched over the whole\n"
            "   viewport of the carousel, `pointer-events: none` so the photo underneath stays\n"
            "   clickable, holding the prev and next buttons and nothing else. Painted, it boards\n"
            "   the photo up: a shop's product page came back with the main image, the thumbnail\n"
            "   row and two recommendation carousels gone — five black rectangles, every picture\n"
            "   on the page. Not :empty (it holds the two buttons) and named nothing a list could\n"
            "   match (`carousel-navs carousel-def car-load-hide abs`), so the structure is the\n"
            "   handle: it holds a control, holds nothing but controls, holds no picture, and lies\n"
            "   beside one. A box whose whole content is chrome has nothing of its own to make\n"
            "   legible — and the controls inside keep their own ground at (2,1,1) regardless. */\n"
          + rule(CONTROL_STRIP_SEL, "background-color: transparent")),

    # The doubled guard is not decoration: `ui: borders` sits at (1,1,0) now that it carves
    # the CSS triangles out, and a single guard here would tie with it and leave which of cyan
    # and yellow wins to injection order. At (2,1,0) the focus ring is above every border rule.
    style("ui: focus",
          rule(":focus-visible" + NEVER + NEVER,
               "outline: 2px solid %s" % CYAN,
               "outline-offset: 0")),

    # ⚠ The only style in the library that can reach inside a shadow root, and the reason it
    # exists.  A widget in a shadow tree is sealed against every rule above: Stylus injects into
    # the document, and document rules do not cross the boundary (it has no shadow-root injection
    # — style-injector.js writes to the page or to document.adoptedStyleSheets, both of which stop
    # at the host).  Two things do cross, because they are inherited: `color`, and custom
    # properties.  So a widget's OWN colour classes keep their light-theme values on our black
    # ground, and the text goes dark-on-dark.
    #
    # unherd.com's comment section is the case that named it — CoEditor mounts into
    # `<div id=my-comments><template shadowrootmode=open>`, and inside it `.text-foreground`
    # resolves to #0a0a0a on a host we have painted black.  Author names survived (no colour class
    # of their own, so they inherit our yellow through the host) while every comment body and
    # timestamp did not; measured at rgb(10,10,10) in 白い熊's screenshot.
    #
    # The repair is to move the tokens rather than the colours.  Tailwind v4 declares them on
    # :root — and `:root` inside a shadow stylesheet matches nothing, since a shadow tree has no
    # root element, so the values the widget reads are the DOCUMENT's, inherited in through the
    # host.  Setting them on <html> therefore lands inside the sealed tree.  Verified against the
    # saved page: overriding --foreground turns the shadow-DOM comment bodies yellow.
    #
    # What it cannot reach is a hard-coded arbitrary value — CoEditor's `Reply` is `#6a7282`
    # written into the class name, not a token, and it stays grey.  Legible on black, and there is
    # no route to it from outside the boundary.
    #
    # Excluded where the bg/fg blankets are already excluded: on those sites we are deliberately
    # not repainting, and moving the tokens would repaint by the back door.
    style("ui: design tokens",
          "/* surfaces */\n"
          + rule("html" + NEVER, *["%s: #000000" % t for t in TOKENS_SURFACE])
          + "\n/* the ink on them */\n"
          + rule("html" + NEVER, *["%s: %s" % (t, YELLOW) for t in TOKENS_INK])
          + "\n/* secondary text keeps a rank of its own rather than flattening to body yellow */\n"
          + rule("html" + NEVER, *["%s: %s" % (t, DIM_YELLOW) for t in TOKENS_DIM])
          + "\n/* borders, focus rings and the input outline — line colours, not fills */\n"
          + rule("html" + NEVER, *["%s: %s" % (t, YELLOW) for t in TOKENS_LINE]),
          [SUMO, CLAUDE, OWNCLOUD]),

    # Sites constrain article text to a narrow column with max-width; this hands the window back.
    # Media keeps its own max-width, which is what stops an oversized image overflowing.
    # max-width alone is not enough, and that took two archives to establish: substack.com pins its
    # column with `width: 728px; margin: 0 auto` and unherd.com with a Bootstrap `width: 960px`
    # grid column. Neither is a max-width, so both survived the first version of this style.
    #
    # The most invasive rule in the library — `width: auto` on every element that is not media, a
    # control or an icon — so it ships as an ALLOWLIST rather than globally: on only the two sites
    # where it has been measured, and nowhere else until 白い熊 adds a domain from the popup menu
    # (☰, then `1` on the domain row). Layouts that size a sidebar or a card explicitly change
    # shape under it, which is not a thing to inflict on every site by default.
    # `[style*="width"]` is excluded, and the reason is not cosmetic. An !important author rule
    # outranks a NON-important inline style, so `width: auto !important` beats
    # `style="width: 41px"` — and an absolutely-positioned empty div then shrink-to-fits to zero.
    # Any extension that draws overlays into the page and sizes them inline (highlighters,
    # annotation tools, region selectors, tooltips) loses its geometry that way, and the failure
    # looks like *that* extension is broken. Reported by the 白い熊 SurfingKeys session, whose
    # in-page search marks collapsed to 1px hairlines; measured here as width 41px -> 0px.
    #
    # Dropping `width: auto` and keeping only `max-width: none` was the other option offered, and
    # it does not work: substack.com pins its column with `width: 728px; margin: 0 auto`, which is
    # the case this style exists for. Neither page that prompted it was limited by max-width.
    style("ui: full-width",
          rule("*%s%s%s%s%s" % (NEVER, NOT_MEDIA, NOT_ICONS,
                                ":not(%s)" % ", ".join(CONTROLS),
                                ':not([style*="width"])'),
               "max-width: none")
          + "\n/* Split from the blanket above on purpose, and the asymmetry is the reason: lifting\n"
            "   an upper bound can only let a box grow, while `width` is the one that can shrink it\n"
            "   to nothing. So max-width is released everywhere and the width release stops beside a\n"
            "   framed picture, where a shut drawer would otherwise open and take the whole row.\n"
            "   It stops at a value bar for the same kind of reason and a stronger one: a volume\n"
            "   slider's width IS its reading, and `!important` beats the page's non-important\n"
            "   `:hover` rule asking for 100px however specific that rule is, so the bar could\n"
            "   never open again: it sat pinned at the content width of an empty div, nothing. */\n"
          + rule("*%s%s%s%s%s%s%s" % (NEVER, NOT_MEDIA, NOT_ICONS,
                                      ":not(%s)" % ", ".join(CONTROLS),
                                      ':not([style*="width"])',
                                      NOT_FRAME_NEIGHBOUR, NOT_VALUE_BAR),
               "width: auto")
          + "\n/* A flex item pinned by flex-basis ignores width. Restricted to :only-child, which\n"
            "   is what makes it safe: a lone column growing to fill its row cannot disturb a\n"
            "   multi-column layout, because there is no second column. unherd.com's article sits\n"
            "   in a flex row of exactly one child at `flex: 0 0 50%`, beside 960px of nothing. */\n"
          + rule("*:only-child%s%s%s%s" % (NEVER, NOT_MEDIA, NOT_ICONS,
                                           ":not(%s)" % ", ".join(CONTROLS)),
                 "flex-grow: 1")
          + "\n/* Releasing every column would leave the text hard against the window edge, so the\n"
            "   page keeps a gutter. On <body> rather than on the text elements, so it reads as a\n"
            "   page margin instead of an indent stacking onto whatever padding a card already has. */\n"
          + rule("body" + NEVER,
                 "padding-left: 1em",
                 "padding-right: 1em"),
          only_on=[SUBSTACK, UNHERD]),

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
    # unherd.com sizes the article with a Bootstrap `flex: 0 0 50%` in a row that only adds up to
    # 75% — a 25% tag sidebar, the 50% article, and 25% of nothing. No width or max-width rule can
    # reach that, and growing every flex item globally would wreck layouts with a deliberately
    # fixed sidebar, so the article column is grown here instead. It takes the free quarter and
    # ends at 75%; going to 100% would mean hiding the tag column, which is content.
    style("site: unherd.com",
          rule(wrap([".col-sm-8" + NEVER + NEVER, ".col-lg-6" + NEVER + NEVER], 1),
               "flex-grow: 1")
          + "\n/* and the tag column beside it, so the article takes the whole row. Scoped to the\n"
            "   article row: the same Bootstrap classes carry real content elsewhere on the site. */\n"
          + rule(".article-body.row > .col-lg-3" + NEVER, "display: none"),
          domains=["unherd.com"]),

    style("site: casopisargument.cz",
          rule(wrap(["*", "*::before", "*::after"], 3), "font-size: 16px")
          + "\n" + rule(wrap(EVERY), "font-size: 16px"),
          domains=["casopisargument.cz"]),
    # pre/code colour is global now; only the block metrics remain site-specific
    # The pale band across the product page is a section texture: #detailItem carries
    # background-image: url(.../sectbgr.png), and background-color cannot remove a background
    # *image*. No global rule can fix this class of thing — CSS gives no way to tell a decorative
    # texture from a logo or a thumbnail drawn the same way — so it is treated where it lives.
    # Two elements on alza that no global rule can handle, for the same underlying reason: CSS
    # cannot see what an element is *for*. #detailItem is a page section carrying a texture image
    # that background-color paints behind, never over. #fixedBottom is a transparent,
    # pointer-events:none container pinned to the bottom purely to host floating widgets — giving
    # it a background turns it into a 64px black band across every page.
    #
    # Both carry the NEVER guard: at (2,0,0) they clear `bg div` at (1,0,1). An id alone would be
    # (1,0,0) and would lose.
    style("site: alza.cz",
          rule("#detailItem" + NEVER, "background-image: none")
          + "\n"
          # .fabs-row is a third transparent, pointer-events:none host. Found by toggling our own
          # stylesheets inside 白い熊's saved archive and listing every wide element that flipped to
          # opaque black — it was the only one carrying pointer-events:none.
          + rule(wrap(["#fixedBottom" + NEVER,
                       ".js-cookies-info" + NEVER + NEVER,
                       ".fabs-row" + NEVER + NEVER], 1),
                 "background-color: transparent"),
          domains=["alza.cz"]),
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
