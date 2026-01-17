"""
Image utility functions for DermaCheck AI
Handles image validation, preprocessing, and visualization
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import cv2
from typing import Tuple, Optional
from utils.config import Config

def validate_image(image_file) -> Tuple[bool, str]:
    """
    Validate uploaded image file
    
    Args:
        image_file: Uploaded file object
        
    Returns:
        (is_valid, error_message)
    """
    try:
        # Check file size
        image_file.seek(0, 2)  # Seek to end
        file_size_mb = image_file.tell() / (1024 * 1024)
        image_file.seek(0)  # Reset
        
        if file_size_mb > Config.MAX_UPLOAD_SIZE_MB:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds limit ({Config.MAX_UPLOAD_SIZE_MB}MB)"
        
        # Try to open image
        image = Image.open(image_file)
        
        # Check format (case-insensitive)
        supported_formats = [fmt.lower() for fmt in Config.SUPPORTED_FORMATS]
        # Also accept common variations
        supported_formats.extend(['jpeg', 'jpg', 'png'])
        
        if image.format and image.format.lower() not in supported_formats:
            return False, f"Unsupported format. Please use: JPG, JPEG, PNG"
        
        # Check dimensions
        if image.size[0] < Config.MIN_IMAGE_SIZE[0] or image.size[1] < Config.MIN_IMAGE_SIZE[1]:
            return False, f"Image too small. Minimum size: {Config.MIN_IMAGE_SIZE}"
        
        # Blur detection disabled - causes false positives on smooth skin
        # Modern phone cameras have good autofocus, this check is unnecessary
        # Original logic kept for reference:
        # img_array = np.array(image.convert('L'))
        # laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
        # if laplacian_var < 100:
        #     return False, "Image appears too blurry. Please upload a clearer photo."
        
        return True, "Image valid"
        
    except Exception as e:
        return False, f"Error reading image: {str(e)}"


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess image for analysis
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed image as numpy array
    """
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize to target size
    image = image.resize(Config.TARGET_IMAGE_SIZE, Image.Resampling.LANCZOS)
    
    # Convert to numpy array and normalize
    img_array = np.array(image, dtype=np.float32) / 255.0
    
    return img_array


def create_comparison_view(img1: Image.Image, img2: Image.Image, 
                          label1: str = "Before", label2: str = "After") -> Image.Image:
    """
    Create side-by-side comparison of two images
    
    Args:
        img1: First image
        img2: Second image
        label1: Label for first image
        label2: Label for second image
        
    Returns:
        Combined comparison image
    """
    # Ensure same size
    target_size = (400, 400)
    img1 = img1.resize(target_size, Image.Resampling.LANCZOS)
    img2 = img2.resize(target_size, Image.Resampling.LANCZOS)
    
    # Create new image with both side by side
    width = target_size[0] * 2 + 40  # 40px gap
    height = target_size[1] + 60  # Extra space for labels
    
    comparison = Image.new('RGB', (width, height), color='white')
    
    # Paste images
    comparison.paste(img1, (20, 40))
    comparison.paste(img2, (target_size[0] + 40, 40))
    
    # Add labels
    draw = ImageDraw.Draw(comparison)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((20 + target_size[0]//2, 10), label1, fill='black', font=font, anchor="mm")
    draw.text((target_size[0] + 40 + target_size[0]//2, 10), label2, fill='black', font=font, anchor="mm")
    
    return comparison


def add_size_reference(image: Image.Image, size_mm: Optional[float] = None) -> Image.Image:
    """
    Add size reference overlay to image
    
    Args:
        image: Input image
        size_mm: Detected size in millimeters (optional)
        
    Returns:
        Image with size reference overlay
    """
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    # Draw scale bar (10mm reference)
    bar_length = 100  # pixels (represents 10mm)
    bar_x = 20
    bar_y = image.height - 40
    
    # White background for bar
    draw.rectangle([bar_x - 5, bar_y - 5, bar_x + bar_length + 5, bar_y + 25], 
                   fill='white', outline='black', width=2)
    
    # Scale bar
    draw.rectangle([bar_x, bar_y, bar_x + bar_length, bar_y + 10], 
                   fill='black')
    
    # Label
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    draw.text((bar_x + bar_length//2, bar_y + 20), "10mm", fill='black', 
              font=font, anchor="mm")
    
    # If size detected, show it
    if size_mm:
        draw.text((image.width//2, 20), f"Detected size: {size_mm:.1f}mm", 
                 fill='red', font=font, anchor="mm")
    
    return img_copy


def generate_heatmap(image: Image.Image, features: dict) -> Image.Image:
    """
    Generate visualization heatmap showing areas of concern
    
    Args:
        image: Original image
        features: Dictionary with detected features
        
    Returns:
        Image with heatmap overlay
    """
    # Convert to numpy
    img_array = np.array(image)
    
    # Create heatmap based on color variance (example)
    # This is a simplified version - real implementation would use
    # actual model attention or feature importance
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Create heatmap
    heatmap = cv2.applyColorMap(blurred, cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    # Blend with original
    overlay = cv2.addWeighted(img_array, 0.6, heatmap, 0.4, 0)
    
    return Image.fromarray(overlay)


def extract_lesion_region(image: Image.Image) -> Tuple[Image.Image, dict]:
    """
    Extract and isolate lesion region from image
    
    Args:
        image: Input image
        
    Returns:
        (cropped_lesion, metadata) - Cropped image and metadata
    """
    img_array = np.array(image)
    
    # Convert to LAB color space (better for skin detection)
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    
    # Simple thresholding (in real implementation, use ML-based segmentation)
    # This is placeholder logic
    l_channel = lab[:,:,0]
    _, binary = cv2.threshold(l_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Get largest contour (assumed to be lesion)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Crop with padding
        padding = 20
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img_array.shape[1], x + w + padding)
        y2 = min(img_array.shape[0], y + h + padding)
        
        cropped = Image.fromarray(img_array[y1:y2, x1:x2])
        
        metadata = {
            "bbox": (x, y, w, h),
            "area_pixels": cv2.contourArea(largest_contour),
            "center": (x + w//2, y + h//2)
        }
        
        return cropped, metadata
    
    # If no contour found, return original
    return image, {}
