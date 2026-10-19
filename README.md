# Hindi Hinglish Voice Chatbot (Flask + Browser Voice)

## Features
- Responsive phone-friendly chat interface
- Python Flask backend with basic rule-based Hindi/Hinglish replies
- Browser speech recognition (`hi-IN`) where supported
- Browser speech synthesis for voice replies
- QR generator for the final public HTTPS URL

## Run locally (Windows)
1. Install Python 3.10+ from https://www.python.org/downloads/
2. Open Command Prompt in this folder.
3. Run:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   python app.py
   ```
4. On the same computer, open http://127.0.0.1:5000

For phone microphone access, use the deployed HTTPS site. A plain local HTTP URL may not grant microphone access from another phone.

## Free hosting on Render
1. Create/sign in to a GitHub account and create a new repository.
2. Upload all project files, including `app.py`, `requirements.txt`, `render.yaml`, and the `templates` folder.
3. Open https://render.com and sign in.
4. Choose **New + → Web Service**, connect your repository.
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Instance type: **Free** (if available for your account)
6. Deploy and wait for the service URL, such as `https://your-service.onrender.com`.
7. Open the URL on your phone and allow microphone access when asked.

Render free services can sleep when idle and may take a short time to wake up. Check current free-plan limits before deploying.

## Generate the QR code after deployment
In the same project folder, run:
```bash
python -m pip install "qrcode[pil]"
python generate_qr.py https://your-service.onrender.com
```
Replace the example URL with your exact Render URL. This creates `chatbot_qr.png`. Print it or display it on another screen and scan it with your phone camera.

## Important voice notes
- The mic uses the browser Web Speech API; speech recognition is not supported in every browser/device and may need internet.
- Speech output uses the phone/browser's built-in speech synthesis voices. A Hindi voice may not be installed on every device.
- This is a starter rule-based chatbot, not a ChatGPT-like AI. It does not save conversation history on the server.
