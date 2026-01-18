"""
Sherlock Engine - Project Sherlock Core Module
Pattern detection and historical analysis for medical symptoms
v1.1: Kaggle environment compatibility improvements
"""
from typing import Dict, List, Optional, Tuple
import json
import os
from datetime import datetime
from collections import Counter
import google.generativeai as genai

# Import API key rotator
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_key_manager import get_api_key, get_rotator


class SherlockEngine:
    """
    Historical pattern detection engine for medical symptoms
    
    Analyzes patient history to detect:
    - Symptom recurrence patterns
    - Temporal correlations
    - Environmental triggers
    - Treatment effectiveness
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize Sherlock Engine
        
        Args:
            data_dir: Directory containing patient history JSON files
                     If None, auto-detects based on current file location
        """
        # Auto-detect data directory if not provided
        if data_dir is None:
            # Try multiple possible locations
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            possible_paths = [
                os.path.join(base_dir, "data"),  # Standard location
                "data",  # Relative to working directory
                "/kaggle/working/dermacheck-ai/data",  # Kaggle specific
            ]
            
            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    data_dir = path
                    break
            
            if data_dir is None:
                data_dir = "data"  # Fall back to relative
        
        self.data_dir = data_dir
        self.api_rotator = get_rotator()
        
        # Configure Gemini for pattern analysis
        self.generation_config = {
            "temperature": 0.4,  # Slightly higher for creative pattern recognition
            "top_p": 0.9,
            "top_k": 50,
            "max_output_tokens": 2048,
        }
        
        print(f"🔍 Sherlock Engine initialized. Data dir: {data_dir}")
    
    def load_patient_history(self, patient_id: str) -> Optional[Dict]:
        """
        Load patient history from JSON file
        
        Args:
            patient_id: Patient ID (e.g., "DEMO_001")
            
        Returns:
            Dict with patient history or None if not found
        """
        # Map patient ID to filename
        filename_map = {
            "DEMO_001": "patient_001_allergic_rhinitis.json",
            "DEMO_002": "patient_002_migraine.json",
            "DEMO_003": "patient_003_eczema.json"
        }
        
        filename = filename_map.get(patient_id)
        if not filename:
            print(f"❌ Unknown patient ID: {patient_id}")
            return None
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded {len(data.get('entries', []))} history entries for {patient_id}")
                return data
        except FileNotFoundError:
            print(f"❌ History file not found: {filepath}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {filepath}: {e}")
            return None
    
    def detect_symptom_recurrence(self, entries: List[Dict]) -> Dict:
        """
        Detect which symptoms recur frequently
        
        Args:
            entries: List of patient history entries
            
        Returns:
            Dict with recurrent symptoms and their frequencies
        """
        symptom_counter = Counter()
        
        for entry in entries:
            symptoms = entry.get('symptoms', [])
            for symptom in symptoms:
                symptom_counter[symptom] += 1
        
        # Consider symptoms recurring if they appear 3+ times
        recurrent = {
            symptom: count 
            for symptom, count in symptom_counter.items() 
            if count >= 3
        }
        
        return {
            "recurrent_symptoms": recurrent,
            "total_unique_symptoms": len(symptom_counter),
            "most_common": symptom_counter.most_common(5)
        }
    
    def detect_temporal_patterns(self, entries: List[Dict]) -> Dict:
        """
        Detect temporal patterns (time-based correlations)
        
        Args:
            entries: List of patient history entries
            
        Returns:
            Dict with temporal patterns
        """
        # Extract timestamps
        timestamps = []
        for entry in entries:
            ts_str = entry.get('timestamp', '')
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    timestamps.append(ts)
                except:
                    pass
        
        if len(timestamps) < 2:
            return {"pattern": "insufficient_data"}
        
        # Calculate time intervals
        intervals = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i-1]).days
            intervals.append(delta)
        
        avg_interval = sum(intervals) / len(intervals) if intervals else 0
        
        # Check for seasonal pattern (60-120 day intervals)
        seasonal = any(45 < interval < 135 for interval in intervals)
        
        return {
            "total_episodes": len(timestamps),
            "average_interval_days": round(avg_interval, 1),
            "shortest_interval_days": min(intervals) if intervals else 0,
            "longest_interval_days": max(intervals) if intervals else 0,
            "suggests_seasonal": seasonal
        }
    
    def analyze_context_correlations(self, entries: List[Dict]) -> Dict:
        """
        Analyze correlations between symptoms and context factors
        
        Args:
            entries: List of patient history entries
            
        Returns:
            Dict with context correlations
        """
        correlations = {}
        
        # Extract context factors from entries with symptoms
        for entry in entries:
            severity = entry.get('severity', 'unknown')
            context = entry.get('context', {})
            
            # Skip entries with no/mild symptoms
            if severity in ['none', 'mild']:
                continue
            
            # Track context factors
            for key, value in context.items():
                if key not in correlations:
                    correlations[key] = []
                correlations[key].append(str(value))
        
        # Find most common context values
        common_contexts = {}
        for key, values in correlations.items():
            if values:
                most_common = Counter(values).most_common(1)[0]
                common_contexts[key] = {
                    "most_frequent_value": most_common[0],
                    "frequency": most_common[1],
                    "total_observations": len(values)
                }
        
        return common_contexts
    
    def generate_insight_prompt(self, patient_data: Dict, current_symptoms: str) -> str:
        """
        Generate prompt for Gemini to analyze patterns
        
        Args:
            patient_data: Full patient history
            current_symptoms: Current symptoms being reported
            
        Returns:
            Formatted prompt string
        """
        entries = patient_data.get('entries', [])
        scenario = patient_data.get('scenario_name', 'Unknown')
        
        # Get pattern analysis
        recurrence = self.detect_symptom_recurrence(entries)
        temporal = self.detect_temporal_patterns(entries)
        contexts = self.analyze_context_correlations(entries)
        
        # Build compact history summary
        history_summary = []
        for i, entry in enumerate(entries[-5:], 1):  # Last 5 entries
            symptoms = ", ".join(entry.get('symptoms', []))
            severity = entry.get('severity', 'unknown')
            date = entry.get('timestamp', '')[:10]
            history_summary.append(f"{i}. {date}: {symptoms} ({severity})")
        
        prompt = f"""Kamu adalah AI Medical Detective. Tugas mu: Temukan POLA dari riwayat medis pasien, BUKAN diagnosis.

**KELUHAN SAAT INI:**
{current_symptoms}

**RIWAYAT MEDIS (5 Terakhir):**
{chr(10).join(history_summary)}

**ANALISIS OTOMATIS:**
- Gejala berulang: {', '.join(recurrence.get('recurrent_symptoms', {}).keys()) if recurrence.get('recurrent_symptoms') else 'Tidak ada'}
- Total episode: {temporal.get('total_episodes', 0)}
- Interval rata-rata: {temporal.get('average_interval_days', 0)} hari
- Pola musiman: {'Ya' if temporal.get('suggests_seasonal', False) else 'Tidak'}

**KONTEKS SAAT FLARE-UP:**
{json.dumps(contexts, indent=2) if contexts else 'Tidak ada data konteks'}

**INSTRUKSI PENTING:**
1. Cari KORELASI (correlation), BUKAN KAUSALITAS (causation)
2. Format output:
   - **Pola Terdeteksi**: [Deskripsi pola yang kamu temukan]
   - **Trigger Potensial**: [Faktor yang sering muncul bersamaan dengan gejala]
   - **Frekuensi**: [Seberapa sering pola ini terjadi]
   - **Rekomendasi**: [Saran pencegahan atau manajemen]

3. WAJIB tambahkan disclaimer:
   "⚠️ Ini adalah korelasi statistik, bukan diagnosis medis. Konsultasikan dengan dokter untuk konfirmasi."

4. Jangan membuat diagnosis definitif
5. Fokus pada pola yang bisa dihindari pasien

Berikan insight sekarang:"""
        
        return prompt
    
    def analyze_with_gemini(self, prompt: str) -> str:
        """
        Get insights from Gemini using pattern detection prompt
        
        Args:
            prompt: Formatted prompt with patient history
            
        Returns:
            Gemini's pattern analysis
        """
        try:
            # Get API key from rotator
            api_key = get_api_key()
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Mark success
            self.api_rotator.mark_success(api_key)
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for rate limit
            if '429' in error_msg or 'quota' in error_msg.lower():
                self.api_rotator.mark_failure(api_key, error_code=429)
                return "⚠️ API rate limit. Sistem akan retry dengan key lain otomatis."
            else:
                self.api_rotator.mark_failure(api_key)
                return f"❌ Error: {error_msg}"
    
    def generate_sherlock_insight(
        self, 
        patient_id: str, 
        current_symptoms: str
    ) -> Dict:
        """
        Main method: Generate Sherlock insight for current symptoms
        
        Args:
            patient_id: Patient ID (DEMO_001, DEMO_002, or DEMO_003)
            current_symptoms: Current symptoms being reported
            
        Returns:
            Dict with pattern insights and metadata
        """
        # Load patient history
        patient_data = self.load_patient_history(patient_id)
        if not patient_data:
            return {
                "status": "error",
                "message": "Patient history not found"
            }
        
        # Generate prompt
        prompt = self.generate_insight_prompt(patient_data, current_symptoms)
        
        # Get Gemini analysis
        print("🔍 Analyzing patterns with Gemini...")
        insight = self.analyze_with_gemini(prompt)
        
        # Get basic pattern stats
        entries = patient_data.get('entries', [])
        recurrence = self.detect_symptom_recurrence(entries)
        temporal = self.detect_temporal_patterns(entries)
        
        return {
            "status": "success",
            "patient_id": patient_id,
            "scenario": patient_data.get('scenario_name', 'Unknown'),
            "insight": insight,
            "pattern_stats": {
                "recurrent_symptoms": list(recurrence.get('recurrent_symptoms', {}).keys()),
                "total_episodes": temporal.get('total_episodes', 0),
                "avg_interval_days": temporal.get('average_interval_days', 0)
            },
            "demo_mode": True,
            "timestamp": datetime.now().isoformat()
        }


# Testing
if __name__ == "__main__":
    print("🧪 Testing Sherlock Engine...\n")
    
    engine = SherlockEngine()
    
    # Test with Patient 001 (Allergic Rhinitis)
    print("\n" + "="*60)
    print("Test 1: Allergic Rhinitis Patient")
    print("="*60)
    
    result = engine.generate_sherlock_insight(
        patient_id="DEMO_001",
        current_symptoms="hidung meler, bersin-bersin, mata gatal"
    )
    
    if result['status'] == 'success':
        print(f"\n📊 Scenario: {result['scenario']}")
        print(f"\n💡 SHERLOCK INSIGHT:")
        print(result['insight'])
        print(f"\n📈 Pattern Stats:")
        print(f"  - Recurrent: {', '.join(result['pattern_stats']['recurrent_symptoms'])}")
        print(f"  - Episodes: {result['pattern_stats']['total_episodes']}")
        print(f"  - Avg Interval: {result['pattern_stats']['avg_interval_days']} days")
    else:
        print(f"❌ Error: {result.get('message')}")
    
    # Print API rotation stats
    print("\n" + "="*60)
    engine.api_rotator.print_stats()
