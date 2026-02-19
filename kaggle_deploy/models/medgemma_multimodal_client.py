"""
MedGemma Multimodal Client - Vision + Text Integration
Supports agent-based multi-step reasoning for dermatology analysis

Author: DermaCheck AI Team
Date: January 30, 2026
Competition: MedGemma Impact Challenge
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from PIL import Image
import logging
from typing import Dict, List, Optional, Union
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedGemmaMultimodalClient:
    """
    MedGemma 4B Multimodal Client with Agent-Based Workflow
    
    Features:
    - Image + Text input support
    - 4-bit quantization for Kaggle T4 GPU
    - Multi-step reasoning (agent workflow)
    - Memory-optimized loading
    """
    
    def __init__(
        self,
        model_name: str = "google/medgemma-1.5-4b-it",  # Updated to 1.5!
        quantize: bool = True,
        device: str = "auto"
    ):
        """
        Initialize MedGemma multimodal client
        
        Args:
            model_name: HuggingFace model ID (now using MedGemma 1.5!)
            quantize: Use 4-bit quantization (recommended for Kaggle T4)
            device: Device placement ("auto", "cuda", "cpu")
        """
        self.model_name = model_name
        self.quantize = quantize
        self.device = device
        
        self.model = None
        self.tokenizer = None
        self.processor = None
        
        # Load model on initialization
        self._load_model()
    
    def _load_model(self):
        """Load MedGemma with multimodal support and quantization"""
        logger.info(f"🔄 Loading MedGemma Multimodal: {self.model_name}")
        start_time = time.time()
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info("✅ Tokenizer loaded")
            
            # Configure quantization if enabled
            if self.quantize:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=bnb_config,
                    device_map=self.device,
                    torch_dtype=torch.float16,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True  # Required for multimodal
                )
                logger.info("✅ Model loaded with 4-bit quantization")
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map=self.device,
                    torch_dtype=torch.float16,
                    trust_remote_code=True
                )
                logger.info("✅ Model loaded (fp16)")
            
            # Log memory usage
            if torch.cuda.is_available():
                mem_allocated = torch.cuda.memory_allocated() / 1e9
                mem_reserved = torch.cuda.memory_reserved() / 1e9
                logger.info(f"📊 GPU Memory - Allocated: {mem_allocated:.2f}GB, Reserved: {mem_reserved:.2f}GB")
            
            load_time = time.time() - start_time
            logger.info(f"⏱️  Model loaded in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"❌ Failed to load MedGemma: {e}")
            raise
    
    def generate_response(
        self,
        prompt: str,
        image: Optional[Union[str, Image.Image]] = None,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response from MedGemma (text-only or multimodal)
        
        Args:
            prompt: Text query/instruction
            image: Optional image (path or PIL Image)
            max_tokens: Maximum generation length
            temperature: Sampling temperature (0=deterministic, 1=creative)
        
        Returns:
            Generated text response
        """
        
        if self.model is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        try:
            # Prepare inputs
            if image is not None:
                # Multimodal: Image + Text
                if isinstance(image, str):
                    image = Image.open(image).convert('RGB')
                
                # Process image + text (MedGemma multimodal format)
                inputs = self.tokenizer(
                    text=prompt,
                    images=image,
                    return_tensors="pt"
                ).to(self.model.device)
                
            else:
                # Text-only
                inputs = self.tokenizer(
                    prompt,
                    return_tensors="pt",
                    truncation=True,
                    max_length=2048
                ).to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True if temperature > 0 else False,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove prompt echo if present
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
        
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return f"Error: {str(e)}"
    
    def analyze_dermatology_agent(
        self,
        image: Union[str, Image.Image],
        body_location: str = "Unknown",
        symptom_history: str = ""
    ) -> Dict:
        """
        Agent-based dermatology analysis (4-step reasoning)
        
        This implements multi-step agentic workflow for bonus prize.
        
        Args:
            image: Skin lesion image
            body_location: Anatomical location
            symptom_history: Patient-reported symptoms/changes
        
        Returns:
            Dict with complete analysis including agent steps
        """
        
        logger.info("🔬 Starting agent-based dermatology analysis...")
        
        results = {
            "agent_steps": [],
            "visual_analysis": {},
            "differential_diagnosis": [],
            "red_flags": [],
            "recommendation": {},
            "processing_time_ms": 0
        }
        
        start_time = time.time()
        
        # STEP 1: Visual Feature Extraction
        logger.info("📸 Agent Step 1: Visual feature extraction...")
        step1_prompt = f"""You are an expert dermatologist analyzing a skin lesion image.

Carefully examine the image and provide a detailed visual description:

1. **Morphology**: Describe the primary lesion type (macule, papule, nodule, plaque, patch, etc.)
2. **Color**: Describe color characteristics (uniform, variegated, shades present)
3. **Border**: Describe border characteristics (well-defined, irregular, notched, blurred)
4. **Asymmetry**: Assess symmetry (symmetric, slightly asymmetric, highly asymmetric)
5. **Size**: Estimate diameter in millimeters
6. **Surface**: Describe surface features (smooth, scaly, crusted, ulcerated)

Respond in structured format with each item clearly labeled.
"""
        
        step1_response = self.generate_response(step1_prompt, image=image, temperature=0.3)
        results["agent_steps"].append({
            "step": 1,
            "name": "Visual Feature Extraction",
            "output": step1_response
        })
        results["visual_analysis"] = self._parse_visual_features(step1_response)
        
        # STEP 2: Differential Diagnosis Generation
        logger.info("🎯 Agent Step 2: Differential diagnosis...")
        step2_prompt = f"""Based on these visual findings from a skin lesion:

{step1_response}

Additional context:
- Body location: {body_location}
- Patient history: {symptom_history if symptom_history else 'No history provided'}

Generate the top 3 differential diagnoses:

For each diagnosis, provide:
1. Condition name
2. ICD-10 code
3. Confidence level (HIGH/MEDIUM/LOW)
4. Key supporting features from the image
5. Typical clinical course

Format as numbered list with clear sections.
"""
        
        step2_response = self.generate_response(step2_prompt, temperature=0.5)
        results["agent_steps"].append({
            "step": 2,
            "name": "Differential Diagnosis",
            "output": step2_response
        })
        results["differential_diagnosis"] = self._parse_differential_dx(step2_response)
        
        # STEP 3: Red Flag Assessment
        logger.info("⚠️  Agent Step 3: Red flag detection...")
        step3_prompt = f"""Review this dermatology case for red flags indicating potential malignancy or urgent conditions:

Visual findings:
{step1_response}

Differential diagnoses:
{step2_response}

Identify any RED FLAGS that suggest:
- Melanoma (ABCDE criteria violations)
- Basal cell carcinoma features
- Squamous cell carcinoma features
- Rapidly growing lesions
- Bleeding/ulceration
- Other concerning features

List each red flag clearly. If NO red flags, state "No immediate red flags identified."
"""
        
        step3_response = self.generate_response(step3_prompt, temperature=0.2)
        results["agent_steps"].append({
            "step": 3,
            "name": "Red Flag Assessment",
            "output": step3_response
        })
        results["red_flags"] = self._parse_red_flags(step3_response)
        
        # STEP 4: Clinical Recommendation
        logger.info("📋 Agent Step 4: Clinical recommendation...")
        step4_prompt = f"""Synthesize this dermatology case and provide clinical recommendations:

Case summary:
- Visual findings: {step1_response[:200]}...
- Top diagnosis: {results['differential_diagnosis'][0]['condition'] if results['differential_diagnosis'] else 'Unknown'}
- Red flags: {len(results['red_flags'])} identified

Provide:
1. **Urgency Classification**: URGENT (within 1 week) / SOON (within 2-4 weeks) / ROUTINE (1-3 months) / REASSURANCE (continue monitoring)
2. **Recommended Specialist**: Dermatologist, Dermatologic oncologist, Primary care, etc.
3. **Suggested Tests**: Biopsy, dermoscopy, imaging, etc.
4. **Home Care**: What patient should do while awaiting appointment
5. **Patient Education**: Key points to explain to patient

Format clearly with section headers.
"""
        
        step4_response = self.generate_response(step4_prompt, temperature=0.4)
        results["agent_steps"].append({
            "step": 4,
            "name": "Clinical Recommendation",
            "output": step4_response
        })
        results["recommendation"] = self._parse_recommendation(step4_response)
        
        # Calculate total processing time
        results["processing_time_ms"] = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Agent analysis complete in {results['processing_time_ms']}ms")
        
        return results
    
    def analyze_with_confidence_scores(
        self,
        image: Union[str, Image.Image],
        body_location: str = "Unknown",
        symptom_history: str = ""
    ) -> str:
        """
        Dermatology analysis with confidence score extraction
        
        This uses structured prompting to get confidence percentages for differential diagnosis.
        Perfect for the competition's confidence visualization feature.
        
        Args:
            image: Skin lesion image
            body_location: Anatomical location
            symptom_history: Patient-reported symptoms/changes
        
        Returns:
            Formatted text response with confidence scores
        """
        
        logger.info("📊 Starting confidence-score analysis...")
        
        prompt = f"""As a dermatology AI assistant, analyze this skin lesion and provide a differential diagnosis with confidence scores.

**CRITICAL INSTRUCTIONS:**
1. Provide PRIMARY diagnosis with confidence percentage (0-100%)
2. List TOP 3 DIFFERENTIAL DIAGNOSES with confidence percentages
3. Use EXACT format shown below (do not deviate)

**Patient Information:**
- Body Location: {body_location}
- Symptom History: {symptom_history if symptom_history else "Not provided"}
- Clinical Image: Provided

**REQUIRED OUTPUT FORMAT:**

PRIMARY DIAGNOSIS: [condition name] (Confidence: XX%)

[Brief 1-2 sentence clinical reasoning for primary diagnosis]

DIFFERENTIAL DIAGNOSES:
1. [condition name] (Confidence: XX%)
   Rationale: [1 sentence why this is considered]

2. [condition name] (Confidence: XX%)
   Rationale: [1 sentence why this is considered]

3. [condition name] (Confidence: XX%)
   Rationale: [1 sentence why this is considered]

RED FLAGS:
[List any concerning features that warrant urgent evaluation, or state "None detected"]

RECOMMENDATION:
Urgency Level: [URGENT/SOON/ROUTINE]
Next Steps: [Specific actionable recommendations]

**Begin differential diagnosis now:**
"""
        
        response = self.generate_response(
            prompt,
            image=image,
            temperature=0.4,  # Balanced temperature for consistency
            max_tokens=800
        )
        
        logger.info("✅ Confidence analysis complete")
        
        return response
    
    def generate_soap_note(
        self,
        symptom_text: str,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        medical_history: Optional[str] = None
    ) -> Dict:
        """
        Generate SOAP note from symptom description
        
        Args:
            symptom_text: Patient's complaint description
            age: Patient age
            gender: Patient gender
            medical_history: Relevant medical history
        
        Returns:
            Dict with SOAP note components and triage level
        """
        
        logger.info("📝 Generating SOAP note...")
        
        prompt = f"""You are a medical AI assistant. Convert this patient complaint into a structured SOAP note.

PATIENT INFORMATION:
- Age: {age if age else 'Not provided'}
- Gender: {gender if gender else 'Not provided'}
- Medical History: {medical_history if medical_history else 'None reported'}

CHIEF COMPLAINT:
{symptom_text}

Generate a complete SOAP note:

**S (SUBJECTIVE):**
- Chief complaint in medical terminology
- History of present illness
- Associated symptoms
- Duration and progression

**O (OBJECTIVE):**
- Vital signs to be measured
- Physical examination findings to assess
- Relevant observations

**A (ASSESSMENT):**
- Top 3 differential diagnoses with ICD-10 codes
- Reasoning for each diagnosis
- Risk factors present

**P (PLAN):**
- Diagnostic tests recommended
- Treatment suggestions
- Referrals needed
- Follow-up timeline
- Patient education points

Also provide:
**TRIAGE LEVEL**: URGENT / SEMI-URGENT / ROUTINE / NON-URGENT

Format with clear section headers and bullet points.
"""
        
        response = self.generate_response(prompt, temperature=0.6)
        
        # Parse SOAP components
        soap_note = {
            "raw_text": response,
            "subjective": self._extract_section(response, "SUBJECTIVE"),
            "objective": self._extract_section(response, "OBJECTIVE"),
            "assessment": self._extract_section(response, "ASSESSMENT"),
            "plan": self._extract_section(response, "PLAN"),
            "triage_level": self._extract_triage(response)
        }
        
        logger.info(f"✅ SOAP note generated - Triage: {soap_note['triage_level']}")
        
        return soap_note
    
    # Helper Methods for Parsing Agent Outputs
    
    def _parse_visual_features(self, text: str) -> Dict:
        """Parse visual feature extraction output"""
        return {
            "morphology": self._extract_field(text, "morphology"),
            "color": self._extract_field(text, "color"),
            "border": self._extract_field(text, "border"),
            "asymmetry": self._extract_field(text, "asymmetry"),
            "size_mm": self._extract_field(text, "size"),
            "surface": self._extract_field(text, "surface")
        }
    
    def _parse_differential_dx(self, text: str) -> List[Dict]:
        """Parse differential diagnosis list"""
        # Simple parsing - can be enhanced with regex
        diagnoses = []
        lines = text.split('\n')
        current_dx = {}
        
        for line in lines:
            if any(str(i) + '.' in line[:3] for i in range(1, 10)):
                if current_dx:
                    diagnoses.append(current_dx)
                current_dx = {"condition": line.strip(), "confidence": "MEDIUM"}
            elif "ICD" in line.upper():
                current_dx["icd10"] = line.split(":")[-1].strip()
            elif "CONFIDENCE" in line.upper() or "LIKELIHOOD" in line.upper():
                if "HIGH" in line.upper():
                    current_dx["confidence"] = "HIGH"
                elif "LOW" in line.upper():
                    current_dx["confidence"] = "LOW"
        
        if current_dx:
            diagnoses.append(current_dx)
        
        return diagnoses[:3]  # Top 3
    
    def _parse_red_flags(self, text: str) -> List[str]:
        """Extract red flags from assessment"""
        if "no red flag" in text.lower() or "no immediate" in text.lower():
            return []
        
        flags = []
        lines = text.split('\n')
        for line in lines:
            if line.strip().startswith('-') or line.strip().startswith('•'):
                flags.append(line.strip().lstrip('-').lstrip('•').strip())
        
        return flags
    
    def _parse_recommendation(self, text: str) -> Dict:
        """Parse clinical recommendation output"""
        return {
            "urgency": self._extract_urgency(text),
            "specialist": self._extract_field(text, "specialist"),
            "tests": self._extract_field(text, "tests"),
            "home_care": self._extract_field(text, "home care"),
            "education": self._extract_field(text, "education")
        }
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract specific field from structured text"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if field_name.lower() in line.lower():
                # Return next line or rest of current line
                if ':' in line:
                    return line.split(':', 1)[1].strip()
                elif i + 1 < len(lines):
                    return lines[i + 1].strip()
        return "Not specified"
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract SOAP section content"""
        lines = text.split('\n')
        in_section = False
        section_content = []
        
        for line in lines:
            if section_name in line.upper():
                in_section = True
                continue
            elif in_section and any(s in line.upper() for s in ['SUBJECTIVE', 'OBJECTIVE', 'ASSESSMENT', 'PLAN', 'TRIAGE']):
                break
            elif in_section:
                section_content.append(line.strip())
        
        return '\n'.join(section_content).strip()
    
    def _extract_urgency(self, text: str) -> str:
        """Extract urgency level"""
        text_upper = text.upper()
        if "URGENT" in text_upper and "NON-URGENT" not in text_upper and "SEMI" not in text_upper:
            return "URGENT"
        elif "SEMI-URGENT" in text_upper:
            return "SEMI-URGENT"
        elif "ROUTINE" in text_upper:
            return "ROUTINE"
        elif "NON-URGENT" in text_upper or "REASSURANCE" in text_upper:
            return "NON-URGENT"
        else:
            return "ROUTINE"
    
    def _extract_triage(self, text: str) -> str:
        """Extract triage level from SOAP note"""
        return self._extract_urgency(text)
    
    def unload_model(self):
        """Free GPU memory by unloading model"""
        if self.model is not None:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache()
            self.model = None
            self.tokenizer = None
            logger.info("🗑️  Model unloaded, GPU memory freed")
    
    def get_memory_usage(self) -> Dict:
        """Get current GPU memory usage"""
        if torch.cuda.is_available():
            return {
                "allocated_gb": torch.cuda.memory_allocated() / 1e9,
                "reserved_gb": torch.cuda.memory_reserved() / 1e9,
                "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9
            }
        return {"error": "CUDA not available"}


# Example usage
if __name__ == "__main__":
    print("🔬 Testing MedGemma Multimodal Client...")
    
    # Initialize client
    client = MedGemmaMultimodalClient(quantize=True)
    
    # Test text-only (SOAP note)
    print("\n📝 Test 1: SOAP Note Generation")
    soap = client.generate_soap_note(
        symptom_text="Sakit kepala hebat 2 hari, muntah, demam tinggi 39°C",
        age=35,
        gender="Female"
    )
    print(f"Triage: {soap['triage_level']}")
    print(f"Assessment: {soap['assessment'][:100]}...")
    
    # Memory usage
    print(f"\n📊 Memory Usage: {client.get_memory_usage()}")
    
    print("\n✅ Client test complete!")
