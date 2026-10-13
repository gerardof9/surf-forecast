# Feature Specification: Pronóstico personalizado de surf para La Paloma

**Feature Branch**: `001-la-paloma-surf-forecast`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Herramienta personal, de uso a demanda, que reúne datos gratuitos de oleaje y viento para estimar, pico por pico, si habrá olas surfeables hoy y en los próximos 4 días en La Paloma, con confianza, perfiles locales y evolución por etapas."

## Scope Summary

**Primary question**: ¿Habrá olas en cada pico de La Paloma hoy y en los próximos 4 días?

**Secondary**: ¿Con qué calidad, en qué horas y con cuánta confianza?

**Medium-term (later stage)**: ¿Qué swell muestran ya los modelos en camino para los días siguientes?

**Surfeable definition**: tamaño estimado ≥ 0,5 m (ola real, no altura bruta del modelo). Viento, período y dirección gradúan la calidad; no descartan por sí solos la existencia de olas.

**First delivery (MVP)**: US1, US2 y US3 — pronóstico operativo básico para hoy + 4 días (5 días), cinco picos, confianza básica, degradación ante fallos de fuentes, interfaz de terminal. Análisis narrativo elaborado, tendencia a mediano plazo, observaciones/ajustes y evaluación de desempeño pertenecen a etapas posteriores y **no amplían** el alcance de la primera entrega.

**Delivery stages (order)**:
1. Primera: US1–US3 (operativo + perfiles + confianza básica)
2. Segunda: US4 (análisis / comparación de modelos) + US5 (tendencia 5–10 días)
3. Tercera: US6 (observaciones y corrección controlada del criterio)
4. Última: US7–US9 (comparación con referencia, cambios entre consultas, otras zonas)

**Out of scope (first delivery and until expressly added)**: otras zonas (p. ej. La Pedrera), uso comercial/multiusuario/cuentas/pagos, alertas o procesos autónomos, interfaces gráficas o web, marea, extracción automática de sitios de pronóstico, modelos propios de propagación/hidrodinámica costera, presentar probabilidad de acierto sin contrastar con observaciones.

## User Scenarios & Testing *(mandatory)*

La condición de surf usa una escala única (también en observaciones): **Sin olas surfeables** (< 0,5 m estimado), **Olas pequeñas pero surfeables**, **Razonable**, **Buena**, **Muy buena**, más **Incierto** (confianza baja) y **Pronóstico incompleto** (faltan datos). El sistema informa; no recomienda ni desaconseja surfear ni viajar.

### User Story 1 - Condiciones hoy y próximos días (Priority: P1) — First delivery

Como surfista de La Paloma, quiero ver para hoy y para los próximos 4 días qué condiciones habrá en cada pico, para saber cuándo y dónde habrá olas surfeables.

**Why this priority**: razón de ser del sistema.

**Independent Test**: con datos de ejemplo, una consulta produce el resumen de cada día.

**Acceptance Scenarios**:

1. **Given** hay datos de al menos una fuente, **When** el usuario pide el pronóstico, **Then** recibe para hoy y cada uno de los siguientes 4 días un resumen con titular, rango de tamaño, swell dominante (período y dirección), viento (rango de velocidad, dirección y rotación durante el día), condición de surf y confianza.
2. **Given** un día en que las condiciones difieren entre picos, **Then** el resumen muestra la condición de cada pico y destaca los mejores.
3. **Given** un día sin datos suficientes de oleaje o de viento, **Then** se marca Pronóstico incompleto y nunca Sin olas surfeables.
4. **Given** un día con confianza baja, **Then** la condición se presenta como Incierto y se explica brevemente la causa (datos incompletos, antiguos, una sola fuente/modelo útil o perfil provisional). La comparación detallada entre modelos pertenece a US4.
5. **Given** el día actual, **Then** solo se consideran las horas que faltan y se indica la hora de la consulta.

---

### User Story 2 - Detalle por pico y franja (Priority: P1) — First delivery

Como surfista, quiero saber cómo evolucionan las condiciones de cada pico a lo largo del día y en qué momento estarán mejor.

**Why this priority**: la hora y el viento definen la calidad tanto como el tamaño.

**Independent Test**: para un pico y un día de ejemplo se obtiene el desglose por franjas.

**Acceptance Scenarios**:

1. **Given** un pico y un día, **When** el usuario mira el detalle, **Then** ve las condiciones a las 06:00, 12:00 y 18:00 (tamaño, período, dirección del swell y si es favorable para ese pico, viento y si es favorable) y la mejor ventana de al menos 2 horas.
2. **Given** que el viento empeora por la tarde sin que cambie el tamaño, **Then** la mejor franja es la mañana y se explica por qué.
3. **Given** que el tamaño aumenta pero el viento empeora, **Then** no se interpreta como una mejora de la calidad.
4. **Given** un día a partir de pasado mañana, **Then** se indica la franja del día más favorable (mañana, mediodía o tarde) sin prometer una hora precisa.

---

### User Story 3 - Perfil de cada pico (Priority: P1) — First delivery

Como conocedor de la zona, quiero describir cómo funciona cada pico (direcciones de swell, vientos limpios, abrigo, períodos, fondo) para que el sistema distinga entre picos cercanos.

**Why this priority**: los modelos regionales no distinguen picos; el perfil es lo que los diferencia.

**Independent Test**: con perfiles completos e incompletos de ejemplo, cada pico recibe su estado correcto.

**Acceptance Scenarios**:

1. **Given** un pico con todos los datos esenciales y sin contraste con observaciones, **Then** se evalúa como provisional, se muestra marcado y su confianza no supera media.
2. **Given** un pico al que le faltan datos esenciales, **Then** es incompleto: no recibe condición, se lista aparte con lo que le falta y con los datos regionales disponibles. Los campos opcionales estimados no lo habilitan.
3. **Given** un pico que el usuario marcó como calibrado tras comparar con observaciones, **Then** se evalúa como calibrado.
4. **Given** un perfil con valores incoherentes, **Then** el sistema lo detecta y lo informa antes de evaluar.
5. **Given** un swell, período o viento que difieren de los ideales del perfil, **Then** el sistema estima con una regla inicial documentada y provisional si aun así podrían llegar olas ≥ 0,5 m; indica que es estimación, expresa incertidumbre; no descarta solo por no ser ideal ni presenta la estimación como medición o conversión física validada.

---

### User Story 4 - Entender por qué (Priority: P2) — Second stage

Como usuario que no quiere confiar a ciegas, quiero ver qué datos y reglas llevaron a cada condición y leer un análisis breve.

**Why this priority**: da confianza y permite detectar errores; la condición ya sirve sin esto.

**Independent Test**: para una condición cualquiera se puede reconstruir el razonamiento.

**Acceptance Scenarios**:

1. **Given** cualquier condición, **When** se consulta el detalle de razonamiento (etapa US4), **Then** el usuario ve valores de oleaje y viento usados, fuente y modelo, factores favorables/perjudiciales y un análisis breve en lenguaje natural marcado como generado automáticamente. En la primera entrega basta con datos básicos, condición, confianza y motivo breve basado en reglas sencillas.
2. **Given** que dos o más modelos difieren, **Then** (US4) se muestran por separado con su desacuerdo, no solo un promedio.
3. **Given** que el resultado depende de un pico provisional, **Then** eso se indica junto a la condición.
4. **Given** que se usaron datos guardados de una consulta anterior, **Then** se informa su antigüedad.

---

### User Story 5 - Tendencia a mediano plazo (Priority: P2) — Second stage

Como usuario, quiero una estimación de lo que viene más adelante, basada en el swell que los modelos ya muestran en camino.

**Why this priority**: amplía el horizonte con menos fiabilidad que el plazo corto.

**Independent Test**: una consulta muestra la tendencia separada del pronóstico operativo.

**Acceptance Scenarios**:

1. **Given** que las fuentes cubren ese plazo, **When** se consulta, **Then** se muestra por día una tendencia regional de oleaje y viento, claramente distinta del pronóstico operativo.
2. **Given** un swell que los modelos ya muestran en camino, **Then** se informa llegada estimada e incertidumbre, sin afirmar olas surfeables en un pico.
3. **Given** un día de ese plazo, **Then** no se emite condición por pico ni por hora.
4. **Given** que la señal cambia entre consultas o entre modelos, **Then** se indica confianza baja.

---

### User Story 6 - Observaciones y corrección del criterio (Priority: P2) — Third stage

Como usuario, quiero anotar lo que encontré en el agua (o lo que dicen otros pronósticos) y que el sistema revise su criterio cuando se equivoca.

**Why this priority**: permite pasar de reglas provisionales a reglas validadas.

**Independent Test**: con un caso de ejemplo en que el sistema se equivoca, se obtiene una propuesta de ajuste.

**Acceptance Scenarios**:

1. **Given** que el usuario registra una observación (fecha, hora, pico, condición en la escala común, tamaño, viento, tipo subjetiva/instrumental), **Then** queda guardada y no se mezcla con otro tipo.
2. **Given** que el usuario avisa inconsistencia con lo que ve en el pico, **Then** el sistema registra la discrepancia, conserva intacto el pronóstico original e identifica criterios involucrados; solo con regla justificable y evidencia suficiente aplica ajuste automático acotado y reversible sin confirmación adicional.
3. **Given** que se aplicó un ajuste, **Then** recalcula el pronóstico vigente, muestra el resultado nuevo e indica qué cambió; la observación no sustituye el pronóstico histórico; si el nuevo resultado no concuerda con la observación, lo informa.
4. **Given** que el error es de las fuentes o la causa no se identifica con respaldo, **Then** registra la discrepancia, no modifica el criterio por error de fuente, y si la causa es incierta propone ajuste para revisión.
5. **Given** que un ajuste empeoraría casos pasados de forma apreciable, **Then** solo se aplica si mejora el caso nuevo y deja constancia del conflicto.
6. **Given** que se aplicó un ajuste, **Then** queda registrado con fecha y motivo, es reversible, y las consultas posteriores usan el criterio nuevo.
7. **Given** un pronóstico de referencia cargado a mano que discrepa, **Then** se registra como evidencia pero no modifica el criterio por sí solo.
8. **Given** un conjunto suficiente de observaciones, **When** el usuario pide evaluación, **Then** recibe informe de aciertos/errores por anticipación (mismo día, 1–4 días, tendencia 5–10) con falsos positivos y oportunidades no detectadas.
9. **Given** días sin pronósticos guardados, **Then** el informe lo declara y solo usa histórico de fuentes si existe.

---

### User Story 7 - Comparar con referencia existente (Priority: P3) — Later stage

Como usuario, quiero comparar el pronóstico del sistema con el de otro sitio uruguayo y con lo observado, para saber si la herramienta es más precisa.

**Why this priority**: la precisión solo se demuestra con comparación; requiere observaciones acumuladas.

**Independent Test**: con referencias y observaciones de ejemplo se obtiene la comparación.

**Acceptance Scenarios**:

1. **Given** un pronóstico de referencia ingresado a mano, **Then** queda guardado separado del propio.
2. **Given** conjunto suficiente de observaciones con propios y referencia, **Then** el informe compara ambos contra lo observado.
3. **Given** cualquier uso, **Then** el sistema no extrae ni reproduce contenido del sitio de referencia: solo guarda lo que el usuario ingresa.

---

### User Story 8 - Cambios desde la última consulta (Priority: P3) — Later stage

Como usuario que consulta cada tanto, quiero ver rápido qué cambió.

**Why this priority**: comodidad; no afecta el contenido del pronóstico.

**Independent Test**: dos consultas seguidas con datos distintos muestran la diferencia.

**Acceptance Scenarios**:

1. **Given** consulta anterior con menos de 72 horas, **Then** se destacan cambios relevantes (condición, mejor pico, tamaño estimado).
2. **Given** que no existe o es más antigua, **Then** se indica "sin comparación reciente".

---

### User Story 9 - Sumar otras zonas (Priority: P3) — Later stage

Como usuario, quiero poder agregar más adelante picos de otras zonas (p. ej. La Pedrera).

**Why this priority**: no se necesita en la primera versión, pero condiciona el diseño.

**Independent Test**: se agrega un pico de prueba y aparece en la consulta.

**Acceptance Scenarios**:

1. **Given** un nuevo pico con su perfil, **When** se agrega, **Then** aparece en las consultas sin modificar el funcionamiento del sistema.

---

### Edge Cases

- Una fuente falla o tarda demasiado: la consulta continúa con las demás; se indica el estado de cada fuente. Con una sola fuente disponible, la confianza no supera media.
- Fallan todas las fuentes: si hay datos guardados recientes, se usan con antigüedad informada; si no, se dice con claridad y no se genera pronóstico.
- Sin conexión: solo puede mostrar la última consulta guardada, identificada como tal.
- Consultas repetidas en poco tiempo: se reutilizan datos recientes salvo que el usuario pida actualizar.
- Modelos en desacuerdo: se muestran por separado y baja la confianza; no se ocultan con un promedio.
- Modelos no independientes (mismo origen/servicio): no cuentan como confirmación mutua.
- Mar de viento vs marejada de fondo: no se confunden.
- Swell en crecimiento o descenso: se informa llegada / pico / bajada cuando haya respaldo.
- Viento que rota: se evalúa por franja; no se usa un valor medio del día.
- Tamaño crece pero viento empeora: no es mejora de calidad.
- Swell llega a la zona pero un pico no lo recibe: no se asume respuesta uniforme de la costa.
- Altura de modelo ≠ altura percibida: el mínimo 0,5 m es sobre ola real; la conversión es estimación ajustable.
- Menos de 2 horas válidas en un día: ese día no tiene ventana y no se clasifica como Sin olas surfeables.
- Datos que no distinguen picos o ubicación sobre tierra: se detecta, se informa; no se presentan diferencias no respaldadas.
- Fuente deja de ser gratuita o cambia condiciones: se sigue con las demás; nunca se activa un costo.
- Referencia vs sistema discrepan: no se declara quién tiene razón; se compara contra lo observado.
- Pocas o ninguna observación: puntaje y confianza no se presentan como probabilidades.
- Aviso aislado: ajustes acotados, reversibles y contrastados con casos pasados; no cambio drástico por un único caso.

## Requirements *(mandatory)*

### Functional Requirements

#### Consulta a demanda

- **FR-001**: El sistema DEBE funcionar a demanda: al recibir la orden del usuario, obtener datos, procesarlos y entregar el pronóstico sin depender de procesos previos ni permanentes.
- **FR-002**: El sistema DEBE entregar el resultado en una interfaz de terminal (texto) simple: resumen inmediato y detalle por pico/franja a pedido, sin requerir navegador ni aplicación gráfica. *(First delivery)*
- **FR-003**: El sistema DEBE reutilizar datos recientes para no repetir descargas innecesarias, y permitir forzar actualización o trabajar solo con lo guardado.

#### Fuentes y datos

- **FR-004**: El sistema DEBE usar exclusivamente fuentes y herramientas de costo cero, sin suscripciones, pruebas que pasen a pago ni créditos que se agoten.
- **FR-005**: El sistema DEBE respetar las condiciones de uso de cada fuente (uso personal, límites de consulta, atribución).
- **FR-006**: El sistema DEBE informar, para cada dato mostrado, de qué fuente y modelo proviene y de cuándo es.
- **FR-007**: El sistema NO DEBE tratar como independientes a fuentes que comparten origen.
- **FR-008**: El sistema DEBE distinguir dato medido, dato pronosticado, inferencia física y regla empírica.
- **FR-009**: El sistema NO DEBE extraer automáticamente contenido de páginas web de terceros cuando su condición de uso no lo permita.
- **FR-010**: El sistema DEBE seguir funcionando con las fuentes restantes cuando una falle o cambie sus condiciones.

#### Perfiles de picos

- **FR-011**: El sistema DEBE mantener un perfil por pico, editable por el usuario sin modificar el sistema: ubicación, orientación, direcciones de swell ideales (y si se conocen aceptables/bloqueadas), vientos terrales, abrigo por dirección, período ideal y tipo de fondo.
- **FR-012**: El sistema DEBE derivar el estado del perfil (incompleto, provisional o calibrado) de su contenido y de la decisión del usuario, y comportarse según ese estado (US3).
- **FR-013**: El sistema NO DEBE estimar ni inventar campos esenciales del perfil (orientación, swell ideales, período ideal, vientos terrales). Campos opcionales faltantes PUEDEN estimarse con regla documentada, marcarse como estimados y ser corregibles; si no hay base, quedan desconocidos. Una estimación no habilita un perfil incompleto.
- **FR-014**: El sistema DEBE informar cuando varios picos reciben los mismos datos de origen (diferencias solo por perfiles).
- **FR-015**: El sistema DEBE permitir agregar picos o zonas nuevas aportando solo sus perfiles.

#### Evaluación y condición de surf

- **FR-016**: El sistema DEBE evaluar para cada pico y franja la compatibilidad entre oleaje, viento y perfil. En la primera entrega DEBE usar una regla inicial sencilla, explícita, documentada y provisional para estimar tamaño surfeable; no presentarla como conversión física validada ni predicción de altura de rompiente; debe poder reemplazarse/calibrarse; variaciones respecto de ideales no descartan automáticamente olas surfeables.
- **FR-017**: El sistema DEBE clasificar el viento respecto de cada pico como terral, terral de costado, de costado, maral de costado o maral, según orientación y abrigo, con intensidad (suave, moderado, fuerte, muy fuerte), y describir la rotación diaria.
- **FR-018**: El sistema DEBE distinguir mar de viento local de marejada lejana cuando los datos lo permitan; informar si el swell crece, está en pico o baja cuando haya respaldo; estimar tamaño surfeable distinto de la altura bruta del modelo (FR-016); si no hay respaldo para el umbral 0,5 m, mostrar rango/incertidumbre o Incierto; NO interpretar altura significativa como altura de olas que rompen.
- **FR-019**: El sistema DEBE clasificar cada franja y cada día de cada pico en la escala común o en Incierto / Pronóstico incompleto. Sin olas surfeables = tamaño estimado < 0,5 m.
- **FR-020**: El sistema DEBE basar la condición del día de un pico en su mejor ventana contigua de al menos 2 horas dentro de horas de luz, no en el promedio del día.
- **FR-021**: El sistema DEBE informar si el tamaño surfeable estimado podría alcanzar 0,5 m (ola real). Viento/período/dirección gradúan calidad pero no descartan existencia. Sin respaldo: Incierto o rango. NO recomendar ni desaconsejar surfear o viajar.
- **FR-022**: El sistema DEBE mostrar solo lo necesario: no incluye energía del oleaje, temperatura del agua ni traje sugerido.
- **FR-023**: El sistema DEBE ajustar precisión al horizonte: hoy y mañana — 06:00/12:00/18:00 y ventana ≥ 2 h; pasado mañana a día 4 — condición del día y franja favorable sin hora precisa; días 5–10 — solo tendencia (US5).
- **FR-024**: Para el día actual, DEBE considerar solo horas restantes e indicar hora de consulta.
- **FR-025**: En segunda etapa, DEBE acompañar cada día/pico con análisis breve en lenguaje natural marcado como automático. En primera entrega: motivo breve basado en reglas, sin narrativa elaborada.
- **FR-026**: El sistema DEBE ofrecer tendencia a mediano plazo (días 5–10) con tamaño, período y dirección esperados y llegada estimada, distinta del operativo, sin condición por pico/hora. Se limita al swell ya mostrado en camino; fenómenos aún no generados se evalúan en el plan. *(Second stage — US5)*

#### Incertidumbre y confianza

- **FR-027**: En primera entrega, confianza alta/media/baja por reglas documentadas (disponibilidad, antigüedad, completitud, estado del perfil). Ausencia de dato necesario NO es señal favorable.
- **FR-028**: Confianza limitada a media con una sola fuente/modelo útil o pico provisional; baja si datos incompletos, antiguos o insuficientes.
- **FR-029**: NO presentar puntajes ni confianza como probabilidades hasta contrastarlos con observaciones.
- **FR-030**: En segunda etapa, mostrar valores por modelo, desacuerdo y rango. En primera entrega, si hay desacuerdo evidente, no ocultarlo y reducir confianza.
- **FR-031**: Falta de un componente de confianza = dato faltante informado, no buena señal.

#### Transparencia y trazabilidad

- **FR-032**: Cada condición DEBE rastrearse hasta datos, fuentes, reglas y perfil.
- **FR-033**: DEBE advertir siempre que los modelos regionales no distinguen picos cercanos.

#### Observaciones y validación *(from third stage / US6–US7)*

- **FR-034**: Permitir registrar observaciones con escala común, tamaño, viento y tipo (subjetiva/instrumental), sin mezclar tipos.
- **FR-035**: Conservar el pronóstico emitido en cada consulta para comparar con lo observado.
- **FR-036**: Permitir ingresar a mano pronósticos de referencia, guardarlos separados y compararlos con lo observado, sin extracción automática.
- **FR-037**: Evaluar desempeño por anticipación (mismo día, 1–4 días, tendencia 5–10): error de tamaño/período/dirección, aciertos/errores de condición, falsos positivos, oportunidades no detectadas, calidad de franja; comparar con referencias.
- **FR-038**: En US6, registrar discrepancias y evaluar posibles ajustes; aplicación automática según FR-047–FR-051.

#### Cambios entre consultas *(US8)*

- **FR-039**: Comparar con consulta anterior solo si tiene < 72 h; si no, "sin comparación reciente".

#### Operación y costo

- **FR-040**: Completar una consulta típica en tiempo breve (SC-001).
- **FR-041**: NO requerir servidores, tareas programadas ni procesos permanentes.
- **FR-042**: Registrar incidencias (fuentes caídas, datos faltantes, cambios de condiciones) y mostrarlas en el resultado.
- **FR-043**: Presentarse en español y mostrar horas en hora local de Uruguay.

#### Flexibilidad y ajuste del criterio

- **FR-044**: Permitir cambiar interpretación (perfiles, tolerancias, relación de alturas, clasificación de viento, escala) sin rehacer el sistema ni perder registros.
- **FR-045**: Permitir incorporar métodos alternativos y compararlos sobre los mismos datos.
- **FR-046**: Indicar en cada resultado con qué criterio se calculó.
- **FR-047**: En US6, ante aviso de inconsistencia: registrar discrepancia, identificar criterios; solo con regla justificable y evidencia suficiente aplicar ajuste automático acotado y reversible. Un aviso aislado no basta para demostrar que la regla general es incorrecta.
- **FR-048**: Tras ajuste: recalcular vigente, mostrar cambios, conservar original y observación separados; si no concuerda con observación, informarlo.
- **FR-049**: Guardar cada ajuste con fecha y motivo y permitir revertirlo.
- **FR-050**: Acotar cada ajuste, comprobarlo contra casos pasados y dejar constancia si mejora el nuevo caso pero empeora anteriores.
- **FR-051**: Si la causa es de las fuentes: registrar y NO modificar criterio. Si la causa es incierta: conservar original, registrar observación y proponer ajuste para revisión.

#### Crecimiento

- **FR-052**: Poder incorporar fuentes nuevas sin cambiar lo que el usuario ve ni cómo se interpretan las condiciones.
- **FR-053**: Poder ofrecerse más adelante con otra forma de uso (web o escritorio) sin rehacer funciones ni perder datos. Hoy: terminal.
- **FR-054**: Ser lo más simple posible; complejidad adicional justificada por beneficio al usuario.
- **FR-055**: Poder crecer en picos, fuentes, días y métodos sin cambiar lo que ya funciona.

### Key Entities

- **Pico**: lugar de surf evaluado individualmente (nombre, zona, ubicación, perfil asociado).
- **Perfil del pico**: cómo funciona el pico (orientación; swell ideales/aceptables/bloqueadas; vientos terrales; abrigo por dirección; períodos útiles; fondo; estado incompleto/provisional/calibrado).
- **Criterio de interpretación**: reglas/fórmulas versionadas reemplazables (tolerancias, relación altura modelo↔ola, clasificación de viento, escala de condición, versión y fecha).
- **Criterio de surfeable**: tamaño mínimo 0,5 m sobre ola real; viento/período/dirección solo gradúan calidad.
- **Fuente de datos**: origen externo (proveedor, modelo, condiciones de uso, costo, estado disponible/degradada/caída).
- **Pronóstico regional**: lo que una fuente/modelo dice hora a hora (oleaje total y por componente, viento/ráfagas; emisión, descarga, validez).
- **Consulta**: una ejecución a demanda (fuentes y estado, versión de criterio, horizonte, incidencias, antigüedad).
- **Condición de un pico en una franja**: tamaño estimado, período, dirección y favorabilidad, viento (clase/intensidad/favorabilidad), condición en escala, valores por modelo.
- **Ventana**: mejor tramo continuo ≥ 2 h (inicio, fin, condición).
- **Resumen del día**: titular, rango de tamaño, swell dominante, viento y rotación, condición por pico, mejor pico/franja, confianza, motivo/análisis.
- **Tendencia a mediano plazo**: días 5–10 (tamaño/período/dirección esperados, llegada, confianza).
- **Confianza**: nivel alta/media/baja, componentes, motivo de límites.
- **Observación**: lo encontrado realmente (fecha/hora/pico/condición/tamaño/viento/tipo/notas).
- **Pronóstico de referencia**: pronóstico ajeno ingresado a mano (emisión, día, pico/zona, tamaño, calificación, origen).
- **Discrepancia**: contradicción observada/referencia vs sistema (estado pendiente/ajustada/descartada).
- **Ajuste de criterio**: cambio aplicado (qué, motivo, discrepancias, fecha, versión anterior reversible).
- **Informe de desempeño**: aciertos/errores por anticipación, falsos positivos, oportunidades no detectadas, comparación con referencia, ajustes sugeridos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una consulta completa (orden → resumen en pantalla) tarda menos de 30 segundos con conexión normal en al menos el 90 % de las consultas.
- **SC-002**: Costo de uso = cero: ninguna función requiere pago, tarjeta ni suscripción.
- **SC-003**: El 100 % de las condiciones puede rastrearse hasta datos, fuentes, reglas y perfil.
- **SC-004**: Ningún pico con perfil incompleto recibe condición en ninguna consulta.
- **SC-005**: Un día sin datos suficientes nunca se muestra como Sin olas surfeables.
- **SC-006**: Con una o más fuentes caídas (pero no todas), la consulta entrega resultado en el 100 % de los casos de prueba y muestra el estado de cada fuente.
- **SC-007**: El usuario entiende la condición de hoy y de los próximos días leyendo el resumen en menos de 2 minutos.
- **SC-008**: Agregar un pico nuevo requiere únicamente completar su perfil, sin cambios en el funcionamiento del sistema.
- **SC-009**: Con ≥ 20 observaciones, el informe de desempeño cubre cada anticipación con datos y declara las que no.
- **SC-010**: Con ≥ 20 observaciones y referencias ingresadas, el informe compara acierto del sistema vs referencia.
- **SC-011**: Metas de acierto se fijan después del primer informe; hasta entonces ningún resultado se presenta como validado.
- **SC-012**: Cambiar un criterio (p. ej. tolerancia de direcciones) no exige modificar el funcionamiento del sistema.
- **SC-013**: En US6, ajuste solo con regla justificable y evidencia suficiente; si no, registra discrepancia y propone cuando corresponda; siempre conserva original y muestra observación, vigente y cambios por separado.
- **SC-014**: Sumar pico, fuente o forma nueva de uso no obliga a rehacer lo que ya funciona.
- **SC-015**: Lo que ya funcionaba sigue dando los mismos resultados tras sumar pico, fuente o forma de uso.

## Assumptions

- Un único usuario, uso personal; terminal de texto y conexión a internet al consultar (salvo modo solo-guardado).
- El usuario aporta perfiles. Esenciales: orientación, swell ideales, período ideal, vientos terrales. Opcionales (estimables si hay base): aceptables/bloqueadas, período mínimo, abrigo, fondo.
- Perfiles actuales describen ideales generales; variaciones razonables también pueden producir ≥ 0,5 m y deben estimarse e informarse como tales.
- Datos de oleaje/viento de modelos globales de resolución gruesa; no hay boyas direccionales confiables cercanas ni verdad de terreno automática.
- Altura de modelo ≠ altura percibida; la relación es estimación inicial ajustable con observaciones.
- Un sitio uruguayo de referencia sirve de modelo de *formato* y de comparación futura; **no** es fuente de datos del sistema.
- Fuentes concretas se eligen en el plan; gratuitas y de uso personal. Varios modelos del mismo servicio ≠ independencia.
- Tendencia 5–10 se limita al swell ya en camino; ciclones aún no formados fuera de la primera versión de esa etapa.
- Referencias solo por ingreso manual; no consulta automática a sitios de terceros.
- Marea, temperatura del agua y traje sugerido fuera de alcance.
- Validación apoyada en consultas que el usuario haga (historial no denso) y, si existen, históricos de fuentes.
- Anaconda, La Pedrera y otras zonas fuera de la primera versión.

### Known peak profiles (user-supplied; locations approximate; all provisional)

| Pico | También llamado | Orientación | Fondo | Swell ideal | Período ideal | Viento terral | Ubicación aprox. | Estado |
|------|-----------------|-------------|-------|-------------|---------------|---------------|------------------|--------|
| La Aguada | Arachania | E | Arena | E y ESE (SE y SSE más cruzado) | 8–12 s o más | SO, O, ONO | -34.6435, -54.1546 | Provisional |
| Zanja Honda | Corumbá | S | Arena y roca | S y SE (E y ESE también) | 9–13 s o más | N, NO, O | -34.6606, -54.1859 | Provisional |
| Los Botes | — | S | Arena y roca | S y SSO | 10–14 s o más | N, NE, ENE | -34.6618, -54.1791 | Provisional |
| La Serena | — | S | Arena y roca | S y SE (SSO también) | 9–13 s o más | N, NE, ENE | -34.6612, -54.1986 | Provisional |
| La Balconada | — | S | Arena y roca | S y SE (SSO también) | 9–13 s o más | N, NE, ENE | -34.6653, -54.1630 | Provisional |

Los cinco picos están en un tramo de pocos kilómetros, menor que la resolución de los modelos; lo que los distingue es exposición, abrigo y fondo. El sistema debe estimar otras direcciones/períodos/vientos que también produzcan ≥ 0,5 m e informarlas como estimaciones.

## Constitution Constraints *(mandatory alignment)*

- **Personal / zero cost**: Solo fuentes y herramientas gratuitas; cuotas gratuitas documentadas; nunca activar un costo.
- **On-demand**: Sin servidores permanentes, alertas autónomas ni procesos en segundo plano.
- **Honesty**: Confianza e Incierto/Incompleto visibles; no probabilidades sin calibración; desacuerdos no ocultos con promedios.
- **Inform, don't decide**: Informa condiciones y confianza; la decisión de surfear/viajar es del usuario.
- **Data integrity**: Distinguir medido / pronosticado / inferido / empírico; altura modelo ≠ rompiente; no inventar campos esenciales del perfil.
- **Traceability**: Toda condición trazable a datos, fuentes, reglas, perfil y versión de criterio.
- **Simplicity first**: Primera entrega = camino más simple (US1–US3 + terminal); etapas posteriores solo con necesidad concreta.
- **Out of scope by default**: Sin cuentas, pagos, telemetría ni multiusuario.
