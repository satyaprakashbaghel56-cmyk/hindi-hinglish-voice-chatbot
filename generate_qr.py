"""Generate a QR image for the deployed website URL.
Usage: python generate_qr.py https://your-app.onrender.com
"""
import sys
from urllib.parse import urlparse
import qrcode

if len(sys.argv) != 2:
    print("Usage: python generate_qr.py https://your-app.onrender.com")
    raise SystemExit(1)

url = sys.argv[1].strip()
parsed = urlparse(url)
if parsed.scheme != "https" or not parsed.netloc:
    print("Please provide a valid public HTTPS URL, e.g. https://your-app.onrender.com")
    raise SystemExit(1)

img = qrcode.make(url)
img.save("chatbot_qr.png")
print("Saved chatbot_qr.png for:", url)
