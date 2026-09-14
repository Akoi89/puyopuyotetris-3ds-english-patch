"""On-screen width model for the Adventure speech bubble, fitted 2026-09-14 against TheGershon's
four 400x240 captures (issue #1):

    screen_px = sum over non-space glyphs of (bearing + advance) from the FONTDATF record
                + SPACE_PX per space          (the atlas space record says width 1; the game draws ~10)

Residuals on the four captures with SPACE_PX=10: -7, -17, -13, -2 px (model over-predicts, i.e. safe side).
Bubble text room: text starts at x=118, inner border at ~333 -> 215 px. LIMIT leaves a margin.
"""
SPACE_PX = 10
LIMIT = 205            # on-screen px, the wrap target
ROOM = 215             # on-screen px actually available (informational)


def screen_width(a, line):
    pen = 0
    for c in line:
        if c == ' ':
            pen += SPACE_PX; continue
        cp = ord(c)
        if cp not in a['widths']:
            pen += a['cw']; continue
        b, w = a['widths'][cp]
        pen += (b + w) if w else a['cw']
    return pen
