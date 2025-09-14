from scipy import io
import streamlit as st
from PIL import Image
from utils.ai_utils import get_gemini_response
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="KalaKarigar.ai", page_icon="🎨", layout="wide")

# --- GEMINI API CONFIGURATION ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not api_key:
        st.error(
            "GEMINI_API_KEY not found. Please set it in Streamlit secrets or a .env file."
        )
    else:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring API: {e}")

# --- SESSION STATE INITIALIZATION ---
if "artisan_name" not in st.session_state:
    st.session_state["artisan_name"] = ""
if "craft_type" not in st.session_state:
    st.session_state["craft_type"] = ""
if "product_image" not in st.session_state:
    st.session_state["product_image"] = None
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = None
if "enhanced_image" not in st.session_state:  # New state for enhanced image
    st.session_state["enhanced_image"] = None

# --- HEADER ---
col1, col2 = st.columns([1, 4])
with col1:
    st.image("assets/logo.png", width=150)
with col2:
    st.title("KalaKarigar.ai ✨")
    st.subheader("Empowering Local Artisans with AI 🤖🎨")
st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to", ["Onboarding", "AI Content Generator", "Image Enhancement"]
)


# --- PAGE 1: ONBOARDING (No changes here) ---
if page == "Onboarding":
    st.header("👤 Step 1: Tell Us About Your Product")
    st.session_state.artisan_name = st.text_input(
        "Your Name", value=st.session_state.artisan_name
    )
    st.session_state.craft_type = st.text_input(
        "Craft Type (e.g., Handloom, Pottery)", value=st.session_state.craft_type
    )

    uploaded_file = st.file_uploader(
        "Upload a product image", type=["jpg", "png", "jpeg"]
    )
    if uploaded_file:
        st.session_state.product_image = Image.open(uploaded_file)
        st.image(
            st.session_state.product_image,
            caption="Your beautiful creation!",
            use_container_width=True,
            width=300,
        )

    if st.button("Next: Generate Content", type="primary"):
        if (
            st.session_state.artisan_name
            and st.session_state.craft_type
            and st.session_state.product_image
        ):
            st.success("Great! Now head to the 'AI Content Generator' in the sidebar.")
        else:
            st.warning("Please fill in all fields and upload an image.")


# --- PAGE 2: AI CONTENT GENERATOR (No changes here) ---
elif page == "AI Content Generator":
    st.header("📝 Step 2: Generate Your Marketing Kit")
    if not st.session_state.product_image:
        st.warning("Please complete the Onboarding step first!")
    else:
        st.image(
            st.session_state.product_image,
            caption="Here is the product we are working on.",
            width=300,
        )
        if st.button("Generate Content with AI", type="primary"):
            with st.spinner("Our AI is crafting the perfect words for you... ✍️"):
                content = get_gemini_response(
                    st.session_state.product_image,
                    st.session_state.craft_type,
                    st.session_state.artisan_name,
                )
                st.session_state.generated_content = content
    if st.session_state.generated_content:
        st.success("Your content is ready!")
        content = st.session_state.generated_content
        st.subheader("Product Description")
        st.write(content.get("product_description", "Not available."))
        st.subheader("Social Media Captions")
        for i, caption in enumerate(content.get("social_media_captions", [])):
            st.text_area(f"Caption Option {i+1}", caption, height=100)
        st.subheader("Hashtags")
        hashtags_string = " ".join(content.get("hashtags", []))
        st.code(hashtags_string, language=None)


# --- PAGE 3: IMAGE ENHANCEMENT ---
elif page == "Image Enhancement":
    st.header("🎨 Step 3: Enhance Your Image with AI")

    if (
        "product_image" not in st.session_state
        or st.session_state.product_image is None
    ):
        st.warning("Please upload a product image on the Onboarding page first!")
    else:
        st.subheader("Your Original Image")
        st.image(
            st.session_state.product_image, caption="Original", use_column_width=True
        )
        st.markdown("---")

        st.subheader("Choose an Enhancement Style")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Vibrant 🎨"):
                with st.spinner("AI is adding a splash of color... 🖌️"):
                    from utils.image_utils import generate_enhanced_image

                    enhanced_image = generate_enhanced_image(
                        st.session_state.product_image, "Vibrant"
                    )
                    if enhanced_image:
                        st.session_state.enhanced_image = enhanced_image

        with col2:
            if st.button("Studio 🖼️"):
                with st.spinner("Setting up the professional studio... 💡"):
                    from utils.image_utils import generate_enhanced_image

                    enhanced_image = generate_enhanced_image(
                        st.session_state.product_image, "Studio"
                    )
                    if enhanced_image:
                        st.session_state.enhanced_image = enhanced_image

        with col3:
            if st.button("Festive ✨"):
                with st.spinner("Getting into the festive spirit... 🎉"):
                    from utils.image_utils import generate_enhanced_image

                    enhanced_image = generate_enhanced_image(
                        st.session_state.product_image, "Festive"
                    )
                    if enhanced_image:
                        st.session_state.enhanced_image = enhanced_image

        # Display the enhanced image if it exists in the session state
        if "enhanced_image" in st.session_state and st.session_state.enhanced_image:
            st.markdown("---")
            st.subheader("Your AI-Enhanced Image")
            st.image(
                st.session_state.enhanced_image,
                caption="Enhanced Version",
                use_column_width=True,
            )

            # Add a download button for the new image
            buffered = io.BytesIO()
            st.session_state.enhanced_image.save(buffered, format="PNG")
            st.download_button(
                label="Download Enhanced Image",
                data=buffered.getvalue(),
                file_name="enhanced_product_image.png",
                mime="image/png",
            )
