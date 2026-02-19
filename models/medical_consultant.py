"""
Medical Consultation Module - MedGemma Text-Only Version
Text-based medical symptom consultation using MedGemma 1.5

✅ COMPETITION COMPLIANT: Uses ONLY MedGemma (no other models)
✅ MedGemma 1.5 IS MULTIMODAL: Supports text-only input!

This module wraps MedGemmaMultimodalClient for text consultations.

Features:
- Emergency triage
- SOAP note generation
- Text-only consultation (no image)
- Indonesian disease context awareness
- Fully compliant with competition rules
"""

import os
import sys
from typing import Dict, Optional

# Ensure parent directory is in path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


class MedicalConsultant:
    """
    AI medical consultation assistant using MedGemma text-only mode
    
    CRITICAL: Uses MedGemmaMultimodalClient for competition compliance
    """
    
    def __init__(self):
        """Initialize consultant - lazy load MedGemma"""
        self._client = None
        self.system_prompt = self._build_system_prompt()
    
    def _get_medgemma_client(self):
        """
        Lazy load MedGemmaMultimodalClient
        Only loads when first consultation is requested
        """
        if self._client is None:
            try:
                from models.medgemma_multimodal_client import MedGemmaMultimodalClient
                print("📥 Loading MedGemma for text consultation...")
                self._client = MedGemmaMultimodalClient(quantize=True)
                print("✅ MedGemma loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load MedGemma: {e}")
                raise
        
        return self._client
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for medical consultation"""
        return """MEDICAL CONSULTATION SYSTEM - INDONESIAN CONTEXT

Format: SOAP Note (Subjective, Objective, Assessment, Plan)
Language: Bahasa Indonesia
Triage: EMERGENCY / URGENT / ROUTINE
Focus: Primary care, dermatology, general health

Emergency Keywords Detection:
- Chest pain + shortness of breath → EMERGENCY
- Severe bleeding → EMERGENCY  
- Loss of consciousness → EMERGENCY
- Anaphylaxis symptoms → EMERGENCY
- Severe head injury → EMERGENCY

OTC Medications (Indonesia):
- Pain/fever: Paracetamol, Ibuprofen
- Allergies: Cetirizine, Loratadine
- Topical: Calamine, Hydrocortisone 1%
- Stomach: Antasida

Always recommend doctor visit for serious symptoms!
"""
    
    def _detect_emergency(self, symptoms_text: str) -> bool:
        """
        Detect emergency symptoms requiring immediate medical attention
        """
        emergency_keywords = [
            # Cardiovascular
            'nyeri dada', 'chest pain', 'sesak napas berat', 'difficulty breathing',
            
            # Neurological  
            'pingsan', 'loss of consciousness', 'stroke', 'kejang', 'seizure',
            
            # Respiratory
            'tidak bisa bernapas', 'cannot breathe', 'bibir biru', 'blue lips',
            
            # Allergic
            'anafilaksis', 'anaphylaxis', 'bengkak lidah', 'tongue swelling',
            'tenggorokan tertutup', 'throat closing',
            
            # Bleeding
            'perdarahan hebat', 'severe bleeding', 'darah tidak berhenti',
            
            # Abdominal
            'nyeri perut hebat', 'severe abdominal pain', 'muntah darah',
            
            # Trauma
            'cedera kepala berat', 'severe head injury'
        ]
        
        symptoms_lower = symptoms_text.lower()
        
        for keyword in emergency_keywords:
            if keyword in symptoms_lower:
                return True
        
        return False
    
    def consult(self, symptoms_text: str, user_age: Optional[int] = None,
                medical_history: Optional[str] = None) -> str:
        """
        Generate medical consultation response using MedGemma TEXT-ONLY mode
        
        Args:
            symptoms_text: Patient's symptom description
            user_age: Patient age (optional)
            medical_history: Previous medical conditions (optional)
        
        Returns:
            SOAP note formatted consultation response
        """
        
        print(f"📝 Text consultation request: {symptoms_text[:100]}...")
        
        try:
            # Get MedGemma client (lazy load)
            client = self._get_medgemma_client()
            
            # Detect emergency
            is_emergency = self._detect_emergency(symptoms_text)
            
            # Generate SOAP note using MedGemma's built-in method
            # This is TEXT-ONLY - no image parameter!
            soap_result = client.generate_soap_note(
                symptom_text=symptoms_text,
                age=user_age,
                gender=None,  # Not provided in current form
                medical_history=medical_history
            )
            
            # Extract SOAP note text
            if isinstance(soap_result, dict):
                consultation_text = soap_result.get('raw_text', '')
                triage_level = soap_result.get('triage_level', 'ROUTINE')
            else:
                consultation_text = str(soap_result)
                triage_level = 'ROUTINE'
            
            # Override triage if emergency detected
            if is_emergency and 'URGENT' not in triage_level.upper():
                triage_level = 'URGENT'
                # Prepend emergency warning
                consultation_text = f"⚠️ GEJALA DARURAT TERDETEKSI ⚠️\n\n{consultation_text}"
            
            # Ensure TRIAGE level is visible
            if 'TRIAGE:' not in consultation_text:
                consultation_text = f"TRIAGE: {triage_level}\n\n{consultation_text}"
            
            print(f"✅ Consultation generated - Triage: {triage_level}")
            
            return consultation_text
            
        except Exception as e:
            print(f"❌ MedGemma consultation error: {e}")
            # Return fallback response
            return self._generate_fallback_response(symptoms_text, user_age, medical_history)
    
    def _generate_fallback_response(self, symptoms_text: str, user_age: Optional[int],
                                    medical_history: Optional[str]) -> str:
        """
        Generate template response when MedGemma is unavailable
        """
        is_emergency = self._detect_emergency(symptoms_text)
        
        if is_emergency:
            triage = "EMERGENCY"
            assessment = "⚠️ Gejala darurat terdeteksi yang memerlukan pemeriksaan medis SEGERA!"
            plan = """
**TINDAKAN SEGERA:**
- Hubungi 119 (ambulans) SEKARANG atau pergi ke UGD/IGD terdekat
- JANGAN menunda - ini adalah kondisi yang mengancam jiwa
- Jika sendirian, minta bantuan orang lain

**JANGAN:**
- Menunggu sampai pagi
- Mencoba obat rumahan
- Mengemudi sendiri ke rumah sakit
"""
        else:
            triage = "ROUTINE"
            assessment = "Gejala umum yang memerlukan monitoring. Konsultasi dokter untuk diagnosis akurat."
            plan = """
**Perawatan di Rumah:**
- Istirahat cukup
- Minum air putih yang banyak (minimal 8 gelas/hari)
- Monitor perkembangan gejala

**Obat yang Disarankan (OTC):**
- Paracetamol 500mg: untuk demam/nyeri (3x sehari setelah makan)
- Konsultasi apoteker untuk rekomendasi spesifik

**Kapan ke Dokter:**
- Jika gejala memburuk dalam 3-5 hari
- Jika muncul demam tinggi (>38.5°C)
- Jika ada gejala baru yang mengkhawatirkan
- Jika tidak membaik setelah 7 hari
"""
        
        return f"""TRIAGE: {triage}

**S - SUBJEKTIF (Keluhan Pasien):**
{symptoms_text[:300]}{"..." if len(symptoms_text) > 300 else ""}

**O - OBJEKTIF (Pemeriksaan):**
Pemeriksaan fisik diperlukan untuk diagnosis akurat. Dokter akan memeriksa:
- Tanda-tanda vital (tekanan darah, nadi, suhu)
- Inspeksi area yang bermasalah
- Tes diagnostik jika diperlukan

**A - ASSESSMENT (Penilaian):**
{assessment}

**Diagnosis Banding:**
1. Evaluasi medis diperlukan untuk diagnosis pasti
2. Pemeriksaan penunjang mungkin direkomendasikan
3. Konsultasi dengan spesialis jika perlu

**P - PLAN (Rencana Perawatan):**
{plan}

---

**DISCLAIMER:** Ini adalah saran medis AI untuk informasi awal. Untuk diagnosis dan pengobatan akurat, konsultasi dengan dokter diperlukan.

**CATATAN:** Sistem menggunakan mode fallback. Untuk konsultasi lengkap dengan MedGemma, pastikan model sudah dimuat dengan benar.
"""


# Export class
__all__ = ['MedicalConsultant']


# Test function
if __name__ == "__main__":
    print("🧪 Testing MedGemma Text-Only Consultation...\n")
    
    consultant = MedicalConsultant()
    
    # Test case
    response = consultant.consult(
        symptoms_text="Ruam gatal di lengan kanan sejak 3 hari, kemerahan, terasa panas",
        user_age=28
    )
    
    print("=" * 70)
    print("CONSULTATION RESPONSE:")
    print("=" * 70)
    print(response)
    print("=" * 70)
    print("\n✅ Test complete!")
