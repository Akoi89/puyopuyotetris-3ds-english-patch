First build of the completed English patch. **Nothing has been booted** — every file is verified byte-for-byte, none of it on a screen. See TESTING.md.

- **`PuyoPuyoTetris-Update-patched.cia`** — the translation packaged as the game's update title (`0004000E`): Sega's v1.2.0 update code with the English game data appended. Installs over the official update; the Japanese base game is left untouched. ~99% of displayed text, all 37 characters' in-battle voices, the online UI textures. Title screen reads **ENG 1.0.0**; the console shows the update as 1.3.0.
- **`PuyoPuyoTetris-DLC-patched.cia`** — three story chapters, text and voices (760 of 763 clips), 33 shop icons. TMD 0.2.0.
- `PuyoPuyoTetris-LayeredFS.zip` — the changed files alone for Luma3DS, if you would rather keep the official update.
- Install order: Japanese base → update CIA → DLC CIA.

The Japanese base game is not distributed here and is never modified. A full patched base CIA can be built locally with `tools/build_cia.py`, but the update CIA makes that unnecessary.
