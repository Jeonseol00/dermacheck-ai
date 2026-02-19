# 🚀 Kaggle Deployment Guide - DermaCheck AI with Confidence Scores

## 📋 Prerequisites

1. **Kaggle Account** with verified phone number
2. **HuggingFace Account** untuk akses MedGemma
3. **HuggingFace Token** dengan read access
4. **Test images** (dermatology photos) untuk testing

---

## 🔧 Setup Steps

### Step 1: Create HuggingFace Token

1. Buka https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name: `kaggle-medgemma`
4. Type: **Read**
5. Copy token (simpan baik-baik!)

### Step 2: Request MedGemma Access

1. Buka https://huggingface.co/google/medgemma-1.5-4b-it
2. Click **"Agree and access repository"**
3. Accept license terms
4. Tunggu approval (~instant)

### Step 3: Add Token to Kaggle Secrets

1. Buka Kaggle Notebook
2. Klik **Settings** (⚙️) di sidebar kanan
3. Scroll ke **Secrets** section
4. Click **"+ Add a new secret"**
5. Label: `HF_TOKEN`
6. Value: paste HuggingFace token Anda
7. Click **Add**

### Step 4: Enable Kaggle GPU

1. Di Kaggle Notebook, klik **Settings** → **Accelerator**
2. Pilih **GPU T4 x2** (atau **GPU P100** jika available)
3. Internet: **ON** (penting!)

---

## 📝 Kaggle Notebook Structure

Berikut urutan cell yang harus Anda copy-paste:

```
┌─────────────────────────────────────────────────────┐
│ CELL 1: Install Dependencies                        │
│ ⏱️ Runtime: ~2 minutes                              │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ CELL 2: Load MedGemma 1.5 4B                       │
│ ⏱️ Runtime: ~3-4 minutes                            │
│ 💾 VRAM: ~8-9 GB (4-bit quantization)              │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ CELL 3: Confidence Score Components                │
│ ⏱️ Runtime: <1 second                               │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ CELL 4: MedGemma Client                            │
│ ⏱️ Runtime: <1 second                               │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ CELL 5: Test Confidence Extraction                 │
│ ⏱️ Runtime: <1 second                               │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│ CELL 6: Gradio App Launch                          │
│ ⏱️ Runtime: ~5 seconds                              │
│ 🌐 Output: Public Gradio link                       │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Start - Copy This to Kaggle

**Option A: Manual Cell-by-Cell** (RECOMMENDED)
1. Buka file `kaggle_confidence_score_notebook.py` yang baru saja dibuat
2. Copy CELL 1, paste ke Kaggle notebook cell, run
3. Wait sampai selesai (✅ muncul)
4. Ulangi untuk CELL 2, 3, 4, 5, 6

**Option B: Copy Entire File**
1. Copy seluruh isi `kaggle_confidence_score_notebook.py`
2. Create new Kaggle notebook
3. Paste SEMUA code ke satu cell
4. Run cell
5. ⚠️ Ini akan run semua sekaligus - lebih cepat tapi sulit debug jika error

---

## ✅ Verification Checklist

Setelah run semua cells, verify:

### After Cell 1 (Install)
```
✅ Transformers: 4.50.0+
✅ Gradio: 4.0.0+
✅ PyTorch: 2.x
✅ CUDA Available: True
✅ GPU: Tesla T4
```

### After Cell 2 (Load Model)
```
✅ MedGemma 1.5 4B loaded successfully!
✅ Model device: cuda:0
✅ VRAM allocated: ~8-9 GB
✅ VRAM reserved: ~9-10 GB
```

### After Cell 5 (Test)
```
PARSED RESULTS:
✅ Primary: Acne Vulgaris (78%)
✅ Differentials: 3 found
✅ Red Flags: 2 detected
✅ Urgency: ROUTINE
✅ HTML Generated: ~7000+ characters
```

### After Cell 6 (Gradio)
```
Running on public URL: https://xxxxx.gradio.live
```

---

## 🧪 Testing the App

### Test 1: Upload Sample Image

1. Open Gradio link (https://xxxxx.gradio.live)
2. Upload test dermatology image
3. Body location: pilih lokasi (e.g., "Face")
4. Symptom history: tulis gejala (e.g., "Red itchy bumps for 3 days")
5. Click **"🔬 Analyze with Confidence Scores"**

**Expected output (3-5 seconds)**:
- ✅ Confidence visualization dengan progress bars
- ✅ Primary diagnosis dengan purple border
- ✅ 3-4 differential diagnoses
- ✅ Red flags (jika ada)
- ✅ Recommendation dengan urgency level

### Test 2: Verify Confidence Scores

Check:
- ✅ Progress bars menampilkan warna yang benar:
  - Blue (60-79%)
  - Orange (40-59%)
  - Red (<40%)
  - Green (80-100%)
- ✅ Percentages terlihat jelas
- ✅ Rationale ter-display di bawah setiap differential

### Test 3: Check Performance

Buka **"⚙️ Performance Metrics"** accordion:
```
✅ Processing Time: 3000-5000 ms (normal)
✅ Model: MedGemma 1.5 4B
✅ Quantization: 4-bit NF4
✅ Primary Confidence: xx%
✅ Diagnoses Analyzed: 4
```

---

## 🎨 Expected UI Look

**Confidence Visualization Output:**

```
┌─────────────────────────────────────────────────────┐
│ 📊 Differential Diagnosis with Confidence Scores    │
├═════════════════════════════════════════════════════┤
│ ┌─────────────────────────────────────┐            │
│ │ 🎯 PRIMARY: Acne Vulgaris    │  78% │            │
│ │ ███████████████▓░░░░░░░░░     (BLUE)│            │
│ └─────────────────────────────────────┘            │
│                                                     │
│ Alternative Considerations:                         │
│ ┌─────────────────────────────────────┐            │
│ │ 1. Folliculitis          │    62%   │            │
│ │ ████████████▓░░░░░░░░       (BLUE)  │            │
│ │ Rationale: Bacterial...              │            │
│ └─────────────────────────────────────┘            │
│                                                     │
│ ⚠️ RED FLAGS DETECTED                              │
│ • Severe cystic acne may lead to scarring          │
│ • Consider isotretinoin if conventional fails      │
│                                                     │
│ ⚠️ Recommendation: ROUTINE                         │
│ Next Steps: Consult dermatologist for topical...  │
│                                                     │
│ ⚠️ DISCLAIMER: AI-generated estimates...           │
└─────────────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Error: "No module named 'gradio'"
**Fix**: Re-run Cell 1, restart session jika perlu

### Error: "HF_TOKEN not found"
**Fix**: 
1. Check Kaggle Secrets → pastikan label = `HF_TOKEN` (exact)
2. Value harus HuggingFace token, bukan password Kaggle

### Error: "CUDA out of memory"
**Fix**:
1. Restart runtime
2. Pastikan GPU = T4 atau P100 (NOT CPU!)
3. Check quantization config di Cell 2 (harus 4-bit)

### Error: "Repository not found"
**Fix**:
1. Buka https://huggingface.co/google/medgemma-1.5-4b-it
2. Accept license agreement
3. Tunggu 1-2 menit
4. Re-run Cell 2

### Model loads but freezes on generate
**Fix**:
1. Check VRAM: `torch.cuda.memory_allocated(0) / 1024**3`
2. Should be ~8-9 GB, not >14 GB
3. Jika >14 GB, restart dan ensure 4-bit quantization

### Confidence scores not showing
**Fix**:
1. Check raw AI response (expand "📋 Raw AI Response")
2. Pastikan format ada "PRIMARY DIAGNOSIS: ... (Confidence: X%)"
3. Jika tidak ada, model belum generate dengan format yang benar
4. Try dengan symptom history yang lebih detailed

---

## 📊 Performance Benchmarks

Expected performance pada Kaggle T4:

| Metric | Value |
|--------|-------|
| Model Load Time | 3-4 minutes |
| First Inference | 8-12 seconds (cold start) |
| Subsequent | 3-5 seconds |
| VRAM Usage | 8-9 GB |
| Inference Batch | 1 image |
| Max Token | 800 tokens |

---

## 🎯 Competition Submission Tips

Setelah testing berhasil:

1. **Capture Screenshots**
   - UI dengan confidence visualization
   - Example outputs (3-4 different cases)
   - Performance metrics

2. **Record Video Demo**
   - Upload image → analyze → show results
   - Highlight confidence scores
   - Show differential diagnoses
   - Max 3 minutes

3. **Save Kaggle Notebook**
   - Title: "DermaCheck AI - MedGemma Confidence Scores"
   - Make public
   - Add description dengan features

4. **Share Link**
   - Gradio public link: https://xxxxx.gradio.live
   - Kaggle notebook link
   - GitHub repo (optional)

---

## 🚀 Next Steps

After successful deployment:

1. **Test with Real Images**
   - DermNet NZ images
   - Kaggle HAM10000 dataset
   - Your own test cases

2. **Fine-tune (Optional)**
   - Use DermNet data for dermatology focus
   - Improve confidence accuracy

3. **Add Features**
   - PDF report generation
   - Before/after photo comparison
   - Lesion localization with bounding boxes

4. **Prepare Submission**
   - Write 3-page writeup
   - Create 3-minute demo video
   - Submit to Kaggle competition

---

## 📞 Support

Jika stuck:
1. Check error message di Kaggle notebook output
2. Verify GPU is enabled
3. Ensure HF_TOKEN is correct
4. Model access granted on HuggingFace

**Good luck! 🚀**
