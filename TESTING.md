# Testing this patch

For anyone playing these builds and reporting back. Spoiler-free.

## What to install, in order

1. **The Japanese base game**: not distributed here. Cartridge or your own dump.
2. **The patched base game**: `PuyoPuyoTetris-Base-xdelta.zip` applied to a
   decrypted dump of your own game (see its README; this route also gives the
   English HOME menu banner), or `PuyoPuyoTetris-EN-voices-patched.cia`
   built from your dump with `tools/build_cia.py` (it replaces the base game,
   same title ID; your save carries over), or on Luma3DS the contents of
   `PuyoPuyoTetris-LayeredFS.zip` under `luma/titles/0004000000101200/`.
   For the Japanese-voice edition use `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.15.zip`
   or `PuyoPuyoTetris-JP-voices-LayeredFS.zip` instead, and in step 4
   `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. One edition or the other, not both.
3. **The Japanese v1.2.0 update** (`0004000E`, 2.4 MB): code only; installs
   over the patched base safely.
4. **`PuyoPuyoTetris-DLC-patched.cia`**: the translated DLC. Or build the same
   file yourself: `PuyoPuyoTetris-DLC-xdelta.zip` holds an xdelta3 patch for a
   decrypted dump of your own Japanese DLC, with hashes to check both ends.

**Do not use `PuyoPuyoTetris-Update-patched.cia` if you have one.** It was
published for a few hours on 2026-09-04 and withdrawn. This game's code only
ever opens the base game's RomFS (SelfNCCH path type 0) and never the update
RomFS (type 5), so an update title carrying the English files is ignored,
Azahar's log shows it loading the update's romfs and the game then reading
Sega's. Uninstall it and install the official update instead.

**Booted on a New 3DS on 6 September 2026, and on a New 3DS XL and an original
3DS on 7 September, with a few games played on hardware.** Base, Japanese update and DLC
installed; HOME menu banner English; title screen and main menu run. The first console launch showed an error dialog with the
wrong text, which turned out to be a shifted error table present since the
first build (fixed in 1.0.11, confirmed on the same console: the SpotPass
opt-in question now reads as itself). Before that, every build from 1.0.1 to
1.0.10 had been booted only in the Azahar emulator: the text pipeline works
in the engine, checked on the Options screen, the Adventure map, the DLC
chapters, the Versus result screen, the boot notice and the Swap-mode call
banners, all in English. Every file was verified byte-for-byte on the way in
and back out of the CIA, and all the writers reproduce the game's own files
byte-identically. Since then the DLC Adventure chapters have been played on a console, and
Chapter 1 through to its end; later story chapters and the 1.0.15 bubble fix are still
worth reporting.

**The Japanese-voice edition (added 11 September 2026) was booted in Azahar on
13 September**: ENG 1.0.12 stamp, main menu, a Quick Play match with audio, and
DLC EX Act 10 with its English plate and story scene. Its text and textures are
byte for byte the 1.0.12 files above; only the voice files differ, and those are
Sega's own. **Confirmed on a New 3DS XL on 14 September 2026** by the player who
asked for the edition: installed by the xdelta route, a couple of DLC Adventure
chapters played, Japanese speech in both story and gameplay under the English
text. That was the one thing the emulator run could not settle, since the voice
files matching Sega's byte for byte is not the same as hearing them.
In that edition a voice in Japanese is correct, not a bug.

**1.0.13 / DLC 0.2.8 (14 September 2026)** fix the two things the first report
in issue #1 found: EX chapter dialogue running past the right edge of its
bubble (276 of 734 bubbles re-broken onto two or three lines, words unchanged)
and the Party-mode Time Up graphic drawn as slices (now Sega's own "TIME!"
art, one letter per sprite). Confirmed on a New 3DS XL on 16 September 2026
(issue #1); the change is line
breaks in three text tables and one texture, each verified byte for byte on
the way in and out of the CIAs. Every base scene script was also checked for the second half of the same
problem, a bubble scripted for fewer lines than the English needs. Two were
found and are raised in **1.0.14** (14 September 2026): one in Chapter 1, one
in the shared end-of-chapter script. The Chapter 1 one was photographed
drawing correctly on a New 3DS XL on 17 September 2026; the shared one has
still not been seen running.

The base chapters were not re-wrapped for width at that point, and should
have been. The tool that measures line width was reading Sega's Japanese font
for them, so every base line came out as a meaningless number and nobody
looked again. The third report in issue #1 (17 September 2026) photographed a
base line running onto the border. **1.0.15** re-breaks 162 lines in 160
bubbles across Chapters 1 to 7 and the shared script so no line is wider than
193 pixels, the widest width a photograph shows drawing cleanly, and raises 28
bubbles to hold the line that results. Words unchanged. None of it has been
seen running, so screenshots of any Adventure scene are worth having.

## How to tell which build you have

- The title screen logo's pink subtitle strip reads **ENG 1.0.15** at its right end.
- The console lists the base game as version **1.0.15** (a locally built CIA)
  and the DLC as **0.2.8** (the fan build and the shipped DLC were 0.0.0 / 0.1.0).

If the stamp is missing, the install did not take.

## If something looks or sounds wrong

Tell me, even if you think it's on the list below. **[Issue #1](../../issues/1)** is the
place. Say which screen, and a photo beats a description. Don't spend time working out
whether I already know. A duplicate costs me nothing and a report somebody talked
themselves out of costs me a bug.

These are the ones I'd most like to hear about, because they're the ways this patch fails:

- **Anything blank.** A menu label, a line of dialogue, a results-screen entry
  that renders as nothing. This is the failure mode of the font-atlas work and
  the one I most want to hear about, say which screen.
- **Text sitting too high or too low in its box, or clipped**, especially on
  the online results screen and the Club screens.
- **A voice that is silent or cut off**: say which character or which DLC scene.
- **Anything that fails to load**: a scene, the DLC shop, a Club screen.
- **Anything at all on real hardware**, good or bad.

### Already known

Here for context, not as a filter. Several of these overlap with the list above, so if
you're looking at something and you're not sure which side it falls on, just tell me.

- **A few dozen strings are Japanese on purpose.** The character-entry
  keyboards (the hiragana/katakana/kanji inventories in name entry) and the
  developer tables define what can be typed; they are not translations waiting
  to happen.
- **Three DLC story lines stay Japanese** (chapter 8 scene 5, chapter 9 scenes
  4 and 7). Those lines were re-recorded for the 3DS and have no English take.
- **Voices are a little duller than the story voices.** Every in-battle and
  DLC voice is re-encoded from Steam's PCM with a home-grown encoder whose
  coefficient search is weaker than Sega's. Pitch and timing are correct.
  As of 1.0.9 the levels are matched to within about 1 dB of Sega's own
  Japanese takes (measured RMS, look-ahead limited so nothing clips). The
  1.0.8 encode had a noise problem from stacked re-encoding, fixed in 1.0.9.
- **Stylised mode names in the online menus (Fusion, Swap, Party, Big Bang)
  are plain white** where the Japanese had a thick two-tone outline.
- **Prefecture buttons in the online rankings are tiny.** Nine-letter names in
  boxes drawn for two kanji.
- **Score digits, 1P/2P/COM badges, You/New!/VS/ON/OFF** were already Latin.
- **A few merged/rotated strings on the league result screen are Japanese**:
  the vertical "you lose" / "congratulations" art doesn't split cleanly from
  the artwork around it.
- **The replay-speed hint strip stays Japanese.**
- **Decorative screenshot thumbnails and the small "New Record" ornament are
  Japanese**, deliberately left as artwork.
- **Starting a local Multiplayer host and backing out crashed the emulator.**
  The Azahar log ends on an assertion in its local-wireless service
  (nwm_uds.cpp line 864); that is the emulator, not the patch. On real
  hardware this path is untested.
- **The match-end hang is fixed in 1.0.5.** See below.

## Where to look first

1. Main Menu and My Data: the control group; text injected through the
   game's original font atlases.
2. The **online results screen** (`net_result`): 161 strings through swapped
   atlases; baseline drift would show here.
3. **Club screens**: redrawn textures on every label.
4. **Chapter 0** of Adventure: hand-written prologue.
5. Any **character-select shout**: re-encoded battle voice.
6. **DLC chapter 8**: text, atlases, voices and shop icons all at once.

## Testing status

| | |
|---|---|
| Adventure bubble line widths | measured through each scene's own Latin atlas and calibrated to within 2 px against console photographs; every drawn line is at or under 193 px as of 1.0.15, but no 1.0.15 bubble has been seen running |
| Text, base and DLC | verified per font atlas section; **seen in the engine 2026-09-04** on the Options screen, Adventure map, and DLC chapters |
| Font atlas swaps | verified by rendering the shipped text through the shipped atlas; confirmed on-screen where the boot above reached |
| Battle and DLC voices | decoded back and compared to source (27 to 37 dB); never heard. All 37 battle banks are now this project's own encode at Sega's 32000 Hz (1,517 waves, verified); the 13 re-imported for 1.0.4 fix a sample-rate mismatch the fan build had left in |
| Character-select pick lines and title-screen announcer | verified by duration against Steam and confirmed by the user by ear from the decoded clip |
| Online UI textures | rendered and reviewed as images; not yet confirmed in the engine beyond the screens above |
| Boot notice and DLC plates | seen in the engine (Azahar); Endless-mode record card not yet checked |
| Title version stamp | seen in Azahar and in the tester's console screenshots; ENG 1.0.15 decoded back out of both built CIAs |
| Update-title packaging | structurally correct, booted in Azahar, **ignored by the game**: withdrawn |
| Versus result screen | **confirmed in the engine by the user 2026-09-04**: no hang, winner dialogue in English after the atlas-compact fix |
| Emulator | **booted 2026-09-04**: Options screen, Adventure map, DLC chapters, Versus result screen, all in English |
| Real hardware | **booted 2026-09-06 (New 3DS) and 2026-09-07 (New 3DS XL, original 3DS)**, a few games played; DLC Adventure chapters played on a New 3DS XL on 14 and 16 September 2026, and Chapter 1 through to its end on 17 September (issue #1); no full story playthrough yet |
