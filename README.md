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

**[Download the current build from Releases](../../releases/latest)** (build 1.0.15, DLC
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
| **Japanese-voice edition** (optional) | the same English text with every voice left as Sega's Japanese: `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.15.zip` (base and DLC patches for your own decrypted dumps), `PuyoPuyoTetris-JP-voices-LayeredFS.zip` (Luma3DS) and `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. Install one edition or the other, not both |

Install order is base, then Japanese update, then DLC. The title screen reads **ENG
1.0.15** in both editions.

> **If you're using any of the xdelta zips, dump the title as an encrypted CIA and decrypt it
> on the PC.** In GodMode9, dump the title to CIA with no decrypt and no trim option, copy that
> to your computer, and run Batch CIA 3DS Decryptor on it there. Its output is what every xdelta
> here applies to. GodMode9's own decrypt hands you a file of the **right size** that isn't the
> same bytes, and the patch will refuse it, so a matching file size is not proof your file is
> right. Each zip's readme carries the SHA-256 of the source I used and of the file you should
> end up with. The LayeredFS zips need none of this.

The patched base game is a full copy of the game with English inside it and is **not
published**; the LayeredFS zip is the published form of the same files. An update-title CIA
was tried and withdrawn, because this game's code only ever opens the base RomFS (details
in TESTING.md).

What stays Japanese, and why, is in [TESTING.md](TESTING.md).

### Checking a download

These are the eight assets currently on the v1.0.0 tag; the tag's files are replaced in place with each build, so an older download will not match.

| File | Bytes | SHA-256 |
|---|---|---|
| `PuyoPuyoTetris-Base-xdelta.zip` | 169205271 | `68b70b6bf7b66be8803757574efa2720a2052a914064c2932decc7b177dd0c01` |
| `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia` | 116165696 | `b742243d81c2b7b2ef91d27c5c6570291b5b4cbcdfd3e3c6d847aab33ad00475` |
| `PuyoPuyoTetris-DLC-patched.cia` | 111889472 | `de833dede4482b83f24e413dc9f3801c66de6f3e6315d2fd4e4449d29e51971c` |
| `PuyoPuyoTetris-DLC-xdelta.zip` | 33920283 | `62952ba3075cf7b367e602a51a353b340a995c240dcd6463816dd31c080d2813` |
| `PuyoPuyoTetris-JP-voices-LayeredFS.zip` | 8612432 | `0668d5e9e8735f7703252d238fa39f25b1a4c45e70ff5d4a56db8bc20a05aee3` |
| `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.15.zip` | 11352401 | `244b0a18d5f83c823f3da0eadac7d7a09418b6be8138b2f99d3b0b6e6a902742` |
| `PuyoPuyoTetris-LayeredFS.zip` | 42849184 | `7ba3b55702ce366b40a265a107c780523d2ed7f5d3fe7c0b492613111da97971` |
| `PuyoPuyoTetris-xdelta-patches-1.0.15.zip` | 203281923 | `abea4da57faaa5f88373cb214520f5dcdf3c7f38f1e2543c4243453809b0e93b` |

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
