#!/bin/bash

SCRIPT_DIR=$(cd "$(dirname $0)" || exit; pwd)

DOCKERFILE="$1"
PLATFORMS_FILE="$SCRIPT_DIR/../platforms.yaml"
DOCKERFILE_BASENAME=$(basename "$DOCKERFILE")

# If architecture is omitted (Dockerfile), build for all configured Docker platforms.
if [ "$DOCKERFILE_BASENAME" = "Dockerfile" ]; then
  yq -r 'keys | join(",")' "$PLATFORMS_FILE"
  exit 0
fi

EXT="${DOCKERFILE_BASENAME##*.}"
PLATFORM=$(EXT="$EXT" yq -r 'to_entries[] | select(.value[] == strenv(EXT)) | .key' "$PLATFORMS_FILE")
echo "$PLATFORM"
