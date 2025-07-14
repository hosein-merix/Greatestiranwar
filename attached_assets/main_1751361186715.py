political_war_bot/main.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes import json import os

TOKEN = "8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4" SUB_CHANNEL = "@Nonobodynonono"

DATA_DIR = "data" PARTIES_FILE = os.path.join(DATA_DIR, "parties.json") PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")

========== Helper Functions ==========

def load_json(path): if not os.path.exists(path): return [] with open(path, "r", encoding="utf-8") as f: return json.load(f)

def save_json(path, data): with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def get_player(user_id): players = load_json(PLAYERS_FILE) for p in players: if p['id'] == user_id: return p return None

def create_player(user): players = load_json(PLAYERS_FILE) if get_player(user.id): return new_player = { "id": user.id, "coins": 1000, "party_id": None, "location": "تهران", "investments": [], "soldiers": 0, "is_alive": True } players.append(new_player) save_json(PLAYERS_FILE, players)

def get_party_by_id(pid): parties = load_json(PARTIES_FILE) for p in parties: if p["id"] == pid: return p return None

========== Command Handlers ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): user = update.effective_user create_player(user) await update.message.reply_text(f"سلام {user.first_name}!\nبرای شروع بازی یکی از احزاب را انتخاب کن با دستور /join")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE): parties = load_json(PARTIES_FILE) keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"join_{p['id']}")] for p in parties] markup = InlineKeyboardMarkup(keyboard) await update.message.reply_text("یکی از احزاب زیر را انتخاب کن:", reply_markup=markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query await query.answer() data = query.data

if data.startswith("join_"):
    party_id = int(data.split("_")[1])
    user_id = query.from_user.id

    player = get_player(user_id)
    if player is None:
        return await query.edit_message_text("شما در بازی ثبت نام نکرده‌اید. ابتدا /start را بزنید.")

    if player['party_id']:
        return await query.edit_message_text("شما قبلاً به حزبی پیوسته‌اید!")

    # عضویت در حزب
    player['party_id'] = party_id
    players = load_json(PLAYERS_FILE)
    for p in players:
        if p['id'] == user_id:
            p['party_id'] = party_id
            break
    save_json(PLAYERS_FILE, players)

    # افزودن به لیست اعضای حزب
    parties = load_json(PARTIES_FILE)
    for party in parties:
        if party['id'] == party_id:
            if user_id not in party['members']:
                party['members'].append(user_id)
            break
    save_json(PARTIES_FILE, parties)

    party_name = get_party_by_id(party_id)['name']
    await query.edit_message_text(f"🎉 شما با موفقیت به {party_name} پیوستید!")

========== Main ==========

if name == 'main': os.makedirs(DATA_DIR, exist_ok=True)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("join", join))
app.add_handler(CallbackQueryHandler(handle_callback))

print("Bot is running...")
app.run_polling()

