#!/usr/bin/env python3
"""
Automated Image Curator
Selects best quality images from downloaded datasets
Organizes into final 50-case structure
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import json

class DatasetCurator:
    def __init__(self, raw_dir="data/raw", output_dir="data/cases"):
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Target conditions (10 categories, 5 each = 50)
        self.target_conditions = {
            "acne": 5,
            "eczema": 5,
            "psoriasis": 5,
            "melanoma": 5,
            "basal_cell_carcinoma": 5,
            "rosacea": 5,
            "vitiligo": 5,
            "seborrheic_dermatitis": 5,
            "folliculitis": 5,
            "contact_dermatitis": 5
        }
        
        self.cases = []
        
    def check_image_quality(self, img_path):
        """Check if image meets quality criteria"""
        try:
            img = Image.open(img_path)
            width, height = img.size
            
            # Criteria
            min_size = 600
            max_size = 5000
            
            if width < min_size or height < min_size:
                return False, "Too small"
            if width > max_size or height > max_size:
                return False, "Too large"
            if img.mode not in ['RGB', 'L']:
                return False, "Wrong color mode"
            
            return True, "OK"
        except Exception as e:
            return False, f"Error: {e}"
    
    def select_best_from_ham10000(self):
        """Select best images from HAM10000"""
        print("\n📂 Curating HAM10000 images...")
        ham_dir = self.raw_dir / "HAM10000_images_part_1"  # Capital letters!
        
        if not ham_dir.exists():
            # Try alternate path
            ham_dir = self.raw_dir
            metadata_file = ham_dir / "HAM10000_metadata.csv"
        else:
            metadata_file = self.raw_dir / "HAM10000_metadata.csv"
        
        if not metadata_file.exists():
            print("   ⚠️ HAM10000 metadata not found, skipping")
            return
        
        import pandas as pd
        df = pd.read_csv(metadata_file)
        
        # Map HAM codes to our conditions
        mapping = {
            'mel': 'melanoma',
            'bcc': 'basal_cell_carcinoma',
            'akiec': 'actinic_keratosis',
            'nv': 'nevus',
            'bkl': 'seborrheic_keratosis',
            'df': 'dermatofibroma',
            'vasc': 'vascular_lesion'
        }
        
        for ham_code, condition in mapping.items():
            subset = df[df['dx'] == ham_code].head(5)
            for idx, row in subset.iterrows():
                image_id = row['image_id']
                # Find image file in both parts
                img_files = list(self.raw_dir.glob(f"**/{image_id}.jpg"))
                if img_files:
                    self.copy_and_rename(img_files[0], condition, len(self.cases) + 1)
        
        print(f"   ✅ Selected {len(self.cases)} images from HAM10000")
    
    def select_best_from_isic(self):
        """Select images from ISIC downloads"""
        print("\n📂 Curating ISIC images...")
        isic_dir = self.raw_dir / "isic"
        
        if not isic_dir.exists():
            print("   ⚠️ ISIC not found, skipping")
            return
        
        count_before = len(self.cases)
        
        for condition_dir in isic_dir.iterdir():
            if condition_dir.is_dir():
                condition = condition_dir.name
                images = sorted(condition_dir.glob("*.jpg"))[:5]
                
                for img in images:
                    quality_ok, msg = self.check_image_quality(img)
                    if quality_ok:
                        self.copy_and_rename(img, condition, len(self.cases) + 1)
        
        print(f"   ✅ Selected {len(self.cases) - count_before} images from ISIC")
    
    def copy_and_rename(self, source, condition, case_id):
        """Copy image to final location with standard naming"""
        # Create condition folder
        condition_dir = self.output_dir / condition
        condition_dir.mkdir(exist_ok=True)
        
        # Standard naming
        dest = condition_dir / f"{condition}_{case_id:03d}.jpg"
        
        # Copy and resize if needed
        img = Image.open(source)
        
        # Resize if too large (save space)
        max_dim = 1024
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save
        img.save(dest, quality=90)
        
        # Track
        self.cases.append({
            "case_id": f"{case_id:03d}",
            "condition": condition,
            "image_path": str(dest.relative_to(self.output_dir.parent)),
            "source": source.parent.name
        })
        
        print(f"   ✅ {condition}: {dest.name}")
    
    def generate_metadata(self):
        """Generate metadata JSON"""
        metadata_file = self.output_dir.parent / "cases_database.json"
        
        with open(metadata_file, 'w') as f:
            json.dump(self.cases, f, indent=2)
        
        print(f"\n✅ Metadata saved: {metadata_file}")
        print(f"   Total cases: {len(self.cases)}")
    
    def run(self):
        """Run full curation process"""
        print("🎨 Starting dataset curation...")
        
        self.select_best_from_ham10000()
        self.select_best_from_isic()
        
        self.generate_metadata()
        
        print(f"\n✅ Curation complete!")
        print(f"📁 Cases: {self.output_dir}")
        print(f"📊 Total: {len(self.cases)} cases")

if __name__ == "__main__":
    curator = DatasetCurator()
    curator.run()
