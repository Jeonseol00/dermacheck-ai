"""
MedGemma Client - Gemma3 Text-Only Mode (FIXED)
Properly handles text-only generation without triggering vision encoder

FIX: For text-only generation, pass string directly (NOT dict with images key)
"""

import keras
import keras_nlp
from PIL import Image
import numpy as np
from typing import Union, Optional, Dict
import re
import logging
import os

logger = logging.getLogger(__name__)


class MedGemmaClient:
    """
    Production MedGemma client for Gemma3 multimodal model
    
    CRITICAL FIXES:
    - Text-only mode: Pass string directly (no vision encoder triggered)
    - bfloat16 precision (50% memory savings)
    - Text cleaning (Telegram API compatibility)
    - Kaggle local path loading
    """
    
    def __init__(self, use_local=True):
        """
        Initialize MedGemma client
        
        Args:
            use_local: If True, load from /kaggle/input (recommended for Kaggle)
        """
        logger.info(f"Initializing MedGemmaClient (Gemma3 Text-Only Mode)")
        
        # FIX: Set bfloat16 precision BEFORE loading model
        print("🔧 Setting bfloat16 precision for memory optimization...")
        keras.config.set_floatx("bfloat16")
        logger.info("✅ bfloat16 precision enabled")
        
        self.model = None
        
        print("")
        print("="*70)
        print("🚀 LOADING MEDGEMMA (GEMMA3 TEXT-ONLY MODE)")
        print("="*70)
        
        if use_local:
            # Kaggle Input Path (instant, no download)
            self.local_path = "/kaggle/input/medgemma/keras/medgemma_1.5_instruct_4b/v1"
            print(f"📂 Mode: Local (Kaggle Input)")
            print(f"📍 Path: {self.local_path}")
            
            # Check if path exists
            if not os.path.exists(self.local_path):
                print(f"⚠️  Path not found: {self.local_path}")
                print(f"💡 Make sure MedGemma is added via Kaggle 'Add Data' menu")
                raise FileNotFoundError(f"MedGemma not found at {self.local_path}")
            
            print(f"✅ Path exists, loading model...")
            preset = self.local_path
        else:
            # Fallback: Download from internet (slower)
            print(f"📥 Mode: Download from internet")
            preset = "medgemma_1.5_4b_en"
        
        print(f"🔧 Precision: bfloat16")
        print(f"🎯 Mode: Text-only (vision encoder bypassed)")
        print(f"⏳ Loading...")
        print("")
        
        try:
            # Load Gemma3 model
            # For text-only: Use GemmaCausalLM (not Gemma3CausalLM to avoid vision)
            # OR use Gemma3CausalLM but only pass text strings
            self.model = keras_nlp.models.GemmaCausalLM.from_preset(preset)
            
            print("="*70)
            print("✅ MODEL LOADED SUCCESSFULLY!")
            print("="*70)
            print(f"📊 Backend: Keras NLP")
            print(f"💾 Precision: bfloat16")
            print(f"🎯 Type: Text medical specialist (vision bypassed)")
            print(f"✅ Ready for text-only generation!")
            print("="*70)
            print("")
            
            logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            print(f"❌ Error: {e}")
            print("")
            print("📝 Troubleshooting:")
            print("   1. Check keras-nlp version (pip install --upgrade keras-nlp)")
            print("   2. Verify path exists (if use_local=True)")
            print("   3. Check internet connection (if use_local=False)")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean model output for Telegram compatibility
        
        Removes:
        - Gemma internal tags
        - Role markers
        - Problematic Markdown
        
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
        Image bypass - MedGemma text-only mode
        
        Returns helpful message asking user to describe condition in text
        
        Args:
            image: PIL Image or path (not used, for API compatibility)
            user_complaint: Optional user complaint text
            
        Returns:
            Dict with bypass message
        """
        logger.info("Image received - returning text-only bypass message")
        
        # Bypass message for image inputs
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
        Medical text consultation (TEXT-ONLY - Core functionality)
        
        CRITICAL FIX: Pass plain string to model.generate()
        DO NOT pass dict with 'images' key - this triggers vision encoder!
        
        Args:
            symptoms_text: User's symptom description
            user_age: Optional user age
            medical_history: Optional medical history
            
        Returns:
            Medical consultation response (cleaned)
        """
        logger.info("Starting text-only consultation...")
        
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
            # CRITICAL FIX: Pass plain string (NOT dict with images)
            # This bypasses vision encoder and prevents Conv2D error
            response = self.model.generate(
                prompt,  # Plain string - no dict!
                max_length=512
            )
            
            # Clean text for Telegram
            cleaned_response = self._clean_text(response)
            
            logger.info(f"Consultation complete: {len(cleaned_response)} chars")
            
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
            "backend": "Keras NLP GemmaCausalLM",
            "precision": "bfloat16",
            "type": "text-only",
            "mode": "Gemma3 text-only (vision bypassed)",
            "fixes": {
                "memory_optimization": "bfloat16 ✅",
                "text_cleaning": "Telegram-safe ✅",
                "image_bypass": "Text-only mode ✅",
                "vision_encoder": "Bypassed (text-only input) ✅"
            }
        }


# Quick loader function
def load_medgemma(use_local=True):
    """
    Load MedGemma with text-only mode
    
    Args:
        use_local: If True, load from /kaggle/input
        
    Returns:
        MedGemmaClient instance (text-only ready)
    """
    client = MedGemmaClient(use_local=use_local)
    return client
