"""
DermaCheck AI - WhatsApp Bot (Cloud API Version)
Powered by Meta WhatsApp Business Platform

MIGRATION: Twilio → WhatsApp Cloud API
Reason: Indonesian geo-blocking fix (Error 63058)
Benefits: Native Meta support, no blocking, lower latency
"""
from flask import Flask, request, jsonify
from PIL import Image
import requests
from io import BytesIO
import os
from dotenv import load_dotenv
import json

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
    print("✅ Med Gemma client ready")
except Exception as e:
    medgemma = None
    print(f"⚠️ MedGemma unavailable: {e}")

# WhatsApp Cloud API Configuration
WHATSAPP_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'dermacheck_secure_token_2026')

print("✅ WhatsApp Cloud API Bot initialized!")


@app.route("/webhook", methods=['GET'])
def webhook_verify():
    """
    Webhook verification for WhatsApp Cloud API
    Meta akan hit endpoint ini untuk verify
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("✅ Webhook verified!")
        return challenge, 200
    else:
        print("❌ Webhook verification failed")
        return 'Forbidden', 403


@app.route("/webhook", methods=['POST'])
def webhook_handler():
    """
    Main webhook handler for incoming WhatsApp messages
    """
    try:
        data = request.get_json()
        print(f"📱 Webhook received: {json.dumps(data, indent=2)}")
        
        # Extract message data
        if not data.get('entry'):
            return jsonify({'status': 'no entry'}), 200
        
        entry = data['entry'][0]
        changes = entry.get('changes', [])
        
        if not changes:
            return jsonify({'status': 'no changes'}), 200
        
        change = changes[0]
        value = change.get('value', {})
        messages = value.get('messages', [])
        
        if not messages:
            return jsonify({'status': 'no messages'}), 200
        
        message = messages[0]
        from_number = message.get('from')
        message_type = message.get('type')
        
        print(f"📩 Message from {from_number}, type: {message_type}")
        
        # Handle different message types
        if message_type == 'image':
            # User sent photo - ANALYZE IT!
            handle_image_message(message, from_number)
        
        elif message_type == 'text':
            # User sent text command
            text = message.get('text', {}).get('body', '').strip().lower()
            handle_text_message(text, from_number)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_image_message(message, from_number):
    """Handle incoming image and perform analysis"""
    try:
        image_data = message.get('image', {})
        image_id = image_data.get('id')
        
        if not image_id:
            send_message(from_number, "⚠️ Gagal mendapatkan gambar. Silakan kirim ulang.")
            return
        
        print(f"📷 Processing image ID: {image_id}")
        
        # Download image from WhatsApp Cloud API
        image_url = get_media_url(image_id)
        
        if not image_url:
            send_message(from_number, "⚠️ Gagal download gambar. Coba lagi ya!")
            return
        
        # Download and open image
        headers = {'Authorization': f'Bearer {WHATSAPP_TOKEN}'}
        img_response = requests.get(image_url, headers=headers, timeout=30)
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
        
        send_message(from_number, reply)
        print("✅ Reply sent!")
        
    except Exception as e:
        print(f"❌ Image handling error: {e}")
        send_message(
            from_number,
            f"⚠️ Maaf, terjadi error saat analisis.\n\n"
            f"Silakan coba lagi dengan foto yang lebih jelas!"
        )


def handle_text_message(text, from_number):
    """Handle text commands"""
    if text in ['hi', 'halo', 'hello', 'help', 'start']:
        send_message(from_number, WELCOME_MESSAGE)
        print("📨 Sent welcome message")
    
    elif text == 'tips':
        send_message(from_number, PHOTO_TIPS)
        print("📨 Sent photo tips")
    
    else:
        send_message(from_number, HELP_MESSAGE)
        print("📨 Sent help message")


def get_media_url(media_id):
    """Get media URL from WhatsApp Cloud API"""
    try:
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {'Authorization': f'Bearer {WHATSAPP_TOKEN}'}
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        return data.get('url')
    except Exception as e:
        print(f"❌ Get media URL error: {e}")
        return None


def send_message(to_number, message_text):
    """Send message via WhatsApp Cloud API"""
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to_number,
            'type': 'text',
            'text': {'body': message_text}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Message sent to {to_number}")
        else:
            print(f"❌ Send failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Send message error: {e}")


def format_whatsapp_reply(abcde_results, medgemma_results=None):
    """Format analysis results for WhatsApp (same as Twilio version)"""
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
    <h1>🏥 DermaCheck AI - WhatsApp Cloud API Bot</h1>
    <p>✅ Bot is running!</p>
    <p>📱 WhatsApp Business Platform Integration</p>
    <p>🔗 Webhook: /webhook (GET/POST)</p>
    <p>🌍 No geo-blocking! Native Meta support!</p>
    """


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 DermaCheck AI - WhatsApp Cloud API Bot")
    print("=" * 50)
    print("📱 Waiting for messages from Meta...")
    print("🌐 Webhook endpoint: http://localhost:5000/webhook")
    print("✅ No geo-blocking! Indonesian support!")
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
