This is a fan made English patch for Puyo Puyo Tetris on 3DS. It carries Sega's own official English text and voice work over from the PC release, DLC included. Everything below covers what changed in each build and whether you need to update anything.

## Japanese-voice edition

If you would rather keep the original Japanese voice acting alongside the English text and menus, this edition is for you. Story scenes, in-battle callouts, character select, the title-screen announcer, the HOME menu jingle and all three DLC chapters play Sega's original Japanese performances, while everything you read on screen stays in English.

It installs the same way as the main patch, using its own set of files on the release page, and it carries the same version number and on-screen stamp as the English-voice build, so only one edition can be installed at a time. The HOME menu jingle is the quickest way to tell which one you have running.

This edition has been confirmed working on real 3DS hardware, with Japanese speech heard through a story chapter and several matches, and it gets rebuilt alongside every update to the main patch.

## 1.0.15 / DLC 0.2.8

This update re-breaks the line breaks in the base game's story dialogue so no line of text runs past the edge of its speech bubble. Earlier builds carried line breaks meant for a wider text box, so a number of lines in the main story chapters pushed past where the bubble stops. Nothing about the wording changes, not a single word is added, removed or altered, only where each line splits. A number of bubbles also grew slightly taller so their text fits properly.

The DLC is unchanged, so if you are already on the current DLC release you only need to update the base game files. This build has not yet been confirmed running on a console or in an emulator, though every file going in and out of it was checked carefully. If you spot a bubble that still looks wrong, please report it.

## 1.0.14 / DLC 0.2.8

This update finishes the speech bubble height fixes reported by a player, this time for the base game rather than the DLC. A speech bubble's height in this game is not worked out automatically from how much text it holds. Each scene sets that height by hand, and it was set to fit the original Japanese line lengths. Where an English line needed more room than the Japanese did, the last line could spill past the bottom of the bubble.

Two bubbles in the base game needed a taller box and now have one. A few other bubbles run to more lines in English than in Japanese, but the original game already draws those the same way, so they were left as they are. The DLC is unchanged, so update the base files only if you already have the current DLC.

## 1.0.13 / DLC 0.2.8

Two fixes from the first player report on this project. First, dialogue in the three DLC story chapters sometimes ran off the right edge of its speech bubble. Those chapters had reused line breaks from the PC release, whose text box is wider than the 3DS allows, so a good number of bubbles needed rewrapping onto two or three lines. The words themselves are unchanged, still Sega's own English text, only where the lines break has moved.

Second, the "Time Up" banner in Party mode had been drawn as several broken pieces instead of one clean word. It now uses Sega's own "Time!" artwork instead.

The base game's main story chapters were not touched in this update, since they turned out to need this same kind of fix too, which arrived later in 1.0.15.

## 1.0.12 / DLC 0.2.7

A visual quality pass, nothing that changes how the game plays. A handful of textures drawn by this patch itself had been compressed with a basic method that softened fine detail, so this update redraws them with a better method that keeps edges sharp. That mostly shows up as cleaner white lettering on colored plates and cards.

A small set of textures were redone this way: the "New Record" card and the rank plates on the Puzzle League standby screen in the base game, plus the DLC chapter plates on the Adventure map. Everything else is identical to 1.0.11 and its matching DLC.

This build was checked in an emulator rather than on hardware, though earlier hardware testing still covers everything except these textures. If you already have 1.0.11, updating is optional, the only difference is sharper lettering on a few screens.

## 1.0.11

The first test on real 3DS hardware turned up a bug present in every earlier build: error messages and system dialogs showed the wrong text. A blank entry near the start of the game's error message list, left over from the fan translation this patch builds on, pushed every message after it into the wrong slot. On first launch, that made the game's SpotPass question read like a corrupted save warning, complete with the wrong buttons.

This update realigns that list to match Sega's original layout, so every message appears in its correct spot with the same English wording as before. Every other text table in the base game and DLC was checked against the originals and confirmed to match. Nothing else changed. If you answered that confusing first-launch question on an earlier build without knowing what it was, it was the SpotPass opt-in, which you can still change from the options menu.

## 1.0.10

This build wraps up a long stretch of early work, most of it already superseded by later updates above, so it is summarized here rather than repeated in full.

Earlier updates in this stretch replaced many remaining Japanese textures with Sega's own official English artwork, including menu labels, mode badges, rank icons and a broadcast logo, matched by reading their text rather than guessing their position on screen. Character voices across the base game and DLC were re-leveled twice, once with a rough fix that left them sounding a bit muffled, then again with a cleaner pass that matches Sega's own Japanese volume without that side effect. If you installed a build from partway through this stretch, replace it with something newer.

This update itself only changes the HOME menu banner, swapping in Sega's official English logo. Everything else carries over from the build before it.

The full technical history, including every measurement behind these updates, is kept in BUILD_NOTES.md.
