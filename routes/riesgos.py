from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from models.models import db, Activo, Riesgo

riesgos = Blueprint('riesgos', __name__, url_prefix='/riesgos')

AMENAZAS_MAGERIT = [
    'Fuego', 'Daños por agua', 'Desastres naturales',
    'Avería de origen físico o lógico', 'Corte del suministro eléctrico',
    'Condiciones inadecuadas de temperatura o humedad',
    'Fallo de servicios de comunicaciones', 'Interrupción de servicios de terceros',
    'Errores de los usuarios', 'Errores del administrador del sistema',
    'Difusión de software dañino (malware)', 'Escapes de información',
    'Alteración accidental de la información', 'Destrucción de información',
    'Divulgación de información confidencial', 'Suplantación de identidad',
    'Abuso de privilegios de acceso', 'Acceso no autorizado al sistema',
    'Interceptación de comunicaciones (Man-in-the-Middle)',
    'Modificación deliberada de la información', 'Denegación de servicio (DoS/DDoS)',
    'Fraude informático / Ingeniería social', 'Robo de equipos',
    'Ataque de ransomware', 'Phishing / Spear Phishing',
    'Explotación de vulnerabilidades técnicas', 'Ataques de fuerza bruta',
]

PROBABILIDAD_LABELS = {
    1: 'Muy Raro (1)', 2: 'Poco Probable (2)', 3: 'Posible (3)',
    4: 'Probable (4)', 5: 'Casi Seguro (5)'
}
IMPACTO_LABELS = {
    1: 'Mínimo (1)', 2: 'Menor (2)', 3: 'Moderado (3)',
    4: 'Mayor (4)', 5: 'Catastrófico (5)'
}


@riesgos.route('/')
@login_required
def index():
    lista = (Riesgo.query
             .join(Activo, Riesgo.activo_id == Activo.id)
             .filter(Activo.usuario_id == current_user.id)
             .options(joinedload(Riesgo.activo))
             .order_by(Riesgo.nivel_riesgo.desc())
             .all())
    return render_template('riesgos/index.html', riesgos=lista)


@riesgos.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    activos_lista = Activo.query.filter_by(usuario_id=current_user.id)\
                                .order_by(Activo.nombre).all()
    if not activos_lista:
        flash('Primero debes registrar al menos un activo de información.', 'warning')
        return redirect(url_for('activos.nuevo'))
    if request.method == 'POST':
        amenaza = request.form.get('amenaza', '').strip()
        vulnerabilidad = request.form.get('vulnerabilidad', '').strip()
        try:
            activo_id = int(request.form.get('activo_id', 0))
            p = int(request.form.get('probabilidad', 1))
            i = int(request.form.get('impacto', 1))
        except (TypeError, ValueError):
            flash('Valores numéricos inválidos.', 'danger')
            return render_template('riesgos/form.html', riesgo=None,
                                   activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        if not activo_id or not amenaza or not vulnerabilidad:
            flash('Todos los campos son obligatorios.', 'warning')
            return render_template('riesgos/form.html', riesgo=None,
                                   activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        activo = db.session.get(Activo, activo_id)
        if not activo or activo.usuario_id != current_user.id:
            abort(403)
        if not (1 <= p <= 5 and 1 <= i <= 5):
            flash('Probabilidad e impacto deben estar entre 1 y 5.', 'danger')
            return render_template('riesgos/form.html', riesgo=None,
                                   activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        riesgo = Riesgo(
            activo_id=activo_id,
            amenaza=amenaza,
            vulnerabilidad=vulnerabilidad,
            probabilidad=p,
            impacto=i,
            nivel_riesgo=p * i
        )
        db.session.add(riesgo)
        db.session.commit()
        flash('Riesgo identificado y registrado exitosamente.', 'success')
        return redirect(url_for('riesgos.index'))
    return render_template('riesgos/form.html', riesgo=None,
                           activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                           prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)


@riesgos.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    riesgo = db.session.get(Riesgo, id)
    if not riesgo:
        flash('Riesgo no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    if riesgo.activo.usuario_id != current_user.id:
        abort(403)
    activos_lista = Activo.query.filter_by(usuario_id=current_user.id)\
                                .order_by(Activo.nombre).all()
    if request.method == 'POST':
        amenaza = request.form.get('amenaza', '').strip()
        vulnerabilidad = request.form.get('vulnerabilidad', '').strip()
        if not amenaza or not vulnerabilidad:
            flash('Amenaza y vulnerabilidad son obligatorios.', 'warning')
            return render_template('riesgos/form.html', riesgo=riesgo,
                                   activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        try:
            activo_id = int(request.form.get('activo_id', 0))
            p = int(request.form.get('probabilidad', 1))
            i = int(request.form.get('impacto', 1))
        except (TypeError, ValueError):
            flash('Valores numéricos inválidos.', 'danger')
            return render_template('riesgos/form.html', riesgo=riesgo,
                                   activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        activo = db.session.get(Activo, activo_id)
        if not activo or activo.usuario_id != current_user.id:
            abort(403)
        if not (1 <= p <= 5 and 1 <= i <= 5):
            flash('Probabilidad e impacto deben estar entre 1 y 5.', 'danger')
            return render_template('riesgos/form.html', riesgo=riesgo,
                                   activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        riesgo.activo_id = activo_id
        riesgo.amenaza = amenaza
        riesgo.vulnerabilidad = vulnerabilidad
        riesgo.probabilidad = p
        riesgo.impacto = i
        riesgo.nivel_riesgo = p * i
        db.session.commit()
        flash('Riesgo actualizado exitosamente.', 'success')
        return redirect(url_for('riesgos.index'))
    return render_template('riesgos/form.html', riesgo=riesgo,
                           activos=activos_lista, amenazas=AMENAZAS_MAGERIT,
                           prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)


@riesgos.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    riesgo = db.session.get(Riesgo, id)
    if not riesgo:
        flash('Riesgo no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    if riesgo.activo.usuario_id != current_user.id:
        abort(403)
    db.session.delete(riesgo)
    db.session.commit()
    flash('Riesgo eliminado junto con su tratamiento y riesgo residual.', 'success')
    return redirect(url_for('riesgos.index'))
