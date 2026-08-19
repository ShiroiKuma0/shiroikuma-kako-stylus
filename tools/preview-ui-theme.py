#!/usr/bin/env python3
"""Static previews of the house theme for 白い熊 Stylus' own windows.

The extension's pages cannot be opened from the filesystem — they call chrome APIs on load — so
these rebuild just enough DOM by hand and link the *built* stylesheets, which is what actually
decides how the theme looks.  Run `pnpm build-firefox` first, then:

  python3 tools/preview-ui-theme.py
  firefox --headless --profile "$PWD/.scratch/ffprof" --window-size=440,760 \
    --screenshot "$PWD/.scratch/popup-theme.png" "file://$PWD/dist-firefox-mv2/_preview.html"
  firefox --headless --profile "$PWD/.scratch/ffprof" --window-size=760,480 \
    --screenshot "$PWD/.scratch/cm-theme.png" "file://$PWD/dist-firefox-mv2/_preview-cm.html"

Delete the two `_preview*.html` from dist before packaging — build-fork.mjs does not know them.
"""
import os, re, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def popup():
    DIST = "dist-firefox-mv2"
    html = open(os.path.join(DIST, "popup.html"), encoding="utf-8").read()
    html = html.replace('href="/css/', 'href="css/').replace('src="/js/', 'src="js/')
    html = re.sub(r'<script[^>]*src="[^"]*"[^>]*>\s*</script>', '', html)
    html = html.replace('<html id="stylus">',
                        '<html id="stylus" data-ui-theme="dark" class="desktop non-touch firefox mv2">')
    
    BOOT = """
    <script>
    const names = ['bg all','bg blocks','bg div','bg ground','bg text','fg all','fg blocks','fg div',
      'fg ground','fg text','line-height','sans-serif','text-align','ui: controls','ui: focus',
      'ui: links'];
    document.body.append(document.querySelector('template[data-id="body"]').content.cloneNode(true));
    const tpl = document.querySelector('template[data-id="style"]');
    const installed = document.getElementById('installed');
    names.forEach((n, i) => {
      const frag = tpl.content.cloneNode(true);
      const entry = frag.querySelector('.entry');
      entry.id = 'style-' + i;
      if (i === 7) entry.classList.add('not-applied');
      const inp = frag.querySelector('.style-name input');
      inp.checked = i !== 7;
      frag.querySelector('.style-name').append(document.createTextNode(n));
      installed.append(frag);
    });
    document.documentElement.classList.remove('no-styles');
    document.querySelectorAll('[i18n]').forEach(el => {
      const v = el.getAttribute('i18n');
      if (v.startsWith('+') || !v.includes(':')) el.textContent ||= v.replace(/^\\+/, '');
    });
    document.getElementById('write-style').textContent = 'Write style for: example.com';
    document.getElementById('fork-version').textContent = '2.4.10.13';
    </script>
    """
    html = html.replace("</body>", BOOT + "</body>")
    out = os.path.join(DIST, "_preview.html")
    open(out, "w", encoding="utf-8").write(html)
    print(out)


def codemirror():
    TOKENS = [
        ('cm-comment', '/* a comment */'), None,
        ('cm-keyword', '@media'), ('', ' '), ('cm-string', '"screen"'), ('', ' {'), None,
        ('', '  '), ('cm-tag', 'div'), ('cm-qualifier', '.card'), ('cm-builtin', '#main'),
        ('cm-attribute', '[data-x]'), ('', ' {'), None,
        ('', '    '), ('cm-property', 'background-color'), ('cm-operator', ':'), ('', ' '),
        ('cm-atom', 'black'), ('', ' '), ('cm-keyword', '!important'), ('', ';'), None,
        ('', '    '), ('cm-property', 'line-height'), ('cm-operator', ':'), ('', ' '),
        ('cm-number', '1em'), ('', ';'), None,
        ('', '    '), ('cm-variable-2', '--sk-fg'), ('cm-operator', ':'), ('', ' '),
        ('cm-atom', '#ffff00'), ('', ';'), None,
        ('', '    '), ('cm-error', 'colour'), ('cm-operator', ':'), ('', ' '),
        ('cm-atom', 'yellow'), ('', ';'), None,
        ('', '  '), ('cm-bracket', '}'), None, ('cm-bracket', '}'), None,
    ]
    rows, cur = [], []
    for t in TOKENS:
        if t is None:
            rows.append(''.join(cur) or '&nbsp;'); cur = []
        else:
            cls, txt = t
            txt = txt.replace('&','&amp;').replace('<','&lt;').replace(' ','&nbsp;')
            cur.append('<span class="%s">%s</span>' % (cls, txt) if cls else txt)
    body = ''.join('<div class="CodeMirror-line">%s</div>' % r for r in rows)
    html = """<!doctype html>
    <html id="stylus" data-ui-theme="dark" class="desktop non-touch firefox mv2">
    <head><meta charset="utf-8">
    <link href="css/common.css" rel="stylesheet">
    <link href="css/codemirror.css" rel="stylesheet">
    <link href="css/edit.css" rel="stylesheet">
    </head><body style="padding:16px">
    <h1>editor palette — cm-s-default on the house theme</h1>
    <div class="CodeMirror cm-s-default" style="padding:10px;height:auto">
     <div class="CodeMirror-code" style="font-family:monospace">%s</div>
    </div>
    <p>Body text sits at the base font size. <a href="#">A link.</a>
    <button>A button</button> <input value="an input"> <select><option>a select</option></select></p>
    </body></html>""" % body
    open("dist-firefox-mv2/_preview-cm.html", "w", encoding="utf-8").write(html)
    print("dist-firefox-mv2/_preview-cm.html")


popup()
codemirror()
