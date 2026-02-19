#!/usr/bin/env python3
"""
Automated Kaggle Dataset Downloader
Downloads HAM10000 and PAD-UFES-20 datasets automatically
"""

import os
import subprocess
import zipfile
from pathlib import Path

class KaggleDatasetDownloader:
    def __init__(self, base_dir="data/raw"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def check_kaggle_setup(self):
        """Check if Kaggle CLI is configured"""
        kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
        if not kaggle_json.exists():
            print("❌ Kaggle API token not found!")
            print("\n📝 Setup Instructions:")
            print("1. Go to: https://www.kaggle.com/account")
            print("2. Scroll to 'API' section")
            print("3. Click 'Create New Token'")
            print("4. Download kaggle.json")
            print("5. Run: mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/")
            print("6. Run: chmod 600 ~/.kaggle/kaggle.json")
            return False
        print("✅ Kaggle API configured!")
        return True
    
    def download_ham10000(self):
        """Download HAM10000 skin cancer dataset"""
        print("\n📦 Downloading HAM10000 dataset...")
        dataset_name = "kmader/skin-cancer-mnist-ham10000"
        output_dir = self.base_dir / "ham10000"
        
        try:
            # Download
            subprocess.run([
                os.path.expanduser("~/.local/bin/kaggle"), "datasets", "download",
                "-d", dataset_name,
                "-p", str(self.base_dir)
            ], check=True)
            
            # Extract
            zip_file = self.base_dir / "skin-cancer-mnist-ham10000.zip"
            if zip_file.exists():
                print("📂 Extracting HAM10000...")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                zip_file.unlink()  # Remove zip
                print(f"✅ HAM10000 extracted to: {output_dir}")
                
                # Count images
                images = list(output_dir.glob("**/*.jpg"))
                print(f"   Found {len(images)} images")
                return True
        except Exception as e:
            print(f"❌ Error downloading HAM10000: {e}")
            return False
    
    def download_pad_ufes(self):
        """Download PAD-UFES-20 dataset"""
        print("\n📦 Downloading PAD-UFES-20 dataset...")
        dataset_name = "mahdavi1202/skin-cancer"
        output_dir = self.base_dir / "pad_ufes"
        
        try:
            # Download
            subprocess.run([
                "kaggle", "datasets", "download",
                "-d", dataset_name,
                "-p", str(self.base_dir)
            ], check=True)
            
            # Extract
            zip_file = self.base_dir / "skin-cancer.zip"
            if zip_file.exists():
                print("📂 Extracting PAD-UFES-20...")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                zip_file.unlink()
                print(f"✅ PAD-UFES-20 extracted to: {output_dir}")
                
                # Count images
                images = list(output_dir.glob("**/*.png")) + list(output_dir.glob("**/*.jpg"))
                print(f"   Found {len(images)} images")
                return True
        except Exception as e:
            print(f"❌ Error downloading PAD-UFES-20: {e}")
            return False
    
    def download_all(self):
        """Download all Kaggle datasets"""
        print("🚀 Starting Kaggle dataset download...")
        
        if not self.check_kaggle_setup():
            return False
        
        success = True
        success &= self.download_ham10000()
        success &= self.download_pad_ufes()
        
        if success:
            print("\n✅ All Kaggle datasets downloaded successfully!")
            print(f"📁 Location: {self.base_dir.absolute()}")
        else:
            print("\n⚠️ Some downloads failed. Check errors above.")
        
        return success

if __name__ == "__main__":
    downloader = KaggleDatasetDownloader()
    downloader.download_all()
