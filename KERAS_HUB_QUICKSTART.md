# ⚡ QUICK START - Keras Hub MedGemma

**Ready to test in Kaggle NOW!**

---

## 🎯 STEP-BY-STEP (30 minutes total)

### 1. Open Kaggle Notebook
- Go to kaggle.com/code
- New Notebook
- Enable GPU (T4)

### 2. Run Cells Sequentially

**Cell 1**: GPU check
```python
!nvidia-smi
```

**Cell 2**: Install
```python
!pip install -q keras-hub keras>=3.0 gradio pillow
```

**Cell 3**: HF Token
```python
import os
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
os.environ['HF_TOKEN'] = user_secrets.get_secret("HF_TOKEN")
print("✅ Token set")
```

**Cell 4**: Load Model (10-15 min)
```python
import keras_hub
medgemma = keras_hub.models.CausalLM.from_preset(
    "hf://google/medgemma-4b-it",
    dtype="bfloat16"
)
print("✅ Loaded!")
```

**Cell 5**: Test
```python
def format_prompt(msg):
    return f"<start_of_turn>user\n{msg}<end_of_turn>\n<start_of_turn>model"

prompt = format_prompt("Patient: fever, headache. Diagnosis:")
output = medgemma.generate(prompt, max_length=200)
print(output)
```

---

## ✅ SUCCESS IF:

- Cell 4: No errors, prints "✅ Loaded!"
- Cell 5: Output contains medical text (not empty)

---

## 📁 FILES READY

1. **`models/keras_hub_medgemma.py`** - Client class
2. **`KAGGLE_KERAS_HUB_GUIDE.md`** - Complete guide

---

## 🚀 GO NOW!

Open Kaggle, run Cells 1-5!

Report back hasil Cell 5! 💪
