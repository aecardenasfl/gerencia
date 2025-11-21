from fastapi import FastAPI
from Controlador.ProductoControlador import router as router_productos

app = FastAPI()
app.include_router(router_productos)
