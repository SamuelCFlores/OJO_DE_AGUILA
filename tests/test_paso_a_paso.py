"""Prueba de humo del Voronoi paso a paso con un frame sintético."""

from ojo.lentes.voronoi import Jugador
from ojo.salidas import paso_a_paso

VISIBLE = [30, 10, 90, 10, 90, 70, 30, 70, 30, 10]
JUGADORES = [Jugador(50, 40, True, actor=True), Jugador(60, 25, True), Jugador(60, 55, True),
             Jugador(70, 40, False), Jugador(75, 20, False), Jugador(75, 60, False),
             Jugador(30.5, 40, False)]  # pegado al borde: se excluye


def test_seis_pasos_y_html_autocontenido() -> None:
    jugada = paso_a_paso.Jugada("Pase", 12, 5, "América", 50, 40, 70, 30)
    pasos = paso_a_paso.pasos(jugada, JUGADORES, VISIBLE)
    assert [p.titulo[0] for p in pasos] == list("123456")
    assert "Cuentan 6" in pasos[2].texto
    pagina = paso_a_paso.html(pasos, "Prueba", "Frame sintético")
    assert pagina.count("<svg") == 6 and "<title>Prueba</title>" in pagina
