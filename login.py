import streamlit as st

# Render the login page
def render_login():
    st.markdown(
        """
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .login-container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                width: 400px;
                box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            .login-title {
                font-size: 24px;
                font-weight: bold;
                color: #1E3A8A;
                margin-bottom: 20px;
            }
            .greeting {
                font-size: 18px;
                color: #555;
                margin-bottom: 20px;
            }
            .form-control {
                width: 100%;
                padding: 12px;
                margin-bottom: 15px;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-sizing: border-box;
            }
            .login-btn {
                width: 100%;
                padding: 12px;
                background-color: #1E3A8A;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }
            .login-btn:hover {
                background-color: #3B82F6;
            }
        </style>
        <div class="login-container">
            <h2 class="login-title">Hasar Organization</h2>
            <p class="greeting" id="greeting-text"></p>
            <input type="email" class="form-control" id="email" placeholder="Email">
            <input type="password" class="form-control" id="password" placeholder="Password">
            <button class="login-btn" onclick="handleLogin()">Sign In</button>
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
            function handleLogin() {
                const email = document.getElementById("email").value;
                const password = document.getElementById("password").value;
                if (email && password) {
                    alert("Login successful! Redirecting...");
                } else {
                    alert("Please enter both email and password.");
                }
            }
            updateGreeting();
        </script>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    render_login()
