# syntax=docker/dockerfile:1
ARG BASE_IMAGE=debian:trixie-slim@sha256:a29215f6a35e51e22adffa17f89e9d2ef06214e64a2bad10d765c46aea49f11f
FROM eclipse-temurin:25-jre-noble@sha256:d9a39a23634650173f1e2bbc176227af9728587ecf0f4b62d53e9355cd7a19ab AS java

FROM ${BASE_IMAGE} AS compiler
ARG BUILD_JOBS=4
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates build-essential bison flex texinfo python3 xz-utils \
    libgmp-dev libmpfr-dev libmpc-dev zlib1g-dev libzstd-dev \
    && rm -rf /var/lib/apt/lists/*
COPY sources.lock.json /build/sources.lock.json
COPY scripts/fetch-sources.py scripts/build-compiler.sh /build/
RUN /build/build-compiler.sh

FROM compiler AS debugger
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreadline-dev libncurses-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*
COPY debugger.lock.json /build/debugger.lock.json
COPY scripts/build-debugger.sh /build/
RUN /build/build-debugger.sh

FROM debugger AS packed-tools
COPY scripts/strip-host-tools.py /build/
RUN python3 /build/strip-host-tools.py

FROM compiler AS sgdk
COPY --from=java /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=/opt/m68k/bin:/opt/java/openjdk/bin:/opt/sgdk/bin:$PATH
RUN apt-get update && apt-get install -y --no-install-recommends unzip \
    libfontconfig1 libfreetype6 && rm -rf /var/lib/apt/lists/*
COPY scripts/build-sgdk.sh scripts/patch-sgdk.py /build/
RUN /build/build-sgdk.sh

FROM ${BASE_IMAGE} AS toolchain
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates build-essential make git python3 unzip xz-utils \
    libgmp10 libmpfr6 libmpc3 libzstd1 zlib1g libfontconfig1 libfreetype6 \
    libreadline8t64 libncursesw6 libpython3.13 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 --shell /bin/bash sgdk \
    && mkdir /workspace && chown sgdk:sgdk /workspace
COPY --from=java /opt/java/openjdk /opt/java/openjdk
COPY --from=packed-tools /opt/m68k /opt/m68k
COPY --from=sgdk /opt/sgdk /opt/sgdk
COPY --from=sgdk /opt/sources /usr/local/share/sgdk/sources
COPY --from=debugger /opt/sources/gdb.tar.xz /usr/local/share/sgdk/sources/gdb.tar.xz
COPY sources.lock.json /usr/local/share/sgdk/sources.lock.json
COPY debugger.lock.json /usr/local/share/sgdk/debugger.lock.json
COPY scripts/fetch-sources.py scripts/build-compiler.sh scripts/build-sgdk.sh scripts/build-debugger.sh scripts/patch-sgdk.py /usr/local/share/sgdk/recipes/
COPY scripts/entrypoint.sh /usr/local/bin/sgdk
COPY scripts/doctor.sh /usr/local/bin/sgdk-doctor
RUN chmod a+r /usr/local/share/sgdk/sources/*
ENV GDK=/opt/sgdk JAVA_HOME=/opt/java/openjdk
ENV PATH=/opt/m68k/bin:/opt/java/openjdk/bin:/opt/sgdk/bin:$PATH
# SGDK 2.11 predates GCC's C23 default. Keep the established C17 dialect.
ENV EXTRA_FLAGS=-std=gnu17
LABEL org.opencontainers.image.title="SGDK toolchain" \
    org.opencontainers.image.description="Native ARM64 and AMD64 SGDK development tools" \
    org.opencontainers.image.source="https://github.com/ewrogers/sgdk-docker" \
    org.opencontainers.image.version="2.11-gcc16.2.0-binutils2.47"
USER sgdk
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/sgdk"]
CMD ["build"]
