# DermaCheck AI - Validation Framework Quick Start

**Phase 3**: Clinical Validation & Testing  
**Created**: 2026-02-08  
**Status**: Framework Complete, Ready for Image Collection

---

## 📊 What We Have

### 1. **Test Case Database** (`validation/test_cases.py`)

**15+ Structured Test Cases**:
- ✅ Common conditions (5 cases): Acne, atopic dermatitis, psoriasis, tinea, seborrheic dermatitis
- ✅ Skin of color (3 cases): Atopic (extensor), PIH, psoriasis (violaceous)
- ✅ Melanomas (3 cases): Superficial spreading, acral lentiginous, subungual (Hutchinson's sign)
- ✅ Emergencies (3 cases): SJS, meningococcemia, necrotizing fasciitis

**Each Test Case Includes**:
```python
- Patient demographics (age, sex, Fitzpatrick type)
- Presentation details (location, duration, symptoms)
- Clinical context (medications, history, travel)
- Expected diagnosis & differential
- Expected prompt type
- Expected urgency level
- Critical flags (melanoma, emergency, acral/mucosal)
- Clinical pearls & common misdiagnoses
```

**Current Stats**:
```
Total Cases: 15
By Fitzpatrick:
  Type I-II: 5 cases (33%)
  Type III: 3 cases (20%)
  Type IV-VI: 7 cases (47%) ✅ Good diversity!

By Urgency:
  Routine: 8 cases
  Urgent: 5 cases (melanomas)
  Emergency: 2 cases

Special Flags:
  Melanomas: 3 cases
  Emergencies: 3 cases
  Acral/mucosal: 2 cases
```

### 2. **Automated Validation Runner** (`validation/validation_runner.py`)

**Features**:
- ✅ API integration (calls deployed backend)
- ✅ Automated test execution (all cases)
- ✅ Intelligent evaluation:
  * Primary diagnosis correctness
  * Differential inclusion (top 3)
  * Prompt selection accuracy
  * Urgency appropriateness
  * Melanoma detection (sensitivity)
  * Emergency detection (100% target)
  * Fitzpatrick adjustments verification

**Metrics Calculated**:
```python
1. Overall Accuracy
   - Top-1: >85% target
   - Top-3: >95% target

2. Melanoma Sensitivity
   - >95% target (CRITICAL!)
   - False negatives tracked

3. Emergency Detection
   - 100% target (zero tolerance!)

4. Fitzpatrick Equity
   - Performance by Type (I-VI)
   - Disparity: <5% target

5. Prompt Selection Accuracy
   - Correct routing %

6. Urgency Triage
   - Appropriate urgency: >90%

7. Performance
   - Average response time
```

**Output**:
- Console report (formatted)
- JSON report (`validation_report.json`)
- Pass/fail determination

---

## 🚀 How to Run Validation

### STEP 1: Collect Test Images

**Current Limitation**: Test cases defined, but **need actual medical images**!

**Options**:

**A. DermNet NZ Research Dataset** (BEST):
- 19,500 labeled dermatology images
- Link: https://licensing.edinburgh-innovations.ed.ac.uk/product/dermatology-images-edinburgh-innovation
- Request academic/research license
- Download subset matching our test conditions

**B. Public Medical Image Datasets**:
- ISIC Archive (melanoma images): https://www.isic-archive.com/
- Fitzpatrick17k (skin of color): https://github.com/mattgroh/fitzpatrick17k
- HAM10000: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T

**C. Create Synthetic Cases** (for testing framework):
- Use placeholder images temporarily
- Test validation pipeline
- Replace with real images later

**D. Collaborate with Medical Expert**:
- Ask for anonymized patient images
- Ensure proper consent & HIPAA compliance
- Gold-standard diagnoses confirmed

### STEP 2: Organize Images

```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai/validation/images/

# Create organized structure:
mkdir -p common melanoma emergency soc

# Example naming:
# common/acne_001.jpg
# melanoma/ssm_fitzI_back.jpg
# melanoma/alm_fitzV_sole.jpg
# emergency/sjs_trunk_mucosa.jpg
# soc/atopic_fitzVI_extensor.jpg
```

### STEP 3: Update Test Cases with Image Paths

Edit `validation/test_cases.py`:

```python
TestCase(
    case_id="COMMON_001",
    condition="Acne vulgaris",
    # ... other fields ...
    image_path="validation/images/common/acne_001.jpg",  # ← Add this!
    image_source="DermNet NZ",  # ← And this!
    # ...
)
```

### STEP 4: Deploy Backend to Kaggle

Follow: `KAGGLE_CLINICAL_V4_DEPLOYMENT.md`

1. Upload prompts to Kaggle dataset
2. Run notebook
3. Get ngrok URL

Example: `https://xxxx-xx-xx-xxx-xxx.ngrok-free.app`

### STEP 5: Run Validation

```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai/validation/

# Run validation script
python validation_runner.py https://YOUR-NGROK-URL.ngrok-free.app
```

**Expected Output**:
```
==================================================================
DERMACHECK AI VALIDATION - STARTING
==================================================================
API URL: https://xxxx.ngrok-free.app
Total test cases: 15
Timestamp: 2026-02-08T...

======================================================================
Test Case 1/15
======================================================================
Testing Case: COMMON_001
Condition: Acne vulgaris
Difficulty: easy
Fitzpatrick: 2
======================================================================

🔍 AI Response:
   Prompt used: master_clinical
   Response time: 3.45s
   Diagnosis (first 200 chars): PRIMARY DIAGNOSIS: Acne vulgaris ...

   ✅ Primary diagnosis CORRECT: Acne vulgaris
   ✅ Prompt selection CORRECT: master_clinical
   ✅ Urgency CORRECT: routine

...

==================================================================
DERMACHECK AI - VALIDATION REPORT
==================================================================

==================================================================
OVERALL ACCURACY
==================================================================
Total Cases: 15
Top-1 Accuracy: 86.7% ✅ PASS
Top-3 Accuracy: 93.3% ❌ FAIL (target: >95%)

==================================================================
MELANOMA SENSITIVITY (CRITICAL!)
==================================================================
Total Melanoma Cases: 3
Detected: 3
Sensitivity: 100.0% ✅ PASS

==================================================================
FITZPATRICK EQUITY
==================================================================
Performance by Fitzpatrick Type:
  Type 1: 100.0% (1 cases)
  Type 2: 83.3% (6 cases)
  Type 3: 100.0% (3 cases)
  Type 5: 100.0% (3 cases)
  Type 6: 80.0% (2 cases)

Disparity: 20.0% ❌ FAIL (target: <5%)

...

🎉 VALIDATION PASSED - ALL TARGETS MET!
OR
⚠️  VALIDATION INCOMPLETE - SOME TARGETS NOT MET
   Please iterate on prompts and re-test
```

---

## 📈 Interpreting Results

### Success Criteria:

```
✅ Top-1 Accuracy: > 85%
✅ Top-3 Accuracy: > 95%
✅ Melanoma Sensitivity: > 95%
✅ Emergency Detection: 100%
✅ Fitzpatrick Equity: < 5% disparity
✅ Urgency Triage: > 90%
```

### If Targets Not Met:

**1. Analyze Failures**:
- Check `validation_report.json` for detailed results
- Identify systematic errors (e.g., "Always misses X in Fitz VI")
- Look for patterns by:
  * Fitzpatrick type
  * Difficulty level
  * Condition category
  * Prompt type

**2. Iterate Prompts**:
- Update relevant prompt in `/prompts/`
- Example: If melanoma sensitivity low → enhance `melanoma_screening_prompt.txt`
- If Fitzpatrick disparity high → refine `skin_of_color_prompt.txt`
- If emergency missed → strengthen `emergency_triage_prompt.txt`

**3. Re-Upload & Re-Test**:
- Update prompts on Kaggle dataset
- Restart notebook (pick up new prompts)
- Re-run validation
- Compare metrics

**4. Document Changes**:
- Track prompt version history
- Note what improved/worsened
- Aim for continuous improvement

---

## 🔧 Extending Test Cases

### To Add More Cases:

Edit `validation/test_cases.py`:

```python
# Add to VALIDATION_TEST_CASES list:

TestCase(
    case_id="COMMON_006",  # Increment ID
    condition="Contact dermatitis",
    difficulty=DifficultyLevel.EASY,
    age=30,
    sex="female",
    fitzpatrick_type=3,
    location="hands",
    duration="1 week",
    chief_complaint="Itchy rash on hands after using new soap",
    symptoms="Very itchy, slightly painful",
    itch_score=8,
    pain_present=True,
    warmth_present=False,
    fever=False,
    rapidly_progressive=False,
    recent_medications="None",
    known_allergies="None",
    medical_history="None",
    family_history="None",
    recent_travel="None",
    image_path="validation/images/common/contact_dermatitis_hands.jpg",
    image_source="DermNet NZ",
    expected_diagnosis="Contact dermatitis",
    expected_differential=["Atopic dermatitis", "Dyshidrotic eczema", "Psoriasis"],
    expected_confidence_min=75,
    expected_urgency=UrgencyLevel.ROUTINE,
    expected_prompt_type=PromptType.MASTER,
    clinical_pearls="Sharp cutoff at wrist (where soap contact ended). New product history.",
    common_misdiagnoses=["Atopic (more chronic, flexural)"]
),
```

### Recommended Additions (to reach 60-100 cases):

**Common Conditions (add 15)**:
- Rosacea
- Urticaria
- Contact dermatitis
- Impetigo
- Scabies
- Pityriasis rosea
- Lichen planus
- Vitiligo
- Alopecia areata
- Molluscum contagiosum
- Warts
- Herpes simplex
- Herpes zoster
- Cellulitis (non-emergency grade)
- Folliculitis

**Moderate Complexity (add 10)**:
- Erythema multiforme
- Granuloma annulare
- Lichen sclerosus
- Discoid lupus
- Dermatomyositis
- Sarcoidosis
- Sweet syndrome
- Pyoderma gangrenosum
- Bullous pemphigoid
- Dermatitis herpetiformis

**More SOC Cases (add 10)**:
- Melasma (Fitz IV-VI)
- Central centrifugal cicatricial alopecia (CCCA)
- Pseudofolliculitis barbae
- Traction alopecia
- Keloids
- Acne with prominent PIH
- Psoriasis (purple plaques)
- More ALM cases
- Cellulitis (violaceous presentation)
- Lupus (subtle malar rash in dark skin)

**More Malignancies (add 5)**:
- Basal cell carcinoma
- Squamous cell carcinoma
- Melanoma in situ
- Lentigo maligna
- Nodular melanoma

**Pediatric (add 5)**:
- Diaper dermatitis
- Infantile seborrheic dermatitis
- Hand-foot-mouth disease
- Chickenpox
- Kawasaki disease

---

## 📁 File Structure

```
/validation/
├── images/
│   ├── common/          # Common condition images
│   ├── melanoma/        # Pigmented lesions
│   ├── emergency/       # Life-threatening cases
│   └── soc/             # Skin of color specific
│
├── cases/               # (Future: JSON case files)
│
├── test_cases.py        # ✅ Test case database
├── validation_runner.py # ✅ Automated runner
├── validation_report.json  # Generated after run
└── README.md            # This file
```

---

## 🎯 Current Status

**Phase 3 Progress**:
- [x] Test case structure defined
- [x] 15+ initial cases created
- [x] Automated validation runner
- [x] Metrics calculation framework
- [ ] **Collect test images** ← NEXT STEP!
- [ ] Update test cases with image paths
- [ ] Deploy backend to Kaggle
- [ ] Run initial validation
- [ ] Analyze results
- [ ] Iterate prompts
- [ ] Re-validate until targets met

---

## 🚨 Critical Notes

### For Medical Images:

**ALWAYS**:
- ✅ Obtain proper consent/license
- ✅ Anonymize (remove patient identifiers)
- ✅ Respect HIPAA/privacy laws
- ✅ Verify diagnoses with medical expert
- ✅ Use high-quality, diagnostic images

**NEVER**:
- ❌ Use images without permission
- ❌ Include patient identifiable information
- ❌ Use poor quality/unclear images
- ❌ Guess at diagnoses

### For Melanoma Cases:

**Zero tolerance for false negatives**!
- Any melanoma case missed = CRITICAL FAILURE
- Must achieve >95% sensitivity (ideally 100%)
- Especially important for acral/mucosal in Fitz IV-VI
- Hutchinson's sign = MUST detect (near-100% melanoma)

### For Emergency Cases:

**Must detect ALL emergencies**!
- SJS/TEN = ICU admission
- Meningococcemia = IV antibiotics within 1 hour
- Necrotizing fasciitis = Surgery within 6 hours
- Missing emergency = patient death risk

---

## 📧 Next Actions

1. **Get Image Dataset**:
   - Request DermNet NZ research license OR
   - Download public datasets (ISIC, Fitzpatrick17k) OR
   - Collaborate with medical expert

2. **Populate Test Cases**:
   - Add image_path to all 15 cases
   - Verify diagnoses
   - Expand to 60-100 cases

3. **Deploy & Test**:
   - Follow Kaggle deployment guide
   - Run validation
   - Iterate until targets met

4. **Document Results**:
   - Save validation reports
   - Track prompt versions
   - Prepare for medical expert review (Phase 5)

---

*Validation Framework Complete* ✅  
*Ready for Image Collection & Testing* 📸
