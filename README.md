# Puyo Puyo Tetris: 3DS English patch

**Sega's official English text and voices, from the Steam release of *Puyo Puyo Tetris*,
carried onto the Japanese Nintendo 3DS release, DLC included.**

*Puyo Puyo Tetris* (3DS, 2014) never had an English release. Sega localized the game for PC
and consoles in 2017 but never brought that text back to the handheld. ongo_gablogian's fan
translation carried the Adventure story across, and Partyderp64's `PPT3dsENG_0.3dx` build
added English story voices on top of it. Between them they still left the online menus, the
prologue, the error dialogs, the shop, most of the in-battle character voices, the DLC
chapters and every texture label in Japanese.

This finishes it: about 99% of displayed text, all 37 characters' in-battle voices, all
three DLC story chapters (text and voices), the online UI textures, and the DLC shop icons.
Sega's own English sprites are used wherever they exist in the Steam data rather than
anything redrawn by hand.

Every count is reproducible. The method behind each one is in [DETAILS.md](DETAILS.md) and
the tools that produce them are in [`tools/`](tools/), which ships as source. Where
something has not been verified, TESTING.md says so.

**[Download the current build from Releases](../../releases/latest)** (build 1.0.14, DLC
0.2.8). What changed in each build is in [RELEASE_NOTES.md](RELEASE_NOTES.md). Also listed
on [romhacking.net](https://www.romhacking.net/translations/7714/).

> ### Playtesters wanted
>
> **Booted on a New 3DS on 6 September 2026, and on a New 3DS XL and an original 3DS on
> 7 September**, with a few games played on hardware. The base game, the Japanese update
> and the DLC install, the HOME menu tile shows the English logo, and the title screen and
> main menu run. That first console run found a bug every earlier build had, which 1.0.11
> fixes. Beyond that, play on hardware is still short: a story chapter or a full match
> played through on a console is worth reporting. The rest was tested in Azahar.
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
| **Japanese-voice edition** (optional) | the same English text with every voice left as Sega's Japanese: `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip` (base and DLC patches for your own decrypted dumps), `PuyoPuyoTetris-JP-voices-LayeredFS.zip` (Luma3DS) and `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. Install one edition or the other, not both |

Install order is base, then Japanese update, then DLC. The title screen reads **ENG
1.0.14** in both editions.

The patched base game is a full copy of the game with English inside it and is **not
published**; the LayeredFS zip is the published form of the same files. An update-title CIA
was tried and withdrawn, because this game's code only ever opens the base RomFS (details
in TESTING.md).

What stays Japanese, and why, is in [TESTING.md](TESTING.md).

### Checking a download

These are the eight assets currently on the v1.0.0 tag; the tag's files are replaced in place with each build, so an older download will not match.

| File | Bytes | SHA-256 |
|---|---|---|
| `PuyoPuyoTetris-Base-xdelta.zip` | 169204774 | `cc872b465b35c938e0313f332ff518283093368e53863494391e29fd90bed3b4` |
| `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia` | 116165696 | `b742243d81c2b7b2ef91d27c5c6570291b5b4cbcdfd3e3c6d847aab33ad00475` |
| `PuyoPuyoTetris-DLC-patched.cia` | 111889472 | `de833dede4482b83f24e413dc9f3801c66de6f3e6315d2fd4e4449d29e51971c` |
| `PuyoPuyoTetris-DLC-xdelta.zip` | 33920283 | `62952ba3075cf7b367e602a51a353b340a995c240dcd6463816dd31c080d2813` |
| `PuyoPuyoTetris-JP-voices-LayeredFS.zip` | 8537268 | `f99c5e53cfa98ac4459200a7c2fa45df07611aaf6242e0a455e1fbafc9d7d7ac` |
| `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.14.zip` | 11352097 | `98de69754b1edf91f1b2046c3d52d6a02d17973205296a6210213039fcb88613` |
| `PuyoPuyoTetris-LayeredFS.zip` | 42774019 | `986e7b6f822a9ffa621b1d904b243d5f8b75b9f9681caf70226af3a543f5defd` |
| `PuyoPuyoTetris-xdelta-patches-1.0.14.zip` | 203281223 | `c441cf880217872583ffbb19557bcd9acf0de48a3a55e7e148b4c00043f3ece3` |

## How it works

`tools/` holds everything, GPL-3.0-or-later, and `translations/` holds the hand-written
English (`tr_batch*.json`, `tr_extra.json`, `labels_en_p*.json`). Fix a line there and
rebuild. What each tool does is in [DETAILS.md](DETAILS.md).

The tooling was written with LLM assistance (Claude, through Claude Code). Nothing
generated ships in the patch: the text and voices are Sega's own files out of the Steam
release, apart from the 392 lines written by hand for screens that don't exist on PC, and
the tools ship as source so you can check that.

## Credits

Sega for the text and voices.

**ongo_gablogian and the original translation team** for the Adventure story and the UI
texture work, which is what made the game playable in English at all.

**Partyderp64**, whose `PPT3dsENG_0.3dx` build put English story voices over that
translation. That build is the fan shell this patch is built from: 2,534 of its 2,535 files
are carried through unchanged, and the one that isn't is the sound archive, where the 13
battle voice banks it had already made English were re-imported at Sega's own sample rate.

Tooling reused from the
[TGAA 3DS patch](https://github.com/Akoi89/tgaa-3ds-english-patch) (3dstool, ctrtool, the
CIA and NCCH writers).

If you want Sega's translation properly, buy *Puyo Puyo Tetris* on PC or a current console.

## License

The tools and docs in this repository are GPL-3.0-or-later; see [LICENSE](LICENSE) and [NOTICE](NOTICE). Sega's game content and the fan team's own files carried through from earlier patches are not covered by that license.
