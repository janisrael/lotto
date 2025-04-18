from flask import Blueprint, request, jsonify, session
from db import get_connection
import jwt
import os
import bcrypt
from config import SECRET_KEY
from flask_mail import Message
from config import mail  # Assuming mail config is initialized here
from werkzeug.utils import secure_filename
import random
from datetime import datetime
import pytesseract
from PIL import Image
import re
from config import mail
from auth.auth_middleware import token_required
# from main import mail  # Import the initialized `mail` extension
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


auth_bp = Blueprint('auth', __name__)

# Simple in-memory OTP store (use Redis or DB in production)
otp_store = {}

def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password_hash(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user and send OTP
    ---
    responses:
        200:
            description: OTP sent to the provided email
            examples:
                application/json: {"message": "OTP sent to email. Please verify."}
        400:
            description: Missing email or password
            examples:
                application/json: {"error": "Email and password are required"}
        409:
            description: Email already exists
            examples:
                application/json: {"error": "Email already exists"}
    """
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    id_image = request.files.get("id_image")

    # if not email or not password or not id_image:
    if not email or not password or not name:
        return jsonify({"error": "Email, password, and ID image required"}), 400

    # DB check
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"error": "Email already exists"}), 409

    # OTP logic
    otp = str(random.randint(100000, 999999))
    otp_store[email] = {"otp": otp, "password": password}
    # otp_store[email] = {"otp": otp, "password": password, "filepath": filepath}

    # Send OTP
    msg = Message('Your OTP Code', recipients=[email], body=f"Your OTP is: {otp}")
    mail.send(msg)

    return jsonify({"message": "OTP sent to email. Please verify."})

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    input_otp = data.get("otp")

    if email not in otp_store:
        return jsonify({"error": "No registration attempt found."}), 400

    record = otp_store[email]
    if input_otp != record['otp']:
        return jsonify({"error": "Invalid OTP."}), 400

    # Save user
    hashed_pw = generate_password_hash(record['password'])
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, password, name) VALUES (%s, %s, %s)", (email, hashed_pw, name))
    conn.commit()
    cursor.close()
    conn.close()

    # Cleanup
    del otp_store[email]

    return jsonify({"message": "Registration successful."})


@auth_bp.route('/verify-account', methods=['POST'])
@token_required
def verify_account():
    email = request.form.get("email")
    id_image = request.files.get("id_image")

 # if not email or not password or not id_image:
    if not email or not id_image:
        return jsonify({"error": "Email, password, and ID image required"}), 400

    # Save uploaded image
    filename = secure_filename(id_image.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    id_image.save(filepath)

    # OCR Processing
    try:
        text = pytesseract.image_to_string(Image.open(filepath))
        print("OCR Text:\n", text)

        clean_text = text.replace('\n', ' ').replace('\r', '').lower()
        dob = None

        keywords = ['pop', 'vos', 'dob', 'd.o.b']
        patterns = [
            r'{}[^\d]*(\d{{2}}[-/]\d{{2}}[-/]\d{{4}})',   # 05-01-1977 or 05/01/1977
            r'{}[^\d]*(\d{{2}}[-/]\d{{2}}[-/]\d{{2}})',    # 05-01-77 or 05/01/77
            r'{}[^\d]*(\d{{8}})',                         # 05011977
            r'{}[^\d]*(\d{{6}})'                          # 050177
        ]

        for keyword in keywords:
            for pattern in patterns:
                regex = pattern.format(keyword)
                match = re.search(regex, clean_text)
                if match:
                    date_str = match.group(1)
                    try:
                        if '-' in date_str:
                            parts = date_str.split('-')
                            fmt = '%d-%m-%Y' if len(parts[2]) == 4 else '%d-%m-%y'
                            dob = datetime.strptime(date_str, fmt).date()
                        elif '/' in date_str:
                            parts = date_str.split('/')
                            fmt = '%d/%m/%Y' if len(parts[2]) == 4 else '%d/%m/%y'
                            dob = datetime.strptime(date_str, fmt).date()
                        elif len(date_str) == 8:
                            dob = datetime.strptime(date_str, '%d%m%Y').date()
                        elif len(date_str) == 6:
                            dob = datetime.strptime(date_str, '%d%m%y').date()
                        break
                    except Exception as e:
                        print("Date parse error:", e)
                        continue
            if dob:
                break

        if not dob:
            return jsonify({"error": "Unable to detect date of birth."}), 400

        # Age check
        age = (datetime.now().date() - dob).days // 365
        if age < 18:
            return jsonify({"error": "Must be 18+ to register."}), 400

    except Exception as e:
        return jsonify({"error": "OCR failed.", "details": str(e)}), 500


    # DB check
    # Update user record with verification status and date of birth
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET is_verified = TRUE, dob = %s
        WHERE email = %s
    """, (dob, email))
    conn.commit()
    cursor.close()
    conn.close()
        # return jsonify({"error": "Email already exists"}), 409


    return jsonify({"message": "Account updated."})


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

        return jsonify({"message": "Login successful", "token": token ,"email": user['email'], "name": user['name']}), 200

    return jsonify({"error": "Invalid credentials"}), 401

