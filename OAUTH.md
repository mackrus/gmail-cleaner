## Gmail API Credentials

To use this tool, you need to set up Gmail API credentials in the Google Cloud Console. Follow these detailed steps, designed for beginners:

1. **Access Google Cloud Console**:
   - Go to [console.cloud.google.com](https://console.cloud.google.com/) and sign in with your Google account.

2. **Create a New Project**:
   - Click the project dropdown at the top and select **"New Project."**
   - Name it (e.g., `Gmail-Cleaner-Project`) and click **"Create."**
   - Switch to your new project using the dropdown.

3. **Enable the Gmail API**:
   - Navigate to **"APIs & Services" > "Library"** in the left sidebar.
   - Search for `Gmail API`, click it, and hit **"Enable."**

4. **Configure the OAuth Consent Screen**:
   - Go to **"APIs & Services" > "OAuth consent screen."**
   - Choose **"External"** and click **"Create."**
   - Fill in:
     - **App name**: `Gmail Cleaner`
     - **User support email**: Your email
     - **Developer contact information**: Your email
   - Click **"Save and Continue."**
   - Skip "Scopes," then add your email as a test user on the "Test users" page.
   - Save and ensure the app is in **"Testing"** mode.

5. **Create OAuth 2.0 Client Credentials**:
   - Go to **"APIs & Services" > "Credentials."**
   - Click **"Create Credentials" > "OAuth client ID."**
   - Select **"Desktop app,"** name it (e.g., `Gmail Cleaner Desktop Client`), and click **"Create."**
   - Download the `credentials.json` file by clicking the download icon next to your client ID.

6. **Place the `credentials.json` File**:
   - Move the file to `~/.gmail-cleaner/credentials.json` (e.g., `mv ~/Downloads/credentials.json ~/.gmail-cleaner/` on macOS/Linux).

7. **Authenticate**:
   - Run the tool (e.g., `gmail-clean "test search"`).
   - A browser will open; log in, approve the requested permissions, and bypass the "unverified app" warning if needed.
   - The tool will save a `token.pickle` file in `~/.gmail-cleaner/` for future use.

The tool requests the scope `https://www.googleapis.com/auth/gmail.modify` which allows it to read, search, label, archive, and delete emails. It does **not** grant full access to your Google Account or the ability to manage your account settings.
