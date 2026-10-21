import os
from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_INSTRUCTION = """
You are Friend for Farmer, an agriculture assistant for Indian farmers.

Reply according to the selected language:
- hi: simple Hindi
- en: simple English
- hi-en: natural Hinglish

Give practical, clear answers about crops, soil, irrigation, seeds,
fertilizers and farming.

Never claim to know live weather, mandi prices or current scheme details
unless verified data is available.

For uncertain crop diseases or pest treatments, ask for symptoms and
recommend consulting a local agriculture expert or KVK.
Do not invent pesticide doses or guarantee results.
Be polite and honest about uncertainty.
"""


def get_ai_reply(message, language):
    response = client.models.generate_content(
        model=MODEL,
        contents=(
            SYSTEM_INSTRUCTION
            + "\n\nSelected language: "
            + language
            + "\nFarmer's question: "
            + message
        ),
    )

    reply = response.text

    if not reply or not reply.strip():
        raise ValueError("Empty response from Gemini")

    return reply.strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()
    language = str(data.get("language", "hi-en")).strip().lower()

    if language not in ("hi", "en", "hi-en"):
        language = "hi-en"

    if not message:
        return jsonify({
            "reply": "Please apna sawal type ya bolkar bhejein.",
            "language": language
        }), 400

    if len(message) > 3000:
        return jsonify({
            "reply": "Please apna sawal 3000 characters se chhota rakhein.",
            "language": language
        }), 400

    if client is None:
        return jsonify({
            "reply": (
                "AI configure nahi hua hai. "
                "Render mein GEMINI_API_KEY check karein."
            ),
            "language": language
        }), 503

    try:
        reply = get_ai_reply(message, language)

        return jsonify({
            "reply": reply,
            "language": language
        }), 200

    except Exception:
        app.logger.exception("Gemini request failed")

        if language == "en":
            error = "AI service is temporarily unavailable. Please try again."
        elif language == "hi":
            error = "AI seva abhi uplabdh nahi hai. Kripya dobara koshish karein."
        else:
            error = "AI service abhi available nahi hai. Thodi der baad try karein."

        return jsonify({
            "reply": error,
            "language": language
        }), 502


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
