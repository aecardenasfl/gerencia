#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Controlador (Router) de FastAPI para operaciones sobre Producto.

Incluye endpoints CRUD y ajuste de stock, usando Pydantic V2 y sesiones inyectadas correctamente.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from Modelo.Producto import Producto
from DAOs.DB import get_session
from Servicios.ProductoServicio import ProductoServicio

# --- Esquemas de Datos ---

class ProductoCrearActualizar(BaseModel):
    nombre: str = Field(..., description="Nombre del producto")
    descripcion: str | None = Field(default=None, description="Descripción detallada")
    precio: float = Field(..., gt=0, description="Precio unitario")
    cantidad: int = Field(default=0, ge=0, description="Cantidad de stock inicial/actualizada")
    codigo: str | None = Field(default=None, description="Código único del producto")
    activo: bool = Field(default=True, description="Indica si el producto está activo")

class ProductoRespuesta(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    precio: float
    cantidad: int
    codigo: str | None
    activo: bool

    model_config = {
        "from_attributes": True
    }

class SolicitudAjustarStock(BaseModel):
    delta: int = Field(..., description="Cambio en la cantidad de stock (positivo o negativo)")

# --- Router ---
router = APIRouter(
    prefix="/productos",
    tags=["productos"]
)

# --- Dependencia del Servicio ---
def get_producto_servicio():
    """Retorna una instancia de ProductoServicio usando la sesión inyectada correctamente."""
    yield ProductoServicio()

# --- Endpoints CRUD ---

@router.post("/", response_model=ProductoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_producto(
    producto_data: ProductoCrearActualizar,
    servicio: ProductoServicio = Depends(get_producto_servicio)
):
    datos = producto_data.model_dump()
    try:
        return servicio.crear_producto(datos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {e}")

@router.get("/", response_model=List[ProductoRespuesta])
def listar_productos(servicio: ProductoServicio = Depends(get_producto_servicio)):
    return servicio.listar_productos()

@router.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener_producto(
    producto_id: int,
    servicio: ProductoServicio = Depends(get_producto_servicio)
):
    producto = servicio.obtener_producto(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=f"Producto con id={producto_id} no encontrado")
    return producto

@router.put("/{producto_id}", response_model=ProductoRespuesta)
def actualizar_producto(
    producto_id: int,
    datos_producto: ProductoCrearActualizar,
    servicio: ProductoServicio = Depends(get_producto_servicio)
):
    datos_dict = datos_producto.model_dump()
    datos_dict["id"] = producto_id
    try:
        return servicio.actualizar_producto(producto_id, datos_dict)
    except ValueError as e:
        detail = str(e)
        if f"id={producto_id} no existe" in detail:
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    servicio: ProductoServicio = Depends(get_producto_servicio)
):
    servicio.eliminar_producto(producto_id)
    return

# --- Endpoint de ajuste de stock ---
@router.post("/{producto_id}/ajustar_stock", response_model=int)
def ajustar_stock_producto(
    producto_id: int,
    solicitud: SolicitudAjustarStock,
    servicio: ProductoServicio = Depends(get_producto_servicio)
):
    try:
        return servicio.ajustar_stock(producto_id, solicitud.delta)
    except ValueError as e:
        detail = str(e)
        if "no existe" in detail:
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=detail)
