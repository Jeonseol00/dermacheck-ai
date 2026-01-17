#!/bin/bash

# DermaCheck AI - Git Setup Script
# Run this to initialize git and push to GitHub

echo "🚀 DermaCheck AI - Git Setup"
echo "=============================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null
then
    echo "📦 Git not found. Installing..."
    sudo apt update && sudo apt install -y git
fi

# Navigate to project directory
cd /home/titiw/Downloads/hackathon/dermacheck-ai

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Configure git (optional - update with your info)
echo "⚙️ Configuring git..."
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
echo "📝 Staging files..."
git add .

# Commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: DermaCheck AI MVP - Med-Gemma Impact Challenge

- Complete ABCDE criteria analyzer
- Med-Gemma integration for medical interpretation
- Timeline tracking with progression alerts
- Premium Streamlit UI with custom CSS
- Full workflow: Analysis → Timeline → Education"

# Add remote (GitHub repo)
echo "🔗 Adding remote repository..."
git remote add origin https://github.com/Jeonseol00/dermacheck-ai.git 2>/dev/null || git remote set-url origin https://github.com/Jeonseol00/dermacheck-ai.git

# Rename branch to main
echo "🌿 Setting branch to main..."
git branch -M main

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Done! Your code is now on GitHub!"
echo "🔗 https://github.com/Jeonseol00/dermacheck-ai"
echo ""
echo "Next steps:"
echo "1. Create .env file with your GOOGLE_API_KEY"
echo "2. Run: python3 -m venv venv && source venv/bin/activate"
echo "3. Run: pip install -r requirements.txt"
echo "4. Run: streamlit run app/main.py"
