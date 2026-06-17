from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

from config import Config
from models.models import db, Usuario

from routes.auth import auth
from routes.dashboard import dashboard
from routes.activos import activos
from routes.riesgos import riesgos
from routes.tratamiento import tratamiento
from routes.residual import residual
from routes.observaciones import observaciones
from routes.reportes import reportes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))

def clasificar_nivel(nivel):
    if nivel <= 6:
        return ('Bajo', 'risk-bajo')
    elif nivel <= 12:
        return ('Moderado', 'risk-moderado')
    elif nivel <= 18:
        return ('Alto', 'risk-alto')
    return ('Crítico', 'risk-critico')

app.jinja_env.globals['clasificar_nivel'] = clasificar_nivel

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(activos)
app.register_blueprint(riesgos)
app.register_blueprint(tratamiento)
app.register_blueprint(residual)
app.register_blueprint(observaciones)
app.register_blueprint(reportes)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home_dashboard'))
    return render_template('home/home.html')

if __name__ == '__main__':
    app.run(debug=True)
