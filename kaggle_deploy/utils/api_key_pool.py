"""
API Key Pool Manager with Round-Robin Rotation
Automatically rotates through multiple API keys to avoid quota limits
"""

import os
from typing import List, Optional
import threading


class APIKeyPool:
    """
    Manages multiple API keys with round-robin rotation
    Thread-safe implementation
    """
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize with list of API keys
        
        Args:
            api_keys: List of valid Google API keys
        """
        if not api_keys:
            raise ValueError("API key pool cannot be empty")
        
        self.api_keys = api_keys
        self.current_index = 0
        self.lock = threading.Lock()
        
        print(f"✅ API Key Pool initialized with {len(api_keys)} keys")
    
    def get_next_key(self) -> str:
        """
        Get next API key in round-robin fashion
        Thread-safe
        
        Returns:
            Next API key from the pool
        """
        with self.lock:
            key = self.api_keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            return key
    
    def get_current_key(self) -> str:
        """Get current key without rotation"""
        with self.lock:
            return self.api_keys[self.current_index]
    
    @classmethod
    def from_env(cls, env_var: str = "GOOGLE_API_KEYS") -> "APIKeyPool":
        """
        Create pool from environment variable
        
        Args:
            env_var: Environment variable name containing comma-separated keys
            
        Returns:
            APIKeyPool instance
        """
        keys_str = os.getenv(env_var, "")
        if not keys_str:
            # Fallback to single key
            single_key = os.getenv("GOOGLE_API_KEY", "")
            if not single_key:
                raise ValueError(f"No API keys found in {env_var} or GOOGLE_API_KEY")
            keys = [single_key]
        else:
            keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        
        return cls(keys)


# Global pool instance
_global_pool: Optional[APIKeyPool] = None


def initialize_key_pool(api_keys: List[str]) -> APIKeyPool:
    """Initialize global API key pool"""
    global _global_pool
    _global_pool = APIKeyPool(api_keys)
    return _global_pool


def get_api_key_pool() -> APIKeyPool:
    """Get global API key pool instance"""
    global _global_pool
    if _global_pool is None:
        # Try to initialize from env
        _global_pool = APIKeyPool.from_env()
    return _global_pool


def get_next_api_key() -> str:
    """Convenience function to get next API key"""
    return get_api_key_pool().get_next_key()
