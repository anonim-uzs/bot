from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import sqlite3

BOT_TOKEN = "8827275523:AAGx5RiXv3KJtLGSt_vz6vGJb8uOncjtIKE"
ADMINS = [7844472879]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    # messages jadvaliga 'admin_id' va 'is_answered' qo'shildi
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, is_answered INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

init_db()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    conn = sqlite3.connect("bot.db")
    conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    conn.close()
    
    if message.from_user.id in ADMINS:
        builder = ReplyKeyboardBuilder()
        builder.button(text="📊 Statistika")
        await message.answer("Assalomu alaykum, Admin!", reply_markup=builder.as_markup(resize_keyboard=True))
    else:
        await message.answer("Assalomu alaykum! Savolingizni yozing.")

@dp.message(~F.from_user.id.in_(ADMINS))
async def handle_user_messages(message: types.Message):
    conn = sqlite3.connect("bot.db")
    # Bazaga xabarni saqlaymiz (user_id bilan)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_id, is_answered) VALUES (?, 0)", (message.from_user.id,))
    msg_db_id = cursor.lastrowid # Xabarning bazadagi IDsi
    conn.commit()
    conn.close()
    
    user_name = message.from_user.full_name
    # Xabar matniga bazadagi IDni ham qo'shamiz (yashirin holda)
    info_header = f"📩 **Yangi xabar!**\n👤 Ismi: {user_name}\n🆔 ID: `{message.from_user.id}`\n🔢 DB_ID: `{msg_db_id}`"
    
    for admin_id in ADMINS:
        try:
            await bot.send_message(chat_id=admin_id, text=info_header, parse_mode="Markdown")
            await message.copy_to(chat_id=admin_id)
        except: pass
    await message.answer("✅ Xabaringiz adminlarga yuborildi.")

@dp.message(F.from_user.id.in_(ADMINS), F.reply_to_message)
async def handle_admin_reply(message: types.Message):
    reply_msg = message.reply_to_message
    if "DB_ID: `" in reply_msg.text:
        db_id = int(reply_msg.text.split("DB_ID: `")[1].split("`")[0])
        user_id = int(reply_msg.text.split("🆔 ID: `")[1].split("`")[0])
        
        conn = sqlite3.connect("bot.db")
        # Tekshiramiz: bu xabar allaqachon javob berilganmi?
        status = conn.execute("SELECT is_answered FROM messages WHERE id = ?", (db_id,)).fetchone()
        
        if status and status[0] == 1:
            await message.answer("❌ Bu xabarga allaqachon boshqa admin javob berib bo'lgan!")
            conn.close()
            return
        
        # Javobni yuboramiz va bazani yangilaymiz
        await bot.send_message(user_id, f"👨‍💻 Admin javobi:\n\n{message.text}")
        conn.execute("UPDATE messages SET is_answered = 1 WHERE id = ?", (db_id,))
        conn.commit()
        conn.close()
        await message.answer("🚀 Javobingiz foydalanuvchiga yuborildi!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
