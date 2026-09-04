# Testing this patch

For anyone playing these builds and reporting back. Spoiler-free.

## What to install, in order

1. **The Japanese base game** — not distributed here. Cartridge or your own dump.
   Leave it exactly as it is.
2. **`PuyoPuyoTetris-Update-patched.cia`** — the translation, packaged as the
   game's **update** (title `0004000E`). It is Sega's own v1.2.0 update code with
   the English game data appended, so it replaces the official update and the
   base game is never touched. Your save carries over.
3. **`PuyoPuyoTetris-DLC-patched.cia`** — the translated DLC.

If the official Japanese v1.2.0 update is already installed, the update CIA
replaces it (the console then shows 1.3.0 instead of 1.2.0). If the earlier
full-base build (`PuyoPuyoTetris-EN-voices-patched.cia`, 1.0.0) is installed it
can stay; the update's data takes precedence. Luma3DS users can instead unpack
`PuyoPuyoTetris-LayeredFS.zip` into `luma/titles/0004000000101200/` and keep
the official update.

**None of this has ever been booted** — not on hardware, not in an emulator.
Every file was verified byte-for-byte on the way in and back out of the CIA,
and all the writers reproduce the game's own files byte-identically, but that
is verification, not testing. If you are the first to boot it, that alone is
worth reporting.

## How to tell which build you have

- The title screen logo's pink subtitle strip reads **ENG 1.0.0** at its right end.
- The console lists the update as version **1.3.0** (the official update is
  1.2.0) and the DLC as **0.2.0** (the shipped DLC was 0.1.0). The earlier
  full-base build shows the base game itself as 1.0.0.

If the stamp is missing, the install did not take.

## Known and expected — please don't report these

- **A few dozen strings are Japanese on purpose.** The character-entry
  keyboards (the hiragana/katakana/kanji inventories in name entry) and the
  developer tables define what can be typed; they are not translations waiting
  to happen.
- **Three DLC story lines stay Japanese** (chapter 8 scene 5, chapter 9 scenes
  4 and 7). Those lines were re-recorded for the 3DS and have no English take.
- **Voices are a little duller than the story voices.** Every in-battle and
  DLC voice is re-encoded from Steam's PCM with a home-grown encoder whose
  coefficient search is weaker than Sega's. Pitch and timing are correct.
- **Stylised mode names in the online menus (Fusion, Swap, Party, Big Bang)
  are plain white** where the Japanese had a thick two-tone outline.
- **Prefecture buttons in the online rankings are tiny.** Nine-letter names in
  boxes drawn for two kanji.
- **The animated "Replay TV" logo in the Broadcast Station is Japanese.** It is
  artwork, not a label.
- **Score digits, 1P/2P/COM badges, You/New!/VS/ON/OFF** were already Latin.

## What is worth reporting

- **Anything blank.** A menu label, a line of dialogue, a results-screen entry
  that renders as nothing. This is the failure mode of the font-atlas work and
  the one I most want to hear about — say which screen.
- **Text sitting too high or too low in its box, or clipped**, especially on
  the online results screen and the Club screens.
- **A voice that is silent, cut off, or in Japanese** — say which character or
  which DLC scene.
- **Anything that fails to load** — a scene, the DLC shop, a Club screen.
- **Anything at all on real hardware**, good or bad.

## Where to look first

1. Main Menu and My Data — the control group; text injected through the
   game's original font atlases.
2. The **online results screen** (`net_result`) — 161 strings through swapped
   atlases; baseline drift would show here.
3. **Club screens** — redrawn textures on every label.
4. **Chapter 0** of Adventure — hand-written prologue.
5. Any **character-select shout** — re-encoded battle voice.
6. **DLC chapter 8** — text, atlases, voices and shop icons all at once.

## Testing status, honestly

| | |
|---|---|
| Text, base and DLC | verified per font atlas section, never seen on screen |
| Font atlas swaps | verified by rendering the shipped text through the shipped atlas |
| Battle and DLC voices | decoded back and compared to source (27–37 dB); never heard |
| Online UI textures | rendered and reviewed as images; never seen in the engine |
| Title version stamp | rendered; never seen in the engine |
| Update-title packaging | the header maths strip and re-add the base game's own romfs byte-for-byte, and 3dstool reads the identical romfs back out of the update; never booted |
| Emulator / hardware | **never** |
