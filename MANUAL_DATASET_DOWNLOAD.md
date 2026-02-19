# 📥 Manual Dataset Download Guide - Terminal Only

**For**: Laptop yang gak kuat automated download  
**Method**: Terminal commands - manual, step-by-step  
**Time**: Download when ready (bisa ditinggal)

---

## 🎯 **Overview**

Kamu akan download **2 datasets** via terminal:
1. **HAM10000** (5.2GB) - ~10 menit
2. **PAD-UFES-20** (3.35GB) - ~7 menit

**Total**: ~8.5GB download

---

## 📋 **STEP-BY-STEP INSTRUCTIONS**

### **PREP: Open Terminal**

```bash
# Go to project directory
cd /home/titiw/Downloads/hackathon/dermacheck-ai

# Create data folder
mkdir -p data/raw
```

---

### **STEP 1: Download HAM10000** (~10 menit)

Copy-paste command ini ke terminal:

```bash
# Download HAM10000
~/.local/bin/kaggle datasets download \
  -d kmader/skin-cancer-mnist-ham10000 \
  -p data/raw

# Cek progress
ls -lh data/raw/
```

**Expected Output**:
```
Downloading skin-cancer-mnist-ham10000.zip to data/raw
100%|████████████████████████████| 5.20G/5.20G [08:30<00:00, 10.4MB/s]
```

**Tips**:
- ✅ Bisa ditinggal (jangan close terminal)
- ✅ Kalau pause: Ctrl+Z
- ✅ Kalau error: Ulangi command yang sama
- ✅ Check size: `du -h data/raw/*.zip`

---

### **STEP 2: Extract HAM10000** (~2 menit)

Setelah download selesai:

```bash
# Extract
cd data/raw
unzip -q skin-cancer-mnist-ham10000.zip -d ham10000/

# Verify
ls -lh ham10000/
echo "✅ HAM10000 extracted!"

# Back to project root
cd ../..
```

**Expected**: Folder `ham10000/` dengan 10,000+ images

---

### **STEP 3: Download PAD-UFES-20** (~7 menit)

```bash
# Download PAD-UFES-20
~/.local/bin/kaggle datasets download \
  -d mahdavi1202/skin-cancer \
  -p data/raw

# Check progress
watch -n 5 "ls -lh data/raw/*.zip"
```

**Expected Output**:
```
Downloading skin-cancer.zip to data/raw
100%|████████████████████████████| 3.35G/3.35G [06:45<00:00, 8.7MB/s]
```

---

### **STEP 4: Extract PAD-UFES-20** (~1 menit)

```bash
# Extract
cd data/raw
unzip -q skin-cancer.zip -d pad_ufes/

# Verify
ls -lh pad_ufes/
echo "✅ PAD-UFES-20 extracted!"

# Back to root
cd ../..
```

---

### **STEP 5: Verify Downloads** (30 detik)

Check semua file ready:

```bash
# Check sizes
du -sh data/raw/ham10000/
du -sh data/raw/pad_ufes/

# Count images
echo "HAM10000 images:"
find data/raw/ham10000 -type f -name "*.jpg" | wc -l

echo "PAD-UFES images:"
find data/raw/pad_ufes -type f \( -name "*.jpg" -o -name "*.png" \) | wc -l
```

**Expected**:
```
HAM10000 images: 10015
PAD-UFES images: 2298
✅ All datasets ready!
```

---

### **STEP 6: Curate Best 50 Images** (~2 menit)

Sekarang select 50 best images:

```bash
# Run curation script
python3 scripts/curate_best_images.py
```

**What It Does**:
- ✅ Selects best quality images
- ✅ Resizes to optimal size
- ✅ Organizes by condition
- ✅ Creates metadata JSON

**Expected Output**:
```
🎨 Starting dataset curation...
📂 Curating HAM10000 images...
   ✅ Selected 30 images from HAM10000
📂 Curating PAD-UFES images...
   ✅ Selected 20 images from PAD-UFES
✅ Metadata saved: data/cases_database.json
   Total cases: 50
✅ Curation complete!
```

---

## 📊 **Final Check**

Verify everything ready:

```bash
# Check final dataset
ls -lh data/cases/*/
cat data/cases_database.json | head -20

# Count curated images
find data/cases -name "*.jpg" | wc -l
```

**Should show**: 50 images organized in folders

---

## ⚠️ **Troubleshooting**

### **"Kaggle command not found"**
```bash
# Use full path
~/.local/bin/kaggle --version
```

### **"Disk space full"**
```bash
# Check space
df -h /home

# Need at least 10GB free
```

### **Download interrupted?**
```bash
# Remove partial file
rm data/raw/*.zip

# Re-run download command
~/.local/bin/kaggle datasets download ...
```

### **Extraction error?**
```bash
# Check if zip complete
unzip -t data/raw/skin-cancer-mnist-ham10000.zip

# If corrupt, delete and re-download
rm data/raw/skin-cancer-mnist-ham10000.zip
```

---

## 🎯 **Timeline**

| Step | Time | Total |
|------|------|-------|
| Download HAM10000 | 10 min | 10 min |
| Extract HAM10000 | 2 min | 12 min |
| Download PAD-UFES | 7 min | 19 min |
| Extract PAD-UFES | 1 min | 20 min |
| Curate 50 images | 2 min | 22 min |

**Total**: ~22 menit (kalau lancar)

---

## ✅ **After Completion**

Setelah selesai semua, beritahu saya:
```
"Dataset ready!"
```

Lalu kita lanjut ke **Next Feature**: Interactive Atlas atau Comparison Engine!

---

## 💡 **Pro Tips**

1. **Download di malam hari** (internet lebih stabil)
2. **Gunakan tmux/screen** (biar bisa detach)
3. **Jangan buka browser** saat download
4. **Check WiFi stabil** (ping 8.8.8.8)

---

**Need Help?** Screenshot error message dan kirim ke saya!

**Ready to start?** Copy command Step 1! 🚀
