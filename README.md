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
## 🛰️ MQTT (Mosquitto)
El proyecto utiliza **Mosquitto** como broker MQTT para recibir las lecturas enviadas por los sensores. El topic utilizado por los sensores es `sensores/#`. Este proyecto incluye su propia configuración de Mosquitto dentro de la carpeta `MQTT/`, que debe tener la siguiente estructura:

```
MQTT/
├── docker-compose.yml
└── mosquitto/
    ├── config/
    │   └── mosquitto.conf
    ├── data/
    └── log/
```
El contenido mínimo recomendado de `mosquitto.conf` es:
```
listener 1883
allow_anonymous true

persistence true
persistence_location /mosquitto/data/

log_dest file /mosquitto/log/mosquitto.log
```

Para iniciar el broker, desde la carpeta `MQTT/` ejecutar:

```bash
docker compose up -d
```

Esto levantará el broker exponiendo **1883** para MQTT TCP (usado por Python, microcontroladores, etc.). Para detener el broker, ejecutar:

docker compose down

Para probar que Mosquitto funciona, puedes suscribirte a un topic con:
```
docker exec -it mosquitto mosquitto_sub -h localhost -p 1883 -t sensores/test
```
Y publicar un mensaje con:
```
docker exec -it mosquitto mosquitto_pub -h localhost -p 1883 -t sensores/test -m "hola"
``` 


### Formato JSON que debe recibir el broker: 

```JSON
{
  "timestamp": "2025-11-26T14:05:00Z",
  "lecturas": [
    {"sensor_id": "sensor_01", "producto_id": 1, "cantidad": 12},
    {"sensor_id": "sensor_02", "producto_id": 2, "cantidad": 8},
    {"sensor_id": "sensor_03", "producto_id": 3, "cantidad": 5},
    {"sensor_id": "sensor_04", "producto_id": 4, "cantidad": 20}
  ]
}
```
Para ejecutar manualmente una inyección al MQTT, correr desde la ruta **\MQTT** el siguiente comando (usando el **.venv** del proyecto):

```Powershell
py -c "import json, paho.mqtt.publish as publish; f = open('test.json','r'); payload = f.read(); f.close(); publish.single('sensores/test', payload, hostname='localhost', port=1883)"
``` 
