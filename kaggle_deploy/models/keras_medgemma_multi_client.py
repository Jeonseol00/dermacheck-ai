"""
Keras MedGemma Client - MULTIMODAL (Image + Text)
Uses Kaggle's Keras backend with Gemma3CausalLM

CRITICAL: This uses keras.models.Gemma3C ausalLM (Gemma 3) which supports:
- Text inputs
- Image inputs
- Multimodal (text + image)

NO HUGGINGFACE, NO BITSANDBYTES, NO QUANTIZATION ISSUES!
"""

import keras
from PIL import Image
import numpy as np
from typing import Union, Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)


class KerasMedGemmaMultimodalClient:
    """
    MedGemma multimodal client using Keras Gemma3CausalLM
    
    Supports:
    - Image analysis (dermatology, radiology, etc.)
    - Text consultation
    - Multimodal (image + text) analysis
    
    Backend: Keras (stable, no quantization issues)
    """
    
    def __init__(self, model_preset: str = "medgemma_1.5_4b_en"):
        """
        Initialize Keras MedGemma multimodal client
        
        Args:
            model_preset: Keras model preset
                Options:
                - medgemma_1.5_4b_en (multimodal, recommended)
                - medgemma_4b_en (multimodal)
        """
        logger.info(f"Initializing KerasMedGemmaMultimodalClient")
        logger.info(f"Model preset: {model_preset}")
        
        self.model = None
        self.model_preset = model_preset
        
        print("="*70)
        print("🚀 LOADING MEDGEMMA MULTIMODAL (KERAS)")
        print("="*70)
        print(f"📦 Model: {model_preset}")
        print(f"🔧 Backend: Keras Gemma3CausalLM")
        print(f"🎯 Capabilities: Image + Text (Multimodal)")
        print(f"⏳ Loading from Kaggle Models...")
        print("")
        
        try:
            # Load Gemma3 multimodal model from Keras
            # This auto-downloads from Kaggle Models hub
            self.model = keras.models.Gemma3CausalLM.from_preset(
                model_preset,
                dtype="bfloat16"  # Stable precision for multimodal
            )
            
            print("="*70)
            print("✅ MODEL LOADED SUCCESSFULLY!")
            print("="*70)
            print(f"📊 Backend: Keras")
            print(f"💾 Dtype: bfloat16 (stable)")
            print(f"🎯 Mode: Multimodal (Image + Text)")
            print(f"🎯 Ready for inference!")
            print("="*70)
            
            logger.info("✅ Multimodal model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            print(f"❌ Error: {e}")
            print("")
            print("📝 Troubleshooting:")
            print("   1. Ensure keras>=3.0 installed")
            print("   2. Running in Kaggle environment")
            print("   3. Internet enabled")
            print("   4. Try: pip install --upgrade keras")
            raise
    
    def analyze_skin_condition(
        self,
        image: Union[str, Image.Image],
        user_complaint: Optional[str] = None
    ) -> Dict:
        """
        Analyze skin condition from image (MULTIMODAL)
        
        Args:
            image: PIL Image or path to image file
            user_complaint: Optional user complaint text
            
        Returns:
            Dictionary with diagnosis results
        """
        logger.info("Starting multimodal skin analysis...")
        
        # Load image
        if isinstance(image, str):
            try:
                image = Image.open(image).convert("RGB")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return {
                    "error": f"Image loading failed: {e}",
                    "fallback": "Gagal membuka gambar."
                }
        
        # Convert PIL to numpy array for Keras
        image_array = np.array(image)
        
        # Build multimodal prompt
        prompt = "<start_of_image>"  # Special token for image input
        
        if user_complaint:
            prompt += f"\n\nAnalisis gambar kondisi kulit ini dalam Bahasa Indonesia.\nKeluhan pasien: {user_complaint}\n\n"
        else:
            prompt += "\n\nAnalisis gambar kondisi kulit ini dalam Bahasa Indonesia. Berikan diagnosis dan rekomendasi.\n\n"
        
        prompt += """Format jawaban:
1. Kondisi yang terlihat pada gambar
2. Kemungkinan diagnosis
3. Tingkat keparahan
4. Rekomendasi perawatan
5. Kapan harus ke dokter

Analisis:"""
        
        try:
            # Generate with multimodal input
            # Keras Gemma3 accepts dict with 'images' and 'text' keys
            response = self.model.generate(
                {
                    "images": image_array[np.newaxis, ...],  # Add batch dimension
                    "text": prompt
                },
                max_length=512
            )
            
            logger.info(f"Analysis complete: {len(response)} chars")
            
            # Return structured response
            return {
                "visual_findings": {
                    "analysis": response[:400]
                },
                "differential_diagnosis": [
                    {
                        "condition": "Lihat analisis lengkap",
                        "confidence": "N/A",
                        "reasoning": response
                    }
                ],
                "home_care": ["Lihat rekomendasi dalam analisis"],
                "referral": {
                    "urgency": "ROUTINE",
                    "reason": "Evaluasi profesional direkomendasikan"
                },
                "education": response,
                "disclaimer": "Ini adalah AI assistant berbasis MedGemma. Untuk diagnosis pasti, konsultasi dengan dokter kulit."
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
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
        Medical text consultation (text-only)
        
        Args:
            symptoms_text: User's symptom description
            user_age: Optional user age
            medical_history: Optional medical history
            
        Returns:
            Medical consultation response
        """
        logger.info("Starting text consultation...")
        
        # Build prompt
        prompt = f"""Anda adalah asisten medis AI berbasis MedGemma. Berikan konsultasi untuk keluhan berikut:

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
            # Text-only generation
            response = self.model.generate(prompt, max_length=512)
            
            logger.info(f"Consultation complete: {len(response)} chars")
            
            # Fallback if too short
            if len(response.strip()) < 30:
                return ("Maaf, saya tidak dapat memberikan konsultasi yang memadai. "
                       "Silakan hubungi dokter atau layanan kesehatan.\n\n📞 Darurat: 119")
            
            return response
            
        except Exception as e:
            logger.error(f"Consultation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return (f"Maaf, terjadi kesalahan: {str(e)}\n\n"
                   "Silakan hubungi layanan kesehatan.\n\n📞 Darurat: 119")
    
    def get_model_status(self) -> Dict:
        """Get model status"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_preset": self.model_preset,
            "backend": "Keras Gemma3CausalLM",
            "type": "multimodal",
            "capabilities": ["text", "image", "multimodal"]
        }


# Quick loader function
def load_keras_medgemma_multimodal(model_preset: str = "medgemma_1.5_4b_en"):
    """
    Load MedGemma multimodal using Keras backend
    
    Args:
        model_preset: Model preset name
            - medgemma_1.5_4b_en (recommended, latest)
            - medgemma_4b_en (stable)
        
    Returns:
        KerasMedGemmaMultimodalClient instance
    """
    client = KerasMedGemmaMultimodalClient(model_preset=model_preset)
    return client
