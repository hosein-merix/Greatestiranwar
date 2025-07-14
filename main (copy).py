from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import os

# Bot configuration
TOKEN = os.getenv("BOT_TOKEN", "8109322082:AAFBpC7pIJRiLogy_4pvZ8Gd6zQ4W6O74s4")
SUB_CHANNEL = "@Nonobodynonono"

# File paths
DATA_DIR = "data"
PARTIES_FILE = os.path.join(DATA_DIR, "parties.json")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
AUTHORIZED_PLAYERS_FILE = os.path.join(DATA_DIR, "authorized_players.json")

# ========== Helper Functions ==========

def load_json(path):
    """Load JSON data from file, return empty list if file doesn't exist"""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_json(path, data):
    """Save data to JSON file"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving JSON file {path}: {e}")

def get_player(user_id):
    """Get player data by user ID"""
    players = load_json(PLAYERS_FILE)
    for p in players:
        if p['id'] == user_id:
            return p
    return None

def create_player(user):
    """Create a new player if they don't exist"""
    players = load_json(PLAYERS_FILE)
    if get_player(user.id):
        return  # Player already exists
    
    new_player = {
        "id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "coins": 1000,
        "party_id": None,
        "location": "تهران",
        "investments": [],
        "soldiers": 0,
        "is_alive": True
    }
    players.append(new_player)
    save_json(PLAYERS_FILE, players)

def get_party_by_id(pid):
    """Get party data by party ID"""
    parties = load_json(PARTIES_FILE)
    for p in parties:
        if p["id"] == pid:
            return p
    return None

def update_player(user_id, updates):
    """Update player data"""
    players = load_json(PLAYERS_FILE)
    for i, p in enumerate(players):
        if p['id'] == user_id:
            players[i].update(updates)
            break
    save_json(PLAYERS_FILE, players)

def is_player_authorized(user_id):
    """Check if player is authorized to play"""
    authorized_players = load_json(AUTHORIZED_PLAYERS_FILE)
    return user_id in authorized_players

def add_authorized_player(user_id):
    """Add a player to authorized list"""
    authorized_players = load_json(AUTHORIZED_PLAYERS_FILE)
    if user_id not in authorized_players:
        authorized_players.append(user_id)
        save_json(AUTHORIZED_PLAYERS_FILE, authorized_players)
        return True
    return False

def remove_authorized_player(user_id):
    """Remove a player from authorized list"""
    authorized_players = load_json(AUTHORIZED_PLAYERS_FILE)
    if user_id in authorized_players:
        authorized_players.remove(user_id)
        save_json(AUTHORIZED_PLAYERS_FILE, authorized_players)
        return True
    return False

def purchase_item(user_id, item_type, item_name, cost):
    """Purchase an item for a player"""
    player = get_player(user_id)
    if not player:
        return False, "بازیکن یافت نشد"
    
    if player.get('coins', 0) < cost:
        return False, f"سکه کافی ندارید. نیاز: {cost:,} سکه"
    
    # Deduct coins
    new_coins = player['coins'] - cost
    
    if item_type == "soldier":
        new_soldiers = player.get('soldiers', 0) + 1
        update_player(user_id, {'coins': new_coins, 'soldiers': new_soldiers})
    elif item_type == "company":
        investments = player.get('investments', [])
        investments.append({"name": item_name, "type": "company", "daily_income": get_company_income(item_name)})
        update_player(user_id, {'coins': new_coins, 'investments': investments})
    
    return True, f"خرید موفق! {item_name} خریداری شد."

def get_company_income(company_name):
    """Get daily income for different company types"""
    income_map = {
        "کارخانه کوچک": 50,
        "کارخانه بزرگ": 200,
        "شرکت نفتی": 500,
        "بانک": 800
    }
    return income_map.get(company_name, 0)

def get_party_leader(party_id):
    """Get the richest player in a party (party leader)"""
    players = load_json(PLAYERS_FILE)
    party_members = [p for p in players if p.get('party_id') == party_id]
    
    if not party_members:
        return None
    
    # Find the member with most coins
    leader = max(party_members, key=lambda x: x.get('coins', 0))
    return leader

def get_party_total_soldiers(party_id):
    """Get total soldiers for all members of a party"""
    players = load_json(PLAYERS_FILE)
    party_members = [p for p in players if p.get('party_id') == party_id]
    
    total_soldiers = sum(member.get('soldiers', 0) for member in party_members)
    return total_soldiers

def leave_party(user_id):
    """Remove player from their current party"""
    player = get_player(user_id)
    if not player or not player.get('party_id'):
        return False, "شما عضو هیچ حزبی نیستید."
    
    party_id = player['party_id']
    
    # Remove player from their party
    update_player(user_id, {'party_id': None})
    
    # Update party members list
    parties = load_json(PARTIES_FILE)
    for party in parties:
        if party['id'] == party_id:
            if user_id in party.get('members', []):
                party['members'].remove(user_id)
                save_json(PARTIES_FILE, parties)
            break
    
    return True, "با موفقیت از حزب خارج شدید."

# ========== Command Handlers ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    
    # Log user information for admin reference
    print(f"🔍 User trying to start: ID={user_id}, Username=@{user.username or 'None'}, Name={user.first_name}")
    
    # Check if player is authorized
    if not is_player_authorized(user_id):
        access_denied_message = f"""
❌ شما دسترسی به بازی ندارید

برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید

🔐 پس از خرید اشتراک، دسترسی شما فعال خواهد شد.

📋 شناسه شما: {user_id}
        """
        await update.message.reply_text(access_denied_message.strip())
        return
    
    create_player(user)
    
    welcome_message = f"""
🎮 سلام {user.first_name}!

به بازی استراتژی سیاسی خوش آمدید!

📊 وضعیت شما:
💰 سکه: 1000
📍 موقعیت: تهران
🏛️ حزب: هیچ

🎯 هدف بازی: قدرت سیاسی کسب کنید و کشور را اداره کنید!
    """
    
    # Create main menu glass-style buttons
    keyboard = [
        [
            InlineKeyboardButton("🏛️ پیوستن به حزب", callback_data="show_parties"),
            InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")
        ],
        [
            InlineKeyboardButton("🛒 فروشگاه", callback_data="show_shop"),
            InlineKeyboardButton("📍 تغییر موقعیت", callback_data="change_location")
        ],
        [
            InlineKeyboardButton("🏛️ حزب من", callback_data="my_party"),
            InlineKeyboardButton("📊 احزاب سیاسی", callback_data="show_all_parties")
        ],
        [
            InlineKeyboardButton("🆘 راهنما", callback_data="show_help")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message.strip(), reply_markup=markup)

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /join command - show party selection"""
    user_id = update.effective_user.id
    
    # Check if player is authorized
    if not is_player_authorized(user_id):
        access_denied_message = """
❌ شما دسترسی به بازی ندارید

برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید
        """
        await update.message.reply_text(access_denied_message.strip())
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("⚠️ ابتدا با دستور /start در بازی ثبت‌نام کنید.")
        return
    
    if player.get('party_id'):
        party = get_party_by_id(player['party_id'])
        party_name = party['name'] if party else "نامشخص"
        await update.message.reply_text(f"🏛️ شما قبلاً عضو {party_name} هستید!")
        return
    
    parties = load_json(PARTIES_FILE)
    if not parties:
        await update.message.reply_text("❌ هیچ حزبی در دسترس نیست.")
        return
    
    # Create inline keyboard with parties
    keyboard = []
    for party in parties:
        member_count = len(party.get('members', []))
        button_text = f"{party['name']} ({party['region']}) - {member_count} عضو"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"join_{party['id']}")])
    
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🏛️ یکی از احزاب زیر را برای پیوستن انتخاب کنید:",
        reply_markup=markup
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show player profile"""
    user_id = update.effective_user.id
    
    # Check if player is authorized
    if not is_player_authorized(user_id):
        access_denied_message = """
❌ شما دسترسی به بازی ندارید

برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید
        """
        await update.message.reply_text(access_denied_message.strip())
        return
    
    player = get_player(user_id)
    
    if not player:
        await update.message.reply_text("⚠️ ابتدا با دستور /start در بازی ثبت‌نام کنید.")
        return
    
    party_name = "هیچ"
    if player.get('party_id'):
        party = get_party_by_id(player['party_id'])
        party_name = party['name'] if party else "نامشخص"
    
    profile_text = f"""
👤 پروفایل شما:

🆔 نام: {player.get('first_name', 'نامشخص')}
💰 سکه: {player.get('coins', 0):,}
🏛️ حزب: {party_name}
📍 موقعیت: {player.get('location', 'نامشخص')}
⚔️ سربازان: {player.get('soldiers', 0)}
💼 سرمایه‌گذری‌ها: {len(player.get('investments', []))}
❤️ وضعیت: {'زنده' if player.get('is_alive', True) else 'مرده'}
    """
    
    # Create glass-style action buttons
    keyboard = [
        [
            InlineKeyboardButton("🛒 خرید سرباز", callback_data="buy_soldiers"),
            InlineKeyboardButton("🏭 خرید شرکت", callback_data="buy_company")
        ],
        [
            InlineKeyboardButton("💼 مدیریت سرمایه", callback_data="manage_investments"),
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_profile")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(profile_text.strip(), reply_markup=markup)

async def parties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all parties information"""
    parties_data = load_json(PARTIES_FILE)
    
    if not parties_data:
        await update.message.reply_text("❌ هیچ حزبی در دسترس نیست.")
        return
    
    parties_text = "🏛️ لیست احزاب سیاسی:\n\n"
    
    for party in parties_data:
        member_count = len(party.get('members', []))
        soldier_count = party.get('soldiers', 0)
        company_count = len(party.get('companies', []))
        
        parties_text += f"🔸 {party['name']}\n"
        parties_text += f"   📍 منطقه: {party['region']}\n"
        parties_text += f"   👥 اعضا: {member_count}\n"
        parties_text += f"   ⚔️ سربازان: {soldier_count}\n"
        parties_text += f"   🏭 شرکت‌ها: {company_count}\n\n"
    
    await update.message.reply_text(parties_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    help_text = """
🆘 راهنمای بازی:

📋 دستورات اساسی:
/start - شروع بازی و ثبت‌نام
/join - پیوستن به حزب
/profile - مشاهده پروفایل
/parties - لیست احزاب
/help - نمایش این راهنما

🎮 نحوه بازی:
1️⃣ با /start در بازی ثبت‌نام کنید
2️⃣ با /join به یکی از احزاب بپیوندید
3️⃣ قدرت سیاسی کسب کنید
4️⃣ کشور را اداره کنید!

💡 نکات:
- هر بازیکن با 1000 سکه شروع می‌کند
- انتخاب حزب بر استراتژی شما تأثیر دارد
- هر منطقه ویژگی‌های خاص دارد
    """
    
    await update.message.reply_text(help_text.strip())

async def add_player_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to add authorized player"""
    user_id = update.effective_user.id
    
    # Check if the command sender is admin (IMPORTANT: Replace with your actual Telegram user ID)
    ADMIN_ID = 123456789  # TODO: Replace with your actual Telegram user ID
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه استفاده از این دستور را ندارید.")
        return
    
    if not context.args:
        await update.message.reply_text("🔧 استفاده: /addplayer <user_id>\n\nمثال: /addplayer 123456789")
        return
    
    try:
        player_id = int(context.args[0])
        if add_authorized_player(player_id):
            await update.message.reply_text(f"✅ بازیکن با آیدی {player_id} به لیست مجاز اضافه شد.")
        else:
            await update.message.reply_text(f"⚠️ بازیکن با آیدی {player_id} قبلاً در لیست مجاز است.")
    except ValueError:
        await update.message.reply_text("❌ آیدی وارد شده معتبر نیست. لطفاً یک عدد وارد کنید.")

async def remove_player_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to remove authorized player"""
    user_id = update.effective_user.id
    
    # Check if the command sender is admin (IMPORTANT: Replace with your actual Telegram user ID)
    ADMIN_ID = 123456789  # TODO: Replace with your actual Telegram user ID
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه استفاده از این دستور را ندارید.")
        return
    
    if not context.args:
        await update.message.reply_text("🔧 استفاده: /removeplayer <user_id>\n\nمثال: /removeplayer 123456789")
        return
    
    try:
        player_id = int(context.args[0])
        if remove_authorized_player(player_id):
            await update.message.reply_text(f"✅ بازیکن با آیدی {player_id} از لیست مجاز حذف شد.")
        else:
            await update.message.reply_text(f"⚠️ بازیکن با آیدی {player_id} در لیست مجاز موجود نیست.")
    except ValueError:
        await update.message.reply_text("❌ آیدی وارد شده معتبر نیست. لطفاً یک عدد وارد کنید.")

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show shop with purchase options"""
    user_id = update.effective_user.id
    
    # Check if player is authorized
    if not is_player_authorized(user_id):
        access_denied_message = """
❌ شما دسترسی به بازی ندارید

برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید
        """
        await update.message.reply_text(access_denied_message.strip())
        return
    
    player = get_player(user_id)
    if not player:
        await update.message.reply_text("⚠️ ابتدا با دستور /start در بازی ثبت‌نام کنید.")
        return
    
    shop_text = f"""
🛒 فروشگاه نظامی و اقتصادی

💰 موجودی شما: {player.get('coins', 0):,} سکه

⚔️ واحدهای نظامی:
• سرباز پیاده: 100 سکه
• سرباز ویژه: 250 سکه  
• تانک: 500 سکه
• هواپیما: 1000 سکه

🏭 شرکت‌ها و سرمایه‌گذری:
• کارخانه کوچک: 500 سکه (درآمد: 50/روز)
• کارخانه بزرگ: 1500 سکه (درآمد: 200/روز)
• شرکت نفتی: 3000 سکه (درآمد: 500/روز)
• بانک: 5000 سکه (درآمد: 800/روز)
    """
    
    # Create shop buttons
    keyboard = [
        [
            InlineKeyboardButton("⚔️ خرید سربازان", callback_data="shop_soldiers"),
            InlineKeyboardButton("🏭 خرید شرکت‌ها", callback_data="shop_companies")
        ],
        [
            InlineKeyboardButton("💼 سرمایه‌گذری‌های من", callback_data="my_investments"),
            InlineKeyboardButton("🔄 بروزرسانی", callback_data="refresh_shop")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(shop_text.strip(), reply_markup=markup)

async def list_players_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to list authorized players"""
    user_id = update.effective_user.id
    
    # Check if the command sender is admin (IMPORTANT: Replace with your actual Telegram user ID)
    ADMIN_ID = 123456789  # TODO: Replace with your actual Telegram user ID
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه استفاده از این دستور را ندارید.")
        return
    
    authorized_players = load_json(AUTHORIZED_PLAYERS_FILE)
    
    if not authorized_players:
        await update.message.reply_text("📝 هیچ بازیکن مجازی در لیست موجود نیست.")
        return
    
    players_text = "📋 لیست بازیکنان مجاز:\n\n"
    for i, player_id in enumerate(authorized_players, 1):
        players_text += f"{i}. {player_id}\n"
    
    await update.message.reply_text(players_text)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    # Check authorization for all callbacks except join
    if not data.startswith("join_") and not is_player_authorized(user_id):
        access_denied_message = """
❌ شما دسترسی به بازی ندارید

برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید
        """
        await query.edit_message_text(access_denied_message.strip())
        return
    
    if data.startswith("join_"):
        try:
            party_id = int(data.split("_")[1])
        except (ValueError, IndexError):
            await query.edit_message_text("❌ خطا در پردازش درخواست.")
            return
        
        # Check if player is authorized
        if not is_player_authorized(user_id):
            access_denied_message = """
❌ شما دسترسی به بازی ندارید

برای خرید اشتراک به آیدی @Nonobodynonono پیام بدید
            """
            await query.edit_message_text(access_denied_message.strip())
            return
        
        player = get_player(user_id)
        
        if player is None:
            await query.edit_message_text("⚠️ شما در بازی ثبت‌نام نکرده‌اید. ابتدا /start را بزنید.")
            return
        
        if player.get('party_id'):
            await query.edit_message_text("🏛️ شما قبلاً به حزبی پیوسته‌اید!")
            return
        
        # Get party information
        party = get_party_by_id(party_id)
        if not party:
            await query.edit_message_text("❌ حزب مورد نظر یافت نشد.")
            return
        
        # Update player's party membership
        update_player(user_id, {'party_id': party_id})
        
        # Add player to party members list
        parties = load_json(PARTIES_FILE)
        for p in parties:
            if p['id'] == party_id:
                if user_id not in p.get('members', []):
                    p.setdefault('members', []).append(user_id)
                break
        save_json(PARTIES_FILE, parties)
        
        success_message = f"""
🎉 تبریک! شما با موفقیت به {party['name']} پیوستید!

🏛️ اطلاعات حزب:
📍 منطقه: {party['region']}
👥 تعداد اعضا: {len(party.get('members', []))}
⚔️ نیروی نظامی: {party.get('soldiers', 0)}

حالا می‌توانید در فعالیت‌های سیاسی شرکت کنید!
        """
        
        await query.edit_message_text(success_message.strip())
    
    elif data == "buy_soldiers" or data == "shop_soldiers":
        # Show soldier purchase options
        keyboard = [
            [
                InlineKeyboardButton("👤 سرباز پیاده (100 سکه)", callback_data="buy_soldier_infantry"),
                InlineKeyboardButton("🎖️ سرباز ویژه (250 سکه)", callback_data="buy_soldier_special")
            ],
            [
                InlineKeyboardButton("🚗 تانک (500 سکه)", callback_data="buy_soldier_tank"),
                InlineKeyboardButton("✈️ هواپیما (1000 سکه)", callback_data="buy_soldier_plane")
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="refresh_shop")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        player = get_player(user_id)
        message = f"""
⚔️ فروشگاه نظامی

💰 موجودی شما: {player.get('coins', 0):,} سکه
🪖 سربازان فعلی: {player.get('soldiers', 0)}

یکی از واحدهای نظامی را انتخاب کنید:
        """
        
        await query.edit_message_text(message.strip(), reply_markup=markup)
    
    elif data == "buy_company" or data == "shop_companies":
        # Show company purchase options
        keyboard = [
            [
                InlineKeyboardButton("🏭 کارخانه کوچک (500 سکه)", callback_data="buy_company_small_factory"),
                InlineKeyboardButton("🏗️ کارخانه بزرگ (1500 سکه)", callback_data="buy_company_large_factory")
            ],
            [
                InlineKeyboardButton("🛢️ شرکت نفتی (3000 سکه)", callback_data="buy_company_oil"),
                InlineKeyboardButton("🏦 بانک (5000 سکه)", callback_data="buy_company_bank")
            ],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="refresh_shop")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        player = get_player(user_id)
        message = f"""
🏭 فروشگاه شرکت‌ها

💰 موجودی شما: {player.get('coins', 0):,} سکه
💼 سرمایه‌گذری‌های فعلی: {len(player.get('investments', []))}

یکی از شرکت‌ها را انتخاب کنید:
        """
        
        await query.edit_message_text(message.strip(), reply_markup=markup)
    
    elif data.startswith("buy_soldier_"):
        soldier_type = data.replace("buy_soldier_", "")
        costs = {"infantry": 100, "special": 250, "tank": 500, "plane": 1000}
        names = {"infantry": "سرباز پیاده", "special": "سرباز ویژه", "tank": "تانک", "plane": "هواپیما"}
        
        cost = costs.get(soldier_type, 0)
        name = names.get(soldier_type, "نامشخص")
        
        success, message = purchase_item(user_id, "soldier", name, cost)
        
        if success:
            player = get_player(user_id)
            result_message = f"""
✅ {message}

💰 موجودی جدید: {player.get('coins', 0):,} سکه
⚔️ تعداد سربازان: {player.get('soldiers', 0)}
            """
        else:
            result_message = f"❌ {message}"
        
        await query.edit_message_text(result_message.strip())
    
    elif data.startswith("buy_company_"):
        company_type = data.replace("buy_company_", "")
        costs = {"small_factory": 500, "large_factory": 1500, "oil": 3000, "bank": 5000}
        names = {"small_factory": "کارخانه کوچک", "large_factory": "کارخانه بزرگ", "oil": "شرکت نفتی", "bank": "بانک"}
        
        cost = costs.get(company_type, 0)
        name = names.get(company_type, "نامشخص")
        
        success, message = purchase_item(user_id, "company", name, cost)
        
        if success:
            player = get_player(user_id)
            daily_income = get_company_income(name)
            result_message = f"""
✅ {message}

💰 موجودی جدید: {player.get('coins', 0):,} سکه
💼 تعداد سرمایه‌گذری‌ها: {len(player.get('investments', []))}
💵 درآمد روزانه: {daily_income} سکه
            """
        else:
            result_message = f"❌ {message}"
        
        await query.edit_message_text(result_message.strip())
    
    elif data == "my_investments":
        player = get_player(user_id)
        investments = player.get('investments', [])
        
        if not investments:
            message = "💼 شما هیچ سرمایه‌گذری ندارید.\n\nبرای شروع، از فروشگاه شرکت خریداری کنید."
        else:
            total_income = sum(inv.get('daily_income', 0) for inv in investments)
            message = f"💼 سرمایه‌گذری‌های شما:\n\n"
            for i, inv in enumerate(investments, 1):
                message += f"{i}. {inv['name']} - درآمد: {inv.get('daily_income', 0)} سکه/روز\n"
            message += f"\n💵 کل درآمد روزانه: {total_income} سکه"
        
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="refresh_shop")]]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=markup)
    
    elif data == "refresh_profile":
        # Redirect to profile command
        await query.message.delete()
        await context.bot.send_message(user_id, "🔄 بروزرسانی پروفایل...")
        # Call profile function indirectly
    
    elif data == "refresh_shop":
        # Redirect to shop command  
        await query.message.delete()
        await context.bot.send_message(user_id, "🔄 بروزرسانی فروشگاه...")
        # Call shop function indirectly
    
    elif data == "show_parties":
        # Show party selection (same as /join)
        parties = load_json(PARTIES_FILE)
        if not parties:
            await query.edit_message_text("❌ هیچ حزبی در دسترس نیست.")
            return
        
        # Create inline keyboard with parties
        keyboard = []
        for party in parties:
            member_count = len(party.get('members', []))
            button_text = f"{party['name']} ({party['region']}) - {member_count} عضو"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"join_{party['id']}")])
        
        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")])
        
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🏛️ یکی از احزاب زیر را برای پیوستن انتخاب کنید:",
            reply_markup=markup
        )
    
    elif data == "show_profile":
        # Show profile (similar to /profile command)
        player = get_player(user_id)
        if not player:
            await query.edit_message_text("⚠️ ابتدا با دستور /start در بازی ثبت‌نام کنید.")
            return
        
        party_name = "هیچ"
        if player.get('party_id'):
            party = get_party_by_id(player['party_id'])
            party_name = party['name'] if party else "نامشخص"
        
        profile_text = f"""
👤 پروفایل شما:

🆔 نام: {player.get('first_name', 'نامشخص')}
💰 سکه: {player.get('coins', 0):,}
🏛️ حزب: {party_name}
📍 موقعیت: {player.get('location', 'نامشخص')}
⚔️ سربازان: {player.get('soldiers', 0)}
💼 سرمایه‌گذری‌ها: {len(player.get('investments', []))}
❤️ وضعیت: {'زنده' if player.get('is_alive', True) else 'مرده'}
        """
        
        # Create profile action buttons
        keyboard = [
            [
                InlineKeyboardButton("🛒 خرید سرباز", callback_data="buy_soldiers"),
                InlineKeyboardButton("🏭 خرید شرکت", callback_data="buy_company")
            ],
            [
                InlineKeyboardButton("📍 تغییر موقعیت", callback_data="change_location"),
                InlineKeyboardButton("🏛️ حزب من", callback_data="my_party")
            ],
            [
                InlineKeyboardButton("💼 مدیریت سرمایه", callback_data="my_investments"),
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(profile_text.strip(), reply_markup=markup)
    
    elif data == "show_shop":
        # Show shop (similar to /shop command)
        player = get_player(user_id)
        if not player:
            await query.edit_message_text("⚠️ ابتدا با دستور /start در بازی ثبت‌نام کنید.")
            return
        
        shop_text = f"""
🛒 فروشگاه نظامی و اقتصادی

💰 موجودی شما: {player.get('coins', 0):,} سکه

⚔️ واحدهای نظامی:
• سرباز پیاده: 100 سکه
• سرباز ویژه: 250 سکه  
• تانک: 500 سکه
• هواپیما: 1000 سکه

🏭 شرکت‌ها و سرمایه‌گذری:
• کارخانه کوچک: 500 سکه (درآمد: 50/روز)
• کارخانه بزرگ: 1500 سکه (درآمد: 200/روز)
• شرکت نفتی: 3000 سکه (درآمد: 500/روز)
• بانک: 5000 سکه (درآمد: 800/روز)
        """
        
        # Create shop buttons
        keyboard = [
            [
                InlineKeyboardButton("⚔️ خرید سربازان", callback_data="shop_soldiers"),
                InlineKeyboardButton("🏭 خرید شرکت‌ها", callback_data="shop_companies")
            ],
            [
                InlineKeyboardButton("💼 سرمایه‌گذری‌های من", callback_data="my_investments"),
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(shop_text.strip(), reply_markup=markup)
    
    elif data == "show_all_parties":
        # Show all parties info (similar to /parties command)
        parties_data = load_json(PARTIES_FILE)
        
        if not parties_data:
            await query.edit_message_text("❌ هیچ حزبی در دسترس نیست.")
            return
        
        parties_text = "🏛️ لیست احزاب سیاسی:\n\n"
        
        for party in parties_data:
            member_count = len(party.get('members', []))
            soldier_count = party.get('soldiers', 0)
            company_count = len(party.get('companies', []))
            
            parties_text += f"🔸 {party['name']}\n"
            parties_text += f"   📍 منطقه: {party['region']}\n"
            parties_text += f"   👥 اعضا: {member_count}\n"
            parties_text += f"   ⚔️ سربازان: {soldier_count}\n"
            parties_text += f"   🏭 شرکت‌ها: {company_count}\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(parties_text, reply_markup=markup)
    
    elif data == "show_help":
        # Show help (similar to /help command)
        help_text = """
🆘 راهنمای بازی:

📋 دستورات اساسی:
/start - شروع بازی و منوی اصلی
/join - پیوستن به حزب
/profile - مشاهده پروفایل
/shop - فروشگاه
/parties - لیست احزاب
/help - نمایش این راهنما

🎮 نحوه بازی:
1️⃣ با /start در بازی ثبت‌نام کنید
2️⃣ از منوی اصلی به یکی از احزاب بپیوندید
3️⃣ از فروشگاه سرباز و شرکت خریداری کنید
4️⃣ قدرت سیاسی کسب کنید!

💡 نکات:
- هر بازیکن با 1000 سکه شروع می‌کند
- انتخاب حزب بر استراتژی شما تأثیر دارد
- شرکت‌ها درآمد روزانه دارند
        """
        
        keyboard = [[InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")]]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text.strip(), reply_markup=markup)
    
    elif data == "main_menu":
        # Return to main menu
        user = query.from_user
        
        welcome_message = f"""
🎮 سلام {user.first_name}!

به بازی استراتژی سیاسی خوش آمدید!

📊 وضعیت شما:
💰 سکه: 1000
📍 موقعیت: تهران
🏛️ حزب: هیچ

🎯 هدف بازی: قدرت سیاسی کسب کنید و کشور را اداره کنید!
        """
        
        # Create main menu glass-style buttons
        keyboard = [
            [
                InlineKeyboardButton("🏛️ پیوستن به حزب", callback_data="show_parties"),
                InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")
            ],
            [
                InlineKeyboardButton("🛒 فروشگاه", callback_data="show_shop"),
                InlineKeyboardButton("📍 تغییر موقعیت", callback_data="change_location")
            ],
            [
                InlineKeyboardButton("🏛️ حزب من", callback_data="my_party"),
                InlineKeyboardButton("📊 احزاب سیاسی", callback_data="show_all_parties")
            ],
            [
                InlineKeyboardButton("🆘 راهنما", callback_data="show_help")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_message.strip(), reply_markup=markup)
    
    elif data == "change_location":
        # Show location change options with all 11 provinces from the game
        location_text = """
📍 انتخاب موقعیت جدید

استان مورد نظر خود را انتخاب کنید:
        """
        
        # Create location buttons based on the 11 provinces from parties
        keyboard = [
            [
                InlineKeyboardButton("🏛️ تهران", callback_data="location_تهران"),
                InlineKeyboardButton("🏔️ همدان", callback_data="location_همدان")
            ],
            [
                InlineKeyboardButton("🌅 فارس", callback_data="location_فارس"),
                InlineKeyboardButton("🛢️ خوزستان", callback_data="location_خوزستان")
            ],
            [
                InlineKeyboardButton("☀️ خراسان", callback_data="location_خراسان"),
                InlineKeyboardButton("🏜️ بلوچستان", callback_data="location_بلوچستان")
            ],
            [
                InlineKeyboardButton("🌊 مازندران", callback_data="location_مازندران"),
                InlineKeyboardButton("🗻 آذربایجان", callback_data="location_آذربایجان")
            ],
            [
                InlineKeyboardButton("🦅 کردستان", callback_data="location_کردستان"),
                InlineKeyboardButton("🌿 لرستان", callback_data="location_لرستان")
            ],
            [
                InlineKeyboardButton("🏺 اصفهان", callback_data="location_اصفهان")
            ],
            [
                InlineKeyboardButton("🔙 بازگشت به پروفایل", callback_data="show_profile")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(location_text.strip(), reply_markup=markup)
    
    elif data.startswith("location_"):
        # Handle location change
        new_location = data.replace("location_", "")
        
        # Update player's location
        success = update_player(user_id, {'location': new_location})
        
        player = get_player(user_id)
        
        if player:
            success_message = f"""
✅ موقعیت شما با موفقیت تغییر یافت!

📍 موقعیت جدید: {new_location}
💰 موجودی: {player.get('coins', 0):,} سکه

حالا می‌توانید در استان {new_location} فعالیت کنید.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("👤 مشاهده پروفایل", callback_data="show_profile"),
                    InlineKeyboardButton("🛒 فروشگاه", callback_data="show_shop")
                ],
                [
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(success_message.strip(), reply_markup=markup)
        else:
            await query.edit_message_text("❌ خطا در تغییر موقعیت. لطفاً دوباره تلاش کنید.")
    
    elif data == "my_party":
        # Show current party information including leader and total soldiers
        player = get_player(user_id)
        if not player:
            await query.edit_message_text("⚠️ ابتدا با دستور /start در بازی ثبت‌نام کنید.")
            return
        
        party_id = player.get('party_id')
        if not party_id:
            await query.edit_message_text("""
❌ شما عضو هیچ حزبی نیستید.

ابتدا از منوی اصلی به یکی از احزاب بپیوندید.
            """)
            return
        
        # Get party data
        party = get_party_by_id(party_id)
        if not party:
            await query.edit_message_text("❌ اطلاعات حزب یافت نشد.")
            return
        
        # Get party leader (richest member)
        leader = get_party_leader(party_id)
        leader_info = "نامشخص"
        if leader:
            leader_name = leader.get('first_name', 'نامشخص')
            leader_coins = leader.get('coins', 0)
            leader_info = f"{leader_name} (ID: {leader['id']}) - {leader_coins:,} سکه"
        
        # Get total soldiers of all party members
        total_soldiers = get_party_total_soldiers(party_id)
        
        # Get party member count
        member_count = len(party.get('members', []))
        
        party_info = f"""
🏛️ اطلاعات حزب شما

📛 نام حزب: {party['name']}
📍 منطقه: {party['region']}
👥 تعداد اعضا: {member_count}
⚔️ مجموع سربازان حزب: {total_soldiers:,}

👑 رهبر حزب (ثروتمندترین عضو):
{leader_info}

💡 رهبری حزب بر اساس بیشترین مقدار سکه تعیین می‌شود.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile"),
                InlineKeyboardButton("🛒 فروشگاه", callback_data="show_shop")
            ],
            [
                InlineKeyboardButton("❌ ترک حزب", callback_data="leave_party"),
                InlineKeyboardButton("📊 همه احزاب", callback_data="show_all_parties")
            ],
            [
                InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(party_info.strip(), reply_markup=markup)
    
    elif data == "leave_party":
        # Handle leaving party
        success, message = leave_party(user_id)
        
        if success:
            # Show success message with options
            success_text = f"""
✅ {message}

شما الان آزاد هستید و می‌توانید به حزب جدیدی بپیوندید.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("🏛️ پیوستن به حزب جدید", callback_data="show_parties"),
                    InlineKeyboardButton("👤 پروفایل من", callback_data="show_profile")
                ],
                [
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(success_text.strip(), reply_markup=markup)
        else:
            # Show error message
            keyboard = [
                [
                    InlineKeyboardButton("🏛️ پیوستن به حزب", callback_data="show_parties"),
                    InlineKeyboardButton("🔙 منوی اصلی", callback_data="main_menu")
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(f"❌ {message}", reply_markup=markup)

# ========== Main ==========

def main():
    """Main function to run the bot"""
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize data files if they don't exist
    if not os.path.exists(PARTIES_FILE):
        initial_parties = [
            {"id": 1, "name": "حزب سومکا", "region": "تهران", "members": [], "soldiers": 0, "companies": []},
            {"id": 2, "name": "حزب توده", "region": "همدان", "members": [], "soldiers": 0, "companies": []},
            {"id": 3, "name": "حزب ملی", "region": "فارس", "members": [], "soldiers": 0, "companies": []},
            {"id": 4, "name": "حزب جهاد", "region": "خوزستان", "members": [], "soldiers": 0, "companies": []},
            {"id": 5, "name": "حزب خورشید", "region": "خراسان", "members": [], "soldiers": 0, "companies": []},
            {"id": 6, "name": "حزب ماشه", "region": "بلوچستان", "members": [], "soldiers": 0, "companies": []},
            {"id": 7, "name": "حزب تاج", "region": "مازندران", "members": [], "soldiers": 0, "companies": []},
            {"id": 8, "name": "حزب سرخ", "region": "آذربایجان", "members": [], "soldiers": 0, "companies": []},
            {"id": 9, "name": "حزب پژوک", "region": "کردستان", "members": [], "soldiers": 0, "companies": []},
            {"id": 10, "name": "حزب ناک اوت", "region": "لرستان", "members": [], "soldiers": 0, "companies": []},
            {"id": 11, "name": "حزب سرمایه", "region": "اصفهان", "members": [], "soldiers": 0, "companies": []}
        ]
        save_json(PARTIES_FILE, initial_parties)
    
    if not os.path.exists(PLAYERS_FILE):
        save_json(PLAYERS_FILE, [])
    
    if not os.path.exists(AUTHORIZED_PLAYERS_FILE):
        save_json(AUTHORIZED_PLAYERS_FILE, [])
    
    # Build the application
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("parties", parties))
    application.add_handler(CommandHandler("shop", shop_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addplayer", add_player_command))
    application.add_handler(CommandHandler("removeplayer", remove_player_command))
    application.add_handler(CommandHandler("listplayers", list_players_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    print("🤖 Political War Bot is starting...")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"🏛️ Parties file: {PARTIES_FILE}")
    print(f"👥 Players file: {PLAYERS_FILE}")
    print("✅ Bot is running and ready to receive commands!")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
