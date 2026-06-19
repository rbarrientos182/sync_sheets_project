# 📊 SyncSheets Platform

Sistema de sincronización, limpieza, almacenamiento y análisis de datos construido con **Django**, **PostgreSQL**, **Vue.js** y **Docker**.

SyncSheets automatiza la ingesta de información desde Google Sheets, aplica corrección inteligente de datos, almacena la información en una base de datos relacional y la expone mediante una API REST para análisis, dashboards y futuros modelos de Machine Learning.

---

## 🚀 Objetivo del Proyecto

Muchas organizaciones gestionan información operativa mediante hojas de cálculo compartidas. Sin embargo, los datos suelen presentar problemas de calidad como:

* Errores ortográficos
* Inconsistencias de formato
* Campos vacíos
* Duplicados
* Diferentes convenciones de captura

SyncSheets busca resolver este problema mediante un pipeline automatizado que:

1. Obtiene datos desde Google Sheets.
2. Limpia y normaliza la información.
3. Registra correcciones realizadas.
4. Almacena los datos en PostgreSQL.
5. Expone la información mediante una API REST.
6. Permite la construcción de dashboards analíticos.
7. Sirve como base para modelos de Machine Learning.

---

# 🏗 Arquitectura

```text
Google Sheets
       │
       ▼
Google Sheets API
       │
       ▼
SyncSheets (Django)
       │
       ▼
Data Cleaning & Validation
(Fuzzy Matching)
       │
       ▼
PostgreSQL
       │
       ├────────► API REST (DRF)
       │
       ├────────► Dashboard Vue.js
       │
       ▼
Machine Learning Pipeline
(Churn Prediction)
```

---

# ✨ Características

### 📥 Ingesta de Datos

* Lectura automática desde Google Sheets API v4
* Sincronización bajo demanda
* Preparado para sincronización periódica

### 🧹 Calidad de Datos

* Corrección automática mediante fuzzy matching
* Normalización de teléfonos
* Corrección de motivos
* Corrección de tipos de baja y retención
* Normalización de colonias
* Conversión de formatos de fecha

### 📝 Auditoría

* Registro detallado de correcciones
* Historial por campo modificado
* Trazabilidad de cambios

### 🌐 API REST

* Endpoints para consulta de registros
* Filtros dinámicos
* Consulta de estadísticas
* Consulta de logs de corrección

### 📊 Visualización

* Dashboard en Vue.js
* Integración con Chart.js
* Estadísticas en tiempo real

### 🐳 Contenedorización

* Docker
* Docker Compose
* PostgreSQL en contenedor

---

# 🛠 Stack Tecnológico

## Backend

* Python 3.12
* Django 6
* Django REST Framework

## Frontend

* Vue.js 3
* Chart.js

## Base de Datos

* PostgreSQL
* SQLite (desarrollo)

## Data Science

* Pandas
* NumPy
* Scikit-Learn
* Jupyter Notebook

## Integraciones

* Google Sheets API
* Google Drive API

## DevOps

* Docker
* Docker Compose

## Próximamente

* Celery
* Redis
* MLflow
* GitHub Actions

---

# 📁 Estructura del Proyecto

```text
sync_sheets_project/
│
├── manage.py
├── .env
├── .gitignore
├── requirements.txt
│
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── sheets_sync/
    ├── credentials.json
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── services.py
    ├── urls.py
    ├── admin.py
    └── management/
        └── commands/
            └── sync_sheets.py
```

---

# ⚙️ Requisitos

* Python 3.12+
* Docker
* Docker Compose
* PostgreSQL
* Node.js 18+
* Cuenta Google Cloud Platform

---

# 🚀 Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sync-sheets-platform.git

cd sync-sheets-platform
```

---

## 2. Configurar variables de entorno

Crear archivo:

```bash
.env
```

Contenido:

```env
# Google Sheets

SPREADSHEET_ID=tu_spreadsheet_id
SHEET_RANGE=Bajas_retenciones!A1:I1000
GOOGLE_CREDENTIALS_PATH=credentials.json

# SQLite (desarrollo)

DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# PostgreSQL (producción)

# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=postgres
# DB_USER=postgres
# DB_PASSWORD=password
# DB_HOST=db
# DB_PORT=5432
```

---

## 3. Levantar el entorno

```bash
docker compose up --build
```

---

## 4. Ejecutar migraciones

```bash
docker compose exec web python manage.py makemigrations

docker compose exec web python manage.py migrate
```

---

## 5. Verificar conexión con Google Sheets

```bash
docker compose exec web python manage.py shell
```

```python
from sheets_sync.services import fetch_sheet_data

rows = fetch_sheet_data()

print(f"Filas encontradas: {len(rows)}")
print(rows[0])
```

---

# ☁ Configuración de Google Cloud

1. Crear proyecto en Google Cloud.
2. Habilitar:

* Google Sheets API
* Google Drive API

3. Crear Service Account.
4. Descargar credentials.json.
5. Compartir el Google Sheet con el correo de la Service Account.

---

# 🔄 Sincronización

## Simulación

```bash
docker compose exec web python manage.py sync_sheets --dry-run
```

## Sincronización real

```bash
docker compose exec web python manage.py sync_sheets
```

Ejemplo:

```text
📥 Conectando a Google Sheets...

✅ 45 filas encontradas

⚠️ Teléfono corregido
⚠️ Colonia normalizada
⚠️ Motivo corregido

📊 RESUMEN

✅ Creados: 43
🔄 Actualizados: 2
⚠️ Correcciones: 8
❌ Errores: 0
```

---

# 🌐 API REST

## Registros

```http
GET /api/sheets/registros/
```

## Detalle

```http
GET /api/sheets/registros/{id}/
```

## Estadísticas

```http
GET /api/sheets/stats/
```

## Sincronización Manual

```http
POST /api/sheets/sync/
```

## Logs

```http
GET /api/sheets/logs/
```

---

# 🔍 Filtros Disponibles

```http
/api/sheets/registros/?tipo=BAJA

/api/sheets/registros/?tipo=RETENCION

/api/sheets/registros/?motivo=economia

/api/sheets/registros/?search=5512345678

/api/sheets/registros/?tipo=BAJA&motivo=economia
```

---

# 🗄 Modelos

## BajaRetencion

Representa registros sincronizados desde Google Sheets.

Campos principales:

* fecha
* cat
* telefono
* tipo
* motivo
* apoyo_utilizado
* comentarios
* colonia
* fila_sheets
* creado
* actualizado

---

## LogCorreccion

Auditoría de correcciones automáticas.

Campos:

* campo
* valor_original
* valor_corregido
* fecha

---

# 🛡 Reglas de Corrección Automática

| Campo    | Regla                          |
| -------- | ------------------------------ |
| fecha    | Conversión de formatos comunes |
| telefono | Limpieza y validación          |
| tipo     | Fuzzy matching                 |
| motivo   | Fuzzy matching                 |
| colonia  | Valor por defecto              |
| cat      | Limpieza y normalización       |

---

# 🤖 Machine Learning Roadmap

SyncSheets está evolucionando hacia una plataforma de análisis predictivo.

## Caso de Uso Inicial

### Churn Prediction

Predicción de abandono de clientes utilizando información histórica almacenada en PostgreSQL.

### Dataset utilizado

Telco Customer Churn Dataset (Kaggle) (prueba)

### Pipeline desarrollado

* Exploratory Data Analysis (EDA)
* Data Cleaning
* Feature Engineering
* Entrenamiento de modelos
* Evaluación y métricas
* Generación del modelo entrenado

### Próximas fases

* Integración del modelo en Django
* Endpoint de inferencia
* Dashboard predictivo
* Reentrenamiento automático
* Monitoreo de desempeño

---

# 📈 Estado Actual

## Backend

✅ Integración Google Sheets

✅ PostgreSQL

✅ API REST

✅ Corrección automática

✅ Docker

## Data Science

✅ Dataset de churn procesado (Prueba)

✅ EDA completado

✅ Modelo inicial entrenado

🚧 Integración del modelo

## Frontend

🚧 Dashboard Vue.js

## Cloud

🚧 Deploy OCI

## MLOps

🚧 Celery

🚧 Redis

🚧 MLflow

🚧 GitHub Actions

---

# 🚀 Roadmap

## Fase 1 — Data Ingestion

✅ Google Sheets API

✅ Limpieza automática

✅ PostgreSQL

✅ API REST

## Fase 2 — Analytics

🚧 Dashboard Vue.js

🚧 Visualización avanzada

## Fase 3 — Machine Learning

🚧 Churn Prediction

🚧 Endpoint de inferencia

🚧 Dashboard predictivo

## Fase 4 — MLOps

🚧 Celery

🚧 Redis

🚧 MLflow

🚧 Model Registry

## Fase 5 — Cloud

🚧 OCI Deployment

🚧 CI/CD

🚧 Observabilidad

---

# 🔒 Seguridad

Nunca subir al repositorio:

```gitignore
.env
credentials.json
venv/
__pycache__/
*.pyc
db.sqlite3
```

---

# 👨‍💻 Autor

**Roberto Alfonso Barrientos Balbuena**

Ingeniero en Sistemas Computacionales
Maestro en Desarrollo de Software
Data Science & Machine Learning Enthusiast
Puebla, México

---

# 📄 Licencia

MIT License

Libre para usar, modificar y distribuir.
