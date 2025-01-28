import streamlit as st
from firebase_admin import auth
from firebase_admin import credentials, initialize_app

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE_KEY"])
    initialize_app(cred)

def render_role_management():
    st.title("User Role Management")

    # Fetch all users
    try:
        users = []
        page_token = None

        # Paginate through all users
        while True:
            result = auth.list_users(page_token=page_token)
            users.extend(result.users)
            page_token = result.page_token
            if not page_token:
                break

        # Display user list
        user_list = [{"Email": user.email, "UID": user.uid} for user in users]
        selected_user_email = st.selectbox("Select a user", [user["Email"] for user in user_list])

        # Display current role
        selected_user = next(user for user in user_list if user["Email"] == selected_user_email)
        user_details = auth.get_user(selected_user["UID"])
        current_role = user_details.custom_claims.get("role", "No role assigned")
        st.write(f"Current Role: **{current_role}**")

        # Assign a new role
        new_role = st.selectbox("Assign a new role", ["Admin", "Approver", "Requester", "No role"])
        if st.button("Update Role"):
            try:
                if new_role == "No role":
                    auth.set_custom_user_claims(selected_user["UID"], None)  # Remove custom claims
                else:
                    auth.set_custom_user_claims(selected_user["UID"], {"role": new_role})
                st.success(f"Role updated to '{new_role}' for {selected_user_email}")
            except Exception as e:
                st.error(f"Error updating role: {e}")

    except Exception as e:
        st.error(f"Error fetching users: {e}")
