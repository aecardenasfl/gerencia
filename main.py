from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Controlador.ProductoControlador import router as router_productos
from Controlador.PedidoControlador import router as router_pedidos
from Controlador.UsuarioControlador import router as router_usuarios
app = FastAPI()
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