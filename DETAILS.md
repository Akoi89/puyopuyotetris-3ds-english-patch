# Puyo Puyo Tetris 3DS patch: the detail

Everything the README used to carry inline. Nothing here has been reworded.


---

## What was done

| area | |
|---|---|
| Text | 1,411 base strings and 875 DLC strings. Sega's Steam text where it exists; 392 lines written for the 3DS-only screens (Chapter 0 prologue, Club, SpotPass, errors, shop) |
| In-battle voices | 24 Japanese character banks replaced from Steam's English recordings, matched by the Japanese takes' durations (zero error); the other 13 banks, already English from the earlier fan translation, are now re-imported from Steam too, so all 37 battle banks are this project's own encode at Sega's sample rate (`import_fan_banks.py`). Levels matched to Sega's own Japanese takes with `voice_gain_clean.py`, gain and limiting done in float with a single encode: 62 of 63 banks re-levelled, averaging about 1 dB below Sega's takes |
| DLC story voices | 760 of 763 clips; the other three were re-recorded for 3DS and have no English take. Levels matched to Sega's own Japanese takes with `voice_gain_clean.py`, a single clean encode: about 1.1 dB below Sega's takes |
| Online UI textures | about 550 labels across the Club, Puzzle League, standby, replay and shop screens, redrawn in place |
| DLC shop icons | 33 redrawn |
| Font atlases | the game pre-renders only the glyphs each screen uses; every screen that gained English got a matching atlas, verified per section |
| Character-select pick lines | all 24 (the fan patch had only 15), matched to Steam's English pick bank by duration |
| Title-screen announcer | the boot call, matched to Steam's title_set_bank by duration across all four takes |
| Boot notice and DLC map plates | re-wrapped/re-fitted into the Japanese texture's own ink window after a first pass cut them off |
| Endless-mode record card | "Best Record", "This Run" and the "beaten" count redrawn with the gradient plates inpainted |
| Swap-mode call logos | Sega's official English "Puyo" / "Tetris" logo art, taken from the Steam release's English swap texture (the 3DS texture at 4x) and scaled down into place |
| Official Steam sprites | 222 hand-redrawn labels replaced with Sega's official English sprites matched by text against the Steam release, including the Broadcast Station and Club mode pills with their proper two-tone outlines; plus the 11 Replay Report badge rows, the 15 Puzzle League rank pills, and the Broadcast Station TV logo (Sega's "World Broadcast" mark), none of which the label match had caught |
| HOME menu banner | Sega's official English "PuyoPuyo" logo swapped into the shared texture in place of the Japanese one, keeping Sega's TETRIS art untouched; this is in a locally built CIA only, since LayeredFS cannot change a banner |

What stays Japanese, and why, is in [TESTING.md](TESTING.md).

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
- `voice_levels.py`: measures peak and RMS in dBFS against Sega's Japanese
  takes.
- `voice_gain_clean.py`: decodes the once-encoded import audio, iterates
  gain and look-ahead limiting in floating point until every base and DLC
  voice clip matches Sega's Japanese take, then encodes DSP-ADPCM a single
  time (`voice_gain.py` and `voice_gain_dlc.py`, an earlier multi-pass
  version, are kept only for reference and are not used anymore).
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
