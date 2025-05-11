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

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   - This script creates a directory at `~/.gmail-cleaner`, sets up a virtual environment, installs dependencies, and adds a shell alias (`gmail-clean`) for easy access.

3. **Source Your Shell Configuration**:

   - After installation, run:

     ```bash
     source ~/.zshrc  # or source ~/.bashrc
     ```
   - This applies the alias to your current shell session.

## Usage

Once installed, you can use the `gmail-clean` alias to run the program:

- **Delete Emails Containing a Search String**:

  ```bash
  gmail-clean "search_string"
  ```

  - This deletes emails containing `"search_string"`, excluding those with whitelisted phrases.

- **Add Phrases to the Whitelist**:

  ```bash
  gmail-clean --add-whitelist "important phrase"
  ```

  - This adds `"important phrase"` to `~/.gmail-cleaner/whitelist.txt`.

- **Specify a Custom Whitelist File**:

  ```bash
  gmail-clean "search_string" --whitelist-file "/path/to/custom_whitelist.txt"
  ```

- **Run Without Deleting (Just Add to Whitelist)**:

  ```bash
  gmail-clean --add-whitelist "new phrase"
  ```

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
- **Adding Phrases**: Use the `--add-whitelist` option or manually edit `whitelist.txt`.

Example `whitelist.txt`:

```
important
urgent
keep this
```

## Remove Token

If the Oauth token expires you may remove it with:
```bash 
gmail-clean --remove-token
```

## Important Considerations

- **Permanent Deletion**: Deleted emails are permanently removed and cannot be recovered. Use this tool with caution.
- **Backup**: Consider backing up important emails before running the script.

## Uninstallation

To uninstall Gmail Cleaner:

1. Run the uninstall script:

   ```bash
   cd gmail-cleaner
   chmod +x uninstall.sh
   ./uninstall.sh
   ```

   - This removes `~/.gmail-cleaner` and the `gmail-clean` alias.

2. Source your shell configuration:

   ```bash
   source ~/.zshrc  # or source ~/.bashrc
   ```

## Authors

Markus Bajlo [markusbajlo@gmail.com](email).

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool permanently deletes emails. Use with caution. The authors are not responsible for any data loss.

