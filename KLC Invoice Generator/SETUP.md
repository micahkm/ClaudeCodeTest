# KLC Invoice Generator — Setup

Follow these steps once before using the app for the first time.

## 1. Enable Google APIs

1. Go to https://console.cloud.google.com/
2. Create a new project (or select an existing one)
3. In the left menu: **APIs & Services → Library**
4. Search for and enable **Google Sheets API**
5. Search for and enable **Google Drive API**

## 2. Create OAuth2 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Name it anything (e.g., "KLC Invoice Generator")
5. Click **Create**, then **Download JSON**
6. Rename the downloaded file to `credentials.json`
7. Move it into this folder (`KLC Invoice Generator/`)

> `credentials.json` is in `.gitignore` — it will not be committed.

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 4. Create the Invoice Template in Google Drive

1. Open Google Drive
2. Create a new Google Sheet named exactly: `Invoice TEMPLATE`
3. Copy your existing invoice layout into it (or design from scratch)
4. Leave data cells blank — the app will fill them in

The template must be in a Google Drive folder (not "My Drive" root if possible).
The app will copy this template for any client that has no prior invoices.

## 5. Run the App

```bash
python app.py
```

On first run, a browser window will open asking you to authorize the app.
After authorizing, a `token.json` file is saved locally — future runs skip the browser.

> `token.json` is in `.gitignore` — it will not be committed.

## Troubleshooting

**"No 'Invoice TEMPLATE' found"** — Check that you created a sheet named exactly `Invoice TEMPLATE` in Drive and it is not in the Trash.

**"credentials.json not found"** — Make sure you downloaded and renamed the file correctly, and placed it in the `KLC Invoice Generator/` folder.

**Wrong cells filled** — The cell positions in `sheets.py` (constants at the top) were set based on the original invoice layout. If your template uses different rows/columns, update those constants.
