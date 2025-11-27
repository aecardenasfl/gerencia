from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from DAOs.DB import create_all_tables
from Controlador.ProductoControlador import router as router_productos
from Controlador.PedidoControlador import router as router_pedidos
from Controlador.UsuarioControlador import router as router_usuarios
from Controlador.NotificacionControlador import router as router_notificaciones
from Sensores.MQTTHandler import MQTTHandler, manejar_mensaje

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_handler
    # startup: iniciar el handler
    mqtt_handler = MQTTHandler(on_message_callback=manejar_mensaje)  # <- usar la función global
    mqtt_handler.start()
    print("MQTTHandler iniciado y escuchando mensajes...")
    try:
        yield  # FastAPI sigue corriendo
    finally:
        # shutdown: detener el handler
        if mqtt_handler:
            mqtt_handler.stop()
            print("MQTTHandler detenido.")

# Crear tablas al iniciar la aplicación
create_all_tables()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_productos)
app.include_router(router_pedidos)
app.include_router(router_usuarios)
app.include_router(router_notificaciones)
