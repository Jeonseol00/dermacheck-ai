"""
PREMIUM PDF Medical Report Generator for DermaCheck AI
Modern, professional design with medical color scheme
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, 
                                 Image as RLImage, Table, TableStyle, PageBreak,
                                 KeepTogether, Frame, PageTemplate)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from datetime import datetime
import io
import os


class PremiumMedicalPDF:
    """
    Premium PDF Generator with Modern Medical Design
    
    Features:
    - Professional color scheme (Medical Blue + Gradients)
    - Beautiful typography with proper hierarchy
    - Visual icons and elements
    - Proper spacing and white space
    - Color-coded sections
    - Modern disclaimer box
    - Professional header/footer
    """
    
    # Color Palette (Medical Theme)
    PRIMARY_BLUE = colors.HexColor('#2563eb')
    PRIMARY_DARK = colors.HexColor('#1e40af')
    ACCENT_PURPLE = colors.HexColor('#8b5cf6')
    ACCENT_GREEN = colors.HexColor('#10b981')
    WARNING_AMBER = colors.HexColor('#f59e0b')
    URGENT_RED = colors.HexColor('#dc2626')
    
    BG_LIGHT_BLUE = colors.HexColor('#eff6ff')
    BG_LIGHT_PURPLE = colors.HexColor('#f5f3ff')
    BG_LIGHT_AMBER = colors.HexColor('#fffbeb')
    
    TEXT_PRIMARY = colors.HexColor('#1f2937')
    TEXT_SECONDARY = colors.HexColor('#6b7280')
    TEXT_LIGHT = colors.HexColor('#9ca3af')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_premium_styles()
    
    def _create_premium_styles(self):
        """Create premium paragraph styles"""
        
        # Prevent duplicate styles on re-instantiation
        if 'PremiumTitle' in self.styles:
            return
        
        # Main Title (Large, Bold, Centered)
        self.styles.add(ParagraphStyle(
            name='PremiumTitle',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=self.PRIMARY_BLUE,
            spaceAfter=6,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=34
        ))
        
        # Subtitle (Under title)
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.TEXT_SECONDARY,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=16
        ))
        
        # Section Header (Color-coded boxes)
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=15,
            textColor=colors.white,
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            leading=18,
            leftIndent=12,
            rightIndent=12,
            backColor=self.PRIMARY_BLUE,
            borderPadding=10,
            borderRadius=6
        ))
        
        # Subsection (Smaller headers)
        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=self.PRIMARY_DARK,
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            leading=16,
            leftIndent=6
        ))
        
        # Body Text (Normal content)
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.TEXT_PRIMARY,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=16,
            leftIndent=6,
            rightIndent=6
        ))
        
        # Bullet Points (For lists)
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.TEXT_PRIMARY,
            spaceAfter=6,
            leading=15,
            leftIndent=20,
            bulletIndent=10,
            bulletFontName='Helvetica',
            bulletFontSize=11
        ))
        
        # Info Box (Highlighted info)
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.PRIMARY_DARK,
            backColor=self.BG_LIGHT_BLUE,
            borderWidth=1,
            borderColor=self.PRIMARY_BLUE,
            borderPadding=12,
            borderRadius=6,
            spaceAfter=12,
            leading=16
        ))
        
        # Warning Box (Amber)
        self.styles.add(ParagraphStyle(
            name='WarningBox',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#78350f'),
            backColor=self.BG_LIGHT_AMBER,
            borderWidth=2,
            borderColor=self.WARNING_AMBER,
            borderPadding=14,
            borderRadius=8,
            spaceAfter=10,
            leading=15,
            leftIndent=8,
            rightIndent=8
        ))
    
    def _draw_header_footer(self, canvas_obj, doc):
        """Draw professional header and footer on each page"""
        canvas_obj.saveState()
        
        # Footer
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(self.TEXT_LIGHT)
        
        # Page number
        page_num = canvas_obj.getPageNumber()
       canvas_obj.drawRightString(
            doc.pagesize[0] - 2*cm,
            1.5*cm,
            f"Page {page_num}"
        )
        
        # Footer text
        canvas_obj.drawString(
            2*cm,
            1.5*cm,
            "DermaCheck AI - Educational Medical Report"
        )
        
        # Footer line
        canvas_obj.setStrokeColor(self.BG_LIGHT_BLUE)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(2*cm, 1.8*cm, doc.pagesize[0] - 2*cm, 1.8*cm)
        
        canvas_obj.restoreState()
    
    def generate_premium_report(
        self, 
        output_path: str,
        patient_info: dict,
        image_path: str,
        ai_response: str
    ) -> str:
        """
        Generate Premium PDF Medical Report
        
        Args:
            output_path: Where to save PDF
            patient_info: Dict with location, symptoms, age, gender
            image_path: Path to medical image (optional)
            ai_response: Full AI analysis text
        
        Returns:
            Path to generated PDF
        """
        
        # Create PDF with custom page template
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )
        
        # Story elements
        story = []
        
        # ==========================================
        # HEADER SECTION (Premium)
        # ==========================================
        
        # Logo emoji + Title
        title_text = "🏥 DermaCheck AI"
        title = Paragraph(title_text, self.styles['PremiumTitle'])
        story.append(title)
        
        # Subtitle
        subtitle_text = f"""
        <b>Medical Dermatology Analysis Report</b><br/>
        <font color="{self.TEXT_SECONDARY.hexval()}">
        Powered by MedGemma 1.5 4B • Generated {datetime.now().strftime("%B %d, %Y at %H:%M")}
        </font>
        """
        subtitle = Paragraph(subtitle_text, self.styles['Subtitle'])
        story.append(subtitle)
        
        # Decorative line
        story.append(Spacer(1, 0.2*cm))
        
        # ==========================================
        # PATIENT INFORMATION (Color Box)
        # ==========================================
        
        section_header = Paragraph(
            "📋 Patient Information", 
            self.styles['SectionHeader']
        )
        story.append(section_header)
        
        # Patient details in a nice table
        patient_data = []
        
        if patient_info.get('age'):
            patient_data.append([
                Paragraph("<b>Age:</b>", self.styles['BodyText']),
                Paragraph(f"{patient_info['age']} years", self.styles['BodyText'])
            ])
        
        if patient_info.get('gender'):
            patient_data.append([
                Paragraph("<b>Gender:</b>", self.styles['BodyText']),
                Paragraph(patient_info['gender'], self.styles['BodyText'])
            ])
        
        if patient_info.get('location'):
            patient_data.append([
                Paragraph("<b>Body Location:</b>", self.styles['BodyText']),
                Paragraph(patient_info['location'], self.styles['BodyText'])
            ])
        
        if patient_info.get('symptoms'):
            patient_data.append([
                Paragraph("<b>Symptoms:</b>", self.styles['BodyText']),
                Paragraph(patient_info['symptoms'], self.styles['BodyText'])
            ])
        
        if patient_data:
            patient_table = Table(patient_data, colWidths=[4*cm, 12*cm])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.BG_LIGHT_BLUE),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.TEXT_PRIMARY),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, self.PRIMARY_BLUE),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, self.BG_LIGHT_BLUE])
            ]))
            story.append(patient_table)
        
        story.append(Spacer(1, 0.4*cm))
        
        # ==========================================
        # CLINICAL IMAGE (if provided)
        # ==========================================
        
        if image_path and os.path.exists(image_path):
            section_header = Paragraph(
                "📸 Clinical Image", 
                self.styles['SectionHeader']
            )
            story.append(section_header)
            
            try:
                img = Image.open(image_path)
                
                # Resize to fit nicely
                max_width = 14*cm
                aspect = img.height / img.width
                img_width = max_width
                img_height = max_width * aspect
                
                if img_height > 12*cm:
                    img_height = 12*cm
                    img_width = img_height / aspect
                
                # Center image with border
                rl_img = RLImage(image_path, width=img_width, height=img_height)
                
                # Add image with padding
                story.append(Spacer(1, 0.2*cm))
                story.append(rl_img)
                story.append(Spacer(1, 0.2*cm))
                
                # Caption
                caption = Paragraph(
                    "<i>Clinical photograph for dermatological assessment</i>",
                    self.styles['BodyText']
                )
                story.append(caption)
                
            except Exception as e:
                error_para = Paragraph(
                    f"<i>Image could not be loaded: {str(e)}</i>",
                    self.styles['BodyText']
                )
                story.append(error_para)
        
        story.append(Spacer(1, 0.4*cm))
        
        # ==========================================
        # AI ANALYSIS (Main content)
        # ==========================================
        
        section_header = Paragraph(
            "🔬 Dermatological Assessment", 
            self.styles['SectionHeader']
        )
        story.append(section_header)
        
        # Parse AI response by sections
        analysis_sections = self._parse_ai_response(ai_response)
        
        for section_num, section_title, section_content in analysis_sections:
            # Subsection header
            subsection = Paragraph(
                f"<b>{section_num}. {section_title}</b>",
                self.styles['Subsection']
            )
            story.append(subsection)
            
            # Content
            # Check if it's a list
            if '•' in section_content or '\n-' in section_content or '\n*' in section_content:
                # Split into bullet points
                lines = section_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Remove bullet markers
                        line = line.lstrip('•-*').strip()
                        if line:
                            bullet = Paragraph(
                                f"• {line}",
                                self.styles['BulletPoint']
                            )
                            story.append(bullet)
            else:
                # Regular paragraph
                content_para = Paragraph(section_content, self.styles['BodyText'])
                story.append(content_para)
            
            story.append(Spacer(1, 0.3*cm))
        
        # If no sections parsed, just output raw
        if not analysis_sections:
            formatted_response = ai_response.replace('\n', '<br/>')
            full_analysis = Paragraph(formatted_response, self.styles['BodyText'])
            story.append(full_analysis)
        
        story.append(Spacer(1, 0.5*cm))
        
        # ==========================================
        # MEDICAL DISCLAIMER (Premium Warning Box)
        # ==========================================
        
        disclaimer_text = """
        <b><font size="12">⚠️ IMPORTANT MEDICAL DISCLAIMER</font></b><br/><br/>
        
        <b>Educational Purpose Only:</b> This report is generated by an artificial intelligence 
        system (Google MedGemma 1.5 4B) for <b>educational and preliminary screening purposes only</b>. 
        It does NOT constitute professional medical advice, diagnosis, or treatment.<br/><br/>
        
        <b>Professional Consultation Required:</b> You should ALWAYS consult a qualified dermatologist 
        or healthcare provider for accurate diagnosis and appropriate treatment. Do not rely solely 
        on this AI-generated assessment for medical decisions.<br/><br/>
        
        <b>Recommended Action:</b> Use this report as a reference tool to facilitate discussion 
        with your healthcare provider. If you have any concerns about your skin condition, 
        please seek professional medical evaluation immediately.<br/><br/>
        
        <b>Limitations:</b> AI analysis may not detect all conditions and can make errors. 
        Clinical examination by a qualified physician is essential for proper diagnosis.
        """
        
        disclaimer = Paragraph(disclaimer_text, self.styles['WarningBox'])
        story.append(disclaimer)
        
        # ==========================================
        # BUILD PDF
        # ==========================================
        
        doc.build(
            story,
            onFirstPage=self._draw_header_footer,
            onLaterPages=self._draw_header_footer
        )
        
        return output_path
    
    def _parse_ai_response(self, text):
        """
        Parse AI response into structured sections
        Returns: List of (section_num, title, content) tuples
        """
        import re
        
        sections = []
        
        # Pattern: **1. Title:** or **1. Title**
        pattern = r'\*{0,2}(\d+)\.\s*([^:*\n]+)[\*:]*\s*'
        
        parts = re.split(pattern, text)
        
        # parts[0] might be intro text, then alternates: num, title, content, num, title, content...
        if len(parts) > 3:
            for i in range(1, len(parts), 3):
                if i+2 < len(parts):
                    num = parts[i]
                    title = parts[i+1].strip()
                    content = parts[i+2].strip()
                    sections.append((num, title, content))
        
        return sections


# Convenience function
def generate_premium_pdf(
    output_path: str,
    patient_info: dict,
    image_path: str = None,
    ai_response: str = ""
) -> str:
    """
    Quick function to generate premium PDF report
    
    Usage:
        pdf_path = generate_premium_pdf(
            output_path="/tmp/report.pdf",
            patient_info={
                'age': 28,
                'gender': 'Female',
                'location': 'Legs',
                'symptoms': 'Red itchy bumps around hair follicles'
            },
            image_path="/path/to/image.jpg",
            ai_response="Full AI diagnosis text..."
        )
    """
    generator = PremiumMedicalPDF()
    return generator.generate_premium_report(
        output_path=output_path,
        patient_info=patient_info,
        image_path=image_path,
        ai_response=ai_response
    )


if __name__ == "__main__":
    # Test premium PDF
    print("🧪 Testing Premium PDF Generator...")
    
    test_response = """
**1. Primary Assessment (Most Likely Condition):**

Based on the image, the most likely condition is **Folliculitis**. This is an inflammation 
of the hair follicles, often caused by bacteria (like Staphylococcus aureus) or fungi.

**2. Key Visual Features Observed:**

• **Small, red bumps:** These are characteristic of inflammation around hair follicles.
• **Pus-filled bumps:** The presence of white dots/pus in the center of the bumps indicates 
  the presence of pus, a sign of infection.
• **Location:** The bumps are located around hair follicles, which is typical for folliculitis.
• **Redness:** The surrounding skin is red, indicating inflammation.

**3. Differential Diagnoses:**

• **Acne:** While acne can present with red bumps and pus-filled lesions, it typically 
  occurs in areas with higher sebum production (face, chest, back).
• **Insect Bites:** Insect bites can cause red bumps and itching, but they are usually 
  more localized and less uniformly distributed.

**4. Red Flags Requiring Immediate Attention:**

• **Severe pain or swelling:** If the bumps are extremely painful or the affected area 
  is significantly swollen, it warrants immediate medical attention.
• **Rapidly spreading rash:** If the lesions are spreading quickly over a large area.
• **Systemic symptoms:** If accompanied by fever, chills, or other signs of a systemic infection.

**5. Recommended Next Steps and Urgency Level:**

**Urgency Level:** Low to Moderate

**Next Steps:**
• **Consult a Dermatologist:** A dermatologist can confirm the diagnosis and recommend 
  appropriate treatment.
• **Cleanliness:** Maintain good hygiene, such as washing the affected area regularly.
• **Topical Treatments:** Over-the-counter or prescription topical antibiotics or 
  antifungal creams may be recommended.
    """
    
    output = "/tmp/premium_medical_report.pdf"
    
    result = generate_premium_pdf(
        output_path=output,
        patient_info={
            'age': 28,
            'gender': 'Female',
            'location': 'Legs',
            'symptoms': 'Small pus-filled bumps around hair follicles, itching for 1 week'
        },
        image_path=None,
        ai_response=test_response
    )
    
    print(f"✅ Premium PDF generated: {result}")
    print(f"📄 Open with: xdg-open {result}")
