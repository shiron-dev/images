#!/bin/bash

PARALLEL_JOBS=10

SCRIPT_DIR=$(cd "$(dirname $0)" || exit; pwd)

find . -maxdepth 1 -name "Dockerfile.*" -print0 | parallel -0 -j "$PARALLEL_JOBS" sh "$SCRIPT_DIR/build_dockerfile.sh {}"
