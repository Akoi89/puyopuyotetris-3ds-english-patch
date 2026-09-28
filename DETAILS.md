# Puyo Puyo Tetris 3DS patch: the detail

The full table of what changed and what stayed Japanese, by screen and system.


---

## What was done

| area | |
|---|---|
| Text | 1,411 base strings and 875 DLC strings. Sega's Steam text where it exists; 392 lines written for the 3DS-only screens (Chapter 0 prologue, Club, SpotPass, errors, shop). This build replaces 367 base lines that had still carried the earlier fan translation's wording, typos and wrong numbers included, with Sega's own text for the same lines, rewrapped for the 3DS bubble; 2 bubbles grew a line taller to hold the result. Booted in
Azahar on 28 September 2026: the opening story scene played with the new text, the first
line confirmed against the game data and the screen captures showing the lines after it;
the remaining rewritten lines have not been seen running yet. |
| In-battle, select and title-call voices | 24 Japanese character banks replaced from Steam's English recordings, matched by the Japanese takes' durations (zero error); the other 13 banks, already English from the earlier fan translation, are re-imported from Steam too, so all 37 battle banks are this project's own encode at Sega's sample rate (`import_fan_banks.py`). Re-levelled for 1.1.0 by `voice_relevel3.py`, one encode per wave from Steam's recording: 1,626 of 1,641 waves re-levelled, 15 kept the 1.0.15 bytes; battle waves within 1 LU of the Japanese take went from 772 to 998 of 1,519, more than 2 LU under from 311 to 59. Unchanged this build. |
| DLC story voices | 760 of 763 clips; the other three were re-recorded for 3DS and have no English take. Re-levelled for 1.1.0 by the same tool: 755 of 760 re-levelled, 5 kept the 0.2.8 bytes; within 1 LU of the Japanese take went from 479 to 538 of 760. Unchanged this build. |
| Base game story (Adventure) voices | 2,320 of 2,321 MZV streams re-imported from Steam's recording for 1.1.0 (`import_story_voices.py` with `voice_relevel3.py`), each aimed at the Japanese stream's loudness; the English-only MZV_07_01_1_039 has no Japanese take or matching Steam row and keeps its shipped audio. This build re-levels the same 2,320 streams a second time, gentler: lines louder than the Japanese take come down to it, and lines quieter rise toward it only as far as a 2% limiting cap allows, so nothing squashes; 1,145 files changed from the 1.1.0 bytes, 1,175 stayed byte-identical; raised lines land at
or within 0.1 LU above the Japanese level, and no stream has a clipped run of samples. Not
yet heard running. |
| Online UI textures | 1,028 label boxes across the Club, Puzzle League, standby, replay and shop screens, 806 of them redrawn here and 222 using Sega's own sprites. This build adds Sega's official English for the Adventure mission screen's "New!" tag, the Broadcast Station badges (11) on both places that screen appears, and the DLC stage's shop sign and stage-select icon. Booted in Azahar on 28 September 2026:
the mission screen's tag and the DLC stage's shop sign showed correctly; the Broadcast
Station screens are online-only and still checked only as rendered images, not confirmed
running. |
| DLC shop icons | 33 redrawn, plus this build's DLC stage shop sign and icon above. |
| Font atlases | the game pre-renders only the glyphs each screen uses; every screen that gained English got a matching atlas, verified per section |
| Character-select pick lines | all 24 (the fan patch had only 15), matched to Steam's English pick bank by duration |
| Title-screen announcer | the boot call, matched to Steam's title_set_bank by duration across all four takes |
| Boot notice and DLC map plates | re-wrapped/re-fitted into the Japanese texture's own ink window after a first pass cut them off |
| Endless-mode record card | "Best Record", "This Run" and the "beaten" count redrawn with the gradient plates inpainted |
| Swap-mode call logos | Sega's official English "Puyo" / "Tetris" logo art, taken from the Steam release's English swap texture (the 3DS texture at 4x) and scaled down into place |
| Official Steam sprites | 222 hand-redrawn labels replaced with Sega's official English sprites matched by text against the Steam release, including the Broadcast Station and Club mode pills with their proper two-tone outlines; plus the 11 Replay Report badge rows, the 15 Puzzle League rank pills, and the Broadcast Station TV logo (Sega's "World Broadcast" mark), none of which the label match had caught. This build adds the mission-screen "New!" tag, the second set of Broadcast Station badges, and the DLC shop sign and icon, all matched the same way. The mission tag and the DLC shop
sign and icon were confirmed on screen in Azahar on 28 September 2026; the Broadcast Station
badges are still checked only as rendered images. |
| HOME menu banner | Sega's official English "PuyoPuyo" logo swapped into the shared texture in place of the Japanese one, keeping Sega's TETRIS art untouched; this is in a locally built CIA only, since LayeredFS cannot change a banner |

Still Japanese on purpose, added this build: a faint Puzzle League medal crest (Sega's
English version read worse once fitted here), the Slot rule's "N more Puyo" counter, and a
handful of online menu preview cards; none of the three has a usable English source in
Sega's PC release. What stays Japanese, and why, is in [TESTING.md](TESTING.md). The
Japanese-voice edition carries this build's text and art fixes too, since neither touches a
voice file; the voice work in this row and the two above it is not in that edition.

---

## How it works

`tools/` holds everything, GPL-3.0-or-later. The parts worth knowing about:

- `mtx.py`, `narc.py`: the text and archive formats; byte-exact on the
  untouched ROM.
- `dsp.py`, `csar.py`: a DSP-ADPCM encoder (3,944 of 3,950 frames identical
  to Sega's own) and CSTM / CWAV / CWAR / CSAR writers, each byte-identical
  rebuilding the game's files.
- `atlas_fix2.py`, `check_glyphs.py`: the per-section font-atlas rule, the one
  thing everything else depends on.
- `atlas_compact.py`: subsets a swapped-in donor atlas back down to the
  glyphs its section actually uses, so a font fix does not quadruple the
  memory a screen needs to load.
- `labels.py`, `labels2.py`: find text labels on texture atlases, group
  identical ones, and redraw them from `labels_en_*.json` / `labels2_en.json`.
- `survey2.py`, `tex.py`: a full-archive texture survey and a codec for every
  CTPK format plus Sega's COMP container; `comp.py` is the COMP (LZ11 +
  header) codec on its own.
- `record_card.py`, `notice.py`, `prefectures.py`, `dlc_plates.py`,
  `swap_logos.py`: dedicated redraw scripts for the Endless-mode record card,
  the boot notice screen, the Options prefecture list, the DLC map plates,
  and the Swap-mode call logos (those come from Steam's English textures;
  Steam's `*_e.narc` archives hold official English art worth checking before
  drawing anything by hand).
- `steam_sweep.py`, `steam_ocr.ps1`, `steam_text.py`, `steam_manual.py`: sweep
  every Steam English texture against its Japanese twin, OCR the results, and
  match them to this project's texture labels by text (Steam's atlases are
  laid out differently from the 3DS's, so position doesn't work) to pull in
  more of Sega's official English art.
- `import_extra_voices.py`, `import_select_voices.py`, `import_title_set.py`:
  import the launch title calls, the character-select confirm and pick
  lines, and the title-screen announcer from Steam's voice banks.
- `import_story_voices.py`: re-imports the base game's story (Adventure) voice
  streams from Steam's master, on the shipped stream as template.
- `voice_levels.py`: measures peak and RMS in dBFS against Sega's Japanese
  takes.
- `voice_gain_clean.py`: decodes the once-encoded import audio, iterates
  gain and look-ahead limiting in floating point across a small set of
  candidate profiles until the level matches Sega's Japanese take under a
  per-frame noise guard, then encodes DSP-ADPCM a single time per wave or
  stream (`voice_gain.py` and `voice_gain_dlc.py`, an earlier multi-pass
  version, are kept only for reference and are not used anymore). The 1.1.0
  pass re-ran this against every battle, select, title and DLC voice and
  every base-game story stream; a candidate that could not beat the shipped
  bytes on its own terms keeps the shipped bytes exactly.
- `import_fan_banks.py`: re-imports the 13 battle banks the earlier fan
  translation had already made English, at Sega's sample rate, so all 37
  battle banks are this project's own encode.
- `banner_build.py`: swaps only the Japanese logo slot in the HOME menu
  banner's shared RGB565 texture for Steam's high-resolution English logo,
  downscaled with Lanczos, keeping Sega's TETRIS art and the rest of the
  texture untouched, then rebuilds the CBMD.
- `banner_cwav.py` (English title call into the banner audio), `exefs_banner.py`: splices the new banner into the ExeFS in place (only
  1,170 bytes of slack), recomputing the file hash and the ExeFS superblock
  hash, instead of rebuilding the CXI.
- `build_cia.py`, `build_dlc_cia.py`: the packages. (`build_update_cia.py`
  builds a structurally valid update-title CIA and is kept for reference; this
  game never reads an update's RomFS, so it is not a delivery route.)

`translations/` holds the hand-written English (`tr_batch*.json`,
`tr_extra.json`, `labels_en_p*.json`). Fix a line there and rebuild.

This build's line-source fix and its story-voice re-level a second time used analysis
helpers that live in a private work repo rather than in `tools/`; the parts of the pipeline
that ship here (the text and archive formats, the encoders and writers, the atlas rule) are
the same ones used to build the result, but the specific scripts that picked which of the
367 lines to replace and re-ran the loudness match are not published.
