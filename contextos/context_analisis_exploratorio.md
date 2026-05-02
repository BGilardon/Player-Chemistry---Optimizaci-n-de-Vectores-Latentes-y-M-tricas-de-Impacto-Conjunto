# Context: AnalisisExp.ipynb — Análisis Exploratorio

**Notebook:** `AnalisisExp.ipynb`  
**Objetivo:** Entender la estructura del dataset de eventos antes de implementar JOI/JDI.

---

## Datos cargados

| Liga | Temporadas disponibles | Filas aprox. por temporada |
|------|------------------------|---------------------------|
| Premier League | 21/22, 22/23, 23/24, 24/25, 25/26 | ~570k–590k |
| Serie A | 21/22, 22/23, 23/24, 24/25, 25/26 | similar |

**Decisión tomada:** Trabajar con PL 21/22, 22/23, 23/24. Análisis principal en **PL 23/24**.  
Serie A descartada por ahora (marcada como "poco valor" en el notebook).

**Discrepancia detectada:** PL tiene columnas `Posesion_id` y `original_id` que Serie A **no tiene**. Las demás columnas son iguales entre temporadas de la misma liga.

---

## Estructura del dataset

Columnas clave agrupadas por uso:

- **Identificadores:** `matchId`, `playerId`, `jugador`, `TeamName`, `TeamRival`, `fecha`, `Competencia`, `Temporada`
- **Acción:** `event_name`, `outcome_type`, `minute`, `second`, `x`, `y`, `endX`, `endY`, `isTouch`, `isGoal`, `isShot`
- **Contexto:** `position`, `receiver_position`, `receiver_playerName`, `previous_event`, `next_event_posesion`, `time_since_previous_action`
- **Métricas pre-calculadas:** `xG`, `xG_corr`, `xGoT`, `xGoT_corr`, `xA`, `xT`
- **Estado del partido:** `goles_equipo`, `goles_rival`, `goles_totales`, `estado_partido`
- **Metainfo:** `qualifiers` (JSON string), `id_formation`, `id_formation_rival`

---

## Estadísticas PL 23/24

- **20 equipos, 573 jugadores, 380 partidos** (dataset completo).
- Promedio de pases por temporada PL: ~356k (caída en 24/25, temporada incompleta probablemente).

**Top eventos por frecuencia:**

| Evento | Count | % Exitoso |
|--------|-------|-----------|
| Pass | 387,581 | 81.0% |
| BallRecovery | 36,689 | 100.0% |
| BallTouch | 24,954 | 56.8% |
| Aerial | 20,303 | 50.0% |
| Foul | 16,811 | 50.0% |

**Tipos de acción relevantes para JOI (interacciones):**  
Pass, Cross, Dribble, TakeOn, Shot — alineados con el paper base. `receiver_playerName` solo tiene valor en `Pass` (confirma que el receptor solo se registra en pases).

---

## Posiciones

17 posiciones únicas + `Sub`. Las más frecuentes: `DC` (114 jugadores), `MC` (131), `Sub` (491 — suplentes sin posición definida al momento de su evento).

Posiciones disponibles: GK, DC, DL, DR, DML, DMR, DMC, ML, MR, MC, AML, AMR, AMC, FWL, FWR, FW, Sub.

---

## Qualifiers

Columna con metadata JSON de cada acción (ej: PassEndX/Y, Length, Angle, Zone, Chipped, etc.).

Se implementó `build_qualifiers_df()` para parsear el JSON y expandirlo en columnas. **Advertencia: operación muy costosa**, desactivada por defecto con `if 2+2==3`.

Qualifiers más presentes (menor % de NaN):

| Qualifier | % presente |
|-----------|------------|
| Zone | 90.2% |
| StandingSave | 74.2% |
| PassEndX / PassEndY | 68.4% |
| Length / Angle | 68.1% |

---

## Herramientas construidas

### `analisis_evento(df, event_name)`
Análisis profundo de un tipo de evento: stats numéricas (media/desvío), outcome breakdown, top jugadores/posiciones/eventos anterior y siguiente. Retorna un `pd.Series` reutilizable.

### `comparativa_efectiva(df, events, Nans)`
Compara múltiples eventos en paralelo. Parámetro `Nans` controla manejo de NaN (`"NADA"` / `"TODOS"` / `"FILA"` / int).

### `dashboard_jugador(df, jugador)` + `buscador_jugador(df)`
Dashboard HTML por jugador: partidos, minutos, goles, pases (%), tiros, xG/tiro, xG/90, xGoT/90, tarjetas. Widget interactivo con búsqueda en tiempo real.

### `dashboard_partido(df, match_id)` + `buscador_partido(df)`
Dashboard HTML por partido: resultado, eventos por equipo (pases, tiros, xG, % pases, 1er/2do tiempo). Widget interactivo para seleccionar por equipos y fecha.

---

## Hallazgos relevantes para JOI/JDI

- La **interacción** (dos acciones consecutivas de jugadores distintos) se construirá principalmente sobre `Pass`, dado que es el único evento con `receiver_playerName` disponible.
- `time_since_previous_action` y `previous_event` / `next_event_posesion` ya están pre-calculados → útiles para definir ventana de interacción.
- Los 6 partidos faltantes en Serie A 21/22 (matchIds identificados) podrían requerir limpieza antes de usar esa liga.
- La columna `Posesion` / `Posesion_id` en PL puede ser útil para definir secuencias de posesión en lugar de interacciones individuales.

---

## Estado actual

- [x] Datos cargados y estructura comprendida
- [x] Análisis de eventos, posiciones y qualifiers
- [x] Herramientas de exploración (dashboards jugador y partido)
- [ ] Implementación de JOI/JDI (siguiente paso)
- [ ] Construcción de feature vectors por jugador y par
- [ ] Modelo predictivo (CatBoost baseline)
