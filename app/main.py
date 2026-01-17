"""
DermaCheck AI - Main Streamlit Application
AI-Powered Dermatology Screening Platform
"""
import streamlit as st
from PIL import Image
import os
from datetime import datetime

# Import custom modules
from models.abcde_analyzer import ABCDEAnalyzer
from models.medgemma_client import MedGemmaClient
from models.symptom_analyzer import SymptomAnalyzer
from utils.timeline_manager import TimelineManager
from utils.image_utils import (
    validate_image, preprocess_image, create_comparison_view,
    add_size_reference
)
from utils.config import Config

# Page configuration
st.set_page_config(
    page_title="DermaCheck AI - Dermatology Screening",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS styling"""
    css_path = os.path.join("assets", "css", "styles_premium.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback to regular styles if premium not found
        css_path_fallback = os.path.join("assets", "css", "styles.css")
        if os.path.exists(css_path_fallback):
            with open(css_path_fallback) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if 'timeline_manager' not in st.session_state:
    st.session_state.timeline_manager = TimelineManager()

if 'abcde_analyzer' not in st.session_state:
    st.session_state.abcde_analyzer = ABCDEAnalyzer()

if 'medgemma_client' not in st.session_state:
    try:
        st.session_state.medgemma_client = MedGemmaClient()
    except ValueError as e:
        st.session_state.medgemma_client = None
        st.warning(f"⚠️ Med-Gemma unavailable: {e}. Please configure GOOGLE_API_KEY in .env file.")

if 'symptom_analyzer' not in st.session_state:
    try:
        st.session_state.symptom_analyzer = SymptomAnalyzer()
    except ValueError as e:
        st.session_state.symptom_analyzer = None

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

if 'current_consultation' not in st.session_state:
    st.session_state.current_consultation = None


def main():
    """Main application function"""
    
    # Header
    st.markdown("<h1>🩺 DermaCheck AI</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>AI-Powered Skin Health Screening & Lesion Tracking</p>",
        unsafe_allow_html=True
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio(
            "Select Feature",
            ["🏠 New Analysis", "💬 General Consultation", "📊 Timeline Tracking", "📚 Education", "ℹ️ About"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Summary stats
        if st.session_state.timeline_manager:
            stats = st.session_state.timeline_manager.get_summary_stats()
            st.markdown("### Your Dashboard")
            st.metric("Tracked Lesions", stats['total_lesions'])
            st.metric("Total Scans", stats['total_entries'])
            
            if stats['total_lesions'] > 0:
                st.markdown("**Risk Distribution:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"🟢 {stats['risk_distribution']['low']}")
                with col2:
                    st.markdown(f"🟡 {stats['risk_distribution']['medium']}")
                with col3:
                    st.markdown(f"🔴 {stats['risk_distribution']['high']}")
    
    # Route to selected page
    if "New Analysis" in page:
        page_new_analysis()
    elif "General Consultation" in page:
        page_general_consultation()
    elif "Timeline" in page:
        page_timeline_tracking()
    elif "Education" in page:
        page_education()
    else:
        page_about()
    
    # Footer disclaimer
    st.markdown("---")
    st.markdown(
        """
        <div class='disclaimer'>
            <div class='disclaimer-title'>⚠️ Medical Disclaimer</div>
            <p>
                <strong>DermaCheck AI is a screening tool, not a diagnostic device.</strong>
                Results are preliminary and for educational purposes only. This tool does NOT replace
                professional medical advice, diagnosis, or treatment. Always consult a qualified 
                healthcare provider for medical concerns. Do not use as the sole basis for medical decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def page_new_analysis():
    """New lesion analysis page"""
    st.markdown("## 📸 New Skin Lesion Analysis")
    
    # Upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload a photo of the skin lesion",
            type=['jpg', 'jpeg', 'png'],
            help="Take a well-lit, focused photo of the lesion. Include a reference object (like a ruler) if possible."
        )
    
    with col2:
        st.markdown("### 📋 Tips for Best Results")
        st.markdown("""
        - Use good lighting
        - Keep camera steady
        - Fill the frame
        - Include size reference
        - Avoid shadows
        """)
    
    if uploaded_file:
        # Validate image
        is_valid, message = validate_image(uploaded_file)
        
        if is_valid:
            # Display uploaded image
            image = Image.open(uploaded_file)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(image, caption="Uploaded Image", use_container_width=True)
            
            with col2:
                # Additional context
                st.markdown("### Additional Information (Optional)")
                body_location = st.selectbox(
                    "Body Location",
                    ["Select...", "Face", "Scalp", "Neck", "Chest", "Back", 
                     "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Other"]
                )
                
                is_existing = st.checkbox("This is a follow-up photo of an existing lesion")
                
                existing_lesion_id = None
                if is_existing:
                    lesions = st.session_state.timeline_manager.get_all_lesions()
                    if lesions:
                        lesion_options = {
                            f"{l['lesion_id']} ({l['body_location']})": l['lesion_id']
                            for l in lesions
                        }
                        selected = st.selectbox("Select Lesion", list(lesion_options.keys()))
                        existing_lesion_id = lesion_options[selected]
                    else:
                        st.info("No existing lesions found. This will be saved as a new lesion.")
            
            # Analyze button
            if st.button("🔍 Analyze Lesion", type="primary", use_container_width=True):
                with st.spinner("Analyzing lesion... This may take a moment."):
                    perform_analysis(image, body_location, existing_lesion_id)
            
            # Display results if available
            if st.session_state.current_analysis:
                display_analysis_results(st.session_state.current_analysis)
        
        else:
            st.error(f"❌ {message}")


def perform_analysis(image, body_location, existing_lesion_id=None):
    """Perform ABCDE analysis and Med-Gemma interpretation"""
    
    # Get previous data for evolution scoring
    previous_data = None
    if existing_lesion_id:
        prev_entry = st.session_state.timeline_manager.get_latest_entry(existing_lesion_id)
        if prev_entry:
            previous_data = {
                'lesion_area': prev_entry['lesion_area'],
                'mean_color': [0, 0, 0]  # Placeholder - would need to store this
            }
    
    # Run ABCDE analysis
    abcde_results = st.session_state.abcde_analyzer.analyze(image, previous_data)
    
    # Get Med-Gemma interpretation
    medgemma_results = None
    if st.session_state.medgemma_client:
        medgemma_results = st.session_state.medgemma_client.analyze_skin_lesion(abcde_results)
    
    # Save to timeline
    if body_location != "Select...":
        lesion_id = st.session_state.timeline_manager.add_lesion_entry(
            image, abcde_results, body_location.lower().replace(" ", "_"), existing_lesion_id
        )
    else:
        lesion_id = None
    
    # Store results in session
    st.session_state.current_analysis = {
        'abcde_results': abcde_results,
        'medgemma_results': medgemma_results,
        'image': image,
        'lesion_id': lesion_id,
        'body_location': body_location
    }


def display_analysis_results(analysis):
    """Display analysis results with premium UI"""
    
    abcde = analysis['abcde_results']
    medgemma = analysis['medgemma_results']
    
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Risk level card
    risk_level = abcde['risk_level']
    total_score = abcde['total_score']
    
    risk_class = f"risk-{risk_level.lower()}"
    risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}[risk_level]
    
    st.markdown(
        f"""
        <div class='risk-card {risk_class}'>
            <h2>{risk_emoji} {risk_level} RISK</h2>
            <p style='font-size: 1.2rem; margin: 0;'>ABCDE Score: <strong>{total_score}/11</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ABCDE Breakdown
    st.markdown("### ABCDE Criteria Breakdown")
    
    cols = st.columns(5)
    criteria = ['asymmetry', 'border', 'color', 'diameter', 'evolution']
    letters = ['A', 'B', 'C', 'D', 'E']
    names = ['Asymmetry', 'Border', 'Color', 'Diameter', 'Evolution']
    max_scores = [2, 2, 2, 2, 3]
    
    for i, (col, criterion, letter, name, max_score) in enumerate(zip(cols, criteria, letters, names, max_scores)):
        with col:
            score = abcde['abcde_scores'][criterion]
            desc = abcde['descriptions'][criterion]
            
            st.markdown(
                f"""
                <div class='criteria-card'>
                    <div class='criteria-letter'>{letter}</div>
                    <div class='criteria-name'>{name}</div>
                    <div class='criteria-score'>{score}/{max_score}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            with st.expander("Details"):
                st.write(desc)
    
    # Med-Gemma Interpretation
    if medgemma:
        st.markdown("---")
        st.markdown("### 🤖 AI Medical Interpretation")
        
        # Triage recommendation
        st.markdown(
            f"""
            <div class='info-box'>
                <strong>Recommended Action:</strong><br>
                {medgemma['triage_action']}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Full interpretation
        with st.expander("📖 View Detailed Interpretation", expanded=True):
            st.markdown(medgemma['interpretation'])
    
    # Save confirmation
    if analysis['lesion_id']:
        st.success(f"✅ Analysis saved to timeline (ID: {analysis['lesion_id']})")


def page_timeline_tracking():
    """Timeline tracking page"""
    st.markdown("## 📊 Lesion Timeline Tracking")
    
    lesions = st.session_state.timeline_manager.get_all_lesions()
    
    if not lesions:
        st.info("📭 No lesions tracked yet. Upload a new image to get started!")
        return
    
    # Lesion selector
    lesion_options = {
        f"{l['lesion_id']} - {l['body_location'].replace('_', ' ').title()}": l
        for l in lesions
    }
    
    selected_name = st.selectbox("Select Lesion to View", list(lesion_options.keys()))
    selected_lesion = lesion_options[selected_name]
    
    # Display timeline
    timeline = selected_lesion['timeline']
    
    st.markdown(f"### {selected_lesion['body_location'].replace('_', ' ').title()}")
    st.markdown(f"**Total scans:** {len(timeline)}")
    st.markdown(f"**First seen:** {datetime.fromisoformat(timeline[0]['timestamp']).strftime('%Y-%m-%d')}")
    st.markdown(f"**Last updated:** {datetime.fromisoformat(timeline[-1]['timestamp']).strftime('%Y-%m-%d')}")
    
    # Timeline visualization
    st.markdown("---")
    st.markdown("### Timeline")
    
    for i, entry in enumerate(reversed(timeline)):
        col1, col2, col3 = st.columns([1, 2, 2])
        
        with col1:
            st.markdown(f"**#{len(timeline) - i}**")
            st.markdown(datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d'))
        
        with col2:
            if os.path.exists(entry['image_path']):
                img = Image.open(entry['image_path'])
                st.image(img, use_container_width=True)
        
        with col3:
            risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}[entry['risk_level']]
            st.markdown(f"{risk_color} **{entry['risk_level']} RISK**")
            st.markdown(f"**Score:** {entry['abcde_score']}/11")
            st.markdown(f"**Size:** {entry['size_mm']}mm")
        
        st.markdown("---")
    
    # Comparison view
    if len(timeline) >= 2:
        st.markdown("### 🔀 Progression Comparison")
        
        comparison = st.session_state.timeline_manager.compare_entries(selected_lesion['lesion_id'])
        
        if comparison:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Earlier Scan**")
                if os.path.exists(comparison['entry1']['image_path']):
                    st.image(Image.open(comparison['entry1']['image_path']))
                st.markdown(f"Date: {datetime.fromisoformat(comparison['entry1']['timestamp']).strftime('%Y-%m-%d')}")
                st.markdown(f"Score: {comparison['entry1']['abcde_score']}/11")
            
            with col2:
                st.markdown("**Recent Scan**")
                if os.path.exists(comparison['entry2']['image_path']):
                    st.image(Image.open(comparison['entry2']['image_path']))
                st.markdown(f"Date: {datetime.fromisoformat(comparison['entry2']['timestamp']).strftime('%Y-%m-%d')}")
                st.markdown(f"Score: {comparison['entry2']['abcde_score']}/11")
            
            # Change summary
            changes = comparison['changes']
            st.markdown(f"**Time elapsed:** {comparison['time_elapsed_days']} days")
            st.markdown(f"**Size change:** {changes['size_percent']:+.1f}%")
            st.markdown(f"**Score change:** {changes['score']:+d} points")
            
            # Alerts
            if comparison['alert']:
                for alert in comparison['alert']['alerts']:
                    st.warning(f"⚠️ {alert['message']}")
                st.info(f"💡 {comparison['alert']['recommendation']}")


def page_education():
    """Education page"""
    st.markdown("## 📚 Skin Health Education")
    
    st.markdown("""
    ### Understanding ABCDE Criteria for Melanoma
    
    The ABCDE method is a clinical standard for identifying suspicious moles and skin lesions:
    """)
    
    with st.expander("A - Asymmetry"):
        st.markdown("""
        **What it means:** One half of the mole doesn't match the other half.
        
        **Why it matters:** Most benign moles are symmetrical. Asymmetry can indicate irregular growth patterns.
        
        **Normal:** Round or oval, symmetric
        **Warning:** Irregular, one side different from other
        """)
    
    with st.expander("B - Border"):
        st.markdown("""
        **What it means:** The edges are irregular, ragged, notched, or blurred.
        
        **Why it matters:** Benign moles usually have smooth, even borders. Irregular borders suggest uncontrolled growth.
        
        **Normal:** Smooth, well-defined edges
        **Warning:** Fuzzy, scalloped, or notched edges
        """)
    
    with st.expander("C - Color"):
        st.markdown("""
        **What it means:** The color is not uniform and may include shades of brown, black, tan, red, white, or blue.
        
        **Why it matters:** Varied colors indicate different types of cells and growth patterns.
        
        **Normal:** Single, uniform color
        **Warning:** Multiple colors or uneven distribution
        """)
    
    with st.expander("D - Diameter"):
        st.markdown("""
        **What it means:** The lesion is larger than 6mm (size of a pencil eraser).
        
        **Why it matters:** While melanomas can be smaller, lesions larger than 6mm warrant closer examination.
        
        **Normal:** Smaller than 6mm
        **Warning:** Larger than 6mm or growing
        """)
    
    with st.expander("E - Evolution"):
        st.markdown("""
        **What it means:** The mole is changing in size, shape, color, elevation, or showing new symptoms (bleeding, itching).
        
        **Why it matters:** Changes over time are among the most important warning signs.
        
        **Normal:** Stable over months/years
        **Warning:** Any change in size, shape, color, or symptoms
        """)
    
    st.markdown("---")
    st.markdown("""
    ### When to See a Dermatologist
    
    **Seek professional consultation if you notice:**
    - Any change in size, shape, or color
    - Bleeding, oozing, or crusting
    - Itching or tenderness
    - New growth with irregular features
    - Family history of melanoma
    
    **Remember:** Early detection saves lives! Regular skin self-exams and professional screenings are crucial.
    """)


def page_about():
    """About page"""
    st.markdown("## ℹ️ About DermaCheck AI")
    
    st.markdown("""
    ### What is DermaCheck AI?
    
    DermaCheck AI is an intelligent skin health screening platform that combines computer vision 
    and medical AI to help users monitor skin lesions and make informed decisions about seeking 
    professional care.
    
    ### How It Works
    
    1. **Image Analysis** - Upload a photo of a skin lesion
    2. **ABCDE Screening** - Automated assessment using clinical criteria
    3. **Risk Scoring** - Calculate melanoma risk level
    4. **AI Interpretation** - Med-Gemma provides medical context
    5. **Triage Guidance** - Clear recommendations on next steps
    6. **Timeline Tracking** - Monitor changes over time
    
    ### Technology Stack
    
    - **Vision Analysis:** Computer vision for lesion segmentation and feature extraction
    - **Medical AI:** Google Med-Gemma for medical reasoning
    - **Framework:** Streamlit for interactive web interface
    - **Deployment:** Kaggle Notebooks with GPU acceleration
    
    ### Built For
    
    **Google Med-Gemma Impact Challenge 2026**
    
    This project demonstrates the potential of AI to improve health literacy and early detection 
    of skin cancer through accessible screening tools.
    
    ### Important Notes
    
    - ✅ Educational screening tool
    - ✅ ABCDE criteria-based analysis
    - ✅ Progression tracking
    - ❌ NOT a medical diagnosis
    - ❌ NOT a substitute for professional care
    
    ### Contact & Support
    
    For questions or feedback, please visit our [GitHub repository](https://github.com/Jeonseol00/dermacheck-ai).
    """)
    
    st.markdown("---")
    st.markdown("**Version:** 2.0.0 | **Last Updated:** January 2026")


def page_general_consultation():
    """General symptom consultation page - Module B"""
    st.markdown("## 💬 General Health Consultation")
    
    st.markdown("""
    **Pre-Consultation Assistant** - Describe your symptoms in your own words.  
    Our AI will help organize your information for your doctor.
    """)
    
    if not st.session_state.symptom_analyzer:
        st.error("⚠️ Symptom analyzer unavailable. Please configure GOOGLE_API_KEY.")
        return
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Describe Your Symptoms")
        
        symptoms_input = st.text_area(
            "Tell us what you're experiencing",
            placeholder="Example: I've had a fever for 3 days, and there's a red rash on my left arm that itches. I also feel dizzy sometimes.",
            height=150,
            help="Describe your symptoms in your own words. Include when they started, where they are, and how severe."
        )
        
        # Optional patient context
        with st.expander("📋 Additional Information (Optional)"):
            col_a, col_b = st.columns(2)
            with col_a:
                age = st.number_input("Age", min_value=0, max_value=120, value=None, step=1)
                gender = st.selectbox("Gender", ["Select...", "Male", "Female", "Other", "Prefer not to say"])
            with col_b:
                medical_history = st.text_input(
                    "Existing conditions",
                    placeholder="Diabetes, hypertension, etc."
                )
        
        # Analyze button
        if st.button("📝 Generate Medical Summary", type="primary", use_container_width=True):
            if symptoms_input.strip():
                with st.spinner("Analyzing symptoms and generating SOAP note... This may take a moment."):
                    patient_context = {}
                    if age:
                        patient_context['age'] = age
                    if gender and gender != "Select...":
                        patient_context['gender'] = gender
                    if medical_history:
                        patient_context['medical_history'] = medical_history
                    
                    # Analyze symptoms
                    result = st.session_state.symptom_analyzer.analyze_symptoms(
                        symptoms_input,
                        patient_context if patient_context else None
                    )
                    
                    st.session_state.current_consultation = result
            else:
                st.warning("⚠️ Please describe your symptoms first.")
    
    with col2:
        st.markdown("### 💡 Tips")
        st.markdown("""
        **Include:**
        - What symptoms you have
        - When they started
        - Where on your body
        - How severe (mild/moderate/severe)
        - What makes it better/worse
        
        **Examples:**
        - "Headache for 2 days, behind eyes, worse with light"
        - "Stomach pain since yesterday, sharp, after eating"
        - "Rash on both legs, itchy, started 1 week ago"
        """)
    
    # Display results if available
    if st.session_state.current_consultation:
        display_consultation_results(st.session_state.current_consultation)


def display_consultation_results(consultation):
    """Display SOAP note and consultation results"""
    
    if consultation['status'] == 'error':
        st.error(f"❌ Error generating analysis: {consultation['raw_response']}")
        return
    
    st.markdown("---")
    st.markdown("## 📋 Medical Summary (SOAP Note)")
    
    st.info("""
    **For Healthcare Providers:** This AI-generated summary can help streamline your consultation.  
    **For Patients:** You can share this with your doctor to help explain your symptoms clearly.
    """)
    
    # Triage Level
    triage = consultation['triage']
    triage_colors = {
        'URGENT': 'red',
        'SEMI-URGENT': 'orange',
        'ROUTINE': 'yellow',
        'NON-URGENT': 'green'
    }
    
    triage_emojis = {
        'URGENT': '🚨',
        'SEMI-URGENT': '⚠️',
        'ROUTINE': '📅',
        'NON-URGENT': '✅'
    }
    
    triage_color = triage_colors.get(triage['level'], 'gray')
    triage_emoji = triage_emojis.get(triage['level'], '📋')
    
    st.markdown(
        f"""
        <div class='risk-card' style='border-left-color: {triage_color}; background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02))'>
            <h2>{triage_emoji} {triage['level']} Priority</h2>
            <p style='font-size: 1.1rem; margin: 0.5rem 0;'><strong>Recommendation:</strong> {triage['recommendation']}</p>
            <p style='font-size: 0.95rem; color: #94A3B8; margin: 0;'>{triage['reasoning']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # SOAP Note Sections
    soap = consultation['soap_note']
    
    # Subjective
    with st.expander("**S - SUBJECTIVE** (Patient's Description)", expanded=True):
        st.markdown(soap.get('subjective', 'No subjective data available'))
    
    # Objective
    with st.expander("**O - OBJECTIVE** (Physical Exam Findings)"):
        st.markdown(soap.get('objective', 'No objective data available'))
    
    # Assessment
    with st.expander("**A - ASSESSMENT** (Clinical Impression)", expanded=True):
        st.markdown(soap.get('assessment', 'No assessment available'))
    
    # Plan
    with st.expander("**P - PLAN** (Recommended Next Steps)", expanded=True):
        st.markdown(soap.get('plan', 'No plan available'))
    
    # Medical Entities Summary
    entities = consultation['medical_entities']
    
    if entities['symptoms'] or entities['duration'] or entities['red_flags']:
        st.markdown("---")
        st.markdown("### 🔍 Detected Key Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if entities['symptoms']:
                st.markdown("**Symptoms Mentioned:**")
                for symptom in entities['symptoms']:
                    st.markdown(f"- {symptom.title()}")
        
        with col2:
            if entities['duration']:
                st.markdown("**Duration:**")
                st.markdown(f"- {entities['duration']}")
        
        with col3:
            if entities['red_flags']:
                st.markdown("**⚠️ Red Flags:**")
                for flag in entities['red_flags']:
                    st.markdown(f"- {flag.title()}")
    
    # Disclaimer
    st.markdown("---")
    st.warning("""
    **⚠️ IMPORTANT MEDICAL DISCLAIMER:**
    
    This AI-generated summary is for **informational and organizational purposes only**.  
    It is **NOT** a medical diagnosis or treatment recommendation.
    
    - Always consult a qualified healthcare professional for medical advice
    - Do not delay seeking medical care based on this summary
    - If you have urgent symptoms, seek immediate medical attention
    - This tool is designed to help communicate with your doctor, not replace them
    """)
    
    # Export option
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**You can copy this summary to share with your healthcare provider**")
    
    with col2:
        # Future: Add PDF export button here
        st.button("📄 Export PDF", disabled=True, help="PDF export coming soon!")


if __name__ == "__main__":
    main()
