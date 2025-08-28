from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
from concurrent.futures import ThreadPoolExecutor
from groq_agent import GroqAgent
from Tools import TOOLS  # Your tools dictionary

# --- Bot token & Groq API key ---
TELEGRAM_BOT_TOKEN = "7897224092:AAFf-VMoofxVt5BQVXlRjK_Ot3M-I0EOF3o"
GROQ_KEY = "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"

# --- Initialize GroqAgent ---
groq_agent = GroqAgent(api_key=GROQ_KEY)
executor = ThreadPoolExecutor(max_workers=2)

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your AI agent. Ask me anything.")

conversation_history = {}  # global dict

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id

    history = conversation_history.get(user_id, [])

    loop = asyncio.get_running_loop()
    def run_agent():
        return groq_agent.handle_request(user_input, history)

    result, updated_history = await loop.run_in_executor(executor, run_agent)
    conversation_history[user_id] = updated_history[-20:]  # keep last 20 messages

    await update.message.reply_text(str(result))


# --- Run Telegram Bot ---
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Telegram bot is running...")
app.run_polling()
