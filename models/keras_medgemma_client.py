"""
Keras MedGemma Client - Native Kaggle Implementation
Uses Kaggle's optimized Keras backend instead of HuggingFace

ADVANTAGES:
- No BitsAndBytes quantization issues
- Pre-optimized for Kaggle environment
- Stable inference (Keras backend)
- Direct model access from Kaggle Models hub
"""

import keras_nlp
import keras
from PIL import Image
import numpy as np
from typing import Union, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class KerasMedGemmaClient:
    """
    MedGemma client using Keras backend
    
    Bypasses HuggingFace/BitsAndBytes issues by using Kaggle's
    native Keras implementation
    """
    
    def __init__(self, model_preset: str = "medgemma_4b_en"):
        """
        Initialize Keras MedGemma client
        
        Args:
            model_preset: Keras model preset name
                Options: medgemma_4b_en, medgemma_2b_en
        """
        logger.info(f"Initializing KerasMedGemmaClient")
        logger.info(f"Model preset: {model_preset}")
        
        self.model = None
        self.model_preset = model_preset
        
        print("="*70)
        print("🚀 LOADING MEDGEMMA (KERAS BACKEND)")
        print("="*70)
        print(f"📦 Model: {model_preset}")
        print(f"🔧 Backend: Keras (Kaggle optimized)")
        print(f"⏳ Loading...")
        print("")
        
        try:
            # Load Keras NLP model
            # This should auto-download from Kaggle Models
            self.model = keras_nlp.models.GemmaCausalLM.from_preset(model_preset)
            
            print("✅ Model loaded successfully!")
            print("🎯 Backend: Keras")
            print("💾 Ready for inference")
            print("="*70)
            
            logger.info("✅ Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            print(f"❌ Error: {e}")
            print("")
            print("📝 Make sure:")
            print("   1. keras-nlp is installed")
            print("   2. Running in Kaggle environment")
            print("   3. Internet is enabled")
            raise
    
    def analyze_skin_condition(
        self,
        image: Union[str, Image.Image],
        user_complaint: Optional[str] = None
    ) -> Dict:
        """
        Analyze skin condition from image
        
        Note: Keras Gemma is text-only, so we'll describe the image
        analysis approach instead
        
        Args:
            image: PIL Image or path to image
            user_complaint: Optional user complaint text
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing skin condition...")
        
        # Build prompt
        prompt = """Anda adalah asisten medis AI. Berikan analisis untuk kondisi kulit dengan gejala berikut:
        
        """
        
        if user_complaint:
            prompt += f"Keluhan pasien: {user_complaint}\n\n"
        else:
            prompt += "Keluhan: Lesi kulit yang memerlukan evaluasi\n\n"
        
        prompt += """Berikan analisis dalam format berikut:
        1. Kemungkinan diagnosis
        2. Gejala yang perlu diperhatikan
        3. Rekomendasi perawatan di rumah
        4. Kapan harus ke dokter
        
        Analisis:"""
        
        try:
            # Generate response
            response = self.model.generate(prompt, max_length=512)
            
            logger.info(f"Analysis complete: {len(response)} chars")
            
            # Return structured response
            return {
                "visual_findings": {
                    "analysis": response[:300]
                },
                "differential_diagnosis": [
                    {
                        "condition": "Lihat analisis lengkap",
                        "confidence": "N/A",
                        "reasoning": response
                    }
                ],
                "home_care": ["Lihat rekomendasi dalam analisis di atas"],
                "referral": {
                    "urgency": "ROUTINE",
                    "reason": "Konsultasi dokter direkomendasikan"
                },
                "education": response,
                "disclaimer": "Ini adalah AI assistant, bukan pengganti dokter. Konsultasi dengan profesional medis untuk diagnosis akurat."
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "error": str(e),
                "visual_findings": {"note": "Error occurred"},
                "differential_diagnosis": [{"condition": "Error", "confidence": "0"}],
                "disclaimer": "Terjadi kesalahan teknis"
            }
    
    def consult_symptoms(
        self,
        symptoms_text: str,
        user_age: Optional[int] = None,
        medical_history: Optional[str] = None
    ) -> str:
        """
        Medical text consultation
        
        Args:
            symptoms_text: User's symptom description
            user_age: Optional user age
            medical_history: Optional medical history
            
        Returns:
            Medical consultation response
        """
        logger.info("Starting consultation...")
        
        # Build prompt
        prompt = f"""Anda adalah asisten medis AI. Berikan konsultasi untuk keluhan berikut:

Keluhan: {symptoms_text}
"""
        
        if user_age:
            prompt += f"Usia: {user_age} tahun\n"
        
        prompt += """\nBerikan respons yang mencakup:
1. Kemungkinan penyebab
2. Gejala yang perlu diawasi
3. Perawatan sementara
4. Kapan harus ke dokter

Konsultasi:"""
        
        try:
            # Generate response
            response = self.model.generate(prompt, max_length=512)
            
            logger.info(f"Consultation complete: {len(response)} chars")
            
            # Fallback if too short
            if len(response.strip()) < 20:
                return ("Maaf, saya tidak dapat memberikan konsultasi yang memadai. "
                       "Silakan hubungi dokter atau layanan kesehatan.\n\n📞 Darurat: 119")
            
            return response
            
        except Exception as e:
            logger.error(f"Consultation failed: {e}")
            return (f"Maaf, terjadi kesalahan: {str(e)}\n\n"
                   "Silakan hubungi layanan kesehatan.\n\n📞 Darurat: 119")
    
    def get_model_status(self) -> Dict:
        """Get model status"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_preset": self.model_preset,
            "backend": "Keras",
            "type": "text-only"
        }


# Quick loader function
def load_keras_medgemma(model_preset: str = "medgemma_4b_en"):
    """
    Load MedGemma using Keras backend
    
    Args:
        model_preset: Model preset name
        
    Returns:
        KerasMedGemmaClient instance
    """
    client = KerasMedGemmaClient(model_preset=model_preset)
    return client
