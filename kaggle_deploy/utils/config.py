"""
Configuration management for DermaCheck AI
Loads environment variables and defines application constants
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")
    NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")
    
    # Model Configuration
    MEDGEMMA_MODEL = os.getenv("MEDGEMMA_MODEL", "medgemma-7b")
    VISION_MODEL = os.getenv("VISION_MODEL", "paligemma-3b")
    
    # Application Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    SUPPORTED_FORMATS = os.getenv("SUPPORTED_FORMATS", "jpg,jpeg,png").split(",")
    
    # Image Processing
    TARGET_IMAGE_SIZE = (512, 512)
    MIN_IMAGE_SIZE = (100, 100)
    
    # ABCDE Thresholds
    RISK_THRESHOLDS = {
        "low": (0, 2),
        "medium": (3, 5),
        "high": (6, 11)
    }
    
    # Timeline Settings
    ALERT_SIZE_CHANGE_THRESHOLD = 0.20  # 20% size increase
    ALERT_TIMEFRAME_DAYS = 30
    
    # Paths
    UPLOAD_DIR = "uploads"
    TEMP_DIR = "temp"
    ASSETS_DIR = "assets"
    
    @staticmethod
    def is_kaggle_environment():
        """Check if running in Kaggle environment"""
        return os.path.exists("/kaggle/working")
    
    @staticmethod
    def validate_config():
        """Validate critical configuration"""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set. Please configure .env file.")
        return True

# Create directories if they don't exist
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(Config.TEMP_DIR, exist_ok=True)
