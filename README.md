# Gmail Cleaner

A Python tool to search and delete emails in Gmail using the Gmail API.

## Features

- Search emails containing a specific string
- Batch delete matching emails
- OAuth 2.0 authentication with token caching
- Command-line interface

## Requirements

- Python 3.6+
- Google account with Gmail access

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/mackrus/gmail-cleaner.git
   cd gmail-cleaner
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up Google Cloud Project:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Gmail API
   - Create OAuth 2.0 credentials
   - Download the credentials file as `credentials.json` and place it in the project root

## Usage

```bash
python main.py "search string"
```

Example: Delete all emails containing "newsletter"

```bash
python main.py "newsletter"
```

## Configuration

The following files are used:

- `credentials.json`: OAuth 2.0 credentials (from Google Cloud Console)
- `token.json`: Auto-generated authentication token

## Authors

Markus Bajlo [markusbajlo@gmail.com](email).

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool permanently deletes emails. Use with caution. The authors are not responsible for any data loss.
