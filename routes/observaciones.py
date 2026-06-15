from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, Observacion

observaciones = Blueprint('observaciones', __name__, url_prefix='/observaciones')

MODULOS_ORIGEN = ['Activos', 'Riesgos', 'Tratamiento', 'Riesgo Residual', 'Monitoreo', 'General']


@observaciones.route('/')
@login_required
def index():
    lista = Observacion.query.order_by(Observacion.fecha_creacion.desc()).all()
    return render_template('observaciones/index.html', observaciones=lista, modulos=MODULOS_ORIGEN)


@observaciones.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    if request.method == 'POST':
        origen = request.form.get('origen_modulo', '')
        comentario = request.form.get('comentario', '').strip()
        if not origen or not comentario:
            flash('Módulo de origen y comentario son obligatorios.', 'warning')
            return render_template('observaciones/form.html', modulos=MODULOS_ORIGEN)
        obs = Observacion(
            origen_modulo=origen,
            comentario=comentario,
            autor_nombre=current_user.nombre
        )
        db.session.add(obs)
        db.session.commit()
        flash('Observación registrada exitosamente.', 'success')
        return redirect(url_for('observaciones.index'))
    return render_template('observaciones/form.html', modulos=MODULOS_ORIGEN)


@observaciones.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    obs = db.session.get(Observacion, id)
    if not obs:
        flash('Observación no encontrada.', 'danger')
        return redirect(url_for('observaciones.index'))
    db.session.delete(obs)
    db.session.commit()
    flash('Observación eliminada.', 'success')
    return redirect(url_for('observaciones.index'))
