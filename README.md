# SGDK Docker

Build Sega Mega Drive games with [SGDK](https://github.com/Stephane-D/SGDK)
using Docker. The compiler and tools run inside the container. Your source
files and finished ROMs stay on your computer.

The image includes the M68K compiler, assembler, linker, debugger, Java
resource tools and SGDK utilities. It supports ARM64 and AMD64, and Docker
selects the right image for your machine.

## Build your game

Run this from your SGDK project folder:

```sh
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11
```

Your release ROM appears at `out/rom.bin`. To clean or make a debug build:

```sh
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 build clean
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 build debug
```

## Use the tools

You can run any command, or open a shell:

```sh
docker run --rm ewrogers/sgdk:2.11 doctor
docker run --rm -it -v "$PWD:/workspace" ewrogers/sgdk:2.11 bash
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:2.11 m68k-elf-objdump -d out/rom.out
```

SGDK is installed at `/opt/sgdk`, available as `$GDK` inside the container.
Its examples are in `$GDK/sample`. Copy an example into your mounted project
folder before editing it. Run your emulator on the host.

## On your computer

- **macOS:** use Docker Desktop.
- **Linux:** use Docker Engine or Docker Desktop. Add `--user "$(id -u):$(id -g)"`
  if you need output files owned by your account.
- **Windows:** use Docker Desktop in Linux-container mode, preferably through
  [WSL2](https://docs.docker.com/desktop/features/wsl/). WSL uses the commands
  above. In PowerShell, replace `-v` with
  `--mount "type=bind,source=$($PWD.Path),target=/workspace"`.

See [versions, local tests and publishing](docs/development.md) for the
maintainer details, and [SGDK's API reference](https://stephane-d.github.io/SGDK/)
for game development.

The packaging is MIT licensed. Bundled tools retain their own licenses and
include GNU source archives under `/usr/local/share/sgdk`.
