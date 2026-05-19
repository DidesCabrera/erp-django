# USDA Foundation Foods import process

Este documento describe el proceso operativo para importar y validar USDA Foundation Foods en My Scoope.

## Objetivo

Enriquecer la base global de alimentos usando USDA FoodData Central Foundation Foods como fuente pública inicial, manteniendo trazabilidad, control de calidad, aliases en español y validación del picker.

## Fuente

- Fuente: USDA FoodData Central
- Dataset: Foundation Foods
- Formato usado: JSON descargable
- Versión actual importada: 2026-04
- Archivo local usado:

~~~txt
data/food_sources/usda/foundation_foods_2026_04.json
~~~

El archivo local no necesita conservar el nombre original descargado desde USDA. Se renombra internamente para reflejar la versión del dataset.

## Flujo operativo

### 1. Descargar dataset

Descargar el archivo JSON de Foundation Foods desde USDA FoodData Central.

Guardar el archivo en:

~~~bash
mkdir -p data/food_sources/usda
~~~

Ejemplo de nombre interno:

~~~txt
data/food_sources/usda/foundation_foods_2026_04.json
~~~

### 2. Ejecutar dry-run

Antes de importar, siempre ejecutar:

~~~bash
python manage.py dry_run_usda_foods_json \
  data/food_sources/usda/foundation_foods_2026_04.json \
  --source-version 2026-04 \
  --source-dataset foundation_foods \
  --show-samples \
  --sample-size 10
~~~

El dry-run no escribe en base de datos.

Debe reportar:

- `total`
- `valid`
- `invalid`
- `duplicates`
- `failed`
- `would_import`
- `would_skip`
- `visibility_extended`
- `visibility_hidden`
- `reasons`
- `samples`, si se usa `--show-samples`

### 3. Ejecutar import real controlado

Si el dry-run es correcto:

~~~bash
python manage.py import_usda_foods_json \
  data/food_sources/usda/foundation_foods_2026_04.json \
  --source-version 2026-04 \
  --source-dataset foundation_foods \
  --notes "USDA Foundation Foods 2026-04 controlled import"
~~~

El import crea alimentos globales y metadata USDA.

### 4. Validar idempotencia

Después del import, volver a correr dry-run:

~~~bash
python manage.py dry_run_usda_foods_json \
  data/food_sources/usda/foundation_foods_2026_04.json \
  --source-version 2026-04 \
  --source-dataset foundation_foods
~~~

Resultado esperado:

~~~txt
would_import=0
~~~

Los alimentos ya importados deben aparecer como:

~~~txt
already_imported
~~~

### 5. Aplicar core seed y aliases

~~~bash
python manage.py apply_core_food_seed
python manage.py apply_usda_spanish_aliases
~~~

Esto promueve alimentos globales conocidos a `core` y agrega aliases/nombres localizados en español.

### 6. Validar conteos

~~~bash
python manage.py shell -c '
from notas.domain.models import Food, FoodAlias, FoodLocalizedName, FoodSourceMetadata

print("Global foods:", Food.objects.filter(is_global=True).count())
print("Core foods:", Food.objects.filter(is_global=True, visibility=Food.VISIBILITY_CORE).count())
print("Extended foods:", Food.objects.filter(is_global=True, visibility=Food.VISIBILITY_EXTENDED).count())
print("Hidden foods:", Food.objects.filter(is_global=True, visibility=Food.VISIBILITY_HIDDEN).count())
print("USDA metadata:", FoodSourceMetadata.objects.filter(source=FoodSourceMetadata.SOURCE_USDA).count())
print("Aliases:", FoodAlias.objects.count())
print("Localized names:", FoodLocalizedName.objects.count())
'
~~~

Para la versión 2026-04, el resultado validado fue:

~~~txt
Global foods: 365
Core foods: 8
Extended foods: 357
Hidden foods: 0
USDA metadata: 365
Aliases: 26
Localized names: 8
~~~

### 7. Validar picker

Correr tests relacionados:

~~~bash
python manage.py test \
  notas.tests.test_food_picker_queries \
  notas.tests.test_dpm_food_picker_builder \
  notas.tests.test_picker_payloads \
  notas.tests.test_dpm_food_picker_payloads
~~~

Validar manualmente en la UI búsquedas como:

~~~txt
avena
pollo
huevo
arroz
arroz integral
almendra
kale
hummus
oats
chicken
egg
rice
almonds
~~~

## Resultado validado para Foundation Foods 2026-04

Archivo procesado:

~~~txt
data/food_sources/usda/foundation_foods_2026_04.json
~~~

Dry-run final posterior al import:

~~~txt
total=395
valid=363
invalid=0
duplicates=363
failed=32
would_import=0
would_skip=395
reasons:
- already_imported: 363
- mapping_failed: 32
~~~

Los `mapping_failed` observados corresponden a entradas `null` dentro del array `FoundationFoods`.

## Decisiones técnicas

### Uso de archivo descargable

Para carga inicial masiva se usa archivo JSON local descargado desde USDA, no API.

Razones:

- permite dry-run completo;
- evita rate limits;
- permite auditoría por versión;
- hace la carga reproducible;
- permite import controlado;
- desacopla el picker de servicios externos.

La API USDA queda como opción futura para enriquecimiento puntual o actualización selectiva por `fdcId`.

### Negative carbs USDA

Algunos alimentos animales venían con carbohidratos negativos desde USDA.

Decisión:

- normalizar carbohidratos negativos USDA a `0`;
- mantener validación estricta para otros macros;
- corregir en el mapper USDA, no en la validación general.

### Visibilidad

Los alimentos importados desde USDA entran como globales y se clasifican inicialmente según calidad.

Los alimentos base conocidos se promueven posteriormente a:

~~~txt
core
~~~

mediante:

~~~bash
python manage.py apply_core_food_seed
~~~

## Alimentos core iniciales

Para 2026-04 quedaron como `core`:

~~~txt
Oats, raw
Chicken breast, cooked
Eggs, Grade A, Large, egg whole
Rice, white, long grain, unenriched, raw
Rice, brown, long grain, unenriched, raw
Nuts, almonds, whole, raw
Kale, raw
Hummus, commercial
~~~

## Aliases principales en español

Ejemplos:

~~~txt
Avena
Pechuga de pollo
Pollo
Huevo
Huevos
Arroz
Arroz blanco
Arroz integral
Almendra
Almendras
Kale
Col rizada
Hummus
Humus
~~~

## Tests recomendados para esta macrofase

~~~bash
python manage.py test \
  notas.tests.test_usda_foundation_foods_reader \
  notas.tests.test_dry_run_usda_foods_json_command \
  notas.tests.test_usda_food_payload_import_command \
  notas.tests.test_import_usda_foods_json_command \
  notas.tests.test_usda_food_mapper \
  notas.tests.test_core_food_seed_catalog \
  notas.tests.test_core_food_seed_service \
  notas.tests.test_apply_core_food_seed_command \
  notas.tests.test_food_picker_queries \
  notas.tests.test_dpm_food_picker_builder \
  notas.tests.test_picker_payloads \
  notas.tests.test_dpm_food_picker_payloads
~~~

## Checklist para futuras versiones USDA

1. Descargar nuevo JSON Foundation Foods.
2. Guardarlo como `data/food_sources/usda/foundation_foods_YYYY_MM.json`.
3. Ejecutar dry-run con `--show-samples`.
4. Revisar `invalid`, `failed`, `would_import`.
5. Ejecutar import real si el dry-run es aceptable.
6. Repetir dry-run para confirmar `would_import=0`.
7. Ejecutar core seed y aliases.
8. Validar conteos.
9. Validar picker.
10. Hacer commit del código si hubo cambios de import/seed/docs.