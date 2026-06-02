from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from datetime import datetime
import random
import os

TOKEN = "YOUR_TOKEN_HERE"

USERS_FILE = "TelegramBot/data/users.txt"
ADMIN_ID = 123456789


# ---------------- USER SYSTEM ----------------

def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()

    with open(USERS_FILE, "r") as file:
        users = file.read().splitlines()

    if str(user_id) not in users:
        with open(USERS_FILE, "a") as file:
            file.write(f"{user_id}\n")


def get_users():
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r") as file:
        return file.read().splitlines()


def count_users():
    return len(get_users())


# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    save_user(update.effective_user.id)

    keyboard = [
        ["Help", "Time"],
        ["About", "Users"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Welcome to Kcodes Utility Bot!",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Commands:\n\n"
        "/start\n"
        "/help\n"
        "/time\n"
        "/echo <message>\n"
        "/about\n"
        "/users\n"
        "/random\n"
        "/calc <expression>\n"
        "/broadcast <message> (Admin)"
    )


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(
        f"🕒 Current Time: {now}"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Kcodes Utility Bot\n\n"
        "Built with Python and Telegram Bot API."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        await update.message.reply_text(" ".join(context.args))
    else:
        await update.message.reply_text(
            "Usage:\n/echo Hello World"
        )


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = count_users()

    await update.message.reply_text(
        f"👥 Total Users: {total}"
    )


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)

    await update.message.reply_text(
        f"🎲 Your random number is: {number}"
    )


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/calc 25+15"
        )
        return

    try:
        expression = "".join(context.args)

        result = eval(expression)

        await update.message.reply_text(
            f"🧮 Result: {result}"
        )

    except:
        await update.message.reply_text(
            "❌ Invalid calculation."
        )


# ---------------- BROADCAST ----------------

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ You are not authorized."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/broadcast Hello Everyone"
        )
        return

    message = " ".join(context.args)

    users = get_users()

    sent = 0

    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 {message}"
            )
            sent += 1

        except:
            pass

    await update.message.reply_text(
        f"✅ Broadcast sent to {sent} users."
    )


# ---------------- BUTTONS ----------------

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "Help":
        await help_command(update, context)

    elif text == "Time":
        await time_command(update, context)

    elif text == "About":
        await about(update, context)

    elif text == "Users":
        await users(update, context)


# ---------------- APP ----------------

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("time", time_command))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(CommandHandler("about", about))
app.add_handler(CommandHandler("users", users))
app.add_handler(CommandHandler("random", random_command))
app.add_handler(CommandHandler("calc", calc))
app.add_handler(CommandHandler("broadcast", broadcast))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, buttons)
)

print("🤖 Bot is running...")
app.run_polling(drop_pending_updates=True)