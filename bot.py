import telebot
import schedule
import time
from datetime import datetime

# ================== SETTINGS ==================
TOKEN = "8447153057:AAFjMgH5HNjN19rSWm1vMLuF-pF2ni_G0z8"
CHANNEL_ID = "@vibeymusic"
SEND_HOUR = "17:00"  # ساعت ارسال روزانه
# ============================================

bot = telebot.TeleBot(TOKEN)

# ---------------- Song list in memory -----------------
song_links = []

# ---------------- Handlers -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_list = telebot.types.KeyboardButton("📋 نمایش آهنگ‌ها")
    keyboard.add(btn_list)
    bot.send_message(
        message.chat.id,
        "سلام! خوش آمدید 😊\nربات آماده ارسال آهنگ‌ها است.\nبرای اضافه کردن آهنگ، دستور /addsong را ارسال کنید.",
        reply_markup=keyboard
    )

# ---------------- Add song -----------------
@bot.message_handler(commands=['addsong'])
def ask_for_song(message):
    msg = bot.send_message(message.chat.id, "لطفاً لینک آهنگ با پسوند .mp3 را ارسال کنید:")
    bot.register_next_step_handler(msg, add_song_to_list)

def add_song_to_list(message):
    link = message.text.strip()
    if link.lower().endswith(".mp3"):
        song_links.append(link)
        bot.reply_to(message, f"✅ آهنگ با موفقیت اضافه شد!\nتعداد آهنگ‌ها در لیست: {len(song_links)}")
        print(f"[LOG] Added new song: {link}")
        # لغو مرحله بعد از اضافه کردن
        bot.clear_step_handler_by_chat_id(message.chat.id)
    else:
        bot.reply_to(message, "❌ لینک اشتباه است! حتماً باید پسوند .mp3 داشته باشد.")
        msg = bot.send_message(message.chat.id, "لطفاً دوباره لینک آهنگ را ارسال کنید:")
        bot.register_next_step_handler(msg, add_song_to_list)

# ---------------- Remove song -----------------
@bot.message_handler(commands=['removesong'])
def ask_remove_song(message):
    if not song_links:
        bot.send_message(message.chat.id, "❌ لیست آهنگ‌ها خالی است. هیچ چیزی برای حذف وجود ندارد.")
        return
    text = "🎵 لیست آهنگ‌ها:\n\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(song_links)])
    bot.send_message(message.chat.id, text)
    msg = bot.send_message(message.chat.id, "لطفاً شماره آهنگی که می‌خواهید حذف شود را وارد کنید:")
    bot.register_next_step_handler(msg, remove_song_by_number)

def remove_song_by_number(message):
    try:
        index = int(message.text.strip()) - 1
        if 0 <= index < len(song_links):
            removed = song_links.pop(index)
            bot.reply_to(message, f"✅ آهنگ حذف شد: {removed}")
            print(f"[LOG] Removed song: {removed}")
        else:
            bot.reply_to(message, "❌ شماره اشتباه است!")
    except:
        bot.reply_to(message, "❌ لطفاً یک عدد معتبر وارد کنید!")
    finally:
        bot.clear_step_handler_by_chat_id(message.chat.id)

# ---------------- Show songs -----------------
@bot.message_handler(func=lambda message: message.text == "📋 نمایش آهنگ‌ها")
def show_songs(message):
    if song_links:
        text = "🎵 لیست آهنگ‌ها:\n\n" + "\n".join([f"{i+1}. {s}" for i, s in enumerate(song_links)])
    else:
        text = "❌ لیست آهنگ‌ها خالی است."
    bot.send_message(message.chat.id, text)

# ---------------- Send Song Directly from URL -----------------
def send_song(url):
    try:
        filename = url.split("/")[-1]
        if not filename.lower().endswith(".mp3"):
            filename += ".mp3"
        print(f"[LOG] 🚀 Sending to channel: {filename}")
        bot.send_audio(chat_id=CHANNEL_ID, audio=url, title=filename)
        print(f"[LOG] ✅ Sent successfully: {filename}")
    except Exception as e:
        print(f"[LOG] ❌ Error sending song: {e}")

# ---------------- Daily Job -----------------
def daily_job():
    print(f"[LOG] ⏳ Running daily job at {datetime.now().strftime('%H:%M')}")
    if song_links:
        link = song_links.pop(0)  # حذف آهنگ بعد از ارسال
        send_song(link)
        print(f"[LOG] ✅ Remaining songs: {len(song_links)}")
    else:
        print("[LOG] ❌ هیچ آهنگی برای ارسال وجود ندارد! (پیامی در کانال ارسال نمی‌شود)")

# ---------------- Scheduler -----------------
schedule.clear()
schedule.every().day.at(SEND_HOUR).do(daily_job)
print(f"[LOG] ⏰ Daily job scheduled at {SEND_HOUR}")

# ---------------- Bot Polling -----------------
print("[LOG] 🤖 Bot is running...")
while True:
    schedule.run_pending()
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"[LOG] ❌ Polling error: {e}")
    time.sleep(5)
