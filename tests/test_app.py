"""Pruebas de la página de la app (portada + explorar) y del marcador de ojo, con datos sintéticos."""

from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ojo.lentes.voronoi import Jugador, analizar_frame
from ojo.salidas import app, marcador
from ojo.salidas.caso import Jugada

VISIBLE = [30, 10, 90, 10, 90, 70, 30, 70, 30, 10]
JUGADORES = [Jugador(50, 40, True, actor=True), Jugador(60, 25, True), Jugador(60, 55, True),
             Jugador(70, 40, False), Jugador(75, 20, False), Jugador(75, 60, False)]


def test_marcador_tiene_iris_dentro_de_la_almendra() -> None:
    f = marcador.formas()
    assert all(not g.is_empty for g in f.values())
    assert f["almendra"].contains(f["iris"].representative_point())
    assert f["iris"].area < f["almendra"].area < f["contorno"].area


def test_nombre_largo_del_rival_cabe_en_la_placa() -> None:
    assert app.tamano_nombre("Toluca") == app.PLACA_MAX_PX
    assert app.tamano_nombre("Atlético San Luis") < app.tamano_nombre("Guadalajara") < app.PLACA_MAX_PX


def test_pagina_llena_todos_los_espacios() -> None:
    resultado = analizar_frame(JUGADORES, VISIBLE)
    jugada = Jugada("12:05", "Uno pasa a Dos", True, resultado,
                    SimpleNamespace(tipo="Pass", x=50.0, y=40.0, fin_x=60.0, fin_y=25.0))
    barra = app.Barra("Rival", 3, [("Otro", 2)], [("Uno", True)], [("AP23", True, False), ("CL26", False, True)],
                      [("01/08", "Fase regular", "1-0", True)], [("Fase", [("Salida de balón", True)])], "Local",
                      "1 partido", [("Control", "50% · 50%")])
    caso = app.Caso("Título", "Antetítulo", "Equipo", "Rival", "Ejemplo", ["AP23"], "Qué muestra", "Lectura", "Método",
                    [("Marcador", "1-0")], [("12'", "Gol", True)], plt.figure(), pd.DataFrame({"a": ["1"]}, index=["x"]),
                    [("12:05", "Uno pasa a Dos", True)], [jugada], jugada, "Uno", plt.figure(), ["resumen"], ["cierre"],
                    barra)
    pagina = app.pagina(caso, "../../branding")
    assert "@@" not in pagina
    assert pagina.count("<svg") >= 5 and 'data-vista="explorar"' in pagina and "Torneo de prueba" in pagina


def test_paleta_azulcrema_solo_dentro_del_bloque() -> None:
    from ojo.salidas import estilo
    assert estilo.color("dorado") == "#E8B100"
    with estilo.paleta("azulcrema"):
        assert (estilo.color("azul"), estilo.color("dorado"), estilo.color("rojo")) == ("#0F1D41", "#F0EB9A", "#F6303E")
        assert estilo.color("blanco") == "#FFFFFF"  # lo que la paleta no cambia sale de --oda-*
    assert estilo.color("azul") == "#0B2545" and estilo.color("rojo") == "#E8B100"


def test_maqueta_3_llena_todos_los_espacios() -> None:
    from ojo.lentes.simulacion import Simulacion
    from ojo.salidas import narrativa
    resultado = analizar_frame(JUGADORES, VISIBLE)
    jugada = Jugada("80:00", "Uno pasa a Dos", True, resultado,
                    SimpleNamespace(tipo="Pass", x=50.0, y=40.0, fin_x=60.0, fin_y=25.0))
    barra = app.Barra("Rival", 3, [], [("Uno", True)], [("AP23", True, False)], [], [], "Local", "1 partido", [])
    principio = narrativa.Principio("Título", "Frase", "Significa", "Uso", "+1", "+0", "+1", "IC", "4 de 5", "Candidato")
    sim = Simulacion(.5, .3, .2, 1.1, .6, [("1-0", .3)])
    datos = {"equipo": "Equipo", "rival": "Rival", "componentes": [], "minutos": [], "fotos": [], "quiebres": [],
             "etiquetasX": [], "jugada": None, "inicio": 0}
    n = narrativa.Narrativa("Título", "Equipo", "Rival", "Ante", ["AP23"], barra, [("Índice", "57", "rivales 48")],
                            plt.figure(), [principio], principio, "Ejemplo", jugada, "Qué muestra", [("Minuto", "80:00")],
                            [("80'", "Roja", True)], datos, [narrativa.Montecarlo("Todo", "Texto", sim)], "Lectura",
                            "Método", [("Riesgo", "Qué mostrará", "predictivo")])
    pagina = narrativa.pagina(n, "../../branding")
    assert "@@" not in pagina and 'id="datos-repro"' in pagina and "En construcción" in pagina
