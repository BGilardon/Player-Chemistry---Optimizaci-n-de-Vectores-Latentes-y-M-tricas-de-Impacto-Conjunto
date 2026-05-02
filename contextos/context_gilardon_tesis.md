# Context: Plan de Tesis — Gilardon Bautista

**Título completo:** Player Chemistry - Optimización de Vectores Latentes y Métricas de Impacto Conjunto  
**Tipo:** Plan de tesis de Licenciatura en Ciencia de Datos (UBA)  
**Autor:** Bautista Gilardon (L.U. 742/21) — bautistagilardon@gmail.com  
**Director:** Manuel Durán (mduran@realracingclub.es) — Ingeniero de datos, Racing de Santander  
**Co-Director:** Guillermo Durán (guillermo.duran@de.fcen.uba.ar) — UBA  
**Duración:** 16 semanas, 17/03/2025 → 30/06/2025, ~20 hs/semana

---

## Problema central

Las métricas existentes evalúan rendimiento **individual** ignorando que el fútbol es colaborativo. La "química" entre jugadores puede determinar el éxito o fracaso de un equipo, y es especialmente relevante en reclutamiento.

**Paper base:** Bransen & Van Haaren (2020), "Player Chemistry: Striving for a Perfectly Balanced Soccer Team" — introduce métricas JOI y JDI y representa a cada jugador como vector de características.

---

## Dos contribuciones de la tesis

### Línea 1 (principal): Optimización de vectores de características
- **Inversión del problema**: dado un equipo y una posición a cubrir, ¿qué vector de características maximiza la química global del equipo?
- Transforma el reclutamiento de reactivo a proactivo: primero se diseña el perfil ideal, luego se buscan jugadores que lo aproximen.
- Validación: matching contra FIFA / Transfermarkt para identificar jugadores reales más cercanos al perfil óptimo.

### Línea 2 (secundaria): Métrica unificada ataque-defensa
- Las métricas JOI y JDI del paper base evalúan ataque y defensa de forma independiente.
- Objetivo: diseñar una métrica que integre ambas dimensiones (rendimiento colaborativo ofensivo-defensivo conjunto).

---

## Metodología

### Datos
- **Eventos:** Datos públicos de eventos futbolísticos de múltiples competiciones, representación **SPADL** (estandarización de acciones).
- **Complementarios:** Datos de Racing de Santander cuando estén disponibles (validación de casos de uso).

### Etapas metodológicas
1. **Replicación del baseline:** Implementar JOI/JDI según paper original. Modelo predictivo con **CatBoost** como baseline. Validar reproducibilidad de resultados.
2. **Optimización de vectores:** Formulación matemática del problema de optimización. Enfoques a explorar:
   - Optimización por gradiente
   - Algoritmos genéticos
   - Optimización Bayesiana
   - Restricciones: posición del jugador, compatibilidad con formación táctica, jugadores "columna vertebral".
3. **Extensión de métricas:** Comparar diferentes arquitecturas (redes neuronales, gradient boosting mejorado). Validación cruzada en múltiples competiciones.

### Métricas de éxito
- RMSE y R² en predicción de química
- Calidad de perfiles sintetizados (similitud con jugadores reales exitosos)
- Utilidad práctica evaluada con casos de uso documentados + validación con expertos del dominio

---

## Cronograma por fases

| Fase | Semanas | Actividades |
|------|---------|-------------|
| 1 - Fundamentación y replicación | 1-4 | Revisión bibliográfica (Player Chemistry, VAEP, optimización, sports analytics). Setup entorno (socceraction, CatBoost). Replicar JOI/JDI. |
| 2 - Desarrollo | 5-11 | Paralelo: optimización de vectores + diseño de métrica unificada. |
| 3 - Validación y casos de uso | 12-13 | Aplicación a escenarios reales de Racing. Generación de reportes. Validación cualitativa con directores. |
| 4 - Escritura y defensa | 14-16 | Redacción completa. Preparación presentación oral. |

---

## Factibilidad

- Acceso directo a expertise de dominio a través de Manuel Durán (Racing de Santander).
- Código del paper base disponible en GitHub: https://github.com/SciSports-Labs/player-chemistry
- Datos de eventos disponibles en múltiples plataformas (sin dependencia crítica de una sola fuente).
- Alcance modular: si la línea 2 se complica, se puede priorizar la optimización de vectores (línea 1) sin comprometer la tesis.

---

## Fuera del alcance

- Métricas en tiempo real o basadas en tracking data.
- El enfoque se centra exclusivamente en **datos de eventos (eventing)** ampliamente disponibles.

---

## Referencias bibliográficas del plan

- [1] Beal & Ramchurn (2019) — StatsBomb Innovation in Football Conference
- [2] **Bransen & Van Haaren (2020)** — Player Chemistry (paper base), arXiv:2003.01712
- [3] Decroos, Bransen, Van Haaren, Davis (2019) — VAEP framework (SIGKDD)
- [4] The Athletic (2021) — Brentford FC y analytics
