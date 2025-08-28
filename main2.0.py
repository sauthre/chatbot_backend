from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from groq_agent import GroqAgent
from Tools import TOOLS  # Your tools dictionary

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Initialize GroqAgent ---
GROQ_KEY = "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"
groq_agent = GroqAgent(api_key=GROQ_KEY)
executor = ThreadPoolExecutor(max_workers=2)

conversation_history = {}  # global conversation dict

@app.route("/", methods=["GET"])
def home():
    return "✅ API is running! Use POST /chat to interact."

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    user_id = data.get("user_id", "default_user")

    history = conversation_history.get(user_id, [])

    # Run GroqAgent in ThreadPoolExecutor to mimic async Telegram behavior
    def run_agent():
        return groq_agent.handle_request(user_input, history)

    result, updated_history = run_agent()  # synchronous call for Flask
    conversation_history[user_id] = updated_history[-20:]  # keep last 20 messages

    return jsonify({"reply": str(result)})

if __name__ == "__main__":
    # Enable CORS if you want the frontend to work
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    print("Flask API is running...")
    app.run(host="0.0.0.0", port=5000)
