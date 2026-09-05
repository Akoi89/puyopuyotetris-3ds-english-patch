# Puyo Puyo Tetris: 3DS English patch

**Sega's official English text and voices, from the Steam release of *Puyo Puyo
Tetris*, carried onto the Japanese Nintendo 3DS release, including the DLC.**

*Puyo Puyo Tetris* (3DS, 2014) never had an English release. Sega localized the
game for PC and consoles in 2017 but never brought that text back to the
handheld. An earlier fan translation carried the Adventure story across but left
the online menus, the prologue, the error dialogs, the shop, most of the in-battle
character voices, the DLC chapters and every texture label in Japanese.

This finishes it: about 99% of displayed text, all 37 characters' in-battle
voices, all three DLC story chapters (text and voices), the online UI textures,
and the DLC shop icons.

> ### Playtesters wanted
>
> **Nothing here has been booted yet** — not on hardware, not in an emulator.
> Every file was verified byte-for-byte on the way in and back out of the
> packages, and every writer reproduces the game's own files byte-identically,
> but that is verification, not testing. If you are the first to boot it, that
> alone is worth reporting.
>
> **[Report anything wrong in issue #1](../../issues/1)** — which screen, and a
> photo beats a description. See **[TESTING.md](TESTING.md)** for what to
> install, how to identify the build, and what is known.

> **You need the Japanese base game.** It is not distributed here or anywhere
> in this project. Cartridge or your own dump.

---

## What you need

| | |
|---|---|
| Japanese *Puyo Puyo Tetris* (3DS) | your own copy |
| **Patched base game** | built from your dump with `tools/build_cia.py` — or **`PuyoPuyoTetris-LayeredFS.zip`** from the release assets, unpacked to `luma/titles/0004000000101200/romfs/` on a Luma3DS card |
| The Japanese v1.2.0 update | code only; installs over the patched base safely |
| **`PuyoPuyoTetris-DLC-patched.cia`** | in the release assets |

Install order: base → Japanese update → DLC. The title screen reads
**ENG 1.0.1**; a locally built base CIA reports version 1.0.1.

The patched base game is a full copy of the game with English inside it and
is **not published**; the LayeredFS zip is the published form of the same
files. An "update title" CIA was tried and withdrawn: this game's code only
ever opens the base RomFS, never an update RomFS, so an update carrying the
English data is ignored (details in TESTING.md).

## What was done

| area | |
|---|---|
| Text | 1,411 base strings and 875 DLC strings. Sega's Steam text where it exists; 392 lines written for the 3DS-only screens (Chapter 0 prologue, Club, SpotPass, errors, shop) |
| In-battle voices | 24 Japanese character banks replaced from Steam's English recordings, matched by the Japanese takes' durations (zero error) |
| DLC story voices | 760 of 763 clips; the other three were re-recorded for 3DS and have no English take |
| Online UI textures | about 550 labels across the Club, Puzzle League, standby, replay and shop screens, redrawn in place |
| DLC shop icons | 33 redrawn |
| Font atlases | the game pre-renders only the glyphs each screen uses; every screen that gained English got a matching atlas, verified per section |

What stays Japanese, and why, is in [TESTING.md](TESTING.md).

## How it works

`tools/` holds everything, GPL-3.0-or-later. The parts worth knowing about:

- `mtx.py`, `narc.py` — the text and archive formats; byte-exact on the
  untouched ROM.
- `dsp.py`, `csar.py` — a DSP-ADPCM encoder (3,944 of 3,950 frames identical
  to Sega's own) and CSTM / CWAV / CWAR / CSAR writers, each byte-identical
  rebuilding the game's files.
- `atlas_fix2.py`, `check_glyphs.py` — the per-section font-atlas rule, the one
  thing everything else depends on.
- `labels.py` — finds text labels on texture atlases, groups identical ones,
  and redraws them from `labels_en_*.json`.
- `build_cia.py`, `build_dlc_cia.py` — the packages. (`build_update_cia.py`
  builds a structurally valid update-title CIA and is kept for reference; this
  game never reads an update's RomFS, so it is not a delivery route.)

`translations/` holds the hand-written English (`tr_batch*.json`,
`tr_extra.json`, `labels_en_p*.json`). Fix a line there and rebuild.

## Credits

Sega for the text and voices; the earlier fan translation for the Adventure
story and the UI texture work it did. Tooling reused from the
[TGAA 3DS patch](https://github.com/Akoi89/tgaa-3ds-english-patch) (3dstool,
ctrtool, the CIA and NCCH writers).
