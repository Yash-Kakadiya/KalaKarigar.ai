# utils/gdrive_utils.py

import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO, StringIO
from PIL import Image

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_gdrive_flow():
    """
    Initializes the Google Drive OAuth flow from secrets for a Web Application.
    """
    try:
        # Load the simpler secrets format
        creds = st.secrets["gdrive_oauth_credentials"]

        # Manually build the client_config in the structure the library expects
        client_config = {
            "web": {
                "client_id": creds["client_id"],
                "project_id": st.secrets["firebase_credentials"][
                    "project_id"
                ],  # Re-use from firebase creds
                "auth_uri": creds["auth_uri"],
                "token_uri": creds["token_uri"],
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": creds["client_secret"],
                "redirect_uris": creds["redirect_uris"],
            }
        }

        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

        # Set the redirect_uri explicitly
        flow.redirect_uri = creds["redirect_uris"][0]

        return flow
    except Exception as e:
        st.error(
            f"Could not load/configure Google Drive credentials. Check your secrets.toml. Error: {e}"
        )
        return None


def get_gdrive_service_from_code(flow, auth_code):
    """
    Fetches the token using the provided auth code and returns an authenticated service.
    """
    try:
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        st.session_state.gdrive_credentials = creds  # Save for future use
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        st.error(
            f"Failed to fetch token. Please try the authentication process again. Error: {e}"
        )
        return None


def get_gdrive_service_from_session():
    """
    Uses existing credentials from the session state to build the service.
    """
    creds_dict = st.session_state.gdrive_credentials
    # The credentials object needs to be rebuilt from the dictionary stored in session state
    creds = Credentials.from_authorized_user_info(creds_dict)
    return build("drive", "v3", credentials=creds)


def export_marketing_pack(
    service, image: Image.Image, text_content: str, folder_name: str
):
    # ... (This function remains exactly the same as before) ...
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

    buffered_image = BytesIO()
    image.save(buffered_image, format="PNG")
    media_image = MediaIoBaseUpload(
        buffered_image, mimetype="image/png", resumable=True
    )
    file_metadata_image = {"name": "AI_Enhanced_Image.png", "parents": [folder_id]}
    service.files().create(
        body=file_metadata_image, media_body=media_image, fields="id"
    ).execute()

    buffered_text = StringIO(text_content)
    media_text = MediaIoBaseUpload(buffered_text, mimetype="text/plain", resumable=True)
    file_metadata_text = {"name": "AI_Generated_Content.txt", "parents": [folder_id]}
    service.files().create(
        body=file_metadata_text, media_body=media_text, fields="id"
    ).execute()

    return folder.get("webViewLink")
