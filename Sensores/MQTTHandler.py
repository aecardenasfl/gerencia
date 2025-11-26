#!/usr/bin/python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json
from typing import Callable
from Servicios.ProductoServicio import ProductoServicio
from config.config_loader import Config  # loader de .env

producto_servicio = ProductoServicio()

class MQTTHandler:
    """
    Maneja la conexión MQTT y la recepción de mensajes.
    """
    def __init__(self, on_message_callback: Callable[[str, str], None]):
        """
        :param on_message_callback: función que recibe (topic, payload)
        """
        self.broker = Config.MQTT_BROKER
        self.port = Config.MQTT_PORT
        self.client_id = Config.MQTT_CLIENT_ID
        self.topic = Config.MQTT_TOPIC

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Callback personalizado que definirá el usuario al crear el handler
        self.user_callback = on_message_callback

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Conectado a MQTT Broker {self.broker}:{self.port}")
            client.subscribe(self.topic)
            print(f"Suscrito al topic: {self.topic}")
        else:
            print(f"Error al conectar con código {rc}")

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        self.user_callback(msg.topic, payload)

    def start(self):
        """Inicia el loop de escucha MQTT."""
        self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def stop(self):
        """Detiene el loop y desconecta."""
        self.client.loop_stop()
        self.client.disconnect()

       
    def manejar_mensaje(topic: str, payload: str):
        """
        Callback que recibe el mensaje MQTT.
        """
        try:
            payload=payload.strip()
            data = json.loads(payload)
            lecturas = data.get("lecturas", [])
            if lecturas:
                producto_servicio.procesar_lecturas_sensor(lecturas)
        except Exception as e:
            print(f"[ERROR] al procesar mensaje MQTT: {e}")

