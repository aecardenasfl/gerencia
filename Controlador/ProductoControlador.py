#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Controlador (Router) de FastAPI para operaciones sobre Producto.

Utiliza la clase Producto directamente para entrada y salida.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# Importar el modelo y el servicio (Asegúrate de que estas rutas sean correctas)
from Modelo.Producto import Producto
from Servicios.ProductoServicio import ProductoServicio

# --- Esquema Mínimo para la Solicitud de Ajuste de Stock ---
# Necesitamos esta clase porque solo queremos el campo 'delta' en el cuerpo
class SolicitudAjustarStock(BaseModel):
    delta: int = Field(..., description="Cambio en la cantidad de stock (positivo o negativo)")


# --- Instancia del Router y Dependencia del Servicio ---

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
)

# Dependencia para obtener la instancia del servicio
def obtener_servicio_producto() -> ProductoServicio:
    """Retorna una instancia del servicio de producto."""
    return ProductoServicio()


# --- Endpoints CRUD ---

@router.post(
    "/",
    response_model=Producto, # Usamos tu dataclass directamente como respuesta
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
)
def crear_producto(
    producto: Producto, # FastAPI mapea JSON de entrada a tu dataclass Producto
    servicio: ProductoServicio = Depends(obtener_servicio_producto),
):
    """
    Crea un nuevo producto en la base de datos. El ID será asignado automáticamente.
    """
    try:
        # Llama al servicio con el objeto Producto
        producto_creado = servicio.create_product(producto)
        return producto_creado
    except ValueError as e:
        # Manejo de errores de validación del servicio
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al crear producto: {e}")


@router.get(
    "/",
    response_model=List[Producto], # Usamos tu dataclass para la lista de respuesta
    summary="Listar todos los productos",
)
def listar_productos(
    servicio: ProductoServicio = Depends(obtener_servicio_producto),
):
    """
    Retorna la lista de todos los productos disponibles.
    """
    return servicio.list_products()


@router.get(
    "/{producto_id}",
    response_model=Producto,
    summary="Obtener un producto por ID",
)
def obtener_producto(
    producto_id: int,
    servicio: ProductoServicio = Depends(obtener_servicio_producto),
):
    """
    Retorna los detalles de un producto específico por su ID.
    """
    producto = servicio.get_product(producto_id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id={producto_id} no encontrado",
        )
    return producto


@router.put(
    "/{producto_id}",
    response_model=Producto,
    summary="Actualizar completamente un producto",
)
def actualizar_producto(
    producto_id: int,
    datos_producto: Producto, # Datos de entrada de tipo Producto
    servicio: ProductoServicio = Depends(obtener_servicio_producto),
):
    """
    Actualiza **todos** los campos de un producto existente.
    """
    try:
        # Aseguramos que el ID en el objeto de entrada coincida con el ID de la ruta
        datos_producto.id = producto_id
        producto_actualizado = servicio.update_product(producto_id, datos_producto)
        return producto_actualizado
    except ValueError as e:
        detail = str(e)
        if f"id={producto_id} no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto",
)
def eliminar_producto(
    producto_id: int,
    servicio: ProductoServicio = Depends(obtener_servicio_producto),
):
    """
    Elimina un producto por su ID.
    """
    servicio.delete_product(producto_id)
    return


# --- Endpoint de Ajuste de Stock ---

@router.post(
    "/{producto_id}/ajustar_stock",
    response_model=int,
    summary="Ajustar el stock de un producto",
)
def ajustar_stock_producto(
    producto_id: int,
    solicitud: SolicitudAjustarStock, # Usamos la clase mínima con solo 'delta'
    servicio: ProductoServicio = Depends(obtener_servicio_producto),
):
    """
    Ajusta la cantidad de stock (incrementa con valor positivo, decrementa con negativo).
    Retorna el nuevo valor de stock.
    """
    try:
        nueva_cantidad = servicio.adjust_stock(producto_id, solicitud.delta)
        return nueva_cantidad
    except ValueError as e:
        detail = str(e)
        if "no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        # Errores de validación como stock insuficiente
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)