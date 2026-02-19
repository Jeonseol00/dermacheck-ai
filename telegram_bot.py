"""
DermaCheck AI — Telegram Bot v2
MedGemma-Powered Dermatology Screening via Kaggle Backend API

Bot: @DermaCheck_Fikri_Bot
Architecture: Telegram ←→ Bot (local) ←→ Kaggle Backend (ngrok)

v2.0: Rewritten to call v10 Kaggle backend API instead of local modules
"""

import os
import io
import re
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Telegram imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

import requests
from PIL import Image

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Backend URL — can be updated via /setbackend command
BACKEND_URL = os.getenv('DERMACHECK_BACKEND_URL', '')

# Store backend URL per-bot (persists in memory during session)
_backend_url_override: Optional[str] = None


def get_backend_url() -> str:
    """Get current backend URL (override > env > empty)"""
    return _backend_url_override or BACKEND_URL


# ═══════════════════════════════════════════════════════════════
# MESSAGES (Indonesian)
# ═══════════════════════════════════════════════════════════════

WELCOME_MESSAGE = """🏥 <b>Selamat Datang di DermaCheck AI!</b>

Saya adalah asisten AI dermatologi bertenaga <b>MedGemma</b> dari Google Health.

📸 <b>Analisis Kulit</b>
Kirim foto lesi kulit untuk mendapat:
• Diagnosis AI dengan tingkat keyakinan
• Tingkat risiko & rekomendasi
• Pedoman klinis international
• Saran tindak lanjut

💬 <b>Konsultasi Gejala</b>
Ketik gejala untuk konsultasi AI

⚠️ <b>Penting:</b>
Ini alat skrining AI, BUKAN pengganti dokter.
Untuk darurat: Hubungi 119 atau ke IGD!

📋 <b>Perintah:</b>
/help — Panduan lengkap
/tips — Tips mengambil foto
/setbackend — Set URL backend Kaggle
/status — Cek koneksi ke backend

Siap membantu! 🔬"""

HELP_MESSAGE = """📖 <b>Panduan DermaCheck AI</b>

🔬 <b>Cara Kerja:</b>
1. Kirim foto kulit → AI analisis via MedGemma
2. Terima diagnosis + confidence score
3. Lihat risk level & rekomendasi

🩺 <b>Yang Bisa Dideteksi:</b>
• Melanoma & kanker kulit
• Jerawat (acne vulgaris)
• Eksim & dermatitis
• Infeksi bakteri (impetigo)
• Psoriasis, rosacea, dll

📊 <b>Tingkat Risiko:</b>
🟢 RENDAH — Pantau rutin
🟡 SEDANG — Konsultasi dokter 
🔴 TINGGI — Segera ke dokter!

🔬 <b>Teknologi:</b>
• MedGemma 1.5-4b-it (Google Health)
• Pedoman AAD & PERDOSKI
• 95% Confidence Interval"""

TIPS_MESSAGE = """📸 <b>Tips Foto untuk Hasil Terbaik</b>

✅ <b>Lakukan:</b>
• Cahaya alami/terang, merata
• Jarak 10-15cm dari kulit
• Fokus tajam pada lesi
• Background polos/gelap
• Foto dari depan/tegak lurus

❌ <b>Jangan:</b>
• Tempat gelap / backlight
• Terlalu jauh atau dekat
• Foto buram/blur
• Pakai filter Instagram dll
• Edit brightness/contrast

📏 <b>Pro Tip:</b>
Letakkan penggaris/koin di samping lesi untuk skala ukuran!

Siap? Kirim foto sekarang! 📤"""


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    """Escape special chars for Telegram HTML parse mode"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def parse_ai_response(analysis_text: str, metadata: Dict[str, Any]) -> str:
    """Parse v10 API response into a comprehensive Telegram message (HTML).
    
    Professional multi-strategy parser:
    1. Structured metadata → highest priority for diagnosis/risk
    2. Section-header regex → parse structured AI output
    3. Narrative NLP → extract from RATIONALE/CLINICAL text
    4. Fallback → show cleaned AI summary
    """
    
    msg_parts = []
    msg_parts.append('🏥 <b>HASIL ANALISIS DERMACHECK AI</b>\n')
    
    # ── Helper: validate extracted diagnosis name ──
    def is_valid_name(name: str) -> bool:
        if not name or len(name) < 2:
            return False
        if re.match(r'^\d+\s*%?$', name):
            return False
        if re.match(r'^(Confidence|Risk|Tingkat|Level|Score|Grade|Primary|Diagnosis)', name, re.IGNORECASE):
            return False
        if not re.search(r'[a-zA-Z]{2,}', name):
            return False
        # Reject backend placeholders
        if 'belum teridentifikasi' in name.lower() or 'not identified' in name.lower():
            return False
        return True
    
    # ══════════════════════════════════════════════
    # PHASE 1: EXTRACT DIAGNOSIS NAME
    # ══════════════════════════════════════════════
    diagnosis_name = ''
    confidence = None
    
    # Strategy 1A: Metadata (v10.1+)
    raw_meta_diag = str(metadata.get('primary_diagnosis', '') or '').strip()
    raw_meta_diag = re.sub(r'\*\*', '', raw_meta_diag)
    raw_meta_diag = re.sub(r'\s*\(.*?\)', '', raw_meta_diag).strip()  # Remove parentheticals
    raw_meta_diag = re.sub(r'\s*\d+\s*%.*$', '', raw_meta_diag).strip()  # Remove trailing %
    if is_valid_name(raw_meta_diag):
        diagnosis_name = raw_meta_diag
    
    meta_conf = metadata.get('confidence_score', None)
    if meta_conf is not None:
        try:
            confidence = int(meta_conf)
        except (ValueError, TypeError):
            pass
    
    # Strategy 1B: Regex on "PRIMARY DIAGNOSIS: Name (Confidence: XX%)" line
    if not diagnosis_name:
        # Pattern: "PRIMARY DIAGNOSIS: Seborrheic Keratosis (Confidence: 90%, Risk: LOW)"
        m = re.search(
            r"PRIMARY\s+DIAGNOSIS:\s*([A-Za-z][A-Za-z\s\-/.]+?)(?:\s*\((?:Confidence|Tingkat))",
            analysis_text, re.IGNORECASE
        )
        if m:
            candidate = m.group(1).strip().strip('*').strip(':,').strip()
            if is_valid_name(candidate):
                diagnosis_name = candidate
    
    if not diagnosis_name:
        # Pattern: "PRIMARY DIAGNOSIS: Name\n" (name on same line, no parenthetical)
        m = re.search(r'PRIMARY\s+DIAGNOSIS:\s*([^\n]+)', analysis_text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip().strip('*')
            candidate = re.sub(r'\(.*?\)', '', candidate).strip()
            candidate = re.sub(r'\s*\d+\s*%.*$', '', candidate).strip()
            candidate = re.sub(r'\s*,\s*Risk.*$', '', candidate, flags=re.IGNORECASE).strip()
            if is_valid_name(candidate):
                diagnosis_name = candidate
    
    # Strategy 1C: Extract from RATIONALE narrative
    if not diagnosis_name:
        narrative_patterns = [
            r'(?:consistent with|characteristic of|suggestive of|indicative of|diagnosis (?:is|of))\s+([A-Z][a-zA-Z\s\-]{2,40}?)(?:\.|,|\s+(?:The|This|It|based|with|due))',
            r'(?:likely|probable|probable diagnosis is)\s+([A-Z][a-zA-Z\s\-]{2,40}?)(?:\.|,)',
            r'Diagnosis Utama:\s*([^\n(]+)',
        ]
        for pat in narrative_patterns:
            m = re.search(pat, analysis_text, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip().strip('*:,')
                candidate = re.sub(r'\s*\d+\s*%.*$', '', candidate).strip()
                if is_valid_name(candidate) and len(candidate) > 3:
                    diagnosis_name = candidate.title() if candidate[0].islower() else candidate
                    break
    
    # Strategy 1D: Extract first differential diagnosis name
    if not diagnosis_name:
        m = re.search(
            r'DIFFERENTIAL\s+DIAGNOS[IE]S?:?\s*\n\s*1\.?\s*([A-Za-z][A-Za-z\s\-/]{2,50})',
            analysis_text, re.IGNORECASE
        )
        if m:
            candidate = m.group(1).strip().split('\n')[0].strip()
            candidate = re.sub(r'\s*\(.*', '', candidate).strip()
            if is_valid_name(candidate):
                diagnosis_name = candidate
    
    # Strategy 1E: Find any medical condition name near a percentage
    if not diagnosis_name:
        m = re.search(r'([A-Z][a-z]+(?:\s+[A-Za-z]+){0,4})\s*(?:\(|\:)?\s*(?:Confidence:?\s*)?\d+\s*%', analysis_text)
        if m:
            candidate = m.group(1).strip()
            if is_valid_name(candidate) and len(candidate) > 3:
                diagnosis_name = candidate
    
    # Extract confidence from text if not from metadata
    if confidence is None:
        conf_m = re.search(r'(?:Confidence|Tingkat\s+Keyakinan)\s*:?\s*(\d+)\s*%', analysis_text, re.IGNORECASE)
        if conf_m:
            confidence = int(conf_m.group(1))
        else:
            confidence = metadata.get('confidence_analysis', {}).get('point_estimate', None)
            if confidence:
                confidence = int(confidence)
    
    # ══════════════════════════════════════════════
    # PHASE 2: BUILD DIAGNOSIS SECTION
    # ══════════════════════════════════════════════
    has_diagnosis = False
    if diagnosis_name:
        has_diagnosis = True
        msg_parts.append(f'🩺 <b>Diagnosis Utama:</b>')
        msg_parts.append(f'   <b>{escape_html(diagnosis_name)}</b>')
        if confidence:
            bar_full = confidence // 10
            bar = '█' * bar_full + '░' * (10 - bar_full)
            msg_parts.append(f'   📊 Keyakinan: <b>{confidence}%</b>')
            msg_parts.append(f'   {bar}')
        msg_parts.append('')
    
    # ══════════════════════════════════════════════
    # PHASE 3: RISK LEVEL
    # ══════════════════════════════════════════════
    risk_found = (str(metadata.get('risk_tier', '') or '')).upper() or None
    if not risk_found or risk_found not in ('LOW', 'MEDIUM', 'HIGH'):
        risk_patterns = [
            r'Risk\s*(?:Tier|Level)?\s*:?\s*[^A-Za-z]*(LOW|MEDIUM|HIGH)',
            r'Tingkat\s+Risiko\s*:?\s*(LOW|MEDIUM|HIGH|RENDAH|SEDANG|TINGGI)',
            r'URGENCY\s*:?\s*(ROUTINE|URGENT|EMERGENCY)',
        ]
        for pattern in risk_patterns:
            rm = re.search(pattern, analysis_text, re.IGNORECASE)
            if rm:
                mapped = rm.group(1).upper()
                # Map urgency → risk
                if mapped == 'ROUTINE':
                    mapped = 'LOW'
                elif mapped in ('URGENT', 'EMERGENCY'):
                    mapped = 'HIGH'
                risk_found = mapped
                break
    
    if risk_found:
        risk_map = {
            'LOW': ('🟢', 'RENDAH', 'Pantau rutin, periksa jika berubah'),
            'RENDAH': ('🟢', 'RENDAH', 'Pantau rutin, periksa jika berubah'),
            'MEDIUM': ('🟡', 'SEDANG', 'Konsultasi dokter kulit dalam 2-4 minggu'),
            'SEDANG': ('🟡', 'SEDANG', 'Konsultasi dokter kulit dalam 2-4 minggu'),
            'HIGH': ('🔴', 'TINGGI', 'SEGERA ke dokter dalam 1-2 minggu!'),
            'TINGGI': ('🔴', 'TINGGI', 'SEGERA ke dokter dalam 1-2 minggu!'),
        }
        emoji, label, advice = risk_map.get(risk_found, ('⚪', risk_found, ''))
        msg_parts.append(f'{emoji} <b>Tingkat Risiko: {label}</b>')
        msg_parts.append(f'   {escape_html(advice)}\n')
    
    # ══════════════════════════════════════════════
    # PHASE 4: CLINICAL EXPLANATION (RATIONALE + FINDINGS)
    # ══════════════════════════════════════════════
    clinical_text = ''
    
    # Try multiple section headers that MedGemma uses
    for section_name in ['RATIONALE', 'CLINICAL FINDINGS', 'CLINICAL DESCRIPTION', 
                          'CLINICAL ASSESSMENT', 'DESKRIPSI KLINIS', 'ASSESSMENT']:
        # Pattern A: Section on its own line
        pattern = re.escape(section_name) + r'\s*:?\s*\n([\s\S]*?)(?=\n\s*(?:DIFFERENTIAL|RECOMMENDATION|ABCDE|RISK|URGENCY|RED FLAG|SKIN OF COLOR|FOLLOW|$))'
        m = re.search(pattern, analysis_text, re.IGNORECASE)
        if m:
            clinical_text = m.group(1).strip()
            break
        # Pattern B: Inline "Rationale: The lesion..." (from safety-net restored text)
        pattern_b = re.escape(section_name) + r'\s*:\s*([^\n].+?)(?=\n\s*(?:DIFFERENTIAL|RECOMMENDATION|ABCDE|RISK|URGENCY|RED FLAG|SKIN OF COLOR|FOLLOW|PRIMARY|$))'
        m = re.search(pattern_b, analysis_text, re.IGNORECASE | re.DOTALL)
        if m:
            clinical_text = m.group(1).strip()
            break
    
    if clinical_text:
        # Clean up
        clinical_text = re.sub(r'\*\*', '', clinical_text)
        
        # Split into content lines, filter non-clinical
        raw_lines = []
        for l in clinical_text.split('\n'):
            l = l.strip()
            if not l or len(l) < 10:
                continue
            if re.match(r'^(PRIMARY\s+DIAGNOSIS|DIFFERENTIAL|RECOMMENDATION|Risk\s*Tier|URGENCY)', l, re.IGNORECASE):
                continue
            raw_lines.append(l)
        
        # Smart sentence split: if a line is too long, break into sentences
        sentences = []
        for line in raw_lines:
            if len(line) > 300:
                # Split by sentence boundaries (". " followed by uppercase)
                parts = re.split(r'(?<=\.)\s+(?=[A-Z])', line)
                sentences.extend(parts)
            else:
                sentences.append(line)
        
        if sentences:
            msg_parts.append('🔍 <b>Penjelasan Klinis:</b>')
            total_chars = 0
            for sent in sentences:
                sent = sent.strip()
                if not sent or len(sent) < 5:
                    continue
                # Remove "Rationale:" prefix if present
                sent = re.sub(r'^Rationale:\s*', '', sent, flags=re.IGNORECASE)
                if not sent:
                    continue
                # Cap total at 900 chars total to stay within Telegram limits
                if total_chars + len(sent) > 900:
                    remaining = 900 - total_chars
                    if remaining > 30:
                        msg_parts.append(f'   {escape_html(sent[:remaining])}...')
                    break
                msg_parts.append(f'   {escape_html(sent)}')
                total_chars += len(sent)
            msg_parts.append('')
    
    # ══════════════════════════════════════════════
    # PHASE 5: DIFFERENTIAL DIAGNOSES
    # ══════════════════════════════════════════════
    
    # Pattern A: "1. Condition (Confidence: 65%)" or "1. Condition (65%)"
    diff_matches = re.findall(
        r'\d+\.?\s*([^(\n]{3,80}?)\s*\((?:Confidence:?\s*)?(\d+)\s*%\)',
        analysis_text, re.IGNORECASE
    )
    
    filtered_diffs = []
    for name, conf in diff_matches:
        name_clean = re.sub(r'\*\*', '', name).strip().rstrip(':,').strip()
        if name_clean.lower().startswith('primary'):
            continue
        if diagnosis_name and name_clean.lower() == diagnosis_name.lower():
            continue
        if not is_valid_name(name_clean):
            continue
        filtered_diffs.append((name_clean, int(conf)))
    
    # Pattern B: Numbered list under DIFFERENTIAL section without percentages
    if not filtered_diffs:
        diff_section = re.search(
            r'DIFFERENTIAL\s+(?:DIAGNOS[IE]S?|CONSIDERATIONS?)\s*:?\s*\n([\s\S]*?)(?=\n\s*(?:CLINICAL|ASSESSMENT|RECOMMENDATION|FOLLOW|ABCDE|RISK|URGENCY|RED FLAG|$))',
            analysis_text, re.IGNORECASE
        )
        if diff_section:
            numbered = re.findall(r'^\s*\d+\.\s*(.+?)$', diff_section.group(1), re.MULTILINE)
            base_conf = confidence if confidence else 80
            for idx, name in enumerate(numbered[:4]):
                name_clean = re.sub(r'\*\*', '', name).strip()
                if re.match(r'^(Rationale|Description|Note|Risk|Key)', name_clean, re.IGNORECASE):
                    continue
                cond_match = re.match(r'^([^(]+)', name_clean)
                if cond_match:
                    cond_name = cond_match.group(1).strip().rstrip(':,')
                    if is_valid_name(cond_name):
                        est_conf = max(15, base_conf - (15 * (idx + 1)))
                        filtered_diffs.append((cond_name, est_conf))
    
    if filtered_diffs:
        msg_parts.append('📋 <b>Diagnosis Banding:</b>')
        for i, (name, conf) in enumerate(filtered_diffs[:4], 1):
            bar_full = conf // 10
            bar = '█' * bar_full + '░' * (10 - bar_full)
            msg_parts.append(f'   {i}. {escape_html(name)} ({conf}%)')
            msg_parts.append(f'      {bar}')
        msg_parts.append('')
    
    # ══════════════════════════════════════════════
    # PHASE 6: RECOMMENDATION
    # ══════════════════════════════════════════════
    rec_match = re.search(
        r'RECOMMENDATION\s*:?\s*\n([\s\S]*?)(?=\n\s*(?:RED FLAG|SKIN OF COLOR|URGENCY|DISCLAIMER|$))',
        analysis_text, re.IGNORECASE
    )
    if rec_match:
        rec_text = re.sub(r'\*\*', '', rec_match.group(1).strip())
        rec_lines = [l.strip() for l in rec_text.split('\n') if l.strip() and len(l.strip()) > 5]
        if rec_lines:
            msg_parts.append('💡 <b>Rekomendasi:</b>')
            for line in rec_lines[:4]:
                if len(line) > 200:
                    line = line[:197] + '...'
                # Add bullet icon for numbered items
                if re.match(r'^\d+\.', line):
                    line = re.sub(r'^(\d+)\.\s*', r'   \1. ', line)
                msg_parts.append(f'   {escape_html(line)}')
            msg_parts.append('')
    
    # ══════════════════════════════════════════════
    # PHASE 7: METADATA-BASED SECTIONS
    # ══════════════════════════════════════════════
    
    # Clinical Guidelines
    guidelines = metadata.get('clinical_guidelines', {})
    if guidelines.get('primary_guideline'):
        msg_parts.append('📖 <b>Pedoman Klinis:</b>')
        msg_parts.append(f'   🌐 {escape_html(guidelines["primary_guideline"])}')
        if guidelines.get('indonesian_reference'):
            msg_parts.append(f'   🇮🇩 {escape_html(guidelines["indonesian_reference"])}')
        msg_parts.append('')
    
    # Follow-up Plan
    follow_up = metadata.get('follow_up_plan', {})
    if follow_up.get('timeframe_indonesian'):
        msg_parts.append('⏰ <b>Tindak Lanjut:</b>')
        msg_parts.append(f'   📅 {escape_html(follow_up["timeframe_indonesian"])}')
        if follow_up.get('urgency_indonesian'):
            msg_parts.append(f'   ⚡ {escape_html(follow_up["urgency_indonesian"])}')
        
        actions = follow_up.get('action_items_indonesian', [])
        if actions:
            msg_parts.append('')
            msg_parts.append('💊 <b>Yang Harus Dilakukan:</b>')
            for action in actions[:5]:
                msg_parts.append(f'   ✅ {escape_html(action)}')
        msg_parts.append('')
    
    # Confidence Interval
    ci = metadata.get('confidence_analysis', {})
    if ci.get('ci_95_lower') is not None:
        lower = ci['ci_95_lower']
        upper = ci['ci_95_upper']
        msg_parts.append(f'📊 <b>95% Confidence Interval:</b> {lower:.1f}% — {upper:.1f}%\n')
    
    # ══════════════════════════════════════════════
    # PHASE 8: FALLBACK (if no diagnosis extracted at all)
    # ══════════════════════════════════════════════
    if not has_diagnosis and not clinical_text:
        clean_text = re.sub(r'\*\*', '', analysis_text).strip()
        # Show first meaningful paragraph
        lines = []
        for line in clean_text.split('\n'):
            line = line.strip()
            if line and len(line) > 15 and not re.match(r'^[-=]{3,}', line):
                lines.append(line)
                if len(lines) >= 6:
                    break
        if lines:
            msg_parts.insert(1, '🔬 <b>Analisis AI:</b>')
            for i, line in enumerate(lines):
                if len(line) > 200:
                    line = line[:197] + '...'
                msg_parts.insert(2 + i, f'   {escape_html(line)}')
            msg_parts.insert(2 + len(lines), '')
    
    # ══════════════════════════════════════════════
    # PHASE 9: DISCLAIMER
    # ══════════════════════════════════════════════
    msg_parts.append('⚕️ <b>Disclaimer:</b>')
    disclaimer = metadata.get('disclaimer', {})
    if disclaimer.get('patient_short'):
        msg_parts.append(f'<i>{escape_html(disclaimer["patient_short"])}</i>')
    else:
        msg_parts.append('<i>Hasil ini BUKAN diagnosis medis resmi. Selalu konsultasi dengan dokter.</i>')
    
    msg_parts.append('')
    msg_parts.append('📸 Kirim foto lain atau /help untuk info')
    
    return '\n'.join(msg_parts)


def parse_simple_response(analysis_text: str) -> str:
    """Fallback: Smart parser when metadata is minimal/absent.
    Extracts structure from raw AI text for readable Telegram display."""
    
    clean = re.sub(r'\*\*', '', analysis_text).strip()
    msg_parts = ['🏥 <b>HASIL ANALISIS DERMACHECK AI</b>\n']
    
    # Try to extract primary diagnosis even from raw text
    primary = re.search(
        r'PRIMARY\s+DIAGNOSIS:\s*(.+?)(?:\n|$)',
        clean, re.IGNORECASE
    )
    if primary:
        diag = primary.group(1).strip()
        msg_parts.append(f'🩺 <b>Diagnosis:</b> {escape_html(diag)}\n')
    
    # Try to extract risk
    risk = re.search(r'Risk\s*(?:Tier|Level)?\s*:?\s*(LOW|MEDIUM|HIGH)', clean, re.IGNORECASE)
    if risk:
        risk_map = {'LOW': '🟢 RENDAH', 'MEDIUM': '🟡 SEDANG', 'HIGH': '🔴 TINGGI'}
        msg_parts.append(f'⚠️ <b>Risiko:</b> {risk_map.get(risk.group(1).upper(), risk.group(1))}\n')
    
    # Show main text (cleaned & truncated)
    # Remove already-extracted sections to avoid duplication
    display_text = clean
    if len(display_text) > 2800:
        display_text = display_text[:2800] + '\n\n... (dipotong untuk Telegram)'
    
    msg_parts.append(escape_html(display_text))
    msg_parts.append('\n⚕️ <i>Hasil ini BUKAN diagnosis medis resmi. Selalu konsultasi dengan dokter.</i>')
    msg_parts.append('📸 Kirim foto lain atau /help untuk info')
    
    return '\n'.join(msg_parts)


async def call_backend_api(image_bytes: bytes, complaint: str = 'Skin evaluation') -> Dict[str, Any]:
    """Call Kaggle backend /analyze API"""
    backend_url = get_backend_url()
    
    if not backend_url:
        return {'success': False, 'error': 'Backend URL belum disiapkan. Gunakan /setbackend <url>'}
    
    url = f'{backend_url.rstrip("/")}/analyze'
    
    try:
        # Prepare multipart form data (matching FastAPI endpoint signature)
        files = {
            'file': ('skin_photo.jpg', image_bytes, 'image/jpeg')
        }
        data = {
            'age': 30,
            'sex': 'male',
            'fitzpatrick_type': 3,
            'body_location': 'face',
            'duration': '1 week',
            'chief_complaint': complaint,
            'symptoms': '',
            'itch_score': 0,
            'pain_present': 'false',
            'warmth_present': 'false',
            'fever': 'false',
            'rapidly_progressive': 'false',
            'recent_medications': 'None',
            'known_allergies': 'None',
            'medical_history': 'None',
            'family_history': 'None',
            'recent_travel': 'None'
        }
        
        logger.info(f'Calling backend: {url}')
        # ngrok free tier requires this header to skip browser warning page
        headers = {'ngrok-skip-browser-warning': 'true'}
        response = requests.post(url, files=files, data=data, headers=headers, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f'Backend response: success={result.get("success")}')
            return result
        else:
            return {
                'success': False, 
                'error': f'Backend error: HTTP {response.status_code}'
            }
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Backend timeout (>5 menit). MedGemma mungkin sedang sibuk, coba lagi.'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Tidak bisa connect ke backend. Pastikan Kaggle notebook berjalan.'}
    except Exception as e:
        return {'success': False, 'error': f'Error: {str(e)[:200]}'}


async def call_consultation_api(symptoms: str) -> Dict[str, Any]:
    """Call Kaggle backend /api/consultation/text endpoint"""
    backend_url = get_backend_url()
    
    if not backend_url:
        return {'success': False, 'error': 'Backend URL belum disiapkan. Gunakan /setbackend <url>'}
    
    url = f'{backend_url.rstrip("/")}/api/consultation/text'
    
    try:
        headers = {
            'ngrok-skip-browser-warning': 'true',
            'Content-Type': 'application/json'
        }
        payload = {
            'symptoms_text': symptoms,
            'user_age': None,
            'medical_history': None
        }
        
        logger.info(f'Calling consultation: {url}')
        response = requests.post(url, json=payload, headers=headers, timeout=300)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Timeout — AI sedang sibuk, coba lagi.'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Tidak bisa connect ke backend.'}
    except Exception as e:
        return {'success': False, 'error': str(e)[:200]}


def format_consultation_response(result: Dict[str, Any]) -> str:
    """Format consultation API response for Telegram HTML"""
    response_text = result.get('response', '')
    
    if not response_text:
        return '❌ AI tidak menghasilkan respons. Coba lagi.'
    
    # Clean markdown formatting for Telegram
    clean = response_text.replace('**', '').replace('*', '')
    clean = escape_html(clean)
    
    # Truncate if too long
    if len(clean) > 3500:
        clean = clean[:3500] + '\n\n... (dipotong)'
    
    msg = '🩺 <b>KONSULTASI MEDIS AI</b>\n\n'
    msg += clean
    msg += '\n\n⚕️ <i>Ini BUKAN diagnosis resmi. Konsultasikan dengan dokter.</i>'
    msg += '\n\n📸 Kirim foto untuk analisis visual, atau ketik gejala lain.'
    
    return msg


# ═══════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode='HTML')
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode='HTML')


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tips command"""
    await update.message.reply_text(TIPS_MESSAGE, parse_mode='HTML')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status — check backend connection"""
    url = get_backend_url()
    
    if not url:
        await update.message.reply_text(
            '⚠️ <b>Backend belum disiapkan!</b>\n\n'
            'Gunakan:\n'
            '<code>/setbackend https://xxxx.ngrok-free.app</code>\n\n'
            'URL ini didapat dari Kaggle notebook setelah Cell 4 dijalankan.',
            parse_mode='HTML'
        )
        return
    
    await update.message.reply_text(f'🔄 Mengecek koneksi ke:\n<code>{escape_html(url)}</code>', parse_mode='HTML')
    
    try:
        # Use root endpoint (/) — backend has no /health route
        # Add ngrok-skip-browser-warning header for ngrok free tier
        headers = {'ngrok-skip-browser-warning': 'true'}
        resp = requests.get(f'{url.rstrip("/")}/', headers=headers, timeout=10)
        if resp.status_code == 200:
            await update.message.reply_text(
                f'✅ <b>Backend aktif!</b>\n\n'
                f'URL: <code>{escape_html(url)}</code>\n'
                f'Status: 🟢 Online\n\n'
                f'Siap menerima foto untuk analisis!',
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f'⚠️ Backend merespon tapi error: HTTP {resp.status_code}',
                parse_mode='HTML'
            )
    except Exception as e:
        await update.message.reply_text(
            f'❌ <b>Tidak bisa connect ke backend</b>\n\n'
            f'Error: {escape_html(str(e)[:200])}\n\n'
            f'Pastikan Kaggle notebook berjalan dan Cell 4 sudah dijalankan.',
            parse_mode='HTML'
        )


async def setbackend_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setbackend <url> — update backend URL"""
    global _backend_url_override
    
    if not context.args:
        current = get_backend_url()
        msg = '⚙️ <b>Set Backend URL</b>\n\n'
        if current:
            msg += f'Current: <code>{escape_html(current)}</code>\n\n'
        msg += 'Gunakan:\n<code>/setbackend https://xxxx.ngrok-free.app</code>'
        await update.message.reply_text(msg, parse_mode='HTML')
        return
    
    url = context.args[0].strip().rstrip('/')
    
    # Validate URL format
    if not url.startswith('http'):
        await update.message.reply_text('❌ URL harus diawali dengan http:// atau https://')
        return
    
    _backend_url_override = url
    
    await update.message.reply_text(
        f'✅ <b>Backend URL berhasil diset!</b>\n\n'
        f'URL: <code>{escape_html(url)}</code>\n\n'
        f'Gunakan /status untuk test koneksi.',
        parse_mode='HTML'
    )
    logger.info(f"Backend URL set to: {url}")


# ═══════════════════════════════════════════════════════════════
# MESSAGE HANDLERS
# ═══════════════════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    text_lower = text.lower()
    
    # Quick responses
    if any(word in text_lower for word in ['halo', 'hai', 'hello', 'hi']):
        await update.message.reply_text(
            '👋 Halo! Saya DermaCheck AI.\n\n'
            '📸 Kirim <b>foto</b> untuk analisis kulit\n'
            '💬 Atau <b>ketik gejala</b> untuk konsultasi\n\n'
            'Contoh: <i>"Muncul bintik merah di tangan sejak 3 hari"</i>',
            parse_mode='HTML'
        )
        return
    
    if 'help' in text_lower or 'bantuan' in text_lower:
        await help_command(update, context)
        return
    
    if 'tips' in text_lower:
        await tips_command(update, context)
        return
    
    # For longer text: forward as symptom consultation to backend
    if len(text) > 10:
        # Check backend
        if not get_backend_url():
            await update.message.reply_text(
                '⚠️ <b>Backend belum disiapkan!</b>\n\n'
                'Gunakan: <code>/setbackend https://xxxx.ngrok-free.app</code>',
                parse_mode='HTML'
            )
            return
        
        processing_msg = await update.message.reply_text(
            '🩺 <b>Menganalisis gejala Anda...</b>\n\n'
            '⏳ AI sedang memeriksa...\n\n'
            f'<i>"{escape_html(text[:80])}..."</i>',
            parse_mode='HTML'
        )
        
        try:
            result = await call_consultation_api(text)
            
            if result.get('success'):
                telegram_msg = format_consultation_response(result)
                if len(telegram_msg) > 4096:
                    telegram_msg = telegram_msg[:4000] + '\n\n... <i>(dipotong)</i>'
                await processing_msg.edit_text(telegram_msg, parse_mode='HTML')
            else:
                error = result.get('error', 'Unknown error')
                await processing_msg.edit_text(
                    f'❌ <b>Konsultasi gagal</b>\n\n{escape_html(error)}\n\n'
                    f'💡 Coba kirim ulang atau kirim foto untuk analisis visual.',
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f'Consultation error: {e}')
            await processing_msg.edit_text(
                f'❌ Error: {escape_html(str(e)[:200])}',
                parse_mode='HTML'
            )
    else:
        await update.message.reply_text(
            '📸 Kirim foto kulit untuk analisis, atau /help untuk panduan.',
            parse_mode='HTML'
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads — send to Kaggle backend API"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or 'User'
    logger.info(f"Photo from user {user_id} ({user_name})")
    
    # Check backend
    if not get_backend_url():
        await update.message.reply_text(
            '⚠️ <b>Backend belum disiapkan!</b>\n\n'
            'Admin perlu menjalankan:\n'
            '<code>/setbackend https://xxxx.ngrok-free.app</code>\n\n'
            'URL didapat dari Kaggle notebook.',
            parse_mode='HTML'
        )
        return
    
    try:
        # Send processing message with animation
        processing_msg = await update.message.reply_text(
            '📥 <b>Foto diterima!</b>\n\n'
            '🔬 Menganalisis dengan MedGemma AI...\n'
            '⏳ Estimasi: 30-60 detik\n\n'
            '<i>AI sedang memeriksa fitur klinis...</i>',
            parse_mode='HTML'
        )
        
        # Download photo (get largest resolution)
        if update.message.photo:
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
        elif update.message.document:
            photo_file = await update.message.document.get_file()
        else:
            await processing_msg.edit_text('❌ Format file tidak didukung.')
            return
        
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Validate image
        try:
            img = Image.open(io.BytesIO(photo_bytes))
            logger.info(f"Image: {img.size}, mode: {img.mode}")
            
            # Convert to JPEG if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            jpeg_buffer = io.BytesIO()
            img.save(jpeg_buffer, format='JPEG', quality=90)
            photo_bytes = jpeg_buffer.getvalue()
            
        except Exception as e:
            await processing_msg.edit_text(
                f'❌ <b>File bukan gambar valid</b>\n\n'
                f'Kirim foto lesi kulit dalam format JPG/PNG.',
                parse_mode='HTML'
            )
            return
        
        # Update progress
        await processing_msg.edit_text(
            '📥 <b>Foto diterima!</b>\n\n'
            '🧠 MedGemma sedang menganalisis...\n'
            '⏳ Mohon tunggu...\n\n'
            '<i>Membandingkan dengan database dermatologi...</i>',
            parse_mode='HTML'
        )
        
        # Get caption as complaint (if any)
        complaint = update.message.caption or 'Skin evaluation'
        
        # Call backend API
        result = await call_backend_api(bytes(photo_bytes), complaint)
        
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            await processing_msg.edit_text(
                f'❌ <b>Analisis gagal</b>\n\n'
                f'{escape_html(error_msg)}\n\n'
                f'💡 Coba lagi atau kirim foto lain.',
                parse_mode='HTML'
            )
            return
        
        # Parse response
        analysis = result.get('analysis', result.get('diagnosis', ''))
        metadata = result.get('metadata', {})
        
        # v10.1: Merge top-level structured fields into metadata
        for key in ('primary_diagnosis', 'confidence_score', 'risk_tier'):
            if key not in metadata and key in result:
                metadata[key] = result[key]
        
        # ── DIAGNOSTIC LOGGING ──
        logger.info("=" * 60)
        logger.info("DEBUG: BACKEND RESPONSE RECEIVED")
        logger.info(f"  result keys: {list(result.keys())}")
        logger.info(f"  metadata keys: {list(metadata.keys())}")
        logger.info(f"  primary_diagnosis (meta): '{metadata.get('primary_diagnosis', 'N/A')}'")
        logger.info(f"  confidence_score (meta): '{metadata.get('confidence_score', 'N/A')}'")
        logger.info(f"  risk_tier (meta): '{metadata.get('risk_tier', 'N/A')}'")
        logger.info(f"  analysis length: {len(analysis)} chars")
        logger.info(f"  analysis first 500 chars:")
        logger.info(analysis[:500] if analysis else "(EMPTY)")
        logger.info("=" * 60)
        
        # v10.1.4: If analysis is too short, use ai_reasoning as fallback
        ai_reasoning = metadata.get('ai_reasoning', '')
        if len(analysis) < 200 and ai_reasoning and len(ai_reasoning) > 500:
            logger.info(f"⚠️ Analysis too short ({len(analysis)} chars) — using ai_reasoning ({len(ai_reasoning)} chars) as analysis")
            analysis = ai_reasoning
        
        # Format for Telegram
        if metadata:
            telegram_message = parse_ai_response(analysis, metadata)
        else:
            telegram_message = parse_simple_response(analysis)
        
        # Telegram message limit is 4096 chars
        if len(telegram_message) > 4096:
            telegram_message = telegram_message[:4000] + '\n\n... <i>(dipotong)</i>'
        
        # Send result
        await processing_msg.edit_text(telegram_message, parse_mode='HTML')
        
        logger.info(f"Analysis sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing photo: {str(e)}")
        try:
            await update.message.reply_text(
                f'❌ <b>Maaf, terjadi kesalahan</b>\n\n'
                f'{escape_html(str(e)[:200])}\n\n'
                f'Silakan coba lagi.',
                parse_mode='HTML'
            )
        except:
            pass


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.message:
            await update.message.reply_text(
                '❌ Maaf, terjadi kesalahan internal. Silakan coba lagi.'
            )
    except:
        pass


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Main function to run the bot"""
    
    if not TELEGRAM_BOT_TOKEN:
        print('❌ Error: TELEGRAM_BOT_TOKEN tidak ditemukan di .env')
        print('Tambahkan: TELEGRAM_BOT_TOKEN=<token> ke file .env')
        return
    
    logger.info('Starting DermaCheck AI Telegram Bot v2...')
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('tips', tips_command))
    application.add_handler(CommandHandler('status', status_command))
    application.add_handler(CommandHandler('setbackend', setbackend_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_photo))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Banner
    backend = get_backend_url()
    print('=' * 60)
    print('🤖 DermaCheck AI — Telegram Bot v2')
    print('=' * 60)
    print(f'✅ Bot     : @DermaCheck_Fikri_Bot')
    print(f'✅ Token   : ...{TELEGRAM_BOT_TOKEN[-8:]}')
    print(f'✅ Backend : {backend or "❌ NOT SET (use /setbackend)"}')
    print(f'✅ Engine  : MedGemma 1.5-4b-it via Kaggle')
    print('=' * 60)
    print()
    print('📱 Test di Telegram:')
    print('   1. Search: @DermaCheck_Fikri_Bot')
    print('   2. Send: /start')
    if not backend:
        print('   3. Set backend: /setbackend <ngrok-url>')
    print('   4. Upload foto lesi kulit')
    print('   5. Terima hasil analisis!')
    print()
    print('⏹️  Press Ctrl+C to stop bot')
    print()
    
    # Run
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
