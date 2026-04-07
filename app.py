# app.py
# ─────────────────────────────────────────────────────────────────
# This is the Flask web server — the "middleman" between the
# HTML chat interface and the chatbot logic in chatbot.py.
#
# Flask is a lightweight Python web framework. Here it does 3 things:
#   1. Serves the chat page (index.html) when you open the browser
#   2. Creates a /chat API endpoint the frontend sends messages to
#   3. Maintains separate session state for each user tab
# ─────────────────────────────────────────────────────────────────

from flask import Flask, request, jsonify, render_template, session
from chatbot import CyberBot
import os

# ── App setup ─────────────────────────────────────────────────────
app = Flask(__name__)

# Secret key is needed for Flask sessions (stores data per browser tab).
# In production, replace this with a long random string from os.urandom(24).
app.secret_key = os.environ.get("SECRET_KEY", "cybershield-dev-secret-2024")

# ── In-memory session store ────────────────────────────────────────
# We store one CyberBot instance per user session ID.
# This means each browser tab gets its own independent chatbot state.
# In production, use a proper session store like Redis.
bot_sessions: dict[str, CyberBot] = {}


def get_bot() -> CyberBot:
    """
    Get (or create) a CyberBot instance for the current user session.
    Flask's session dict persists a unique session ID per browser tab.
    """
    # Assign a unique session ID if this is a new visitor
    if "session_id" not in session:
        session["session_id"] = os.urandom(16).hex()

    sid = session["session_id"]

    # Create a new bot if this session doesn't have one yet
    if sid not in bot_sessions:
        bot_sessions[sid] = CyberBot()

    return bot_sessions[sid]


# ── Routes ────────────────────────────────────────────────────────

@app.route("/")
def index():
    """
    Serve the main chat page.
    Flask looks for templates in the /templates folder automatically.
    """
    bot = get_bot()
    welcome_message = bot.get_welcome()
    return render_template("index.html", welcome=welcome_message)


@app.route("/chat", methods=["POST"])
def chat():
    """
    API endpoint for sending messages.
    
    The frontend sends: { "message": "user's text" }
    This returns:       { "response": "bot's reply (HTML)" }
    
    Uses POST because we're sending data (the user's message) to the server.
    """
    # Parse the JSON body from the frontend
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()

    if not user_message:
        return jsonify({"response": "Please type a message! 😊"})

    # Get this user's bot and process the message
    bot = get_bot()
    reply = bot.process(user_message)

    return jsonify({"response": reply})


@app.route("/reset", methods=["POST"])
def reset():
    """
    Resets the chatbot state for the current session.
    Called when the user clicks the 'Reset' button in the UI.
    """
    bot = get_bot()
    bot.reset()
    return jsonify({"response": bot.get_welcome()})


# ── Run the server ────────────────────────────────────────────────
if __name__ == "__main__":
    # debug=True means:
    #   • The server auto-reloads when you save a file
    #   • Detailed error pages are shown in the browser
    # NEVER use debug=True in production!
    print("🛡️  CyberShield Bot starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
