#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname $0)" || exit; pwd)

DOCKERFILE="$1"
PLATFORMS_FILE="$SCRIPT_DIR/../platforms.yaml"
DOCKERFILE_BASENAME=$(basename "$DOCKERFILE")

# If architecture is omitted (Dockerfile), build for all configured Docker platforms.
if [ "$DOCKERFILE_BASENAME" = "Dockerfile" ]; then
  yq -r 'keys | map(select(test("^linux/"))) | join(",")' "$PLATFORMS_FILE"
  exit 0
fi

EXT="${DOCKERFILE_BASENAME##*.}"

GROUP_PLATFORMS=$(EXT="$EXT" yq -r '.groups[strenv(EXT)] // [] | join(",")' "$PLATFORMS_FILE")
if [ -n "$GROUP_PLATFORMS" ]; then
  echo "$GROUP_PLATFORMS"
  exit 0
fi

PLATFORM=$(EXT="$EXT" yq -r 'to_entries[] | select(.key | test("^linux/")) | select(.value[] == strenv(EXT)) | .key' "$PLATFORMS_FILE")
if [ -z "$PLATFORM" ]; then
  echo "Unknown Dockerfile suffix: $EXT" >&2
  exit 1
fi

echo "$PLATFORM"
