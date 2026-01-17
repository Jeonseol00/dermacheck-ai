"""
Symptom Analyzer - Module B (v2.0.5)
Converts patient symptoms (free text) to structured SOAP medical notes
Uses Gemini 2.5 Flash for medical entity extraction and formatting
"""
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime
from utils.config import Config
import re
import json


class SymptomAnalyzer:
    """
    Analyzes patient-reported symptoms and generates structured medical documentation
    """
    
    def __init__(self):
        """Initialize symptom analyzer with latest Gemini models"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured for symptom analysis")
        
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        
        # Use latest Gemini models (January 2026)
        # Hierarchy: 2.5 Flash (stable) → 3.0 Flash (experimental) → legacy
        try:
            # Primary: Gemini 2.5 Flash (STABLE - June 2025 GA)
            # Best for production: predictable latency, proven reliability
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print("Using Gemini 2.5 Flash (stable)")
        except Exception as e:
            print(f"Gemini 2.5 Flash unavailable: {e}, trying 3.0 Flash...")
            try:
                # Fallback 1: Gemini 3.0 Flash (LATEST - Dec 2025 preview)
                # Frontier intelligence, fastest, but newer/experimental
                self.model = genai.GenerativeModel('gemini-3-flash')
                print("Using Gemini 3.0 Flash (latest experimental)")
            except Exception as e2:
                print(f"Gemini 3.0 Flash unavailable: {e2}, trying legacy...")
                try:
                    # Fallback 2: Gemini 1.5 Flash (older stable)
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    print("Using Gemini 1.5 Flash (legacy)")
                except Exception as e3:
                    # Last resort: basic gemini
                    print(f"All modern models unavailable: {e3}, using basic gemini-pro")
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
        Build detailed prompt for Gemini to generate SOAP note
        
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

**IMPORTANT: Use this EXACT format with clear section headers. ALL 4 SECTIONS ARE MANDATORY:**

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
- [If no data: write "Pending physical examination"]

**A (ASSESSMENT):**
- Differential Diagnoses (in order of likelihood):
  1. [Most likely diagnosis with brief rationale]
  2. [Second possibility]
  3. [Third possibility - if applicable]
- Clinical Impression: [Summary assessment]

**P (PLAN):**
- Diagnostic Tests: [Specific tests recommended]
- Treatment: [Medications and non-pharmacological interventions]
- Follow-up: [When to return and warning signs]
- Referrals: [If specialist consultation needed]

**CRITICAL FORMATTING REQUIREMENTS:**
1. Start each main section with the EXACT header format: **S (SUBJECTIVE):**
2. Include ALL 4 sections (S, O, A, P) - even if brief
3. Use proper medical terminology
4. Be specific with anatomical locations
5. Include time-based information
6. Assessment should be differential, not definitive
7. Plans must be actionable and safe

Generate the complete SOAP note now with ALL 4 sections:
"""
        
        return prompt
    
    def _parse_soap_response(self, soap_text: str) -> Dict:
        """
        Parse SOAP response into structured components
        v2.0.5: Ultra-lenient parsing for Gemini 2.5 format variations
        
        Args:
            soap_text: Raw SOAP note text from LLM
            
        Returns:
            Dictionary with S, O, A, P components
        """
        sections = {
            'subjective': '',
            'objective': '',
            'assessment': '',
            'plan': ''
        }
        
        # STRATEGY 1: Try multiple flexible regex patterns
        pattern_variants = [
            # Variant 1: **S (SUBJECTIVE):** format
            {
                'subjective': r'\*\*\s*S\s*[\(\-]*\s*SUBJECTIVE\s*[\)\s]*:?\s*\*\*\s*(.*?)(?=\*\*\s*O\s*[\(\-]|$)',
                'objective': r'\*\*\s*O\s*[\(\-]*\s*OBJECTIVE\s*[\)\s]*:?\s*\*\*\s*(.*?)(?=\*\*\s*A\s*[\(\-]|$)',
                'assessment': r'\*\*\s*A\s*[\(\-]*\s*ASSESSMENT\s*[\)\s]*:?\s*\*\*\s*(.*?)(?=\*\*\s*P\s*[\(\-]|$)',
                'plan': r'\*\*\s*P\s*[\(\-]*\s*PLAN\s*[\)\s]*:?\s*\*\*\s*(.*?)$'
            },
            # Variant 2: **SUBJECTIVE:** format (no S prefix)
            {
                'subjective': r'\*\*\s*SUBJECTIVE\s*:?\s*\*\*\s*(.*?)(?=\*\*\s*OBJECTIVE|$)',
                'objective': r'\*\*\s*OBJECTIVE\s*:?\s*\*\*\s*(.*?)(?=\*\*\s*ASSESSMENT|$)',
                'assessment': r'\*\*\s*ASSESSMENT\s*:?\s*\*\*\s*(.*?)(?=\*\*\s*PLAN|$)',
                'plan': r'\*\*\s*PLAN\s*:?\s*\*\*\s*(.*?)$'
            }
        ]
        
        for pattern_set in pattern_variants:
            temp_sections = {}
            all_found = True
            
            for section, pattern in pattern_set.items():
                match = re.search(pattern, soap_text, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    content = re.sub(r'^\*+|\*+$', '', content).strip()
                    temp_sections[section] = content
                else:
                    all_found = False
                    break
            
            if all_found and temp_sections['subjective']:
                sections = temp_sections
                break
        
        # STRATEGY 2: Line-by-line parsing if regex failed
        if not sections['subjective']:
            lines = soap_text.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line_clean = line.strip()
                line_upper = line_clean.upper()
                
                # Check for section headers
                is_header = False
                if 'SUBJECTIVE' in line_upper and ('**S' in line or '**SUBJECTIVE' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'subjective'
                    current_content = []
                    is_header = True
                elif 'OBJECTIVE' in line_upper and ('**O' in line or '**OBJECTIVE' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'objective'
                    current_content = []
                    is_header = True
                elif 'ASSESSMENT' in line_upper and ('**A' in line or '**ASSESSMENT' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'assessment'
                    current_content = []
                    is_header = True
                elif 'PLAN' in line_upper and ('**P' in line or '**PLAN' in line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = 'plan'
                    current_content = []
                    is_header = True
                elif current_section and not is_header:
                    current_content.append(line_clean)
            
            # Save last section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
        
        # Ensure sensible defaults for empty sections
        if not sections['objective']:
            sections['objective'] = "No objective data provided (pending physical examination)"
        if not sections['assessment']:
            sections['assessment'] = "[Assessment parsing failed - please review AI response above or consult healthcare provider]"
        if not sections['plan']:
            sections['plan'] = "[Plan parsing failed - please consult healthcare provider for recommendations]"
        
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
