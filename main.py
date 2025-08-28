from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from groq_agent import GroqAgent
from Tools import TOOLS  # Your tools dictionary
import os
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Al

# --- Initialize GroqAgent ---
GROQ_KEY = os.environ.get("GROQ_KEY")  # key comes from environment
if not GROQ_KEY:
    raise ValueError("GROQ_KEY environment variable is not set!")

groq_agent = GroqAgent(api_key=GROQ_KEY)
executor = ThreadPoolExecutor(max_workers=2)

# --- Global conversation history ---
conversation_history = {}  # store last 20 messages per user

# --- Routes ---
@app.route("/", methods=["GET"])
def home():
    return "✅ API is running! Use POST /chat to interact."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    user_id = data.get("user_id", "default_user")

    history = conversation_history.get(user_id, [])

    # Run GroqAgent synchronously
    def run_agent():
        return groq_agent.handle_request(user_input, history)

    result, updated_history = run_agent()
    conversation_history[user_id] = updated_history[-20:]  # keep last 20 messages

    return jsonify({"reply": str(result)})

# --- No app.run() needed for Render / Gunicorn ---

