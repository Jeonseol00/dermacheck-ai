# DermaCheck AI - Setup & Run Instructions

## Local Development Setup

### 1. Install Git (if not installed)
```bash
sudo apt update && sudo apt install -y git
```

### 2. Navigate to Project Directory
```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai
```

### 3. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: DermaCheck AI MVP"
```

### 4. Connect to GitHub Repository
```bash
git remote add origin https://github.com/Jeonseol00/dermacheck-ai.git
git branch -M main
git push -u origin main
```

### 5. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 6. Install Dependencies
```bash
pip install -r requirements.txt
```

### 7. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env file and add your Google API key
nano .env
```

**Required in .env:**
```
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 8. Run the Application
```bash
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

---

## For Kaggle Deployment

### 1. Create Kaggle Notebook

1. Go to https://www.kaggle.com/
2. Create new notebook
3. Enable GPU (T4) accelerator
4. Clone this repository or upload files

### 2. Install Dependencies in Kaggle
```python
!pip install streamlit pyngrok python-dotenv Pillow opencv-python scikit-learn google-generativeai
```

### 3. Setup Ngrok
```python
# Get ngrok token from: https://dashboard.ngrok.com/get-started/your-authtoken
!ngrok authtoken YOUR_NGROK_TOKEN

from pyngrok import ngrok
import os

# Set environment variables
os.environ['GOOGLE_API_KEY'] = 'your_google_api_key'

# Start ngrok tunnel
public_url = ngrok.connect(8501)
print(f"Public URL: {public_url}")
```

### 4. Run Streamlit
```python
!streamlit run app/main.py &
```

### 5. Access Your App
Open the ngrok public URL in your browser to access the app.

---

## Testing Checklist

- [ ] Upload test image
- [ ] Verify ABCDE analysis works
- [ ] Check risk scoring
- [ ] Test Med-Gemma interpretation (requires API key)
- [ ] Save to timeline
- [ ] Upload second image for same lesion
- [ ] View timeline comparison
- [ ] Check alerts for changes
- [ ] Navigate all pages (Analysis, Timeline, Education, About)

---

## Troubleshooting

### Error: "GOOGLE_API_KEY not configured"
**Solution:** Create `.env` file and add your API key

### Error: Module not found
**Solution:** Make sure you're in the virtual environment and run `pip install -r requirements.txt`

### Error: "Unable to load image"
**Solution:** Ensure image is JPEG or PNG format, less than 10MB

### Streamlit not opening
**Solution:** Check if port 8501 is available. Try: `streamlit run app/main.py --server.port 8502`

---

## Getting Google API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy and paste into `.env` file

---

## Project Structure

```
dermacheck-ai/
├── app/
│   └── main.py              # Main Streamlit application
├── models/
│   ├── abcde_analyzer.py    # ABCDE criteria analysis
│   └── medgemma_client.py   # Med-Gemma AI integration
├── utils/
│   ├── config.py            # Configuration management
│   ├── image_utils.py       # Image processing utilities
│   └── timeline_manager.py  # Timeline tracking system
├── assets/
│   └── css/
│       └── styles.css       # Custom styling
├── uploads/                 # User uploads (auto-created)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

---

## Next Steps for Hackathon

1. ✅ Test application locally
2. ✅ Get Google API key
3. ✅ Test Med-Gemma integration
4. ✅ Deploy to Kaggle
5. ✅ Record demo video (2-3 minutes)
6. ✅ Prepare submission materials
7. ✅ Submit to Google Med-Gemma Impact Challenge

---

**Good luck! 🚀**
