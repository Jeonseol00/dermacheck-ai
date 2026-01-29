#!/bin/bash
# DermaCheck AI - Quick Setup Script
# MedGemma Impact Challenge 2026

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     DermaCheck AI - Quick Setup                           ║"
echo "║     Installing dependencies for MedGemma Gradio App       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"
echo ""

# Check pip
echo "🔍 Checking pip..."
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Installing..."
    python3 -m ensurepip --upgrade
fi
echo "✅ pip is available"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing dependencies from requirements_gradio.txt..."
echo "   This may take 5-10 minutes..."
echo ""

if [ -f "requirements_gradio.txt" ]; then
    pip install -r requirements_gradio.txt
    echo ""
    echo "✅ All dependencies installed!"
else
    echo "⚠️  requirements_gradio.txt not found!"
    echo "Installing core packages manually..."
    
    pip install transformers==4.36.2
    pip install torch==2.1.0
    pip install gradio==4.16.0
    pip install bitsandbytes==0.41.3
    pip install accelerate==0.25.0
    pip install pillow
    
    echo "✅ Core packages installed!"
fi

echo ""
echo "=" * 60
echo "📊 Installation Summary"
echo "=" * 60

# Verify installations
echo ""
echo "Verifying key packages..."
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}')" || echo "❌ PyTorch failed"
python3 -c "import transformers; print(f'✅ Transformers {transformers.__version__}')" || echo "❌ Transformers failed"
python3 -c "import gradio; print(f'✅ Gradio {gradio.__version__}')" || echo "❌ Gradio failed"
python3 -c "import bitsandbytes; print(f'✅ BitsAndBytes OK')" || echo "❌ BitsAndBytes failed"

echo ""
echo "=" * 60
echo "🎉 Setup Complete!"
echo "=" * 60
echo ""
echo "Next steps:"
echo "1. Run environment test: python test_medgemma_setup.py"
echo "2. Set HF_TOKEN: export HF_TOKEN='your_huggingface_token'"
echo "3. Test MedGemma: python models/medgemma_multimodal_client.py"
echo "4. Launch Gradio: python app/gradio_app.py"
echo ""
echo "Need help? Check EXECUTION_SUMMARY.md in artifacts folder"
echo ""
