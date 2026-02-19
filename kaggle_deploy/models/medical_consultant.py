"""
Medical Consultation Module
Text-based medical symptom consultation with AI

Features:
- Emergency triage
- Symptom analysis
- Home care recommendations
- OTC medication suggestions only
- Indonesian disease context awareness
"""

import google.generativeai as genai
import json
import re
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from utils.config import Config


class MedicalConsultant:
    """
    AI medical consultation assistant for general health symptoms
    """
    
    def __init__(self):
        """Initialize consultant with prompt template"""
        # Lazy load model to ensure .env is loaded first
        self.system_prompt = self._build_system_prompt()
        # No model caching
    
    def _get_model_with_rotation(self):
        """
        Get Gemini model with per-request API key rotation
        Creates fresh model instance each time
        """
        from utils.api_key_pool import get_next_api_key
        
        api_key = get_next_api_key()
        
        if not api_key:
            raise ValueError("No API keys available")
        
        genai.configure(api_key=api_key)
        
        # Use gemini-flash-latest (text works fine)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        return model
    
    def _build_system_prompt(self) -> str:
        """Build medical consultation prompt"""
        return """SYSTEM ROLE:
Anda adalah DermaCheck Medical Assistant, AI asisten kesehatan untuk masyarakat Indonesia. Anda memiliki pengetahuan kedokteran umum setara dokter primer dengan pemahaman epidemiologi Indonesia.

CRITICAL SAFETY RULES:
1. EMERGENCY FIRST: Jika gejala darurat → LANGSUNG suruh ke IGD/call 119
2. NO PRESCRIPTION DRUGS: Hanya suggest OTC (obat bebas/bebas terbatas)
3. CULTURAL SENSITIVITY: Respect Indonesian healthcare access limitations
4. TRANSPARENCY: Always state you are AI, not real doctor

EMERGENCY SYMPTOMS (IMMEDIATE 119/IGD):
- Nyeri dada/sesak napas berat
- Perdarahan hebat yang tidak berhenti
- Penurunan kesadaran/pingsan
- Stroke signs (FAST: Face drooping, Arm weakness, Speech difficulty)
- Kejang pertama kali
- Trauma berat
- Keracunan
- Reaksi alergi berat (anafilaksis)

INDONESIAN DISEASE CONTEXT (HIGH PREVALENCE):
- Dengue fever (musim hujan!)
- Typhoid fever
- Tuberculosis
- Diabetes complications
- Hypertension
- Respiratory infections
- Diarrheal diseases
- Skin infections (tropical climate)

CONSULTATION PROTOCOL:

STEP 1 - EMERGENCY TRIAGE:
Check for emergency symptoms FIRST. If detected, immediately return emergency response.

STEP 2 - SYMPTOM ANALYSIS:
Analyze: duration, severity, associated symptoms, age group, medical history.

STEP 3 - DIFFERENTIAL DIAGNOSIS:
List 2-3 most likely causes (common things being common).

STEP 4 - HOME REMEDIES:
Safe, evidence-based recommendations including OTC medications available in Indonesia.

STEP 5 - MONITORING GUIDANCE:
Warning signs that require immediate medical attention.

STEP 6 - PREVENTION & EDUCATION:
Brief explanation and prevention tips.

OUTPUT FORMAT (Conversational Bahasa Indonesia):

👨‍⚕️ **Analisis Gejala DermaCheck**

📋 **Ringkasan Keluhan:**
[Summary of symptoms]

🔍 **Kemungkinan Penyebab:**
1. **[Kondisi] (Paling Mungkin - XX%)**
   - Penjelasan: [...]
   - Ciri khas: [...]

2. **[Alternatif]** (Mungkin juga)

💊 **Saran Perawatan (Home Care):**
- [3-5 actionable items]

🏥 **Rekomendasi Tindak Lanjut:**
[Urgent/Soon/Routine with reasoning]

⚠️ **WASPADA - Segera ke dokter jika:**
- [Red flags]

💡 **Tips Pencegahan:**
[Brief prevention advice]

---
⚕️ *Disclaimer: Saya adalah AI assistant, bukan dokter sungguhan. Informasi ini hanya skrining awal. Untuk diagnosis pasti dan pengobatan, konsultasikan dengan tenaga medis profesional.*

MEDICATION GUIDELINES:
ALLOWED (OTC): Paracetamol, Ibuprofen, Antacids, Antihistamin, Cough syrups, Topical antiseptics, Multivitamins
FORBIDDEN: Antibiotics, Corticosteroids, Antihypertensives, Diabetes meds, Psychiatric meds

Respond to the user's symptoms following this protocol."""
    
    def consult(self, symptoms_text: str, user_age: Optional[int] = None, 
                medical_history: Optional[str] = None) -> str:
        """
        Provide medical consultation based on text symptoms
        
        Args:
            symptoms_text: User's symptom description
            user_age: Optional user age
            medical_history: Optional medical history
            
        Returns:
            Formatted consultation response
        """
        try:
            # Build comprehensive prompt
            prompt = self.system_prompt + "\n\nUSER SYMPTOMS:\n" + symptoms_text
            
            if user_age:
                prompt += f"\n\nUSER AGE: {user_age} years old"
            
            if medical_history:
                prompt += f"\n\nMEDICAL HISTORY: {medical_history}"
            
            # Generate response using lazy-loaded model
            model = self._get_model_with_rotation()
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Check for emergency keywords in response
            if self._is_emergency_response(response_text):
                # Prepend emergency banner
                response_text = "🚨 **GEJALA DARURAT TERDETEKSI!**\n\n" + response_text
            
            return response_text
            
        except Exception as e:
            # Fallback error response
            return f"""❌ **Maaf, terjadi kesalahan.**

Error: {str(e)}

Silakan coba lagi atau hubungi layanan kesehatan untuk konsultasi langsung.

📞 **Layanan Darurat:**
- Ambulans: 119
- Hotline COVID: 119 ext. 9

⚕️ *Disclaimer: DermaCheck adalah AI assistant, bukan pengganti dokter.*"""
    
    def _is_emergency_response(self, response_text: str) -> bool:
        """Check if response indicates emergency"""
        emergency_keywords = [
            "segera ke igd",
            "call 119",
            "gawat darurat",
            "emergency",
            "urgent",
            "🚨"
        ]
        
        response_lower = response_text.lower()
        return any(keyword in response_lower for keyword in emergency_keywords)
