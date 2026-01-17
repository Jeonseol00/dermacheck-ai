# 🚀 Git Push ke GitHub - Step by Step Guide

## Persiapan: Dapatkan Personal Access Token (PAT)

### 1. Buat Personal Access Token di GitHub
1. Buka browser, login ke GitHub
2. Klik foto profile (kanan atas) → **Settings**
3. Scroll ke bawah → klik **Developer settings** (paling bawah sidebar kiri)
4. Klik **Personal access tokens** → **Tokens (classic)**
5. Klik **Generate new token** → **Generate new token (classic)**
6. Isi form:
   - **Note**: `DermaCheck AI - Hackathon`
   - **Expiration**: 90 days (atau sesuai kebutuhan)
   - **Select scopes**: ✅ **repo** (centang semua sub-items di bawahnya)
7. Scroll ke bawah → klik **Generate token**
8. **PENTING**: Copy token yang muncul (contoh: `ghp_xxxxxxxxxxxxxxxxxxxx`)
   - Simpan di notepad, token ini ga akan muncul lagi!

---

## Metode 1: Push dengan Personal Access Token (RECOMMENDED ✅)

### Step 1: Buka Terminal
```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai
```

### Step 2: Setup Credential Helper (biar token tersimpan)
```bash
git config credential.helper store
```

### Step 3: Push ke GitHub
```bash
git push -u origin main
```

### Step 4: Input Credentials
Nanti akan muncul prompt:
```
Username for 'https://github.com': 
```
**Ketik:** `Jeonseol00` → Enter

```
Password for 'https://Jeonseol00@github.com':
```
**Paste:** Token yang lu copy tadi (ghp_xxx...) → Enter
*(Password ga akan keliatan saat lu ketik, ini normal)*

### Step 5: Tunggu Upload Selesai
Kalau berhasil, akan muncul:
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
Delta compression using up to X threads
Compressing objects: 100% (X/X), done.
Writing objects: 100% (X/X), X KiB | X MiB/s, done.
Total X (delta X), reused 0 (delta 0), pack-reused 0
To https://github.com/Jeonseol00/dermacheck-ai.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

**SELESAI! ✅** Code udah di GitHub!

---

## Metode 2: Push dengan Token di URL (Alternative)

Kalau Metode 1 ribet, bisa pake cara ini (token langsung di URL):

### Step 1: Buka Terminal
```bash
cd /home/titiw/Downloads/hackathon/dermacheck-ai
```

### Step 2: Update Remote URL dengan Token
```bash
git remote set-url origin https://Jeonseol00:YOUR_TOKEN_HERE@github.com/Jeonseol00/dermacheck-ai.git
```

**Ganti `YOUR_TOKEN_HERE`** dengan token lu (ghp_xxx...)

Contoh:
```bash
git remote set-url origin https://Jeonseol00:ghp_abc123xyz456@github.com/Jeonseol00/dermacheck-ai.git
```

### Step 3: Push
```bash
git push -u origin main
```

Ga akan ada prompt username/password, langsung push! ✅

---

## Metode 3: Pakai GitHub CLI (Paling Gampang!)

Kalau mau yang super simple, install GitHub CLI:

### Step 1: Install GitHub CLI
```bash
# Install gh (GitHub CLI)
sudo apt update
sudo apt install gh -y
```

### Step 2: Login
```bash
gh auth login
```

Pilih:
- `GitHub.com`
- `HTTPS`
- `Login with a web browser` (paling gampang)

Follow instruksi di layar (copy kode, paste di browser).

### Step 3: Push
```bash
git push -u origin main
```

DONE! ✅

---

## Verifikasi Berhasil

Setelah push berhasil, cek di browser:

**Buka:** https://github.com/Jeonseol00/dermacheck-ai

Lu harusnya liat:
- ✅ 16 files
- ✅ `app/`, `models/`, `utils/`, `assets/` folders
- ✅ `README.md` dengan description
- ✅ Last commit: "Initial commit: DermaCheck AI MVP..."

---

## Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/Jeonseol00/dermacheck-ai.git
```

### Error: "Authentication failed"
- Cek token lu masih valid
- Pastikan scope `repo` udah di-check saat bikin token
- Generate token baru kalau perlu

### Error: "failed to push some refs"
Kemungkinan ada file di GitHub yang ga ada di local. Pull dulu:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Token hilang / lupa
Buat token baru di: https://github.com/settings/tokens

---

## Quick Commands Cheat Sheet

```bash
# Navigate to project
cd /home/titiw/Downloads/hackathon/dermacheck-ai

# Check status
git status

# Check remote
git remote -v

# Push to GitHub
git push -u origin main

# Pull from GitHub
git pull origin main

# View commit history
git log --oneline
```

---

## Next Steps Setelah Push Berhasil

1. ✅ Verify di GitHub: https://github.com/Jeonseol00/dermacheck-ai
2. ✅ Setup untuk run local (buat .env dengan GOOGLE_API_KEY)
3. ✅ Test aplikasi: `streamlit run app/main.py`
4. ✅ Deploy ke Kaggle untuk demo
5. ✅ Record demo video
6. ✅ Submit ke Google Med-Gemma Impact Challenge

---

**Good luck bro! 🔥**
