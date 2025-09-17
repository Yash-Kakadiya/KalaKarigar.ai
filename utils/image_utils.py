# utils/image_utils.py
import streamlit as st
from PIL import Image
from google import genai
from io import BytesIO


def generate_enhanced_image(image: Image.Image, style: str):
    """
    Generates an enhanced image using the Gemini image generation model (via google.genai).
    """
    try:
        # Create a client each time (or you could reuse the one from app.py via st.session_state)
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

        style_prompts = {
            "Vibrant": "A vibrant, professional product photograph of the subject. Enhance the colors to be more vivid and ensure the focus is sharp. The image should look bright and high-contrast, suitable for an e-commerce website.",
            "Studio": "A professional studio product shot of the subject against a clean, minimalist, light-gray background. The lighting should be soft and even, highlighting the texture and details of the craftsmanship. The final image should look elegant and high-end.",
            "Festive": "A festive-themed product photograph of the subject. The background should have warm, celebratory elements like soft bokeh lights or subtle traditional patterns. The lighting should be warm and inviting, evoking a sense of celebration (like Diwali or a wedding).",
        }

        prompt = style_prompts.get(
            style, "A high-quality, professional product photograph of the subject."
        )

        # Call the model with prompt + image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt, image],
        )

        if not response.candidates:
            st.error("No candidates returned from Gemini.")
            return None

        for part in response.candidates[0].content.parts:
            if part.inline_data:
                try:
                    enhanced_image = Image.open(BytesIO(part.inline_data.data))
                    return enhanced_image
                except Exception as decode_err:
                    st.error(f"Failed to decode image: {decode_err}")
            elif part.text:
                st.warning(f"Gemini returned text instead of image: {part.text}")

        st.error("Image generation failed: No valid image data found in response.")
        return None

    except Exception as e:
        st.error(f"An error occurred during image generation: {e}")
        return None
