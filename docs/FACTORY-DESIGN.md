# Lights-out — diseño de la fábrica

> Movido desde `docs/HACKATHON.md` (secciones 12–14) el 26 sep 2026, cuando ese archivo pasó a ser el brief del evento en inglés.

## Hoja de ruta por fases

Seis fases en orden. Se pasa a la siguiente cuando se cumple el criterio de salida, no por fecha (el calendario está en **Plan**). Los mandates cargan solo lo de la fase en curso: cada regla de más es costo por turno y *verbosity*.

### F0 — Setup

- Inscripción en lablab, Discord conectado y equipo propio como admin.
- Cuenta BAND, Desktop, CLI y plugin `band-peer`; readiness check.
- `band --help` en la versión instalada para verificar los comandos del ítem 21 y los gotchas de Jam.
- Leer las specs completas de los tracks.

**Sale** con readiness en verde, *Submit Project* habilitado y los comandos reales de `band` anotados.

### F1 — Diseño de la fábrica y toy

- Mandates con la plantilla de la regla 1 y el bloque anti-loop (regla 2); brief con la plantilla del ítem 14.
- Protocolo: **Vocabulario único y última línea** (ítems 26–28).
- Alcance: ítems 1, 2, 5, 9, 15, 17, 19, 26, 27, 28, 45, 46; reglas 1–5, 7, 11, 13.
- Validador v1 (ítem 22 básico): SHA existentes, veredicto por etapa, rechazos con reparación.
- Preflight del seat (Operación). Primero el **caso chico** y, cuando cumple sus criterios, el **caso mediano** (toy) en modo aislado (ver **Casos de prueba de la fábrica**).

**Sale** con los criterios de los casos chico y mediano cumplidos y las **Decisiones pendientes** 1–5 resueltas y escritas.

### F2 — Iteración sobre tablekeeper

- Corridas del **caso grande** (el track real); los mandates cambian solo por defectos genéricos de la fábrica (regla 19) y cada cambio queda registrado.
- Alcance que se suma si el toy lo probó: ítems 3, 4, 6, 7, 8, 13, 16, 18, 23, 31, 32, 33, 34, 36, 41, 42, 43, 44, 47; breaker o auditor según la Decisión 4.
- Validador v2: menciones y ciclos (ítems 29, 30), errores vs warnings (ítem 38).

**Sale** con una corrida que cumple los criterios del caso grande (salvo los de la corrida final: repo nuevo y un solo intento) y los mandates y el brief congelados con sus hashes SHA-256 (Operación: freeze).

### F3 — Corrida final

- Preflight: los ítems de la corrida en el **Checklist de entrega** (Mac despierta, repo nuevo con remote y push), seats *bound*, `jam list`, ningún permiso en modo manual.
- Un solo dispatch con las 4 etapas; sin intervención humana después.

**Sale** cuando la corrida termina. Si falla un gate, se repite en una ventana de cupo nueva y el toy de cierre de F4 pasa a ser opcional.

### F4 — Empaquetado

- Descargar `room.json` de la console, redactar credenciales y registrar en `evidence/PACKAGING.json` (ítem 23).
- Checks del paquete final (Contrato del runner) y validador sobre la corrida final.
- Toy de cierre: el caso mediano re-corrido con los mandates congelados, evidencia de genericidad (ítem 14; la métrica del ítem 35 solo si sobra tiempo).
- README y `FACTORY.md` a mano; ficha con `hackathon-submission`.

**Sale** con `harness check` y `harness run --all --mode isolated` limpios sobre un clon fresco y `docs/submission.md` dentro de los límites de cada campo.

### F5 — Entrega

- Deck con `hackathon-deck`, después de la ficha para no contradecirla.
- Video con `personal-record-video` (3 a 4:30 min, con la grabación del room).
- Formulario de lablab y auditoría con `hackathon-close`.

**Sale** con el formulario enviado y el **Checklist de entrega** completo.

### Solo si sobra tiempo

Ítems 21, 24 (si no entró por la Decisión 4), 35, 37, 39, 40; watchdog, worktrees, sobre de protocolo completo y el resto de "Esfuerzo medio" de Lecciones.

## Casos de prueba de la fábrica

Movidos a `docs/USE-CASES.md` (en inglés, trazados a los R y AE de `docs/BRIEF.md`): chico con la API de notas (`cases/small/`), mediano con el track toy y grande con tablekeeper, cada uno con criterios de producto y de sistema y cómo se prueban.

## Setup propio de Lights-out

**Modelos y cupo**
- Todos los seats en **Claude Code con la suscripción Max**: no hay costo por token, pero los seats en paralelo comparten el cupo de uso.
- Mezcla de modelos para estirar el cupo: el modelo más fuerte en el seat que construye; el de los que revisan, pendiente (ver **Decisiones pendientes**). Declarar el ID exacto en cada mandate.
- Plan B: un seat en **OpenCode + key paga de Gemini** como revisor. Descarga cupo de Max y da diversidad real entre seats. Evitar el plan gratuito de Gemini en la corrida final, porque sus límites de requests pueden trabar un seat sin posibilidad de intervenir.
- Plan C: un seat en **OpenCode + Featherless** como revisor, con los US$25 de créditos del evento (primeros 1.000 inscriptos, promo por mail; el alta pide tarjeta, cancelar antes del próximo ciclo). Modelos documentados en la guía: MiniMax-M2.5, Kimi-K2.5, DeepSeek-V3.2. Config en `~/.config/opencode/opencode.json`, nunca en el repo; `turn_timeout_s=900`; no corre en Docker Sandbox. Probarlo en el toy: si el seat no arranca, pasarlo a Claude Code sin depurar el runtime.

**Costo**
- Medir con el track **toy** cuánto consume una corrida completa de 4 etapas antes de ir al track real.
- Lanzar la corrida final **al inicio de una ventana de uso limpia**.
- Reportar el costo en `FACTORY.md` como tiempo y tokens; la fuente de los tokens está en **Decisiones pendientes** 1.

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
| Task board del room (**Beta**) | REST `POST /api/v1/agent/chats/{id}/tasks` (`subject`, `detail`); update con `status` `pending → in_progress → in_review → completed/failed`, `comment`, `linked_native_id` | Reparto visible con `#N`; `in_review → in_progress` con comentario = review que cambió el resultado; `linked_native_id` = SHA del commit. Sirve para **coordinar**: el board no llega a `room.json`, así que la evidencia para el jurado es la tabla `#N from→to SHA` publicada como `text` al cierre de cada etapa | `/api/agent-api/agent-api-chat-tasks` |
| Historial de tasks | `GET .../tasks/{id}/history`, append-only con actor y `from → to` | Evidencia de reviews y reintentos | idem |
| Goal del room | `PUT .../board` con `goal_title`, `goal_summary` | El coordinador fija la misión de la etapa | idem |
| Evento `attention` tipo `assumption` | REST `POST /api/v1/agent/chats/{id}/events`, `metadata.kind=assumption`, no bloqueante | Registrar decisiones en vez de preguntarle al humano (autonomía). `attention` **no llega** a `room.json`: cada suposición se publica también como `text` y va al log de enmiendas (ítem 16) | `/api/agent-api` |
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
3. Tasks/board son Beta. En la API figuran solo por REST, pero la CLI `band` 0.4.12 los maneja sin key en el repo: `band work assign` (tarea compartida del room), `take`, `room-status`, `board`, `history` y `edit` (guarda `from -> to`). Probar en el caso chico antes de meterlas en un mandate.
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
4. **Veredicto atado a SHA + tree hash.** Todo veredicto cita `sha=` y `tree=` (tree hash de la carpeta, `git rev-parse HEAD:stage-N`) en la última línea del ítem 26. El reviewer verifica que los tree hash de las etapas anteriores no cambiaron.
5. **Release check.** Antes de aprobar una etapa: checkout limpio, build del contenedor, suites 1..N verdes y la suite N+1 **no debe pasar completa** (el harness solo invalida si pasa entera; la etapa 4 no tiene N+1). Después se congela la carpeta.
6. **Diversidad de modelo como regla.** El verifier nunca corre el mismo modelo que el builder: dos instancias del mismo modelo se equivocan en lo mismo. Escrito como restricción en `FACTORY.md`, no como descripción.
7. **Grafo de ruteo restringido.** El builder no menciona al auditor ni al humano; solo el coordinador habla con el humano; nadie tiene camino hacia su propia aprobación. `FACTORY.md` suma la sección "qué se rompe sin el room".
8. **Ruteo por rol, no por handle.** Cada seat consulta los participantes y menciona al que tiene el rol destino (tabla emisor → condición → rol). Hace a los mandates re-armables con otros nombres.
9. **Espera acotada.** Si un seat no responde en 10 min, se registra "unanswered wait", se lo re-agrega al room y se reintenta una vez; nunca se auto-aprueba. Prohibido reclutar agentes ajenos a la banda. Un bloqueo real se registra como resultado de la etapa y se para, sin preguntar.
10. **"No reply requested".** Los mensajes de evidencia suplementaria lo dicen explícito para no disparar turnos inútiles (ahorra tokens).
11. **Barrido de riesgos obligatorio en cada veredicto**: cada riesgo como confirmed-safe con `archivo:línea`, tested, accepted u open; un ACCEPT con riesgos `open` los lista como follow-up. Los hallazgos equivocados se retractan en público. El vocabulario de veredictos es el de **Vocabulario único** (abajo).
12. **Ley de conservación.** Cuando el dominio tiene una cantidad que debe balancear, una aserción de invariante global es obligatoria al final de cada test de concurrencia; si falta, es blocker.
13. **Gate de regresión.** Conteo base de tests: si baja, hay que explicar qué se borró. El gate nunca se pipea por `tail`/`grep` (el exit code miente) y nombra el paso que falló. Una suite sin línea de resultado se trata como colgada.
14. **Brief separado de los mandates.** Plantilla Goal / Spec / Milestones / Constraints / Done state / Escalation ("una pregunta con default recomendado, nunca un menú"). El brief es reemplazable; los mandates no. Se demuestra corriendo los mismos mandates, ya congelados, con el brief del toy (toy de cierre, ver F4 en **Hoja de ruta por fases**).
15. **Handoff con campos fijos.** Qué cambió, cómo se construye y corre, qué verificó el emisor, `open_failures`, `next_action`. Todo handoff delegado lleva **la tarea y la spec completas pegadas** (la guía oficial lo exige: "pointing at a room message id or asking a seat to read the room is insufficient"; el reviewer también recibe los requisitos completos). Si es largo, en partes numeradas con la última marcada "final"; nunca recortar requisitos. El costo de pegarla se controla con partes numeradas y la regla "un turno por unidad de trabajo", no referenciando.
16. **Log de enmiendas A1..An.** Cada vez que un review cambia el plan queda una entrada fechada con la razón (se complementa con los eventos `assumption`).
17. **Higiene del repo.** `.gitattributes` con LF (un CRLF rompe el Dockerfile y tira la compuerta 3); el servicio lee `PORT` con default `8080` y bindea `0.0.0.0` (con `127.0.0.1` no es alcanzable desde afuera del contenedor; el runner no pasa ninguna otra variable); sin paths absolutos del host, ids de room ni emails en docs.
18. **Métricas de la fábrica.** Además de tiempo y tokens: tasa de rechazo por etapa y *override-rate* (veces que el humano tuvo que corregir), que en la corrida final tiene que ser 0.
19. **Regla de restart en cada mandate.** Al reengancharse: anunciar el reattach, leer historia y plan, retomar el último ítem; el verifier re-corre el check en curso en vez de asumir su resultado.
    Un seat solo se despierta con un mensaje, así que la espera de 10 minutos del coordinador no tiene disparador propio. Desde el 29 sep (corrida 4 del caso chico, una respuesta staged que se perdió) la cubre `tools/watchdog.py`: reinicia con `band restart` al seat mencionado que lleva 10 minutos inactivo sin contestar, y no escribe en el room. Los seats publican con `send`, que publica al instante, y confirman que el mensaje llegó.
20. **Eventos vs. mensajes.** Solo el progreso descartable va como evento (no llega a `room.json`). Hallazgos, handoffs, veredictos y suposiciones van como `text`: son lo que leen el jurado y el validador.

### Esfuerzo medio

21. **Script de lanzamiento idempotente (bash).** Crea los seats con `jam agent create --transport claude-code-cli --runtime-auth subscription --runtime-model <id> --instructions-file mandates/<seat>.md`, arma el room con `jam chat new` / `jam chat add`, guarda estado en un archivo ignorado por git, falla si el `Model:` del mandate no coincide con el modelo real del seat y tiene un flag para forzar room nuevo en la corrida entregada. Verificado el 28 sep con `band --help` (v0.4.12, `jam` es alias): existen `band agent create` / `agent instructions`, `band chat new|list|add|remove|participants`, `band plan set|diagram|show|focus|status`, `band work …`, `band usage …`, `band send`, `band attach` (alias `reattach`), `band preflight`, `band doctor`, `band permissions`. Los flags exactos de `agent create` se leen con `band agent create --help` al escribir el script.
22. **Validador post-run.** Cruza `room.json` ↔ tasks ↔ commits: cada etapa cerrada tiene veredicto con SHA, cada SHA existe en el historial y cada rechazo tiene su reparación. Falla si queda algo huérfano.
23. **Paquete de verificación final.** Clon público fresco → `harness check` → `harness run --all --mode isolated` → `evidence/verification-receipt.json` con comandos, exit codes y tiempos. `evidence/PACKAGING.json` con sha256, bytes y `exportedAt` de `room.json`, y `edited` en `false` solo si no hubo que redactar nada; si se redactó una credencial, se registra qué y dónde (redactar ya es editar). Audit de symlinks, gitlinks, `.git` anidado, credenciales en todo el historial y vocabulario del track en mandates.
24. **Seat Spec Auditor** (opcional, suma un seat y costo). Solo lectura: matriz spec → código → check, busca faltantes y también extras no pedidos, firma por etapa y no por ítem para no llenar el room. El cierre de etapa requiere doble firma (verifier + auditor).
25. **Ensayo general sobre el toy con criterios de aceptación de la fábrica.** Ruteo autónomo sin handles en el brief; al menos un rechazo que vuelve al builder (si no ocurre solo, se inyecta un bug a propósito); la fábrica sobrevive a un reinicio sin crear identidades nuevas; swim lanes grabables para el video.

### De A2A y AGNTCY (relevado el 27 sep 2026)

Ideas de protocolo tomadas de la spec de A2A (https://a2a-protocol.org), sus samples, los repos de la org `agntcy` y proyectos que los usan. Ninguno se adopta como transporte: BAND es obligatoria, y reemplazar el room falla el delete test.

26. **Última línea parseable con estado cerrado.** Todo handoff y veredicto termina en la única línea de protocolo definida en **Vocabulario único** (abajo), seguida de `NEXT @<handle>` o `DONE`. `refused` es el receptor negándose a tomar un handoff (inválido o fuera de su rol), distinto de un REJECT del producto y de `failed`; `input-required` va al coordinador, nunca al humano. El protocolo se versiona como `factory-protocol/v1` en `FACTORY.md`. Es la versión barata del sobre de protocolo y lo que parsea el validador del ítem 22. Fuentes: SHADI AgentBridge "Line protocol" (`agntcy/shadi`), `TaskState` de `a2a.proto`, extensiones de A2A.
27. **Rechazo tipado de un handoff incompleto.** El receptor valida los campos del ítem 15 antes de trabajar; si falta uno responde `STATE refused code=MISSING_FIELD details=[...]` y cierra el turno. Fuente: spec A2A §3.3.2 y §3.3.4.
28. **ACCEPT / DISPUTE / CLARIFY por hallazgo.** El builder contesta cada `[C-nn]` rechazado: ACCEPT con el SHA de la reparación, DISPUTE con evidencia o CLARIFY. Un ACCEPT no cierra el hallazgo hasta que el reviewer lo re-verifica. Al tope de rondas decide el coordinador. Es el disenso visible que premian los jueces.
29. **Grafo de menciones observado contra el declarado.** El validador saca las aristas rol→rol de las `@mention` en `room.json` y las compara con la matriz de capacidades: toda arista no declarada falla y nadie aprueba su propio SHA. Antes de correr, la tabla de ruteo no puede tener un camino a la autoaprobación. La matriz con conteos se publica como `text` y responde "a quién se dejó afuera". Solo el coordinador conserva `band_add_participant` (modelo del moderador de SLIM): **verificar en el toy si band-peer respeta filtros de tools**, documentados solo para el SDK. Fuente: `agent_to_agent_interactions.py` de `agntcy/telemetry-hub`.
30. **Contador de ciclos.** Por etapa, las secuencias A→B→A→B sin SHA nuevo son ping-pong (ruido) y con SHA nuevo son reparaciones. Se publican los dos conteos: mide la regla anti-loop. Fuente: `cycles.py` de `telemetry-hub`.
31. **Niveles de evidencia.** Columna en el evidence index: absent / declared / checked / demonstrated / attested; el validador cuenta solo demonstrated o más. Verificar al consumir: antes de construir sobre algo que otro afirmó ("tests verdes"), se re-corre ese chequeo. En un caso publicado, un "11/11 GREEN" eran 11 fallas.
32. **Corte por plateau y por rol no mapeado.** Si la cantidad de checks fallados no baja en 2 rondas seguidas, se escala al coordinador sin esperar la quinta. Si una tarea no encaja en ningún rol de los mandates, se registra y se para; no se improvisa un rol. Fuente: tabla "Halt" de ASSEMBLY/CONVERGE (SHADI).
33. **Brief versionado con acuse.** El coordinador publica el goal de la etapa como `brief@vN`; cada handoff lo cita en el campo `brief=` de su última línea, y el receptor lo repite en la suya. Un handoff con versión vieja se descarta, y un seat puede objetar con `CHALLENGE brief@vN <razón>` al coordinador. Fuente: patrón "shared intent registry" de CoffeeAGNTCY.
34. **Roster activado y publicado en runtime.** Qué seats existen (con su mandate) se decide antes del dispatch (Decisión pendiente 4): `harness check` exige mandate de todo seat que habló, y un seat creado que nunca habla no lo rompe. En la corrida, el coordinador decide si **activa** al breaker o al auditor; al hacerlo publica SELF / COLLABORATE / HANDOFF con el motivo y qué trabajo se conserva, o una encuesta de roles con `ACCEPT role=<r> model=<m>` / `DECLINE <motivo>`, y cierra con `ROSTER stage=N rol=@handle…` como `text`. Solo seats de la banda (ítem 9). Es la señal "roster decidido en runtime" del delete test.
35. **Genericidad medida por distancia de grafos.** Diferencia simétrica entre las aristas rol→rol del toy de cierre y de la corrida final, con los mismos mandates congelados y otro brief (un toy con mandates anteriores no sirve de comparación). Una diferencia chica prueba que la forma de la fábrica no depende del dominio; la cifra va a `FACTORY.md` y sale de un comando. Fuente: `graph_determinism_score.py` de `telemetry-hub`.
36. **Una tarea terminal no se reabre.** La reparación es una tarea nueva con `refs=[#N@<sha-rechazado>]` en su última línea, y el validador sigue la cadena sin heurística. El board puede seguir usando `in_review → in_progress` para coordinar. Fuente: "Task Immutability" de A2A.
37. **Contratos abiertos al cierre de etapa.** El coordinador publica las obligaciones pendientes (emisor, receptor, entregable, `close_loop_time`); la etapa no cierra con ninguna abierta.
38. **Métricas del validador.** Tasa de recuperación autónoma = rechazos reparados y aceptados sin humano / rechazos totales (junto al override-rate del ítem 18). El validador separa errores (SHA inexistente, veredicto sin reparación: fallan) de warnings (latencia alta, ciclo de ruido: se reportan). El uso por etapa se publica con forma de spans (`step_id`, `parent_step_id`, seat, tokens, latencia): da el formato de la Decisión pendiente 1, no la fuente del número. Fuentes: `error_recovery_rate` de `agntcy/observe`, validación de OASF, extensión traceability de a2a-samples.
39. **Cadena de hashes entre veredictos.** Cada veredicto cita en `prev=` el sha256 del veredicto anterior de la etapa; el validador detecta mensajes perdidos, cruzados o duplicados por la entrega at-least-once. Git encadena commits, no veredictos.
40. **Retro post-run.** Al cerrar, el coordinador publica cambios genéricos propuestos a los mandates; no se aplican durante la corrida (regla 19) y alimentan la revisión entre ensayos. **Implementado (1 oct):** después del resultado, el coordinador pide la retro a cada seat (paso 8) y cada uno contesta con líneas `LESSON` genéricas (regla común **Retro**); `tools/retro.py` las junta por seat y marca términos del dominio, el coordinador revisa cada retro al llegar, decide qué aplicar y edita él mismo `## Lessons` de cada mandate, fuera del bloque común y sin commitear (paso 9, registro `task=retro-apply`); el humano audita el diff al cerrar. El validador imprime el `run time` (despacho → resultado, sin la retro) para comparar corridas con los mismos requisitos.

Descartado de estas fuentes: usar A2A, SLIM, Dir o SHADI como transporte; `auth-required`, interrupts con resume y approval gates humanos (steering); OAuth, DID, firmas y pagos (sin superficie en BAND); recruiter o descubrimiento fuera de la banda (ítem 9); varios builders compitiendo con voto (multiplica costo); orquestadores por turno (no pasan el delete test); métricas con LLM como juez (no reproducibles).

### De zero-pi (relevado el 27 sep 2026)

Paquete de flujo spec-driven para el agente pi (https://github.com/gonzalonicolasr/zero-pi): clarify → explore → plan → analyze → build → veredicto, cada fase como sub-agente de un orquestador. La arquitectura no se copia (orquestador por turno: falla el delete test); se toman reglas de proceso.

41. **Veredicto `REPLAN` separado de `REJECT`.** Si el defecto es la interpretación de la spec o el plan, no el código, el reviewer emite `REPLAN` dirigido al coordinador, no al builder; el coordinador corrige el plan (enmienda del ítem 16) y re-delega. Evita rondas de reparación sobre un plan equivocado. Fuente: veredicto `replantear` de `prompts/phases/veredicto.md`.
42. **Contador de rondas durable.** Las rondas de review de cada `task` se cuentan desde las líneas `STATE` del room, no desde la memoria del seat: un reinicio (regla 19) no devuelve el cupo de la regla 11. Fuente: `/zero-rounds` (`rounds.json`).
43. **Tope de re-planes.** El segundo `REPLAN` de una misma etapa la cierra como "no verificada" y se registra como resultado (ítem 9), en vez de seguir girando. Fuente: gate `analyze` ("the second replan stops blocked/not verified").
44. **Auditoría de calidad de tests.** El reviewer revisa los tests del builder además de correrlos: rechaza tautologías, loops que no afirman nada, tests solo de humo y asserts sobre detalles internos. Complementa los niveles de evidencia (ítem 31). Fuente: `prompts/support/strict-tdd-verify.md`.
45. **Disciplina de tokens del revisor.** En el mandate de quien revisa: no releer un archivo que no cambió desde la última lectura y buscar solo dentro del repo (nunca desde `/` o `~`); el revisor suele ser el seat más caro. No baja la vara del veredicto. Fuente: `veredicto.md`.
46. **Guard de proveedor en el preflight.** Verificar que cada seat de Claude Code corre con la suscripción Max y no con una API key paga (variable `ANTHROPIC_API_KEY` presente en el entorno del seat): el costo real cambia y el reporte también. Fuente: extensión `provider-guard`.
47. **Specs por etapa como deltas con IDs estables.** El coordinador describe cada etapa como `ADDED / MODIFIED / REMOVED / RENAMED` sobre los requisitos de la anterior; los `[C-nn]` conservan su ID entre etapas, y un requisito renombrado mantiene el ID. Hace trazable la regresión (ítem 13) y la extensión sin inflado. Fuente: `/zero-sync` y "Spec deltas" del README.

### Vocabulario único y última línea

Un enum por nivel; ningún otro término de veredicto en mandates ni mensajes.

| Nivel | Valores | Quién lo emite |
|---|---|---|
| Hallazgo `[C-nn]` | `CONFORMS` / `DEVIATES` | reviewer, auditor |
| Respuesta a un hallazgo | `ACCEPT` / `DISPUTE` / `CLARIFY` (ítem 28) | builder |
| Candidato (SHA) | `ACCEPT` / `REJECT` / `REPLAN` (ítem 41) / `INSUFFICIENT_EVIDENCE` / `BLOCKED` (reglas 12–13) | reviewer, breaker, auditor |
| Handoff | `working` / `input-required` / `completed` / `failed` / `refused` | todo seat |

Línea de protocolo, única y al final de cada handoff o veredicto (ítem 26); los campos que no aplican se omiten:

```
STATE <estado|veredicto> stage=N task=<key> sha=<sha> tree=<tree> refs=[#N@<sha>] prev=<sha256> brief=vN
NEXT @<handle> | DONE
```

Es la referencia de estado de la regla 5 y reúne lo que piden los ítems 4, 33, 36 y 39. El ACCEPT del builder a un hallazgo y el ACCEPT del reviewer a un candidato se distinguen por el nivel: el primero lleva `[C-nn]`, el segundo `sha=`.

### Instalación del plugin (28 sep)

`band plugin install` falla si `~/.claude/commands` es un symlink ("not a regular directory"). Se instaló desde lights-out con `claude plugin marketplace add /Applications/Band.app/Contents/Resources/claude-plugin-marketplace --scope local` y `claude plugin install band-peer@jam --scope local`: queda habilitado solo en este proyecto (`.claude/settings.local.json`) y `band preflight` pasa. Los seats tienen que arrancar en un directorio donde el plugin esté habilitado.

### Gotchas operativos de Jam (no están en las docs; los subcomandos existen en `band` 0.4.12, el comportamiento está sin probar)

- Una mención a un seat con el runtime parado es un no-op silencioso: `jam list` antes del dispatch es parte del preflight.
- `room send` devuelve 404 hasta que el humano es participante del room.
- `jam restart` no revive un peer parado, y Jam no recoge procesos `claude` huérfanos: revisarlos entre corridas.
- El timeout de una aprobación humana hace auto-deny: en la corrida final no puede quedar ningún permiso en modo manual.
- `jam plan set --snapshot` / `jam plan diagram` publican el plan en el room (re-ejecutar tras cada edición); `band usage agents|rooms|sessions|blocks` da tokens y USD estimados por agente local, por room y por sesión (basado en ccusage, no es facturación).
- Pegar la spec completa en cada handoff es obligatorio (guía oficial), pero en una corrida real (decenas de KB por mensaje, turnos de horas) disparó compactaciones de contexto y mensajes cruzados: se mitiga partiendo en mensajes numerados y cerrando el turno después de cada handoff, no dejando de pegarla.
- Los eventos `room_tasks` por WebSocket están detrás del flag `ff_room_tasks` y el SDK Python no los auto-une: nadie recibe push de cambios del board.
- Verificado en el caso chico (28 sep, `cases/small/RUN-1.md`): con la suscripción el seat necesita `--claude-context-mode local_config`, así que hereda `~/.claude` (hooks e instrucciones globales); `--claude-strict-mcp-config` deja solo el relay de Jam. Aislarlo más no se puede (1 oct): BAND solo deja pasar `--model`, `--fallback-model`, `--max-budget-usd` y `--autocompact` al runtime, así que `--setting-sources` no llega a Claude Code. `band restart` abre otra sesión de Claude Code con la misma identidad. `band usage` no atribuye esas sesiones al agente. Un seat puede dejar un server escuchando en el host después de su turno.
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

1. **Plantilla por rol**: Own / Do not / Use / Escalate / Done means. *Escalate* va al coordinador, nunca al humano durante una corrida (ver ítem 9). Incluye "no afirmar que los tests pasan sin haberlos corrido".
2. **Bloque anti-loop**: mencionar es llamar a una función; los acks van sin `@`; silencio después de un handoff; nada de "ready and waiting" o "standing by"; nombrar sin `@` a quien no tiene que actuar.
3. **Un turno por unidad de trabajo**: mandar el handoff y cerrar el turno; nunca seguir con la etapa siguiente en el mismo turno. Un seat publica su respuesta recién al cerrar el turno: turnos de 1–2 h produjeron respuestas con hasta 72 min de atraso, un handoff cruzado y una reparación delegada dos veces.
4. **Handoffs sin esperar respuesta**: un envío que bloquea esperando contestación, con un trabajo de más de 10 min del otro lado, dejó a un coordinador 74 min parado con 6 timeouts.
5. **Cada mensaje dice a qué estado responde** (campos `stage=` y `sha=` de la última línea, ver **Vocabulario único**); el receptor descarta en silencio lo anterior al último veredicto que conoce.
6. **Antes de pedir un handoff, mirar el board**: el handoff se registra también como transición de la tarea con el SHA.
7. **Un solo dueño de la reparación**: el REJECT va del reviewer al builder y el coordinador no re-delega.
8. **El coordinador no reenvía contenido**: el emisor le habla directo al destinatario. Antes de pasar un reporte, el coordinador lo verifica con un comando.
9. **Archivos con un solo dueño** (`notes/plan.md` del planner, `notes/review.md` del reviewer) para el detalle extra: evidencia, logs, diseño de aceptación. **No reemplazan** a la spec pegada en el handoff (ítem 15): los requisitos siempre van en el mensaje.
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
- **Jev de TypeSafe** (modelo "System One": decisiones tipadas con probabilidad calibrada, https://typesafe.ai/blog/introducing-system-one-models-and-jev), evaluado el 27 sep 2026: no puede ser seat (no es agente de código); clasificar veredictos y detectar seats colgados ya se resuelve determinista (ítem 26, watchdog sin LLM) y un número probabilístico choca con "todo número sale de un comando"; early access con waitlist desde el 26 sep, propietario, cifras autorreportadas. Candidato a guardrail barato fuera del hackathon.

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

## Decisiones pendientes (resolver en F1, casos chico y mediano)

1. **De dónde sale el número de tokens.** Resuelta el 28 sep (U5): la ventana de etapa sale de los transcripts, porque `band usage` solo filtra por fecha; `band usage sessions --agent` da la atribución seat → sesión y sus totales sirven de control cruzado (`tools/measure_cost.py`). `Emit.USAGE` es del SDK (`ClaudeSDKAdapter`) y nuestros seats son Claude Code con el plugin de Desktop; `room.json` no trae usage. Primera candidata (28 sep): `band usage agents` y `band usage rooms` (ccusage, tokens y USD estimados por agente y por room; falta ver si corta por ventana de etapa). Probar en el toy qué fuente da tokens por seat y por etapa, y publicarlo como `text` al cierre de cada etapa. Candidata verificada a medias (28 sep): los transcripts de Claude Code (`~/.claude/projects/<proyecto>/<sesión>.jsonl`) traen `timestamp` por línea y `message.usage` (input, output, cache read, cache creation) en las del asistente; un mensaje ocupa varias líneas con el mismo `message.id` (573 líneas para 297 ids en una sesión real), así que se suma una vez por id. Falta confirmar en el caso chico que los seats lanzados desde Desktop escriben ahí y que las dos fuentes coinciden (PLAN U5).
2. **Cómo se crean los seats.** Onboarding manual con `/jam` desde Desktop, script headless (ítem 21, comandos sin verificar) o seats SDK para OpenCode (Plan B/C). Elegir uno para la corrida final y documentarlo en `FACTORY.md`.
3. **Qué modelo va en el seat que verifica.** Resuelta el 28 sep para F1 (U2): builder `claude-opus-5-5`, coordinador y reviewer `claude-sonnet-5-5`; se sube el reviewer si el toy muestra que no alcanza. El setup sugiere modelos livianos en los que revisan, pero en la corrida analizada la review fue el cuello de botella y la verificación de caja negra encontró 4 de 5 defectos. Diversidad de modelo sí (ítem 6); modelo más débil en quien verifica, solo si el toy muestra que alcanza. El 30 sep, el reviewer pasa a pedir dos reviews independientes en paralelo por candidato, un subagente `claude-sonnet-5-5` y `codex exec` con `gpt-5.6-terra` (suscripción de ChatGPT), y las consolida: un `DEVIATES` de cualquiera de las dos rechaza solo si el reviewer lo confirma. Así el ítem 6 se cumple con otro proveedor, no solo otro modelo.
4. **Qué seats suma la fábrica además de los tres base.** El toy arranca con coordinador (también planifica: parte la spec en tareas del board y lleva el log de enmiendas), builder y reviewer. Candidatos, en orden de prioridad:
   - **Verificador de caja negra (breaker)**, idealmente en otro proveedor (Plan B/C): prueba casos extremos y la checklist adversarial contra el servicio corriendo, con poder de veto. Es donde salieron 4 de 5 defectos en la corrida analizada. Se suma si en el toy se escapan defectos que el reviewer no ve.
   - **Auditor de spec** (ítem 24): solo lectura, matriz spec → código → check, detecta faltantes y extras, doble firma de cierre de etapa. Se suma si el cupo lo permite después del breaker.
   - **Seat de ambientes (`environment`): sumado el 29 sep** tras la corrida 3 del caso chico, donde el builder levantó el runtime de contenedores compartido y lo apagó al terminar, y el reviewer se quedó sin daemon. Es dueño del runtime y de los puertos del host: los prepara antes de la primera etapa, los repone si un seat no los alcanza y al final verifica que no quede nada de la corrida. No construye ni verifica el producto; los demás seats nunca arrancan ni apagan un servicio compartido (regla del bloque común).
   - **Planner separado: descartado por ahora.** No es el cuello de botella (la review sí), suma cupo y un salto por handoff, y un pipeline fijo de roles puntúa bajo con los jueces. Solo se reconsidera si el toy muestra al coordinador saturado, y en ese caso con un plan que el reviewer o el breaker puedan rechazar antes de construir.
5. **Repo del entregable y quién pushea.** BAND no integra GitHub ni guarda archivos: solo lleva mensajes. Los seats corren en la Mac (Claude Code con `band-peer`) y usan `git` con las credenciales locales; en el room viajan referencias (`stage=` y `sha=` en la última línea). El entregable vive en un **repo público nuevo** creado para la corrida final; `lights-out` queda como workspace (plan, docs, ensayos). El coordinador es el único que pushea, después del ACCEPT de cada etapa (resuelto el 28 sep en U2), así el historial muestra un push por etapa y nunca un candidato sin aceptar. No hay CI ni deploy: el release check del reviewer (ítem 5) cumple ese papel. Si los seats se crean con script (ítem 21), el `remote` y los permisos de push quedan configurados antes del dispatch. Ningún seat imprime tokens de GitHub en la salida de un tool: quedarían en `room.json`.

---

## Plan

| Cuándo | Qué |
|---|---|
| sáb 26 – dom 27 sep | Inscribirse en lablab. Crear cuenta BAND, instalar Desktop + CLI + plugin, readiness check. Unirse a los dos Discord. Leer las specs completas. Track elegido: **tablekeeper** (26 sep) |
| lun 28 – mar 29 sep | F0 y F1: diseñar la fábrica con el alcance de F1 (roles, mandates, protocolo de handoff y review). Correr el caso chico y después el **toy** completo en modo aislado; medir tiempo, tokens y cupo. Resolver Decisiones pendientes 1–5 |
| mié 30 sep – vie 2 oct | Iterar sobre el track real: etapas 1–4, ajustar mandates según las fallas. Vie 2 oct: **congelar mandates** (hashes SHA-256) |
| sáb 3 oct | **Corrida final**: room y repo nuevos, autónoma, al inicio de una ventana de cupo |
| dom 4 oct | `harness check` + suites en modo aislado. Descargar `room.json` a mano de la console de Band (**Download full session**; no hay comando) y redactar credenciales. Validador post-run. **Toy de cierre** con los mandates congelados, en paralelo (evidencia de genericidad, ítems 14 y 35). Escribir README y FACTORY.md a mano. Ficha con `hackathon-submission` |
| lun 5 oct | Deck (`hackathon-deck`, después de la ficha para no contradecirla) y video. Enviar el formulario antes de la noche (cierre mar 6 oct 03:59 ART) |

---

## Checklist de entrega

- [ ] Inscripto en lablab, con Discord conectado y equipo propio creado como admin (sin eso *Submit Project* queda gris)
- [ ] 3+ seats, cada uno con `mandates/<seat>.md` que empieza con `Harness:` / `Model:`
- [ ] Mandates sin vocabulario del track
- [ ] `@handle` recíprocos visibles en el room
- [ ] Corrida final en room y repo nuevos, sin intervención después del dispatch
- [ ] Mac enchufada, despierta (`caffeinate -dimsu`) y con red estable durante toda la corrida; sin otra carga pesada en paralelo
- [ ] Repo público del entregable creado, con `remote` y push configurados antes del dispatch
- [ ] `stage-1..4/` con `Dockerfile` + `RUN.md`, cada una copia extendida de la anterior, sin `.git` anidado
- [ ] Ninguna línea de código escrita a mano en `stage-N/`
- [ ] Suites en `--mode isolated` corridas por etapa; `harness check` limpio
- [ ] `room.json` sin editar, salvo credenciales redactadas con `[REDACTED]` y registradas en `evidence/PACKAGING.json` (redactar ya es editar)
- [ ] `README.md` y `FACTORY.md` escritos a mano: diseño, costo, falla atrapada, etapa alcanzada
- [ ] Repo público, clonable sin cuenta de BAND
- [ ] Cada `stage-N/` sirve en `0.0.0.0:$PORT` (8080), `/health` → `{"status":"ok"}` en ≤ 30 s, `POST /_test/reset` → 204
- [ ] `docs/DESIGN.md` declarado en `FACTORY.md` como insumo del dispatch
- [ ] Video `.mp4`/`.mov` **subido**, de 3 a 4:30 min, con la **grabación del room** (sin ella, descalificación), un handoff y el servicio funcionando
- [ ] Deck en **PDF** de 8–10 slides
- [ ] Formulario de lablab enviado antes del **mar 6 oct 03:59 ART**
