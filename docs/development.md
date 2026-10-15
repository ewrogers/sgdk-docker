# Development and releases

## Versions

| Component | Version |
| --- | --- |
| SGDK | 2.11, exact release commit |
| M68K GCC | 16.2.0 |
| GNU binutils | 2.47 |
| GNU GDB | 18.1 |
| Java | Temurin 25, maintained LTS image |
| Linux base | Debian 13, pinned image digest |

Source archives and base images are pinned and verified. SGDK's libraries are
rebuilt with the same compiler used by projects. `EXTRA_FLAGS=-std=gnu17`
keeps SGDK 2.11 on C17 rather than GCC's newer C23 default. SGDK's existing
optimizer workarounds remain intact.

We apply one host portability fix to SGDK's `xgmtool`: negative PCM samples
are converted to a signed integer before encoding the unsigned byte. The
original direct floating-point conversion produced silence for those samples
on ARM64. The fix preserves the established AMD64 output; a PCM regression
test and matching ROM hashes check both architectures. We also disable fused
floating-point operations in this converter to keep PCM rounding identical
between host architectures. Game compilation keeps SGDK's normal flags.

GCC 16.2 can incorrectly fold a byte copy into a M68000 instruction that
increments a pointer before using it again for the destination address.
This shifted SGDK's uploaded Z80 sound driver by one byte and caused silence.
The compiler defaults to `-fno-auto-inc-dec` through its installed specs,
and SGDK's libraries are rebuilt with that default. This also protects custom
compiler invocations; changing `EXTRA_FLAGS` does not remove the workaround.
Do not enable `-fauto-inc-dec` in game builds while using this compiler.

The test suite executes actual M68000 code with Unicorn, including SGDK's
public Z80 upload/download functions. It checks full driver-sized copies,
zero and odd lengths, unaligned sources and surrounding guard bytes. A separate
negative control explicitly enables the faulty optimization and must reproduce
the corruption. Both native CI architectures run these tests. This checks memory
copy correctness, not complete console emulation or audible playback.

Use `2.11-gcc16.2.0-binutils2.47` to select this toolchain release, `2.11` to
track tested updates for SGDK 2.11, or `latest` for the current tested release.
Use an image digest when exact reproducibility matters.

## Build and test locally

```sh
python3 -m venv build/test-venv
build/test-venv/bin/pip install -r tests/requirements.txt
docker buildx build --platform linux/arm64 --load -t sgdk-local:arm64 .
build/test-venv/bin/python scripts/test-image.py sgdk-local:arm64 --platform linux/arm64 --output build/test-arm64
docker buildx build --platform linux/amd64 --load -t sgdk-local:amd64 .
build/test-venv/bin/python scripts/test-image.py sgdk-local:amd64 --platform linux/amd64 --output build/test-amd64
```

An opposite-architecture build uses Docker's emulation and can take longer.
CI builds and tests both images on matching native runners. Tests cover the
compiler, assembler, debugger, command handling, failed builds and five fresh
upstream examples including graphics, sprites and sound. No checked-in ROM is
accepted as a build result.

The Container matrix workflow tests native ARM64 and AMD64 images, then
compares their five example ROMs. A successful code change merged to `main`
publishes to Docker Hub. PRs only build and test. Manual publishing is also
available through the workflow on `main`.

Create a Docker Hub personal access token with Read & Write permission and
store it as the repository secret `DOCKERHUB_TOKEN`. Do not commit the token.
The GitHub secret is separate from your local Docker login.

```sh
gh secret set DOCKERHUB_TOKEN --repo ewrogers/sgdk-docker
```

After local tests, `scripts/publish.py` can publish the exact tested image IDs
using your existing `docker login`:

```sh
python3 scripts/publish.py --arm64 build/test-arm64/report.json --amd64 build/test-amd64/report.json
```

The Docker packaging is MIT licensed. SGDK and the bundled GNU/Java tools
retain their own licenses. GNU source archives and build recipes are included
under `/usr/local/share/sgdk` for inspection and rebuilding.
