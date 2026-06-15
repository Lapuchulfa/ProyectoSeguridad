from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import db, Riesgo, Tratamiento

tratamiento = Blueprint('tratamiento', __name__, url_prefix='/tratamiento')

ESTRATEGIAS = ['Mitigar', 'Transferir', 'Aceptar', 'Evitar']

CONTROLES_ISO27002 = [
    'A.5.1 - Políticas de seguridad de la información',
    'A.5.2 - Roles y responsabilidades de seguridad de la información',
    'A.5.7 - Inteligencia de amenazas',
    'A.5.9 - Inventario de activos de información',
    'A.5.10 - Uso aceptable de activos de información',
    'A.5.14 - Transferencia de información',
    'A.5.15 - Control de acceso',
    'A.5.16 - Gestión de identidad',
    'A.5.17 - Información de autenticación',
    'A.5.18 - Derechos de acceso',
    'A.5.23 - Seguridad del uso de servicios en la nube',
    'A.5.24 - Planificación y preparación de gestión de incidentes',
    'A.5.25 - Evaluación y decisión sobre incidentes de SI',
    'A.5.26 - Respuesta a incidentes de seguridad de la información',
    'A.5.29 - Seguridad de la información durante la interrupción',
    'A.5.30 - Preparación de las TIC para continuidad del negocio',
    'A.5.33 - Protección de registros',
    'A.5.34 - Privacidad y protección de datos personales',
    'A.6.1 - Investigación de antecedentes',
    'A.6.3 - Concienciación, educación y formación en seguridad',
    'A.6.5 - Responsabilidades tras la finalización del contrato',
    'A.6.7 - Trabajo remoto',
    'A.6.8 - Notificación de eventos de seguridad de la información',
    'A.7.1 - Perímetros de seguridad física',
    'A.7.2 - Acceso físico',
    'A.7.4 - Monitorización de la seguridad física',
    'A.7.7 - Escritorio y pantalla limpia',
    'A.7.10 - Medios de almacenamiento',
    'A.7.11 - Servicios de suministro',
    'A.7.14 - Eliminación segura o reutilización de equipos',
    'A.8.1 - Dispositivos de usuario final',
    'A.8.2 - Derechos de acceso privilegiado',
    'A.8.4 - Acceso al código fuente',
    'A.8.5 - Autenticación segura',
    'A.8.6 - Gestión de la capacidad',
    'A.8.7 - Protección contra malware',
    'A.8.8 - Gestión de vulnerabilidades técnicas',
    'A.8.9 - Gestión de la configuración',
    'A.8.12 - Prevención de fuga de datos (DLP)',
    'A.8.15 - Registro de actividad (logging)',
    'A.8.16 - Actividades de monitoreo',
    'A.8.20 - Seguridad en redes',
    'A.8.21 - Seguridad de los servicios de red',
    'A.8.22 - Segregación de redes',
    'A.8.23 - Filtrado Web',
    'A.8.24 - Uso de la criptografía',
    'A.8.25 - Ciclo de vida de desarrollo seguro',
    'A.8.28 - Codificación segura',
    'A.8.32 - Gestión de cambios',
]


@tratamiento.route('/nuevo/<int:riesgo_id>', methods=['GET', 'POST'])
@login_required
def nuevo(riesgo_id):
    riesgo = db.session.get(Riesgo, riesgo_id)
    if not riesgo:
        flash('Riesgo no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    if riesgo.tratamiento:
        flash('Este riesgo ya tiene un tratamiento. Puedes editarlo.', 'info')
        return redirect(url_for('tratamiento.editar', id=riesgo.tratamiento.id))
    if request.method == 'POST':
        estrategia = request.form.get('estrategia', '')
        control = request.form.get('control_iso27002', '').strip()
        responsable = request.form.get('responsable', '').strip()
        if not estrategia or not control or not responsable:
            flash('Estrategia, control ISO y responsable son obligatorios.', 'warning')
            return render_template('tratamiento/form.html', riesgo=riesgo, trat=None,
                                   estrategias=ESTRATEGIAS, controles=CONTROLES_ISO27002)
        t = Tratamiento(
            riesgo_id=riesgo_id,
            estrategia=estrategia,
            control_iso27002=control,
            detalles_control=request.form.get('detalles_control', '').strip(),
            responsable=responsable
        )
        db.session.add(t)
        db.session.commit()
        flash('Tratamiento registrado exitosamente.', 'success')
        return redirect(url_for('riesgos.index'))
    return render_template('tratamiento/form.html', riesgo=riesgo, trat=None,
                           estrategias=ESTRATEGIAS, controles=CONTROLES_ISO27002)


@tratamiento.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    t = db.session.get(Tratamiento, id)
    if not t:
        flash('Tratamiento no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    riesgo = t.riesgo
    if request.method == 'POST':
        estrategia = request.form.get('estrategia', '')
        control = request.form.get('control_iso27002', '').strip()
        responsable = request.form.get('responsable', '').strip()
        if not estrategia or not control or not responsable:
            flash('Estrategia, control ISO y responsable son obligatorios.', 'warning')
            return render_template('tratamiento/form.html', riesgo=riesgo, trat=t,
                                   estrategias=ESTRATEGIAS, controles=CONTROLES_ISO27002)
        t.estrategia = estrategia
        t.control_iso27002 = control
        t.detalles_control = request.form.get('detalles_control', '').strip()
        t.responsable = responsable
        db.session.commit()
        flash('Tratamiento actualizado exitosamente.', 'success')
        return redirect(url_for('riesgos.index'))
    return render_template('tratamiento/form.html', riesgo=riesgo, trat=t,
                           estrategias=ESTRATEGIAS, controles=CONTROLES_ISO27002)


@tratamiento.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    t = db.session.get(Tratamiento, id)
    if not t:
        flash('Tratamiento no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    db.session.delete(t)
    db.session.commit()
    flash('Tratamiento eliminado.', 'success')
    return redirect(url_for('riesgos.index'))
