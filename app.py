from flask import Flask, render_template, request, jsonify
import os
import random
from datetime import datetime

app = Flask(__name__)

def get_reply(message: str) -> str:
    msg = (message or "").strip().lower()
    if not msg:
        return "Kuch likho ya microphone se bolo, phir main jawab dunga."

    if any(w in msg for w in ["hello", "hi", "hey", "namaste", "नमस्ते", "हेलो"]):
        return random.choice([
            "Namaste! Kaise ho?",
            "Hello dost! Main tumhari kya help kar sakta hoon?",
            "Hi! Aaj kya seekhna hai?"
        ])
    if any(w in msg for w in ["tumhara naam", "naam kya", "your name", "तुम्हारा नाम", "नाम क्या"]):
        return "Mera naam Hindi Hinglish Voice Chatbot hai!"
    if any(w in msg for w in ["kaise ho", "how are you", "कैसे हो"]):
        return "Main badhiya hoon! Tum kaise ho?"
    if "python" in msg or "पायथन" in msg or "पाइथन" in msg:
        return "Python ek popular programming language hai. Isse websites, automation aur AI projects banaye ja sakte hain."
    if any(w in msg for w in ["joke", "chutkula", "चुटकुला", "मजाक"]):
        return "Ek computer ne chai kyun nahi pi? Kyunki uska cup hi nahi tha!"
    if any(w in msg for w in ["time", "samay", "समय", "टाइम"]):
        return "Abhi time hai " + datetime.now().strftime("%I:%M %p")
    if any(w in msg for w in ["help", "madad", "मदद"]):
        return "Main basic chatbot hoon. Tum mujhse Python, apna naam, time ya ek joke pooch sakte ho."
    if any(w in msg for w in ["bye", "goodbye", "alvida", "बाय"]):
        return "Bye dost! Phir baat karenge."
    return "Main abhi basic chatbot hoon, isliye ye sawaal samajh nahi aaya. Thode simple shabdon mein poochho."

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", ""))[:1000]
    return jsonify({"reply": get_reply(message)})

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
