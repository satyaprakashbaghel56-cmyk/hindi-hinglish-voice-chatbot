from flask import Flask, render_template, request, jsonify
import random
import re
import ast
import operator
from datetime import datetime

app = Flask(__name__)

# Basic conversation memory for the current browser session
# (Yeh sirf simple naam yaad rakhta hai.)
user_names = {}

JOKES = [
    "Computer thak kyun nahi jaata? Kyunki woh hamesha sleep mode mein ja sakta hai!",
    "Teacher: Computer ka dimaag kahan hota hai? Student: CPU mein!",
    "Programmer chai kyun peeta hai? Taaki uska system refresh ho sake!"
]

def safe_math(expression):
    """Sirf basic arithmetic allow karta hai; arbitrary code nahi."""
    allowed = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def calculate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10**12:
                raise ValueError("Number too large")
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in allowed:
            left = calculate(node.left)
            right = calculate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Power too large")

            result = allowed[type(node.op)](left, right)
            if abs(result) > 10**12:
                raise ValueError("Result too large")
            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
            return allowed[type(node.op)](calculate(node.operand))

        raise ValueError("Unsupported expression")

    tree = ast.parse(expression, mode="eval")
    return calculate(tree.body)


def get_reply(message, user_id="default"):
    message = (message or "").strip()
    text = message.lower()

    if not message:
        return "Kuch likho ya microphone se bolo, phir main jawab dunga."

    # Naam yaad rakhna
    name_match = re.search(
        r"(?:mera naam|my name is|mujhe)\s+([a-zA-Z][a-zA-Z ]{0,30})",
        message,
        re.IGNORECASE
    )

    if name_match and ("naam" in text or "my name is" in text):
        name = name_match.group(1).strip().title()
        user_names[user_id] = name
        return f"Namaste {name}! 😊 Ab main is browser session mein tumhara naam yaad rakhunga."

    if any(x in text for x in ["mera naam kya", "what is my name", "naam yaad hai"]):
        name = user_names.get(user_id)
        if name:
            return f"Tumhara naam {name} hai!"
        return "Tumne abhi mujhe apna naam nahi bataya. 'Mera naam Rahul hai' aise likho."

    # Greetings
    if any(x in text for x in ["namaste", "hello", "hi", "hey", "pranam"]):
        return random.choice([
            "Namaste! 😊 Aaj main tumhari kya help karun?",
            "Hello! Kaise ho? Kuch poochhna hai?",
            "Hi! Main taiyaar hoon. Batao kya jaanna hai!"
        ])

    if any(x in text for x in ["kaise ho", "how are you", "kya haal"]):
        return "Main badhiya hoon aur tumhari help ke liye taiyaar hoon! 😊 Tum kaise ho?"

    if any(x in text for x in ["tumhara naam", "your name", "who are you"]):
        return "Main tumhara Hindi-Hinglish chatbot hoon. 😊 Tum mujhe apna AI helper keh sakte ho!"

    if any(x in text for x in ["thank you", "thanks", "shukriya", "dhanyavaad"]):
        return "Koi baat nahi! 😊 Aur kuch poochhna ho toh batao."

    if any(x in text for x in ["bye", "alvida", "good night"]):
        return "Achha, phir milte hain! Apna khayal rakhna. 👋"

    # Jokes
    if any(x in text for x in ["joke", "chutkula", "hasao", "funny"]):
        return random.choice(JOKES)

    # Time and date
    if "time" in text or "samay" in text or "kitne baje" in text:
        return "Abhi server ka time hai: " + datetime.now().strftime("%I:%M %p")

    if "date" in text or "aaj ki tareekh" in text or "aaj kya date" in text:
        return "Aaj ki tareekh: " + datetime.now().strftime("%d-%m-%Y")

    # Binary conversion
    binary_match = re.search(
        r"(?:binary|bainari)\s+(?:mein\s+)?(?:convert|badlo|batao)?\s*(\d+)",
        text
    )
    if binary_match:
        number = int(binary_match.group(1))
        return f"{number} ka binary code hai: {bin(number)[2:]}"

    # ASCII for a single character
    ascii_match = re.search(r"ascii\s+(?:of\s+)?(?:letter\s+)?([a-zA-Z0-9])", text)
    if ascii_match:
        char = ascii_match.group(1)
        return f"'{char}' ka ASCII decimal {ord(char)} aur binary {format(ord(char), '08b')} hai."

    # Basic maths: e.g. calculate 12 * 4
    math_match = re.search(
        r"(?:calculate|solve|kitna hota hai|jodo|plus)\s+([0-9().+\-*/% ]{1,60})$",
        text
    )
    if math_match:
        try:
            answer = safe_math(math_match.group(1).strip())
            return f"Jawab hai: {answer}"
        except Exception:
            pass

    # Educational topics
    if "binary" in text:
        return (
            "Binary number system mein sirf 0 aur 1 hote hain. "
            "Computer data ko binary form mein represent karta hai. "
            "Example: decimal 5 ka binary 101 hota hai."
        )

    if "ascii" in text:
        return (
            "ASCII ek character encoding standard hai. Yeh letters aur "
            "symbols ko numbers assign karta hai. Example: A = 65 aur "
            "a = 97. A ka 8-bit binary 01000001 hai."
        )

    if "python" in text and any(x in text for x in ["kya hai", "what is", "samjhao", "explain"]):
        return (
            "Python ek programming language hai. Iska syntax beginners ke "
            "liye relatively simple hai. Example:\n\n"
            "print('Namaste duniya!')\n\n"
            "Yeh screen par Namaste duniya! print karega."
        )

    if any(x in text for x in ["help", "kya kar sakte", "what can you do"]):
        return (
            "Main abhi in cheezon mein help kar sakta hoon:\n"
            "• Greetings aur simple conversation\n"
            "• Jokes\n"
            "• Basic maths\n"
            "• Binary aur ASCII\n"
            "• Python ki basic information\n\n"
            "Koshish karo: 'binary 25', 'ASCII A', ya 'joke sunao'."
        )

    # Fallback
    return (
        "Main tumhari baat poori tarah samajh nahi paaya. 😊 "
        "Thoda alag tareeke se poochho. Tum 'help' likhkar dekh sakte ho."
    )


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", ""))[:500]

    # A simple browser identifier; this is not secure authentication.
    user_id = request.remote_addr or "default"
    reply = get_reply(message, user_id)

    return jsonify({"reply": reply})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(__import__("os").environ.get("PORT", 5000)),
        debug=False
    )
