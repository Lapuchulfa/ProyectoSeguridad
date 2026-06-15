from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import db, Activo

activos = Blueprint('activos', __name__, url_prefix='/activos')

TIPOS_ACTIVO = [
    'Hardware', 'Software', 'Redes', 'Datos / Información',
    'Personal', 'Instalaciones', 'Servicios Externos'
]

LABELS_CID = {0: 'Sin valor', 1: 'Muy Bajo', 2: 'Bajo', 3: 'Medio', 4: 'Alto', 5: 'Muy Alto'}


@activos.route('/')
@login_required
def index():
    lista = Activo.query.order_by(Activo.valor_total.desc()).all()
    return render_template('activos/index.html', activos=lista, labels_cid=LABELS_CID)


@activos.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        tipo = request.form.get('tipo', '')
        if not nombre or not tipo:
            flash('Nombre y tipo son obligatorios.', 'warning')
            return render_template('activos/form.html', activo=None, tipos=TIPOS_ACTIVO)
        c = int(request.form.get('confidencialidad', 0))
        i = int(request.form.get('integridad', 0))
        d = int(request.form.get('disponibilidad', 0))
        activo = Activo(
            nombre=nombre,
            tipo=tipo,
            descripcion=request.form.get('descripcion', '').strip(),
            confidencialidad=c,
            integridad=i,
            disponibilidad=d,
            valor_total=max(c, i, d)
        )
        db.session.add(activo)
        db.session.commit()
        flash(f'Activo "{nombre}" registrado exitosamente.', 'success')
        return redirect(url_for('activos.index'))
    return render_template('activos/form.html', activo=None, tipos=TIPOS_ACTIVO)


@activos.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    activo = db.session.get(Activo, id)
    if not activo:
        flash('Activo no encontrado.', 'danger')
        return redirect(url_for('activos.index'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        tipo = request.form.get('tipo', '')
        if not nombre or not tipo:
            flash('Nombre y tipo son obligatorios.', 'warning')
            return render_template('activos/form.html', activo=activo, tipos=TIPOS_ACTIVO)
        c = int(request.form.get('confidencialidad', 0))
        i = int(request.form.get('integridad', 0))
        d = int(request.form.get('disponibilidad', 0))
        activo.nombre = nombre
        activo.tipo = tipo
        activo.descripcion = request.form.get('descripcion', '').strip()
        activo.confidencialidad = c
        activo.integridad = i
        activo.disponibilidad = d
        activo.valor_total = max(c, i, d)
        db.session.commit()
        flash(f'Activo "{nombre}" actualizado.', 'success')
        return redirect(url_for('activos.index'))
    return render_template('activos/form.html', activo=activo, tipos=TIPOS_ACTIVO)


@activos.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    activo = db.session.get(Activo, id)
    if not activo:
        flash('Activo no encontrado.', 'danger')
        return redirect(url_for('activos.index'))
    nombre = activo.nombre
    db.session.delete(activo)
    db.session.commit()
    flash(f'Activo "{nombre}" eliminado junto con sus riesgos asociados.', 'success')
    return redirect(url_for('activos.index'))
