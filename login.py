def render_login():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #f0f2f6;
            }
            .login-container {
                max-width: 450px;
                margin: auto;
                padding: 3rem;
                background: white;
                border-radius: 10px;
                box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .login-title {
                font-size: 2rem;
                font-weight: bold;
                color: #007BFF;
            }
            .login-info {
                font-size: 1rem;
                color: #555;
                margin-bottom: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Welcome to Hasar Organization</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='login-info'>
            Hasar Organization for Climate Action is dedicated to creating sustainable environmental solutions.
            This app helps you manage financial operations efficiently, ensuring smooth financial oversight.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image("https://www.hasar.org/logo.png", use_container_width=True)

    st.markdown("## 🔐 Login")

    # Use session state to persist credentials
    if "saved_email" not in st.session_state:
        st.session_state.saved_email = ""
    if "saved_password" not in st.session_state:
        st.session_state.saved_password = ""

    # Login form
    email = st.text_input("Email:", value=st.session_state.saved_email, placeholder="Enter your email")
    password = st.text_input("Password:", value=st.session_state.saved_password, placeholder="Enter your password", type="password")
    remember_me = st.checkbox("Keep me signed in")

    if st.button("Login", use_container_width=True):
        if not email or not password:
            st.warning("Please fill out all fields.")
            return

        try:
            # Fetch users from Google Sheets
            users = fetch_user_data()
            user = users[users["Email"].str.lower() == email.lower()]

            if user.empty:
                st.error("User not found.")
                return

            # Get the first matching user
            user = user.iloc[0]
            hashed_password = user["Password"]
            role = user["Role"]

            # Validate password
            password_hash = hash_password(password)
            if password_hash != hashed_password:
                st.error("Incorrect password.")
                return

            # Successful login
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = role

            # Save session state if "Remember Me" is checked
            if remember_me:
                st.session_state.saved_email = email
                st.session_state.saved_password = password
            else:
                st.session_state.saved_email = ""
                st.session_state.saved_password = ""

            st.success("Login successful! Redirecting...")

            # Correct way to update query parameters
            st.query_params.update({"page": "database"})

        except Exception as e:
            st.error(f"Error during login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
