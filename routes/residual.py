from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.models import db, Riesgo, RiesgoResidual

residual = Blueprint('residual', __name__, url_prefix='/residual')

PROBABILIDAD_LABELS = {
    1: 'Muy Raro (1)', 2: 'Poco Probable (2)', 3: 'Posible (3)',
    4: 'Probable (4)', 5: 'Casi Seguro (5)'
}
IMPACTO_LABELS = {
    1: 'Mínimo (1)', 2: 'Menor (2)', 3: 'Moderado (3)',
    4: 'Mayor (4)', 5: 'Catastrófico (5)'
}


@residual.route('/nuevo/<int:riesgo_id>', methods=['GET', 'POST'])
@login_required
def nuevo(riesgo_id):
    riesgo = db.session.get(Riesgo, riesgo_id)
    if not riesgo:
        flash('Riesgo no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    if riesgo.activo.usuario_id != current_user.id:
        abort(403)
    if not riesgo.tratamiento:
        flash('Debes registrar un tratamiento antes de calcular el riesgo residual.', 'warning')
        return redirect(url_for('tratamiento.nuevo', riesgo_id=riesgo_id))
    if riesgo.residual:
        flash('Este riesgo ya tiene riesgo residual calculado. Puedes editarlo.', 'info')
        return redirect(url_for('residual.editar', id=riesgo.residual.id))
    if request.method == 'POST':
        try:
            pr = int(request.form.get('probabilidad_residual', 1))
            ir = int(request.form.get('impacto_residual', 1))
        except (TypeError, ValueError):
            flash('Valores de probabilidad/impacto inválidos.', 'danger')
            return render_template('residual/form.html', riesgo=riesgo, res=None,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        if not (1 <= pr <= 5 and 1 <= ir <= 5):
            flash('Probabilidad e impacto residual deben estar entre 1 y 5.', 'danger')
            return render_template('residual/form.html', riesgo=riesgo, res=None,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        nivel_residual = pr * ir
        if nivel_residual > riesgo.nivel_riesgo:
            flash('Advertencia: el riesgo residual supera al riesgo original. Revisa los valores.', 'warning')
        r = RiesgoResidual(
            riesgo_id=riesgo_id,
            probabilidad_residual=pr,
            impacto_residual=ir,
            nivel_residual=nivel_residual
        )
        db.session.add(r)
        db.session.commit()
        flash('Riesgo residual calculado exitosamente.', 'success')
        return redirect(url_for('riesgos.index'))
    return render_template('residual/form.html', riesgo=riesgo, res=None,
                           prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)


@residual.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    r = db.session.get(RiesgoResidual, id)
    if not r:
        flash('Riesgo residual no encontrado.', 'danger')
        return redirect(url_for('riesgos.index'))
    if r.riesgo.activo.usuario_id != current_user.id:
        abort(403)
    riesgo = r.riesgo
    if request.method == 'POST':
        try:
            pr = int(request.form.get('probabilidad_residual', 1))
            ir = int(request.form.get('impacto_residual', 1))
        except (TypeError, ValueError):
            flash('Valores de probabilidad/impacto inválidos.', 'danger')
            return render_template('residual/form.html', riesgo=riesgo, res=r,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        if not (1 <= pr <= 5 and 1 <= ir <= 5):
            flash('Probabilidad e impacto residual deben estar entre 1 y 5.', 'danger')
            return render_template('residual/form.html', riesgo=riesgo, res=r,
                                   prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
        nivel_residual = pr * ir
        if nivel_residual > riesgo.nivel_riesgo:
            flash('Advertencia: el riesgo residual supera al riesgo original. Revisa los valores.', 'warning')
        r.probabilidad_residual = pr
        r.impacto_residual = ir
        r.nivel_residual = nivel_residual
        db.session.commit()
        flash('Riesgo residual actualizado exitosamente.', 'success')
        return redirect(url_for('riesgos.index'))
    return render_template('residual/form.html', riesgo=riesgo, res=r,
                           prob_labels=PROBABILIDAD_LABELS, imp_labels=IMPACTO_LABELS)
