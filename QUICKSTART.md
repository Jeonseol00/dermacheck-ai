# ⚡ QUICK START - DermaCheck AI Testing

**Time**: 1 hour | **Date**: Jan 30, 2026

---

## 🚀 ONE-COMMAND INSTALL

```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai
./setup_quick.sh
```

---

## 🔍 ONE-COMMAND TEST

```bash
python test_medgemma_setup.py
```

---

## 🔐 SET HUGGINGFACE TOKEN

```bash
# Get token from: https://huggingface.co/settings/tokens
export HF_TOKEN='hf_xxxxxxxxxxxxxxxxxxxx'

# Accept license: https://huggingface.co/google/medgemma-4b-it
```

---

## 🧠 TEST MEDGEMMA

```bash
python models/medgemma_multimodal_client.py
```

**Expected**: Model loads, SOAP note generates, ~8-10GB GPU memory

---

## 🎨 LAUNCH GRADIO

```bash
python app/gradio_app.py
```

**Expected**: Opens at http://localhost:7860

---

## 📊 CHECK GPU

```bash
nvidia-smi
```

**Need**: 10GB+ free VRAM for MedGemma 4B (4-bit)

---

## 🐛 COMMON FIXES

### No CUDA GPU?
→ **Skip local, use Kaggle T4 (that's the plan anyway!)**

### 403 Forbidden?
→ **Accept MedGemma license on HuggingFace**

### Out of Memory?
→ **Close other GPU apps, check `nvidia-smi`**

### Package errors?
→ **`pip install [package]` one by one**

---

## ✅ SUCCESS = ANY OF THESE:

1. ✅ **BEST**: Everything works locally
2. ✅ **GOOD**: Works but no GPU (use Kaggle)
3. ✅ **OK**: Dependencies install (code runs on Kaggle)

---

## 📞 REPORT FORMAT

```
✅/❌ Dependencies
✅/❌ Environment test
✅/❌ MedGemma loads
✅/❌ Gradio works

Status: READY / PARTIAL / BLOCKED
```

---

**GO! 🔥**
