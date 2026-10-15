# SGDK Docker

Build Sega Mega Drive and Genesis games with
[SGDK](https://github.com/Stephane-D/SGDK), the open-source C development kit.
Docker keeps the compiler and tools in one place, so you don't need to install
the toolchain on your computer. Your source files and finished ROMs stay on
your computer.

The image includes the M68K compiler, assembler, linker, debugger, Java
resource tools and SGDK utilities. It supports ARM64 and AMD64, and Docker
selects the right image for your machine.

## Use the Docker Hub image

Install Docker and make sure it is running, then pull the image from
[Docker Hub](https://hub.docker.com/r/ewrogers/sgdk):

```sh
docker pull ewrogers/sgdk:latest
```

Run this from your SGDK project folder:

```sh
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:latest
```

Your release ROM appears at `out/rom.bin`. To clean or make a debug build:

```sh
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:latest build clean
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:latest build debug
```

Don't have a project yet? Start with SGDK's Hello World example in a new folder:

```sh
mkdir my-game
cd my-game
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:latest sh -c 'cp -R "$GDK/sample/basics/hello-world/." .'
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:latest
```

## Build the container locally

You can build your own image from this repository instead of pulling it:

```sh
git clone https://github.com/ewrogers/sgdk-docker.git
cd sgdk-docker
docker buildx build --load -t sgdk-local .
docker run --rm sgdk-local doctor
```

The first build compiles the toolchain and can take a while. It builds for your
machine's architecture by default. From your SGDK project folder, use the
same commands above with `sgdk-local` in place of `ewrogers/sgdk:latest`.

## Use the tools

You can run any command, or open a shell:

```sh
docker run --rm ewrogers/sgdk:latest doctor
docker run --rm -it -v "$PWD:/workspace" ewrogers/sgdk:latest bash
docker run --rm -v "$PWD:/workspace" ewrogers/sgdk:latest m68k-elf-objdump -d out/rom.out
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
maintainer details. To learn SGDK, see its
[getting-started guide](https://github.com/Stephane-D/SGDK/wiki) and
[API reference](https://stephane-d.github.io/SGDK/).

The packaging is MIT licensed. Bundled tools retain their own licenses and
include GNU source archives under `/usr/local/share/sgdk`.

## Disclaimer

SGDK Docker is an independent community project. It is not affiliated with,
endorsed by or sponsored by SEGA CORPORATION or SEGA SAMMY HOLDINGS INC.
SEGA and related names, logos and trademarks belong to their respective owners.
They are used here to identify the hardware and tools this project supports.

This repository's original work is available under the [MIT License](LICENSE).
Third-party software and materials retain their own licenses and notices.
