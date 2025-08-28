from flask import Blueprint, jsonify
from src.models.user import User, db
from src.models.case import Case, Client, Equipment, Transaction, Contact
from src.routes.auth import require_auth
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """Obtener estadísticas principales del dashboard"""
    try:
        # Estadísticas básicas
        total_cases = Case.query.count()
        active_cases = Case.query.filter_by(estado='en_proceso').count()
        total_clients = Client.query.count()
        total_equipment = Equipment.query.count()
        
        # Casos por estado
        pending_cases = Case.query.filter_by(estado='pendiente').count()
        closed_cases = Case.query.filter_by(estado='cerrado').count()
        
        # Casos por prioridad
        urgent_cases = Case.query.filter_by(prioridad='urgente').count()
        high_priority_cases = Case.query.filter_by(prioridad='alta').count()
        
        # Actividad reciente (últimos 7 días)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_cases = Case.query.filter(Case.fecha_apertura >= seven_days_ago).count()
        recent_clients = Client.query.filter(Client.fecha_registro >= seven_days_ago).count()
        
        # Ingresos del mes actual
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_income = db.session.query(func.sum(Transaction.monto)).filter(
            Transaction.tipo == 'ingreso',
            Transaction.fecha >= current_month_start
        ).scalar() or 0
        
        return jsonify({
            'basic_stats': {
                'total_cases': total_cases,
                'active_cases': active_cases,
                'total_clients': total_clients,
                'total_equipment': total_equipment
            },
            'case_stats': {
                'pending': pending_cases,
                'active': active_cases,
                'closed': closed_cases,
                'urgent': urgent_cases,
                'high_priority': high_priority_cases
            },
            'recent_activity': {
                'new_cases_week': recent_cases,
                'new_clients_week': recent_clients
            },
            'financial': {
                'monthly_income': monthly_income
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/recent-activity', methods=['GET'])
@require_auth
def get_recent_activity():
    """Obtener actividad reciente del sistema"""
    try:
        # Casos recientes (últimos 10)
        recent_cases = Case.query.order_by(Case.fecha_apertura.desc()).limit(10).all()
        
        # Clientes recientes (últimos 5)
        recent_clients = Client.query.order_by(Client.fecha_registro.desc()).limit(5).all()
        
        # Mensajes de contacto no leídos
        unread_contacts = Contact.query.filter_by(leido=False).order_by(Contact.fecha_envio.desc()).limit(5).all()
        
        activity_items = []
        
        # Agregar casos recientes
        for case in recent_cases:
            activity_items.append({
                'type': 'case',
                'description': f'Nuevo caso: {case.titulo}',
                'time': case.fecha_apertura.isoformat(),
                'id': case.id,
                'priority': case.prioridad
            })
        
        # Agregar clientes recientes
        for client in recent_clients:
            activity_items.append({
                'type': 'client',
                'description': f'Nuevo cliente registrado: {client.nombre_completo}',
                'time': client.fecha_registro.isoformat(),
                'id': client.id
            })
        
        # Agregar mensajes de contacto
        for contact in unread_contacts:
            activity_items.append({
                'type': 'contact',
                'description': f'Nuevo mensaje de: {contact.nombre}',
                'time': contact.fecha_envio.isoformat(),
                'id': contact.id,
                'subject': contact.asunto
            })
        
        # Ordenar por fecha (más reciente primero)
        activity_items.sort(key=lambda x: x['time'], reverse=True)
        
        return jsonify({
            'activity': activity_items[:15]  # Últimos 15 elementos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/pending-cases', methods=['GET'])
@require_auth
def get_pending_cases():
    """Obtener casos pendientes de revisión"""
    try:
        pending_cases = Case.query.filter(
            Case.estado.in_(['pendiente', 'en_proceso'])
        ).order_by(Case.fecha_apertura.desc()).limit(10).all()
        
        cases_data = []
        for case in pending_cases:
            case_data = case.to_dict()
            # Agregar información adicional
            case_data['days_open'] = (datetime.utcnow() - case.fecha_apertura).days
            cases_data.append(case_data)
        
        return jsonify({
            'pending_cases': cases_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/charts/cases-by-month', methods=['GET'])
@require_auth
def get_cases_by_month():
    """Obtener datos para gráfico de casos por mes"""
    try:
        # Últimos 12 meses
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        # Consulta para obtener casos por mes
        cases_by_month = db.session.query(
            func.strftime('%Y-%m', Case.fecha_apertura).label('month'),
            func.count(Case.id).label('count')
        ).filter(
            Case.fecha_apertura >= twelve_months_ago
        ).group_by(
            func.strftime('%Y-%m', Case.fecha_apertura)
        ).order_by('month').all()
        
        # Formatear datos para el gráfico
        months = []
        counts = []
        
        for month_data in cases_by_month:
            # Convertir formato de fecha
            month_obj = datetime.strptime(month_data.month, '%Y-%m')
            month_name = month_obj.strftime('%b %Y')
            months.append(month_name)
            counts.append(month_data.count)
        
        return jsonify({
            'labels': months,
            'data': counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/charts/cases-by-status', methods=['GET'])
@require_auth
def get_cases_by_status():
    """Obtener datos para gráfico de casos por estado"""
    try:
        cases_by_status = db.session.query(
            Case.estado,
            func.count(Case.id).label('count')
        ).group_by(Case.estado).all()
        
        # Mapear estados a nombres legibles
        status_names = {
            'pendiente': 'Pendientes',
            'en_proceso': 'En Proceso',
            'cerrado': 'Cerrados',
            'archivado': 'Archivados'
        }
        
        labels = []
        data = []
        colors = []
        
        # Colores para cada estado
        status_colors = {
            'pendiente': '#ffc107',
            'en_proceso': '#17a2b8',
            'cerrado': '#28a745',
            'archivado': '#6c757d'
        }
        
        for status_data in cases_by_status:
            labels.append(status_names.get(status_data.estado, status_data.estado))
            data.append(status_data.count)
            colors.append(status_colors.get(status_data.estado, '#007bff'))
        
        return jsonify({
            'labels': labels,
            'data': data,
            'colors': colors
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/charts/revenue-by-month', methods=['GET'])
@require_auth
def get_revenue_by_month():
    """Obtener datos para gráfico de ingresos por mes"""
    try:
        # Últimos 12 meses
        twelve_months_ago = datetime.utcnow() - timedelta(days=365)
        
        # Consulta para obtener ingresos por mes
        revenue_by_month = db.session.query(
            func.strftime('%Y-%m', Transaction.fecha).label('month'),
            func.sum(Transaction.monto).label('total')
        ).filter(
            Transaction.tipo == 'ingreso',
            Transaction.fecha >= twelve_months_ago
        ).group_by(
            func.strftime('%Y-%m', Transaction.fecha)
        ).order_by('month').all()
        
        # Formatear datos para el gráfico
        months = []
        amounts = []
        
        for revenue_data in revenue_by_month:
            month_obj = datetime.strptime(revenue_data.month, '%Y-%m')
            month_name = month_obj.strftime('%b %Y')
            months.append(month_name)
            amounts.append(float(revenue_data.total or 0))
        
        return jsonify({
            'labels': months,
            'data': amounts
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

