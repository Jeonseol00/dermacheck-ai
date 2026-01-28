"""
Local MedGemma Client
Replaces API-based Gemini Flash with local Med Gemma inference
Compliant with HAI-DEF model requirements for competition
"""

import torch
from PIL import Image
from typing import Union, Optional, Dict, List
from utils.model_loader import MedGemmaModelLoader
import json
import re
import logging

logger = logging.getLogger(__name__)


class LocalMedGemmaClient:
    """
    Local MedGemma client for dermatology analysis and medical consultation
    Runs MedGemma 4B multimodal model locally for HAI-DEF compliance
    
    Features:
    - Skin condition analysis from photos
    - Text-based medical consultation
    - Emergency triage detection
    - Indonesian language support
    - OTC-only medication recommendations
    """
    
    def __init__(self, model_name: str = "google/medgemma-4b-it"):
        """
        Initialize local MedGemma client
        
        Args:
            model_name: HuggingFace model ID (default: google/medgemma-4b-it)
        """
        logger.info(f"Initializing LocalMedGemmaClient with {model_name}")
        
        self.model_name = model_name
        self.loader = MedGemmaModelLoader(model_name=model_name, quantize_4bit=True)
        
        # Load model at initialization
        logger.info("Loading MedGemma model...")
        self.model, self.processor = self.loader.load_model()
        
        logger.info("✅ LocalMedGemmaClient ready!")
    
    def analyze_skin_condition(
        self,
        image: Union[str, Image.Image],
        user_complaint: Optional[str] = None
    ) -> Dict:
        """
        Analyze skin condition from image using local MedGemma
        
        Args:
            image: PIL Image or path to image file
            user_complaint: Optional user-provided symptom description
            
        Returns:
            Dictionary with analysis results:
            {
                "visual_findings": {...},
                "differential_diagnosis": [...],
                "red_flags": [...],
                "home_care": [...],
                "referral": {...},
                "education": str,
                "disclaimer": str
            }
        """
        logger.info("Starting skin condition analysis...")
        
        # Load image if path provided
        if isinstance(image, str):
            try:
                image = Image.open(image).convert("RGB")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return {"error": f"Image loading failed: {e}"}
        
        # Build medical prompt
        prompt = self._build_dermatology_prompt(user_complaint)
        
        # Prepare messages for MedGemma
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        try:
            # Apply chat template and process inputs
            text_prompt = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=False
            )
            
            inputs = self.processor(
                text=text_prompt,
                images=image,
                return_tensors="pt"
            ).to(self.model.device)
            
            # Generate response
            logger.info("Generating analysis...")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Decode response
            response_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            logger.info("Parsing response...")
            
            # Parse JSON response
            try:
                result = self._parse_json_response(response_text)
                logger.info("✅ Analysis complete")
                return result
            except Exception as e:
                logger.warning(f"JSON parsing failed: {e}, returning raw text")
                # Fallback to text response
                return {
                    "raw_response": response_text,
                    "note": "Structured parsing failed, returning raw AI response"
                }
                
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def consult_symptoms(
        self,
        symptoms_text: str,
        user_age: Optional[int] = None,
        medical_history: Optional[str] = None
    ) -> str:
        """
        Medical text consultation using local MedGemma
        
        Args:
            symptoms_text: User-reported symptoms in natural language
            user_age: Optional patient age
            medical_history: Optional relevant medical history
            
        Returns:
            Medical consultation response in Indonesian
        """
        logger.info("Starting text consultation...")
        
        # Build consultation prompt
        prompt = self._build_consultation_prompt(symptoms_text, user_age, medical_history)
        
        # Prepare text-only message
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        try:
            # Apply chat template
            text_prompt = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=False
            )
            
            # Process text-only input
            inputs = self.processor(
                text=text_prompt,
                return_tensors="pt"
            ).to(self.model.device)
            
            # Generate response
            logger.info("Generating consultation...")
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.processor.decode(outputs[0], skip_special_tokens=True)
            
            logger.info("✅ Consultation complete")
            return response
            
        except Exception as e:
            logger.error(f"Consultation failed: {e}")
            return f"❌ Maaf, terjadi kesalahan: {str(e)}"
    
    def _build_dermatology_prompt(self, user_complaint: Optional[str]) -> str:
        """Build structured dermatology analysis prompt for Indonesian users"""
        
        base_prompt = """Anda adalah asisten AI dermatologi Indonesia yang ahli. Analisis gambar kulit ini dan berikan diagnosis dalam format JSON.

**INSTRUKSI PENTING:**
- Gunakan Bahasa Indonesia yang jelas dan ramah
- HANYA rekomendasikan obat OTC (over-the-counter) yang tersedia di Indonesia
- Deteksi kondisi darurat (infeksi berat, melanoma suspek, dll)
- Berikan confidence score dalam persen (%)
- Gunakan istilah medis dengan penjelasan sederhana

**FORMAT OUTPUT (JSON):**
```json
{
  "visual_findings": {
    "location": "Bagian kulit (contoh: pipi kiri, dahi, lengan atas)",
    "morphology": "Bentuk lesi (papul, pustul, nodul, plak, vesikel, makula, dll)",
    "color": "Warna dominan (eritema/merah, coklat, hitam, putih, dll)"
  },
  "differential_diagnosis": [
    {
      "condition": "Nama kondisi kulit dalam Bahasa Indonesia",
      "confidence": "90",
      "reasoning": "Alasan diagnosis berdasarkan temuan visual"
    },
    {
      "condition": "Diagnosis alternatif jika ada",
      "confidence": "60",
      "reasoning": "Alasan alternatif"
    }
  ],
  "red_flags": [
    "Tanda bahaya yang perlu perhatian segera (jika ada)"
  ],
  "home_care": [
    "Saran perawatan rumah dengan produk OTC (sabun, pelembab, krim, dll)",
    "Langkah-langkah yang bisa dilakukan sendiri"
  ],
  "referral": {
    "urgency": "URGENT/SOON/ROUTINE",
    "reason": "Alasan rujukan ke dokter spesialis kulit"
  },
  "education": "Informasi edukatif singkat tentang kondisi ini (2-3 kalimat)",
  "disclaimer": "Pernyataan bahwa ini adalah AI assistant, bukan dokter sungguhan"
}
```

**KONTEKS INDONESIA:**
- Obat OTC umum: Paracetamol, Ibuprofen, krim hydrocortisone 1%, salep antibiotik (Betadine), pelembab (Cetaphil, Vaseline)
- Kondisi tropis: Pertimbangkan infeksi jamur, heat rash, gigitan serangga
- Akses kesehatan: Rujuk ke Puskesmas untuk kasus ringan, SpKK untuk kasus kompleks
"""
        
        if user_complaint:
            base_prompt += f"\n\n**KELUHAN PASIEN:**\n{user_complaint}\n"
        
        base_prompt += "\n\n**TUGAS ANDA:**\nBerikan analisis dalam format JSON seperti di atas. Pastikan JSON valid dan lengkap."
        
        return base_prompt
    
    def _build_consultation_prompt(
        self,
        symptoms: str,
        user_age: Optional[int],
        medical_history: Optional[str]
    ) -> str:
        """Build medical consultation prompt for Indonesian text consultation"""
        
        prompt = f"""Anda adalah asisten medis AI Indonesia yang profesional dan empatik. Berikan konsultasi untuk gejala berikut:

**GEJALA PASIEN:**
{symptoms}
"""
        
        if user_age:
            prompt += f"\n**USIA:** {user_age} tahun\n"
        
        if medical_history:
            prompt += f"\n**RIWAYAT MEDIS:** {medical_history}\n"
        
        prompt += """
**INSTRUKSI KONSULTASI:**

1. **DETEKSI DARURAT TERLEBIH DAHULU** (PRIORITAS TERTINGGI):
   - Nyeri dada menjalar ke lengan/rahang → Kemungkinan serangan jantung
   - Stroke signs (FAST: Face drooping, Arm weakness, Speech difficulty, Time = critical)
   - Sesak napas berat, kehilangan kesadaran, perdarahan hebat
   - **Jika terdeteksi: SEGERA beri instruksi ke IGD/Poli Darurat**

2. **Ringkasan Keluhan:**
   - Parafrasa gejala utama secukupnya

3. **Kemungkinan Penyebab (Differential Diagnosis):**
   - Berikan 2-3 kemungkinan penyebab, mulai dari yang paling mungkin
   - Jelaskan karakteristik khas masing-masing
   - Gunakan istilah medis dengan penjelasan awam

4. **Perawatan Rumah (Home Care):**
   - HANYA obat OTC yang tersedia di Indonesia (Paracetamol, Ibuprofen, dll)
   - Istirahat, hidrasi, kompres, dll
   - Dosis yang aman (jika menyarankan obat)

5. **Kapan Harus ke Dokter:**
   - Red flags yang memerlukan evaluasi medis
   - Timeframe: SEGERA (hari ini), 1-2 hari, 1 minggu, dll

6. **Saran Pencegahan:**
   - Tips untuk mencegah kekambuhan
   - Perubahan gaya hidup jika relevan

7. **Disclaimer:**
   - Tegaskan bahwa ini AI assistant, BUKAN dokter
   - Diagnosis pasti memerlukan pemeriksaan fisik oleh tenaga medis

**GAYA KOMUNIKASI:**
- Gunakan Bahasa Indonesia yang hangat dan profesional
- Emoji untuk readability (🚨 untuk darurat, 💊 untuk obat, 🏥 untuk rujukan, dll)
- Hindari jargon medis tanpa penjelasan
- Berikan keyakinan tanpa memberikan diagnosis pasti

**KONTEKS INDONESIA:**
- Sistem kesehatan: Puskesmas (ringan), Klinik/RS (sedang-berat), IGD (darurat)
- Obat OTC umum tersedia di Apotek/Alfamart/Indomaret
- Pertimbangkan kondisi tropis (infeksi dengue, tifoid, dll jika relevan)

Berikan konsultasi sekarang dalam format yang terstruktur dan mudah dipahami.
"""
        
        return prompt
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """
        Parse JSON from MedGemma response
        
        Args:
            response_text: Raw response from model
            
        Returns:
            Parsed dictionary
            
        Raises:
            ValueError: If JSON parsing fails
        """
        # Try to find JSON block with code fence
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        
        # Try to find JSON without code fence
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        
        # If no JSON found, raise error
        raise ValueError("No valid JSON found in response")
    
    def get_model_status(self) -> Dict:
        """
        Get current model status and info
        
        Returns:
            Dictionary with model information
        """
        return self.loader.get_model_info()
