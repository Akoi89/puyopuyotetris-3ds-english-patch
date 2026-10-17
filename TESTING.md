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

- The title screen logo's pink subtitle strip reads **ENG 1.1.2** at its right
  end on both editions. The Japanese-voice edition carries the same version
  stamp as the English-voice one, since this build's redrawn pictures aren't
  voice files; the HOME menu jingle is the only way to tell which edition is
  running.
- The console lists the base game as version **1.1.2** and the DLC as
  **0.2.11**, on either edition (the fan build and the shipped DLC were
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
  it drew the way it should. The same goes for 1.1.1's re-worded
  lines: only the opening scene has been seen running.
- **Any battle shout, DLC voice line or story voice heard on hardware.** None
  of 1.1.0's or 1.1.1's re-leveled voices have been heard outside this
  project yet.
- **Both Broadcast Station screens.** 1.1.1's new replay badges sit on
  online screens I can't reach offline, so they haven't been seen running yet.
- **1.1.1's new art on a console.** The mission screen's "New!" tag and
  the DLC stage's shop sign and icon were checked in Azahar, not yet on hardware.
- **This build's redrawn pictures on a console.** The menus (two of them
  tile previews on the main menu), the Club, the internet, replay and results
  screens, the "Ready" call, the tournament card and the DLC chapter strips have been looked at in an emulator only. A label that runs
  past its box, a grid that looks uneven, or a plate or icon that's missing
  is worth a photo.

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
- **A few labels are wider than the box the original art had for them, and
  some of the small grids use condensed lettering to fit.**
- **Four small rank-suffix pictures, the Japanese mark that follows a rank
  number, are still Japanese** on two replay and league screens.
- **The right-hand column on the tournament screens is text the game builds
  itself, and it may read oddly.**
- **Eleven other pictures still show Japanese.** Mostly small tile previews I did not redraw: one picture holding six tile previews (league standings, stats, game settings, the EX chapter 8 tile, a replay tile and club info), three Solo Arcade tile pictures (their mode, level and counter labels), two rule-settings pictures (Classic, Wins, Margin Time and similar labels; I have not confirmed either is shown in the game), the vertical club sign-up label, the replay speed hint strip, the "this league's results" text at the top right of one result screen, and two Puzzle League emblem pictures (faint laurels, and a dark emblem I could not read).
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
   1.1.1's new art.
8. **Any screen with redrawn pictures** (this build): the menus (including
   the main menu's Online and My Data tile previews), Club, internet, replay
   and results screens, the "Ready" call before a match, the tournament card
   and the DLC chapter strips.

## Testing status

| | |
|---|---|
| Adventure bubble line widths | measured through each scene's own Latin atlas and calibrated to within 2 px against console photographs; every drawn line is at or under 193 px as of 1.0.15, but no 1.0.15 bubble has been seen running |
| 1.0.14 bubble raises | the Chapter 1 bubble was photographed drawing correctly on a New 3DS XL on 17 September 2026; the shared end-of-chapter script bubble has not been seen running |
| 1.1.1's re-worded lines | the lines that had still carried the earlier fan translation's wording now carry Sega's; rewrapped and, where needed, given a taller bubble the same way as 1.0.15's fix; the opening scene of Chapter 1 played in Azahar on 28 September 2026, and its re-worded first line ("This is not good!") was seen and heard there; the other re-worded lines haven't been seen on screen yet |
| Text, base and DLC | verified per font atlas section; **seen in the engine 2026-09-04** on the Options screen, Adventure map, and DLC chapters |
| Font atlas swaps | verified by rendering the shipped text through the shipped atlas; confirmed on-screen where the boot below reached |
| Battle, DLC and story voices | decoded back and compared to source; never heard on hardware. All 37 battle banks are this project's own encode at Sega's 32000 Hz (1,517 waves, verified); the 13 re-imported for 1.0.4 fix a sample-rate mismatch the fan build had left in; 1.1.0 re-levels the quiet battle and DLC voices and re-imports the crackly base-game story voices; 1.1.1 re-levels the base-game story voices a second time, gentler, toward the Japanese level; each pass re-verified byte for byte, but not yet heard outside this project |
| 1.1.1's art (mission "New!" tag, Broadcast Station badges, DLC shop sign and icon) | rendered and reviewed as images; the "New!" tag and the DLC shop sign (stage preview and a live match) seen in Azahar on 28 September 2026; the Broadcast Station badges only as images, since those screens are online |
| Character-select pick lines and title-screen announcer | verified by duration against Steam and confirmed by the user by ear from the decoded clip |
| 1.1.2's redrawn pictures (111) | each one decoded back out of the patched archives and out of the built CIAs and compared with its source image, 111 of 111 matching in both editions with 0 failures; the title stamp read back out of the built base CIAs as an image; checked on an emulator only (Azahar, English-voice edition). First pass, on an earlier 1.1.2 build: the title stamp, main menu tiles, Options, Solo Arcade tiles, Versus setup and rules panel, pause menus, My Data and the Adventure mission panel with its "New!" tag, all in English. Second pass, on the final build: the "Ready" call whole in Endless Puyo, Endless Fever, Marathon, Sprint, Tiny Puyo and Ultra, the main menu Online tile preview ("Must Watch!", "Choose a replay"), the My Data Options tile preview (Location "Tokyo") and the Endless Puyo Puyo mode card, with no crash, freeze or garbling. Not seen: "Ready" in a versus match (the pass was cut short), the DLC chapter strips, the tournament card, or anything on a console |
| Online UI textures | rendered and reviewed as images; not yet confirmed in the engine beyond the screens above |
| Boot notice and DLC plates | seen in the engine (Azahar); Endless-mode record card not yet checked |
| Title version stamp | seen in Azahar and in the tester's console screenshots through 1.1.0; **ENG 1.1.1** seen in Azahar on 28 September 2026; **ENG 1.1.2** read back out of the built CIAs as an image and seen in Azahar on an earlier 1.1.2 build (English-voice edition), not yet on a console |
| Update-title packaging | structurally correct, booted in Azahar, **ignored by the game**: withdrawn |
| Versus result screen | **confirmed in the engine by the user 2026-09-04**: no hang, winner dialogue in English after the atlas-compact fix |
| Emulator | **booted 2026-09-04**: Options screen, Adventure map, DLC chapters, Versus result screen, all in English. Later emulator runs, before the first hardware boot, also showed the boot notice screen and the Swap-mode call banners in English |
| Real hardware | **booted 2026-09-06 (New 3DS) and 2026-09-07 (New 3DS XL, original 3DS)**, a few games played; DLC Adventure chapters played on a New 3DS XL on 14 and 16 September 2026, and Chapter 1 through to its end on 17 September (issue #1); no full story playthrough yet; 1.1.0's re-leveled battle shouts heard in a Versus match in Azahar, not yet on a console; 1.1.1 was booted in Azahar on 28 September 2026 (title screen, a Versus match on the DLC stage, Adventure Act 1); 1.1.2 has been checked on an emulator only, not yet on a console |
| Japanese-voice edition | booted in Azahar on 13 September 2026; **confirmed on a New 3DS XL on 14 September 2026** by the player who asked for it; rebuilt alongside every base update through 1.0.15 with the same line-break fix; 1.1.0 did not touch it, so it stayed at 1.0.15 / DLC 0.2.8; 1.1.1's text and art fixes aren't voice files, so it moved to 1.1.1 / DLC 0.2.10; 1.1.2's redrawn pictures aren't either, so it moves with the English-voice build to 1.1.2 / DLC 0.2.11; neither of those two builds of this edition has been booted, in Azahar or on a console (the 1.1.2 emulator passes were on the English-voice edition only) |
| File verification | every file is verified byte-for-byte on the way in and back out of the CIA, and all the writers reproduce the game's own files byte-identically |

Full build-by-build history, including every measurement behind these updates, is kept in
BUILD_NOTES.md.
