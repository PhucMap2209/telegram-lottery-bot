import os
import re
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 🔹 Token bot Telegram (Thay bằng token thật của bạn)
TOKEN = "7814237273:AAFKavPlRVZWSSw-ewl2tD9Fk6YeMANyBxw"

# 🔹 Tạo bot
app = Application.builder().token(TOKEN).build()

# 🔹 Tạo Flask app để tự ping
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot đang chạy!"

# 🔹 Chạy Flask trong luồng riêng
def run_flask():
    import os
port = int(os.environ.get("PORT", 5000))  # Railway cấp cổng tự động
flask_app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

# 🔹 Tự động ping bot mỗi 5 phút
def auto_ping():
    while True:
        try:
            requests.get("https://118d7ca6-7ee3-4fe4-9f07-6a620df7a3e9-00-3if5d50jx2ueo.sisko.replit.dev/")
            print("✅ Ping thành công!")
        except:
            print("⚠ Lỗi khi ping!")
        threading.Event().wait(300)  # Chờ 5 phút

threading.Thread(target=auto_ping, daemon=True).start()

# 🔹 Hàm xử lý tin nhắn và tính toán cược
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.upper().strip()

        # Kiểm tra nếu có "MB" (Miền Bắc)
        is_mb = bool(re.search(r"\bMB\b", text, re.IGNORECASE))
        text = re.sub(r"\bMB\b", "", text, flags=re.IGNORECASE).strip()

        # Regex nhận dạng cược
        bet_pattern = r"([\d\s]+)\s*(BAO|XC|ĐẦU ĐUÔI|ĐẦU|ĐUÔI|ĐÁ)\s*(\d+)(K|K)?"
        bets = re.findall(bet_pattern, text)

        # Lấy số đài
        num_lotto_match = re.search(r"(\d+)\s*ĐÀI", text)
        num_lotto = int(num_lotto_match.group(1)) if num_lotto_match else 1

        total_bet_amount = 0
        response = "📢 Tổng kết cược:\n"

        if not bets:
            await update.message.reply_text("⚠ Không tìm thấy cược hợp lệ!")
            return

        for bet in bets:
            numbers = bet[0].strip().split()
            bet_type = bet[1]
            bet_amount = int(bet[2]) * 1000

            if bet_type == "ĐÁ":
                num_numbers = len(numbers)
                if is_mb:
                    if num_numbers == 2:
                        total_bet = 46 * bet_amount
                    elif num_numbers == 3:
                        total_bet = 138 * bet_amount
                    else:
                        response += f"⚠ Không hỗ trợ cược ĐÁ với {num_numbers} số ở miền Bắc!\n"
                        continue
                else:
                    if num_numbers == 2:
                        if num_lotto == 1:
                            total_bet = 30 * bet_amount
                        elif num_lotto == 2:
                            total_bet = 60 * bet_amount
                        elif num_lotto == 3:
                            total_bet = 180 * bet_amount
                        else:
                            response += f"⚠ Không hỗ trợ {num_lotto} đài cho cược ĐÁ 2 số!\n"
                            continue
                    elif num_numbers == 3:
                        if num_lotto == 1:
                            total_bet = 90 * bet_amount
                        elif num_lotto == 2:
                            total_bet = 180 * bet_amount
                        elif num_lotto == 3:
                            total_bet = 540 * bet_amount
                        else:
                            response += f"⚠ Không hỗ trợ {num_lotto} đài cho cược ĐÁ 3 số!\n"
                            continue
                    else:
                        response += f"⚠ Không hỗ trợ cược ĐÁ với {num_numbers} số ở miền Nam!\n"
                        continue
            else:
                total_bet = len(numbers) * bet_amount

            total_bet_amount += total_bet
            response += f"🎲 {len(numbers)} số: {', '.join(numbers)}\n"
            response += f"📌 Loại cược: {bet_type}\n"
            response += f"💰 Tổng cược: {total_bet:,} VND\n\n"

        response += f"📢 Miền: {'Bắc' if is_mb else 'Nam'}\n"
        response += f"📢 Số đài: {num_lotto}\n"
        response += f"💵 Tổng cược: {total_bet_amount:,} VND\n"

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"⚠ Lỗi: {str(e)}")
        print(f"LỖI: {e}")

# 🔹 Thêm handler vào bot
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

# 🔹 Chạy bot
print("🤖 Bot đang chạy...")
app.run_polling()
