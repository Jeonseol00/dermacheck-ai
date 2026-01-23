# 🚀 Evolution API Setup Guide - DermaCheck AI

**Self-Hosted WhatsApp Gateway for Direct Image Upload**

---

## 📋 QUICK START (30 Minutes)

### **Prerequisites**

✅ Ubuntu 24.04 (or any Linux)
✅ Docker installed
✅ Docker Compose installed
✅ 8GB RAM minimum
✅ Stable internet connection

---

## 🔧 STEP 1: Install Docker (If Not Installed)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (no need sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version

# Logout and login again for group changes to take effect
```

---

## 🚀 STEP 2: Deploy Evolution API

```bash
# Navigate to project directory
cd ~/Downloads/hackathon/dermacheck-ai

# Start Evolution API + PostgreSQL
docker-compose up -d

# Check if containers are running
docker ps

# Expected output:
# evolution_api       - Port 8080
# evolution_postgres  - Port 5432
```

**Wait 30 seconds** for containers to fully start.

---

## 📱 STEP 3: Connect WhatsApp

### **A. Create Instance**

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: dermacheck_ai_secret_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "dermacheck",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

**Response:**
```json
{
  "instance": {
    "instanceName": "dermacheck",
    "status": "created"
  },
  "hash": {
    "apikey": "..."
  },
  "qrcode": {
    "code": "...",
    "base64": "data:image/png;base64,..."
  }
}
```

### **B. Get QR Code (Visual)**

**Option 1: Open in browser**
```
http://localhost:8080/instance/connect/dermacheck
```

**Option 2: Via API**
```bash
curl -X GET http://localhost:8080/instance/qrcode/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026"
```

### **C. Scan QR Code**

1. Open WhatsApp on your phone
2. Go to **Settings → Linked Devices**
3. **Link a Device**
4. Scan the QR code from browser/terminal

**Wait for connection...**

### **D. Verify Connection**

```bash
curl -X GET http://localhost:8080/instance/connectionState/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026"
```

**Expected:**
```json
{
  "instance": "dermacheck",
  "state": "open"
}
```

✅ **WhatsApp Connected!**

---

## 🔗 STEP 4: Configure Webhook

Evolution API already configured to send webhooks to:
```
http://host.docker.internal:5000/webhook
```

This points to your Python bot on port 5000!

**Verify webhook:**
```bash
curl -X GET http://localhost:8080/webhook/find/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026"
```

---

## 🐍 STEP 5: Update Python Bot

### **A. Create Evolution API Bot**

File: `whatsapp_bot_evolution.py`

```python
from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
from PIL import Image

# Import existing analyzers
from models.abcde_analyzer import ABCDEAnalyzer
from models.medgemma_client import MedGemmaClient

app = Flask(__name__)

# Evolution API Configuration
EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "dermacheck_ai_secret_key_2026"
INSTANCE_NAME = "dermacheck"

# Initialize analyzers
analyzer = ABCDEAnalyzer()
medgemma = MedGemmaClient()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages from Evolution API"""
    try:
        data = request.json
        
        print("="*60)
        print("📥 EVOLUTION API WEBHOOK:")
        print(data)
        print("="*60)
        
        # Extract message data
        event = data.get('event')
        
        if event != 'messages.upsert':
            return jsonify({'status': 'ignored'}), 200
        
        message_data = data.get('data', {})
        key = message_data.get('key', {})
        message = message_data.get('message', {})
        
        # Get sender
        sender = key.get('remoteJid', '')
        
        # Skip group messages
        if '@g.us' in sender:
            return jsonify({'status': 'group_ignored'}), 200
        
        # Skip own messages
        if key.get('fromMe'):
            return jsonify({'status': 'own_message'}), 200
        
        # Extract message content
        text_msg = None
        image_data = None
        
        # Check for text message
        if 'conversation' in message:
            text_msg = message['conversation']
        elif 'extendedTextMessage' in message:
            text_msg = message['extendedTextMessage'].get('text', '')
        
        # Check for image message
        if 'imageMessage' in message:
            image_msg = message['imageMessage']
            
            # Get image via Evolution API
            message_id = key.get('id')
            image_data = download_media(message_id)
        
        print(f"📱 From: {sender}")
        print(f"💬 Text: {text_msg}")
        print(f"🖼️ Image: {'Yes' if image_data else 'No'}")
        
        # Process message
        if image_data:
            # Analyze image
            reply = analyze_image(image_data, sender)
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
        return jsonify({'status': 'error', 'message': str(e)}), 500


def download_media(message_id):
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
                    "id": message_id
                }
            },
            "convertToMp4": False
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            base64_data = data.get('base64', '')
            
            # Decode base64 to image
            if base64_data:
                # Remove data URL prefix if present
                if ',' in base64_data:
                    base64_data = base64_data.split(',')[1]
                
                image_bytes = base64.b64decode(base64_data)
                return Image.open(BytesIO(image_bytes))
        
        return None
        
    except Exception as e:
        print(f"❌ Media download error: {e}")
        return None


def analyze_image(image, sender):
    """Analyze skin lesion image"""
    try:
        # Run ABCDE analysis
        results = analyzer.analyze(image)
        
        if results.get('status') == 'rejected':
            return format_rejection(results)
        
        # Get MedGemma interpretation
        medgemma_results = medgemma.analyze_skin_lesion(results)
        
        return format_analysis_reply(results, medgemma_results)
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return f"⚠️ Error saat analisis: {str(e)}"


def handle_text(text):
    """Handle text commands"""
    if text in ['hi', 'halo', 'hello', 'start']:
        return """
🏥 *Selamat Datang di DermaCheck AI!*

Kirim foto tahi lalat/lesi kulit Anda untuk analisis AI.

💬 Perintah:
• HALO - Pesan ini
• TIPS - Panduan foto
• HELP - Bantuan

📸 Kirim foto sekarang!
"""
    
    elif text in ['tips', 'panduan']:
        return """
📸 *TIPS FOTO YANG BAIK*

✅ YANG BENAR:
1. Close-up pada lesi
2. Jarak 10-15 cm
3. Cahaya terang
4. Fokus jelas

❌ YANG SALAH:
1. Terlalu jauh
2. Gelap/blur
3. Lesi tidak jelas

Selamat mencoba! 📷
"""
    
    else:
        return """
📋 *BANTUAN DERMACHECK AI*

Kirim foto lesi kulit untuk analisis.

Perintah:
• HALO - Selamat datang
• TIPS - Panduan foto
• HELP - Bantuan ini

📸 Kirim foto untuk mulai!
"""


def send_message(to, message):
    """Send message via Evolution API"""
    try:
        url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
        
        headers = {
            "apikey": EVOLUTION_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "number": to,
            "text": message
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            print(f"✅ Message sent to {to}")
        else:
            print(f"❌ Send failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Send error: {e}")


def format_analysis_reply(abcde_results, medgemma_results):
    """Format analysis for WhatsApp"""
    risk = abcde_results['risk_level']
    score = abcde_results['total_score']
    
    risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🔴'}.get(risk, '⚪')
    
    msg = f"""
╔══════════════════╗
  HASIL ANALISIS  
╚══════════════════╝

{risk_emoji} *TINGKAT RISIKO: {risk}*
Skor: {score}/11

📊 *DETAIL ABCDE:*

• Asymmetry: {abcde_results['abcde_scores']['asymmetry']}/2
• Border: {abcde_results['abcde_scores']['border']}/2
• Color: {abcde_results['abcde_scores']['color']}/2
• Diameter: {abcde_results['abcde_scores']['diameter']}/2
• Evolution: {abcde_results['abcde_scores']['evolution']}/3

━━━━━━━━━━━━━━━━━━
"""
    
    if risk == 'HIGH':
        msg += "\n🚨 Segera konsultasi dokter kulit dalam 1-2 minggu!"
    elif risk == 'MEDIUM':
        msg += "\n⚠️ Sebaiknya periksa ke dokter dalam 1 bulan."
    else:
        msg += "\n✅ Kemungkinan tidak berbahaya. Tetap pantau!"
    
    msg += "\n\n⚠️ *Disclaimer:* Ini bukan diagnosa medis.\nSelalu konsultasi dokter."
    
    return msg.strip()


def format_rejection(results):
    """Format rejection message"""
    return """
⚠️ *FOTO KURANG JELAS*

Silakan kirim foto ulang dengan:
• Fokus pada lesi
• Jarak 10-15 cm
• Cahaya cukup

Ketik TIPS untuk panduan lengkap.
"""


if __name__ == '__main__':
    print("="*60)
    print("🚀 DermaCheck AI - Evolution API Bot")
    print("="*60)
    print("📱 Waiting for messages...")
    print("🌐 Webhook: http://localhost:5000/webhook")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### **B. Run Bot**

```bash
cd ~/Downloads/hackathon/dermacheck-ai
python whatsapp_bot_evolution.py
```

---

## ✅ STEP 6: Test Complete Flow

### **1. Send Test Message**

From another phone, send WhatsApp to your connected number:
```
Halo
```

**Expected bot reply:**
```
🏥 Selamat Datang di DermaCheck AI!
...
```

### **2. Send Test Image**

Send a photo of a skin lesion.

**Expected:**
- Bot receives image ✅
- Downloads media from Evolution API ✅
- Analyzes with ABCDE + Gemini ✅
- Sends result ✅

---

## 🔍 DEBUGGING

### **Check Evolution API Logs**

```bash
docker logs evolution_api -f
```

### **Check Bot Logs**

Look at terminal where bot is running

### **Verify Instance Status**

```bash
curl -X GET http://localhost:8080/instance/connectionState/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026"
```

### **Test Send Message Manually**

```bash
curl -X POST http://localhost:8080/message/sendText/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "6289699280299",
    "text": "Test from Evolution API!"
  }'
```

---

## 🛠️ MANAGEMENT COMMANDS

### **Stop Services**

```bash
docker-compose down
```

### **Restart Services**

```bash
docker-compose restart
```

### **View Logs**

```bash
docker-compose logs -f
```

### **Delete Instance (Fresh Start)**

```bash
curl -X DELETE http://localhost:8080/instance/logout/dermacheck \
  -H "apikey: dermacheck_ai_secret_key_2026"
```

---

## 📊 EVOLUTION API vs FONNTE

| Feature | Fonnte Free | Evolution API |
|---------|-------------|---------------|
| Image Support | ❌ | ✅ |
| Base64 Media | ❌ | ✅ |
| Self-Hosted | ❌ | ✅ |
| Cost | Free | Free |
| Setup Time | 5 min | 30 min |
| Reliability | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎯 SUCCESS CRITERIA

✅ Evolution API container running
✅ PostgreSQL connected
✅ WhatsApp instance connected
✅ Webhook receiving messages
✅ Python bot processing images
✅ Gemini AI analysis working
✅ Bot replying successfully

---

## 🚀 READY FOR PRODUCTION!

**You now have:**
- ✅ Self-hosted WhatsApp gateway
- ✅ Direct image upload support
- ✅ No external dependencies
- ✅ Full control over infrastructure

**Demo ready!** 🎉
