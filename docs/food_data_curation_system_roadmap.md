# Food Data Curation System Roadmap

Este documento define la hoja de ruta para construir un sistema robusto de curación alimentaria multi-fuente en My Scoope.

## Contexto

My Scoope ya cuenta con una primera base importada desde USDA Foundation Foods.

El flujo actual permite:

- importar alimentos globales;
- guardar metadata de fuente;
- aplicar aliases en español;
- generar `display_name` localizado;
- buscar alimentos desde el picker con server-side search;
- mostrar nombres localizados en paneles y tablas.

Sin embargo, Foundation Foods es una base limitada. Para construir un catálogo robusto será necesario integrar otras fuentes como:

- USDA SR Legacy;
- USDA Survey/FNDDS;
- Open Food Facts;
- CIQUAL;
- FAO/INFOODS;
- LATINFOODS u otras fuentes regionales.

El desafío principal no es solo importar más alimentos, sino evitar duplicados, mantener trazabilidad y construir un catálogo confiable en español.

## Principio estratégico

My Scoope no debe crecer importando cada fuente como filas independientes en `Food`.

El sistema debe evolucionar hacia una arquitectura donde múltiples registros externos puedan apuntar a un mismo concepto alimentario curado.

Ejemplo:

~~~txt
FoodConcept: Avena cruda
├── USDA Foundation Foods: Oats, raw
├── USDA SR Legacy: Oats
├── CIQUAL: Flocons d'avoine
├── Open Food Facts: Avena tradicional
└── Alias usuario/regional: Avena
~~~

## Objetivo general

Construir un sistema de curación alimentaria que permita:

- integrar múltiples fuentes;
- detectar alimentos equivalentes;
- evitar duplicados;
- comparar información nutricional;
- crear propuestas de fusión o creación;
- usar IA como asistente de curación;
- mantener aprobación humana para cambios ambiguos;
- mejorar nombres, aliases y categorías de forma continua.

## Roadmap general

| % | Bloque | Objetivo | Resultado esperado |
|---:|---|---|---|
| 10% | Diagnóstico del modelo actual | Entender límites de `Food`, `FoodSourceMetadata`, aliases y localized names. | Mapa claro de qué se conserva y qué debe evolucionar. |
| 20% | Diseñar `FoodConcept` | Separar concepto alimentario de registro fuente. | Modelo conceptual para evitar duplicados multi-fuente. |
| 30% | Diseñar `FoodSourceItem` | Guardar cada alimento externo como fuente trazable. | Varias fuentes pueden apuntar al mismo concepto. |
| 40% | Migrar USDA actual a conceptos | Vincular alimentos actuales a conceptos iniciales. | Catálogo USDA queda preparado para multi-fuente. |
| 50% | Matching determinístico | Crear reglas seguras para detectar duplicados obvios. | Casos simples se detectan sin IA. |
| 60% | Proposal queue | Crear propuestas revisables. | Cambios ambiguos no se aplican automáticamente. |
| 70% | AI-assisted matching | Usar IA para analizar candidatos ambiguos. | Propuestas con confianza, razones y riesgos. |
| 80% | Admin review UI | Crear interfaz para aprobar/rechazar propuestas. | Curación humana eficiente. |
| 90% | Segunda fuente piloto | Importar una segunda fuente sin duplicar. | Validación real del sistema multi-fuente. |
| 100% | Documentación operativa | Dejar proceso repetible. | Sistema listo para crecimiento continuo. |

---

# Fase 1 — Diagnóstico del modelo actual

## Objetivo

Determinar qué partes del sistema actual se conservan, cuáles se adaptan y cuáles deben evolucionar.

## Estado actual

El sistema ya tiene:

~~~txt
Food
FoodSourceMetadata
FoodAlias
FoodLocalizedName
FoodImportBatch
~~~

Esto permite trabajar con una fuente externa, pero no resuelve completamente el problema multi-fuente.

## Preguntas clave

- ¿`Food` representa el alimento curado o el alimento importado desde una fuente?
- ¿Qué ocurre si dos fuentes describen el mismo alimento?
- ¿Qué fuente nutricional se considera principal?
- ¿Cómo se decide si dos alimentos son el mismo concepto?
- ¿Dónde vive el nombre visible oficial?
- ¿Dónde vive la metadata técnica de cada fuente?

## Resultado esperado

Un documento técnico corto que defina:

~~~txt
Food actual = alimento utilizable por el usuario
FoodConcept futuro = concepto alimentario curado
FoodSourceItem futuro = registro externo trazable
FoodCurationProposal futuro = propuesta revisable
~~~

---

# Fase 2 — FoodConcept

## Objetivo

Crear una entidad superior que represente el concepto alimentario curado.

## Modelo sugerido

~~~txt
FoodConcept
- id
- canonical_name
- display_name
- normalized_key
- category
- base_food
- state
- preparation
- is_generic
- status
- created_at
- updated_at
~~~

## Ejemplos

~~~txt
Avena cruda
Arroz blanco crudo
Arroz blanco cocido
Pechuga de pollo cocida
Atún en agua drenado
Harina de trigo
Semillas de zapallo crudas
~~~

## Status sugeridos

~~~txt
draft
approved
needs_review
deprecated
hidden
~~~

## Decisión importante

`FoodConcept` no reemplaza inmediatamente a `Food`.

Primero puede convivir con `Food` para reducir riesgo.

---

# Fase 3 — FoodSourceItem

## Objetivo

Separar los datos provenientes de fuentes externas del concepto alimentario curado.

## Modelo sugerido

~~~txt
FoodSourceItem
- id
- concept_id
- source
- source_food_id
- source_dataset
- source_version
- source_name
- raw_payload
- normalized_payload
- confidence
- link_status
- created_at
- updated_at
~~~

## Fuentes posibles

~~~txt
USDA_FOUNDATION
USDA_SR_LEGACY
USDA_SURVEY
OPEN_FOOD_FACTS
CIQUAL
FAO_INFOODS
LATINFOODS
MANUAL
USER
~~~

## Link status sugeridos

~~~txt
unmatched
proposed_match
approved_match
rejected_match
ignored
needs_review
~~~

## Beneficio

Varias fuentes pueden apuntar al mismo concepto sin duplicar alimentos visibles.

---

# Fase 4 — Migración del USDA actual

## Objetivo

Vincular los alimentos USDA ya importados a conceptos iniciales.

## Estrategia inicial

Para cada `Food` global USDA existente:

1. Crear un `FoodConcept`.
2. Usar `FoodLocalizedName` como `display_name` inicial.
3. Usar `FoodSourceMetadata` para crear `FoodSourceItem`.
4. Vincular `FoodSourceItem` al concepto.
5. Mantener el `Food` actual operativo para no romper picker ni planes existentes.

## Resultado esperado

~~~txt
365 USDA foods actuales
→ 365 FoodConcept iniciales
→ 365 FoodSourceItem USDA vinculados
~~~

En etapas posteriores, algunos conceptos podrán fusionarse.

---

# Fase 5 — Matching determinístico

## Objetivo

Crear reglas seguras para detectar duplicados obvios sin IA.

## Señales a usar

- normalized name exacto;
- source id exacto;
- alias exacto;
- base food;
- estado crudo/cocido;
- preparación;
- categoría;
- macros por 100g;
- diferencia calórica;
- si es producto comercial o genérico.

## Casos que pueden tener alta confianza

~~~txt
Oats, raw
Avena cruda
~~~

~~~txt
Rice, white, raw
Arroz blanco crudo
~~~

## Casos que NO deben fusionarse automáticamente

~~~txt
Arroz blanco crudo
Arroz blanco cocido
~~~

~~~txt
Huevo entero
Clara de huevo
Yema de huevo
~~~

~~~txt
Pechuga de pollo cocida
Pechuga de pollo cruda
Trutro de pollo
~~~

~~~txt
Arroz
Harina de arroz
Arroz frito preparado
~~~

## Resultado esperado

Un servicio como:

~~~txt
find_food_concept_candidates(source_item)
~~~

que devuelva:

~~~txt
candidate_concept
score
matched_signals
risk_flags
decision_hint
~~~

---

# Fase 6 — Proposal Queue

## Objetivo

Crear una cola de propuestas revisables.

La IA y las reglas determinísticas no deben modificar datos ambiguos directamente.

## Modelo sugerido

~~~txt
FoodCurationProposal
- id
- proposal_type
- candidate_source_item_id
- target_concept_id
- proposed_concept_payload
- proposed_display_name
- proposed_aliases
- proposed_category
- confidence
- reasoning_summary
- risk_flags
- status
- reviewed_by
- created_at
- reviewed_at
~~~

## Tipos de propuesta

~~~txt
create_concept
merge_with_concept
rename_concept
add_aliases
change_category
flag_quality_issue
reject_source_item
ignore_source_item
~~~

## Status

~~~txt
pending_review
approved
rejected
applied
cancelled
~~~

## Ejemplo

~~~txt
Source item:
Fish, cod, Atlantic, wild caught, raw

Proposal:
create_concept
display_name: Bacalao atlántico crudo
aliases: bacalao, pescado bacalao
category: pescado
confidence: 0.91
~~~

---

# Fase 7 — AI-assisted matching

## Objetivo

Usar IA para analizar casos ambiguos y generar propuestas explicables.

## Rol de la IA

La IA puede:

- normalizar nombres;
- extraer atributos semánticos;
- detectar equivalencias;
- detectar diferencias importantes;
- proponer display names;
- proponer aliases;
- estimar riesgo;
- explicar decisión.

## La IA no debe

- fusionar automáticamente alimentos ambiguos;
- borrar alimentos;
- cambiar macros sin revisión;
- decidir fuente nutricional principal sin reglas;
- modificar planes existentes.

## Input ideal para IA

~~~json
{
  "candidate": {
    "source": "CIQUAL",
    "name": "Riz blanc cru",
    "macros": {
      "protein": 7.1,
      "carbs": 78.0,
      "fat": 0.7,
      "kcal": 350
    }
  },
  "existing_candidates": [
    {
      "concept_id": 12,
      "display_name": "Arroz blanco crudo",
      "source_names": ["Rice, white, long grain, unenriched, raw"],
      "macros": {
        "protein": 7.13,
        "carbs": 80.0,
        "fat": 0.66,
        "kcal": 365
      }
    }
  ]
}
~~~

## Output ideal de IA

~~~json
{
  "recommended_action": "merge_with_concept",
  "target_concept_id": 12,
  "confidence": 0.94,
  "proposed_display_name": "Arroz blanco crudo",
  "proposed_aliases": ["arroz blanco", "arroz crudo"],
  "reasoning_summary": [
    "Mismo alimento base: arroz blanco",
    "Ambos están crudos",
    "Macros compatibles por 100g",
    "No hay marca comercial"
  ],
  "risk_flags": []
}
~~~

---

# Fase 8 — Admin Review UI

## Objetivo

Crear una interfaz para revisar propuestas de curación.

## Vista sugerida

Cada propuesta debería mostrar:

- alimento candidato;
- fuente;
- concepto sugerido;
- comparación de nombres;
- comparación de macros;
- explicación IA;
- risk flags;
- botones de acción.

## Acciones

~~~txt
Aprobar
Rechazar
Editar propuesta
Crear concepto nuevo
Fusionar con otro concepto
Agregar alias
Marcar como ignorado
~~~

## Principio

La curación debe ser rápida, no pesada.

El objetivo no es revisar miles de alimentos manualmente uno por uno, sino que la IA y las reglas ordenen los casos por confianza y riesgo.

---

# Fase 9 — Segunda fuente piloto

## Objetivo

Validar el sistema integrando una segunda fuente sin duplicar conceptos.

## Fuente recomendada

Primera opción:

~~~txt
USDA SR Legacy
~~~

Motivos:

- sigue siendo USDA;
- probablemente se adapta mejor al pipeline actual;
- amplía alimentos básicos;
- reduce complejidad de integración inicial.

Segunda opción:

~~~txt
CIQUAL
~~~

Motivos:

- buena base genérica;
- robusta para composición nutricional;
- útil para comparar conceptos.

Open Food Facts debería quedar para una fase separada de productos comerciales.

## Flujo

~~~txt
Source reader
→ SourceFoodCandidate
→ normalized source item
→ deterministic matching
→ AI-assisted matching
→ proposal queue
→ human review
→ concept/source link
~~~

---

# Fase 10 — Documentación operativa

## Objetivo

Documentar el protocolo de curación continua.

## Debe incluir

- cómo importar una nueva fuente;
- cómo correr dry-run;
- cómo revisar propuestas;
- cómo aprobar merges;
- cómo detectar duplicados;
- cómo revertir una propuesta;
- cómo elegir fuente nutricional principal;
- cómo actualizar nombres y aliases;
- cómo validar picker.

---

# Reglas críticas de negocio

## Nunca fusionar automáticamente si difiere estado

~~~txt
raw vs cooked
crudo vs cocido
seco vs hidratado
enlatado vs fresco
drenado vs no drenado
~~~

## Nunca fusionar automáticamente si difiere parte del alimento

~~~txt
huevo entero vs clara
pechuga vs muslo
carne con piel vs sin piel
grano vs harina
fruta vs jugo
~~~

## Separar genéricos de productos comerciales

~~~txt
Avena cruda
Quaker Old Fashioned Oats
~~~

Pueden relacionarse, pero no deberían ser el mismo concepto sin una regla clara.

## Mantener trazabilidad

Todo dato nutricional debe poder responder:

~~~txt
¿De qué fuente viene?
¿Qué versión?
¿Qué fecha?
¿Qué alimento externo?
¿Qué payload original?
~~~

---

# Rol futuro de la IA

## IA como asistente

La IA puede:

- proponer;
- explicar;
- rankear;
- detectar inconsistencias;
- sugerir aliases;
- sugerir categorías;
- sugerir nombres visibles.

## Humano como validador

El humano aprueba:

- fusiones;
- creación de conceptos importantes;
- cambios de nombre oficiales;
- resolución de conflictos entre fuentes.

## Reglas como protección

Las reglas determinísticas bloquean decisiones peligrosas aunque la IA sugiera algo.

Ejemplo:

~~~txt
Si uno es raw y otro cooked:
no auto-merge.
~~~

---

# Métricas de calidad del sistema

Medir:

- alimentos sin concepto;
- source items sin match;
- propuestas pendientes;
- propuestas aprobadas;
- propuestas rechazadas;
- duplicados detectados;
- conceptos con múltiples fuentes;
- conceptos sin nombre español;
- conceptos sin aliases;
- conflictos nutricionales entre fuentes;
- alimentos buscados sin resultado en picker.

---

# Roadmap resumido

## Macro 1 — Concept layer MVP

~~~txt
FoodConcept
FoodSourceItem
Migración USDA actual
Tests
Documentación
~~~

## Macro 2 — Matching MVP

~~~txt
Normalización semántica
Matching determinístico
Risk flags
Candidate scoring
~~~

## Macro 3 — Proposal queue

~~~txt
FoodCurationProposal
Approval workflow
Apply/reject commands
Tests
~~~

## Macro 4 — AI-assisted curation

~~~txt
Tool contract
Prompt/schema
Proposal generation
No auto-apply
Human approval
~~~

## Macro 5 — Admin review UI

~~~txt
Proposal list
Comparison view
Approve/reject actions
Bulk safe actions
~~~

## Macro 6 — Second source pilot

~~~txt
USDA SR Legacy or CIQUAL
Reader
Dry-run
Matching
Proposals
Review
Picker validation
~~~

---

# Recomendación de implementación

No comenzar importando una nueva fuente.

Primero construir:

~~~txt
FoodConcept + FoodSourceItem + FoodCurationProposal
~~~

Luego usar la segunda fuente como prueba real del sistema.

Esto evita crecer con duplicados y convierte la base de alimentos en un activo curado de My Scoope.