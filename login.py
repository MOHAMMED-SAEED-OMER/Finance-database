import streamlit as st

# Define the custom HTML structure for the login page
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
        </style>
        <div class="login-container">
            <h2 class="login-title">Hasar Organization</h2>
            <p class="greeting" id="greeting-text"></p>
            <input type="email" id="email" class="form-control" placeholder="Email">
            <input type="password" id="password" class="form-control" placeholder="Password">
            <button class="login-btn" id="login-btn">Sign In</button>
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
            updateGreeting();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Handle user input and login (this part will still be Python-based)
    email = st.text_input("Email", label_visibility="collapsed")
    password = st.text_input("Password", type="password", label_visibility="collapsed")
    if st.button("Sign In"):
        if not email or not password:
            st.warning("Please fill out all fields.")
        else:
            # Perform login logic here
            st.success("Login successful!")

---

### What Happens Here:
- **HTML & CSS**:
  - The login page's design is rendered through the custom HTML and styled using CSS.
  - The `background` gradient, card design, and button styles are directly embedded.

- **Streamlit Components**:
  - Email and password fields are duplicated to capture the user’s input using Streamlit.
  - A button (`Sign In`) triggers the Python logic for handling login.

---

### Why This Design is Better:
- **Professional Look**:
  - The login page has a modern, clean design with gradients and animations.
  
- **Dynamic Greeting**:
  - A greeting updates based on the time of day using JavaScript.

---

### Final Note:
Test this code by running your Streamlit app. Let me know if you'd like further tweaks or enhancements!
