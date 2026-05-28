
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio

BOT_TOKEN = "8827275523:AAF19lC2WCesrFvzP1g7uCbD3Jv3Ngo7lCI"
ADMINS = [7844472879, 1368643171, 5368264484]  # Adminlar ID ro'yxati

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n"
        "Savolingizni yozib qoldiring, adminlarimiz tez orada javob berishadi."
    )

# 1. FOYDALANUVCHIDAN XABAR OLISH VA BARCHA ADMINGA YUBORISH
@dp.message(F.chat.type == "private", ~F.from_user.id.in_(ADMINS))
async def handle_user_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text if message.text else "[Matnli bo'lmagan xabar]"
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

    # Xabar matni (barcha adminlarga bir xil formatda boradi)
    admin_text = (
        f"📩 **Yangi xabar keldi!**\n\n"
        f"👤 Kimdan: {message.from_user.full_name}\n"
        f"🆔 User ID: `{user_id}`\n"
        f"🌐 Username: {username}\n\n"
        f"💬 Xabar:\n{text}"
    )
    
    # Xabarni hamma adminga tarqatamiz
    for admin_id in ADMINS:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_text, parse_mode="Markdown")
        except Exception as e:
            print(f"Admin {admin_id} botni bloklagan bo'lishi mumkin: {e}")
            
    await message.answer("✅ Xabaringiz barcha adminlarga yetkazildi. Javobni kuting... ⏳")


# 2. ADMINlardan BIRI JAVOB BERGANDA QOLGANLARINI OGOHLANTIRISH
@dp.message(F.chat.type == "private", F.from_user.id.in_(ADMINS))
async def handle_admin_reply(message: types.Message):
    if not message.reply_to_message:
        await message.answer("⚠️ Foydalanuvchiga javob yozish uchun, xabarga 'Reply' (Ответить) qilib yozing!")
        return

    try:
        reply_text = message.reply_to_message.text
        target_user_id = None
        
        # Xabar ichidan foydalanuvchi ID sini aniqlaymiz
        for line in reply_text.split("\n"):
            if "User ID:" in line:
                target_user_id = int(line.split(":")[1].strip())
                break
        
        if target_user_id:
            # 1. Foydalanuvchining o'ziga javobni yuboramiz
            admin_answer = f"👨‍💻 **Admin javobi:**\n\n{message.text}"
            await bot.send_message(chat_id=target_user_id, text=admin_answer, parse_mode="Markdown")
            
            # Javob bergan adminning ismi
            responder_name = message.from_user.full_name
            
            # 2. QOLGAN ADMINLARNI OGOHLANTIRISH
            notification_text = (
                f"✅ **Javob berildi!**\n\n"
                f"👤 Foydalanuvchi ID: `{target_user_id}`\n"
                f"👨‍💻 Javob bergan admin: {responder_name}\n"
                f"💬 Berilgan javob: *{message.text}*"
            )
            
            for admin_id in ADMINS:
                # Javob bergan adminning o'ziga "Muvaffaqiyatli ketdi" deymiz, 
                # qolganlarga esa kim javob berganini bildiramiz
                if admin_id == message.from_user.id:
                    await bot.send_message(chat_id=admin_id, text="🚀 Javobingiz foydalanuvchiga yetkazildi!")
                else:
                    try:
                        await bot.send_message(chat_id=admin_id, text=notification_text, parse_mode="Markdown")
                    except Exception:
                        pass
        else:
            await message.reply("❌ Xabar matnidan foydalanuvchi ID-sini aniqlab bo'lmadi.")
            
    except Exception as e:
        await message.reply(f"❌ Xatolik yuz berdi: {str(e)}")

async def main():
    print("Ko'p adminli qayta aloqa boti ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())