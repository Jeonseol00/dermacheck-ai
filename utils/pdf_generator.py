"""
SOAP Note PDF Generator
Creates professional medical summary PDFs from SOAP consultation results
v2.1.1: Fixed emoji encoding for latin-1 font compatibility
"""
from fpdf import FPDF
from datetime import datetime
from typing import Dict, Optional
import os
import re


def sanitize_for_pdf(text: str) -> str:
    """
    Remove emoji and non-latin characters for PDF compatibility
    
    Args:
        text: Input text possibly containing emoji
        
    Returns:
        Cleaned text with only latin-1 compatible characters
    """
    # SAFETY CHECK: Only process strings, return non-strings as-is
    # This prevents errors when called on bytearray, None, or other types
    if not isinstance(text, str):
        return text
    
    # Return empty string as-is
    if not text:
        return text
    
    # Method 1: Remove emoji using regex pattern
    # Covers most common emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # extended symbols
        "]+",
        flags=re.UNICODE
    )
    
    text = emoji_pattern.sub('', text)
    
    # Method 2: Encode to latin-1 and ignore errors
    # This catches any remaining non-latin characters
    try:
        text = text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        pass
    
    return text.strip()


class SOAPReportGenerator(FPDF):
    """
    Professional PDF generator for SOAP medical notes
    """
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Custom header with DermaCheck branding"""
        # Logo/Title - NO EMOJI
        self.set_font('Arial', 'B', 20)
        self.set_text_color(20, 184, 166)  # Medical Teal
        self.cell(0, 10, 'DermaCheck AI', 0, 1, 'C')
        
        # Subtitle
        self.set_font('Arial', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'AI Pre-Consultation Medical Assistant', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """Custom footer with page numbers and disclaimer"""
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Page number
        self.cell(0, 5, f'Page {self.page_no()}', 0, 1, 'C')
        
        # Disclaimer
        self.set_text_color(200, 0, 0)  # Red warning
        self.set_font('Arial', 'B', 8)
        self.multi_cell(0, 4, 'IMPORTANT: This is AI-generated assistance, not a medical diagnosis. '
                              'Always consult a qualified healthcare professional.', 0, 'C')
        
    def add_section_title(self, title: str, color_r: int = 59, color_g: int = 130, color_b: int = 246):
        """Add a styled section title"""
        title = sanitize_for_pdf(title)  # Clean text
        self.set_font('Arial', 'B', 14)
        self.set_text_color(color_r, color_g, color_b)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.ln(2)
        
    def add_info_box(self, label: str, value: str, color_r: int = 240, color_g: int = 240, color_b: int = 240):
        """Add an info box with label and value"""
        label = sanitize_for_pdf(label)  # Clean text
        value = sanitize_for_pdf(value)  # Clean text
        
        # Background box
        self.set_fill_color(color_r, color_g, color_b)
        self.rect(self.get_x(), self.get_y(), 190, 10, 'F')
        
        # Label
        self.set_font('Arial', 'B', 10)
        self.cell(50, 10, label + ':', 0, 0, 'L')
        
        # Value
        self.set_font('Arial', '', 10)
        self.cell(0, 10, value, 0, 1, 'L')
        self.ln(2)
        
    def add_triage_badge(self, level: str, color: str, recommendation: str):
        """Add styled triage priority badge"""
        level = sanitize_for_pdf(level)  # Clean text
        recommendation = sanitize_for_pdf(recommendation)  # Clean text
        
        # Map colors
        color_map = {
            'red': (220, 38, 38),
            'orange': (249, 115, 22),
            'yellow': (234, 179, 8),
            'green': (34, 197, 94)
        }
        
        rgb = color_map.get(color, (128, 128, 128))
        
        # Title - NO EMOJI
        self.set_font('Arial', 'B', 12)
        self.set_text_color(rgb[0], rgb[1], rgb[2])
        self.cell(0, 8, f'TRIAGE PRIORITY: {level}', 0, 1, 'L')
        
        # Recommendation
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, f'Recommendation: {recommendation}', 0, 'L')
        self.ln(5)
        
    def add_soap_section(self, section_letter: str, section_name: str, content: str):
        """Add a SOAP section (S, O, A, or P)"""
        section_letter = sanitize_for_pdf(section_letter)  # Clean text
        section_name = sanitize_for_pdf(section_name)  # Clean text
        content = sanitize_for_pdf(content)  # Clean text
        
        # Section header with colored bar
        self.set_fill_color(20, 184, 166)  # Medical teal
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, f' {section_letter} - {section_name.upper()} ', 0, 1, 'L', True)
        
        # Content
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 10)
        self.ln(2)
        
        # Clean and format content
        if content:
            # Remove excessive whitespace
            content = content.strip()
            # Wrap text properly
            self.multi_cell(0, 5, content, 0, 'L')
        else:
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 5, '[No data provided]', 0, 'L')
            self.set_text_color(0, 0, 0)
        
        self.ln(5)


def generate_soap_pdf(
    consultation_data: Dict,
    patient_name: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_gender: Optional[str] = None
) -> bytes:
    """
    Generate professional PDF from SOAP consultation result
    
    Args:
        consultation_data: Dictionary with SOAP note and triage info
        patient_name: Optional patient name
        patient_age: Optional patient age
        patient_gender: Optional patient gender
        
    Returns:
        PDF content as bytes
    """
    pdf = SOAPReportGenerator()
    pdf.add_page()
    
    # Document Info
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', 0, 1, 'R')
    pdf.ln(5)
    
    # Patient Information Section
    if patient_name or patient_age or patient_gender:
        pdf.add_section_title('Patient Information', 59, 130, 246)
        
        if patient_name:
            pdf.add_info_box('Patient Name', sanitize_for_pdf(patient_name))
        if patient_age:
            pdf.add_info_box('Age', f'{patient_age} years')
        if patient_gender and patient_gender != "Select...":
            pdf.add_info_box('Gender', sanitize_for_pdf(patient_gender))
        
        pdf.ln(5)
    
    # Chief Complaint (from raw input)
    pdf.add_section_title('Chief Complaint', 59, 130, 246)
    pdf.set_font('Arial', '', 10)
    complaint_text = sanitize_for_pdf(consultation_data.get('raw_input', 'No complaint provided'))
    pdf.multi_cell(0, 5, complaint_text, 0, 'L')
    pdf.ln(5)
    
    # Triage Priority
    triage = consultation_data.get('triage', {})
    if triage:
        pdf.add_section_title('Triage Assessment', 220, 38, 38)
        pdf.add_triage_badge(
            triage.get('level', 'ROUTINE'),
            triage.get('color', 'yellow'),
            triage.get('recommendation', 'Consult healthcare provider')
        )
    
    # Horizontal separator
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # SOAP Note Title
    pdf.add_section_title('SOAP Medical Note', 20, 184, 166)
    pdf.ln(2)
    
    # SOAP Sections
    soap = consultation_data.get('soap_note', {})
    
    pdf.add_soap_section('S', 'SUBJECTIVE', soap.get('subjective', ''))
    pdf.add_soap_section('O', 'OBJECTIVE', soap.get('objective', ''))
    pdf.add_soap_section('A', 'ASSESSMENT', soap.get('assessment', ''))
    pdf.add_soap_section('P', 'PLAN', soap.get('plan', ''))
    
    # Medical Entities (if significant)
    entities = consultation_data.get('medical_entities', {})
    if entities.get('red_flags'):
        pdf.ln(5)
        pdf.set_fill_color(254, 226, 226)  # Light red
        pdf.rect(pdf.get_x(), pdf.get_y(), 190, 8 + len(entities['red_flags']) * 5, 'F')
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(220, 38, 38)
        pdf.cell(0, 8, 'RED FLAGS DETECTED:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        for flag in entities['red_flags']:
            clean_flag = sanitize_for_pdf(flag.title())
            pdf.cell(0, 5, f'  - {clean_flag}', 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
    
    # Final Medical Disclaimer (prominent)
    pdf.ln(10)
    pdf.set_fill_color(255, 243, 205)  # Light yellow
    pdf.rect(10, pdf.get_y(), 190, 30, 'F')
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(146, 64, 14)  # Dark orange
    pdf.cell(0, 8, 'IMPORTANT MEDICAL DISCLAIMER', 0, 1, 'C')
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 4, 
        'This document is generated by artificial intelligence for informational and organizational '
        'purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. '
        'Always seek the advice of your physician or other qualified health provider with any questions '
        'you may have regarding a medical condition. Never disregard professional medical advice or delay '
        'in seeking it because of something you have read in this document.', 
        0, 'C')
    
    # Return PDF as bytes
    # fpdf2 v2.x: output(dest='S') already returns bytes, no need to encode
    pdf_output = pdf.output(dest='S')
    
    # Handle both str and bytes return types (fpdf2 version compatibility)
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    else:
        return pdf_output  # Already bytes


def create_downloadable_soap_pdf(consultation_data: Dict, filename: str = "soap_medical_summary.pdf") -> str:
    """
    Create a downloadable PDF file from SOAP data
    
    Args:
        consultation_data: SOAP consultation result
        filename: Desired filename
        
    Returns:
        Path to created PDF file
    """
    pdf_bytes = generate_soap_pdf(consultation_data)
    
    # Save to temp file
    output_path = f"/tmp/{filename}"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return output_path
