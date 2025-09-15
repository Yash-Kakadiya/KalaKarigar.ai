# utils/image_utils.py

import streamlit as st
from PIL import Image
import google.generativeai as genai
from io import BytesIO


def generate_enhanced_image(image: Image.Image, style: str):
    """
    Generates an enhanced image using the Gemini image generation model.

    Args:
        image: The original PIL Image object.
        style: The desired style ("Vibrant", "Studio", "Festive").

    Returns:
        A new PIL Image object of the enhanced image, or None on failure.
    """
    try:
        # We use the Gemini model specified by the user
        model = genai.GenerativeModel("gemini-2.5-flash-image-preview")

        # Define style-specific prompts
        style_prompts = {
            "Vibrant": "A vibrant, professional product photograph of the subject. Enhance the colors to be more vivid and ensure the focus is sharp. The image should look bright and high-contrast, suitable for an e-commerce website.",
            "Studio": "A professional studio product shot of the subject against a clean, minimalist, light-gray background. The lighting should be soft and even, highlighting the texture and details of the craftsmanship. The final image should look elegant and high-end.",
            "Festive": "A festive-themed product photograph of the subject. The background should have warm, celebratory elements like soft bokeh lights or subtle traditional patterns. The lighting should be warm and inviting, evoking a sense of celebration (like Diwali or a wedding).",
        }

        prompt = style_prompts.get(
            style, "A high-quality, professional product photograph of the subject."
        )

        # Generate content using the multimodal capabilities
        response = model.generate_content(
            contents=[prompt, image],
            generation_config={"output_mime_type": "image/png"},
        )

        # Extract the image data from the response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type == "image/png":
                    image_data = part.inline_data.data
                    enhanced_image = Image.open(BytesIO(image_data))
                    return enhanced_image

        st.error("Image generation failed: No image data found in the response.")
        return None

    except Exception as e:
        st.error(f"An error occurred during image generation: {e}")
        # Add specific advice for common errors if possible
        if "permission" in str(e).lower():
            st.warning(
                "Please ensure the Gemini API is enabled and your project has access to the 'gemini-2.5-flash-image-preview' model in your Google Cloud Console."
            )
        return None
