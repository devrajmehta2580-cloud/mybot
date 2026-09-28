import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8770186204:AAFA2Blfh5mle0d9gQerStrVK0I0UCXPFKw'
ZAPUPI_API_KEY = 'zapc81b73d4f8e5244de8e7c105fa5b397c'

bot = telebot.TeleBot(API_TOKEN)
user_balances = {}
user_input_amounts = {}

def get_main_menu(user_id, name):
    balance = user_balances.get(user_id, 0)
    text = (
        "👑 —— DEVRAJ MEHTA CORE —— 👑\n\n"
        f"👋 Hello, {name}!\n\n"
        "🔑 Premium Game Keys Only\n"
        "⚡ Instant Key Delivery\n"
        "🛡 Secure & Trusted\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User ID: {user_id}\n"
        f"💰 Wallet Balance: ₹{balance}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Tap any button below to begin."
    )
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🛒 Shop", callback_data="shop"))
    markup.add(InlineKeyboardButton("💰 Add Balance", callback_data="add_balance_input"),
               InlineKeyboardButton("📋 My Orders", callback_data="orders"))
    markup.add(InlineKeyboardButton("📢 Support", url="https://t.me"))
    return text, markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 0
    text, markup = get_main_menu(user_id, message.from_user.first_name)
    bot.send_message(message.chat.id, text, reply_markup=markup)

def get_keypad_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(str(i), callback_data=f"num_{i}") for i in range(1, 10)]
    markup.add(*buttons)
    markup.add(
        InlineKeyboardButton("❌ Delete", callback_data="num_del"),
        InlineKeyboardButton("0", callback_data="num_0"),
        InlineKeyboardButton("✅ Confirm", callback_data="num_confirm")
    )
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="main_menu"))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    
    if call.data == "add_balance_input":
        user_input_amounts[user_id] = "0"
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="💰 **Custom Amount**\n\nMethod: 💳 UPI (ZapUPI)\n‼️ Min: ₹10 | Max: ₹5,000\n\n⬇️ Amount: ₹0\n\n⬇️ Amount type karo — buttons se:",
            reply_markup=get_keypad_markup(), parse_mode="Markdown"
        )
        
    elif call.data.startswith("num_"):
        action = call.data.split("_")[-1]
        current = user_input_amounts.get(user_id, "0")
        
        if action == "del":
            current = current[:-1] if len(current) > 1 else "0"
        elif action == "confirm":
            amount = int(current)
            if amount < 10 or amount > 5000:
                bot.answer_callback_query(call.id, "❌ Amount ₹10 se ₹5000 ke beech hona chahiye!", show_alert=True)
                return
            
            payment_url = f"https://zapupi.com{ZAPUPI_API_KEY}&amount={amount}&order_id=DEV{call.id}&p_info=Wallet"
            
            pay_markup = InlineKeyboardMarkup(row_width=1)
            pay_markup.add(
                InlineKeyboardButton("🔗 Pay Now", url=payment_url),
                InlineKeyboardButton("❌ Cancel Payment", callback_data="main_menu")
            )
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=f"💳 **Pay ₹{amount}**\n\n1️⃣ Neeche **Pay Now** button dabao\n2️⃣ Payment complete karo\n3️⃣ Balance automatic wallet me add ho jaayega.",
                reply_markup=pay_markup, parse_mode="Markdown"
            )
            return
        else:
            current = action if current == "0" else current + action
                
        user_input_amounts[user_id] = current
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=f"💰 **Custom Amount**\n\nMethod: 💳 UPI (ZapUPI)\n‼️ Min: ₹10 | Max: ₹5,000\n\n⬇️ Amount: ₹{current}\n\n⬇️ Amount type karo — buttons se:",
            reply_markup=get_keypad_markup(), parse_mode="Markdown"
        )
        
    elif call.data == "main_menu":
        text, markup = get_main_menu(user_id, call.from_user.first_name)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup)

bot.remove_webhook()
bot.infinity_polling()
