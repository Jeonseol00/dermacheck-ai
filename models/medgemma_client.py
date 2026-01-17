"""
Med-Gemma Client for Medical Reasoning and Triage Recommendations
Integrates Google's Med-Gemma model for dermatology analysis interpretation
"""
import google.generativeai as genai
from typing import Dict, Optional
from utils.config import Config
import time


class MedGemmaClient:
    """
    Client for Med-Gemma medical AI model
    Provides medical context, risk interpretation, and triage recommendations
    """
    
    def __init__(self):
        """Initialize Med-Gemma client"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        # Initialize model
        # Note: Actual model name may vary - check Google AI Studio for available models
        # For now, using gemini-pro as fallback if med-gemma not directly available
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Warning: Could not load Med-Gemma, using fallback: {e}")
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Configure generation settings
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        # Safety settings
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    
    def analyze_skin_lesion(self, abcde_results: Dict, user_context: Optional[Dict] = None) -> Dict:
        """
        Get medical interpretation and recommendations based on ABCDE analysis
        
        Args:
            abcde_results: Results from ABCDE analyzer
            user_context: Optional user context (age, skin type, history)
            
        Returns:
            Dictionary with interpretation, recommendations, and triage
        """
        prompt = self._build_prompt(abcde_results, user_context)
        
        try:
            # Generate response with retry logic
            response = self._generate_with_retry(prompt)
            
            # Parse response
            result = self._parse_response(response, abcde_results)
            
            return result
            
        except Exception as e:
            # Return fallback response if API fails
            return self._get_fallback_response(abcde_results, str(e))
    
    def _build_prompt(self, abcde_results: Dict, user_context: Optional[Dict]) -> str:
        """
        Build structured prompt for Med-Gemma
        
        Args:
            abcde_results: ABCDE analysis results
            user_context: Optional user context
            
        Returns:
            Formatted prompt string
        """
        scores = abcde_results["abcde_scores"]
        descriptions = abcde_results["descriptions"]
        total_score = abcde_results["total_score"]
        risk_level = abcde_results["risk_level"]
        visual_features = abcde_results["visual_features"]
        
        prompt = f"""You are a dermatology education assistant AI. Provide clear, empathetic guidance based on the following skin lesion screening data.

**IMPORTANT CONTEXT:**
- This is a preliminary screening tool, NOT a medical diagnosis
- Always recommend professional consultation for concerning features
- Use plain, patient-friendly language
- Be reassuring while being medically responsible

**ABCDE SCREENING RESULTS:**

Total Risk Score: {total_score}/11 ({risk_level} RISK)

**Detailed Findings:**

1. **Asymmetry** (Score: {scores['asymmetry']}/2)
   - {descriptions['asymmetry']}

2. **Border** (Score: {scores['border']}/2)
   - {descriptions['border']}

3. **Color** (Score: {scores['color']}/2)
   - {descriptions['color']}

4. **Diameter** (Score: {scores['diameter']}/2)
   - {descriptions['diameter']}
   - Measured size: {visual_features['size_mm']}mm

5. **Evolution** (Score: {scores['evolution']}/3)
   - {descriptions['evolution']}
"""
        
        # Add user context if available
        if user_context:
            prompt += f"\n**PATIENT CONTEXT:**\n"
            if 'age' in user_context:
                prompt += f"- Age: {user_context['age']}\n"
            if 'skin_type' in user_context:
                prompt += f"- Skin type: {user_context['skin_type']}\n"
            if 'family_history' in user_context:
                prompt += f"- Family history: {user_context['family_history']}\n"
        
        prompt += """

**YOUR TASK:**
Please provide a structured response with the following sections:

1. **Plain Language Explanation** (2-3 sentences)
   - Explain what these findings mean in simple terms
   - Avoid medical jargon or explain it clearly

2. **Risk Interpretation** (1-2 sentences)
   - What does this risk level mean practically?
   - Context about similar lesions

3. **Triage Recommendation** (Clear action item)
   - Choose ONE of these recommendations based on risk:
     * LOW: "Continue monitoring at home, check monthly for changes"
     * MEDIUM: "Schedule a dermatologist consultation within 2-4 weeks"
     * HIGH: "Seek professional evaluation within 1 week"
     * URGENT: "Contact healthcare provider immediately"

4. **Educational Points** (2-3 bullet points)
   - Key things to know about this type of finding
   - What to watch for going forward

5. **Questions for Doctor** (3-4 questions)
   - Helpful questions the patient should ask during consultation
   - Specific to these findings

**CRITICAL REMINDER:** End with a clear disclaimer that this is screening, not diagnosis.

Please respond in a warm, professional tone that empowers the patient while being medically responsible.
"""
        
        return prompt
    
    def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response with retry logic
        
        Args:
            prompt: Input prompt
            max_retries: Maximum number generation attempts
            
        Returns:
            Generated response text
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )
                
                return response.text
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise e
    
    def _parse_response(self, response_text: str, abcde_results: Dict) -> Dict:
        """
        Parse Med-Gemma response into structured format
        
        Args:
            response_text: Raw response from model
            abcde_results: Original ABCDE results
            
        Returns:
            Structured response dictionary
        """
        # For now, return as-is with structure
        # In production, could parse into specific fields using regex or LLM
        
        return {
            "interpretation": response_text,
            "risk_level": abcde_results["risk_level"],
            "total_score": abcde_results["total_score"],
            "triage_action": self._extract_triage_action(abcde_results["risk_level"]),
            "urgency_level": self._get_urgency_level(abcde_results["risk_level"]),
            "raw_response": response_text
        }
    
    def _extract_triage_action(self, risk_level: str) -> str:
        """
        Extract triage action based on risk level
        
        Args:
            risk_level: LOW, MEDIUM, or HIGH
            
        Returns:
            Triage action string
        """
        triage_map = {
            "LOW": "Continue monitoring at home. Check monthly for any changes in size, color, or shape.",
            "MEDIUM": "Schedule a dermatologist consultation within 2-4 weeks for professional evaluation.",
            "HIGH": "Seek professional dermatologist evaluation within 1 week. This requires prompt attention."
        }
        
        return triage_map.get(risk_level, "Consult with a healthcare professional")
    
    def _get_urgency_level(self, risk_level: str) -> str:
        """
        Get urgency level for UI display
        
        Args:
            risk_level: LOW, MEDIUM, or HIGH
            
        Returns:
            Urgency string
        """
        urgency_map = {
            "LOW": "routine",
            "MEDIUM": "soon",
            "HIGH": "urgent"
        }
        
        return urgency_map.get(risk_level, "routine")
    
    def _get_fallback_response(self, abcde_results: Dict, error_msg: str) -> Dict:
        """
        Provide fallback response if API fails
        
        Args:
            abcde_results: ABCDE analysis results
            error_msg: Error message
            
        Returns:
            Fallback response dictionary
        """
        risk_level = abcde_results["risk_level"]
        total_score = abcde_results["total_score"]
        
        fallback_text = f"""**Automated Screening Result**

Your skin lesion screening shows a **{risk_level} RISK** level (score: {total_score}/11).

**What this means:**
Based on the ABCDE criteria analysis, this lesion has features that warrant {"immediate attention" if risk_level == "HIGH" else "monitoring"}.

**Recommended Action:**
{self._extract_triage_action(risk_level)}

**Important Reminders:**
- This is a preliminary screening, not a medical diagnosis
- Only a qualified dermatologist can provide a definitive assessment
- When in doubt, always consult a healthcare professional
- Take photos monthly to track any changes

**Note:** The detailed AI analysis is temporarily unavailable. Please consult with a healthcare provider for a comprehensive evaluation.

---
*This screening tool is for educational purposes only and does not replace professional medical advice.*
"""
        
        return {
            "interpretation": fallback_text,
            "risk_level": risk_level,
            "total_score": total_score,
            "triage_action": self._extract_triage_action(risk_level),
            "urgency_level": self._get_urgency_level(risk_level),
            "raw_response": fallback_text,
            "error": f"API unavailable: {error_msg}"
        }
