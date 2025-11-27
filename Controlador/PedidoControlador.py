# Controladores/PedidoControlador.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from Modelo.Pedido import Pedido, DetallePedido
from Servicios.PedidoServicio import PedidoServicio

# -------------------------------
# Schemas Pydantic
# -------------------------------

class SolicitudCambioEstado(BaseModel):
    estado: str = Field(..., description="Nuevo estado del pedido (pendiente, confirmado, enviado, cancelado)")

class DetallePedidoRespuesta(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    pedido_id: int
    
    model_config = {"from_attributes": True}

class PedidoRespuesta(BaseModel):
    id: int
    usuario_id: int
    estado: str
    total: float
    items: List[DetallePedidoRespuesta]  # Ajuste: usamos 'items' en vez de 'detalles'
    
    model_config = {"from_attributes": True}

class DetallePedidoCrear(BaseModel):
    producto_id: int
    cantidad: int = Field(..., gt=0, description="Cantidad a solicitar")

class PedidoCrear(BaseModel):
    usuario_id: int
    items: List[DetallePedidoCrear] = Field(..., min_length=1, description="Lista de productos del pedido")

# -------------------------------
# Router
# -------------------------------

router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"]
)

def obtener_servicio_pedido() -> PedidoServicio:
    return PedidoServicio()

# -------------------------------
# Endpoints
# -------------------------------

@router.post("/", response_model=PedidoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_pedido(
    pedido_data: PedidoCrear,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido)
):
    try:
        datos_dict = pedido_data.model_dump()
        pedido_creado = servicio.crear_pedido(datos_dict)
        return pedido_creado
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{pedido_id}", response_model=PedidoRespuesta)
def obtener_pedido(
    pedido_id: int,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido)
):
    pedido = servicio.obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pedido {pedido_id} no encontrado")
    return pedido

@router.get("/usuario/{usuario_id}", response_model=List[PedidoRespuesta])
def listar_pedidos_por_usuario(
    usuario_id: int,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido)
):
    try:
        pedidos = servicio.listar_pedidos_usuario(usuario_id)
        return pedidos
    except ValueError as e:
        detail = str(e)
        if "no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.patch("/{pedido_id}/estado", response_model=PedidoRespuesta)
def cambiar_estado_pedido(
    pedido_id: int,
    solicitud: SolicitudCambioEstado,
    servicio: PedidoServicio = Depends(obtener_servicio_pedido)
):
    try:
        pedido_actualizado = servicio.cambiar_estado(pedido_id, solicitud.estado)
        return pedido_actualizado
    except ValueError as e:
        detail = str(e)
        if "no existe" in detail:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
