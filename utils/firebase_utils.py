import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from uuid import uuid4  # To generate unique filenames


def init_firebase():
    """Initializes the Firebase Admin SDK, checking if it's already initialized."""
    try:
        creds_dict = dict(st.secrets["firebase_credentials"])

        # Fix private key formatting if it has literal \n
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

    # Create a unique filename to avoid overwrites
    unique_filename = f"products/{uuid4()}_{file_name}"

    blob = bucket.blob(unique_filename)

    # Upload the bytes
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    # Make the blob publicly viewable
    blob.make_public()

    return blob.public_url


def save_artisan_data(artisan_name, craft_type, image_url):
    """Saves artisan data to the Cloud Firestore."""
    db = firestore.client()

    # Data to be saved
    data = {
        "name": artisan_name,
        "craft_type": craft_type,
        "product_image_url": image_url,
        "timestamp": firestore.SERVER_TIMESTAMP,  # Adds a server-side timestamp
    }

    # Add a new doc in collection 'artisans' with a new auto-ID
    doc_ref = db.collection("artisans").add(data)

    return doc_ref
