from django.core.management.base import BaseCommand
from sheets_sync.services import fetch_sheet_data, validar_y_corregir_fila
from sheets_sync.models import BajaRetencion, LogCorreccion


class Command(BaseCommand):
    help = 'Sincroniza hoja Bajas_retenciones desde Google Sheets a MySQL'

    def add_arguments(self, parser):
        # Argumento opcional para solo ver sin guardar
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra los datos sin guardar en base de datos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 Modo dry-run — no se guardará nada\n'))

        # ── 1. Leer Google Sheets ────────────────────────────────────────
        self.stdout.write('📥 Conectando a Google Sheets...')
        try:
            rows = fetch_sheet_data()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al conectar con Google Sheets: {e}'))
            return

        if not rows:
            self.stdout.write(self.style.WARNING('⚠️  La hoja está vacía o no se encontraron datos'))
            return

        self.stdout.write(self.style.SUCCESS(f'✅ {len(rows)} filas encontradas en Sheets\n'))

        # ── 2. Procesar cada fila ────────────────────────────────────────
        creados      = 0
        actualizados = 0
        correcciones = 0
        errores      = 0
        omitidos     = 0

        for i, row in enumerate(rows, start=2):  # start=2 porque fila 1 es header

            # Omitir filas completamente vacías
            if not any(row.values()):
                omitidos += 1
                continue

            try:
                datos, advertencias = validar_y_corregir_fila(row)

                # Mostrar advertencias de corrección
                for campo, valor_orig, warn in advertencias:
                    self.stdout.write(f'  ⚠️  Fila {i} [{campo}]: {warn}')

                if dry_run:
                    self.stdout.write(f'  📋 Fila {i}: {datos}')
                    continue

                # ── 3. Guardar en MySQL ──────────────────────────────────
                # Clave única: telefono + fecha para evitar duplicados
                registro, created = BajaRetencion.objects.update_or_create(
                    telefono=datos['telefono'],
                    fecha=datos['fecha'],
                    defaults={
                        'cat':             datos['cat'],
                        'retencion_baja':  datos['retencion_baja'],
                        'motivo':          datos['motivo'],
                        'apoyo_utilizado': datos['apoyo_utilizado'],
                        'comentarios':     datos['comentarios'],
                        'tipo':            datos['tipo'],
                        'colonia':         datos['colonia'],
                        'fila_sheets':     i,
                    }
                )

                # ── 4. Guardar log de correcciones ───────────────────────
                for campo, valor_orig, warn in advertencias:
                    LogCorreccion.objects.create(
                        registro=registro,
                        campo=campo,
                        valor_original=valor_orig,
                        valor_corregido=warn,
                    )
                    correcciones += 1

                if created:
                    creados += 1
                    self.stdout.write(f'  ✅ Fila {i}: CREADO — {datos["telefono"]}')
                else:
                    actualizados += 1

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Fila {i}: {e} — datos: {row}')
                )
                continue

        # ── 5. Resumen final ─────────────────────────────────────────────
        self.stdout.write('\n' + '─' * 50)
        self.stdout.write(self.style.SUCCESS(
            f'📊 RESUMEN:\n'
            f'   ✅ Creados:      {creados}\n'
            f'   🔄 Actualizados: {actualizados}\n'
            f'   ⚠️  Correcciones: {correcciones}\n'
            f'   ⏭️  Omitidos:     {omitidos}\n'
            f'   ❌ Errores:      {errores}\n'
        ))