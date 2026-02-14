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

    # Check and install Python 3
    install_python

    # Create installation directory
    print_msg "Creating directory $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"

    # Copy main.py and requirements.txt to INSTALL_DIR
    print_msg "Copying main.py and requirements.txt to $INSTALL_DIR"
    cp main.py requirements.txt "$INSTALL_DIR" || print_error "Failed to copy files. Ensure main.py and requirements.txt are in the current directory."

    # Create virtual environment
    print_msg "Creating virtual environment at $INSTALL_DIR/.venv"
    python3 -m venv "$INSTALL_DIR/.venv" || print_error "Failed to create virtual environment."

    # Install dependencies in the virtual environment
    print_msg "Installing dependencies from requirements.txt"
    "$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" || print_error "Failed to install dependencies."

    # Set up alias in shell configuration file
    SHELL_RC_FILE=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC_FILE="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC_FILE="$HOME/.bashrc"
    fi

    ALIAS_CMD="alias gmail-clean='$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/main.py'"

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
            print_msg "Alias already exists in $SHELL_RC_FILE."
        fi
    else
        print_msg "No .zshrc or .bashrc found. Please add the following alias manually:" "$YELLOW"
        print_msg "$ALIAS_CMD"
    fi

    # Remind user about credentials.json
    print_msg "Please place your credentials.json file in $INSTALL_DIR" "$YELLOW"
    print_msg "You can obtain it from https://console.cloud.google.com/ by creating a project, enabling Gmail API, and creating OAuth 2.0 Client Credentials." "$YELLOW"

    print_msg "Installation complete!"
    print_msg "To run the program, use: gmail-clean \"search string\""
    print_msg "To add phrases to the whitelist: gmail-clean --add-whitelist \"new phrase\""
}

# Run main installation
main
