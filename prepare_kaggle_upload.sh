#!/bin/bash

# DermaCheck AI - Kaggle Deployment Preparation Script
# Usage: bash prepare_kaggle_upload.sh

echo "🚀 DermaCheck AI - Kaggle Deployment Prep"
echo "=========================================="

# Check if in correct directory
if [ ! -f "app/gradio_app.py" ]; then
    echo "❌ Error: Tidak di folder dermacheck-ai!"
    echo "   Jalankan script ini dari /home/titiw/Downloads/hackathon/dermacheck-ai"
    exit 1
fi

# Create deployment folder
echo ""
echo "📦 Step 1: Creating deployment folder..."
mkdir -p kaggle_deploy
rm -rf kaggle_deploy/*  # Clean previous

# Copy essential files
echo "📋 Step 2: Copying files..."

# App files
echo "   - App components..."
cp -r app kaggle_deploy/

# Models
echo "   - Models..."
cp -r models kaggle_deploy/

# Utils (if exists)
if [ -d "utils" ]; then
    echo "   - Utils..."
    cp -r utils kaggle_deploy/
fi

# Data (cases only, not raw datasets)
echo "   - Dataset (35 cases)..."
mkdir -p kaggle_deploy/data
if [ -d "data/cases" ]; then
    cp -r data/cases kaggle_deploy/data/
fi
if [ -f "data/cases_database.json" ]; then
    cp data/cases_database.json kaggle_deploy/data/
fi

# Requirements
if [ -f "requirements.txt" ]; then
    echo "   - Requirements..."
    cp requirements.txt kaggle_deploy/
fi

# README for Kaggle
echo "   - Creating README..."
cat > kaggle_deploy/README.md << 'EOF'
# DermaCheck AI - Kaggle Deployment

## Quick Start

```python
# Cell 1: Extract and setup
import os, zipfile
os.chdir('/kaggle/working')
!mkdir -p dermacheck-ai

# Extract files (adjust path to your uploaded dataset)
with zipfile.ZipFile('/kaggle/input/YOUR_DATASET/dermacheck_ai.zip', 'r') as z:
    z.extractall('dermacheck-ai')

os.chdir('dermacheck-ai')

# Cell 2: Install
!pip install -q gradio transformers torch accelerate bitsandbytes pillow reportlab pandas

# Cell 3: Launch
import sys
sys.path.insert(0, '/kaggle/working/dermacheck-ai')
from app.gradio_app import demo
demo.launch(share=True)
```

## Features
- 🔬 Dermatology Analysis with MedGemma
- 📄 PDF Report Generator
- 📚 Interactive Atlas (35 cases)
- 🔄 Side-by-Side Comparison
- 🎨 Premium UI with Glassmorphism

**Requirements**: Kaggle GPU T4
EOF

# Check sizes
echo ""
echo "📊 Step 3: Checking sizes..."
TOTAL_SIZE=$(du -sh kaggle_deploy | cut -f1)
echo "   Total size: $TOTAL_SIZE"

# Count files
FILE_COUNT=$(find kaggle_deploy -type f | wc -l)
echo "   Files: $FILE_COUNT"

# Create ZIP
echo ""
echo "🗜️  Step 4: Creating ZIP archive..."
cd kaggle_deploy
zip -r ../dermacheck_ai.zip . -q

cd ..
ZIP_SIZE=$(du -sh dermacheck_ai.zip | cut -f1)

echo ""
echo "✅ PREPARATION COMPLETE!"
echo "=========================================="
echo ""
echo "📦 Archive created: dermacheck_ai.zip"
echo "   Size: $ZIP_SIZE"
echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "1. Go to: https://www.kaggle.com"
echo "2. Create New Notebook"
echo "3. Settings → GPU T4 x2 → Internet ON"
echo "4. Add Data → Upload → dermacheck_ai.zip"
echo "5. Follow guide in: kaggle_deployment_final.md"
echo ""
echo "📍 Archive location:"
echo "   $(pwd)/dermacheck_ai.zip"
echo ""
echo "🚀 Ready to upload! Good luck!"
