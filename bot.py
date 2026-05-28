from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import sqlite3

BOT_TOKEN = "8827275523:AAGx5RiXv3KJtLGSt_vz6vGJb8uOncjtIKE"
ADMINS = [7844472879]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- BAZA OCHISH ---
def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, is_answered INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

init_db()

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    conn = sqlite3.connect("bot.db")
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    if message.from_user.id in ADMINS:
        builder = ReplyKeyboardBuilder()
        builder.button(text="📊 Statistika")
        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.answer("Assalomu alaykum! Savolingizni yoki rasmingizni yuboring.")

# --- STATISTIKA ---
@dp.message(F.text == "📊 Statistika", F.from_user.id.in_(ADMINS))
async def show_stats(message: types.Message):
    conn = sqlite3.connect("bot.db")
    u = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    ans = conn.execute("SELECT COUNT(*) FROM messages WHERE is_answered = 1").fetchone()[0]
    unans = conn.execute("SELECT COUNT(*) FROM messages WHERE is_answered = 0").fetchone()[0]
    conn.close()
    await message.answer(f"📊 **Statistika:**\n\n✅ Javob berilgan: {ans} ta\n⏳ Javob berilmagan: {unans} ta\n👤 Umumiy foydalanuvchilar: {u} ta")

# --- FOYDALANUVCHI XABARI ---
@dp.message(~F.from_user.id.in_(ADMINS))
async def handle_user_messages(message: types.Message):
    conn = sqlite3.connect("bot.db")
    conn.execute("INSERT INTO messages (is_answered) VALUES (0)")
    conn.commit()
    conn.close()
    
    for admin_id in ADMINS:
        try:
            await bot.send_message(admin_id, f"📩 Yangi murojaat (ID: `{message.from_user.id}`)", parse_mode="Markdown")
            await message.copy_to(admin_id)
        except: pass
    await message.answer("✅ Xabaringiz yuborildi.")

# --- ADMIN JAVOBI ---
@dp.message(F.from_user.id.in_(ADMINS), F.reply_to_message)
async def handle_admin_reply(message: types.Message):
    try:
        reply_msg = message.reply_to_message
        target_id = None
        if "ID: `" in reply_msg.text:
            target_id = int(reply_msg.text.split("ID: `")[1].split("`")[0])
        
        if target_id:
            await bot.send_message(target_id, f"👨‍💻 Admin javobi:\n\n{message.text}")
            conn = sqlite3.connect("bot.db")
            conn.execute("UPDATE messages SET is_answered = 1 WHERE is_answered = 0 LIMIT 1")
            conn.commit()
            conn.close()
            await message.answer("🚀 Javob yuborildi!")
    except Exception as e:
        await message.answer(f"Xatolik: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
