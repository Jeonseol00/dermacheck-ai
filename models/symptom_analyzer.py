"""
Symptom Analyzer - Module B
Converts patient symptoms (free text) to structured SOAP medical notes
Uses Med-Gemma for medical entity extraction and formatting
"""
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime
from utils.config import Config
import re


class SymptomAnalyzer:
    """
    Analyzes patient-reported symptoms and generates structured medical documentation
    """
    
    def __init__(self):
        """Initialize symptom analyzer with Med-Gemma"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured for symptom analysis")
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        # Use Med-Gemma or Gemini Pro for medical text generation
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Warning: Could not load Med-Gemma, using fallback: {e}")
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Configure for medical documentation
        self.generation_config = {
            "temperature": 0.3,  # Lower for more factual, consistent output
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    
    def analyze_symptoms(self, symptoms_text: str, patient_context: Optional[Dict] = None) -> Dict:
        """
        Analyze patient symptoms and generate SOAP note
        
        Args:
            symptoms_text: Free-text description of symptoms from patient
            patient_context: Optional patient info (age, gender, medical history)
            
        Returns:
            Dictionary with SOAP note components and metadata
        """
        # Build comprehensive prompt
        prompt = self._build_soap_prompt(symptoms_text, patient_context)
        
        try:
            # Generate SOAP note
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            soap_text = response.text
            
            # Parse structured SOAP components
            parsed_soap = self._parse_soap_response(soap_text)
            
            # Extract key entities
            entities = self._extract_medical_entities(symptoms_text, soap_text)
            
            # Generate triage level
            triage = self._determine_triage_level(parsed_soap, entities)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "raw_input": symptoms_text,
                "soap_note": parsed_soap,
                "medical_entities": entities,
                "triage": triage,
                "raw_response": soap_text,
                "status": "success"
            }
            
        except Exception as e:
            return self._get_fallback_response(symptoms_text, str(e))
    
    def _build_soap_prompt(self, symptoms: str, context: Optional[Dict]) -> str:
        """
        Build detailed prompt for Med-Gemma to generate SOAP note
        
        Args:
            symptoms: Patient symptom description
            context: Optional patient context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an experienced medical scribe AI assistant helping to document patient consultations.

**Your Role:**
- Convert patient's informal complaint into professional SOAP note format
- Extract key medical entities (symptoms, duration, severity, location)
- Translate layman terms to medical terminology
- Provide differential diagnoses for physician review
- Suggest appropriate next steps

**Patient Input:**
"{symptoms}"
"""
        
        if context:
            prompt += f"\n**Patient Context:**\n"
            if 'age' in context:
                prompt += f"- Age: {context['age']} years\n"
            if 'gender' in context:
                prompt += f"- Gender: {context['gender']}\n"
            if 'medical_history' in context:
                prompt += f"- Medical History: {context['medical_history']}\n"
        
        prompt += """

**Generate a structured SOAP note with the following format:**

**S (SUBJECTIVE):**
- Chief Complaint: [Main symptom in medical terminology]
- History of Present Illness (HPI):
  - Onset: [When symptoms started]
  - Duration: [How long]
  - Location: [Where on body]
  - Quality: [Description of pain/sensation]
  - Severity: [Mild/Moderate/Severe on scale 1-10]
  - Associated symptoms: [Other symptoms]
  - Aggravating/Relieving factors: [What makes it worse/better]

**O (OBJECTIVE):**
- Vital Signs: [To be measured - note what should be checked]
- Physical Examination Findings: [What doctor should examine]
- [If skin lesion from image analysis was mentioned, note it here]

**A (ASSESSMENT):**
- Differential Diagnoses (in order of likelihood):
  1. [Most likely diagnosis with brief rationale]
  2. [Second possibility]
  3. [Third possibility - if applicable]
- Clinical Impression: [Summary assessment]

**P (PLAN):**
- Diagnostic Tests:
  - [Lab tests to order, if any]
  - [Imaging studies, if indicated]
- Treatment:
  - Medications: [If symptomatic treatment appropriate]
  - Non-pharmacological: [Rest, diet, etc.]
- Follow-up:
  - Schedule: [When to return]
  - Warning signs: [Red flags to watch for]
- Referrals: [If specialist consultation needed]

**CRITICAL REMINDERS:**
1. Use proper medical terminology but explain complex terms
2. Be specific with anatomical locations (e.g., "left upper extremity" not "arm")
3. Include time-based information (onset, duration)
4. Assessment should be differential, not definitive diagnosis
5. Plans should be actionable and safe
6. Always include red flag warnings

Generate the SOAP note now:
"""
        
        return prompt
    
    def _parse_soap_response(self, soap_text: str) -> Dict:
        """
        Parse SOAP response into structured components
        
        Args:
            soap_text: Raw SOAP note text from LLM
            
        Returns:
            Dictionary with S, O, A, P components
        """
        # Extract sections using regex
        sections = {
            'subjective': '',
            'objective': '',
            'assessment': '',
            'plan': ''
        }
        
        # Find each section
        patterns = {
            'subjective': r'\*\*S.*?SUBJECTIVE.*?\*\*:?(.*?)(?=\*\*O|\*\*OBJECTIVE|\Z)',
            'objective': r'\*\*O.*?OBJECTIVE.*?\*\*:?(.*?)(?=\*\*A|\*\*ASSESSMENT|\Z)',
            'assessment': r'\*\*A.*?ASSESSMENT.*?\*\*:?(.*?)(?=\*\*P|\*\*PLAN|\Z)',
            'plan': r'\*\*P.*?PLAN.*?\*\*:?(.*?)(?=\Z)'
        }
        
        for section, pattern in patterns.items():
            match = re.search(pattern, soap_text, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section] = match.group(1).strip()
        
        # If regex fails, use simple split
        if not any(sections.values()):
            parts = soap_text.split('**')
            for i, part in enumerate(parts):
                if 'SUBJECTIVE' in part.upper() and i+1 < len(parts):
                    sections['subjective'] = parts[i+1].strip()
                elif 'OBJECTIVE' in part.upper() and i+1 < len(parts):
                    sections['objective'] = parts[i+1].strip()
                elif 'ASSESSMENT' in part.upper() and i+1 < len(parts):
                    sections['assessment'] = parts[i+1].strip()
                elif 'PLAN' in part.upper() and i+1 < len(parts):
                    sections['plan'] = parts[i+1].strip()
        
        return sections
    
    def _extract_medical_entities(self, original_text: str, soap_text: str) -> Dict:
        """
        Extract key medical entities from text
        
        Args:
            original_text: Patient's original input
            soap_text: Generated SOAP note
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            'symptoms': [],
            'duration': None,
            'severity': None,
            'location': [],
            'red_flags': []
        }
        
        # Common symptom keywords
        symptom_keywords = [
            'fever', 'pain', 'cough', 'rash', 'headache', 'nausea', 
            'vomiting', 'dizziness', 'fatigue', 'bleeding', 'swelling',
            'demam', 'sakit', 'batuk', 'gatal', 'pusing', 'lemas'
        ]
        
        text_lower = original_text.lower()
        for keyword in symptom_keywords:
            if keyword in text_lower:
                entities['symptoms'].append(keyword)
        
        # Extract duration patterns
        duration_patterns = [
            r'(\d+)\s*(hari|day|minggu|week|bulan|month)',
            r'sejak\s+(\d+)',
            r'selama\s+(\d+)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities['duration'] = match.group(0)
                break
        
        # Red flag detection
        red_flags = [
            'chest pain', 'difficulty breathing', 'severe bleeding',
            'unconscious', 'seizure', 'nyeri dada', 'sesak napas'
        ]
        
        for flag in red_flags:
            if flag in text_lower:
                entities['red_flags'].append(flag)
        
        return entities
    
    def _determine_triage_level(self, soap: Dict, entities: Dict) -> Dict:
        """
        Determine urgency/triage level based on SOAP and entities
        
        Args:
            soap: Parsed SOAP note
            entities: Extracted entities
            
        Returns:
            Dictionary with triage level and reasoning
        """
        # Check for red flags
        if entities['red_flags']:
            return {
                'level': 'URGENT',
                'color': 'red',
                'recommendation': 'Seek immediate medical attention',
                'reasoning': f"Red flag symptoms detected: {', '.join(entities['red_flags'])}"
            }
        
        # Check assessment for keywords
        assessment = soap.get('assessment', '').lower()
        
        urgent_keywords = ['emergency', 'acute', 'severe', 'critical']
        semi_urgent_keywords = ['moderate', 'persistent', 'worsening']
        
        if any(keyword in assessment for keyword in urgent_keywords):
            return {
                'level': 'SEMI-URGENT',
                'color': 'orange',
                'recommendation': 'Schedule appointment within 24-48 hours',
                'reasoning': 'Potentially serious condition requiring prompt evaluation'
            }
        elif any(keyword in assessment for keyword in semi_urgent_keywords):
            return {
                'level': 'ROUTINE',
                'color': 'yellow',
                'recommendation': 'Schedule appointment within 1 week',
                'reasoning': 'Condition warrants medical evaluation but not urgent'
            }
        else:
            return {
                'level': 'NON-URGENT',
                'color': 'green',
                'recommendation': 'Schedule routine appointment or monitor at home',
                'reasoning': 'Symptoms appear manageable with routine care'
            }
    
    def _get_fallback_response(self, symptoms: str, error: str) -> Dict:
        """
        Provide fallback response if AI generation fails
        
        Args:
            symptoms: Original symptom text
            error: Error message
            
        Returns:
            Basic structured response
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "raw_input": symptoms,
            "soap_note": {
                "subjective": f"Patient reports: {symptoms}",
                "objective": "[Physical examination pending]",
                "assessment": "[Requires physician evaluation - AI analysis unavailable]",
                "plan": "Schedule in-person consultation for complete assessment"
            },
            "medical_entities": {
                "symptoms": [],
                "duration": None,
                "severity": None,
                "location": [],
                "red_flags": []
            },
            "triage": {
                'level': 'ROUTINE',
                'color': 'yellow',
                'recommendation': 'Schedule medical consultation',
                'reasoning': 'Unable to complete automated triage - human review needed'
            },
            "raw_response": f"Error: {error}",
            "status": "error"
        }
