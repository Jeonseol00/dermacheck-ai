#!/bin/bash
# Master script to download ALL datasets automatically
# Run this ONE command and get everything!

set -e  # Exit on error

echo "🚀 DermaCheck AI - Automated Dataset Downloader"
echo "================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found! Please install Python 3."
    exit 1
fi

# Check pip packages
echo "📦 Installing required packages..."
pip install -q kaggle requests pillow tqdm pandas

echo ""
echo "Step 1/3: Downloading Kaggle Datasets (HAM10000 + PAD-UFES-20)"
echo "----------------------------------------------------------------"
python3 scripts/download_kaggle_datasets.py

echo ""
echo "Step 2/3: Downloading ISIC Archive Images"
echo "----------------------------------------------------------------"
python3 scripts/download_isic_archive.py

echo ""
echo "Step 3/3: Curating Best Images (Selecting 50 cases)"
echo "----------------------------------------------------------------"
python3 scripts/curate_best_images.py

echo ""
echo "✅ ALL DONE! Dataset ready!"
echo "📁 Location: data/cases/"
echo "📊 Total cases: 50"
echo ""
echo "Next step: Run generate_ai_analysis.py to add MedGemma analysis!"
