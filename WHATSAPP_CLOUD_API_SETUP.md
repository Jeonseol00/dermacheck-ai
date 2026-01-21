# 🚀 WhatsApp Cloud API Setup - Indonesian Support!

**Migration dari Twilio → WhatsApp Cloud API**

**Reason:** Fix geo-blocking Error 63058 untuk nomor Indonesia

---

## 🎯 Benefits

✅ **No Geo-Blocking** - Native Meta support  
✅ **Lower Latency** - Direct to WhatsApp servers  
✅ **Better for Indonesia** - Full regional support  
✅ **Production Ready** - Official Meta API  

---

## 📋 Setup Steps

### 1. Create Meta Developer Account

1. **Go to:** https://developers.facebook.com/
2. **Sign up / Login** with Facebook account
3. **Create App:**
   - App Type: **Business**
   - App Name: `DermaCheck AI`
   - Contact Email: Your email

### 2. Add WhatsApp Product

1. In your app dashboard
2. Click **Add Product**
3. Find **WhatsApp** → Click **Set up**
4. Select **WhatsApp Business Account** or create new

### 3. Get Test Phone Number

Meta provides a test number automatically!

1. Go to **WhatsApp → Getting Started**
2. See **Test phone number** (e.g., `+1 555 025 3483`)
3. Add your Indonesian number to **Test number recipients**
4. Click **Send code** to verify your number

### 4. Get Access Token

1. In WhatsApp settings
2. Find **Temporary access token** (valid 24 hours)
3. Copy this token

**For Production:** Generate permanent token

### 5. Get Phone Number ID

1. Still in WhatsApp settings
2. Find **Phone number ID** (under test number)
3. Copy this ID (e.g., `123456789012345`)

### 6. Configure .env

Update your `.env` file:

```bash
# WhatsApp Cloud API (Meta)
WHATSAPP_ACCESS_TOKEN=your_temporary_access_token_here
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_VERIFY_TOKEN=dermacheck_secure_token_2026

# Keep existing
GOOGLE_API_KEY=...
```

### 7. Configure Webhook

1. **Start ngrok:**
   ```bash
   ngrok http 5000
   ```

2. **Copy HTTPS URL:** `https://abc123.ngrok.io`

3. **In Meta Developer Console:**
   - WhatsApp → Configuration → Webhook
   - **Callback URL:** `https://abc123.ngrok.io/webhook`
   - **Verify Token:** `dermacheck_secure_token_2026`
   - Click **Verify and Save**

4. **Subscribe to Webhooks:**
   - Check: `messages`
   - Click **Subscribe**

### 8. Start Bot

```bash
python whatsapp_bot_cloud.py
```

Expected output:
```
==================================================
🚀 DermaCheck AI - WhatsApp Cloud API Bot
==================================================
📱 Waiting for messages from Meta...
🌐 Webhook endpoint: http://localhost:5000/webhook
✅ No geo-blocking! Indonesian support!
==================================================
```

### 9. Test It!

**On your phone (Indonesian number):**

1. Open WhatsApp
2. Message the test number
3. Send: `Halo`
4. **Send a  photo!**
5. Get AI analysis in 15-30 seconds! ✅

---

## 🔄 Migration from Twilio

**Changes:**

| Aspect | Twilio | Cloud API |
|--------|--------|-----------|
| Endpoint | `/whatsapp` (POST) | `/webhook` (GET/POST) |
| Verification | TwiML | Token-based |
| Media | `MediaUrl0` | Image ID → URL |
| Response | TwiML | JSON API call |

**Code Changes:**
- ✅ Webhook verification (GET)
- ✅ JSON payload parsing
- ✅ Image download via Media ID
- ✅ Message sending via Graph API

**Logic Reuse:**
- ✅ ABCDEAnalyzer (same!)
- ✅ MedGemmaClient (same!)
- ✅ Message formatting (same!)
- ✅ Blank detection (same!)

---

## 🎯 Testing Checklist

- [ ] Webhook verified (green checkmark in Meta console)
- [ ] ngrok running
- [ ] Flask bot running
- [ ] Test message received (HALO)
- [ ] Test image analysis working
- [ ] Indonesian number works (no geo-blocking!)

---

## 🚀 Production Deployment

**For Hackathon Demo:** Current setup OK! ✅

**For Real Deployment:**

1. **Get Permanent Token:**
   - App → WhatsApp → System Users
   - Generate permanent token

2. **Get Business Phone Number:**
   - Add verified business number
   - No test restrictions

3. **Webhook Security:**
   - Deploy Flask to cloud (Heroku/AWS)
   - Use HTTPS only
   - Implement request signature verification

---

## ⚠️ Troubleshooting

**Issue:** Webhook verification fails
- **Fix:** Check Verify Token matches `.env`
- **Fix:** Ensure ngrok URL is correct

**Issue:** Message not received
- **Fix:** Check webhook subscribed to `messages`
- **Fix:** Verify your number is in test recipients

**Issue:** Image download fails
- **Fix:** Check access token validity
- **Fix:** Token might be expired (24h limit)

**Issue:** Still geo-blocked?
- **Fix:** You shouldn't be! Cloud API has no restrictions
- **Fix:** Check your number is verified

---

## 📊 Comparison: Twilio vs Cloud API

**Twilio:**
- ❌ Geo-blocking (Error 63058)
- ❌ Sandbox limitations
- ✅ Easy setup (for non-blocked regions)

**Cloud API:**
- ✅ No geo-blocking
- ✅ Native Meta support
- ✅ Better for Indonesia
- ⚠️ Slightly more setup steps

**Verdict:** Cloud API = Better for Indonesian market! 🇮🇩

---

## 💡 Key API Endpoints

**Send Message:**
```
POST https://graph.facebook.com/v18.0/{phone_id}/messages
```

**Get Media URL:**
```
GET https://graph.facebook.com/v18.0/{media_id}
```

**Download Media:**
```
GET {media_url}
Headers: Authorization: Bearer {token}
```

---

## 🎬 Demo Ready!

**Storyline (Updated):**

```
"Kami menghadapi geo-blocking dengan Twilio.
Error 63058 untuk nomor Indonesia.

SOLUSI? Migrasi ke WhatsApp Cloud API!

[Live Demo]
1. Native Meta integration ✅
2. No geo-blocking ✅
3. Indonesian full support! ✅

[Show phone] Kirim foto dari nomor Indonesia
[Show laptop] AI analisis
[Show phone] Hasil dalam 15 detik!

Cloud API = Production-ready untuk pasar Indonesia!"
```

---

## 🔗 Resources

- **Meta Developers:** https://developers.facebook.com/
- **WhatsApp Business Platform:** https://developers.facebook.com/docs/whatsapp
- **Cloud API Docs:** https://developers.facebook.com/docs/whatsapp/cloud-api

---

**READY FOR INDONESIAN USERS!** 🇮🇩🚀

No more geo-blocking! Full market accessibility! 💯
