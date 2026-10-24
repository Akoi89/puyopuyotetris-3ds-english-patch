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

Nearly every count here is reproducible. The method is in [DETAILS.md](DETAILS.md), and
most of the tools that produce those counts are in [`tools/`](tools/), which ships as
source. The exceptions: the two string totals in DETAILS, 1,411 and 875, came from a count
made while the work was going on and no shipped tool reproduces them, so treat those two as
approximate; and the voice re-level tools used from 1.0.8 through 1.1.1 depend on local
analysis helpers that live in a private work repo, not in `tools/`, so don't expect to
rebuild that step yourself from what's published here. The same goes for the scripts
that staged and checked 1.1.2's and 1.1.3's redrawn pictures, which aren't in `tools/` either. Where
something has not been verified, TESTING.md says so.

**[Download the current build from Releases](../../releases/latest)** (build 1.1.3, DLC
0.3.3). What changed in each build is in [RELEASE_NOTES.md](RELEASE_NOTES.md). Also listed
on [romhacking.net](https://www.romhacking.net/translations/7714/).

> ### Playtesters wanted
>
> **Booted on a New 3DS on 6 September 2026, and on a New 3DS XL and an original 3DS on
> 7 September**, with a few games played on hardware. The base game, the Japanese update
> and the DLC install, the HOME menu tile shows the English logo, and the title screen and
> main menu run. Since then the DLC Adventure chapters have been played on a console, and
> Chapter 1 through to its end; later story chapters, the 1.0.15 bubble fix, and 1.1.0's and
> 1.1.1's re-leveled voices are still worth reporting. DLC 0.3.3 is a smaller DLC file that holds only the
> parts that carry anything, so it starts in about 12 seconds instead of about a minute and a half on one
> console. A test build with the same contents was played through on that console (the DLC skins, stages
> and EX chapter 8, no crashes). The 0.3.3 files themselves, the re-broken lines in EX chapters 8 to 10
> and the Japanese-voice DLC haven't been run yet. 1.1.3 fixes three more Japanese leftovers (the Tetris combo bar and chain notice, the replay speed hint
> and the Magic School gate sign) and was checked in Azahar only as far as the title screen reading
> ENG 1.1.3 and a letter showing on both gate pillars in the Staff Roll; the combo bar and chain
> notice (neither has come up in a match yet), the replay hint and the gate in battles and cutscenes haven't been seen yet.
> 1.1.2 redraws 111 pictures and has
> been checked on an emulator only, not on a console. In Azahar (English-voice edition) the menus and tiles, Options, Versus setup, My Data, the Adventure mission panel and the "Ready" call all showed English, with no crash, freeze or garbled screen. Not seen yet: "Ready" in a versus match, the DLC chapter strips, the tournament card, the Japanese-voice edition and a console. 1.1.1 was checked
> in Azahar on 28 September 2026: the title screen, the DLC stage's new shop sign, the
> Adventure mission screen's new tag and its opening story text all showed correctly. The
> re-leveled voices, the Broadcast Station art, the Japanese-voice edition and a real
> console are not yet confirmed. The rest was tested in Azahar.
>
> **[Report anything wrong in issue #1](../../issues/1)** (which screen, and a photo beats a
> description). Don't check first to see whether I already know. A duplicate costs me
> nothing and a report you talked yourself out of costs me a bug.
>
> **[TESTING.md](TESTING.md) lists what's already known**, along with what to install and
> how to identify the build you're running.

> **You need the Japanese base game.** It isn't distributed here or anywhere in this
> project. Cartridge or your own dump.

---

## What you need

| | |
|---|---|
| Japanese *Puyo Puyo Tetris* (3DS) | your own copy |
| **Patched base game** | `PuyoPuyoTetris-Base-xdelta.zip` (xdelta3 patch for your own decrypted dump; the only route to the English HOME menu banner), or built from your dump with `tools/build_cia.py`, or `PuyoPuyoTetris-LayeredFS.zip` unpacked to `luma/titles/0004000000101200/romfs/` on a Luma3DS card |
| The Japanese v1.2.0 update | code only; installs over the patched base safely |
| **The DLC** | `PuyoPuyoTetris-DLC-patched.cia`, or `PuyoPuyoTetris-DLC-xdelta.zip` for your own decrypted DLC dump, which produces the same file. If an older DLC is installed, install this one over it. |
| **Japanese-voice edition** (optional) | the same English text with every voice left as Sega's Japanese: a base xdelta patch, a LayeredFS zip, and a DLC CIA, all at 1.1.3 / DLC 0.3.3 as of this build. Install one edition or the other, not both |

Install order is base, then Japanese update, then DLC. The title screen reads **ENG
1.1.3** on both editions: this build's redrawn pictures aren't voice
files, so the Japanese-voice edition carries the same version number as the English-voice
build. The HOME menu jingle, not the version stamp, is what tells the two editions apart.

> **If you're using any of the xdelta zips, dump the title as an encrypted CIA and decrypt it
> on the PC.** In GodMode9, dump the title to CIA with no decrypt and no trim option, copy that
> to your computer, and run Batch CIA 3DS Decryptor on it there. Its output is what every xdelta
> here applies to. GodMode9's own decrypt hands you a file of the **right size** that isn't the
> same bytes, and the patch will refuse it with `target window checksum mismatch`, so a
> matching file size is not proof your file is
> right. Each zip's readme carries the SHA-256 of the source I used and of the file you should
> end up with. The LayeredFS zips need none of this.

The patched base game is a full copy of the game with English inside it and is **not
published**; the LayeredFS zip is the published form of the same files. An update-title CIA
was tried and withdrawn, because this game's code only ever opens the base RomFS (details
in TESTING.md).

What stays Japanese, and why, is in [TESTING.md](TESTING.md).

### Checking a download

These are the current files on the v1.0.0 tag; the tag's files are replaced in place with each build, so an older download will not match. The previous build's bundle zip stays on the tag until romhacking.net links the new one.

| File | Bytes | SHA-256 |
|---|---|---|
| `PuyoPuyoTetris-Base-xdelta.zip` | 168,209,259 | `d24f1dfeaad9e2a2267478d9dcc6a0b3172864aa5140e709c11788c7cd1096a8` |
| `PuyoPuyoTetris-DLC-JP-voices-0.3.3.cia` | 102,921,088 | `0ebda2b9af2d03ad42e01a0c24f2bd8636634a480f7f608d41db85a6f75e099b` |
| `PuyoPuyoTetris-DLC-patched.cia` | 98,640,768 | `20699aa35a00b1af145f73a392449011d93b160cdf1b8596c06e4d88d7004a1b` |
| `PuyoPuyoTetris-DLC-xdelta.zip` | 33,897,980 | `e8e50776e3b9dc73967c112e54932a54a8ddfe3f68c741ccffd7c8b33db3a2d3` |
| `PuyoPuyoTetris-JP-voices-LayeredFS.zip` | 10,283,834 | `2fd0eacc09a5c4ca97bf2c36cf4d00ebc5718781df3712f19d8d06973a83085c` |
| `PuyoPuyoTetris-JP-voices-xdelta-patches-1.1.3.zip` | 10,964,740 | `6bc697675d06496c2ab36488ffebcf470c41cb7e725fcc3186fa53415243b713` |
| `PuyoPuyoTetris-LayeredFS.zip` | 172,832,866 | `20a944705d65a337b385d097e3fa8747c1c2c2214aa647ec90ff4b6b2f1990fe` |
| `PuyoPuyoTetris-xdelta-patches-1.1.3.zip` | 202,264,368 | `a0c8cb5e4f1dc5c982e4f61161dd5c4bce1f7fb5494c68b100433e61f5bb3482` |

Five of the eight files change this build: both DLC CIAs, the DLC xdelta zip and both patch bundles. The three base-game zips (the base xdelta zip and both LayeredFS zips) carry over unchanged from 1.1.3.

## How it works

`tools/` holds everything, GPL-3.0-or-later, and `translations/` holds the hand-written
English (`tr_batch*.json`, `tr_extra.json`, `labels_en_p*.json`). Fix a line there and
rebuild. What each tool does is in [DETAILS.md](DETAILS.md).

The tooling was written with LLM assistance (Claude, through Claude Code). Nothing
generated ships in the patch: the text and voices are Sega's own files out of the Steam
release, apart from the 392 lines written by hand for screens that don't exist on PC, and
the tools ship as source so you can check that, except the voice re-level tools noted above.

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
