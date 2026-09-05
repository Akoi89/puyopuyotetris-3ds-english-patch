First build of the completed English patch. **Nothing has been booted on hardware** — every file is verified byte-for-byte; the base build has been booted in Azahar only far enough to prove the files load. See TESTING.md.

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.0.1**; the built CIA reports 1.0.1.
- **`PuyoPuyoTetris-DLC-patched.cia`** — three story chapters, text and voices (760 of 763 clips), 33 shop icons. TMD 0.2.0.
- Install order: Japanese base → patched base (or LayeredFS) → Japanese v1.2.0 update (code only) → this DLC.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folds in a second-opinion review of the hand-written text.
