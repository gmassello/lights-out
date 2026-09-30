# Code review — cierre de environment con `DONE` (30 sep 2026)

## Alcance

Esta review cubre el diff sin commitear sobre `8d32664`, con esfuerzo xhigh. Toca cuatro archivos:

- `mandates/environment.md`: líneas literales `NEXT @coordinator` en los pasos 1 y 3.
- `tools/validate_room.py`: problema nuevo "mentions a seat but ends with DONE".
- `cases/tiny/RUN-3.md`: hallazgo registrado.
- `.claude/skills/band-factory-run/SKILL.md`: gotcha nuevo.

Método:

- Se corrieron el validador de `HEAD` y el nuevo sobre los 8 `room.json` de `~/Documents/band-work`.
- Se hicieron pruebas de mutación sobre `--self-check`.

Los hallazgos 1, 2, 3 y 4 se confirmaron ejecutando el código.

## Hallazgos

| # | Severidad | Archivo | Hallazgo | Escenario de falla | Propuesta |
|---|---|---|---|---|---|
| 1 | alta | `tools/validate_room.py:63` | El `continue` después del problema de DONE saca el mensaje de `parsed`. Un ACCEPT válido que menciona un seat y termina en `DONE` deja de cerrar la etapa y de reparar el REJECT. | Sala base con el ACCEPT final `@[[c]] … STATE ACCEPT stage=1 sha=good / DONE`. Da "stages closed 0/1, rejections repaired 0/1, problems 3", con "stage 1: open" y "REJECT … has no repair" falsos. | Registrar el problema sin `continue`. |
| 2 | alta | `tools/validate_room.py:147` | Los casos "self-accept" y "missing sha" terminan en `@[[c]] … DONE`. La regla nueva los atrapa antes que la guarda de autor y la de `commit_exists`, así que el self-check pasa por el motivo equivocado. | Mutación: quitar la guarda de autor y `commit_exists` deja `--self-check` en ok, exit 0. `docs/PLAN.md:66` afirma que ignorar al autor lo hace fallar. Las pruebas de AE3 y AE10 quedan vacías. | Casos del self-check con `NEXT @…` correcto. Comprobar el texto del problema esperado, no solo la cantidad. |
| 3 | media | `tools/validate_room.py:61` | La regla nueva va antes y termina en `continue`, así que tapa el chequeo de `stage=` en environment y los de veredicto y sha. | tiny-run-1 #220, tiny-run-2 #215 y small-run-5 #257 reportaban "environment message with stage=". Ahora solo reportan la regla nueva. | Se arregla con el hallazgo 1: acumular problemas sin cortar. |
| 4 | alta | `mandates/environment.md:34` y `tools/watchdog.py` | El paso 1 pide publicar el registro inicial sin nombrar a ningún seat y terminado en `DONE`. Eso es justo lo que `watchdog.finished()` toma como resultado de la corrida. | `finished([registro env sin menciones con DONE])` devuelve True. En una corrida que cumpla el mandate, el watchdog sale antes de la etapa 1 y deja de reiniciar seats silenciosos. En las corridas hechas no pasó porque environment metió el registro en su respuesta al coordinator. | El watchdog sale solo con un `DONE` sin mención del coordinator, que es el único que cierra la corrida. |
| 5 | media | `mandates/environment.md:38` | El paso 2 (responder al seat que reporta el runtime caído) sigue sin línea de protocolo. Es la misma brecha que el diff arregla en el paso 3. | environment contesta a `@builder` y cierra con `DONE`. La regla nueva lo marca y el mandate no dice qué línea usar. | Línea literal `STATE completed task=env-restore` / `NEXT @<seat que reportó>`. |
| 6 | media | `tools/validate_room.py:61` | La última línea se recalcula con `content.strip().splitlines()[-1]`. `protocol()` descarta las líneas con ` ``` ` y las vacías, así que los dos criterios divergen. | Un mensaje con mención que termina `… / DONE / ``` ` pasa `protocol()` con NEXT=DONE, pero la regla nueva ve ` ``` ` y no lo marca. | Devolver `next` desde `protocol()` y comparar `line["next"] == "DONE"`. |
| 7 | media | `tools/validate_room.py:152` | Falta el caso negativo: un mensaje con STATE y DONE sin mención, que es la forma que el mandate exige para el registro inicial. El caso nuevo tampoco comprueba el texto del problema. | Mutación: borrar `addresses and` (marcar todo DONE) deja el self-check en ok. | Agregar ese caso esperando 0 problemas y comprobar el texto. |
| 8 | media | `cases/tiny/RUN-3.md:79`, `cases/small/RUN-2.md:26`, `cases/small/RUN-3.md:32`, `docs/PLAN.md:66` | La regla cambia cifras publicadas y no se actualizaron todos los lugares donde aparecen (regla "Todo número publicado sale de un comando"). | small RUN-2 y RUN-3 publican "exit 0 … 0 problems". Hoy dan exit 1: el cierre de etapa del coordinator (#132, #229) menciona al reviewer y termina en DONE. tiny-run-1 pasa de 3 a 4 problemas. | Volver a correr el validador sobre todos los rooms y actualizar cada cifra, o anotar que la regla es posterior a la corrida. |
| 9 | baja | `tools/validate_room.py:61` | Parche de altura baja: solo detecta "mención + DONE". El invariante del bloque común es que el seat mencionado sea el que nombra `NEXT`. | Un mensaje que menciona a @reviewer y termina `NEXT @builder` rompe la misma regla y pasa limpio. | Comparar el seat mencionado con el de `NEXT` (dentro de la función única del hallazgo 10). |
| 10 | media | `tools/watchdog.py:46` | "DONE con o sin mención" se decide en dos herramientas con criterios distintos (regla "Un solo lugar decide"). | validate_room detecta la mención por `@[[id]]` en el contenido y descarta ` ``` `. watchdog usa `mention_names` y `last_line` sin descartarlos. Un mismo mensaje puede recibir veredictos distintos. | Una función pura compartida para el cierre de la corrida, usada por las dos herramientas. |
| 11 | baja | `tools/validate_room.py:54` | `addresses` busca `@[[id]]` en todo el contenido, incluida la salida de comandos pegada. | environment pega la salida de `band room messages` con un `@[[<coordinator-id>]]` en su registro sin mención con DONE, y queda marcado. | Buscar el token fuera de los bloques de código, o usar la metadata de menciones cuando está disponible. |
| 12 | baja | `mandates/environment.md:45` | `sha=<sha>` en el paso 3 no dice cuál. El validador corre `commit_exists` sobre ese sha. | Si environment pone un sha de otro clon o de la imagen, aparece "sha … is not a commit" y la corrida sale con exit 1. | Escribir "the sha from the coordinator's request". |
| 13 | baja | `tools/validate_room.py:167` | La lista de casos del print del self-check está escrita a mano y repite las claves de `cases`. | Cada caso nuevo obliga a editar dos lugares, y el mensaje puede anunciar casos que no corrieron. | `", ".join(cases)`. |

## Arreglo propuesto

1. **Validador:**
   - `protocol()` devuelve `next`.
   - Los problemas se acumulan sin descartar el mensaje (hallazgos 1, 3, 6).
   - Self-check con casos limpios, caso negativo, texto del problema comprobado y print generado desde `cases` (hallazgos 2, 7, 13).
2. **Una función pura "fin de corrida"** compartida por validate_room y watchdog: `DONE` sin mención de un seat, enviado por el coordinator. Sirve de base para comparar la mención con `NEXT` (hallazgos 4, 9, 10, 11).
3. **Mandates:**
   - Líneas literales en el paso 2 de environment y en el cierre de etapa del coordinator.
   - El sha de environment es el del pedido del coordinator (hallazgos 5, 12).
4. **Docs:** volver a correr el validador sobre los 8 rooms y actualizar las cifras de `cases/*/RUN-*.md` y `docs/PLAN.md` (hallazgo 8).

## Estado

Sin aplicar. El diff revisado sigue sin commitear.
