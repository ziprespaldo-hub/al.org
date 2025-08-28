from flask import Blueprint, request, jsonify, session
from src.models.case import Case, Client, Equipment, db
from src.routes.auth import require_auth
from datetime import datetime

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/', methods=['GET'])
@require_auth
def get_cases():
    """Obtener lista de casos"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        estado = request.args.get('estado')
        
        query = Case.query
        
        # Filtrar por estado si se proporciona
        if estado:
            query = query.filter_by(estado=estado)
        
        # Paginación
        cases = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'cases': [case.to_dict() for case in cases.items],
            'total': cases.total,
            'pages': cases.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cases_bp.route('/', methods=['POST'])
@require_auth
def create_case():
    """Crear nuevo caso"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['numero_caso', 'titulo', 'cliente_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Verificar que el número de caso no exista
        existing_case = Case.query.filter_by(numero_caso=data['numero_caso']).first()
        if existing_case:
            return jsonify({'error': 'El número de caso ya existe'}), 400
        
        # Verificar que el cliente existe
        client = Client.query.get(data['cliente_id'])
        if not client:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        
        # Crear nuevo caso
        new_case = Case(
            numero_caso=data['numero_caso'],
            titulo=data['titulo'],
            descripcion=data.get('descripcion', ''),
            cliente_id=data['cliente_id'],
            abogado_asignado_id=data.get('abogado_asignado_id'),
            estado=data.get('estado', 'pendiente'),
            prioridad=data.get('prioridad', 'media')
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Caso creado exitosamente',
            'case': new_case.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cases_bp.route('/<int:case_id>', methods=['GET'])
@require_auth
def get_case(case_id):
    """Obtener caso específico"""
    try:
        case = Case.query.get_or_404(case_id)
        
        # Incluir equipos relacionados
        case_data = case.to_dict()
        case_data['equipos'] = [equipo.to_dict() for equipo in case.equipos]
        
        return jsonify({'case': case_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cases_bp.route('/<int:case_id>', methods=['PUT'])
@require_auth
def update_case(case_id):
    """Actualizar caso"""
    try:
        case = Case.query.get_or_404(case_id)
        data = request.get_json()
        
        # Actualizar campos permitidos
        allowed_fields = ['titulo', 'descripcion', 'abogado_asignado_id', 'estado', 'prioridad']
        for field in allowed_fields:
            if field in data:
                setattr(case, field, data[field])
        
        # Si se cierra el caso, establecer fecha de cierre
        if data.get('estado') == 'cerrado' and not case.fecha_cierre:
            case.fecha_cierre = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Caso actualizado exitosamente',
            'case': case.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cases_bp.route('/<int:case_id>', methods=['DELETE'])
@require_auth
def delete_case(case_id):
    """Eliminar caso"""
    try:
        case = Case.query.get_or_404(case_id)
        
        db.session.delete(case)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Caso eliminado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cases_bp.route('/<int:case_id>/equipment', methods=['POST'])
@require_auth
def add_equipment(case_id):
    """Agregar equipo a un caso"""
    try:
        case = Case.query.get_or_404(case_id)
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['tipo_equipo']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} es requerido'}), 400
        
        # Crear nuevo equipo
        new_equipment = Equipment(
            caso_id=case_id,
            tipo_equipo=data['tipo_equipo'],
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            numero_serie=data.get('numero_serie'),
            imei=data.get('imei'),
            condicion_fisica=data.get('condicion_fisica'),
            descripcion_danos=data.get('descripcion_danos'),
            accesorios=data.get('accesorios'),
            recibido_de=data.get('recibido_de'),
            notas_custodia=data.get('notas_custodia')
        )
        
        db.session.add(new_equipment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Equipo agregado exitosamente',
            'equipment': new_equipment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cases_bp.route('/stats', methods=['GET'])
@require_auth
def get_case_stats():
    """Obtener estadísticas de casos"""
    try:
        total_cases = Case.query.count()
        active_cases = Case.query.filter_by(estado='en_proceso').count()
        pending_cases = Case.query.filter_by(estado='pendiente').count()
        closed_cases = Case.query.filter_by(estado='cerrado').count()
        
        # Casos por prioridad
        high_priority = Case.query.filter_by(prioridad='alta').count()
        urgent_cases = Case.query.filter_by(prioridad='urgente').count()
        
        # Casos recientes (últimos 30 días)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_cases = Case.query.filter(Case.fecha_apertura >= thirty_days_ago).count()
        
        return jsonify({
            'total_cases': total_cases,
            'active_cases': active_cases,
            'pending_cases': pending_cases,
            'closed_cases': closed_cases,
            'high_priority': high_priority,
            'urgent_cases': urgent_cases,
            'recent_cases': recent_cases
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

