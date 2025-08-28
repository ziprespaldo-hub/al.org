from flask import Blueprint, request, jsonify
from src.models.case import Contact, db

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/', methods=['POST'])
def submit_contact():
    """Enviar mensaje de contacto desde el sitio público"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['nombre', 'email', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Validar formato de email básico
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        # Crear nuevo mensaje de contacto
        new_contact = Contact(
            nombre=data['nombre'],
            email=data['email'],
            asunto=data.get('asunto', ''),
            mensaje=data['mensaje']
        )
        
        db.session.add(new_contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mensaje enviado exitosamente. Nos pondremos en contacto contigo pronto.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

@contact_bp.route('/', methods=['GET'])
def get_contacts():
    """Obtener mensajes de contacto (para el dashboard)"""
    try:
        # Esta ruta requiere autenticación en un sistema real
        # Por simplicidad, la dejamos sin autenticación por ahora
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Contact.query
        
        if unread_only:
            query = query.filter_by(leido=False)
        
        contacts = query.order_by(Contact.fecha_envio.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'contacts': [contact.to_dict() for contact in contacts.items],
            'total': contacts.total,
            'pages': contacts.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/<int:contact_id>/read', methods=['PUT'])
def mark_as_read(contact_id):
    """Marcar mensaje como leído"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        contact.leido = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Mensaje marcado como leído'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@contact_bp.route('/stats', methods=['GET'])
def get_contact_stats():
    """Obtener estadísticas de mensajes de contacto"""
    try:
        total_contacts = Contact.query.count()
        unread_contacts = Contact.query.filter_by(leido=False).count()
        
        # Mensajes de los últimos 30 días
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_contacts = Contact.query.filter(Contact.fecha_envio >= thirty_days_ago).count()
        
        return jsonify({
            'total_contacts': total_contacts,
            'unread_contacts': unread_contacts,
            'recent_contacts': recent_contacts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

