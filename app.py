from flask import Flask, request, jsonify, render_template
import jwt

app = Flask(__name__)

SECRET_KEY = "secret123"

# Real users
users = {
    "nope": {"password": "nope123", "role": "user"},
    "bob": {"password": "admin123", "role": "admin"}  # hidden admin
}

# Dummy users (admin only)
dummy_users = {
    "charlie": {
        "role": "user",
        "email": "charlie@gmail.com",
        "password": "charlie123"
    },
    "dave": {
        "role": "user",
        "email": "dave@gmail.com",
        "password": "dave123"
    }
}

def get_user(token):
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except:
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

# 🔐 LOGIN
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = users.get(data.get("username"))

    if user and user["password"] == data.get("password"):
        token = jwt.encode({
            "username": data["username"],
            "role": user["role"]
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401


# 👤 USER INFO
@app.route("/api/me")
def me():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_user(token)

    if not user:
        return jsonify({"error": "Invalid token"}), 401

    return jsonify(user)


# 👑 ADMIN USERS
@app.route("/api/admin/users")
def admin_users():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_user(token)

    if not user or user.get("role") != "admin":
        return jsonify({"error": "Access denied"}), 403

    return jsonify(dummy_users)


# ❌ DELETE USER
@app.route("/api/admin/delete/<username>", methods=["POST"])
def delete_user(username):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_user(token)

    if not user or user.get("role") != "admin":
        return jsonify({"error": "Access denied"}), 403

    if username in dummy_users:
        del dummy_users[username]
        return jsonify({"success": f"{username} deleted"})

    return jsonify({"error": "User not found"}), 400


# 🚀 FLAG
@app.route("/api/admin/flag")
def flag():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = get_user(token)

    if not user or user.get("role") != "admin":
        return jsonify({"error": "Access denied"}), 403

    return jsonify({
        "flag": "FLAG{JWT_ESCALATION_SUCCESS}",
        "msg": "You are admin now 🚀"
    })


if __name__ == "__main__":
    app.run(debug=True)