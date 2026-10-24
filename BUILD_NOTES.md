# Build notes

This is the full technical record of every build. RELEASE_NOTES.md is now
written for players and kept short; everything that used to live there,
including every figure and measurement, stays here in full.

The completed English patch. This release tag is v1.0.0; the assets on it are replaced in place with each build, and the current one is **1.1.3** with DLC 0.2.11 (see below). **Booted on a New 3DS** on 6 September 2026 (install, HOME menu, title and main menu; 1.0.11 fixes the misaligned error dialogs that run found; 1.0.12 changes eight textures and was checked in Azahar; 1.0.13 fixes the EX chapter line breaks and the Party-mode Time Up graphic; 1.0.14 raises two base-game speech bubbles; 1.0.15 re-breaks the base-game Adventure dialogue so no line runs past the bubble edge; 1.1.0 re-levels quiet battle and DLC voices and re-imports the base game's story voices; 1.1.1 puts Sega's text on lines that still carried the earlier fan translation's wording, re-levels the story voices a second time, and adds Steam's art for the mission "New!" tag, the Broadcast Station screens and the DLC shop; 1.1.3 redraws the Tetris combo bar, the replay hint strip and the school gate sign; 1.1.2 redraws 111 pictures from Sega's original Japanese art and has been checked on an emulator only (Azahar, English-voice edition; see the 1.1.2 section below); 1.1.1 was booted in Azahar on 28 September 2026 with the DLC installed, where the title screen, the DLC stage's new shop sign, and the mission screen's "New!" tag and opening story text all showed correctly, but the re-levelled voices, the Broadcast Station art, the Japanese-voice edition and a real console are not yet confirmed). Every file is verified byte-for-byte; base and DLC were tested in Azahar. See TESTING.md, and report problems in [issue #1](../../issues/1).

- **Base game** (~99% of displayed text, all 37 characters' in-battle voices, the online UI textures, the HOME menu banner): build it from your own dump with `tools/build_cia.py`, or use **`PuyoPuyoTetris-LayeredFS.zip`** on Luma3DS. Title screen reads **ENG 1.1.3**; the built CIA reports 1.1.3.
- **`PuyoPuyoTetris-DLC-patched.cia`**: three story chapters, text and voices (760 of 763 clips), 33 shop icons and the three EX chapter plates, plus the DLC stage's shop sign and stage icon (0.2.10) and six redrawn chapter title strip pictures (0.2.11). TMD 0.2.11.
- **`PuyoPuyoTetris-Base-xdelta.zip`**: the base game as an xdelta3 patch (about 168,209,259 bytes) for your own DECRYPTED dump (Batch CIA 3DS Decryptor turns a base game dump into a decrypted .cci; that .cci is the source). Dump the title as an encrypted CIA with GodMode9 and decrypt it on the PC; GodMode9's own decrypt gives a file of the right size that the patch refuses. It builds the full English CIA including the English HOME menu banner, which LayeredFS cannot change. The README inside has the hashes and the command.
- **`PuyoPuyoTetris-DLC-xdelta.zip`**: the same DLC as an xdelta3 patch for people who would rather build it from their own dump. Apply it to your DECRYPTED Japanese DLC dump (Batch CIA 3DS Decryptor); the README inside has the hashes and the one-line command. The result is byte for byte the released DLC CIA.
- Install order: Japanese base, patched base (or LayeredFS), Japanese v1.2.0 update (code only), this DLC.
- **Japanese-voice edition** (added 11 September 2026, asked for in [issue #2](../../issues/2)): the same English text and textures with every voice left as Sega's Japanese. A base xdelta zip, a LayeredFS zip and a DLC CIA. Same title ID as the English-voice build; from 1.1.1 it carries the same ENG stamp as the English-voice build (**ENG 1.1.3** now), since 1.1.1's, 1.1.2's and 1.1.3's fixes are text and art, not voice files, and this edition is rebuilt for them. Install one edition or the other, not both. Details in the section below.

**Withdrawn the same day: an "update title" CIA.** It packaged the English data inside Sega's v1.2.0 update. Puyo Puyo Tetris's code only ever opens the base game's RomFS (path type 0) and never asks for an update RomFS (type 5), so the console and Azahar keep reading Sega's Japanese files no matter what the update carries. It did nothing. If you downloaded it, delete it and install the official update instead.

The Japanese base game is not distributed here. 1.0.1 folded in a second-opinion review of the hand-written text; 1.1.3 (below) is the current build.

---

## 1.1.3 / DLC 0.2.11

A pictures-only build for the base game; the DLC is unchanged. Three Japanese leftovers were redrawn: the Tetris
combo bar and the notice beside it, the replay speed hint strip, and the sign on the Magic School gate pillars. Six
textures in five archives changed, in both editions. Text, voices and the program file are the same as 1.1.2; the
only other file that changes is the title screen stamp, now **ENG 1.1.3**.

**What changed.**
- `tetris/tetris2p/tetris2p.narc`, member 7 (RGBA4): the combo bar reads "COMBO" where it said "REN" (the bar keeps
  the 3DS version's navy colour, since every label on that side is navy; Sega's PC bar is grey), and the notice
  that shows a chain of line clears reads "CHAIN!" and "LINES" where it had Japanese text and "LINE". The engine
  draws these through fixed cells in the archive's layout data, so the lettering stays inside the original cells.
- The Magic School gate: the Japanese "pu" character on both pillars is a Latin P in three textures,
  `ingame_bg/bg_0030.narc` and `adventure_bg/bg_0030.narc` (ETC1A4, the sign is part of the brick picture, so the
  surrounding brick was rebuilt with inpainting) and `ingame_bg/s_bg_0030.narc` (the small school scene). The credits
  scene shows the gate too; which of the three pictures it draws was not pinned down, and all three are fixed.
- `tenp/replay/replay.narc`: the replay speed hint strip reads "Press left/right to adjust playback speed!". That
  is Sega's own wording; it is in the Steam data as `tenp/replay/replay_e` and an earlier note in this file saying
  the strip was not found anywhere was wrong.
- `title/title.narc`: the stamp.

**How it was checked.** Both built CIAs were read back independently: the title version, contents 1 and 2, the program
file and ExeFS identical to 1.1.2, the file system hash, and the file system compared with 1.1.2's, which differs in
exactly six files (the five archives and title.narc) in each edition. Each replaced texture was decoded back out of the CIA and compared with its
source picture: exact for the RGBA4 and compressed ones, and for the two ETC1A4 ones identical to the encoder's own
preview with every pixel outside the block-aligned box unchanged from 1.1.2 (46 of 46 checks pass). ETC1A4 re-encodes
whole 4x4 blocks, so pixels inside the edge blocks of the redrawn area can move slightly: at most 21 levels in the
brick pillar blocks of the battle picture and one visible pixel (10 levels) in the adventure picture. The two
compressed pictures got smaller than the shipped ones at the same decompressed size. The xdelta patches were built
and proven as in 1.1.2.

**Checked in a game.** In Azahar (English-voice edition only): the title stamp reads ENG 1.1.3, and the credits scene
shows a Latin letter on both gate pillars (at that size it reads a little like a lowercase p). Not seen: the combo bar
and the CHAIN!/LINES notice (they only show in a Tetris match that reaches a combo), the replay strip (needs a saved
replay), the gate in the battle and small-scene pictures (no Versus stage uses it) and the adventure cutscenes, and
nothing has been run on a console.

LayeredFS: the five archives are new files in the zips (they were untouched Japanese originals in 1.1.2's), so the
zips grow by those and the new title.narc.

## 1.1.2 / DLC 0.2.11

A pictures-only build. The earlier English lettering on a set of menu, Club, internet,
replay and results pictures, two main menu tile previews, the "Ready" call, the tournament
card, a banner and the DLC chapter title strips had problems, so 111 pictures were redrawn
from Sega's original Japanese art, 105 in the base game and 6 in the DLC. Text, voices and the program file are the same as 1.1.1 / DLC
0.2.10; the only other file that changes is the title screen stamp, now **ENG 1.1.2**.

**What was wrong and what changed.** Plates, pills and icons that an earlier pass had erased
are back. The lettering now follows the original's outline, shading and size instead of plain
thin text, and text in grids is one consistent size. Japanese leftovers on a few screens are
English now. Some textures looked slightly washed out or see-through, from a 4-bit colour
rounding that came in with the earlier fan translation; they are exact again. Wording the
player may notice: the wins counter (was "beaten"), "Chain FX" for the Chain Animations
option, "chains+" and "colors+" in a rule tip, "RANK" on the club rank pill, "Interstellar
Dream" (was "An Interstellar Dream") on a DLC chapter strip, the tournament card's "Wins" /
"High Score:" / "Final Score:" (were "beaten" / "Best Record" / "This Run"), and "Big Bang
Mode" (was "Bing Bang Mode"). The main menu's Online tile preview now reads "Must Watch!" and
"Choose a replay", the My Data Options tile preview shows "Tokyo" for Location (it was a
Japanese prefecture), and the "Ready" call (picture 73) was redrawn after the first emulator
pass showed it clipped; the second pass shows it whole.

**Counts, from `_img112\MANIFEST.json`.** 39 archives are touched (33 base, 6 DLC) and 111
entries are replaced (105 base, 6 DLC); none were blocked. By format: 95 RGBA4, 7 ETC1A4,
8 RGBA8 and 1 RGBA5551. The overlay is 58,850,507 bytes. 12 archives change size; of
those, four grew (system 61,799 to 65,645 bytes, bottom_bg 157,507 to 175,379, party2p
230,080 to 239,118, toko 616,124 to 622,123). The two newest overlay files are the main
menu's and My Data's tile-preview archives (menu\main_menu.narc and mydata\mydata\mydata.narc,
both taken from the earlier fan translation's tree, same size as before, spliced in place). In the DLC, the six pictures sit in contents
0010, 0011 and 0012 (two archives each); content 00ca and every other content are
byte-identical to 0.2.10.

**Checks that were run.** Each of the 111 replaced entries was decoded back out of the
patched archives and matched its source image (RGBA exact; ETC1A4 alpha exact with a
maximum colour error of 0 on visible pixels), 221 untouched members and 490 untouched
texture entries in the touched archives were byte-identical to 1.1.1, and the same decode
was repeated on the built CIAs for both editions (105 base and 6 DLC pictures each, 0
mismatches; 160 checks passed, 0 failed). The title stamp was read back out of the built base CIAs as an image. The
earlier 1.1.1 art in the same archives (the "New!" tag, the Broadcast Station badges) is
untouched except one overlap: the "New!" tag's texture entry is redrawn again, and of the
1,043 pixels 1.1.1 had changed in it, the new version matches 1.1.1 on all 780 visible ones.

**Checked on an emulator only.** Azahar on a PC, English-voice edition only, saves untouched. Pass 1 (an
earlier 1.1.2 build): title stamp "ENG 1.1.2", Quick Play and all main menu tiles, Options (Chain
FX, SpotPass Toggle, Location as a spinner), Solo Arcade tiles, Versus setup, rules panel and Handicap,
pause menus, My Data (Stats, Theatre, Options, Shop), Adventure mission panel "Your Mission:" and the "New!"
tag. Pass 2 (this final build, viewed at 2x): the "Ready" call whole in Endless Puyo, Endless Fever, Marathon,
Sprint, Tiny Puyo and Ultra (letters shrink toward the end, as in the Japanese original); the Online tile
preview ("Must Watch!", "Choose a replay"); the My Data Options tile preview (Location "Tokyo"); the Endless
Puyo Puyo mode card; no crash, freeze or garbling. Pass 2 was cut short by a usage limit before the versus
"Ready" burst, so "Ready" was not checked in a versus match. Not seen: a real console, the Japanese-voice
edition booted, the DLC chapter title strips in game, the tournament card (Wins / High Score: / Final Score:)
on a live screen. Captures: work\_rig112b. Not run on a real console.

**Known problems added.** A few labels are wider than the box the original art had for them
and some of the small grids use condensed lettering to fit; four small rank-suffix pictures
(the Japanese mark that follows a rank number) on two replay and league screens are still
Japanese; and the right-hand column on the tournament screens is text the game builds itself
and may read oddly; and eleven other untouched pictures still show Japanese (work\_leftover112\CANDIDATES.md items 1 to 11; item 12 is the logo, a brand mark, left alone): the six tile previews in menu\nettop.narc (nettop08), the Solo Arcade tile pictures tokoton05_s, hitoride05 and minnade05_s (HUD labels), the two rule-settings pictures gamesetting01 and gamesetting02 in ingame_common.narc (use on screen unconfirmed), clubentry02 (vertical club sign-up label), the replay speed hint strip in replay.narc, result_04a (the "this league's results" text, top right), and standby_puzzleleague05 (faint laurel emblems) and standby_puzzleleague00 (a dark emblem, text not legible, not verified).

**Both editions.** The Japanese-voice edition is rebuilt with the same picture overlay and
stays at the same version number as the English-voice build: **ENG 1.1.2 / DLC 0.2.11**.

## 1.1.1 / DLC 0.2.10

The final check of 1.1.0 (in-game, both offline and on the rig) found that a real share of the
base game's text was still the earlier fan translation's own wording rather than Sega's,
typos and wrong numbers included, and turned up new art and voice leftovers besides. This
build fixes what the check found.

**Text.** `inject.py` had started from the fan translation's own romfs and only pulled Sega's
Steam text in for lines the fan build had left in Japanese; lines the fan had already
translated passed through untouched. That was never a documented choice; BUILD_NOTES only
ever said the base text came from the fan translation. An audit found 367 lines across 38
base text tables where this had left the earlier fan wording standing where Sega's own line
existed, worst in the Adventure story (chapter01 and the shared script) and the lesson
screens; examples include Adventure mission targets missing a zero ("Score 10,00 pts" for
10,000), "This it not good!", "spayed", "Let met check", "focuse", "frightened.!", and "that
this". Seven rows were kept as shipped after review: six lesson lines about pressing the A
or B Button, which are already worded for the 3DS control scheme where Steam's own two
button-name variants are its own PC phrasing, and one placeholder-only slot with no real
fan line behind it. The other 365 rows take Sega's text, rewrapped for the 3DS bubble the
same way as 1.0.15's line-break fix; 2 bubbles grow a line taller to hold the result. Control
codes, the font's glyph coverage (including Sega's ASCII "~" in place of the fan build's
fullwidth "～"), and the word order of every rewritten line were checked before release.
The DLC's text was Sega's own from the start and needed no change here. Booted
in Azahar on 28 September 2026: the opening story scene played with the new
text, the first line confirmed against the game data and the screen captures
showing the lines after it; the rest of the 367 rewritten lines have not been
seen running yet.

**Story (Adventure) voices, re-levelled a second time.** 1.1.0's rule brought every story
stream up toward the Japanese line's loudness and, on a few of the loudest lines, ended up
sounding squashed. This build's rule instead brings any line louder than the Japanese take
down to it, and raises a quiet line toward the Japanese level only as far as a per-line
limiting cap allows, so nothing gets pushed past clean; where even that isn't enough on a
handful of lines, the gentlest clean level under today's loudness is kept instead of forcing
a match. Of the 2,320 story streams, 1,145 files changed from the 1.1.0 bytes and 1,175 stayed
byte-identical to it; raised lines land at or within 0.1 LU above the Japanese level, and no
stream has a clipped run of samples.

**Art from Steam's PC release**, matched to the 3DS screens the same way as 1.0.7's sweep:
the Adventure mission screen's red "New!" tag (the Japanese screen had a "新ルール" banner
in its place); the Broadcast Station's eleven replay badges, which needed
fixing on both screens that carry them; and the DLC stage's shop sign and its stage-select
icon, both of which read "Ando Family FRESH PRODUCE" in Sega's own lettering. Each was
checked against a render before building. Booted in Azahar on 28 September 2026: the mission
screen's "New!" tag showed correctly on the Your Mission screen for Act 1 stage 1-1, and both
the DLC stage's preview and its in-match background showed the new shop sign with no gaps
around it. The Broadcast Station screens are online-only and not reachable offline, so their
badges are still checked only as rendered images, not confirmed running.

**Known problems added.** A faint Puzzle League medal crest is listed as known rather than
fixed: Sega's own English version of it was tried and read worse once fitted into this
game's smaller crest, so the Japanese one is kept. The Slot rule's "N more Puyo" counter and
a handful of baked-in online menu preview cards are also newly listed as known; neither has
a usable English source anywhere in Sega's PC release. Separately, the Tetris-side HOLD/NEXT
labels looking clipped, already reported and listed as known in issue #1 since 1.0.6, is now
also listed in TESTING.md and RELEASE_NOTES.md, which had not carried it.

**Docs.** README.md no longer implies every tool that produces this project's counts ships
as source: the voice re-level tools used since 1.0.8, including this build's, depend on
local analysis helpers that live in a private work repo, and DETAILS.md says so plainly
instead of naming scripts that aren't in `tools/`. The zip readmes' known-problem list now
carries the stylised online-menu mode names alongside everything else.

**The Japanese-voice edition is rebuilt for this release**, the first time since 1.0.15 that
it moves with the English-voice build's version number: none of the above touches a voice
file, so the same text and art overlay applies to both editions, and both now read **ENG
1.1.1 / DLC 0.2.10**. Its own rebuild recipe (swap the `sound` folder for Sega's Japanese
one, compare file by file) is unchanged; see the section below.

What has been checked so far: every rewritten table was verified byte for byte against its
source list, control codes preserved, box widths checked against each scene's own font, and
the story-voice set was re-verified byte for byte on the way into both CIAs; a second reviewer
checked the rework independently. **Also checked**: booted in Azahar on 28 September 2026
with the DLC installed (every content read back equal to the CIAs); the title screen read
ENG 1.1.1, the DLC stage's shop sign and stage-select icon showed the new art with no gaps,
the Adventure mission screen's "New!" tag showed on Act 1 stage 1-1, and the opening story
scene played with the new text (the first line confirmed against the game data, the screen
captures showing the lines after it). **Not yet checked**: the re-levelled story voices and
the Broadcast Station badges (online-only, so far checked only as rendered images), the
Japanese-voice edition (same files verified byte for byte identical, but not run), and a real
console.

## Japanese-voice edition (first released 11 September 2026 for 1.0.12, now 1.1.3 / DLC 0.2.11)

Asked for in issue #2: the English text without the English voices. This is
the 1.0.12 build taken apart and put back together with its `sound` folder
swapped for Sega's original (2,320 story voice streams and the in-battle
voice bank), and the HOME menu banner's audio put back to Sega's jingle. The
rebuilt file system was compared against the English-voice build file by
file: the only differences are under `sound`. The DLC was rebuilt from the
same text and texture overlay with the 760 imported voice clips left out;
676 of its 701 contents are byte for byte the Japanese DLC, and the other
three differ from it only in their 12 text and texture files each.

What that means in play: story scenes, in-battle voices, character select,
the title-screen announcer, the HOME menu jingle and the three DLC chapters
all play Sega's Japanese takes, and everything on screen is the same English
as the main release.

Rebuilt on 14 September 2026 as 1.0.13 / DLC 0.2.8, again as 1.0.14, and on
17 September 2026 as 1.0.15 with the line-break fix. Each time the recipe and
the file-by-file comparison were repeated on the new files, and none of those
builds touches a voice file. **1.1.0 did not rebuild this edition**: none of
its changes touched text or textures, only the English `sound` archive this
edition already replaces with Sega's Japanese one, so it stayed at **ENG
1.0.15 / DLC 0.2.8**, one version behind the English-voice build. **1.1.1
rebuilds it again**, because this build's text and art fixes are not voice
files: the same overlay that goes into the English-voice build goes into this
one, with `sound` swapped back to Sega's Japanese files the same way as every
earlier rebuild, and the file-by-file comparison repeated. This is the first
time since the split that both editions carry the same version stamp, **ENG
1.1.1 / DLC 0.2.10**; the HOME menu jingle remains the way to tell them apart,
since the title screen no longer does. This rebuild has not been booted; its
files are verified byte for byte identical to the English-voice build's text
and art overlay, but it has not been run.

**1.1.2 rebuilds it again** with the same picture overlay as the English-voice build (the `sound` folder
stays Sega's Japanese one), and both editions read **ENG 1.1.2 / DLC 0.2.11**.

**1.1.3 rebuilds it again** with the same six replaced textures and the new stamp, and both editions read **ENG 1.1.3 / DLC 0.2.11**; this edition's 1.1.3 build has not been booted.

## Current build before this one: 1.1.0 / DLC 0.2.9

Three voice problems, all levelling issues rather than new recordings: some battle and DLC voice lines
were clearly quieter than the Japanese lines they replace, and the base game's story (Adventure) voices,
imported by the earlier fan build, had been pushed loud enough to clip on their loudest lines. All three
are fixed by `voice_relevel3.py` (story streams go through `import_story_voices.py`), each wave encoded
once from Steam's own recording.

**Battle, select, title-call and DLC voices** (1,641 tenp.bcsar waves plus 760 DLC clips). Each wave tries
up to three candidate encodes, from the loudest to the gentlest limiting, and takes the first whose worst
20 ms stretch is no more than 2 dB noisier (against Steam's recording) than the wave that shipped in
1.0.15. Quiet waves aim at the Japanese take's loudness; waves that were already fine stay within 0.1 LU
of 1.0.15. A wave where nothing qualifies keeps the 1.0.15 bytes exactly: 15 of the 1,641 tenp waves and
5 of the 760 DLC clips. Measured against the Japanese takes, battle waves within 1 LU went from 772 to
998 of 1,519, more than 2 LU under from 311 to 59, and more than 4 LU under from 65 to 8. DLC clips within
1 LU went from 479 to 538 of 760, more than 2 LU under from 95 to 20, more than 4 LU under from 20 to 5.
No wave in either set ended more than 0.1 LU quieter than 1.0.15.

**The base game's story voices** (2,321 MZV streams in `sound/stream`). 2,320 are re-imported from Steam's
recording, each aimed at the Japanese stream's loudness, trying the gentlest limiting first. The one
English-only stream (MZV_07_01_1_039) has no Japanese take and no matching Steam row, so it keeps its
shipped audio. Four streams whose Japanese take is more than 15 LU quieter than 1.0.15's keep 1.0.15's
level, and ten that can't reach the Japanese level at any gain keep 1.0.15's level with the least
processing that holds it. Clip events (three or more samples pinned at full scale) went from 117,198 across
the shipped streams to zero; streams within 1 LU of the Japanese take went from 672 to 2,306 of 2,320.
1.1.1 revisits this set a second time; see above.

**The LayeredFS zip now carries the English story voices for the first time.** The overlay behind every
earlier LayeredFS build held no story streams, so on a Luma3DS card the game played Sega's Japanese ones;
the built CIA and the xdelta routes always carried the English ones. From 1.1.0 the 2,320 streams are in
the overlay, and the LayeredFS zip is 171,228,121 bytes (1.0.15's was 42,849,354).

**Why 1.1.0 and not 1.0.16**: a 3DS title version keeps only four bits for its last number, so 1.0.15 was
the last 1.0.x build possible; 1.1.1 continues from there for the same reason.

**The Japanese-voice edition was not rebuilt for 1.1.0**, as above: it stayed at 1.0.15 / DLC 0.2.8 until
1.1.1.

What has been heard: the re-levelled battle shouts in a Versus match in Azahar (Tee), and samples of the
battle, DLC and story voices from the files. Every wave and stream was re-verified byte for byte on the way
into both CIAs, and a refuter independently re-decoded every story stream and DLC clip and a random sample of the battle waves against the tables. Not yet heard in a
story scene or on a console. The title screen read **ENG 1.1.0** and the DLC was **TMD 0.2.9**.

## 1.0.15 / DLC 0.2.8

The base game's Adventure dialogue, re-broken so no line runs past the edge of
its speech bubble. The DLC is unchanged; if you are already on DLC 0.2.8 you
only need the base files.

This is the width half of the bubble problem, and until now only the DLC had
been checked for it. The base text came from the earlier fan translation with
its line breaks set for a wider box, and 162 lines in 160 bubbles, spread
across Chapters 1 to 7 and the shared end-of-chapter script, were wide enough
to run into the border. They are all re-broken. **No word is changed, added or
dropped**; only where the breaks fall. Where the text no longer fits the number
of lines the bubble was scripted for, the height goes up too: 28 bubbles, one
byte each.

The cap is 193 pixels, which is not a guess. A player on a New 3DS XL
photographed one line at 204 pixels landing on the border and another at 193
drawing with 22 pixels to spare, so 193 is the widest width there is a
photograph of working. Line widths are summed from the game's own glyph table
for the scene, and against those photographs the model lands within 2 pixels of
what the console actually drew.

The reason this took until the third report is worth writing down. The tool that
measures bubble width was reading Sega's Japanese font for base chapters, where
every English letter misses the table and falls back to a default cell width, so
every base line came out as a meaningless number and the base was never
width-checked at all. The Latin glyphs live in the `_F1` companion archive, one
font per scene.

1.0.15 was not seen running anywhere before 1.1.0. It is line breaks in eight
text tables and 28 single script bytes, each verified byte for byte on the way
in and out of both CIAs. The title screen read **ENG 1.0.15** and the DLC
stayed **TMD 0.2.8**.

## 1.0.14 / DLC 0.2.8

The rest of the bubble work from [issue #1](../../issues/1), in the base game
this time. The DLC is unchanged; if you are already on DLC 0.2.8 you only need
the base files.

A speech bubble's height is not worked out from the text. Each scene script
sets it per line, and Sega's values were chosen for the Japanese. Where an
English line needs more lines than the Japanese did, the extra line falls
outside the bubble, which is what the DLC report showed. Every base scene
script was checked against that rule and two bubbles needed a taller box: one
in Chapter 1 and one in the shared end-of-chapter script. Two bytes in total,
and the two archives are otherwise byte for byte Sega's own.

Four more base bubbles hold English that runs to more lines than the bubble
implies, but Sega's own Japanese runs to the same number or more in those same
bubbles, so they draw the way the original game draws them and were left alone.

The two bubbles were not looked at in the engine; the edit is one byte in each of two
scene scripts, and both CIAs were compared against 1.0.13 file by file. The title screen reads **ENG 1.0.14**
and the DLC stays **TMD 0.2.8**.

## 1.0.13 / DLC 0.2.8

Two fixes from the first report in [issue #1](../../issues/1) (14 September
2026, a New 3DS XL running the Japanese-voice edition). Nothing else changed.

1. **EX chapter dialogue ran off the right edge of its speech bubble.** The
   three DLC story chapters (EX Acts 8, 9 and 10) took Sega's English lines
   from the Steam release with Steam's line breaks, and the 3DS bubble is
   narrower: about 215 pixels of text room, measured on the reporter's
   screenshots. 276 of the 734 English bubbles had at least one line too
   wide. DLC 0.2.8 re-breaks those bubbles onto two or three lines so that no
   line is wider than 205 pixels. The words are Sega's and unchanged; only
   where the lines break has moved, and Sega's own Japanese script already
   uses three-line bubbles in the same scenes. The base game's chapters 1 to
   7 were left alone here. That was a mistake: they draw through a different
   font, and the tool was reading the wrong one for them, so they were never
   width-checked at all until 1.0.15.
2. **The "Time Up" call in Party mode was drawn as slices.** The game draws
   that graphic as six separate sprites, one per Japanese character, and 1.0.12
   had painted "TIME UP!" across the whole texture, so each sprite showed a
   piece of it. 1.0.13 uses Sega's own "TIME!" art from the Steam release, cut
   into one letter per sprite.

Files changed: base game 2 (the title screen stamp and the Party-mode texture
archive), DLC 3 (the three chapter text tables). Both CIAs were compared
against 1.0.12 / 0.2.7 file by file and differ in exactly those. The
Japanese-voice edition of this build was confirmed on a New 3DS XL on 14
September 2026, and again on the same console on 16 September (issue #1);
the change is line breaks in three text tables and one
texture, each verified byte for byte on the way in and out of the CIAs. The
Japanese-voice edition was rebuilt the same way and carries the same two
fixes; its release files now read 1.0.13 / 0.2.8. The title screen reads **ENG
1.0.13** and the DLC is **TMD 0.2.8**.

## 1.0.12 / DLC 0.2.7

A texture quality pass, nothing functional. The textures this patch draws
itself and that the game stores compressed (ETC1) had gone through a small
encoder that took each block's average colour and stopped there. 1.0.12
re-renders them with an encoder that searches for the best colour per block
and ignores the pixels the game never shows, so the edges of white lettering
on coloured plates come out cleaner. It covers fewer textures than I expected
when I started: eight in total. Base game: the "New Record" card and the rank
plates on the Puzzle League standby screen. DLC: the six EX chapter plates on
the Adventure map (Act number and title for each of the three chapters).
Every other file is byte-identical to 1.0.11 / 0.2.6; the title screen reads
**ENG 1.0.12** and the DLC is **TMD 0.2.7**.

Checked in Azahar. The hardware confirmation from 1.0.11 covers everything
except these eight textures. If you already have 1.0.11 and DLC 0.2.6 there's
no need to update; the difference is slightly sharper lettering on those
screens.

## 1.0.11

The first run on real hardware (a New 3DS, 6 September 2026) found a bug that
had been in every build: the error and system dialogs showed the wrong
message. The game's error table (`tenp/text/error/errorJapanese.mtx`) had a
blank entry at position 1, inherited from the earlier fan translation's files
that this project built on, so every message after it was drawn one slot late.
On a first launch that looked like "Could not read data. Turn off the power and
reinsert the SD Card." with Yes and No buttons, when the game was actually
asking whether to use SpotPass. 1.0.11 realigns the table to Sega's original
38 entries, same English text, right slots. The other 29 base text tables and
all 30 DLC tables were checked against the originals and match. Nothing else
changed; the title screen reads **ENG 1.0.11**. Confirmed on the console: the
SpotPass question now reads as itself.

If you answered that first-launch question on 1.0.10 without knowing what it
was, it was the SpotPass opt-in; the setting is in Options.

## 1.0.10

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
- One stability report from testing: starting a local
  Multiplayer host and backing out crashed the emulator (an emulator-side
  assertion, not the patch).
- Install order is unchanged: Japanese base, then patched base (or
  LayeredFS), then the Japanese v1.2.0 update (code only), then this DLC.
  The withdrawn update-title CIA note above still applies: do not use it.

1.0.9 redid the voice loudness fix, within hours of 1.0.8:

- **The 1.0.8 fix should be replaced.** It matched levels by running gain,
  a limiter, and a DSP-ADPCM re-encode three times per clip, which stacked
  four generations of encoder error. Both the 1.0.8 base voices and the DLC
  0.2.5 voices came out sounding muffled and gritty next to Sega's takes.
- **Fix: a single clean encode.** Gain and limiting are now done in
  floating point on the decoded audio, iterated until the level matches
  Sega's Japanese take, and DSP-ADPCM is encoded exactly once. Base
  battle/select/title voices now average about 1 dB below Sega's takes (62
  of 63 banks re-levelled); DLC story clips about 1.1 dB below (760 clips
  re-levelled). Pitch and timing untouched.
- **Base game**: title screen now reads **ENG 1.0.9**; the built CIA
  reports 1.0.9.
- **`PuyoPuyoTetris-DLC-patched.cia`** is now **TMD 0.2.6**.
- Nothing else changed since 1.0.8.
- If you installed 1.0.8 or DLC 0.2.5, replace them with 1.0.9 and 0.2.6.

1.0.10 changed the HOME menu banner only:

- **The HOME menu banner now shows Sega's official English "PuyoPuyo" logo**
  instead of the Japanese one, built from Sega's own banner with only the
  logo swapped, Sega's TETRIS art untouched. This lives in the locally
  built CIA only; LayeredFS cannot carry a banner, so nothing public
  changes apart from the version stamp.
- **Base game**: title screen now reads **ENG 1.0.10**; the built CIA
  reports 1.0.10.
- **`PuyoPuyoTetris-DLC-patched.cia`** stays **TMD 0.2.6**.
- Nothing else changed since 1.0.9.

---

# Earlier versions, 1.0.3 to 1.0.10

These entries used to live in TESTING.md, which is about what has been checked rather than
what changed. They are the only record of these builds and are kept here verbatim.

## What changed in 1.0.3

Found by the user playing 1.0.2 in Azahar on 2026-09-04, fixed the same day:

- **Character-select pick lines**: the fan patch had replaced only 15 of the
  24. All 24 are now from Steam's English pick bank, verified by duration
  match 24 of 24 (`work/import_select_voices.py`).
- **The title-screen announcer at boot** (sound bank 143, four takes) was a
  3DS-only bank; Steam's title_set_bank matched all four takes by duration,
  so the English takes are in (`work/import_title_set.py`).
- **The boot notice screen** was cut off on screen because the game shows
  only the left part of the texture; it is re-wrapped into the 290 px column
  the Japanese occupied (`work/notice.py`).
- **The DLC map plates** were cut off for the same reason; the English is now
  fitted into the measured Japanese ink window (`work/dlc_plates.py`); the
  long names are small (8 to 9 px).
- **The Endless-mode record card** ("Best Record", "This Run", "beaten" after
  the count) is redrawn by a dedicated script (`work/record_card.py`) that
  inpaints the gradient plates.

## What changed in 1.0.4

Found by the user playing 1.0.3 in Azahar on 2026-09-04, fixed the same day:

- **The boot notice screen was still cut off on the bottom screen**: the
  bottom screen shows a narrower window of the texture (x 70 to 315) than the
  top screen (x 60 to 350). Each half now has its own column
  (`work/notice.py`).
- **The DLC map plates** were width-fitted in a wide font and came out short
  next to Sega's "Act 1" plate. They now use Bahnschrift Bold Condensed with
  Sega's dark-green outline, fitted height-first: small plates 15 to 16 px,
  titles 14 px, "An Interstellar Dream" 11 px (`work/dlc_plates.py`).
- **Sound**: the 13 battle banks the fan patch had already made English
  carried odd per-wave sample rates (24600, 23500, 10000 Hz and so on; 236
  waves) where Sega's are 32000 Hz. All 13 are re-imported from Steam at
  Sega's rate (`work/import_fan_banks.py`), so all 37 battle banks are now
  this project's own encode: 1,517 waves, all 32000 Hz, verified.

## What changed in 1.0.5

Found by the user playing Versus matches in Azahar on 2026-09-04, bisected and fixed the same day:

- **The match-end hang is fixed.** Versus matches hung at the win/lose screen (the emulator sat at 0 FPS); Marathon never hung. The cause was the per-section font atlas fix, which had replaced any incomplete atlas member with a whole donor atlas: a 32 KB, about 130 glyph, 512x128 member could become a 131 KB, 820 glyph, 512x512 one. 60 of 101 members in the base overlay had more than doubled this way, 126 in the DLC. The Versus result screen loads three such members at once (tenp/text/win_dialogue) and stopped there. The fix is a new tool, `work/atlas_compact.py`, which subsets every swapped member down to the glyphs its section actually uses plus printable ASCII, in the donor's own cell geometry, on the smallest power of two bitmap that fits and never smaller than Sega's original. Its self test subsets Sega's own atlas to its full glyph set and reproduces it byte for byte. Result: base atlas bitmaps went from 7.4 MB to 2.0 MB across 80 members, DLC from 16.5 MB to 2.7 MB across 126 members. The user played Versus matches on the compacted build with no hang, and the winner dialogue rendered in English. One thing learned along the way: a donor can declare more glyphs than its bitmap has cells (one donor claimed 820 glyphs on a 720 cell bitmap), so indices past the last cell point outside the bitmap; the compactor drops those (one fullwidth question mark was affected).
- **The version stamp on the title logo** is now 11 px tall in the strip's full height instead of 7 px (`work/stamp_title.py`).
- **The bottom-screen notice** moved 3 px left.
- **The Swap-mode "Puyo Puyo"/"Tetris" call banners** were tried again in English and reverted: the game layers that banner from two textures and the redraw looked wrong, so it stays Sega's art. Still Japanese, as noted above.

## What changed in 1.0.6

- **The Swap-mode "Puyo"/"Tetris" call logos are now Sega's official English
  logo art**, not a hand redraw. Steam's `data/tenp/swap/swap2p/swap2p_e.narc`
  (member 3, a `tppk` container of DDS/DXT5 textures) carries a 1024x1024
  texture that is the same layout as the 3DS's `pla_swap_notice_d4444` at four
  times the size, with "Puyo" and "Tetris" where the 3DS has the Japanese
  marks. `work/swap_logos.py` scales Sega's two logos down 4x into the 3DS
  texture, touching only the logo cells (rows 102..132); the curved "PUYO
  PUYO / TET RIS" lettering and everything else is unchanged, still Sega's
  art. The earlier note that this banner stays Japanese no longer applies.
- **The bottom-screen boot notice text** moved a further 21 px left in three steps while testing, so it sits under the top-screen text
  (`work/notice.py`, bottom column centre 166).
- **The mixed-mode (Tetris side) HOLD/NEXT labels** were checked because they
  looked clipped in the emulator. The texture (`tenp/mix/mix2p/mix2P.narc`) is
  byte-identical in the Japanese original, the fan build, and this patch, and
  the user confirmed the PC version shows the same clipping, so this is
  Sega's own design and was left as shipped; a redraw was made and discarded.
- New rule: Steam's `*_e.narc` archives carry the official English textures
  (DDS/DXT5 inside `tppk` containers); check them before hand-drawing any logo.

## What changed in 1.0.7

A sweep of the Steam release's English textures for Sega's official art,
matching by text instead of position since Steam's English atlases are laid
out differently from both the 3DS atlases and Steam's own Japanese atlases:

- **222 hand-redrawn labels replaced with Sega's official English sprites**,
  including the Broadcast Station and Club mode pills (Fusion, Swap, Party,
  Big Bang, Marathon, Sprint, Ultra, Endless Puyo, Endless Fever, Tiny Puyo)
  with their proper two-tone outlines, coloured category rows, Yes/No
  buttons, and Puzzle League headers. Labels where the Steam sprite would be
  unreadable or clash in style keep the hand redraw.
- **The Replay Report badge rows (all 11)** are now Sega's official English
  art: Epic Showdown!, Master Battle!, Regional Battle!, Must Watch!, Major
  Upset!, Amazing Match!, Huge Comeback!, Back-n-Forth!, Surprise Win!, Great
  Match!, Rank Up!
- **The 15 Puzzle League rank pills** (Grand Master, Platinum, Golden,
  Legend, Superstar, Star, Virtuoso, Elite, Professional, Wizard, Ace,
  Amateur, Rookie, Beginner, Student) are now Sega's official English art;
  these were still Japanese and had not previously been listed as a known
  leftover.
- **The Broadcast Station TV logo** is now Sega's official "World Broadcast"
  mark. Earlier notes called this the "Replay TV" logo and said it was
  artwork left Japanese; that is no longer true.
- Still Japanese: the replay-speed hint strip (not found anywhere in the
  Steam data), the three DLC voice lines with no English take, the
  name-entry keyboards by design, the vertical league result art, decorative
  screenshot thumbnails, and the "New Record" ornament.

## What changed in 1.0.8

The user reported the in-battle and DLC voices sounded quiet next to the
story voices. Measured with `work/voice_levels.py` (peak and RMS in dBFS,
decoded straight from the CSAR/CSTM): Sega's Japanese 3DS takes run about
-11 dBFS RMS with peaks near 0 dBFS (heavily limited); the clips imported
from Steam's PCM sat 5 to 11 dB below that in RMS, at about -18 dBFS RMS,
with peaks already close to full scale, so a flat gain would have clipped.
The DLC story clips were about 7 dB low the same way.

Fix: `work/voice_gain.py` (base CSAR banks) and `work/voice_gain_dlc.py`
(DLC CSTM stream clips) gain each clip to the RMS of Sega's Japanese take of
the same line, through a look-ahead peak limiter (ceiling -0.5 dBFS, 1.5 ms
look-ahead, 60 ms release), then re-encode DSP-ADPCM. Three passes each,
since the limiter gives some loudness back on every pass.

- Base battle/select/title voices: 62 of 63 banks re-levelled, now averaging
  1.2 dB below Sega's takes (range -3.1 to +2.4 dB); the title announcer bank
  was already louder than Sega's and was left alone.
- DLC story clips: 734 clips re-levelled, now about 1.3 dB below Sega's takes.
- Pitch and timing untouched. The remaining gap is the limiter: my re-encoded
  takes are less compressed than Sega's.
- Nothing else changed: text, textures and atlases are as in 1.0.7.

## What changed in 1.0.9

The 1.0.8 loudness fix ran gain, limiter, and DSP-ADPCM re-encode three
times per clip to match Sega's levels, since the limiter gave some loudness
back on every pass. That stacked four generations of encoder error, and the
user heard the result as muffled and gritty next to Sega's takes.

Fix: `work/voice_gain_clean.py` decodes the once-encoded import audio,
iterates gain and look-ahead limiting in floating point until the RMS meets
Sega's Japanese take, and encodes DSP-ADPCM exactly once. Measured with
`work/voice_gain_clean.py snr`: the 1.0.8 waves ran 18 to 25 dB
signal-to-noise against the intended audio; a single clean encode runs 31
to 36 dB.

- Base battle/select/title voices: 62 of 63 banks re-levelled, now averaging
  1.0 dB below Sega's takes (range -4.5 to +2.4 dB); the title announcer
  bank was left alone, as before.
- DLC story clips: 760 clips re-levelled, now about 1.1 dB below Sega's
  takes.
- `voice_gain.py` and `voice_gain_dlc.py` (the old three-pass tools) are
  kept only as a record and are not used anymore.
- Nothing else changed since 1.0.8.

## What changed in 1.0.10

The HOME menu banner now shows Sega's official English "PuyoPuyo" logo
instead of the Japanese one. This lives only in the locally built CIA;
LayeredFS cannot carry a banner, so nothing public shows it. Nothing else
changed since 1.0.9.
