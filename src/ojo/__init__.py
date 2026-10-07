"""Ojo de Águila: motor analítico reutilizable sobre las APIs de StatsBomb.

Las capas siguen la propuesta (APIs → framework → lentes → salidas) y las
dependencias van en un solo sentido; una capa nunca importa a una posterior:

    ingesta → datos → framework → lentes → salidas

Nada en este paquete fija ids del América o de Jardine: todo sale de
config/params.yaml, para que el mismo código sirva para cualquier equipo.
"""
