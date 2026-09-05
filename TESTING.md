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

**Booted in Azahar, not yet on real hardware.** Every build from 1.0.1 to
1.0.6 has been booted in the Azahar emulator on 2026-09-04: it runs, and the
text pipeline works in the engine: checked on the Options screen, the
Adventure map, the DLC chapters, the Versus result screen, the boot notice
and the Swap-mode call banners, all in English. Every file was also verified byte-for-byte on the way in and
back out of the CIA, and all the writers reproduce the game's own files
byte-identically. Real hardware is still untested: if you boot it on a
console, that alone is worth reporting.

## How to tell which build you have

- The title screen logo's pink subtitle strip reads **ENG 1.0.10** at its right end.
- The console lists the base game as version **1.0.10** (a locally built CIA)
  and the DLC as **0.2.6** (the fan build and the shipped DLC were 0.0.0 / 0.1.0).

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

## What changed in 1.0.3

Found by the user playing 1.0.2 in Azahar on 2026-09-04, fixed the same day:

- **Character-select pick lines**: the fan patch had replaced only 15 of the
  24. All 24 are now from Steam's English pick bank, verified by duration
  match 24 of 24 (`work/import_select_voices.py`).
- **The title-screen announcer at boot** (sound bank 143, four takes) was a
  3DS-only bank; Steam's title_set_bank matched all four takes by duration,
  so the English takes are in (`work/import_title_set.py`).
- **The boot notice screen** was cut off on screen because the game shows
  only the left part of the texture; it is re-wrapped into the 290 px column
  the Japanese occupied (`work/notice.py`).
- **The DLC map plates** were cut off for the same reason; the English is now
  fitted into the measured Japanese ink window (`work/dlc_plates.py`); the
  long names are small (8 to 9 px).
- **The Endless-mode record card** ("Best Record", "This Run", "beaten" after
  the count) is redrawn by a dedicated script (`work/record_card.py`) that
  inpaints the gradient plates.

## What changed in 1.0.4

Found by the user playing 1.0.3 in Azahar on 2026-09-04, fixed the same day:

- **The boot notice screen was still cut off on the bottom screen**: the
  bottom screen shows a narrower window of the texture (x 70 to 315) than the
  top screen (x 60 to 350). Each half now has its own column
  (`work/notice.py`).
- **The DLC map plates** were width-fitted in a wide font and came out short
  next to Sega's "Act 1" plate. They now use Bahnschrift Bold Condensed with
  Sega's dark-green outline, fitted height-first: small plates 15 to 16 px,
  titles 14 px, "An Interstellar Dream" 11 px (`work/dlc_plates.py`).
- **Sound**: the 13 battle banks the fan patch had already made English
  carried odd per-wave sample rates (24600, 23500, 10000 Hz and so on; 236
  waves) where Sega's are 32000 Hz. All 13 are re-imported from Steam at
  Sega's rate (`work/import_fan_banks.py`), so all 37 battle banks are now
  this project's own encode: 1,517 waves, all 32000 Hz, verified.

## What changed in 1.0.5

Found by the user playing Versus matches in Azahar on 2026-09-04, bisected and fixed the same day:

- **The match-end hang is fixed.** Versus matches hung at the win/lose screen (the emulator sat at 0 FPS); Marathon never hung. The cause was the per-section font atlas fix, which had replaced any incomplete atlas member with a whole donor atlas: a 32 KB, about 130 glyph, 512x128 member could become a 131 KB, 820 glyph, 512x512 one. 60 of 101 members in the base overlay had more than doubled this way, 126 in the DLC. The Versus result screen loads three such members at once (tenp/text/win_dialogue) and stopped there. The fix is a new tool, `work/atlas_compact.py`, which subsets every swapped member down to the glyphs its section actually uses plus printable ASCII, in the donor's own cell geometry, on the smallest power of two bitmap that fits and never smaller than Sega's original. Its self test subsets Sega's own atlas to its full glyph set and reproduces it byte for byte. Result: base atlas bitmaps went from 7.4 MB to 2.0 MB across 80 members, DLC from 16.5 MB to 2.7 MB across 126 members. The user played Versus matches on the compacted build with no hang, and the winner dialogue rendered in English. One thing learned along the way: a donor can declare more glyphs than its bitmap has cells (one donor claimed 820 glyphs on a 720 cell bitmap), so indices past the last cell point outside the bitmap; the compactor drops those (one fullwidth question mark was affected).
- **The version stamp on the title logo** is now 11 px tall in the strip's full height instead of 7 px (`work/stamp_title.py`).
- **The bottom-screen notice** moved 3 px left.
- **The Swap-mode "Puyo Puyo"/"Tetris" call banners** were tried again in English and reverted: the game layers that banner from two textures and the redraw looked wrong, so it stays Sega's art. Still Japanese, as noted above.

## What changed in 1.0.6

- **The Swap-mode "Puyo"/"Tetris" call logos are now Sega's official English
  logo art**, not a hand redraw. Steam's `data/tenp/swap/swap2p/swap2p_e.narc`
  (member 3, a `tppk` container of DDS/DXT5 textures) carries a 1024x1024
  texture that is the same layout as the 3DS's `pla_swap_notice_d4444` at four
  times the size, with "Puyo" and "Tetris" where the 3DS has the Japanese
  marks. `work/swap_logos.py` scales Sega's two logos down 4x into the 3DS
  texture, touching only the logo cells (rows 102..132); the curved "PUYO
  PUYO / TET RIS" lettering and everything else is unchanged, still Sega's
  art. The earlier note that this banner stays Japanese no longer applies.
- **The bottom-screen boot notice text** moved a further 21 px left in three steps while testing, so it sits under the top-screen text
  (`work/notice.py`, bottom column centre 166).
- **The mixed-mode (Tetris side) HOLD/NEXT labels** were checked because they
  looked clipped in the emulator. The texture (`tenp/mix/mix2p/mix2P.narc`) is
  byte-identical in the Japanese original, the fan build, and this patch, and
  the user confirmed the PC version shows the same clipping, so this is
  Sega's own design and was left as shipped; a redraw was made and discarded.
- New rule: Steam's `*_e.narc` archives carry the official English textures
  (DDS/DXT5 inside `tppk` containers); check them before hand-drawing any logo.

## What changed in 1.0.7

A sweep of the Steam release's English textures for Sega's official art,
matching by text instead of position since Steam's English atlases are laid
out differently from both the 3DS atlases and Steam's own Japanese atlases:

- **222 hand-redrawn labels replaced with Sega's official English sprites**,
  including the Broadcast Station and Club mode pills (Fusion, Swap, Party,
  Big Bang, Marathon, Sprint, Ultra, Endless Puyo, Endless Fever, Tiny Puyo)
  with their proper two-tone outlines, coloured category rows, Yes/No
  buttons, and Puzzle League headers. Labels where the Steam sprite would be
  unreadable or clash in style keep the hand redraw.
- **The Replay Report badge rows (all 11)** are now Sega's official English
  art: Epic Showdown!, Master Battle!, Regional Battle!, Must Watch!, Major
  Upset!, Amazing Match!, Huge Comeback!, Back-n-Forth!, Surprise Win!, Great
  Match!, Rank Up!
- **The 15 Puzzle League rank pills** (Grand Master, Platinum, Golden,
  Legend, Superstar, Star, Virtuoso, Elite, Professional, Wizard, Ace,
  Amateur, Rookie, Beginner, Student) are now Sega's official English art;
  these were still Japanese and had not previously been listed as a known
  leftover.
- **The Broadcast Station TV logo** is now Sega's official "World Broadcast"
  mark. Earlier notes called this the "Replay TV" logo and said it was
  artwork left Japanese; that is no longer true.
- Still Japanese: the replay-speed hint strip (not found anywhere in the
  Steam data), the three DLC voice lines with no English take, the
  name-entry keyboards by design, the vertical league result art, decorative
  screenshot thumbnails, and the "New Record" ornament.

## What changed in 1.0.8

The user reported the in-battle and DLC voices sounded quiet next to the
story voices. Measured with `work/voice_levels.py` (peak and RMS in dBFS,
decoded straight from the CSAR/CSTM): Sega's Japanese 3DS takes run about
-11 dBFS RMS with peaks near 0 dBFS (heavily limited); the clips imported
from Steam's PCM sat 5 to 11 dB below that in RMS, at about -18 dBFS RMS,
with peaks already close to full scale, so a flat gain would have clipped.
The DLC story clips were about 7 dB low the same way.

Fix: `work/voice_gain.py` (base CSAR banks) and `work/voice_gain_dlc.py`
(DLC CSTM stream clips) gain each clip to the RMS of Sega's Japanese take of
the same line, through a look-ahead peak limiter (ceiling -0.5 dBFS, 1.5 ms
look-ahead, 60 ms release), then re-encode DSP-ADPCM. Three passes each,
since the limiter gives some loudness back on every pass.

- Base battle/select/title voices: 62 of 63 banks re-levelled, now averaging
  1.2 dB below Sega's takes (range -3.1 to +2.4 dB); the title announcer bank
  was already louder than Sega's and was left alone.
- DLC story clips: 734 clips re-levelled, now about 1.3 dB below Sega's takes.
- Pitch and timing untouched. The remaining gap is the limiter: our takes
  are less compressed than Sega's.
- Nothing else changed: text, textures and atlases are as in 1.0.7.

## What changed in 1.0.9

The 1.0.8 loudness fix ran gain, limiter, and DSP-ADPCM re-encode three
times per clip to match Sega's levels, since the limiter gave some loudness
back on every pass. That stacked four generations of encoder error, and the
user heard the result as muffled and gritty next to Sega's takes.

Fix: `work/voice_gain_clean.py` decodes the once-encoded import audio,
iterates gain and look-ahead limiting in floating point until the RMS meets
Sega's Japanese take, and encodes DSP-ADPCM exactly once. Measured with
`work/voice_gain_clean.py snr`: the 1.0.8 waves ran 18 to 25 dB
signal-to-noise against the intended audio; a single clean encode runs 31
to 36 dB.

- Base battle/select/title voices: 62 of 63 banks re-levelled, now averaging
  1.0 dB below Sega's takes (range -4.5 to +2.4 dB); the title announcer
  bank was left alone, as before.
- DLC story clips: 760 clips re-levelled, now about 1.1 dB below Sega's
  takes.
- `voice_gain.py` and `voice_gain_dlc.py` (the old three-pass tools) are
  kept only as a record and are not used anymore.
- Nothing else changed since 1.0.8.

## What changed in 1.0.10

The HOME menu banner now shows Sega's official English "PuyoPuyo" logo
instead of the Japanese one. This lives only in the locally built CIA;
LayeredFS cannot carry a banner, so nothing public shows it. Nothing else
changed since 1.0.9.

## Testing status, honestly

| | |
|---|---|
| Text, base and DLC | verified per font atlas section; **seen in the engine 2026-09-04** on the Options screen, Adventure map, and DLC chapters |
| Font atlas swaps | verified by rendering the shipped text through the shipped atlas; confirmed on-screen where the boot above reached |
| Battle and DLC voices | decoded back and compared to source (27 to 37 dB); never heard. All 37 battle banks are now this project's own encode at Sega's 32000 Hz (1,517 waves, verified); the 13 re-imported for 1.0.4 fix a sample-rate mismatch the fan build had left in |
| Character-select pick lines and title-screen announcer | verified by duration against Steam and confirmed by the user by ear from the decoded clip |
| Online UI textures | rendered and reviewed as images; not yet confirmed in the engine beyond the screens above |
| Boot notice, DLC plates and Endless-mode record card | rendered and reviewed, not yet seen in the engine after the fix |
| Title version stamp | rendered; never seen in the engine |
| Update-title packaging | structurally correct, booted in Azahar, **ignored by the game**: withdrawn |
| Versus result screen | **confirmed in the engine by the user 2026-09-04**: no hang, winner dialogue in English after the atlas-compact fix |
| Emulator | **booted 2026-09-04**: Options screen, Adventure map, DLC chapters, Versus result screen, all in English |
| Real hardware | **never** |
