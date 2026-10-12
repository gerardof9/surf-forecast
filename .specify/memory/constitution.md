<!--
Sync Impact Report
- Version change: (template placeholders) → 1.0.0
- Modified principles: template PRINCIPLE_1–5 → I–XIV (full replacement with project principles)
- Added sections: Precedence Criterion; Compliance Expectations
- Removed sections: none (template slots filled; example-only comments removed)
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated (Constitution Check gates)
  - .specify/templates/spec-template.md ✅ updated (constitution-aligned constraints)
  - .specify/templates/tasks-template.md ✅ updated (pragmatic tests; no auth-by-default)
  - .specify/templates/commands/*.md — N/A (directory absent)
  - README.md / docs/quickstart.md — N/A (no project runtime docs yet)
- Follow-up TODOs: none
-->

# Surf Forecast La Paloma Constitution

## Core Principles

### I. Costo cero y uso personal

El proyecto es exclusivamente personal y no comercial. Ninguna decisión
puede introducir costos obligatorios ni depender de servicios de pago,
suscripciones o licencias comerciales. Se priorizan fuentes de datos,
herramientas y servicios gratuitos compatibles con este uso. Las
limitaciones de las cuotas gratuitas DEBEN documentarse.

**Rationale**: Un proyecto personal no debe acumular costos fijos ni
bloquearse por licencias; la transparencia de cuotas evita fallos
sorpresa.

### II. Ejecución bajo demanda y sin infraestructura permanente

El sistema se ejecuta únicamente cuando el usuario lo solicita. NO
requiere servidores permanentemente activos, procesos en segundo plano,
servicios autónomos ni infraestructura de ejecución continua. Puede
consumir servicios externos gratuitos y reutilizar datos almacenados
localmente. Cada ejecución DEBE poder realizarse de forma controlada y
explicar qué datos utilizó.

**Rationale**: Sin siempre-encendido no hay costo de hosting ni
mantenimiento de daemons; la trazabilidad por ejecución es el mínimo
operativo.

### III. Flexibilidad y capacidad de corrección

Los criterios de evaluación, ponderaciones, umbrales y fórmulas DEBEN
ser configurables, versionados y reemplazables sin modificar
innecesariamente el resto del sistema. Las observaciones reales pueden
justificar cambios en los criterios. Ningún modelo, fórmula o umbral
DEBE considerarse definitivo sin validación suficiente.

**Rationale**: El surf es empírico; los criterios deben evolucionar con
evidencia sin reescrituras totales.

### IV. Modularidad y simplicidad arquitectónica

La obtención de datos, el almacenamiento, la evaluación de condiciones y
la presentación de resultados DEBEN mantener responsabilidades
separadas. Las fuentes de datos y los criterios de evaluación DEBEN
poder sustituirse de forma independiente. NO se incorporará
infraestructura, abstracciones ni dependencias que no aporten un
beneficio concreto y justificado.

**Rationale**: Separar concerns permite cambiar fuentes o reglas sin
arrastrar el resto; YAGNI evita complejidad prematura.

### V. Honestidad sobre la incertidumbre

Los puntajes y niveles de confianza son indicadores de evaluación, no
probabilidades de éxito, salvo que hayan sido calibrados y validados
estadísticamente. Las discrepancias entre fuentes y modelos DEBEN
hacerse visibles. La falta de datos, la incertidumbre y las limitaciones
del pronóstico DEBEN comunicarse explícitamente; NO deben ocultarse
mediante puntajes aparentemente precisos.

**Rationale**: Una precisión falsa es más peligrosa que una incertidumbre
declarada.

### VI. Informar, no decidir por el usuario

El sistema presenta datos, condiciones estimadas, evaluaciones,
limitaciones y niveles de confianza para facilitar la decisión personal
de viajar o surfear. NO debe presentar sus clasificaciones como
garantías de que habrá olas surfables ni sustituir la evaluación del
usuario sobre las condiciones reales y su seguridad.

**Rationale**: La seguridad en el agua es responsabilidad del usuario; el
sistema es un apoyo informativo.

### VII. Validación contra la realidad

La calidad del pronóstico DEBE evaluarse mediante observaciones reales
de las condiciones de surf y, cuando sea posible, mediante comparación
con pronósticos o referencias existentes. Las mejoras DEBEN
demostrarse mediante comparaciones documentadas y criterios
consistentes. NO se afirmará que una fuente, fórmula o modelo es
superior sin evidencia suficiente.

**Rationale**: Sin anclaje empírico, las “mejoras” son opinión.

### VIII. No inventar ni confundir datos

Los nombres y unidades de las variables, las capacidades de las fuentes,
las coordenadas, las orientaciones de los picos y cualquier otro dato
técnico DEBEN verificarse antes de utilizarse. Los datos observados,
los pronósticos de modelos y las estimaciones derivadas DEBEN
distinguirse claramente. En particular, la altura de ola pronosticada
en mar abierto NO debe presentarse como altura real de rompiente en la
playa. Los datos desconocidos DEBEN identificarse como tales, no
completarse mediante suposiciones silenciosas.

**Rationale**: Confundir offshore con rompiente o rellenar huecos
silenciosos produce decisiones erróneas.

### IX. Trazabilidad y reproducibilidad

Cada evaluación DEBE poder relacionarse con los datos de entrada, las
fuentes consultadas, la fecha y hora de referencia, las reglas aplicadas
y la versión de los criterios utilizados. Cuando sea técnicamente
viable, DEBEN conservarse los datos y resultados necesarios para
reproducir y analizar evaluaciones anteriores.

**Rationale**: Sin trazabilidad no hay depuración ni aprendizaje de
errores.

### X. Simplicidad primero y evolución basada en evidencia

La primera versión DEBE implementar el camino más sencillo que permita
generar evaluaciones útiles, transparentes y verificables. Se
incorporarán nuevas fuentes, modelos, funcionalidades o componentes
únicamente cuando exista una necesidad concreta y un beneficio esperado
que justifique su costo, complejidad y mantenimiento.

**Rationale**: Empezar simple acelera el aprendizaje real; escalar solo
con evidencia evita over-engineering.

### XI. Verificación pragmática y proporcional al riesgo

La validación DEBE incluir situaciones reales de oleaje y viento, casos
históricos cuando estén disponibles y revisión manual de los resultados.
NO se exige una infraestructura compleja de pruebas ni integración
continua. Se permiten pruebas automatizadas pequeñas y focalizadas
cuando reduzcan significativamente el riesgo de errores o regresiones,
especialmente en cálculos, umbrales y transformaciones de datos.

**Rationale**: El riesgo está en los números y transformaciones, no en
montar un CI enterprise para un uso personal.

### XII. Degradación elegante y transparencia ante fallos

La caída, indisponibilidad o falta de datos de una fuente NO debe
provocar resultados engañosos ni el fallo innecesario de todo el
sistema. Siempre que sea posible, se utilizarán los datos válidos
disponibles y se indicará qué fuentes fallaron, qué información falta y
cómo afecta esa limitación al resultado. La confianza NUNCA debe
aumentar artificialmente por la ausencia de información.

**Rationale**: Fallar en silencio o inventar confianza ante huecos es
peor que un resultado parcial explícito.

### XIII. Privacidad y alcance mínimo

El proyecto es de uso personal y NO requiere cuentas de usuario,
autenticación multiusuario, pagos, telemetría ni recopilación de
información personal. NO se incorporarán estas capacidades salvo que el
alcance se modifique expresamente y se justifique su necesidad.

**Rationale**: Alcance mínimo = menos superficie de ataque, menos
dependencias y alineación con el uso personal.

### XIV. Disciplina de implementación

Las decisiones técnicas DEBEN ser coherentes con estos principios y con
la especificación vigente. Ante una ambigüedad, se DEBE preferir la
alternativa más sencilla, gratuita, verificable y reversible. Las
decisiones que introduzcan costos, complejidad significativa, nuevas
dependencias o cambios arquitectónicos relevantes DEBEN justificarse
explícitamente antes de implementarse.

**Rationale**: La constitución solo funciona si las implementaciones la
respetan de forma deliberada.

## Precedence Criterion

Estos principios orientan todas las decisiones del proyecto. Si una
propuesta contradice alguno de ellos, la contradicción DEBE identificarse
y resolverse explícitamente antes de continuar. Los cambios en estos
principios DEBEN ser deliberados y documentados, no introducirse
implícitamente como consecuencia de una decisión de implementación.

## Compliance Expectations

- Todo plan (`plan.md`) DEBE pasar el Constitution Check antes de
  investigación (Phase 0) y revalidarse tras el diseño (Phase 1).
- Toda especificación DEBE respetar costo cero, honestidad sobre
  incertidumbre, no inventar datos, y el rol informativo (no decisional).
- Las tareas DEBEN favorecer modularidad, trazabilidad y verificación
  pragmática; NO asumen cuentas, CI complejo ni infraestructura
  permanente por defecto.
- Violaciones justificadas se documentan en Complexity Tracking del plan
  con alternativa más simple rechazada y motivo.

## Governance

Esta constitución prevalece sobre hábitos informales, plantillas genéricas
y preferencias ad hoc. Las enmiendas DEBEN:

1. Documentar el cambio (principio afectado, motivo, impacto).
2. Incrementar la versión según semver:
   - MAJOR: eliminación o redefinición incompatible de principios.
   - MINOR: nuevo principio/sección o expansión material de guía.
   - PATCH: aclaraciones, redacción, typos, refinamientos no semánticos.
3. Actualizar `Last Amended` a la fecha ISO del cambio.
4. Propagar el impacto a plantillas y guías dependientes cuando cambien
   restricciones o categorías de trabajo.
5. Resolver conflictos con la especificación vigente de forma explícita
   antes de implementar.

La revisión de cumplimiento ocurre en Constitution Check de cada plan y
en revisiones manuales de resultados contra observaciones reales
(Principios VII y XI). Complejidad, costos y nuevas dependencias
requieren justificación escrita previa (Principio XIV).

**Version**: 1.0.0 | **Ratified**: 2026-10-12 | **Last Amended**: 2026-10-12
