import streamlit as st
import hashlib

# Custom HTML and CSS for the login page
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
            <button class="login-btn" id="login-btn" onclick="submitLogin()">Sign In</button>
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
            function submitLogin() {
                const email = document.getElementById("email").value;
                const password = document.getElementById("password").value;
                if (!email || !password) {
                    alert("Please fill out all fields.");
                    return;
                }
                // Placeholder logic for demo purposes
                alert("Login button clicked. Backend logic goes here!");
            }
            updateGreeting();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Backend logic placeholder in Streamlit
    # The email and password from the JS part are processed in a real scenario using Streamlit backend
    st.info(
        "This design uses modern HTML, CSS, and JavaScript. Actual login validation needs backend processing, which you can connect."
    )

if __name__ == "__main__":
    render_login()
