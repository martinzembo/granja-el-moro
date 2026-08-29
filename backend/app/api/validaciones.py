"""Guardas de integridad compartidas entre routers (crianzas, lecturas,
insumos, retiros). Son chequeos simples ligados a HTTP (levantan
HTTPException directo) — no son "lógica de negocio no trivial" en el
sentido de CLAUDE.md, por eso no viven en app/services/, pero se repiten en
varios routers y conviene no duplicarlos.
"""

from datetime import date

from fastapi import HTTPException

from app.models.crianza import Crianza, EstadoCrianza


def requiere_crianza_en_curso(crianza: Crianza) -> None:
    if crianza.estado != EstadoCrianza.en_curso:
        raise HTTPException(
            status_code=400, detail="La crianza ya está cerrada, no admite más cargas"
        )


def requiere_fecha_no_futura(fecha: date) -> None:
    if fecha > date.today():
        raise HTTPException(status_code=400, detail="La fecha no puede ser futura")


def requiere_fecha_no_anterior(fecha: date, minima: date, motivo: str) -> None:
    if fecha < minima:
        raise HTTPException(
            status_code=400,
            detail=f"La fecha ({fecha}) no puede ser anterior a {motivo} ({minima})",
        )
