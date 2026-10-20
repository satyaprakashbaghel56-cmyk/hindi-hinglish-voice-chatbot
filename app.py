from flask import Flask, request, jsonify, render_template
from datetime import datetime
import ast
import operator
import re
import os

app = Flask(__name__)

# Rule-based Hindi agriculture chatbot. No paid AI API or live weather data.

CROPS = {
    "गेहूं": "गेहूं के लिए समय पर बुवाई, संतुलित खाद, खेत की नमी और स्थानीय सलाह के अनुसार सिंचाई जरूरी है।",
    "धान": "धान में पानी का प्रबंधन, खरपतवार नियंत्रण और क्षेत्र के अनुसार उपयुक्त किस्म महत्वपूर्ण हैं।",
    "मक्का": "मक्का में अच्छी जल निकासी, सही समय पर बुवाई और मिट्टी की नमी का ध्यान रखें।",
    "चना": "चना सामान्यतः रबी फसल है। जलभराव से बचाएँ और स्थानीय सलाह के अनुसार बीज उपचार करें।",
    "सरसों": "सरसों में समय पर बुवाई और कीटों की नियमित निगरानी उपयोगी है।",
    "सोयाबीन": "सोयाबीन में अच्छी जल निकासी, उपयुक्त बीज और खरपतवार नियंत्रण महत्वपूर्ण हैं।",
    "कपास": "कपास में नियमित खेत निरीक्षण और नमी का प्रबंधन जरूरी है। कीट की पहचान के बिना स्प्रे न करें।",
    "आलू": "आलू में जल निकासी, स्वस्थ बीज-कंद और स्थानीय सलाह के अनुसार सिंचाई का ध्यान रखें।",
    "टमाटर": "टमाटर में संतुलित सिंचाई, सहारा और नियमित निरीक्षण उपयोगी हैं। लक्षण हों तो कृषि विशेषज्ञ से पहचान कराएँ।",
    "प्याज": "प्याज में नमी का संतुलन, अच्छी जल निकासी और कटाई के बाद सही सुखाना महत्वपूर्ण है।",
}

def has_any(text, words):
    return any(word in text for word in words)

def safe_calculate(expr):
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
    tree = ast.parse(expr, mode="eval")
    binops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
    unops = {ast.UAdd: operator.pos, ast.USub: operator.neg}

    def visit(node, depth=0):
        if depth > 10:
            raise ValueError("Too complex")
        if isinstance(node, ast.Expression):
            return visit(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 10**12:
                raise ValueError("Too large")
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in binops:
            left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 8:
                raise ValueError("Power too large")
            result = binops[type(node.op)](left, right)
            if abs(result) > 10**15:
                raise ValueError("Result too large")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in unops:
            return unops[type(node.op)](visit(node.operand, depth + 1))
        raise ValueError("Unsupported expression")
    return visit(tree)

def get_reply(message):
    raw = (message or "").strip()
    text = raw.lower()
    if not raw:
        return "कृपया अपना सवाल लिखें या माइक से बोलें।"

    if has_any(text, ["नमस्ते", "नमस्कार", "राम राम", "hello", "hi", "हेलो"]):
        return "नमस्ते किसान भाई/बहन! 🙏 मैं Friend for Farmer हूँ। आप फसल, सिंचाई, मिट्टी और खेती की सामान्य जानकारी पूछ सकते हैं।"
    if has_any(text, ["तुम कौन", "आप कौन", "तुम्हारा नाम", "आपका नाम", "who are you"]):
        return "मेरा नाम Friend for Farmer है। 🌾 मैं खेती से जुड़ी सामान्य जानकारी देने वाला chatbot हूँ।"

    for crop, advice in CROPS.items():
        if crop in raw:
            if has_any(text, ["बीमारी", "रोग", "पीला", "दाग", "कीड़ा", "कीट", "इलाज", "स्प्रे", "दवा", "कीटनाशक", "pesticide"]):
                return f"{crop} में रोग या कीट की पहचान केवल टेक्स्ट से पक्की नहीं हो सकती। फसल की साफ तस्वीर और जिला/गाँव की जानकारी लेकर स्थानीय कृषि विज्ञान केंद्र (KVK) से पुष्टि करें। पहचान के बिना दवा या मात्रा तय न करें।"
            if has_any(text, ["खाद", "उर्वरक", "fertilizer", "यूरिया", "डीएपी"]):
                return f"{crop} में खाद की मात्रा मिट्टी की जाँच, किस्म और फसल की अवस्था पर निर्भर करती है। मिट्टी परीक्षण रिपोर्ट और स्थानीय कृषि विभाग/KVK की सिफारिश अपनाएँ।"
            if has_any(text, ["पानी", "सिंचाई", "irrigation"]):
                return f"{crop} में सिंचाई का समय मिट्टी, फसल की अवस्था और बारिश पर निर्भर करता है। खेत की नमी जाँचें, जलभराव से बचें और स्थानीय कृषि सलाह अपनाएँ।"
            if has_any(text, ["मौसम", "बारिश", "weather", "तापमान"]):
                return "मेरे पास लाइव मौसम डेटा नहीं है। अपने जिले का ताज़ा पूर्वानुमान IMD की आधिकारिक सेवा या स्थानीय कृषि विभाग से जाँचें।"
            return advice

    if has_any(text, ["मौसम", "आज बारिश", "कल बारिश", "तापमान", "weather"]):
        return "लाइव मौसम बताने के लिए मौसम सेवा जोड़नी होगी। अभी मेरे पास लाइव मौसम डेटा नहीं है। IMD की आधिकारिक सेवा या अपने जिले के कृषि विभाग का पूर्वानुमान देखें।"
    if has_any(text, ["मिट्टी", "soil", "मिट्टी की जांच", "मिट्टी परीक्षण"]):
        return "मिट्टी की जाँच के लिए नजदीकी कृषि विभाग, कृषि विज्ञान केंद्र (KVK) या मिट्टी परीक्षण प्रयोगशाला से संपर्क करें। खाद की मात्रा रिपोर्ट के आधार पर तय करें।"
    if has_any(text, ["खाद", "उर्वरक", "fertilizer", "यूरिया", "डीएपी"]):
        return "खाद की सही मात्रा फसल, मिट्टी और अवस्था पर निर्भर करती है। मिट्टी परीक्षण और स्थानीय कृषि विभाग/KVK की सलाह के अनुसार ही खाद दें।"
    if has_any(text, ["कीड़ा", "कीट", "बीमारी", "रोग", "पत्ते पीले", "दाग", "स्प्रे", "कीटनाशक", "pesticide"]):
        return "कीट या रोग की पहचान के बिना दवा बताना सुरक्षित नहीं है। फसल की साफ तस्वीर और जिला/गाँव की जानकारी के साथ कृषि विज्ञान केंद्र या कृषि अधिकारी से सलाह लें।"
    if has_any(text, ["सिंचाई", "पानी कब", "पानी कितना", "irrigation"]):
        return "सिंचाई का समय मिट्टी, फसल की अवस्था और बारिश पर निर्भर करता है। खेत की नमी जाँचें, जलभराव से बचें और स्थानीय कृषि सलाह अपनाएँ।"
    if has_any(text, ["सरकारी योजना", "योजना", "सब्सिडी", "पीएम किसान", "pm kisan"]):
        return "सरकारी योजनाओं के नियम बदल सकते हैं। ताज़ा जानकारी आधिकारिक सरकारी पोर्टल या अपने कृषि/राजस्व कार्यालय से पुष्टि करें।"
    if has_any(text, ["समय", "टाइम", "time", "तारीख", "date"]):
        now = datetime.now()
        return f"सर्वर के अनुसार तारीख {now.strftime('%d-%m-%Y')} और समय {now.strftime('%I:%M %p')} है।"
    if has_any(text, ["धन्यवाद", "शुक्रिया", "thank you"]):
        return "आपका स्वागत है! 🌾 खेती से जुड़ा कोई और सवाल हो तो पूछिए।"
    if has_any(text, ["मदद", "help", "क्या पूछ", "क्या कर सकते"]):
        return "आप गेहूं, धान, मक्का, चना, सरसों, सोयाबीन, मिट्टी परीक्षण, सिंचाई और खाद के बारे में पूछ सकते हैं। लाइव मौसम या दवा की सलाह के लिए आधिकारिक स्रोत से पुष्टि जरूरी है।"

    candidate = re.sub(r"^(calculate|गणना करो|हल करो)\s*", "", raw.lower())
    if len(candidate) <= 80 and re.fullmatch(r"[\d\s.+\-*/()%×÷^]+", candidate):
        try:
            return f"जवाब: {safe_calculate(candidate)}"
        except Exception:
            pass

    return "माफ़ कीजिए, मुझे इस सवाल का पक्का जवाब अभी नहीं पता। सवाल थोड़ा विस्तार से लिखें या स्थानीय कृषि विज्ञान केंद्र/KVK से सलाह लें।"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "Friend for Farmer"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify({"reply": "कृपया सवाल टेक्स्ट में भेजें।"}), 400
    if len(message) > 1000:
        return jsonify({"reply": "कृपया 1000 अक्षरों से छोटा सवाल भेजें।"}), 400
    return jsonify({"reply": get_reply(message)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))

