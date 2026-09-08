# Puyo Puyo Tetris: 3DS English patch

**Sega's official English text and voices, from the Steam release of *Puyo Puyo Tetris*,
carried onto the Japanese Nintendo 3DS release, DLC included.**

*Puyo Puyo Tetris* (3DS, 2014) never had an English release. Sega localized the game for PC
and consoles in 2017 but never brought that text back to the handheld. An earlier fan
translation carried the Adventure story across but left the online menus, the prologue, the
error dialogs, the shop, most of the in-battle character voices, the DLC chapters and every
texture label in Japanese.

This finishes it: about 99% of displayed text, all 37 characters' in-battle voices, all
three DLC story chapters (text and voices), the online UI textures, and the DLC shop icons.
Sega's own English sprites are used wherever they exist in the Steam data rather than
anything redrawn by hand.

Every count is reproducible. The method behind each one is in [DETAILS.md](DETAILS.md) and
the tools that produce them are in [`tools/`](tools/), which ships as source. Where
something has not been verified, TESTING.md says so.

**[Download the current build from Releases](../../releases/latest)** (build 1.0.12, DLC
0.2.7). What changed in each build is in [RELEASE_NOTES.md](RELEASE_NOTES.md). Also listed
on [romhacking.net](https://www.romhacking.net/translations/7714/).

> ### Playtesters wanted
>
> **Booted on a New 3DS on 6 September 2026**, and that's about the extent of it. The base
> game, the Japanese update and the DLC install, the HOME menu tile shows the English logo,
> the title screen and main menu run. That first run on a console found a bug every earlier
> build had, which 1.0.11 fixes. Beyond the menus, play on hardware is a few minutes old.
> The rest was tested in Azahar.
>
> **[Report anything wrong in issue #1](../../issues/1)** (which screen, and a photo beats a
> description). See [TESTING.md](TESTING.md) for what to install, how to identify the build,
> and what's known.

> **You need the Japanese base game.** It isn't distributed here or anywhere in this
> project. Cartridge or your own dump.

---

## What you need

| | |
|---|---|
| Japanese *Puyo Puyo Tetris* (3DS) | your own copy |
| **Patched base game** | `PuyoPuyoTetris-Base-xdelta.zip` (xdelta3 patch for your own decrypted dump; the only route to the English HOME menu banner), or built from your dump with `tools/build_cia.py`, or `PuyoPuyoTetris-LayeredFS.zip` unpacked to `luma/titles/0004000000101200/romfs/` on a Luma3DS card |
| The Japanese v1.2.0 update | code only; installs over the patched base safely |
| **The DLC** | `PuyoPuyoTetris-DLC-patched.cia`, or `PuyoPuyoTetris-DLC-xdelta.zip` for your own decrypted DLC dump, which produces the same file |

Install order is base, then Japanese update, then DLC. The title screen reads **ENG
1.0.12**.

The patched base game is a full copy of the game with English inside it and is **not
published**; the LayeredFS zip is the published form of the same files. An update-title CIA
was tried and withdrawn, because this game's code only ever opens the base RomFS (details
in TESTING.md).

What stays Japanese, and why, is in [TESTING.md](TESTING.md).

## How it works

`tools/` holds everything, GPL-3.0-or-later, and `translations/` holds the hand-written
English (`tr_batch*.json`, `tr_extra.json`, `labels_en_p*.json`). Fix a line there and
rebuild. What each tool does is in [DETAILS.md](DETAILS.md).

The tooling was written with LLM assistance (Claude, through Claude Code). Nothing
generated ships in the patch: the text and voices are Sega's own files out of the Steam
release, apart from the 392 lines written by hand for screens that don't exist on PC, and
the tools ship as source so you can check that.

## Credits

Sega for the text and voices; the earlier fan translation for the Adventure story and the
UI texture work it did. Tooling reused from the
[TGAA 3DS patch](https://github.com/Akoi89/tgaa-3ds-english-patch) (3dstool, ctrtool, the
CIA and NCCH writers).

If you want Sega's translation properly, buy *Puyo Puyo Tetris* on PC or a current console.
