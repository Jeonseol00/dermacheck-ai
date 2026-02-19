#!/usr/bin/env python3
"""
ISIC Archive Automated Downloader
Downloads curated dermatology images from ISIC Archive
Uses their public API - NO manual download needed!
"""

import requests
import json
from pathlib import Path
from tqdm import tqdm
import time

class ISICDownloader:
    def __init__(self, output_dir="data/raw/isic"):
        self.base_url = "https://isic-archive.com/api/v2"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def search_images(self, diagnosis, limit=5):
        """Search for images by diagnosis"""
        endpoint = f"{self.base_url}/images"
        params = {
            "limit": limit,
            "diagnosis": diagnosis
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"❌ Error searching for {diagnosis}: {e}")
            return []
    
    def download_image(self, image_id, diagnosis, index):
        """Download single image"""
        image_url = f"{self.base_url}/images/{image_id}/thumbnail/full"
        save_path = self.output_dir / diagnosis.lower().replace(" ", "_") / f"{diagnosis.lower()}_{index:03d}.jpg"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            response = requests.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"   ❌ Failed to download {image_id}: {e}")
            return False
    
    def download_condition_set(self, diagnosis, count=5):
        """Download a set of images for one condition"""
        print(f"\n📥 Downloading {count} images for: {diagnosis}")
        
        # Search
        results = self.search_images(diagnosis, limit=count)
        if not results:
            print(f"   ⚠️ No images found for {diagnosis}")
            return 0
        
        # Download
        downloaded = 0
        for i, result in enumerate(results[:count], 1):
            image_id = result.get("_id")
            if image_id:
                print(f"   [{i}/{count}] Downloading {image_id}...", end=" ")
                if self.download_image(image_id, diagnosis, i):
                    print("✅")
                    downloaded += 1
                else:
                    print("❌")
                time.sleep(0.5)  # Rate limiting
        
        print(f"   ✅ Downloaded {downloaded}/{count} images")
        return downloaded
    
    def download_all_conditions(self):
        """Download images for all target conditions"""
        conditions = [
            ("Melanoma", 5),
            ("Basal cell carcinoma", 5),
            ("Actinic keratosis", 5),
            ("Squamous cell carcinoma", 3),
            ("Nevus", 5),
            ("Seborrheic keratosis", 5),
            ("Dermatofibroma", 3)
        ]
        
        print("🚀 Starting ISIC Archive download...")
        print(f"📁 Output: {self.output_dir.absolute()}")
        
        total_downloaded = 0
        for diagnosis, count in conditions:
            downloaded = self.download_condition_set(diagnosis, count)
            total_downloaded += downloaded
        
        print(f"\n✅ Total downloaded: {total_downloaded} images")
        print(f"📂 Location: {self.output_dir.absolute()}")
        
        return total_downloaded

if __name__ == "__main__":
    downloader = ISICDownloader()
    downloader.download_all_conditions()
