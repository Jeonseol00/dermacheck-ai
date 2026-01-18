"""
API Key Manager - Project Sherlock
Manages round-robin rotation of multiple Gemini API keys for load balancing
"""
from typing import List, Optional, Dict
import os
from datetime import datetime, timedelta
import time


def load_env_file(env_path=".env"):
    """
    Simple .env file loader (standalone, no dependencies)
    Only loads if file exists and env vars not already set
    """
    if not os.path.exists(env_path):
        # Try alternative path (Kaggle might have different structure)
        alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', env_path)
        if os.path.exists(alt_path):
            env_path = alt_path
        else:
            return  # No .env file found, rely on system env vars
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value


class APIKeyRotator:
    """
    Round-robin API key rotation with failure tracking and cooldown management
    
    Features:
    - Automatic rotation across multiple API keys
    - Failure tracking per key
    - Cooldown period for rate-limited keys
    - Usage statistics
    - Kaggle/Cloud environment compatible
    """
    
    def __init__(self):
        """Initialize API key rotator with keys from environment"""
        # Try to load .env file (but don't fail if not found)
        # This is optional - Kaggle uses system environment variables
        try:
            load_env_file()
        except Exception as e:
            print(f"⚠️ .env file not loaded (using system env vars): {e}")
        
        # Load all Sherlock API keys from environment
        # Priority: os.environ (system/Kaggle) > .env file
        self.keys: List[str] = []
        for i in range(1, 8):  # 7 keys total
            key = os.getenv(f'SHERLOCK_API_KEY_{i}')
            if key:
                self.keys.append(key)
        
        if not self.keys:
            raise ValueError("❌ No Sherlock API keys found in .env file!")
        
        # Rotation state
        self.current_index = 0
        self.total_keys = len(self.keys)
        
        # Failure tracking
        self.failure_counts: Dict[str, int] = {key: 0 for key in self.keys}
        self.cooldown_until: Dict[str, datetime] = {}
        
        # Usage statistics
        self.usage_counts: Dict[str, int] = {key: 0 for key in self.keys}
        self.last_used: Dict[str, datetime] = {}
        
        print(f"✅ API Key Rotator initialized with {self.total_keys} keys")
    
    def get_next_key(self) -> str:
        """
        Get the next available API key using round-robin rotation
        
        Returns:
            str: Next available API key
            
        Raises:
            RuntimeError: If all keys are in cooldown
        """
        attempts = 0
        max_attempts = self.total_keys * 2  # Try twice around the pool
        
        while attempts < max_attempts:
            # Get current key
            key = self.keys[self.current_index]
            
            # Check if key is available (not in cooldown)
            if self.is_available(key):
                # Mark as used
                self.usage_counts[key] += 1
                self.last_used[key] = datetime.now()
                
                # Move to next key for next request
                self.current_index = (self.current_index + 1) % self.total_keys
                
                return key
            
            # This key is in cooldown, try next
            self.current_index = (self.current_index + 1) % self.total_keys
            attempts += 1
        
        # All keys are in cooldown!
        raise RuntimeError("🚨 All API keys are currently in cooldown. Please wait.")
    
    def is_available(self, key: str) -> bool:
        """
        Check if a key is available (not in cooldown)
        
        Args:
            key: API key to check
            
        Returns:
            bool: True if available, False if in cooldown
        """
        if key not in self.cooldown_until:
            return True
        
        # Check if cooldown period has passed
        if datetime.now() >= self.cooldown_until[key]:
            # Cooldown expired, remove from cooldown list
            del self.cooldown_until[key]
            return True
        
        return False
    
    def mark_failure(self, key: str, error_code: Optional[int] = None):
        """
        Mark a key as failed and potentially put it in cooldown
        
        Args:
            key: The API key that failed
            error_code: Optional HTTP error code (429 for rate limit)
        """
        self.failure_counts[key] += 1
        
        # If rate limit error (429), put in cooldown
        if error_code == 429:
            # Cooldown for 60 seconds
            cooldown_duration = timedelta(seconds=60)
            self.cooldown_until[key] = datetime.now() + cooldown_duration
            print(f"⚠️ Key ending in ...{key[-6:]} hit rate limit. Cooldown until {self.cooldown_until[key].strftime('%H:%M:%S')}")
        
        # If too many failures (5+), put in longer cooldown
        elif self.failure_counts[key] >= 5:
            cooldown_duration = timedelta(minutes=5)
            self.cooldown_until[key] = datetime.now() + cooldown_duration
            print(f"❌ Key ending in ...{key[-6:]} failed 5+ times. Extended cooldown until {self.cooldown_until[key].strftime('%H:%M:%S')}")
    
    def mark_success(self, key: str):
        """
        Mark a key as successful (reset failure count)
        
        Args:
            key: The API key that succeeded
        """
        if self.failure_counts[key] > 0:
            self.failure_counts[key] = 0
            print(f"✅ Key ending in ...{key[-6:]} recovered")
    
    def get_stats(self) -> Dict:
        """
        Get usage statistics for all keys
        
        Returns:
            Dict with usage stats per key
        """
        stats = {
            "total_keys": self.total_keys,
            "keys_in_cooldown": len(self.cooldown_until),
            "keys_available": self.total_keys - len(self.cooldown_until),
            "usage_per_key": {}
        }
        
        for i, key in enumerate(self.keys, 1):
            key_id = f"Key_{i}"
            stats["usage_per_key"][key_id] = {
                "usage_count": self.usage_counts[key],
                "failure_count": self.failure_counts[key],
                "in_cooldown": key in self.cooldown_until,
                "last_used": self.last_used.get(key, "Never").isoformat() if isinstance(self.last_used.get(key), datetime) else "Never"
            }
        
        return stats
    
    def print_stats(self):
        """Print usage statistics to console"""
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print(" 📊 API KEY ROTATION STATISTICS")
        print("="*50)
        print(f"Total Keys: {stats['total_keys']}")
        print(f"Available: {stats['keys_available']}")
        print(f"In Cooldown: {stats['keys_in_cooldown']}")
        print("\nPer-Key Stats:")
        
        for key_id, key_stats in stats["usage_per_key"].items():
            status = "🔴 COOLDOWN" if key_stats["in_cooldown"] else "🟢 AVAILABLE"
            print(f"  {key_id}: {status}")
            print(f"    ├─ Used: {key_stats['usage_count']} times")
            print(f"    ├─ Failed: {key_stats['failure_count']} times")
            print(f"    └─ Last Used: {key_stats['last_used']}")
        
        print("="*50 + "\n")


# Global instance (singleton pattern)
_rotator_instance: Optional[APIKeyRotator] = None


def get_rotator() -> APIKeyRotator:
    """
    Get the global API key rotator instance (singleton)
    
    Returns:
        APIKeyRotator: The global rotator instance
    """
    global _rotator_instance
    
    if _rotator_instance is None:
        _rotator_instance = APIKeyRotator()
    
    return _rotator_instance


def get_api_key() -> str:
    """
    Convenience function to get next API key
    
    Returns:
        str: Next available API key
    """
    rotator = get_rotator()
    return rotator.get_next_key()


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing API Key Rotator...\n")
    
    rotator = get_rotator()
    
    # Simulate 15 requests
    print("📡 Simulating 15 API requests...\n")
    for i in range(15):
        try:
            key = rotator.get_next_key()
            print(f"Request {i+1}: Using key ending in ...{key[-6:]}")
            time.sleep(0.1)  # Simulate API call delay
        except RuntimeError as e:
            print(f"❌ {e}")
            break
    
    # Print statistics
    rotator.print_stats()
    
    # Test failure tracking
    print("\n🧪 Testing failure tracking...")
    test_key = rotator.keys[0]
    rotator.mark_failure(test_key, error_code=429)
    rotator.print_stats()
