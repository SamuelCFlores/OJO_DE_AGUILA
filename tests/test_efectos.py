"""Prueba de humo de ojo.lentes.efectos: la diferencia en diferencias con datos sintéticos (auditoría del 19 oct, N8)."""

import pandas as pd

from ojo.lentes import efectos, minuto


def _evento(match_id, indice, periodo, minuto_, tipo, equipo, **extra) -> dict:
    base = {"match_id": match_id, "indice": indice, "periodo": periodo, "minuto": minuto_, "tipo": tipo, "equipo_id": equipo,
            "tiro_resultado": None, "tarjeta": None, "formacion": None, "sustitucion_resultado": None}
    return base | extra


def _eventos() -> pd.DataFrame:
    """Partido 1: el equipo 1 anota al 20' con 0-0. Partidos 2 y 3: sin quiebres (sirven de control)."""
    filas = []
    for m in (1, 2, 3):
        filas += [_evento(m, 1, 1, 0, "Starting XI", 1, formacion=4231), _evento(m, 2, 1, 0, "Starting XI", 2, formacion=442),
                  _evento(m, 4, 1, 45, "Pass", 1), _evento(m, 5, 2, 45, "Pass", 2), _evento(m, 6, 2, 90, "Pass", 1)]
    filas.append(_evento(1, 3, 1, 20, "Shot", 1, tiro_resultado="Goal"))
    return pd.DataFrame(filas)


def _medir_falso(panel, aristas, ventanas):
    """Cada métrica vale 1 antes; después, 3 en el quiebre y 1.5 en los controles (cambio 2 frente a 0.5)."""
    filas = []
    for v in ventanas.itertuples():
        id_, fase = v.ventana_id.rsplit("|", 1)
        valor = 1.0 if fase == "antes" else (1.5 if "|c" in id_ else 3.0)
        for lado in (minuto.PROPIO, minuto.RIVAL):
            filas.append({"ventana_id": v.ventana_id, "lado": lado, **{m: valor for m in efectos.METRICAS}})
    return pd.DataFrame(filas)


def test_efecto_es_cambio_del_quiebre_menos_cambio_medio_de_controles(monkeypatch) -> None:
    monkeypatch.setattr(minuto, "medir", _medir_falso)
    partidos = pd.DataFrame({"match_id": [1, 2, 3], "grupo": "Jardine", "torneo_corto": "AP23"})
    e = efectos.efectos(_eventos(), pd.DataFrame(), pd.DataFrame(), partidos, equipo_id=1)
    assert set(e["tipo"]) == {"gol_favor"}
    assert len(e) == 2 * len(efectos.METRICAS)  # un quiebre × dos lados × cada métrica
    assert (e["n_controles"] >= 1).all()
    assert e["cambio"].eq(2.0).all() and e["cambio_control"].eq(0.5).all() and e["efecto"].eq(1.5).all()
    assert e["estado_antes"].eq("empata").all() and e["grupo"].eq("Jardine").all()
