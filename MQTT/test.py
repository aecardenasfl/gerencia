#!/usr/bin/python
# -*- coding: utf-8 -*-

from Sensores.MQTTHandler import MQTTHandler

def imprimir_mensaje(topic: str, payload: str):
    print(f"[PRUEBA] Mensaje recibido: topic={topic}, payload={payload}")

if __name__ == "__main__":
    handler = MQTTHandler(on_message_callback=imprimir_mensaje)
    handler.start()
    print("Escuchando mensajes MQTT... presiona Ctrl+C para salir")

    try:
        while True:
            pass  # Mantener el script corriendo
    except KeyboardInterrupt:
        print("Deteniendo MQTTHandler...")
        handler.stop()
