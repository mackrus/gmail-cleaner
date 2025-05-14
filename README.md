# Gmail Cleaner

Gmail Cleaner is a command-line tool that helps you manage your Gmail inbox by deleting emails that contain a specific search string. It also includes a whitelist feature to prevent the deletion of emails containing certain phrases, ensuring important messages are preserved.

## Features

- Delete emails based on a search string.
- Exclude emails containing whitelisted phrases.
- Easy-to-use command-line interface.
- Secure authentication via Gmail API.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mackrus/gmail-cleaner.git
   cd gmail-cleaner
   ```

2. **Run the Install Script**:
   - **On Linux/macOS**:
     ```bash
     chmod +x install.sh
     ./install.sh
     ```
     - This creates a directory at `~/.gmail-cleaner`, sets up a virtual environment, installs dependencies, and adds a shell alias (`gmail-clean`) for easy access.
   - **On Windows (PowerShell)**:
     ```powershell
     .\install.ps1
     ```
     - This sets up the same environment in `~/.gmail-cleaner` and configures the `gmail-clean` alias for PowerShell. Ensure PowerShell execution policies allow running scripts (e.g., `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`).

3. **Source Your Shell Configuration**:
   - **On Linux/macOS**:
     ```bash
     source ~/.zshrc  # or source ~/.bashrc
     ```
   - **On Windows (PowerShell)**:
     ```powershell
     . $PROFILE
     ```
   - This applies the `gmail-clean` alias to your current shell session.

## Usage

The `gmail-clean` program helps you manage your Gmail emails by searching for emails based on a query and performing actions like moving them to a 'to delete' label, archiving, or permanently deleting them. You can also clean the 'to delete' label or remove the OAuth token. All email actions respect a **whitelist** of phrases, excluding emails containing those phrases in their snippets from being affected.

### Available Actions

- **Move Emails to 'to delete' Label** (default action):
  ```bash
  gmail-clean "search_string"
  ```
  - Moves emails containing `"search_string"` to the 'to delete' label, excluding those with whitelisted phrases.

- **Archive Emails**:
  ```bash
  gmail-clean "search_string" -a
  ```
  - Archives emails containing `"search_string"`, excluding those with whitelisted phrases.

- **Permanently Delete Emails**:
  ```bash
  gmail-clean "search_string" -p
  ```
  - Permanently deletes emails containing `"search_string"`, excluding those with whitelisted phrases. **Use with caution!**

- **Clean the 'to delete' Label**:
  ```bash
  gmail-clean -c
  ```
  - Permanently deletes all emails in the 'to delete' label, excluding those with whitelisted phrases. **Use with caution!**

### Options

- **Specify a Custom Whitelist File**:
  ```bash
  gmail-clean "search_string" -w /path/to/custom_whitelist.txt
  ```
  - Uses the specified whitelist file instead of the default `whitelist.txt`.

- **Remove OAuth Token**:
  ```bash
  gmail-clean -r
  ```
  - Removes the OAuth token file (`~/.gmail-cleaner/token.pickle`) to force re-authentication on the next run.

### Confirmation Prompts

For actions that modify emails (e.g., moving, archiving, or deleting), the program prompts for confirmation. You must type `'y'` to proceed with the action.

### Whitelist Management

The whitelist is a text file where each line is a phrase. Emails with these phrases in their snippets are excluded from all actions.

- **Default Location**: `~/.gmail-cleaner/whitelist.txt`
- **Default Phrases**: If the file doesn’t exist, it’s created with `"important"`, `"urgent"`, and `"keep this"`.
- **Editing the Whitelist**: Manually edit the file with a text editor to add or remove phrases.
  **Example - Adding a Phrase**:
  1. Open `~/.gmail-cleaner/whitelist.txt` in a text editor.
  2. Add a new phrase (e.g., `"important phrase"`) on a new line.
  3. Save the file.
  **Example - Removing a Phrase**: Delete the corresponding line from the file.

### First Run

- The first time you run the script, it will prompt you to authenticate with Gmail via a browser. Follow the instructions to grant access.

## Gmail API Credentials

To use this tool, you need to set up Gmail API credentials:

1. Go to the Google Cloud Console.
2. Create a new project or select an existing one.
3. Enable the **Gmail API** for your project.
4. Create **OAuth 2.0 Client Credentials** and download the `credentials.json` file.
5. Place `credentials.json` in `~/.gmail-cleaner`.

For detailed instructions, see [OAUTH](OAUTH.md) and Google's Gmail API Quickstart.

## Whitelist Feature

The whitelist prevents emails containing specific phrases from being deleted, even if they match the search string.

- **Default Location**: `~/.gmail-cleaner/whitelist.txt`
- **Format**: One phrase per line.
- **Example `whitelist.txt`**:
  ```
  important
  urgent
  keep this
  ```

## Remove Token

If your OAuth token expires or becomes invalid, you can remove it to force re-authentication:
```bash
gmail-clean -r
```
Then run the script again (e.g., `gmail-clean -c`) to generate a new token.

## Important Considerations

- **Permanent Deletion**: Deleted emails are permanently removed and cannot be recovered. Use this tool with caution.
- **Backup**: Consider backing up important emails before running the script.

## Uninstallation

To uninstall Gmail Cleaner:

1. Run the uninstall script:
   - **On Linux/macOS**:
     ```bash
     cd gmail-cleaner
     chmod +x uninstall.sh
     ./uninstall.sh
     ```
   - **On Windows (PowerShell)**:
     ```powershell
     cd gmail-cleaner
     .\uninstall.ps1
     ```
   - This removes `~/.gmail-cleaner` and the `gmail-clean` alias.

2. Source your shell configuration:
   - **On Linux/macOS**:
     ```bash
     source ~/.zshrc  # or source ~/.bashrc
     ```
   - **On Windows (PowerShell)**:
     ```powershell
     . $PROFILE
     ```

## Authors

Markus Bajlo [markusbajlo@gmail.com](email).

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool permanently deletes emails. Use with caution. The authors are not responsible for any data loss.

