"""
Confidence Score Extraction and Visualization Component
For DermaCheck AI - MedGemma Impact Challenge

This module provides:
1. Prompt engineering for confidence score extraction
2. Parser for extracting confidence percentages from AI output
3. HTML/CSS visualization for progress bars
"""

import re
from typing import Dict, List, Tuple, Optional


class ConfidenceScoreExtractor:
    """
    Extract confidence scores from MedGemma responses using prompt engineering
    """
    
    @staticmethod
    def create_confidence_prompt(
        body_location: str,
        symptom_history: str,
        include_image: bool = True
    ) -> str:
        """
        Create structured prompt for confidence score extraction
        
        Args:
            body_location: Location on body
            symptom_history: Patient's symptom description
            include_image: Whether image is included
            
        Returns:
            Formatted prompt string
        """
        
        prompt = f"""As a dermatology AI assistant, analyze this skin lesion and provide a differential diagnosis with confidence scores.

**CRITICAL INSTRUCTIONS:**
1. Provide PRIMARY diagnosis with confidence percentage (0-100%)
2. List TOP 3 DIFFERENTIAL DIAGNOSES with confidence percentages
3. Use EXACT format shown below (do not deviate)

**Patient Information:**
- Body Location: {body_location}
- Symptom History: {symptom_history if symptom_history else "Not provided"}
{"- Clinical Image: Provided" if include_image else ""}

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
        
        return prompt
    
    @staticmethod
    def parse_confidence_response(ai_response: str) -> Dict:
        """
        Parse AI response to extract structured confidence data
        
        Args:
            ai_response: Raw text output from MedGemma
            
        Returns:
            Dictionary containing:
                - primary: {diagnosis, confidence, rationale}
                - differentials: List of {diagnosis, confidence, rationale}
                - red_flags: List of strings
                - recommendation: {urgency, next_steps}
        """
        
        result = {
            "primary": None,
            "differentials": [],
            "red_flags": [],
            "recommendation": {}
        }
        
        try:
            # Parse PRIMARY DIAGNOSIS
            primary_pattern = r"PRIMARY DIAGNOSIS:\s*(.+?)\s*\(Confidence:\s*(\d+)%\)"
            primary_match = re.search(primary_pattern, ai_response, re.IGNORECASE)
            
            if primary_match:
                diagnosis_name = primary_match.group(1).strip()
                confidence = int(primary_match.group(2))
                
                # Extract rationale (text after primary diagnosis until DIFFERENTIAL section)
                rationale_pattern = r"PRIMARY DIAGNOSIS:.*?\n\n(.*?)\n\nDIFFERENTIAL"
                rationale_match = re.search(rationale_pattern, ai_response, re.DOTALL | re.IGNORECASE)
                rationale = rationale_match.group(1).strip() if rationale_match else ""
                
                result["primary"] = {
                    "diagnosis": diagnosis_name,
                    "confidence": confidence,
                    "rationale": rationale
                }
            
            # Parse DIFFERENTIAL DIAGNOSES
            diff_pattern = r"\d+\.\s*(.+?)\s*\(Confidence:\s*(\d+)%\)\s*(?:Rationale:\s*(.+?))(?=\n\d+\.|RED FLAGS|RECOMMENDATION|$)"
            diff_matches = re.findall(diff_pattern, ai_response, re.DOTALL | re.IGNORECASE)
            
            for match in diff_matches[:3]:  # Top 3 only
                diagnosis_name = match[0].strip()
                confidence = int(match[1])
                rationale = match[2].strip() if len(match) > 2 else ""
                
                result["differentials"].append({
                    "diagnosis": diagnosis_name,
                    "confidence": confidence,
                    "rationale": rationale
                })
            
            # Parse RED FLAGS
            red_flags_pattern = r"RED FLAGS:\s*\n(.*?)(?=\n\nRECOMMENDATION|$)"
            red_flags_match = re.search(red_flags_pattern, ai_response, re.DOTALL | re.IGNORECASE)
            
            if red_flags_match:
                red_flags_text = red_flags_match.group(1).strip()
                # Split by lines, remove bullets/numbers
                flags = [
                    re.sub(r"^[-*•\d.)\s]+", "", line).strip() 
                    for line in red_flags_text.split("\n") 
                    if line.strip() and "none detected" not in line.lower()
                ]
                result["red_flags"] = flags
            
            # Parse RECOMMENDATION
            urgency_pattern = r"Urgency Level:\s*(\w+)"
            next_steps_pattern = r"Next Steps:\s*(.+?)(?=\n\n|\Z)"
            
            urgency_match = re.search(urgency_pattern, ai_response, re.IGNORECASE)
            next_steps_match = re.search(next_steps_pattern, ai_response, re.DOTALL | re.IGNORECASE)
            
            result["recommendation"] = {
                "urgency": urgency_match.group(1).upper() if urgency_match else "ROUTINE",
                "next_steps": next_steps_match.group(1).strip() if next_steps_match else ""
            }
            
        except Exception as e:
            print(f"⚠️ Parsing error: {e}")
            # Return partial results if parsing fails
        
        return result


class ConfidenceVisualizer:
    """
    Generate HTML/CSS visualizations for confidence scores
    """
    
    @staticmethod
    def generate_progress_bar(
        diagnosis: str,
        confidence: int,
        rationale: str = "",
        is_primary: bool = False
    ) -> str:
        """
        Generate HTML/CSS for a single confidence progress bar
        
        Args:
            diagnosis: Diagnosis name
            confidence: Confidence percentage (0-100)
            rationale: Clinical rationale
            is_primary: Whether this is the primary diagnosis
            
        Returns:
            HTML string with embedded CSS
        """
        
        # Color coding based on confidence level
        if confidence >= 80:
            bar_color = "#10b981"  # Green - high confidence
            text_color = "#065f46"
        elif confidence >= 60:
            bar_color = "#3b82f6"  # Blue - moderate confidence
            text_color = "#1e40af"
        elif confidence >= 40:
            bar_color = "#f59e0b"  # Orange - low-moderate confidence
            text_color = "#92400e"
        else:
            bar_color = "#ef4444"  # Red - low confidence
            text_color = "#991b1b"
        
        # Border style for primary diagnosis
        border_style = "border: 3px solid #4f46e5;" if is_primary else "border: 2px solid #e5e7eb;"
        
        html = f"""
        <div style="{border_style} border-radius: 12px; padding: 16px; margin-bottom: 12px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 600; font-size: 16px; color: #1f2937;">
                    {"🎯 PRIMARY: " if is_primary else ""}
                    {diagnosis}
                </div>
                <div style="font-weight: 700; font-size: 18px; color: {text_color};">
                    {confidence}%
                </div>
            </div>
            
            <div style="background: #e5e7eb; border-radius: 999px; height: 24px; overflow: hidden; margin-bottom: 8px;">
                <div style="background: {bar_color}; height: 100%; width: {confidence}%; transition: width 0.6s ease-in-out; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;">
                    <span style="color: white; font-size: 12px; font-weight: 600;">{"█" * min(confidence // 5, 20)}</span>
                </div>
            </div>
            
            {f'<div style="font-size: 13px; color: #6b7280; margin-top: 6px;"><em>{rationale}</em></div>' if rationale else ''}
        </div>
        """
        
        return html
    
    @staticmethod
    def generate_full_visualization(parsed_data: Dict) -> str:
        """
        Generate complete HTML visualization for all diagnoses
        
        Args:
            parsed_data: Parsed confidence data from extract method
            
        Returns:
            Complete HTML string with all visualizations
        """
        
        html = """
        <div style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; max-width: 700px; margin: 16px 0;">
            <h3 style="color: #1f2937; font-size: 20px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                <span style="font-size: 24px; margin-right: 8px;">📊</span>
                Differential Diagnosis with Confidence Scores
            </h3>
        """
        
        #Primary diagnosis
        if parsed_data.get("primary"):
            primary = parsed_data["primary"]
            html += ConfidenceVisualizer.generate_progress_bar(
                diagnosis=primary["diagnosis"],
                confidence=primary["confidence"],
                rationale=primary.get("rationale", ""),
                is_primary=True
            )
        
        # Differential diagnoses
        if parsed_data.get("differentials"):
            html += """
            <div style="margin-top: 20px; margin-bottom: 12px;">
                <h4 style="color: #374151; font-size: 16px; font-weight: 600; margin-bottom: 12px;">
                    Alternative Considerations:
                </h4>
            </div>
            """
            
            for idx, diff in enumerate(parsed_data["differentials"], 1):
                html += ConfidenceVisualizer.generate_progress_bar(
                    diagnosis=f"{idx}. {diff['diagnosis']}",
                    confidence=diff["confidence"],
                    rationale=diff.get("rationale", ""),
                    is_primary=False
                )
        
        # Red flags section
        if parsed_data.get("red_flags") and len(parsed_data["red_flags"]) > 0:
            html += """
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 12px 16px; border-radius: 8px; margin-top: 16px;">
                <div style="font-weight: 600; color: #991b1b; margin-bottom: 8px; font-size: 15px;">
                    ⚠️ RED FLAGS DETECTED
                </div>
                <ul style="margin: 0; padding-left: 20px; color: #7f1d1d;">
            """
            
            for flag in parsed_data["red_flags"]:
                html += f"<li style='margin-bottom: 4px;'>{flag}</li>"
            
            html += """
                </ul>
            </div>
            """
        else:
            html += """
            <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 8px; margin-top: 16px;">
                <div style="font-weight: 600; color: #065f46; font-size: 15px;">
                    ✅ No Immediate Red Flags Detected
                </div>
            </div>
            """
        
        # Recommendation section
        if parsed_data.get("recommendation"):
            rec = parsed_data["recommendation"]
            urgency = rec.get("urgency", "ROUTINE")
            
            urgency_colors = {
                "URGENT": ("#fee2e2", "#991b1b", "🚨"),
                "SOON": ("#fef3c7", "#92400e", "⚠️"),
                "ROUTINE": ("#dbeafe", "#1e40af", "📅")
            }
            
            bg_color, text_color, emoji = urgency_colors.get(urgency, urgency_colors["ROUTINE"])
            
            html += f"""
            <div style="background: {bg_color}; border-radius: 8px; padding: 14px; margin-top: 16px;">
                <div style="font-weight: 600; color: {text_color}; margin-bottom: 6px; font-size: 15px;">
                    {emoji} Recommendation: {urgency}
                </div>
                <div style="color: {text_color}; font-size: 14px;">
                    {rec.get('next_steps', '')}
                </div>
            </div>
            """
        
        html += """
            <div style="margin-top: 16px; padding: 12px; background: #fef9c3; border-radius: 8px; font-size: 13px; color: #854d0e;">
                <strong>⚠️ DISCLAIMER:</strong> These confidence scores are AI-generated estimates for preliminary screening only. 
                They should NOT be used as definitive diagnostic probabilities. Always consult a qualified dermatologist for professional evaluation.
            </div>
        </div>
        """
        
        return html


# ============================================
# USAGE EXAMPLE
# ============================================

if __name__ == "__main__":
    # Example AI response
    example_response = """
    PRIMARY DIAGNOSIS: Basal Cell Carcinoma (Confidence: 75%)
    
    The lesion shows characteristic pearly borders with central ulceration, highly suggestive of BCC. 
    Telangiectasias visible on surface. Location on sun-exposed area increases likelihood.
    
    DIFFERENTIAL DIAGNOSES:
    1. Squamous Cell Carcinoma (Confidence: 60%)
       Rationale: Crusty appearance and rapid growth could indicate SCC, though less likely given smooth borders.
    
    2. Melanoma (Confidence: 45%)
       Rationale: Irregular pigmentation warrants exclusion of melanoma, despite low suspicion based on morphology.
    
    3. Seborrheic Keratosis (Confidence: 30%)
       Rationale: Benign lesion possible, but lacks typical "stuck-on" appearance.
    
    RED FLAGS:
    - Irregular border with central ulceration
    - Located on chronically sun-exposed area (face)
    - Patient reports progressive growth over 18 months
    
    RECOMMENDATION:
    Urgency Level: SOON
    Next Steps: Dermatology referral within 2 weeks for biopsy. Avoid sun exposure. Do not attempt home remedies.
    """
    
    # Test extraction
    extractor = ConfidenceScoreExtractor()
    parsed = extractor.parse_confidence_response(example_response)
    
    print("=" * 60)
    print("PARSED DATA:")
    print("=" * 60)
    print(f"Primary: {parsed['primary']}")
    print(f"\nDifferentials: {len(parsed['differentials'])} found")
    for diff in parsed['differentials']:
        print(f"  - {diff}")
    print(f"\nRed Flags: {parsed['red_flags']}")
    print(f"\nRecommendation: {parsed['recommendation']}")
    
    # Test visualization
    visualizer = ConfidenceVisualizer()
    html_output = visualizer.generate_full_visualization(parsed)
    
    print("\n" + "=" * 60)
    print("HTML VISUALIZATION GENERATED")
    print("=" * 60)
    print(f"Length: {len(html_output)} characters")
    
    # Save to file for testing
    with open("/tmp/confidence_viz_test.html", "w") as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Confidence Score Test</title>
        </head>
        <body style="padding: 40px; background: #f9fafb;">
            {html_output}
        </body>
        </html>
        """)
    
    print("✅ Test HTML saved to /tmp/confidence_viz_test.html")
