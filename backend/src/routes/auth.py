from flask import Blueprint, request, jsonify, session
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuario"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']) and user.activo:
            # Crear sesión
            session['user_id'] = user.id
            session['user_role'] = user.rol
            
            return jsonify({
                'success': True,
                'message': 'Login exitoso',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Sesión cerrada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def profile():
    """Obtener perfil del usuario autenticado"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'No autenticado'}), 401
        
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Verificar si el usuario está autenticado"""
    try:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.activo:
                return jsonify({
                    'authenticated': True,
                    'user': user.to_dict()
                }), 200
        
        return jsonify({'authenticated': False}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def require_auth(f):
    """Decorador para requerir autenticación"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticación requerida'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.activo:
            return jsonify({'error': 'Usuario no válido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorador para requerir rol de administrador"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autenticación requerida'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not user.activo or user.rol != 'admin':
            return jsonify({'error': 'Permisos de administrador requeridos'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

