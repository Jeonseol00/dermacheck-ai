# DermaCheck AI - Clinical Prompt Library

**Version**: 4.0 (Clinical Research Integration)  
**Created**: 2026-02-08  
**Status**: Phase 1 Complete

---

## 📚 Overview

This prompt library contains evidence-based clinical evaluation templates that combine expertise from:

1. **DermNet NZ** - 2,500+ conditions, standardized clinical structure
2. **LearnDerm** - 5-step systematic framework
3. **Fitzpatrick's Dermatology** - Wheel of Diagnosis methodology
4. **NHS e-Learning for Healthcare** - Clinical scenarios & risk stratification
5. **CyberDerm** - Validation framework & diverse skin representation
6. **Skin of Color Society** - Equity protocols & bias reduction

---

## 📂 Prompt Files

### 1. **master_clinical_prompt.txt** (Main Evaluation)

**Purpose**: Comprehensive systematic dermatology evaluation  
**Use When**: Standard dermatology consultation, complete workup needed  
**Framework**: LearnDerm 5 steps + Fitzpatrick Wheel + SOCS adjustments

**Key Features**:
- Step-by-step systematic evaluation
- Fitzpatrick-aware color interpretation
- Differential diagnosis generation
- Risk stratification (NHS e-LfH)
- Management recommendations
- Safety disclaimers

**Input Parameters Required**:
```
- age
- sex
- fitzpatrick_type (1-6)
- body_location
- duration
- symptoms
- itch_score (0-10)
- pain_present (yes/no)
- warmth_present (yes/no)
- systemic_symptoms
- recent_medications
- known_allergies
- medical_history
- family_history
- recent_travel
```

**Token Count**: ~4,500 tokens

---

### 2. **melanoma_screening_prompt.txt** (Focused Screening)

**Purpose**: Melanoma risk assessment for pigmented lesions  
**Use When**: Patient presents with mole/pigmented lesion concern  
**Framework**: ABCDE criteria + Acral lentiginous melanoma (skin of color)

**Key Features**:
- ABCDE criteria scoring (0-6 scale)
- Acral/mucosal location high-risk assessment
- Hutchinson's sign detection (subungual melanoma)
- Dermoscopy clues (if available)
- Zero-tolerance false negative approach
- Fitzpatrick IV-VI specific patterns

**Input Parameters Required**:
```
- age
- fitzpatrick_type
- location (⚠️ CRITICAL for acral/mucosal detection!)
- duration
- evolution_description (changes over time)
- family_hx_melanoma
- personal_hx (previous skin cancer)
- sun_exposure
```

**Output**:
- ABCDE score (0-6)
- Melanoma suspicion level (Low/Moderate/High)
- Urgency (Routine monitor / Refer 2-4 weeks / URGENT 1-2 weeks / EMERGENCY)
- Acral/mucosal flag
- Hutchinson's sign detection

**Token Count**: ~1,800 tokens

---

### 3. **emergency_triage_prompt.txt** (Life-Threatening Detection)

**Purpose**: Rapid triage for dermatological emergencies  
**Use When**: Patient has rash + systemic symptoms OR rapidly progressive condition  
**Framework**: NHS e-LfH red flag protocols

**Key Features**:
- Life-threatening condition detection:
  * Stevens-Johnson Syndrome (SJS) / Toxic Epidermal Necrolysis (TEN)
  * Meningococcemia
  * Necrotizing fasciitis
  * Rocky Mountain Spotted Fever
  * DRESS syndrome
- Fever + rash assessment
- Mucosal involvement screening
- Pain disproportionate to appearance (necrotizing fasciitis red flag!)
- Non-blanching purpura detection
- Triage decision tree

**Input Parameters Required**:
```
- age
- duration
- progression_rate (stable/slowly worsening/RAPIDLY worsening)
- fever_temp
- systemic_symptoms (chills, malaise, headache, neck_stiffness, confusion, dyspnea, dysphagia)
- severe_pain (disproportionate)
- recent_meds (1-3 weeks)
- oral_lesions
- eye_involvement
- genital_lesions
- blistering
- skin_detachment
- purpura (non-blanching)
- body_surface_area (% if skin peeling)
```

**Output**:
- Urgency level: ROUTINE / URGENT SAME DAY / **EMERGENCY - ED NOW**
- Suspected condition(s)
- Red flags present
- Time-sensitive actions
- 911/ED criteria

**Token Count**: ~2,200 tokens

---

### 4. **skin_of_color_prompt.txt** (Fitzpatrick IV-VI Specialized)

**Purpose**: Specialized evaluation for darker skin tones  
**Use When**: Patient is Fitzpatrick Type IV, V, or VI  
**Framework**: Skin of Color Society protocols + DermNet NZ diversity guidelines

**Key Features**:
- Erythema color variations (purple/violaceous/grayish, NOT red!)
- Alternative diagnostic cues (warmth, texture, elevation, symptoms)
- Post-inflammatory hyperpigmentation (PIH) assessment
- Acral lentiginous melanoma screening
- Central centrifugal cicatricial alopecia (CCCA) detection
- Keloid/hypertrophic scar risk counseling
- Severity scoring bias correction (don't underestimate!)
- Cultural considerations (hair care, skin lightening products)

**Input Parameters Required**:
```
- fitzpatrick_type (4, 5, or 6)
- ethnicity
- chief_complaint
- body_location (⚠️ acral sites critical!)
- duration
- (all standard clinical parameters)
```

**Output**:
- Fitzpatrick-adjusted diagnosis
- Erythema presentation description (actual colors seen)
- PIH status (active disease / resolving / pure PIH)
- Acral/mucosal melanoma risk
- Severity (adjusted for non-erythema factors)
- Skin of color counseling points
- PIH prevention strategies
- Keloid risk at site

**Token Count**: ~3,000 tokens

---

## 🎯 Usage Guide

### Selecting the Right Prompt:

```
IF patient_concern == "mole/pigmented lesion":
    USE melanoma_screening_prompt.txt
    
ELIF systemic_symptoms OR rapidly_progressive:
    USE emergency_triage_prompt.txt
    CHECK if requires 911/ED IMMEDIATELY
    
ELIF fitzpatrick_type >= 4:
    USE skin_of_color_prompt.txt
    (Includes all standard evaluation + SOC adjustments)
    
ELSE:
    USE master_clinical_prompt.txt
    (Comprehensive standard evaluation)
```

### Combining Prompts:

**Example 1**: Fitzpatrick VI patient with pigmented lesion on sole
```
PRIMARY: melanoma_screening_prompt.txt
SUPPLEMENTAL: skin_of_color_prompt.txt (Section: Acral Lentiginous Melanoma)
→ HIGH RISK scenario! URGENT referral threshold!
```

**Example 2**: Fitzpatrick III patient with fever + rash + new medication
```
PRIMARY: emergency_triage_prompt.txt
→ Screen for SJS/TEN, DRESS
IF NOT emergency:
  SECONDARY: master_clinical_prompt.txt
```

---

## 🔧 Integration Instructions

### For Backend (Kaggle/FastAPI):

```python
import os

# Load prompts
MASTER_PROMPT = open("/kaggle/input/prompts/master_clinical_prompt.txt").read()
MELANOMA_PROMPT = open("/kaggle/input/prompts/melanoma_screening_prompt.txt").read()
EMERGENCY_PROMPT = open("/kaggle/input/prompts/emergency_triage_prompt.txt").read()
SOC_PROMPT = open("/kaggle/input/prompts/skin_of_color_prompt.txt").read"().read()

def select_prompt(patient_data):
    """
    Route to appropriate prompt based on presentation
    """
    
    # Emergency triage first!
    if patient_data["fever"] or patient_data["rapidly_progressive"]:
        return EMERGENCY_PROMPT
    
    # Melanoma screening for pigmented lesions
    if "mole" in patient_data["chief_complaint"].lower() or \
       "changing" in patient_data["chief_complaint"].lower() or \
       patient_data["location"] in ["palm", "sole", "nail", "oral", "genital"]:
        prompt = MELANOMA_PROMPT
        # Add SOC supplement if Fitz IV-VI
        if patient_data["fitzpatrick_type"] >= 4:
            prompt += "\n\n" + extract_section(SOC_PROMPT, "ACRAL LENTIGINOUS MELANOMA")
        return prompt
    
    # Skin of color specialized
    if patient_data["fitzpatrick_type"] >= 4:
        return SOC_PROMPT
    
    # Default: comprehensive evaluation
    return MASTER_PROMPT

def generate_diagnosis(image, patient_data):
    """
    Generate AI diagnosis with appropriate prompt
    """
    
    prompt_template = select_prompt(patient_data)
    
    # Fill in patient data
    prompt = prompt_template.format(**patient_data)
    
    # Generate (deterministic!)
    response = model.generate(
        inputs=prompt,
        max_length=2048,
        do_sample=False,  # Consistency!
        temperature=0.0
    )
    
    return response
```

### For Frontend:

**Patient Intake Form** should collect:

**Basic Demographics**:
- Age
- Sex*

**Fitzpatrick Skin Type** (Visual selector with example images):
- Type I-VI with photos

**Lesion Details**:
- Location (dropdown with acral/mucosal flagged!)
- Duration
- Symptoms (itch 0-10, pain yes/no, warmth yes/no)

**Red Flag Screening**:
- Fever? (🚨 triggers emergency prompt)
- Rapidly worsening? (🚨)
- Recent medication? (⚠️ drug reaction risk)
- Mole changing? (→ melanoma screening)

**Medical History**:
- Medications
- Allergies
- Chronic conditions
- Family history (skin cancer, melanoma)
- Recent travel

---

## 📊 Validation & Testing

### Test Cases Required:

**Common Conditions** (60 cases):
- Acne, eczema, psoriasis, tinea, cellulitis, etc.
- Balanced across Fitzpatrick I-VI

**Malignancies** (20 cases):
- Melanoma (including ALM on acral sites!)
- Basal cell carcinoma
- Squamous cell carcinoma

**Emergencies** (10 cases):
- SJS/TEN
- Meningococcemia
- Necrotizing fasciitis

**Skin of Color** (30 cases):
- Fitzpatrick IV-VI representations
- PIH scenarios (active vs resolving)
- ALM on acral/mucosal sites
- CCCA, keloids

**Total**: 120+ cases minimum

### Success Metrics:

```
✅ Top-1 Accuracy: > 85%
✅ Top-3 Accuracy: > 95%
✅ Melanoma Sensitivity: > 95% (CRITICAL!)
✅ Melanoma Specificity: > 90%
✅ Fitzpatrick Equity: < 5% disparity
✅ Emergency Detection: 100%
✅ Appropriate Urgency Triage: > 90%
```

---

## 🔄 Version History

**v4.0** (2026-02-08) - Clinical Research Integration
- Created comprehensive prompt library
- Integrated 6 expert frameworks
- Fitzpatrick-aware evaluation - Acral lentiginous melanoma protocols
- Emergency triage prompts
- Skin of color specialized evaluation

**v3.0** (Previous) - Deterministic generation, English-only
**v2.0** (Previous) - Bilingual support
**v1.0** (Initial) - Basic MedGemma prompts

---

## 📝 Maintenance

### When to Update Prompts:

1. **Medical Expert Feedback**: Systematic errors identified
2. **Validation Results**: Accuracy < targets
3. **Clinical Guidelines Update**: New evidence-based recommendations
4. **DermNet NZ Updates**: New conditions, treatment changes
5. **Fitzpatrick Equity Issues**: Performance disparity across skin tones

### Update Process:

1. Identify specific issue (e.g., "Under-diagnosing cellulitis in Fitz V-VI")
2. Research correction (SOCS protocols, DermNet NZ)
3. Update relevant prompt section
4. Test on validation cases
5. Measure impact on metrics
6. Document change in version history

---

## 🚨 Critical Safety Reminders

### For ALL Prompts:

1. **Zero tolerance for melanoma false negatives**
   - When in doubt → REFER!
   - Acral/mucosal + pigmentation in Fitz IV-VI = URGENT

2. **Fever + rash = URGENT until proven otherwise**
   - Screen for SJS, TEN, meningococcemia, DRESS

3. **Severe pain > appearance = Necrotizing fasciitis**
   - SURGICAL EMERGENCY!

4. **Always include disclaimers**:
   - AI is preliminary assessment only
   - Does NOT replace in-person evaluation
   - Seek medical care if concerned

5. **Fitzpatrick adjustments are MANDATORY**
   - Do not apply lighter-skin criteria to darker skin!
   - Adjust erythema interpretation
   - Assess PIH appropriately

---

## 📧 Contact & Contribution

For medical expert review, clinical feedback, or validation collaboration:
- Medical Expert: [TBD - your collaborating physician]
- Technical Lead: [Your name]
- Project: DermaCheck AI Clinical v4

---

*Prompt Library Complete* ✅  
*Evidence-Based, Equity-Focused, Safety-First* 🎯
