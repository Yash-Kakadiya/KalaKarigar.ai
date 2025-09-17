# utils/gcp_ai_utils.py
import streamlit as st
from google.cloud import speech
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account
from pydub import AudioSegment
import io
from google.cloud import vision
from io import BytesIO
from PIL import Image


# Load GCP service account credentials from Streamlit secrets
try:
    gcp_credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
except Exception as e:
    st.error(f"Error loading GCP credentials: {e}")
    gcp_credentials = None


def convert_to_mono(audio_bytes):
    """
    Ensures audio is mono (1 channel) before sending to Google Speech API.
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        audio = audio.set_channels(1)  # force mono
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Audio conversion error: {e}")
        return audio_bytes  # fallback: return original


def transcribe_audio(audio_bytes, language_code="en-US"):
    """
    Transcribes audio bytes into text using Google Cloud Speech-to-Text.
    """
    if not gcp_credentials:
        st.error("GCP credentials not available.")
        return None

    try:
        client = speech.SpeechClient(credentials=gcp_credentials)

        # Convert audio to mono before sending
        audio_bytes = convert_to_mono(audio_bytes)

        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=language_code,
            # Let Google auto-detect sample rate
        )

        response = client.recognize(config=config, audio=audio)

        if response.results:
            return response.results[0].alternatives[0].transcript
        else:
            return None
    except Exception as e:
        st.error(f"Speech-to-Text Error: {e}")
        return None


def translate_text(text, target_language="en"):
    """
    Translates text into the target language using Google Cloud Translation.
    """
    if not gcp_credentials:
        st.error("GCP credentials not available.")
        return None

    try:
        translate_client = translate.Client(credentials=gcp_credentials)
        result = translate_client.translate(text, target_language=target_language)
        return result["translatedText"]
    except Exception as e:
        st.error(f"Translation Error: {e}")
        return None


def get_image_labels(image: Image.Image):
    """
    Analyzes an image using Google Cloud Vision AI to get relevant labels/tags.
    """
    if not gcp_credentials:
        st.error("GCP credentials not available for Vision AI.")
        return []

    try:
        client = vision.ImageAnnotatorClient(credentials=gcp_credentials)

        # Convert PIL image to bytes
        buf = BytesIO()
        image.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

        gcp_vision_image = vision.Image(content=image_bytes)

        # Perform label detection
        response = client.label_detection(image=gcp_vision_image)
        labels = response.label_annotations

        # Return the descriptions of the labels
        return [label.description for label in labels]

    except Exception as e:
        st.error(f"Cloud Vision AI Error: {e}")
        return []

