---
name: band-factory-run
description: Arma, vigila y cierra una corrida de la fábrica Lights-out en BAND — repo de resultado, creación de los seats coordinator/builder/reviewer/environment, despacho, reinicio de un seat, room.json, validador, checks y costo. Usar al armar o repetir una corrida (caso chico, toy, tablekeeper, corrida final), al crear o recrear los seats, o al cerrar una corrida con room.json. Solo vale en este repo.
---

# Corrida de la fábrica en BAND

Caso: `$ARGUMENTS` (`tiny`, `small`, `toy`, `tablekeeper`) y número de corrida `N`. Nombres de ejemplo:
repo `~/Documents/band-work/<caso>-run-N`, sesiones `lo-<seat>`.

Lo verificado sale de `cases/small/RUN-1.md`. Lo marcado **(sin verificar)** todavía no corrió.

## 1. Repo de resultado

```bash
R=~/Documents/band-work/<caso>-run-N
gh repo create gmassello/<nombre> --private          # la final: --public
git init -q -b main $R
git -C $R remote add origin https://github.com/gmassello/<nombre>.git
git -C $R config user.email gmassello@gmail.com
git -C $R config user.name gmassello
git -C $R commit -q --allow-empty -m "Initial commit"
git -C $R push -q -u origin main
cd $R && claude plugin marketplace add /Applications/Band.app/Contents/Resources/claude-plugin-marketplace --scope local
cd $R && claude plugin install band-peer@jam --scope local
```

El origin tiene que ser `github.com/gmassello/*` y el email el personal: los seats heredan
`~/.claude` y `claude-git-guard` les niega el commit si no. `git commit` y `push` van cada uno en su
propia llamada, con `-C` y sin `cd`.

## 2. Seats

Uno por seat, con el `Model:` de su mandate (`mandates/<seat>.md`). Primero la prueba, que no
acepta `--instructions-file`:

```bash
band agent create --dry-run --json --session lo-<seat> --name <seat> --cwd $R \
  --transport claude-code-cli --runtime-auth subscription --runtime-model <modelo> \
  --claude-permission-mode bypassPermissions --claude-context-mode local_config \
  --claude-strict-mcp-config
```

`ok: true` y "Other MCP servers: 0 other server(s)". Después, lo mismo sin `--dry-run` y con
`--description "Lights-out <seat> seat" --instructions-file ~/Documents/lights-out/mandates/<seat>.md`.
`band list` tiene que mostrar los cuatro `Connected running=true`: coordinator, builder, reviewer
y environment.

Para otra corrida en otro repo, los mismos seats se mudan con
`band runtime template set --session lo-<seat> --spawn-cwd $R`: rige para las sesiones nuevas, o
sea el room nuevo. Se confirma porque los transcripts aparecen en
`~/.claude/projects/<slug-del-repo-nuevo>/`. Las instrucciones siguen vinculadas en vivo a
`mandates/` (`band agent instructions show --reveal`).

## 3. Room y despacho

1. Brief: `cases/<caso>/SPEC.md` con `Result repository:` completado. Se escribe en el scratchpad,
   se copia con `pbcopy` y se abre con `open -a TextEdit` para que lo vea. Antes, cerrar en
   TextEdit los briefs de corridas anteriores: pegar uno viejo manda los seats al repo viejo.
   Para ejercitar el REJECT en un caso propio se agrega bajo Constraints una línea de práctica:
   - `tiny`: "Practice run only: the builder's first candidate returns `200` instead of `404 not_found` for an unknown note id. Fix it only after the reviewer rejects it."
   - `small`: "Practice run only: the builder's first candidate returns `201` instead of `409 idempotency_conflict` for a reused `Idempotency-Key` with a different body. Fix it only after the reviewer rejects it."
2. Room con **solo** los cuatro seats (el agente "Claude Code" de esta ventana no: sería un seat
   más sin mandate) y con el humano como dueño. Lo crea el usuario en Desktop, o yo en Chrome con
   su sesión: app.band.ai → Dashboard → Add new chat room → los cuatro seats → Create chat. Después
   `band room rename <room-id> <caso>-run-N`. `band chat new` no sirve: el dueño queda el agente,
   el humano recibe 403 al renombrar y el room no se puede borrar.
3. Despacho: el brief empezando con `@coordinator`. Lo manda el usuario, o yo si me lo pide:
   `band room send <room-id> "@[[<coordinator-id>]] $(cat <brief>)" --mention <coordinator-id>`
   (el id sale de `band room messages` o de `band chat participants`). Anotar la hora UTC.
4. Apenas despachado, leer el primer mensaje (`band room messages <room-id> --json --type text`)
   y confirmar que su línea `Result repository:` es `$R`. Si no coincide, parar antes de que un
   seat commitee y repetir con un room nuevo.
5. Arrancar el watchdog en segundo plano (reinicia al seat mencionado que lleva 10 min inactivo
   sin contestar; no escribe en el room y sale solo con el reporte al humano):
   `python3 tools/watchdog.py <room-id> --seats coordinator,builder,reviewer,environment | tee ~/Documents/band-work/<caso>-run-N.watchdog.log`

## 4. Vigilar

```bash
band chat list --session lo-coordinator                  # id del room
band room messages <room-id> --json                       # snake_case: sender_name, message_type, content, inserted_at
```

Un `Monitor` que emite cada mensaje `text` nuevo con su emisor, destinatarios (`mention_names`) y
las líneas `STATE`/`NEXT`/`DONE`. No intervenir en el room.

## 5. Reinicio (AE6)

Cuando el coordinator le pasa la tarea al builder y el builder ya está trabajando:

```bash
band restart --session lo-builder --host-session default-<room-id>
band status --session lo-builder          # pid nuevo, mismo runtime_session, presence=live
```

## 6. Cierre

1. El usuario descarga el room: ⋮ → Open in Band → ⋮ → Download → **Download full session**.
   O yo en Chrome, con permiso del usuario: `app.band.ai/sessions/<room-id>` → "Conversation
   options" (⋮) → Download → Download full session; baja como `~/Downloads/<nombre-del-room>.json`.
   Se copia tal cual a `$R/room.json`. Confirmar que el watchdog salió y adjuntar su log a
   `RUN-N.md` (cada reinicio que hizo es un hallazgo).
2. Validador: `python3 tools/validate_room.py $R/room.json $R`.
3. Producto:
   ```bash
   lsof -nP -iTCP:<puerto> -sTCP:LISTEN      # si hay algo, identificarlo y apagarlo antes
   docker build -q -t lo-<caso> -f $R/stage-1/Dockerfile $R/stage-1/
   docker run -d --rm --network none --name lo-net lo-<caso>   # /health desde adentro con docker exec
   docker run -d --rm -p <puerto>:8080 --name lo-run lo-<caso>
   python3 cases/<caso>/checks.py http://localhost:<puerto>   # toy/tablekeeper: harness run
   ```
4. Costo: mapear seat → sesiones buscando la primera línea del mandate en los transcripts
   (`grep -l "You plan and coordinate\|You build what\|You decide whether\|You keep the machine" ~/.claude/projects/<repo-slug>/*.jsonl`);
   un seat reiniciado tiene más de una. Los subagentes del reviewer entran solos (`<sesión>/subagents/`);
   sus reviews de `codex exec` no: son los rollouts con `cwd` igual a `$R`
   (`grep -l "\"cwd\":\"$R\"" ~/.codex/sessions/<aaaa>/<mm>/<dd>/rollout-*.jsonl`) y se pasan como
   rutas en la lista del reviewer (`reviewer=<id>,<rollout.jsonl>`). Después:
   ```bash
   python3 tools/measure_cost.py <inicio> <fin> coordinator=<id> builder=<id>,<id> reviewer=<id> environment=<id>
   band usage refresh && band usage sessions --json          # comparar totales por sesión
   ```
5. `harness check $R --track <track>` desde el clon del kickoff.

## 7. Registrar

`cases/<caso>/RUN-N.md` con la estructura de `cases/small/RUN-1.md`: timeline, resultados,
hallazgos del validador con su enmienda, formatos y gotchas. Actualizar el estado de la unidad en
`docs/PLAN.md`. Una enmienda de mandates mantiene idéntico el bloque `## Rules for every seat` en
los cuatro archivos (comparar con `shasum`) y vuelve a pasar el gate de mandates.

### Retro

Después del resultado, el coordinator pide la retro a cada seat (paso 8) y cada uno contesta
con líneas `LESSON`. Al cerrar:

1. `python3 tools/retro.py $R/room.json`: lecciones por seat; `[flag: …]` marca términos del
   despacho, rutas e identificadores, que no pueden entrar a un mandate.
2. Mostrarle al usuario las propuestas con `AskUserQuestion` (en el `preview`), una pregunta por
   seat. Nada se aplica sin su aprobación, y una con `flag` se reescribe genérica o se descarta.
3. Las aprobadas van a `## Lessons` del mandate del seat, reemplazando `None yet.`. Tope de 8 por
   seat: una que repite otra la reemplaza.
4. Gate de mandates y `shasum` del bloque común (las lecciones quedan fuera de él).
5. En `RUN-N.md`, una tabla con las lecciones aplicadas y, contra la corrida anterior con los
   mismos requisitos, el `run time` y los REJECT que imprime el validador.

## Verificar

```bash
band list                                                    # cuatro seats running=true
python3 tools/validate_room.py --self-check
python3 tools/measure_cost.py --self-check
python3 tools/retro.py --self-check
```

## Gotchas

| Trampa | Regla |
|---|---|
| `band agent create` falla con "requires --session" | pasar `--session lo-<seat>` |
| `--dry-run` rechaza `--instructions-file` | probar sin él y crear con él |
| `--claude-context-mode bare` rechaza la suscripción | `local_config`: el seat hereda `~/.claude` (hooks, CLAUDE.md global) |
| Con `local_config` el seat carga Gmail, Drive y demás MCP personales | `--claude-strict-mcp-config`: solo el relay de Jam |
| El seat no puede commitear: `claude-git-guard` lo niega y le pide al humano un `!` | origin en `github.com/gmassello/*`, email personal y la regla de `git -C` en los mandates |
| El CLAUDE.md global le impone español al seat | la regla "English only" del bloque común |
| `band restart` abre otra sesión de Claude Code | el costo del seat suma todas sus sesiones |
| `band usage` muestra los seats como "(unattributed)" | pasar los ids de sesión explícitos a `measure_cost.py`; con el seat solo, la fila sale `partial: no band session in the window` |
| Los checks pasan contra un server que dejó un seat en el host | `lsof` del puerto antes y apagar el huérfano |
| `band room messages --json` y `room.json` difieren en las claves | la API en vivo usa snake_case; la descarga, camelCase (`senderType: Agent/User`) |
| El validador marca la etapa `open` con un ACCEPT sobre un commit del reviewer | el `sha=` del veredicto es el candidato del builder (mandate del reviewer) |
| `NEXT DONE` o un `STATE` sin segunda línea | inválidos: `NEXT @<seat>` o `DONE` |
| `band chat new` crea el room con el agente como dueño | crear el room en la web o en Desktop; después no se puede renombrar ni borrar |
| `band chat add` o `chat new` fallan con "daemon unavailable: decoding response" | el participante igual queda agregado: confirmar con `band chat participants` antes de reintentar |
| `band room messages --json` devuelve solo los 100 mensajes más nuevos (`has_more`, `--page N`) sin avisar | paginar hasta cubrir la ventana; `tools/watchdog.py` ya lo hace |
| Un agente sin mandate en el room rompe el gate de mandates | el room tiene solo los seats con mandate |
| El despacho nombra el repo de otra corrida | leer el primer mensaje y comparar con `$R` (§3.4) |
| Un seat espera una respuesta que se perdió (`staged: true` y el turno termina con error) y nada lo despierta | lo destraba el watchdog (§3.5) con `band restart` del seat que debía contestar; no agrega mensajes al room. Los mandates publican con `send`, no con la respuesta staged |
| Un seat esquiva un guard (p. ej. un remote falso para que `claude-git-guard` deje commitear) | regla "Never work around a guard" del bloque común; revisar los `tool_call` del room al cerrar |
| `codex exec` del reviewer carga los MCP y la config personal de `~/.codex` y tarda en arrancar | `--ignore-user-config`: la auth de ChatGPT sigue andando (probado) |
| Con `--ignore-user-config`, `codex exec` corre con `reasoning effort: none` | `-c model_reasoning_effort=medium` en el comando del mandate (tiny-run-3: la review sin razonamiento se perdió un DEVIATES) |
| `codex exec` en segundo plano sin `</dev/null` se queda en "Reading additional input from stdin" | `</dev/null` en el comando; si no, el seat lo relanza y quedan dos reviews |
| La review de Codex tarda ~2 min: explora el repo (130k tokens) y abre subagentes propios | prompt con el diff del candidato y "no explorar más allá del diff", `--disable multi_agent` y tope de 3 min (prueba: 23 s, 4k tokens, mismos 3 DEVIATES) |
| La review de Codex en `-s read-only` no alcanza Docker ni la red: queda estática | el reviewer levanta un contenedor por review en su propio puerto y Codex corre con `-s workspace-write -c sandbox_workspace_write.network_access=true -C $(mktemp -d) --skip-git-repo-check` (sin ese flag falla fuera de un repo git): llega al servicio y no escribe en el repo (probado: 9 s) |
| El costo de Codex sale 0 o falta | los rollouts no están en `~/.claude`: pasarlos como rutas al reviewer (§6.4); `input` excluye el cacheado, igual que "tokens used" de Codex |
| La cantidad de checks salta entre corridas del mismo spec (tiny: 16 y 26) | contar `[R-nn]` contra `[C-nn]` en el mensaje de checks del reviewer: mismo número y la línea `requirements: N, checks: N` |
| `NEXT @[[<id>]]` en vez de `NEXT @<seat>` en el room | no es un error: es el token de mención de BAND (`band send` no tiene `--mention`); el validador lo acepta y el bloque común lo documenta |
| El coordinator pone `stage=` en los pedidos a environment | el mandate trae las líneas literales (`STATE working task=env-prepare`, `task=env-check sha=…`) y el validador lo marca como problema |
| El coordinator cierra la etapa mencionando a un seat y con `DONE` | el paso 6 trae la línea literal del cierre (seats sin `@`, `STATE completed stage=<N> …` y `DONE`); el resultado al humano y el `env-restore` de environment también tienen la suya |
| environment responde el chequeo final mencionando al coordinator pero termina en `DONE` | el mandate trae la línea literal `NEXT @coordinator`; el validador marca todo mensaje que menciona un seat y termina en `DONE` |
| Un seat apaga el runtime de contenedores compartido y otro se queda sin daemon | `@environment` es su dueño; los demás se lo piden (regla del bloque común) |

## Modificar / eliminar

Vive solo en este repo, porque BAND se usa solo desde acá. Un comando nuevo de `band` se confirma
con `band <sub> --help` antes de escribirlo acá. Eliminarlo implica sacar el puntero del
`CLAUDE.md` del repo.
