# Context: Player Chemistry — Bransen & Van Haaren (2020)

**Título:** Player Chemistry: Striving for a Perfectly Balanced Soccer Team  
**Autores:** Lotte Bransen, Jan Van Haaren — SciSports (NL) / KU Leuven (BE)  
**Publicado:** MIT Sloan Sports Analytics Conference 2020  
**arXiv:** 2003.01712  
**Código:** https://github.com/SciSports-Labs/player-chemistry

---

## Resumen ejecutivo

El paper cuantifica la "química" entre pares de jugadores de fútbol. Opera en dos settings: (1) **observacional** — medir química entre jugadores que ya jugaron juntos; (2) **predictivo** — estimar química entre jugadores que nunca jugaron juntos. El supuesto central es que dos jugadores con alta química mutua rinden mejor que dos con baja química, *ceteris paribus*.

**Cuatro contribuciones:**
1. Métricas JOI y JDI para medir química ofensiva y defensiva de un par de jugadores.
2. Dos modelos ML (CatBoost) para predecir JOI/JDI de pares que nunca jugaron juntos.
3. **Team Builder**: ensamble automático de equipo de máxima química (programación entera mixta).
4. Tres observaciones analíticas + tres casos de uso prácticos.

---

## Dataset

**Fuente:** Wyscout — datos de eventos de partidos (on-the-ball actions).  
**Cobertura:** 106 competencias domésticas e internacionales, desde temporada 2015/2016.

| Propiedad | Cantidad |
|-----------|----------|
| Competencias | 106 |
| Temporadas | 361 |
| Partidos | 106,496 |
| Equipos | 2,154 |
| Jugadores | 38,447 |
| Combinaciones jugador-temporada | 97,491 |
| Nacionalidades | 190 |
| Idiomas maternos | 68 |

**Representación:** SPADL (socceraction Python package). Cada acción tiene: match_id, team_id, player_id, tiempo, ubicación inicio/fin, resultado, parte del cuerpo.

**Enriquecimiento por jugador (SciSports):**
- SciSkill y Potential (habilidad actual y potencial)
- Player Roles (22 roles, e.g., Mobile Striker, Deep-Lying Playmaker, Ball-Winning Defender)
- Physical Performance Indicators: ground duel strength, air duel strength, speed, work rate (escala 1-5)

**Enriquecimiento por par de jugadores:**
- Misma nacionalidad, mismo idioma materno, misma región/subregión
- Número de partidos jugados juntos antes de cada temporada

---

## Métricas de química

### 3.1 JOI — Joint Offensive Impact

Mide el impacto conjunto de dos jugadores en **incrementar** la probabilidad de gol.

**Base:** Framework VAEP (Valuing Actions in Expected goals), que valora acciones on-the-ball según su impacto en probabilidad de scoring/conceding.

**Interacción:** Dos acciones consecutivas donde cada jugador realiza una. Tipos válidos: pase, centro, dribble, take-on, remate.

**Fórmula:**
```
JOI_m(p,q) = Σ_k VAEP(I_k^m(p,q)) + Σ_l VAEP(I_l^m(q,p))
```
donde `I_j^m(p,q) = (a_i^p, a_{i+1}^q)` es la j-ésima interacción entre p y q en partido m.

**Normalización a 90 minutos:**
```
JOI90(p,q) = Σ_m JOI_m(p,q) * 90 / Σ_m MINS_m(p,q)
```

---

### 3.2 JDI — Joint Defensive Impact

Mide el impacto conjunto de dos jugadores en **decrementar** el impacto ofensivo de sus oponentes.

**Lógica:** Los eventos defensivos exitosos (smart runs, posicionamiento) no aparecen en datos de eventos. Proxy: si un oponente rinde *por debajo* de su expectativa ofensiva, el par defensivo responsable recibe crédito.

**Impacto ofensivo real:**
```
OI_m(p) = Σ_k VAEP(a_k^p)   [pases, centros, dribbles, take-ons, remates]
```

**Impacto ofensivo esperado:** Promedio histórico del jugador en la misma temporada/competición (partidos anteriores). Para jugadores con <700 minutos se usa un **prior Bayesiano** por posición, con peso proporcional a la fracción de 700 minutos jugados.

**Responsibility share** de par (p,q) para defender oponente o:
```
RESP_m(p,q,o) = (RESP_m(p,o) + RESP_m(q,o)) / 2
```
La responsabilidad individual se computa por distancia euclidiana en una **grilla 5x5** de posiciones (inversamente proporcional a la distancia). Posiciones: de Left Back a Right Wing Forward (ver Tabla 2 del paper).

**Fórmula JDI:**
```
JDI_m(p,q) = Σ_o [(E[OI_m(o)] - OI_m(o)) * RESP_m(p,q,o) * MINS_m(p,q,o)/90]
```

**Normalización:**
```
JDI90(p,q) = Σ_m JDI_m(p,q) * 90 / Σ_m MINS_m(p,q)
```

---

## Predicción de química (Sección 4)

### Feature vector por jugador
- Edad, línea de posición (GK/DEF/MID/FWD), altura, peso
- Nacionalidad, región, subregión, idioma materno
- 4 Physical Performance Indicators
- 22 Player Role scores

### Feature vector por par
- Todas las features individuales de ambos jugadores
- Indicadores binarios: misma nación, mismo idioma, misma región, misma subregión
- Número de partidos jugados juntos antes de la temporada

### Modelo
- **Algoritmo:** CatBoost (gradient boosting con manejo nativo de categóricas)
- **Split temporal:**
  - Train: 2015/16 y 2016/17 → 355,671 pares
  - Val: 2017/18 → 185,927 pares
  - Test: 2018/19 + 2019/20 (hasta 10/12/2019) → 234,408 pares
- Mínimo 700 minutos juntos para incluir un par en el dataset
- **Hiperparámetros:** JOI model = 500 árboles, depth 7 | JDI model = 1000 árboles, depth 5
- **Optimización:** RMSE en validation set

### Resultados

| Métrica | RMSE baseline | RMSE modelo |
|---------|---------------|-------------|
| JOI90 | 0.05448 | **0.04464** |
| JDI90 | 0.89075 | **0.88906** |

Baseline = predecir el promedio del training set.

### Análisis de importancia de features
- **JOI:** Player Roles más importantes: Mobile Striker, Deep-Lying Playmaker, Ball-Playing Defender.
- **JDI:** Holding Midfielder, Ball-Winning Defender.
- **Partidos previos juntos:** alto impacto inicial; se estabiliza después de 50 partidos (~1 temporada).
- **Features culturales** (nacionalidad, idioma): baja importancia predictiva en ambos modelos. Lo que importa es que los jugadores se comuniquen bien con los pies y tengan estilos de juego complementarios.

---

## Team Builder (Sección 5)

Ensambla automáticamente el equipo de máxima química dado un conjunto de jugadores.

**Formulación MIP (PuLP):**
```
max  Σ_p Σ_q (α·E[JOI90(p,q)] + (1-α)·E[JDI90(p,q)]) · x_p · x_q

s.t. Σ_p x_p = 11
     Σ_p GKP_p · x_p = 1
     3 ≤ Σ_p DEF_p · x_p ≤ 5
     3 ≤ Σ_p MID_p · x_p ≤ 5
     1 ≤ Σ_p FWD_p · x_p ≤ 3
```

- `x_p ∈ {0,1}`: si el jugador p es seleccionado.
- `α ∈ [0,1]`: parámetro de trade-off ofensivo-defensivo (configurable por el usuario).

---

## Observaciones clave (Sección 6)

### Top pares por JOI90 (≥900 minutos juntos)

| # | Par | Equipo | Temporada | JOI90 |
|---|-----|--------|-----------|-------|
| 1 | Salah - Firmino | Liverpool | CL 2017/18 | 0.7077 |
| 2 | Suárez - Messi | Barcelona | La Liga 2015/16 | 0.6497 |
| 3 | Nagasato - S. Kerr | Chicago Red Stars | NWSL 2019 | 0.6096 |

### Liverpool 2018/19 (Champions League winners)
- **Ofensiva:** Alta química entre los 3 atacantes (Salah, Mané, Firmino) y entre los full backs (Robertson, Alexander-Arnold) con los atacantes.
- **Defensiva:** Alta química en mediocampo y en la dupla central de defensores. Links débiles entre defensores centrales y los full backs.

### Özil en Arsenal (2015/16 → 2018/19)
- JOI90 promedio de Arsenal cayó fuertemente desde la salida de Alexis Sánchez en 2018.
- Özil aparece en 6 de los top-10 pares ofensivos de Arsenal (incluyendo los 4 primeros).
- La dupla Özil-Sánchez aparece 3 veces en el top 10.

---

## Casos de uso (Sección 7)

### 7.1 ¿Qué central debe fichar Manchester City?
Candidatos: Koulibaly, Škrinar, Alderweireld.
- **Defensivo:** Koulibaly es el mejor fit (excepto con Otamendi).
- **Ofensivo (línea defensiva):** Koulibaly también lidera.
- **Ofensivo (con creativos: De Bruyne, Mahrez, Agüero, etc.):** Alderweireld gana, en parte por 41 partidos juntos con De Bruyne en la selección belga.
- **Conclusión:** Koulibaly = opción defensiva obvia; Alderweireld = mejor fit ofensivo global.

### 7.2 ¿Qué extremo derecho debe jugar Real Madrid?
Candidatos: Bale, Rodrygo, Vinícius Jr.
- Al inicio de 2019/20: Bale tiene mayor química predicha.
- A medida que Rodrygo y Vinícius acumulan partidos, superan a Bale (~20 partidos Vinícius, ~40 partidos Rodrygo).
- Con los creativos (Benzema, Kroos, Hazard, Isco): Bale lidera, pero Hazard gela mejor con Rodrygo y Vinícius.

### 7.3 ¿A qué club debería ir Hakim Ziyech (Ajax)?
Candidatos pre-seleccionados: Internazionale, Roma, Chelsea, Bayern Munich, Arsenal.
- **Metodología:** (1) SciSports predice minutos jugados, evolución de SciSkill y viabilidad económica → top 5 clubs. (2) Team Builder con Ziyech forzado + 10 del club.
- **Resultado:** Bayern Munich ofrece la mayor química ofensiva predicha para Ziyech.

---

## Limitaciones y trabajo futuro

- JDI limitado por ausencia de tracking data (acciones defensivas invisibles en event data).
- Actualmente solo captura química entre **pares**; futuro: grupos de más de dos jugadores.
- Incorporar spatio-temporal tracking data para métricas defensivas más precisas.

---

## Referencias clave

| # | Referencia |
|---|-----------|
| [2] | **Este paper**: Bransen & Van Haaren (2020) — Player Chemistry |
| [6] | Decroos, Bransen, Van Haaren, Davis (2019) — **VAEP framework** (SIGKDD) |
| [7] | Aalbers (2016) — SciSkill Index |
| [8] | Aalbers & Van Haaren (2018) — **Player Roles** (22 roles desde event data) |
| [9] | Cervone et al. (2014) — EPV framework para basketball (inspiró VAEP) |
| [10] | Prokhorenkova et al. (2018) — **CatBoost** (NeurIPS) |
| [1] | Beal & Ramchurn (2019) — Teamwork en StatsBomb Conference |
