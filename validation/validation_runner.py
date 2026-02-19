"""
DermaCheck AI - Automated Validation Runner
Phase 3: Performance Testing & Metrics

This script runs all validation test cases against the deployed API
and calculates comprehensive performance metrics.

Success Criteria:
✅ Top-1 Accuracy: > 85%
✅ Top-3 Accuracy: > 95%
✅ Melanoma Sensitivity: > 95% (CRITICAL!)
✅ Fitzpatrick Equity: < 5% disparity
✅ Emergency Detection: 100%
✅ Appropriate Urgency: > 90%
"""

import requests
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import asdict
import time
from datetime import datetime

from test_cases import (
    VALIDATION_TEST_CASES,
    TestCase,
    DifficultyLevel,
    UrgencyLevel,
    PromptType,
    get_test_case_stats
)


class ValidationRunner:
    """Automated validation test runner"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.results = []
        self.metrics = {}
        
    def run_single_case(self, test_case: TestCase) -> Dict:
        """Run a single test case against API"""
        
        print(f"\n{'='*70}")
        print(f"Testing Case: {test_case.case_id}")
        print(f"Condition: {test_case.condition}")
        print(f"Difficulty: {test_case.difficulty.value}")
        print(f"Fitzpatrick: {test_case.fitzpatrick_type}")
        print(f"{'='*70}")
        
        # Prepare image
        if not test_case.image_path or not Path(test_case.image_path).exists():
            print(f"⚠️  Warning: Image not found: {test_case.image_path}")
            print(f"   Skipping this case (needs real image)")
            return {
                'case_id': test_case.case_id,
                'status': 'skipped',
                'reason': 'image_not_found'
            }
        
        # Prepare request data
        files = {'file': open(test_case.image_path, 'rb')}
        data = {
            'age': test_case.age,
            'sex': test_case.sex,
            'fitzpatrick_type': test_case.fitzpatrick_type,
            'body_location': test_case.location,
            'duration': test_case.duration,
            'chief_complaint': test_case.chief_complaint,
            'symptoms': test_case.symptoms,
            'itch_score': test_case.itch_score,
            'pain_present': test_case.pain_present,
            'warmth_present': test_case.warmth_present,
            'fever': test_case.fever,
            'rapidly_progressive': test_case.rapidly_progressive,
            'recent_medications': test_case.recent_medications,
            'known_allergies': test_case.known_allergies,
            'medical_history': test_case.medical_history,
            'family_history': test_case.family_history,
            'recent_travel': test_case.recent_travel
        }
        
        # Call API
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/analyze",
                files=files,
                data=data,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                return {
                    'case_id': test_case.case_id,
                    'status': 'error',
                    'error': f"HTTP {response.status_code}"
                }
            
            result = response.json()
            
            # Extract diagnosis
            diagnosis_text = result.get('diagnosis', '')
            metadata = result.get('metadata', {})
            
            print(f"\n🔍 AI Response:")
            print(f"   Prompt used: {metadata.get('prompt_used', 'unknown')}")
            print(f"   Response time: {response_time:.2f}s")
            print(f"   Diagnosis (first 200 chars): {diagnosis_text[:200]}...")
            
            # Evaluate result
            evaluation = self.evaluate_result(test_case, diagnosis_text, metadata)
            
            return {
                'case_id': test_case.case_id,
                'status': 'completed',
                'test_case': test_case,
                'ai_response': diagnosis_text,
                'metadata': metadata,
                'response_time': response_time,
                'evaluation': evaluation
            }
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return {
                'case_id': test_case.case_id,
                'status': 'error',
                'error': str(e)
            }
    
    def evaluate_result(self, test_case: TestCase, diagnosis_text: str, metadata: Dict) -> Dict:
        """Evaluate AI output against expected results"""
        
        diagnosis_lower = diagnosis_text.lower()
        evaluation = {}
        
        # 1. Primary diagnosis correct?
        expected_primary = test_case.expected_diagnosis.lower()
        primary_correct = expected_primary in diagnosis_lower
        evaluation['primary_diagnosis_correct'] = primary_correct
        
        if primary_correct:
            print(f"   ✅ Primary diagnosis CORRECT: {test_case.expected_diagnosis}")
        else:
            print(f"   ❌ Primary diagnosis WRONG (expected: {test_case.expected_diagnosis})")
        
        # 2. In differential (top 3)?
        in_differential = primary_correct  # If primary correct, it's in differential
        if not in_differential:
            # Check if it's mentioned elsewhere in text
            in_differential = expected_primary in diagnosis_lower
        evaluation['in_differential'] = in_differential
        
        # 3. Prompt selection correct?
        prompt_used = metadata.get('prompt_used', '')
        prompt_correct = (prompt_used == test_case.expected_prompt_type.value)
        evaluation['prompt_selection_correct'] = prompt_correct
        
        if prompt_correct:
            print(f"   ✅ Prompt selection CORRECT: {prompt_used}")
        else:
            print(f"   ⚠️  Prompt selection: {prompt_used} (expected: {test_case.expected_prompt_type.value})")
        
        # 4. Urgency appropriate?
        # Parse urgency from text (look for keywords)
        urgency_detected = self.detect_urgency(diagnosis_text)
        urgency_appropriate = (urgency_detected == test_case.expected_urgency.value)
        evaluation['urgency_appropriate'] = urgency_appropriate
        
        if urgency_appropriate:
            print(f"   ✅ Urgency CORRECT: {urgency_detected}")
        else:
            print(f"   ⚠️  Urgency: {urgency_detected} (expected: {test_case.expected_urgency.value})")
        
        # 5. Melanoma detection (if applicable)
        if test_case.is_melanoma:
            melanoma_detected = 'melanoma' in diagnosis_lower
            evaluation['melanoma_detected'] = melanoma_detected
            
            if melanoma_detected:
                print(f"   ✅ MELANOMA DETECTED (CRITICAL!)")
            else:
                print(f"   🚨 MELANOMA MISSED (FALSE NEGATIVE!)")
        
        # 6. Emergency detection (if applicable)
        if test_case.is_emergency:
            emergency_keywords = ['emergency', 'urgent', 'immediate', '911', 'hospital']
            emergency_detected = any(kw in diagnosis_lower for kw in emergency_keywords)
            evaluation['emergency_detected'] = emergency_detected
            
            if emergency_detected:
                print(f"   ✅ EMERGENCY DETECTED")
            else:
                print(f"   🚨 EMERGENCY MISSED!")
        
        # 7. Must-not-miss conditions
        if test_case.must_not_miss:
            missed_critical = []
            for critical_condition in test_case.must_not_miss:
                if critical_condition.lower() not in diagnosis_lower:
                    missed_critical.append(critical_condition)
            
            evaluation['missed_critical_conditions'] = missed_critical
            
            if missed_critical:
                print(f"   🚨 CRITICAL CONDITIONS MISSED: {missed_critical}")
        
        # 8. Fitzpatrick adjustments (if SOC case)
        if test_case.fitzpatrick_type >= 4:
            fitz_adjusted = metadata.get('fitzpatrick_adjusted', False)
            evaluation['fitzpatrick_adjusted'] = fitz_adjusted
            
            if fitz_adjusted:
                print(f"   ✅ Fitzpatrick adjustments applied")
        
        return evaluation
    
    def detect_urgency(self, text: str) -> str:
        """Detect urgency level from diagnosis text"""
        text_lower = text.lower()
        
        # Emergency keywords
        if any(kw in text_lower for kw in ['emergency', '911', 'immediate', 'icu', 'call emergency']):
            return 'emergency'
        
        # Urgent keywords
        if any(kw in text_lower for kw in ['urgent', 'within 1-2 weeks', 'prompt', 'soon']):
            return 'urgent'
        
        # Default routine
        return 'routine'
    
    def run_all_cases(self) -> List[Dict]:
        """Run all test cases"""
        print("\n" + "="*70)
        print("DERMACHECK AI VALIDATION - STARTING")
        print("="*70)
        print(f"API URL: {self.api_url}")
        print(f"Total test cases: {len(VALIDATION_TEST_CASES)}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        self.results = []
        
        for i, test_case in enumerate(VALIDATION_TEST_CASES, 1):
            print(f"\n\n{'#'*70}")
            print(f"Test Case {i}/{len(VALIDATION_TEST_CASES)}")
            print(f"{'#'*70}")
            
            result = self.run_single_case(test_case)
            self.results.append(result)
            
            # Small delay between requests
            time.sleep(1)
        
        return self.results
    
    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        # Filter completed results
        completed = [r for r in self.results if r['status'] == 'completed']
        total_completed = len(completed)
        
        if total_completed == 0:
            return {'error': 'No completed test cases'}
        
        metrics = {}
        
        # 1. Overall Accuracy
        primary_correct = sum(1 for r in completed if r['evaluation']['primary_diagnosis_correct'])
        top1_accuracy = primary_correct / total_completed
        
        in_diff_correct = sum(1 for r in completed if r['evaluation']['in_differential'])
        top3_accuracy = in_diff_correct / total_completed
        
        metrics['overall'] = {
            'total_cases': total_completed,
            'top1_accuracy': top1_accuracy,
            'top3_accuracy': top3_accuracy,
            'top1_percentage': f"{top1_accuracy*100:.1f}%",
            'top3_percentage': f"{top3_accuracy*100:.1f}%"
        }
        
        # 2. Melanoma Sensitivity (CRITICAL!)
        melanoma_cases = [r for r in completed if r['test_case'].is_melanoma]
        if melanoma_cases:
            melanoma_detected = sum(1 for r in melanoma_cases if r['evaluation'].get('melanoma_detected', False))
            melanoma_sensitivity = melanoma_detected / len(melanoma_cases)
            
            metrics['melanoma'] = {
                'total_cases': len(melanoma_cases),
                'detected': melanoma_detected,
                'sensitivity': melanoma_sensitivity,
                'sensitivity_percentage': f"{melanoma_sensitivity*100:.1f}%",
                'pass': melanoma_sensitivity >= 0.95
            }
        
        # 3. Emergency Detection
        emergency_cases = [r for r in completed if r['test_case'].is_emergency]
        if emergency_cases:
            emergency_detected = sum(1 for r in emergency_cases if r['evaluation'].get('emergency_detected', False))
            emergency_detection_rate = emergency_detected / len(emergency_cases)
            
            metrics['emergency'] = {
                'total_cases': len(emergency_cases),
                'detected': emergency_detected,
                'detection_rate': emergency_detection_rate,
                'detection_percentage': f"{emergency_detection_rate*100:.1f}%",
                'pass': emergency_detection_rate == 1.0
            }
        
        # 4. Fitzpatrick Equity
        fitz_performance = {}
        for fitz_type in range(1, 7):
            fitz_cases = [r for r in completed if r['test_case'].fitzpatrick_type == fitz_type]
            if fitz_cases:
                fitz_correct = sum(1 for r in fitz_cases if r['evaluation']['primary_diagnosis_correct'])
                fitz_accuracy = fitz_correct / len(fitz_cases)
                fitz_performance[fitz_type] = {
                    'cases': len(fitz_cases),
                    'accuracy': fitz_accuracy,
                    'percentage': f"{fitz_accuracy*100:.1f}%"
                }
        
        if fitz_performance:
            accuracies = [v['accuracy'] for v in fitz_performance.values()]
            disparity = max(accuracies) - min(accuracies)
            
            metrics['fitzpatrick_equity'] = {
                'by_type': fitz_performance,
                'disparity': disparity,
                'disparity_percentage': f"{disparity*100:.1f}%",
                'pass': disparity < 0.05
            }
        
        # 5. Prompt Selection Accuracy
        prompt_correct = sum(1 for r in completed if r['evaluation']['prompt_selection_correct'])
        prompt_accuracy = prompt_correct / total_completed
        
        metrics['prompt_selection'] = {
            'correct': prompt_correct,
            'total': total_completed,
            'accuracy': prompt_accuracy,
            'percentage': f"{prompt_accuracy*100:.1f}%"
        }
        
        # 6. Urgency Appropriateness
        urgency_correct = sum(1 for r in completed if r['evaluation']['urgency_appropriate'])
        urgency_accuracy = urgency_correct / total_completed
        
        metrics['urgency_triage'] = {
            'correct': urgency_correct,
            'total': total_completed,
            'accuracy': urgency_accuracy,
            'percentage': f"{urgency_accuracy*100:.1f}%",
            'pass': urgency_accuracy >= 0.90
        }
        
        # 7. Average Response Time
        response_times = [r['response_time'] for r in completed]
        avg_response_time = sum(response_times) / len(response_times)
        
        metrics['performance'] = {
            'avg_response_time': avg_response_time,
            'avg_response_time_formatted': f"{avg_response_time:.2f}s"
        }
        
        self.metrics = metrics
        return metrics
    
    def print_report(self):
        """Print comprehensive validation report"""
        
        if not self.metrics:
            self.calculate_metrics()
        
        print("\n\n" + "="*70)
        print("DERMACHECK AI - VALIDATION REPORT")
        print("="*70)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"API URL: {self.api_url}")
        
        # Overall Accuracy
        print(f"\n{'='*70}")
        print("OVERALL ACCURACY")
        print(f"{'='*70}")
        overall = self.metrics['overall']
        print(f"Total Cases: {overall['total_cases']}")
        print(f"Top-1 Accuracy: {overall['top1_percentage']} {'✅ PASS' if overall['top1_accuracy'] >= 0.85 else '❌ FAIL (target: >85%)'}")
        print(f"Top-3 Accuracy: {overall['top3_percentage']} {'✅ PASS' if overall['top3_accuracy'] >= 0.95 else '❌ FAIL (target: >95%)'}")
        
        # Melanoma Sensitivity
        if 'melanoma' in self.metrics:
            print(f"\n{'='*70}")
            print("MELANOMA SENSITIVITY (CRITICAL!)")
            print(f"{'='*70}")
            mel = self.metrics['melanoma']
            print(f"Total Melanoma Cases: {mel['total_cases']}")
            print(f"Detected: {mel['detected']}")
            print(f"Sensitivity: {mel['sensitivity_percentage']} {'✅ PASS' if mel['pass'] else '🚨 FAIL (target: >95%)'}")
        
        # Emergency Detection
        if 'emergency' in self.metrics:
            print(f"\n{'='*70}")
            print("EMERGENCY DETECTION")
            print(f"{'='*70}")
            emerg = self.metrics['emergency']
            print(f"Total Emergency Cases: {emerg['total_cases']}")
            print(f"Detected: {emerg['detected']}")
            print(f"Detection Rate: {emerg['detection_percentage']} {'✅ PASS' if emerg['pass'] else '🚨 FAIL (target: 100%)'}")
        
        # Fitzpatrick Equity
        if 'fitzpatrick_equity' in self.metrics:
            print(f"\n{'='*70}")
            print("FITZPATRICK EQUITY")
            print(f"{'='*70}")
            fitz = self.metrics['fitzpatrick_equity']
            print(f"Performance by Fitzpatrick Type:")
            for fitz_type, data in fitz['by_type'].items():
                print(f"  Type {fitz_type}: {data['percentage']} ({data['cases']} cases)")
            print(f"\nDisparity: {fitz['disparity_percentage']} {'✅ PASS' if fitz['pass'] else '❌ FAIL (target: <5%)'}")
        
        # Prompt Selection
        print(f"\n{'='*70}")
        print("PROMPT SELECTION ACCURACY")
        print(f"{'='*70}")
        prompt = self.metrics['prompt_selection']
        print(f"Correct: {prompt['correct']}/{prompt['total']}")
        print(f"Accuracy: {prompt['percentage']}")
        
        # Urgency Triage
        print(f"\n{'='*70}")
        print("URGENCY TRIAGE")
        print(f"{'='*70}")
        urgency = self.metrics['urgency_triage']
        print(f"Appropriate: {urgency['correct']}/{urgency['total']}")
        print(f"Accuracy: {urgency['percentage']} {'✅ PASS' if urgency['pass'] else '❌ FAIL (target: >90%)'}")
        
        # Performance
        print(f"\n{'='*70}")
        print("PERFORMANCE")
        print(f"{'='*70}")
        perf = self.metrics['performance']
        print(f"Average Response Time: {perf['avg_response_time_formatted']}")
        
        # Overall Pass/Fail
        print(f"\n{'='*70}")
        print("OVERALL VALIDATION RESULT")
        print(f"{'='*70}")
        
        passes = []
        fails = []
        
        if overall['top1_accuracy'] >= 0.85:
            passes.append("Top-1 Accuracy")
        else:
            fails.append("Top-1 Accuracy")
        
        if overall['top3_accuracy'] >= 0.95:
            passes.append("Top-3 Accuracy")
        else:
            fails.append("Top-3 Accuracy")
        
        if 'melanoma' in self.metrics and self.metrics['melanoma']['pass']:
            passes.append("Melanoma Sensitivity")
        elif 'melanoma' in self.metrics:
            fails.append("Melanoma Sensitivity")
        
        if 'emergency' in self.metrics and self.metrics['emergency']['pass']:
            passes.append("Emergency Detection")
        elif 'emergency' in self.metrics:
            fails.append("Emergency Detection")
        
        if 'fitzpatrick_equity' in self.metrics and self.metrics['fitzpatrick_equity']['pass']:
            passes.append("Fitzpatrick Equity")
        elif 'fitzpatrick_equity' in self.metrics:
            fails.append("Fitzpatrick Equity")
        
        if urgency['pass']:
            passes.append("Urgency Triage")
        else:
            fails.append("Urgency Triage")
        
        print(f"\n✅ PASSING ({len(passes)}):")
        for p in passes:
            print(f"   - {p}")
        
        if fails:
            print(f"\n❌ FAILING ({len(fails)}):")
            for f in fails:
                print(f"   - {f}")
        
        all_pass = len(fails) == 0
        print(f"\n{'='*70}")
        if all_pass:
            print("🎉 VALIDATION PASSED - ALL TARGETS MET!")
        else:
            print("⚠️  VALIDATION INCOMPLETE - SOME TARGETS NOT MET")
            print("   Please iterate on prompts and re-test")
        print(f"{'='*70}\n")
    
    def save_report(self, filename: str = "validation_report.json"):
        """Save detailed report to JSON file"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'api_url': self.api_url,
            'metrics': self.metrics,
            'detailed_results': [
                {
                    'case_id': r['case_id'],
                    'status': r['status'],
                    'evaluation': r.get('evaluation', {})
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {filename}")


# ═══════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validation_runner.py <API_URL>")
        print("Example: python validation_runner.py https://xxxx.ngrok-free.app")
        sys.exit(1)
    
    api_url = sys.argv[1]
    
    # Run validation
    runner = ValidationRunner(api_url)
    runner.run_all_cases()
    runner.calculate_metrics()
    runner.print_report()
    runner.save_report()
    
    print("\n✅ Validation complete!")
