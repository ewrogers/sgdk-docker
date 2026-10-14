# SGDK Docker

Build Sega Mega Drive games with SGDK in Docker on ARM64 and AMD64 hosts.

A toolchain in a box: a native host compiler targeting the 68000, assembler,
linker, debugger, Java resource tools and SGDK utilities. Docker selects the
ARM64 image on Apple Silicon and the AMD64 image on x86-64 machines.

## Build a game

Run this in your SGDK project directory:

```sh
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11
```

The default command builds a release ROM in `out/rom.bin`. Other build targets
work through the `build` convenience command:

```sh
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 build clean
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 build debug
```

On Linux, add `--user "$(id -u):$(id -g)"` to keep output files owned by your
account. The image defaults to an unprivileged user. Run emulators on the host.

On Windows, use Docker Desktop's **Linux containers**, preferably with its
[WSL2 backend](https://docs.docker.com/desktop/features/wsl/). A WSL shell uses
the commands above. In PowerShell, mount the project with
`--mount "type=bind,source=$($PWD.Path),target=/workspace"` instead of `-v`.
Native Windows-container mode is not supported by these Linux images.

The image matrix covers CPU architecture. Linux CI and local macOS tests
check actual builds; a Windows Docker Desktop smoke test is still needed.

## Use any tool

Commands and arguments pass through directly:

```sh
docker run --rm ewrogers/sgdk:2.11 doctor
docker run --rm -it -v "$PWD:/workspace" ewrogers/sgdk:2.11 bash
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 m68k-elf-objdump -d out/rom.out
docker run --rm -it -v "$PWD:/workspace" ewrogers/sgdk:2.11 m68k-elf-gdb out/rom.out
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 sh -c 'java -jar "$GDK/bin/rescomp.jar" res/resources.res res/resources.rs'
```

`GDK=/opt/sgdk`. The compiler and SGDK native utilities are on `PATH`.
Source templates are available in `$GDK/sample`; copy a template into your
mounted workspace before editing it. Git, Python and native C/C++ build tools
are included for supporting development tasks.

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

Use `2.11-gcc16.2.0-binutils2.47` to select this toolchain release, `2.11` to
track tested updates for SGDK 2.11, or `latest` for the current tested release.
Use an image digest when exact reproducibility matters.

## Build and test locally

```sh
docker buildx build --platform linux/arm64 --load -t sgdk-local:arm64 .
python3 scripts/test-image.py sgdk-local:arm64 --platform linux/arm64 --output build/test-arm64
docker buildx build --platform linux/amd64 --load -t sgdk-local:amd64 .
python3 scripts/test-image.py sgdk-local:amd64 --platform linux/amd64 --output build/test-amd64
```

An opposite-architecture build uses Docker's emulation and can take longer.
CI builds and tests both images on matching native runners. Tests cover the
compiler, assembler, debugger, command handling, failed builds and five fresh
upstream examples including graphics, sprites and sound. No checked-in ROM is
accepted as a build result.

The Container matrix workflow publishes only after both platforms pass. To
publish from GitHub, configure `DOCKERHUB_TOKEN` and manually run the workflow
on `main` with publishing enabled. Ordinary pushes and PRs only build/test.

After local tests, `scripts/publish.py` can publish the exact tested image IDs
using your existing `docker login`:

```sh
python3 scripts/publish.py --arm64 build/test-arm64/report.json --amd64 build/test-amd64/report.json
```

The Docker packaging is MIT licensed. SGDK and the bundled GNU/Java tools
retain their own licenses. GNU source archives and build recipes are included
under `/usr/local/share/sgdk` for inspection and rebuilding.
