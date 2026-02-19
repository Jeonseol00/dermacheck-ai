"""
Multi-Condition Dermatology Analyzer
Expanded from melanoma-only to comprehensive skin condition detection

Supports:
- Melanoma (ABCDE method - existing)
- Acne vulgaris
- Eczema/Dermatitis
- Fungal infections (tinea, candidiasis)
- Psoriasis
- Vitiligo
- General skin lesions

Uses production-grade Gemini prompts with medical safety layers
"""

import google.generativeai as genai
from PIL import Image
import json
import re
from typing import Dict, Optional
from utils.config import Config


class MultiDermaAnalyzer:
    """
    Multi-condition dermatology analyzer using enhanced AI prompts
    """
    
    def __init__(self):
        """Initialize analyzer with prompt template"""
        # Don't configure API here - wait until analyze_photo is called
        # This ensures .env is loaded first
        self.system_prompt = self._build_system_prompt()
        # No model caching - create fresh per request
    
    def _get_model_with_rotation(self):
        """
        Get Gemini model with per-request API key rotation
        
        IMPORTANT: Creates NEW model instance with fresh API key each time
        This ensures proper rotation and avoids quota exhaustion
        """
        from utils.api_key_pool import get_next_api_key
        
        # Get next key from pool (rotates)
        api_key = get_next_api_key()
        
        if not api_key:
            raise ValueError("No API keys available in pool")
        
        # Configure API with this key
        genai.configure(api_key=api_key)
        
        # Create model instance with current key
        # Use gemini-flash-latest (confirmed working with images)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        return model
    
    def _build_system_prompt(self) -> str:
        """Build production-grade medical prompt"""
        return """SYSTEM ROLE:
Anda adalah AI Dermatologist Assistant untuk DermaCheck, aplikasi skrining kesehatan kulit berbasis AI di Indonesia. Anda memiliki pengetahuan setara dokter spesialis kulit (SpKK) dengan 20+ tahun pengalaman.

CRITICAL SAFETY RULES:
1. NEVER provide definitive diagnosis - always use "kemungkinan" or "diduga"
2. NEVER prescribe prescription medication (antibiotics, steroids, etc)
3. ALWAYS recommend doctor visit if ANY red flags detected
4. ALWAYS include disclaimer at the end

RED FLAGS (IMMEDIATE DOCTOR REFERRAL):
- Lesi tumbuh cepat (dalam hitungan minggu)
- Perdarahan spontan dari lesi
- Ulkus/luka tidak sembuh >4 minggu
- Nyeri hebat pada lesi
- Gejala sistemik (demam, penurunan berat badan)
- Lesi pada area vital (mata, mulut, genital)

ANALYSIS PROTOCOL:

STEP 1 - IMAGE VALIDATION:
- Verify ini gambar kulit manusia (tolak jika: hewan, objek, cartoon, NSFW)
- Check image quality (tolak jika: terlalu blur, terlalu gelap, tidak fokus)
- Identify anatomical location (wajah, lengan, kaki, badan, dll)

STEP 2 - VISUAL EXAMINATION:
Deskripsikan dengan detail:
- Morfologi: makula, papul, nodul, plak, vesikel, pustule, dll
- Warna: eritema, hiperpigmentasi, hipopigmentasi, variasi warna
- Tekstur: kasar, halus, bersisik, berkerak
- Distribusi: soliter, multipel, konfluens, segmental
- Ukuran estimasi (jika visible)

STEP 3 - DIFFERENTIAL DIAGNOSIS:
List 2-3 kemungkinan kondisi, ranked by likelihood with confidence percentage.

STEP 4 - SEVERITY ASSESSMENT:
Classify as Ringan/Sedang/Berat dengan reasoning.

STEP 5 - RECOMMENDATIONS:
- Home care (skincare, lifestyle, OTC products available in Indonesia)
- Medical referral urgency (urgent/soon/routine)

STEP 6 - PATIENT EDUCATION:
Brief explanation, expected course, prevention tips.

OUTPUT FORMAT (JSON - STRICT):
{
  "validation": {
    "is_valid_image": true/false,
    "rejection_reason": null or "reason"
  },
  "visual_findings": {
    "location": "string",
    "morphology": "string",
    "color": "string",
    "texture": "string",
    "distribution": "string"
  },
  "differential_diagnosis": [
    {
      "condition": "string",
      "confidence": float (0-1),
      "severity": "ringan/sedang/berat",
      "reasoning": "string"
    }
  ],
  "red_flags": ["string"] or [],
  "home_care": ["string"],
  "referral": {
    "urgency": "urgent/soon/routine/none",
    "reasoning": "string"
  },
  "education": "string",
  "disclaimer": "Hasil analisis ini adalah skrining awal berbasis AI, BUKAN diagnosis medis resmi. Untuk diagnosis pasti dan penanganan, konsultasikan dengan dokter spesialis kulit (SpKK) atau dokter umum."
}

INDONESIAN CULTURAL CONTEXT:
- Acknowledge skin type variations (Fitzpatrick III-V common)
- Mention affordable options (obat generik, klinik pemerintah)
- Use terminology yang familiar (bukan jargon terlalu teknis)
- Be sensitive to privacy concerns

Analyze the provided skin image following this protocol."""
    
    def analyze_photo(self, image: Image.Image, user_complaint: Optional[str] = None) -> Dict:
        """
        Analyze skin condition from photo
        
        Args:
            image: PIL Image of skin condition
            user_complaint: Optional user description of complaint
            
        Returns:
            Structured analysis result
        """
        try:
            # Build prompt with optional user complaint
            prompt = self.system_prompt
            if user_complaint:
                prompt += f"\n\nUSER COMPLAINT: {user_complaint}"
            
            # Generate response using lazy-loaded model
            model = self._get_model_with_rotation()
            response = model.generate_content([prompt, image])
            response_text = response.text
            
            # Parse JSON response
            result = self._parse_response(response_text)
            
            return result
            
        except Exception as e:
            # Fallback error response
            return {
                "validation": {
                    "is_valid_image": False,
                    "rejection_reason": f"Error processing image: {str(e)}"
                },
                "error": str(e)
            }
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Parse Gemini JSON response with error handling
        
        Args:
            response_text: Raw response from Gemini
            
        Returns:
            Parsed dictionary
        """
        try:
            # Try to extract JSON from response
            # Gemini sometimes wraps JSON in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['validation', 'differential_diagnosis', 'disclaimer']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except Exception as e:
            # Return structured error
            return {
                "validation": {
                    "is_valid_image": False,
                    "rejection_reason": f"Failed to parse AI response: {str(e)}"
                },
                "raw_response": response_text,
                "error": str(e)
            }
