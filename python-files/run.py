# run.py
from app import create_app, db
from app.models import User, Configuracion

app = create_app()

@app.cli.command('init-db')
def init_db_command():
    """Crea las tablas de la DB y la configuración/usuario inicial."""
    db.create_all()
    
    if User.query.filter_by(username='admin').first() is None:
        print('Creando usuario administrador...')
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')  # ¡Cambiar esta contraseña en producción!
        db.session.add(admin)
    
    if Configuracion.query.get(1) is None:
        print('Creando configuración inicial de la tasa de cambio...')
        config = Configuracion(id=1, tasa_cambio_ves=1.00)
        db.session.add(config)
        
    db.session.commit()
    print('Base de datos inicializada con éxito.')