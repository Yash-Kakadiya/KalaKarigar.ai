# utils/firebase_utils.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from uuid import uuid4


def init_firebase():
    """Initializes the Firebase Admin SDK."""
    try:
        creds_dict = dict(st.secrets["firebase_credentials"])
        if "\\n" in creds_dict["private_key"]:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(
                cred,
                {"storageBucket": f"{creds_dict['project_id']}.firebasestorage.app"},
            )
        return True
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        return False


def upload_image_to_storage(image_bytes, file_name):
    """Uploads image bytes to Firebase Storage and returns the public URL."""
    bucket = storage.bucket()
    unique_filename = f"products/{uuid4()}_{file_name}"
    blob = bucket.blob(unique_filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")
    blob.make_public()
    return blob.public_url


# --- UPDATED FUNCTION ---
def save_artisan_data(artisan_data):
    """Saves the complete artisan and product data to Cloud Firestore."""
    db = firestore.client()
    # Add a server-side timestamp to the data
    artisan_data["timestamp"] = firestore.SERVER_TIMESTAMP
    # Add a new doc in collection 'artisans'
    doc_ref = db.collection("artisans").add(artisan_data)
    return doc_ref
