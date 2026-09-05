First build of the completed English patch. **Nothing has been booted on hardware**: every file is verified byte-for-byte; base and DLC have been booted in Azahar and the English shows in the engine. See TESTING.md.

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.0.4**; the built CIA reports 1.0.4.
- **`PuyoPuyoTetris-DLC-patched.cia`**: three story chapters, text and voices (760 of 763 clips), 33 shop icons and the three EX chapter plates. TMD 0.2.3.
- Install order: Japanese base → patched base (or LayeredFS) → Japanese v1.2.0 update (code only) → this DLC.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folded in a second-opinion review of the hand-written text; 1.0.4 (below) is the current build.

---

## Current build: 1.0.4

The build has moved on from 1.0.1, 1.0.2 and 1.0.3 above. **Booted in the
Azahar emulator**: base and DLC both run, and the text pipeline works in the
engine: checked on the Options screen, the Adventure map, and the DLC
chapters, all in English. Real hardware is still untested.

1.0.2 (below) added a full texture survey, a second label pass, and two more
imported voice sets. 1.0.3 fixed the character-select pick lines, the
title-screen announcer, the boot notice screen, the DLC map plates, and the
Endless-mode record card, and moved the DLC CIA to TMD 0.2.2. 1.0.4 fixes
three more things the user found playing 1.0.3 in Azahar on 2026-09-04:

- **Base game**: title screen now reads **ENG 1.0.4**; the built CIA reports
  1.0.4.
- **The boot notice screen was still cut off on the bottom screen**: it shows
  a narrower window of the texture than the top screen does, and each half
  now has its own fitted column.
- **The DLC map plates** were width-fitted in a wide font and came out short
  next to Sega's own "Act 1" plate. They now use a condensed font with
  Sega's dark-green outline, fitted by height instead.
- **Sound**: the 13 battle banks the earlier fan translation had already made
  English carried odd per-wave sample rates against Sega's. All 13 are
  re-imported from Steam at Sega's rate, so all 37 battle banks are now this
  project's own encode, verified.
- **`PuyoPuyoTetris-DLC-patched.cia`** is now **TMD 0.2.3**.
- Still Japanese, deliberately or not yet: a few merged/rotated strings on
  the league result screen (vertical "you lose"/"congratulations" art), the
  replay-speed hint strip, the Swap-mode Puyo/Tetris logos, decorative
  screenshot thumbnails, the small "New Record" ornament, and the Broadcast
  Station category badge rows on the Replay Report.
- Two stability reports from testing, recorded honestly: a local Multiplayer
  host crashed the emulator on backing out (an emulator-side assertion, not
  the patch), and a solo match hung once at match end with nothing logged;
  cause unknown, worth reporting if it repeats.
- Install order is unchanged: Japanese base → patched base (or LayeredFS) →
  Japanese v1.2.0 update (code only) → this DLC. The withdrawn update-title
  CIA note above still applies: do not use it.
