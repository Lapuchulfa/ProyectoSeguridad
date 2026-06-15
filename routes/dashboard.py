from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Activo, Riesgo, Tratamiento, RiesgoResidual, Observacion

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard')
@login_required
def home_dashboard():
    total_activos = Activo.query.count()
    total_riesgos = Riesgo.query.count()

    riesgos_criticos = Riesgo.query.filter(Riesgo.nivel_riesgo >= 19).count()
    riesgos_altos = Riesgo.query.filter(Riesgo.nivel_riesgo.between(13, 18)).count()
    riesgos_moderados = Riesgo.query.filter(Riesgo.nivel_riesgo.between(7, 12)).count()
    riesgos_bajos = Riesgo.query.filter(Riesgo.nivel_riesgo <= 6).count()

    total_tratamientos = Tratamiento.query.count()

    sin_tratamiento = (
        Riesgo.query
        .outerjoin(Tratamiento, Tratamiento.riesgo_id == Riesgo.id)
        .filter(Tratamiento.id == None)
        .count()
    )

    con_residual = RiesgoResidual.query.count()

    riesgos_recientes = (
        Riesgo.query
        .order_by(Riesgo.nivel_riesgo.desc())
        .limit(5)
        .all()
    )

    total_observaciones = Observacion.query.count()

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
