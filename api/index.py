from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import os
from services.character import get_character
from services.ai import generate_reply

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "waifu_secret_key_88")

MAX_HISTORY = 10


@app.route("/")
def home():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html", history=session["history"])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    role = data.get("role", "waguri")
    user_message = data.get("message")

    # Reset history kalau karakter berubah, biar konteks gak kebawa dari role lain.
    current_role = session.get("role")
    if current_role != role:
        session["history"] = []
        session["role"] = role

    character = get_character(role)
    if not character:
        return jsonify({"error": "Karakter tidak ditemukan!"}), 404

    history = session.get("history", [])


    reply = generate_reply(
        character_prompt=character["prompt"],
        history=history,
        user_message=user_message
    )

    history.append({"user": user_message, "waifu": reply})
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    session["history"] = history
    session.modified = True

    return jsonify({
        "name": character["name"],
        "reply": reply,
        "avatar": character["avatar"],
        "emoji": character["emoji"]
    })

@app.route("/ai")
def ai_interface():
    role = request.args.get('role', 'waguri')
    return render_template("ai.html", role=role)

@app.route("/reset")
def reset():
    session.pop("history", None)
    return jsonify({"message": "Memory waifu telah di-reset!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)