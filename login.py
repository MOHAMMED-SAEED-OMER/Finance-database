import streamlit as st
import pandas as pd
import hashlib
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets setup
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1hZqFmgpMNr4JSTIwBL18MIPwL4eNjq-FAw7-eQ8NiIE/edit#gid=0"

def load_credentials():
    key_data = st.secrets["GOOGLE_CREDENTIALS"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(key_data, scopes=scopes)
    return gspread.authorize(credentials)

# Fetch user data from Google Sheets
def fetch_user_data():
    try:
        client = load_credentials()
        sheet = client.open_by_url(GOOGLE_SHEET_URL).worksheet("Users")
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return pd.DataFrame()

# Hash the password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Render login page with dynamic HTML and backend validation
def render_login():
    st.markdown(
        """
        <style>
            body {
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Arial', sans-serif;
            }
            .login-container {
                background: #fff;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
                width: 100%;
                max-width: 400px;
                margin: auto;
            }
            .login-title {
                font-size: 24px;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 15px;
            }
            .greeting {
                font-size: 18px;
                color: #555;
                margin-bottom: 10px;
            }
            .form-control {
                border-radius: 8px;
                padding: 12px;
                width: 100%;
                margin-bottom: 15px;
                font-size: 14px;
            }
            .login-btn {
                background-color: #1E3A8A;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                transition: 0.3s;
                width: 100%;
                border: none;
            }
            .login-btn:hover {
                background-color: #3B82F6;
                transform: scale(1.05);
            }
            .footer {
                font-size: 0.9rem;
                color: #374151;
                text-align: center;
                margin-top: 20px;
                font-family: 'Arial', sans-serif;
            }
        </style>
        <div class="login-container">
            <h2 class="login-title">Hasar Organization</h2>
            <p class="greeting" id="greeting-text"></p>
            <input type="email" id="email" class="form-control" placeholder="Email">
            <input type="password" id="password" class="form-control" placeholder="Password">
            <button class="login-btn" onclick="sendLoginData()">Sign In</button>
        </div>
        <script>
            function updateGreeting() {
                const hour = new Date().getHours();
                let greeting;
                if (hour < 12) {
                    greeting = "🌅 Good Morning!";
                } else if (hour < 18) {
                    greeting = "☀️ Good Afternoon!";
                } else {
                    greeting = "🌙 Good Evening!";
                }
                document.getElementById("greeting-text").innerText = greeting;
            }

            function sendLoginData() {
                const email = document.getElementById("email").value;
                const password = document.getElementById("password").value;
                if (email && password) {
                    fetch("/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ email, password }),
                    }).then((response) => {
                        response.json().then((data) => {
                            alert(data.message);
                            if (data.success) {
                                location.reload();
                            }
                        });
                    });
                } else {
                    alert("Please fill in all fields.");
                }
            }
            updateGreeting();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Handle backend login validation
    if st.experimental_get_query_params().get("action") == ["login"]:
        try:
            # Parse email and password sent from frontend
            email = st.experimental_get_query_params()["email"][0]
            password = st.experimental_get_query_params()["password"][0]

            # Fetch users from Google Sheets
            users = fetch_user_data()
            user = users[users["Email"].str.lower() == email.lower()]

            if user.empty:
                st.json({"success": False, "message": "❌ User not found."})
                return

            # Validate password
            user = user.iloc[0]
            hashed_password = hash_password(password)
            if hashed_password != user["Password"]:
                st.json({"success": False, "message": "❌ Incorrect password."})
                return

            # Successful login
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_role"] = user["Role"]
            st.session_state["user_name"] = user.get("Name", "User")

            st.json({"success": True, "message": "✅ Login successful!"})
        except Exception as e:
            st.json({"success": False, "message": f"Error during login: {e}"})

if __name__ == "__main__":
    render_login()
