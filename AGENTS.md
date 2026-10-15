# Development conventions

- This repository packages SGDK, native host tools and a cross-compiler. Keep
  gameplay and custom engine code outside it.
- Pin downloaded source revisions and hashes in `sources.lock.json`. Verify
  downloads before extracting or executing them. Document deliberate patches.
- Build native `linux/arm64` and `linux/amd64` images. Never describe an
  emulated AMD64 image as native ARM64 support.
- Test unmodified upstream SGDK examples from fresh source copies with no
  prebuilt `out/` files. Cover C compilation, resources, sprites and sound.
- Use maintained stable tool releases, then establish SGDK compatibility with
  tests. Keep required compiler workarounds and intentional C dialect settings.
- Keep container entrypoints small, preserve argument boundaries and propagate
  build failures. Do not require privileged containers or Docker socket mounts.
- Keep the README concise and update it with commands and tested limitations.
- Use `ewrogers/sgdk:latest` for public usage examples. Retain versioned release
  tags and locked build sources; those do not need to appear in normal commands.
- Generated files, downloaded archives, logs and ROMs belong in ignored paths.
- Do not prune unrelated Docker containers, volumes or images during testing.
- Publish only after both architectures pass. Keep versioned tags available;
  use the same tested digests in the multi-platform release manifest.
