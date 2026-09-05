First build of the completed English patch. **Nothing has been booted on hardware** — every file is verified byte-for-byte; base and DLC have been booted in Azahar and the English shows in the engine. See TESTING.md.

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.0.2**; the built CIA reports 1.0.2.
- **`PuyoPuyoTetris-DLC-patched.cia`** — three story chapters, text and voices (760 of 763 clips), 33 shop icons and the three EX chapter plates. TMD 0.2.1.
- Install order: Japanese base → patched base (or LayeredFS) → Japanese v1.2.0 update (code only) → this DLC.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folded in a second-opinion review of the hand-written text; 1.0.2 (below) is the current build.

---

## Current build: 1.0.2

The build has moved on from 1.0.1 above. **Booted in the Azahar emulator**:
base and DLC both run, and the text pipeline works in the engine — checked on
the Options screen, the Adventure map, and the DLC chapters, all in English.
Real hardware is still untested.

- **Base game**: title screen now reads **ENG 1.0.2**; the built CIA reports
  1.0.2. A full texture survey (`survey2.py` + `tex.py`, covering every CTPK
  format plus Sega's COMP container, which turned out to be plain Nintendo
  LZ11 with a 16-byte texture header) found many Japanese textures the first
  pass missed — mostly in-game HUD art that lived in COMP-wrapped archives
  the first survey never opened. A second label pass redrew roughly 480 more
  labels: the Internet hub menu and its region/prefecture picker, the Options
  prefecture list, the local Multiplayer Arcade card labels, the
  Theatre/Broadcast Station category badges, the online Replay Report
  screen, the Endless-mode in-game banners and stat labels, the Adventure
  in-game "Game Start" plate, the attract-demo ranking screen, the Party item
  call-outs and "Time Up", the character-unlock notice, the Puyo-side pause
  menus and spice-level labels, in-game Puyo call-outs (Garbage Puyo Clear,
  Freeze, Field Swap, Synchro Chain, Reach, and more), the Endless/Challenge
  mode title cards, the league and Club result screens, and the system
  save-delete dialogs. The boot notice screen is also redrawn in English now.
  Two more voice sets were imported from Steam: the per-character title calls
  heard at launch and the character-select confirm lines, so the launch
  "Sega / Puyo Puyo Tetris" call and the character-select lines are now
  English too.
- **`PuyoPuyoTetris-DLC-patched.cia`** is now **TMD 0.2.1**: the three EX
  chapter plates on the Adventure map read "EX Act 8/9/10" and Sega's own
  chapter names — "A Suzuran Dream", "A Primp Dream", "An Interstellar
  Dream".
- Still Japanese, deliberately or not yet: a few merged/rotated strings on
  the league result screen (vertical "you lose"/"congratulations" art), the
  replay-speed hint strip, the Swap-mode Puyo/Tetris logos, decorative
  screenshot thumbnails, the small "New Record" ornament, and the Broadcast
  Station category badge rows on the Replay Report.
- Install order is unchanged: Japanese base → patched base (or LayeredFS) →
  Japanese v1.2.0 update (code only) → this DLC. The withdrawn update-title
  CIA note above still applies — do not use it.
