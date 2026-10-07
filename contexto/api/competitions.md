# Competitions v4.0.0 (StatsBomb)

- Endpoint: `GET https://data.statsbombservices.com/api/v4/competitions` (sin parámetros).
- Respuesta: arreglo JSON, un objeto por combinación competición-temporada con licencia.

| Campo | Tipo | Notas |
| --- | --- | --- |
| `competition_id`, `season_id` | int | Llaves para Matches y para las stats de temporada |
| `competition_name`, `season_name` | str | Buscar Liga MX y sus 8 torneos (Apertura 2021 – Clausura 2025) |
| `competition_gender` | str | |
| `competition_youth`, `competition_international` | bool | |
| `country_name` | str | |
| `match_updated`, `match_updated_360` | datetime | Última actualización de algún partido (eventos / 360) |
| `match_available`, `match_available_360` | datetime | Última vez que se publicó o actualizó un partido disponible |
