"""
DermaCheck AI - WhatsApp Bot
Powered by Twilio Sandbox

Enables grassroots accessibility for elderly/rural users.
Reuses existing ABCDE analysis logic - zero duplication!
"""
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv

# REUSE existing analyzers! 100% logic reuse!
from models.abcde_analyzer import ABCDEAnalyzer
from models.medgemma_client import MedGemmaClient

load_dotenv()

app = Flask(__name__)

# Initialize analyzers (REUSE!)
print("🔧 Initializing analyzers...")
analyzer = ABCDEAnalyzer()

try:
    medgemma = MedGemmaClient()
    print("✅ MedGemma client ready")
except Exception as e:
    medgemma = None
    print(f"⚠️ MedGemma unavailable: {e}")

# Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

print("✅ WhatsApp Bot initialized!")


@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    """
    Receive WhatsApp messages from Twilio
    Main webhook endpoint
    """
    # Get message data
    incoming_msg = request.values.get('Body', '').strip().lower()
    from_number = request.values.get('From', '')
    media_url = request.values.get('MediaUrl0', '')
    
    print(f"📱 Message from {from_number}: {incoming_msg[:50]}")
    if media_url:
        print(f"📷 Photo received: {media_url}")
    
    # Create response
    resp = MessagingResponse()
    
    # Handle different message types
    if media_url:
        # User sent photo - ANALYZE IT!
        try:
            print("🔍 Analyzing image...")
            
            # Download image from Twilio
            img_response = requests.get(media_url, timeout=30)
            image = Image.open(BytesIO(img_response.content))
            
            print(f"✅ Image loaded: {image.size}")
            
            # REUSE EXISTING LOGIC!
            abcde_results = analyzer.analyze(image)
            
            # Check if blank detection rejected
            if abcde_results.get('status') == 'rejected':
                print("⚠️ Image rejected (blank detection)")
                reply = format_rejection_reply(abcde_results)
            else:
                print(f"✅ Analysis complete: {abcde_results.get('risk_level')}")
                
                # Get medgemma interpretation (if available)
                if medgemma:
                    try:
                        medgemma_results = medgemma.analyze_skin_lesion(abcde_results)
                        reply = format_whatsapp_reply(abcde_results, medgemma_results)
                    except Exception as e:
                        print(f"⚠️ MedGemma error: {e}")
                        reply = format_simple_reply(abcde_results)
                else:
                    reply = format_simple_reply(abcde_results)
            
            resp.message(reply)
            print("✅ Reply sent!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            resp.message(
                f"⚠️ Maaf, terjadi error saat analisis.\n\n"
                f"Silakan coba lagi dengan:\n"
                f"• Foto lebih jelas\n"
                f"• Cahaya lebih terang\n"
                f"• Fokus pada lesi\n\n"
                f"Error: {str(e)[:100]}"
            )
    
    elif incoming_msg in ['hi', 'halo', 'hello', 'help', 'start']:
        # Welcome message
        resp.message(WELCOME_MESSAGE)
        print("📨 Sent welcome message")
    
    elif incoming_msg == 'tips':
        # Photo tips
        resp.message(PHOTO_TIPS)
        print("📨 Sent photo tips")
    
    else:
        # Default help
        resp.message(HELP_MESSAGE)
        print("📨 Sent help message")
    
    return str(resp)


def format_whatsapp_reply(abcde_results, medgemma_results=None):
    """
    Format analysis results for WhatsApp
    Simple, concise, elderly-friendly!
    """
    risk = abcde_results['risk_level']
    score = abcde_results['total_score']
    
    # Risk emoji
    risk_emoji = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🔴'
    }.get(risk, '⚪')
    
    # Build message
    msg = f"""
╔══════════════════╗
  HASIL ANALISIS  
╚══════════════════╝

{risk_emoji} *TINGKAT RISIKO: {risk}*
Skor: {score}/11

━━━━━━━━━━━━━━━━━━

📊 *DETAIL ABCDE:*

• Asymmetry: {abcde_results['abcde_scores']['asymmetry']}/2
• Border: {abcde_results['abcde_scores']['border']}/2
• Color: {abcde_results['abcde_scores']['color']}/2
• Diameter: {abcde_results['abcde_scores']['diameter']}/2
• Evolution: {abcde_results['abcde_scores']['evolution']}/3

━━━━━━━━━━━━━━━━━━
"""
    
    # Add recommendation based on risk
    if risk == 'HIGH':
        msg += """
🚨 *PENTING!*

Segera konsultasi ke dokter kulit dalam 1-2 minggu!

Jangan tunda. Bawa hasil ini saat ke dokter.
"""
    elif risk == 'MEDIUM':
        msg += """
⚠️ *PERHATIAN*

Sebaiknya periksa ke dokter dalam 1 bulan.

Pantau terus. Kalau ada perubahan, segera ke dokter.
"""
    else:
        msg += """
✅ *AMAN*

Kemungkinan tidak berbahaya.

Tetap pantau. Kalau berubah, foto lagi ya!
"""
    
    msg += """
━━━━━━━━━━━━━━━━━━

💬 Kirim "TIPS" untuk tips foto
📸 Kirim foto lagi untuk analisis baru

⚠️ *Disclaimer:*
Ini BUKAN diagnosa medis.
Selalu konsultasi dokter untuk kepastian.

━━━━━━━━━━━━━━━━━━
DermaCheck AI v3.0
"""
    
    return msg.strip()


def format_simple_reply(abcde_results):
    """Simplified reply without MedGemma"""
    return format_whatsapp_reply(abcde_results, None)


def format_rejection_reply(abcde_results):
    """Reply when blank detection rejects image"""
    blank_info = abcde_results.get('blank_detection', {})
    variance = blank_info.get('variance', 0)
    
    return f"""
⚠️ *FOTO KURANG JELAS*

Foto yang Anda kirim terlalu kosong/polos.

Variance: {variance:.1f} (threshold: 500)

📸 *TIPS FOTO YANG BAIK:*

1️⃣ Fokus pada lesi/tahi lalat
2️⃣ Jarak 10-15 cm
3️⃣ Cahaya cukup (tidak gelap)
4️⃣ Lesi terlihat jelas
5️⃣ Tidak blur/goyang

Silakan kirim foto ulang yang lebih jelas ya! 👍

Ketik "TIPS" untuk panduan lengkap.
"""


WELCOME_MESSAGE = """
🏥 *Selamat Datang di DermaCheck AI!*

Saya adalah asisten AI untuk analisis awal kondisi kulit Anda.

📸 *CARA PAKAI:*

1. Foto tahi lalat/lesi Anda
2. Kirim foto ke chat ini
3. Tunggu hasil (15-30 detik)
4. Baca saran yang diberikan

⚠️ *PENTING:*

• Ini BUKAN diagnosa medis
• Selalu konsultasi dokter
• Hasil hanya referensi awal

💬 Ketik "TIPS" untuk panduan foto

Kirim foto Anda sekarang! 📷
"""

HELP_MESSAGE = """
📋 *BANTUAN DERMACHECK AI*

Cara menggunakan:

1️⃣ *Kirim Foto*
   Kirim foto tahi lalat/lesi kulit

2️⃣ *Tunggu Analisis*
   AI analisis dalam 15-30 detik

3️⃣ *Baca Hasil*
   Lihat tingkat risiko & saran

💬 *Perintah:*

• HELP - Bantuan ini
• TIPS - Panduan foto
• HALO - Selamat datang

📸 Langsung kirim foto untuk mulai!
"""

PHOTO_TIPS = """
📸 *TIPS FOTO YANG BAIK*

✅ *YANG BENAR:*

1. Fokus pada lesi (close-up)
2. Jarak 10-15 cm
3. Cahaya terang & merata
4. Lesi di tengah foto
5. Tidak blur/goyang

❌ *YANG SALAH:*

1. Terlalu jauh
2. Gelap/bayangan
3. Blur/tidak fokus
4. Lesi tidak jelas
5. Tangan goyang

💡 *BONUS TIPS:*

• Foto di siang hari (cahaya alami)
• Gunakan lampu tambahan jika perlu
• Tahan HP stabil saat foto
• Bersihkan kamera HP

Selamat mencoba! 📷✨
"""


@app.route("/")
def home():
    """Health check endpoint"""
    return """
    <h1>🏥 DermaCheck AI - WhatsApp Bot</h1>
    <p>✅ Bot is running!</p>
    <p>📱 Send a message to the Twilio WhatsApp number to start.</p>
    <p>🔗 Webhook: /whatsapp (POST)</p>
    """


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 DermaCheck AI - WhatsApp Bot")
    print("=" * 50)
    print("📱 Waiting for messages from Twilio...")
    print("🌐 Webhook endpoint: http://localhost:5000/whatsapp")
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
