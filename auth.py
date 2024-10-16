from flask import request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta
from database import Session, User
from os import getenv

SECRET_KEY = getenv('SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            session = Session()
            current_user = session.query(User).filter_by(id=data['user_id']).first()
            session.close()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated