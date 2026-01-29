"""
Telegram Bot for DermaCheck AI with MedGemma
Production version with image bypass (FIX C)
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from models.medgemma_client import MedGemmaClient

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize MedGemma client (global to avoid reloading)
medgemma_client = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🏥 *Selamat datang di DermaCheck AI!*

Saya adalah asisten medis berbasis MedGemma yang dapat membantu Anda dengan:

📝 *Konsultasi Gejala*
Kirim pesan teks mendeskripsikan gejala Anda

💬 *Cara Penggunaan:*
Cukup kirim pesan teks dengan keluhan atau gejala Anda, misalnya:
"Saya mengalami ruam merah di tangan yang gatal sudah 3 hari"

⚠️ *Penting:*
• Ini adalah AI assistant, bukan pengganti dokter
• Untuk diagnosis pasti, konsultasi dengan profesional medis
• Dalam kondisi darurat, hubungi 119

Silakan kirim keluhan Anda! 🩺
"""
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    FIX C: Handle photo messages with bypass
    
    MedGemma is text-only, so we return a helpful message
    asking user to describe their condition in text
    """
    logger.info(f"Photo received from user {update.effective_user.id}")
    
    # Send processing message
    await update.message.reply_text("📷 Gambar diterima. Memproses...")
    
    try:
        # Get bypass response from client
        result = medgemma_client.analyze_skin_condition(
            image=None,  # Not used in bypass mode
            user_complaint=update.message.caption
        )
        
        # Send bypass message
        bypass_text = result.get('education', result['visual_findings']['analysis'])
        
        await update.message.reply_text(bypass_text)
        
        logger.info(f"Image bypass message sent to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan.\n\n"
            "Untuk saat ini, silakan kirim deskripsi kondisi Anda sebagai pesan teks. "
            "Ini akan memberikan analisis yang lebih akurat!\n\n"
            "📞 Darurat: 119"
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (symptoms consultation)"""
    user_message = update.message.text
    logger.info(f"Text consultation from user {update.effective_user.id}: {user_message[:50]}...")
    
    # Send processing message
    await update.message.reply_text("🔍 Menganalisis gejala Anda...")
    
    try:
        # Get consultation from MedGemma
        response = medgemma_client.consult_symptoms(
            symptoms_text=user_message,
            user_age=None,  # Could extract from context if needed
            medical_history=None
        )
        
        # Response already cleaned by _clean_text in client
        # Safe to send to Telegram
        await update.message.reply_text(response)
        
        logger.info(f"Consultation sent to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Text consultation error: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan saat memproses konsultasi.\n\n"
            "Silakan coba lagi atau hubungi layanan kesehatan.\n\n"
            "📞 Darurat: 119"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "⚠️ Terjadi kesalahan teknis.\n\n"
            "Silakan coba lagi atau hubungi layanan kesehatan.\n\n"
            "📞 Darurat: 119"
        )


def main():
    """Start the bot"""
    global medgemma_client
    
    print("="*70)
    print("🚀 STARTING DERMACHECK AI TELEGRAM BOT")
    print("="*70)
    print("")
    
    # Get bot token
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")
    
    print(f"🔑 Bot token: {bot_token[:20]}...")
    print("")
    
    # Initialize MedGemma client
    print("🧠 Initializing MedGemma client...")
    print("")
    
    medgemma_client = MedGemmaClient()
    
    print("")
    print("✅ MedGemma client ready!")
    print("")
    
    # Create bot application
    print("🤖 Creating Telegram bot application...")
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_error_handler(error_handler)
    
    print("✅ Handlers registered")
    print("")
    print("="*70)
    print("✅ BOT IS RUNNING!")
    print("="*70)
    print("")
    print("📱 Ready to receive messages on Telegram")
    print("⏸️  Press Ctrl+C to stop")
    print("")
    
    # Start bot
    logger.info("Bot started successfully")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
