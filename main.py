from fastapi import FastAPI
from Controlador.ProductoControlador import router as router_productos
from Controlador.UsuarioControlador import router as usuario_router
from fastapi.responses import RedirectResponse
from Managers.ProductoManager import ProductoManager
from Managers.UsuarioManager import UsuarioManager
from Managers.PedidoManager import PedidoManager

app = FastAPI()
app.include_router(router_productos)
app.include_router(usuario_router)

@app.on_event("startup")
def on_startup():
    try:
        ProductoManager().ensure_table()
        UsuarioManager().ensure_table()
        PedidoManager().ensure_tables()
    except Exception as e:
        print("Advertencia al crear tablas en startup:", e)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")