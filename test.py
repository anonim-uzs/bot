from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio

# Bot tokeni va Adminning Telegram ID raqami
BOT_TOKEN = "8827275523:AAGx5RiXv3KJtLGSt_vz6vGJb8uOncjtIKE"
ADMIN_ID = 7844472879 # Bu yerga o'zingizning Telegram ID-ingizni yozing

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. BOTNI ISHGA TUSHIRISH (/start)
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        "Savol yoki taklifingizni shu yerga yozib qoldiring, admin tez orada javob beradi."
    )

# 2. FOYDALANUVCHIDAN XABAR OLISH VA DARHOL ADMINGA YUBORISH
@dp.message(F.chat.type == "private", F.from_user.id != ADMIN_ID)
async def handle_user_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text if message.text else "[Matnli bo'lmagan xabar]"
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

    # Adminga yuboriladigan xabar formati (User ID maxsus belgi ichida saqlanadi)
    admin_text = (
        f"📩 **Yangi xabar keldi!**\n\n"
        f"👤 Kimdan: {message.from_user.full_name}\n"
        f"🆔 User ID: `{user_id}`\n"
        f"🌐 Username: {username}\n\n"
        f"💬 Xabar:\n{text}"
    )
    
    try:
        # Xabarni darhol adminga yuboramiz
        await bot.send_message(chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown")
        
        # Foydalanuvchiga tasdiq xabari yuboramiz
        await message.answer("✅ Xabaringiz adminga yetkazildi. Admin javobini kuting... ⏳")
    except Exception as e:
        await message.answer("❌ Xabarni yuborishda xatolik yuz berdi. Keyinroq qayta urinib ko'ring.")
        print(f"Xatolik: {e}")

# 3. ADMIN JAVOBINI FOYDALANUVCHIGA YETKAZISH (REPLY ORQALI)
@dp.message(F.chat.type == "private", F.from_user.id == ADMIN_ID)
async def handle_admin_reply(message: types.Message):
    # Admin bot yuborgan xabarga 'Reply' (Javob berish) qilganini tekshiramiz
    if not message.reply_to_message:
        await message.answer("⚠️ Foydalanuvchiga javob yozish uchun, bot yuborgan o'sha xabarga 'Reply' (Ответить) qilib yozing!")
        return

    try:
        # Admin javob bergan xabar matnidan foydalanuvchining ID-sini qidirib topamiz
        reply_text = message.reply_to_message.text
        
        target_user_id = None
        # Matn ichidan "User ID:" qatorini qidiramiz
        for line in reply_text.split("\n"):
            if "User ID:" in line:
                # "User ID:" so'zidan keyingi raqamni ajratib olamiz
                target_user_id = int(line.split(":")[1].strip())
                break
        
        if target_user_id:
            # Foydalanuvchiga admin javobini yuboramiz
            admin_answer = f"👨‍💻 **Admin javobi:**\n\n{message.text}"
            await bot.send_message(chat_id=target_user_id, text=admin_answer, parse_mode="Markdown")
            
            # Adminga xabar muvaffaqiyatli ketganini bildiramiz
            await message.reply("🚀 Javobingiz foydalanuvchiga yetkazildi!")
        else:
            await message.reply("❌ Xabar matnidan foydalanuvchi ID-sini aniqlab bo'lmadi (Matn o'zgarib ketgan bo'lishi mumkin).")
            
    except Exception as e:
        await message.reply(f"❌ Xabarni foydalanuvchiga yuborib bo'lmadi. Foydalanuvchi botni bloklagan bo'lishi mumkin.\nXatolik: {str(e)}")

# BOTNI ISHGA TUSHIRISH
async def main():
    print("Qayta aloqa boti muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
