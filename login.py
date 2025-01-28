import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # Avoid multiple initializations
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    })
    firebase_admin.initialize_app(cred)

# Add a new user
def add_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password,
        )
        print(f"User {user.email} created successfully!")
    except Exception as e:
        print(f"Error creating user: {e}")

# Example usage
add_user("user@example.com", "secure_password")
