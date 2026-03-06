import re
from datetime import datetime
from difflib import get_close_matches
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# ── Catálogos exactos de tu Sheet ───────────────────────────────────────────

RETENCION_BAJA_VALIDOS = ['baja', 'retencion']

MOTIVOS_VALIDOS = [
    'calidad de servicio',
    'cambio de compania',
    'cambio de residencia',
    'cambio residencia zona sin red',
    'cargos no reconocidos',
    'cierre de negocio',
    'defuncion',
    'economia',
    'escalacion de queja',
    'facturacion',
    'oferta comercial',
    'oferta de la competencia',
    'reestructura cuenta maestra',
    'reventa',
]

TIPOS_VALIDOS = ['residencial', 'comercial']


# ── Conexión a Google Sheets ─────────────────────────────────────────────────

def get_sheets_service():
    creds = Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS_PATH,
        scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)


def fetch_sheet_data():
    service = get_sheets_service()
    result  = service.spreadsheets().values().get(
        spreadsheetId=settings.SPREADSHEET_ID,
        range=settings.SHEET_RANGE
    ).execute()

    rows = result.get('values', [])
    if not rows:
        return []

    # ✅ Normalizar encabezados — ahora incluye ñ y ú
    headers = [h.strip().lower()
                .replace(' ', '_')
                .replace('á', 'a')
                .replace('é', 'e')
                .replace('í', 'i')
                .replace('ó', 'o')
                .replace('ú', 'u')
                .replace('ñ', 'n')
               for h in rows[0]]

    data = []
    for row in rows[1:]:
        row_completa = row + [''] * (len(headers) - len(row))
        data.append(dict(zip(headers, row_completa)))

    return data


# ── Helpers de limpieza ──────────────────────────────────────────────────────

def normalizar(texto):
    if not texto:
        return ''
    texto = texto.strip().lower()
    for k, v in {
        'á':'a','é':'e','í':'i','ó':'o','ú':'u',
        'ä':'a','ë':'e','ï':'i','ö':'o','ü':'u','ñ':'n'
    }.items():
        texto = texto.replace(k, v)
    return texto


def corregir_con_catalogo(valor, catalogo, campo):
    if not valor:
        return '', f"{campo} vacío"

    norm = normalizar(valor)

    if norm in catalogo:
        return norm.upper(), None

    match = get_close_matches(norm, catalogo, n=1, cutoff=0.6)
    if match:
        return match[0].upper(), f"{campo} '{valor}' corregido → '{match[0].upper()}'"

    return norm.upper(), f"{campo} '{valor}' no reconocido en catálogo"


def limpiar_telefono(valor):
    if not valor:
        return '', 'Teléfono vacío'
    solo_num = re.sub(r'\D', '', valor)
    if len(solo_num) == 10:
        return solo_num, None
    return solo_num, f"Teléfono '{valor}' tiene {len(solo_num)} dígitos (esperado 10)"


def parsear_fecha(valor):
    if not valor or not valor.strip():
        return None, 'Fecha vacía'

    formatos = [
        '%d/%m/%Y', '%d/%m/%y',
        '%Y-%m-%d', '%d-%m-%Y',
        '%m/%d/%Y', '%d.%m.%Y',
    ]
    for fmt in formatos:
        try:
            return datetime.strptime(valor.strip(), fmt).date(), None
        except ValueError:
            continue

    return None, f"Fecha '{valor}' no reconocida — revisa el formato"


def limpiar_colonia(valor):
    limpio = valor.strip().title() if valor else ''
    if not limpio:
        return 'Sin Colonia', "Colonia vacía → asignado 'Sin Colonia'"
    return limpio, None


# ── Validación y corrección principal ───────────────────────────────────────

def validar_y_corregir_fila(row):
    advertencias = []
    datos = {}

    # Fecha
    datos['fecha'], warn = parsear_fecha(row.get('fecha', ''))
    if warn:
        advertencias.append(('fecha', row.get('fecha', ''), warn))

    # CAT
    datos['cat'] = row.get('cat', '').strip().upper()

    # Teléfono
    datos['telefono'], warn = limpiar_telefono(row.get('telefono', ''))
    if warn:
        advertencias.append(('telefono', row.get('telefono', ''), warn))

    # ✅ Retención o Baja — key corregido
    val_ret = row.get('retencion_o_baja', '')
    datos['retencion_baja'], warn = corregir_con_catalogo(
        val_ret, RETENCION_BAJA_VALIDOS, 'retencion_baja'
    )
    if warn:
        advertencias.append(('retencion_baja', val_ret, warn))

    # Motivo
    datos['motivo'], warn = corregir_con_catalogo(
        row.get('motivo', ''), MOTIVOS_VALIDOS, 'motivo'
    )
    if warn:
        advertencias.append(('motivo', row.get('motivo', ''), warn))

    # Apoyo utilizado
    datos['apoyo_utilizado'] = row.get('apoyo_utilizado', '').strip().title()

    # Comentarios
    datos['comentarios'] = row.get('comentarios', '').strip()

    # Tipo — ahora RESIDENCIAL / COMERCIAL
    datos['tipo'], warn = corregir_con_catalogo(
        row.get('tipo', ''), TIPOS_VALIDOS, 'tipo'
    )
    if warn:
        advertencias.append(('tipo', row.get('tipo', ''), warn))

    # Colonia
    datos['colonia'], warn = limpiar_colonia(row.get('colonia', ''))
    if warn:
        advertencias.append(('colonia', row.get('colonia', ''), warn))

    return datos, advertencias