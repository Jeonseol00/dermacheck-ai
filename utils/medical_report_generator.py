"""
Enhanced Medical Report Generator for DermaCheck AI
Generates professional medical referral PDFs with timeline visualization
Designed for doctor adoption - clear, actionable, professional format
"""
from fpdf import FPDF
from datetime import datetime
from typing import Dict, List, Optional
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import io
from PIL import Image
import numpy as np


class MedicalReferralReport(FPDF):
    """
    Professional medical referral PDF with timeline visualization
    Optimized for doctor readability and clinical workflow
    """
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(15, 15, 15)
        
    def header(self):
        """Professional medical header"""
        # Title
        self.set_font('Arial', 'B', 18)
        self.set_text_color(20, 100, 180)  # Medical Blue
        self.cell(0, 10, 'DERMACHECK AI - MEDICAL REFERRAL', 0, 1, 'C')
        
        # Subtitle
        self.set_font('Arial', 'I', 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, 'AI-Assisted Skin Lesion Documentation', 0, 1, 'C')
        
        # Horizontal line
        self.set_draw_color(200, 200, 200)
        self.line(15, 25, 195, 25)
        self.ln(5)
        
    def footer(self):
        """Professional footer with disclaimers"""
        self.set_y(-20)
        
        # Page number
        self.set_font('Arial', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f'Page {self.page_no()}', 0, 1, 'R')
        
        # Medical disclaimer (CRITICAL!)
        self.set_font('Arial', 'B', 7)
        self.set_text_color(180, 0, 0)
        self.multi_cell(0, 3, 
            'MEDICAL DISCLAIMER: This report is AI-generated for informational purposes only. '
            'It does NOT constitute a medical diagnosis. Clinical examination and professional '
            'judgment are required.', 0, 'C')
        
    def add_section_header(self, title: str):
        """Styled section header"""
        self.set_font('Arial', 'B', 12)
        self.set_text_color(20, 100, 180)
        self.set_fill_color(240, 245, 250)
        self.cell(0, 8, title, 0, 1, 'L', True)
        self.ln(2)
        
    def add_info_row(self, label: str, value: str):
        """Key-value information row"""
        self.set_font('Arial', 'B', 10)
        self.set_text_color(60, 60, 60)
        self.cell(50, 6, label + ':', 0, 0)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, str(value))
        
    def add_patient_summary(self, patient_data: Dict):
        """Add patient information section"""
        self.add_section_header('PATIENT INFORMATION')
        
        self.add_info_row('Report Date', datetime.now().strftime('%Y-%m-%d %H:%M WIB'))
        self.add_info_row('Patient ID', patient_data.get('patient_id', 'N/A'))
        self.add_info_row('Lesion Location', patient_data.get('body_location', 'Unknown'))
        
        if 'symptoms' in patient_data:
            self.add_info_row('Chief Complaint', patient_data['symptoms'])
        
        self.ln(5)
    
    def add_timeline_grid(self, timeline_entries: List[Dict]):
        """
        Add visual timeline grid with side-by-side comparison
        This is the KEY VALUE for doctors!
        """
        self.add_section_header('LESION EVOLUTION TIMELINE')
        
        if not timeline_entries:
            self.set_font('Arial', 'I', 10)
            self.cell(0, 6, 'No timeline data available', 0, 1)
            return
        
        # Take last 3 entries for comparison
        recent_entries = timeline_entries[-3:] if len(timeline_entries) > 3 else timeline_entries
        
        num_entries = len(recent_entries)
        col_width = 60
        x_start = 15
        y_start = self.get_y()
        
        # Headers (Dates)
        self.set_font('Arial', 'B', 9)
        for i, entry in enumerate(recent_entries):
            x = x_start + (i * col_width)
            self.set_xy(x, y_start)
            
            date_str = entry.get('timestamp', entry.get('date', 'Unknown'))
            if isinstance(date_str, str) and len(date_str) > 10:
                date_str = date_str[:10]  # YYYY-MM-DD only
            
            self.cell(col_width, 6, date_str, 1, 0, 'C')
        
        self.ln(6)
        
        # Images (if available)
        img_y = self.get_y()
        img_height = 45
        
        for i, entry in enumerate(recent_entries):
            x = x_start + (i * col_width)
            
            # Draw placeholder box
            self.rect(x, img_y, col_width, img_height)
            
            # Try to add actual image if available
            if 'image_path' in entry and entry['image_path']:
                try:
                    self.image(entry['image_path'], x=x+2, y=img_y+2, w=col_width-4)
                except:
                    # If image fails, show text placeholder
                    self.set_xy(x, img_y + 20)
                    self.set_font('Arial', 'I', 8)
                    self.cell(col_width, 6, '[Image]', 0, 0, 'C')
        
        self.set_y(img_y + img_height + 2)
        
        # Scores
        self.set_font('Arial', 'B', 10)
        for i, entry in enumerate(recent_entries):
            x = x_start + (i * col_width)
            self.set_xy(x, self.get_y())
            
            score = entry.get('abcde_results', {}).get('total_score', 0)
            max_score = entry.get('abcde_results', {}).get('max_score', 11)
            risk = entry.get('abcde_results', {}).get('risk_level', 'UNKNOWN')
            
            # Color-code based on risk
            if risk == 'HIGH':
                self.set_text_color(200, 0, 0)
            elif risk == 'MEDIUM':
                self.set_text_color(200, 120, 0)
            else:
                self.set_text_color(0, 150, 0)
            
            self.cell(col_width, 6, f'{score}/{max_score} - {risk}', 1, 0, 'C')
        
        self.set_text_color(0, 0, 0)  # Reset color
        self.ln(10)
        
    def add_trend_chart(self, timeline_entries: List[Dict]):
        """Add ABCDE score trend chart"""
        if len(timeline_entries) < 2:
            return  # Need at least 2 points for a trend
        
        # Extract scores and dates
        dates = []
        scores = []
        
        for entry in timeline_entries:
            try:
                date_str = entry.get('timestamp', entry.get('date', ''))
                if date_str:
                    dates.append(date_str[:10])  # YYYY-MM-DD
                score = entry.get('abcde_results', {}).get('total_score', 0)
                scores.append(score)
            except:
                continue
        
        if len(scores) < 2:
            return
        
        # Create chart
        fig, ax = plt.subplots(figsize=(6, 3))
        
        ax.plot(range(len(scores)), scores, marker='o', linewidth=2, color='#1464B4')
        ax.fill_between(range(len(scores)), scores, alpha=0.3, color='#1464B4')
        
        # Formatting
        ax.set_xlabel('Timeline', fontsize=9)
        ax.set_ylabel('ABCDE Score (out of 11)', fontsize=9)
        ax.set_title('Risk Score Progression', fontsize=10, fontweight='bold')
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)
        ax.set_ylim(0, 11)
        ax.grid(True, alpha=0.3)
        
        # Risk zones (background colors)
        ax.axhspan(0, 3, alpha=0.1, color='green', label='Low Risk')
        ax.axhspan(3, 7, alpha=0.1, color='orange', label='Medium Risk')
        ax.axhspan(7, 11, alpha=0.1, color='red', label='High Risk')
        
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        # Add to PDF
        try:
            chart_img = Image.open(buf)
            chart_path = '/tmp/dermacheck_trend_chart.png'
            chart_img.save(chart_path)
            
            self.add_section_header('RISK SCORE TREND ANALYSIS')
            self.image(chart_path, x=30, w=150)
            self.ln(5)
        except Exception as e:
            print(f"Chart generation error: {e}")
    
    def add_latest_analysis(self, latest_entry: Dict):
        """Add detailed ABCDE analysis from latest entry"""
        self.add_section_header('LATEST AI-ASSISTED ANALYSIS')
        
        abcde = latest_entry.get('abcde_results', {})
        if not abcde:
            self.cell(0, 6, 'No analysis data available', 0, 1)
            return
        
        scores = abcde.get('abcde_scores', {})
        descriptions = abcde.get('descriptions', {})
        
        # ABCDE breakdown
        self.set_font('Arial', '', 9)
        
        criteria = [
            ('Asymmetry', 'asymmetry', 2),
            ('Border', 'border', 2),
            ('Color', 'color', 2),
            ('Diameter', 'diameter', 2),
            ('Evolution', 'evolution', 3)
        ]
        
        for name, key, max_val in criteria:
            score = scores.get(key, 0)
            desc = descriptions.get(key, 'No description')
            
            self.set_font('Arial', 'B', 9)
            self.cell(30, 5, f'{name}:', 0, 0)
            
            self.set_font('Arial', '', 9)
            self.cell(20, 5, f'{score}/{max_val}', 0, 0)
            
            self.set_font('Arial', 'I', 9)
            self.multi_cell(0, 5, f'- {desc}')
        
        # Total score
        self.ln(2)
        self.set_font('Arial', 'B', 11)
        total = abcde.get('total_score', 0)
        risk = abcde.get('risk_level', 'UNKNOWN')
        
        if risk == 'HIGH':
            self.set_text_color(200, 0, 0)
        elif risk == 'MEDIUM':
            self.set_text_color(200, 120, 0)
        else:
            self.set_text_color(0, 150, 0)
        
        self.cell(0, 8, f'TOTAL RISK SCORE: {total}/11 - {risk} RISK', 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        
        # AI Recommendation
        if 'recommendation' in abcde:
            self.ln(2)
            self.set_font('Arial', 'B', 10)
            self.cell(0, 6, 'AI Recommendation:', 0, 1)
            self.set_font('Arial', '', 9)
            self.multi_cell(0, 5, abcde['recommendation'])
        
        self.ln(5)
    
    def add_clinical_notes_section(self):
        """Add blank section for doctor's clinical notes"""
        self.add_section_header('CLINICAL EXAMINATION NOTES (For Doctor Use)')
        
        # Blank lined area for handwritten notes
        self.set_draw_color(200, 200, 200)
        y_start = self.get_y()
        
        for i in range(8):
            y = y_start + (i * 6)
            self.line(15, y, 195, y)
        
        self.set_y(y_start + 50)
        
    def generate_report(self, patient_data: Dict, timeline_entries: List[Dict]) -> bytes:
        """
        Generate complete medical referral PDF
        
        Args:
            patient_data: Dict with patient info and symptoms
            timeline_entries: List of timeline entries (chronological)
            
        Returns:
            PDF bytes
        """
        self.add_page()
        
        # Section 1: Patient Summary
        self.add_patient_summary(patient_data)
        
        # Section 2: Visual Timeline (KEY VALUE!)
        self.add_timeline_grid(timeline_entries)
        
        # Section 3: Trend Chart
        if len(timeline_entries) >= 2:
            self.add_trend_chart(timeline_entries)
        
        # Section 4: Latest AI Analysis
        if timeline_entries:
            self.add_latest_analysis(timeline_entries[-1])
        
        # Section 5: Clinical Notes (For Doctor)
        self.add_clinical_notes_section()
        
        # Section 6: Footer Info
        self.ln(5)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 4, 
            f'Generated by: DermaCheck AI v3.0\n'
            f'Generation Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")}\n'
            f'Total Timeline Entries: {len(timeline_entries)}'
        )
        
        # Return PDF bytes
        return self.output(dest='S').encode('latin-1')


# Helper function for easy integration
def generate_medical_referral_pdf(patient_data: Dict, timeline_entries: List[Dict], output_path: str = None) -> bytes:
    """
    Generate medical referral PDF
    
    Args:
        patient_data: Dict with patient_id, body_location, symptoms
        timeline_entries: List of timeline data (from TimelineManager)
        output_path: Optional file path to save PDF
        
    Returns:
        PDF bytes
    """
    report = MedicalReferralReport()
    pdf_bytes = report.generate_report(patient_data, timeline_entries)
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
    
    return pdf_bytes
