# AI-Based Phishing and Scam Detector (Prototype)

This repository contains a minimal prototype of an AI-based phishing and scam detector composed of:

- `server/` — FastAPI backend that analyzes text using a transformer-based classifier plus heuristics for links and suspicious keywords.
- `extension/` — A Chrome extension (Manifest V3) popup UI to paste messages, enter sender info, and get a risk analysis from the backend.

This is a starting point — the classifier is a prototype. For production use, train a dedicated model, add secure deployment, and follow privacy best practices.

## Quick start (macOS / zsh)

1. Create and activate a Python virtualenv, then install server deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r server/requirements.txt
```

2. Run the backend server:

```bash
uvicorn server.main:app --reload --port 8000
```

3. Load the extension in Chrome/Edge/Brave:

- Open `chrome://extensions`
- Enable "Developer mode"
- Click "Load unpacked" and choose the `extension/` directory

4. Open the extension popup, paste an email or SMS text, enter sender, and click "Analyze".

## Notes

- This prototype uses a general text-classification transformer as a placeholder. Replace with a trained phishing classifier for higher accuracy.
- For privacy, consider on-device inference or an encrypted server. Avoid sending user-sensitive data without consent.

## CLI: analyze files locally

If you'd rather analyze local email files, there's a simple CLI tool that uses the same analyzer.

Run:

```bash
source .venv/bin/activate
python server/cli.py /path/to/email.eml
# or analyze all .eml/.txt files in a folder and write JSON output
python server/cli.py /path/to/emails/ --json results.json
```

The CLI will print a short verdict for each file: `SCAM`, `POTENTIAL`, or `OK`, along with a numeric risk score and reasons.

# BEA
