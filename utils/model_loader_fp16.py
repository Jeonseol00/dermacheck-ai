"""
MedGemma Model Loader - FP16 (NO QUANTIZATION)
Stable inference for T4 GPU with 16GB VRAM
"""

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
from typing import Union, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class MedGemmaModelLoader:
    """
    Load MedGemma with FP16 precision (no quantization)
    Memory: ~8GB for 4B model - fits perfectly in T4 (16GB)
    """
    
    def __init__(
        self,
        model_name: str = "google/medgemma-4b-it",
        device_map: str = "auto"
    ):
        self.model_name = model_name
        self.device_map = device_map
        
        self.model = None
        self.processor = None
        
        # Get HF token
        self.hf_token = os.environ.get('HF_TOKEN')
        if not self.hf_token:
            raise ValueError("HF_TOKEN not found in environment")
        
        logger.info(f"Initialized MedGemmaModelLoader for {model_name}")
        logger.info("Mode: FP16 (NO QUANTIZATION) for numerical stability")
    
    def load_model(self):
        """
        Load MedGemma with FP16 precision
        
        No BitsAndBytes quantization - direct FP16 loading
        Expected memory: ~8GB (fits in T4's 16GB)
        """
        logger.info(f"🔄 Loading {self.model_name} in FP16...")
        print(f"🔄 Loading {self.model_name} (FP16, ~2-3 minutes)...")
        
        try:
            # Load processor
            logger.info("📝 Loading processor...")
            print("📝 Loading processor...")
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                token=self.hf_token
            )
            
            # Load model - FP16, NO QUANTIZATION
            logger.info("🧠 Loading model weights (FP16)...")
            print("🧠 Loading model weights (FP16 - stable mode)...")
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,  # FP16 instead of INT4!
                device_map=self.device_map,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
                token=self.hf_token
            )
            
            # Set to eval mode
            self.model.eval()
            
            # Log success
            device_info = str(self.model.device)
            
            logger.info(f"✅ Model loaded successfully!")
            print("✅ Model loaded successfully!")
            print(f"📊 Device: {device_info}")
            print(f"💾 Precision: FP16 (float16)")
            print(f"🎯 Numerical stability: HIGH")
            print(f"🎯 Ready for inference!")
            
            # Check memory
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1e9
                reserved = torch.cuda.memory_reserved() / 1e9
                total = torch.cuda.get_device_properties(0).total_memory / 1e9
                
                print(f"\n💾 GPU Memory Usage:")
                print(f"   Allocated: {allocated:.2f} GB")
                print(f"   Reserved: {reserved:.2f} GB")
                print(f"   Total Available: {total:.2f} GB")
                print(f"   Free: {total - reserved:.2f} GB")
            
            return self.model, self.processor
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def get_model_info(self) -> dict:
        """Get model information"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        memory_allocated = 0
        memory_reserved = 0
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1e9
            memory_reserved = torch.cuda.memory_reserved() / 1e9
        
        return {
            "status": "loaded",
            "model_name": self.model_name,
            "device": str(self.model.device),
            "dtype": str(self.model.dtype),
            "precision": "FP16",
            "quantized": False,
            "memory_allocated_gb": f"{memory_allocated:.2f}",
            "memory_reserved_gb": f"{memory_reserved:.2f}"
        }
    
    def validate_gpu(self) -> bool:
        """Validate GPU availability"""
        if not torch.cuda.is_available():
            logger.warning("⚠️ CUDA not available")
            return False
        
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        
        logger.info(f"🎮 GPU: {gpu_name}")
        logger.info(f"💾 GPU Memory: {gpu_memory:.2f} GB")
        
        if gpu_memory < 12:
            logger.warning(f"⚠️ GPU has only {gpu_memory:.2f}GB. May be tight.")
            return False
        
        logger.info("✅ GPU validation passed")
        return True


def load_medgemma(model_name: str = "google/medgemma-4b-it"):
    """
    Quick function to load MedGemma in FP16
    
    NO QUANTIZATION - stable inference
    
    Args:
        model_name: HuggingFace model ID
        
    Returns:
        Tuple of (model, processor)
    """
    loader = MedGemmaModelLoader(model_name=model_name)
    loader.validate_gpu()
    return loader.load_model()
