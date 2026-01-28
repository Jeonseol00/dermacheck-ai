# 🚀 KAGGLE DEPLOYMENT QUICKSTART

## 📋 Pre-Flight Checklist

### ✅ Tokens Ready:
- **HF_TOKEN**: `YOUR_HF_TOKEN_HERE` (from huggingface.co/settings/tokens)
- **TELEGRAM_BOT_TOKEN**: `YOUR_TELEGRAM_BOT_TOKEN`
- **NGROK_TOKEN**: `YOUR_NGROK_TOKEN`

---

## 🎯 DEPLOYMENT STEPS (5 Minutes)

### Step 1: Upload to Kaggle (2 min)

1. **Go to**: https://www.kaggle.com/code
2. **Click**: "New Notebook"
3. **Upload**: `kaggle_dermacheck_deployment.ipynb`
4. **Or**: Copy-paste cells manually

### Step 2: Configure Kaggle Settings (1 min)

**CRITICAL Settings**:
```
Settings Menu:
├─ Accelerator: GPU T4 ← MUST SELECT!
├─ Internet: ON ← MUST ENABLE!
└─ Persistence: OFF (optional)
```

**How to Access**:
- Click ⚙️ icon (top right)
- Or: File → Notebook Settings

### Step 3: Add Secrets (2 min)

**Kaggle Secrets**: Add-ons → Secrets

Add 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `TELEGRAM_BOT_TOKEN` | `YOUR_TELEGRAM_BOT_TOKEN` |
| `HF_TOKEN` | `YOUR_HF_TOKEN_HERE` |
| `NGROK_TOKEN` | `YOUR_NGROK_TOKEN` |

**IMPORTANT**: Enable "Notebook access" untuk semua secrets!

### Step 4: Update Repository URL

**Find this cell** (Cell 3 in notebook):
```python
REPO_URL = "https://github.com/YOUR_USERNAME/dermacheck-ai.git"
```

**Change to**:
```python
REPO_URL = "https://github.com/titiw/dermacheck-ai.git"  # ← Your actual GitHub
```

> **Note**: Push code to GitHub FIRST before running notebook!

### Step 5: RUN! 🚀

**Execute cells in order**:
1. Run Cell 1-7 sequentially (setup)
2. Cell 8 = Bot starts (runs continuously)
3. Test bot on Telegram
4. Cell 9 = Monitor logs (optional)

**Expected Timeline**:
- Cells 1-5: ~3-4 minutes
- Cell 6 (model test): ~2-3 minutes
- Cell 7 (ngrok): ~10 seconds
- Cell 8 (bot): Runs forever (until stopped)

---

## 🧪 TESTING CHECKLIST

Once bot is running:

### Test 1: Photo Analysis
1. Open Telegram → Search your bot
2. Send `/start`
3. Upload acne photo
4. **Expected**: Analysis dalam 15-20 detik

### Test 2: Text Consultation
1. Type: "sakit kepala sejak 2 hari"
2. **Expected**: Medical advice dalam 8-10 detik

### Test 3: Emergency Detection
1. Type: "nyeri dada kiri menjalar ke lengan"
2. **Expected**: URGENT warning + IGD recommendation

---

## ⚠️ COMMON ISSUES

### Issue 1: "403 Forbidden" saat load model
**Cause**: HF belum approve access ke MedGemma  
**Solution**: 
- Check email untuk approval
- Bisa butuh 1-2 jam
- Coba request ulang di: https://huggingface.co/google/medgemma-4b-it

### Issue 2: "No GPU detected"
**Cause**: Lupa enable GPU  
**Solution**: Settings → Accelerator → GPU T4 → Save → Restart Kernel

### Issue 3: "Secrets not found"
**Cause**: Secrets belum di-enable untuk notebook  
**Solution**: Add-ons → Secrets → Enable "Notebook access"

### Issue 4: Bot tidak respond
**Check**:
```python
# Run in new cell:
import ngrok
tunnels = ngrok.get_tunnels()
print(tunnels)  # Should show active tunnel
```

### Issue 5: "Out of memory"
**Cause**: Quantization tidak jalan  
**Check**: Cell 6 output должен show "Quantized: True"

---

## 📊 PERFORMANCE MONITORING

### Check GPU Usage:
```python
# Run in new cell:
!nvidia-smi
```

### Check Bot Status:
```python
# Run in new cell:
!tail -20 bot.log
```

### Check Memory:
```python
import torch
print(f"Allocated: {torch.cuda.memory_allocated()/1e9:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved()/1e9:.2f} GB")
```

---

## 🎬 DEMO DAY CHECKLIST

**30 Minutes Before Demo**:
- [ ] Start Kaggle notebook
- [ ] Verify all cells run successfully
- [ ] Test bot dengan 1 foto + 1 text
- [ ] Screenshot hasil untuk backup

**During Demo**:
- [ ] Show Kaggle notebook running
- [ ] Show GPU usage (`nvidia-smi`)
- [ ] Point out "MedGemma 4B" in logs
- [ ] Emphasize: Zero cost, HAI-DEF compliant

**After Demo**:
- [ ] Run cleanup cell (Cell 10)
- [ ] Or: Just close notebook

---

## 🔄 RESTART PROCEDURE

Jika notebook crash atau error:

1. **Stop Kernel**: Kernel → Interrupt
2. **Clear Output**: Cell → All Output → Clear
3. **Restart**: Kernel → Restart & Run All
4. **Wait**: ~5-6 minutes untuk reload semua

---

## 💾 BACKUP PLAN

Jika Kaggle completely fails:

**Option A: Google Colab**
- Same notebook works di Colab
- Change: `kaggle_secrets` → `google.colab.userdata`
- Free T4 GPU juga available

**Option B: Local Fallback**
- Revert ke Gemini Flash API
- Explain: "Demo purposes, production uses MedGemma"

---

## 📞 SUPPORT CONTACTS

**HuggingFace Issues**:
- Community: https://huggingface.co/google/medgemma-4b-it/discussions

**Kaggle Issues**:
- Forum: https://www.kaggle.com/discussions

**ngrok Issues**:
- Dashboard: https://dashboard.ngrok.com/

---

**STATUS**: Ready untuk immediate deployment! 🎉  
**NEXT STEP**: Push code ke GitHub, buka Kaggle, upload notebook, RUN!

---

**Pro Tips**:
- Keep notebook tab open during demo
- Pre-test 1 hour before actual demo
- Have backup photos ready on phone
- Screenshot working demo sebagai proof
