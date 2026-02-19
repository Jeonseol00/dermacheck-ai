# DermaCheck Clinical v4 - Kaggle Deployment Guide

**Version**: 4.0  
**Date**: 2026-02-08  
**Status**: Phase 2 Complete - Ready for Deployment

---

## 📋 Pre-Deployment Checklist

### ✅ Phase 1 Complete:
- [x] Master clinical prompt created (4,500 tokens)
- [x] Melanoma screening prompt created (1,800 tokens)
- [x] Emergency triage prompt created (2,200 tokens)
- [x] Skin of color prompt created (3,000 tokens)
- [x] Prompt library README documentation

### ✅ Phase 2 Complete:
- [x] Enhanced backend v4 created
- [x] Intelligent prompt selection logic
- [x] Patient context parameters (15+ fields)
- [x] Deterministic generation maintained
- [x] Kaggle notebook created

---

## 🚀 Deployment Steps

### STEP 1: Upload Prompt Library to Kaggle

1. **Create New Kaggle Dataset**:
   - Go to https://www.kaggle.com/datasets
   - Click "New Dataset"
   - Title: `dermacheck-clinical-prompts`
   - Description: "Clinical prompt library for DermaCheck AI v4 (DermNet NZ + LearnDerm + Fitzpatrick + SOCS + NHS e-LfH + CyberDerm)"

2. **Upload Files**:
   Navigate to `/home/titiw/Downloads/hackathon/dermacheck-ai/prompts/`
   
   Upload ALL 5 files:
   ```
   ✓ master_clinical_prompt.txt (13 KB)
   ✓ melanoma_screening_prompt.txt (7.2 KB)
   ✓ emergency_triage_prompt.txt (7.3 KB)
   ✓ skin_of_color_prompt.txt (15 KB)
   ✓ README.md (12 KB)
   ```

3. **Set Visibility**:
   - Public (recommended for sharing) OR Private (your projects only)

4. **Create Dataset**

---

### STEP 2: Create Kaggle Notebook

1. **Create New Notebook**:
   - Go to https://www.kaggle.com/code
   - Click "New Notebook"
   - Title: `DermaCheck AI Clinical v4 - Enhanced`

2. **Settings**:
   - **GPU**: T4 x2 (required for MedGemma)
   - **Internet**: ON (required for ngrok)
   - **Environment**: Kaggle/Python Docker image

3. **Add Secrets**:
   - Click "Add-ons" → "Secrets"
   - Add secret: `HF_TOKEN` = Your Hugging Face token
   - (Get token from: https://huggingface.co/settings/tokens)

4. **Add Data** (CRITICAL!):
   - Click "Add Data" button
   - Search: your_username/dermacheck-clinical-prompts
   - Click "+" to add
   - Verify it shows in "Input" section

---

### STEP 3: Import Notebook

**Option A: Copy-Paste**
1. Open `/home/titiw/Downloads/hackathon/dermacheck-ai/kaggle_deploy/dermacheck_clinical_v4_notebook.ipynb` locally
2. Copy all cells to your Kaggle notebook
3. Run cells in order

**Option B: Upload File**
1. Download notebook from local machine
2. Upload to Kaggle directly
3. Verify prompts dataset is linked

---

### STEP 4: Run Deployment

1. **Cell 1**: Verify prompts directory
   ```
   Expected output:
   ✅ Prompts directory found!
   Files (5):
     - master_clinical_prompt.txt
     - melanoma_screening_prompt.txt
     - emergency_triage_prompt.txt
     - skin_of_color_prompt.txt
     - README.md
   ```

2. **Cell 2**: Install dependencies (~2 min)

3. **Cell 3**: Load MedGemma model (~3-5 min)
   ```
   Expected output:
   ✅ Model loaded on cuda:0
   ```

4. **Cell 4**: Deploy API (~30 sec)
   ```
   Expected output:
   🌐 DERMACHECK AI CLINICAL v4 READY
   📍 API URL: https://XXXX-XX-XX-XXX-XXX.ngrok-free.app
   ```

5. **Copy ngrok URL** - This is your API endpoint!

---

## 🔗 Update Frontend

### Update API Endpoint

**File**: `/home/titiw/Downloads/hackathon/dermacheck-frontend/lib/api.ts`

```typescript
// Update this line:
const API_URL = 'https://YOUR-NEW-NGROK-URL.ngrok-free.app';
```

---

## 🧪 Testing

### Test 1: Health Check

```bash
curl https://YOUR-NGROK-URL/
```

Expected response:
```json
{
  "app": "DermaCheck AI Clinical",
  "version": "v4-enhanced",
  "status": "ready",
  "prompts": ["master", "melanoma", "emergency", "skin_of_color"],
  "features": ["intelligent_selection", "fitzpatrick_aware", "deterministic"]
}
```

---

### Test 2: Simple Analysis

```python
import requests

url = 'https://YOUR-NGROK-URL/analyze'

files = {'file': open('test_image.jpg', 'rb')}
data = {
    'age': 35,
    'sex': 'female',
    'fitzpatrick_type': 3,
    'body_location': 'arm',
    'duration': '2 weeks',
    'chief_complaint': 'Itchy rash',
    'symptoms': 'Itching',
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

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Success: {result['success']}")
print(f"Prompt used: {result['metadata']['prompt_used']}")
print(f"\nDiagnosis:\n{result['diagnosis']}")
```

Expected: Should select **master_clinical** prompt (Fitz III, no red flags)

---

### Test 3: Melanoma Screening Trigger

```python
data = {
    'age': 50,
    'sex': 'male',
    'fitzpatrick_type': 5,  # Darker skin
    'body_location': 'sole of foot',  # ACRAL!
    'duration': '6 months',
    'chief_complaint': 'Dark spot on foot',
    'symptoms': 'None',
    'itch_score': 0,
    'fever': False,
    'rapidly_progressive': False
    # ... rest of fields
}
```

Expected: Should select **melanoma_screening** prompt (acral location!)

---

### Test 4: Emergency Triage Trigger

```python
data = {
    'age': 28,
    'sex': 'female',
    'fitzpatrick_type': 2,
    'body_location': 'trunk',
    'duration': '2 days',
    'chief_complaint': 'Widespread rash with fever',
    'symptoms': 'Rash, fever, feeling unwell',
    'fever': True,  # 🚨 TRIGGER!
    'rapidly_progressive': True,  # 🚨 TRIGGER!
    'recent_medications': 'Amoxicillin (started 10 days ago)'
    # ... rest
}
```

Expected: Should select **emergency_triage** prompt (fever + rapid!)  
Expected diagnosis should screen for: SJS/TEN, DRESS, meningococcemia

---

### Test 5: Skin of Color Trigger

```python
data = {
    'age': 40,
    'sex': 'female',
    'fitzpatrick_type': 6,  # Very dark skin - TRIGGER!
    'body_location': 'face',
    'duration': '3 months',
    'chief_complaint': 'Facial rash',
    'symptoms': 'Mild itching',
    'itch_score': 3
    # ... rest
}
```

Expected: Should select **skin_of_color** prompt  
Expected features: Erythema color adjustments, PIH assessment

---

## 📊 Validation Strategy

### Prompt Selection Validation:

| Case | Fitz | Location | Complaint | Fever | Expected Prompt |
|------|------|----------|-----------|-------|-----------------|
| 1 | 3 | Arm | Itchy rash | No | master_clinical |
| 2 | 5 | Sole | Dark spot | No | melanoma_screening |
| 3 | 2 | Trunk | Fever + rash | Yes | emergency_triage |
| 4 | 6 | Face | Rash | No | skin_of_color |
| 5 | 4 | Palm | Changing mole | No | melanoma_screening |

Run all 5 cases, verify correct prompt selected in logs!

---

## 🔧 Troubleshooting

### Issue: "Prompts directory not found"

**Solution**:
1. Verify dataset uploaded correctly
2. Check dataset is added to notebook ("Add Data")
3. Verify path: `/kaggle/input/dermacheck-clinical-prompts/`
4. Re-run Cell 1

---

### Issue: "HF_TOKEN not found"

**Solution**:
1. Get token from https://huggingface.co/settings/tokens
2. Add to Kaggle Secrets (Add-ons → Secrets)
3. Name must be exactly: `HF_TOKEN`
4. Restart kernel

---

### Issue: "CUDA out of memory"

**Solution**:
1. Verify GPU is enabled (Settings → Accelerator → GPU T4 x2)
2. Restart kernel
3. If persists, reduce `max_new_tokens` from 2048 to 1024

---

### Issue: "ngrok connection failed"

**Solution**:
1. Verify internet is enabled (Settings → Internet → ON)
2. Check ngrok token is valid
3. Try re-running Cell 4

---

## 📝 Backend vs Frontend Parameters

### Backend REQUIRES (15 parameters):

```python
{
    'age': int,
    'sex': str,
    'fitzpatrick_type': int (1-6),
    'body_location': str,
    'duration': str,
    'chief_complaint': str,
    'symptoms': str,
    'itch_score': int (0-10),
    'pain_present': bool,
    'warmth_present': bool,
    'fever': bool,
    'rapidly_progressive': bool,
    'recent_medications': str,
    'known_allergies': str,
    'medical_history': str,
    'family_history': str,
    'recent_travel': str
}
```

### Frontend MUST Collect:

**Minimum (Phase 4 task)**:
- Age, sex, Fitzpatrick type selector
- Body location, duration
- Chief complaint (auto-generate or user input)
- Fever yes/no (red flag screening)

**Full (Recommended)**:
- All 15+ parameters above for best AI performance

---

## 🎯 Next Steps (Phase 3)

After successful deployment:

1. **Create test case database** (50-100 cases)
2. **Run validation suite** (measure accuracy)
3. **Iterate prompts** based on errors
4. **Document performance** metrics

---

## ✅ Deployment Checklist

Before going live:

- [ ] Prompts dataset uploaded to Kaggle
- [ ] Kaggle notebook created with GPU enabled
- [ ] HF_TOKEN secret added
- [ ] Dataset linked to notebook
- [ ] All cells run successfully
- [ ] ngrok URL obtained
- [ ] Frontend updated with new API URL
- [ ] Health check passed (`GET /`)
- [ ] Test analysis successful (`POST /analyze`)
- [ ] Prompt selection logic verified (5 test cases)
- [ ] Deterministic generation confirmed (same image → same result)

---

*Deployment Guide Complete* ✅  
*Ready for Phase 3: Validation & Testing* 🚀
