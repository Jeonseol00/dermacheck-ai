# 🏥 DermaCheck AI

> **AI-Powered Dermatological Analysis** — Built with Google MedGemma 1.5  
> 🏆 Submission for [MedGemma Impact Challenge](https://www.kaggle.com/competitions/med-gemma-impact-challenge) on Kaggle

[![MedGemma](https://img.shields.io/badge/Model-MedGemma%201.5-blue)](https://ai.google.dev/gemma/docs/medgemma)
[![Kaggle](https://img.shields.io/badge/Platform-Kaggle%20GPU%20T4-orange)](https://www.kaggle.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📖 Overview

DermaCheck AI is a comprehensive dermatological analysis platform that leverages **Google's MedGemma 1.5 multimodal model** to provide instant, clinical-grade skin lesion assessments. Designed for patients and healthcare providers in underserved regions, it combines advanced AI with accessible interfaces (web app & Telegram bot).

### 🎯 Problem Statement

In Indonesia, the ratio of dermatologists to population is approximately **1:200,000** — leaving millions without access to specialized skin care. DermaCheck AI bridges this gap by providing:

- **Instant AI-powered skin analysis** from a simple photo
- **ABCDE melanoma scoring** (Asymmetry, Border, Color, Diameter, Evolution)
- **Clinical-grade risk assessment** with confidence intervals
- **Treatment tracking** — monitor lesion changes over time
- **Accessible deployment** via Telegram bot (no app download needed)

---

## 🏗 Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Patient/User  │────▶│   Frontend (Next.js)  │────▶│  Kaggle Backend │
│                 │     │   localhost:3000       │     │  (FastAPI + GPU)│
│   Telegram Bot  │────▶│   telegram_bot.py     │────▶│  MedGemma 1.5   │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
                                                            │
                                                     ┌──────┴──────┐
                                                     │ AI Pipeline │
                                                     ├─────────────┤
                                                     │ Image Proc  │
                                                     │ ABCDE Score  │
                                                     │ Risk Tier    │
                                                     │ Clinical Dx  │
                                                     │ Follow-up    │
                                                     └─────────────┘
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔬 **Multimodal Analysis** | MedGemma 1.5 analyzes skin images with clinical context |
| 📊 **ABCDE Scoring** | Automated melanoma risk scoring (0-10 scale) |
| 📈 **Progress Tracking** | Save baseline → upload follow-up → see improvement % |
| 🔒 **Confidence Intervals** | 95% CI for diagnosis confidence, not just point estimates |
| 📋 **PDF Reports** | Generate clinical-grade PDF reports for doctors |
| 💬 **Text Consultation** | Chat with MedGemma for medical Q&A |
| 🔎 **Multi-Lesion Detection** | Analyze multiple lesions in one image |
| 📱 **Telegram Bot** | Full analysis via Telegram — no app download needed |
| 🌏 **Bilingual** | Indonesian & English clinical output |
| 🧬 **Differential Diagnosis** | Top 3 differentials with rationale |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | Google MedGemma 1.5-4b-it (multimodal) |
| **Backend** | Python, FastAPI, running on Kaggle GPU T4 |
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS |
| **Bot** | python-telegram-bot (Telegram API) |
| **Deployment** | Kaggle Notebooks (GPU), Vercel-ready frontend |

---

## 🚀 Quick Start

### Backend (Kaggle Notebook)

1. Open [Kaggle Notebook](https://www.kaggle.com) and create a new notebook
2. Enable **GPU T4 x2** accelerator
3. Copy contents of `CELL4_V10.0_MEDICAL_GRADE.py` into a cell
4. Add `KAGGLE_TOKEN` to Kaggle Secrets
5. Run the cell — FastAPI server starts with ngrok tunnel

### Frontend (Local)

```bash
cd dermacheck-frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Telegram Bot

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your-token"
export KAGGLE_API_BASE="your-ngrok-url"

# Run
python3 telegram_bot.py
```

---

## 📁 Project Structure

```
dermacheck-ai/
├── CELL4_V10.0_MEDICAL_GRADE.py   # 🧠 Main Kaggle backend (MedGemma + FastAPI)
├── telegram_bot.py                 # 🤖 Telegram bot with full analysis pipeline
├── models/                         # AI model clients & analyzers
│   ├── medgemma_multimodal_client.py
│   ├── keras_medgemma_client.py
│   └── abcde_analyzer.py
├── app/                            # Web app components
│   ├── components/                 # PDF generator, comparison engine, etc.
│   └── dermacheck_v10_renderer.js
├── prompts/                        # Clinical prompt templates
├── utils/                          # Image processing, API utilities
├── validation/                     # Test cases & validation suite
├── kaggle_deploy/                  # Kaggle deployment scripts
├── docs/                           # System Design Document (SDD)
└── requirements.txt
```

---

## 🔬 Clinical Capabilities

### ABCDE Melanoma Scoring
Each lesion is evaluated on the dermoscopic ABCDE criteria:
- **A**symmetry — Is the lesion symmetric?
- **B**order — Are borders well-defined?
- **C**olor — Is color distribution uniform?
- **D**iameter — Is diameter > 6mm?
- **E**volution — Has the lesion changed over time?

### Risk Stratification
| Risk Tier | ABCDE Score | Action |
|-----------|-------------|--------|
| 🟢 LOW | 0-3 | Routine monitoring |
| 🟡 MEDIUM | 4-6 | Schedule dermatology consult |
| 🔴 HIGH | 7-10 | Urgent referral recommended |

---

## ⚠️ Disclaimer

> **DermaCheck AI is a screening tool, NOT a diagnostic device.** All results should be confirmed by a qualified healthcare professional. This tool is designed to assist clinical decision-making, not replace it.

---

## 👨‍💻 Author

**Muhamad Fikri**

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- **Google Health AI** — MedGemma model & HAI-DEF framework
- **Kaggle** — GPU infrastructure & competition platform
- **HAM10000 Dataset** — Dermatoscopic image training data
