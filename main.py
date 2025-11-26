from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from Controlador.ProductoControlador import router as router_productos
from Controlador.PedidoControlador import router as router_pedidos
from Controlador.UsuarioControlador import router as router_usuarios
from Sensores.MQTTHandler import MQTTHandler

mqtt_handler: MQTTHandler | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_handler
    # startup: iniciar el handler
    mqtt_handler = MQTTHandler(on_message_callback=MQTTHandler.manejar_mensaje)  
    mqtt_handler.start()
    print("MQTTHandler iniciado y escuchando mensajes...")
    try:
        yield  # FastAPI sigue corriendo
    finally:
        # shutdown: detener el handler
        if mqtt_handler:
            mqtt_handler.stop()
            print("MQTTHandler detenido.")

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
