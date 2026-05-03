# management/commands/sync_sheets.py
from django.core.management.base import BaseCommand
from sheets_sync.services import fetch_sheet_data, validar_y_corregir_fila
from sheets_sync.models import BajaRetencion, LogCorreccion

class Command(BaseCommand):
    help = 'Sincroniza Bajas_retenciones desde Google Sheets'

    def handle(self, *args, **kwargs):
        self.stdout.write('📥 Leyendo Google Sheets...')
        rows = fetch_sheet_data()
        creados = actualizados = correcciones = errores = 0

        for i, row in enumerate(rows, start=2):
            try:
                datos, advertencias = validar_y_corregir_fila(row)

                # Clave única: telefono + fecha
                registro, created = BajaRetencion.objects.update_or_create(
                    telefono=datos['telefono'],
                    fecha=datos['fecha'],
                    defaults={**datos, 'fila_sheets': i}
                )

                for campo, valor_orig, warn in advertencias:
                    LogCorreccion.objects.create(
                        registro=registro,
                        campo=campo,
                        valor_original=valor_orig,
                        valor_corregido=warn,
                    )
                    correcciones += 1
                    self.stdout.write(f'  ⚠️  Fila {i}: {warn}')

                if created: creados += 1
                else: actualizados += 1

            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f'  ❌ Fila {i}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Creados: {creados} | Actualizados: {actualizados} '
            f'| Correcciones: {correcciones} | Errores: {errores}'
        ))