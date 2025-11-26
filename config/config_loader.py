#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------------------------------
# Localiza el archivo .env que está dentro de /config
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if not ENV_PATH.exists():
    raise RuntimeError(f"No se encontró archivo .env en: {ENV_PATH}")

# -------------------------------------------------------
# Cargar variables del .env usando python-dotenv
# -------------------------------------------------------
load_dotenv(dotenv_path=ENV_PATH)

# -------------------------------------------------------
# Clase unificada de configuración
# -------------------------------------------------------
class Config:
    # ----------- PostgreSQL -----------
    PGHOST = os.getenv("PGHOST")
    PGPORT = os.getenv("PGPORT")
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")
    PGDATABASE = os.getenv("PGDATABASE")
    POSTGRES_DSN = os.getenv("POSTGRES_DSN")
    PGSCHEMA = os.getenv("PGSCHEMA")

    # ----------- MQTT -----------------
    MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    MQTT_HOST = os.getenv("MQTT_HOST")
    MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "proyecto_cliente_mqtt")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USER = os.getenv("MQTT_USER")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
    MQTT_TOPIC = os.getenv("MQTT_TOPIC", "sensores/#")
