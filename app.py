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
import os
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="KalaKarigar.ai", page_icon="🎨", layout="wide")

# --- GEMINI & FIREBASE INITIALIZATION ---
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

# --- SESSION STATE ---
# Initialize session state variables to preserve data across pages/reruns
if "page" not in st.session_state:
    st.session_state.page = "Onboarding"
if "artisan_name" not in st.session_state:
    st.session_state.artisan_name = ""
if "craft_type" not in st.session_state:
    st.session_state.craft_type = ""
if "product_image" not in st.session_state:
    st.session_state.product_image = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = ""
if "generated_content" not in st.session_state:
    st.session_state.generated_content = None
if "enhanced_image" not in st.session_state:
    st.session_state.enhanced_image = None


# --- UI HELPER FUNCTIONS ---
def change_page(page_name):
    st.session_state.page = page_name


# --- HEADER & BRANDING ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Using the full landscape logo for better branding
    st.image("assets/full-landscape-logo-without-bg.png", use_container_width=True)

st.markdown(
    "<h3 style='text-align: center; color: #FF4B4B;'>Empowering Local Artisans with AI 🤖🎨</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")


# --- NAVIGATION ---
st.sidebar.title("Navigation")
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

# --- PAGE DISPLAY LOGIC ---

# --- ONBOARDING PAGE ---
if st.session_state.page == "Onboarding":
    st.header("👤 Step 1: Tell Us About Your Product")
    st.info(
        "Let's start by getting to know you and your beautiful creation. This information will help us craft the perfect marketing content."
    )

    left_col, right_col = st.columns(2)
    with left_col:
        st.session_state.artisan_name = st.text_input(
            "Your Name", value=st.session_state.artisan_name
        )
        st.session_state.craft_type = st.text_input(
            "Your Craft's Name (e.g., Bandhani Saree, Terracotta Horse)",
            value=st.session_state.craft_type,
        )

        uploaded_file = st.file_uploader(
            "Upload a product image", type=["jpg", "png", "jpeg"]
        )
        if uploaded_file:
            st.session_state.product_image = Image.open(uploaded_file)
            st.session_state.uploaded_file_name = uploaded_file.name
    with right_col:
        if st.session_state.product_image:
            st.image(
                st.session_state.product_image,
                caption="Your beautiful creation!",
                use_container_width=True,
            )

    if st.button(
        "Save & Go to Content Generation ➡", type="primary", use_container_width=True
    ):
        if (
            st.session_state.artisan_name
            and st.session_state.craft_type
            and st.session_state.product_image
        ):
            with st.spinner("Saving your profile..."):
                buffered = BytesIO()
                st.session_state.product_image.save(buffered, format="JPEG")
                image_bytes = buffered.getvalue()
                image_url = upload_image_to_storage(
                    image_bytes, st.session_state.uploaded_file_name
                )
                save_artisan_data(
                    st.session_state.artisan_name,
                    st.session_state.craft_type,
                    image_url,
                )
            st.success("Your profile is saved! Let's create some content.")
            change_page("Content")
        else:
            st.warning("Please fill in all fields and upload an image.")

# --- CONTENT GENERATION PAGE ---
elif st.session_state.page == "Content":
    st.header("📝 Step 2: Generate Your Marketing Kit")
    st.info(
        "Click the button below to use AI to generate a product description, social media captions, and hashtags tailored to your product."
    )

    left_col, right_col = st.columns([1, 1])
    with left_col:
        st.image(st.session_state.product_image, caption="Current Product")
    with right_col:
        if st.button(
            "Generate Content with AI ✨", type="primary", use_container_width=True
        ):
            with st.spinner("Our AI is crafting the perfect words... ✍️"):
                st.session_state.generated_content = get_gemini_response(
                    st.session_state.product_image,
                    st.session_state.craft_type,
                    st.session_state.artisan_name,
                )

    if st.session_state.generated_content:
        st.markdown("---")
        st.success("Your content is ready!")
        content = st.session_state.generated_content

        st.subheader("Product Description")
        st.markdown(f"> {content.get('product_description', 'Not available.')}")

        st.subheader("Social Media Captions")
        for i, caption in enumerate(content.get("social_media_captions", [])):
            st.text_area(
                f"Caption Option {i+1}", caption, height=100, key=f"caption_{i}"
            )

        st.subheader("Hashtags")
        hashtags_string = " ".join(content.get("hashtags", []))
        st.code(hashtags_string)

# --- IMAGE ENHANCEMENT PAGE ---
elif st.session_state.page == "Image":
    st.header("🎨 Step 3: Enhance Your Image with AI")
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
