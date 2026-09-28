This is a fan English patch for *Puyo Puyo Tetris* on 3DS, carrying Sega's own official English text and voice work over from the PC release, DLC included. This page covers what the patch fixes overall, one line of history per build, and what's still known to be off.

## What this build fixes

- **Some story, tutorial and profile lines still read the earlier fan translation's wording, typos and all.** A mission target could read "10,00 pts" where it meant 10,000, and the opening story line read "This it not good!" Those lines, and others like them across the Adventure story, the lesson screens and the profile/records screens, now read Sega's official English instead, refitted to the 3DS speech bubbles. Sega's wording is kept as written, except that a few records lines spell out "percent" because the 3DS font has no % sign, and a couple of bubbles grew a line taller to hold the result.
- **Story (Adventure) voices, re-leveled again.** 1.1.0 brought these up toward the Japanese volume and a few of the loudest lines ended up sounding squashed. They're re-leveled a second time to sit as close to the Japanese volume as they can without squashing, and they still don't crackle.
- **The Adventure mission screen's red "New!" tag is now Sega's English art**, replacing a Japanese banner that had been sitting above "Versus" on that screen.
- **The Broadcast Station's replay badges are now Sega's English art**, on both places that screen appears; they'd read as an untranslated grid of Japanese badges before.
- **The DLC stage's shop sign and its stage-select icon now read "Ando Family FRESH PRODUCE"** in Sega's own lettering, where both had shown the Japanese sign before.
- **Some graphics are still Japanese or clipped.** The Slot rule's "N more Puyo" counter and a handful of online menu preview cards are still Japanese because Sega's PC release has no English version of them. A faint Puzzle League medal crest stays Japanese on purpose: Sega's English one looked worse at the 3DS crest's size. The clipped HOLD/NEXT labels on the Tetris side, already reported in issue #1, are listed too.

## Version history

- **1.1.1 / DLC 0.2.10**: Sega's official English on lines that had kept the earlier fan translation's wording; a second, gentler voice re-level for the base game's story voices; Steam's official art for the Adventure "New!" tag, the Broadcast Station badges, and the DLC stage's shop sign and icon. The Japanese-voice edition gets the text and art fixes too and now shares the same version number.
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
- The HOLD and NEXT labels on the Tetris side of a mixed match look clipped at the top; that's Sega's own art, and the PC version shows the same clipping.
- Prefecture buttons in the online rankings are tiny: nine-letter names in boxes drawn for two kanji.
- A few merged/rotated strings on the league result screen are Japanese: the vertical "you lose" / "congratulations" art doesn't split cleanly from the artwork around it.
- The replay-speed hint strip stays Japanese, along with decorative screenshot thumbnails and the small "New Record" ornament, left as artwork on purpose.
- A faint Puzzle League medal crest stays Japanese; Sega's own English version of it read worse once fitted here, so the Japanese one was kept.
- The Slot rule's "N more Puyo" counter and a handful of online menu preview cards stay Japanese; Sega's PC release has no matching English art for either.
- Starting a local Multiplayer host and backing out crashed the emulator; this is an emulator-side assertion, not the patch, and is untested on real hardware.

The full list, with what to report and how, is in TESTING.md.

## Files

Install order is the Japanese base game, then the patched base, then the Japanese v1.2.0 update, then the patched DLC.

- **Base game**: `PuyoPuyoTetris-xdelta-patches-1.1.1.zip` (the base and DLC xdelta3 patches together, with a readme carrying every hash; the file romhacking.net links to), or `PuyoPuyoTetris-Base-xdelta.zip` on its own (xdelta3 patch for your own decrypted dump; the only route to the English HOME menu banner), or `PuyoPuyoTetris-LayeredFS.zip` for Luma3DS.
- **DLC**: `PuyoPuyoTetris-DLC-patched.cia`, or `PuyoPuyoTetris-DLC-xdelta.zip` for your own decrypted DLC dump.
- **Japanese-voice edition**: `PuyoPuyoTetris-JP-voices-xdelta-patches-1.1.1.zip`, `PuyoPuyoTetris-JP-voices-LayeredFS.zip` and `PuyoPuyoTetris-DLC-JP-voices-0.2.10.cia`. Rebuilt this time along with the main release, since the text and art fixes aren't voice files; now at the same 1.1.1 / DLC 0.2.10 as the English-voice build. Install one edition or the other, not both.

If you're using any of the xdelta zips, dump the title as an encrypted CIA with GodMode9 and decrypt it on the PC; GodMode9's own decrypt gives a file of the right size that the patch will refuse. Sizes and hashes for every file are in the README.

The full technical history, including every measurement behind these updates, is kept in BUILD_NOTES.md.

## Credits

Sega for the text and voices.

ongo_gablogian and the original translation team, for the Adventure story and the UI texture work that made the game playable in English at all.

Partyderp64, whose `PPT3dsENG_0.3dx` build put English story voices over that translation and is the fan shell this patch is built from.

Tooling reused from the TGAA 3DS patch (3dstool, ctrtool, the CIA and NCCH writers).
