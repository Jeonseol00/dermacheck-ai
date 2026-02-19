"""
DermaCheck AI - Validation Test Case Database
Phase 3: Clinical Validation Framework

This module defines the structure for comprehensive test cases
combining DermNet NZ, CyberDerm, and clinical literature validation data.

Test Case Distribution:
- Common Conditions: 40 cases (60%)
- Malignancies: 15 cases (22%)
- Emergencies: 5 cases (7%)
- Skin of Color Specific: 20 cases (30% overlap)
Total: 60-70 base cases, expandable to 100+

Fitzpatrick Distribution:
- Type I-II: 20 cases (30%)
- Type III: 20 cases (30%)
- Type IV-VI: 27 cases (40%) - Ensure equity!
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class DifficultyLevel(str, Enum):
    EASY = "easy"           # Classic presentation, common
    MODERATE = "moderate"   # Requires differential
    HARD = "hard"          # Atypical, rare, or complex

class UrgencyLevel(str, Enum):
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class PromptType(str, Enum):
    MASTER = "master_clinical"
    MELANOMA = "melanoma_screening"
    EMERGENCY = "emergency_triage"
    SKIN_OF_COLOR = "skin_of_color"

@dataclass
class TestCase:
    """Single validation test case"""
    
    # Identification
    case_id: str
    condition: str
    difficulty: DifficultyLevel
    
    # Patient Demographics
    age: int
    sex: str
    fitzpatrick_type: int  # 1-6
    
    # Presentation
    location: str
    duration: str
    chief_complaint: str
    symptoms: str
    
    # Clinical Details
    itch_score: int = 0  # 0-10
    pain_present: bool = False
    warmth_present: bool = False
    fever: bool = False
    rapidly_progressive: bool = False
    
    # History
    recent_medications: str = "None"
    known_allergies: str = "None"
    medical_history: str = "None"
    family_history: str = "None"
    recent_travel: str = "None"
    
    # Image
    image_path: str = ""  # Path to test image
    image_source: str = ""  # DermNet NZ, CyberDerm, etc.
    
    # Expected Outputs
    expected_diagnosis: str = ""
    expected_differential: List[str] = None
    expected_confidence_min: int = 0  # Minimum acceptable confidence %
    expected_urgency: UrgencyLevel = UrgencyLevel.ROUTINE
    expected_prompt_type: PromptType = PromptType.MASTER
    
    # Critical Flags
    is_melanoma: bool = False
    is_emergency: bool = False
    is_acral_mucosal: bool = False
    
    # Skin of Color Specific
    expected_soc_adjustments: List[str] = None  # e.g., ["erythema_variation", "PIH_assessment"]
    
    # Special Notes
    clinical_pearls: str = ""
    common_misdiagnoses: List[str] = None
    
    # Validation Criteria
    must_include_in_differential: List[str] = None
    must_not_miss: List[str] = None  # Critical conditions
    
    def __post_init__(self):
        if self.expected_differential is None:
            self.expected_differential = []
        if self.expected_soc_adjustments is None:
            self.expected_soc_adjustments = []
        if self.common_misdiagnoses is None:
            self.common_misdiagnoses = []
        if self.must_include_in_differential is None:
            self.must_include_in_differential = []
        if self.must_not_miss is None:
            self.must_not_miss = []


# ═══════════════════════════════════════════════════════════
# TEST CASE DATABASE
# ═══════════════════════════════════════════════════════════

VALIDATION_TEST_CASES = [
    
    # ═══════════════════════════════════════════════════════════
    # CATEGORY 1: COMMON CONDITIONS (Easy - 20 cases)
    # ═══════════════════════════════════════════════════════════
    
    TestCase(
        case_id="COMMON_001",
        condition="Acne vulgaris",
        difficulty=DifficultyLevel.EASY,
        age=16,
        sex="female",
        fitzpatrick_type=2,
        location="face (cheeks, forehead, chin)",
        duration="2 years, worsening last 6 months",
        chief_complaint="Pimples and oily skin",
        symptoms="Occasional tenderness of larger lesions",
        itch_score=0,
        pain_present=True,
        expected_diagnosis="Acne vulgaris",
        expected_differential=["Rosacea", "Folliculitis", "Perioral dermatitis"],
        expected_confidence_min=80,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.MASTER,
        clinical_pearls="Comedones (blackheads/whiteheads) are pathognomonic. Adolescent age typical.",
        common_misdiagnoses=["Rosacea (older age, no comedones)"]
    ),
    
    TestCase(
        case_id="COMMON_002",
        condition="Atopic dermatitis",
        difficulty=DifficultyLevel.EASY,
        age=8,
        sex="male",
        fitzpatrick_type=3,
        location="antecubital and popliteal fossae",
        duration="Since infancy, chronic with flares",
        chief_complaint="Very itchy rash in elbow and knee creases",
        symptoms="Severe itching, worse at night, dry skin",
        itch_score=9,
        pain_present=False,
        warmth_present=False,
        family_history="Mother has asthma, father has allergic rhinitis",
        expected_diagnosis="Atopic dermatitis",
        expected_differential=["Contact dermatitis", "Nummular eczema", "Psoriasis"],
        expected_confidence_min=85,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.MASTER,
        clinical_pearls="Flexural distribution classic in children. Family atopy history supportive. Severe pruritus hallmark.",
        common_misdiagnoses=["Psoriasis (typically extensor, not as itchy)"]
    ),
    
    TestCase(
        case_id="COMMON_003",
        condition="Psoriasis vulgaris",
        difficulty=DifficultyLevel.EASY,
        age=35,
        sex="male",
        fitzpatrick_type=2,
        location="elbows and knees",
        duration="5 years, stable",
        chief_complaint="Scaly patches on elbows and knees",
        symptoms="Mild itch, cosmetic concern",
        itch_score=3,
        pain_present=False,
        family_history="Father has psoriasis",
        expected_diagnosis="Psoriasis vulgaris",
        expected_differential=["Eczema", "Tinea corporis", "Pityriasis rosea"],
        expected_confidence_min=85,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.MASTER,
        clinical_pearls="Silvery scale on erythematous plaques. Extensor surfaces classic. Positive family history.",
        common_misdiagnoses=["Eczema (more itchy, less well-defined)"]
    ),
    
    TestCase(
        case_id="COMMON_004",
        condition="Tinea corporis",
        difficulty=DifficultyLevel.EASY,
        age=25,
        sex="female",
        fitzpatrick_type=3,
        location="thigh",
        duration="3 weeks",
        chief_complaint="Circular itchy rash on thigh",
        symptoms="Itchy, spreading ring",
        itch_score=6,
        pain_present=False,
        recent_travel="None, but recently joined gym",
        expected_diagnosis="Tinea corporis",
        expected_differential=["Granuloma annulare", "Nummular eczema", "Pityriasis rosea"],
        expected_confidence_min=80,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.MASTER,
        clinical_pearls="Annular (ring-shaped) with central clearing and scale at advancing edge. KOH prep confirmatory.",
        common_misdiagnoses=["Granuloma annulare (no scale, not itchy)"],
        must_include_in_differential=["Tinea corporis"]
    ),
    
    TestCase(
        case_id="COMMON_005",
        condition="Seborrheic dermatitis",
        difficulty=DifficultyLevel.EASY,
        age=45,
        sex="male",
        fitzpatrick_type=2,
        location="scalp, eyebrows, nasolabial folds",
        duration="Chronic, waxing and waning for years",
        chief_complaint="Flaky, greasy scales on scalp and face",
        symptoms="Mild itch, embarrassing flaking",
        itch_score=4,
        expected_diagnosis="Seborrheic dermatitis",
        expected_differential=["Psoriasis", "Atopic dermatitis", "Tinea faciei"],
        expected_confidence_min=80,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.MASTER,
        clinical_pearls="Greasy yellow scale in seborrheic areas (scalp, face). Distribution key.",
        common_misdiagnoses=["Psoriasis (thicker scale, can overlap)"]
    ),
    
    # ═══════════════════════════════════════════════════════════
    # CATEGORY 2: SKIN OF COLOR CASES (Fitzpatrick IV-VI)
    # ═══════════════════════════════════════════════════════════
    
    TestCase(
        case_id="SOC_001",
        condition="Atopic dermatitis (extensor variant)",
        difficulty=DifficultyLevel.MODERATE,
        age=10,
        sex="female",
        fitzpatrick_type=6,
        location="extensor elbows and knees",  # Note: NOT flexural!
        duration="1 year",
        chief_complaint="Bumpy, dark rash on arms and legs",
        symptoms="Very itchy, worse at night",
        itch_score=8,
        pain_present=False,
        expected_diagnosis="Atopic dermatitis",
        expected_differential=["Psoriasis", "Lichen simplex chronicus", "Papular eczema"],
        expected_confidence_min=70,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.SKIN_OF_COLOR,
        expected_soc_adjustments=["erythema_variation", "extensor_distribution", "follicular_prominence", "PIH_prominent"],
        clinical_pearls="Extensor distribution common in darker skin (NOT flexural!). Follicular papules. Violaceous/brown.",
        common_misdiagnoses=["Psoriasis (can be difficult to distinguish in darker skin)"]
    ),
    
    TestCase(
        case_id="SOC_002",
        condition="Post-inflammatory hyperpigmentation (resolved acne)",
        difficulty=DifficultyLevel.MODERATE,
        age=22,
        sex="male",
        fitzpatrick_type=5,
        location="face (cheeks)",
        duration="6 months since acne resolved",
        chief_complaint="Dark spots on face where acne was",
        symptoms="No symptoms, cosmetic concern",
        itch_score=0,
        pain_present=False,
        expected_diagnosis="Post-inflammatory hyperpigmentation (PIH)",
        expected_differential=["Active acne", "Melasma", "Lentigos"],
        expected_confidence_min=85,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.SKIN_OF_COLOR,
        expected_soc_adjustments=["PIH_assessment", "active_vs_resolving"],
        clinical_pearls="CRITICAL: Flat, asymptomatic, uniform color = RESOLVED (PIH only, not active disease!). Patient may think it's worsening but it's actually healed.",
        common_misdiagnoses=["Active acne (PIH is flat, no papules/pustules)"]
    ),
    
    TestCase(
        case_id="SOC_003",
        condition="Psoriasis (violaceous plaques)",
        difficulty=DifficultyLevel.MODERATE,
        age=40,
        sex="female",
        fitzpatrick_type=5,
        location="elbows, knees, scalp",
        duration="3 years",
        chief_complaint="Purple, scaly patches on elbows and knees",
        symptoms="Mild itch, cosmetic concern",
        itch_score=3,
        family_history="Sister has psoriasis",
        expected_diagnosis="Psoriasis vulgaris",
        expected_differential=["Lichen planus", "Atopic dermatitis", "Eczema"],
        expected_confidence_min=75,
        expected_urgency=UrgencyLevel.ROUTINE,
        expected_prompt_type=PromptType.SKIN_OF_COLOR,
        expected_soc_adjustments=["erythema_variation"],
        clinical_pearls="Erythema appears PURPLE/VIOLACEOUS (NOT salmon-pink!). Scale may be gray/white vs silvery.",
        common_misdiagnoses=["May be under-diagnosed if looking for 'red' plaques"]
    ),
    
    # ═══════════════════════════════════════════════════════════
    # CATEGORY 3: MELANOMA / HIGH-RISK PIGMENTED LESIONS
    # ═══════════════════════════════════════════════════════════
    
    TestCase(
        case_id="MELANOMA_001",
        condition="Superficial spreading melanoma",
        difficulty=DifficultyLevel.HARD,
        age=55,
        sex="female",
        fitzpatrick_type=1,
        location="upper back",
        duration="6 months (changing over last 2 months)",
        chief_complaint="Changing mole on back",
        symptoms="None",
        itch_score=0,
        pain_present=False,
        family_history="Mother had melanoma",
        recent_medications="None",
        expected_diagnosis="Melanoma (suspected)",
        expected_differential=["Dysplastic nevus", "Seborrheic keratosis", "Atypical nevus"],
        expected_confidence_min=60,
        expected_urgency=UrgencyLevel.URGENT,
        expected_prompt_type=PromptType.MELANOMA,
        is_melanoma=True,
        clinical_pearls="ABCDE: Asymmetry, Border irregular, Color variegated, Diameter >6mm, Evolution (MOST IMPORTANT!)",
        must_not_miss=["Melanoma"],
        common_misdiagnoses=["Dysplastic nevus (biopsy required to distinguish!)"]
    ),
    
    TestCase(
        case_id="MELANOMA_002",
        condition="Acral lentiginous melanoma",
        difficulty=DifficultyLevel.HARD,
        age=62,
        sex="male",
        fitzpatrick_type=5,  # 🚨 Darker skin + ACRAL = HIGH RISK!
        location="sole of right foot",
        duration="1 year, slowly expanding",
        chief_complaint="Dark spot on bottom of foot",
        symptoms="None",
        itch_score=0,
        pain_present=False,
        family_history="None",
        expected_diagnosis="Acral lentiginous melanoma (suspected)",
        expected_differential=["Plantar wart", "Traumatic hematoma", "Nevus"],
        expected_confidence_min=70,
        expected_urgency=UrgencyLevel.URGENT,  # 🚨 CRITICAL!
        expected_prompt_type=PromptType.MELANOMA,
        is_melanoma=True,
        is_acral_mucosal=True,
        expected_soc_adjustments=["acral_melanoma_screening"],
        clinical_pearls="ALM most common melanoma in people of color. Acral location = URGENT referral! Not sun-related.",
        must_not_miss=["Melanoma", "Acral lentiginous melanoma"],
        common_misdiagnoses=["Plantar wart (has punctate black dots, tender)", "Traumatic hematoma (history of trauma)"]
    ),
    
    TestCase(
        case_id="MELANOMA_003",
        condition="Subungual melanoma (Hutchinson's sign)",
        difficulty=DifficultyLevel.HARD,
        age=58,
        sex="female",
        fitzpatrick_type=6,
        location="thumb nail",
        duration="8 months, pigment spreading to cuticle",
        chief_complaint="Dark line in thumbnail, spreading to skin",
        symptoms="None",
        itch_score=0,
        pain_present=False,
        expected_diagnosis="Subungual melanoma (suspected)",
        expected_differential=["Melanonychia (benign)", "Subungual hematoma", "Fungal infection"],
        expected_confidence_min=80,
        expected_urgency=UrgencyLevel.URGENT,  # 🚨 Hutchinson's sign = CRITICAL!
        expected_prompt_type=PromptType.MELANOMA,
        is_melanoma=True,
        is_acral_mucosal=True,
        expected_soc_adjustments=["acral_melanoma_screening", "hutchinsons_sign"],
        clinical_pearls="Hutchinson's sign (pigment extends to nail fold/cuticle) = near-100% melanoma! URGENT biopsy!",
        must_not_miss=["Melanoma", "Hutchinson's sign"],
        common_misdiagnoses=["Benign melanonychia (doesn't extend to cuticle)"]
    ),
    
    # ═══════════════════════════════════════════════════════════
    # CATEGORY 4: EMERGENCIES (Life-Threatening)
    # ═══════════════════════════════════════════════════════════
    
    TestCase(
        case_id="EMERGENCY_001",
        condition="Stevens-Johnson Syndrome (SJS)",
        difficulty=DifficultyLevel.HARD,
        age=35,
        sex="female",
        fitzpatrick_type=2,
        location="trunk, face, oral mucosa",
        duration="3 days",
        chief_complaint="Widespread painful rash with mouth sores and fever",
        symptoms="Fever, malaise, painful skin, cannot eat due to mouth pain",
        itch_score=0,
        pain_present=True,
        warmth_present=True,
        fever=True,  # 🚨 RED FLAG!
        rapidly_progressive=True,  # 🚨 RED FLAG!
        recent_medications="Trimethoprim-sulfamethoxazole (started 2 weeks ago for UTI)",
        expected_diagnosis="Stevens-Johnson Syndrome",
        expected_differential=["Toxic epidermal necrolysis", "Erythema multiforme major", "DRESS syndrome"],
        expected_confidence_min=70,
        expected_urgency=UrgencyLevel.EMERGENCY,
        expected_prompt_type=PromptType.EMERGENCY,
        is_emergency=True,
        clinical_pearls="Fever + mucosal involvement + targetoid lesions + recent medication = SJS! EMERGENCY ICU admission!",
        must_not_miss=["Stevens-Johnson Syndrome", "Toxic epidermal necrolysis"],
        common_misdiagnoses=["Erythema multiforme (no mucosal involvement, drug trigger)"]
    ),
    
    TestCase(
        case_id="EMERGENCY_002",
        condition="Meningococcemia",
        difficulty=DifficultyLevel.HARD,
        age=19,
        sex="male",
        fitzpatrick_type=2,
        location="trunk, extremities",
        duration="< 12 hours, rapidly worsening",
        chief_complaint="Fever, rash, severe headache, confused",
        symptoms="High fever, severe headache, neck stiffness, rash, confusion",
        itch_score=0,
        pain_present=True,
        warmth_present=True,
        fever=True,  # 🚨 RED FLAG!
        rapidly_progressive=True,  # 🚨 RED FLAG!
        expected_diagnosis="Meningococcemia",
        expected_differential=["Viral exanthem", "Rocky Mountain spotted fever", "Sepsis"],
        expected_confidence_min=65,
        expected_urgency=UrgencyLevel.EMERGENCY,
        expected_prompt_type=PromptType.EMERGENCY,
        is_emergency=True,
        clinical_pearls="Non-blanching petechiae/purpura + fever + neck stiffness/headache = MENINGOCOCCEMIA! Call 911 NOW! IV antibiotics within 1 hour!",
        must_not_miss=["Meningococcemia", "Bacterial meningitis"],
        common_misdiagnoses=["Viral illness (petechiae don't blanch = NOT viral!)"]
    ),
    
    TestCase(
        case_id="EMERGENCY_003",
        condition="Necrotizing fasciitis",
        difficulty=DifficultyLevel.HARD,
        age=50,
        sex="male",
        fitzpatrick_type=3,
        location="leg",
        duration="2 days",
        chief_complaint="Extremely painful red swollen leg, rapidly worsening",
        symptoms="SEVERE pain out of proportion to appearance, fever, feeling very ill",
        itch_score=0,
        pain_present=True,  # SEVERE!
        warmth_present=True,
        fever=True,
        rapidly_progressive=True,
        medical_history="Diabetes mellitus type 2",
        expected_diagnosis="Necrotizing fasciitis (suspected)",
        expected_differential=["Severe cellulitis", "Deep vein thrombosis", "Compartment syndrome"],
        expected_confidence_min=60,
        expected_urgency=UrgencyLevel.EMERGENCY,
        expected_prompt_type=PromptType.EMERGENCY,
        is_emergency=True,
        clinical_pearls="Severe pain OUT OF PROPORTION to appearance = NECROTIZING FASCIITIS! SURGICAL EMERGENCY! Debridement within 6 hours!",
        must_not_miss=["Necrotizing fasciitis"],
        common_misdiagnoses=["Cellulitis (pain proportional, less systemic toxicity)"]
    ),
    
    # ═══════════════════════════════════════════════════════════
    # Add more cases here... (Target: 60-100 total)
    # Categories to add:
    # - Moderate complexity (differential required): 20 cases
    # - Rare conditions: 10 cases
    # - Pediatric cases: 10 cases
    # - Elderly cases: 10 cases
    # - More SOC cases: 10 more
    # ═══════════════════════════════════════════════════════════
]

# ═══════════════════════════════════════════════════════════
# METADATA & STATISTICS
# ═══════════════════════════════════════════════════════════

def get_test_case_stats():
    """Calculate statistics about test case database"""
    total = len(VALIDATION_TEST_CASES)
    
    # By difficulty
    easy = sum(1 for case in VALIDATION_TEST_CASES if case.difficulty == DifficultyLevel.EASY)
    moderate = sum(1 for case in VALIDATION_TEST_CASES if case.difficulty == DifficultyLevel.MODERATE)
    hard = sum(1 for case in VALIDATION_TEST_CASES if case.difficulty == DifficultyLevel.HARD)
    
    # By Fitzpatrick
    fitz_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    for case in VALIDATION_TEST_CASES:
        fitz_counts[case.fitzpatrick_type] += 1
    
    # By urgency
    routine = sum(1 for case in VALIDATION_TEST_CASES if case.expected_urgency == UrgencyLevel.ROUTINE)
    urgent = sum(1 for case in VALIDATION_TEST_CASES if case.expected_urgency == UrgencyLevel.URGENT)
    emergency = sum(1 for case in VALIDATION_TEST_CASES if case.expected_urgency == UrgencyLevel.EMERGENCY)
    
    # Special flags
    melanomas = sum(1 for case in VALIDATION_TEST_CASES if case.is_melanoma)
    emergencies = sum(1 for case in VALIDATION_TEST_CASES if case.is_emergency)
    acral_mucosal = sum(1 for case in VALIDATION_TEST_CASES if case.is_acral_mucosal)
    
    return {
        'total_cases': total,
        'by_difficulty': {'easy': easy, 'moderate': moderate, 'hard': hard},
        'by_fitzpatrick': fitz_counts,
        'by_urgency': {'routine': routine, 'urgent': urgent, 'emergency': emergency},
        'special_flags': {
            'melanomas': melanomas,
            'emergencies': emergencies,
            'acral_mucosal': acral_mucosal
        }
    }

if __name__ == "__main__":
    stats = get_test_case_stats()
    print("DermaCheck AI - Test Case Database Statistics")
    print("=" * 60)
    print(f"Total Cases: {stats['total_cases']}")
    print(f"\nBy Difficulty:")
    print(f"  Easy: {stats['by_difficulty']['easy']}")
    print(f"  Moderate: {stats['by_difficulty']['moderate']}")
    print(f"  Hard: {stats['by_difficulty']['hard']}")
    print(f"\nBy Fitzpatrick Type:")
    for fitz, count in stats['by_fitzpatrick'].items():
        print(f"  Type {fitz}: {count}")
    fitz_iv_vi = sum(stats['by_fitzpatrick'][i] for i in [4, 5, 6])
    print(f"  Total IV-VI: {fitz_iv_vi} ({fitz_iv_vi/stats['total_cases']*100:.1f}%)")
    print(f"\nBy Urgency:")
    print(f"  Routine: {stats['by_urgency']['routine']}")
    print(f"  Urgent: {stats['by_urgency']['urgent']}")
    print(f"  Emergency: {stats['by_urgency']['emergency']}")
    print(f"\nSpecial Flags:")
    print(f"  Melanoma cases: {stats['special_flags']['melanomas']}")
    print(f"  Emergency cases: {stats['special_flags']['emergencies']}")
    print(f"  Acral/mucosal cases: {stats['special_flags']['acral_mucosal']}")
