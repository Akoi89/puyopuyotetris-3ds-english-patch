"""2026-09-15: fix two stale bundle readmes in place.

JP bundle: the 13 Sep Azahar paragraph said the edition was 'not yet on a
console' and asked readers to confirm Japanese speech, which TheGershon
confirmed on a New 3DS XL on 14 Sep (issue #2). Also corrects '1.0.13 not yet
booted anywhere' (it was checked in Azahar) and notes the two 1.0.14 bubbles
are unchecked in the engine.

EN bundle: names ongo_gablogian and Partyderp64 in the credit paragraph, which
README.md and RHDN 7714 already do.

The xdelta members are copied through byte for byte; only README.md changes.
"""
import zipfile, hashlib, io, os, re, sys

CUR = 'Final/_CURRENT'

JP_OLD = """**Booted in Azahar on 13 September 2026** (base and DLC, with the Japanese
v1.2.0 update installed): the title screen reads ENG 1.0.12, the main menu
and Quick Play run with audio, and DLC EX Act 10 opens with its English plate
and an English story scene. What that run could not check is the language of
the voices themselves; that rests on the file comparison above, where every
voice file is byte for byte Sega's. Not yet on a console. If you try it, the
first things worth confirming are that a battle and a DLC chapter play Japanese
speech under the English text."""

JP_NEW = """**Booted in Azahar on 13 September 2026** (base and DLC, with the Japanese
v1.2.0 update installed, on what was then the 1.0.12 build): the main menu
and Quick Play ran with audio, and DLC EX Act 10 opened with its English plate
and an English story scene. What that run could not check is the language of
the voices themselves.

**Confirmed on a New 3DS XL on 14 September 2026.** A player installed this
edition by the xdelta route and heard Japanese speech under the English text,
in story scenes and in play, across a couple of DLC Adventure chapters. That
was the 1.0.12 build of this edition; 1.0.13 and 1.0.14 changed only text
tables, one texture and two script bytes, so every voice file is the one they
heard."""

JP_OLD2 = """letter per sprite instead of slices. Not yet booted anywhere; the change is
line breaks in three text tables and one texture, each verified byte for byte
on the way in and out of the CIAs."""

JP_NEW2 = """letter per sprite instead of slices. Checked in Azahar on the EX Act 8 and
EX Act 10 scenes; the change is line breaks in three text tables and one
texture, each verified byte for byte on the way in and out of the CIAs."""

JP_OLD3 = """1.0.14 (2026-09-14) raises two speech bubbles in the base game that were
scripted for fewer lines than the English text needs. The DLC is unchanged from
0.2.8."""

JP_NEW3 = """1.0.14 (2026-09-14) raises two speech bubbles in the base game that were
scripted for fewer lines than the English text needs; those two have not been
looked at in the engine yet. The DLC is unchanged from 0.2.8."""

EN_OLD = """The English text and voices are Sega's, from the Steam release of Puyo Puyo
Tetris. The earlier fan translation carried the Adventure story across and
did the first pass of the UI texture work."""

EN_NEW = """The English text and voices are Sega's, from the Steam release of Puyo Puyo
Tetris. The earlier fan translation, ongo_gablogian's, with Partyderp64's
PPT3dsENG_0.3dx build, carried the Adventure story across and did the first
pass of the UI texture work."""


def edit(text, pairs):
    for old, new in pairs:
        pat = re.compile(r"\r?\n".join(re.escape(l) for l in old.split("\n")))
        n = len(pat.findall(text))
        if n != 1:
            sys.exit("ANCHOR FAIL count=%d for: %r" % (n, old[:60]))
        text = pat.sub(lambda m: new.replace("\n", "\r\n"), text, count=1)
    return text


JOBS = [
    ("PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip",
     [(JP_OLD, JP_NEW), (JP_OLD2, JP_NEW2), (JP_OLD3, JP_NEW3)],
     "rhdn_bundle_README_JP-voices_1.0.14.md"),
    ("PuyoPuyoTetris-xdelta-patches-1.0.14.zip",
     [(EN_OLD, EN_NEW)],
     "rhdn_bundle_README_1.0.14.md"),
]

for zname, pairs, curname in JOBS:
    zp = os.path.join(CUR, zname)
    zin = zipfile.ZipFile(zp)
    members = [(i.filename, zin.read(i.filename)) for i in zin.infolist()]
    zin.close()
    before = {fn: hashlib.sha256(d).hexdigest() for fn, d in members}

    out = []
    for fn, data in members:
        if fn == "README.md":
            t = data.decode("utf-8")
            t2 = edit(t, pairs)
            bad = sorted({hex(ord(c)) for c in t2 if ord(c) > 126})
            if bad:
                sys.exit("NON-ASCII in %s: %s" % (zname, bad))
            data = t2.encode("utf-8")
            print("%s  README.md %d -> %d bytes" % (zname, len(t.encode()), len(data)))
        out.append((fn, data))

    for fn, data in out:
        if fn != "README.md":
            assert hashlib.sha256(data).hexdigest() == before[fn], fn
    print("   patches copied through unchanged: "
          + ", ".join(fn for fn, _ in out if fn != "README.md"))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fn, data in out:
            z.writestr(fn, data)
    blob = buf.getvalue()
    open(zp, "wb").write(blob)
    open(os.path.join(CUR, curname), "wb").write(dict(out)["README.md"])
    print("   %s  %d B  sha256 %s" % (zname, len(blob), hashlib.sha256(blob).hexdigest()))

print("OK")
