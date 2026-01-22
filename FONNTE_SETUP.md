# 🚀 Fonnte WhatsApp Setup - Indonesian Solution!

**FINAL MIGRATION: Twilio → Meta → Fonnte**

**Why Fonnte:**
- ✅ No geo-blocking
- ✅ No Meta verification needed
- ✅ Indonesian-focused
- ✅ Simple API
- ✅ Works immediately!

---

## 📋 Quick Setup (5 Minutes!)

### 1. Get Fonnte Account

1. **Go to:** https://fonnte.com/
2. **Register** with Indonesian phone number
3. **Login** to dashboard

### 2. Get API Token

1. In Fonnte dashboard
2. Go to **Settings → API**
3. Copy your **API Token** (looks like: `abc123xyz...`)

### 3. Connect WhatsApp

1. In dashboard, go to **Device**
2. Scan QR code with your WhatsApp
3. Wait for "Connected" status ✅

### 4. Configure .env

Add to your `.env`:

```bash
# Fonnte WhatsApp Bot (Indonesian Gateway)
FONNTE_TOKEN=your_fonnte_api_token_here

# Keep existing
GOOGLE_API_KEY=...
```

### 5. Configure Webhook

1. **Start ngrok:**
   ```bash
   ngrok http 5000
   ```

2. **Copy HTTPS URL:** `https://abc123.ngrok.io`

3. **In Fonnte Dashboard:**
   - Go to **Settings → Webhook**
   - Set Webhook URL: `https://abc123.ngrok.io/webhook`
   - Save ✅

### 6. Start Bot

```bash
python whatsapp_bot_fonnte.py
```

Expected output:
```
==================================================
🚀 DermaCheck AI - Fonnte WhatsApp Bot
==================================================
📱 Waiting for messages from Fonnte...
🌐 Webhook endpoint: http://localhost:5000/webhook
✅ Indonesian-focused! No verification needed!
==================================================
```

### 7. Test It!

**Send to your connected WhatsApp:**

1. Send: `Halo`
2. **Send a photo of lesion!**
3. Wait 15-30 seconds
4. Get AI analysis! ✅

---

## 🔄 Migration Comparison

| Feature | Twilio | Meta Cloud API | Fonnte |
|---------|--------|---------------|---------|
| **Indonesian Support** | ❌ Geo-blocked | ⚠️ Verification issues | ✅ Full support |
| **Setup Complexity** | Medium | High | **Low!** |
| **Verification** | Sandbox | Business verification | **None!** |
| **Cost** | Free sandbox | Free tier | Free tier |
| **Reliability** | ❌ Blocked | ⚠️ Complex | ✅ Simple |

**Winner:** Fonnte! 🏆

---

## 📡 API Differences

### Webhook Format (Fonnte)

**Incoming Message:**
```json
{
  "sender": "628123456789",
  "message": "Halo",
  "message_type": "text"
}
```

**Incoming Image:**
```json
{
  "sender": "628123456789",
  "message_type": "image",
  "file": "https://fonnte.com/path/to/image.jpg"
}
```

### Send Message (Fonnte)

```python
POST https://api.fonnte.com/send

Headers:
  Authorization: YOUR_FONNTE_TOKEN

Body:
  target: "628123456789"
  message: "Your message here"
  countryCode: "62"
```

---

## ✅ Code Changes Summary

**Removed:**
- ❌ `twilio` library
- ❌ TwiML response
- ❌ `request.values` parsing

**Added:**
- ✅ `request.get_json()` parsing
- ✅ Fonnte API integration
- ✅ Simple HTTP POST for sending

**Unchanged (100% Reuse!):**
- ✅ ABCDEAnalyzer logic
- ✅ MedGemmaClient logic
- ✅ Blank detection
- ✅ Message formatting

---

## 🎯 Testing Checklist

- [ ] Fonnte account created
- [ ] WhatsApp connected (QR scanned)
- [ ] API token copied to `.env`
- [ ] Webhook URL configured
- [ ] ngrok running
- [ ] Flask bot running
- [ ] Test message (HALO) works
- [ ] Test image analysis works
- [ ] Indonesian number works! ✅

---

## 💡 Pro Tips

**1. Keep WhatsApp Active:**
- Fonnte uses your actual WhatsApp
- Keep phone connected to internet
- Don't logout from WhatsApp

**2. Webhook Stability:**
- Use ngrok for testing
- Use cloud server for production
- Fonnte will retry failed webhooks

**3. Rate Limits:**
- Free tier: ~1000 messages/day
- Upgrade for unlimited
- Good enough for demo/hackathon!

---

## 🚀 Production Deployment

**For Hackathon:** Current setup perfect! ✅

**For Production:**

1. **Deploy Flask to Cloud:**
   - Heroku / AWS / Google Cloud
   - No ngrok needed

2. **Multiple Devices:**
   - Fonnte supports multiple WhatsApp
   - Load balancing possible

3. **Business Account:**
   - Use WhatsApp Business app
   - Professional profile

---

## ⚠️ Troubleshooting

**Issue:** Webhook not receiving
- **Fix:** Check ngrok URL matches Fonnte webhook setting
- **Fix:** Ensure Fonnte device is "Connected"

**Issue:** Message not sending
- **Fix:** Verify API token is correct
- **Fix:** Check Fonnte dashboard for errors

**Issue:** Image not downloading
- **Fix:** Check file URL in webhook data
- **Fix:** Verify internet connection

**Issue:** WhatsApp disconnected
- **Fix:** Re-scan QR code in Fonnte dashboard
- **Fix:** Keep phone online

---

## 🎬 Demo Narrative (Updated!)

```
"Kita menghadapi banyak masalah teknis:

❌ Twilio → Error 63058 (geo-blocking)
❌ Meta Cloud API → Verification gagal terus

SOLUSI FINAL? FONNTE!

[Show Fonnte dashboard]
✅ Indonesian WhatsApp gateway
✅ No verification needed
✅ Setup 5 menit!

[Live Demo]
1. WhatsApp connected ✅
2. Send photo dari Indonesian number
3. AI analisis real-time
4. Hasil dalam 15 detik!

Fonnte = Praktis untuk pasar Indonesia! 🇮🇩"
```

---

## 📊 Why Fonnte Works

**Technical:**
- Uses unofficial WhatsApp Web API
- No Meta approval needed
- Direct HTTP webhooks
- Simple JSON format

**Business:**
- Indonesian company (Jakarta-based)
- Understands Indonesian market
- Popular for WA automation
- Reliable for demos

**Hackathon Perfect:**
- Fast setup
- No approval delays
- Works immediately
- Demo-ready in 5 min!

---

## 🔗 Resources

- **Fonnte Website:** https://fonnte.com/
- **API Docs:** https://fonnte.com/api
- **Dashboard:** https://fonnte.com/dashboard
- **Support:** support@fonnte.com

---

**READY FOR INDONESIAN DEMO!** 🇮🇩🚀

Simple, reliable, works! Perfect for hackathon! 💯
