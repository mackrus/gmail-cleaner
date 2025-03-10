import os
import base64
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# If modifying these SCOPES, delete the token.json file
SCOPES = ["https://www.googleapis.com/auth/gmail.modify", "https://mail.google.com/"]


def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
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


def main(search_string):
    """Main function with enhanced logging."""
    service = authenticate_gmail()

    # Search for emails containing the string
    query = f'"{search_string}"'
    print(f"Searching for emails containing: {search_string}")

    emails = search_emails(service, query)
    print(f"Found {len(emails)} emails matching the search criteria")

    if emails:
        # Delete the found emails
        delete_emails(service, emails)
    else:
        print("No emails found matching the search criteria.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Delete Gmail emails containing a specific string."
    )
    parser.add_argument(
        "search_string", type=str, help="The string to search for in emails"
    )
    args = parser.parse_args()

    main(args.search_string)
