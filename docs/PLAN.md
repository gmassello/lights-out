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

21. **Script de lanzamiento idempotente (bash).** Crea los seats con `jam agent create --transport claude-code-cli --runtime-auth subscription --runtime-model <id> --instructions-file mandates/<seat>.md`, arma el room con `jam chat new` / `jam chat add`, guarda estado en un archivo ignorado por git, falla si el `Model:` del mandate no coincide con el modelo real del seat y tiene un flag para forzar room nuevo en la corrida entregada. Verificar los flags contra nuestra versión de Jam.
22. **Validador post-run.** Cruza `room.json` ↔ tasks ↔ commits: cada etapa cerrada tiene veredicto con SHA, cada SHA existe en el historial y cada rechazo tiene su reparación. Falla si queda algo huérfano.
23. **Paquete de verificación final.** Clon público fresco → `harness check` → `harness run --all --mode isolated` → `evidence/verification-receipt.json` con comandos, exit codes y tiempos. `evidence/PACKAGING.json` con sha256, bytes y `exportedAt` de `room.json` y `"edited": false`. Audit de symlinks, gitlinks, `.git` anidado, credenciales en todo el historial y vocabulario del track en mandates.
24. **Seat Spec Auditor** (opcional, suma un seat y costo). Solo lectura: matriz spec → código → check, busca faltantes y también extras no pedidos, firma por etapa y no por ítem para no llenar el room. El cierre de etapa requiere doble firma (verifier + auditor).
25. **Ensayo general sobre el toy con criterios de aceptación de la fábrica.** Ruteo autónomo sin handles en el brief; al menos un rechazo que vuelve al builder (si no ocurre solo, se inyecta un bug a propósito); la fábrica sobrevive a un reinicio sin crear identidades nuevas; swim lanes grabables para el video.

### Gotchas operativos de Jam (no están en las docs)

- Una mención a un seat con el runtime parado es un no-op silencioso: `jam list` antes del dispatch es parte del preflight.
- `room send` devuelve 404 hasta que el humano es participante del room.
- `jam restart` no revive un peer parado, y Jam no recoge procesos `claude` huérfanos: revisarlos entre corridas.
- El timeout de una aprobación humana hace auto-deny: en la corrida final no puede quedar ningún permiso en modo manual.
- `jam plan set --snapshot` / `jam plan diagram` publican el plan en el room (re-ejecutar tras cada edición); `jam usage` da el consumo.
- Pegar la spec completa en cada handoff (decenas de KB por mensaje) dispara compactaciones de contexto y mensajes cruzados entre etapas.

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
