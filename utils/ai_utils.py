# utils/ai_utils.py
import streamlit as st
import google.generativeai as genai
from PIL import Image
import json


# --- UPDATED FUNCTION ---
def get_gemini_response(image: Image.Image, craft_details: dict):
    """
    Generates marketing content from an image and detailed craft information.
    Args:
        image: A PIL Image object of the product.
        craft_details: A dictionary with artisan name, craft type, description, etc.
    Returns:
        A dictionary containing the generated content, or None if an error occurs.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Build a more detailed prompt
    prompt = f"""
    You are an expert e-commerce marketing assistant for an Indian artisan named {craft_details.get('name', 'the artisan')}. 
    Your task is to generate a complete marketing kit based on the provided image and the artisan's own words.

    **Artisan's Input:**
    - **Craft Type:** {craft_details.get('craft_type', 'N/A')}
    - **Product Description:** {craft_details.get('description', 'N/A')}
    - **Materials Used:** {craft_details.get('materials', 'N/A')}
    - **AI-Suggested Tags:** {", ".join(craft_details.get('tags', []))}

    Analyze all the provided information carefully. Generate the following content in a JSON format with three keys: "product_description", "social_media_captions", and "hashtags".

    1.  **product_description**: Refine the artisan's product description into an evocative and professional paragraph (around 80-100 words). Weave in some of the AI-Suggested Tags where relevant.
    2.  **social_media_captions**: Create a list of 2 engaging captions.
    3.  **hashtags**: Provide a list of 10-15 relevant hashtags, incorporating the AI-Suggested Tags.
    """

    try:
        response = model.generate_content([prompt, image])
        cleaned_response = (
            response.text.strip().replace("```json", "").replace("```", "")
        )
        return json.loads(cleaned_response)
    except Exception as e:
        st.error(f"An error occurred while generating content: {e}")
        return None
