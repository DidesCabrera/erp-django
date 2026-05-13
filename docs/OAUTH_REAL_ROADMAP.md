# My Scoope OAuth Real Roadmap

Este documento define el diseño para implementar OAuth real sobre la base ya validada de `MCPUserToken`.

## Objetivo de producto

Permitir que un usuario conecte su cuenta de My Scoope desde ChatGPT y autorice a ChatGPT a crear propuestas de dieta en su cuenta.

Flujo objetivo:

```text
Usuario abre ChatGPT
→ conecta My Scoope
→ inicia sesión en My Scoope
→ autoriza scopes
→ ChatGPT recibe access token
→ ChatGPT llama al MCP remoto
→ MCP/Django resuelven usuario real
→ NutritionProposal queda pending_review en la cuenta del usuario
```

La IA no debe aplicar cambios finales directamente.

---

## Estado actual

Ya existe un modo puente funcional:

```text
Cliente MCP
→ Authorization: Bearer mcp_user_xxx
→ MCP remoto
→ Django API Adapter
→ MCPUserToken
→ usuario real
```

Este flujo ya valida:

```text
- token por usuario;
- scopes;
- ownership;
- tools seguras;
- proposals creadas por usuario real;
- modo legacy todavía funcional.
```

OAuth real debe construir encima de esto, no reemplazarlo desde cero.

---

## Principio de seguridad

La regla principal se mantiene:

```text
ChatGPT propone.
My Scoope valida.
El usuario revisa.
El usuario aprueba/aplica.
```

Por lo tanto, los access tokens OAuth iniciales solo deben permitir:

```text
myscoope:read
myscoope:proposals:create
```

No deben permitir:

```text
apply_proposal
delete_dailyplan
update_dailyplan
raw_sql
raw_model_mutation
```

---

## OAuth mental model

En el flujo final:

```text
ChatGPT = OAuth client
My Scoope = Authorization Server
My Scoope MCP/Django API = Resource Server
MCPUserToken = access token storage / validation base
```

ChatGPT solicita autorización.

My Scoope autentica al usuario y pide consentimiento.

My Scoope emite un authorization code.

ChatGPT intercambia el authorization code por access token.

ChatGPT usa ese access token como Bearer token contra el MCP remoto.

---

## Flujo OAuth esperado

```text
1. ChatGPT detecta que My Scoope requiere auth.
2. ChatGPT inicia flujo OAuth.
3. Usuario es redirigido a My Scoope /oauth/authorize.
4. My Scoope verifica login del usuario.
5. My Scoope muestra consentimiento:
   - Leer información nutricional.
   - Crear propuestas de dieta.
6. Usuario aprueba.
7. My Scoope emite authorization code.
8. ChatGPT envía el code al token endpoint.
9. My Scoope valida code + PKCE.
10. My Scoope emite access token.
11. ChatGPT llama MCP con:
    Authorization: Bearer <access_token>
12. MCP reenvía token a Django.
13. Django resuelve usuario real.
14. Tools operan sobre ese usuario.
```

---

## Redirect URI de ChatGPT

Para Apps/Connectors de ChatGPT, OpenAI indica que ChatGPT completa el flujo OAuth redirigiendo a una URL de esta forma:

```text
https://chatgpt.com/connector/oauth/{callback_id}
```

Esa redirect URI se obtiene desde la configuración de la app/conector y debe agregarse como redirect URI permitida en My Scoope.

En desarrollo, puede existir una redirect URI distinta. No se deben aceptar redirects arbitrarios.

---

## Scopes iniciales

### `myscoope:read`

Permite:

```text
list_food_catalog
read_dailyplan
read_proposal
list_user_proposals
compare_dailyplan_to_targets
```

### `myscoope:proposals:create`

Permite:

```text
create_validated_meal_proposal
create_validated_dailyplan_proposal
create_validated_dailyplan_build_proposal
```

### Scopes no incluidos inicialmente

```text
myscoope:proposals:apply
myscoope:dailyplans:update
myscoope:foods:write
myscoope:admin
```

---

## Endpoints OAuth necesarios

### Discovery / metadata

```text
GET /.well-known/oauth-authorization-server
```

Debe describir:

```text
issuer
authorization_endpoint
token_endpoint
registration_endpoint si se implementa DCR
scopes_supported
response_types_supported
grant_types_supported
code_challenge_methods_supported
```

---

### Authorization endpoint

```text
GET /oauth/authorize
```

Responsabilidades:

```text
- recibir client_id;
- recibir redirect_uri;
- recibir response_type=code;
- recibir scope;
- recibir state;
- recibir code_challenge;
- recibir code_challenge_method=S256;
- verificar usuario logueado;
- mostrar consentimiento;
- emitir authorization code temporal;
- redirigir a redirect_uri con code y state.
```

---

### Consent endpoint

Puede ser parte de `/oauth/authorize` o una pantalla intermedia.

Debe mostrar:

```text
ChatGPT quiere conectarse a My Scoope con permisos:
- Leer datos necesarios para construir dietas.
- Crear propuestas de dieta pendientes de revisión.
```

No debe mencionar permisos no concedidos.

---

### Token endpoint

```text
POST /oauth/token
```

Responsabilidades:

```text
- recibir grant_type=authorization_code;
- recibir code;
- recibir redirect_uri;
- recibir client_id;
- recibir code_verifier;
- validar PKCE;
- validar que el code no expiró;
- validar que el code no fue usado;
- crear access token asociado al usuario;
- devolver token response.
```

Respuesta esperada:

```json
{
  "access_token": "mcp_user_xxx",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "myscoope:read myscoope:proposals:create"
}
```

---

### Revocation endpoint

Opcional al inicio, recomendado después:

```text
POST /oauth/revoke
```

Responsabilidades:

```text
- revocar access token;
- dejar revoked_at;
- dejar is_active=False.
```

---

## Modelos propuestos

### OAuthClient

Representa un cliente autorizado, por ejemplo ChatGPT.

Campos sugeridos:

```text
client_id
client_name
redirect_uris
allowed_scopes
is_active
created_at
updated_at
```

Para MVP privado, puede existir un cliente único para ChatGPT.

Más adelante se puede evaluar Dynamic Client Registration.

---

### OAuthAuthorizationCode

Representa un code temporal.

Campos sugeridos:

```text
client
user
code_hash
redirect_uri
scopes
code_challenge
code_challenge_method
expires_at
used_at
created_at
```

Reglas:

```text
- expira rápido, por ejemplo 5 minutos;
- se usa una sola vez;
- se guarda como hash;
- está asociado a user + client + redirect_uri + scopes.
```

---

### Access token

Para el access token podemos reutilizar:

```text
MCPUserToken
```

OAuth puede crear un `MCPUserToken` con:

```text
user = usuario autenticado
name = "ChatGPT OAuth access token"
scopes = scopes aprobados
expires_at = now + duración configurada
```

Así reutilizamos toda la validación ya implementada:

```text
Bearer token
→ hash
→ MCPUserToken
→ user
→ scopes
→ ownership
```

---

## PKCE

El token endpoint debe validar PKCE.

Para `S256`:

```text
BASE64URL(SHA256(code_verifier)) == code_challenge
```

Solo deberíamos aceptar:

```text
code_challenge_method=S256
```

No aceptar `plain` salvo necesidad explícita de compatibilidad.

---

## Duración de tokens

Valores iniciales recomendados:

```text
authorization code: 5 minutos
access token: 1 hora o 24 horas para MVP privado
```

Para producto final, evaluar:

```text
refresh tokens
revocación
rotación
duraciones más cortas
```

Para MVP inicial, podemos evitar refresh tokens y permitir reconexión.

---

## Client registration

Hay dos caminos:

### Camino A — Cliente estático

Crear manualmente un `OAuthClient` para ChatGPT.

Ventajas:

```text
- más simple;
- más controlado;
- suficiente para MVP privado.
```

Desventajas:

```text
- menos estándar si ChatGPT exige Dynamic Client Registration.
```

---

### Camino B — Dynamic Client Registration

Implementar:

```text
POST /oauth/register
```

Ventajas:

```text
- más compatible con clientes OAuth modernos;
- mejor camino para apps/conectores.
```

Desventajas:

```text
- más trabajo;
- más superficie de seguridad.
```

---

## Recomendación para My Scoope

Implementar primero:

```text
OAuth privado con cliente estático
```

Y dejar preparado el diseño para DCR si ChatGPT/App lo exige.

Orden recomendado:

```text
1. OAuthClient estático.
2. AuthorizationCode + PKCE.
3. Token endpoint que emite MCPUserToken.
4. Metadata endpoint.
5. Probar con cliente manual.
6. Luego probar con ChatGPT App/Connector.
7. Si ChatGPT requiere DCR, agregar registration endpoint.
```

---

## Relación con MCP

El MCP ya está preparado para:

```text
Authorization: Bearer mcp_user_xxx
```

Por lo tanto, OAuth no debería requerir cambiar las tools.

OAuth solo debe resolver cómo ChatGPT obtiene ese token.

Flujo final:

```text
OAuth emite mcp_user_xxx
→ ChatGPT lo usa contra MCP
→ MCP lo acepta
→ MCP lo reenvía a Django
→ Django resuelve usuario
```

---

## Tests mínimos esperados

### Metadata

```text
GET /.well-known/oauth-authorization-server
→ 200
→ contiene authorization_endpoint
→ contiene token_endpoint
→ contiene scopes_supported
```

### Authorization requiere login

```text
GET /oauth/authorize sin sesión
→ redirige a login
```

### Authorization con usuario logueado

```text
GET /oauth/authorize con sesión
→ muestra consentimiento
```

### Consent aprobado

```text
POST consentimiento
→ genera authorization code
→ redirige a redirect_uri con code y state
```

### Token endpoint

```text
POST /oauth/token con code válido + PKCE válido
→ 200
→ access_token empieza con mcp_user_
→ token_type Bearer
```

### Code usado dos veces

```text
POST /oauth/token dos veces con el mismo code
→ segunda vez falla
```

### PKCE inválido

```text
POST /oauth/token con code_verifier incorrecto
→ falla
```

### Scope no permitido

```text
/oauth/authorize con scope no permitido
→ falla
```

### Access token funciona en MCP

```text
access_token OAuth
→ MCP list_user_proposals
→ ok:true
```

---

## Seguridad mínima

```text
- No guardar raw authorization code.
- No guardar raw access token.
- Validar redirect_uri contra allowlist.
- Validar state devolviéndolo intacto.
- Validar PKCE S256.
- Expirar authorization codes.
- Evitar reutilización de code.
- Restringir scopes.
- Mantener apply_proposal fuera del MCP.
- Mostrar consentimiento claro.
```

---

## Decisiones abiertas

```text
1. ¿OAuthClient estático o Dynamic Client Registration desde el inicio?
2. ¿Access token dura 1 hora, 24 horas o más?
3. ¿Habrá refresh token en el MVP?
4. ¿Dónde se administran/revocan conexiones ChatGPT en la UI de My Scoope?
5. ¿Qué redirect URI exacta entrega ChatGPT Developer Mode?
```

---

## Decisión recomendada para el siguiente bloque

Para avanzar rápido y seguro:

```text
6.2 — Implementar modelos OAuth mínimos:
- OAuthClient
- OAuthAuthorizationCode

Sin implementar todavía endpoints.
```

Luego:

```text
6.3 — Metadata + authorize endpoint
6.4 — Token endpoint + PKCE
6.5 — Prueba manual OAuth
6.6 — Prueba con ChatGPT/App
```

---

## Criterio de cierre de 6.1

Este diseño se considera cerrado cuando:

```text
- Está definido el flujo OAuth objetivo.
- Está definido que OAuth emitirá MCPUserToken.
- Están definidos scopes iniciales.
- Están definidos endpoints mínimos.
- Está definido el modelo OAuthClient.
- Está definido el modelo OAuthAuthorizationCode.
- Está definido el uso de PKCE S256.
- Está definido el set mínimo de tests.
```