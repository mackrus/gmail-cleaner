#!/bin/bash

# Install script for the Gmail cleaner Python program
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect package manager
detect_package_manager() {
    if command_exists apt; then
        PKG_MANAGER="apt"
        UPDATE_CMD="sudo apt update"
        INSTALL_CMD="sudo apt install -y"
    elif command_exists yum; then
        PKG_MANAGER="yum"
        UPDATE_CMD="sudo yum update -y"
        INSTALL_CMD="sudo yum install -y"
    elif command_exists dnf; then
        PKG_MANAGER="dnf"
        UPDATE_CMD="sudo dnf update -y"
        INSTALL_CMD="sudo dnf install -y"
    elif command_exists pacman; then
        PKG_MANAGER="pacman"
        UPDATE_CMD="sudo pacman -Syu --noconfirm"
        INSTALL_CMD="sudo pacman -S --noconfirm"
    elif command_exists brew; then
        PKG_MANAGER="brew"
        UPDATE_CMD="brew update"
        INSTALL_CMD="brew install"
    else
        print_error "No supported package manager found (apt, yum, dnf, pacman, brew)."
    fi
    print_msg "Detected package manager: $PKG_MANAGER"
}

# Install Python if not present
install_python() {
    if ! command_exists python3; then
        print_msg "Python 3 is not installed. Installing..."
        detect_package_manager
        $UPDATE_CMD
        $INSTALL_CMD python3 || print_error "Failed to install Python 3."
    else
        print_msg "Python 3 is already installed."
    fi
}

# Main installation function
main() {
    INSTALL_DIR="$HOME/.gmail-cleaner"

    # Check for uv
    if ! command_exists uv; then
        print_msg "uv is not installed. Installing via curl..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        print_msg "uv is already installed."
    fi

    # Create installation directory
    print_msg "Creating directory $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"

    # Copy files to INSTALL_DIR
    print_msg "Copying files to $INSTALL_DIR"
    cp main.py requirements.txt pyproject.toml "$INSTALL_DIR" || print_error "Failed to copy files. Ensure main.py, requirements.txt, and pyproject.toml are in the current directory."

    # Set up alias in shell configuration file
    SHELL_RC_FILE=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC_FILE="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC_FILE="$HOME/.bashrc"
    fi

    ALIAS_CMD="alias gmail-clean='uv run --project $INSTALL_DIR $INSTALL_DIR/main.py'"

    if [ -n "$SHELL_RC_FILE" ]; then
        if ! grep -q "alias gmail-clean=" "$SHELL_RC_FILE"; then
            echo -e "${YELLOW}[?] Would you like to add the 'gmail-clean' alias to $SHELL_RC_FILE? (y/N): ${NC}\c"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                echo "$ALIAS_CMD" >> "$SHELL_RC_FILE"
                print_msg "Alias added to $SHELL_RC_FILE. Please run 'source $SHELL_RC_FILE' or restart your shell."
            else
                print_msg "Skipping alias addition. You can add it manually:" "$YELLOW"
                print_msg "$ALIAS_CMD"
            fi
        else
            # Update the existing alias
            sed -i '' "s|alias gmail-clean=.*|alias gmail-clean='uv run --project $INSTALL_DIR $INSTALL_DIR/main.py'|" "$SHELL_RC_FILE"
            print_msg "Alias updated in $SHELL_RC_FILE."
        fi
    else
        print_msg "No .zshrc or .bashrc found. Please add the following alias manually:" "$YELLOW"
        print_msg "$ALIAS_CMD"
    fi

    # Sync dependencies with uv
    print_msg "Syncing dependencies with uv..."
    (cd "$INSTALL_DIR" && uv sync)

    # Remind user about credentials.json
    print_msg "Please place your credentials.json file in $INSTALL_DIR" "$YELLOW"
    print_msg "You can obtain it from https://console.cloud.google.com/ by creating a project, enabling Gmail API, and creating OAuth 2.0 Client Credentials." "$YELLOW"

    print_msg "Installation complete!"
    print_msg "To run the program, use: gmail-clean \"search string\""
    print_msg "To add phrases to the whitelist: gmail-clean --add-whitelist \"new phrase\""
}

# Run main installation
main
