# tools

Scripts used to build and verify this project's patches. They are research code,
written to answer specific questions about this one game, not a general toolkit.

## Environment variables

Nothing is hardcoded to a machine any more. Set what a given script needs:

| variable | what it points at |
|---|---|
| `PUYO_ROOT` | the Puyo Puyo Tetris project folder these scripts were written against |
| `TGAA_ROOT` | a checkout of the TGAA project, whose `testimony_pipeline` and `3dstool`/`patches` folders some of these scripts reuse |
