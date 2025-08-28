import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.case import Case, Client, Equipment, AgendaEvent, Transaction, Contact

# Importar blueprints
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.cases import cases_bp
from src.routes.clients import clients_bp
from src.routes.dashboard import dashboard_bp
from src.routes.contact import contact_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para permitir requests desde el frontend
CORS(app, supports_credentials=True)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(cases_bp, url_prefix='/api/cases')
app.register_blueprint(clients_bp, url_prefix='/api/clients')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(contact_bp, url_prefix='/api/contact')

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Crear tablas y datos de ejemplo
with app.app_context():
    db.create_all()
    
    # Crear usuario administrador por defecto si no existe
    from src.models.user import User
    admin_user = User.query.filter_by(email='admin@forensicweb.com').first()
    if not admin_user:
        admin_user = User(
            nombre_completo='Administrador',
            email='admin@forensicweb.com',
            rol='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        # Crear algunos datos de ejemplo
        from datetime import datetime
        
        # Cliente de ejemplo
        client_example = Client(
            nombre_completo='Cliente Ejemplo',
            email='cliente@ejemplo.com',
            telefono='+123456789',
            direccion='Calle Ejemplo 123'
        )
        db.session.add(client_example)
        db.session.flush()  # Para obtener el ID
        
        # Caso de ejemplo
        case_example = Case(
            numero_caso='CASE-2024-001',
            titulo='Caso de ejemplo',
            descripcion='Este es un caso de ejemplo para demostrar el sistema',
            cliente_id=client_example.id,
            abogado_asignado_id=admin_user.id,
            estado='en_proceso',
            prioridad='media'
        )
        db.session.add(case_example)
        
        try:
            db.session.commit()
            print("Datos de ejemplo creados exitosamente")
        except Exception as e:
            db.session.rollback()
            print(f"Error creando datos de ejemplo: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud de la API"""
    return {'status': 'OK', 'message': 'ForensicWeb API funcionando correctamente'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
