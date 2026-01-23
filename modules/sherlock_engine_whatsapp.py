"""
DermaCheck AI - Sherlock Engine for WhatsApp Bot
Kaggle-optimized version with Gemini Vision API
"""
import os
import requests
from io import BytesIO

try:
    from PIL import Image
    import numpy as np
except ImportError:
    os.system('pip install pillow numpy -q')
    from PIL import Image
    import numpy as np

try:
    import google.generativeai as genai
except ImportError:
    os.system('pip install google-generativeai -q')
    import google.generativeai as genai


class SherlockEngine:
    """
    DermaCheck AI Engine for skin lesion analysis
    Integrated with WhatsApp bot via Fonnte
    """
    
    def __init__(self):
        """Initialize AI engine with Gemini API"""
        # Get API key from environment
        self.api_key = os.getenv('GOOGLE_API_KEY', 'AIzaSyAcG511Kx_rk5EqCon9HsAgvXVvXYm8yS8')
        
        # Configure Gemini
        try:
            genai.configure(api_key=self.api_key)
            
            # Try models in order of preference (2026 latest models)
            model_names = [
                'gemini-2.0-flash-exp',           # Latest experimental (Jan 2026)
                'gemini-1.5-flash-002',           # Stable 1.5 Flash
                'gemini-1.5-flash-latest',        # Latest 1.5 Flash
                'gemini-1.5-flash',               # Standard 1.5 Flash
                'gemini-pro-vision',              # Fallback vision model
            ]
            
            self.model = None
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"✅ Gemini AI configured: {model_name}")
                    break
                except Exception as e:
                    print(f"⚠️ {model_name} not available: {e}")
                    continue
            
            if not self.model:
                raise Exception("No Gemini model available")
                
        except Exception as e:
            print(f"❌ Gemini config error: {e}")
            self.model = None
    
    
    def process_message(self, sender, message, image_url=None):
        """
        Main processing function for WhatsApp messages
        
        Args:
            sender: Phone number of sender
            message: Text message
            image_url: URL of image (if any)
            
        Returns:
            str: Reply message
        """
        message_lower = message.lower().strip()
        
        # Handle text commands
        if message_lower in ['hi', 'halo', 'hello', 'help', 'start', 'mulai']:
            return self._welcome_message()
        
        elif message_lower in ['tips', 'panduan', 'cara']:
            return self._photo_tips()
        
        # Handle image analysis
        elif image_url:
            return self._analyze_image(image_url, sender)
        
        # Default help
        else:
            return self._help_message()
    
    
    def _analyze_image(self, image_url, sender):
        """
        Analyze skin lesion image using Gemini AI
        
        Args:
            image_url: URL of the image
            sender: Sender phone number
            
        Returns:
            str: Analysis result formatted for WhatsApp
        """
        try:
            print(f"📥 Downloading image from: {image_url}")
            
            # Download image
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                return "⚠️ Gagal download gambar. Silakan kirim ulang."
            
            # Open image
            image = Image.open(BytesIO(response.content))
            print(f"✅ Image loaded: {image.size}")
            
            # Check if image is blank/empty
            if self._is_blank_image(image):
                return self._blank_rejection_message()
            
            # Analyze with Gemini
            if not self.model:
                return "⚠️ AI service sedang maintenance. Coba lagi nanti."
            
            # Create prompt for analysis
            prompt = """
Analyze this skin lesion image using ABCDE criteria for melanoma detection:

A - Asymmetry (0-2 points)
B - Border irregularity (0-2 points)
C - Color variation (0-2 points)
D - Diameter >6mm (0-2 points)
E - Evolution/changes (0-3 points)

Provide scores and recommendations in Indonesian language.

Format your response as:
ASYMMETRY: [score]/2
BORDER: [score]/2
COLOR: [score]/2
DIAMETER: [score]/2
EVOLUTION: [score]/3
TOTAL: [total]/11
RISK: [LOW/MEDIUM/HIGH]
RECOMMENDATION: [advice in Indonesian]
"""
            
            print("🤖 Sending to Gemini AI...")
            
            # Generate analysis
            response = self.model.generate_content([prompt, image])
            analysis_text = response.text
            
            print("✅ Analysis complete!")
            
            # Parse and format response
            return self._format_analysis_reply(analysis_text)
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return f"""
⚠️ Maaf, terjadi error saat analisis.

Silakan coba lagi dengan foto yang lebih jelas!

Tips:
• Cahaya terang
• Fokus jelas
• Jarak 10-15cm

Error: {str(e)[:100]}
"""
    
    
    def _is_blank_image(self, image):
        """Check if image is blank/empty"""
        try:
            # Convert to grayscale
            gray = image.convert('L')
            # Calculate variance
            img_array = np.array(gray)
            variance = np.var(img_array)
            
            print(f"📊 Image variance: {variance:.2f}")
            
            # If variance too low, image is blank
            return variance < 500
            
        except:
            return False
    
    
    def _format_analysis_reply(self, analysis_text):
        """
        Format Gemini analysis into WhatsApp message
        
        Args:
            analysis_text: Raw analysis from Gemini
            
        Returns:
            str: Formatted WhatsApp message
        """
        try:
            # Parse response (simple extraction)
            lines = analysis_text.upper().split('\n')
            
            # Extract scores
            asymmetry = 1
            border = 1
            color = 1
            diameter = 1
            evolution = 2
            
            for line in lines:
                if 'ASYMMETRY' in line or 'ASIMETRI' in line:
                    try:
                        asymmetry = int(line.split('/')[0].split(':')[-1].strip())
                    except:
                        pass
                elif 'BORDER' in line or 'BATAS' in line:
                    try:
                        border = int(line.split('/')[0].split(':')[-1].strip())
                    except:
                        pass
                elif 'COLOR' in line or 'WARNA' in line:
                    try:
                        color = int(line.split('/')[0].split(':')[-1].strip())
                    except:
                        pass
                elif 'DIAMETER' in line:
                    try:
                        diameter = int(line.split('/')[0].split(':')[-1].strip())
                    except:
                        pass
                elif 'EVOLUTION' in line or 'EVOLUSI' in line:
                    try:
                        evolution = int(line.split('/')[0].split(':')[-1].strip())
                    except:
                        pass
            
            # Calculate total
            total = asymmetry + border + color + diameter + evolution
            
            # Determine risk level
            if total <= 3:
                risk = 'LOW'
                risk_emoji = '🟢'
            elif total <= 6:
                risk = 'MEDIUM'
                risk_emoji = '🟡'
            else:
                risk = 'HIGH'
                risk_emoji = '🔴'
            
            # Format message
            msg = f"""
╔══════════════════╗
  HASIL ANALISIS  
╚══════════════════╝

{risk_emoji} *TINGKAT RISIKO: {risk}*
Skor: {total}/11

━━━━━━━━━━━━━━━━━━

📊 *DETAIL ABCDE:*

• Asymmetry: {asymmetry}/2
• Border: {border}/2
• Color: {color}/2
• Diameter: {diameter}/2
• Evolution: {evolution}/3

━━━━━━━━━━━━━━━━━━
"""
            
            # Add recommendation
            if risk == 'HIGH':
                msg += """
🚨 *PENTING!*

Segera konsultasi ke dokter kulit dalam 1-2 minggu!

Jangan tunda. Bawa hasil ini saat ke dokter.
"""
            elif risk == 'MEDIUM':
                msg += """
⚠️ *PERHATIAN*

Sebaiknya periksa ke dokter dalam 1 bulan.

Pantau terus. Kalau ada perubahan, segera ke dokter.
"""
            else:
                msg += """
✅ *AMAN*

Kemungkinan tidak berbahaya.

Tetap pantau. Kalau berubah, foto lagi ya!
"""
            
            msg += """
━━━━━━━━━━━━━━━━━━

💬 Kirim "TIPS" untuk panduan foto
📸 Kirim foto lagi untuk analisis baru

⚠️ *Disclaimer:*
Ini BUKAN diagnosa medis.
Selalu konsultasi dokter untuk kepastian.

━━━━━━━━━━━━━━━━━━
DermaCheck AI v3.0
Powered by Gemini AI
"""
            
            return msg.strip()
            
        except Exception as e:
            print(f"Format error: {e}")
            return "✅ Analisis selesai! Silakan konsultasi dokter untuk pemeriksaan lebih lanjut."
    
    
    def _blank_rejection_message(self):
        """Message when image is too blank"""
        return """
⚠️ *FOTO KURANG JELAS*

Foto yang Anda kirim terlalu kosong/polos.

📸 *TIPS FOTO YANG BAIK:*

1️⃣ Fokus pada lesi/tahi lalat
2️⃣ Jarak 10-15 cm
3️⃣ Cahaya cukup (tidak gelap)
4️⃣ Lesi terlihat jelas
5️⃣ Tidak blur/goyang

Silakan kirim foto ulang yang lebih jelas ya! 👍

Ketik "TIPS" untuk panduan lengkap.
"""
    
    
    def _welcome_message(self):
        """Welcome message"""
        return """
🏥 *Selamat Datang di DermaCheck AI!*

Saya adalah asisten AI untuk analisis awal kondisi kulit Anda.

📸 *CARA PAKAI:*

1. Foto tahi lalat/lesi Anda
2. Kirim foto ke chat ini
3. Tunggu hasil (15-30 detik)
4. Baca saran yang diberikan

⚠️ *PENTING:*

• Ini BUKAN diagnosa medis
• Selalu konsultasi dokter
• Hasil hanya referensi awal

💬 Ketik "TIPS" untuk panduan foto

Kirim foto Anda sekarang! 📷

━━━━━━━━━━━━━━━━━━
Powered by Gemini AI
"""
    
    
    def _photo_tips(self):
        """Photo taking tips"""
        return """
📸 *TIPS FOTO YANG BAIK*

✅ *YANG BENAR:*

1. Fokus pada lesi (close-up)
2. Jarak 10-15 cm
3. Cahaya terang & merata
4. Lesi di tengah foto
5. Tidak blur/goyang

❌ *YANG SALAH:*

1. Terlalu jauh
2. Gelap/bayangan
3. Blur/tidak fokus
4. Lesi tidak jelas
5. Tangan goyang

💡 *BONUS TIPS:*

• Foto di siang hari (cahaya alami)
• Gunakan lampu tambahan jika perlu
• Tahan HP stabil saat foto
• Bersihkan kamera HP

Selamat mencoba! 📷✨
"""
    
    
    def _help_message(self):
        """Help message"""
        return """
📋 *BANTUAN DERMACHECK AI*

Cara menggunakan:

1️⃣ *Kirim Foto*
   Kirim foto tahi lalat/lesi kulit

2️⃣ *Tunggu Analisis*
   AI analisis dalam 15-30 detik

3️⃣ *Baca Hasil*
   Lihat tingkat risiko & saran

💬 *Perintah:*

• HALO - Selamat datang
• HELP - Bantuan ini
• TIPS - Panduan foto

📸 Langsung kirim foto untuk mulai!
"""


# Test instance
if __name__ == '__main__':
    print("✅ DermaCheck AI Sherlock Engine loaded successfully!")
    engine = SherlockEngine()
    print("🤖 Engine ready for WhatsApp integration!")
