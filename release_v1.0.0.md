The completed English patch. This release tag is v1.0.0; the assets on it are replaced in place with each build, and the current one is **1.0.8** (see below). **Nothing has been booted on real hardware**: every file is verified byte-for-byte; base and DLC have been booted in Azahar and the English shows in the engine. See TESTING.md, and report problems in [issue #1](../../issues/1).

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.0.8**; the built CIA reports 1.0.8.
- **`PuyoPuyoTetris-DLC-patched.cia`**: three story chapters, text and voices (760 of 763 clips), 33 shop icons and the three EX chapter plates. TMD 0.2.5.
- Install order: Japanese base → patched base (or LayeredFS) → Japanese v1.2.0 update (code only) → this DLC.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folded in a second-opinion review of the hand-written text; 1.0.8 (below) is the current build.

---

## Current build: 1.0.8

The build has moved on from 1.0.1 through 1.0.6 above. **Booted in the
Azahar emulator**: base and DLC both run, and the text pipeline works in the
engine: checked on the Options screen, the Adventure map, the DLC chapters,
and the Versus result screen, all in English. Real hardware is still
untested.

1.0.2 (below) added a full texture survey, a second label pass, and two more
imported voice sets. 1.0.3 fixed the character-select pick lines, the
title-screen announcer, the boot notice screen, the DLC map plates, and the
Endless-mode record card. 1.0.4 fixed the bottom-screen boot notice column,
refit the DLC map plates in a condensed font, and re-encoded all 37 battle
banks to Sega's sample rate. 1.0.5 fixed the match-end hang by compacting the
font atlases. 1.0.6 replaced the Swap-mode call logos with Sega's official
English logo art and moved the bottom-screen boot notice text a further 21
px left. 1.0.7 replaced the Swap-mode call logos and moved the boot notice text; 1.0.8:

- **A sweep of the Steam release's English textures for Sega's official
  art.** Because Steam's English atlases are laid out differently from both
  the 3DS atlases and Steam's own Japanese atlases, sprites are matched by
  their text instead of their position. 222 hand-redrawn labels are replaced
  with Sega's official English sprites, including the Broadcast Station and
  Club mode pills (Fusion, Swap, Party, Big Bang, Marathon, Sprint, Ultra,
  Endless Puyo, Endless Fever, Tiny Puyo) with their proper two-tone
  outlines, coloured category rows, Yes/No buttons, and Puzzle League
  headers. Labels where the Steam sprite would be unreadable or clash in
  style keep the hand redraw.
- **The Replay Report badge rows (all 11)** are now Sega's official English
  art: Epic Showdown!, Master Battle!, Regional Battle!, Must Watch!, Major
  Upset!, Amazing Match!, Huge Comeback!, Back-n-Forth!, Surprise Win!, Great
  Match!, Rank Up!
- **The 15 Puzzle League rank pills** (Grand Master, Platinum, Golden,
  Legend, Superstar, Star, Virtuoso, Elite, Professional, Wizard, Ace,
  Amateur, Rookie, Beginner, Student) are now Sega's official English art;
  these were still Japanese and hadn't previously been listed as a known
  leftover.
- **The Broadcast Station TV logo** is now Sega's official "World Broadcast"
  mark. Earlier notes called this the "Replay TV" logo and said it was
  artwork left Japanese; that isn't true any more.
- **Base game**: title screen now reads **ENG 1.0.7**; the built CIA reports
  1.0.7.
- **`PuyoPuyoTetris-DLC-patched.cia`** stays **TMD 0.2.4**.

1.0.8 fixed the in-battle and DLC voice loudness, reported as quiet next
to the story voices:

- Measured with `voice_levels.py` (peak and RMS in dBFS): Sega's Japanese
  3DS takes run about -11 dBFS RMS with peaks near 0 dBFS (heavily
  limited); the imported base voice clips sat 5 to 11 dB below that in
  RMS, and the DLC story clips about 7 dB low, in both cases with peaks
  already close to full scale, so a flat gain would have clipped.
- Fix: gain each clip to the RMS of Sega's Japanese take of the same line
  through a look-ahead peak limiter, then re-encode. Base battle/select/
  title voices now average 1.2 dB below Sega's takes (62 of 63 banks
  re-levelled); DLC story clips about 1.3 dB below (734 clips
  re-levelled). Pitch and timing untouched.
- **Base game**: title screen now reads **ENG 1.0.8**; the built CIA
  reports 1.0.8.
- **`PuyoPuyoTetris-DLC-patched.cia`** is now **TMD 0.2.5**.
- Nothing else changed: text, textures and atlases are as in 1.0.7.
- Still Japanese, deliberately or not yet: a few merged/rotated strings on
  the league result screen (vertical "you lose"/"congratulations" art), the
  replay-speed hint strip (not found anywhere in the Steam data), the three
  DLC voice lines with no English take, decorative screenshot thumbnails,
  and the small "New Record" ornament.
- One stability report from testing, recorded honestly: starting a local
  Multiplayer host and backing out crashed the emulator (an emulator-side
  assertion, not the patch).
- Install order is unchanged: Japanese base, then patched base (or
  LayeredFS), then the Japanese v1.2.0 update (code only), then this DLC.
  The withdrawn update-title CIA note above still applies: do not use it.
