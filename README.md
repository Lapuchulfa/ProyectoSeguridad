# ProyectoSeguridad — Sistema de Gestión de Riesgos de Seguridad Informática

Aplicación web desarrollada en Flask para la gestión integral de riesgos de seguridad de la información, alineada con los controles de la norma **ISO/IEC 27002**.

## Características

- **Autenticación** — registro e inicio de sesión de usuarios con contraseñas hasheadas (Werkzeug).
- **Activos** — inventario de activos de información con valoración por criterios CIA (Confidencialidad, Integridad, Disponibilidad).
- **Riesgos** — identificación y calificación de riesgos (probabilidad × impacto) por activo.
- **Tratamiento** — definición de estrategia de tratamiento y controles ISO 27002 para cada riesgo.
- **Riesgo Residual** — re-evaluación del riesgo tras aplicar los controles.
- **Observaciones** — bitácora de comentarios transversales por módulo.
- **Reportes** — generación de reportes en PDF con ReportLab.
- **Dashboard** — resumen ejecutivo del estado de riesgos de la organización.

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.13 / Flask 3.1 |
| ORM | Flask-SQLAlchemy 3.1 / SQLite |
| Autenticación | Flask-Login 0.6 |
| Formularios / CSRF | Flask-WTF 1.3 |
| Generación de PDF | ReportLab 4.5 |
| Templates | Jinja2 |

## Requisitos previos

- Python 3.13+
- `pip` o `pipenv`

## Instalación

### Con pip (recomendado para producción)

```bash
# 1. Clonar el repositorio
git clone https://github.com/Lapuchulfa/ProyectoSeguridad.git
cd ProyectoSeguridad

# 2. Crear y activar entorno virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env y reemplazar SECRET_KEY con un valor seguro
```

### Con Pipenv

```bash
pipenv install
pipenv shell
```

## Configuración

Copia el archivo de ejemplo y genera una clave secreta aleatoria:

```bash
cp .env.example .env
```

Contenido de `.env`:

```
SECRET_KEY=<cadena-hexadecimal-aleatoria-de-32-bytes>
```

Puedes generar una clave con Python:

```python
import secrets
print(secrets.token_hex(32))
```

> **Nunca** subas el archivo `.env` real al repositorio. Ya está incluido en `.gitignore`.

## Ejecución

```bash
python app.py
```

La base de datos SQLite se crea automáticamente en `instance/database.db` la primera vez que se ejecuta la app.

Accede en el navegador: [http://localhost:5000](http://localhost:5000)

## Estructura del proyecto

```
ProyectoSeguridad/
├── app.py                  # Punto de entrada de la aplicación
├── config.py               # Configuración (carga .env)
├── models/
│   └── models.py           # Modelos SQLAlchemy (Usuario, Activo, Riesgo, ...)
├── routes/
│   ├── auth.py             # Registro / login / perfil
│   ├── dashboard.py        # Panel principal
│   ├── activos.py          # CRUD de activos
│   ├── riesgos.py          # CRUD de riesgos
│   ├── tratamiento.py      # Tratamiento de riesgos
│   ├── residual.py         # Riesgo residual
│   ├── observaciones.py    # Observaciones / bitácora
│   └── reportes.py         # Generación de reportes PDF
├── templates/              # Plantillas Jinja2
├── requirements.txt        # Dependencias Python
├── Pipfile                 # Alternativa con Pipenv
└── .env.example            # Plantilla de variables de entorno
```

## Clasificación de niveles de riesgo

| Nivel (P × I) | Clasificación |
|---|---|
| 1 – 6 | Bajo |
| 7 – 12 | Moderado |
| 13 – 18 | Alto |
| 19 – 25 | Crítico |

## Seguridad

- Contraseñas almacenadas con hash mediante `werkzeug.security`.
- Protección CSRF habilitada globalmente con `Flask-WTF`.
- La `SECRET_KEY` se carga desde variables de entorno; nunca se incluye en el código.
- La base de datos `instance/` y el archivo `.env` están excluidos del repositorio vía `.gitignore`.

## Licencia

Proyecto académico — Universidad de Las Américas (UDLA). Uso educativo.
