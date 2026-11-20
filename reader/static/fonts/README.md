# Bundled fonts

Self-hosted web fonts for MythLab Reader, so reading works offline (PWA, Android, desktop).
Only the `latin`, `latin-ext` and `vietnamese` subsets are included, as woff2. Variable fonts (wght axis) are used where
fontsource publishes one; otherwise static weights 400 and 700. Literata (the default reading font) also ships italic.

Files were taken unmodified from the npm packages listed below (`npm pack`, files from `files/`); `fonts.css` is generated from the
packages' CSS (same `unicode-range` per subset). Proprietary fonts are never bundled; system fonts are referenced by name only.

| Font | Group | Faces | License | npm package | Upstream |
|---|---|---|---|---|---|
| Literata | serif | variable wght + italic | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/literata@5.3.0` | https://github.com/google/fonts |
| Merriweather | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/merriweather@5.3.0` | https://github.com/google/fonts |
| Lora | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/lora@5.3.0` | https://github.com/google/fonts |
| Noto Serif | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/noto-serif@5.3.0` | https://github.com/google/fonts |
| Source Serif 4 | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/source-serif-4@5.3.1` | https://github.com/google/fonts |
| Spectral | serif | 400, 700 | [SIL OFL 1.1](OFL.txt) | `@fontsource/spectral@5.3.0` | https://github.com/google/fonts |
| Crimson Pro | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/crimson-pro@5.3.0` | https://github.com/google/fonts |
| EB Garamond | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/eb-garamond@5.3.0` | https://github.com/google/fonts |
| Alegreya | serif | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/alegreya@5.3.0` | https://github.com/google/fonts |
| Tinos | serif | 400, 700 | [SIL OFL 1.1](OFL.txt) | `@fontsource/tinos@5.3.0` | https://github.com/google/fonts |
| Roboto Slab | serif | variable wght | [Apache 2.0](Apache-2.0.txt) | `@fontsource-variable/roboto-slab@5.3.0` | https://github.com/google/fonts |
| Inter | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/inter@5.3.0` | https://github.com/google/fonts |
| Be Vietnam Pro | sans | 400, 700 | [SIL OFL 1.1](OFL.txt) | `@fontsource/be-vietnam-pro@5.3.0` | https://github.com/google/fonts |
| Noto Sans | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/noto-sans@5.3.0` | https://github.com/google/fonts |
| Roboto | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/roboto@5.3.0` | https://github.com/google/fonts |
| Open Sans | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/open-sans@5.3.0` | https://github.com/google/fonts |
| Nunito Sans | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/nunito-sans@5.3.0` | https://github.com/google/fonts |
| Mulish | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/mulish@5.3.0` | https://github.com/google/fonts |
| Arimo | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/arimo@5.3.0` | https://github.com/google/fonts |
| Montserrat | sans | variable wght | [SIL OFL 1.1](OFL.txt) | `@fontsource-variable/montserrat@5.3.0` | https://github.com/google/fonts |

Copyright notices are reproduced at the top of `OFL.txt` and `Apache-2.0.txt`.
