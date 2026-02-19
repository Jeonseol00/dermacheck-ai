"""
Backend Format Validation for DermaCheck v11.0 Hybrid Prompt
Add this to Cell 4 after AI generation, before returning response

Purpose: Auto-fix common PRIMARY DIAGNOSIS format issues
Reliability target: 99%+ format compliance
"""

import re
from typing import Tuple, List

def validate_primary_diagnosis(response: str) -> Tuple[bool, str, List[str]]:
    """
    Validate and auto-fix PRIMARY DIAGNOSIS line format.
    
    Args:
        response: Raw AI-generated response text
        
    Returns:
        (is_valid, fixed_response, warnings)
        - is_valid: True if format correct or successfully fixed
        - fixed_response: Response with fixes applied (or original if no fix needed)
        - warnings: List of issues found and fixes applied
    
    Examples:
        >>> validate_primary_diagnosis("PRIMARY DIAGNOSIS: Acne (Confidence: 85%)\n...")
        (True, "PRIMARY DIAGNOSIS: Acne (Confidence: 85%)\n...", [])
        
        >>> validate_primary_diagnosis("**PRIMARY DIAGNOSIS**: Acne (Confidence: 85%)\n...")
        (True, "PRIMARY DIAGNOSIS: Acne (Confidence: 85%)\n...", ["Fixed: Removed markdown"])
    """
    lines = response.strip().split('\n')
    if not lines:
        return False, response, ["❌ Empty response"]
    
    first_line = lines[0].strip()
    warnings = []
    
    # Perfect format pattern
    perfect_pattern = r'^PRIMARY DIAGNOSIS: ([A-Z][a-zA-Z\s\-\/]+) \(Confidence: (\d{1,3})%\)$'
    
    # Check if already perfect
    if re.match(perfect_pattern, first_line):
        return True, response, []
    
    # ═══════════════════════════════════════════
    # AUTO-FIX ATTEMPTS (in order of specificity)
    # ═══════════════════════════════════════════
    
    # Fix 1: Markdown formatting (**PRIMARY DIAGNOSIS**:)
    if first_line.startswith('**PRIMARY DIAGNOSIS**'):
        fixed = first_line.replace('**PRIMARY DIAGNOSIS**', 'PRIMARY DIAGNOSIS')
        fixed = fixed.replace('**', '')  # Remove any other ** markers
        lines[0] = fixed
        warnings.append("Fixed: Removed markdown formatting")
        first_line = fixed
    
    # Fix 2: Case sensitivity (primary diagnosis:, Primary Diagnosis:)
    case_pattern = r'^(primary diagnosis|Primary Diagnosis|PRIMARY diagnosis|Primary DIAGNOSIS):'
    match = re.match(case_pattern, first_line, re.IGNORECASE)
    if match:
        fixed = re.sub(case_pattern, 'PRIMARY DIAGNOSIS:', first_line, flags=re.IGNORECASE)
        lines[0] = fixed
        warnings.append("Fixed: Corrected capitalization")
        first_line = fixed
    
    # Fix 3: Extra text before condition name
    # Pattern: "PRIMARY DIAGNOSIS: [extra text] Condition Name (Confidence: XX%)"
    # Handles: "Based on features, Eczema" OR "This is Melanoma" formats
    extra_text_pattern = r'PRIMARY DIAGNOSIS:\s*(?:Based on[^,]+,\s*|This is|This appears to be|Diagnosis is|I believe this is|The diagnosis is|I diagnose this as)\s*([A-Z][a-zA-Z\s\-\/]+?)\s*\(Confidence:\s*(\d{1,3})%\)'
    match = re.search(extra_text_pattern, first_line, re.IGNORECASE)
    if match:
        fixed = f"PRIMARY DIAGNOSIS: {match.group(1).strip()} (Confidence: {match.group(2)}%)"
        lines[0] = fixed
        warnings.append("Fixed: Removed extra text before condition")
        first_line = fixed
    
    # Fix 4: Indonesian interference
    # Pattern: "PRIMARY DIAGNOSIS: Diagnosis Utama: Acne... " or "... (Keyakinan: XX%)"
    indonesian_patterns = [
        (r'PRIMARY DIAGNOSIS:\s*Diagnosis Utama:\s*([A-Z][a-zA-Z\s\-\/]+)\s*\((?:Confidence|Keyakinan):\s*(\d{1,3})%\)', 
         "Removed 'Diagnosis Utama' prefix"),
        (r'PRIMARY DIAGNOSIS:\s*([A-Z][a-zA-Z\s\-\/]+)\s*\(Keyakinan:\s*(\d{1,3})%\)',
         "Changed 'Keyakinan' to 'Confidence'"),
    ]
    
    for pattern, fix_desc in indonesian_patterns:
        match = re.search(pattern, first_line)
        if match:
            fixed = f"PRIMARY DIAGNOSIS: {match.group(1)} (Confidence: {match.group(2)}%)"
            lines[0] = fixed
            warnings.append(f"Fixed: {fix_desc}")
            first_line = fixed
            break
    
    # Fix 5: Extra fields on same line
    # Pattern: "PRIMARY DIAGNOSIS: Acne (Confidence: 85%, Risk: HIGH)"
    extra_fields_pattern = r'PRIMARY DIAGNOSIS:\s*([A-Z][a-zA-Z\s\-\/]+)\s*\(Confidence:\s*(\d{1,3})%[,;].*?\)'
    match = re.search(extra_fields_pattern, first_line)
    if match:
        fixed = f"PRIMARY DIAGNOSIS: {match.group(1)} (Confidence: {match.group(2)}%)"
        lines[0] = fixed
        warnings.append("Fixed: Removed extra fields (Risk, Grade, etc.) from diagnosis line")
        first_line = fixed
    
    # Fix 6: Extra whitespace
    whitespace_pattern = r'PRIMARY\s+DIAGNOSIS:\s+([A-Z][a-zA-Z\s\-\/]+?)\s+\(Confidence:\s+(\d{1,3})%\)'
    match = re.search(whitespace_pattern, first_line)
    if match:
        fixed = f"PRIMARY DIAGNOSIS: {match.group(1)} (Confidence: {match.group(2)}%)"
        lines[0] = fixed
        warnings.append("Fixed: Normalized whitespace")
        first_line = fixed
   
    # Fix 7: Missing space after colon
    no_space_pattern = r'PRIMARY DIAGNOSIS:([A-Z][a-zA-Z\s\-\/]+)\s*\(Confidence:\s*(\d{1,3})%\)'
    match = re.match(no_space_pattern, first_line)
    if match:
        fixed = f"PRIMARY DIAGNOSIS: {match.group(1)} (Confidence: {match.group(2)}%)"
        lines[0] = fixed
        warnings.append("Fixed: Added space after colon")
        first_line = fixed
    
    # ═══════════════════════════════════════════
    # FINAL VALIDATION
    # ═══════════════════════════════════════════
    
    fixed_response = '\n'.join(lines)
    
    # Check if fix was successful
    if re.match(perfect_pattern, lines[0].strip()):
        return True, fixed_response, warnings
    
    # Unable to auto-fix
    warnings.append(f"⚠️ UNABLE TO FIX - First line: {first_line[:100]}")
    warnings.append("Format should be: PRIMARY DIAGNOSIS: [Condition] (Confidence: XX%)")
    return False, response, warnings


def log_validation_result(is_valid: bool, warnings: List[str], response_preview: str):
    """Log validation results for monitoring"""
    if is_valid and not warnings:
        print("✅ Format validation: PASSED")
    elif is_valid and warnings:
        print(f"⚠️  Format validation: FIXED")
        for warning in warnings:
            print(f"   - {warning}")
    else:
        print(f"❌ Format validation: FAILED")
        for warning in warnings:
            print(f"   - {warning}")
        print(f"Response preview: {response_preview[:200]}...")


# ═══════════════════════════════════════════
# INTEGRATION INTO CELL 4
# ═══════════════════════════════════════════

"""
Add after generation (around line ~XXX where response is decoded):

# Generate response
with torch.inference_mode():
    generation = model.generate(**inputs, max_new_tokens=2048, do_sample=False)
    
response = processor.decode(generation[0][input_len:], skip_special_tokens=True)

# ✅ VALIDATE AND FIX FORMAT
is_valid, response, warnings = validate_primary_diagnosis(response)
log_validation_result(is_valid, warnings, response)

# Continue with post-processing, metadata extraction, etc.
"""


# ═══════════════════════════════════════════
# UNIT TESTS
# ═══════════════════════════════════════════

def test_validation():
    """Test validation with common edge cases"""
    
    test_cases = [
        # (input, should_be_valid, expected_warnings_count)
        ("PRIMARY DIAGNOSIS: Acne Vulgaris (Confidence: 85%)\n...", True, 0),
        ("**PRIMARY DIAGNOSIS**: Melanoma (Confidence: 90%)\n...", True, 1),
        ("PRIMARY DIAGNOSIS: Based on features, Eczema (Confidence: 75%)\n...", True, 1),
        ("primary diagnosis: Psoriasis (Confidence: 80%)\n...", True, 1),
        ("PRIMARY DIAGNOSIS: Diagnosis Utama: Dermatitis (Confidence: 70%)\n...", True, 1),
        ("PRIMARY DIAGNOSIS: Acne (Keyakinan: 88%)\n...", True, 1),
        ("PRIMARY DIAGNOSIS: Acne (Confidence: 85%, Risk: HIGH)\n...", True, 1),
        ("PRIMARY  DIAGNOSIS:  Rosacea  (Confidence:  65%)\n...", True, 1),
        ("PRIMARY DIAGNOSIS:Impetigo (Confidence: 92%)\n...", True, 1),
    ]
    
    print("Running validation tests...\n")
    passed = 0
    failed = 0
    
    for i, (test_input, expected_valid, expected_warnings) in enumerate(test_cases, 1):
        is_valid, fixed, warnings = validate_primary_diagnosis(test_input)
        
        test_passed = (is_valid == expected_valid)
        if test_passed:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"
        
        print(f"Test {i}: {status}")
        print(f"  Input:  {test_input.split(chr(10))[0][:60]}...")
        print(f"  Output: {fixed.split(chr(10))[0]}")
        print(f"  Valid: {is_valid} (expected {expected_valid})")
        print(f"  Warnings: {len(warnings)} (expected ~{expected_warnings})")
        if warnings:
            for w in warnings:
                print(f"    - {w}")
        print()
    
    print(f"Summary: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    # Run tests
    test_validation()
