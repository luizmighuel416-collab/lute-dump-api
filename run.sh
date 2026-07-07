#!/bin/bash

# Usage: ./run.sh <input.lua> [out.lua] [extra settings...]
# Example: ./run.sh sample.lua out.lua debug

INPUT="${1:?Usage: ./run.sh <input.lua> [out.lua] [extra settings...]}"
OUT="${2:-out.lua}"
shift 2

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export HOOKOP_BIN="$SCRIPT_DIR/lute"

cd "$SCRIPT_DIR"
./lune run main.luau "$INPUT" "out=$OUT" "$@"
echo "Done -> $OUT"
