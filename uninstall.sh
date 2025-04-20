#!/bin/bash

# Uninstall script for the Gmail cleaner Python program
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print messages
print_msg() {
    echo -e "${2:-$GREEN}[*] $1${NC}"
}

print_error() {
    echo -e "${RED}[!] Error: $1${NC}" >&2
    exit 1
}

# Main uninstallation function
main() {
    INSTALL_DIR="$HOME/.gmail-cleaner"
    ALIAS_LINE="alias gmail-clean='$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/main.py'"

    # Check if the installation directory exists
    if [ ! -d "$INSTALL_DIR" ]; then
        print_msg "No installation found at $INSTALL_DIR. Nothing to uninstall." "$YELLOW"
        exit 0
    fi

    # Prompt user for confirmation
    print_msg "WARNING: This will delete the entire directory $INSTALL_DIR and all its contents, including any custom files." "$YELLOW"
    read -p "Are you sure you want to uninstall and delete all data? (y/n): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_msg "Uninstallation cancelled."
        exit 0
    fi

    # Remove the installation directory
    print_msg "Removing $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR" || print_error "Failed to remove $INSTALL_DIR."

    # Remove the alias from shell configuration files
    SHELL_RC_FILES=("$HOME/.zshrc" "$HOME/.bashrc")
    for rc_file in "${SHELL_RC_FILES[@]}"; do
        if [ -f "$rc_file" ]; then
            if grep -q "$ALIAS_LINE" "$rc_file"; then
                print_msg "Removing alias from $rc_file..."
                sed -i "\|$ALIAS_LINE|d" "$rc_file" || print_error "Failed to remove alias from $rc_file."
            else
                print_msg "Alias not found in $rc_file."
            fi
        fi
    done

    print_msg "Uninstallation complete!"
    print_msg "Please run 'source ~/.zshrc' or 'source ~/.bashrc' to update your shell, or restart your shell."
}

# Run main uninstallation
main
