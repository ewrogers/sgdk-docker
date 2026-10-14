#!/bin/sh
set -eu
if [ "$#" -eq 0 ]; then set -- build; fi
case "$1" in
    build)
        shift
        exec make -f "$GDK/makefile.gen" "$@"
        ;;
    doctor)
        shift
        exec /usr/local/bin/sgdk-doctor "$@"
        ;;
    *) exec "$@" ;;
esac
