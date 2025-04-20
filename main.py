import os
import base64
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import argparse

# If modifying these SCOPES, delete the token.json file
SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://mail.google.com/"]

# local constants
CONFIG_DIR = os.path.expanduser("~/.gmail-cleaner")
WHITELIST_FILE = os.path.join(CONFIG_DIR, "whitelist.txt")
CREDENTIALS_JSON = os.path.join(CONFIG_DIR, "credentials.json")
TOKEN_JSON = os.path.join(CONFIG_DIR, "token.json")


def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None
    if os.path.exists(TOKEN_JSON):
        creds = Credentials.from_authorized_user_file(TOKEN_JSON, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_JSON, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def search_emails(service, query):
    """Search emails with pagination."""
    emails = []
    page_token = None

    while True:
        try:
            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q=query,
                    maxResults=500,  # Max allowed per page
                    pageToken=page_token,
                )
                .execute()
            )

            emails.extend(results.get("messages", []))
            page_token = results.get("nextPageToken")

            if not page_token:
                break

        except HttpError as error:
            print(f"An error occurred: {error}")
            break

    return emails


def delete_emails(service, email_ids):
    """Batch delete emails with pagination and logging."""
    if not email_ids:
        print("No emails to delete.")
        return

    # Confirmation prompt
    print(f"WARNING: About to delete {len(email_ids)} emails. This action cannot be undone.")
    confirm = input("Type 'y' to proceed, or any other key to cancel: ").strip().lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return

    # Process in batches of 1000
    batch_size = 1000
    total_deleted = 0

    for i in range(0, len(email_ids), batch_size):
        batch = email_ids[i : i + batch_size]

        try:
            service.users().messages().batchDelete(
                userId="me", body={"ids": [msg["id"] for msg in batch]}
            ).execute()

            total_deleted += len(batch)
            print(f"Deleted {len(batch)} emails (total: {total_deleted})")

            # Rate limiting: sleep between batches
            time.sleep(1)

        except HttpError as error:
            print(f"Error deleting batch: {error}")
            # Optionally: retry or log failed batch


def read_whitelist_file(file_path):
    """Read whitelist phrases from a file, creating it with defaults if it doesn't exist."""
    if not os.path.exists(file_path):
        print(f"Whitelist file '{file_path}' does not exist. Creating with default phrases.")
        try:
            with open(file_path, "w") as file:
                default_phrases = ["important", "urgent", "keep this"]
                file.write("\n".join(default_phrases) + "\n")
            print(f"Created '{file_path}' with default phrases: {', '.join(default_phrases)}")
        except Exception as e:
            print(f"Error creating whitelist file '{file_path}': {e}")
            return []
    
    try:
        with open(file_path, "r") as file:
            # Read lines, strip whitespace, and filter out empty lines
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"Error reading whitelist file '{file_path}': {e}")
        return []


def add_to_whitelist_file(file_path, new_phrases):
    """Add new phrases to the whitelist file, avoiding duplicates."""
    if not new_phrases:
        return
    
    # Read existing phrases
    existing_phrases = read_whitelist_file(file_path)
    
    # Filter out duplicates (case-insensitive for comparison)
    new_phrases = [phrase.strip() for phrase in new_phrases if phrase.strip()]
    new_unique_phrases = [
        phrase for phrase in new_phrases
        if phrase.lower() not in [p.lower() for p in existing_phrases]
    ]
    
    if not new_unique_phrases:
        print("No new unique phrases to add to whitelist.")
        return
    
    try:
        with open(file_path, "a") as file:
            file.write("\n".join(new_unique_phrases) + "\n")
        print(f"Added {len(new_unique_phrases)} new phrases to '{file_path}': {', '.join(new_unique_phrases)}")
    except Exception as e:
        print(f"Error adding phrases to whitelist file '{file_path}': {e}")


def main(search_string, whitelist_file, add_whitelist_phrases):
    """Main function to search and delete emails, with whitelist support from a file."""
    # Add new phrases to whitelist file before reading it
    add_to_whitelist_file(whitelist_file, add_whitelist_phrases)
    
    # Read whitelist phrases from file
    whitelist = read_whitelist_file(whitelist_file)
    print(f"Loaded {len(whitelist)} whitelist phrases from '{whitelist_file}'")

    # Prevent running with empty search_string
    if not search_string:
        print("Error: No search string provided. Please specify a search string to proceed.")
        print("Use --add-whitelist to add phrases without deleting emails.")
        return

    # Safety check: prevent deletion if both search_string is empty and whitelist is empty
    if not search_string and not whitelist:
        print("Error: No search string or whitelist phrases provided. Aborting to prevent unintended deletions.")
        return

    # Authenticate Gmail service
    service = authenticate_gmail()

    # Construct the search query with whitelist exclusions
    query = f'"{search_string}"'
    if whitelist:
        query += ' ' + ' '.join([f'-"{phrase}"' for phrase in whitelist])
    print(f"Using search query: {query}")

    # Search for emails
    emails = search_emails(service, query)
    print(f"Found {len(emails)} emails matching the search criteria")

    if emails:
        # Delete the found emails
        delete_emails(service, emails)
    else:
        print("No emails found matching the search criteria.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete Gmail emails containing a specific string, excluding those containing whitelisted phrases from a file."
    )
    parser.add_argument(
        "search_string",
        type=str,
        nargs="?",
        default="",
        help="The string to search for in emails (required for deletion)"
    )
    parser.add_argument(
        "--whitelist-file",
        type=str,
        default=WHITELIST_FILE,
        help="Path to a text file containing whitelisted phrases, one per line (default: ¨/.gmail-cleaner/whitelist.txt)"
    )
    parser.add_argument(
        "--add-whitelist",
        type=str,
        action="append",
        default=[],
        help="Phrases to add to the whitelist file"
    )
    args = parser.parse_args()
    main(args.search_string, args.whitelist_file, args.add_whitelist)
