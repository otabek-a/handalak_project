from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update, ReplyKeyboardMarkup
import sqlite3
from telegram.ext import MessageHandler, Filters
import sqlite3
def create_table():
    conn = sqlite3.connect("maqolalar.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maqolalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ism TEXT NOT NULL,
            familiya TEXT NOT NULL,
            hudud TEXT NOT NULL,
            til TEXT NOT NULL,
            turi TEXT NOT NULL,
            boglanish TEXT DEFAULT 'Ko‘rsatilmagan',
            mavzu TEXT NOT NULL,
            matn TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Jadval muvaffaqiyatli yaratildi.")

# Dastur ishga tushganda chaqiriladi
create_table()
import sqlite3

def maqola_qabul(update, context):
    text = update.message.text

    try:
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        data = {}

        synonyms = {
            'familya': 'familiya',
            'maqola tili': 'maqola tili',
            'maqola turi': 'maqola turi',
            'youzvchi bilan boglanish': 'boglanish',
            'maqola mavzu': 'maqola mavzusi',
            'maqola matni': 'maqola',
        }

        current_key = None
        maqola_lines = []

        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                key = synonyms.get(key, key)

                if key == 'maqola':
                    current_key = 'maqola'
                    maqola_lines.append(value.strip())
                else:
                    data[key] = value.strip()
                    current_key = None
            else:
                if current_key == 'maqola':
                    maqola_lines.append(line.strip())

        if maqola_lines:
            data['maqola'] = '\n'.join(maqola_lines)

        required_fields = ['ism', 'familiya', 'hudud', 'maqola tili', 'maqola turi', 'maqola mavzusi', 'maqola']
        missing = [field for field in required_fields if field not in data]

        if missing:
            update.message.reply_text(f"❌ Quyidagi maydonlar yetishmayapti: {', '.join(missing)}")
            return

        boglanish = data.get('boglanish', 'Ko‘rsatilmagan')

        conn = sqlite3.connect("maqolalar.db")
        cursor = conn.cursor()

        # 🔍 MAQOLA MATNI TAKRORINI TEKSHIRISH
        cursor.execute("SELECT COUNT(*) FROM maqolalar WHERE matn = ?", (data['maqola'],))
        count = cursor.fetchone()[0]
        if count > 0:
            update.message.reply_text("⚠️ Bunday maqola matni allaqachon bazada mavjud. Iltimos, yangi va original maqola yuboring.")
            conn.close()
            return

        # ✅ INSERT MAQOLA
        cursor.execute("""
            INSERT INTO maqolalar (ism, familiya, hudud, til, turi, boglanish, mavzu, matn)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['ism'],
            data['familiya'],
            data['hudud'],
            data['maqola tili'],
            data['maqola turi'],
            boglanish,
            data['maqola mavzusi'],
            data['maqola']
        ))

        conn.commit()
        conn.close()

        update.message.reply_text("✅ Maqolangiz muvaffaqiyatli qabul qilindi va bazaga saqlandi.")

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        update.message.reply_text(f"❗ Xatolik yuz berdi:\n{str(e)}\n\n{traceback_str}")

def start(update,context):
    relpy_key = [['Maqola chop etish', 'mening hamyonim']]
    key = ReplyKeyboardMarkup(relpy_key)
    user_id = update.message.from_user.id
    user_username = update.message.from_user.username
    if user_username:
        update.message.reply_text(f"👋 Assalomu aleykum do'stim  @{user_username}, xush kelibsiz botimizga!",  reply_markup=key)
    else:
        user_first_name = update.message.from_user.first_name
        update.message.reply_text(f"👋 Assalomu aleykum do'stim  @{user_username}, xush kelibsiz botimizga!", reply_markup=key )
def yordam(update, context):
    update.message.reply_text("""
📌 *Maqola yuborish uchun namunaviy format:*

✍️ *Ism:* Abdurashid  
👨‍👩‍👧‍👦 *Familiya:* Karimov  
📍 *Hudud:* Samarqand viloyati, Kattaqo‘rg‘on tumani  
🗣 *Maqola tili:* O‘zbekcha  
📚 *Maqola turi:* Ilmiy maqola  
📞 *Yozuvchi bilan bog‘lanish:* +998 90 123 45 67 (ixtiyoriy)  
🎯 *Maqola mavzusi:* Iqlim o‘zgarishi va uning oqibatlari  
📝 *Maqola:*  
Bugungi kunda iqlim o‘zgarishi butun dunyo bo‘ylab dolzarb masalalardan biridir. Bu holat inson hayot tarziga, qishloq xo‘jaligiga va atrof-muhitga jiddiy ta’sir ko‘rsatmoqda... (davom ettiring)

✅ *Eslatma:*  
- Maqola kamida **200 ta so‘z** bo‘lishi kerak  
- Imlo va uslubga e’tibor bering  
- So‘kinish yoki nomaqbul so‘zlardan foydalanmang

🧠 AI (sun’iy intellekt) sizning maqolangizni tahlil qilib, **1 dan 10 gacha baho beradi**. Har bir yulduz (ball) uchun sizga pul to‘lanadi.
""", parse_mode="Markdown")

def maqola(update, context):
    update.message.reply_text("""
📝 *Maqola yuborish bo‘yicha yo‘riqnoma:*

📌 *1-qadam: Ma’lumotlarni to‘ldiring*
Quyidagi ma’lumotlarni kiriting:

- Ism:
- Familiya:
- Hudud:
- Maqola tili:
- Maqola turi: (Iltimos shu tugmani bosing: /maqolalar)
- Yozuvchi bilan bog‘lanish: (ixtiyoriy)
- Maqola mavzusi:
- Maqola matni:

👉 Misol uchun format: /yordam ,/format

📌 *2-qadam: Tekshiruv jarayoni*
Maqolangiz saytga chiqishi uchun biz uni tekshiramiz. Iltimos, quyidagilarga e’tibor bering:

- Maqola kamida 200 ta so‘zdan iborat bo‘lsin
- Imloviy xatolarsiz va adabiy tilga mos yozilgan bo‘lsin
- Nomaqbul (so‘kinish, haqorat) so‘zlar ishlatilmasin
- AI (sun’iy intellekt) tomonidan tahlil qilinadi

📌 *3-qadam: Baholash va mukofot*
Agar maqolangiz o‘zbek tilida bo‘lsa, AI tomonidan 1 dan 10 gacha baho beriladi. Har bir yulduz (ball) uchun sizga haq to‘lanadi.

*⚠️ Eslatma:* Biz emas, aynan AI baho beradi. 
""", parse_mode="Markdown")

def maqolalar(update, context):
    update.message.reply_text(
        "📚 *Maqola turlari va misollar:*\n\n"
        "1. 🧠 *Ilmiy maqola*\n"
        "   - Quyosh sistemasining tarkibi\n"
        "   - Organik va noorganik moddalarning farqi\n\n"
        "2. 📰 *Publitsistik maqola*\n"
        "   - Ijtimoiy tarmoqlarning yoshlar hayotiga ta’siri\n"
        "   - Zamonaviy texnologiya – imkoniyatmi yoki xavf?\n\n"
        "3. 🧾 *Tahliliy maqola*\n"
        "   - O‘zbekistonda ishsizlik muammosi\n"
        "   - Maktab ta’limining sifati va natijalari\n\n"
        "4. 🧚 *Ertak*\n"
        "   - Zumrad va Qimmat\n"
        "   - Tog‘da yashagan tulki\n\n"
        "5. 📝 *She’r*\n"
        "   - O‘zbekiston — Vatani azizim\n"
        "   - Bahor go‘zalligi\n\n"
        "6. 📖 *Hikoya*\n"
        "   - Odob-axloq\n"
        "   - Sinovdagi do‘stlik\n\n"
        "7. 😄 *Latifa*\n"
        "   👨‍🏫 Ustoz: “Sardor, nega darsga kech qolding?”\n"
        "   👦 Sardor: “Dadam aytdi: kim erta turadi, shuni ishi ko‘p bo‘ladi. Men esa kam ishlashni istadim.”\n"
        "   👨‍🏫 😅",
        parse_mode='Markdown'
    )

def format_ber(update, context):
    update.message.reply_text("""

Ism: 
Familiya: 
Hudud: 
Maqola Tili: 
Maqola turi: 
Youzvchi bilan boglanish: 
Maqola mavzusi: 
Maqola:
""")


updater = Updater('7701511616:AAFDiUqn-62MuTxr0rvchf96C6dW1AusheY', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text('Maqola chop etish'), maqola))
dispatcher.add_handler(CommandHandler("format", format_ber))
dispatcher.add_handler(CommandHandler('maqolalar', maqolalar))
dispatcher.add_handler(CommandHandler('yordam', yordam))

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, maqola_qabul))
updater.start_polling()
updater.idle()
