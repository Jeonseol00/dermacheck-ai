# 🚀 DermaCheck AI - WhatsApp Bot Setup

**Pillar 3: Grassroots Accessibility via WhatsApp**

---

## 📋 Quick Start

### 1. Install Dependencies

```bash
pip install twilio flask pyngrok requests
```

Or:
```bash
pip install -r requirements.txt
```

### 2. Twilio Sandbox Setup

1. **Create Twilio Account:**
   - Go to: https://www.twilio.com/try-twilio
   - Sign up (free trial)

2. **Access WhatsApp Sandbox:**
   - Console: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Note your sandbox number (e.g., `+1 415 523 8886`)
   - Note the join code (e.g., `join happy-cat`)

3. **Get Credentials:**
   - Go to: https://console.twilio.com/
   - Copy **Account SID**
   - Copy **Auth Token**

### 3. Configure Environment

Add to `.env`:

```
# Twilio WhatsApp Bot
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 4. Start ngrok Tunnel

```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 5. Configure Twilio Webhook

1. Go to: Twilio Console → WhatsApp Sandbox Settings
2. Find "WHEN A MESSAGE COMES IN"
3. Set to: `https://abc123.ngrok.io/whatsapp`
4. Method: `POST`
5. Save!

### 6. Run WhatsApp Bot

```bash
python whatsapp_bot.py
```

Expected output:
```
==================================================
🚀 DermaCheck AI - WhatsApp Bot
==================================================
📱 Waiting for messages from Twilio...
🌐 Webhook endpoint: http://localhost:5000/whatsapp
==================================================
```

### 7. Test It!

**On your phone:**

1. Save Twilio sandbox number to contacts
2. Open WhatsApp
3. Send: `join happy-cat` (your join code)
4. Wait for confirmation
5. Send: `Halo`
6. **Send a photo of a lesion!**
7. Wait 15-30 seconds
8. Get AI analysis! ✅

---

## 💬 Commands

**User sends:**
- `HALO` / `HI` / `HELLO` → Welcome message
- `HELP` → Help instructions
- `TIPS` → Photo quality tips
- **[Photo]** → AI analysis!

---

## 🎯 Demo Scenario

**For Competition Presentation:**

```
"Ini Nenek Siti, 65 tahun, desa terpencil.
Dia tidak bisa buka browser web.
TAPI... WhatsApp? EXPERT!

[Live Demo]
1. [Show phone] Nenek kirim foto via WhatsApp
2. [Show laptop] Server terima & analisis
3. [Show phone] Hasil muncul dalam 15 detik!

'Lesi Anda: MEDIUM RISK. Periksa ke dokter dalam 1 bulan.'

Aksesibilitas 100%! Tidak perlu smartphone canggih.
Hanya butuh WhatsApp yang sudah biasa dipakai!"
```

**Wow Factor:** Live WhatsApp analysis! 🔥

---

## 🏗️ Architecture

```
[User's WhatsApp]
       ↓
[Twilio Sandbox]
       ↓ (webhook)
[Flask Server] (localhost:5000)
       ↓
[REUSE: ABCDEAnalyzer] ← Zero duplication!
[REUSE: MedGemmaClient] ← Zero duplication!
       ↓
[Twilio API]
       ↓
[User's WhatsApp] ✅
```

---

## ⚠️ Troubleshooting

**Issue:** "Connection refused"
- **Fix:** Check if Flask is running on port 5000

**Issue:** "Webhook not receiving"
- **Fix:** Verify ngrok URL in Twilio settings
- **Fix:** Check ngrok is still running (restart if needed)

**Issue:** "Analysis taking too long"
- **Fix:** Normal! First analysis can take 30 sec
- **Fix:** Subsequent analyses are faster

**Issue:** "Image not downloading"
- **Fix:** Check internet connection
- **Fix:** Verify Twilio credentials

---

## 🚀 Production Deployment (Future)

For real deployment (not hackathon demo):

1. **Upgrade to WhatsApp Business API:**
   - Business verification required
   - ~$0.005 per message
   - No "join code" needed

2. **Deploy Flask to cloud:**
   - Heroku / AWS / Google Cloud
   - No ngrok needed

3. **Add database:**
   - Store user history
   - Track usage analytics

**For Hackathon:** Sandbox + ngrok = Perfect! ✅

---

## 📊 Features

✅ **Zero Code Duplication** - Reuses existing analyzers
✅ **Elderly-Friendly** - Simple Indonesian messages
✅ **Blank Detection** - Rejects unclear photos
✅ **Real-Time** - Analysis in 15-30 seconds
✅ **Error Handling** - Graceful error messages

---

**READY FOR DEMO!** 🎯

Need help? Check `whatsapp_bot.py` for code comments!
