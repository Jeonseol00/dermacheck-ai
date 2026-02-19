"""
Timeline Manager for tracking lesion progression over time
Stores and compares historical lesion data
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from PIL import Image
import shutil
from utils.config import Config


class TimelineManager:
    """
    Manages timeline tracking for skin lesions
    Stores images and analysis results for progression monitoring
    """
    
    def __init__(self, user_id: str = "default_user"):
        """
        Initialize timeline manager
        
        Args:
            user_id: Unique identifier for user (session ID or account ID)
        """
        self.user_id = user_id
        self.data_file = os.path.join(Config.UPLOAD_DIR, f"{user_id}_timeline.json")
        self.image_dir = os.path.join(Config.UPLOAD_DIR, user_id)
        
        # Create directories
        os.makedirs(self.image_dir, exist_ok=True)
        
        # Load existing data
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load timeline data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading timeline data: {e}")
                return self._get_empty_data()
        return self._get_empty_data()
    
    def _get_empty_data(self) -> Dict:
        """Get empty data structure"""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "lesions": []
        }
    
    def _save_data(self):
        """Save timeline data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving timeline data: {e}")
    
    def add_lesion_entry(self, image: Image.Image, abcde_results: Dict, 
                        body_location: str, lesion_id: Optional[str] = None) -> str:
        """
        Add new lesion entry or update existing lesion timeline
        
        Args:
            image: PIL Image of lesion
            abcde_results: Results from ABCDE analysis
            body_location: Body location (e.g., "left_shoulder", "face")
            lesion_id: Optional ID if updating existing lesion
            
        Returns:
            lesion_id for this entry
        """
        timestamp = datetime.now().isoformat()
        
        # Generate lesion_id if not provided
        if lesion_id is None:
            lesion_id = self._generate_lesion_id(body_location)
        
        # Save image
        image_filename = f"{lesion_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image_path = os.path.join(self.image_dir, image_filename)
        image.save(image_path, "JPEG", quality=95)
        
        # Create timeline entry
        entry = {
            "timestamp": timestamp,
            "image_path": image_path,
            "image_filename": image_filename,
            "abcde_score": abcde_results["total_score"],
            "risk_level": abcde_results["risk_level"],
            "size_mm": abcde_results["visual_features"]["size_mm"],
            "lesion_area": abcde_results["visual_features"]["lesion_area"],
            "individual_scores": abcde_results["abcde_scores"]
        }
        
        # Find existing lesion or create new one
        lesion = self._find_lesion(lesion_id)
        
        if lesion:
            # Update existing lesion timeline
            lesion["timeline"].append(entry)
            lesion["last_updated"] = timestamp
        else:
            # Create new lesion
            new_lesion = {
                "lesion_id": lesion_id,
                "body_location": body_location,
                "created_at": timestamp,
                "last_updated": timestamp,
                "timeline": [entry]
            }
            self.data["lesions"].append(new_lesion)
        
        # Save data
        self._save_data()
        
        return lesion_id
    
    def get_lesion_timeline(self, lesion_id: str) -> Optional[List[Dict]]:
        """
        Get complete timeline for a specific lesion
        
        Args:
            lesion_id: ID of lesion
            
        Returns:
            List of timeline entries, or None if not found
        """
        lesion = self._find_lesion(lesion_id)
        if lesion:
            return lesion["timeline"]
        return None
    
    def get_all_lesions(self) -> List[Dict]:
        """
        Get all tracked lesions for this user
        
        Returns:
            List of lesion dictionaries
        """
        return self.data["lesions"]
    
    def get_latest_entry(self, lesion_id: str) -> Optional[Dict]:
        """
        Get most recent entry for a lesion
        
        Args:
            lesion_id: ID of lesion
            
        Returns:
            Latest timeline entry, or None if not found
        """
        timeline = self.get_lesion_timeline(lesion_id)
        if timeline and len(timeline) > 0:
            return timeline[-1]
        return None
    
    def get_previous_entry(self, lesion_id: str) -> Optional[Dict]:
        """
        Get second most recent entry (for comparison)
        
        Args:
            lesion_id: ID of lesion
            
        Returns:
            Previous timeline entry, or None if not enough history
        """
        timeline = self.get_lesion_timeline(lesion_id)
        if timeline and len(timeline) > 1:
            return timeline[-2]
        return None
    
    def compare_entries(self, lesion_id: str, entry1_idx: int = -2, 
                       entry2_idx: int = -1) -> Optional[Dict]:
        """
        Compare two timeline entries
        
        Args:
            lesion_id: ID of lesion
            entry1_idx: Index of first entry (default: second-to-last)
            entry2_idx: Index of second entry (default: last)
            
        Returns:
            Comparison dictionary with changes, or None if insufficient data
        """
        timeline = self.get_lesion_timeline(lesion_id)
        
        if not timeline or len(timeline) < 2:
            return None
        
        entry1 = timeline[entry1_idx]
        entry2 = timeline[entry2_idx]
        
        # Calculate changes
        size_change = entry2["size_mm"] - entry1["size_mm"]
        size_change_percent = (size_change / entry1["size_mm"]) * 100 if entry1["size_mm"] > 0 else 0
        
        score_change = entry2["abcde_score"] - entry1["abcde_score"]
        
        # Time difference
        time1 = datetime.fromisoformat(entry1["timestamp"])
        time2 = datetime.fromisoformat(entry2["timestamp"])
        days_elapsed = (time2 - time1).days
        
        # Alert check
        alert = self._check_alerts(size_change_percent, score_change, days_elapsed)
        
        return {
            "entry1": entry1,
            "entry2": entry2,
            "changes": {
                "size_mm": size_change,
                "size_percent": size_change_percent,
                "score": score_change,
                "risk_level_change": entry1["risk_level"] != entry2["risk_level"]
            },
            "time_elapsed_days": days_elapsed,
            "alert": alert
        }
    
    def _check_alerts(self, size_change_percent: float, score_change: int, 
                     days_elapsed: int) -> Optional[Dict]:
        """
        Check if changes warrant an alert
        
        Args:
            size_change_percent: Percentage change in size
            score_change: Change in ABCDE score
            days_elapsed: Days between measurements
            
        Returns:
            Alert dictionary if threshold exceeded, None otherwise
        """
        alerts = []
        
        # Size increase alert
        if size_change_percent > (Config.ALERT_SIZE_CHANGE_THRESHOLD * 100):
            alerts.append({
                "type": "size_increase",
                "severity": "high" if size_change_percent > 30 else "medium",
                "message": f"Lesion size increased by {size_change_percent:.1f}% in {days_elapsed} days"
            })
        
        # Score increase alert
        if score_change >= 2:
            alerts.append({
                "type": "score_increase",
                "severity": "high",
                "message": f"Risk score increased by {score_change} points"
            })
        
        # Rapid growth alert (within 30 days)
        if days_elapsed <= Config.ALERT_TIMEFRAME_DAYS and size_change_percent > 10:
            alerts.append({
                "type": "rapid_growth",
                "severity": "high",
                "message": f"Rapid growth detected: {size_change_percent:.1f}% in {days_elapsed} days"
            })
        
        if alerts:
            return {
                "has_alert": True,
                "alerts": alerts,
                "recommendation": "Schedule dermatologist consultation soon"
            }
        
        return None
    
    def _find_lesion(self, lesion_id: str) -> Optional[Dict]:
        """Find lesion by ID"""
        for lesion in self.data["lesions"]:
            if lesion["lesion_id"] == lesion_id:
                return lesion
        return None
    
    def _generate_lesion_id(self, body_location: str) -> str:
        """Generate unique lesion ID"""
        # Count existing lesions at this location
        location_lesions = [l for l in self.data["lesions"] 
                           if l["body_location"] == body_location]
        count = len(location_lesions) + 1
        
        # Create ID
        location_code = body_location.replace(" ", "_").lower()
        return f"{location_code}_{count:03d}"
    
    def delete_lesion(self, lesion_id: str) -> bool:
        """
        Delete lesion and all associated data
        
        Args:
            lesion_id: ID of lesion to delete
            
        Returns:
            True if deleted, False if not found
        """
        lesion = self._find_lesion(lesion_id)
        
        if not lesion:
            return False
        
        # Delete images
        for entry in lesion["timeline"]:
            image_path = entry["image_path"]
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image {image_path}: {e}")
        
        # Remove from data
        self.data["lesions"] = [l for l in self.data["lesions"] 
                               if l["lesion_id"] != lesion_id]
        
        self._save_data()
        return True
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for all tracked lesions
        
        Returns:
            Dictionary with summary stats
        """
        total_lesions = len(self.data["lesions"])
        total_entries = sum(len(l["timeline"]) for l in self.data["lesions"])
        
        # Risk distribution
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        
        for lesion in self.data["lesions"]:
            latest = lesion["timeline"][-1]
            risk = latest["risk_level"]
            if risk == "HIGH":
                high_risk_count += 1
            elif risk == "MEDIUM":
                medium_risk_count += 1
            else:
                low_risk_count += 1
        
        return {
            "total_lesions": total_lesions,
            "total_entries": total_entries,
            "risk_distribution": {
                "high": high_risk_count,
                "medium": medium_risk_count,
                "low": low_risk_count
            }
        }
