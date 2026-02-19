"""
MedGemma Model Loader - INT8 SAFE MODE
BULLETPROOF version for Kaggle T4 GPU
NO 4-bit - HARDCODED INT8 for stability
"""

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)


class MedGemmaModelLoader:
    """
    MedGemma loader with HARDCODED INT8 quantization
    
    INT8 Benefits:
    - Memory: ~4-5GB (fits comfortably in T4's 16GB)
    - Stability: Much better than INT4 (no inf/nan issues)
    - Speed: Faster than FP16
    - Quality: Minimal accuracy loss vs FP16
    
    NO 4-BIT OPTION - removed for safety
    """
    
    def __init__(self, model_name: str = "google/medgemma-4b-it"):
        """
        Initialize loader with HARDCODED INT8
        
        Args:
            model_name: HuggingFace model ID
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        
        # Get HF token from environment
        self.hf_token = os.environ.get('HF_TOKEN')
        if not self.hf_token:
            raise ValueError("❌ HF_TOKEN not found in environment variables")
        
        logger.info(f"✅ MedGemmaModelLoader initialized")
        logger.info(f"📦 Model: {model_name}")
        logger.info(f"🔧 Mode: INT8 quantization (HARDCODED)")
    
    def load_model(self):
        """
        Load MedGemma with INT8 quantization (HARDCODED)
        
        This is SAFE MODE - no options, no flexibility, just works
        
        Expected:
        - Load time: 2-3 minutes
        - Memory: 4-5 GB
        - Stable inference (NO CUDA errors)
        
        Returns:
            Tuple of (model, processor)
        """
        print("="*70)
        print("🔄 LOADING MEDGEMMA - INT8 SAFE MODE")
        print("="*70)
        print(f"📦 Model: {self.model_name}")
        print(f"🔧 Quantization: INT8 (hardcoded for stability)")
        print(f"⏳ Expected time: 2-3 minutes")
        print(f"💾 Expected memory: 4-5 GB")
        print("")
        
        try:
            # STEP 1: Configure INT8 quantization (HARDCODED)
            print("🔧 Step 1/3: Configuring INT8 quantization...")
            
            # INT8 config - SAFE and STABLE
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,  # INT8 - HARDCODED
                llm_int8_threshold=6.0,  # Standard threshold
                llm_int8_has_fp16_weight=False  # Use INT8 weights
            )
            
            print("   ✅ INT8 config created")
            print(f"   📊 load_in_8bit: True")
            print(f"   📊 load_in_4bit: False (DISABLED)")
            print("")
            
            # STEP 2: Load processor
            print("🔧 Step 2/3: Loading processor...")
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=self.hf_token
            )
            
            print("   ✅ Processor loaded")
            print("")
            
            # STEP 3: Load model with INT8
            print("🔧 Step 3/3: Loading model weights (INT8)...")
            print("   ⏳ This will take 2-3 minutes (downloading + loading)...")
            print("")
            
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,  # INT8 config
                device_map="auto",  # Auto distribute to GPU
                trust_remote_code=True,
                token=self.hf_token
            )
            
            # Set to eval mode
            self.model.eval()
            
            # SUCCESS - Print status
            print("="*70)
            print("✅ MODEL LOADED SUCCESSFULLY!")
            print("="*70)
            
            # Device info
            device = str(self.model.device)
            print(f"📊 Device: {device}")
            print(f"💾 Dtype: {self.model.dtype}")
            print(f"🔧 Quantization: INT8 (8-bit)")
            print(f"🎯 Mode: Evaluation (inference ready)")
            print("")
            
            # Memory info
            if torch.cuda.is_available():
                allocated_gb = torch.cuda.memory_allocated() / 1e9
                reserved_gb = torch.cuda.memory_reserved() / 1e9
                total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
                free_gb = total_gb - reserved_gb
                
                print("💾 GPU Memory Status:")
                print(f"   Allocated: {allocated_gb:.2f} GB")
                print(f"   Reserved:  {reserved_gb:.2f} GB")
                print(f"   Total:     {total_gb:.2f} GB")
                print(f"   Free:      {free_gb:.2f} GB")
                
                # Validate reasonable memory usage
                if allocated_gb < 1.0:
                    print("")
                    print("⚠️  WARNING: Very low memory usage!")
                    print(f"   Expected: 4-5 GB, Got: {allocated_gb:.2f} GB")
                    print("   Model weights may not be loaded correctly!")
                elif allocated_gb < 3.0:
                    print("")
                    print("⚠️  WARNING: Lower than expected memory")
                    print(f"   Expected: 4-5 GB, Got: {allocated_gb:.2f} GB")
                elif allocated_gb > 12.0:
                    print("")
                    print("⚠️  WARNING: High memory usage")
                    print(f"   Expected: 4-5 GB, Got: {allocated_gb:.2f} GB")
                    print("   May cause issues on T4 (16GB)")
                else:
                    print("")
                    print(f"✅ Memory usage looks good! ({allocated_gb:.2f} GB)")
            
            print("")
            print("="*70)
            print("🎉 READY FOR INFERENCE!")
            print("="*70)
            
            logger.info(f"✅ Model loaded successfully")
            logger.info(f"📊 Device: {device}")
            logger.info(f"💾 Memory: {allocated_gb:.2f} GB allocated")
            
            return self.model, self.processor
            
        except Exception as e:
            print("")
            print("="*70)
            print("❌ MODEL LOADING FAILED")
            print("="*70)
            print(f"Error: {str(e)}")
            print("")
            print("🔍 Troubleshooting:")
            print("1. Check HF_TOKEN is valid")
            print("2. Verify internet connection")
            print("3. Ensure GPU is enabled (T4)")
            print("4. Check HuggingFace access to MedGemma")
            print("="*70)
            
            logger.error(f"❌ Model loading failed: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def get_model_info(self) -> dict:
        """
        Get model information
        
        Returns:
            Dictionary with model metadata
        """
        if self.model is None:
            return {
                "status": "not_loaded",
                "message": "Model not loaded. Call load_model() first."
            }
        
        info = {
            "status": "loaded",
            "model_name": self.model_name,
            "device": str(self.model.device),
            "dtype": str(self.model.dtype),
            "quantization": "INT8",
            "quantization_bits": 8
        }
        
        # Add memory info if CUDA available
        if torch.cuda.is_available():
            info["memory_allocated_gb"] = f"{torch.cuda.memory_allocated() / 1e9:.2f}"
            info["memory_reserved_gb"] = f"{torch.cuda.memory_reserved() / 1e9:.2f}"
        
        return info


def load_medgemma(model_name: str = "google/medgemma-4b-it"):
    """
    Quick function to load MedGemma with INT8 quantization
    
    HARDCODED INT8 - no options for safety
    
    Args:
        model_name: HuggingFace model ID (default: google/medgemma-4b-it)
        
    Returns:
        Tuple of (model, processor)
        
    Example:
        >>> model, processor = load_medgemma()
        >>> # Model ready for inference
    """
    loader = MedGemmaModelLoader(model_name=model_name)
    return loader.load_model()


# GPU validation helper
def validate_gpu():
    """
    Validate GPU is available and suitable
    
    Returns:
        True if GPU OK, False otherwise
    """
    print("🎮 GPU Validation")
    print("="*50)
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available!")
        print("   Enable GPU in Kaggle settings")
        print("   Settings → Accelerator → GPU T4")
        return False
    
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    print(f"✅ CUDA available")
    print(f"📊 GPU: {gpu_name}")
    print(f"💾 Total Memory: {gpu_memory_gb:.2f} GB")
    
    # Check if T4 or better
    if "T4" in gpu_name:
        print(f"✅ T4 GPU detected - perfect for INT8 MedGemma")
    elif gpu_memory_gb < 12:
        print(f"⚠️  GPU has only {gpu_memory_gb:.2f}GB")
        print(f"   Minimum 12GB recommended for INT8")
        return False
    else:
        print(f"✅ GPU suitable ({gpu_memory_gb:.2f}GB)")
    
    print("="*50)
    return True
