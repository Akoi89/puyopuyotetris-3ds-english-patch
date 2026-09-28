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
   For the Japanese-voice edition use the equivalent Japanese-voice xdelta
   zip or LayeredFS zip instead, and in step 4 the Japanese-voice DLC CIA.
   One edition or the other, not both.
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

## How to tell which build you have

- The title screen logo's pink subtitle strip reads **ENG 1.1.1** at its right
  end on both editions. This is the first build where the Japanese-voice
  edition carries the same version stamp as the English-voice one, since
  neither of this build's fixes touches a voice file; the HOME menu jingle is
  now the only way to tell which edition is running.
- The console lists the base game as version **1.1.1** and the DLC as
  **0.2.10**, on either edition (the fan build and the shipped DLC were
  0.0.0 / 0.1.0).
- **Japanese-voice edition**: same title ID as the English-voice build, so
  install one edition or the other; the HOME menu jingle is the way to tell
  which one you have running. In that edition a voice in Japanese is
  correct, not a bug.

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
- **Anything at all on real hardware, good or bad.**
- **Later story chapters, and the 1.0.15 bubble fix.** DLC chapters and
  Chapter 1 have been played on a console; later story chapters and whether
  1.0.15's re-broken lines draw correctly are still worth reporting.
- **Screenshots of any Adventure scene.** None of 1.0.15's line-break fix has
  been seen running anywhere, so a screenshot of any story scene helps confirm
  it drew the way it should. The same goes for this build's own re-worded
  lines: none of them have been seen running yet either.
- **Any battle shout, DLC voice line or story voice heard on hardware.** None
  of 1.1.0's or this build's re-leveled voices have been heard outside this
  project yet.
- **Both Broadcast Station screens.** This build's new replay badges sit on
  online screens I can't reach offline, so they haven't been seen running yet.
- **This build's new art on a console.** The mission screen's "New!" tag and
  the DLC stage's shop sign and icon were checked in Azahar, not yet on hardware.

## Already known

Here for context, not as a filter. Several of these overlap with the list above, so if
you're looking at something and you're not sure which side it falls on, just tell me.

- **A few dozen strings are Japanese on purpose.** The character-entry
  keyboards (the hiragana/katakana/kanji inventories in name entry) and the
  developer tables define what can be typed; they are not translations waiting
  to happen.
- **Three DLC story lines stay Japanese** (chapter 8 scene 5, chapter 9 scenes
  4 and 7). Those lines were re-recorded for the 3DS and have no English take.
- **Voices can sound a touch less crisp than on PC.** Every English voice is
  re-encoded from Steam's recordings with a home-grown encoder that's a little
  weaker than Sega's. Pitch and timing are correct.
- **Stylised mode names in the online menus (Fusion, Swap, Party, Big Bang)
  are plain white** where the Japanese had a thick two-tone outline.
- **The HOLD and NEXT labels on the Tetris side of a mixed match look
  clipped at the top.** That's Sega's own art; the PC version shows the same
  clipping.
- **Prefecture buttons in the online rankings are tiny.** Nine-letter names in
  boxes drawn for two kanji.
- **Score digits, 1P/2P/COM badges, You/New!/VS/ON/OFF** were already Latin.
- **A few merged/rotated strings on the league result screen are Japanese**:
  the vertical "you lose"/"congratulations" art doesn't split cleanly from
  the artwork around it.
- **The replay-speed hint strip stays Japanese.**
- **Decorative screenshot thumbnails and the small "New Record" ornament are
  Japanese**, deliberately left as artwork.
- **A faint Puzzle League medal crest stays Japanese.** Sega's own English
  version of that crest read worse once it was fitted here, so the Japanese
  one was kept on purpose.
- **The Slot rule's "N more Puyo" counter is Japanese.** There's no English
  version of that art in Sega's PC release to draw from.
- **A handful of online menu preview cards are Japanese.** They're baked into
  the background art, and Sega's PC release has no matching English scene for
  any of them.
- **Starting a local Multiplayer host and backing out crashed the emulator.**
  The Azahar log ends on an assertion in its local-wireless service
  (nwm_uds.cpp line 864); that is the emulator, not the patch. On real
  hardware this path is untested.

## Where to look first

1. Main Menu and My Data: the control group; text injected through the
   game's original font atlases.
2. The **online results screen** (`net_result`): 161 strings through swapped
   atlases; baseline drift would show here.
3. **Club screens**: redrawn textures on every label.
4. **Chapter 0** of Adventure: hand-written prologue.
5. Any **character-select shout**: re-encoded battle voice.
6. **DLC chapter 8**: text, atlases, voices and shop icons all at once.
7. **The Adventure map's mission screen and both Broadcast Station screens**:
   this build's new art.

## Testing status

| | |
|---|---|
| Adventure bubble line widths | measured through each scene's own Latin atlas and calibrated to within 2 px against console photographs; every drawn line is at or under 193 px as of 1.0.15, but no 1.0.15 bubble has been seen running |
| 1.0.14 bubble raises | the Chapter 1 bubble was photographed drawing correctly on a New 3DS XL on 17 September 2026; the shared end-of-chapter script bubble has not been seen running |
| This build's re-worded lines | the lines that had still carried the earlier fan translation's wording now carry Sega's; rewrapped and, where needed, given a taller bubble the same way as 1.0.15's fix; the opening scene of Chapter 1 played in Azahar on 28 September 2026, and its re-worded first line ("This is not good!") was seen and heard there; the other re-worded lines haven't been seen on screen yet |
| Text, base and DLC | verified per font atlas section; **seen in the engine 2026-09-04** on the Options screen, Adventure map, and DLC chapters |
| Font atlas swaps | verified by rendering the shipped text through the shipped atlas; confirmed on-screen where the boot below reached |
| Battle, DLC and story voices | decoded back and compared to source; never heard on hardware. All 37 battle banks are this project's own encode at Sega's 32000 Hz (1,517 waves, verified); the 13 re-imported for 1.0.4 fix a sample-rate mismatch the fan build had left in; 1.1.0 re-levels the quiet battle and DLC voices and re-imports the crackly base-game story voices; this build re-levels the base-game story voices a second time, gentler, toward the Japanese level; each pass re-verified byte for byte, but not yet heard outside this project |
| This build's art (mission "New!" tag, Broadcast Station badges, DLC shop sign and icon) | rendered and reviewed as images; the "New!" tag and the DLC shop sign (stage preview and a live match) seen in Azahar on 28 September 2026; the Broadcast Station badges only as images, since those screens are online |
| Character-select pick lines and title-screen announcer | verified by duration against Steam and confirmed by the user by ear from the decoded clip |
| Online UI textures | rendered and reviewed as images; not yet confirmed in the engine beyond the screens above |
| Boot notice and DLC plates | seen in the engine (Azahar); Endless-mode record card not yet checked |
| Title version stamp | seen in Azahar and in the tester's console screenshots through 1.1.0; **ENG 1.1.1** seen in Azahar on 28 September 2026, not yet on a console |
| Update-title packaging | structurally correct, booted in Azahar, **ignored by the game**: withdrawn |
| Versus result screen | **confirmed in the engine by the user 2026-09-04**: no hang, winner dialogue in English after the atlas-compact fix |
| Emulator | **booted 2026-09-04**: Options screen, Adventure map, DLC chapters, Versus result screen, all in English. Later emulator runs, before the first hardware boot, also showed the boot notice screen and the Swap-mode call banners in English |
| Real hardware | **booted 2026-09-06 (New 3DS) and 2026-09-07 (New 3DS XL, original 3DS)**, a few games played; DLC Adventure chapters played on a New 3DS XL on 14 and 16 September 2026, and Chapter 1 through to its end on 17 September (issue #1); no full story playthrough yet; 1.1.0's re-leveled battle shouts heard in a Versus match in Azahar, not yet on a console; this build was booted in Azahar on 28 September 2026 (title screen, a Versus match on the DLC stage, Adventure Act 1), not yet on a console |
| Japanese-voice edition | booted in Azahar on 13 September 2026; **confirmed on a New 3DS XL on 14 September 2026** by the player who asked for it; rebuilt alongside every base update through 1.0.15 with the same line-break fix; 1.1.0 did not touch it, so it stayed at 1.0.15 / DLC 0.2.8; this build's text and art fixes aren't voice files, so this edition is rebuilt again and moves to 1.1.1 / DLC 0.2.10, the same as the English-voice build, but has not been booted yet |
| File verification | every file is verified byte-for-byte on the way in and back out of the CIA, and all the writers reproduce the game's own files byte-identically |

Full build-by-build history, including every measurement behind these updates, is kept in
BUILD_NOTES.md.
