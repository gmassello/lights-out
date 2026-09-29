---
name: band-factory-run
description: Arma, vigila y cierra una corrida de la fábrica Lights-out en BAND — repo de resultado, creación de los seats coordinator/builder/reviewer, despacho, reinicio de un seat, room.json, validador, checks y costo. Usar al armar o repetir una corrida (caso chico, toy, tablekeeper, corrida final), al crear o recrear los seats, o al cerrar una corrida con room.json. Solo vale en este repo.
---

# Corrida de la fábrica en BAND

Caso: `$ARGUMENTS` (`small`, `toy`, `tablekeeper`) y número de corrida `N`. Nombres de ejemplo:
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
`band list` tiene que mostrar los tres `Connected running=true`.

Los seats ya creados quedan atados a su `--cwd`. Para otra corrida en otro repo, crear seats nuevos
o cambiar el cwd **(sin verificar: `band agent` no tiene subcomando de edición de cwd)**.

## 3. Room y despacho (los hace el usuario)

1. Brief: `cases/<caso>/SPEC.md` con `Result repository:` completado. Se escribe en el scratchpad,
   se copia con `pbcopy` y se abre con `open -a TextEdit` para que lo vea.
2. El usuario crea el room en Desktop con **solo** los tres seats (el agente "Claude Code" de esta
   ventana no: sería un cuarto seat sin mandate).
3. El usuario pega el brief empezando con `@coordinator` y lo manda. Anotar la hora UTC.

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
   Se copia tal cual a `$R/room.json`.
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
   (`grep -l "You plan and coordinate\|You build what\|You decide whether" ~/.claude/projects/<repo-slug>/*.jsonl`);
   un seat reiniciado tiene más de una. Después:
   ```bash
   python3 tools/measure_cost.py <inicio> <fin> coordinator=<id> builder=<id>,<id> reviewer=<id>
   band usage refresh && band usage sessions --json          # comparar totales por sesión
   ```
5. `harness check $R --track <track>` desde el clon del kickoff.

## 7. Registrar

`cases/<caso>/RUN-N.md` con la estructura de `cases/small/RUN-1.md`: timeline, resultados,
hallazgos del validador con su enmienda, formatos y gotchas. Actualizar el estado de la unidad en
`docs/PLAN.md`. Una enmienda de mandates mantiene idéntico el bloque `## Rules for every seat` en
los tres archivos (comparar con `shasum`) y vuelve a pasar el gate de mandates.

## Verificar

```bash
band list                                                    # tres seats running=true
python3 tools/validate_room.py --self-check
python3 tools/measure_cost.py --self-check
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
| `band usage` muestra los seats como "(unattributed)" | pasar los ids de sesión explícitos a `measure_cost.py` |
| Los checks pasan contra un server que dejó un seat en el host | `lsof` del puerto antes y apagar el huérfano |
| `band room messages --json` y `room.json` difieren en las claves | la API en vivo usa snake_case; la descarga, camelCase (`senderType: Agent/User`) |
| El validador marca la etapa `open` con un ACCEPT sobre un commit del reviewer | el `sha=` del veredicto es el candidato del builder (mandate del reviewer) |
| `NEXT DONE` o un `STATE` sin segunda línea | inválidos: `NEXT @<seat>` o `DONE` |
| Un cuarto agente en el room rompe el gate de mandates | el room tiene solo los seats con mandate |

## Modificar / eliminar

Vive solo en este repo, porque BAND se usa solo desde acá. Un comando nuevo de `band` se confirma
con `band <sub> --help` antes de escribirlo acá. Eliminarlo implica sacar el puntero del
`CLAUDE.md` del repo.
