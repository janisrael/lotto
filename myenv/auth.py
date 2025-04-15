from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
import jwt
import os
from config import SECRET_KEY

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"error": "Email already exists"}), 409

    hashed_pw = generate_password_hash(password)
    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_pw))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Registered successfully!"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user["password"], password):
        token = jwt.encode(
            {"sub": str(user["id"])},
            SECRET_KEY,
            algorithm="HS256"
        )
        # token = jwt.encode({
        #     'sub': user['id'],
        #     'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
        # }, SECRET_KEY, algorithm='HS256')
        # Ensure token is string (PyJWT sometimes returns bytes)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return jsonify({"message": "Login successful", "token": token}), 200

    return jsonify({"error": "Invalid credentials"}), 401
