from flask import Blueprint, request, jsonify
from src.models.case import Client, db
from src.routes.auth import require_auth

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/', methods=['GET'])
@require_auth
def get_clients():
    """Obtener lista de clientes"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Client.query
        
        # Búsqueda por nombre o email
        if search:
            query = query.filter(
                (Client.nombre_completo.contains(search)) |
                (Client.email.contains(search))
            )
        
        # Paginación
        clients = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'clients': [client.to_dict() for client in clients.items],
            'total': clients.total,
            'pages': clients.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/', methods=['POST'])
@require_auth
def create_client():
    """Crear nuevo cliente"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['nombre_completo', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar que el email no exista
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Crear nuevo cliente
        new_client = Client(
            nombre_completo=data['nombre_completo'],
            email=data['email'],
            telefono=data.get('telefono'),
            direccion=data.get('direccion')
        )
        
        db.session.add(new_client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cliente creado exitosamente',
            'client': new_client.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['GET'])
@require_auth
def get_client(client_id):
    """Obtener cliente específico"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Incluir casos relacionados
        client_data = client.to_dict()
        client_data['casos'] = [caso.to_dict() for caso in client.casos]
        
        return jsonify({'client': client_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['PUT'])
@require_auth
def update_client(client_id):
    """Actualizar cliente"""
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        # Verificar email único si se está cambiando
        if 'email' in data and data['email'] != client.email:
            existing_client = Client.query.filter_by(email=data['email']).first()
            if existing_client:
                return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Actualizar campos permitidos
        allowed_fields = ['nombre_completo', 'email', 'telefono', 'direccion']
        for field in allowed_fields:
            if field in data:
                setattr(client, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cliente actualizado exitosamente',
            'client': client.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['DELETE'])
@require_auth
def delete_client(client_id):
    """Eliminar cliente"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Verificar que no tenga casos activos
        active_cases = len([caso for caso in client.casos if caso.estado != 'cerrado'])
        if active_cases > 0:
            return jsonify({
                'error': f'No se puede eliminar el cliente. Tiene {active_cases} casos activos.'
            }), 400
        
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@clients_bp.route('/stats', methods=['GET'])
@require_auth
def get_client_stats():
    """Obtener estadísticas de clientes"""
    try:
        total_clients = Client.query.count()
        
        # Clientes con casos activos
        from src.models.case import Case
        clients_with_active_cases = db.session.query(Client.id).join(Case).filter(
            Case.estado.in_(['pendiente', 'en_proceso'])
        ).distinct().count()
        
        # Clientes registrados en los últimos 30 días
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_clients = Client.query.filter(Client.fecha_registro >= thirty_days_ago).count()
        
        return jsonify({
            'total_clients': total_clients,
            'clients_with_active_cases': clients_with_active_cases,
            'recent_clients': recent_clients
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

