# ⚡ QUICK FIX - MedGemma Kaggle

**Problem**: CUDA errors, NaN in generation  
**Solution**: Downgrade transformers to 4.38.2

---

## 🔄 RESTART KERNEL FIRST!

Kaggle: **Kernel → Restart Kernel**

---

## 📋 COPY-PASTE CELLS

### Cell 1: GPU Check
```python
!nvidia-smi
```

### Cell 2: Install RIGHT Versions
```python
!pip uninstall -y transformers
!pip install -q transformers==4.38.2
!pip install -q gradio pillow sentencepiece
print("✅ Done! Continue to Cell 3")
```

### Cell 3: Verify
```python
import torch, transformers
print(f"Transformers: {transformers.__version__}")  # Must be 4.38.2
print(f"CUDA: {torch.cuda.is_available()}")
```

### Cell 4: HF Token
```python
import os
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
os.environ['HF_TOKEN'] = user_secrets.get_secret("HF_TOKEN")
print("✅ Token set")
```

### Cell 5: Load MedGemma
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained(
    "google/medgemma-4b-it",
    token=os.environ['HF_TOKEN'],
    trust_remote_code=True
)

model = AutoModelForCausalLM.from_pretrained(
    "google/medgemma-4b-it",
    torch_dtype=torch.float16,
    token=os.environ['HF_TOKEN'],
    trust_remote_code=True,
    low_cpu_mem_usage=True
)

device = torch.device("cuda")
model = model.to(device)
model.eval()

print(f"✅ Loaded! Memory: {torch.cuda.memory_allocated()/1e9:.2f} GB")
```

### Cell 6: TEST
```python
prompt = "Patient: fever 39°C, headache, neck stiffness. Diagnosis:"
inputs = tokenizer(prompt, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model.generate(
        inputs['input_ids'],
        max_new_tokens=150,
        do_sample=True,
        temperature=0.6,
        top_p=0.85,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
    )

result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(result)
```

---

## ✅ SUCCESS IF:

- No CUDA errors
- Output is medical text (not padding)
- Memory < 12GB

---

## 🐛 IF STILL FAILS:

Try greedy:
```python
outputs = model.generate(
    inputs['input_ids'],
    max_new_tokens=100,
    do_sample=False  # No sampling
)
```

---

**GO! 🔥**
