# Install script for the Gmail cleaner Python program

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"

# Function to print messages
function Print-Msg {
    param (
        [string]$message,
        [string]$color = $GREEN
    )
    Write-Host "[*] $message" -ForegroundColor $color
}

# Function to print errors and exit
function Print-Error {
    param (
        [string]$message
    )
    Write-Host "[!] Error: $message" -ForegroundColor $RED
    exit 1
}

# Function to check if a command exists
function Command-Exists {
    param (
        [string]$command
    )
    return (Get-Command $command -ErrorAction SilentlyContinue) -ne $null
}

# Function to detect package manager
function Detect-PackageManager {
    if (Command-Exists apt) {
        $script:PKG_MANAGER = "apt"
        $script:INSTALL_PYTHON_CMD = "sudo apt install -y python3"
    } elseif (Command-Exists yum) {
        $script:PKG_MANAGER = "yum"
        $script:INSTALL_PYTHON_CMD = "sudo yum install -y python3"
    } elseif (Command-Exists dnf) {
        $script:PKG_MANAGER = "dnf"
        $script:INSTALL_PYTHON_CMD = "sudo dnf install -y python3"
    } elseif (Command-Exists pacman) {
        $script:PKG_MANAGER = "pacman"
        $script:INSTALL_PYTHON_CMD = "sudo pacman -S --noconfirm python"
    } elseif (Command-Exists brew) {
        $script:PKG_MANAGER = "brew"
        $script:INSTALL_PYTHON_CMD = "brew install python"
    } elseif (Command-Exists choco) {
        $script:PKG_MANAGER = "choco"
        $script:INSTALL_PYTHON_CMD = "choco install -y python"
    } else {
        $script:PKG_MANAGER = $null
        $script:INSTALL_PYTHON_CMD = $null
        Print-Msg "No supported package manager found (apt, yum, dnf, pacman, brew, choco)." -color $YELLOW
        Print-Msg "If Python 3 is installed, installation will proceed. Otherwise, please install Python 3 manually from https://www.python.org/downloads/." -color $YELLOW
    }
}

# Function to get Python command
function Get-PythonCommand {
    try {
        $output = & python --version 2>&1
        if ($output -match "^Python 3") {
            return "python"
        }
    } catch {}
    try {
        $output = & python3 --version 2>&1
        if ($output -match "^Python 3") {
            return "python3"
        }
    } catch {}
    return $null
}

# Main installation function
function Main {
    $INSTALL_DIR = "$HOME/.gmail-cleaner"

    # Check for Python 3
    $pythonCmd = Get-PythonCommand
    if (-not $pythonCmd) {
        Print-Msg "Python 3 is not installed. Checking for package manager to install..."
        Detect-PackageManager
        if ($script:PKG_MANAGER -and $script:INSTALL_PYTHON_CMD) {
            Print-Msg "Installing Python 3 using $script:PKG_MANAGER..."
            Invoke-Expression $script:INSTALL_PYTHON_CMD
            if ($LASTEXITCODE -ne 0) {
                Print-Error "Failed to install Python 3. Please install it manually from https://www.python.org/downloads/."
            }
            # Try to get Python command again
            $pythonCmd = Get-PythonCommand
            if (-not $pythonCmd) {
                Print-Error "Python 3 installation failed or not in PATH. Please ensure Python 3 is installed and added to PATH."
            }
        } else {
            Print-Error "No package manager available to install Python 3. Please install it manually from https://www.python.org/downloads/."
        }
    } else {
        Print-Msg "Python 3 is already installed (using command: $pythonCmd)."
    }

    # Create installation directory
    Print-Msg "Creating directory $INSTALL_DIR"
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null

    # Copy main.py and requirements.txt to INSTALL_DIR
    Print-Msg "Copying main.py and requirements.txt to $INSTALL_DIR"
    try {
        Copy-Item -Path "main.py", "requirements.txt" -Destination $INSTALL_DIR -ErrorAction Stop
    } catch {
        Print-Error "Failed to copy files. Ensure main.py and requirements.txt are in the current directory."
    }

    # Create virtual environment
    Print-Msg "Creating virtual environment at $INSTALL_DIR/.venv"
    & $pythonCmd -m venv "$INSTALL_DIR/.venv"
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Failed to create virtual environment."
    }

    # Determine venv Python path (Windows-specific by default, adjusted for cross-platform)
    if ([System.Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
        $venvPython = "$INSTALL_DIR\.venv\Scripts\python.exe"
        $venvPip = "$INSTALL_DIR\.venv\Scripts\pip.exe"
    } else {
        $venvPython = "$INSTALL_DIR/.venv/bin/python"
        $venvPip = "$INSTALL_DIR/.venv/bin/pip"
    }

    # Install dependencies
    Print-Msg "Installing dependencies from requirements.txt"
    & $venvPip install -r "$INSTALL_DIR/requirements.txt"
    if ($LASTEXITCODE -ne 0) {
        Print-Error "Failed to install dependencies."
    }

    # Set up function in PowerShell profile
    $aliasDef = "function gmail-clean { & '$venvPython' '$INSTALL_DIR/main.py' @args }"
    
    if (-not (Select-String -Path $PROFILE -Pattern "function gmail-clean" -Quiet -ErrorAction SilentlyContinue)) {
        $response = Read-Host "[?] Would you like to add the 'gmail-clean' function to your PowerShell profile ($PROFILE)? (y/N)"
        if ($response -match "^[yY](es)?$") {
            if (-not (Test-Path $PROFILE)) {
                New-Item -Path $PROFILE -ItemType File -Force | Out-Null
            }
            Add-Content -Path $PROFILE -Value "`n$aliasDef"
            Print-Msg "Function added to $PROFILE. Please run '. $PROFILE' or restart PowerShell to load it."
        } else {
            Print-Msg "Skipping function addition. You can add it manually to your profile:" -color $YELLOW
            Print-Msg $aliasDef -color $YELLOW
        }
    } else {
        Print-Msg "Function already exists in $PROFILE."
    }

    # Remind user about credentials.json
    Print-Msg "Please place your credentials.json file in $INSTALL_DIR" -color $YELLOW
    Print-Msg "Obtain it from https://console.cloud.google.com/ by creating a project, enabling Gmail API, and creating OAuth 2.0 Client Credentials." -color $YELLOW

    # Final instructions
    Print-Msg "Installation complete!"
    Print-Msg "To run the program, use: gmail-clean 'search string'"
    Print-Msg "To add phrases to the whitelist: gmail-clean --add-whitelist 'new phrase'"
}

# Run main installation
Main
