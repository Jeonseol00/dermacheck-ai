"""
MedGemma Local Model Loader
Handles HuggingFace model loading with optimization for Kaggle T4 GPU
"""

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig
from PIL import Image
from typing import Union, List, Optional
import logging

logger = logging.getLogger(__name__)


class MedGemmaModelLoader:
    """
    Loads and manages local MedGemma model with quantization
    Optimized for Kaggle T4 GPU (16GB VRAM)
    """
    
    def __init__(
        self,
        model_name: str = "google/medgemma-4b-it",
        quantize_4bit: bool = True,
        device_map: str = "auto"
    ):
        """
        Initialize model loader
        
        Args:
            model_name: HuggingFace model ID (default: google/medgemma-4b-it)
            quantize_4bit: Enable 4-bit quantization for T4 GPU compatibility
            device_map: Device mapping strategy ('auto' recommended)
        """
        self.model_name = model_name
        self.quantize_4bit = quantize_4bit
        self.device_map = device_map
        
        self.model = None
        self.processor = None
        
        logger.info(f"Initialized MedGemmaModelLoader for {model_name}")
    
    def load_model(self):
        """
        Load MedGemma model with quantization
        
        This method:
        1. Configures 4-bit quantization (if enabled)
        2. Loads processor for image+text preprocessing
        3. Loads model weights from HuggingFace
        4. Validates GPU allocation
        
        Returns:
            Tuple of (model, processor)
            
        Raises:
            ValueError: If HuggingFace token not configured
            RuntimeError: If model loading fails
        """
        logger.info(f"🔄 Loading {self.model_name}...")
        print(f"🔄 Loading {self.model_name} (this may take 2-3 minutes)...")
        
        # Configure quantization for T4 GPU (16GB VRAM)
        if self.quantize_4bit:
            logger.info("Configuring 4-bit quantization...")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",  # NormalFloat4 quantization
                bnb_4bit_use_double_quant=True  # Nested quantization for better memory
            )
        else:
            quantization_config = None
            logger.warning("Running without quantization - requires 32GB+ VRAM")
        
        try:
            # Load processor (handles image + text preprocessing)
            logger.info("📝 Loading processor...")
            print("📝 Loading processor...")
            self.processor = AutoProcessor.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            logger.info("🧠 Loading model weights...")
            print("🧠 Loading model weights...")
            self.model = AutoModelForImageTextToText.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map=self.device_map,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            
            # Log success info
            device_info = str(self.model.device)
            param_count = sum(p.numel() for p in self.model.parameters()) / 1e9
            
            logger.info(f"✅ Model loaded successfully!")
            logger.info(f"📊 Device: {device_info}")
            logger.info(f"💾 Parameters: {param_count:.2f}B")
            logger.info(f"🔧 Quantized: {self.quantize_4bit}")
            
            print("✅ Model loaded successfully!")
            print(f"📊 Model device: {device_info}")
            print(f"💾 Quantized: {self.quantize_4bit}")
            print(f"🎯 Ready for inference!")
            
            return self.model, self.processor
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")
    
    def get_model_info(self) -> dict:
        """
        Get detailed model information
        
        Returns:
            Dictionary with model metadata
        """
        if self.model is None:
            return {
                "status": "not_loaded",
                "message": "Model not loaded yet. Call load_model() first."
            }
        
        # Calculate memory usage if on CUDA
        memory_allocated = 0
        memory_reserved = 0
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1e9  # GB
            memory_reserved = torch.cuda.memory_reserved() / 1e9  # GB
        
        return {
            "status": "loaded",
            "model_name": self.model_name,
            "device": str(self.model.device),
            "dtype": str(self.model.dtype),
            "quantized": self.quantize_4bit,
            "parameters": f"{sum(p.numel() for p in self.model.parameters()) / 1e9:.2f}B",
            "memory_allocated_gb": f"{memory_allocated:.2f}",
            "memory_reserved_gb": f"{memory_reserved:.2f}"
        }
    
    def validate_gpu(self) -> bool:
        """
        Validate GPU availability and compatibility
        
        Returns:
            True if GPU available and suitable, False otherwise
        """
        if not torch.cuda.is_available():
            logger.warning("⚠️ CUDA not available - model will run on CPU (very slow)")
            return False
        
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9  # GB
        
        logger.info(f"🎮 GPU: {gpu_name}")
        logger.info(f"💾 GPU Memory: {gpu_memory:.2f} GB")
        
        # Check if T4 or better
        recommended_gpus = ["T4", "V100", "A100", "A10", "L4"]
        is_recommended = any(gpu in gpu_name for gpu in recommended_gpus)
        
        if not is_recommended:
            logger.warning(f"⚠️ GPU {gpu_name} not in recommended list. May be slow.")
        
        # Check memory
        if gpu_memory < 12:
            logger.warning(f"⚠️ GPU has only {gpu_memory:.2f}GB. Minimum 12GB recommended.")
            return False
        
        logger.info("✅ GPU validation passed")
        return True
    
    def unload_model(self):
        """
        Unload model from memory to free GPU
        Useful for switching models or cleaning up
        """
        if self.model is not None:
            logger.info("🗑️ Unloading model from memory...")
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ Model unloaded successfully")
            print("✅ Model unloaded from memory")


# Convenience function for quick loading
def load_medgemma(
    model_name: str = "google/medgemma-4b-it",
    quantize: bool = True
):
    """
    Quick function to load MedGemma model
    
    Args:
        model_name: HuggingFace model ID
        quantize: Enable 4-bit quantization
        
    Returns:
        Tuple of (model, processor)
        
    Example:
        >>> model, processor = load_medgemma()
        >>> # Ready to use for inference
    """
    loader = MedGemmaModelLoader(
        model_name=model_name,
        quantize_4bit=quantize
    )
    
    # Validate GPU before loading
    loader.validate_gpu()
    
    # Load model
    return loader.load_model()
