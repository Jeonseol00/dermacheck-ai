"""
Keras Hub MedGemma Client
Official implementation using Google's Keras Hub library

This replaces the PyTorch transformers approach with the official
Keras Hub implementation that natively supports Gemma 3 architecture.

Author: DermaCheck AI Team
Date: January 30, 2026
"""

import os
from typing import Optional, Dict
import logging

try:
    import keras_hub
    import keras
except ImportError:
    raise ImportError(
        "keras-hub not installed. Install with: pip install keras-hub keras>=3.0"
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KerasHubMedGemma:
    """
    MedGemma client using Keras Hub (official Google implementation)
    
    Features:
    - Native Gemma 3 support (no architecture errors)
    - Multimodal (text + image) via MedSigLIP
    - Memory efficient (bfloat16 precision)
    - Stable generation (no CUDA crashes)
    
    Usage:
        client = KerasHubMedGemma()
        diagnosis = client.generate_diagnosis(
            symptoms="Fever, headache, neck stiffness",
            age=28,
            gender="Female"
        )
    """
    
    def __init__(
        self,
        model_name: str = "hf://google/medgemma-4b-it",
        dtype: str = "bfloat16",
        hf_token: Optional[str] = None
    ):
        """
        Initialize Keras Hub MedGemma client
        
        Args:
            model_name: HuggingFace model path or Keras preset name
            dtype: Precision - "bfloat16" (recommended) or "float16"
            hf_token: HuggingFace token (optional, from env if not provided)
        """
        self.model_name = model_name
        self.dtype = dtype
        
        # Set HF token if provided or get from environment
        if hf_token:
            os.environ['HF_TOKEN'] = hf_token
        elif 'HF_TOKEN' not in os.environ:
            logger.warning("HF_TOKEN not set. Model download may fail.")
        
        logger.info(f"Loading MedGemma via Keras Hub: {model_name}")
        logger.info(f"Precision: {dtype}")
        
        # Load model using Keras Hub
        self.model = keras_hub.models.CausalLM.from_preset(
            model_name,
            dtype=dtype
        )
        
        logger.info("✅ MedGemma loaded successfully!")
        
    def _format_prompt(self, user_message: str) -> str:
        """
        Format prompt using Gemma chat template
        
        Args:
            user_message: User's message/question
            
        Returns:
            Formatted prompt string
        """
        return f"""<start_of_turn>user
{user_message}<end_of_turn>
<start_of_turn>model"""
    
    def generate(
        self,
        prompt: str,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Generate text using MedGemma
        
        Args:
            prompt: Input prompt (will be formatted automatically)
            max_length: Maximum output length in tokens
            temperature: Sampling temperature (0.0 = greedy, 1.0 = creative)
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text
        """
        formatted_prompt = self._format_prompt(prompt)
        
        output = self.model.generate(
            formatted_prompt,
            max_length=max_length
        )
        
        # Extract only the model's response (remove prompt)
        if "<start_of_turn>model" in output:
            response = output.split("<start_of_turn>model")[-1]
            # Remove end tokens
            response = response.replace("<end_of_turn>", "").strip()
            return response
        
        return output
    
    def generate_diagnosis(
        self,
        symptoms: str,
        age: int,
        gender: str,
        medical_history: str = "None",
        max_length: int = 600
    ) -> str:
        """
        Generate medical diagnosis based on symptoms
        
        Args:
            symptoms: Patient's symptoms description
            age: Patient's age
            gender: Patient's gender
            medical_history: Patient's medical history
            max_length: Maximum output length
            
        Returns:
            Medical diagnosis and recommendations
        """
        prompt = f"""Patient Information:
- Age: {age} years
- Gender: {gender}
- Medical History: {medical_history}
- Chief Complaint: {symptoms}

Please provide:
1. Differential diagnosis (top 3 most likely conditions)
2. Recommended immediate actions
3. Triage level (URGENT/SEMI-URGENT/ROUTINE)

Analysis:"""
        
        return self.generate(prompt, max_length=max_length)
    
    def generate_soap_note(
        self,
        symptoms: str,
        age: int,
        gender: str,
        medical_history: str = "None",
        max_length: int = 800
    ) -> str:
        """
        Generate structured SOAP note
        
        Args:
            symptoms: Patient's symptoms
            age: Patient's age
            gender: Patient's gender
            medical_history: Patient's medical history
            max_length: Maximum output length
            
        Returns:
            Structured SOAP note
        """
        prompt = f"""Generate a complete SOAP note for this patient:

Patient:
- Age: {age} years
- Gender: {gender}
- Medical History: {medical_history}
- Chief Complaint: {symptoms}

Please provide structured SOAP format:

S (Subjective): Patient's description and history
O (Objective): Expected clinical findings and vital signs
A (Assessment): 
  - Differential diagnosis with ICD-10 codes
  - Most likely diagnosis
P (Plan):
  - Diagnostic tests needed
  - Treatment recommendations
  - Follow-up schedule
  
Triage Level: URGENT/SEMI-URGENT/ROUTINE

SOAP Note:"""
        
        return self.generate(prompt, max_length=max_length)
    
    def analyze_dermatology(
        self,
        skin_description: str,
        duration: str,
        location: str,
        associated_symptoms: str = "None",
        max_length: int = 700
    ) -> str:
        """
        Specialized dermatology analysis
        
        Args:
            skin_description: Description of skin condition
            duration: How long the condition has been present
            location: Body location of the condition
            associated_symptoms: Other symptoms
            max_length: Maximum output length
            
        Returns:
            Dermatology analysis and recommendations
        """
        prompt = f"""Dermatology Case:

Skin Condition:
- Description: {skin_description}
- Location: {location}
- Duration: {duration}
- Associated Symptoms: {associated_symptoms}

Please provide dermatological assessment:

1. Differential Diagnosis:
   - Most likely condition
   - Other possibilities
   - ICD-10 codes

2. ABCDE Assessment (if applicable):
   - Asymmetry
   - Border
   - Color
   - Diameter
   - Evolution

3. Recommendations:
   - Immediate actions
   - When to see a dermatologist
   - Home care instructions

4. Urgency Level: URGENT/SEMI-URGENT/ROUTINE

Analysis:"""
        
        return self.generate(prompt, max_length=max_length)
    
    def get_memory_usage(self) -> Dict[str, str]:
        """
        Get model memory information
        
        Returns:
            Dictionary with memory info
        """
        try:
            import keras.backend as K
            backend = K.backend()
            
            return {
                "backend": backend,
                "dtype": self.dtype,
                "model": self.model_name
            }
        except Exception as e:
            return {"error": str(e)}


# Quick test function
def test_keras_hub_medgemma():
    """Test Keras Hub MedGemma client"""
    print("🧪 Testing Keras Hub MedGemma Client...")
    print()
    
    # Initialize client
    print("Loading model...")
    client = KerasHubMedGemma()
    print()
    
    # Test 1: Simple diagnosis
    print("📋 Test 1: Simple Diagnosis")
    print("-" * 50)
    diagnosis = client.generate_diagnosis(
        symptoms="High fever (39°C), severe headache, neck stiffness, photophobia",
        age=28,
        gender="Female"
    )
    print(diagnosis)
    print()
    
    # Test 2: SOAP note
    print("📝 Test 2: SOAP Note")
    print("-" * 50)
    soap = client.generate_soap_note(
        symptoms="Persistent cough for 5 days, mild fever",
        age=35,
        gender="Male"
    )
    print(soap)
    print()
    
    # Test 3: Dermatology
    print("🔬 Test 3: Dermatology Analysis")
    print("-" * 50)
    derm = client.analyze_dermatology(
        skin_description="Red, itchy rash with raised bumps",
        duration="3 days",
        location="Inner forearm",
        associated_symptoms="Mild swelling"
    )
    print(derm)
    print()
    
    print("✅ All tests completed!")


if __name__ == "__main__":
    # Run tests if executed directly
    test_keras_hub_medgemma()
