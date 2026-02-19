# 🤖 Automated Dataset Collection Guide

**NO Manual Downloads!** Everything automated! 🎉

---

## ✅ What You Get

**50 high-quality dermatology cases** from:
- ✅ HAM10000 (Kaggle) - 20 cases
- ✅ PAD-UFES-20 (Kaggle) - 10 cases  
- ✅ ISIC Archive (via API) - 20 cases

**Total time**: ~15-20 minutes (fully automated!)

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Setup Kaggle API** (2 minutes)

```bash
# 1. Get API token
# Go to: https://www.kaggle.com/account
# Scroll to "API" → Click "Create New Token"
# Download kaggle.json

# 2. Setup
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 3. Verify
kaggle datasets list
```

### **Step 2: Run Automated Download** (15-20 min)

```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai

# ONE command to download EVERYTHING!
./scripts/download_all_datasets.sh
```

**What it does**:
1. ✅ Downloads HAM10000 (~1.5GB)
2. ✅ Downloads PAD-UFES-20 (~500MB)
3. ✅ Downloads 20 images from ISIC (via API)
4. ✅ Selects best 50 images
5. ✅ Organizes into folders
6. ✅ Generates metadata JSON

**Output**:
```
data/
├── cases/
│   ├── acne/
│   ├── melanoma/
│   ├── psoriasis/
│   └── ... (10 conditions)
├── cases_database.json
└── raw/ (source datasets)
```

### **Step 3: Done!** ✅

Check your dataset:
```bash
ls -lh data/cases/*/
cat data/cases_database.json | head -20
```

---

## 📂 What Gets Downloaded

### Kaggle Datasets (Automated):
- **HAM10000**: 10,000 dermoscopy images
  - Melanoma, BCC, Nevus, etc.
  - Pre-labeled metadata
  
- **PAD-UFES-20**: 2,298 images
  - Diverse skin tones
  - Brazilian dataset

### ISIC Archive (Automated via API):
- **31 selected images**
  - Melanoma (5)
  - Basal cell carcinoma (5)
  - Actinic keratosis (5)
  - And more...

### Final Curated Set:
- **50 best images** selected automatically
- Quality checked (size, clarity)
- Organized by condition

---

## 🔧 Manual Scripts (If Needed)

### Download only Kaggle:
```bash
python3 scripts/download_kaggle_datasets.py
```

### Download only ISIC:
```bash
python3 scripts/download_isic_archive.py
```

### Re-run curation:
```bash
python3 scripts/curate_best_images.py
```

---

## ⚠️ Troubleshooting

### "Kaggle API not configured"
```bash
# Check if token exists
ls -la ~/.kaggle/kaggle.json

# If not, download from https://www.kaggle.com/account
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### "pip: command not found"
```bash
# Install pip
sudo apt install python3-pip
```

### "Slow download"
- ✅ Normal! HAM10000 is 1.5GB
- ✅ Takes 5-10 min on good connection
- ✅ Script shows progress

---

## 📊 Expected Results

```
✅ HAM10000: 10,015 images extracted
✅ PAD-UFES-20: 2,298 images extracted
✅ ISIC: 31 images downloaded
✅ Curated: 50 best images selected
✅ Metadata: cases_database.json created
```

---

## 🎯 Next Steps

After dataset ready:
1. ✅ Run `generate_ai_analysis.py` (adds MedGemma analysis)
2. ✅ Build Interactive Atlas (Day 7)
3. ✅ Build Comparison Engine (Day 6)

---

**Total Time**: ~20 minutes  
**Manual Work**: ~2 minutes (Kaggle token setup)  
**Automated**: 90%+ 🎉

**Ready to run?** Just execute:
```bash
./scripts/download_all_datasets.sh
```
