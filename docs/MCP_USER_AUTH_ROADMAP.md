# My Scoope MCP User Auth Roadmap

Este documento define el roadmap para pasar desde autenticación MCP con usuario fijo a autenticación por usuario real, preparando el camino para OAuth y ChatGPT Apps/Connectors.

## Objetivo de producto

La visión de producto es:

```text
Un usuario abre ChatGPT,
conecta su cuenta de My Scoope,
pide una dieta según sus objetivos,
y ChatGPT deja una propuesta de dieta en su cuenta de My Scoope.
```

La propuesta debe quedar como `pending_review`.

La IA no debe aplicar cambios finales directamente.

---

## Estado actual

Actualmente el flujo MCP remoto funciona así:

```text
OpenAI / Cliente MCP
        ↓
My Scoope MCP Server
        ↓
Django API Adapter
        ↓
MYSCOOPE_INTERNAL_API_USERNAME
        ↓
Usuario fijo
```

Esto permitió validar:

```text
- MCP remoto en Render.
- Auth externa IA → MCP.
- Auth interna MCP → Django.
- OpenAI usando MCP remoto.
- Creación de NutritionProposal real.
- Creación de DailyPlan build proposal con comidas y alimentos.
- Revisión/aprobación/aplicación humana en My Scoope.
```

Pero tiene una limitación importante:

```text
Todas las requests MCP se ejecutan como el usuario configurado por entorno.
```

Eso sirve para demo y validación técnica, pero no para producto multiusuario.

---

## Problema a resolver

Para producto real necesitamos:

```text
Usuario A en ChatGPT → proposal en cuenta de Usuario A.
Usuario B en ChatGPT → proposal en cuenta de Usuario B.
```

Por lo tanto, el sistema debe resolver:

```text
Bearer token recibido
→ usuario real
→ scopes/permisos
→ tools permitidas
→ ownership correcto
```

---

## Principio de seguridad

La regla principal no cambia:

```text
La IA puede leer, validar y crear propuestas.
La IA no puede aplicar cambios finales directamente.
El usuario humano revisa, aprueba y aplica desde My Scoope.
```

Por lo tanto, la primera versión de auth por usuario debe permitir:

```text
- Leer datos necesarios del usuario.
- Leer catálogo de alimentos globales y alimentos propios.
- Crear NutritionProposals.
- Leer NutritionProposals del usuario.
```

Y debe bloquear:

```text
- Aplicar propuestas automáticamente.
- Modificar DailyPlans directamente.
- Borrar datos.
- Leer datos de otro usuario.
- Usar foods privados de otro usuario.
```

---

## Scopes iniciales

Scopes recomendados para la primera versión:

```text
myscoope:read
myscoope:proposals:create
```

### `myscoope:read`

Permite:

```text
- read_dailyplan
- read_proposal
- list_user_proposals
- list_food_catalog
- compare_dailyplan_to_targets
```

### `myscoope:proposals:create`

Permite:

```text
- create_validated_meal_proposal
- create_validated_dailyplan_proposal
- create_validated_dailyplan_build_proposal
```

### Scopes que no se agregarán todavía

```text
myscoope:proposals:apply
myscoope:dailyplans:update
myscoope:foods:write
myscoope:admin
```

Estos scopes quedan fuera porque la IA no debe aplicar cambios finales directamente en la primera versión.

---

## Flujo objetivo final con OAuth

El flujo final esperado es:

```text
1. Usuario abre ChatGPT.
2. Usuario conecta My Scoope.
3. ChatGPT redirige al usuario a My Scoope para login/consentimiento.
4. My Scoope autentica al usuario.
5. My Scoope emite authorization code.
6. ChatGPT intercambia el code por access token usando PKCE.
7. ChatGPT llama al MCP remoto con:
   Authorization: Bearer <access_token>
8. MCP valida el token o delega validación en Django.
9. Django resuelve el usuario real.
10. Las tools operan sobre datos de ese usuario.
11. La proposal queda pending_review en la cuenta correcta.
```

---

## Flujo intermedio recomendado

Antes de implementar OAuth completo, se recomienda implementar una etapa intermedia:

```text
Bearer user token
→ Django resuelve usuario
→ MCP opera como ese usuario
```

Esto permite validar primero la parte crítica:

```text
¿My Scoope puede ejecutar tools MCP en nombre de usuarios distintos?
```

Luego OAuth se encargará de emitir esos tokens mediante login/consentimiento.

---

## Por qué usar token por usuario como puente

OAuth tiene dos problemas separados:

```text
A. Resolver usuario desde un token.
B. Entregar ese token mediante login, consentimiento, callback y PKCE.
```

El puente por token de usuario permite implementar primero el problema A.

Esto reduce riesgo porque permite probar:

```text
token_usuario_a → proposal de Usuario A
token_usuario_b → proposal de Usuario B
token inválido → 401
token sin scope → 403
```

sin depender todavía de ChatGPT Developer Mode, redirect URIs, OAuth callbacks ni PKCE.

---

## Modelo propuesto: MCPUserToken

Modelo conceptual:

```python
class MCPUserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    token_hash = models.CharField(max_length=128, unique=True)
    scopes = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

Reglas:

```text
- El token real solo se muestra una vez al crearlo.
- En base de datos solo se guarda token_hash.
- El token puede revocarse.
- El token puede expirar.
- El token contiene scopes.
- Cada token pertenece a un usuario real.
```

---

## Formato de token

Formato sugerido:

```text
mcp_user_<random_secret>
```

Ejemplo conceptual:

```text
mcp_user_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

El valor completo nunca debe guardarse en texto plano.

---

## Hash del token

El token debe guardarse como hash usando una función estable.

Ejemplo conceptual:

```python
import hashlib

token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
```

Validación:

```text
1. Recibir raw bearer token.
2. Calcular SHA256.
3. Buscar MCPUserToken.token_hash.
4. Verificar is_active.
5. Verificar expires_at.
6. Verificar revoked_at.
7. Verificar scopes.
8. Resolver user.
```

---

## Cambios esperados en Django API Adapter

Hoy la API interna se valida conceptualmente con:

```text
MYSCOOPE_INTERNAL_API_TOKEN
MYSCOOPE_INTERNAL_API_USERNAME
```

La nueva versión debe soportar dos modos durante transición:

```text
Modo legacy:
- Token interno global + username por entorno.

Modo user token:
- Bearer token dinámico → usuario real.
```

Durante la transición, ambos pueden coexistir.

Pero el objetivo final es que MCP/ChatGPT use el modo user token.

---

## Resolución de usuario

La nueva función de resolución debería hacer algo como:

```text
Authorization header
        ↓
Bearer token
        ↓
¿es token de usuario?
        ↓
sí → resolver user desde MCPUserToken
        ↓
no → intentar modo legacy interno
        ↓
si falla → 401
```

---

## Mapeo de scopes por tool

| Tool | Scopes requeridos |
|---|---|
| list_food_catalog | myscoope:read |
| read_dailyplan | myscoope:read |
| read_proposal | myscoope:read |
| list_user_proposals | myscoope:read |
| compare_dailyplan_to_targets | myscoope:read |
| create_validated_meal_proposal | myscoope:proposals:create |
| create_validated_dailyplan_proposal | myscoope:proposals:create |
| create_validated_dailyplan_build_proposal | myscoope:proposals:create |

No agregar en esta etapa:

| Tool futura | Estado |
|---|---|
| apply_proposal | No expuesta a IA |
| delete_dailyplan | No expuesta a IA |
| raw_sql | Prohibida |
| update_dailyplan | Prohibida |
| update_food | Prohibida |

---

## Cambios esperados en MCP Server

Actualmente el MCP server usa:

```text
MYSCOOPE_API_AUTH_TOKEN
```

para llamar a Django.

Con auth por usuario, el MCP debe recibir el bearer token del cliente y usarlo para llamar al API Adapter.

Flujo objetivo:

```text
Cliente MCP / ChatGPT
        ↓
Authorization: Bearer <user_token>
        ↓
MCP Server
        ↓
Django API Adapter
Authorization: Bearer <user_token>
        ↓
Django resuelve usuario real
```

Durante transición puede seguir existiendo:

```text
MYSCOOPE_API_AUTH_TOKEN
```

para smoke tests técnicos y entorno dev.

Pero para producto real, las requests de usuario deben llevar token dinámico.

---

## Reglas de ownership

La resolución de usuario debe integrarse con las fronteras existentes:

```text
- read_dailyplan solo puede leer DailyPlans disponibles para el usuario.
- read_proposal solo puede leer proposals del usuario.
- list_user_proposals solo lista proposals del usuario.
- list_food_catalog lista:
  - foods globales;
  - foods propios del usuario;
  - no lista foods privados de otros usuarios.
- create proposal crea la proposal con created_by=user.
```

---

## Tests mínimos esperados

### Token válido

```text
Dado token de Usuario A
Cuando llama list_user_proposals
Entonces solo ve proposals de Usuario A.
```

### Token inválido

```text
Dado bearer token inexistente
Cuando llama cualquier tool
Entonces recibe 401.
```

### Token revocado

```text
Dado token revocado
Cuando llama cualquier tool
Entonces recibe 401.
```

### Token sin scope read

```text
Dado token sin myscoope:read
Cuando llama read_dailyplan
Entonces recibe 403.
```

### Token sin scope create

```text
Dado token solo con myscoope:read
Cuando llama create_validated_dailyplan_build_proposal
Entonces recibe 403.
```

### Ownership de proposals

```text
Usuario A no puede leer proposal de Usuario B.
```

### Ownership de foods

```text
Usuario A puede usar food global.
Usuario A puede usar food propio.
Usuario A no puede usar food privado de Usuario B.
```

---

## Estado final de esta etapa

La etapa 5.1 se considera cerrada cuando:

```text
- Está definido el flujo actual.
- Está definido el flujo objetivo.
- Están definidos los scopes iniciales.
- Está definido el modelo MCPUserToken.
- Está definido cómo Django resolverá usuario desde bearer token.
- Está definido cómo MCP reenviará token dinámico.
- Está definido el set mínimo de tests.
```

---

## Etapas siguientes

### 5.2 — Implementar MCPUserToken

Objetivo:

```text
Crear modelo, migración, servicios de generación/validación y tests.
```

### 5.3 — Resolver usuario desde token en API Adapter

Objetivo:

```text
Cambiar la autenticación interna para resolver user dinámico desde bearer token.
```

### 5.4 — Reenviar token dinámico desde MCP

Objetivo:

```text
MCP debe llamar a Django usando el bearer token recibido del cliente.
```

### 5.5 — Preparar OAuth real

Objetivo:

```text
Implementar authorization/token endpoints o integrar proveedor OAuth externo.
```

---

## Decisión estratégica

La ruta recomendada es:

```text
1. Mantener el modo legacy funcionando.
2. Agregar token por usuario.
3. Probar multiusuario con tokens manuales.
4. Cambiar MCP para usar token dinámico.
5. Luego implementar OAuth para que ChatGPT obtenga tokens automáticamente.
```

Esto evita mezclar demasiados problemas en una sola etapa.

---

## Regla final

La autenticación por usuario no debe debilitar la frontera de seguridad actual.

Aunque el usuario autorice ChatGPT:

```text
ChatGPT puede proponer.
My Scoope valida.
El usuario aprueba.
My Scoope aplica.
```