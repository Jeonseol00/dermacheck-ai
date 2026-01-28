"""
DermaCheck AI Telegram Bot - MedGemma Local Version
Uses local Med Gemma model for HAI-DEF compliance
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import asyncio

# Import local MedGemma client
from models.local_medgemma_client import LocalMedGemmaClient

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize local MedGemma client (loads model at startup)
logger.info("="*60)
logger.info("🚀 Initializing DermaCheck AI with MedGemma...")
logger.info("="*60)

try:
    medgemma_client = LocalMedGemmaClient(model_name="google/medgemma-4b-it")
    logger.info("✅ MedGemma client initialized successfully!")
except Exception as e:
    logger.error(f"❌ Failed to initialize MedGemma: {e}")
    raise

# Get bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """🏥 *Selamat datang di DermaCheck AI!*

 Saya asisten kesehatan AI powered by MedGemma dari Google.

📸 *Kirim foto kulit* untuk analisis dermatologi
💬 *Kirim gejala* untuk konsultasi medis

🔬 *Using*: MedGemma 4B (HAI-DEF Compliant)
⚡ *Running*: Local inference di Kaggle GPU

⚠️ *Disclaimer*: Ini adalah AI assistant, bukan dokter sungguhan."""
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )
    logger.info(f"User {update.effective_user.id} started the bot")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo analysis"""
    logger.info(f"Received photo from user {update.effective_user.id}")
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "🔬 *Menganalisis gambar dengan MedGemma...*\\n\\n"
        "⏳ Mohon tunggu 15-20 detik...",
        parse_mode='Markdown'
    )
    
    try:
        # Download photo
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"temp_photo_{update.effective_user.id}.jpg"
        await photo_file.download_to_drive(photo_path)
        
        logger.info(f"Photo downloaded: {photo_path}")
        
        # Analyze with MedGemma
        result = medgemma_client.analyze_skin_condition(
            image=photo_path,
            user_complaint=update.message.caption
        )
        
        # Format response
        if "error" in result:
            response = f"❌ *Error*: {result['error']}"
        elif "raw_response" in result:
            # Fallback to raw text if JSON parsing failed
            response = f"🩺 *HASIL ANALISIS KULIT*\\n\\n{result['raw_response']}"
        else:
            # Format structured response
            response = format_dermatology_result(result)
        
        # Send result
        await processing_msg.edit_text(
            response,
            parse_mode='Markdown'
        )
        
        logger.info(f"Analysis sent to user {update.effective_user.id}")
        
        # Cleanup
        if os.path.exists(photo_path):
            os.remove(photo_path)
        
    except Exception as e:
        logger.error(f"Photo analysis error: {str(e)}")
        await processing_msg.edit_text(
            "❌ *Maaf, terjadi kesalahan.*\\n\\n"
            "Silakan coba lagi atau hubungi support.",
            parse_mode='Markdown'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text consultation"""
    text = update.message.text
    
    # Ignore if no text or command
    if not text or text.startswith('/'):
        return
    
    logger.info(f"Medical consultation request from user {update.effective_user.id}")
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "🩺 *Menganalisis gejala Anda...*\\n\\n"
        "⏳ Mohon tunggu sebentar...",
        parse_mode='Markdown'
    )
    
    try:
        # Consult with MedGemma
        result = medgemma_client.consult_symptoms(text)
        
        # Send result
        await processing_msg.edit_text(
            result,
            parse_mode='HTML'  # MedGemma uses emoji, HTML is safer
        )
        
        logger.info(f"Consultation sent to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Medical consultation error: {str(e)}")
        await processing_msg.edit_text(
            "❌ *Maaf, terjadi kesalahan.*\\n\\n"
            "Silakan coba lagi atau hubungi layanan kesehatan langsung.\\n\\n"
            "📞 *Darurat: 119*",
            parse_mode='Markdown'
        )


def format_dermatology_result(result: dict) -> str:
    """Format dermatology analysis for Telegram"""
    
    message = "🩺 *HASIL ANALISIS KULIT*\\n\\n"
    
    # Visual findings
    if "visual_findings" in result:
        visual = result["visual_findings"]
        message += "👁️ *Temuan Visual:*\\n"
        message += f"• Lokasi: {visual.get('location', 'N/A')}\\n"
        message += f"• Morfologi: {visual.get('morphology', 'N/A')}\\n"
        message += f"• Warna: {visual.get('color', 'N/A')}\\n\\n"
    
    # Differential diagnosis
    if "differential_diagnosis" in result:
        message += "🔍 *Kemungkinan Kondisi:*\\n"
        for i, dx in enumerate(result["differential_diagnosis"][:3], 1):
            condition = dx.get("condition", "Unknown")
            confidence = dx.get("confidence", "?")
            message += f"{i}. {condition} - Confidence: {confidence}%\\n"
        message += "\\n"
    
    # Red flags
    if "red_flags" in result and result["red_flags"]:
        message += "⚠️ *WARNING - Tanda Bahaya:*\\n"
        for flag in result["red_flags"]:
            message += f"• {flag}\\n"
        message += "\\n"
    
    # Home care
    if "home_care" in result:
        message += "💊 *Saran Perawatan (Home Care):*\\n"
        for care in result["home_care"]:
            message += f"• {care}\\n"
        message += "\\n"
    
    # Referral
    if "referral" in result:
        referral = result["referral"]
        urgency_emoji = {"URGENT": "🚨", "SOON": "⏰", "ROUTINE": "📅"}.get(
            referral.get("urgency", "ROUTINE"), "📋"
        )
        message += f"{urgency_emoji} *Rekomendasi Tindak Lanjut:*\\n"
        message += f"{referral.get('reason', 'Konsultasi dokter kulit')}\\n\\n"
    
    # Disclaimer
    if "disclaimer" in result:
        message += f"⚠️ *Disclaimer:*\\n{result['disclaimer']}"
    
    return message


def main():
    """Main bot function"""
    logger.info("Starting DermaCheck AI Telegram Bot (MedGemma version)...")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run bot
    logger.info("Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
