"""Acceso a datos: convierte el JSON crudo en tablas parquet y las carga.

Único punto de lectura de data/ para el resto del paquete, los scripts y los
notebooks; nadie más abre archivos de data/raw/ directamente.
"""
