First build of the completed English patch. **Nothing has been booted on hardware**: every file is verified byte-for-byte; base and DLC have been booted in Azahar and the English shows in the engine. See TESTING.md.

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.0.3**; the built CIA reports 1.0.3.
- **`PuyoPuyoTetris-DLC-patched.cia`**: three story chapters, text and voices (760 of 763 clips), 33 shop icons and the three EX chapter plates. TMD 0.2.2.
- Install order: Japanese base → patched base (or LayeredFS) → Japanese v1.2.0 update (code only) → this DLC.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folded in a second-opinion review of the hand-written text; 1.0.3 (below) is the current build.

---

## Current build: 1.0.3

The build has moved on from 1.0.1 and 1.0.2 above. **Booted in the Azahar
emulator**: base and DLC both run, and the text pipeline works in the
engine: checked on the Options screen, the Adventure map, and the DLC
chapters, all in English. Real hardware is still untested.

1.0.2 (below) added a full texture survey, a second label pass, and two more
imported voice sets. 1.0.3 fixes five things the user found playing 1.0.2 in
Azahar on 2026-09-04:

- **Base game**: title screen now reads **ENG 1.0.3**; the built CIA reports
  1.0.3.
- **Character-select pick lines**: the fan patch had replaced only 15 of the
  24; all 24 are now from Steam's English pick bank, verified by duration
  match 24 of 24.
- **The title-screen announcer at boot** (sound bank 143, four takes) was a
  3DS-only bank; Steam's title_set_bank matched all four takes by duration,
  so the English takes are in.
- **The boot notice screen** was cut off on screen because the game shows
  only the left part of the texture; it is re-wrapped into the 290 px column
  the Japanese occupied.
- **The DLC map plates** were cut off for the same reason; the English is
  now fitted into the measured Japanese ink window (the long names are
  small, 8 to 9 px).
- **The Endless-mode record card** ("Best Record", "This Run", "beaten"
  after the count) is redrawn by a dedicated script that inpaints the
  gradient plates.
- **`PuyoPuyoTetris-DLC-patched.cia`** is now **TMD 0.2.2**.
- Still Japanese, deliberately or not yet: a few merged/rotated strings on
  the league result screen (vertical "you lose"/"congratulations" art), the
  replay-speed hint strip, the Swap-mode Puyo/Tetris logos, decorative
  screenshot thumbnails, the small "New Record" ornament, and the Broadcast
  Station category badge rows on the Replay Report.
- Install order is unchanged: Japanese base → patched base (or LayeredFS) →
  Japanese v1.2.0 update (code only) → this DLC. The withdrawn update-title
  CIA note above still applies: do not use it.
