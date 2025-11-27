#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Maneja la conexión y el procesamiento de mensajes MQTT de sensores.
Utiliza una clase Handler y la inicialización de la base de datos
para inyectar el ProductoServicio de manera global.
"""
import paho.mqtt.client as mqtt
import json
from typing import Callable, Iterator
from Servicios.ProductoServicio import ProductoServicio
from config.config_loader import Config # loader de .env
from DAOs.DB import get_session

#db = get_session()  
producto_servicio = ProductoServicio()

# El callback definido globalmente para ser usado por el Handler
def manejar_mensaje(topic: str, payload: str):
    """
    Callback que recibe el mensaje MQTT y lo procesa.
    Esta función usa el 'producto_servicio' inicializado globalmente.
    """
    try:
        payload = payload.strip()
        data = json.loads(payload)
        
        lecturas = data.get("lecturas", [])
        
        if lecturas:
            print(f"[MQTT] Recibidas {len(lecturas)} lecturas en el tópico {topic}")
            producto_servicio.procesar_lecturas_sensor(lecturas)
            
    except json.JSONDecodeError:
        print(f"[ERROR] JSON inválido en el tópico {topic}: {payload[:50]}...")
    except Exception as e:
        print(f"[ERROR] al procesar mensaje MQTT: {e}")


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
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            print("MQTT Handler iniciado. Esperando mensajes...")
        except Exception as e:
            print(f"[ERROR] No se pudo conectar/iniciar MQTT: {e}")

    def stop(self):
        """Detiene el loop y desconecta."""
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT Handler detenido.")