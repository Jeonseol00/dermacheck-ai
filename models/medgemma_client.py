"""
MedGemma Client - Production Ready for Kaggle Deployment
Implements 3 critical fixes from field testing:
1. bfloat16 precision (memory optimization)
2. Text cleaning (Telegram compatibility)
3. Text-only mode (MedGemma constraint)
"""

import keras
import keras_nlp
from PIL import Image
import numpy as np
from typing import Union, Optional, Dict
import re
import logging

logger = logging.getLogger(__name__)


class MedGemmaClient:
    """
    Production MedGemma client for Kaggle T4 GPU
    
    CRITICAL FIXES APPLIED:
    - bfloat16 precision (50% memory savings)
    - Text cleaning (Telegram API compatibility)
    - Text-only mode (MedGemma is not multimodal)
    """
    
    def __init__(self, model_preset: str = "medgemma_1.5_4b_en"):
        """
        Initialize MedGemma client with production fixes
        
        Args:
            model_preset: Keras model preset (default: medgemma_1.5_4b_en)
        """
        logger.info(f"Initializing MedGemmaClient (Production Mode)")
        logger.info(f"Model preset: {model_preset}")
        
        # FIX A: Set bfloat16 precision (CRITICAL for T4 memory)
        print("🔧 FIX A: Setting bfloat16 precision for memory optimization...")
        keras.config.set_floatx("bfloat16")
        logger.info("✅ bfloat16 precision enabled (50% memory reduction)")
        
        self.model = None
        self.model_preset = model_preset
        
        print("")
        print("="*70)
        print("🚀 LOADING MEDGEMMA (PRODUCTION MODE)")
        print("="*70)
        print(f"📦 Model: {model_preset}")
        print(f"🔧 Precision: bfloat16 (memory optimized)")
        print(f"🎯 Mode: Text-only medical specialist")
        print(f"⏳ Loading from Kaggle Models...")
        print("")
        
        try:
            # Load MedGemma with bfloat16
            self.model = keras_nlp.models.GemmaCausalLM.from_preset(model_preset)
            
            print("="*70)
            print("✅ MODEL LOADED SUCCESSFULLY!")
            print("="*70)
            print(f"📊 Backend: Keras NLP")
            print(f"💾 Precision: bfloat16")
            print(f"🎯 Type: Text medical specialist")
            print(f"✅ Production fixes applied: 3/3")
            print("="*70)
            print("")
            
            logger.info("✅ Model loaded successfully with production config")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            print(f"❌ Error: {e}")
            print("")
            print("📝 Troubleshooting:")
            print("   1. Ensure keras-nlp installed")
            print("   2. Check internet connection")
            print("   3. Verify Kaggle environment")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        FIX B: Clean model output for Telegram compatibility
        
        Removes:
        - Gemma internal tags (<start_of_turn>, <end_of_turn>)
        - Role markers (user, model)
        - Markdown formatting that breaks Telegram API
        
        Args:
            text: Raw model output
            
        Returns:
            Cleaned text safe for Telegram
        """
        # Remove Gemma internal tags
        text = text.replace("<start_of_turn>", "")
        text = text.replace("<end_of_turn>", "")
        text = text.replace("user", "")
        text = text.replace("model", "")
        
        # Remove problematic Markdown
        text = text.replace("**", "")  # Bold
        text = text.replace("*", "-")  # Italic → dash
        text = text.replace("[", "(")  # Brackets
        text = text.replace("]", ")")
        
        # Clean extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 newlines
        text = text.strip()
        
        return text
    
    def analyze_skin_condition(
        self,
        image: Union[str, Image.Image],
        user_complaint: Optional[str] = None
    ) -> Dict:
        """
        FIX C: Image bypass - MedGemma is text-only
        
        Instead of crashing, returns helpful message asking user
        to describe their condition in text
        
        Args:
            image: PIL Image or path (not used, for API compatibility)
            user_complaint: Optional user complaint text
            
        Returns:
            Dict with bypass message
        """
        logger.info("Image received - returning text-only bypass message")
        
        # FIX C: Bypass message for image inputs
        bypass_message = (
            "⚠️ MedGemma adalah model spesialis teks medis.\n\n"
            "Untuk analisis terbaik, silakan deskripsikan kondisi visual kulit Anda secara detail:\n\n"
            "📝 Yang perlu disebutkan:\n"
            "• Warna (merah, putih, coklat, dll)\n"
            "• Tekstur (kasar, halus, bersisik, dll)\n"
            "• Ukuran (diameter atau luas area)\n"
            "• Lokasi di tubuh\n"
            "• Durasi sudah berapa lama\n"
            "• Apakah gatal, nyeri, atau tidak terasa\n\n"
            "💡 Contoh: \"Ada bercak merah diameter 2cm di lengan kanan, "
            "tekstur kasar dan sedikit gatal, sudah 3 hari\"\n\n"
            "Silakan kirim deskripsi Anda sebagai pesan teks! 📱"
        )
        
        # Return structured response
        return {
            "visual_findings": {
                "analysis": bypass_message
            },
            "differential_diagnosis": [
                {
                    "condition": "Deskripsi teks diperlukan",
                    "confidence": "N/A",
                    "reasoning": "MedGemma memproses input teks untuk akurasi optimal"
                }
            ],
            "home_care": [
                "Kirim deskripsi detail kondisi kulit Anda sebagai pesan teks"
            ],
            "referral": {
                "urgency": "ROUTINE",
                "reason": "Deskripsi teks akan membantu analisis yang lebih akurat"
            },
            "education": bypass_message,
            "disclaimer": "Untuk diagnosis pasti, konsultasi dengan dokter kulit profesional."
        }
    
    def consult_symptoms(
        self,
        symptoms_text: str,
        user_age: Optional[int] = None,
        medical_history: Optional[str] = None
    ) -> str:
        """
        Medical text consultation (core functionality)
        
        Args:
            symptoms_text: User's symptom description
            user_age: Optional user age
            medical_history: Optional medical history
            
        Returns:
            Medical consultation response (cleaned)
        """
        logger.info("Starting text consultation...")
        
        # Build prompt
        prompt = f"""Anda adalah asisten medis AI berbasis MedGemma. Berikan konsultasi medis untuk keluhan berikut:

Keluhan: {symptoms_text}
"""
        
        if user_age:
            prompt += f"Usia: {user_age} tahun\n"
        
        if medical_history:
            prompt += f"Riwayat medis: {medical_history}\n"
        
        prompt += """
Berikan respons yang mencakup:
1. Kemungkinan penyebab atau diagnosis
2. Gejala yang perlu diawasi
3. Rekomendasi perawatan sementara
4. Kapan harus segera ke dokter

Konsultasi:"""
        
        try:
            # Generate response
            response = self.model.generate(prompt, max_length=512)
            
            # FIX B: Clean text for Telegram
            cleaned_response = self._clean_text(response)
            
            logger.info(f"Consultation complete: {len(cleaned_response)} chars (cleaned)")
            
            # Fallback if too short after cleaning
            if len(cleaned_response.strip()) < 30:
                return (
                    "Maaf, saya tidak dapat memberikan konsultasi yang memadai untuk keluhan ini.\n\n"
                    "Silakan hubungi dokter atau layanan kesehatan langsung.\n\n"
                    "📞 Darurat: 119"
                )
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Consultation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return (
                f"Maaf, terjadi kesalahan teknis: {str(e)}\n\n"
                "Silakan hubungi layanan kesehatan.\n\n"
                "📞 Darurat: 119"
            )
    
    def get_model_status(self) -> Dict:
        """Get model status"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_preset": self.model_preset,
            "backend": "Keras NLP",
            "precision": "bfloat16",
            "type": "text-only",
            "production_fixes": {
                "memory_optimization": "bfloat16 ✅",
                "text_cleaning": "Telegram-safe ✅",
                "image_bypass": "Text-only mode ✅"
            }
        }


# Quick loader function
def load_medgemma(model_preset: str = "medgemma_1.5_4b_en"):
    """
    Load MedGemma with production fixes
    
    Args:
        model_preset: Model preset name
        
    Returns:
        MedGemmaClient instance (production ready)
    """
    client = MedGemmaClient(model_preset=model_preset)
    return client
