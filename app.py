# app.py
import streamlit as st
from PIL import Image
from utils.ai_utils import get_gemini_response
from utils.firebase_utils import (
    init_firebase,
    upload_image_to_storage,
    save_artisan_data,
)
from utils.image_utils import generate_enhanced_image
from utils.gcp_ai_utils import transcribe_audio, translate_text, get_image_labels
from st_audiorec import st_audiorec
from io import BytesIO
from utils.gdrive_utils import (
    get_gdrive_flow,
    get_gdrive_service_from_session,
    get_user_info,
    export_marketing_pack,
)
import time
import base64

# ==================== CONFIGURATION ====================
FAVICON_PATH = "assets/favicon.png"  # Update with your actual favicon path

st.set_page_config(
    page_title="KalaKarigar.ai - Empower Your Craft",
    page_icon=FAVICON_PATH,
    layout="wide",
    initial_sidebar_state="collapsed",  # Start collapsed for better mobile experience
)


# ==================== CUSTOM CSS STYLING ====================
def load_custom_css():
    st.markdown(
        """
    <style>
    /* Theme Variables */
    :root {
        --primary: #667eea;
        --primary-dark: #5a67d8;
        --secondary: #764ba2;
        --accent: #FFE66D;
        --success: #4CAF50;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F7FAFC;
        --card-bg: #FFFFFF;
        --border-color: #E2E8F0;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --text-primary: #F7FAFC;
            --text-secondary: #CBD5E0;
            --bg-primary: #0E1117;
            --bg-secondary: #1A202C;
            --card-bg: #2D3748;
            --border-color: #4A5568;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.2), 0 1px 2px 0 rgba(0, 0, 0, 0.12);
            --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
        }
    }
    
    /* Fix toolbar z-index issue */
    .stApp > header {
        z-index: 999 !important;
    }
    
    /* Main container adjustments */
    .main > div {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Hide Streamlit branding but keep header accessible */
    #MainMenu {visibility: ;}
    footer {visibility: hidden;}
    
    /* Custom Container Styling */
    .main-container {
        padding: 2rem;
        background: var(--card-bg);
        border-radius: 12px;
        box-shadow: var(--shadow);
        margin: 1rem 0 2rem 0;
        border: 1px solid var(--border-color);
    }
    
    /* Progress Indicator Container */
    .progress-container {
        text-align: center;
        margin: 1.5rem 0 2rem 0;
        padding: 1rem;
        background: var(--bg-secondary);
        border-radius: 12px;
    }
    
    .progress-inner {
        display: inline-flex;
        align-items: center;
        gap: 0;
    }
    
    .progress-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .progress-step {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: #E2E8F0;
        color: #A0AEC0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .progress-step.active {
        background: var(--bg-gradient);
        color: white;
        transform: scale(1.1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .progress-step.completed {
        background: var(--success);
        color: white;
    }
    
    .progress-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-secondary);
    }
    
    .progress-label.active {
        color: var(--primary);
        font-weight: 600;
    }
    
    .progress-label.completed {
        color: var(--success);
    }
    
    .progress-connector {
        width: 60px;
        height: 2px;
        background: #E2E8F0;
        margin: 0 -8px;
        align-self: center;
        margin-bottom: 1.5rem;
    }
    
    .progress-connector.completed {
        background: var(--success);
    }
    
    /* Card Styling */
    .feature-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    /* Button Styling */
    .stButton > button {
        background: var(--bg-gradient);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Success Message Styling */
    .success-message {
        background: linear-gradient(135deg, #48BB78, #38A169);
        color: white;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .success-message h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.5rem;
    }
    
    .success-message p {
        margin: 0;
        opacity: 0.95;
    }
    
    /* Logo Container */
    .logo-container {
        text-align: center;
        margin: 1rem 0;
    }
    
    .logo-image {
        max-width: 200px;
        height: auto;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-container {
            padding: 1rem;
            margin: 0.5rem 0 1rem 0;
        }
        
        .progress-inner {
            flex-direction: column;
            gap: 1rem;
        }
        
        .progress-connector {
            width: 2px;
            height: 40px;
            margin: -8px 0;
        }
        
        .logo-image {
            max-width: 150px;
        }
        
        .stButton > button {
            padding: 0.6rem 1rem;
            font-size: 0.9rem;
        }
    }
    
    /* Fix sidebar z-index */
    section[data-testid="stSidebar"] {
        z-index: 998 !important;
        background: var(--bg-secondary);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--primary);
    }
    
    /* Text input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
    }
    
    /* User info display */
    .user-info {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.75rem;
        background: var(--bg-secondary);
        border-radius: 12px;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--bg-gradient);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        margin-bottom: 0.25rem;
    }
    
    .user-name {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_logo():
    """Render the responsive logo with fallback"""
    try:
        # Try to load desktop logo
        with open("assets/logo_desktop.png", "rb") as f:
            logo_desktop_data = base64.b64encode(f.read()).decode()

        # Try to load mobile logo
        with open("assets/logo_mobile.png", "rb") as f:
            logo_mobile_data = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            .desktop-logo {{ display: block; margin: 0 auto; }}
            .mobile-logo {{ display: none; }}
            @media (max-width: 768px) {{
                .desktop-logo {{ display: none; }}
                .mobile-logo {{ display: block; margin: 0 auto; }}
            }}
            </style>
            <div class="logo-container">
                <img src="data:image/png;base64,{logo_desktop_data}" class="desktop-logo logo-image" alt="KalaKarigar.ai">
                <img src="data:image/png;base64,{logo_mobile_data}" class="mobile-logo logo-image" alt="KalaKarigar.ai">
            </div>
            """,
            unsafe_allow_html=True,
        )
    except:
        # Fallback to text logo if images not found
        st.markdown(
            """
            <div class="logo-container">
                <h2 style="color: var(--primary); margin: 0;">🎨 KalaKarigar.ai</h2>
                <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">Empower Your Craft with AI</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================== INITIALIZATION ====================
@st.cache_resource
def initialize_services():
    """Initialize Firebase and other services"""
    try:
        init_firebase()
        return True
    except Exception as e:
        st.error(f"⚠️ Failed to initialize services: {e}")
        return False


# ==================== SESSION STATE MANAGEMENT ====================
class SessionState:
    """Centralized session state management"""

    @staticmethod
    def init():
        """Initialize all session state variables"""
        defaults = {
            "gdrive_credentials": None,
            "user_profile": None,
            "page": "Onboarding",
            "artisan_data": {
                "craft_type": "",
                "description": "",
                "materials": "",
                "dimensions": "",
                "tags": [],
            },
            "product_image": None,
            "uploaded_file_name": "",
            "generated_content": None,
            "enhanced_image": None,
            "transcribed_text": None,
            "suggested_tags": None,
            "current_step": 1,
            "steps_completed": [],
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


# ==================== HELPER FUNCTIONS ====================
def change_page(page_name, step_number):
    """Change page with step tracking"""
    st.session_state.page = page_name
    st.session_state.current_step = step_number
    if step_number not in st.session_state.steps_completed:
        st.session_state.steps_completed.append(step_number)


def render_progress_indicator():
    """Render visual progress indicator"""
    steps = [
        ("1", "Details", 1),
        ("2", "Content", 2),
        ("3", "Enhance", 3),
        ("4", "Export", 4),
    ]

    html = '<div class="progress-container"><div class="progress-inner">'

    for i, (num, label, step) in enumerate(steps):
        is_active = st.session_state.current_step == step
        is_completed = step in st.session_state.steps_completed and not is_active

        step_class = "active" if is_active else "completed" if is_completed else ""
        label_class = "active" if is_active else "completed" if is_completed else ""

        html += f"""
        <div class="progress-item">
            <div class="progress-step {step_class}">{num}</div>
            <div class="progress-label {label_class}">{label}</div>
        </div>
        """

        if i < len(steps) - 1:
            connector_class = "completed" if is_completed else ""
            html += f'<div class="progress-connector {connector_class}"></div>'

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


def render_header():
    """Render application header with user info"""
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if st.session_state.user_profile:
            name = st.session_state.user_profile["name"].split()[0]
            initial = name[0].upper()
            st.markdown(
                f"""
                <div class="user-info">
                    <div class="user-avatar">{initial}</div>
                    <div class="user-name">{name}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        render_logo()

    with col3:
        if st.session_state.user_profile:
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


# ==================== PAGE RENDERERS ====================
def render_onboarding_page():
    """Render the onboarding/details page"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### 📝 Product Information")

        data = st.session_state.artisan_data

        # Craft Type
        data["craft_type"] = st.text_input(
            "🏺 **Craft Name**",
            value=data["craft_type"],
            placeholder="e.g., Bandhani Saree, Pottery, Jewelry",
            help="Enter the name of your craft or product",
        )

        # Voice Recording Section
        with st.expander(
            "🎤 **Record Product Description** (Optional)", expanded=False
        ):
            lang_options = {
                "English": "en-US",
                "हिन्दी (Hindi)": "hi-IN",
                "ગુજરાતી (Gujarati)": "gu-IN",
            }

            col_a, col_b = st.columns([1, 2])
            with col_a:
                selected_lang = st.selectbox(
                    "Language:", options=list(lang_options.keys())
                )
            with col_b:
                st.info("Record in your preferred language")

            audio = st_audiorec()

            if audio:
                col_1, col_2 = st.columns(2)
                with col_1:
                    if st.button(
                        "📝 Transcribe Audio",
                        type="secondary",
                        use_container_width=True,
                    ):
                        with st.spinner("Transcribing..."):
                            transcribed = transcribe_audio(
                                audio, lang_options[selected_lang]
                            )
                            if transcribed:
                                st.session_state.transcribed_text = transcribed
                                st.success("✅ Transcription complete!")
                                if not data["description"]:
                                    data["description"] = transcribed

                with col_2:
                    if st.session_state.transcribed_text and selected_lang != "English":
                        if st.button(
                            "🌐 Translate to English",
                            type="secondary",
                            use_container_width=True,
                        ):
                            with st.spinner("Translating..."):
                                translated = translate_text(
                                    st.session_state.transcribed_text, "en"
                                )
                                if translated:
                                    data["description"] = translated
                                    st.success("✅ Translation added!")

        # Text Fields
        data["description"] = st.text_area(
            "📋 **Product Description**",
            height=120,
            value=data["description"],
            placeholder="Describe your product in detail...",
            help="Provide a detailed description",
        )

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            data["materials"] = st.text_input(
                "🧵 **Materials Used**",
                value=data["materials"],
                placeholder="e.g., Cotton, Silk, Clay",
                help="Materials used in your craft",
            )
        with col_m2:
            data["dimensions"] = st.text_input(
                "📏 **Dimensions** (Optional)",
                value=data["dimensions"],
                placeholder="e.g., 6x9 feet",
                help="Size/dimensions of product",
            )

    with col2:
        st.markdown("### 🖼️ Product Image")

        uploaded_file = st.file_uploader(
            "Upload a clear photo",
            type=["jpg", "png", "jpeg"],
            help="Best results with well-lit, clear images",
        )

        if uploaded_file:
            if (
                st.session_state.product_image is None
                or uploaded_file.name != st.session_state.uploaded_file_name
            ):

                st.session_state.product_image = Image.open(uploaded_file)
                st.session_state.uploaded_file_name = uploaded_file.name

                with st.spinner("🔍 Analyzing image..."):
                    st.session_state.suggested_tags = get_image_labels(
                        st.session_state.product_image
                    )
                    time.sleep(0.5)

        if st.session_state.product_image:
            st.image(
                st.session_state.product_image,
                use_column_width=True,
                caption="Your Product",
            )

            if st.session_state.suggested_tags:
                st.markdown("#### 🏷️ AI-Suggested Tags")
                data["tags"] = st.multiselect(
                    "Select relevant tags:",
                    options=st.session_state.suggested_tags,
                    default=st.session_state.suggested_tags[:5],
                    help="These help with marketing",
                )

    st.markdown("</div>", unsafe_allow_html=True)

    # Action Button
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button(
            "💾 Save & Continue →",
            type="primary",
            use_container_width=True,
            disabled=not (data["craft_type"] and st.session_state.product_image),
        ):
            if validate_onboarding_data():
                with st.spinner("Saving..."):
                    save_onboarding_data()
                    st.success("✅ Saved successfully!")
                    time.sleep(1)
                    change_page("Content", 2)
                    st.rerun()


def render_content_page():
    """Render the AI content generation page"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### 🖼️ Your Product")
        if st.session_state.product_image:
            st.image(st.session_state.product_image, use_column_width=True)

        st.markdown("### 📋 Details")
        st.markdown(
            f"""
            <div class="feature-card">
                <strong>🏺 Craft:</strong> {st.session_state.artisan_data['craft_type']}<br>
                <strong>📝 Description:</strong> {st.session_state.artisan_data['description'][:100]}...<br>
                <strong>🧵 Materials:</strong> {st.session_state.artisan_data['materials']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "✨ Generate Marketing Content", type="primary", use_container_width=True
        ):
            with st.spinner("Creating content..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)

                st.session_state.generated_content = get_gemini_response(
                    st.session_state.product_image, st.session_state.artisan_data
                )
                if st.session_state.generated_content:
                    st.balloons()
                    st.success("✅ Content generated!")

    with col2:
        st.markdown("### 📱 Marketing Content")

        if st.session_state.generated_content:
            content = st.session_state.generated_content

            # Product Description
            st.markdown("#### 📝 Enhanced Description")
            st.markdown(
                f"""<div class="feature-card">{content.get('product_description', 'Not available.')}</div>""",
                unsafe_allow_html=True,
            )

            # Social Media Captions
            st.markdown("#### 💬 Social Media Captions")
            captions = content.get("social_media_captions", [])
            if captions:
                tabs = st.tabs([f"Caption {i+1}" for i in range(len(captions))])
                for i, (tab, caption) in enumerate(zip(tabs, captions)):
                    with tab:
                        st.text_area("", caption, height=100, key=f"caption_{i}")

            # Hashtags
            hashtags = content.get("hashtags", [])
            if hashtags:
                st.markdown("#### #️⃣ Hashtags")
                st.code(" ".join(f"#{tag}" for tag in hashtags), language=None)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(
                "Continue to Enhancement →", type="primary", use_container_width=True
            ):
                change_page("Image", 3)
                st.rerun()
        else:
            st.info("👈 Click 'Generate Marketing Content' to start")

    st.markdown("</div>", unsafe_allow_html=True)


def render_image_page():
    """Render the AI image enhancement page"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("### 🎨 AI-Powered Image Enhancement")
    st.info("Choose a style to enhance your product image")

    # Style Selection
    cols = st.columns(3)
    styles = [
        ("🎨 Vibrant", "Enhanced colors and contrast", "Vibrant"),
        ("📸 Studio", "Professional studio lighting", "Studio"),
        ("✨ Festive", "Warm, celebratory atmosphere", "Festive"),
    ]

    for col, (title, desc, style_name) in zip(cols, styles):
        with col:
            st.markdown(
                f"""
                <div class="feature-card" style="text-align: center; min-height: 120px;">
                    <h4>{title}</h4>
                    <p style="font-size: 0.85rem; color: var(--text-secondary);">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Apply {style_name}", use_container_width=True, key=style_name.lower()
            ):
                enhance_image(style_name)

    # Image Comparison
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

    col_img1, col_img2 = st.columns(2)

    with col_img1:
        st.markdown("#### 📷 Original")
        if st.session_state.product_image:
            st.image(st.session_state.product_image, use_column_width=True)

    with col_img2:
        st.markdown("#### ✨ Enhanced")
        if st.session_state.enhanced_image:
            st.image(st.session_state.enhanced_image, use_column_width=True)

            buffered = BytesIO()
            st.session_state.enhanced_image.save(buffered, format="PNG")

            st.download_button(
                label="⬇️ Download Enhanced Image",
                data=buffered.getvalue(),
                file_name=f"enhanced_{st.session_state.artisan_data['craft_type'].replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True,
            )

            if st.button(
                "Continue to Export →", type="primary", use_container_width=True
            ):
                change_page("Export", 4)
                st.rerun()
        else:
            st.info("Select a style above to enhance")

    st.markdown("</div>", unsafe_allow_html=True)


def render_export_page():
    """Render the final export page"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Success Message
    st.markdown(
        """
        <div class="success-message">
            <h3>🎉 Congratulations!</h3>
            <p>Your Marketing Pack is Ready</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Preview Section
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📦 Package Contents")
        st.markdown(
            """
            <div class="feature-card">
                ✅ Enhanced product image<br>
                ✅ Professional description<br>
                ✅ Social media captions<br>
                ✅ Relevant hashtags<br>
                ✅ Marketing optimized content
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.enhanced_image:
            st.markdown("#### 🖼️ Final Image")
            st.image(st.session_state.enhanced_image, use_column_width=True)

    with col2:
        st.markdown("#### 📤 Export Options")

        st.markdown(
            """
            <div class="feature-card">
                <h4>📁 Google Drive Export</h4>
                <p>Save your marketing pack to Google Drive for easy access and sharing.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚀 Export to Google Drive", type="primary", use_container_width=True
        ):
            export_to_drive()

        # Quick Stats
        st.markdown("#### 📊 Quick Stats")
        if st.session_state.generated_content:
            content = st.session_state.generated_content
            st.markdown(
                f"""
                <div class="feature-card">
                    <strong>Product:</strong> {st.session_state.artisan_data['craft_type']}<br>
                    <strong>Captions:</strong> {len(content.get('social_media_captions', []))}<br>
                    <strong>Hashtags:</strong> {len(content.get('hashtags', []))}<br>
                    <strong>Status:</strong> Ready to Export
                </div>
                """,
                unsafe_allow_html=True,
            )

    # New Project Button
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    col_new1, col_new2, col_new3 = st.columns([1, 2, 1])
    with col_new2:
        if st.button("📝 Start New Project", use_container_width=True):
            reset_project_state()
            change_page("Onboarding", 1)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ==================== UTILITY FUNCTIONS ====================
def validate_onboarding_data():
    """Validate onboarding form data"""
    data = st.session_state.artisan_data
    if not data["craft_type"]:
        st.error("Please enter your craft type")
        return False
    if not st.session_state.product_image:
        st.error("Please upload a product image")
        return False
    return True


def save_onboarding_data():
    """Save onboarding data to Firebase"""
    data = st.session_state.artisan_data.copy()
    data["name"] = st.session_state.user_profile["name"]
    data["user_email"] = st.session_state.user_profile["email"]

    # Upload image
    buffered = BytesIO()
    st.session_state.product_image.save(buffered, format="JPEG")
    image_url = upload_image_to_storage(
        buffered.getvalue(), st.session_state.uploaded_file_name
    )
    data["product_image_url"] = image_url

    # Save to Firestore
    save_artisan_data(data)


def enhance_image(style):
    """Enhance image with selected style"""
    with st.spinner(f"Applying {style} style... 🎨"):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        st.session_state.enhanced_image = generate_enhanced_image(
            st.session_state.product_image, style
        )
        if st.session_state.enhanced_image:
            st.success(f"✨ {style} style applied!")
            time.sleep(0.5)
            st.rerun()


def export_to_drive():
    """Export marketing pack to Google Drive"""
    if not st.session_state.enhanced_image or not st.session_state.generated_content:
        st.error("Please complete all steps before exporting")
        return

    with st.spinner("Uploading to Google Drive..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

        service = get_gdrive_service_from_session()
        content = st.session_state.generated_content

        # Format export text
        export_text = f"""
# KalaKarigar.ai Marketing Pack
Generated for: {st.session_state.user_profile['name']}
Product: {st.session_state.artisan_data['craft_type']}
Date: {time.strftime('%Y-%m-%d %H:%M')}

---

## Product Description
{content.get('product_description', 'N/A')}

## Social Media Captions
### Caption 1:
{content.get('social_media_captions', ['N/A'])[0]}

### Caption 2:
{content.get('social_media_captions', ['N/A', 'N/A'])[1] if len(content.get('social_media_captions', [])) > 1 else 'N/A'}

## Hashtags
{' '.join('#' + tag for tag in content.get('hashtags', []))}

## Product Details
- Materials: {st.session_state.artisan_data.get('materials', 'N/A')}
- Dimensions: {st.session_state.artisan_data.get('dimensions', 'N/A')}
- Tags: {', '.join(st.session_state.artisan_data.get('tags', []))}
"""

        folder_name = f"KalaKarigar_{st.session_state.artisan_data['craft_type']}_{time.strftime('%Y%m%d_%H%M%S')}"

        folder_link = export_marketing_pack(
            service, st.session_state.enhanced_image, export_text, folder_name
        )

        st.balloons()
        st.success("🎉 Successfully exported to Google Drive!")
        st.markdown(f"[📁 Open in Google Drive]({folder_link})")


def reset_project_state():
    """Reset project-specific state for new project"""
    st.session_state.artisan_data = {
        "craft_type": "",
        "description": "",
        "materials": "",
        "dimensions": "",
        "tags": [],
    }
    st.session_state.product_image = None
    st.session_state.uploaded_file_name = ""
    st.session_state.generated_content = None
    st.session_state.enhanced_image = None
    st.session_state.transcribed_text = None
    st.session_state.suggested_tags = None
    st.session_state.current_step = 1
    st.session_state.steps_completed = []


# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point"""
    # Load custom CSS
    load_custom_css()

    # Initialize session state
    SessionState.init()

    # Initialize services
    if not initialize_services():
        st.stop()

    # Handle Google OAuth
    flow = get_gdrive_flow()
    auth_code = st.query_params.get("code")

    # Process OAuth callback
    if auth_code and not st.session_state.gdrive_credentials:
        try:
            with st.spinner("🔐 Authenticating..."):
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                st.session_state.gdrive_credentials = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes,
                }
                st.query_params.clear()
                st.rerun()
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
            st.stop()

    # Check authentication
    if not st.session_state.gdrive_credentials:
        render_login_page(flow)
    else:
        # Fetch user profile if needed
        if not st.session_state.user_profile:
            with st.spinner("Loading your profile..."):
                st.session_state.user_profile = get_user_info()
                st.rerun()

        # Render main application
        render_main_app()


def render_login_page(flow):
    """Render the login page"""
    # Load custom CSS for login page
    load_custom_css()

    # Logo
    render_logo()

    # Login content
    st.markdown(
        """
        <div style="max-width: 600px; margin: 2rem auto; text-align: center;">
            <h3 style="color: var(--text-primary); margin-bottom: 2rem;">Empower Your Craft with AI</h3>
            <div class="feature-card" style="text-align: left; margin: 2rem 0;">
                <h4>Welcome, Artisan! 👋</h4>
                <p>Transform your handmade products into professional marketing materials:</p>
                <ul style="text-align: left; margin-top: 1rem;">
                    <li>📸 AI-enhanced product photography</li>
                    <li>✍️ Professional product descriptions</li>
                    <li>📱 Social media ready content</li>
                    <li>🏷️ Smart hashtag generation</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if flow:
            auth_url, _ = flow.authorization_url(prompt="consent")
            st.markdown(
                f"""
                <div style="text-align: center; margin-top: 2rem;">
                    <a href="{auth_url}" style="
                        display: inline-block;
                        background: var(--bg-gradient);
                        color: white;
                        padding: 1rem 2rem;
                        border-radius: 8px;
                        text-decoration: none;
                        font-weight: 600;
                        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
                        transition: all 0.3s ease;
                    ">🔐 Login with Google</a>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_main_app():
    """Render the main application interface"""
    # Header
    render_header()

    # Progress Indicator
    render_progress_indicator()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")

        nav_buttons = [
            ("📝 Step 1: Details", "Onboarding", 1, True),
            (
                "✍️ Step 2: Content",
                "Content",
                2,
                st.session_state.product_image is not None,
            ),
            (
                "🎨 Step 3: Enhance",
                "Image",
                3,
                st.session_state.generated_content is not None,
            ),
            (
                "📤 Step 4: Export",
                "Export",
                4,
                st.session_state.enhanced_image is not None,
            ),
        ]

        for label, page, step, enabled in nav_buttons:
            if st.button(
                label,
                use_container_width=True,
                disabled=not enabled,
                type="primary" if st.session_state.page == page else "secondary",
            ):
                change_page(page, step)
                st.rerun()

        # Help Section
        st.markdown("---")
        with st.expander("💡 Need Help?"):
            st.markdown(
                """
                **Quick Tips:**
                - Take clear, well-lit photos
                - Provide detailed descriptions
                - Select relevant tags
                - Try different image styles
                
                **Support:**
                support@kalakarigar.ai
                """
            )

    # Page Content
    if st.session_state.page == "Onboarding":
        render_onboarding_page()
    elif st.session_state.page == "Content":
        render_content_page()
    elif st.session_state.page == "Image":
        render_image_page()
    elif st.session_state.page == "Export":
        render_export_page()


# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
