"""
LocalMedGemmaClient - Simplified for INT8 stability
Uses bulletproof INT8 model loader
"""

import torch
from PIL import Image
from typing import Union, Optional, Dict
from utils.model_loader import MedGemmaModelLoader
import logging

logger = logging.getLogger(__name__)


class LocalMedGemmaClient:
    """
    Client for MedGemma local inference with INT8
    
    Simplified for maximum stability
    """
    
    def __init__(self, model_name: str = "google/medgemma-4b-it"):
        """Initialize client with INT8 model"""
        logger.info(f"Initializing LocalMedGemmaClient")
        
        self.model_name = model_name
        self.loader = MedGemmaModelLoader(model_name=model_name)
        
        # Load model
        print("\n" + "="*70)
        print("🚀 INITIALIZING DERMACHECK AI WITH MEDGEMMA")
        print("="*70)
        print("")
        
        self.model, self.processor = self.loader.load_model()
        
        print("")
        logger.info("✅ LocalMedGemmaClient ready")
    
    def analyze_skin_condition(
        self,
        image: Union[str, Image.Image],
        user_complaint: Optional[str] = None
    ) -> Dict:
        """
        Analyze skin condition from image
        
        Args:
            image: PIL Image or path to image file
            user_complaint: Optional user complaint text
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Starting skin analysis...")
        
        # Load image
        if isinstance(image, str):
            try:
                image = Image.open(image).convert("RGB")
            except Exception as e:
                logger.error(f"Failed to load image: {e}")
                return {
                    "error": f"Image loading failed: {e}",
                    "fallback": "Gagal membuka gambar. Silakan coba lagi."
                }
        
        # Build prompt
        prompt = "Analyze this skin condition image. Provide diagnosis in Indonesian language."
        if user_complaint:
            prompt += f" Patient complaint: {user_complaint}"
        
        try:
            # Prepare multimodal input
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            }]
            
            # Apply chat template
            text = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=False
            )
            
            # Process inputs
            inputs = self.processor(
                text=text,
                images=image,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            logger.info("Generating analysis...")
            
            # Generate with safe parameters
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=300,
                    min_new_tokens=20,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                    eos_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # Decode response
            full_response = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            # Extract generated part
            prompt_len = inputs['input_ids'].shape[1]
            generated_ids = outputs[:, prompt_len:]
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Use whichever is longer/better
            response_text = generated_text if len(generated_text) > 20 else full_response
            
            logger.info(f"Analysis complete: {len(response_text)} chars")
            
            # Return structured response
            return {
                "visual_findings": {
                    "analysis": response_text[:400]
                },
                "differential_diagnosis": [
                    {
                        "condition": "Lihat analisis lengkap di atas",
                        "confidence": "N/A",
                        "reasoning": response_text
                    }
                ],
                "home_care": [
                    "Lihat rekomendasi dalam analisis",
                    "Konsultasi dokter untuk diagnosis pasti"
                ],
                "referral": {
                    "urgency": "ROUTINE",
                    "reason": "Evaluasi profesional direkomendasikan"
                },
                "education": response_text,
                "disclaimer": "Ini adalah AI assistant, bukan dokter sungguhan. Untuk diagnosis pasti, konsultasi dengan dokter kulit."
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "error": str(e),
                "visual_findings": {"note": "Error occurred during analysis"},
                "differential_diagnosis": [{"condition": "Error", "confidence": "0"}],
                "home_care": ["Silakan coba lagi atau hubungi dokter"],
                "disclaimer": "Maaf, terjadi kesalahan teknis"
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
        logger.info("Starting text consultation...")
        
        # Build prompt
        prompt = f"Medical consultation in Indonesian: {symptoms_text}"
        if user_age:
            prompt += f" Patient age: {user_age} years"
        
        try:
            # Text-only input
            messages = [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }]
            
            text = self.processor.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=False
            )
            
            inputs = self.processor(text=text, return_tensors="pt")
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=300,
                    min_new_tokens=20,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            full_response = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            prompt_len = inputs['input_ids'].shape[1]
            generated_ids = outputs[:, prompt_len:]
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            response = generated_text if len(generated_text) > 20 else full_response
            
            logger.info(f"Consultation complete: {len(response)} chars")
            
            # Fallback if empty
            if len(response.strip()) < 10:
                return ("Maaf, saya tidak dapat memberikan konsultasi yang memadai untuk keluhan ini. "
                       "Silakan hubungi dokter langsung atau layanan kesehatan.\n\n"
                       "📞 Darurat: 119")
            
            return response
            
        except Exception as e:
            logger.error(f"Consultation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return (f"Maaf, terjadi kesalahan teknis: {str(e)}\n\n"
                   "Silakan hubungi dokter atau layanan kesehatan.\n\n"
                   "📞 Darurat: 119")
    
    def get_model_status(self) -> Dict:
        """Get current model status"""
        return self.loader.get_model_info()
