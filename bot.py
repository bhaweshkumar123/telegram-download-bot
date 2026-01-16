import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

print("=" * 50)
print("🤖 Telegram Video Downloader Bot")
print("🚀 Starting...")
print("=" * 50)

# Get bot token from Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found!")
    print("ℹ️ Please set BOT_TOKEN in Railway dashboard")
    exit(1)

print(f"✅ BOT_TOKEN: {BOT_TOKEN[:10]}...")

# Channel settings
CHANNEL_USERNAME = "@tradingword007"
CHANNEL_LINK = "https://t.me/tradingword007"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔎 Check if user joined channel
async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except:
        return False

# ▶ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    joined = await is_user_joined(update, context)
    if not joined:
        await update.message.reply_text(
            "🚫 Bot use करने से पहले हमारा चैनल Join करें:\n\n"
            f"👉 {CHANNEL_LINK}\n\n"
            "Join करने के बाद दोबारा /start भेजें।"
        )
        return

    await update.message.reply_text(
        f'नमस्ते {user.first_name}! 👋\n\n'
        '🎬 **Video Downloader Bot** में आपका स्वागत है!\n\n'
        '📌 **कैसे उपयोग करें:**\n'
        'बस किसी भी platform का video link भेजें\n'
        'मैं download करके आपको भेज दूंगा।\n\n'
        '🌐 **Example:** https://www.youtube.com/watch?v=dQw4w9WgXcQ\n\n'
        '✅ Bot 24×7 online है 🚀'
    )
    logger.info(f"User {user.id} started bot")

# 📥 Download Video
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await update.message.reply_text(
            "❌ पहले हमारा चैनल Join करें:\n"
            f"{CHANNEL_LINK}\n\n"
            "फिर दोबारा link भेजें।"
        )
        return

    url = update.message.text.strip()
    user = update.effective_user
    
    logger.info(f"Download request from {user.id}: {url[:50]}...")
    msg = await update.message.reply_text("📥 Downloading... Please wait.")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown')

        await msg.edit_text(f"✅ Downloaded! Sending: {video_title}")

        # Find downloaded file
        for file in os.listdir():
            if file.startswith("video."):
                with open(file, 'rb') as video:
                    await update.message.reply_video(
                        video=video,
                        caption=f"🎬 {video_title}\n\n✅ Powered by @tradingword007",
                        supports_streaming=True
                    )
                os.remove(file)
                break

        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ Video डाउनलोड नहीं हो पाया। कोई और link भेजें।")
        logger.error(f"Download error: {e}")

# 🚀 Main
def main():
    print("✅ Creating application...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    print("✅ Adding handlers...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("✅ Starting bot polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
