FROM python:3.12-slim

WORKDIR /app

# Copia los archivos de gestión de dependencias
COPY pyproject.toml poetry.lock* ./

# Instala Poetry y las dependencias
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copia el resto del código
COPY . .

# Crea el directorio de templates si no existe
RUN mkdir -p web_interface/templates

# Instalar Flask-CORS para permitir el uso de iframe
RUN pip install flask-cors

# Variable de entorno para Cloud Run
ENV PORT=8080

# Comando para iniciar la aplicación
CMD ["python", "web_interface/app.py"]
