# cc-project6 — College Inquiry Chatbot (Flask + Dialogflow ES)

This project is a simple web chatbot for common college questions. It:
- collects **First Name / Last Name / Email** on a login page
- displays that info on the chat page
- provides 4 **suggested questions** (assignment examples)
- sends user messages to **Dialogflow ES** and displays the agent response

## Tech
- **Frontend**: `templates/login.html`, `templates/index.html`
- **Backend**: Flask in `main.py`
- **Dialogflow**: `google-cloud-dialogflow` (ES, `dialogflow_v2`)
- **Cloud hosting**: designed for **Cloud Run** via `Dockerfile` (would need to add `app.yaml` for App Engine if that route is chosen)

## Configuration (recommended via environment variables)
The app reads these environment variables:
- **`DIALOGFLOW_PROJECT_ID`**: the GCP Project ID that contains your Dialogflow ES agent
- **`DIALOGFLOW_SESSION_ID`**: optional; defaults to `chatbot-session`
- **`FLASK_SECRET_KEY`**: required for secure sessions (login cookie)

If `DIALOGFLOW_PROJECT_ID` is not set, it falls back to the placeholder value in `main.py`.

## Local run (for development)
1) Create/activate a virtual environment (optional but recommended)
2) Install dependencies:

**PowerShell (Windows):**
```powershell
pip install -r requirements.txt
```

**Bash (macOS/Linux, Git Bash, WSL):**
```bash
pip3 install -r requirements.txt
```

3) If running locally and you want to authenticate with a service account key:
- Download a service account JSON key from GCP (do **not** commit it; `*.json` is ignored)
- Set credentials:

**PowerShell (Windows):**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\full\path\to\key.json"
```

**Bash (macOS/Linux, Git Bash, WSL):**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/full/path/to/key.json"
```

4) Set environment variables:

**PowerShell (Windows):**
```powershell
$env:DIALOGFLOW_PROJECT_ID="intro-to-cc-project-6"
$env:FLASK_SECRET_KEY="dev-not-for-production"
```

**Bash (macOS/Linux, Git Bash, WSL):**
```bash
export DIALOGFLOW_PROJECT_ID="intro-to-cc-project-6"
export FLASK_SECRET_KEY="dev-not-for-production"
```

5) Run:

**PowerShell (Windows):**
```powershell
python main.py
```

**Bash (macOS/Linux, Git Bash, WSL):**
```bash
python3 main.py
```

Then open `http://127.0.0.1:8080`.

## Deploy to Cloud Run (Console / dashboard method)

### One-time GCP setup
In your GCP project (the same one your Dialogflow agent uses), enable:
- **Cloud Run API**
- **Cloud Build API**
- **Artifact Registry API**
- **Dialogflow API**

### Deploy (no terminal)
1) Cloud Console → **Cloud Run** → **Create service**
2) Choose **Deploy one revision from source code**
3) Connect your GitHub repository (or select it if already connected)
4) Service settings:
   - Region: pick one (e.g. `us-central1`)
   - Authentication: **Allow unauthenticated invocations** (for TA testing)
5) Click **Create** and wait for build + deploy

Cloud Run will show a **Service URL**. That is where you can access the deployed application.

### Set required environment variables in Cloud Run
Cloud Run → your service → **Edit & deploy new revision** → **Variables & secrets**:
- `DIALOGFLOW_PROJECT_ID` = your GCP project id (where the Dialogflow agent lives)
- `FLASK_SECRET_KEY` = long random string
- (optional) `DIALOGFLOW_SESSION_ID`

### Grant Cloud Run permission to call Dialogflow
1) Cloud Run → your service → find **Service account** (under Security / Revision settings)
2) Cloud Console → **IAM & Admin → IAM** → **Grant access**
3) Principal: that service account email
4) Role: **Dialogflow API Client**

After IAM updates, retry the app. If you still see errors, check Cloud Run → **Logs** for `PermissionDenied` or `403`.

## Dialogflow notes (ES)
This app uses Dialogflow ES (`google.cloud.dialogflow_v2`). Your Dialogflow agent should include intents for the 4 assignment questions so the agent returns the detailed responses you configured.

## Troubleshooting
- **Fallback intent triggers**: add more training phrases / synonyms to intents
- **403 PermissionDenied**: IAM role missing for the Cloud Run service account, or `DIALOGFLOW_PROJECT_ID` is wrong
- **500 errors**: check Cloud Run logs for stack traces
