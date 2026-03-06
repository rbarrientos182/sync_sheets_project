# 📊 SyncSheets — Google Sheets → Django + PostgreSQL/SQLite

Sincronización automática de datos desde Google Sheets hacia una base de datos relacional (SQLite en desarrollo, PostgreSQL en producción), con corrección automática de datos, API REST y dashboard en Vue.js.

---

## ✨ Características

- Lectura automática de Google Sheets vía **Google Sheets API v4**
- Corrección automática de datos con **fuzzy matching** (estatus, motivos, colonias, teléfonos)
- Log de correcciones por registro
- API REST con **Django REST Framework**
- Dashboard de visualización en **Vue.js + Chart.js**
- Sincronización periódica con **Celery + Redis** *(próximamente)*

---

## 🗂 Estructura del proyecto

```
sync_sheets_project/
│
├── manage.py
├── .env                          # Variables de entorno (no subir a git)
├── .gitignore
├── credentials.json              # Service Account de Google Cloud (no subir a git)
├── requirements.txt
│
├── core/                         # Configuración principal de Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── sheets_sync/                  # App principal
    ├── models.py                 # BajaRetencion + LogCorreccion
    ├── serializers.py            # Serializers DRF
    ├── views.py                  # Endpoints con @api_view
    ├── services.py               # Lógica de Google Sheets + corrección de datos
    ├── urls.py                   # Rutas de la app
    ├── admin.py
    └── management/
        └── commands/
            └── sync_sheets.py    # Comando: python manage.py sync_sheets
```

---

## ⚙️ Requisitos

- Python 3.10+
- Node.js 18+ *(para el dashboard Vue.js)*
- SQLite *(desarrollo)* / PostgreSQL *(producción)*
- Cuenta en [Google Cloud Console](https://console.cloud.google.com)

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sync-sheets-project.git
cd sync-sheets-project
```

### 2. Crear y activar entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Google Sheets
SPREADSHEET_ID=tu_spreadsheet_id_aqui
SHEET_RANGE=Bajas_retenciones!A1:I1000
GOOGLE_CREDENTIALS_PATH=credentials.json

# Base de datos — SQLite (desarrollo)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Base de datos — PostgreSQL (producción)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=nombre_base
# DB_USER=postgres
# DB_PASSWORD=tu_password
# DB_HOST=localhost
# DB_PORT=5432
```

### 5. Configurar Google Cloud

1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. Habilita **Google Sheets API** y **Google Drive API**
3. Crea una **Service Account** con rol `Viewer`
4. Descarga el `credentials.json` y colócalo en la raíz del proyecto
5. Copia el `client_email` del JSON y comparte tu Google Sheet con ese correo como **Lector**

### 6. Migrar base de datos

```bash
python manage.py makemigrations sheets_sync
python manage.py migrate
```

### 7. Probar la conexión con Google Sheets

```bash
python manage.py shell
```

```python
from sheets_sync.services import fetch_sheet_data

rows = fetch_sheet_data()
print(f"Filas encontradas: {len(rows)}")
print("Primera fila:", rows[0])
```

---

## 🔄 Sincronización

### Prueba sin guardar (dry-run)

```bash
python manage.py sync_sheets --dry-run
```

### Sincronización real

```bash
python manage.py sync_sheets
```

Salida esperada:

```
📥 Conectando a Google Sheets...
✅ 45 filas encontradas en Sheets

  ⚠️  Fila 5 [telefono]: Teléfono '55 123-456-78' → '5512345678'
  ⚠️  Fila 8 [colonia]: Colonia vacía → asignado 'Sin Colonia'
  ⚠️  Fila 12 [motivo]: motivo 'Economía' → 'ECONOMIA'

──────────────────────────────────────────────────
📊 RESUMEN:
   ✅ Creados:      43
   🔄 Actualizados: 2
   ⚠️  Correcciones: 8
   ⏭️  Omitidos:     0
   ❌ Errores:      0
```

---

## 🌐 API Endpoints

Arranca el servidor:

```bash
python manage.py runserver
```

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/sheets/registros/` | Lista todos los registros |
| GET | `/api/sheets/registros/<id>/` | Detalle de un registro |
| GET | `/api/sheets/stats/` | Estadísticas para el dashboard |
| POST | `/api/sheets/sync/` | Dispara sincronización manual |
| GET | `/api/sheets/logs/` | Log de correcciones automáticas |

### Filtros disponibles en `/registros/`

```
/api/sheets/registros/?tipo=BAJA
/api/sheets/registros/?tipo=RETENCION
/api/sheets/registros/?motivo=economia
/api/sheets/registros/?search=5512345678
/api/sheets/registros/?tipo=BAJA&motivo=economia
```

---

## 🗃 Modelos

### `BajaRetencion`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fecha` | DateField | Fecha del registro |
| `cat` | CharField | Identificador CAT |
| `telefono` | CharField | Teléfono (10 dígitos) |
| `retencion_baja` | CharField | RETENCION / BAJA |
| `tipo` | CharField | RETENCION / BAJA (con choices) |
| `motivo` | CharField | Motivo del catálogo |
| `apoyo_utilizado` | CharField | Apoyo aplicado |
| `comentarios` | TextField | Texto libre |
| `colonia` | CharField | Colonia o "Sin Colonia" |
| `fila_sheets` | IntegerField | Número de fila en el Sheet |
| `creado` | DateTimeField | Fecha de creación |
| `actualizado` | DateTimeField | Última actualización |

### `LogCorreccion`

Registra cada corrección automática aplicada sobre un registro:

| Campo | Descripción |
|-------|-------------|
| `campo` | Nombre del campo corregido |
| `valor_original` | Valor tal como vino del Sheet |
| `valor_corregido` | Descripción de la corrección aplicada |
| `fecha` | Timestamp de la corrección |

---

## 🛡 Corrección automática de datos

| Campo | Regla |
|-------|-------|
| `fecha` | Acepta `dd/mm/yyyy`, `yyyy-mm-dd`, `dd-mm-yyyy`, etc. |
| `telefono` | Elimina caracteres no numéricos, valida 10 dígitos |
| `tipo` | Fuzzy matching contra catálogo `BAJA` / `RETENCION` |
| `motivo` | Fuzzy matching contra 14 motivos del catálogo |
| `colonia` | Si viene vacía asigna `"Sin Colonia"` |
| `cat` | Solo limpieza de espacios, guarda en mayúsculas |

---

## 📦 requirements.txt

```
django>=4.2
djangorestframework>=3.15
python-dotenv>=1.0
google-auth>=2.29
google-api-python-client>=2.126
psycopg2-binary>=2.9      # PostgreSQL
# mysqlclient>=2.2         # MySQL (alternativa)
```

---

## 🔒 Seguridad

Los siguientes archivos **nunca** deben subirse al repositorio:

```
# .gitignore
.env
credentials.json
venv/
__pycache__/
*.pyc
db.sqlite3
```

---

## 🗺 Roadmap

- [x] Conexión Google Sheets API
- [x] Corrección automática de datos con fuzzy matching
- [x] API REST con Django REST Framework
- [x] Log de correcciones por registro
- [ ] Celery + Redis para sincronización automática periódica
- [ ] Dashboard Vue.js con Chart.js
- [ ] Migración a PostgreSQL en producción
- [ ] Autenticación JWT en la API
- [ ] Deploy en servidor (Railway / Render / VPS)

---

## 👤 Autor

**Roberto Alfonso Barrientos Balbuena**  
Puebla, México

---

## 📄 Licencia

MIT License — libre para usar y modificar.