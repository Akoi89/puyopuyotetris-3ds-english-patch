# Testing this patch

For anyone playing these builds and reporting back. Spoiler-free.

## What to install, in order

1. **The Japanese base game** — not distributed here. Cartridge or your own dump.
2. **The patched base game** — either `PuyoPuyoTetris-EN-voices-patched.cia`
   built from your dump with `tools/build_cia.py` (it replaces the base game,
   same title ID; your save carries over), or on Luma3DS the contents of
   `PuyoPuyoTetris-LayeredFS.zip` under `luma/titles/0004000000101200/`.
3. **The Japanese v1.2.0 update** (`0004000E`, 2.4 MB) — code only; installs
   over the patched base safely.
4. **`PuyoPuyoTetris-DLC-patched.cia`** — the translated DLC.

**Do not use `PuyoPuyoTetris-Update-patched.cia` if you have one.** It was
published for a few hours on 2026-09-04 and withdrawn. This game's code only
ever opens the base game's RomFS (SelfNCCH path type 0) and never the update
RomFS (type 5), so an update title carrying the English files is ignored —
Azahar's log shows it loading the update's romfs and the game then reading
Sega's. Uninstall it and install the official update instead.

**None of this has ever been booted** — not on hardware, not in an emulator.
Every file was verified byte-for-byte on the way in and back out of the CIA,
and all the writers reproduce the game's own files byte-identically, but that
is verification, not testing. If you are the first to boot it, that alone is
worth reporting.

## How to tell which build you have

- The title screen logo's pink subtitle strip reads **ENG 1.0.1** at its right end.
- The console lists the base game as version **1.0.1** (a locally built CIA)
  and the DLC as **0.2.0** (the fan build and the shipped DLC were 0.0.0 / 0.1.0).

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
| Update-title packaging | structurally correct, booted in Azahar, **ignored by the game** — withdrawn |
| Emulator / hardware | **never** |
