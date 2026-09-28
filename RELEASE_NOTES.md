This is a fan English patch for *Puyo Puyo Tetris* on 3DS, carrying Sega's own official English text and voice work over from the PC release, DLC included. This page covers what the patch fixes overall, one line of history per build, and what's still known to be off.

## What this build fixes

- **Story dialogue running past the edge of its speech bubble, or off the bottom.** The base game's dialogue kept line breaks and box heights sized for a wider text box, so English lines pushed past where the bubble stops, and a few ran below the bottom edge. Words unchanged; only where lines split and how tall a handful of bubbles are.
- **DLC dialogue running off the right edge of its bubble.** The three DLC story chapters kept line breaks sized for the PC release's wider text box; they're rewrapped for the 3DS bubble, words unchanged.
- **Wrong text in error messages and system dialogs**, including the first-launch SpotPass prompt reading like a save-corruption warning. A blank entry near the start of the error message list had pushed every later message into the wrong slot; the list now matches Sega's original layout. If you answered that question on an earlier build without knowing what it was, it was the SpotPass opt-in, changeable from the options menu.
- **Some battle shouts and DLC voice lines sounding clearly quieter than the Japanese lines they replace**, worst on characters like Dark Prince, Feli, Tee, Ess and Zed. Steam's English recordings are mastered at a lower volume, and the earlier fix for this was capped too low; they're re-leveled from Steam's recordings in one clean pass and now sit close to the Japanese volume.
- **Story (Adventure) voices crackling on loud lines.** They came from the earlier fan translation, which had turned Steam's recordings up and cut off the loudest parts. Re-imported from Steam in one clean pass, each set to the volume of the Japanese line it replaces; one English-only line keeps its earlier version.
- **LayeredFS players hearing the story in Japanese even when using the English voice edition.** The LayeredFS zip never carried the English story voices; only the built CIA or xdelta routes did. It now includes them, so it's a much bigger download than before.
- **A Japanese-voice edition, for anyone who'd rather keep the original cast.** Story scenes, in-battle callouts, character select, the title-screen announcer, the HOME menu jingle and all three DLC chapters play Sega's original Japanese performances, while everything you read stays in English. This build's fixes are all in voices this edition doesn't use, so it's unchanged and stays at 1.0.15 / DLC 0.2.8.

## Version history

- **1.1.0 / DLC 0.2.9**: re-leveled quiet battle and DLC voices, and re-imported crackly story voices in one clean pass; LayeredFS now includes the English story voices for the first time.
- **1.0.15 / DLC 0.2.8**: re-broke the base game's Adventure dialogue so no line runs past its bubble.
- **1.0.14 / DLC 0.2.8**: raised base-game speech bubbles that were cutting off their last line.
- **1.0.13 / DLC 0.2.8**: rewrapped DLC dialogue to fit its bubbles and redrew the Party-mode "Time Up" graphic as one clean word.
- **1.0.12 / DLC 0.2.7**: redrew a handful of this patch's own textures (the "New Record" card, rank plates, DLC map plates) with sharper lettering.
- **1.0.11**: realigned the error-message table to Sega's layout, fixing the misplaced first-launch SpotPass prompt.
- **1.0.10 / DLC 0.2.6**: swapped the HOME menu banner to Sega's official English logo.
- **1.0.9 / DLC 0.2.6**: redid the voice loudness fix with a single clean encode after the earlier pass left voices sounding muffled.
- **1.0.8 / DLC 0.2.5**: raised the in-battle and DLC voices to Sega's Japanese volume, first pass.
- **1.0.7 / DLC 0.2.4**: swept Steam's English textures for official label art, including the Puzzle League rank pills.
- **1.0.6**: swapped the Swap-mode call logos to Sega's official English art and nudged the boot notice further left.
- **1.0.5**: fixed a Versus-match hang at the win/lose screen.
- **1.0.4**: fixed the boot notice on the bottom screen, refit the DLC map plates, and brought back the fan build's English battle voices at Sega's sample rate.
- **1.0.3**: fixed the character-select pick lines, the title-screen announcer, the boot notice, the DLC map plates and the Endless-mode record card.
- **1.0.2**: added a full texture survey, a second label pass, and more imported voice sets.
- **1.0.1**: folded in a second-opinion review of the hand-written text.

## Known problems

- A few dozen strings are Japanese on purpose: the character-entry keyboards (the hiragana/katakana/kanji inventories in name entry) and the developer tables define what can be typed and aren't translations waiting to happen.
- Three DLC story lines stay Japanese (chapter 8 scene 5, chapter 9 scenes 4 and 7); those lines were re-recorded for the 3DS and have no English take.
- Voices can sound a touch less crisp than on PC. Every English voice is re-encoded from Steam's recordings with a home-grown encoder that's a little weaker than Sega's. Pitch and timing are correct.
- Stylised mode names in the online menus (Fusion, Swap, Party, Big Bang) are plain white where the Japanese had a thick two-tone outline.
- Prefecture buttons in the online rankings are tiny: nine-letter names in boxes drawn for two kanji.
- A few merged/rotated strings on the league result screen are Japanese: the vertical "you lose" / "congratulations" art doesn't split cleanly from the artwork around it.
- The replay-speed hint strip stays Japanese, along with decorative screenshot thumbnails and the small "New Record" ornament, left as artwork on purpose.
- Starting a local Multiplayer host and backing out crashed the emulator; this is an emulator-side assertion, not the patch, and is untested on real hardware.

The full list, with what to report and how, is in TESTING.md.

## Files

Install order is the Japanese base game, then the patched base, then the Japanese v1.2.0 update, then the patched DLC.

- **Base game**: `PuyoPuyoTetris-xdelta-patches-1.1.0.zip` (the base and DLC xdelta3 patches together, with a readme carrying every hash; the file romhacking.net links to), or `PuyoPuyoTetris-Base-xdelta.zip` on its own (xdelta3 patch for your own decrypted dump; the only route to the English HOME menu banner), or `PuyoPuyoTetris-LayeredFS.zip` for Luma3DS, now much bigger since it includes the English story voices for the first time.
- **DLC**: `PuyoPuyoTetris-DLC-patched.cia`, or `PuyoPuyoTetris-DLC-xdelta.zip` for your own decrypted DLC dump.
- **Japanese-voice edition**: `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.15.zip`, `PuyoPuyoTetris-JP-voices-LayeredFS.zip` and `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. Unchanged this build and still at 1.0.15 / DLC 0.2.8. Install one edition or the other, not both.

If you're using any of the xdelta zips, dump the title as an encrypted CIA with GodMode9 and decrypt it on the PC; GodMode9's own decrypt gives a file of the right size that the patch will refuse. Sizes and hashes for every file are in the README.

The full technical history, including every measurement behind these updates, is kept in BUILD_NOTES.md.

## Credits

Sega for the text and voices.

ongo_gablogian and the original translation team, for the Adventure story and the UI texture work that made the game playable in English at all.

Partyderp64, whose `PPT3dsENG_0.3dx` build put English story voices over that translation and is the fan shell this patch is built from.

Tooling reused from the TGAA 3DS patch (3dstool, ctrtool, the CIA and NCCH writers).
