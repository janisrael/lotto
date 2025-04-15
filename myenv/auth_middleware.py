from functools import wraps
from flask import request, jsonify
import jwt
from config import SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.split()[1] if ' ' in bearer else bearer

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            print(f"Received token: {token}")
            print(f"SECRET_KEY in middleware: {SECRET_KEY}")
            jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 401
        except jwt.InvalidTokenError as e:
            print("JWT Error:", e)
            return jsonify({'message': 'Invalid token!'}), 401

        return f(*args, **kwargs)
    return decorated
