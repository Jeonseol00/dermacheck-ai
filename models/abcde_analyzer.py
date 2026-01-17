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
        Segment lesion from surrounding skin
        
        Args:
            img_array: Input image as numpy array
            
        Returns:
            Binary mask of lesion region
        """
        # Convert to LAB color space (better for skin)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l_channel = lab[:,:,0]
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(l_channel, (5, 5), 0)
        
        # Otsu thresholding
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = np.ones((5,5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find largest contour (assumed to be lesion)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(binary)
            cv2.drawContours(mask, [largest_contour], -1, 255, -1)
            return mask
        
        return binary
    
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
        Analyze lesion diameter
        
        Returns:
            (score, description, size_mm) - 0-2 points
        """
        # Find bounding box
        contours, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 0, "Unable to measure diameter", 0.0
        
        contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Maximum diameter in pixels
        max_diameter_px = max(w, h)
        
        # Convert to mm (assumption: ~10 pixels per mm - this should be calibrated)
        # In real app, user would provide a reference object
        pixels_per_mm = 10
        size_mm = max_diameter_px / pixels_per_mm
        
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
