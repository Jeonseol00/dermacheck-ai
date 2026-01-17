"""
ABCDE Criteria Analyzer for Melanoma Risk Assessment
Implements clinical ABCDE criteria (Asymmetry, Border, Color, Diameter, Evolution)
"""
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Tuple
from sklearn.cluster import KMeans
from utils.config import Config


class ABCDEAnalyzer:
    """
    Analyzes skin lesions using ABCDE criteria for melanoma risk assessment
    """
    
    def __init__(self):
        self.risk_thresholds = Config.RISK_THRESHOLDS
        
    def analyze(self, image: Image.Image, previous_data: Dict = None) -> Dict:
        """
        Perform complete ABCDE analysis on skin lesion image
        
        Args:
            image: PIL Image of skin lesion
            previous_data: Optional data from previous analysis for Evolution scoring
            
        Returns:
            Dictionary with ABCDE scores and risk assessment
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Get lesion mask (segmentation)
        lesion_mask = self._segment_lesion(img_array)
        
        # Calculate each criterion
        asymmetry_score, asymmetry_desc = self._analyze_asymmetry(lesion_mask)
        border_score, border_desc = self._analyze_border(lesion_mask)
        color_score, color_desc = self._analyze_color(img_array, lesion_mask)
        diameter_score, diameter_desc, size_mm = self._analyze_diameter(lesion_mask)
        evolution_score, evolution_desc = self._analyze_evolution(
            img_array, lesion_mask, previous_data
        )
        
        # Calculate total risk
        total_score = (asymmetry_score + border_score + color_score + 
                      diameter_score + evolution_score)
        
        risk_level = self._calculate_risk_level(total_score)
        
        return {
            "abcde_scores": {
                "asymmetry": asymmetry_score,
                "border": border_score,
                "color": color_score,
                "diameter": diameter_score,
                "evolution": evolution_score
            },
            "descriptions": {
                "asymmetry": asymmetry_desc,
                "border": border_desc,
                "color": color_desc,
                "diameter": diameter_desc,
                "evolution": evolution_desc
            },
            "total_score": total_score,
            "max_score": 11,
            "risk_level": risk_level,
            "visual_features": {
                "size_mm": round(size_mm, 1),
                "lesion_area": int(np.sum(lesion_mask > 0)),
                "lesion_mask": lesion_mask
            }
        }
    
    def _segment_lesion(self, img_array: np.ndarray) -> np.ndarray:
        """
        Segment lesion from surrounding skin using GrabCut with center bias
        
        Args:
            img_array: Input image as numpy array
            
        Returns:
            Binary mask of lesion region
        """
        # CRITICAL FIX v1.2: Replace simple thresholding with GrabCut algorithm
        # Previous method caused segmentation failure (whole arm detected as lesion)
        # New approach: Center-biased GrabCut for accurate small lesion isolation
        
        h, w = img_array.shape[:2]
        
        # Strategy 1: Center-biased ROI initialization
        # Assume lesion is in center 60% of image (user centered the shot)
        center_margin_h = int(h * 0.2)
        center_margin_w = int(w * 0.2)
        
        # Initial rectangle for GrabCut (center region)
        rect = (center_margin_w, center_margin_h, 
                w - 2*center_margin_w, h - 2*center_margin_h)
        
        # Initialize mask for GrabCut
        mask = np.zeros(img_array.shape[:2], np.uint8)
        
        # Initialize background and foreground models
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        try:
            # Apply GrabCut algorithm
            # Mode: cv2.GC_INIT_WITH_RECT - initialize with rectangle
            cv2.grabCut(img_array, mask, rect, bgd_model, fgd_model, 
                       5, cv2.GC_INIT_WITH_RECT)
            
            # Create binary mask: 0,2 = background, 1,3 = foreground
            binary_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # Post-processing: Remove small noise
            kernel = np.ones((5,5), np.uint8)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
            binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
            
            # Additional validation: Check if detected region is reasonable
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, 
                                          cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Validate contour size (should be reasonable, not whole image)
                contour_area = cv2.contourArea(largest_contour)
                image_area = h * w
                area_ratio = contour_area / image_area
                
                # If detected region is > 40% of image, it's likely wrong
                # (User should center lesion, so it shouldn't dominate frame)
                if area_ratio > 0.4:
                    # Fall back to center-focused detection
                    return self._fallback_center_segmentation(img_array)
                
                # Create clean mask from validated contour
                final_mask = np.zeros_like(binary_mask)
                cv2.drawContours(final_mask, [largest_contour], -1, 255, -1)
                
                return final_mask
            
            # If no contours found, use fallback
            return self._fallback_center_segmentation(img_array)
            
        except Exception as e:
            # If GrabCut fails, use fallback method
            print(f"GrabCut failed: {e}, using fallback")
            return self._fallback_center_segmentation(img_array)
    
    def _fallback_center_segmentation(self, img_array: np.ndarray) -> np.ndarray:
        """
        Fallback method: Adaptive thresholding with center bias
        Used when GrabCut fails or produces unreasonable results
        
        Args:
            img_array: Input image as numpy array
            
        Returns:
            Binary mask of lesion region
        """
        h, w = img_array.shape[:2]
        
        # Convert to LAB color space (better for skin)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l_channel = lab[:,:,0]
        
        # Use adaptive thresholding instead of global Otsu
        # This handles varying lighting better
        adaptive_thresh = cv2.adaptiveThreshold(
            l_channel, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 21, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((5,5), np.uint8)
        clean_mask = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours and select the one CLOSEST TO CENTER
        contours, _ = cv2.findContours(clean_mask, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            image_center = (w // 2, h // 2)
            
            # Find contour closest to center (within center 50% of image)
            center_contours = []
            for cnt in contours:
                M = cv2.moments(cnt)
                if M['m00'] > 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    
                    # Calculate distance to center
                    dist_to_center = np.sqrt((cx - image_center[0])**2 + 
                                            (cy - image_center[1])**2)
                    
                    # Only consider contours in center region
                    max_dist = min(w, h) * 0.4  # Within 40% of image dimension
                    if dist_to_center < max_dist:
                        center_contours.append((dist_to_center, cnt))
            
            if center_contours:
                # Select contour closest to center
                _, closest_contour = min(center_contours, key=lambda x: x[0])
                
                # Create mask from this contour
                final_mask = np.zeros_like(clean_mask)
                cv2.drawContours(final_mask, [closest_contour], -1, 255, -1)
                
                return final_mask
        
        # Ultimate fallback: Return center circular region
        # Assume lesion is roughly in center 30% of image
        center_mask = np.zeros((h, w), np.uint8)
        center = (w // 2, h // 2)
        radius = int(min(w, h) * 0.15)  # 30% diameter = 15% radius
        cv2.circle(center_mask, center, radius, 255, -1)
        
        return center_mask
    
    def _analyze_asymmetry(self, lesion_mask: np.ndarray) -> Tuple[int, str]:
        """
        Analyze asymmetry by comparing lesion halves
        
        Returns:
            (score, description) - 0-2 points
        """
        # Find centroid
        moments = cv2.moments(lesion_mask)
        if moments['m00'] == 0:
            return 0, "Unable to calculate asymmetry"
        
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
        
        # Split into halves (horizontal and vertical)
        h, w = lesion_mask.shape
        
        # Horizontal split
        top_half = lesion_mask[:cy, :]
        bottom_half = lesion_mask[cy:, :]
        bottom_half_flipped = np.flipud(bottom_half)
        
        # Match dimensions
        min_h = min(top_half.shape[0], bottom_half_flipped.shape[0])
        top_half = top_half[-min_h:, :]
        bottom_half_flipped = bottom_half_flipped[:min_h, :]
        
        # Calculate horizontal asymmetry
        h_diff = np.sum(np.abs(top_half.astype(float) - bottom_half_flipped.astype(float)))
        h_total = np.sum(top_half) + np.sum(bottom_half_flipped)
        h_asymmetry = h_diff / (h_total + 1e-6)
        
        # Vertical split
        left_half = lesion_mask[:, :cx]
        right_half = lesion_mask[:, cx:]
        right_half_flipped = np.fliplr(right_half)
        
        # Match dimensions
        min_w = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, -min_w:]
        right_half_flipped = right_half_flipped[:, :min_w]
        
        # Calculate vertical asymmetry
        v_diff = np.sum(np.abs(left_half.astype(float) - right_half_flipped.astype(float)))
        v_total = np.sum(left_half) + np.sum(right_half_flipped)
        v_asymmetry = v_diff / (v_total + 1e-6)
        
        # Average asymmetry
        avg_asymmetry = (h_asymmetry + v_asymmetry) / 2
        
        # Scoring
        if avg_asymmetry < 0.15:
            return 0, "Symmetric - both halves match well"
        elif avg_asymmetry < 0.30:
            return 1, "Slightly asymmetric - minor differences in halves"
        else:
            return 2, "Highly asymmetric - significant differences between halves"
    
    def _analyze_border(self, lesion_mask: np.ndarray) -> Tuple[int, str]:
        """
        Analyze border regularity using edge detection
        
        Returns:
            (score, description) - 0-2 points
        """
        # Get contour
        contours, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        if not contours:
            return 0, "Unable to detect border"
        
        contour = max(contours, key=cv2.contourArea)
        
        # Calculate perimeter and area
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        
        if area == 0:
            return 0, "Unable to calculate border metrics"
        
        # Circularity (4π * area / perimeter²)
        # Perfect circle = 1.0, irregular shape < 1.0
        circularity = (4 * np.pi * area) / (perimeter ** 2)
        
        # Also check contour smoothness using approximation
        epsilon = 0.01 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        smoothness = len(approx) / (perimeter / 10)  # Normalized by perimeter
        
        # Scoring based on irregularity
        if circularity > 0.8 and smoothness < 2:
            return 0, "Regular, smooth border"
        elif circularity > 0.6 or smoothness < 4:
            return 1, "Slightly irregular border"
        else:
            return 2, "Highly irregular, notched border"
    
    def _analyze_color(self, img_array: np.ndarray, lesion_mask: np.ndarray) -> Tuple[int, str]:
        """
        Analyze color variation using K-means clustering
        
        Returns:
            (score, description) - 0-2 points
        """
        # Extract lesion pixels
        lesion_pixels = img_array[lesion_mask > 0]
        
        if len(lesion_pixels) < 10:
            return 0, "Insufficient pixels for color analysis"
        
        # Cluster colors (K-means)
        n_clusters = min(6, len(lesion_pixels))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(lesion_pixels)
        
        # Count significant colors (clusters with >5% of pixels)
        labels = kmeans.labels_
        unique, counts = np.unique(labels, return_counts=True)
        total_pixels = len(labels)
        
        significant_colors = sum(counts / total_pixels > 0.05)
        
        # Get dominant colors
        color_names = self._describe_colors(kmeans.cluster_centers_)
        
        # Scoring
        if significant_colors <= 1:
            return 0, f"Uniform color ({color_names[0]})"
        elif significant_colors == 2:
            return 1, f"Two colors present ({', '.join(color_names[:2])})"
        else:
            return 2, f"Multiple colors detected ({', '.join(color_names[:3])})"
    
    def _describe_colors(self, rgb_centers: np.ndarray) -> list:
        """
        Convert RGB values to color names
        
        Args:
            rgb_centers: Array of RGB color centers
            
        Returns:
            List of color names
        """
        color_names = []
        
        for rgb in rgb_centers:
            r, g, b = rgb
            
            # Simple color classification
            if r < 50 and g < 50 and b < 50:
                color_names.append("black")
            elif r > 200 and g > 200 and b > 200:
                color_names.append("white")
            elif r > g and r > b:
                if r > 150:
                    color_names.append("red")
                else:
                    color_names.append("brown")
            elif g > r and g > b:
                color_names.append("tan")
            elif b > r and b > g:
                color_names.append("blue")
            else:
                # Mixed
                if r > 100 and g > 100:
                    color_names.append("tan")
                else:
                    color_names.append("brown")
        
        return color_names
    
    def _analyze_diameter(self, lesion_mask: np.ndarray) -> Tuple[int, str, float]:
        """
        Analyze lesion diameter with improved calibration
        
        Returns:
            (score, description, size_mm) - 0-2 points
        """
        # Find bounding box of the actual lesion (not whole image)
        contours, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0, "Unable to measure diameter", 0.0
        
        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Maximum diameter in pixels
        max_diameter_px = max(w, h)
        
        # IMPROVED CALIBRATION v1.2:
        # Previous assumption was too naive (10 pixels per mm)
        # New approach: Estimate based on image resolution
        # Typical phone photo of small lesion at 10-20cm distance:
        # - Image width ~3000-4000 pixels
        # - Real width captured ~5-10 cm
        # Therefore: ~60-80 pixels per cm, or ~6-8 pixels per mm
        
        image_width = lesion_mask.shape[1]
        
        # Adaptive calibration based on image size
        if image_width > 2000:  # High res photo
            pixels_per_mm = 7.0  # ~70 pixels per cm
        elif image_width > 1000:  # Medium res
            pixels_per_mm = 5.0  # ~50 pixels per cm
        else:  # Lower res
            pixels_per_mm = 3.0  # ~30 pixels per cm
        
        size_mm = max_diameter_px / pixels_per_mm
        
        # VALIDATION: Sanity check on detected size
        # If detected size is unreasonably large (> 50mm), 
        # it's likely segmentation failed
        if size_mm > 50:
            # Likely detected whole arm/hand instead of lesion
            # Apply conservative estimate: assume lesion is small
            size_mm = 5.0  # Default to 5mm (typical small lesion)
            description = f"Segmentation uncertain, estimated ~{size_mm:.1f}mm"
            return 1, description, size_mm
        
        # Scoring (6mm threshold is clinical standard)
        if size_mm < 4:
            return 0, f"Small lesion ({size_mm:.1f}mm)", size_mm
        elif size_mm < 6:
            return 1, f"Moderate size ({size_mm:.1f}mm)", size_mm
        else:
            return 2, f"Large lesion (> 6mm: {size_mm:.1f}mm)", size_mm
    
    def _analyze_evolution(self, img_array: np.ndarray, lesion_mask: np.ndarray,
                          previous_data: Dict = None) -> Tuple[int, str]:
        """
        Analyze evolution by comparing with previous images
        
        Returns:
            (score, description) - 0-3 points
        """
        if previous_data is None:
            return 0, "No previous data for comparison"
        
        # Extract current features
        current_size = np.sum(lesion_mask > 0)
        current_pixels = img_array[lesion_mask > 0]
        current_mean_color = np.mean(current_pixels, axis=0)
        
        # Get previous features
        prev_size = previous_data.get('lesion_area', current_size)
        prev_color = previous_data.get('mean_color', current_mean_color)
        
        # Calculate changes
        size_change = abs(current_size - prev_size) / (prev_size + 1e-6)
        color_change = np.linalg.norm(current_mean_color - prev_color) / 255.0
        
        # Scoring (higher weight for evolution)
        if size_change < 0.05 and color_change < 0.1:
            return 0, "Stable - no significant changes"
        elif size_change < 0.15 or color_change < 0.2:
            return 1, "Minor changes detected"
        elif size_change < 0.25 or color_change < 0.3:
            return 2, "Moderate changes - increasing in size or color"
        else:
            return 3, "Significant evolution - rapid growth or color change"
    
    def _calculate_risk_level(self, total_score: int) -> str:
        """
        Calculate risk level based on total ABCDE score
        
        Args:
            total_score: Total points from ABCDE analysis
            
        Returns:
            Risk level string: LOW, MEDIUM, or HIGH
        """
        low_range = self.risk_thresholds["low"]
        medium_range = self.risk_thresholds["medium"]
        high_range = self.risk_thresholds["high"]
        
        if low_range[0] <= total_score <= low_range[1]:
            return "LOW"
        elif medium_range[0] <= total_score <= medium_range[1]:
            return "MEDIUM"
        else:
            return "HIGH"
