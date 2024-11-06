# Usa una imagen base de Python
FROM python:3.8-slim

# Instalación de dependencias necesarias
RUN apt-get update && apt-get install -y \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear y cambiar al directorio de trabajo
WORKDIR /app

# Copiar solo el archivo de dependencias primero para instalar paquetes de Python
COPY requirements.txt /app/

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código al contenedor
COPY . /app

# Exponer el puerto en el que Flask estará corriendo
EXPOSE 5000

# Ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]
