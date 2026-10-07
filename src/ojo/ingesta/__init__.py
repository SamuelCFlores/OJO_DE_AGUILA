"""Capa 1 (APIs): cliente HTTP con caché en disco y un módulo por API de StatsBomb.

Único lugar del proyecto que habla con la red. Guarda las respuestas tal como
llegan (JSON gzip) en data/raw/ y no transforma nada.
"""
