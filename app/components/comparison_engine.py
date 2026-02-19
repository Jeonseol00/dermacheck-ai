"""
Side-by-Side Lesion Comparison Engine
Compare two skin lesions and highlight differences
"""

from typing import Dict, Optional, Tuple
import re

class LesionComparator:
    """Compare two skin lesions side-by-side"""
    
    def __init__(self):
        """Initialize comparator"""
        pass
    
    def extract_diagnosis_data(self, ai_response: str) -> Dict:
        """
        Extract structured data from AI response
        
        Args:
            ai_response: Raw MedGemma analysis text
            
        Returns:
            Dictionary with extracted diagnosis info
        """
        data = {
            "primary_diagnosis": "Unknown",
            "confidence": 0,
            "risk_level": "UNKNOWN",
            "features": [],
            "recommendation": "Consult dermatologist"
        }
        
        try:
            # Extract primary diagnosis (first mentioned condition)
            diagnosis_pattern = r"(?:diagnosis|condition|consistent with|suggests|appears to be|likely)\s*:?\s*([A-Za-z\s]+)"
            diagnosis_match = re.search(diagnosis_pattern, ai_response, re.IGNORECASE)
            if diagnosis_match:
                data["primary_diagnosis"] = diagnosis_match.group(1).strip().title()
            
            # Extract confidence (percentage)
            confidence_pattern = r"(\d{1,3})\s*%"
            confidence_matches = re.findall(confidence_pattern, ai_response)
            if confidence_matches:
                # Take highest confidence
                data["confidence"] = max(int(c) for c in confidence_matches)
            
            # Determine risk level
            if any(word in ai_response.lower() for word in ["urgent", "immediate", "emergency", "malignant"]):
                data["risk_level"] = "HIGH"
            elif any(word in ai_response.lower() for word in ["moderate", "monitor", "follow-up"]):
                data["risk_level"] = "MEDIUM"
            else:
                data["risk_level"] = "LOW"
            
            # Extract features
            feature_keywords = ["asymmetry", "border", "color", "diameter", "evolution", "irregular", "pigment"]
            data["features"] = [kw for kw in feature_keywords if kw in ai_response.lower()]
            
            # Extract recommendation
            rec_pattern = r"(?:recommend|should|advise|suggest)\s*:?\s*([^.]+)"
            rec_match = re.search(rec_pattern, ai_response, re.IGNORECASE)
            if rec_match:
                data["recommendation"] = rec_match.group(1).strip()
        
        except Exception as e:
            print(f"Error extracting data: {e}")
        
        return data
    
    def compare_lesions(self, data_a: Dict, data_b: Dict) -> str:
        """
        Generate comparison report
        
        Args:
            data_a: Extracted data from Image A
            data_b: Extracted data from Image B
            
        Returns:
            Formatted markdown comparison
        """
        # Risk level emojis
        risk_emoji = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "UNKNOWN": "⚪"
        }
        
        # Build comparison table
        comparison = f"""
## 🔬 Side-by-Side Comparison Results

### 📊 Summary Table

| Feature | 📸 Image A | 📸 Image B |
|---------|-----------|-----------|
| **Primary Diagnosis** | {data_a['primary_diagnosis']} | {data_b['primary_diagnosis']} |
| **Confidence Score** | {data_a['confidence']}% | {data_b['confidence']}% |
| **Risk Level** | {risk_emoji.get(data_a['risk_level'], '⚪')} {data_a['risk_level']} | {risk_emoji.get(data_b['risk_level'], '⚪')} {data_b['risk_level']} |
| **Features Detected** | {len(data_a['features'])} features | {len(data_b['features'])} features |

---

### 📈 Confidence Score Visualization

**Image A**: {self._create_progress_bar(data_a['confidence'])} {data_a['confidence']}%  
**Image B**: {self._create_progress_bar(data_b['confidence'])} {data_b['confidence']}%

---

### 🔍 Key Differences

{self._highlight_differences(data_a, data_b)}

---

### 💊 Recommendations

**Image A**: {data_a['recommendation']}

**Image B**: {data_b['recommendation']}

---

### ⚠️ Clinical Notes

{self._generate_clinical_notes(data_a, data_b)}
"""
        return comparison
    
    def _create_progress_bar(self, percentage: int, length: int = 10) -> str:
        """Create ASCII progress bar"""
        filled = int((percentage / 100) * length)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    def _highlight_differences(self, data_a: Dict, data_b: Dict) -> str:
        """Highlight key differences between lesions"""
        differences = []
        
        # Compare diagnoses
        if data_a['primary_diagnosis'] != data_b['primary_diagnosis']:
            differences.append(f"**Diagnosis**: Different conditions detected (A: {data_a['primary_diagnosis']}, B: {data_b['primary_diagnosis']})")
        else:
            differences.append(f"**Diagnosis**: Both identified as {data_a['primary_diagnosis']}")
        
        # Compare confidence
        conf_diff = abs(data_a['confidence'] - data_b['confidence'])
        if conf_diff > 20:
            higher = "A" if data_a['confidence'] > data_b['confidence'] else "B"
            differences.append(f"**Confidence**: ⚠️ Significant difference ({conf_diff}% gap). Image {higher} has higher diagnostic confidence.")
        elif conf_diff > 10:
            differences.append(f"**Confidence**: Notable difference ({conf_diff}% gap)")
        else:
            differences.append(f"**Confidence**: Similar confidence levels (within {conf_diff}%)")
        
        # Compare risk levels
        if data_a['risk_level'] != data_b['risk_level']:
            if data_a['risk_level'] == "HIGH" or data_b['risk_level'] == "HIGH":
                high_image = "A" if data_a['risk_level'] == "HIGH" else "B"
                differences.append(f"**Risk**: 🔴 **CRITICAL** - Image {high_image} shows HIGH risk features requiring urgent attention!")
            else:
                differences.append(f"**Risk**: Different risk levels (A: {data_a['risk_level']}, B: {data_b['risk_level']})")
        else:
            differences.append(f"**Risk**: Both lesions show {data_a['risk_level']} risk level")
        
        # Compare features
        features_a_only = set(data_a['features']) - set(data_b['features'])
        features_b_only = set(data_b['features']) - set(data_a['features'])
        
        if features_a_only:
            differences.append(f"**Features**: Image A shows additional features: {', '.join(features_a_only)}")
        if features_b_only:
            differences.append(f"**Features**: Image B shows additional features: {', '.join(features_b_only)}")
        
        return "\n".join(f"- {diff}" for diff in differences)
    
    def _generate_clinical_notes(self, data_a: Dict, data_b: Dict) -> str:
        """Generate clinical insights"""
        notes = []
        
        # Priority assessment
        if data_a['risk_level'] == "HIGH" or data_b['risk_level'] == "HIGH":
            high_image = "A" if data_a['risk_level'] == "HIGH" else "B"
            notes.append(f"⚠️ **URGENT**: Image {high_image} requires immediate dermatologist evaluation.")
        
        # Monitoring recommendation
        if data_a['risk_level'] == "LOW" and data_b['risk_level'] == "LOW":
            notes.append("✅ Both lesions appear to be low-risk, but routine monitoring is recommended.")
        
        # Progression note (if both same condition)
        if data_a['primary_diagnosis'] == data_b['primary_diagnosis']:
            notes.append(f"📋 Both images suggest {data_a['primary_diagnosis']}. If these are the same lesion over time, compare for changes in size, color, or borders.")
        
        # General disclaimer
        notes.append("ℹ️ This AI comparison is for informational purposes only. Always consult a healthcare professional for medical advice.")
        
        return "\n\n".join(notes)
    
    def create_individual_analysis(self, image_label: str, data: Dict) -> str:
        """Format individual lesion analysis"""
        risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "UNKNOWN": "⚪"}
        
        analysis = f"""
### 📋 Image {image_label} Analysis

**Diagnosis**: {data['primary_diagnosis']}  
**Confidence**: {self._create_progress_bar(data['confidence'])} {data['confidence']}%  
**Risk Level**: {risk_emoji.get(data['risk_level'], '⚪')} {data['risk_level']}

**Features Detected**: {', '.join(data['features']) if data['features'] else 'None specified'}

**Recommendation**: {data['recommendation']}
"""
        return analysis


# Convenience function
def create_comparator():
    """Factory function to create comparator instance"""
    return LesionComparator()
