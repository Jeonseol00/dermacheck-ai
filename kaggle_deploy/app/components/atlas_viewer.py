"""
Interactive Derma Atlas Component
Displays curated dermatology cases in browsable gallery
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class DermaAtlas:
    """Interactive atlas for browsing curated dermatology cases"""
    
    def __init__(self, cases_json="data/cases_database.json"):
        self.cases_path = Path(cases_json)
        self.cases = self.load_cases()
        
        # Available conditions (extracted from data)
        self.conditions = self._get_unique_conditions()
    
    def load_cases(self) -> List[Dict]:
        """Load all cases from JSON database"""
        try:
            with open(self.cases_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Cases database not found: {self.cases_path}")
            return []
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing cases JSON: {e}")
            return []
    
    def _get_unique_conditions(self) -> List[str]:
        """Extract unique conditions from cases"""
        if not self.cases:
            return ["All"]
        
        conditions = set(case.get('condition', 'unknown') for case in self.cases)
        # Convert to readable format and sort
        readable = [c.replace('_', ' ').title() for c in sorted(conditions)]
        return ["All"] + readable
    
    def get_gallery_items(self, condition: str = "All") -> List[Tuple[str, str]]:
        """
        Get filtered cases for gallery display
        
        Args:
            condition: Filter by condition name (or "All")
            
        Returns:
            List of (image_path, label) tuples for Gradio Gallery
        """
        # Filter cases
        if condition == "All":
            filtered = self.cases
        else:
            # Convert back to snake_case for matching
            condition_key = condition.lower().replace(" ", "_")
            filtered = [c for c in self.cases if c.get('condition') == condition_key]
        
        # Build gallery items
        gallery = []
        for case in filtered:
            # Construct full image path
            img_path = f"data/{case.get('image_path', '')}"
            
            # Create readable label
            cond = case.get('condition', 'unknown').replace('_', ' ').title()
            case_id = case.get('case_id', '???')
            label = f"{cond} - Case {case_id}"
            
            gallery.append((img_path, label))
        
        return gallery
    
    def get_case_by_index(self, index: int) -> Optional[Dict]:
        """Get case by gallery index"""
        if 0 <= index < len(self.cases):
            return self.cases[index]
        return None
    
    def get_case_details(self, case: Dict) -> str:
        """
        Format case details as markdown
        
        Args:
            case: Case dictionary
            
        Returns:
            Formatted markdown string
        """
        if not case:
            return "### No case selected"
        
        condition = case.get('condition', 'unknown').replace('_', ' ').title()
        case_id = case.get('case_id', '???')
        source = case.get('source', 'Unknown')
        image_path = case.get('image_path', 'N/A')
        
        return f"""
### 📋 Case Details: {condition}

**Case ID**: `{case_id}`  
**Diagnosis**: **{condition}**  
**Source Dataset**: {source}  
**Image Path**: `{image_path}`

---

### 🔬 About This Condition

{self._get_condition_info(case.get('condition', ''))}

---

**💡 Tip**: Click "Analyze with AI" to see MedGemma's assessment of this case.
"""
    
    def _get_condition_info(self, condition: str) -> str:
        """Get brief info about condition"""
        info_map = {
            'melanoma': 'Melanoma is the most serious type of skin cancer. Early detection is critical for successful treatment.',
            'basal_cell_carcinoma': 'Basal cell carcinoma (BCC) is the most common form of skin cancer. It rarely spreads but should be treated.',
            'actinic_keratosis': 'Actinic keratosis is a precancerous skin lesion caused by sun exposure. Can develop into skin cancer if left untreated.',
            'nevus': 'A nevus (mole) is a benign growth of melanocytes. Most are harmless, but changes should be monitored.',
            'seborrheic_keratosis': 'Seborrheic keratosis is a common benign skin growth. Appears as brown, black, or tan growths.',
            'dermatofibroma': 'Dermatofibroma is a benign skin lesion, often appearing as a firm, reddish-brown nodule.',
            'vascular_lesion': 'Vascular lesions are abnormalities of blood vessels in the skin. Most are benign.'
        }
        
        return info_map.get(condition, 'No additional information available.')
    
    def get_statistics(self) -> str:
        """Get atlas statistics"""
        total = len(self.cases)
        conditions_count = {}
        
        for case in self.cases:
            cond = case.get('condition', 'unknown')
            conditions_count[cond] = conditions_count.get(cond, 0) + 1
        
        stats = f"### 📊 Atlas Statistics\n\n**Total Cases**: {total}\n\n**By Condition**:\n"
        for cond, count in sorted(conditions_count.items()):
            readable = cond.replace('_', ' ').title()
            stats += f"- {readable}: {count} cases\n"
        
        return stats


# Convenience function for Gradio integration
def create_atlas(cases_json="data/cases_database.json"):
    """Factory function to create atlas instance"""
    return DermaAtlas(cases_json)
