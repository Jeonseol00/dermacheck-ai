# 🩺 DermaCheck AI

> AI-Powered Dermatology Screening Platform for Early Detection & Health Literacy
> 
> Built for **Google Med-Gemma Impact Challenge 2026**

---

## 🎯 What is DermaCheck AI?

DermaCheck AI is an intelligent skin health screening platform that combines computer vision and medical AI to help users:

- 📸 **Visual Analysis** - Upload photos of skin lesions/moles for automated assessment
- 🔍 **ABCDE Screening** - Systematic melanoma risk evaluation using clinical criteria
- 📊 **Progression Tracking** - Monitor changes over time with photo timeline comparison
- 🚨 **Smart Triage** - Get actionable recommendations on when to seek professional care
- 📚 **Health Education** - Learn about skin conditions with Med-Gemma powered explanations

**Not a replacement for medical diagnosis** - DermaCheck provides preliminary screening tools to help you make informed decisions about seeking professional care.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│  Frontend: Streamlit Web App                        │
│  └─ Image Upload + Timeline Viewer + Results UI    │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Vision Analysis Engine                             │
│  └─ PaliGemma / SigLIP (Feature Extraction)        │
└─────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│  Medical Reasoning: Med-Gemma 2B/7B                 │
│  └─ ABCDE Analysis + Risk Scoring + Triage         │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd dermacheck-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app/main.py
```

### Kaggle Deployment

1. Upload project to Kaggle Notebook
2. Enable GPU (T4) runtime
3. Install dependencies and run with pyngrok for tunneling
4. Access via generated public URL

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Custom CSS
- **Vision AI**: PaliGemma / SigLIP (Google)
- **Medical AI**: Med-Gemma 2B/7B
- **Image Processing**: OpenCV, Pillow
- **Deployment**: Kaggle Notebooks + pyngrok
- **Version Control**: Git + GitHub

---

## 📋 Features

### MVP (Phase 1)
- [x] Image upload interface
- [x] ABCDE criteria analysis
- [x] Risk scoring system
- [x] Basic triage recommendations
- [x] Med-Gemma integration

### Enhanced (Phase 2)
- [ ] Temporal comparison (before/after)
- [ ] Body mapping (multiple lesion tracking)
- [ ] Condition library with visual reference
- [ ] Export reports (PDF)

---

## ⚠️ Medical Disclaimer

**DermaCheck AI is a screening tool, not a diagnostic device.**

- Results are preliminary and educational only
- Always consult qualified healthcare professionals for medical advice
- Do not use as sole basis for medical decisions
- Urgent symptoms require immediate medical attention

---

## 👥 Team

Built by passionate developers for the Google Med-Gemma Impact Challenge.

- **Lead Developer**: [Your Name]
- **Collaborator**: Antigravity AI Assistant

---

## 📄 License

[To be determined - likely MIT or Apache 2.0]

---

## 🙏 Acknowledgments

- Google Med-Gemma Team for the powerful medical AI model
- Kaggle for GPU resources and platform
- Medical community for ABCDE criteria and dermatology datasets

---

**Last Updated**: January 2026
