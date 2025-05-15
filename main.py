import argparse
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://mail.google.com/"]

# Constant for the label name
LABEL_NAME = "to delete"

# Constant for credentials path
CONFIG_DIR = os.path.expanduser("~/.gmail-cleaner")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.pickle")


def get_gmail_service():
    """Authenticate and return a Gmail API service instance."""
    # Create directory if it doesn't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)

    creds = None
    token_path = os.path.join(
        CONFIG_DIR, "token.pickle"
    )  # Also use CONFIG_DIR for token
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)


def get_or_create_label(service, label_name):
    """Get the ID of the label with the given name, or create it if it doesn't exist."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in labels:
        if label["name"].lower() == label_name.lower():
            return label["id"]
    # If not found, create it
    print(f"Label '{label_name}' not found, creating it.")
    new_label = (
        service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )
    return new_label["id"]


def search_emails(service, query, whitelist_phrases):
    """Search for emails matching the query, excluding those with whitelist phrases."""
    email_ids = []
    page_token = None
    while True:
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=500,
                pageToken=page_token,
                fields="messages(id,snippet),nextPageToken",
            )
            .execute()
        )
        messages = results.get("messages", [])
        for msg in messages:
            snippet = msg.get("snippet", "").lower()
            if not any(phrase.lower() in snippet for phrase in whitelist_phrases):
                email_ids.append({"id": msg["id"]})
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    return email_ids


def delete_emails(service, email_ids):
    """Delete the specified emails in batches."""
    if not email_ids:
        print("No emails to delete.")
        return
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
            time.sleep(1)
        except HttpError as error:
            print(f"Error deleting batch: {error}")


def archive_emails(service, email_ids):
    """Archive the specified emails by removing the INBOX label in batches."""
    if not email_ids:
        print("No emails to archive.")
        return
    batch_size = 1000
    total_archived = 0
    for i in range(0, len(email_ids), batch_size):
        batch = email_ids[i : i + batch_size]
        try:
            service.users().messages().batchModify(
                userId="me",
                body={"ids": [msg["id"] for msg in batch], "removeLabelIds": ["INBOX"]},
            ).execute()
            total_archived += len(batch)
            print(f"Archived {len(batch)} emails (total: {total_archived})")
            time.sleep(1)
        except HttpError as error:
            print(f"Error archiving batch: {error}")


def move_to_label(service, email_ids, label_id):
    """Move the specified emails to the given label by adding the label and removing INBOX in batches."""
    if not email_ids:
        print("No emails to move.")
        return
    batch_size = 1000
    total_moved = 0
    for i in range(0, len(email_ids), batch_size):
        batch = email_ids[i : i + batch_size]
        try:
            service.users().messages().batchModify(
                userId="me",
                body={
                    "ids": [msg["id"] for msg in batch],
                    "addLabelIds": [label_id],
                    "removeLabelIds": ["INBOX"],
                },
            ).execute()
            total_moved += len(batch)
            print(f"Moved {len(batch)} emails to '{LABEL_NAME}' (total: {total_moved})")
            time.sleep(1)
        except HttpError as error:
            print(f"Error moving batch: {error}")


def clean_move_to_label(service, whitelist_phrases):
    """
    Delete emails from the 'to delete' label, excluding those containing whitelist phrases.
    """
    # Search for emails with the 'to delete' label
    query = "label:to delete"
    print("Searching for emails with label 'to delete'...")
    email_ids = search_emails(service, query, whitelist_phrases)

    # Check if there are emails to delete
    if not email_ids:
        print("No emails found in 'to delete' label matching the criteria.")
        return

    # Prompt for confirmation
    print(
        f"WARNING: About to permanently delete {len(email_ids)} emails from 'to delete' label."
    )
    confirm = input("Type 'y' to proceed, or any other key to cancel: ").strip().lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return

    # Delete the emails
    delete_emails(service, email_ids)


def remove_token():
    """Remove the OAuth token file to force re-authentication."""
    if os.path.exists(TOKEN_PATH):
        try:
            os.remove(TOKEN_PATH)
            print(f"Successfully removed OAuth token file: {TOKEN_PATH}")
        except Exception as e:
            print(f"Error removing OAuth token file: {e}")
    else:
        print(f"No OAuth token file found at: {TOKEN_PATH}")


def main():
    """Manage Gmail emails by deleting, archiving, or moving them to a 'to delete' label."""
    parser = argparse.ArgumentParser(
        description="Manage Gmail emails by deleting, archiving, or moving them to a 'to delete' label, excluding those containing whitelisted phrases from a file."
    )
    parser.add_argument(
        "search_query",
        nargs="?",
        default=None,
        help="The Gmail search query to find emails to delete or move.",
    )
    parser.add_argument(
        "-w",
        "--whitelist",
        default="whitelist.txt",
        help="Path to the file containing whitelisted phrases (default: whitelist.txt).",
    )
    parser.add_argument(
        "-a",
        "--archive",
        action="store_true",
        help="If set, archive emails instead of deleting them.",
    )
    parser.add_argument(
        "--move-to-delete",
        action="store_true",
        help="(default) If set, move emails to the 'to delete' label instead of deleting or archiving.",
    )
    parser.add_argument(
        "-p",
        "--permanently",
        action="store_true",
        help="If set, deletes email permanently. Use with caution!",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="If set, moves all emails in 'to delete' to be deleted permanently. Use with caution!",
    )
    parser.add_argument(
        "-r",
        "--remove-token",
        action="store_true",
        help="If set, removes the OAuth token file to force re-authentication.",
    )
    args = parser.parse_args()

    # Handle remove-token action
    if args.remove_token:
        remove_token()
        return

    # Determine the action
    if args.permanently:
        action = "delete"
    elif args.archive:
        action = "archive"
    elif args.clean:
        action = "clean"
    elif args.move_to_delete:
        action = "move_to_delete"
    else:
        action = "move_to_delete"  # Default action

    # For actions other than clean, require search_query
    if action != "clean" and args.search_query is None:
        parser.error(
            "search_query is required unless --clean or --remove-token is used."
        )

    # Load whitelist phrases
    whitelist_phrases = []
    if os.path.exists(args.whitelist):
        with open(args.whitelist, "r") as f:
            whitelist_phrases = [line.strip() for line in f if line.strip()]

    # Authenticate and get Gmail service
    service = get_gmail_service()

    # If moving to delete, get or create the label
    if action == "move_to_delete":
        label_id = get_or_create_label(service, LABEL_NAME)

    # Search for emails
    if args.search_query is not None:
        print(f"Searching for emails containing '{args.search_query}'...")

    emails = search_emails(service, args.search_query, whitelist_phrases)

    if emails:
        # Prompt for confirmation based on action
        if action == "delete":
            print(
                f"WARNING: About to permanently delete {len(emails)} emails. This action cannot be undone."
            )
        elif action == "archive":
            print(
                f"About to archive {len(emails)} emails. They will be moved out of the inbox but can be found in 'All Mail'."
            )
        elif action == "move_to_delete":
            print(
                f"About to move {len(emails)} emails to the '{LABEL_NAME}' label. They will be removed from the inbox."
            )
        if action == "clean":
            # print(
            #     f"WARNING: About to permanently delete {len(emails)} emails from the 'to delete' folder. This action cannot be undone."
            # )
            clean_move_to_label(service, whitelist_phrases)
            return

        confirm = (
            input("Type 'y' to proceed, or any other key to cancel: ").strip().lower()
        )
        if confirm == "y":
            if action == "delete":
                delete_emails(service, emails)
            elif action == "archive":
                archive_emails(service, emails)
            elif action == "move_to_delete":
                move_to_label(service, emails, label_id)
            elif action == "clean":
                clean_move_to_label(service, whitelist_phrases)

        else:
            print("Action cancelled.")
    else:
        print("No emails found matching the search criteria.")


if __name__ == "__main__":
    main()
