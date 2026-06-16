# Django 6.x es altamente compatible con Python 3.12 o 3.13. 
# Usaremos 3.12-slim por estabilidad y buen soporte.
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de Google y DB
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto donde corre Django
EXPOSE 8000

# Comando para arrancar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]