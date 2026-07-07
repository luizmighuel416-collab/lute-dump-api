#!/bin/bash

INPUT="${1:?Usage: ./runner.sh <input> [out]}"
OUT="${2:-out.lua}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export HOOKOP_BIN="$SCRIPT_DIR/lute"

cd "$SCRIPT_DIR"
./lune run main.luau "$INPUT" "out=$OUT" "$@"
echo "Done -> $OUT"
