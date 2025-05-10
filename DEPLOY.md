# Despliegue de la Aplicación Web del Agente en Google Cloud Run

Este documento proporciona instrucciones paso a paso para desplegar la interfaz web de tu agente en Google Cloud Run, haciéndola accesible públicamente.

## Requisitos Previos

1. Cuenta de Google Cloud con facturación habilitada
2. Google Cloud CLI instalada en tu computadora

## Pasos para el Despliegue

### 1. Instalar Google Cloud SDK

- Descarga e instala el [SDK de Google Cloud](https://cloud.google.com/sdk/docs/install)
- Abre una terminal (PowerShell o CMD) y ejecuta:

```powershell
gcloud auth login
```

- Sigue las instrucciones para iniciar sesión en tu cuenta de Google

### 2. Configurar el Proyecto

```powershell
gcloud config set project agent01-458901
```

### 3. Habilitar APIs Necesarias

```powershell
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 4. Construir y Desplegar la Aplicación

Desde la carpeta raíz del proyecto, ejecuta:

```powershell
# Construir la imagen
gcloud builds submit --tag gcr.io/agent01-458901/agent-web-interface

# Desplegar en Cloud Run
gcloud run deploy agent-web-interface --image gcr.io/agent01-458901/agent-web-interface --platform managed --region us-central1 --allow-unauthenticated
```

La opción `--allow-unauthenticated` permite que cualquier persona acceda a la aplicación. Omítela si deseas restringir el acceso.

### 5. Configurar Variables de Entorno

Desde la consola de Google Cloud:

1. Ve a [Cloud Run](https://console.cloud.google.com/run)
2. Selecciona tu servicio "agent-web-interface"
3. Haz clic en "Editar y desplegar nueva revisión"
4. En la sección "Variables de entorno", agrega:
   - `GOOGLE_CLOUD_PROJECT`: agent01-458901
   - `GOOGLE_CLOUD_LOCATION`: us-central1 (o la región elegida)
   - `GOOGLE_CLOUD_STAGING_BUCKET`: el nombre de tu bucket
   - `RESOURCE_ID`: 575132542257070080

5. Haz clic en "Desplegar"

### 6. Acceder a la Aplicación

Una vez completado el despliegue, encontrarás la URL de tu aplicación en la consola de Google Cloud. Será algo como:
`https://agent-web-interface-abcdefghij-uc.a.run.app`

## Solución de Problemas

- **Problemas de autenticación**: Asegúrate de que la cuenta de servicio de Cloud Run tiene permisos para acceder a Vertex AI
- **Errores de variables**: Verifica que todas las variables de entorno estén correctamente configuradas
- **Revisar logs**: Ve a Cloud Run > agent-web-interface > Logs para diagnosticar problemas

## Actualizar la Aplicación

Para actualizar tu aplicación después de cambios:

```powershell
gcloud builds submit --tag gcr.io/agent01-458901/agent-web-interface
gcloud run deploy agent-web-interface --image gcr.io/agent01-458901/agent-web-interface --platform managed
```
