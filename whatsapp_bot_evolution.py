"""
DermaCheck AI - Evolution API WhatsApp Bot
Self-hosted gateway with direct image upload support
"""
from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

# Import existing analyzers (100% code reuse!)
from models.abcde_analyzer import ABCDEAnalyzer
from models.medgemma_client import MedGemmaClient

app = Flask(__name__)

# Evolution API Configuration
EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', 'dermacheck_ai_secret_key_2026')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME', 'dermacheck')

# Initialize analyzers
print("🔧 Initializing analyzers...")
analyzer = ABCDEAnalyzer()

try:
    medgemma = MedGemmaClient()
    print("✅ MedGemma client ready")
except Exception as e:
    medgemma = None
    print(f"⚠️ MedGemma unavailable: {e}")

print("✅ Evolution API WhatsApp Bot initialized!")


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return """
    <h1>🏥 DermaCheck AI - Evolution API Bot</h1>
    <p>✅ Bot is running!</p>
    <p>📱 Powered by Evolution API (Self-Hosted)</p>
    <p>🔗 Webhook: /webhook (POST)</p>
    <p>🇮🇩 Indonesia-focused, no geo-blocking!</p>
    """, 200


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Handle incoming messages from Evolution API"""
    
    # Handle GET request (for testing in browser)
    if request.method == 'GET':
        return """
        <h1>✅ Webhook Endpoint Active!</h1>
        <p>🔗 This is the Evolution API webhook endpoint.</p>
        <p>📱 Configure this URL in Evolution API instance settings.</p>
        <p>⚠️ Note: Evolution API sends POST requests to this endpoint.</p>
        <p>🔍 If you see this page, the URL is correct!</p>
        """, 200
    
    # Handle POST request (actual webhook from Evolution API)
    try:
        data = request.json
        
        print("="*60)
        print("📥 EVOLUTION API WEBHOOK:")
        print(data)
        print("="*60)
        
        # Extract event type
        event = data.get('event')
        
        # Only process message events
        if event != 'messages.upsert':
            print(f"⚠️ Ignored event: {event}")
            return jsonify({'status': 'ignored', 'event': event}), 200
        
        # Extract message data
        message_data = data.get('data', {})
        key = message_data.get('key', {})
        message = message_data.get('message', {})
        
        # Get sender
        sender = key.get('remoteJid', '')
        
        # Skip group messages
        if '@g.us' in sender:
            print("⚠️ Ignored group message")
            return jsonify({'status': 'group_ignored'}), 200
        
        # Skip own messages
        if key.get('fromMe'):
            print("⚠️ Ignored own message")
            return jsonify({'status': 'own_message'}), 200
        
        # Extract message content
        text_msg = None
        has_image = False
        
        # Check for text message
        if 'conversation' in message:
            text_msg = message['conversation']
        elif 'extendedTextMessage' in message:
            text_msg = message['extendedTextMessage'].get('text', '')
        
        # Check for image message
        if 'imageMessage' in message:
            has_image = True
        
        print(f"📱 From: {sender}")
        print(f"💬 Text: {text_msg}")
        print(f"🖼️ Has Image: {has_image}")
        
        # Process message
        if has_image:
            # Get message ID for media download
            message_id = key.get('id')
            print(f"📥 Downloading image (message ID: {message_id})...")
            
            # Download and analyze image
            image_data = download_media(message_id, sender)
            
            if image_data:
                # Send processing message
                send_message(sender, "🔍 Sedang menganalisis gambar Anda...\nMohon tunggu 15-30 detik.")
                
                # Analyze image
                reply = analyze_image(image_data, sender)
            else:
                reply = "⚠️ Gagal download gambar. Silakan kirim ulang dengan foto yang lebih jelas!"
        
        elif text_msg:
            # Handle text commands
            reply = handle_text(text_msg.lower().strip())
        
        else:
            reply = "❓ Pesan tidak dikenali. Ketik HELP untuk bantuan."
        
        # Send reply
        send_message(sender, reply)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


def download_media(message_id, sender):
    """Download media from Evolution API"""
    try:
        url = f"{EVOLUTION_API_URL}/chat/getBase64FromMediaMessage/{INSTANCE_NAME}"
        
        headers = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "message": {
                "key": {
                    "id": message_id,
                    "remoteJid": sender
                }
            },
            "convertToMp4": False
        }
        
        print(f"🔗 Requesting media from: {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            base64_data = data.get('base64', '')
            
            if base64_data:
                # Remove data URL prefix if present
                if ',' in base64_data:
                    base64_data = base64_data.split(',')[1]
                
                # Decode base64 to image
                image_bytes = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_bytes))
                
                print(f"✅ Image downloaded: {image.size}")
                return image
            else:
                print("❌ No base64 data in response")
        else:
            print(f"❌ Media download failed: {response.status_code} - {response.text}")
        
        return None
        
    except Exception as e:
        print(f"❌ Media download error: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_image(image, sender):
    """Analyze skin lesion image using ABCDE + Gemini"""
    try:
        print("🔬 Running ABCDE analysis...")
        
        # Run ABCDE analysis
        abcde_results = analyzer.analyze(image)
        
        # Check if blank detection rejected
        if abcde_results.get('status') == 'rejected':
            print("⚠️ Image rejected (blank detection)")
            return format_rejection_reply(abcde_results)
        
        print(f"✅ ABCDE complete: {abcde_results.get('risk_level')}")
        
        # Get MedGemma interpretation (if available)
        if medgemma:
            try:
                print("🤖 Getting Gemini interpretation...")
                medgemma_results = medgemma.analyze_skin_lesion(abcde_results)
                reply = format_whatsapp_reply(abcde_results, medgemma_results)
            except Exception as e:
                print(f"⚠️ MedGemma error: {e}")
                reply = format_simple_reply(abcde_results)
        else:
            reply = format_simple_reply(abcde_results)
        
        print("✅ Analysis complete!")
        return reply
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        return f"""
⚠️ Maaf, terjadi error saat analisis.

Silakan coba lagi dengan foto yang lebih jelas!

Tips:
• Cahaya terang
• Fokus jelas
• Jarak 10-15cm
"""


def handle_text(text):
    """Handle text commands"""
    if text in ['hi', 'halo', 'hello', 'help', 'start', 'mulai']:
        print("📨 Sending welcome message")
        return WELCOME_MESSAGE
    
    elif text in ['tips', 'panduan', 'cara']:
        print("📨 Sending photo tips")
        return PHOTO_TIPS
    
    else:
        print("📨 Sending help message")
        return HELP_MESSAGE


def send_message(to, message_text):
    """Send message via Evolution API"""
    try:
        url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
        
        headers = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "number": to,
            "text": message_text
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"✅ Message sent to {to}")
        else:
            print(f"❌ Send failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Send message error: {e}")


def format_whatsapp_reply(abcde_results, medgemma_results=None):
    """Format analysis results for WhatsApp"""
    risk = abcde_results['risk_level']
    score = abcde_results['total_score']
    
    risk_emoji = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🔴'
    }.get(risk, '⚪')
    
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

💬 Kirim "TIPS" untuk panduan foto
📸 Kirim foto lagi untuk analisis baru

⚠️ *Disclaimer:*
Ini BUKAN diagnosa medis.
Selalu konsultasi dokter untuk kepastian.

━━━━━━━━━━━━━━━━━━
DermaCheck AI v3.0
Self-Hosted via Evolution API
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


# Message templates
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

━━━━━━━━━━━━━━━━━━
Powered by Evolution API (Self-Hosted)
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

• HALO - Selamat datang
• HELP - Bantuan ini
• TIPS - Panduan foto

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


if __name__ == '__main__':
    print("="*60)
    print("🚀 DermaCheck AI - Evolution API WhatsApp Bot")
    print("="*60)
    print("📱 Waiting for messages from Evolution API...")
    print("🌐 Webhook endpoint: http://localhost:5000/webhook")
    print(f"🔗 Evolution API: {EVOLUTION_API_URL}")
    print(f"📦 Instance: {INSTANCE_NAME}")
    print("✅ Self-hosted! No external dependencies!")
    print("="*60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
