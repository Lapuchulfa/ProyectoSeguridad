from flask import Blueprint, render_template, make_response
from flask_login import login_required, current_user
from models.models import Activo, Riesgo, Tratamiento, RiesgoResidual, Observacion
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import io
from datetime import datetime

reportes = Blueprint('reportes', __name__, url_prefix='/reportes')


def _clasificar(nivel):
    if nivel <= 6:
        return 'Bajo'
    elif nivel <= 12:
        return 'Moderado'
    elif nivel <= 18:
        return 'Alto'
    return 'Crítico'


@reportes.route('/')
@login_required
def index():
    uid = current_user.id
    activos_lista = Activo.query.filter_by(usuario_id=uid)\
                               .order_by(Activo.valor_total.desc()).all()
    riesgos_lista = (Riesgo.query
                     .join(Activo, Riesgo.activo_id == Activo.id)
                     .filter(Activo.usuario_id == uid)
                     .order_by(Riesgo.nivel_riesgo.desc()).all())
    observaciones_lista = Observacion.query.filter_by(usuario_id=uid)\
                                          .order_by(Observacion.fecha_creacion.desc()).all()
    return render_template('reportes/index.html',
                           activos=activos_lista,
                           riesgos=riesgos_lista,
                           observaciones=observaciones_lista,
                           clasificar=_clasificar,
                           fecha=datetime.now().strftime('%d/%m/%Y %H:%M'))


@reportes.route('/pdf')
@login_required
def pdf():
    uid = current_user.id
    activos_lista = Activo.query.filter_by(usuario_id=uid)\
                               .order_by(Activo.valor_total.desc()).all()
    riesgos_lista = (Riesgo.query
                     .join(Activo, Riesgo.activo_id == Activo.id)
                     .filter(Activo.usuario_id == uid)
                     .order_by(Riesgo.nivel_riesgo.desc()).all())
    tratamientos = (Tratamiento.query
                    .join(Riesgo, Tratamiento.riesgo_id == Riesgo.id)
                    .join(Activo, Riesgo.activo_id == Activo.id)
                    .filter(Activo.usuario_id == uid).all())
    residuales = (RiesgoResidual.query
                  .join(Riesgo, RiesgoResidual.riesgo_id == Riesgo.id)
                  .join(Activo, Riesgo.activo_id == Activo.id)
                  .filter(Activo.usuario_id == uid).all())
    observaciones_lista = Observacion.query.filter_by(usuario_id=uid)\
                                          .order_by(Observacion.fecha_creacion.desc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                 fontSize=16, spaceAfter=6)
    h1_style = ParagraphStyle('CustomH1', parent=styles['Heading1'],
                              fontSize=12, spaceAfter=4, spaceBefore=12)

    story = []
    story.append(Paragraph('Reporte de Evaluación de Riesgos Cibernéticos', title_style))
    story.append(Paragraph(
        f'Metodología MAGERIT v3 | Usuario: {current_user.nombre} | Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
        styles['Normal']
    ))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.darkblue, spaceAfter=12))

    # 1. Activos
    story.append(Paragraph('1. Valoración de Activos de Información', h1_style))
    if activos_lista:
        data = [['#', 'Nombre del Activo', 'Tipo', 'Confidencialidad', 'Integridad', 'Disponibilidad', 'Valor Total']]
        for idx, a in enumerate(activos_lista, 1):
            data.append([str(idx), a.nombre, a.tipo,
                         str(a.confidencialidad), str(a.integridad),
                         str(a.disponibilidad), str(a.valor_total)])
        t = Table(data, hAlign='LEFT', colWidths=[1*cm, 6*cm, 4*cm, 3*cm, 3*cm, 3*cm, 3*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3a5c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
            ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(t)
    else:
        story.append(Paragraph('No hay activos registrados.', styles['Normal']))
    story.append(Spacer(1, 0.4 * cm))

    # 2. Riesgos
    story.append(Paragraph('2. Análisis y Valoración de Riesgos', h1_style))
    if riesgos_lista:
        data2 = [['#', 'Activo', 'Amenaza', 'Vulnerabilidad', 'P', 'I', 'Nivel', 'Clasificación']]
        for idx, r in enumerate(riesgos_lista, 1):
            data2.append([str(idx), r.activo.nombre, r.amenaza[:35],
                          r.vulnerabilidad[:35], str(r.probabilidad),
                          str(r.impacto), str(r.nivel_riesgo), _clasificar(r.nivel_riesgo)])
        t2 = Table(data2, hAlign='LEFT', colWidths=[1*cm, 4*cm, 5*cm, 5*cm, 1.2*cm, 1.2*cm, 1.5*cm, 2.5*cm])
        nivel_colors = {'Bajo': colors.HexColor('#c3e6cb'), 'Moderado': colors.HexColor('#fff3cd'),
                        'Alto': colors.HexColor('#ffd8a8'), 'Crítico': colors.HexColor('#f5c6cb')}
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b1a1a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ALIGN', (4, 0), (-1, -1), 'CENTER'),
        ]
        for row_idx, r in enumerate(riesgos_lista, 1):
            cls = _clasificar(r.nivel_riesgo)
            style_cmds.append(('BACKGROUND', (7, row_idx), (7, row_idx), nivel_colors.get(cls, colors.white)))
        t2.setStyle(TableStyle(style_cmds))
        story.append(t2)
    else:
        story.append(Paragraph('No hay riesgos registrados.', styles['Normal']))
    story.append(Spacer(1, 0.4 * cm))

    # 3. Tratamientos
    story.append(Paragraph('3. Tratamiento de Riesgos (ISO/IEC 27002:2022)', h1_style))
    if tratamientos:
        data3 = [['#', 'Activo / Amenaza', 'Estrategia', 'Control ISO 27002:2022', 'Responsable', 'Fecha']]
        for idx, t_item in enumerate(tratamientos, 1):
            data3.append([
                str(idx),
                f"{t_item.riesgo.activo.nombre[:20]}\n{t_item.riesgo.amenaza[:25]}",
                t_item.estrategia,
                t_item.control_iso27002[:45],
                t_item.responsable[:20],
                t_item.fecha_registro.strftime('%d/%m/%Y')
            ])
        t3 = Table(data3, hAlign='LEFT', colWidths=[0.8*cm, 5*cm, 2.5*cm, 7*cm, 3*cm, 2.2*cm])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#155724')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph('No hay tratamientos registrados.', styles['Normal']))
    story.append(Spacer(1, 0.4 * cm))

    # 4. Riesgo Residual
    story.append(Paragraph('4. Cálculo de Riesgo Residual', h1_style))
    if residuales:
        data4 = [['#', 'Activo', 'Amenaza', 'Nivel Inicial', 'P Residual', 'I Residual', 'Nivel Residual', 'Reducción']]
        for idx, res in enumerate(residuales, 1):
            r = res.riesgo
            reduccion = r.nivel_riesgo - res.nivel_residual
            data4.append([
                str(idx), r.activo.nombre[:20], r.amenaza[:25],
                str(r.nivel_riesgo), str(res.probabilidad_residual),
                str(res.impacto_residual), str(res.nivel_residual),
                f'{reduccion:+d}'
            ])
        t4 = Table(data4, hAlign='LEFT', colWidths=[0.8*cm, 4*cm, 4.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.8*cm, 2.4*cm])
        t4.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5a3e8b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
            ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(t4)
    else:
        story.append(Paragraph('No hay riesgos residuales calculados.', styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    ts = datetime.now().strftime('%Y%m%d_%H%M')
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_riesgos_{ts}.pdf'
    return response
