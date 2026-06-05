# Brand assets (logo & icon)

Home Assistant and HACS do **not** read the integration logo/icon from this
repository. They are served from the central
[`home-assistant/brands`](https://github.com/home-assistant/brands) repository.

This `brands/` folder is a **staging area**: it mirrors the exact directory
layout that `home-assistant/brands` expects so you can drop in the final PNGs
and copy them straight across when opening the PR. Nothing in this folder is
used by the integration at runtime.

## Folder layout

```
brands/
└── custom_integrations/
    └── chargee/
        ├── icon.png        # required - 256x256
        ├── icon@2x.png     # optional - 512x512 (hDPI)
        ├── logo.png        # optional - max 512px on the longest side
        ├── logo@2x.png     # optional - hDPI logo
        ├── dark_icon.png   # optional - dark-mode icon variant
        └── dark_logo.png   # optional - dark-mode logo variant
```

The folder name **must** equal the integration domain: `chargee`
(see `custom_components/chargee/manifest.json`). When the integration is later
accepted into Home Assistant Core, the same files move to
`core_integrations/chargee/` instead of `custom_integrations/chargee/`.

## Image requirements (enforced by the brands CI)

- Format: **PNG**. Transparency is preferred (and strongly recommended for the
  `dark_*` variants so they don't show a solid box on dark backgrounds).
- `icon.png`: **exactly 256x256** px, square (1:1). `icon@2x.png`: exactly
  512x512.
- `logo.png`: landscape; its **shortest side must be 128-256 px**.
  `logo@2x.png`: shortest side **256-512 px**, and exactly double the normal
  version's pixel dimensions. The long side scales with your logo's aspect
  ratio (no fixed cap).
- Trim surrounding padding (the image should be tight to the art).
- Keep file sizes reasonable; optimize the PNGs (e.g. with `pngquant`/`oxipng`).
- Provide `dark_*` variants only if your normal art is hard to see on a dark
  background.

## How to submit the PR

1. Replace the placeholder files in `brands/custom_integrations/chargee/` with
   your real PNGs (same names).
2. Fork and clone `home-assistant/brands`.
3. Copy the folder across:

   ```bash
   cp -r brands/custom_integrations/chargee \
     /path/to/brands/custom_integrations/chargee
   ```

4. From the brands repo, validate locally (optional but recommended):

   ```bash
   python -m script.hassfest  # not applicable here; brands uses its own CI
   ```

   The brands repo runs an automated image-dimension/format check on the PR;
   just make sure your images meet the sizes above.
5. Commit, push to your fork, and open a PR against `home-assistant/brands`
   titled something like `Add brand images for chargee`.

Until that PR is merged, Home Assistant and HACS show a generic placeholder
icon for the integration - this is expected.

## References

- Brands repo + contributing guide: https://github.com/home-assistant/brands
- Why brands are external: https://developers.home-assistant.io/docs/creating_integration_brand
