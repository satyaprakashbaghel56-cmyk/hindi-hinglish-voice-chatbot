from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)


def detect_language(text, requested_language=None):
    """Choose Hindi, English, or Hinglish response language."""
    allowed = {"hi", "en", "hi-en"}
    if requested_language in allowed:
        return requested_language

    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    words = set(re.findall(r"[a-z]+", text.lower()))
    hinglish_words = {
        "kya", "kaise", "kaisa", "kab", "kyun", "kyon", "hai",
        "hain", "ka", "ki", "ke", "mein", "me", "ko", "batao",
        "bataiye", "chahiye", "fasal", "paani", "pani", "mitti",
        "gehu", "gehun", "kheti", "sinchai", "khad", "mausam",
        "kaise", "karo", "karna", "kitna", "kitni", "mera", "meri"
    }
    return "hi-en" if words & hinglish_words else "en"


RESPONSES = {
    "greeting": {
        "hi": "नमस्ते किसान भाई! 🙏 मैं Friend for Farmer हूँ। आप फसल, मिट्टी, सिंचाई, खाद और खेती के बारे में पूछ सकते हैं। 🌱",
        "en": "Hello, Farmer! 🙏 I am Friend for Farmer. Ask me about crops, soil, irrigation, fertilizer, and farming. 🌱",
        "hi-en": "Namaste Kisaan Bhai! 🙏 Main Friend for Farmer hoon. Aap crops, soil, irrigation, fertilizer aur farming ke baare mein pooch sakte hain. 🌱"
    },
    "wheat": {
        "hi": "🌾 गेहूँ की अच्छी पैदावार के लिए मिट्टी की जाँच कराएँ, फसल की अवस्था के अनुसार सिंचाई करें और संतुलित खाद दें। सही मात्रा के लिए स्थानीय कृषि विशेषज्ञ की सलाह लें।",
        "en": "🌾 For better wheat yield, test your soil, irrigate according to the crop's growth stage, and use balanced fertilizer based on soil-test recommendations.",
        "hi-en": "🌾 Gehu ki achhi yield ke liye soil test karayein, crop ki growth stage ke according irrigation karein aur soil-test recommendation ke hisaab se balanced fertilizer use karein."
    },
    "rice": {
        "hi": "🌾 धान में सिंचाई का प्रबंधन मिट्टी, मौसम और फसल की अवस्था के अनुसार करें। अनावश्यक जलभराव और पानी की बर्बादी से बचें।",
        "en": "🌾 Manage rice irrigation according to soil, weather, and crop stage. Avoid unnecessary waterlogging and water waste.",
        "hi-en": "🌾 Rice mein soil, weather aur crop stage ke according irrigation manage karein. Extra waterlogging aur paani ki barbadi se bachein."
    },
    "maize": {
        "hi": "🌽 मक्का की फसल में समय पर सिंचाई, खरपतवार नियंत्रण और मिट्टी की जाँच के अनुसार खाद देना उपयोगी है।",
        "en": "🌽 Maize benefits from timely irrigation, weed control, and fertilizer based on soil-test recommendations.",
        "hi-en": "🌽 Maize mein timely irrigation, weed control aur soil-test ke according fertilizer dena useful hai."
    },
    "soil": {
        "hi": "🌱 मिट्टी की जाँच से pH और पोषक तत्वों की जानकारी मिलती है। इससे सही खाद चुनने और अनावश्यक खर्च घटाने में मदद मिलती है।",
        "en": "🌱 Soil testing measures pH and nutrient levels. It helps you choose suitable fertilizer and avoid unnecessary costs.",
        "hi-en": "🌱 Soil testing se pH aur nutrients ka pata chalta hai. Isse sahi fertilizer choose karne aur extra cost bachane mein help milti hai."
    },
    "water": {
        "hi": "💧 सिंचाई का समय फसल, मिट्टी, मौसम और फसल की अवस्था पर निर्भर करता है। मिट्टी की नमी देखें और जलभराव से बचें।",
        "en": "💧 Irrigation timing depends on the crop, soil, weather, and growth stage. Check soil moisture and avoid waterlogging.",
        "hi-en": "💧 Irrigation ka time crop, soil, weather aur growth stage par depend karta hai. Soil moisture check karein aur waterlogging se bachein."
    },
    "fertilizer": {
        "hi": "🌿 खाद का प्रकार और मात्रा फसल, मिट्टी की जाँच और फसल की अवस्था पर निर्भर करते हैं। मिट्टी की जाँच के आधार पर खाद दें।",
        "en": "🌿 Fertilizer type and quantity depend on the crop, soil test, and growth stage. Follow local agricultural recommendations.",
        "hi-en": "🌿 Fertilizer ki type aur quantity crop, soil test aur growth stage par depend karti hai. Local agriculture recommendations follow karein."
    },
    "weather": {
        "hi": "🌦️ मैं अभी लाइव मौसम नहीं देख सकता। ताज़ा पूर्वानुमान के लिए मौसम विभाग या आधिकारिक मौसम सेवा देखें।",
        "en": "🌦️ I cannot access live weather data right now. Check your official local weather service for the latest forecast.",
        "hi-en": "🌦️ Main abhi live weather check nahi kar sakta. Latest forecast ke liye official local weather service dekhein."
    },
    "disease": {
        "hi": "🍃 कृपया फसल का नाम और लक्षण बताएँ। सही पहचान और उपचार के लिए स्थानीय कृषि विशेषज्ञ या कृषि विज्ञान केंद्र (KVK) से सलाह लें।",
        "en": "🍃 Please share the crop name and symptoms. Consult a local agricultural expert or Krishi Vigyan Kendra (KVK) for reliable diagnosis and treatment advice.",
        "hi-en": "🍃 Crop ka naam aur symptoms batayein. Sahi diagnosis aur treatment ke liye local agriculture expert ya KVK se salah lein."
    },
    "schemes": {
        "hi": "🏛️ किसान योजनाओं के लिए कृषि विभाग या आधिकारिक सरकारी पोर्टल देखें। पात्रता और नियम योजना के अनुसार बदलते हैं।",
        "en": "🏛️ Check your agriculture department or official government portals for farmer schemes. Eligibility and rules vary by scheme.",
        "hi-en": "🏛️ Farmer schemes ke liye agriculture department ya official government portal check karein. Eligibility aur rules scheme ke according alag hote hain."
    },
    "unknown": {
        "hi": "माफ़ कीजिए, मैं यह सवाल अभी समझ नहीं पाया। आप फसल, मिट्टी, सिंचाई या खाद के बारे में पूछ सकते हैं।",
        "en": "Sorry, I couldn't understand that question. Try asking about crops, soil, irrigation, or fertilizer.",
        "hi-en": "Sorry, main abhi ye question samajh nahi paya. Aap crop, soil, irrigation ya fertilizer ke baare mein pooch sakte hain."
    }
}


def find_topic(message):
    text = message.lower()

    if any(x in text for x in (
        "namaste", "hello", "hey", "नमस्ते", "नमस्कार", "प्रणाम"
    )):
        return "greeting"

    if any(x in text for x in (
        "weather", "mausam", "मौसम", "बारिश", "वर्षा", "rain", "forecast"
    )):
        return "weather"

    if any(x in text for x in (
        "disease", "bimari", "बीमारी", "रोग", "कीट", "pest",
        "daag", "दाग", "spots", "पत्ते पीले", "yellow leaves"
    )):
        return "disease"

    if any(x in text for x in (
        "scheme", "yojana", "योजना", "subsidy", "सरकारी योजना",
        "government scheme", "पीएम किसान", "pm kisan"
    )):
        return "schemes"

    if any(x in text for x in (
        "fertilizer", "fertiliser", "khad", "खाद", "उर्वरक", "manure"
    )):
        return "fertilizer"

    if any(x in text for x in (
        "water", "irrigation", "sinchai", "सिंचाई", "पानी", "paani",
        "सिंचन", "waterlogging"
    )):
        return "water"

    if any(x in text for x in (
        "soil", "mitti", "मिट्टी", "भूमि", "जमीन", "zameen"
    )):
        return "soil"

    if any(x in text for x in (
        "wheat", "gehu", "gehun", "गेहूँ", "गेहूं", "गेंहू"
    )):
        return "wheat"

    if any(x in text for x in (
        "rice", "paddy", "dhan", "धान", "चावल"
    )):
        return "rice"

    if any(x in text for x in (
        "maize", "corn", "makka", "मक्का"
    )):
        return "maize"

    return "unknown"


def get_reply(message, requested_language=None):
    language = detect_language(message, requested_language)
    topic = find_topic(message)
    return RESPONSES[topic][language], language


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", data.get("text", ""))).strip()
    requested_language = data.get("language")

    if not message:
        return jsonify({"reply": "Please enter a message.", "language": "en"}), 400

    reply, language = get_reply(message, requested_language)
    return jsonify({"reply": reply, "language": language})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
