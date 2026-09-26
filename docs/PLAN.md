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
