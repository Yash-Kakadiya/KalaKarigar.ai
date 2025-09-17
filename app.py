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

# --- ADD get_image_labels ---
from utils.gcp_ai_utils import transcribe_audio, translate_text, get_image_labels
from st_audiorec import st_audiorec
import os
from io import BytesIO

# ... (Initializations remain the same) ...
st.set_page_config(page_title="KalaKarigar.ai", page_icon="🎨", layout="wide")
try:
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not api_key:
        st.error("GEMINI_API_KEY not found.")
    else:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring API: {e}")
init_firebase()

# --- SESSION STATE (with new variables for tags) ---
if "page" not in st.session_state:
    st.session_state.page = "Onboarding"
if "artisan_data" not in st.session_state:
    st.session_state.artisan_data = {
        "name": "",
        "craft_type": "",
        "description": "",
        "materials": "",
        "dimensions": "",
        "tags": [],
    }
# ... (rest of session state is the same) ...
if "product_image" not in st.session_state:
    st.session_state.product_image = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "generated_content" not in st.session_state:
    st.session_state.generated_content = None
if "enhanced_image" not in st.session_state:
    st.session_state.enhanced_image = None
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = None
# --- NEW STATE VARIABLES ---
if "suggested_tags" not in st.session_state:
    st.session_state.suggested_tags = None


def change_page(page_name):
    st.session_state.page = page_name


# ... (Header & Navigation remain the same) ...
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/full-landscape-logo-without-bg.png", use_column_width=True)
st.markdown(
    "<h3 style='text-align: center; color: #FF4B4B;'>Empowering Local Artisans with AI 🤖🎨</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")
st.sidebar.title("Navigation")
# ... (Sidebar buttons remain the same) ...
if st.sidebar.button(
    "Step 1: Onboarding",
    use_container_width=True,
    type="primary" if st.session_state.page == "Onboarding" else "secondary",
):
    change_page("Onboarding")
if st.sidebar.button(
    "Step 2: AI Content Generator",
    use_container_width=True,
    type="primary" if st.session_state.page == "Content" else "secondary",
    disabled=st.session_state.product_image is None,
):
    change_page("Content")
if st.sidebar.button(
    "Step 3: AI Image Enhancement",
    use_container_width=True,
    type="primary" if st.session_state.page == "Image" else "secondary",
    disabled=st.session_state.product_image is None,
):
    change_page("Image")


# --- ONBOARDING PAGE (UPDATED WITH VISION AI) ---
if st.session_state.page == "Onboarding":
    st.header("👤 Step 1: Tell Us About Your Product")
    st.info(
        "Fill in the details, upload a photo, and our AI will suggest tags to improve your product's discoverability!"
    )

    data = st.session_state.artisan_data
    # ... (Name, craft type, and voice description sections remain the same) ...
    data["name"] = st.text_input("Your Name", value=data["name"])
    data["craft_type"] = st.text_input("Your Craft's Name", value=data["craft_type"])
    st.markdown("---")
    st.subheader("🎤 Describe Your Product with Your Voice")
    # ... (voice code is unchanged) ...
    lang_options = {
        "English": "en-US",
        "हिन्दी (Hindi)": "hi-IN",
        "ગુજરાતી (Gujarati)": "gu-IN",
    }
    selected_lang_label = st.selectbox(
        "1. Select your language:", options=list(lang_options.keys())
    )
    language_code = lang_options[selected_lang_label]
    st.write("2. Record your description:")
    audio_bytes = st_audiorec()
    if audio_bytes and not st.session_state.transcribed_text:
        with st.spinner("Transcribing your voice..."):
            st.session_state.transcribed_text = transcribe_audio(
                audio_bytes, language_code
            )
    if st.session_state.transcribed_text:
        st.info(f"What we heard ({selected_lang_label}):")
        st.write(f'**"{st.session_state.transcribed_text}"**')
        confirm_col, retry_col = st.columns(2)
        with confirm_col:
            if st.button(
                "👍 Looks Good! Translate & Use This Text",
                type="primary",
                use_container_width=True,
            ):
                with st.spinner("Translating..."):
                    if language_code != "en-US":
                        translated_text = translate_text(
                            st.session_state.transcribed_text
                        )
                        data["description"] = translated_text
                    else:
                        data["description"] = st.session_state.transcribed_text
                    st.session_state.transcribed_text = None
                    st.success("Description updated!")
        with retry_col:
            if st.button("Retry Recording", use_container_width=True):
                st.session_state.transcribed_text = None
                st.rerun()

    st.markdown("---")
    data["description"] = st.text_area(
        "Product Description", height=150, value=data["description"]
    )
    data["materials"] = st.text_input("Materials Used", value=data["materials"])
    data["dimensions"] = st.text_input("Dimensions", value=data["dimensions"])

    st.markdown("---")
    st.subheader("🖼️ Upload Your Product Image")
    uploaded_file = st.file_uploader(
        "Upload a clear photo of your product",
        type=["jpg", "png", "jpeg"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        if (
            st.session_state.product_image is None
            or uploaded_file.name != st.session_state.uploaded_file_name
        ):
            st.session_state.product_image = Image.open(uploaded_file)
            st.session_state.uploaded_file_name = uploaded_file.name
            with st.spinner("Analyzing image for tags..."):
                st.session_state.suggested_tags = get_image_labels(
                    st.session_state.product_image
                )

    if st.session_state.product_image:
        st.image(
            st.session_state.product_image,
            caption="Your beautiful creation!",
            width=300,
        )

    # --- NEW: Display Suggested Tags ---
    if st.session_state.suggested_tags:
        st.subheader("🤖 AI-Suggested Tags")
        st.info(
            "Select the tags that best describe your product. This helps in generating better content."
        )
        data["tags"] = st.multiselect(
            "Review and confirm your tags:",
            options=st.session_state.suggested_tags,
            default=st.session_state.suggested_tags,
        )

    if st.button(
        "Save & Go to Content Generation ➡", type="primary", use_container_width=True
    ):
        if data["name"] and data["craft_type"] and st.session_state.product_image:
            # ... (Save logic remains the same, as `data` now includes the tags) ...
            with st.spinner("Saving your profile..."):
                buffered = BytesIO()
                st.session_state.product_image.save(buffered, format="JPEG")
                image_url = upload_image_to_storage(
                    buffered.getvalue(), st.session_state.uploaded_file_name
                )
                data["product_image_url"] = image_url
                save_artisan_data(data)
            st.success("Your product details are saved!")
            change_page("Content")
        else:
            st.warning("Please provide your Name, Craft Type, and upload an Image.")

# --- The other pages (Content and Image) remain exactly the same ---
# (No changes needed for the rest of the file)
elif st.session_state.page == "Content":
    # ... (code is unchanged)
    st.header("📝 Step 2: Generate Your Marketing Kit")
    if not st.session_state.product_image:
        st.warning("Please complete the Onboarding step first!")
        st.stop()
    st.info(
        "Click the button to use AI to refine your description and create new marketing content."
    )
    left_col, right_col = st.columns([1, 1])
    with left_col:
        st.image(st.session_state.product_image, caption="Current Product")
    with right_col:
        st.subheader("Your Details")
        st.markdown(f"**Artisan:** {st.session_state.artisan_data['name']}")
        st.markdown(f"**Craft:** {st.session_state.artisan_data['craft_type']}")
        st.markdown(f"**Description:** {st.session_state.artisan_data['description']}")
        if st.session_state.artisan_data["tags"]:
            st.markdown(f"**Tags:** {', '.join(st.session_state.artisan_data['tags'])}")
        if st.button(
            "Generate Content with AI ✨", type="primary", use_container_width=True
        ):
            with st.spinner("Our AI is crafting the perfect words... ✍️"):
                st.session_state.generated_content = get_gemini_response(
                    st.session_state.product_image, st.session_state.artisan_data
                )
    if st.session_state.generated_content:
        st.markdown("---")
        content = st.session_state.generated_content
        st.subheader("AI-Refined Product Description")
        st.markdown(f"> {content.get('product_description', 'Not available.')}")
        st.subheader("Social Media Captions")
        for i, caption in enumerate(content.get("social_media_captions", [])):
            st.text_area(
                f"Caption Option {i+1}", caption, height=100, key=f"caption_{i}"
            )
        st.subheader("Hashtags")
        hashtags_string = " ".join(content.get("hashtags", []))
        st.code(hashtags_string)

elif st.session_state.page == "Image":
    # ... (code is unchanged)
    st.header("🎨 Step 3: Enhance Your Image with AI")
    if not st.session_state.product_image:
        st.warning("Please complete the Onboarding step first!")
        st.stop()
    st.info(
        "Choose a style below to generate a new, professional-looking version of your product photo."
    )
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("Original Image")
        st.image(st.session_state.product_image, caption="Original")
    style_col1, style_col2, style_col3 = st.columns(3)
    with style_col1:
        if st.button("Vibrant 🎨", use_container_width=True):
            with st.spinner("AI is adding a splash of color..."):
                st.session_state.enhanced_image = generate_enhanced_image(
                    st.session_state.product_image, "Vibrant"
                )
    with style_col2:
        if st.button("Studio 🖼️", use_container_width=True):
            with st.spinner("Setting up the professional studio..."):
                st.session_state.enhanced_image = generate_enhanced_image(
                    st.session_state.product_image, "Studio"
                )
    with style_col3:
        if st.button("Festive ✨", use_container_width=True):
            with st.spinner("Getting into the festive spirit..."):
                st.session_state.enhanced_image = generate_enhanced_image(
                    st.session_state.product_image, "Festive"
                )
    with right_col:
        st.subheader("AI-Enhanced Image")
        if st.session_state.enhanced_image:
            st.image(st.session_state.enhanced_image, caption="Enhanced Version")
            buffered = BytesIO()
            st.session_state.enhanced_image.save(buffered, format="PNG")
            st.download_button(
                label="⬇️ Download Enhanced Image",
                data=buffered.getvalue(),
                file_name="enhanced_product_image.png",
                mime="image/png",
                use_container_width=True,
            )
        else:
            st.info("Your new image will appear here once generated.")
