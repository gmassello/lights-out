# Lights-out — plan y setup propio

> Movido desde `docs/HACKATHON.md` (secciones 12–14) el 26 sep 2026, cuando ese archivo pasó a ser el brief del evento en inglés.

## Setup propio de Lights-out

**Modelos y cupo**
- Todos los seats en **Claude Code con la suscripción Max**: no hay costo por token, pero los seats en paralelo comparten el cupo de uso.
- Mezcla de modelos para estirar el cupo: el modelo más fuerte en el seat que construye y modelos más livianos en los que revisan o testean. Declarar el ID exacto en cada mandate.
- Plan B: un seat en **OpenCode + key paga de Gemini** como revisor. Descarga cupo de Max y da diversidad real entre seats. Evitar el plan gratuito de Gemini en la corrida final, porque sus límites de requests pueden trabar un seat sin posibilidad de intervenir.
- Plan C: un seat en **OpenCode + Featherless** como revisor, con los US$25 de créditos del evento (primeros 1.000 inscriptos, promo por mail; el alta pide tarjeta, cancelar antes del próximo ciclo). Modelos documentados en la guía: MiniMax-M2.5, Kimi-K2.5, DeepSeek-V3.2. Config en `~/.config/opencode/opencode.json`, nunca en el repo; `turn_timeout_s=900`; no corre en Docker Sandbox. Probarlo en el toy: si el seat no arranca, pasarlo a Claude Code sin depurar el runtime.

**Costo**
- Medir con el track **toy** cuánto consume una corrida completa de 4 etapas antes de ir al track real.
- Lanzar la corrida final **al inicio de una ventana de uso limpia**.
- Reportar el costo en `FACTORY.md` como tiempo y tokens, que Claude Code muestra por sesión.

**Mandates:** genéricos, reusables para otro problema. Nada del track: ni endpoints, ni campos, ni dominio.

---

## Features de BAND a usar

Relevado de las 190 páginas de https://docs.band.ai (índice `llms.txt`) el 26 sep 2026. La página de Desktop es corta: no documenta subcomandos del CLI `band`, las tools del plugin `band-peer` ni el formato de `room.json`. Casi todo lo operable está en la API REST y el SDK. MCP de las docs para los seats: `https://docs.band.ai/_mcp/server`.

### Qué usamos y para qué criterio

| Feature | Cómo | Para qué (criterio) | Fuente |
|---|---|---|---|
| Plugin `band-peer` en Claude Code | Se instala desde Desktop; después `/reload-plugins` o reiniciar Claude Code | Cada ventana de Claude Code es un seat (compuerta 1) | `/band-desktop` |
| Onboarding `/jam` | En Claude Code: `/jam` + "Start a Band Desktop session as the architect…"; el architect crea el room e invita | Arranque genérico de seats, citable en `FACTORY.md` (Factory: reusable) | `/band-desktop` |
| Sesión "bound" | Verificar que los 3+ seats estén *bound* (no *parked*) antes del dispatch | Evita handoffs a un seat ausente (autonomía) | `/band-desktop` |
| Reattach | "Reattach this session to the existing architect peer." | Reiniciar un seat caído sin perder identidad (Factory: recuperación) | `/band-desktop` |
| Ruteo por `@mention` | Solo el mencionado recibe; varios `@` despiertan a varios | Handoffs trazables (compuerta 2, Teamwork) | `/core-concepts/chat-rooms` |
| `band_send_message` obligatorio | El texto plano del modelo es "internal thought", invisible | Regla dura en todo mandate: sin la tool no hay handoff | `/core-concepts/agents` |
| Handoff autocontenido | Un agente no ve mensajes dirigidos a otros | Cada handoff lleva tarea + spec completas (lo exige también la guía) | `/core-concepts/chat-rooms` |
| Descripción del seat en el roster | El roster inyectado incluye la descripción | Ruteo por rol; nombres de rol, nunca "Agent"/"Bot" | changelog SDK 23-ago |
| Participantes dinámicos | `band_add_participant`, `band_get_participants`, `band_lookup_peers` | El coordinador suma a todos los seats antes del primer handoff | `/core-concepts/agents` |
| Task board del room (**Beta**) | REST `POST /api/v1/agent/chats/{id}/tasks` (`subject`, `detail`); update con `status` `pending → in_progress → in_review → completed/failed`, `comment`, `linked_native_id` | Reparto visible con `#N`; `in_review → in_progress` con comentario = review que cambió el resultado; `linked_native_id` = SHA del commit (Teamwork: código trazable) | `/api/agent-api/agent-api-chat-tasks` |
| Historial de tasks | `GET .../tasks/{id}/history`, append-only con actor y `from → to` | Evidencia de reviews y reintentos | idem |
| Goal del room | `PUT .../board` con `goal_title`, `goal_summary` | El coordinador fija la misión de la etapa | idem |
| Evento `attention` tipo `assumption` | REST `POST /api/v1/agent/chats/{id}/events`, `metadata.kind=assumption`, no bloqueante | Registrar decisiones en vez de preguntarle al humano (autonomía) | `/api/agent-api` |
| Renombrar room | tool `set_chat_title` | Nombrar el room por corrida | `/core-concepts/agents` |
| Filtros de tools por seat | `include_tools`, `exclude_tools`, `include_categories` | Menos superficie por rol (reviewer sin crear rooms) | `/integrations/sdks/overview` |
| `Emit.USAGE` | Tokens por turno (input/output/cache) como eventos en el room | Costos medidos dentro del room (Factory: costos) | `/integrations/sdks/reference` |
| `Emit.TOOL_CALLS` / `THOUGHTS` | Tool calls y razonamiento en el timeline | Código trazable al room | idem |
| Estados de entrega | `delivered/processing/processed/failed` por destinatario, con intentos | Evidencia de fallas y reintentos | `/core-concepts/chat-rooms` |
| Indicador de actividad | Los adapters lo reportan solos; expira a ~10 s | Detectar un seat colgado | changelog SDK 22-jun |
| Context para rehidratar | `GET /api/v1/agent/chats/{id}/context` | Un seat reiniciado recupera lo suyo (recuperación) | `/api/agent-api` |
| Panel de Desktop | Board, swim lanes, usage, actividad | Tomas para el video (room + handoff) | `/band-desktop` |

### Alternativas y descartes

- **SDK headless (`ClaudeSDKAdapter`, `OpencodeAdapter`)**: para correr seats sin Desktop. Para autonomía: OpenCode con `approval_mode="auto_accept"` y `question_mode="auto_reject"` (por defecto ambos son `manual` y traban el seat). El runner Docker multi-agente (`agent_config.yaml` + `prompts/<role>.md`, ejemplo `examples/coding_agents/`) sirve de plantilla de fábrica genérica.
- **`band-mcp`**: crea rooms y manda mensajes, pero **no recibe**. No sirve como seat, sí para un script de soporte.
- **Memoria compartida** (`band_store_memory`…): requiere **Enterprise**. Descartada.
- **Archivos del room** (`Capability.FILES`): "not yet available on Band SaaS". Descartada; los artefactos van por Git.
- **Human API** (`/me/...`, historial completo por API): Enterprise. El `room.json` sale de la descarga manual de la console.
- **Contactos**, sandboxes Copilot/NemoClaw, adapters de otros frameworks: no aplican.

### Gotchas

1. Una conexión WS por Agent ID, gana la última: dos procesos con la misma identidad se desconectan en silencio.
2. Entrega *at-least-once*: un mensaje puede repetirse tras un crash, así que los efectos (commits) tienen que ser idempotentes.
3. Tasks/board son Beta y solo REST (sin tool de SDK/MCP): el seat las maneja con `curl` y necesita su agent key fuera del repo. Probar en el toy antes de meterlas en un mandate.
4. No figura si la descarga del room (Chat Export, tier **Pro** según changelog 9-jun) incluye tasks, board, usage o `attention`. Verificarlo en el `room.json` del toy; si no los incluye, el SHA también va en el mensaje.
5. Requieren humano: login de Desktop, instalar/recargar el plugin, API keys (se ven una sola vez), readiness "Recheck", interrupt/stop/play. Todo antes del dispatch.
6. OpenCode no chequea salud al arrancar: un puerto muerto aparece recién en el primer mensaje.
7. Claude SDK sin `ANTHROPIC_API_KEY` responde "Not logged in" en cada turno y parece sano.
8. Límites: `content` de eventos 16.384 caracteres (handoffs largos se parten en mensajes numerados), `metadata` 64 KB, 403 `limit_reached` por cuota de plan, 429 por rate limit.
9. Desktop no soporta Windows. Renombres: Jam → Band Desktop (el daemon sigue siendo `jamd`, estado en `~/.jam`).

---

## Diseño de la fábrica: ideas a adoptar

Relevado el 26 sep 2026. Se ordenan por esfuerzo; casi todo es texto en mandates o `FACTORY.md`. Nada de esto se copia como código: los mandates siguen genéricos y lo del track va en el brief.

### Esfuerzo bajo (mandates y FACTORY.md)

1. **Aceptación antes que código.** El reviewer escribe y commitea su diseño de aceptación (sección de la spec → casos) antes de leer la implementación. Sus checks salen de la spec, nunca del código ni de los tests del builder.
2. **Checklist de conformidad numerado `[C-nn]`.** Cada ítem atado a una sección de la spec y a un check. Veredicto por ítem: CONFORMS con `archivo:línea` o DEVIATES con esperado vs. actual. Un solo desvío rechaza el handoff. Las ambigüedades se marcan y van al coordinador.
3. **Evidencia de recuperación.** Tabla en `FACTORY.md`: hallazgo → quién lo encontró → SHA rechazado → SHA de la reparación. Cada rechazo se preserva en `evidence/stage-N/rejection-NN.md` con pasos, esperado, actual y pasaje de la spec. Los errores de tooling o de test se registran aparte y no cuentan como defectos del producto.
4. **Veredicto atado a SHA + tree hash.** Todo ACCEPT/REJECT cita `<sha>` y el tree hash de la carpeta (`git rev-parse HEAD:stage-N`). El reviewer verifica que los tree hash de las etapas anteriores no cambiaron.
5. **Release check.** Antes de aprobar una etapa: checkout limpio, build del contenedor, suites 1..N verdes y la suite N+1 **tiene que fallar**. Después se congela la carpeta.
6. **Diversidad de modelo como regla.** El verifier nunca corre el mismo modelo que el builder: dos instancias del mismo modelo se equivocan en lo mismo. Escrito como restricción en `FACTORY.md`, no como descripción.
7. **Grafo de ruteo restringido.** El builder no menciona al auditor ni al humano; solo el coordinador habla con el humano; nadie tiene camino hacia su propia aprobación. `FACTORY.md` suma la sección "qué se rompe sin el room".
8. **Ruteo por rol, no por handle.** Cada seat consulta los participantes y menciona al que tiene el rol destino (tabla emisor → condición → rol). Hace a los mandates re-armables con otros nombres.
9. **Espera acotada.** Si un seat no responde en 10 min, se registra "unanswered wait", se lo re-agrega al room y se reintenta una vez; nunca se auto-aprueba. Prohibido reclutar agentes ajenos a la banda. Un bloqueo real se registra como resultado de la etapa y se para, sin preguntar.
10. **"No reply requested".** Los mensajes de evidencia suplementaria lo dicen explícito para no disparar turnos inútiles (ahorra tokens).
11. **Veredicto en tres estados** (APPROVED / approved-with-follow-up / held-open-because-X) con barrido de riesgos obligatorio (cada uno: confirmed-safe con `archivo:línea`, tested, accepted u open). Los hallazgos equivocados se retractan en público.
12. **Ley de conservación.** Cuando el dominio tiene una cantidad que debe balancear, una aserción de invariante global es obligatoria al final de cada test de concurrencia; si falta, es blocker.
13. **Gate de regresión.** Conteo base de tests: si baja, hay que explicar qué se borró. El gate nunca se pipea por `tail`/`grep` (el exit code miente) y nombra el paso que falló. Una suite sin línea de resultado se trata como colgada.
14. **Brief separado de los mandates.** Plantilla Goal / Spec / Milestones / Constraints / Done state / Escalation ("una pregunta con default recomendado, nunca un menú"). El brief es reemplazable; los mandates no. Se demuestra corriendo los mismos mandates con el brief del toy.
15. **Handoff con campos fijos.** Qué cambió, cómo se construye y corre, qué verificó el emisor, `open_failures`, `next_action`. Si es largo, en partes numeradas con la última marcada "final"; nunca recortar requisitos. Referenciar la spec por sección en vez de pegarla entera en cada mensaje.
16. **Log de enmiendas A1..An.** Cada vez que un review cambia el plan queda una entrada fechada con la razón (se complementa con los eventos `assumption`).
17. **Higiene del repo.** `.gitattributes` con LF (un CRLF rompe el Dockerfile y tira la compuerta 3); el servicio bindea por env `HOST` con fallback `0.0.0.0` (con `127.0.0.1` no es alcanzable desde afuera del contenedor); sin paths absolutos del host, ids de room ni emails en docs.
18. **Métricas de la fábrica.** Además de tiempo y tokens: tasa de rechazo por etapa y *override-rate* (veces que el humano tuvo que corregir), que en la corrida final tiene que ser 0.
19. **Regla de restart en cada mandate.** Al reengancharse: anunciar el reattach, leer historia y plan, retomar el último ítem; el verifier re-corre el check en curso en vez de asumir su resultado.
20. **Eventos vs. mensajes.** Progreso y hallazgos individuales como eventos; handoffs y veredictos como mensajes.

### Esfuerzo medio

21. **Script de lanzamiento idempotente (bash).** Crea los seats con `jam agent create --transport claude-code-cli --runtime-auth subscription --runtime-model <id> --instructions-file mandates/<seat>.md`, arma el room con `jam chat new` / `jam chat add`, guarda estado en un archivo ignorado por git, falla si el `Model:` del mandate no coincide con el modelo real del seat y tiene un flag para forzar room nuevo en la corrida entregada. **Ningún comando `jam plan`/`work`/`usage`/`agent create`/`chat` figura en las docs oficiales, la hacker guide ni el SDK**: verificarlos con `band --help` en la versión instalada antes de escribir el script.
22. **Validador post-run.** Cruza `room.json` ↔ tasks ↔ commits: cada etapa cerrada tiene veredicto con SHA, cada SHA existe en el historial y cada rechazo tiene su reparación. Falla si queda algo huérfano.
23. **Paquete de verificación final.** Clon público fresco → `harness check` → `harness run --all --mode isolated` → `evidence/verification-receipt.json` con comandos, exit codes y tiempos. `evidence/PACKAGING.json` con sha256, bytes y `exportedAt` de `room.json`, y `edited` en `false` solo si no hubo que redactar nada; si se redactó una credencial, se registra qué y dónde (redactar ya es editar). Audit de symlinks, gitlinks, `.git` anidado, credenciales en todo el historial y vocabulario del track en mandates.
24. **Seat Spec Auditor** (opcional, suma un seat y costo). Solo lectura: matriz spec → código → check, busca faltantes y también extras no pedidos, firma por etapa y no por ítem para no llenar el room. El cierre de etapa requiere doble firma (verifier + auditor).
25. **Ensayo general sobre el toy con criterios de aceptación de la fábrica.** Ruteo autónomo sin handles en el brief; al menos un rechazo que vuelve al builder (si no ocurre solo, se inyecta un bug a propósito); la fábrica sobrevive a un reinicio sin crear identidades nuevas; swim lanes grabables para el video.

### Gotchas operativos de Jam (no están en las docs; comandos sin verificar con `band --help`)

- Una mención a un seat con el runtime parado es un no-op silencioso: `jam list` antes del dispatch es parte del preflight.
- `room send` devuelve 404 hasta que el humano es participante del room.
- `jam restart` no revive un peer parado, y Jam no recoge procesos `claude` huérfanos: revisarlos entre corridas.
- El timeout de una aprobación humana hace auto-deny: en la corrida final no puede quedar ningún permiso en modo manual.
- `jam plan set --snapshot` / `jam plan diagram` publican el plan en el room (re-ejecutar tras cada edición); `jam usage` da el consumo.
- Pegar la spec completa en cada handoff (decenas de KB por mensaje) dispara compactaciones de contexto y mensajes cruzados entre etapas.
- Los eventos `room_tasks` por WebSocket están detrás del flag `ff_room_tasks` y el SDK Python no los auto-une: nadie recibe push de cambios del board.
- Codex arranca con `approval_mode="manual"`, y con `approval_timeout_decision="decline"` un timeout termina en rechazo.

---

## Contrato del runner (harness del evento)

Leído de `harness/*.py` del repo oficial, sin abrir los tests de los tracks. Es formato, no contenido.

### Lo que el servicio tiene que cumplir

| Regla | Detalle |
|---|---|
| Puerto y bind | `0.0.0.0:8080`; el runner pasa **solo** `PORT=8080`. Un bind a `127.0.0.1` falla en los dos modos |
| Health | `GET /health` → 200, JSON `{"status":"ok"}`, sano en **< 60 s** desde `docker run`. En modo aislado cada intento del health es un contenedor nuevo del runner, así que el margen real es menor: apuntar a ≤ 30 s |
| Reset | `POST /_test/reset` → **204**, síncrono, < 10 s |
| Sin red en runtime | Nada de instalar, migrar descargando ni recursos de CDN en la UI: el browser también corre en la red interna |
| Sin config externa | Ninguna variable salvo `PORT`: todo con default dentro de la imagen |
| Recursos | 2 vCPU / 2 GiB. Desde la etapa 2 corren **dos contenedores a la vez** (N y N-1, en la misma red) para probar upgrades: una etapa anterior que no levanta tumba a la siguiente |
| Build | `docker build -f stage-N/Dockerfile stage-N/`, timeout 30 min. Nada de `COPY ../`, symlinks ni submódulos (`check` no los detecta) |
| Timeouts | 5 s por request, 900 s por suite. Ráfagas de hasta 50 hilos liberados juntos: subir el backlog de escucha |
| UI | Selectores solo por `data-testid`, 10 s por acción, contexto nuevo por test |
| Errores | El helper compartido espera la forma `{"error":{"code","message"}}` |
| Arquitectura | El jurado puede buildear en amd64: nada de binarios de arquitectura fija |

### Cómo cuenta

- `pass_rate` es el **promedio de la tasa de acierto por archivo de test**, no el total de checks. Una carpeta reclama su etapa si **cada** suite 1..N llega a 0,5.
- Overshoot: si la carpeta ya reclama, corre la suite N+1 con `-x`; si pasa **completa**, `claimed_stage` queda en `None`.
- Los jueces tienen un módulo `quality` (no incluido) que mide la **trayectoria de calidad entre etapas**: *erosion* y *verbosity*. El reviewer vigila que cada etapa extienda el código sin inflarlo.
- No existe `harness export-room`: `room.json` se baja a mano de la console.

### Lo que valida `harness check`

- `README.md`, `FACTORY.md`, `stage-1/`; carpetas `stage-[1-4]` exactas; `Dockerfile` y `RUN.md` por carpeta; sin `.git` adentro.
- `mandates/*.md` de primer nivel, ≥ 3. `Harness:` y `Model:` al inicio de línea (acepta `**Harness:**` o `- Model:`; falla en un heading, en una tabla o vacío). **No** compara contra el modelo real.
- Vocabulario: tokeniza cada línea del mandate (rutas, snake_case, kebab-case) y falla con coincidencia **exacta** contra la lista del track. Términos genéricos como `/health`, `idempotency-key`, `data-testid` o `stage-1` no están.
- `room.json`: objeto con `messages[]` y `scope` ausente o `"full"`. Seats = remitentes con `senderType` agent, ≥ 3 distintos por `senderId`. **Todo agente que habló necesita mandate** (slug de `senderName` sin no-alfanuméricos = nombre del archivo); dos seats con el mismo nombre visible colapsan en uno.
- Reciprocidad: solo mensajes `text` de agentes con `@[[<senderId>]]` literal. Una mención dentro de un tool call no cuenta.
- Credenciales en `.md .py .txt .json .yml .toml .env .js .ts .sh` y afines (no mira `.html .tsx .jsx .css`): `bearer <token>`, `sk-…`, `AKIA…`, `gh[pousr]_…`, `://user:pass@`, y `*KEY|TOKEN|SECRET|PASSWORD=` en archivos de config. Un `curl` con `Authorization: Bearer` en la salida de un tool dentro de `room.json` **hace fallar el check**.

### Checks del paquete final (se suman al ítem 23)

1. `harness check` y `harness run --all --mode isolated` sobre un clon fresco; ninguna carpeta en overshoot.
2. Tiempo hasta `/health` sano por etapa en modo aislado (≤ 30 s).
3. `docker run --network none -e PORT=8080` por etapa → `/health` 200.
4. `POST /_test/reset` → 204 en < 10 s.
5. Grep de binds a `127.0.0.1`/`localhost` en el código servido.
6. `find . -type l`, `git submodule status`, `find stage-* -name .git`, `git ls-files -s | grep ^160000`: todo vacío.
7. Scan de credenciales sobre `git log -p` completo, incluyendo `.html .tsx .css`.
8. Ningún `._*` de macOS en el repo (rompen el build y el gate 1): `COPYFILE_DISABLE=1`, `._*` en `.dockerignore`, repo en disco interno, no en exFAT.

---

## Lecciones de una corrida real y de la guía de BAND

Sacadas del `room.json` público de otra fábrica (3 seats, 4 etapas, 2.896 mensajes, 3 h 43 min), del ejemplo `examples/coding_agents` del SDK, del orquestador oficial `band-ai/codeband` y de la hacker guide (https://www.band.ai/hacker-guide).

### Qué evalúa el jurado según BAND: el delete test

"Take the room out of your design. Does the app still work? If it does, you've built a single-agent app with a chat log attached" — y "it's what hackathon judges look for". Hay que mostrar al menos una, idealmente dos o tres, de estas señales:

- **Handoff dependiente**: el trabajo del segundo seat cambia por lo que encontró el primero, no por su texto pegado.
- **Roster decidido en runtime**: el coordinador recluta según la necesidad.
- **Un límite que BAND hace cumplir**: quién puede mencionar a quién.
- **Un veredicto que puede bloquear**: la conclusión de un seat no sale porque otro dijo que no.

No cuenta: mensajes de estado que nadie necesita leer, un proceso cambiando de persona, un orquestador propio llamando agentes por turno (el room queda como transcript de decisiones ya tomadas), un dashboard como entregable.

La presentación responde cuatro preguntas: el equipo; quién le habla a quién, **incluido a quién se dejó afuera de una mención y por qué**; un flujo típico de punta a punta; y qué se rompe sin el room. La línea de flujo con flechas se escribe antes de grabar la demo.

### Qué llega realmente en `room.json`

- Llegan `text` (completos), `tool_call` (args cortados a ~4,3 KB), `tool_result` (salida cortada a ~4 KB), `thought` (completos) y eventos del runtime (turnos, compactaciones, respawns). `metadata.deliveryStatus` trae `deliveredAt`/`processedAt` por destinatario: mide la latencia real de cada handoff.
- **No llegan** tokens ni usage, `attention`, memoria ni el estado del task board.
- Por eso: al cerrar cada etapa, el coordinador publica un `text` con el uso medido y la tabla de tareas `#N from→to SHA`. Cada corrida de checks imprime primero una línea resumen (pasados, fallados, SHA, segundos) y el veredicto la copia textual.
- Los thoughts se leen: idioma fijo (inglés) y que digan qué se va a verificar.

### Reglas para los mandates

1. **Plantilla por rol**: Own / Do not / Use / Ask a person / Done means. Incluye "no afirmar que los tests pasan sin haberlos corrido".
2. **Bloque anti-loop**: mencionar es llamar a una función; los acks van sin `@`; silencio después de un handoff; nada de "ready and waiting" o "standing by"; nombrar sin `@` a quien no tiene que actuar.
3. **Un turno por unidad de trabajo**: mandar el handoff y cerrar el turno; nunca seguir con la etapa siguiente en el mismo turno. Un seat publica su respuesta recién al cerrar el turno: turnos de 1–2 h produjeron respuestas con hasta 72 min de atraso, un handoff cruzado y una reparación delegada dos veces.
4. **Handoffs sin esperar respuesta**: un envío que bloquea esperando contestación, con un trabajo de más de 10 min del otro lado, dejó a un coordinador 74 min parado con 6 timeouts.
5. **Cada mensaje dice a qué estado responde** (`re: <SHA> etapa N`); el receptor descarta en silencio lo anterior al último veredicto que conoce.
6. **Antes de pedir un handoff, mirar el board**: el handoff se registra también como transición de la tarea con el SHA.
7. **Un solo dueño de la reparación**: el REJECT va del reviewer al builder y el coordinador no re-delega.
8. **El coordinador no reenvía contenido**: el emisor le habla directo al destinatario. Antes de pasar un reporte, el coordinador lo verifica con un comando.
9. **Archivos con un solo dueño** (`notes/plan.md` del planner, `notes/review.md` del reviewer): el chat lleva el veredicto y la ruta. Complementa la regla de handoffs autocontenidos: lo que el receptor necesita va en el mensaje, el detalle largo en el archivo.
10. **`task_key`** kebab-case (≤ 32 caracteres) en cada mensaje, branch y commit.
11. **Tope de 5 rondas de review por ítem**; el coordinador interviene antes si se repite el mismo fallo.
12. **Regla de evidencia del crítico**: una afirmación sin un hallazgo publicado en el room recibe `BLOCKED` con la evidencia faltante; para el coordinador un `BLOCKED` es terminal hasta resolverse. Vara: "¿bloquearía este merge?".
13. **Veredicto `INSUFFICIENT_EVIDENCE`** separado de REJECT: separa "producto mal" de "evidencia incompleta".
14. **Un candidato corregido es nuevo**: no hereda la aceptación; se re-corren primero las pruebas que fallaron y después la regresión.
15. **El verifier pierde autoridad si edita producción**, y arranca siempre del commit declarado, nunca de un workspace sin commitear. Registra limitaciones aunque acepte.
16. **El breaker entrega la lista de lo que no probó** y rechaza si el éxito depende de estado del entorno no declarado.
17. **Prioridad de cola del coordinador**: falla bloqueante → candidato esperando verificación → aclaración → snapshot → siguiente etapa → pulido.
18. **Guard de branch antes de editar**: branch correcto, `HEAD` esperado y `git status --short` limpio; si no, escalar con el estado concreto, nunca con un "I stopped" genérico.
19. **Mandates congelados**: solo se revisan por un defecto genérico de la fábrica, nunca por la tarea, y cada revisión queda registrada.
20. **Auto-test de genericidad por oración** ("¿tiene sentido para un editor de documentos o una cola de mensajes?") más una lista de huellas prohibidas: sustantivos de dominio y umbrales numéricos.
21. **No comprimir texto para que entre** (borrar espacios lo vuelve ilegible): si es largo, se parte.

### Verificación que atrapa lo que las suites no ven

- En la corrida analizada, **4 de los 5 rechazos salieron de pruebas de caja negra del coordinador**, mientras las suites propias del reviewer (75 grupos, 2.585 llamadas) y las oficiales (120/120) daban verde. Se formaliza: el coordinador prueba casos extremos mientras el reviewer revisa, y el reviewer reproduce cada uno antes de rechazar.
- Categorías que se escaparon y van al checklist adversarial: profundidad y tamaño de input, IDs opacos con caracteres codificados (`%2F`), textos largos sin espacios a 375 px, UI que queda vieja después de un cambio del servidor, persistencia tras reiniciar el contenedor.
- La review es el cuello de botella (4–19 min contra 3–4 min de reparación): FACTORY.md reporta latencia handoff → veredicto y rechazo → reparación, sacada de `deliveryStatus`.

### Operación

- **Un solo dispatch con las 4 etapas**; un segundo mensaje humano entre etapas cuenta como intervención.
- **Preflight del seat**: herramientas verificadas (`rg` faltaba en los 3 seats), hoja de comandos del CLI en el brief (hubo 7 `--help` y 7 greps fallidos buscando subcomandos), MCP no usados desactivados (11 fallas por respawn) y nada de `sleep` como espera (108 eventos de ruido).
- **Freeze antes del dispatch**: tabla PASS/BLOCKED con los hashes SHA-256 de cada mandate y del brief; un valor sin verificar bloquea el dispatch.
- **Matriz de capacidades por seat** en FACTORY.md: quién escribe producción, quién acepta, quién habla con quién.
- **Evidence index**: criterio → etapa → comando → archivo → PASS/FAIL, para que el jurado no lea logs.
- **Handoff con `evidence[{path, sha256}]` y `assumptions`** (extiende el ítem 15).
- **Roles forzados por permisos, no solo por prompt**: escritura limitada por path (el reviewer escribe solo en tests y evidencia).
- **Descripción del seat con tokens** `role=<rol> harness=<…>` para reclutar con `band_lookup_peers` por rol.

### Esfuerzo medio

- **Watchdog determinista sin LLM**: consulta REST, umbral de inactividad por rol, un nudge y una escalada, sin volver a molestar a un seat que confirmó estar vivo. Pasa la espera acotada del ítem 9 de prompt a código.
- **Worktree por seat sobre un clon compartido**: reviewer y planner en detached HEAD de solo lectura, builder en su branch. El veredicto queda atado al SHA por construcción.
- **Máquina de estados por etapa** (`active / paused / human_owned / closed`), anunciada al room; cada seat la consulta antes de actuar.
- **Sobre de protocolo con id de correlación** (`protocol code_review cid cr_<n>_r<round> state … from X to Y`) como evento del room o JSONL append-only: insumo del validador del ítem 22.
- **Índice de contexto del repo** (`structure/patterns/dependencies.md`) regenerado solo si cambia HEAD e inyectado en el prompt: menos exploración por seat.
- **`TASK.md` + `.state.json` por seat** para rearmar contexto tras un reinicio (git log + cambios sin commitear + tarea).
- **Ledger de ids de agentes creados** (`.agent_ids.txt`) y rechazo a sobrescribir la config sin `FORCE=1` en el script de lanzamiento.
- **Seat breaker en otro proveedor vía SDK** para diversidad real de modelo. Riesgo: confirmar en el toy que aparece en el roster y en `room.json`, y que su modelo coincide con el `Model:` del mandate.

### Descartado

- Pasos humanos durante la corrida (aclaraciones, QA humano realimentado, pedidos de pulido): es steering.
- Meter arquitectura o valores de prueba en el brief: el brief es la spec oficial más `docs/DESIGN.md`. El design system es la única excepción, decidida el 26 sep, y se declara en `FACTORY.md` como insumo del dispatch.
- Reglas de fuentes no oficiales (licencia cerrada obligatoria).

---

## Entrega en lablab: lo que premian los jurados

Relevado de ganadores públicos de lablab el 26 sep 2026, sobre todo del **Band of Agents Hackathon** (jun 2026, mismo sponsor, 391 proyectos). Cada página de proyecto trae `eventPosition` y las reviews de los jueces son públicas, con puntaje por criterio y a veces con comentario.

### Qué separa a los ganadores

- **El mecanismo, no la etiqueta.** Los jueces de BAND castigan nombrarlo en los tags sin mostrar la coordinación ("unclear how Band is used", 10/20) y premian una frase explícita del tipo "Remove Band and the chain collapses" ("exactly how Band should be used"). Es el delete test.
- **Un agente que objeta a otro**: disenso, veto, red team, observer que se corrige, gate humano. Un pipeline fijo de roles (PM → Architect → QA) les pareció poco ("competes with model progress").
- **Números verificables**: antes/después de tiempo, cantidad de tests, agentes × frameworks, hashes o `jsonl` de auditoría. Cada cifra rastreable en el repo; lo inferido se rotula "inferred".
- **"Nothing is mocked"** con la fuente de cada dato.
- **Diagrama de arquitectura** en deck y README: un 1° puesto perdió puntos de presentación por no tenerlo.
- **Commits repartidos en la ventana del evento** (ganadores: 93, 39, 28). "An empty repo with one final push raises red flags".
- **UI cuidada**: aparece explícita en los comentarios ("Great UI", "user persona and journeys are well explained").
- Lo que resta: long description vacía o genérica, video incompleto, deck de 4 slides "too limited", error en vivo durante la demo.

### Ficha

- **Título** (≤ 50): nombre + promesa después de dos puntos o raya ("<Nombre>: <qué hace la fábrica>").
- **Short** (230–255): una escena y un resultado, no la tecnología. Por ejemplo: entra una spec, un seat la entrega a otro, otro la rechaza, sale un servicio verificado.
- **Long** (~1800 de 2000), en cuatro bloques: problema con una cifra dura → la fábrica paso a paso con los seats → qué no está simulado → por qué sin BAND se cae.
- Los ganadores usan casi todo el límite de cada campo.

### Video

- **3 a 4:30 min**: la rúbrica de lablab baja la presentación por debajo de 3 min, y más de 5 no suma (mediana de ganadores ~4 min, rango 95–326 s).
- Estructura: problema en 30 s → room de BAND con los seats en vivo → el handoff marcado en pantalla → el rechazo que cambió el resultado → el servicio funcionando → costo, falla atrapada y etapa alcanzada.
- "Judges reward clarity over production value." La mayor parte del tiempo, el producto funcionando.

### Deck

- **8–10 slides**, 2–3 oraciones por slide, mucho diagrama.
- Arco: claim → problema con cifra → diseño de la fábrica (diagrama de seats y handoffs) → los seats y sus modelos → la falla atrapada con el disenso textual → costo medido → "sin mocks" → por qué BAND → outcome con links a GitHub y al video.

### README

- Diagrama mermaid de la fábrica, elenco de seats, cómo correrlo, cómo reproducir una etapa.
- Sección **"How it maps to the judging criteria"**: Factory 50%, App 25%, Agent Teamwork 25%, cada uno con su evidencia.

### Fuentes

- Rúbrica de lablab (1 a 5 por criterio): https://lablab.ai/hackathon-rules
- https://lablab.ai/delivering-your-hackathon-solution: el video arranca con una introducción, pasa por el PDF y después muestra el producto.
- https://lablab.ai/guide/how-to-win-an-ai-hackathon

---

## Plan

| Cuándo | Qué |
|---|---|
| sáb 26 – dom 27 sep | Inscribirse en lablab. Crear cuenta BAND, instalar Desktop + CLI + plugin, readiness check. Unirse a los dos Discord. Leer las specs completas de ambos tracks y **elegir track** |
| lun 28 – mar 29 sep | Diseñar la fábrica (roles, mandates, protocolo de handoff y review). Correr **toy** completo en modo aislado y medir tiempo, tokens y cupo |
| mié 30 sep – vie 2 oct | Iterar sobre el track real: etapas 1–4, ajustar mandates según las fallas |
| sáb 3 oct | **Corrida final**: room y repo nuevos, autónoma, al inicio de una ventana de cupo |
| dom 4 oct | `harness check` + suites en modo aislado. Exportar `room.json` y redactar credenciales. Escribir README y FACTORY.md a mano |
| lun 5 oct | Video + slides. Enviar el formulario antes de la noche (cierre mar 6 oct 03:59 ART) |

---

## Checklist de entrega

- [ ] Inscripto en lablab
- [ ] 3+ seats, cada uno con `mandates/<seat>.md` que empieza con `Harness:` / `Model:`
- [ ] Mandates sin vocabulario del track
- [ ] `@handle` recíprocos visibles en el room
- [ ] Corrida final en room y repo nuevos, sin intervención después del dispatch
- [ ] `stage-1..4/` con `Dockerfile` + `RUN.md`, cada una copia extendida de la anterior, sin `.git` anidado
- [ ] Ninguna línea de código escrita a mano en `stage-N/`
- [ ] Suites en `--mode isolated` corridas por etapa; `harness check` limpio
- [ ] `room.json` sin modificar, con credenciales redactadas
- [ ] `README.md` y `FACTORY.md` escritos a mano: diseño, costo, falla atrapada, etapa alcanzada
- [ ] Repo público, clonable sin cuenta de BAND
- [ ] Video con room, handoff y servicio funcionando
- [ ] Slides
- [ ] Formulario de lablab enviado antes del **mar 6 oct 03:59 ART**
