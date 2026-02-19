"""
PDF Medical Report Generator for DermaCheck AI
Generates professional medical reports with embedded images and diagnosis
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image
from datetime import datetime
import io
import os


class MedicalReportGenerator:
    """
    Professional PDF report generator for dermatology analysis
    
    Features:
    - Header with branding
    - Patient information section
    - Embedded medical image
    - Primary diagnosis with confidence score
    - Differential diagnoses
    - Red flags and recommendations
    - Medical disclaimer
    """
    
    def __init__(self):
        self.page_width = A4[0]
        self.page_height = A4[1]
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for medical report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#3b82f6'),
            borderPadding=6,
            backColor=colors.HexColor('#eff6ff')
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=16
        ))
        
        # Diagnosis style
        self.styles.add(ParagraphStyle(
            name='Diagnosis',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(
        self, 
        output_path: str,
        patient_info: dict,
        image_path: str,
        diagnosis_data: dict,
        ai_response: str
    ) -> str:
        """
        Generate complete PDF medical report
        
        Args:
            output_path: Path to save PDF
            patient_info: Dict with patient details (age, gender, location, symptoms)
            image_path: Path to uploaded medical image
            diagnosis_data: Dict with parsed diagnosis info
            ai_response: Full AI response text
        
        Returns:
            Path to generated PDF
        """
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Container for PDF elements
        story = []
        
        # 1. Header
        story.extend(self._create_header())
        
        # 2. Patient Information
        story.extend(self._create_patient_section(patient_info))
        
        # 3. Medical Image
        if image_path and os.path.exists(image_path):
            story.extend(self._create_image_section(image_path))
        
        # 4. Primary Diagnosis
        story.extend(self._create_diagnosis_section(diagnosis_data))
        
        # 5. AI Analysis Details
        story.extend(self._create_analysis_section(ai_response))
        
        # 6. Disclaimer
        story.extend(self._create_disclaimer())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_header(self):
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph("🏥 DermaCheck AI", self.styles['CustomTitle'])
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph(
            "<b>Medical Dermatology Analysis Report</b><br/>"
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            self.styles['Normal']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _create_patient_section(self, patient_info):
        """Create patient information section"""
        elements = []
        
        # Section header
        header = Paragraph("📋 Patient Information", self.styles['SectionHeader'])
        elements.append(header)
        
        # Patient details table
        data = []
        
        if patient_info.get('age'):
            data.append(['Age:', f"{patient_info['age']} years"])
        
        if patient_info.get('gender'):
            data.append(['Gender:', patient_info['gender']])
        
        if patient_info.get('location'):
            data.append(['Body Location:', patient_info['location']])
        
        if patient_info.get('symptoms'):
            data.append(['Symptoms:', patient_info['symptoms']])
        
        if data:
            table = Table(data, colWidths=[3*cm, 12*cm])
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
                ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_image_section(self, image_path):
        """Embed medical image in report"""
        elements = []
        
        # Section header
        header = Paragraph("📸 Clinical Image", self.styles['SectionHeader'])
        elements.append(header)
        
        try:
            # Load and resize image
            img = Image.open(image_path)
            
            # Calculate dimensions (max width 12cm, maintain aspect ratio)
            max_width = 12*cm
            aspect = img.height / img.width
            img_width = max_width
            img_height = max_width * aspect
            
            # If too tall, limit height
            if img_height > 10*cm:
                img_height = 10*cm
                img_width = img_height / aspect
            
            # Add image to PDF
            rl_img = RLImage(image_path, width=img_width, height=img_height)
            elements.append(rl_img)
            
        except Exception as e:
            error_text = Paragraph(
                f"<i>Error loading image: {str(e)}</i>",
                self.styles['BodyText']
            )
            elements.append(error_text)
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_diagnosis_section(self, diagnosis_data):
        """Create diagnosis section with confidence scores"""
        elements = []
        
        # Section header
        header = Paragraph("🔬 Diagnostic Assessment", self.styles['SectionHeader'])
        elements.append(header)
        
        # Primary diagnosis
        primary = diagnosis_data.get('primary', {})
        if primary:
            primary_text = f"""
            <b>Primary Diagnosis:</b> {primary.get('diagnosis', 'Not specified')}<br/>
            <b>Confidence Level:</b> {primary.get('confidence', 0)}%<br/>
            <b>Rationale:</b> {primary.get('rationale', 'Not provided')}
            """
            elements.append(Paragraph(primary_text, self.styles['BodyText']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Differential diagnoses
        differentials = diagnosis_data.get('differentials', [])
        if differentials:
            diff_header = Paragraph("<b>Differential Diagnoses:</b>", self.styles['Diagnosis'])
            elements.append(diff_header)
            
            for i, diff in enumerate(differentials, 1):
                diff_text = f"""
                {i}. <b>{diff.get('diagnosis', 'Unknown')}</b> 
                (Confidence: {diff.get('confidence', 0)}%)<br/>
                   {diff.get('rationale', '')}
                """
                elements.append(Paragraph(diff_text, self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        # Red flags
        red_flags = diagnosis_data.get('red_flags', [])
        if red_flags:
            flag_header = Paragraph("🚨 Red Flags / Important Considerations:", self.styles['SectionHeader'])
            elements.append(flag_header)
            
            for flag in red_flags:
                flag_text = f"• {flag}"
                elements.append(Paragraph(flag_text, self.styles['BodyText']))
            
            elements.append(Spacer(1, 0.15*inch))
        
        # Recommendations
        recommendations = diagnosis_data.get('recommendations', '')
        if recommendations:
            rec_header = Paragraph("💡 Recommendations:", self.styles['SectionHeader'])
            elements.append(rec_header)
            elements.append(Paragraph(recommendations, self.styles['BodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_analysis_section(self, ai_response):
        """Create detailed AI analysis section"""
        elements = []
        
        # Section header
        header = Paragraph("📄 Detailed AI Analysis", self.styles['SectionHeader'])
        elements.append(header)
        
        # Format AI response (preserve line breaks)
        formatted_response = ai_response.replace('\n', '<br/>')
        analysis = Paragraph(formatted_response, self.styles['BodyText'])
        elements.append(analysis)
        
        elements.append(Spacer(1, 0.2*inch))
        return elements
    
    def _create_disclaimer(self):
        """Create medical disclaimer footer"""
        elements = []
        
        disclaimer_text = """
        <b>⚠️ MEDICAL DISCLAIMER</b><br/><br/>
        This report is generated by an AI system (MedGemma 1.5) for <b>educational 
        and preliminary screening purposes only</b>. It does NOT constitute professional 
        medical advice, diagnosis, or treatment.<br/><br/>
        
        <b>Important:</b> Always consult a qualified dermatologist or healthcare provider 
        for accurate diagnosis and appropriate treatment. Do not rely solely on this 
        AI-generated assessment for medical decisions.<br/><br/>
        
        This report should be used as a reference tool to facilitate discussion with 
        your healthcare provider, not as a replacement for professional medical evaluation.
        """
        
        disclaimer_style = ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#78350f'),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=12,
            backColor=colors.HexColor('#fef3c7'),
            borderWidth=1,
            borderColor=colors.HexColor('#f59e0b'),
            borderPadding=12,
            borderRadius=4
        )
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        return elements


# Convenience function
def generate_medical_pdf(
    output_path: str,
    patient_info: dict,
    image_path: str,
    diagnosis_data: dict,
    ai_response: str
) -> str:
    """
    Quick function to generate medical report PDF
    
    Usage:
        pdf_path = generate_medical_pdf(
            output_path="/tmp/report.pdf",
            patient_info={
                'age': 28,
                'gender': 'Female',
                'location': 'Legs',
                'symptoms': 'Red itchy bumps'
            },
            image_path="/path/to/skin_photo.jpg",
            diagnosis_data={
                'primary': {
                    'diagnosis': 'Folliculitis',
                    'confidence': 85,
                    'rationale': 'Characteristic red bumps...'
                },
                'differentials': [
                    {'diagnosis': 'Acne', 'confidence': 65, 'rationale': '...'}
                ],
                'red_flags': ['Monitor for spreading'],
                'recommendations': 'Consult dermatologist'
            },
            ai_response="Full AI response text..."
        )
    """
    generator = MedicalReportGenerator()
    return generator.generate_report(
        output_path=output_path,
        patient_info=patient_info,
        image_path=image_path,
        diagnosis_data=diagnosis_data,
        ai_response=ai_response
    )


if __name__ == "__main__":
    # Test PDF generation
    print("🧪 Testing PDF generator...")
    
    test_data = {
        'patient_info': {
            'age': 28,
            'gender': 'Female',
            'location': 'Legs',
            'symptoms': 'Small red bumps around hair follicles, itchy'
        },
        'diagnosis_data': {
            'primary': {
                'diagnosis': 'Folliculitis',
                'confidence': 92,
                'rationale': 'Red bumps with white centers around hair follicles'
            },
            'differentials': [
                {'diagnosis': 'Acne Vulgaris', 'confidence': 65, 'rationale': 'Similar presentation'},
                {'diagnosis': 'Bacterial Infection', 'confidence': 45, 'rationale': 'Less likely'}
            ],
            'red_flags': ['Monitor for spreading', 'Check for fever'],
            'recommendations': 'Topical antibiotic cream, warm compress'
        },
        'ai_response': 'This is a test AI response showing folliculitis diagnosis.'
    }
    
    output = "/tmp/test_medical_report.pdf"
    
    result = generate_medical_pdf(
        output_path=output,
        patient_info=test_data['patient_info'],
        image_path=None,  # No test image
        diagnosis_data=test_data['diagnosis_data'],
        ai_response=test_data['ai_response']
    )
    
    print(f"✅ PDF generated: {result}")
    print(f"📄 Open with: xdg-open {result}")
