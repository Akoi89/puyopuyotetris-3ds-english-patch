# Testing this patch

For anyone playing these builds and reporting back. Spoiler-free.

## What to install, in order

1. **The Japanese base game**: not distributed here. Cartridge or your own dump.
2. **The patched base game**: either `PuyoPuyoTetris-EN-voices-patched.cia`
   built from your dump with `tools/build_cia.py` (it replaces the base game,
   same title ID; your save carries over), or on Luma3DS the contents of
   `PuyoPuyoTetris-LayeredFS.zip` under `luma/titles/0004000000101200/`.
3. **The Japanese v1.2.0 update** (`0004000E`, 2.4 MB): code only; installs
   over the patched base safely.
4. **`PuyoPuyoTetris-DLC-patched.cia`**: the translated DLC.

**Do not use `PuyoPuyoTetris-Update-patched.cia` if you have one.** It was
published for a few hours on 2026-09-04 and withdrawn. This game's code only
ever opens the base game's RomFS (SelfNCCH path type 0) and never the update
RomFS (type 5), so an update title carrying the English files is ignored,
Azahar's log shows it loading the update's romfs and the game then reading
Sega's. Uninstall it and install the official update instead.

**Booted in Azahar, not yet on real hardware.** The user booted 1.0.1 in the
Azahar emulator on 2026-09-04: it runs, and the text pipeline works in the
engine: checked on the Options screen, the Adventure map, and DLC chapters,
all in English. Every file was also verified byte-for-byte on the way in and
back out of the CIA, and all the writers reproduce the game's own files
byte-identically. Real hardware is still untested: if you boot it on a
console, that alone is worth reporting.

## How to tell which build you have

- The title screen logo's pink subtitle strip reads **ENG 1.0.2** at its right end.
- The console lists the base game as version **1.0.2** (a locally built CIA)
  and the DLC as **0.2.1** (the fan build and the shipped DLC were 0.0.0 / 0.1.0).

If the stamp is missing, the install did not take.

## Known and expected: please don't report these

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
- **A few merged/rotated strings on the league result screen are Japanese**:
  the vertical "you lose" / "congratulations" art doesn't split cleanly from
  the artwork around it.
- **The replay-speed hint strip stays Japanese.**
- **The Swap-mode Puyo/Tetris logos are Japanese.** Decorative logotype, not text.
- **Decorative screenshot thumbnails and the small "New Record" ornament are
  Japanese**, deliberately left as artwork.
- **The Broadcast Station category badge rows on the Replay Report stay
  Japanese**, not yet redrawn.

## What is worth reporting

- **Anything blank.** A menu label, a line of dialogue, a results-screen entry
  that renders as nothing. This is the failure mode of the font-atlas work and
  the one I most want to hear about, say which screen.
- **Text sitting too high or too low in its box, or clipped**, especially on
  the online results screen and the Club screens.
- **A voice that is silent, cut off, or in Japanese**: say which character or
  which DLC scene.
- **Anything that fails to load**: a scene, the DLC shop, a Club screen.
- **Anything at all on real hardware**, good or bad.

## Where to look first

1. Main Menu and My Data: the control group; text injected through the
   game's original font atlases.
2. The **online results screen** (`net_result`): 161 strings through swapped
   atlases; baseline drift would show here.
3. **Club screens**: redrawn textures on every label.
4. **Chapter 0** of Adventure: hand-written prologue.
5. Any **character-select shout**: re-encoded battle voice.
6. **DLC chapter 8**: text, atlases, voices and shop icons all at once.

## Testing status, honestly

| | |
|---|---|
| Text, base and DLC | verified per font atlas section; **seen in the engine 2026-09-04** on the Options screen, Adventure map, and DLC chapters |
| Font atlas swaps | verified by rendering the shipped text through the shipped atlas; confirmed on-screen where the boot above reached |
| Battle and DLC voices | decoded back and compared to source (27 to 37 dB); never heard |
| Online UI textures | rendered and reviewed as images; not yet confirmed in the engine beyond the screens above |
| Title version stamp | rendered; never seen in the engine |
| Update-title packaging | structurally correct, booted in Azahar, **ignored by the game**: withdrawn |
| Emulator | **booted 2026-09-04**: Options screen, Adventure map, DLC chapters, all in English |
| Real hardware | **never** |
