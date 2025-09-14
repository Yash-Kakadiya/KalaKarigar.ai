import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# It's better to configure the API key once in the main app
# and pass the model object to utility functions.
# This avoids re-configuring it in every utility file.


def get_gemini_response(image: Image.Image, craft_type: str, artisan_name: str):
    """
    Generates product description, social media captions, and hashtags from an image.

    Args:
        image: A PIL Image object of the product.
        craft_type: The type of craft (e.g., "Madhubani Painting").
        artisan_name: The name of the artisan.

    Returns:
        A dictionary containing the generated content, or None if an error occurs.
    """
    # Use the configured model from Streamlit's secrets
    model = genai.GenerativeModel("gemini-1.5-pro-latest")

    # The prompt for Gemini
    prompt = f"""
    You are an expert marketing assistant for an Indian artisan named {artisan_name}. 
    Your task is to generate a complete marketing kit based on the provided image of their {craft_type}.

    Analyze the image carefully, paying attention to colors, patterns, texture, and craftsmanship.

    Generate the following content in a JSON format with three keys: "product_description", "social_media_captions", and "hashtags".

    1.  **product_description**: Write one evocative and authentic paragraph (around 80-100 words). Highlight the beauty and the skill involved.
    2.  **social_media_captions**: Create a list of 2 engaging captions for Instagram or Facebook. Use emojis and a friendly tone. Mention it's handmade by {artisan_name}.
    3.  **hashtags**: Provide a list of 10-15 relevant hashtags, mixing general tags (e.g., #handmade) with specific ones related to the craft and Indian art.
    """

    try:
        response = model.generate_content([prompt, image])
        # Clean up the response and parse the JSON
        cleaned_response = (
            response.text.strip().replace("```json", "").replace("```", "")
        )
        return json.loads(cleaned_response)
    except Exception as e:
        st.error(f"An error occurred while generating content: {e}")
        return None
