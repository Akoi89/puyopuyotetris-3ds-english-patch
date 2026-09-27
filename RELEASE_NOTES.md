This is a fan English patch for *Puyo Puyo Tetris* on 3DS, carrying Sega's own official English text and voice work over from the PC release, DLC included. This page covers what the patch fixes overall, one line of history per build, and what's still known to be off.

## What this build fixes

- **Story lines running past the edge of their speech bubble.** The base game's dialogue kept line breaks sized for a wider text box, so lines in the main story chapters pushed past where the bubble stops. The words are unchanged, not one is added, removed or altered, only where each line splits. This build has not yet been confirmed running on a console or in an emulator; if you spot a bubble that still looks wrong, please report it.
- **Lines spilling past the bottom of a speech bubble.** A speech bubble's height in this game is set by hand for each scene, sized to the original Japanese line lengths, so an English line that needed more room could run past the bottom edge. The affected bubbles are now taller.
- **DLC dialogue running off the right edge of its bubble.** The three DLC story chapters kept line breaks sized for the PC release's wider text box; they're rewrapped for the 3DS bubble, words unchanged.
- **The Party-mode "Time Up" banner drawn as broken pieces instead of one clean word.** It now uses Sega's own "Time!" artwork.
- **Wrong text in error messages and system dialogs**, including the first-launch SpotPass prompt reading like a save-corruption warning. A blank entry near the start of the error message list had pushed every later message into the wrong slot; the list now matches Sega's original layout. If you answered that confusing first-launch question on an earlier build without knowing what it was, it was the SpotPass opt-in, which you can still change from the options menu.
- **Soft, blurry lettering on a handful of this patch's own textures** (the "New Record" card, the rank plates, the DLC map plates). They had been compressed with a method that softened fine detail and are now redrawn with one that keeps edges sharp.
- **Character voices sounding muffled after the first loudness fix.** Character voices across the base game and DLC were re-leveled twice, once with a rough fix that left them sounding a bit muffled, then again with a cleaner pass that matches Sega's own Japanese volume without that side effect.
- **A Japanese-voice edition, for anyone who'd rather keep the original cast.** Story scenes, in-battle callouts, character select, the title-screen announcer, the HOME menu jingle and all three DLC chapters play Sega's original Japanese performances, while everything you read on screen stays in English. It installs the same way as the main patch and gets rebuilt alongside every update to it.

## Version history

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
- Voices are a little duller than the story voices. Every in-battle and DLC voice is re-encoded from Steam's PCM with a home-grown encoder whose coefficient search is weaker than Sega's. Pitch and timing are correct. The levels are matched to within about 1 dB of Sega's own Japanese takes (measured RMS, look-ahead limited so nothing clips).
- Stylised mode names in the online menus (Fusion, Swap, Party, Big Bang) are plain white where the Japanese had a thick two-tone outline.
- Prefecture buttons in the online rankings are tiny: nine-letter names in boxes drawn for two kanji.
- A few merged/rotated strings on the league result screen are Japanese: the vertical "you lose" / "congratulations" art doesn't split cleanly from the artwork around it.
- The replay-speed hint strip stays Japanese, along with decorative screenshot thumbnails and the small "New Record" ornament, left as artwork on purpose.
- Starting a local Multiplayer host and backing out crashed the emulator; this is an emulator-side assertion, not the patch, and is untested on real hardware.

The full list, with what to report and how, is in TESTING.md.

## Files

Install order is the Japanese base game, then the patched base, then the Japanese v1.2.0 update, then the patched DLC.

- **Base game**: `PuyoPuyoTetris-xdelta-patches-1.0.15.zip` (the base and DLC xdelta3 patches together, with a readme carrying every hash; the file romhacking.net links to), or `PuyoPuyoTetris-Base-xdelta.zip` on its own (xdelta3 patch for your own decrypted dump; the only route to the English HOME menu banner), or `PuyoPuyoTetris-LayeredFS.zip` for Luma3DS.
- **DLC**: `PuyoPuyoTetris-DLC-patched.cia`, or `PuyoPuyoTetris-DLC-xdelta.zip` for your own decrypted DLC dump.
- **Japanese-voice edition**: `PuyoPuyoTetris-JP-voices-xdelta-patches-1.0.15.zip`, `PuyoPuyoTetris-JP-voices-LayeredFS.zip` and `PuyoPuyoTetris-DLC-JP-voices-0.2.8.cia`. Install one edition or the other, not both.

If you're using any of the xdelta zips, dump the title as an encrypted CIA with GodMode9 and decrypt it on the PC; GodMode9's own decrypt gives a file of the right size that the patch will refuse. Sizes and hashes for every file are in the README.

The full technical history, including every measurement behind these updates, is kept in BUILD_NOTES.md.

## Credits

Sega for the text and voices.

ongo_gablogian and the original translation team, for the Adventure story and the UI texture work that made the game playable in English at all.

Partyderp64, whose `PPT3dsENG_0.3dx` build put English story voices over that translation and is the fan shell this patch is built from.

Tooling reused from the TGAA 3DS patch (3dstool, ctrtool, the CIA and NCCH writers).
