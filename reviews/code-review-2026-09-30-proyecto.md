# Code review — proyecto completo (30 sep 2026)

## Alcance

- **Qué se revisó:** con esfuerzo xhigh, el código del proyecto (`tools/`, `cases/*/checks.py`), el diff sin commitear sobre `8d32664` y los mandates.
- **Qué se corrió:** los tres `--self-check` pasan, y el validador se corrió sobre los 8 `room.json` de `~/Documents/band-work`.
- **Cómo se confirmó cada hallazgo:**
  - del 1 al 9, del 11 al 13 y el 16 se confirmaron ejecutando el código;
  - el 10 sale de comparar las cifras publicadas con lo que el validador da hoy;
  - el 14 y el 15 se leyeron contra el spec y las reglas, sin ejecutar.
- **Relación con la review anterior:** los hallazgos 2, 8, 11 y 12 se superponen con `reviews/code-review-2026-09-30-env-done.md`.

## Hallazgos

| # | Severidad | Archivo | Hallazgo | Escenario de falla | Propuesta |
|---|---|---|---|---|---|
| 1 | alta | `tools/validate_room.py:101` | La búsqueda de la reparación de un REJECT lee `e[3]["sha"]` de cualquier mensaje parseado que venga después. Si ese mensaje no tiene `sha=`, tira `KeyError`, y `main()` solo atrapa `OSError` y `ValueError`. | Un REJECT seguido de `STATE working stage=1 task=t` sin sha (el update del builder o el `unanswered wait`): el validador aborta con traceback y la corrida queda sin veredicto. Reproducido. | Usar `e[3].get("sha")` y exigirlo en la condición de reparación. |
| 2 | alta | `tools/validate_room.py:63` | El `continue` de "mentions a seat but ends with DONE" saca el mensaje de `parsed`, y como va antes, tapa los chequeos de `stage=` en environment, de veredicto sin sha y de `commit_exists`. | Un ACCEPT válido que termina en DONE da "stages closed 0/1", "stage 1: open" y "REJECT … has no repair" falsos. En tiny-run-1 #220 y small-run-5 #257 el problema de `stage=` queda oculto. | Registrar el problema sin `continue`. |
| 3 | alta | `tools/watchdog.py:46` | `finished()` da la corrida por terminada con cualquier mensaje de cualquier seat que termine en DONE sin mencionar a otro seat. Es la forma que exigen el registro inicial de environment y el cierre de etapa del coordinator. | El watchdog loguea "run outcome posted; exiting" antes de la etapa 1 y deja de reiniciar seats. Toy y tablekeeper son de varias etapas. Simulado. | Exigir que lo mande el coordinator y que mencione al humano. |
| 4 | alta | `tools/measure_cost.py:118` | En el modo "seat solo" (el que documenta `CLAUDE.md`), las sesiones salen de `band usage sessions` sin refrescar. Las de la última corrida no aparecen y el seat da 0 tokens, con exit 0 y sin la marca `partial`. | `measure_cost.py 21:27:19Z 21:37:12Z reviewer` da `output=0` con exit 0. RUN-3 registra 16.743 tokens. | Correr `band usage refresh` antes, o marcar `partial` / salir con error cuando una sesión cae fuera de la ventana. |
| 5 | alta | `tools/watchdog.py:35` | `due()` supone que todo seat mencionado tiene que contestar, pero los veredictos y los handoffs mencionan a dos seats y solo uno actúa. | Un REJECT menciona al coordinator, y el mandate le prohíbe actuar. Si la reparación dura más de 10 min, el watchdog lo reinicia sin motivo y puede re-delegar. Pasa en las 8 salas. Simulado. | Vigilar solo al seat del `NEXT`. |
| 6 | media | `tools/validate_room.py:83` | Los sha se comparan como strings crudos: un sha corto y uno completo del mismo commit no coinciden. | Si el builder entrega `abc1234` y el reviewer acepta el sha completo, la etapa queda "open" (falso). Un REJECT sobre `bad[:7]` y un ACCEPT sobre `bad` completo dan "repaired" sin commit nuevo. Reproducido. small-run-1/2 y tiny-run-2 ya mezclan largos. | Normalizar con `git rev-parse` antes de comparar. |
| 7 | media | `tools/validate_room.py:10` | El vocabulario del validador no coincide con el de los mandates. El `ACCEPT` con el que el builder contesta un hallazgo se cuenta como veredicto, y `DISPUTE`, `CLARIFY`, `CONFORMS` y `DEVIATES` en la línea STATE se marcan como inválidos. | Una respuesta `STATE ACCEPT` del builder da "verdicts 3, stages closed 0/1" con problemas falsos, y `STATE DISPUTE …` da "without a valid protocol line". Reproducido. | Contar como veredicto solo el que manda el reviewer, y aceptar el vocabulario de respuesta a hallazgos. |
| 8 | alta | `tools/validate_room.py:147` | Los casos "self-accept" y "missing sha" terminan en `@[[c]] … DONE`, así que la regla nueva los hace fallar antes que las guardas que tenían que probar. Además falta el caso negativo. | Si se quitan la guarda de autor y `commit_exists`, `--self-check` sigue en ok. Mutación ejecutada. `docs/PLAN.md:66` afirma lo contrario. | Casos con `NEXT` correcto, un caso de DONE sin mención que dé 0 problemas, y comprobar el texto del problema. |
| 9 | media | `tools/watchdog.py:90` | El `subprocess.run` de `band restart` tiene `timeout=120`, pero no atrapa `TimeoutExpired` ni `OSError`. | Un restart lento o un daemon caído mata al watchdog en segundo plano, y el resto de la corrida queda sin vigilancia. | Atraparlas, loguearlas y seguir. |
| 10 | media | `cases/tiny/RUN-3.md:60` y otros | Hay cifras publicadas que ya no salen del comando. Rompe la regla "Todo número publicado sale de un comando". | RUN-3 dice "exit 0 … 0 problems" y hoy da 3 problemas. También quedan desactualizados small RUN-2:26, RUN-3:32 y RUN-5:36, tiny RUN-1:36 y RUN-2:44, y `PLAN.md:90`. | Volver a correr el validador sobre los 8 rooms y actualizar cada cifra, o anotar que la regla es posterior a la corrida. |
| 11 | media | `mandates/environment.md:38`, `mandates/coordinator.md:54` | El paso 2 de environment y el cierre de etapa del coordinator (paso 6) siguen sin línea de protocolo literal. La regla nueva marca los cierres que ya cumplían el mandate. | small-run-2 #132 y small-run-3 #229 pasan a PROBLEM con exit 1. | Agregar líneas literales en los dos pasos. |
| 12 | media | `tools/validate_room.py:61`, `tools/watchdog.py` | La regla nueva recalcula la última línea en vez de usar lo que ya parseó `protocol()`. Encima, el watchdog decide "DONE con o sin mención" con otro criterio. Rompe la regla "Un solo lugar decide". | Un mensaje que termina en ` ``` ` recibe veredictos distintos del validador y del watchdog. | Que `protocol()` devuelva `next`, y una función pura compartida. |
| 13 | baja | `tools/watchdog.py:33` | `due()` ignora las menciones que no vienen de un seat, así que el despacho del humano al coordinator nunca se vigila. | Si el coordinator no toma el despacho, el watchdog nunca lo reinicia y no deja ningún log. | Incluir las menciones del humano. |
| 14 | media | `cases/small/checks.py:7` | El timeout de 5 s es más corto que los 10 s que el spec da para el reset, y los checks no esperan a que `/health` responda (hasta 30 s). SKILL §6.3 los corre justo después de `docker run -d`. | Un servicio que cumple el spec pero tarda 6 s en el reset, o 3 s en arrancar, da 0/9 o 0/5 falso. | Timeout de 10 s y un loop sobre `/health` hasta 30 s antes del primer check. |
| 15 | baja | `cases/small/checks.py:55` | `check_create` exige que el título se guarde recortado. El spec solo pide recortar para validar la longitud. | Una implementación que cumple el spec y guarda el título original falla el check: el FAIL es del check, no del producto. | Aceptar el título original o el recortado, o aclararlo en el spec. |
| 16 | baja | `tools/measure_cost.py`, `cases/tiny/checks.py`, `tools/validate_room.py` | Tres limpiezas que quedaron fuera del tope de 15. | `measure_cost` lee cada transcript dos veces; `cases/tiny/checks.py` repite `check_health`; `commit_exists` sobre una ruta que no es un repo no da error de uso. | Limpiezas menores. |

## Orden sugerido para arreglar

1. **Validador:** hallazgos 1, 2, 6, 7, 8 y 12. Son los que producen veredictos falsos y un self-check que no detecta regresiones.
2. **Watchdog:** hallazgos 3, 5, 9 y 13. Hoy puede irse antes de tiempo o reiniciar al seat equivocado en las corridas de varias etapas.
3. **Costo:** hallazgo 4. Publica ceros falsos.
4. **Mandates y cifras publicadas:** hallazgos 10 y 11.
5. **Checks del caso chico:** hallazgos 14 y 15.

## Estado

Sin aplicar. Sigue sin commitear el diff de la review anterior (environment `NEXT @coordinator` y la regla "mention + DONE").
