First build of the completed English patch. **Nothing has been booted on hardware**: every file is verified byte-for-byte; base and DLC have been booted in Azahar and the English shows in the engine. See TESTING.md.

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.0.5**; the built CIA reports 1.0.5.
- **`PuyoPuyoTetris-DLC-patched.cia`**: three story chapters, text and voices (760 of 763 clips), 33 shop icons and the three EX chapter plates. TMD 0.2.4.
- Install order: Japanese base → patched base (or LayeredFS) → Japanese v1.2.0 update (code only) → this DLC.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folded in a second-opinion review of the hand-written text; 1.0.5 (below) is the current build.

---

## Current build: 1.0.5

The build has moved on from 1.0.1 through 1.0.4 above. **Booted in the
Azahar emulator**: base and DLC both run, and the text pipeline works in the
engine: checked on the Options screen, the Adventure map, the DLC chapters,
and the Versus result screen, all in English. Real hardware is still
untested.

1.0.2 (below) added a full texture survey, a second label pass, and two more
imported voice sets. 1.0.3 fixed the character-select pick lines, the
title-screen announcer, the boot notice screen, the DLC map plates, and the
Endless-mode record card. 1.0.4 fixed the bottom-screen boot notice column,
refit the DLC map plates in a condensed font, and re-encoded all 37 battle
banks to Sega's sample rate. 1.0.5 fixes the biggest issue found so far:

- **The match-end hang is found and fixed.** Versus matches were hanging at
  the win/lose screen; Marathon never hung. The cause was the font-atlas
  fix from earlier builds: it had replaced incomplete atlas members with
  whole donor atlases up to four times their needed size, and the Versus
  result screen loads three of those members at once. A new tool,
  `atlas_compact.py`, now subsets every swapped member down to only the
  glyphs its section uses, cutting the affected atlas bitmaps by roughly
  three quarters. The user played Versus matches on the fixed build with no
  hang, and the winner dialogue rendered in English.
- **Base game**: title screen now reads **ENG 1.0.5**; the built CIA reports
  1.0.5.
- **The version stamp on the title logo** is a little taller and easier to
  read.
- **The bottom-screen notice** shifted slightly left.
- An attempt at redrawing the Swap-mode "Puyo Puyo"/"Tetris" call banners was
  tried and reverted; that art stays Sega's.
- **`PuyoPuyoTetris-DLC-patched.cia`** is now **TMD 0.2.4**.
- Still Japanese, deliberately or not yet: a few merged/rotated strings on
  the league result screen (vertical "you lose"/"congratulations" art), the
  replay-speed hint strip, the Swap-mode Puyo/Tetris logos, decorative
  screenshot thumbnails, the small "New Record" ornament, and the Broadcast
  Station category badge rows on the Replay Report.
- One stability report from testing, recorded honestly: starting a local
  Multiplayer host and backing out crashed the emulator (an emulator-side
  assertion, not the patch).
- Install order is unchanged: Japanese base, then patched base (or
  LayeredFS), then the Japanese v1.2.0 update (code only), then this DLC.
  The withdrawn update-title CIA note above still applies: do not use it.
