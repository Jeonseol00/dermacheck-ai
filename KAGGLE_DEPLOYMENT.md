# DermaCheck AI - Kaggle Deployment Notebook
**MedGemma Local Inference on T4 GPU**

This notebook runs DermaCheck AI Telegram bot using local MedGemma model (HAI-DEF compliant).

---

## Setup Instructions

### Prerequisites
1. **HuggingFace Access**:
   - Go to: https://huggingface.co/google/medgemma-4b-it
   - Click "Request Access"
   - Accept HAI-DEF terms
   - Get HF token from: https://huggingface.co/settings/tokens

2. **Kaggle Secrets** (Add-ons → Secrets):
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
   - `HF_TOKEN`: Your HuggingFace access token
   - `NGROK_TOKEN`: Your ngrok auth token (from ngrok.com)

3. **Kaggle Settings**:
   - **Accelerator**: GPU T4
   - **Internet**: ON
   - **Persistence**: OFF (stateless bot)

---

## Cell 1: Install Dependencies

```python
# Install required packages
!pip install -q python-telegram-bot transformers torch torchvision
!pip install -q bitsandbytes accelerate sentencepiece protobuf
!pip install -q pyngrok python-dotenv Pillow

print("✅ All dependencies installed!")
```

---

## Cell 2: Clone Repository

```python
import os

# Clone your GitHub repository
REPO_URL = "https://github.com/YOUR_USERNAME/dermacheck-ai.git"  # ← UPDATE THIS

!git clone {REPO_URL}
%cd dermacheck-ai

print(f"✅ Repository cloned: {os.getcwd()}")
!ls -la
```

---

## Cell 3: Setup Secrets & Environment

```python
from kaggle_secrets import UserSecretsClient
import os

# Initialize secrets client
user_secrets = UserSecretsClient()

# Load secrets
try:
    os.environ['TELEGRAM_BOT_TOKEN'] = user_secrets.get_secret("TELEGRAM_BOT_TOKEN")
    os.environ['HF_TOKEN'] = user_secrets.get_secret("HF_TOKEN")
    os.environ['NGROK_TOKEN'] = user_secrets.get_secret("NGROK_TOKEN")
    
    print("✅ All secrets loaded successfully!")
    print(f"📱 Telegram token: {os.environ['TELEGRAM_BOT_TOKEN'][:20]}...")
    print(f"🤗 HF token: {os.environ['HF_TOKEN'][:20]}...")
    
except Exception as e:
    print(f"❌ Failed to load secrets: {e}")
    print("Please add secrets in Kaggle: Add-ons → Secrets")
```

---

## Cell 4: Authenticate HuggingFace

```python
from huggingface_hub import login

# Login to HuggingFace to access MedGemma
HF_TOKEN = os.environ.get('HF_TOKEN')

if HF_TOKEN:
    login(token=HF_TOKEN)
    print("✅ HuggingFace authentication successful!")
else:
    print("❌ HF_TOKEN not found. Add it to Kaggle Secrets.")
```

---

## Cell 5: Verify GPU

```python
import torch

print("🔍 GPU Check:")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print("✅ GPU ready for MedGemma!")
else:
    print("⚠️  No GPU detected. Enable GPU in Kaggle settings: Accelerator → GPU T4")
```

---

## Cell 6: Test Model Loading (Optional but Recommended)

```python
# Quick test to ensure MedGemma can be loaded
print("🧪 Testing MedGemma model loading...")

from utils.model_loader import load_medgemma

try:
    model, processor = load_medgemma(model_name="google/medgemma-4b-it", quantize=True)
    print("✅ MedGemma loaded successfully!")
    print(f"📊 Model device: {model.device}")
    
    # Free memory for bot
    del model
    del processor
    torch.cuda.empty_cache()
    print("🗑️  Test model unloaded, memory cleared")
    
except Exception as e:
    print(f"❌ Model loading failed: {e}")
    print("Troubleshooting:")
    print("1. Check HF access was granted to MedGemma")
    print("2. Verify GPU is enabled (T4)")
    print("3. Ensure internet is ON")
```

---

## Cell 7: Setup ngrok for Telegram Webhook

```python
from pyngrok import ngrok
import time

# Set ngrok auth token
NGROK_TOKEN = os.environ.get('NGROK_TOKEN')
ngrok.set_auth_token(NGROK_TOKEN)

# Start ngrok tunnel
print("🌐 Starting ngrok tunnel...")
public_url = ngrok.connect(8080)
print(f"✅ ngrok tunnel active: {public_url}")

# Save for Telegram webhook
os.environ['PUBLIC_URL'] = str(public_url)

time.sleep(2)
print("ngrok status:", ngrok.get_tunnels())
```

---

## Cell 8: Run DermaCheck AI Bot!

```python
# Run the Telegram bot
print("🚀 Starting DermaCheck AI Bot...")
print("=" * 60)

# This will load MedGemma and start the bot
!python telegram_bot_medgemma.py

# Note: Bot will run continuously. Stop with Kernel → Interrupt.
```

---

## Cell 9: Monitor Logs (Optional - Run in separate output)

```python
# Tail logs in real-time
!tail -f bot.log
```

---

## Troubleshooting

### Model Loading Fails (400/403 Error)
**Solution**: Request access to MedGemma on HuggingFace (may take ~1 hour)

### Out of Memory Error
**Solution**: Ensure 4-bit quantization is enabled (`quantize=True`)

### Telegram Bot Not Responding
**Check**:
1. Bot token is correct (from @BotFather)
2. ngrok tunnel is active
3. Webhook set correctly
4. Check logs: `!tail bot.log`

### GPU Not Detected
**Solution**: Kaggle Settings → Accelerator → GPU T4 → Save

---

## Performance Expectations

| Metric | Value |
|--------|-------|
| Model load time | ~2-3 min (one-time) |
| Photo analysis | ~15-20s |
| Text consultation | ~8-10s |
| GPU memory usage | ~12-14GB |

---

## After Demo

```python
# Stop bot gracefully
# Kernel → Interrupt

# Cleanup (optional)
!pkill -f telegram_bot

# Check ngrok
ngrok.kill()
```

---

**Status**: Ready for deployment! 🎉  
**Compliance**: HAI-DEF (MedGemma) ✅  
**Cost**: $0 (Kaggle free tier) ✅
