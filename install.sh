#!/bin/bash

# Source file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="$SCRIPT_DIR/session-manager.py"

# Target file
DEFAULT_TARGET_DIR="$HOME/.local/bin"
TARGET_DIR="${1:-$DEFAULT_TARGET_DIR}"
TARGET_FILE="$TARGET_DIR/session-manager"

# Check if session-manager is not found in the PATH
if ! which session-manager >/dev/null 2>&1; then
    # Ensure the target directory exists
    mkdir -p "$TARGET_DIR"

    # Create a symbolic link
    ln -s "$SOURCE_FILE" "$TARGET_FILE"

    # Make sure the source file is executable
    chmod +x "$SOURCE_FILE"

    echo "Symlink created: $TARGET_FILE -> $SOURCE_FILE"
else
    echo "session-manager is already installed."
fi

