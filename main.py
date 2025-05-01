import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import threading

TOKEN = "ТВОЙ_TELEGRAM_ТОКЕН"  # ← сюда вставлен твой Telegram-токен
CMC_API_KEY = "ТВОЙ_CMC_API_КЛЮЧ"  # ← сюда вставлен твой CoinMarketCap API-ключ

app = Flask('')

@app.route('/')
def home():
    return "CryptoPulse Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

users = {}
premium_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = 'en' if update.effective_user.language_code == 'en' else 'ru'
    msg = "Welcome to CryptoPulse Bot!" if lang == 'en' else "Добро пожаловать в CryptoPulse Бот!"
    await update.message.reply_text(msg)

async def newtokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    params = {'start': '1', 'limit': '5', 'sort': 'date_added'}
    response = requests.get(url, headers=headers, params=params).json()
    tokens = response.get("data", [])
    msg = "🆕 Новые токены:\n" + "\n".join([f"{t['name']} ({t['symbol']})" for t in tokens])
    await update.message.reply_text(msg)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {'X-CMC_PRO_API_KEY': CMC_API_KEY}
    params = {'start': '1', 'limit': '5', 'sort': 'market_cap'}
    response = requests.get(url, headers=headers, params=params).json()
    coins = response.get("data", [])
    msg = "🏆 Топ-5 криптовалют:\n" + "\n".join([f"{c['name']} ({c['symbol']}): ${c['quote']['USD']['price']:.2f}" for c in coins])
    await update.message.reply_text(msg)

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(f"🤝 Твоя реферальная ссылка:\n{ref_link}")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    premium_users.add(user_id)
    await update.message.reply_text("✅ Подписка активирована!")

app_bot = ApplicationBuilder().token(TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))
app_bot.add_handler(CommandHandler("newtokens", newtokens))
app_bot.add_handler(CommandHandler("top", top))
app_bot.add_handler(CommandHandler("referral", referral))
app_bot.add_handler(CommandHandler("subscribe", subscribe))

keep_alive()
app_bot.run_polling()

