# utils/gdrive_utils.py

import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO, StringIO
from PIL import Image

# Scopes now also include user info
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


def get_gdrive_flow():
    """Initializes the Google Drive OAuth flow from secrets."""
    try:
        creds = st.secrets["gdrive_oauth_credentials"]
        client_config = {
            "web": {
                "client_id": creds["client_id"],
                "project_id": st.secrets["firebase_credentials"]["project_id"],
                "auth_uri": creds["auth_uri"],
                "token_uri": creds["token_uri"],
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": creds["client_secret"],
                "redirect_uris": creds["redirect_uris"],
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        flow.redirect_uri = creds["redirect_uris"][0]
        return flow
    except Exception as e:
        st.error(f"Could not configure Google Drive. Check secrets.toml. Error: {e}")
        return None


def get_gdrive_service_from_session():
    """Uses existing credentials from the session state to build the service."""
    creds_dict = st.session_state.gdrive_credentials
    creds = Credentials.from_authorized_user_info(creds_dict)
    return build("drive", "v3", credentials=creds)


def get_user_info():
    """Fetches user's name and email using credentials from the session."""
    creds_dict = st.session_state.gdrive_credentials
    creds = Credentials.from_authorized_user_info(creds_dict)
    service = build("people", "v1", credentials=creds)
    profile = (
        service.people()
        .get(resourceName="people/me", personFields="names,emailAddresses")
        .execute()
    )
    name = profile.get("names", [{}])[0].get("displayName", "N/A")
    email = profile.get("emailAddresses", [{}])[0].get("value", "N/A")
    return {"name": name, "email": email}


def export_marketing_pack(
    service, image: Image.Image, text_content: str, folder_name: str
):
    # ... (The code to find/create the folder is the same) ...
    query = "name='KalaKarigar.ai Exports' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = (
        service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    )
    files = response.get("files", [])
    if not files:
        file_metadata = {
            "name": "KalaKarigar.ai Exports",
            "mimeType": "application/vnd.google-apps.folder",
        }
        root_folder = service.files().create(body=file_metadata, fields="id").execute()
        root_folder_id = root_folder.get("id")
    else:
        root_folder_id = files[0].get("id")
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [root_folder_id],
    }
    folder = (
        service.files().create(body=folder_metadata, fields="id, webViewLink").execute()
    )
    folder_id = folder.get("id")

    # Image upload logic (unchanged and correct)
    buffered_image = BytesIO()
    image.save(buffered_image, format="PNG")
    media_image = MediaIoBaseUpload(
        buffered_image, mimetype="image/png", resumable=True
    )
    file_metadata_image = {"name": "AI_Enhanced_Image.png", "parents": [folder_id]}
    service.files().create(
        body=file_metadata_image, media_body=media_image, fields="id"
    ).execute()

    # --- THIS IS THE FIX ---
    # 1. Encode the string content into bytes using UTF-8.
    text_bytes = text_content.encode("utf-8")
    # 2. Use BytesIO to handle the raw bytes, not StringIO.
    buffered_text = BytesIO(text_bytes)

    media_text = MediaIoBaseUpload(buffered_text, mimetype="text/plain", resumable=True)
    file_metadata_text = {"name": "AI_Generated_Content.txt", "parents": [folder_id]}
    service.files().create(
        body=file_metadata_text, media_body=media_text, fields="id"
    ).execute()

    return folder.get("webViewLink")
