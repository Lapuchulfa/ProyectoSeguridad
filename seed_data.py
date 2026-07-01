"""
Script de datos de prueba.
Crea (o reutiliza) un usuario demo y llena activos, riesgos, tratamientos,
riesgos residuales y observaciones cubriendo todos los tipos de activo
y todos los niveles de criticidad (Bajo, Moderado, Alto, Crítico).

Uso:
    python seed_data.py
"""
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from app import app
from models.models import db, Usuario, Activo, Riesgo, Tratamiento, RiesgoResidual, Observacion

DEMO_CORREO = 'miguel123@correo.com'
DEMO_PASSWORD = 'miguel123'

# (tipo, nombre, descripcion, confidencialidad, integridad, disponibilidad)
ACTIVOS_DATA = [
    ('Hardware', 'Servidor de Base de Datos Principal', 'Servidor físico que aloja la BD transaccional de la empresa.', 5, 5, 5),
    ('Hardware', 'Estaciones de trabajo administrativas', 'Equipos de escritorio del área administrativa.', 2, 2, 2),
    ('Software', 'Sistema ERP', 'Plataforma de gestión de recursos empresariales.', 5, 4, 4),
    ('Software', 'Antivirus corporativo', 'Solución de protección de endpoints.', 2, 3, 3),
    ('Redes', 'Firewall perimetral', 'Dispositivo de seguridad de borde de red.', 4, 5, 5),
    ('Redes', 'Red Wi-Fi de invitados', 'Red inalámbrica de acceso público en oficinas.', 1, 1, 2),
    ('Datos / Información', 'Base de datos de clientes', 'Información personal y financiera de clientes (PII).', 5, 5, 4),
    ('Datos / Información', 'Repositorio de documentos internos', 'Documentación operativa no confidencial.', 1, 2, 2,),
    ('Personal', 'Administrador de sistemas', 'Personal con acceso privilegiado a infraestructura crítica.', 4, 3, 3),
    ('Personal', 'Personal de soporte técnico', 'Mesa de ayuda de primer nivel.', 1, 1, 1),
    ('Instalaciones', 'Centro de datos (Data Center)', 'Sala de servidores con control de acceso físico.', 4, 4, 5),
    ('Instalaciones', 'Oficinas administrativas', 'Espacio físico de trabajo general.', 1, 1, 1),
    ('Servicios Externos', 'Proveedor de hosting en la nube', 'Servicio de infraestructura como servicio (IaaS).', 4, 4, 5),
    ('Servicios Externos', 'Servicio de correo electrónico externo', 'Plataforma de correo corporativo tercerizada.', 3, 3, 3),
]

# (nombre_activo, amenaza, vulnerabilidad, probabilidad, impacto, con_tratamiento, con_residual)
RIESGOS_DATA = [
    ('Servidor de Base de Datos Principal', 'Ataque de ransomware', 'Ausencia de segmentación de red y backups desactualizados.', 5, 5, True, True),
    ('Servidor de Base de Datos Principal', 'Corte del suministro eléctrico', 'No existe UPS de respaldo suficiente.', 3, 4, True, False),
    ('Estaciones de trabajo administrativas', 'Difusión de software dañino (malware)', 'Usuarios con permisos de instalación local.', 3, 2, True, True),
    ('Sistema ERP', 'Explotación de vulnerabilidades técnicas', 'Versión desactualizada sin parches de seguridad.', 4, 5, True, False),
    ('Sistema ERP', 'Abuso de privilegios de acceso', 'Roles de usuario mal configurados.', 3, 3, False, False),
    ('Antivirus corporativo', 'Errores del administrador del sistema', 'Actualización de firmas de virus manual e inconsistente.', 2, 2, False, False),
    ('Firewall perimetral', 'Acceso no autorizado al sistema', 'Reglas de firewall permisivas heredadas.', 3, 5, True, True),
    ('Firewall perimetral', 'Denegación de servicio (DoS/DDoS)', 'Sin mitigación de tráfico anómalo.', 4, 4, True, False),
    ('Red Wi-Fi de invitados', 'Interceptación de comunicaciones (Man-in-the-Middle)', 'Cifrado WPA2 con contraseña compartida y no rotada.', 3, 2, False, False),
    ('Base de datos de clientes', 'Divulgación de información confidencial', 'Datos sin cifrar en reposo.', 4, 5, True, True),
    ('Base de datos de clientes', 'Fraude informático / Ingeniería social', 'Falta de capacitación en manejo de datos sensibles.', 3, 5, True, False),
    ('Repositorio de documentos internos', 'Errores de los usuarios', 'Ausencia de control de versiones.', 2, 1, False, False),
    ('Administrador de sistemas', 'Suplantación de identidad', 'Autenticación sin doble factor (2FA).', 3, 4, True, True),
    ('Personal de soporte técnico', 'Phishing / Spear Phishing', 'Filtrado de correo básico sin capacitación periódica.', 4, 2, False, False),
    ('Centro de datos (Data Center)', 'Desastres naturales', 'Ubicación en zona de riesgo sísmico sin plan de continuidad.', 2, 5, True, False),
    ('Centro de datos (Data Center)', 'Robo de equipos', 'Control de acceso físico con vigilancia limitada.', 2, 4, False, False),
    ('Oficinas administrativas', 'Fuego', 'Sistema contraincendios sin mantenimiento reciente.', 1, 3, False, False),
    ('Proveedor de hosting en la nube', 'Interrupción de servicios de terceros', 'Sin acuerdo de nivel de servicio (SLA) de alta disponibilidad.', 3, 4, True, True),
    ('Servicio de correo electrónico externo', 'Ataques de fuerza bruta', 'Política de contraseñas débil en cuentas de correo.', 3, 3, False, False),
]


def run():
    with app.app_context():
        usuario = Usuario.query.filter_by(correo=DEMO_CORREO).first()
        if usuario:
            print(f'Usuario existente encontrado (id={usuario.id}). Limpiando datos previos...')
            # Se borran uno por uno (no bulk delete) para que SQLAlchemy dispare
            # el cascade="all, delete-orphan" sobre riesgos/tratamientos/residuales.
            for activo in Activo.query.filter_by(usuario_id=usuario.id).all():
                db.session.delete(activo)
            for obs in Observacion.query.filter_by(usuario_id=usuario.id).all():
                db.session.delete(obs)
            db.session.commit()
        else:
            usuario = Usuario(
                nombre='Usuario Demo',
                correo=DEMO_CORREO,
                password=generate_password_hash(DEMO_PASSWORD)
            )
            db.session.add(usuario)
            db.session.commit()
            print(f'Usuario demo creado (id={usuario.id}).')

        activos_por_nombre = {}
        for tipo, nombre, descripcion, c, i, d in ACTIVOS_DATA:
            activo = Activo(
                usuario_id=usuario.id,
                nombre=nombre,
                tipo=tipo,
                descripcion=descripcion,
                confidencialidad=c,
                integridad=i,
                disponibilidad=d,
                valor_total=max(c, i, d)
            )
            db.session.add(activo)
            activos_por_nombre[nombre] = activo
        db.session.commit()
        print(f'{len(ACTIVOS_DATA)} activos creados.')

        estrategias = ['Mitigar', 'Transferir', 'Aceptar', 'Evitar']
        responsables = ['Jefe de TI', 'Oficial de Seguridad', 'Administrador de Redes', 'Gerente de Operaciones']

        total_riesgos = 0
        total_tratamientos = 0
        total_residuales = 0
        for idx, (nombre_activo, amenaza, vulnerabilidad, p, im, con_trat, con_resid) in enumerate(RIESGOS_DATA):
            activo = activos_por_nombre[nombre_activo]
            riesgo = Riesgo(
                activo_id=activo.id,
                amenaza=amenaza,
                vulnerabilidad=vulnerabilidad,
                probabilidad=p,
                impacto=im,
                nivel_riesgo=p * im
            )
            db.session.add(riesgo)
            db.session.flush()
            total_riesgos += 1

            if con_trat:
                tratamiento = Tratamiento(
                    riesgo_id=riesgo.id,
                    estrategia=estrategias[idx % len(estrategias)],
                    control_iso27002=f'A.{8 + (idx % 10)}.{1 + (idx % 5)} - Control asociado ISO/IEC 27002',
                    detalles_control='Implementación de control definido en el plan de tratamiento de riesgos.',
                    responsable=responsables[idx % len(responsables)],
                    fecha_registro=datetime.utcnow() - timedelta(days=idx)
                )
                db.session.add(tratamiento)
                total_tratamientos += 1

                if con_resid:
                    p_res = max(1, p - 2)
                    i_res = max(1, im - 2)
                    residual = RiesgoResidual(
                        riesgo_id=riesgo.id,
                        probabilidad_residual=p_res,
                        impacto_residual=i_res,
                        nivel_residual=p_res * i_res
                    )
                    db.session.add(residual)
                    total_residuales += 1

        db.session.commit()
        print(f'{total_riesgos} riesgos creados ({total_tratamientos} con tratamiento, {total_residuales} con riesgo residual).')

        observaciones_data = [
            ('activos', 'Revisar la clasificación CID del ERP tras la última auditoría.', 'Auditor Interno'),
            ('riesgos', 'Priorizar tratamiento de riesgos críticos del Data Center este trimestre.', 'Oficial de Seguridad'),
            ('tratamiento', 'Confirmar cierre del plan de acción para el firewall perimetral.', 'Jefe de TI'),
        ]
        for origen, comentario, autor in observaciones_data:
            db.session.add(Observacion(
                usuario_id=usuario.id,
                origen_modulo=origen,
                comentario=comentario,
                autor_nombre=autor
            ))
        db.session.commit()
        print(f'{len(observaciones_data)} observaciones creadas.')

        print('\nListo. Inicia sesión con:')
        print(f'  Correo:     {DEMO_CORREO}')
        print(f'  Contraseña: {DEMO_PASSWORD}')


if __name__ == '__main__':
    run()
