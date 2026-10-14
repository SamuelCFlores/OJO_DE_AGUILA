"""Pruebas del seguimiento estimado entre fotos 360 (animación del Voronoi)."""

from ojo.lentes import seguimiento

CFG = {"velocidad_max_yd_s": 10, "tolerancia_yd": 3}


def test_empareja_por_equipo_con_el_desplazamiento_minimo() -> None:
    a = [(10, 10, True), (20, 10, True), (50, 40, False)]
    b = [(21, 11, True), (11, 9, True), (52, 41, False)]  # mismo orden cambiado: se recupera por cercanía
    assert seguimiento.emparejar(a, b, dt=0.5, cfg=CFG) == [(0, 1), (1, 0), (2, 2)]


def test_no_empareja_saltos_imposibles_ni_entre_equipos() -> None:
    a = [(10, 10, True), (30, 30, False)]
    b = [(40, 10, True), (31, 30, True)]  # 30 yd en 0.5 s es imposible; el de (31, 30) es de otro equipo
    assert seguimiento.emparejar(a, b, dt=0.5, cfg=CFG) == []


def test_pistas_conservan_identidad_y_dan_numero_nuevo_al_que_entra() -> None:
    fotos = [[(10, 10, True), (20, 20, False)], [(11, 10, True), (21, 20, False), (60, 60, True)], [(12, 10, True)]]
    ids = seguimiento.pistas(fotos, [0.0, 0.5, 1.0], CFG)
    assert ids[0] == [0, 1] and ids[1] == [0, 1, 2] and ids[2] == [0]
