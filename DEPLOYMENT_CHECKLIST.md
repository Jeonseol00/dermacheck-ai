# 🚀 DEPLOYMENT CHECKLIST - DermaCheck AI Clinical v4

**Target**: Deploy backend v4 ke Kaggle dengan clinical prompt library  
**Timeline**: 30-45 menit  
**Output**: Ngrok URL untuk API testing

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### 1. File Preparation ✅ COMPLETE

**Prompt Library** (`/prompts/`):
- [x] master_clinical_prompt.txt (13 KB, ~170 lines)
- [x] melanoma_screening_prompt.txt (7.2 KB, ~95 lines)
- [x] emergency_triage_prompt.txt (7.3 KB, ~100 lines)
- [x] skin_of_color_prompt.txt (15 KB, ~190 lines)
- [x] README.md (12 KB, ~300 lines)

**Backend Files** (`/kaggle_deploy/`):
- [x] dermacheck_clinical_v4_enhanced.py (12 KB, 380 lines)
- [x] dermacheck_clinical_v4_notebook.ipynb (Jupyter notebook)

**Documentation**:
- [x] KAGGLE_CLINICAL_V4_DEPLOYMENT.md (Complete guide)
- [x] Phase 1, 2, 3 walkthroughs

**Status**: ✅ Semua file sudah siap!

---

## 📋 DEPLOYMENT STEPS (Dilakukan di Kaggle)

### STEP 1: Buat Kaggle Account (Jika Belum Punya)

**Link**: https://www.kaggle.com/account/login?phase=startRegisterTab

1. Sign up dengan Google/Email
2. Verify email
3. Complete profile (username, etc.)

**Status**: [ ] Done / [ ] Already have account

---

### STEP 2: Upload Prompts ke Kaggle Dataset

**A. Prepare Prompts Folder**

Di komputer lokal, pastikan folder ini siap:
```
/home/titiw/Downloads/hackathon/dermacheck-ai/prompts/
├── master_clinical_prompt.txt
├── melanoma_screening_prompt.txt
├── emergency_triage_prompt.txt
├── skin_of_color_prompt.txt
└── README.md
```

✅ **VERIFIED**: Semua 5 files ada!

**B. Create New Dataset di Kaggle**

1. **Go to**: https://www.kaggle.com/datasets
2. **Click**: "New Dataset" button (tombol biru di kanan atas)
3. **Upload files**:
   - Click "Select Files to Upload"
   - Navigate ke: `/home/titiw/Downloads/hackathon/dermacheck-ai/prompts/`
   - Select ALL 5 files (Ctrl+A atau Cmd+A)
   - Click "Open"
   
4. **Dataset Settings**:
   ```
   Title: dermacheck-clinical-prompts
   
   Subtitle: Clinical Prompt Library for DermaCheck AI v4
   
   Description:
   Comprehensive dermatology evaluation prompts integrating:
   - DermNet NZ (2,500+ conditions)
   - LearnDerm (5-step systematic evaluation)
   - Fitzpatrick's Dermatology (Wheel of Diagnosis)
   - Skin of Color Society (Equity protocols)
   - NHS e-LfH (Risk stratification)
   - CyberDerm (Validation framework)
   
   Contains 4 specialized prompts:
   - Master Clinical: Comprehensive evaluation
   - Melanoma Screening: ABCDE + Acral lentiginous detection
   - Emergency Triage: Life-threatening condition detection
   - Skin of Color: Fitzpatrick IV-VI specialized assessment
   
   License: [Pilih sesuai kebutuhan - bisa "Other" atau "CC BY-SA 4.0"]
   
   Visibility: 
   - Public (recommended - bisa di-share)
   - Private (hanya kamu yang bisa akses)
   ```

5. **Click**: "Create" button

6. **Copy Dataset URL**: 
   - Format: `https://www.kaggle.com/datasets/YOUR_USERNAME/dermacheck-clinical-prompts`
   - Save this!

**Status**: [ ] Dataset created
**Dataset URL**: ___________________________________

---

### STEP 3: Get Hugging Face Token

**A. Login ke Hugging Face**

1. **Go to**: https://huggingface.co/
2. **Sign Up / Login**

**B. Create Access Token**

1. **Go to**: https://huggingface.co/settings/tokens
2. **Click**: "New token"
3. **Settings**:
   ```
   Name: dermacheck-kaggle
   Type: Read (cukup read untuk download model)
   ```
4. **Click**: "Generate token"
5. **COPY TOKEN** (format: `hf_xxxxxxxxxxxxxxxxxxxx`)
6. **SAVE SOMEWHERE SAFE** - Token hanya muncul sekali!

**Status**: [ ] Token created
**Token**: `hf_____________________________` (JANGAN SHARE!)

---

### STEP 4: Create Kaggle Notebook

**A. Create New Notebook**

1. **Go to**: https://www.kaggle.com/code
2. **Click**: "New Notebook"
3. **Settings** (Click gear icon ⚙️ di kanan atas):
   
   **Notebook Settings**:
   ```
   Title: DermaCheck AI Clinical v4 - Enhanced
   
   Language: Python
   
   Accelerator: GPU T4 x2 (REQUIRED!)
   
   Internet: ON (REQUIRED for ngrok!)
   
   Environment: Latest available
   ```

4. **Click**: "Save" (di settings)

**Status**: [ ] Notebook created

---

**B. Add Secrets (HF Token)**

1. **In notebook, click**: "Add-ons" menu (di kanan)
2. **Click**: "Secrets" tab
3. **Click**: "+ Add a new secret"
4. **Fill**:
   ```
   Label: HF_TOKEN
   Value: [Paste your Hugging Face token dari Step 3]
   ```
5. **Click**: "Add"

**Status**: [ ] HF_TOKEN added

---

**C. Add Prompts Dataset**

1. **In notebook, click**: "+ Add Data" button (di kanan atas)
2. **Search**: "dermacheck-clinical-prompts" atau search your username
3. **Find your dataset** yang dibuat di Step 2
4. **Click**: "+" button next to dataset name
5. **Verify**: Dataset muncul di "Input" section (kanan bawah)
6. **Path akan jadi**: `/kaggle/input/dermacheck-clinical-prompts/`

**Status**: [ ] Dataset linked

---

### STEP 5: Import Notebook Code

**OPTION A: Copy-Paste (Recommended)**

1. **Open file lokal**: `/home/titiw/Downloads/hackathon/dermacheck-ai/kaggle_deploy/dermacheck_clinical_v4_notebook.ipynb`
2. **Open in text editor** atau Jupyter/VSCode
3. **Copy semua cells**:
   - Cell 1: Verify prompts
   - Cell 2: Install dependencies
   - Cell 3: Load MedGemma
   - Cell 4: Deploy API
4. **Paste ke Kaggle notebook** (one cell at a time)

**OPTION B: Upload .ipynb File**

1. **In Kaggle notebook page**: Click "File" → "Upload Notebook"
2. **Select**: `dermacheck_clinical_v4_notebook.ipynb`
3. **Verify**: All cells imported correctly

**Status**: [ ] Code imported

---

### STEP 6: Verify Setup

**Before running, CHECK**:

1. **GPU Enabled?**
   - Settings → Accelerator → GPU T4 x2 ✅

2. **Internet ON?**
   - Settings → Internet → ON ✅

3. **HF_TOKEN Added?**
   - Add-ons → Secrets → HF_TOKEN exists ✅

4. **Dataset Linked?**
   - Input section shows: dermacheck-clinical-prompts ✅

5. **All Cells Present?**
   - Cell 1: Verify prompts ✅
   - Cell 2: Install dependencies ✅
   - Cell 3: Load model ✅
   - Cell 4: Deploy API ✅

**Status**: [ ] Everything verified

---

### STEP 7: RUN DEPLOYMENT! 🚀

**A. Run Cell 1: Verify Prompts**

1. **Click**: Run button pada Cell 1
2. **Expected Output**:
   ```
   📂 Checking prompt library...
   ✅ Prompts directory found!
   
   Files (5):
     - master_clinical_prompt.txt (13,XXX bytes)
     - melanoma_screening_prompt.txt (7,XXX bytes)
     - emergency_triage_prompt.txt (7,XXX bytes)
     - skin_of_color_prompt.txt (15,XXX bytes)
     - README.md (12,XXX bytes)
   ```

**If ERROR**: "Prompts directory not found"
- **Fix**: Dataset belum linked! Back to Step 4C

**Status**: [ ] Cell 1 passed

---

**B. Run Cell 2: Install Dependencies**

1. **Click**: Run button pada Cell 2
2. **Wait**: ~2 minutes
3. **Expected**: Installation messages, no errors

**Status**: [ ] Cell 2 passed

---

**C. Run Cell 3: Load MedGemma**

1. **Click**: Run button pada Cell 3
2. **Wait**: ~3-5 minutes (downloading model)
3. **Expected Output**:
   ```
   🔄 Loading MedGemma 1.5-4b-it...
   Downloading... [progress bars]
   ✅ Model loaded on cuda:0
   📊 Model size: 4,XXX,XXX,XXX parameters
   ```

**If ERROR**: "HF_TOKEN not found"
- **Fix**: HF_TOKEN secret belum di-add! Back to Step 4B

**Status**: [ ] Cell 3 passed (Model loaded!)

---

**D. Run Cell 4: Deploy API**

1. **Click**: Run button pada Cell 4
2. **Wait**: ~30 seconds
3. **Expected Output**:
   ```
   📚 Loading clinical prompt library...
   ✅ Prompts loaded!
   
   ==================================================================
   🌐 DERMACHECK AI CLINICAL v4 READY
   ==================================================================
   📍 API URL: https://XXXX-XX-XX-XXX-XXX.ngrok-free.app
   ==================================================================
   
   ✨ FEATURES:
      ✅ 4 Specialized Prompts
      ✅ Intelligent Selection
      ✅ Fitzpatrick-Aware
      ✅ Deterministic Generation
   
   🚀 Starting server...
   ```

4. **COPY THE NGROK URL!** 
   - Format: `https://XXXX-XX-XX-XXX-XXX.ngrok-free.app`
   - SAVE THIS - This is your API endpoint!

**Status**: [ ] Cell 4 running
**Ngrok URL**: ___________________________________

---

## 🧪 STEP 8: Test API

**A. Health Check Test**

Open new browser tab:
```
https://YOUR-NGROK-URL.ngrok-free.app/
```

**Expected Response** (JSON):
```json
{
  "app": "DermaCheck AI Clinical",
  "version": "v4-enhanced",
  "status": "ready",
  "prompts": ["master", "melanoma", "emergency", "skin_of_color"],
  "features": ["intelligent_selection", "fitzpatrick_aware", "deterministic"]
}
```

**Status**: [ ] Health check passed

---

**B. Simple Test (Nanti - Setelah Punya Foto)**

**Cara test dengan Python**:

```python
import requests

url = 'https://YOUR-NGROK-URL/analyze'

# Prepare test image
files = {'file': open('test_skin_image.jpg', 'rb')}

# Patient data
data = {
    'age': 25,
    'sex': 'female',
    'fitzpatrick_type': 3,
    'body_location': 'arm',
    'duration': '2 weeks',
    'chief_complaint': 'Itchy rash',
    'symptoms': 'Very itchy',
    'itch_score': 7,
    'pain_present': False,
    'warmth_present': False,
    'fever': False,
    'rapidly_progressive': False,
    'recent_medications': 'None',
    'known_allergies': 'None',
    'medical_history': 'None',
    'family_history': 'None',
    'recent_travel': 'None'
}

# Call API
response = requests.post(url, files=files, data=data)
result = response.json()

# Check result
print(f"Success: {result['success']}")
print(f"Prompt used: {result['metadata']['prompt_used']}")
print(f"\nDiagnosis:\n{result['diagnosis']}")
```

**Status**: [ ] Ready to test (Nanti dengan foto)

---

## 📝 POST-DEPLOYMENT

### Update Frontend API URL

**File**: `/home/titiw/Downloads/hackathon/dermacheck-frontend/lib/api.ts`

**Change line**:
```typescript
// OLD:
const API_URL = 'https://OLD-URL.ngrok-free.app';

// NEW:
const API_URL = 'https://YOUR-NEW-NGROK-URL.ngrok-free.app';
```

**Status**: [ ] Frontend updated

---

### Save Deployment Info

**Record these for future use**:

```
Deployment Date: _________________
Kaggle Notebook: https://www.kaggle.com/code/YOUR_USERNAME/___________
Prompts Dataset: https://www.kaggle.com/datasets/YOUR_USERNAME/dermacheck-clinical-prompts
Ngrok URL: https://_____________________________.ngrok-free.app
HF Token: hf_________________________ (KEEP SECRET!)
```

**Status**: [ ] Info saved

---

## 🚨 TROUBLESHOOTING

### Issue 1: "Prompts directory not found"

**Cause**: Dataset tidak linked ke notebook  
**Fix**: 
1. Click "+ Add Data"
2. Search & add your dataset
3. Re-run Cell 1

---

### Issue 2: "HF_TOKEN not found"

**Cause**: Secret belum ditambahkan  
**Fix**:
1. Add-ons → Secrets
2. Add: HF_TOKEN = your_token
3. Restart kernel
4. Re-run from Cell 3

---

### Issue 3: "CUDA out of memory"

**Cause**: GPU tidak enabled atau insufficient  
**Fix**:
1. Settings → Accelerator
2. Select: GPU T4 x2
3. Restart kernel
4. Re-run

---

### Issue 4: "ngrok connection failed"

**Cause**: Internet tidak enabled  
**Fix**:
1. Settings → Internet → ON
2. Re-run Cell 4

---

### Issue 5: Model loading lambat/timeout

**Cause**: Normal untuk first time (download ~16GB)  
**Fix**: 
- Just wait (bisa 5-10 menit)
- Jangan restart di tengah download!

---

## ✅ FINAL CHECKLIST

Before declaring success:

- [ ] Kaggle account created/logged in
- [ ] Prompts dataset uploaded & public/private
- [ ] HF token created & saved
- [ ] Kaggle notebook created with GPU enabled
- [ ] HF_TOKEN secret added
- [ ] Prompts dataset linked to notebook
- [ ] Cell 1 (Verify) passed
- [ ] Cell 2 (Install) passed
- [ ] Cell 3 (Load model) passed
- [ ] Cell 4 (Deploy) running
- [ ] Ngrok URL obtained & saved
- [ ] Health check test passed (GET /)
- [ ] Frontend API URL updated (optional)

**DEPLOYMENT STATUS**: [ ] COMPLETE ✅

---

## 📊 What's Next?

**Setelah Deploy Berhasil**:

1. **Cari Test Images** (14 jenis penyakit)
2. **Test Manual** dengan foto dari Google Images
3. **Verify Prompt Selection**:
   - Upload foto melanoma → Harus trigger melanoma_screening
   - Upload foto dengan Fitz V-VI → Harus trigger skin_of_color
   - Kasus emergency → Harus trigger emergency_triage
4. **Run Automated Validation** (nanti dengan dataset lengkap)

**Timeline**:
- Deploy sekarang: 30-45 menit
- Test manual: Kapan ada foto
- Full validation: Nanti dengan dataset

---

## 📞 Need Help?

**Dokumentasi**:
- Deployment guide lengkap: `KAGGLE_CLINICAL_V4_DEPLOYMENT.md`
- Phase 2 walkthrough: `phase2_completion_walkthrough.md`

**Kaggle Docs**:
- https://www.kaggle.com/docs/notebooks
- https://www.kaggle.com/docs/datasets

---

*Ready to Deploy!* 🚀  
*Follow steps 1-8 di atas, Good luck!* ✨
