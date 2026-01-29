#!/usr/bin/env python3
"""
Quick Test Script for MedGemma Setup
Tests if all dependencies and model loading work correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("=" * 60)
    print("🔍 Testing Package Imports...")
    print("=" * 60)
    
    packages = {
        'torch': 'torch',
        'transformers': 'transformers',
        'gradio': 'gradio',
        'bitsandbytes': 'bitsandbytes',
        'accelerate': 'accelerate',
        'PIL': 'Pillow'
    }
    
    failed = []
    for display_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✅ {display_name:20s} - OK")
        except ImportError as e:
            print(f"❌ {display_name:20s} - MISSING")
            failed.append(import_name)
    
    print()
    if failed:
        print(f"⚠️  Missing packages: {', '.join(failed)}")
        print(f"\nInstall with: pip install {' '.join(failed)}")
        return False
    else:
        print("✅ All packages installed!")
        return True


def test_cuda():
    """Test CUDA availability"""
    print("=" * 60)
    print("🔍 Testing CUDA/GPU...")
    print("=" * 60)
    
    import torch
    
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    
    if cuda_available:
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"GPU Count: {torch.cuda.device_count()}")
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        
        # Check memory
        total_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU Memory: {total_mem:.2f} GB")
        
        if total_mem < 10:
            print("⚠️  WARNING: Less than 10GB GPU memory. MedGemma 4B might struggle.")
            print("   Recommendation: Use Kaggle T4 (15GB) or Colab GPU")
        else:
            print("✅ GPU memory sufficient for MedGemma 4B!")
    else:
        print("❌ No CUDA GPU detected!")
        print("\nOptions:")
        print("1. Install CUDA toolkit locally")
        print("2. Use Kaggle notebook (recommended)")
        print("3. Use Google Colab")
        return False
    
    print()
    return True


def test_huggingface_auth():
    """Test HuggingFace authentication"""
    print("=" * 60)
    print("🔍 Testing HuggingFace Authentication...")
    print("=" * 60)
    
    hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
    
    if hf_token:
        print(f"✅ HF Token found: {hf_token[:10]}...{hf_token[-5:]}")
        print("\nNote: Make sure you've accepted the MedGemma license at:")
        print("https://huggingface.co/google/medgemma-4b-it")
    else:
        print("⚠️  No HF_TOKEN environment variable found")
        print("\nTo set it:")
        print("export HF_TOKEN='your_token_here'")
        print("\nGet token from: https://huggingface.co/settings/tokens")
    
    print()
    return True


def test_model_loading():
    """Test MedGemma model loading (dry run)"""
    print("=" * 60)
    print("🔍 Testing MedGemma Model Loading...")
    print("=" * 60)
    
    try:
        from models.medgemma_multimodal_client import MedGemmaMultimodalClient
        
        print("📦 Importing MedGemmaMultimodalClient...")
        print("✅ Import successful!")
        
        print("\n⚠️  NOTE: Actual model loading requires:")
        print("   1. HuggingFace token (HF_TOKEN)")
        print("   2. Accepted MedGemma license")
        print("   3. CUDA GPU with 10GB+ VRAM")
        print("   4. ~10-15 minutes for first download (~8GB)")
        
        print("\n💡 To test full loading, run:")
        print("   python models/medgemma_multimodal_client.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     DermaCheck AI - MedGemma Setup Test Suite            ║")
    print("║     MedGemma Impact Challenge 2026                        ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()
    
    results = []
    
    # Run tests
    results.append(("Package Imports", test_imports()))
    results.append(("CUDA/GPU", test_cuda()))
    results.append(("HuggingFace Auth", test_huggingface_auth()))
    results.append(("Model Import", test_model_loading()))
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25s} - {status}")
    
    print()
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Your environment is ready for MedGemma!")
        print("\nNext steps:")
        print("1. Set HF_TOKEN environment variable")
        print("2. Accept MedGemma license on HuggingFace")
        print("3. Run: python models/medgemma_multimodal_client.py")
        print("4. Run: python app/gradio_app.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Missing packages: pip install -r requirements_gradio.txt")
        print("- No GPU: Use Kaggle or Colab")
        print("- No HF token: export HF_TOKEN='your_token'")
    
    print("\n" + "=" * 60)
    print()


if __name__ == "__main__":
    main()
