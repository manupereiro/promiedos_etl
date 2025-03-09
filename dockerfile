FROM apache/airflow:latest

USER root

# Si el usuario airflow no existe, crearlo
RUN id airflow || adduser --disabled-password --gecos "" airflow

# Actualizar e instalar paquetes requeridos, incluyendo dependencias de Chrome
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    gnupg \
    curl \
    wget \
    unzip \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils

# Agregar el repositorio de Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Importar la llave pública de Google Cloud
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Actualizar e instalar Google Cloud SDK
RUN apt-get update && apt-get install -y google-cloud-sdk

# Instalar Google Chrome y sus dependencias
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean

# Copiar el archivo de requirements y otros archivos necesarios
COPY requirements.txt /tmp/requirements.txt

# Volver al usuario airflow para instalar paquetes de Python
USER airflow
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copiar DAGs y plugins
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root airflow/plugins /opt/airflow/plugins

USER airflow