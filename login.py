<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Hasar Organization</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #1E3A8A, #3B82F6);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: #fff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
            width: 100%;
            max-width: 400px;
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
        }
        .login-btn {
            background-color: #1E3A8A;
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            transition: 0.3s;
        }
        .login-btn:hover {
            background-color: #3B82F6;
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2 class="login-title">Hasar Organization</h2>
        <p class="greeting" id="greeting-text"></p>
        <input type="email" class="form-control mb-3" placeholder="Email" id="email">
        <input type="password" class="form-control mb-3" placeholder="Password" id="password">
        <button class="btn login-btn w-100">Sign In</button>
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
</body>
</html>
