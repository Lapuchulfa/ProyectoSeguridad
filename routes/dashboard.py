from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.models import Activo, Riesgo, Tratamiento, RiesgoResidual, Observacion

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def home_dashboard():
    uid = current_user.id

    total_activos = Activo.query.filter_by(usuario_id=uid).count()

    user_riesgos = (Riesgo.query
                    .join(Activo, Riesgo.activo_id == Activo.id)
                    .filter(Activo.usuario_id == uid))

    total_riesgos = user_riesgos.count()
    riesgos_criticos = user_riesgos.filter(Riesgo.nivel_riesgo >= 19).count()
    riesgos_altos = user_riesgos.filter(Riesgo.nivel_riesgo.between(13, 18)).count()
    riesgos_moderados = user_riesgos.filter(Riesgo.nivel_riesgo.between(7, 12)).count()
    riesgos_bajos = user_riesgos.filter(Riesgo.nivel_riesgo <= 6).count()

    total_tratamientos = (Tratamiento.query
                          .join(Riesgo, Tratamiento.riesgo_id == Riesgo.id)
                          .join(Activo, Riesgo.activo_id == Activo.id)
                          .filter(Activo.usuario_id == uid)
                          .count())

    sin_tratamiento = (Riesgo.query
                       .join(Activo, Riesgo.activo_id == Activo.id)
                       .filter(Activo.usuario_id == uid)
                       .outerjoin(Tratamiento, Tratamiento.riesgo_id == Riesgo.id)
                       .filter(Tratamiento.id == None)
                       .count())

    con_residual = (RiesgoResidual.query
                    .join(Riesgo, RiesgoResidual.riesgo_id == Riesgo.id)
                    .join(Activo, Riesgo.activo_id == Activo.id)
                    .filter(Activo.usuario_id == uid)
                    .count())

    riesgos_recientes = (Riesgo.query
                         .join(Activo, Riesgo.activo_id == Activo.id)
                         .filter(Activo.usuario_id == uid)
                         .order_by(Riesgo.nivel_riesgo.desc())
                         .limit(5)
                         .all())

    total_observaciones = Observacion.query.filter_by(usuario_id=uid).count()

    return render_template('dashboard/dashboard.html',
                           total_activos=total_activos,
                           total_riesgos=total_riesgos,
                           riesgos_criticos=riesgos_criticos,
                           riesgos_altos=riesgos_altos,
                           riesgos_moderados=riesgos_moderados,
                           riesgos_bajos=riesgos_bajos,
                           total_tratamientos=total_tratamientos,
                           sin_tratamiento=sin_tratamiento,
                           con_residual=con_residual,
                           riesgos_recientes=riesgos_recientes,
                           total_observaciones=total_observaciones)
