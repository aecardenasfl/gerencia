# Tienda IoT - Gestión de Inventario con Sensores y FastAPI

Este proyecto es una aplicación web desarrollada en **Python** usando **FastAPI** para la gestión de inventario de una tienda. La particularidad es que el stock de productos se actualiza automáticamente mediante **sensores IoT** que reportan cantidades a un servidor **MQTT (Mosquitto)**.

El proyecto sigue un patrón **MVC** y utiliza **PostgreSQL** como base de datos.

---

## Características principales

- CRUD completo de usuarios y productos vía API REST.
- Actualización automática de inventario desde sensores conectados a MQTT.
- Notificaciones automáticas para administradores cuando el stock está bajo o agotado.
- Validación de usuarios con contraseñas hasheadas usando `bcrypt`.
- Arquitectura modular (DAO, Servicios, Controladores, Sensor Handler).

---

## Tecnologías

- Python 3.11+
- FastAPI
- PostgreSQL
- MQTT (Mosquitto)
- Redis (opcional)
- Paho-MQTT
- Bcrypt

---

## Configuración del entorno

1. Crear un archivo `.env` dentro de la carpeta `config` con las credenciales de la base de datos y MQTT:

```dotenv
# --- PostgreSQL ---
PGHOST=localhost
PGPORT=5432
PGUSER=admin
PGPASSWORD=password123
PGDATABASE=ejemplo

# --- MQTT ---
MQTT_BROKER=localhost
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USER=
MQTT_PASSWORD=
MQTT_CLIENT_ID=proyecto_iot_cliente
MQTT_TOPIC=sensores/#

```

## Instalación de dependencias

Instalar las dependencias del proyecto usando `pip`:

```bash
pip install -r requirements.txt
```

---

## Base de Datos

Este proyecto utiliza **PostgreSQL** como base de datos.  
Las credenciales se configuran en el archivo `.env` dentro de la carpeta `config`.

### Levantar PostgreSQL con Docker

```bash
docker run -d --name postgres_ejemplo \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=ejemplo \
  -p 5432:5432 \
  postgres:15
```
## MQTT (Mosquitto)

El proyecto utiliza **Mosquitto** como broker MQTT para recibir las lecturas de los sensores.  
El topic que se usa para los sensores es: `sensores/#`.

### Levantar Mosquitto con Docker

```bash
docker run -d --name mosquitto \
  -p 1883:1883 -p 9001:9001 \
  -v $(pwd)/mosquitto/config:/mosquitto/config \
  -v $(pwd)/mosquitto/data:/mosquitto/data \
  -v $(pwd)/mosquitto/log:/mosquitto/log \
  eclipse-mosquitto:2.0
```
