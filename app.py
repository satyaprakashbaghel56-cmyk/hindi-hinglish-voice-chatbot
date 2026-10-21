import os

from flask import Flask, render_template, request, jsonify
from google import genai

app = Flask(__name__)

# API key Render ke Environment Variables se milegi.
API_KEY = os.environ.get("GEMINI_API_KEY")

# Zaroorat padne par Render mein GEMINI_MODEL badal sakte ho.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_INSTRUCTION = """
You are Friend for Farmer, a helpful agriculture assistant for Indian farmers.

Language rules:
- If language is hi, answer in simple Hindi.
- If language is en, answer in simple English.
- If language is hi-en, answer in natural Hinglish using easy Hindi and English.
- Follow the language selected by the user.
- Give clear, practical, beginner-friendly answers with short headings or steps when useful.

Agriculture rules:
- Help with crops, soil, irrigation, seeds, nutrients, farming methods,
  crop problems and general agriculture education.
- Never pretend that you checked live weather, live market prices,
  current government schemes or real-time data unless a verified tool is connected.
- For crop disease or pest questions, explain possible causes carefully.
  Do not confidently diagnose from limited information.
- Do not invent pesticide names, doses, mixing instructions or guaranteed results.
  Recommend checking the product label and consulting a qualified local
  agriculture officer or Krishi Vigyan Kendra (KVK) when treatment is uncertain.
- For government schemes, explain general information and advise checking
  official government sources for current eligibility and application dates.
- If a question lacks important details, ask a short follow-up question.
- Be polite, useful and honest about uncertainty.
"""


def get_ai_reply(message, language):
    """Gemini se agriculture-related answer generate karta hai."""

    prompt = f"""
Selected response language: {language}

Farmer's question:
{message}

Answer the farmer in the selected language.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=SYSTEM_INSTRUCTION + "\n\n" + prompt,
    )

    reply = response.text

    if not reply or not reply.strip():
        raise ValueError("The AI returned an empty response.")

    return reply.strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    # Health check API key ke bina bhi kaam karega.
    return jsonify({
        "status": "ok",
        "service": "Friend for Farmer"
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}

    message = str(data.get("message", "")).strip()
    language = str(data.get("language", "hi-en")).strip().lower()

    # Supported language values ko limit karte hain.
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
        app.logger.error("GEMINI_API_KEY is not configured.")
        return jsonify({
            "reply": (
                "AI abhi configure nahi hua hai. "
                "Please administrator se API setup check karwayein."
            ),
            "language": language
        }), 503

    try:
        reply = get_ai_reply(message, language)

        return jsonify({
            "reply": reply,
            "language": language
        })

    except Exception:
        # Secret keys ya internal error details user ko nahi dikhate.
        app.logger.exception("Gemini API request failed.")

        if language == "en":
            error_reply = (
                "Sorry, the AI service is temporarily unavailable. "
                "Please try again in a little while."
            )
        elif language == "hi":
            error_reply = (
                "Maaf kijiye, AI seva abhi uplabdh nahi hai. "
                "Kripya thodi der baad dobara koshish karein."
            )
        else:
            error_reply = (
                "Maaf kijiye, AI service abhi available nahi hai. "
                "Thodi der baad dobara try karein."
            )

        return jsonify({
            "reply": error_reply,
            "language": language
        }), 502


if __name__ == "__main__":
    # Local testing only; Render par Gunicorn start command use hoga.
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
